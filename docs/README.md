# Synthepyzer manual

This is the static, user-facing manual for Synthepyzer. It is intentionally separate from the PyQt6 application so the product language and first-time user journey can be shaped before the app is built.

## Run locally

From the repository root, start a simple HTTP server:

```text
python3 -m http.server
```

Then open `http://localhost:8000/docs/` in a browser.

The manual uses Markdown files in `content/`, a small vendored renderer in `markdown.js`, and no package installation or build step.
