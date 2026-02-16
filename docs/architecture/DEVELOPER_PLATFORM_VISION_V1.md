# Developer Platform Vision V1 (Capability Model and Third-Party Integration)

| Field       | Value                                                    |
|-------------|----------------------------------------------------------|
| Version     | 1.0                                                      |
| Status      | Draft                                                    |
| Author      | Architecture Team                                        |
| Bead        | `rin-3i0.18.1`                                           |
| Date        | 2026-02-15                                               |
| Horizon     | v2 - v3 (not v1 launch scope)                            |

Primary references:
- `docs/architecture/SYSTEM_ARCHITECTURE_DB_FIRST_V2.md`
- `docs/architecture/DATA_MODEL_BOUNDARIES_V1.md`
- `docs/architecture/GRAPH_DATA_LIFECYCLE_V1.md`
- `docs/product/RIN_SCORE_V1.md`
- `docs/architecture/SERVICE_IMPLEMENTATION_BLUEPRINT_V1.md`

---

## TL;DR

Rin's developer platform exposes **relationship intelligence as a service** without ever exposing the underlying contact graph. Third-party apps get derived answers (trust signals, distance metrics, identity verification, recommendations) but never raw graph data. The platform is structured into four capability tiers gated by progressive trust, with a "Service for Signal" data exchange model where developers receive relationship-aware context and return anonymized interaction signals. The core invariant: **the graph is the crown jewel, and it must never leave the castle.**

---

## 1) Purpose

Define the capability model, trust boundaries, data exchange mechanics, and phased rollout plan for Rin's third-party developer platform so that:
- external apps can build on Rin's trust and identity graph without accessing the graph itself,
- Rin's competitive moat deepens with every integration rather than eroding,
- user privacy is enforced architecturally rather than contractually,
- the platform learns from every developer interaction without compromising user sovereignty.

---

## 2) Core Principle

**"The graph is the crown jewel, and it must never leave the castle."**

Developers receive derived intelligence from the graph:
- recommendations,
- trust signals,
- distance metrics,
- identity verification.

Developers never receive:
- raw contact lists,
- edge data,
- friend-of-friend traversals,
- graph topology,
- any data sufficient to reconstruct meaningful subgraphs.

This is not a policy constraint. It is an architectural invariant enforced at the API layer.

---

## 3) Platform Vision

Position Rin not as "access to people's contacts" but as **"relationship intelligence as a service."**

The API answers questions about the graph without ever exposing the graph:
- "Does this user have a strong connection to that user?" (yes/no + confidence)
- "What is the trust distance between these two users?" (ordinal bucket, not path)
- "Is this user likely a real person with genuine relationships?" (score)
- "Which of these users are most relevant to a given context?" (ranked list, no graph reasons)

The platform's value proposition to developers is access to a trust layer that no individual app can build, because it requires the network effect of a contact graph that users have already invested in curating.

---

## 4) Lessons from Major Platforms

These inform every design decision below.

### 4.1 Facebook

Key lesson: **friends-of-friends is the nuclear option.**

- Login with Facebook was the most successful platform feature because it solved a real developer problem (authentication) without requiring deep graph access.
- The Open Graph auto-publishing to feeds was rejected by users and developers alike.
- Cambridge Analytica proved that data, once extracted, cannot be un-extracted. Legal agreements are insufficient. Only architectural enforcement works.
- Start restrictive and expand over time. Never start open and restrict.

### 4.2 WeChat

Key lesson: **the platform gets the relationship, the developer gets the transaction.**

- Mini Programs give developers a commerce/service channel inside WeChat, but WeChat retains the social graph and messaging relationship.
- Most rigorous quality control of any platform: pre-publication review, real-name developer verification, runtime sandboxing, retroactive revocation.
- Developer gets distribution; platform gets intelligence about what users do. Both sides benefit without graph leakage.

### 4.3 Telegram

Key lesson: **user-initiated interaction is the most elegant trust mechanism.**

