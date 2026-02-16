# API Productization and Access Tiers V1

| Field   | Value |
|---------|-------|
| Version | 1.0 |
| Status  | Draft |
| Author  | Founder + Claude Opus 4.6 |
| Bead    | `rin-3i0.18.2` |
| Date    | 2026-02-15 |

Primary references:
- `docs/architecture/SYSTEM_ARCHITECTURE_DB_FIRST_V2.md`
- `docs/architecture/SERVICE_IMPLEMENTATION_BLUEPRINT_V1.md`
- `docs/architecture/DATA_MODEL_BOUNDARIES_V1.md`
- `docs/product/RIN_SCORE_V1.md`
- `docs/architecture/GRAPH_DATA_LIFECYCLE_V1.md`

---

## TL;DR

Rin exposes a four-tier developer API that progressively unlocks graph intelligence while **never exposing raw graph data**. Tier 0 (authentication only) and Tier 1 (score summary + circle names) are self-serve. Tier 2 (mutual connections, distance categories, bidirectional signals) requires business verification and review. Tier 3 (aggregate analytics, recommendation engine, bidirectional data exchange) requires a strategic partnership agreement. Revenue comes from volume-based pricing at Tier 2 and revenue sharing at Tier 3; Tiers 0-1 are free to maximize ecosystem adoption. Architectural enforcement (derived-insight-only responses, Rin-mediated UI flows, differential privacy, scoped short-lived tokens) is the primary protection layer; legal agreements are secondary.

---

## 1) Purpose

Define the access model, packaging, verification requirements, enforcement architecture, and revenue model for Rin's developer platform (targeted for v2/v3).

Goals:
1. Establish Rin as an identity and relationship intelligence layer for third-party apps.
2. Grow the developer ecosystem through a low-friction entry point (Tier 0).
3. Monetize high-value graph intelligence at scale without ever leaking raw graph data.
4. Ensure user consent, privacy, and trust are preserved at every tier.

Non-goals:
- Internal service-to-service API design (covered in Service Implementation Blueprint).
- Mobile SDK implementation details.
- Specific OAuth/OIDC provider selection.

---

## 2) Guiding Principles

1. **Architecture over legal.** Technical enforcement is the primary guard. Legal agreements are supplementary.
2. **Derived insights only.** No tier returns raw graph data. Every response is a computed, bounded insight.
3. **User consent is granular.** Users approve each app independently, per-scope, revocable at any time.
4. **Progressive trust.** Developers earn expanded access through demonstrated responsible use.
5. **Rin mediates sensitive flows.** When an operation touches another user's data, Rin's own UI handles the display, not the third-party app.

---

## 3) Four-Tier Access Model

### 3.1 Tier 0 -- "Sign In with Rin" (Self-Serve, No Review)

**Purpose:** Establish Rin as an identity/authentication layer. This is the beachhead for developer adoption.

**Access model:** Self-serve. Developer registers an app, accepts terms, receives credentials immediately.

**Capabilities:**

| Operation | Type | Description |
|-----------|------|-------------|
| Authenticate user | Read | OAuth/OIDC flow returning authorization code |
| User identity | Read | Rin user ID, display name, avatar URL, verification status |

**Explicitly excluded from Tier 0:**
- Score (any form)
- Contact or connection data
- Circle names or membership
- Graph position or distance

**User experience:** Standard OAuth consent screen. User sees: "App X wants to verify your Rin identity."

**Token model:** Short-lived access token (15 min), refresh token (30 days), scoped to `identity:read`.

---

### 3.2 Tier 1 -- "Rin-Aware Apps" (Self-Serve with Terms Acceptance)

**Purpose:** Apps benefit from Rin's intelligence without extracting graph data. Users get value from sharing their score context with apps they trust.

**Access model:** Self-serve. Developer accepts additional data-handling terms. No human review.

**Capabilities:**

