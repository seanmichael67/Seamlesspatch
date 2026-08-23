# ACTIONS.md - Next Concrete Tasks

## Queue

- [DONE 2026-08-11] Sean approved; `autofix/seamless-seo-index-20260807` merged to main, pushed, and Vercel deployed. Public readback verified: `robots.txt` and `sitemap.xml` both serve `https://www.seamlesspatch.com/`, homepage serves canonical + `og:url`.
- [ASK] Confirm before publishing major public copy or branding changes.
- [BLOCKED 2026-08-23] Set `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` on the `seamlesspatch` Vercel project (Production). Needs the credentials for the Supabase project holding `seamlesspatch_quote_requests`; they are not on this box. Until then every quote submission fails.
- [BLOCKED 2026-08-23] After the env vars land, submit a real test quote end-to-end. The 500 fires before `parseForm`, so the upload+insert half of `api/quote.js` has never executed in production; `module.exports.config = { api: { bodyParser: false } }` is Next.js syntax on a bare Vercel function and may be ignored. Env vars alone do not prove the form works.
- [ASK 2026-08-23] PR #1 `fix/quote-form-failsafe-20260823` is open and unmerged; it hardens the failure path and changes public copy. Merging auto-deploys to production.
- [PARKED] Nothing notifies anyone when a quote arrives - rows only land in Supabase. Decide on an alert path (Lettera poll, email, or SMS).

## Default Next Step After Reconnect

- [AUTO] Read AGENTS.md, FOCUS.md, PROJECT.md, LOG.md, and git status; then summarize what is safe to do next.

## Parking Lot

- Add or prune tasks as the project becomes clearer.
