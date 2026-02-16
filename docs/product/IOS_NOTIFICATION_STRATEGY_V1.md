# iOS Notification Strategy V1

## 1) Purpose

Define the complete push notification and in-app notification strategy for the Rin iOS app: what fires, when, exact copy, deep links, permission flow, preferences, grouping, badge management, rate limits, and analytics events.

Core constraint: notifications must honor the onboarding promise made in S3 -- "No spam. No surprise outreach. We never notify anyone or expose your information without your permission."

Companion docs:
- `docs/architecture/IOS_NAVIGATION_STATE_V1.md` (deep link scheme, tab badge rules)
- `docs/product/IOS_ONBOARDING_SCREEN_SPEC_V1.md` (S3 no-spam promise)
- `docs/product/CIRCLE_MANAGEMENT_UX_V1.md` (Ask flow generates notifications)
- `docs/product/SHADOW_PROFILE_UX_V1.md` (cross-profile notifications, identity reveal)
- `docs/product/CONTACTS_IMPORT_SYNC_UX_V1.md` (sync completion, dedup results)
- `docs/product/IOS_SCORE_EXPLANATION_SCREEN_SPEC_V1.md` (score change context)
- `docs/analytics/PRODUCT_ANALYTICS_EVENT_TAXONOMY_V1.md` (event naming conventions)
- `docs/design/BRAND_NARRATIVE_V1.md` (tone of voice, notification tone -- section 6.5)
- `docs/design/IOS_DESIGN_TOKENS_V1.md` (visual tokens)

---

## 2) Notification Philosophy

### 2.1 Core Principle

Every notification must be worth the interruption. If the user would not thank Rin for sending it, it does not send.

### 2.2 What Rin Sends

- Actionable alerts the user can act on immediately (approve request, review duplicates, check score change).
- Time-sensitive security notifications (access requests, account alerts).
- User-configured reminders (follow-ups, birthdays).
- Premium feature summaries (weekly viewer digest).

### 2.3 What Rin Never Sends (V1)

| Prohibited notification type | Reason |
|------------------------------|--------|
| Marketing or promotional | No marketing notifications in v1. Future versions require explicit opt-in. |
| Social pressure ("X just joined Rin") | Violates no-surprise-outreach promise. Never sent in any version. |
| Re-engagement ("We miss you") | Banned by brand voice (Brand Narrative V1 section 6.5). |
| Congratulatory ("You hit 100 contacts") | No engagement farming. Substance over performance. |
| Gamification nudges ("Keep your streak") | No dark patterns. |
| Permission re-prompts via push | Never use push to nag about denied permissions. |
| Notifications about other users joining | Violates no-surprise-outreach. |

### 2.4 Guiding Rules

1. Every notification is actionable -- tapping it leads to something the user can do.
2. No notification fires without the user having opted in (either system permission or in-app preference).
3. Notification copy states facts, not feelings. No "Yay" or "Great news" (per Brand Narrative V1 section 5.2).
4. Frequency: less is always more. Rate limits enforce this structurally.
5. Respect iOS notification settings, Focus modes, and in-app preferences. If iOS says quiet, Rin is quiet.
6. Shadow profile notifications display that profile's avatar and name, not the primary identity (per Shadow Profile UX V1 section 4.4).

---

## 3) Notification Categories and Catalog

iOS notification categories registered with `UNNotificationCategory`. Each category maps to an in-app preference toggle.

### 3.1 Category Overview

| Category ID | Display name | Default | Premium-gated |
|-------------|-------------|---------|---------------|
| `SCORE` | Score Updates | On | No |
| `CONTACTS` | Contact Updates | On | No |
| `SECURITY` | Security Alerts | On (locked on) | No |
| `PREMIUM` | Premium Insights | On | Yes |
| `REMINDER` | Reminders | On | No |
| `PROFILE` | Profile Alerts | On | No |

### 3.2 Complete Notification Catalog

#### SCORE Category

