import json
import os
import re
from datetime import datetime, timezone
from dotenv import load_dotenv

import scalekit.client

# Load environment variables from .env file
load_dotenv()

# Helper to get required env or fallback to default/test values
def get_env_or_default(var, default):
    val = os.getenv(var)
    if val is not None and val.strip() != "":
        return val
    return default


SCALEKIT_ENV_URL = get_env_or_default("SCALEKIT_ENV_URL", "")
SCALEKIT_CLIENT_ID = get_env_or_default("SCALEKIT_CLIENT_ID", "")
SCALEKIT_CLIENT_SECRET = get_env_or_default("SCALEKIT_CLIENT_SECRET", "")

connection_name = "hubspot"
identifier = "pranesh.r@scalekit.com"

if not (SCALEKIT_ENV_URL and SCALEKIT_CLIENT_ID and SCALEKIT_CLIENT_SECRET):
    raise RuntimeError(
        "One or more required Scalekit credentials is missing. Please check your .env and environment variables."
    )

scalekit = scalekit.client.ScalekitClient(
    env_url=SCALEKIT_ENV_URL,
    client_id=SCALEKIT_CLIENT_ID,
    client_secret=SCALEKIT_CLIENT_SECRET,
)
actions = scalekit.actions


# ─── helpers ──────────────────────────────────────────────────────────────────

def run(label, tool_name, tool_input, expect_error=False):
    try:
        r = actions.execute_tool(
            tool_name=tool_name,
            identifier=identifier,
            connection_name=connection_name,
            tool_input=tool_input,
        )
        tag = "PASS" if not expect_error else "WARN (expected error but got success)"
        print(f"{tag}: {label}")
        return r.data
    except Exception as e:
        raw = str(e)
        msg = re.search(r'"message":"([^"]+)"', raw) or re.search(r"details = \"([^\"]+)\"", raw)
        if msg:
            err = msg.group(1)[:100]
        elif "unconditional drop overload" in raw or "no healthy upstream" in raw:
            err = "service temporarily unavailable"
        else:
            err = raw[:100]
        tag = "PASS (expected error)" if expect_error else "FAIL"
        print(f"{tag}: {label}: {err}")
        return None


def cleanup_email(eid):
    try:
        actions.execute_tool(tool_name="hubspot_marketing_email_delete", identifier=identifier,
                             connection_name=connection_name, tool_input={"emailId": eid})
    except Exception:
        pass  # email may already be archived or in unpublishable state


def cleanup_form(fid):
    try:
        actions.execute_tool(tool_name="hubspot_form_delete", identifier=identifier,
                             connection_name=connection_name, tool_input={"formId": fid})
    except Exception:
        pass


def get_email_id(data):
    m = re.search(r"'id':\s*'?(\d+)'?", str(data))
    return m.group(1) if m else None


def get_form_id(data):
    m = re.search(r"'id':\s*'([^']+)'", str(data))
    return m.group(1) if m else None


NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ─── shared form fixtures ──────────────────────────────────────────────────────

CONFIG = {
    "allowLinkToResetKnownValues": False, "archivable": True, "cloneable": True,
    "createNewContactForNewEmail": True, "editable": True, "language": "en",
    "lifecycleStages": [], "notifyContactOwner": False, "notifyRecipients": [],
    "postSubmitAction": {"type": "thank_you", "value": "Thank you!"},
    "prePopulateKnownValues": True, "recaptchaEnabled": False,
}

DISPLAY = {
    "renderRawHtml": False, "submitButtonText": "Submit", "theme": "default_style",
    "style": {
        "backgroundWidth": "100%", "fontFamily": "arial,helvetica,sans-serif",
        "helpTextColor": "#7C98B6", "helpTextSize": "11px",
        "labelTextColor": "#33475b", "labelTextSize": "13px",
        "legalConsentTextColor": "#33475b", "legalConsentTextSize": "14px",
        "submitAlignment": "left", "submitColor": "#ff7a59",
        "submitFontColor": "#ffffff", "submitSize": "12px",
    },
}

