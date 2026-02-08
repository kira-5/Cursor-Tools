"""DB category: list_databases, run_database_query, run_database_query_from_file."""
import json
import os
import re
from pathlib import Path

_MCP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(os.environ.get("CURSOR_PROJECT_ROOT", _MCP_DIR.parent))

# Load mcp_server/.db_env into os.environ (for ${env:VAR} in databases.json)
for _db_env in [_MCP_DIR / ".db_env"]:
    if _db_env.exists():
        for line in _db_env.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ[k.strip()] = v.strip().strip('"').strip("'")
        break


def _substitute_env(s: str) -> str:
    """Replace ${env:VAR} with os.environ.get('VAR', ''). Keeps secrets out of committed files."""
    def repl(m):
        return os.environ.get(m.group(1), "")
    return re.sub(r"\$\{env:(\w+)\}", repl, s)


def _load_databases():
    """Load database connection strings from mcp_server/databases.json. Supports ${env:VAR} for secrets."""
    config_file = _MCP_DIR / "databases.json"
    if not config_file.exists():
        return {}
    try:
        data = json.loads(config_file.read_text())
        dbs = data.get("databases", data)
        return {k: _substitute_env(v) for k, v in dbs.items()}
    except (json.JSONDecodeError, KeyError):
        return {}


def _get_default_database():
    """Get default database name from backend .secrets.toml: TENANT_NAME + '_' + DEPLOYMENT_ENV."""
    for path in [PROJECT_ROOT / "backend" / ".secrets.toml", PROJECT_ROOT / ".secrets.toml"]:
        if not path.exists():
            continue
        try:
            import tomllib
            with open(path, "rb") as f:
                data = tomllib.load(f)
            merged = {}
            for section in ("base-pricing-local", "DEFAULT", "local"):
                if section in data and isinstance(data[section], dict):
                    merged.update(data[section])
            for section_name, section_data in data.items():
                if isinstance(section_data, dict) and not section_name.startswith("_"):
                    merged.update(section_data)
            tenant = merged.get("TENANT_NAME") or merged.get("tenant_name")
            env = merged.get("DEPLOYMENT_ENV") or merged.get("DEPLOY_ENV") or merged.get("deployment_env")
            if tenant and env:
                return f"{tenant}_{env}"
        except Exception:
            continue
    return None


