# iOS Day-2+ Retention Loop Spec V1

## 1) Purpose

Define the retention mechanics that bring users back to Rin after onboarding. Rin is an episodic-use contact intelligence app, not a daily-engagement social feed. The north star metric is MAU-V (Monthly Active Users with Value Received), not DAU. The retention system is designed for weekly and biweekly return patterns with periodic daily spikes around actionable events.

This spec covers: return triggers by timeframe, value loops, smart home section lifecycle, notification cadence, lapsed user re-engagement, welcome-back state, anti-churn detection, and retention metrics.

Core constraint from Brand Narrative V1 section 3.2: "Every notification, every screen, every sentence must earn the user's time. No engagement farming. No dark patterns."

Companion docs:
- `docs/product/USER_JOURNEY_PLAN.md` (Journey 5: Ongoing Loop, Steps 15-16)
- `docs/product/IOS_INSTALL_TO_FIRST_VALUE_UX_V1.md` (first-value, magic moment section 5)
- `docs/product/IOS_HOME_TAB_SCREEN_SPEC_V1.md` (smart sections, steady state)
- `docs/product/IOS_NOTIFICATION_STRATEGY_V1.md` (notification catalog, rate limits)
- `docs/product/CONTACTS_IMPORT_SYNC_UX_V1.md` (ongoing sync lifecycle)
- `docs/product/IOS_SCORE_EXPLANATION_SCREEN_SPEC_V1.md` (score changes as return driver)
- `docs/product/IOS_CONTACT_NOTES_HISTORY_SPEC_V1.md` (notes, reminders, friend CRM loop)
- `docs/product/CIRCLE_MANAGEMENT_UX_V1.md` (circle maintenance nudges)
- `docs/analytics/KPI_HIERARCHY_V1.md` (D30 >15% retention target, MAU-V north star)
- `docs/plan/POST_LAUNCH_STABILIZATION_V1.md` (retention milestones)
- `docs/product/RIN_SCORE_V1.md` (score update cadence)
- `docs/design/BRAND_NARRATIVE_V1.md` (tone)
- `docs/design/IOS_DESIGN_TOKENS_V1.md` (visual foundation)

---

## 2) Retention Model

### 2.1 Episodic-Use Pattern

Rin's usage pattern is closer to a banking app or health tracker than a social feed. Users return when they have a reason, not out of habit. The retention system creates and communicates those reasons without manufacturing false urgency.

Expected return cadence:
- **Power users (10-15% of MAU)**: 3-5 opens per week. CRM note-takers, active circle managers, people in job transitions.
- **Regular users (40-50% of MAU)**: 1-2 opens per week. Check score, review dedup, respond to access requests.
- **Casual users (35-50% of MAU)**: 2-4 opens per month. Score curiosity, birthday reminders, periodic cleanup.

All three segments count as healthy retention. The system does not try to convert casual users into power users.

### 2.2 Value Delivery Model

```
Passive value (no app open required)
├── Background sync detects contact changes
├── Enrichment adds data the user didn't have
├── Dedup catches new duplicates from ongoing imports
├── Score recalculates daily
└── Reminders fire on schedule

Active value (app open required)
├── Review dedup suggestions
├── Explore score changes and component breakdown
├── Respond to access requests
├── Add/review notes and reminders
├── Adjust circle membership and access policies
└── Meeting prep: review contact before seeing them
```

Passive value is delivered whether the user opens the app or not. Active value is communicated through notifications and smart home sections that pull users back when they have something to act on.

---

## 3) Return Triggers by Timeframe

### 3.1 Day 1 (Same Day as Onboarding)

| Trigger | Condition | Mechanism | Priority |
|---------|-----------|-----------|----------|
| Pending dedup suggestions | User exited onboarding without reviewing all suggestions | Push notification: `contacts.dedup_ready` | High |
| First score calculated | Score batch completes for new user | Push notification: `score.updated` | Medium |
| Remaining cleanup cards | Smart section items unresolved from first session | Tab badge on Home (count of unreviewed items) | Medium |
| Profile incomplete | User skipped photo or username during onboarding | Smart section card on next open (not push) | Low |

Day 1 notifications are limited. The user chose to stop their first session. Respect that. One dedup reminder and one score notification maximum.

### 3.2 Day 2-7 (First Week)

| Trigger | Condition | Mechanism | Priority |
|---------|-----------|-----------|----------|
| Score change | First meaningful movement (>= +/-2 points) after initial calculation | Push: `score.updated` | Medium |
| New enrichment data | Contacts matched to Rin users; new fields available | Push: `contacts.enrichment` (batched) | Low |
| Circle organization nudge | User has not created any custom circles and has 20+ contacts | Smart section: Suggested Circle Assignments | Low |
| Profile completion | Photo or username still missing after 3 days | Smart section: profile completion card (in-app only, never push) | Low |
| New dedup suggestions | Background sync or delayed processing finds additional matches | Push: `contacts.dedup_ready` | High |

