from openai import OpenAI
import json
import os
from dotenv import load_dotenv
import scalekit.client
import tool



# Load environment variables from .env file
load_dotenv()
sk = scalekit.client.ScalekitClient(
    client_id="skc_53814741268693059",
    client_secret="test_ZBeqNRT3fQjTfGzFmFObkTDMlMbndBjZ3jOBADvd5OONZFBWzeOBmXiWwjlGLqCu",
    env_url="https://kindle-dev.scalekit.cloud",
)
client = OpenAI()




input_messages = [
    {"role": "user", "content": "read latest  emails in gmail then send a summary to Slack channel #connect"},
]

# Initial AI request with tools
response = client.responses.create(
    model="gpt-4.1",
    input=input_messages,
    tools=tool.ALL_TOOLS,
    tool_choice="auto",
    parallel_tool_calls=False
)



# Handle tool calls and get responses
tool_response = sk.connect.handle_tool_calls(
   input_messages=input_messages,
   openai_response=response,
   identifier = "avinash.kamath@scalekit.com"
)


response = client.responses.create(
    model="gpt-4.1",
    input=tool_response,
    tools=tool.ALL_TOOLS,
    tool_choice="auto",
    parallel_tool_calls=False
)

tool_response = sk.connect.handle_tool_calls(
    input_messages = [],
    openai_response=response,
    identifier = "avinash.kamath@scalekit.com"
)


