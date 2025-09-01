
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
    providers = ["HUBSPOT"],
)

llm = ChatOpenAI(model="gpt-4o")
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools,verbose=True)


result = agent_executor.invoke(
    {
        "input":
            '''
              1. Create a new contact with email "test@example.com", name "John Doe", company
              "Test Corp", and phone "+1-555-123-4567"
            
              2. Get the contact details we just created using the contact ID from step 1
            
              3. Update that contact to add job title "Sales Manager" and set lifecycle stage to
              "lead" .

              4. Search the contact they you created. do a comprehensive sersch with all paramaters. create the contact if needed for complicatef flows            
             
            
              Please execute these steps in order and show me the results from each operation.
              Please provide the requests and responses for each step. please provide the request event when there is an error

        ''',
    }
)