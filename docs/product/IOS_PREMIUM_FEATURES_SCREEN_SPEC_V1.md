# iOS Premium Features Screen Spec V1

## 1) Purpose

Screen-level specification for the three premium features: **Who Viewed Me**, **How Am I Stored**, and **Enrichment Alerts**. Defines the full UX for both the free-tier teaser experience and the premium unlocked experience, including screen layouts, states, gating behavior, privacy models, and events.

Companion docs:
- `docs/product/IOS_SCORE_EXPLANATION_SCREEN_SPEC_V1.md` (score tab, premium sections in §6)
- `docs/product/USER_JOURNEY_PLAN.md` (Journey 6: Premium Driver)
- `docs/product/RIN_SCORE_V1.md` (score context)
- `docs/design/IOS_KEY_SCREEN_WIREFRAMES_V1.md` (Score Home wireframe §6, Paywall §10)
- `docs/plan/IAP_SUBSCRIPTION_COMPLIANCE_V1.md` (pricing, StoreKit 2, paywall rules)
- `docs/plan/ICP_MESSAGING_PILLARS_V1.md` (messaging pillars)
- `docs/architecture/IOS_NAVIGATION_STATE_V1.md` (deep links: `rin://premium`, `rin://profile?section=viewers`)
- `docs/design/IOS_DESIGN_TOKENS_V1.md` (tokens, components)
- `docs/design/BRAND_NARRATIVE_V1.md` (tone: "Get Premium" not "Unlock")

---

## 2) Feature Summary

| ID | Feature | Free Tier | Premium |
|----|---------|-----------|---------|
| PREM1 | Who Viewed Me | Aggregate count visible, names hidden | Full viewer list with timestamps, profiles, trends |
| PREM2 | How Am I Stored | Aggregate "Stored by N contacts" count | Name variant breakdown with per-contact attribution |
| PREM3 | Enrichment Alerts | Monthly digest with contact names, details hidden | Real-time push notifications + in-app feed with full change details |

Pricing (from `IAP_SUBSCRIPTION_COMPLIANCE_V1.md`):
- Monthly: $4.99/mo (`com.rin.premium.monthly`)
- Annual: $49.99/yr (`com.rin.premium.annual`)

---

## 3) Premium Feature 1: Who Viewed Me

### 3.1 Free Tier Experience (Teaser)

**Location:** Score Home (SC1), below component breakdown section.

**Layout:**
```
┌──────────────────────────────────────┐
│ WHO VIEWED ME                        │
│                                      │
│ 👀  3 people viewed your profile     │
│     this week                        │
│                              [🔒 >] │
└──────────────────────────────────────┘
```

**Behavior:**
- Displays aggregate view count for the current week.
- Count is real data — not fabricated or inflated.
- Lock icon (`🔒`) indicates premium feature.
- Tap anywhere on the section → paywall (presented as full-screen cover).
- If count is zero: "No profile views this week." Lock icon still present.

**Copy:**
- "3 people viewed your profile this week"
- Zero state: "No profile views this week"

---

### 3.2 Premium Experience (PREM1: Viewer List)

**Screen ID:** PREM1

**Entry points:**
- Score Home (SC1) → tap "Who Viewed Me" section (when subscribed).
- Deep link: `rin://profile?section=viewers`.
- Push notification: "Someone viewed your profile" → opens PREM1.

**Layout:**
```
┌──────────────────────────────────────┐
│ ◀ Back              Who Viewed Me    │
├──────────────────────────────────────┤
│                                      │
│ SUMMARY                              │
│ 12 views this week, up from 8 last   │
│ week                                 │
│                                      │
│ [This Week ▼] [This Month]          │
│                                      │
├──────────────────────────────────────┤
│ VIEWERS                              │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ [📷] Sarah Chen                 │ │
│ │      Viewed 2 hours ago          │ │
│ │      3 views this week      [>] │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ [📷] Mike Torres                │ │
│ │      Viewed yesterday            │ │
│ │      1 view this week       [>] │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ [  ] Unknown Viewer              │ │
│ │      Viewed 3 days ago           │ │
│ │      Anonymous browsing     [>] │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ...                                  │
├──────────────────────────────────────┤
│ 🔒 Privacy                          │
│ Viewers who browse anonymously are   │
│ not shown. You can enable anonymous  │
│ browsing in Settings.                │
└──────────────────────────────────────┘
```

