# Service Implementation Blueprint V1

## 1. Purpose
Translate existing architecture contracts into implementation-ready service boundaries, runtime composition, and rollout sequence for backend delivery.

Linked bead:
- `rin-3i0.4.1`

Primary references:
- `docs/architecture/SYSTEM_ARCHITECTURE_DB_FIRST_V2.md`
- `docs/architecture/DATA_MODEL_BOUNDARIES_V1.md`
- `docs/architecture/EVENT_CONTRACT_CATALOG_V1.md`
- `docs/architecture/OWNERSHIP_STATE_MACHINE_SPEC_V1.md`
- `docs/architecture/PROFILE_CLASS_CONTRACT_V1.md`
- `docs/plan/outlines/02_API_SURFACE_OUTLINE_V1.md`

## 2. Delivery Model (Founder-Operable First)
Use a staged model to minimize operational complexity early:

**Staging terminology:** This document uses **Infrastructure Stage A/B/C** for deployment progression. User cohort progression uses **Beta Stage 1/2/3** — see Beta Cohort Strategy.

1. Stage A: modular monolith deployment (single backend binary) with strict internal domain boundaries.
2. Stage B: split high-churn workers/services (search projector, score orchestrator, dispute processor).
3. Stage C: split API and domain services where scale guardrails force separation.

Contract rule:
- Service boundaries below are logical from day 1, even if initially deployed as one process.

## 3. Logical Service Map

### 3.1 API Gateway/BFF

**Compatibility note:** ConnectRPC handlers produce `net/http.Handler` implementations. Fiber uses a custom context model. Use the `fibernewrelic`-style adapter pattern or consider switching to Chi/stdlib `net/http` mux for native ConnectRPC compatibility. Decision to be finalized at implementation.

Responsibilities:
- Fiber HTTP entrypoint.
- AuthN/AuthZ enforcement and request validation.
- Idempotency key handling and correlation IDs.
- Command routing and query aggregation.

Writes:
- none (delegates to domain services).

Events:
- none directly; receives async status via query projections.

### 3.2 Identity Service
Responsibilities:
- Principal lifecycle and username policies.
- Account restrictions/restorations.

Writes:
- identity aggregate only.

Produces:
- `identity.*`

Consumes:
- `security.*` and `trust.*` for account capability effects.

### 3.3 Channel Ownership Service
Responsibilities:
- Channel claim/verify lifecycle.
- Ownership state-machine transitions.
- Recovery and transfer handling.

Writes:
- ownership/channel aggregate only.

Produces:
- `channel.*`

Consumes:
- `security.case_*`, `trust.restricted`, `trust.restored`.

### 3.4 Contact Sync Service
Responsibilities:
- Snapshot/delta ingestion.
- Sync sessions, chunk processing, and edge freshness.
- Reversible merge/split requests.

Writes:
- sync sessions and contact-edge truth aggregates.

Produces:
- `contact.*`

Consumes:
- identity/channel summaries needed for canonical linking.

### 3.5 Profile Service
Responsibilities:
- Profile metadata and class assignment (`single|shadow|business|employee`).
- Discoverability flags and presentation settings.

Writes:
- profile aggregate only.

Produces:
- `profile.*`

Consumes:
- `org.*`, `security.*` for visibility constraints.

### 3.6 Policy/Circle Service
Responsibilities:
- Circle lifecycle and membership.
- Field-level visibility/reachability controls.

Writes:
- policy/circle aggregate only.

Produces:
- `policy.*`

Consumes:
- `profile.*` and `org.*` context events.

### 3.7 Organization Authority Service
Responsibilities:
- Business roles, delegation, and employee-org authority links.
- Offboarding authority revocation.

Writes:
- organization authority aggregate only.

Produces:
- `org.*`

Consumes:
- `identity.*`, `profile.*`, `security.*` as gating context.

### 3.8 Security and Dispute Service
Responsibilities:
- Case lifecycle, severity bundles, trust restrictions.
- Auto/manual adjudication orchestration.

Writes:
- case/trust aggregate only.

Produces:
- `security.*`, `trust.*`

Consumes:
- `channel.*`, `contact.*`, `org.*`, abuse signals.

### 3.9 Search Projection Service
Responsibilities:
- Maintain search documents from canonical events.
- Reindex and drift correction.

Writes:
- search projection only.

Produces:
- `search.*`

Consumes:
- `identity.*`, `profile.*`, `policy.*`, `channel.*`, `org.*`.

### 3.10 Graph and Score Services
Graph Projection responsibilities:
- Event-to-lake projection checkpoints.
- Feed incremental/full compute requests.

Score responsibilities:
- Score snapshot publish + explanation projection.

