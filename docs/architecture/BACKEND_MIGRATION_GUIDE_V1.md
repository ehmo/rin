# Backend Migration Guide V1 (Monolith → Distributed)

## 1) Purpose

Step-by-step migration procedure for transitioning the backend from modular monolith (Stage A) through worker extraction (Stage B) to full service split (Stage C). Includes triggers, data migration, traffic shifting, rollback plans, and resiliency model.

Companion docs:
- `docs/architecture/SERVICE_IMPLEMENTATION_BLUEPRINT_V1.md` (service map)
- `docs/architecture/SYSTEM_ARCHITECTURE_DB_FIRST_V2.md` (architecture overview)

---

## 2) Stage Overview

```
Stage A: Modular Monolith (v1 launch)
├── Single Go binary
├── Logical domain boundaries (packages)
├── Shared PostgreSQL
├── NATS JetStream for async
├── Handles: 0-1,000 users
│
↓ Trigger: specific thresholds met
│
Stage B: Worker Extraction
├── API monolith (commands + queries)
├── Extracted workers:
│   ├── Score Orchestrator (batch compute)
│   ├── Search Projector (index updates)
│   └── Dispute Processor (queue drain)
├── Shared PostgreSQL
├── NATS JetStream (worker communication)
├── Handles: 1,000-10,000 users
│
↓ Trigger: specific thresholds met
│
Stage C: Service Split
├── API Gateway/BFF
├── Domain services (Identity, Contacts, Circles, etc.)
├── Workers (Score, Search, Dispute)
├── Per-domain DB schemas (logical split, physical shared)
├── NATS JetStream (inter-service events)
├── Handles: 10,000+ users
```

---

## 3) Stage A → B: Worker Extraction

### 3.1 Triggers (Any One Met)

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| Score batch duration | >30 minutes | Blocks API resources during compute |
| Search index update lag | >5 minutes | User sees stale search results |
| Dispute queue depth | >100 pending for >1 hour | Time-sensitive safety operations delayed |
| API p95 latency | >500ms during batch compute | Batch work degrades real-time performance |
| Daily active users | >1,000 | Scale trigger independent of symptoms |

### 3.2 Extraction Order

1. **Score Orchestrator** (highest impact, most isolated).
2. **Search Projector** (clearly separable, read-path optimization).
3. **Dispute Processor** (safety-critical, benefits from isolation).

### 3.3 Score Orchestrator Extraction

**Pre-migration:**
1. Ensure score computation logic is in a standalone Go package (`internal/score/`).
2. Verify NATS consumer for score triggers is cleanly separable.
3. Create score worker Dockerfile and deployment config.
4. Set up dedicated NATS consumer group for score worker.

**Migration steps:**
1. Deploy score worker alongside monolith (both running, worker idle).
2. Feature flag: route score trigger events to worker consumer group.
3. Verify: worker computes scores correctly (compare output to monolith).
4. Cutover: disable score computation in monolith, enable in worker.
5. Monitor: score batch duration, publish latency, error rate.
6. Stabilize for 72 hours before proceeding.

**Rollback:**
- Flip feature flag: re-enable score computation in monolith.
- Worker continues running but idle (no events routed).
- Rollback time: <5 minutes.

### 3.4 Search Projector Extraction

**Pre-migration:**
1. Isolate search index update logic into `internal/search/projector/`.
2. Create projector worker deployment.
3. Set up NATS consumer group.

**Migration steps:**
1. Deploy projector alongside monolith.
2. Route contact/circle change events to projector consumer group.
3. Verify: search index freshness matches monolith behavior.
4. Cutover: disable projection updates in monolith.
5. Monitor: index freshness lag, query latency.

**Rollback:** Same feature flag pattern. <5 minutes.

### 3.5 Dispute Processor Extraction

**Pre-migration:**
1. Isolate dispute processing into `internal/security/dispute/processor/`.
2. Create processor worker deployment.
3. Set up priority-aware NATS consumer (P0 disputes processed first).

**Migration steps:**
1. Deploy processor alongside monolith.
2. Route dispute events to processor consumer group.
3. Verify: auto-adjudication produces same outcomes.
4. Cutover: disable dispute processing in monolith.
5. Monitor: queue depth, resolution latency, auto-adjudication rate.

**Rollback:** Same pattern. <5 minutes.

---

## 4) Stage B → C: Service Split

### 4.1 Triggers (Any One Met)

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| Monolith deployment frequency | >3x/day desired | Different domains need different release cadences |
| API binary size | >200MB | Build times impacting iteration speed |
| Team size | >3 engineers | Conway's Law — services should match team boundaries |
| Cross-domain coupling bugs | >5 in 30 days | Logical boundaries insufficient, need physical isolation |
| Daily active users | >10,000 | Scale trigger |

### 4.2 Split Order

