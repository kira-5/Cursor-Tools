# POSTMAN Usage Guide

Comprehensive API management and local collection execution.

## 🛠️ Tools

| Tool | Parameters | Description |
| :--- | :--- | :--- |
| `postman_list_workspaces` | None | List all accessible workspaces. |
| `postman_get_collection` | `uid` | Fetch a full collection definition. |
| `postman_run_collection` | `collection_uid`, `environment_uid` (optional) | Run a collection locally using **Newman**. |
| `postman_add_request` | `collection_uid`, `request_path`, `method`, `url` | Add a new request to a collection. |
| `postman_rename_folder` | `collection_uid`, `folder_path`, `rename_to` | Organize your collections. |

## 💡 Example Prompts
- "Find the `Base Pricing` collection and run it on `UAT`."
- "Add a GET request to the `Users` folder in the `Auth` collection."
- "List all collections in my Personal workspace."

## ⚙️ Configuration
- Requires `POSTMAN_API_KEY` in `mcp_env_config/.postman_env` (at your project root).
- If the file is missing, a template will be created in `mcp_env_config/` automatically.
- For `postman_run_collection`, **Newman** must be installed on your system.

## 🚀 Best Practices
- Use `postman_search_collection_items` to quickly find a specific request by name.
- Always check the environment UID before running a collection to avoid hitting the wrong server.
