#!/usr/bin/env python3
"""Compare two results files from proxy_matrix.py or the Salesforce matrix scripts.

    python compare_results.py results_staging.json results_production.json

Each case gets two verdicts:

  outcome  the HTTP status and the outcome match. The wording of timeout error pages and
           exact byte counts are ignored because they vary between runs on one environment.
  time     the elapsed times are comparable: the difference is at most --abs-tol seconds
           or --rel-tol of the larger time, whichever is greater.

The command exits with status 1 when any case differs in outcome or time.
"""
import argparse
import json
import re
import sys
from pathlib import Path


def normalize(result: dict) -> tuple:
    outcome = str(result.get("outcome", ""))
    outcome = re.sub(r"body=b?'[^']*'", "", outcome)  # 504 page wording varies between runs
    outcome = re.sub(r"\d+(\.\d+)?s\b", "Ns", outcome)  # seconds inside the outcome text
    outcome = re.sub(r"(got|sent|after) \d+ MiB", r"\1 N MiB", outcome)
    outcome = re.sub(r"records=\d+", "records=N", outcome)
    outcome = re.sub(r"xml \d+B", "xml NB", outcome)  # response size depends on the org's data
    return str(result.get("status")), outcome.strip()


def time_gap(a: float, b: float, abs_tol: float, rel_tol: float):
    """Return (difference in seconds, allowed difference, comparable)."""
    allowed = max(abs_tol, rel_tol * max(a, b))
    return b - a, allowed, abs(b - a) <= allowed


def short(result: dict) -> str:
    return f"{result.get('status')} {str(result.get('outcome', ''))[:30]}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("first")
    parser.add_argument("second")
    parser.add_argument("--abs-tol", type=float, default=3.0, help="always allow this many seconds of difference (default 3)")
    parser.add_argument("--rel-tol", type=float, default=0.30, help="allow this fraction of the larger time (default 0.30)")
    args = parser.parse_args()

    a, b = json.loads(Path(args.first).read_text()), json.loads(Path(args.second).read_text())
    label_a, label_b = a.get("label", "first"), b.get("label", "second")
    ra, rb = a["results"], b["results"]
    ids = list(ra) + [k for k in rb if k not in ra]

    print(f"{'case':5s} {label_a + ' (status outcome)':36s} {label_b + ' (status outcome)':36s} {'outcome':8s} "
          f"{label_a[:9] + ' s':>10s} {label_b[:9] + ' s':>10s} {'diff s':>7s} {'ratio':>6s}  time")
    outcome_diff, time_diff, missing = [], [], []
    for case_id in ids:
        if case_id not in ra or case_id not in rb:
            missing.append(case_id)
            only = label_a if case_id in ra else label_b
            print(f"{case_id:5s} only in {only}")
            continue
        x, y = ra[case_id], rb[case_id]
        same_outcome = normalize(x) == normalize(y)
        ex, ey = float(x.get("elapsed", 0)), float(y.get("elapsed", 0))
        diff, allowed, comparable = time_gap(ex, ey, args.abs_tol, args.rel_tol)
        ratio = (ey / ex) if ex > 0 else float("nan")
        if not same_outcome:
            outcome_diff.append(case_id)
        if not comparable:
            time_diff.append(case_id)
        print(f"{case_id:5s} {short(x):36s} {short(y):36s} {'same' if same_outcome else 'DIFFERENT':8s} "
              f"{ex:10.1f} {ey:10.1f} {diff:+7.1f} {ratio:6.2f}  {'ok' if comparable else 'DIFFERS (allowed ±%.1fs)' % allowed}")

    compared = len(ids) - len(missing)
    print(f"\nOutcome: {compared - len(outcome_diff)} of {compared} cases are the same. Different: {outcome_diff or 'none'}.")
    print(f"Time:    {compared - len(time_diff)} of {compared} cases are within ±max({args.abs_tol:g}s, {args.rel_tol:.0%}). "
          f"Outside that: {time_diff or 'none'}.")
    if missing:
        print(f"Only in one file: {missing}.")
    return 1 if outcome_diff or time_diff else 0


if __name__ == "__main__":
    sys.exit(main())