First-week goal: establish that Rin has ongoing value. The user should see at least one thing change without their input. Score movement and enrichment data are the strongest signals.

### 3.3 Day 7-30 (First Month)

| Trigger | Condition | Mechanism | Priority |
|---------|-----------|-----------|----------|
| Weekly score summary | Score changed by any amount since last viewed | Push: `score.updated` (max 1/day) | Medium |
| New sync results | Background delta sync detects added/changed/removed contacts | Smart section: Recently Added | Low |
| Circle maintenance suggestion | 3+ new contacts match metadata pattern of existing circle | Smart section: Suggested Circle Assignments | Low |
| Birthday reminder | Contact birthday within 7 days (auto-imported or user-added) | Push: `reminder.birthday` + smart section: Upcoming | Medium |
| Custom reminder fires | User-scheduled follow-up | Push: `reminder.followup` | Medium |
| Score milestone | Score crosses quality label boundary (e.g., Building to Good at 60) | Push: `score.milestone` | Medium |
| Who Viewed Me teaser | Premium: weekly viewer summary. Free: teaser count if applicable | Push: `premium.who_viewed` (premium only) | Low |

First-month goal: the user has returned at least 2-3 times and taken at least one intentional action (dedup, circle assignment, note, policy change). This establishes the habit loop.

### 3.4 Day 30+ (Ongoing)

| Trigger | Condition | Mechanism | Priority |
|---------|-----------|-----------|----------|
| Monthly enrichment digest | Enrichment updates accumulated over 30 days | Smart section: Enrichment Updates | Low |
| Score milestone | Score reaches new quality label | Push: `score.milestone` | Medium |
| Recurring reminders | Birthdays, monthly check-ins, user-set follow-ups | Push: `reminder.followup` / `reminder.birthday` | Medium |
| Annual contact review | User has been on Rin for 12 months | Smart section: "Review your network" card | Low |
| Seasonal prompt | January / start of quarter | Smart section: "Start of the year. Review your circles." | Low |
| New dedup from sync | Ongoing contact changes create new merge opportunities | Push: `contacts.dedup_ready` | High |
| Access request received | Someone requests access to user's Ask-protected field | Push: `security.access_request` (immediate) | High |
| Circle merge suggestion | Two circles have >70% overlap after organic growth | Smart section: circle merge suggestion card | Low |

Ongoing goal: maintain MAU-V >30% (public launch target per KPI Hierarchy V1). Every return delivers at least one value event.

### 3.5 Return Trigger Timeline

```
Day 0 (Onboarding)
│  ── First-value: dedup, enrichment, score calculating ──
│
Day 1
│  ── Push: dedup pending / score first calculated ──
│
Day 2-3
│  ── Push: first score change (if moved >=2) ──
│  ── Smart section: enrichment updates ──
│
Day 4-7
│  ── Smart section: circle suggestion nudge ──
│  ── Smart section: profile completion (if incomplete) ──
│  ── Push: new dedup from background sync ──
│
Day 7-14
│  ── Push: weekly score change ──
│  ── Push: birthday reminder (if applicable) ──
│  ── Smart section: new contacts from sync ──
│
Day 14-30
│  ── Push: score milestone (if crossed label boundary) ──
│  ── Smart section: circle maintenance suggestion ──
│  ── Push: custom reminders firing ──
│  ── Push: premium viewer summary (premium users) ──
│
Day 30+
│  ── Push: score updates (1/day max when >=2 movement) ──
│  ── Push: access requests (immediate) ──
│  ── Push: reminders (per user schedule) ──
│  ── Smart section: enrichment digest ──
│  ── Smart section: seasonal review prompts ──
```

---

## 4) Value Loops

Five distinct value loops drive returns. Each loop is self-contained and does not require the others to function. Users may engage with one, some, or all loops depending on their usage pattern.

### 4.1 Loop 1: Contact Intelligence (Passive)

**Mechanism**: Rin works in the background. The user's contact list gets cleaner and richer without effort.

```
Background sync detects contact changes
    → Dedup engine finds new duplicates
    → Enrichment adds data from Rin network
    → Score recalculates with new data
        → Notification surfaces what changed
            → User opens app to review
                → Takes action (merge, review, explore)
                    → Contact graph improves
                        → Next cycle has more to work with
```

**Return value**: "Rin is working for me even when I'm not using it."

