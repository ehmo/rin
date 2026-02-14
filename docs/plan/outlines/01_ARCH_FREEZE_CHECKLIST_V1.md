# Architecture Freeze Checklist V1

## 1. Purpose
Define objective criteria for `ARCH_FREEZE_V1` so implementation starts only after core contracts are coherent, signed, and operationally defensible.

Linked beads:
- `rin-3i0.1.1`
- `rin-3i0.1.2`
- `rin-3i0.1.3`

## 2. Freeze Scope
`ARCH_FREEZE_V1` covers only Phase 0/Phase 1 foundations for v1:
- identity, ownership, contacts, circles, dispute, and rank contracts,
- event semantics and replay behavior,
- service ownership boundaries,
- deployment/observability planning baseline.

Out of scope for freeze:
- Phase 2/3/4 roadmap features (media/location/information),
- full endpoint-level API details,
- implementation-level table/index tuning.

## 3. Decision Closure List (Must Be Closed)
Status options: `closed`, `deferred_with_guardrail`, `blocked`.

1. Hold windows by risk level and jurisdiction.
2. Shadow profile limits and friction rules.
3. Business authority proof strictness in v1.
4. External search default (`OpenSearch` vs `Meilisearch`) and transition trigger.
5. Maximum acceptable whale-sync duration under throttle controls.
6. Replay authorization policy for operator-triggered reprocessing.

Acceptance rule:
- No item can remain `blocked` at freeze time.
- Any `deferred_with_guardrail` item must include explicit trigger, owner, due date, and fallback behavior.

## 4. Contract Completeness Checklist
Required docs must be internally consistent and cross-referenced.

1. `docs/architecture/SYSTEM_ARCHITECTURE_DB_FIRST_V2.md`
2. `docs/architecture/OWNERSHIP_STATE_MACHINE_SPEC_V1.md`
3. `docs/architecture/EVENT_CONTRACT_CATALOG_V1.md`
4. `docs/architecture/PROFILE_CLASS_CONTRACT_V1.md`
5. `docs/architecture/SCALE_GUARDRAIL_CONTRACT_V1.md`
6. `docs/architecture/DATA_MODEL_BOUNDARIES_V1.md`
7. `docs/operations/DISPUTE_PLAYBOOK_V1.md`
8. `docs/operations/SYSTEM_RUNBOOK_V1.md`
9. `docs/plan/outlines/02_API_SURFACE_OUTLINE_V1.md`
10. `docs/plan/outlines/03_DEPLOYMENT_TOPOLOGY_OUTLINE_V1.md`
11. `docs/plan/outlines/04_OBSERVABILITY_ALERTING_OUTLINE_V1.md`

Each required doc must include:
- scope and assumptions,
- explicit invariants (must/never),
- failure/rollback behavior,
- owner and update policy,
- links to related contracts.

## 5. Risk Acceptance Register (Freeze Artifact)
Create or update: `docs/plan/freeze/ARCH_FREEZE_V1_RISK_REGISTER.md`.

Required fields per risk entry:
- `risk_id`
- `description`
- `impact` (`product`, `security`, `ops`, `compliance`, `cost`)
- `likelihood`
- `mitigation`
- `temporary_guardrail`
- `owner`
- `review_date`
- `acceptor`

Rule:
- Every unresolved risk at freeze time must be explicitly accepted by named owner(s).

## 6. Sign-Off Matrix
Minimum approvers:
1. Product/Founder owner: product behavior, UX consequences.
2. Architecture owner: contract consistency, boundary integrity.
3. Operations owner: incident and replay operability.
4. Security/trust owner: abuse/dispute/hijack controls.

Single-founder mode:
- One person can hold all roles, but sign-off must still be recorded per role.

## 7. Freeze Procedure
1. Run decision closure review against Section 3.
2. Validate document completeness against Section 4.
3. Record unresolved risks using Section 5.
4. Execute sign-off log in `docs/plan/freeze/ARCH_FREEZE_V1_SIGNOFF.md`.
5. Create freeze marker document `docs/plan/freeze/ARCH_FREEZE_V1.md` containing:
   - included docs and versions,
   - deferred items with guardrails,
   - sign-off timestamp.
6. Update beads statuses:
   - close `rin-3i0.1.1` when decisions closed,
   - close `rin-3i0.1.2` when sign-off procedure is complete.

## 8. Post-Freeze Change Control
Any change touching frozen contracts requires a short ADR entry with:
- reason for change,
- impacted docs/services,
- migration and rollback impact,
- approval by architecture + operations roles.

Severity policy:
- `critical`: security/compliance/irreversible data risk -> immediate hot-change allowed with post-hoc ADR in 24h.
- `normal`: scheduled to weekly architecture review.

## 9. Exit Criteria
`ARCH_FREEZE_V1` is achieved when all are true:
- Section 3 items are closed or deferred with guardrails.
- Section 4 checklist is complete.
- Risk register and sign-off docs exist.
- `docs/architecture/ARCHITECTURE_MASTER_INDEX.md` references freeze state.
- `rin-3i0.1.1` and `rin-3i0.1.2` are closed.
