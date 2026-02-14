# Simulation Results V1 (Architecture Stress Testing)

Date: 2026-02-14
Purpose: validate DB-first architecture under extreme contact-degree skew, ownership collisions, stale data, and class expansion.

## A. Program Summary

- Monte Carlo passes run: 3
- Total iterations executed: 3,900
  - Pass A (degree distribution): 1,500
  - Pass B (baseline vs mitigated architecture stress): 1,200
  - Pass C (user class expansion: single/shadow/business): 1,200
- Forced constraints in all relevant runs:
  - at least one user with 1,000,000 contacts
  - at least one user with 5 contacts

## B. Pass A: Degree Distribution

Median outputs:

- `p95 contacts/user`: 523.5
- `p99 contacts/user`: 1223.5
- `gini`: 0.675
- Top 0.1% edge share: 15.23% (p90 20.99%)
- Top 1% edge share: 26.16%
- Whale share of edges (median): 11.71%

Scale-derived operational medians:

| Records | Whale Daily Mutations (median) | Whale Daily Mutations (p95) | Candidate Match Fanout (median/p95) |
|---:|---:|---:|---:|
| 10M | 11,711 | 21,628 | 4.81 / 6.75 |
| 100M | 117,109 | 216,281 | 4.81 / 6.75 |
| 1B | 1,171,091 | 2,162,811 | 4.81 / 6.75 |
| 10B | 11,710,905 | 21,628,111 | 4.81 / 6.75 |

## C. Pass B: Baseline vs Mitigated Architecture

### Baseline assumptions

- Owner-only partition hot path
- No owner-level ingest throttling
- No stale-decay policy
- No claim hold-period

### Mitigated assumptions

- Owner + bucket strategy (200 buckets for 1M-contact owner)
- Owner ingest rate cap: 200 writes/s
- Stale-decay policy active
- Ownership claim hold period: 72h

### Results (event rates by run)

| Metric | Baseline | Mitigated |
|---|---:|---:|
| Hot partition overload rate | 100% | 0% |
| NATS throughput overload rate | 0% | 0% |
| Verification/dispute overload rate at 10B records | 65.9% | 64.2% |
| Whale sync duration (1M contacts, median) | 13.9 min | 83.3 min |
| Hijack exposure (p95) | ~114h | ~89h |
| False-merge risk index (median, relative) | ~20.2 | ~7.2 |

Interpretation:

- Write-path reliability improves drastically with bucketization + throttling.
- Verification/dispute operations become dominant bottleneck at very high scale.
- Faster whale sync and safer partitions are a direct tradeoff unless more infra and parallelism are added.

## D. Pass C: User Class Expansion Risk

Simulated classes:
- Single user
- Shadow user (owner-controlled alter ego)
- Business user + employee profiles

Median results:

- Shadow-to-single ratio: ~0.25
- Search index document multiplier: ~1.6x (p95 ~2.2x)
- Business principal share: ~1.8%
- Org employee p99 (median across runs): ~50-56

Shadow abuse workload estimates:

| Records | Shadow Abuse Cases/Day (median) | p95 |
|---:|---:|---:|
| 10M | 17.7 | 55.1 |
| 100M | 169.9 | 558.1 |
| 1B | 1,890.3 | 5,480.3 |
| 10B | 17,310.5 | 53,792.1 |

Interpretation:

- Shadow class materially amplifies moderation and search load if discoverable by default.
- Namespace and discoverability policies are required before feature launch.

## E. Unresolved After Two Iterative Adjustments

1. Verification/dispute throughput at extreme record scale.
2. Shadow discoverability abuse policy.
3. Business delegated-authority lifecycle policy.

These require product-policy decisions, not only architecture changes.
