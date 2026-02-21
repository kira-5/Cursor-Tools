"""Postman category: workspaces, collections, environments, and runs."""

import json
import os
import shutil
import ssl
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


def _build_ssl_context() -> ssl.SSLContext:
    """Build SSL context using certifi if available, else default.
    Resolves macOS 'Basic Constraints of CA cert not marked critical' error.
    Set POSTMAN_SSL_VERIFY=false in .postman_env to disable verification (last resort).
    """
    if os.environ.get("POSTMAN_SSL_VERIFY", "true").lower() == "false":
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        pass
    return ssl.create_default_context()


_MCP_DIR = Path(__file__).resolve().parent
_BASE_URL = "https://api.getpostman.com"
_DISABLED_MSG = "Tool disabled. Enable 'postman' in CURSOR_TOOLS_ENABLED."

# Name-to-local-file mapping for hybrid sync
_LOCAL_COLLECTION_MAP = {
    "BaseSmart": "BaseSmart.postman_collection.json",
    "Scratchpad": "Scratchpad.postman_collection.json",
}

# Load mcp_server/.postman_env into os.environ
_POSTMAN_ENV = _MCP_DIR / ".postman_env"
if _POSTMAN_ENV.exists():
    for line in _POSTMAN_ENV.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _get_auth_headers() -> tuple[dict, str | None]:
    """Build auth header from env. Returns (headers, error)."""
    api_key = os.environ.get("POSTMAN_API_KEY")
    if not api_key:
        return {}, "Missing POSTMAN_API_KEY."
    return {"X-Api-Key": api_key}, None


def _api_json(method: str, path: str, params: dict | None = None, body: dict | None = None):
    """Call Postman API and return (ok, data_or_error)."""
    url = f"{_BASE_URL}{path}"
    if params:
        query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        url = f"{url}?{query}"
    headers, err = _get_auth_headers()
    if err:
        return False, err
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20, context=_build_ssl_context()) as resp:
            text = resp.read().decode("utf-8", errors="ignore")
        if not text:
            return True, {}
        return True, json.loads(text)
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="ignore")
        return False, f"HTTP {e.code}: {msg[:500]}"
    except Exception as e:
        return False, f"Error: {e}"


def _require_dict(ok: bool, data: object) -> tuple[dict | None, str | None]:
    if not ok:
        return None, data if isinstance(data, str) else "Request failed."
    if not isinstance(data, dict):
        return None, "Unexpected response format."
    return data, None


def _normalize_values(values: dict | list | None) -> list:
    """Normalize env values to Postman format list."""
    if not values:
        return []
    if isinstance(values, list):
        return values
    result = []
    for k, v in values.items():
        result.append({"key": str(k), "value": str(v), "enabled": True})
    return result


def _collection_items(collection: dict) -> list:
    return (collection.get("collection") or collection).get("item", []) or []


def _split_path(path: str) -> list[str]:
    return [p for p in path.strip("/").split("/") if p]


def _ensure_folder(items: list, path_parts: list[str]) -> list:
    current = items
    for part in path_parts:
        found = None
        for item in current:
            if item.get("name") == part and "item" in item:
                found = item
                break
        if not found:
            found = {"name": part, "item": []}
            current.append(found)
        current = found["item"]
    return current


def _find_item_by_path(items: list, path_parts: list[str]) -> tuple[list | None, dict | None]:
    if not path_parts:
        return None, None
    current = items
    for part in path_parts[:-1]:
        next_folder = None
        for item in current:
            if item.get("name") == part and "item" in item:
                next_folder = item
                break
        if not next_folder:
            return None, None
        current = next_folder.get("item", [])
    target_name = path_parts[-1]
    for item in current:
        if item.get("name") == target_name:
            return current, item
    return current, None


def _headers_to_list(headers: dict | None) -> list:
    if not headers:
        return []
    return [{"key": k, "value": v} for k, v in headers.items()]