| Operation | Type | Description |
|-----------|------|-------------|
| All Tier 0 capabilities | -- | Inherited |
| Score summary | Read | User's own score summary (categorical, not raw numeric). Requires user's explicit per-app consent |
| Circle names | Read | Names of user's own circles (not circle members) |
| Suggest connection | Write | Submit a suggested contact/connection to user. Displayed in Rin's UI, not the app's UI |

**Consent model:** Per-app, per-scope. User sees: "App X wants to see your Rin Score summary and circle names." Each scope is independently toggleable.

**Key constraint:** The "suggest connection" write operation triggers a flow inside Rin's native UI. The developer app cannot render or control how the suggestion is displayed.

**Token model:** Access token (15 min), refresh token (30 days), scoped to `identity:read`, `score:read_summary`, `circles:read_names`, `connections:suggest`.

---

### 3.3 Tier 2 -- "Rin-Integrated Apps" (Application Review Required)

**Purpose:** Apps enhanced by graph intelligence without exposing the graph itself. Enables meaningful relationship-aware features (e.g., "you and this person have mutual connections") without leaking who those connections are.

**Access model:** Application required. Business verification, privacy assessment, data handling agreement. Human review within 5 business days.

**Requirements before approval:**
1. Business entity verification (registered company or equivalent).
2. Privacy assessment questionnaire completed.
3. Data handling agreement signed.
4. App description and use-case justification reviewed.

**Capabilities:**

| Operation | Type | Description |
|-----------|------|-------------|
| All Tier 0-1 capabilities | -- | Inherited |
| Mutual connection count | Read | Number of mutual connections between two consenting users within app's context. Returns count only, not identities |
| Score explanation components | Read | Qualitative explanation factors (e.g., "strong mutual network," "frequent interaction") for consenting users. Not raw score values |
| Distance category | Read | Relationship distance as category: `close`, `extended`, `distant`. Not exact graph distance |
| Interaction signal contribution | Write | Contribute interaction signals back to Rin (co-occurrence events, shared activity signals, communication frequency hints) |

**Consent model:** Both users must have independently consented for mutual-connection and distance queries. The app submits both user tokens; Rin validates consent on both sides before returning results.

**Signal contribution rules:**
- Contributed signals are treated as one input among many; they cannot dominate score calculations.
- Rin reserves the right to discount or ignore signals from any source.
- Signal schema is defined by Rin and versioned; developers cannot inject arbitrary signal types.

**Token model:** Access token (15 min), refresh token (90 days), scoped per approved capability set. Tokens are app-context-bound (cannot be used across different registered app contexts).

---

### 3.4 Tier 3 -- "Rin Strategic Partners" (Partnership Agreement, Legal Review)

**Purpose:** Deep integrations for strategic partners who contribute meaningful data back to Rin's graph intelligence (e.g., a CRM using Rin for relationship intelligence, a hiring platform using Rin for referral quality).

**Access model:** Business development engagement. Legal review. Partnership agreement. Months-long onboarding.

**Requirements before approval:**
1. All Tier 2 requirements.
2. Revenue sharing agreement executed.
3. Quarterly compliance audit commitment.
4. Dedicated partner engineering allocation (from Rin side).
5. Data exchange agreement specifying bidirectional flows.

**Capabilities:**

| Operation | Type | Description |
|-----------|------|-------------|
| All Tier 0-2 capabilities | -- | Inherited |
| Aggregate graph analytics | Read | Anonymized, differential-privacy-protected aggregate statistics (e.g., network density trends, connection patterns by industry). Never individual-level |
| Recommendation engine access | Read | Rin suggests connections within the partner's context. Partner provides context (e.g., "users interested in topic X"), Rin returns ranked anonymous candidates that the user can then reveal |
| Bidirectional data exchange | Write | Partner contributes interaction data (meeting frequency, collaboration signals, transaction co-occurrence). Rin contributes intelligence back through enhanced recommendations and analytics |

**Aggregate analytics constraints:**
- All aggregate queries are subject to differential privacy guarantees (epsilon budget per query, per partner, per time window).
- Minimum cohort size enforced (no analytics on groups smaller than a defined k-anonymity threshold).
- Results are cached and batched; no real-time individual-level inference is possible.

