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

## 2026-08-11 - Google Search Console property + sitemap

- Added `https://www.seamlesspatch.com/` as a URL-prefix property in Sean's Search Console (seanmichael67@gmail.com) and verified ownership via the `google-site-verification` meta tag in index.html (do not remove it).
- Note: Vercel `cleanUrls` 308-redirects `/google64cda59d857c9f4a.html`, so the HTML-file method was abandoned; the file remains in the repo but the meta tag is the active verification.
- Submitted `sitemap.xml`; Google read it immediately: Status Success, 1 page discovered.

## 2026-08-23 - Quote form fallback hardened; root cause found (not fixed)

- The quote form has not been able to save anything. `POST /api/quote` returns
  `500 {"ok":false,"error":"Quote backend is not configured yet"}`, and the Vercel
  project `seamlesspatch` (`prj_LLek9U77JAlg3tFUp4FZDTX7W15m`) returns
  `{"envs": [], "hiddenProductionEnvCount": 0}` - no environment variable is set at all.
  `api/quote.js` checks `SUPABASE_URL`/`SUPABASE_SERVICE_ROLE_KEY` first, so every web
  submission takes the failure path.
- That failure path promised "your text app is opening as backup", then ran
  `window.location.href = smsUrl`. Desktop browsers usually have no `sms:` handler, so
  nothing happened and the message contained no link and no phone number to fall back on.
- Fix: failure path now stays on the page, keeps what the visitor typed, and renders a
  tap-to-text link, a tap-to-call link, and (602) 881-1676 as plain readable text.
- Also removed internal-facing copy that was shipping to visitors ("Upload real job photos
  here as soon as he sends them", "will outperform stock photos", "Gallery Coming Next")
  and replaced the panel with a plain quote CTA that promises no photo callback.
- Added `scripts/check_quote_failsafe.py` + 10 unit tests + `npm run check:quote` and an
  `npm test` script that discovers all `scripts/test_*.py`.
- Verification: new check fails 4/8 against the pre-fix page and passes 8/8 after;
  `npm test` 12/12; `npm run check:seo` still 13/13; headless Chromium with `/api/quote`
  forced to 500 stayed on the page with fields preserved and both recovery links present.
  Repo `main` was byte-identical to live production HTML before the edits.
- Boundary: PR #1 opened and left UNMERGED. Merging main auto-deploys to production.
- STILL BROKEN: the form cannot save until the two Supabase env vars are set, and that is
  not proven sufficient - the 500 fires before `parseForm`, so upload+insert have never run
  in production. Requires a live test submission. Nothing notifies anyone on a new quote.
