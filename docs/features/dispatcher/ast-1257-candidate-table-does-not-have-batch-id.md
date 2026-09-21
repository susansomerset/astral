# AST-1257 — candidate table does not have batch_id

<!-- linear-archive: AST-1257 archived 2026-08-17 -->

## Linear archive (AST-1257)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1257/candidate-table-does-not-have-batch-id  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Scheduled Actions already treat `entity_type=candidate` as a dispatch claim queue (stage keys, inflow discovery, REQUESTED_* workers), but the candidate row has no `batch_id` lock and the dispatcher path selects by state / context without claim → process → release. Job and company use batch locking as the concurrency and audit spine. This epic closes that parity gap in product, pattern catalog, and statute law so a silent candidate carve-out cannot pass review again — candidate claim is the same pool claim shape as job/company, not a single-row special case.

## Functional scope

1. **Candidate lock columns** — The candidate entity carries the same batch-lock fields job and company use (`batch_id` plus `batch_created_at` for claim/release parity), with null/empty meaning unclaimed.
2. **Candidate claim / get / clear (pool parity)** — Data and core expose claim → get → clear helpers with the same shape as job/company: `batch_id` first, claim up to `limit` unclaimed candidates in the claimable state set (cross-candidate pool), get by `batch_id`, clear releases the lock. Not a single-ctx / one-row-only gate.
3. **Dispatcher parity** — Scheduled candidate work claims through those helpers using `batch_size` / claim-state mechanics like other ENTITY_TYPES members, and always releases in `finally` (no state-only “use ctx if claimable” path, no empty release stub).
4. **Eligibility honesty** — Candidate availability / count for claimable stage tasks treats locked rows as unavailable and counts the unclaimed pool the same way job and company do.
5. **Canon and docs honesty** — Tighten `astral.batch.claim-process-release` in place so every ENTITY_TYPES claim queue requires batch locking; survey and **remove or amend any statutes** (and align pattern catalog + CODE_RULES §2.4 + `CANDIDATE_DATA_MODEL`) that bless unlocked / non-pool candidate processing or otherwise conflict with full job/company parity. Review must fail a candidate carve-out unless Archie has an explicit approved exception statute.
6. **Debug on touched claim paths** — When `debug=True` on the candidate claim/dispatch path, log what was found and what was recorded per step (index headers with `index N/M`, primary id, outcome; working detail lines use the Style D detail prefix (two spaces, pipe, two spaces)), per the AST-538 / CODE_RULES debug contract.

## Architectural definition

* **Patterns to reuse** — `pattern.batch.entity-claim-process-release` (mandatory claim → process → release with golden-ticket `batch_id`; candidate helpers are first-class peers of job/company in `canonical_refs` and solution language — same pool claim, not a candidate-only shape). `pattern.state.entity-state-transitions` (state changes stay core-owned; claim lock is not a substitute for transitions).
* **New patterns proposed** — none (strengthen the existing batch claim pattern; do not invent a candidate-only locking shape).
* **Applicable statutes** — `astral.batch.claim-process-release` (**amend in place**: every `ENTITY_TYPES` member used as a dispatch claim queue must have row batch locking and pool claim parity — silent per-entity carve-outs are review defects; retire/remove conflicting candidate-processing statute text found in survey); `astral.batch.batch-id-first`; `astral.batch.batch-id-format`; `astral.standards.database-header-inventory` (candidate table inventory when columns land); `astral.layers.import-direction`; `astral.state.core-decides-transitions`; `astral.standards.debug-contract-gated` (touched `debug=` claim/dispatch surfaces); `orch.roles.archie-approves-statutes` (statute amend/retire requires Archie approval in frontmatter).

## Boundaries

* Does **not** change job or company claim SQL beyond shared helpers if reused.
* Does **not** redefine `CANDIDATE_STATES`, stage dispatch keys, or craft/`run_next` hop graphs (except as required so candidate claim uses the shared batch APIs).
* Does **not** turn mailbox / null-entity pollers (`gaze_email`, meteorite mailbox shells) into claim queues — they stay non-`ENTITY_TYPES` claim exceptions already documented.
* Does **not** keep AST-972’s “no batch primitives / no claim_candidate_batch / single-candidate-only” decisions — overturned in favor of full job/company pool claim parity.
* Must not break existing agent_data / ledger trails that already use a dispatch `batch_id` while the candidate row lacked a lock column.

## Acceptance criteria

1. Candidate schema (ensure + inventory) exposes `batch_id` and `batch_created_at`; unclaimed rows have null/empty `batch_id`.
2. Candidate claim → get → clear can lock multiple unclaimed candidates in claimable states in one `batch_id` (pool), release them all on clear, and refuse a second concurrent claim on already-locked rows.
3. Dispatcher `entity_type=candidate` scheduled runs claim via those helpers (respecting `batch_size` / claim states) and clear the lock in `finally` (including empty-batch / early-exit paths that today clear job but `pass` for candidate).
4. Eligibility/count for candidate stage claim tasks reports the unclaimed pool size (0 when none available or all locked / not claimable).
5. `astral.batch.claim-process-release` is tightened in place; conflicting candidate-processing statute text is removed or amended; pattern catalog + CODE_RULES §2.4 + `CANDIDATE_DATA_MODEL` no longer bless unlocked or non-pool candidate claim; a candidate-only unlocked path would fail statute/pattern review.
6. With `debug=True` on the touched candidate claim/dispatch path, logs show per-step found/recorded detail with Style D index headers and Style D detail-prefix working lines (backend only).

