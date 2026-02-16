# Blocked Users and Blocking Behavior Spec V1

## 1) Purpose

Define the complete blocking system for Rin iOS v1: how users block other profiles, what blocking does across both sides of the relationship, how blocking interacts with shadow profiles, how to unblock, and how blocking integrates with abuse reporting and escalation.

Blocking is a privacy and safety primitive. It must be easy to invoke, immediately effective, silent toward the blocked party, and reversible by the blocker. The system must handle the complexity of Rin's multi-profile (shadow) architecture without leaking identity connections to either party.

Companion docs:
- `docs/design/IOS_KEY_SCREEN_WIREFRAMES_V1.md` (section 11 -- Settings, "Blocked Users" row)
- `docs/product/SHADOW_PROFILE_UX_V1.md` (section 9 -- abuse controls, shadow-specific blocking)
- `docs/product/CIRCLE_MANAGEMENT_UX_V1.md` (access control model, circle membership)
- `docs/product/CONTACTS_IMPORT_SYNC_UX_V1.md` (contact management, enrichment)
- `docs/operations/DISPUTE_PLAYBOOK_V1.md` (dispute escalation, case type C6)
- `docs/architecture/PROFILE_CLASS_CONTRACT_V1.md` (class-aware security controls)
- `docs/design/IOS_DESIGN_TOKENS_V1.md` (tokens and components)
- `docs/product/IOS_CONTACT_NOTES_HISTORY_SPEC_V1.md` (notes preservation on block)
- `docs/product/IOS_SEARCH_DISCOVERY_SCREEN_SPEC_V1.md` (search visibility)

---

## 2) Block Entry Points

Users can initiate a block from four surfaces. All entry points converge on the same confirmation dialog (BLK1, section 3).

### 2.1 Contact Detail -- Three-Dot Menu

From a contact's detail screen (as defined in CONTACTS_IMPORT_SYNC_UX_V1.md section 7.3):
- Tap the three-dot overflow menu (`...`) in the navigation bar.
- Menu items: "Share Contact", "Add to Circle", **"Block"**, "Delete Contact".
- "Block" uses `rin.brand.error` color and `nosign` SF Symbol to signal destructive intent.
- Tapping "Block" opens the BLK1 confirmation dialog.

### 2.2 Search Result -- Long-Press

From the search results screen (IOS_SEARCH_DISCOVERY_SCREEN_SPEC_V1.md):
- Long-press on any search result row to reveal a context menu.
- Context menu includes: "View Profile", "Add to Contacts", **"Block"**.
- "Block" appears as the last item with destructive styling.
- Tapping "Block" opens the BLK1 confirmation dialog.

### 2.3 Security Inbox -- Access Request

From the Security Inbox (referenced in IOS_KEY_SCREEN_WIREFRAMES_V1.md section 7, "Security Inbox" row):
- When viewing an incoming access request (Ask flow from CIRCLE_MANAGEMENT_UX_V1.md section 3.3):
  - Actions: "Approve", "Deny", **"Block this person"**.
  - "Block this person" appears below the primary actions, separated by a divider.
  - Tapping opens the BLK1 confirmation dialog with the requester's name pre-filled.

### 2.4 Profile View

When viewing another Rin user's public profile (reachable via search, shared link, or enrichment badge tap):
- Three-dot overflow menu in navigation bar.
- Menu items: "Add to Contacts", "Share Profile", **"Block"**.
- "Block" uses destructive styling.
- Tapping "Block" opens the BLK1 confirmation dialog.

### 2.5 Entry Point Summary

| Surface | Gesture | Menu position |
|---------|---------|---------------|
| Contact Detail | Tap three-dot menu | Last before "Delete Contact" |
| Search Result | Long-press context menu | Last item |
| Security Inbox | Inline action on access request | Below Approve/Deny |
| Profile View | Tap three-dot menu | Last item |

---

## 3) Block Confirmation Dialog (BLK1)

### 3.1 Layout

```
┌──────────────────────────────────┐
│                                  │
│       Block Alice Johnson?       │
│                                  │
│  They won't be able to find      │
│  your profile, see your info,    │
│  or send you access requests.    │
│  They won't be notified.         │
│                                  │
│  ┌────────────────────────────┐  │
│  │ ☐ Also report for abuse   │  │
│  └────────────────────────────┘  │
│                                  │
│  ┌────────────────────────────┐  │
│  │          Block             │  │
│  └────────────────────────────┘  │
│                                  │
│          Cancel                  │
│                                  │
└──────────────────────────────────┘
```

