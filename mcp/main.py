import asyncio

from dotenv import load_dotenv
from langchain.agents import create_react_agent, create_openai_tools_agent, AgentExecutor
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from prompt import prompt
load_dotenv()

client = MultiServerMCPClient(
    {
        "scalekita": {
            "transport": "streamable_http",
            "url": "https://kindle-dev.scalekit.cloud/mcp/v1/1a5def0d-af53-427b-b395-d78c4c77ed80/",
            "headers": {
                "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6InNua181MzgxNDc0MDM2MjcyMzM5NSIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2tpbmRsZS1kZXYuc2NhbGVraXQuY2xvdWQiLCJzdWIiOiJza2NfNTM4MTQ3NDEyNjg2OTMwNTkiLCJhdWQiOlsic2tjXzUzODE0NzQxMjY4NjkzMDU5Il0sImV4cCI6MTc1NDk1NjM4NSwiaWF0IjoxNzU0OTI3NTg1LCJuYmYiOjE3NTQ5Mjc1ODUsImNsaWVudF9pZCI6InNrY181MzgxNDc0MTI2ODY5MzA1OSIsImp0aSI6InRrbl84NTMyOTU2NzUzOTAwMzQyMSJ9.kTDj53bOboFMbdopA-iBIqkA7RSxkaU_iKUqPf-650lhi-VQE20ITLz1fM9QsNu04_qNZbsZDFIoF0kHn03vMDhcRUNcZBsOfA7TpluSnZrBggXj-U2nenyYHRL3RZg33oyqP5ZM0ERgQIQfFmyx8j6OhF3vC9NQ6rI-nNSoLE8VqfWc7RqHjYJ9S_1NRuvSfux6OH5_tgUwRYOK3UAF4IWV4_ueb3BA9iVWM9dQqz4amdIjhn-FfOUGyGyN9bMEsEioncUVJNgoZrxIkDim2ArGpn7nqCBWIO7ZzIElKhl5wtEwv7pnrhPUmBINJGLkzKO6Hoj2ZHdaSIpu1-ZQGA",
            },
        }
    }
)

async def main():

    llm = ChatOpenAI(model="gpt-4o")

    async with client.session("scalekita") as session:
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

