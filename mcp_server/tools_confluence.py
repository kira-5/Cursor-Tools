"""Confluence category: spaces, pages, comments."""

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

_MCP_DIR = Path(__file__).resolve().parent
from utils import get_project_root, load_env_file

PROJECT_ROOT = get_project_root()

_CONFLUENCE_ENV_TEMPLATE = """
# Confluence often shares auth with Jira. If you set these, they override Jira settings for Confluence tools.
# CONFLUENCE_EMAIL="your_email@example.com"
# CONFLUENCE_API_TOKEN="your_confluence_api_token"
# CONFLUENCE_HOST="https://your-domain.atlassian.net"
"""

# Load mcp_server/.jira_env and .confluence_env into os.environ (sharing auth by default but allowing overrides)
# Note: Since jira is likely already loaded, we just use a blank template for jira here just in case,
# but the tools_jira.py loader has the full template.
load_env_file(".jira_env", _MCP_DIR, "")
load_env_file(".confluence_env", _MCP_DIR, _CONFLUENCE_ENV_TEMPLATE)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _get_auth_headers() -> tuple[dict, str | None]:
    email = os.environ.get("CONFLUENCE_EMAIL") or os.environ.get("JIRA_EMAIL")
    token = os.environ.get("CONFLUENCE_API_TOKEN") or os.environ.get("JIRA_API_TOKEN")
    if not email or not token:
        return {}, (
            "Missing CONFLUENCE_EMAIL/JIRA_EMAIL or "
            "CONFLUENCE_API_TOKEN/JIRA_API_TOKEN in .confluence_env or .jira_env."
        )
    encoded = base64.b64encode(f"{email}:{token}".encode()).decode()
    return {
        "Authorization": f"Basic {encoded}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }, None


def _get_host() -> tuple[str, str | None]:
    host = (os.environ.get("CONFLUENCE_HOST") or os.environ.get("JIRA_HOST", "")).rstrip("/")
    if not host:
        return "", "Missing CONFLUENCE_HOST or JIRA_HOST in .confluence_env or .jira_env."
    return host, None


def _api(method: str, path: str, body: dict | None = None, params: dict | None = None) -> tuple[bool, str]:
    """Call Confluence REST API v2. Returns (ok, json_string_or_error)."""
    host, err = _get_host()
    if err:
        return False, err
    headers, err = _get_auth_headers()
    if err:
        return False, err

    url = f"{host}/wiki/api/v2{path}"
    if params:
        query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        url = f"{url}?{query}"

    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            text = resp.read().decode("utf-8", errors="ignore")
        return True, text or "{}"
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="ignore")
        return False, f"HTTP {e.code}: {msg[:600]}"
    except Exception as e:
        return False, f"Error: {e}"


# ---------------------------------------------------------------------------
# Data trimmers
# ---------------------------------------------------------------------------


def _trim_page(page: dict) -> dict:
    host = (os.environ.get("CONFLUENCE_HOST") or os.environ.get("JIRA_HOST", "")).rstrip("/")
    body = page.get("body", {})
    storage = body.get("storage") or body.get("view") or body.get("atlas_doc_format") or {}

    # Optional parent fields if expanded

    return {
        "id": page.get("id"),
        "title": page.get("title"),
        "status": page.get("status"),
        "created": page.get("createdAt"),
        "version": (page.get("version") or {}).get("number", 1),
        "url": f"{host}/wiki{page.get('_links', {}).get('webui', '')}" if "_links" in page else "",
        "content_type": "storage/html" if "storage" in body else "adf",
        "content_length": len(storage.get("value", "")),
        "content": storage.get("value", "")[:1500] if storage.get("value") else "",  # Trimmed representation
    }


def _trim_search_result(result: dict) -> dict:
    page = result.get("content") or result
    host = (os.environ.get("CONFLUENCE_HOST") or os.environ.get("JIRA_HOST", "")).rstrip("/")
    return {
        "id": page.get("id"),
        "type": page.get("type"),
        "title": page.get("title"),
        "space": (page.get("space") or {}).get("key") or result.get("space", {}).get("key"),
        "excerpt": result.get("excerpt", "").replace("@@@hl@@@", "**").replace("@@@endhl@@@", "**"),
        "url": f"{host}/wiki{page.get('_links', {}).get('webui', '')}",
    }


# ---------------------------------------------------------------------------
# Tool registration
# ---------------------------------------------------------------------------


