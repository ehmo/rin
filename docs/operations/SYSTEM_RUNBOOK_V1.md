# Rin System Runbook V1 (Integrated Operations)

## 1) Purpose

Provide a single operational playbook that ties together:
- architecture,
- ownership/dispute state machine,
- event contracts,
- profile class rules,
- scale guardrails.

This runbook is for operating Rin as a single-team/single-operator system that can scale over time without ad-hoc decisions.

Related specs:
- `SYSTEM_ARCHITECTURE_DB_FIRST_V2.md`
- `DISPUTE_PLAYBOOK_V1.md`
- `OWNERSHIP_STATE_MACHINE_SPEC_V1.md`
- `EVENT_CONTRACT_CATALOG_V1.md`
- `PROFILE_CLASS_CONTRACT_V1.md`
- `SCALE_GUARDRAIL_CONTRACT_V1.md`

---

## 2) System Baseline (Always-On Components)

## 2.1 Control Plane

- Go/Fiber API/BFF services.
- PostgreSQL (or Citus in distributed mode).
- NATS JetStream.
- Core workers:
  - outbox publisher,
  - search projector,
  - lake projector,
  - trust/dispute processor,
  - notification dispatcher.

## 2.2 Compute Plane

- Iceberg/Parquet object storage.
- Spark jobs:
  - incremental scoring,
  - full recompute,
  - backfill/replay.

## 2.3 Projection Plane

- Search backend:
  - PG FTS in starter mode,
  - OpenSearch/Meilisearch in growth+.
- Score serving projections in PostgreSQL.

---

## 3) Daily Operating Rhythm

## 3.1 Start-of-Day Checklist

1. Check API p95/p99 and 5xx trend.
2. Check DB writer CPU, replication lag, lock waits.
3. Check JetStream lag, redelivery, DLQ counts.
4. Check search freshness and index drift sample.
5. Check score freshness and last snapshot status.
6. Check high-severity dispute queue age/SLA.

## 3.2 Midday Checkpoint

1. Review ingest spikes and owner hotspot indicators.
2. Review security case inflow (hijack/reassignment patterns).
3. Validate event publish/consume parity by stream.

## 3.3 End-of-Day Checklist

1. Confirm official score snapshot publication.
2. Confirm no unresolved high-severity cases > SLA.
3. Confirm backup jobs and WAL/archive integrity.
4. Record anomalies and guardrail trigger status.

---

## 4) Normal Flow Operations

## 4.1 User Signup and Verification

Expected flow:
1. `identity.principal_created`
2. `channel.claim_started`
3. `channel.claim_verified`
4. projection updates (search/lake/score triggers as needed)

Runbook checks:
- claim success rate,
- challenge timeout rate,
- duplicate claim rejection rate.

## 4.2 Contact Sync

Expected flow:
1. `contact.sync_started`
2. chunked edge upserts/deletes
3. `contact.sync_completed`
4. graph + search + score triggers

Runbook checks:
- sync completion rate,
- chunk retry/redelivery,
- owner hotspot warnings.

## 4.3 Score Publish

Expected flow:
1. `score.recompute_requested`
2. Spark compute
3. `score.snapshot_published`
4. `score.explanation_updated`

Runbook checks:
- freshness window,
- failed run count,
- projection apply latency.

---

## 5) Incident Playbooks

## 5.1 Incident Class A: Ownership/Hijack Spike

Trigger examples:
- surge in `channel.ownership_challenged`,
- reassignment wave,
- abnormal transfer/recovery ratio.

Immediate actions:
1. Activate stricter hold windows (per policy).
2. Prioritize C1/C2 dispute queue lane.
3. Freeze high-risk capability paths (L2/L3 bundles).
4. Increase user notifications for security prompts.

Validation:
- reduced unauthorized transfer rate,
- backlog under SLA trend.

Rollback:
- return to default holds after spike clears and backlog normalizes.

## 5.2 Incident Class B: Ingest Hotspot / Whale Sync Pressure

Trigger examples:
- hot partition warnings,
- lock wait spikes linked to contact writes,
- sync failure rate > baseline.

Immediate actions:
1. Enforce owner-level write caps.
2. Enable/deepen owner+bucket path.
3. Defer non-critical projections.
4. Keep resumable sync status visible to users.

Validation:
- hotspot warnings drop,
- sync success recovers.

Tradeoff communication:
- whale syncs may take longer; system stability prioritized.

## 5.3 Incident Class C: Event Pipeline Degradation

Trigger examples:
- JetStream lag > action threshold,
- DLQ spike,
- redelivery ratio spike.

Immediate actions:
1. Identify failing consumers by stream.
2. Throttle non-critical producers if needed.
3. Route poison payloads to DLQ and continue healthy flow.
4. Roll back incompatible consumer deployment if schema mismatch.

Validation:
- lag and DLQ trend normalize,
- replay plan created for missed projections.

