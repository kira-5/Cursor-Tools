# cursor-tools: The Antigravity-Native Global Agentic Hub 🚀

A centralized Model Context Protocol (MCP) hub and script library designed to be shared across all your development projects.

## 🏛️ Architecture

`cursor-tools` acts as a **Single Source of Truth** for your AI tools. Instead of duplicating logic, you point your project-specific `.cursor/mcp.json` back to this directory.

```
cursor-tools/
├── mcp_server/     # The "Brain" (FastMCP Hub)
│   └── docs/       # 13 Detailed Tool Category Guides
└── scripts/        # Multi-project automation utilities
```

## 🛠️ Global Setup

Initialize the hub once on your system:

```bash
cd mcp_server
uv sync   # Recommended
# or: pip install -r requirements.txt
```

## 🔗 Connecting Your Projects

To enable this hub in any project, add this block to its `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "cursor-tools": {
      "command": "/absolute/path/to/cursor-tools/mcp_server/.venv/bin/python",
      "args": ["-u", "/absolute/path/to/cursor-tools/mcp_server/server.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/cursor-tools/mcp_server",
        "CURSOR_PROJECT_ROOT": "/absolute/path/to/YOUR_CURRENT_PROJECT",
        "CURSOR_TOOLS_ENABLED": "docs,project_info,db,search,env,git,logs,bitbucket,postman,google_search,fetch,memory"
      }
    }
  }
}
```

> [!IMPORTANT]
> Always set `CURSOR_PROJECT_ROOT` to the absolute path of the project you are currently working in.

## 📚 Documentation

For a full list of tools and how to prompt for them, see the [Master Index](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/TOOLS_USAGE.md).
