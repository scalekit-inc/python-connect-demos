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

Then create your `.env` from the example and fill in your real values:

```bash
cp .env.example .env
```

Edit `.env`:

```dotenv
SCALEKIT_ENV_URL=https://your-auth-domain
SCALEKIT_CLIENT_ID=skc_xxxxxx
SCALEKIT_CLIENT_SECRET=xxxxxxxx
CONNECTED_ACCOUNT_ID=ca_xxxxxx
```

`.env` is gitignored, so your credentials stay out of version control.

## Run

```bash
python refresh_connected_account.py
```

## Notes

- Requires Python 3.11+.
- The SDK handles authentication, so you do not need to fetch or pass a bearer token.
