# Graph Data Lifecycle Contract V1 (Hot/Warm/Cold)

## 1) Purpose
Define the canonical lifecycle for graph data (contacts/edges/identity links) across hot, warm, and cold tiers so the system remains:
- reversible,
- replay-safe,
- privacy-aware,
- cost-efficient at scale.

Linked bead:
- `rin-3i0.5.1`

Primary dependencies:
- `docs/architecture/SYSTEM_ARCHITECTURE_DB_FIRST_V2.md`
- `docs/architecture/SCALE_GUARDRAIL_CONTRACT_V1.md`
- `docs/architecture/DATA_MODEL_BOUNDARIES_V1.md`
- `docs/architecture/EVENT_CONTRACT_CATALOG_V1.md`

## 2) Scope and Non-Goals
Scope:
- contact-edge lifecycle,
- canonical link confidence lifecycle,
- freshness/decay/archival transitions,
- replay and retention rules by tier.

Non-goals:
- physical schema/index design,
- exact Spark job implementation details,
- jurisdiction-specific legal wording.

## 3) Canonical Graph Artifacts

1. Raw intake artifacts
- immutable contact snapshot and delta evidence from sync sessions.
- never edited in place.

2. Working edge truth
- current directed edges used by product APIs and policy checks.
- includes evidence freshness metadata.

3. Canonical identity links
- linkage between observed endpoints and canonical principals.
- states: probable vs confirmed.

4. Derived ranking/search projections
- disposable projections generated from canonical truth.
- rebuildable from events + lake.

5. Historical lineage artifacts
- immutable event and snapshot history for replay/audit.

## 4) Tier Definitions

### 4.1 Hot Tier
Storage: PostgreSQL/Citus
Use:
- live app behavior,
- ownership/dispute enforcement,
- current scoring inputs.

Contains:
- active edges,
- recently changed edges,
- active canonical links,
- sync session progress metadata,
- recent provenance references.

SLO intent:
- low-latency reads/writes,
- strict consistency for authoritative state.

### 4.2 Warm Tier
Storage: PostgreSQL partitions and/or warm object storage projections
Use:
- recent historical analysis,
- quick replay windows,
- dispute investigations.

Contains:
- stale/dormant edges,
- recently archived edge history,
- prior canonical-link confidence states,
- score input windows not needed in hot path.

SLO intent:
- moderate-latency access,
- fast replay of recent windows.

### 4.3 Cold Tier
Storage: Iceberg/Parquet on object storage
Use:
- long-horizon replay,
- forensic audit,
- calibration/research datasets,
- cost-efficient retention.

Contains:
- immutable historical snapshots/deltas,
- archived edge lineage,
- score run artifacts,
- dispute outcome lineage.

SLO intent:
- throughput over latency,
- full reproducibility over interactivity.

## 5) Edge Lifecycle State Model
State applies to directed edge records in canonical graph domain.

1. `observed_new`
- newly ingested edge from contact sync evidence.

2. `active_confirmed`
- currently valid and freshness-positive edge.

3. `active_probable`
- edge usable with reduced trust weight pending stronger confirmation.

4. `stale_decay`
- edge retained but decaying influence due to age/inactivity.

5. `dormant`
- no longer used for hot computations; available for reversibility and dispute context.

6. `archived`
- moved to cold lineage dataset; not used in hot/warm serving.

7. `tombstoned`
- deletion marker retained for replay/order integrity.

## 6) Transition Rules (Tier + State)

### 6.1 Ingestion Path
- `observed_new` -> `active_probable` when dedup confidence exists but not confirmed.
- `observed_new` -> `active_confirmed` when confirmation threshold met.

### 6.2 Freshness Decay Path
- `active_*` -> `stale_decay` when freshness age exceeds threshold.
- `stale_decay` -> `dormant` when age exceeds dormant threshold.
- `dormant` -> `archived` on archive job schedule.

### 6.3 Recovery Path
- `stale_decay` or `dormant` -> `active_confirmed` when new strong evidence arrives.
- `archived` -> `dormant` via replay restore when dispute/recovery requires reactivation.

