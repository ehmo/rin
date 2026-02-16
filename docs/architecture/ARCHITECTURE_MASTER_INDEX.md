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
8. `docs/architecture/GRAPH_DATA_LIFECYCLE_V1.md`
9. `docs/simulations/SIMULATION_RESULTS_V1.md`

Goal:
- understand high-level infra and simulation-backed risks.

## Phase C: Security/Ownership and Event Contracts

10. `docs/operations/DISPUTE_PLAYBOOK_V1.md`
11. `docs/architecture/OWNERSHIP_STATE_MACHINE_SPEC_V1.md`
12. `docs/architecture/EVENT_CONTRACT_CATALOG_V1.md`

Goal:
- lock dispute handling, state transitions, and event semantics.

## Phase D: Class and Scale Governance

13. `docs/architecture/PROFILE_CLASS_CONTRACT_V1.md`
14. `docs/architecture/SCALE_GUARDRAIL_CONTRACT_V1.md`
15. `docs/architecture/DATA_MODEL_BOUNDARIES_V1.md`
16. `docs/operations/SYSTEM_RUNBOOK_V1.md`
17. `docs/architecture/MONOREPO_CONVENTIONS_V1.md`

Goal:
- lock class behavior, scale triggers, ownership boundaries, and day-2 operations.

---

## Extended Architecture Documents

### iOS Architecture
- `docs/architecture/IOS_APP_ARCHITECTURE_V1.md` — iOS app module structure and MVVM+Coordinator
- `docs/architecture/IOS_API_CLIENT_V1.md` — ConnectRPC wire protocol and contract versioning
- `docs/architecture/IOS_NAVIGATION_STATE_V1.md` — Navigation, deep linking, and state management
- `docs/architecture/IOS_OFFLINE_STORAGE_V1.md` — SwiftData cache and mutation queue

### Infrastructure
- `docs/architecture/CLOUD_PROVIDER_STRATEGY_V1.md` — Hetzner + Cloudflare stack evaluation
- `docs/architecture/ONPREM_HYBRID_ARCHITECTURE_V1.md` — K3s reference architecture
- `docs/architecture/SECRETS_CONFIG_MANAGEMENT_V1.md` — SOPS + age secret management

### Data and Search
- `docs/architecture/SEARCH_RELEVANCE_STRATEGY_V1.md` — PostgreSQL FTS architecture
- `docs/architecture/RANKING_QUALITY_EVALUATION_V1.md` — Synthetic persona test framework
- `docs/architecture/DATA_RETENTION_DELETION_V1.md` — Three-stage anonymize-purge policy

### Backend Evolution
- `docs/architecture/BACKEND_MIGRATION_GUIDE_V1.md` — Stage A → B → C migration plan
- `docs/architecture/EXPERIMENTATION_FRAMEWORK_V1.md` — PostHog A/B testing and ADR register

### Developer Platform (v2/v3)
- `docs/architecture/DEVELOPER_PLATFORM_VISION_V1.md` — Platform vision and capability model
- `docs/architecture/API_PRODUCTIZATION_TIERS_V1.md` — Four-tier API access model
- `docs/architecture/KYC_TRUST_ASSERTIONS_V1.md` — Trust assertions and portable badges

---

## 3) Contract Dependency Graph

1. `docs/operations/DISPUTE_PLAYBOOK_V1.md` depends on `docs/product/RIN_SCORE_V1.md` and journey decisions.
2. `docs/architecture/OWNERSHIP_STATE_MACHINE_SPEC_V1.md` is derived from dispute playbook.
3. `docs/architecture/EVENT_CONTRACT_CATALOG_V1.md` encodes side-effects from ownership/dispute contracts.
4. `docs/architecture/PROFILE_CLASS_CONTRACT_V1.md` constrains ownership + events + ranking.
5. `docs/architecture/SCALE_GUARDRAIL_CONTRACT_V1.md` uses architecture + simulation + runbook targets.
6. `docs/architecture/GRAPH_DATA_LIFECYCLE_V1.md` defines tiering and transitions for graph truth and history.
7. `docs/architecture/DATA_MODEL_BOUNDARIES_V1.md` enforces service ownership across all contracts.
8. `docs/operations/SYSTEM_RUNBOOK_V1.md` operationalizes all of the above.
9. `docs/architecture/MONOREPO_CONVENTIONS_V1.md` defines repository structure and change rules for implementation phase.
10. `docs/architecture/SERVICE_IMPLEMENTATION_BLUEPRINT_V1.md` translates contracts into build-ready service boundaries.

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
- `docs/architecture/GRAPH_DATA_LIFECYCLE_V1.md`
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
