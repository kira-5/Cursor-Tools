"""Git category: git_status, git_branches, recent_commits."""
import os
import subprocess
from pathlib import Path

_MCP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(os.environ.get("CURSOR_PROJECT_ROOT", _MCP_DIR.parent))


def _run_git(args: list[str]) -> str:
    """Run git command, return stdout or error message."""
    try:
        r = subprocess.run(
            ["git"] + args,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if r.returncode != 0:
            return r.stderr or r.stdout or "git command failed"
        return r.stdout.strip()
    except FileNotFoundError:
        return "git not found"
    except subprocess.TimeoutExpired:
        return "git command timed out"


def register(mcp, enabled_fn):
    """Register git tools. Disabled when 'git' category is off."""

    @mcp.tool()
    def git_status() -> str:
        """Show git status (modified, staged, untracked files)."""
        if not enabled_fn("git"):
            return "Tool disabled. Enable 'git' in CURSOR_TOOLS_ENABLED (e.g. docs,project_info,db,search,env,git)."
        return _run_git(["status", "--short"])

    @mcp.tool()
    def git_branches() -> str:
        """List git branches. Current branch marked with *."""
        if not enabled_fn("git"):
            return "Tool disabled. Enable 'git' in CURSOR_TOOLS_ENABLED."
        return _run_git(["branch", "-a"])

    @mcp.tool()
    def recent_commits(n: int = 10) -> str:
        """Show recent n commits (default 10). Format: hash short message."""
        if not enabled_fn("git"):
            return "Tool disabled. Enable 'git' in CURSOR_TOOLS_ENABLED."
        return _run_git(["log", "-n", str(n), "--oneline"])
