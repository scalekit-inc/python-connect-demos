"""Shared helpers for the proxy timeout / behaviour tests.

Reads TOOL_ENV_URL, TOOL_CLIENT_ID and TOOL_CLIENT_SECRET from the repo-root .env
(or from --env-file, e.g. a separate file for another environment) and talks to the
Scalekit tool proxy: <TOOL_ENV_URL>/proxy/<path>
"""
import argparse
import datetime
import hashlib
import http.client
import json
import os
import ssl
import threading
import time
import urllib.parse
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT_ENV = Path(__file__).resolve().parents[2] / ".env"  # <repo>/.env
REQUIRED = ("TOOL_ENV_URL", "TOOL_CLIENT_ID", "TOOL_CLIENT_SECRET")
TEXT_TYPES = ("json", "xml", "text", "html", "javascript")


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S")


def load_env(env_file=None) -> dict:
    """Parse a .env file (no extra dependency). Real environment variables are the fallback."""
    path = Path(env_file) if env_file else ROOT_ENV
    values = {}
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip().strip("\"'")
    for key in REQUIRED:
        values.setdefault(key, os.getenv(key, ""))
    missing = [k for k in REQUIRED if not values.get(k)]
    if missing:
        raise SystemExit(f"Missing {', '.join(missing)} in {path} (or the environment)")
    return values


def retry(fn, attempts=4, delay=2):
    """Retry transient connection errors (the TLS handshake occasionally drops)."""
    for i in range(attempts):
        try:
            return fn()
        except (ssl.SSLError, ConnectionError, OSError):
            if i == attempts - 1:
                raise
            time.sleep(delay)


def fetch_token(env: dict) -> str:
    base = env["TOOL_ENV_URL"].rstrip("/")
    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": env["TOOL_CLIENT_ID"],
        "client_secret": env["TOOL_CLIENT_SECRET"],
    }).encode()
    req = urllib.request.Request(base + "/oauth/token", data=data)
    return retry(lambda: json.loads(urllib.request.urlopen(req, timeout=30).read())["access_token"])


def add_common_args(parser: argparse.ArgumentParser, default_label="run"):
    parser.add_argument("--env-file", help="path to a .env with TOOL_ENV_URL/TOOL_CLIENT_ID/TOOL_CLIENT_SECRET (default: repo-root .env)")
    parser.add_argument("--connection", required=True, help="connection name, e.g. google_drive")
    parser.add_argument("--identifier", required=True, help="connected account identifier")
    parser.add_argument("--label", default=default_label, help="label used in output and the results file name")
    parser.add_argument("--out-dir", default=".", help="directory for the results_<label>.json file")
    return parser


def request_info(method, path, body_bytes, extra):
    """Describe a request for the results file. Credentials are never recorded."""
    safe = {k: v for k, v in (extra or {}).items() if k.lower() in ("x-proxy-domain", "range", "content-type", "soapaction")}
    return {"method": method, "path": "/proxy" + path, "body_bytes": body_bytes, "headers": safe}


def snapshot(result, limit=4000):
    """A JSON-friendly copy of one request and response for the results file."""
    if not result:
        return None
    ctype = (result.get("content_type") or "").lower()
    body = result.get("body", "")
    if result.get("status") == "ERR":
        text = result.get("end", "")
    elif not ctype or any(t in ctype for t in TEXT_TYPES):
        text = body[:limit]
    else:
        text = f"<{result.get('got', 0)} bytes of {ctype}; md5 {result.get('md5', '')}>"
    return {"request": result.get("request"), "status": result.get("status"), "elapsed": round(result.get("elapsed", 0), 2),
            "content_type": ctype, "headers": result.get("headers") or {}, "body": text,
            "bytes_received": result.get("got"), "end": result.get("end")}


