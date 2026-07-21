# refresh-tools (Python)

A small helper script to force-refresh tools for a given connected account id (`ca_xxx`),
built on [`scalekit-sdk-python`](https://pypi.org/project/scalekit-sdk-python/).

## What it does

1. Creates a `ScalekitClient` — the SDK authenticates with your client credentials
   internally, so there is no separate access-token step.
2. Fetches the connected account's current state by id.
3. Forces tools refresh by connected account by id.

## Setup

Use a virtual environment and install the SDK:

```bash
cd ~/Documents/repos/python-connect-demos/mcp-helper-scripts/refresh-tools
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then open `refresh_connected_account.py` and fill in the four values at the top:

```python
ENV_URL = "https://your-env.scalekit.cloud"   # your environment URL
CLIENT_ID = "skc_xxxxxxxxxxxxxxxx"             # SCALEKIT_CLIENT_ID
CLIENT_SECRET = "test_xxxxxxxxxxxxxxxx"        # SCALEKIT_CLIENT_SECRET
CA_ID = "ca_xxxxxxxxxxxxxxxx"                   # connected account id
```

## Run

```bash
python refresh_connected_account.py
```

## Notes

- Requires Python 3.11+.
- The SDK handles authentication, so you do not need to fetch or pass a bearer token.
