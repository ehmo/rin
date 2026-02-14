# Rin Design Decision Memo (V1)

## 1) Corpus Coverage

Analyzed inputs:
- Claude transcripts: 2
- PMF guide: 1
- Link dump: 35 links
- Additional PDF (replacement for ChatGPT share): 1
- Archived sources: 34/35 links + PDF text extract
- Media extraction:
  - Tweet links processed: 29
  - Substantive content-media posts: 13
  - Recoverable videos: 6

## 2) What The Evidence Says

### Strong demand signals (consistent across sources)
- People want a **friend CRM** (history, context, who-knows-who).
- People want **serendipity tools** (who is nearby / available / in-city).
- People want **low-noise social utility**, not another content feed.
- “Network as leverage” is a motivating frame that can drive usage.

### Strong design constraints
- Rank systems need predictability and explanation.
- Circle systems need both simple defaults and advanced controls.
- Trust/safety primitives are mandatory early (ownership, fraud, hijack, spam).
- Identity should be phone-first with strict channel ownership verification.

### Weak/noisy signals
- Generic social commentary without actionable product mechanics.
- Media-only references with unclear context.

## 3) Product Direction (Refined)

Working category:
- **Friend CRM + controlled reachability + social graph intelligence**

Positioning:
- **Be easy to find, hard to reach.**

Primary early user:
- High-context, high-network users (“super connectors”).

## 4) V1 Product Boundary (Recommended)

Include:
1. Identity + profile:
- Start with phone-first signup and verified source ownership per channel/account.
- Support multiple accounts per channel (multiple phones/emails).
- Name + username at registration (initial min length constraint).

2. Contact graph foundation:
- Import contacts, deduplicate, maintain immutable source history.

3. Circles:
- User-defined circles with optional default templates.
- Circle-based access control for profile fields.

4. Utility outputs:
- Local and 2-hop insights (not global leaderboard yet).
- “Who you may have forgotten” + “who can bridge you” suggestions.

5. Relationship management:
- Notes/history timeline for contacts (friend CRM core loop).

6. Contact identity override:
- When a contact is a Rin user, render their user-owned display profile (policy permitting), not only local alias data.

Exclude (for initial launch):
- Full global rank publication
- Broad paid reachability marketplace
- Heavy social content feed
- Full multi-app ingestion explosion

## 5) Ranking + Distance Policy (Design-Level)

### Rank model
- Keep two components separate:
1. **Relationship Strength Score** (cadence/reciprocity/context)
2. **Network Position Score** (centrality/random-walk style)

- User-facing score should be composed + explainable.
- Show rank as bands/percentiles first, not fragile absolute numbers.
- Proposed V1 weighting spec captured in `RIN_SCORE_V1.md`.

### Update cadence
- Official rank refresh on fixed schedule (daily/weekly).
- Optional provisional local updates clearly labeled as estimates.

### Distance
- Keep distance visible as an informational primitive.
- Delay aggressive monetization function until behavioral data validates fairness and abuse resistance.

### Monetization (early driver)
- Candidate paid driver: **“How am I stored in other people’s phones?”**
- Keep two possible product forms for testing:
1. Aggregate/identifier-based summary
2. Explicit per-user listing (privacy constrained)

## 6) Media-Derived UI Guidance

Directly useful visual references found:

1. Access-level sharing screen pattern:
- Fine-grained per-field access controls mapped to circles/persons.
- Source: keyframe extracted from tweet `012` in `resources/media/keyframes/012.jpg`.

2. Circle color interaction:
- Circle color picker mechanic with clear visual hierarchy.
- Source: keyframe `034` in `resources/media/keyframes/034.jpg`.

3. Location/network map utility:
- Lightweight map-based friend distribution and “follow location” concept.
- Source: keyframe `013` in `resources/media/keyframes/013.jpg`.

## 7) Core Risks To Control Early

1. Algorithm credibility risk:
- If users can’t understand why rank moves, trust collapses.

2. Identity trust risk:
- Wrong merges or source-ownership fraud can permanently damage product trust.

3. Behavioral incentive risk:
- Raw ranking can encourage vanity/gaming instead of meaningful relationships.

4. Operational complexity risk:
- Global-scale ambitions can outpace product validation.

5. Circle-management risk:
- Users forget and mismanage circles; low-obtrusion maintenance UX is critical because circles gate access.

## 8) Immediate Next Design Work

1. Lock exact V1 magic moment definition.
2. Freeze V1 score components and explanation model.
3. Define circle schema (default set + user-custom fields + limits).
4. Design source-ownership verification + recovery flows.
5. Specify V1 insight surfaces (local + 2-hop discovery) with no-feed UX.
6. Lock username policy (initial constraints + future paid short-handle rules + max handles/user).
7. Define phased product expansion explicitly:
   - Phase 1: phone + contacts
   - Phase 2: camera + media
   - Phase 3: location + maps
   - Phase 4: information layer
