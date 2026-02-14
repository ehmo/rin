# Scale Guardrail Contract V1

## 1) Purpose

Define objective thresholds and operational actions for scaling transitions in Rin.

This contract prevents ad-hoc scaling decisions by specifying:
- entry criteria,
- required preparatory actions,
- cutover steps,
- rollback criteria,
- post-cutover validation.

Scope:
- PostgreSQL -> Citus transition,
- PostgreSQL FTS -> OpenSearch/Meilisearch transition,
- ingest throttling and partition hardening,
- dispute pipeline hardening,
- score pipeline cadence/partition adjustments.

---

## 2) Operating Modes

- `Mode S` (Starter): single Postgres primary + replica, PG FTS, on-demand Spark.
- `Mode G` (Growth): larger Postgres footprint, JetStream 3-node, external search projection, scheduled Spark incremental.
- `Mode D` (Distributed): Citus, JetStream 5-node, dedicated search cluster, continuous incremental score pipeline.

Mode progression must be monotonic unless rollback criteria trigger.

---

## 3) Core Metrics and SLO Baselines

## 3.1 API

- API p95 latency target: < 250 ms for read endpoints.
- API p99 latency target: < 600 ms for read endpoints.
- 5xx error rate target: < 0.5%.

## 3.2 PostgreSQL/Citus

- writer CPU sustained threshold: 70% (warn), 80% (action).
- writer storage growth threshold: >10% per week sustained.
- lock wait p95 threshold: >200 ms sustained.
- replication lag threshold: >3s sustained (warn), >10s (action).

## 3.3 NATS JetStream

- consumer lag threshold (core): >30s sustained (warn), >120s (action).
- redelivery ratio threshold: >1.5% sustained.
- DLQ rate threshold: >0.1% of total events sustained.

## 3.4 Search

- search p95 latency target: < 300 ms.
- stale index lag target: < 60s normal, < 5m degraded.
- search miss-drift threshold (index vs source mismatch): >0.5% sampled docs.

## 3.5 Score Pipeline

- incremental freshness target: < 2h.
- daily official snapshot completion target: before publish window.
- recompute failure threshold: >2 consecutive failed runs.

## 3.6 Security/Dispute

- case open-to-first-action p95 target: < 15m high severity.
- unresolved high-severity case age threshold: >24h (action).
- dispute queue backlog threshold: >4h projected wait (action).

---

## 4) Scale Trigger Matrix

## 4.1 Postgres Vertical Scale Trigger

Trigger if any 7-day sustained condition:
1. writer CPU > 70% for >30% of peak hours,
2. API read p95 breaches with DB wait as top contributor,
3. lock wait p95 > 200 ms,
4. storage growth projects exhaustion in <90 days.

Action:
- scale vertically and tune indexes/queries before architectural transition.

## 4.2 PG Partition Hardening Trigger

Trigger if any:
1. top 1% owners generate >20% write volume,
2. per-owner ingest burst causes hot partition warnings >1% of sync sessions,
3. row churn hotspots dominate vacuum/autovacuum pressure.

Action:
- enforce owner+bucket partition strategy,
- enforce owner-level ingest quotas,
- enable resumable sync chunking.

## 4.3 PG -> Citus Transition Trigger

Trigger when 2+ conditions hold for 14 days after vertical/partition tuning:
1. writer CPU > 80% sustained,
2. read replica lag > 10s sustained at peak,
3. total edge/contact tables exceed 70% practical single-node envelope,
4. shardable high-volume writes remain hotspot-prone,
5. maintenance windows can no longer complete safely.

Action:
- execute Citus migration plan (Section 6.1).

## 4.4 PG FTS -> External Search Trigger

Trigger when any 2 conditions hold for 7 days:
1. search p95 > 300 ms under normal load,
2. FTS query CPU dominates writer/reader pressure,
3. indexing lag > 60s sustained,
4. shadow/business class projection complexity causes query plan instability.

Action:
- cut over to OpenSearch/Meilisearch projection.

## 4.5 NATS Topology Upgrade Trigger

- Upgrade to 3-node JetStream if core stream lag > 120s for >3 events/day.
- Upgrade to 5-node when redelivery ratio >1.5% or replay windows exceed retention comfort.

## 4.6 Dispute Pipeline Hardening Trigger

