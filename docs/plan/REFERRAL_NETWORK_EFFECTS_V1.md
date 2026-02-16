# Referral and Network Effects Strategy V1

## 1) Purpose

Define the referral mechanics, network effects model, viral coefficient targets, natural share moments, and phased implementation plan for Rin's organic growth engine.

Primary incentive model: invite 3 friends who install and import contacts, receive 1 month of premium free.

Companion docs:
- `docs/plan/ICP_MESSAGING_PILLARS_V1.md` (messaging framework)
- `docs/plan/IAP_SUBSCRIPTION_COMPLIANCE_V1.md` (premium tier and StoreKit)
- `docs/analytics/PRODUCT_ANALYTICS_EVENT_TAXONOMY_V1.md` (event definitions)
- `docs/analytics/KPI_HIERARCHY_V1.md` (viral coefficient targets)
- `docs/plan/BETA_COHORT_STRATEGY_V1.md` (staged rollout)

---

## 2) Referral Mechanics

### 2.1 Invite Flow UX

**Entry points** (user initiates an invite):

| Entry point | Context |
|-------------|---------|
| Settings > Invite Friends | Intentional sharing |
| Score milestone card > Share | Achievement moment |
| Dedup complete card > Share | Value-delivered moment |
| Import summary card > Share | Onboarding completion |
| Premium upsell screen > "Or invite friends" | Free alternative to payment |

**Invite flow:**

```
User taps "Invite Friends"
    |
Show invite dashboard:
    - Progress bar: "X of 3 friends joined" (toward 1 month premium)
    - Current tier and next reward
    - List of pending/completed referrals (first name + status)
    |
User taps "Send Invite"
    |
Generate unique referral link:
    - Format: rin.app/r/<short_code>
    - Short code: 8-character alphanumeric, tied to referrer principal ID
    - Encodes referrer ID, creation timestamp, campaign tag
    |
Present iOS share sheet:
    - Pre-filled message: "I've been using Rin to clean up my contacts and map my network. Try it free: [link]"
    - User can edit message before sending
    - Supports: iMessage, WhatsApp, Telegram, email, copy link, AirDrop
    |
Track share method (analytics only, no content inspection)
```

**Referral link behavior:**
- Opens App Store listing on iOS (universal link with App Store fallback).
- On first launch after install, app reads deferred deep link to attribute referral.
- Uses Apple's App Clips / SKAdNetwork attribution where available; falls back to server-side link resolution.

### 2.2 Referral Link Tracking

| Component | Implementation |
|-----------|---------------|
| Link generation | Server-side; unique per referrer, reusable across sends |
| Attribution | Deferred deep link resolved on first app launch |
| Qualification | Referred user must: (1) install, (2) complete onboarding, (3) import contacts |
| Status states | `sent` > `clicked` > `installed` > `qualified` > `rewarded` |
| Dashboard | In-app screen showing referral status per invited user |

### 2.3 Reward Structure

**Primary reward: invite 3 qualified friends, get 1 month premium free.**

Qualification criteria for a referred friend to count:
1. Install Rin via the referral link.
2. Complete phone verification and onboarding.
3. Grant contacts permission and complete initial import (minimum 10 contacts imported).
4. Remain active for at least 3 days after signup (opened app on 3 distinct days within first 14 days).

**Reward tiers:**

| Qualified referrals | Reward | Cumulative premium |
|---------------------|--------|-------------------|
| 3 | 1 month premium free | 1 month |
| 5 | +1 month premium free | 2 months |
| 10 | +1 month premium free | 3 months |
| 25 | +3 months premium free | 6 months |
| 50 | Lifetime premium (or 12 months, see open decisions) | 6-12+ months |

**Reward delivery:**
- Premium credit applied automatically when threshold is crossed.
- If user already has an active paid subscription, credit extends the subscription end date.
- If user is on the free tier, premium unlocks immediately for the credited duration.
- Credits stack; they do not expire.
- Notification sent on each reward unlock: "Your friend [first name] joined Rin. You've earned 1 month of premium!"

**Referred user reward:**
- The invited friend also receives a benefit: 7-day premium trial (regardless of whether a trial is normally offered).
- This creates a two-sided incentive.

### 2.4 Fraud Prevention

