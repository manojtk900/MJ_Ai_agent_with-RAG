"""
MCP Filesystem Server — File system operations as MCP tools.
"""
from pathlib import Path
from typing import Any


async def read_file(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return p.read_text(encoding="utf-8")


async def write_file(path: str, content: str) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Written {len(content)} bytes to {path}"


async def list_directory(path: str = ".") -> str:
    p = Path(path)
    if not p.is_dir():
        raise NotADirectoryError(f"Not a directory: {path}")
    items = sorted(str(item) for item in p.iterdir())
    return "\n".join(items)


async def delete_file(path: str) -> str:
    """Requires approval — do not call directly without permission check."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    p.unlink()
    return f"Deleted: {path}"
