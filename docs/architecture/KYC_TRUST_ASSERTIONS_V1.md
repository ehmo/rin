# KYC and Trust Assertions Exposure Strategy V1

| Field | Value |
|-------|-------|
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | ehmo |
| **Bead** | `rin-3i0.18.3` |
| **Epic** | `rin-3i0.18` Developer ecosystem and superapp platform |
| **Dependencies** | `docs/product/RIN_SCORE_V1.md`, `docs/architecture/SERVICE_IMPLEMENTATION_BLUEPRINT_V1.md`, `docs/architecture/DATA_RETENTION_DELETION_V1.md`, `docs/plan/outlines/02_API_SURFACE_OUTLINE_V1.md` |
| **Siblings** | `rin-3i0.18.1` (developer platform vision), `rin-3i0.18.2` (API productization and access tiers) |

---

## TL;DR

Rin's verification pipeline and scoring system produce trust signals that are valuable to third-party applications. This specification defines a **Trust Assertions API** that exposes categorical, privacy-preserving statements about users (e.g., "phone verified", "top-25% score", "3 mutual connections") without ever revealing raw data. All assertions require explicit user consent via OAuth scopes, are designed to resist correlation attacks, and are phased across v2-v3 of the platform. A portable badge system ("Rin Verified", "Rin Trusted", "Rin Connected") provides a lightweight integration path for partner apps.

---

## 1) Purpose

Define how Rin's internally generated trust signals are exposed to third-party developers as **assertions** -- categorical, privacy-preserving statements about a user's identity, network position, and behavior -- without compromising user privacy, graph integrity, or Rin's competitive moat.

This document covers:
- taxonomy of assertions and their derivation sources,
- exposure rules and consent model,
- portable badge system for lightweight integration,
- privacy architecture and anti-correlation design,
- OAuth scope mapping and developer tier requirements,
- implementation phasing across v2-v3.

This document does not cover:
- raw API endpoint schemas (see `rin-3i0.18.2`),
- developer portal UX or SDK implementation details,
- pricing or monetization of API access (see `rin-3i0.18.2`),
- Rin Score internals or tuning (see `docs/product/RIN_SCORE_V1.md`).

---

## 2) Design Principles

1. **Assertions, not data.** Never expose raw underlying data. Every output is a categorical bucket, boolean, or count that cannot be reverse-engineered to reconstruct source material.
2. **User-first consent.** No assertion is shared without the user's explicit, per-app, per-scope authorization. Users can revoke at any time.
3. **Categorical by default.** Continuous values (scores, counts, timestamps) are bucketed into categories before exposure. Exact values are never returned.
4. **No historical leakage.** Only current-state assertions are available. Trend data, historical snapshots, and temporal patterns are never exposed.
5. **Anti-correlation by design.** Per-app identifiers, categorical outputs, and differential privacy techniques prevent third parties from correlating users across apps.
6. **Progressive trust.** Developer access is tiered. More sensitive assertions require higher tier access, stronger review, and stricter audit logging.

---

## 3) Trust Assertions Taxonomy

### 3.1 Identity Assertions (from verification pipeline)

Source: Identity Service, Channel Ownership Service (see `docs/architecture/SERVICE_IMPLEMENTATION_BLUEPRINT_V1.md` sections 3.2, 3.3).

| Assertion | Type | Description | Derivation |
|-----------|------|-------------|------------|
| `phone_verified` | boolean | User has verified at least one phone number | Channel ownership state machine: at least one phone channel in `verified` state |
| `email_verified` | boolean | User has verified at least one email address | Channel ownership state machine: at least one email channel in `verified` state |
| `contact_import_completed` | boolean | User has completed at least one contact import cycle | Contact Sync Service: at least one sync session in `completed` state |
| `profile_completeness` | enum | `"minimal"` / `"standard"` / `"complete"` | Composite: count of populated profile fields against defined thresholds |
| `account_age_bucket` | enum | `"<30d"` / `"30-180d"` / `"180d-1y"` / `"1y+"` | Identity Service: principal creation timestamp bucketed |
| `verification_level` | enum | `"basic"` / `"enhanced"` / `"full"` | Composite (see section 3.1.1) |

