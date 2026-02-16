# iOS Invite and Referral Screen Spec V1

## 1) Purpose

Screen-level specification for the invite and referral flow. Covers invite creation, invite receipt (new user from link), contextual invite prompts, and invite tracking dashboard. Designed to drive organic viral growth (K > 0.5) without spam, pressure, or dark patterns. Aligns with brand promise: "No spam. No surprise outreach."

Companion docs:
- `docs/plan/REFERRAL_NETWORK_EFFECTS_V1.md` (referral mechanics, reward tiers, fraud prevention)
- `docs/architecture/IOS_NAVIGATION_STATE_V1.md` (deep links: `rin://invite/{code}`, universal links: `rin.app/invite/{code}`)
- `docs/product/IOS_ONBOARDING_SCREEN_SPEC_V1.md` (onboarding flow, S1-S12)
- `docs/product/IOS_INSTALL_TO_FIRST_VALUE_UX_V1.md` (first-value context)
- `docs/product/CONTACTS_IMPORT_SYNC_UX_V1.md` (contacts context)
- `docs/product/IOS_PROFILE_CIRCLE_SCREEN_SPEC_V1.md` (Profile Home quick actions)
- `docs/design/BRAND_NARRATIVE_V1.md` (tone, positioning)
- `docs/design/IOS_DESIGN_TOKENS_V1.md` (visual tokens)
- `docs/analytics/KPI_HIERARCHY_V1.md` (viral coefficient K target > 0.5)
- `docs/analytics/PRODUCT_ANALYTICS_EVENT_TAXONOMY_V1.md` (event naming conventions)

---

## 2) Flow Overview

Four primary flows:

1. **INV1: Share Rin** — user-initiated invite via share sheet.
2. **INV2: Invite from Contact Detail** — invite a specific non-Rin contact.
3. **INV3: Invite Receipt** — new user arrives from invite link.
4. **INV4: Invite Tracking Dashboard** — inviter views their invite activity.

Plus one supporting mechanism:

5. **Contextual invite prompts** — non-intrusive, in-app-only nudges after value-delivered moments.

---

## 3) Navigation Map

```
Profile Home (P1)
├── "Share Rin" quick action → INV1 (Share Screen)
│   └── INV4 (Invite Tracking Dashboard)
│       └── Referral Terms (How Referrals Work)
└── Settings
    └── "Share Rin" → INV1

Contact Detail
└── "Invite to Rin" action → INV2 (Contact-Specific Share)

Home Tab
└── Contextual prompt card → INV1

Deep Link (rin.app/invite/{code})
└── INV3 (Invite Receipt Flow → Onboarding with attribution)
```

---

## 4) INV1: Share Rin

### 4.1 Entry Points

| Entry point | Location | Context |
|-------------|----------|---------|
| Profile Home → Share Rin | Quick Actions section in P1 | Intentional sharing from profile |
| Contact Detail → Invite to Rin | Action row on non-Rin contact | Relationship-specific invite (see INV2) |
| Home tab → contextual prompt | Smart sections card | After value-delivered moment (see section 9) |
| Settings → Share Rin | Settings list item | Intentional sharing from settings |

### 4.2 Share Screen Layout

```
+------------------------------------------+
|  < Back              Share Rin            |
+------------------------------------------+
|                                           |
|         [Rin logo / brand mark]           |
|                                           |
|      Own your network.                    |
|      Share Rin with someone who           |
|      cares about their contacts.          |
|                                           |
+------------------------------------------+
|  Your invite link                         |
|  ┌──────────────────────────────────┐     |
|  │ https://rin.app/invite/a3Xk9m2Q │     |
|  │                          [Copy]  │     |
|  └──────────────────────────────────┘     |
|                                           |
|  Message preview                          |
|  ┌──────────────────────────────────┐     |
|  │ I use Rin to organize and        │     |
|  │ control my contacts. Try it:     │     |
|  │ https://rin.app/invite/a3Xk9m2Q  │     |
|  │                          [Edit]  │     |
|  └──────────────────────────────────┘     |
|                                           |
|  [ Share via Messages ]  (primary CTA)    |
|  [ Share via... ]        (iOS share sheet)|
|                                           |
+------------------------------------------+
|  Your invites: 5 sent, 3 joined           |
|  [View invite activity →]                 |
+------------------------------------------+
```

