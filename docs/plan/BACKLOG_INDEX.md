# Backlog Index (Beads)

## Program Epic
- `rin-3i0` - Program: Rin end-to-end build plan (v1 launch + future roadmap)

## Epic Map
- `rin-3i0.1` Requirements and decision closure
- `rin-3i0.2` UX journeys and interaction model
- `rin-3i0.3` Design system and visual language
- `rin-3i0.4` Backend architecture implementation planning
- `rin-3i0.5` Data, search, and ranking systems
- `rin-3i0.6` Security, trust, and dispute operations
- `rin-3i0.7` iOS app foundation
- `rin-3i0.8` iOS v1 feature build
- `rin-3i0.9` Infrastructure and deployment platform
- `rin-3i0.10` Cloud provider and on-prem strategy
- `rin-3i0.11` SRE, observability, and run operations
- `rin-3i0.12` App Store readiness and release management
- `rin-3i0.13` Marketing, distribution, and growth
- `rin-3i0.14` Business model and monetization
- `rin-3i0.15` Analytics, metrics, and experimentation
- `rin-3i0.16` Beta and launch program
- `rin-3i0.17` Future roadmap streams (Phase 2-4)
- `rin-3i0.18` Developer ecosystem and superapp platform

## Current Priority Queue (P0)
- `rin-3i0.6.1` Operationalize dispute queue lanes and auto-adjudication tiers
- `rin-3i0.7.1` Define iOS app architecture and module boundaries
- `rin-3i0.12.1` Create App Store policy requirements checklist
- `rin-3i0.16.1` Define beta cohort strategy and acceptance criteria

## Recently Completed (This Session)
- `rin-3i0.2.1` Design complete v1 user journey map with happy/unhappy paths
- `rin-3i0.5.1` Define canonical graph data lifecycle (hot/warm/cold)
- `rin-3i0.4.1` Translate contract docs into service implementation blueprint
- `rin-3i0.1.1` Finalize high-priority architecture open decisions
- `rin-3i0.1.2` Define architecture freeze criteria and sign-off process
- `rin-3i0.4.2` Define command/query API surface outline for all domains
- `rin-3i0.9.1` Define environment topology for dev/staging/prod
- `rin-3i0.9.2` Define CI/CD pipeline stages and quality gates
- `rin-3i0.11.1` Define SLO/SLI dashboard implementation plan

## How To Use This Index
- Inspect program: `bd show rin-3i0`
- See direct children: `bd children rin-3i0`
- List ready issues: `bd ready`
- Set active task: `bd update <id> --status in_progress`
- Close finished task: `bd close <id> --reason done`

## Planned Session Flow
1. Pick one P0 issue.
2. Move it to in-progress.
3. Produce/update linked docs.
4. Close issue only after references are updated.
5. Return to `bd ready` for next item.
