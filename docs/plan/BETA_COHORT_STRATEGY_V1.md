# Beta Cohort Strategy V1

## 1) Purpose

Define the staged beta rollout plan: cohort selection, test goals per stage, go/no-go criteria, and feedback collection.

Companion docs:
- `docs/plan/BATTLE_PLAN_IMPLEMENTATION_V1.md` (program timeline)
- `docs/plan/APPSTORE_COMPLIANCE_CHECKLIST_V1.md` (TestFlight requirements)
- `docs/product/IOS_ONBOARDING_SCREEN_SPEC_V1.md` (onboarding funnel)

**Staging terminology:** This document uses **Beta Stage 1/2/3** for user cohort progression. Infrastructure deployment uses a separate scheme (**Infrastructure Stage A/B/C**) — see Service Implementation Blueprint.

---

## 2) Staged Rollout Model

```
Stage 1: 50 users → validate core loop
    ↓ go/no-go gate
Stage 2: 200 users → measure retention
    ↓ go/no-go gate
Stage 3: 1,000 users → test growth mechanics
    ↓ go/no-go gate
Public launch
```

---

## 3) Stage 1: Core Loop Validation (50 Users)

### 3.1 Cohort Selection

- Friends, family, and close professional network of founder.
- Mix of:
  - Heavy phone users (500+ contacts) — stress test import/dedup.
  - Light phone users (50-100 contacts) — test low-contact value prop.
  - iOS-only users (no Android testers in v1).
  - At least 5 pairs of people who know each other — test graph overlap and enrichment.

### 3.2 Distribution

- TestFlight internal testing (up to 100 internal testers, no App Store review required).
- Direct invite via personal message with TestFlight link.

### 3.3 Test Goals

| Goal | Success metric | Target |
|------|---------------|--------|
| **Onboarding completion** | % who reach first-value home (S12) | >80% |
| **Contact import success** | % who grant contacts permission | >70% |
| **Magic moment delivery** | % who see dedup/cleanup cards | >90% of importers |
| **First action** | % who take at least one action (merge, circle assign, policy change) | >50% |
| **Crash-free rate** | % sessions without crashes | >99% |
| **Critical bugs** | P0/P1 bugs discovered | 0 P0 at stage end |

### 3.4 Feedback Collection

- Weekly 1:1 conversations (founder talks to 10+ testers personally).
- In-app feedback button (shake to report or Settings > Send Feedback).
- Crash reports via Sentry.
- Screen recording opt-in for UX observation.

### 3.5 Duration

- 2-3 weeks active testing.
- 1 week for bug fixes and iteration before Stage 2 gate.

### 3.6 Go/No-Go Criteria

**Go to Stage 2 when:**
- [ ] Onboarding completion >80%.
- [ ] 0 P0 bugs open.
- [ ] Import/dedup pipeline stable (no data loss incidents).
- [ ] At least 3 testers report the magic moment ("this is useful").
- [ ] Core flows work on all supported iOS versions.

**No-Go signals:**
- P0 crash affecting >5% of sessions.
- Contact import fails or produces duplicates for >10% of testers.
- Onboarding completion <60%.

---

## 4) Stage 2: Retention Measurement (200 Users)

### 4.1 Cohort Selection

- Stage 1 cohort (retained).
- Extended network: friends of friends, early supporters, professional contacts.
- More demographic diversity (age, contact list size, geographic spread).
- At least 20 pairs of mutual contacts — test graph enrichment at scale.

### 4.2 Distribution

- TestFlight external testing (up to 10,000 testers, requires Beta App Review).
- Invite via personal message + limited shareable invite link.

### 4.3 Test Goals

| Goal | Success metric | Target |
|------|---------------|--------|
| **D1 retention** | % who return day after first session | >40% |
| **D7 retention** | % who return within 7 days | >25% |
| **Score engagement** | % who view their Rin Score at least twice | >30% |
| **Circle adoption** | % who create at least 1 custom circle | >20% |
| **Profile management** | % who modify access policies after default setup | >15% |
| **Dedup quality** | False positive rate on auto-merges | <5% |
| **Sync reliability** | Background sync success rate | >95% |

### 4.4 Feedback Collection

- NPS survey at D7 and D14.
- In-app feedback button (continued).
- Cohort Slack/WhatsApp group for real-time feedback.
- Analytics funnel dashboards operational by this stage.

### 4.5 Duration

- 3-4 weeks active measurement.
- 1-2 weeks for iteration before Stage 3 gate.

### 4.6 Go/No-Go Criteria

**Go to Stage 3 when:**
- [ ] D7 retention >25%.
- [ ] NPS >30.
- [ ] 0 P0 bugs open.
- [ ] Dedup false positive rate <5%.
- [ ] At least 5 organic "this is great" moments reported without prompting.
- [ ] Background sync stable across iOS versions.

