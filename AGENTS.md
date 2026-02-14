# Agent Instructions

Rin monorepo for product docs, architecture, infrastructure, backend, and iOS app.

## Scope

Use these instructions as the default workflow for this repository.

## Boundaries

**Never**:
- Commit or expose secrets, credentials, or `.env` files
- Force push to any branch
- Rewrite published history unless explicitly approved
- Run destructive delete commands outside this folder without explicit approval

**Ask First**:
- Installing global tools or changing machine-level configuration
- Large structural changes outside `/Users/nan/Work/ai/rin`

**Always**:
- Prefer minimal, reversible edits
- Keep outputs in readable plain text formats (like `.md`) unless asked otherwise
- Keep the scratch pad up to date every session

## Git Workflow

When completing work:
1. Ensure branch is current with remote (`git pull --rebase` when needed)
2. Commit related changes in focused commits
3. Push to remote before ending the session
4. Verify clean state (`git status`) and upstream tracking

Rules:
- Do not leave completed work only in local commits.
- Avoid large mixed commits across unrelated areas.
- Commit `.scratch-pad.md` with session changes.

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

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
