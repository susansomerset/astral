# AST-1129 — Manage Email — select inbox messages and Land Meteorite

<!-- linear-archive: AST-1129 archived 2026-08-11 -->

## Linear archive (AST-1129)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1129/manage-email-select-inbox-messages-and-land-meteorite  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Manage Email already lets Archie browse the shared Astral inbox and Create a meteorite job from a matched row, but bulk landing still forces one-by-one Create (or waiting on dispatcher `gaze_email`). This epic adds multi-select + **Land Meteorite** so Archie can choose specific inbox messages and run the **same** `gaze_email` ingest outcomes for those ids only — bind / shape-route / Ruth parse / scrape / per-candidate dedupe / **METEORITE_NEW** / archive — without inventing a second pipeline or waiting for a full mailbox poll. When Land Meteorite ships, the per-row **Create** control is retired.

## Functional scope

1. **Multi-select on Manage Email inbox list** — Archie can select multiple current inbox messages on Manage Email (including select-all / clear selection).
2. **Land Meteorite action** — With one or more messages selected, Archie can click **Land Meteorite**. The action targets **only those selected message ids** (not the whole inbox).
3. **Selected-ids** `gaze_email` **ingest** — Land Meteorite invokes the shared core `gaze_email` ingest path for those ids (the callable path left by **AST-1128**): same bind / route / scrape / dedupe / create / archive-or-ignore behavior as dispatcher `gaze_email`, not a forked runner and not the old Create strip/extract path.
4. **Unbound / unmatched selected messages** — Selected messages that do not bind to a candidate (or are ambiguous) are **skipped** with explicit operator feedback; they do not fail or block the rest of the batch.
5. **Retire per-row Create** — When Land Meteorite ships, remove/hide the Manage Email per-row **Create** control (AST-1048/AST-1051 strip/extract create-job UX). Land Meteorite is the Manage Email landing action going forward.
6. **Operator-visible batch outcome** — After Land Meteorite, Archie sees clear success / skip / failure feedback for the selection without leaving Manage Email.
7. **Debug observability (backend)** — When `debug=True` on touched Land Meteorite / selected-ids ingest paths, log what was found and what was recorded per selected message and per create/skip/archive/ignore outcome (Style D index headers with `index N/M`, primary id, outcome; working detail lines prefixed with two spaces, pipe, two spaces; long payloads truncated per AST-538 / Code Rules). No React debug requirements.

## Architectural definition

* **Patterns to reuse**
  * `pattern.ui.admin-endpoint` — thin authenticated admin API for Land Meteorite; React stays presentational; eligibility and ingest decisions stay server-side.
  * `pattern.layers.import-discipline` — Gmail list/get/archive/trash stays external; core owns selected-ids orchestration and bind/route/dedupe; UI calls core via API only.
  * `pattern.state.entity-state-transitions` — ingest still stops at **METEORITE_NEW**; no daisy-chain into qualify/GDL in this action.
  * `pattern.config.config-block` — reuse `GAZE_EMAIL_CONFIG` / existing ingest literals; do not invent parallel Land-Meteorite config for the same behavior.
* **New patterns proposed**
  * none — multi-select admin action + selected-ids call into the shared AST-1128 runner shape; not a new catalog pattern.
* **Applicable statutes**
  * `astral.layers.core-vs-external-bright-line` / `astral.layers.import-direction` — mailbox I/O vs core policy.
  * `astral.layers.ui-config-driven-business-logic` / `astral.patterns.require-auth-on-protected-endpoints` — admin mutator auth + thin UI.
  * `astral.config.config-source-of-truth` / `astral.config.secrets-and-env-specific-from-environ` — ingest literals in config; Gmail secrets environ-only.
  * `astral.state.no-daisy-chain-in-run` / `astral.state.core-decides-transitions` — land **METEORITE_NEW** only.
  * `astral.standards.in-scope-only` / `astral.standards.no-hardcoded-sets` / `astral.standards.no-cross-contamination` — selection + Land Meteorite + Create retirement only; no parallel task-key sets.
  * `astral.standards.debug-contract-gated` — Style D only when `debug=True`.
  * `universal` product-code set implied for any `src/` change.

## Boundaries

