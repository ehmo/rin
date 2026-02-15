# Dispute Operations V1

## 1) Purpose

Operationalize the dispute playbook with concrete queue routing, auto-adjudication decision trees, user-facing flows, and staffing model for v1.

Companion docs:
- `docs/operations/DISPUTE_PLAYBOOK_V1.md` (case types, state machines, SLAs)
- `docs/product/SHADOW_PROFILE_UX_V1.md` (shadow abuse rollup)
- `docs/product/BUSINESS_EMPLOYEE_UX_V1.md` (business authority disputes)
- `docs/architecture/OWNERSHIP_STATE_MACHINE_SPEC_V1.md` (channel ownership transitions)

---

## 2) Staffing Model (V1)

### 2.1 Founder + Auto-Adjudication

V1 operates with minimal human staffing:

| Role | Who | Responsibility |
|------|-----|----------------|
| **Auto-adjudicator** | System | Resolves 95%+ confidence cases automatically |
| **Queue operator** | Founder | Reviews escalated cases, sets policy, handles edge cases |
| **On-call** | Founder | Emergency response for P0 incidents (account compromise, business authority) |

### 2.2 Scaling Triggers

Add dedicated T&S staffing when:
- Manual review queue exceeds 20 open cases sustained over 48h.
- Average case resolution time exceeds SLA by 2x.
- Auto-adjudication rate drops below 60% of total cases.

---

## 3) Queue Architecture

### 3.1 Priority Lanes

Cases are routed into priority lanes based on case type and severity:

| Lane | Priority | Case types | SLA |
|------|----------|-----------|-----|
| **P0: Critical** | Immediate | Account compromise, business authority takeover | <15 min triage |
| **P1: High** | Same-day | Channel ownership conflict, impersonation (high severity) | <4h first response |
| **P2: Medium** | Next-day | Channel reassignment, impersonation (low severity), trust appeals | <24h first response |
| **P3: Low** | Best-effort | Merge disputes, general trust questions | <72h first response |

### 3.2 Routing Rules

Automatic lane assignment based on:

```
IF case_type IN (C1, C5) AND severity >= L2:
    → P0 Critical
ELIF case_type = C4 AND impersonation_target_is_rin_user:
    → P1 High
ELIF case_type IN (C1, C2) AND severity = L1:
    → P2 Medium
ELIF case_type = C6 AND trust_score_delta > 30:
    → P1 High
ELIF case_type = C3:
    → P3 Low
ELSE:
    → P2 Medium
```

### 3.3 Escalation Rules

Auto-escalate one lane higher when:
- Case has been in current lane beyond SLA without first response.
- User submits additional evidence after initial triage.
- Case involves a verified business profile.
- Multiple cases from the same principal within 24h (coordinated attack signal).

---

## 4) Auto-Adjudication Decision Trees

### 4.1 Confidence Threshold

- **95%+ confidence**: auto-resolve without human review.
- **Below 95%**: queue for manual review in appropriate lane.

### 4.2 C1: Channel Ownership Conflict

```
1. Both claimants submit OTP proof?
   ├── Only one passes OTP → award to OTP holder (confidence 99%)
   │   → AUTO-RESOLVE
   └── Both pass OTP (SIM swap scenario)
       ├── Check recent device/session history
       │   ├── One claimant has 30+ day device history → favor incumbent (confidence 85%)
       │   │   → QUEUE for manual review
       │   └── Both have recent device history → ambiguous
       │       → QUEUE P1 with hold window (72h)
       └── Neither passes OTP
           → QUEUE P0 (possible system error or fraud)
```

### 4.3 C2: Channel Reassignment (Phone Recycled)

```
1. New claimant passes OTP?
   ├── Yes
   │   ├── Old owner active in last 90 days?
   │   │   ├── Yes → 7-day cooldown enforced, old owner notified
   │   │   │   ├── Old owner disputes within 7 days → QUEUE P2
   │   │   │   └── No dispute after 7 days → transfer (confidence 98%)
   │   │   │       → AUTO-RESOLVE
   │   │   └── No (inactive > 90 days) → transfer (confidence 99%)
   │   │       → AUTO-RESOLVE
   │   └── (continued from cooldown dispute)
   └── No → reject claim, no case opened
```

### 4.4 C3: Mistaken Identity Merge

```
1. Was merge auto-applied (95%+ confidence)?
   ├── Yes → allow instant undo, no case needed (confidence 100%)
   │   → AUTO-RESOLVE (undo)
   └── No (user-confirmed merge)
       ├── User requesting split is the merge confirmer?
       │   ├── Yes → allow split with provenance audit (confidence 95%)
       │   │   → AUTO-RESOLVE
       │   └── No (third party requesting)
       │       → QUEUE P3 for review
```

