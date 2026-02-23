# mtp-tools MCP Reference

Portable MCP server for MTP projects. Copy `mcp_server/` to another project and toggle by **category**.

---

## 📚 Documentation Library (Master Index)

Click any category below for a detailed guide on available tools, example prompts, and best practices.

| Category | High-Level Features | Detailed Guide |
| :--- | :--- | :--- |
| **docs** | Architectural clarity | [DOCS_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/DOCS_USAGE.md) |
| **project_info** | Tech stack & context | [PROJECT_INFO_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/PROJECT_INFO_USAGE.md) |
| **db** | Direct DB insight | [DB_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/DB_USAGE.md) |
| **jira** | Issue Tracking | [JIRA_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/JIRA_USAGE.md) |
| **confluence** | Knowledge Base | [CONFLUENCE_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/CONFLUENCE_USAGE.md) |
| **bitbucket** | Repository Governance | [BITBUCKET_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/BITBUCKET_USAGE.md) |
| **git** | Local history | [GIT_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/GIT_USAGE.md) |
| **postman** | API Lifecycle | [POSTMAN_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/POSTMAN_USAGE.md) |
| **google_search** | Web Research | [GOOGLE_SEARCH_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/GOOGLE_SEARCH_USAGE.md) |
| **fetch** | Web Extraction | [FETCH_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/FETCH_USAGE.md) |
| **memory** | Knowledge Persistence | [MEMORY_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/MEMORY_USAGE.md) |
| **logs** | Live debugging | [LOGS_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/LOGS_USAGE.md) |
| **env** | Secrets & Config | [ENV_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/ENV_USAGE.md) |
| **setup** | Configuration Hub | [SETUP_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/SETUP_USAGE.md) |
| **quickstart** | Teammate Setup | [TEAM_SETUP_GUIDE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/TEAM_SETUP_GUIDE.md) |
| **health** | System verification | `mcp_health_check` (See server.py) |

---

## ⚙️ Unified Configuration (`mcp_env_config/`)

This server uses a standardized configuration flow for all teammates:
1. **Priority 1**: `[Project Root]/mcp_env_config/` (Local overrides, git-ignored)
2. **Priority 2**: `[MCP Package]/env_config/` (Package defaults)

On first run, missing `.env` files and `databases.json` are automatically created in `mcp_env_config/` at your project root. Simply fill in your credentials there.

---

## 🔌 Toggle Categories

In your `.cursor/mcp.json`, use `CURSOR_TOOLS_ENABLED` to select required tools:

```json
{
  "mcpServers": {
    "mtp-tools": {
      "command": "uvx",
      "args": ["mcp-server"],
      "env": {
        "CURSOR_TOOLS_ENABLED": "docs,db,jira,confluence,bitbucket"
      }
    }
  }
}
```

---

> [!NOTE]
> All tools are modular. To enable/disable a category, update the `CURSOR_TOOLS_ENABLED` environment variable.
