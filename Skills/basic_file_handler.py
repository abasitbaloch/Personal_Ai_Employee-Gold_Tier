"""Basic File Handler — Read markdown files and move them between vault directories."""

import shutil
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent


def read_markdown(file_path: str) -> str:
    """Read and return the contents of a markdown file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix.lower() != ".md":
        raise ValueError(f"Expected a markdown file, got: {path.suffix}")
    return path.read_text(encoding="utf-8")


def move_file(file_path: str, destination_dir: str) -> Path:
    """Move a file from its current location to a destination vault directory.

    Args:
        file_path: Path to the source file.
        destination_dir: Name of the target folder (e.g. 'Needs_Action', 'Done').

    Returns:
        The new path of the moved file.
    """
    src = Path(file_path)
    dest_dir = VAULT_ROOT / destination_dir

    if not src.exists():
        raise FileNotFoundError(f"Source file not found: {file_path}")
    if not dest_dir.exists():
        raise FileNotFoundError(f"Destination directory not found: {dest_dir}")

    dest = dest_dir / src.name
    shutil.move(str(src), str(dest))
    return dest


if __name__ == "__main__":
    # Quick smoke test
    print(f"Vault root: {VAULT_ROOT}")
    print("basic_file_handler ready.")
