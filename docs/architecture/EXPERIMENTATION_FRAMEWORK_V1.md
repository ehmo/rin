# Experimentation Framework V1

## 1) Purpose

Minimal viable experimentation process for a solo founder. PostHog feature flags for A/B tests. Lightweight decision register (ADR format).

Companion docs:
- `docs/analytics/PRODUCT_ANALYTICS_EVENT_TAXONOMY_V1.md` (event tracking)
- `docs/analytics/KPI_HIERARCHY_V1.md` (metrics to measure)

---

## 2) A/B Testing via PostHog Feature Flags

### 2.1 Setup

- PostHog Cloud feature flags (included in free tier).
- Split by user ID (principal ID) for consistent assignment.
- No custom experimentation framework — PostHog handles it.

### 2.2 Experiment Template

For each experiment, document in a markdown file (`docs/experiments/EXP-{number}.md`):

```markdown
## EXP-001: [Name]
- **Hypothesis**: [If we X, then Y because Z]
- **Metric**: [Primary metric to measure]
- **Variant A**: [Control — current behavior]
- **Variant B**: [Treatment — new behavior]
- **Traffic split**: [50/50 unless specific reason]
- **Sample size**: [Minimum users needed for significance]
- **Duration**: [Minimum days to run]
- **Status**: [Planning / Running / Analyzing / Complete]
- **Result**: [Winner + confidence level]
- **Decision**: [Ship variant A/B or iterate]
```

### 2.3 Sample Size Guidelines

For a contact management app with episodic usage:

| Metric type | Minimum sample per variant | Minimum duration |
|-------------|---------------------------|-----------------|
| Conversion (paywall) | 200 users | 14 days |
| Retention (D7) | 500 users | 21 days |
| Engagement (actions/user) | 100 users | 7 days |

Use PostHog's built-in significance calculator. Don't peek at results before minimum duration.

### 2.4 Planned Experiments (Stage 2+)

| # | Name | Hypothesis |
|---|------|-----------|
| EXP-001 | Paywall trigger timing | Earlier paywall exposure (after first dedup) increases trial starts without harming retention |
| EXP-002 | Annual plan emphasis | Highlighting annual plan savings increases annual:monthly ratio |
| EXP-003 | Score notification frequency | Weekly score notifications (vs daily) improve D30 retention |
| EXP-004 | Onboarding circle setup | Making circle setup optional (vs required) improves onboarding completion |

---

## 3) Decision Register (ADR Format)

### 3.1 ADR Template

One-page decision record. Store in `docs/decisions/ADR-{number}.md`:

```markdown
# ADR-{number}: [Title]

**Status**: Proposed | Accepted | Superseded by ADR-{n}
**Date**: YYYY-MM-DD
**Context**: [1-2 sentences on what prompted this decision]
**Decision**: [What we decided]
**Rationale**: [Why this over alternatives]
**Alternatives considered**: [Bullet list of other options]
**Consequences**: [What this enables and constrains]
```

### 3.2 When to Write an ADR

- Technology choice (ConnectRPC over REST, PostHog over Mixpanel).
- Architecture pattern (MVVM+Coordinator, event sourcing).
- Product decision with tradeoffs (pricing, feature gating).
- Policy decision (data retention periods, abuse thresholds).

Don't write ADRs for:
- Obvious choices (use Swift for iOS).
- Reversible decisions (button color, copy changes).
- Implementation details (variable naming, code structure).

### 3.3 Existing Decisions to Backfill

| ADR # | Decision | Document |
|-------|----------|----------|
| ADR-001 | MVVM + Coordinator for iOS | `IOS_APP_ARCHITECTURE_V1.md` |
| ADR-002 | ConnectRPC for API contract | `IOS_API_CLIENT_V1.md` |
| ADR-003 | PostHog Cloud for analytics | `PRODUCT_ANALYTICS_EVENT_TAXONOMY_V1.md` |
| ADR-004 | Cloudflare + Hetzner for hosting | `CLOUD_PROVIDER_STRATEGY_V1.md` |
| ADR-005 | MAU-V as north star metric | `KPI_HIERARCHY_V1.md` |
| ADR-006 | $4.99/mo premium pricing | `IAP_SUBSCRIPTION_COMPLIANCE_V1.md` |
| ADR-007 | PostgreSQL FTS for search | `SEARCH_RELEVANCE_STRATEGY_V1.md` |
| ADR-008 | Anonymize + purge for deletion | `DATA_RETENTION_DELETION_V1.md` |

Backfill these as individual ADR files when time permits. The specs themselves serve as the decision record for now.

---

## 4) Ranking Quality Evaluation

### 4.1 Method

See `docs/architecture/RANKING_QUALITY_EVALUATION_V1.md` for full framework. Summary:
- 10 synthetic test personas with expected score ranges.
- 6 acceptance criteria (quality > quantity, spam penalized, etc.).
- Run after each formula change.
- Manual spot-check, not automated CI.

### 4.2 Calibration Cadence

- After each beta stage gate.
- After any formula weight change.
- Monthly during post-launch stabilization.

---

## 5) Open Decisions

1. Whether to create a dedicated `docs/decisions/` directory now or wait until first ADR is needed.
2. Whether experiment results should be shared with beta testers (transparency) or kept internal.
3. Whether to use PostHog's experiment analysis or export to a notebook for custom analysis.
