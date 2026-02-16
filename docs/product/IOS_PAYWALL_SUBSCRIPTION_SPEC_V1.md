# iOS Paywall and Subscription Behavior Spec V1

## 1) Purpose

Define the complete subscription UX from discovery through purchase, management, and cancellation. Covers paywall entry points, contextual variants, StoreKit 2 integration, feature gating, subscription lifecycle, and analytics instrumentation.

Companion docs:
- `docs/design/IOS_KEY_SCREEN_WIREFRAMES_V1.md` (wireframe reference, section 10)
- `docs/plan/IAP_SUBSCRIPTION_COMPLIANCE_V1.md` (pricing, StoreKit 2, compliance)
- `docs/architecture/IOS_NAVIGATION_STATE_V1.md` (deep link: `rin://premium`)
- `docs/product/IOS_SCORE_EXPLANATION_SCREEN_SPEC_V1.md` (premium sections as entry points)
- `docs/design/BRAND_NARRATIVE_V1.md` (tone guide)
- `docs/design/IOS_DESIGN_TOKENS_V1.md` (visual tokens)
- `docs/analytics/KPI_HIERARCHY_V1.md` (conversion targets)
- `docs/analytics/PRODUCT_ANALYTICS_EVENT_TAXONOMY_V1.md` (event naming)

---

## 2) Paywall Screen (PAY1)

### 2.1 Layout

```
┌──────────────────────────────────────┐
│                              [✕]    │
│                                      │
│         ⭐ Get Premium               │
│                                      │
│  ┌──────────────────────────────────┐│
│  │ 👀  Who Viewed Me               ││
│  │ See who checked your profile    ││
│  │ this week                        ││
│  └──────────────────────────────────┘│
│                                      │
│  ┌──────────────────────────────────┐│
│  │ ✨  Enrichment Alerts           ││
│  │ Know when contact info updates  ││
│  └──────────────────────────────────┘│
│                                      │
│  ┌──────────────────────────────────┐│
│  │ 📋  How Am I Stored             ││
│  │ See how others save your info   ││
│  └──────────────────────────────────┘│
│                                      │
│  ┌──────────┐  ┌──────────────────┐ │
│  │  $4.99   │  │  $49.99/year    │ │
│  │  /month  │  │  Save 16% ★     │ │
│  └──────────┘  └──────────────────┘ │
│                                      │
│  Auto-renews. Cancel anytime.        │
│                                      │
│        [Subscribe Now]               │
│                                      │
│   Restore Purchases                  │
│   Terms  ·  Privacy Policy           │
└──────────────────────────────────────┘
```

### 2.2 Component Breakdown

| Element | Token / Style | Notes |
|---------|---------------|-------|
| Close button (X) | Top-right, `rin.space.base` inset | Always visible. Tappable area 44x44pt minimum. |
| Header "Get Premium" | `rin.type.title1`, bold | "Get" not "Unlock" (banned word per brand narrative). Star icon left of text. |
| Feature cards (x3) | `rin.radius.lg` corners, `rin.bg.secondary` fill | 16pt internal padding (`rin.space.base`). |
| Feature card icon | SF Symbol, `rin.brand.accent` tint | `eye` (Who Viewed Me), `sparkles` (Enrichment), `doc.text` (How Am I Stored). |
| Feature card title | `rin.type.headline`, semibold | Feature name. |
| Feature card description | `rin.type.callout`, `rin.text.secondary` | One sentence. Under 12 words. |
| Pricing cards | Side-by-side, equal width | Monthly left, Annual right. |
| Monthly card | `rin.border.default` border, `rin.radius.md` | Shows `Product.displayPrice` + "/month". |
| Annual card | `rin.brand.primary` border (2pt), `rin.radius.md` | Shows `Product.displayPrice` + "/year" + "Save 16%" + star badge. Pre-selected. |
| "Subscribe Now" CTA | `PrimaryButton`, full width | `rin.brand.primary` fill, white text. Title Case. |
| Auto-renewal disclosure | `rin.type.footnote`, `rin.text.secondary` | "Auto-renews. Cancel anytime." Required by Apple. |
| "Restore Purchases" | `rin.type.callout`, `rin.brand.primary` text | Tappable text link. Not a button. |
| "Terms" / "Privacy Policy" | `rin.type.footnote`, `rin.text.secondary` | Open respective web URLs in SFSafariViewController. |

### 2.3 Presentation

- Presented as `.fullScreenCover` (per navigation spec, section 5.1).
- No swipe-to-dismiss (intentional; user must tap X).
- Background: `rin.bg.primary`.
- Content is vertically scrollable if it overflows (Dynamic Type large sizes).

