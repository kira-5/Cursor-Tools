# ENV Usage Guide

Securely read configuration values from `.secrets.toml` or `.env` files with automatic credential masking.

## 🛠️ Tools

| Tool | Parameters | Description |
| :--- | :--- | :--- |
| `get_config` | `config_path` (optional), `section` (optional) | Reads and parses TOML or ENV files. |

## 💡 Example Prompts
- "Read the database configuration from `.secrets.toml`."
- "Show me the environment variables in `.env`."
- "Get the `base-pricing-local` section from the config."

## 🚀 Best Practices
- The tool automatically masks values containing `key`, `secret`, `token`, `password`, or `auth` to prevent leaking credentials into the chat log.
- It prioritizes `backend/.secrets.toml` as the default project configuration source.