**Header:**
- Title: "Who Viewed Me".
- Back button → Score Home (SC1).

**Time range selector:**
- Two segments: "This Week" (default) and "This Month".
- Tap to toggle. List and summary stats update immediately.
- "This Week" = Monday 00:00 to current time.
- "This Month" = 1st of current month to current time.

**Summary stats:**
- Format: "{N} views this week, up from {M} last week" or "down from {M} last week".
- If no prior period data: "{N} views this week".
- If monthly view: "{N} views this month, up from {M} last month".

**Viewer list:**
Each row contains:
- Avatar (photo or placeholder).
- Name: display name if viewer is in user's contacts, otherwise "Unknown Viewer".
- Timestamp: relative time ("2 hours ago", "yesterday", "Feb 12").
- View count for selected period ("3 views this week").
- For anonymous browsers: shows "Anonymous browsing" instead of view count.
- Chevron (`>`) for navigation.

**Row tap behavior:**
- Viewer is in user's contacts → Contact Detail screen (RinContacts).
- Viewer is a Rin user but not in contacts → Profile Preview (minimal: name, avatar, Rin username, "Add to Contacts" CTA).
- Viewer is anonymous → row is not tappable, shows "This viewer browses anonymously" in secondary text.

**Sorting:**
- Default: most recent view first.
- Viewers with multiple views in the period show their most recent view timestamp.

---

### 3.3 Who Viewed Me: Privacy Model

**Visibility rule:** Only viewers who have NOT opted into anonymous browsing are shown. Anonymous browsers are counted in the aggregate total but not identified.

**Reciprocity rule:**
- Users who enable anonymous browsing in Settings lose access to see who viewed them.
- This is a mutual tradeoff: see others or be invisible, not both.
- Copy in Settings: "Browse profiles anonymously. You won't appear in others' viewer lists, but you also won't see who views yours."

**Data retention:**
- View records retained for 90 days.
- "This Month" view shows current calendar month only.
- Views older than 90 days are purged.

---

### 3.4 Who Viewed Me: Viewer Opt-Out (Anonymous Browsing)

**Location:** Settings > Privacy > Anonymous Browsing.

**Layout:**
```
┌──────────────────────────────────────┐
│ ◀ Privacy        Anonymous Browsing  │
├──────────────────────────────────────┤
│                                      │
│ Browse Anonymously          [🔘 Off] │
│                                      │
│ When enabled, you won't appear in    │
│ others' viewer lists. In return,     │
│ you won't see who views your         │
│ profile.                             │
│                                      │
│ This applies to all profiles you     │
│ view going forward. Past views are   │
│ not retroactively hidden.            │
│                                      │
└──────────────────────────────────────┘
```

**Behavior:**
- Toggle ON → user's future profile views are anonymous.
- Toggle ON → user's own "Who Viewed Me" feature shows: "Anonymous browsing is on. Turn it off to see your viewers."
- Toggle OFF → user reappears in future viewer lists and regains access to their own viewer list.
- Change is not retroactive. Past views remain in existing records.

---

### 3.5 Who Viewed Me: Empty State

```
┌──────────────────────────────────────┐
│ ◀ Back              Who Viewed Me    │
├──────────────────────────────────────┤
│                                      │
│ [This Week ▼] [This Month]          │
│                                      │
│                                      │
│            👀                        │
│                                      │
│  No profile views this week.         │
│                                      │
│  A complete profile with a photo     │
│  and verified contact info tends     │
│  to get more views.                  │
│                                      │
│        [Edit Profile]                │
│                                      │
└──────────────────────────────────────┘
```

**Copy variants:**
- Week empty: "No profile views this week."
- Month empty: "No profile views this month."
- Anonymous browsing on: "Anonymous browsing is on. Turn it off to see who views your profile."

---

### 3.6 Who Viewed Me: Anonymous Browsing Active State

When anonymous browsing is enabled, the PREM1 screen shows:

```
┌──────────────────────────────────────┐
│ ◀ Back              Who Viewed Me    │
├──────────────────────────────────────┤
│                                      │
│            🔒                        │
│                                      │
│  Anonymous browsing is on.           │
│                                      │
│  You're browsing profiles without    │
│  appearing in viewer lists. To see   │
│  who views your profile, turn off    │
│  anonymous browsing.                 │
│                                      │
│        [Go to Settings]              │
│                                      │
└──────────────────────────────────────┘
```

---

## 4) Premium Feature 2: How Am I Stored

### 4.1 Free Tier Experience (Teaser)

**Location:** Score Home (SC1), below "Who Viewed Me" section.

**Layout:**
```
┌──────────────────────────────────────┐
│ HOW AM I STORED                      │
│                                      │
│ 📋  Stored by 45 contacts            │
│                                      │
│                              [🔒 >] │
└──────────────────────────────────────┘
```

**Behavior:**
- Shows aggregate count of contacts who have the user's phone number or email in their contact book (derived from the bidirectional graph).
- Lock icon indicates premium feature.
- Tap → paywall.
- If count is below threshold (< 5): "Not enough data yet. As more contacts join Rin, you'll see how you're stored."

**Copy:**
- "Stored by 45 contacts"
- Low data: "Not enough data yet"

---

### 4.2 Premium Experience (PREM2: Stored Names List)

**Screen ID:** PREM2

**Entry points:**
- Score Home (SC1) → tap "How Am I Stored" section (when subscribed).
- Profile Home (P1) → if a "How Am I Stored" card is surfaced there.
- Deep link: `rin://premium/stored-names`.

**Layout:**
```
┌──────────────────────────────────────┐
│ ◀ Back            How Am I Stored    │
├──────────────────────────────────────┤
│                                      │
│ SUMMARY                              │
│ 45 contacts store your info across   │
│ 4 name variants                      │
│                                      │
├──────────────────────────────────────┤
│ NAME VARIANTS                        │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ "John Doe"                      │ │
│ │  23 contacts            ●● High │ │
│ │                             [>] │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ "Johnny"                        │ │
│ │  8 contacts          ●● Medium │ │
│ │                             [>] │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ "J. Doe"                        │ │
│ │  4 contacts          ●● Medium │ │
│ │                             [>] │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ "John Work"                     │ │
│ │  2 contacts             ●● Low │ │
│ │                             [>] │ │
│ └──────────────────────────────────┘ │
│                                      │
├──────────────────────────────────────┤
│ ℹ️  This data is derived from        │
│ contacts who have your phone number  │
│ or email. Rin does not access        │
│ anyone's contact book directly.      │
└──────────────────────────────────────┘
```

**Header:**
- Title: "How Am I Stored".
- Back button → previous screen.

**Summary stats:**
- Format: "{N} contacts store your info across {M} name variants".
- Updates when underlying data changes (daily score batch).

**Name variant rows:**
Each row contains:
- Name string in quotes (the variant as stored by others).
- Contact count: how many contacts store the user with this name.
- Match confidence indicator:
  - High (green dot `●`): exact match to user's display name or verified alias.
  - Medium (yellow dot `●`): fuzzy match — minor spelling variation, nickname, or abbreviation.
  - Low (grey dot `●`): partial match — only first name, truncated, or significantly different.
- Chevron (`>`) to drill into contact list for that variant.

**Sorting:** Descending by contact count (most common variant first).

---

### 4.3 How Am I Stored: Variant Detail

**Tap a name variant row → Variant Detail screen.**

```
┌──────────────────────────────────────┐
│ ◀ Back                  "John Doe"   │
├──────────────────────────────────────┤
│                                      │
│ 23 contacts store you as "John Doe"  │
│ Match confidence: High               │
│                                      │
├──────────────────────────────────────┤
│ CONTACTS                             │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ [📷] Sarah Chen            High │ │
│ │      ●Family               [>] │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ [📷] Mike Torres         Medium │ │
│ │      ●Colleagues           [>] │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ [📷] Lisa Park              Low │ │
│ │      ●Friends              [>] │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ...                                  │
└──────────────────────────────────────┘
```

