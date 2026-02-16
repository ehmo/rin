# iOS Home Tab Screen Spec V1

## 1) Purpose

The Home tab is the daily contact intelligence hub. It is the first screen users see every time they open Rin after onboarding. Its job is to surface actionable contact management tasks, provide fast access to any contact, and reflect the current health of the user's network. It is explicitly not a social feed, timeline, or engagement loop. Value comes from clarity, organization, and control.

The Home tab transitions seamlessly from the onboarding first-value home (S12 in `IOS_ONBOARDING_SCREEN_SPEC_V1.md`). On day 1, it is dominated by smart section cards (dedup suggestions, enrichment updates, cleanup tasks). On day 30, it may be a clean, organized contact list with occasional contextual cards. Both states are correct.

Companion docs:
- `docs/product/IOS_INSTALL_TO_FIRST_VALUE_UX_V1.md` (Step 8: first-session home)
- `docs/product/IOS_ONBOARDING_SCREEN_SPEC_V1.md` (S12: first-value home)
- `docs/product/CONTACTS_IMPORT_SYNC_UX_V1.md` (smart sections, dedup, enrichment, contact list)
- `docs/product/IOS_SEARCH_DISCOVERY_SCREEN_SPEC_V1.md` (S1: contact search)
- `docs/product/CIRCLE_MANAGEMENT_UX_V1.md` (circles, assignment, access control)
- `docs/architecture/IOS_NAVIGATION_STATE_V1.md` (tab structure, deep links, badges)
- `docs/design/IOS_KEY_SCREEN_WIREFRAMES_V1.md` (Home tab wireframe, section 3)
- `docs/design/IOS_DESIGN_TOKENS_V1.md` (colors, typography, spacing, components)
- `docs/product/RIN_SCORE_V1.md` (score change card context)

---

## 2) Screen Layout

### 2.1 Structural Hierarchy

```
┌──────────────────────────────────────┐
│ A. Navigation Bar                    │
├──────────────────────────────────────┤
│ B. Search Bar                        │
├──────────────────────────────────────┤
│ C. Smart Sections Area               │
│    (dynamic, 0-N cards)              │
├──────────────────────────────────────┤
│ D. Contact List Main Body            │
│    (grouped, scrollable)             │
├──────────────────────────────────────┤
│ E. Tab Bar                           │
└──────────────────────────────────────┘
```

The entire area from B through D is a single `ScrollView` (or `List`) with pull-to-refresh. The navigation bar (A) and tab bar (E) remain fixed.

### 2.2 Navigation Bar

```
┌──────────────────────────────────────┐
│ Rin                          [+ Add] │
└──────────────────────────────────────┘
```

| Element | Spec |
|---------|------|
| Title | `Rin` — left-aligned, `rin.type.title1` (28pt Bold). Uses large title style that collapses on scroll. |
| Add button | SF Symbol `plus.circle` (`.medium` weight), positioned trailing. Tap opens manual contact creation (see `CONTACTS_IMPORT_SYNC_UX_V1.md` section 8). |

The navigation bar uses iOS large title behavior: expanded at scroll-top, collapsed inline when user scrolls down.

### 2.3 Search Bar

```
┌──────────────────────────────────────┐
│ [magnifyingglass] Search contacts... │
└──────────────────────────────────────┘
```

- Persistent at the top of the scroll content, below the navigation bar.
- Background: `rin.bg.tertiary`. Corner radius: `rin.radius.md` (8pt). Height: 36pt.
- Placeholder text: `Search contacts...` in `rin.text.tertiary`.
- Tap activates full search mode as defined in `IOS_SEARCH_DISCOVERY_SCREEN_SPEC_V1.md` S1.
- When search is active: keyboard appears, smart sections and contact list filter in real-time, cancel button appears trailing.
- Search remains visible when scrolled to top but scrolls away with content (standard iOS `.searchable` behavior pinned below navigation bar).

### 2.4 Smart Sections Area

Dynamic cards that appear between the search bar and the contact list. Zero or more sections may be visible at any time. When no sections are active, this area collapses to zero height (no empty placeholder). See section 3 for full smart section specification.

### 2.5 Contact List Main Body

The primary content area. Shows all contacts organized by the user's chosen grouping. See section 5 for full specification.

### 2.6 Pull-to-Refresh

- Standard iOS pull-to-refresh indicator attached to the scroll view.
- See section 9 for trigger behavior and sync mechanics.

### 2.7 Floating Action Button

No floating action button in v1. The `[+ Add]` button in the navigation bar serves as the primary creation entry point. A FAB would compete with the tab bar and add visual noise to a screen designed for clarity.

---

## 3) Smart Sections

Smart sections are dynamic, context-aware card groups that surface actionable items at the top of the Home tab. They appear and disappear based on user state. They are the primary mechanism for delivering ongoing single-player value after onboarding.

### 3.1 Section Catalog

#### 3.1.1 Needs Attention

**Trigger**: Unreviewed merge suggestions (70-95% confidence), unresolved sync conflicts, or contacts with critically incomplete data (name-only with no phone/email).

