# iOS Error and Empty State Catalog V1

## 1) Purpose

Single authoritative reference for every error, empty, loading, and degraded state in the Rin iOS app. This catalog ensures consistent UX language, prevents ad-hoc error handling during implementation, and provides exact copy for every state a user can encounter.

Every error message, empty state illustration, loading treatment, and degraded-mode fallback in the app must trace back to an entry in this catalog. If a state is not listed here, it does not ship without adding it here first.

Companion docs:
- `docs/product/IOS_ONBOARDING_SCREEN_SPEC_V1.md` (onboarding screens, global state variants)
- `docs/product/CONTACTS_IMPORT_SYNC_UX_V1.md` (import, sync, dedup, enrichment)
- `docs/product/IOS_HOME_TAB_SCREEN_SPEC_V1.md` (home tab layout, smart sections, empty states)
- `docs/product/IOS_SEARCH_DISCOVERY_SCREEN_SPEC_V1.md` (search states)
- `docs/product/IOS_SCORE_EXPLANATION_SCREEN_SPEC_V1.md` (score states)
- `docs/product/IOS_PROFILE_CIRCLE_SCREEN_SPEC_V1.md` (profile/circle states)
- `docs/product/IOS_CONTACT_NOTES_HISTORY_SPEC_V1.md` (notes/timeline/reminder states)
- `docs/product/SHADOW_PROFILE_UX_V1.md` (shadow profile states)
- `docs/design/IOS_DESIGN_TOKENS_V1.md` (color tokens, typography, component inventory)
- `docs/design/BRAND_NARRATIVE_V1.md` (tone, voice, banned words, copy principles)

---

## 2) Copy Principles

All copy in this catalog follows the Brand Narrative V1 voice principles. These rules override any developer instinct about error wording.

| Principle | Rule | Example |
|-----------|------|---------|
| Calm, not alarming | State the situation. No exclamation marks. No "ERROR" labels. | "Sync couldn't complete" not "SYNC ERROR!" |
| Actionable | Always offer a next step when one exists. If no user action is possible, say what the system will do. | "Will retry automatically" or "Pull to retry" |
| Brief | One line primary copy, one line secondary max. | Primary: "You're offline." Secondary: "Showing cached data." |
| No jargon | No error codes, HTTP status codes, or technical terms. | "Something went wrong on our end" not "Server returned 503" |
| No banned words | Per BRAND_NARRATIVE_V1 section 7.2: no "Oops," "Uh oh," "Whoops," "Please," or exclamation marks. | "That code didn't work. Try again." not "Oops! Please try again!" |
| Positive framing | Empty states use achievement language when things are clean. Motivating, not guilt-tripping. | "All caught up" not "Nothing to see here" |
| State facts | Per voice principle 5.2: state what happened, what it means, what to do next. Don't narrate feelings. | "Import interrupted. 847 of 1,247 imported." not "We're sorry your import was interrupted." |
| No first-person | Rin does not say "I" or "We found." Use impersonal phrasing. | "12 duplicates found" not "We found 12 duplicates" |

---

## 3) Global Error States

These states can appear on any screen. They are handled at the app level and layer on top of screen-specific content.

### 3.1 Network Offline

| Property | Value |
|----------|-------|
| **ID** | `ERR-GLOBAL-OFFLINE` |
| **Detection** | `NWPathMonitor` via Network framework. Fires on path status change to `.unsatisfied`. |
| **Component** | `StatusBanner` (info variant) |
| **Placement** | Persistent banner, top of screen below navigation bar. Pushes content down. |
| **Icon** | SF Symbol `wifi.slash` |
| **Primary copy** | `You're offline.` |
| **Secondary copy** | `Showing cached data.` |
| **Color** | Background: `rin.bg.secondary`. Text: `rin.text.primary`. Icon: `rin.text.secondary`. |
| **Actions** | None. Banner is informational. |
| **Dismiss** | Auto-dismisses when connectivity returns. Brief "Back online" confirmation (1.5s) before removal. |
| **Behavior** | App remains fully functional with cached SwiftData. Write operations (note creation, circle changes, contact edits) queued for sync. Server search disabled; local search only. |
| **VoiceOver** | "Offline. Showing cached data." Announced once on appearance. |

### 3.2 Server Error (5xx)

| Property | Value |
|----------|-------|
| **ID** | `ERR-GLOBAL-SERVER` |
| **Detection** | HTTP response status 500-599 from any API call. |
| **Component** | Context-dependent: `StatusBanner` (warning variant) for non-blocking errors; `EmptyStateView` for full-screen blocking errors. |
| **Placement — inline** | Banner below navigation bar when the failed request was a background refresh, enrichment update, or non-critical fetch. |
| **Placement — full-screen** | Centered in content area when the failed request was the primary content load (e.g., first load of Score tab, first load of timeline). |
| **Icon** | SF Symbol `exclamationmark.triangle` |
| **Primary copy** | `Something went wrong on our end.` |
| **Secondary copy** | `Try again in a moment.` |
| **Action** | `Retry` button (primary style). |
| **Color** | Icon: `rin.brand.warning`. Text: `rin.text.primary`. |
| **Retry behavior** | Tap Retry re-issues the failed request. Button shows inline spinner while retrying. If retry fails, copy updates to: `Still having trouble. Try again later.` |
| **VoiceOver** | "Error. Something went wrong on our end. Retry button available." |

### 3.3 Session Expired (401)

