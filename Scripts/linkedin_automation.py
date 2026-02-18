#!/usr/bin/env python3
"""
LinkedIn Automation Script - Silver Tier HITL Compliant
Prepares a LinkedIn post draft but does NOT publish (respects Human-In-The-Loop)
"""

import sys
import time
from playwright.sync_api import sync_playwright

def read_post_content(file_path):
    """Read the post content from the approved draft file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

def prepare_linkedin_post(post_content):
    """
    Navigate to LinkedIn and prepare the post draft.
    Does NOT click the Post button (HITL compliance).
    """
    with sync_playwright() as p:
        # Launch browser in headed mode so user can see the draft
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        try:
            # Navigate to LinkedIn
            print("Navigating to LinkedIn...")
            page.goto("https://www.linkedin.com/feed/")

            # Wait for user to log in if needed
            print("Waiting for LinkedIn to load...")
            print("If you're not logged in, please log in manually.")
            time.sleep(5)

            # Click on "Start a post" button
            print("Looking for 'Start a post' button...")
            try:
                # Common selectors for LinkedIn's post button
                start_post_selectors = [
                    "button:has-text('Start a post')",
                    "[aria-label*='Start a post']",
                    ".share-box-feed-entry__trigger"
                ]

                for selector in start_post_selectors:
                    try:
                        page.click(selector, timeout=3000)
                        print("Clicked 'Start a post' button")
                        break
                    except:
                        continue

                time.sleep(2)

                # Find the post text area and fill it
                print("Filling in post content...")
                text_area_selectors = [
                    "[contenteditable='true']",
                    ".ql-editor",
                    "[role='textbox']"
                ]

                for selector in text_area_selectors:
                    try:
                        page.fill(selector, post_content, timeout=3000)
                        print("Post content filled successfully!")
                        break
                    except:
                        continue

                print("\n" + "="*60)
                print("DRAFT PREPARED - HUMAN REVIEW REQUIRED")
                print("="*60)
                print("\nThe post has been prepared in your browser.")
                print("Please review the content carefully.")
                print("\nIMPORTANT: This script will NOT click 'Post' automatically.")
                print("If you want to publish, click the 'Post' button manually.")
                print("\nPress Enter to close the browser...")
                input()

            except Exception as e:
                print(f"Error preparing post: {e}")
                print("Browser will remain open for manual intervention.")
                print("Press Enter to close...")
                input()

        finally:
            browser.close()
            print("Browser closed.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python linkedin_automation.py <path_to_post_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    print(f"Reading post content from: {file_path}")

    post_content = read_post_content(file_path)
    print(f"Post content loaded ({len(post_content)} characters)")

    prepare_linkedin_post(post_content)
    print("\nLinkedIn automation completed.")

if __name__ == "__main__":
    main()
