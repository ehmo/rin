# iOS Settings Screen Spec V1

## 1) Purpose

Screen-level specification for the Settings hub. Defines every screen, component, state, and transition for account management, privacy controls, notification preferences, support, and account lifecycle (including deletion).

Settings is the central administrative surface for the app. It is intentionally separated from the Profile tab to keep daily-use screens (profile editing, circle management, shadow switching) uncluttered, while giving users clear access to account-level controls.

Companion docs:
- `docs/design/IOS_KEY_SCREEN_WIREFRAMES_V1.md` (Section 11 wireframe)
- `docs/product/IOS_PROFILE_CIRCLE_SCREEN_SPEC_V1.md` (P1 Profile Home -> Settings)
- `docs/product/CIRCLE_MANAGEMENT_UX_V1.md` (default access controls, circle taxonomy)
- `docs/architecture/IOS_NAVIGATION_STATE_V1.md` (deep link: `rin://settings`)
- `docs/architecture/DATA_RETENTION_DELETION_V1.md` (data export, deletion policies)
- `docs/plan/IAP_SUBSCRIPTION_COMPLIANCE_V1.md` (subscription management)
- `docs/design/IOS_DESIGN_TOKENS_V1.md` (tokens and components)

---

## 2) Settings Navigation Map

```
SET1 Settings Root
├── Verified Channels (SET8)
│   └── Add Channel (OTP / email verification)
├── Subscription Management (SET9)
│   └── Paywall (RinPremium)
├── SET2 Default Access Controls
├── SET3 Blocked Users
├── SET4 Export My Data
├── SET5 Send Feedback
├── SET6 Help & FAQ
│   └── Contact Support
├── Sign Out (confirmation dialog)
└── SET7 Delete Account (multi-step flow)
```

Deep link: `rin://settings` navigates to SET1 via ProfileCoordinator.

---

## 3) SET1: Settings Root

### Layout

Standard grouped `List` with inset style (`InsetGroupedListStyle`). Sections are visually separated by `rin.bg.secondary` section backgrounds against `rin.bg.primary` screen background.

```
┌──────────────────────────────────────┐
│ ◀ Profile          Settings          │
├──────────────────────────────────────┤
│                                      │
│ ACCOUNT                              │
│ ┌──────────────────────────────────┐ │
│ │ Phone   +1 (555) 000-0000   [>] │ │
│ │ Email   john@email.com       [>] │ │
│ │ Plan    Free                 [>] │ │
│ └──────────────────────────────────┘ │
│                                      │
│ PRIVACY                              │
│ ┌──────────────────────────────────┐ │
│ │ Default Access Controls      [>] │ │
│ │ Blocked Users           (0)  [>] │ │
│ │ Export My Data               [>] │ │
│ └──────────────────────────────────┘ │
│                                      │
│ NOTIFICATIONS                        │
│ ┌──────────────────────────────────┐ │
│ │ Score Updates           [====○] │ │
│ │ Dedup Suggestions       [====○] │ │
│ │ Enrichment Alerts  🔒   [====○] │ │
│ │ Access Requests         [====○] │ │
│ │ Marketing               [○====] │ │
│ └──────────────────────────────────┘ │
│                                      │
│ SUPPORT                              │
│ ┌──────────────────────────────────┐ │
│ │ Send Feedback                [>] │ │
│ │ Help & FAQ                   [>] │ │
│ │ Rate Rin                     [>] │ │
│ └──────────────────────────────────┘ │
│                                      │
│ DANGER ZONE                          │
│ ┌──────────────────────────────────┐ │
│ │ Sign Out                         │ │
│ │ Delete Account           [🔴>]  │ │
│ └──────────────────────────────────┘ │
│                                      │
│        Rin v1.0.0 (build 42)        │
│                                      │
└──────────────────────────────────────┘

[====○] = toggle ON (tinted rin.brand.primary)
[○====] = toggle OFF
🔒 = Premium-only indicator
🔴 = destructive indicator
```

### Section: ACCOUNT

| Row | Left label | Right detail | Tap action |
|-----|-----------|-------------|------------|
| Phone | "Phone" | Primary phone number, masked middle digits: `+1 (555) ***-0000` | Push → SET8 (Verified Channels) |
| Email | "Email" | Primary email, truncated if long: `john@ema...` | Push → SET8 (Verified Channels) |
| Plan | "Plan" | "Free" or "Premium" with expiry: `Premium (renews Mar 12)` | Push → SET9 (Subscription Management) |

- Phone and Email rows show the primary verified channel only.
- If no email is verified, Email row shows "Not set" in `rin.text.tertiary`.
- Plan row shows a premium badge icon (`rin.brand.accent` star) if subscribed.

### Section: PRIVACY

| Row | Label | Right detail | Tap action |
|-----|-------|-------------|------------|
| Default Access Controls | "Default Access Controls" | Chevron | Push → SET2 |
| Blocked Users | "Blocked Users" | Count badge `(N)` or none if 0 | Push → SET3 |
| Export My Data | "Export My Data" | Chevron | Push → SET4 |

### Section: NOTIFICATIONS

Each row is a standard toggle (`Toggle` with `SwitchToggleStyle`).

| Row | Label | Default | Notes |
|-----|-------|---------|-------|
| Score Updates | "Score Updates" | ON | Daily score change push notifications |
| Dedup Suggestions | "Dedup Suggestions" | ON | New duplicate detected push notifications |
| Enrichment Alerts | "Enrichment Alerts" | OFF | Premium-only. Shows lock icon and "Premium" subtitle if free user. Toggle disabled for free users; tapping row opens paywall |
| Access Requests | "Access Requests" | ON | Someone used Ask flow to request a field |
| Marketing | "Promotional" | OFF | Marketing and promotional messages |

Toggle state is persisted to `UserDefaults` and synced to server via `NotificationPreferenceService`.

When a free user taps the Enrichment Alerts row, present the paywall sheet (same as `rin://premium` deep link). If the user subscribes, toggle becomes enabled and defaults to ON.

### Section: SUPPORT

| Row | Label | Tap action |
|-----|-------|------------|
| Send Feedback | "Send Feedback" | Push → SET5 |
| Help & FAQ | "Help & FAQ" | Push → SET6 |
| Rate Rin | "Rate Rin" | Open `SKStoreReviewController.requestReview()` if available; fallback deep link to App Store page |

### Section: DANGER ZONE

Section header text uses `rin.brand.error` color.

| Row | Label | Style | Tap action |
|-----|-------|-------|------------|
| Sign Out | "Sign Out" | Standard text color | Present `.confirmationDialog` |
| Delete Account | "Delete Account" | `rin.brand.error` text + destructive indicator | Push → SET7 |

**Sign Out Confirmation Dialog:**

