# Ownership State Machine Spec V1

## 1) Purpose

Define strict state-transition contracts for channel ownership in Rin.

Scope:
- phone/email channel ownership,
- disputes and recovery,
- transfer and reassignment,
- operational safeguards.

Non-goals:
- UI copy details,
- physical schema design,
- cryptographic protocol implementation details.

---

## 2) Primary Entities

- `principal`: account holder (single user, business user, employee profile owner).
- `channel`: claimable endpoint (phone, email).
- `ownership_link`: relationship between principal and channel with state.
- `case`: dispute/security case associated with ownership_link.

Shadow rule:
- Shadow profiles never directly own channels.
- Shadow profiles may reference owner-principal channels via policy projection only.

---

## 3) Ownership States

Canonical ownership state values:

1. `unclaimed`
2. `claim_pending`
3. `verified_active`
4. `challenged`
5. `limited`
6. `disputed`
7. `transferred`
8. `recovered`
9. `revoked`

State semantics:

- `unclaimed`: no active verified owner.
- `claim_pending`: claim initiated; proof not complete.
- `verified_active`: current verified owner with normal capabilities.
- `challenged`: risk or competing claim detected; challenge required.
- `limited`: ownership remains but sensitive capabilities restricted.
- `disputed`: active case adjudication underway.
- `transferred`: ownership moved to another principal after adjudication.
- `recovered`: prior owner reinstated after challenge/dispute.
- `revoked`: ownership link explicitly invalidated (fraud/admin/legal).

---

## 4) Allowed Transitions

Only these transitions are valid:

1. `unclaimed -> claim_pending`
2. `claim_pending -> verified_active`
3. `claim_pending -> revoked`
4. `verified_active -> challenged`
5. `verified_active -> revoked`
6. `challenged -> limited`
7. `challenged -> verified_active`
8. `limited -> disputed`
9. `limited -> verified_active`
10. `disputed -> transferred`
11. `disputed -> recovered`
12. `disputed -> revoked`
13. `transferred -> challenged`
14. `recovered -> verified_active`
15. `revoked -> claim_pending`

Notes:
- `transferred` and `recovered` are terminal outcome markers for case resolution events and are followed by normalization into active flow (`verified_active` or new challenge if needed).
- A transition must include reason code and actor context.

---

## 5) Forbidden Transitions

All non-listed transitions are forbidden. Explicitly forbidden high-risk examples:

1. `verified_active -> transferred` without `disputed`.
2. `challenged -> transferred` without `disputed`.
3. `claim_pending -> transferred`.
4. `revoked -> verified_active` without new claim proof.
5. `unclaimed -> verified_active` bypassing claim proof.
6. `disputed -> verified_active` (must resolve to `transferred`, `recovered`, or `revoked`).

Invalid transition behavior:
- Reject with deterministic error code.
- Emit `ownership.transition.rejected` event.
- Record audit row with attempted transition and actor.

---

## 6) Transition Triggers and Preconditions

## T1: Start Claim (`unclaimed -> claim_pending`)

Preconditions:
- channel normalized and eligible,
- no active lock by unresolved severe case.

Required inputs:
- claimant principal,
- verification method requested.

## T2: Verify Claim (`claim_pending -> verified_active`)

Preconditions:
- proof challenge successful,
- anti-abuse checks pass,
- idempotency token valid.

## T3: Challenge Active Owner (`verified_active -> challenged`)

Triggers:
- competing verified claim,
- takeover signal,
- fraud detection threshold,
- user security report.

Preconditions:
- risk score above configured threshold or manual override by privileged actor.

## T4: Restrict (`challenged -> limited`)

Triggers:
- challenge timeout,
- high-confidence risk evidence.

Effect:
- freeze sensitive updates and high-impact actions.

## T5: Open Dispute (`limited -> disputed`)

Preconditions:
- case ID exists,
- evidence package created,
- hold window configuration attached.

## T6: Resolve Transfer (`disputed -> transferred`)

Preconditions:
- claimant proof complete,
- hold window complete,
- prior-owner notification sent,
- adjudication decision code present.

## T7: Resolve Recovery (`disputed -> recovered`)

Preconditions:
- incumbent proof complete,
- adjudication decision code present.

## T8: Revoke (`* -> revoked` where allowed)

Preconditions:
- fraud/legal/admin justification code,
- audit approval level satisfied.

---

## 7) Timers and Holds

Configurable default timers (v1 proposal):

- claim verification TTL: 15 minutes.
- challenge response window: 24 hours.
- high-risk transfer hold: 72 hours.
- low-risk transfer hold: 24 hours.
- post-resolution observation window: 7 days.

Timer expirations are stateful events:
- `ownership.timer.expired` with timer type and case/channel IDs.

---

## 8) Concurrency and Consistency Rules

Single-writer rule:
- one active state transition per channel at a time.

