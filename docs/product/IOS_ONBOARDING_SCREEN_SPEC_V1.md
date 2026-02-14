# iOS Onboarding Screen Spec V1

## 1) Purpose
Define exact onboarding screens from first launch through first-value home state.

This spec complements:
- `docs/product/IOS_INSTALL_TO_FIRST_VALUE_UX_V1.md`
- `docs/product/USER_JOURNEY_PLAN.md`

## 2) Flow Overview
1. Welcome carousel (3 screens)
2. Phone number input
3. OTP verification
4. Contacts trust explainer + permission
5. Name input
6. Photo setup
7. Username setup (optional)
8. Sharing defaults setup
9. Onboarding sync/progress bridge
10. First-value home

## 3) Screen-by-Screen Specification

## S1: Welcome 1 - Value
Purpose:
- establish single-player utility immediately.

Content:
- Title: `Own your network.`
- Body: `Rin helps you clean, organize, and control your contacts.`

Actions:
- Primary: `Continue`
- Secondary: `Skip intro`

Events:
- `onboarding.welcome_1_shown`
- `onboarding.intro_skipped` (if skipped)

## S2: Welcome 2 - Control and Privacy
Content:
- Title: `You decide who can reach you.`
- Body: `Set default sharing rules and override them by circle.`

Actions:
- Primary: `Continue`
- Secondary: `Back`

Events:
- `onboarding.welcome_2_shown`

## S3: Welcome 3 - Contacts and Trust
Content:
- Title: `No spam. No surprise outreach.`
- Body: `We never notify anyone or expose your information without your permission.`

Actions:
- Primary: `Get started`
- Secondary: `Back`

Events:
- `onboarding.welcome_3_shown`

## S4: Phone Number Input
Purpose:
- collect and verify identity anchor.

Content:
- Title: `What’s your phone number?`
- Supporting text: `This is your primary identity on Rin.`
- Optional social proof line once number entered: `People in your network already have this number.`

Inputs:
- Country selector + phone number field.

Actions:
- Primary: `Send code`
- Secondary: `Back`

Validation:
- proper E.164 formatting.
- anti-abuse guardrail on frequent number changes.

Events:
- `identity.phone_submitted`
- `identity.phone_social_proof_shown`

## S5: OTP Verification
Purpose:
- prove ownership.

Content:
- Title: `Enter verification code`
- Body: `We sent a code to +X XXX XXX XXXX.`

Actions:
- Primary: `Verify`
- Secondary: `Resend code`
- Tertiary: `Change number`

States:
- Loading: spinner + disabled primary.
- Error: `That code didn’t work. Try again.`
- Cooldown: resend timer displayed.

Events:
- `identity.otp_verify_started`
- `identity.phone_verified`
- `identity.otp_verify_failed`

## S6: Contacts Permission Explainer
Purpose:
- explain why full contacts access matters before system prompt.

Content:
- Title: `Import contacts to unlock Rin`
- Body bullets:
  - `Find duplicates and clean your network faster`
  - `Match and enrich contacts when available`
  - `You stay in control of what is shared`

Trust block:
- `We do not message your contacts without permission.`

Actions:
- Primary: `Allow contacts`
- Secondary: `Not now`

Behavior:
- primary triggers iOS Contacts permission dialog.
- if allowed, sync starts immediately in background.

Events:
- `consent.contacts_prompt_shown`
- `contacts.permission_granted|denied`
- `contact.sync_started`

## S7: Name Setup
Content:
- Title: `Your name`
- Body: `How should people in your circles see you?`

Inputs:
- first name (required)
- last name (optional in v1, recommended)

Actions:
- Primary: `Continue`
- Secondary: `Back`

Events:
- `profile.name_set`

## S8: Photo Setup
Content:
- Title: `Add a photo`
- Body: `Profiles with photos are easier to recognize.`

Actions:
- Primary: `Add photo`
- Secondary: `Skip`

Events:
- `profile.photo_set|skipped`

## S9: Username Setup (Optional)
Content:
- Title: `Choose your username`
- Body: `You can change this later.`

Rules:
- min length 6 characters.
- uniqueness enforced.

Skip behavior:
- assign generated two-word username (>=6 chars).
- example pattern: adjective + noun.

Actions:
- Primary: `Continue`
- Secondary: `Skip`

Events:
- `profile.username_set|auto_assigned`

## S10: Sharing Defaults
Purpose:
- set one global default before advanced circle overrides.

Content:
- Title: `Set default sharing`
- Body: `You can override this for each circle later.`

System circles shown:
- `Everyone` (immutable)
- `Public` (immutable)

Actions:
- Primary: `Save defaults`
- Secondary: `Use recommended`

Events:
- `policy.defaults_set`

## S11: Sync Progress Bridge
Purpose:
- avoid dead time while contact sync/dedup runs.

Content:
- Title: `Preparing your network`
- Progress sections:
  - `Importing contacts`
  - `Finding duplicates`
  - `Building suggestions`

Actions:
- Primary: `Continue`

Behavior:
- screen is non-blocking after minimum viable data is ready.

Events:
- `contact.sync_progressed`
- `insight.first_value_generated`

## S12: First-Value Home
Purpose:
- deliver single-player value regardless of network effects.

Top cards:
1. `Duplicates to review`
2. `Contact cleanup suggestions`
3. `Your reachability defaults`

Primary CTA:
- `Review and clean your network`

Secondary CTAs:
- `Set who can reach you`
- `Improve your profile visibility`

Events:
- `onboarding.completed`
- `user.first_session_primary_action`

## 4) Global State Variants

### Loading
- skeletons for cards/lists.
- disable destructive actions during critical write steps.

### Offline / network error
- concise retry state:
  - message: `You’re offline. We’ll continue when connection returns.`
  - action: `Retry now`

### Permission denied (Contacts)
- show limited-mode summary:
  - `You can still set up your profile and sharing.`
- contextual re-prompt only from relevant actions.

### OTP abuse/rate limit
- show cooldown timer and clear reason.
- hide sensitive anti-abuse internals.

## 5) Copy Principles
1. Keep copy direct and non-legalistic.
2. Reassure user around control and permission.
3. Avoid gamified pressure in first session.
4. Keep each body block under 2 short lines where possible.

## 6) Accessibility and Interaction
1. Support Dynamic Type and VoiceOver labels on all onboarding controls.
2. Ensure contrast-compliant text and CTA buttons.
3. Respect reduced motion settings for transitions.
4. Keep primary action placement stable across screens.

## 7) Instrumentation Checklist
Minimum funnel checkpoints:
1. intro shown/skipped,
2. phone submitted,
3. phone verified,
4. contacts permission grant/deny,
5. profile basics complete,
6. defaults saved,
7. onboarding complete,
8. first-value action taken.

## 8) Open UX Decisions
1. Final App Store-facing slogan selection.
2. Exact social-proof copy tone and whether to show count value.
3. Username generator wordlist style and moderation constraints.
4. Whether S11 auto-advances or waits for user tap at fixed readiness threshold.