### 4.3 Share Screen Behavior

**On screen load:**
1. Fetch or reuse the user's unique referral link. Link format: `https://rin.app/invite/{code}`.
2. Code is 8-character alphanumeric, tied to the inviter's principal ID.
3. Link is unique per inviter, reusable across sends. No expiry in v1.
4. Pre-fill message: `"I use Rin to organize and control my contacts. Try it: [link]"`
5. Show invite summary footer: sent count and joined count.

**User actions:**
- **Copy link**: copies `https://rin.app/invite/{code}` to clipboard. Brief haptic + "Copied" toast (1.5s).
- **Edit message**: tapping Edit on the message preview makes the text editable inline. User can customize before sharing.
- **Share via Messages**: opens iOS Messages compose with pre-filled message text.
- **Share via...**: opens standard iOS `UIActivityViewController` with the message text and link. Available channels: Messages, WhatsApp, Telegram, Email, Copy, AirDrop, and any other installed share targets.
- **View invite activity**: navigates to INV4 (Invite Tracking Dashboard).

**Link mechanics (universal link):**
- `rin.app/invite/{code}` is registered as a universal link via Apple-App-Site-Association.
- If Rin is installed: opens app directly, deep links to invite attribution handler.
- If Rin is not installed: opens App Store listing. Invite context preserved via deferred deep link (server-side link resolution on first app launch).

### 4.4 Share Screen States

| State | Condition | Behavior |
|-------|-----------|----------|
| Default | Screen loaded, link ready | Full layout as described |
| Link loading | Link being generated (first time) | Skeleton placeholder for link field, primary CTA disabled |
| Link error | Server unreachable | Error banner: "Can't generate invite link right now. Try again." with Retry |
| Message editing | User tapped Edit | Message field becomes editable, keyboard visible, Save/Cancel controls |
| Share sheet open | User tapped Share via... | iOS share sheet presented as half-sheet |
| Copy confirmed | User tapped Copy | "Copied" toast, Copy button briefly shows checkmark |
| Offline | No network | Link from cache if previously generated; if no cached link, show offline state |

### 4.5 Design Tokens

| Element | Token | Value |
|---------|-------|-------|
| Screen title | `rin.type.title1` | 28pt Bold |
| Tagline | `rin.type.body` | 17pt Regular, `rin.text.primary` |
| Link field background | `rin.bg.tertiary` | Light: `#F3F4F6`, Dark: `#1A1A1A` |
| Link text | `rin.type.callout` | 16pt Regular, `rin.brand.primary` |
| Copy button | `rin.type.caption` | 12pt, `rin.brand.primary` |
| Message preview background | `rin.bg.secondary` | Light: `#F9FAFB`, Dark: `#111111` |
| Message text | `rin.type.body` | 17pt Regular, `rin.text.primary` |
| Primary CTA | `PrimaryButton` | Full width, `rin.brand.primary` background |
| Secondary CTA | `SecondaryButton` | Full width, outlined |
| Footer stats | `rin.type.footnote` | 13pt Regular, `rin.text.secondary` |
| Card corners | `rin.radius.lg` | 12pt |
| Internal padding | `rin.space.base` | 16pt |
| Section gaps | `rin.space.lg` | 24pt |

---

## 5) INV2: Invite from Contact Detail

### 5.1 Visibility Rule

The "Invite to Rin" button appears in the contact detail action row when:
- The contact is NOT a Rin user (no matched Rin principal ID).
- The contact has at least one phone number or email address (a channel to reach them).

When the contact IS a Rin user: button is not shown. The "On Rin" enrichment badge is shown instead (per CONTACTS_IMPORT_SYNC_UX_V1.md section 6.2).

### 5.2 Button Placement

Within the Contact Detail view (CONTACTS_IMPORT_SYNC_UX_V1.md section 7.3), the "Invite to Rin" button sits in the **Actions** section (section 6 of the contact detail layout), alongside call, message, share contact, and remove from Rin.