| Vector | Prevention |
|--------|-----------|
| **Self-referral (multiple accounts)** | Minimum activity threshold: 3 distinct days active within 14 days. Rate-limit: max 1 new account per device (device fingerprint via `identifierForVendor`). Same-device referral and referee rejected. |
| **Fake accounts** | Referral only qualifies after contact import of 10+ real contacts (non-duplicate, non-empty records). Phone verification required (real phone number). |
| **Burner phones** | Qualification requires sustained activity (3 days active), not just install-and-abandon. |
| **Referral farms** | Cap rewards at 50 qualified referrals (lifetime maximum per user). Flag accounts with >10 referrals in a 7-day window for manual review. |
| **Shared device abuse** | `identifierForVendor` tracking. Multiple accounts on same device do not generate referral credit. |
| **VPN/geo manipulation** | Not a primary concern in V1; phone verification is the trust anchor. Monitor if patterns emerge. |

**Fraud review process:**
- Automated: referrals from flagged accounts are held in `pending_review` state.
- Manual: founder reviews flagged accounts weekly (Stage 3). Automate at scale.
- Clawback: if a referred user is determined fraudulent within 30 days, premium credit is revoked.

### 2.5 Attribution Window

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Link validity | 30 days from generation | Covers the typical "I'll download it later" window |
| Install attribution | 7 days from link click | Aligns with standard mobile attribution windows |
| Qualification deadline | 14 days from install | User must meet activity threshold within 2 weeks |
| Multi-touch | Last-click attribution | If user clicks multiple referral links, credit goes to the most recent referrer |

Links do not expire for the referrer (they can reshare the same link), but the attribution window for any given click resets on each new click.

---

## 3) Network Effects Model

### 3.1 Direct Network Effects

Rin's contact graph becomes more valuable as more users join. This is the core growth flywheel.

```
More users join
    |
More contact graphs imported
    |
Higher graph overlap (reciprocal edges)
    |
Better scores (Quality component rewards reciprocity)
    |
Better dedup (cross-user canonical matching)
    |
More value delivered per user
    |
Higher retention and more invites
    |
(cycle repeats)
```

**Specific value unlocks as network grows:**

| Network milestone | Value unlocked |
|-------------------|---------------|
| 2 mutual users | Reciprocity edges appear; Quality component activates |
| 5 mutual users | Bridge positions detectable; Position component improves |
| 20+ mutual users | Cluster patterns visible; circle suggestions improve |
| 100+ in local graph | Enrichment accuracy increases; dedup confidence rises |
| 1,000+ in local graph | "Who Viewed Me" becomes meaningful; social proof strong |

### 3.2 Data Network Effects

More aggregate data (across all users, privacy-preserving) improves the product for everyone:

| Data signal | Improvement |
|-------------|-------------|
| **Contact dedup** | More canonical records = higher confidence matching. Cross-user signal (A and B both have "John Smith" with same phone) confirms identity without exposing data. |
| **Enrichment** | Aggregated contact metadata (job titles, companies, cities) improves field suggestions and auto-fill accuracy. |
| **Spam/abuse detection** | More users reporting the same number/contact pattern = faster abuse identification. |
| **Score calibration** | Larger population enables better percentile ranking and score distribution tuning. |

**Privacy boundary:** Data network effects are derived from aggregate, anonymized signals. No individual contact data is shared between users without consent. The system operates on hashed identifiers and statistical patterns, not plaintext PII.

### 3.3 Communicating Network Value to Users

Users should understand that inviting friends directly improves their own experience, beyond just the premium reward.

**In-product messaging:**

| Context | Message |
|---------|---------|
| Score screen (low reciprocity) | "Your score improves when your contacts join Rin. Invite friends to unlock reciprocal connections." |
| Contact detail (non-Rin user) | "If [first name] joins Rin, you'll see mutual connection strength and richer profile data." |
| Post-invite dashboard | "When your friends join, your network graph gets stronger. More mutual connections = better scores." |
| Score increase after friend joins | "[First name] joined Rin. Your Quality score just improved because of a new mutual connection." |
| Weekly score summary | "This week, 2 of your contacts joined Rin. Your reciprocity ratio improved by 8%." |

**Key principle:** Frame invitations as *mutual benefit*, not extraction. "Your network improves" not "help us grow." This aligns with the privacy-first messaging pillar.

### 3.4 Critical Mass Thresholds

