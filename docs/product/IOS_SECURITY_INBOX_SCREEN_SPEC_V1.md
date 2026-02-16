# iOS Security Inbox Screen Spec V1

## 1) Purpose

Single destination for reviewing, triaging, and acting on all security-related items: access requests (Ask flow), ownership disputes, account alerts, abuse reports, and trust signals. Reachable from Profile Home (P1 > Quick Actions > Security Inbox) and via deep link `rin://security`.

Companion docs:
- `docs/product/IOS_PROFILE_CIRCLE_SCREEN_SPEC_V1.md` (P1 Profile Home, C5 Access Request Detail)
- `docs/architecture/IOS_NAVIGATION_STATE_V1.md` (deep link table, tab badge management)
- `docs/operations/DISPUTE_PLAYBOOK_V1.md` (dispute case types, state machines, resolution workflows)
- `docs/product/SHADOW_PROFILE_UX_V1.md` (abuse controls S9, shadow restrictions)
- `docs/product/CIRCLE_MANAGEMENT_UX_V1.md` (Ask flow S3.3, access request lifecycle)
- `docs/architecture/PROFILE_CLASS_CONTRACT_V1.md` (class-specific security controls S9)
- `docs/design/IOS_DESIGN_TOKENS_V1.md` (color tokens, typography, spacing, components)

---

## 2) Screen Inventory

| ID | Screen | Entry point |
|----|--------|-------------|
| SEC1 | Security Inbox Root | P1 Quick Actions, deep link, push notification |
| SEC2 | Access Request Detail | SEC1 item tap (ACCESS REQUESTS section) |
| SEC3 | Dispute Detail | SEC1 item tap (DISPUTES section), deep link |
| SEC4 | Account Alert Detail | SEC1 item tap (ACCOUNT ALERTS section) |
| SEC5 | Report Status | SEC1 item tap (REPORTS section) |
| SEC6 | Evidence Submission | SEC3 inline action |
| SEC7 | File New Report | SEC5 CTA, contact/profile context menus |

---

## 3) SEC1: Security Inbox Root

### 3.1 Layout

```
┌──────────────────────────────────────────┐
│ ◀ Profile        Security (4)            │
│──────────────────────────────────────────│
│ [ All ] [ Action Needed ] [ Resolved ]   │
│──────────────────────────────────────────│
│                                          │
│  ACCESS REQUESTS                    2 ▸  │
│ ┌──────────────────────────────────────┐ │
│ │ 🔑  Alex wants your email            │ │
│ │     from Friends circle · 2h ago     │ │
│ │                      [Action Needed] │ │
│ ├──────────────────────────────────────┤ │
│ │ 🔑  Jordan wants your phone          │ │
│ │     from Colleagues circle · 1d ago  │ │
│ │                          [Pending]   │ │
│ └──────────────────────────────────────┘ │
│                                          │
│  DISPUTES                           0 ▸  │
│  No dispute items                        │
│                                          │
│  ACCOUNT ALERTS                     1 ▸  │
│ ┌──────────────────────────────────────┐ │
│ │ ⚠️  New device login detected        │ │
│ │     iPhone 17 Pro · San Jose · 4h    │ │
│ │                      [Action Needed] │ │
│ └──────────────────────────────────────┘ │
│                                          │
│  REPORTS                            1 ▸  │
│ ┌──────────────────────────────────────┐ │
│ │ 🛡  Report: fake_account_23          │ │
│ │     Impersonation · Filed 3d ago     │ │
│ │                      [Under Review]  │ │
│ └──────────────────────────────────────┘ │
│                                          │
└──────────────────────────────────────────┘
```

### 3.2 Header

- Back button returns to P1 (Profile Home).
- Title: "Security" with parenthetical count of unresolved items. Count uses `rin.brand.error` color token when > 0.
- Typography: `rin.type.title1` for title, `rin.type.headline` for count badge.

### 3.3 Filter Tabs

Horizontal segmented control below the header. Three segments:

| Tab | Shows |
|-----|-------|
| **All** | Every item across all categories, newest first |
| **Action Needed** | Items requiring user action (pending requests, unacknowledged alerts, open disputes awaiting user input) |
| **Resolved** | Items that are completed, dismissed, or closed |

Default selection: **All**. If the user arrives via a deep link with `?tab=requests` or `?tab=alerts`, scroll to that section within the active filter.

Tokens: `rin.type.subheadline` for segment labels. Active segment uses `rin.brand.primary` tint.

### 3.4 Section Layout

Sections are displayed in fixed order regardless of content:

1. **ACCESS REQUESTS**
2. **DISPUTES**
3. **ACCOUNT ALERTS**
4. **REPORTS**

Each section has:
- Section header: `SectionHeader` component with category name (left) and item count (right). Typography: `rin.type.caption` uppercase, color `rin.text.secondary`.
- Section count chevron: tappable, navigates to a filtered list showing only that category.
- Items listed as rows within the section.

If a section has zero items under the current filter, show a single-line placeholder: "No [category] items" in `rin.text.tertiary`, `rin.type.footnote`.

Sections with items are expanded by default. The filter tabs hide entire sections if they contain no matching items.

### 3.5 Item Row

Each item row is a `CardView` (standard variant) containing:

| Element | Token | Position |
|---------|-------|----------|
| Category icon | SF Symbol, `rin.text.secondary` | Leading, 24x24 |
| Title | `rin.type.headline` | Top, after icon |
| Subtitle / context | `rin.type.footnote`, `rin.text.secondary` | Below title |
| Relative timestamp | `rin.type.footnote`, `rin.text.tertiary` | Trailing or inline with subtitle |
| Status badge | `rin.type.caption`, pill shape (`rin.radius.full`) | Trailing, bottom |

**Category icons (SF Symbols):**

| Category | SF Symbol |
|----------|-----------|
| Access Request | `key.fill` |
| Dispute | `exclamationmark.shield.fill` |
| Account Alert | `exclamationmark.triangle.fill` |
| Report | `shield.lefthalf.filled` |

