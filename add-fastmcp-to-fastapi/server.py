import json
import os
from pathlib import Path

import httpx
import uvicorn
from dotenv import load_dotenv
from fastmcp import FastMCP

from todo_api import app

load_dotenv(Path(__file__).parent / ".env")
API_KEY = os.getenv("API_KEY", "demo-secret-key")

spec = json.loads(Path(__file__).parent.joinpath("openapi.json").read_text())
client = httpx.AsyncClient(base_url="http://localhost:8000", headers={"Authorization": API_KEY})
mcp = FastMCP.from_openapi(openapi_spec=spec, client=client, name="Todo MCP")

mcp_app = mcp.http_app(path="/", stateless_http=True)
app.router.lifespan_context = mcp_app.lifespan
app.mount("/mcp", mcp_app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