### 2.4 Copy Rules

Per brand narrative section 6.4 (Premium Upsell):
- Describe features factually. No anxiety-inducing language.
- Never use "unlock," "exclusive," or "limited time."
- No countdowns, flashing elements, or nagging.
- Always provide dismissal without friction.

---

## 3) Entry Points

Every location in the app where the paywall can be triggered.

### 3.1 Entry Point Map

| ID | Location | Trigger | Context Passed | Feature Emphasized |
|----|----------|---------|----------------|--------------------|
| EP1 | Score Home (SC1) | Tap "Who Viewed Me" section | `source: "score_who_viewed"` | Who Viewed Me |
| EP2 | Score Home (SC1) | Tap "How Am I Stored" section | `source: "score_how_stored"` | How Am I Stored |
| EP3 | Profile Home (P1) | Tap "Premium" row in Account section | `source: "profile_premium"` | None (neutral) |
| EP4 | Settings | Tap "Premium" row in Account section | `source: "settings_premium"` | None (neutral) |
| EP5 | Enrichment notification | Tap push notification (free tier) | `source: "enrichment_notification"` | Enrichment Alerts |
| EP6 | Deep link | `rin://premium` | `source: "deep_link"` | None (neutral) |
| EP7 | Deep link with param | `rin://premium?feature=who_viewed` | `source: "deep_link"`, `feature` | Specified feature |

### 3.2 Navigation Behavior

```
Entry point tapped
    ↓
Check PremiumService.isSubscribed
    ↓
├── If subscribed → Navigate directly to feature content
│   (Who Viewed Me list, How Am I Stored list, etc.)
│
└── If not subscribed → Present PAY1 as fullScreenCover
    Pass entry point context to PaywallViewModel
```

### 3.3 Entry Point Rules

1. Paywall never appears during onboarding.
2. Paywall never blocks core app functionality (score viewing, dedup, circles, contacts).
3. Max one paywall presentation per session after user dismisses. If the user dismissed PAY1 in this session, subsequent premium feature taps show a brief inline message ("This is a premium feature") instead of re-presenting the full paywall. The user can still access PAY1 from Settings or Profile.
4. If the user is already subscribed, tapping a premium feature navigates directly to the feature content. No paywall shown.

---

## 4) Contextual Paywall Variants

### 4.1 Emphasis Behavior

When the paywall is triggered from a specific feature entry point, that feature card receives visual emphasis.

| Entry Source | Emphasized Card | Visual Treatment |
|-------------|-----------------|------------------|
| `score_who_viewed` | Who Viewed Me | Card has `rin.brand.accent` left border (3pt), other cards at 80% opacity |
| `score_how_stored` | How Am I Stored | Card has `rin.brand.accent` left border (3pt), other cards at 80% opacity |
| `enrichment_notification` | Enrichment Alerts | Card has `rin.brand.accent` left border (3pt), other cards at 80% opacity |
| `profile_premium` | None | All cards equal presentation (full opacity, no accent border) |
| `settings_premium` | None | All cards equal presentation |
| `deep_link` (no param) | None | All cards equal presentation |
| `deep_link` (with param) | Matching feature | Same accent treatment as above |

### 4.2 Feature Blurred Preview (Teaser)

When a free-tier user taps a premium section on Score Home:

```
┌──────────────────────────────────────┐
│ 👀 WHO VIEWED ME (3)       [🔒]    │
├──────────────────────────────────────┤
│                                      │
│  ┌──────────────────────────────────┐│
│  │  ░░░░░░░░░░  ←  blurred name   ││
│  │  ░░░░░░      ←  blurred time   ││
│  └──────────────────────────────────┘│
│  ┌──────────────────────────────────┐│
│  │  ░░░░░░░░░░░░                   ││
│  │  ░░░░░                          ││
│  └──────────────────────────────────┘│
│  ┌──────────────────────────────────┐│
│  │  ░░░░░░░░                       ││
│  │  ░░░░░░░                        ││
│  └──────────────────────────────────┘│
│                                      │
│       [Get Premium to See]           │
│                                      │
└──────────────────────────────────────┘
```

- The blurred preview is synthetic placeholder content (not real data). Three rows of blurred gray rectangles simulating names and timestamps.
- "Get Premium to See" button presents PAY1.
- The lock icon (🔒) on the section header indicates gated content.
- Blurred preview uses `rin.bg.tertiary` rectangles with `rin.radius.sm` corners.
- This intermediate screen appears briefly before the paywall auto-presents. The user sees the teaser for 300ms, then PAY1 slides up. If the user dismisses PAY1, they return to Score Home (not the teaser).