**Content**:
```
┌──────────────────────────────────────┐
│ NEEDS ATTENTION                  (5) │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ John Smith  <->  Jon Smith      │ │
│ │ 92% match - Phone + Email       │ │
│ │ [Merge]  [Not Same]  [Skip]    │ │
│ └──────────────────────────────────┘ │
│ ┌──────────────────────────────────┐ │
│ │ Conflict: Alex Johnson          │ │
│ │ Name differs between Phone/Rin  │ │
│ │                     [Resolve >] │ │
│ └──────────────────────────────────┘ │
│                                      │
│ [See All 5 Items >]                  │
└──────────────────────────────────────┘
```

| Property | Value |
|----------|-------|
| Header | `NEEDS ATTENTION` with count badge (total items) |
| Count badge | `rin.brand.error` background, white text, `rin.radius.full` (capsule) |
| Cards shown inline | Up to 2. Remaining accessible via "See All" which pushes a full-screen review list. |
| Card types | Dedup suggestion card (`DedupCard` component), conflict card, incomplete contact card |
| Priority within | Conflicts first (data integrity), then dedup by confidence descending, then incomplete |
| Dismiss behavior | Individual cards dismissable via "Skip" or "Not Now". Dismissed dedup cards do not reappear for the same pair. Dismissed conflicts persist until resolved. |
| Badge link | Count badge here is the source for the Home tab badge (see section 7). |

**Dedup card inline actions** (per `CONTACTS_IMPORT_SYNC_UX_V1.md` section 5.2):
- **Merge**: executes merge, card animates out, count decrements.
- **Not Same**: marks pair as distinct, card animates out, pair never re-suggested.
- **Skip**: hides card for this session. Reappears on next app launch.

#### 3.1.2 Recently Added

**Trigger**: One or more contacts added (via sync or manual) in the last 7 days.

**Content**:
```
┌──────────────────────────────────────┐
│ RECENTLY ADDED                       │
│ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐   │
│ │[Av] │ │[Av] │ │[Av] │ │[Av] │   │
│ │Sarah│ │Mike │ │Lisa │ │Tom  │   │
│ │ 2d  │ │ 3d  │ │ 5d  │ │ 6d  │   │
│ └─────┘ └─────┘ └─────┘ └─────┘   │
│              <- scroll ->            │
└──────────────────────────────────────┘
```

| Property | Value |
|----------|-------|
| Layout | Horizontal scroll row of compact contact cards. |
| Card size | 72pt wide x 88pt tall. Avatar (`AvatarView` md 40pt), name (1 line, truncated, `rin.type.caption`), relative time (`rin.type.caption`, `rin.text.secondary`). |
| Order | Most recent first (left to right). |
| Maximum shown | Up to 20 in horizontal scroll. If >20, last card is "+N more" that pushes a full list. |
| Tap behavior | Tap any card to push contact detail. |
| Dismiss | Section auto-hides when no contacts have been added in the last 7 days. No manual dismiss. |

#### 3.1.3 Enrichment Updates

**Trigger**: One or more contacts received new Rin-sourced enrichment data since the user last viewed this section.

**Content**:
```
┌──────────────────────────────────────┐
│ ENRICHMENT UPDATES               (3) │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ [Av] John Smith                 │ │
│ │      + Company: Acme Corp       │ │
│ │      + Title: VP Engineering    │ │
│ │                     [View >]    │ │
│ └──────────────────────────────────┘ │
│                                      │
│ [See All 3 Updates >]                │
└──────────────────────────────────────┘
```

| Property | Value |
|----------|-------|
| Header | `ENRICHMENT UPDATES` with count |
| Cards shown inline | Up to 2. Remaining via "See All". |
| Card content | Contact avatar + name, list of newly enriched fields with `EnrichmentBadge` indicator. |
| Tap behavior | Tap card or "View" to push contact detail. |
| Seen tracking | Once user taps "See All" or views all individual cards, section hides until new enrichments arrive. |

#### 3.1.4 Suggested Circle Assignments

**Trigger**: System detected contacts matching metadata patterns of an existing circle (shared employer domain, area code cluster, name pattern) but not yet assigned to that circle. Minimum 3 suggestions required to show section.

**Content**:
```
┌──────────────────────────────────────┐
│ SUGGESTED CIRCLES                    │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ 5 contacts may belong in        │ │
│ │ "Colleagues"                     │ │
│ │ Shared domain: @acme.com        │ │
│ │ [Review]            [Dismiss]   │ │
│ └──────────────────────────────────┘ │
└──────────────────────────────────────┘
```

| Property | Value |
|----------|-------|
| Card content | Suggested circle name + emoji, contact count, matching reason. |
| "Review" action | Pushes a confirmation screen showing the contacts and target circle. User can select/deselect individuals, then confirm assignment. |
| "Dismiss" action | Removes suggestion permanently for this exact group. Similar future suggestions (different contacts, same pattern) may still appear. |
| Maximum cards | 2 visible. Additional accessible via "See More Suggestions" link. |