#### 3.1.1 Verification Level Definitions

| Level | Criteria |
|-------|----------|
| `basic` | Phone OR email verified |
| `enhanced` | Phone AND email verified, contact import completed |
| `full` | Enhanced + profile completeness = `"complete"` + account age >= 180 days |

These levels are computed server-side and cached. They do not require additional user action beyond what the normal Rin onboarding flow already collects.

### 3.2 Graph Assertions (derived, never raw)

Source: Score Orchestrator, Contact Graph projections. These assertions are derived from the canonical graph truth (see `docs/architecture/GRAPH_DATA_LIFECYCLE_V1.md`) and never expose raw edges, adjacency lists, or graph topology.

| Assertion | Type | Description | Derivation |
|-----------|------|-------------|------------|
| `network_density` | enum | `"sparse"` / `"moderate"` / `"dense"` | Bucketed ratio of actual edges to potential edges in 1-hop neighborhood |
| `score_percentile` | enum | `"top-10%"` / `"top-25%"` / `"top-50%"` / `"below-50%"` | User's Rin Score rank relative to global active-user distribution |
| `mutual_connection_count` | integer | Exact count of mutual connections between two users | Graph intersection query. **Requires consent from both users.** |
| `distance_category` | enum | `"close"` / `"extended"` / `"distant"` / `"none"` | Shortest-path bucket between two users in the reciprocal graph |
| `circle_membership` | boolean | Whether the queried contact appears in any of the user's circles | Circle membership lookup. Does not reveal which circle. |

#### 3.2.1 Distance Category Definitions

| Category | Meaning |
|----------|---------|
| `close` | 1-hop reciprocal connection |
| `extended` | 2-hop path via at least one reciprocal intermediary |
| `distant` | 3+ hops or non-reciprocal path exists |
| `none` | No path found in the reciprocal graph |

#### 3.2.2 Mutual Connection Count: Bilateral Consent

`mutual_connection_count` is the only assertion that returns an exact integer and involves two users. Requirements:
- Both users must have granted the requesting app the `rin.graph.mutual` scope.
- If either user has not granted consent, the API returns `null` (not zero).
- The count includes only reciprocal connections (A has B in contacts AND B has A).

### 3.3 Behavioral Assertions (activity-derived)

Source: Product analytics pipeline, engagement projections. These assertions reflect activity patterns without exposing specific actions, timestamps, or usage details.

| Assertion | Type | Description | Derivation |
|-----------|------|-------------|------------|
| `active_user` | boolean | User has been active within the last 30 days | Any meaningful app session in the trailing 30-day window |
| `engagement_tier` | enum | `"casual"` / `"regular"` / `"power"` | Bucketed session frequency and depth over trailing 30 days |
| `network_maintenance` | enum | `"low"` / `"medium"` / `"high"` | Frequency of circle updates, score checks, and contact management actions over trailing 30 days |

#### 3.3.1 Engagement Tier Thresholds (Internal, Not Exposed)

| Tier | Indicative Criteria |
|------|--------------------|
| `casual` | <2 sessions/week, limited feature depth |
| `regular` | 2-5 sessions/week, moderate feature use |
| `power` | >5 sessions/week, deep feature engagement (circles, score review, contact management) |

Exact thresholds are internal tuning parameters. They are not exposed to developers and may be adjusted based on calibration data.

---

## 4) Exposure Rules

### 4.1 User Consent Model

Every assertion exposed to a third-party application requires **explicit, informed user consent**:

