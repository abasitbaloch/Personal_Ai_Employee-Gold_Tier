#!/usr/bin/env python3
"""
Master Orchestrator Loop - Gold Tier Autonomous Operation
The Ralph Wiggum Hook: "I'm helping! I'm helping!"

This script continuously monitors and processes tasks until all queues are empty.
True autonomous AI employee operation.
"""

import os
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Paths
VAULT_ROOT = Path(__file__).parent
NEEDS_ACTION_DIR = VAULT_ROOT / 'Needs_Action'
SCRIPTS_DIR = VAULT_ROOT / 'Scripts'

# Scripts to execute
CROSS_DOMAIN_INTEGRATOR = SCRIPTS_DIR / 'cross_domain_integrator.py'
SOCIAL_SUMMARY_GENERATOR = SCRIPTS_DIR / 'social_summary_generator.py'


def check_needs_action():
    """
    Check if there are any files in /Needs_Action/ or its subfolders.

    Returns:
        tuple: (has_files, file_count, file_list)
    """
    if not NEEDS_ACTION_DIR.exists():
        return False, 0, []

    # Find all .md files in Needs_Action and subfolders
    md_files = list(NEEDS_ACTION_DIR.rglob('*.md'))

    return len(md_files) > 0, len(md_files), md_files


def run_script(script_path, script_name):
    """
    Execute a Python script using subprocess.

    Args:
        script_path: Path to the script
        script_name: Human-readable name for logging

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"  -> Executing {script_name}...")
        result = subprocess.run(
            ['python', str(script_path)],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print(f"  [SUCCESS] {script_name} completed successfully")
            if result.stdout:
                print(f"    Output: {result.stdout.strip()}")
            return True
        else:
            print(f"  [ERROR] {script_name} failed with exit code {result.returncode}")
            if result.stderr:
                print(f"    Error: {result.stderr.strip()}")
            return False

    except subprocess.TimeoutExpired:
        print(f"  [ERROR] {script_name} timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"  [ERROR] Error running {script_name}: {e}")
        return False


def process_tasks():
    """
    Execute the task processing pipeline.
    """
    print(f"\n{'='*60}")
    print(f"[PROCESSING] Processing tasks...")
    print(f"{'='*60}\n")

    # Step 1: Run Cross-Domain Integrator
    if CROSS_DOMAIN_INTEGRATOR.exists():
        run_script(CROSS_DOMAIN_INTEGRATOR, "Cross-Domain Integrator")
    else:
        print(f"  [WARNING] Cross-Domain Integrator not found at {CROSS_DOMAIN_INTEGRATOR}")

    time.sleep(2)  # Brief pause between scripts

    # Step 2: Run Social Summary Generator
    if SOCIAL_SUMMARY_GENERATOR.exists():
        run_script(SOCIAL_SUMMARY_GENERATOR, "Social Summary Generator")
    else:
        print(f"  [WARNING] Social Summary Generator not found at {SOCIAL_SUMMARY_GENERATOR}")

    print(f"\n{'='*60}")
    print(f"[SUCCESS] Task processing cycle complete")
    print(f"{'='*60}\n")


def run_orchestrator():
    """
    Main orchestrator loop - continuously monitors and processes tasks.
    """
    print("""
================================================================

        MASTER ORCHESTRATOR - GOLD TIER ACTIVATED

              "I'm helping! I'm helping!"
                  - Ralph Wiggum Hook

================================================================
""")

    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Monitoring: {NEEDS_ACTION_DIR}")
    print(f"\nPress Ctrl+C to stop the orchestrator\n")

    cycle_count = 0

    try:
        while True:
            cycle_count += 1
            timestamp = datetime.now().strftime('%H:%M:%S')

            # Check for tasks
            has_files, file_count, file_list = check_needs_action()

            if has_files:
                print(f"[{timestamp}] Cycle #{cycle_count}: Found {file_count} task(s) in queue")

                # Show what files were found
                for file_path in file_list[:5]:  # Show first 5 files
                    relative_path = file_path.relative_to(NEEDS_ACTION_DIR)
                    print(f"  - {relative_path}")
                if file_count > 5:
                    print(f"  ... and {file_count - 5} more")

                # Process the tasks
                process_tasks()

                # Brief pause before checking again
                print(f"[{timestamp}] Checking for more tasks in 5 seconds...\n")
                time.sleep(5)

            else:
                # Queue is empty - Ralph Wiggum mode
                print(f"[{timestamp}] Cycle #{cycle_count}: Queue empty. Ralph Wiggum hook activated. Waiting for new tasks...")
                time.sleep(30)  # Wait 30 seconds before checking again

    except KeyboardInterrupt:
        print(f"\n\n{'='*60}")
        print(f"[STOPPED] Orchestrator stopped by user")
        print(f"{'='*60}")
        print(f"Total cycles completed: {cycle_count}")
        print(f"Stopped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nThank you for using the Master Orchestrator!")


if __name__ == '__main__':
    run_orchestrator()
