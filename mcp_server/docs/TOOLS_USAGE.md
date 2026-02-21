# mtp-tools MCP Reference

Portable MCP server for MTP projects. Copy `mcp_server/` to another project and toggle by **category**.

---

## 📚 Documentation Library (Master Index)

Click any category below for a detailed guide on available tools, example prompts, and best practices.

| Category | High-Level Features | Detailed Guide |
| :--- | :--- | :--- |
| **docs** | Architectural clarity | [DOCS_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/DOCS_USAGE.md) |
| **db** | Direct DB insight | [DB_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/DB_USAGE.md) |
| **postman** | Local Collection Lifecycle | [POSTMAN_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/POSTMAN_USAGE.md) |
| **bitbucket** | Repository Governance | [BITBUCKET_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/BITBUCKET_USAGE.md) |
| **git** | Local state & history | [GIT_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/GIT_USAGE.md) |
| **search** | Precision code grepping | [SEARCH_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/SEARCH_USAGE.md) |
| **google_search** | Web Research | [GOOGLE_SEARCH_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/GOOGLE_SEARCH_USAGE.md) |
| **fetch** | Web Extraction | [FETCH_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/FETCH_USAGE.md) |
| **memory** | Knowledge Persistence | [MEMORY_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/MEMORY_USAGE.md) |
| **logs** | Live debugging | [LOGS_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/LOGS_USAGE.md) |
| **env** | Secrets & Config | [ENV_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/ENV_USAGE.md) |
| **project_info** | Context injection | [PROJECT_INFO_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/PROJECT_INFO_USAGE.md) |
| **setup** | Configuration Hub | [SETUP_USAGE.md](file:///Users/abhisheksingh/Documents/Development/cursor-tools/mcp_server/docs/SETUP_USAGE.md) |
| **health** | System verification | `mcp_health_check` (See server.py) |

---

**Disable a category = all tools in that category off.** e.g. disable `db` → list_databases, run_database_query, run_database_query_from_file all disabled.

---

## Toggle per Project

In `.cursor/mcp.json`, set `CURSOR_TOOLS_ENABLED` to categories you want (comma-separated):

```json
{
  "mtp-tools": {
    "command": "/path/to/mcp_server/.venv/bin/python",
    "args": ["-u", "/path/to/mcp_server/server.py"],
    "env": {
      "PYTHONPATH": "/path/to/project-root",
      "PYTHONUNBUFFERED": "1",
      "CURSOR_TOOLS_ENABLED": "docs,project_info,db,search,env,git,logs,bitbucket,postman"
    }
  }
}
```

**Examples:**
- `"docs,project_info,db,search,env,git,logs,bitbucket,postman"` — all enabled (default)
- `"docs,project_info"` — no DB tools
- `"db"` — only DB tools
- Omit `CURSOR_TOOLS_ENABLED` — all enabled

---

## Copying to Another Project

1. Copy `mcp_server/` folder to the project root
2. Run `uv sync` or `pip install -r requirements.txt` in `mcp_server/`
3. Add to `.cursor/mcp.json` (see above)
4. Optional: add `mcp_server/databases.json` if using DB tools
5. Optional: add `backend/.secrets.toml` with `TENANT_NAME` + `DEPLOYMENT_ENV` for default DB

---

## Secure config (avoid committing secrets)

Use env var interpolation so the same `mcp.json` works for the team while each person uses their own credentials.

**In `mcp_server/databases.json`** — one env var per DB (scales to n databases):
```json
{
  "databases": {
    "leslies_dev": "${env:MTP_DB_LESLIES_DEV}",
    "leslies_uat": "${env:MTP_DB_LESLIES_UAT}"
  }
}
```

**In `mcp_server/.db_env`** — full connection string per DB (copy from `mcp_server/.db_env.example`):
```
MTP_DB_LESLIES_DEV=postgresql://user:pass@host:port/db_name  # pragma: allowlist secret
MTP_DB_LESLIES_UAT=postgresql://user:pass@host:port/db_name  # pragma: allowlist secret
# Add one line per DB
```

**Option B — `~/.zshrc`**: `export MTP_DB_PASS=your_password`

**In `.cursor/mcp.json`** — pass env vars to mtp-tools:
```json
{
  "mtp-tools": {
    "command": "/path/to/mcp_server/.venv/bin/python",
    "args": ["-u", "/path/to/mcp_server/server.py"],
    "env": {
      "PYTHONPATH": "/path/to/project",
      "CURSOR_TOOLS_ENABLED": "docs,project_info,db,search,env,git,logs,bitbucket",
      "MTP_DB_PASS": "${env:MTP_DB_PASS}"
    }
  }
}
```
Or put creds in `mcp_server/.db_env` — mtp-tools loads it automatically. Copy `mcp_server/.db_env.example` to `mcp_server/.db_env`.

**Postman API key**

Put your key in `mcp_server/.postman_env`:
```
POSTMAN_API_KEY=your_key_here
```

---

---

> [!NOTE]
> All tools are modular. To enable or disable a category, update the `CURSOR_TOOLS_ENABLED` environment variable in your `mcp.json`.