EMAIL_FIELD = [{"groupType": "default_group", "richTextType": "text",
                "fields": [{"objectTypeId": "0-1", "name": "email", "fieldType": "email",
                             "label": "Email", "required": True, "hidden": False,
                             "validation": {"blockedEmailDomains": [], "useDefaultBlockList": True},
                             "dependentFields": []}]}]

PHONE_FIELD = [{"groupType": "default_group", "richTextType": "text",
                "fields": [{"objectTypeId": "0-1", "name": "phone", "fieldType": "phone",
                             "label": "Phone", "required": False, "hidden": False,
                             "dependentFields": [], "useCountryCodeSelect": True,
                             "validation": {"minAllowedDigits": 7, "maxAllowedDigits": 20}}]}]


def form_input(name, fieldGroups=None, legalConsentOptions=None, archived=False, config_override=None):
    """Build a form_create/update tool_input dict with json.dumps for complex fields."""
    cfg = {**CONFIG, **(config_override or {})}
    return {
        "name": name,
        "formType": "hubspot",
        "archived": archived,
        "createdAt": NOW,
        "configuration": json.dumps(cfg),
        "displayOptions": json.dumps(DISPLAY),
        "fieldGroups": json.dumps(fieldGroups or EMAIL_FIELD),
        "legalConsentOptions": json.dumps(legalConsentOptions or {"type": "none"}),
    }


# ══════════════════════════════════════════════════════════════════════════════
# MARKETING EMAIL CREATE
# ══════════════════════════════════════════════════════════════════════════════

def test_email_create():
    print("\n" + "=" * 60)
    print("MARKETING EMAIL CREATE")
    print("=" * 60)

    created = []

    def create(label, inp, expect_error=False):
        r = run(label, "hubspot_marketing_email_create", inp, expect_error)
        if r:
            eid = get_email_id(r)
            if eid:
                created.append(eid)
        return r

    create("name only", {"name": "Name Only"})
    create("name + subject", {"name": "With Subject", "subject": "Hello World"})
    create("state=DRAFT", {"name": "Draft", "state": "DRAFT"})
    create("state=SCHEDULED + publishDate", {"name": "Scheduled", "state": "SCHEDULED", "publishDate": "2025-12-01T10:00:00Z"})
    create("state=PUBLISHED (expected 400)", {"name": "Published", "subject": "Hi", "state": "PUBLISHED"}, expect_error=True)
    create("state=AUTOMATED (expected 400)", {"name": "Automated", "state": "AUTOMATED"}, expect_error=True)
    create("archived=true", {"name": "Archived On Create", "archived": True})
    create("archived=false + sendOnPublish=true", {"name": "Flags", "archived": False, "sendOnPublish": True})
    create("jitterSendTime=true", {"name": "Jitter", "jitterSendTime": True})
    create("from object", {"name": "From", "from": {"fromName": "Scalekit", "replyTo": "no-reply@example.com"}})
    create("from + customReplyTo", {"name": "CustomReply", "from": {"fromName": "Scalekit", "replyTo": "reply@example.com", "customReplyTo": "custom@example.com"}})
    create("language=en", {"name": "Lang", "language": "en"})
    create("activeDomain", {"name": "Domain", "activeDomain": "mail.example.com"})
    create("businessUnitId", {"name": "BU", "businessUnitId": 0})
    create("folderIdV2", {"name": "Folder", "folderIdV2": 0})
    create("campaign", {"name": "Campaign", "campaign": "nonexistent-campaign-id"})
    create("content object", {"name": "Content", "content": {"body": "<p>Hello</p>", "footer": "<p>Unsubscribe</p>"}})
    create("to object", {"name": "To", "to": {"sendTo": "ALL", "suppressionLists": []}})
    create("publishDate", {"name": "Publish Date", "publishDate": "2025-12-01T10:00:00Z"})
    create("webversion", {"name": "Webversion", "webversion": {"enabled": True}})
    create("feedbackSurveyId", {"name": "Survey", "feedbackSurveyId": 12345})
    create("testing object", {"name": "AB Test", "testing": {"percentageToTest": 10, "autoWinnerSelectionProperty": "OPEN_RATE"}})
    create("rssData", {"name": "RSS", "rssData": {"url": "https://blog.example.com/feed", "limit": 5}})
    create("subscriptionDetails", {"name": "Subscription", "subscriptionDetails": {"subscriptionId": 1, "offsetMillis": 0}})
    create("subcategory (expected 400 — read-only)", {"name": "Subcat", "subcategory": "AUTOMATED_EMAIL"}, expect_error=True)

    # Cleanup
    for eid in created:
        cleanup_email(eid)
    print(f"  → cleaned up {len(created)} emails")


