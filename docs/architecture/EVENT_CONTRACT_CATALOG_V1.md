# Event Contract Catalog V1 (NATS JetStream)

## 1) Purpose

Define the event model for Rin services:
- subject taxonomy,
- payload envelope,
- idempotency and ordering,
- retry/replay behavior,
- producer/consumer responsibilities.

This is a system contract document for implementation planning (no code).

---

## 2) Global Envelope Contract

Every event payload must include:

- `event_id` (UUID)
- `event_name` (stable, dot-separated)
- `event_version` (integer, starts at 1)
- `occurred_at` (UTC timestamp)
- `producer` (service name)
- `actor`:
  - `actor_id`
  - `actor_type` (`user`, `system`, `operator`, `business_admin`)
- `subject`:
  - `subject_type` (`principal`, `channel`, `profile`, `case`, `org`, `edge`, `score_snapshot`)
  - `subject_id`
- `correlation_id` (request/session trace)
- `causation_id` (upstream event or command ID)
- `idempotency_key` (required for side-effecting workflows)
- `tenant_scope` (default `global` for v1 unless multi-tenant introduced)
- `payload` (event-specific fields)

Envelope invariants:
1. `event_id` unique globally.
2. `event_version` immutable and explicit.
3. Unknown fields tolerated by consumers.
4. Breaking changes require new `event_name` or major version migration plan.

---

## 3) Subject Taxonomy

Top-level subjects (NATS):

- `identity.*`
- `channel.*`
- `profile.*`
- `contact.*`
- `policy.*`
- `org.*`
- `security.*`
- `trust.*`
- `graph.*`
- `score.*`
- `search.*`
- `system.*`

Naming rule:
- `<domain>.<entity>.<verb_past_tense>`
- Example: `channel.ownership_challenged`

---

## 4) Core Event Catalog

## 4.1 Identity

- `identity.principal_created`
- `identity.principal_updated`
- `identity.username_assigned`
- `identity.username_released`
- `identity.account_restricted`
- `identity.account_restored`

Primary producers:
- Identity service.

Primary consumers:
- Search projector,
- Graph projector,
- Notification service,
- Audit sink.

## 4.2 Channel and Ownership

- `channel.claim_started`
- `channel.claim_verified`
- `channel.ownership_challenged`
- `channel.ownership_limited`
- `channel.dispute_opened`
- `channel.ownership_transferred`
- `channel.ownership_recovered`
- `channel.ownership_revoked`
- `channel.transition_rejected`

Primary producers:
- Channel service,
- Security/Dispute service.

Primary consumers:
- Trust service,
- Score trigger,
- Search projector,
- Notification service,
- Audit sink.

## 4.3 Profile Class and Visibility

- `profile.created`
- `profile.updated`
- `profile.class_changed`
- `profile.visibility_changed`
- `profile.shadow_creation_blocked`

Rules:
- `profile.class_changed` must include previous and next class.
- Shadow profiles are flagged non-ranked in payload.

## 4.4 Contacts and Graph Edges

- `contact.sync_started`
- `contact.sync_progressed`
- `contact.sync_completed`
- `contact.edge_upserted`
- `contact.edge_deleted`
- `contact.edge_stale_marked`
- `contact.edge_restored`
- `contact.merge_contested`
- `contact.merge_split_applied`

Primary consumers:
- Graph lake writer,
- Search projector (for display/link updates),
- Score incremental trigger.

## 4.5 Policy and Circle

- `policy.circle_created`
- `policy.circle_membership_changed`
- `policy.field_visibility_changed`
- `policy.reachability_rule_changed`

Primary consumers:
- Profile render service,
- Search projection updater,
- Score modifier updater.

## 4.6 Organization / Business Authority

- `org.created`
- `org.role_granted`
- `org.role_revoked`
- `org.authority_contested`
- `org.authority_resolved`
- `org.employee_offboarded`

Primary consumers:
- Access control service,
- Notification service,
- Search projector,
- Audit sink.

## 4.7 Security and Trust

- `security.case_opened`
- `security.case_state_changed`
- `security.case_resolved`
- `security.case_reopened`
- `trust.restricted`
- `trust.restored`
- `trust.penalty_applied`
- `trust.penalty_decayed`

Primary consumers:
- Channel service,
- Score service,
- Abuse analytics,
- Notification service.

## 4.8 Score and Explainability

- `score.recompute_requested`
- `score.incremental_computed`
- `score.snapshot_published`
- `score.explanation_updated`
- `score.backfill_completed`

Primary consumers:
- Score API serving projector,
- User notifications (optional),
- Audit/reporting.

## 4.9 Search Projection

- `search.document_upserted`
- `search.document_deleted`
- `search.reindex_started`
- `search.reindex_completed`
- `search.reindex_failed`

---

## 5) JetStream Stream Design (Logical)

Suggested streams:

1. `rin.core`
- subjects: identity/channel/profile/policy/org/security/trust
- retention: work-queue + replay window

2. `rin.contact`
- subjects: contact.*
- retention: longer replay horizon (sync/debug-heavy)

