# Contact Notes and History Spec V1

## 1) Purpose

Define the contact notes, timeline, and reminder system for v1. This is the **friend CRM core loop** — the single-player retention feature that gives Rin daily-use value independent of network effects.

The Design Decision Memo (section 4.5) explicitly includes "Notes/history timeline for contacts (friend CRM core loop)" in V1 scope. This spec covers the full notes model, contact timeline view, reminder system, search, and integration with existing contact detail, home tab, and offline storage surfaces.

Core value proposition: **remember context about every person in your network.** When you meet someone, follow up on a conversation, or need to recall what you discussed three months ago — Rin has it. This is the habit loop that brings users back daily.

Companion docs:
- `docs/product/DESIGN_DECISION_MEMO_V1.md` (section 4.5 — V1 scope)
- `docs/product/CONTACTS_IMPORT_SYNC_UX_V1.md` (contact detail section 7.3)
- `docs/product/IOS_PROFILE_CIRCLE_SCREEN_SPEC_V1.md` (profile context)
- `docs/product/CIRCLE_MANAGEMENT_UX_V1.md` (circles context)
- `docs/product/IOS_SEARCH_DISCOVERY_SCREEN_SPEC_V1.md` (search integration)
- `docs/architecture/IOS_OFFLINE_STORAGE_V1.md` (storage model)
- `docs/design/IOS_DESIGN_TOKENS_V1.md` (design tokens)

---

## 2) Entry Points

### 2.1 Contact Detail Screen

New section added to the contact detail view (as defined in CONTACTS_IMPORT_SYNC_UX_V1.md section 7.3). Notes and reminders appear between the existing "Effective access" section (4) and "Provenance" section (5).

Updated contact detail section order:
1. Header
2. Contact channels
3. Circle membership
4. Effective access
5. **Notes** (new)
6. **Upcoming reminders** (new)
7. Provenance
8. Actions

Tapping "See all" on either new section navigates to the full timeline view (N2).

### 2.2 Home Tab Smart Section

New smart section on the Home tab contact list:

| Section | Position | Content | Trigger |
|---------|----------|---------|---------|
| **Upcoming** | After "Needs Attention", before "Recently Added" | Reminders due in the next 7 days | Any active reminder within window |

Card format:
```
┌─────────────────────────────────┐
│ UPCOMING                        │
│                                 │
│ 🎂 Sarah Chen — Birthday Mar 15│
│ 📋 Alex J. — Follow up on      │
│    project proposal — Mar 20    │
│ 📝 3 more this week             │
│                                 │
│          [See All Reminders]    │
└─────────────────────────────────┘
```

Section collapses when no reminders are due in the next 7 days.

### 2.3 Quick-Add from Contact List

Long-press a contact row in the contact list to reveal a context menu:

| Action | Icon | Behavior |
|--------|------|----------|
| Add Note | `square.and.pencil` (SF Symbol) | Opens note creation sheet (N3) pre-filled with contact |
| Add to Circle | `circle.grid.2x2` | Existing circle picker flow |
| Share Contact | `square.and.arrow.up` | Existing share flow |

Quick-add is the lowest-friction path to creating a note: long-press, tap "Add Note", type, save.

### 2.4 Push Notification Deep Link

When a reminder fires as a push notification, tapping the notification navigates directly to the contact's timeline view (N2) with the triggering reminder scrolled into view.

---

## 3) Notes Model

### 3.1 Note Entity

Each note is a discrete record attached to a single contact.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | Yes | Server-assigned unique identifier |
| `contactId` | String | Yes | The contact this note belongs to |
| `profileId` | String | Yes | The principal or shadow profile that owns this note |
| `type` | Enum | Yes | One of: `free`, `meeting`, `reminder`, `birthday`, `milestone` |
| `content` | String | Yes | Plain text, up to 5,000 characters |
| `associatedDate` | Date? | No | Optional date the note is about (e.g., meeting date, birthday) |
| `reminder` | Reminder? | No | Optional attached reminder (see section 6) |
| `createdAt` | Date | Yes | Timestamp of creation |
| `updatedAt` | Date | Yes | Timestamp of last edit |

### 3.2 Content Format: Plain Text (V1)

V1 uses plain text only. No rich text, no markdown rendering, no inline images.

Rationale:
- Minimizes creation friction (no toolbar, no formatting decisions).
- Keeps storage and sync simple.
- Rich text is a v2 candidate after usage patterns are observed.

Line breaks are preserved. URLs in note content are auto-detected and rendered as tappable links.

