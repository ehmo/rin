# Rin Dispute Playbook V1

## 1) Purpose

Define how verification and ownership disputes are handled end-to-end across:
- technical systems,
- operational workflow,
- user experience,
- ranking and policy side-effects.

This playbook is designed for:
- single user profiles,
- shadow profiles (non-ranked),
- business + employee-linked profiles.

---

## 2) Design Principles

1. Safety before convenience in identity conflicts.
2. Minimize permanent damage via reversible actions.
3. Keep most users functional while high-risk capabilities are limited.
4. Keep user-facing steps clear, short, and time-bounded.
5. Make all decisions auditable and replayable.

---

## 3) Dispute Case Types

### C1: Channel Ownership Conflict

Definition:
- Same phone/email is claimed by multiple principals.

Common causes:
- account takeover,
- shared devices,
- stale linkage,
- malicious claim.

### C2: Channel Reassignment (Phone Recycled)

Definition:
- Number is reassigned by carrier; old owner still linked in graph.

Common causes:
- long inactivity,
- carrier recycling.

### C3: Mistaken Identity Merge

Definition:
- Two real people are merged into one identity cluster.

Common causes:
- weak dedup confidence,
- common names + stale channels.

### C4: Impersonation / Pretend Identity

Definition:
- Profile identity suggests unauthorized representation of another person/business.

Common causes:
- fake account,
- abusive shadow profile.

### C5: Business Authority Conflict

Definition:
- Current actor controls business profile/channels without valid role.

Common causes:
- ex-employee retention,
- role drift,
- compromised admin.

### C6: Abuse-Driven Trust Dispute

Definition:
- spam/harassment/fraud flags trigger risk state challenge.

Common causes:
- high outbound abuse,
- coordinated reports,
- suspicious graph behavior.

---

## 4) Core State Machines

## 4.1 Channel State

- `verified_active`
- `challenged`
- `limited`
- `disputed`
- `recovered`
- `transferred`

Transitions:
1. `verified_active -> challenged` on risk trigger or competing claim.
2. `challenged -> limited` if challenge window expires or evidence is strong.
3. `limited -> disputed` when case opens and adjudication begins.
4. `disputed -> recovered` if original owner proves control.
5. `disputed -> transferred` if new claimant proves control and hold period clears.

## 4.2 Case State

- `opened`
- `triaged`
- `awaiting_user`
- `awaiting_system_hold`
- `adjudication`
- `resolved`
- `reopened`

Case closure requirements:
- machine-readable resolution code,
- evidence references,
- impacted entities list,
- reversal plan ID.

---

## 5) Resolution Workflow by Case Type

## C1/C2 (Channel ownership / reassignment)

Technical flow:
1. Create case and freeze sensitive channel actions.
2. Require claimant OTP proof.
3. Notify previous verified owner.
4. Enforce hold window (default 72h for high-risk, 24h for low-risk).
5. Collect additional evidence (recent trusted device/session, prior verified factor, behavior consistency).
6. Auto-adjudicate if confidence threshold met; else queue manual review.
7. Apply reversible transfer or recovery event.

User flow:
1. User receives security alert with plain-language summary.
2. One-tap actions: `This is me`, `This is not me`, `Start recovery`.
3. Progress screen shows countdown and required steps.
4. On resolution, user sees exactly what changed.

## C3 (Mistaken merge)

Technical flow:
1. Mark merge edge as `contested`.
2. Remove contested edge from ranking/search projections immediately.
3. Generate split candidate plan from provenance graph.
4. Apply split transaction with reversible linkage map.
5. Trigger reindex + score delta recompute.

User flow:
1. User reviews “Why merged” evidence summary.
2. User confirms split request.
3. UI shows post-split preview before final confirmation.

## C4 (Impersonation)

Technical flow:
1. Temporarily reduce discoverability and outbound reach capabilities.
2. Run identity verification challenge.
3. If failed or no response, quarantine profile visibility.
4. If malicious confidence is high, enforce restrictions and preserve forensic snapshot.

User flow:
1. Reporter gets status updates (without private details).
2. Accused profile owner gets clear appeal path and required proof.

## C5 (Business authority)

Technical flow:
1. Validate role assignment chain (org owner/admin/manager).
2. Freeze high-risk org actions on conflict.
3. Require business-domain or legal-entity proof for top-level ownership challenge.
4. Remove invalid delegates and revoke sessions/tokens on decision.

User flow:
1. Organization sees who currently has authority and why.
2. Offboarding checklist shown for disputed delegates.