1. Consent is granted **per-app** via OAuth scope selection during the authorization flow.
2. Users see a plain-language description of each assertion scope before granting access (e.g., "This app wants to know if your phone number is verified -- it will NOT see your actual phone number").
3. Consent is **granular**: users can approve some scopes and deny others within the same authorization request.
4. Consent is **revocable**: users can revoke any app's access at any time from Rin's settings. Revocation propagates within 1 hour.
5. Consent is **auditable**: Rin logs every consent grant, revocation, and assertion query for user review.

### 4.2 Assertion Composition Rules

| Developer Tier | Composition Allowed |
|----------------|---------------------|
| Tier 0 (Public) | No assertion access |
| Tier 1 (Registered) | Individual assertions only. One scope per query. No cross-assertion joins. |
| Tier 2 (Verified) | Multiple assertion bundles in a single request. Cross-category queries allowed (e.g., identity + graph). |
| Tier 3 (Partner) | Full bundle access + anonymized aggregate analytics across their user base. |

Rationale: Restricting composition at lower tiers limits the information density available to less-trusted developers, reducing the attack surface for user profiling.

### 4.3 Assertion Freshness and Staleness

| Assertion Category | Refresh Cadence | Staleness Window | Cache Behavior |
|--------------------|----------------|------------------|----------------|
| Identity | On re-verification events | Long-lived (until next verification state change) | Cached indefinitely; invalidated on state change |
| Graph | Daily (aligned with score pipeline cadence) | 24 hours | Recomputed with daily score run |
| Behavioral | Weekly | 7 days | Recomputed on weekly analytics roll-up |

Assertion responses include a `computed_at` timestamp so consuming apps can assess freshness. Rin does not guarantee real-time accuracy; assertions reflect the last computation window.

### 4.4 No Historical Access

Apps receive only the **current-state** assertion value. The API does not support:
- historical queries ("what was this user's score percentile last month?"),
- trend indicators ("is this user's engagement increasing or decreasing?"),
- change notifications ("alert me when this user's verification level changes").

Rationale: Historical and trend data dramatically increases the profiling surface area. If change detection is needed in the future, it would be delivered as a separate, higher-tier capability with additional consent requirements.

### 4.5 Anonymized Aggregates (Tier 3 Only)

Tier 3 partners can request aggregate assertion distributions across their authorized user base:
- Example: "What percentage of my app's Rin-connected users are in the top-25% score bucket?"
- Results are subject to differential privacy and k-anonymity constraints (see section 6).
- Individual-level assertions are never returned at bulk scale for Tier 3 aggregate queries.

---

## 5) Portable Trust Signal: Badge System

### 5.1 Badge Definitions

| Badge | Display Name | Criteria | Minimum Tier |
|-------|-------------|----------|--------------|
| `rin_verified` | Rin Verified | `phone_verified = true` AND `email_verified = true` AND `contact_import_completed = true` | Tier 1 |
| `rin_trusted` | Rin Trusted | `verification_level = "enhanced"` or `"full"` AND `score_percentile` in (`"top-10%"`, `"top-25%"`) AND `account_age_bucket` in (`"180d-1y"`, `"1y+"`) | Tier 2 |
| `rin_connected` | Rin Connected | `mutual_connection_count >= 1` between the user and at least one other user in the requesting app's context | Tier 2 |

### 5.2 Badge Rendering and Integrity

1. **SDK-rendered.** Badges are rendered by the Rin SDK (iOS SDK and web embed), not by the consuming app. This prevents visual forgery and ensures consistent branding.
2. **Real-time verification.** The badge component calls the Rin API on render to confirm validity. A stale or revoked badge displays a neutral state, not a false positive.
3. **24-hour cache.** Badge validity is cached locally for 24 hours to reduce API load. After cache expiry, the SDK re-verifies before rendering.
4. **Tamper detection.** Badge responses are signed with an app-specific HMAC. The SDK validates the signature before rendering. If verification fails, the badge is not displayed.
5. **Visual states.** The badge component has three visual states:
   - **Active**: criteria met, verified within cache window.
   - **Pending**: verification in progress (loading state).
   - **Unavailable**: user has not granted consent, or criteria are not met. Displayed as an empty/neutral element (not a "failed" badge).

