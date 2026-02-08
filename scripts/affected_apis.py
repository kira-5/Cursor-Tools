#!/usr/bin/env python3
"""
Show affected API areas from git changes.

Usage:
  python scripts/affected_apis.py           # unstaged + staged changes
  python scripts/affected_apis.py --staged  # staged only (before commit)

Config: .affected_apis.json in project root. See .affected_apis.json.example.
"""
import json
import subprocess
import sys
from pathlib import Path

# Defaults (overridden by config file)
DEFAULT_APP_PATH = "backend/app"
DEFAULT_API_PREFIX = ""
DEFAULT_MODULE_TO_TAG = {}


def get_project_root() -> Path:
    """Project root = git repo root (when run from project) or script's parent (fallback)."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip())
    except Exception:
        pass
    return Path(__file__).resolve().parent.parent


def load_config() -> dict:
    """Load config from project root: .affected_apis.json or affected_apis.config.json (legacy)."""
    root = get_project_root()
    for path in [
        root / ".affected_apis.json",
        root / "affected_apis.config.json",
        root / "scripts" / "affected_apis.config.json",
    ]:
        if path.exists():
            try:
                return json.loads(path.read_text())
            except json.JSONDecodeError:
                pass
    return {}


def get_config() -> tuple[str, str, dict]:
    """Return (app_path, api_prefix, module_to_tag)."""
    cfg = load_config()
    app_path = cfg.get("app_path", DEFAULT_APP_PATH)
    api_prefix = cfg.get("api_prefix", DEFAULT_API_PREFIX)
    module_to_tag = cfg.get("module_to_tag", DEFAULT_MODULE_TO_TAG)
    return app_path, api_prefix, module_to_tag


def get_changed_files(staged_only: bool = False) -> list[str]:
    """Get list of changed files from git."""
    cmd = ["git", "diff", "--name-only"]
    if staged_only:
        cmd.append("--cached")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=get_project_root())
    if result.returncode != 0:
        return []
    return [f.strip() for f in result.stdout.splitlines() if f.strip()]


def file_to_area(filepath: str, app_path: str) -> str | None:
    """Map file path to API area (can be nested like reporting/exception_report)."""
    prefix = app_path.rstrip("/") + "/"
    if not filepath.startswith(prefix):
        return None
    parts = filepath.replace(prefix, "").split("/")
    if not parts:
        return None
    if len(parts) >= 2 and parts[0] == "reporting":
        return f"{parts[0]}/{parts[1]}"
    return parts[0]


def area_to_tag(area: str, module_to_tag: dict) -> str:
    """Map area to display tag."""
    if area in module_to_tag:
        return module_to_tag[area]
    if "/" in area:
        _, sub = area.split("/", 1)
        return module_to_tag.get(area) or module_to_tag.get(sub, area)
    return module_to_tag.get(area, area)


def main():
    app_path, api_prefix, module_to_tag = get_config()
    staged_only = "--staged" in sys.argv or "--cached" in sys.argv
    files = get_changed_files(staged_only=staged_only)

    if not files:
        scope = "staged" if staged_only else "unstaged + staged"
        print(f"No {scope} changes. Run after making edits or staging files.")
        return 0

    prefix = app_path.rstrip("/") + "/"
    areas = set()
    app_files = []
    for f in files:
        if f.startswith(prefix):
            app_files.append(f)
            area = file_to_area(f, app_path)
            if area:
                tag = area_to_tag(area, module_to_tag)
                areas.add(tag)

    if not areas:
        print(f"Changed files (none in {app_path}):")
        for f in files[:20]:
            print(f"  {f}")
        if len(files) > 20:
            print(f"  ... and {len(files) - 20} more")
        return 0

    # Output
    scope = "staged" if staged_only else "all"
    print(f"Affected APIs ({scope} changes):")
    print()
    for tag in sorted(areas):
        print(f"  • {tag}")
    if api_prefix:
        print()
        print(f"API prefix: {api_prefix}")
    print()
    print(f"Changed files in {app_path}:")
    for f in app_files[:15]:
        print(f"  {f}")
    if len(app_files) > 15:
        print(f"  ... and {len(app_files) - 15} more")

    return 0


if __name__ == "__main__":
    sys.exit(main())
