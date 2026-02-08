# cursor-tools

Shared MCP server and scripts for Cursor. Use from any project without copying.

## Structure

```
cursor-tools/
├── mcp_server/     # MCP server (tools, config)
└── scripts/        # Utilities (affected_apis, etc.)
```

## Per-project setup

### 1. mcp.json (`.cursor/mcp.json`)

```json
{
  "cursor-tools": {
    "command": "/path/to/cursor-tools/mcp_server/.venv/bin/python",
    "args": ["-u", "/path/to/cursor-tools/mcp_server/server.py"],
    "env": {
      "PYTHONPATH": "/path/to/your-project",
      "CURSOR_PROJECT_ROOT": "/path/to/your-project",
      "CURSOR_TOOLS_ENABLED": "docs,project_info,db,search,env,git,logs"
    }
  }
}
```

**Important:** Set `CURSOR_PROJECT_ROOT` to the project root so the MCP server reads that project's code.

### 2. .affected_apis.json (in each project root)

Each project keeps its own config. See `scripts/.affected_apis.json.example`.

### 3. Cursor commands (`.cursor/commands/`)

Point to the shared script path in affected-apis.md.

## First-time setup

```bash
cd cursor-tools/mcp_server
uv sync   # or: pip install -r requirements.txt
```

Copy `mcp_server/databases.json.example` to `mcp_server/databases.json` and `mcp_server/.db_env.example` to `mcp_server/.db_env` if using DB tools.
