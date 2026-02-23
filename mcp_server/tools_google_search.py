"""Google Search MCP tools (Native Python)."""

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

_MCP_DIR = Path(__file__).resolve().parent
from utils import get_project_root, load_env_file

PROJECT_ROOT = get_project_root()

_DISABLED_MSG = "Tool disabled. Enable 'google_search' in CURSOR_TOOLS_ENABLED."

_GOOGLE_ENV_TEMPLATE = """
GOOGLE_API_KEY="your_api_key"  # pragma: allowlist secret
GOOGLE_CX="your_custom_search_engine_id"
"""

# Load mcp_env_config/.google_env into os.environ
load_env_file(".google_env", _MCP_DIR, _GOOGLE_ENV_TEMPLATE)


def register(mcp, enabled_fn):
    """Register Google Search MCP tools."""

    @mcp.tool()
    def google_search(query: str) -> str:
        """Perform a Google search using the Custom Search API.
        Requires GOOGLE_API_KEY and GOOGLE_CX environment variables.
        """
        if not enabled_fn("google_search"):
            return _DISABLED_MSG

        api_key = os.environ.get("GOOGLE_API_KEY")
        cx = os.environ.get("GOOGLE_CX")

        if not api_key or not cx:
            return "Error: GOOGLE_API_KEY or GOOGLE_CX not found in environment. Please add them to your env configuration."

        try:
            safe_query = urllib.parse.quote(query)
            url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cx}&q={safe_query}"

            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())

                if "items" not in data:
                    return "No results found."

                results = []
                for item in data.get("items", [])[:5]:  # Top 5 results
                    results.append(
                        f"### {item.get('title')}\nURL: {item.get('link')}\nSnippet: {item.get('snippet')}\n"
                    )

                return "\n".join(results)
        except Exception as e:
            return f"Error performing Google Search: {str(e)}"
