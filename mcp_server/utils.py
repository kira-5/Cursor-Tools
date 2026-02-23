import os
from pathlib import Path


def _find_repo_root(start: Path) -> Path | None:
    """Walk up from start; return first directory that has .git or .cursor."""
    start = start.resolve()
    for parent in [start] + list(start.parents):
        if (parent / ".git").exists() or (parent / ".cursor").exists():
            return parent
    return None


def get_project_root(start_path: Path | None = None) -> Path:
    """
    Detect project root in an IDE-agnostic way:

    1. Explicit env: MCP_PROJECT_ROOT or CURSOR_PROJECT_ROOT (any IDE can set these).
    2. Search upward from start_path (default: CWD) for .git or .cursor.
    3. If start_path is None and CWD search fails, search from this file's package dir.
    4. Fallback to CWD, then home directory.

    Pass start_path=mcp_dir when resolving config so the repo containing the MCP
    server is found regardless of which IDE started the process or what CWD is.
    """
    for env_var in ("MCP_PROJECT_ROOT", "CURSOR_PROJECT_ROOT"):
        if env_root := os.getenv(env_var):
            return Path(env_root).resolve()

    try:
        current = (start_path or Path.cwd()).resolve()
        root = _find_repo_root(current)
        if root is not None:
            return root
        if start_path is None:
            pkg_dir = Path(__file__).resolve().parent
            root = _find_repo_root(pkg_dir)
            if root is not None:
                return root
        if current.as_posix() != "/":
            return current
    except Exception:
        pass
    return Path.home()


def setup_config_file(filename: str, mcp_dir: Path, template: str) -> Path:
    """
    Finds or creates a configuration file. IDE-agnostic: project root is resolved
    from the repo containing mcp_dir (or MCP_PROJECT_ROOT / CURSOR_PROJECT_ROOT).

    Precedence:
    1. {mcp_dir}/env_config/{filename}  (package/repo default – use this for real credentials)
    2. PROJECT_ROOT/mcp_env_config/{filename}  (project root override)

    If the file does not exist in any of these locations, it is created at
    PROJECT_ROOT/mcp_env_config/{filename} using the provided template.
    """
    # Resolve project root from repo containing the MCP server (works in any IDE)
    project_root = get_project_root(mcp_dir)
    env_config_dir = project_root / "mcp_env_config"
    mcp_package_env = mcp_dir / "env_config"

    # When MCP_PROJECT_ROOT/CURSOR_PROJECT_ROOT is set, prefer repo's mcp_server/env_config
    # (uvx may run from cache so mcp_dir can be outside the repo)
    locations = [mcp_package_env / filename, env_config_dir / filename]
    if os.environ.get("MCP_PROJECT_ROOT") or os.environ.get("CURSOR_PROJECT_ROOT"):
        repo_mcp_env = project_root / "mcp_server" / "env_config" / filename
        if repo_mcp_env.exists():
            locations.insert(0, repo_mcp_env)

    for loc in locations:
        if loc.exists():
            return loc

    # If not found, create in mcp_env_config
    env_config_dir.mkdir(exist_ok=True, parents=True)
    target_file = env_config_dir / filename
    target_file.write_text(template.strip() + "\n")
    return target_file


def load_env_file(filename: str, mcp_dir: Path, template: str) -> None:
    """
    Finds or creates an env file using setup_config_file, then loads it into os.environ.
    Does not overwrite existing environment variables.
    """
    env_path = setup_config_file(filename, mcp_dir, template)

    for line in env_path.read_text().splitlines():
        line = line.strip()
        # Handle comments
        if "#" in line:
            line = line[: line.index("#")].strip()

        if line and "=" in line:
            k, _, v = line.partition("=")
            # setdefault ensures we don't overwrite if it's already set in true environment
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
