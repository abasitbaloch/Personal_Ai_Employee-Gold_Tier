#!/usr/bin/env python3
"""
AI Employee Vault - Scheduler (Silver Tier)
Automatically creates trigger files for scheduled tasks
"""

import schedule
import time
from datetime import datetime
import os

# Get the vault root directory
VAULT_ROOT = os.path.dirname(os.path.abspath(__file__))
NEEDS_ACTION_FOLDER = os.path.join(VAULT_ROOT, "Needs_Action")

def create_morning_briefing():
    """Create morning briefing trigger file at 08:00 AM daily"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_path = os.path.join(NEEDS_ACTION_FOLDER, "FILE_morning_briefing.md")

    content = f"""# Morning Briefing Trigger

**Created:** {timestamp}
**Type:** Scheduled Task
**Action:** Generate morning status summary

This is an automated trigger file created by the scheduler.
The AI Employee will process this and generate a morning briefing.
"""

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[{timestamp}] ✓ Morning briefing trigger created")
    except Exception as e:
        print(f"[{timestamp}] ✗ Error creating morning briefing: {e}")

def create_test_schedule():
    """Create test schedule trigger file every 1 minute (for testing)"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_path = os.path.join(NEEDS_ACTION_FOLDER, "FILE_test_schedule.md")

    content = f"""# Test Schedule Trigger

**Created:** {timestamp}
**Type:** Test Scheduled Task
**Action:** Verify scheduler is working

This is a test trigger file created every minute to verify the scheduler is functioning correctly.
"""

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[{timestamp}] ✓ Test schedule trigger created")
    except Exception as e:
        print(f"[{timestamp}] ✗ Error creating test schedule: {e}")

def main():
    """Main scheduler loop"""
    print("="*60)
    print("AI Employee Vault - Scheduler Started")
    print("="*60)
    print(f"Vault Root: {VAULT_ROOT}")
    print(f"Needs Action Folder: {NEEDS_ACTION_FOLDER}")
    print()
    print("Scheduled Tasks:")
    print("  - Morning Briefing: Daily at 08:00 AM")
    print("  - Test Schedule: Every 1 minute (for testing)")
    print()
    print("Press Ctrl+C to stop the scheduler")
    print("="*60)
    print()

    # Schedule the jobs
    schedule.every().day.at("08:00").do(create_morning_briefing)
    schedule.every(1).minutes.do(create_test_schedule)

    # Run the scheduler loop
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user")
        print("="*60)

if __name__ == "__main__":
    main()
