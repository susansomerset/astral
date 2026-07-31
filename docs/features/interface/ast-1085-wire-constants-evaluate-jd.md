# Wire constants into evaluate_jd rubric path

**Linear:** [AST-1085](https://linear.app/astralcareermatch/issue/AST-1085/wire-constants-into-evaluate-jd-rubric-path-add-a-constant-set-of)
**Parent:** [AST-1077](https://linear.app/astralcareermatch/issue/AST-1077/add-a-constant-set-of-rubric-vectors-to-generated-jd-evaluate-vectors)
**Publish ref:** `sub/AST-1077/AST-1085-wire-constants-evaluate-jd`

Always-merge Quality Check (**QC**) and Gut Check (**GC**) from `EMBEDDED_EVALUATE_JD_CRITERIA` (AST-1084) into the `evaluate_jd` / `jobdesc_rubric` criteria path — **append** after candidate-authored rows, restore on hydrate / generate / save if missing, dedupe by code (embedded wins). Hard-fail on F uses the existing evaluate_jd dealbreaker; no other rubric owners change.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Import `EMBEDDED_EVALUATE_JD_CRITERIA`; add append-merge helper; wire hydrate / save / generate restore for `evaluate_jd` only | core |

No `config.py` edits (definitions are AST-1084). No `consult.py` / dispatcher / UI / other rubric-owner changes.

## Stage 1: Append-merge helper + hydrate

**Done when:** `rubric_criteria_for_task(candidate_id, "evaluate_jd")` returns candidate criteria with QC then GC **appended** from `EMBEDDED_EVALUATE_JD_CRITERIA`, deduped by code (embedded row wins). Other owner keys (`prefilter_company`, `grade_do`, etc.) are unchanged. GET candidate hydration (`hydrate_rubric_artifacts_for_response` → `jobdesc_rubric`) surfaces both constants after candidate rows.

1. In `src/core/candidate.py`, add `EMBEDDED_EVALUATE_JD_CRITERIA` to the existing `src.utils.config` import block (next to `EMBEDDED_COMPANY_PREFILTER_CRITERIA`).

2. Immediately above `rubric_criteria_for_task`, add a private helper:

   ```python
   def _merge_embedded_evaluate_jd_criteria(criteria: list) -> list:
       """Append EMBEDDED_EVALUATE_JD_CRITERIA; embedded wins on duplicate code (AST-1085)."""
       embedded_codes = {
           str(c.get("code")).strip().upper()
           for c in EMBEDDED_EVALUATE_JD_CRITERIA
           if isinstance(c, dict) and c.get("code")
       }
       head = [
           c
           for c in (criteria or [])
           if isinstance(c, dict)
           and str(c.get("code") or "").strip().upper() not in embedded_codes
       ]
       return head + list(EMBEDDED_EVALUATE_JD_CRITERIA)
   ```

3. In `rubric_criteria_for_task`, after the existing `prefilter_company` branch (and before the bare `return criteria`), add:

   ```python
   if owner_task_key == "evaluate_jd":
       return _merge_embedded_evaluate_jd_criteria(criteria)
   ```

   Keep the `prefilter_company` prepend branch exactly as it is today.

⚠️ **Decision:** Reuse the RC merge shape (strip matching codes from candidate rows, then place embedded rows) but **append** instead of prepend — locked by parent Architectural definition / AC#2. Embedded wins on duplicate `QC`/`GC` so restore always re-applies config text/importance, not a stale operator edit of those codes.

⚠️ **Decision:** Single helper owned by `candidate.py` (same module as `rubric_criteria_for_task`) — no second embedding mechanism in consult/agent.

## Stage 2: Restore on save and generate

**Done when:** Saving `jobdesc_rubric` without QC/GC persists them from config (appended). Generating `craft_jobdesc_rubric` returns and stashes criteria with QC/GC appended. Dispatch persist for `craft_jobdesc_rubric` also merges before `sync_rubric_vectors_from_criteria`. evaluate_jd batch grading continues to read criteria via `rubric_criteria_for_task` → constants participate in existing F-dealbreaker with no consult changes.

1. In `apply_rubric_vectors_save`, inside the loop after validating `val` is a list and `owner` is resolved, immediately before `database.sync_rubric_vectors_from_criteria(...)`:

   ```python
   if owner == "evaluate_jd":
       val = _merge_embedded_evaluate_jd_criteria(val)
   ```

   Then sync that `val` (not the pre-merge list). This covers UI candidate save (`api_candidate` → `normalize_rubric_artifacts_on_save` → `apply_rubric_vectors_save`) and any other caller of `apply_rubric_vectors_save` for `jobdesc_rubric`.

2. In `_persist_craft_dispatch_success`, in the `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` branch, after validating `criteria` is a non-empty list and **before** building `arts`:

   ```python
   if artifact_key == "jobdesc_rubric":
       criteria = _merge_embedded_evaluate_jd_criteria(criteria)
   ```

3. In `run_candidate_artifact_generation`, inside the `_is_craft_rubric_ui_task` success path, after the empty-criteria rejection and **before** `_stash_pending_craft_generation(...)`:

   ```python
   if task_key == "craft_jobdesc_rubric" and isinstance(parsed_response, dict):
       crit = parsed_response.get("criteria")
       if isinstance(crit, list):
           parsed_response["criteria"] = _merge_embedded_evaluate_jd_criteria(crit)
           criteria_count = len(parsed_response["criteria"])
   ```

   Ensure the mutated `parsed_response` is what gets stashed and returned in the 200 body so the Artifacts editor shows QC/GC without a separate hydrate round-trip.

4. Do **not** modify `consult.py`, `_render_pass_fail`, `_render_score`, dispatcher claim surfaces, DO/GET/LIKE/joblist/company-prefilter merge paths, or `EMBEDDED_EVALUATE_JD_CRITERIA` itself. F on QC/GC hard-fails via the existing evaluate_jd dealbreaker once those vectors are in the hydrated criteria list used by `evaluate_jd_batch`.

⚠️ **Decision:** Restore-on-save lives in `apply_rubric_vectors_save` (owner gate) rather than `normalize_rubric_artifacts_on_save` so grade-table normalization still runs on candidate-authored rows first, and merge/append is a single owner-specific step next to persist.

⚠️ **Decision:** No one-time DB backfill — existing candidates pick up QC/GC on next hydrate / generate / save (parent Boundaries).

⚠️ **Decision:** `get_pending_craft_generation` for `craft_jobdesc_rubric` will behave like company-prefilter after this change: `rubric_criteria_for_task(..., "evaluate_jd")` is never empty once embedded rows exist, so page-return recovery stays 404 when the table/hydrate path already surfaces criteria. That matches Susan’s AST-905 prefilter ruling (restore only when none already). Do not special-case “empty means no candidate rows ignoring embedded.”

## Self-Assessment

**Scope:** `Single-Component` — one core module (`candidate.py`) wires the AST-1084 config constant into evaluate_jd hydrate/save/generate; consult/UI unchanged.

**Conf:** `high` — mirror of `prefilter_company` + `EMBEDDED_COMPANY_PREFILTER_CRITERIA` with append order and three call sites named by the ticket AC.

**Risk:** `Medium` — wrong merge order or owner gate would either omit QC/GC from evaluate_jd (breaking hard-fail / editor visibility) or leak constants into another rubric owner if the `evaluate_jd` / `jobdesc_rubric` gates are mistyped.

## Rules check

- §1.3 DRY — one `_merge_embedded_evaluate_jd_criteria`; hydrate/save/generate all call it; no second embedding mechanism.
- §2.1 / `astral.config.config-source-of-truth` — consume `EMBEDDED_EVALUATE_JD_CRITERIA` only; no inline QC/GC prose in core.
- `astral.standards.no-hardcoded-sets` — codes/labels/grades stay in config.
- `astral.agent.grade-vector-validation` — no new grade letters; agent still grades from criterion `grade_descriptions` (QC A/B/C/F, GC A–D/F/X from AST-1084).
- §3.3 / `astral.layers.import-direction` — core imports utils config; no UI→core inversion; no consult import of the constant.
- `astral.standards.in-scope-only` — only `evaluate_jd` / `jobdesc_rubric` / `craft_jobdesc_rubric`; other owners untouched.
- `pattern.config.config-block` — consume the organized block from AST-1084.

## Out of scope (do not implement)

- Redefining or editing `EMBEDDED_EVALUATE_JD_CRITERIA` text (AST-1084).
- DO / GET / LIKE / joblist / company-prefilter constant vectors.
- Scoring math, importance multipliers, or dealbreaker rule changes.
- Jobs list / Recommended Job Modal display (AST-1059 / 1063 / 1064).
- Admin UI to edit constant definitions.
- One-time `rubric_vector` backfill migration.

## Review

- **Commit:** `889a68d7`
- **Branch:** `sub/AST-1077/AST-1085-wire-constants-evaluate-jd`

### Radia — code-rubric.v1 (2026-07-31)

[code-rubric] revision=1
**Overall:** DISCUSS (product CLEAN; plan-exclusion stragglers on three-dot diff)

**What's solid**
- `_merge_embedded_evaluate_jd_criteria` + hydrate/save/generate call sites match Stage 1/2 literals (append; embedded wins).
- Owner gates limited to `evaluate_jd` / `jobdesc_rubric` / `craft_jobdesc_rubric`; consult reads hydrate via `rubric_criteria_for_task`.
- `code(AST-1085)` touches only `src/core/candidate.py`; one Betty `merge-tests`.

**Issues (discuss)**
- Stragglers vs Joan Excluded (in-scope on `origin/dev...publish-ref` because plan + Betty tests + AST-1084 config landed on the sub): `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.utils-data-late-import-only`, `astral.ui.single-gunicorn-worker`. All score **conforms**; no product fix.

**Recommended actions**
- resolve-child: acknowledge stragglers; no src change required.

## Resolution

**2026-07-31 — resolve-child (Ada)**

- **fix-now:** none.
- **discuss (stragglers):** acknowledged — `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.ui-config-driven-business-logic`, `astral.standards.utils-data-late-import-only`, and `astral.ui.single-gunicorn-worker` were Joan-Excluded against plan Files Changed `{core}` but appear on the three-dot diff once plan + Betty test-tree + AST-1084 config landed. All six scored **conforms** in Radia's review; no product or plan change.
- **advisory:** craft persist + `apply_rubric_vectors_save` double-merge is idempotent — left as-is (helper is safe to call twice).
- **src:** no change this pass (`889a68d7` already matches Stages 1–2).