### 6.4 Deletion Path
- any state -> `tombstoned` on valid deletion/legal/privacy command.
- tombstones retained long enough to preserve replay correctness and dedupe safety.

Rule:
- state transitions are event-driven and auditable; no silent mutation.

## 7) Default Lifecycle Thresholds (V1)
These are operational defaults and can be tuned by guardrail review.

- Fresh threshold (`active`): <= 90 days since last strong evidence.
- Decay window (`stale_decay`): 91-365 days.
- Dormant window (`dormant`): 366-730 days.
- Cold archive target: > 730 days (or sooner when storage pressure triggers).

Notes:
- Sensitive dispute-linked edges can be retained warm longer for safety and reversibility.
- High-risk ownership cases can pin associated lineage in warm tier until case closure + observation window.

## 8) Freshness and Ranking Influence

1. Edge freshness contributes to ranking weight.
2. `active_confirmed` edges have full allowed influence.
3. `active_probable` edges have capped influence.
4. `stale_decay` edges have decaying influence toward zero.
5. `dormant` and `archived` edges do not contribute to live ranking.

Mandatory constraint:
- shadow-profile-only edges never contribute to ranking regardless of freshness.

## 9) Privacy, Reversibility, and Retention

Privacy principles:
- no hidden-channel leakage from canonical linkage,
- policy-filtered serving always enforced,
- deletion and dispute actions are auditable.

Reversibility principles:
- raw evidence and transition lineage must remain reconstructable,
- merge/split actions are reversible,
- transferred/recovered ownership timelines are replayable.

Retention baseline (until legal matrix is finalized):
- hot: only current + operationally recent records,
- warm: active reversibility horizon,
- cold: long-term immutable lineage with policy-controlled access.

## 10) Replay Contract by Tier

### Hot replay
- targeted replay of recent command/event windows.
- used for projection repair and immediate incident response.

### Warm replay
- bounded replay for recent months and dispute forensics.
- used for model drift correction and merge/split correction.

### Cold replay
- full historical reconstruction for audit, research, and major recovery.
- used for deterministic full-graph recomputation.

Replay authorization:
- follow approved policy in `docs/plan/freeze/ARCH_DECISION_CLOSURE_V1.md` (R1/R2/R3).

## 11) Scale-Band Behavior
Align with record bands from guardrails.

B1 (`<=100M` records):
- hot-heavy operation, simple warm backlog, periodic cold archive.

B2 (`100M-1B`):
- stronger decay/archival cadence,
- structured warm partitions,
- frequent incremental replay checks.

B3 (`1B-10B`):
- continuous archival pipeline,
- aggressive dormant demotion,
- replay scope isolation by owner/bucket.

B4 (`>10B`):
- strict hot budget,
- warm window minimized to operational necessities,
- cold tier as primary historical source.

## 12) Observability Requirements
Track at minimum:
1. edge counts by state (`active`, `stale_decay`, `dormant`, `archived`, `tombstoned`),
2. transition throughput and failures,
3. freshness-age percentile by cohort,
4. replay success/divergence rates,
5. archive lag and cold-write failure rates,
6. rank-input edge volume by class and freshness state.

Alert examples:
- stale backlog growth above threshold,
- archive lag beyond window,
- replay divergence above tolerance,
- hot tier growth trend risking capacity boundary.

## 13) Failure and Recovery Playbook Hooks

Scenario A: Hot tier bloat spike
- accelerate stale->dormant demotion,
- increase archive throughput,
- temporarily tighten ingestion for whale owners.

Scenario B: Archival pipeline failure
- keep warm retention extended,
- pause destructive compaction,
- prioritize recovery replay checks.

Scenario C: Incorrect demotion logic
- replay warm/cold lineage to rebuild hot-state sets,
- disable transition job until validation passes.

## 14) Exit Criteria
`rin-3i0.5.1` is complete when:
- hot/warm/cold definitions are explicit,
- edge/state transitions are defined and auditable,
- freshness/decay/archive thresholds are documented,
- replay contract is mapped by tier,
- observability hooks are defined for operations.
