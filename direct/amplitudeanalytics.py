import scalekit.client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

scalekit = scalekit.client.ScalekitClient(
    client_id=os.getenv("SCALEKIT_CLIENT_ID"),
    client_secret=os.getenv("SCALEKIT_CLIENT_SECRET"),
    env_url=os.getenv("SCALEKIT_ENV_URL"),
)
connect = scalekit.connect

connection_name = "amplitudeanalytics"
identifier = "your_amplitude_user"

link_response = connect.get_authorization_link(
    connection_name=connection_name,
    identifier=identifier,
)
print("click on the link to authorize Amplitude Analytics", link_response.link)
input("Press Enter after authorizing Amplitude Analytics...")

# GET example — list chart annotations
list_response = connect.execute_tool(
    tool_name="amplitudeanalytics_list_annotations",
    identifier=identifier,
    tool_input={},
)
print("Annotations:", list_response)

# POST example — create a chart annotation
create_response = connect.execute_tool(
    tool_name="amplitudeanalytics_create_annotation",
    identifier=identifier,
    tool_input={
        "label": "Demo annotation from python-connect-demos",
        "start": "2026-07-24T00:00-0800",
    },
)
print("Created annotation:", create_response)