#### 3.1.5 Score Changed

**Trigger**: User's Rin Score changed since last Home tab visit. Shows only when score change is non-zero.

**Content**:
```
┌──────────────────────────────────────┐
│ ┌──────────────────────────────────┐ │
│ │ Your Rin Score        72  +3 ▲  │ │
│ │ Good - up from 69              │ │
│ │                [View Score >]   │ │
│ └──────────────────────────────────┘ │
└──────────────────────────────────────┘
```

| Property | Value |
|----------|-------|
| Layout | Single compact card. No section header (self-contained). |
| Score display | Current score in `rin.type.title3`, delta with directional arrow colored by score tier (`rin.score.*` tokens). |
| Label | Score tier label ("Good", "Strong", etc.) and previous value. |
| Tap behavior | Switches to Score tab. |
| Dismiss | Card auto-hides after user taps it or after 48 hours (whichever is first). Reappears on next score change. |

#### 3.1.6 Upcoming

**Trigger**: A contact has a birthday within the next 7 days, or a user-set custom reminder from contact notes is approaching.

**Content**:
```
┌──────────────────────────────────────┐
│ UPCOMING                             │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ [Av] Sarah Chen - Birthday      │ │
│ │      Tomorrow, Feb 16           │ │
│ │              [View] [Dismiss]   │ │
│ └──────────────────────────────────┘ │
│ ┌──────────────────────────────────┐ │
│ │ [Av] Mike Torres - Reminder     │ │
│ │      "Follow up on project"     │ │
│ │      Feb 19                     │ │
│ │              [View] [Dismiss]   │ │
│ └──────────────────────────────────┘ │
└──────────────────────────────────────┘
```

| Property | Value |
|----------|-------|
| Card content | Contact avatar + name, event type, date (relative for <3 days, absolute otherwise). For reminders: the reminder text (truncated to 1 line). |
| Order | Soonest first. |
| Maximum shown | 3 inline. Remaining via "See All Upcoming". |
| Dismiss | Per-card dismiss hides that specific event for this occurrence. Birthday reappears next year. Reminder is marked complete. |
| Data source | Birthday from device contacts or Rin enrichment. Reminders from user-created notes on contact detail (future CRM-lite feature). |

### 3.2 Section Ordering Rules

When multiple smart sections are active, they display in this fixed priority order:

| Priority | Section | Rationale |
|----------|---------|-----------|
| 1 | Needs Attention | Data integrity is highest priority. Dedup/conflicts degrade contact quality. |
| 2 | Score Changed | Quick glance, high engagement, auto-dismisses. |
| 3 | Upcoming | Time-sensitive. Missing a birthday is worse than missing a suggestion. |
| 4 | Recently Added | Recency-relevant context. |
| 5 | Enrichment Updates | Informational. No urgency. |
| 6 | Suggested Circle Assignments | Organizational improvement. Can wait. |

### 3.3 Section Visibility Limits

- **Maximum visible sections**: 3 at a time before the contact list begins.
- **Overflow behavior**: If more than 3 sections are active, sections 4+ are collapsed behind a `See N More Sections` link between the last visible section and the contact list header.
- **Rationale**: The contact list is the primary content. Smart sections should enhance, not bury it. Three sections consume roughly one screen height; more than that and the user must scroll past cards to reach their contacts.

### 3.4 Section Collapse and Dismiss

| Gesture | Behavior |
|---------|----------|
| Tap section header | Toggles collapse/expand for that section. Collapsed state shows header + count only. |
| Swipe left on section header | Reveals "Hide" button. Tap hides section for 24 hours. |
| Long-press section header | Opens context menu: "Collapse", "Hide for today", "Don't show this section". |
| "Don't show this section" | Permanently hides that section type. Reversible from Settings > Home Sections. |

Collapse state persists across app launches (stored in UserDefaults). Hidden/dismissed state stored per section type with timestamp for time-based re-show.

---

## 4) Day-2+ Steady State

As the user resolves dedup suggestions, reviews enrichments, and organizes contacts, smart sections will naturally empty out. The Home tab must remain valuable in this quiescent state.

### 4.1 All Sections Cleared

When no smart sections are active:
- Smart section area collapses to zero height.
- Search bar sits directly above the contact list header.
- No placeholder, motivational card, or empty-state illustration in the smart section area. The clean state IS the goal. Celebrating it with a card would be ironic ("Congratulations, here's more UI to look at").

### 4.2 Steady-State Screen

```
┌──────────────────────────────────────┐
│ Rin                          [+ Add] │
├──────────────────────────────────────┤
│ [Search contacts...                ] │
├──────────────────────────────────────┤
│ ALL CONTACTS (342)         [Filter] │
│                                      │
│ A                                    │
│ ┌──────────────────────────────────┐ │
│ │ [Av] Alice Johnson              │ │
│ │      +1 (555) 123-4567         │ │
│ │      ●● (Family, Friends)  [>] │ │
│ └──────────────────────────────────┘ │
│ ┌──────────────────────────────────┐ │
│ │ [Av] Andrew Park          [enr] │ │
│ │      andrew@company.com        │ │
│ │      ● (Colleagues)        [>] │ │
│ └──────────────────────────────────┘ │
│                                      │
│ B                                    │
│ ...                                  │
└──────────────────────────────────────┘
```

