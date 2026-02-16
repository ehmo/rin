# Monetization Experiments and Success Criteria V1

## 1) Purpose

Define the full experiment matrix for optimizing Rin's premium monetization. Covers price testing, paywall placement, feature gating, trial configuration, annual discount optimization, and experiment governance. All experiments run through PostHog feature flags with clear go/no-go thresholds.

Companion docs:
- `docs/plan/IAP_SUBSCRIPTION_COMPLIANCE_V1.md` (pricing and StoreKit 2 implementation)
- `docs/architecture/EXPERIMENTATION_FRAMEWORK_V1.md` (A/B test process and ADR format)
- `docs/analytics/KPI_HIERARCHY_V1.md` (metric definitions and targets)
- `docs/analytics/PRODUCT_ANALYTICS_EVENT_TAXONOMY_V1.md` (event instrumentation)
- `docs/plan/BETA_COHORT_STRATEGY_V1.md` (staged rollout and premium beta strategy)

---

## 2) Baseline Assumptions

### 2.1 Current Configuration

| Parameter | Value |
|-----------|-------|
| Monthly price | $4.99/mo (`com.rin.premium.monthly`) |
| Annual price | $49.99/yr (`com.rin.premium.annual`) |
| Premium features | Who Viewed Me, Enrichment Alerts, Enhanced How Am I Stored |
| Free features | Dedup, score (full breakdown), circles, import/sync, shadow profiles |
| Analytics platform | PostHog Cloud (feature flags, experiments, funnels) |
| Identity | Split by principal ID for consistent assignment |

### 2.2 When Experiments Begin

Monetization experiments require Stage 3 traffic (1,000+ users) for statistical power. Stage 2 serves as instrumentation validation only (premium gated for 50% of new testers per Beta Cohort Strategy).

### 2.3 Key Analytics Events

All experiments measure outcomes through these events (from Event Taxonomy 5.8):
- `paywall_viewed` (trigger, feature_requested)
- `paywall_dismissed` (duration_ms)
- `subscription_started` (plan, price, trial)
- `subscription_cancelled` (plan, tenure_days, reason)
- `subscription_renewed` (plan, period_count)
- `premium_feature_used` (feature)

---

## 3) Experiment Matrix

### EXP-M01: Monthly Price Point Testing

**Hypothesis**: A higher monthly price does not materially reduce conversion rate and increases ARPU, because Rin's contact intelligence features have high perceived value once experienced.

| Parameter | Detail |
|-----------|--------|
| **Variants** | A: $4.99/mo (control) / B: $6.99/mo / C: $9.99/mo |
| **Traffic split** | 33/33/34 |
| **Assignment unit** | Principal ID |
| **Implementation** | PostHog multivariate flag `price_monthly_test`. StoreKit products configured for all three price points in App Store Connect. Paywall reads active variant and displays corresponding `Product.displayPrice`. |
| **Duration** | Minimum 28 days (2 renewal cycles for monthly) |
| **Sample size** | 300 users per variant (900 total exposed to paywall) |

**Primary metrics**:

| Metric | Definition | Go threshold |
|--------|-----------|-------------|
| ARPU (28-day) | Total revenue / total users in variant | Must increase vs control |
| Conversion rate | `subscription_started` / `paywall_viewed` | Must not drop >30% vs control |
| LTV (projected 90-day) | ARPU * projected retention rate | Must increase vs control |

**Guardrail metrics**:

| Metric | Threshold | Kill if breached |
|--------|-----------|-----------------|
| D30 retention | Must not drop >5pp vs control | Yes |
| NPS | Must not drop >10 points vs control | Yes |
| Paywall dismiss rate | Must not increase >15pp vs control | Investigate |

**Decision framework**:
- Ship higher price if ARPU increases and conversion drop is <30%.
- If $6.99 and $9.99 both pass, ship whichever maximizes LTV.
- Kill if any guardrail breaches threshold.

---

### EXP-M02: Annual Discount Depth Testing

**Hypothesis**: Deeper annual discounts increase annual plan adoption rate and improve LTV by reducing churn (annual subscribers have lower churn than monthly).