### 3.3 Note Types

| Type | Icon | Default behavior | Template |
|------|------|-----------------|----------|
| `free` | `note.text` | General note, no structure | None |
| `meeting` | `person.2` | Structured meeting record | Date + attendees + key points + follow-ups |
| `reminder` | `bell` | Note exists primarily to carry a reminder | Reminder toggle pre-enabled |
| `birthday` | `gift` | Birthday record, annual recurrence suggested | Date field pre-focused, recurring reminder suggested |
| `milestone` | `star` | Significant life event (promotion, wedding, etc.) | Date field pre-focused |

The type selector is a horizontal chip bar at the top of the creation sheet. Default selection is `free`. Changing the type adjusts which fields are prominent but never hides the content field.

### 3.4 Ownership and Privacy Rules

**Notes are Rin-only data.**
- Notes are never synced to the device address book.
- Notes are never shared with anyone — not with the contact, not with other Rin users, not with any third party.
- Notes are owned by the creating profile (principal or shadow).

**Per-profile isolation:**
- Each profile (principal and each shadow profile) has its own independent notes for each contact.
- Switching active profile changes which notes are visible on a contact's timeline.
- Shadow profile notes are not visible from the principal profile, and vice versa.

Rationale: a user's professional shadow profile may have meeting notes about a colleague that should not bleed into their personal profile's view of the same contact.

### 3.5 Limits

| Limit | Value | Rationale |
|-------|-------|-----------|
| Note content length | 5,000 characters | Long enough for detailed meeting notes, short enough to encourage conciseness |
| Notes per contact | Unlimited | No artificial cap; pagination handles display |
| Reminders per contact | 50 active | Prevents notification spam; past reminders do not count |

---

## 4) Contact Timeline View

### 4.1 Screen: N2 — Contact Timeline

**Layout:**

```
┌─────────────────────────────────┐
│ ← Back          Alex Johnson    │
│                                 │
│ [All] [Notes] [System] [Search]│
│                                 │
│ ── March 2026 ──────────────── │
│                                 │
│ 📝 Mar 12, 2:30 PM             │
│ Met at Sarah's dinner party.    │
│ Really interesting conversation │
│ about AI ethics.                │
│                      [···]      │
│                                 │
│ 🔗 Mar 10                       │
│ Added to Friends circle         │
│                                 │
│ ── February 2026 ────────────  │
│                                 │
│ 📝 Feb 28, 10:00 AM            │
│ Working on AI project at Acme.  │
│ Interested in collab.           │
│                      [···]      │
│                                 │
│ ⭐ Feb 15                       │
│ Added to Rin                    │
│                                 │
│              [+]                │
└─────────────────────────────────┘
```

**Key elements:**
- Title: contact name in navigation bar.
- Filter bar: horizontal segmented control (All / Notes / System / search icon).
- Timeline: reverse chronological (newest first), grouped by month.
- Floating action button: "+" at bottom-right to create a new note.

### 4.2 Timeline Entry Types

The timeline merges two categories of entries:

**User-created notes** (editable):

| Entry type | Icon | Source |
|-----------|------|--------|
| Free note | `note.text` | User created |
| Meeting note | `person.2` | User created |
| Reminder note | `bell` | User created |
| Birthday note | `gift` | User created or auto-imported |
| Milestone note | `star` | User created |

**System events** (read-only):

| Entry type | Icon | Source |
|-----------|------|--------|
| Added to Rin | `plus.circle` | Contact import or manual creation |
| Merged with another contact | `arrow.triangle.merge` | Dedup merge |
| Enriched | `sparkles` | Network enrichment update |
| Circle change | `circle.grid.2x2` | Added to or removed from a circle |
| Contact edited | `pencil` | Field modified by user or sync |

### 4.3 Timeline Entry Layout

Each entry renders as:

```
[Icon] [Timestamp]                    [···] (overflow menu)
[Content text — up to 3 lines preview]
[Associated date badge, if present]
[Reminder badge, if present]
```

- Icon: SF Symbol, colored by entry type (notes use `rin.brand.primary`, system events use `rin.text.secondary`).
- Timestamp: relative for entries <7 days old ("2 days ago"), absolute date for older ("Mar 12, 2:30 PM").
- Content: truncated to 3 lines in the timeline list. Tap to expand inline.
- Overflow menu (`[···]`): for user notes — Edit, Delete. For system events — no menu.

### 4.4 Filter Bar