### 5.3 Badge API Flow

```
Partner App                    Rin SDK                    Rin API
    │                            │                          │
    │── render badge ──────────→ │                          │
    │                            │── GET /v1/badge/status ─→│
    │                            │                          │── verify consent
    │                            │                          │── evaluate criteria
    │                            │                          │── sign response
    │                            │←── signed badge result ──│
    │                            │── validate HMAC          │
    │                            │── render badge UI        │
    │←── badge displayed ────────│                          │
```

---

## 6) Privacy Architecture

### 6.1 Differential Privacy (Aggregate Queries)

Aggregate queries (Tier 3) apply calibrated Laplace noise to all returned counts and distributions:

| Query Sensitivity | Epsilon (ε) | Use Case |
|-------------------|-------------|----------|
| Standard | 1.0 | General aggregate distributions (e.g., score percentile breakdown) |
| Sensitive | 0.5 | Assertions involving behavioral patterns or network structure |

Privacy budget is tracked per-app per rolling 24-hour window. Once an app's budget is exhausted, aggregate queries return `429 Too Many Requests` until the window resets.

### 6.2 K-Anonymity

No aggregate assertion query returns results for groups smaller than **k=50**:
- If a query would return a bucket with fewer than 50 users, that bucket is suppressed or merged with an adjacent bucket.
- This prevents identification of individuals within small populations.

### 6.3 Per-App Identity Isolation

- Each user's identifier is **per-app** (not a global Rin user ID). The app receives an opaque, app-scoped token.
- Two apps granted access by the same user cannot correlate their tokens to determine they refer to the same person.
- Implementation: HMAC-derived identifiers using `HMAC(user_id, app_secret)` truncated and encoded.

### 6.4 Purpose Limitation and Audit

1. **Purpose declaration.** When registering for assertion access, developers must declare the intended use case for each scope (e.g., "fraud reduction", "safety signal", "community trust").
2. **Audit logging.** Rin logs every assertion query with: requesting app ID, scope, user's app-scoped ID, timestamp, and declared purpose.
3. **Compliance review.** Rin reserves the right to audit assertion usage against declared purposes. Misuse results in scope revocation or tier demotion.

### 6.5 Right to Revoke

- Users can revoke assertion access for any app at any time from Rin's account settings.
- Revocation propagates to the assertion API within **1 hour** (eventual consistency via cache invalidation).
- After revocation, all subsequent assertion queries for that user from the revoked app return `403 Forbidden`.
- Badge components automatically transition to the "Unavailable" state on next verification check.

### 6.6 Anti-Correlation Design Summary

| Attack Vector | Mitigation |
|---------------|------------|
| Cross-app user linking via shared ID | Per-app opaque identifiers (section 6.3) |
| Precise value inference from categorical assertions | Buckets are deliberately coarse; no exact values returned |
| Temporal correlation via assertion change timing | No historical access; no change notifications (section 4.4) |
| Small-group deanonymization in aggregates | K-anonymity with k=50 (section 6.2) |
| Statistical inference from repeated aggregate queries | Differential privacy with budget tracking (section 6.1) |
| Badge presence/absence as a signal | Badge "Unavailable" state is ambiguous (could be no consent OR criteria not met) |

---

## 7) OAuth Scopes for Trust Assertions

### 7.1 Scope Definitions

```
rin.identity.basic          # verified status, account age bucket
rin.identity.enhanced       # verification level, profile completeness tier
rin.graph.mutual            # mutual connection count with specific user
rin.graph.distance          # distance category to specific user
rin.graph.density           # user's network density category
rin.score.percentile        # score percentile bucket
rin.behavior.active         # active user boolean
rin.behavior.engagement     # engagement tier
rin.aggregate.demographics  # anonymized aggregate distributions (Tier 3 only)
```

### 7.2 Scope-to-Tier Mapping

