# Circle Management UX V1

## 1) Purpose

Define the circle system UX for v1: creation, assignment, per-field access control, and overlap handling. Optimized for low cognitive load while delivering granular privacy control.

Companion docs:
- `docs/product/USER_JOURNEY_PLAN.md` (Journey 3: Circle and Access Management)
- `docs/product/IOS_INSTALL_TO_FIRST_VALUE_UX_V1.md` (Section 6-7)
- `docs/architecture/PROFILE_CLASS_CONTRACT_V1.md` (Class-aware policy rules)

---

## 2) Circle Taxonomy

### 2.1 Mandatory Circles (Immutable)

Two system circles exist for every user. Cannot be deleted or renamed.

**Contacts**
- Contains every entity the user has imported or manually added.
- Every contact is always in this circle regardless of other circle membership.
- Purpose: baseline container. Access policy on this circle defines the default for anyone not in a more specific circle.

> Naming note: "Contacts" chosen over "Everyone" (confusable with platform-wide), "Network" (too abstract), "My People" (too informal for plumber/mechanic contacts). Revisit after user testing.

**Public**
- Follow-style visibility circle.
- Anyone on the platform can see fields allowed for Public.
- Analogous to Twitter follow — one-directional discovery, no mutual requirement.

### 2.2 Prepopulated Circles

Three circles created at onboarding with sensible defaults. User can rename, customize, or delete.

1. **Family** — emoji: default. Suggested access: permissive (most fields allowed).
2. **Friends** — emoji: default. Suggested access: moderate.
3. **Colleagues** — emoji: default. Suggested access: restricted (work contact info only).

### 2.3 Custom Circles

User-created circles for any purpose. Unlimited count.