```
┌──────────────────────────────────────┐
│                                      │
│         Sign out of Rin?             │
│                                      │
│  You can sign back in anytime with   │
│  your verified phone number.         │
│                                      │
│  ┌──────────────────────────────────┐│
│  │           Sign Out               ││  ← destructive style
│  ├──────────────────────────────────┤│
│  │           Cancel                 ││
│  └──────────────────────────────────┘│
│                                      │
└──────────────────────────────────────┘
```

On "Sign Out":
1. Call `AuthService.signOut()`.
2. Clear session tokens from Keychain.
3. Clear `UserDefaults` preferences (retain only onboarding-complete flag for smoother re-login).
4. Reset all coordinators to root.
5. Present onboarding/login screen (`rin://onboarding`).

### Footer

Centered, `rin.type.footnote`, `rin.text.tertiary`:
```
Rin v{CFBundleShortVersionString} (build {CFBundleVersion})
```

Dynamic: reads from `Bundle.main.infoDictionary`.

### States

| State | Behavior |
|-------|----------|
| Default | All sections visible, toggles reflect persisted preferences |
| Loading preferences | Skeleton shimmer on toggle states until preferences load |
| Offline | Toggles disabled with "Offline" badge; read-only mode |
| Premium active | Enrichment Alerts toggle enabled, Plan row shows "Premium" |
| Free user | Enrichment Alerts toggle disabled with lock icon and "Premium" label |

---

## 4) SET2: Default Access Controls

### Purpose

Global baseline visibility defaults applied to the "Contacts" circle. When a new contact is added and placed only in the Contacts circle, these defaults determine what they can see. This is the same access control matrix as P5 (Field-Level Access Matrix) from the profile spec, but scoped to system-wide defaults rather than per-circle overrides.

### Layout

```
┌──────────────────────────────────────┐
│ ◀ Settings    Default Access         │
├──────────────────────────────────────┤
│                                      │
│ These defaults apply to anyone in    │
│ your Contacts circle. You can        │
│ override per-circle or per-contact.  │
│                                      │
│ PERSONAL INFO                        │
│ ┌──────────────────────────────────┐ │
│ │ Display Name                     │ │
│ │   ○ Allow   ● Don't   ○ Ask     │ │
│ │ ──────────────────────────────── │ │
│ │ Photo                            │ │
│ │   ● Allow   ○ Don't   ○ Ask     │ │
│ │ ──────────────────────────────── │ │
│ │ Bio                              │ │
│ │   ○ Allow   ● Don't   ○ Ask     │ │
│ │ ──────────────────────────────── │ │
│ │ Birthday                         │ │
│ │   ○ Allow   ○ Don't   ● Ask     │ │
│ └──────────────────────────────────┘ │
│                                      │
│ CONTACT INFO                         │
│ ┌──────────────────────────────────┐ │
│ │ Phone                            │ │
│ │   ○ Allow   ● Don't   ○ Ask     │ │
│ │ ──────────────────────────────── │ │
│ │ Email                            │ │
│ │   ○ Allow   ● Don't   ○ Ask     │ │
│ │ ──────────────────────────────── │ │
│ │ Address                          │ │
│ │   ○ Allow   ○ Don't   ● Ask     │ │
│ └──────────────────────────────────┘ │
│                                      │
│ SOCIAL ACCOUNTS                      │
│ ┌──────────────────────────────────┐ │
│ │ LinkedIn                         │ │
│ │   ○ Allow   ● Don't   ○ Ask     │ │
│ │ ──────────────────────────────── │ │
│ │ X (Twitter)                      │ │
│ │   ○ Allow   ● Don't   ○ Ask     │ │
│ │ ──────────────────────────────── │ │
│ │ WhatsApp                         │ │
│ │   ○ Allow   ● Don't   ○ Ask     │ │
│ └──────────────────────────────────┘ │
│                                      │
│       [Reset to Defaults]            │
│                                      │
└──────────────────────────────────────┘

● = selected state
○ = unselected state
```

### Field List

Fields correspond to all user-editable profile fields. Grouped into sections:

| Section | Fields |
|---------|--------|
| Personal Info | Display Name, Photo, Bio, Birthday |
| Contact Info | Phone (each number individually if multiple), Email (each address individually), Address |
| Social Accounts | LinkedIn, X (Twitter), WhatsApp, and any future user-added social channels |

### Three-State Toggle

Each field row uses a segmented control or `AccessStateToggle` component (from RinUI) with three states:

| State | Visual | Meaning |
|-------|--------|---------|
| Allow | Green checkmark / filled segment | Field visible immediately |
| Don't Allow | Red X / filled segment | Field completely hidden |
| Ask | Amber question mark / filled segment | Field shows "Request" button to viewer |

### Initial Defaults

Match the Contacts circle defaults from CIRCLE_MANAGEMENT_UX_V1.md Section 3.4:

| Field | Default |
|-------|---------|
| Display Name | Allow |
| All other fields | Don't Allow |

### Propagation Rules

- Changes here update the global default for the Contacts circle.
- Existing contacts already in Contacts circle are NOT retroactively changed (prevents accidental exposure).
- Only newly added contacts receive the updated defaults.
- Banner at top explains this: "Changes apply to future contacts only. To update existing contacts, edit per-circle controls."

### "Reset to Defaults" Button

