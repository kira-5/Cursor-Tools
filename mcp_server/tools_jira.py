"""Jira category: projects, sprints, issues, comments, transitions, links."""

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

_JIRA_ENV_TEMPLATE = """
JIRA_EMAIL="your_email@example.com"
JIRA_API_TOKEN="your_jira_api_token"
JIRA_HOST="https://your-domain.atlassian.net"
JIRA_DEFAULT_PROJECT="PROJ"  # Optional: Default project key for new issues
"""

# Load mcp_server/.jira_env into os.environ
load_env_file(".jira_env", _MCP_DIR, _JIRA_ENV_TEMPLATE)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _get_auth_headers() -> tuple[dict, str | None]:
    email = os.environ.get("JIRA_EMAIL")
    token = os.environ.get("JIRA_API_TOKEN")
    if not email or not token:
        return {}, "Missing JIRA_EMAIL or JIRA_API_TOKEN in .jira_env."
    encoded = base64.b64encode(f"{email}:{token}".encode()).decode()
    return {
        "Authorization": f"Basic {encoded}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }, None


def _get_host() -> tuple[str, str | None]:
    host = os.environ.get("JIRA_HOST", "").rstrip("/")
    if not host:
        return "", "Missing JIRA_HOST in .jira_env."
    return host, None


def _api(method: str, path: str, body: dict | None = None, params: dict | None = None) -> tuple[bool, str]:
    """Call Jira REST API v3. Returns (ok, json_string_or_error)."""
    host, err = _get_host()
    if err:
        return False, err
    headers, err = _get_auth_headers()
    if err:
        return False, err

    url = f"{host}/rest/api/3{path}"
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


def _agile_api(method: str, path: str, params: dict | None = None) -> tuple[bool, str]:
    """Call Jira Agile API. Returns (ok, json_string_or_error)."""
    host, err = _get_host()
    if err:
        return False, err
    headers, err = _get_auth_headers()
    if err:
        return False, err

    url = f"{host}/rest/agile/1.0{path}"
    if params:
        query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        url = f"{url}?{query}"

    req = urllib.request.Request(url, method=method, headers=headers)
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


def _extract_adf_text(node: dict | None) -> str:
    """Recursively extract plain text from Atlassian Document Format (ADF)."""
    if not node:
        return ""
    if node.get("type") == "text":
        return node.get("text", "")
    parts = [_extract_adf_text(child) for child in node.get("content") or []]
    return " ".join(p for p in parts if p)


def _trim_issue(issue: dict) -> dict:
    fields = issue.get("fields") or {}
    assignee = fields.get("assignee") or {}
    reporter = fields.get("reporter") or {}
    status = fields.get("status") or {}
    priority = fields.get("priority") or {}
    issue_type = fields.get("issuetype") or {}
    labels = fields.get("labels") or []
    raw_desc = fields.get("description")
    desc_text = _extract_adf_text(raw_desc) if isinstance(raw_desc, dict) else (raw_desc or "")
    host = os.environ.get("JIRA_HOST", "").rstrip("/")
    return {
        "key": issue.get("key"),
        "id": issue.get("id"),
        "summary": fields.get("summary"),
        "status": status.get("name"),
        "type": issue_type.get("name"),
        "priority": priority.get("name"),
        "assignee": assignee.get("displayName"),
        "reporter": reporter.get("displayName"),
        "labels": labels,
        "description": desc_text[:500] if desc_text else "",
        "url": f"{host}/browse/{issue.get('key')}",
    }


def _trim_project(proj: dict) -> dict:
    return {
        "key": proj.get("key"),
        "id": proj.get("id"),
        "name": proj.get("name"),
        "type": proj.get("projectTypeKey"),
        "style": proj.get("style"),
    }


def _trim_sprint(sprint: dict) -> dict:
    return {
        "id": sprint.get("id"),
        "name": sprint.get("name"),
        "state": sprint.get("state"),
        "start": sprint.get("startDate"),
        "end": sprint.get("endDate"),
        "goal": sprint.get("goal"),
    }


# ---------------------------------------------------------------------------
# Tool registration
# ---------------------------------------------------------------------------


def register(mcp, enabled_fn):  # noqa: ANN001
    """Register Jira tools. Disabled when 'jira' category is off."""

    # ── READ ────────────────────────────────────────────────────────────────

    @mcp.tool()
    def jira_get_issue(issue_key: str) -> str:
        """Get full details of a Jira ticket (status, assignee, description, labels, etc.).
        Example: jira_get_issue('MTP-1234')
        """
        if not enabled_fn("jira"):
            return "Tool disabled. Add 'jira' to CURSOR_TOOLS_ENABLED."
        ok, raw = _api("GET", f"/issue/{issue_key}")
        if not ok:
            return raw
        return json.dumps(_trim_issue(json.loads(raw)), indent=2)

    @mcp.tool()
    def jira_search_issues(
        jql: str,
        max_results: int = 25,
        fields: str | None = None,
    ) -> str:
        """Search Jira issues using JQL.
        Examples:
          jira_search_issues('project = MTP AND status = "In Progress"')
          jira_search_issues('assignee = currentUser() AND sprint in openSprints()')
        """
        if not enabled_fn("jira"):
            return "Tool disabled. Add 'jira' to CURSOR_TOOLS_ENABLED."
        field_list = (
            fields.split(",")
            if fields
            else [
                "summary",
                "status",
                "assignee",
                "reporter",
                "priority",
                "issuetype",
                "labels",
                "description",
            ]
        )
        body: dict = {"jql": jql, "maxResults": max_results, "fields": field_list}
        ok, raw = _api("POST", "/search/jql", body=body)
        if not ok:
            return raw
        data = json.loads(raw)
        issues = [_trim_issue(i) for i in data.get("issues", [])]
        return json.dumps({"total": data.get("total"), "issues": issues}, indent=2)

    @mcp.tool()
    def jira_list_projects(max_results: int = 50) -> str:
        """List all Jira projects accessible to the configured account."""
        if not enabled_fn("jira"):
            return "Tool disabled. Add 'jira' to CURSOR_TOOLS_ENABLED."
        ok, raw = _api("GET", "/project/search", params={"maxResults": max_results})
        if not ok:
            return raw
        data = json.loads(raw)
        return json.dumps([_trim_project(p) for p in data.get("values", [])], indent=2)

    @mcp.tool()
    def jira_get_project(project_key: str) -> str:
        """Get details of a specific Jira project.
        Example: jira_get_project('MTP')
        """
        if not enabled_fn("jira"):
            return "Tool disabled. Add 'jira' to CURSOR_TOOLS_ENABLED."
        ok, raw = _api("GET", f"/project/{project_key}")
        if not ok:
            return raw
        return json.dumps(_trim_project(json.loads(raw)), indent=2)

    @mcp.tool()
    def jira_list_sprints(board_id: int, state: str | None = None) -> str:
        """List sprints for a Jira Software board.
        state: 'active' | 'future' | 'closed' (omit for all)
        Example: jira_list_sprints(42, state='active')
        """
        if not enabled_fn("jira"):
            return "Tool disabled. Add 'jira' to CURSOR_TOOLS_ENABLED."
        params: dict = {"maxResults": 50}
        if state:
            params["state"] = state
        ok, raw = _agile_api("GET", f"/board/{board_id}/sprint", params=params)
        if not ok:
            return raw
        data = json.loads(raw)
        return json.dumps([_trim_sprint(s) for s in data.get("values", [])], indent=2)

    @mcp.tool()
    def jira_get_sprint_issues(board_id: int, sprint_id: int, max_results: int = 50) -> str:
        """Get all issues in a specific sprint.
        Example: jira_get_sprint_issues(42, 101)
        """
        if not enabled_fn("jira"):
            return "Tool disabled. Add 'jira' to CURSOR_TOOLS_ENABLED."
        ok, raw = _agile_api(
            "GET",
            f"/board/{board_id}/sprint/{sprint_id}/issue",
            params={"maxResults": max_results},
        )
        if not ok:
            return raw
        data = json.loads(raw)
        issues = [_trim_issue(i) for i in data.get("issues", [])]
        return json.dumps({"total": data.get("total"), "issues": issues}, indent=2)

    # ── WRITE ───────────────────────────────────────────────────────────────

    @mcp.tool()
    def jira_create_issue(
        summary: str,
        issue_type: str = "Task",
        project_key: str | None = None,
        description: str | None = None,
        assignee_account_id: str | None = None,
        priority: str | None = None,
        labels: str | None = None,
        components: str | None = None,
    ) -> str:
        """Create a new Jira issue (Bug, Story, Task, Sub-task, Epic, etc.).
        project_key defaults to JIRA_DEFAULT_PROJECT from .jira_env.
        labels: comma-separated string e.g. 'backend,urgent'
        components: comma-separated string e.g. 'PriceSmart-BasePricing'
        Example: jira_create_issue('Fix login bug', issue_type='Bug', project_key='MTP')
        """
        if not enabled_fn("jira"):
            return "Tool disabled. Add 'jira' to CURSOR_TOOLS_ENABLED."
        proj = project_key or os.environ.get("JIRA_DEFAULT_PROJECT", "")
        if not proj:
            return "project_key is required (or set JIRA_DEFAULT_PROJECT in .jira_env)."
        comps = components or os.environ.get("JIRA_DEFAULT_COMPONENTS")
        fields: dict = {
            "project": {"key": proj},
            "summary": summary,
            "issuetype": {"name": issue_type},
        }
        if description:
            fields["description"] = {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}],
            }
        if assignee_account_id:
            fields["assignee"] = {"accountId": assignee_account_id}
        if priority:
            fields["priority"] = {"name": priority}
        if labels:
            fields["labels"] = [lbl.strip() for lbl in labels.split(",")]
        if comps:
            fields["components"] = [{"name": c.strip()} for c in comps.split(",")]
        ok, raw = _api("POST", "/issue", body={"fields": fields})
        if not ok:
            return raw
        data = json.loads(raw)
        key = data.get("key", "")
        host = os.environ.get("JIRA_HOST", "").rstrip("/")
        return json.dumps({"key": key, "url": f"{host}/browse/{key}"}, indent=2)

    @mcp.tool()
    def jira_update_issue(
        issue_key: str,
        summary: str | None = None,
        description: str | None = None,
        priority: str | None = None,
        labels: str | None = None,
        components: str | None = None,
        assignee_account_id: str | None = None,
    ) -> str:
        """Update fields on an existing Jira issue. Only supplied fields are changed.
        labels: comma-separated string e.g. 'backend,urgent'
        components: comma-separated string e.g. 'PriceSmart-BasePricing'
        Example: jira_update_issue('MTP-1234', priority='High', labels='backend')
        """
        if not enabled_fn("jira"):
            return "Tool disabled. Add 'jira' to CURSOR_TOOLS_ENABLED."
        fields: dict = {}
        if summary:
            fields["summary"] = summary
        if description:
            fields["description"] = {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}],
            }
        if priority:
            fields["priority"] = {"name": priority}
        if labels is not None:
            fields["labels"] = [lbl.strip() for lbl in labels.split(",") if lbl.strip()]
        if components is not None:
            fields["components"] = [{"name": c.strip()} for c in components.split(",") if c.strip()]
        if assignee_account_id:
            fields["assignee"] = {"accountId": assignee_account_id}
        if not fields:
            return "No fields provided to update."
        ok, raw = _api("PUT", f"/issue/{issue_key}", body={"fields": fields})
        if not ok:
            return raw
        return json.dumps({"updated": issue_key, "fields": list(fields.keys())}, indent=2)

    @mcp.tool()
    def jira_add_comment(issue_key: str, comment: str) -> str:
        """Add a comment to a Jira issue.
        Example: jira_add_comment('MTP-1234', 'Fixed in commit abc123.')
        """
        if not enabled_fn("jira"):
            return "Tool disabled. Add 'jira' to CURSOR_TOOLS_ENABLED."
        body = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment}]}],
            }
        }
        ok, raw = _api("POST", f"/issue/{issue_key}/comment", body=body)
        if not ok:
            return raw
        data = json.loads(raw)
        return json.dumps(
            {
                "comment_id": data.get("id"),
                "author": (data.get("author") or {}).get("displayName"),
                "created": data.get("created"),
            },
            indent=2,
        )

    @mcp.tool()
    def jira_transition_issue(issue_key: str, transition_name: str) -> str:
        """Move a Jira issue through its workflow by transition name.
        Common names: 'To Do', 'In Progress', 'In Review', 'Done'
        Example: jira_transition_issue('MTP-1234', 'In Progress')
        """
        if not enabled_fn("jira"):
            return "Tool disabled. Add 'jira' to CURSOR_TOOLS_ENABLED."
        ok, raw = _api("GET", f"/issue/{issue_key}/transitions")
        if not ok:
            return raw
        transitions = json.loads(raw).get("transitions", [])
        match = next(
            (t for t in transitions if t.get("name", "").lower() == transition_name.lower()),
            None,
        )
        if not match:
            available = [t.get("name") for t in transitions]
            return json.dumps(
                {"error": f"Transition '{transition_name}' not found.", "available": available},
                indent=2,
            )
        ok, raw = _api(
            "POST",
            f"/issue/{issue_key}/transitions",
            body={"transition": {"id": match["id"]}},
        )
        if not ok:
            return raw
        return json.dumps({"transitioned": issue_key, "to": transition_name}, indent=2)

    @mcp.tool()
    def jira_assign_issue(issue_key: str, account_id: str) -> str:
        """Assign a Jira issue to a user by their Atlassian accountId.
        Tip: accountIds appear in the 'assignee' field of jira_get_issue results.
        Example: jira_assign_issue('MTP-1234', '5b10a2844c20165700ede21g')
        """
        if not enabled_fn("jira"):
            return "Tool disabled. Add 'jira' to CURSOR_TOOLS_ENABLED."
        ok, raw = _api("PUT", f"/issue/{issue_key}/assignee", body={"accountId": account_id})
        if not ok:
            return raw
        return json.dumps({"assigned": issue_key, "accountId": account_id}, indent=2)

    @mcp.tool()
    def jira_link_issue(
        issue_key: str,
        target_issue_key: str,
        link_type: str = "Relates",
    ) -> str:
        """Link two Jira issues together.
        Common link types: 'Blocks', 'Cloners', 'Duplicate', 'Relates'
        Example: jira_link_issue('MTP-1234', 'MTP-5678', 'Blocks')
        """
        if not enabled_fn("jira"):
            return "Tool disabled. Add 'jira' to CURSOR_TOOLS_ENABLED."
        body = {
            "type": {"name": link_type},
            "inwardIssue": {"key": issue_key},
            "outwardIssue": {"key": target_issue_key},
        }
        ok, raw = _api("POST", "/issueLink", body=body)
        if not ok:
            return raw
        return json.dumps(
            {"linked": f"{issue_key} --[{link_type}]--> {target_issue_key}"},
            indent=2,
        )
