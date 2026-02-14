# LOGS Usage Guide

Live debugging and inspection of application log files.

## 🛠️ Tools

| Tool | Parameters | Description |
| :--- | :--- | :--- |
| `tail_logs` | `n` (optional), `file_path` (optional) | Get the last `n` lines from a log file. |
| `read_log_file` | `file_path`, `lines` (optional) | Read a full log file or the first `n` lines. |

## 💡 Example Prompts
- "Tail the last 50 lines of `app.log`."
- "Show me the logs for the last few minutes."
- "Read the first 100 lines of `error.log`."

## 🚀 Best Practices
- Use `tail_logs` for checking the result of a fresh manual test run.
- Default path is `logs/app.log`. If your logs are elsewhere, specify the `file_path` explicitly.
- For very large logs, `tail_logs` is much more performance-friendly than `read_log_file`.