- Bots cannot initiate contact with users. Users must start the conversation.
- This eliminates spam architecturally rather than through moderation.
- Proves that restricting developer-initiated outreach does not kill ecosystem growth.

### 4.4 LinkedIn

Key lesson: **restricting graph access is compatible with platform success.**

- Thriving ecosystem of recruiting tools, sales intelligence products, and HR integrations.
- None have direct access to the social graph. The graph is the product, not the API.
- LinkedIn sells derived intelligence (InMail, search, recommendations) while keeping the graph proprietary.

### 4.5 Twitter/X (Cautionary Tale)

Key lesson: **unpredictability destroys developer trust.**

- Sudden API pricing changes (free to $42K/month overnight).
- Killing third-party clients that built the platform's early success.
- Trust destruction through inconsistency is nearly impossible to repair.
- Platform invitation must be honored for the life of the product, or developers will never invest.

---

## 5) Data Exchange Model: "Service for Signal"

### 5.1 What Rin Provides to Developers

1. **Authentication**: identity verification via "Sign In with Rin" (OAuth 2.0/OIDC).
2. **Relationship-aware context**: ordinal trust distance, connection strength buckets, mutual connection count (not identities).
3. **Score-based trust signals**: Rin score as a portable trust indicator (with user consent).
4. **Distribution**: ability to surface app actions within Rin's UI through sanctioned integration points.

### 5.2 What Developers Return to Rin

1. **Interaction co-occurrence signals**: anonymized indicators that two users interacted within the third-party app (not what they did).
2. **Connection confirmation signals**: evidence that a relationship exists outside Rin's primary graph sources.
3. **Activity diversity signals**: that a user is active across multiple contexts (not which contexts).
4. **Introduction outcomes**: whether an introduction facilitated through Rin resulted in a connection (success/failure, not content).

### 5.3 Critical Data Exchange Rules

1. **Never require data that would let Rin reconstruct what a user did in a third-party app.** Signals must be relationship-confirming, not behavior-revealing.
2. **All signal return is aggregated and delayed.** No real-time behavioral streams.
3. **Users must explicitly consent to signal sharing.** Per-app, revocable, visible in Rin settings.
4. **Developers must not be able to correlate returned signals to specific user actions.** The signal format must make this impossible, not just prohibited.
5. **Rin must not become a surveillance substrate.** If a signal pattern would let Rin infer sensitive behavior, the signal must be redesigned or dropped.

### 5.4 Signal Schema (Conceptual)

```
interaction_signal {
  app_id:          string    // registered developer app
  signal_type:     enum      // co_occurrence | connection_confirm | activity_diversity | intro_outcome
  user_pair_hash:  string    // double-blind hash of user pair (Rin cannot reverse without both users' consent)
  strength_bucket: enum      // weak | moderate | strong
  period:          string    // weekly aggregation window (never real-time)
  timestamp:       ISO-8601  // aggregation window end, not event time
}
```

---

## 6) Four Platform Moats (Priority Order)

### 6.1 Moat 1: Authentication and Identity (v2)

**"Sign In with Rin"** -- identity layer for apps that care about real relationships.

Value to developer:
- users authenticated against a verified-identity social graph,
- confidence that the user is a real person with genuine relationships,
- optional trust score attached to authentication token.

Value to Rin:
- distribution into third-party apps,
- signal about which apps users trust enough to authenticate with,
- network effect: every app using "Sign In with Rin" makes the next app more likely to adopt.

Technical model:
- standard OAuth 2.0 + OpenID Connect,
- scopes: `identity.basic`, `identity.verified`, `trust.score.read`,
- no graph-related scopes at Tier 0.

Differentiator vs "Sign In with Google/Apple":
- Rin authentication carries a trust signal. Google/Apple confirm identity. Rin confirms identity AND relationship quality.

### 6.2 Moat 2: Relationship Intelligence (v2-v3)

Access to **answers about the graph**, not the graph itself.