**Recommendation engine constraints:**
- Rin generates recommendations; the partner app does not see the underlying graph reasoning.
- Recommended users must consent to being discoverable in the partner's context.
- The partner receives anonymized candidate IDs until the target user opts to reveal their identity.

**Token model:** Service-to-service tokens with mutual TLS. Scoped per partnership agreement. Audit-logged at both ends.

---

## 4) Data That Is NEVER Exposed at Any Tier

This list is absolute. No tier, no partnership, no agreement overrides these restrictions.

| Data Category | Rationale |
|---------------|-----------|
| Raw contact lists or friend lists | Core graph asset; exposure would commoditize Rin's value and violate user trust |
| Friends-of-friends traversal | Enables full graph reconstruction through iterative queries |
| Circle membership lists | Circles are private organizational tools; exposing members leaks intimate social structure |
| Raw score values | Numeric scores invite gaming, comparison, and misuse. Only categorical/qualitative representations are allowed |
| Imported contact details (phone numbers, emails) | Users imported these under trust with Rin, not with third-party apps |
| Graph adjacency or topology data | Any form of "who is connected to whom" beyond the specific, bounded queries defined per tier |
| Behavioral telemetry or activity logs | Internal signals used for scoring are never surfaced |

---

## 5) Developer Verification by Tier

| Tier | Developer Verification | Review Process | Time to First API Call |
|------|----------------------|----------------|----------------------|
| 0 | Email verification + terms of service acceptance | Automated (none) | Minutes |
| 1 | Email verification + data handling terms acceptance | Automated (none) | Minutes |
| 2 | Business entity verification + privacy assessment questionnaire | Human review (5 business days) | ~1 week |
| 3 | Legal agreement + compliance audit + BD engagement | Partnership BD process | Months |

**Identity verification escalation:**
- Tier 0-1: Email domain validation only. Disposable email domains blocked.
- Tier 2: Business registration document or equivalent (D-U-N-S, tax ID, incorporation certificate).
- Tier 3: Full KYB (Know Your Business) plus executive sponsor identification.

---

## 6) Developer Trust and Progressive Scoring

### 6.1 Trust Signals Tracked

| Signal | Description | Weight |
|--------|-------------|--------|
| API usage patterns | Normal distribution of calls, no scraping patterns | High |
| Error rates | Low 4xx/5xx rates indicate well-built integration | Medium |
| Rate limit compliance | Respects limits, implements backoff correctly | High |
| User complaint rate | Low rate of users revoking app consent or reporting abuse | Critical |
| Data handling compliance | No evidence of data resale, re-sharing, or misuse | Critical |
| Signal contribution quality | For Tier 2+: contributed signals are internally consistent and improve graph quality | Medium |

### 6.2 Trust Score Outcomes

**Positive outcomes (responsible developers):**
- Automatic rate limit increases (up to 2x tier baseline).
- Access to beta endpoints before general availability.
- Priority review queue for tier upgrade applications.
- Featured placement in Rin's app directory (if one exists).

**Negative outcomes (problematic developers):**
- Rate limit reduction.
- Scope restriction (specific capabilities suspended).
- Tier downgrade.
- Revocation.

### 6.3 Revocation Policy

| Severity | Grace Period | Process |
|----------|-------------|---------|
| Standard violation (rate limit abuse, minor terms breach) | 30 calendar days written notice | Developer notified, given remediation guidance, access reduced during grace period |
| Serious violation (data misuse, consent bypass, re-identification attempts) | 72 hours | Immediate scope restriction, 72-hour window for developer response before full revocation |
| Egregious abuse (data exfiltration, graph reconstruction attempts, user harm) | Immediate | Instant revocation, no grace period, permanent ban, potential legal action |

---

## 7) Architectural Enforcement

Legal agreements are necessary but insufficient. The API architecture itself must make abuse structurally difficult.

