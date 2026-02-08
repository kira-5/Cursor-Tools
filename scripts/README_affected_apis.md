# Affected APIs — Use in Other Projects

Copy these files to another project:

1. **scripts/affected_apis.py** — the script
2. **.affected_apis.json.example** — example config (copy to `.affected_apis.json` in project root)

## Setup in another project

```bash
# 1. Create config in project root (edit for your project)
cp .affected_apis.json.example /path/to/your-project/.affected_apis.json
```

Script runs from cursor-tools; it detects project root via git and loads `.affected_apis.json`.

## Config format (.affected_apis.json)

```json
{
  "app_path": "backend/app",
  "api_prefix": "/api/v1",
  "module_to_tag": {
    "products": "products",
    "users": "users",
    "orders": "orders"
  }
}
```

| Field | Description |
|-------|-------------|
| `app_path` | Path to your app code (e.g. `backend/app`, `app`, `src`) |
| `api_prefix` | Your API prefix (optional, for display) |
| `module_to_tag` | Map directory names to friendly API area names. Omit to use directory names as-is. |

## Optional: Cursor commands

Copy to `.cursor/commands/`:

- `affected-apis.md` — run on demand
- `affected-apis-before-commit.md` — run for staged changes

## Optional: Pre-commit hook

Add to your `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: affected-apis
      name: Affected APIs (staged changes)
      entry: bash -c 'cd "$(git rev-parse --show-toplevel)" && python scripts/affected_apis.py --staged'
      language: system
      pass_filenames: false
      always_run: true
```

## Usage

```bash
python scripts/affected_apis.py           # all changes
python scripts/affected_apis.py --staged # staged only
```
