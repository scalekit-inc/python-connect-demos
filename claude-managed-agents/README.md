# Claude Managed Agents + Scalekit

This demo shows how to build an AI agent using Claude Managed Agents that reads your Gmail and creates Google Calendar events — powered by Scalekit for secure, user-scoped tool authorization.

---

## What's in this project

**Agent Builder (`builder.py`)** — Run once when you're setting up the agent. It discovers available apps and tools from your Scalekit environment, creates a Virtual MCP server scoped to the tools you want, and registers a Claude Managed Agent backed by that server.

**Agent Executor (`executor_setup.py` + `executor_run.py`)** — The runtime side. `executor_setup.py` connects an end-user's accounts (one-time). `executor_run.py` mints a short-lived token, stores it in the agent's vault, and runs a live agent session.

---

## Prerequisites

- Python 3.11+
- `uv` installed ([docs](https://docs.astral.sh/uv/getting-started/installation/))
- A [Scalekit](https://scalekit.com) account with an active environment
- An [Anthropic](https://platform.claude.com/) account with Claude Managed Agents access
- Active connections in your Scalekit environment:
  - `gmail` — Gmail is pre-configured in Scalekit, no setup needed
  - `googlecalendar` — must be created manually (see below)

#### Set up Google Calendar connection

Gmail comes pre-configured in Scalekit. For Google Calendar, create the connection manually:

1. Go to **Scalekit Dashboard → Connections → Create Connection**
2. Select **Google Calendar**
3. Set the connection name to exactly `googlecalendar`
4. Click **Save**

---

### Environment variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

| Variable | Where to find it |
|---|---|
| `SCALEKIT_ENV_URL` | Scalekit Dashboard → Settings |
| `SCALEKIT_CLIENT_ID` | Scalekit Dashboard → Settings |
| `SCALEKIT_CLIENT_SECRET` | Scalekit Dashboard → Settings |
| `ANTHROPIC_API_KEY` | [platform.claude.com](https://platform.claude.com/) |
| `ANTHROPIC_ENVIRONMENT_ID` | [platform.claude.com](https://platform.claude.com/) |

---

## Getting started

### 1. Set up the virtual environment

```bash
uv sync
source .venv/bin/activate
```

### 2. Run the Agent Builder

```bash
uv run builder.py
```

This is a one-time step done by whoever is building the agent. The script walks you through what it's doing at each stage:

- Lists all available apps and tools from your Scalekit environment
- Creates a Virtual MCP server scoped to Gmail and Google Calendar tools
- Registers a Claude Managed Agent that uses that Virtual MCP server

The agent ID and Virtual MCP server config are saved to the `datastore/` folder for use in subsequent steps.

### 3. Authorize with external connectors (one-time per end-user)

```bash
uv run executor_setup.py
```

This is the equivalent of an "Integrations" screen in a real app — each end-user runs this once to authorize their Gmail and Google Calendar accounts. The script:

- Checks which connections already have an authorized account
- For any that don't, prompts you to authorize and gives you a link to complete the OAuth flow in your browser
- Confirms the final connection status before exiting

### 4. Run the agent

```bash
uv run executor_run.py
```

This is what runs at agent invocation time — whether the agent is conversational or running as a background job, the flow is the same:

- Verifies all connected accounts are active (exits with guidance if any are not)
- Mints a short-lived scoped token from Scalekit for the end-user
- Stores the token in the agent's User Vault, linked to the Virtual MCP server — so when the agent calls a tool, it uses this token automatically
- Creates an agent session and streams the response, showing each tool call and result as it happens
- Archives the session when done

---

## Cleanup

To tear down the agent and Virtual MCP server:

```bash
uv run cleanup.py
```