* Does **not** redesign Manage Email beyond selection chrome + **Land Meteorite** + retiring Create (no new match rules UI, no mailbox client rewrite, no Topic Menu / nav overhaul).
* Does **not** keep per-row **Create** after Land Meteorite ships (Create is retired by this epic).
* Does **not** fork a second ingest pipeline or build a throwaway interim adapter on the null-candidate shell — calls the shared selected-ids-capable core path from **AST-1128** (less code waste).
* Does **not** stamp `candidate.last_email_check` — that stamp stays exclusive to dispatcher `gaze_email` runs (**AST-1128**).
* Does **not** own candidate-bound dispatch rows, Avail counts, or `last_email_check` schema (**AST-1128**).
* Does **not** own `qualify_meteorite`, GDL, Recommended, LIKE/upshot, or attachments.
* Does **not** change From→candidate bind rules.
* Does **not** send outbound mail or trash/archive outside existing `gaze_email` outcome rules for bound selected messages.
* Does **not** force processing of the entire inbox when nothing is selected.
* Does **not** absorb **AST-1130** (Create button bug) as scope — Create is retired when Land Meteorite ships; interim Create fixes stay on AST-1130 if still needed before then.

## Acceptance criteria

1. On Manage Email, Archie can select multiple current inbox messages and clear that selection without leaving the page.
2. With a non-empty selection, **Land Meteorite** is available; with an empty selection it is not actionable.
3. Clicking **Land Meteorite** processes **only** the selected message ids through the shared `gaze_email` ingest path from AST-1128 (bind / route / scrape / dedupe / **METEORITE_NEW** / archive-or-ignore as established for that path).
4. Land Meteorite does **not** call the retired Create strip/extract create-job path for those messages.
5. Unbound / unmatched selected messages are skipped with explicit feedback; bound selected messages in the same batch still process.
6. After the action, Archie can tell which selected messages succeeded, were skipped, or failed, without leaving Manage Email.
7. A single Land Meteorite action does not advance jobs into qualify/GDL and does not update `candidate.last_email_check`.
8. When Land Meteorite is available on Manage Email, the per-row **Create** control is gone (retired).
9. With `debug=True`, each selected message and each create/skip/archive/ignore outcome is visible in Style D (found + recorded); with `debug=False`, no new debug noise from this path.

## Dependencies and blockers

