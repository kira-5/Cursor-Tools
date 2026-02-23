# GOOGLE_SEARCH Usage Guide

Native high-performance web research within Cursor.

## 🛠️ Tools

| Tool | Parameters | Description |
| :--- | :--- | :--- |
| `google_search` | `query` | Performs a Google search and returns the top 5 results. |

## 💡 Example Prompts
- "Search for the latest FastAPI documentation for background tasks."
- "Find the official GitHub repository for the Model Context Protocol."
- "Google the error: `PydanticValidationError: field required`."

## ⚙️ Configuration
- Requires `GOOGLE_API_KEY` and `GOOGLE_CX` in `mcp_env_config/.google_env` (at your project root).
- If the file is missing, it will be automatically created with a template.

## 🚀 Best Practices
- Be specific with your query to get the most relevant snippet.
- If a result looks promising, use the **Fetch** tool (`fetch_url`) to read the full page and convert it to Markdown.
