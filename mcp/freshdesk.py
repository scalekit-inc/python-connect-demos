import os
import asyncio
from dotenv import load_dotenv
import scalekit.client
from scalekit.connect.types import ToolMapping
from utils import authenticate_tool

load_dotenv()

scalekit = scalekit.client.ScalekitClient(
    client_id="skc_88455227035877920",
    client_secret="test_rIhgBWjlWD2dTA8srZbWYSvvdHig3ivgFrlgIJzKvawELRBAGaScYpd1PTvpoBwT",
    env_url="https://scalekit-ae5eddy7aabca-dev.scalekit.cloud"
)
connect = scalekit.connect

def main():




    mcp_response = connect.create_mcp(
        identifier = "mihir.abnave@scalekit.com",
        tool_mappings = [
            ToolMapping(
                tool_names=[],
                connection_name="F4resh",
            )
        ]
    )
    print(mcp_response.url)

main()