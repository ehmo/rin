# In-App Purchase and Subscription Compliance V1

## 1) Purpose

Define the StoreKit 2 implementation plan, subscription configuration, and App Store compliance for Rin's premium tier.

Companion docs:
- `docs/plan/APPSTORE_COMPLIANCE_CHECKLIST_V1.md` (compliance checklist)
- `docs/plan/BETA_COHORT_STRATEGY_V1.md` (premium beta strategy)

---

## 2) Premium Tier (Locked)

### 2.1 Pricing

| Plan | Price | Product ID |
|------|-------|-----------|
| Monthly | $4.99/mo | `com.rin.premium.monthly` |
| Annual | $49.99/yr ($4.17/mo effective) | `com.rin.premium.annual` |

### 2.2 Premium Features

| Feature | Description |
|---------|------------|
| **Who Viewed Me** | See who viewed your profile this week with timestamps |
| **Enrichment Alerts** | Push notification when contact enrichment data updates |
| **Enhanced How Am I Stored** | See how your name appears in others' contact books |

### 2.3 Free Features (Not Gated)

- Advanced deduplication and smart merge.
- Network health analytics.
- Rin Score and all component breakdowns.
- Circle management and access controls.
- Contact import and sync.
- Shadow profiles.

---

## 3) StoreKit 2 Implementation

### 3.1 Subscription Group

- Group name: "Rin Premium"
- Group ID: configured in App Store Connect.
- Contains: Monthly and Annual plans.
- Level: Monthly = Level 1, Annual = Level 2 (upgrade path).

### 3.2 Purchase Flow

```
User taps premium feature (or Premium in Settings)
    ↓
Show paywall screen:
    - Feature highlights (3 premium features)
    - Pricing cards (Monthly / Annual, annual highlighted as "Save 16%")
    - "Terms of Service" and "Privacy Policy" links (required by Apple)
    - "Restore Purchases" button (required by Apple)
    ↓
User selects plan → StoreKit 2 purchase sheet
    ↓
Transaction verified (StoreKit 2 handles this)
    ↓
Server notified via App Store Server Notifications V2
    ↓
Premium features unlocked
```

### 3.3 StoreKit 2 Code Structure

```swift
// In RinPremium package
class PremiumService: ObservableObject {
    @Published var isSubscribed: Bool = false
    @Published var currentPlan: Plan? = nil

    func checkEntitlement() async {
        for await result in Transaction.currentEntitlements {
            // Verify and update subscription status
        }
    }

    func purchase(_ product: Product) async throws -> Transaction {
        let result = try await product.purchase()
        // Handle result
    }

    func restorePurchases() async {
        try? await AppStore.sync()
    }
}
```

### 3.4 Server-Side Verification

- Enable App Store Server Notifications V2.
- Server endpoint receives subscription lifecycle events.
- Store subscription status in user's principal record.
- iOS client checks server-side status on launch (source of truth).
- Fallback: StoreKit 2 `Transaction.currentEntitlements` for offline access.

---

## 4) Paywall Design

### 4.1 Paywall Screen

```
┌──────────────────────────────────────┐
│               [X Close]              │
│                                      │
│         Unlock Premium               │
│                                      │
│   ┌──────────────────────────┐       │
│   │ 👀 Who Viewed Me         │       │
│   │ See who checked your     │       │
│   │ profile this week        │       │
│   └──────────────────────────┘       │
│                                      │
│   ┌──────────────────────────┐       │
│   │ ✨ Enrichment Alerts     │       │
│   │ Know when contact info   │       │
│   │ gets updated             │       │
│   └──────────────────────────┘       │
│                                      │
│   ┌──────────────────────────┐       │
│   │ 📋 How Am I Stored       │       │
│   │ See how others save      │       │
│   │ your contact info        │       │
│   └──────────────────────────┘       │
│                                      │
│   ┌────────┐  ┌────────────────┐     │
│   │ $4.99  │  │ $49.99/year   │     │
│   │ /month │  │ Save 16% ★    │     │
│   └────────┘  └────────────────┘     │
│                                      │
│       [Subscribe Now]                │
│                                      │
│  Restore Purchases                   │
│  Terms of Service | Privacy Policy   │
└──────────────────────────────────────┘
```

### 4.2 Paywall Triggers

| Trigger | Context |
|---------|---------|
| Tap "Who Viewed Me" section on Score tab | Feature discovery |
| Tap "How Am I Stored" on Profile tab | Feature discovery |
| Settings > "Upgrade to Premium" | Intentional exploration |
| Stage 2+: After N dedup resolutions | Upsell moment (value proven) |

### 4.3 Paywall Rules

- Always dismissible (close button required by Apple).
- Never blocks core app functionality.
- Never shown during onboarding.
- Max once per session (don't re-show after dismiss).
- Annual plan highlighted as default selection.

---

## 5) App Store Compliance Requirements

### 5.1 Required Elements

| Requirement | Implementation |
|-------------|---------------|
| Restore Purchases button | Visible on paywall and in Settings |
| Terms of Service link | Opens web URL on paywall |
| Privacy Policy link | Opens web URL on paywall |
| Subscription management link | Settings > Manage Subscription (opens iOS settings) |
| Price display | Shows localized price from StoreKit (not hardcoded) |
| Auto-renewal disclosure | "Subscription auto-renews unless cancelled at least 24 hours before the end of the current period" |
| Free trial disclosure (if offered) | "Free trial converts to paid subscription after [N] days" |

### 5.2 Pricing Display

- Always use StoreKit `Product.displayPrice` for localized pricing.
- Never hardcode "$4.99" — Apple handles currency conversion.
- Show savings percentage for annual plan dynamically.

### 5.3 Subscription Cancellation

- Settings > Account > Manage Subscription → opens iOS subscription management.
- In-app: clearly explain how to cancel.
- No dark patterns (hiding cancel, confusing wording, guilt trips).

---

## 6) Beta Pricing Strategy

| Beta stage | Premium behavior |
|-----------|-----------------|
| Stage 1 | Premium unlocked for all (testing features, not conversion) |
| Stage 2 | Premium gated for 50% of new testers (A/B test) |
| Stage 3 | Premium gated for all new testers |
| Post-launch | Premium gated for all users |

- StoreKit sandbox environment during TestFlight (no real charges).
- Premium pricing configured but not billed until public launch.

---

## 7) Revenue Tracking

### 7.1 Server-Side Events (App Store Server Notifications V2)

| Event | Action |
|-------|--------|
| `SUBSCRIBED` | Mark user as premium |
| `DID_RENEW` | Update expiry date |
| `DID_CHANGE_RENEWAL_STATUS` (to false) | Flag as churning |
| `EXPIRED` | Remove premium status |
| `REFUND` | Remove premium status, log for analytics |
| `GRACE_PERIOD_EXPIRED` | Remove premium status |
| `REVOKE` | Remove premium status (family sharing revocation) |

### 7.2 Analytics Events

Map to PostHog events (defined in Event Taxonomy):
- `paywall_viewed`, `paywall_dismissed`, `subscription_started`, `subscription_cancelled`, `subscription_renewed`, `premium_feature_used`.

---

## 8) Open Decisions

1. Whether to offer a free trial (7 days or 3 days) or go straight to paid.
2. Whether to offer a lifetime purchase option alongside subscriptions.
3. Whether to implement introductory offers (first month at $0.99).
4. Whether beta testers should get a permanent discount as thanks.