### 3.2 Dialog Elements

| Element | Spec |
|---------|------|
| Title | "Block [Display Name]?" -- `rin.type.title3` (20pt semibold) |
| Body | "They won't be able to find your profile, see your info, or send you access requests. They won't be notified." -- `rin.type.body` (17pt regular), `rin.text.secondary` |
| Report checkbox | "Also report for abuse" -- `rin.type.callout` (16pt regular). Unchecked by default. |
| Block button | Full-width, `rin.brand.error` background, white text. `SecondaryButton` destructive variant. |
| Cancel | Text-only, `rin.brand.primary` color. Centered below Block button. |

### 3.3 Behavior

- Presented as a system-style alert dialog (`.alert` modifier in SwiftUI).
- Tap "Block" without checkbox: executes block immediately. No further steps.
- Tap "Block" with checkbox checked: executes block AND opens the Report flow (section 9).
- Tap "Cancel": dismisses dialog with no action.
- Dialog is non-dismissible by background tap (requires explicit Cancel or Block).

### 3.4 States

| State | Behavior |
|-------|----------|
| Default | Dialog shown, Block button enabled, checkbox unchecked |
| Processing | Block button shows loading spinner, all inputs disabled |
| Success | Dialog dismisses, toast: "Blocked." Contact view updates immediately |
| Error | Toast: "Could not block. Try again." Dialog remains open for retry |
| Offline | Block applied locally, queued for sync. Toast: "Blocked. Will sync when online." |

---

## 4) What Blocking Does (Bidirectional Effects)

Blocking is bidirectional and immediate. Both sides experience changes, but the blocked person receives no notification or indication that they have been blocked.

### 4.1 Effects on the Blocker's View

| Effect | Detail |
|--------|--------|
| Contact list | Blocked person removed from contact list view. Hidden, not deleted. Does not appear in any circle member list. |
| Enrichment | Blocked person's enrichment data no longer displayed on their contact card. Enriched fields (marked with `✦` badge per CONTACTS_IMPORT_SYNC_UX_V1.md section 6.2) are stripped. |
| Search | Blocked person does not appear in the blocker's search results (contact search or global search). |
| Access requests | Blocked person cannot send access requests (Ask flow) to the blocker. |
| Profile viewing | Blocked person's profile is not viewable by the blocker. If the blocker navigates to the blocked person's profile via deep link, they see "Profile not available." |
| Notes and timeline | Historical notes preserved. Contact name displayed as "[Blocked]" with a muted style in the timeline view. Notes remain accessible from the Blocked Users list (BLK2, section 7). |
| Circles | Blocked person automatically removed from all of the blocker's custom circles. They remain in the system "Contacts" circle (hidden from view) to preserve data integrity. |
| Notifications | No further notifications from the blocked person (access requests, enrichment updates, etc.). |

### 4.2 Effects on the Blocked Person's View

| Effect | Detail |
|--------|--------|
| Search | Blocker's profile disappears from the blocked person's search results entirely. |
| Enrichment | Blocker's enrichment data no longer shown on the blocked person's contact card. If the blocker was a Rin user providing enrichment, those `✦`-badged fields are removed. |
| Access requests | Any pending access requests from the blocked person to the blocker are auto-denied silently. No notification of denial. |
| No notification | The blocked person receives no notification, toast, badge, or any other signal that they have been blocked. |
| Profile via direct link | If the blocked person attempts to view the blocker's profile via a direct link or shared URL, they see: "Profile not available." No indication that this is due to a block. |
| Invite links | If the blocked person sends an invite link to the blocker: the invite is silently ignored. No error shown to the sender. |

### 4.3 Graph and Ranking Effects

| Effect | Detail |
|--------|--------|
| Edge exclusion | The edge between the blocker and the blocked person is excluded from all ranking computation. Neither party's Rin Score is influenced by the other. |
| Silent recalculation | Score recalculates silently after the block. No score change notification is generated specifically for the block event. The recalculated score appears as a normal periodic update. |
| Search projections | Search index projections are updated to exclude the blocked relationship on both sides. |

### 4.4 Data Preservation

