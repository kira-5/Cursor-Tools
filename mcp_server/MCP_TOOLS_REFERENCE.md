# mtp-tools MCP Reference

Portable MCP server for MTP projects. Copy `mcp_server/` to another project and toggle by **category**.

---

## Categories (one file each)

| Category | File | Tools / Resources |
|----------|------|-------------------|
| **docs** | `tools_docs.py` | get_docs_urls, get_doc, cursor-index, readme, mcp-readme, mcp-setup, mcp-tools-reference, email-template |
| **project_info** | `tools_project_info.py` | get_project_info |
| **db** | `tools_db.py` | list_databases, run_database_query, run_database_query_from_file, list_tables, describe_table |
| **search** | `tools_search.py` | grep_code, search_docs |
| **env** | `tools_env.py` | get_config |
| **git** | `tools_git.py` | git_status, git_branches, recent_commits |
| **logs** | `tools_logs.py` | tail_logs, read_log_file |

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
      "CURSOR_TOOLS_ENABLED": "docs,project_info,db,search,env,git,logs"
    }
  }
}
```

**Examples:**
- `"docs,project_info,db,search,env,git,logs"` — all enabled (default)
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
MTP_DB_LESLIES_DEV=postgresql://user:pass@host:5432/leslies_dev
MTP_DB_LESLIES_UAT=postgresql://user:pass@host:5432/leslies_uat
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
      "CURSOR_TOOLS_ENABLED": "docs,project_info,db,search,env,git,logs",
      "MTP_DB_PASS": "${env:MTP_DB_PASS}"
    }
  }
}
```
Or put creds in `mcp_server/.db_env` — mtp-tools loads it automatically. Copy `mcp_server/.db_env.example` to `mcp_server/.db_env`.

---

## Docs

- **get_docs_urls** — Get Cursor docs URLs (FastAPI, Pydantic, etc.) by priority.
- **get_doc** — Read a project doc. `get_doc("cursor-index")` | `get_doc("readme")` | `get_doc("mcp-readme")` | `get_doc("mcp-setup")` | `get_doc("mcp-tools-reference")` | `get_doc("email-template")`

**Resources:** mtp://docs/cursor-index, mtp://project/readme, mtp://mcp/readme, mtp://project/mcp-setup, mtp://mcp/tools-reference, mtp://docs/email-template

---

## Project Info

- **get_project_info** — Get project name, version, Python version, and tech stack (requirements) in one call.

---

## Search Tools

- **grep_code** — Search regex in code. `grep_code("run_database_query", "*.py")` or `grep_code("TENANT_NAME", "*.toml")`
- **search_docs** — Search in `backend/app/assets/docs/`. `search_docs("filter")` or `search_docs("API", docs_path="backend/app/assets/docs")`

---

## Env / Config

- **get_config** — Read `backend/.secrets.toml` or `.env`. Sensitive values (password, secret, key, token) are masked. `get_config()` or `get_config(section="base-pricing-local")` or `get_config(config_path=".env")`

---

## Git

- **git_status** — Show modified, staged, untracked files
- **git_branches** — List branches (current marked with *)
- **recent_commits** — Show last n commits. `recent_commits(5)` or `recent_commits()` (default 10)

---

## Logs

- **tail_logs** — Last n lines from logs/app.log. `tail_logs(50)` or `tail_logs(100, file_path="backend/logs/app.log")`
- **read_log_file** — Read full or first N lines. `read_log_file()` or `read_log_file(lines=100)`

---

## Schema (DB introspection)

- **list_tables** — List tables in a schema. `list_tables("base_pricing")` or `list_tables("base_pricing", database_name="leslies_uat")`
- **describe_table** — Column name, type, nullable. `describe_table("base_pricing", "bp_actions")` — No hardcoding; uses PostgreSQL information_schema.

---

## Large SQL Queries

1. Put SQL in `mcp_server/queries/query.sql` (default)
2. Call: `run_database_query_from_file(database_name="leslies_dev")`

For a different file: `run_database_query_from_file(database_name="leslies_dev", file_path="mcp_server/queries/orders.sql")`
