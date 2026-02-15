# Post-Launch Stabilization Plan V1 (30/60/90 Days)

## 1) Purpose

Metric-driven stabilization plan for the first 90 days after public App Store launch. Each checkpoint has target metrics — if healthy, proceed; if not, extend stabilization.

Companion docs:
- `docs/analytics/KPI_HIERARCHY_V1.md` (metric definitions)
- `docs/plan/LAUNCH_READINESS_CHECKLIST_V1.md` (launch gate)
- `docs/plan/BETA_COHORT_STRATEGY_V1.md` (beta metrics baseline)

---

## 2) Stabilization Phases

```
Public Launch
    ↓
Phase 1: Stability (Days 1-30)
    ↓ checkpoint
Phase 2: Optimization (Days 31-60)
    ↓ checkpoint
Phase 3: Feature Readiness (Days 61-90)
    ↓ checkpoint
Begin Phase 2 Features
```

---

## 3) Phase 1: Stability (Days 1-30)

### 3.1 Focus

Ensure the app is stable, performant, and delivering core value under real-world load.

### 3.2 Rules

- **No new features** during Phase 1.
- **No score formula changes** for first 14 days.
- Hotfix releases only (crash fixes, critical bugs).
- Release cadence: as needed (no scheduled releases).

### 3.3 Target Metrics

| Metric | Target | Action if missed |
|--------|--------|-----------------|
| Crash-free rate | >99.5% | Stop all non-fix work. Prioritize stability. |
| API p95 latency | <300ms reads, <500ms writes | Profile and optimize hot paths. |
| Import success rate | >95% | Investigate failure patterns, add device-specific handling. |
| Onboarding completion | >75% | Review analytics funnel, fix drop-off points. |
| D1 retention | >30% | Investigate first-session experience quality. |
| P0 bugs open | 0 | Hotfix immediately. |
| Sentry error rate | <1% of sessions | Triage and fix top 5 errors. |

### 3.4 Daily Checks

- Review Sentry dashboard (new errors, error trends).
- Check API health (uptime, latency).
- Review App Store reviews (respond within 24h).
- Check import/sync success rates.

### 3.5 Phase 1 Checkpoint (Day 30)

**Proceed to Phase 2 when:**
- [ ] All target metrics met for at least 7 consecutive days.
- [ ] No P0/P1 bugs open.
- [ ] App Store rating >= 3.5 stars.
- [ ] No pending App Store compliance issues.

**Extend Phase 1 if:**
- Crash-free rate <99%.
- P0 bug open.
- App Store rating <3.0.

---

## 4) Phase 2: Optimization (Days 31-60)

### 4.1 Focus

Improve retention, optimize core flows, begin premium conversion experiments.

### 4.2 Rules

- Small improvements allowed (UX tweaks, copy changes, performance optimizations).
- A/B tests for paywall positioning.
- No major new features.
- Release cadence: weekly.

### 4.3 Target Metrics

| Metric | Target | Action if missed |
|--------|--------|-----------------|
| MAU-V (north star) | >30% of registered users | Investigate value delivery pipeline. |
| D7 retention | >20% | Improve first-week engagement hooks. |
| D30 retention | >15% | Analyze churn reasons, improve stickiness. |
| NPS | >30 | Deep-dive detractor feedback. |
| Dedup resolution rate | >60% | Improve dedup card UX if users ignore suggestions. |
| Score view frequency | >1.5x per MAU per month | Improve score visibility and notifications. |
| Paywall view rate | >15% of MAU | Optimize paywall trigger points. |
| Premium trial start | >3% of paywall viewers | Iterate paywall copy and design. |

### 4.4 Weekly Focus Areas

| Week | Focus |
|------|-------|
| 5 | Analyze D7 retention cohort. Identify top churn reasons. |
| 6 | Optimize onboarding based on funnel data. Test copy changes. |
| 7 | First paywall A/B test (trigger timing). |
| 8 | Score engagement improvements (notifications, in-app prompts). |

### 4.5 Phase 2 Checkpoint (Day 60)

**Proceed to Phase 3 when:**
- [ ] MAU-V >30%.
- [ ] D30 retention >15%.
- [ ] NPS >30.
- [ ] Premium trial start rate >3%.
- [ ] No P0/P1 bugs open.

**Extend Phase 2 if:**
- MAU-V <20%.
- D30 retention <10%.
- NPS <10.

---

## 5) Phase 3: Feature Readiness (Days 61-90)

### 5.1 Focus

Prepare for Phase 2 feature development. Validate growth mechanics. Establish sustainable operating rhythm.

### 5.2 Rules

- Begin Phase 2 feature planning (not building).
- Growth experiments (referral testing, ASO optimization).
- Infrastructure scaling assessment.
- Release cadence: weekly or biweekly.

### 5.3 Target Metrics

| Metric | Target | Action if missed |
|--------|--------|-----------------|
| MAU-V | >30% (stable or growing) | Focus on value delivery, defer new features. |
| Viral coefficient | >0.5 | Experiment with invite mechanics. |
| Premium conversion | >2% of MAU | Iterate pricing or paywall. |
| App Store rating | >4.0 | Address review feedback systematically. |
| Infrastructure headroom | >50% capacity remaining | Plan scaling before Phase 2 features add load. |
| Weekly operating review | Operational | Review process working reliably. |

### 5.4 Phase 3 Outputs

By Day 90, have:
- [ ] Phase 2 feature roadmap prioritized (based on user feedback and metrics).
- [ ] Infrastructure scaling plan (if growth projects demand).
- [ ] Sustainable operating rhythm (daily checks, weekly review, monthly north star review).
- [ ] Decision on whether to hire or continue solo.

### 5.5 Phase 3 Checkpoint (Day 90)

**Begin Phase 2 features when:**
- [ ] All Phase 2 checkpoint metrics sustained for 30 days.
- [ ] Phase 2 roadmap approved.
- [ ] No open stability concerns.

**Continue stabilization if:**
- Core metrics declining.
- Infrastructure concerns.
- Unresolved user feedback themes.

---

## 6) Rollback and Emergency Procedures

### 6.1 Critical Regression

If a release causes metric regression:

| Regression | Threshold | Action |
|-----------|-----------|--------|
| Crash rate spike | >1% of sessions | Immediate rollback to previous build |
| API outage | >5 minutes | Restart services, investigate root cause |
| Import failures | >10% | Disable import feature flag, hotfix |
| Score anomaly | Auto-rollback threshold (>5% users, >10 point change) | Auto-rollback triggers |
| App Store rejection | Any | Fix compliance issue, re-submit |

### 6.2 Feature Flags for Safe Rollout

Key features behind feature flags for Phase 1:
- Score visibility (can hide if formula issues).
- Dedup auto-merge (can disable if false positive spike).
- Push notifications (can disable if over-sending).
- Premium paywall (can disable entirely).

---

## 7) Open Decisions

1. Whether to target Phase 2 features for Day 91 or allow a buffer period.
2. Whether to hire before or during Phase 2 feature development.
3. Whether to expand beta cohort during stabilization (keep acquiring users) or pause.
4. Whether Day 90 checkpoint should be formal (written report) or informal (dashboard review).