Network effects have thresholds below which they are not perceptible to individual users.

| Threshold | User count | Network state | Strategy |
|-----------|-----------|---------------|----------|
| **Cold start** | 0-50 | No network effects. Single-player value only (dedup, cleanup, organization). | Lean entirely on single-player utility. Do not promise network value. |
| **Early signal** | 50-500 | Sparse reciprocal edges. Some users see 1-2 mutual connections. | Highlight any mutual connections prominently. Celebrate network moments. |
| **Local density** | 500-5,000 | Clusters form in specific communities (city, industry, company). Graph effects visible to power users. | Enable "X people in your contacts use Rin" social proof. Target cluster growth. |
| **Self-sustaining** | 5,000-50,000 | Most active users have 5+ mutual connections on Rin. Reciprocity drives meaningful score differentiation. Network value obvious without explanation. | Reduce referral incentive weight; organic spread dominates. |
| **Mainstream** | 50,000+ | Network effects are the primary value driver. Rin without the network is significantly less useful. | Shift messaging from utility to network intelligence. |

**Pre-critical-mass strategy:**
During cold start and early signal phases, Rin must deliver strong single-player value (dedup, cleanup, organization, access control). The referral program supplements growth but the product must not depend on network effects for retention until local density is achieved.

---

## 4) Viral Coefficient Targets

### 4.1 K-Factor Formula

```
K = i * c

Where:
  i = average invites sent per user per viral cycle
  c = conversion rate (% of invite recipients who become qualified users)
```

**Target values:**

| Phase | i (invites/user) | c (conversion) | K | Interpretation |
|-------|-----------------|----------------|---|----------------|
| Stage 3 beta | 3.0 | 0.20 | 0.60 | Healthy organic supplement |
| Public launch | 2.5 | 0.25 | 0.63 | Improving conversion offsets lower invite volume |
| Growth phase | 2.0 | 0.30 | 0.60 | Stable organic supplement to other channels |
| Aspirational | 3.0 | 0.35 | 1.05 | Self-sustaining viral growth (rare for utility apps) |

**K > 1.0** means every user brings in more than one new user, creating exponential growth. This is aspirational but not required. **K > 0.5** is a strong organic supplement that meaningfully reduces customer acquisition cost.

**Realistic expectations:** Contact/utility apps typically achieve K = 0.3-0.7. Social apps with strong share moments can reach K = 0.8-1.5. Rin's target of K > 0.5 is ambitious but achievable with the referral incentive plus natural share moments.

### 4.2 Viral Cycle Time

Viral cycle time (ct) is the average time between when a user joins and when their invited contacts become qualified users.

```
Viral cycle time = time_to_first_invite + recipient_decision_time + install_to_qualification

Estimated:
  time_to_first_invite: 2-5 days (user discovers invite flow or share moment)
  recipient_decision_time: 1-3 days (recipient clicks link and installs)
  install_to_qualification: 3-7 days (3 days active within 14 days)

Total estimated ct: 6-15 days
Target ct: <10 days
```

**Effective viral growth rate** = K^(1/ct). A lower cycle time amplifies the same K-factor significantly.

**Strategies to reduce cycle time:**
1. Surface invite flow early (during onboarding completion, not buried in settings).
2. Share moments trigger within first session (dedup results, import summary).
3. Push notification when referred friend installs (keeps referrer engaged).
4. Lower qualification bar where safe (3 days active is already lean).

### 4.3 Measurement Methodology

**Weekly viral coefficient calculation:**

```
K_weekly = (invites_sent_this_week / active_users_this_week) *
           (qualified_referrals_this_week / invites_sent_this_week)
```

**Rolling 30-day viral coefficient** (preferred, less noisy):

```
K_30d = (invites_sent_last_30d / MAU) *
        (qualified_referrals_last_30d / invites_sent_last_30d)
```

**PostHog implementation:**
- Track via existing events: `invite_sent`, `invite_accepted` (extended with `invite_qualified` for full qualification).
- Dashboard: viral coefficient trend line, invite funnel breakdown, cycle time distribution.

**New events to add to taxonomy (see section 7.3):**