Writes:
- lake projection artifacts (graph service),
- score serving projections (score service).

Produces:
- `graph.*`, `score.*`

Consumes:
- `contact.*`, `policy.*`, `trust.*`, `channel.*`.

### 3.11 Notification Service
Responsibilities:
- Dispatch in-app/push/email/SMS operational notifications.

Writes:
- delivery logs only.

Produces:
- optional notification telemetry events.

Consumes:
- `security.*`, `channel.*`, `score.*`, `org.*`.

## 4. Command and Query Ownership

### 4.1 Command Routing (from API)
- Identity commands -> Identity Service.
- Ownership commands -> Channel Ownership Service.
- Contact ingestion commands -> Contact Sync Service.
- Circle/policy commands -> Policy/Circle Service.
- Profile-class commands -> Profile Service (+ Org Authority for employee/business role operations).
- Dispute/abuse commands -> Security and Dispute Service.

### 4.2 Query Ownership
- User/profile reads: Profile + Identity projections.
- Channel state reads: Ownership projections.
- Contacts/circles reads: Contact + Policy projections.
- Search/discovery reads: Search projection with read-time policy filter.
- Score reads: Score serving projection only.
- Dispute/security reads: Security case projection.

## 5. Event Topology and Stream Assignment
Canonical subjects (contract):
- `identity.*`, `channel.*`, `profile.*`, `contact.*`, `policy.*`, `org.*`, `security.*`, `trust.*`, `graph.*`, `score.*`, `search.*`, `system.*`

Logical stream grouping:
- `rin.core`: identity/channel/profile/policy/org/security/trust
- `rin.contact`: contact
- `rin.graph`: graph + recompute triggers
- `rin.score`: score lifecycle
- `rin.search`: search projection lifecycle

Consumer contract requirements:
- idempotent apply,
- version-aware parsing,
- retry + DLQ behavior,
- checkpointed progress,
- replay-safe side effects.

## 6. Data Ownership Rules (Implementation Enforcement)
Enforce in code and review:
1. Each aggregate has one writing service.
2. Cross-domain mutation must go through command + event path.
3. Derived stores (search, score, lake) are never authoritative write sources.
4. Outbox publication is part of the same write transaction for authoritative updates.
5. Shadow profiles can never own channels and are never ranking inputs.

## 7. Runtime Composition by Stage

### Stage A (Initial)
Deployables:
- `apps/server/cmd/api` (includes domain modules)
- `apps/server/cmd/worker` (outbox publisher + core consumers)
- `apps/server/cmd/score-worker` (score/lake orchestration)

Dependencies:
- PostgreSQL
- NATS JetStream
- object store + Spark jobs (scheduled)
- PG FTS search

### Stage B (Growth)
Split deployables:
- search projector worker
- dispute/trust worker
- score orchestrator worker

Reason to split:
- queue lag isolation,
- failure-domain control,
- release independence for high-churn components.

### Stage C (Distributed)
Further split if triggered by guardrails:
- dedicated API/BFF tier,
- dedicated ownership/dispute tier,
- external search cluster,
- Citus migration.

## 8. Monorepo Implementation Targets
Planned paths (no code yet):
- `apps/server/cmd/api/`
- `apps/server/cmd/worker/`
- `apps/server/cmd/score-worker/`
- `apps/server/internal/identity/`
- `apps/server/internal/ownership/`
- `apps/server/internal/contactsync/`
- `apps/server/internal/profile/`
- `apps/server/internal/policy/`
- `apps/server/internal/org/`
- `apps/server/internal/security/`
- `apps/server/internal/searchproj/`
- `apps/server/internal/score/`
- `packages/contracts/api/`
- `packages/contracts/events/`

## 9. Reliability and Security Baseline
- All command handlers require idempotency keys.
- Every request/event chain carries correlation IDs.
- Sensitive transitions write immutable audit records.
- Replay authorization follows approved policy from `docs/plan/freeze/ARCH_DECISION_CLOSURE_V1.md`.
- Incident and rollback behavior follows `docs/operations/SYSTEM_RUNBOOK_V1.md`.

## 10. Rollout Plan (Execution)
1. Lock service contracts and command/query ownership (this doc + API surface doc).
2. Define endpoint-level contract docs by domain.
3. Define event schema files for each subject family.
4. Create deployment manifests for Stage A services.
5. Run end-to-end replay and dispute scenario drills in staging.

## 11. Exit Criteria
`rin-3i0.4.1` is complete when:
- service boundaries and responsibilities are explicit,
- command/query ownership is mapped,
- event producer/consumer responsibilities are mapped,
- stage-based runtime composition is defined,
- monorepo target paths for implementation are defined.
