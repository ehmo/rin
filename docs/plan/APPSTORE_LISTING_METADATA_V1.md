# App Store Listing and Metadata Plan V1

## 1) Purpose

Define the App Store listing content, metadata, and ASO strategy. Position Rin as network intelligence — emphasizing breadth and depth of contact graph insights.

Companion docs:
- `docs/plan/APPSTORE_COMPLIANCE_CHECKLIST_V1.md` (compliance requirements)
- `docs/plan/ICP_MESSAGING_PILLARS_V1.md` (target audience and messaging)

---

## 2) Positioning

### 2.1 Category

- **Primary**: Social Networking
- **Secondary**: Utilities (or Productivity)

### 2.2 Tagline

"Understand your real network."

### 2.3 Positioning Statement

Rin is the first app that turns your contact list into actionable network intelligence. Go beyond names and numbers — see relationship strength, network patterns, and your true social graph.

---

## 3) App Store Metadata

### 3.1 App Name

**Rin — Network Intelligence** (max 30 chars)

### 3.2 Subtitle

"Your contacts, decoded." (max 30 chars)

### 3.3 Keywords (max 100 chars)

`contacts,network,score,dedup,relationship,graph,cleanup,organize,circles,privacy`

### 3.4 Description

```
Your contact list is more than names and numbers. Rin reveals the intelligence hidden in your network.

NETWORK INTELLIGENCE
• Rin Score: A 0-100 measure of your network strength, updated daily
• See which connections are mutual, one-sided, or fading
• Understand your position across different social clusters
• Track how your network evolves over time

CONTACT INTELLIGENCE
• Automatic duplicate detection and smart merge suggestions
• Contact enrichment with professional context
• See how your contacts store you (Premium)
• Know who viewed your profile (Premium)

ORGANIZE WITH CIRCLES
• Group contacts into circles (Family, Friends, Colleagues, custom)
• Control exactly what each circle can see about you
• Per-field privacy controls: Allow, Don't Allow, or Ask
• Your data, your rules

CLEAN & SIMPLE
• Import your contacts in seconds
• Intelligent dedup handles the mess
• Background sync keeps everything current
• No ads. No selling your data. Ever.

PRIVACY FIRST
• Your contact data stays yours
• Three-state access controls for every field
• Shadow profiles for context-appropriate identity
• Account deletion with full data purge

Rin is free to use. Premium features ($4.99/mo) include Who Viewed Me, Enrichment Alerts, and Enhanced How Am I Stored.
```

### 3.5 Promotional Text (max 170 chars, changeable without review)

"New: Rin Score reveals your network strength. Import contacts and discover your social graph intelligence in seconds."

### 3.6 What's New (for updates)

Template:
```
• [Feature/fix 1]
• [Feature/fix 2]
• Bug fixes and performance improvements
```

---

## 4) Screenshots

### 4.1 Screenshot Sequence (6 screens)

| # | Screen | Headline text | Shows |
|---|--------|--------------|-------|
| 1 | Score overview | "Your network, scored." | Score ring (72), component bars, quality label |
| 2 | Contact list with dedup | "Smart contact cleanup." | Contact list with dedup card, merge suggestion |
| 3 | Circle management | "Privacy in circles." | Circle list with access toggles, emoji badges |
| 4 | Score component detail | "Understand every signal." | Quality component drill-down, improvement tips |
| 5 | Profile with shadow picker | "Multiple identities, one app." | Card deck picker, profile cards |
| 6 | Enrichment + Who Viewed | "Know who's looking." | Premium features, enrichment badges |

### 4.2 Device Sizes Required

- iPhone 6.9" (15 Pro Max) — required.
- iPhone 6.7" (14 Pro Max) — recommended.
- iPhone 6.1" (15 Pro) — recommended.
- iPad Pro 12.9" — if iPad supported.

### 4.3 Screenshot Style

- Device frame (optional, Apple allows either).
- Headline text above or below device frame.
- Clean, minimal design matching app's design tokens.
- Dark mode variant as alternate set.

---

## 5) App Preview Video (Optional)

### 5.1 Storyboard (30 seconds max)

| Time | Content |
|------|---------|
| 0-5s | App icon animation → launch |
| 5-10s | Contact import (animated counter) |
| 10-15s | Dedup suggestions appearing, user merges one |
| 15-20s | Score reveal (ring fills up, quality label appears) |
| 20-25s | Circle management, access toggles |
| 25-30s | End card: "Rin — Understand your real network." |

### 5.2 Defer for v1

App preview video is optional and can be added post-launch. Focus on screenshots first.

---

## 6) ASO Keyword Strategy

### 6.1 Primary Keywords (High Intent)

| Keyword | Difficulty | Relevance |
|---------|-----------|-----------|
| contact manager | Medium | High |
| duplicate contacts | Low | High |
| contact cleanup | Low | High |
| contact organizer | Medium | High |

### 6.2 Secondary Keywords (Discovery)

| Keyword | Difficulty | Relevance |
|---------|-----------|-----------|
| network score | Low | High |
| relationship manager | Medium | Medium |
| privacy contacts | Low | Medium |
| contact graph | Low | High |

### 6.3 Competitive Keywords

| Keyword | Competitor | Strategy |
|---------|-----------|----------|
| contacts+ | Contacts+ app | Target dissatisfied users with superior dedup |
| truecaller alternative | Truecaller | Privacy-first positioning against data harvesting |
| personal CRM | Monica, Dex, Clay | Network intelligence > CRM busy-work |

---

## 7) Ratings and Reviews Strategy

### 7.1 In-App Rating Prompt

- Trigger: after second "magic moment" (e.g., second dedup resolved OR first score view after D7).
- Max frequency: once per 30 days.
- Use `SKStoreReviewController.requestReview()`.
- Never prompt during: onboarding, error states, after denied permissions.

### 7.2 Review Response Templates

**Positive review:**
> Thank you for the kind words! We're working hard to make Rin even better. If you have feature suggestions, we'd love to hear them via Settings > Send Feedback.

**Bug report review:**
> Sorry about this! Please send us details via Settings > Send Feedback so we can investigate and fix this quickly. We appreciate your patience.

**Feature request review:**
> Great idea! We're always looking at what to build next. Please share more details via Settings > Send Feedback — user input drives our roadmap.

---

## 8) Localization (v1)

- **v1**: English only.
- **v1.1**: Add localization infrastructure (string catalogs).
- **v2**: Priority languages — Spanish, Japanese, German, French, Portuguese.

---

## 9) Open Decisions

1. Whether the app name should include "Network Intelligence" or just "Rin".
2. Whether to use device frames in screenshots or frameless style.
3. Whether to invest in an app preview video before launch or wait for traction.
4. Whether to target "personal CRM" keywords or distance from the CRM category.
