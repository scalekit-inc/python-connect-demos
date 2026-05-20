"""
LeadIQ demo using Scalekit Agent Auth.

LeadIQ uses API key authentication (BASIC). The API key is stored as
`username` in the connection's static_auth credentials.

Run:
    python leadiq.py
"""

import os

import scalekit.client
from dotenv import load_dotenv

load_dotenv()

scalekit = scalekit.client.ScalekitClient(
    os.getenv("SCALEKIT_ENV_URL"),
    os.getenv("SCALEKIT_CLIENT_ID"),
    os.getenv("SCALEKIT_CLIENT_SECRET"),
)
actions = scalekit.actions

CONNECTION_NAME = "leadiq"
IDENTIFIER = "user_123"
LEADIQ_API_KEY = os.getenv("LEADIQ_API_KEY", "<YOUR_LEADIQ_API_KEY>")


def main():
    # ── Step 1: Connect with API key ──────────────────────────────────────────
    # LeadIQ uses BASIC auth — the API key is the username, password is empty.

    response = actions.get_or_create_connected_account(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        authorization_details={
            "static_auth": {
                "username": LEADIQ_API_KEY,
            }
        },
    )
    account = response.connected_account
    print(f"Connected account: {account.id} | Status: {account.status}")

    # ── Step 2: Check quota before consuming credits ──────────────────────────

    usage = actions.execute_tool(
        tool_name="leadiq_get_usage",
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        tool_input={},
    )
    print("\nCredit usage:")
    print(usage.data)

    # ── Step 3: Preview — check if a contact has data (no credits consumed) ──

    preview = actions.execute_tool(
        tool_name="leadiq_search_people_preview",
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        tool_input={
            "linkedin_url": "https://www.linkedin.com/in/satyanadella",
        },
    )
    print("\nSearch people preview:")
    print(preview.data)

    # ── Step 4: Full contact lookup (consumes credits) ────────────────────────

    contact = actions.execute_tool(
        tool_name="leadiq_search_people",
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        tool_input={
            "first_name": "Satya",
            "last_name": "Nadella",
            "company_name": "Microsoft",
            "limit": 1,
        },
    )
    print("\nSearch people result:")
    print(contact.data)

    # ── Step 5: Enrich a company by domain ───────────────────────────────────

    company = actions.execute_tool(
        tool_name="leadiq_search_company",
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        tool_input={
            "company_domain": "microsoft.com",
        },
    )
    print("\nSearch company result:")
    print(company.data)

    # ── Step 6: Advanced people search with filters (consumes credits) ────────

    advanced = actions.execute_tool(
        tool_name="leadiq_flat_advanced_search",
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        tool_input={
            "company_filter": {
                "industries": ["Software Development"],
                "sizes": [{"min": 50, "max": 500}],
            },
            "contact_filter": {
                "seniorities": ["VP", "Director"],
            },
            "limit": 5,
        },
    )
    print("\nFlat advanced search result:")
    print(advanced.data)

    # ── Step 7: Advanced search grouped by company ────────────────────────────

    grouped = actions.execute_tool(
        tool_name="leadiq_grouped_advanced_search",
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        tool_input={
            "company_filter": {
                "industries": ["Software Development"],
            },
            "contact_filter": {
                "seniorities": ["Executive"],
            },
            "limit": 3,
            "limit_per_company": 2,
        },
    )
    print("\nGrouped advanced search result:")
    print(grouped.data)


if __name__ == "__main__":
    main()