### 4.5 C4: Impersonation

```
1. Reported profile name matches a verified Rin user?
   ├── Exact match → reduce discoverability immediately
   │   ├── Reporter is the impersonated user → high priority (confidence 90%)
   │   │   → QUEUE P1
   │   └── Reporter is third party → moderate priority
   │       → QUEUE P2
   └── No exact match
       ├── Fuzzy match > 80% → QUEUE P2
       └── No match → dismiss with low evidence (confidence 70%)
           → QUEUE P3 if reporter insists
```

### 4.6 C5: Business Authority Conflict

Always requires human review. Never auto-resolved.

```
1. Freeze high-risk org actions immediately.
2. Check verification chain:
   ├── Challenger has higher domain-level verification → favor challenger
   ├── Both have equal verification → require legal documentation
   └── Challenger has no verification → dismiss unless new evidence
3. → QUEUE P0 or P1 based on business size and impact.
```

### 4.7 C6: Abuse-Driven Trust Dispute

```
1. Trust score drop triggered by:
   ├── Automated abuse signals (spam rate, block rate)
   │   ├── Signals exceed 3x threshold → restrict + QUEUE P2 for appeal
   │   └── Signals exceed 1.5x threshold → warn user, no restriction yet
   │       → AUTO-RESOLVE (warning only)
   └── Manual reports from other users
       ├── 5+ reports from unique users in 24h → restrict + QUEUE P1
       ├── 2-4 reports → warn + QUEUE P3 for monitoring
       └── 1 report → no action, log for pattern detection
           → AUTO-RESOLVE (logged)
```

---

## 5) Hold Windows (Founder Approved)

| Risk tier | Window | Use case |
|-----------|--------|----------|
| **Low** | 24 hours | Simple OTP-resolved conflicts, merge undo requests |
| **Medium** | 48 hours | Channel reassignment after cooldown, moderate impersonation |
| **High** | 72 hours | Competing OTP claims, business authority challenges |

During hold window:
- Affected channels are in `limited` state (visible but not transferable).
- Both parties can submit additional evidence.
- Hold extends by 24h if new material evidence is submitted (max 1 extension).

### Phone Number Cooldown (Founder Approved)

When a phone number is reassigned by carrier:
- **7-day cooldown** before the new owner can claim the number on Rin.
- Old owner is notified immediately when a new claim attempt is detected.
- Old owner can preemptively release the number during cooldown to speed transfer.

---

## 6) User-Facing Dispute Flows

### 6.1 Design Principle: Outcome + Required Actions Only

Users see:
- What happened (plain language, no internal evidence or confidence scores).
- What they need to do.
- Timeline and deadlines.

Users do **not** see:
- Internal confidence scores.
- Evidence from the other party.
- Decision reasoning details.
- System scoring or routing internals.

### 6.2 Security Inbox

Accessible from: Settings > Security, or via push notification deep link.

```
┌─────────────────────────────────┐
│ 🔒 Security                    │
│                                 │
│ Active (2)                      │
│ ┌─────────────────────────────┐ │
│ │ ⚠ Phone number dispute      │ │
│ │ +1 555-0123                 │ │
│ │ Action needed · 47h left    │ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ 🔍 Identity review          │ │
│ │ Waiting for review          │ │
│ │ No action needed            │ │
│ └─────────────────────────────┘ │
│                                 │
│ Resolved (5)                    │
│ [View history]                  │
└─────────────────────────────────┘
```

Each case card shows:
- Case type icon and label
- Affected asset (phone number, profile name, business name)
- Status: "Action needed" / "Waiting for review" / "Resolved"
- Countdown timer if in hold window

### 6.3 Case Detail Screen

```
┌─────────────────────────────────┐
│ ⚠ Phone number dispute          │
│ +1 555-0123                     │
│                                 │
│ What happened                   │
│ Someone else claimed this       │
│ phone number. We've paused      │
│ changes while we verify.        │
│                                 │
│ What's limited now              │
│ • Can't change this number      │
│ • Number hidden from search     │
│                                 │
│ What you need to do             │
│ ┌─────────────────────────────┐ │
│ │ ☐ Verify this is your       │ │
│ │   number  [Verify now]      │ │
│ └─────────────────────────────┘ │
│                                 │
│ Timeline                        │
│ Feb 14  Case opened             │
│ Feb 14  Verification requested  │
│ Feb 17  Deadline for response   │
│                                 │
│ Need help?  [Contact support]   │
└─────────────────────────────────┘
```

Sections:
1. **What happened**: 1-2 sentences in plain language.
2. **What's limited now**: bullet list of current restrictions.
3. **What you need to do**: action checklist with CTAs.
4. **Timeline**: chronological event list with deadlines.
5. **Help link**: escalation path.

