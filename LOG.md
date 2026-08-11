# LOG.md - Running Handoff Notes

## 2026-05-18 - Context scaffold added

- Added standard project context file scaffold where missing.
- Future sessions should append concise notes here after meaningful work.
- Reconnect ritual: read AGENTS.md, FOCUS.md, ACTIONS.md, PROJECT.md, LOG.md, then inspect git status.

## 2026-08-07 - Local SEO index safe fix

- Public readback returned HTTP 200 for the homepage, `robots.txt`, and `sitemap.xml`, but both SEO discovery files pointed at `www.seaslessjpatch.com`, which did not resolve.
- Created local branch `autofix/seamless-seo-index-20260807` and corrected both URLs to `https://www.seamlesspatch.com/`.
- Added canonical + Open Graph URL metadata and reduced the meta description from 170 to 137 characters.
- Added `scripts/check_seo_index.py`, `scripts/test_check_seo_index.py`, and `npm run check:seo` so the canonical-host/index contract fails closed without network access.
- Verification: regression tests 2/2 passed; local contract 13/13 passed; Python compilation and `git diff --check` passed.
- Boundary: local-only; no push or deployment. Public files remain stale until an approved deploy.

## 2026-08-11 - SEO index fix deployed

- Sean approved the deploy. Merged `autofix/seamless-seo-index-20260807` into main (merge cc47a5e) and pushed; Vercel deployed in ~20s.
- Public readback verified: `robots.txt` sitemap line and `sitemap.xml` `<loc>` both serve `https://www.seamlesspatch.com/`; homepage serves the canonical and `og:url` tags. Apex 307s to www, www returns 200.