**Status badge colors:**

| Status | Background | Text |
|--------|-----------|------|
| Action Needed | `rin.brand.error` at 15% opacity | `rin.brand.error` |
| Pending | `rin.brand.warning` at 15% opacity | `rin.brand.warning` |
| Under Review | `rin.brand.primary` at 15% opacity | `rin.brand.primary` |
| Resolved | `rin.brand.secondary` at 15% opacity | `rin.brand.secondary` |
| Dismissed | `rin.text.tertiary` at 15% opacity | `rin.text.tertiary` |
| Appealed | `rin.brand.accent` at 15% opacity | `rin.brand.accent` |

### 3.6 Sorting

Items within each section are sorted by:
1. Status priority: Action Needed > Pending > Under Review > Appealed > Resolved > Dismissed.
2. Within the same status: newest first (by creation or last-updated timestamp).

### 3.7 Pull-to-Refresh

Standard pull-to-refresh gesture triggers a sync of all security items from the server. Spinner uses `rin.brand.primary`.

### 3.8 States

| State | Behavior |
|-------|----------|
| Loading | Skeleton placeholders for 4 rows across 2 sections |
| Loaded (items present) | Full section layout as described |
| Loaded (empty — all clear) | Empty state (see S12) |
| Loaded (filter yields no results) | Inline message: "No items match this filter" with option to reset filter |
| Error | `StatusBanner` (error variant) with retry button |
| Offline | `StatusBanner` (offline variant): "You're offline. Showing cached items." |

---

## 4) SEC2: Access Request Detail

Expands the C5 screen from `IOS_PROFILE_CIRCLE_SCREEN_SPEC_V1.md` with additional context for the Security Inbox surface.

### 4.1 Layout

```
┌──────────────────────────────────────────┐
│ ◀ Security     Access Request            │
│──────────────────────────────────────────│
│                                          │
│         ┌──────────┐                     │
│         │  [Photo] │                     │
│         │   Alex   │                     │
│         │  Friends │                     │
│         └──────────┘                     │
│                                          │
│  REQUESTER                               │
│  Name           Alex Rivera              │
│  Circle         Friends                  │
│  Relationship   Added 3 months ago       │
│  Mutual circles 2 (Friends, Colleagues)  │
│                                          │
│  WHAT THEY'RE REQUESTING                 │
│ ┌──────────────────────────────────────┐ │
│ │  📧 Email address                    │ │
│ │  📞 Phone number                     │ │
│ └──────────────────────────────────────┘ │
│                                          │
│  REASON (optional)                       │
│  "Need to send you the event invite"     │
│                                          │
│  ┌─ Allow for all fields from ─────┐    │
│  │  this person              [ OFF ]│    │
│  └──────────────────────────────────┘    │
│                                          │
│  ┌──────────────────────────────────┐    │
│  │          ✓ Allow                 │    │
│  └──────────────────────────────────┘    │
│  ┌──────────────────────────────────┐    │
│  │        ✗ Don't Allow             │    │
│  └──────────────────────────────────┘    │
│                                          │
│  Block this person                       │
│                                          │
│  HISTORY                                 │
│  Sep 12 — Requested phone → Denied       │
│  Aug 3  — Requested email → Approved     │
│                                          │
└──────────────────────────────────────────┘
```

### 4.2 Requester Info Section

| Field | Source | Typography |
|-------|--------|------------|
| Name | Contact display name | `rin.type.title3` |
| Photo | Contact avatar, `AvatarView` size `lg` (56pt) | — |
| Circle membership | All circles this contact belongs to, shown as `CircleDot` chips | `rin.type.callout` |
| Relationship context | How long ago they were added, who added them (import source) | `rin.type.footnote`, `rin.text.secondary` |
| Mutual circles | Count and names of shared circles | `rin.type.footnote` |

### 4.3 Requested Fields Section

Each requested field shown as a row with:
- SF Symbol icon for the field type (e.g., `envelope.fill` for email, `phone.fill` for phone).
- Field label in `rin.type.body`.
- If multiple fields requested in a single batch, all displayed together.

### 4.4 Request Reason

Displayed only if the requester provided a reason. Shown in a quoted block style:
- Background: `rin.bg.tertiary`.
- Text: `rin.type.body`, italic.
- Corner radius: `rin.radius.md`.

If no reason: section omitted entirely (not shown as "No reason provided").

### 4.5 Actions

**Primary actions (mutually exclusive):**

| Action | Button | Behavior |
|--------|--------|----------|
| Allow | `PrimaryButton` (standard) | Grants access to the specific requested field(s). Emits `security.request_approved`. Navigates back to SEC1 with brief success toast. |
| Don't Allow | `SecondaryButton` (standard) | Denies the request. No notification sent to requester per Ask flow spec. Emits `security.request_denied`. Navigates back with brief confirmation. |

**Optional toggle:**

"Allow for all fields from this person" — toggle switch. When enabled and the user taps Allow, creates a per-contact override granting visibility on all current and future fields. Warning text appears below toggle when active: "This person will see all your fields regardless of circle policy."

**Destructive secondary action:**

"Block this person" — text link in `rin.brand.error`. Opens confirmation dialog:
- Title: "Block [Name]?"
- Body: "They won't be able to send you requests or see your profile. You can unblock them later in Settings."
- Actions: "Block" (destructive) / "Cancel".
- Blocking prevents all future Ask requests from this contact. Emits `security.contact_blocked`.

### 4.6 Request History

Displayed only if previous requests from this person exist. Shown as a timeline list:

| Element | Typography |
|---------|------------|
| Date | `rin.type.caption`, `rin.text.tertiary` |
| Description | `rin.type.footnote`: "Requested [field] -> [outcome]" |

Outcomes displayed as colored text: Approved (`rin.brand.secondary`), Denied (`rin.brand.error`), Expired (`rin.text.tertiary`).

