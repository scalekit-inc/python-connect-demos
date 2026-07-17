# End-to-End Setup

Full end-to-end examples that create a custom MCP provider, wire up an environment connection,
create a connected account, and either complete an OAuth flow or list available tools — all in
a single script.

| Script | Auth type | What it does |
|---|---|---|
| `1_oauth_pylon_provider.py` | OAuth 2.1 | Creates a Pylon MCP connector and prints the authorization URL for the user to complete |
| `2_bearer_apify_provider.py` | Bearer token | Creates an Apify MCP connector and lists available tools immediately after account creation |
| `3_apikey_context7_provider.py` | API Key | Creates a Context7 MCP connector and queries library docs immediately after account creation |
| `4_public_bloomreach_provider.py` | No Auth | Creates a public Bloomreach MCP connector (no credentials) and searches docs immediately after account creation |

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

For `2_bearer_apify_provider.py` also set:

```
APIFY_API_TOKEN=apify_api_...
```

For `3_apikey_context7_provider.py` also set:

```
CONTEXT7_API_KEY=your_context7_api_key_here
```

---

## Running

### Pylon OAuth MCP connector

Before running, set your user identifier in the script:

```bash
python 1_oauth_pylon_provider.py
```

The script prints an authorization URL. Open it in a browser to complete the OAuth flow.
Once authorized, the connected account becomes active and tools are available via `list_scoped_tools`
(see the commented example at the bottom of the script).

---

### Apify Bearer Token MCP connector

```bash
python 2_bearer_apify_provider.py
```

Bearer auth requires no browser flow — the token is active immediately, so the script proceeds
straight to listing available tools after creating the connected account.

---

### Context7 API Key MCP connector

```bash
python 3_apikey_context7_provider.py
```

API key auth requires no browser flow — the key is active immediately. The script lists available
tools then queries Next.js docs via `c-customcontext7mcp_query_docs`.

---

### Bloomreach Public (No Auth) MCP connector

```bash
python 4_public_bloomreach_provider.py
```

No-auth connectors require no credentials at all — the connected account is created with an empty
`authorization_details` and is active immediately. The script lists available tools then searches
Bloomreach docs via `c-publicbloomreachmcp_search`.
