"""Filesystem Watcher — Monitors /Inbox and routes new files to /Needs_Action with metadata."""

import time
import shutil
import traceback
from datetime import datetime, timezone
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

VAULT_ROOT = Path(__file__).resolve().parent
INBOX = VAULT_ROOT / "Inbox"
NEEDS_ACTION = VAULT_ROOT / "Needs_Action"
ERROR_LOG = VAULT_ROOT / "Logs" / "watcher_errors.txt"

MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds


def log_error(message: str):
    """Append a timestamped error entry to /Logs/watcher_errors.txt."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    try:
        ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        # Last resort — if we can't even write the log, print to console
        print(f"[FATAL]  Cannot write to error log: {message}")


def move_with_retry(src: Path, dest: Path) -> bool:
    """Attempt shutil.move up to MAX_RETRIES times, waiting RETRY_DELAY between attempts."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            shutil.move(str(src), str(dest))
            return True
        except Exception as e:
            print(f"[RETRY]  Attempt {attempt}/{MAX_RETRIES} failed for {src.name}: {e}")
            log_error(f"Move attempt {attempt}/{MAX_RETRIES} failed for {src.name}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
    return False


class InboxHandler(FileSystemEventHandler):
    """React to new files created in /Inbox."""

    def on_created(self, event):
        if event.is_directory:
            return

        src = Path(event.src_path)

        try:
            self._process_file(src)
        except Exception as e:
            msg = f"Unhandled exception while processing {src.name}:\n{traceback.format_exc()}"
            print(f"[CRASH]  {e}")
            log_error(msg)

    def _process_file(self, src: Path):
        # Wait for the OS to fully release the file handle
        time.sleep(1)

        if not src.exists():
            print(f"[SKIP]   {src.name} — file no longer exists in Inbox")
            return

        # Capture metadata before moving
        try:
            file_size = src.stat().st_size
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        except OSError as e:
            msg = f"Could not read metadata for {src.name}: {e}"
            print(f"[ERROR]  {msg}")
            log_error(msg)
            return

        # Move the file to /Needs_Action with retry logic
        dest = NEEDS_ACTION / src.name
        if not move_with_retry(src, dest):
            msg = f"GAVE UP moving {src.name} after {MAX_RETRIES} attempts"
            print(f"[FAIL]   {msg}")
            log_error(msg)
            return

        # Verify the move actually succeeded
        if not (dest.exists() and not src.exists()):
            msg = (
                f"Move verification failed for {src.name} — "
                f"source exists: {src.exists()}, dest exists: {dest.exists()}"
            )
            print(f"[ERROR]  {msg}")
            log_error(msg)
            return

        print(f"[MOVED]  {src.name} -> /Needs_Action  ({file_size} bytes)")

        # Create ALERT metadata file
        alert_name = f"ALERT_{src.stem}.md"
        alert_path = NEEDS_ACTION / alert_name
        try:
            alert_path.write_text(
                f"# Alert — New File Received\n\n"
                f"file_name: {src.name}\n"
                f"file_size: {file_size} bytes\n"
                f"timestamp: {timestamp}\n"
                f"status: pending\n",
                encoding="utf-8",
            )
            print(f"[ALERT]  {alert_name} created")
        except Exception as e:
            msg = f"Failed to create metadata file {alert_name}: {e}"
            print(f"[ERROR]  {msg}")
            log_error(msg)


def main():
    INBOX.mkdir(parents=True, exist_ok=True)
    NEEDS_ACTION.mkdir(parents=True, exist_ok=True)
    ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)

    handler = InboxHandler()
    observer = Observer()
    observer.schedule(handler, str(INBOX), recursive=False)

    try:
        observer.start()
    except Exception as e:
        msg = f"Failed to start observer: {e}\n{traceback.format_exc()}"
        print(f"[FATAL]  {msg}")
        log_error(msg)
        return

    print(f"Watching: {INBOX}")
    print(f"Error log: {ERROR_LOG}")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    except Exception as e:
        msg = f"Watcher crashed: {e}\n{traceback.format_exc()}"
        print(f"[CRASH]  {msg}")
        log_error(msg)
        observer.stop()

    observer.join()
    print("\nWatcher stopped.")


if __name__ == "__main__":
    main()
