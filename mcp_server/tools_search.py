"""Search category: grep_code, search_docs."""

import re
from pathlib import Path

_MCP_DIR = Path(__file__).resolve().parent
from utils import get_project_root

PROJECT_ROOT = get_project_root()

# Directories to skip when searching code
_IGNORE_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".cursor"}


def _grep_in_file(path: Path, pattern: str, case_sensitive: bool = False) -> list[tuple[int, str]]:
    """Search for pattern in file. Returns list of (line_num, line_text)."""
    try:
        text = path.read_text(errors="ignore")
    except Exception:
        return []
    flags = 0 if case_sensitive else re.IGNORECASE
    matches = []
    for i, line in enumerate(text.splitlines(), 1):
        if re.search(pattern, line, flags):
            matches.append((i, line))
    return matches


def register(mcp, enabled_fn):
    """Register search tools. Disabled when 'search' category is off."""

    @mcp.tool()
    def grep_code(
        pattern: str,
        glob: str = "*.py",
        case_sensitive: bool = False,
        max_matches: int = 50,
    ) -> str:
        """Search for a regex pattern in the codebase. Use glob (e.g., *.py, **/*.html) to narrow scope. Ideal for finding function definitions or variable usage."""
        if not enabled_fn("search"):
            return "Tool disabled. Enable 'search' in CURSOR_TOOLS_ENABLED (e.g. docs,project_info,db,search)."
        results = []
        count = 0
        pattern_glob = glob.replace("**/", "").lstrip("./") or "*"
        for path in PROJECT_ROOT.rglob(pattern_glob):
            if not path.is_file():
                continue
            rel_parts = path.relative_to(PROJECT_ROOT).parts
            if any(p in _IGNORE_DIRS for p in rel_parts):
                continue
            matches = _grep_in_file(path, pattern, case_sensitive)
            for line_num, line_text in matches:
                if count >= max_matches:
                    results.append(f"... (truncated at {max_matches} matches)")
                    break
                results.append(f"{path.relative_to(PROJECT_ROOT)}:{line_num}: {line_text.strip()[:200]}")
                count += 1
            if count >= max_matches:
                break
        if not results:
            return f"No matches for pattern: {pattern}"
        return "\n".join(results)

    @mcp.tool()
    def search_docs(
        query: str,
        docs_path: str | None = None,
        case_sensitive: bool = False,
    ) -> str:
        """Iterate through project documentation and search for specific text. Use this when global grep is too noisy. Default path: backend/app/assets/docs/."""
        if not enabled_fn("search"):
            return "Tool disabled. Enable 'search' in CURSOR_TOOLS_ENABLED (e.g. docs,project_info,db,search)."
        base = PROJECT_ROOT / (docs_path or "backend/app/assets/docs")
        if not base.exists():
            return f"Docs path not found: {base}"
        flags = 0 if case_sensitive else re.IGNORECASE
        matches = []
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            try:
                text = path.read_text(errors="ignore")
            except Exception:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if re.search(re.escape(query), line, flags):
                    rel = path.relative_to(PROJECT_ROOT)
                    matches.append(f"{rel}:{i}: {line.strip()[:150]}")
                    if len(matches) >= 30:
                        break
            if len(matches) >= 30:
                break
        if not matches:
            return f"No matches for '{query}' in docs"
        return "\n".join(matches)