---

## 5) StoreKit 2 Integration

### 5.1 Product Configuration

| Property | Monthly | Annual |
|----------|---------|--------|
| Product ID | `com.rin.premium.monthly` | `com.rin.premium.annual` |
| Subscription Group | "Rin Premium" | "Rin Premium" |
| Group Level | Level 1 | Level 2 (upgrade path) |
| Display Price | `Product.displayPrice` (localized) | `Product.displayPrice` (localized) |

Prices shown in the wireframe ($4.99/mo, $49.99/yr) are reference prices for the US App Store. The app always uses `Product.displayPrice` for rendering — never hardcoded strings.

### 5.2 Subscription Status Architecture

```
                    ┌─────────────────────┐
                    │   PremiumService     │
                    │  (@Observable)       │
                    ├─────────────────────┤
                    │ isSubscribed: Bool   │
                    │ currentPlan: Plan?   │
                    │ expiryDate: Date?    │
                    │ isInGracePeriod: Bool│
                    │ isInBillingRetry: Bool│
                    ├─────────────────────┤
                    │ checkEntitlement()   │
                    │ purchase(_:)         │
                    │ restorePurchases()   │
                    └────────┬────────────┘
                             │
              ┌──────────────┼──────────────┐
              ↓              ↓              ↓
    ┌─────────────┐ ┌──────────────┐ ┌──────────────┐
    │ StoreKit 2  │ │ Server-side  │ │  UserDefaults │
    │ Transaction │ │ status API   │ │  (cache)      │
    │ .current    │ │ (source of   │ │               │
    │ Entitlements│ │  truth)      │ │               │
    └─────────────┘ └──────────────┘ └──────────────┘
```

**Status check priority:**
1. Server-side status API (source of truth when online).
2. StoreKit 2 `Transaction.currentEntitlements` (fallback when offline).
3. UserDefaults cached status (immediate display while async checks complete).

### 5.3 Entitlement Check Flow

```
App launch / App foreground
    ↓
Read cached status from UserDefaults (instant UI)
    ↓
Async: Query server-side subscription status
    ↓
├── Server reachable → Update PremiumService with server response
│   └── Cache new status to UserDefaults
│
└── Server unreachable → Fallback to StoreKit 2
    ↓
    for await result in Transaction.currentEntitlements
    ↓
    Verify JWS signature (StoreKit 2 handles this)
    ↓
    Update PremiumService
    └── Cache to UserDefaults
```

### 5.4 Transaction States

| Transaction State | Handling |
|-------------------|----------|
| `.purchased` | Verify transaction. Grant premium access. Finish transaction. |
| `.pending` | User triggered Ask to Buy (minors). Show "Purchase pending approval" message. Do not grant access yet. |
| `.userCancelled` | User cancelled the StoreKit payment sheet. No action needed. Keep paywall open. |
| `.failed(let error)` | Show error message based on error type. Keep paywall open. |

### 5.5 Transaction Listener

`PremiumService` starts a `Transaction.updates` listener on app launch:

```
Task launched on app start:
    for await verificationResult in Transaction.updates {
        switch verificationResult {
        case .verified(let transaction):
            → Update subscription status
            → Finish transaction
        case .unverified(_, let error):
            → Log verification failure
            → Do not grant access
        }
    }
```

This catches transactions that complete outside the app (Ask to Buy approval, subscription renewals, family sharing changes).

### 5.6 Grace Period and Billing Retry

| Scenario | Behavior |
|----------|----------|
| Billing retry period (Apple retrying failed payment) | `isInBillingRetry = true`. Premium access remains active. No user-facing change. |
| Grace period (configurable in App Store Connect, up to 16 days) | `isInGracePeriod = true`. Premium access remains active. Show subtle banner on PAY2: "There's an issue with your payment method. Update it in Settings to keep Premium." |
| Grace period expired | Premium access revoked. Features degrade to free tier. No aggressive prompts. |

### 5.7 Server-Side Notifications (V2)

The server receives App Store Server Notifications V2 and updates the user's subscription record.

| Notification | Server Action | Client Effect |
|--------------|---------------|---------------|
| `SUBSCRIBED` | Set premium = true, store plan and expiry | Next status check grants access |
| `DID_RENEW` | Update expiry date | Access continues |
| `DID_CHANGE_RENEWAL_STATUS` (off) | Flag as churning | No immediate client change |
| `EXPIRED` | Set premium = false | Next status check revokes access |
| `GRACE_PERIOD_EXPIRED` | Set premium = false | Access revoked |
| `REFUND` | Set premium = false, log refund | Access revoked |
| `REVOKE` | Set premium = false | Access revoked (family sharing) |
| `DID_CHANGE_RENEWAL_INFO` | Update plan type (monthly ↔ annual) | Reflected on next status check |