## 5.4 Incident Class D: Search Drift/Leak Risk

Trigger examples:
- sampled drift > threshold,
- policy leakage signals,
- stale disputed ownership in search results.

Immediate actions:
1. Force read-time strict policy filtering.
2. Pause problematic index updater.
3. Run targeted reindex for impacted aggregates.

Validation:
- drift back under threshold,
- no policy leakage in random samples.

## 5.5 Incident Class E: Score Pipeline Missed Window

Trigger examples:
- incremental freshness misses,
- full snapshot missed publish window,
- recompute run failures.

Immediate actions:
1. Run incremental fallback for critical cohorts.
2. Publish “last verified snapshot” marker if full run misses.
3. Scale Spark workers/parallelism.

Validation:
- freshness recovers,
- snapshot publishing stabilized.

---

## 6) Migration Day Playbooks

## 6.1 Postgres -> Citus

Pre-migration:
1. Confirm guardrail triggers sustained.
2. Confirm shard key and compatibility report approved.
3. Dry-run migration and checksum validation in staging.

Cutover window:
1. Backfill shards.
2. Enable dual-write/dual-read verification window.
3. Switch primary write path.
4. Monitor correctness + latency + error rates continuously.

Abort conditions:
- correctness mismatch > allowed threshold,
- write failures spike,
- latency regression beyond rollback threshold.

Post-migration:
1. Keep fallback path for defined soak period.
2. Reconcile row counts and event parity.
3. Close migration with signed run report.

## 6.2 PG FTS -> External Search

Pre-cutover:
1. Full index build.
2. Relevance parity sample tests.
3. Policy filtering verification.

Cutover:
1. Dual-read compare mode.
2. Switch primary search backend.
3. Keep PG FTS as emergency fallback.

Abort conditions:
- policy leak,
- unacceptable latency regression,
- drift beyond threshold.

---

## 7) Security and Dispute Operations

## 7.1 Case Priority Queue

Priority order:
1. account/channel takeover,
2. business authority compromise,
3. impersonation,
4. mistaken merge,
5. trust appeal.

## 7.2 Case Handling Sequence

1. Open case (`security.case_opened`).
2. Apply severity safeguards.
3. Execute ownership transition workflow per state machine.
4. Resolve case (`security.case_resolved`).
5. Trigger score/search projection recompute.

## 7.3 SLA Monitoring

- high severity: first action under target.
- aged unresolved cases: page operator.
- breach trend: activate temporary stricter policy bundle.

---

## 8) Profile Class Enforcement in Operations

Operational checks:

1. `shadow` profile discoverability defaults remain off.
2. `shadow` rank inclusion always false.
3. Business role revocations propagate quickly to projections.
4. Employee offboarding invalidates delegated authority immediately.

Incident checks:
- Any shadow profile in ranking index is a P1 policy bug.
- Any employee retaining org authority after revocation is a P1 auth bug.

---

## 9) Replay and Recovery Operations

## 9.1 Safe Replay Procedure

1. Define replay scope (stream + time window + aggregates).
2. Use isolated consumer group.
3. Cap replay rate to protect live traffic.
4. Confirm idempotency dedupe metrics stable.
5. Validate projection parity after replay.

## 9.2 Recovery from Partial Outage

1. Verify outbox backlog.
2. Resume event publication.
3. Drain consumers by priority:
   - core ownership/security
   - contact graph
   - score/search projections
4. Reconcile lag and missing projections.

---

## 10) Dashboards and Alert Policies

Required dashboards:
1. API health.
2. DB/Citus health.
3. NATS JetStream health.
4. Search freshness/drift.
5. Score freshness/publish.
6. Dispute queue and SLA.

Critical alerts (page):
1. ownership transfer anomalies,
2. unresolved high-severity dispute backlog,
3. JetStream core lag sustained beyond threshold,
4. search policy leakage indicator,
5. score publish window miss.

---

## 11) Decision Framework (When Unsure)

Use this order:
1. Safety and ownership integrity.
2. Correctness and reversibility.
3. User-visible continuity.
4. Throughput/cost optimization.

If conflict exists:
- choose safer, slower path,
- communicate temporary degradation clearly.

---

## 12) Weekly/Monthly Governance

Weekly:
1. SLO breach review.
2. dispute trend review.
3. class-behavior compliance review.

Monthly:
1. guardrail trigger audit.
2. replay and restore drill report.
3. threshold tuning proposals.

Quarterly:
1. architecture mode evaluation (`S/G/D`).
2. migration readiness evaluation.
3. unresolved risk register update.

---

## 13) Open Items to Finalize

1. Exact acceptable sync-time ceiling for whale owners.
2. Final default hold windows by risk and jurisdiction.
3. External search default choice (OpenSearch vs Meilisearch).
4. Criteria for introducing dedicated human dispute review lane.
5. Business public metric policy (if not personal ranking).