| Event | Properties | Trigger |
|-------|-----------|---------|
| `referral_link_generated` | `referrer_id`, `campaign` | Unique link created |
| `referral_link_clicked` | `referrer_id`, `platform` | Recipient clicks link |
| `referral_qualified` | `referrer_id`, `referee_id`, `days_to_qualify` | Referee meets all criteria |
| `referral_reward_granted` | `referrer_id`, `tier`, `premium_months` | Premium credit applied |
| `referral_dashboard_viewed` | `pending_count`, `qualified_count`, `tier` | User views referral status |

---

## 5) Share Moments

Natural share triggers are product moments where a user feels compelled to share. These are more powerful than generic "invite a friend" prompts because they carry social proof and authentic enthusiasm.

### 5.1 Score Milestone

**Trigger:** User's Rin Score crosses a round-number threshold (e.g., 50, 60, 70, 75, 80, 85, 90, 95).

**UX:**
```
+--------------------------------------+
|                                      |
|     Your Rin Score just hit 85       |
|                                      |
|         [  85  ]                     |
|     Top 15% of Rin users             |
|                                      |
|   Network Quality    ████████░░  82  |
|   Network Position   ██████░░░░  64  |
|   Stability          █████████░  91  |
|   Trust              ██████████  98  |
|                                      |
|   [Share Score]    [Dismiss]         |
+--------------------------------------+
```

**Share output (pre-filled, editable):**
- Text: "My Rin Score just hit 85. How strong is your contact network?"
- Image: Generated score card (dark background, score number, component bars, Rin branding).
- Link: rin.app/score (lands on App Store / marketing page).

**When to show:** Immediately after daily score batch if a milestone was crossed. Maximum once per milestone (never re-show 85 after the first time).

### 5.2 Dedup Result

**Trigger:** User completes a dedup review session (merges or reviews 5+ suggestions).

**UX:**
```
+--------------------------------------+
|                                      |
|     Cleanup Complete                 |
|                                      |
|     47 duplicates found              |
|     38 merged automatically          |
|      9 reviewed by you               |
|                                      |
|     Your contacts are now            |
|     12% cleaner than average         |
|                                      |
|   [Share Result]    [Done]           |
+--------------------------------------+
```

**Share output:**
- Text: "Rin found 47 duplicate contacts I never noticed. My contact list just got way cleaner."
- Image: Generated cleanup summary card.
- Link: rin.app/cleanup

**When to show:** After the first dedup batch completion, and again after any session resolving 10+ suggestions. Maximum once per week.

### 5.3 Circle Insight

**Trigger:** User views their circle breakdown and has established circles with meaningful membership.

**UX:**
```
+--------------------------------------+
|                                      |
|     Your Inner Circle                |
|                                      |
|     12 closest contacts              |
|     based on mutual connections      |
|     and interaction strength         |
|                                      |
|     [See who's in it]               |
|                                      |
|   [Share Insight]    [Dismiss]       |
+--------------------------------------+
```

**Share output:**
- Text: "My closest 12 contacts according to Rin. Curious who's in yours?"
- Image: Abstract circle visualization (no names exposed; count + category breakdown only).
- Link: rin.app/circles

**When to show:** After user has 50+ contacts imported and views the circles tab. Maximum once per month.

### 5.4 Import Complete

**Trigger:** Initial contact import finishes with results worth sharing.

**UX:**
```
+--------------------------------------+
|                                      |
|     Network Mapped                   |
|                                      |
|     1,247 contacts imported          |
|       832 unique people              |
|        47 duplicates found           |
|         5 circles suggested          |
|                                      |
|   [Share]    [Start Exploring]       |
+--------------------------------------+
```

**Share output:**
- Text: "Just mapped my 1,247 contacts on Rin. Found 47 duplicates I never knew about."
- Image: Import summary card with count and dedup preview.
- Link: rin.app/start

**When to show:** Immediately after first import completes. One-time only.

### 5.5 Share Moment Prioritization

| Moment | Frequency | Virality potential | Phase |
|--------|-----------|-------------------|-------|
| Import complete | Once per user | High (first impression, high numbers are impressive) | Phase 2 |
| Dedup result | After major cleanups | High (tangible value, relatable pain) | Phase 2 |
| Score milestone | Per milestone reached | Medium (curiosity-driven, competitive) | Phase 2 |
| Circle insight | Monthly maximum | Medium (personal, intriguing) | Phase 3 |

### 5.6 Share Image Generation

