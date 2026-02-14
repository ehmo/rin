# Observability and Alerting V1 (Planning Spec)

## 1. Purpose
Define SLI/SLO and alert policies that keep Rin operable and replay-safe during growth.

Linked beads:
- `rin-3i0.11.1`
- `rin-3i0.11.2`

## 2. Telemetry Standards
All services must emit:
1. Structured logs (zerolog format discipline).
2. Metrics (service, domain, queue, data pipeline).
3. Distributed traces (request and event propagation).
4. Correlation IDs linking API request -> command -> event -> projection update.

Operational requirements:
- Sentry for exception tracking and release correlation.
- Log fields standardized across services (`service`, `env`, `request_id`, `user_class`, `event_subject`).

## 3. Golden Signals by Domain

### 3.1 API/Command Plane
- request rate
- latency (p50/p95/p99)
- error rate
- saturation (CPU/memory/thread pools)

### 3.2 Event and Queue Plane
- publish/consume throughput
- consumer lag
- redelivery/retry rates
- dead-letter volume

### 3.3 Data/Projection Plane
- projection freshness lag
- rank publish duration
- indexing backlog
- replay completion time

### 3.4 Trust/Dispute Plane
- dispute queue depth by severity
- hold application latency
- auto-resolution rate
- escalated manual-review volume

## 4. Initial SLI/SLO Targets
Planning targets (to be tuned with live data):
1. API availability >= 99.9% monthly.
2. API p95 latency <= 300ms for core read queries.
3. Command acceptance p95 <= 500ms excluding async projection lag.
4. Event consumer lag p95 <= 60s in normal mode.
5. Critical projection freshness <= 5 min.
6. P0 dispute safeguards applied <= 2 min.

## 5. Alert Routing and Severity
Severity model:
- `P0`: user safety/security or widespread outage.
- `P1`: major degradation with user-visible impact.
- `P2`: partial degradation or elevated risk trend.
- `P3`: low urgency anomaly requiring review.

Routing policy:
- P0/P1: immediate pager + incident channel + owner ack.
- P2: on-call queue within business window.
- P3: backlog ticket with weekly review.

## 6. Required Dashboards
1. Service health overview.
2. Command success/error and transition failures.
3. JetStream throughput, lag, retries, DLQ.
4. Projection freshness and replay status.
5. Dispute/security operations dashboard.
6. Deployment impact dashboard (before/after diff).

## 7. Incident Snapshot Template
During incident capture:
- start time and detection source,
- affected domains and profile classes,
- top failing commands/events,
- customer impact estimate,
- immediate mitigation actions,
- next rollback/recovery decision point.

## 8. Replay and Recovery Observability
Must monitor:
1. replay start/end markers,
2. processed event count vs expected count,
3. idempotency conflict count,
4. projection divergence checks,
5. post-replay SLI stabilization window.

Rule:
- No replay considered complete until divergence checks pass.

## 9. Governance and Review Cadence
- Daily operational check (key SLI + queue lag + dispute backlog).
- Weekly reliability review (alert quality and noisy rules).
- Monthly SLO review and threshold recalibration.

## 10. Exit Criteria
This planning spec is complete when:
- SLI/SLO targets are accepted,
- alert routing policy is approved,
- dashboard minimum set is defined,
- replay observability checks are formalized,
- `rin-3i0.11.1` is ready for implementation plan.