| Scope | Minimum Tier | Assertions Included |
|-------|-------------|---------------------|
| `rin.identity.basic` | Tier 1 | `phone_verified`, `email_verified`, `contact_import_completed`, `account_age_bucket` |
| `rin.identity.enhanced` | Tier 1 | `verification_level`, `profile_completeness` |
| `rin.graph.mutual` | Tier 2 | `mutual_connection_count` (bilateral consent required) |
| `rin.graph.distance` | Tier 2 | `distance_category` |
| `rin.graph.density` | Tier 2 | `network_density` |
| `rin.score.percentile` | Tier 2 | `score_percentile` |
| `rin.behavior.active` | Tier 1 | `active_user` |
| `rin.behavior.engagement` | Tier 2 | `engagement_tier`, `network_maintenance` |
| `rin.aggregate.demographics` | Tier 3 | Aggregate distributions across all granted assertion types |

### 7.3 Scope Request Rules

1. Apps can only request scopes allowed by their tier. Requesting an above-tier scope returns `403` during OAuth authorization.
2. Scope grants are user-specific. An app may hold `rin.graph.mutual` for User A but not User B.
3. Scopes are additive. An app can request additional scopes in subsequent authorization flows without revoking existing grants.
4. Scope descriptions are user-facing and must use plain language. Rin controls the copy; apps cannot customize consent screen text.

---

## 8) Use Cases by Industry

| Industry | Primary Assertions | Example Integration | Value Proposition |
|----------|-------------------|---------------------|-------------------|
| **Marketplaces** | `rin_verified` badge, `engagement_tier` | Display "Rin Verified" badge on seller profiles | Reduce fraud, increase buyer confidence in new sellers |
| **Dating apps** | `mutual_connection_count`, `distance_category` | "You have 3 mutual connections with this person" | Safety signal; social proof reduces catfishing risk |
| **Professional networks** | `score_percentile`, `network_density` | Prioritize outreach to well-connected individuals | Quality signal for recruiters and business development |
| **Financial services** | `verification_level`, `account_age_bucket` | Lightweight KYC supplement for onboarding | Faster onboarding for pre-verified users (not a KYC replacement) |
| **Event platforms** | `circle_membership`, `active_user` | "5 people in your network are attending" | Social context for event discovery and attendance decisions |
| **Community platforms** | `rin_trusted` badge, `engagement_tier` | Grant elevated privileges to trusted members | Bootstrap trust in new communities without building proprietary reputation systems |

### 8.1 Financial Services Disclaimer

Rin assertions are **not a substitute for regulatory KYC/AML compliance**. They are supplementary trust signals that may:
- accelerate onboarding for users who have already completed Rin verification,
- provide additional risk signals for fraud scoring models,
- reduce friction in low-risk transactions.

Financial institutions must still perform their own regulatory-compliant identity verification. Rin does not store or transmit government ID, SSN, or other regulated identity documents.

---

## 9) Developer Tier Requirements

Tier definitions are owned by `rin-3i0.18.2` (API productization and access tiers). This section summarizes the assertion-relevant requirements for each tier.

| Tier | Name | Requirements | Assertion Access |
|------|------|-------------|------------------|
| 0 | Public | API key only | No assertion access. Read-only public API only. |
| 1 | Registered | Verified developer identity, accepted ToS, app review | Identity assertions, active user boolean. Individual queries only. |
| 2 | Verified | Business entity verification, security review, data handling audit | All individual assertions including graph and behavioral. Bundle queries allowed. |
| 3 | Partner | Contractual agreement, dedicated review, compliance audit | Full access including anonymized aggregates. |

### 9.1 Tier Progression

- Tier progression requires human review by Rin team.
- Tier 2 requires a completed security questionnaire and evidence of appropriate data handling practices.
- Tier 3 requires a signed data processing agreement (DPA) and ongoing compliance audits.
- Tier demotion can occur if audit reveals policy violations or misuse of assertion data.

---