### 7.1 Derived Insights Only

Every API response is a computed, bounded result. The system never returns raw records from the graph store.

Examples:
- "Mutual connection count: 7" (not "Mutual connections: Alice, Bob, Carol...").
- "Distance: close" (not "Distance: 2 hops via Node X").
- "Score factors: strong mutual network, frequent interaction" (not "Score: 847").

### 7.2 Rin-Mediated UI Flows

For operations that touch sensitive data or affect other users, the developer app triggers a flow but Rin's native UI handles display and confirmation.

Mediated flows:
- Connection suggestions (Tier 1+): Developer submits suggestion, Rin displays it in-app.
- Mutual connection details (Tier 2): If future tiers allow showing mutual names, it would be via Rin's embedded UI component, not raw API data.
- Recommendation reveal (Tier 3): Anonymous recommendations are revealed through Rin's consent flow.

### 7.3 Differential Privacy on Aggregates

Tier 3 aggregate analytics use differential privacy:
- Per-query epsilon budget.
- Per-partner cumulative epsilon budget per time window.
- Queries that would exceed budget are rejected, not degraded.
- Minimum cohort size (k-anonymity) enforced before differential privacy is applied.

### 7.4 Token Architecture

| Property | Design |
|----------|--------|
| Token lifetime | Short-lived access tokens (15 min default) |
| Refresh tokens | Tier 0-1: 30 days. Tier 2: 90 days. Tier 3: Mutual TLS, no bearer refresh |
| Scope binding | Tokens are scoped to approved capabilities; cannot be used for unapproved endpoints |
| Context binding | Tier 2+ tokens are bound to the registered app context |
| Rotation | Refresh tokens rotate on use (one-time use refresh tokens) |
| Revocation | User can revoke any app's tokens instantly from Rin settings |

### 7.5 Anti-Scraping and Anti-Reconstruction

| Defense | Mechanism |
|---------|-----------|
| Query rate analysis | Detect patterns consistent with systematic graph enumeration |
| Response jitter | Add controlled noise to counts and categories at the margin (e.g., mutual count of 1 might occasionally return 0 or 2) |
| Cross-query correlation detection | Flag apps that systematically query all possible user pairs |
| Per-app query budget | Daily cap on unique user-pair queries (Tier 2) |
| Canary users | Synthetic graph nodes that trigger alerts if queried systematically |

---

## 8) Rate Limits

### 8.1 Baseline Limits

| Tier | Reads/min | Writes/min | Monthly Cap (total calls) |
|------|-----------|------------|--------------------------|
| 0 | 60 | 10 | 50,000 |
| 1 | 120 | 30 | 200,000 |
| 2 | 300 | 60 | 1,000,000 |
| 3 | Custom | Custom | Negotiated per agreement |

### 8.2 Burst Allowance

- All tiers allow 2x burst for up to 10 seconds, followed by standard rate limiting.
- Burst does not count toward monthly cap differently than normal calls.

### 8.3 Rate Limit Response

