
import scalekit.client
import os
from dotenv import load_dotenv
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from scalekit.connect.models.tool_mapping import ToolMapping

from prompt import prompt

# Load environment variables
load_dotenv()
connection_name = "SALESFORCE"
identifier = "default"


scalekit = scalekit.client.ScalekitClient(
    client_id=os.getenv("SCALEKIT_CLIENT_ID"),
    client_secret=os.getenv("SCALEKIT_CLIENT_SECRET"),
    env_url=os.getenv("SCALEKIT_ENV_URL"),
)
connect = scalekit.connect



link = connect.get_authorization_link(
    connection_name=connection_name,
    identifier=identifier,
)

print("click on the link to authorize Salseforce", link.link)
input("Press Enter after authorizing salesforce...")

tools =  connect.langchain.get_tools(
    identifier=identifier,
    providers = ["SALESFORCE"],
    page_size=100,
)

# optionally create an MCP creation
# mcp = connect.create_mcp(
#     identifier=identifier,
#     tool_mappings=[
#         ToolMapping(
#             connection_name=connection_name,
#             tool_names=[],
#         )
#     ],
# )
#print("MCP created successfully:", mcp.url)

llm = ChatOpenAI(model="gpt-4o")
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools,verbose=True)


result = agent_executor.invoke(
    {
        "input":
            '''
        get all my accounts from salesforce with united  in the name
        ''',
    }
)