| Property | Value |
|----------|-------|
| **ID** | `ERR-GLOBAL-SESSION` |
| **Detection** | HTTP 401 response. Token refresh fails. |
| **Component** | Full-screen overlay (blocks all interaction). |
| **Placement** | Covers entire app content. Tab bar hidden. |
| **Icon** | SF Symbol `lock.circle` |
| **Primary copy** | `Your session has expired.` |
| **Secondary copy** | `Verify your phone to continue.` |
| **Action** | `Verify` button. Navigates to OTP flow with phone number pre-filled from stored credentials. |
| **Dismiss** | No dismiss option. User must re-verify. |
| **Behavior** | All background operations paused. No data loss — local cache intact. After successful OTP, overlay dismisses and app resumes from previous state. |
| **VoiceOver** | "Session expired. Verify your phone to continue. Verify button." |

### 3.4 Force Update Required

| Property | Value |
|----------|-------|
| **ID** | `ERR-GLOBAL-FORCE-UPDATE` |
| **Detection** | Server response includes `minimum_app_version` header exceeding current build. Checked on every API call. |
| **Component** | Full-screen blocking modal. |
| **Placement** | Covers entire app. No navigation possible. |
| **Icon** | SF Symbol `arrow.down.circle` |
| **Primary copy** | `A new version of Rin is required.` |
| **Secondary copy** | `Update to continue.` |
| **Action** | `Update` button. Opens App Store deep link to Rin listing. |
| **Dismiss** | No dismiss. No skip. App is non-functional until updated. |
| **VoiceOver** | "Update required. A new version of Rin is required. Update button." |

### 3.5 Rate Limited (429)

| Property | Value |
|----------|-------|
| **ID** | `ERR-GLOBAL-RATE-LIMIT` |
| **Detection** | HTTP 429 response. `Retry-After` header parsed for cooldown duration. |
| **Component** | Inline error below the triggering action (not a banner). |
| **Placement** | Appears directly below the button or input that triggered the rate limit. |
| **Icon** | SF Symbol `clock` |
| **Primary copy** | `Too many requests.` |
| **Secondary copy** | `Try again in [N] seconds.` (live countdown timer if `Retry-After` header present) |
| **Action** | Auto-retry after cooldown. Button re-enables automatically. |
| **Color** | Text: `rin.brand.warning`. Timer: `rin.text.secondary`. |
| **VoiceOver** | "Rate limited. Try again in [N] seconds." Timer updates announced every 10 seconds. |

### 3.6 No Internet on First Launch

| Property | Value |
|----------|-------|
| **ID** | `ERR-GLOBAL-NO-INTERNET-FIRST-LAUNCH` |
| **Detection** | `NWPathMonitor` reports `.unsatisfied` during onboarding (before any cache exists). |
| **Component** | `EmptyStateView` (full-screen). |
| **Placement** | Replaces onboarding screen content. |
| **Icon** | SF Symbol `wifi.exclamationmark` |
| **Primary copy** | `No internet connection.` |
| **Secondary copy** | `Rin needs a connection to get started. Connect and try again.` |
| **Action** | `Try Again` button. Re-checks connectivity. |
| **VoiceOver** | "No internet connection. Connect and try again. Try Again button." |

---

## 4) Per-Screen Empty States

### 4.1 Home Tab

| State ID | Condition | Icon | Primary Copy | Secondary Copy | CTA | Component | Notes |
|----------|-----------|------|-------------|---------------|-----|-----------|-------|
| `EMPTY-HOME-NO-CONTACTS-DENIED` | Contacts permission denied AND zero manual contacts | `person.3` (56pt, `rin.text.tertiary`) | `Import your contacts to get started with Rin` | `Rin finds duplicates, enriches info, and helps you organize.` | `Import Contacts` (triggers permission re-prompt) | `EmptyStateView` | Per Home Tab Spec 6.1. Also shows hint: "or add contacts manually with the + button above" |
| `EMPTY-HOME-SYNC-PENDING` | Permission granted, initial sync not complete | Spinner (`ProgressView`) | `Importing your contacts...` | `This usually takes a few seconds.` | None | Inline spinner | If >15s, append: `Taking a bit longer for large contact lists.` Per Home Tab Spec 6.2. |
| `EMPTY-HOME-ALL-REVIEWED` | All smart sections cleared, contacts exist | None | None | None | None | N/A | Smart section area collapses to zero height. Contact list is primary content. Clean state IS the goal. Per Home Tab Spec 4.1 — no placeholder card, no celebration UI. |
| `EMPTY-HOME-SEARCH-NO-RESULTS` | Search active, no contacts match query | `magnifyingglass` | `No contacts found` | `Try a different search term` | `Add Contact Manually` | `EmptyStateView` | Per Search Spec 4.2. Delegates to search spec. |

### 4.2 Circles Tab

| State ID | Condition | Icon | Primary Copy | Secondary Copy | CTA | Component |
|----------|-----------|------|-------------|---------------|-----|-----------|
| `EMPTY-CIRCLES-NO-CUSTOM` | No user-created circles exist. Mandatory and prepopulated circles still shown. | `circle.grid.2x2` | `Create your first circle to organize contacts` | `Circles let you group contacts and control what they can see.` | `Create Circle` | `EmptyStateView` inside custom circles section |
| `EMPTY-CIRCLES-DETAIL-NO-MEMBERS` | A circle has zero members | `person.badge.plus` | `This circle has no members yet.` | `Add contacts to manage their access together.` | `Add Members` | `EmptyStateView` within C2 (Circle Detail) |
| `EMPTY-CIRCLES-NO-PENDING-REQUESTS` | Circle detail, pending access requests section empty | None | `No pending requests` | None | None | Inline text, `rin.text.secondary` |

