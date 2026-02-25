#!/usr/bin/env python3
"""
WhatsApp Watcher - Gold Tier Component
Monitors WhatsApp Web for unread messages and creates action items.
"""

import os
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
from Scripts.retry_handler import with_retry

# Paths
VAULT_ROOT = Path(__file__).parent
NEEDS_ACTION = VAULT_ROOT / 'Needs_Action' / 'Business'
USER_DATA = VAULT_ROOT / 'user_data'
SESSION_PATH = USER_DATA / 'whatsapp_session'

def setup_directories():
    """Create necessary directories if they don't exist."""
    NEEDS_ACTION.mkdir(parents=True, exist_ok=True)
    USER_DATA.mkdir(parents=True, exist_ok=True)
    SESSION_PATH.mkdir(parents=True, exist_ok=True)


def create_action_file(sender, message_text):
    """Create a markdown file in Needs_Action for unread messages."""
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

*Auto-detected by WhatsApp Watcher*
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[ACTION] Created: {filename}")
    return filename


@with_retry(max_attempts=3)
def navigate_to_whatsapp(page):
    """Navigate to WhatsApp Web with retry logic."""
    page.goto('https://web.whatsapp.com', timeout=0)


@with_retry(max_attempts=3)
def scan_whatsapp_messages(page):
    """Scan WhatsApp Web for all unread messages and extract them."""
    try:
        print("[WATCHER] Scanning for unread messages...")

        # Wait for chat list to load
        time.sleep(3)

        # Click the "Unread chats filter" button to show only unread chats
        try:
            print("[INFO] Looking for unread filter button...")
            # Try exact match first
            unread_filter = page.query_selector('[aria-label="Unread chats filter"]')

            # Fallback to fuzzy matching if exact match fails
            if not unread_filter:
                unread_filter = page.query_selector('[aria-label*="Unread" i][role="button"], button[aria-label*="Unread" i]')

            if unread_filter:
                print("[INFO] Clicking unread filter button...")
                unread_filter.click()
                time.sleep(3)  # Wait for filter to apply
                print("[SUCCESS] Unread filter applied")
            else:
                print("[WARNING] Unread filter button not found, scanning all chats")
        except Exception as e:
            print(f"[WARNING] Could not click unread filter: {e}")

        # Take debug screenshot after filtering
        debug_path = VAULT_ROOT / 'debug_whatsapp.png'
        page.screenshot(path=str(debug_path))
        print(f"[DEBUG] Screenshot saved to: {debug_path}")

        # Strategy 1: Look for elements with aria-label containing "unread" (case-insensitive)
        unread_chats = page.query_selector_all('[aria-label*="unread" i]')

        # Strategy 2: If no results, look for unread badge indicators (green dots/counters)
        if not unread_chats:
            print("[DEBUG] Strategy 1 failed, trying badge selectors...")
            unread_chats = page.query_selector_all('span[data-testid="icon-unread-count"], span[aria-label][data-icon="unread-count"]')

        # Strategy 3: Look for chat items with unread status
        if not unread_chats:
            print("[DEBUG] Strategy 2 failed, trying chat container selectors...")
            unread_chats = page.query_selector_all('[data-testid="cell-frame-container"]:has(span[data-testid="icon-unread-count"])')

        # Strategy 4: Look for any element with role and unread in aria-label
        if not unread_chats:
            print("[DEBUG] Strategy 3 failed, trying role-based selectors...")
            all_elements = page.query_selector_all('[role="listitem"], [role="row"]')
            unread_chats = [elem for elem in all_elements if 'unread' in (elem.get_attribute('aria-label') or '').lower()]

        if not unread_chats:
            print("[INFO] No unread messages found with any detection strategy.")
            return 0

        print(f"[INFO] Found {len(unread_chats)} unread chat(s)")
        action_count = 0

        for chat in unread_chats[:10]:  # Limit to first 10 unread chats
            try:
                # Click on the chat to open it in main window
                print("[DEBUG] Clicking chat to open...")
                chat.click()
                time.sleep(2)  # Wait for chat pane to load

                # Get chat title (sender name) with multiple strategies
                sender = "Unknown Sender"
                try:
                    # Strategy 1: conversation-header
                    title_elem = page.query_selector('[data-testid="conversation-header"]')
                    if title_elem:
                        sender = title_elem.inner_text().split('\n')[0]

                    # Strategy 2: header-title
                    if sender == "Unknown Sender":
                        title_elem = page.query_selector('[data-testid="header-title"]')
                        if title_elem:
                            sender = title_elem.inner_text().split('\n')[0]
                except Exception as e:
                    print(f"[WARNING] Could not extract sender name: {e}")

                print(f"[INFO] Processing chat from: {sender}")

                # Extract the last incoming message with bulletproof selectors
                message_text = None

                # Strategy 1: Look for elements with data-pre-plain-text (most reliable)
                try:
                    messages_with_metadata = page.query_selector_all('[data-pre-plain-text]')
                    if messages_with_metadata:
                        # Get the last message
                        last_msg_elem = messages_with_metadata[-1]
                        # The actual message text is in a sibling or child span
                        message_text = last_msg_elem.inner_text()
                        print(f"[DEBUG] Extracted message using data-pre-plain-text strategy")
                except Exception as e:
                    print(f"[DEBUG] Strategy 1 (data-pre-plain-text) failed: {e}")

                # Strategy 2: Look for div.message-in (incoming messages)
                if not message_text:
                    try:
                        incoming_messages = page.query_selector_all('div.message-in')
                        if incoming_messages:
                            last_msg_elem = incoming_messages[-1]
                            message_text = last_msg_elem.inner_text()
                            print(f"[DEBUG] Extracted message using div.message-in strategy")
                    except Exception as e:
                        print(f"[DEBUG] Strategy 2 (div.message-in) failed: {e}")

                # Strategy 3: Look for message containers with copyable-text
                if not message_text:
                    try:
                        copyable_messages = page.query_selector_all('span[data-testid="msg-container"] span.copyable-text')
                        if copyable_messages:
                            last_msg_elem = copyable_messages[-1]
                            message_text = last_msg_elem.inner_text()
                            print(f"[DEBUG] Extracted message using copyable-text strategy")
                    except Exception as e:
                        print(f"[DEBUG] Strategy 3 (copyable-text) failed: {e}")

                # Strategy 4: Fallback to any message container
                if not message_text:
                    try:
                        messages = page.query_selector_all('[data-testid="msg-container"]')
                        if messages:
                            last_msg_elem = messages[-1]
                            message_text = last_msg_elem.inner_text()
                            print(f"[DEBUG] Extracted message using msg-container fallback")
                    except Exception as e:
                        print(f"[DEBUG] Strategy 4 (msg-container) failed: {e}")

                # Create action file if we successfully extracted a message
                if message_text and message_text.strip():
                    create_action_file(sender, message_text)
                    action_count += 1
                    print(f"[SUCCESS] Extracted and saved message from {sender}")
                else:
                    print(f"[WARNING] No messages found in chat with {sender}")

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
                channel='chrome',
                args=['--disable-blink-features=AutomationControlled', '--disable-extensions'],
                ignore_default_args=['--enable-automation'],
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            )

            page = browser.pages[0] if browser.pages else browser.new_page()

            print("[WATCHER] Navigating to WhatsApp Web...")
            navigate_to_whatsapp(page)

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

            # Continuous monitoring loop
            check_count = 0
            print("[SUCCESS] WhatsApp watcher is now running continuously...")

            while True:
                try:
                    check_count += 1
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Check #{check_count} - Scanning WhatsApp messages...")

                    # Scan for unread messages
                    action_count = scan_whatsapp_messages(page)

                    if action_count > 0:
                        print(f"[SUCCESS] Created {action_count} action item(s)")
                    else:
                        print("[INFO] No unread messages found.")

                    print("[INFO] Next check in 15 seconds...\n")
                    time.sleep(15)

                except KeyboardInterrupt:
                    print("\n[STOPPED] WhatsApp watcher stopped by user.")
                    break
                except Exception as e:
                    print(f"[ERROR] Error in monitoring loop: {e}")
                    print("[INFO] Retrying in 15 seconds...\n")
                    time.sleep(15)

            browser.close()

        except Exception as e:
            print(f"[ERROR] WhatsApp watcher failed: {e}")
            raise


if __name__ == '__main__':
    run_whatsapp_watcher()
