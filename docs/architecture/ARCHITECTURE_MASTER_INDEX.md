# Rin Architecture Master Index

## 1) Purpose

Single entry point for the architecture package.

Use this file to:
- read docs in the right order,
- understand dependency between contracts,
- see what is locked vs still open,
- know the next planning steps before implementation.

---

## 2) Recommended Reading Order

## Phase A: Product and System Context

1. `docs/product/PROJECT_SYNTHESIS.md`
2. `docs/product/DESIGN_DECISION_MEMO_V1.md`
3. `docs/product/USER_JOURNEY_PLAN.md`
4. `docs/product/RIN_SCORE_V1.md`

Goal:
- align on product intent, journey, and score philosophy.

## Phase B: Core Architecture and Validation

5. `docs/architecture/ARCHITECTURE_PLAN_OSS_V1.md`
6. `docs/architecture/SYSTEM_ARCHITECTURE_DB_FIRST_V2.md`
7. `docs/architecture/SERVICE_IMPLEMENTATION_BLUEPRINT_V1.md`
8. `docs/simulations/SIMULATION_RESULTS_V1.md`

Goal:
- understand high-level infra and simulation-backed risks.

## Phase C: Security/Ownership and Event Contracts

8. `docs/operations/DISPUTE_PLAYBOOK_V1.md`
9. `docs/architecture/OWNERSHIP_STATE_MACHINE_SPEC_V1.md`
10. `docs/architecture/EVENT_CONTRACT_CATALOG_V1.md`

Goal:
- lock dispute handling, state transitions, and event semantics.

## Phase D: Class and Scale Governance

11. `docs/architecture/PROFILE_CLASS_CONTRACT_V1.md`
12. `docs/architecture/SCALE_GUARDRAIL_CONTRACT_V1.md`
13. `docs/architecture/DATA_MODEL_BOUNDARIES_V1.md`
14. `docs/operations/SYSTEM_RUNBOOK_V1.md`
15. `docs/architecture/MONOREPO_CONVENTIONS_V1.md`

Goal:
- lock class behavior, scale triggers, ownership boundaries, and day-2 operations.

---

## 3) Contract Dependency Graph

1. `docs/operations/DISPUTE_PLAYBOOK_V1.md` depends on `docs/product/RIN_SCORE_V1.md` and journey decisions.
2. `docs/architecture/OWNERSHIP_STATE_MACHINE_SPEC_V1.md` is derived from dispute playbook.
3. `docs/architecture/EVENT_CONTRACT_CATALOG_V1.md` encodes side-effects from ownership/dispute contracts.
4. `docs/architecture/PROFILE_CLASS_CONTRACT_V1.md` constrains ownership + events + ranking.
5. `docs/architecture/SCALE_GUARDRAIL_CONTRACT_V1.md` uses architecture + simulation + runbook targets.
6. `docs/architecture/DATA_MODEL_BOUNDARIES_V1.md` enforces service ownership across all contracts.
7. `docs/operations/SYSTEM_RUNBOOK_V1.md` operationalizes all of the above.
8. `docs/architecture/MONOREPO_CONVENTIONS_V1.md` defines repository structure and change rules for implementation phase.
9. `docs/architecture/SERVICE_IMPLEMENTATION_BLUEPRINT_V1.md` translates contracts into build-ready service boundaries.

---

## 4) Locked Decisions (Current)

1. OSS-first architecture.
2. Core stack:
- PostgreSQL -> Citus,
- NATS JetStream,
- Iceberg/Parquet,
- Spark,
- PG FTS -> OpenSearch/Meilisearch when triggered.
3. Shadow profile policy:
- excluded from ranking input/output,
- non-discoverable by default,
- cannot directly own channels.
4. Ownership/dispute model uses explicit state machine + reversible transitions.
5. Event architecture uses outbox + idempotent consumers + replay-safe contracts.
6. Scale transitions are threshold-triggered with rollback criteria.

---

## 5) Open Decisions (Need Founder Confirmation)

Closure packet:
- `docs/plan/freeze/ARCH_DECISION_CLOSURE_V1.md`

High priority:
1. Completed and approved in `docs/plan/freeze/ARCH_DECISION_CLOSURE_V1.md` on 2026-02-14.

Medium priority:
6. Business public metric policy (if no personal ranking).
7. Employee org-affiliation visibility defaults.
8. Operator SQL incident policy hardening.

---

## 6) Execution Sequence (No Code Yet)

1. Finalize open decisions above.
2. Freeze v1 contract set (state machine, events, class, guardrails, boundaries).
3. Produce implementation planning artifacts:
- API surface contract,
- deployment topology,
- observability/alert spec,
- migration checklist.
4. Start implementation only after contract freeze tag.

---

## 7) Suggested Freeze Tag

When all high-priority open decisions are resolved, create architecture freeze marker:
- `ARCH_FREEZE_V1`

Freeze package should include:
- all Phase C and D contracts,
- runbook,
- unresolved-risk register with explicit acceptance.

---

## 8) Quick Navigation

Planning and guide docs:
- `docs/guide/README.md`
- `docs/plan/BATTLE_PLAN_IMPLEMENTATION_V1.md`
- `docs/plan/BACKLOG_INDEX.md`

Core technical docs:
- `docs/architecture/SYSTEM_ARCHITECTURE_DB_FIRST_V2.md`
- `docs/architecture/SERVICE_IMPLEMENTATION_BLUEPRINT_V1.md`
- `docs/architecture/OWNERSHIP_STATE_MACHINE_SPEC_V1.md`
- `docs/architecture/EVENT_CONTRACT_CATALOG_V1.md`
- `docs/architecture/PROFILE_CLASS_CONTRACT_V1.md`
- `docs/architecture/SCALE_GUARDRAIL_CONTRACT_V1.md`
- `docs/architecture/DATA_MODEL_BOUNDARIES_V1.md`
- `docs/architecture/MONOREPO_CONVENTIONS_V1.md`
- `docs/operations/SYSTEM_RUNBOOK_V1.md`

Validation docs:
- `docs/simulations/SIMULATION_RESULTS_V1.md`

Product anchors:
- `docs/product/USER_JOURNEY_PLAN.md`
- `docs/product/RIN_SCORE_V1.md`
