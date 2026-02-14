# Rin System Architecture (DB-First, OSS, iOS-Only v1)

## 1. Scope and Non-Negotiables

- Backend runtime: Go services, Fiber HTTP framework, `zerolog`, Sentry.
- Queue/event system: NATS JetStream.
- Primary transactional DB: PostgreSQL first, Citus when sharding is required.
- Passive compute store: Iceberg tables in Parquet on object storage.
- Graph compute: Spark incremental + periodic full recompute.
- Client: iOS (Swift) only for now.
- Product mode: design-first and architecture-first (no implementation code yet).

Primary architecture objective:
- Keep one durable source of product truth (PostgreSQL) while offloading heavy graph math and history to Iceberg/Spark, so the system scales without changing the product contract.

---

## 2. Database-First Domain Model (Conceptual, No Physical Schema Yet)

PostgreSQL holds the canonical current state for:

- Identity and account ownership.
- Verified communication channels (phone/email/etc) and verification status.
- Contact graph working set for product reads/writes.
- Circle and access-control policy decisions.
- User class records (single, shadow, business, employee-link).
- Ownership disputes, anti-abuse flags, recovery state.
- Serving projections (current score, explanation snippets, search-safe profile fields).
- Event outbox for exactly-once publication semantics to NATS.

Iceberg/Parquet holds:

- Immutable append-only graph deltas.
- Historical snapshots for replay and forensic audit.
- Feature tables for ranking calibration.
- Archived stale edges and resolution outcomes.

Design rule:
- PostgreSQL answers “what is true now for app behavior”.
- Iceberg answers “what happened over time and what should be recomputed”.

---

## 3. User Class Architecture

### 3.1 Single User

- Human account with verified channel ownership.
- Can manage circles, policies, multiple channels, multiple usernames (as previously defined).
- Base identity for scoring and discovery.

### 3.2 Shadow User (Future Feature, Prepared Now)

- Alter-ego profile controlled by a single user principal.
- Unlimited potential count by product policy, but architecture must isolate:
  - namespace,
  - policy scope,
  - discoverability scope,
  - abuse controls.
- Shadow profiles must not leak into global search by default unless explicitly allowed by owner and policy.

Architecture preparation now:
- Every profile object carries `profile_class` and `owner_principal_id`.
- Access-control and search services always branch behavior by profile class.
- Scoring pipeline supports class-specific inclusion/exclusion policies.

### 3.3 Business User + Employee Profiles

- Business account is a first-class user principal.
- Employees are separate human profiles linked to the business by relationship type.
- Employee profile != business profile.
- Business may own channels and public endpoints; employees hold personal verified channels.

Architecture preparation now:
- Relationship graph must support typed edges:
  - `works_for`,
  - `represents`,
  - `administers`,
  - `delegated_contact`.
- Policy engine must resolve fields differently for business vs employee contexts.

---

## 4. Service Topology (Go + Fiber)

Core services:

- API/BFF service (authn/authz, idempotency, request shaping).
- Identity service (principal lifecycle, verification state transitions).
- Channel service (phone/email ownership verification + dispute workflows).
- Contact sync service (diff-based ingestion, conflict-safe updates).
- Policy/circle service (field-level visibility and relationship policy).
- Directory/search service (query + policy-filtered rendering).
- Graph projection service (writes deltas to lake; produces recompute triggers).
- Score serving service (reads published scores/explanations).
- Abuse and trust service (flags, throttles, recovery interventions).
- Notification service (push/SMS/email operational events).

Cross-cutting:

- Structured logs with `zerolog` correlation IDs.
- Sentry for exception + trace sampling.
- Outbox publisher for transactional event emission.

---

## 5. NATS Topology (Subjects and Responsibility)

Subject families:

- `identity.*`
- `channel.*`
- `contact.*`
- `policy.*`
- `graph.*`
- `score.*`
- `security.*`
- `search.*`

Consumer groups:

- Search index projector.
- Lake writer/projector.
- Incremental score trigger.
- Abuse/risk detector.
- Notification dispatcher.

Operational rules:

- All consumers idempotent.
- At-least-once delivery; dedupe by event key/version.
- Replay-safe event payload contracts (immutable event shape + versioning).

---

## 6. Search Architecture

Phase plan:

- Phase A (low scale): PostgreSQL FTS + trigram for person/business discovery.
- Phase B (growth): OpenSearch or Meilisearch projection.

Search invariants:

- Search index is derived, never authoritative.
- Rebuildable from PostgreSQL + event log.
- Must enforce policy filtering on read path even if index contains pre-filtered projections.

---

## 7. Rank Pipeline Architecture

Input sources:

- Contact deltas from lake.
- Verification/trust events.
- Policy-derived edge modifiers (low weight).

Pipeline layers:

- Incremental runs (high cadence, impacted neighborhoods only).
- Full recompute runs (lower cadence, correction/calibration).
- Explanation artifact generation for user-facing clarity.

Publish:

- Write current score + explanation fragments to PostgreSQL serving tables.
- Persist full run outputs in Iceberg for replay and drift analysis.

---

## 8. Collision, Hijack, and Stale Data Handling

### 8.1 Phone Hijack/Reassignment Risk

Required state machine:

- `verified_active`
- `suspected_compromise`
- `verification_challenged`
- `disputed`
- `limited_visibility`
- `recovered`

Controls:

- Hold period before irreversible ownership transfer.
- Dual-proof requirement for high-risk reclaims.
- Temporary capability downgrade during dispute.
- Full provenance trail for reversal.

### 8.2 Stale Contact Data