All share moments generate a branded card image:
- Dark background with Rin brand colors.
- Key metric prominently displayed.
- Rin logo and "rin.app" watermark (subtle, bottom corner).
- Generated client-side (no server call needed).
- Aspect ratio: 1200x630px (optimized for iMessage/social previews).
- No PII: never include contact names, phone numbers, or other personal data in share images.

---

## 6) Implementation Plan

### 6.1 Phase 1: Basic Referral with Premium Reward (Stage 3 Beta)

**Scope:** Core referral loop functional. No share moments yet.

**Build:**
- [ ] Server: referral link generation endpoint (`POST /referral/link`).
- [ ] Server: referral attribution service (deferred deep link resolution).
- [ ] Server: qualification tracking (import + activity threshold).
- [ ] Server: reward ledger (premium credit application, stacking, expiry tracking).
- [ ] iOS: "Invite Friends" screen in Settings tab.
- [ ] iOS: referral dashboard (progress bar, pending/qualified list).
- [ ] iOS: share sheet integration with pre-filled message and referral link.
- [ ] iOS: push notification on referral status change (installed, qualified, rewarded).
- [ ] Analytics: instrument `referral_link_generated`, `referral_link_clicked`, `referral_qualified`, `referral_reward_granted`.
- [ ] Fraud: device fingerprint check, activity threshold validation, referral cap enforcement.

**Success criteria:**
- Invite send rate > 1.5 per active user per month.
- Invite-to-install conversion > 20%.
- Install-to-qualification conversion > 50%.
- Zero fraud incidents in first 4 weeks.

**Timeline:** Build during Stage 2 stabilization, launch at Stage 3 start.

### 6.2 Phase 2: Share Moments and Social Proof (Stage 3 Weeks 2-4)

**Scope:** Natural share triggers active. Share card generation. Social proof counters.

**Build:**
- [ ] iOS: share card image generator (client-side rendering).
- [ ] iOS: score milestone detection and share prompt.
- [ ] iOS: dedup completion share prompt.
- [ ] iOS: import complete share prompt.
- [ ] iOS: "X of your contacts use Rin" counter on contacts list (privacy-safe, hashed matching).
- [ ] Analytics: instrument `app_shared` with `content_type` property for each share moment.
- [ ] A/B test: share prompt copy and timing variants.

**Success criteria:**
- At least 20% of users trigger one share moment in first 30 days.
- Share moment invites convert at > 25% (higher than generic invites).
- Share cards are actually sent (not just generated) > 60% of the time.

**Timeline:** Iterative during Stage 3.

### 6.3 Phase 3: Network Value Messaging (Post-Launch)

**Scope:** Explicit communication of network effects. Network growth becomes part of the product narrative.

**Build:**
- [ ] iOS: "Your network is growing" feed/cards on home screen.
- [ ] iOS: score attribution ("Your score improved because [name] joined").
- [ ] iOS: contact detail enrichment indicator ("On Rin" badge for contacts who are users).
- [ ] iOS: weekly network summary push notification ("2 contacts joined Rin this week. Your reciprocity improved.").
- [ ] Server: compute and surface per-user network growth metrics.
- [ ] Messaging: update onboarding copy to reference network value (only after local density threshold is reached).

**Success criteria:**
- Users who receive "friend joined" notifications retain at D30 > 25% (vs baseline).
- Network value messaging increases invite send rate by > 20%.
- Score attribution messages are viewed by > 50% of eligible users.

**Timeline:** Post public launch, iterate based on network density data.

---

## 7) Analytics and Measurement

### 7.1 Referral Funnel

```
referral_link_generated
    -> referral_link_clicked
    -> onboarding_started (source=invite)
    -> onboarding_completed
    -> contact_import_completed
    -> referral_qualified (3 days active within 14 days)
    -> referral_reward_granted
```

### 7.2 Share Moment Funnel

```
[share_moment]_shown (e.g., score_milestone_shown)
    -> share_sheet_opened
    -> app_shared (method=iMessage/WhatsApp/etc.)
    -> referral_link_clicked (from shared link)
    -> onboarding_started (source=share_moment)
```

### 7.3 New Events (Additions to Event Taxonomy)

