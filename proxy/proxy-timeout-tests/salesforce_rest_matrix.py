#!/usr/bin/env python3
"""Run the Salesforce REST proxy cases (read-only) and save the results.

    python salesforce_rest_matrix.py --connection salesforce-xxxx --identifier you@example.com --label staging

The Salesforce proxy base is `https://<domain>/services/data/<version>`, so every path below
is relative to it (`/limits`, not `/services/data/...`). The cases only read data.

Note: calls that fail with an invalid Salesforce session can make Scalekit mark the connected
account EXPIRED. Authorize the account before you run the matrix.
"""
import argparse
import json
import urllib.parse

from common import ProxyClient, add_common_args, load_env, save_results, utc_now


def describe(response: dict) -> str:
    """Summarize a response in a form that compares across environments."""
    try:
        parsed = json.loads(response["body"])
    except ValueError:
        return ""
    if response["status"] == 200 and isinstance(parsed, dict):
        if "records" in parsed:
            return f"records={len(parsed['records'])}"
        if "sobjects" in parsed:
            return f"sobjects={len(parsed['sobjects'])}"
        if "fields" in parsed:
            return f"fields={len(parsed['fields'])} name={parsed.get('name')}"
        return f"keys={len(parsed)}"
    item = parsed[0] if isinstance(parsed, list) and parsed else parsed
    return "err=" + str(item.get("errorCode") or item.get("code") or "")[:30] if isinstance(item, dict) else ""


def main():
    args = add_common_args(argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)).parse_args()
    client = ProxyClient(load_env(args.env_file), args.connection, args.identifier)
    quote = urllib.parse.quote
    cases = [
        ("H1", "GET /limits", "GET", "/limits", {}),
        ("H2", "SOQL, one row (Account)", "GET", "/query?q=" + quote("SELECT Id, Name FROM Account LIMIT 1"), {}),
        ("H3", "list sobjects", "GET", "/sobjects", {}),
        ("H4", "describe Account", "GET", "/sobjects/Account/describe", {}),
        ("H5", "SOQL, up to 200 users", "GET", "/query?q=" + quote("SELECT Id, Name, Email FROM User LIMIT 200"), {}),
        ("H6", "tooling query", "GET", "/tooling/query?q=" + quote("SELECT Id, Name FROM ApexClass LIMIT 5"), {}),
        ("H7", "SOSL search", "GET", "/search?q=" + quote("FIND {test} IN ALL FIELDS RETURNING Account(Id) LIMIT 3"), {}),
        ("H8", "recent items", "GET", "/recent?limit=5", {}),
        ("N1", "no Authorization header", "GET", "/limits", {"auth": False}),
        ("N2", "invalid bearer token", "GET", "/limits", {"auth": "not-a-real-token"}),
        ("N3", "missing Connection_name", "GET", "/limits", {"drop": ("Connection_name",)}),
        ("N4", "missing Identifier", "GET", "/limits", {"drop": ("Identifier",)}),
        ("N5", "nonexistent connection name", "GET", "/limits", {"connection": "does-not-exist"}),
        ("N6", "nonexistent identifier", "GET", "/limits", {"identifier": "nobody@example.invalid"}),
        ("N7", "SOQL syntax error (400 relayed)", "GET", "/query?q=" + quote("SELEC Id FROM Account"), {}),
        ("N8", "unknown sobject (404 relayed)", "GET", "/sobjects/NoSuchObject__c/describe", {}),
        ("N9", "unknown field in SOQL (400 relayed)", "GET", "/query?q=" + quote("SELECT NoSuchField__c FROM Account LIMIT 1"), {}),
        ("N10", "wrong path form (/services/data/... is not relative)", "GET", "/services/data/", {}),
        ("X1", "X-Proxy-Domain override to example.com", "GET", "/limits", {"extra": {"X-Proxy-Domain": "example.com"}}),
        ("X2", "X-Proxy-Domain override to the metadata address", "GET", "/limits", {"extra": {"X-Proxy-Domain": "169.254.169.254"}}),
        ("X3", "X-Proxy-Domain override to localhost", "GET", "/limits", {"extra": {"X-Proxy-Domain": "localhost"}}),
        ("X4", "X-Proxy-Domain override to a private address", "GET", "/limits", {"extra": {"X-Proxy-Domain": "10.0.0.1"}}),
    ]
    print(f"[{args.label}] account status before: {client.account_status()}")
    results = {}
    for case_id, description, method, path, options in cases:
        r = client.request(method, path, **options)
        outcome = describe(r) or ("ok" if r["status"] == 200 else "")
        results[case_id] = {"desc": description, "status": r["status"], "outcome": outcome, "elapsed": r["elapsed"]}
        print(f"[{args.label} {utc_now()}] {case_id:4s} {description[:56]:56s} {r['status']} {outcome} ({r['elapsed']:.1f}s)", flush=True)
    print(f"[{args.label}] account status after: {client.account_status()}")
    save_results(args.out_dir, args.label, results, {"host": client.host})


if __name__ == "__main__":
    main()
