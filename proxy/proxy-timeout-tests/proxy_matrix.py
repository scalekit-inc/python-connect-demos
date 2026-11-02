#!/usr/bin/env python3
"""Run every proxy test case against one environment and save the results.

Covers happy paths (multipart create and update, small, medium, large and huge files, slow
upload, slow download), negative paths, `X-Proxy-Domain` override cases and long-running
cases (an upload that outlasts the server read timeout, a download held open past the load
balancer timeout).

The cases use Google Drive. Run the same command against two environments, then compare:

    python proxy_matrix.py --connection google_drive --identifier you@example.com --label staging
    python proxy_matrix.py --env-file other.env --connection google_drive --identifier you@example.com --label production
    python compare_results.py results_staging.json results_production.json

Cases that need a stalled upstream (S1-S7) run only when you pass --slow-connection and
--slow-identifier. See README.md for how to create that connection.
"""
import argparse
import json
import re
import threading
import urllib.parse

from common import ProxyClient, add_common_args, load_env, save_results, snapshot, utc_now

MIB = 1 << 20


def multipart_body(name: str, size: int):
    """A multipart/related body of exactly `size` bytes (metadata part plus padded media part)."""
    boundary = "proxytests"
    head = (f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n"
            f"{json.dumps({'name': name})}\r\n--{boundary}\r\nContent-Type: application/octet-stream\r\n\r\n").encode()
    tail = f"\r\n--{boundary}--".encode()
    body = head + b"m" * (size - len(head) - len(tail)) + tail
    return body, {"Content-Type": f"multipart/related; boundary={boundary}", "Content-Length": str(len(body))}


def error_code(body: str) -> str:
    try:
        parsed = json.loads(body)
        error = parsed.get("error", parsed) if isinstance(parsed, dict) else {}
        return str(error.get("code") or error.get("status") or error.get("error_code") or "")[:30]
    except ValueError:
        return body.strip()[:40]


def file_id(response: dict):
    try:
        return json.loads(response["body"])["id"] if response["status"] == 200 else None
    except (ValueError, KeyError):
        return None