Properties per circle:
- **Name** (required, free text, max 30 chars)
- **Emoji** (optional, user-picked)
- **Accent color** (optional, user-picked from palette)
- **Profile photo** (optional, one per circle — what contacts in this circle see as user's photo)
- **Access policy** (per-field visibility matrix)

When custom circle count becomes unwieldy, system suggests merging similar circles based on membership overlap and access policy similarity. No hard cap enforced.

### 2.4 Circle Types (V1 vs Future)

| Type | V1 | Description |
|------|-----|-------------|
| **Permanent** | Ship | User-created, manually managed |
| **Temporary** | Backlog | Event-scoped (conference, ski trip, dating), time-bounded |
| **Imported** | Backlog | Pulled from group chats (WhatsApp, Signal). Suggested as circle, user normalizes |
| **Shared** | Backlog | Collaborative circle (college group, team). Import if allowed by creator |

Temporary circles will need per-type expiry behavior (manual archive, date-based auto-archive, inactivity fade). Track as separate design task when scoped.

---

## 3) Access Control Model

### 3.1 Per-Field Visibility

Every field the user adds to their profile is independently controllable per circle. Fields include all channels and personal information:

- Phone numbers (each individually controllable)
- Email addresses (each individually)
- Social accounts (X, LinkedIn, WhatsApp, etc.)
- Physical addresses (each individually)
- Date of birth
- Any future user-added fields

### 3.2 Three Visibility States

Each field × circle combination has exactly one state:

| State | Icon | Behavior for viewer |
|-------|------|---------------------|
| **Allow** | Checkmark / green | Field is visible immediately on contact card |
| **Don't Allow** | X / red | Field is completely hidden. Viewer does not know it exists |
| **Ask** | Question / amber | Viewer sees the field label with a "Request" button. Tapping sends a request to the owner |

### 3.3 Ask Flow

When a viewer taps "Request" on an Ask field:

1. Owner receives a push notification: `"Alex requested your email address."`
2. Request appears in owner's in-app request queue.
3. Owner taps Approve or Deny.
4. If approved: field becomes visible to that specific person (personal override, not circle-wide).
5. If denied: viewer sees no change. No notification sent to viewer about denial.
6. Requests have no expiry in v1. Owner can review and act at any time.

Anti-abuse:
- One active request per field per person. No re-request until previous is resolved.
- Rate limit on total outbound requests per user per day (prevent spam-requesting).

### 3.4 Default Access Policies

At onboarding, system sets recommended defaults per prepopulated circle:

| Circle | Default policy |
|--------|---------------|
| **Contacts** | Name: Allow. All else: Don't Allow |
| **Public** | Name: Allow. All else: Don't Allow |
| **Family** | All fields: Allow |
| **Friends** | Name, primary phone, primary email, photo: Allow. Rest: Ask |
| **Colleagues** | Name, work email, work phone: Allow. Personal fields: Don't Allow |

User can modify all defaults during onboarding (S10) or later.

### 3.5 Per-Circle Profile Photo

Each circle can have a distinct profile photo that contacts in that circle see when interacting with the user (calls, messages, contact card).

- Default: primary profile photo applies to all circles.
- Override: user uploads a different photo for specific circles.
- Use case: professional headshot for Colleagues, casual photo for Friends.

---

## 4) Multi-Circle Overlap

### 4.1 Rule: Most Permissive Wins

When a contact belongs to multiple circles with different access policies for the same field, the most permissive setting applies:

- Allow > Ask > Don't Allow

Example: Alex is in both Friends (email: Allow) and Colleagues (email: Ask). Alex sees the email immediately (Allow wins).

### 4.2 Overlap Transparency

Three layers of warning to prevent accidental over-sharing:

**Layer 1: Inline badge on contact card**
- Small indicator: `"Also in: Friends, Colleagues"`
- Tap to see full circle membership list.

**Layer 2: Warning during circle policy edit**
- When changing a circle's access policy, show affected contacts:
  - `"3 contacts are also in Friends. This change will make their email visible."`
- Pre-action warning before saving.

**Layer 3: Merged view in contact profile**
- Contact detail screen shows the effective (merged) access with source attribution:
  - `"Email: visible (via Friends circle)"`
  - `"Phone: requestable (via Colleagues circle)"`
  - `"Address: hidden (default from Contacts circle)"`
- Allows user to understand exactly what this person sees and why.

---

## 5) Circle Creation and Assignment

### 5.1 Creation Entry Points

Multiple paths to circle creation, all converge on the same creation flow:

**From contact profile (primary path)**
- Long-press contact → "Add to circle" → "Create new circle"
- Lowest friction. Discovered naturally during contact management.

**From circles management screen**
- Dedicated tab/section → "New circle" button.
- Better for planned organization.

**From bulk selection**
- Multi-select contacts from list → "Add to circle" → "Create new circle"
- Power-user path for batch operations.

### 5.2 Creation Flow

1. Name (required)
2. Emoji (optional, skip for later)
3. Color (optional, auto-assigned if skipped)
4. Profile photo for this circle (optional, uses default)
5. Access policy (start from template: Permissive / Moderate / Restricted, then customize)

### 5.3 Assignment Mechanisms

| Mechanism | Description | Primary use |
|-----------|-------------|-------------|
| **Contact-centric** | From contact profile, tap to see/change circle membership | Daily management |
| **Circle-centric** | Open circle, add/remove contacts from it | Batch setup |
| **Multi-select bulk** | Select contacts from list, assign to circle(s) | Initial organization |
| **Smart suggestions** | System suggests assignments based on contact metadata patterns | Passive assistance |

Smart suggestions trigger:
- After contact import (group contacts by shared attributes: same company domain, same area code, etc.)
- When a new contact shares metadata patterns with an existing circle's members.
- Suggestions are dismissable and never auto-applied.

---

## 6) Circle Management Screen

### 6.1 Circle List View

Ordered by:
1. Mandatory circles (Contacts, Public) — always at top, visually distinct.
2. Prepopulated circles (Family, Friends, Colleagues) — unless deleted.
3. Custom circles — alphabetical or by most recently modified.

Each circle row shows:
- Emoji + color accent
- Circle name
- Member count
- Access policy summary (e.g., "Permissive" / "3 fields shared")

### 6.2 Circle Detail View

Sections:
1. **Header**: emoji, color, name, profile photo for this circle.
2. **Members**: scrollable contact list with quick-remove swipe.
3. **Access policy**: per-field card list with Allow / Don't Allow / Ask toggles.
4. **Preview**: "How you appear to this circle" — rendered profile card as a member would see it.

### 6.3 Circle Deletion

- Prepopulated and custom circles can be deleted.
- Contacts in a deleted circle remain in Contacts (mandatory).
- Confirmation dialog explains: "These contacts will keep their default access from the Contacts circle."
- Mandatory circles cannot be deleted. Attempting shows explanation.

---

## 7) Contact Profile Circle Section

On any contact's detail screen:

**Circle membership badge area**
- Shows all circles this contact belongs to as emoji+name chips.
- Tap any chip to jump to that circle's detail view.
- "+" button to add to another circle.

**Effective access summary**
- Collapsed by default: "This person can see 4 of your 8 fields."
- Expanded: full merged view with per-field source attribution (see 4.2 Layer 3).

**Override capability**
- Per-contact field overrides that supersede circle policy.
- Use case: share personal phone with one colleague without changing the entire Colleagues circle policy.
- Overrides shown distinctly in the merged view: `"Phone: visible (personal override)"`.

---

## 8) Events

### Circle Lifecycle
- `circle.created` — name, type, initial access policy snapshot
- `circle.updated` — changed fields (name, emoji, color, photo, policy)
- `circle.deleted` — circle ID, member count at deletion
- `circle.merge_suggested` — suggested pair, overlap percentage

### Membership
- `circle.member_added` — contact ID, circle ID, source (manual / bulk / suggestion)
- `circle.member_removed` — contact ID, circle ID

### Access Control
- `policy.field_changed` — circle ID, field, old state, new state
- `policy.override_set` — contact ID, field, override value
- `access.request_sent` — requester, field, target user
- `access.request_approved` — requester, field
- `access.request_denied` — requester, field (no notification to requester)

### Profile Photo
- `circle.photo_set` — circle ID
- `circle.photo_removed` — circle ID

---

## 9) Smart Merge Suggestions

When custom circle count grows, system monitors for:
- **High membership overlap**: two circles with >70% shared contacts.
- **Identical access policies**: two circles with the same field visibility settings.
- **Low differentiation**: circles with <3 unique members not in the other.

Suggestion format:
- In-app card (not push notification): `"Friends and Close Friends share 12 contacts. Merge them?"`
- Actions: "Merge" (keeps more permissive policy), "Keep separate", "Dismiss forever".

No automatic merging. Always user-initiated.

---

## 10) Edge Cases

1. **Contact removed from all custom circles**: reverts to Contacts-only access policy.
2. **User deletes all prepopulated circles**: allowed. Contacts and Public remain. User manages with custom circles only.
3. **Same field in Allow (Circle A) and Don't Allow (Circle B)**: Allow wins per most-permissive rule. Overlap warning surfaces.
4. **Ask request approved, then circle membership removed**: personal override persists. User must explicitly revoke if desired.
5. **Per-contact override contradicts circle policy**: override always wins. Override is noted in merged view.
6. **Profile photo set for circle, then circle deleted**: photo orphaned and cleaned up. No impact on other circles.
7. **Contact appears in 10+ circles**: UI caps visible chips at 3-4 with "+N more" expansion. All circles shown on tap.

---

## 11) Accessibility

1. All circle emoji/color combinations must pass contrast requirements against background.
2. VoiceOver reads circle chips as "Circle: [name], [member count] members".
3. Access policy toggles are three-state accessible controls with clear labels.
4. Overlap warnings are announced to assistive tech when they appear.
5. Dynamic Type supported across all circle management screens.

---

## 12) Open UX Decisions

1. Final naming for the mandatory "all imported contacts" circle (Contacts vs alternative after user testing).
2. Exact emoji and color defaults for prepopulated circles.
3. Whether per-contact overrides require confirmation ("You're sharing this outside circle policy").
4. Maximum outbound Ask requests per day rate limit value.
5. Whether denied Ask requests should have a cooldown before the same person can re-request.
6. Smart merge suggestion threshold tuning (overlap %, differentiation floor).
7. Whether circle photo appears in the OS-level caller ID / message preview or only in-app.