3. `rin.graph`
- subjects: graph.* and score.recompute_requested
- retention: enough to replay incremental triggers

4. `rin.score`
- subjects: score.*
- retention: moderate, with snapshots archived to Iceberg

5. `rin.search`
- subjects: search.*
- retention: short-to-medium, fully rebuildable

Durability principle:
- JetStream is durable queue + replay buffer, not long-term historical source.
- Long-term immutable history goes to Iceberg/audit storage.

---

## 6) Consumer Contract

Every consumer must implement:

1. Idempotent apply semantics (by `event_id` and/or domain dedupe key).
2. Version-aware parsing (`event_version` routing).
3. Retry-safe behavior.
4. Dead-letter handling for poison events.
5. Progress checkpointing.

Dedupe key guidance:
- transition events: `subject_id + transition_version`
- sync events: `sync_session_id + chunk_seq`
- score snapshot: `score_run_id + subject_scope`

---

## 7) Ordering Guarantees

Target guarantee:
- Per-aggregate ordering, not global ordering.

Aggregate ordering keys:
- channel ownership events: normalized channel key.
- case events: `case_id`.
- contact sync events: `sync_session_id`.
- org authority events: `org_id`.

Consumer strategy:
- enforce monotonic version checks within aggregate.
- reject/regress out-of-order events with retry/backoff.

---

## 8) Retry, Backoff, DLQ

Retry policy baseline:
- exponential backoff with jitter,
- finite attempts for deterministic failures,
- infinite/long-lived for transient infra failures with circuit-breaking.

DLQ policy:
- route malformed or repeatedly failing events to domain DLQ streams:
  - `rin.dlq.core`
  - `rin.dlq.contact`
  - `rin.dlq.graph`
  - `rin.dlq.score`

DLQ remediation process:
1. classify root cause,
2. patch consumer or data issue,
3. replay corrected events.

---

## 9) Replay and Rebuild Protocol

Supported replay scenarios:

1. Rebuild search index from core + profile events.
2. Rebuild score projections from score snapshots.
3. Rehydrate graph deltas to lake from contact stream.
4. Case/audit timeline reconstitution.

Replay rules:
- never mutate historical event payloads,
- replay under new correlation context,
- maintain idempotency semantics unchanged.

---

## 10) Outbox to NATS Publication Contract

Producer-side pattern:
1. Write domain state + outbox event in same DB transaction.
2. Publisher reads outbox and publishes to NATS.
3. Mark outbox row delivered after ack.

Outbox invariants:
- exactly-once domain state mutation,
- at-least-once event publication,
- consumer idempotency provides effective exactly-once side effects.

---

## 11) Security and Privacy Rules

1. No raw secrets or OTP codes in event payloads.
2. PII minimization by subject type.
3. Sensitive fields tokenized/hashed where possible.
4. Access to streams controlled by service account roles.
5. Audit events for privileged operator actions mandatory.

Shadow profile privacy:
- `profile.class=shadow` events must include discoverability flags and rank exclusion bit.

---

## 12) Observability Requirements

Minimum telemetry per stream/consumer:

- publish rate,
- ack latency,
- redelivery count,
- consumer lag,
- DLQ rate,
- version parse failures,
- idempotency discard rate.

SLO examples:

- core stream p95 end-to-end latency < 5s.
- contact stream lag < 2 minutes in normal operation.
- score recompute request to completion p95 < configured window.

---

## 13) Failure Scenarios and Expected Behavior

1. NATS partial outage:
- outbox accumulates; publication resumes when cluster healthy.

2. Consumer deploy with incompatible schema:
- version parse failure metric spikes,
- events routed to DLQ,
- rollback consumer or add version adapter.

3. Duplicate publish after retry:
- consumer dedupe absorbs duplicate.

4. Out-of-order ownership events:
- monotonic aggregate version check rejects stale event apply.

5. Replay during live traffic:
- replay runs in isolated consumer group with side-effect gating.

---

## 14) Event Governance Process

Before adding/modifying events:

1. define aggregate and ordering key,
2. define idempotency/dedupe key,
3. specify required consumers,
4. add version migration note,
5. add observability checks.

Change control:
- event contract review required by platform + domain owner.

---

## 15) Initial Event Set to Implement First

Phase 1 (must-have):

- `identity.principal_created`
- `channel.claim_verified`
- `channel.ownership_challenged`
- `channel.ownership_transferred`
- `security.case_opened`
- `security.case_resolved`
- `contact.sync_started`
- `contact.edge_upserted`
- `contact.sync_completed`
- `score.recompute_requested`
- `score.snapshot_published`
- `search.document_upserted`

Phase 2:

- merge contest/split events,
- org authority contest/resolution events,
- trust penalty decay events,
- reindex lifecycle events.

---

## 16) Open Decisions

1. default stream retention windows by domain.
2. maximum payload size policy and chunking threshold for large sync events.
3. strict per-subject ordering enforcement mechanism in consumer framework.
4. whether to split score and graph streams earlier for operational isolation.
5. replay authorization workflow for operator-initiated rebuilds.