| Filter | Behavior |
|--------|----------|
| All | Shows notes and system events interleaved chronologically |
| Notes | Shows only user-created notes (all types) |
| System | Shows only system-generated events |
| Search (icon) | Activates in-timeline search (see section 7) |

Active filter indicated by `rin.brand.primary` color on the selected segment. Filter persists during the session but resets to "All" on next visit.

### 4.5 States

| State | Behavior |
|-------|----------|
| Default | Timeline loaded with entries |
| Empty (no notes, no events) | "No history yet. Add your first note." with prominent "+" CTA |
| Empty (no notes, has events) | System events shown; "Add a note about [Name]" prompt above first event |
| Loading | Skeleton placeholders for 3 entries |
| Error | "Could not load timeline. Pull to retry." |
| Offline | Cached entries shown; "Offline — showing cached data" banner |

### 4.6 Pagination

- Initial load: 20 entries.
- Infinite scroll: load 20 more when user scrolls within 5 entries of the bottom.
- Month headers are sticky during scroll.
- "Loading more..." spinner at bottom during fetch.

---

## 5) Note Creation Flow

### 5.1 Screen: N3 — Note Creation Sheet

Presented as a modal sheet (half-sheet by default, expandable to full-screen by drag).

**Layout:**

```
┌─────────────────────────────────┐
│ Cancel          Add Note   Save │
│                                 │
│ [Free] [Meeting] [Reminder]     │
│ [Birthday] [Milestone]          │
│                                 │
│ ┌─────────────────────────────┐ │
│ │ Write your note...          │ │
│ │                             │ │
│ │                             │ │
│ └─────────────────────────────┘ │
│                                 │
│ 📅 Add date (optional)          │
│ 🔔 Set reminder (optional)      │
│                                 │
└─────────────────────────────────┘
```

### 5.2 Fields

| Field | Component | Required | Default |
|-------|-----------|----------|---------|
| Type selector | Horizontal chip bar | Yes | `free` |
| Content | Multi-line text field, auto-focus on open | Yes | Empty, placeholder: "Write your note..." |
| Associated date | Date picker (tap to reveal) | No | None |
| Reminder toggle | Toggle + date/time picker | No | Off |

### 5.3 Type-Specific Behavior

**Free note**: content field only. Date and reminder are optional add-ons.

**Meeting note**: content field with structured placeholder:

```
Date: [auto-filled if associated date set]
Who was there:
Key points:
Follow-up items:
```

The placeholder is suggestive, not enforced. User can type freely and ignore the template. The template text disappears as soon as the user begins typing.

**Reminder note**: reminder toggle pre-enabled. Content field placeholder: "What do you want to remember?"

**Birthday note**: associated date field pre-focused with date picker open. If the contact has a birthday imported from device contacts, it auto-fills. Recurring annual reminder suggested (toggle pre-enabled).

**Milestone note**: associated date field pre-focused. Content placeholder: "What happened?"

### 5.4 Save Behavior

- "Save" button enabled when content field is non-empty (at least 1 non-whitespace character).
- Save is immediate. No drafts in v1.
- On save: sheet dismisses, new entry appears at top of timeline with brief insert animation.
- If offline: note saved to local SwiftData cache and queued for sync. Toast: "Saved. Will sync when online."
- Cancel with unsaved text: confirmation dialog ("Discard note?").

### 5.5 Edit Flow

- Tap overflow menu (`[···]`) on any user-created note → "Edit".
- Opens N3 sheet pre-filled with existing note content and metadata.
- Same save behavior. `updatedAt` timestamp updated.
- No edit history in v1 (edited notes do not show "edited" indicator).

### 5.6 Delete Flow

- Tap overflow menu → "Delete".
- Confirmation dialog: "Delete this note? This cannot be undone."
- On confirm: note removed from timeline with collapse animation.
- If note had an active reminder: reminder is also deleted.
- Deletion is a soft-delete server-side (retained 30 days for data recovery), but immediately removed from the user's view.

---

## 6) Reminders

### 6.1 Reminder Entity

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | Yes | Unique identifier |
| `noteId` | String? | No | The note this reminder is attached to (null for standalone contact reminders) |
| `contactId` | String | Yes | The contact this reminder is for |
| `profileId` | String | Yes | Owning profile |
| `type` | Enum | Yes | `one_time` or `recurring` |
| `scheduledAt` | Date | Yes | Next trigger date/time |
| `recurrenceRule` | String? | No | For recurring: `annual` (birthdays), `monthly`, `weekly` |
| `status` | Enum | Yes | `active`, `snoozed`, `dismissed`, `completed` |
| `title` | String | Yes | Short summary shown in notification and smart section |
| `createdAt` | Date | Yes | Creation timestamp |