### 4.3 Score Tab

| State ID | Condition | Icon | Primary Copy | Secondary Copy | CTA | Component |
|----------|-----------|------|-------------|---------------|-----|-----------|
| `EMPTY-SCORE-NOT-CALCULATED` | First day, no score data exists | `chart.bar.xaxis` | `Your score is being calculated.` | `Check back tomorrow. Rin Score measures your network strength across quality, position, stability, and trust.` | `Learn How Scoring Works` (navigates to SC3) | `EmptyStateView` |
| `STATE-SCORE-STALE` | Score >24h old | None | Score displayed normally | `Estimated` badge in `rin.brand.warning` color, muted color palette on score ring | None | Score ring with `Estimated` badge overlay |
| `EMPTY-SCORE-HISTORY-INSUFFICIENT` | Score history <7 days | `chart.xyaxis.line` | `Your score history is building.` | `Check back in a few days for your trend.` | None | `EmptyStateView` within SC4 (Score History) |
| `EMPTY-SCORE-COMPONENT-NO-DATA` | Individual component has zero data points | None | Muted bar with `--` instead of percentage | `Not enough data for this component yet.` | None | Component bar in muted `rin.text.tertiary` color |

### 4.4 Profile Tab

| State ID | Condition | Icon | Primary Copy | Secondary Copy | CTA | Component |
|----------|-----------|------|-------------|---------------|-----|-----------|
| `EMPTY-PROFILE-NO-SHADOWS` | User has only primary profile | None | "Your Profiles" section shows primary profile card only | None | `Create New Profile` | Inline CTA below primary profile card in P1 |
| `EMPTY-PROFILE-SECURITY-INBOX` | Security inbox has no items | `shield.checkmark` | `All clear.` | `No security items need your attention.` | None | `EmptyStateView` |
| `STATE-PROFILE-FREE-TIER` | User has no premium subscription | None | Premium row shows `Free` label in `rin.text.secondary` | None | None | Inline label on Premium row in P1 |

### 4.5 Contact Detail

| State ID | Condition | Icon | Primary Copy | Secondary Copy | CTA | Component |
|----------|-----------|------|-------------|---------------|-----|-----------|
| `EMPTY-CONTACT-NO-NOTES` | Contact has zero user-created notes | `square.and.pencil` | `No notes yet.` | `Add one to remember context about this person.` | `Add Note` (opens N3) | Inline in Notes section of contact detail |
| `EMPTY-CONTACT-NO-REMINDERS` | Contact has no active or upcoming reminders | None | Section hidden entirely | N/A | N/A | Upcoming Reminders section not rendered |
| `EMPTY-CONTACT-TIMELINE-EMPTY` | Timeline has no notes and no system events | `note.text` | `No history yet.` | `Add your first note.` | `+` FAB prominent | `EmptyStateView` in N2 |
| `EMPTY-CONTACT-TIMELINE-NOTES-ONLY` | Timeline has system events but no user notes | None | System events shown | `Add a note about [Name]` prompt above first event | `+` FAB | Inline prompt |
| `ERR-CONTACT-NOT-FOUND` | Deep link to contact ID that does not exist | `person.slash` | `Contact not found.` | `It may have been deleted or merged.` | `Go Back` | `EmptyStateView` pushed onto navigation stack. Per Home Tab Spec 8.1. |

### 4.6 Contact Timeline (N2)

| State ID | Condition | Icon | Primary Copy | Secondary Copy | CTA | Component |
|----------|-----------|------|-------------|---------------|-----|-----------|
| `ERR-TIMELINE-LOAD-FAILED` | Server error loading timeline entries | `exclamationmark.triangle` | `Could not load timeline.` | `Pull to retry.` | Pull-to-refresh | Inline error per Notes Spec 4.5 |
| `STATE-TIMELINE-OFFLINE` | Device offline while viewing timeline | None | Cached entries displayed | `Offline — showing cached data` banner | None | `StatusBanner` (info) |

---

## 5) Feature-Specific Error States

### 5.1 Contact Import and Sync

| State ID | Condition | Primary Copy | Secondary Copy | CTA | Auto-Retry |
|----------|-----------|-------------|---------------|-----|------------|
| `ERR-SYNC-NETWORK` | Sync failed due to network loss | `Sync couldn't complete.` | `Will retry automatically when you're back online.` | `Retry Now` | Yes, on connectivity return |
| `ERR-SYNC-SERVER` | Sync failed due to server error (5xx) | `Contact import ran into a problem.` | `Will retry automatically.` | None | Yes, next foreground or background refresh |
| `ERR-SYNC-TIMEOUT` | Sync timed out (>60s with no progress) | `Sync is taking longer than expected.` | `It will continue in the background.` | None | Yes, background retry |
| `STATE-SYNC-LARGE-IMPORT` | Import >5,000 contacts, takes >30s | `This is a one-time setup.` | `Future syncs are instant.` | None (reassurance line) | N/A |
| `STATE-SYNC-RESUMED` | Sync resumed after interruption | `Picking up where you left off.` | `[N] of [total] imported.` | None | N/A |
| `ERR-SYNC-PULL-REFRESH-OFFLINE` | Pull-to-refresh while offline | `You're offline.` | `Contacts will sync when you reconnect.` | None | Yes, on connectivity return |
| `ERR-SYNC-PULL-REFRESH-FAILED` | Pull-to-refresh sync failed | `Sync failed.` | `Pull to retry.` | Pull-to-refresh | Yes, next foreground |