def register(mcp, enabled_fn):  # noqa: ANN001
    """Register Confluence tools. Disabled when 'confluence' category is off."""

    # ── READ ────────────────────────────────────────────────────────────────

    @mcp.tool()
    def confluence_get_page(page_id: str, include_content: bool = True) -> str:
        """Get full details and content of a Confluence page by its ID.
        Example: confluence_get_page('123456789')
        """
        if not enabled_fn("confluence"):
            return "Tool disabled. Add 'confluence' to CURSOR_TOOLS_ENABLED."

        params = {"body-format": "storage"} if include_content else {}
        ok, raw = _api("GET", f"/pages/{page_id}", params=params)
        if not ok:
            return raw

        data = json.loads(raw)
        trimmed = _trim_page(data)

        # If they explicitly wanted content, don't trim it
        if include_content:
            body = data.get("body", {})
            storage = body.get("storage", {})
            trimmed["content"] = storage.get("value", "")

        return json.dumps(trimmed, indent=2)

    @mcp.tool()
    def confluence_search_pages(cql: str, limit: int = 15) -> str:
        """Search Confluence using Confluence Query Language (CQL).
        Examples:
          confluence_search_pages('type=page AND text ~ "architecture"')
          confluence_search_pages('space="MTP" AND title ~ "Meeting Notes"')
        """
        if not enabled_fn("confluence"):
            return "Tool disabled. Add 'confluence' to CURSOR_TOOLS_ENABLED."

        # Confluence search is on v1 API
        host, err = _get_host()
        if err:
            return err
        headers, err = _get_auth_headers()
        if err:
            return err

        url = f"{host}/wiki/rest/api/search?cql={urllib.parse.quote(cql)}&limit={limit}"
        req = urllib.request.Request(url, method="GET", headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                text = resp.read().decode("utf-8", errors="ignore")
            data = json.loads(text or "{}")
            results = [_trim_search_result(r) for r in data.get("results", [])]
            return json.dumps({"totalSize": data.get("totalSize"), "results": results}, indent=2)
        except Exception as e:
            return f"Search error: {e}"

    # ── WRITE ───────────────────────────────────────────────────────────────

    @mcp.tool()
    def confluence_add_comment(page_id: str, comment_text: str) -> str:
        """Add a comment to a Confluence page using ADF (Atlassian Document Format).
        Wait... actually, this is simpler using the v1 API for comment creation.
        Let's use v2 API for consistency, which expects ADF format for comments.
        Example: confluence_add_comment('123456789', 'This is a great plan.')
        """
        if not enabled_fn("confluence"):
            return "Tool disabled. Add 'confluence' to CURSOR_TOOLS_ENABLED."

        body = {
            "pageId": page_id,
            "body": {
                "representation": "atlas_doc_format",
                "value": json.dumps(
                    {
                        "version": 1,
                        "type": "doc",
                        "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment_text}]}],
                    }
                ),
            },
        }

        ok, raw = _api("POST", "/footer-comments", body=body)
        if not ok:
            return raw

        data = json.loads(raw)
        return json.dumps({"comment_id": data.get("id"), "status": "Created", "pageId": page_id}, indent=2)

    @mcp.tool()
    def confluence_create_page(space_id: str, title: str, content_markdown: str, parent_id: str | None = None) -> str:
        """Create a new Confluence page in a specific space.
        Note: space_id is required. You can find it using confluence_search_pages.
        Example: confluence_create_page('12345', 'New Architecture', '<h1>Hello</h1>')
        """
        if not enabled_fn("confluence"):
            return "Tool disabled. Add 'confluence' to CURSOR_TOOLS_ENABLED."

        body = {
            "spaceId": space_id,
            "status": "current",
            "title": title,
            "body": {"representation": "storage", "value": content_markdown},
        }

        if parent_id:
            body["parentId"] = parent_id

        ok, raw = _api("POST", "/pages", body=body)
        if not ok:
            return raw

        data = json.loads(raw)
        return json.dumps(_trim_page(data), indent=2)

    @mcp.tool()
    def confluence_update_page(page_id: str, title: str, content_markdown: str, version_number: int) -> str:
        """Update an existing Confluence page.
        IMPORTANT: You must provide the exact NEXT `version_number`.
        If the page is currently on version 2, you must pass version_number=3.
        Use confluence_get_page to check the current version before updating.
        Example: confluence_update_page('123456789', 'Updated Title', '<p>New content</p>', 3)
        """
        if not enabled_fn("confluence"):
            return "Tool disabled. Add 'confluence' to CURSOR_TOOLS_ENABLED."

        body = {
            "id": page_id,
            "status": "current",
            "title": title,
            "body": {"representation": "storage", "value": content_markdown},
            "version": {"number": version_number, "message": "Updated via MCP"},
        }

        ok, raw = _api("PUT", f"/pages/{page_id}", body=body)
        if not ok:
            return raw

        data = json.loads(raw)
        return json.dumps(_trim_page(data), indent=2)
