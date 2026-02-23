# MCP Setup Summary

> [!IMPORTANT]
> For the most up-to-date teammate setup instructions, please refer to the **[TEAM_SETUP_GUIDE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/TEAM_SETUP_GUIDE.md)**.

## Overview

This MCP server (`mtp-tools`) provides a centralized hub for project documentation, database introspection, and integration with external services (Jira, Confluence, Bitbucket, Postman, etc.).

### 1. Unified Configuration
The server now uses a standardized configuration flow:
1. **Priority 1**: `[Project Root]/mcp_env_config/` (Local overrides, git-ignored)
2. **Priority 2**: `[MCP Package]/env_config/` (Package defaults)

To configure your credentials, simply duplicate the templates created in `mcp_env_config/` at the root of your project after the first run.

### 2. Available Categories
Toggle features via the `CURSOR_TOOLS_ENABLED` environment variable in your `mcp.json`.

| Category | Description |
|----------|-------------|
| `docs` | Architectural docs and READMEs |
| `project_info` | Tech stack and requirements |
| `db` | SQL queries and table introspection |
| `search` | Precision code grepping |
| `bitbucket` | PRs and repo management |
| `jira` | Issue tracking |
| `confluence` | Page search and content |
| `postman` | API management |
| `google_search` | Native web research |
| `fetch` | URL to Markdown conversion |
| `memory` | Cross-chat project persistence |

---

## 📋 Prerequisites

1. **Install uv**: This project uses `uv` for lightning-fast Python management.
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Sync Dependencies**: Navigate to the server directory and lock the environment.
   ```bash
   cd mcp_server && uv sync
   ```

---

## 🛠 Step 1: Add to Your IDE

Choose the configuration block for your IDE below.

### Option 1: Standard (via `uvx`) — RECOMMENDED

#### 1. For Cursor (Add to `.cursor/mcp.json`)
```json
{
  "mcpServers": {
    "mtp-tools": {
      "command": "uvx",
      "args": [
        "--from",
        "/Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server",
        "mcp-server"
      ],
      "env": {
        "CURSOR_TOOLS_ENABLED": "bitbucket,confluence,db,docs,env,fetch,git,google_search,jira,logs,memory,postman,project_info,search"
      },
      "disabled": false
    }
  }
}
```

#### 2. For Antigravity (Update `~/.gemini/antigravity/mcp_config.json`)
```json
{
  "mcpServers": {
    "mtp-tools": {
      "command": "uvx",
      "args": [
        "--from",
        "/Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server",
        "mcp-server"
      ],
      "env": {
        "CURSOR_TOOLS_ENABLED": "bitbucket,confluence,db,docs,env,fetch,git,google_search,jira,logs,memory,postman,project_info,search"
      },
      "disabled": false
    }
  }
}
```

---

### Option 2: Local Expert (Direct Path)
Use this if you are developing the MCP server code and want to bypass `uvx` caching.

```json
{
  "mcpServers": {
    "cursor-tools-local": {
      "command": "/Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/.venv-mcp_server/bin/python",
      "args": [
        "-u",
        "/Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/server.py"
      ],
      "env": {
        "PYTHONPATH": "/Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server",
        "PYTHONUNBUFFERED": "1",
        "CURSOR_TOOLS_ENABLED": "bitbucket,confluence,db,docs,env,fetch,git,google_search,jira,logs,memory,postman,project_info,search"
      },
      "disabled": false
    }
  }
}
```

---

## ⚡️ Step 2: Secret Management

Once the server is added, it will automatically create a folder called `mcp_env_config/` in your project root upon first use. Open that folder and fill in your details:

*   **`.jira_env`**: Add your email and Atlassian API token.
*   **`.bitbucket_env`**: Add your Bitbucket username and App Password.
*   **`.postman_env`**: Add your Postman API key.

---

## 🔄 Step 4: Refresh

After you've filled in your secrets, go back to your IDE's MCP settings and click **"Refresh"** (the circular arrow icon) next to the `mtp-tools` server.

---

## 💡 Useful Toggle: "disabled"

You can temporarily deactivate the MCP server without deleting its configuration by adding the `"disabled"` key to your JSON block:

```json
{
  "mcpServers": {
    "mtp-tools": {
      "command": "uvx",
      "args": [...],
      "disabled": true
    }
  }
}
```

*   `"disabled": true`: Server is inactive and tools are hidden.
*   `"disabled": false`: Server is active (default).

This works identically in both **Cursor** and **Antigravity**.

**You are now ready to go!** 🚀