Maximum 5 history entries shown. If more: "View all history" link to a paginated list.

### 4.7 States

| State | Behavior |
|-------|----------|
| Pending | Default state, both action buttons enabled |
| Submitting | Selected button shows loading spinner. Other button disabled |
| Approved | Brief success animation (checkmark), auto-navigate back after 1s |
| Denied | Brief confirmation animation, auto-navigate back after 1s |
| Already resolved | If navigated to via stale notification, show "This request has already been [resolved]." with back button |

---

## 5) SEC3: Dispute Detail

### 5.1 Layout

```
┌──────────────────────────────────────────┐
│ ◀ Security      Dispute Detail           │
│──────────────────────────────────────────│
│                                          │
│  ┌──────────────────────────────────┐    │
│  │ CHANNEL OWNERSHIP DISPUTE        │    │
│  │ Status: Under Review             │    │
│  │ Case ID: DSP-2026-0847           │    │
│  └──────────────────────────────────┘    │
│                                          │
│  DISPUTED CHANNEL                        │
│  📞 +1 (555) 012-3456                   │
│  Previously verified by you on Jan 3     │
│                                          │
│  TIMELINE                                │
│  ┌─ ● Feb 12  Case opened              │
│  │    Initiated by: system              │
│  │    Reason: competing claim detected  │
│  │                                      │
│  ├─ ● Feb 12  Evidence requested        │
│  │    Submit proof of ownership         │
│  │    Deadline: Feb 15                  │
│  │                                      │
│  ├─ ● Feb 13  You submitted evidence    │
│  │    OTP verification completed        │
│  │                                      │
│  ├─ ○ Feb 14  Under admin review        │
│  │    Estimated resolution: 48h         │
│  │                                      │
│  └─ ○ Pending resolution                │
│                                          │
│  WHAT'S LIMITED NOW                      │
│  • Channel edits frozen                  │
│  • Username transfer blocked             │
│  • Search visibility reduced             │
│                                          │
│  YOUR ACTIONS                            │
│  ┌──────────────────────────────────┐    │
│  │     Submit Additional Evidence    │    │
│  └──────────────────────────────────┘    │
│  ┌──────────────────────────────────┐    │
│  │     Respond to Questions          │    │
│  └──────────────────────────────────┘    │
│                                          │
└──────────────────────────────────────────┘
```

### 5.2 Dispute Type Header

Card at top displaying:

| Field | Typography | Notes |
|-------|------------|-------|
| Dispute type label | `rin.type.title3`, uppercase | See type mapping below |
| Status | `rin.type.headline` with status badge (same badge style as SEC1) | |
| Case ID | `rin.type.caption`, `rin.text.tertiary` | System-generated, read-only |

**Dispute type mapping** (from DISPUTE_PLAYBOOK_V1.md):

| Case type | User-facing label |
|-----------|-------------------|
| C1 | Channel Ownership Dispute |
| C2 | Channel Reassignment |
| C3 | Identity Merge Dispute |
| C4 | Impersonation Report |
| C5 | Business Authority Dispute |
| C6 | Trust Review |

### 5.3 Disputed Channel Section

Shows the channel(s) under dispute:
- Channel type icon (SF Symbol: `phone.fill`, `envelope.fill`, etc.).
- Channel value (masked for security if dispute involves another party: show last 4 digits for phone, domain for email).
- Verification date: when the user originally verified this channel.

### 5.4 Timeline

Vertical timeline using a connected-dot pattern. Each event node:

| Element | Token | Notes |
|---------|-------|-------|
| Dot (completed) | Filled circle, `rin.brand.primary` | Past events |
| Dot (current) | Filled circle, `rin.brand.warning` with pulse animation | Current step |
| Dot (pending) | Open circle, `rin.border.default` | Future steps |
| Connecting line | 2pt, `rin.border.default` | Between dots |
| Date | `rin.type.caption`, `rin.text.secondary` | Left-aligned |
| Event title | `rin.type.headline` | Right of dot |
| Event description | `rin.type.footnote`, `rin.text.secondary` | Below title |
| Deadline (if any) | `rin.type.footnote`, `rin.brand.error` | Inline with description |

Timeline events sourced from case state machine (DISPUTE_PLAYBOOK_V1.md S4.2):
- `opened` — date, initiator (system/other party), reason.
- `triaged` — severity assignment.
- `awaiting_user` — evidence or response requested, deadline.
- `awaiting_system_hold` — hold period countdown.
- `adjudication` — under admin review, estimated resolution time.
- `resolved` — outcome, what changed.
- `reopened` — if appealed successfully.

### 5.5 Restrictions Summary

"What's limited now" section. Lists the active automatic safeguards applied per DISPUTE_PLAYBOOK_V1.md S6:

- Bulleted list.
- Each item: plain-language description of the restriction.
- Typography: `rin.type.body`.
- No internal evidence or confidence scores exposed (per founder decision S14.3).

Only shown when the dispute is active (not resolved).

### 5.6 User Actions

Available actions depend on the current case state:

| Case state | Available actions |
|------------|-------------------|
| `awaiting_user` | Submit Evidence, Respond to Questions |
| `awaiting_system_hold` | No actions (countdown shown) |
| `adjudication` | No actions (waiting indicator) |
| `resolved` | Appeal Resolution (if within appeal window) |
| `reopened` | Submit Additional Evidence |

**Submit Evidence** — navigates to SEC6 (Evidence Submission).
**Respond to Questions** — navigates to SEC6 with pre-filled question prompts.
**Appeal Resolution** — opens confirmation sheet:
- Title: "Appeal this decision?"
- Body: "Your case will be reopened for review. You can submit additional evidence."
- Actions: "Appeal" / "Cancel".
- Appeal window: 14 days from resolution date. After window closes, action is hidden.

### 5.7 Dispute Status Values