| Type ID | Trigger | Copy | Subtitle | Deep link | Delivery | Max frequency |
|---------|---------|------|----------|-----------|----------|---------------|
| `score.updated` | Daily score batch detects meaningful change (>= +/-2 points) | "Your Rin Score changed: 72 to 75 (+3). Tap to see what improved." | nil | `rin://score` | Standard | 1 per day |
| `score.milestone` | Score crosses a quality label boundary (e.g., Building to Good) | "Your Rin Score reached Good (60). Your network is growing stronger." | nil | `rin://score` | Standard | 1 per event (rare) |

Copy variants for `score.updated`:
- Positive: "Your Rin Score changed: 72 to 75 (+3). Tap to see what improved."
- Negative: "Your Rin Score changed: 75 to 71 (-4). Tap to see what shifted."
- Large positive (>=10): "Your Rin Score jumped to 82 (+12). See the breakdown."

#### CONTACTS Category

| Type ID | Trigger | Copy | Subtitle | Deep link | Delivery | Max frequency |
|---------|---------|------|----------|-----------|----------|---------------|
| `contacts.dedup_ready` | Dedup scan completes with reviewable suggestions | "3 possible duplicates found. Review and clean your contacts." | nil | `rin://home?section=dedup` | Standard | 1 per day |
| `contacts.enrichment` | Contact profile updated via network enrichment | "[Name] updated their profile. New info available." | nil | `rin://contacts/{id}` | Batched | 3 per day |
| `contacts.sync_completed` | Background sync finishes | (silent) | nil | nil | Silent (badge update only) | No limit |
| `contacts.conflict` | Sync detects field conflict requiring user resolution | "1 contact needs your attention. A field changed on your device and in Rin." | nil | `rin://home?section=conflicts` | Standard | 1 per day |

Copy variants for `contacts.dedup_ready`:
- Singular: "1 possible duplicate found. Review and clean your contacts."
- Plural: "{count} possible duplicates found. Review and clean your contacts."

Copy variants for `contacts.enrichment`:
- Single: "[Name] updated their profile. New info available."
- Batched: "[Name] and {count} others updated their profiles. New info available."

#### SECURITY Category

| Type ID | Trigger | Copy | Subtitle | Deep link | Delivery | Max frequency |
|---------|---------|------|----------|-----------|----------|---------------|
| `security.access_request` | Someone taps "Request" on an Ask field (Circle Management UX V1 section 3.3) | "[Name] requested access to your [field]." | "Tap to approve or deny." | `rin://security?tab=requests&id={id}` | Immediate (time-sensitive) | No limit |
| `security.dispute_update` | Ownership dispute status changes | "Your ownership dispute has been updated." | nil | `rin://security/dispute/{id}` | Standard | No limit |
| `security.new_signin` | New device or location sign-in detected | "New sign-in detected from [device/location]." | nil | `rin://security?tab=alerts` | Immediate (time-sensitive) | No limit |
| `security.suspicious_activity` | Automated abuse detection flags unusual behavior | "Unusual activity detected on your account. Review now." | nil | `rin://security?tab=alerts` | Immediate (time-sensitive) | No limit |
| `security.access_approved` | Owner approved the user's field access request | "Your request to see [Name]'s [field] was approved." | nil | `rin://contacts/{id}` | Standard | No limit |

Note: `security.access_denied` does NOT generate a notification. Denied requests produce no signal to the requester (per Circle Management UX V1 section 3.3).

#### PREMIUM Category

| Type ID | Trigger | Copy | Subtitle | Deep link | Delivery | Max frequency |
|---------|---------|------|----------|-----------|----------|---------------|
| `premium.who_viewed` | Weekly profile viewer summary (premium subscribers only) | "3 people viewed your profile this week." | nil | `rin://profile?section=viewers` | Standard | 1 per week |

Copy variants for `premium.who_viewed`:
- Singular: "1 person viewed your profile this week."
- Plural: "{count} people viewed your profile this week."
- Zero viewers: (no notification sent)

#### REMINDER Category

