# Rin Battle Plan (Implementation V1)

## 1. Goal
Build Rin end-to-end from planning to launch with one coherent operating system across:
- product and UX,
- architecture and data systems,
- iOS delivery,
- infrastructure and operations,
- App Store compliance,
- growth and monetization,
- future superapp roadmap.

This plan is tied to the bead program epic `rin-3i0`.

## 2. Planning Principles
- Contracts before code: freeze behavior, events, and ownership rules first.
- One source of truth: all execution references this docs package + beads.
- Scale by guardrails: only introduce new infrastructure at explicit thresholds.
- Founder-operable by default: prefer simpler systems unless a trigger forces complexity.
- Reversible changes: design for history, auditability, and replay.

## 3. Workstreams (Beads)
- Program umbrella: `rin-3i0`
- Requirements and decision closure: `rin-3i0.1`
- UX journeys and behavior model: `rin-3i0.2`
- Design system and visual language: `rin-3i0.3`
- Backend architecture planning: `rin-3i0.4`
- Data, ranking, search: `rin-3i0.5`
- Security, trust, disputes: `rin-3i0.6`
- iOS foundation and features: `rin-3i0.7`, `rin-3i0.8`
- Infra, cloud, on-prem, SRE: `rin-3i0.9`, `rin-3i0.10`, `rin-3i0.11`
- App Store and release: `rin-3i0.12`
- GTM, business model, analytics: `rin-3i0.13`, `rin-3i0.14`, `rin-3i0.15`
- Beta and launch program: `rin-3i0.16`
- Future roadmap streams and developer platform: `rin-3i0.17`, `rin-3i0.18`

## 4. Phase Plan

### Phase 0: Architecture Freeze Prep (Now)
Outcomes:
- Close high-priority open architecture decisions.
- Confirm freeze criteria and sign-off model.
- Convert contracts into implementation outlines.

Primary beads:
- `rin-3i0.1.1`, `rin-3i0.1.2`, `rin-3i0.1.3`
- `rin-3i0.4.1`, `rin-3i0.4.2`
- `rin-3i0.5.1`, `rin-3i0.6.1`

Gate:
- `ARCH_FREEZE_V1` criteria drafted and accepted.

### Phase 1: Product Behavior and UX System
Outcomes:
- Final journey map (happy/unhappy paths) for single, shadow, business, employee.
- Circle-management UX and dispute UX with low cognitive overhead.
- iOS information architecture and screen contracts.

Primary beads:
- `rin-3i0.2.*`, `rin-3i0.3.*`, `rin-3i0.7.2`

Gate:
- UX flows signed; edge-case states mapped to backend events.

### Phase 2: Technical Design and Platform Blueprint
Outcomes:
- Service boundaries and command/query API surface.
- Ranking/search computation lifecycle and release policy.
- Environment topology, CI/CD gates, config/secrets model.

Primary beads:
- `rin-3i0.4.*`, `rin-3i0.5.*`, `rin-3i0.9.*`, `rin-3i0.11.1`

Gate:
- Deployment topology + observability outline approved.

### Phase 3: App Store and Launch Readiness Design
Outcomes:
- App Store policy and metadata checklist.
- TestFlight and release process.
- Beta acceptance criteria and launch readiness checklist.

Primary beads:
- `rin-3i0.12.*`, `rin-3i0.16.*`

Gate:
- App Store compliance matrix complete for v1 scope.

### Phase 4: Growth, Monetization, and Analytics Operating Model
Outcomes:
- KPI hierarchy and event taxonomy.
- Monetization ladder and pricing hypotheses.
- GTM ICP/messaging and channel experiments.

Primary beads:
- `rin-3i0.13.*`, `rin-3i0.14.*`, `rin-3i0.15.*`

Gate:
- Weekly operating review template and experiment governance ready.

### Phase 5: Future Streams Backlog Design
Outcomes:
- Phase 2/3/4 capabilities (media, location, information) prioritized.
- Developer ecosystem and trust API concept backlog formalized.

Primary beads:
- `rin-3i0.17.*`, `rin-3i0.18.*`

Gate:
- Long-range roadmap linked to current architecture constraints.

## 5. Dependency Spine
Execution order constraints:
1. Requirements closure -> UX flows -> API contracts.
2. Ownership/dispute rules -> ranking/search behavior.
3. Data lifecycle and guardrails -> infra topology and SRE plans.
4. iOS flows + backend contracts -> App Store readiness.
5. Analytics taxonomy -> GTM and monetization experiments.

## 6. Suggested Start Point (Immediate)
Start with Phase 0 and focus on four artifacts in order:
1. `docs/plan/outlines/01_ARCH_FREEZE_CHECKLIST_V1.md`
2. `docs/plan/outlines/02_API_SURFACE_OUTLINE_V1.md`
3. `docs/plan/outlines/03_DEPLOYMENT_TOPOLOGY_OUTLINE_V1.md`
4. `docs/plan/outlines/04_OBSERVABILITY_ALERTING_OUTLINE_V1.md`

Why this start:
- It reduces rewrite risk before implementation.
- It translates current architecture contracts into build-ready guidance.
- It keeps the system operable for a single-founder setup.

## 7. Tracking and Cadence
- Daily: update issue status and blockers in beads.
- Weekly: architecture + product review against this plan.
- Monthly: roadmap and scale-trigger review.

Useful commands:
- `bd show rin-3i0`
- `bd children rin-3i0`
- `bd ready`
- `bd update <id> --status in_progress`

## 8. References
- Program index: `docs/plan/BACKLOG_INDEX.md`
- Interactive guide: `docs/guide/README.md`
- Architecture index: `docs/architecture/ARCHITECTURE_MASTER_INDEX.md`
