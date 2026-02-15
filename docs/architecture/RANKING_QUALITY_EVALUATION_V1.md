# Ranking Quality Evaluation Framework V1

## 1) Purpose

Lightweight framework for evaluating whether the Rin Score formula produces sensible rankings. Minimal viable process for a solo founder.

Companion docs:
- `docs/product/RIN_SCORE_V1.md` (score formula)
- `docs/operations/SCORE_RELEASE_CADENCE_V1.md` (deploy and rollback)

---

## 2) Evaluation Method: Synthetic Test Users

### 2.1 Test Personas

Create 10 synthetic test users representing different network archetypes:

| Persona | Contacts | Reciprocal % | Circles | Verification | Expected rank |
|---------|----------|-------------|---------|--------------|---------------|
| **Power Networker** | 2,000 | 30% | 8 | Full | 70-85 |
| **Close Circle** | 50 | 90% | 3 | Full | 80-95 |
| **Professional** | 500 | 50% | 5 | Full | 65-80 |
| **Casual User** | 150 | 40% | 2 | Phone only | 45-60 |
| **New User** | 20 | 60% | 1 | Phone only | 25-40 |
| **Spam Adder** | 5,000 | 5% | 0 | Phone only | 15-30 |
| **Ghost** | 300 | 10% | 0 | Phone only | 20-35 |
| **Bridge Builder** | 200 | 60% | 6 | Full | 75-90 |
| **Family Focused** | 30 | 95% | 2 | Full | 70-85 |
| **Flagged User** | 100 | 40% | 2 | Full, 1 dispute | 30-50 |

### 2.2 Acceptance Criteria

The formula passes if:
1. **Close Circle > Power Networker** — quality over quantity.
2. **Bridge Builder > Ghost** — reciprocal connections matter.
3. **Spam Adder ranks lowest** among non-flagged users.
4. **Flagged User has visible trust penalty** (10-15 point drop from clean baseline).
5. **New User has building-range score** (not 0, shows potential).
6. **Family Focused scores well** despite small network (high reciprocity).

### 2.3 Calibration Spot-Check

Run after each formula change:
1. Compute scores for all 10 personas.
2. Check acceptance criteria pass/fail.
3. If any criteria fails: investigate which component weight needs adjustment.
4. Adjust weights in ±5 point increments.
5. Re-run until all criteria pass.

---

## 3) Live Calibration (Post-Launch)

### 3.1 Distribution Health Checks

Weekly review of score distribution:
- Mean score should be 45-65 (not too generous, not too harsh).
- Standard deviation should be 15-25 (meaningful spread).
- <5% of users at exactly 0 or 100 (avoid ceiling/floor compression).
- No bimodal distribution (indicates formula discontinuity).

### 3.2 User Feedback Signals

Track complaints and feedback about scores:
- "My score seems too low" — investigate Quality and Position components.
- "My score dropped for no reason" — check Stability component sensitivity.
- "I added contacts but score didn't change" — verify diminishing returns work.

---

## 4) Open Decisions

1. Whether to create a dedicated test data generator or manually construct synthetic users.
2. Whether to add persona diversity (geographic spread, contact list language variety).
3. Whether to run calibration checks in CI or as a manual scheduled task.