**Display rules:**
- Sync status appears in the thin inline status bar below the search bar on the Home tab (per Home Tab Spec 9.2).
- Status bar uses `rin.bg.secondary` background, `rin.type.footnote`, `rin.text.secondary`.
- On success: briefly shows `Updated just now` (1.5s), then fades.
- On failure: persists in `rin.brand.warning` text until next successful sync.

### 5.2 Dedup and Merge

| State ID | Condition | Primary Copy | Secondary Copy | CTA | Component |
|----------|-----------|-------------|---------------|-----|-----------|
| `EMPTY-DEDUP-NO-SUGGESTIONS` | Dedup scan complete, zero duplicates found | `No duplicates found. Your contacts are clean.` | None | None | Inline text in Needs Attention area (if user navigated to dedup review) |
| `EMPTY-DEDUP-ALL-REVIEWED` | All dedup suggestions actioned | `All duplicates reviewed.` | None | None | Brief positive acknowledgment, then section collapses |
| `ERR-DEDUP-MERGE-FAILED` | Merge operation failed (server error) | `Merge couldn't be completed.` | `Try again.` | `Retry` on the merge card | N/A |

### 5.3 Search

| State ID | Condition | Primary Copy | Secondary Copy | CTA | Component |
|----------|-----------|-------------|---------------|-----|-----------|
| `EMPTY-SEARCH-NO-RESULTS-LOCAL` | Local search returns zero matches | `No contacts match '[query]'` | `Try a different search term` | `Add Contact Manually` | `EmptyStateView` |
| `EMPTY-SEARCH-NO-RESULTS-SERVER` | Local + server search both return zero | `No results found on Rin` | None | `Add Contact Manually` | `EmptyStateView` |
| `ERR-SEARCH-FAILED` | Server search request failed | `Search isn't working right now.` | `Local results shown. Pull to retry.` | `Retry` | Inline error below search bar; local results still displayed if available |
| `EMPTY-SEARCH-NOTES-NO-RESULTS` | In-timeline note search returns zero | `No notes match '[query]'` | None | None | Inline text in N2 search results area |

### 5.4 Score

| State ID | Condition | Primary Copy | Secondary Copy | CTA | Component |
|----------|-----------|-------------|---------------|-----|-----------|
| `ERR-SCORE-COMPUTATION-FAILED` | Score update failed on server | `Score couldn't be updated.` | `It will refresh automatically.` | None | Inline text below score display, `rin.text.secondary` |
| `STATE-SCORE-COMPONENT-UNAVAILABLE` | Component data unavailable from server | Muted bar with `--` | `Data not available right now.` | None | Component bar in `rin.text.tertiary` color |
| `ERR-SCORE-HISTORY-LOAD-FAILED` | Score history endpoint failed | `Could not load score history.` | `Try again in a moment.` | `Retry` | `EmptyStateView` in SC4 |

### 5.5 Premium and Paywall

| State ID | Condition | Primary Copy | Secondary Copy | CTA | Component |
|----------|-----------|-------------|---------------|-----|-----------|
| `ERR-PREMIUM-PURCHASE-FAILED` | StoreKit purchase failed or was canceled by system | `Purchase couldn't be completed.` | `No charge was made.` | `Try Again` | Alert dialog |
| `ERR-PREMIUM-RESTORE-FAILED` | Restore purchases failed (network or Apple ID issue) | `Couldn't restore purchases.` | `Check your Apple ID and try again.` | `Try Again` | Alert dialog |
| `EMPTY-PREMIUM-NO-PURCHASES` | Restore completed but found no previous purchases | `No previous purchases found for this Apple ID.` | None | `Dismiss` | Alert dialog |
| `ERR-PREMIUM-VERIFICATION-FAILED` | Receipt verification failed server-side | `Purchase verification is pending.` | `Your subscription will activate shortly.` | None | Inline text; auto-retries receipt validation |

### 5.6 Notes and Reminders

| State ID | Condition | Primary Copy | Secondary Copy | CTA | Component |
|----------|-----------|-------------|---------------|-----|-----------|
| `ERR-NOTE-SAVE-FAILED` | Note save failed (server error) | `Note couldn't be saved.` | `Check your connection and try again.` | `Retry` | Alert dialog (note creation sheet stays open) |
| `STATE-NOTE-SAVED-OFFLINE` | Note saved while offline | `Saved. Will sync when online.` | None | None | Toast notification (1.5s) |
| `ERR-NOTE-DELETE-FAILED` | Note delete failed | `Couldn't delete this note.` | `Try again.` | `Retry` | Alert dialog |
| `ERR-REMINDER-SCHEDULE-FAILED` | Reminder scheduling failed | `Reminder couldn't be set.` | `Try again.` | `Retry` | Alert dialog |
| `STATE-REMINDER-NO-NOTIFICATION-PERMISSION` | User creates reminder but notification permission denied | `To get notified about this reminder, enable notifications in Settings.` | None | `Open Settings` / `Not Now` | Inline prompt after reminder creation |

### 5.7 Invite and Referral

| State ID | Condition | Primary Copy | Secondary Copy | CTA | Component |
|----------|-----------|-------------|---------------|-----|-----------|
| `EMPTY-INVITE-NO-ACTIVITY` | No invites sent yet | `Share Rin to see your invite activity here.` | None | `Share Rin` | `EmptyStateView` |
| `ERR-INVITE-LINK-FAILED` | Invite link generation failed | `Couldn't create invite link.` | `Try again.` | `Try Again` | Alert dialog |