---

## 6) Purchase Flow

### 6.1 Happy Path

```
User on PAY1
    ↓
Select plan (annual pre-selected, or tap monthly)
    ↓
Tap "Subscribe Now"
    ↓
[Subscribe Now] button → loading spinner state
    ↓
StoreKit 2 payment sheet appears (system UI)
    ↓
User authenticates (Face ID / Touch ID / password)
    ↓
Transaction completes with .purchased
    ↓
Verify transaction
    ↓
Grant premium access (PremiumService.isSubscribed = true)
    ↓
Dismiss paywall
    ↓
Navigate to source feature (if entry was feature-specific)
    ↓
Show celebration moment (brief confetti animation, 1.5s)
    ↓
Feature content loads
```

### 6.2 Plan Selection

```
┌─────────────────────────────────────────┐
│                                         │
│  ┌──────────┐  ┌────────────────────┐  │
│  │  $4.99   │  │  $49.99/year      │  │
│  │  /month  │  │  Save 16% ★  ✓   │  │
│  │          │  │  ($4.17/mo)       │  │
│  └──────────┘  └────────────────────┘  │
│     (dimmed)     (selected, border)     │
│                                         │
└─────────────────────────────────────────┘
```

- Annual plan is pre-selected on load (checkmark visible, `rin.brand.primary` border).
- Monthly plan is dimmed (`rin.text.secondary` text, `rin.border.default` border).
- Tapping monthly selects it; annual becomes dimmed. Single selection.
- Annual card shows per-month equivalent: "($4.17/mo)" in `rin.type.footnote`.
- Savings percentage calculated dynamically: `1 - (annualPrice / (monthlyPrice * 12))`.

### 6.3 Post-Purchase Navigation

| Entry Source | After Purchase Navigation |
|-------------|---------------------------|
| `score_who_viewed` | Dismiss paywall → Push "Who Viewed Me" list onto Score tab stack |
| `score_how_stored` | Dismiss paywall → Push "How Am I Stored" list onto Score tab stack |
| `enrichment_notification` | Dismiss paywall → Navigate to enriched contact detail |
| `profile_premium` | Dismiss paywall → Show PAY2 (subscription management) |
| `settings_premium` | Dismiss paywall → Show PAY2 (subscription management) |
| `deep_link` | Dismiss paywall → Return to previous screen |

### 6.4 Celebration Moment

After successful purchase, before navigating to the destination:
- Brief confetti particle animation overlay (1.5 seconds).
- Text: "You're all set." centered, `rin.type.title2`.
- Auto-dismisses and navigates to destination.
- No "Yay!" or "Awesome!" copy (per brand narrative).

### 6.5 Error States

| Error | UI | Action |
|-------|----|--------|
| `StoreKitError.userCancelled` | No error message. Payment sheet dismissed. Paywall stays open. | None. |
| `StoreKitError.networkError` | Inline error below CTA: "Can't connect to the App Store. Check your connection." | "Try Again" button retries purchase. |
| `StoreKitError.purchaseNotAllowed` | Inline error: "Purchases aren't allowed on this device." | Dismiss only. |
| `StoreKitError.unknown` | Inline error: "Something didn't work. Try again." | "Try Again" button. |
| `VerificationResult.unverified` | Inline error: "Purchase couldn't be verified. Contact support if this continues." | "Try Again" + "Contact Support" link. |
| Ask to Buy (`.pending`) | Replace CTA area with: "Purchase sent for approval. You'll get access once it's approved." | Dismiss paywall. Monitor `Transaction.updates` for approval. |

Error messages follow brand tone: state what happened, state what to do. No "Oops" or "Uh oh."

---

## 7) Subscription Management (PAY2)

### 7.1 Layout — Subscribed State

```
┌──────────────────────────────────────┐
│ ◀ Back              Premium          │
├──────────────────────────────────────┤
│                                      │
│  ⭐ Rin Premium                      │
│  Your plan: Annual                   │
│                                      │
│  SUBSCRIPTION DETAILS                │
│  ┌──────────────────────────────────┐│
│  │ Plan          Annual ($49.99/yr)││
│  │ Status        Active            ││
│  │ Renews        Mar 15, 2026      ││
│  │ Member since  Jan 15, 2026      ││
│  └──────────────────────────────────┘│
│                                      │
│  ┌──────────────────────────────────┐│
│  │ Change Plan                  [>]││
│  │ Manage Subscription          [>]││
│  └──────────────────────────────────┘│
│                                      │
│  PREMIUM FEATURES                    │
│  ┌──────────────────────────────────┐│
│  │ 👀 Who Viewed Me             [>]││
│  │ ✨ Enrichment Alerts         [>]││
│  │ 📋 How Am I Stored           [>]││
│  └──────────────────────────────────┘│
│                                      │
└──────────────────────────────────────┘
```

