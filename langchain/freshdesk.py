
import scalekit.client
import os
from dotenv import load_dotenv
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_openai import ChatOpenAI

from prompt import prompt

# Load environment variables
load_dotenv()
connection_name = "freshdesk"
identifier = "avinash"


scalekit = scalekit.client.ScalekitClient(
    client_id=os.getenv("SCALEKIT_CLIENT_ID"),
    client_secret=os.getenv("SCALEKIT_CLIENT_SECRET"),
    env_url=os.getenv("SCALEKIT_ENV_URL"),
)
connect = scalekit.connect



tools =  connect.langchain.get_tools(
    identifier=identifier,
    providers = ["FRESHDESK","SLACK","GMAIL"],
)

llm = ChatOpenAI(model="gpt-4o")
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools,verbose=True)


result = agent_executor.invoke(
    {
        "input":
            '''
            I need you to help me test a complete customer support workflow in Freshdesk and slack:
            Create a new contact for "Jiten" with email "jitender.rana@scalekit.com", job title "testter", and phone "+1-555-0123"
            Create a high priority ticket from this contact about "All tests are failing" with description "Site Has crashed"
            Update the ticket to assign it to agent  avinash figure the agent by listing  and change status to "Pending" while we investigate
            
            Add a reply to the ticket saying "Hi Jiten, we've received your ticket and our senior engineer is investigating the Exchange server issue. We'll provide an update within 2 hours. Thank you for your patience."
            
            Get the full ticket details to review the conversation
            
            Update the ticket status to "Resolved" and add a final reply: "The server has been restored. All email services are now functioning normally. Please test and confirm everything is working on your end."
            
            List all tickets updated in the last 24 hours to see our recent activity
            
            Execute this complete workflow and show me the results of each step.
            
            Send the summary of this entire interaction to #connect channel in slack
            ''',
    }
)