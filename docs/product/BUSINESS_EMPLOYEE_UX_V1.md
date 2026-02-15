# Business and Employee Role UX V1

## 1) Purpose

Define the business profile, employee role, admin delegation, and reputation model UX. Documents the full vision for business features, scoped to **v2 delivery** — business profiles are not part of the v1 personal-focused launch.

Companion docs:
- `docs/architecture/PROFILE_CLASS_CONTRACT_V1.md` (business/employee class contracts)
- `docs/product/SHADOW_PROFILE_UX_V1.md` (professional shadow profiles, offboarding)
- `docs/product/CIRCLE_MANAGEMENT_UX_V1.md` (circle model that business profiles use)

**V1 scope**: Personal profiles only. Business profiles, employee roles, and admin features are deferred to v2.

---

## 2) Core Model: Organic Business Profiles

### 2.1 Key Principle: Bottom-Up Creation

Business profiles are **not** top-down registrations. They emerge organically:

1. Any user can declare an employer on their professional shadow profile: "I work at Google."
2. This declaration creates (or references) a **business entity stub** for that organization.
3. The stub is initially **unclaimed** — no admin, no verified authority.
4. Multiple employees can independently declare the same employer, growing the entity.
5. The business can later **claim** the entity to take administrative control.

This mirrors how LinkedIn company pages populate from employee declarations. The business profile exists as a community-created entity before the business itself participates.

### 2.2 Business Entity States

| State | Description |
|-------|-------------|
| **Stub** | Created by employee declarations. No admin. Basic info aggregated from declarations. |
| **Claimed** | A user with business authority has claimed the entity. Pending verification. |
| **Verified** | Business verification complete (domain, documents). Admin has full control. |
| **Suspended** | Flagged for abuse or disputed authority. Admin access frozen. |

---

## 3) Business Profile (Company Card)

### 3.1 What It Contains

The business profile is a public-facing company card:

- **Name** (from employee declarations initially, editable by admin after claim)
- **Logo** (uploaded by claiming admin, or aggregated/absent in stub state)
- **Description** (editable by admin)
- **Verified channels**: business phone, business email, website (added by admin)
- **Industry/category** (optional)
- **Location(s)** (optional)

### 3.2 What It Does NOT Show

- No employee roster. Individual employees are not listed on the business card.
- No organizational hierarchy.
- Employees are discoverable through their own professional shadow profiles, not through the business card.

### 3.3 Stub State Appearance

When a business entity exists only from employee declarations (unclaimed):

```
┌─────────────────────────────────┐
│ [Generic building icon]         │
│                                 │
│ Google                          │
│ Unclaimed business              │
│                                 │
│ No verified information yet.    │
│                                 │
│ [Claim this business]           │
└─────────────────────────────────┘
```

- Minimal info: name only (aggregated from employee declarations).
- "Unclaimed" label clearly shown.
- Claim CTA visible to anyone, but claiming requires verification.

---

## 4) Business Onboarding (Claiming)

### 4.1 Who Can Claim

Any existing Rin user can initiate a claim. Claiming triggers a verification process:

1. User taps "Claim this business" on the stub entity, or creates a new business profile from Settings.
2. User enters business details: official name, domain, role/authority.
3. Verification begins (see §4.2).
4. During verification: business profile moves to "Claimed (pending)" state. Claimant becomes provisional admin.
5. After verification: business profile becomes "Verified." Claimant is confirmed admin.

### 4.2 Verification Methods

Verification confirms the claimant has authority to represent the business:

| Method | How it works |
|--------|-------------|
| **Domain verification** | Claimant proves control of the business domain (DNS TXT record or email to admin@domain). |
| **Email verification** | Claimant verifies an email at the business domain. Weaker than domain-level. |
| **Document upload** | Business registration documents, articles of incorporation. Manual review. |
| **Existing employee attestation** | N existing employees on Rin confirm the claimant's authority. Social proof. |

V2 launch: start with domain + email verification. Add document upload and social attestation later.

### 4.3 Disputed Claims

If a business is already claimed and another user tries to claim it:
- Dispute flow initiated.
- Existing admin notified.
- Higher-authority verification required from the challenger.
- Resolved via the dispute playbook (`docs/operations/DISPUTE_PLAYBOOK_V1.md`).

---

## 5) Employee Linking

### 5.1 How Employees Connect

Two paths converge:

**Path A: Admin sends invite**
- Admin enters employee's email or Rin username.
- Employee receives invitation: "Join [Company] on Rin as a team member."
- Employee accepts → their account is linked to the business entity.
- Employee's professional shadow (if it exists) gains org badge.

**Path B: Domain auto-matching**
- When an employee verifies an email matching the business's verified domain, system suggests linking.
- Suggestion: "[Company] is on Rin. Link your account?"
- Employee accepts → linked. Employee declines → no action, no repeated prompts.