Blocking does NOT delete any data. All of the following are preserved:
- Contact record (hidden from the blocker's contact list but not deleted)
- Notes and timeline entries associated with the blocked contact
- Circle membership history (for audit and restore on unblock)
- Merge history and provenance records

This ensures that unblocking (section 8) can fully restore the previous state.

---

## 5) Shadow-Aware Blocking

Rin's multi-profile architecture (SHADOW_PROFILE_UX_V1.md) requires specific blocking rules to maintain identity separation while providing meaningful protection.

### 5.1 Block Scope: Per-Profile

A block operates at the profile level, not the principal level.

- Blocking a shadow profile does NOT block other profiles belonging to the same principal.
- The blocker does not know whether a shadow profile is connected to another profile (per the identity separation guarantee in SHADOW_PROFILE_UX_V1.md section 6.1).
- Each block is an independent edge: `blocker_profile_id -> blocked_profile_id`.

### 5.2 Blocker's Perspective

The blocker sees each profile as an independent identity. If the blocker encounters multiple profiles of the same principal, they must block each one individually. This is intentional -- the blocker has no way to know the profiles are related, and surfacing that information would violate shadow identity separation.

### 5.3 Identity-Linked Escalation

In the case where the blocked person's principal identity is revealed (per SHADOW_PROFILE_UX_V1.md section 6.2, opt-in identity reveal), the system may offer an escalated block:

**Trigger**: The blocker has blocked at least one profile of a principal, AND the blocker has received an identity reveal from another profile of the same principal (meaning the blocker now knows the two profiles are the same person).

**Offer**:
```
┌──────────────────────────────────┐
│                                  │
│   Block all profiles from        │
│   this person?                   │
│                                  │
│   You've blocked [Shadow Name].  │
│   [Primary Name] is the same     │
│   person. Block both?            │
│                                  │
│   [Block All]     [Just This One]│
│                                  │
└──────────────────────────────────┘
```

- "Block All" blocks all known profiles of that principal.
- "Just This One" blocks only the current profile.
- This offer appears only when the identity link is known to the blocker. The system never reveals identity links that the blocker does not already know.

### 5.4 Abuse Rollup

Per SHADOW_PROFILE_UX_V1.md section 9.1 and PROFILE_CLASS_CONTRACT_V1.md section 9:
- Abuse reports from blocking (when the "Also report for abuse" checkbox is checked) count against the principal, not just the reported profile.
- If a principal accumulates sufficient abuse reports across multiple shadow profiles, all shadows may be suspended.
- The blocker is not informed of principal-level enforcement actions.

### 5.5 Shadow Blocking Matrix

| Scenario | Block behavior |
|----------|---------------|
| Block a `single` (Primary) profile | Standard block. Per-profile only. |
| Block a `shadow` profile | Block applies to that shadow only. Other shadows and primary unaffected. |
| Block an `employee` profile | Block applies to that employee profile. Business profile and personal profile unaffected. |
| Block a `business` profile | Block applies to the business profile. Employee profiles of that org unaffected. |
| Blocker has multiple profiles | Each of the blocker's profiles manages its own block list independently. Blocking from Profile A does not block from Profile B. |

---

## 6) Block Execution Sequence

When the user confirms a block (taps "Block" in BLK1):

### 6.1 Client-Side (Immediate)

1. Dismiss BLK1 dialog.
2. Show brief toast: "Blocked." (200ms fade-in, 2s visible, 200ms fade-out).
3. Remove blocked profile from contact list, search index, and circle membership views.
4. Strip enrichment data from the blocked person's contact card in the local SwiftData cache.
5. Rename the contact to "[Blocked]" in timeline views.
6. Navigate back to the previous screen if current screen is the blocked person's detail view.

### 6.2 Server-Side

1. Create block record: `{ blocker_profile_id, blocked_profile_id, created_at, source_entry_point }`.
2. Update search projections: remove blocked profile from blocker's search index; remove blocker's profile from blocked person's search index.
3. Auto-deny any pending access requests from blocked person to blocker. No notification emitted.
4. Remove enrichment edges between the two profiles.
5. Exclude the edge from ranking computation. Enqueue score recomputation for both profiles.
6. If "Also report for abuse" was checked: create abuse report record (see section 9).

### 6.3 Offline Handling

If the device is offline at block time:
- Block is applied locally to the SwiftData cache immediately.
- Block record is queued in the mutation queue (same pattern as IOS_OFFLINE_STORAGE_V1.md section 5.2).
- On connectivity restore: mutation replays to server. Server reconciles.
- If the server rejects the block (e.g., profile no longer exists): local block is rolled back, user sees toast: "Block could not be applied."

---

## 7) Blocked Users List (BLK2)

### 7.1 Navigation

Settings > Privacy > Blocked Users (as referenced in IOS_KEY_SCREEN_WIREFRAMES_V1.md section 11).

### 7.2 Layout

```
┌──────────────────────────────────┐
│ ◀ Privacy        Blocked Users   │
├──────────────────────────────────┤
│                                  │
│ 🔍 [Search blocked users...   ] │
│                                  │
│ ┌──────────────────────────────┐ │
│ │ [📷] Alice Johnson           │ │
│ │      Blocked Feb 10, 2026    │ │
│ │                         [>]  │ │
│ └──────────────────────────────┘ │
│ ┌──────────────────────────────┐ │
│ │ [📷] Unknown Sender          │ │
│ │      Blocked Jan 28, 2026    │ │
│ │                         [>]  │ │
│ └──────────────────────────────┘ │
│ ┌──────────────────────────────┐ │
│ │ [📷] SpamBot42               │ │
│ │      Blocked Jan 15, 2026    │ │
│ │                         [>]  │ │
│ └──────────────────────────────┘ │
│                                  │
└──────────────────────────────────┘
```

### 7.3 List Elements

Each row displays:

| Element | Spec |
|---------|------|
| Avatar | `AvatarView` size `md` (40pt). Uses the blocked person's last-known photo. If photo was enrichment-sourced, fallback to initials avatar. |
| Name | `rin.type.headline` (17pt semibold). Blocked person's display name at time of block. |
| Block date | `rin.type.footnote` (13pt regular), `rin.text.secondary`. Format: "Blocked [Month Day, Year]". |
| Chevron | Standard disclosure indicator. Tap navigates to blocked contact detail (read-only view showing preserved notes and history). |

### 7.4 Search

- Search bar at top of the blocked list.
- Searches across blocked user names.
- Minimum query length: 2 characters.
- Local search over cached block records.

### 7.5 Unblock Interaction

Two methods to initiate unblock:

**Swipe**: Swipe left on a blocked user row to reveal "Unblock" button (`rin.brand.secondary` green background, white text).

**Tap**: Tap the row to view the blocked contact detail, then tap "Unblock" button at the bottom of the detail view.

Both methods open the BLK3 unblock confirmation dialog (section 8).

### 7.6 Accessing Notes for Blocked Contacts

From the blocked contact detail view (navigated via chevron tap):
- Contact header shows name, photo, and "[Blocked]" badge in `rin.brand.error` color.
- Notes section is visible and scrollable (per section 4.1, notes are preserved).
- Timeline entries are read-only. No new notes can be added while the contact is blocked.
- System events show the block event: "Blocked [Date]".

### 7.7 States

| State | Behavior |
|-------|----------|
| Default | List of blocked profiles, sorted by block date (most recent first) |
| Empty | Center-aligned: `EmptyStateView` with icon `person.slash` (SF Symbol), title "No blocked users", subtitle "You haven't blocked anyone." |
| Loading | Skeleton placeholders for 3 rows |
| Error | "Could not load blocked users. Pull to retry." |
| Search active, no results | "No results for [query]" |

### 7.8 Per-Profile Scope

The blocked users list shows only blocks created by the currently active profile. Switching profiles (via the card picker from SHADOW_PROFILE_UX_V1.md section 4) updates the blocked list to reflect that profile's blocks.

---

## 8) Unblock Flow (BLK3)

### 8.1 Confirmation Dialog

```
┌──────────────────────────────────┐
│                                  │
│    Unblock Alice Johnson?        │
│                                  │
│    They'll be able to find       │
│    your profile and request      │
│    access again.                 │
│                                  │
│  ┌────────────────────────────┐  │
│  │        Unblock             │  │
│  └────────────────────────────┘  │
│                                  │
│          Cancel                  │
│                                  │
└──────────────────────────────────┘
```

### 8.2 Dialog Elements

| Element | Spec |
|---------|------|
| Title | "Unblock [Display Name]?" -- `rin.type.title3` (20pt semibold) |
| Body | "They'll be able to find your profile and request access again." -- `rin.type.body` (17pt regular), `rin.text.secondary` |
| Unblock button | Full-width, `rin.brand.primary` background, white text. `PrimaryButton` standard variant. |
| Cancel | Text-only, `rin.brand.primary` color. Centered below Unblock button. |

### 8.3 On Unblock

When the user confirms unblock:

| Action | Detail |
|--------|--------|
| Contact list | Contact reappears in the contact list, placed in the "Contacts" mandatory circle. Previous custom circle memberships are NOT auto-restored (user must re-add to circles manually). |
| Enrichment | If the unblocked person is still a Rin user and their access policies allow it, enrichment data is restored on next sync. |
| Search | Both parties become visible in each other's search results again (subject to normal discoverability rules). |
| Profile viewing | Both parties can view each other's profiles again (subject to normal access policies). |
| Notification | The previously blocked person is NOT notified of the unblock. |
| Score | Rin Score recalculates silently to re-include the restored edge. |
| Notes | Notes and timeline entries are fully restored to normal view. "[Blocked]" label removed from contact name. |
| Access requests | The unblocked person can send new access requests. |

### 8.4 Re-Block Cooldown

After unblocking a person, the blocker cannot re-block the same profile for 24 hours.

- If the blocker attempts to block during the cooldown period, the BLK1 dialog does not open.
- Instead, a toast appears: "You can block this person again after [time remaining]."
- Cooldown prevents harassment via rapid block/unblock cycling.
- Cooldown is per-profile pair: unblocking Profile A from Profile X sets a 24-hour cooldown only for that specific pair.

### 8.5 States

| State | Behavior |
|-------|----------|
| Default | Dialog shown, Unblock button enabled |
| Processing | Unblock button shows loading spinner, all inputs disabled |
| Success | Dialog dismisses, blocked user removed from BLK2 list with collapse animation. Toast: "Unblocked." |
| Error | Toast: "Could not unblock. Try again." Dialog remains open for retry |
| Offline | Unblock applied locally, queued for sync. Toast: "Unblocked. Will sync when online." |

---

## 9) Block + Report Flow

### 9.1 Report Trigger

When the user checks "Also report for abuse" in the BLK1 dialog and taps "Block":
1. Block executes immediately (section 6).
2. Report sheet (BLK4) presents after the block toast dismisses.

### 9.2 Report Sheet (BLK4)

```
┌──────────────────────────────────┐
│ Cancel       Report        Submit│
├──────────────────────────────────┤
│                                  │
│  Why are you reporting            │
│  Alice Johnson?                  │
│                                  │
│  ┌────────────────────────────┐  │
│  │ ○ Spam                     │  │
│  │ ○ Impersonation            │  │
│  │ ○ Harassment               │  │
│  │ ○ Inappropriate Content    │  │
│  │ ○ Other                    │  │
│  └────────────────────────────┘  │
│                                  │
│  ┌────────────────────────────┐  │
│  │ Add details (optional)...  │  │
│  │                            │  │
│  └────────────────────────────┘  │
│                                  │
└──────────────────────────────────┘
```

### 9.3 Report Elements

| Element | Spec |
|---------|------|
| Title | "Why are you reporting [Display Name]?" -- `rin.type.title3` |
| Reason selector | Single-select radio list. One reason required. |
| Details field | Optional multi-line text field, max 1,000 characters. Placeholder: "Add details (optional)..." |
| Submit button | Enabled when a reason is selected. `PrimaryButton` standard variant. |
| Cancel | Dismisses sheet without submitting report. Block remains in effect. |

### 9.4 Report Reasons

| Reason | Description | Escalation |
|--------|-------------|------------|
| Spam | Unsolicited bulk or promotional contact attempts | Auto-triaged, low priority |
| Impersonation | Profile pretends to be someone else | Dispatched as case type C4 per DISPUTE_PLAYBOOK_V1.md section 5 |
| Harassment | Repeated unwanted contact, threats, or intimidation | Dispatched as case type C6 per DISPUTE_PLAYBOOK_V1.md section 5 |
| Inappropriate Content | Profile contains offensive or harmful material | Manual review queue |
| Other | Does not fit above categories | Manual review queue |

### 9.5 Report Submission

On submit:
1. Report record created: `{ reporter_profile_id, reported_profile_id, reason, details, block_id, created_at }`.
2. Report dispatched to the Security Inbox backend for admin review (per DISPUTE_PLAYBOOK_V1.md section 8).
3. Sheet dismisses.
4. Toast: "Report submitted. We'll review it."

### 9.6 Blocking Without Reporting

Blocking without checking the report checkbox is valid and common. Not all blocks indicate abuse -- users may block for personal reasons (ex-partner, unwanted acquaintance, privacy preference). No report is created in this case.

### 9.7 Report-Only Path (Without Block)

V1 does not support reporting without blocking. The report checkbox is only available within the block confirmation flow. A standalone "Report" action (without blocking) is a candidate for v2 if usage data shows demand.

---

## 10) Edge Cases

### 10.1 Blocked Person Imports Blocker from Device Contacts

The blocked person imports the blocker's phone number or email from their device address book into Rin:
- The contact appears as a regular contact in the blocked person's Rin (device import is independent of Rin blocking).
- However, the blocked person cannot view the blocker's Rin profile or receive enrichment data.
- The contact card shows only device-imported data (no `✦`-badged Rin enrichment fields).

### 10.2 Blocker and Blocked in Same Third-Party Circle

If both the blocker and blocked person are members of a circle owned by a third party:
- They do not see each other in that circle's member list.
- The circle owner sees both members normally (the block is between the two parties, not visible to third parties).
- Access policy computations for the circle still apply to both parties independently, but neither party's enrichment data flows to the other.

### 10.3 Blocked Person Sends Invite Link to Blocker

If the blocked person shares a Rin invite link and the blocker receives it:
- The invite is silently ignored. No error is shown to the sender.
- The blocker does not see the invite in any inbox or notification.
- If the blocker taps the invite link from an external source (e.g., SMS), they see "Profile not available."

### 10.4 Blocking a Contact with Notes

- All notes created by the blocker about the blocked contact are preserved.
- Notes remain accessible from the blocked contact's detail view (navigated via BLK2 list).
- Notes cannot be edited or added while the contact is blocked (read-only).
- On unblock, full note editing capability is restored.

### 10.5 User Blocks All Profiles, Then Deletes Account

- On account deletion, all block records associated with the deleted account are cleaned up.
- Previously blocked persons regain normal search and enrichment access (as if the blocker never existed).
- Block cleanup is part of the standard account deletion pipeline (no separate process needed).

### 10.6 Blocking During Active Access Request

If the blocker has a pending access request from someone they then block:
- The pending request is auto-denied silently (no notification to the requester).
- The requester sees no change in their request status (it simply never resolves).
- If the requester checks their pending requests list, the request appears as "Pending" indefinitely until the system garbage-collects stale requests.

### 10.7 Blocking a Contact Mid-Merge

If the blocker is reviewing a dedup merge suggestion that involves the blocked person:
- The merge suggestion is dismissed automatically.
- If the merge was already confirmed but not yet processed, the merge is canceled.
- A merged contact that included the now-blocked person is not retroactively split -- but the blocked person's enrichment data is stripped.

### 10.8 Mutual Blocking

If User A blocks User B, and User B independently blocks User A:
- Both blocks are independent records.
- Effects stack but are functionally identical to a single block (bidirectional invisibility).
- Unblocking by one party does not remove the other party's block. User A can unblock User B, but if User B still has User A blocked, User A remains invisible to User B.

### 10.9 Blocking an Enrichment Source

If the blocked person was the source of enrichment data for one of the blocker's other contacts (e.g., the blocked person is a Rin user whose profile enriched a mutual contact):
- The enrichment data itself is not removed from the mutual contact's card (the data originated from a Rin user, not from the blocked person's relationship with the blocker).
- Enrichment from the Rin network is anonymized by design -- the blocker does not see who sourced the enrichment.