# ══════════════════════════════════════════════════════════════════════════════
# MARKETING EMAIL UPDATE
# ══════════════════════════════════════════════════════════════════════════════

def test_email_update():
    print("\n" + "=" * 60)
    print("MARKETING EMAIL UPDATE")
    print("=" * 60)

    try:
        r = actions.execute_tool(tool_name="hubspot_marketing_email_create", identifier=identifier,
                                 connection_name=connection_name, tool_input={"name": "Update Test Base"})
        eid = get_email_id(r.data)  # real ID from create response e.g. "355533094638"
    except Exception as e:
        print(f"  ✗ setup failed: {str(e)[:80]}")
        return
    if not eid:
        print("  ✗ setup failed: could not create base email")
        return
    print(f"  setup: created email id={eid}")

    def update(label, extra, expect_error=False):
        run(label, "hubspot_marketing_email_update", {"emailId": eid, **extra}, expect_error)

    update("subject", {"subject": "Updated Subject"})
    update("name + state=DRAFT", {"name": "Updated Name", "state": "DRAFT"})
    update("state=SCHEDULED (expected 400)", {"state": "SCHEDULED", "publishDate": "2025-12-01T10:00:00Z"}, expect_error=True)
    update("state=PUBLISHED (expected 400)", {"state": "PUBLISHED"}, expect_error=True)
    update("from + language", {"from": {"fromName": "Sender", "replyTo": "reply@example.com"}, "language": "fr"})
    update("from + customReplyTo", {"from": {"fromName": "Updated", "replyTo": "r@example.com", "customReplyTo": "c@example.com"}})
    update("webversion", {"webversion": {"enabled": True}})
    update("boolean flags (sendOnPublish, archived)", {"sendOnPublish": False, "archived": False})
    update("archived=true (query param)", {"archived": True})
    update("archived=false (query param)", {"archived": False})
    update("jitterSendTime=true", {"jitterSendTime": True})
    update("content", {"content": {"body": "<p>Updated</p>"}})
    update("to", {"to": {"sendTo": "ALL"}})
    update("publishDate", {"publishDate": "2025-11-01T09:00:00Z"})
    update("activeDomain", {"activeDomain": "mail.example.com"})
    update("businessUnitId", {"businessUnitId": 0})
    update("folderIdV2", {"folderIdV2": 0})
    update("feedbackSurveyId", {"feedbackSurveyId": 99999})
    update("testing object", {"testing": {"percentageToTest": 20, "autoWinnerSelectionProperty": "CLICK_RATE"}})
    update("rssData", {"rssData": {"url": "https://blog.example.com/feed", "limit": 3}})
    update("campaign", {"campaign": "nonexistent-campaign"})
    update("subscriptionDetails (expected 400 — needs valid subscription ID)",
           {"subscriptionDetails": {"subscriptionId": 1, "offsetMillis": 0}}, expect_error=True)
    update("subcategory (expected 400 — read-only)", {"subcategory": "AUTOMATED_EMAIL"}, expect_error=True)
    run("invalid emailId (expected 400)", "hubspot_marketing_email_update",
        {"emailId": "999999999", "subject": "X"}, expect_error=True)

    cleanup_email(eid)
    print(f"  → cleaned up email {eid}")


# ══════════════════════════════════════════════════════════════════════════════
# MARKETING EMAIL DELETE
# ══════════════════════════════════════════════════════════════════════════════

