"""Docs category: get_docs_urls, get_doc, cursor-docs-index, readme, etc."""
import os
from pathlib import Path

_MCP_DIR = Path(__file__).resolve().parent

def get_project_root() -> Path:
    if env_root := os.getenv("CURSOR_PROJECT_ROOT"):
        return Path(env_root).resolve()
    current = Path.cwd().resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists() or (parent / ".cursor").exists():
            return parent
    return _MCP_DIR.parent

PROJECT_ROOT = get_project_root()

# Docs that get_doc can read. Paths may be relative to MCP dir or project root.
_DOC_NAMES = {"cursor-index", "readme", "mcp-readme", "mcp-setup", "mcp-tools-reference", "email-template"}


def _doc_path(doc_name: str) -> Path:
    mcp_docs = {
        "cursor-index": "cursor-docs-index.json",
        "mcp-readme": "README.md",
        "mcp-setup": "docs/SETUP_USAGE.md",
        "mcp-tools-reference": "docs/TOOLS_USAGE.md",
    }
    if doc_name in mcp_docs:
        return _MCP_DIR / mcp_docs[doc_name]
    if doc_name == "readme":
        for p in [PROJECT_ROOT / "README.md", PROJECT_ROOT / "readme.md", PROJECT_ROOT / "backend" / "README.md"]:
            if p.exists():
                return p
    return PROJECT_ROOT / {"email-template": "EMAIL_TEMPLATE_SAMPLE.html"}.get(
        doc_name, doc_name
    )


def register(mcp, enabled_fn):
    """Register docs tools/resources. Disabled when 'docs' category is off."""
    @mcp.tool()
    def get_docs_urls(priority: str = "core") -> str:
        """Get prioritized list of official documentation URLs for Cursor indexing. use priority: core (FastAPI/Pydantic), recommended (SQLAlchemy/GCP), or optional (Dynaconf)."""
        if not enabled_fn("docs"):
            return "Tool disabled. Enable 'docs' in CURSOR_TOOLS_ENABLED (e.g. docs,project_info,db)."
        docs = [
            {"name": "FastAPI", "url": "https://fastapi.tiangolo.com/", "priority": "core"},
            {"name": "Pydantic", "url": "https://docs.pydantic.dev/", "priority": "core"},
            {"name": "SQLAlchemy", "url": "https://docs.sqlalchemy.org/", "priority": "core"},
            {"name": "asyncpg", "url": "https://magicstack.github.io/asyncpg/", "priority": "recommended"},
            {"name": "Uvicorn", "url": "https://www.uvicorn.org/", "priority": "recommended"},
            {"name": "Google Pub/Sub", "url": "https://cloud.google.com/pubsub/docs", "priority": "recommended"},
            {"name": "Google BigQuery", "url": "https://cloud.google.com/bigquery/docs", "priority": "recommended"},
            {"name": "Dynaconf", "url": "https://www.dynaconf.com/", "priority": "optional"},
        ]
        filtered = [d for d in docs if d["priority"] == priority]
        if not filtered:
            filtered = docs
        return "\n".join([f"{d['name']}: {d['url']}" for d in filtered])

    @mcp.tool()
    def get_doc(doc_name: str) -> str:
        """Read a project-specific architectural or setup document. available doc_names: cursor-index, readme, mcp-readme, mcp-setup, mcp-tools-reference, email-template."""
        if not enabled_fn("docs"):
            return "Tool disabled. Enable 'docs' in CURSOR_TOOLS_ENABLED."
        if doc_name not in _DOC_NAMES:
            return f"Unknown doc. Available: {', '.join(sorted(_DOC_NAMES))}"
        path = _doc_path(doc_name)
        if not path.exists():
            return f"File not found: {path}"
        return path.read_text()

    @mcp.resource("mtp://docs/cursor-index")
    def get_cursor_docs_index() -> str:
        """Get the cursor-docs-index JSON for backup/reference."""
        if not enabled_fn("docs"):
            return "Resource disabled. Enable 'docs' in CURSOR_TOOLS_ENABLED."
        return get_doc("cursor-index")

    @mcp.resource("mtp://project/readme")
    def get_readme() -> str:
        """Get the project README."""
        if not enabled_fn("docs"):
            return "Resource disabled. Enable 'docs' in CURSOR_TOOLS_ENABLED."
        return get_doc("readme")

    @mcp.resource("mtp://mcp/readme")
    def get_mcp_readme() -> str:
        """Get mcp_server README."""
        if not enabled_fn("docs"):
            return "Resource disabled. Enable 'docs' in CURSOR_TOOLS_ENABLED."
        return get_doc("mcp-readme")

    @mcp.resource("mtp://project/mcp-setup")
    def get_mcp_setup() -> str:
        """Get MCP setup summary."""
        if not enabled_fn("docs"):
            return "Resource disabled. Enable 'docs' in CURSOR_TOOLS_ENABLED."
        return get_doc("mcp-setup")

    @mcp.resource("mtp://mcp/tools-reference")
    def get_mcp_tools_reference() -> str:
        """Get MCP tools reference."""
        if not enabled_fn("docs"):
            return "Resource disabled. Enable 'docs' in CURSOR_TOOLS_ENABLED."
        return get_doc("mcp-tools-reference")

    @mcp.resource("mtp://docs/email-template")
    def get_email_template() -> str:
        """Get email template sample."""
        if not enabled_fn("docs"):
            return "Resource disabled. Enable 'docs' in CURSOR_TOOLS_ENABLED."
        return get_doc("email-template")