- HTTP 429 with `Retry-After` header.
- Response body includes `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `X-RateLimit-Monthly-Remaining`.
- Progressive backoff expectation: apps that repeatedly hit limits without backing off get their burst allowance removed.

### 8.4 Trust-Based Adjustments

Responsible developers (per Section 6) can receive automatic upgrades:
- Up to 2x baseline reads/min.
- Up to 1.5x baseline writes/min.
- Up to 2x monthly cap.
- Upgrades are revocable and recalculated monthly.

---

## 9) Revenue Model

### 9.1 Pricing by Tier

| Tier | Pricing Model | Rationale |
|------|--------------|-----------|
| 0 | Free | Maximize adoption. Rin becomes a ubiquitous identity layer |
| 1 | Free | Ecosystem growth. More Rin-aware apps increase user engagement |
| 2 | Free up to monthly cap, then per-call pricing beyond threshold | Value scales with usage. Free tier ensures accessibility for small developers |
| 3 | Revenue sharing on transactions facilitated through the platform | Aligns incentives. Rin earns when partner earns |

### 9.2 Tier 2 Pricing Details (Indicative)

| Usage Band | Price per 1,000 calls |
|-----------|----------------------|
| First 1M calls/month | Free |
| 1M - 10M | $X (to be determined based on market analysis) |
| 10M - 100M | Volume discount (declining per-unit cost) |
| 100M+ | Enterprise agreement |

### 9.3 Tier 3 Revenue Sharing

- Rin takes a percentage of transactions facilitated through the partner integration (e.g., introductions, access grants, recommendations that convert).
- Exact percentage negotiated per partnership.
- Floor: minimum annual commitment to maintain Tier 3 status.
- Ceiling: revenue share capped at a negotiated maximum per transaction.

### 9.4 Future Consideration

- **Introduction fee model:** If a partner app facilitates a paid introduction or access request through Rin's recommendation engine, Rin takes a transaction fee on the facilitated exchange.
- **Premium analytics packages:** Curated aggregate analytics reports beyond the standard API, priced as subscription add-ons for Tier 3 partners.

---

## 10) Consent and Privacy Architecture

### 10.1 User Consent Model

| Consent Property | Design |
|-----------------|--------|
| Granularity | Per-app, per-scope (e.g., user can grant score access but deny circle names) |
| Visibility | User sees a clear consent screen listing exactly what data the app will access |
| Revocability | User can revoke any app's access instantly from Rin settings. Revocation takes effect within 60 seconds |
| Durability | Consent is stored as an immutable audit log. Revocations are appended, not deleted |
| Expiry | Consents expire after 12 months of app inactivity (no API calls using that user's token). User is prompted to re-consent |

### 10.2 Dual-Consent for Multi-User Queries

Tier 2 queries that involve two users (mutual connections, distance) require:
1. Both users have active, non-expired consent for the requesting app.
2. Both users have granted the specific scope being queried.
3. If either user has revoked consent, the query returns a generic "insufficient consent" error (not indicating which user revoked).

### 10.3 Data Minimization

- API responses contain the minimum data needed for the requested operation.
- No "include everything" convenience endpoints.
- Developers cannot request data they have not been approved for, even if technically adjacent.

---

## 11) Developer Onboarding Flow

### 11.1 Tier 0-1 (Self-Serve)

```
Developer signs up on developer.rin.app
    |
    v
Email verification
    |
    v
Accept Terms of Service (Tier 0) or Data Handling Terms (Tier 1)
    |
    v
Register app (name, redirect URIs, description)
    |
    v
Receive client ID + client secret
    |
    v
Access sandbox environment immediately
    |
    v
Request production access (automated check)
    |
    v
First API call in production (minutes)
```

### 11.2 Tier 2 (Reviewed)

```
Complete Tier 1 onboarding
    |
    v
Submit Tier 2 application:
  - Business entity documentation
  - Privacy assessment questionnaire
  - Use-case description
  - Data handling agreement signature
    |
    v
Rin reviews application (~5 business days)
    |
    v
If approved: Tier 2 scopes enabled, production access granted
If denied: Feedback provided, resubmission allowed after 30 days
```

### 11.3 Tier 3 (Partnership)

```
Active Tier 2 developer with good trust score
    |
    v
BD outreach (either direction)
    |
    v
Technical scoping and feasibility assessment
    |
    v
Legal review and partnership agreement negotiation
    |
    v
Compliance audit
    |
    v
Dedicated partner engineering onboarding
    |
    v
Staged rollout (shadow mode -> limited GA -> full GA)
    |
    v