### 6.2 Reminder Types

**One-time**: fires at a specific date and time, then moves to `completed` status.

**Recurring**: fires at scheduled intervals. After each trigger, the system computes the next occurrence and keeps the reminder `active`.

| Recurrence | Behavior | Primary use |
|-----------|----------|-------------|
| Annual | Same month/day each year | Birthdays, anniversaries |
| Monthly | Same day each month | Regular check-in reminders |
| Weekly | Same day each week | Frequent follow-up cycles |

### 6.3 Birthday Auto-Import

When a contact has a birthday in the device address book:
1. On first import, Rin creates a birthday note with the date.
2. An annual recurring reminder is attached, set to fire at 9:00 AM local time on the birthday.
3. The auto-imported birthday appears in the timeline as a birthday note with a "From device contacts" source badge.
4. User can edit or delete the auto-imported birthday like any other note.

If the birthday is removed from device contacts on a subsequent sync, the Rin note and reminder persist (Rin-only data is not deleted by device changes).

### 6.4 Reminder Creation

Reminders can be created in two ways:

**Attached to a note**: toggle "Set reminder" during note creation (N3). User picks date/time and optional recurrence.

**Standalone from contact detail**: in the "Upcoming" section of contact detail, tap "Add Reminder". This creates a minimal note of type `reminder` with the reminder pre-configured.

### 6.5 Reminder Surfaces

Reminders appear in four locations:

| Surface | Display | Behavior |
|---------|---------|----------|
| Push notification | `"[Contact Name]: [Reminder title]"` | Tap → deep link to contact timeline (N2) |
| Home tab smart section | Card in "Upcoming" section (see section 2.2) | Tap card → contact timeline |
| Contact detail "Upcoming" section | Inline list of upcoming reminders for this contact | Tap → expand or navigate to timeline |
| Contact list badge | Small `bell` indicator on contacts with reminders due today | Visual indicator only |

### 6.6 Reminder Actions

When a reminder fires (via push notification or in-app surface):

| Action | Behavior |
|--------|----------|
| **View** | Navigate to contact timeline |
| **Snooze** | Reschedule: +1 hour, +1 day, +1 week (picker) |
| **Dismiss** | Mark as dismissed; does not fire again (one-time) or skips this occurrence (recurring) |
| **Complete** | Mark as completed; same as dismiss for one-time; for recurring, skips this occurrence |

Snooze options presented as an action sheet. Default snooze is +1 day.

### 6.7 Reminder Management

All active and upcoming reminders for a contact are visible in:
- The contact's timeline view (N2), filterable under "Notes" filter.
- The contact detail "Upcoming" section.

Editing a reminder: tap the reminder in timeline → overflow menu → "Edit Reminder" → modify date/time/recurrence.

Deleting a reminder: deleting the parent note also deletes the reminder. Or: edit the note and toggle the reminder off.

### 6.8 Past Reminders

Reminders with a `scheduledAt` date in the past and status `completed` or `dismissed` appear in the timeline as past events (not as active reminders). They render with a muted style (`rin.text.secondary` color) and a "Completed" or "Dismissed" badge.

### 6.9 Notification Permissions

Rin must request push notification permission to deliver reminder notifications.

- If notification permission is granted: reminders fire as push notifications at the scheduled time.
- If notification permission is denied: reminders appear only in-app (Home tab smart section and contact detail). No push notification.
- Re-prompt strategy: contextual only, matching the pattern from CONTACTS_IMPORT_SYNC_UX_V1.md section 9.2. When user creates a reminder without notification permission, show: "To get notified about this reminder, enable notifications in Settings." with an "Open Settings" button.

---

## 7) Search Within Notes

### 7.1 In-Timeline Search

Activated by tapping the search icon in the filter bar on the timeline view (N2).

**Layout:**

```
┌─────────────────────────────────┐
│ ← Back          Alex Johnson    │
│                                 │
│ 🔍 [Search notes...        ] X │
│                                 │
│ 3 results for "project"         │
│                                 │
│ 📝 Feb 28                       │
│ Working on AI **project** at    │
│ Acme. Interested in collab.     │
│                                 │
│ 👥 Jan 15                       │
│ Discussed **project** timeline  │
│ and deliverables.               │
│                                 │
│ 📝 Dec 3, 2025                  │
│ **Project** idea: shared doc... │
│                                 │
└─────────────────────────────────┘
```