### 5.8 OTP and Authentication

| State ID | Condition | Primary Copy | Secondary Copy | CTA | Component |
|----------|-----------|-------------|---------------|-----|-----------|
| `ERR-OTP-INVALID` | OTP code verification failed | `That code didn't work.` | `Try again.` | `Verify` (re-enabled) | Inline error below code input, `rin.brand.error` text. Per Onboarding Spec S5. |
| `ERR-OTP-RATE-LIMITED` | Too many OTP attempts | `Too many attempts.` | `Try again in [N] seconds.` | Resend timer displayed | Inline error with countdown timer |
| `ERR-OTP-SEND-FAILED` | Code send failed (network/server) | `Code couldn't be sent.` | `Check your connection and try again.` | `Resend Code` | Inline error below phone input |

### 5.9 Profile and Shadow Management

| State ID | Condition | Primary Copy | Secondary Copy | CTA | Component |
|----------|-----------|-------------|---------------|-----|-----------|
| `ERR-SHADOW-CREATE-RATE-LIMITED` | >3 shadow profiles created in 24 hours | `Profile creation limit reached.` | `You can create another profile tomorrow.` | `Dismiss` | Alert dialog |
| `ERR-SHADOW-CREATE-FAILED` | Server error during shadow creation | `Profile couldn't be created.` | `Try again.` | `Retry` | Alert dialog |
| `ERR-PROFILE-SAVE-FAILED` | Profile edit save failed | `Changes couldn't be saved.` | `Check your connection and try again.` | `Retry` | Alert dialog |
| `STATE-SHADOW-OFFBOARDING` | Professional shadow unlinked from org | `Your professional profile is no longer linked to [Company].` | `Choose what to do with it.` | `Convert` / `Archive` / `Delete` | Full-screen notification per Shadow Profile Spec 8.2 |
| `ERR-SHADOW-REVEAL-FAILED` | Identity reveal failed | `Identity reveal couldn't be completed.` | `Try again.` | `Retry` | Alert dialog |

### 5.10 Permissions

| State ID | Condition | Primary Copy | Secondary Copy | CTA | Component |
|----------|-----------|-------------|---------------|-----|-----------|
| `ERR-PERMISSION-CONTACTS-DENIED` | Contacts permission denied, user attempts import-dependent action | `Contacts access needed` | `To [action], Rin needs access to your contacts.` | `Open Settings` / `Not Now` | Alert dialog per Contacts Spec 9.2 |
| `ERR-PERMISSION-NOTIFICATIONS-DENIED` | Notification permission denied, user creates reminder | `Notifications are off.` | `Reminders will appear only in the app.` | `Open Settings` / `Not Now` | Inline prompt |
| `ERR-PERMISSION-PHOTO-DENIED` | Photo library access denied during profile photo setup | `Photo access needed` | `To add a photo, allow access in Settings.` | `Open Settings` / `Not Now` | Alert dialog |
| `ERR-PERMISSION-CAMERA-DENIED` | Camera access denied during photo capture | `Camera access needed` | `To take a photo, allow access in Settings.` | `Open Settings` / `Not Now` | Alert dialog |

---

## 6) Loading States

### 6.1 Loading Patterns

| Pattern | When to Use | Component | Behavior |
|---------|------------|-----------|----------|
| **Skeleton screens** | Content lists, cards, profile sections. Any area where the layout shape is known. | Gray placeholder rectangles matching content layout | Subtle shimmer animation (pulse opacity 0.3-0.7, 1.5s cycle). Non-blocking: user can navigate away. |
| **Inline spinners** | Action buttons (Save, Merge, Create). Loading state for a specific user action. | `ProgressView` inside the button, replacing label text | Button disabled during load. Other UI remains interactive. |
| **Pull-to-refresh** | Contact list, timeline. User-initiated refresh. | Standard iOS `refreshable` modifier | Standard iOS spinner. Status bar appears below search bar on completion/failure. |
| **Full-screen spinner** | Critical first loads with no cached data (onboarding sync, first score load). | Centered `ProgressView` + descriptive label | Rare. Use only when no skeleton shape is available. |
| **Progress bar** | Import progress, large operations with known completion percentage. | Determinate `ProgressView` with counter text | Shows "N of M" progress. Non-blocking after minimum viable data is ready. |

### 6.2 Skeleton Screen Specifications

| Screen | Skeleton Layout | Elements |
|--------|----------------|----------|
| Home tab contact list | Repeating rows: circle placeholder (40pt) + two text lines (60% and 40% width) | 8 placeholder rows |
| Smart section cards | Rounded rectangle cards (full width, 88pt height) | 2 placeholder cards |
| Score tab | Large circle placeholder (120pt) + 4 horizontal bars | Score ring + component bars |
| Circle detail member list | Same as contact list skeleton | 6 placeholder rows |
| Contact detail | Large circle (80pt) + 4 section blocks | Header + sections |
| Contact timeline | Repeating: small icon (16pt) + text block (3 lines) | 5 placeholder entries |
| Profile home | Large card (header) + 3 section blocks | Profile card + sections |

### 6.3 Loading Timeout

