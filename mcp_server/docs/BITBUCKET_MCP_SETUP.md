# Bitbucket MCP Setup (Requirements)

This doc lists exactly what you must provide to enable Bitbucket MCP tools.

## Required inputs

- **Workspace slug**: the URL segment in `https://bitbucket.org/<workspace-slug>/<repo>`
- **Username**: your Bitbucket account username (not email)
- **App password / API token**: create a scoped token in Bitbucket
- Which tools do you want? (e.g., list repos, read PRs, create PR, search code, list issues)

## Recommended token scope (full access)

Use a scoped token and select these permissions:

- Account: Read
- Workspace membership: Read
- Projects: Read
- Repositories: Read + Write
- Pull requests: Read + Write
- Issues: Read + Write
- Webhooks: Read + Write (optional)

If you only need read-only access, select Read for each category above.

## Where to store secrets

Use environment variables (do not commit secrets). Example names:

- `BITBUCKET_USERNAME`
- `BITBUCKET_PASSWORD`
- `BITBUCKET_WORKSPACE`

You can store these in your shell profile or a local `.env` or `.bitbucket_env` file and pass them to your MCP config.

## Example (MCP config snippet)

```json
{
  "mcpServers": {
    "bitbucket": {
      "command": "npx",
      "args": ["-y", "bitbucket-mcp"],
      "env": {
        "BITBUCKET_USERNAME": "${env:BITBUCKET_USERNAME}",
        "BITBUCKET_PASSWORD": "${env:BITBUCKET_PASSWORD}",
        "BITBUCKET_WORKSPACE": "${env:BITBUCKET_WORKSPACE}"
      }
    }
  }
}
```
