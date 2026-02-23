# Jira Integration (`jira`)

This MCP server provides a native integration with the Atlassian Jira REST API.
It allows Cursor (and other IDE clients) to read, search, and write to Jira projects directly from the editor.

## Configuration

Config is loaded from (in order):

1. **`[Project root]/mcp_env_config/.jira_env`** – per-project overrides (create this folder if you want overrides).
2. **`mcp_server/env_config/.jira_env`** – default location in this repo (works in any IDE; project root is detected from the MCP server’s location).

To use the Jira tools, ensure `.jira_env` exists in one of the above and contains:

```env
JIRA_HOST=https://yourcompany.atlassian.net
JIRA_EMAIL=your.email@company.com
JIRA_API_TOKEN=your_atlassian_api_token
JIRA_DEFAULT_PROJECT=MTP
JIRA_DEFAULT_COMPONENTS=PriceSmart-BasePricing
```

**IDE-agnostic:** If your IDE starts the MCP server with a different working directory, the server still finds the repo that contains `mcp_server` and uses `mcp_server/env_config/.jira_env`. You can override the project root by setting **`MCP_PROJECT_ROOT`** (or `CURSOR_PROJECT_ROOT`) to your repo path in the MCP server’s environment.

**Note:** If no `.jira_env` exists anywhere, a template is created at `mcp_env_config/.jira_env` on first run.

**Note:** Create an Atlassian API Token at:
[https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)

## Available Tools

The following tools are available when `jira` is enabled in `CURSOR_TOOLS_ENABLED`:

### Reading and Searching
* **`jira_get_issue`**: Gets full details, fields, transitions, and recent comments for a single Jira issue.
* **`jira_search_issues`**: Runs a JQL search query (e.g. `assignee = currentUser() AND status = "In Progress"`).
* **`jira_list_projects`**: Lists all projects available to the authenticated user.
* **`jira_get_project`**: Gets project details including issue types and available components/roles.
* **`jira_list_sprints`**: List sprints for a specific board.
* **`jira_get_sprint_issues`**: Retrieves all the issues assigned to a specific sprint.

### Writing and Updating
* **`jira_create_issue`**: Creates a new Jira issue. Can automatically use `JIRA_DEFAULT_PROJECT` and `JIRA_DEFAULT_COMPONENTS` if none are passed.
* **`jira_update_issue`**: Updates specific fields on an issue.
* **`jira_add_comment`**: Appends a new comment to a ticket.
* **`jira_transition_issue`**: Moves an issue through its workflow based on the exact transition name (e.g. `Done`, `In Review`).
* **`jira_assign_issue`**: Assigns an issue to a user by their Atlassian Account ID.
* **`jira_link_issue`**: Creates a link between two Jira tickets (e.g. `Blocks`, `Relates To`).
