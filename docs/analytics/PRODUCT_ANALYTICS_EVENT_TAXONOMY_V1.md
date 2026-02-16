# Product Analytics Event Taxonomy V1

## 1) Purpose

Define the unified event model for all product, trust, score, and growth analytics. Establishes naming conventions, property standards, and the canonical event catalog for PostHog.

Companion docs:
- `docs/analytics/KPI_HIERARCHY_V1.md` (metrics these events feed)
- `docs/plan/BETA_COHORT_STRATEGY_V1.md` (stage-specific measurement)
- `docs/plan/outlines/04_OBSERVABILITY_ALERTING_OUTLINE_V1.md` (operational telemetry)

---

## 2) Platform and Setup

### 2.1 Analytics Provider

- **PostHog Cloud** (managed SaaS).
- Free tier: 1M events/month (sufficient through Stage 2 beta).
- Migration to self-hosted planned before public launch if data sovereignty requires it.

### 2.2 SDK Integration

- iOS: PostHog Swift SDK via Swift Package Manager.
- Backend: PostHog API (HTTP) for server-side events.
- Event buffer: batch and flush every 30 seconds or 20 events (whichever first).

### 2.3 Environments

| Environment | PostHog project | Purpose |
|-------------|----------------|---------|
| Development | `rin-dev` | Testing event instrumentation |
| Staging | `rin-staging` | Pre-release validation |
| Production | `rin-prod` | Live analytics |

---

## 3) Naming Convention

### 3.1 Format

`object_action` — lowercase, underscore-separated.

Examples:
- `contact_imported`
- `circle_created`
- `score_viewed`
- `dedup_resolved`

### 3.2 Rules

1. Object comes first (noun), action comes second (past tense verb).
2. Use singular nouns: `contact_imported` not `contacts_imported`.
3. Use past tense: `contact_imported` not `contact_import`.
4. No domain prefix: PostHog groups handle categorization.
5. Maximum 3 segments: `dedup_suggestion_dismissed` (not deeper).
6. Consistent verb vocabulary:

| Verb | Meaning |
|------|---------|
| `viewed` | User saw a screen/element |
| `tapped` | User tapped a button/control |
| `created` | New entity created |
| `updated` | Existing entity modified |
| `deleted` | Entity removed |
| `imported` | Data brought into Rin |
| `resolved` | Pending item addressed |
| `dismissed` | User chose to skip/ignore |
| `completed` | Multi-step flow finished |
| `failed` | Operation did not succeed |
| `granted` | Permission given |
| `denied` | Permission refused |

---

## 4) User Identification

### 4.1 Identity Model

- **Distinct ID**: Rin principal ID (stable across devices).
- **Anonymous ID**: Generated on first app launch (pre-auth).
- **Merge**: Anonymous ID merged to principal ID after phone verification.

### 4.2 Super Properties

Set once, attached to every event automatically:

| Property | Type | Example |
|----------|------|---------|
| `$app_version` | string | `1.0.0` |
| `$os_version` | string | `18.2` |
| `device_model` | string | `iPhone 15 Pro` |
| `user_class` | string | `personal` / `business`. Maps to architecture `profile_class` enum: `personal` = `single`, `business` = `business`. Shadow and employee classes are tracked via separate `profile_class` property on profile-specific events. See `docs/architecture/PROFILE_CLASS_CONTRACT_V1.md`. |
| `profile_count` | int | `2` |
| `beta_stage` | string | `stage_1` / `stage_2` / `stage_3` / `public` |
| `account_age_days` | int | `14` |
| `contacts_count` | int | `342` |
| `circles_count` | int | `5` |

---

## 5) Event Catalog

### 5.1 Onboarding

| Event | Properties | Trigger |
|-------|-----------|---------|
| `onboarding_started` | `source` (organic/invite/ad) | App first launch |
| `onboarding_screen_viewed` | `screen_id` (S1-S12), `screen_name` | Each onboarding screen shown |
| `onboarding_screen_completed` | `screen_id`, `duration_ms` | User advances past screen |
| `phone_verification_requested` | `country_code` | OTP sent |
| `phone_verification_completed` | `duration_ms`, `attempt_count` | OTP verified |
| `phone_verification_failed` | `error_type` | OTP failed |
| `permission_prompted` | `permission_type` (contacts/notifications/tracking) | System dialog shown |
| `permission_granted` | `permission_type` | User allowed |
| `permission_denied` | `permission_type` | User denied |
| `onboarding_completed` | `duration_ms`, `screens_viewed`, `permissions_granted[]` | User reaches home |
| `onboarding_abandoned` | `last_screen_id`, `duration_ms` | App killed during onboarding |

### 5.2 Contacts

