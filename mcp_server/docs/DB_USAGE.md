# DB Usage Guide

Direct PostgreSQL introspection and querying. Supports multiple databases via configuration.

## 🛠️ Tools

| Tool | Parameters | Description |
| :--- | :--- | :--- |
| `list_databases` | None | Show all databases available in `mcp_server/databases.json`. |
| `run_database_query` | `sql`, `database_name` (optional) | Execute read-only SQL queries. |
| `list_tables` | `schema_name`, `database_name` (optional) | List tables within a specific schema. |
| `describe_table` | `schema_name`, `table_name` | Show columns, types, and nullability. |

## 💡 Example Prompts
- "List all tables in the `base_pricing` schema."
- "Count the rows in the `orders` table."
- "Describe the columns of the `users` table."
- "Run this query on `leslies_uat`: SELECT * FROM ..."

## ⚙️ Configuration
- **Databases**: Mapped in `mcp_env_config/databases.json`.
- **Credentials**: Stored in `mcp_env_config/.db_env`.
- **Auto-Scaffolding**: Check `mcp_env_config/` at your project root for templates if files are missing.

## 🚀 Best Practices
- Always `list_tables` before assuming a table exists.
- Use `describe_table` to avoid "Column not found" errors in your SQL.
- Queries are read-only by default for safety.
