from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain.tools import tool

from gmail_tool import fetch_gmail_emails
from slack_tool import slack_tool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from prompt import prompt
load_dotenv()



# Create the agent and executor
if __name__ == "__main__":
    tools = [slack_tool,fetch_gmail_emails]
    # Initialize the OpenAI LLM

    tools = scalekit.connect.get_tools([],identifier)

    llm = ChatOpenAI(model="gpt-4o")
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools,verbose=True)

    # Invoke the agent with a Slack message request
    result = agent_executor.invoke(
        {
            "input": "read the 1st emails in gmail and send summary to Slack channel #connect",
        }
    )






















