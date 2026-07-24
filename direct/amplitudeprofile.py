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

connection_name = "amplitudeprofile"
identifier = "your_amplitude_user"

link_response = connect.get_authorization_link(
    connection_name=connection_name,
    identifier=identifier,
)
print("click on the link to authorize Amplitude Profile API", link_response.link)
input("Press Enter after authorizing Amplitude Profile API...")

# GET example — fetch a user's profile (properties, cohorts, recommendations,
# computations, and propensity scores are all opt-in via the get_* flags)
profile_response = connect.execute_tool(
    tool_name="amplitudeprofile_get_user_profile",
    identifier=identifier,
    tool_input={
        "user_id": "user_12345",
        "get_amp_props": True,
        "get_cohort_ids": True,
    },
)
print("User profile:", profile_response)

# No POST example: this connector wraps a single Amplitude endpoint
# (GET /v1/userprofile) — there is no write/POST tool for Profile API.