### 10.10 Rapid Block/Unblock Before Server Sync

If the user blocks and then unblocks before the block syncs to the server:
- The mutation queue processes both operations in order.
- The server applies the block and then the unblock, resulting in no active block.
- The 24-hour re-block cooldown still applies (tracked locally).

---

## 11) Events

### Block Lifecycle

| Event | Properties |
|-------|-----------|
| `block.initiated` | `source_entry_point` (contact_detail / search_result / security_inbox / profile_view), `blocked_profile_class` (single / shadow / business / employee) |
| `block.confirmed` | `blocker_profile_id`, `blocked_profile_id`, `with_report` (bool) |
| `block.with_report` | `report_reason` (spam / impersonation / harassment / inappropriate_content / other), `has_details` (bool) |
| `block.failed` | `error_type`, `was_offline` (bool) |

### Unblock Lifecycle

| Event | Properties |
|-------|-----------|
| `unblock.initiated` | `source` (blocked_list_swipe / blocked_contact_detail) |
| `unblock.confirmed` | `blocker_profile_id`, `unblocked_profile_id`, `block_duration_days` |
| `unblock.failed` | `error_type`, `was_offline` (bool) |
| `unblock.cooldown_hit` | `blocker_profile_id`, `target_profile_id`, `hours_remaining` |