### 7.2 Layout — Not Subscribed State

```
┌──────────────────────────────────────┐
│ ◀ Back              Premium          │
├──────────────────────────────────────┤
│                                      │
│  ⭐ Get Premium                      │
│                                      │
│  See who viewed your profile. Get    │
│  enrichment alerts. Know how others  │
│  store your info.                    │
│                                      │
│        [Get Premium]                 │
│                                      │
│  Restore Purchases                   │
│                                      │
└──────────────────────────────────────┘
```

- "Get Premium" button presents PAY1 as fullScreenCover.

### 7.3 Access Points to PAY2

| Location | Path |
|----------|------|
| Profile Home (P1) | Account section → "Premium" row |
| Settings | Account section → "Premium" row |

### 7.4 Change Plan

| Current Plan | Action | Behavior |
|-------------|--------|----------|
| Monthly | Tap "Change Plan" | Confirmation sheet: "Switch to Annual ($49.99/yr, Save 16%)?" → StoreKit handles proration. Apple manages credit/refund for unused portion. |
| Annual | Tap "Change Plan" | Confirmation sheet: "Switch to Monthly ($4.99/mo)?" → Change takes effect at next renewal date. |

StoreKit 2 `Product.SubscriptionInfo` handles plan changes within the same subscription group. The app calls `product.purchase()` for the new plan; Apple manages the transition.

### 7.5 Manage Subscription

"Manage Subscription" opens the iOS system subscription management screen:

```swift
// Opens iOS Settings > Subscriptions > Rin Premium
if let url = URL(string: "https://apps.apple.com/account/subscriptions") {
    await UIApplication.shared.open(url)
}
```

This is where users cancel, change payment method, or review billing history. Apple requires this link to be accessible.

### 7.6 PAY2 States

| State | Display |
|-------|---------|
| Active (monthly) | Plan: Monthly. Renewal date shown. |
| Active (annual) | Plan: Annual. Renewal date shown. |
| Grace period | Status: "Payment issue". Banner: "Update your payment method to keep Premium." Link to Manage Subscription. |
| Billing retry | Same as active. No user-facing indication (Apple retries silently). |
| Cancelled (not yet expired) | Status: "Cancelling". "Your Premium access ends on [date]." No renewal date. |
| Expired | Not subscribed state (section 7.2 layout). |

---

## 8) Restore Purchases

### 8.1 Flow

```
User taps "Restore Purchases" (on PAY1 or PAY2-not-subscribed)
    ↓
Show inline loading spinner next to "Restore Purchases" text
    ↓
Call AppStore.sync()
    ↓
Check Transaction.currentEntitlements
    ↓
├── Entitlement found
│   ↓
│   Update PremiumService.isSubscribed = true
│   ↓
│   Dismiss paywall (if on PAY1)
│   ↓
│   Show confirmation toast: "Premium restored."
│
└── No entitlement found
    ↓
    Show inline message: "No previous purchases found."
    ↓
    Message auto-dismisses after 3 seconds
    ↓
    Paywall remains open
```

### 8.2 Restore from PAY2 (Not Subscribed)

Same flow, but instead of dismissing a paywall, the PAY2 screen transitions from "Not Subscribed" to "Subscribed" layout.

---

## 9) Feature Gating

### 9.1 Gated Features

| Feature | Free Tier | Premium |
|---------|-----------|---------|
| Who Viewed Me | Lock icon on section. Tap → PAY1. | Full viewer list with names and timestamps. |
| Enrichment Alerts | Push notifications disabled. Section shows "Premium" badge. | Push notifications active. Real-time alerts. |
| How Am I Stored | Lock icon on section. Tap → PAY1. | Full list of stored names with match confidence. |
| Rin Score | Full access. | Full access. |
| Deduplication | Full access. | Full access. |
| Circles | Full access. | Full access. |
| Contact sync | Full access. | Full access. |
| Shadow profiles | Full access. | Full access. |

### 9.2 Gate Check Pattern

```swift
// In any view that contains gated content:
if premiumService.isSubscribed {
    // Show premium content
    PremiumFeatureView(feature: .whoViewedMe)
} else {
    // Show gated preview
    GatedFeaturePreview(feature: .whoViewedMe) {
        // On tap: present paywall
        showPaywall(source: .scoreWhoViewed)
    }
}
```