## C6 (Abuse-driven trust)

Technical flow:
1. Trust state lowered; rate limits tightened.
2. Run abuse model + rule evidence package.
3. Allow appeal with specific missing context fields.
4. Restore trust gradually on clean-window decay.

User flow:
1. Explain restriction type and duration.
2. Provide concrete remediation steps.

---

## 6) Automatic Actions (Immediate Safeguards)

On case open, apply policy bundle by severity:

Severity L1:
- require re-verification for sensitive updates.

Severity L2:
- freeze channel edits,
- freeze username transfers,
- reduce search visibility.

Severity L3:
- disable public reachability,
- block new shadow profile creation,
- require strong recovery path.

All automatic actions must be:
- reversible,
- logged,
- tied to case ID.

---

## 7) Ranking and Graph Side Effects

Rules:
1. Contested channels are excluded from trust-positive scoring signals.
2. Disputed identity links are excluded from centrality contribution until resolved.
3. Shadow profiles never participate in ranking input/output.
4. Business-employee disputed edges are excluded from org influence features.

When case resolves:
- publish `score.recompute.requested` for impacted neighborhood,
- produce explanation update for affected user scores.

---

## 8) UX Blueprint (iOS)

Primary surfaces:
1. `Security & Ownership Inbox`
2. `Case Detail Screen`
3. `Action Checklist`
4. `Resolution Timeline`

Message style:
- short,
- specific,
- no legal jargon,
- clear deadlines.

Required UX elements:
- visible countdown for hold periods,
- evidence summary (“what we saw”),
- explicit consequence summary (“what is limited now”),
- one-step appeal action.

---

## 9) Operational SLAs

Suggested v1 SLA targets:

- C1/C2 low-risk auto resolution: 5-30 minutes.
- C1/C2 high-risk with hold: 24-72 hours.
- C3 merge split processing: under 2 hours.
- C4 impersonation high-severity triage: under 15 minutes.
- C5 business authority urgent freeze: under 10 minutes.
- C6 trust appeals: first response under 4 hours.

Queue priorities:
1. Account compromise / channel takeover
2. Business authority compromise
3. Impersonation
4. Merge mistakes
5. Trust-score appeals

---

## 10) Event Contracts (High-Level)

Core events:
- `security.case.opened`
- `security.case.state_changed`
- `channel.challenge.started`
- `channel.challenge.completed`
- `identity.dispute.opened`
- `identity.dispute.resolved`
- `identity.link.contested`
- `identity.link.split_applied`
- `org.authority.contested`
- `org.authority.resolved`
- `trust.restricted`
- `trust.restored`
- `score.recompute.requested`

Event requirements:
- immutable payload version,
- idempotency key,
- actor + subject + case ID,
- causation ID and correlation ID.

---

## 11) Data Retention and Reversibility Defaults

Operational defaults (proposed):

1. Verification artifacts (OTP proofs, challenge outcomes): 180 days hot, then hashed/summary retention.
2. Dispute case logs and decisions: 2 years active, archive thereafter.
3. Merge/split provenance events: retained for full reversibility horizon (no hard delete without legal policy decision).
4. High-risk forensic snapshots: restricted access, shorter retention unless escalated.

Deletion policy principle:
- user-facing deletion can remove discoverable personal data while preserving minimal compliance/audit skeleton.

---

## 12) Capacity and Bottlenecks

Expected bottleneck at high scale:
- verification/dispute operations throughput, not graph math.

Mitigations:
1. stronger auto-adjudication for low-risk cases,
2. evidence scoring pipeline for triage quality,
3. strict queue priority lanes,
4. abuse-resistant self-serve flows to reduce manual burden.

---

## 13) Edge Cases Checklist

1. Old owner and new owner both pass OTP due SIM-swap window.
2. User loses all factors and cannot respond in hold period.
3. Business loses sole admin account.
4. Shadow profile linked to disputed channel.
5. Mass false-report attack on legitimate user.
6. Event replay emits duplicate freeze/unfreeze actions.
7. Search index temporarily exposes stale authority state.

Each edge case must map to:
- automatic safeguard,
- user remediation path,
- operational escalation path.

---

## 14) Decisions to Confirm with Founder

1. Default hold windows by risk tier (24h/48h/72h).
2. Whether reassigned numbers require forced cooldown before transfer.
3. How much evidence to expose in-app vs keep internal.
4. Whether business disputes require external/legal verification in v1.
5. Shadow-profile public discoverability default (recommended: off).
