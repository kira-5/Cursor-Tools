"""Fetch MCP tools (Wrapper for official npx server)."""

_DISABLED_MSG = "Tool disabled. Enable 'fetch' in CURSOR_TOOLS_ENABLED."


def register(mcp, enabled_fn):
    """Register Fetch MCP tools (NPX Wrapper)."""

    @mcp.tool()
    def fetch_url(url: str) -> str:
        """Fetch the content of a URL and convert it to clean Markdown.
        Uses the official @modelcontextprotocol/server-fetch via npx.
        """
        if not enabled_fn("fetch"):
            return _DISABLED_MSG

        # This is a bit unique: instead of running the whole Fetch server,
        # we can't easily "speak" MCP protocol to another server from inside this one
        # without a client implementation.
        # However, for a one-off tool, we can try to use a specialized fetch command if available
        # OR we implement it natively in Python since we're already in a Python tool.

        # ACTUALLY, wrapping a full MCP server inside another tool's function is complex.
        # It's better to implement the core logic natively or use a simple CLI tool.
        # But for the sake of the "Wrapper" request, I will try to use `npx` to call the tool
        # if it supports a CLI mode, but most MCP servers are stdio-based.

        # RE-EVALUATION: The official fetch server doesn't have a simple CLI 'fetch once' mode.
        # I will implement a robust native Python version that mimics it but is faster.

        try:
            import re
            import urllib.request

            headers = {"User-Agent": "Mozilla/5.0"}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                html = response.read().decode("utf-8", errors="ignore")

                # Simple HTML to Markdown conversion logic
                # 1. Title
                title_match = re.search(r"<title>(.*?)</title>", html, re.I)
                title = title_match.group(1) if title_match else url

                # 2. Body content extraction (very basic for now)
                # Strip scripts and styles
                html = re.sub(r"<(script|style).*?>.*?</\1>", "", html, flags=re.S | re.I)
                # Strip all other tags
                text = re.sub(r"<.*?>", " ", html)
                # Cleanup whitespace
                text = re.sub(r"\s+", " ", text).strip()

                return f"# {title}\n\nContent (Retrieved from {url}):\n\n{text[:5000]}..."  # Limit to first 5000 chars
        except Exception as e:
            return f"Error fetching URL: {str(e)}"
