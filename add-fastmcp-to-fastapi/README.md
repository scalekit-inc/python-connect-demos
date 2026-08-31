# Add FastMCP to a FastAPI app (spec-first)

Take an existing FastAPI service, generate its OpenAPI spec locally, and stand up
an MCP server **from that spec** — reusing the API's existing auth. No tools are
hand-written and no new auth layer is added. The API and the MCP server run in
**one process on one port** (`:8000`).

- **Todo API** (FastAPI): `create / list / update / delete`, protected by a static
  key in **middleware** via the standard `Authorization` header. Method and
  parameter descriptions come from docstrings and `Field` / `Path` descriptions.
- **`openapi.json`**: the API's spec, dumped locally.
- **MCP server**: `FastMCP.from_openapi(spec, client)`, mounted at `/mcp`. Each
  tool call is proxied to the Todo API; the `httpx` client sends the **same key**,
  so the **same middleware** validates it.

```
                     ┌─ /api/todos ── Todo API (Authorization middleware)
MCP client ──▶ :8000 ┤
                     └─ /mcp/       ── MCP server ──(httpx + Authorization)──▶ /api/todos
```

Refer `server.py` to understand how mcp is wrapped over your existing apis in just 4 lines of code.

## 1. Run the demo locally

```bash
cd add-fastmcp-to-fastapi
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -r requirements.txt
cp .env.example .env

# Generate the spec (re-run after changing todo_api.py)
python generate_openapi.py

# Start API + MCP
python server.py                 # http://localhost:8000  (MCP at /mcp/)
```

## 2. Expose with ngrok and add it as a Scalekit custom connector

Scalekit needs a public **HTTPS** URL. Keep `server.py` running, and in a new
terminal:

```bash
ngrok http 8000
```

ngrok prints a forwarding URL. Your public MCP endpoint is that URL + `/mcp`:

```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:8000
# MCP endpoint: https://abc123.ngrok-free.app/mcp
```

Now register it in [Scalekit Dashboard](https://app.scalekit.com) → **AgentKit** → **Connectors** → **Create custom connector**, and fill
the **Add MCP connector** form:

- **Display name**: `Todo MCP`
- **Description**: `Todo list API exposed over MCP`
- **Server URL**: your ngrok MCP URL, e.g. `https://abc123.ngrok-free.app/mcp`
- **Auth type**: **API key**

Click **Save**, create a connection for the connector and connected account, and Scalekit can will fetch the
four tools and call them by name. Note the default API key value for this project is `demo-secret-key`.
