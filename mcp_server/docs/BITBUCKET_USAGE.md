# BITBUCKET Usage Guide

Automate repository management, pull requests, and issue tracking.

## 🛠️ Tools

| Tool | Parameters | Description |
| :--- | :--- | :--- |
| `bitbucket_list_repos` | `workspace` | List repositories in a workspace. |
| `bitbucket_get_repo` | `workspace`, `repo_slug` | Get detailed repository metadata. |
| `bitbucket_list_pull_requests` | `workspace`, `repo_slug`, `state` | List open/merged PRs. |
| `bitbucket_create_pull_request` | `workspace`, `repo_slug`, `title`, `source_branch`, `description` | Create a new PR. |
| `bitbucket_list_issues` | `workspace`, `repo_slug` | List repository issues. |
| `bitbucket_create_issue` | `workspace`, `repo_slug`, `title`, `content` | Create a new bug or task. |
| `bitbucket_get_file` | `workspace`, `repo_slug`, `file_path`, `ref` | Fetch raw file content from a branch. |

## 💡 Example Prompts
- "List all pull requests for the `cursor-tools` repo."
- "Create a new PR from `feature-x` to `main`."
- "Show me all open issues in our workspace."
- "Fetch the `README.md` from the `develop` branch of `backend-api`."

## ⚙️ Configuration
- **Auth**: Requires a Bitbucket App Password stored in `mcp_server/.bitbucket_env`.

## 🚀 Best Practices
- Use `bitbucket_list_repos` first if you aren't sure of the exact `repo_slug`.
- When fetching files, specify the `ref` (branch name) to ensure you get the latest version.
