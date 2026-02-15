# Launch Readiness Checklist V1

## 1) Purpose

Scored go/no-go checklist for public App Store launch. Evaluated after Stage 3 beta completes. All 7 pillars scored; minimum 85% overall required to proceed.

Companion docs:
- `docs/plan/BETA_COHORT_STRATEGY_V1.md` (beta stage gates)
- `docs/plan/APPSTORE_COMPLIANCE_CHECKLIST_V1.md` (App Store requirements)
- `docs/analytics/KPI_HIERARCHY_V1.md` (metric definitions)

---

## 2) Scoring Model

### 2.1 Scale

Each item scored 0–2:

| Score | Meaning |
|-------|---------|
| **0** | Not started or critically incomplete |
| **1** | Partial — in progress but gaps remain |
| **2** | Ready — meets launch criteria |

### 2.2 Thresholds

- **Overall**: Must score **≥85%** of maximum possible points.
- **Per-pillar minimum**: No individual pillar may score **0** on any item (at least partial progress everywhere).
- **Blockers**: Any item explicitly marked as a **blocker** must score **2** to launch.

### 2.3 Calculation

```
Overall score = (sum of all item scores) / (count of items × 2) × 100%
```

---

## 3) Pillar 1: Product Quality

| # | Item | Blocker | Score |
|---|------|---------|-------|
| 1.1 | Onboarding completion rate >80% (Stage 3 data) | Yes | ☐ |
| 1.2 | Contact import success rate >95% | Yes | ☐ |
| 1.3 | Dedup false positive rate <5% | Yes | ☐ |
| 1.4 | Core flows work on all supported iOS versions (16+) | Yes | ☐ |
| 1.5 | Score computation delivers daily for all users | | ☐ |
| 1.6 | Circle management flows complete and tested | | ☐ |
| 1.7 | Profile and shadow profile switching works | | ☐ |
| 1.8 | Search returns relevant results in <500ms | | ☐ |
| 1.9 | D30 retention >15% (Stage 3 data) | Yes | ☐ |
| 1.10 | NPS >40 (Stage 3 data) | | ☐ |

**Pillar max: 20 points**

---

## 4) Pillar 2: Engineering Stability

| # | Item | Blocker | Score |
|---|------|---------|-------|
| 2.1 | Crash-free rate >99.5% (trailing 7 days) | Yes | ☐ |
| 2.2 | API p95 latency <300ms for core reads | Yes | ☐ |
| 2.3 | API p95 latency <500ms for commands | | ☐ |
| 2.4 | 0 P0 bugs open | Yes | ☐ |
| 2.5 | 0 P1 bugs open | | ☐ |
| 2.6 | Background sync success rate >95% | | ☐ |
| 2.7 | Infrastructure handles 1,000 concurrent users without degradation | Yes | ☐ |
| 2.8 | Score auto-rollback tested and verified | | ☐ |
| 2.9 | CI/CD pipeline green with all quality gates passing | | ☐ |
| 2.10 | Database backup and restore tested | Yes | ☐ |

**Pillar max: 20 points**

---

## 5) Pillar 3: App Store Compliance

| # | Item | Blocker | Score |
|---|------|---------|-------|
| 3.1 | Privacy nutrition label accurate and submitted | Yes | ☐ |
| 3.2 | Privacy policy URL live and accurate | Yes | ☐ |
| 3.3 | Account deletion flow implemented and tested | Yes | ☐ |
| 3.4 | StoreKit 2 subscription flow tested in sandbox | Yes | ☐ |
| 3.5 | Sign In with Apple implemented (if other social sign-in exists) | | ☐ |
| 3.6 | App Store metadata complete (screenshots, description, keywords) | Yes | ☐ |
| 3.7 | Age rating questionnaire submitted | | ☐ |
| 3.8 | Content moderation for UGC (profile names, photos) | | ☐ |
| 3.9 | Push notification permission follows Apple guidelines | | ☐ |
| 3.10 | No private API usage, all frameworks approved | Yes | ☐ |

**Pillar max: 20 points**

---

## 6) Pillar 4: Support Readiness

| # | Item | Blocker | Score |
|---|------|---------|-------|
| 4.1 | In-app feedback mechanism working | | ☐ |
| 4.2 | Help center / FAQ content written (top 10 questions) | | ☐ |
| 4.3 | Dispute submission flow tested end-to-end | Yes | ☐ |
| 4.4 | Auto-adjudication pipeline operational | | ☐ |
| 4.5 | Founder can access and resolve disputes within SLA | | ☐ |
| 4.6 | Account recovery flow documented and tested | Yes | ☐ |
| 4.7 | Known issues list prepared for launch | | ☐ |
| 4.8 | Escalation path defined (what gets paged vs queued) | | ☐ |

**Pillar max: 16 points**

---

## 7) Pillar 5: Growth Mechanics

