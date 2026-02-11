"""
MCP Server for mtp-base-pricing backend.
Exposes tools and resources for Cursor to use.
Copy to other projects; toggle by category via CURSOR_TOOLS_ENABLED env var.

Categories: docs, project_info, db, search, env, git, logs, bitbucket
- docs: get_docs_urls, get_doc, cursor-index, readme, mcp-readme, mcp-setup, mcp-tools-reference, email-template
- project_info: get_project_info (name, version, Python, tech stack)
- db: list_databases, run_database_query, run_database_query_from_file, list_tables, describe_table (disable db = all db tools off)
- search: grep_code, search_docs
- env: get_config (read .secrets.toml, .env with sensitive values masked)
- git: git_status, git_branches, recent_commits
- logs: tail_logs, read_log_file (default: logs/app.log)
"""
import os
from pathlib import Path

# Ensure mcp_server is on path for tools_* imports (works when run as script or module)
_path = Path(__file__).resolve().parent
if str(_path) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(_path))

from mcp.server.fastmcp import FastMCP

# Category-based toggles. Default: all. Omit a category to disable it.
# docs, project_info, db, search, env, git, logs
_ENABLED = os.getenv("CURSOR_TOOLS_ENABLED", "docs,project_info,db,search,env,git,logs,bitbucket").split(",")
_ENABLED = {t.strip() for t in _ENABLED if t.strip()}


def _enabled(category: str) -> bool:
    """If CURSOR_TOOLS_ENABLED is set, only listed categories are enabled. If empty/unset, all enabled."""
    return not _ENABLED or category in _ENABLED


mcp = FastMCP(
    "mtp-tools",
    instructions="MCP server for the mtp-base-pricing backend project. Use tools to get docs, tech stack, run database queries, and project info.",
)

# Register tools by category (one file per category)
from tools_docs import register as register_docs
from tools_project_info import register as register_project_info
from tools_db import register as register_db
from tools_search import register as register_search
from tools_env import register as register_env
from tools_git import register as register_git
from tools_logs import register as register_logs
from tools_bitbucket import register as register_bitbucket

register_docs(mcp, _enabled)
register_project_info(mcp, _enabled)
register_db(mcp, _enabled)
register_search(mcp, _enabled)
register_env(mcp, _enabled)
register_git(mcp, _enabled)
register_logs(mcp, _enabled)
register_bitbucket(mcp, _enabled)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