| Duration | Behavior |
|----------|----------|
| 0-5 seconds | Normal loading state displayed |
| 5-10 seconds | No change. Patience is expected. |
| >10 seconds | Append retry option: `Taking longer than usual. [Retry]` below the loading indicator. Loading continues — retry does not cancel the current request, it queues a new one. |
| >30 seconds | Cancel the request. Show server error state (`ERR-GLOBAL-SERVER`). |

---

## 7) Degraded States (Partial Data)

Degraded states occur when some data is available but incomplete. The app shows what it has and gracefully handles what it does not.

| State ID | Condition | Behavior | Visual Treatment |
|----------|-----------|----------|-----------------|
| `DEGRADED-ENRICHMENT-UNAVAILABLE` | Contact has no enrichment data from Rin network | Show contact with device-imported data only. No enrichment badge. | No `EnrichmentBadge` icon. No "enriched" section. Contact renders normally with phone-sourced data. |
| `DEGRADED-SCORE-STALE` | Score data >24h old | Display cached score with staleness indicator. | Score ring in muted colors. `Estimated` badge in `rin.brand.warning` below score number. Last-updated timestamp shown: "Last updated [date]." |
| `DEGRADED-PHOTO-FAILED` | Contact or profile photo failed to load (network error, CDN issue) | Show generated initials avatar as fallback. | `AvatarView` renders first+last initials on `rin.bg.secondary` background. No error indicator — initials avatar is the standard fallback. |
| `DEGRADED-TIMELINE-PARTIAL` | Timeline loaded some entries but pagination failed | Show loaded entries, indicate more exist. | Entries render normally. At bottom: `Loading more...` spinner. If spinner fails: `Could not load older entries. Tap to retry.` |
| `DEGRADED-SERVER-SEARCH-FAILED` | Local search succeeded but server search failed | Show local results. Indicate server results unavailable. | Local results displayed normally. Subtle inline text below results: `Showing local results only.` No disruptive error. |
| `DEGRADED-NOTIFICATION-PERMISSION-DENIED` | Reminders exist but push notifications are off | Reminders appear in-app only (Home smart section, contact detail). No push delivery. | No visual indicator on reminders themselves. Reminder creation flow shows the notification permission prompt (see `STATE-REMINDER-NO-NOTIFICATION-PERMISSION`). |
| `DEGRADED-CONTACT-MISSING-FIELDS` | Contact has name but no phone, email, or other channels | Contact renders with name only. Subtitle shows "No contact info." | Subtitle text in `rin.text.tertiary`. Contact appears in "Needs Attention" if classified as critically incomplete. |
| `DEGRADED-SCORE-COMPONENT-PARTIAL` | Some score components loaded, others failed | Show loaded components normally. Failed components show placeholder. | Loaded bars render with data. Failed bars show muted fill with `--` and "Data not available" in `rin.text.tertiary`. |

---

## 8) Onboarding-Specific States

These states are unique to the onboarding flow (S1-S12) and do not recur in the post-onboarding app.

| State ID | Screen | Condition | Primary Copy | Secondary Copy | CTA |
|----------|--------|-----------|-------------|---------------|-----|
| `ERR-ONBOARD-OFFLINE` | Any onboarding screen | No connectivity during onboarding | `You're offline.` | `We'll continue when connection returns.` | `Retry Now` |
| `ERR-ONBOARD-OTP-INVALID` | S5 | Wrong OTP code | `That code didn't work.` | `Try again.` | `Verify` (re-enabled) |
| `ERR-ONBOARD-OTP-COOLDOWN` | S5 | Resend rate limited | Cooldown timer displayed | `Resend code in [N]s` | Timer auto-counts down |
| `STATE-ONBOARD-CONTACTS-DENIED` | S6 | User denied contacts permission | `You can still set up your profile and sharing.` | None | `Continue` (proceeds to S7 in limited mode) |
| `ERR-ONBOARD-USERNAME-TAKEN` | S9 | Username already exists | `That username is taken.` | `Try another.` | Input field re-focused |
| `ERR-ONBOARD-USERNAME-INVALID` | S9 | Username <6 chars or invalid characters | `Usernames must be at least 6 characters.` | None | Input field re-focused |
| `STATE-ONBOARD-SYNC-SLOW` | S11 | Import >30 seconds | `This is a one-time setup.` | `Future syncs are instant.` | `Continue` remains available (non-blocking) |

---

## 9) Component Reference

### 9.1 EmptyStateView

Reusable component for all empty states where content area has nothing to show.

```
┌──────────────────────────────────────┐
│                                      │
│           [SF Symbol icon]           │
│            56pt, centered            │
│                                      │
│         [Primary copy]               │
│         rin.type.title3              │
│         20pt Semibold                │
│         center-aligned               │
│                                      │
│         [Secondary copy]             │
│         rin.type.body                │
│         17pt Regular                 │
│         rin.text.secondary           │
│         center-aligned               │
│                                      │
│         [CTA Button]                 │
│         PrimaryButton                │
│                                      │
└──────────────────────────────────────┘
```

| Property | Token |
|----------|-------|
| Icon color | `rin.text.tertiary` |
| Icon size | 56pt |
| Title font | `rin.type.title3` (20pt Semibold) |
| Title color | `rin.text.primary` |
| Body font | `rin.type.body` (17pt Regular) |
| Body color | `rin.text.secondary` |
| Vertical spacing (icon to title) | `rin.space.lg` (24pt) |
| Vertical spacing (title to body) | `rin.space.sm` (8pt) |
| Vertical spacing (body to CTA) | `rin.space.lg` (24pt) |
| Horizontal padding | `rin.space.2xl` (48pt) from edges |

### 9.2 StatusBanner