This state is the long-term daily experience. It should feel fast, organized, and unremarkable. The search bar provides instant access. The contact list provides browse access. Smart sections reappear organically as new events occur (sync brings new contacts, enrichment updates arrive, score changes, birthday approaches).

### 4.3 Periodic Re-engagement

Even in steady state, the system generates new smart section content over time:
- **Daily score batch** may produce a Score Changed card.
- **Background sync** may detect new contacts, enrichments, or dedup opportunities.
- **Calendar proximity** surfaces Upcoming cards.
- **Circle pattern detection** runs periodically and may suggest assignments.

No artificial content generation. If nothing has changed, nothing appears.

---

## 5) Contact List Main Body

### 5.1 Header

```
┌──────────────────────────────────────┐
│ ALL CONTACTS (342)         [Filter] │
└──────────────────────────────────────┘
```

| Element | Spec |
|---------|------|
| Title | `ALL CONTACTS` in `rin.type.title2` (22pt Bold) |
| Count | Total contact count in parentheses, `rin.text.secondary` |
| Filter button | SF Symbol `line.3.horizontal.decrease.circle`. Tap opens filter/sort options (see 5.3). |

### 5.2 Default Grouping: Alphabetical

The default view groups contacts alphabetically by display name with section index headers.

```
A ─────────────────────────────────────
┌──────────────────────────────────────┐
│ [Av] Alice Johnson                   │
│      +1 (555) 123-4567              │
│      ●●                         [>] │
└──────────────────────────────────────┘
┌──────────────────────────────────────┐
│ [Av] Andrew Park               [enr]│
│      andrew@company.com             │
│      ●                          [>] │
└──────────────────────────────────────┘

B ─────────────────────────────────────
┌──────────────────────────────────────┐
│ [Av] Bob Williams                    │
│      bob@email.com                  │
│                                 [>] │
└──────────────────────────────────────┘
```

- Section index scrubber (A-Z) appears on the trailing edge for fast letter jumping.
- Contacts with names starting with non-Latin characters grouped under `#` at the end.
- Contacts with no name (phone-number-only) grouped under `#`.

### 5.3 Filter and Sort Options

Tap the Filter button to reveal a bottom sheet with:

**Group By** (single-select):
| Option | Behavior |
|--------|----------|
| Alphabetical (default) | A-Z section headers with section index scrubber |
| By Circle | Section headers are circle names (emoji + name). Contacts appear under their primary circle. Contacts in multiple circles appear under the most specific custom circle (not "Contacts"). Contacts in no custom circle appear under "Contacts" at the bottom. |

**Sort By** (single-select):
| Option | Behavior |
|--------|----------|
| Name A-Z (default) | Alphabetical ascending |
| Name Z-A | Alphabetical descending |
| Recently Added | Newest first |
| Recently Updated | Most recently synced/edited first |

**Filter By Circle** (multi-select chips):
- Circle chips with emoji + name.
- Tap one or more to filter the list to contacts in those circles.
- "All" chip selected by default (no filter active).
- Active filters shown as a chip bar below the contact list header.

User selections persist across sessions (stored in UserDefaults).

### 5.4 Contact Row

Each contact row in the list:

```
┌──────────────────────────────────────┐
│ [Avatar]  Display Name         [enr] │
│           Match context / subtitle   │
│           ●●●                   [>]  │
└──────────────────────────────────────┘
```

| Element | Spec |
|---------|------|
| Avatar | `AvatarView` md (40pt). Circle-clipped photo or initials fallback with `rin.bg.secondary` background. |
| Display name | `rin.type.headline` (17pt Semibold). Primary display name. Single line, truncated. |
| Subtitle | `rin.type.subheadline` (15pt Regular), `rin.text.secondary`. Shows primary phone number, or primary email if no phone, or "No contact info" if neither. |
| Circle dots | `CircleDot` row. Up to 4 colored dots representing circle membership. Colors from `rin.circle.*` tokens. If >4 circles, show 3 dots + `+N`. |
| Enrichment badge | `EnrichmentBadge` indicator. Visible only if contact has at least one Rin-enriched field. SF Symbol `sparkles` in `rin.brand.accent`, 12pt. |
| Disclosure | Chevron `>` in `rin.text.tertiary`. |
| Row height | Dynamic, minimum 64pt. Content-hugging with `rin.space.md` (12pt) vertical padding. |
| Tap | Pushes contact detail screen. |

### 5.5 Batch Multi-Select Mode

**Entry**: Long-press any contact row, or tap "Select" from the navigation bar's trailing menu (accessible via `ellipsis.circle` button that replaces `[+ Add]` in edit mode).