### Blocked List

| Event | Properties |
|-------|-----------|
| `block.list_viewed` | `blocked_count`, `active_profile_class` |
| `block.search_used` | `query_length`, `result_count` |
| `block.contact_detail_viewed` | `blocked_profile_id`, `notes_count` |

### Report

| Event | Properties |
|-------|-----------|
| `report.submitted` | `reporter_profile_id`, `reported_profile_id`, `reason`, `details_length`, `associated_block_id` |
| `report.sheet_dismissed` | `reason_selected` (bool), without submission |

### Graph

| Event | Properties |
|-------|-----------|
| `score.recompute.requested` | `trigger` (block / unblock), `affected_profile_ids` |

---

## 12) Accessibility

### 12.1 VoiceOver

| Element | VoiceOver label |
|---------|----------------|
| Block menu item (contact detail) | "Block [Name]. Double tap to block this contact." |
| Block menu item (search result) | "Block [Name]. Double tap to block this person." |
| BLK1 dialog title | "Alert. Block [Name]?" |
| BLK1 body text | Full body text read in sequence. |
| Report checkbox | "Also report for abuse. Checkbox. [Unchecked/Checked]." |
| Block button (BLK1) | "Block. Destructive action. Double tap to confirm." |
| Cancel button (BLK1) | "Cancel. Double tap to dismiss." |
| Blocked user row (BLK2) | "[Name], blocked [date]. Swipe left for unblock action." |
| Unblock swipe action | "Unblock [Name]." |
| BLK3 dialog title | "Alert. Unblock [Name]?" |
| Empty blocked list | "No blocked users. You haven't blocked anyone." |
| Report reason option | "[Reason]. Radio button. [Selected/Not selected]." |

