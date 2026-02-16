# Monorepo Conventions V1

## 1) Purpose

Define stable conventions for organizing and evolving the Rin monorepo.

Goals:
- keep long-term structure predictable,
- reduce architectural drift,
- make future code additions straightforward,
- preserve clear ownership boundaries.

---

## 2) Repository Principles

1. Domain-first structure over framework-first structure.
2. Contracts before implementation.
3. One source of truth per concern.
4. Keep root clean and navigable.
5. Prefer additive changes; avoid destructive restructures.

---

## 3) Top-Level Directory Contract

- `apps/`: deployable apps
  - `apps/server/`: backend services and workers (Go)
  - `apps/ios/`: iOS app (Swift)
- `packages/`: shared code and schemas
  - `packages/contracts/`: API/event/schema contracts
  - `packages/go/`: shared Go packages
  - `packages/swift/`: shared Swift modules
- `infra/`: infrastructure and environment config
- `docs/`: product, architecture, operations, research, simulations, archive
- `design/`: UX, brand, assets
- `scripts/`: automation scripts

Rules:
- Do not add new top-level folders without architecture review.
- If a folder does not fit this model, it likely belongs under an existing domain.

---

## 4) Naming Conventions

## 4.1 Files and Folders

- Use lowercase with hyphen or underscore only when needed.
- Contract/spec docs use uppercase suffix pattern: `*_V1.md`.
- Operational runbooks use `*_RUNBOOK_*.md`.

## 4.2 Service Names

- Use domain names (`identity`, `channel`, `policy`, `security`, `score`).
- Avoid transport/framework names in service names.

## 4.3 Event Names

- Dot-separated past-tense format: `<domain>.<entity>.<verb_past_tense>`.
- Maintain naming consistency with `EVENT_CONTRACT_CATALOG_V1.md`.

---

## 5) Documentation Conventions

1. Product intent docs in `docs/product/`.
2. System contracts in `docs/architecture/`.
3. Day-2/incident docs in `docs/operations/`.
4. Simulation outputs in `docs/simulations/`.
5. Source corpus and external captures in `docs/research/`.

Required updates when changing architecture:
- Update `docs/architecture/ARCHITECTURE_MASTER_INDEX.md`.
- Update impacted contract docs.
- Add a short decision/change note to `.scratch-pad.md`.

---

## 6) Service and Data Boundaries

Use `docs/architecture/DATA_MODEL_BOUNDARIES_V1.md` as authority.

Rules:
1. A service only writes aggregates it owns.
2. Cross-domain effects happen via events/commands.
3. Projection stores never become canonical source.
4. Ownership transitions must follow state machine contract.

---

## 7) Code Placement Conventions (When Implementation Starts)

## 7.1 Server (Go)

- `apps/server/cmd/` for service/worker entrypoints.
- `apps/server/internal/` for service-private code.
- `packages/go/` for reusable, non-service-specific libraries.
- Shared contracts imported from `packages/contracts/`.

## 7.2 iOS (Swift)

**Note:** iOS feature packages may be organized under `packages/swift/` or `apps/ios/Features/` — the exact structure will be finalized at implementation. Proto/contract files live in `packages/contracts/` (canonical path).

- `apps/ios/App/` for app shell and navigation.
- `apps/ios/Features/` for product features.
- `packages/swift/` for shared Swift modules.
- Generated/hand-authored API contracts sourced from `packages/contracts/`.

## 7.3 Contracts

- Keep transport-agnostic contracts in `packages/contracts/`.
- Version contract changes explicitly.
- Breaking changes require migration notes.

---

## 8) Infrastructure Conventions

- `infra/environments/{dev,staging,prod}/` is authoritative for environment differences.
- Keep reusable IaC modules in `infra/terraform/modules` (when introduced).
- Keep deployment specs in `infra/kubernetes/` by service and environment overlay.
- Keep observability config in `infra/observability/` aligned with runbook metrics.

---

## 9) Testing and Quality Conventions

Baseline expectations when coding starts:

1. Unit tests for domain logic.
2. Contract tests for API/events.
3. Replay/idempotency tests for event consumers.
4. Ownership-state transition matrix tests.
5. Profile class enforcement tests (`shadow` non-ranked/non-owning).

CI policy (future):
- contract validation gates first,
- build/test per app/package,
- lint/format checks,
- migration/replay safety checks for critical changes.

---

## 10) Change Management for Structure

Before restructuring directories:
1. Document reason and impact.
2. Show mapping old -> new paths.
3. Update indexes and references in same change.
4. Avoid moving code and changing behavior in one step.

Monorepo structure changes should be rare and explicit.

---

## 11) Security and Secrets Conventions

1. No secrets in repo.
2. Environment-specific secret references only; values in secret manager.
3. PII handling must follow event/privacy constraints in architecture docs.
4. Incident patches must not bypass ownership/state-machine contracts.

---

## 12) Versioning and Freeze Policy

- Architecture contracts remain versioned (`V1`, `V2`, ...).
- Use freeze markers (e.g. `ARCH_FREEZE_V1`) before implementation starts.
- During a freeze, only clarifications/fixes allowed; no semantic drift without explicit version bump.

---

## 13) Open Questions

1. Preferred package manager/workspace strategy once server and iOS code exist.
2. Whether to keep one shared contracts format or dual-format generated artifacts.
3. Whether to enforce per-domain ownership CODEOWNERS when team grows.