**Key signals to user**: dedup suggestions, enrichment badges, "Recently Added" smart section, sync status on pull-to-refresh.

**MAU-V qualification**: `dedup_suggestion_shown`, `dedup_auto_merged`, `contact_sync_completed` where `updated > 0`.

### 4.2 Loop 2: Score Movement (Curiosity)

**Mechanism**: Daily score recalculation creates natural curiosity about what changed and why.

```
Daily score batch runs
    → Score changes by >=2 points
        → Push notification: "Your Rin Score changed: 72 to 75 (+3)"
            → User opens Score tab
                → Sees component breakdown
                    → Explores what drove the change
                        → May take action (verify email, organize contacts)
                            → Next score reflects improvement
```

**Return value**: "What changed? Why did my score go up or down?"

**Key signals to user**: score change notification, score change smart section card, sparkline trend, component bars.

**MAU-V qualification**: `score_updated`.

**Cadence alignment**: score recalculates daily, but notifications fire only when change is meaningful (>=2 points per Notification Strategy V1 section 3.2). Most users see 1-3 score changes per week during the first month (contact graph is still stabilizing), declining to 1-2 per month as the graph settles.

### 4.3 Loop 3: Access Control (Agency)

**Mechanism**: incoming access requests require a response. Life changes prompt policy review.

```
Contact taps "Request" on an Ask-protected field
    → Owner receives immediate push notification
        → Owner reviews request in Security Inbox
            → Approves or denies
                → Requester sees the result (if approved)
                    → Owner may review circle policies
                        → Adjusts access for relevant circles
```

**Return value**: "I'm in control of who sees what."

**Key signals to user**: access request notification (immediate, never rate-limited), Security Inbox badge, effective access preview on contact detail.

**MAU-V qualification**: `premium_feature_used` (for full access control features), counted via `policy.updated` and `access.request_approved`.

**Frequency**: event-driven. Increases as Rin network grows (more users, more Ask requests). Early stage: rare. Growth stage: primary engagement driver.

### 4.4 Loop 4: CRM / Notes (Personal Investment)

**Mechanism**: notes and reminders create personal investment in the contact graph. Each note adds private context that makes Rin more valuable over time.

```
User meets someone or has a conversation
    → Adds a note to the contact (quick-add via long-press)
        → Sets a follow-up reminder
            → Reminder fires on schedule
                → User opens contact timeline
                    → Reviews previous notes for context
                        → Takes the follow-up action
                            → Adds another note
                                → Investment deepens
```

**Return value**: "Rin remembers what I'd forget."

**Key signals to user**: Upcoming smart section, reminder push notifications, note search results, contact timeline.

**MAU-V qualification**: counted via `note.created`, `reminder.triggered` leading to app open.

**This is the daily-use loop**. Contact Notes and History Spec V1 identifies this as "the habit loop that brings users back daily." Power users (10-15% of MAU) engage with this loop 3-5 times per week.

### 4.5 Loop 5: Premium Curiosity (Monetization)

**Mechanism**: free users see teaser counts and gated features that demonstrate premium value.

```
Score tab shows "Who viewed your profile this week: 3 people"
    → User taps → premium paywall
        → User considers subscription
            → If subscribed: sees viewer list, enrichment alerts, full analysis
            → If not: remembers the count, returns next week to check again
```

**Return value**: "I wonder who's looking at me."

**Key signals to user**: viewer count teaser on Score tab (SC1 section 6.1 in Score Explanation Screen Spec V1), premium paywall, weekly `premium.who_viewed` notification (subscribers only).

**MAU-V qualification**: `premium_feature_used`.

**Retention mechanic for free users**: the teaser count is visible without subscribing. The number itself is the hook. "3 people viewed your profile" costs nothing to show and creates repeat curiosity.

### 4.6 Loop Interaction Model

```
                    ┌─────────────────────────┐
                    │   User Opens Rin App     │
                    └──────────┬──────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │   Loop 1    │  │   Loop 2    │  │   Loop 4    │
    │  Contact    │  │   Score     │  │  CRM/Notes  │
    │Intelligence │  │  Movement   │  │             │
    └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
           │                │                │
           │  improves      │  reflects      │  deepens
           │  contact data  │  graph health  │  investment
           │                │                │
           └────────────────┼────────────────┘
                            │
                   ┌────────▼────────┐
                   │   Contact Graph  │
                   │    Improves      │
                   └────────┬────────┘
                            │
              ┌─────────────┼─────────────┐
              │                           │
              ▼                           ▼
    ┌─────────────────┐         ┌─────────────────┐
    │    Loop 3       │         │    Loop 5        │
    │ Access Control  │         │ Premium Curiosity│
    │  (event-driven) │         │  (monetization)  │
    └─────────────────┘         └─────────────────┘
```