- Searches only the current contact's notes (not system events).
- Full-text search across note content.
- Matching substring highlighted in bold within results.
- Results ordered by relevance (exact match > partial match), with recency as tiebreaker.
- Minimum query length: 2 characters.
- Search is local-first (SwiftData cache), with server fallback for notes not yet cached.

### 7.2 Global Note Search

Accessible from the main contact search (S1 in IOS_SEARCH_DISCOVERY_SCREEN_SPEC_V1.md).

When a search query matches note content but not the contact's name, phone, or email:
- The contact appears in search results with match context showing the note snippet.
- Result row format: `[Photo] Contact Name / "...matching note text..." (note)`

This enables finding contacts by what you wrote about them, not just by their name or number.

**Search behavior:**
- Local-first: searches `CachedNote` in SwiftData.
- Server search triggered for queries >= 3 characters (same pattern as contact search).
- Results merge below direct contact matches.

### 7.3 Global Note Search Result Row

```
┌────────────────────────────────────┐
│ [Photo] Alex Johnson               │
│         "...working on AI project  │
│         at Acme..." (note)         │
│         Friends · Colleagues       │
│                         [arrow >]  │
└────────────────────────────────────┘
```

- Photo: 40pt circle thumbnail (matches existing search result row from IOS_SEARCH_DISCOVERY_SCREEN_SPEC_V1.md section 4.1).
- Match context: note snippet with matching term highlighted, prefixed with "(note)" badge.
- Circle badges below as in standard search results.

---

## 8) Privacy and Storage

### 8.1 Server-Side Storage

Notes are stored on Rin servers, associated with the owning user's account.

- Notes sync across devices when the user logs in on a new device.
- Notes are encrypted in transit (TLS) and at rest (server-side encryption).
- Notes are included in account data export (GDPR compliance).
- Notes are permanently deleted 30 days after account deletion.

### 8.2 Privacy Guarantees

| Guarantee | Enforcement |
|-----------|------------|
| Notes are never shared | No API endpoint exposes notes to other users. Server enforces owner-only access. |
| Notes are never used for recommendations | Notes content is not fed into graph analysis, enrichment, or ranking services. |
| Notes are per-profile | Shadow profiles maintain independent note collections. Switching profiles shows only that profile's notes. |
| Notes are not searchable by others | No cross-user note search exists. Notes are invisible to the contact they are about. |

### 8.3 Offline Storage (SwiftData)

New SwiftData model added to the local cache (extends the models in IOS_OFFLINE_STORAGE_V1.md section 3):

```
CachedNote
├── id: String (server note ID)
├── contactId: String
├── profileId: String
├── type: String (free/meeting/reminder/birthday/milestone)
├── content: String
├── associatedDate: Date?
├── hasReminder: Bool
├── reminderScheduledAt: Date?
├── reminderType: String? (one_time/recurring)
├── reminderStatus: String? (active/snoozed/dismissed/completed)
├── reminderRecurrenceRule: String?
├── createdAt: Date
├── updatedAt: Date
├── lastSyncedAt: Date
├── pendingSync: Bool (true if created/edited offline)
```

```
CachedTimelineEvent
├── id: String (server event ID)
├── contactId: String
├── profileId: String
├── eventType: String (added_to_rin/merged/enriched/circle_change/contact_edited)
├── description: String
├── metadata: String? (JSON — e.g., circle name, merge details)
├── occurredAt: Date
├── lastSyncedAt: Date
```

### 8.4 Cache Freshness

| Data type | Freshness window | Stale indicator |
|-----------|-----------------|-----------------|
| Notes | 1 hour | None (background refresh) |
| Timeline events | 24 hours | None |
| Reminders | Real-time (push-triggered) | None |

### 8.5 Offline Behavior

| Feature | Offline behavior |
|---------|-----------------|
| View timeline | Cached data displayed |
| Create note | Saved to SwiftData, queued for sync |
| Edit note | Saved locally, queued for sync |
| Delete note | Marked deleted locally, queued for sync |
| Search notes (in-timeline) | Local search over cached notes |
| Search notes (global) | Local search only; server results unavailable |
| Create reminder | Saved locally; push notification scheduled locally via `UNUserNotificationCenter` |
| Snooze/dismiss reminder | Applied locally, queued for sync |

Mutation queue follows the same pattern as IOS_OFFLINE_STORAGE_V1.md section 5.2: mutations are queued and replayed when connectivity resumes.

### 8.6 Sync Conflict Resolution

