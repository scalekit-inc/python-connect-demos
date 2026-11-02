#!/usr/bin/env python3
"""Run the Salesforce SOAP proxy cases (read-only) and save the results.

    python salesforce_soap_matrix.py --connection salesforce-xxxx --identifier you@example.com --label staging

What the SOAP proxy needs to work:
  1. The `actions_soap_proxy_enabled` feature flag is on for the workspace. With the flag off,
     a SOAP request is handled as an ordinary REST call and Salesforce returns 404.
  2. The connection requests the `refresh_token` scope next to `full`. The `full` scope alone does
     not return a refresh token, so the proxy cannot refresh the session.
  3. The request is a Salesforce Metadata API envelope with no <Header>. The proxy injects the
     SessionHeader itself. An envelope that already has one gets a second, and a Partner API
     envelope has no Metadata namespace to build on. Both fail with "Illegal Session".

The cases only read data. Calls that fail with an invalid session can make Scalekit mark the
connected account EXPIRED, so the failing cases run last.
"""
import argparse
import re

from common import ProxyClient, add_common_args, load_env, save_results, snapshot, utc_now

SOAP_HEADERS = {"Content-Type": "text/xml; charset=UTF-8", "SOAPAction": '""'}
NAMESPACES = 'xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:met="http://soap.sforce.com/2006/04/metadata"'


def envelope(body: str, header: str = "", padding: str = "") -> bytes:
    return (f'<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope {NAMESPACES}>{header}'
            f"<soapenv:Body>{padding}{body}</soapenv:Body></soapenv:Envelope>").encode()


def describe_metadata(version: str = "62.0") -> bytes:
    return envelope(f"<met:describeMetadata><met:asOfVersion>{version}</met:asOfVersion></met:describeMetadata>")


def list_metadata(metadata_type: str) -> bytes:
    return envelope(f"<met:listMetadata><met:queries><met:type>{metadata_type}</met:type></met:queries>"
                    "<met:asOfVersion>62.0</met:asOfVersion></met:listMetadata>")


def summarize(response: dict) -> str:
    body = response["body"]
    fault = re.search(r"<faultstring>(.*?)</faultstring>", body)
    if fault:
        return "fault: " + fault.group(1).split(":")[0][:30]
    if response["status"] == 200 and body.lstrip().startswith("<"):
        return f"xml {response['got']}B"
    return "err=" + re.sub(r'.*"code":"([A-Z_]+)".*', r"\1", body)[:30] if '"code"' in body else body.strip()[:40].replace("\n", " ")


def main():
    args = add_common_args(argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)).parse_args()
    client = ProxyClient(load_env(args.env_file), args.connection, args.identifier)
    results = {}

    def run(case_id, description, method, path, body, extra=SOAP_HEADERS, **options):
        r = client.request(method, path, body=body, extra=extra, **options)
        outcome = summarize(r)
        results[case_id] = {"desc": description, "status": r["status"], "outcome": outcome, "elapsed": r["elapsed"], "response": snapshot(r)}
        print(f"[{args.label} {utc_now()}] {case_id:4s} {description[:56]:56s} {r['status']} {outcome} ({r['elapsed']:.1f}s)", flush=True)

    soap = "/services/Soap/m/62.0"
    print(f"[{args.label}] account status before: {client.account_status()}")
    run("SH1", "describeMetadata, /m/62.0, no Header", "POST", soap, describe_metadata())
    run("SH2", "describeMetadata, /m/68.0 (production-style path)", "POST", "/services/Soap/m/68.0", describe_metadata("68.0"))
    run("SH3", "listMetadata CustomObject (large response)", "POST", soap, list_metadata("CustomObject"))
    run("SH4", "listMetadata for a type the org lacks", "POST", soap, list_metadata("ApexClass"))
    run("SH5", "large request body (3 MB of padding)", "POST", soap,
        envelope("<met:describeMetadata><met:asOfVersion>62.0</met:asOfVersion></met:describeMetadata>", padding="<!--" + "x" * 3_000_000 + "-->"))
    run("SH6", "no SOAPAction header", "POST", soap, describe_metadata(), extra={"Content-Type": "text/xml; charset=UTF-8"})
    run("SH7", "Content-Type application/xml", "POST", soap, describe_metadata(), extra={"Content-Type": "application/xml", "SOAPAction": '""'})
    run("SH8", "X-Proxy-Domain override on a SOAP call", "POST", soap, describe_metadata(), extra={**SOAP_HEADERS, "X-Proxy-Domain": "example.com"})
    print(f"[{args.label}] account status after the happy cases: {client.account_status()}")
    run("SN1", "no Authorization header", "POST", soap, describe_metadata(), auth=False)
    run("SN2", "missing Connection_name", "POST", soap, describe_metadata(), drop=("Connection_name",))
    run("SN3", "missing Identifier", "POST", soap, describe_metadata(), drop=("Identifier",))
    run("SN4", "nonexistent connection name", "POST", soap, describe_metadata(), connection="does-not-exist")
    run("SN5", "nonexistent identifier", "POST", soap, describe_metadata(), identifier="nobody@example.invalid")
    run("SN6", "XML body that is not a SOAP envelope", "POST", soap, b"<notsoap><a/></notsoap>")
    run("SN7", "malformed XML body", "POST", soap, b"<soapenv:Envelope><unclosed>")
    run("SN8", "GET on a SOAP path", "GET", soap, None, extra={})
    run("SN9", "envelope with its own SessionHeader (duplicate)", "POST", soap,
        envelope("<met:describeMetadata><met:asOfVersion>62.0</met:asOfVersion></met:describeMetadata>",
                 header="<soapenv:Header><met:SessionHeader><met:sessionId>placeholder</met:sessionId></met:SessionHeader></soapenv:Header>"))
    run("SN10", "Partner API envelope (no Metadata namespace)", "POST", "/services/Soap/u/62.0",
        b'<?xml version="1.0"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" '
        b'xmlns:urn="urn:partner.soap.sforce.com"><soapenv:Body><urn:getUserInfo/></soapenv:Body></soapenv:Envelope>')
    print(f"[{args.label}] account status after the negative cases: {client.account_status()}")
    save_results(args.out_dir, args.label, results, {"host": client.host})


if __name__ == "__main__":
    main()