```
┌─────────────────────────────────┐
│ Alex Johnson                    │
│                                 │
│ Actions                         │
│   [Call]  [Message]  [Share]    │
│   [Invite to Rin]               │
│   [Remove from Rin]             │
└─────────────────────────────────┘
```

### 5.3 Contact-Specific Share Behavior

Tapping "Invite to Rin" opens the share sheet (same as INV1) with a personalized pre-filled message:

- Default message: `"Hey [First Name], I use Rin to manage my contacts. Join me: [link]"`
- `[First Name]` is the contact's given name from the contact record.
- If first name is unavailable, fall back to generic: `"I use Rin to organize and control my contacts. Try it: [link]"`
- User can edit the message before sending.

The share sheet opens directly (no intermediate Share Rin screen) because the context is already specific: inviting a known contact.

### 5.4 States

| State | Condition | Behavior |
|-------|-----------|----------|
| Visible | Contact is not a Rin user and has a reachable channel | "Invite to Rin" button shown in actions |
| Hidden | Contact is a Rin user | Button not rendered |
| Hidden | Contact has no phone or email | Button not rendered (no way to reach them) |
| Loading | Share sheet preparing | Brief loading indicator on button |
| Shared | User completed share | Button text changes to "Invited" with checkmark for current session |

---

## 6) INV3: Invite Receipt Flow (New User from Invite)

### 6.1 Link Resolution

```
Recipient taps rin.app/invite/{code}
    |
    ├── App installed → app opens
    │   └── AppCoordinator.handleDeepLink(url:)
    │       └── Parse invite code → store attribution locally
    │           └── If authenticated: capture attribution, show confirmation
    │           └── If not authenticated: proceed to onboarding with attribution
    │
    └── App not installed → App Store
        └── User installs → first launch
            └── Deferred deep link resolved (server-side)
                └── Attribution captured → onboarding begins with invite context
```

**Deferred deep link resolution:**
- On first app launch, client calls server with device identifiers.
- Server matches against invite link click records.
- If match found: attribution stored. Invite code associated with new principal.
- Attribution window: 7 days from link click (per REFERRAL_NETWORK_EFFECTS_V1.md section 2.5).

### 6.2 Onboarding Modifications for Invited Users

The standard onboarding flow (S1-S12) applies with the following additions:

**S1 modification — Social proof enhancement:**

```
+------------------------------------------+
|                                           |
|      Own your network.                    |
|                                           |
|      Rin helps you clean, organize,       |
|      and control your contacts.           |
|                                           |
|  ┌──────────────────────────────────┐     |
|  │  [Avatar]  Invited by [Name]     │     |
|  └──────────────────────────────────┘     |
|                                           |
|      [ Continue ]                         |
|                                           |
+------------------------------------------+
```

- A small card below the standard S1 body text shows: the inviter's avatar (if available) and display name.
- Copy: `"Invited by [Inviter Display Name]"`.
- If inviter name is unavailable (edge case: account deleted), omit the card entirely. Fall back to standard S1.

**Post-S5 (phone verification) — Auto-connection:**

After the invitee completes phone verification (S5):
1. Server creates a mutual connection between inviter and invitee.
2. Both are added to each other's "Contacts" circle (the mandatory default circle).
3. No additional permission is needed — the invite implies mutual interest in connecting.
4. This connection happens silently in the background; no blocking UI step is added to onboarding.

**S12 (First-Value Home) — Inviter visible:**

On the first-value home screen, the inviter appears in the contact list as an already-connected Rin user with the enrichment badge. This provides immediate social proof and demonstrates network value.

### 6.3 Inviter Notification

When the invitee completes onboarding (reaches S12):
- Inviter receives a push notification: `"[Invitee Name] joined Rin from your invite."`
- Deep link: `rin://contacts/{invitee_id}` (opens the invitee's contact detail in the inviter's app).
- Notification type added to the push notification deep link table (per IOS_NAVIGATION_STATE_V1.md section 3.4):