| Type ID | Trigger | Copy | Subtitle | Deep link | Delivery | Max frequency |
|---------|---------|------|----------|-----------|----------|---------------|
| `reminder.followup` | User-scheduled follow-up reminder fires | "Reminder: Follow up with [Name] about [note context]." | nil | `rin://contacts/{id}` | Standard (scheduled) | As scheduled by user |
| `reminder.birthday` | Contact's birthday is today | "[Name]'s birthday is today." | nil | `rin://contacts/{id}` | Standard (morning delivery) | 1 per contact per year |

Copy note for `reminder.followup`: the "[note context]" is user-authored when setting the reminder. If no note was provided, copy is: "Reminder: Follow up with [Name]."

#### PROFILE Category

| Type ID | Trigger | Copy | Subtitle | Deep link | Delivery | Max frequency |
|---------|---------|------|----------|-----------|----------|---------------|
| `profile.shadow_offboarding` | Professional shadow unlinked from org (Shadow Profile UX V1 section 8.2) | "Your professional profile is no longer linked to [Company]. Choose what to do." | "You have 30 days to convert, archive, or delete it." | `rin://profile/shadow/{id}` | Standard | 1 per event |
| `profile.identity_reveal` | Shadow owner reveals primary identity to the user (Shadow Profile UX V1 section 6.2) | "[Shadow name] is also known as [Primary name] on Rin." | nil | `rin://contacts/{id}` | Standard | No limit |
| `profile.offboarding_reminder` | 7 days before auto-archive deadline for offboarded shadow | "7 days left to decide what happens to your [Company] profile." | nil | `rin://profile/shadow/{id}` | Standard | 1 per event |

---

## 4) Notification Permission Flow

### 4.1 When to Request

Notification permission is NOT requested during onboarding. It is requested after first value delivery -- specifically, after the user completes their first meaningful action on the Home tab (reviewing a dedup suggestion, viewing their score, or completing circle setup).

Rationale: the onboarding promise is "no spam, no surprise outreach." Asking for notification permission before proving value undermines that promise.

### 4.2 Pre-Permission Screen

Before triggering the iOS system permission dialog, show a pre-permission explainer screen (half-sheet modal):

```
--------------------------------------------
|                                          |
|  Stay in control                         |
|                                          |
|  Rin notifications are limited to:       |
|                                          |
|  [shield]  Security alerts               |
|            Access requests, account       |
|            activity                       |
|                                          |
|  [chart]   Score changes                 |
|            When your Rin Score moves      |
|                                          |
|  [person]  Contact updates               |
|            Duplicates found, profile      |
|            changes                        |
|                                          |
|  What you won't get:                     |
|  No marketing. No "come back" nudges.    |
|  No social pressure. Ever.              |
|                                          |
|  [Enable Notifications]  (primary)       |
|  [Not Now]               (secondary)     |
|                                          |
--------------------------------------------
```

- "Enable Notifications" triggers `UNUserNotificationCenter.requestAuthorization`.
- "Not Now" dismisses the sheet. App continues fully functional without notifications.

### 4.3 If Permission Denied

- App works fully without push notifications. No degraded mode.
- In-app notification center (badge counts, request queue) still works via polling/background sync.
- Contextual re-prompt: shown ONLY when the user explicitly navigates to Settings > Notifications and the toggle state shows iOS permission is denied. Copy: "Notifications are turned off in iOS Settings. [Open Settings]"
- No nagging. No repeated prompts. No "you're missing out" messaging.

### 4.4 If Permission Granted

- Register for remote notifications via APNs.
- Send device token to backend.
- All categories default to ON (except premium-gated categories for non-subscribers).
- User can fine-tune per category in Settings > Notifications.

### 4.5 Provisional Notifications (iOS 12+)

Consider using `UNAuthorizationOptions.provisional` for silent trial delivery. If enabled:
- Notifications delivered silently to notification center (no banner, no sound, no badge).
- User sees "Keep" or "Turn Off" on first silent notification.
- Reduces permission dialog friction.
- Trade-off: lower initial visibility.

See Open Decisions section 12 for final call.

---

## 5) In-App Notification Preferences

