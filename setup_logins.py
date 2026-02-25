"""
Login Setup Script for Social Media Watchers
Opens persistent browser contexts for WhatsApp, Twitter, and Facebook
"""

from playwright.sync_api import sync_playwright
import os

def main():
    # Define user data directories
    user_data_dirs = {
        'whatsapp': './user_data/whatsapp_session',
        'twitter': './user_data/twitter_session',
        'facebook': './user_data/facebook_session'
    }

    # Create user_data directory if it doesn't exist
    os.makedirs('./user_data', exist_ok=True)

    # URLs for each platform
    urls = {
        'whatsapp': 'https://web.whatsapp.com',
        'twitter': 'https://x.com/messages',
        'facebook': 'https://www.messenger.com/'
    }

    print("Launching browsers for login setup...")
    print("=" * 60)

    with sync_playwright() as p:
        # Create persistent contexts
        contexts = {}
        pages = {}

        try:
            # Browser 1: WhatsApp
            print("[1/3] Opening WhatsApp Web...")
            contexts['whatsapp'] = p.chromium.launch_persistent_context(
                user_data_dirs['whatsapp'],
                headless=False,
                channel='chrome',
                args=['--disable-blink-features=AutomationControlled', '--disable-extensions'],
                ignore_default_args=['--enable-automation'],
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            )
            pages['whatsapp'] = contexts['whatsapp'].pages[0] if contexts['whatsapp'].pages else contexts['whatsapp'].new_page()
            pages['whatsapp'].goto(urls['whatsapp'], timeout=0, wait_until='domcontentloaded')

            # Browser 2: Twitter/X
            print("[2/3] Opening Twitter/X Messages...")
            contexts['twitter'] = p.chromium.launch_persistent_context(
                user_data_dirs['twitter'],
                headless=False,
                channel='chrome',
                args=['--disable-blink-features=AutomationControlled', '--disable-extensions'],
                ignore_default_args=['--enable-automation'],
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            )
            pages['twitter'] = contexts['twitter'].pages[0] if contexts['twitter'].pages else contexts['twitter'].new_page()
            pages['twitter'].goto(urls['twitter'], timeout=0, wait_until='domcontentloaded')

            # Browser 3: Facebook
            print("[3/3] Opening Facebook Messenger...")
            contexts['facebook'] = p.chromium.launch_persistent_context(
                user_data_dirs['facebook'],
                headless=False,
                channel='chrome',
                args=['--disable-blink-features=AutomationControlled', '--disable-extensions'],
                ignore_default_args=['--enable-automation'],
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            )
            pages['facebook'] = contexts['facebook'].pages[0] if contexts['facebook'].pages else contexts['facebook'].new_page()
            pages['facebook'].goto(urls['facebook'], timeout=0, wait_until='domcontentloaded')

            print("=" * 60)
            print("SUCCESS: All browser windows opened successfully!")
            print()
            print("INSTRUCTIONS:")
            print("   1. Log in to WhatsApp Web (scan QR code)")
            print("   2. Log in to Twitter/X")
            print("   3. Log in to Facebook Messenger")
            print()
            print("Please log in to all platforms in the opened browser windows.")
            print("Press ENTER in this terminal when you are completely finished.")
            print("=" * 60)

            # Wait for user confirmation
            input()

            print()
            print("Saving session data...")
            print("   [OK] Sessions are automatically persisted to user_data directories")

            print()
            print("Closing browsers...")

            # Close all contexts
            for context in contexts.values():
                context.close()

            print("=" * 60)
            print("SUCCESS: Setup complete! Your login sessions have been saved.")
            print("   Your watchers can now use these persistent sessions.")
            print("=" * 60)

        except Exception as e:
            print(f"ERROR: {e}")
            # Clean up on error
            for context in contexts.values():
                try:
                    context.close()
                except:
                    pass
            raise

if __name__ == "__main__":
    main()