### 9.3 Enrichment Notification Gating

- Free tier: Enrichment occurs server-side but push notifications are suppressed.
- When a free user receives an enrichment notification tap (e.g., from a legacy notification before downgrade): PAY1 presented with Enrichment Alerts emphasized.
- Premium: enrichment push notifications delivered normally. Tap opens the enriched contact detail.

---

## 10) Cancellation and Expiry

### 10.1 Cancellation Path

Cancellation happens in iOS Settings, not in-app. Rin does not provide an in-app cancel button. This is standard iOS practice and Apple-compliant.

The "Manage Subscription" link on PAY2 takes users to the system subscription management screen where cancellation is available.

### 10.2 Post-Cancellation Behavior

```
User cancels in iOS Settings
    ↓
App Store Server Notification: DID_CHANGE_RENEWAL_STATUS (auto_renew = false)
    ↓
Server flags user as churning
    ↓
PremiumService reflects: cancelled but not yet expired
    ↓
PAY2 shows: "Your Premium access ends on [expiry date]."
    ↓
User retains full premium access until expiry date
    ↓
On expiry date:
    ↓
App Store Server Notification: EXPIRED
    ↓
Server sets premium = false
    ↓
Next app launch / foreground: PremiumService checks status
    ↓
Features degrade to free tier
```

### 10.3 Graceful Degradation

When premium expires:

| Feature | Behavior |
|---------|----------|
| Who Viewed Me | Section reverts to locked state. Historical viewer data persists on server but is no longer displayed. |
| Enrichment Alerts | Push notifications stop. Previously enriched data remains on contacts (enriched fields are not removed). |
| How Am I Stored | Section reverts to locked state. Historical stored-name data persists on server but is no longer displayed. |

Rules:
- No aggressive re-subscription prompts on expiry. The gated section displays the lock icon as it did before the user ever subscribed.
- No "Your Premium expired" interstitial or pop-up.
- No countdown to expiry in the UI (except the expiry date on PAY2 during the cancellation period).
- If the user re-subscribes, access is restored immediately. Historical data (viewer list, stored names) becomes visible again.

---

## 11) Trial Experience

### 11.1 Trial Configuration (If Offered)

Trial eligibility is configured in App Store Connect and managed by StoreKit 2. The app does not independently track trial state.

| Property | Value |
|----------|-------|
| Duration | 7 days (preferred over 3 days; contacts apps need time to demonstrate value) |
| Eligible plans | Annual plan only (higher LTV conversion target) |
| Eligibility | New subscribers only (StoreKit 2 manages via `Product.SubscriptionInfo.isEligibleForIntroOffer`) |

### 11.2 Trial UI

When the user is eligible for a trial, PAY1 adapts:

```
┌──────────────────────────────────────┐
│                              [✕]    │
│                                      │
│         ⭐ Get Premium               │
│                                      │
│  [Feature cards same as section 2]   │
│                                      │
│  ┌──────────┐  ┌──────────────────┐ │
│  │  $4.99   │  │  FREE for 7 days│ │
│  │  /month  │  │  then $49.99/yr │ │
│  │          │  │  Save 16% ★     │ │
│  └──────────┘  └──────────────────┘ │
│                                      │
│  Your free trial starts today.       │
│  You won't be charged until          │
│  [date 7 days from now].             │
│                                      │
│     [Start Free Trial]               │
│                                      │
│   Restore Purchases                  │
│   Terms  ·  Privacy Policy           │
└──────────────────────────────────────┘
```

- CTA changes from "Subscribe Now" to "Start Free Trial" when trial eligible and annual plan selected.
- CTA reverts to "Subscribe Now" if user selects monthly (no trial on monthly).
- Trial disclosure text is mandatory per Apple: explicit date when billing begins.
- Disclosure uses `rin.type.callout`, `rin.text.primary` (not secondary; this must be legible).

### 11.3 Trial Expiry

- Apple sends push notification before trial ends (system-managed).
- On trial expiry, if user doesn't cancel:
  - StoreKit converts to paid subscription automatically.
  - App receives `SUBSCRIBED` notification.
  - No change in UX; user retains access.
- On trial expiry, if user cancelled during trial:
  - Access revoked at trial end date.
  - Graceful degradation per section 10.3.

---

## 12) Events

All events follow `object_action` naming convention per event taxonomy. Events are PostHog events fired client-side unless marked as server-side.

### 12.1 Paywall Events

