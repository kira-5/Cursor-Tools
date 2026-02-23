import os
from pathlib import Path


def get_project_root() -> Path:
    """
    Detect project root by:
    1. Checking CURSOR_PROJECT_ROOT env var.
    2. Searching upwards from CWD for .git or .cursor.
    3. Fallback to CWD (but avoid returning / if possible).
    4. Last resort: User's home directory.
    """
    # 1. Explicit environment variable
    if env_root := os.getenv("CURSOR_PROJECT_ROOT"):
        return Path(env_root).resolve()

    try:
        # 2. Search upwards from CWD
        current = Path.cwd().resolve()
        for parent in [current] + list(current.parents):
            if (parent / ".git").exists() or (parent / ".cursor").exists():
                return parent

        # 3. Fallback to CWD if it's not root
        if current.as_posix() != "/":
            return current
    except Exception:
        pass

    # 4. Final fallback to home directory to avoid read-only / errors
    return Path.home()


def setup_config_file(filename: str, mcp_dir: Path, template: str) -> Path:
    """
    Finds or creates a configuration file in the following order of precedence:
    1. PROJECT_ROOT/mcp_env_config/{filename}
    2. {mcp_dir}/env_config/{filename}

    If the file does not exist in any of these locations, it is created at
    PROJECT_ROOT/mcp_env_config/{filename} using the provided template.
    """
    project_root = get_project_root()
    env_config_dir = project_root / "mcp_env_config"
    mcp_env_config_fallback = mcp_dir / "env_config"

    # Check possible locations
    locations = [env_config_dir / filename, mcp_env_config_fallback / filename]

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