Concurrency control:
- optimistic version check on ownership_link.
- advisory lock on normalized channel key during transition transaction.

Conflict resolution:
- stale version write fails with retryable error.
- repeated transition request with same idempotency key returns prior result.

Ordering:
- case resolution transitions require monotonic event order by case version.

---

## 9) Idempotency and Replay Safety

Every transition command requires:

- `idempotency_key`
- `actor_id`
- `causation_id`
- `correlation_id`
- `requested_transition`

Rules:

1. Same key + same payload => return prior outcome.
2. Same key + different payload => reject with conflict error.
3. Replayed events must not trigger duplicate side effects.

---

## 10) Side-Effects by Transition

Mandatory side-effects are deterministic.

Examples:

- `verified_active -> challenged`
  - emit `ownership.challenged`
  - open or attach case
  - notify active owner
  - schedule challenge timer

- `challenged -> limited`
  - emit `ownership.limited`
  - apply capability freeze bundle L2/L3 by severity
  - request trust score downgrade

- `limited -> disputed`
  - emit `ownership.dispute_opened`
  - lock sensitive channel mutations

- `disputed -> transferred`
  - emit `ownership.transferred`
  - update reachability projections
  - trigger score recompute for impacted neighborhood
  - schedule post-transfer monitoring

- `disputed -> recovered`
  - emit `ownership.recovered`
  - restore capabilities by policy
  - trigger score recompute

- `* -> revoked`
  - emit `ownership.revoked`
  - remove positive-trust channel influence
  - enforce restrictive policy package

---

## 11) Capability Matrix by Ownership State

Capabilities:
- edit channel metadata,
- use channel for public reachability,
- contribute channel to trust-positive scoring,
- add shadow profile references to channel,
- transfer/rename sensitive handles,
- business delegated administration.

Policy by state:

- `verified_active`: all allowed by role.
- `challenged`: public reachability and sensitive edits restricted.
- `limited`: trust-positive contribution disabled; sensitive ops frozen.
- `disputed`: only remediation flows allowed.
- `transferred`: old owner loses capabilities immediately.
- `recovered`: capabilities restored with observation window constraints.
- `revoked`: all capabilities blocked except recovery/appeal.

---

## 12) Role and Authorization Model

Actors:

- principal owner,
- competing claimant,
- business org owner/admin,
- trust & safety operator,
- system automation.

Authorization principles:

1. Only trusted automation or authorized operators can force high-severity transitions.
2. Business delegate cannot overrule org owner on top-level ownership transfer.
3. Employee profiles cannot claim business primary channels without delegated authority.
4. Shadow profile cannot initiate channel claims.

---

## 13) Business-Specific Ownership Rules

1. Business channels are owned by business principal, not employee principal.
2. Employee offboarding auto-revokes delegated channel controls.
3. Business authority dispute forces temporary freeze on high-risk org actions.
4. Emergency break-glass path exists for compromised sole admin.

---

## 14) Observability and Audit Requirements

Every transition must log:

- old state,
- new state,
- transition reason code,
- actor and actor type,
- case ID,
- evidence reference IDs,
- request and outcome timestamps,
- idempotency/correlation/causation identifiers.

Metrics:

- transition rate per state edge,
- invalid transition attempts,
- case resolution latency,
- reversal rate,
- challenged->limited conversion rate,
- disputed outcome distribution.

Alerts:

- surge in `verified_active -> challenged`,
- surge in invalid transitions for same channel,
- transfer reversals above threshold,
- timer backlog growth.

---

## 15) Error Codes (Contract Level)

Suggested stable codes:

- `OWNERSHIP_INVALID_TRANSITION`
- `OWNERSHIP_PRECONDITION_FAILED`
- `OWNERSHIP_VERSION_CONFLICT`
- `OWNERSHIP_IDEMPOTENCY_CONFLICT`
- `OWNERSHIP_LOCK_CONFLICT`
- `OWNERSHIP_CASE_REQUIRED`
- `OWNERSHIP_HOLD_INCOMPLETE`
- `OWNERSHIP_UNAUTHORIZED`

---

## 16) Test and Simulation Requirements

Minimum test suites before production:

1. transition matrix test (all allowed/forbidden edges),
2. idempotency replay test,
3. concurrent claimant race test,
4. timer expiry transition test,
5. business authority offboarding test,
6. shadow profile claim rejection test,
7. rollback/reversal consistency test.

Simulation requirement:
- include extreme skew scenarios (1M-contact owner, 5-contact owner) and disputed channel race conditions.

---

## 17) Open Decisions

1. exact risk threshold tuning for auto-challenge.
2. default hold windows by jurisdiction and risk tier.
3. what level of evidence is exposed to users in-app.
4. strictness of automatic capability freezes during dispute.
5. maximum reopen count per case before mandatory manual adjudication.
