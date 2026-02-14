# GIT Usage Guide

Manage local git state, branches, and commit history.

## 🛠️ Tools

| Tool | Parameters | Description |
| :--- | :--- | :--- |
| `git_status` | None | Show modified, staged, and untracked files. |
| `git_branches` | None | List local branches (current marked with `*`). |
| `recent_commits` | `n` (optional, default 10) | Show the last `n` commits with short hashes and messages. |

## 💡 Example Prompts
- "What files have I changed in this branch?"
- "List all local branches."
- "Show me the last 5 commits."

## 🚀 Best Practices
- Run `git_status` regularly to help the agent track which files are ready for commitment.
- Use `recent_commits` to understand the context of recent changes made by you or other team members.
- This category is purely for local inspection; use **Bitbucket** tools for remote operations.