| # | Item | Blocker | Score |
|---|------|---------|-------|
| 5.1 | Viral coefficient >1.0 (Stage 3 data) | | ☐ |
| 5.2 | Invite flow working (SMS + share sheet + link) | Yes | ☐ |
| 5.3 | Invite conversion rate >30% | | ☐ |
| 5.4 | App Store rating prompt implemented (post-magic-moment) | | ☐ |
| 5.5 | Referral attribution tracking working | | ☐ |
| 5.6 | App Store Optimization (ASO) keywords researched and set | | ☐ |
| 5.7 | Landing page / website live with App Store link | | ☐ |

**Pillar max: 14 points**

---

## 8) Pillar 6: Legal and Privacy Compliance

| # | Item | Blocker | Score |
|---|------|---------|-------|
| 6.1 | Terms of Service finalized and accessible | Yes | ☐ |
| 6.2 | Privacy Policy covers all data collection (contacts, analytics, enrichment) | Yes | ☐ |
| 6.3 | GDPR/CCPA data export functionality working | | ☐ |
| 6.4 | Data retention policies defined and enforced | | ☐ |
| 6.5 | Contact data handling compliant with platform policies (Apple, carriers) | Yes | ☐ |
| 6.6 | Shadow profile anti-abuse policy documented and enforced | | ☐ |
| 6.7 | No PII in analytics events (verified) | Yes | ☐ |
| 6.8 | Third-party data processor agreements in place (PostHog, Sentry, etc.) | | ☐ |

**Pillar max: 16 points**

---

## 9) Pillar 7: Analytics and Measurement

| # | Item | Blocker | Score |
|---|------|---------|-------|
| 7.1 | PostHog instrumentation live for all Stage 1 events | Yes | ☐ |
| 7.2 | Onboarding funnel dashboard operational | | ☐ |
| 7.3 | MAU-V (north star) trackable and dashboarded | Yes | ☐ |
| 7.4 | Daily health check dashboard operational | | ☐ |
| 7.5 | Weekly metrics report auto-generated | | ☐ |
| 7.6 | Retention cohort tracking operational (D1/D7/D30) | | ☐ |
| 7.7 | Premium conversion funnel trackable | | ☐ |
| 7.8 | Score auto-rollback monitoring connected to alerts | | ☐ |

**Pillar max: 16 points**

---

## 10) Score Summary

| Pillar | Max Points | Score | % |
|--------|-----------|-------|---|
| 1. Product Quality | 20 | ☐ | ☐ |
| 2. Engineering Stability | 20 | ☐ | ☐ |
| 3. App Store Compliance | 20 | ☐ | ☐ |
| 4. Support Readiness | 16 | ☐ | ☐ |
| 5. Growth Mechanics | 14 | ☐ | ☐ |
| 6. Legal/Privacy Compliance | 16 | ☐ | ☐ |
| 7. Analytics/Measurement | 16 | ☐ | ☐ |
| **Total** | **122** | **☐** | **☐** |

**Pass threshold: 104/122 (85%)**

---

## 11) Go/No-Go Decision Process

### 11.1 Evaluation Timing

- Evaluate after Stage 3 beta completes (minimum 4 weeks of Stage 3 data).
- Allow 2 weeks between evaluation and target launch date for final fixes.

### 11.2 Decision Flow

```
Score all items
    ↓
Overall ≥85%?
    ├─ No → Identify gaps. Set fix timeline. Re-evaluate in 1 week.
    └─ Yes
        ↓
Any blocker item scored 0?
    ├─ Yes → Fix blockers first. Re-evaluate when resolved.
    └─ No
        ↓
Any pillar below 50%?
    ├─ Yes → Investigate. May proceed if founder accepts risk.
    └─ No → ✅ GO FOR LAUNCH
```

### 11.3 Conditional Launch

If overall score is 80-84%:
- Founder may choose conditional launch with documented risk acceptance.
- Must identify which items will be fixed in first post-launch update.
- First update must ship within 7 days of launch.

### 11.4 Hard No-Go

Launch is blocked regardless of overall score if:
- Any **blocker** item scores 0.
- Crash-free rate <99%.
- Active P0 bug.
- App Store review rejection pending.
- Privacy policy not live.

---

## 12) Post-Launch Stabilization

### 12.1 First 30 Days

- Daily health check (automated dashboard).
- No formula changes for first 14 days.
- Weekly deep dive review.
- Hotfix releases as needed (no feature changes).

### 12.2 30-Day Review

At launch +30 days, review:
- MAU-V trend.
- App Store rating trend.
- Crash-free rate stability.
- Support ticket volume and resolution time.
- Premium conversion rate.

Decide whether to begin Phase 2 feature work or continue stabilization.

---

## 13) Open Decisions

1. Whether conditional launch (80-84%) should require a written risk acceptance document.
2. Whether to add a "Partner/Integration Readiness" pillar if third-party integrations exist at launch.
3. Whether the checklist should be re-evaluated weekly during Stage 3 to track convergence toward readiness.
4. Whether to include a "Marketing Readiness" sub-pillar under Growth Mechanics (press kit, launch blog post, social accounts).
