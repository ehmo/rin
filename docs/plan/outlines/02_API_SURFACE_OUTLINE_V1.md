# API Surface V1 (Planning Spec)

## 1. Purpose
Define the command/query API boundaries for v1 domains before endpoint-level implementation.

Linked beads:
- `rin-3i0.4.2`
- `rin-3i0.7.3`

## 2. API Design Principles
1. Command/query separation for clarity and replay safety.
2. Idempotent command handling by default.
3. Explicit versioning and backward-compatible evolution.
4. Class-aware behavior (single, shadow, business, employee).
5. Outbox-driven event publication for every accepted command.

## 3. Domain Command Surface

### 3.1 Identity and Channels
Commands:
- `RegisterUser`
- `VerifyChannelOwnership`
- `SetPrimaryChannel`
- `AddChannel`
- `RemoveChannel`
- `InitiateChannelRecovery`

Invariants:
- Unverified channels cannot be promoted to primary.
- Shadow profiles cannot directly own channels.

### 3.2 Contacts and Ingestion
Commands:
- `UploadContactSnapshot`
- `SubmitContactDelta`
- `AcknowledgeIngestionResult`
- `RequestContactMergeReversal`

Invariants:
- Raw ingestion preserved for reversibility.
- Canonical promotion must not leak non-shared private attributes.

### 3.3 Circles and Access Policies
Commands:
- `CreateCircle`
- `UpdateCircle`
- `AssignContactToCircle`
- `SetAttributeAccessPolicy`
- `RequestAttributeAccess`
- `RespondToAccessRequest`

Invariants:
- Default policy is deny-until-allowed for sensitive attributes.
- Circle naming does not alter internal ranking semantics.

### 3.4 Profiles and Classes
Commands:
- `CreateShadowProfile`
- `UpdateProfilePresentation`
- `CreateBusinessProfile`
- `InviteEmployee`
- `GrantEmployeeRole`
- `RevokeEmployeeRole`

Invariants:
- Shadow profiles excluded from ranking input/output.
- Business authority transitions require elevated verification.

### 3.5 Disputes, Trust, and Security
Commands:
- `OpenOwnershipDispute`
- `SubmitDisputeEvidence`
- `ApplyProtectiveHold`
- `ResolveDispute`
- `ReportAbuse`
- `AcknowledgeSecurityNotice`

Invariants:
- Dispute transition rules follow ownership state machine.
- Protective holds must produce deterministic side effects.

## 4. Query Surface (Read Models)

### 4.1 User and Identity
Queries:
- `GetMyProfile`
- `GetMyChannels`
- `GetVerificationState`
- `GetSecurityState`

### 4.2 Contacts and Circles
Queries:
- `ListContacts`
- `GetContactDetail`
- `ListCircles`
- `GetCircleMembers`
- `GetAccessPolicyPreview`

### 4.3 Discovery and Ranking
Queries:
- `SearchProfiles`
- `GetSuggestedConnections`
- `GetScoreSummary`
- `GetScoreExplanation`

### 4.4 Trust and Disputes
Queries:
- `ListDisputes`
- `GetDisputeStatus`
- `GetAuditTrail`
- `GetRecoveryTimeline`

## 5. API Contract Policies

### 5.1 Idempotency
- All write commands require idempotency key.
- Server stores request fingerprint and response envelope for replay window.
- Duplicate idempotency key with changed payload returns conflict.

### 5.2 Versioning
- Stable major version path (`/v1`) with additive minor evolution.
- Breaking changes require `/v2` and migration compatibility window.

### 5.3 Pagination and Consistency
- Cursor-based pagination for lists.
- Query responses include projection version and freshness timestamp.

### 5.4 Error Taxonomy
Canonical classes:
- `validation_error`
- `auth_error`
- `permission_denied`
- `conflict`
- `rate_limited`
- `temporarily_unavailable`
- `state_transition_forbidden`
- `policy_violation`

Error payload minimum:
- `error_code`
- `message`
- `retryable` (bool)
- `correlation_id`

## 6. Event and Outbox Mapping
For each successful command:
1. persist state change,
2. append outbox record,
3. publish domain event,
4. update read models asynchronously.

Minimum event subjects by domain:
- `identity.*`
- `channel.*`
- `contact.*`
- `policy.*`
- `profile.*`
- `security.*`
- `trust.*`
- `score.*`

See canonical event structure:
- `docs/architecture/EVENT_CONTRACT_CATALOG_V1.md`

## 7. Security and Access Model
- AuthN via session/token layer (implementation TBD).
- AuthZ enforced at command handler boundary.
- Profile-class constraints checked before policy evaluation.
- Sensitive queries require elevated audit logging.

## 8. iOS Integration Contract
- iOS consumes query projections only; no direct event coupling.
- Commands return accepted/rejected status with correlation ID.
- Optimistic UI allowed only for explicitly safe commands.

## 9. Out of Scope (This Doc)
- Exact HTTP route list.
- DTO field-by-field schema.
- SDK-level client abstractions.

## 10. Exit Criteria
This planning spec is complete when:
- domain command/query inventory is accepted,
- idempotency/versioning/error policies are locked,
- mapping to event/outbox flow is approved,
- `rin-3i0.4.2` is ready for endpoint-level breakdown.
