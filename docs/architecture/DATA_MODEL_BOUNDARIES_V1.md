# Data Model Boundaries V1 (Service Ownership, No Physical Schema)

## 1) Purpose

Define high-level data ownership boundaries so each service has clear authority over:
- what it can write,
- what it can read,
- what it publishes as events,
- what it must never mutate directly.

This prevents cross-service coupling and preserves replayability, auditability, and safe scaling.

---

## 2) Boundary Principles

1. One primary writer per domain aggregate.
2. Other services consume projections/events, not direct writes.
3. Cross-domain changes happen via commands/events, not shared mutable ownership.
4. Source-of-truth writes occur in PostgreSQL/Citus + outbox transaction.
5. Derived stores (search index, score projections, lake tables) are rebuildable.

---

## 3) Canonical Domain Aggregates

Core aggregate groups:

1. Principal Identity
2. Channel Ownership
3. Contact Edge and Sync Session
4. Profile and Profile Class
5. Circle/Policy
6. Organization Authority
7. Security Case and Trust State
8. Score Snapshot/Explanation
9. Search Document Projection
10. Lake Projection Artifact

---

## 4) Service-to-Data Ownership Matrix

## 4.1 Identity Service

Primary writes:
- principal lifecycle,
- username assignment/release,
- account-level status flags.

Reads:
- policy state (read-only),
- trust restrictions (read-only),
- org linkage summary (read-only).

Must not write directly:
- channel ownership transitions,
- contact edges,
- score outputs,
- search documents.

Publishes:
- `identity.*` events.

## 4.2 Channel/Ownership Service

Primary writes:
- channel claims,
- ownership state transitions,
- challenge and transfer outcomes.

Reads:
- principal status,
- security case context,
- trust risk signals.

Must not write directly:
- search index rows,
- score tables,
- profile class assignments.

Publishes:
- `channel.*` events.

## 4.3 Contact Sync Service

Primary writes:
- sync session state,
- edge upsert/delete intents,
- freshness metadata for edges.

Reads:
- principal/channel mapping summaries,
- policy hints for ingestion constraints.

Must not write directly:
- ownership state,
- trust penalties,
- score outputs,
- search documents.

Publishes:
- `contact.*` events.

## 4.4 Profile Service

Primary writes:
- profile metadata,
- profile class assignment,
- discoverability flags.

Reads:
- identity summary,
- policy settings,
- org role summary.

Must not write directly:
- ownership transitions,
- trust case lifecycle,
- score computation outputs.

Publishes:
- `profile.*` events.

## 4.5 Policy/Circle Service

Primary writes:
- circle definitions,
- memberships,
- field visibility/reachability policy.

Reads:
- profile metadata,
- org relationship context.

Must not write directly:
- contact edge data,
- channel ownership,
- search/score derived docs.

Publishes:
- `policy.*` events.

## 4.6 Organization Authority Service

Primary writes:
- org roles,
- delegation grants/revocations,
- employee-business authority links.

Reads:
- identity/profile summaries,
- security case restrictions.

Must not write directly:
- business channel ownership transitions (command channel service instead),
- ranking outputs.

Publishes:
- `org.*` events.

## 4.7 Security/Dispute Service

Primary writes:
- security case lifecycle,
- severity and action bundles,
- trust restrictions/restorations.

Reads:
- ownership timelines,
- profile class context,
- org authority context,
- abuse signals.

Must not write directly:
- ownership state without calling ownership transition contract,
- search index data,
- score snapshots.

Publishes:
- `security.*` and `trust.*` events.

## 4.8 Score Service

Primary writes:
- score serving projections,
- explanation snippets,
- score run metadata.

Reads:
- graph features from lake,
- policy modifiers,
- trust signals.

Must not write directly:
- identity ownership data,
- contact edge truth,
- profile class assignments.

Publishes:
- `score.*` events.

## 4.9 Search Projection Service

Primary writes:
- search documents only.

Reads:
- identity/profile/policy/ownership projection events.

Must not write directly:
- source-of-truth business tables,
- trust/ownership canonical states.

Publishes:
- `search.*` projection lifecycle events.

## 4.10 Lake Projection Service

Primary writes:
- Iceberg projection artifacts,
- projection checkpoints.

Reads:
- contact/policy/ownership/trust events.

Must not write directly:
- OLTP canonical records.

Publishes:
- optional `graph.*` projection status events.

---

## 5) Read Models vs Write Models

Write models (authoritative):
- Identity, Ownership, Contacts, Profile Class, Policy, Org Authority, Security Case.

Read/derived models:
- Search docs,
- score serving views,
- graph feature tables,
- analytics/reporting datasets.

Rule:
- Never promote a derived model into an authoritative write source.

---

## 6) Cross-Domain Change Rules

Allowed patterns:

1. Sync command -> owning service writes -> outbox -> events -> projections.
2. Security case decision -> ownership transition command -> ownership service applies state transition.
3. Org role revocation -> profile/search/permission projections update asynchronously.

Disallowed patterns:

1. service A directly updates service B aggregate tables.
2. search or score service writing back identity truth fields.
3. projection stores used as conflict-resolution source.

---

## 7) Consistency Model

- Intra-aggregate updates: strong consistency in PostgreSQL/Citus transaction.
- Inter-aggregate updates: eventual consistency via NATS.
- User-visible constraints:
  - critical security effects should appear near-immediate,
  - non-critical projections may lag within SLO windows.

Consistency guardrails:
- each aggregate has version/sequence for monotonic processing.
- idempotent consumers required for all side-effect handlers.

---

## 8) Profile Class Boundary Rules (Critical)

1. `shadow` cannot own channels; ownership aggregate rejects shadow actor.
2. `shadow` rank inclusion is always false in score write model.
3. `business` authority changes must flow through org authority aggregate.
4. `employee` org representation rights are projection of delegated role, not implicit.

Boundary violations are P1 defects.

---

## 9) Security and Audit Boundaries

Audit ownership:
- Security/Dispute service owns case and action audit records.
- Ownership service owns transition audit records.
- Event publisher owns delivery audit checkpoints.

Immutable trail requirements:
- transition reason codes,
- actor metadata,
- timestamps,
- causation/correlation IDs,
- reversal references.

---

## 10) Scale Boundary Evolution

Mode S:
- keep boundaries strict even if services share deploy/runtime.

Mode G:
- split high-churn domains into independent worker pools.

Mode D:
- enforce explicit service-level DB access policies and shard-aware ownership.

Boundary evolution rule:
- scaling changes should alter deployment topology, not domain ownership authority.

---

## 11) Boundary Compliance Checks

Weekly checks:
1. unauthorized writer detection by aggregate.
2. projection drift sampling.
3. cross-service write anomalies.

Pre-release checks:
1. event contract compatibility,
2. ownership transition invariants,
3. profile class enforcement,
4. search/rank exclusion rules for shadow class.

---

## 12) Common Boundary Failure Modes

1. “Shortcut writes” directly to search or score to patch incidents.
2. Security service forcing ownership state without transition contract.
3. Org role changes not propagating before profile/search reads.
4. Derived projections accidentally treated as canonical source.

Mitigation:
- enforce DB permission boundaries by service,
- run invariant checks in CI and periodic production audits,
- standard incident patch procedure that preserves ownership rules.

---

## 13) Open Decisions

1. exact service decomposition for v1 deployment (combined vs separate binaries).
2. whether score service owns explanation generation or separate explainer service.
3. whether lake projection service is separate from contact projection worker in mode S.
4. access policy for ad-hoc operator SQL in incidents.
5. minimal required projection lag SLO per domain in mode S.
