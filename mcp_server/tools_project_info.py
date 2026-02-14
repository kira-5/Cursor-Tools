"""Project info category: get_project_info (name, version, Python, tech stack)."""
import os
import re
from pathlib import Path

_MCP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(os.environ.get("CURSOR_PROJECT_ROOT", _MCP_DIR.parent))


def _get_version() -> str | None:
    """Get backend version from setup.py or pyproject.toml."""
    setup = PROJECT_ROOT / "backend" / "setup.py"
    if setup.exists():
        text = setup.read_text()
        m = re.search(r'version\s*=\s*["\']([^"\']+)["\']', text, re.I)
        if m:
            return m.group(1)
    for p in [PROJECT_ROOT / "backend" / "pyproject.toml", PROJECT_ROOT / "pyproject.toml"]:
        if p.exists():
            try:
                import tomllib
                with open(p, "rb") as f:
                    data = tomllib.load(f)
                v = data.get("tool", {}).get("poetry", {}).get("version")
                if v:
                    return str(v)
            except Exception:
                pass
    return None


def _get_python_version() -> str | None:
    """Get Python version from setup.py, pyproject.toml, or .python-version."""
    for p in [PROJECT_ROOT / "backend" / "setup.py", PROJECT_ROOT / "setup.py"]:
        if p.exists():
            m = re.search(r'python_requires\s*=\s*["\']([^"\']+)["\']', p.read_text(), re.I)
            if m:
                return m.group(1)
    for p in [PROJECT_ROOT / "pyproject.toml", PROJECT_ROOT / "backend" / "pyproject.toml"]:
        if p.exists():
            try:
                import tomllib
                with open(p, "rb") as f:
                    data = tomllib.load(f)
                py = data.get("tool", {}).get("poetry", {}).get("dependencies", {}).get("python")
                if py:
                    return str(py)
            except Exception:
                pass
    for p in [PROJECT_ROOT / "runtime.txt", PROJECT_ROOT / "backend" / "runtime.txt"]:
        if p.exists():
            return p.read_text().strip()
    for p in [PROJECT_ROOT / ".python-version", PROJECT_ROOT / "backend" / ".python-version"]:
        if p.exists():
            return p.read_text().strip()
    return None


def _get_project_name() -> str | None:
    """Get project name from readme or setup.py."""
    for readme in [PROJECT_ROOT / "readme.md", PROJECT_ROOT / "README.md", PROJECT_ROOT / "backend" / "README.md"]:
        if readme.exists():
            first = readme.read_text().splitlines()[0].strip()
            if first.startswith("#"):
                return first.lstrip("#").strip()
    setup = PROJECT_ROOT / "backend" / "setup.py"
    if setup.exists():
        m = re.search(r'name\s*=\s*["\']([^"\']+)["\']', setup.read_text(), re.I)
        if m:
            return m.group(1)
    return None


def _get_tech_stack() -> str:
    """Get tech stack from requirements.txt."""
    req = PROJECT_ROOT / "backend" / "requirements.txt"
    if not req.exists():
        req = PROJECT_ROOT / "requirements.txt"
    if not req.exists():
        return "requirements.txt not found"
    return req.read_text()


def register(mcp, enabled_fn):
    """Register project_info tools. Disabled when 'project_info' category is off."""

    @mcp.tool()
    def get_project_info() -> str:
        """Get project info: name, version, Python version, and tech stack (requirements) in one call."""
        if not enabled_fn("project_info"):
            return "Tool disabled. Enable 'project_info' in CURSOR_TOOLS_ENABLED."
        import json
        info = {
            "project": _get_project_name() or "unknown",
            "version": _get_version() or "unknown",
            "python": _get_python_version() or "unknown",
            "tech_stack": _get_tech_stack(),
        }
        return json.dumps(info, indent=2)