## Dependencies and blockers

none.

## Open questions

none.

## Proposed child tickets

#### 1!!!: **Candidate batch lock schema and pool claim APIs - Katherine**

Add candidate `batch_id` / `batch_created_at`, inventory/header honesty, and data-layer claim / get / clear with **job/company pool parity** (claim up to limit unclaimed candidates in claim states; batch_id-first) plus eligibility/count over the unclaimed pool. Does not wire dispatcher. **Citations:** `pattern.batch.entity-claim-process-release`; `astral.batch.claim-process-release`; `astral.batch.batch-id-first`; `astral.batch.batch-id-format`; `astral.standards.database-header-inventory`.

#### 2!: **Dispatcher and core candidate pool claim parity - Ada**

Add core `get_new_candidate_batch` / clear wrappers and replace the unlocked single-ctx candidate branch in unified dispatch with claim → process → release using the same batch_size / claim-state pool mechanics as job/company (finally clears; debug contract on touched path). After #1. Does not own statute text. **Citations:** `pattern.batch.entity-claim-process-release`; `astral.batch.claim-process-release`; `astral.batch.batch-id-first`; `astral.batch.batch-id-format`; `astral.standards.debug-contract-gated`; `astral.layers.import-direction`.

#### 3: **Tighten claim-process-release; remove conflicting candidate law - Hedy**

Amend `astral.batch.claim-process-release` **in place** (explicit ENTITY_TYPES + pool claim + no silent carve-outs). Survey canon for statutes that conflict with candidate batch/pool parity and **remove or amend** them. Update `pattern.batch.entity-claim-process-release` (canonical_refs + solution language), CODE_RULES §2.4 wording, and `docs/features/candidate/CANDIDATE_DATA_MODEL.md` (remove “no batch primitives” / single-candidate carve-out). Archie approval on statute frontmatter. Can draft in parallel with #1/#2; must land before parent UAT so law matches product. **Citations:** `astral.batch.claim-process-release`; `pattern.batch.entity-claim-process-release`; `orch.roles.archie-approves-statutes`.

**New patterns:** none — child #3 strengthens the existing batch claim pattern and statute rather than proposing a new catalog id.

**Monolith check:** six Functional scope items → three children (schema/data pool APIs, dispatcher/core, canon/docs); intentional split so law and product can review independently.

---

## Original brief

Looks like we are claiming candidate work from scheduled actions without a locking mechanism as we have for job and company.

Please analyze the pattern used to claim candidates for scheduled work, how it differs from the batch claim process for other entities (job and company), and correct the statutes so that this would have been caught in review, and resolve the discrepancy in the candidate table, the pattern catalog, and of course the dispatch logic.

## Git (authoritative — ignore Linear `gitBranchName`)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Ticket | `origin/…` |
| -- | -- |
| AST-1257 (parent) | ftr/AST-1257-candidate-table-does-not-have-batch-id |
| AST-1258 | sub/AST-1257/AST-1258-candidate-batch-lock-schema-and-pool-claim-apis |
| AST-1259 | sub/AST-1257/AST-1259-dispatcher-and-core-candidate-pool-claim-parity |
| AST-1260 | sub/AST-1257/AST-1260-tighten-claim-process-release-remove-conflicting-candidate-law |

**Epic worktree:** `astral-AST-1257/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

*(generated from epic registry — do not hand-edit; edits are overwritten)*

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | `/home/susan/.cursor/chats/d4b58f0be865d3c403629d1b263613d9/7c73b5e1-94f8-40a0-83c5-6623c955fe1e/store.db` |
| Hedy | engineer | `/home/susan/.cursor/chats/d4b58f0be865d3c403629d1b263613d9/47620ed9-f713-4d15-bd28-f8cd182ff1a2/store.db` |
| Katherine | engineer | `/home/susan/.cursor/chats/d4b58f0be865d3c403629d1b263613d9/437416d3-2a4c-475a-8b2b-9d6bb947d48c/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/833be217-683b-44fa-bfe2-ac819ca3dbb8/store.db` |
| Radia | review | `/home/susan/.cursor/chats/d4b58f0be865d3c403629d1b263613d9/a515d809-6955-4f5e-8485-b921c6665f8c/store.db` |

### Comments

#### chuckles — 2026-08-07T17:40:44.301Z
@susan definition drafted — need your call on:

1. Claim shape: **(A)** one candidate per `dispatch_task.candidate_id` + row `batch_id` locking (recommended), or **(B)** cross-candidate pool claiming like job/company?
2. Statute amend: tighten `astral.batch.claim-process-release` in place, or a new sibling statute for candidate parity?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
