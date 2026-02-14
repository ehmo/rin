# Rin User Journey Plan (UX + System + Backend)

## Scope (Updated)

This plan reflects latest product decisions:
- **Phone-number-first identity**
- Verified ownership required for every channel/account
- User may attach multiple accounts per channel (multiple phone numbers, emails, etc.)
- Contact import + two-layer dedup + immutable history + full reversibility
- Circles control access and display behavior
- Ranking shown as abstract `Rin Score` (0-100 style), not global absolute rank
- V1 focus is phone/contact graph only (no device contact writeback yet)

## Identity and Handle Policy

- On signup, user sets:
  - Name
  - Username (minimum 6 chars in initial phase)
- One user can hold up to 6 usernames.
- Future monetization path for shorter usernames (when `rin.com` is active):
  - 1 char: $1,000,000
  - 2 chars: $500,000
  - 3 chars: $25,000
  - 4 chars: $1,000
  - 5 chars: $500

## System Actors

- User App (mobile/web)
- API Gateway
- Identity Service
- Username/Handle Service
- Source Ownership/Verification Service
- Contact Ingestion Service
- Dedup & Entity Resolution Service
- User Display Profile Service
- Circle & Policy Service
- Graph Service (local + 2-hop)
- Ranking Service
- Insights/Recommendation Service
- Reachability/Anti-Abuse Service
- Billing Service (premium features)
- Audit/Event Log Service

## Journey 1: First-Time Onboarding

### Step 1: Entry
- User:
  - Lands on app with value proposition.
  - Starts account flow.
- System:
  - Creates onboarding session.
  - Tracks acquisition source.
- Backend:
  - `identity.signup_started` event.

### Step 2: Phone First + Social Proof
- User:
  - Enters primary phone number (required).
  - Sees motivation text: e.g. “People in your network already have this number.”
- System:
  - Computes social-proof count from contact graph overlap (privacy-safe aggregate).
  - Renders count-based motivation.
- Backend:
  - `identity.phone_collected`
  - `identity.phone_social_proof_shown` with aggregate count only.

### Step 3: Phone Ownership Verification
- User:
  - Completes OTP challenge.
- System:
  - Marks phone source verified.
  - Creates authenticated user account.
- Backend:
  - `identity.phone_verified`
  - `identity.account_created`

### Step 4: Name + Username
- User:
  - Chooses display name and primary username.
- System:
  - Enforces username policy (length, uniqueness, reserved names).
- Backend:
  - `handle.primary_set`
  - Username ownership ledger updated.

### Step 5: Optional Additional Channels
- User:
  - Adds email(s), additional phone(s), and later other channels.
- System:
  - Requires ownership verification per added account.
- Backend:
  - `source.connected`
  - `source.verified`
  - account-channel mapping with many-to-one user linkage.

### Step 6: Consent + Permissions
- User:
  - Accepts data use terms and contact import permissions.
- System:
  - Captures versioned consent.
- Backend:
  - `consent.accepted`

## Journey 2: Contact Import + Canonicalization

### Step 7: Raw Ingestion
- User:
  - Connects contacts and sees progress.
- System:
  - Stores raw import exactly as provided.
- Backend:
  - Immutable source snapshot.
  - `contacts.ingest.started/completed`.

### Step 8: Two-Level Dedup (Critical)
- User:
  - Sees possible merge suggestions where confidence is not high.
- System:
  - Level 1 (user-data inference): probabilistic match from phone/email/name patterns.
  - Level 2 (network-grounded certainty): uses confirmed network identity graph.
  - Applies privacy guardrails so enrichments do not reveal hidden user data.
- Backend:
  - Merge ledger stores reason + confidence + source of truth.
  - `entity.merge.applied` events include level and evidence class.

### Step 9: Provenance + Reversibility
- User:
  - Can inspect “where this info came from.”
  - Can undo system or manual merges.
- System:
  - Exposes timeline of every mutation and source.
- Backend:
  - Full audit chain + reversible merge operations.
  - `entity.merge.reverted`

### Step 10: Rin User Override on Match
- User:
  - Sees that matched contacts who are Rin users display using their preferred profile identity (not just local alias).
- System:
  - Replaces local alias display with user-owned display profile where permitted.
  - Supports per-group display variants (name/photo differences by audience/circle).
- Backend:
  - Canonical user-profile display policy resolved at render time.
  - `display.policy.resolved`

## Journey 3: Circle and Access Management

### Step 11: Circle Setup (Low Obtrusion)
- User:
  - Creates/uses circles with minimal friction.
  - Gets reminders because people forget circle membership over time.
- System:
  - Suggests circle maintenance nudges (non-intrusive).
  - Supports fast recategorization patterns.
