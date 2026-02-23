"""Bitbucket category: repos, projects, PRs, issues, files."""

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

_MCP_DIR = Path(__file__).resolve().parent
_BASE_URL = "https://api.bitbucket.org/2.0"

# Load mcp_server/.bitbucket_env into os.environ
_BITBUCKET_ENV = _MCP_DIR / ".bitbucket_env"
if _BITBUCKET_ENV.exists():
    for line in _BITBUCKET_ENV.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _get_auth_headers() -> tuple[dict, str | None]:
    """Build auth header from env. Returns (headers, error)."""
    email = os.environ.get("BITBUCKET_EMAIL")
    token = os.environ.get("BITBUCKET_API_TOKEN")
    if not email or not token:
        return {}, "Missing BITBUCKET_EMAIL or BITBUCKET_API_TOKEN."
    token_str = base64.b64encode(f"{email}:{token}".encode()).decode("utf-8")
    return {"Authorization": f"Basic {token_str}"}, None


def _get_workspace(workspace: str | None) -> tuple[str | None, str | None]:
    """Resolve workspace from arg or env."""
    ws = (workspace or os.environ.get("BITBUCKET_WORKSPACE") or "").strip()
    if not ws:
        return None, "Missing BITBUCKET_WORKSPACE."
    if "bitbucket.org" in ws:
        parsed = urllib.parse.urlparse(ws)
        path = parsed.path.strip("/")
        if path:
            ws = path.split("/")[0]
    return ws, None


def _api_json(method: str, path_or_url: str, params: dict | None = None, body: dict | None = None):
    """Call Bitbucket API and return (ok, data_or_error)."""
    url = path_or_url if path_or_url.startswith("http") else f"{_BASE_URL}{path_or_url}"
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
        with urllib.request.urlopen(req, timeout=20) as resp:
            text = resp.read().decode("utf-8", errors="ignore")
        if not text:
            return True, {}
        return True, json.loads(text)
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="ignore")
        return False, f"HTTP {e.code}: {msg[:500]}"
    except Exception as e:
        return False, f"Error: {e}"


def _api_text(method: str, path_or_url: str):
    """Call Bitbucket API and return text content."""
    url = path_or_url if path_or_url.startswith("http") else f"{_BASE_URL}{path_or_url}"
    headers, err = _get_auth_headers()
    if err:
        return False, err
    req = urllib.request.Request(url, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            text = resp.read().decode("utf-8", errors="ignore")
        return True, text
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="ignore")
        return False, f"HTTP {e.code}: {msg[:500]}"
    except Exception as e:
        return False, f"Error: {e}"


def _fetch_values(path: str, params: dict | None = None, max_pages: int = 5) -> tuple[bool, list | str]:
    """Fetch paginated values from a Bitbucket list endpoint."""
    ok, data = _api_json("GET", path, params=params)
    if not ok:
        return False, data
    values = list(data.get("values", []))
    next_url = data.get("next")
    pages = 1
    while next_url and pages < max_pages:
        ok, page = _api_json("GET", next_url)
        if not ok:
            return False, page
        values.extend(page.get("values", []))
        next_url = page.get("next")
        pages += 1
    return True, values


def _trim_repo(repo: dict) -> dict:
    project = repo.get("project") or {}
    return {
        "name": repo.get("name"),
        "slug": repo.get("slug"),
        "full_name": repo.get("full_name"),
        "is_private": repo.get("is_private"),
        "project": project.get("name") or project.get("key"),
    }


def _trim_pr(pr: dict) -> dict:
    author = pr.get("author") or {}
    source = (pr.get("source") or {}).get("branch") or {}
    dest = (pr.get("destination") or {}).get("branch") or {}
    return {
        "id": pr.get("id"),
        "title": pr.get("title"),
        "state": pr.get("state"),
        "author": author.get("display_name"),
        "source_branch": source.get("name"),
        "destination_branch": dest.get("name"),
    }


def _trim_issue(issue: dict) -> dict:
    return {
        "id": issue.get("id"),
        "title": issue.get("title"),
        "state": issue.get("state"),
        "priority": issue.get("priority"),
        "kind": issue.get("kind"),
    }


