# Unit Economics Model V1

Back-of-napkin model for Rin's freemium subscription business. Updated: 2026-02-15.

Companion docs:
- `docs/plan/IAP_SUBSCRIPTION_COMPLIANCE_V1.md` (pricing, StoreKit)
- `docs/architecture/CLOUD_PROVIDER_STRATEGY_V1.md` (infra costs)

---

## 1) Revenue Per User

### Assumptions

| Input | Value | Notes |
|-------|-------|-------|
| Monthly price | $4.99 | StoreKit localized |
| Annual price | $49.99/yr ($4.17/mo effective) | ~16% discount |
| Free-to-premium conversion | 4% | 3-5% typical for freemium (see note below) |
| Plan mix (monthly:annual) | 40:60 | Annual highlighted as default |
| Apple cut | 15% | Small Business Program (<$1M revenue) |

**Note:** The 4% conversion rate is an aspirational target. The Monetization Experiments funnel model (20% paywall exposure x 5% trial start x 30% trial conversion) implies ~0.3% of MAU initially. Early-stage break-even likely requires higher organic conversion from power users. Monitor actual conversion from Beta Stage 2 onward and revise this model accordingly.

### Blended ARPU Calculation

Blended premium monthly revenue per subscriber:

```
Monthly subs:  0.40 x $4.99  = $2.00
Annual subs:   0.60 x $4.17  = $2.50
                               ------
Blended revenue/user/mo      = $4.50

After Apple's 15% cut:
  $4.50 x 0.85               = $3.83 net per premium user/mo
```

**Monthly ARPU across all users** (at 4% conversion):

```
$3.83 x 0.04 = $0.15 ARPU/mo (blended across free + paid)
```

---

## 2) Cost Per User

### Fixed Costs (Stage A: 0-1,000 Users)

| Item | Monthly Cost | Notes |
|------|-------------|-------|
| Hetzner CPX31 (4 vCPU, 8 GB) | ~$44 (~EUR40) | Go monolith + NATS |
| Managed Postgres (Ubicloud/Neon) | ~$16 (~EUR15) | Included backups |
| Hetzner Object Storage | ~$5 | Backups, media |
| Cloudflare | $0 | Free tier (DNS, CDN, DDoS) |
| PostHog | $0 | Free tier (<1M events/mo) |
| Sentry | $0 | Free tier (5K events/mo) |
| UptimeRobot | $0 | Free tier |
| Apple Developer Program | $8.25 | $99/yr amortized |
| Domain | ~$2 | ~$24/yr amortized |
| **Total fixed** | **~$75/mo** | |

### Variable Cost Per User (Marginal)

At Stage A scale (single VM handles ~1,000 users), marginal cost per additional user is near zero until the VM saturates. Meaningful variable costs kick in at scale:

| Scale | Infra Cost/Mo | Cost/User/Mo | Notes |
|-------|--------------|-------------|-------|
| 100 users | $75 | $0.75 | Fixed cost dominated |
| 1,000 users | $75 | $0.075 | VM still has headroom |
| 10,000 users | ~$100 | $0.010 | Stage B: ~EUR80/mo compute (Cloud Provider Strategy) plus managed DB scale-up and storage growth |
| 100,000 users | ~$500 | $0.005 | Stage C: service split |

---

## 3) Key Ratios

### Customer Acquisition Cost (CAC)

| Channel | CAC | Notes |
|---------|-----|-------|
| Organic / word-of-mouth | ~$0 | Solo founder, no paid acq |
| Referral (free premium month) | $3.83 | Net cost of 1 free month |
| Blended (90% organic, 10% referral) | ~$0.38 | Early stage |

### Lifetime Value (LTV)

| Scenario | Retention | LTV (net) | Calculation |
|----------|-----------|-----------|-------------|
| Conservative | 6 months | $23.00 | $3.83 x 6 |
| Moderate | 9 months | $34.47 | $3.83 x 9 |
| Optimistic | 12 months | $45.96 | $3.83 x 12 |

### Ratios