class ProxyClient:
    def __init__(self, env: dict, connection: str, identifier: str):
        self.env = env
        self.base = env["TOOL_ENV_URL"].rstrip("/")
        self.host = urlparse(self.base).netloc
        self.connection = connection
        self.identifier = identifier
        self.token = fetch_token(env)
        self._local = threading.local()  # last request and response per thread, read by last()

    # -- plumbing -----------------------------------------------------------------
    def headers(self, auth=True, connection=None, identifier=None, drop=(), extra=None) -> dict:
        h = {"User-Agent": "proxy-timeout-tests"}
        if auth:
            h["Authorization"] = "Bearer " + (self.token if auth is True else auth)
        if "Connection_name" not in drop:
            h["Connection_name"] = connection or self.connection
        if "Identifier" not in drop:
            h["Identifier"] = identifier or self.identifier
        h.update(extra or {})
        return h

    def connect(self, timeout=300) -> http.client.HTTPSConnection:
        return http.client.HTTPSConnection(self.host, 443, timeout=timeout, context=ssl.create_default_context())

    # -- calls --------------------------------------------------------------------
    def request(self, method, path, body=None, extra=None, rate_read=None, timeout=90, **header_opts) -> dict:
        """One proxied call. rate_read (MiB/s) throttles reading the response to hold it open."""
        def go():
            hdrs = self.headers(extra=extra, **header_opts)
            if body is not None:
                hdrs["Content-Length"] = str(len(body))
            start = time.time()
            conn = self.connect(timeout)
            conn.request(method, "/proxy" + path, body=body, headers=hdrs)
            resp = conn.getresponse()
            got, md5, kept, end = 0, hashlib.md5(), b"", "complete"
            try:
                while True:
                    chunk = resp.read(1 << 18)
                    if not chunk:
                        break
                    got += len(chunk)
                    md5.update(chunk)
                    if len(kept) < 4000:
                        kept += chunk[:4000]
                    if rate_read:
                        time.sleep(len(chunk) / (rate_read * 1048576))
            except Exception as exc:  # the stream was cut mid-body
                end = "ERR " + type(exc).__name__
            result = {"status": resp.status, "elapsed": time.time() - start, "body": kept.decode("utf-8", "replace"),
                      "got": got, "md5": md5.hexdigest(), "end": end, "content_type": resp.getheader("content-type", ""),
                      "headers": dict(resp.getheaders()),
                      "request": request_info(method, path, len(body) if body else 0, extra)}
            self._local.last = result
            return result
        return retry(go)

    def upload(self, path, total, rate=None, method="POST", extra=None) -> dict:
        """Stream `total` bytes of a repeating 1 MiB pattern; rate (MiB/s) throttles the upload."""
        block = (b"proxy-timeout-tests-" * 60000)[: 1 << 20]
        md5, sent, start = hashlib.md5(), 0, time.time()
        conn = self.connect(600)
        conn.putrequest(method, "/proxy" + path)
        hdrs = self.headers(extra={"Content-Type": "application/octet-stream", "Content-Length": str(total), **(extra or {})})
        for k, v in hdrs.items():
            conn.putheader(k, v)
        conn.endheaders()
        try:
            while sent < total:
                chunk = block[: min(len(block), total - sent)]
                conn.send(chunk)
                md5.update(chunk)
                sent += len(chunk)
                if rate:
                    time.sleep(len(chunk) / (rate * 1048576))
            resp = conn.getresponse()
            body, status, end = resp.read().decode("utf-8", "replace"), resp.status, "complete"
            content_type, resp_headers = resp.getheader("content-type", ""), dict(resp.getheaders())
        except Exception as exc:
            status, body, end, content_type, resp_headers = "ERR", "", "ERR " + type(exc).__name__, "", {}
        result = {"status": status, "elapsed": time.time() - start, "body": body[:4000], "sent": sent, "md5": md5.hexdigest(), "end": end,
                  "content_type": content_type, "headers": resp_headers, "request": request_info(method, path, total, extra)}
        self._local.last = result
        return result

    def last(self):
        """The most recent request and response made on the calling thread."""
        return getattr(self._local, "last", None)

    def account_status(self):
        """Connected account status (handy: invalid-session calls can flip it to EXPIRED)."""
        qs = urllib.parse.urlencode({"connector": self.connection, "identifier": self.identifier})
        req = urllib.request.Request(self.base + "/api/v1/connected_accounts?" + qs,
                                     headers={"Authorization": "Bearer " + self.token})
        try:
            accounts = json.loads(urllib.request.urlopen(req, timeout=30).read()).get("connected_accounts", [])
            return accounts[0].get("status") if accounts else "not found"
        except Exception:
            return "n/a"


def save_results(out_dir, label, results, extra=None):
    path = Path(out_dir) / f"results_{label}.json"
    path.write_text(json.dumps({"label": label, **(extra or {}), "results": results}, indent=1))
    print(f"[{label}] saved {path} ({len(results)} cases)")
    return path