If a note is edited on two devices while offline:
- Last-write-wins based on `updatedAt` timestamp.
- No user-facing conflict resolution for notes in v1 (unlike contact field conflicts which use the user-decides model from CONTACTS_IMPORT_SYNC_UX_V1.md section 4.2).
- Rationale: notes are single-author private data; simultaneous cross-device editing is rare and the cost of losing a minor edit is low compared to the complexity of a conflict UI.

---

## 9) Contact Detail Integration

### 9.1 Notes Section

New section in the contact detail view, positioned after "Effective access" and before "Provenance."

**Layout:**

```
┌─────────────────────────────────┐
│ NOTES (3)                       │
│                                 │
│ 📝 "Met at Sarah's dinner       │
│    party" — 2 days ago          │
│                                 │
│ 👥 "Working on AI project,      │
│    interested in..." — 1 week   │
│                                 │
│ 📝 "Former colleague at Acme"   │
│    — 3 weeks ago                │
│                                 │
│          [+ Add Note]           │
│          [See all →]            │
└─────────────────────────────────┘
```

- Shows the 3 most recent notes (not system events).
- Each note: type icon, truncated content (1 line), relative timestamp.
- Tap a note: expand inline to show full content, or navigate to timeline if content is long (>5 lines).
- "[+ Add Note]" opens N3 (note creation sheet).
- "[See all]" navigates to N2 (full timeline view).

**States:**

| State | Display |
|-------|---------|
| Has notes | Up to 3 recent notes + Add Note + See All |
| No notes | "No notes yet" + prominent [+ Add Note] button |

### 9.2 Upcoming Reminders Section

New section below Notes, above Provenance.

**Layout:**

```
┌─────────────────────────────────┐
│ UPCOMING                        │
│                                 │
│ 🎂 Birthday: March 15           │
│ 📋 Follow up on project         │
│    proposal — Mar 20            │
│                                 │
│       [+ Add Reminder]          │
└─────────────────────────────────┘
```

- Shows all active reminders for this contact, sorted by `scheduledAt` ascending (soonest first).
- Each reminder: type icon, title, scheduled date.
- Tap a reminder: navigate to the parent note in timeline view.
- "[+ Add Reminder]" creates a new reminder-type note via N3.
- Section hidden entirely if the contact has no active reminders and no past reminders.

---

## 10) Events (Analytics)

### Note Lifecycle

| Event | Properties |
|-------|-----------|
| `note.created` | `type`, `character_count`, `has_associated_date`, `has_reminder`, `source` (timeline / quick_add / contact_detail) |
| `note.edited` | `note_id`, `type`, `character_count_delta` |
| `note.deleted` | `note_id`, `type`, `age_days` (days since creation) |
| `note.expanded` | `note_id`, `source` (timeline / contact_detail) |

### Reminder Lifecycle

| Event | Properties |
|-------|-----------|
| `reminder.created` | `type` (one_time / recurring), `recurrence_rule`, `days_until_trigger`, `source` (note_attachment / standalone) |
| `reminder.triggered` | `reminder_id`, `type`, `delivery` (push / in_app_only) |
| `reminder.snoozed` | `reminder_id`, `snooze_duration` (1h / 1d / 1w) |
| `reminder.dismissed` | `reminder_id`, `type` |
| `reminder.completed` | `reminder_id`, `type` |
| `reminder.edited` | `reminder_id`, `fields_changed` |
| `reminder.deleted` | `reminder_id`, `type`, `was_active` |

### Timeline

| Event | Properties |
|-------|-----------|
| `timeline.viewed` | `contact_id`, `entry_count`, `source` (contact_detail / notification / search) |
| `timeline.filtered` | `filter` (all / notes / system) |
| `timeline.scrolled` | `depth` (how many entries scrolled past) |
| `timeline.searched` | `query_length`, `result_count` |

### Global Note Search

| Event | Properties |
|-------|-----------|
| `note.search_global` | `query_length`, `result_count`, `contacts_matched` |
| `note.search_global_tapped` | `contact_id`, `note_id` |

### Birthday Auto-Import

| Event | Properties |
|-------|-----------|
| `birthday.auto_imported` | `contact_id`, `reminder_created` (bool) |
| `birthday.auto_import_edited` | `contact_id`, `field_changed` |
| `birthday.auto_import_deleted` | `contact_id` |

---

## 11) Accessibility

### 11.1 VoiceOver

