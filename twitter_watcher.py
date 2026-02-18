#!/usr/bin/env python3
"""
Twitter (X) Watcher - Gold Tier Component
Monitors Twitter/X DMs for business-related messages and creates action items.
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
SESSION_PATH = USER_DATA / 'twitter_session'

# Keywords to monitor
BUSINESS_KEYWORDS = ['client', 'project', 'sale', 'urgent', 'business', 'opportunity']


def setup_directories():
    """Create necessary directories if they don't exist."""
    NEEDS_ACTION.mkdir(parents=True, exist_ok=True)
    USER_DATA.mkdir(parents=True, exist_ok=True)
    SESSION_PATH.mkdir(parents=True, exist_ok=True)


def check_for_keywords(text):
    """Check if text contains any business keywords."""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in BUSINESS_KEYWORDS)


def create_action_file(sender, message_text):
    """Create a markdown file in Needs_Action for business messages."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"TWITTER_MSG_{timestamp}.md"
    filepath = NEEDS_ACTION / filename

    content = f"""# Twitter/X Message - Action Required

**Platform:** Twitter/X
**Sender:** {sender}
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Message Content

{message_text}

---

**Status:** Pending Review
**Priority:** High (Contains business keywords)

*Auto-detected by Twitter Watcher*
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[ACTION] Created: {filename}")
    return filename


def scan_twitter_messages(page):
    """Scan Twitter/X DMs for unread messages with business keywords."""
    try:
        print("[WATCHER] Scanning for unread messages...")

        # Wait for messages to load
        time.sleep(3)

        # Look for conversation list
        conversations = page.query_selector_all('[data-testid="conversation"]')

        if not conversations:
            print("[INFO] No conversations found.")
            return 0

        print(f"[INFO] Found {len(conversations)} conversation(s)")
        action_count = 0

        for conv in conversations[:10]:  # Limit to first 10 conversations
            try:
                # Check if conversation has unread indicator
                has_unread = conv.query_selector('[data-testid="unread-indicator"]')

                if not has_unread:
                    continue

                # Click on the conversation
                conv.click()
                time.sleep(2)

                # Get sender name from conversation header
                header = page.query_selector('[data-testid="conversation-header"]')
                sender = header.inner_text().split('\n')[0] if header else "Unknown Sender"

                # Get messages in this conversation
                messages = page.query_selector_all('[data-testid="messageEntry"]')

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
                print(f"[WARNING] Error processing conversation: {e}")
                continue

        return action_count

    except Exception as e:
        print(f"[ERROR] Error scanning messages: {e}")
        return 0


def run_twitter_watcher():
    """Main function to run Twitter watcher."""
    setup_directories()

    print("[WATCHER] Starting Twitter/X Watcher...")
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

            print("[WATCHER] Navigating to Twitter/X Messages...")
            page.goto('https://x.com/messages', timeout=60000)

            # Wait for page to load
            print("[INFO] Waiting for Twitter/X to load...")
            print("[INFO] If not logged in, please log in manually.")

            # Wait for either login form or messages
            try:
                page.wait_for_selector('[data-testid="conversation"], [data-testid="LoginForm"]', timeout=30000)
                time.sleep(5)  # Additional wait for full load
            except:
                print("[WARNING] Timeout waiting for Twitter/X to load. Continuing anyway...")

            # Check if login is required
            if page.query_selector('[data-testid="LoginForm"]'):
                print("[WARNING] Login required. Please log in manually.")
                print("[INFO] Waiting 60 seconds for login...")
                time.sleep(60)

            # Scan for business messages
            action_count = scan_twitter_messages(page)

            print(f"[SUCCESS] Twitter/X scan complete!")
            print(f"[INFO] Created {action_count} action item(s)")

            browser.close()

        except Exception as e:
            print(f"[ERROR] Twitter watcher failed: {e}")
            raise


if __name__ == '__main__':
    run_twitter_watcher()
