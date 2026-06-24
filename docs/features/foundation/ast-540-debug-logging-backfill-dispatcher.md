# AST-540 — Debug logging backfill: dispatcher

<!-- linear-archive: AST-540 archived 2026-06-23 -->

## Linear archive (AST-540)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-540/debug-logging-backfill-dispatcher  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Susan runs scheduled and manual dispatch batches with **debug** enabled while tuning pipelines. At the **dispatcher** layer she currently sees batch-level claim counts and final summary dicts, but not UAT-grade traceability for each batch iteration, each claimed entity, or why a run stopped early. This ticket backfills the **AST-538** debug logging contract across dispatcher orchestration — claim, loop drain, scheduler handoff, and debug-flag passthrough to downstream runners — so console output shows **what was claimed and how each batch pass concluded**, not only aggregate totals.

## Functional scope

* Apply the shared debug helper delivered by **AST-538** to every dispatcher code path that reads or propagates the dispatch task **debug** flag.
* **Task start:** When debug is on, log dispatch task identity (task key, candidate), available count, new batch id, auto vs manual (click) mode, and whether the task uses a multi-hop chain ledger.
* **Claim phase:** After entities are claimed (jobs, companies, board searches, or single-candidate runs), emit an index header per claimed item using universal `index N/M`, primary identifier (slug, job id, board id, or candidate id as applicable), and claim outcome. Follow with `|` detail lines for claim context: entity type, trigger state, batch-call vs per-entity mode, chunk-exhaust split when applicable, and batch size limits.
* **Batch loop drain:** When a dispatch task runs multiple batches in one thread (loop mode), each iteration gets its own index header and detail showing processed/passed/failed counts for that pass and why the loop continues or stops (min_count not met, drain flag, max_runs reached, zero processed).
* **Skip and guard paths:** When debug is on, log structured detail (not only scheduler INFO) for early exits: network unreachable before claim, missing candidate or API key, below min_count on first pass, circuit-breaker auto-disable trigger context.
* **Batch end:** Retain batch summary counts, but only **after** per-index/per-iteration detail; summary must not be the only debug output for a non-empty batch.
* **Passthrough:** Continue passing **debug** unchanged into consult, roster, and agent runners — their step-by-step detail is owned by sibling backfill tickets (**AST-541**–**AST-546**).
* **Migration:** Retire hand-rolled `[DEBUG]` INFO lines in touched dispatcher files when otherwise editing; grandfather untouched lines until the file is next modified (per **AST-538** decision).

## Boundaries

* Does **not** instrument consult, roster, agent, gazer, builder, or external LLM modules — those are separate backfill tickets.
* Does **not** change hop-boundary logging from **AST-527** / **AST-530** (agent chain hops).
* Does **not** add debug-logging requirements on React/UI or admin API handlers.
* Does **not** change dispatch business logic, batch sizes, ledger schema, or scheduler threading model.
* Does **not** add Betty log-string tests; Radia enforces instrumentation on review.
* Data layer remains **no log** per Code Rules.

## Acceptance criteria

1. A representative **inflow_discovery** (or other company-batch) dispatch with **debug=True** on the task row shows, **before** the batch summary line, index headers and `|` detail for each claimed entity in that pass plus loop-iteration context when multiple passes run.
2. A **job** dispatch using batch-call mode with chunk exhaustion shows debug headers for each chunk (index, size, task key) before downstream consult output.
3. A dispatch skipped for network unreachable or below **min_count** with **debug=True** emits `|` detail explaining the skip reason; with **debug=False** behavior is unchanged from today.
4. **debug=False** produces no new debug-only log lines on touched dispatcher paths (spot-check one company batch and one job batch).
5. Radia review treats missing or inadequate debug instrumentation on touched dispatcher **debug** surfaces as **fix-now** per **AST-538**.

## Dependencies and blockers

* **AST-538** — Code Rules contract, shared debug helper, review rubric (must complete first; ticket is **blockedBy** this relation).

## Open questions

none.

### Comments

#### chuckles — 2026-06-14T03:30:14.708Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-540 (parent) | ftr/ast-540-debug-logging-backfill-dispatcher |
| AST-615 | sub/AST-540/AST-615-dispatcher-claim-loop-guard-debug |

**Epic worktree:** `astral-AST-540/` — one active sub checked out at a time.

**Parent:** AST-540

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