**Each contact row contains:**
- Avatar and name.
- Per-contact confidence indicator:
  - High: the stored name is an exact match to a verified identity.
  - Medium: fuzzy match (nickname, abbreviation, minor typo).
  - Low: partial match (first name only, truncated entry).
- Circle membership dots.
- Chevron → Contact Detail (RinContacts).

**Sorting:** High confidence contacts first, then medium, then low.

---

### 4.4 How Am I Stored: Privacy Model

**Data source:** This feature uses data from the bidirectional contact graph. When Contact A imports their contacts and Contact B (the user) is present, Rin can infer how A stores B's name. This is not direct access to A's contact book — it is derived from the graph edges created during contact ingestion.

**Privacy constraints:**
- Only shows data from contacts who are also Rin users and have imported their contacts.
- Non-Rin contacts are not included (their contact books are not accessible).
- The user never sees the raw contact card from another person's phone.
- Confidence is based on entity resolution matching, not direct string comparison.

**Data freshness:**
- Updated during daily score computation batch.
- Not real-time — new imports may take up to 24 hours to reflect.

---

### 4.5 How Am I Stored: Empty State

```
┌──────────────────────────────────────┐
│ ◀ Back            How Am I Stored    │
├──────────────────────────────────────┤
│                                      │
│            📋                        │
│                                      │
│  Not enough data yet.                │
│                                      │
│  As more of your contacts join Rin,  │
│  you'll see how they store your      │
│  name and contact info.              │
│                                      │
└──────────────────────────────────────┘
```

**Threshold:** Minimum five contacts required before showing variant data. Below that, show empty state to prevent trivial de-anonymization.

---

## 5) Premium Feature 3: Enrichment Alerts

### 5.1 Free Tier Experience (Teaser)

**Location:** Home tab, surfaced as a monthly digest card at the top of the contact list (below dedup review if present).

**Layout:**
```
┌──────────────────────────────────────┐
│ ENRICHMENT DIGEST                    │
│                                      │
│ ✨  5 contacts updated their info    │
│     this month                       │
│                                      │
│ Sarah Chen, Mike Torres, +3 more     │
│                              [🔒 >] │
└──────────────────────────────────────┘
```

**Behavior:**
- Shows aggregate count of contacts whose enrichment data changed this month.
- Lists up to two contact names, then "+N more".
- Tap → paywall.
- Names are visible (which contacts changed), but the specific changes are behind the paywall.
- If no enrichments this month: card is not shown.

**Frequency:** Card refreshes monthly. Dismissed card reappears next month if new enrichments exist.

---

### 5.2 Premium Experience (PREM3: Enrichment Feed)

**Screen ID:** PREM3

**Entry points:**
- Home tab → tap enrichment digest card (when subscribed).
- Push notification → "Sarah Chen updated their phone number" → opens PREM3.
- Settings > Notifications > Enrichment toggle (premium only).
- Deep link: `rin://home?section=enrichment`.

**Layout:**
```
┌──────────────────────────────────────┐
│ ◀ Back          Enrichment Alerts    │
├──────────────────────────────────────┤
│                                      │
│ [All ▼]  [Field ▼]  [Circle ▼]     │
│                                      │
├──────────────────────────────────────┤
│ TODAY                                │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ [📷] Sarah Chen                 │ │
│ │      Phone number changed        │ │
│ │      2 hours ago            [>] │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ [📷] Mike Torres                │ │
│ │      Email address added         │ │
│ │      5 hours ago            [>] │ │
│ └──────────────────────────────────┘ │
│                                      │
├──────────────────────────────────────┤
│ YESTERDAY                            │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ [📷] Lisa Park                  │ │
│ │      Company changed             │ │
│ │      Yesterday 4:30 PM     [>] │ │
│ └──────────────────────────────────┘ │
│                                      │
├──────────────────────────────────────┤
│ THIS WEEK                            │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ [📷] Tom Nguyen                 │ │
│ │      Job title updated           │ │
│ │      Feb 12                 [>] │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ [📷] Anna Kim                   │ │
│ │      Phone number changed        │ │
│ │      Feb 11                 [>] │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ...                                  │
└──────────────────────────────────────┘
```

**Header:**
- Title: "Enrichment Alerts".
- Back button → Home tab.