Trigger when:
1. projected high-severity queue wait >4h,
2. >5% of high-severity cases miss SLA for 3 days,
3. reassignment/hijack case volume spikes >2x baseline.

Action:
- stricter auto-adjudication for low-risk cases,
- temporary capability restrictions by policy,
- dedicated queue lane and on-call escalation.

## 4.7 Score Pipeline Scaling Trigger

Trigger when:
1. incremental freshness misses >2h target for 2 consecutive intervals,
2. full run misses publish window twice in 7 days,
3. replay/recovery exceeds maintenance window.

Action:
- increase Spark parallelism,
- partition score jobs by impacted subgraph,
- separate score and graph trigger streams if coupled lag persists.

---

## 5) Guardrail Actions by Scale Band (Records)

Scale bands (records, not users):
- B1: <=100M
- B2: 100M-1B
- B3: 1B-10B
- B4: >10B

## B1
- Mode S default.
- PG FTS acceptable.
- Nightly incremental + daily/weekly full score schedule.

## B2
- Mode G transition likely.
- Enforce owner-bucket writes and stricter ingest quotas.
- Move search to external engine if thresholds breach.
- JetStream 3-node baseline.

## B3
- Mode D likely.
- Citus adoption required if sustained write/read pressure remains high.
- JetStream 5-node baseline.
- Continuous incremental scoring.

## B4
- Full distributed mode mandatory.
- Dedicated dispute SRE/ops lane required.
- Aggressive stale-edge decay and recompute partitioning.

---

## 6) Transition Playbooks

## 6.1 PostgreSQL -> Citus

Preconditions:
1. shard key strategy approved (owner/bucket oriented).
2. dual-write or migration cutover path tested in staging.
3. read/query compatibility report complete.

Cutover:
1. backfill shards,
2. validate row counts/checksums,
3. switch write path,
4. monitor lag/error metrics,
5. decommission legacy path after soak period.

Rollback criteria:
- correctness mismatch >0.1% sampled,
- sustained write failure spike >1%,
- unacceptable latency regression >25% p95.

## 6.2 PG FTS -> External Search

Preconditions:
1. projection event pipeline stable,
2. sampled relevance parity validated,
3. policy filters validated on read path.

Cutover:
1. full reindex,
2. dual-read compare window,
3. switch primary search backend,
4. retain PG FTS fallback for emergency.

Rollback criteria:
- index drift >0.5%,
- p95 latency regression >30%,
- policy leakage incident.

## 6.3 Ingest Hardening Cutover

Preconditions:
- resumable sync sessions enabled,
- owner-level quota policy published,
- customer-visible sync status UI present.

Cutover:
1. enable owner write caps,
2. enable owner+bucket partition path,
3. monitor hot partition and sync completion metrics.

Rollback criteria:
- sync failure rate >2x baseline for 24h without hotspot relief.

---

## 7) Edge-Case Guardrails

1. Whale owner (1M contacts) repeated syncs.
- apply strict owner quota + deferred non-critical projections.

2. Rapid phone reassignment wave.
- tighten transfer holds temporarily,
- prioritize C1/C2 case queue lanes.

3. Shadow profile spam wave.
- freeze new public discoverability for shadow class,
- enforce trust-gated shadow actions.

4. Business admin compromise cluster.
- org-wide high-risk action freeze + forced authority re-validation.

5. Replay storm after outage.
- isolate replay consumer group and cap replay rate to protect live traffic.

---

## 8) Governance and Review Cadence

- Weekly review: core SLO breaches and leading indicators.
- Monthly review: scale band status and pending transitions.
- Quarterly review: threshold recalibration from observed production data.

Any threshold changes require:
1. reasoned proposal,
2. simulated impact estimate,
3. rollback plan.

---

## 9) Required Dashboards

1. API latency/error dashboard.
2. Postgres/Citus capacity and lock dashboard.
3. JetStream lag/redelivery/DLQ dashboard.
4. Search freshness and drift dashboard.
5. Score pipeline freshness/completion dashboard.
6. Dispute queue SLA dashboard.

---

## 10) Open Decisions

1. Exact practical single-node Postgres envelope for your hardware budget.
2. Preferred external search engine default (OpenSearch vs Meilisearch).
3. Maximum acceptable sync duration for whale owners after throttling.
4. Whether to auto-trigger temporary stricter dispute holds during reassignment spikes.
5. Whether B4 requires dedicated human review team before launch.