def _build_request(
    method: str,
    url: str,
    headers: dict | None = None,
    body: str | dict | list | None = None,
    description: str | None = None,
) -> dict:
    request: dict[str, Any] = {"method": method.upper(), "url": url}
    if headers:
        request["header"] = _headers_to_list(headers)
    if description:
        request["description"] = description
    if body is not None:
        if isinstance(body, (dict, list)):
            body = json.dumps(body)
        request["body"] = {"mode": "raw", "raw": body}
    return request


# ---------------------------------------------------------------------------
# Hybrid Sync Helpers
# Detect and update local collection files, then run update_postman.sh.
# Falls back silently if local project structure is absent (e.g. on team machines).
# ---------------------------------------------------------------------------


def _find_local_collection(collection_name: str) -> Path | None:
    """Try to resolve a local postman collection JSON file by name.
    Searches upward from cwd for `postman/collections/<file>`."""
    filename = _LOCAL_COLLECTION_MAP.get(collection_name)
    if not filename:
        return None
    cwd = Path.cwd()
    # Search cwd and up to 4 parent directories
    for candidate in [cwd, *cwd.parents[:4]]:
        path = candidate / "postman" / "collections" / filename
        if path.exists():
            return path
    return None


def _collection_name_from_uid(collection_uid: str) -> str | None:
    """Fetch the collection name from Postman Cloud by uid."""
    ok, data = _api_json("GET", f"/collections/{collection_uid}")
    if not ok or not isinstance(data, dict):
        return None
    info = (data.get("collection") or {}).get("info") or {}
    return info.get("name")


