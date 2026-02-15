# Shadow Profile Anti-Abuse Policy V1

## 1) Purpose

Define detection, enforcement, and escalation policies for shadow profile abuse. Addresses three primary abuse vectors: mass creation for spam, impersonation, and block evasion.

Companion docs:
- `docs/product/SHADOW_PROFILE_UX_V1.md` (shadow UX, creation controls, abuse rollup)
- `docs/operations/DISPUTE_PLAYBOOK_V1.md` (case type C4: impersonation, C6: abuse-driven trust)
- `docs/operations/DISPUTE_OPERATIONS_V1.md` (queue routing, auto-adjudication)
- `docs/architecture/PROFILE_CLASS_CONTRACT_V1.md` (shadow class restrictions)

---

## 2) Threat Model

### T1: Mass Shadow Creation for Spam

**Attack**: user creates many shadows to send bulk unsolicited messages, each from a "fresh" identity.

**Why it works without controls**: each shadow appears as a new person with no prior reports. Rate limits on individual profiles don't aggregate.

### T2: Impersonation via Shadow

**Attack**: user creates a shadow mimicking another real person's name, photo, or identity to deceive recipients.

**Why it works without controls**: shadows are fully independent identities. System doesn't cross-reference shadow names against existing users by default.

### T3: Block Evasion via Shadow

**Attack**: user blocked on their primary (or another shadow) creates a new shadow to re-contact the blocker.

**Why it works without controls**: shadows are separate identities. The blocker doesn't know they're from the same principal.

---

## 3) Prevention Layer (Before Abuse Occurs)

### 3.1 Creation Rate Limits

| Account age | Max shadows per 24h | Max total shadows |
|-------------|--------------------|--------------------|
| < 7 days | 1 | 1 |
| 7-30 days | 2 | 3 |
| 30-90 days | 3 | 10 |
| 90+ days | 3 | Unlimited |

Rate limit hit → soft block with message: "You've reached the limit for new profiles today. Try again tomorrow."

### 3.2 Name Screening at Creation

On shadow creation, name is checked against:
1. **Exact match** with existing verified Rin usernames → warning + flag for review.
2. **Fuzzy match** (>80% similarity) with prominent/verified accounts → warning shown to creator.
3. **Banned name patterns** (slurs, impersonation keywords like "official", "real", "verified") → blocked.

Creator can proceed past warnings (except banned patterns), but the shadow is flagged for elevated monitoring.

### 3.3 Photo Screening at Creation

Shadow profile photos are checked against:
1. **Reverse image match** against other Rin user profile photos → flag if match found.
2. **Known stock photo database** (future) → flag as potential fake identity.

Flagged photos don't block creation but trigger elevated monitoring.

### 3.4 Outbound Restrictions for New Shadows

Fresh shadows (< 48h old) have outbound restrictions:

| Action | Restriction |
|--------|------------|
| Direct message to non-contacts | Blocked until 48h age |
| Ask requests (field access) | Limited to 5/day |
| Contact discovery/search | Normal |
| Circle management | Normal |

Restrictions lift automatically after 48h if no abuse signals detected.

---

## 4) Detection Layer (Identifying Active Abuse)

### 4.1 T1 Detection: Mass Spam

**Signals monitored per principal (across all shadows):**

| Signal | Threshold | Action |
|--------|-----------|--------|
| Outbound messages from all shadows combined | > 50/hour | Throttle to 10/hour |
| Unique recipients from all shadows combined | > 100/day | Throttle + flag |
| Block rate across all shadows | > 10% of recipients block | Restrict + queue P2 case |
| Report rate across all shadows | > 5 reports from unique users in 24h | Restrict + queue P1 case |

Key insight: **signals aggregate across the principal**, not per-shadow. This prevents the "fresh shadow" bypass.

### 4.2 T2 Detection: Impersonation

**Signals:**

| Signal | Detection method | Action |
|--------|-----------------|--------|
| Name match with verified user | Fuzzy matching on create + periodic scan | Flag for review |
| Photo match with verified user | Reverse image check | Flag for review |
| Behavioral mimicry | Shadow contacts the same people as the impersonated user | Queue P1 case |
| Report from impersonated user | Explicit report | Queue P1 case, immediate discoverability reduction |

### 4.3 T3 Detection: Block Evasion

**Signals:**

| Signal | Detection method | Action |
|--------|-----------------|--------|
| Shadow contacts someone who blocked another profile of the same principal | Cross-reference block list against principal's shadow set | Block message delivery silently |
| Shadow sends Ask request to someone who blocked principal | Same cross-reference | Reject request silently |
| Pattern: shadow created shortly after a block event on another profile | Temporal correlation | Elevate monitoring on new shadow |

**Critical enforcement**: block lists are enforced at the **principal level**, not the profile level. When User A blocks any profile of Principal B, all of Principal B's profiles (current and future) are blocked from contacting User A.

This is the single most important anti-abuse rule for shadow profiles.

---

## 5) Enforcement Actions

### 5.1 Graduated Response

| Level | Trigger | Actions | Duration |
|-------|---------|---------|----------|
| **Warning** | First threshold breach | In-app warning, behavior logged | Permanent record |
| **Throttle** | Sustained or repeated breach | Outbound rate limits tightened across all shadows | 24h, auto-lift if clean |
| **Restrict** | Multiple breaches or high-severity signal | Shadow outbound disabled, discoverability removed | Until case review |
| **Shadow suspend** | Confirmed abuse | Specific shadow deactivated | Until appeal resolved |
| **Principal suspend** | Severe or coordinated abuse | All profiles (primary + all shadows) suspended | Until appeal resolved |

### 5.2 Per-Action Enforcement Details

