# Jira Integration (`jira`)

This MCP server provides a native integration with the Atlassian Jira REST API.
It allows Cursor (and other clients) to read, search, and write to Jira projects directly from the IDE.

## Configuration

To use the Jira tools, you must populate the `.jira_env` file in the root of the `mcp_server` directory:

```env
JIRA_HOST=https://yourcompany.atlassian.net
JIRA_EMAIL=your.email@company.com
JIRA_API_TOKEN=your_atlassian_api_token
JIRA_DEFAULT_PROJECT=MTP
JIRA_DEFAULT_COMPONENTS=PriceSmart-BasePricing
```

**Note:** You can quickly create an Atlassian API Token by visiting:
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
