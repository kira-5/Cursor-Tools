# Jira MCP Setup (Requirements)

This doc lists exactly what you must provide to enable Jira MCP tools.

## Required inputs

- **Site URL**: your Atlassian cloud URL (e.g., `https://yourcompany.atlassian.net`)
- **Email / username**: the account used to create the token
- **API token**: create a scoped token for Jira

## Token creation

Select **Jira** when creating the token.

## Recommended token scope (full access)

Use a scoped token and select permissions that cover your workflows:

- Read issues and projects
- Create or update issues
- Comment and transition issues

If you only need read-only access, select read scopes only.

## Where to store secrets

Use environment variables (do not commit secrets). Example names:

- `JIRA_SITE_URL`
- `JIRA_EMAIL`
- `JIRA_API_TOKEN`

You can store these in your shell profile or a local `.env` file and pass them to your MCP config.

## What you must provide

- Site URL
- Email / username
- API token (scoped, recommended)
- Required scopes (use full access list above, or read-only)

## Example (MCP config snippet)

```json
{
  "mcpServers": {
    "jira": {
      "serverUrl": "https://mcp.atlassian.com/v1/mcp",
      "headers": {
        "Authorization": "Bearer ${env:JIRA_API_TOKEN}"
      }
    }
  }
}
```