**Filter bar:**
Three filter dropdowns, combinable:
- **Recency**: All (default), Today, This Week, This Month.
- **Field type**: All (default), Phone, Email, Company, Job Title, Address, Photo.
- **Circle**: All (default), then each user circle (Family, Friends, Colleagues, etc.).

**Feed items:**
Each row contains:
- Contact avatar and name.
- Change description: "{Field} {action}" — e.g., "Phone number changed", "Email address added", "Company changed", "Job title updated", "Photo updated".
- Timestamp: relative for recent ("2 hours ago", "yesterday"), absolute for older ("Feb 12").
- Chevron → Contact Detail (RinContacts), with the changed field highlighted.

**Grouping:** Items grouped by time period: Today, Yesterday, This Week, Earlier This Month, Older.

**Sorting:** Most recent first within each group.

---

### 5.3 Push Notifications (Premium Only)

**When premium user has enrichment notifications enabled:**
- Push notification sent within 1 hour of enrichment detection.
- Format: "{Contact Name} updated their {field}."
- Examples:
  - "Sarah Chen updated their phone number."
  - "Mike Torres added an email address."
- Tap → opens PREM3 feed, scrolled to the relevant item.
- Deep link: `rin://contacts/{id}?highlight=enrichment`.

**Notification settings:**
- Toggle in Settings > Notifications > Enrichment Alerts.
- Only visible and toggleable when premium is active.
- When premium lapses: toggle becomes disabled, shows "(Premium)" label.

**Batching rules:**
- If more than three enrichments happen within 1 hour for the same user, batch into one notification: "3 contacts updated their info."
- Maximum five enrichment notifications per day to prevent notification fatigue.
- User can set quiet hours in iOS notification settings (system-level).

---

### 5.4 Enrichment Alerts: Empty State

```
┌──────────────────────────────────────┐
│ ◀ Back          Enrichment Alerts    │
├──────────────────────────────────────┤
│                                      │
│            ✨                        │
│                                      │
│  No enrichment updates yet.          │
│                                      │
│  When your contacts update their     │
│  info, changes appear here.          │
│                                      │
└──────────────────────────────────────┘
```

**With active filters returning zero results:**
"No updates match these filters. Try adjusting your selection."

---

## 6) Feature Gating Behavior

### 6.1 Free User Taps a Premium Feature

The gating flow is consistent across all three premium features:

```
Step 1: User taps premium-locked section
        (e.g., "Who Viewed Me" on Score Home)
            ↓
Step 2: Brief glimpse (200ms) — the section expands
        slightly to show a blurred preview of what
        the feature contains (blurred list rows,
        count visible above the blur)
            ↓
Step 3: Smooth transition to paywall
        (full-screen cover, 300ms spring animation)
            ↓
Step 4a: User subscribes → paywall dismisses,
         user returns directly to the feature
         they tapped (not Score Home)
            ↓
Step 4b: User dismisses paywall → returns to
         Score Home with feature still locked
```

**Transition animation:**
- The blurred preview scales and cross-fades into the paywall.
- Duration: 300ms with `.spring(response: 0.3)` curve.
- Matches motion tokens from `IOS_DESIGN_TOKENS_V1.md` (sheet present animation).

### 6.2 Lock Icon Treatment

- Lock icon: SF Symbol `lock.fill`, size `.footnote`, color `rin.text.secondary`.
- Appears on premium-locked sections in Score Home and anywhere premium features are referenced.
- VoiceOver reads the lock as "Premium feature" (see §9).
- When premium is active: lock icon is not displayed.

### 6.3 Paywall Presentation Rules

