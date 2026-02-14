# Project Synthesis: Contact-Graph Social Network

## 1) Product Intent

Build a new social network from private contact graphs (phone contacts first, then app imports like WhatsApp/Signal/Telegram), then evolve into a super app.

Immediate product focus is the social graph:
- Help users connect faster
- Help users organize and control relationships
- Surface forgotten/unknown contacts
- Create visible ranking mechanics that drive intentional network building

Primary early user:
- Technical "super connectors" with large, complex networks

## 2) Core Product Mechanics (What You Were Designing)

### A. Three Ranking Scopes
- Local: me + my direct contacts
- Regional/Community: 2-hop neighborhood (friends of friends)
- Global: all users in the network

### B. Ranking Outcomes
- Vanity and comparison (explicit rank/percentile)
- Discovery (recommended people and bridge connections)
- Intentionality (optimize for stronger network composition)

### C. Network Distance as a Product Primitive
- Distance between users is first-class UX and business logic
- Distance informs messaging/contact access pricing
- Pricing is not only path distance; it also includes target user strength/rank

## 3) Data and Identity Model Direction

From the transcripts, the system direction is clear:

### A. Immutable Raw Ingestion
- Keep source data exactly as uploaded per source/app
- Never mutate original records
- Preserve provenance: who, when, source app, import event

### B. Canonicalized Identity Layer
- Deduplicate and unify contacts into canonical entities
- Keep reversible merge history and confidence scores
- Maintain complete auditability of every identity decision

### C. Exposure Layer Separated from Dedup Layer
- Use cross-network signals to improve matching confidence
- Do not expose third-party relationship data just because it helped dedup
- Matching intelligence can be shared; relationship visibility is policy-controlled

## 4) Algorithm Trajectory You Explored

You explored two ranking families:

### A. PageRank-style / Random Walk family (dominant direction)
- Weighted transitions across contact edges
- Damping/restart mechanics
- Monte Carlo approximation for large-scale global rank
- Periodic global recompute + near-real-time local approximation

### B. TrueSkill/Elo-style family (exploratory direction)
- Treat contact-list asymmetry and circle placement as "match signals"
- Multi-dimensional ratings by circle
- Circle-value inference without explicit user-entered circle weights

Current best fit for your stated goals:
- Use graph-centrality/random-walk approach as primary global ranking system
- Keep TrueSkill-style ideas as auxiliary signal layer for experimentation

## 5) Product Design Constraints You Called Out

### A. Ranking Stability and Mental Model
- Users must understand how to improve rank
- Official rank should update on a predictable cadence (daily/weekly)
- Local/provisional changes can be faster but should be clearly labeled
- Decompose rank into understandable components (quality, diversity, reach)

### B. Quality over Quantity Incentive
- Connecting to high-signal users should matter more than raw contact count
- Many weak edges should not dominate score
- Product should visually teach this incentive structure

### C. Dynamic Network Updates
- Full global rank recomputation on schedule
- Bounded local recalculation on connection/disconnection events
- Reconcile local approximations into the next global snapshot

## 6) Business Mechanic Direction (Access Pricing)

Intent captured from your notes:
- Direct connection: free
- One-hop with similar strength: low cost (e.g., $1 baseline)
- Distant + high-strength target: high cost
- System-wide upper bound target: up to $1M for extreme cases

So pricing function inputs should be:
- Graph distance(user_a, user_b)
- Target strength/rank percentile
- Potentially requester strength and route quality (future)

## 7) System Architecture Direction (Non-Code)

### A. Compute Layers
- Global ranking batch layer (Monte Carlo/random walk, large cluster)
- Local reactive ranking layer (bounded subgraph updates)
- Retrieval/slicing layer (local/regional/global views per user)
- Recommendation layer (bridges, introductions, strategic connections)

### B. Storage Layers
- Immutable raw import log
- Canonical entity graph + merge ledger
- Rank snapshots (versioned)
- Low-latency serving/index/cache for rank and distance queries

### C. Operational Principles
- Version every ranking run
- Keep replay/rebuild ability from source logs
- Treat cost model and rank model as configurable, not hardcoded

## 8) Risks You Identified

Top concerns you named:
- Distribution
- Scale and operational complexity
- Algorithm quality/value ("nail the algorithm")

Additional risks from transcript context:
- User confusion from unstable ranks
- Self-reinforcing ranking loops
- Economic abuse/gaming around paid access
- Identity merge errors damaging trust

## 9) Recommended MVP Boundary (Draft to Refine Together)

Suggested MVP scope:
- Phone contacts import only (v1)
- Basic canonicalization + manual correction + full history/audit
- Local + 2-hop ranking only (delay global public leaderboard)
- Rank explanation panel (why score changed)
- Lightweight discovery suggestions inside 2-hop network

Explicitly postpone:
- Full global ranking publication
- High-stakes paid distance-to-contact market
- Multi-app ingestion at full scale

Reason:
- De-risks algorithm correctness, UX clarity, and trust before global mechanics

## 10) Key Open Decisions for Next Design Session

1. Define the exact "magic moment" for first-time users.
2. Choose initial rank display: percentile, tier, or absolute rank.
3. Decide official rank cadence (daily vs weekly).
4. Finalize v1 ranking objective function (quality/quantity balance).
5. Decide when to introduce pricing and at which scope (local only vs wider).
6. Set merge-confidence thresholds and user override UX.