| Parameter | Detail |
|-----------|--------|
| **Variants** | A: $49.99/yr = ~2 months free (control) / B: $39.99/yr = ~4 months free / C: $59.99/yr = ~17% save |
| **Traffic split** | 33/33/34 |
| **Prerequisite** | Run after EXP-M01 concludes (use winning monthly price as reference) |
| **Duration** | Minimum 42 days (to observe annual selection behavior, not actual renewal) |
| **Sample size** | 250 users per variant who reach paywall |

**Primary metrics**:

| Metric | Definition | Go threshold |
|--------|-----------|-------------|
| Annual plan selection rate | % of subscribers choosing annual | Must increase vs control |
| ARPU (per subscriber) | Average revenue per subscriber at signup | Track tradeoff |
| Projected annual LTV | Plan price * projected renewal rate | Must increase vs control |

**Secondary metrics**:
- Annual:monthly subscriber ratio.
- Time from paywall view to subscription (decision speed).

**Decision framework**:
- Ship the price that maximizes projected annual LTV.
- If $39.99 cannibalized revenue too much (ARPU drops >20%), revert to control.
- If $59.99 shows negligible uptake improvement, keep control (simpler).

---

### EXP-M03: Annual Offer Timing

**Hypothesis**: Surfacing the annual plan after a user has been on monthly for 2+ months (vs at initial signup) increases annual conversion because the user has established habit and proven value.

| Parameter | Detail |
|-----------|--------|
| **Variants** | A: Show annual at signup paywall (control) / B: Show monthly-only at signup; surface annual upgrade offer after 60 days of active monthly subscription |
| **Traffic split** | 50/50 |
| **Duration** | 90 days minimum (to observe the 60-day delayed offer in variant B) |
| **Sample size** | 200 monthly subscribers per variant |

**Primary metrics**:

| Metric | Definition | Go threshold |
|--------|-----------|-------------|
| Annual subscriber % at 90 days | % of paying users on annual plan | Must increase vs control |
| Total revenue per user at 90 days | Sum of all payments in 90-day window | Must not decrease |
| Monthly churn before annual offer (B only) | % of monthly subs lost before 60-day mark | Must be <30% |

**Decision framework**:
- Ship variant B only if it increases annual adoption without losing revenue in the 90-day window.
- If monthly churn before the annual offer is >30%, the delayed approach loses too many users.

---

### EXP-M04: Paywall Placement -- Hard vs Soft

**Hypothesis**: A soft paywall (gate specific premium features but keep core app fully free) outperforms a hard time-limited paywall (full access for N days, then gate everything premium) in both conversion and retention.

| Parameter | Detail |
|-----------|--------|
| **Variants** | A: Soft paywall on premium features only (control, current plan) / B: Hard paywall after 7-day full-access trial |
| **Traffic split** | 50/50 |
| **Duration** | 35 days minimum (7-day trial + 28 days post-trial observation) |
| **Sample size** | 400 users per variant |

**Primary metrics**:

| Metric | Definition | Go threshold |
|--------|-----------|-------------|
| Trial-to-paid conversion | `subscription_started` / users who reached paywall | Must increase vs control |
| D30 retention (all users) | % of variant users active at D30 | Must not drop >5pp |
| ARPU (30-day, all users) | Revenue / total users in variant | Must increase vs control |

**Guardrail metrics**:

| Metric | Threshold |
|--------|-----------|
| Onboarding completion | Must not drop >5pp |
| App uninstall rate | Must not increase >10% |
| NPS | Must not drop >10 points |

**Decision framework**:
- Hard paywall ships only if conversion increase outweighs any retention loss.
- If retention drops >5pp, hard paywall is killed regardless of conversion.

---

### EXP-M05: Paywall Trigger Points

**Hypothesis**: Showing the paywall at high-value moments (after the user experiences a "wow" moment) converts better than showing it at a static feature gate.

| Parameter | Detail |
|-----------|--------|
| **Variants** | A: Paywall on premium feature tap only (control) / B: Paywall after 3rd dedup resolution (value-proven moment) / C: Paywall after 2nd score view (engagement signal) / D: Paywall after circle limit reached (need-based) |
| **Traffic split** | 25/25/25/25 |
| **Duration** | 21 days minimum |
| **Sample size** | 200 users per variant |

**Primary metrics**:

| Metric | Definition | Go threshold |
|--------|-----------|-------------|
| Paywall view-to-trial rate | `subscription_started` / `paywall_viewed` | Best variant wins if statistically significant |
| Time to first paywall view | Median time from install to first `paywall_viewed` | Track (faster is not always better) |
| Paywall fatigue (dismiss rate) | `paywall_dismissed` / `paywall_viewed` | Must not exceed 90% |