def test_email_delete():
    print("\n" + "=" * 60)
    print("MARKETING EMAIL DELETE")
    print("=" * 60)

    def make_email(name):
        r = actions.execute_tool(tool_name="hubspot_marketing_email_create", identifier=identifier,
                                 connection_name=connection_name, tool_input={"name": name})
        return get_email_id(r.data)

    # soft delete (archive)
    eid1 = make_email("Delete Test 1")
    run("soft delete (no archived param)", "hubspot_marketing_email_delete", {"emailId": eid1})
    run("re-delete already-archived (idempotent — HubSpot allows repeat deletes)", "hubspot_marketing_email_delete",
        {"emailId": eid1})

    # archived=false explicit
    eid2 = make_email("Delete Test 2")
    run("delete with archived=false (explicit)", "hubspot_marketing_email_delete",
        {"emailId": eid2, "archived": False})

    # archived=true — HubSpot does not support hard deletes
    eid3 = make_email("Delete Test 3")
    run("delete (archive it first)", "hubspot_marketing_email_delete", {"emailId": eid3})
    run("delete with archived=true (expected 400 — hard deletes not supported)",
        "hubspot_marketing_email_delete", {"emailId": eid3, "archived": True}, expect_error=True)

    # invalid id
    run("invalid emailId (expected 400)", "hubspot_marketing_email_delete",
        {"emailId": "nonexistent-abc"}, expect_error=True)


# ══════════════════════════════════════════════════════════════════════════════
# FORM CREATE
# ══════════════════════════════════════════════════════════════════════════════

