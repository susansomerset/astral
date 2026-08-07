# AST-1260 — Tighten claim-process-release; remove conflicting candidate law

**Linear:** [AST-1260](https://linear.app/astralcareermatch/issue/AST-1260/tighten-claim-process-release-remove-conflicting-candidate-law)
**Parent:** [AST-1257](https://linear.app/astralcareermatch/issue/AST-1257/candidate-table-does-not-have-batch-id) — candidate table does not have batch_id
**Publish ref:** `origin/sub/AST-1257/AST-1260-tighten-claim-process-release-remove-conflicting-candidate-law`

Amend `astral.batch.claim-process-release` **in place** so every `ENTITY_TYPES` dispatch claim queue requires pool claim → process → release (no silent carve-outs). Align `pattern.batch.entity-claim-process-release` (candidate helpers as peers of job/company), CODE_RULES §2.4 wording, and `CANDIDATE_DATA_MODEL.md` (remove “no batch primitives” / single-candidate carve-out). Docs/canon only — product claim/dispatch is AST-1258 / AST-1259.

## UAT fitness

- **AC restored:** Parent AC 5 — “`astral.batch.claim-process-release` is tightened in place; conflicting candidate-processing statute text is removed or amended; pattern catalog + CODE_RULES §2.4 + `CANDIDATE_DATA_MODEL` no longer bless unlocked or non-pool candidate claim; a candidate-only unlocked path would fail statute/pattern review.”
- **Correct outcome:** Review and plan validation treat unlocked / single-ctx candidate claim as a statute/pattern defect; law and data-model docs describe candidate pool claim the same way as job/company.
- **Sibling check:** AST-1258 (schema + `claim_candidate_batch` / get / clear + pool Avail) and AST-1259 (`get_new_candidate_batch` / dispatcher finally-clear) already landed on `origin/ftr/AST-1257-candidate-table-does-not-have-batch-id`. This ticket does not re-implement them — only makes law/docs match that product. Verified by reading those plans + tip symbols before Plan Ready.
- **Not sufficient:** Deleting the “No batch primitives” sentence alone, or refreshing `approved_at` without tightening the Statement / pattern solution language, is **not** done.
- **Wrong fix rejected:** Inventing a new pattern/statute id, or a candidate-only exception statute that re-blesses unlocked claim — parent and child Boundaries forbid that. Softening only Examples while leaving a vague Statement would still let unlocked candidate paths pass review.

## Survey findings (baked into this plan — builder does not re-decide)

Search on tip after merge of `origin/ftr/AST-1257-candidate-table-does-not-have-batch-id` (`rg` over `canon/statutes/**`, `canon/patterns/**` for unlocked / no-batch / single-candidate / carve-out candidate claim language):

| Location | Finding | Action this ticket |
|----------|---------|-------------------|
| `canon/statutes/astral/batch/astral.batch.claim-process-release.md` | Statement too weak — does not name `ENTITY_TYPES`, pool claim, or ban silent carve-outs | **Amend in place** (Stage 1) |
| Other active statutes under `canon/statutes/**` | No separate statute file blesses unlocked / non-pool candidate claim | **Do not retire** any statute file |
| `canon/patterns/batch/pattern.batch.entity-claim-process-release.md` | `canonical_refs` are job-only; Solution shape omits candidate pool peers | **Amend in place** (Stage 2) |
| `docs/ASTRAL_CODE_RULES.md` §2.4 | Says “all entity types” but does not call out candidate / `ENTITY_TYPES` claim-queue duty; company-only narrative | **Amend wording** (Stage 2) |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Line “No batch primitives on candidate — candidates are not batch-processed.” + missing lock columns | **Amend** (Stage 3) |
| Archived AST-972 feature docs under `docs/features/candidate/` | Historical decisions (single-ctx / no claim helpers) — overturned by AST-1257 | **Do not rewrite** archives |

⚠️ **Decision — Archie approval:** Parent AST-1257 Architectural definition already names this in-place amend and cites `orch.roles.archie-approves-statutes`. On each statute/pattern amend commit, set `approved_by: Archie` and refresh `approved_at` to that commit’s UTC date (`YYYY-MM-DD`). Do **not** set `approved_by` to an engineer name. If Archie rejects the exact Statement/Solution text at Plan Discuss / Plan Ready, stop and revise — do not invent alternate law.

⚠️ **Decision — no new ids:** Strengthen existing statute id `astral.batch.claim-process-release` and pattern id `pattern.batch.entity-claim-process-release`. Do not create a candidate-only pattern or exception statute.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `canon/statutes/astral/batch/astral.batch.claim-process-release.md` | Tighten Statement / Rationale / Examples; refresh `approved_at` | canon / statutes |
| `canon/patterns/batch/pattern.batch.entity-claim-process-release.md` | Add candidate `canonical_refs`; pool-parity Solution language; refresh `approved_at` | canon / patterns |
| `docs/ASTRAL_CODE_RULES.md` | §2.4 wording: explicit `ENTITY_TYPES` claim-queue + candidate pool parity | docs |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Remove “no batch primitives”; document `batch_id` / `batch_created_at` | docs |

No `src/**`, no `tests/**`, no bible, no new statute/pattern files, no `HARVEST.md` / SCHEMA / AUTHORING rewrites.

## Stage 1: Amend `astral.batch.claim-process-release`

**Done when:** The statute Statement requires pool claim → process → release for every `ENTITY_TYPES` dispatch claim queue (candidate included), bans silent carve-outs, and Examples flag unlocked single-ctx candidate claim as violating. Frontmatter keeps `id` / path / `status: active` / `approved_by: Archie` with refreshed `approved_at`.

1. Edit **only** `canon/statutes/astral/batch/astral.batch.claim-process-release.md`. Keep all SCHEMA frontmatter keys; do not change `id`, `tier`, `checkable`, `applies_when`, `source_docs`, or supersession fields. Set `approved_by: Archie` and `approved_at: "<UTC date of this commit YYYY-MM-DD>"`.
2. Replace `# Statement` body with exactly:

   > Every `ENTITY_TYPES` member used as a dispatch claim queue (`candidate`, `company`, `job`) must use claim → process → release with a row `batch_id` lock and **pool** claim parity: claim up to `limit` unclaimed rows in the claimable state set under one `batch_id`, process only those rows, and clear the lock in `finally` (and on every early-exit path **on which rows were actually claimed** — a zero-row claim needs no release). Do not select by state or single-ctx and process without batch locking. Silent per-entity carve-outs that skip pool claim for any `ENTITY_TYPES` claim queue are review defects unless Archie has an explicit approved exception statute.

3. Replace `## Rationale` body with exactly:

   > Batch locking is the concurrency and audit spine for dispatch. Candidate is an `ENTITY_TYPES` claim queue peer of job and company — not a single-row unlocked special case.

4. Replace `## Examples` with exactly:

   ```markdown
   ## Examples

   ### Conforming

   - Dispatcher claims candidates via `get_new_candidate_batch` / `claim_candidate_batch`, processes claimed rows, then `clear_candidate_batch` in `finally` (same shape as job/company).
   - Job or company claim → process → `clear_*_batch` in `finally`.

   ### Violating

   - A candidate dispatch branch sets `entities = [ctx]` when the ctx state is claimable and never locks `candidate.batch_id`.
   - A runner `SELECT`s jobs (or candidates) by state and updates them with no claim/clear.
   - Docs or statutes bless a candidate-only unlocked / non-pool claim path.
   ```

5. Optional `## Notes` — if present, replace with exactly this; if absent, append after Examples:

   > Non-`ENTITY_TYPES` pollers (e.g. `gaze_email`, meteorite mailbox shells) are not dispatch claim queues and stay outside this statute’s claim-lock duty. Do not use that exception to skip candidate pool claim.
   >
   > A zero-row claim locks no rows; company's empty-batch early exit without `clear_company_batch` is known-conforming under this Statement.

6. Do **not** create, retire, or rename any other statute file in this stage.

**Commit message:** `docs(AST-1260): tighten astral.batch.claim-process-release for ENTITY_TYPES pool claim`

## Stage 2: Pattern catalog + CODE_RULES §2.4

**Done when:** Pattern `canonical_refs` include candidate claim/get/clear (data) and core wrappers; Solution shape states candidate is a pool-claim peer of job/company; §2.4 prose explicitly requires the same for every `ENTITY_TYPES` claim queue and no longer reads as company-only law.

1. Edit `canon/patterns/batch/pattern.batch.entity-claim-process-release.md`:
   - Keep `id`, `status: approved`, `proposed_in`, `related_statutes`, supersession fields.
   - Set `approved_by: Archie` and refresh `approved_at` to this commit’s UTC date.
   - Replace `canonical_refs` with exactly this list (YAML):

     ```yaml
     canonical_refs:
       - path: src/data/database.py
         symbol: claim_job_batch
       - path: src/data/database.py
         symbol: clear_job_batch
       - path: src/data/database.py
         symbol: claim_candidate_batch
       - path: src/data/database.py
         symbol: get_candidate_batch
       - path: src/data/database.py
         symbol: clear_candidate_batch
       - path: src/core/candidate.py
         symbol: get_new_candidate_batch
       - path: src/core/candidate.py
         symbol: clear_candidate_batch
       - path: docs/ASTRAL_CODE_RULES.md
         symbol: "§2.4"
     ```

   - Replace `# Solution shape` body with exactly:

     > Claim a batch with a `batch_id` (first parameter on claim/get/clear helpers), process only claimed rows, and clear the batch in `finally` (or equivalent release). Pool claim applies to every `ENTITY_TYPES` dispatch claim queue — candidate helpers (`claim_candidate_batch` / `get_new_candidate_batch` / `clear_candidate_batch`) are first-class peers of job/company, not a single-ctx unlocked shape. Core decides transitions; data owns claim/clear. Point at `canonical_refs` — do not paste large code into this catalog entry.

   - Keep `# Problem` unchanged unless it still implies job-only scope; if so, replace Problem with:

     > Dispatch and entity runners need a concurrency-safe way to select work across an unclaimed pool, process it, and release the claim without racing other workers or losing auditability.

   - Under `## When not to use`, keep the three existing bullets and ensure this bullet is present (add if missing; do not duplicate):

     > Non-`ENTITY_TYPES` mailbox / null-entity pollers (e.g. `gaze_email`) that are not dispatch claim queues.

2. In `docs/ASTRAL_CODE_RULES.md` §2.4 (`### 2.4 Batch Processing Pattern`):
   - After the sentence “All batch jobs that process entities by state use batch locking.” insert (if not already present) exactly:

     > Every `ENTITY_TYPES` member used as a dispatch claim queue (`candidate`, `company`, `job`) uses the same pool claim → process → release shape. Candidate is not exempt: no unlocked single-ctx claim path, no empty release stub.

   - Keep the existing `batch_id` format paragraph, claim → process → release numbered list, Data layer / Core signature lines, and dispatcher narrative/pseudocode (company example may remain as illustration).
   - Replace the closing sentence “Do not select by state and process without batch_id. Use claim / get / clear and batch_id-first order consistently for all entity types.” with exactly:

     > Do not select by state (or single-ctx) and process without batch_id. Use claim / get / clear and batch_id-first order consistently for every `ENTITY_TYPES` claim queue, including candidate.

3. Do **not** edit other CODE_RULES sections, `HARVEST.md`, or pattern SCHEMA/AUTHORING/README.

**Commit message:** `docs(AST-1260): candidate pool peers in claim pattern and §2.4`

## Stage 3: `CANDIDATE_DATA_MODEL` honesty

**Done when:** Both column inventories in the candidate data-model doc list `batch_id` / `batch_created_at` (`## Candidate table (columns)` and `## Snake_case` → **DB columns**); the doc no longer says candidates lack batch primitives or are not batch-processed; `state_history[].batch_id` does not contradict row locks.

1. In `docs/features/candidate/CANDIDATE_DATA_MODEL.md`, under `## Candidate table (columns)`:
   - **Delete** the standalone line: `No batch primitives on candidate — candidates are not batch-processed.`
   - After the identity / `candidate_data` / `candidate_api_key` bullets (and with the timestamp bullets), ensure these two column bullets exist (add if missing; do not duplicate):

     - **batch_id** — Golden-ticket lock for dispatch claim → process → release (AST-1258). Null or empty means unclaimed. Same pool-claim role as job/company `batch_id`.
     - **batch_created_at** — Timestamp set when the row is claimed; cleared with `batch_id` on release.

   - Update the **state_history** bullet so it does **not** say batch claim “does not exist.” Keep the field shape `{from_state, to_state, timestamp, batch_id}`. Replace any “until candidate batch claim exists” wording with: `batch_id` on a history entry may be null when the transition was not batch-anchored; row lock columns are separate (claim/clear).

2. Under `## Snake_case`, replace the **DB columns:** line with exactly:

   `**DB columns:** astral_candidate_id, state, state_history, first, last, full, pronouns, candidate_data, candidate_api_key, batch_id, batch_created_at, created_at, updated_at, state_changed_at.`

3. Do **not** change token tables, library section layouts, or company FK notes except where they contradict pool claim (leave `company.candidate_id` batch-filter note as-is — that is company scoping, not candidate row locks).

4. Do **not** edit archived AST-972 plan markdown under `docs/features/candidate/`.

**Commit message:** `docs(AST-1260): candidate data model batch lock columns`

## Manual check (no product commit)

After Stage 3, from the epic worktree tip:

1. Confirm `rg -n "No batch primitives|not batch-processed" docs/features/candidate/CANDIDATE_DATA_MODEL.md` returns no matches.
2. Confirm statute Statement contains `ENTITY_TYPES` and `pool`.
3. Confirm pattern `canonical_refs` lists `claim_candidate_batch` and `get_new_candidate_batch`.
4. Confirm statute Statement contains `zero-row claim needs no release` (or equivalent empty-claim release qualification).
5. Confirm `rg -n "batch_id|batch_created_at" docs/features/candidate/CANDIDATE_DATA_MODEL.md` matches both names on the `## Snake_case` → **DB columns** line (and on the column bullets).
6. Do **not** run or edit pytest / bible.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1257/AST-1260-tighten-claim-process-release-remove-conflicting-candidate-law`.
- Do not add files outside **Files Changed**.
- Do not implement or revise product claim/dispatch code (AST-1258 / AST-1259).
- On ambiguity or drift: stop and comment on **parent** AST-1257 with the 🛑 Stage N blocked template.

## Self-Assessment

**Scope:** Single-Component — canon statute + pattern + two docs files; no `src/` product change.

**Conf:** high — survey found no separate statute to retire; exact Statement / Solution / column bullets are pinned; siblings already expose the symbols this law cites.

**Risk:** Medium — under-broad language would let unlocked candidate paths pass review again; over-broad empty-batch wording mitigated by zero-row release qualification + Notes (company empty-path known-conforming).

## Revisions

**Revision 1 — 2026-08-07**  
Driven by: Joan `[plan-discuss] round=1 concern` (REVISE @ `b84bf175`)  
Changes: (fix-now) Stage 3 updates `## Snake_case` → **DB columns** to include `batch_id`, `batch_created_at`; Manual check 5 asserts both names on that line. (discuss) Stage 1 Statement qualifies release to early-exit paths where rows were actually claimed (zero-row needs no release); Notes records company's empty-batch early exit as known-conforming.

## Rules check (plan vs ASTRAL_CODE_RULES)

| Rule | Plan stance |
|------|-------------|
| §2.4 claim-process-release / batch-id-first / batch-id-format | This ticket amends the statute + §2.4 prose; does not reimplement claim SQL |
| `orch.roles.archie-approves-statutes` | Amend keeps `approved_by: Archie`; refresh `approved_at` per stage commit |
| `astral.docs.features-single-file-per-ticket` | Plan lives at this path only |
| `astral.git.engineer-test-tree-ban` / Betty owns tests | No `tests/` or bible edits |
| §3.3 import direction | N/A — docs/canon only |
| Out of scope | `src/data/database.py`, `src/core/dispatcher.py`, `src/core/candidate.py` product logic — siblings |
