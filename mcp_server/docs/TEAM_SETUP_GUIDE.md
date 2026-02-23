# 🚀 Teammate Setup Guide: Cursor-Tools MCP

This guide explains how to get the **Cursor-Tools MCP Server** running in less than 2 minutes.

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

### Option A: Standard (Portable via `uvx`) — RECOMMENDED

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

### Option B: Local Expert (Direct Path)
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

## ⚡️ Step 2: The "Magic" Setup

Once the server is added, simply ask your agent a question that requires a tool, for example:
> "Search Jira for ticket MTP-123"

### What will happen:
1. The server will start for the first time.
2. It will detect you have no configuration and **automatically create** a folder called `mcp_env_config/` in your current project root.
3. It will generate boilerplate `.env` files inside that folder.

---

## 🔑 Step 3: Add Your Secrets

Open the new `mcp_env_config/` folder in your project and fill in your details:

*   **`.jira_env`**: Add your email and Atlassian API token.
*   **`.bitbucket_env`**: Add your Bitbucket username and App Password.
*   **`.postman_env`**: Add your Postman API key.

> [!NOTE]
> This folder is automatically added to `.gitignore`, so your personal secrets will never be committed to the repo.

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
