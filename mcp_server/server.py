"""
MCP Server for cursor-tools backend.
Exposes tools and resources for Cursor to use.
Copy to other projects; toggle by category via CURSOR_TOOLS_ENABLED env var.

Categories: docs, project_info, db, search, env, git, logs, bitbucket, postman, postman_official
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
PROJECT_ROOT = _path.parent # Assuming mcp_server is inside the project root
if str(_path) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(_path))

from mcp.server.fastmcp import FastMCP

# Category-based toggles. Default: all. Omit a category to disable it.
# docs, project_info, db, search, env, git, logs, bitbucket, postman, postman_official
_ENABLED = os.getenv(
    "CURSOR_TOOLS_ENABLED",
    "docs,project_info,db,search,env,git,logs,bitbucket,postman,postman_official,google_search,fetch,memory",
).split(",")
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
from tools_postman import register as register_postman
from tools_postman_official import register as register_postman_official
from tools_google_search import register as register_google_search
from tools_fetch import register as register_fetch
from tools_memory import register as register_memory

register_docs(mcp, _enabled)
register_project_info(mcp, _enabled)
register_db(mcp, _enabled)
register_search(mcp, _enabled)
register_env(mcp, _enabled)
register_git(mcp, _enabled)
register_logs(mcp, _enabled)
register_bitbucket(mcp, _enabled)
register_postman(mcp, _enabled)
register_postman_official(mcp, _enabled)
register_google_search(mcp, _enabled)
register_fetch(mcp, _enabled)
register_memory(mcp, _enabled)


@mcp.tool()
def mcp_health_check() -> str:
    """Verify MCP server health: check project root access and lists enabled/disabled categories."""
    status = []
    # 1. Check Project Root
    root_exists = PROJECT_ROOT.exists()
    status.append(f"Project Root: {'✅' if root_exists else '❌'} ({PROJECT_ROOT})")

    # 2. Categories
    status.append("\nTool Categories:")
    all_categories = [
        "docs", "project_info", "db", "search", "env",
        "git", "logs", "bitbucket", "postman", "postman_official",
        "google_search", "fetch", "memory"
    ]
    for cat in all_categories:
        icon = "🟢" if _enabled(cat) else "⚪"
        status.append(f"{icon} {cat}")

    return "\n".join(status)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
