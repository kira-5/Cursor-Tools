import os
from pathlib import Path
import re

tools_dir = Path("mcp_server")
files_to_fix = [
    "tools_confluence.py", "tools_jira.py", "tools_bitbucket.py",
    "tools_db.py", "tools_git.py", "tools_docs.py", "tools_env.py",
    "tools_postman.py", "tools_logs.py", "tools_search.py",
    "tools_memory.py", "tools_project_info.py"
]

for fname in files_to_fix:
    fpath = tools_dir / fname
    if not fpath.exists(): continue
    content = fpath.read_text()

    # Add utils import
    if "from utils import get_project_root" not in content:
        content = content.replace("from pathlib import Path", "from pathlib import Path\nfrom utils import get_project_root")

    # Replace existing fallback logic
    content = re.sub(
        r"PROJECT_ROOT\s*=\s*Path\(os\.environ\.get\([^)]+\)\)",
        "PROJECT_ROOT = get_project_root()",
        content
    )

    # Ensure PROJECT_ROOT exists where we need it
    if "PROJECT_ROOT =" not in content and "_MCP_DIR" in content:
        content = content.replace(
            "_MCP_DIR = Path(__file__).resolve().parent",
            "_MCP_DIR = Path(__file__).resolve().parent\nPROJECT_ROOT = get_project_root()"
        )

    # Patch user configuration file locations to use PROJECT_ROOT
    content = content.replace("_MCP_DIR / \".jira_env\"", "PROJECT_ROOT / \".jira_env\"")
    content = content.replace("_MCP_DIR / \".confluence_env\"", "PROJECT_ROOT / \".confluence_env\"")
    content = content.replace("_MCP_DIR / \".bitbucket_env\"", "PROJECT_ROOT / \".bitbucket_env\"")
    content = content.replace("_MCP_DIR / \".db_env\"", "PROJECT_ROOT / \".db_env\"")
    content = content.replace("_MCP_DIR / \"databases.json\"", "PROJECT_ROOT / \"databases.json\"")
    content = content.replace("_MCP_DIR / \".postman_env\"", "PROJECT_ROOT / \".postman_env\"")
    content = content.replace("_MCP_DIR / \".memory.json\"", "PROJECT_ROOT / \".memory.json\"")
    content = content.replace("_MCP_DIR.parent", "PROJECT_ROOT")

    fpath.write_text(content)

print("Updated tools successfully")