1. **Identity Service** (most critical, most isolated, fewest dependencies).
2. **Contacts Service** (high read volume, benefits from independent scaling).
3. **Circles Service** (closely coupled with Contacts, split together or immediately after).
4. **Security Service** (safety-critical, benefits from isolation).
5. **API Gateway/BFF** (extract after domain services exist).

### 4.3 Per-Service Split Procedure

For each service extraction:

**Phase 1: Database Schema Isolation (1 week)**
1. Create schema within shared PostgreSQL (e.g., `identity.`, `contacts.`).
2. Migrate tables to domain-specific schema.
3. Replace cross-schema queries with API calls or event-driven reads.
4. Verify: no direct cross-schema foreign keys remain.

**Phase 2: Service Deployment (1 week)**
1. Create service binary with domain-specific routes.
2. Deploy alongside monolith.
3. API Gateway routes domain-specific requests to new service.
4. Monolith stops handling those routes.
5. Verify: functional parity via integration tests.

**Phase 3: Traffic Shift (1 week)**
1. Route 10% of domain traffic to new service.
2. Compare: latency, error rate, data consistency.
3. Route 50% → 100% over 3 days.
4. Decommission domain code from monolith.

**Phase 4: Stabilization (1 week)**
1. Monitor for 7 days at 100%.
2. Tune resource allocation.
3. Document operational runbook for new service.

**Rollback at any phase:**
- Phase 1: Revert schema migration (reverse SQL).
- Phase 2: Remove service, restore monolith routes.
- Phase 3: Route 100% back to monolith.
- All rollbacks: <30 minutes.

---

## 5) Failure-Domain and Resiliency Model

### 5.1 Failure Domains (Stage A)

Single failure domain — if the monolith fails, everything fails.

Mitigations:
- Health check endpoint for load balancer.
- Graceful shutdown with in-flight request drain.
- Automatic restart via process manager.
- PostgreSQL connection pool with health checks.
- NATS JetStream replay on consumer restart.

### 5.2 Failure Domains (Stage B)

| Component | Blast radius | Mitigation |
|-----------|-------------|------------|
| API monolith | All user-facing operations | Redundant instances, health checks |
| Score worker | Score staleness (24h tolerance) | Dead-letter queue, manual trigger |
| Search projector | Search index staleness | Fallback to database query |
| Dispute processor | Dispute resolution delay | Priority queue ensures P0 processed first |
| PostgreSQL | Full outage | Managed service HA, automated failover |
| NATS | Async operations degraded | JetStream persistence, consumer replay |

### 5.3 Failure Domains (Stage C)

Each service is an independent failure domain. Cross-service communication via NATS (async) ensures one service failure doesn't cascade synchronously.

Circuit breaker pattern for any synchronous cross-service calls:
- Open after 5 failures in 30 seconds.
- Half-open after 60 seconds.
- Close after 3 successes.

### 5.4 Resiliency Patterns

| Pattern | When applied | Implementation |
|---------|-------------|----------------|
| **Retry with backoff** | Transient failures (5xx, timeout) | 3 retries, exponential backoff |
| **Circuit breaker** | Cross-service calls (Stage C) | Per-service breaker |
| **Bulkhead** | Resource isolation (DB pools, goroutines) | Per-domain connection pools |
| **Timeout** | All external calls | 5s default, 30s for batch operations |
| **Dead-letter queue** | Failed event processing | Per-consumer DLQ in NATS |
| **Idempotency** | All mutations | Idempotency key in command handler |
| **Graceful degradation** | Partial system failure | Serve cached/stale data with staleness indicator |

### 5.5 Data Consistency

| Stage | Consistency model |
|-------|------------------|
| A | Strong (single process, single DB) |
| B | Strong for API, eventual for worker outputs (projections lag by seconds) |
| C | Eventual consistency between services. Saga pattern for cross-domain transactions. |

---

## 6) Database Migration Safety

### 6.1 Migration Rules

1. **Never drop columns in production** — mark deprecated, remove after 2 release cycles.
2. **Add columns as nullable** — backfill, then add NOT NULL constraint.
3. **No long-running locks** — use `CREATE INDEX CONCURRENTLY`, avoid `ALTER TABLE` with table lock.
4. **Test migrations on staging** with production-like data volume.
5. **Backward-compatible migrations only** — old code must work with new schema during rollout.

### 6.2 Schema Change Procedure

1. Write migration SQL (up + down).
2. Test on staging with production dump.
3. Measure lock time and impact.
4. Deploy migration during low-traffic window.
5. Monitor for 1 hour post-migration.
6. If issues: run down migration.

---

## 7) Open Decisions

1. Whether to use PostgreSQL logical replication for per-service read replicas in Stage C or shared connection pooler.
2. Whether to introduce a service mesh (Consul Connect, Linkerd) in Stage C or rely on DNS-based discovery.
3. Whether the API Gateway in Stage C should be a custom Go service or an off-the-shelf solution (Kong, Traefik).
4. Exact NATS JetStream stream topology for multi-service event routing.