def register(mcp, enabled_fn):
    """Register Bitbucket tools. Disabled when 'bitbucket' category is off."""

    @mcp.tool()
    def bitbucket_list_repos(workspace: str | None = None, max_pages: int = 3) -> str:
        """List repositories in a workspace."""
        if not enabled_fn("bitbucket"):
            return "Tool disabled. Enable 'bitbucket' in CURSOR_TOOLS_ENABLED."
        ws, err = _get_workspace(workspace)
        if err:
            return err
        ok, values = _fetch_values(f"/repositories/{ws}", params={"pagelen": 50}, max_pages=max_pages)
        if not ok:
            return values
        data = [_trim_repo(r) for r in values]
        return json.dumps(data, indent=2)

    @mcp.tool()
    def bitbucket_get_repo(workspace: str, repo_slug: str) -> str:
        """Get repository details."""
        if not enabled_fn("bitbucket"):
            return "Tool disabled. Enable 'bitbucket' in CURSOR_TOOLS_ENABLED."
        ok, data = _api_json("GET", f"/repositories/{workspace}/{repo_slug}")
        if not ok:
            return data
        return json.dumps(_trim_repo(data), indent=2)

    @mcp.tool()
    def bitbucket_list_projects(workspace: str | None = None, max_pages: int = 3) -> str:
        """List projects in a workspace."""
        if not enabled_fn("bitbucket"):
            return "Tool disabled. Enable 'bitbucket' in CURSOR_TOOLS_ENABLED."
        ws, err = _get_workspace(workspace)
        if err:
            return err
        ok, values = _fetch_values(f"/workspaces/{ws}/projects", params={"pagelen": 50}, max_pages=max_pages)
        if not ok:
            return values
        data = [{"key": p.get("key"), "name": p.get("name"), "uuid": p.get("uuid")} for p in values]
        return json.dumps(data, indent=2)

    @mcp.tool()
    def bitbucket_list_pull_requests(workspace: str, repo_slug: str, state: str = "OPEN", max_pages: int = 3) -> str:
        """List pull requests for a repository."""
        if not enabled_fn("bitbucket"):
            return "Tool disabled. Enable 'bitbucket' in CURSOR_TOOLS_ENABLED."
        params = {"state": state, "pagelen": 50}
        ok, values = _fetch_values(
            f"/repositories/{workspace}/{repo_slug}/pullrequests",
            params=params,
            max_pages=max_pages,
        )
        if not ok:
            return values
        data = [_trim_pr(pr) for pr in values]
        return json.dumps(data, indent=2)

    @mcp.tool()
    def bitbucket_get_pull_request(workspace: str, repo_slug: str, pr_id: int) -> str:
        """Get pull request details."""
        if not enabled_fn("bitbucket"):
            return "Tool disabled. Enable 'bitbucket' in CURSOR_TOOLS_ENABLED."
        ok, data = _api_json("GET", f"/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}")
        if not ok:
            return data
        return json.dumps(_trim_pr(data), indent=2)

    @mcp.tool()
    def bitbucket_create_pull_request(
        workspace: str,
        repo_slug: str,
        title: str,
        source_branch: str,
        destination_branch: str = "main",
        description: str | None = None,
    ) -> str:
        """Create a pull request."""
        if not enabled_fn("bitbucket"):
            return "Tool disabled. Enable 'bitbucket' in CURSOR_TOOLS_ENABLED."
        payload = {
            "title": title,
            "source": {"branch": {"name": source_branch}},
            "destination": {"branch": {"name": destination_branch}},
        }
        if description:
            payload["description"] = description
        ok, data = _api_json("POST", f"/repositories/{workspace}/{repo_slug}/pullrequests", body=payload)
        if not ok:
            return data
        return json.dumps(_trim_pr(data), indent=2)

    @mcp.tool()
    def bitbucket_list_issues(workspace: str, repo_slug: str, state: str = "OPEN", max_pages: int = 3) -> str:
        """List issues for a repository."""
        if not enabled_fn("bitbucket"):
            return "Tool disabled. Enable 'bitbucket' in CURSOR_TOOLS_ENABLED."
        params = {"state": state, "pagelen": 50}
        ok, values = _fetch_values(
            f"/repositories/{workspace}/{repo_slug}/issues",
            params=params,
            max_pages=max_pages,
        )
        if not ok:
            return values
        data = [_trim_issue(i) for i in values]
        return json.dumps(data, indent=2)

    @mcp.tool()
    def bitbucket_get_issue(workspace: str, repo_slug: str, issue_id: int) -> str:
        """Get issue details."""
        if not enabled_fn("bitbucket"):
            return "Tool disabled. Enable 'bitbucket' in CURSOR_TOOLS_ENABLED."
        ok, data = _api_json("GET", f"/repositories/{workspace}/{repo_slug}/issues/{issue_id}")
        if not ok:
            return data
        return json.dumps(_trim_issue(data), indent=2)

    @mcp.tool()
    def bitbucket_create_issue(workspace: str, repo_slug: str, title: str, content: str | None = None) -> str:
        """Create an issue."""
        if not enabled_fn("bitbucket"):
            return "Tool disabled. Enable 'bitbucket' in CURSOR_TOOLS_ENABLED."
        payload = {"title": title}
        if content:
            payload["content"] = {"raw": content}
        ok, data = _api_json("POST", f"/repositories/{workspace}/{repo_slug}/issues", body=payload)
        if not ok:
            return data
        return json.dumps(_trim_issue(data), indent=2)

    @mcp.tool()
    def bitbucket_get_file(workspace: str, repo_slug: str, file_path: str, ref: str = "HEAD") -> str:
        """Get raw file content from a repository."""
        if not enabled_fn("bitbucket"):
            return "Tool disabled. Enable 'bitbucket' in CURSOR_TOOLS_ENABLED."
        safe_path = urllib.parse.quote(file_path.strip("/"))
        ok, text = _api_text("GET", f"/repositories/{workspace}/{repo_slug}/src/{ref}/{safe_path}")
        if not ok:
            return text
        return text
