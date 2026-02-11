# Confluence MCP Setup (Requirements)

This doc lists exactly what you must provide to enable Confluence MCP tools.

## Required inputs

- **Site URL**: your Atlassian cloud URL (e.g., `https://yourcompany.atlassian.net`)
- **Email / username**: the account used to create the token
- **API token**: create a scoped token for Confluence

## Token creation

Select **Confluence** when creating the token.

## Recommended token scope (full access)

Use a scoped token and select permissions that cover your workflows:

- Read pages and spaces
- Create or update pages
- Comment and manage content

If you only need read-only access, select read scopes only.

## Where to store secrets

Use environment variables (do not commit secrets). Example names:

- `CONFLUENCE_SITE_URL`
- `CONFLUENCE_EMAIL`
- `CONFLUENCE_API_TOKEN`

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
    "confluence": {
      "serverUrl": "https://mcp.atlassian.com/v1/mcp",
      "headers": {
        "Authorization": "Bearer ${env:CONFLUENCE_API_TOKEN}"
      }
    }
  }
}
```
