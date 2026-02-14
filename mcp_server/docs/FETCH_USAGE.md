# FETCH Usage Guide

Convert any URL into clean, readable Markdown for deep reading by the AI.

## 🛠️ Tools

| Tool | Parameters | Description |
| :--- | :--- | :--- |
| `fetch_url` | `url` | Fetches HTML and converts it to basic Markdown. |

## 💡 Example Prompts
- "Fetch the content of this documentation URL: `https://fastapi.tiangolo.com/`."
- "Read this blog post and summarize the key findings."

## 🚀 Best Practices
- Great for reading long-form documentation that isn't included in the project's internal docs.
- The tool automatically strips scripts and styles to focus on the text, saving token usage.
- If the page is very long, it may truncate the result to the first 5,000 characters.
