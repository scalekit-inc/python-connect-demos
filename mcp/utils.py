def authenticate_tool(connect, connection_name, identifier):
    
    try:
        response = connect.get_connected_account(
            connection_name=connection_name,
            identifier=identifier
        )
        if(response.connected_account.status != "ACTIVE"):
            print(f"{connection_name} is not connected: {response.connected_account.status}")
            link_response = connect.get_authorization_link(
                connection_name=connection_name,
                identifier=identifier
            )
            print(f"🔗click on the link to authorize {connection_name}", link_response.link)
            input(f"⎆ Press Enter after authorizing {connection_name}...")
    except Exception as e:
        link_response = connect.get_authorization_link(
            connection_name=connection_name,
            identifier=identifier
        )
        print(f"🔗 click on the link to authorize {connection_name}", link_response.link)
        input(f"⎆ Press Enter after authorizing {connection_name}...")
    
    return True