| Notification type | Deep link |
|-------------------|-----------|
| Invite accepted | `rin://contacts/{id}` |

### 6.4 Existing User Taps Invite Link

If a user who already has Rin installed and is authenticated taps an invite link:
- App opens and recognizes the user is already on Rin.
- Show a brief toast: `"You're already on Rin."`
- No attribution is recorded (existing users cannot be re-attributed).
- Navigate to Home tab.

### 6.5 States

| State | Condition | Behavior |
|-------|-----------|----------|
| Fresh install from invite | App not installed, link tapped | App Store → install → deferred deep link → onboarding with invite context |
| Direct open from invite | App installed, not authenticated | Open app → onboarding with invite context |
| Existing user | App installed, authenticated | Toast "You're already on Rin." → Home |
| Attribution expired | Link clicked > 7 days ago, now installing | Standard onboarding, no invite context |
| Inviter account deleted | Inviter no longer exists | Omit "Invited by" card, standard onboarding |
| Link invalid | Code not found on server | Standard onboarding, no invite context |

---

## 7) INV4: Invite Tracking Dashboard

### 7.1 Access

- From INV1 (Share Screen): tap "View invite activity" footer link.
- From Profile Home (P1): Share Rin quick action → Share Screen → View invite activity.

### 7.2 Dashboard Layout

```
+------------------------------------------+
|  < Back        Your Invites               |
+------------------------------------------+
|                                           |
|  ┌──────────────────────────────────┐     |
|  │  Invites Sent          12       │     |
|  │  Installed               7       │     |
|  │  Completed Onboarding    5       │     |
|  │                                  │     |
|  │  ████████████░░░░  5 of 12      │     |
|  │  joined Rin                      │     |
|  └──────────────────────────────────┘     |
|                                           |
|  Accepted Invites                         |
|  ┌──────────────────────────────────┐     |
|  │ [Avatar] Alex Johnson            │     |
|  │          Joined Feb 12, 2026     │     |
|  ├──────────────────────────────────┤     |
|  │ [Avatar] Sam Park                │     |
|  │          Joined Feb 10, 2026     │     |
|  ├──────────────────────────────────┤     |
|  │ [Avatar] Jordan Lee              │     |
|  │          Joined Feb 8, 2026      │     |
|  └──────────────────────────────────┘     |
|                                           |
|  [How referrals work →]                   |
|                                           |
+------------------------------------------+
```

### 7.3 Dashboard Sections

**Summary card (top):**

| Metric | Definition | Display |
|--------|-----------|---------|
| Invites Sent | Total invite links shared (tracked via share sheet completion) | Integer |
| Installed | Invitees who installed Rin via this user's link | Integer |
| Completed Onboarding | Invitees who completed onboarding (reached S12) | Integer |

- Progress bar: visual ratio of `Completed Onboarding / Invites Sent`.
- Bar color: `rin.brand.primary` for filled portion, `rin.bg.tertiary` for unfilled.
- Summary line: `"[N] of [M] joined Rin"` below the bar.

**Accepted invites list:**
- Each row: invitee avatar, display name, and join date.
- Sorted by join date, most recent first.
- Tapping a row navigates to that contact's detail screen: `rin://contacts/{id}`.
- Only invitees who completed onboarding appear in this list.

**Referral terms link:**
- Footer link: "How referrals work" → opens referral terms screen.
- Terms content matches REFERRAL_NETWORK_EFFECTS_V1.md section 9, rendered as a scrollable text screen.

### 7.4 Dashboard States

| State | Condition | Behavior |
|-------|-----------|----------|
| Default | Has invite activity | Full layout with summary card and accepted list |
| Empty | No invites sent yet | Empty state view (see section 7.5) |
| Partial | Invites sent but none accepted | Summary card with counts, empty accepted list with "No one has joined yet. Share your link to get started." |
| Loading | Fetching dashboard data | Skeleton placeholders for summary card and list |
| Error | Server unreachable | Error banner: "Can't load invite activity. Try again." with Retry |
| Offline | No network | Show cached data if available, stale indicator. If no cache, offline state |

