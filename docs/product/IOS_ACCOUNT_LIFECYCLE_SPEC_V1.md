# iOS Account Lifecycle Spec V1

## 1) Purpose

Define every account state transition, its behavioral spec, data implications, and UI flows. Covers sign out, account deletion (with 30-day recovery), session management, and force sign-out.

Companion docs:
- `docs/design/IOS_KEY_SCREEN_WIREFRAMES_V1.md` (Settings wireframe, Danger Zone)
- `docs/architecture/DATA_RETENTION_DELETION_V1.md` (retention and deletion policy)
- `docs/architecture/IOS_NAVIGATION_STATE_V1.md` (state persistence, coordinators)
- `docs/architecture/IOS_OFFLINE_STORAGE_V1.md` (local storage, SwiftData, Keychain)
- `docs/product/SHADOW_PROFILE_UX_V1.md` (shadow profile lifecycle)
- `docs/product/IOS_ONBOARDING_SCREEN_SPEC_V1.md` (re-onboarding after sign-in)
- `docs/design/IOS_DESIGN_TOKENS_V1.md` (colors, typography, components)

---

## 2) Account State Machine

### 2.1 States

| State | Description |
|-------|-------------|
| **Active** | Authenticated, full access. Normal operation. |
| **Signed Out** | Device-local. Auth cleared, server data preserved. Can sign back in. |
| **Deletion Pending** | 30-day soft-delete. Profile removed from search. Recoverable. |
| **Hard Deleted** | PII purged. Anonymized graph retained per retention policy. Irrecoverable. |
| **Suspended** | Abuse-triggered. All profiles frozen. Appeal path available. |

### 2.2 Transitions

```
                    ┌──────────┐
         ┌─────────│  Active   │─────────────┐
         │         └──────────┘              │
         │          ↑        ↑               │
    Sign Out    Sign In   Recovery       Delete Account
         │      (OTP)    (within 30d)        │
         ↓          │        │               ↓
   ┌───────────┐    │    ┌─────────────────────┐
   │ Signed Out │────┘    │  Deletion Pending   │
   └───────────┘          │     (30 days)       │
                          └─────────────────────┘
                                    │
                              30 days expire
                                    │
                                    ↓
                          ┌───────────────────┐
                          │   Hard Deleted     │
                          └───────────────────┘

   ┌──────────┐   Abuse     ┌───────────┐  Appeal    ┌──────────┐
   │  Active   │───────────→│ Suspended  │──────────→│  Active   │
   └──────────┘             └───────────┘            └──────────┘
```

### 2.3 Transition Rules

| From | To | Trigger | Requires Auth |
|------|----|---------|---------------|
| Active | Signed Out | User taps Sign Out | Already authenticated |
| Signed Out | Active | Phone OTP verification | OTP |
| Active | Deletion Pending | User completes deletion flow (ACCT2) | Already authenticated |
| Deletion Pending | Active | User signs in during 30-day window | OTP |
| Deletion Pending | Hard Deleted | 30-day grace period expires | Automated job |
| Active | Suspended | Abuse system trigger | System action |
| Suspended | Active | Appeal approved | Admin action |

---

## 3) Sign Out Flow (ACCT1)

### 3.1 Entry Point

Settings screen (wireframe section 11) → Danger Zone → "Sign Out".

### 3.2 Confirmation Dialog

Presented as `.alert` (per navigation state spec section 5.1).

```
┌──────────────────────────────────────┐
│                                      │
│           Sign Out?                  │
│                                      │
│  You'll need to verify your phone    │
│  number to sign back in.            │
│                                      │
│  ┌──────────────┐ ┌──────────────┐  │
│  │    Cancel     │ │   Sign Out   │  │
│  │   (primary)   │ │(destructive) │  │
│  └──────────────┘ └──────────────┘  │
│                                      │
└──────────────────────────────────────┘
```