Persistent banner for global state notifications.

```
┌──────────────────────────────────────┐
│ [icon] Primary copy. Secondary copy. │
└──────────────────────────────────────┘
```

| Variant | Background | Icon Color | Text Color | Icon |
|---------|-----------|------------|------------|------|
| Info (offline) | `rin.bg.secondary` | `rin.text.secondary` | `rin.text.primary` | `wifi.slash` |
| Warning (sync failed) | `rin.bg.secondary` | `rin.brand.warning` | `rin.text.primary` | `exclamationmark.triangle` |
| Error (server error) | `rin.bg.secondary` | `rin.brand.error` | `rin.text.primary` | `xmark.circle` |

| Property | Token |
|----------|-------|
| Height | 44pt |
| Font | `rin.type.footnote` (13pt Regular) |
| Icon size | 16pt |
| Internal padding | `rin.space.md` (12pt) horizontal, centered vertical |
| Corner radius | None (full-width, flush with navigation bar) |
| Animation | Slide down on appear (200ms, `.easeOut`). Slide up on dismiss (200ms, `.easeIn`). |

### 9.3 Inline Error Text

For field-level validation and action-specific errors.

| Property | Token |
|----------|-------|
| Font | `rin.type.footnote` (13pt Regular) |
| Color | `rin.brand.error` |
| Spacing | `rin.space.xs` (4pt) above the error text, below the triggering element |
| Icon | None (color alone conveys error state) |
| Animation | Fade in (150ms, `.easeIn`) |

---

## 10) State Matrix by Screen

Complete cross-reference of which states apply to which screens.

### 10.1 Home Tab

| State | Smart Sections | Contact List | Search | Tab Badge | Sync Bar |
|-------|---------------|-------------|--------|-----------|----------|
| Normal (post-onboarding) | Populated | Full list | Available | Count from dedup | Hidden |
| All sections cleared | None (collapsed) | Full list | Available | 0 | Hidden |
| Permission denied, no contacts | None | `EMPTY-HOME-NO-CONTACTS-DENIED` | Hidden | 0 | Hidden |
| Permission denied, manual contacts | Possibly populated | Manual contacts | Available | 0 | Hidden |
| Sync in progress | Partially populated | Partial or loading | Available (local) | Previous count | `Syncing contacts...` |
| Sync failed | Cached | Cached list | Available (local) | Cached count | `ERR-SYNC-PULL-REFRESH-FAILED` |
| Offline | Cached | Cached list | Local only | Cached count | `ERR-GLOBAL-OFFLINE` banner |
| Server error | Cached | Cached list | Local only | Cached count | `ERR-GLOBAL-SERVER` |
| Session expired | Blocked | Blocked | Blocked | N/A | `ERR-GLOBAL-SESSION` overlay |

### 10.2 Score Tab

| State | Score Display | Components | History | Explainability |
|-------|-------------|------------|---------|----------------|
| Score loaded | Full display | All bars | Available | Dynamic string |
| Score stale (>24h) | `STATE-SCORE-STALE` | Bars with cached data | Available | Cached string |
| Score unavailable (day 1) | `EMPTY-SCORE-NOT-CALCULATED` | Hidden | Hidden | Hidden |
| History insufficient (<7 days) | Full display | All bars | `EMPTY-SCORE-HISTORY-INSUFFICIENT` | Dynamic string |
| Component data missing | Full display | `EMPTY-SCORE-COMPONENT-NO-DATA` for affected | Available | Adjusted string |
| Server error | `ERR-GLOBAL-SERVER` (full-screen if first load, inline if refresh) | Cached or hidden | Cached or hidden | Cached or hidden |
| Offline | Cached display with `DEGRADED-SCORE-STALE` | Cached bars | Cached | Cached |

### 10.3 Circles Tab

| State | Circle List | Circle Detail | Member List | Access Requests |
|-------|------------|--------------|-------------|-----------------|
| Normal | All circles | Members shown | Full list | Requests listed |
| No custom circles | Mandatory + prepopulated shown, `EMPTY-CIRCLES-NO-CUSTOM` in custom section | N/A | N/A | N/A |
| Empty circle | N/A | `EMPTY-CIRCLES-DETAIL-NO-MEMBERS` | Empty | None |
| No pending requests | N/A | Normal | Normal | `EMPTY-CIRCLES-NO-PENDING-REQUESTS` |
| Offline | Cached list | Cached detail | Cached | Cached |

### 10.4 Profile Tab

| State | Profile Home | Profile Detail | Shadow Picker | Security Inbox |
|-------|-------------|---------------|---------------|----------------|
| Normal | Active profile + stats | Editable fields | Cards browsable | Items listed |
| No shadows | `EMPTY-PROFILE-NO-SHADOWS` | Primary only | Primary card + "+" | N/A |
| Security inbox clear | N/A | N/A | N/A | `EMPTY-PROFILE-SECURITY-INBOX` |
| Free tier | `STATE-PROFILE-FREE-TIER` | N/A | N/A | N/A |
| Offline | Cached profile | Edit queued for sync | Cached cards | Cached items |

---

## 11) Accessibility Requirements

All error and empty states must meet these accessibility standards.

### 11.1 VoiceOver