### 7.5 Empty State

```
+------------------------------------------+
|  < Back        Your Invites               |
+------------------------------------------+
|                                           |
|                                           |
|          [share icon]                     |
|                                           |
|   Share Rin to see your                   |
|   invite activity here.                   |
|                                           |
|      [ Share Rin ]                        |
|                                           |
|                                           |
+------------------------------------------+
```

- Icon: SF Symbol `square.and.arrow.up` at size 48pt, color `rin.text.tertiary`.
- CTA: "Share Rin" → navigates back to INV1 share screen.

### 7.6 Design Tokens

| Element | Token | Value |
|---------|-------|-------|
| Screen title | `rin.type.title1` | 28pt Bold |
| Summary card | `CardView` standard variant | `rin.bg.secondary` background, `rin.radius.lg` corners |
| Metric labels | `rin.type.subheadline` | 15pt Regular, `rin.text.secondary` |
| Metric values | `rin.type.headline` | 17pt Semibold, `rin.text.primary` |
| Progress bar height | — | 8pt, `rin.radius.full` corners |
| Progress bar fill | `rin.brand.primary` | `#1A73E8` |
| Progress bar background | `rin.bg.tertiary` | Light: `#F3F4F6`, Dark: `#1A1A1A` |
| Summary line | `rin.type.footnote` | 13pt Regular, `rin.text.secondary` |
| List row avatar | `AvatarView` sm (32pt) | — |
| List row name | `rin.type.headline` | 17pt Semibold |
| List row date | `rin.type.footnote` | 13pt Regular, `rin.text.secondary` |
| Footer link | `rin.type.callout` | 16pt Regular, `rin.brand.primary` |
| Empty state icon | SF Symbol | 48pt, `rin.text.tertiary` |
| Empty state title | `rin.type.title3` | 20pt Semibold, `rin.text.primary` |
| Empty state body | `rin.type.body` | 17pt Regular, `rin.text.secondary` |
| Section gaps | `rin.space.lg` | 24pt |

---

## 8) Referral Incentive Display (V1)

### 8.1 V1 Approach: Social Incentive Only

V1 does not include monetary or premium rewards for referrals. The incentive is social:
- Inviter sees their invite count and accepted count on the share screen footer and tracking dashboard.
- The "Invited by [Name]" card during invitee onboarding creates social reciprocity.
- The auto-connection after onboarding delivers immediate relationship value.

### 8.2 Premium Reward (Future, Per REFERRAL_NETWORK_EFFECTS_V1.md)

The referral strategy doc defines a premium reward structure (3 qualified friends = 1 month premium). This is **not implemented in v1** but the dashboard data model should support it:
- Track qualification status per invitee (installed, completed onboarding, met activity threshold).
- When premium rewards are enabled, the dashboard summary card extends with reward tier display.
- The share screen footer extends with: "Invite 3 friends who join to get 1 month of Rin Premium."

### 8.3 No Aggressive Gamification

Per brand values (BRAND_NARRATIVE_V1.md section 3.2 — Respect for Attention):
- No leaderboards.
- No competitive ranking against other inviters.
- No countdown timers or urgency mechanics.
- No "you're so close!" progress nudges outside the dashboard.
- The invite count is informational, not motivational pressure.

---

## 9) Contextual Invite Prompts

### 9.1 Principles

- In-app only. Never push notifications.
- Dismissable. Never modal or blocking.
- Infrequent. Max one prompt per week. Max three total per user lifetime before permanently suppressed.
- Contextual. Shown only after a value-delivered moment, when the user has reason to believe Rin is worth sharing.
- Format: small card in Home tab smart sections (same visual treatment as dedup suggestion cards).

### 9.2 Prompt Triggers

| Trigger | Condition | Message |
|---------|-----------|---------|
| First dedup review complete | User resolved 3+ dedup suggestions in one session | "Know someone who'd benefit from cleaning up their contacts?" |
| Contact count threshold | User reaches 50+ imported contacts | "Rin works better when your contacts join too." |
| Score milestone | Rin Score reaches "Good" (60+) for the first time | "Share Rin with friends to grow your network." |