| Event | Properties | Trigger |
|-------|-----------|---------|
| `referral_link_generated` | `campaign` (generic/share_moment), `source_screen` | Referral link created |
| `referral_link_clicked` | `referrer_id`, `platform` (web/app), `days_since_generation` | Recipient clicks link |
| `referral_qualified` | `referrer_id`, `referee_id`, `days_to_qualify`, `contacts_imported` | Referee meets qualification |
| `referral_reward_granted` | `referrer_id`, `tier` (3/5/10/25/50), `premium_months_granted`, `total_premium_earned` | Premium credit applied |
| `referral_dashboard_viewed` | `pending_count`, `qualified_count`, `current_tier` | Referral status screen opened |
| `share_moment_shown` | `moment_type` (score_milestone/dedup_result/circle_insight/import_complete), `value` | Share card displayed |
| `share_moment_shared` | `moment_type`, `method` (iMessage/whatsapp/copy/other) | User shares via share sheet |
| `share_moment_dismissed` | `moment_type` | User dismisses share card |

### 7.4 Key Dashboards

| Dashboard | Metrics | Build phase |
|-----------|---------|-------------|
| **Referral Health** | K-factor (weekly + 30d rolling), viral cycle time, invite-to-qualified conversion | Phase 1 |
| **Referral Funnel** | Step-by-step conversion: generated > clicked > installed > qualified > rewarded | Phase 1 |
| **Share Moments** | Shown rate, share rate, conversion per moment type | Phase 2 |
| **Network Density** | Average mutual connections, reciprocity ratio, "on Rin" percentage of contacts | Phase 3 |
| **Fraud Monitor** | Flagged accounts, same-device attempts, referral velocity outliers | Phase 1 |

---

## 8) App Store Compliance

Referral programs must comply with Apple's App Store Review Guidelines:

| Requirement | Implementation |
|-------------|---------------|
| No incentivized reviews | Referral reward is for friend joining, never for App Store ratings |
| No misleading claims | Share cards show factual data only (actual scores, actual dedup counts) |
| Premium credit via server | Premium entitlement managed server-side; not a StoreKit promotional offer |
| Transparent terms | Referral terms accessible from invite dashboard ("How referrals work" link) |
| No spam | Share sheet is user-initiated; no automatic message sending; no contact list scraping for invites |

**Premium credit implementation note:** Referral-earned premium is applied server-side as a time-based entitlement extension, not as a StoreKit promotional offer or subscription modification. The client checks server-side entitlement status on launch, same as paid subscriptions. This avoids StoreKit compliance issues with non-App-Store premium grants.

---

## 9) Referral Terms (User-Facing)

Accessible from the invite dashboard via "How referrals work" link:

1. Share your unique link with friends.
2. When a friend installs Rin using your link, verifies their phone, and imports their contacts, they become a qualified referral.
3. Your friend must use Rin for at least 3 days within their first 2 weeks.
4. Invite 3 qualifying friends to earn 1 month of Rin Premium free.
5. Additional invites unlock more premium time (5 friends = 2 months, 10 friends = 3 months).
6. Premium credits are applied automatically and stack with existing subscriptions.
7. Premium credits do not expire.
8. Maximum 50 qualifying referrals per account.
9. Rin reserves the right to revoke credits from fraudulent referrals.

---

## 10) Open Decisions

1. Whether the top referral tier (50 qualified referrals) should grant lifetime premium or a fixed duration (e.g., 12 months).
2. Whether referred users should also get a benefit (proposed: 7-day premium trial). This doubles the incentive cost but may improve conversion significantly.
3. Whether to implement a leaderboard or public referral count (social proof vs. privacy concerns).
4. Whether referral links should be personalized with the referrer's name ("Nan invited you to Rin") or generic.
5. Whether to allow users to customize their referral link slug (e.g., rin.app/r/nan) for power referrers.
6. Whether to implement referral tiers as a permanent program or a limited-time launch promotion.
7. Whether share moment images should include the user's profile photo or remain abstract.
8. Whether the qualification threshold (3 days active in 14 days) is too strict or too lenient; needs calibration with Stage 3 data.
9. Whether to integrate with iOS Contact Suggestions API to surface Rin in the share sheet for specific contacts.
10. Whether the viral coefficient target in the KPI hierarchy (currently >1.0 in `KPI_HIERARCHY_V1.md`) should be revised to >0.5 as the realistic target, with >1.0 as aspirational.
