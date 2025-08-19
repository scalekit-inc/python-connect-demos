from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain.tools import tool
from scalekit_client import scalekit_client
from langchain.agents import AgentExecutor, create_openai_tools_agent
from prompt import prompt
from scalekit.v1.tools.tools_pb2 import Filter

connect = scalekit_client.connect
load_dotenv()
identifier = "sdk-avinash"

def authenticate_tool(connection_name,identifier):
    link_response = connect.get_authorization_link(
        connection_name=connection_name,
        identifier=identifier,
    )
    print(f"Click on the link to authorize {connection_name}: {link_response.link}")
    input(f"Press Enter after authorizing {connection_name}...")

# Create the agent and executor
if __name__ == "__main__":

    #Outh2.0 flows for all connections

    authenticate_tool("gcal", identifier)


    tools =  connect.langchain.get_tools(identifier=identifier,filter = Filter(
        provider = "GOOGLECALENDAR",
    ))
    print("Available tools:", tools)

    llm = ChatOpenAI(model="gpt-4o")
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools,verbose=True)


    result = agent_executor.invoke(
        {
            "input":
                '''
                What are the events in my calendar for next 3 days today is 19th august 2025.
                Please provide the details of each event including the time, title, and description.
                ''',
        }
    )



















