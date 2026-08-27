<p align="center">
  <a href="https://scalekit.com" target="_blank" rel="noopener noreferrer">
    <picture>
      <img src="https://cdn.scalekit.cloud/v1/scalekit-logo-dark.svg" height="64">
    </picture>
  </a>
</p>

<h1 align="center">
  Scalekit Python Connect Demos
</h1>

<p align="center">
  <strong>Auth stack for AI apps ⚡ Python agent integrations</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/scalekit-sdk/"><img src="https://img.shields.io/pypi/v/scalekit-sdk.svg" alt="PyPI version"></a>
  <a href="https://github.com/scalekit-inc/python-connect-demos/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://docs.scalekit.com"><img src="https://img.shields.io/badge/docs-scalekit.com-blue" alt="Documentation"></a>
</p>

<p align="center">
  Python examples demonstrating third-party app integrations and AI agent connectivity with Scalekit Connect
</p>

## 🚀 Available Demos

### 1. Direct Integration
**Direct Python SDK usage with third-party apps**

- **OAuth Flows**: Connect to Gmail, Slack, and other third-party services
- **Tool Execution**: Execute pre-built tools for common app integrations  
- **Authorization Links**: Generate OAuth authorization URLs for users
- **API Interactions**: Direct API calls to integrated third-party services

### 2. LangChain Integration
**AI agents with third-party app access**

- **LangChain Tools**: Pre-built tools for Gmail, Google Calendar, Salesforce, HubSpot
- **Agent Workflows**: AI agents that can read emails, manage calendars, update CRM
- **Authentication Flow**: OAuth-based access to user's third-party accounts
- **Multi-App Chains**: Complex workflows across multiple integrated apps

### 3. OpenAI Integration
**OpenAI functions with app integrations**

- **Function Calling**: OpenAI functions that can access Gmail, Slack, etc.
- **Email Management**: Read latest emails and send summaries to Slack
- **Automated Workflows**: AI-driven actions across multiple connected apps
- **OAuth Integration**: Secure access to user's authorized third-party accounts

### 4. Model Context Protocol (MCP)
**MCP server with third-party app tools**

- **MCP Server**: Expose third-party app tools through Model Context Protocol
- **Tool Mappings**: Configure which apps and tools are available to AI agents
- **Multi-App Access**: Single MCP server providing access to Gmail, Calendar, etc.
- **Client Compatibility**: Works with various MCP-compatible AI clients

## Getting Started

### Prerequisites

- Python 3.8+ 
- Scalekit account and credentials
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/scalekit-inc/python-connect-demos.git
cd python-connect-demos
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
# Create .env file with your Scalekit credentials
SCALEKIT_ENV_URL=your_environment_url
SCALEKIT_CLIENT_ID=your_client_id
SCALEKIT_CLIENT_SECRET=your_client_secret
```

### Running the Examples

Each demo directory contains specific setup and running instructions. Navigate to the desired demo and follow its README:

- `direct/` - Direct API integration examples
- `langchain/` - LangChain agent examples  
- `openai/` - OpenAI assistant examples
- `mcp/` - Model Context Protocol server examples

## Key Features

- **Third-Party App Integrations**: OAuth connections to Gmail, Slack, Google Calendar, Salesforce, HubSpot
- **AI Agent Tools**: Pre-built tools for AI agents to interact with connected apps
- **Multi-Framework Support**: Examples for direct SDK usage, LangChain, OpenAI, and MCP
- **OAuth Flows**: Secure authorization and token management for third-party services
- **Tool Execution**: Execute actions like reading emails, sending messages, managing calendar events

## Additional Resources

  - 📚 [Scalekit Documentation](https://docs.scalekit.com)
  - 🔧 [API Reference](https://docs.scalekit.com/apis/)
  - 🚀 [Full Stack Auth Quickstart](https://docs.scalekit.com/fsa/quickstart/)
  - 💬 [Community Examples](https://github.com/orgs/scalekit-developers/repositories)
  - 🐍 [Python SDK](https://github.com/scalekit-inc/scalekit-sdk-python)

## Contributing

We welcome contributions! Please feel free to submit a pull request with any improvements or additional examples.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

<p align="center">
  Made with ❤️ by <a href="https://scalekit.com">Scalekit</a>
</p>