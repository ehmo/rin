# Shadow Profile UX V1

## 1) Purpose

Define the shadow profile creation, switching, management, and safeguard UX for v1. Shadow profiles allow users to maintain multiple identities with independent circles, access policies, and contact relationships.

Companion docs:
- `docs/architecture/PROFILE_CLASS_CONTRACT_V1.md` (class definitions, capabilities, transitions)
- `docs/product/CIRCLE_MANAGEMENT_UX_V1.md` (per-profile circle independence)
- `docs/product/USER_JOURNEY_PLAN.md` (Journey 7: Abuse Prevention)

---

## 2) What Is a Shadow Profile

A shadow profile is an alternate identity controlled by the same human principal. Each shadow has its own:
- Display name and photo
- Circles and circle membership
- Access policies (per-field visibility)
- Contact relationships

Shadows do **not** have:
- Independent channel ownership (cannot verify a phone or email)
- Ranking inclusion (excluded from Rin Score input and output)
- Default discoverability (private and non-indexed unless explicitly opted in)

The primary profile remains the user's canonical identity and the only one that contributes to their Rin Score.

---

## 3) Shadow Profile Types

When creating a shadow, user selects a type. Type affects default settings and UI treatment but is **invisible to recipients** — they see only the shadow's identity, not its type label.

### 3.1 Professional

- Purpose: work/business identity. LinkedIn-like separation.
- Defaults: real name encouraged, professional photo, work-related channels shared.
- Use cases: multiple jobs, freelance identity, business representation.
- May be linked to a business org (see §8 for offboarding rules).

### 3.2 Personal

- Purpose: secondary personal identity for social segmentation.
- Defaults: user's choice of name/photo, moderate access policies.
- Use cases: hobby communities, local groups, dating.

### 3.3 Anonymous

- Purpose: pseudonymous identity for privacy-first interactions.
- Defaults: random generated name suggested, no photo required, restrictive access policies.
- Use cases: community participation without identity disclosure, early-stage trust building.

### 3.4 Disposable (V2 — Not in V1)

- System-generated throwaway identities for untrusted interactions.
- Expiring profiles with auto-delete.
- Deferred due to abuse complexity. Tracked as backlog item.

---

## 4) Profile Card Picker

### 4.1 Activation

Long-press on the active profile avatar in the app header.

### 4.2 Card Deck UI

Opens a card picker overlay — each profile rendered as a distinct card:

```
┌─────────────────────────────────┐
│                                 │
│   ┌───────────┐                 │
│   │           │                 │
│   │  [Photo]  │                 │
│   │           │                 │
│   │  Nan      │                 │
│   │  ● Primary│                 │
│   │  3 circles│                 │
│   │  142 ppl  │                 │
│   └───────────┘                 │
│         ┌───────────┐           │
│         │           │           │
│         │  [Photo]  │           │
│         │           │           │
│         │  N. Ehmo  │           │
│         │  💼 Work  │           │
│         │  2 circles│           │
│         │  38 ppl   │           │
│         └───────────┘           │
│               ┌───────────┐     │
│               │  ...      │     │
│               └───────────┘     │
│                                 │
│        [+ Create new profile]   │
└─────────────────────────────────┘
```

**Card layout per profile:**
- Profile photo (or generated avatar for Anonymous)
- Display name
- Type badge with emoji: `● Primary`, `💼 Professional`, `👤 Personal`, `🎭 Anonymous`
- Circle count and contact count
- Active indicator on current profile (glow/border)

**Interaction:**
- Cards are arranged in a scrollable fan/stack (like a hand of cards).
- Tap a card to switch to that profile.
- Swipe through if many profiles exist.
- "Create new profile" button at the bottom of the deck.

**Scale handling (10+ profiles):**
- Cards condense into a scrollable grid (3-4 visible at a time).
- Search/filter bar appears at top: filter by type or name.
- Most recently used profiles float to the top.

### 4.3 Switch Behavior

On profile switch:
1. Brief transition animation (card flip or slide).
2. Entire app context switches: circles, contacts, access policies, and home view reflect the active profile.
3. Header avatar updates to active profile's photo.
4. No re-authentication required for switch (long-press is the deliberate gesture).

### 4.4 Active Profile Indicator

- Header always shows the active profile's avatar.
- Subtle type badge overlay on avatar corner (emoji or colored dot) so user always knows which identity is active.
- If a notification arrives for a different profile, it shows that profile's avatar in the notification.

---

## 5) Shadow Profile Creation

### 5.1 Entry Points

1. **Card picker**: "Create new profile" at bottom of card deck.
2. **Settings > Profiles**: dedicated management screen.
3. **Contextual**: when setting up a circle's access policy, option to "Use a different profile for this circle" (creates shadow if none exist).

