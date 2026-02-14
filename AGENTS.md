# Agent Instructions

Rin workspace for lightweight local tasks and document handling.

## Scope

This folder currently contains standalone files (for example, downloaded chat exports) and is **not** a git repository.

Use these instructions as the default workflow for this workspace.

## Boundaries

**Never**:
- Commit or expose secrets, credentials, or `.env` files
- Run destructive delete commands outside this folder without explicit approval

**Ask First**:
- Installing global tools or changing machine-level configuration
- Large structural changes outside `/Users/nan/Work/ai/rin`

**Always**:
- Prefer minimal, reversible edits
- Keep outputs in readable plain text formats (like `.md`) unless asked otherwise
- Keep the scratch pad up to date every session

## Scratch Pad (Continual Learning)

A persistent scratch pad at `.scratch-pad.md` tracks errors, corrections, preferences, and learnings across sessions.

**Session Start**: Read `.scratch-pad.md` before doing any work.

**Session End**: Update `.scratch-pad.md` with:
1. **Session Log** entry — query summary, approach, errors, corrections, key learnings
2. **Error Tracker** updates
3. **Corrections and Preferences** updates
4. **Anticipated Improvements** updates
5. **Cumulative Learnings** summary

**Rules**:
- Every session gets a numbered entry
- By session 3+, proactively apply patterns from logged errors/preferences
- Keep entries concise (working reference, not journal)