Loops 1, 2, and 4 are the primary retention drivers. Loop 3 activates as the network grows. Loop 5 is a monetization overlay that adds retention value without being required.

---

## 5) Smart Home Section Lifecycle

Smart sections on the Home tab (defined in IOS_HOME_TAB_SCREEN_SPEC_V1.md section 3) are the primary in-app mechanism for surfacing return value. This section defines how they cycle over time to keep the experience fresh without becoming stale or noisy.

### 5.1 Section Priority Order

When multiple smart sections are active, they display in fixed priority order (matching Home Tab Screen Spec V1 section 3.2):

| Priority | Section | Category | Rationale |
|----------|---------|----------|-----------|
| 1 | Needs Attention | Action required | Data integrity: dedup, conflicts, access requests degrade contact quality if ignored |
| 2 | Score Changed | New information | Quick glance, high engagement, auto-dismisses |
| 3 | Upcoming | Time-sensitive | Missing a birthday or reminder is worse than missing a suggestion |
| 4 | Recently Added | New information | Recency-relevant context from sync |
| 5 | Enrichment Updates | New information | Informational, no urgency |
| 6 | Suggested Circle Assignments | Suggestion | Organizational improvement, can wait |
| 7 | Profile Completion | Suggestion | Low urgency, nudge only |
| 8 | Welcome Back | Motivational | Summary card after lapsed return (see section 8) |
| 9 | Network Health | Motivational | Clean state acknowledgment, milestone celebration |

Maximum 3 visible sections at a time (per Home Tab Spec V1 section 3.3). Overflow sections accessible via "See N More Sections" link.

### 5.2 Section Lifecycle Rules

| Rule | Behavior |
|------|----------|
| Dismiss cooldown | Sections dismissed via swipe or "Hide for today" do not return for 7 days |
| Permanent hide | "Don't show this section" hides permanently, reversible from Settings > Home Sections |
| Auto-dismiss | Score Changed card auto-hides after 48 hours or after user taps it |
| Empty collapse | Sections with no items collapse to zero height (no empty placeholder) |
| Content refresh | Sections re-evaluate triggers on every app foreground and after every sync |

### 5.3 Clean State

