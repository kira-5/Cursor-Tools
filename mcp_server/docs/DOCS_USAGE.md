# DOCS Usage Guide

Access and search internal project documentation, including READMEs, setup guides, and architectural indices.

## 🛠️ Tools

| Tool | Parameters | Description |
| :--- | :--- | :--- |
| `get_docs_urls` | `priority` (core, recommended, optional) | Get curated Cursor docs for the tech stack. |
| `get_doc` | `doc_name` (`readme`, `mcp-setup`, `mcp-tools-reference`) | Read specific setup or reference documentation. |

## 💡 Example Prompts
- "Show me the project README."
- "Show me the MCP setup guide."
- "Open the Master Index of all MCP tools."
- "What core frameworks are recommended in the documentation?"

## 🚀 Best Practices
- Use `get_doc("cursor-index")` first to see a map of all available documentation.
- Combine with `search_docs` (from the **Search** category) to find specific topics in large files.
