# Security

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security reports.

1. Open a **[private security advisory](https://github.com/xicelestin/echolon-platform/security/advisories/new)** on this repository, or  
2. Email the maintainer with a clear subject line (e.g. “Security: Echolon Platform”).

Include:

- Description of the issue and impact  
- Steps to reproduce (if possible)  
- Affected versions or components (dashboard, backend, deployment)

We aim to acknowledge reports within a few business days.

## Good practices for this project

- Never commit **API keys**, **database URLs**, or **`.env`** files — use `.env.example` and GitHub/Streamlit secrets.  
- Rotate credentials if they were ever exposed in git history.  
- Keep **dependencies** updated (Dependabot PRs) and re-run **`CI`** after upgrades.