### 12.2 Destructive Action Labeling

All destructive actions (Block button in BLK1, "Block" in menus) use the `.destructive` role in SwiftUI:
- Rendered in `rin.brand.error` color (red).
- VoiceOver announces "Destructive action" trait.
- Haptic feedback: `UINotificationFeedbackGenerator` with `.warning` type on block confirmation.

### 12.3 Dynamic Type

All text in BLK1, BLK2, BLK3, and BLK4 screens uses the token-based type scale from IOS_DESIGN_TOKENS_V1.md section 3:
- Dialog titles: `rin.type.title3` (20pt base, scales with Dynamic Type).
- Body text: `rin.type.body` (17pt base).
- List names: `rin.type.headline` (17pt semibold base).
- Timestamps: `rin.type.footnote` (13pt base).
- Blocked list supports up to `AX5` accessibility size.
- At large accessibility sizes, blocked user rows stack vertically (avatar above name/date instead of inline).

### 12.4 Reduce Motion

- Block/unblock list animations (row removal/insertion) use fade transitions instead of slide when "Reduce Motion" is enabled.
- Toast notifications appear/disappear without animation.

### 12.5 Keyboard Navigation (iPad)

- Tab key cycles through blocked user rows and the search field.
- Return key on a blocked user row navigates to the detail view.
- Swipe-to-unblock is also available via the Delete key on a focused row.
- Escape key dismisses BLK1/BLK3/BLK4 dialogs.

