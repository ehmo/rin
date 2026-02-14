# PMF Evaluation Playbook for LLM Agent

Source adapted from: `The PMF Playbook.txt` (John Danner)

Purpose:
- Give an LLM agent a strict, repeatable process to evaluate PMF progress for this contact-graph social network.
- Enforce stage order so the team does not chase growth before magic/habit.

## 1) Agent Operating Rules

1. Evaluate one primary stage metric at a time.
2. Require evidence, not claims.
3. Block paid-growth recommendations until Magic + Habit pass minimum gates.
4. Recommend daily experiments and weekly review cadence.
5. Grade each stage A/B/C/F and compute overall PMF readiness.

## 2) Inputs the Agent Must Collect

For the latest 4-8 weeks:
- Visitor counts (organic vs paid split)
- Signup conversion funnel
- Retention cohorts (D1, D7, D30)
- Sessions per active user per week
- Organic new users per week by channel
- Organic MoM growth rate
- Activation funnel events
- Paid conversion rate (if monetization is active)
- Qualitative evidence: user interviews, support logs, churn reasons

For this product specifically:
- `% users who import contacts successfully`
- `% users who experience first network insight ("magic moment")`
- `% users who return to check rank/discovery within 7 days`
- `% users who perform intentional graph action` (organize/contact/discover)

## 3) Stage Scorecard (Adapted)

Use these thresholds:

| Stage | Metric | A | B | C | Minimum Gate |
|---|---|---:|---:|---:|---|
| Magic | % visitors who see magic and become users | 80% | 60% | 40% | **B required** |
| Habit | D7 retention and D7->D30 retention | 80% | 60% | 40% | C required |
| Engagement | Avg visits per week | 7 | 5 | 3 | C required |
| Channel | Organic visitors per week | 1000 | 800 | 600 | C required |
| Growth | Organic MoM growth | 20% | 15% | 10% | C required |
| Activation | D7 retention from activated users | 80% | 60% | 40% | C required |
| Monetization | Top-of-funnel to paid | 10% | 7% | 3% | C required (if paywall active) |

## 4) Product-Specific Metric Definitions

Use these operational definitions:

- Magic event:
  User imports contacts and receives at least one meaningful network output
  (e.g., rank view + discovery candidate + clear explanation).

- Activated user:
  User completes import + sees first rank + takes one intentional action
  (label, organize, connect request, or discovery interaction).

- Habit:
  User returns in week 1 and week 4 to evaluate/improve network position.

- Engagement:
  Weekly sessions where user performs network-management actions, not passive opens.

## 5) Evaluation Algorithm (Agent Workflow)

1. Validate data quality and cohort integrity.
2. Calculate each stage metric using trailing 4-week cohorts.
3. Assign grade by threshold.
4. Check gates:
   - If Magic < B: force focus on Magic only.
   - Else if any other stage < C: focus only on the lowest stage.
5. Generate root-cause diagnosis:
   - Funnel friction
   - Weak value perception
   - Poor onboarding/time-to-magic
   - Low rank explainability
   - Discovery relevance mismatch
6. Propose exactly 3-5 experiments for the next 7 days.
7. Define expected movement and stop condition for each experiment.

## 6) Weekly Output Format (Required)

The agent must output:

1. PMF Scorecard Table
2. Overall PMF Readiness:
   - `Not Ready`
   - `Emerging`
   - `Approaching PMF`
   - `PMF Likely`
3. Biggest Constraint (single stage only)
4. Top 3 hypotheses for why that stage is constrained
5. Next 7-day experiment plan (3-5 tests)
6. Risks:
   - data quality risk
   - false-positive growth risk
   - retention illusion risk

## 7) Decision Gates

- Do not prioritize growth loops if Magic < B or Habit < C.
- Do not prioritize monetization if activation/habit are below gates.
- If metrics plateau for ~6 months despite high experiment cadence, trigger adjacency/pivot review.

## 8) Experiment Cadence

Daily:
- At least one meaningful product or go-to-market experiment.

Weekly:
- Recompute scorecard
- Review one stage deeply
- Kill low-signal experiments quickly
- Double down on experiments that move the single constrained metric

## 9) Anti-Gaming Rules

Agent must flag:
- Paid traffic mixed into organic growth claims
- Vanity metrics replacing retention metrics
- Rank views counted as engagement without user action
- Funnel changes that increase signups but degrade D7/D30 retention

## 10) Current Product Focus Recommendation

Based on current strategy, evaluate in this order:

1. Magic (first network insight quality)
2. Habit (weekly return behavior)
3. Activation (time-to-magic and first intentional action)
4. Channel (organic super-connector acquisition)
5. Growth loops
6. Monetization later

