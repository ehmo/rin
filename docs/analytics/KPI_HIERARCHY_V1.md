# KPI Hierarchy and Weekly Operating Metrics V1

## 1) Purpose

Define the north star metric, guardrail metrics, input metrics, and operating review cadence for Rin. Maps analytics events to business outcomes.

Companion docs:
- `docs/analytics/PRODUCT_ANALYTICS_EVENT_TAXONOMY_V1.md` (event definitions)
- `docs/plan/BETA_COHORT_STRATEGY_V1.md` (stage-specific targets)
- `docs/product/RIN_SCORE_V1.md` (score system)

---

## 2) North Star Metric

### MAU-V: Monthly Active Users with Value Received

**Definition**: Distinct users who received at least one *value event* in the trailing 30 days.

**Value events** (any one qualifies):
- `dedup_suggestion_shown` — dedup insight surfaced.
- `dedup_auto_merged` — automatic cleanup occurred.
- `score_updated` — daily score published.
- `contact_sync_completed` where `updated > 0` — contact data refreshed.
- `premium_feature_used` — premium value delivered.

**Why MAU-V**:
- Contacts apps are episodic, not daily-use. Monthly cadence matches real usage.
- Measures *delivered value*, not vanity opens. A user who never opens the app but whose contact list is being silently cleaned still counts.
- Prevents leaky bucket: if value delivery stops, MAU-V drops before churn becomes visible.
- High switching cost: users with value delivered have invested data (imported contacts, organized circles).

**Target progression**:

| Stage | MAU-V target | Notes |
|-------|-------------|-------|
| Stage 1 (50 users) | >80% | Core loop must deliver value to nearly everyone |
| Stage 2 (200 users) | >60% | Acceptable drop as cohort diversifies |
| Stage 3 (1,000 users) | >40% | Growth brings casual users |
| Public launch | >30% | Healthy for a utility app |

---

## 3) Guardrail Metrics

Guardrails prevent growth at the expense of quality. If any guardrail breaches its threshold, pause growth and investigate.

| Metric | Formula | Threshold | Action if breached |
|--------|---------|-----------|-------------------|
| **D30 retention** | % users returning within 30 days of signup | >15% | Investigate churn drivers |
| **Crash-free rate** | % sessions without crashes | >99.5% | Stop releases, fix stability |
| **Contact import success** | % imports that complete without error | >95% | Pause onboarding changes |
| **Dedup false positive rate** | % auto-merges that are wrong (user-reported) | <5% | Tighten confidence threshold |
| **Dispute resolution time** | P95 time from submission to resolution | <48h for P0/P1 | Scale dispute handling |
| **NPS** | Net Promoter Score from in-app survey | >25 | Deep-dive detractor feedback |

*D30 retention: Contacts apps are episodic; >15% D30 is the baseline, >20% is the stretch target.*

*NPS floor >25 (guardrail), Stage 2 target >30, Stage 3 target >40, post-launch steady-state >30 (broader audience dilutes early-adopter NPS).*

---

## 4) Input Metrics

Input metrics are the levers that drive MAU-V up. Organized by growth stage.

### 4.1 Acquisition Inputs

| Metric | Definition | Target |
|--------|-----------|--------|
| Invite send rate | Invites sent per active user per month | >1.5 |
| Invite conversion | % of invite recipients who complete onboarding | >30% |
| Onboarding completion | % who reach home screen from app launch | >80% |
| Contact import rate | % who grant contacts permission | >70% |

### 4.2 Activation Inputs

| Metric | Definition | Target |
|--------|-----------|--------|
| Time to first value | Minutes from app launch to first dedup/score view | <5 min |
| First action rate | % who take at least one action in first session | >50% |
| Magic moment rate | % who see dedup/cleanup cards within first session | >90% of importers |
| Circle setup rate | % who create at least 1 custom circle in first week | >20% |

### 4.3 Engagement Inputs

| Metric | Definition | Target |
|--------|-----------|--------|
| Score view frequency | Score views per MAU per month | >2 |
| Dedup resolution rate | % of shown suggestions resolved (merge or dismiss) | >70% |
| Circle adoption | % of users with >1 custom circle after 30 days | >25% |
| Contact management actions | Edits, merges, circle assignments per MAU per month | >3 |

### 4.4 Revenue Inputs

| Metric | Definition | Target |
|--------|-----------|--------|
| Paywall exposure rate | % of MAU who see paywall at least once | >20% |
| Premium trial start rate | % of paywall viewers who start trial | >5% |
| Premium conversion rate | % of trial users who convert to paid | >30% |
| Premium retention (monthly) | % of paid users who renew | >85% |

### 4.5 Virality Inputs

| Metric | Definition | Target |
|--------|-----------|--------|
| Viral coefficient (k) | New users per existing user per month | >0.5 |

*K >1.0 is aspirational for mature product; K >0.5 is the launch gate per Referral Network Effects analysis.*

| Organic install rate | % of installs with no invite attribution | Track only |
| Graph density | Average mutual connections per user | >3 |

---

## 5) Metric Tree

```
                        MAU-V (North Star)
                       /        |         \
                 Acquisition  Activation  Engagement
                 /    |         |    \        |     \
           Invites  Onboard  First   Magic  Score   Dedup
           sent     complete value   moment view    resolve
              |                |
         Invite              Import
         convert             rate
              \               /
               Viral coefficient
```

