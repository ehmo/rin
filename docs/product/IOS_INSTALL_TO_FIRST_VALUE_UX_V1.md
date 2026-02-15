# iOS Install to First Value UX V1

## 1) Goal
Design a back-to-back experience from App Store install to first retained value, optimized for early-stage network size and single-player utility.

Core objective for first session:
- user gets immediate personal value even if few friends are on Rin.

## 2) Candidate Positioning and Slogan

### Positioning statement
Rin helps you organize and control your real-world network from your phone contacts, without spam or forced social noise.

### Slogan options
1. `Own your network.`
2. `Your contacts, finally under control.`
3. `Findable when you want. Private when you don’t.`
4. `Know your network. Control your reach.`
5. `Turn contacts into real relationships.`

Recommended for v1 testing:
- Primary: `Own your network.`
- Secondary line: `Make it easy to find you and hard to reach you without permission.`

## 3) Product Decisions Locked from Founder Input
1. Onboarding starts with a short intro, then phone number.
2. Social-proof count can be shown before/around verification with abuse rate limits.
3. Contacts permission requested after clear trust explainer.
4. If contacts access denied, app still works in self-management mode.
5. Setup order: name -> photo -> username.
6. Username is skippable; system can assign random two-word default (minimum 6 characters).
7. Circles start with immutable defaults:
- `Everyone` (all contact-list based entities)
- `Public` (public follow-style visibility)
8. Access controls are defaults-first with per-circle overrides.
9. Contact sync should start as early as safely possible to finish during onboarding.
10. Early UX should prioritize single-player value: dedup, enrichment, personal control.

## 4) End-to-End Journey (Install -> First Session)

### Step 0: App Store Impression
User sees:
- Title/subtitle/screenshot copy around control, clarity, and privacy.

System objective:
- set expectation that Rin is contact intelligence + controlled reachability, not a feed app.

### Step 1: Launch Intro (3 screens max)
User sees:
1. what Rin does,
2. why contact import is needed,
3. privacy promise (no unsolicited notifications without permission).

Primary CTA:
- `Continue`

### Step 2: Phone Number Entry
User action:
- enters phone number.

System behavior:
- applies anti-abuse guardrail on number switching attempts.
- computes privacy-safe social proof counter.

UI copy pattern:
- `People in your network already have this number.`
- optional count shown as motivational proof.

### Step 3: OTP Verification
User action:
- completes OTP.

System behavior:
- verifies ownership and creates principal account.
- unlocks onboarding continuation.

### Step 4: Contact Permission Explainer
User sees:
- short plain-language trust contract:
  - why contacts are needed,
  - no spam policy,
  - user-controlled sharing.

CTA:
- `Allow Contacts`
- secondary: `Not now`

System behavior:
- if allowed, starts sync immediately in background while onboarding continues.

### Step 5: Profile Basics
User action order:
1. set name,
2. set photo,
3. set username (optional).

If skipped:
- assign generated username (two words, >=6 chars) and allow easy edit later.

### Step 6: Default Circles + Sharing Defaults
User sees:
- immutable circles pre-created:
  - `Everyone`
  - `Public`
- one global sharing-default screen.
- optional per-circle override entry point (can skip for now).

System behavior:
- saves baseline access policy matrix.

### Step 7: Sync Progress and Immediate Utility
User sees:
- live sync status (non-blocking).
- early single-player outputs as they become available.

Required first-value cards:
1. dedup opportunities found,
2. contact cleanup suggestions,
3. profile/control checklist.

### Step 8: Home (First Session End State)
Primary home objective:
- personal contact quality control, not social feed engagement.

Primary CTA (recommended):
- `Review and clean your network`

Secondary CTAs:
- `Set who can reach you`
- `Improve your profile visibility rules`

## 5) Magic Moment Design (First 2 Minutes)
Recommended magic moment:
- `Rin instantly cleaned and organized part of your network, and you can see/control how people can reach you.`

UI proof bundle (first-session card stack):
1. `X duplicate contacts detected` (with one-tap merge review).
2. `Y contacts with better identity matches` (preview before apply).
3. `Your current reachability policy` (simple summary + one-tap tighten).

Why this works now:
- gives value even with low app network penetration,
- demonstrates control and intelligence immediately,
- creates a reason to return (ongoing cleanup and policy tuning).

## 6) Permission-Denied Fallback Journey
If user denies Contacts:
1. continue onboarding without hard block,
2. land in self-management mode,
3. highlight limited mode benefits:
- manage own profile,
- define public/everyone visibility,
- prepare for later sync.

Re-prompt strategy:
- contextual prompts only when action needs contacts, not repeated nagging.

## 7) Circle UX Automation Rules

Full circle management UX specification: `docs/product/CIRCLE_MANAGEMENT_UX_V1.md`

Summary:
1. Two mandatory circles (Contacts, Public) + three prepopulated (Family, Friends, Colleagues).
2. Per-field access control with three states: Allow, Don't Allow, Ask.
3. Smart suggestions and passive assistance, not mandatory taxonomy work.
4. Show "why this person is here" provenance for trust and reversibility.

Future concept:
- `Met Today` auto-circle is conceptually strong, but implementation must use iOS-safe proximity approaches.

Important iOS platform note:
- Apple Exposure Notification API is restricted to authorized public-health use, not general social networking features.
- Source: https://developer.apple.com/documentation/exposurenotification

## 8) Key UX Metrics for This Flow
1. install -> phone-verified conversion,
2. contact-permission acceptance rate,
3. time-to-first-value card display,
4. first-session completion rate,
5. first-session action rate on cleanup/policy cards,
6. D1 return rate for users who reached first-value state.

## 9) Backend Event Spine (High Level)
- `identity.signup_started`
- `identity.phone_submitted`
- `identity.phone_verified`
- `consent.contacts_prompt_shown`
- `contacts.permission_granted|denied`
- `contact.sync_started|progressed|completed`
- `profile.basics_completed`
- `policy.defaults_set`
- `insight.first_value_generated`
- `user.first_session_primary_action`

## 10) Next UX Artifact
Completed:
- `docs/product/IOS_ONBOARDING_SCREEN_SPEC_V1.md` with per-screen content, states, and empty/loading/error variants.
