
import scalekit.client
import os
from dotenv import load_dotenv
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_openai import ChatOpenAI

from prompt import prompt

# Load environment variables
load_dotenv()
connection_name = "hubspot"
identifier = "avinash"


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

print("click on the link to authorize hubspot", link.link)
input("Press Enter after authorizing hubspot...")

tools =  connect.langchain.get_tools(
    identifier=identifier,
    providers = [
        "HUBSPOT",
        "SLACK"
    ],
    page_size=100,
)

llm = ChatOpenAI(model="gpt-4o")
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools,verbose=True)


result = agent_executor.invoke(
    {
        "input":
            '''
            List all my contacts in hubspot give me a summary. and send it to slack channel #connect
           ''',
    }
)