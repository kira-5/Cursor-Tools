# MEMORY Usage Guide

Cross-chat context persistence: Let the AI remember facts, patterns, and preferences across different talk sessions.

## 🛠️ Tools

| Tool | Parameters | Description |
| :--- | :--- | :--- |
| `store_memory` | `key`, `value` | Persist a fact or preference to a local JSON file. |
| `retrieve_memory` | `key` | Look up a previously stored fact. |
| `list_memories` | None | Show all keys currently stored in the memory. |

## 💡 Example Prompts
- "Remember that we use functional components for all React work."
- "What did I tell you about the database naming convention?"
- "List everything you remember about the project preferences."

## 🚀 Best Practices
- Use `store_memory` for "knowledge injection" that you don't want to repeat every time you open a new chat.
- Memories are stored locally in `mcp_server/.memory.json`.
- Periodically use `list_memories` to clean up old or redundant entries.
