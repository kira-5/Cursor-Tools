"""Memory MCP tools (Wrapper for official npx server)."""
import json
from pathlib import Path

_DISABLED_MSG = "Tool disabled. Enable 'memory' in CURSOR_TOOLS_ENABLED."
_MEMORY_FILE = Path(__file__).resolve().parent / ".memory.json"

def _load_memory():
    if not _MEMORY_FILE.exists():
        return {}
    try:
        return json.loads(_MEMORY_FILE.read_text())
    except:
        return {}

def _save_memory(data):
    _MEMORY_FILE.write_text(json.dumps(data, indent=2))

def register(mcp, enabled_fn):
    """Register Memory MCP tools (Native Python implementation for maximum control)."""

    @mcp.tool()
    def store_memory(key: str, value: str) -> str:
        """Store a value in persistent memory for the agent to remember across chats."""
        if not enabled_fn("memory"):
            return _DISABLED_MSG
        
        mem = _load_memory()
        mem[key] = value
        _save_memory(mem)
        return f"Successfully remembered: {key}"

    @mcp.tool()
    def retrieve_memory(key: str) -> str:
        """Retrieve a stored value from the agent's persistent memory."""
        if not enabled_fn("memory"):
            return _DISABLED_MSG
        
        mem = _load_memory()
        return mem.get(key, f"No memory found for key: {key}")

    @mcp.tool()
    def list_memories() -> str:
        """List all keys currently stored in the agent's persistent memory."""
        if not enabled_fn("memory"):
            return _DISABLED_MSG
        
        mem = _load_memory()
        if not mem:
            return "Memory is currently empty."
        return "Stored keys:\n- " + "\n- ".join(mem.keys())
