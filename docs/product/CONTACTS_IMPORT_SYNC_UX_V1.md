# Contacts Import and Sync UX V1

## 1) Purpose

Define the end-to-end contacts import, sync, dedup, enrichment, and management UX for v1. Covers initial onboarding import through ongoing sync lifecycle.

Companion docs:
- `docs/product/USER_JOURNEY_PLAN.md` (Journey 2: Contact Import + Canonicalization)
- `docs/product/IOS_ONBOARDING_SCREEN_SPEC_V1.md` (S6, S11, S12)
- `docs/product/CIRCLE_MANAGEMENT_UX_V1.md` (circle assignment after import)
- `docs/architecture/PROFILE_CLASS_CONTRACT_V1.md` (shadow profile exclusions)

---

## 2) Sync Architecture

### 2.1 Sync Model: Event-Triggered + Background Fallback

**Primary trigger**: `CNContactStoreDidChangeNotification`
- iOS fires this notification when the device address book changes (contact added, edited, deleted).
- Rin listens for this notification and triggers a delta sync immediately.

**Fallback**: `BGAppRefreshTask` via `BGTaskScheduler`
- Scheduled background refresh (~daily) catches changes missed while app was terminated.
- ~30 seconds of execution time. Sufficient for delta sync against server.

**On app foreground**:
- Check last sync timestamp. If stale (>1 hour), trigger a delta sync.

### 2.2 Sync Direction: One-Way in V1

- Device address book → Rin (read-only import).
- No writeback to device contacts in v1.
- Enrichments, merges, and circle assignments live only in Rin.

### 2.3 Sync Resumability

If sync is interrupted (app killed, network loss, phone died):
- **Silent auto-resume** on next app launch or background execution.
- Sync is idempotent — safe to restart from any point without duplicates.
- No user action required. Progress indicator updates to reflect resumed state.

### 2.4 Data Flow

```
Device Address Book
    ↓ (CNContactStore read)
Raw Contact Snapshot (immutable)
    ↓ (normalization)
Canonical Contact Record
    ↓ (dedup engine)
Merge Suggestions / Auto-Merges
    ↓ (network enrichment)
Enriched Contact Profile
    ↓ (circle assignment)
Circle-Aware Contact Card
```

Every stage preserves the raw snapshot for provenance and reversibility.

---

## 3) Initial Import (Onboarding)

### 3.1 Permission Grant → Immediate Sync Start

After user grants contacts permission (S6 in onboarding spec):
1. Sync starts immediately in background.
2. User continues onboarding (name, photo, username, sharing defaults).
3. By the time user reaches S11 (sync progress bridge), import is partially or fully complete.

### 3.2 Progress Bridge Screen (S11)

Animated counter with phased messaging:

**Phase 1: Import**
- Counter: `Importing... 847 of 1,243 contacts`
- Animated contact card icons flowing into a container.

**Phase 2: Dedup**
- Counter: `Finding duplicates... 23 potential matches`
- Visual: pairs of cards sliding together.

**Phase 3: Suggestions**
- Counter: `Building suggestions...`
- Visual: cards arranging into organized groups.

**Completion transition:**
- Once minimum viable data is ready (all contacts imported + dedup pass complete), primary CTA enables: `Continue`
- Screen is non-blocking — user can tap Continue before Phase 3 finishes. Suggestions continue building in background.

### 3.3 Large Import Handling (1000+ contacts)

- Import runs in batches (100 contacts per batch) to manage memory.
- Counter updates per-batch, not per-contact, to avoid UI thrash.
- If import takes >30 seconds, show a reassurance line: `This is a one-time setup. Future syncs are instant.`

---

## 4) Conflict Resolution

### 4.1 When Conflicts Arise

A conflict occurs when:
- A contact field is modified on-device AND has been independently modified in Rin since last sync.
- Example: user edits contact name in Phone.app AND edits it in Rin.

### 4.2 Resolution: User Decides

Both versions are preserved. User sees a conflict card:

```
┌─────────────────────────────────┐
│ ⚠ Conflict: Alex Johnson       │
│                                 │
│ Name                            │
│   Phone:  "Alex J."            │
│   Rin:    "Alexander Johnson"   │
│                                 │
│   [Keep Phone]  [Keep Rin]      │
│                                 │
│ Email                           │
│   Phone:  alex@gmail.com        │
│   Rin:    alex.j@work.com       │
│                                 │
│   [Keep Phone]  [Keep Rin]      │
│   [Keep Both]                   │
└─────────────────────────────────┘
```

- Per-field resolution. User picks which version to keep for each conflicting field.
- Non-conflicting fields merge silently (e.g., phone added a birthday, Rin added an email — both kept).
- Conflicts surface as a "Needs attention" card in the smart sections home view.

### 4.3 Conflict Deferral

- User can dismiss conflict card without resolving.
- Conflict persists in "Needs attention" section until resolved.
- No data is lost while conflict is unresolved — both versions are preserved.

---

## 5) Dedup and Merge

### 5.1 Confidence-Tiered Processing