| Metric | Conservative | Moderate | Notes |
|--------|-------------|----------|-------|
| LTV | $23.00 | $34.47 | Per premium subscriber |
| CAC (blended) | $0.38 | $0.38 | Mostly organic |
| **LTV:CAC** | **61:1** | **91:1** | Absurdly high because CAC~0 |
| Payback period | <1 month | <1 month | First payment covers CAC |
| Gross margin | ~80-95% | ~80-95% | Depends on scale (see below) |

*LTV:CAC is artificially high with zero paid acquisition. When/if paid channels are added ($5-15 CAC typical for social apps), ratio normalizes to 2-7:1.*

### Gross Margin by Scale

```
Gross margin = (Revenue - Infra costs) / Revenue

At 1,000 users (40 premium):
  Revenue:  40 x $3.83 = $153/mo
  Infra:    $75/mo
  Margin:   ($153 - $75) / $153 = 51%

At 10,000 users (400 premium):
  Revenue:  400 x $3.83 = $1,532/mo
  Infra:    $100/mo
  Margin:   ($1,532 - $100) / $1,532 = 93%
```

---

## 4) Break-Even Analysis

### Monthly Fixed Costs

```
Infrastructure:  $75/mo  (Stage A)
Apple Dev:       $8/mo
Domain:          $2/mo
                 -------
Total:           $85/mo
```

### Break-Even Subscribers

```
Net revenue per premium user:  $3.83/mo
Fixed costs:                   $85/mo

Premium subs needed:  $85 / $3.83 = 23 premium subscribers
```

### Break-Even Total Users

```
At 4% conversion:  23 / 0.04 = 575 total users

At 3% conversion:  23 / 0.03 = 767 total users
At 5% conversion:  23 / 0.05 = 460 total users
```

**Bottom line: ~575 total users to break even on infrastructure.**

### Founder Salary Break-Even

For a modest $5,000/mo founder salary:

```
($5,000 + $85) / $3.83 = 1,327 premium subscribers
1,327 / 0.04 = ~33,175 total users
```

---

## 5) Milestones Table

| Metric | 100 Users | 1K Users | 10K Users | 100K Users |
|--------|-----------|----------|-----------|------------|
| **Premium subs** (4%) | 4 | 40 | 400 | 4,000 |
| **Gross revenue/mo** | $18 | $180 | $1,800 | $18,000 |
| **Net revenue/mo** (after Apple) | $15 | $153 | $1,532 | $15,320 |
| **Infra cost/mo** | $75 | $75 | $100 | $500 |
| **Net margin/mo** | -$60 | +$78 | +$1,432 | +$14,820 |
| **Gross margin %** | -300% | 51% | 93% | 97% |
| **Infra stage** | A (1 VM) | A (1 VM) | B (3 VMs) | C (10+ VMs) |
| **ARR** | $180 | $1,836 | $18,384 | $183,840 |
| **Viable?** | Hobby | Ramen break-even | Solo salary | Small team |

---

## 6) Key Sensitivities

Things that move the needle most:

| Lever | Impact | Notes |
|-------|--------|-------|
| Conversion rate (3% vs 5%) | +/- 67% revenue | Paywall design, feature value |
| Annual mix (40% vs 80%) | -10% to +5% revenue | Annual has lower effective rate but better retention |
| Retention (6 vs 12 months) | 2x LTV | Core product value drives this |
| Apple cut (15% vs 30%) | 18% revenue swing | Lose Small Business Program at $1M |
| Price increase ($4.99 vs $6.99) | +40% revenue | Test after PMF, grandfathering existing |

---

## 7) Assumptions to Revisit

- [ ] Actual conversion rate after Stage 2 beta (gated premium).
- [ ] Monthly vs annual plan mix from real subscriber data.
- [ ] Average retention / churn rate from first 3 months of paid subs.
- [ ] Whether referral program is worth the $3.83 cost per referral.
- [ ] Infrastructure cost curve as usage patterns emerge (storage vs compute bound).
- [ ] Whether to offer free trial (impact on conversion vs immediate revenue).
