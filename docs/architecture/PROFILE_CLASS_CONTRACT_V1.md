# Profile Class Contract V1

## 1) Purpose

Define class-level behavior contracts for all profile types in Rin.

Classes in scope:
- `single`
- `shadow`
- `business`
- `employee`

This contract governs:
- identity semantics,
- ownership and delegation rules,
- discoverability/search behavior,
- ranking inclusion/exclusion,
- allowed transitions and lifecycle events.

---

## 2) Core Concepts

- `principal`: account identity with authentication and ownership rights.
- `profile`: renderable identity surface shown to others.
- `profile_class`: one of `single|shadow|business|employee`.
- `owner_principal_id`: controlling principal for profile operations.
- `org_id`: organization linkage for business/employee contexts.

General invariants:
1. Every profile has exactly one class.
2. Every profile has exactly one owner principal.
3. Class changes are explicit lifecycle events.
4. Policy engine behavior is class-aware for all reads/writes.

---

## 3) Class Definitions

## 3.1 `single`

Definition:
- Standard human profile for individual users.

Ownership:
- Owned directly by human principal.

Capabilities:
- may own verified channels,
- may manage circles/policies,
- may appear in ranking.

Default discoverability:
- discoverable by policy and search settings.

## 3.2 `shadow`

Definition:
- Alter-ego profile controlled by a single human principal.

Ownership:
- owned by parent principal (`owner_principal_id`).

Capabilities:
- may have independent display metadata,
- may have independent policy settings,
- cannot directly own channels,
- cannot initiate ownership claims.

Default discoverability:
- private/non-indexed by default.

Ranking rule:
- excluded from ranking input and output.

## 3.3 `business`

Definition:
- Organization profile representing a company/entity.

Ownership:
- owned by business principal, administered by org roles.

Capabilities:
- may own business channels,
- may manage org-level discoverability,
- may delegate employee roles.

Default discoverability:
- discoverable by default unless policy restricts.

Ranking rule:
- business ranking policy deferred; v1 uses separate visibility metrics, not personal Rin score.

## 3.4 `employee`

Definition:
- Human profile linked to a business relationship.

Ownership:
- owned by human principal; linked to org via typed relation.

Capabilities:
- may have personal verified channels,
- may represent business if delegated,
- cannot claim business primary channels without org authority.

Default discoverability:
- discoverable as person; org affiliation shown by policy.

Ranking rule:
- eligible for personal ranking as human profile (business influence edges policy-gated).

---

## 4) Capability Matrix

Capabilities:
- `own_channels`
- `claim_channels`
- `public_discoverability_default`
- `rank_included`
- `can_create_shadow`
- `can_admin_org`
- `can_represent_org`

Class matrix:

- `single`
  - own_channels: yes
  - claim_channels: yes
  - public_discoverability_default: policy-based on
  - rank_included: yes
  - can_create_shadow: yes
  - can_admin_org: no (unless separately delegated)
  - can_represent_org: no (unless separately delegated)

- `shadow`
  - own_channels: no
  - claim_channels: no
  - public_discoverability_default: off
  - rank_included: no
  - can_create_shadow: no
  - can_admin_org: no
  - can_represent_org: no

- `business`
  - own_channels: yes
  - claim_channels: yes
  - public_discoverability_default: on
  - rank_included: no (v1)
  - can_create_shadow: no
  - can_admin_org: yes
  - can_represent_org: n/a

- `employee`
  - own_channels: yes (personal)
  - claim_channels: yes (personal), org claims only with delegation
  - public_discoverability_default: policy-based on
  - rank_included: yes (personal)
  - can_create_shadow: yes (if personal policy permits)
  - can_admin_org: delegated only
  - can_represent_org: delegated only

---

## 5) Discoverability and Search Contract

## 5.1 Defaults

- `single`: indexed by default with policy-safe fields.
- `shadow`: not indexed by default.
- `business`: indexed by default with org-safe fields.
- `employee`: indexed as person; org relation visibility policy-controlled.

## 5.2 Indexing Rules

1. Search index stores only policy-safe projections.
2. `shadow` profiles require explicit opt-in flags to become searchable.
3. Business authority disputes auto-restrict org profile discoverability as needed.
4. Disputed ownership channels are removed from search projections immediately.

---

## 6) Ranking Contract by Class

Rules:

1. `single`: included in ranking input and output.
2. `employee`: included in personal ranking; org edges are policy-gated modifiers.
3. `business`: excluded from personal ranking in v1.
4. `shadow`: always excluded from ranking input/output.

Additional safeguards:
- Any edge involving `shadow` is ignored by ranking graph builders.
- Score explainability must indicate when class-based exclusions apply.

---

## 7) Ownership and Delegation Rules

1. `shadow` cannot own or claim channels.
2. `business` channels belong to business principal.
3. `employee` cannot transfer business channels unless delegated and authorized.
4. Offboarding employee revokes delegated org authority immediately.
5. Delegation grants are explicit, time-bounded, and auditable.

---

## 8) Allowed Class Transitions

Supported transitions:

1. `single -> shadow` (create alter profile)
2. `shadow -> revoked` (delete/deactivate shadow)
3. `single -> employee` (org linkage added)
4. `employee -> single` (org linkage removed)
5. `business -> revoked` (business profile deactivation)

Not allowed:

1. `shadow -> single` in-place conversion (create new single profile instead).
2. `employee -> business` direct conversion.
3. `single -> business` direct conversion without org onboarding flow.

Transition invariants:
- class transition requires lifecycle event and audit record.
- policy and search projections must be recomputed on transition.
- ranking inclusion recalculated on transition.

---

## 9) Class-Specific Security Controls

`single`:
- standard account security and dispute flow.

`shadow`:
- stricter creation rate limits.
- default outbound restrictions until trust criteria met.
- impersonation checks higher sensitivity.

`business`:
- mandatory role-based access controls.
- emergency admin recovery path.
- stronger verification for channel transfer.

`employee`:
- delegated authority separation from personal ownership.
- automatic role expiry/offboarding revocation.

---

## 10) Events Required by Class Contract

Mandatory lifecycle events:

- `profile.created`
- `profile.class_changed`
- `profile.visibility_changed`
- `profile.deactivated`
- `org.role_granted`
- `org.role_revoked`
- `org.employee_offboarded`

Class payload requirements:
- `profile_class`
- `owner_principal_id`
- `discoverability_flags`
- `rank_inclusion` (boolean)
- `org_id` (if applicable)

---

## 11) Edge Cases and Required Behavior

1. Shadow profile attempts channel claim.
- reject with authorization error; emit security signal.

2. Shadow profile accidentally indexed due projector bug.
- enforce read-time policy filter + reindex remediation.

3. Employee removed from org but still appears as representative.
- role revocation event forces projection invalidation and cache purge.

4. Business admin compromised.
- freeze high-risk org actions; invoke business authority dispute flow.

5. User creates many shadows to game trust/discovery.
- throttle creation, visibility gating, and abuse scoring constraints.

---

## 12) Observability Requirements

Track per class:
- profile count growth,
- discoverable vs hidden ratio,
- search impressions,
- abuse/report rates,
- dispute rates,
- rank inclusion exclusions.

Alert examples:
- sudden surge in `shadow` creation,
- shadow discoverability flips above threshold,
- org role churn spike,
- class transition failure rate spikes.

---

## 13) Open Decisions

1. Maximum shadow profiles allowed before progressive friction.
2. Whether business profiles get a separate public score/health metric in v1.
3. Whether employee profile can opt out of public org affiliation display.
4. Default discoverability behavior for newly created employee profiles.
5. Which delegation scopes can permit business-channel messaging.