### 5.1 Settings Screen: Notifications

Located at Settings > Notifications. Available regardless of iOS push permission status (controls in-app badges and notification center behavior even without push).

```
--------------------------------------------
| Notifications                            |
|                                          |
| Push notifications are [enabled/disabled]|
| [Open iOS Settings] (if disabled)        |
|                                          |
| ---------------------------------------- |
|                                          |
| Score Updates                       [ON] |
| Score changes of 2+ points              |
|                                          |
| Contact Updates                     [ON] |
| Duplicates, enrichments, sync results    |
|                                          |
| Security Alerts                     [ON] |
| Access requests, sign-ins, disputes  🔒  |
|                                          |
| Premium Insights                   [🔒]  |
| Weekly profile viewers              LOCK |
|                                          |
| Reminders                           [ON] |
| Follow-ups, birthdays                    |
|                                          |
| Profile Alerts                      [ON] |
| Shadow profile updates, identity reveals |
|                                          |
| ---------------------------------------- |
|                                          |
| Quiet Hours                              |
| Defer to iOS Focus modes            [>]  |
|                                          |
--------------------------------------------
```

### 5.2 Toggle Behavior

- Each category: on/off toggle.
- Security Alerts: always on, toggle is locked with a lock icon and explanatory text: "Security alerts can't be turned off." Rationale: account security notifications should always reach the user.
- Premium Insights: shows lock icon (`🔒`) if user is not a premium subscriber. Tapping shows the premium paywall. If subscribed, toggle becomes functional.
- Toggling a category off stops both push notifications AND in-app badge counts for that category.

### 5.3 Quiet Hours

V1 defers entirely to iOS Focus modes. No custom quiet hours implementation.

- Copy in settings: "Rin respects your iOS Focus modes. Manage notification delivery in iOS Settings > Focus."
- Rin registers all notification categories with appropriate `interruptionLevel`:
  - `.timeSensitive`: `security.access_request`, `security.new_signin`, `security.suspicious_activity`
  - `.active`: all other standard notifications
  - `.passive`: `contacts.sync_completed` (silent), batched enrichments

---

## 6) Notification Presentation

### 6.1 Notification Content

Every notification includes:

| Field | Content |
|-------|---------|
| Title | Category or sender context (e.g., "Rin Score", "[Name]", "Security Alert") |
| Body | The notification copy from section 3.2 |
| Subtitle | Optional secondary line (used only where specified in catalog) |
| Badge | Updated app icon badge count |
| Sound | Category-specific (see section 10) |
| Thread ID | Grouping identifier (see section 6.3) |
| Category | iOS category identifier for action buttons |

### 6.2 Notification Actions (Quick Actions)

Registered with `UNNotificationCategory` for inline action buttons:

| Category | Actions | Behavior |
|----------|---------|----------|
| `SECURITY` (access request) | "Approve", "Deny" | Inline response without opening app |
| `CONTACTS` (dedup) | "Review" | Opens app to dedup section |
| `REMINDER` | "Done", "Snooze 1h" | Marks complete or reschedules |
| `PROFILE` (offboarding) | "Choose Now" | Opens profile management |

### 6.3 Notification Grouping

Notifications group by category in the iOS notification center using `threadIdentifier`:

| Category | Thread ID pattern | Result |
|----------|-------------------|--------|
| `SCORE` | `score` | All score notifications grouped |
| `CONTACTS` | `contacts` | All contact notifications grouped |
| `SECURITY` | `security.{type}` | Access requests grouped separately from account alerts |
| `PREMIUM` | `premium` | All premium notifications grouped |
| `REMINDER` | `reminder.{contactId}` | Reminders for same contact grouped |
| `PROFILE` | `profile.{profileId}` | Notifications per shadow profile grouped separately |

### 6.4 Shadow Profile Notification Presentation

Per Shadow Profile UX V1 section 4.4:

