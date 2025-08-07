import scalekit.client

scalekit = scalekit.client.ScalekitClient(
    client_id="skc_53814741268693059",
    client_secret="test_ZBeqNRT3fQjTfGzFmFObkTDMlMbndBjZ3jOBADvd5OONZFBWzeOBmXiWwjlGLqCu",
    env_url="https://kindle-dev.scalekit.cloud",
)
connect = scalekit.connect
link_response = connect.get_authorization_link(
    connection_name="GMAIL",
    identifier="avinash.kamath@scalekit.com",
)

print("click on the link to authorize gmail", link_response.link)
input("Press Enter after authorizing gmail...")

response = scalekit.connect.execute_tool(
    tool_name="GMAIL.FETCH_MAILS",
    identifier="default",
    tool_input={
        "max_results" : 1
    },
)

print(response)