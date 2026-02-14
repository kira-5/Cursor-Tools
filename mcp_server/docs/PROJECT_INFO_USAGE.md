# PROJECT_INFO Usage Guide

Quickly identify the project's technology stack, versions, and core metadata.

## 🛠️ Tools

| Tool | Parameters | Description |
| :--- | :--- | :--- |
| `get_project_info` | None | Returns name, version, Python version, and a list of dependencies. |

## 💡 Example Prompts
- "What is the current version of this project?"
- "Check the tech stack and tell me if we are using FastAPI."
- "What Python version is required for this backend?"

## 🚀 Best Practices
- Run this tool at the very beginning of a new session to ground the agent in the correct tech stack.
- It automatically checks both the project root and the `backend/` directory for configuration files (`pyproject.toml`, `requirements.txt`).