| Status | Meaning |
|--------|---------|
| Open | Case created, initial triage |
| Under Review | Admin or system evaluating evidence |
| Awaiting Your Response | User action needed (evidence, questions) |
| Hold Period | Automatic hold window in effect (countdown visible) |
| Resolved | Final decision rendered |
| Appealed | Appeal submitted, case reopened |

### 5.8 States

| State | Behavior |
|-------|----------|
| Loading | Skeleton for header card + 3 timeline nodes |
| Active dispute | Full layout with timeline and actions |
| Resolved dispute | Timeline completed (all dots filled), actions section shows outcome summary and optional appeal |
| Stale deep link | "This dispute has been closed." with resolution summary and back button |
| Error | `StatusBanner` with retry |

---

## 6) SEC4: Account Alert Detail

### 6.1 Layout

```
┌──────────────────────────────────────────┐
│ ◀ Security      Account Alert            │
│──────────────────────────────────────────│
│                                          │
│         ⚠️                               │
│   New device login detected              │
│                                          │
│  DETAILS                                 │
│  Device       iPhone 17 Pro              │
│  Location     San Jose, CA               │
│  Time         Feb 14, 2026 at 3:42 PM   │
│  IP Address   198.51.100.***             │
│                                          │
│  RECOMMENDED ACTION                      │
│  If this was you, no action needed.      │
│  If this wasn't you, secure your         │
│  account immediately.                    │
│                                          │
│  ┌──────────────────────────────────┐    │
│  │       ✓ This Was Me               │    │
│  └──────────────────────────────────┘    │
│  ┌──────────────────────────────────┐    │
│  │     ✗ This Wasn't Me              │    │
│  └──────────────────────────────────┘    │
│  ┌──────────────────────────────────┐    │
│  │       🔒 Change Password          │    │
│  └──────────────────────────────────┘    │
│                                          │
└──────────────────────────────────────────┘
```

### 6.2 Alert Types

| Alert type | SF Symbol | Description |
|------------|-----------|-------------|
| New device login | `desktopcomputer` | Login detected from unrecognized device |
| Failed login attempts | `lock.trianglebadge.exclamationmark` | Multiple failed authentication attempts |
| Channel verification expiring | `clock.badge.exclamationmark` | Verified phone/email approaching re-verification deadline |
| Suspicious activity | `eye.trianglebadge.exclamationmark` | Unusual patterns: rapid contact exports, abnormal API usage, bulk field access |
| Account recovery initiated | `arrow.triangle.2.circlepath` | Password reset or recovery flow started |

### 6.3 Alert Detail Sections

**Icon and Title:**
- Large SF Symbol icon (48pt), centered, colored by severity:
  - Critical (login, recovery): `rin.brand.error`
  - Warning (suspicious activity, failed attempts): `rin.brand.warning`
  - Info (verification expiring): `rin.brand.primary`
- Title: `rin.type.title2`.

**Details:**
- Key-value table of contextual information.
- Fields vary by alert type:

| Alert type | Detail fields |
|------------|---------------|
| New device login | Device name, location (city/region), timestamp, masked IP |
| Failed login attempts | Attempt count, time range, source location (if available) |
| Channel verification expiring | Channel type + value (masked), expiry date, days remaining |
| Suspicious activity | Activity type, volume/count, time window |
| Account recovery initiated | Recovery method, timestamp, source IP (masked) |

Typography: `rin.type.subheadline` for labels, `rin.type.body` for values.

**Recommended Action:**
- Plain-language guidance text.
- Typography: `rin.type.body`.
- Background: `rin.bg.secondary` card with `rin.radius.lg`.

### 6.4 Actions

Actions vary by alert type:

| Alert type | Actions |
|------------|---------|
| New device login | "This Was Me" (dismiss), "This Wasn't Me" (escalate), "Change Password" |
| Failed login attempts | "This Was Me" (dismiss), "This Wasn't Me" (escalate), "Change Password" |
| Channel verification expiring | "Re-verify Now" (starts verification flow), "Remind Me Later" |
| Suspicious activity | "This Was Me" (dismiss), "This Wasn't Me" (escalate), "Review Activity Log" |
| Account recovery initiated | "This Was Me" (dismiss), "This Wasn't Me" (lock account + escalate) |

**"This Was Me"** — dismisses the alert. Brief confirmation: "Alert dismissed." Emits `security.alert_acknowledged`.

**"This Wasn't Me"** — initiates security review:
1. Confirmation dialog: "We'll secure your account. You may need to re-verify your identity."
2. On confirm: triggers account security review (locks sessions, requires re-authentication). Emits `security.alert_escalated`.
3. Navigates to an in-progress security review state within the same screen.

**"Change Password"** — navigates to password change flow (external to Security Inbox).

**"Re-verify Now"** — navigates to channel verification flow for the expiring channel.

**"Review Activity Log"** — navigates to a read-only list of recent account activity (login timestamps, API access, contact exports). V1 scope: last 30 days.

### 6.5 Severity Levels

Alerts carry a severity that affects visual treatment and notification urgency:

| Severity | Visual | Push behavior |
|----------|--------|---------------|
| Critical | Red icon, red top border on card | Immediate push, sound + banner |
| Warning | Amber icon, amber top border on card | Standard push |
| Info | Blue icon, no colored border | Silent push (badge only) |

### 6.6 States

