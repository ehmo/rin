# Actionable Intake From Resource Review

## 0) Immediate Product Positioning

- Core promise: `Be easy to find, hard to reach.`
- Working product category: `Friend CRM + social graph utility`
- Avoid becoming generic feed/video social app (see signals around TikTok-ification).

## 1) MVP Candidate (Design/Product Only)

1. Identity and profile
- Start with email identity + controlled profile
- Add phone and additional sources progressively

2. Relationship graph
- Import contacts
- Create circles
- Show rank/context in local graph first

3. Discovery utility
- Surface:
  - “People you know but forgot”
  - “Friends in city / available now” style prompts

4. Reachability controls
- Public contact endpoint with circle-based openness
- Distance/strength-aware access logic (pricing later or limited beta)

## 2) Ranking Design Inputs To Keep

- Use cadence-based relationship intensity as a strong signal (daily/weekly/rare buckets).
- Use circles as explicit intent signals, but do not rely only on circle size.
- Keep quality-over-quantity incentives visible in UX.

## 3) Data Connector Priorities

Priority order:
1. Email metadata connector (sender/recipient patterns, not content by default)
2. Phone contacts
3. Calendar/location availability signals (opt-in)
4. Additional messaging apps

## 4) Safety/Trust Design Requirements

- Ownership verification for each source before activation
- Anti-hijack recovery flows
- Fraudulent source-claim dispute workflow
- Bounce/spam feedback loop for outreach channels

## 5) Research/Algorithm Queue

1. Damping factor sensitivity experiments for ranking stability
2. Distance computation options for large directed graph
3. Circle-weight inference using behavior + explicit labels
4. Rank volatility smoothing for user-facing predictability

## 6) GTM/Validation Implications

- Validate as utility (CRM/discovery/reachability), not as another feed.
- Track demand among super-connectors first.
- Keep weekly PMF scorecard tied to:
  - Time-to-first-insight
  - D7 return for rank/discovery actions
  - Intentional graph-management behavior

