# Deployment Topology V1 (Planning Spec)

## 1. Purpose
Define environment topology and service placement for dev/staging/prod with clear promotion and rollback behavior.

Linked beads:
- `rin-3i0.9.1`
- `rin-3i0.9.2`
- `rin-3i0.4.4`

## 2. Environments

### 2.1 Development
- Single-tenant internal environment.
- Reduced dataset and compute cadence.
- Fast iteration; lower durability requirements.

### 2.2 Staging
- Production-like topology.
- Migration rehearsal and load replay tests.
- Release candidate validation and incident drill checks.

### 2.3 Production
- Hardened security controls.
- Controlled deploy windows and rollback paths.
- SLO-driven change approval.

## 3. Runtime Components
Core services (Go/Fiber):
1. API gateway/application edge.
2. Identity/ownership service.
3. Contacts/circles service.
4. Profile service.
5. Dispute/trust service.
6. Ranking orchestration service.
7. Search/query projection service.

Messaging/data plane:
- PostgreSQL (OLTP, outbox).
- NATS JetStream (event transport).
- Object storage + Iceberg/Parquet (batch/analytics).
- Spark compute (rank/search pipelines).
- Search engine when trigger reached (PG FTS first, external engine later).

## 4. Network and Trust Boundaries
Zones:
1. Public edge zone (API ingress).
2. Private app zone (services).
3. Data zone (DB, queue, storage).
4. Ops zone (admin tooling, observability, backup controls).

Rules:
- No direct public access to data-plane services.
- Service-to-service communication must be authenticated and logged.
- Operator privileged access is audited and time-bound.

## 5. Deployment Promotion Model
Pipeline stages:
1. Build and static checks.
2. Contract validation (schema/event compatibility checks).
3. Staging deploy.
4. Smoke + regression + replay tests.
5. Controlled production rollout.

Rollout policy:
- Start with canary slice.
- Promote only if SLI deltas remain within guardrails.
- Auto-halt on elevated error rate or latency regression.

## 6. Rollback Strategy
Rollback points:
1. Service binary rollback.
2. Feature-flag rollback.
3. Consumer pause/restart and replay rollback.
4. Migration rollback (expand/contract strategy only).

Rule:
- No irreversible schema/data migration without tested fallback path.

## 7. Secrets and Config Management
Minimum model:
- Centralized secret store.
- Short-lived credentials where possible.
- Per-environment config layering.
- Rotation schedule with expiry alarms.

Never:
- hardcode secrets in repo,
- share production secrets across environments.

## 8. Capacity and Scale Trigger Baseline
Use scale guardrails from:
- `docs/architecture/SCALE_GUARDRAIL_CONTRACT_V1.md`

Planning baseline:
- Start with PostgreSQL + NATS + PG FTS.
- Introduce Citus/search cluster only on sustained trigger thresholds.
- Keep compute workloads isolated from OLTP hot path.

## 9. Backup, Recovery, and Drills
Requirements:
- Daily OLTP snapshots + WAL/archive strategy.
- Periodic restore drills in staging.
- Event replay rehearsal with deterministic checks.
- Recovery objectives (RPO/RTO) tracked in runbook.

Reference:
- `docs/operations/SYSTEM_RUNBOOK_V1.md`

## 10. Exit Criteria
This planning spec is complete when:
- environment topology is accepted,
- promotion/rollback flow is defined,
- secrets/config policy is accepted,
- backup/recovery drill cadence is documented,
- `rin-3i0.9.1` and `rin-3i0.9.2` are ready for implementation breakdown.
