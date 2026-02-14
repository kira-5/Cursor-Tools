# SEARCH Usage Guide

High-precision searching across code and documentation.

## 🛠️ Tools

| Tool | Parameters | Description |
| :--- | :--- | :--- |
| `grep_code` | `pattern`, `glob` (optional) | Regex search across the entire codebase. |
| `search_docs` | `query`, `docs_path` (optional) | Search within `backend/app/assets/docs/`. |

## 💡 Example Prompts
- "Grep the codebase for all instances of `TENANT_NAME`."
- "Find where the `FastAPI` instance is initialized in `*.py` files."
- "Search the internal docs for 'authentication'."

## 🚀 Best Practices
- Use specific file extensions in `grep_code` (e.g., `*.toml`) to reduce noise.
- This tool is better than standard Cursor search for finding exact regex patterns.
