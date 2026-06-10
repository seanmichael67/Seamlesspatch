# AGENTS.md - AI Operating Instructions

This file is the first stop for any AI or tmux session entering this project.

## Reconnect Ritual

1. Confirm location with `pwd`.
2. Check repo state with `git status` and current branch.
3. Read these files before acting:
   - AGENTS.md
   - FOCUS.md
   - ACTIONS.md
   - PROJECT.md
   - LOG.md
   - README.md if present
4. Summarize current state before editing files.
5. Do not perform external sends, production deploys, destructive commands, or credential changes without explicit approval.

## Working Rules

- Files are the source of truth after a crash; tmux scrollback is not.
- Prefer small, verifiable changes.
- Record meaningful work and handoff notes in LOG.md.
- Update ACTIONS.md when task priority changes.
- Keep FOCUS.md short and current.
