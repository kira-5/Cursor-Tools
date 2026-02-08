# MCP Setup Summary

## Global Level

**Location:** `~/.cursor/mcp.json`

| Server | Purpose | Config Required |
|--------|---------|-----------------|
| **google-search** | Web search in Cursor | `GOOGLE_API_KEY`, `GOOGLE_CX` |

**Config:**
```json
{
  "mcpServers": {
    "google-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-google-search"],
      "env": {
        "GOOGLE_API_KEY": "YOUR_API_KEY",
        "GOOGLE_CX": "YOUR_ENGINE_ID"
      }
    }
  }
}
```

---

## Project Level

**Location:** `.cursor/mcp.json` (in mtp-base-pricing)

| Server | Purpose |
|--------|---------|
| **mtp-tools** | Docs URLs, tech stack, cursor-docs-index, README |
| **leslies-dev-postgres-db** | PostgreSQL (leslies_dev @ 10.75.0.2:5432) |

**Config:**
```json
{
  "mcpServers": {
    "mtp-tools": {
      "command": "/path/to/mcp_server/.venv/bin/python",
      "args": ["-u", "/path/to/mcp_server/server.py"],
      "env": {
        "PYTHONPATH": "/path/to/mtp-base-pricing",
        "PYTHONUNBUFFERED": "1",
        "CURSOR_TOOLS_ENABLED": "docs,tech_stack,db"
      }
    },
    "leslies-dev-postgres-db": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://user:pass@host:port/dbname"]
    }
  }
}
```

---

## What You Can Do With These Servers

### 1. leslies-dev-postgres-db (1 tool, 18 resources)

**Database-related tasks:**
- Run SQL queries
- Inspect tables and schemas
- Get data from the leslies_dev database
- Explore the base_pricing schema
- Debug data and relationships

**Example prompts:**
- "Query the top 10 rows from base_pricing.bp_actions"
- "List all tables in base_pricing schema"
- "Find records where X"

---

### 2. mtp-tools (3 categories: docs, tech_stack, db)

**Toggle categories:** `CURSOR_TOOLS_ENABLED=docs,tech_stack,db` (omit to disable)
- **docs:** get_docs_urls, cursor-docs-index, readme
- **tech_stack:** get_tech_stack
- **db:** list_databases, run_database_query, run_database_query_from_file

**Project-related tasks:**
- **get_docs_urls** – Get Cursor docs URLs (FastAPI, Pydantic, etc.)
- **get_tech_stack** – Get backend/requirements.txt
- **list_databases** – List available database names from mcp_server/databases.json
- **run_database_query** – Run SQL (sql, database_name?). Default DB from TENANT_NAME_DEPLOYMENT_ENV in .secrets.toml
- **Resources** – Access cursor-docs-index.json and README

**Example prompts:**
- "What docs should I add to Cursor?"
- "Show me our tech stack"
- "List available databases"
- "Run SELECT * FROM base_pricing.bp_actions LIMIT 5" (uses default from .secrets.toml)
- "Run SELECT 1 on leslies_dev" (explicit database)

---

## Multi-Database Setup (mtp-tools)

Configure multiple databases in `mcp_server/databases.json` (see `mcp_server/databases.json.example`):

```json
{
  "databases": {
    "leslies_dev": "postgresql://user:pass@host:port/dbname",
    "another_db": "postgresql://user:pass@host:port/dbname"
  }
}
```

One MCP server, query any DB via `run_database_query(sql, database_name?)`.  
**Default DB:** Derived from `backend/.secrets.toml` as `TENANT_NAME` + `_` + `DEPLOYMENT_ENV` (e.g. `crackerbarrel_prod`, `lesliespool_dev`). Ensure that key exists in `mcp_server/databases.json`.

---

## Quick Reference

| Need | Server / Tool |
|------|---------------|
| Run SQL on any configured DB | mtp-tools → run_database_query |
| List available databases | mtp-tools → list_databases |
| Postgres MCP (table resources) | leslies-dev-postgres-db |
| Docs URLs / tech stack / README | mtp-tools |

---

## Folder Strategy

| Folder | Git Host | MCP Servers |
|--------|----------|-------------|
| `~/Documents/Work/` | Bitbucket | mtp-tools, leslies-dev-postgres-db (project-specific) |
| `~/Documents/Development/` | Personal GitHub | github (with personal token) – add when needed |

---

## Summary

| Level | Servers |
|-------|---------|
| **Global** | 1 (google-search) |
| **mtp-base-pricing (project)** | 2 (mtp-tools, leslies-dev-postgres-db) |
| **mtp-database (project)** | 1 (postgres-db) |


mtp-tools MCP list
Type	Name	Toggle ID	Purpose
Tool	get_docs_urls	get_docs_urls	Cursor docs URLs
Tool	get_tech_stack	get_tech_stack	Read backend/requirements.txt
Tool	list_databases	list_databases	List DB names from databases.json
Tool	run_database_query	run_database_query	Run read-only SQL
Resource	mtp://docs/cursor-index	cursor_docs_index	cursor-docs-index.json
Resource	mtp://project/readme	readme	Project README