| Event | Properties | When |
|-------|-----------|------|
| `paywall_viewed` | `source` (entry point ID), `feature_emphasized` (or null), `trial_eligible: Bool` | PAY1 presented on screen |
| `paywall_plan_selected` | `plan` (monthly/annual), `previous_plan` (what was selected before) | User taps a pricing card |
| `paywall_purchase_started` | `plan`, `price`, `is_trial: Bool` | User taps Subscribe Now / Start Free Trial |
| `paywall_purchase_completed` | `plan`, `price`, `is_trial: Bool`, `transaction_id` | StoreKit transaction verified successfully |
| `paywall_purchase_failed` | `plan`, `error_type` (network/not_allowed/unknown/verification_failed) | StoreKit transaction failed |
| `paywall_purchase_cancelled` | `plan` | User cancelled StoreKit payment sheet |
| `paywall_dismissed` | `source`, `duration_ms`, `plan_selected` (what was selected when dismissed, or null) | User taps X to close PAY1 |
| `paywall_restore_tapped` | (none) | User taps Restore Purchases |
| `paywall_restore_completed` | `found: Bool` | Restore finishes (with or without entitlement) |

### 12.2 Subscription Lifecycle Events (Server-Side)

| Event | Properties | When |
|-------|-----------|------|
| `subscription_started` | `plan`, `price`, `is_trial: Bool` | New subscription created |
| `subscription_renewed` | `plan`, `period_count` | Auto-renewal processed |
| `subscription_expired` | `plan`, `tenure_days`, `was_trial: Bool` | Subscription expired |
| `subscription_cancelled` | `plan`, `tenure_days`, `reason` (if available) | Auto-renew turned off |
| `subscription_plan_changed` | `from_plan`, `to_plan` | Monthly to annual or vice versa |
| `subscription_refunded` | `plan`, `tenure_days` | Apple processed refund |
| `subscription_grace_period_entered` | `plan` | Payment failed, grace period started |

### 12.3 Premium Feature Events

| Event | Properties | When |
|-------|-----------|------|
| `premium_feature_used` | `feature` (who_viewed/enrichment_alerts/how_am_i_stored) | User views premium content |
| `premium_feature_gated` | `feature`, `source` | Free user taps gated section |

### 12.4 Event Flow

```
paywall_viewed (source=score_who_viewed)
    ↓
paywall_plan_selected (plan=annual)        ← optional, if user changes plan
    ↓
paywall_purchase_started (plan=annual)
    ↓
├── paywall_purchase_completed             ← success path
│   → subscription_started (server)
│   → premium_feature_used (who_viewed)
│
├── paywall_purchase_failed                ← error path
│
├── paywall_purchase_cancelled             ← user backed out
│
└── paywall_dismissed                      ← user closed paywall
```

### 12.5 KPI Alignment

These events feed the revenue input metrics from KPI Hierarchy:

| KPI | Source Events |
|-----|--------------|
| Paywall exposure rate (target >20% MAU) | `paywall_viewed` / MAU |
| Premium trial start rate (target >5%) | `paywall_purchase_completed` where `is_trial=true` / `paywall_viewed` |
| Premium conversion rate (target >30%) | `subscription_started` where `was_trial=false` / trial completions |
| Premium retention monthly (target >85%) | `subscription_renewed` / active subscriptions |

---

## 13) Compliance

### 13.1 Apple Required Elements

| Requirement | Implementation | Location |
|-------------|---------------|----------|
| Restore Purchases button | "Restore Purchases" link on PAY1 | Below CTA |
| Terms of Service link | "Terms" link opening web URL | Footer of PAY1 |
| Privacy Policy link | "Privacy Policy" link opening web URL | Footer of PAY1 |
| Subscription management access | "Manage Subscription" row on PAY2 | Settings → Premium |
| Localized pricing | `Product.displayPrice` used everywhere | PAY1 pricing cards |
| Auto-renewal disclosure | "Auto-renews. Cancel anytime." | Above CTA on PAY1 |
| Free trial billing date | "You won't be charged until [date]." | Below pricing on PAY1 (trial variant) |
| Paywall dismissibility | Close button (X) always visible | Top-right of PAY1 |

### 13.2 Pricing Display Rules

1. Never hardcode "$4.99" or "$49.99." Always use `Product.displayPrice` from StoreKit.
2. Annual savings percentage calculated dynamically: `1 - (annual / (monthly * 12))`.
3. Per-month equivalent on annual card: `annual / 12`, formatted with `Product.priceFormatStyle`.
4. If StoreKit products fail to load, pricing cards show a loading skeleton. Do not show stale or placeholder prices.

### 13.3 No Dark Patterns