Capabilities (all require user consent):
- trust distance between two users (ordinal: close/moderate/distant/unknown),
- mutual connection count (integer, no identities),
- relationship strength bucket for a pair (strong/moderate/weak/none),
- user trust score (Rin score, numeric),
- contextual relevance ranking (given a list of user IDs, return ranked by relevance to requester).

What is never exposed:
- connection lists,
- friend-of-friend paths,
- graph topology or structure,
- edge metadata,
- circle membership,
- any data sufficient to reconstruct even partial subgraphs.

### 6.3 Moat 3: Introduction and Access (v3)

Access pricing exposed as platform infrastructure.

Concept:
- Rin mediates introductions between users who are not directly connected,
- third-party apps can request introductions on behalf of users,
- the access pricing model (from Rin's core product) extends to developer-initiated introductions,
- introduction requests are always user-approved on both sides.

Value to developer:
- structured access to high-value connections without cold outreach,
- Rin handles trust negotiation and consent.

Value to Rin:
- introduction outcome data feeds back into graph intelligence,
- potential revenue from premium introduction facilitation,
- reinforces Rin as the relationship layer, not individual apps.

### 6.4 Moat 4: Portable Trust Signal (v3+)

Rin score as a cross-platform trust primitive.

Concept:
- Rin score becomes a portable credential that users carry across platforms,
- analogous to a credit score for social trust,
- third-party apps can request a user's Rin score (with consent) for trust-sensitive decisions.

Use cases:
- marketplace apps using Rin score to reduce fraud,
- dating apps using Rin score for identity confidence,
- professional networks using Rin score for credibility,
- community platforms using Rin score for moderation trust.

Governance:
- score is read-only for third parties (cannot be written or influenced),
- score methodology is published but not gameable from outside Rin,
- users control which apps see their score.

---

## 7) API Tier Model

### Tier 0: Public (No Review Required)

Access: self-service registration, immediate access.

Capabilities:
- Sign In with Rin (OAuth 2.0/OIDC),
- basic user identity (display name, profile image, verification status),
- user's own Rin score (with user consent).

Rate limits: conservative (suitable for indie apps and prototypes).

Data returned: only the authenticated user's own data. No relational queries.

### Tier 1: Verified Developer (Light Review)

Access: developer identity verification, ToS acceptance, app description review.

Capabilities:
- everything in Tier 0,
- trust distance query (is user A connected to user B? ordinal answer),
- mutual connection count (integer only),
- share-to-Rin deep linking.

Rate limits: moderate.

Data returned: pair-level relational answers. No lists, no traversals.

Review process:
- automated checks (developer identity, app description, stated use case),
- human review only if automated flags trigger.

### Tier 2: Reviewed App (Full Review)

Access: full app review process (functionality, privacy policy, data handling, stated purpose).

Capabilities:
- everything in Tier 1,
- relationship strength bucket queries,
- contextual relevance ranking (given N user IDs, ranked by relevance),
- Rin score read for other users (with their consent),
- progressive trust scoring (app's own trust level with Rin increases over time).

Rate limits: generous.

Data returned: derived intelligence about user pairs and small sets. Still no lists or graph structure.

Review process:
- human review of app functionality and privacy practices,
- sandbox testing period before production access,
- ongoing compliance monitoring.

### Tier 3: Strategic Partner (Partnership Agreement)

Access: business development relationship, legal agreement, deep technical integration review.

Capabilities:
- everything in Tier 2,
- relationship intelligence API (batch queries, higher throughput),
- introduction/access pricing as infrastructure,
- data reciprocity framework (structured signal exchange),
- co-branded trust experiences,
- early access to new platform capabilities.

Rate limits: custom, negotiated.

Data returned: same derived intelligence at higher volume. Graph access invariant still holds absolutely.

Review process:
- full partnership evaluation,
- security audit of partner systems,
- ongoing relationship management.

---

## 8) Architectural Enforcement

### 8.1 Principle: Technical Over Legal

Every privacy guarantee must be enforced architecturally. Legal agreements are a supplement, not a substitute.

If data can be extracted, it will eventually be misused. The only safe data is data that cannot be extracted.

### 8.2 Enforcement Mechanisms

1. **API response shaping**: the API layer computes derived answers server-side and returns only the answer, never the inputs. There is no "raw mode" or "debug mode" that leaks graph data.

2. **Query budget enforcement**: each app has a per-user query budget that makes graph reconstruction infeasible. Querying "is user A connected to user B?" for all possible B values is rate-limited to make enumeration impractical.

3. **Differential privacy on aggregate queries**: any query that touches multiple users applies differential privacy noise to prevent inference of individual edges from aggregate patterns.

4. **Pair-level consent gating**: relational queries about a pair (A, B) require consent from both A and B, or at minimum from the user initiating the query within the app context. This is enforced at the API layer, not delegated to the app.

5. **Signal aggregation and delay**: returned interaction signals are aggregated over weekly windows and delayed, preventing real-time behavioral correlation.

6. **App sandboxing**: each app's view of the graph is isolated. Two colluding apps cannot combine their query results to reconstruct more graph than either could access alone. Cross-app query correlation is architecturally prevented.

7. **Revocation with teeth**: when an app's access is revoked, all cached derived data expires. Apps must re-query and re-consent. There is no "downloaded data" to un-download because no raw data was ever provided.

### 8.3 Graph Reconstruction Attack Mitigations

| Attack Vector | Mitigation |
|---------------|------------|
| Enumerate all pairs via trust-distance queries | Per-app per-user query budget; anomaly detection on query patterns |
| Correlate multiple pair queries to infer topology | Query results include calibrated noise at low confidence levels |
| Collude across multiple registered apps | Cross-app query isolation; app fingerprinting; human review for suspicious registration patterns |
| Use introduction outcomes to map connections | Introduction outcomes are binary (success/fail) with no path or intermediary data |
| Accumulate historical queries to build graph over time | Rolling query budgets; stale result expiration; periodic budget reset |
| Abuse batch ranking endpoint to enumerate connections | Ranking input must be app-provided list (not "give me all"); result is order only, no scores |

---

## 9) Developer Experience

### 9.1 Onboarding Flow

1. Register at `developers.rin.app`.
2. Verify developer identity (email + phone, optionally Rin account).
3. Create app, describe use case, select initial tier.
4. Receive API credentials and sandbox access.
5. Build and test against sandbox (synthetic graph, realistic responses).
6. Submit for review (Tier 1+).
7. Receive production credentials upon approval.

### 9.2 SDK and Integration

- **iOS SDK** (Swift): native integration for iOS apps.
- **Web SDK** (TypeScript): for web applications using Sign In with Rin.
- **Server SDK** (Go, Python, Node): for backend-to-backend API calls.
- **Webhook support**: for async signal delivery and event notifications.

### 9.3 Developer Dashboard

- real-time API usage and quota monitoring,
- user consent analytics (how many users authorized, revoked),
- signal quality metrics (for apps participating in data reciprocity),
- app trust score (progressive trust level with Rin),
- review status and compliance notifications.

### 9.4 Sandbox Environment

- synthetic graph with realistic topology and scoring,
- deterministic responses for integration testing,
- no real user data, ever,
- full API parity with production (same endpoints, same response shapes).

---

## 10) Mistakes to Avoid

Derived from platform history research. Each prevention strategy is architecturally enforced.

| Mistake | Who Made It | Prevention |
|---------|-------------|------------|
| Exposing friends-of-friends | Facebook pre-2014 | Never expose transitive graph data. API returns ordinal answers, not paths or lists. |
| Auto-publishing to user feeds | Facebook Open Graph | All sharing must be explicit and user-initiated. No implicit social actions. |
| Killing third-party clients | Twitter | Honor platform invitation for the life of the product. Deprecation requires 12+ months notice. |
| Sudden API pricing changes | Twitter/X 2023 | 6+ months notice minimum. Grandfather early developers for 18 months. Price changes require published justification. |
| Trusting legal agreements over technical controls | Facebook / Cambridge Analytica | Enforce architecturally. If data cannot be extracted, it cannot be misused. Legal is supplementary. |
| No review process for graph access | Telegram (early) | All relational queries (Tier 1+) require developer review. Tier 0 is identity-only. |
| Over-restricting small developers | LinkedIn | Tier 0 and Tier 1 must be genuinely useful standalone. Authentication and trust-distance are high value even without deeper access. |
| Opaque enforcement and bans | Multiple platforms | Published review criteria. Appeal process with human review. Transparent violation explanations. |

---

## 11) Data Reciprocity Framework

### 11.1 Principle

The platform relationship is bidirectional. Rin provides intelligence; developers provide signals that improve the graph. Neither side extracts more than they contribute over time.

### 11.2 Developer Signal Contributions

| Signal Type | What Developer Sends | What Rin Learns | What Rin Never Learns |
|-------------|---------------------|-----------------|----------------------|
| Co-occurrence | Hashed user pair + strength bucket | Two users interact outside Rin | What they did |
| Connection confirmation | Hashed user pair + boolean | Relationship exists in another context | Nature of relationship |
| Activity diversity | User hash + active boolean | User is active across ecosystem | Which apps, what activity |
| Introduction outcome | Introduction ID + success boolean | Whether facilitated intro worked | Conversation content |

### 11.3 Progressive Trust Scoring for Apps

Apps that contribute higher-quality signals earn:
- higher rate limits,
- earlier access to new capabilities,
- priority review for tier upgrades,
- featured placement in developer marketplace (v3).

Signal quality is measured by:
- consistency with Rin's existing graph signals (cross-validation),
- volume relative to app's user base,
- user complaint rate about the app's signal collection disclosures.

---

## 12) Phased Rollout Plan

### Phase 1: v2 Launch

Deliverables:
- Sign In with Rin (OAuth 2.0/OIDC) production-ready.
- Tier 0 and Tier 1 API endpoints live.
- Developer portal (`developers.rin.app`) with documentation.
- Sandbox environment with synthetic graph.
- Developer Terms of Service published.
- Developer dashboard (basic: usage, quota, status).

Success criteria:
- 5+ apps using Sign In with Rin in production.
- Sandbox used by 20+ developers.
- Zero graph data leakage incidents.

### Phase 2: v2.5 Expansion

Deliverables:
- Tier 2 API endpoints with full app review process.
- iOS and Web SDKs (public release).
- 10-20 beta partners with Tier 2 access.
- Progressive trust scoring for apps (initial implementation).
- Share-to-Rin deep linking for third-party apps.
- Data reciprocity signal ingestion pipeline (basic).

Success criteria:
- 10+ Tier 2 apps in production.
- Measurable signal quality from reciprocity framework.
- Developer NPS > 40.

### Phase 3: v3 Full Platform

Deliverables:
- Tier 3 strategic partnerships (3-5 initial partners).
- Relationship intelligence API (batch, high-throughput).
- Introduction/access pricing as platform infrastructure.
- Data reciprocity framework (full, with progressive trust).
- Developer marketplace (apps discoverable within Rin).
- Portable trust signal (Rin score as cross-platform credential).

Success criteria:
- platform API calls represent meaningful percentage of total Rin API traffic.
- Rin score used as trust signal by 10+ external apps.
- Introduction facilitation generating measurable conversion.
- Graph intelligence quality measurably improved by developer signal contributions.

---

## 13) Governance and Trust Commitments

### 13.1 Developer Bill of Rights

1. **Predictability**: API contracts are versioned. Breaking changes require 6+ months notice and migration path.
2. **Transparency**: review criteria, rate limits, and enforcement policies are published, not secret.
3. **Fairness**: tier advancement criteria are objective and documented. No preferential treatment based on company size.
4. **Appeal**: every enforcement action includes explanation and appeal path with human review.
5. **Stability**: early adopters are grandfathered through pricing and policy changes for a minimum of 18 months.
6. **Privacy**: Rin will never sell developer usage data or share it with competitors.

### 13.2 User Bill of Rights (Platform Context)

1. **Consent**: every third-party data access requires explicit, informed, per-app user consent.
2. **Visibility**: users can see exactly which apps have access and what data categories they can query.
3. **Revocation**: users can revoke any app's access instantly, with immediate effect.
4. **Minimization**: apps receive the minimum data necessary for their stated function and approved tier.
5. **No surprises**: no social actions taken on behalf of the user without explicit, per-action approval.

### 13.3 Platform Review Board

- quarterly review of platform policies, enforcement actions, and developer feedback,
- includes external advisors (privacy, developer relations, security),
- publishes transparency report on enforcement actions (anonymized aggregate statistics).

---

## 14) Revenue Model (Sketch)

Not fully specified here; included for architectural alignment.

| Revenue Stream | Tier | Model |
|----------------|------|-------|
| Sign In with Rin | 0 | Free (growth/distribution play) |
| Trust distance / relationship queries | 1-2 | Freemium: generous free tier, usage-based above threshold |
| Relationship intelligence (batch) | 3 | Custom pricing, negotiated |
| Introduction facilitation | 3 | Per-introduction fee or revenue share |
| Portable trust signal (Rin score) | 2-3 | Usage-based |
| Developer marketplace listing | 2-3 | Free basic listing; featured placement is paid |

Architectural implication:
- metering and billing infrastructure must be designed into the API gateway from v2 launch, even if initially free.

---

## 15) Dependencies on Core Architecture

| Platform Capability | Core Dependency | Reference |
|---------------------|----------------|-----------|
| Sign In with Rin | Identity Service, Channel Ownership | `SERVICE_IMPLEMENTATION_BLUEPRINT_V1.md` |
| Trust distance queries | Score Service, Graph Data Lifecycle | `RIN_SCORE_V1.md`, `GRAPH_DATA_LIFECYCLE_V1.md` |
| Relationship strength | Contact Edge lifecycle, Score Service | `DATA_MODEL_BOUNDARIES_V1.md` |
| Contextual ranking | Score Service, Search Projection | `SEARCH_RELEVANCE_STRATEGY_V1.md` |
| Introduction facilitation | Access pricing model (TBD) | Product spec required |
| Signal ingestion | Contact Sync pipeline, Event Contract | `EVENT_CONTRACT_CATALOG_V1.md` |
| Consent management | Policy/Circle Service | `DATA_MODEL_BOUNDARIES_V1.md` |

---

## 16) Open Questions

1. **Consent UX**: how does per-app, per-scope consent present in iOS without excessive friction? Needs UX research.
2. **Score stability under signal ingestion**: does third-party signal ingestion destabilize Rin score? Needs simulation.
3. **Pair-hash scheme**: exact double-blind hashing protocol for user pair signals. Needs cryptographic design.
4. **Query budget calibration**: what per-user per-app query limits prevent reconstruction while remaining useful? Needs adversarial modeling.
5. **Cross-app isolation enforcement**: technical mechanism for preventing query correlation across colluding apps. Needs security architecture.
6. **Introduction pricing model**: exact fee structure and revenue share for facilitated introductions. Needs product/business design.
7. **Developer identity verification**: required verification level for each tier (email only vs government ID vs Rin account with score threshold).
8. **International data residency**: how developer API access interacts with jurisdiction-specific data residency requirements.

---

## 17) Exit Criteria

`rin-3i0.18.1` is complete when:
- platform vision and positioning are documented (this document),
- capability model with four moats is defined and prioritized,
- API tier model with access gates is specified,
- data exchange model ("Service for Signal") is defined with privacy invariants,
- architectural enforcement mechanisms are enumerated,
- phased rollout plan with success criteria exists,
- platform lessons from major platforms are documented with prevention strategies,
- open questions are logged for future resolution.