**No-Go signals:**
- D7 retention <15%.
- NPS <0 (net detractors).
- Data integrity issue (lost contacts, wrong merges) affecting >3 users.

---

## 5) Stage 3: Growth Mechanics (1,000 Users)

### 5.1 Cohort Selection

- Stages 1+2 (retained).
- Broader invite distribution:
  - Invite codes (each existing user gets 5-10 invite codes).
  - Targeted outreach to communities (tech, productivity, privacy-conscious groups).
  - Social media teaser posts with TestFlight link.

### 5.2 Distribution

- TestFlight external testing (continued).
- Invite code system for controlled expansion.

### 5.3 Test Goals

| Goal | Success metric | Target |
|------|---------------|--------|
| **Viral coefficient** | Invites sent per active user | >1.5 |
| **Invite conversion** | % of invite recipients who install | >30% |
| **D30 retention** | % still active after 30 days | >15% |
| **Premium conversion** | % who hit premium paywall | >20% |
| **Premium trial** | % who start premium trial (if offered) | >5% |
| **Graph density** | Average mutual connections per user | >3 |
| **Infrastructure stress** | API p95 latency under load | <500ms |
| **Concurrent sync** | 100+ simultaneous imports stable | Yes |

### 5.4 Feedback Collection

- Automated NPS at D7, D14, D30.
- In-app feedback (continued).
- App Store rating prompt (soft, post-magic-moment, max once per 30 days).
- Analytics dashboards fully operational.
- Cohort comparison: Stage 1 vs 2 vs 3 behavior differences.

### 5.5 Duration

- 4-6 weeks active measurement.
- 2 weeks for final polish before public launch gate.

### 5.6 Go/No-Go Criteria

**Go to public launch when:**
- [ ] D30 retention >15%.
- [ ] Viral coefficient >0.5 (organic growth emerging; K >1.0 is aspirational, not required for launch).
- [ ] Premium paywall exposure >20% of users.
- [ ] Infrastructure handles 1,000 concurrent users without degradation.
- [ ] NPS >40.
- [ ] App Store compliance checklist 100% complete.
- [ ] 0 P0 or P1 bugs open.
- [ ] Dispute/security flows tested with at least 5 real cases.

**No-Go signals:**
- D30 retention <10%.
- Viral coefficient <0.3 (no organic spread).
- Infrastructure instability under load.
- App Store review rejection on any compliance item.

---

## 6) Cross-Stage Infrastructure

### 6.1 Analytics Requirements by Stage

| Stage | Requirement |
|-------|------------|
| 1 | Crash reporting (Sentry). Basic funnel events logged. Manual analysis. |
| 2 | Product analytics dashboard. Automated funnel metrics. Retention cohort tracking. |
| 3 | Full analytics suite. A/B test infrastructure ready. Premium conversion funnel. |

### 6.2 Support Requirements by Stage

| Stage | Support model |
|-------|--------------|
| 1 | Founder handles all feedback directly. |
| 2 | Founder + automated FAQ/help center. Cohort group chat for quick responses. |
| 3 | Help center + in-app support. Founder escalation for complex issues. |

### 6.3 Build Cadence

| Stage | Release frequency |
|-------|------------------|
| 1 | Daily or every-other-day. Fast iteration. |
| 2 | 2x per week. Stabilizing. |
| 3 | Weekly. Polish and reliability focus. |

---

## 7) Premium Beta Strategy

### 7.1 Premium in Beta

- Stage 1: premium features unlocked for all testers (testing functionality, not conversion).
- Stage 2: premium features gated behind paywall for 50% of new testers (A/B test conversion).
- Stage 3: premium features gated for all new testers. Existing testers grandfathered during beta.

### 7.2 Beta Pricing

- No real charges during TestFlight beta (Apple sandbox).
- Use StoreKit sandbox environment for payment flow testing.
- Premium pricing ($4.99/mo, $49.99/yr) configured but not billed until public launch.

---

## 8) Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Low onboarding completion | Iterate onboarding copy and flow between stages |
| Poor retention | Add engagement hooks (score updates, circle suggestions) |
| Contact import failures | Expand device/iOS version test matrix |
| Privacy concerns from testers | Over-communicate data handling; provide easy deletion |
| Beta fatigue (testers lose interest) | Keep stages short; send progress updates; celebrate milestones |
| Negative word-of-mouth | Address critical feedback within 48h; consider NDA for Stage 1 |

---

## 9) Open Decisions

1. Whether Stage 1 testers should sign an NDA or informal agreement.
2. Exact invite code allocation per user in Stage 3 (5 vs 10 vs unlimited).
3. Whether to offer beta testers a permanent premium discount as thanks.
4. Whether to run a waitlist/pre-registration page during beta for public launch hype.
5. Whether to test Android demand signals during iOS beta (landing page, waitlist).