---

## 13) Design Token Usage

| Element | Token | Value |
|---------|-------|-------|
| BLK1/BLK3 dialog background | `rin.bg.primary` | White / Black |
| Dialog title text | `rin.text.primary` + `rin.type.title3` | 20pt semibold |
| Dialog body text | `rin.text.secondary` + `rin.type.body` | 17pt regular, grey |
| Block button background | `rin.brand.error` | `#EF4444` (red) |
| Block button text | White | Constant |
| Unblock button background | `rin.brand.primary` | `#1A73E8` (blue) |
| Cancel text | `rin.brand.primary` | `#1A73E8` (blue) |
| Report checkbox label | `rin.text.primary` + `rin.type.callout` | 16pt regular |
| Blocked user row background | `rin.bg.secondary` | Card background |
| Blocked user name | `rin.text.primary` + `rin.type.headline` | 17pt semibold |
| Blocked user date | `rin.text.secondary` + `rin.type.footnote` | 13pt grey |
| "[Blocked]" badge | `rin.brand.error` + `rin.type.caption` | 12pt red |
| Unblock swipe action | `rin.brand.secondary` background | `#34A853` (green) |
| Toast text | `rin.text.primary` + `rin.type.callout` | 16pt |
| Search bar | `rin.bg.tertiary` + `rin.radius.md` | Input field style |
| Empty state icon | `rin.text.tertiary` | Light grey |
| Empty state title | `rin.text.primary` + `rin.type.title3` | 20pt semibold |
| Empty state subtitle | `rin.text.secondary` + `rin.type.body` | 17pt grey |
| Report reason text | `rin.text.primary` + `rin.type.body` | 17pt |
| Report details field | `rin.bg.tertiary` + `rin.radius.md` | Input field style |