### 9.3 Prompt Layout

```
┌──────────────────────────────────┐
│  Share Rin                       │
│                                  │
│  Know someone who'd benefit from │
│  cleaning up their contacts?     │
│                                  │
│  [Share Rin]        [Dismiss]    │
└──────────────────────────────────┘
```

- Rendered as a `CardView` standard variant in the Home tab smart sections.
- Position: below "Needs Attention" section, above "Recently Added" section.
- "Share Rin" button navigates to INV1 (Share Screen).
- "Dismiss" removes the card and increments the user's prompt dismiss counter.

### 9.4 Prompt Suppression Rules

| Rule | Threshold |
|------|-----------|
| Minimum interval between prompts | 7 days |
| Maximum prompts shown (lifetime) | 3 |
| Suppress if user has shared in last 14 days | Yes |
| Suppress if user dismissed last prompt < 7 days ago | Yes |
| Suppress if user has < 10 contacts | Yes (insufficient value delivered) |

After 3 prompts shown (whether dismissed or acted on), no further contextual invite prompts are displayed. The user can still access invite functionality via entry points in section 4.1.

### 9.5 Prompt States

| State | Behavior |
|-------|----------|
| Eligible | Trigger condition met and suppression rules pass → card rendered |
| Dismissed | User tapped Dismiss → card removed, counter incremented |
| Acted on | User tapped Share Rin → navigate to INV1, card removed, counter incremented |
| Suppressed | Counter >= 3 or interval rule active → card not rendered |

---

## 10) Privacy Constraints

| Constraint | Implementation |
|------------|---------------|
| Invite link landing page is generic | The web page at `rin.app/invite/{code}` does NOT show the inviter's name, photo, or profile. It shows a generic Rin marketing page with App Store link. Attribution is resolved server-side only after install. |
| Inviter cannot see link click data | The tracking dashboard shows installs and onboarding completions only. Link clicks, App Store views, and incomplete installs are not surfaced to the inviter. This prevents surveillance of link recipients. |
| Auto-connection is limited to Contacts circle | Invitee is added to inviter's "Contacts" circle only. Not "Friends," not "Family," not any custom circle. The inviter can manually move the invitee to a closer circle later. |
| No contact list scraping for invites | Rin never reads the user's address book to generate a list of "people to invite." The user chooses who to share with via the standard iOS share sheet. |
| No auto-messaging | Rin never sends messages to the user's contacts on the user's behalf. All sharing is user-initiated through the iOS share sheet. |
| Invite data retention | Invite link click records are retained for the 7-day attribution window, then deleted. Successful attributions (install + onboarding) are retained permanently as part of the referral relationship. |

---

## 11) Events

All events follow the `object_action` naming convention (per PRODUCT_ANALYTICS_EVENT_TAXONOMY_V1.md section 3).

### 11.1 Invite Creation Events

| Event | Properties | Trigger |
|-------|-----------|---------|
| `invite_link_created` | `source` (profile / contact / prompt / settings) | Referral link generated (first time or refreshed) |
| `invite_link_shared` | `channel` (messages / whatsapp / email / copy / airdrop / other), `source`, `message_customized` (bool) | User completes share via share sheet |
| `invite_link_copied` | `source` | User taps Copy on share screen |

### 11.2 Invite Receipt Events

| Event | Properties | Trigger |
|-------|-----------|---------|
| `invite_link_opened` | `invite_code`, `referrer_id` (hashed) | Recipient opens universal link (app installed) |
| `invite_deferred_resolved` | `invite_code`, `referrer_id` (hashed), `days_since_click` | Deferred deep link resolved on first launch |
| `invite_app_installed` | `invite_code`, `referrer_id` (hashed) | Attributed install detected |
| `invite_onboarding_completed` | `invite_code`, `referrer_id` (hashed), `invitee_id` (hashed) | Invited user reaches S12 |
| `invite_auto_connected` | `inviter_id` (hashed), `invitee_id` (hashed) | Mutual connection created post-verification |

### 11.3 Prompt Events

