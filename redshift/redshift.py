import scalekit.client
import os
import time
from dotenv import load_dotenv


load_dotenv()


connection_name = "redshift-ayazsW7f"
identifier = "avinashk"

scalekit = scalekit.client.ScalekitClient(
    client_id=os.getenv("SCALEKIT_CLIENT_ID"),
    client_secret=os.getenv("SCALEKIT_CLIENT_SECRET"),
    env_url=os.getenv("SCALEKIT_ENV_URL"),
)
connect = scalekit.connect



connected_account = connect.get_or_create_connected_account(
    connection_name=connection_name,
    identifier=identifier,
)

print("Connected account:", connected_account)


# Update the connected account with the correct connection details after the customer has set up the connection in their AWS account and provided the necessary details to you.
connected_account = scalekit.actions.update_connected_account(
    connection_name=connection_name,
    identifier=identifier,
    api_config={
        "role_arn": "arn:aws:iam::166424725243:role/Avinash-Kindle-Redshift",
        "region": "us-east-1",
        "database": "sample_data_dev",
        "cluster_identifier": "",
        "workgroup_name": "test",
        "namespace_name": "test",
    },
)
print("Connected account after update", connected_account)

start = time.time()
response = scalekit.actions.execute_tool(
    tool_name="redshift_execute_sql",
    identifier=identifier,
    connection_name=connection_name,
    tool_input={
        "sql": "SELECT * from tickit.category",
        "with_event": False
    }
)
elapsed = time.time() - start
print(f"execute_tool took {elapsed:.2f}s")
print(response.data)