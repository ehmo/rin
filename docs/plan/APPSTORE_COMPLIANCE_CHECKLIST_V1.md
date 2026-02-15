# App Store Compliance Checklist V1

## 1) Purpose

Comprehensive checklist of Apple App Store policies that Rin must satisfy for submission and approval. Organized by review risk level.

Companion docs:
- `docs/product/IOS_ONBOARDING_SCREEN_SPEC_V1.md` (screen inventory)
- `docs/product/SHADOW_PROFILE_UX_V1.md` (multiple profiles)
- `docs/architecture/IOS_APP_ARCHITECTURE_V1.md` (module structure)

---

## 2) High Risk (Likely Rejection if Missed)

### 2.1 Privacy and Data Collection

- [ ] **Privacy Nutrition Labels**: declare all data collected in App Store Connect (contacts, phone number, name, usage data, diagnostics).
- [ ] **App Tracking Transparency**: if any third-party analytics tracks users across apps, implement ATT prompt. If no cross-app tracking, document why ATT is not needed.
- [ ] **Privacy Policy URL**: required. Must be accessible from app and App Store listing. Must describe: data collected, how it's used, who it's shared with, retention periods, deletion process.
- [ ] **Contacts permission purpose string**: `NSContactsUsageDescription` must clearly explain why contacts access is needed. Vague descriptions get rejected.
- [ ] **Push notification purpose string**: `NSUserNotificationsUsageDescription` if applicable.
- [ ] **Camera/photo permission purpose string**: if profile photo upload uses camera.
- [ ] **Minimum data collection**: only request permissions actually used. Unused permission requests trigger rejection.

### 2.2 Account Deletion (Mandatory Since 2022)

- [ ] **In-app account deletion**: users must be able to delete their account from within the app. Apple requires this for any app with account creation.
- [ ] **Clear deletion flow**: Settings > Account > Delete Account. Explain what data is deleted and what is retained (compliance/audit skeleton).
- [ ] **Deletion timeline**: Apple expects deletion to be "reasonably prompt." Document expected timeline (e.g., "within 30 days").
- [ ] **Active subscriptions**: if user has active subscription, warn them before deletion. Subscription must be cancelable from the deletion flow or link to Apple subscription management.

### 2.3 In-App Purchase Compliance (StoreKit 2)

- [ ] **All digital content/features via IAP**: premium features (Who Viewed Me, Enrichment Alerts, Enhanced How Am I Stored) must use Apple's IAP system. No external payment links for digital content.
- [ ] **Subscription terms displayed**: before purchase, show price, billing period, renewal terms, and cancellation instructions.
- [ ] **Restore purchases**: implement a "Restore Purchases" button in Settings. Required by Apple.
- [ ] **Free trial disclosure**: if offering free trial, clearly state trial length and post-trial price.
- [ ] **No IAP for physical goods/services**: if Rin ever sells physical items, those bypass IAP (not applicable for v1).
- [ ] **Subscription management link**: provide easy access to Apple's subscription management (Settings > Apple ID > Subscriptions).

### 2.4 Sign In with Apple

- [ ] **Required if third-party sign-in offered**: if Rin adds Google Sign-In or social login, Sign In with Apple must also be offered.
- [ ] **Not required for phone-only auth**: Rin's v1 phone-first auth does not trigger this requirement.
- [ ] **Track this requirement**: if any social login is added later, SIWA becomes mandatory.

---

## 3) Medium Risk (Common Review Friction)

### 3.1 Content and User Safety

- [ ] **Report/block mechanism**: users must be able to report and block other users. Required for social networking apps.
- [ ] **Content moderation**: if any user-generated content exists (profile names, photos, messages), moderation must be in place.
- [ ] **CSAM detection**: Apple may require PhotoDNA or similar for user-uploaded photos. Evaluate if profile photos trigger this requirement.
- [ ] **User safety disclosures**: social networking apps may need to describe safety measures in App Store review notes.

### 3.2 Age Rating and Restrictions

- [ ] **Content rating**: select appropriate age rating. Social networking with user-generated content typically rates 12+ or 17+ depending on content controls.
- [ ] **Parental gate**: if rated 4+ or 9+, additional restrictions may apply for social features.
- [ ] **COPPA compliance**: if any users could be under 13, additional protections required. Consider age gate during onboarding.

### 3.3 Push Notification Guidelines

- [ ] **No promotional push without opt-in**: push notifications for marketing require explicit user consent beyond the system notification permission.
- [ ] **Functional notifications first**: security alerts, dispute updates, and Ask requests are functional. Marketing/engagement pushes need separate opt-in.

### 3.4 Network Extensions and Background Activity

- [ ] **Background refresh justification**: if using BGAppRefreshTask for contact sync, justify in review notes why background activity is needed.
- [ ] **No excessive battery drain**: Apple rejects apps that drain battery in background. Contact sync must be efficient.

---

## 4) Low Risk (Best Practices)

### 4.1 App Store Listing Metadata

