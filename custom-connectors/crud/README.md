# CRUD

Examples for managing the lifecycle of a custom MCP provider via the Scalekit Python SDK.

| Script | What it does |
|---|---|
| `provider_crud.py` | Full CRUD lifecycle for a custom provider — create, read, update (PUT-style), delete |

---

## Setup

From the `custom-connectors/` root, activate the virtual environment and install dependencies:

```bash
source ../.venv/bin/activate
uv sync --active
```

Set the required environment variables in `../.env`:

```
SCALEKIT_ENV_URL=https://your-env.scalekit.cloud
SCALEKIT_CLIENT_ID=skc_...
SCALEKIT_CLIENT_SECRET=sks_...
```

---

## Running

```bash
python provider_crud.py
```

Demonstrates the full create → read → update → delete lifecycle for a custom provider.
Useful for understanding how the API works before building a real connector.

> **Note:** The update call is PUT-style — you must echo back all existing fields
> (auth_patterns, metadata, etc.) alongside the fields you want to change, or the
> server will wipe the omitted values.
