from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
from langchain.tools import tool
from gmail_tool import fetch_gmail_emails
from scalekit_client import scalekit_client
from calendar_tool import create_calendar_event
from slack_tool import slack_tool
from datetime_tool import datetime_tool, datetime_converter_tool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from prompt import prompt

connect = scalekit_client.connect
load_dotenv()
identifier = "demo_user"

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
    authenticate_tool("SLACK", identifier)
    authenticate_tool("CALENDAR", identifier)


    tools = [slack_tool, fetch_gmail_emails, create_calendar_event, datetime_tool, datetime_converter_tool]
    llm = ChatOpenAI(model="gpt-4o")
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools,verbose=True)


    result = agent_executor.invoke(
        {
            "input":
                '''
                schedule  meeting with akshay.parihar@scalekit.com 
                for tomorrow at 10:00 AM IST and 
                send a message to slack channel #connect 
                with the meeting details
                ''',
        }
    )



















