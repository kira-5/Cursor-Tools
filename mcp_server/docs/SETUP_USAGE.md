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

## Quick Reference

| Need | Guide |
|------|-------|
| **Initial Setup** | [TEAM_SETUP_GUIDE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/TEAM_SETUP_GUIDE.md) |
| **All Tools Master List** | [TOOLS_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/TOOLS_USAGE.md) |
| **Database Queries** | [DB_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/DB_USAGE.md) |
| **Jira / Confluence** | [JIRA_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/JIRA_USAGE.md) |
| **Bitbucket / Git** | [BITBUCKET_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/BITBUCKET_USAGE.md) |
| **Postman** | [POSTMAN_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/POSTMAN_USAGE.md) |