| Element | VoiceOver Behavior |
|---------|-------------------|
| `StatusBanner` | Announced immediately on appearance as an alert: "[variant]: [primary copy] [secondary copy]." Uses `.accessibilityAddTraits(.isStaticText)` and posts `UIAccessibility.Notification.announcement`. |
| `EmptyStateView` | Icon not announced (decorative). Title and body announced as group. CTA announced as button with hint. |
| Inline error text | Announced immediately on appearance. Associated with the input field using `.accessibilityLinkedTo`. |
| Retry buttons | Label: "Retry". Hint: "Double tap to retry the failed operation." |
| Loading spinners | Announced: "Loading." For specific contexts: "Loading contacts," "Loading score," "Loading timeline." Uses `accessibilityLabel`. |
| Skeleton screens | Not individually announced. Container announces: "Content loading." |
| Countdown timers | Value announced on appearance. Updates announced every 10 seconds to avoid VoiceOver spam. |
| Alert dialogs | Standard iOS alert accessibility. Title and message read automatically. Buttons announced with labels. |

### 11.2 Dynamic Type

All error and empty state views support Dynamic Type from default size through `AX5`:

| Element | Base Size | Scales With |
|---------|----------|-------------|
| `EmptyStateView` title | 20pt (`rin.type.title3`) | `.title3` TextStyle |
| `EmptyStateView` body | 17pt (`rin.type.body`) | `.body` TextStyle |
| `StatusBanner` text | 13pt (`rin.type.footnote`) | `.footnote` TextStyle |
| Inline error text | 13pt (`rin.type.footnote`) | `.footnote` TextStyle |
| Button labels | 17pt (`rin.type.body`) | `.body` TextStyle |

At `AX5` sizes:
- `EmptyStateView` icon remains 56pt (minimum; does not scale further).
- `StatusBanner` height expands vertically to accommodate larger text (no fixed height at large sizes).
- Inline errors may wrap to multiple lines.

### 11.3 Semantic Roles

| Component | Accessibility Trait | Role |
|-----------|-------------------|------|
| `StatusBanner` | `.isStaticText` | Informational. Not interactive unless it contains a button. |
| `EmptyStateView` | Container | Groups icon + text + button as a single semantic element. |
| Retry buttons | `.isButton` | Standard button semantics. |
| Error text | `.isStaticText` | Linked to the field or action that caused the error. |
| Loading indicators | `.updatesFrequently` | Conveyed as an active process. |

### 11.4 Color and Contrast

- All error text in `rin.brand.error` (`#EF4444`) meets WCAG 2.1 AA contrast ratio against both `rin.bg.primary` and `rin.bg.secondary` backgrounds.
- Warning text in `rin.brand.warning` (`#F59E0B`) meets 3:1 contrast ratio for large text (used only in `rin.type.footnote` contexts within banners).
- Error states never rely on color alone. All error states include text descriptions and/or icons.
- Skeleton shimmer animation respects `UIAccessibility.isReduceMotionEnabled` — shimmer disabled, static gray shown instead.

### 11.5 Reduced Motion

When `UIAccessibility.isReduceMotionEnabled` is true:
- `StatusBanner` appears/disappears with fade (no slide).
- Skeleton screens show static gray (no shimmer).
- Inline errors appear instantly (no fade-in).
- Loading spinners use standard iOS `ProgressView` (already motion-appropriate).

---

## 12) Implementation Checklist

For each new screen or feature, verify against this checklist before shipping:

| # | Check | Verified |
|---|-------|----------|
| 1 | Every API call has a defined error state for network failure, server error (5xx), and timeout. | |
| 2 | Every list/grid has a defined empty state when zero items exist. | |
| 3 | Every loading state uses skeleton screens (not spinners) for content areas. | |
| 4 | Every retry button has a loading state and a failure-after-retry state. | |
| 5 | Every error message uses copy from this catalog (not ad-hoc strings). | |
| 6 | VoiceOver announces all error and empty states. | |
| 7 | Offline mode degrades gracefully (cached data shown, write operations queued). | |
| 8 | Dynamic Type is tested at AX5 for all error/empty views. | |
| 9 | No banned words per BRAND_NARRATIVE_V1 section 7.2 appear in any copy. | |
| 10 | Error states tested in both light and dark mode. | |
| 11 | Reduced motion preference respected for all animations. | |
| 12 | Timeout behavior defined (>10s shows retry, >30s shows error). | |

---

## 13) Open Decisions

1. **Offline write queue visibility**: Should the user see a count of pending offline operations (e.g., "3 changes waiting to sync") or should the queue be invisible? Visible queue gives control and transparency. Invisible queue reduces cognitive load. Current spec keeps it invisible except for notes (`STATE-NOTE-SAVED-OFFLINE` toast).

2. **Error retry limits**: Should there be a maximum retry count before showing a different message (e.g., "This might be a longer outage. Try again later.")? Current spec allows unlimited retries. A cap of 3 automatic retries with escalated messaging may be appropriate.

3. **Empty state illustrations**: Should empty states use custom illustrations beyond SF Symbols, or stay with SF Symbols only for visual consistency and development speed? SF Symbols are specified in this catalog. Custom illustrations could add warmth but require design resources and increase asset size.

4. **Banner stacking**: When multiple global states are active simultaneously (e.g., offline + sync failed + session expired), how should banners stack? Current spec: session expired takes full precedence (full-screen overlay). For non-blocking banners, only the highest-priority banner should display. Priority order: force update > session expired > server error > offline > rate limit.

5. **Error analytics**: Should every error state fire an analytics event automatically, or should analytics be opt-in per state? Systematic error tracking would catch issues faster. Proposed: every state with an `ERR-` prefix auto-fires `error.displayed` with `state_id`, `screen`, and `context` properties.