- If a notification arrives for a profile other than the currently active one, the notification displays that profile's avatar and name.
- Push notification payload includes `profileId` and `profileDisplayName`.
- Notification title prefix: "[Profile Name]:" for non-active profiles.
- Example: if active profile is "Nan" but a security request arrives for shadow "N. Ehmo", the notification shows: Title: "N. Ehmo: Access Request", Body: "[Name] requested access to your email address."
- Tapping the notification switches to the relevant profile before navigating to the deep link (per Shadow Profile UX V1 section 4.3 switch behavior).

---

## 7) Badge Management

### 7.1 Tab Badge Rules

Per Navigation State V1 section 6, with notification-driven updates:

| Tab | Badge source | Update trigger | Clears when |
|-----|-------------|---------------|-------------|
| Home | Unreviewed dedup suggestion count | Sync completion, background dedup scan | User views dedup section |
| Circles | Pending access request count (Ask flow) | Push notification (`security.access_request`) | User views request queue |
| Score | Score changed since last view (boolean dot) | Daily score batch push | User opens Score tab |
| Profile | Security inbox unread count | Push notification (security category) | User views security inbox |

### 7.2 App Icon Badge

- App icon badge number = sum of all tab badge counts.
- Updated server-side via APNs badge payload on every push notification.
- Also updated on app foreground via `NotificationService` shared state.
- Badge resets to accurate count on every app open (prevents stale badge).

### 7.3 Badge Update Logic

```
On push notification received (background):
    1. Parse category and update local badge store
    2. Set app icon badge via notification payload

On app foreground:
    1. Fetch current counts from NotificationService
    2. Update all tab badges
    3. Update app icon badge to match sum

On relevant screen viewed:
    1. Clear that tab's badge count
    2. Recalculate app icon badge
    3. Update server badge state (prevents stale badge on next push)
```

---

## 8) Rate Limits and Anti-Annoyance

### 8.1 Rate Limit Table

| Category | Type | Max per day | Max per week | Batching behavior |
|----------|------|-------------|--------------|-------------------|
| SCORE | `score.updated` | 1 | 7 | Only fires on >= +/-2 point change |
| SCORE | `score.milestone` | 1 | 1 | Only on label boundary crossing |
| CONTACTS | `contacts.dedup_ready` | 1 | 3 | Aggregates all pending suggestions into one notification |
| CONTACTS | `contacts.enrichment` | 3 | 10 | Batches multiple enrichments into single notification if >3 would fire |
| CONTACTS | `contacts.sync_completed` | No limit | No limit | Silent; badge only |
| CONTACTS | `contacts.conflict` | 1 | 3 | Aggregates all pending conflicts |
| SECURITY | `security.access_request` | No limit | No limit | Real-time; never batched or delayed |
| SECURITY | `security.dispute_update` | No limit | No limit | Event-driven |
| SECURITY | `security.new_signin` | No limit | No limit | Real-time |
| SECURITY | `security.suspicious_activity` | No limit | No limit | Real-time |
| SECURITY | `security.access_approved` | 5 | 20 | Batched if >5 approvals in a day |
| PREMIUM | `premium.who_viewed` | 0 (weekly) | 1 | Weekly digest only |
| REMINDER | `reminder.followup` | No limit | No limit | User-scheduled |
| REMINDER | `reminder.birthday` | No limit | No limit | 1 per contact per year |
| PROFILE | `profile.shadow_offboarding` | 1 | 1 | Per event |
| PROFILE | `profile.identity_reveal` | 5 | 20 | Per event |
| PROFILE | `profile.offboarding_reminder` | 1 | 1 | Per event |

### 8.2 Anti-Annoyance Rules

1. **No duplicate notifications**: if the same notification type with the same content would fire within 1 hour of a previous identical notification, suppress it.
2. **Daily digest fallback**: if more than 5 non-security notifications would fire in a single day, batch the lower-priority ones into a single daily digest notification:
   - Copy: "You have {count} updates today. Tap to review."
   - Deep link: `rin://home`
   - Sent at a fixed time (default: 9:00 AM local time, or first quiet moment after).
