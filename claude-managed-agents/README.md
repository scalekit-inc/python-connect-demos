# Claude Managed Agents + Scalekit

This demo shows how Claude Managed Agents integrate with Scalekit for secure, user-scoped tool calling.

---

## Personas

### Agent Builder — `builder.py`

A one-time setup run by whoever is building the agent. Discovers available apps and tools, creates a virtual MCP server, and registers the agent.

```python
# 1. Show apps and tools available using scalekit sdk

# 2. Create a Virtual MCP server scoped to selected tools
→ scalekit generates mcp url

# 3. Register the Claude Managed Agent
```

---

### Agent Executor — `executor_setup.py` + `executor_run.py`

#### `executor_setup.py` — End-user account connection (one-time)

Run once per end-user to connect their accounts. Analogous to an Integrations screen in a web app.

```python
# Get auth links for each connection in the MCP config

# User clicks links to complete authorization with Gmail and Google Calendar
```

#### `executor_run.py` — Run an agent session

Mints a short-lived token for the user, stores it in a CMA vault, and runs the agent.

```python
# 1. Mint a scoped session token for the end-user using scalekit

# 2. Store token in a CMA vault

# 3. Create and stream an agent session
```

---

## Running in local steps

```bash
cp .env.example .env   # fill in credentials
uv run builder.py      # Agent Builder (run once)
uv run executor_setup.py  # end-user connects accounts (run once per user)
uv run executor_run.py    # run an agent session
uv run cleanup.py         # tear everything down
```