| Element | VoiceOver label |
|---------|----------------|
| Timeline entry (note) | "[Type] note, [relative timestamp]. [Content preview]. Actions available." |
| Timeline entry (system event) | "System event, [relative timestamp]. [Description]." |
| Filter bar segment | "[Filter name], [selected/not selected]" |
| Note creation sheet | "Add note for [Contact Name]" |
| Type selector chip | "[Type name], [selected/not selected]" |
| Reminder badge on contact list | "[Contact Name], reminder due [date]" |
| Upcoming card on Home tab | "Upcoming reminders. [Count] reminders this week." |

All interactive elements within timeline entries (edit, delete, expand) are accessible as VoiceOver actions via the rotor or custom actions.

### 11.2 Dynamic Type

- Note content respects Dynamic Type from `rin.type.body` (17pt base) through `AX5`.
- Timeline timestamps use `rin.type.footnote` (13pt base).
- Section headers use `rin.type.headline` (17pt semibold base).
- Month separators use `rin.type.subheadline` (15pt base).
- At large accessibility sizes, timeline entries stack vertically (icon above content instead of inline).

### 11.3 Reduce Motion

- If "Reduce Motion" is enabled, note insertion/deletion animations are replaced with fade transitions.
- Scroll-to-reminder on deep link uses instant positioning instead of animated scroll.

### 11.4 Keyboard Navigation (iPad)

- Tab key cycles through filter segments, timeline entries, and action buttons.
- Return key on a timeline entry expands it.
- Cmd+N opens note creation sheet.
- Escape dismisses creation sheet (with discard confirmation if content exists).

---

## 12) Edge Cases

### 12.1 Contact Merged

When two contacts are merged (via dedup):
- Notes from both contacts are combined into a single timeline.
- Each note retains its original `createdAt` timestamp, so they interleave correctly chronologically.
- A system event "Merged with [Other Contact]" appears in the timeline at the merge timestamp.
- Reminders from both contacts are preserved and remain active.
- If both contacts had birthday notes with different dates: both are preserved. User can delete the incorrect one.

If the merge is undone:
- Notes return to their original contacts based on which contact they were originally created for.
- The "Merged" system event is replaced with a "Merge undone" system event.

### 12.2 Contact Deleted

When a contact is removed from Rin:
- Notes are soft-deleted (retained server-side for 30 days).
- If the contact is restored (from "Recently Deleted" or by re-import and match), notes are re-attached.
- After 30 days without restoration, notes are permanently deleted.
- Active reminders for a deleted contact are canceled immediately.

### 12.3 Large Note Volume (100+ Notes)

- Pagination handles display (20 entries per page, infinite scroll).
- Month headers remain sticky for orientation.
- Filter bar helps narrow the view (Notes / System).
- Search becomes the primary navigation tool for contacts with many notes.
- Performance: SwiftData queries are indexed on `contactId` + `profileId` + `createdAt` for efficient pagination.

### 12.4 Reminders for Past Dates

- A reminder with `scheduledAt` in the past displays as a past event in the timeline.
- It does not fire a push notification retroactively.
- If a reminder was in `active` status and the date has passed (e.g., app was not opened), it fires immediately on next app launch and moves to `completed`.

### 12.5 Contact Not Yet in Rin

- Notes can only be created for contacts that exist in Rin (imported or manually added).
- There is no path to create a note for a person who is not a Rin contact.
- If a user wants to note something about a person not in their contacts, they must first add the contact.

### 12.6 Profile Switching