**Behavior when active**:
- Navigation bar title changes to `N Selected`.
- Navigation bar trailing buttons: `Done` (exits select mode), `Select All`.
- Each contact row shows a leading circular checkbox.
- Tap rows to toggle selection.
- Bottom toolbar appears above the tab bar:

```
┌──────────────────────────────────────┐
│ [Add to Circle]  [Delete]  [More...] │
└──────────────────────────────────────┘
```

| Action | Behavior |
|--------|----------|
| Add to Circle | Presents circle picker sheet. Selected contacts added to chosen circle(s). |
| Delete | Confirmation alert: "Remove N contacts from Rin? This cannot be undone." Contacts removed from Rin (not from device address book). |
| More | Context menu: "Export vCards", "Share" (future). |

**Exit**: Tap "Done", tap outside selection, or swipe back.

### 5.6 Section Index Scrubber

- Vertical A-Z index on the trailing edge (standard `UITableView` section index behavior).
- Visible only in alphabetical grouping mode.
- Touch-and-drag for rapid letter jumping.
- Haptic feedback (`UIImpactFeedbackGenerator` light) on each letter change.

---

## 6) Empty States

### 6.1 No Contacts Imported (Permission Denied)

Shown when user denied contacts permission and has not added any manual contacts.

```
┌──────────────────────────────────────┐
│ Rin                          [+ Add] │
├──────────────────────────────────────┤
│                                      │
│          [person.3 SF Symbol]        │
│                                      │
│     Import your contacts to get      │
│     started with Rin                 │
│                                      │
│     Rin finds duplicates, enriches   │
│     info, and helps you organize.    │
│                                      │
│       [Import Contacts]              │
│                                      │
│     or add contacts manually         │
│     with the + button above          │
│                                      │
└──────────────────────────────────────┘
```

| Element | Spec |
|---------|------|
| Icon | SF Symbol `person.3`, 56pt, `rin.text.tertiary` |
| Title | `rin.type.title3` (20pt Semibold) |
| Body | `rin.type.body` (17pt Regular), `rin.text.secondary`, center-aligned |
| CTA | `PrimaryButton`: "Import Contacts". Triggers contextual permission re-prompt (see `CONTACTS_IMPORT_SYNC_UX_V1.md` section 9.2). |

### 6.2 Zero Contacts (Sync Pending)

Shown briefly when contacts permission was granted but initial sync has not completed.

```
┌──────────────────────────────────────┐
│                                      │
│          [progress spinner]          │
│                                      │
│     Importing your contacts...       │
│                                      │
│     This usually takes a few         │
│     seconds.                         │
│                                      │
└──────────────────────────────────────┘
```

- Uses `ProgressView` with indeterminate spinner.
- Transitions automatically to the populated contact list once first batch arrives.
- If sync takes >15 seconds, append: `Taking a bit longer for large contact lists.`

### 6.3 Zero Contacts (Manual-Only User)

Shown when user denied contacts permission but has subsequently deleted all manually-added contacts.

Same as 6.1 (permission denied empty state). The "Import Contacts" CTA remains relevant.

### 6.4 Search No Results

Handled by `IOS_SEARCH_DISCOVERY_SCREEN_SPEC_V1.md` section 4.2. The Home tab delegates to that spec when search is active and returns no matches.

### 6.5 All Smart Sections Cleared

As described in section 4.1: no placeholder. Clean state is the goal. The contact list is the primary content and is always visible when contacts exist.

---

## 7) Tab Badge

### 7.1 Badge Source

The Home tab badge shows the count of unreviewed items in the "Needs Attention" section:
- Pending merge suggestions (70-95% confidence range).
- Unresolved sync conflicts.

Auto-merged contacts (95%+ confidence) do NOT contribute to the badge count. They are informational, not action-required.

### 7.2 Badge Display

| State | Badge |
|-------|-------|
| 0 items | No badge |
| 1-99 items | Numeric badge (e.g., `3`) |
| 100+ items | `99+` |

Badge uses `TabBadge` component with `rin.brand.error` background.

### 7.3 Badge Clearing

The badge count decrements when:
- User merges a dedup suggestion (Merge action).
- User dismisses a dedup suggestion (Not Same action).
- User resolves a sync conflict.
- User taps "Skip" on a suggestion (temporary hide, does NOT decrement badge).

The badge does NOT clear simply by visiting the Home tab. The user must take action on the individual items.

### 7.4 Badge Update Triggers

Badge recalculates on:
- Sync completion (new dedup suggestions or conflicts detected).
- Push notification delivery for new dedup batch.
- App foreground (recount from local SwiftData cache).

---

## 8) Deep Link Handling

All deep links follow the routing architecture defined in `IOS_NAVIGATION_STATE_V1.md` section 3.