When no smart sections qualify for display:

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
│ ...                                  │
└──────────────────────────────────────┘
```

The clean state IS the goal. No "All caught up" card, no motivational message, no confetti. Per Home Tab Spec V1 section 4.1: "Celebrating it with a card would be ironic."

The contact list is always visible and useful. Smart sections enhance it; they never replace it.

### 5.4 Section Generation Over Time

Even in steady state, the system generates new smart section content organically:

| Source | Sections generated | Frequency |
|--------|-------------------|-----------|
| Daily score batch | Score Changed card (if >=2 point change) | Daily |
| Background sync | Recently Added, Needs Attention (new dedup), Enrichment Updates | Per sync cycle (event-triggered + daily fallback) |
| Calendar proximity | Upcoming (birthdays, reminders within 7 days) | Rolling window |
| Circle pattern detection | Suggested Circle Assignments | After sync detects new contacts matching patterns |
| Access requests | Needs Attention (incoming requests) | Event-driven |

No artificial content generation. If nothing changed, nothing appears.

---

## 6) Re-Engagement Notification Cadence

### 6.1 Notification Catalog (Retention-Relevant Subset)

All notifications below are defined in IOS_NOTIFICATION_STRATEGY_V1.md section 3.2. This table adds retention-specific context: when each notification serves as a return trigger and its expected frequency over the user lifecycle.

| Notification | Category | Max Frequency | Condition | Return Priority | Lifecycle Phase |
|-------------|----------|---------------|-----------|-----------------|-----------------|
| Score change | SCORE | 1/day | Score moved >=2 points | Medium | All phases |
| Score milestone | SCORE | 1/event | Score crossed label boundary | Medium | First month, then rare |
| Dedup ready | CONTACTS | 1/day | New merge suggestions | High | Heavy in first week, then periodic |
| Enrichment update | CONTACTS | 3/day (batched) | Contact matched Rin user, new fields | Low | Grows with network |
| Sync conflict | CONTACTS | 1/day | Field changed on device and in Rin | High | Periodic |
| Access request | SECURITY | Immediate, no limit | Someone requests an Ask field | High | Grows with network |
| Birthday reminder | REMINDER | 1 per event | Contact birthday today | Medium | Annual per contact |
| Custom reminder | REMINDER | Per user schedule | User-set follow-up fires | Medium | Grows with usage |
| Weekly viewer summary | PREMIUM | 1/week | Premium subscriber, has viewers | Low | Ongoing for subscribers |
| Profile incomplete | (in-app only) | 1/week, max 3 total | Missing photo or username | Low | First 3 weeks only |

### 6.2 Daily Notification Budget

**Hard cap: never more than 3 non-security notifications per day across all categories.**

Security notifications (`security.access_request`, `security.new_signin`, `security.suspicious_activity`) are exempt from the daily cap. They are time-sensitive and always delivered immediately.

When the daily cap would be exceeded, notifications are suppressed in reverse priority order:

1. Security (never suppressed)
2. Reminders (user-scheduled, suppress only as last resort)
3. Score updates
4. Dedup ready
5. Enrichment updates (first to suppress)

Suppressed notifications are not lost. Their content is reflected in smart sections on next app open.

### 6.3 Anti-Annoyance Rules

Per IOS_Notification_Strategy_V1.md section 8.2, with retention-specific additions:

| Rule | Behavior |
|------|----------|
| Daily digest fallback | If >5 non-security notifications would fire in a day, batch into one digest at 9:00 AM local: "You have {count} updates. Tap to review." |
| Coalescing | Multiple notifications in the same category within 30 seconds merge into one |
| Cool-down on dismissal | If user dismisses 3+ notifications from same category in 24 hours without tapping, reduce that category's frequency for 7 days |
| No duplicate content | Same notification type with same content suppressed within 1 hour |
| Quiet mode | If user has not opened app in 14+ days, reduce to maximum 1 notification per week (see section 7) |

### 6.4 Notification Copy Standards

Per Brand Narrative V1 section 6.5, all notification copy:
- States facts, not feelings. No "Great news" or "Yay."
- Delivers concrete information. "3 possible duplicates found" not "Check out what's new."
- No re-engagement phrasing. No "We miss you," "Come back," or "Don't miss out."
- No congratulatory messages. No "You hit 100 contacts."
- No exclamation marks.

Copy examples for retention-relevant notifications:

| Notification | Copy |
|-------------|------|
| Score up | "Your Rin Score changed: 72 to 75 (+3). Tap to see what improved." |
| Score down | "Your Rin Score changed: 75 to 71 (-4). Tap to see what shifted." |
| Score milestone | "Your Rin Score reached Good (60). Your network is growing stronger." |
| Dedup ready | "3 possible duplicates found. Review and clean your contacts." |
| Enrichment (single) | "[Name] updated their profile. New info available." |
| Enrichment (batch) | "[Name] and 4 others updated their profiles. New info available." |
| Birthday | "[Name]'s birthday is today." |
| Lapsed summary (14d) | "12 enrichment updates and 2 dedup suggestions since your last visit. Score: 75." |
| Lapsed summary (30d) | "Your contacts have been syncing in the background. 5 new enrichments available." |

---

## 7) Lapsed User Re-Engagement

### 7.1 Inactivity Tiers

Rin is episodic. Not opening the app for a week is normal. The re-engagement system distinguishes between normal usage gaps and genuine lapsing.

| Days inactive | Classification | System response |
|---------------|---------------|-----------------|
| 0-7 | Normal | Standard notification cadence. No special treatment. |
| 7-13 | Extended gap | Standard notifications continue. No re-engagement messaging. |
| 14-29 | Lapsed | One summary notification with accumulated value. Enter quiet mode (max 1 notification/week). |
| 30-59 | Deeply lapsed | One value-reminder notification. Continue quiet mode. |
| 60+ | Dormant | Stop push notifications entirely. Re-engage only via email if user opted in to email communications. |

### 7.2 Lapsed Notifications

**14-day notification** (one-time):
- Copy: "{N} enrichment updates and {N} dedup suggestions since your last visit. Score: {score}."
- Deep link: `rin://home`
- Category: CONTACTS
- Tone: factual summary of accumulated value. No guilt, no urgency.

**30-day notification** (one-time):
- Copy: "Your contacts have been syncing in the background. {N} new enrichments available."
- Deep link: `rin://home`
- Category: CONTACTS
- Tone: reminder that passive value continues. Not a plea to return.

**60+ days**: no notification. If the user has email communications enabled and has not unsubscribed, a single email may be sent (email strategy is out of scope for this spec). Push notifications stop entirely to avoid becoming notification noise on a phone the user no longer associates with Rin.

### 7.3 Quiet Mode

Activated when user has not opened the app in 14+ days.

| Behavior | Standard mode | Quiet mode |
|----------|--------------|------------|
| Max non-security notifications/day | 3 | 0 (except the scheduled weekly summary) |
| Max notifications/week | ~15 (3/day cap) | 1 |
| Notification types allowed | All | Lapsed summary only (plus security, which is never suppressed) |
| Score change notifications | Enabled | Suppressed |
| Dedup notifications | Enabled | Suppressed |
| Enrichment notifications | Enabled | Suppressed |
| Reminders | Enabled | Still fire (user-scheduled commitments are honored) |