def _run_update_script(project_root: Path) -> str:
    """Run update_postman.sh to sync local → cloud."""
    script = project_root / "postman" / "scripts" / "update_postman.sh"
    if not script.exists():
        return "(local sync script not found, cloud sync skipped)"
    try:
        proc = subprocess.run(
            ["bash", str(script)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(project_root),
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        return out[-1000:] if out else "(no output)"
    except Exception as e:
        return f"(sync script error: {e})"


def _local_add_request(
    collection_name: str,
    request_path: str,
    method: str,
    url: str,
    headers: dict | None = None,
    body: str | dict | list | None = None,
    description: str | None = None,
) -> tuple[bool, str]:
    """Add a request to a local collection JSON. Returns (success, message)."""
    local_path = _find_local_collection(collection_name)
    if not local_path:
        return False, f"No local file found for '{collection_name}'."
    try:
        raw = local_path.read_text(encoding="utf-8")
        data = json.loads(raw)
        collection = data.get("collection") or data
        items = collection.get("item") or []
        parts = _split_path(request_path)
        if not parts:
            return False, "request_path is required."
        parent_items = _ensure_folder(items, parts[:-1])
        request_item = {
            "name": parts[-1],
            "request": _build_request(method, url, headers=headers, body=body, description=description),
            "response": [],
        }
        parent_items.append(request_item)
        collection["item"] = items
        if "collection" in data:
            data["collection"] = collection
        local_path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
        # Trigger cloud sync
        sync_out = _run_update_script(local_path.parent.parent.parent)
        return (
            True,
            f"✅ Local file updated at {local_path}.\n📡 Cloud sync:\n{sync_out}",
        )
    except Exception as e:
        return False, f"Local update failed: {e}"


def _local_update_request(
    collection_name: str,
    request_path: str,
    method: str | None = None,
    url: str | None = None,
    headers: dict | None = None,
    body: str | dict | list | None = None,
    description: str | None = None,
    rename_to: str | None = None,
) -> tuple[bool, str]:
    """Update a request in a local collection JSON. Returns (success, message)."""
    local_path = _find_local_collection(collection_name)
    if not local_path:
        return False, f"No local file found for '{collection_name}'."
    try:
        raw = local_path.read_text(encoding="utf-8")
        data = json.loads(raw)
        collection = data.get("collection") or data
        items = collection.get("item") or []
        _parent, item = _find_item_by_path(items, _split_path(request_path))
        if not item or "request" not in item:
            return False, "Request not found in local file."
        req = item.get("request") or {}
        if method:
            req["method"] = method.upper()
        if url:
            req["url"] = url
        if headers is not None:
            req["header"] = _headers_to_list(headers)
        if description is not None:
            req["description"] = description
        if body is not None:
            if isinstance(body, (dict, list)):
                body = json.dumps(body)
            req["body"] = {"mode": "raw", "raw": body}
        item["request"] = req
        if rename_to:
            item["name"] = rename_to
        collection["item"] = items
        if "collection" in data:
            data["collection"] = collection
        local_path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
        sync_out = _run_update_script(local_path.parent.parent.parent)
        return (
            True,
            f"✅ Local file updated at {local_path}.\n📡 Cloud sync:\n{sync_out}",
        )
    except Exception as e:
        return False, f"Local update failed: {e}"


# ---------------------------------------------------------------------------


def _snapshot_paths(items: list) -> list[str]:
    snapshot = []
    for entry in _walk_items(items):
        item_type = entry.get("type", "item")
        path = entry.get("path", "")
        snapshot.append(f"{item_type}:{path}")
    return sorted(snapshot)


def _diff_paths(before: list[str], after: list[str]) -> dict:
    before_set = set(before)
    after_set = set(after)
    return {
        "added": sorted(after_set - before_set),
        "removed": sorted(before_set - after_set),
    }


def _dry_run_summary(before_items: list, after_items: list, note: str | None = None) -> str:
    diff = _diff_paths(_snapshot_paths(before_items), _snapshot_paths(after_items))
    payload: dict[str, Any] = {"diff": diff}
    if note:
        payload["note"] = note
    return json.dumps(payload, indent=2)


def _walk_items(items: list, parent_path: str = "") -> list:
    results = []
    for item in items:
        name = item.get("name") or ""
        path = f"{parent_path}/{name}" if parent_path else name
        if "item" in item:
            results.append(
                {
                    "type": "folder",
                    "name": name,
                    "path": path,
                    "id": item.get("id"),
                }
            )
            results.extend(_walk_items(item.get("item", []), path))
        else:
            results.append(
                {
                    "type": "request",
                    "name": name,
                    "path": path,
                    "id": item.get("id"),
                    "request": item.get("request"),
                }
            )
    return results


def _find_items(items: list, query: str, case_sensitive: bool = False) -> list:
    if not case_sensitive:
        query = query.lower()
    matches = []
    for entry in _walk_items(items):
        name = entry.get("name", "")
        haystack = name if case_sensitive else name.lower()
        if query in haystack:
            matches.append(entry)
    return matches


def _pick_item(items: list, name: str, case_sensitive: bool = False) -> dict | None:
    matches = _find_items(items, name, case_sensitive=case_sensitive)
    for entry in matches:
        if (entry.get("name") == name) or (not case_sensitive and entry.get("name", "").lower() == name.lower()):
            return entry
    return matches[:1][0] if matches else None


def _request_url(request: dict | None) -> str:
    if not request:
        return ""
    url = request.get("url")
    if isinstance(url, str):
        return url
    if isinstance(url, dict):
        return url.get("raw") or ""
    return ""


def _request_headers(request: dict | None) -> dict:
    headers = {}
    if not request:
        return headers
    for h in request.get("header", []) or []:
        if h.get("disabled"):
            continue
        k = h.get("key")
        v = h.get("value")
        if k:
            headers[k] = v if v is not None else ""
    return headers


def _request_body(request: dict | None) -> tuple[str | None, dict | None]:
    if not request:
        return None, None
    body = request.get("body") or {}
    mode = body.get("mode")
    if mode == "raw":
        return body.get("raw"), None
    if mode == "urlencoded":
        data = {item.get("key"): item.get("value") for item in body.get("urlencoded", []) or []}
        return None, data
    if mode == "formdata":
        data = {item.get("key"): item.get("value") for item in body.get("formdata", []) or []}
        return None, data
    return None, None


def _format_curl(method: str, url: str, headers: dict, raw_body: str | None, data_body: dict | None) -> str:
    parts = [f"curl -X {method.upper()} '{url}'"]
    for k, v in headers.items():
        parts.append(f"-H '{k}: {v}'")
    if raw_body:
        parts.append(f"--data-raw '{raw_body}'")
    elif data_body:
        parts.append(f"--data '{json.dumps(data_body)}'")
    return " \\\n  ".join(parts)


def _format_python_requests(method: str, url: str, headers: dict, raw_body: str | None, data_body: dict | None) -> str:
    lines = ["import requests", "", f"url = {json.dumps(url)}"]
    if headers:
        lines.append(f"headers = {json.dumps(headers, indent=2)}")
    else:
        lines.append("headers = {}")
    if raw_body:
        lines.append(f"data = {json.dumps(raw_body)}")
        lines.append(f"resp = requests.request('{method.upper()}', url, headers=headers, data=data)")
    elif data_body:
        lines.append(f"data = {json.dumps(data_body, indent=2)}")
        lines.append(f"resp = requests.request('{method.upper()}', url, headers=headers, data=data)")
    else:
        lines.append(f"resp = requests.request('{method.upper()}', url, headers=headers)")
    lines.append("print(resp.status_code)")
    lines.append("print(resp.text)")
    return "\n".join(lines)


def _run_newman(collection: dict, environment: dict | None, iterations: int, timeout_ms: int) -> str:
    newman_path = shutil.which("newman")
    if not newman_path:
        return "Newman is not installed. Install with: npm install -g newman"
    with tempfile.TemporaryDirectory() as tmpdir:
        collection_path = Path(tmpdir) / "collection.json"
        collection_path.write_text(json.dumps(collection))
        cmd = [newman_path, "run", str(collection_path)]
        if environment:
            env_path = Path(tmpdir) / "environment.json"
            env_path.write_text(json.dumps(environment))
            cmd += ["-e", str(env_path)]
        if iterations and iterations > 1:
            cmd += ["-n", str(iterations)]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_ms / 1000)
        except subprocess.TimeoutExpired:
            return f"Newman run timed out after {timeout_ms}ms."
        output = (proc.stdout or "") + "\n" + (proc.stderr or "")
        return output[-4000:] if output else "Newman run completed with no output."


def register(mcp, enabled_fn):
    """Register Postman tools. Disabled when 'postman' category is off."""

    @mcp.tool()
    def postman_list_workspaces() -> str:
        """List Postman workspaces."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", "/workspaces")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        return json.dumps(data.get("workspaces", []), indent=2)

    @mcp.tool()
    def postman_get_workspace(workspace_id: str) -> str:
        """Get a Postman workspace by id."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", f"/workspaces/{workspace_id}")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        return json.dumps(data, indent=2)

    @mcp.tool()
    def postman_create_workspace(
        name: str,
        workspace_type: str = "team",
        description: str | None = None,
    ) -> str:
        """Create a Postman workspace."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        workspace = {"name": name, "type": workspace_type}
        if description:
            workspace["description"] = description
        ok, data = _api_json("POST", "/workspaces", body={"workspace": workspace})
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        return json.dumps(data, indent=2)

    @mcp.tool()
    def postman_update_workspace(
        workspace_id: str,
        name: str | None = None,
        description: str | None = None,
    ) -> str:
        """Update a Postman workspace."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        workspace: dict[str, Any] = {}
        if name:
            workspace["name"] = name
        if description is not None:
            workspace["description"] = description
        if not workspace:
            return "No updates provided."
        ok, data = _api_json("PUT", f"/workspaces/{workspace_id}", body={"workspace": workspace})
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        return json.dumps(data, indent=2)

    @mcp.tool()
    def postman_delete_workspace(workspace_id: str) -> str:
        """Delete a Postman workspace."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("DELETE", f"/workspaces/{workspace_id}")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        return json.dumps(data, indent=2)

    @mcp.tool()
    def postman_list_workspace_members(workspace_id: str) -> str:
        """List members in a Postman workspace."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", f"/workspaces/{workspace_id}/members")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        return json.dumps(data, indent=2)

    @mcp.tool()
    def postman_add_workspace_members(
        workspace_id: str,
        members_payload: dict,
    ) -> str:
        """Add members to a Postman workspace. Payload is passed through to the API."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("POST", f"/workspaces/{workspace_id}/members", body=members_payload)
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        return json.dumps(data, indent=2)

    @mcp.tool()
    def postman_remove_workspace_member(
        workspace_id: str,
        member_id: str,
    ) -> str:
        """Remove a member from a Postman workspace by member id."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("DELETE", f"/workspaces/{workspace_id}/members/{member_id}")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        return json.dumps(data, indent=2)

    @mcp.tool()
    def postman_list_collections() -> str:
        """List Postman collections."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", "/collections")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        return json.dumps(data.get("collections", []), indent=2)

    @mcp.tool()
    def postman_get_collection(uid: str) -> str:
        """Get a Postman collection by uid."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", f"/collections/{uid}")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        return json.dumps(data, indent=2)

    @mcp.tool()
    def postman_create_collection(
        name: str,
        description: str | None = None,
        items: list | None = None,
        workspace_id: str | None = None,
    ) -> str:
        """Create a Postman collection."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        info = {
            "name": name,
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        }
        if description:
            info["description"] = description
        payload = {"collection": {"info": info, "item": items or []}}
        ok, data = _api_json("POST", "/collections", params={"workspace": workspace_id}, body=payload)
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        return json.dumps(data, indent=2)

    @mcp.tool()
    def postman_update_collection(
        collection_uid: str,
        name: str | None = None,
        description: str | None = None,
    ) -> str:
        """Update a Postman collection's metadata."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", f"/collections/{collection_uid}")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        collection = data.get("collection")
        if not isinstance(collection, dict):
            return "Collection not found."
        info = collection.get("info") or {}
        if name:
            info["name"] = name
        if description is not None:
            info["description"] = description
        collection["info"] = info
        ok, updated = _api_json("PUT", f"/collections/{collection_uid}", body={"collection": collection})
        updated, err = _require_dict(ok, updated)
        if err:
            return err
        assert updated is not None
        return json.dumps(updated, indent=2)

    @mcp.tool()
    def postman_delete_collection(collection_uid: str) -> str:
        """Delete a Postman collection by uid."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("DELETE", f"/collections/{collection_uid}")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        return json.dumps(data, indent=2)

    @mcp.tool()
    def postman_list_environments() -> str:
        """List Postman environments."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", "/environments")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        return json.dumps(data.get("environments", []), indent=2)

    @mcp.tool()
    def postman_get_environment(uid: str) -> str:
        """Get a Postman environment by uid."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", f"/environments/{uid}")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        return json.dumps(data, indent=2)

    @mcp.tool()
    def postman_create_environment(
        name: str,
        values: dict | list | None = None,
        workspace_id: str | None = None,
    ) -> str:
        """Create a Postman environment."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        payload = {"environment": {"name": name, "values": _normalize_values(values)}}
        ok, data = _api_json("POST", "/environments", params={"workspace": workspace_id}, body=payload)
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        return json.dumps(data, indent=2)

    @mcp.tool()
    def postman_update_environment(
        uid: str,
        name: str | None = None,
        values: dict | list | None = None,
    ) -> str:
        """Update a Postman environment by uid."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        env: dict[str, Any] = {"values": _normalize_values(values)}
        if name:
            env["name"] = name
        payload = {"environment": env}
        ok, data = _api_json("PUT", f"/environments/{uid}", body=payload)
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        return json.dumps(data, indent=2)

    @mcp.tool()
    def postman_search_collection_items(
        collection_uid: str,
        query: str,
        case_sensitive: bool = False,
    ) -> str:
        """Search requests/folders by name within a collection."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", f"/collections/{collection_uid}")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        items = _collection_items(data)
        matches = _find_items(items, query, case_sensitive=case_sensitive)
        trimmed = [{k: v for k, v in m.items() if k in {"type", "name", "path", "id"}} for m in matches]
        return json.dumps(trimmed, indent=2)

    @mcp.tool()
    def postman_get_collection_item(
        collection_uid: str,
        item_name: str,
        case_sensitive: bool = False,
    ) -> str:
        """Get a specific request or folder in a collection by name."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", f"/collections/{collection_uid}")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        items = _collection_items(data)
        item = _pick_item(items, item_name, case_sensitive=case_sensitive)
        if not item:
            return "Item not found."
        return json.dumps(item, indent=2)

    @mcp.tool()
    def postman_add_folder(
        collection_uid: str,
        folder_path: str,
        dry_run: bool = False,
    ) -> str:
        """Add a folder (and parents) to a collection."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", f"/collections/{collection_uid}")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        collection = data.get("collection")
        if not isinstance(collection, dict):
            return "Collection not found."
        items = collection.get("item") or []
        before = json.loads(json.dumps(items))
        _ensure_folder(items, _split_path(folder_path))
        if dry_run:
            return _dry_run_summary(before, items, note="Dry-run only. No changes saved.")
        collection["item"] = items
        ok, updated = _api_json("PUT", f"/collections/{collection_uid}", body={"collection": collection})
        updated, err = _require_dict(ok, updated)
        if err:
            return err
        assert updated is not None
        return json.dumps(updated, indent=2)

    @mcp.tool()
    def postman_add_request(
        collection_uid: str,
        request_path: str,
        method: str,
        url: str,
        headers: dict | None = None,
        body: str | dict | list | None = None,
        description: str | None = None,
        dry_run: bool = False,
    ) -> str:
        """Add a request to a collection at the given path.

        🔄 HYBRID SYNC: If a local Postman project exists (postman/collections/),
        this tool will update the local JSON file AND push to Postman Cloud.
        On machines without a local project (e.g. team members), it falls back
        to cloud-only mode.
        """
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", f"/collections/{collection_uid}")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        collection = data.get("collection")
        if not isinstance(collection, dict):
            return "Collection not found."
        parts = _split_path(request_path)
        if not parts:
            return "request_path is required."
        items = collection.get("item") or []
        before = json.loads(json.dumps(items))
        parent_items = _ensure_folder(items, parts[:-1])
        request_item = {
            "name": parts[-1],
            "request": _build_request(method, url, headers=headers, body=body, description=description),
            "response": [],
        }
        parent_items.append(request_item)
        collection["item"] = items
        if dry_run:
            return _dry_run_summary(before, items, note="Dry-run only. No changes saved.")

        # 🔄 HYBRID SYNC: Try local-first approach
        collection_name = (collection.get("info") or {}).get("name", "")
        local_ok, local_msg = _local_add_request(
            collection_name,
            request_path,
            method,
            url,
            headers=headers,
            body=body,
            description=description,
        )
        if local_ok:
            return f"🔄 Hybrid Sync completed.\n{local_msg}"

        # Fallback: Cloud-only (for team members without local project)
        ok, updated = _api_json("PUT", f"/collections/{collection_uid}", body={"collection": collection})
        updated, err = _require_dict(ok, updated)
        if err:
            return err
        assert updated is not None
        return json.dumps(updated, indent=2)

    @mcp.tool()
    def postman_update_request(
        collection_uid: str,
        request_path: str,
        method: str | None = None,
        url: str | None = None,
        headers: dict | None = None,
        body: str | dict | list | None = None,
        description: str | None = None,
        rename_to: str | None = None,
        dry_run: bool = False,
    ) -> str:
        """Update a request in a collection by path.

        🔄 HYBRID SYNC: If a local Postman project exists (postman/collections/),
        this tool will update the local JSON file AND push to Postman Cloud.
        On machines without a local project (e.g. team members), it falls back
        to cloud-only mode.
        """
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", f"/collections/{collection_uid}")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        collection = data.get("collection")
        if not isinstance(collection, dict):
            return "Collection not found."
        items = collection.get("item") or []
        before = json.loads(json.dumps(items))
        _parent, item = _find_item_by_path(items, _split_path(request_path))
        if not item or "request" not in item:
            return "Request not found."
        req = item.get("request") or {}
        if method:
            req["method"] = method.upper()
        if url:
            req["url"] = url
        if headers is not None:
            req["header"] = _headers_to_list(headers)
        if description is not None:
            req["description"] = description
        if body is not None:
            if isinstance(body, (dict, list)):
                body = json.dumps(body)
            req["body"] = {"mode": "raw", "raw": body}
        item["request"] = req
        if rename_to:
            item["name"] = rename_to
        collection["item"] = items
        if dry_run:
            note = "Dry-run only. No changes saved."
            if rename_to:
                note = f"{note} Request will be renamed to {rename_to}."
            return _dry_run_summary(before, items, note=note)

        # 🔄 HYBRID SYNC: Try local-first approach
        collection_name = (collection.get("info") or {}).get("name", "")
        local_ok, local_msg = _local_update_request(
            collection_name,
            request_path,
            method=method,
            url=url,
            headers=headers,
            body=body,
            description=description,
            rename_to=rename_to,
        )
        if local_ok:
            return f"🔄 Hybrid Sync completed.\n{local_msg}"

        # Fallback: Cloud-only (for team members without local project)
        ok, updated = _api_json("PUT", f"/collections/{collection_uid}", body={"collection": collection})
        updated, err = _require_dict(ok, updated)
        if err:
            return err
        assert updated is not None
        return json.dumps(updated, indent=2)

    @mcp.tool()
    def postman_delete_item(
        collection_uid: str,
        item_path: str,
        dry_run: bool = False,
    ) -> str:
        """Delete a request or folder from a collection by path."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", f"/collections/{collection_uid}")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        collection = data.get("collection")
        if not isinstance(collection, dict):
            return "Collection not found."
        items = collection.get("item") or []
        before = json.loads(json.dumps(items))
        parent, item = _find_item_by_path(items, _split_path(item_path))
        if parent is None:
            return "Item not found."
        if item in parent:
            parent.remove(item)
        collection["item"] = items
        if dry_run:
            return _dry_run_summary(before, items, note="Dry-run only. No changes saved.")
        ok, updated = _api_json("PUT", f"/collections/{collection_uid}", body={"collection": collection})
        updated, err = _require_dict(ok, updated)
        if err:
            return err
        assert updated is not None
        return json.dumps(updated, indent=2)

    @mcp.tool()
    def postman_rename_folder(
        collection_uid: str,
        folder_path: str,
        rename_to: str,
        dry_run: bool = False,
    ) -> str:
        """Rename a folder in a collection by path."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", f"/collections/{collection_uid}")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        collection = data.get("collection")
        if not isinstance(collection, dict):
            return "Collection not found."
        items = collection.get("item") or []
        before = json.loads(json.dumps(items))
        _parent, item = _find_item_by_path(items, _split_path(folder_path))
        if not item or "item" not in item:
            return "Folder not found."
        item["name"] = rename_to
        collection["item"] = items
        if dry_run:
            return _dry_run_summary(
                before,
                items,
                note=f"Dry-run only. Folder will be renamed to {rename_to}.",
            )
        ok, updated = _api_json("PUT", f"/collections/{collection_uid}", body={"collection": collection})
        updated, err = _require_dict(ok, updated)
        if err:
            return err
        assert updated is not None
        return json.dumps(updated, indent=2)

    @mcp.tool()
    def postman_delete_folder(
        collection_uid: str,
        folder_path: str,
        dry_run: bool = False,
    ) -> str:
        """Delete a folder from a collection by path."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        return postman_delete_item(collection_uid, folder_path, dry_run=dry_run)

    @mcp.tool()
    def postman_run_collection(
        collection_uid: str,
        environment_uid: str | None = None,
        iterations: int = 1,
        timeout_ms: int = 600000,
    ) -> str:
        """Run a collection locally with Newman (if installed)."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", f"/collections/{collection_uid}")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        collection = data.get("collection") or data
        environment = None
        if environment_uid:
            ok, env = _api_json("GET", f"/environments/{environment_uid}")
            env, env_err = _require_dict(ok, env)
            if env_err:
                return env_err
            assert env is not None
            environment = env.get("environment") or env
        return _run_newman(collection, environment, iterations, timeout_ms)

    @mcp.tool()
    def postman_list_apis() -> str:
        """List Postman API definitions."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", "/apis")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        return json.dumps(data.get("apis", []), indent=2)

    @mcp.tool()
    def postman_get_api(api_id: str) -> str:
        """Get a Postman API definition by id."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", f"/apis/{api_id}")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        return json.dumps(data, indent=2)

    @mcp.tool()
    def postman_search_apis(query: str, case_sensitive: bool = False) -> str:
        """Search Postman APIs by name."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", "/apis")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        apis = data.get("apis", [])
        if not case_sensitive:
            query_l = query.lower()
            apis = [a for a in apis if query_l in (a.get("name", "").lower())]
        else:
            apis = [a for a in apis if query in (a.get("name", ""))]
        return json.dumps(apis, indent=2)

    @mcp.tool()
    def postman_list_mocks() -> str:
        """List Postman mocks."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", "/mocks")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        return json.dumps(data.get("mocks", []), indent=2)

    @mcp.tool()
    def postman_get_mock(uid: str) -> str:
        """Get a Postman mock by uid."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", f"/mocks/{uid}")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        return json.dumps(data, indent=2)

    @mcp.tool()
    def postman_list_monitors() -> str:
        """List Postman monitors."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", "/monitors")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        return json.dumps(data.get("monitors", []), indent=2)

    @mcp.tool()
    def postman_get_monitor(uid: str) -> str:
        """Get a Postman monitor by uid."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", f"/monitors/{uid}")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        return json.dumps(data, indent=2)

    @mcp.tool()
    def postman_run_monitor(uid: str) -> str:
        """Trigger a Postman monitor run."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("POST", f"/monitors/{uid}/run")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        return json.dumps(data, indent=2)

    @mcp.tool()
    def postman_generate_code_snippet(
        collection_uid: str,
        item_name: str,
        language: str = "curl",
    ) -> str:
        """Generate a simple code snippet for a collection item."""
        if not enabled_fn("postman"):
            return _DISABLED_MSG
        ok, data = _api_json("GET", f"/collections/{collection_uid}")
        data, err = _require_dict(ok, data)
        if err:
            return err
        assert data is not None
        items = _collection_items(data)
        item = _pick_item(items, item_name, case_sensitive=False)
        if not item or item.get("type") != "request":
            return "Request not found."
        req = item.get("request") or {}
        method = req.get("method") or "GET"
        url = _request_url(req)
        headers = _request_headers(req)
        raw_body, data_body = _request_body(req)
        lang = language.lower()
        if lang in {"curl"}:
            return _format_curl(method, url, headers, raw_body, data_body)
        if lang in {"python", "python-requests", "requests"}:
            return _format_python_requests(method, url, headers, raw_body, data_body)
        return "Unsupported language. Use 'curl' or 'python-requests'."