| URL | Behavior |
|-----|----------|
| `rin://home` | Switch to Home tab. Pop to root of Home navigation stack. |
| `rin://home?section=dedup` | Switch to Home tab. Pop to root. Scroll to "Needs Attention" section and briefly highlight it with a `rin.brand.primary` border pulse (300ms, then fade). If section is collapsed, expand it. |
| `rin://home?section=enrichment` | Switch to Home tab. Pop to root. Scroll to "Enrichment Updates" section. |
| `rin://home?section=upcoming` | Switch to Home tab. Pop to root. Scroll to "Upcoming" section. |
| `rin://contacts/{id}` | Switch to Home tab. Push contact detail for the given contact ID onto the Home navigation stack. If contact not found in local cache, show loading state while fetching from server, then error if not found. |

### 8.1 Deep Link Error Handling

| Error | Behavior |
|-------|----------|
| `rin://contacts/{id}` with unknown ID | Push error screen: "Contact not found. It may have been deleted or merged." with "Go Back" button. |
| `rin://home?section=dedup` with no dedup items | Navigate to Home root. No scroll action. No error (section simply isn't present). |
| Malformed URL | Ignore silently. Log `deeplink.parse_failed` event. |

---

## 9) Pull-to-Refresh

### 9.1 Trigger Conditions

| Condition | Sync behavior |
|-----------|--------------|
| Manual pull-to-refresh | Always triggers delta sync, regardless of staleness. |
| App foreground, last sync >1 hour | Automatic delta sync (no user action). |
| App foreground, last sync <=1 hour | No sync. Smart sections refresh from local cache only. |
| Background refresh (BGAppRefreshTask) | Delta sync per `CONTACTS_IMPORT_SYNC_UX_V1.md` section 2.1. |

### 9.2 Progress Indication

```
┌──────────────────────────────────────┐
│ [spinner] Syncing contacts...        │
└──────────────────────────────────────┘
```

- Standard iOS pull-to-refresh spinner during pull gesture.
- After release, a thin inline status bar appears below the search bar: `Syncing contacts...` with a subtle progress spinner.
- Status bar uses `rin.bg.secondary` background, `rin.type.footnote`, `rin.text.secondary`.
- On completion: status bar briefly shows `Updated just now` (1.5 seconds), then fades out.
- On failure: status bar shows `Sync failed. Pull to retry.` in `rin.brand.warning` text. Persists until next successful sync or manual dismissal.

### 9.3 Post-Sync Refresh

After sync completes:
1. Smart sections re-evaluate their triggers and update in place (new items appear, resolved items disappear).
2. Contact list updates with any new/modified/removed contacts.
3. Tab badge recalculates.
4. All updates are animated (standard `List` insert/delete animations).

---

## 10) Events (Analytics)

### 10.1 Screen Lifecycle

| Event | Trigger | Properties |
|-------|---------|------------|
| `home.viewed` | Home tab becomes visible (including tab switch) | `smart_section_count`, `contact_count`, `has_badge`, `badge_count` |
| `home.pull_to_refresh` | User initiates pull-to-refresh | `last_sync_age_seconds` |
| `home.sync_completed` | Sync triggered from Home completes | `new_contacts`, `new_dedup`, `new_enrichments`, `duration_ms` |

### 10.2 Smart Section Interactions

| Event | Trigger | Properties |
|-------|---------|------------|
| `home.section_viewed` | Smart section scrolls into viewport (>50% visible for >1 second) | `section_type`, `item_count`, `position` |
| `home.section_tapped` | User taps a smart section header or "See All" | `section_type`, `action` (expand/collapse/see_all) |
| `home.section_dismissed` | User hides or permanently disables a section | `section_type`, `dismiss_type` (temporary/permanent) |
| `home.dedup_action` | User acts on an inline dedup card | `action` (merge/not_same/skip), `confidence`, `evidence_types` |
| `home.enrichment_viewed` | User taps an enrichment update card | `contact_id`, `enriched_fields_count` |
| `home.suggestion_action` | User acts on a circle suggestion | `action` (review/dismiss), `circle_name`, `contact_count` |
| `home.score_card_tapped` | User taps the score change card | `score_current`, `score_delta` |
| `home.upcoming_action` | User acts on an upcoming event card | `action` (view/dismiss), `event_type` (birthday/reminder) |

### 10.3 Contact List Interactions

| Event | Trigger | Properties |
|-------|---------|------------|
| `home.contact_selected` | User taps a contact row | `contact_id`, `has_enrichment`, `circle_count`, `list_position`, `grouping_mode` |
| `home.search_activated` | User taps the search bar | `contact_count`, `smart_section_count` |
| `home.filter_changed` | User changes grouping, sort, or circle filter | `group_by`, `sort_by`, `circle_filter_count` |
| `home.multi_select_started` | User enters batch selection mode | `contact_count` |
| `home.bulk_action_completed` | User completes a batch action | `action` (add_to_circle/delete), `selected_count`, `target_circle` (if applicable) |

### 10.4 Navigation

| Event | Trigger | Properties |
|-------|---------|------------|
| `home.add_contact_tapped` | User taps [+ Add] button | (none) |
| `home.deep_link_handled` | Deep link routed to Home tab | `url`, `section` (if applicable), `contact_id` (if applicable) |

---

## 11) Accessibility

### 11.1 VoiceOver Labels

| Element | VoiceOver label | VoiceOver hint |
|---------|----------------|----------------|
| Navigation title | "Rin, Home" | (none) |
| Add button | "Add contact" | "Creates a new contact" |
| Search bar | "Search contacts" | "Search by name, phone, or email" |
| Smart section header | "[Section name], [count] items" | "Double tap to expand or collapse" |
| Dedup card | "Possible duplicate, [name 1] and [name 2], [confidence] percent match" | "Actions available: merge, not the same, skip" |
| Contact row | "[Name], [subtitle], in [circle names]" | "Double tap to view contact details" |
| Circle dots | "Member of [circle 1], [circle 2]" | (none) |
| Enrichment badge | "Has enriched information from Rin" | (none) |
| Tab badge | "Home, [count] items need attention" | (none) |
| Filter button | "Filter and sort contacts" | "Opens filter options" |
| Multi-select checkbox | "[Name], [selected/not selected]" | "Double tap to toggle selection" |
| Pull-to-refresh | "Pull to refresh contacts" (system default) | (none) |

### 11.2 Dynamic Type

- All text elements use `Font.system` with `TextStyle` mapping for Dynamic Type scaling.
- Contact row height adapts to accommodate larger text sizes.
- Smart section cards grow vertically; horizontal scroll sections maintain card width and increase card height.
- At AX5 size: contact row may expand to 3 lines (name, subtitle each get more room). Circle dots remain fixed size (minimum 8pt).
- Section index scrubber letter size scales with Dynamic Type.

### 11.3 Semantic Grouping

- Smart sections area is an `accessibilityElement` container labeled "Smart sections".
- Contact list sections (A, B, C...) are labeled as "Section [letter], [count] contacts".
- Multi-select toolbar is an `accessibilityElement` container labeled "Batch actions, [count] selected".

### 11.4 Reduced Motion

- When `UIAccessibility.isReduceMotionEnabled`:
  - Dedup card dismiss uses fade instead of slide.
  - Score card delta arrow does not animate.
  - Pull-to-refresh uses standard spinner without custom animation.
  - Smart section expand/collapse is instant (no spring animation).

### 11.5 Color and Contrast

- All text meets WCAG 2.1 AA contrast ratio (4.5:1 for body text, 3:1 for large text).
- Circle dots have sufficient contrast against both `rin.bg.primary` and `rin.bg.secondary`.
- Enrichment badge icon is not color-only; it also uses a distinct shape (sparkles) recognizable without color.
- Badge counts use white text on `rin.brand.error` background (contrast ratio >4.5:1).

---

## 12) Transitions

### 12.1 Contact Detail

| From | To | Transition | Navigation |
|------|----|-----------|------------|
| Contact row tap | Contact detail screen | Standard push (slide left) | `HomeCoordinator.navigate(to: .contactDetail(id:))` |
| Recently Added card tap | Contact detail screen | Standard push | Same |
| Enrichment Update card tap | Contact detail screen | Standard push | Same |
| Upcoming card "View" | Contact detail screen | Standard push | Same |

### 12.2 Dedup Review

| From | To | Transition | Navigation |
|------|----|-----------|------------|
| "See All N Items" in Needs Attention | Full-screen dedup review list | Standard push | `HomeCoordinator.navigate(to: .dedupReview)` |
| Inline dedup card actions (Merge/Not Same/Skip) | Card animates out in place | Card removal animation (250ms, `rin.motion.dedupDismiss`) | No navigation change |

### 12.3 Search

| From | To | Transition | Navigation |
|------|----|-----------|------------|
| Search bar tap | Search active state | Keyboard slides up, list filters inline | No navigation change (same screen, different state) |
| Search result tap | Contact detail screen | Standard push | `HomeCoordinator.navigate(to: .contactDetail(id:))` |
| Search cancel | Full list restored | Keyboard dismisses, list restores | No navigation change |

### 12.4 Circle Management

| From | To | Transition | Navigation |
|------|----|-----------|------------|
| Suggested Circle card "Review" | Circle assignment confirmation sheet | Half-sheet modal | `.sheet(isPresented:)` |
| Filter > Circle chip tap | Filtered contact list | Inline filter (no navigation) | No navigation change |
| Multi-select > "Add to Circle" | Circle picker sheet | Half-sheet modal | `.sheet(isPresented:)` |

### 12.5 Score

| From | To | Transition | Navigation |
|------|----|-----------|------------|
| Score Changed card tap | Score tab | Tab switch | `AppCoordinator.switchTab(.score)` |

### 12.6 Manual Contact Creation

| From | To | Transition | Navigation |
|------|----|-----------|------------|
| [+ Add] button | New contact form | Full-height sheet modal | `.sheet(isPresented:)` with NavigationStack inside |

---

## 13) Onboarding-to-Home Transition

The onboarding first-value home (S12) and the steady-state Home tab are the same screen with different initial content.

### 13.1 S12 to Home Continuity

When onboarding completes (S12):
1. `onboarding.completed` event fires.
2. Full-screen onboarding cover dismisses.
3. Tab bar appears. Home tab is selected.
4. Home tab loads with smart sections populated from the just-completed sync:
   - "Needs Attention" with dedup suggestions (if any found during onboarding sync).
   - "Recently Added" with all imported contacts (all are "recent" on day 1).
   - "Enrichment Updates" (if any enrichments resolved during sync).
5. The S12 CTAs ("Review and clean your network", "Set who can reach you") are NOT replicated on the steady-state Home tab. They were one-time onboarding prompts. The smart sections now serve that purpose organically.

### 13.2 First-Launch Differentiation

On the very first Home tab display (immediately post-onboarding), if the dedup count is non-zero, the "Needs Attention" section is expanded by default and the first dedup card is visually emphasized with a subtle border pulse (same animation as deep link highlight). This draws the user's eye to their first actionable task.

On all subsequent launches, sections are in their last-saved collapse state.

---

## 14) State Matrix

| State | Smart Sections | Contact List | Search | Badge | Notes |
|-------|---------------|-------------|--------|-------|-------|
| First launch (post-onboarding) | Populated from initial sync | Full list | Available | Count from dedup | S12 transition |
| Day-2 with pending dedup | Needs Attention + others | Full list | Available | Count | Normal active state |
| All dedup reviewed, no events | None visible | Full list | Available | 0 (no badge) | Steady state (section 4) |
| Permission denied, no manual contacts | None | Empty state 6.1 | Hidden (no contacts to search) | 0 | Re-prompt on CTA tap |
| Permission denied, some manual contacts | May have sections if applicable | Manual contacts list | Available | 0 | Limited mode |
| Sync in progress | May be partially populated | Partial or loading | Available (searches cache) | Previous count | Inline sync indicator |
| Offline | Cached sections | Cached list | Local search only | Cached count | Offline banner at top |
| Error (sync failed) | Cached sections | Cached list | Local search only | Cached count | Error in sync status bar |

---

## 15) Offline and Error Behavior

### 15.1 Offline Mode

When the device has no network connectivity:
- All cached data remains fully browsable (contacts, smart sections from last sync).
- Search operates against local SwiftData cache only (no server search).
- Pull-to-refresh shows: `You're offline. Contacts will sync when you reconnect.`
- No smart section updates (enrichment, score changes require server).
- Tab badge shows last-known count.

### 15.2 Sync Error

If a delta sync fails (server error, timeout):
- Sync status bar shows: `Sync failed. Pull to retry.` with `rin.brand.warning` color.
- All cached data remains usable.
- No data is lost or corrupted (sync is idempotent per `CONTACTS_IMPORT_SYNC_UX_V1.md` section 2.3).
- Automatic retry on next app foreground or next background refresh cycle.

---

## 16) Performance Requirements

| Metric | Target | Notes |
|--------|--------|-------|
| Time to interactive (Home tab) | <500ms | From tab switch or app launch to scrollable list |
| Contact list scroll | 60fps | No dropped frames during scroll through 10,000+ contacts |
| Search keystroke response | <100ms | Local search result update after each character |
| Smart section render | <200ms | All visible sections rendered from cached data |
| Pull-to-refresh to updated UI | <3 seconds | For delta sync with <100 changes |

### 16.1 Implementation Notes

- Contact list uses `LazyVStack` (or `List` with lazy loading) for virtualized rendering.
- Smart section cards are rendered eagerly (small count, above the fold).
- Contact avatar images loaded lazily with placeholder initials.
- Section index scrubber pre-computes section offsets.
- SwiftData `@Query` with appropriate `fetchLimit` and `fetchOffset` for large contact sets.

---

## 17) Open Decisions

1. **Alphabetical vs By Circle default**: Should the contact list default to alphabetical grouping (simpler, familiar) or grouped-by-circle (emphasizes Rin's unique value)? Alphabetical is specified as default in this spec, but circle grouping may better reinforce the product mental model. Needs user testing.

2. **Smart section persistence across sessions**: When a user collapses a section, should it stay collapsed forever, or reset to expanded on next app launch? Current spec says persists. Alternative: reset daily so users re-encounter sections they might have dismissed hastily.

3. **Score Changed card auto-dismiss timing**: Currently set to 48 hours. Should this be shorter (24 hours, one session) or should it persist until explicitly dismissed? Balances between "don't miss it" and "don't nag."

4. **Contact row subtitle content**: Should the subtitle always show the primary phone/email, or should it show contextual info (e.g., "VP Engineering at Acme Corp" if enriched, circle names if no phone)? Current spec uses phone/email for consistency. Contextual subtitles are richer but less predictable.

5. **Multi-select entry gesture**: Long-press is standard iOS but may conflict with future context menu on contact rows (peek, quick actions). Should multi-select require an explicit "Select" button in the navigation bar instead? Or should long-press trigger a context menu that includes "Select" as one option?