Quiet mode deactivates automatically when the user opens the app.

---

## 8) Welcome Back State

### 8.1 Trigger

The Welcome Back summary card appears when the user opens Rin after 7 or more days of inactivity. It surfaces at the top of the smart sections area on the Home tab, above all other sections.

### 8.2 Content

The card aggregates changes that occurred while the user was away:

```
┌──────────────────────────────────────┐
│                                      │
│  While you were away                 │
│                                      │
│  Score: 72 → 75 (+3)                │
│  5 enrichment updates               │
│  2 dedup suggestions                │
│  1 birthday this week               │
│                                      │
│  [Review Changes]         [Dismiss]  │
│                                      │
└──────────────────────────────────────┘
```

**Content rules**:
- Only include lines with non-zero values. If score did not change, omit the score line.
- If no changes occurred while away (rare but possible), do not show the Welcome Back card.
- Maximum 5 content lines. If more categories have updates, show the top 5 by priority and append "and {N} more updates."
- Copy uses Brand Narrative V1 tone: factual, no exclamation marks, no "Welcome back" phrasing (despite the internal name of this state).

**Content line priority** (most important first):
1. Score change (delta + direction)
2. Dedup suggestions count
3. Access requests pending
4. Enrichment updates count
5. Birthdays this week
6. Custom reminders fired while away
7. New contacts from sync

### 8.3 Visual Spec

| Element | Token | Value |
|---------|-------|-------|
| Card background | `rin.bg.secondary` | Grouped section background |
| Card border | `rin.border.default` | Standard card border |
| Corner radius | `rin.radius.lg` | 12pt |
| Padding | `rin.space.base` | 16pt internal |
| Title ("While you were away") | `rin.type.title3` (20pt Semibold) | Card title |
| Content lines | `rin.type.body` (17pt Regular) | Body text |
| Score delta (positive) | `rin.score.good` or appropriate tier color | Delta colored by direction |
| Score delta (negative) | `rin.brand.warning` | Amber for decline |
| "Review Changes" button | `PrimaryButton` | `rin.brand.primary` background |
| "Dismiss" button | `SecondaryButton` | Text-only, `rin.text.secondary` |

### 8.4 Interactions

| Action | Behavior |
|--------|----------|
| Tap "Review Changes" | Dismiss the Welcome Back card. Scroll to the first active smart section below. If score changed, switch to Score tab first. |
| Tap "Dismiss" | Card animates out (250ms, `.easeInOut`). Normal Home tab state below is revealed. |
| Swipe left on card | Same as Dismiss. |
| Ignore (scroll past) | Card remains until explicitly dismissed or until the user's next session (7+ days later). Auto-dismisses after 48 hours. |

### 8.5 Welcome Back vs Smart Sections

The Welcome Back card is a summary overlay, not a replacement for smart sections. After dismissing the Welcome Back card, the user sees the normal smart section stack (Needs Attention, Score Changed, Upcoming, etc.) populated with the individual items referenced in the summary.

---

## 9) Anti-Churn Signals

### 9.1 At-Risk Indicators

The backend monitors per-user signals that correlate with churn risk. These signals are used to trigger appropriate (never aggressive) re-engagement.

| Signal | Detection | Risk level | Response |
|--------|-----------|------------|----------|
| No app open in 14 days | Server-side: last `app_opened` timestamp | Moderate | Send lapsed summary notification (section 7.2). Enter quiet mode. |
| Score declining 3+ consecutive calculations | Score service: compare last 3 daily batches | Low | Score change notification with "Tap to see what shifted" copy. No special treatment beyond standard notification. |
| No intentional action in 30 days | No events: `dedup_suggestion_accepted`, `circle.member_added`, `policy.field_changed`, `note.created`, `access.request_approved` | Moderate | Send value-reminder notification (section 7.2). |
| Notification permission revoked | iOS callback: `UNAuthorizationStatus` changed to `.denied` | High | No push re-engagement possible. In-app: when user next opens, show contextual re-prompt only if they attempt an action that benefits from notifications (per Notification Strategy V1 section 4.3). |
| Contacts permission revoked | `CNAuthorizationStatus` changed to `.denied` | High | No sync, enrichment, or dedup possible. On next open: contextual re-prompt when user interacts with contact-dependent features (per Contacts Import Sync UX V1 section 9.2). |
| Dedup suggestions accumulating without review | 10+ unreviewed suggestions for 14+ days | Low | One push notification reminding of pending suggestions. Smart section badge persists. |
| All smart sections permanently hidden | User disabled all section types via Settings | Low | No smart sections appear. Contact list is the full experience. This is a valid user choice; do not attempt to override it. |