* **Blocked by AST-1128** — wait for its callable selected-ids / candidate-bound core entrypoint (AST-1128 child #3 intent). No interim adapter on the current null-candidate runner (throwaway work = more code waste).
* Related **AST-1130** (Create button not working) — adjacent; Create retirement here may moot further Create UX once Land Meteorite ships.
* Reuses Done foundations: AST-1032 inbox read, AST-1044/AST-1047 bind, AST-1048/AST-1051 Manage Email Create UI (to be retired), AST-1049 create-job (adjacent legacy path), AST-1087/AST-1090 runner helpers reused via AST-1128 redesign.

## Open questions

none

## Proposed child tickets

#### 1!!!: **Selected-ids gaze_email ingest entrypoint - Ada**

Owns wiring Land Meteorite to the shared AST-1128 core callable that ingests an explicit list of Astral inbox message ids through the same bind / route / scrape / dedupe / create / mailbox outcomes as dispatcher `gaze_email` — including skip behavior for unbound/unmatched ids. Does **not** stamp `last_email_check`. Style D debug on the touched path. Does **not** own admin HTTP or Manage Email React (siblings #2/#3). After AST-1128.
**Citations:** `pattern.layers.import-discipline`; `pattern.state.entity-state-transitions`; `pattern.config.config-block`; `astral.state.no-daisy-chain-in-run`; `astral.standards.debug-contract-gated`; `astral.standards.in-scope-only`.

#### 2!: **Admin Land Meteorite API for selected message ids - Hedy**

After #1: thin authenticated admin endpoint that accepts selected message ids, calls the shared selected-ids ingest entrypoint, and returns per-id (or equivalent) outcome payload including skips. Does **not** own multi-select chrome (sibling #3).
**Citations:** `pattern.ui.admin-endpoint`; `astral.patterns.require-auth-on-protected-endpoints`; `astral.layers.ui-config-driven-business-logic`; `astral.layers.core-vs-external-bright-line`.

#### 3: **Manage Email multi-select + Land Meteorite + retire Create - Katherine**

After #2: Manage Email list multi-select + **Land Meteorite** control wired to the admin API; operator-visible batch outcome (including skips); **retire** the per-row Create control when Land Meteorite ships. Does **not** redesign the rest of Manage Email.
**Citations:** `pattern.ui.admin-endpoint`; `astral.layers.ui-config-driven-business-logic`; `astral.standards.in-scope-only`.

**New patterns:** none.

**Monolith check:** Functional scope has 7 capabilities; 3 children — shared selected-ids ingest wiring, admin API, Manage Email selection UI + Create retirement — split across layers intentionally.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-1129 (parent) | ftr/AST-1129-manage-email-select-inbox-messages-and-land-meteorite |
| AST-1140 | sub/AST-1129/AST-1140-selected-ids-gaze-email-ingest-entrypoint |
| AST-1141 | sub/AST-1129/AST-1141-admin-land-meteorite-api-selected-message-ids |
| AST-1142 | sub/AST-1129/AST-1142-manage-email-multi-select-land-meteorite-retire-create |

**Epic worktree:** `astral-AST-1129/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **Thread** column is the fully-qualified `store.db` path (UUID is the directory name — extract for `agent --resume`). **datt resume:** read this table — not chat memory. One UUID per agent; never the parent Chuckles Thread UUID.

| Agent | Role | Thread |
| -- | -- | -- |
| Katherine | engineer | `/home/susan/.cursor/chats/faa85ebf3de469250ba53b605b89a7b3/e1279aa0-eaf0-43ad-8147-4e3312d9c66e/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/faa85ebf3de469250ba53b605b89a7b3/4691851d-d434-4ff2-9323-6438b12b2cb8/store.db` |
| Ada | engineer | `/home/susan/.cursor/chats/faa85ebf3de469250ba53b605b89a7b3/5b87b8a4-5e3e-4f1f-8d51-93c25d7aeca9/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/c3f11b73-c9b4-4d23-8f5c-e7834053c751/store.db` |
| Radia | review | `/home/susan/.cursor/chats/faa85ebf3de469250ba53b605b89a7b3/ef29429e-2f29-4e74-b1b7-4c584f0d27d8/store.db` |

---

## Original brief

## Brief

Refactor Manage Email so Archie can multi-select messages in the shared Astral inbox and click **Land Meteorite**. That action runs the `gaze_email` ingest path for **only the selected message ids** (same bind / route / scrape / dedupe / archive behavior as dispatcher `gaze_email`, not a separate pipeline).

Out of scope here: redesigning the whole Manage Email product beyond selection + Land Meteorite; qualify/GDL hops.

## Next

Chuckles **define-parent** in Discussion; coordinate with the candidate-bound `gaze_email` redesign epic so Land Meteorite calls the same core path.

### Comments

#### chuckles — 2026-08-02T21:51:06.274Z
[publish-ref-stale] AST-1142 STALE(dev+54) — pausing AST-1141 build until refresh. Spawning @Katherine Johnson to merge origin/dev + origin/ftr/AST-1129-manage-email-select-inbox-messages-and-land-meteorite and republish `sub/AST-1129/AST-1142-manage-email-multi-select-land-meteorite-retire-create`.

— Chuckles

#### chuckles — 2026-08-02T21:46:34.559Z
[thread-missing] Hedy engineer Team UUID `1147180d-daa7-4ce0-bd1c-ef8fa493e9e7` had no store.db on this host. populate-team recovered `4691851d-d434-4ff2-9323-6438b12b2cb8` → `/home/susan/.cursor/chats/faa85ebf3de469250ba53b605b89a7b3/4691851d-d434-4ff2-9323-6438b12b2cb8/store.db`. First-spawn plan-child for AST-1141.

— Chuckles

#### chuckles — 2026-08-02T20:47:48.146Z
[thread-missing] Betty qa Team thread 7b3e38cc-95eb-4e40-915a-adf8ddc63ebd store.db not on this host — minted 28a78840-7853-41a0-96c1-c243495fe42d and updated ## Team.

— Chuckles

#### chuckles — 2026-08-02T20:40:38.072Z
[thread-orphan] Joan session da0027e7-276d-4fe2-a6e6-65c8eb77e24d relocated: /home/susan/.cursor/chats/0f41bf986cfef9e06ea903e586d6d4d9/da0027e7-276d-4fe2-a6e6-65c8eb77e24d/store.db → /home/susan/.cursor/chats/faa85ebf3de469250ba53b605b89a7b3/da0027e7-276d-4fe2-a6e6-65c8eb77e24d/store.db

— Chuckles

#### chuckles — 2026-08-02T20:36:50.160Z
[thread-missing] Ada engineer Team thread e513a72e-76a7-47c8-8d2e-f610f032ee3f store.db not on this host — minted 4431a083-45aa-4f07-8c39-7a7797c4bfdd and updated ## Team.

— Chuckles

#### chuckles — 2026-08-02T19:03:51.159Z
@susan

1. **Create coexistence** — Keep per-row Create beside Land Meteorite, or retire/hide Create once Land Meteorite ships?
2. **Unbound / unmatched selections** — Per-message gaze_email unbound/ignore rules, skip with feedback, or refuse the whole batch until all selected are bound?
3. **Hard block on AST-1128?** — Wait for its selected-ids / candidate-bound core entrypoint, or allow a temporary adapter on the current runner (no permanent fork)?
4. **`last_email_check`** — Should Land Meteorite stamp it for touched candidates (once AST-1128 adds the column), or only dispatcher `gaze_email` runs?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