### 5.2 Creation Flow

1. **Select type**: Professional / Personal / Anonymous
2. **Set name**:
   - Professional: real name encouraged. Free text.
   - Personal: free text.
   - Anonymous: system suggests a random two-word name. User can customize.
3. **Set photo**:
   - Professional/Personal: upload or reuse from another profile.
   - Anonymous: generated avatar offered. Photo optional.
4. **Set default access policy**:
   - Template based on type (Permissive / Moderate / Restrictive).
   - User can customize per-field immediately or later.
5. **Confirmation**: preview card showing how this profile appears to others.

### 5.3 No Limit on Count

- Users can create unlimited shadow profiles.
- Shadow profiles have zero impact on Rin Score or ranking.
- This fact is **not prominently communicated** to users — we want them to invest effort in their shadows for the experience to feel real and valuable.

---

## 6) Recipient Experience

### 6.1 Full Identity Separation

When someone interacts with a shadow profile, they see **only the shadow's identity**:
- Shadow name
- Shadow photo
- Shadow's allowed fields per their circle membership

There is no indication that this is a shadow profile. No link to the primary identity. No "verified user" badge that might imply a separate primary exists.

### 6.2 Opt-In Identity Reveal

The shadow owner can choose to reveal their primary identity to specific people:
- From the shadow profile's contact management: select a contact → "Reveal my primary identity"
- One-way, irreversible action per contact. Once revealed, that person knows the connection.
- Reveal notification to recipient: `"[Shadow name] is also known as [Primary name] on Rin"`

### 6.3 Cross-Profile Discovery

- By default, there is **no way** for a recipient to discover that two profiles belong to the same person.
- Search does not cross-reference shadow and primary profiles.
- Network graph treats shadows as completely separate nodes (though excluded from ranking).

---

## 7) Independence Model

### 7.1 Fully Independent Profiles

Each shadow profile operates as its own identity space:

| Attribute | Independent? |
|-----------|-------------|
| Display name | Yes — each shadow has its own |
| Photo | Yes — each shadow has its own |
| Circles | Yes — each shadow manages its own circles |
| Circle membership | Yes — contacts assigned per-shadow |
| Access policies | Yes — per-field visibility per shadow's circles |
| Contact list | Yes — each shadow can have different contacts |
| Channels (phone/email) | No — shadows cannot own/verify channels |
| Ranking | No — shadows excluded entirely |
| Discoverability | Independent — each shadow has its own search/discovery settings |

### 7.2 Shared Infrastructure

All shadow profiles share:
- Authentication: same login session, same biometric, same device.
- Billing: premium features apply to the principal, not per-shadow.
- Trust scoring: only the primary profile contributes to and receives a Rin Score.
- Abuse tracking: abuse signals from any shadow roll up to the principal for enforcement.

---

## 8) Professional Profile × Business Offboarding

### 8.1 Org-Linked Professional Profiles

A professional shadow can be linked to a business organization:
- Business admin delegates org representation to the employee's professional shadow.
- Professional shadow gains org badge and can represent the business.
- Business channels (org email, org phone) are accessible via delegation, not ownership.

### 8.2 Offboarding Sequence

When a user leaves a business (voluntarily or involuntarily):

**Immediate (triggered by business admin or system):**
1. Org badge removed from professional shadow.
2. Delegation rights revoked — no more org representation.
3. Business channels (org email, org phone) access revoked.
4. Search projections updated: org affiliation stripped.
5. Events: `org.employee_offboarded`, `org.role_revoked`

**30-day user choice window:**
User receives notification: `"Your professional profile is no longer linked to [Company]. Choose what to do."`

Options:
1. **Convert to personal shadow**: strip all org branding. Keep name, photo, contacts, circles. Profile continues as a regular shadow.
2. **Archive**: freeze profile. Read-only. Contacts preserved. Can be reactivated later.
3. **Delete**: permanently remove the professional shadow and all its data.

**After 30 days with no action:**
- Auto-archive. Profile frozen, not deleted.
- User can still access and convert/delete later from Settings > Profiles > Archived.

### 8.3 Business Perspective

The business admin sees:
- Employee removed from org roster immediately.
- Org channels no longer accessible by former employee.
- No visibility into what the user does with the professional shadow post-offboarding.

---

## 9) Safety and Abuse Controls

### 9.1 Abuse Rollup

All shadow profiles share the same abuse scoring and enforcement as the primary:
- Abuse reports against any shadow count against the principal.
- If principal is suspended, all shadows are suspended.
- Shadow-specific blocks are possible: a person can block one shadow without blocking others (they don't know they're related).