---

## 6) Operating Review Cadence

### 6.1 Daily Health Check (Automated)

Automated PostHog dashboard, reviewed in <2 minutes:

| Signal | Source | Alert threshold |
|--------|--------|----------------|
| Crash-free rate | Sentry | <99.5% |
| Import failure rate | PostHog | >5% |
| API error rate | Observability | >1% |
| Dispute queue depth (P0/P1) | Dispute dashboard | >0 unresolved >2h |
| Score batch completion | Score pipeline | Batch not completed by 06:00 UTC |

If any threshold breaches: founder investigates same day.

### 6.2 Weekly Deep Dive (30-Minute Review)

Every Monday, founder reviews:

**Growth section:**
- New users this week (count + trend).
- Onboarding completion rate (trend).
- Invite send rate and conversion.
- MAU-V (trailing 30 days, updated weekly).

**Product section:**
- Dedup suggestions shown vs resolved (resolution rate).
- Circle adoption (new circles created, members added).
- Score engagement (view frequency, component exploration).
- Contact sync health (success rate, sync frequency).

**Quality section:**
- Crash-free rate trend.
- Bugs filed vs resolved.
- Import failure breakdown by error type.
- Dedup false positive reports.

**Revenue section** (Stage 2+):
- Paywall views and conversion.
- Premium feature usage by feature.
- Subscription starts and cancellations.

### 6.3 Monthly North Star Review

First Monday of each month:
- MAU-V trend over trailing 3 months.
- Cohort retention curves (D1, D7, D30 by signup week).
- NPS trend and verbatim review.
- KPI target recalibration if needed.
- Guardrail threshold review.

---

## 7) Dashboard Requirements

### 7.1 PostHog Dashboards (Build Order)

| Dashboard | Build by | Contents |
|-----------|---------|----------|
| **Daily Health** | Stage 1 launch | Crash rate, import success, API errors, batch status |
| **Onboarding Funnel** | Stage 1 launch | S1→S12 conversion, permission rates, import completion |
| **Core Loop** | Stage 1 week 2 | Dedup shown/resolved, score views, first action rate |
| **Retention** | Stage 2 launch | D1/D7/D30 cohort curves, MAU-V trend |
| **Growth** | Stage 3 launch | Viral coefficient, invite funnel, organic vs invited |
| **Revenue** | Stage 2+ | Paywall funnel, premium usage, subscription health |

### 7.2 Weekly Report Template

Auto-generated from PostHog, sent to founder:

```
Week of [date] — Rin Weekly Metrics

NORTH STAR
  MAU-V: [n] ([+/-]% vs last week)

GUARDRAILS                      STATUS
  D30 retention: [n]%           [✅/⚠️/🔴]
  Crash-free rate: [n]%         [✅/⚠️/🔴]
  Import success: [n]%          [✅/⚠️/🔴]
  Dedup FP rate: [n]%           [✅/⚠️/🔴]
  NPS: [n]                      [✅/⚠️/🔴]

KEY MOVEMENTS
  [Top 3 metrics that moved most this week]

ACTIONS
  [Items requiring attention]
```

---

## 8) Stage-Specific Focus

### 8.1 Stage 1: Core Loop

Primary metrics to watch:
- Onboarding completion rate (target >80%).
- First value delivery time (<5 min).
- Dedup magic moment rate (>90% of importers).
- Crash-free rate (>99.5%).

Ignore during Stage 1:
- Retention (sample too small).
- Revenue (premium unlocked for all).
- Viral coefficient (closed cohort).

### 8.2 Stage 2: Retention

Primary metrics to watch:
- D7 retention (target >25%).
- D30 retention (target >15%).
- MAU-V (target >60%).
- NPS (target >30).
- Score engagement frequency.

Add during Stage 2:
- Premium A/B test conversion.
- Circle adoption tracking.

### 8.3 Stage 3: Growth

Primary metrics to watch:
- Viral coefficient (target >0.5).
- Invite conversion (target >30%).
- D30 retention (target >15%).
- Premium paywall exposure (target >20%).
- Infrastructure metrics (API p95, sync reliability).

Add during Stage 3:
- Full revenue dashboard.
- Cohort comparison (Stage 1 vs 2 vs 3 behavior).

---

## 9) Data Quality Rules

1. **Event validation**: All events must include required properties or be dropped (no partial events).
2. **Deduplication**: PostHog event dedup by `event_id` (UUID generated client-side).
3. **Clock skew**: Use server timestamp for server events, client timestamp for client events. PostHog reconciles.
4. **Backfill policy**: If instrumentation was missing, never backfill synthetic events. Add a `backfill_start_date` property to new events indicating when tracking began.
5. **Schema changes**: New properties can be added anytime. Property removal requires 30-day deprecation (stop sending, then remove from dashboards).

---

## 10) Open Decisions

1. Whether MAU-V should count background-only value (e.g., silent auto-merge while app is closed) or require at least one app open.
2. Whether to set individual guardrail thresholds per beta stage or use fixed thresholds throughout.
3. Whether the weekly report should be emailed or posted to a Slack/Discord channel.
4. Whether to add a "Team Health" section to the weekly review if/when team grows beyond solo founder.
5. Whether viral coefficient should be measured monthly or weekly (weekly is noisier but faster signal).