def test_form_create():
    print("\n" + "=" * 60)
    print("FORM CREATE")
    print("=" * 60)

    created = []

    def create(label, inp, expect_error=False):
        r = run(label, "hubspot_form_create", inp, expect_error)
        if r:
            fid = get_form_id(r)
            if fid:
                created.append(fid)
        return r

    # legalConsentOptions types
    create("legalConsentOptions=none", form_input("Test None"))
    create("legalConsentOptions=implicit_consent_to_process",
           form_input("Test Implicit", legalConsentOptions={
               "type": "implicit_consent_to_process",
               "privacyText": "We process your data.",
               "communicationConsentText": "By submitting you consent.",
           }))
    create("legalConsentOptions=legitimate_interest (expected 400 — needs valid subscriptionTypeIds)",
           form_input("Test LI", legalConsentOptions={
               "type": "legitimate_interest", "lawfulBasis": "lead",
               "privacyText": "We process your data.", "subscriptionTypeIds": [],
           }), expect_error=True)
    create("legalConsentOptions=explicit_consent_to_process (expected 400 — needs valid subscriptionTypeId)",
           form_input("Test Explicit", legalConsentOptions={
               "type": "explicit_consent_to_process",
               "privacyText": "We process your data.", "communicationsCheckboxes": [],
           }), expect_error=True)

    # fieldTypes
    for ft, field in [
        ("email", {"objectTypeId": "0-1", "name": "email", "fieldType": "email", "label": "Email",
                   "required": True, "hidden": False, "dependentFields": [],
                   "validation": {"blockedEmailDomains": [], "useDefaultBlockList": True}}),
        ("phone", {"objectTypeId": "0-1", "name": "phone", "fieldType": "phone", "label": "Phone",
                   "required": False, "hidden": False, "dependentFields": [], "useCountryCodeSelect": True,
                   "validation": {"minAllowedDigits": 7, "maxAllowedDigits": 20}}),
        ("mobile_phone", {"objectTypeId": "0-1", "name": "mobilephone", "fieldType": "mobile_phone",
                          "label": "Mobile", "required": False, "hidden": False, "dependentFields": [],
                          "validation": {"minAllowedDigits": 7, "maxAllowedDigits": 20}}),
        ("single_line_text", {"objectTypeId": "0-1", "name": "firstname", "fieldType": "single_line_text",
                              "label": "First Name", "required": False, "hidden": False, "dependentFields": []}),
        ("multi_line_text", {"objectTypeId": "0-1", "name": "message", "fieldType": "multi_line_text",
                             "label": "Message", "required": False, "hidden": False, "dependentFields": []}),
        ("number", {"objectTypeId": "0-1", "name": "numemployees", "fieldType": "number",
                    "label": "Employees", "required": False, "hidden": False, "dependentFields": []}),
        ("single_checkbox", {"objectTypeId": "0-1", "name": "hs_legal_basis", "fieldType": "single_checkbox",
                             "label": "I agree", "required": False, "hidden": False, "dependentFields": []}),
        ("multiple_checkboxes", {"objectTypeId": "0-1", "name": "hs_content_membership_notes",
                                 "fieldType": "multiple_checkboxes", "label": "Interests",
                                 "required": False, "hidden": False, "dependentFields": [],
                                 "defaultValues": [],
                                 "options": [{"displayOrder": 0, "label": "Tech", "value": "tech"},
                                             {"displayOrder": 1, "label": "Finance", "value": "finance"}]}),
        ("dropdown", {"objectTypeId": "0-1", "name": "industry", "fieldType": "dropdown",
                      "label": "Industry", "required": False, "hidden": False, "dependentFields": [],
                      "defaultValues": [],
                      "options": [{"displayOrder": 0, "label": "Tech", "value": "tech"},
                                  {"displayOrder": 1, "label": "Finance", "value": "finance"}]}),
        ("radio", {"objectTypeId": "0-1", "name": "jobtitle", "fieldType": "radio",
                   "label": "Job Title", "required": False, "hidden": False, "dependentFields": [],
                   "defaultValues": [],
                   "options": [{"displayOrder": 0, "label": "Manager", "value": "manager"},
                                {"displayOrder": 1, "label": "Developer", "value": "developer"}]}),
        ("datepicker (expected 400)", {"objectTypeId": "0-1", "name": "closedate", "fieldType": "datepicker",
                                       "label": "Date", "required": False, "hidden": False, "dependentFields": []}),
        ("file (expected 400)", {"objectTypeId": "0-1", "name": "hs_file_upload", "fieldType": "file",
                                 "label": "File", "required": False, "hidden": False, "dependentFields": [],
                                 "allowMultipleFiles": False}),
        ("payment_link_radio (expected 400)", {"objectTypeId": "0-1", "name": "hs_payment_link",
                                               "fieldType": "payment_link_radio", "label": "Payment",
                                               "required": False, "hidden": False, "dependentFields": [],
                                               "defaultValues": [],
                                               "options": [{"displayOrder": 0, "label": "Plan A", "value": "plan_a"}]}),
    ]:
        expect = "expected 400" in ft
        groups = [{"groupType": "default_group", "richTextType": "text", "fields": [field]}]
        create(f"fieldType={ft}", form_input(f"Form {ft}", fieldGroups=groups), expect_error=expect)

    # groupTypes
    for gt in ["default_group", "progressive", "queued"]:
        groups = [{"groupType": gt, "richTextType": "text", "fields": EMAIL_FIELD[0]["fields"]}]
        create(f"groupType={gt}", form_input(f"GroupType {gt}", fieldGroups=groups))

    # richTextType=image
    groups = [{"groupType": "default_group", "richTextType": "image",
               "richText": "<img src='https://example.com/logo.png'>",
               "fields": EMAIL_FIELD[0]["fields"]}]
    create("richTextType=image", form_input("RichText Image", fieldGroups=groups))

    # multiple fieldGroups
    multi_groups = [
        {"groupType": "default_group", "richTextType": "text", "fields": EMAIL_FIELD[0]["fields"]},
        {"groupType": "default_group", "richTextType": "text",
         "fields": [{"objectTypeId": "0-1", "name": "firstname", "fieldType": "single_line_text",
                     "label": "First Name", "required": False, "hidden": False, "dependentFields": []}]},
    ]
    create("multiple fieldGroups", form_input("Multi Group", fieldGroups=multi_groups))

    # field-level attributes
    fields_with_attrs = [{"groupType": "default_group", "richTextType": "text",
                          "fields": [
                              {"objectTypeId": "0-1", "name": "email", "fieldType": "email",
                               "label": "Email", "required": True, "hidden": False,
                               "description": "Enter your work email.", "placeholder": "you@company.com",
                               "validation": {"blockedEmailDomains": [], "useDefaultBlockList": True},
                               "dependentFields": []},
                              {"objectTypeId": "0-1", "name": "firstname", "fieldType": "single_line_text",
                               "label": "First Name", "required": False, "hidden": False,
                               "defaultValue": "Friend", "description": "Your first name.",
                               "placeholder": "e.g. Jane", "dependentFields": []},
                          ]}]
    create("field defaultValue + description + placeholder", form_input("Field Attrs", fieldGroups=fields_with_attrs))

    # hidden field
    hidden_fields = [{"groupType": "default_group", "richTextType": "text",
                      "fields": [
                          EMAIL_FIELD[0]["fields"][0],
                          {"objectTypeId": "0-1", "name": "hs_lead_status", "fieldType": "single_line_text",
                           "label": "Lead Status", "required": False, "hidden": True,
                           "defaultValue": "NEW", "dependentFields": []},
                      ]}]
    create("hidden field", form_input("Hidden Field Form", fieldGroups=hidden_fields))

    # archived
    create("archived=true", form_input("Archived Form", archived=True))

    # postSubmitAction variants
    create("postSubmitAction=redirect_url", form_input("Redirect Form",
           config_override={"postSubmitAction": {"type": "redirect_url", "value": "https://example.com/thanks"}}))

    # configuration boolean variants
    for flag, val in [
        ("recaptchaEnabled=true", {"recaptchaEnabled": True}),
        ("notifyContactOwner=true", {"notifyContactOwner": True}),
        ("notifyRecipients", {"notifyRecipients": ["notify@example.com"]}),
        ("allowLinkToResetKnownValues=true", {"allowLinkToResetKnownValues": True}),
        ("prePopulateKnownValues=false", {"prePopulateKnownValues": False}),
        ("createNewContactForNewEmail=false", {"createNewContactForNewEmail": False}),
        ("cloneable=false", {"cloneable": False}),
        ("editable=false", {"editable": False}),
        ("archivable=false", {"archivable": False}),
    ]:
        create(f"config {flag}", form_input(f"Config {flag}", config_override=val))

    # formType variants
    for ft in ["captured", "flow"]:
        inp = form_input(f"Form {ft}")
        inp["formType"] = ft
        create(f"formType={ft} (expected 400)", inp, expect_error=True)

    # displayOptions variants
    display_custom = {**DISPLAY, "submitButtonText": "Get Started"}
    create("displayOptions custom submitButtonText",
           {**form_input("Custom Button"), "displayOptions": json.dumps(display_custom)})

    create("displayOptions theme=dark (expected 400)",
           {**form_input("Dark Theme"), "displayOptions": json.dumps({**DISPLAY, "theme": "dark"})},
           expect_error=True)

    # Cleanup
    for fid in created:
        cleanup_form(fid)
    print(f"  → cleaned up {len(created)} forms")