### 9.2 Response Principles

- Never aggressive. If a user is leaving, nagging accelerates departure.
- Never guilt-based. No "We miss you" or "Your network needs you."
- Factual only. "12 enrichment updates available" not "Don't miss out on updates."
- Respect user choices. If they revoked permissions or disabled notifications, those are decisions, not mistakes to correct.
- One chance per tier. Each inactivity tier (14-day, 30-day) sends at most one re-engagement notification. No repeated attempts at the same tier.

---

## 10) Metrics

### 10.1 Retention Cohort Metrics

| Metric | Definition | Target | Source |
|--------|-----------|--------|--------|
| D1 retention | % of users who open app on day 1 after signup | >30% | Post-Launch Stabilization V1 |
| D7 retention | % of users who return within 7 days of signup | >20% | Post-Launch Stabilization V1 |
| D30 retention | % of users who return within 30 days of signup | >15% | KPI Hierarchy V1 (guardrail) |
| D60 retention | % of users who return within 60 days | >10% | Tracked, no target set |
| D90 retention | % of users who return within 90 days | >8% | Tracked, no target set |

### 10.2 North Star Metric

**MAU-V (Monthly Active Users with Value Received)**: distinct users who received at least one value event in the trailing 30 days. See KPI Hierarchy V1 section 2 for full definition.

Value events (any one qualifies):
- `dedup_suggestion_shown`
- `dedup_auto_merged`
- `score_updated`
- `contact_sync_completed` where `updated > 0`
- `premium_feature_used`

Target progression: >80% (Stage 1, 50 users) down to >30% (public launch).

### 10.3 Return Behavior Metrics

| Metric | Definition | Purpose |
|--------|-----------|---------|
| Return frequency distribution | Histogram of days between consecutive app opens per user | Understand whether users are daily, weekly, or monthly returners |
| Notification-to-open conversion rate | % of notifications that result in an app open within 1 hour, by category | Measure notification effectiveness per type |
| Smart section engagement rate | % of visible smart sections that receive a tap or action, by section type | Measure section value; low engagement = candidate for removal |
| Value loop attribution | Which loop (1-5) was the primary driver for each return session | Understand what brings users back; invest in high-attribution loops |
| Welcome Back card engagement | % of Welcome Back cards that result in "Review Changes" tap vs dismiss | Measure whether the summary format is useful |
| Time to first action on return | Seconds from app open to first intentional action (dedup, note, policy change) | Measure activation friction for returning users |
| Lapsed recovery rate | % of 14-day lapsed users who return within 30 days | Measure re-engagement effectiveness |

### 10.4 Value Loop Attribution

To attribute returns to specific value loops, the system tracks the entry path:

| Entry path | Attributed loop |
|-----------|----------------|
| Tapped `score.updated` or `score.milestone` notification | Loop 2: Score Movement |
| Tapped `contacts.dedup_ready` or `contacts.enrichment` notification | Loop 1: Contact Intelligence |
| Tapped `security.access_request` notification | Loop 3: Access Control |
| Tapped `reminder.followup` or `reminder.birthday` notification | Loop 4: CRM / Notes |
| Tapped `premium.who_viewed` notification | Loop 5: Premium Curiosity |
| Organic open (no notification attribution) | Unattributed (track separately) |

---

## 11) Events

All events follow the naming convention from Product Analytics Event Taxonomy V1: `object.action`, lowercase, dot-separated.

### 11.1 Retention Lifecycle Events

| Event | Properties | Trigger |
|-------|-----------|---------|
| `retention.app_opened` | `days_since_last_open`, `entry_source` (notification / organic / deep_link), `notification_category` (if from notification), `is_lapsed` (bool, true if >=14 days) | App enters foreground |
| `retention.welcome_back_shown` | `days_since_last_open`, `score_delta`, `enrichment_count`, `dedup_count`, `birthday_count`, `reminder_count`, `content_lines_shown` | Welcome Back card rendered |
| `retention.welcome_back_tapped` | `action` (review_changes / dismiss), `time_visible_ms` | User interacts with Welcome Back card |
| `retention.smart_section_engaged` | `section_type` (needs_attention / score_changed / upcoming / recently_added / enrichment / circle_suggestion / profile_completion / welcome_back), `action` (tap / expand / dismiss / see_all) | User interacts with any smart section |
| `retention.notification_opened` | `category` (score / contacts / security / premium / reminder / profile), `type` (specific notification type from catalog), `time_since_delivery_ms`, `days_since_last_open` | User taps a notification |
| `retention.lapsed_reengaged` | `days_inactive`, `reengagement_type` (14d_summary / 30d_reminder / organic), `entry_source` | Lapsed user (14+ days) returns |
| `retention.quiet_mode_entered` | `days_inactive`, `last_notification_category` | User crosses 14-day inactivity threshold |
| `retention.quiet_mode_exited` | `days_in_quiet_mode` | Lapsed user opens app, exiting quiet mode |
| `retention.value_event_delivered` | `event_type` (dedup_shown / auto_merged / score_updated / sync_completed / premium_used), `user_was_active` (bool, app was open) | Any MAU-V qualifying event occurs |
| `retention.churn_signal_detected` | `signal_type` (14d_inactive / score_declining / no_action_30d / notification_revoked / contacts_revoked / dedup_accumulating), `user_age_days` | Anti-churn signal triggered |