- `SecondaryButton` style, centered below all sections.
- Tapping shows confirmation: "Reset all defaults to their original values? This won't affect existing contacts."
- On confirm: all fields reset to initial defaults (Name: Allow, all else: Don't Allow).

### States

| State | Behavior |
|-------|----------|
| Default | All fields shown with current values |
| Modified (unsaved) | Nav bar shows "Save" button; back navigation triggers unsaved-changes alert |
| Saving | "Save" button shows loading spinner |
| Save failed | Inline error banner: "Couldn't save. Check your connection and try again." with retry |
| Offline | Read-only mode, toggles disabled, "Offline" banner |

---

## 5) SET3: Blocked Users

### Purpose

View and manage the list of users the current user has blocked. Blocking prevents the blocked person from viewing any of the blocker's profiles, searching for them, or sending access requests.

### Layout

```
┌──────────────────────────────────────┐
│ ◀ Settings       Blocked Users       │
├──────────────────────────────────────┤
│ [🔍 Search blocked users...       ] │
├──────────────────────────────────────┤
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ [📷] Alex Thompson               │ │
│ │      Blocked Jan 15, 2026        │ │
│ │                          ← swipe │ │
│ └──────────────────────────────────┘ │
│ ┌──────────────────────────────────┐ │
│ │ [📷] Jamie Lee                   │ │
│ │      Blocked Dec 3, 2025         │ │
│ └──────────────────────────────────┘ │
│ ┌──────────────────────────────────┐ │
│ │ [📷] Chris Morgan                │ │
│ │      Blocked Nov 20, 2025        │ │
│ └──────────────────────────────────┘ │
│                                      │
└──────────────────────────────────────┘


SWIPE-TO-UNBLOCK:
┌──────────────────────────────────────┐
│ │ [📷] Alex Thompson     [Unblock] │ │
│ │      Blocked Jan 15    ← red bg  │ │
└──────────────────────────────────────┘


EMPTY STATE:
┌──────────────────────────────────────┐
│ ◀ Settings       Blocked Users       │
├──────────────────────────────────────┤
│                                      │
│                                      │
│            🚫                        │
│                                      │
│      No blocked users                │
│                                      │
│   You haven't blocked anyone.        │
│   Block someone from their profile   │
│   to prevent them from seeing your   │
│   information.                       │
│                                      │
│                                      │
└──────────────────────────────────────┘
```

### Row Structure

Each row contains:
- `AvatarView` (size: `md`, 40pt) with the blocked user's photo (or default avatar if deleted/unavailable).
- Display name: `rin.type.headline`.
- Blocked date: `rin.type.footnote`, `rin.text.secondary`, format: "Blocked MMM d, yyyy".

### Search

- `SearchBar` component at top.
- Filters blocked list by name (client-side, since blocked list is small).
- If no results: "No results for '[query]'" inline.

### Unblock Flow

1. User swipes left on a blocked user row.
2. "Unblock" button appears (red background, white text).
3. Tapping "Unblock" shows confirmation dialog:

```
┌──────────────────────────────────────┐
│                                      │
│        Unblock Alex Thompson?        │
│                                      │
│  They will be able to find your      │
│  profile and send you access         │
│  requests again. They won't be       │
│  notified that you unblocked them.   │
│                                      │
│  ┌──────────────────────────────────┐│
│  │           Unblock                ││  ← destructive style
│  ├──────────────────────────────────┤│
│  │           Cancel                 ││
│  └──────────────────────────────────┘│
│                                      │
└──────────────────────────────────────┘
```

4. On confirm: row animates out, server call to unblock.
5. On failure: row reappears with error toast: "Couldn't unblock. Try again."

### Blocking Effects (Reference)

When User A blocks User B:
- B cannot see any of A's profiles (primary or shadow) in search results.
- B cannot view A's profile if they have a direct link.
- B cannot send access requests to A.
- B is not notified of the block.
- Existing access permissions from B to A's fields are revoked.
- If B is in any of A's circles, B remains in the circle but their access is suspended.

### States

| State | Behavior |
|-------|----------|
| Default | List of blocked users sorted by block date (most recent first) |
| Empty | `EmptyStateView` with icon, title, subtitle |
| Searching | Filtered list updates in real-time |
| Unblocking | Row shows brief loading indicator before removal |
| Offline | List shown from cache, swipe disabled, "Offline" banner |
| Loading | Skeleton shimmer rows while fetching from server |

---

## 6) SET4: Export My Data

### Purpose

GDPR Article 20 compliant data portability. Allows users to request a machine-readable export of all their personal data. Cross-references `DATA_RETENTION_DELETION_V1.md` Section 5.

### Layout

```
┌──────────────────────────────────────┐
│ ◀ Settings       Export My Data      │
├──────────────────────────────────────┤
│                                      │
│ Request a copy of your Rin data.     │
│ The export includes:                 │
│                                      │
│ WHAT'S INCLUDED                      │
│ ┌──────────────────────────────────┐ │
│ │ ● Profile data (name, email,    │ │
│ │   phone, bio, photo metadata)   │ │
│ │ ● Contact list (names and       │ │
│ │   identifiers only)             │ │
│ │ ● Circle names and membership   │ │
│ │ ● Notes and tags                │ │
│ │ ● Access policy settings        │ │
│ │ ● Score history (last 90 days)  │ │
│ │ ● Account activity log          │ │
│ └──────────────────────────────────┘ │
│                                      │
│ FORMAT                               │
│ ┌──────────────────────────────────┐ │
│ │ JSON archive (.zip)              │ │
│ │ Download link expires after      │ │
│ │ 7 days.                          │ │
│ └──────────────────────────────────┘ │
│                                      │
│ TIMING                               │
│ ┌──────────────────────────────────┐ │
│ │ Export may take up to 72 hours   │ │
│ │ to prepare. You'll receive a     │ │
│ │ push notification when it's      │ │
│ │ ready.                           │ │
│ └──────────────────────────────────┘ │
│                                      │
│       [Request Data Export]          │
│                                      │
└──────────────────────────────────────┘


EXPORT IN PROGRESS:
┌──────────────────────────────────────┐
│ ◀ Settings       Export My Data      │
├──────────────────────────────────────┤
│                                      │
│ ┌──────────────────────────────────┐ │
│ │      ⏳ Export in progress       │ │
│ │                                  │ │
│ │  Requested: Feb 15, 2026         │ │
│ │  Estimated: Ready by Feb 18      │ │
│ │                                  │ │
│ │  We'll notify you when your      │ │
│ │  data is ready to download.      │ │
│ └──────────────────────────────────┘ │
│                                      │
│  You can request a new export in     │
│  24 hours.                           │
│                                      │
└──────────────────────────────────────┘


EXPORT READY:
┌──────────────────────────────────────┐
│ ◀ Settings       Export My Data      │
├──────────────────────────────────────┤
│                                      │
│ ┌──────────────────────────────────┐ │
│ │      ✅ Export ready             │ │
│ │                                  │ │
│ │  Created: Feb 16, 2026           │ │
│ │  Expires: Feb 23, 2026           │ │
│ │  Size: 2.4 MB                    │ │
│ │                                  │ │
│ │       [Download Export]          │ │
│ └──────────────────────────────────┘ │
│                                      │
│       [Request New Export]           │
│                                      │
└──────────────────────────────────────┘
```

### Export Contents Detail

| Data category | Included fields | Notes |
|--------------|----------------|-------|
| Profile data | Name, email, phone, bio, photo metadata | Photo files NOT included (metadata only) |
| Contact list | Names and identifiers | Other people's PII is NOT included |
| Circles | Circle names, membership lists | Anonymized circle IDs for members |
| Notes and tags | All user-created notes on contacts | Free text included |
| Access policies | Per-circle and per-contact field visibility settings | Full matrix |
| Score history | Daily score values for last 90 days | Component breakdowns included |
| Activity log | Login history, major account actions | Timestamps and action types |

### Rate Limiting

- One export request per 24 hours.
- If user requests a second export within 24h, show: "You can request a new export in [N hours, N minutes]."
- "Request Data Export" button disabled with countdown timer.

### States

| State | Behavior |
|-------|----------|
| Default (no pending export) | Information screen with "Request Data Export" button |
| Request in progress | Button replaced by progress card with estimated completion |
| Export ready | Download button visible, expiry date shown |
| Export expired | "Your previous export has expired." with new request button |
| Rate limited | Button disabled with countdown |
| Request failed | Error banner: "Couldn't start export. Try again later." |
| Offline | Button disabled, "Offline" banner |

---

## 7) SET5: Send Feedback

### Purpose

Simple feedback form for bug reports, feature requests, and general comments. Submissions go to an internal feedback queue (not email).

### Layout

```
┌──────────────────────────────────────┐
│ ◀ Settings       Send Feedback       │
├──────────────────────────────────────┤
│                                      │
│ CATEGORY                             │
│ ┌──────────────────────────────────┐ │
│ │ [Bug] [Feature Request] [Other]  │ │
│ └──────────────────────────────────┘ │
│                                      │
│ MESSAGE                              │
│ ┌──────────────────────────────────┐ │
│ │ Tell us what's on your mind...   │ │
│ │                                  │ │
│ │                                  │ │
│ │                                  │ │
│ │                                  │ │
│ │                          0/1000  │ │
│ └──────────────────────────────────┘ │
│                                      │
│ SCREENSHOT (OPTIONAL)                │
│ ┌──────────────────────────────────┐ │
│ │     [+ Add Screenshot]           │ │
│ └──────────────────────────────────┘ │
│                                      │
│         [Send Feedback]              │
│                                      │
└──────────────────────────────────────┘


SCREENSHOT ATTACHED:
┌──────────────────────────────────────┐
│ │  ┌──────┐                        │ │
│ │  │ 🖼️  │ screenshot.png  [✕]   │ │
│ │  │      │ 1.2 MB                 │ │
│ │  └──────┘                        │ │
└──────────────────────────────────────┘


CONFIRMATION:
┌──────────────────────────────────────┐
│                                      │
│              ✅                      │
│                                      │
│      Thanks for your feedback!       │
│                                      │
│   We read every message. If you      │
│   reported a bug, we'll look into    │
│   it as soon as possible.            │
│                                      │
│           [Done]                     │
│                                      │
└──────────────────────────────────────┘
```

### Category Selector

Segmented control (horizontal pill picker) with three options:
- **Bug** — "Something isn't working"
- **Feature Request** — "I'd like to see..."
- **Other** — General comments

Default: no category selected. Category is required before submission.

### Message Field

- Multi-line `TextEditor`.
- Placeholder: "Tell us what's on your mind..."
- Character limit: 1,000 characters.
- Character counter in bottom-right corner: `rin.type.caption`, `rin.text.tertiary`.
- Counter turns `rin.brand.error` when within 50 characters of limit.

### Screenshot

- Tap "Add Screenshot" opens `PHPickerViewController` (photos library) with `filter: .images`, selection limit 1.
- After selection: thumbnail preview with filename, file size, and remove button (X).
- Max file size: 10 MB. If exceeded: "Image too large. Choose a smaller image."
- Formats accepted: JPEG, PNG, HEIF.

### Submission

- "Send Feedback" is a `PrimaryButton`.
- Disabled until both category and message (min 10 characters) are provided.
- On tap: button shows loading state.
- Payload sent to feedback API: `{ category, message, screenshot_url?, app_version, os_version, device_model }`.
- On success: navigate to confirmation screen (auto-dismiss after 3s or tap "Done").
- On failure: inline error: "Couldn't send feedback. Check your connection and try again."

### Metadata Automatically Attached

The following metadata is silently included with every submission (no user action required):
- App version and build number.
- iOS version.
- Device model.
- Locale.
- Current premium status.
- Timestamp.

### States

| State | Behavior |
|-------|----------|
| Default | Empty form, "Send Feedback" disabled |
| Partially filled | Category or message missing, button disabled |
| Valid | Category + message (10+ chars), button enabled |
| Sending | Button loading state, form non-interactive |
| Success | Confirmation screen |
| Failed | Error banner, form remains editable for retry |
| Offline | "Send Feedback" disabled, "Offline" banner |

---

## 8) SET6: Help & FAQ

### Purpose

In-app help surface with searchable FAQ organized by category. Provides self-service answers before directing users to support.

### Layout

```
┌──────────────────────────────────────┐
│ ◀ Settings         Help & FAQ        │
├──────────────────────────────────────┤
│ [🔍 Search help articles...       ] │
├──────────────────────────────────────┤
│                                      │
│ ACCOUNT                              │
│ ┌──────────────────────────────────┐ │
│ │ How do I change my phone number? │ │
│ │ How do I change my email?        │ │
│ │ How do I delete my account?      │ │
│ │ How do I restore a purchase?     │ │
│ └──────────────────────────────────┘ │
│                                      │
│ CONTACTS                             │
│ ┌──────────────────────────────────┐ │
│ │ How does contact import work?    │ │
│ │ What happens when I merge dupes? │ │
│ │ Can I undo a merge?              │ │
│ └──────────────────────────────────┘ │
│                                      │
│ CIRCLES                              │
│ ┌──────────────────────────────────┐ │
│ │ What are circles?                │ │
│ │ What does "Ask" access mean?     │ │
│ │ How do I change who sees my info?│ │
│ └──────────────────────────────────┘ │
│                                      │
│ SCORE                                │
│ ┌──────────────────────────────────┐ │
│ │ What is Rin Score?               │ │
│ │ How is my score calculated?      │ │
│ │ Why did my score change?         │ │
│ └──────────────────────────────────┘ │
│                                      │
│ PREMIUM                              │
│ ┌──────────────────────────────────┐ │
│ │ What's included in Premium?      │ │
│ │ How do I cancel my subscription? │ │
│ │ How do I restore my purchase?    │ │
│ └──────────────────────────────────┘ │
│                                      │
│ PRIVACY                              │
│ ┌──────────────────────────────────┐ │
│ │ What data does Rin collect?      │ │
│ │ How do I export my data?         │ │
│ │ Who can see my information?      │ │
│ │ How do I block someone?          │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ Can't find what you're looking   │ │
│ │ for?                             │ │
│ │                                  │ │
│ │       [Contact Support]          │ │
│ └──────────────────────────────────┘ │
│                                      │
└──────────────────────────────────────┘


ARTICLE EXPANDED:
┌──────────────────────────────────────┐
│ ◀ Help           Article Title       │
├──────────────────────────────────────┤
│                                      │
│ How do I change my phone number?     │
│                                      │
│ To change your phone number:         │
│                                      │
│ 1. Go to Settings > Account.         │
│ 2. Tap your phone number.            │
│ 3. Tap "Add new number."             │
│ 4. Verify via OTP.                   │
│ 5. Set the new number as primary.    │
│ 6. Remove the old number if desired. │
│                                      │
│ Note: You must always have at least  │
│ one verified phone number.           │
│                                      │
│ ──────────────────────────────────── │
│                                      │
│ Was this helpful?                    │
│ [👍 Yes]   [👎 No]                  │
│                                      │
└──────────────────────────────────────┘
```

### Implementation

Two implementation options (open decision -- see Section 17):

**Option A: Native list** (preferred for v1)
- FAQ content bundled in app as JSON.
- Categories displayed as collapsible sections.
- Tap article title → push to article detail screen.
- Search filters across all articles (title + body text).
- Content updated via remote config (no app update needed).

**Option B: In-app WebView**
- `SFSafariViewController` or `WKWebView` pointing to help.rin.app.
- Styled to match app theme.
- Requires network connectivity.

### FAQ Categories

| Category | Article count (initial) |
|----------|------------------------|
| Account | 4 |
| Contacts | 3 |
| Circles | 3 |
| Score | 3 |
| Premium | 3 |
| Privacy | 4 |

### Search

- `SearchBar` at top.
- Client-side full-text search across article titles and body content.
- Results shown as flat list (no category grouping).
- No results: "No articles found for '[query]'. Try a different search or contact support."

### Article Detail

- Pushed screen with article title in nav bar.
- Rendered markdown body.
- "Was this helpful?" feedback at bottom: thumbs up / thumbs down.
- Feedback sent as analytics event: `faq.article_rated { article_id, helpful: bool }`.

### "Contact Support" CTA

- Positioned at bottom of the FAQ list.
- Tapping opens `MFMailComposeViewController` if available.
- Pre-fills: To: `support@rin.app`, Subject: `Rin Support Request`, Body: includes app version and device info.
- If mail not configured: copy `support@rin.app` to clipboard with toast: "Email address copied."

### States

| State | Behavior |
|-------|----------|
| Default | All categories expanded with article titles |
| Searching | Flat filtered list |
| No results | Empty state with "Contact Support" fallback |
| Article viewed | Pushed detail screen |
| Offline (native) | Cached content available |
| Offline (WebView) | Error state: "Help articles require an internet connection." |

---

## 9) SET7: Delete Account

### Purpose

Multi-step account deletion flow. This is a critical, irreversible (after grace period) action. The flow is intentionally high-friction to prevent accidental deletion. Cross-references `DATA_RETENTION_DELETION_V1.md` for backend behavior.

### Flow Overview

```
SET7-1 Explanation
    ↓ [Continue]
SET7-2 Data Scope
    ↓ [Continue]
SET7-3 Grace Period Info
    ↓ [Continue]
SET7-4 Final Confirmation (type "DELETE")
    ↓ [Delete My Account]
Processing → Sign Out → Login Screen
```

### SET7-1: Explanation

```
┌──────────────────────────────────────┐
│ ◀ Settings     Delete Account        │
├──────────────────────────────────────┤
│                                      │
│              ⚠️                      │
│                                      │
│     We're sorry to see you go        │
│                                      │
│  Deleting your account is a serious  │
│  action. Before you proceed, please  │
│  understand what this means.         │
│                                      │
│  Once your account is permanently    │
│  deleted, we cannot recover it.      │
│                                      │
│  If you're experiencing an issue,    │
│  consider contacting support first.  │
│                                      │
│       [Contact Support]              │
│                                      │
│                                      │
│  ┌──────────────────────────────────┐│
│  │   Continue with deletion    [>]  ││
│  └──────────────────────────────────┘│
│                                      │
│                Step 1 of 4           │
└──────────────────────────────────────┘
```

### SET7-2: Data Scope

```
┌──────────────────────────────────────┐
│ ◀ Back        What Gets Deleted      │
├──────────────────────────────────────┤
│                                      │
│ The following data will be           │
│ permanently deleted:                 │
│                                      │
│ DELETED IMMEDIATELY                  │
│ ┌──────────────────────────────────┐ │
│ │ ● Your profile and all shadow   │ │
│ │   profiles                       │ │
│ │ ● Your profile photos            │ │
│ │ ● Your contacts and notes        │ │
│ │ ● Your circles and access        │ │
│ │   policies                       │ │
│ │ ● Your score and score history   │ │
│ │ ● Your notification preferences  │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ANONYMIZED (KEPT FOR ANALYTICS)      │
│ ┌──────────────────────────────────┐ │
│ │ ● Network graph edges (180 days, │ │
│ │   fully anonymized)              │ │
│ │ ● Score distribution data        │ │
│ │   (90 days, fully anonymized)    │ │
│ └──────────────────────────────────┘ │
│                                      │
│ NOT AFFECTED                         │
│ ┌──────────────────────────────────┐ │
│ │ ● How others have saved your     │ │
│ │   contact info in their phones   │ │
│ │ ● Other users' copies of your    │ │
│ │   contact data                   │ │
│ └──────────────────────────────────┘ │
│                                      │
│         [Continue]                   │
│                                      │
│                Step 2 of 4           │
└──────────────────────────────────────┘
```

### SET7-3: Grace Period

```
┌──────────────────────────────────────┐
│ ◀ Back          Grace Period         │
├──────────────────────────────────────┤
│                                      │
│             🕐                       │
│                                      │
│       30-day recovery window         │
│                                      │
│  After you confirm deletion:         │
│                                      │
│  ┌──────────────────────────────────┐│
│  │ ● Your account will be          ││
│  │   immediately deactivated        ││
│  │                                  ││
│  │ ● Your profile will be hidden   ││
│  │   from search and other users    ││
│  │                                  ││
│  │ ● Your data will be anonymized  ││
│  │   but held for 30 days           ││
│  │                                  ││
│  │ ● Sign back in within 30 days   ││
│  │   to recover your account        ││
│  │                                  ││
│  │ ● After 30 days, all original   ││
│  │   data is permanently purged     ││
│  └──────────────────────────────────┘│
│                                      │
│  If you have an active Premium       │
│  subscription, manage it through     │
│  iOS Settings to avoid being         │
│  charged after deletion.             │
│  [Manage Subscription]               │
│                                      │
│         [Continue]                   │
│                                      │
│                Step 3 of 4           │
└──────────────────────────────────────┘
```

"Manage Subscription" link opens `UIApplication.openURL` to `https://apps.apple.com/account/subscriptions`.

### SET7-4: Final Confirmation

```
┌──────────────────────────────────────┐
│ ◀ Back       Confirm Deletion        │
├──────────────────────────────────────┤
│                                      │
│              🔴                      │
│                                      │
│   This action cannot be undone       │
│   after 30 days.                     │
│                                      │
│   Type DELETE to confirm:            │
│                                      │
│   ┌──────────────────────────────┐   │
│   │                              │   │
│   └──────────────────────────────┘   │
│                                      │
│   ┌──────────────────────────────┐   │
│   │      Delete My Account       │   │  ← disabled until
│   └──────────────────────────────┘   │     "DELETE" typed
│                                      │
│              [Cancel]                │
│                                      │
│                Step 4 of 4           │
└──────────────────────────────────────┘
```

### Final Confirmation Logic

- Text field accepts free text input.
- "Delete My Account" button is `PrimaryButton` with destructive style (`rin.brand.error` background).
- Button disabled until text field exactly matches "DELETE" (case-sensitive).
- On tap:
  1. Button enters loading state.
  2. API call: `DELETE /api/v1/account` with auth token.
  3. On success:
     - Clear all local data (Keychain, UserDefaults, SwiftData cache).
     - Dismiss all navigation stacks.
     - Present login screen with transient banner: "Your account has been scheduled for deletion."
  4. On failure:
     - Error alert: "Couldn't delete your account right now. Please try again later or contact support."
     - Remain on SET7-4.

### Subscription Handling

If user has an active Premium subscription:
- SET7-3 prominently displays the subscription warning.
- "Manage Subscription" link opens iOS subscription management.
- Deletion proceeds regardless of subscription status (Apple handles subscription lifecycle independently).
- Server marks the subscription for cancellation tracking.

### States

| State | Behavior |
|-------|----------|
| Step navigation | Linear flow, back button on each step returns to previous |
| Text field empty | "Delete My Account" button disabled |
| Text field incorrect | Button remains disabled |
| Text field matches "DELETE" | Button enabled with destructive styling |
| Processing | Full-screen loading overlay: "Deleting your account..." |
| Success | Auto-redirect to login screen |
| Failed | Error alert on SET7-4, can retry |
| Offline | "Continue" buttons disabled on each step, "Offline" banner |

---

## 10) SET8: Verified Channels

### Purpose

Manage all verified communication channels (phone numbers and email addresses) linked to the account. The primary channel is used for authentication and account recovery.

### Layout

```
┌──────────────────────────────────────┐
│ ◀ Settings     Verified Channels     │
├──────────────────────────────────────┤
│                                      │
│ PHONE NUMBERS                        │
│ ┌──────────────────────────────────┐ │
│ │ +1 (555) 000-0000     Primary ✓ │ │
│ │ Verified Jan 1, 2026            │ │
│ │──────────────────────────────────│ │
│ │ +44 20 7946 0958                │ │
│ │ Verified Feb 10, 2026           │ │
│ └──────────────────────────────────┘ │
│                                      │
│ [+ Add Phone Number]                 │
│                                      │
│ EMAIL ADDRESSES                      │
│ ┌──────────────────────────────────┐ │
│ │ john@email.com        Primary ✓ │ │
│ │ Verified Jan 1, 2026            │ │
│ │──────────────────────────────────│ │
│ │ john@work.com                    │ │
│ │ Verified Feb 5, 2026            │ │
│ └──────────────────────────────────┘ │
│                                      │
│ [+ Add Email Address]                │
│                                      │
└──────────────────────────────────────┘


CHANNEL ROW CONTEXT MENU (long-press):
┌──────────────────────────────────────┐
│  Set as Primary                      │
│  ──────────────────────────────────  │
│  Remove Channel               🔴    │
└──────────────────────────────────────┘
```

### Channel Row

Each channel row contains:
- Channel value: phone number (formatted) or email address. `rin.type.headline`.
- "Primary" badge + checkmark if this is the primary channel. Badge uses `rin.brand.primary` tint.
- Verification date: `rin.type.footnote`, `rin.text.secondary`. Format: "Verified MMM d, yyyy".

### Add Phone Number Flow

1. Tap "Add Phone Number".
2. Sheet presents phone input with country code picker.
3. User enters phone number, taps "Send Code".
4. OTP entry screen (6-digit code, same as onboarding verification).
5. On verification success: phone number added to list, marked as verified.
6. On failure: "Invalid code. Try again." with resend option.

```
┌──────────────────────────────────────┐
│                           [Cancel]   │
│                                      │
│      Add Phone Number                │
│                                      │
│  ┌────────────────────────────┐      │
│  │ +1  │ (___) ___-____      │      │
│  └────────────────────────────┘      │
│                                      │
│     [Send Verification Code]         │
│                                      │
└──────────────────────────────────────┘


OTP ENTRY:
┌──────────────────────────────────────┐
│                           [Cancel]   │
│                                      │
│      Enter the code we sent to       │
│      +1 (555) 123-4567              │
│                                      │
│      ┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐      │
│      │  ││  ││  ││  ││  ││  │      │
│      └──┘└──┘└──┘└──┘└──┘└──┘      │
│                                      │
│      Resend code (59s)               │
│                                      │
└──────────────────────────────────────┘
```

### Add Email Address Flow

1. Tap "Add Email Address".
2. Sheet presents email input field.
3. User enters email, taps "Send Verification Link".
4. Confirmation: "We sent a verification link to john@work.com. Check your inbox."
5. User taps link in email → deep link back to app → email marked as verified.
6. If user returns to app before verifying: email shown as "Pending verification" with "Resend" option.

```
┌──────────────────────────────────────┐
│                           [Cancel]   │
│                                      │
│      Add Email Address               │
│                                      │
│  ┌────────────────────────────┐      │
│  │ email@example.com          │      │
│  └────────────────────────────┘      │
│                                      │
│    [Send Verification Link]          │
│                                      │
└──────────────────────────────────────┘


PENDING VERIFICATION:
┌──────────────────────────────────────┐
│ │ john@work.com                    │ │
│ │ ⏳ Pending verification          │ │
│ │ [Resend Link]   [Cancel]         │ │
└──────────────────────────────────────┘
```

### Set as Primary

- Long-press any non-primary channel → context menu → "Set as Primary".
- Confirmation dialog: "Set +44 20 7946 0958 as your primary phone number? This will be used for sign-in."
- On confirm: update primary designation, server sync.
- Primary channel is used for authentication (sign-in OTP) and account recovery.

### Remove Channel

- Long-press any non-primary channel → context menu → "Remove Channel".
- Cannot remove the primary channel. If user tries (should not be possible via UI), show: "You can't remove your primary channel. Set another channel as primary first."
- Cannot remove the last channel of a type if it's the only verified channel overall. At least one verified channel (phone or email) must remain.
- Confirmation dialog: "Remove +44 20 7946 0958? You'll need to re-verify if you add it again."
- On confirm: channel removed, server sync.

### Constraints

| Rule | Enforcement |
|------|------------|
| At least one verified channel must exist at all times | "Remove" hidden/disabled on last remaining channel |
| Primary channel cannot be removed directly | Context menu shows "Set another channel as primary first" |
| Primary phone required for authentication | At least one verified phone must remain |
| Duplicate channels not allowed | "This number/email is already verified on your account" |

### States

| State | Behavior |
|-------|----------|
| Default | List of all verified channels grouped by type |
| Adding phone | Sheet with phone input + OTP flow |
| Adding email | Sheet with email input + pending verification |
| Pending verification | Email row shows pending status with resend/cancel |
| Removing | Brief loading indicator, row animates out |
| Single channel remaining | Remove option hidden |
| Offline | Add/remove disabled, "Offline" banner |

---

## 11) SET9: Subscription Management

### Purpose

Display current subscription status and provide management actions. Cross-references `IAP_SUBSCRIPTION_COMPLIANCE_V1.md` for StoreKit 2 implementation details and App Store compliance requirements.

### Layout: Free User

```
┌──────────────────────────────────────┐
│ ◀ Settings       Subscription        │
├──────────────────────────────────────┤
│                                      │
│            ┌──────┐                  │
│            │  ⭐  │                  │
│            └──────┘                  │
│                                      │
│         You're on the Free plan      │
│                                      │
│  Upgrade to Premium to unlock:       │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ 👀 Who Viewed Me                │ │
│ │ See who checked your profile    │ │
│ │ this week                        │ │
│ │──────────────────────────────────│ │
│ │ ✨ Enrichment Alerts            │ │
│ │ Know when contact info updates  │ │
│ │──────────────────────────────────│ │
│ │ 📋 How Am I Stored              │ │
│ │ See how others save your info   │ │
│ └──────────────────────────────────┘ │
│                                      │
│       [Upgrade to Premium]           │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │      Restore Purchases           │ │
│ └──────────────────────────────────┘ │
│                                      │
└──────────────────────────────────────┘
```

### Layout: Premium User

```
┌──────────────────────────────────────┐
│ ◀ Settings       Subscription        │
├──────────────────────────────────────┤
│                                      │
│            ┌──────┐                  │
│            │  ⭐  │                  │
│            └──────┘                  │
│                                      │
│       You're on Premium              │
│                                      │
│ PLAN DETAILS                         │
│ ┌──────────────────────────────────┐ │
│ │ Plan          Annual             │ │
│ │ Price         $49.99/year        │ │
│ │ Renews        Mar 12, 2026       │ │
│ │ Member since  Mar 12, 2025       │ │
│ └──────────────────────────────────┘ │
│                                      │
│ FEATURES INCLUDED                    │
│ ┌──────────────────────────────────┐ │
│ │ ✅ Who Viewed Me                 │ │
│ │ ✅ Enrichment Alerts             │ │
│ │ ✅ How Am I Stored               │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ Manage Subscription          [>] │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │      Restore Purchases           │ │
│ └──────────────────────────────────┘ │
│                                      │
│ To cancel, change plan, or update    │
│ payment, use "Manage Subscription"   │
│ above. This opens your iOS           │
│ subscription settings.               │
│                                      │
└──────────────────────────────────────┘
```

### "Upgrade to Premium" Button

- `PrimaryButton` style, `rin.brand.accent` tint.
- Tapping presents the paywall as a full-screen cover (same paywall from `rin://premium`).
- Paywall handles the StoreKit 2 purchase flow.
- On successful purchase: dismiss paywall, refresh SET9 to show Premium layout.

### Plan Details (Premium)

| Row | Label | Value source |
|-----|-------|-------------|
| Plan | "Plan" | `Product.subscription.subscriptionPeriod` → "Monthly" or "Annual" |
| Price | "Price" | `Product.displayPrice` + period (always localized, never hardcoded) |
| Renews | "Renews" | `Transaction.expirationDate` formatted as "MMM d, yyyy". If auto-renew off: "Expires" instead of "Renews" |
| Member since | "Member since" | `Transaction.originalPurchaseDate` |

### "Manage Subscription"

- Tapping opens `UIApplication.openURL` to `https://apps.apple.com/account/subscriptions`.
- This is the Apple-required mechanism for cancellation, plan changes, and payment updates.
- Explanatory footer text ensures the user understands why they are leaving the app.

### "Restore Purchases"

- Visible for both free and premium users.
- Tapping calls `AppStore.sync()` via StoreKit 2.
- Loading indicator on button during restore.
- On success (entitlement found): refresh screen, show toast: "Purchase restored successfully."
- On success (no entitlement): toast: "No previous purchases found."
- On failure: toast: "Couldn't restore purchases. Check your connection and try again."

### Subscription State Display

| Subscription state | Display |
|-------------------|---------|
| Free (never subscribed) | Free layout with upgrade CTA |
| Free (previously subscribed, expired) | Free layout with "Your Premium subscription expired on [date]. Resubscribe?" |
| Premium (auto-renew on) | Premium layout, "Renews [date]" |
| Premium (auto-renew off) | Premium layout, "Expires [date]" with amber warning |
| Premium (grace period — billing issue) | Premium layout with warning banner: "There's a billing issue with your subscription. Update your payment method to keep Premium." + "Manage Subscription" link |
| Premium (revoked — family sharing) | Reverts to Free layout with explanation |

### States

| State | Behavior |
|-------|----------|
| Loading | Skeleton shimmer while checking entitlements |
| Free | Upgrade CTA prominent |
| Premium | Plan details and management |
| Restoring | "Restore Purchases" button in loading state |
| Offline | Cached status displayed, "Upgrade" and "Restore" disabled |

---

## 12) Events

All events follow the existing PostHog event taxonomy.

### Settings Root

| Event | Properties | Trigger |
|-------|-----------|---------|
| `settings.viewed` | `source: "profile" \| "deep_link"` | SET1 appears |
| `settings.section_tapped` | `section: "account" \| "privacy" \| "notifications" \| "support" \| "danger_zone"`, `row: string` | Any row tapped |

### Notification Toggles

| Event | Properties | Trigger |
|-------|-----------|---------|
| `settings.notification_toggled` | `type: "score_updates" \| "dedup_suggestions" \| "enrichment_alerts" \| "access_requests" \| "marketing"`, `enabled: bool` | Any toggle changed |

### Privacy

| Event | Properties | Trigger |
|-------|-----------|---------|
| `settings.default_access_changed` | `field: string`, `old_state: "allow" \| "dont_allow" \| "ask"`, `new_state: string` | Access control changed in SET2 |
| `settings.default_access_reset` | — | "Reset to Defaults" confirmed in SET2 |
| `settings.blocked_user_unblocked` | `blocked_user_id: string` | User unblocked in SET3 |

### Data Export

| Event | Properties | Trigger |
|-------|-----------|---------|
| `settings.data_export_requested` | — | Export requested in SET4 |
| `settings.data_export_downloaded` | `size_bytes: int` | Export downloaded in SET4 |

### Feedback

| Event | Properties | Trigger |
|-------|-----------|---------|
| `settings.feedback_sent` | `category: "bug" \| "feature_request" \| "other"`, `has_screenshot: bool` | Feedback submitted in SET5 |

### Help

| Event | Properties | Trigger |
|-------|-----------|---------|
| `settings.faq_viewed` | `article_id: string`, `category: string` | FAQ article opened in SET6 |
| `settings.faq_rated` | `article_id: string`, `helpful: bool` | Article rated in SET6 |
| `settings.contact_support_tapped` | — | "Contact Support" tapped in SET6 |

### Account Lifecycle

| Event | Properties | Trigger |
|-------|-----------|---------|
| `settings.sign_out` | — | Sign out confirmed |
| `settings.account_deletion_initiated` | `step: 1..4` | Each step viewed in SET7 |
| `settings.account_deletion_confirmed` | — | "DELETE" typed and confirmed in SET7-4 |
| `settings.account_deletion_abandoned` | `step: 1..4` | User backs out of SET7 at any step |

### Verified Channels

| Event | Properties | Trigger |
|-------|-----------|---------|
| `settings.channel_added` | `type: "phone" \| "email"` | Channel verified in SET8 |
| `settings.channel_removed` | `type: "phone" \| "email"` | Channel removed in SET8 |
| `settings.channel_primary_changed` | `type: "phone" \| "email"` | Primary channel changed in SET8 |

### Subscription

| Event | Properties | Trigger |
|-------|-----------|---------|
| `settings.subscription_viewed` | `current_plan: "free" \| "monthly" \| "annual"` | SET9 appears |
| `settings.restore_purchases_tapped` | — | "Restore Purchases" tapped |
| `settings.manage_subscription_tapped` | — | "Manage Subscription" tapped (premium) |

---

## 13) Accessibility

### General

- All screens support Dynamic Type up to `AX5` size category.
- Section headers use semantic header trait for VoiceOver navigation.
- All interactive elements have minimum 44x44pt touch targets.

### VoiceOver Announcements

| Element | VoiceOver label |
|---------|----------------|
| Phone row (SET1) | "Phone, [number], verified. Tap to manage verified channels." |
| Email row (SET1) | "Email, [address], verified. Tap to manage verified channels." |
| Plan row (SET1) | "Plan, [Free/Premium]. Tap to manage subscription." |
| Notification toggle | "[Name] notifications, [on/off]. Double tap to toggle." |
| Enrichment toggle (free) | "Enrichment Alerts, Premium feature, locked. Double tap to learn about Premium." |
| Blocked user row | "[Name], blocked [date]. Swipe left to unblock." |
| Access state toggle (SET2) | "[Field name], currently set to [Allow/Don't Allow/Ask]. Tap to change." |
| Delete Account button | "Delete Account. Caution: this will permanently remove your account." |
| Version footer | "Rin version [version], build [build]" |

### Semantic Grouping

- Each section (Account, Privacy, Notifications, Support, Danger Zone) is wrapped in an accessibility container with the section name as label.
- Toggle rows group the label and toggle as a single accessible element.
- The Danger Zone section announces "Caution area" when entered via VoiceOver.

### Reduced Motion

- All navigation transitions respect `UIAccessibility.isReduceMotionEnabled`.
- Toggle animations replaced with instant state change.
- Card transitions in SET7 steps use cross-dissolve instead of push.

### Color Independence

- Toggle states never rely on color alone: "ON"/"OFF" text labels shown alongside toggle for color-blind users in high-contrast mode.
- Destructive actions use both color (`rin.brand.error`) and iconography (warning icons).
- Blocked user count badge uses both color and text.

---

## 14) Design Token Usage

### Typography

| Element | Token |
|---------|-------|
| Screen titles ("Settings", "Blocked Users") | `rin.type.title1` |
| Section headers ("ACCOUNT", "PRIVACY") | `rin.type.footnote` with `rin.text.secondary`, uppercased |
| Row labels ("Phone", "Email") | `rin.type.body` |
| Row detail values ("+1 (555) 000-0000") | `rin.type.body` with `rin.text.secondary` |
| Footer version string | `rin.type.footnote` with `rin.text.tertiary` |
| Badges ("Primary", "Premium") | `rin.type.caption` |
| Explanatory body text (SET2 banner, SET7 steps) | `rin.type.callout` |

### Spacing

| Context | Token |
|---------|-------|
| Screen horizontal padding | `rin.space.base` (16pt) |
| Section gap | `rin.space.lg` (24pt) |
| Row internal padding | `rin.space.base` horizontal, `rin.space.md` (12pt) vertical |
| Between icon and label | `rin.space.md` (12pt) |
| Footer vertical padding | `rin.space.xl` (32pt) top and bottom |

### Colors

| Element | Token |
|---------|-------|
| Screen background | `rin.bg.primary` |
| Section background | `rin.bg.secondary` |
| Toggle tint (on) | `rin.brand.primary` |
| "Danger Zone" header | `rin.brand.error` |
| "Delete Account" text | `rin.brand.error` |
| "Premium" badge | `rin.brand.accent` |
| Destructive buttons | `rin.brand.error` background, white text |
| Primary buttons | `rin.brand.primary` background, white text |

### Corner Radius

| Element | Token |
|---------|-------|
| Section cards | `rin.radius.lg` (12pt) |
| Input fields | `rin.radius.md` (8pt) |
| Buttons | `rin.radius.full` (capsule) |
| Screenshot thumbnail | `rin.radius.md` (8pt) |
| OTP digit boxes | `rin.radius.md` (8pt) |

---

## 15) State Persistence

| Setting | Storage | Synced to server |
|---------|---------|-----------------|
| Notification preferences (5 toggles) | `UserDefaults` | Yes |
| Default access controls (field matrix) | SwiftData cache | Yes (source of truth: server) |
| Blocked users list | SwiftData cache | Yes (source of truth: server) |
| Verified channels list | SwiftData cache | Yes (source of truth: server) |
| Subscription status | StoreKit 2 + server | Yes |
| FAQ article read state | `UserDefaults` | No |
| Last export request date (rate limit) | `UserDefaults` | No |

---

## 16) Error Handling

| Scenario | Behavior |
|----------|----------|
| Network timeout on any server call | Inline error banner with "Retry" button |
| Sign out fails | Alert: "Couldn't sign out. Try again." (rare; local sign-out still executes) |
| Deletion API fails | Alert on SET7-4: "Couldn't delete your account right now. Please try again later or contact support." |
| Toggle sync fails | Toggle reverts to previous state with brief error toast |
| Channel verification OTP expired | "Code expired. Tap Resend to get a new code." |
| Export request fails | Error banner on SET4 with retry |
| Feedback submission fails | Error banner on SET5, form preserved for retry |
| Restore purchases fails | Toast: "Couldn't restore purchases. Check your connection and try again." |

---

## 17) Open Decisions

1. **FAQ implementation**: Native bundled JSON list vs. in-app WebView pointing to `help.rin.app`. Native is preferred for offline access and performance, but WebView allows content updates without remote config infrastructure.

2. **Notification preferences granularity**: Whether to add per-circle notification controls (e.g., mute access requests from a specific circle) or keep it as global toggles only for v1.

3. **Export format**: Whether to offer additional formats beyond JSON (e.g., CSV for contacts, vCard) or keep JSON-only for simplicity.

4. **Blocked users source**: Whether blocking happens only from the contact detail screen (current assumption) or also from search results, access request screens, and profile views. Entry points affect where the "Block" action surfaces, but all converge on the SET3 list.

5. **Delete account subscription handling**: Whether the deletion flow should actively cancel the Apple subscription via server-side API or only warn the user to cancel manually through iOS Settings. Active cancellation is better UX but adds server-side complexity with App Store Server API.