| Event | Properties | Trigger |
|-------|-----------|---------|
| `invite_prompt_shown` | `trigger` (dedup_review / contact_threshold / score_milestone), `prompt_number` (1-3) | Contextual prompt card rendered |
| `invite_prompt_dismissed` | `trigger`, `prompt_number` | User taps Dismiss |
| `invite_prompt_tapped` | `trigger`, `prompt_number` | User taps Share Rin on prompt |

### 11.4 Dashboard Events

| Event | Properties | Trigger |
|-------|-----------|---------|
| `invite_dashboard_viewed` | `sent_count`, `installed_count`, `completed_count` | Dashboard screen opened |
| `invite_dashboard_contact_tapped` | `invitee_id` (hashed) | User taps an accepted invite row |
| `invite_terms_viewed` | — | User opens "How referrals work" |

### 11.5 Notification Events

| Event | Properties | Trigger |
|-------|-----------|---------|
| `invite_notification_sent` | `inviter_id` (hashed), `invitee_id` (hashed) | Push sent to inviter when invitee joins |
| `invite_notification_tapped` | `inviter_id` (hashed), `invitee_id` (hashed) | Inviter taps the notification |

---

## 12) Accessibility

### 12.1 Share Screen (INV1)

- Invite link field: VoiceOver reads full URL. Copy button labeled "Copy invite link."
- Message preview: VoiceOver reads full message text. Edit button labeled "Edit invite message."
- Share buttons: labeled "Share via Messages" and "Open share options."
- Footer stats: VoiceOver reads as a single group: "You've sent 5 invites. 3 people joined."

### 12.2 Contact Invite (INV2)

- "Invite to Rin" button: VoiceOver label includes contact name: "Invite Alex Johnson to Rin."
- Button state change: when showing "Invited" state, VoiceOver reads "Alex Johnson invited to Rin."

### 12.3 Onboarding Invite Context (INV3)

- "Invited by" card: VoiceOver reads as "Invited by [Name]" with inviter avatar described.
- Auto-connection is silent and requires no accessibility consideration (no UI element).

### 12.4 Tracking Dashboard (INV4)

- Summary card metrics: each metric is a VoiceOver element reading label and value ("Invites sent: 12").
- Progress bar: VoiceOver reads as "5 of 12 invited friends joined Rin."
- Accepted invites list: standard list row accessibility. Each row reads name and join date.
- Empty state: VoiceOver reads title and body as a group, CTA is the focus target.

### 12.5 Contextual Prompts

- Prompt card: VoiceOver announces when card appears in smart sections.
- VoiceOver reads card title and message as a group.
- "Share Rin" and "Dismiss" buttons are separately focusable.
- Dismiss action: VoiceOver announces "Invite prompt dismissed."

### 12.6 Global

- All screens support Dynamic Type up to `AX5`.
- All interactive elements meet minimum 44x44pt touch target.
- All text meets WCAG AA contrast ratios (enforced by semantic color tokens).
- Reduced Motion: no custom animations in invite flow beyond standard navigation transitions.

---

## 13) Error Handling

| Error | Cause | User-facing message | Recovery |
|-------|-------|---------------------|----------|
| Link generation failed | Server error | "Can't generate invite link right now." | Retry button |
| Link generation timeout | Slow network | "Taking longer than expected." | Retry button, 10s timeout |
| Deferred deep link not resolved | Attribution server unreachable | (Silent) No invite context shown | Standard onboarding proceeds |
| Dashboard data load failed | Server error | "Can't load invite activity." | Retry button |
| Share sheet cancelled | User dismissed iOS share sheet | (Silent) Return to share screen | No action needed |
| Auto-connection failed | Server error during mutual add | (Silent) Retry in background | Auto-retry on next sync |

All errors follow the brand tone: state what happened, state what the user can do. No "Oops," no apologies.

---

## 14) Edge Cases

1. **User has no network connection when opening share screen**: show cached invite link if previously generated. If no cached link, show offline state with "You need a connection to generate your invite link."

2. **Invitee installs app weeks after clicking link (beyond 7-day attribution window)**: standard onboarding without invite context. No "Invited by" card. No auto-connection. Inviter receives no notification.