## 10) Rate Limits and Quotas

| Tier | Individual Assertion Queries | Aggregate Queries | Badge Verification |
|------|------------------------------|-------------------|--------------------|
| Tier 1 | 1,000/hour per app | N/A | 5,000/hour |
| Tier 2 | 10,000/hour per app | N/A | 50,000/hour |
| Tier 3 | 50,000/hour per app | 100/hour per app | 200,000/hour |

Rate limits are per-app, not per-user. Exceeding limits returns `429 Too Many Requests` with a `Retry-After` header.

Badge verification calls are rate-limited separately and more generously because they are triggered by end-user page views and must not degrade the partner app's UX.

---

## 11) API Response Contract (Illustrative)

### 11.1 Individual Assertion Query

Request:
```
GET /v1/assertions/{user_app_id}
Authorization: Bearer {app_token}
X-Rin-Scopes: rin.identity.basic,rin.score.percentile
X-Idempotency-Key: {uuid}
```

Response:
```json
{
  "user_app_id": "rau_abc123def456",
  "assertions": {
    "phone_verified": true,
    "email_verified": true,
    "contact_import_completed": true,
    "account_age_bucket": "180d-1y",
    "score_percentile": "top-25%"
  },
  "computed_at": "2026-02-15T00:00:00Z",
  "expires_at": "2026-02-16T00:00:00Z"
}
```

### 11.2 Badge Status Query

Request:
```
GET /v1/badge/status/{user_app_id}?badge=rin_verified
Authorization: Bearer {app_token}
```

Response:
```json
{
  "user_app_id": "rau_abc123def456",
  "badge": "rin_verified",
  "status": "active",
  "verified_at": "2026-02-15T00:00:00Z",
  "expires_at": "2026-02-15T23:59:59Z",
  "signature": "hmac_sha256_..."
}
```

### 11.3 Error Response

```json
{
  "error_code": "scope_not_granted",
  "message": "User has not granted the rin.score.percentile scope to this app.",
  "retryable": false,
  "correlation_id": "corr_xyz789"
}
```

Error codes follow the taxonomy defined in `docs/plan/outlines/02_API_SURFACE_OUTLINE_V1.md` section 5.4, extended with assertion-specific codes:
- `scope_not_granted` -- user has not authorized the requested scope.
- `consent_revoked` -- user has revoked access for this app.
- `bilateral_consent_missing` -- mutual connection query requires consent from both users.
- `tier_insufficient` -- app's developer tier does not permit the requested scope.
- `aggregate_k_suppressed` -- aggregate result suppressed due to k-anonymity constraint.

---

## 12) Implementation Phasing

### Phase 1: v2 -- Identity Assertions and Basic Badge

Timeline: Post-v1 launch, aligned with developer platform beta.

Deliverables:
- Identity assertions (`rin.identity.basic`, `rin.identity.enhanced`).
- `active_user` boolean (`rin.behavior.active`).
- "Rin Verified" badge (SDK + API).
- OAuth authorization flow with assertion scopes.
- Per-app identity isolation.
- Tier 1 developer access.

Dependencies:
- Identity Service and Channel Ownership Service are operational (v1).
- OAuth/authorization infrastructure is built.
- Developer registration and review process is defined (`rin-3i0.18.1`).

### Phase 2: v2.5 -- Graph Assertions and Trusted Badge

Timeline: 3-6 months post-v2.

Deliverables:
- Graph assertions (`rin.graph.mutual`, `rin.graph.distance`, `rin.graph.density`).
- Score percentile assertion (`rin.score.percentile`).
- "Rin Trusted" badge.
- "Rin Connected" badge.
- Tier 2 developer access with security review process.
- Bundle query support for Tier 2+.

Dependencies:
- Score pipeline is stable and calibrated.
- Graph projection infrastructure supports assertion derivation queries.
- Bilateral consent mechanism is implemented.

### Phase 3: v3 -- Behavioral Assertions and Aggregates