### 11.2 Event Volume Expectations

| Event | Expected volume per user per month |
|-------|-----------------------------------|
| `retention.app_opened` | 4-20 (varies by user segment) |
| `retention.welcome_back_shown` | 0-2 (only after 7+ day gaps) |
| `retention.smart_section_engaged` | 2-10 |
| `retention.notification_opened` | 1-8 |
| `retention.value_event_delivered` | 5-30 (background events included) |
| `retention.churn_signal_detected` | 0-1 |

---

## 12) Accessibility

### 12.1 Welcome Back Card

| Element | VoiceOver label | VoiceOver hint |
|---------|----------------|----------------|
| Card container | "While you were away summary" | "Shows changes since your last visit" |
| Score delta line | "Score changed from [old] to [new], [direction] [delta] points" | (none) |
| Enrichment line | "[count] enrichment updates" | (none) |
| Dedup line | "[count] dedup suggestions" | (none) |
| Birthday line | "[count] birthdays this week" | (none) |
| "Review Changes" button | "Review changes" | "Shows the details of what changed" |
| "Dismiss" button | "Dismiss summary" | "Hides this summary card" |

### 12.2 Smart Sections

Per IOS_Home_Tab_Screen_Spec_V1.md section 11. All smart sections are navigable with assistive technology. Section headers announce type and item count. Collapse/expand state is announced.

### 12.3 Notifications

Per IOS_Notification_Strategy_V1.md section 10. All notification titles and bodies are read by VoiceOver. Quick action buttons have expanded accessible labels.

### 12.4 Dynamic Type

- Welcome Back card scales with Dynamic Type up to AX5.
- Content lines stack vertically at large sizes.
- Buttons remain tappable at all sizes (minimum 44pt touch target).

### 12.5 Reduce Motion

- Welcome Back card dismiss uses fade instead of slide when "Reduce Motion" is enabled.
- Smart section transitions are instant (no spring animation).

---

## 13) Open Decisions

1. **Welcome Back threshold**: should the Welcome Back card trigger after 7 days (current spec) or 14 days? Seven days catches more users but may feel premature for an episodic app where weekly gaps are normal. Fourteen days means only genuinely lapsed users see it. Needs A/B testing.

2. **Score notification deep link**: should `score.updated` notifications deep-link to SC1 (Score Home overview) or SC2 (Component Detail for the component that changed most)? SC1 is simpler and lets the user choose what to explore. SC2 is more actionable but may confuse users who want the full picture. Also noted as open decision in Score Explanation Screen Spec V1 section 8.

3. **Seasonal prompts**: should Rin show seasonal review prompts ("Start of the year. Review your circles.") or does this violate the "no artificial engagement" principle? The prompt has legitimate value (annual network review) but no user-initiated trigger. Could be limited to users who have been on Rin for 6+ months.

4. **Quiet mode notification type**: in quiet mode (14+ days inactive), should the single weekly notification be the lapsed summary (accumulated value) or the highest-priority pending notification (e.g., an unreviewed dedup suggestion)? Summary gives a holistic reason to return; single notification gives a specific action.

5. **Premium teaser for free users**: should the "Who viewed your profile: 3 people" teaser count be visible on the Score tab for free users, or only as a paywall preview? Visible teaser creates Loop 5 return value for free users but may feel like a dark pattern if overemphasized. Current Score Explanation Screen Spec V1 section 6.1 shows it on SC1 with paywall on tap.

6. **Value loop attribution accuracy**: organic opens (no notification) cannot be attributed to a specific loop. Should the system infer attribution from the user's first action after opening (e.g., if they immediately check score, attribute to Loop 2)? Inference is noisy but better than "unattributed." Alternative: accept that 40-60% of returns will be unattributed and focus on notification-driven attribution.
