"""Postman official MCP helper tools (config + docs)."""
import json
import os
from pathlib import Path

_MCP_DIR = Path(__file__).resolve().parent
_POSTMAN_ENV = _MCP_DIR / ".postman_env"
_DOCS_URL = "https://learning.postman.com/docs/developer/postman-api/postman-mcp-server/set-up-postman-mcp-server/"
_DISABLED_MSG = "Tool disabled. Enable 'postman_official' in CURSOR_TOOLS_ENABLED."

# Load mcp_server/.postman_env into os.environ
if _POSTMAN_ENV.exists():
    for line in _POSTMAN_ENV.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _remote_url(mode: str, region: str) -> str:
    base = "https://mcp.postman.com" if region.lower() != "eu" else "https://mcp.eu.postman.com"
    if mode == "minimal":
        path = "minimal"
    elif mode == "code":
        path = "code"
    else:
        path = "mcp"
    return f"{base}/{path}"


def register(mcp, enabled_fn):
    """Register Postman official MCP helper tools."""

    @mcp.tool()
    def postman_official_docs() -> str:
        """Get the official Postman MCP setup docs URL."""
        if not enabled_fn("postman_official"):
            return _DISABLED_MSG
        return _DOCS_URL

    @mcp.tool()
    def postman_official_mcp_config(
        mode: str = "full",
        region: str = "us",
        server_name: str = "postman-official",
    ) -> str:
        """Get a Cursor mcp.json snippet for the official Postman MCP server."""
        if not enabled_fn("postman_official"):
            return _DISABLED_MSG
        url = _remote_url(mode.lower(), region.lower())
        config = {
            "mcpServers": {
                server_name: {
                    "type": "http",
                    "url": url,
                    "headers": {"Authorization": "Bearer ${POSTMAN_API_KEY}"},
                }
            }
        }
        return json.dumps(config, indent=2)

    @mcp.tool()
    def postman_official_env_status() -> str:
        """Check whether POSTMAN_API_KEY is available via .postman_env or env vars."""
        if not enabled_fn("postman_official"):
            return _DISABLED_MSG
        key = os.environ.get("POSTMAN_API_KEY")
        if not key:
            return "POSTMAN_API_KEY not found. Add it to mcp_server/.postman_env."
        return "POSTMAN_API_KEY found."