| Event | Properties | Trigger |
|-------|-----------|---------|
| `contact_import_started` | `source` (phone/manual), `estimated_count` | Import begins |
| `contact_imported` | `source`, `has_phone`, `has_email`, `has_photo` | Single contact ingested |
| `contact_import_completed` | `total_count`, `duration_ms`, `new_count`, `updated_count` | Batch import finishes |
| `contact_import_failed` | `error_type`, `contacts_processed` | Import errors out |
| `contact_viewed` | `contact_id`, `has_enrichment`, `profile_class` | Contact detail opened |
| `contact_created` | `source` (manual), `fields_filled` | Manual contact add |
| `contact_updated` | `field_changed`, `source` (manual/sync/enrichment) | Contact field modified |
| `contact_deleted` | `contact_id`, `reason` | Contact removed |
| `contact_sync_triggered` | `trigger` (event/background/manual), `changes_detected` | Sync cycle runs |
| `contact_sync_completed` | `added`, `updated`, `removed`, `duration_ms` | Sync cycle finishes |
| `contact_search_performed` | `query_length`, `result_count` | User searches contacts |

### 5.3 Deduplication

| Event | Properties | Trigger |
|-------|-----------|---------|
| `dedup_suggestion_shown` | `confidence_tier` (auto/review/low), `match_type` | Dedup card displayed |
| `dedup_resolved` | `action` (merge/dismiss/skip), `confidence`, `duration_ms` | User acts on suggestion |
| `dedup_auto_merged` | `confidence`, `field_count` | Auto-merge at 95%+ |
| `dedup_batch_shown` | `suggestion_count`, `auto_merged_count` | Dedup review screen opened |
| `dedup_batch_completed` | `merged_count`, `dismissed_count`, `duration_ms` | User finishes review batch |

### 5.4 Circles

| Event | Properties | Trigger |
|-------|-----------|---------|
| `circle_created` | `name`, `type` (custom/imported), `color`, `emoji` | New circle created |
| `circle_updated` | `field_changed` (name/color/emoji/policy) | Circle settings modified |
| `circle_deleted` | `member_count`, `circle_age_days` | Circle removed |
| `circle_member_added` | `circle_name`, `method` (manual/bulk/import) | Contact added to circle |
| `circle_member_removed` | `circle_name` | Contact removed from circle |
| `circle_policy_changed` | `circle_name`, `field`, `old_state`, `new_state` | Access control toggle changed |
| `circle_viewed` | `circle_name`, `member_count` | Circle detail screen opened |

### 5.5 Profiles and Shadow Profiles

| Event | Properties | Trigger |
|-------|-----------|---------|
| `profile_viewed` | `profile_type` (primary/shadow), `is_own_profile` | Profile screen opened |
| `profile_updated` | `field_changed`, `profile_type` | Profile field modified |
| `profile_photo_changed` | `profile_type` | Photo uploaded/changed |
| `shadow_profile_created` | `type` (professional/personal/anonymous) | New shadow created |
| `shadow_profile_switched` | `from_type`, `to_type` | User switches active profile |
| `shadow_profile_deleted` | `type`, `age_days` | Shadow profile removed |
| `identity_reveal_initiated` | `shadow_type`, `contact_count` | Opt-in reveal started |
| `identity_reveal_completed` | `contacts_revealed_to` | Reveal confirmed |

### 5.6 Score

| Event | Properties | Trigger |
|-------|-----------|---------|
| `score_viewed` | `score_value`, `previous_value`, `delta` | Score screen opened |
| `score_component_viewed` | `component` (quality/position/stability/trust) | Component bar tapped |
| `score_updated` | `old_value`, `new_value`, `delta`, `formula_version` | Daily score batch published |
| `score_trend_viewed` | `period_days` | Score history/trend viewed |

### 5.7 Trust and Disputes

| Event | Properties | Trigger |
|-------|-----------|---------|
| `dispute_submitted` | `case_type` (C1-C6), `evidence_attached` | User files dispute |
| `dispute_resolved` | `case_type`, `outcome`, `resolution_method` (auto/manual), `duration_hours` | Dispute closed |
| `report_submitted` | `report_type`, `target_profile_class` | User reports profile/content |
| `block_created` | `target_profile_class` | User blocks someone |
| `block_removed` | `target_profile_class` | User unblocks |

### 5.8 Premium and Monetization

| Event | Properties | Trigger |
|-------|-----------|---------|
| `paywall_viewed` | `trigger` (feature/upsell/settings), `feature_requested` | Paywall screen shown |
| `paywall_dismissed` | `duration_ms` | User closes paywall |
| `subscription_started` | `plan` (monthly/annual), `price`, `trial` | Purchase completed |
| `subscription_cancelled` | `plan`, `tenure_days`, `reason` | Subscription cancelled |
| `subscription_renewed` | `plan`, `period_count` | Auto-renewal processed |
| `premium_feature_used` | `feature` (who_viewed/enrichment_alerts/how_am_i_stored) | Premium feature accessed |