| Confidence | Behavior | User action |
|-----------|----------|-------------|
| **95%+** | Auto-merge silently | None. Appears in "Recent merges" for review/undo |
| **70-95%** | Shown as suggestion | User reviews and confirms or dismisses |
| **Below 70%** | Not suggested | No action. System does not surface low-confidence noise |

### 5.2 Merge Suggestion Card

Each suggestion shows confidence level and matching evidence:

```
┌─────────────────────────────────┐
│ 🔗 Possible duplicate (87%)    │
│                                 │
│ Alex Johnson  ↔  Alex J.        │
│                                 │
│ Why matched:                    │
│  • Same phone: +1 555-0123     │
│  • Similar name (87% match)    │
│  • 4 shared network connections │
│                                 │
│ [Merge]  [Not the same]  [Skip]│
└─────────────────────────────────┘
```

**Evidence types shown:**
- Matching phone number(s)
- Matching email address(es)
- Name similarity percentage
- Shared network connections (if both are Rin users or appear in mutual contacts)
- Matching employer domain

### 5.3 Merge Execution

When user confirms a merge:
1. System creates a merged contact preserving all fields from both sources.
2. If fields conflict (two different emails), both are kept.
3. Merge is recorded in audit ledger with source attribution.
4. Merge is fully reversible — undo available from contact detail and "Recent merges" list.

### 5.4 Auto-Merge Review

High-confidence auto-merges appear in a dedicated review list:
- Accessible from home smart section: `"12 contacts auto-merged"`
- Each entry shows what was merged and why.
- One-tap undo per merge. Undo restores both original contacts.

### 5.5 Two-Level Dedup (from architecture)

**Level 1 — User-data inference:**
- Probabilistic matching from phone/email/name patterns.
- Runs entirely on user's own imported data.
- Powers the confidence percentages shown to user.

**Level 2 — Network-grounded certainty:**
- Uses confirmed identities from the Rin network graph.
- Example: two contacts both verified the same phone number on Rin → definite match.
- Level 2 matches always score 95%+ and auto-merge.
- Privacy guardrail: enrichment does not reveal hidden user data from other accounts.

---

## 6) Network Enrichment

### 6.1 What Gets Enriched