### 9.2 Creation Controls

- No hard cap on shadow count.
- Rate limit: maximum 3 new shadows per 24 hours. Prevents rapid mass creation.
- New accounts (< 7 days old) limited to 1 shadow until account age threshold met.

### 9.3 Impersonation Detection

- Shadow names are checked against existing Rin usernames for impersonation risk.
- Flagged shadows get manual review if name closely matches a prominent account.
- Users can report suspected impersonation on any profile.

### 9.4 Shadow-Specific Restrictions

Per the profile class contract:
- Shadows cannot own or claim channels.
- Shadows cannot initiate ownership disputes.
- Shadows are excluded from ranking input and output.
- Shadows are non-discoverable by default (opt-in required to appear in search).

---

## 10) Management Screen (Settings > Profiles)

### 10.1 Profile List

All profiles displayed as cards:
1. Primary (always first, cannot be deleted, marked distinctly).
2. Active shadows (by type grouping: Professional, Personal, Anonymous).
3. Archived shadows (collapsed section at bottom).

Each card shows: photo, name, type, circle count, contact count, last active date.

### 10.2 Per-Profile Actions

- **Edit**: change name, photo, type label, default access policy.
- **Archive**: freeze profile. Contacts preserved. Can reactivate.
- **Delete**: permanent removal after confirmation. Contacts in this shadow are not deleted from server — they lose their shadow association.
- **Reveal log**: see which contacts have been shown the primary identity.

### 10.3 Archived Profiles

- Visible in a collapsed section.
- Actions: Reactivate, Delete permanently.
- Auto-archived professional profiles (from offboarding) have a label: `"Archived: [Company] offboarding"`

---

## 11) Events

### Profile Lifecycle
- `shadow.created` — type, name (hashed), creation source (picker / settings / contextual)
- `shadow.updated` — changed fields
- `shadow.archived` — reason (manual / offboarding auto-archive)
- `shadow.reactivated`
- `shadow.deleted`

### Switching
- `profile.switched` — from profile ID, to profile ID, switch method (picker / notification tap)

### Identity Reveal
- `shadow.identity_revealed` — shadow ID, target contact ID
- `shadow.identity_reveal_received` — by recipient

### Business Offboarding
- `shadow.org_unlinked` — shadow ID, org ID, trigger (admin / system)
- `shadow.offboarding_choice` — choice (convert / archive / delete)
- `shadow.offboarding_auto_archived` — 30-day timeout

### Abuse
- `shadow.abuse_reported` — shadow ID, report type
- `shadow.impersonation_flagged` — shadow ID, matched name
- `shadow.creation_rate_limited` — principal ID

---

## 12) Edge Cases

1. **User switches to shadow mid-conversation**: recipient sees shadow identity. No notification about the switch. Messages from different profiles are separate threads.
2. **User reveals identity and then deletes shadow**: reveal is irreversible — recipient already knows. Shadow deletion does not retract the reveal.
3. **User creates Anonymous shadow with same name as their primary**: allowed but system warns during creation.
4. **Business admin offboards user who has no professional shadow**: no-op for shadow system. Standard org role revocation applies.
5. **User has 10+ shadows and wants to find one quickly**: card picker search/filter. Type-based grouping. Most recently used float to top.
6. **Shadow profile receives an Ask request for a field it doesn't have**: request rejected automatically. Requester sees "This information is not available."
7. **Two shadows of the same user are in the same group/circle owned by someone else**: they appear as two separate people. No cross-reference surfaced.
8. **Abuse suspension on primary**: all shadows suspended simultaneously. Reactivation restores all.

---

## 13) Accessibility

1. Card picker supports VoiceOver with card-by-card navigation. Each card announces: "[name], [type] profile, [N] circles, [N] contacts."
2. Profile switch announces: "Switched to [profile name]."
3. Type badges use both emoji and text label for non-visual distinction.
4. Active profile indicator uses both visual (glow) and semantic (VoiceOver "active") signals.
5. Dynamic Type supported across all profile management screens.

---

## 14) Open UX Decisions

1. Card picker animation style (fan spread, stack shuffle, grid, or carousel).
2. Whether Anonymous shadows should have a generated avatar style (geometric, abstract, animal-based).
3. Whether shadow profiles can have their own username (separate from primary) or are name-only.
4. Notification grouping: should notifications from different profiles be grouped separately in iOS notification center?
5. Whether to show a "profiles" count anywhere in the app (could imply the feature exists to recipients scanning over someone's shoulder).
6. Whether archived shadows should auto-delete after a long dormancy period (e.g., 1 year).
7. Exact rate limit values for shadow creation (proposed: 3/day, 1 for new accounts < 7 days).
