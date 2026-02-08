"""Env/Config category: get_config."""
import os
from pathlib import Path

_MCP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(os.environ.get("CURSOR_PROJECT_ROOT", _MCP_DIR.parent))

# Keys (case-insensitive) whose values should be masked
_SENSITIVE_KEYS = frozenset(
    k.lower()
    for k in ("password", "secret", "key", "token", "credential", "api_key", "apikey")
)


def _mask_value(key: str, value: str) -> str:
    """Mask value if key looks sensitive."""
    if any(s in key.lower() for s in _SENSITIVE_KEYS):
        return "***" if value else ""
    return value


def _load_toml_safe(path: Path) -> dict:
    """Load TOML, masking sensitive values."""
    import tomllib
    with open(path, "rb") as f:
        data = tomllib.load(f)
    result = {}
    for section_name, section_data in data.items():
        if not isinstance(section_data, dict):
            result[section_name] = section_data
            continue
        masked = {}
        for k, v in section_data.items():
            if isinstance(v, str):
                masked[k] = _mask_value(k, v)
            else:
                masked[k] = v
        result[section_name] = masked
    return result


def _load_env_safe(path: Path) -> dict:
    """Load .env, masking sensitive values."""
    text = path.read_text()
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip().strip('"').strip("'")
            result[k] = _mask_value(k, v)
    return result


def register(mcp, enabled_fn):
    """Register env/config tools. Disabled when 'env' category is off."""

    @mcp.tool()
    def get_config(
        config_path: str | None = None,
        section: str | None = None,
    ) -> str:
        """Read config from .secrets.toml or .env. Sensitive values (password, secret, key, token) are masked. Pass config_path (e.g. backend/.secrets.toml) or section (e.g. base-pricing-local) to narrow."""
        if not enabled_fn("env"):
            return "Tool disabled. Enable 'env' in CURSOR_TOOLS_ENABLED (e.g. docs,project_info,db,search,env,git)."
        path = PROJECT_ROOT / (config_path or "backend/.secrets.toml")
        if not path.exists():
            env_path = PROJECT_ROOT / ".env"
            if env_path.exists():
                path = env_path
            else:
                return f"Config not found: {config_path or 'backend/.secrets.toml'}"
        try:
            if path.suffix in (".toml", ".tml"):
                data = _load_toml_safe(path)
                if section:
                    data = {k: v for k, v in data.items() if k == section}
            else:
                data = {"env": _load_env_safe(path)}
        except Exception as e:
            return f"Error reading config: {e}"
        import json
        return json.dumps(data, indent=2)