**Combined flow:** admin invites explicitly, and system also auto-suggests for matching domain emails. Both paths lead to the same linked state.

### 5.2 What Linking Does

When an employee is linked:
- Their professional shadow profile (if one exists) gains an org badge.
- They can access delegated business channels per their role.
- They appear in the business admin's employee roster (internal only, not public).
- Their personal profile and other shadows are **not affected** — linking is scoped to the professional shadow.

### 5.3 Employee Without Professional Shadow

If an employee accepts a link but has no professional shadow:
- System offers to create one: "Create a professional profile for [Company]?"
- Quick creation flow with business-context defaults.
- Or: employee declines, and linking applies to their primary profile's org affiliation metadata (lighter touch).

---

## 6) Roles: Admin and Member

### 6.1 Two Roles Only

| Role | Capabilities |
|------|-------------|
| **Admin** | Full business profile management: edit company card, manage channels, invite/remove employees, grant admin to others, manage policies. |
| **Member** | Represent the business via professional shadow. Access delegated business channels. Cannot change business settings or manage other employees. |

### 6.2 Admin Management

- First admin is the claimant who verified the business.
- Admins can promote members to admin.
- Admins can demote other admins (except themselves — prevents lock-out).
- At least one admin must exist at all times. Last admin cannot self-demote.

### 6.3 Role Visibility

- Employees see their role in their profile settings: "Member at [Company]" or "Admin at [Company]."
- Role is **not visible** to people outside the organization.
- The business card does not show who is admin vs member.

---

## 7) Business Admin Section

### 7.1 Separate Section in App

Business admin features live in a distinct app section, accessible from:
- Card picker (if admin has a professional shadow linked to a business).
- Settings > Business > [Company name].

### 7.2 Admin Section Screens

**Company Profile**
- Edit name, logo, description, industry, location.
- Manage verified channels (add/remove business phone, email, website).

**Team Roster**
- List of all linked employees with role badges.
- Actions per employee: promote to admin, demote to member, remove from org.
- Invite new employees (by email or Rin username).

**Pending**
- Pending invitations (sent but not accepted).
- Pending domain-match suggestions.
- Pending verification (if business is in claimed state).

### 7.3 V2 Scope for Admin

V2 ships with the minimal admin section above. Future additions (v3+):
- Business analytics (interaction metrics, discovery stats).
- Team communication tools.
- Branded business card customization.
- Org-level access policy templates.

---

## 8) Offboarding

Offboarding is defined in detail in `docs/product/SHADOW_PROFILE_UX_V1.md` §8.

Summary:
1. Admin removes employee from org → immediate org badge and delegation revocation.
2. Employee gets 30-day window to convert, archive, or delete their professional shadow.
3. Auto-archive after 30 days with no action.
4. Employee's personal profile and other shadows are unaffected.

### 8.1 Voluntary Departure

Employee can self-remove from a business:
- Settings > Business > [Company] > "Leave this organization"
- Confirmation: "Your professional profile will be unlinked from [Company]. You can convert it to a personal profile."
- Same 30-day choice flow as admin-initiated offboarding.

### 8.2 Business Dissolution

If a business admin deletes the business entity:
1. All employees receive notification: "[Company] has been removed from Rin."
2. All professional shadows linked to this business enter the 30-day choice flow.
3. Business entity moves to "Dissolved" state (retained for audit, not discoverable).

---

## 9) Business Reputation Index (Design Direction)

### 9.1 Vision

A composite internal signal reflecting business interaction quality. Not a public score number.

### 9.2 Signal Components

| Signal | Source | Direction |
|--------|--------|-----------|
| **Interaction quality** | User ratings after engaging with business employees | Higher = better |
| **Annoyance/spam rate** | Blocks, reports, mutes from people the business contacts | Higher = worse |
| **Verification depth** | Domain verified, channels confirmed, documents submitted | More = better |
| **Response quality** | Reply rate and speed on inbound inquiries | Faster = better |
| **Employee network quality** | Aggregate Rin Scores of linked employees | Higher = better |

### 9.3 How It Surfaces

**Internal use:**
- Search ranking: higher reputation → more discoverable.
- Abuse thresholds: low reputation → stricter outbound rate limits.
- System alerts: reputation drops below floor → admin notified.

**Public-facing (qualitative, not numeric):**
- Trust badges on company card: "Verified Business", "Responsive"
- Warning indicators if reputation is critically low.
- No numeric score shown to the business or to viewers.

### 9.4 Cold Start Problem

At launch, with few businesses operating:
- Start all verified businesses at a neutral baseline.
- Verification depth is the primary initial signal (domain verified > email only > unclaimed).
- Employee network quality provides immediate differentiation without needing interaction data.
- As interactions accumulate, interaction quality and response metrics gain weight.

### 9.5 Deferred Details

- Exact signal weights: calibrate after real interaction data exists.
- Badge criteria thresholds: define after baseline distributions are known.
- Whether businesses see their own reputation metrics (transparency vs gaming risk).