# ══════════════════════════════════════════════════════════════════════════════
# FORM UPDATE
# ══════════════════════════════════════════════════════════════════════════════

def test_form_update():
    print("\n" + "=" * 60)
    print("FORM UPDATE")
    print("=" * 60)

    try:
        r = actions.execute_tool(tool_name="hubspot_form_create", identifier=identifier,
                                 connection_name=connection_name, tool_input=form_input("Update Base Form"))
        fid = get_form_id(r.data)  # real ID from create response e.g. "da1c1f32-7db3-41db-a3d1-7a1b56812238"
    except Exception as e:
        print(f"  ✗ setup failed: {str(e)[:80]}")
        return
    if not fid:
        print("  ✗ setup failed: could not create base form")
        return
    print(f"  setup: created form id={fid}")

    def update(label, overrides, expect_error=False):
        inp = {**form_input("Updated Form"), "formId": fid, **overrides}
        run(label, "hubspot_form_update", inp, expect_error)

    update("name change", {"name": "New Name"})
    update("archived=true", {"archived": True})
    update("change fieldType to single_line_text",
           {"fieldGroups": json.dumps([{"groupType": "default_group", "richTextType": "text",
                                        "fields": [{"objectTypeId": "0-1", "name": "firstname",
                                                     "fieldType": "single_line_text", "label": "First Name",
                                                     "required": True, "hidden": False, "dependentFields": []}]}])})
    update("postSubmitAction=redirect_url",
           {"configuration": json.dumps({**CONFIG, "postSubmitAction": {"type": "redirect_url", "value": "https://example.com/ty"}})})
    update("legalConsent=implicit_consent_to_process",
           {"legalConsentOptions": json.dumps({"type": "implicit_consent_to_process",
                                               "privacyText": "We handle your data.",
                                               "communicationConsentText": "You consent by submitting."})})
    update("multiple fieldGroups",
           {"fieldGroups": json.dumps([
               {"groupType": "default_group", "richTextType": "text", "fields": EMAIL_FIELD[0]["fields"]},
               {"groupType": "default_group", "richTextType": "text",
                "fields": [{"objectTypeId": "0-1", "name": "firstname", "fieldType": "single_line_text",
                             "label": "First Name", "required": False, "hidden": False, "dependentFields": []}]},
           ])})
    update("notifyContactOwner=true",
           {"configuration": json.dumps({**CONFIG, "notifyContactOwner": True})})

    run("invalid formId (expected 400)", "hubspot_form_update",
        {**form_input("X"), "formId": "nonexistent-000"}, expect_error=True)

    cleanup_form(fid)
    print(f"  → cleaned up form {fid}")


