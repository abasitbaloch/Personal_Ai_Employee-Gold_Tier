"""Task Analyzer — Parse ALERT metadata files and extract file name + status."""

import re
from pathlib import Path


def parse_metadata(metadata_path: str) -> dict:
    """Read an ALERT_*.md metadata file and extract key fields.

    Expected metadata format (YAML-like front matter):
        file_name: some_document.md
        status: pending

    Returns:
        Dict with 'file_name' and 'status' keys.
    """
    path = Path(metadata_path)
    if not path.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    content = path.read_text(encoding="utf-8")

    file_name = _extract_field(content, "file_name")
    status = _extract_field(content, "status")

    return {
        "file_name": file_name,
        "status": status,
    }


def _extract_field(content: str, field: str) -> str | None:
    """Extract a 'key: value' field from metadata content."""
    match = re.search(rf"^{field}:\s*(.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else None


if __name__ == "__main__":
    # Quick smoke test
    print("task_analyzer ready.")