| State | Behavior |
|-------|----------|
| Unacknowledged | Full detail with action buttons |
| Submitting action | Selected button loading, others disabled |
| Acknowledged (This Was Me) | Checkmark confirmation, fades to resolved |
| Escalated (This Wasn't Me) | Security review in-progress indicator with guidance text |
| Expired (verification) | Channel re-verification deadline passed; alert shows "Verification lapsed" with "Re-verify Now" as sole action |

---

## 7) SEC5: Report Status

### 7.1 Layout

```
┌──────────────────────────────────────────┐
│ ◀ Security        My Reports             │
│──────────────────────────────────────────│
│                                          │
│  ┌──────────────────────────────────┐    │
│  │     + File New Report             │    │
│  └──────────────────────────────────┘    │
│                                          │
│  YOUR REPORTS                            │
│ ┌──────────────────────────────────────┐ │
│ │ 🛡  fake_account_23                  │ │
│ │    Reason: Impersonation             │ │
│ │    Filed: Feb 11, 2026               │ │
│ │    Status: Under Review              │ │
│ ├──────────────────────────────────────┤ │
│ │ 🛡  spam_bot_99                      │ │
│ │    Reason: Spam                      │ │
│ │    Filed: Jan 28, 2026               │ │
│ │    Status: Action Taken              │ │
│ ├──────────────────────────────────────┤ │
│ │ 🛡  john.suspicious                  │ │
│ │    Reason: Harassment                │ │
│ │    Filed: Jan 15, 2026               │ │
│ │    Status: Dismissed                 │ │
│ └──────────────────────────────────────┘ │
│                                          │
│  Reports are reviewed by our trust and   │
│  safety team. For privacy, we can't      │
│  share specific actions taken against     │
│  reported accounts.                      │
│                                          │
└──────────────────────────────────────────┘
```

### 7.2 Report List

Each report row:

| Element | Typography | Notes |
|---------|------------|-------|
| Target profile name/identifier | `rin.type.headline` | Display name or username of the reported profile |
| Report reason | `rin.type.footnote`, `rin.text.secondary` | Category from report taxonomy |
| Date filed | `rin.type.footnote`, `rin.text.tertiary` | Absolute date format |
| Status badge | Same pill style as SEC1 | See status values below |

**Report status values:**

| Status | Badge color | Meaning |
|--------|-------------|---------|
| Pending | `rin.brand.warning` | Report received, not yet reviewed |
| Under Review | `rin.brand.primary` | Actively being evaluated |
| Action Taken | `rin.brand.secondary` | Enforcement action applied (no details disclosed) |
| Dismissed | `rin.text.tertiary` | Report reviewed, no action warranted |

Per privacy policy: no details about specific actions taken against the reported user are ever disclosed. A brief explanation is shown as footer text below the list.

### 7.3 Report Reason Taxonomy

| Reason | Description |
|--------|-------------|
| Spam | Unwanted bulk messaging or contact requests |
| Harassment | Abusive, threatening, or intimidating behavior |
| Impersonation | Profile falsely representing another person or business |
| Fake Account | Profile does not represent a real person or entity |
| Inappropriate Content | Offensive profile content (photo, bio, name) |
| Other | Free-text reason provided by reporter |

### 7.4 File New Report

"File New Report" button at top. Navigates to SEC7 (report filing flow). Also accessible from:
- Contact detail screen context menu ("Report this contact").
- Profile view context menu ("Report this profile").

When launched from SEC5 (no pre-selected target), the flow begins with a contact/profile search step.

### 7.5 Tapping a Report Row

Opens a detail view showing:
- All fields from the list row (target, reason, date, status).
- If the user provided additional details at filing time, those are shown.
- No additional information about the review outcome or enforcement.
- If Dismissed: a brief generic explanation: "Our team reviewed this report and determined it did not violate our guidelines."

### 7.6 States

| State | Behavior |
|-------|----------|
| Loading | Skeleton rows for 3 items |
| Reports present | Full list with CTA at top |
| No reports | Empty state: "You haven't filed any reports." with "File New Report" CTA |
| Error | `StatusBanner` with retry |

---

## 8) SEC6: Evidence Submission

Presented as a sheet (half-screen detent, expandable to full) from SEC3.

### 8.1 Layout

```
┌──────────────────────────────────────────┐
│           Submit Evidence                 │
│──────────────────────────────────────────│
│                                          │
│  Case: DSP-2026-0847                     │
│  Channel: +1 (555) 012-3456             │
│                                          │
│  EVIDENCE TYPE                           │
│  ( ) OTP Verification                    │
│  ( ) Screenshot / Document               │
│  ( ) Written Statement                   │
│                                          │
│  ┌──────────────────────────────────┐    │
│  │  [Evidence content area]          │    │
│  │  (changes by type selection)      │    │
│  └──────────────────────────────────┘    │
│                                          │
│  ┌──────────────────────────────────┐    │
│  │          Submit                    │    │
│  └──────────────────────────────────┘    │
│                                          │
└──────────────────────────────────────────┘
```

### 8.2 Evidence Types

| Type | Content area |
|------|-------------|
| OTP Verification | "We'll send a code to this channel. Enter it below to prove ownership." Triggers OTP flow inline. |
| Screenshot / Document | Photo picker (camera + library). Max 5 attachments. Accepted formats: JPEG, PNG, PDF. Max 10 MB per file. |
| Written Statement | Multi-line text field. Max 2000 characters. Placeholder: "Describe your relationship to this channel and any additional context." |

### 8.3 States

| State | Behavior |
|-------|----------|
| Selecting type | Radio buttons, content area updates on selection |
| Filling evidence | Content area active |
| Submitting | Submit button shows spinner. Content area read-only |
| Success | Checkmark animation. Dismiss sheet. SEC3 timeline updates with new "Evidence submitted" node |
| Validation error | Inline error below content area (e.g., "File too large", "Statement required") |
| Network error | Inline error with retry option |

---

## 9) SEC7: File New Report

Presented as a full-screen sheet with its own `NavigationStack`.

### 9.1 Steps

1. **Select target** — Search bar to find a contact or profile to report. If launched from a contact/profile context menu, this step is pre-filled and skipped.
2. **Select reason** — List of reasons from S7.3 taxonomy. Tap to select.
3. **Additional details** — Optional text field (max 2000 chars). "Provide any additional context."
4. **Review and submit** — Summary of target, reason, and details. "Submit Report" button.

### 9.2 States

| State | Behavior |
|-------|----------|
| Step navigation | Step indicator at top (4 steps). Back button to previous step. |
| Submitting | Submit button loading. All fields read-only. |
| Success | Confirmation screen: "Report submitted. We'll review it and update you here." with "Done" button returning to SEC5. |
| Error | Inline error with retry on submit step. |

---

## 10) Navigation Map

```
SEC1 Security Inbox Root
├── SEC2 Access Request Detail
├── SEC3 Dispute Detail
│   └── SEC6 Evidence Submission (sheet)
├── SEC4 Account Alert Detail
│   ├── Change Password (RinSettings)
│   ├── Channel Re-verification (RinSecurity)
│   └── Activity Log (RinSecurity)
├── SEC5 Report Status
│   ├── SEC7 File New Report (full-screen sheet)
│   └── Report Detail (inline)
└── Filter views (inline, not separate screens)
```

Integration with Profile tab navigation:

```
P1 Profile Home
├── ...
├── Security Inbox (SEC1) ← "Security Inbox" in Quick Actions
│   └── (full SEC1-SEC7 tree above)
└── ...
```

---

## 11) Deep Link Routing

| Deep link | Destination | Behavior |
|-----------|-------------|----------|
| `rin://security` | SEC1 | Open Security Inbox Root. Switch to Profile tab if needed. |
| `rin://security?tab=requests` | SEC1 | Open SEC1, scroll to ACCESS REQUESTS section |
| `rin://security?tab=requests&id={requestId}` | SEC2 | Push SEC1 then SEC2 for the specified request. If request not found, show SEC1 with error toast. |
| `rin://security/dispute/{id}` | SEC3 | Push SEC1 then SEC3 for the specified dispute. If dispute not found, show SEC1 with error toast. |
| `rin://security?tab=alerts` | SEC1 | Open SEC1, scroll to ACCOUNT ALERTS section |
| `rin://security?tab=alerts&id={alertId}` | SEC4 | Push SEC1 then SEC4 for the specified alert. If alert not found, show SEC1 with error toast. |
| `rin://security?tab=reports` | SEC1 | Open SEC1, scroll to REPORTS section |

Routing behavior:
1. `AppCoordinator.handleDeepLink(url:)` parses the URL.
2. Switches to Profile tab.
3. Pushes SEC1 onto the `profilePath` NavigationStack.
4. If a sub-route is specified, pushes the detail screen onto the stack.
5. If the target item is not found (stale notification), show SEC1 with inline toast: "This item is no longer available."

---

## 12) Empty States

### 12.1 Inbox Completely Empty

```
┌──────────────────────────────────────────┐
│ ◀ Profile        Security (0)            │
│──────────────────────────────────────────│
│                                          │
│                                          │
│              🛡️                          │
│                                          │
│         All clear.                       │
│   No security items need                 │
│       your attention.                    │
│                                          │
│                                          │
└──────────────────────────────────────────┘
```

Uses `EmptyStateView` component:
- Icon: SF Symbol `shield.checkmark`, size 64pt, color `rin.brand.secondary`.
- Title: "All clear." in `rin.type.title2`.
- Subtitle: "No security items need your attention." in `rin.type.body`, `rin.text.secondary`.
- No CTA button (nothing for the user to do).

### 12.2 Empty Within a Category

Inline within the section: "No [access request / dispute / alert / report] items" in `rin.type.footnote`, `rin.text.tertiary`.

### 12.3 Empty Filter Result

When a filter tab yields no items:
- `EmptyStateView` variant:
  - Icon: SF Symbol `line.3.horizontal.decrease.circle`, size 48pt, `rin.text.tertiary`.
  - Title: "No items match this filter."
  - Subtitle: none.
  - CTA: "Show All" button that resets filter to "All".

---

## 13) Tab Badge Integration

### 13.1 Profile Tab Badge

The Profile tab badge count includes unresolved security inbox items, as defined in `IOS_NAVIGATION_STATE_V1.md` S6:

| Source | Counts toward badge |
|--------|--------------------|
| Pending access requests (Action Needed) | Yes |
| Active disputes awaiting user response | Yes |
| Unacknowledged account alerts | Yes |
| Reports with status updates since last view | Yes (once, until viewed) |

Badge uses the `TabBadge` component (numeric variant). Badge appears on the Profile tab in the main tab bar.

### 13.2 Badge Clearing

- Opening SEC1 clears the badge for report status updates (viewed).
- Acknowledging an alert (any action on SEC4) clears that alert from the badge count.
- Resolving an access request (Allow or Don't Allow on SEC2) clears that request from the badge count.
- A dispute clears from the badge count only when it no longer requires user action (case state leaves `awaiting_user`).

### 13.3 Badge Update Sources

Badge count is updated via:
- Push notification payload (server-sent count).
- Pull-to-refresh on SEC1.
- Background app refresh (periodic sync).
- Real-time event via `NotificationService` shared state (see `IOS_NAVIGATION_STATE_V1.md` S4.2).

---

## 14) Push Notification Deep Links

Extends the push notification deep link table from `IOS_NAVIGATION_STATE_V1.md` S3.4:

| Notification type | Deep link | Notification body example |
|-------------------|-----------|---------------------------|
| New access request | `rin://security?tab=requests&id={requestId}` | "[Name] requested your [field]." |
| Access request reminder (48h) | `rin://security?tab=requests&id={requestId}` | "Reminder: [Name] is waiting for access to your [field]." |
| Dispute opened | `rin://security/dispute/{id}` | "A dispute has been opened on your [channel type]." |
| Dispute status change | `rin://security/dispute/{id}` | "Your dispute DSP-[id] has been updated." |
| Dispute resolution | `rin://security/dispute/{id}` | "Your dispute has been resolved. Tap to see the outcome." |
| New device login | `rin://security?tab=alerts&id={alertId}` | "New login from [device] in [location]." |
| Failed login attempts | `rin://security?tab=alerts&id={alertId}` | "Multiple failed login attempts detected on your account." |
| Verification expiring | `rin://security?tab=alerts&id={alertId}` | "Your [channel] verification expires in [N] days." |
| Suspicious activity | `rin://security?tab=alerts&id={alertId}` | "Unusual activity detected on your account." |
| Account recovery | `rin://security?tab=alerts&id={alertId}` | "An account recovery was initiated. Was this you?" |
| Report status update | `rin://security?tab=reports` | "Your report has been reviewed." |

All push notifications for Security Inbox items include:
- `category`: `security` (for notification actions).
- `thread-id`: grouped by security category for notification center stacking.
- `interruption-level`: Critical alerts use `.timeSensitive`. Info alerts use `.active`.

---

## 15) Events

### 15.1 Screen-Level Events

| Event | Trigger | Payload |
|-------|---------|---------|
| `security.inbox_viewed` | SEC1 loads | `filter` (all/action_needed/resolved), `item_count`, `profile_id` |
| `security.inbox_filtered` | User changes filter tab | `filter`, `result_count` |
| `security.category_expanded` | User taps section chevron | `category` |

### 15.2 Access Request Events

| Event | Trigger | Payload |
|-------|---------|---------|
| `security.request_viewed` | SEC2 loads | `request_id`, `requester_id`, `fields_requested` |
| `security.request_approved` | User taps Allow | `request_id`, `requester_id`, `fields_granted`, `all_fields_toggle` |
| `security.request_denied` | User taps Don't Allow | `request_id`, `requester_id`, `fields_denied` |
| `security.contact_blocked` | User blocks requester | `request_id`, `blocked_contact_id` |

### 15.3 Dispute Events

| Event | Trigger | Payload |
|-------|---------|---------|
| `security.dispute_viewed` | SEC3 loads | `case_id`, `case_type`, `case_state` |
| `security.evidence_submitted` | Evidence submission completes | `case_id`, `evidence_type` |
| `security.dispute_appealed` | User taps Appeal | `case_id` |
| `security.question_responded` | User submits response to dispute questions | `case_id` |

### 15.4 Alert Events

| Event | Trigger | Payload |
|-------|---------|---------|
| `security.alert_viewed` | SEC4 loads | `alert_id`, `alert_type`, `severity` |
| `security.alert_acknowledged` | User taps "This Was Me" | `alert_id`, `alert_type` |
| `security.alert_escalated` | User taps "This Wasn't Me" | `alert_id`, `alert_type` |
| `security.password_change_initiated` | User taps "Change Password" | `alert_id` (if originated from alert) |
| `security.reverification_initiated` | User taps "Re-verify Now" | `alert_id`, `channel_type` |

### 15.5 Report Events

| Event | Trigger | Payload |
|-------|---------|---------|
| `security.report_viewed` | SEC5 loads | `report_count` |
| `security.report_detail_viewed` | User taps report row | `report_id`, `report_status` |
| `security.report_filed` | Report submission completes (SEC7) | `report_id`, `target_profile_id`, `reason` |

---

## 16) Accessibility

### 16.1 VoiceOver

**SEC1 (Inbox Root):**
- Filter tabs announced as: "Filter: [tab name], [position] of 3. [Selected/Not selected]."
- Section headers announced as: "[Category name], [count] items."
- Item rows announced as: "[Title]. [Subtitle]. [Status]. [Timestamp]."
- Status badges include semantic role: "Status: [value]."

**SEC2 (Access Request Detail):**
- Requester photo announced as: "Photo of [name]."
- Action buttons include semantic result description: "Allow. Grants [name] access to [fields]."
- Block action announced with destructive trait: "Block this person. Destructive action."
- History section announced as: "Request history. [count] previous requests."

**SEC3 (Dispute Detail):**
- Timeline nodes announced sequentially: "Step [N] of [total]. [Date]. [Event title]. [Description]. [Status: complete/current/pending]."
- Deadline text includes urgency: "Deadline: [date]. [N] days remaining."
- Restrictions section: "Current limitations. [count] restrictions active."

**SEC4 (Account Alert Detail):**
- Alert icon includes severity in announcement: "[Severity] alert. [Alert type]."
- "This Wasn't Me" button includes consequence description: "This wasn't me. Initiates account security review."
- Severity maps to VoiceOver priority: Critical alerts use `.announcement` posting for immediate reading.

**SEC5 (Report Status):**
- Report rows: "[Target name]. Reason: [reason]. Filed: [date]. Status: [status]."
- Privacy footer text read as part of the list container's accessibility description.

### 16.2 Dynamic Type

All screens support Dynamic Type through `AX5` size:
- Layouts reflow from horizontal to vertical when text exceeds available width.
- Status badges wrap below timestamps at large sizes.
- Timeline dots and connecting lines scale with text.
- Action buttons remain full-width and stack vertically.

### 16.3 Semantic Urgency

Account alerts carry semantic urgency levels that map to iOS `AccessibilityNotification`:

| Urgency | VoiceOver behavior | Haptic |
|---------|-------------------|--------|
| Critical | Posted as `.announcement` (interrupts current speech) | `.warning` feedback on screen load |
| Warning | Standard reading order, but placed first in focus order | `.notification` feedback |
| Info | Standard reading order | None |

### 16.4 Color Independence

All status information is conveyed through both color and text label. Status badges always include the text value (never color-only). Timeline dot state is conveyed through filled vs. open shape in addition to color.

### 16.5 Reduce Motion

When "Reduce Motion" is enabled:
- Timeline pulse animation on current step is replaced with a static bold border.
- Success/confirmation animations replaced with instant state change.
- Sheet presentations use cross-dissolve instead of slide.

---

## 17) Error Handling

| Error scenario | User-facing behavior |
|----------------|---------------------|
| Network timeout on SEC1 load | Show cached items (if any) with `StatusBanner` (offline). If no cache: full-screen error with retry. |
| Access request action fails | Inline error below buttons: "Couldn't complete this action. Try again." Buttons re-enabled. |
| Evidence upload fails | Inline error in SEC6: "Upload failed. Check your connection and try again." Retry button. |
| Dispute detail fails to load | `StatusBanner` (error) with retry. Back button available. |
| Report submission fails | Stay on review step. Inline error with retry. User input preserved. |
| Stale item (deleted server-side) | Toast on SEC1: "This item is no longer available." Navigate back if on detail screen. |
| Rate limited (too many actions) | Inline warning: "Too many actions. Please wait a moment and try again." |

---

## 18) Performance Targets

| Metric | Target |
|--------|--------|
| SEC1 initial load (cached) | < 200ms |
| SEC1 initial load (network) | < 1s |
| SEC2/SEC3/SEC4 detail load | < 500ms |
| Action response (Allow/Deny/Acknowledge) | < 1s server round-trip |
| Evidence upload (per file) | < 5s for 10 MB file |
| Pull-to-refresh | < 2s full refresh |
| Badge count update after action | < 500ms (optimistic local update, server confirmation async) |

---

## 19) Data Model Summary

Conceptual models backing the Security Inbox screens:

```
SecurityItem (abstract)
├── AccessRequest
│   ├── id: UUID
│   ├── requesterId: UUID
│   ├── fields: [FieldType]
│   ├── reason: String?
│   ├── status: pending | approved | denied
│   ├── createdAt: Date
│   └── resolvedAt: Date?
│
├── DisputeCase
│   ├── id: String (DSP-YYYY-NNNN)
│   ├── caseType: C1 | C2 | C3 | C4 | C5 | C6
│   ├── channelId: UUID
│   ├── state: opened | triaged | awaiting_user | awaiting_system_hold | adjudication | resolved | reopened
│   ├── severity: L1 | L2 | L3
│   ├── timeline: [DisputeEvent]
│   ├── restrictions: [Restriction]
│   ├── createdAt: Date
│   └── resolvedAt: Date?
│
├── AccountAlert
│   ├── id: UUID
│   ├── alertType: new_device | failed_login | verification_expiring | suspicious_activity | recovery_initiated
│   ├── severity: critical | warning | info
│   ├── details: [String: String]
│   ├── acknowledged: Bool
│   ├── createdAt: Date
│   └── acknowledgedAt: Date?
│
└── AbuseReport
    ├── id: UUID
    ├── targetProfileId: UUID
    ├── reason: spam | harassment | impersonation | fake_account | inappropriate_content | other
    ├── details: String?
    ├── status: pending | under_review | action_taken | dismissed
    ├── createdAt: Date
    └── updatedAt: Date?
```

---

## 20) Cross-References

| Topic | Document | Section |
|-------|----------|---------|
| Ask flow lifecycle | `docs/product/CIRCLE_MANAGEMENT_UX_V1.md` | S3.3 |
| C5 Access Request Detail (Circles tab) | `docs/product/IOS_PROFILE_CIRCLE_SCREEN_SPEC_V1.md` | S3 C5 |
| Dispute case types and state machines | `docs/operations/DISPUTE_PLAYBOOK_V1.md` | S3, S4 |
| Dispute resolution workflows | `docs/operations/DISPUTE_PLAYBOOK_V1.md` | S5 |
| Automatic safeguards by severity | `docs/operations/DISPUTE_PLAYBOOK_V1.md` | S6 |
| Dispute UX blueprint | `docs/operations/DISPUTE_PLAYBOOK_V1.md` | S8 |
| Dispute event contracts | `docs/operations/DISPUTE_PLAYBOOK_V1.md` | S10 |
| Abuse rollup and shadow restrictions | `docs/product/SHADOW_PROFILE_UX_V1.md` | S9 |
| Class-specific security controls | `docs/architecture/PROFILE_CLASS_CONTRACT_V1.md` | S9 |
| Deep link URL scheme | `docs/architecture/IOS_NAVIGATION_STATE_V1.md` | S3.1 |
| Push notification deep links | `docs/architecture/IOS_NAVIGATION_STATE_V1.md` | S3.4 |
| Tab badge management | `docs/architecture/IOS_NAVIGATION_STATE_V1.md` | S6 |
| Coordinator and navigation model | `docs/architecture/IOS_NAVIGATION_STATE_V1.md` | S2 |
| Color tokens and typography | `docs/design/IOS_DESIGN_TOKENS_V1.md` | S2, S3 |
| Component inventory | `docs/design/IOS_DESIGN_TOKENS_V1.md` | S6 |
| Hold windows (founder decision) | `docs/operations/DISPUTE_PLAYBOOK_V1.md` | S14.1 |
| User transparency policy (founder decision) | `docs/operations/DISPUTE_PLAYBOOK_V1.md` | S14.3 |

---

## 21) Open Decisions

1. **SEC2 + C5 unification** — The Access Request Detail screen exists both in the Circles tab (C5) and the Security Inbox (SEC2). Should they be the same SwiftUI view parameterized by context, or two distinct screens? Sharing a view reduces code but couples Circles and Security coordinators.

2. **Dispute real-time updates** — Should SEC3 use a WebSocket/SSE connection for live timeline updates while the user is viewing an active dispute, or rely on pull-to-refresh? Real-time improves UX during hold-period countdowns but adds infrastructure cost.

3. **Alert auto-dismiss threshold** — Should account alerts auto-resolve after a configurable period (e.g., 30 days with no action) to prevent inbox clutter, or persist indefinitely until explicitly acknowledged? Auto-dismiss risks missing a genuine threat; persistence risks alert fatigue.

4. **Security Inbox scope for shadow profiles** — When a shadow profile is active, should the Security Inbox show only items relevant to that shadow, or always show all items across the principal's identity? Shadow profiles cannot own channels or initiate disputes, so most items apply to the primary. Showing all items may break the identity separation mental model.

5. **Batch actions on access requests** — Should SEC1 support multi-select on access requests for batch Allow/Deny (e.g., "Allow all 5 pending requests"), or require individual review of each? Batch reduces friction for users with many requests but increases risk of accidental over-sharing.