**Guardrail metrics**:

| Metric | Threshold |
|--------|-----------|
| D7 retention | Must not drop >3pp vs control |
| Core action rate (dedup, circle) | Must not drop >10% vs control |

**Decision framework**:
- Ship the variant with highest view-to-trial rate, provided guardrails hold.
- Can combine winning trigger with control (add a trigger, don't replace).
- Still respect the existing rule: max one paywall per session.

---

### EXP-M06: Free Actions Before Paywall

**Hypothesis**: Allowing users a set number of free premium actions before gating increases perceived value and conversion compared to immediate gating.

| Parameter | Detail |
|-----------|--------|
| **Variants** | A: Immediate gate on premium features (control) / B: 3 free premium actions, then gate / C: 5 free premium actions, then gate |
| **Traffic split** | 33/33/34 |
| **Duration** | 21 days minimum |
| **Sample size** | 250 users per variant |

**Premium actions counted**: Who Viewed Me views, How Am I Stored views, Enrichment Alert taps. Each action decrements the user's free allocation (tracked via PostHog person property `free_premium_actions_remaining`).

**Primary metrics**:

| Metric | Definition | Go threshold |
|--------|-----------|-------------|
| Conversion rate | `subscription_started` / users who exhausted free actions | Must exceed control by >20% relative |
| Time to conversion | Median days from install to `subscription_started` | Track (not a hard gate) |
| Feature exploration depth | Distinct premium features tried during free window | Track |

**Decision framework**:
- Ship if conversion rate exceeds control by >20% relative.
- If users churn after free actions run out without converting, this signals the premium features need strengthening (not a paywall problem).

---

### EXP-M07: Paywall Messaging Variants

**Hypothesis**: Paywall copy significantly impacts conversion rate. Value-focused messaging outperforms FOMO and social proof for a utility app.

| Parameter | Detail |
|-----------|--------|
| **Variants** | A: Value-focused ("Unlock deeper insights into your network") / B: FOMO ("12 people viewed your profile this week -- see who") / C: Social proof ("Join 500+ users managing their network smarter") / D: Quantified value ("Users save 2 hours/month on contact cleanup") |
| **Traffic split** | 25/25/25/25 |
| **Duration** | 14 days minimum |
| **Sample size** | 200 users per variant |

**Primary metrics**:

| Metric | Definition | Go threshold |
|--------|-----------|-------------|
| Paywall-to-subscribe rate | `subscription_started` / `paywall_viewed` | Best variant wins |
| Paywall dwell time | `paywall_dismissed.duration_ms` median | Longer = more consideration (track) |
| Plan selection (annual vs monthly) | % choosing annual plan | Track |

**Decision framework**:
- Ship winning copy variant.
- Can iterate on winner with further refinements.
- If FOMO wins, validate NPS has not dropped (dark pattern risk).

---

### EXP-M08: Feature Gating -- Which Features Drive Conversion

**Hypothesis**: Gating certain features drives more conversion than others. Identifying the highest-converting gate informs what to keep free vs premium.

| Parameter | Detail |
|-----------|--------|
| **Variants** | A: Gate only Who Viewed Me + Enrichment Alerts + How Am I Stored (control, current plan) / B: Also gate unlimited circles (free tier = 3 circles) / C: Also gate score component breakdown (free tier = overall score only) / D: Also gate priority dedup (free tier = manual dedup only, no auto-merge) |
| **Traffic split** | 25/25/25/25 |
| **Duration** | 28 days minimum |
| **Sample size** | 300 users per variant |

**Primary metrics**:

| Metric | Definition | Go threshold |
|--------|-----------|-------------|
| Conversion rate | `subscription_started` / `paywall_viewed` | Variant must beat control by >15% relative |
| Revenue per user (28-day) | Total revenue / users in variant | Must increase vs control |
| Premium feature usage post-conversion | `premium_feature_used` events per subscriber per week | Track (validates feature value) |

**Guardrail metrics**:

| Metric | Threshold |
|--------|-----------|
| D30 retention (all users, including free) | Must not drop >5pp vs control |
| NPS (free users in variant) | Must not drop >15 points vs control |
| Core loop completion (dedup + score) | Must not drop >10% |

**Decision framework**:
- Ship additional gating only if conversion lift exceeds retention loss.
- Critical: gating score breakdown or dedup may damage the core value prop. NPS guardrail is essential.
- If variant D (gate dedup) harms retention, do not ship -- dedup is the magic moment.

---

### EXP-M09: Progressive Reveal vs Immediate Gating

**Hypothesis**: Progressively revealing premium features (showing blurred/teaser content before gating) converts better than hard feature locks because it demonstrates value before asking for payment.

| Parameter | Detail |
|-----------|--------|
| **Variants** | A: Hard gate -- tap premium feature, see paywall immediately (control) / B: Progressive reveal -- show blurred "Who Viewed Me" list with count visible, tap to unlock via paywall |
| **Traffic split** | 50/50 |
| **Duration** | 21 days minimum |
| **Sample size** | 300 users per variant |

**Primary metrics**:

| Metric | Definition | Go threshold |
|--------|-----------|-------------|
| Paywall conversion rate | `subscription_started` / `paywall_viewed` | Must increase >10% relative vs control |
| Paywall engagement rate | % of users who tap blurred content (B) vs % who tap locked feature (A) | Track (B should be higher) |
| Feature exploration rate | % of users who discover 2+ premium features | Track |

**Decision framework**:
- Ship progressive reveal if conversion increases without adding engineering complexity disproportionate to the lift.
- Extend to all gated features if proven on Who Viewed Me.

---

### EXP-M10: Free Tier Circle Limits

**Hypothesis**: The number of free circles affects conversion. Too few frustrates users (churn); too many removes incentive to upgrade.

| Parameter | Detail |
|-----------|--------|
| **Variants** | A: Unlimited circles free (control, current plan) / B: 3 circles free, then paywall / C: 5 circles free, then paywall / D: 10 circles free, then paywall |
| **Traffic split** | 25/25/25/25 |
| **Prerequisite** | Only run if EXP-M08 shows circle gating has conversion potential |
| **Duration** | 28 days minimum |
| **Sample size** | 250 users per variant |

**Primary metrics**:

| Metric | Definition | Go threshold |
|--------|-----------|-------------|
| Conversion rate | `subscription_started` from circle paywall trigger | Track per variant |
| Circle adoption (free tier) | % of free users who create circles | Must not drop >20% vs control |
| D30 retention | % returning at 30 days | Must not drop >3pp |

**Decision framework**:
- Ship the limit that maximizes conversion without materially harming circle adoption or retention.
- If all gated variants harm retention >3pp, keep circles unlimited and focus gating elsewhere.

---

### EXP-M11: Trial Length Testing

**Hypothesis**: Trial length significantly impacts conversion-to-paid rate. Shorter trials create urgency but may not allow enough value discovery; longer trials build habit but reduce urgency.

| Parameter | Detail |
|-----------|--------|
| **Variants** | A: 7-day trial (control) / B: 14-day trial / C: 30-day trial |
| **Traffic split** | 33/33/34 |
| **Duration** | 60 days minimum (to observe 30-day trial conversion in variant C) |
| **Sample size** | 300 users per variant |

**Primary metrics**:

| Metric | Definition | Go threshold |
|--------|-----------|-------------|
| Trial start rate | `subscription_started (trial=true)` / `paywall_viewed` | Track |
| Trial-to-paid conversion | `subscription_renewed (period_count=1)` / `subscription_started (trial=true)` | Best variant wins |
| Time-to-cancel during trial | Median days from trial start to `subscription_cancelled` | Track |
| D60 ARPU | Revenue per exposed user at 60 days | Must be highest for winning variant |

**Guardrail metrics**:

| Metric | Threshold |
|--------|-----------|
| D30 retention | Must not drop >3pp |
| Premium feature engagement during trial | Must show increasing usage over trial period |

**Decision framework**:
- Optimize for trial-to-paid conversion rate, not trial start rate. Getting users into trials that don't convert is worse than fewer trials that convert well.
- If 30-day trial converts best but D60 ARPU is lower (delayed revenue), model the break-even point.

---

### EXP-M12: Trial -- Card Upfront vs No Card

**Hypothesis**: Requiring payment method upfront reduces trial starts but increases trial-to-paid conversion (self-selection of intent). Net effect on revenue is the question.

| Parameter | Detail |
|-----------|--------|
| **Variants** | A: No card required for trial (StoreKit default, control) / B: Card required upfront (auto-converts unless cancelled) |
| **Traffic split** | 50/50 |
| **Note** | StoreKit 2 trials with auto-renewal inherently require a payment method. This experiment tests whether to offer a "free preview" (variant A: limited time access with no payment method, manual conversion required) vs standard StoreKit trial (variant B). |
| **Duration** | 35 days minimum |
| **Sample size** | 300 users per variant |

**Primary metrics**:

| Metric | Definition | Go threshold |
|--------|-----------|-------------|
| Trial start rate | Trials started / paywall views | Track |
| Trial-to-paid conversion | Paid subscribers / trial starters | Track |
| Net conversion (combined) | Paid subscribers / paywall views | Best variant wins |
| D30 ARPU | Revenue per exposed user at 30 days | Must be highest for winner |

**Decision framework**:
- Optimize for net conversion (trial start rate * trial-to-paid rate).
- Card-upfront typically wins on net conversion for utility apps. Validate this assumption.

---

### EXP-M13: Trial Feature Set

**Hypothesis**: Offering the full premium experience during trial (vs a limited preview) creates stronger habit formation and converts better, despite revealing all value upfront.

| Parameter | Detail |
|-----------|--------|
| **Variants** | A: Full premium during trial (all 3 premium features, control) / B: Partial premium (Who Viewed Me only; other features shown as "available after subscribing") |
| **Traffic split** | 50/50 |
| **Duration** | 28 days minimum |
| **Sample size** | 250 users per variant |

**Primary metrics**:

| Metric | Definition | Go threshold |
|--------|-----------|-------------|
| Trial-to-paid conversion | Paid subscribers / trial starters | Best variant wins |
| Premium feature usage during trial | Distinct features used per trial user | Track |
| Post-conversion feature usage | `premium_feature_used` per week after conversion | Track (validates long-term value) |

**Decision framework**:
- Ship full premium trial if it converts better (expected).
- If partial trial converts equally, ship partial (reduces perceived loss at trial end for non-converters, better for retention).

---

### EXP-M14: Regional Pricing Strategy

**Hypothesis**: Localizing prices to purchasing power parity (PPP) increases conversion in lower-income regions without significantly cannibalizing revenue in higher-income regions.

| Parameter | Detail |
|-----------|--------|
| **Tiers** | Tier 1: US/UK/EU/AU ($4.99 baseline) / Tier 2: LATAM/Eastern Europe/SE Asia ($2.99 equivalent) / Tier 3: India/Africa ($1.99 equivalent) |
| **Implementation** | Use App Store Connect price tiers. StoreKit `Product.displayPrice` handles localization automatically. No feature flags needed -- this is an App Store Connect configuration. |
| **Duration** | 90 days (slower volume in Tier 2/3 regions requires longer observation) |
| **Sample size** | 100 subscribers per tier minimum |

**Primary metrics**:

| Metric | Definition | Go threshold |
|--------|-----------|-------------|
| Conversion rate per tier | `subscription_started` / `paywall_viewed` per region | Tier 2/3 must exceed Tier 1 by >50% relative |
| Total revenue impact | Sum of all regional revenue vs uniform pricing counterfactual | Must be net positive |
| ARPU per region | Revenue / users per region | Track (expected lower in Tier 2/3) |

**Decision framework**:
- Ship regional pricing if total revenue increases (more subscribers at lower prices > fewer subscribers at higher prices).
- Monitor for VPN abuse (users in Tier 1 countries accessing Tier 2/3 pricing). If >5% of Tier 2/3 subscribers are VPN users, add verification.

---

## 4) Experiment Governance

### 4.1 Experiment Calendar and Sequencing

**Maximum concurrent monetization experiments**: 2.

**Sequencing constraints**:

```
Phase 1 (Stage 3, weeks 1-6):
  EXP-M01 (price testing)         ← runs first, foundational
  EXP-M07 (paywall messaging)     ← independent, can run concurrently

Phase 2 (Stage 3, weeks 5-12):
  EXP-M02 (annual discount)       ← depends on M01 winner
  EXP-M05 (paywall triggers)      ← independent of M02

Phase 3 (Stage 3, weeks 10-16):
  EXP-M04 (hard vs soft paywall)  ← depends on M05 learnings
  EXP-M08 (feature gating)        ← independent of M04

Phase 4 (pre-launch, weeks 14-22):
  EXP-M11 (trial length)          ← depends on M04 decision
  EXP-M06 (free actions)          ← can run concurrent

Phase 5 (post-launch, weeks 20+):
  EXP-M03 (annual timing)         ← requires 90 days, run post-launch
  EXP-M14 (regional pricing)      ← requires regional traffic
  EXP-M09 (progressive reveal)    ← polish optimization
  EXP-M10 (circle limits)         ← conditional on M08 result
  EXP-M12 (card upfront)          ← trial optimization
  EXP-M13 (trial feature set)     ← trial optimization
```

### 4.2 Statistical Standards

| Parameter | Standard |
|-----------|----------|
| Significance threshold | 95% confidence (p < 0.05) |
| Power | 80% minimum |
| Minimum detectable effect | 15% relative change in primary metric |
| Peeking policy | No peeking before minimum duration. Use PostHog sequential testing if available. |
| Multiple comparison correction | Bonferroni correction for multivariate tests (3+ variants) |

### 4.3 Sample Size Calculator

For a two-variant test with 50/50 split:

| Baseline conversion rate | MDE (relative) | Sample per variant | Total needed |
|--------------------------|-----------------|-------------------|-------------|
| 5% (paywall conversion) | 15% | ~17,000 | ~34,000 |
| 5% (paywall conversion) | 30% | ~4,500 | ~9,000 |
| 5% (paywall conversion) | 50% | ~1,700 | ~3,400 |
| 20% (trial-to-paid) | 15% | ~3,500 | ~7,000 |
| 20% (trial-to-paid) | 30% | ~900 | ~1,800 |
| 50% (annual selection) | 15% | ~1,200 | ~2,400 |

**Reality check for Rin at Stage 3 (1,000 users)**:
- With 20% paywall exposure rate: ~200 users see paywall per month.
- At 200 users/month, a 50/50 test detecting 30% relative lift on 5% baseline needs ~9,000 total paywall views = ~45 months. This is not feasible.
- **Practical minimum**: Detect 50% relative lift (large effects only) with 1,700 total = ~8.5 months. Still long.
- **Implication**: At Stage 3 scale, only test for large effects (>50% relative). Smaller optimizations wait for post-launch scale.
- Post-launch at 10,000+ users with 20% paywall exposure: ~2,000 paywall views/month. 30% MDE test completes in ~4.5 months. Still slow. Monetization experiments require patience.

### 4.4 Guardrail Metrics (Universal)

Every monetization experiment must monitor these guardrails. Breach any guardrail = pause and investigate.

| Guardrail | Threshold | Measurement |
|-----------|-----------|-------------|
| D30 retention (all users) | Must not drop >5 percentage points vs control | PostHog retention cohort |
| NPS | Must not drop >10 points vs control | In-app NPS survey at D14 |
| Onboarding completion | Must not drop >5pp | PostHog funnel |
| Crash-free rate | >99.5% | Sentry |
| Core action rate (dedup resolve + score view) | Must not drop >10% | PostHog |
| App Store rating | Must not drop below 4.0 | App Store Connect |
| Support ticket volume | Must not increase >50% | Support dashboard |

### 4.5 Decision Framework

For each completed experiment, apply this decision tree:

```
1. Did the experiment run for minimum duration?
   NO → Continue running.
   YES ↓

2. Is the primary metric statistically significant (p < 0.05)?
   NO → Insufficient data. Options:
        a) Extend duration if approaching significance (p < 0.10)
        b) Declare inconclusive and revert to control
        c) Redesign with larger effect size target
   YES ↓

3. Are all guardrail metrics within thresholds?
   NO → Do not ship. Investigate guardrail breach.
        If fixable: iterate and re-run.
        If fundamental: kill experiment.
   YES ↓

4. Is the effect size practically significant (worth the complexity)?
   NO → Revert to control. Log learnings.
   YES ↓

5. SHIP the winning variant.
   - Document result in experiment file (EXP-M##.md)
   - Update IAP_SUBSCRIPTION_COMPLIANCE_V1.md if pricing changes
   - Remove feature flag (hardcode winner)
   - Update PostHog dashboards
```

### 4.6 Experiment Documentation

Each experiment gets a file at `docs/experiments/EXP-M{number}.md` following the template from Experimentation Framework V1. Additionally track:

```markdown
## EXP-M##: [Name]
- **Hypothesis**: [If we X, then Y because Z]
- **Primary metric**: [Metric to decide on]
- **Variants**: [Control vs treatments]
- **Traffic split**: [%/%]
- **Sample size target**: [N per variant]
- **Minimum duration**: [Days]
- **PostHog flag name**: [flag_name]
- **Status**: Planning / Running / Analyzing / Complete
- **Start date**: YYYY-MM-DD
- **End date**: YYYY-MM-DD
- **Result**: [Winner + confidence + effect size]
- **Guardrail status**: [All green / breach details]
- **Decision**: Ship / Iterate / Kill
- **Learnings**: [What we learned regardless of outcome]
```

### 4.7 Kill Criteria

Immediately stop any experiment if:
- Crash-free rate drops below 99% (data corruption or app instability).
- Any user reports incorrect billing or double-charging.
- App Store rejects an update due to experiment-related compliance issue.
- D7 retention drops >10pp in any variant (severe harm).
- Support ticket volume doubles within first week.

---

## 5) Success Criteria Per Experiment Type

### 5.1 Price Testing (EXP-M01, M02, M14)

| Outcome | Criteria | Action |
|---------|----------|--------|
| **Ship** | ARPU increases by >10% with conversion drop <30% relative | Update App Store Connect pricing |
| **Iterate** | ARPU increases but guardrail breach is minor and addressable | Adjust variant and re-run |
| **Kill** | Conversion drops >50% relative or any guardrail hard breach | Revert to control price |

### 5.2 Paywall Placement (EXP-M04, M05, M06, M07)

| Outcome | Criteria | Action |
|---------|----------|--------|
| **Ship** | Conversion rate increases >15% relative with retention intact | Update paywall trigger logic |
| **Iterate** | Promising signal but insufficient sample size or mixed guardrail results | Extend or refine |
| **Kill** | D30 retention drops >5pp or NPS drops >15 points | Revert to control placement |

### 5.3 Feature Gating (EXP-M08, M09, M10)

| Outcome | Criteria | Action |
|---------|----------|--------|
| **Ship** | Gating increases conversion >15% relative without harming core loop metrics | Update feature gate configuration |
| **Iterate** | Conversion increases but free-tier NPS drops >10 points | Adjust gate threshold (e.g., more free actions) |
| **Kill** | Core loop engagement (dedup, score) drops >10% or D30 retention drops >5pp | Keep feature free |

### 5.4 Trial Configuration (EXP-M11, M12, M13)

| Outcome | Criteria | Action |
|---------|----------|--------|
| **Ship** | Trial-to-paid conversion increases >20% relative | Update StoreKit trial configuration |
| **Iterate** | Trial starts increase but conversion is flat | Adjust trial content or length |
| **Kill** | Trial-to-paid conversion drops >20% relative or trial abusers detected at scale | Revert to control trial |

### 5.5 Annual Discount (EXP-M02, M03)

| Outcome | Criteria | Action |
|---------|----------|--------|
| **Ship** | Annual plan adoption increases >10pp and projected LTV improves | Update annual pricing |
| **Iterate** | Annual adoption increases but total revenue per user decreases | Adjust discount depth |
| **Kill** | Discount cannibalizes revenue (lower ARPU) without sufficient volume increase | Keep current annual pricing |

---

## 6) Revenue Projections and Sensitivity Analysis

### 6.1 Baseline Revenue Model

At public launch (assume 5,000 MAU):

| Parameter | Conservative | Base | Optimistic |
|-----------|-------------|------|-----------|
| Paywall exposure rate | 15% | 20% | 30% |
| Paywall-to-trial rate | 3% | 5% | 8% |
| Trial-to-paid rate | 20% | 30% | 40% |
| Monthly price | $4.99 | $4.99 | $6.99 |
| Annual plan adoption | 30% | 40% | 50% |
| Monthly churn | 15% | 10% | 7% |

**Base case monthly revenue at steady state**:
- 5,000 MAU * 20% paywall * 5% trial * 30% convert = 15 new subscribers/month.
- At steady state (new = churn): ~150 active subscribers.
- Revenue: ~150 * blended $5.50/mo = ~$825/month MRR.

**What experiments must improve**:
- Moving conversion from 5% to 8% = 24 new subs/month = ~240 active = ~$1,320/month (60% increase).
- Moving price from $4.99 to $6.99 with 20% conversion loss = ~$1,035/month (25% increase).
- Combined improvements are multiplicative.

### 6.2 Experiment Impact Sizing

| Experiment | Expected revenue impact | Priority |
|-----------|----------------------|----------|
| EXP-M01 (price) | High -- directly multiplies all revenue | P1 |
| EXP-M05 (triggers) | High -- increases paywall exposure | P1 |
| EXP-M08 (feature gating) | High -- increases conversion rate | P1 |
| EXP-M11 (trial length) | Medium -- optimizes funnel step | P2 |
| EXP-M07 (messaging) | Medium -- incremental conversion lift | P2 |
| EXP-M02 (annual discount) | Medium -- improves LTV via retention | P2 |
| EXP-M09 (progressive reveal) | Low-Medium -- UX polish | P3 |
| EXP-M14 (regional pricing) | Low until international scale | P3 |
| EXP-M03 (annual timing) | Low -- long feedback cycle | P3 |
| EXP-M10 (circle limits) | Conditional on M08 | P3 |

---

## 7) PostHog Implementation Notes

### 7.1 Feature Flag Naming Convention

`monetization_{experiment_id}_{short_name}`

Examples:
- `monetization_m01_price_monthly`
- `monetization_m07_paywall_copy`
- `monetization_m11_trial_length`

### 7.2 Event Properties for Experiments

Add to all monetization events when an experiment is active:

| Property | Type | Description |
|----------|------|-------------|
| `experiment_id` | string | `EXP-M01`, `EXP-M02`, etc. |
| `experiment_variant` | string | `control`, `variant_b`, `variant_c` |
| `experiment_flag` | string | PostHog flag name |

### 7.3 Experiment Dashboards

Build one PostHog dashboard per active experiment:

- **Funnel**: paywall_viewed -> subscription_started -> subscription_renewed, split by variant.
- **Retention**: D7/D30 cohort curves, split by variant.
- **Revenue**: ARPU trend, split by variant.
- **Guardrails**: All guardrail metrics on a single row, with threshold lines.

### 7.4 Holdout Group

Reserve 10% of users as a global control (no monetization experiments applied). This holdout enables measuring the cumulative effect of all shipped experiment winners vs the original experience. Implement as PostHog feature flag `monetization_holdout` (10% in holdout, 90% eligible for experiments).

---

## 8) Compliance Considerations

### 8.1 App Store Rules for Price Testing

- All price points must be configured as valid products in App Store Connect.
- Users must see accurate, localized pricing via `Product.displayPrice` (never hardcoded).
- Price changes for existing subscribers require App Store Connect's "Manage Subscription Price Changes" flow (subscribers must consent).
- New subscribers can be assigned to different price variants via feature flags.

### 8.2 Trial Disclosure

- Per App Store guidelines and IAP_SUBSCRIPTION_COMPLIANCE_V1.md: "Free trial converts to paid subscription after [N] days" must be displayed.
- For trial length experiments, the disclosure must dynamically reflect the assigned variant's trial length.
- Auto-renewal disclosure required regardless of trial variant.

### 8.3 No Dark Patterns

- Paywall messaging experiments must not use deceptive language.
- FOMO variant (EXP-M07 variant B) must use real data, not fabricated numbers.
- All paywalls must remain dismissible.
- No buried cancellation flows.

---

## 9) Open Decisions

1. Whether to offer a lifetime purchase option alongside subscriptions (complicates LTV modeling but may appeal to privacy-conscious users who distrust subscriptions).
2. Whether beta testers receive a permanent discount or limited-time loyalty pricing.
3. Whether to implement introductory offers ($0.99 first month) as a separate experiment or test within EXP-M01.
4. Whether the 10% holdout group is viable at Stage 3 scale (reduces experiment traffic by 10%).
5. Whether to use PostHog's built-in experiment analysis or export to a separate tool for revenue analysis that PostHog does not natively support.
6. Whether paywall A/B tests require separate App Store review (likely not, since the app binary is the same and only flag-driven content changes).
7. Exact threshold for declaring an experiment "inconclusive" -- current guidance is p > 0.10 after maximum duration, but this may be too conservative for early-stage.