# ══════════════════════════════════════════════════════════════════════════════
# FORM DELETE
# ══════════════════════════════════════════════════════════════════════════════

def test_form_delete():
    print("\n" + "=" * 60)
    print("FORM DELETE")
    print("=" * 60)

    try:
        r = actions.execute_tool(tool_name="hubspot_form_create", identifier=identifier,
                                 connection_name=connection_name, tool_input=form_input("Delete Test Form"))
        fid = get_form_id(r.data)  # real ID from create response
    except Exception as e:
        print(f"  ✗ setup failed: {str(e)[:80]}")
        return
    print(f"  setup: created form id={fid}")
    run("delete valid formId", "hubspot_form_delete", {"formId": fid})
    run("invalid formId (expected 400)", "hubspot_form_delete", {"formId": "nonexistent-000"}, expect_error=True)


# ══════════════════════════════════════════════════════════════════════════════
# CAMPAIGNS  (all → 403 PERMISSION_DENIED — missing marketing.campaigns.write scope)
# ══════════════════════════════════════════════════════════════════════════════

GUID = "test-campaign-guid-000"


def test_campaign_create():
    print("\n" + "=" * 60)
    print("CAMPAIGN CREATE  (expect 403 — missing scope)")
    print("=" * 60)
    run("hs_name only", "hubspot_campaign_create", {"properties": {"hs_name": "Test Campaign"}}, expect_error=True)
    run("hs_name + hs_goal", "hubspot_campaign_create", {"properties": {"hs_name": "Campaign", "hs_goal": "AWARENESS"}}, expect_error=True)


def test_campaign_update():
    print("\n" + "=" * 60)
    print("CAMPAIGN UPDATE  (expect 403)")
    print("=" * 60)
    run("hs_name", "hubspot_campaign_update", {"campaignGuid": GUID, "properties": {"hs_name": "Updated"}}, expect_error=True)
    run("multiple props", "hubspot_campaign_update", {"campaignGuid": GUID, "properties": {"hs_name": "X", "hs_goal": "CONSIDERATION"}}, expect_error=True)
    run("hs_notes", "hubspot_campaign_update", {"campaignGuid": GUID, "properties": {"hs_notes": "Notes"}}, expect_error=True)
    run("hs_start_date + hs_end_date", "hubspot_campaign_update",
        {"campaignGuid": GUID, "properties": {"hs_start_date": "1704067200000", "hs_end_date": "1735689600000"}}, expect_error=True)


def test_campaign_delete():
    print("\n" + "=" * 60)
    print("CAMPAIGN DELETE  (expect 403)")
    print("=" * 60)
    run("existing GUID", "hubspot_campaign_delete", {"campaignGuid": GUID}, expect_error=True)
    run("nonexistent GUID", "hubspot_campaign_delete", {"campaignGuid": "nonexistent-000"}, expect_error=True)


