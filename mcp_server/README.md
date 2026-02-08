# mtp-base-pricing MCP Server

Model Context Protocol server for the mtp-base-pricing backend. Exposes tools and resources for Cursor.

## Tools

| Tool | Description |
|------|-------------|
| `get_docs_urls` | Get Cursor docs URLs (filter by priority: core, recommended, optional) |
| `get_project_info` | Get project name, version, Python, tech stack |
| `get_cursor_docs_index` | Get cursor-docs-index.json (resource) |
| `get_readme` | Get project README (resource) |

## Setup

```bash
cd mcp_server
uv sync
# or: pip install mcp
```

## Add to Cursor

The server is already added to `~/.cursor/mcp.json` if you're on this machine.

To add manually: **Cursor Settings** → **Tools & MCP** → **Edit Config** → add to `mcpServers`:

```json
"mtp-base-pricing": {
  "command": "/path/to/mtp-base-pricing/mcp_server/.venv/bin/python",
  "args": ["/path/to/mtp-base-pricing/mcp_server/server.py"]
}
```

Use the venv's Python so it doesn't conflict with your backend dependencies. Restart Cursor after adding.

## Test

```bash
uv run server.py
# Or use MCP Inspector: npx -y @modelcontextprotocol/inspector
```