Quarterly review cadence begins
```

---

## 12) API Versioning and Lifecycle

| Policy | Detail |
|--------|--------|
| Versioning scheme | URL path versioning (`/v1/`, `/v2/`) |
| Deprecation notice | Minimum 12 months before any version is sunset |
| Breaking changes | Only in new major versions. Never in minor/patch |
| Beta endpoints | Available to trusted developers (Section 6). Marked with `X-Rin-Beta: true` header. No stability guarantee |
| Changelog | Published per release with migration guides for breaking changes |

---

## 13) Incident and Abuse Response

### 13.1 Abuse Detection

- Automated monitoring for scraping patterns, consent bypass attempts, and anomalous query distributions.
- Dedicated abuse review queue staffed during business hours (initially founder-operated).
- User-facing "Report this app" flow in Rin's connected apps settings.

### 13.2 Incident Response

| Severity | Response Time | Action |
|----------|--------------|--------|
| User reports app misuse | 24 hours | Investigation opened, app flagged |
| Automated abuse detection trigger | 1 hour | Automatic rate reduction, human review queued |
| Data breach by developer | Immediate | App suspended, affected users notified, legal engaged |

---

## 14) Phased Rollout Plan

| Phase | Timeline | Scope |
|-------|----------|-------|
| Phase 1 (v2.0) | Launch | Tier 0 only. "Sign In with Rin" as identity layer |
| Phase 2 (v2.x) | +3-6 months | Tier 1 added. Score summary and circle names |
| Phase 3 (v3.0) | +6-12 months | Tier 2 added with full review pipeline |
| Phase 4 (v3.x) | +12-18 months | Tier 3 pilot with 1-2 strategic partners |
| Phase 5 | Ongoing | Tier 3 GA, introduction fee model evaluation |

Each phase gate requires:
1. Previous tier stable with <0.1% error rate.
2. Abuse detection pipeline validated for new tier's capabilities.
3. User consent flows tested and approved.
4. Documentation and SDK published.

---

## 15) Open Questions

1. **OAuth provider selection.** Build custom OIDC provider vs. leverage existing provider (Auth0, etc.) with Rin-specific claims?
2. **Developer portal hosting.** Subdomain (`developer.rin.app`) vs. separate domain?
3. **SDK strategy.** Provide official SDKs (Swift, Kotlin, JS) or API-first with community SDKs?
4. **Sandbox environment.** Dedicated sandbox with synthetic graph data vs. production with test accounts?
5. **Tier 2 pricing.** Exact per-call pricing requires market analysis and competitive benchmarking.
6. **Tier 3 revenue share percentage.** Requires financial modeling based on partner value creation.
7. **Differential privacy epsilon budget.** Specific epsilon values require privacy engineering analysis.
8. **k-anonymity threshold.** Minimum cohort size for aggregate analytics (candidate: k=50).
9. **Canary user density.** How many synthetic graph nodes per real user for anti-scraping detection?
10. **App directory.** Should Rin maintain a curated directory of approved apps, and if so, when?

---

## 16) Dependencies

| Dependency | Status | Blocking |
|------------|--------|----------|
| Core API surface contract (`02_API_SURFACE_OUTLINE_V1.md`) | In progress | Phase 1 |
| OAuth/OIDC implementation | Not started | Phase 1 |
| User consent UI in iOS app | Not started | Phase 1 |
| Developer portal infrastructure | Not started | Phase 1 |
| Business verification pipeline | Not started | Phase 3 |
| Differential privacy framework | Not started | Phase 4 |
| Partner engineering capacity | Not started | Phase 4 |

---

## 17) Glossary

| Term | Definition |
|------|-----------|
| Derived insight | A computed, bounded result that does not reveal raw graph data (e.g., "close" distance category instead of "2 hops") |
| Mediated flow | A UI flow where Rin's native interface handles sensitive data display, triggered by but not controlled by the developer app |
| Dual consent | Requirement that both users in a multi-user query have independently granted the relevant scope to the requesting app |
| Developer trust score | Internal Rin metric tracking a developer's API usage quality and compliance. Not to be confused with the Trust component of the user-facing Rin Score. |
| Epsilon budget | Differential privacy parameter controlling the total information leakage allowed per partner per time window |
| Graph reconstruction | The threat of an attacker iteratively querying the API to rebuild the underlying social graph |