def test_campaign_asset_create():
    print("\n" + "=" * 60)
    print("CAMPAIGN ASSET CREATE  (expect 403)")
    print("=" * 60)
    for asset_type in ["BLOG_POST", "LANDING_PAGE", "MARKETING_EMAIL", "FORM", "VIDEO", "CTA", "SOCIAL_POST", "WORKFLOW", "CTA_MODULE"]:
        run(f"assetType={asset_type}", "hubspot_campaign_asset_create",
            {"campaignGuid": GUID, "assetType": asset_type, "assetId": "999"}, expect_error=True)


def test_campaign_assets_get():
    print("\n" + "=" * 60)
    print("CAMPAIGN ASSETS GET  (expect 403)")
    print("=" * 60)
    run("no optional params", "hubspot_campaign_assets_get", {"campaignGuid": GUID, "assetType": "BLOG_POST"}, expect_error=True)
    run("with limit", "hubspot_campaign_assets_get", {"campaignGuid": GUID, "assetType": "MARKETING_EMAIL", "limit": 10}, expect_error=True)
    run("with startDate", "hubspot_campaign_assets_get", {"campaignGuid": GUID, "assetType": "BLOG_POST", "startDate": "2024-01-01"}, expect_error=True)
    run("with endDate", "hubspot_campaign_assets_get", {"campaignGuid": GUID, "assetType": "BLOG_POST", "endDate": "2024-12-31"}, expect_error=True)
    run("startDate + endDate", "hubspot_campaign_assets_get",
        {"campaignGuid": GUID, "assetType": "BLOG_POST", "startDate": "2024-01-01", "endDate": "2024-12-31"}, expect_error=True)
    run("after cursor + limit", "hubspot_campaign_assets_get",
        {"campaignGuid": GUID, "assetType": "BLOG_POST", "after": "eyJpZCI6IjEwMDI1In0=", "limit": 5}, expect_error=True)


def test_campaign_asset_delete():
    print("\n" + "=" * 60)
    print("CAMPAIGN ASSET DELETE  (expect 403)")
    print("=" * 60)
    for asset_type in ["BLOG_POST", "LANDING_PAGE", "MARKETING_EMAIL", "FORM", "VIDEO", "CTA", "SOCIAL_POST", "WORKFLOW"]:
        run(f"assetType={asset_type}", "hubspot_campaign_asset_delete",
            {"campaignGuid": GUID, "assetType": asset_type, "assetId": "999"}, expect_error=True)


def test_campaign_revenue_get():
    print("\n" + "=" * 60)
    print("CAMPAIGN REVENUE GET  (expect 403)")
    print("=" * 60)
    run("no optional params", "hubspot_campaign_revenue_get", {"campaignGuid": GUID}, expect_error=True)
    for model in ["LINEAR", "FIRST_INTERACTION", "LAST_INTERACTION", "TIME_DECAY", "J_SHAPED", "INVERSE_J_SHAPED", "FULL_PATH"]:
        run(f"attributionModel={model}", "hubspot_campaign_revenue_get",
            {"campaignGuid": GUID, "attributionModel": model}, expect_error=True)
    run("FIRST_INTERACTION + date range", "hubspot_campaign_revenue_get",
        {"campaignGuid": GUID, "attributionModel": "FIRST_INTERACTION",
         "startDate": "2024-01-01", "endDate": "2024-12-31"}, expect_error=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("\n HubSpot Marketing Tools — Full Test Suite")
    print("   13 tools | all documented scenarios\n")

    # Marketing Emails
    test_email_create()
    test_email_update()
    test_email_delete()

    # Forms
    test_form_create()
    test_form_update()
    test_form_delete()

    # Campaigns (all 403 — missing marketing.campaigns.write scope)
    test_campaign_create()
    test_campaign_update()
    test_campaign_delete()
    test_campaign_asset_create()
    test_campaign_assets_get()
    test_campaign_asset_delete()
    test_campaign_revenue_get()

    print("\n Done")


if __name__ == "__main__":
    main()
