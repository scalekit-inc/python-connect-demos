# Proxy timeout tests

Run the same set of proxy test cases against two environments and compare the results. The cases check that the Scalekit tool proxy handles small and large files, slow transfers, header errors, `X-Proxy-Domain` overrides and stalled upstreams the same way everywhere.

The scripts call the proxy over HTTPS with the Python standard library. They read credentials from environment variables, never from the code.

## Prerequisites

- Python 3.9 or later. No packages to install.
- A Scalekit environment with a connected account for each provider you test:
  - **Google Drive** for `proxy_matrix.py`.
  - **Salesforce** for the two Salesforce scripts.
- `TOOL_ENV_URL`, `TOOL_CLIENT_ID` and `TOOL_CLIENT_SECRET` for each environment, in the repo-root `.env` or in a separate file you pass with `--env-file`.

## Run the matrix

Run the Drive matrix from this folder. Each run writes `results_<label>.json` to `--out-dir`.

```bash
python proxy_matrix.py --connection google_drive --identifier you@example.com --label staging
python proxy_matrix.py --env-file production.env --connection google_drive --identifier you@example.com --label production
python compare_results.py results_staging.json results_production.json
```

The run creates test files in the connected Drive and deletes them at the end. The file names start with `proxy-tests-`.

| Option | Effect |
|---|---|
| `--skip-long` | Skips the cases that take over a minute (`L*`, `S*`). |
| `--skip-huge` | Skips the huge upload and huge download. |
| `--huge-size-mib` | Sets the huge file size. The default is 1024. |
| `--huge-file-id` | Downloads an existing Drive file for the huge download case and skips the huge upload. |
| `--keep-files` | Keeps the test files in Drive, names them `proxy-tests-<case>.bin` and prints a link to each. Delete them yourself afterwards. |
| `--slow-connection`, `--slow-identifier` | Enables the stalled-upstream cases `S1` to `S7`. |

## Build a report with raw responses

Every results file stores the request and the response of each case: the status, key headers and the body (truncated to 4,000 characters; binary downloads show their size and checksum). `build_report.py` turns one or more pairs of results files into a Markdown report with a comparison table, per-case times and the raw responses.

```bash
python build_report.py --out report.md \
  --pair "Google Drive proxy matrix" results_staging.json results_production.json \
  --pair "Salesforce REST proxy" sfrest_staging.json sfrest_production.json
```

The report contains real ids and addresses from the tested accounts. Review it before you share it.

## Cases in the Drive matrix

| Cases | What they test |
|---|---|
| `H1`–`H5` | Account check, list with query parameters, multipart create and update (40,883 bytes, the shape seen in production), delete. |
| `M1`, `M2` | Multipart create and update with a 5 MiB body. |
| `F1`–`F6` | Small (1 KiB), medium (5 MiB) and large (60 MiB) upload and download, with checksum checks. |
| `HU1`, `HD1` | Huge upload and huge download (1 GiB by default). |
| `SU1`, `SD1` | Slow upload (about 15 seconds) and slow download (about 25 seconds). Both outlast the old 10-second deadline. |
| `N1`–`N8` | No token, bad token, missing headers, unknown connection or account, upstream 404 and 400 passed through. |
| `X0`–`X13` | `X-Proxy-Domain` overrides: other host, metadata address, localhost, private address, port, scheme, the provider's own host, uppercase, list, blank, on an upload, with a missing header. Each is compared with a control request. |
| `L1`, `L2`, `L2b` | An upload that takes about 45 seconds, and two parallel downloads held open past 60 seconds. |
| `S1`–`S7` | Stalled upstream: replies after 15 and 45 seconds, and never replies (Graph-shaped GET, multipart PATCH and POST, export-shaped GET). |

## Reproduce a stalled upstream

Cases `S1` to `S7` need an upstream that stays silent. Use the included server and a connection that points at it.

1. Start the server:

   ```bash
   python slow_upstream.py --default-delay 90 --port 9500
   ```

2. Expose the port through a public HTTPS tunnel, for example `ngrok http 9500`.
3. In the Scalekit dashboard, create a custom connector with the tunnel URL as the proxy URL and an API key authentication pattern. Create a connection and a connected account for it.
4. Pass the connection name and identifier to the matrix:

   ```bash
   python proxy_matrix.py --connection google_drive --identifier you@example.com --label staging \
     --slow-connection slow-test --slow-identifier slow-user
   ```

5. Delete the connector, connection and account, then stop the server and the tunnel.

> **Security:** the tunnel is a public URL that reaches your machine. Run it only while you test, and expose only the slow server.

## Salesforce scripts

| Script | What it tests |
|---|---|
| `salesforce_rest_matrix.py` | Read-only REST calls, error passthrough, header errors and `X-Proxy-Domain` overrides. Paths are relative to `/services/data/<version>`. |
| `salesforce_soap_matrix.py` | The SOAP proxy with Metadata API calls and its failure shapes. |

```bash
python salesforce_rest_matrix.py --connection salesforce-xxxx --identifier you@example.com --label staging
python salesforce_soap_matrix.py --connection salesforce-xxxx --identifier you@example.com --label staging
```

The SOAP proxy works when all three conditions hold:

1. The `actions_soap_proxy_enabled` flag is on for the workspace. With the flag off, Salesforce returns `404` because the proxy treats the call as REST.
2. The connection requests the `refresh_token` scope next to `full`. The `full` scope alone returns no refresh token, and the proxy returns `SOAP_TOKEN_REFRESH_FAILED`.
3. The request is a Metadata API envelope with no `<Header>`. The proxy adds the session header itself. An envelope with its own `SessionHeader`, or a Partner API envelope, fails with `Illegal Session`.

A call that fails with an invalid session can make Scalekit mark the connected account `EXPIRED`. Authorize the account before you run the scripts.

## Read the results

`compare_results.py` calls two cases the same when the status and outcome match and the elapsed times are close. It ignores the wording of timeout pages and exact byte counts. The command exits with status 1 when any case differs.

| Outcome | Meaning |
|---|---|
| `504` at about 60 seconds, `backend_timeout` in the load balancer log | The load balancer cut a request the upstream never answered. |
| `200` with fewer bytes than the file size | The load balancer cut a download after the headers were sent. The client sees no error. |
| An upload cut at about 30 seconds | The server read timeout. It applies to every request body. |
| `X-Proxy-Domain` marked `ignored, same as control` | The proxy did not use the override. |