- Backend:
  - `circle.created`
  - `circle.membership.updated`
  - `circle.maintenance.nudge_shown`

### Step 12: Access Policy Matrix
- User:
  - Sets visibility/access per field (phone/email/address/birthday/etc.).
- System:
  - Shows “how you appear to this circle/person” preview.
- Backend:
  - Policy matrix versioned.
  - `policy.updated`

## Journey 4: First Magic Moment

### Step 13: First Graph Insight
- User:
  - Receives first useful output quickly:
    - `Rin Score` (0-100 style)
    - explanation card (what drives score)
    - local + 2-hop insight suggestions
- System:
  - Computes strength-over-size weighted score.
  - Avoids raw “you are #X of Y” presentation.
- Backend:
  - Ranking component compute (quality, reciprocity, network position, etc.).
  - `insight.generated`
  - `ranking.score_published_local`
  - Score policy from `RIN_SCORE_V1.md`

### Step 14: First Intentional Action
- User:
  - Takes one intentional action (adjust policy/circle, follow suggestion, manage contact).
- System:
  - Confirms impact in plain language.
- Backend:
  - `user.intentional_action`

## Journey 5: Ongoing Loop

### Step 15: Return and Review
- User:
  - Returns to monitor score movement and circle health.
- System:
  - Shows stable score + why-changed explanations.
- Backend:
  - Snapshot retrieval + incremental updates.

### Step 16: Graph and Policy Changes
- User:
  - Adds/removes contacts, updates channels, modifies circles/policies.
- System:
  - Recomputes affected local areas.
- Backend:
  - Graph deltas + bounded recompute.
  - `graph.delta_applied`

## Journey 6: Premium Driver

### Step 17: “How Am I Stored?” Premium Experience
- User:
  - Upgrades to view how they appear across others’ contact storage.
- System:
  - Option A: show aggregate/unique labels.
  - Option B: show explicit per-user mapping (policy-limited, privacy-reviewed).
- Backend:
  - Billing entitlement check.
  - Privacy-safe query path.
  - `premium.feature_accessed`

## Journey 7: Abuse Prevention and Trust

### Step 18: Spam/Abuse Controls
- User:
  - Benefits from verified-identity-based limits.
- System:
  - Applies anti-spam thresholds and trust scoring.
- Backend:
  - `abuse.check_applied`
  - Request/rate limiting events.

### Step 19: Source Hijack / Fraudulent Ownership Handling
- User:
  - Gets security prompts and recovery options.
- System:
  - Freezes risky operations and requests re-verification.
- Backend:
  - `security.anomaly_detected`
  - `source.ownership_dispute_opened`
  - Reversion support from audit ledger.

## Journey 8: Platform Expansion Roadmap

Your planned sequence:

1. Phone + contacts (current focus)
2. Camera + media
3. Location + maps
4. Information layer

Future opt-in example:
- On-device face recognition against anonymized network signatures.
- If probable match:
  - owner gets “you may have X’s photo, share?”
  - target gets “X may have your photo, request?”
- No default opt-in.

## Failure States to Design Upfront

1. Incorrect dedup/enrichment:
- Must be reversible with provenance visible.

2. Circle drift and user forgetfulness:
- Must have gentle maintenance UX.

3. Ranking confusion:
- Must keep score explainable and emotionally positive.

4. Abuse at scale:
- Must enforce verified ownership + progressive trust controls.

## Event Backbone (Updated Minimal Contract)

- `identity.signup_started`
- `identity.phone_collected`
- `identity.phone_social_proof_shown`
- `identity.phone_verified`
- `identity.account_created`
- `handle.primary_set`
- `source.connected`
- `source.verified`
- `consent.accepted`
- `contacts.ingest.started`
- `contacts.ingest.completed`
- `entity.merge.applied`
- `entity.merge.reverted`
- `display.policy.resolved`
- `circle.created`
- `circle.membership.updated`
- `circle.maintenance.nudge_shown`
- `policy.updated`
- `insight.generated`
- `ranking.score_published_local`
- `user.intentional_action`
- `graph.delta_applied`
- `premium.feature_accessed`
- `abuse.check_applied`
- `security.anomaly_detected`
- `source.ownership_dispute_opened`

## KPI Mapping

- Phone onboarding completion rate (Steps 2-3)
- Social-proof uplift on continuation (Step 2)
- Verified channel attach rate (Step 5)
- Time-to-first-insight (Step 13)
- D7 return for score/circle management (Steps 15-16)
- Premium conversion for “How am I stored?” (Step 17)
- Reversal correctness + dispute resolution time (Steps 9, 19)
