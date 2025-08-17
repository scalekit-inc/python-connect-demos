import asyncio
from dotenv import load_dotenv
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from scalekit.connect.types import ToolMapping
from prompt import prompt
import scalekit.client
load_dotenv()

scalekit_client = scalekit.client.ScalekitClient(
    os.getenv("SCALEKIT_ENV_URL"),
    os.getenv("SCALEKIT_CLIENT_ID"),
    os.getenv("SCALEKIT_CLIENT_SECRET")
)

async def main():


    mcp_response = scalekit_client.connect.create_mcpc(
        identifier = "default",
        tool_mappings = [
            ToolMapping(
                tool_names=["gmail_fetch_mails", "gmail_send_mails"],
                connection_name="GMAIL",
            )
        ]
    )


    client = MultiServerMCPClient(
        {
            "scalekit": {
                "transport": "streamable_http",
                "url": mcp_response.url,
            }
        }
    )

    llm = ChatOpenAI(model="gpt-4o")
    async with client.session("scalekit") as session:
        await session.initialize()
        tools = await load_mcp_tools(session)
        print("Available tools:", tools)
        agent = create_openai_tools_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools,verbose=True)
        result = await agent_executor.ainvoke(
            {
                "input": " read the 1st unread emails in gmail and send summary to Slack channel #connect,keep ",
            }
        )
        print("Agent result:", result)




if __name__ == "__main__":
    asyncio.run(main())

