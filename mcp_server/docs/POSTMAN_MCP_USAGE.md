# Postman MCP (Local) Usage

This doc covers the **local Postman MCP server** implemented in `mcp_server/tools_postman.py`.
It uses your Postman API key from `mcp_server/.postman_env`.

## Setup

1. Add your Postman API key:

```text
POSTMAN_API_KEY=your_key_here
```

1. Ensure the `postman` category is enabled in `CURSOR_TOOLS_ENABLED` (in `.cursor/mcp.json`).

1. Restart the MCP server in Cursor.

## Workspaces

List workspaces:

```text
postman_list_workspaces()
```

Get workspace:

```text
postman_get_workspace("WORKSPACE_ID")
```

Create workspace:

```text
postman_create_workspace("My Workspace", workspace_type="team", description="Team APIs")
```

Update workspace:

```text
postman_update_workspace("WORKSPACE_ID", name="New Name", description="Updated")
```

Delete workspace:

```text
postman_delete_workspace("WORKSPACE_ID")
```

Workspace members:

```text
postman_list_workspace_members("WORKSPACE_ID")
postman_add_workspace_members("WORKSPACE_ID", {"members":[{"email":"a@b.com","roles":["editor"]}]})
postman_remove_workspace_member("WORKSPACE_ID", "MEMBER_ID")
```

## Collections

List collections:

```text
postman_list_collections()
```

Get collection:

```text
postman_get_collection("COLLECTION_UID")
```

Create collection:

```text
postman_create_collection("My Collection", description="Local MCP")
```

Update collection metadata:

```text
postman_update_collection("COLLECTION_UID", name="New Name", description="Updated")
```

Delete collection:

```text
postman_delete_collection("COLLECTION_UID")
```

Search items:

```text
postman_search_collection_items("COLLECTION_UID", "login")
```

Get item by name:

```text
postman_get_collection_item("COLLECTION_UID", "Login")
```

Add folder (with parents):

```text
postman_add_folder("COLLECTION_UID", "Folder/Subfolder")
```

Add request:

```text
postman_add_request(
  "COLLECTION_UID",
  "Folder/Login",
  "POST",
  "https://api.example.com/login",
  headers={"Content-Type":"application/json"},
  body={"user":"a","pass":"b"}
)
```

Update request:

```text
postman_update_request(
  "COLLECTION_UID",
  "Folder/Login",
  method="PUT",
  url="https://api.example.com/login",
  headers={"X-Env":"dev"},
  body={"user":"a"},
  rename_to="Login v2"
)
```

Delete item (request or folder):

```text
postman_delete_item("COLLECTION_UID", "Folder/Login")
```

Rename folder:

```text
postman_rename_folder("COLLECTION_UID", "Folder/Old", "New")
```

Delete folder:

```text
postman_delete_folder("COLLECTION_UID", "Folder/Old")
```

### Dry-run changes

Use `dry_run=true` to preview the item diff without saving:

```text
postman_add_folder("COLLECTION_UID", "Folder/Subfolder", dry_run=true)
postman_add_request("COLLECTION_UID", "Folder/Login", "POST", "https://api...", dry_run=true)
postman_update_request("COLLECTION_UID", "Folder/Login", method="PUT", dry_run=true)
postman_delete_item("COLLECTION_UID", "Folder/Login", dry_run=true)
postman_rename_folder("COLLECTION_UID", "Folder/Old", "New", dry_run=true)
postman_delete_folder("COLLECTION_UID", "Folder/Old", dry_run=true)
```

## Environments

List environments:

```text
postman_list_environments()
```

Get environment:

```text
postman_get_environment("ENV_UID")
```

Create environment:

```text
postman_create_environment("Staging", {"API_URL":"https://api.example.com"})
```

Update environment:

```text
postman_update_environment("ENV_UID", name="Staging", values={"API_URL":"https://api.example.com"})
```

## Runs

Run a collection locally (requires Newman):

```text
postman_run_collection("COLLECTION_UID", environment_uid="ENV_UID", iterations=1)
```

Install Newman if needed:

```text
npm install -g newman
```

## APIs / Mocks / Monitors

APIs:

```text
postman_list_apis()
postman_get_api("API_ID")
postman_search_apis("payments")
```

Mocks:

```text
postman_list_mocks()
postman_get_mock("MOCK_UID")
```

Monitors:

```text
postman_list_monitors()
postman_get_monitor("MONITOR_UID")
postman_run_monitor("MONITOR_UID")
```

## Code Generation

Generate a snippet for a request:

```text
postman_generate_code_snippet("COLLECTION_UID", "Login", "curl")
postman_generate_code_snippet("COLLECTION_UID", "Login", "python-requests")
```

## Notes

- Collection updates **overwrite** the collection in Postman. Use `dry_run=true` to preview changes.
- Workspace member payloads are passed through to the Postman API. Ensure the payload matches Postman’s API requirements.