Timeline: 6-12 months post-v2.

Deliverables:
- Behavioral assertions (`rin.behavior.engagement`).
- Anonymized aggregate analytics (`rin.aggregate.demographics`).
- Differential privacy infrastructure.
- K-anonymity enforcement layer.
- Tier 3 partner program with DPA and compliance audit process.
- Full badge suite.
- Portable trust signal documentation and case studies.

Dependencies:
- Product analytics pipeline is mature enough to derive behavioral assertions.
- Legal review of aggregate data sharing under applicable privacy regulations.
- Partner pipeline has sufficient volume to justify aggregate infrastructure.

---

## 13) Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Assertion gaming (users inflate metrics to earn badges) | Badge credibility erosion | Anti-gaming rules from Rin Score (see `docs/product/RIN_SCORE_V1.md`). Badges depend on multiple independent signals. |
| Developer misuse of assertions for discrimination | Regulatory and reputational risk | Purpose limitation, audit logging, compliance review. ToS prohibits discriminatory use. |
| Correlation attacks across apps despite per-app IDs | Privacy violation | Categorical assertions, no temporal data, differential privacy. Regular red-team reviews of correlation attack surface. |
| Badge forgery by apps that skip SDK rendering | Trust erosion of badge system | Signed responses, HMAC verification, SDK-only rendering. Forgery detection via API call pattern analysis. |
| Assertion freshness misunderstanding by developers | Incorrect trust decisions | Clear `computed_at` and `expires_at` fields. Developer documentation emphasizes staleness semantics. |
| Privacy regulation changes (GDPR, CCPA evolution) | Compliance gaps | Assertions are categorical and minimal by design. Privacy architecture exceeds current requirements. Legal review at each phase gate. |

---

## 14) Open Questions

1. **Billing model for assertion queries.** Should assertion queries be metered separately from general API access, or bundled into tier pricing? Deferred to `rin-3i0.18.2`.
2. **Webhook for consent changes.** Should apps receive a webhook when a user revokes consent, or must they discover revocation via failed queries? Tradeoff: webhooks improve UX but create a timing signal.
3. **Assertion versioning.** When assertion definitions evolve (e.g., engagement tier thresholds change), should apps pin to a version? Likely yes, but versioning strategy needs alignment with general API versioning policy.
4. **International privacy regulation variance.** Should assertion availability vary by jurisdiction (e.g., stricter behavioral assertion limits in the EU)? Needs legal review.
5. **Self-serve tier progression.** Can Tier 1 to Tier 2 progression be partially automated (e.g., automated security questionnaire scoring), or must it remain fully manual? Depends on developer volume.

---

## 15) Glossary

| Term | Definition |
|------|------------|
| **Assertion** | A categorical, privacy-preserving statement about a user derived from Rin's internal systems. Never raw data. |
| **Badge** | A portable, embeddable visual trust signal rendered by the Rin SDK in partner apps. |
| **Bilateral consent** | Requirement that both users involved in a relational assertion (e.g., mutual connections) have independently granted the requesting app access. |
| **Developer tier** | Access level assigned to a third-party developer, determining which assertions and query modes are available. |
| **K-anonymity** | Privacy property ensuring that any individual in a query result is indistinguishable from at least k-1 others. |
| **Per-app identity** | An opaque, app-scoped user identifier that cannot be correlated across different apps. |
| **Scope** | An OAuth permission that grants access to a specific set of assertions. |
| **Staleness window** | The maximum age of an assertion value before it is recomputed. |

---

## 16) Exit Criteria

This specification is complete when:
1. Assertion taxonomy is reviewed and accepted.
2. Privacy architecture is validated against current GDPR/CCPA requirements.
3. OAuth scope design is aligned with general API versioning policy (`rin-3i0.18.2`).
4. Badge rendering approach is validated by iOS engineering for SDK feasibility.
5. Implementation phasing is accepted and reflected in the program backlog.
6. `rin-3i0.18.3` is closed.
