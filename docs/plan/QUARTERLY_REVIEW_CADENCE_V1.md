# Quarterly Roadmap Review Cadence V1

Solo founder self-review. No board, no advisors. Lightweight but structured enough to prevent drift.

Companion docs:
- `docs/analytics/KPI_HIERARCHY_V1.md` (metric definitions and targets)
- `docs/plan/BACKLOG_INDEX.md` (Beads epic map)
- `docs/plan/freeze/ARCH_DECISION_CLOSURE_V1.md` (decision register)

---

## 1) Review Template

Complete this checklist every quarter. Output goes to `docs/reviews/YYYY-QN.md`.

### Metric Snapshot

| Metric | Value | Trend | Target | Status |
|--------|-------|-------|--------|--------|
| MAU-V | | | See KPI doc | |
| D30 retention | | | >15% | |
| Premium conversion | | | >30% of trials | |
| NPS | | | >25 | |
| MRR | | | -- | |

### What Shipped

List features, specs, and launches completed this quarter.

### What Didn't Ship and Why

List planned items that slipped. One sentence per item on root cause.

### Top 3 Wins

1.
2.
3.

### Top 3 Misses / Learnings

1.
2.
3.

### Next Quarter Priorities (Max 3)

| # | Objective | Key Result | Maps to KPI |
|---|-----------|-----------|-------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

### Decision Log Review

- Any ADRs that need revisiting given what happened this quarter?
- Any frozen decisions that new data invalidates?
- List ADR IDs to reopen (if any).

### Beads Backlog Health Check

- Total open issues: ___
- Oldest unresolved P0/P1: ___
- Epics with no progress this quarter: ___
- Issues to close as stale: ___

Run `bd stats` and `bd list --status=open` to populate.

---

## 2) Review Schedule

| Item | Detail |
|------|--------|
| When | Last week of each quarter (Mar, Jun, Sep, Dec) |
| Duration | ~2 hours |
| Output | `docs/reviews/YYYY-QN.md` (e.g., `2026-Q1.md`) |
| Prep | Pull PostHog dashboard exports, run `bd stats` |

Calendar quarters: Q1 = Jan-Mar, Q2 = Apr-Jun, Q3 = Jul-Sep, Q4 = Oct-Dec.

---

## 3) Decision Review Triggers

Revisit architectural decisions outside the quarterly cycle when any of these occur:

| Trigger | Threshold | Action |
|---------|-----------|--------|
| User milestone | 1K, 10K, 100K MAU-V | Review infra ADRs, scaling assumptions |
| Revenue milestone | $1K, $10K MRR | Review monetization ADRs, pricing model |
| Performance breach | Any guardrail from KPI doc trips | Review relevant system ADR immediately |
| Market change | Competitor launch, platform policy shift, API deprecation | Review affected ADRs within 1 week |

When triggered: create a Beads issue (`bd create --type=task --title="ADR review: <trigger>"`) and link to the relevant ADR.

---

## 4) Anti-Drift Guardrails

Five rules. Non-negotiable.

1. **Max 3 objectives per quarter.** If a fourth feels urgent, it replaces one of the three.
2. **No new epic without closing one.** Backlog grows only through tasks within existing epics, not new epics.
3. **Every feature must map to a KPI.** If it doesn't move MAU-V, retention, conversion, or NPS, it waits.
4. **Spec before code.** No implementation without a doc in `docs/` that a future session can reference.
5. **Weekly review is mandatory.** Skip the weekly 30-min review (KPI doc section 6.2) and the quarter is already drifting.
