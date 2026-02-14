# Rin Score V1 (0-100)

## Goal

Design a ranking score that:
- rewards **strength of network** over raw size
- is explainable to users
- can be computed from currently available signals (contacts + circles + verification + graph structure)
- is stable enough for user trust
- adds near-zero extra user work

## What V1 Uses (and does not use)

Uses:
- verified phone/email ownership
- contact graph edges
- reciprocity (A has B and B has A)
- lightweight circle signal (only if user already organized contacts)
- edge persistence across snapshots
- 1-hop and 2-hop structure

Does not use (V1):
- iMessage metadata/content
- private message content from any source
- invasive behavioral tracking

## Score Shape

`Rin Score = 100 * (0.40*Quality + 0.30*Position + 0.20*Stability + 0.10*Trust)`

Each component is normalized to `[0,1]`.

## Component Definitions

## 1) Quality (40%)

Intent:
- prioritize strong, reciprocal, meaningful ties.

Signals:
- reciprocity ratio
- matched canonical confidence
- verified-identity coverage among top ties
- optional small boost for explicitly organized contacts (if present)

Design notes:
- one-way edges count less.
- user-provided circle data is **optional** and low weight in V1.
- no extra tier selection is required.

## 2) Position (30%)

Intent:
- measure network strength without rewarding bulk spammy contact lists.

Signals:
- weighted centrality on local + 2-hop graph
- bridge value (connects otherwise separate clusters)
- diminishing returns on large edge counts

Design notes:
- use log/sqrt dampening on edge volume to prevent “more contacts = always better.”

## 3) Stability (20%)

Intent:
- reward consistent, persistent relationship graph over time.

Signals:
- persistence of core ties across snapshots
- low churn in reciprocal high-confidence ties
- continuity of verified channels

Design notes:
- protects users from huge day-to-day score swings.

## 4) Trust (10%)

Intent:
- make verified, low-abuse behavior part of ranking health.

Signals:
- low abuse/spam flags
- low unresolved identity-dispute risk
- account integrity freshness (e.g., recent recovery/reverification events)

Design notes:
- small but meaningful component to discourage abuse.

## Anti-Gaming Rules

1. Diminishing returns on total contacts.
2. Minimal gain from non-reciprocal bulk additions.
3. Stronger weighting for verified reciprocal ties.
4. Rate-limited impact from sudden contact spikes.
5. Confidence-adjusted scoring for uncertain dedup links.

## User-Facing Explainability

Show score plus component bars:
- `Network Quality`
- `Network Position`
- `Stability`
- `Trust`

Example copy:
- “Your score is strong because many of your close-circle connections are mutual and stable.”
- “You added many new contacts, but score impact is limited until those ties are verified/mutual.”

## Update Cadence

- Official score: fixed schedule (daily or weekly).
- Optional provisional local estimate: separate visual label.

## Suggested V1 Default Tuning

- Quality: 40
- Position: 30
- Stability: 20
- Trust: 10
- Stability window: **90 days**
- Official score cadence: **daily**

Reason:
- aligns with product goal: strength > size
- keeps graph effects meaningful without overpowering trust and stability

## Circle Signal Policy (Low Burden)

Problem:
- Circle management is already cognitively expensive.
- Additional tiering inputs would add too much friction.

V1 rule:
- No extra tier metadata required from user.
- Circle names are not interpreted semantically.
- Circle information contributes only a small optional boost when present.
- Users who never organize circles should still get a high-quality score from passive graph signals.

Implementation hint:
- Keep most Quality weight on reciprocity + verified canonical ties.
- Cap circle-based uplift to a small range (e.g., max +5% of Quality component).

Locked baseline (v1.1):
- Circle uplift cap: **+5%** (optional signal only)
- Trust penalty severity: **Moderate** (max **-15** score points)
- Stability window: **90 days**
- Official cadence: **daily**

Note:
- These are intentionally conservative and can be revisited after live calibration.

## Trust Penalty Model (Updated)

Important:
- If only verified channels are ingestible, “unverified channel” is not a valid penalty trigger.

V1 trust penalties should use:
1. unresolved ownership disputes
2. abuse/spam risk flags
3. account integrity risk (suspicious takeover, forced recovery, repeated re-verification failures)

Severity bands:
- Soft: max `-8` score points
- Moderate: max `-15` score points
- Hard: max `-30` score points

Decay:
- Penalties decay after clean behavior windows (e.g., 30/60/90 days).

## Calibration Plan

1. Run on internal/test cohorts.
2. Compare users with:
- many weak ties
- few strong ties
- mixed profiles
3. Check if score ordering matches expected product intuition.
4. Tune weights in small increments (e.g., ±5 points).
5. Freeze one version per release cycle for user trust.