- "Cancel" button: `rin.brand.primary` (#1A73E8). Default action.
- "Sign Out" button: `rin.brand.error` (#EF4444). Destructive role.

### 3.3 On Confirm: Cleanup Sequence

Executed in order:

| Step | Action | Target |
|------|--------|--------|
| 1 | Clear auth tokens | Keychain (`kSecAttrAccessibleAfterFirstUnlock` items) |
| 2 | Clear biometric trust flag | Keychain |
| 3 | Clear SwiftData cache | All `CachedContact`, `CachedCircle`, `CachedScore`, `CachedDedupSuggestion` records |
| 4 | Clear sensitive UserDefaults | Active profile selection, last sync timestamp, badge counts |
| 5 | Preserve non-sensitive UserDefaults | Theme preference, notification preferences, onboarding completion flag |
| 6 | Clear photo cache | FileManager Caches directory (contact thumbnails) |
| 7 | Clear mutation queue | All pending SwiftData mutation entries |
| 8 | Cancel background tasks | `BGAppRefreshTask`, `BGProcessingTask` for sync |
| 9 | Dismiss all navigation | Pop all `NavigationPath` stacks, dismiss modals/sheets |
| 10 | Navigate to welcome screen | `AppCoordinator` → welcome/sign-in state |

### 3.4 Re-Sign-In After Sign Out

1. Welcome screen displayed (not full onboarding carousel).
2. User enters phone number (screen S4 from onboarding spec).
3. OTP verification (screen S5 from onboarding spec).
4. On successful OTP: navigate directly to Home tab. Skip onboarding screens S1-S3, S6-S12.
5. Full sync triggered: contacts, circles, score, dedup suggestions fetched from server.
6. SwiftData cache rebuilt from server data.

The `onboarding_completed` flag in UserDefaults (preserved during sign out) gates whether to show the full onboarding flow or the abbreviated re-auth flow.

### 3.5 Multi-Device Behavior

- Sign out is device-local only. Other devices remain signed in.
- No server-side notification sent to other devices on sign out.
- Server auth tokens for other devices remain valid.

---

## 4) Account Deletion Flow (ACCT2)

### 4.1 Entry Point

Settings screen → Danger Zone → "Delete Account" (marked with red dot indicator per wireframe).

### 4.2 Flow Overview

Four-step flow presented as a full-screen modal with its own `NavigationStack` (per navigation state spec section 5.2: multi-step flows use sheet with fullscreen detent).

```
ACCT2-S1: Information    →  ACCT2-S2: Data Summary
                              →  ACCT2-S3: Reason (optional)
                                   →  ACCT2-S4: Final Confirmation
                                        →  Deletion initiated → Sign out
```

### 4.3 ACCT2-S1: Information Screen

```
┌──────────────────────────────────────┐
│ ◀ Cancel      Delete Your Account    │
├──────────────────────────────────────┤
│                                      │
│  ⚠️                                 │
│                                      │
│  Before you go, please understand    │
│  what happens when you delete        │
│  your account.                       │
│                                      │
│  ┌──────────────────────────────────┐│
│  │ Your profile will be removed     ││
│  │ from search and discovery.       ││
│  └──────────────────────────────────┘│
│  ┌──────────────────────────────────┐│
│  │ Your contacts, circles, notes,   ││
│  │ and score history will be        ││
│  │ deleted.                         ││
│  └──────────────────────────────────┘│
│  ┌──────────────────────────────────┐│
│  │ All shadow profiles will be      ││
│  │ deleted.                         ││
│  └──────────────────────────────────┘│
│  ┌──────────────────────────────────┐│
│  │ Premium subscription will NOT    ││
│  │ be auto-cancelled. Cancel it     ││
│  │ in iOS Settings > Subscriptions. ││
│  └──────────────────────────────────┘│
│  ┌──────────────────────────────────┐│
│  │ This action is reversible for    ││
│  │ 30 days, then permanent.         ││
│  └──────────────────────────────────┘│
│                                      │
│         [Continue]                   │
│                                      │
│  ░░░░░░░░░░░░  step 1 of 4          │
└──────────────────────────────────────┘
```

**Typography:**
- Title: `rin.type.title1` (28pt Bold).
- Consequence cards: `rin.type.body` (17pt Regular) on `rin.bg.secondary` background.
- Premium warning card: `rin.brand.warning` (#F59E0B) left border accent.
- "Continue" button: `SecondaryButton` standard style.

**Content rules:**
- Each consequence is a separate card for scannability.
- Premium warning is visually distinct (warning accent) to prevent accidental subscription continuation.
- 30-day reversibility is stated clearly as the final card.

### 4.4 ACCT2-S2: Data Summary

```
┌──────────────────────────────────────┐
│ ◀ Back        Your Data              │
├──────────────────────────────────────┤
│                                      │
│  The following will be deleted:      │
│                                      │
│  ┌──────────────────────────────────┐│
│  │ 👤  Profile                      ││
│  │     Primary + 3 shadow profiles  ││
│  ├──────────────────────────────────┤│
│  │ 📇  Contacts              342   ││
│  ├──────────────────────────────────┤│
│  │ ⭕  Circles                  5   ││
│  ├──────────────────────────────────┤│
│  │ 📝  Notes                   28   ││
│  ├──────────────────────────────────┤│
│  │ 📊  Score history       30 days  ││
│  ├──────────────────────────────────┤│
│  │ ⭐  Premium status        Free   ││
│  └──────────────────────────────────┘│
│                                      │
│  ┌──────────────────────────────────┐│
│  │ 📦 Export My Data First     [>]  ││
│  └──────────────────────────────────┘│
│                                      │
│         [Continue]                   │
│                                      │
│  ░░░░░░░░░░░░  step 2 of 4          │
└──────────────────────────────────────┘
```

**Data counts:**
- Fetched live from server or SwiftData cache.
- Shadow profile count includes all active + archived shadows.
- Premium status shows "Active" (with subscription type) or "Free".
- If counts fail to load: show "—" with footnote "Counts unavailable. All data will still be deleted."

**Export CTA:**
- Taps opens data export flow (Settings → Privacy → Export My Data, per wireframe section 11).
- Navigates within the deletion modal or presents as a separate sheet.
- Export format: JSON archive per DATA_RETENTION_DELETION_V1.md section 5.

### 4.5 ACCT2-S3: Reason Collection (Optional)

```
┌──────────────────────────────────────┐
│ ◀ Back        Help Us Improve        │
├──────────────────────────────────────┤
│                                      │
│  Why are you leaving?                │
│  (optional)                          │
│                                      │
│  ┌──────────────────────────────────┐│
│  │ ○  Not useful                    ││
│  │ ○  Privacy concerns              ││
│  │ ○  Too many notifications        ││
│  │ ○  Found an alternative          ││
│  │ ○  Other                         ││
│  └──────────────────────────────────┘│
│                                      │
│  ┌──────────────────────────────────┐│
│  │ Tell us more (optional)          ││
│  │                                  ││
│  │                                  ││
│  └──────────────────────────────────┘│
│                                      │
│    [Continue]        [Skip]          │
│                                      │
│  ░░░░░░░░░░░░  step 3 of 4          │
└──────────────────────────────────────┘
```

**Behavior:**
- Single selection radio group. "Other" enables the text field.
- Text field: max 500 characters. `rin.type.body` on `rin.bg.tertiary`.
- "Skip" button: `SecondaryButton` style. Advances without recording a reason.
- "Continue" button: records selected reason + optional text, then advances.
- Reason stored server-side for product analytics. Anonymized after account deletion.

### 4.6 ACCT2-S4: Final Confirmation

```
┌──────────────────────────────────────┐
│ ◀ Back        Confirm Deletion       │
├──────────────────────────────────────┤
│                                      │
│                                      │
│  ⚠️ This cannot be undone after     │
│     30 days.                         │
│                                      │
│  Type DELETE to confirm:             │
│                                      │
│  ┌──────────────────────────────────┐│
│  │                                  ││
│  └──────────────────────────────────┘│
│                                      │
│                                      │
│  ┌──────────────────────────────────┐│
│  │       Delete My Account          ││
│  │      (destructive, red)          ││
│  └──────────────────────────────────┘│
│                                      │
│  ┌──────────────────────────────────┐│
│  │          Cancel                  ││
│  │      (primary, blue)             ││
│  └──────────────────────────────────┘│
│                                      │
│  ░░░░░░░░░░░░  step 4 of 4          │
└──────────────────────────────────────┘
```

**Behavior:**
- Text field requires exact string "DELETE" (case-sensitive).
- "Delete My Account" button: disabled until text field matches. Uses `rin.brand.error` (#EF4444) background, white text. `PrimaryButton` destructive variant.
- "Cancel" button: `rin.brand.primary` (#1A73E8). Prominent placement, larger than delete button. Encourages staying.
- On "Delete My Account" tap: show loading spinner on button, disable all interaction.

**Button hierarchy (deliberate):**
- "Cancel" is visually more prominent (primary blue, standard button size).
- "Delete My Account" is visually secondary until DELETE is typed (then red, but still below Cancel).
- This nudges users toward cancellation without blocking determined users.

### 4.7 After Deletion Initiated

Server-side actions (immediate):

| Step | Action |
|------|--------|
| 1 | Account status set to `deletion_pending` with expiry date (now + 30 days) |
| 2 | PII anonymized immediately (per DATA_RETENTION_DELETION_V1.md section 2.1) |
| 3 | Deletion hold snapshot created (encrypted PII copy for recovery) |
| 4 | Profile removed from search indexes |
| 5 | All auth tokens revoked (all devices) |
| 6 | All outbound Ask requests cancelled |
| 7 | All pending inbound access requests auto-denied |
| 8 | All shadow profiles marked for deletion |
| 9 | Push notification tokens deleted |
| 10 | Background sync and enrichment stopped |

Client-side actions (immediate, same as sign-out cleanup):

| Step | Action |
|------|--------|
| 1 | Clear auth tokens from Keychain |
| 2 | Clear SwiftData cache |
| 3 | Clear all UserDefaults (including preferences — full wipe, unlike sign out) |
| 4 | Clear photo cache |
| 5 | Clear mutation queue |
| 6 | Cancel all background tasks |
| 7 | Dismiss all navigation |
| 8 | Navigate to welcome screen |

User sees a brief confirmation toast before sign-out: "Your account will be deleted on [date]. Sign back in within 30 days to cancel."

---

## 5) 30-Day Recovery Window

### 5.1 Recovery Entry

User opens the app and signs in with their phone number during the 30-day grace period.

### 5.2 Recovery Flow

```
User opens app → Welcome screen
    ↓
Phone number input (S4)
    ↓
OTP verification (S5)
    ↓
Server detects: account is in deletion_pending state
    ↓
Recovery screen displayed
    ↓
Account restored → Navigate to Home
```

### 5.3 Recovery Screen

```
┌──────────────────────────────────────┐
│                                      │
│                                      │
│            Welcome back!             │
│                                      │
│  Your account was scheduled for      │
│  deletion on [date].                 │
│                                      │
│  Would you like to cancel the        │
│  deletion and restore your account?  │
│                                      │
│                                      │
│  ┌──────────────────────────────────┐│
│  │     Restore My Account           ││
│  │       (primary, blue)            ││
│  └──────────────────────────────────┘│
│                                      │
│  ┌──────────────────────────────────┐│
│  │    Continue With Deletion        ││
│  │      (secondary, muted)          ││
│  └──────────────────────────────────┘│
│                                      │
└──────────────────────────────────────┘
```

### 5.4 On "Restore My Account"

Server-side restoration (per DATA_RETENTION_DELETION_V1.md section 3.2):

| Step | Action |
|------|--------|
| 1 | Account status set back to `active` |
| 2 | PII restored from deletion hold snapshot |
| 3 | Profile re-indexed in search |
| 4 | Sync and enrichment resumed |
| 5 | All shadow profiles restored to pre-deletion state |
| 6 | Score history restored |
| 7 | Deletion hold snapshot retained (cleared on next scheduled job) |

Client-side:
- Full sync triggered (same as first-launch sync per offline storage spec section 6.1).
- Navigate to Home tab. Skip onboarding (onboarding was completed before deletion).
- Toast: "Your account has been restored."

### 5.5 On "Continue With Deletion"

- User is signed out again.
- Deletion countdown continues unchanged.
- No additional confirmation required (user already completed full ACCT2 flow previously).

### 5.6 After 30 Days: Hard Deletion

Automated daily job (per DATA_RETENTION_DELETION_V1.md section 7.1):

| Step | Action |
|------|--------|
| 1 | Purge deletion hold snapshot (PII originals) |
| 2 | Purge contact book import data |
| 3 | Purge enrichment data linked to user |
| 4 | Purge session data and push tokens |
| 5 | Purge mutation queue entries |
| 6 | Anonymized graph edges retained for 180 days |
| 7 | Anonymized score history retained for 90 days |
| 8 | Dispute/abuse records retained for 365 days (anonymized) |

After hard deletion, signing in with the same phone number creates a brand new account with full onboarding.

---

## 6) Session Management

### 6.1 Session Model

- Single active session per device. No multi-session support.
- Each device holds one auth token in Keychain.
- Auth token format: opaque JWT, signed server-side.

### 6.2 Token Lifecycle

| Event | Behavior |
|-------|----------|
| Sign in (OTP verified) | New token issued, stored in Keychain |
| App foreground | Token validated against server (if >1h since last check) |
| API request | Token sent in Authorization header |
| Token near expiry | Auto-refreshed transparently (no user interaction) |
| 30 days inactive | Token expires. Forced re-auth via OTP. |
| Sign out | Token cleared from Keychain, invalidated server-side |
| Account deletion | All tokens invalidated server-side across all devices |

### 6.3 Device Trust and Biometric Auth

After first successful OTP verification on a device:

1. Device is marked as "trusted" (flag stored in Keychain).
2. Subsequent app opens: biometric auth (Face ID / Touch ID) replaces OTP.
3. Biometric prompt: "Unlock Rin" with fallback to device passcode.
4. If biometric fails 3 times: fall back to OTP re-verification.
5. Device trust cleared on sign out.

### 6.4 New Device Login

When a user signs in on a new device:

1. OTP verification required (biometric trust does not transfer).
2. Push notification sent to all existing signed-in devices: "New sign-in from [Device Name]."
3. Notification includes: "If this wasn't you, tap to secure your account."
4. "Secure your account" deep links to force sign-out flow (ACCT3).

### 6.5 Token Expiry (Forced Re-Auth)

If 30 days pass with no app activity:

1. On next app open: auth token is expired.
2. SwiftData cache preserved (not cleared).
3. User sees sign-in screen with phone number pre-filled.
4. OTP verification required.
5. On success: resume session with existing cache. Incremental sync to catch up.
6. Device trust re-established for biometric auth.

---

## 7) Force Sign Out All Devices (ACCT3)

### 7.1 Entry Point

Settings → Account → "Sign out everywhere".

### 7.2 Confirmation Dialog

```
┌──────────────────────────────────────┐
│                                      │
│      Sign Out Everywhere?            │
│                                      │
│  All other devices will be signed    │
│  out immediately. You'll stay        │
│  signed in on this device.           │
│                                      │
│  ┌──────────────┐ ┌──────────────┐  │
│  │    Cancel     │ │  Sign Out    │  │
│  │   (primary)   │ │   All        │  │
│  │               │ │(destructive) │  │
│  └──────────────┘ └──────────────┘  │
│                                      │
└──────────────────────────────────────┘
```

### 7.3 On Confirm

| Step | Action |
|------|--------|
| 1 | Server invalidates all auth tokens except the requesting device's token |
| 2 | A new token is issued for the current device (rotation for security) |
| 3 | Push notification sent to all other devices: "You've been signed out." |
| 4 | Other devices: on next app open, cleared to sign-in screen |
| 5 | Toast on current device: "All other devices have been signed out." |

### 7.4 When to Suggest

- After a new device login notification the user did not initiate.
- After a security concern is raised in the Security Inbox.
- After changing phone number (future feature).

---

## 8) Data Cleanup: Sign Out vs Delete

| Data | Sign Out (ACCT1) | Deletion Initiated (ACCT2) |
|------|------------------|---------------------------|
| **Auth tokens (Keychain)** | Cleared (device only) | Cleared (all devices, server-side) |
| **Biometric trust (Keychain)** | Cleared | Cleared |
| **SwiftData cache** | Cleared | Cleared |
| **UserDefaults (preferences)** | Preserved (theme, notifications) | Cleared (full wipe) |
| **UserDefaults (app state)** | Cleared (profile selection, sync timestamp) | Cleared |
| **UserDefaults (onboarding flag)** | Preserved | Cleared |
| **Photo cache (FileManager)** | Cleared | Cleared |
| **Mutation queue (SwiftData)** | Cleared | Cleared |
| **Background tasks** | Cancelled | Cancelled |
| **Server: profile data** | Preserved | Anonymized immediately |
| **Server: contacts** | Preserved | Soft-deleted (purged after 30d) |
| **Server: circles** | Preserved | Soft-deleted (purged after 30d) |
| **Server: score** | Preserved | Anonymized (retained 90d) |
| **Server: shadow profiles** | Preserved | All marked for deletion |
| **Server: graph edges** | Preserved | Anonymized (retained 180d) |
| **Server: enrichment data** | Preserved | Purged after 30d |
| **Server: search index** | Preserved | Removed immediately |
| **Server: Ask requests (outbound)** | Preserved | Cancelled immediately |
| **Server: access requests (inbound)** | Preserved | Auto-denied immediately |

---

## 9) Events

### 9.1 Sign Out Events

| Event | Properties | Trigger |
|-------|-----------|---------|
| `account.sign_out` | `device_id`, `method` (manual / forced / token_expired) | User signs out or token expires |
| `account.sign_out_cancelled` | — | User dismisses sign-out confirmation |

### 9.2 Deletion Events

| Event | Properties | Trigger |
|-------|-----------|---------|
| `account.deletion_step_viewed` | `step` (1-4) | User views each deletion step |
| `account.deletion_export_tapped` | — | User taps "Export My Data First" |
| `account.deletion_reason` | `reason` (enum), `detail_text` (optional, hashed) | User submits reason |
| `account.deletion_reason_skipped` | — | User skips reason step |
| `account.deletion_initiated` | `scheduled_purge_date`, `shadow_count`, `contact_count` | User confirms DELETE |
| `account.deletion_cancelled` | `days_remaining` | User restores account during grace period |
| `account.deletion_continued` | `days_remaining` | User declines recovery, continues deletion |
| `account.deletion_completed` | `principal_id_hash` | Hard delete job runs after 30 days |

### 9.3 Session Events

| Event | Properties | Trigger |
|-------|-----------|---------|
| `account.re_authenticated` | `method` (otp / biometric), `device_id` | User signs back in |
| `account.session_expired` | `inactive_days`, `device_id` | Token expires after 30 days inactive |
| `account.new_device_login` | `new_device_id`, `device_name` | Login from a new device |
| `account.force_sign_out_all` | `device_count_invalidated` | User triggers ACCT3 |
| `account.biometric_auth_success` | `biometric_type` (face_id / touch_id) | Biometric unlock |
| `account.biometric_auth_failed` | `attempt_count` | Failed biometric attempt |

---

## 10) Accessibility

### 10.1 Sign Out

- Confirmation dialog: VoiceOver reads title and body text as a single announcement.
- "Sign Out" button labeled with accessibility trait `.destructive`.
- Cancel is the default action (selected by default with VoiceOver).

### 10.2 Account Deletion Flow

- Each step has a step indicator read by VoiceOver: "Step [N] of 4".
- Consequence cards in ACCT2-S1: each card is a separate VoiceOver element with full text.
- Premium warning card: VoiceOver prefixes with "Important:" for emphasis.
- Data summary in ACCT2-S2: VoiceOver reads each row as "[category]: [count]".
- Reason selection in ACCT2-S3: radio buttons use standard accessibility traits.
- DELETE text field in ACCT2-S4:
  - VoiceOver hint: "Type the word DELETE in all capital letters to confirm account deletion."
  - Keyboard type: `.asciiCapable` (no autocorrect, no suggestions).
  - Field uses `accessibilityLabel`: "Deletion confirmation".
- "Delete My Account" button:
  - When disabled: VoiceOver announces "Delete My Account, dimmed. Type DELETE above to enable."
  - When enabled: VoiceOver announces "Delete My Account, button, destructive action."
- "Cancel" button: VoiceOver announces "Cancel, button. Returns to Settings."

### 10.3 Recovery Screen

- VoiceOver reads recovery screen as: "Welcome back. Your account was scheduled for deletion on [date]. Would you like to restore it?"
- "Restore My Account" has trait `.default`.
- "Continue With Deletion" has trait `.destructive`.

### 10.4 General

- All screens support Dynamic Type up to AX5.
- Reduced motion: no transition animations between deletion steps.
- Sufficient color contrast: destructive red (#EF4444) on white passes WCAG AA for large text.
- Focus order: interactive elements are in logical top-to-bottom order.

---

## 11) Edge Cases

1. **User initiates deletion while offline.** Mutation queued. Deletion does not proceed until device is online and server confirms. Show: "Account deletion requires an internet connection."

2. **User signs out on one device, another device still signed in.** Other device continues normally. No cross-device sign-out unless ACCT3 is used.

3. **User deletes account while having active Premium.** Premium subscription continues billing through Apple. Deletion info screen (ACCT2-S1) warns explicitly. Rin does not auto-cancel the subscription (Apple does not allow apps to cancel subscriptions programmatically).

4. **User signs back in after deletion on the same device.** UserDefaults were fully cleared (including onboarding flag). User sees full onboarding if account was hard-deleted. Sees recovery screen if within 30-day window.

5. **User creates new account with same phone after hard deletion.** Treated as entirely new user. No data carryover. Full onboarding. Brand new principal ID.

6. **User attempts deletion while mutation queue has pending changes.** Pending mutations are abandoned (not synced). Deletion proceeds. Data summary shows server-side counts, not local pending state.

7. **Force sign-out (ACCT3) while another device is mid-sync.** Other device's sync fails with 401. On next app open, that device shows sign-in screen.

8. **Token expires during active app use (rare: 30-day expiry mid-session).** API returns 401. App prompts OTP re-verification inline without clearing local data.

9. **Suspended account attempts sign-in.** After OTP, server returns suspended status. App shows: "Your account has been suspended. Contact support for assistance." with link to help.

10. **User restores account, but shadow profiles had org-linked professional profiles.** Professional profiles restored but org linkage is not automatically re-established. User must request re-linkage from business admin.

---

## 12) Implementation Notes

### 12.1 AuthService Integration

The `AuthService` (shared state per navigation spec section 4.2) manages all state transitions:

```
AuthService
├── signOut()           → ACCT1 cleanup sequence
├── deleteAccount()     → ACCT2 server request + cleanup
├── restoreAccount()    → Recovery flow
├── forceSignOutAll()   → ACCT3 server request
├── refreshToken()      → Auto token refresh
└── checkTokenValidity()→ Called on app foreground
```

`AuthService` publishes `authState: AuthState` (active / signedOut / deletionPending / suspended) consumed by `AppCoordinator` to determine root view.

### 12.2 Coordinator Navigation

On sign out or deletion:
1. `AuthService.authState` transitions to `.signedOut`.
2. `AppCoordinator` observes state change.
3. `AppCoordinator` replaces root view with welcome/sign-in screen.
4. All tab coordinators' `NavigationPath` instances are reset.
5. All presented sheets/covers are dismissed.

### 12.3 Deletion Flow as Modal

The ACCT2 deletion flow is presented as a `.fullScreenCover` from the Settings screen, containing its own `NavigationStack` for the 4-step flow. This isolates the deletion flow from the main navigation hierarchy and prevents accidental dismissal via swipe.

---

## 13) Open Decisions

1. **Biometric prompt frequency.** Should biometric auth be required on every app open, or only after the app has been in background for a configurable duration (e.g., 5 minutes)?

2. **Deletion flow interruption.** If the user force-quits the app mid-deletion flow (e.g., after step 2 but before confirming), should the flow resume where they left off on next launch, or restart from step 1?

3. **Data export blocking.** Should the deletion flow block advancement from ACCT2-S2 until the user has either exported their data or explicitly declined? Current spec allows proceeding without export.

4. **Subscription cancellation deep link.** Should ACCT2-S1 include a direct deep link to iOS Settings > Subscriptions for Premium users, or just text instructions? Apple may have restrictions on deep-linking to subscription management.

5. **Session limit per account.** Should there be a maximum number of concurrent signed-in devices (e.g., 5)? Current spec allows unlimited devices with the same account.
