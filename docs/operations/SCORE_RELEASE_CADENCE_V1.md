# Score Computation Release Cadence V1

## 1) Purpose

Define how Rin Score formula changes are deployed, monitored, and rolled back. Ensures user trust through stable scores while allowing continuous formula improvement.

Companion docs:
- `docs/product/RIN_SCORE_V1.md` (score formula and components)
- `docs/plan/outlines/04_OBSERVABILITY_ALERTING_OUTLINE_V1.md` (SLI/SLO framework)

---

## 2) Computation Schedule

### 2.1 Official Score

- Cadence: **daily** (locked in RIN_SCORE_V1.md v1.1).
- Compute window: 02:00-04:00 UTC (off-peak).
- All users scored in single batch.
- Score becomes visible after full batch completes (atomic publish).

### 2.2 Provisional Local Estimate

- Computed on-device after significant local changes (import, dedup, circle edit).
- Labeled distinctly from official score (e.g., "estimated" indicator).
- Replaced by next official score.
- Not stored server-side.

---

## 3) Formula Versioning

### 3.1 Version Scheme

`v<major>.<minor>` — e.g., `v1.0`, `v1.1`, `v1.2`.

| Change type | Version bump | Example |
|-------------|-------------|---------|
| Weight rebalance (±5 points) | Minor | Quality 40→42, Position 30→28 |
| New signal added | Minor | Add "contact recency" to Stability |
| Component restructure | Major | Split Quality into sub-components |
| Formula architecture change | Major | Change from weighted sum to ML model |

### 3.2 Version Tracking

- Current formula version stored in deployment config.
- Each score record tagged with formula version used.
- Historical scores queryable by version for comparison.

---

## 4) Deploy Process

### 4.1 Silent Deploy (Default)

All formula changes deploy silently:

1. **Author**: Update formula weights/signals in config.
2. **Shadow run**: New formula computes alongside current for 1 batch cycle (1 day).
3. **Compare**: Generate distribution diff report (mean shift, percentile changes, affected user count).
4. **Deploy**: If distribution diff within acceptable range, activate new formula for next batch.
5. **Monitor**: Watch auto-rollback triggers for 72 hours post-deploy.

### 4.2 No User Notification

- Score changes appear naturally after next daily batch.
- No in-app announcement for minor/patch changes.
- Major version changes (v2.0+): consider optional blog/changelog post, but still no in-app interruption.

---

## 5) Auto-Rollback Policy

### 5.1 Triggers (Conservative)

Auto-rollback fires if **any** of these conditions are met within 24 hours of deploy:

| Trigger | Threshold |
|---------|-----------|
| Users with score change >10 points | >5% of active users |
| Users with score change >20 points | >1% of active users |
| Mean score shift across all users | >5 points in either direction |
| Score computation failure rate | >0.1% of users |
| Computation duration | >2x normal batch time |

### 5.2 Rollback Mechanics

1. **Detection**: Monitoring job runs at batch+1h, batch+6h, batch+24h.
2. **Revert**: Restore previous formula version config.
3. **Recompute**: Trigger off-cycle batch with reverted formula.
4. **Publish**: Reverted scores replace anomalous scores.
5. **Alert**: Founder notified via push + Sentry alert.

### 5.3 Revert Timeline

- Detection to revert decision: automated (no human in loop).
- Revert to recompute start: <5 minutes.
- Recompute to publish: same as normal batch duration.
- Users see corrected scores within 1 batch cycle of rollback trigger.

---

## 6) Shadow Mode

### 6.1 Pre-Deploy Shadow

Before any formula change goes live:

1. New formula runs in parallel with current during one batch cycle.
2. Shadow results stored in separate table (not user-visible).
3. Distribution comparison report generated automatically:
   - Mean/median/p10/p50/p90 shift.
   - Count of users with >5, >10, >15, >20 point changes.
   - Per-component breakdown (Quality, Position, Stability, Trust).
4. Report reviewed before deploy decision.

### 6.2 Shadow Duration

- **Minor changes**: 1 day shadow minimum.
- **Major changes**: 3 day shadow minimum.
- **New signal introduction**: 7 day shadow recommended.

---

## 7) Monitoring Dashboard

### 7.1 Score Health Metrics

| Metric | Check frequency |
|--------|----------------|
| Batch completion time | Every batch |
| Computation failure count | Every batch |
| Score distribution (p10/p50/p90) | Daily |
| Day-over-day mean shift | Daily |
| Users with >10 point change | Daily |
| Formula version in production | Continuous |

### 7.2 Post-Deploy Watch

After any formula deploy, enhanced monitoring for 72 hours:
- Hourly distribution snapshots (not just daily).
- Auto-rollback checks at 1h, 6h, 24h, 48h, 72h.
- Founder receives daily summary of score distribution health.

---

## 8) Calibration Process

### 8.1 When to Tune

- After each beta stage gate (Stage 1→2, 2→3, 3→launch).
- When score distribution is heavily skewed (>80% of users in same 10-point band).
- When user feedback indicates score doesn't match perceived network quality.
- After adding new data signals (e.g., enrichment data becomes available).

### 8.2 Tuning Protocol

1. Export current score distribution + component breakdowns.
2. Identify calibration targets (e.g., "users with 5 strong reciprocal ties should score 60+").
3. Adjust weights in ±5 point increments only.
4. Shadow run for minimum required duration.
5. Review distribution report.
6. Deploy if healthy, iterate if not.

### 8.3 Freeze Windows

- No formula changes within 48 hours of a beta stage gate evaluation.
- No formula changes during the 7 days before public launch.
- Post-launch: no changes in first 14 days (let users establish baseline).

---

## 9) Score Persistence and History

### 9.1 Storage

- Official scores persisted with timestamp and formula version.
- Keep 90 days of daily scores per user (matches stability window).
- Older scores archived to cold storage (queryable but not instant).

### 9.2 User-Facing History

- Users can see score trend (last 30 days) as a simple sparkline.
- No formula version exposed to users.
- Component bar breakdown shows current snapshot only.

---

## 10) Open Decisions

1. Whether shadow mode comparison should auto-block deploys that exceed thresholds or just warn.
2. Whether to expose score history beyond 30 days to users (e.g., "Your score 3 months ago").
3. Whether A/B testing different formula versions across user segments is acceptable (could create fairness concerns).
4. Exact off-peak compute window (02:00-04:00 UTC assumed; may need adjustment for user geography).
