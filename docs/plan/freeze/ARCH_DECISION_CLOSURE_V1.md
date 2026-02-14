# Architecture Decision Closure V1 (High-Priority)

Status: `proposed_for_founder_signoff`
Linked bead: `rin-3i0.1.1`
Date: 2026-02-14

## Purpose
Close the high-priority architecture decisions required by `ARCH_FREEZE_V1` with explicit defaults and operational guardrails.

This document covers:
1. hold windows by risk/jurisdiction,
2. shadow profile limits and friction policy,
3. business authority proof strictness,
4. external search engine default,
5. whale sync maximum duration,
6. replay authorization policy.

## Decision Summary

| ID | Decision | Proposed Default | Status |
|---|---|---|---|
| AD-001 | Hold windows | `24h low`, `48h medium`, `72h high`; unknown jurisdiction defaults to high | proposed |
| AD-002 | Shadow profile limits | Unlimited creation; strict friction on discoverability/reach actions; never ranked | proposed |
| AD-003 | Business authority proof | Tiered: lightweight proof for create/manage, strict legal proof for transfer/dispute/high-risk | proposed |
| AD-004 | External search default | `PG FTS` in starter mode, `Meilisearch` as first external engine on trigger | proposed |
| AD-005 | Whale sync ceiling | Acceptable max completion: `24h` per full whale sync under safety throttles | proposed |
| AD-006 | Replay authorization | Two-person approval for production replays affecting identity/dispute/rank; full audit trail mandatory | proposed |

## AD-001: Hold Windows by Risk/Jurisdiction
### Proposed
- Low risk: `24h`
- Medium risk: `48h`
- High risk: `72h`
- If jurisdiction risk mapping is unknown: treat as `high risk` (72h)

### Rationale
- Balances safety and usability.
- Matches prior design assumptions in dispute and ownership flow.
- Provides deterministic behavior before jurisdiction-specific legal policy is finalized.

### Guardrails
- If carrier reassignment confidence is very high and no conflicting evidence exists, allow low-risk fast path with manual override audit.
- Any hold override requires reason code and operator ID.

## AD-002: Shadow Profile Limits and Progressive Friction
### Proposed
- Unlimited shadow profile creation (aligned with product direction).
- Default state: non-discoverable, non-ranked, no direct channel ownership.
- Progressive friction applies to risky actions, not creation:
  - cap daily public reachability changes,
  - cap outbound contact requests from shadow profiles,
  - require stronger account trust for high-volume action bursts.

### Rationale
- Preserves long-term product flexibility (unlimited pseudos).
- Controls abuse through action gating rather than hard profile-count limits.

### Guardrails
- Automatic temporary restrictions on abuse spikes.
- Dispute-triggered freeze on new shadow high-risk actions until cleared.

## AD-003: Business Authority Verification Strictness
### Proposed
- Tiered model in v1:
  - Tier A (low risk): verified domain email + existing authority chain.
  - Tier B (high risk actions: ownership transfer, dispute, top-level admin changes): legal-entity proof required.

### Rationale
- Keeps onboarding practical while protecting critical authority paths.
- Avoids high support overhead for every low-risk action.

### Guardrails
- If authority chain is ambiguous, enforce Tier B and temporary high-risk-action freeze.
- Mandatory session/token revocation after confirmed authority reversal.

## AD-004: External Search Default Engine
### Proposed
- Starter: PostgreSQL FTS.
- First external engine on trigger: `Meilisearch`.
- Escalate to `OpenSearch` only if sustained scale/feature thresholds demand it.

### Rationale
- Minimizes operational burden for single-founder operation.
- Preserves migration path to heavier engine when needed.

### Trigger Reference
- Use existing trigger contract in `docs/architecture/SCALE_GUARDRAIL_CONTRACT_V1.md`.

## AD-005: Whale Sync Maximum Duration
### Proposed
- Maximum acceptable completion window for whale full sync: `24 hours`.
- Internal targets:
  - p50 <= 2h
  - p95 <= 12h
  - hard ceiling 24h

### Rationale
- Protects platform stability while setting a clear UX boundary.
- Compatible with owner-level throttling and resumable chunked sync.

### Guardrails
- Show progressive sync state and expected completion windows.
- If projected to exceed 24h, system must auto-split and schedule deferred stages with user-visible status.

## AD-006: Replay Authorization Policy
### Proposed
Production replay classes:
- Class R1 (low risk, local projection replay): one approver + automatic logging.
- Class R2 (identity/dispute/rank impact): two-person approval required.
- Class R3 (cross-domain wide replay): two-person approval + explicit blast-radius record + post-replay reconciliation review.

### Rationale
- Prevents operator error in sensitive systems while retaining incident responsiveness.

### Guardrails
- Replay job must capture: actor, reason, scope, expected entity count, start/end, divergence results.
- Replay not complete until divergence checks pass.

## Approval Block
Set each decision to `approved` or `needs_change`.

- AD-001 Hold windows: `pending`
- AD-002 Shadow profile friction model: `pending`
- AD-003 Business authority strictness: `pending`
- AD-004 External search default: `pending`
- AD-005 Whale sync ceiling: `pending`
- AD-006 Replay authorization policy: `pending`

When all six are `approved`, close bead `rin-3i0.1.1`.