- When the active profile switches (principal to shadow or vice versa), the timeline view reloads to show only the new active profile's notes.
- System events are shared across profiles (they describe the contact, not the user's notes).
- If a user views a contact's timeline as Profile A, switches to Profile B, and returns to the same contact, they see Profile B's notes.

### 12.7 Device Time Zone Changes

- Reminder `scheduledAt` is stored as UTC on the server.
- Local notification scheduling uses the device's current time zone.
- If a user travels across time zones, reminders fire at the correct local time in the new zone.
- Associated dates on notes are stored as date-only (no time component) and are not affected by time zone.

### 12.8 Simultaneous Note Creation (Multi-Device)

- Two notes created at nearly the same time on different devices are both preserved (no conflict).
- Sync reconciliation uses server-assigned IDs; duplicate prevention relies on the server rejecting duplicate `id` values (not content dedup).

---

## 13) Navigation Map

```
Home Tab
├── Upcoming Smart Section
│   ├── Tap reminder card → N2 (Contact Timeline)
│   └── "See All Reminders" → N5 (All Reminders, future)
├── Contact List
│   ├── Long-press → Context Menu → "Add Note" → N3 (Note Creation)
│   └── Tap contact → Contact Detail
│       ├── Notes Section
│       │   ├── Tap note → Expand inline / N2
│       │   ├── [+ Add Note] → N3
│       │   └── [See all] → N2
│       └── Upcoming Section
│           ├── Tap reminder → N2
│           └── [+ Add Reminder] → N3 (reminder type)
└── Search → Global note search results → Contact Detail / N2

N2: Contact Timeline
├── Filter bar (All / Notes / System / Search)
├── Timeline entries
│   ├── Tap note → Expand inline
│   ├── [···] → Edit → N3 (edit mode)
│   └── [···] → Delete → Confirmation
├── [+] FAB → N3 (Note Creation)
└── Search → In-timeline search results

N3: Note Creation Sheet
├── Type selector
├── Content field
├── Date picker (optional)
├── Reminder picker (optional)
└── Save / Cancel

Push Notification
└── Tap → N2 (Contact Timeline, scrolled to reminder)
```

---

## 14) Design Token Usage

| Element | Token | Value |
|---------|-------|-------|
| Timeline background | `rin.bg.primary` | White / Black |
| Month separator | `rin.text.secondary` + `rin.type.subheadline` | Grey, 15pt |
| Note content text | `rin.text.primary` + `rin.type.body` | Body text, 17pt |
| Timestamp text | `rin.text.secondary` + `rin.type.footnote` | Grey, 13pt |
| Note icon (user) | `rin.brand.primary` | Blue |
| System event icon | `rin.text.tertiary` | Light grey |
| Reminder badge (active) | `rin.brand.warning` | Amber |
| Reminder badge (past) | `rin.text.secondary` | Grey |
| Birthday icon | `rin.brand.error` | Red (matches celebration) |
| Milestone icon | `rin.brand.accent` | Purple |
| Filter bar active | `rin.brand.primary` | Blue |
| Filter bar inactive | `rin.text.secondary` | Grey |
| FAB background | `rin.brand.primary` | Blue |
| FAB icon | `rin.bg.primary` | White |
| Note card (contact detail) | `rin.bg.secondary` with `rin.radius.lg` | Card background, 12pt radius |
| Upcoming section card | `rin.bg.secondary` with `rin.radius.lg` | Card background, 12pt radius |
| Creation sheet background | `rin.bg.primary` | White / Black |
| Type selector chip (selected) | `rin.brand.primary` background, white text | Blue chip |
| Type selector chip (unselected) | `rin.bg.tertiary` background, `rin.text.primary` text | Grey chip |
| Content text field | `rin.bg.tertiary` background, `rin.radius.md` | Input field |

### Animation Tokens

| Animation | Duration | Curve | Usage |
|-----------|----------|-------|-------|
| Note insert | 250ms | `.spring(response: 0.25, dampingFraction: 0.8)` | New note appears in timeline |
| Note delete | 200ms | `.easeInOut` | Note removed from timeline |
| Sheet present | 300ms | `.spring(response: 0.3)` | Note creation sheet |
| Filter switch | 200ms | `.easeInOut` | Timeline filter animation |
| Inline expand | 250ms | `.spring(response: 0.25)` | Note content expansion |

---

## 15) Open Decisions

1. **Rich text in v2**: Should v2 support markdown formatting, or should notes remain plain text with only link detection? Rich text adds toolbar complexity and storage overhead. Usage data from v1 plain text adoption should inform this.

2. **Shared notes between profiles**: Should there be an option to share a note across all profiles (principal + shadows) for a contact, or should per-profile isolation be absolute? Use case: a user may want their birthday reminder to exist across all profiles.

3. **Note templates**: Should users be able to create custom note templates beyond the built-in meeting template? E.g., "Coffee chat", "Interview debrief", "Conference connection". Templates could reduce friction for power users but add UX surface area.

4. **All Reminders view**: Should there be a dedicated screen (N5) showing all reminders across all contacts, accessible from the Home tab "Upcoming" section? The current spec surfaces reminders per-contact and in the Home smart section, but a unified reminders management view may be needed for users with many active reminders.

5. **Note attachments (v2)**: Should v2 allow attaching photos or files to notes? Use case: photo of a business card, screenshot of a conversation, document shared during a meeting. Adds significant storage and sync complexity.

6. **Suggested reminders**: Should Rin proactively suggest follow-up reminders based on note content? E.g., if a note mentions "follow up next week", suggest creating a reminder. This crosses into AI-assisted features and may conflict with the "low-noise utility" positioning.
