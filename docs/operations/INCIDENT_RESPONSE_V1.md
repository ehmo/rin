# Incident Response and Communication V1

## 1) Purpose

Define the minimal incident response process and user communication templates for a founder-operated service. Lightweight and reactive — formalize as team grows.

Companion docs:
- `docs/plan/outlines/04_OBSERVABILITY_ALERTING_OUTLINE_V1.md` (SLI/SLO framework)
- `docs/architecture/CLOUD_PROVIDER_STRATEGY_V1.md` (monitoring stack)

---

## 2) Monitoring Stack (Minimal)

| Tool | Detects | Alert channel |
|------|---------|--------------|
| **Sentry** | Crashes, unhandled errors, performance issues | Push notification + email |
| **UptimeRobot** | API down, health check failure | Push notification + email + SMS |
| **Hetzner Console** | VM resource exhaustion (CPU, disk) | Email |
| **Managed DB dashboard** | Connection pool exhaustion, slow queries | Email |

No PagerDuty, no Slack bot, no formal on-call rotation. Founder is always on-call.

---

## 3) Severity Classification

| Severity | Definition | Response time |
|----------|-----------|---------------|
| **P0** | Full outage or data safety issue (users can't access app, data loss risk) | <15 minutes |
| **P1** | Major degradation (core feature broken for >10% users) | <1 hour |
| **P2** | Partial degradation (non-core feature broken, performance degraded) | <4 hours |
| **P3** | Minor issue (cosmetic, edge case, low-impact) | Next business day |

---

## 4) Response Procedure

### 4.1 P0/P1 (Immediate)

1. **Acknowledge**: See alert, start investigating.
2. **Assess**: Determine scope (how many users affected, what's broken).
3. **Mitigate**: Apply quickest fix (restart service, rollback deploy, disable feature flag).
4. **Communicate**: Post in-app banner if user-facing impact (see §5).
5. **Resolve**: Fix root cause.
6. **Document**: Write brief incident note (see §4.3).

### 4.2 P2/P3 (Scheduled)

1. **Log**: Create beads issue with details.
2. **Investigate**: Root cause analysis when time permits.
3. **Fix**: Ship fix in next release cycle.
4. **No user communication** unless asked.

### 4.3 Incident Note Template

```markdown
## Incident: [Brief Title]
- **Severity**: P0/P1/P2/P3
- **Duration**: [start time] - [end time] ([minutes] total)
- **Impact**: [what users experienced]
- **Root cause**: [what went wrong]
- **Mitigation**: [what was done immediately]
- **Fix**: [permanent solution]
- **Follow-up**: [any remaining work]
```

Store in `docs/incidents/` directory. One file per incident.

---

## 5) User Communication

### 5.1 Communication Channel: In-App Banner

For user-facing incidents, show a dismissible banner in the app:

```
┌──────────────────────────────────────┐
│ ⚠️ Some features may be temporarily  │
│ unavailable. We're working on it.    │
│                              [Dismiss]│
└──────────────────────────────────────┘
```

Controlled via a server-side feature flag (`incident_banner`). Set banner text remotely without app update.

### 5.2 Communication Templates

**Template 1: Service Degradation (Active)**
> Some features may be slower than usual. We're investigating and will have things back to normal shortly.

**Template 2: Outage (Active)**
> Rin is temporarily unavailable. We're working to restore service as quickly as possible. Your data is safe.

**Template 3: Resolved**
> The issue affecting [feature] has been resolved. Everything should be working normally now. Sorry for the inconvenience.

**Template 4: Planned Maintenance**
> Rin will undergo brief maintenance on [date] at [time]. The app may be unavailable for up to [duration]. Your data will not be affected.

**Template 5: Score Rollback**
> We detected an issue with today's score calculation and have reverted to yesterday's scores. Updated scores will be available tomorrow.

### 5.3 What NOT to Communicate

- Internal technical details (database, servers, infrastructure).
- Root cause analysis to end users (keep in incident notes).
- Timeline promises ("will be fixed in 30 minutes") — say "working on it" instead.
- Blame (third-party services, providers).

---

## 6) Escalation Path

```
Alert detected (Sentry/UptimeRobot)
    ↓
Founder investigates
    ↓
Can fix in <1 hour?
├── Yes → Fix, monitor, done
└── No →
    ├── Data safety at risk? → Take service offline, fix, restore
    └── Degraded but safe? → Set incident banner, fix at pace
```

No external escalation in v1. If team grows:
- Add on-call rotation.
- Add Slack/Discord alert channel.
- Add formal incident commander role.

---

## 7) Open Decisions

1. Whether to add a public status page (e.g., Instatus) before public launch or keep it in-app only.
2. Whether incident notes should be shared with beta testers or kept internal.
3. Whether to set up automated rollback triggers (deploy causes error spike → auto-revert).
