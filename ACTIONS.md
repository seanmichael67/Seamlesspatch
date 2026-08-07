# ACTIONS.md - Next Concrete Tasks

## Queue

- [DONE_LOCAL 2026-08-07][AUTO] Corrected the unresolved typo in the sitemap/robots host, added canonical + `og:url` metadata, shortened the meta description to 137 characters, and added a no-network SEO index check. Verification: 2/2 regression tests, local index contract 13/13, `git diff --check` clean.
- [ASK][DEPLOY] Review, push, and deploy `autofix/seamless-seo-index-20260807`; the public `robots.txt` and `sitemap.xml` will continue serving the misspelled unresolved host until deployment. After deployment, rerun `npm run check:seo` locally and read back both public files.
- [ASK] Confirm before publishing major public copy or branding changes.

## Default Next Step After Reconnect

- [AUTO] Read AGENTS.md, FOCUS.md, PROJECT.md, LOG.md, and git status; then summarize what is safe to do next.

## Parking Lot

- Add or prune tasks as the project becomes clearer.
