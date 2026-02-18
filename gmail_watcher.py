"""Gmail Watcher — Polls Gmail for unread messages and routes them to /Needs_Action as markdown."""

import time
import base64
import traceback
from datetime import datetime, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

VAULT_ROOT = Path(__file__).resolve().parent
NEEDS_ACTION = VAULT_ROOT / "Needs_Action"
CREDENTIALS_FILE = VAULT_ROOT / "credentials.json"
TOKEN_FILE = VAULT_ROOT / "token.json"
ERROR_LOG = VAULT_ROOT / "Logs" / "watcher_errors.txt"

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
POLL_INTERVAL = 60  # seconds
QUERY = "is:unread"


def log_error(message: str):
    """Append a timestamped error entry to /Logs/watcher_errors.txt."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    try:
        ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [GMAIL] {message}\n")
    except Exception:
        print(f"[FATAL]  Cannot write to error log: {message}")


def authenticate():
    """Authenticate with Gmail API using credentials.json / token.json."""
    creds = None

    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        except Exception as e:
            print(f"[WARN]   Existing token invalid, re-authenticating: {e}")
            creds = None

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            print(f"[WARN]   Token refresh failed, re-authenticating: {e}")
            creds = None

    if not creds or not creds.valid:
        if not CREDENTIALS_FILE.exists():
            msg = f"credentials.json not found at {CREDENTIALS_FILE}"
            print(f"[ERROR]  {msg}")
            log_error(msg)
            raise FileNotFoundError(msg)

        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
        creds = flow.run_local_server(port=0)

    # Save token for future runs
    try:
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    except Exception as e:
        print(f"[WARN]   Could not save token.json: {e}")

    return creds


def get_message_detail(service, msg_id: str) -> dict:
    """Fetch full message details by ID."""
    msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()

    headers = {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}

    sender = headers.get("from", "Unknown Sender")
    subject = headers.get("subject", "(No Subject)")
    date_str = headers.get("date", "")
    snippet = msg.get("snippet", "")

    # Parse the date into a clean timestamp
    received = date_str if date_str else datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    return {
        "id": msg_id,
        "from": sender,
        "subject": subject,
        "received": received,
        "snippet": snippet,
    }


def mark_as_read(service, msg_id: str):
    """Remove the UNREAD label from a message."""
    service.users().messages().modify(
        userId="me",
        id=msg_id,
        body={"removeLabelIds": ["UNREAD"]},
    ).execute()


def create_email_markdown(detail: dict):
    """Write an EMAIL_[message_id].md file into /Needs_Action."""
    NEEDS_ACTION.mkdir(parents=True, exist_ok=True)

    filename = f"EMAIL_{detail['id']}.md"
    filepath = NEEDS_ACTION / filename

    content = (
        f"# Email Alert\n\n"
        f"type: email\n"
        f"from: {detail['from']}\n"
        f"subject: {detail['subject']}\n"
        f"received: {detail['received']}\n"
        f"priority: high\n"
        f"status: pending\n\n"
        f"## Email Content\n\n"
        f"{detail['snippet']}\n\n"
        f"## Suggested Actions\n\n"
        f"- [ ] Reply to sender\n"
        f"- [ ] Forward to relevant party\n"
        f"- [ ] Archive after processing\n"
    )

    filepath.write_text(content, encoding="utf-8")
    return filename


def poll_inbox(service):
    """Check for unread messages and process them."""
    try:
        results = service.users().messages().list(userId="me", q=QUERY).execute()
    except Exception as e:
        msg = f"Failed to query Gmail: {e}"
        print(f"[ERROR]  {msg}")
        log_error(msg)
        return

    messages = results.get("messages", [])

    if not messages:
        print("[POLL]   No unread messages.")
        return

    print(f"[POLL]   Found {len(messages)} unread message(s).")

    for msg_ref in messages:
        msg_id = msg_ref["id"]

        # Skip if already processed (file exists in Needs_Action)
        if (NEEDS_ACTION / f"EMAIL_{msg_id}.md").exists():
            continue

        try:
            detail = get_message_detail(service, msg_id)
        except Exception as e:
            msg = f"Failed to fetch message {msg_id}: {e}"
            print(f"[ERROR]  {msg}")
            log_error(msg)
            continue

        try:
            filename = create_email_markdown(detail)
            print(f"[EMAIL]  {filename} created — from: {detail['from']}")
        except Exception as e:
            msg = f"Failed to create markdown for {msg_id}: {e}"
            print(f"[ERROR]  {msg}")
            log_error(msg)
            continue

        try:
            mark_as_read(service, msg_id)
            print(f"[READ]   {msg_id} marked as read")
        except Exception as e:
            msg = f"Failed to mark {msg_id} as read: {e}"
            print(f"[ERROR]  {msg}")
            log_error(msg)


def main():
    NEEDS_ACTION.mkdir(parents=True, exist_ok=True)
    ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)

    print("[AUTH]   Authenticating with Gmail API...")
    try:
        creds = authenticate()
    except Exception as e:
        msg = f"Authentication failed: {e}\n{traceback.format_exc()}"
        print(f"[FATAL]  {msg}")
        log_error(msg)
        return

    try:
        service = build("gmail", "v1", credentials=creds)
    except Exception as e:
        msg = f"Failed to build Gmail service: {e}\n{traceback.format_exc()}"
        print(f"[FATAL]  {msg}")
        log_error(msg)
        return

    print(f"[START]  Gmail watcher active — polling every {POLL_INTERVAL}s")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            poll_inbox(service)
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\n[STOP]   Gmail watcher stopped.")
    except Exception as e:
        msg = f"Gmail watcher crashed: {e}\n{traceback.format_exc()}"
        print(f"[CRASH]  {msg}")
        log_error(msg)


if __name__ == "__main__":
    main()