- [ ] **App name**: max 30 characters. Must not include generic terms that imply editorial endorsement.
- [ ] **Subtitle**: max 30 characters. Complement the name.
- [ ] **Description**: clear, accurate. No misleading claims about data security without specifics.
- [ ] **Keywords**: max 100 characters. Research-driven selection.
- [ ] **Screenshots**: minimum 3 for each device size. Must represent actual app functionality. No misleading mockups.
- [ ] **App preview video**: optional but recommended. Max 30 seconds.
- [ ] **Category**: primary "Social Networking," secondary "Utilities" or "Productivity."

### 4.2 Design and UX Requirements

- [ ] **Human Interface Guidelines compliance**: standard navigation patterns, no custom gestures without affordances.
- [ ] **Dynamic Type support**: text must respect user's preferred text size.
- [ ] **Dark Mode support**: recommended but not required. If supported, must work correctly throughout.
- [ ] **Launch screen**: required. Must not be a splash ad.
- [ ] **No dead-end screens**: every screen must have a way to navigate back or forward.

### 4.3 Performance Requirements

- [ ] **App launches in reasonable time**: Apple rejects apps that take >20 seconds to become interactive.
- [ ] **No crashes during review**: Apple tests core flows. Ensure onboarding, contact import, and profile setup are stable.
- [ ] **Minimum iOS version**: declare and test on the minimum supported version.

### 4.4 Legal and Terms

- [ ] **Terms of Service URL**: recommended for social networking apps.
- [ ] **EULA**: Apple's standard EULA applies unless custom EULA is provided.
- [ ] **GDPR compliance**: if serving EU users, data export and deletion must be available.
- [ ] **Contact information**: App Store listing must include a support URL or email.

---

## 5) Review Submission Notes

When submitting for review, include:

### 5.1 Demo Account

- [ ] Provide a demo phone number and OTP code for the reviewer.
- [ ] Pre-populate the demo account with sample contacts so the reviewer can see value screens.
- [ ] Document the demo account credentials in App Store Connect review notes.

### 5.2 Feature Explanation

Include review notes explaining:
- [ ] Why contacts permission is needed (contact graph intelligence, not spam).
- [ ] How shadow profiles work and their intended use (multiple personas, not abuse).
- [ ] What premium features include and how subscription works.
- [ ] How the dispute/reporting system works.
- [ ] That no Exposure Notification API is used (preempt confusion from contact-related functionality).

### 5.3 Background Activity Justification

- [ ] Explain that BGAppRefreshTask is used for contact sync delta detection, not surveillance.
- [ ] State expected frequency (daily) and battery impact (minimal, <30s execution).

---

## 6) Premium / StoreKit 2 Specifics

### 6.1 Subscription Configuration

| Field | Value |
|-------|-------|
| **Product ID** | `com.rin.premium.monthly` / `com.rin.premium.annual` |
| **Price** | $4.99/month / $49.99/year |
| **Free trial** | TBD (consider 7-day trial) |
| **Grace period** | 16 days (Apple default for auto-renewable) |
| **Billing retry** | Enabled (Apple manages) |

### 6.2 Premium Features Gated

| Feature | Free | Premium |
|---------|------|---------|
| Contact import and sync | Yes | Yes |
| Dedup and smart merge | Yes | Yes |
| Circle management | Yes | Yes |
| Rin Score and network analytics | Yes | Yes |
| Shadow profiles | Yes | Yes |
| **Who Viewed / Searched Me** | Count only | Full viewer list + trends |
| **Contact Enrichment Alerts** | Monthly refresh | Real-time + life-event alerts |
| **Enhanced How Am I Stored** | N people have your info | Full detail + correction requests |

### 6.3 Paywall UX

- Paywall shown when user taps a premium-gated feature.
- Show feature preview with blurred/teased content.
- Clear price, billing terms, and "Restore Purchases" button.
- No forced upsell during onboarding. Premium surfaces organically through usage.

---

## 7) Pre-Submission Checklist

Run before every App Store submission:

- [ ] All privacy strings are present and descriptive.
- [ ] Account deletion flow works end-to-end.
- [ ] Restore Purchases works.
- [ ] Demo account is functional and pre-populated.
- [ ] Review notes are updated with current feature explanations.
- [ ] No placeholder text or lorem ipsum in the app.
- [ ] All links (privacy policy, ToS, support) resolve to live pages.
- [ ] App does not crash on any supported iOS version.
- [ ] App works offline gracefully (no blank screens or crashes).
- [ ] Background refresh is efficient and justified.

---

## 8) Open Decisions

1. Whether to offer a free trial period for premium (7-day or 14-day).
2. Whether to support older iOS versions (16+) or require iOS 17+ (SwiftData dependency).
3. Whether to add Sign In with Apple proactively or wait until a social login trigger requires it.
4. Whether to implement CSAM detection for profile photos in v1 or rely on Apple's on-device scanning.
5. Minimum age requirement: 12+ or 17+ content rating.
6. Whether to include a custom EULA or use Apple's standard.
