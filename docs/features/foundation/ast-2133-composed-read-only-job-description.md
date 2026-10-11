# AST-2133 — Composed, read-only job description

**Parent:** [AST-2130 — Create a new table telescope_data](https://linear.app/astralcareermatch/issue/AST-2130)
**Ticket:** [AST-2133](https://linear.app/astralcareermatch/issue/AST-2133)
**Publish ref:** `origin/sub/AST-2130/AST-2133-composed-jd`

After AST-2132, a scraped job description is no longer written into `job_data.job_description`; gazer keeps the raw capture in `telescope_data` and stores its row id on `job_data.jd_telescope_data_id`, and `job_description` becomes the **preamble** (email / pasted / agent-parsed text). This ticket adds the one reader that turns those two into the complete JD — preamble, then the referenced capture run through today's blank-line collapse and `jd_prune_rules` — and switches every JD consumer in consult and the job list / detail APIs to it. The JD becomes read-only: the job edit API stops accepting `job_description`, and the job modal shows it as display text instead of a textarea.

## Scope check

This ticket's `## Scope` names four files, and every stage below edits only these:

- `src/core/tracker.py` — new composed-JD function; `get_job_data` JD key returns it (self-heal unchanged); job-field update (`persist_skipped_job_edits`) drops `job_description`.
- `src/core/consult.py` — JD reads call the composed-JD function.
- `src/ui/api/api_jobs.py` — `list_view` / `detail` put the composed JD in the response's `job_data.job_description` (never written back); `persist_skipped_edits` stops accepting `job_description`.
- `src/ui/frontend/src/components/JobDetailModal.tsx` — JD read-only; out of draft, dirty check and save payload.

Not edited: `src/core/gazer.py` (AST-2132), `src/core/roster.py` / `src/ui/api/api_admin.py` (AST-2134), `src/data/database.py` / `src/utils/config.py` (AST-2131), `src/core/meteorite.py` (parent out-of-scope — its `jd_key` uses are preamble writes), tests and bible (Betty).

## Canon

`stat.logging.debug`, `stat.logging.warning`, `stat.logging.error` (`canon/directives/active/`; `docs/canon-index.md` is absent on this ref). Binding consequences here:

- The composed-JD function logs `Calling resolve_telescope_value: [...]` / `Response from resolve_telescope_value: ...` at `logger.debug` around the one callee it adds — full values, no truncation, no `if debug` gate.
- A missing `telescope_data` row is already warned once inside `resolve_telescope_value` (AST-2132); the composed-JD function adds **no** second warning and composes from the preamble alone.
- No new `logger.exception` / `logger.error`. A DB error while resolving propagates to the caller's existing handler (data raises, the handler logs once). The API routes keep their current error handling.
- The existing self-heal `logger.warning` f-string lines in `get_job_data` are left as they are (the Scope says the self-heal path is unchanged).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/tracker.py` | Module docstring; formatting import; new `compose_job_description`; `get_job_data` JD branch; `persist_skipped_job_edits` drops `job_description` | core |
| `src/core/consult.py` | `build_job_token_context`, `qualify_meteorite`, `_jd_ready_for_evaluate`, `evaluate_jd_batch` read the composed JD | core |
| `src/ui/api/api_jobs.py` | Import; new `_compose_jd_for_response`; `list_view` / `detail` call it; `persist_skipped_edits` field tuple + docstring | ui |
| `src/ui/frontend/src/components/JobDetailModal.tsx` | `FieldDraft`, `draftFromJob`, dirty check, save payload drop `job_description`; JD tab read-only | ui |

## Stage 0: Drift check (no commit)

**Done when:** every item below holds on the synced sub, or the builder has stopped and commented.

1. `src/core/gazer.py` defines `resolve_telescope_value(value)` (row id → content, `None` when the row is gone; non-id values returned unchanged) and `_prune_jd(text: str, job_title: str = "") -> str`; `_apply_jd_gates` saves `{ref_key: telescope_data_id}` where `ref_key = TRACKER_CONFIG["job_data_keys"]["jd_telescope_data_id"]`.
2. `src/utils/config.py` `TRACKER_CONFIG["job_data_keys"]` has `"job_description": "job_description"` and `"jd_telescope_data_id": "jd_telescope_data_id"`; `TRACKER_CONFIG["jd_min_chars"]` exists.
3. `src/utils/formatting.py` exports `collapse_consecutive_blank_lines(text: str) -> str`.
4. `src/core/gazer.py` imports `from src.core.tracker import ...` at module level (so tracker must import gazer lazily, as `get_job_data` already does).
5. `git grep -n -E "\.get\((jd_key|[\"']job_description[\"'])" -- src/core src/ui/api ':!src/core/tracker.py'` returns exactly these 9 lines: `consult.py` 1189, 2226, 2238, 2251, 2345, 2386, 2416; `api_admin.py` 1497, 1506 (line numbers may shift by a few; the set of functions must match).
6. `src/core/tracker.py` `get_job_data` and `persist_skipped_job_edits` match the shapes quoted in Stage 1 / Stage 2; `src/ui/api/api_jobs.py` `persist_skipped_edits` builds `fields` from `("job_title", "job_link", "job_description", "state")`.
7. Ruff baselines (`ruff check --no-fix <file> | grep -o 'Found [0-9]* error'`): planner measured **tracker 157**, **consult 224**, **api_jobs 14**.
8. Frontend: `src/ui/frontend/node_modules` is absent in this worktree. Run `cd src/ui/frontend && npm ci` (gitignored; no tracked file changes — confirm `git status --short` is clean afterwards), then record baselines: `npx tsc -b --noEmit` (expect clean) and `npx eslint src/components/JobDetailModal.tsx` (record the count).

If any item does not hold, **stop** and post the 🛑 comment on AST-2130. Do not adapt.

## Stage 1: Composed-JD reader in tracker

**Done when:** `src/core/tracker.py` compiles; a scratch check against a temp DB shows `compose_job_description` returns the stored preamble byte-for-byte when there is no reference, `preamble + "\n\n" + pruned capture` when there is one, the pruned capture alone when the preamble is empty, and the preamble alone (plus the one resolve warning) when the referenced row is gone; `get_job_data(job, "job_description")` returns the composed value without calling `fetch_jd_batch` when it is ≥ `jd_min_chars`.

1. Module docstring: in the `In-scope:` list, after `get_job_effective_resume_structure (AST-2081).`, add ` compose_job_description (AST-2133: preamble + scraped JD, read-only).` On the `get_job_data:` line, replace `return value if present` with `return value if present (JD key: the composed JD)`.
2. Change `from src.utils.formatting import _strip_json_markdown_fences, parse_text` to `from src.utils.formatting import _strip_json_markdown_fences, collapse_consecutive_blank_lines, parse_text`.
3. Directly **above** `async def get_job_data(`, add:
   ```python
   def compose_job_description(job: Dict[str, Any]) -> str:
       """The complete JD every consumer reads (AST-2130): preamble (job_data.job_description — email /
       pasted / agent-parsed text), then the scraped capture referenced by jd_telescope_data_id run
       through the same collapse + prune rules fetch_jd gates on. Read-only — never saved back.

       No reference -> exactly the stored preamble (pasted / meteorite / pre-AST-2130 jobs).
       Reference whose row is gone -> preamble alone (resolve_telescope_value warns once)."""
       # Lazy import: gazer imports tracker at module load (same cycle break as the self-heal below)
       from src.core.gazer import _prune_jd, resolve_telescope_value

       job_data = job.get("job_data") if isinstance(job.get("job_data"), dict) else {}
       keys = TRACKER_CONFIG["job_data_keys"]
       preamble = job_data.get(keys["job_description"]) or ""
       ref = job_data.get(keys["jd_telescope_data_id"])
       if not ref:
           return preamble
       logger.debug("Calling resolve_telescope_value: [%s]", ref)
       raw = resolve_telescope_value(ref) or ""
       logger.debug("Response from resolve_telescope_value: %s", raw)
       # Stored capture is raw (AST-2132); collapse then prune, in _apply_jd_gates order
       scraped = _prune_jd(collapse_consecutive_blank_lines(raw), job.get("job_title") or "")
       # Blank halves drop so a preamble-less scraped job is just the pruned capture
       return "\n\n".join(part for part in (preamble, scraped) if part.strip())
   ```
4. In `get_job_data`, replace everything from the line `# Happy path: value already present and long enough` through `    if key != jd_key:\n        return None` (the happy-path `if` block and the non-JD `return None`) with:
   ```python
       if key != jd_key:
           return job_data.get(key) or None
       # Happy path: composed JD (preamble + referenced capture) already long enough
       composed = compose_job_description(job)
       if len(composed) >= min_chars:
           return composed
   ```
   Leave the self-heal block (`# Self-heal: ...` comment, `astral_job_id = ...`, the `logger.warning(...)`, the `try` / `except` around `fetch_jd_batch`) exactly as it is. Replace the final two lines
   `# job["job_data"] was written back by fetch_jd_batch if successful` / `return job["job_data"].get(jd_key)` with
   ```python
       # fetch_jd_batch wrote the jd_telescope_data_id reference back into job["job_data"] on pass
       return compose_job_description(job) or None
   ```
   Update the docstring's first sentence to: `Return job_data[key]; for the job_description key (from config) return the composed JD (compose_job_description). If that is missing or short: self-heal via fetch_jd_batch, then return the composed JD.` Keep the remaining docstring sentences.
5. `python3 -m py_compile src/core/tracker.py`; ruff count ≤ 157 (Lint gate).
6. Scratch check (`/tmp/AST-2133/stage1.py`, not committed — `debug/` is cursorignored, so use `/tmp`): set `ASTRAL_DB_DIR` to a temp dir **before** importing `src.*` (never the live `data/astral.db`), call `ensure_all_upsert_registry_schemas_at_startup()`, store a capture with `gazer.keep_telescope_data(...)`, then verify the **Done when** cases on in-memory job dicts (no job row needed for compose). For the `get_job_data` case, monkeypatch `src.core.gazer.fetch_jd_batch` to raise so a self-heal call would fail loudly.

⚠️ **Decision:** Separator is one blank line (`"\n\n"`) between preamble and capture. AC 7 says "P followed by the pruned scraped text"; a blank line keeps the two readable as separate blocks in prompts and the modal, and both the modal and `JobAnalysisReportModal` already collapse 3+ newlines.

⚠️ **Decision:** The preamble is returned as stored (no strip, no prune). The Scope applies the prune / collapse rules to the scraped text only, and AC 7 requires the no-reference case to be "exactly today's stored text".

⚠️ **Decision:** `_prune_jd` is imported from gazer (private name, lazy import) rather than copied or moved. Copying would fork the prune rules; moving it edits `gazer.py` (AST-2132's file). Cross-module private import has precedent in gazer's own `_merge_pjl_scrape_record` / `_scrape_pjl_page` imports from roster.

⚠️ **Decision:** The self-heal trigger is "composed JD shorter than `jd_min_chars`" — today's rule ("stored JD shorter than `jd_min_chars`") applied to the value consumers now see. A pasted / pre-AST-2130 job with a long preamble still never self-heals; a job with a short preamble and no reference self-heals and composes preamble + new capture.

## Stage 2: JD is read-only on the edit path

**Done when:** `PUT /api/jobs/<id>` (skipped job, temp DB) with only `{"job_description": "x"}` returns 400 `{"error": "No valid fields to update"}` and `job_data` is unchanged; with `job_title` + `job_description`, the title saves and `job_data.job_description` is unchanged.

1. `src/core/tracker.py` `persist_skipped_job_edits`:
   - Delete the block `if "job_description" in fields:` … `save_job_data(astral_job_id, {jd_key: text})` (4 lines).
   - Docstring: `Persist title/link/JD (and optional state hop) ...` → `Persist title/link (and optional state hop) only when job.state is in SKIPPED_STATES. The JD is read-only (AST-2133) — a job_description field is ignored.`
   - Comment `# Column + JD writes first so an unregistered target still keeps field edits` → `# Column writes first so an unregistered target still keeps field edits`.
2. `src/ui/api/api_jobs.py` `persist_skipped_edits`:
   - Field tuple `("job_title", "job_link", "job_description", "state")` → `("job_title", "job_link", "state")`.
   - Docstring → `Persist title/link/state for a job currently in SKIPPED_STATES (AST-1453). JD is read-only (AST-2133).`
3. `python3 -m py_compile src/core/tracker.py src/ui/api/api_jobs.py`; ruff gate.
4. Scratch check (`/tmp/AST-2133/stage2.py`): temp `ASTRAL_DB_DIR`, create one job in a `SKIPPED_STATES` state, call the route through the Flask test client (auth bypassed the way existing API scratch checks do — e.g. patch `ui.auth.require_auth` before importing the blueprint, or set the app's test auth config), and confirm both **Done when** cases via `get_job`.

⚠️ **Decision:** `persist_skipped_job_edits` silently ignores a `job_description` key instead of raising. The API no longer forwards it (AC 9's 400 comes from the empty-`fields` guard), and no other caller passes it; raising would add an error path nobody hits.

## Stage 3: Every JD consumer reads the composed JD

**Done when:** the AC 8 grep returns only the two `api_admin.py` lines (AST-2134's); a scratch check shows `build_job_token_context(job, ...)["VISIBLE_JD"]`, `_jd_ready_for_evaluate`, and the `evaluate_jd_batch` / `qualify_meteorite` assembled live content carry the composed JD for a job with a reference and the stored text for a job without one.

1. `src/core/consult.py` `build_job_token_context`: replace `visible = (jd_data.get("job_description") or "").strip()` with `visible = tracker.compose_job_description(job).strip()`. Keep the `jd_data = ...` line (phase tokens use it).
2. `qualify_meteorite`:
   - Delete `jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]` (no remaining use after the three edits below — re-grep inside the function before deleting).
   - Loop debug line: `jd_len = len((j.get("job_data") or {}).get(jd_key, "") or "")` → `jd_len = len(tracker.compose_job_description(j))`.
   - `assemble`: `f"CONTENT:\n{(j.get('job_data') or {}).get(jd_key, '') or ''}"` → `f"CONTENT:\n{tracker.compose_job_description(j)}"`.
   - `process`: `input_jd = ((input_job.get("job_data") or {}).get(jd_key, "") or "")` → `input_jd = tracker.compose_job_description(input_job)`.
3. `_jd_ready_for_evaluate`: `jd = ((job.get("job_data") or {}).get("job_description") or "").strip()` → `jd = tracker.compose_job_description(job).strip()`.
4. `evaluate_jd_batch`:
   - Not-ready loop: `jd = ((job.get("job_data") or {}).get("job_description") or "").strip()` → `jd = tracker.compose_job_description(job).strip()`.
   - `assemble`: delete `jd_key = "job_description"` and change `jd_texts = [j.get("job_data", {}).get(jd_key, "") or "" for j in jobs]` → `jd_texts = [tracker.compose_job_description(j) for j in jobs]`.
   - Docstring: `Expects scraped JD in ``job_data``.` → `Reads the composed JD (tracker.compose_job_description).`
5. `_prep_live_content` is **unchanged** — it already reads `tracker.get_job_data(job, "job_description")`, which returns the composed JD after Stage 1.
6. Remove `TRACKER_CONFIG,` from the `from src.utils.config import (...)` block in `consult.py` — planner grep: its only use is the `jd_key` line deleted in step 2. Re-grep first; if another use exists, keep the import and note it in the Review stub.
7. `python3 -m py_compile src/core/consult.py`; ruff count ≤ 224.
8. Run the AC 8 grep; expect only `src/ui/api/api_admin.py` (2 lines).
9. Scratch check (`/tmp/AST-2133/stage3.py`): temp DB; one job dict with preamble + reference, one with preamble only. Call `build_job_token_context` (minimal `candidate_data={}`), `_jd_ready_for_evaluate(job, 80)`; for the batch `assemble` closures, monkeypatch `consult._run_batch_consult` to capture the `assemble` argument and call it on the jobs list.

⚠️ **Decision:** The Scope's "relative-JD" consult path has no direct JD read: consult only parks relative links (`relative_link_state`) and dispatches `fetch_relative_jd`, whose JD save is gazer's (AST-2132). The seven consult hits of the AC 8 grep — token context, qualify_meteorite, evaluate readiness / assemble — are the complete consult set; `_prep_live_content` is covered through `get_job_data`.

⚠️ **Decision:** `evaluate_jd_batch` composes per job in both the readiness split and `assemble` (two resolves per referenced job) rather than caching the composed string on the job dict. Caching would add a mutable side-channel on shared job dicts; jobs without a reference (all pre-AST-2130 jobs) do no DB read at all.

## Stage 4: Job list / detail responses carry the composed JD

**Done when:** `GET /api/jobs/<id>` (temp DB) returns `job_data.job_description` == preamble + `"\n\n"` + pruned capture for a referenced job and exactly the stored text for an unreferenced one (AC 7), `GET /api/jobs?view=<v>` rows carry the same value, and the stored `job_data` is unchanged after both calls.

1. `src/ui/api/api_jobs.py`: add `compose_job_description,` to the `from src.core.tracker import (...)` block (alphabetical: after `candidate_skip_job,`).
2. Directly after `_attach_skipped_edit_meta`, add:
   ```python
   def _compose_jd_for_response(job: dict) -> dict:
       """Response only (AST-2133): job_data.job_description carries the composed JD the UI reads.
       New dict on the row — the stored job_data is never written back."""
       jd = job.get("job_data") if isinstance(job.get("job_data"), dict) else {}
       job["job_data"] = {**jd, "job_description": compose_job_description(job)}
       return job
   ```
3. `list_view`: replace each `_flatten_grades(r)` / `_flatten_grades(ann)` call (7 sites: ready, review, applied, processing, skipped rows, skipped virtual rows) with `_compose_jd_for_response(_flatten_grades(r))` / `_compose_jd_for_response(_flatten_grades(ann))`.
4. `detail`: replace `job = _flatten_grades(job)` with `job = _compose_jd_for_response(_flatten_grades(job))`. (The later `jd = job.get("job_data") ...` / `job["job_data"] = {**jd, "artifacts": art}` lines then carry the composed value through.)
5. `python3 -m py_compile src/ui/api/api_jobs.py`; ruff count ≤ 14.
6. Scratch check (`/tmp/AST-2133/stage4.py`): temp DB, Flask test client as in Stage 2; one referenced and one unreferenced job; confirm the **Done when** lines and that `database.get_job(id)["job_data"]` is byte-identical before and after.

⚠️ **Decision:** The list view composes every row. Rows without a reference return immediately (no DB read); referenced rows do one `telescope_data` read each. A batched resolve would need a new gazer / tracker bulk API outside this Scope — flagged below, not built.

## Stage 5: Job modal shows the JD read-only

**Done when:** `git grep -n "job_description: e.target.value" -- src/ui/frontend` returns nothing; `npx tsc -b --noEmit` is clean; eslint on the file is ≤ the Stage 0 count; the save payload contains only `job_title`, `job_link` and (when changed) `state`.

1. `src/ui/frontend/src/components/JobDetailModal.tsx`:
   - `type FieldDraft`: delete the `job_description: string` member.
   - `draftFromJob`: delete the `job_description: String(...)` property (3 lines).
   - `isDraftDirty`: delete the `|| draft.job_description !== baseline.job_description` line.
   - `handleSave` payload: delete the `job_description: draft.job_description,` line.
   - `showJdTab`: `const showJdTab = fieldsEditable || hasJD` → `const showJdTab = hasJD`.
   - `renderSideContent` `__jd__` branch: delete the whole `if (fieldsEditable && draft) { return ( <textarea ... /> ) }` block, so the branch always renders the existing read-only `<div className="entity-jd-content">{normalized}</div>`. Directly above the `const jd = ...` line add the line comment `// Read-only: composed JD (preamble + scraped text) from the API — not editable (AST-2133)`.
2. `cd src/ui/frontend && npx tsc -b --noEmit`; `npx eslint src/components/JobDetailModal.tsx` (≤ baseline).
3. Run the AC 9 modal grep; expect empty.

⚠️ **Decision:** The JD tab shows only when there is a JD (`hasJD`). It used to show on every skipped job so the operator could type one; with the JD read-only, an always-empty tab on skipped jobs without a JD is dead UI.

## AC traceability

- **AC 7** (JD composes): Stage 1 (`compose_job_description`) + Stage 4 (`detail` / `list_view` response). No-reference jobs return the stored preamble unchanged.
- **AC 8** (one JD reader): Stage 3 removes every consult hit; tracker is excluded by the grep. The two remaining hits are in `src/ui/api/api_admin.py` `_build_adhoc_live_content`, which is **AST-2134's** Scope ("job branch to use the composed-JD function"). AC 8 holds on `ftr` once AST-2134 lands; on this sub the builder confirms the grep returns only those two lines. AST-2134 calls `tracker.compose_job_description(job)`.
- **AC 9** (read-only): Stage 2 (API 400 on JD-only body; title saves, JD unchanged) + Stage 5 (modal grep empty).

## Integration notes (siblings — reference only, not planned here)

- **AST-2134:** use `from src.core.tracker import compose_job_description` (or `tracker.compose_job_description`) in `api_admin._build_adhoc_live_content`'s job branch. Note that branch today falls back to `raw_job_listing` when the JD is empty — that fallback is AST-2134's call to keep or drop.
- **AST-2132 contract consumed:** the reference key is `jd_telescope_data_id`, the stored row is the **raw** capture (pre-collapse, pre-prune), classified jobs carry a reference too (so their composed JD shows the bad page, as today), and `fetch_jd_batch`'s self-heal writes the reference back into the in-memory `job["job_data"]`.

## Flags for Chuckles / Archie (not acted on)

- **List-view resolve cost:** each referenced row in `GET /api/jobs?view=...` does one `telescope_data` read. Fine at today's volumes; a bulk compose (one `get_telescope_data_for_ids` call per list) would need a new gazer/tracker function outside this Scope — needs Susan's approval before anyone adds it.
- **Other API surfaces:** only `list_view` / `detail` (and `PUT`, which returns `detail`) are in Scope. Any other route that returns raw `job_data` (e.g. company or meteorite screens embedding jobs) still shows the preamble only. Planner found no other `src/ui/api` JD read via the AC 8 grep besides `api_admin.py`.

## Lint / compile gate (every stage commit)

- `python3 -m py_compile` on every changed `.py` file.
- `ruff check --no-fix <file>` — finding count must not exceed the Stage 0 baseline (tracker 157, consult 224, api_jobs 14). Fix any new finding on lines this ticket touched; do not clean up pre-existing findings.
- Stage 5 only: `cd src/ui/frontend && npx tsc -b --noEmit` clean; `npx eslint src/components/JobDetailModal.tsx` ≤ baseline.
- **Live DB guard:** scratch checks set `ASTRAL_DB_DIR` to a temp dir before any `src.*` import; nothing runs against `data/astral.db` (symlink to Susan's live DB).

## Boundaries

No gazer JD write or resolve-helper changes (AST-2132). No roster / company paths or admin preview (AST-2134). No data move (AST-2135). No `database.py` / `config.py` changes. No meteorite land paths. No tests or bible edits (Betty).

## Estimate

Confirm Chuckles estimate: 5 — revise to 3 because the reader consumes AST-2132's existing pattern and the rest is mechanical call-site and field removal across four known files (light cross-layer glue).

## Joan validate

[plan-rubric]
**Ticket:** AST-2133
**Overall:** APPROVED
**Corpus:** 26c4e86a4d08addcefdbc3be68116703fedf6762 (canon tree at publish tip; `docs/canon-index.md` absent on ref)
**Publish ref:** `origin/sub/AST-2130/AST-2133-composed-jd` @ `5873f8586e51cf93728d24bdff5aef2c2c11ed61`

## Canon scores

stat.logging.debug | A |
stat.logging.warning | A |
stat.logging.error | A |

## Traceability

AC7 → Stage 1 (`compose_job_description`: preamble + collapse/prune on raw capture, `"\n\n"` join) + Stage 4 (`_compose_jd_for_response` on `list_view` / `detail`, response-only); AC8 → Stage 3 (consult call sites) + tracker as sole reader — **on this sub** grep still hits `api_admin.py` (2 lines) until AST-2134 per plan `## AC traceability`; AC9 → Stage 2 (field tuple / `persist_skipped_job_edits` drop JD; 400 when no valid fields) + Stage 5 (modal read-only + grep).

### discuss — AC 8 vs sibling AST-2134

- **Location:** Child AC 8 (zero grep hits) vs plan Stages 3 / 8 and `## AC traceability`.
- **Finding:** `api_admin._build_adhoc_live_content` remains in the AC 8 pattern until AST-2134; plan documents that and names `tracker.compose_job_description` for 2134. Isolated sub UAT on AC 8 as written will fail until 2134 merges on `ftr`.
- **Recommendation:** Score AC 8 at parent UAT or after 2134; do not widen AST-2133 scope to edit `api_admin.py`.

### discuss — AC 7 separator

- **Location:** Stage 1 Decision (`"\n\n"` between preamble and pruned capture).
- **Finding:** Parent AC says “P followed by the pruned scraped text”; plan adds one blank line for readability (modal/prompts already collapse runs). Likely acceptable for operators; if Susan wants byte-concat with no blank line, clarify before UAT.
- **Recommendation:** Optional parent AC wording note; not a plan blocker.

### acceptable — List-view N× resolve

- **Location:** `## Flags for Chuckles / Archie` / Stage 4 Decision.
- **Finding:** One `telescope_data` read per referenced list row; bulk compose deferred pending approval — honest blast-radius flag.
- **Recommendation:** None at plan stage.

### acceptable — Lazy `_prune_jd` import from gazer

- **Location:** Stage 1 `compose_job_description`.
- **Finding:** Reuses gate-order prune rules without editing AST-2132’s file; cycle broken via lazy import (same pattern as existing tracker↔gazer).
- **Recommendation:** Builder follows plan; no duplicate prune copy.

### acceptable — No `## Self-assessment` block

- **Location:** Plan structure (`## Estimate` confirm only).
- **Finding:** Stage 0 drift gate + five stages carry complexity; not blocking.

**R6 (summary):** Four-file scope matches ticket. Composed reader, self-heal on composed length, read-only API/modal, and consult rewires align with parent functional items 6–7 and child Boundaries (no gazer/roster/migration). Stage 0 gates on AST-2132 symbols on the sub (`resolve_telescope_value`, `jd_telescope_data_id` save path). No `fix-now` gaps.

context_tokens≈62000

## Review

- **Branch:** `origin/sub/AST-2130/AST-2133-composed-jd`
- **Stage 0:** drift check clean — `resolve_telescope_value` / `_prune_jd` in gazer, `jd_telescope_data_id` + `jd_min_chars` in config, `collapse_consecutive_blank_lines` in formatting; AC 8 grep = the 9 planned lines; ruff baselines tracker 157 / consult 224 / api_jobs 14; `npm ci` (tree clean after), `tsc -b --noEmit` clean, eslint on the modal 0.
- **Stage 1:** `0676bb4c0` — `compose_job_description`; `get_job_data` JD key returns the composed JD, self-heal block unchanged.
- **Stage 2:** `ddaa166e3` — `persist_skipped_job_edits` ignores `job_description`; `PUT /api/jobs/<id>` no longer accepts it.
- **Stage 3:** `28b551d4c` — consult token context, `qualify_meteorite`, `_jd_ready_for_evaluate`, `evaluate_jd_batch` read the composed JD. **Kept** `jd_key` in `qualify_meteorite` and the `TRACKER_CONFIG` import: the step-2 re-grep found one more use — the `parsed_job` write (`jd_key: jd_text`) that lands the meteorite JD as preamble — so deleting the line was wrong; the plan's re-grep fallback (step 6) applied.
- **Stage 4:** `83b19402c` — `_compose_jd_for_response` on every `list_view` row and in `detail`. Call-site count is **6** (5 `r` + 1 `ann`), not the "7" in the plan text; the plan's own list names those 6 — all were converted.
- **Stage 5:** `a010c737d` — modal JD read-only, out of draft / dirty check / payload; JD tab shows only when there is a JD.
- **Verify:** `py_compile` OK; ruff tracker 156 (baseline 157), consult 224, api_jobs 14; tsc clean, eslint 0; AC 8 grep → only `api_admin.py` 1497 / 1506 (AST-2134); AC 9 modal grep empty. Scratch checks (temp `ASTRAL_DB_DIR` under `/tmp`, DB path asserted): Stage 1 compose cases (no ref exact, ref + preamble, ref only, missing row → preamble + one warning) and `get_job_data` no self-heal on long composed; Stage 2 JD-only PUT → 400, title + JD → title saved, JD unchanged; Stage 3 token context / readiness / evaluate + qualify assembled content carry the composed JD; Stage 4 detail + skipped list return the composed JD, stored `job_data` byte-identical.
- **Existing tests (Betty):** over the 12 test files that reference the touched functions, 3 new failures vs untouched ftr (pre-existing reds there unchanged), all asserting the pre-AST-2133 contract: `test_tracker.py::TestAst1453PersistSkippedJobEdits::test_writes_title_link_jd_then_transition` and `::test_empty_jd_persists_without_strip_whole_blob` (expect the JD write), `test_api_jobs.py::TestJobsRoutes::test_list_processing_filters_score_floor` (expects `job_data == {}`; now carries the composed `job_description`). `test_page_intake.py` fails collection on both trees (missing module) — not this ticket's.
- **No new tests** — coverage is Betty's (qa-child).

## Radia review

[code-rubric]
**Ticket:** AST-2133
**Publish ref:** `ef7cfc97498a8957151b59f6c500ff7fc56e0c1a` (`origin/sub/AST-2130/AST-2133-composed-jd`)
**Corpus:** `0d01e20d2b313a4e35cf3d07434b6cd69f615768`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.debug | A | | |
| stat.logging.warning | A | | |
| stat.logging.error | A | | |

## Column diff vs plan stage

(aligned) — Joan scored all three logging directives **A**; code review matches.

## Frame diff

- [ ] **AC7:** `GET /api/jobs/<id>` (and list views) return composed `job_data.job_description` (preamble + pruned capture when `jd_telescope_data_id` set); no-reference jobs return stored preamble only — `TestAst2133ComposeJobDescription`, `TestAst2133ComposedJdResponses`, E2E PUT tests.
- [ ] **AC8:** Consult paths use `tracker.compose_job_description` / `get_job_data(..., "job_description")`; **not** literal zero-hit grep until AST-2134 — `api_admin.py` lines 1497 / 1506 remain (documented sibling).
- [ ] **AC9:** JD-only `PUT` → 400 / unchanged blob; title + JD → title only; modal grep empty; skipped persist ignores `job_description`.

## Findings

### fix-now

(none)

### discuss

- **AC8 vs Linear wording @susan:** Ticket AC8 requires zero grep hits; tip still has two `api_admin.py` reads (plan + Joan: AST-2134). **Default:** Treat AC8 as satisfied for **AST-2133** scope (`tracker` + consult + `api_jobs` rewired); run the strict grep as a **parent UAT** gate after AST-2134 lands on `ftr` — do not widen this child to edit `api_admin.py` in `resolve-child`.
- **AC7 separator @susan:** `compose_job_description` joins preamble and pruned capture with `"\n\n"` (plan Decision); parent AC text says “P followed by” without mandating a blank line. **Default:** Keep `"\n\n"` unless UAT shows a consumer that requires byte-adjacent concat.

### advisory

- **Sibling diff carry:** Three-dot diff vs `origin/dev` includes full AST-2131 / AST-2132 stack (`gazer.py`, `database.py`, …) — expected on stacked subs; score AST-2133 on the four scoped files (+ their tests).
- **Plan §Boundaries vs qa-child:** Betty landed `TestAst2133*`, revised `TestAst1453PersistSkippedJobEdits`, `test_api_jobs` processing-list expectation, bible sections — overrides “No tests or bible edits.”
- **Issue doc `## Review`:** “3 failures / no new tests” is stale vs tip `ef7cfc974` (tests revised on branch).
- **List-view cost:** Each referenced row in list views calls `compose_job_description` → one resolve/read per job (plan flag); bulk compose deferred — not a canon defect.
- **Other API surfaces:** Routes outside `api_jobs` `list_view` / `detail` may still expose raw stored `job_data` (plan Flags) — out of scope until a future ticket.

## Notes (Canon Scope — not scored)

- `consult.qualify_meteorite` correctly **keeps** `jd_key` for the meteorite `parsed_job` preamble write (`jd_key: jd_text`); reads go through `compose_job_description`.
- `get_job_data` self-heal unchanged in spirit: short composed JD still triggers `fetch_jd_batch`; success returns `compose_job_description(job)` (reference path), not raw blob text.

## What’s solid

- **Single reader:** `compose_job_description` in `tracker.py` — preamble, `resolve_telescope_value` on `jd_telescope_data_id`, `collapse_consecutive_blank_lines` + lazy `_prune_jd`, `"\n\n"` join; never writes composed text back.
- **Consumers:** consult token context, meteorite qualify/evaluate, `_jd_ready_for_evaluate`; `api_jobs` `_compose_jd_for_response` on all list branches + `detail`; `persist_skipped_edits` / `persist_skipped_job_edits` drop JD writes.
- **UI:** `JobDetailModal` JD read-only; AC9 frontend grep empty.
- **Logging:** `compose_job_description` uses ungated `Calling` / `Response` `logger.debug` around resolve; no new exception swallowing in added paths.

## Recommended actions (downstream — not for Radia)

- Chuckles: append artifact, `docs(AST-2133): Radia review — clean`, post slim upshot, **Review Posted** → datt **PROCEED** to **User Testing**.
- UAT AC7–9 on this sub; defer strict AC8 grep to post–AST-2134 on `ftr` (discuss defaults above).
- Optional: trim stale build `## Review` paragraph when appending.

context_tokens≈34000

---
