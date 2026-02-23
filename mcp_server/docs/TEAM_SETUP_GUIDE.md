# 🚀 Teammate Setup Guide: Cursor-Tools MCP

This guide explains how to get the **Cursor-Tools MCP Server** running in your local Cursor IDE in less than 2 minutes.

## 📋 Prerequisites

1. **Install uv**: This project uses `uv` for lightning-fast Python management.
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

---

## 🛠 Step 1: Add to Your IDE

Depending on which tool you are using, the configuration filename and path will differ:

| IDE Mode | Config Filename | Standard Path |
| :--- | :--- | :--- |
| **Cursor** | `mcp.json` | `.cursor/mcp.json` |
| **Antigravity** | `mcp_config.json` | `~/.gemini/antigravity/mcp_config.json` |

### Configuration Details

Add a new server with these details:

### Option A: Standard (via uvx)
Use this if you just want the tools to work. It installs the server globally via `uvx`.

*   **Name**: `cursor-tools`
*   **Type**: `command`
*   **Command**: `uvx --from git+https://github.com/kira-5/Cursor-Tools.git mcp-server`
*   **Env**: `CURSOR_TOOLS_ENABLED=bitbucket,confluence,db,docs,env,fetch,git,google_search,jira,logs,memory,postman,project_info,search`

```json
{
  "mcpServers": {
    "cursor-tools": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/kira-5/Cursor-Tools.git",
        "mcp-server"
      ],
      "env": {
        "CURSOR_TOOLS_ENABLED": "bitbucket,confluence,db,docs,env,fetch,git,google_search,jira,logs,memory,postman,project_info,search"
      }
    }
  }
}
```

### Option B: Local Development (Inside cursor-tools Repo)
Use this if you have the repository cloned and want to test code changes.

*   **Name**: `cursor-tools`
*   **Type**: `command`
*   **Command**: `/PATH/TO/YOUR/REPO/mcp_server/.venv-mcp_server/bin/python`
*   **Args**: `-u`, `/PATH/TO/YOUR/REPO/mcp_server/server.py`
*   **Env**: `PYTHONPATH=/PATH/TO/YOUR/REPO/mcp_server`

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
      }
    }
  }
}
```
---

## ⚡️ Step 2: The "Magic" Setup

Once the server is added, simply ask Cursor a question that requires a tool, for example:
> "Search Jira for ticket MTP-123"

### What will happen:
1. The server will start for the first time.
2. It will detect you have no configuration and **automatically create** a folder called `mcp_env_config/` in your current project root.
3. It will generate boilerplate `.env` files inside that folder.

---

## 🔑 Step 3: Add Your Secrets

Look at your project sidebar. Open the new `mcp_env_config/` folder and fill in your details:

*   **`.jira_env`**: Add your email and Atlassian API token.
*   **`.bitbucket_env`**: Add your Bitbucket username and App Password.
*   **`.postman_env`**: Add your Postman API key.
*   **`.google_env`**: Add your Google Search API key (optional).

> [!NOTE]
> This folder is automatically added to `.gitignore`, so your personal secrets will never be committed to the repo.

---

## 🔄 Step 4: Refresh

After you've filled in your secrets, go back to Cursor Settings and click **"Refresh"** (the circular arrow icon) next to the `cursor-tools` server.

**You are now ready to go!** 🚀
