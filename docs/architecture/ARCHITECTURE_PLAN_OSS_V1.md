# Rin OSS Architecture Plan (High-Level, App-First)

## 1) Goals and Constraints

- Open-source-first stack only.
- Single-operator friendly: minimal always-on systems.
- Built for graph growth without re-platforming.
- Keep transactional truth and graph computation separated.

Core stack decision:
- Live OLTP: PostgreSQL now, Citus when needed.
- Event/task backbone: NATS JetStream.
- Passive/compute storage: Iceberg tables in Parquet (object storage).
- Graph compute: Spark batch + incremental.
- Score serving: write back to PostgreSQL.
- User search: PostgreSQL FTS at small scale, OpenSearch (or Meilisearch) when needed.

---

## 2) End-to-End System Map (Start at User App)

```text
[iOS/Android App]
  -> [API Gateway/BFF]
      -> [Identity + Verification Service]
      -> [Contacts Sync Service]
      -> [Circle/Policy Service]
      -> [Profile/Directory Service]
      -> [Search API]
      -> [Score API]

Services write OLTP truth to PostgreSQL/Citus
Services publish domain events to NATS JetStream

NATS consumers:
  -> Search Indexer -> OpenSearch/Meilisearch
  -> Lake Writer -> Iceberg/Parquet
  -> Fraud/Abuse Workers -> PostgreSQL flags/actions
  -> Notification Workers -> push/email/SMS

Spark jobs read Iceberg snapshots + deltas:
  -> dedup/canonical graph
  -> incremental rank
  -> full recompute
  -> explainability artifacts

Spark outputs:
  -> Score tables in PostgreSQL (online serving)
  -> Historical outputs in Iceberg (audit/replay)
```

---

## 3) What Overlaps with What

The same event stream feeds multiple planes:

- `contact.upserted`:
  - Updates OLTP contact state.
  - Updates search index.
  - Updates graph delta in lake.
  - Triggers incremental scoring queue.

- `identity.verified`:
  - Rebinds dedup confidence and ownership state.
  - Re-indexes public directory projection.
  - Triggers rank recompute for impacted neighborhood.

- `circle.policy_changed`:
  - Updates access-control projections.
  - Regenerates reachable channels for search/view responses.
  - Can trigger score/explainability recalculation (low priority).

Design rule:
- OLTP is source of truth for current product behavior.
- Iceberg is source of truth for historical reproducibility and compute replay.
- Search index is disposable/derivable projection.

---

## 4) Core Infrastructure Plan

### A. App + API Layer

- Mobile apps call BFF/API gateway.
- BFF enforces auth, rate limits, idempotency keys, and request shaping.
- Keep API layer stateless for horizontal scaling.

### B. Transaction Layer (PostgreSQL -> Citus)

- Start with PostgreSQL primary + replica.
- Use logical replication/outbox pattern to publish events to NATS.
- Promote to Citus when write/read pressure or table size requires sharding.

### C. Queue/Event Layer (NATS JetStream)

- NATS subjects for domain events and async tasks.
- JetStream for persistence + replay + backpressure handling.
- Keep task workers idempotent; retries are normal.

### D. Passive Data + Compute Layer (Iceberg + Spark)

- Land immutable deltas/snapshots in Iceberg (Parquet files).
- Spark pipeline stages:
  - ingestion normalization,
  - canonical edge build,
  - incremental score refresh,
  - periodic full recompute.
- Preserve run metadata for exact replay and score audits.

### E. Search Layer

- Phase 1: PostgreSQL FTS + trigram for name/username lookup.
- Phase 2: OpenSearch (or Meilisearch if simplicity is priority).
- Search index contains only policy-safe searchable projections.

### F. Serving Layer

- APIs read score + explainability from PostgreSQL serving tables.
- Redis cache optional for hot reads (profile/search snippets).

### G. Platform/Ops Layer

- Object storage with versioning for lake and backups.
- Metrics/logs/traces (Prometheus + Grafana + Loki/OpenTelemetry).
- Backups + restore drills (PostgreSQL base backups + WAL archive, Iceberg snapshot retention).

---

## 5) Data Flow (Back and Forth)

### Flow 1: New User Onboarding
1. App verifies phone.
2. Identity service writes user + verified channel to PostgreSQL.
3. Event published to NATS.
4. Search projection updated.
5. Lake projection updated for future graph jobs.

### Flow 2: Contacts Sync
1. App uploads hashed/raw contact payload (as policy allows).
2. Contacts service computes diff, writes only changes.
3. `contact.upserted` events emitted.
4. Search and lake projections update.
5. Incremental rank task enqueued.

### Flow 3: Discover/Search User
1. App calls Search API.
2. Search API queries PG FTS/OpenSearch.
3. Policy service filters fields by relationship/circle access.
4. Response includes only allowed channels/fields.

