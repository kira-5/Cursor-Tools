"""Logs category: tail_logs, read_log_file. Default: logs/app.log."""

import os
from pathlib import Path

_MCP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(os.environ.get("CURSOR_PROJECT_ROOT", _MCP_DIR.parent))
DEFAULT_LOG = "logs/app.log"


def register(mcp, enabled_fn):
    """Register logs tools. Disabled when 'logs' category is off."""

    @mcp.tool()
    def tail_logs(n: int = 50, file_path: str | None = None) -> str:
        """Get last n lines from logs/app.log (default). Pass file_path to use a different file."""
        if not enabled_fn("logs"):
            return "Tool disabled. Enable 'logs' in CURSOR_TOOLS_ENABLED."
        path = PROJECT_ROOT / (file_path or DEFAULT_LOG)
        if not path.exists():
            return f"File not found: {path}"
        lines = path.read_text().splitlines()
        tail = lines[-n:] if len(lines) > n else lines
        return "\n".join(tail)

    @mcp.tool()
    def read_log_file(file_path: str | None = None, lines: int | None = None) -> str:
        """Read logs/app.log (default). Pass lines to limit (e.g. first 100). Omit lines for full file."""
        if not enabled_fn("logs"):
            return "Tool disabled. Enable 'logs' in CURSOR_TOOLS_ENABLED."
        path = PROJECT_ROOT / (file_path or DEFAULT_LOG)
        if not path.exists():
            return f"File not found: {path}"
        content = path.read_text()
        if lines is not None:
            content = "\n".join(content.splitlines()[:lines])
        return content
