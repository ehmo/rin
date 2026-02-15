# Data Retention and Deletion Policy V1

## 1) Purpose

Define the data lifecycle, retention periods, anonymization procedures, and deletion flows for compliance with Apple App Store requirements and GDPR/CCPA.

Companion docs:
- `docs/plan/APPSTORE_COMPLIANCE_CHECKLIST_V1.md` (compliance requirements)
- `docs/operations/SHADOW_ANTI_ABUSE_POLICY_V1.md` (abuse data retention)

---

## 2) Deletion Model: Anonymize + Purge

When a user requests account deletion:

```
User requests deletion
    ↓ (immediate)
Step 1: Anonymize PII
    - Replace display name with hash
    - Replace phone numbers with hashes
    - Replace email addresses with hashes
    - Replace profile photos with default
    - Replace usernames with "[deleted-{hash}]"
    ↓ (immediate)
Step 2: Deactivate account
    - Mark principal as deleted
    - Revoke all auth tokens
    - Remove from search indexes
    - Stop all sync/enrichment
    ↓ (30-day grace period)
Step 3: Purge originals
    - Delete original PII from all storage
    - Delete from backups (next backup rotation)
    - Retain anonymized graph structure
    ↓
Complete
```

### 2.1 What Gets Anonymized (Immediate)

| Data | Anonymization method |
|------|---------------------|
| Display name | SHA-256 hash, truncated to 8 chars |
| Phone numbers | SHA-256 hash |
| Email addresses | SHA-256 hash |
| Profile photos | Deleted (replaced with default avatar) |
| Usernames | `[deleted-{8-char-hash}]` |
| Bio/description | Deleted |
| Circle names | Preserved (non-PII) |
| Access policies | Preserved (non-PII) |

### 2.2 What Gets Retained (Anonymized)

| Data | Retention period | Reason |
|------|-----------------|--------|
| Anonymized graph edges | 180 days | Analytics: network density metrics |
| Anonymized score history | 90 days | Analytics: score distribution calibration |
| Dispute/abuse records | 365 days | Safety: prevent re-registration abuse |
| Aggregated analytics events | Indefinite | Product metrics (no PII in events) |
| Circle structure (anonymized) | 90 days | Analytics: circle adoption patterns |

### 2.3 What Gets Purged (30 Days)

| Data | Purge method |
|------|-------------|
| Original PII (pre-anonymization) | Hard delete from all tables |
| Contact book data (imported contacts) | Hard delete |
| Enrichment data linked to user | Hard delete |
| Session data and tokens | Hard delete |
| Push notification tokens | Hard delete |
| Mutation queue entries | Hard delete |

---

## 3) Account Recovery (Grace Period)

### 3.1 30-Day Recovery Window

- During the 30-day grace period, user can log in and cancel deletion.
- PII has already been anonymized — recovery restores from a "deletion hold" snapshot.
- Deletion hold snapshot: encrypted copy of PII stored in separate table.
- After 30 days: deletion hold snapshot purged, recovery impossible.

### 3.2 Recovery Flow

```
User logs in during grace period
    ↓
Show: "Your account is scheduled for deletion on [date]. Cancel?"
    ↓ (user cancels)
Restore PII from deletion hold snapshot
    ↓
Re-index in search
    ↓
Resume sync and enrichment
    ↓
Account fully active
```

---

## 4) Retention Schedule by Data Type

| Data category | Active retention | Post-deletion retention | Storage |
|--------------|-----------------|------------------------|---------|
| **Identity (PII)** | While active | 30 days (hold), then purge | PostgreSQL |
| **Contact graph** | While active | 180 days (anonymized) | PostgreSQL → Iceberg |
| **Score data** | 90 days rolling | 90 days (anonymized) | PostgreSQL |
| **Analytics events** | Indefinite | Indefinite (no PII) | PostHog Cloud |
| **Crash reports** | 90 days | 90 days | Sentry |
| **Dispute records** | 365 days | 365 days (anonymized) | PostgreSQL |
| **Backups** | 30 days rolling | Next rotation cycle | Object storage |
| **Contact book imports** | While active | 30 days, then purge | PostgreSQL |
| **Enrichment data** | While active | 30 days, then purge | PostgreSQL |
| **Photos** | While active | Immediate delete | Object storage |
| **Auth tokens** | While active | Immediate delete | Keychain/server |

---

## 5) Right to Export (GDPR Article 20)

### 5.1 Data Export Contents

On user request, provide a downloadable archive containing:
- Profile data (name, email, phone, bio).
- Contact list (names and identifiers only — not other people's PII).
- Circle names and membership.
- Score history (last 90 days).
- Access policy settings.
- Account activity log (login history, major actions).

### 5.2 Export Format

- JSON file with clear schema.
- Delivered via in-app download or secure email link.
- Available within 72 hours of request.
- Link expires after 7 days.

---

## 6) Third-Party Data Processors

| Processor | Data shared | DPA required | Retention |
|-----------|-----------|-------------|-----------|
| PostHog Cloud | Anonymous analytics events | Yes | Per PostHog policy |
| Sentry | Crash reports (anonymized principal ID) | Yes | 90 days |
| Managed Postgres provider | All database data | Yes | Per provider policy |
| NATS Cloud (if used) | Event payloads (transient) | Yes | JetStream retention |

---

## 7) Automated Deletion Jobs

### 7.1 Scheduled Jobs

| Job | Frequency | Action |
|-----|-----------|--------|
| Grace period expiry | Daily | Purge PII for accounts past 30-day grace |
| Anonymized data expiry | Weekly | Purge anonymized graph data past 180 days |
| Score history trim | Weekly | Remove score data older than 90 days |
| Dispute record trim | Monthly | Purge dispute records older than 365 days |
| Backup rotation | Daily | Remove backups older than 30 days |
| Orphan media cleanup | Weekly | Delete photos not referenced by any active record |

### 7.2 Deletion Verification

- Each deletion job logs: record count deleted, execution time, errors.
- Monthly audit: verify no PII exists past retention periods.
- Spot-check: randomly sample deleted accounts to confirm purge completeness.

---

## 8) Implementation Notes

### 8.1 Contact Book Data (Imported Contacts)

Imported contacts belong to the importing user, not the contact subjects. On user deletion:
- Delete all imported contacts immediately.
- Do NOT notify contacts that they were in someone's imported list (privacy).
- Graph edges derived from imports: anonymize, retain for analytics period.

### 8.2 Cross-User Data

When user A deletes their account:
- User B still sees their own copy of contact data for A (B's phone book).
- Enrichment data A contributed is anonymized.
- Mutual connection graph edges are anonymized on A's side.

---

## 9) Open Decisions

1. Whether the 30-day grace period is sufficient or should be 14 days (faster deletion, less recovery time).
2. Whether anonymized graph data retention (180 days) is acceptable or should be shorter.
3. Whether to offer "delete just my data but keep my account" vs "full account deletion".
4. Whether deletion should cascade to shadow profiles immediately or offer per-profile deletion.