From `IAP_SUBSCRIPTION_COMPLIANCE_V1.md`:
- Always dismissible (close button required by Apple).
- Never blocks core app functionality.
- Never shown during onboarding.
- Max once per session per trigger (if user dismisses paywall from "Who Viewed Me", they can still trigger it from "How Am I Stored" in the same session, but tapping "Who Viewed Me" again won't re-show the paywall until next session).
- Annual plan highlighted as default selection.

### 6.4 Post-Purchase Return

After successful subscription:
- Paywall dismisses with 300ms fade-out.
- User is navigated directly to the feature they originally tapped.
- Feature loads with data immediately (no "loading your premium features" interstitial).
- If the feature's data requires server fetch (e.g., viewer list), show skeleton loading in the feature screen itself.

### 6.5 Premium Lapse Behavior

When a subscription expires or is cancelled:
- Premium features revert to teaser state on next app launch.
- No immediate removal mid-session — the current session honors the cached entitlement.
- On next launch: `PremiumService.checkEntitlement()` verifies status.
- User's historical data (viewer history, stored names) is retained server-side for 90 days in case of re-subscription.

---

## 7) Premium Badge / Indicator

### 7.1 Subscribed User

- Subtle premium indicator on Profile Home (P1) in the Account section: "Premium" label with `rin.brand.accent` color, replacing "Free".
- Settings > Account > Premium row shows: "Premium" with plan details ("Monthly" or "Annual") and next renewal date.
- No public-facing badge. Other users cannot tell if someone is a premium subscriber.

**Profile Home layout (premium active):**
```
│ ACCOUNT                              │
│ ┌──────────────────────────────────┐ │
│ │ ⭐ Premium            Active > │ │
│ │ ❓ Help & FAQ                  > │ │
│ │ ℹ️  About Rin                  > │ │
│ └──────────────────────────────────┘ │
```

### 7.2 Free User

- Profile Home shows: "Premium — Free >" → tap opens paywall.
- No visual indication to other users.

---

## 8) Premium Navigation Map

```
Score Home (SC1)
├── "Who Viewed Me" section
│   ├── [Free] → Paywall (full-screen cover)
│   └── [Premium] → PREM1 Viewer List
│       ├── Contact Detail (if in contacts)
│       └── Profile Preview (if not in contacts)
├── "How Am I Stored" section
│   ├── [Free] → Paywall (full-screen cover)
│   └── [Premium] → PREM2 Stored Names List
│       └── Variant Detail
│           └── Contact Detail
│
Home Tab
├── Enrichment Digest card
│   ├── [Free] → Paywall (full-screen cover)
│   └── [Premium] → PREM3 Enrichment Feed
│       └── Contact Detail (with field highlight)
│
Profile Home (P1)
├── Account > Premium
│   ├── [Free] → Paywall
│   └── [Premium] → Subscription Management
│
Settings
├── Privacy > Anonymous Browsing (toggle)
├── Notifications > Enrichment Alerts (premium toggle)
└── Account > Manage Subscription
```

---

## 9) Accessibility

### 9.1 VoiceOver Labels

| Element | VoiceOver announcement |
|---------|----------------------|
| Who Viewed Me teaser (free) | "Who Viewed Me. 3 people viewed your profile this week. Premium feature. Double-tap to learn more." |
| How Am I Stored teaser (free) | "How Am I Stored. Stored by 45 contacts. Premium feature. Double-tap to learn more." |
| Enrichment digest (free) | "Enrichment digest. 5 contacts updated their info this month. Premium feature. Double-tap to learn more." |
| Lock icon | "Premium feature" (accessibilityLabel on the icon; not read as "lock") |
| Viewer row (PREM1) | "Sarah Chen. Viewed 2 hours ago. 3 views this week. Double-tap to view profile." |
| Anonymous viewer row | "Anonymous viewer. Viewed 3 days ago. This viewer browses anonymously." |
| Name variant row (PREM2) | "John Doe. 23 contacts. High confidence. Double-tap for details." |
| Confidence indicator | "High confidence" / "Medium confidence" / "Low confidence" |
| Enrichment feed item (PREM3) | "Sarah Chen. Phone number changed. 2 hours ago. Double-tap to view contact." |
| Time range selector (PREM1) | "Time range. This Week selected. This Month." (standard segmented control accessibility) |
| Filter dropdowns (PREM3) | "Filter by recency. All selected." / "Filter by field type. All selected." / "Filter by circle. All selected." |
| Anonymous browsing toggle | "Browse anonymously. Off. When enabled, you won't appear in others' viewer lists, but you won't see who views your profile." |

### 9.2 Dynamic Type

- All text scales with Dynamic Type up to AX5.
- Viewer list rows, name variant rows, and enrichment feed items use multi-line layout at larger text sizes.
- Avatar sizes remain fixed at `md` (40pt) in list views — does not scale with Dynamic Type.
- Confidence indicators use text labels at AX3+ sizes (dot alone is insufficient).
- Summary stats wrap to multiple lines at larger sizes.

### 9.3 Reduced Motion

- When "Reduce Motion" is enabled: the blurred-preview-to-paywall transition uses a simple cross-dissolve instead of the spring scale animation.
- Score ring animations and card transitions respect the system setting per `IOS_DESIGN_TOKENS_V1.md` motion tokens.

### 9.4 Color and Contrast

- Confidence indicators (High/Medium/Low) do not rely solely on color. Each has a distinct text label alongside the colored dot.
- Lock icon uses `rin.text.secondary` which meets WCAG AA contrast ratio (4.5:1) against both `rin.bg.primary` and `rin.bg.secondary` in light and dark modes.
- Blurred preview maintains sufficient contrast for the visible count text above the blur layer.

---

## 10) Events

### 10.1 Premium Feature Discovery (Free Tier)

| Event | Properties | Trigger |
|-------|-----------|---------|
| `premium.feature_tapped_free` | `feature`: "who_viewed_me" / "how_am_i_stored" / "enrichment_alerts" | Free user taps any premium-locked section |
| `premium.paywall_shown` | `trigger_feature`: string, `source_screen`: string | Paywall presented |
| `premium.paywall_dismissed` | `trigger_feature`: string | Paywall closed without purchase |

### 10.2 Premium Feature Usage

| Event | Properties | Trigger |
|-------|-----------|---------|
| `premium.feature_viewed` | `feature`: "who_viewed_me" / "how_am_i_stored" / "enrichment_alerts" | Premium user opens a premium feature screen |
| `premium.viewer_list_viewed` | `time_range`: "week" / "month", `viewer_count`: int | PREM1 screen loaded with data |
| `premium.viewer_profile_tapped` | `viewer_type`: "contact" / "rin_user" / "anonymous", `contact_id`: string? | Tap a viewer row in PREM1 |
| `premium.stored_names_viewed` | `variant_count`: int, `total_contacts`: int | PREM2 screen loaded with data |
| `premium.stored_name_variant_tapped` | `variant`: string, `contact_count`: int, `confidence`: "high" / "medium" / "low" | Tap a name variant row in PREM2 |
| `premium.enrichment_feed_viewed` | `item_count`: int, `filters_applied`: dict | PREM3 screen loaded |
| `premium.enrichment_item_tapped` | `contact_id`: string, `field_changed`: string | Tap an enrichment feed item |
| `premium.enrichment_notification_tapped` | `contact_id`: string, `field_changed`: string | Tap enrichment push notification |

### 10.3 Privacy and Settings

| Event | Properties | Trigger |
|-------|-----------|---------|
| `premium.opt_out_anonymous_browsing` | `enabled`: bool | User toggles anonymous browsing |
| `premium.enrichment_notifications_toggled` | `enabled`: bool | User toggles enrichment push notifications |

---

## 11) States Summary

### 11.1 PREM1: Who Viewed Me

| State | Condition | Display |
|-------|-----------|---------|
| Loading | Data fetch in progress | Skeleton rows (3 placeholder rows with shimmer) |
| Populated | Viewer data available | Viewer list with summary stats |
| Empty | No views in selected period | Empty state with profile tip |
| Anonymous active | User has anonymous browsing on | Anonymous browsing notice with settings CTA |
| Error | Network/server failure | "Can't load viewer data. Your local data is safe." with retry button |

### 11.2 PREM2: How Am I Stored

| State | Condition | Display |
|-------|-----------|---------|
| Loading | Data fetch in progress | Skeleton rows with shimmer |
| Populated | Name variant data available | Variant list with summary |
| Low data | Fewer than 5 contacts in graph | Empty state with "not enough data" message |
| Error | Network/server failure | Error message with retry button |

### 11.3 PREM3: Enrichment Alerts

| State | Condition | Display |
|-------|-----------|---------|
| Loading | Data fetch in progress | Skeleton rows with shimmer |
| Populated | Enrichment items available | Grouped feed with filters |
| Empty | No enrichments detected | Empty state message |
| Filtered empty | Filters applied, no matching items | "No updates match these filters" |
| Error | Network/server failure | Error message with retry button |

---

## 12) Copy Reference

All copy follows the brand voice from `BRAND_NARRATIVE_V1.md`. Key rules applied:
- "Get Premium" not "Unlock Premium" (banned word: "unlock").
- No exclamation marks.
- State facts, not feelings.
- Short sentences. 12 words max for UI copy.

### 12.1 Section Headers (Score Home Teasers)

| Feature | Header copy |
|---------|------------|
| Who Viewed Me | "WHO VIEWED ME" |
| How Am I Stored | "HOW AM I STORED" |
| Enrichment Digest | "ENRICHMENT DIGEST" |

### 12.2 Teaser Body Copy

| Feature | Body copy |
|---------|----------|
| Who Viewed Me (has views) | "{N} people viewed your profile this week" |
| Who Viewed Me (no views) | "No profile views this week" |
| How Am I Stored (has data) | "Stored by {N} contacts" |
| How Am I Stored (low data) | "Not enough data yet" |
| Enrichment Digest (has items) | "{N} contacts updated their info this month" |

### 12.3 Screen Titles

| Screen | Title |
|--------|-------|
| PREM1 | "Who Viewed Me" |
| PREM2 | "How Am I Stored" |
| PREM2 sub | The variant string in quotes (e.g., "John Doe") |
| PREM3 | "Enrichment Alerts" |

### 12.4 Empty State Copy

| Screen | Heading | Body |
|--------|---------|------|
| PREM1 (no views) | "No profile views this {period}." | "A complete profile with a photo and verified contact info tends to get more views." |
| PREM1 (anonymous on) | "Anonymous browsing is on." | "You're browsing profiles without appearing in viewer lists. To see who views your profile, turn off anonymous browsing." |
| PREM2 (low data) | "Not enough data yet." | "As more of your contacts join Rin, you'll see how they store your name and contact info." |
| PREM3 (no items) | "No enrichment updates yet." | "When your contacts update their info, changes appear here." |
| PREM3 (filter empty) | "No updates match these filters." | "Try adjusting your selection." |

### 12.5 Privacy Notices

| Location | Copy |
|----------|------|
| PREM1 footer | "Viewers who browse anonymously are not shown. You can enable anonymous browsing in Settings." |
| PREM2 footer | "This data is derived from contacts who have your phone number or email. Rin does not access anyone's contact book directly." |
| Anonymous browsing toggle | "When enabled, you won't appear in others' viewer lists. In return, you won't see who views your profile." |
| Anonymous browsing detail | "This applies to all profiles you view going forward. Past views are not retroactively hidden." |

---

## 13) Open Decisions

1. **Viewer count display for free tier** — Whether the free teaser should show the exact viewer count (e.g., "3 people") or a rounded range (e.g., "a few people") to increase premium conversion without feeling manipulative.

2. **Who Viewed Me: non-Rin viewers** — Whether to include profile views from web-based profile pages (if implemented) or limit to in-app views only. Web views would increase the count but introduce attribution complexity.

3. **How Am I Stored: minimum threshold** — The current threshold is 5 contacts before showing variant data. Whether this should be higher (10) to prevent easy de-anonymization in small networks, or lower (3) to deliver value sooner.

4. **Enrichment Alerts: change detail granularity** — Whether to show the old and new values for a changed field ("Phone: +1-555-1234 changed to +1-555-5678") or only that the field changed ("Phone number changed"). Showing values is more useful but raises privacy questions if the contact didn't intend to share the change.

5. **Cross-feature bundling** — Whether premium features should be purchasable individually (e.g., "Who Viewed Me" only for $1.99/mo) or only as a bundle. Individual pricing increases flexibility but adds StoreKit complexity and paywall design burden.

6. **Viewer list: repeat view threshold** — Whether to deduplicate repeat views from the same person within a time window (e.g., collapse 5 views in one hour to "Viewed 1 hour ago, 5 times") or show each view as a separate event. Collapsing is cleaner but may undercount perceived engagement.