### Flow 4: Score Update + Serve
1. Spark incremental jobs consume new graph deltas from Iceberg.
2. Recompute impacted rank partitions.
3. Write fresh scores + explainability summaries to PostgreSQL.
4. App reads score instantly from serving tables.
5. Daily official snapshot is published from stable run.

---

## 6) Why This Avoids Rebuilds

- PostgreSQL and Citus keep SQL model stable from day 1 to larger scale.
- NATS decouples product writes from async compute/index work.
- Iceberg keeps historical compatibility across Spark job versions.
- Search stays projection-only, so replacing engine is low-risk.
- Scoring logic evolves in Spark without breaking app OLTP schema.

---

## 7) Benchmark Model (Records, Not Users)

Assumptions for benchmark below:
- `records` = directed contact edges.
- Average contacts/user = 140.
- DAU = 20% of users.
- API requests per DAU/day = 30.
- Daily contact scans = 20% of total records.
- Daily net record mutations after diff = 1%.
- Full rank run = 25 iterations over full graph.
- Incremental rank/day budget modeled as: `mutations * 40 impacted-edge multiplier * 8 local iterations`.

### 7.1 Workload Size by Record Count

| Records | Est. Users | DAU | API Avg QPS | API Peak QPS (x3) | Daily Scanned Records | Daily Mutated Records |
|---:|---:|---:|---:|---:|---:|---:|
| 10M | 71k | 14k | 5 | 15 | 2.0M | 100k |
| 100M | 714k | 143k | 50 | 149 | 20M | 1.0M |
| 1B | 7.1M | 1.4M | 496 | 1,488 | 200M | 10M |
| 10B | 71.4M | 14.3M | 4,960 | 14,881 | 2.0B | 100M |

### 7.2 Graph Compute Operations

| Records | Full Rank Edge Visits/Day (`25*R`) | Incremental Edge Visits/Day (model) |
|---:|---:|---:|
| 10M | 250M | 32M |
| 100M | 2.5B | 320M |
| 1B | 25B | 3.2B |
| 10B | 250B | 32B |

### 7.3 Memory Footprint (Graph Runtime)

Two memory models:
- Raw model: ~24 bytes/edge, ~2.25x runtime overhead.
- Optimized model (compact IDs + quantized ranks): ~10 bytes/edge, ~1.8x overhead.

| Records | Raw Runtime Memory | Optimized Runtime Memory |
|---:|---:|---:|
| 10M | ~0.0005 TiB | ~0.00016 TiB |
| 100M | ~0.0049 TiB | ~0.0016 TiB |
| 1B | ~0.049 TiB | ~0.016 TiB |
| 10B | ~0.491 TiB | ~0.164 TiB |

Important context:
- 10B records is far smaller than the earlier “9B users * 140 contacts” scenario.
- This benchmark is exactly for record counts requested here.

---

## 8) Operational Runbook by Scale (What Must Run)

### 10M Records
- Always on: API/BFF, PostgreSQL, NATS, basic workers.
- Search: PostgreSQL FTS.
- Compute: nightly incremental + weekly full rank Spark run.
- Ops focus: backup/restore automation, idempotency, replay validation.

### 100M Records
- Always on: PostgreSQL + read replica, NATS JetStream 3-node, dedicated worker pools.
- Search: move to OpenSearch or Meilisearch.
- Compute: hourly incremental + daily full rank.
- Ops focus: queue lag SLOs, partitioning strategy, search reindex playbook.

### 1B Records
- Always on: Citus cluster, NATS 5-node, search cluster (multi-node), Spark persistent cluster.
- Compute: continuous incremental + daily full + weekly calibration full run.
- Ops focus: cost controls, partition hot-spot management, DR drills.

### 10B Records
- Always on: Citus larger shard topology, larger NATS/search clusters, Spark autoscaling workers.
- Compute: continuous incremental, daily official score cut, weekly full graph correction.
- Ops focus: strict SLO/error budgets, automated capacity checks, staged rollouts for scoring model changes.

---

## 9) Option Exploration Summary (OSS Only)

- **Keep as primary path:** PostgreSQL/Citus + NATS + Iceberg/Parquet + Spark + OpenSearch/Meilisearch.
- **Viable alternatives:**
  - FoundationDB for transactional core (higher ops complexity).
  - Cassandra for adjacency-heavy serving plane (weaker transactional ergonomics for product logic).
  - Flink instead of Spark for stronger streaming-first compute.
- **Not recommended for solo simplicity right now:** multi-database “all-at-once” topology in v1.

---

## 10) Next Architecture Artifact (After This Doc)

Do next:
1. Deployment topology diagram (single-region v1).
2. Event contract catalog (subjects, producers, consumers, replay policy).
3. SLO sheet (API latency, queue lag, rank freshness, search freshness).
4. Capacity guardrails (when to move PG -> Citus; PG FTS -> OpenSearch).
