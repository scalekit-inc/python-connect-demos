# Custom Connectors

Examples showing how to create and manage custom MCP providers with the Scalekit Python SDK.

| Script | What it does |
|---|---|
| `provider_crud.py` | Full CRUD lifecycle for a custom provider — create, read, update (PUT-style), delete |
| `pylon_oauth_provider.py` | Creates a Pylon OAuth MCP connector and prints the authorization URL |
| `apify_bearer_provider.py` | Creates an Apify bearer-token MCP connector and lists available tools |

---

## Setup

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
uv sync --active
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Open `.env` and set:

```
SCALEKIT_ENV_URL=https://your-env.scalekit.cloud
SCALEKIT_CLIENT_ID=skc_...
SCALEKIT_CLIENT_SECRET=sks_...
```

For `apify_bearer_provider.py` also set:

```
APIFY_API_TOKEN=apify_api_...
```

---

## Running the scripts

### Provider CRUD

Demonstrates the full create → read → update → delete lifecycle for a custom provider.
Useful for understanding how the API works before building a real connector.

```bash
python provider_crud.py
```

> **Note:** The update call is PUT-style — you must echo back all existing fields
> (auth_patterns, metadata, etc.) alongside the fields you want to change, or the
> server will wipe the omitted values.

---

### Pylon OAuth MCP connector

Creates a Pylon MCP provider, an environment connection, a connected account, and
prints an authorization URL for the user to complete the OAuth flow.

Before running, set your user identifier in the script:

```python
# pylon_oauth_provider.py
USER_IDENTIFIER = "you@example.com"
```

Then run:

```bash
python pylon_oauth_provider.py
```

The script prints an authorization URL at the end. Open it in a browser to complete
the OAuth flow. Once the user authorizes, the connected account becomes active and
tools are available via `list_scoped_tools` (see the commented example at the bottom
of the script).

---

### Apify Bearer Token MCP connector

Creates an Apify MCP provider, an environment connection, a connected account with
the API token supplied directly, and lists the tools available for that connection.

Before running, set your user identifier in the script:

```python
# apify_bearer_provider.py
USER_IDENTIFIER = "you@example.com"
```

Then run:

```bash
python apify_bearer_provider.py
```

Bearer auth requires no browser flow — the token is active immediately, so the script
proceeds straight to listing available tools after creating the connected account.