def _format_table(columns: list, rows: list, database_name: str) -> str:
    """Format query result as a scrollable Markdown table for chat."""
    def _fmt(v):
        if v is None:
            return ""
        if isinstance(v, bool):
            return str(v)
        if isinstance(v, list):
            return ", ".join(str(x) for x in v)
        s = str(v).replace("|", "\\|").replace("\n", " ")
        return s

    header = "| " + " | ".join(str(c) for c in columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    data_rows = ["| " + " | ".join(_fmt(r[i]) for i in range(len(columns))) + " |" for r in rows]
    table = "\n".join([header, sep] + data_rows)
    return f"**Database: {database_name}**\n\n{table}\n\n*{len(rows)} rows*"


def register(mcp, enabled_fn):
    """Register db tools. Disabled when 'db' category is off. Disabling db turns off all: list_databases, run_database_query, run_database_query_from_file, list_tables, describe_table."""
    @mcp.tool()
    def list_databases() -> str:
        """List available database names from mcp_server/databases.json. Use these names with run_database_query."""
        if not enabled_fn("db"):
            return "Tool disabled. Enable 'db' in CURSOR_TOOLS_ENABLED (e.g. docs,project_info,db)."
        dbs = _load_databases()
        if not dbs:
            return "No databases configured. Add mcp_server/databases.json (see mcp_server/databases.json.example)"
        return "\n".join(sorted(dbs.keys()))

    @mcp.tool()
    def run_database_query(sql: str | None = None, database_name: str | None = None, output_file: str | None = "queries/result.md") -> str:
        """Run a read-only SQL query. Pass sql to execute; if sql is empty/omitted and database_name is given, uses project's queries/query.sql. If database_name omitted, uses TENANT_NAME_DEPLOYMENT_ENV from .secrets.toml. Pass output_file (e.g. queries/result.md) to write results to a file—open in a new tab to view outside chat. Pass empty string to skip file output."""
        if not enabled_fn("db"):
            return "Tool disabled. Enable 'db' in CURSOR_TOOLS_ENABLED (e.g. docs,project_info,db)."
        import psycopg2

        dbs = _load_databases()
        if not dbs:
            return "No databases configured. Add mcp_server/databases.json"

        if not database_name:
            database_name = _get_default_database()
            if not database_name:
                return f"No database specified. Pass database_name or set TENANT_NAME_DEPLOYMENT_ENV in backend/.secrets.toml. Available: {', '.join(sorted(dbs.keys()))}"

        if database_name not in dbs:
            return f"Unknown database: {database_name}. Available: {', '.join(sorted(dbs.keys()))}"

        if not sql or not sql.strip():
            sql_file = PROJECT_ROOT / "queries" / "query.sql"
            if not sql_file.exists():
                return f"No query provided. Pass sql, or create {sql_file}"
            sql = sql_file.read_text()

        conn_str = dbs[database_name]
        try:
            with psycopg2.connect(conn_str) as conn:
                conn.set_session(readonly=True)
                with conn.cursor() as cur:
                    cur.execute(sql)
                    if cur.description:
                        columns = [desc[0] for desc in cur.description]
                        rows = cur.fetchall()
                        result = _format_table(columns, rows, database_name)
                        if output_file:
                            out_path = PROJECT_ROOT / output_file
                            out_path.parent.mkdir(parents=True, exist_ok=True)
                            out_path.write_text(result)
                            return f"Database: **{database_name}** · Results written to **{output_file}** — open in a new tab to view outside chat.\n\n{result}"
                        return result
                    return f"Database: {database_name}\n{cur.rowcount} rows affected"
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    def run_database_query_from_file(database_name: str | None = None, file_path: str | None = None) -> str:
        """Run SQL from project's queries/query.sql (default). Pass database_name to target a DB. Pass file_path for a different file. If only database_name given, reads from {project_root}/queries/query.sql."""
        if not enabled_fn("db"):
            return "Tool disabled. Enable 'db' in CURSOR_TOOLS_ENABLED (e.g. docs,project_info,db)."
        if file_path:
            sql_file = PROJECT_ROOT / file_path
        else:
            sql_file = PROJECT_ROOT / "queries" / "query.sql"
        if not sql_file.exists():
            return f"File not found: {sql_file}. Create queries/query.sql in project root or pass file_path."
        sql = sql_file.read_text()
        return run_database_query(sql, database_name)

    @mcp.tool()
    def list_tables(schema_name: str, database_name: str | None = None) -> str:
        """List tables in a schema. Uses PostgreSQL information_schema. No hardcoding needed."""
        if not enabled_fn("db"):
            return "Tool disabled. Enable 'db' in CURSOR_TOOLS_ENABLED."
        dbs = _load_databases()
        if not dbs:
            return "No databases configured. Add mcp_server/databases.json"
        if not database_name:
            database_name = _get_default_database()
            if not database_name:
                return f"No database specified. Pass database_name or set TENANT_NAME+DEPLOYMENT_ENV. Available: {', '.join(sorted(dbs.keys()))}"
        if database_name not in dbs:
            return f"Unknown database: {database_name}. Available: {', '.join(sorted(dbs.keys()))}"
        sql = f"""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema = %s AND table_type = 'BASE TABLE'
            ORDER BY table_schema, table_name
        """
        import psycopg2
        try:
            with psycopg2.connect(dbs[database_name]) as conn:
                conn.set_session(readonly=True)
                with conn.cursor() as cur:
                    cur.execute(sql, (schema_name,))
                    if cur.description:
                        columns = [desc[0] for desc in cur.description]
                        rows = cur.fetchall()
                        return _format_table(columns, rows, database_name)
                    return f"Database: {database_name}\n0 tables"
        except Exception as e:
            return f"Error: {e}"

    @mcp.tool()
    def describe_table(schema_name: str, table_name: str, database_name: str | None = None) -> str:
        """Describe table columns (name, type, nullable). Uses PostgreSQL information_schema. No hardcoding needed."""
        if not enabled_fn("db"):
            return "Tool disabled. Enable 'db' in CURSOR_TOOLS_ENABLED."
        dbs = _load_databases()
        if not dbs:
            return "No databases configured. Add mcp_server/databases.json"
        if not database_name:
            database_name = _get_default_database()
            if not database_name:
                return f"No database specified. Pass database_name or set TENANT_NAME+DEPLOYMENT_ENV. Available: {', '.join(sorted(dbs.keys()))}"
        if database_name not in dbs:
            return f"Unknown database: {database_name}. Available: {', '.join(sorted(dbs.keys()))}"
        sql = """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """
        import psycopg2
        try:
            with psycopg2.connect(dbs[database_name]) as conn:
                conn.set_session(readonly=True)
                with conn.cursor() as cur:
                    cur.execute(sql, (schema_name, table_name))
                    if cur.description:
                        columns = [desc[0] for desc in cur.description]
                        rows = cur.fetchall()
                        return _format_table(columns, rows, database_name)
                    return f"Table {schema_name}.{table_name} not found"
        except Exception as e:
            return f"Error: {e}"