3. **Per-contact muting**: users can mute notifications from a specific contact. Muted contacts do not trigger `contacts.enrichment`, `reminder.followup`, or `reminder.birthday` notifications. Security notifications (`security.access_request`) are NOT mutable -- they always fire.
4. **Notification coalescing**: if multiple notifications in the same thread arrive within 30 seconds, coalesce into a single notification with updated content. Example: three enrichment notifications become "3 contacts updated their profiles."
5. **Cool-down after denial**: if a user dismisses 3+ notifications from the same category within 24 hours without tapping any, backend reduces that category's frequency for 7 days.

### 8.3 Priority Hierarchy

When rate limits force suppression, notifications are preserved in this order (highest priority first):

1. Security (never suppressed)
2. Reminders (user-scheduled, never suppressed)
3. Profile alerts
4. Score updates
5. Contact updates
6. Premium insights

---

## 9) Notification Service Architecture

### 9.1 Backend Responsibilities

- Maintain per-user notification preference state.
- Enforce rate limits server-side (client cannot bypass).
- Compose notification payloads with correct deep links, thread IDs, and badge counts.
- Deliver via APNs with appropriate `apns-priority` (10 for immediate, 5 for batched).
- Track delivery status for analytics.

### 9.2 Client Responsibilities

- Register/unregister for push notifications.
- Handle notification presentation when app is in foreground (show in-app banner, not system notification).
- Process deep links from notification taps.
- Update badge counts on `NotificationService` shared state.
- Sync notification preferences to backend.
- Handle notification actions (approve/deny, done/snooze).

### 9.3 Foreground Notification Handling

When app is in foreground and a notification arrives:
- Do NOT show iOS system notification (suppress via `UNUserNotificationCenterDelegate`).
- Show in-app notification banner (top of screen, auto-dismisses after 4 seconds).
- In-app banner matches notification content and is tappable (same deep link).
- Security notifications show with `rin.brand.error` accent bar for urgency.

### 9.4 Notification Payload Structure

```json
{
  "aps": {
    "alert": {
      "title": "Rin Score",
      "body": "Your Rin Score changed: 72 to 75 (+3). Tap to see what improved.",
      "subtitle": null
    },
    "badge": 4,
    "sound": "score_update.caf",
    "thread-id": "score",
    "category": "SCORE",
    "interruption-level": "active",
    "relevance-score": 0.8
  },
  "rin": {
    "type": "score.updated",
    "deep_link": "rin://score",
    "profile_id": "primary",
    "profile_display_name": "Nan",
    "metadata": {
      "old_score": 72,
      "new_score": 75,
      "delta": 3
    }
  }
}
```

---

## 10) Accessibility

### 10.1 Notification Sounds

| Category | Sound | File | Duration |
|----------|-------|------|----------|
| SCORE | Subtle ascending tone | `score_update.caf` | < 2s |
| CONTACTS | Soft double tap | `contact_update.caf` | < 1s |
| SECURITY | Firm alert tone (distinct from others) | `security_alert.caf` | < 2s |
| PREMIUM | Same as CONTACTS | `contact_update.caf` | < 1s |
| REMINDER | Gentle chime | `reminder.caf` | < 2s |
| PROFILE | Same as CONTACTS | `contact_update.caf` | < 1s |
| Silent | None | nil | 0 |

- All custom sounds are under 30 seconds (iOS requirement).
- Users who set iOS system "Default" notification sound override custom sounds. This is expected.

### 10.2 Haptics

- Security notifications (time-sensitive): `.notification` type UINotificationFeedbackGenerator with `.warning` style.
- All other notifications: default system haptic.
- Respects iOS "System Haptics" setting. If disabled, no haptic feedback.

### 10.3 VoiceOver in Notification Center

- Notification title and body are read by VoiceOver as composed (standard iOS behavior).
- Quick action buttons have accessible labels:
  - "Approve" reads as "Approve access request".
  - "Deny" reads as "Deny access request".
  - "Done" reads as "Mark reminder as done".
  - "Snooze 1h" reads as "Snooze reminder for one hour".
