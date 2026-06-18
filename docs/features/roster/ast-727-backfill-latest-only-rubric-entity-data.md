# Backfill script for latest-only rubric entity data (Store only the latest rubric results in `<entity>_data`)

**Linear:** [AST-727](https://linear.app/astralcareermatch/issue/AST-727/backfill-latest-only-rubric-entity-data-store-only-the-latest-rubric-results-in)  
**Parent:** [AST-717](https://linear.app/astralcareermatch/issue/AST-717/store-only-the-latest-rubric-results-in-entity-data) (context only — runtime writes are **AST-726**)  
**Publish ref:** `sub/AST-717/AST-727-backfill-latest-only-rubric-entity-data`

**Summary:** Ship a one-time CLI migration that cleans **existing** job and company rows: dedupe `agent_responses` to one ref per `task_key` (latest `created_at` wins), drop legacy empty-`task_key` refs, and leave **`agent_data` untouched**. Reuses the same dedupe rules as **AST-726** runtime/read path. Idempotent with `--dry-run` for Susan review before live writes.

**Out of scope:** Runtime write-path changes (**AST-726**); candidate rows; rubric artifacts on candidates; admin UI trigger (CLI-only like **`backfill_collapse_blank_lines`**); decoding grades from `agent_data` to rewrite `job_data` / `company_data` blobs (runtime merge already kept scalar rubric keys — duplicate *navigation* refs are the primary legacy defect).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `scripts/migrations/backfill_latest_only_rubric_entity_data.py` | New one-time backfill CLI | scripts |
| `src/core/roster.py` | Export dedupe helper for script reuse (rename private → public or thin public wrapper) | core |

**No test edits in this ticket** — Betty owns manifest + bible at **qa-child**.

Spike output (if needed): **`debug/spikes/AST-727/…`** only — not repo root `artifacts/`.

---

## Stage 1: Shared dedupe helper (reuse AST-726 rules)

**Done when:** Migration script imports one roster function that implements identical dedupe semantics to **`get_entity_agent_story`** today; no duplicated dedupe logic in the script.

1. In `src/core/roster.py`, rename **`_dedupe_agent_responses_latest`** → **`dedupe_agent_responses_latest`** (public) **or** add a one-line public alias:
   ```python
   def dedupe_agent_responses_latest(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
       return _dedupe_agent_responses_latest(entries)
   ```
   Keep **`get_entity_agent_story`** calling the same implementation (private name OK if alias exists).

2. Add **`normalize_agent_responses_for_backfill(entries: list) -> tuple[list, dict]`** in the same file (or in the script if Susan prefers zero core churn — prefer **roster** for DRY with runtime):
   - Input: raw `agent_responses` list from entity column (coerce non-list → `[]`).
   - Drop dict entries whose `(entry.get("task_key") or "").strip()` is empty; count as **`dropped_empty_key`** in stats dict.
   - Apply **`dedupe_agent_responses_latest`** on the remainder.
   - Return **`(normalized_list, {"dropped_empty_key": n, "deduped_removed": before_len - after_dedupe_len})`**.

⚠️ **Decision:** Helper lives in **roster** (not database) so backfill and **`get_entity_agent_story`** share one dedupe implementation — matches **AST-726** plan and **ASTRAL_CODE_RULES** §1.3 DRY.

---

## Stage 2: Migration script

**Done when:** Script runs with `--dry-run` against a copy of prod-shaped DB, prints per-entity actions and summary counts, and with live flags writes only changed `agent_responses` columns on **job** and **company** rows; **`agent_data` row count unchanged**.

1. Create **`scripts/migrations/backfill_latest_only_rubric_entity_data.py`** following **`scripts/migrations/backfill_collapse_blank_lines.py`** layout:
   - Module docstring: purpose, idempotency, **Susan backup guidance** (copy `data/` SQLite file or Railway snapshot before live run).
   - `sys.path.insert(0, …)` repo root pattern.
   - **`argparse`**: `--dry-run`, `--company SHORT_NAME`, `--job ASTRAL_JOB_ID` (same narrowing semantics as collapse-blank-lines backfill).

2. **Imports:**
   - `list_companies`, `list_jobs` from **`src.data.database`**
   - `update_company` from **`src.data.database`**
   - `normalize_agent_responses_for_backfill` from **`src.core.roster`**
   - `json` for job-row agent_responses UPDATE (see step 4).

3. **Counts dict** keys: `scanned`, `updated`, `unchanged`, `errors`, `dropped_empty_key_total`, `deduped_refs_removed_total` (aggregate stats from step 5).

4. **Write path for `agent_responses`:**
   - **Company:** `update_company(short_name, agent_responses=normalized_list)` when not dry-run.
   - **Job:** add **`_set_job_agent_responses(astral_job_id, entries, dry_run)`** in the script — copy the **`append_agent_response`** table map (`company`/`job`/`candidate` → table + pk) from `database.py` but **SET** the full JSON array (do **not** call `append_agent_response` — avoids re-upsert side effects). **Do not** add a new database.py public API in this ticket unless the script helper proves insufficient.

5. **Per-entity algorithm** (`backfill_one_entity(entity_type, row)`):
   - Read `entries = row.get("agent_responses") or []`.
   - `normalized, stats = normalize_agent_responses_for_backfill(entries)`.
   - If `normalized == entries` (deep equality after JSON-normalizing list order): **`unchanged`**, return.
   - If **`--dry-run`**: print `[job|company <id>] DRY RUN — would set agent_responses {len(entries)} -> {len(normalized)} refs (dropped_empty={…}, deduped_removed={…})`; count as **`updated`** for summary.
   - Else: write via company **`update_company`** or job **`_set_job_agent_responses`**; count **`updated`**.

6. **`backfill_companies(dry_run, company)`** — iterate `list_companies()`, optional single-`short_name` filter; call per-entity algorithm.

7. **`backfill_jobs(dry_run, job_id)`** — iterate `list_jobs()`, optional single-`astral_job_id` filter.

8. **`run_backfill(dry_run, company, job_id)`** — mirror collapse-blank-lines: when both filters None, run **both** company and job scans; when `--company` only, jobs skipped; when `--job` only, companies skipped.

9. **`if __name__ == "__main__"`** — parse args, call `run_backfill`, print **`=== SUMMARY ===`** sections.

⚠️ **Decision:** Script touches **`agent_responses` column only** — not `job_data` / `company_data` rubric scalar keys. **AST-726** runtime already overwrote `{prefix}_grades` / scores on each run; legacy duplicate *modal tabs* came from duplicate refs. Re-decoding `agent_data` to rebuild blobs is high-risk and out of AC for this ticket.

⚠️ **Decision:** **Candidates excluded** — parent AC names job and company entities only.

---

## Stage 3: Operator runbook (in script docstring + plan)

**Done when:** Susan can run safely on staging/local without reading source.

1. In script module docstring, document **recommended order**:
   ```bash
   # 1. Backup: cp data/astral.db data/astral.db.pre-AST-727-$(date +%Y%m%d)
   # 2. Dry-run full scan
   python scripts/migrations/backfill_latest_only_rubric_entity_data.py --dry-run
   # 3. Spot-check one noisy entity
   python scripts/migrations/backfill_latest_only_rubric_entity_data.py --dry-run --job <id>
   # 4. Live run (after Susan OK)
   python scripts/migrations/backfill_latest_only_rubric_entity_data.py
   ```

2. Note: **Idempotent** — second live run should report all **`unchanged`** if **AST-726** runtime upsert is already active.

3. Note: **`agent_data` is never DELETE/UPDATE** — verify with `SELECT COUNT(*) FROM agent_data` before/after if desired.

---

## Stage 4: Compile gate

**Done when:** `python -m py_compile scripts/migrations/backfill_latest_only_rubric_entity_data.py src/core/roster.py` passes.

1. Run compile on touched modules before **Code Complete**.

---

## Execution contract

Binding per **plan-child**: stages **1 → 2 → 3 → 4** in order; **one commit per stage** on epic worktree during **build-child**, publish each to **`origin/sub/AST-717/AST-727-backfill-latest-only-rubric-entity-data`**. Do not edit **`tests/`** or **`docs/test-bible/**`**. On ambiguity — **`🛑 Stage N blocked`** on **AST-717** parent; stop.

---

## Self-Assessment

**Scope:** `Single-Component` — one migration script plus a small roster export/wrapper; no UI or runtime consult/roster write changes.

**Conf:** `high` — **AST-726** already defined dedupe semantics and upsert behavior; backfill mirrors read-path rules with established migration-script patterns.

**Risk:** `Medium` — wrong dedupe or accidental `agent_data` touch would corrupt audit history; mitigated by column-scoped writes, dry-run default workflow, and shared roster helper.

---

## Self-review against ASTRAL_CODE_RULES

| Rule | Assessment |
|------|------------|
| §1.3 DRY | Single `normalize_agent_responses_for_backfill` + `dedupe_agent_responses_latest` shared with runtime story shaping. |
| §2.1 config | No new config keys; scored task keys unchanged. |
| §2.4 batch | No batch claim/clear changes; offline migration only. |
| §2.6 state machine | Script does not transition entity states. |
| §3.3 imports | Script imports `database` + `roster` (same as other migrations); no UI/external bends. |
| §3.6 spikes | Any investigation under `debug/spikes/AST-727/` only. |

No unresolved conflicts.

---

## Review

**Branch:** `origin/sub/AST-717/AST-727-backfill-latest-only-rubric-entity-data`  
**Diff baseline:** `origin/dev`  
**Review tip:** `2446a63`

**Built:** Stages 1–4 — public `dedupe_agent_responses_latest` + `normalize_agent_responses_for_backfill` in roster; CLI migration script with `--dry-run` / `--company` / `--job` filters; column-scoped `agent_responses` writes only (job + company; candidates excluded); operator runbook in module docstring.

### Radia review (AST-727)

| | |
|---|---|
| **What's solid** | Plan stages 1–4 match AST-727 commits: shared roster normalizer (drop empty `task_key`, dedupe latest `created_at`, stats dict); migration script mirrors `backfill_collapse_blank_lines` layout (filters, dry-run summary, idempotent unchanged path, error → `errors` count); company writes via `update_company`; job writes via script-local full-array SET (no `append_agent_response` side effects); `agent_data` untouched; candidates excluded. Betty manifest covers normalizer, company/job backfill paths, and filter routing. Compile gate passes on touched modules. |
| **Issues** | None **fix-now**. |
| **Discuss** | Branch diff vs `origin/dev` also carries **AST-726** runtime sibling changes (upsert, consult/roster saves, story dedupe) — expected epic stacking on one publish ref; AST-727-specific scope is script + normalizer export only. |
| **Advisory** | Job write path imports private `database._get_connection` / `_ensure_job_schema` / `_run_with_retry` — plan authorized copying the append pattern without a new public API; same precedent as `bootstrap_candidate.py`. Non-dict `agent_responses` elements are dropped by the normalizer without a dedicated stat counter (test covers `"bad"` skip). |
| **Recommended actions** | Hedy → **resolve-child** — no code changes required. Susan: run `--dry-run` full scan, spot-check noisy entities, then live run after backup per script docstring. |