3. **Invitee already has a Rin account (different phone number)**: if they verify a different phone number during onboarding, attribution is captured normally. Auto-connection uses the verified identity.

4. **Inviter deletes their account before invitee completes onboarding**: "Invited by" card is omitted. No auto-connection. Attribution still recorded for analytics (referrer marked as deleted).

5. **Multiple people share the same link with the same recipient**: last-click attribution (per REFERRAL_NETWORK_EFFECTS_V1.md section 2.5). Credit goes to the most recent referrer whose link the recipient clicked.

6. **User taps their own invite link**: app opens, recognizes authenticated user, shows toast "You're already on Rin." No self-referral recorded.

7. **Invitee denies contacts permission during onboarding**: auto-connection still works (it's server-side, not dependent on device contacts). The inviter appears as a Rin-only contact in the invitee's account.

8. **User shares link via copy and pastes into a channel not tracked**: `invite_link_copied` event is recorded. Downstream attribution works the same (link click is tracked regardless of source).

9. **Share screen opened from contextual prompt that was the user's 3rd prompt**: prompt counter incremented before navigation. Share screen opens normally. No further prompts will be shown.

10. **Invite link contains special characters in URL**: link codes are strictly alphanumeric (8 characters, [a-zA-Z0-9]). No URL encoding issues.

---

## 15) Implementation Phasing

Per REFERRAL_NETWORK_EFFECTS_V1.md section 6, invite features roll out in phases:

### Phase 1: Core Invite Loop (Stage 3 Beta)

Build:
- INV1 share screen with link generation and iOS share sheet.
- INV2 contact detail invite button.
- INV3 invite receipt with deferred deep link and auto-connection.
- INV4 tracking dashboard (social metrics only, no premium rewards).
- Push notification to inviter on invitee join.
- All invite creation and receipt events instrumented.

### Phase 2: Contextual Prompts (Stage 3 Weeks 2-4)

Build:
- Contextual invite prompt cards in Home smart sections.
- Prompt suppression logic (interval, lifetime cap, recent share check).
- Prompt events instrumented.
- A/B test: prompt copy and trigger timing.

### Phase 3: Premium Reward Integration (Post-Launch)

Build:
- Extend dashboard with reward tier display (per REFERRAL_NETWORK_EFFECTS_V1.md section 2.3).
- Add qualification tracking (activity threshold) to dashboard metrics.
- Add premium credit messaging to share screen.
- Add "Or invite friends" entry point on premium paywall.

---

## 16) KPI Alignment

This spec directly supports the following KPI targets (per KPI_HIERARCHY_V1.md):

| Metric | Target | How this spec contributes |
|--------|--------|---------------------------|
| Viral coefficient (K) | > 0.5 | Multiple low-friction entry points, personalized messages, contextual prompts, share moment alignment |
| Invite send rate | > 1.5 per active user/month | Four entry points, contextual triggers, frictionless share sheet |
| Invite conversion | > 30% | Personalized messages, "Invited by" social proof, auto-connection value |
| Onboarding completion | > 80% | Invite context enhances motivation, social proof on S1 |

---

## 17) Open Decisions

1. **Invite link format**: whether to use `rin.app/invite/{code}` (as defined in navigation spec) or `rin.app/r/{code}` (shorter, as mentioned in referral strategy doc). Need to align on one canonical format.

2. **Message pre-fill per channel**: whether to customize the default message based on share channel (shorter for iMessage, longer for email) or use one universal message.

3. **Inviter avatar on landing page**: whether the web landing page at `rin.app/invite/{code}` should show the inviter's name/photo for social proof (at the cost of privacy) or remain fully generic.

4. **Auto-connection notification for invitee**: whether the invitee should also receive a notification or in-app message confirming the auto-connection with the inviter, or if the inviter simply appearing in their contacts is sufficient.

5. **Dashboard data freshness**: whether the tracking dashboard should poll for updates in real-time (WebSocket or polling) or refresh only on screen load. Real-time adds complexity; on-load is simpler but stale.