### Animation Tokens

| Animation | Duration | Curve | Usage |
|-----------|----------|-------|-------|
| Dialog present | 300ms | `.spring(response: 0.3)` | BLK1/BLK3/BLK4 sheet presentation |
| Toast fade-in | 200ms | `.easeIn` | Block/unblock confirmation toast |
| Toast fade-out | 200ms | `.easeOut` | Toast dismissal |
| Row removal | 250ms | `.easeInOut` | Unblocked user removed from BLK2 list |
| Row insertion | 250ms | `.spring(response: 0.25, dampingFraction: 0.8)` | Newly blocked user appears in BLK2 list |
| Swipe reveal | 200ms | `.easeInOut` | Unblock action revealed on swipe |

---

## 14) Navigation Map

```
Contact Detail
├── Three-dot menu → "Block" → BLK1 (Block Confirmation)
│   ├── Block → Execute block → Toast → Previous screen
│   └── Block + Report → Execute block → BLK4 (Report Sheet)
│       ├── Submit → Toast: "Report submitted" → Previous screen
│       └── Cancel → Previous screen (block remains)
│
Search Results
├── Long-press → "Block" → BLK1
│
Security Inbox
├── Access Request → "Block this person" → BLK1
│
Profile View
├── Three-dot menu → "Block" → BLK1
│
Settings
└── Privacy
    └── Blocked Users (BLK2)
        ├── Search blocked users
        ├── Swipe row → "Unblock" → BLK3 (Unblock Confirmation)
        │   ├── Unblock → Remove from list → Toast: "Unblocked"
        │   └── Cancel → Dismiss
        ├── Tap row → Blocked Contact Detail
        │   ├── Notes (read-only)
        │   ├── Timeline (read-only)
        │   └── "Unblock" button → BLK3
        └── Empty state: "No blocked users"
```

---

## 15) Open Decisions

1. **Circle restoration on unblock**: Should unblocking restore the contact's previous custom circle memberships, or should the contact always return to only the "Contacts" mandatory circle? Auto-restoration is more user-friendly but may surprise users who restructured their circles since the block. Current spec: no auto-restoration (user re-adds manually).

2. **Re-block cooldown duration**: The 24-hour cooldown prevents harassment via rapid block/unblock, but the exact duration needs user testing. Alternatives considered: 12 hours (faster re-block), 48 hours (stronger protection), or no cooldown with rate limiting instead (max 3 blocks of the same person per week).

3. **Block from notification**: Should users be able to block directly from a push notification (e.g., an access request notification)? This would add a "Block" action to notification categories. Faster for abuse scenarios but risks accidental blocks from the lock screen.

4. **Blocked contact data export**: When a user exports their data (Settings > Privacy > Export My Data), should blocked contact records and associated notes be included in the export? GDPR compliance likely requires it, but the UX of seeing blocked contacts in an export may confuse users.

5. **Cross-profile block awareness**: If the user blocks someone from Profile A, should Profile B surface any hint (e.g., "You blocked this person from another profile")? This would break shadow identity isolation but could prevent scenarios where a user unknowingly interacts with a blocked person from a different profile. Current spec: no cross-profile awareness.