---

## 10) Representation Model

### 10.1 Professional Shadow = Business Representation

There is no separate "represent mode." Representing a business is handled entirely through the professional shadow profile system:

1. Employee creates (or has) a professional shadow linked to the org.
2. When the professional shadow is active in the card picker, the employee acts as themselves-at-company.
3. The professional shadow shows the org badge.
4. Business channels are accessible through the professional shadow (delegated, not owned).

### 10.2 Per-Interaction Identity

Because profile switching is handled via the card picker:
- Before any outreach, the employee's active profile determines their identity.
- If they want to reach out as the business: switch to professional shadow first.
- If they want to reach out personally: switch to primary or personal shadow.
- No per-message identity selection — it's per-session, determined by active profile.

---

## 11) Events

### Business Lifecycle
- `business.stub_created` — created from employee declaration, name
- `business.claim_initiated` — claimant principal, verification method
- `business.claim_verified` — verification method, admin principal
- `business.claim_disputed` — challenger principal, existing admin
- `business.profile_updated` — changed fields
- `business.dissolved` — admin principal, employee count at dissolution

### Employee Linking
- `business.invite_sent` — target email/username, business ID
- `business.invite_accepted` — employee principal, business ID
- `business.domain_match_suggested` — employee principal, matched domain
- `business.domain_match_accepted` — employee principal
- `business.employee_linked` — employee principal, role, link source (invite / domain)
- `business.employee_removed` — employee principal, reason (admin / self / offboarding)

### Roles
- `business.role_changed` — employee principal, old role, new role, changed by

### Reputation (Internal Tracking)
- `business.interaction_rated` — rater principal, business ID, rating
- `business.spam_reported` — reporter principal, business ID
- `business.reputation_recalculated` — business ID, new composite (internal)
- `business.reputation_threshold_crossed` — business ID, direction (up/down), threshold

---

## 12) Edge Cases

1. **Two users claim the same business**: dispute flow. Higher verification wins. If both have domain access, manual review.
2. **Employee declares employer that doesn't exist on Rin**: stub created automatically. No verification needed for stubs.
3. **Employee linked to two businesses simultaneously**: allowed. Each has a separate professional shadow. Card picker shows both.
4. **Admin removes themselves as admin with no other admins**: blocked. System requires at least one admin.
5. **Business verified, then domain expires/transfers**: periodic re-verification check. If domain no longer validates, business moves to "reverification needed" state. Admin notified.
6. **Employee has professional shadow but declines org linking**: shadow remains as a standalone professional profile with no org badge. No delegation access.
7. **Unclaimed stub has 50+ employee declarations**: stub becomes prominent in search. "Claim this business" shown more aggressively. Consider proactive outreach.
8. **Business admin account is compromised**: emergency freeze on business profile. Dispute flow for authority recovery per dispute playbook.
9. **Employee creates professional shadow, links to business, then business is dissolved**: shadow enters 30-day choice flow per offboarding rules.

---

## 13) Accessibility

1. Admin section follows same Dynamic Type and VoiceOver standards as rest of app.
2. Role badges announce role text, not just visual indicator.
3. Verification status steps are sequential and navigable with assistive tech.
4. Team roster supports VoiceOver list navigation with per-employee actions.

---

## 14) V1 vs V2 Scope

| Feature | V1 | V2 |
|---------|-----|-----|
| Personal profiles | Ship | — |
| Professional shadow profiles | Ship | — |
| Business entity stubs (from employee declarations) | — | Ship |
| Business claiming and verification | — | Ship |
| Admin/member roles | — | Ship |
| Employee invite + domain matching | — | Ship |
| Admin section (roster, channels, profile) | — | Ship |
| Business reputation tracking | — | Ship (internal only) |
| Public trust badges | — | Later (v3+, after data) |
| Business analytics | — | Later (v3+) |
| Team communication | — | Later (v3+) |

### V1 Professional Shadow Behavior (Without Business Features)

In v1, professional shadow profiles exist but operate independently:
- User can create a professional shadow and name their employer (free text).
- No org linking, no admin delegation, no business channels.
- The employer name is display-only metadata on the professional shadow.
- When business features ship in v2, existing professional shadows can be retroactively linked to claimed business entities.

---

## 15) Open UX Decisions

1. How employee declarations aggregate into stub entity names (majority vote? first declaration? manual merge?).
2. Whether stub entities should be searchable or only discoverable through employees.
3. Re-verification cadence for business domain validation (annual? triggered by domain change detection?).
4. Whether businesses can see which employees declared them before the business claimed the entity.
5. Maximum employees per business entity before requiring enterprise verification.
6. Whether business reputation signals should be visible to the business admin as a dashboard metric.
7. Exact cold-start baseline values for newly verified businesses.
8. Whether dissolved businesses should remain in search results with a "no longer active" label.