**Warning:**
- In-app notification: "Your activity on [shadow name] triggered a review. Continued unusual activity may result in restrictions."
- No functionality change.

**Throttle:**
- All shadows limited to 5 outbound messages/hour, 2 Ask requests/day.
- Throttle applies silently — messages queue and deliver slowly, no error shown.

**Restrict:**
- Shadow cannot send messages, Ask requests, or appear in search.
- User sees restriction notice with timeline and appeal CTA.
- Other profiles (primary, other shadows) unaffected unless principal-level action.

**Shadow suspend:**
- Shadow is fully deactivated. Not visible, not contactable, not switchable.
- User sees: "[Shadow name] has been suspended due to policy violation."
- Appeal available.

**Principal suspend:**
- All profiles deactivated.
- User sees full-screen suspension notice with appeal path.
- This is the nuclear option — reserved for clear, severe, or coordinated abuse.

---

## 6) Block Enforcement Architecture

### 6.1 Principal-Level Block Propagation

When User A blocks Profile X (which belongs to Principal B):

1. Block record created: `blocker=A, blocked_principal=B`
2. All existing profiles of Principal B are blocked from contacting A.
3. All **future** profiles of Principal B are automatically blocked from contacting A.
4. A does not learn that X has other profiles. The block is silent and invisible.

### 6.2 Block Scope

| Action | Blocked? |
|--------|----------|
| Send message to A | Yes (silently dropped) |
| Send Ask request to A | Yes (silently rejected) |
| View A's profile | Yes (profile hidden, shows "User not found") |
| Appear in A's search results | No — A never sees any of B's profiles |
| Appear in A's contact import | Filtered out |

### 6.3 Transparency to Blocked Principal

- Principal B does **not** know they are blocked.
- Messages sent to A appear to send successfully but are never delivered (shadow ban pattern).
- This prevents retaliation and reduces harassment escalation.

---

## 7) Impersonation Response Playbook

### 7.1 Immediate Actions (Auto-Applied on Report)

1. Reduce reported shadow's discoverability (remove from search, reduce visibility).
2. Add warning interstitial if someone navigates to the shadow's profile directly.
3. Notify the shadow owner that a review is in progress.

### 7.2 Investigation

1. Compare name/photo to reporter's claimed identity.
2. Check behavioral patterns (contacting the same network as the impersonated user).
3. Check if shadow owner has a history of impersonation flags.

### 7.3 Resolution Outcomes

| Finding | Action |
|---------|--------|
| **Confirmed impersonation** | Shadow suspended. Name/photo forcibly changed or deleted. Principal warned. |
| **Likely impersonation, uncertain** | Shadow restricted. Owner required to change name/photo or provide justification. |
| **Not impersonation** (common name, coincidence) | Restrictions lifted. Reporter notified of outcome. |
| **Repeated impersonation by same principal** | Principal-level restriction. Escalate to P0. |

---

## 8) Monitoring and Observability

### 8.1 Dashboards

Track daily:
- Shadow creation rate (total and per-principal).
- Outbound message volume from shadow profiles (aggregate).
- Block rate for shadow-originated contacts.
- Report rate for shadow profiles.
- Impersonation flag rate.

### 8.2 Alerts

| Alert | Threshold | Priority |
|-------|-----------|----------|
| Shadow creation spike | >3x daily average | P2 |
| Principal with >5 shadows in 7 days | Per-principal | P3 (monitor) |
| Block evasion attempt detected | Any | P1 |
| Impersonation report from verified user | Any | P1 |
| Mass shadow outbound spike | >2x hourly average | P2 |

---

## 9) Events

- `shadow.abuse.warning_issued` — principal ID, shadow ID, trigger signal
- `shadow.abuse.throttled` — principal ID, shadow IDs affected, duration
- `shadow.abuse.restricted` — shadow ID, restriction scope, case ID
- `shadow.abuse.suspended` — shadow ID, case ID
- `principal.abuse.suspended` — principal ID, case ID, shadow count affected
- `shadow.block_evasion.detected` — principal ID, shadow ID, blocked user ID
- `shadow.block_evasion.prevented` — message/request silently dropped
- `shadow.impersonation.reported` — shadow ID, reporter, matched identity
- `shadow.impersonation.confirmed` — shadow ID, case ID, action taken
- `shadow.name_screened` — shadow ID, match type (exact/fuzzy/banned), matched against

---

## 10) Edge Cases

1. **User legitimately named "John Smith" flagged for impersonation**: common name handling. If creator can verify their own identity matches the name, restrictions lifted.
2. **User creates shadow, gets blocked, deletes shadow, creates new one to contact same person**: principal-level block persists across shadow deletion and creation. New shadow still blocked.
3. **User shares device with family member, one person's block affects the other**: blocks are per-principal, not per-device. Family members on separate accounts are not affected.
4. **Shadow owner appeals impersonation finding**: appeal creates P2 case. Shadow remains restricted during appeal. If overturned, full restoration.
5. **Coordinated mass reporting attack against a legitimate shadow**: detect report velocity patterns. If >10 reports arrive within 1 hour from accounts with similar characteristics, flag reports as potentially coordinated. Manual review before enforcement.
6. **Shadow used for legitimate pseudonymous journalism/activism**: no special exemption in v1. Standard rules apply. If restricted, appeal path available with context.

---

## 11) Open Decisions

1. Exact fuzzy match threshold for name screening (80% proposed).
2. Whether to implement reverse image matching in v1 or defer.
3. Shadow ban pattern (silently drop messages) vs explicit "your message could not be delivered" — tradeoffs between user experience and harassment prevention.
4. Whether to expose any shadow abuse metrics to the principal (e.g., "your account health is good" vs keeping it invisible).
5. Whether block evasion detection should trigger automatic shadow suspension or just silent blocking.
