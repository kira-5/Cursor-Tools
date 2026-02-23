# CONFLUENCE Usage Guide

Directly interact with Confluence pages, search content, and management.

## 🛠️ Tools

| Tool | Parameters | Description |
| :--- | :--- | :--- |
| `confluence_search_pages` | `cql` | Search Confluence using CQL (Confluence Query Language). |
| `confluence_get_page` | `page_id` | Fetch full details and content of a page. |
| `confluence_create_page` | `space_id`, `title`, `content_markdown`, `parent_id` (opt) | Create a new page. |
| `confluence_update_page` | `page_id`, `title`, `content_markdown`, `version_number` | Update an existing page. |
| `confluence_add_comment` | `page_id`, `comment_text` | Add a comment to a page. |

## 💡 Example Prompts
- "Search Confluence for 'architecture' in the MTP space."
- "Get the content of page ID 123456789."
- "Update the 'Meeting Notes' page with a summary of today's chat."
- "Create a new page in space 'DEV' titled 'Refactor Plan'."

## ⚙️ Configuration
- **Auth**: Reuses Jira credentials from `mcp_env_config/.jira_env`.
- **Primary Config**: `JIRA_HOST`, `JIRA_EMAIL`, and `JIRA_API_TOKEN`.
- **Custom Config**: You can optionally create `mcp_env_config/.confluence_env` for Confluence-specific overrides.

## 🚀 Best Practices
- Use `confluence_search_pages` to find the `page_id` and current `version_number` before updating.
- CQL examples: `space = "MTP" AND title ~ "Architecture"` or `text ~ "design"`.
