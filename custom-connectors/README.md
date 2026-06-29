# Custom Connectors

Examples showing how to create and manage custom MCP providers with the Scalekit Python SDK.

## Structure

| Folder | What it covers |
|---|---|
| [`crud/`](./crud/) | Full CRUD lifecycle for a custom provider — create, read, update (PUT-style), delete |
| [`end-to-end-setup/`](./end-to-end-setup/) | Complete setup examples: provider → connection → connected account, for both OAuth and Bearer auth |

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

For `end-to-end-setup/apify_bearer_provider.py` also set:

```
APIFY_API_TOKEN=apify_api_...
```

---

## Running the scripts

See the README in each subfolder for script-specific instructions:

- [`crud/README.md`](./crud/README.md)
- [`end-to-end-setup/README.md`](./end-to-end-setup/README.md)