### 5.9 Growth and Virality

| Event | Properties | Trigger |
|-------|-----------|---------|
| `invite_sent` | `method` (sms/share_sheet/link), `recipient_is_contact` | User sends invite |
| `invite_accepted` | `inviter_id`, `method` | Invited user completes onboarding |
| `app_rating_prompted` | `trigger`, `session_count` | Rating dialog shown |
| `app_rating_submitted` | `rating` | User rates in App Store |
| `app_shared` | `method`, `content_type` | Share sheet used |

### 5.10 Navigation and Engagement

| Event | Properties | Trigger |
|-------|-----------|---------|
| `app_opened` | `source` (cold/warm/push/deeplink) | App foregrounded |
| `app_backgrounded` | `session_duration_ms`, `screens_viewed` | App backgrounded |
| `tab_switched` | `from_tab`, `to_tab` | Bottom tab navigation |
| `settings_viewed` | — | Settings screen opened |
| `feedback_submitted` | `method` (shake/settings), `has_screenshot` | User sends feedback |

---

## 6) Property Standards

### 6.1 Common Properties

Attached to all events automatically (beyond super properties):

| Property | Type | Description |
|----------|------|-------------|
| `timestamp` | ISO 8601 | Event time (PostHog handles) |
| `session_id` | string | PostHog session tracking |
| `screen_name` | string | Current screen when event fired |

### 6.2 Property Types

- Strings: lowercase, underscore-separated.
- Booleans: `true`/`false`.
- Numbers: integers or floats (no strings).
- Arrays: JSON arrays for multi-value properties (e.g., `permissions_granted[]`).
- Duration: always in `_ms` (milliseconds).
- Counts: always integers.

### 6.3 PII Rules

**Never send as event properties:**
- Phone numbers
- Email addresses
- Contact names
- Physical addresses
- Any field from the user's contact book

**Use hashed IDs only** for cross-referencing contacts in analytics.

---

## 7) Funnel Definitions

### 7.1 Onboarding Funnel

```
onboarding_started
  → phone_verification_completed
  → permission_granted (contacts)
  → contact_import_completed
  → onboarding_completed
```

### 7.2 First Value Funnel

```
onboarding_completed
  → dedup_suggestion_shown
  → dedup_resolved (first action)
  → score_viewed (first score view)
```

### 7.3 Premium Conversion Funnel

```
paywall_viewed
  → subscription_started (trial or paid)
  → premium_feature_used
  → subscription_renewed
```

### 7.4 Viral Loop

```
invite_sent
  → invite_accepted
  → onboarding_completed (invited user)
  → invite_sent (invited user sends their own invite)
```

---

## 8) Implementation Priority

### 8.1 Stage 1 (Core Loop Validation)

Must-have events (instrument before first beta tester):
- All onboarding events (5.1)
- `contact_import_started`, `contact_import_completed`, `contact_import_failed`
- `dedup_suggestion_shown`, `dedup_resolved`, `dedup_auto_merged`
- `score_viewed`, `score_updated`
- `app_opened`, `app_backgrounded`
- `permission_prompted`, `permission_granted`, `permission_denied`

### 8.2 Stage 2 (Retention Measurement)

Add:
- All circle events (5.4)
- All contact detail events (`contact_viewed`, `contact_updated`, `contact_search_performed`)
- Profile events (5.5)
- `feedback_submitted`
- `tab_switched`

### 8.3 Stage 3 (Growth Mechanics)

Add:
- All premium/monetization events (5.8)
- All growth/virality events (5.9)
- All trust/dispute events (5.7)
- `app_rating_prompted`, `app_rating_submitted`

---

## 9) PostHog Configuration

### 9.1 Groups

| Group type | Key | Purpose |
|-----------|-----|---------|
| `beta_cohort` | `stage_1`/`stage_2`/`stage_3` | Cohort comparison |

### 9.2 Feature Flags

PostHog feature flags used for:
- Premium paywall A/B test (Stage 2).
- Onboarding flow variants.
- Score visibility experiments.

### 9.3 Session Recording

- Enabled for Stage 1 testers (opt-in).
- Disabled by default in Stage 2+.
- Never record keyboard input or contact data.

---

## 10) Open Decisions

1. Whether to use PostHog's group analytics for circle-level metrics or keep all metrics user-level.
2. Whether `contact_imported` should fire per-contact (high volume) or only as batch summary (`contact_import_completed`).
3. Whether to track scroll depth on key screens (contact list, dedup review).
4. Whether to implement server-side event validation before PostHog ingestion.
5. Session recording data retention policy (30 days vs 90 days).
