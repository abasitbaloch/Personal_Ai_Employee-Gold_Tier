#!/usr/bin/env python3
"""
Watchdog Process Manager - Gold Tier 24/7 Operation
Keeps the AI Employee alive by monitoring and auto-restarting crashed processes.
"""

import os
import sys
import time
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Paths
VAULT_ROOT = Path(__file__).parent

# Process definitions: {name: script_path}
PROCESSES = {
    'orchestrator_loop': VAULT_ROOT / 'orchestrator_loop.py',
    'social_media_watcher': VAULT_ROOT / 'social_media_watcher.py',
    'twitter_watcher': VAULT_ROOT / 'twitter_watcher.py',
    'whatsapp_watcher': VAULT_ROOT / 'whatsapp_watcher.py'
}

# Process tracking: {name: {'process': Popen_object, 'restarts': count}}
process_registry = {}


def start_process(name, script_path):
    """
    Start a process using subprocess.Popen.

    Args:
        name (str): Process name for logging
        script_path (Path): Path to the Python script

    Returns:
        subprocess.Popen: The started process object, or None if failed
    """
    try:
        logger.info(f"[START] Starting {name}...")

        # Start the process
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        logger.info(f"[SUCCESS] {name} started with PID {process.pid}")
        return process

    except Exception as e:
        logger.error(f"[ERROR] Failed to start {name}: {e}")
        return None


def is_process_running(process):
    """
    Check if a process is still running.

    Args:
        process (subprocess.Popen): Process object to check

    Returns:
        bool: True if running, False if crashed/stopped
    """
    if process is None:
        return False

    # poll() returns None if process is still running
    return process.poll() is None


def restart_process(name, script_path):
    """
    Restart a crashed process.

    Args:
        name (str): Process name
        script_path (Path): Path to the script

    Returns:
        subprocess.Popen: New process object
    """
    logger.warning(f"[RESTART] {name} has crashed. Restarting...")

    # Increment restart counter
    if name in process_registry:
        process_registry[name]['restarts'] += 1
        restart_count = process_registry[name]['restarts']
        logger.info(f"[INFO] {name} restart count: {restart_count}")

    # Start the process again
    new_process = start_process(name, script_path)

    return new_process


def initialize_processes():
    """
    Initialize all processes defined in PROCESSES dictionary.
    """
    logger.info("="*60)
    logger.info("WATCHDOG PROCESS MANAGER - INITIALIZING")
    logger.info("="*60)

    for name, script_path in PROCESSES.items():
        if not script_path.exists():
            logger.warning(f"[SKIP] {name} script not found at {script_path}")
            continue

        process = start_process(name, script_path)

        if process:
            process_registry[name] = {
                'process': process,
                'script_path': script_path,
                'restarts': 0
            }

    logger.info(f"[INFO] Initialized {len(process_registry)} process(es)")
    logger.info("="*60 + "\n")


def monitor_processes():
    """
    Main monitoring loop - checks process health and restarts if needed.
    """
    check_interval = 10  # Check every 10 seconds
    check_count = 0

    logger.info("Starting process monitoring...")
    logger.info(f"Check interval: {check_interval} seconds")
    logger.info("Press Ctrl+C to stop the watchdog\n")

    try:
        while True:
            check_count += 1
            timestamp = datetime.now().strftime('%H:%M:%S')

            # Check each registered process
            for name, data in list(process_registry.items()):
                process = data['process']
                script_path = data['script_path']

                if not is_process_running(process):
                    logger.warning(
                        f"[{timestamp}] ALERT: {name} (PID {process.pid if process else 'N/A'}) is not running!"
                    )

                    # Restart the process
                    new_process = restart_process(name, script_path)

                    if new_process:
                        # Update registry with new process
                        process_registry[name]['process'] = new_process
                    else:
                        logger.error(f"[ERROR] Failed to restart {name}")

            # Periodic status report every 60 checks (10 minutes)
            if check_count % 60 == 0:
                logger.info(f"[{timestamp}] Status Report - All {len(process_registry)} process(es) monitored")
                for name, data in process_registry.items():
                    pid = data['process'].pid if data['process'] else 'N/A'
                    restarts = data['restarts']
                    status = "RUNNING" if is_process_running(data['process']) else "STOPPED"
                    logger.info(f"  - {name}: {status} (PID: {pid}, Restarts: {restarts})")

            # Wait before next check
            time.sleep(check_interval)

    except KeyboardInterrupt:
        logger.info("\n" + "="*60)
        logger.info("WATCHDOG STOPPED BY USER")
        logger.info("="*60)

        # Terminate all managed processes
        logger.info("Terminating managed processes...")
        for name, data in process_registry.items():
            process = data['process']
            if is_process_running(process):
                logger.info(f"  - Stopping {name} (PID {process.pid})...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                    logger.info(f"    {name} stopped gracefully")
                except subprocess.TimeoutExpired:
                    logger.warning(f"    {name} did not stop gracefully, killing...")
                    process.kill()

        logger.info("\nWatchdog shutdown complete.")


def run_watchdog():
    """
    Main entry point for the watchdog manager.
    """
    print("""
================================================================

           WATCHDOG PROCESS MANAGER - GOLD TIER
                   24/7 AI Employee Guardian

================================================================
""")

    # Initialize all processes
    initialize_processes()

    if not process_registry:
        logger.error("No processes to monitor. Exiting.")
        return

    # Start monitoring
    monitor_processes()


if __name__ == '__main__':
    run_watchdog()