def main():
    parser = add_common_args(argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter))
    parser.add_argument("--skip-long", action="store_true", help="skip the cases that take over a minute (L*, S*)")
    parser.add_argument("--skip-huge", action="store_true", help="skip the huge upload and huge download cases")
    parser.add_argument("--huge-size-mib", type=int, default=1024, help="size of the huge file in MiB (default 1024)")
    parser.add_argument("--huge-file-id", help="Drive file id to download for the huge download case (skips the huge upload)")
    parser.add_argument("--keep-files", action="store_true", help="keep the test files in Drive, give them readable names and list them (default: delete them)")
    parser.add_argument("--slow-connection", help="connection whose upstream stalls, for cases S1-S7")
    parser.add_argument("--slow-identifier", help="connected account identifier for --slow-connection")
    args = parser.parse_args()

    client = ProxyClient(load_env(args.env_file), args.connection, args.identifier)
    results, created, names, lock = {}, [], {}, threading.Lock()

    def record(case_id, description, status, outcome, elapsed, call="last", **extra):
        """Store the case result with the request and response of the call just made on this thread."""
        response = snapshot(client.last() if call == "last" else call)
        with lock:
            results[case_id] = {"desc": description, "status": status, "outcome": outcome, "elapsed": elapsed, "response": response, **extra}
            print(f"[{args.label} {utc_now()}] {case_id:4s} {description[:60]:60s} {status} {outcome} ({elapsed:.1f}s)", flush=True)

    def drive_upload(path_query, total, rate=None, label=None):
        response = client.upload(f"/upload/drive/v3/files?uploadType=media&fields=id,size,md5Checksum{path_query}", total, rate=rate)
        fid = file_id(response)
        if fid:
            created.append(fid)
            if label:
                names[fid] = label  # used by --keep-files: a media upload has no name, so Drive calls it "Untitled"
        return response, fid

    def checksum_outcome(response, total):
        try:
            stored = json.loads(response["body"])
        except ValueError:
            return error_code(response["body"])
        ok = stored.get("md5Checksum") == response["md5"] and int(stored.get("size", 0)) == total
        return "ok md5 match" if ok else "MISMATCH"

    # ---- happy paths: account, query parameters, multipart (the production request shape) ----
    r = client.request("GET", "/drive/v3/about?fields=user(emailAddress)")
    record("H1", "account check (about)", r["status"], "ok" if r["status"] == 200 else error_code(r["body"]), r["elapsed"])
    r = client.request("GET", "/drive/v3/files?pageSize=1&fields=files(id)")
    record("H2", "list files with query parameters", r["status"], "ok" if r["status"] == 200 else error_code(r["body"]), r["elapsed"])
    fields = "fields=id%2Cname%2CmimeType"
    body, hdrs = multipart_body("proxy-tests-multipart.bin", 40883)
    r = client.request("POST", f"/upload/drive/v3/files?uploadType=multipart&{fields}&supportsAllDrives=true", body=body, extra=hdrs)
    multipart_id = file_id(r)
    if multipart_id:
        created.append(multipart_id)
    record("H3", "multipart POST, 40,883 bytes (production shape)", r["status"], "ok" if multipart_id else error_code(r["body"]), r["elapsed"])
    if multipart_id:
        body, hdrs = multipart_body("proxy-tests-multipart-2.bin", 40883)
        r = client.request("PATCH", f"/upload/drive/v3/files/{multipart_id}?uploadType=multipart&{fields}&supportsAllDrives=true", body=body, extra=hdrs)
        record("H4", "multipart PATCH (update), 40,883 bytes (production shape)", r["status"], "ok" if r["status"] == 200 else error_code(r["body"]), r["elapsed"])
    # Larger multipart bodies: create with POST, then update the same file with PATCH.
    body, hdrs = multipart_body("proxy-tests-multipart-large.bin", 5 * MIB)
    r = client.request("POST", f"/upload/drive/v3/files?uploadType=multipart&{fields}&supportsAllDrives=true", body=body, extra=hdrs, timeout=120)
    large_multipart_id = file_id(r)
    if large_multipart_id:
        created.append(large_multipart_id)
    record("M1", "multipart POST (create), 5 MiB", r["status"], "ok" if large_multipart_id else error_code(r["body"]), r["elapsed"])
    if large_multipart_id:
        body, hdrs = multipart_body("proxy-tests-multipart-large-2.bin", 5 * MIB)
        r = client.request("PATCH", f"/upload/drive/v3/files/{large_multipart_id}?uploadType=multipart&{fields}&supportsAllDrives=true", body=body, extra=hdrs, timeout=120)
        record("M2", "multipart PATCH (update), 5 MiB", r["status"], "ok" if r["status"] == 200 else error_code(r["body"]), r["elapsed"])

    # ---- small, medium and large files ----
    response, small_id = drive_upload("", 1024, label="F1-small-1KiB")
    record("F1", "small file upload, 1 KiB, checksum", response["status"], checksum_outcome(response, 1024) if small_id else error_code(response["body"]), response["elapsed"])
    if small_id:
        r = client.request("GET", f"/drive/v3/files/{small_id}?alt=media")
        record("F2", "small file download, checksum", r["status"], "ok md5 match" if r["md5"] == response["md5"] else "MISMATCH", r["elapsed"])
    response, medium_id = drive_upload("", 5 * MIB, label="F3-medium-5MiB")
    record("F3", "medium file upload, 5 MiB, checksum", response["status"], checksum_outcome(response, 5 * MIB) if medium_id else error_code(response["body"]), response["elapsed"])
    if medium_id:
        r = client.request("GET", f"/drive/v3/files/{medium_id}?alt=media")
        record("F4", "medium file download, checksum", r["status"], "ok md5 match" if r["md5"] == response["md5"] and r["got"] == 5 * MIB else "MISMATCH", r["elapsed"])
    response, large_id = drive_upload("", 60 * MIB, label="F5-large-60MiB")
    record("F5", "large file upload, 60 MiB, checksum", response["status"], checksum_outcome(response, 60 * MIB) if large_id else response["end"], response["elapsed"])
    if large_id:
        r = client.request("GET", f"/drive/v3/files/{large_id}?alt=media", timeout=300)
        record("F6", "large file download, 60 MiB, checksum", r["status"], "ok md5 match" if r["md5"] == response["md5"] and r["got"] == 60 * MIB else f"got {r['got'] >> 20} MiB {r['end']}", r["elapsed"])
    # ---- huge upload and huge download ----
    # The server cuts a request body that takes longer than about 30 seconds to arrive, so a huge
    # upload only completes on a fast connection. The huge download needs a huge file in Drive:
    # it uses the file from the huge upload, or the file you pass with --huge-file-id.
    if not args.skip_huge:
        huge_bytes = args.huge_size_mib * MIB
        huge_md5, huge_id = None, args.huge_file_id
        if not huge_id:
            response, huge_id = drive_upload("", huge_bytes, label="HU1-huge")
            huge_md5 = response["md5"]
            record("HU1", f"huge upload, {args.huge_size_mib} MiB, unthrottled", response["status"],
                   checksum_outcome(response, huge_bytes) if huge_id else f"cut after {response['sent'] >> 20} MiB ({response['end']})", response["elapsed"])
        if huge_id:
            r = client.request("GET", f"/drive/v3/files/{huge_id}?alt=media", timeout=900)
            expected = "ok md5 match" if huge_md5 and r["md5"] == huge_md5 and r["got"] == huge_bytes else None
            record("HD1", "huge download, full file, unthrottled", r["status"], expected or f"got {r['got'] >> 20} MiB {r['end']}", r["elapsed"])
        else:
            record("HD1", "huge download, full file, unthrottled", "skipped", "the huge upload did not complete; pass --huge-file-id to test the download", 0.0, call=None)

    # ---- slow upload and slow download (outlast the old 10-second deadline, stay under 30 seconds of reading) ----
    response, slow_up_id = drive_upload("", 45 * MIB, rate=3.0, label="SU1-slow-upload-45MiB")
    record("SU1", "slow upload, 45 MiB at about 3 MiB/s (~15s)", response["status"], checksum_outcome(response, 45 * MIB) if slow_up_id else response["end"], response["elapsed"])
    if slow_up_id:
        r = client.request("GET", f"/drive/v3/files/{slow_up_id}?alt=media", extra={"Range": f"bytes=0-{30 * MIB - 1}"}, rate_read=1.2, timeout=120)
        record("SD1", "slow download, 30 MiB range at about 1.2 MiB/s (~25s)", r["status"], f"got {r['got'] >> 20} MiB {r['end']}", r["elapsed"])

    # ---- DELETE ----
    r = client.upload("/upload/drive/v3/files?uploadType=media&fields=id", 9)
    delete_id = file_id(r)
    if delete_id:
        r = client.request("DELETE", f"/drive/v3/files/{delete_id}")
        record("H5", "DELETE a file (204, empty body)", r["status"], "ok" if r["status"] == 204 else error_code(r["body"]), r["elapsed"])

    # ---- negative paths ----
    def negative(case_id, description, method, path, **options):
        r = client.request(method, path, **options)
        record(case_id, description, r["status"], f"err={error_code(r['body'])}", r["elapsed"])

    about = "/drive/v3/about?fields=user"
    negative("N1", "no Authorization header", "GET", about, auth=False)
    negative("N2", "invalid bearer token", "GET", about, auth="not-a-real-token")
    negative("N3", "missing Connection_name header", "GET", about, drop=("Connection_name",))
    negative("N4", "missing Identifier header", "GET", about, drop=("Identifier",))
    negative("N5", "nonexistent connection name", "GET", about, connection="does-not-exist")
    negative("N6", "nonexistent identifier", "GET", about, identifier="nobody@example.invalid")
    negative("N7", "upstream 404 relayed (unknown file id)", "GET", "/drive/v3/files/doesNotExist123?fields=id")
    negative("N8", "upstream 400 relayed (bad fields value)", "GET", "/drive/v3/files?fields=bogusField")

    # ---- X-Proxy-Domain override cases: each is compared with a control request ----
    control = client.request("GET", about)
    record("X0", "control: no X-Proxy-Domain header", control["status"], "ok" if control["status"] == 200 else error_code(control["body"]), control["elapsed"])
    override_values = [
        ("X1", "override to a different public host", "example.com"),
        ("X2", "override to the cloud metadata address", "169.254.169.254"),
        ("X3", "override to localhost", "localhost"),
        ("X4", "override to a private address", "10.0.0.1"),
        ("X5", "override with a port", "example.com:8080"),
        ("X6", "override with a scheme", "https://example.com"),
        ("X7", "override to the provider's own host", "www.googleapis.com"),
        ("X8", "override to the provider's host, uppercase", "WWW.GOOGLEAPIS.COM"),
        ("X9", "override with a comma-separated list", "example.com,evil.com"),
        ("X10", "override with whitespace only", "   "),
        ("X11", "override with an empty value", ""),
    ]
    for case_id, description, value in override_values:
        r = client.request("GET", about, extra={"X-Proxy-Domain": value})
        same = r["status"] == control["status"] and r["body"] == control["body"]
        record(case_id, description + f" ({value!r})", r["status"], "ignored, same as control" if same else f"differs from control: err={error_code(r['body'])}", r["elapsed"])
    body, hdrs = multipart_body("proxy-tests-override.bin", 2048)
    r = client.request("POST", f"/upload/drive/v3/files?uploadType=multipart&{fields}", body=body, extra={**hdrs, "X-Proxy-Domain": "example.com"})
    override_upload_id = file_id(r)
    if override_upload_id:
        created.append(override_upload_id)
    record("X12", "override on an upload (POST with a body)", r["status"], "ignored, upload succeeded" if override_upload_id else f"err={error_code(r['body'])}", r["elapsed"])
    negative("X13", "override with a missing Identifier header", "GET", about, drop=("Identifier",), extra={"X-Proxy-Domain": "example.com"})

    # ---- long-running cases (run in parallel) ----
    long_threads = []
    if not args.skip_long:
        def l1():
            r = client.upload("/upload/drive/v3/files?uploadType=media&fields=id", 120 * MIB, rate=2.8)
            fid = file_id(r)
            if fid:
                created.append(fid)
                names[fid] = "L1-45-second-upload"
            record("L1", "upload that takes about 45s (past the 30s read timeout)", r["status"], "ok" if fid else f"cut after {r['sent'] >> 20} MiB ({r['end']})", r["elapsed"])

        big = {}
        ready = threading.Event()

        def l2():
            r = client.upload("/upload/drive/v3/files?uploadType=media&fields=id", 60 * MIB, rate=6.0)
            fid = file_id(r)
            if not fid:
                record("L2", "download held open past 60s", r["status"], "setup upload failed", r["elapsed"])
                return
            created.append(fid)
            names[fid] = "L2-60MiB-held-open-download"
            big["id"] = fid
            ready.set()
            d = client.request("GET", f"/drive/v3/files/{fid}?alt=media", rate_read=0.5, timeout=300)
            full = d["got"] == 60 * MIB
            record("L2", "download held open by a slow reader (~120s to finish)", d["status"], "complete" if full else f"truncated at {d['elapsed']:.0f}s, got {d['got'] >> 20} MiB", d["elapsed"])

        def l2b():
            ready.wait(200)
            if "id" not in big:
                return
            d = client.request("GET", f"/drive/v3/files/{big['id']}?alt=media", rate_read=0.5, timeout=300)
            full = d["got"] == 60 * MIB
            record("L2b", "second parallel held-open download", d["status"], "complete" if full else f"truncated at {d['elapsed']:.0f}s, got {d['got'] >> 20} MiB", d["elapsed"])

        long_threads += [threading.Thread(target=f) for f in (l1, l2, l2b)]

        if args.slow_connection and args.slow_identifier:
            def stalled(case_id, description, method, path, body=None, extra=None):
                r = client.request(method, path, body=body, extra=extra, timeout=200, connection=args.slow_connection, identifier=args.slow_identifier)
                record(case_id, description, r["status"], f"{r['elapsed']:.0f}s body={r['body'][:40]!r}", r["elapsed"])

            mp_body, mp_hdrs = multipart_body("proxy-tests-stalled.bin", 40883)
            stalled_cases = [
                ("S1", "upstream replies after 15s", "GET", "/delay/15/v1.0/drives/b!Tests/items/01TEST", None, None),
                ("S2", "upstream replies after 45s", "GET", "/delay/45/v1.0/drives/b!Tests/items/01TEST", None, None),
                ("S3", "upstream stalls 90s: Graph-shaped GET", "GET", "/v1.0/drives/b!Tests/items/01TEST", None, None),
                ("S4", "upstream stalls 90s: GET with $select=id", "GET", "/v1.0/drives/b!Tests/items/01TEST?$select=id", None, None),
                ("S5", "upstream stalls 90s: multipart PATCH, 40,883 bytes", "PATCH", f"/upload/drive/v3/files/abc?uploadType=multipart&{fields}&supportsAllDrives=true", mp_body, mp_hdrs),
                ("S6", "upstream stalls 90s: multipart POST", "POST", f"/upload/drive/v3/files?uploadType=multipart&{fields}", mp_body, mp_hdrs),
                ("S7", "upstream stalls 90s: Sheets-export-shaped GET", "GET", "/spreadsheets/d/abc/export?format=xlsx", None, None),
            ]
            long_threads += [threading.Thread(target=stalled, args=case) for case in stalled_cases]
        else:
            print(f"[{args.label}] skipping S1-S7 (no --slow-connection / --slow-identifier)")

    for thread in long_threads:
        thread.start()
    for thread in long_threads:
        thread.join()

    # ---- clean up every file this run created ----
    kept = []
    if args.keep_files:
        for fid, label in names.items():
            client.request("PATCH", f"/drive/v3/files/{fid}?fields=id,name", body=json.dumps({"name": f"proxy-tests-{label}.bin"}).encode(),
                           extra={"Content-Type": "application/json"})
        print(f"[{args.label}] kept {len(created)} test files in Drive (delete them when you finish):")
        for fid in created:
            info = json.loads(client.request("GET", f"/drive/v3/files/{fid}?fields=id,name,size,webViewLink")["body"] or "{}")
            kept.append(info)
            print(f"    {info.get('name', '?'):44s} {int(info.get('size', 0)) / MIB:9.2f} MiB  {info.get('webViewLink', '')}")
    else:
        cleaned = [client.request("DELETE", f"/drive/v3/files/{fid}")["status"] for fid in created]
        print(f"[{args.label}] deleted {len(created)} test files: {cleaned}")
    save_results(args.out_dir, args.label, results, {"host": client.host, "kept_files": kept})


if __name__ == "__main__":
    main()
