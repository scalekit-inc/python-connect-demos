#!/usr/bin/env python3
"""Build a Markdown report, with raw responses, from results files of two environments.

Each --pair takes a section name and two results files (the first and second environment):

    python build_report.py --out report.md \\
        --pair "Drive matrix" results_staging.json results_production.json \\
        --pair "Salesforce REST" sf_rest_staging.json sf_rest_production.json

The report has a summary, a comparison table with times, and for every case the request and
the response of both environments (bodies are shown once when they are identical).

The responses contain real ids and addresses from the tested accounts. Review the file before
you share it outside the team.
"""
import argparse
import json
from pathlib import Path

from compare_results import normalize, time_gap

LIMIT = 4000
SHOWN_HEADERS = ("content-type", "content-length", "via", "server", "date")


def pretty(body: str) -> tuple:
    """Return (language, text) for a response body."""
    try:
        return "json", json.dumps(json.loads(body), indent=2, ensure_ascii=False)
    except ValueError:
        return ("xml" if body.lstrip().startswith("<") else "text"), body


def block(body: str) -> str:
    language, text = pretty(body)
    note = "\n(shown truncated)" if len(body) >= LIMIT else ""
    return f"```{language}\n{text}{note}\n```"


def headers_line(response: dict) -> str:
    headers = {k.lower(): v for k, v in (response.get("headers") or {}).items()}
    shown = [f"`{name}: {headers[name]}`" for name in SHOWN_HEADERS if name in headers]
    return ", ".join(shown) if shown else "no headers recorded"


def request_line(response: dict) -> str:
    request = (response or {}).get("request") or {}
    if not request:
        return "no request was sent"
    extra = ", ".join(f"`{k}: {v}`" for k, v in (request.get("headers") or {}).items())
    size = request.get("body_bytes") or 0
    return f"`{request.get('method')} {request.get('path')}`" + (f", body {size:,} bytes" if size else "") + (f", {extra}" if extra else "")


def section(name: str, path_a: str, path_b: str, abs_tol: float, rel_tol: float) -> str:
    a, b = json.loads(Path(path_a).read_text()), json.loads(Path(path_b).read_text())
    la, lb = a.get("label", "first"), b.get("label", "second")
    ra, rb = a["results"], b["results"]
    ids = list(ra) + [k for k in rb if k not in ra]
    rows, details, outcome_diff, time_diff = [], [], [], []
    for case_id in ids:
        x, y = ra.get(case_id), rb.get(case_id)
        if x is None or y is None:
            rows.append(f"| {case_id} | only in {la if x else lb} | | | | |")
            continue
        same_outcome = normalize(x) == normalize(y)
        ex, ey = float(x.get("elapsed", 0)), float(y.get("elapsed", 0))
        diff, allowed, comparable = time_gap(ex, ey, abs_tol, rel_tol)
        if not same_outcome:
            outcome_diff.append(case_id)
        if not comparable:
            time_diff.append(case_id)
        cell = lambda r: f"{r.get('status')} {str(r.get('outcome', '')).replace('|', '/')[:38]}"
        rows.append(f"| {case_id} | {x['desc']} | {cell(x)} | {cell(y)} | {'same' if same_outcome else '**different**'} | "
                    f"{ex:.1f}s / {ey:.1f}s ({diff:+.1f}s) {'ok' if comparable else '**outside limit**'} |")
        rx, ry = x.get("response") or {}, y.get("response") or {}
        part = [f"#### {case_id}: {x['desc']}", "", f"Request ({la}): {request_line(rx)}"]
        if request_line(rx) != request_line(ry):
            part.append(f"Request ({lb}): {request_line(ry)}")
        part += ["", f"| | {la} | {lb} |", "|---|---|---|",
                 f"| Status | {rx.get('status')} | {ry.get('status')} |",
                 f"| Time | {ex:.1f}s | {ey:.1f}s |",
                 f"| Headers | {headers_line(rx)} | {headers_line(ry)} |", ""]
        bx, by = rx.get("body", ""), ry.get("body", "")
        if bx == by:
            part += [f"Response body (identical on both):", "", block(bx) if bx else "_empty_", ""]
        else:
            part += [f"Response body, {la}:", "", block(bx) if bx else "_empty_", "", f"Response body, {lb}:", "", block(by) if by else "_empty_", ""]
        details.append("\n".join(part))
    compared = len(ids)
    summary = (f"**{compared - len(outcome_diff)} of {compared}** cases have the same outcome. "
               f"**{compared - len(time_diff)} of {compared}** have times within max({abs_tol:g}s, {rel_tol:.0%}) of each other."
               + (f" Times outside the limit: {', '.join(time_diff)}." if time_diff else "")
               + (f" Outcomes that differ: {', '.join(outcome_diff)}." if outcome_diff else ""))
    return "\n".join([f"## {name}", "", summary, "", f"| Case | What was tested | {la} | {lb} | Outcome | Time ({la} / {lb}) |",
                      "|---|---|---|---|---|---|", *rows, "", f"### Requests and responses: {name}", "", *details])


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True)
    parser.add_argument("--title", default="Proxy test results")
    parser.add_argument("--pair", nargs=3, action="append", metavar=("NAME", "FIRST", "SECOND"), required=True)
    parser.add_argument("--abs-tol", type=float, default=3.0)
    parser.add_argument("--rel-tol", type=float, default=0.30)
    args = parser.parse_args()
    parts = [f"# {args.title}", "",
             "Each case ran with the same script on both environments. Times are compared per case: the limit is the greater of "
             f"{args.abs_tol:g} seconds or {args.rel_tol:.0%} of the larger time. Response bodies are the raw bodies the proxy returned, "
             "truncated to 4,000 characters; downloads of binary files show their size and checksum instead.", ""]
    parts += [section(name, a, b, args.abs_tol, args.rel_tol) + "\n" for name, a, b in args.pair]
    Path(args.out).write_text("\n".join(parts))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