When a contact matches a Rin user, available enrichments include:
- Verified name (from the Rin user's profile)
- Profile photo (if shared with the viewer's circle)
- Additional contact channels (if shared)
- Username

### 6.2 Enrichment Display: Inline Badge

Enriched fields show a small indicator distinguishing them from device-imported data:

```
┌─────────────────────────────────┐
│ Alex Johnson                    │
│                                 │
│ 📱 +1 555-0123          (phone)│
│ 📧 alex@gmail.com       (phone)│
│ 📧 alex@work.com      ✦ (rin) │
│ 🖼 [photo]             ✦ (rin) │
└─────────────────────────────────┘
```

- `✦` badge (or similar subtle indicator) marks Rin-sourced fields.
- Tap badge to see source: `"Added from Alex's Rin profile"`
- Enriched fields are read-only in Rin — they update when the source user changes them.

### 6.3 Enrichment vs Privacy

- Enrichment only surfaces fields the Rin user has explicitly allowed for the viewer's circle.
- If the viewer is not in any circle (or only in Contacts/Public), they see only what that policy allows.
- Shadow profiles are never used as enrichment sources.

---

## 7) Contact List View

### 7.1 Smart Sections (Home View)

The primary contact list uses system-generated sections:

**Needs Attention** (top, collapsible)
- Merge suggestions (70-95% confidence)
- Unresolved conflicts
- Contacts with incomplete data
- Count badge: `"5 items need attention"`

**Recently Added** (if any in last 7 days)
- New contacts from latest sync.
- Each shows source: `"From phone contacts"` or `"Added manually"`.

**By Circle** (main body)
- Contacts grouped by primary circle (most specific circle, not "Contacts").
- Expandable sections per circle with emoji + color + member count.
- Contacts not in any custom circle appear under "Contacts" (the mandatory circle).
- Alphabetical within each circle section.

### 7.2 Filtering and Search

- Circle filter: tap circle chips at top to filter by one or more circles.
- Text search: searches name, phone, email, username across all contacts.
- Sort options: alphabetical (default), recently added, recently contacted.

### 7.3 Contact Detail View

Sections on a contact's detail screen:

1. **Header**: name, photo, username (if Rin user), online status indicator.
2. **Contact channels**: all phone numbers, emails, social accounts, addresses. Enriched fields badged.
3. **Circle membership**: chips showing all circles this contact belongs to, with "+" to add more.
4. **Effective access**: what this person can see of your profile (merged view from circle UX spec).
5. **Provenance**: "Where this info came from" expandable section. Timeline of imports, merges, enrichments.
6. **Actions**: call, message, share contact, remove from Rin.

---

## 8) Manual Contact Entry

### 8.1 Adding Contacts Outside Device Address Book

Users can create contacts directly in Rin that don't exist in the device address book.

**Entry points:**
- "+" button on contact list.
- From search: "No results. Create a new contact?"
- From circle management: "Add contact to this circle" → "Create new"

**Fields available:**
- Name (required)
- Phone number(s)
- Email address(es)
- Username (if known Rin user — auto-fills if found)
- Any other standard fields

**Behavior:**
- Manual contacts are Rin-only. They are NOT written back to the device address book (v1 no-writeback rule).
- If a phone number or email matches an existing contact, prompt: "This looks like [existing contact]. Merge?"
- Manual contacts appear in the "Contacts" mandatory circle by default. User can assign to custom circles.

### 8.2 Adding by Rin Username

- User enters a Rin username.
- If found: pull public profile and create a contact card with allowed fields.
- If not found: show error. No stub creation from username alone.

---

## 9) Permission-Denied Flow

### 9.1 Limited Mode

If user denied contacts permission at onboarding (S6):
- App continues in self-management mode.
- User can: set up profile, configure sharing defaults, manage circles (empty), add manual contacts.
- Home shows value proposition without contact data.

### 9.2 Re-Prompt Strategy: Contextual Only

Re-prompt happens ONLY when user takes an action that requires contacts:
- Tapping "Import contacts" in an empty circle.
- Searching for contacts with no results.
- Viewing the "Needs attention" section (which would be empty without import).

Re-prompt format:
```
┌─────────────────────────────────┐
│ Contacts access needed          │
│                                 │
│ To [action], Rin needs access   │
│ to your contacts.               │
│                                 │
│ [Open Settings]  [Not now]      │
└─────────────────────────────────┘
```

- Links directly to iOS Settings for the app.
- No repeated nagging. If dismissed, only re-prompts on the next distinct action attempt.
- Never uses push notifications for permission re-prompts.

---

## 10) Events

### Import Lifecycle
- `contact.sync_started` — trigger source (onboarding / foreground / background / manual)
- `contact.sync_progressed` — batch number, count imported so far, total estimated
- `contact.sync_completed` — total imported, duration, new contacts count
- `contact.sync_resumed` — after interruption, previous progress state
- `contact.sync_failed` — error type, retry scheduled

### Dedup and Merge
- `dedup.scan_completed` — total duplicates found, confidence tier breakdown
- `dedup.auto_merged` — contact pair, confidence, evidence summary
- `dedup.suggestion_shown` — contact pair, confidence
- `dedup.suggestion_accepted` — contact pair
- `dedup.suggestion_dismissed` — contact pair, reason (not same / skip)
- `dedup.merge_undone` — contact pair, original merge source

### Enrichment
- `enrichment.applied` — contact ID, fields enriched, source user ID (hashed)
- `enrichment.updated` — contact ID, field changed, old/new value

### Conflict
- `conflict.detected` — contact ID, conflicting fields count
- `conflict.resolved` — contact ID, resolution per field (kept phone / kept rin)
- `conflict.deferred` — contact ID

### Manual Entry
- `contact.manual_created` — fields provided, source (direct / search / circle)
- `contact.manual_matched` — matched to existing contact during creation

### Permission
- `permission.reprompt_shown` — trigger action context
- `permission.reprompt_accepted` — user opened settings
- `permission.reprompt_dismissed`

---

## 11) Edge Cases

1. **User has 0 contacts on device**: skip dedup/enrichment phases. Show empty state with manual add CTA and value explanation.
2. **User has 10,000+ contacts**: batch import with progress. Dedup runs incrementally. First-value cards appear before full scan completes.
3. **Contact deleted on device during active sync**: next delta sync removes it from Rin import record. Rin-only data (circle membership, enrichments) preserved with "source removed" notation.
4. **Rin user changes their shared fields**: enrichment updates propagate on next sync or push event. Old values kept in provenance log.
5. **Two device contacts merge on-device (e.g., via iCloud)**: detected as deletion + modification. Rin dedup engine reconciles automatically.
6. **Manual contact later appears in device address book import**: dedup engine detects overlap and suggests merge.
7. **User re-imports after deleting and reinstalling app**: fresh import against server state. Previously merged/enriched data restored from server if user authenticated.
8. **Contact exists in multiple users' imports with different names**: each user sees their own local alias. Rin user's preferred display name shown as enrichment, not replacement.

---

## 12) Accessibility

1. Progress counter and phase labels announced to VoiceOver as they update.
2. Merge suggestion cards are fully navigable with assistive tech. Evidence items are individual VoiceOver elements.
3. Conflict resolution buttons have clear accessible labels: "Keep version from Phone app" / "Keep version from Rin".
4. Enrichment badges announce as "Added from Rin network" on focus.
5. Dynamic Type supported across all import and contact management screens.

---

## 13) Open UX Decisions

1. Exact auto-merge confidence threshold (95% proposed, needs calibration against real data).
2. Whether auto-merged contacts should show a transient notification or only appear in review list.
3. Maximum manual contacts allowed before suggesting device import.
4. Whether conflict cards should auto-dismiss after a timeout period.
5. Background sync frequency for BGAppRefreshTask fallback (daily proposed).
6. Whether to show sync status persistently in app or only during active sync.
7. Import progress animation style and visual treatment for each phase.
