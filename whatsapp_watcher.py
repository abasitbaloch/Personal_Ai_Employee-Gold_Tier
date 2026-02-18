#!/usr/bin/env python3
"""
WhatsApp Watcher - Gold Tier Component
Monitors WhatsApp Web for urgent business messages and creates action items.
"""

import os
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

# Paths
VAULT_ROOT = Path(__file__).parent
NEEDS_ACTION = VAULT_ROOT / 'Needs_Action' / 'Business'
USER_DATA = VAULT_ROOT / 'user_data'
SESSION_PATH = USER_DATA / 'whatsapp_session'

# Keywords to monitor
URGENT_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'client']


def setup_directories():
    """Create necessary directories if they don't exist."""
    NEEDS_ACTION.mkdir(parents=True, exist_ok=True)
    USER_DATA.mkdir(parents=True, exist_ok=True)
    SESSION_PATH.mkdir(parents=True, exist_ok=True)


def check_for_keywords(text):
    """Check if text contains any urgent keywords."""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in URGENT_KEYWORDS)


def create_action_file(sender, message_text):
    """Create a markdown file in Needs_Action for urgent messages."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"WHATSAPP_MSG_{timestamp}.md"
    filepath = NEEDS_ACTION / filename

    content = f"""# WhatsApp Message - Action Required

**Platform:** WhatsApp
**Sender:** {sender}
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Message Content

{message_text}

---

**Status:** Pending Review
**Priority:** High (Contains urgent keywords)

*Auto-detected by WhatsApp Watcher*
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[ACTION] Created: {filename}")
    return filename


def scan_whatsapp_messages(page):
    """Scan WhatsApp Web for unread messages with urgent keywords."""
    try:
        print("[WATCHER] Scanning for unread messages...")

        # Wait for chat list to load
        time.sleep(3)

        # Look for unread message indicators
        unread_chats = page.query_selector_all('[aria-label*="unread"]')

        if not unread_chats:
            print("[INFO] No unread messages found.")
            return 0

        print(f"[INFO] Found {len(unread_chats)} unread chat(s)")
        action_count = 0

        for chat in unread_chats[:10]:  # Limit to first 10 unread chats
            try:
                # Click on the chat
                chat.click()
                time.sleep(2)

                # Get chat title (sender name)
                title_elem = page.query_selector('[data-testid="conversation-header"]')
                sender = title_elem.inner_text().split('\n')[0] if title_elem else "Unknown Sender"

                # Get unread messages in this chat
                messages = page.query_selector_all('[data-testid="msg-container"]')

                for msg in messages[-5:]:  # Check last 5 messages
                    try:
                        message_text = msg.inner_text()

                        if check_for_keywords(message_text):
                            create_action_file(sender, message_text)
                            action_count += 1

                    except Exception as e:
                        print(f"[WARNING] Error reading message: {e}")
                        continue

            except Exception as e:
                print(f"[WARNING] Error processing chat: {e}")
                continue

        return action_count

    except Exception as e:
        print(f"[ERROR] Error scanning messages: {e}")
        return 0


def run_whatsapp_watcher():
    """Main function to run WhatsApp watcher."""
    setup_directories()

    print("[WATCHER] Starting WhatsApp Watcher...")
    print(f"[INFO] Session path: {SESSION_PATH}")

    with sync_playwright() as p:
        try:
            # Launch browser with persistent context
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(SESSION_PATH),
                headless=False,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )

            page = browser.pages[0] if browser.pages else browser.new_page()

            print("[WATCHER] Navigating to WhatsApp Web...")
            page.goto('https://web.whatsapp.com', timeout=60000)

            # Wait for WhatsApp to load (either QR code or chat list)
            print("[INFO] Waiting for WhatsApp to load...")
            print("[INFO] If this is your first time, please scan the QR code.")

            # Wait for either QR code or chat list
            try:
                page.wait_for_selector('[data-testid="chat-list"], canvas', timeout=30000)
                time.sleep(5)  # Additional wait for full load
            except:
                print("[WARNING] Timeout waiting for WhatsApp to load. Continuing anyway...")

            # Check if logged in
            if page.query_selector('canvas'):
                print("[WARNING] QR code detected. Please scan to log in.")
                print("[INFO] Waiting 60 seconds for login...")
                time.sleep(60)

            # Scan for urgent messages
            action_count = scan_whatsapp_messages(page)

            print(f"[SUCCESS] WhatsApp scan complete!")
            print(f"[INFO] Created {action_count} action item(s)")

            browser.close()

        except Exception as e:
            print(f"[ERROR] WhatsApp watcher failed: {e}")
            raise


if __name__ == '__main__':
    run_whatsapp_watcher()
