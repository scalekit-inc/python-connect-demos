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


def run_region_demo(identifier, region_label):
    """Authorize (pick US or EU on the hosted form) and run one GET + one POST call."""
    link_response = connect.get_authorization_link(
        connection_name=connection_name,
        identifier=identifier,
    )
    print(f"click on the link to authorize Amplitude Analytics ({region_label})", link_response.link)
    input(f"Press Enter after authorizing Amplitude Analytics ({region_label})...")

    # GET example — list chart annotations
    list_response = connect.execute_tool(
        tool_name="amplitudeanalytics_list_annotations",
        identifier=identifier,
        tool_input={},
    )
    print(f"[{region_label}] Annotations:", list_response)

    # POST example — create a chart annotation
    create_response = connect.execute_tool(
        tool_name="amplitudeanalytics_create_annotation",
        identifier=identifier,
        tool_input={
            "label": f"Demo annotation from python-connect-demos ({region_label})",
            "start": "2026-07-24T00:00-0800",
        },
    )
    print(f"[{region_label}] Created annotation:", create_response)


# US region — pick "US" on the hosted authorization form
run_region_demo(identifier="your_amplitude_user_us", region_label="US")

# EU region — pick "EU" on the hosted authorization form. Same connection_name,
# same tools — only the connected account (and the region chosen at
# authorization time) differs between US and EU.
run_region_demo(identifier="your_amplitude_user_eu", region_label="EU")
