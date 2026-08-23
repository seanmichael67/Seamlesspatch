# PROJECT.md - Stable Project Summary

## Name

Seamless Patch

## Summary

Drywall repair website for Sean’s nephew-in-law; GitHub/Vercel-backed static/web project.

## Project Path

`/home/cryptonovado/projects/seamless-patch`

## Current State

Verified 2026-08-23: the SEO index fix shipped (merged 2026-08-11) and the public site is healthy on the read path - homepage, `robots.txt`, and `sitemap.xml` all 200 with the correct canonical host, and the sitemap is accepted in Search Console. The lead path is not healthy: `POST /api/quote` returns 500 because the Vercel project has no environment variables set, so no quote submission has ever been saved. PR #1 hardens the failure path so leads are not silently lost; the root cause needs credentials plus a live test submission. See LOG.md and ACTIONS.md.

## Source of Truth

- AGENTS.md: operating rules
- FOCUS.md: current priority
- ACTIONS.md: executable queue
- LOG.md: handoff/history
- README.md or app docs if present

## Safety Notes

- Verify before acting.
- Do not assume tmux state survived a crash.
- Ask before external/public/destructive actions.
