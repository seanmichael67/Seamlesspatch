# PROJECT.md - Stable Project Summary

## Name

Seamless Patch

## Summary

Drywall repair website for Sean’s nephew-in-law; GitHub/Vercel-backed static/web project.

## Project Path

`/home/cryptonovado/projects/seamless-patch`

## Current State

Verified 2026-08-07: local `main` matched `origin/main` before the safe-fix branch was created, and the public homepage, `robots.txt`, and `sitemap.xml` all returned HTTP 200. The public SEO files still reference an unresolved misspelled host. Local branch `autofix/seamless-seo-index-20260807` fixes that host, adds canonical metadata, and adds a deterministic no-network check; it is not pushed or deployed.

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
