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
# 1. Check which connections already have an active account

# 2. For each connection without an account, prompt (y/n) to authorize
#    → if yes, fetch and print the authorization link
#    → wait for the user to complete authorization in the browser before moving on

# 3. Print final connection status for all accounts
```

#### `executor_run.py` — Run an agent session

Mints a short-lived token for the user, stores it in a CMA vault, and runs the agent.

```python
# 1. Verify all connected accounts for the identifier are in active state
#    → exits gracefully if any connection is inactive, with guidance to re-run executor_setup.py

# 2. Mint a scoped session token for the end-user using scalekit

# 3. Store token in a CMA vault

# 4. Create and stream an agent session
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

