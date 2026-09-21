# AST-1757 — Land staged job_title onto job

**Linear:** [AST-1757](https://linear.app/astralcareermatch/issue/AST-1757/land-staged-job-title-onto-job-stage-email-meteorite-enhancements)  
**Parent:** [AST-1753](https://linear.app/astralcareermatch/issue/AST-1753/stage-email-meteorite-enhancements) — stage_email_meteorite enhancements  
**Publish ref:** `sub/AST-1753/AST-1757-land-staged-job-title-onto-job`

When a meteorite lands, flow a non-empty staged `meteorite.job_title` onto the job record via `tracker.save_meteorite_job`. Enrich/qualify title wins when present; otherwise use the meteorite column. Does **not** edit agent_task prompts (**AST-1755**) or stage `jd_text`→blob fallback (**AST-1756**).

## UAT fitness

- **AC restored:** Parent AC7 — `rg -n 'job_title' src/core/meteorite.py` shows the dispatch land runner (`run_land_meteorite`) passing `job_title` into `tracker.save_meteorite_job`. Fail if that call site still omits `job_title=`. Parent AC8 — Landing a READY meteorite whose row `job_title` is non-empty and whose enrich/qualify title is empty yields a `job` row whose `job_title` equals the meteorite column. Fail if `job.job_title` is NULL/blank while `meteorite.job_title` was set. Parent AC9 — Landing when enrich/qualify returns a non-empty `job_title` keeps that enrich title on `job` even if the meteorite column differs. Fail if staged title overwrites a non-empty enrich title.
- **Correct outcome:** After land, the job’s title is the enrich/qualify title when Ruth returned one; otherwise it is the staged meteorite `job_title` when that column was set — so operators see a useful title on the job before (or without) a separate qualify pass inventing one.
- **Sibling check:** **AST-1755** owns asking Ruth for optional `job_title` in `stage_meteorite` prompts and leaving the column on the meteorite row (already User Testing). **AST-1756** owns stage-map `content` fallback when `jd_text` is blank — disjoint edit sites in `meteorite.py` (stage map only). This ticket only wires land save `job_title=`; do not touch stage map, prompts, or `config.py`. Verified by Scope partition + no stage-map / `agent_task.json` rows in Files Changed.
- **Not sufficient:** Removing a missing-kwarg / silent-None symptom alone is **not** done — both land call sites must apply the enrich-preferred / staged-fallback rule, and AC8/AC9 outcomes must hold on real land.
- **Wrong fix rejected:** Always preferring staged `meteorite.job_title` over a non-empty enrich title would break AC9. Passing `job_title` only on one of the two land paths (dispatch vs public) would leave AC7 or the public-path half of AC8/AC9 unsatisfied. Inventing titles in land when both enrich and staged are empty is out of scope and forbidden by the epic brief.

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/core/meteorite.py` — **modified** — dispatch land and public land paths pass staged `job_title` through to `tracker.save_meteorite_job` (enrich title preferred when present). Technical: in the READY/BOT_BLOCKED dispatch land runner, pass the meteorite row's `job_title` into the Tracker save call when non-empty; in the public land path after enrich, fall back to the meteorite row's `job_title` when enrich omitted one (same preference pattern already used for employer name from scrap metadata).

All Files Changed / Stages stay inside that set.

**Out of scope (siblings / other):**

- `data/admin/agent_task.json` stage prompts — **AST-1755**
- Stage map / ingress-blob `jd_text` fallback — **AST-1756** (disjoint sites in `meteorite.py`)
- `src/core/tracker.py` / `save_meteorite_job` signature — already accepts `job_title=`; do not change Tracker
- Paste / HTML create helpers that call `save_meteorite_job` without enrich (e.g. non-dispatch create paths) — not named in this ticket’s Scope
- New info logs for title (statutes: keep existing entity info / debug call-response only)

**Depends on:** after **AST-1755** for full end-to-end title UAT (prompts populate the column). Land wiring itself does not require that sibling’s code on this branch — staged column may already exist from prior stage map.

**AC partition (this ticket):** Parent AC7–AC9 only.

**Canon Scope:** `patt.task.daisy-chain` (full — consume the staged meteorite column through land; do not invent a parallel title extract). `stat.logging.debug`, `stat.logging.info.entity` — placement: keep existing debug call/response and entity info lines; **no** new title- or fallback-specific info logs.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/meteorite.py` | `run_land_meteorite`: pass non-empty row `job_title` into `tracker.save_meteorite_job`. `land_meteorite` enrich loop: `job_title=` = enrich title if non-empty else meteorite row `job_title` | core |

## Stage 1: Dispatch land — pass staged job_title

**Done when:** `run_land_meteorite`’s `tracker.save_meteorite_job` call includes `job_title=` from the claimed meteorite row when non-empty (empty/None → omit value as `None`); `rg -n 'job_title' src/core/meteorite.py` shows that call site; `python3 -m py_compile src/core/meteorite.py` succeeds.

1. In `src/core/meteorite.py` `run_land_meteorite`, inside the per-row try **after** content/empty-BOT_BLOCKED gates and **before** `tracker.save_meteorite_job` (~line 1906 today):

   - Read staged title from the claimed batch row:

     ```python
     staged_title = (row.get("job_title") or "").strip() or None
     ```

     (`row` is the meteorite batch dict from `get_meteorite_batch`.)

2. Add `job_title=staged_title` to the existing `tracker.save_meteorite_job(...)` kwargs (alongside `job_data`, `job_link`, `employer_name=None`, etc.). Do **not** change claim states, content gates, LANDED transitions, or `_entity_info` / `_meteorite_state_info` lines.

3. Logging: leave the existing debug “Calling tracker.save_meteorite_job” / “Response from …” pair unchanged. Do **not** add an info line that mentions title.

⚠️ **Decision:** Dispatch land has no enrich step — staged column is the only title source here. Preferring enrich is only for the public `land_meteorite` path (Stage 2). That matches Scope’s split wording and AC7’s focus on `run_land_meteorite`.

## Stage 2: Public land — enrich title wins; else meteorite column

**Done when:** In `land_meteorite`’s enrich job loop, `tracker.save_meteorite_job` receives enrich `job_title` when non-empty; when enrich title is blank/missing, it receives the meteorite row’s `job_title` when that column is non-empty; when both empty, passes `None`. Existing `_entity_info` on ok outcomes unchanged. `python3 -m py_compile src/core/meteorite.py` succeeds.

1. In `land_meteorite`’s loop over `enriched_jobs` (today ~1159–1191), after `mrow = get_meteorite(mid) or {}` (already present for link inherit) and **before** `tracker.save_meteorite_job`:

   - Resolve title with enrich-preferred / staged-fallback (same preference shape as enrich’s `ruth_emp or scrap["employer_name"]`, but applied at save time from meteorite row):

     ```python
     enrich_title = (row.get("job_title") or "").strip()
     staged_title = (mrow.get("job_title") or "").strip()
     title_for_save = enrich_title or staged_title or None
     ```

   - Replace today’s `job_title=row.get("job_title") or None` with `job_title=title_for_save`.

2. Do **not** change `enrich_meteorite_land_packet` (Ruth title extraction stays as today). Do **not** edit stage-map code, prompts, or Tracker. Do **not** touch paste/HTML create helpers outside this loop.

3. Logging: no new always-on info for title preference; keep existing debug call/response and `_entity_info` on success.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1757
**Overall:** APPROVED
**Corpus:** 2ac86c3f693409c364f8630a97198c8dbfa9c6f3
**Publish ref:** `sub/AST-1753/AST-1757-land-staged-job-title-onto-job` @ `b51b33a346838be6f0e90ac481a3f315b5b10260`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.task.daisy-chain | A | | |
| stat.logging.debug | A | | |
| stat.logging.info.entity | A | | |

## Traceability

AC7→Stage 1 §1–2 ( `run_land_meteorite` passes `job_title=staged_title` into `tracker.save_meteorite_job` ); AC8→Stage 2 §1 (enrich blank → meteorite row `job_title` via `title_for_save` ); AC9→Stage 2 §1 (enrich non-empty wins over staged column )

## Findings

### acceptable

- **Location:** Stage 1 ⚠️ Decision — dispatch vs public enrich split  
- **Finding:** `run_land_meteorite` has no enrich hop; staged column is the sole title source there. Public `land_meteorite` applies enrich-preferred / staged-fallback at save time — matches parent AC7 wording and AC8/AC9 enrich scenarios.  
- **Recommendation:** None.

- **Location:** Scope gate — paste/HTML create path (~line 376)  
- **Finding:** Another `tracker.save_meteorite_job` call still omits `job_title=`; plan explicitly excludes non-dispatch create helpers. Parent AC7 names `run_land_meteorite` only — in scope.  
- **Recommendation:** None.

- **Location:** ## UAT fitness  
- **Finding:** Plan documents correct AC8/AC9 outcomes, sibling boundaries, and rejected wrong fixes (staged-over-enrich, single-path wiring, invented titles) — stronger adversarial coverage than rg/py_compile alone.  
- **Recommendation:** None.

### discuss

- **Location:** Stage 1–2 Done when / verify  
- **Finding:** AC7 gate is `rg` + `py_compile`; AC8/AC9 have no inline epic-worktree assert script (unlike AST-1756). Behavioral proof deferred to Tests Ready / UAT.  
- **Recommendation:** Optional: Betty lands land-path cases for enrich-empty vs enrich-present; not blocking plan approval given UAT fitness section and pinned edit sites.

## R6 checklist (summary)

- Definition fidelity: `src/core/meteorite.py` land paths only; parent AC7–AC9 addressed; siblings AST-1755/AST-1756 excluded; Tracker signature unchanged.  
- DRY / scope: reuses existing `save_meteorite_job` kwarg and employer-name preference shape; no stage-map or prompt edits.  
- Self-assessment: Estimate `2 — agree` matches two call-site edits and no new logging.  
- Plan Discuss: status `Plan Ready`, assignee Joan, zero completed `[plan-discuss]` rounds.

context_tokens≈26500

[plan-rubric] PROCEED (Commit: b51b33a346838be6f0e90ac481a3f315b5b10260) Land staged job_title wiring

## Review (build stub)

**Publish ref:** `origin/sub/AST-1753/AST-1757-land-staged-job-title-onto-job`  
**Plan path:** `docs/features/meteorite/ast-1757-land-staged-job-title-onto-job.md`

**Built tip:** `079c0593f92903988ca4db83620725901a09902d` (`079c0593`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–2 | `079c0593` | `run_land_meteorite` + `land_meteorite` pass staged/enrich-preferred `job_title=` |

**Betty note:** AC8/AC9 land preference cases deferred to qa-child (engineer test-tree ban).

## Radia review

[code-rubric]
**Ticket:** AST-1757
**Publish ref:** `17085cf80f99aa2ab1f99a0b5433d4623378dc17` (`origin/sub/AST-1753/AST-1757-land-staged-job-title-onto-job`)
**Corpus:** `2ac86c3f693409c364f8630a97198c8dbfa9c6f3`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.task.daisy-chain | A | | |
| stat.logging.debug | A | | |
| stat.logging.info.entity | A | | |

## Column diff vs plan stage

(aligned) — Joan scored all three directives **A**; diff confirms same.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

- **Location:** `docs/uat-fixtures/AST-756/expected-agent_task.json`, `tests/component/core/test_repo_admin_json.py::TestAst1755StageMeteoriteJobTitlePrompts`, `docs/test-bible/core/repo_admin_json.md` § AST-1755
- **Finding:** Sibling **AST-1755** artifacts ride this publish ref via `merge-tests`, but `data/admin/agent_task.json` on this tip still lacks AST-1755 `job_title` prompts — fixture bytes ≠ catalog bytes. AST-1757 manifest correctly scopes to meteorite land tests only, so **Tests Passed** is valid.
- **Recommendation:** No action on AST-1757 product; avoid running AST-1755 fixture lockstep outside its own ref. Chuckles may note for epic rollup hygiene.

- **Location:** `tests/component/core/test_meteorite.py::TestAst1756IngressBlobJdTextFallback`
- **Finding:** Sibling **AST-1756** test class merged without `ingress_blob` product code on this tip — would `TypeError` if run outside manifest.
- **Recommendation:** Same merge-tests pattern as AST-1755/1756 reviews; manifest omission is correct.

### advisory

- **Location:** `docs/test-bible/core/meteorite.md` § AST-1757
- **Finding:** Bible shasum line still reads “record after publish.”
- **Recommendation:** Chuckles stamps on doc writeback.

## What's solid

- Product diff is minimal and plan-exact (~9 lines in `src/core/meteorite.py` only): `run_land_meteorite` passes `job_title=staged_title` from claimed row; `land_meteorite` uses `title_for_save = enrich_title or staged_title or None` (AC7–AC9).
- No new `logger.debug` / `logger.info` / `_entity_info` lines — existing call/response pairs untouched; inline comments only.
- Consumes staged `meteorite.job_title` through land save — no parallel title extract (`patt.task.daisy-chain`).
- `TestAst1757LandStagedJobTitle` covers dispatch pass (AC7), enrich-blank→staged (AC8), enrich-wins-over-staged (AC9) — closes Joan’s plan-stage discuss on deferred behavioral proof.
- Sibling boundaries hold: no `agent_task.json`, no stage-map / `ingress_blob`, no Tracker signature edits.
- Estimate **2 — agree** still fits.

## Recommended actions (Chuckles downstream — not Radia)

- Append artifact; `docs()` push on publish ref.
- Post slim upshot `--as radia`.
- Move to **Review Posted** → **PROCEED** / User Testing path.

```
[code-rubric] PROCEED (Commit: 17085cf8) land job_title wiring clean
```