### 6.4 Action Types

| Action | CTA | Behavior |
|--------|-----|----------|
| **Verify ownership** | "Verify now" | Triggers OTP or re-verification challenge |
| **Confirm identity** | "This is me" | One-tap confirmation with biometric |
| **Deny activity** | "This wasn't me" | Opens recovery flow |
| **Submit evidence** | "Add information" | Free-text + file upload |
| **Accept outcome** | "OK" | Acknowledges resolution |
| **Appeal** | "Appeal this decision" | Opens appeal form with required fields |

### 6.5 Resolution Notification

When a case resolves, user receives push notification + in-app card:

```
┌─────────────────────────────────┐
│ ✓ Resolved: Phone number        │
│                                 │
│ Your phone number +1 555-0123   │
│ has been verified and restored. │
│                                 │
│ What changed:                   │
│ • Number is active again        │
│ • Search visibility restored    │
│                                 │
│ [OK]                            │
└─────────────────────────────────┘
```

### 6.6 Appeal Flow

If user disagrees with an auto-adjudication or manual decision:

1. Tap "Appeal this decision" from resolved case screen.
2. Required fields: reason (dropdown) + details (free text).
3. Appeal creates a new case in P2 lane, linked to original.
4. One appeal per case. Second appeal requires founder-level escalation.

---

## 7) Notifications

### 7.1 Push Notification Templates

| Trigger | Message | Deep link |
|---------|---------|-----------|
| Case opened (you're affected) | "Security alert: action needed for your [asset]" | Case detail |
| Hold window starting | "We're reviewing a change to your [asset]. No action needed yet." | Case detail |
| Action required | "Verify your [asset] before [deadline]" | Verification flow |
| Case resolved (favorable) | "Resolved: your [asset] is secure" | Resolution card |
| Case resolved (unfavorable) | "Update: a change was made to your [asset]" | Resolution card + appeal |
| Trust restriction applied | "Your account has a temporary restriction" | Case detail |

### 7.2 Notification Rules

- Maximum 3 push notifications per case.
- No notifications between 10pm-8am local time (queue and deliver in morning).
- Batch multiple cases into one notification if they happen within 5 minutes.

---

## 8) Operational Dashboard (Founder View)

### 8.1 Queue Overview

Minimal admin interface for the founder to manage cases:

- **Open cases by lane**: P0 count, P1 count, P2 count, P3 count.
- **Cases requiring action**: sorted by urgency.
- **Auto-resolved today**: count and sample for quality check.
- **SLA health**: cases at risk of breaching SLA.

### 8.2 Case Review Actions

For each case, the operator can:
- View full evidence package (both parties' submissions, system signals).
- Resolve: approve transfer, deny transfer, split merge, dismiss impersonation.
- Escalate: bump lane priority.
- Extend hold: add 24h to hold window.
- Add internal note.

### 8.3 Implementation

V1: simple admin page in the backend service, not in the iOS app.
Future: dedicated admin panel with analytics and trends.

---

## 9) Metrics and Health

### 9.1 Operational Metrics

Track and review weekly:

| Metric | Target | Alert threshold |
|--------|--------|-----------------|
| Auto-adjudication rate | >70% of cases | <50% |
| P0 triage time | <15 min | >30 min |
| P1 first response | <4h | >8h |
| Case resolution time (median) | <24h | >48h |
| Appeal rate | <10% of resolutions | >20% |
| False positive rate (auto-resolve) | <2% | >5% |

### 9.2 Quality Checks

- Weekly sample review: 10% of auto-resolved cases manually audited.
- Monthly: review all appealed cases for pattern detection.
- Quarterly: recalibrate auto-adjudication thresholds based on accumulated data.

---

## 10) Events

- `dispute.queue.routed` — case ID, assigned lane, routing rule matched
- `dispute.queue.escalated` — case ID, old lane, new lane, reason
- `dispute.auto_adjudicated` — case ID, decision, confidence, evidence summary hash
- `dispute.manual_reviewed` — case ID, operator, decision, time to resolution
- `dispute.hold_started` — case ID, window duration, affected assets
- `dispute.hold_extended` — case ID, new deadline, reason
- `dispute.notification_sent` — case ID, user ID, notification type, channel (push/in-app)
- `dispute.appeal_filed` — case ID, original case ID, reason category
- `dispute.sla_breach` — case ID, lane, breached threshold

---

## 11) Open Decisions

1. Whether the founder admin dashboard should be web-based or CLI-based for v1.
2. Exact auto-adjudication threshold tuning after first 100 cases.
3. Whether to expose a public-facing "Trust Center" page explaining dispute policies.
4. Maximum evidence file upload size for user submissions.
5. Whether resolved cases should be visible to the user permanently or archived after 90 days.