- In-app notification banners are announced by VoiceOver with `.announcement` post.
- Badge counts: VoiceOver reads tab badges as "[Tab name], {count} notifications".

### 10.4 Dynamic Type

- In-app notification banner text supports Dynamic Type up to AX5.
- Banner height adapts to accommodate larger text sizes.

---

## 11) Events

All events follow the naming convention from Product Analytics Event Taxonomy V1 (section 3): `object_action`, lowercase, underscore-separated, past tense verbs.

### 11.1 Permission Events

| Event | Properties | Trigger |
|-------|-----------|---------|
| `notification_permission_prompted` | `source` (first_value/settings), `provisional` (bool) | Pre-permission screen shown |
| `notification_permission_granted` | `source`, `provisional` (bool) | User allowed notifications |
| `notification_permission_denied` | `source` | User denied notifications |
| `notification_permission_changed` | `old_state`, `new_state` | iOS permission state changed (e.g., user toggled in iOS Settings) |

### 11.2 Delivery Events

| Event | Properties | Trigger |
|-------|-----------|---------|
| `notification_sent` | `category`, `type`, `profile_id`, `is_batched` (bool) | Server sends notification |
| `notification_delivered` | `category`, `type`, `delivery_latency_ms` | APNs confirms delivery |
| `notification_suppressed` | `category`, `type`, `reason` (rate_limit/duplicate/digest/muted/preference_off) | Server suppresses notification |

### 11.3 Interaction Events

| Event | Properties | Trigger |
|-------|-----------|---------|
| `notification_tapped` | `category`, `type`, `deep_link`, `time_since_delivery_ms` | User taps notification |
| `notification_action_taken` | `category`, `type`, `action` (approve/deny/done/snooze/review) | User taps quick action |
| `notification_dismissed` | `category`, `type` | User swipes away notification |
| `notification_banner_shown` | `category`, `type` | In-app foreground banner displayed |
| `notification_banner_tapped` | `category`, `type` | User taps in-app banner |
| `notification_banner_dismissed` | `category`, `type` | In-app banner auto-dismisses or user swipes |

### 11.4 Preference Events

| Event | Properties | Trigger |
|-------|-----------|---------|
| `notification_preference_changed` | `category`, `old_state` (on/off), `new_state` (on/off) | User toggles category in Settings |
| `notification_contact_muted` | `contact_id` (hashed) | User mutes notifications from a contact |
| `notification_contact_unmuted` | `contact_id` (hashed) | User unmutes a contact |

### 11.5 Funnel: Permission to Engagement

```
notification_permission_prompted
  -> notification_permission_granted
  -> notification_sent (first)
  -> notification_tapped (first tap)
  -> [conversion action from deep link]
```

---

## 12) Open Decisions

1. **Provisional notifications**: whether to use `UNAuthorizationOptions.provisional` for silent trial delivery before requesting full permission. Pro: lower friction. Con: lower initial engagement with notifications.

2. **Daily digest time**: whether the daily digest notification fires at a fixed time (9:00 AM local) or adapts to user's typical app usage window. Fixed time is simpler; adaptive requires usage pattern modeling.

3. **Score notification deep link target**: whether `score.updated` should deep-link to SC1 (Score Home overview) or SC2 (Component Detail for the component that changed most). SC1 is simpler; SC2 is more actionable. See also Score Explanation Screen Spec V1 section 8, open decision 2.

4. **Birthday notification source**: whether birthday data comes only from device contacts (CNContact birthday field) or also from Rin profile data. Device-only is more reliable; Rin profiles may have self-reported birthdays that are less trustworthy.

5. **Notification sound customization**: whether to ship custom notification sounds per category (requires audio design) or use iOS default sounds in v1 and add custom sounds later. Custom sounds improve category recognition; default sounds reduce v1 scope.

6. **Shadow profile notification grouping**: whether notifications for different profiles should appear as separate notification groups in iOS notification center, or all under one "Rin" group with profile name in the title. Separate groups reveal that multiple profiles exist to anyone viewing the lock screen. See also Shadow Profile UX V1 section 14, open decision 4.