Per brand narrative and Apple guidelines:
- No pre-checked trial that auto-converts without clear disclosure.
- No hidden cancellation flow (link to iOS subscription settings always accessible).
- No countdown timers on pricing.
- No "last chance" or "limited time" language.
- No guilt-inducing cancellation copy.
- Annual plan highlighted as "recommended" via visual emphasis only — not labeled "Best Value" or "Most Popular" (unverifiable claims).

### 13.4 Cross-Reference

Full compliance checklist in `docs/plan/IAP_SUBSCRIPTION_COMPLIANCE_V1.md`. This spec implements all requirements defined there. Any conflict between this spec and the compliance doc should be resolved in favor of the compliance doc.

---

## 14) Accessibility

### 14.1 VoiceOver

| Element | VoiceOver Label | Trait |
|---------|----------------|-------|
| Close button | "Close paywall" | `.button` |
| Header | "Get Premium" | `.header` |
| Feature card (Who Viewed Me) | "Who Viewed Me. See who checked your profile this week." | `.staticText` |
| Feature card (Enrichment Alerts) | "Enrichment Alerts. Know when contact info updates." | `.staticText` |
| Feature card (How Am I Stored) | "How Am I Stored. See how others save your info." | `.staticText` |
| Monthly pricing card | "Monthly plan, [displayPrice] per month" | `.button` + `.selected` when active |
| Annual pricing card | "Annual plan, [displayPrice] per year, save 16 percent, [per-month equivalent] per month" | `.button` + `.selected` when active |
| Subscribe Now button | "Subscribe now, [selected plan] at [price]" | `.button` |
| Start Free Trial button | "Start free trial, 7 days free then [price] per year" | `.button` |
| Restore Purchases link | "Restore previous purchases" | `.button` |
| Auto-renewal disclosure | "Auto-renews. Cancel anytime." | `.staticText` |
| Trial disclosure | "Your free trial starts today. You won't be charged until [date]." | `.staticText` |

### 14.2 Dynamic Type

- All text elements use `Font.system` with corresponding `TextStyle`.
- Layout accommodates up to `AX5` accessibility size.
- Feature cards stack vertically at very large text sizes (horizontal padding collapses).
- Pricing cards stack vertically at `AX3` and above (side-by-side below).

### 14.3 Color Contrast

- All text meets WCAG 2.1 AA (4.5:1 for body text, 3:1 for large text).
- Selected plan border uses `rin.brand.primary` at 2pt width — also indicated by a checkmark (not color-dependent).
- Emphasized feature card uses accent border plus reduced opacity on siblings — the emphasized card also appears first in VoiceOver reading order.

### 14.4 Reduce Motion

- If `UIAccessibility.isReduceMotionEnabled`: confetti animation replaced with static "You're all set." text (no particles).
- Card emphasis transitions use crossfade instead of spring animation.

---

## 15) Paywall Navigation Map

```
Profile Home (P1)
├── Account → Premium → PAY2 (Subscription Management)
│   ├── If not subscribed → "Get Premium" → PAY1
│   ├── Change Plan → StoreKit plan change
│   └── Manage Subscription → iOS Settings (external)
│
Settings
├── Account → Premium → PAY2 (same as above)
│
Score Home (SC1)
├── Who Viewed Me [🔒] → Blurred teaser → PAY1 (feature emphasized)
├── How Am I Stored [🔒] → Blurred teaser → PAY1 (feature emphasized)
│
Enrichment push notification → PAY1 (feature emphasized)
│
Deep link: rin://premium → PAY1 (neutral)
Deep link: rin://premium?feature=X → PAY1 (feature emphasized)
```

---

## 16) Screen Summary

| Screen ID | Name | Presentation | Module |
|-----------|------|-------------|--------|
| PAY1 | Paywall | `.fullScreenCover` | RinPremium |
| PAY2 | Subscription Management | Pushed onto Profile/Settings NavigationStack | RinPremium |

---

## 17) Open Decisions

1. Whether to offer a free trial at launch or defer to post-launch (section 11 defines the trial UX if offered; the decision of whether to launch with it is unresolved).
2. Whether the max-one-paywall-per-session rule (section 3.3 rule 3) should reset after a configurable time (e.g., 30 minutes) or only reset on a new app session.
3. Whether the blurred teaser (section 4.2) should auto-present the paywall after 300ms or require a tap on the "Get Premium to See" button.
4. Whether the post-purchase celebration (section 6.4) should be skipped for trial starts (since the user hasn't paid yet) or shown with different copy ("Your trial has started.").
5. Whether to show a subscription status badge on the Profile tab icon (e.g., star) when the user is subscribed, or keep the tab icon neutral.