# Rin Monorepo

This repository is organized for product, backend, iOS, infrastructure, and research in one place.

## Top-Level Layout

- `apps/` deployable applications
  - `apps/ios/` iOS client (Swift)
  - `apps/server/` backend services (Go/Fiber)
- `packages/` shared contracts and libraries
  - `packages/contracts/` API/event/schema contracts
  - `packages/go/` shared Go libraries
  - `packages/swift/` shared Swift modules
- `infra/` infrastructure and operations configuration
  - `infra/terraform/`
  - `infra/kubernetes/`
  - `infra/observability/`
  - `infra/environments/{dev,staging,prod}/`
- `docs/` product and engineering documents
  - `docs/product/`
  - `docs/architecture/`
  - `docs/operations/`
  - `docs/simulations/`
  - `docs/research/`
  - `docs/archive/`
- `design/` UX, brand, and visual assets
- `scripts/` local automation and repo tooling scripts

## Start Here

- Interactive guide: `docs/guide/README.md`
- Battle plan: `docs/plan/BATTLE_PLAN_IMPLEMENTATION_V1.md`
- Backlog index: `docs/plan/BACKLOG_INDEX.md`
- Architecture index: `docs/architecture/ARCHITECTURE_MASTER_INDEX.md`
- Monorepo conventions: `docs/architecture/MONOREPO_CONVENTIONS_V1.md`
- Operator runbook: `docs/operations/SYSTEM_RUNBOOK_V1.md`
- Product journey and score: `docs/product/USER_JOURNEY_PLAN.md`, `docs/product/RIN_SCORE_V1.md`

## Workspace Notes

- Keep `AGENTS.md` and `.scratch-pad.md` at repository root.
- Treat docs under `docs/architecture/` as contract-level sources before coding.