- Edge freshness tracked by last-confirmed evidence.
- Stale edges decay in rank influence before deletion/archival.
- Stale edges remain in history (for provenance), but not in hot compute forever.

### 8.3 Dedup Collision Safety

- Separate “likely same” from “confirmed same” links.
- Never auto-expose hidden channels via dedup confidence alone.
- Reversible merges only; no destructive hard merge without audit path.

---

## 9. Distribution and Scale Path

### Stage 1

- PostgreSQL primary + replica.
- NATS JetStream small cluster.
- PG FTS search.
- Spark on-demand jobs.

### Stage 2

- PostgreSQL partitioning + read scale.
- NATS 3-node JetStream.
- Search projection service + OpenSearch/Meilisearch.
- Regular Spark incremental jobs.

### Stage 3

- Citus sharded PostgreSQL.
- NATS 5-node.
- Persistent Spark cluster.
- Strict SLO-based autoscaling and queue lag protections.

---

## 10. Simulation Program and Results

I ran two simulation passes to force architecture stress and then validate adjustments.

### 10.1 Degree-Distribution Monte Carlo (Pass 1)

- Iterations: 1,500.
- Each iteration forces at least one user with 1,000,000 contacts and one user with 5 contacts.
- Remaining users sampled from heavy-tail distributions.

Median distribution outputs:

- `p95 contacts/user`: ~524
- `p99 contacts/user`: ~1,224
- `gini`: ~0.675
- edge share held by top 0.1% users: ~15.2% (p90 ~21.0%)
- edge share held by top 1% users: ~26.2%

Implication:
- Heavy-tail concentration is strong. Any per-owner unbucketed write path will hotspot.

### 10.2 Stress Model (Pass 1 vs Pass 2)

Iterations: 1,200 for each architecture profile.

Baseline profile:
- owner-partition only,
- no per-owner sync throttling,
- no stale-decay control,
- no claim-hold period.

Mitigated profile:
- owner+bucket partitioning (200 buckets for 1M-contact owners),
- per-owner sync cap (200 writes/s),
- stale-decay policy,
- ownership claim hold period (72h class).

Result highlights:

- Hot-partition overload event rate:
  - baseline: `100%` across scales.
  - mitigated: `0%` across scales.

- Whale sync completion time (1M contacts):
  - baseline: ~13.9 minutes.
  - mitigated: ~83.3 minutes.

Tradeoff:
- Hotspot safety requires slower large-owner ingestion unless more parallelism is allowed.

- Hijack exposure p95:
  - baseline: ~114h.
  - mitigated: ~89h.

- False-merge risk index (relative metric):
  - baseline median: ~20.2
  - mitigated median: ~7.2

Persistent issue in both passes:
- At 10B-record scale, verification/dispute processing capacity breaches modeled threshold in ~64% of runs.

Conclusion:
- Database/write path is stabilizable with bucketing + rate control.
- Human/ops-intensive verification queue becomes the dominant bottleneck at highest scale.

### 10.3 User-Class Simulation (Shadow + Business)

Iterations: 1,200.

Median outcomes across scales:

- shadow profile ratio to single-user principals: ~0.25
- search document multiplier from class expansion: ~1.6x median (p95 ~2.2x)
- business principal ratio: ~1.8%
- p99 employee-count in orgs: ~50-56 in simulation median

Risk:
- Unbounded shadow profile discoverability can double effective search/index footprint and abuse workload.

Required guardrails:
- Shadow profiles non-discoverable by default.
- Separate username/handle namespace policy for shadow class.
- Strict per-owner creation rate and trust-gated expansion.

---

## 11. Edge Cases and Architectural Responses

1) Whale account uploads 1M contacts repeatedly.
- Response: owner-level rate caps, bucketed contact storage, resumable sync sessions, dedup before write.

2) Reassigned phone number re-verified by a new owner.
- Response: ownership state machine, hold period, capability freeze, reversible link transfer.

3) Old contacts point to stale numbers/emails.
- Response: freshness decay, stale quarantine, low-confidence matching path.

4) Shadow profiles used for impersonation/spam.
- Response: class-based discoverability, higher friction for public visibility, trust-gated promotions.

5) Business offboarding employee leaves orphan links.
- Response: employee-business relation lifecycle and automatic edge deactivation policies.

6) Event replay duplicates side effects.
- Response: idempotent consumers + event versioning + dedupe keys.

7) Search index drift from transactional truth.
- Response: periodic reindex from OLTP snapshots + event checksum audits.

8) Queue backlog during contact import spikes.
- Response: per-owner quotas, stream backpressure, deferred non-critical projections.

---

## 12. Outstanding Risks After Two Iterations

These are not fully resolved by architecture iteration 2 and should be product-policy decisions:

1. Verification/dispute throughput at very high record scale (10B records scenario).
- Architecture helps, but process capacity and automation policy determine real outcomes.

2. Shadow profile abuse economics.
- Need explicit product policy for discoverability, throttles, trust levels, and monetization constraints.

3. Business-employee delegated authority boundaries.
- Need clear policy for who can edit what and what survives employment changes.

4. Jurisdiction-specific identity/retention obligations.
- Needs legal/policy pass to finalize retention + reversibility timing defaults.

---

## 13. Recommended Next Step (Still No Code)

Finalize four architecture contracts before implementation:

1. Ownership/dispute state machine contract.
2. Profile-class contract (single/shadow/business/employee).
3. Event contract catalog (subjects, idempotency keys, replay rules).
4. Scale guardrail contract (when to enable Citus, external search, and stricter sync throttles).
