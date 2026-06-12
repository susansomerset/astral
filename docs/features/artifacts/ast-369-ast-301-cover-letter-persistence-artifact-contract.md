# AST-369 — [AST-301] cover-letter persistence + artifact contract integration

**Linear:** [AST-369](https://linear.app/astralcareermatch/issue/AST-369/ast-301-cover-letter-persistence-artifact-contract-integration)  
**Feature branch:** `<agent>/ast-369-ast-301-cover-letter-persistence-artifact-contract`  
**Parent:** [AST-301](https://linear.app/astralcareermatch/issue/AST-301)

## Summary

Ensure **`job_data.artifacts.cover_letter`** persists as the **`{ re_line, body, signature }`** object end-to-end: from **`craft_job_cover_letter`** (or merge step) through **`tracker` / `database.save_job_data`** to UI/editor/print consumers (**`builder._resolve_cover_letter`**, JAR panels). Align dispatch transitions so the cover-letter pipeline runs **after** resume-first sequencing agreed in **AST-301**. This ticket is **integration glue** — if **AST-309** or **AST-302** already landed the schema or states, **rebase** and shrink this plan to only the remaining gaps (document deltas in **Revisions**).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/tracker.py` | Ensure public save path merges `artifacts.cover_letter` without dropping keys; add thin wrapper if missing. | core |
| `src/core/dispatcher.py` (or artifact runner) | Trigger ordering vs resume artifact task — match **AST-301** doc or Linear parent comments. | core |
| `src/data/database.py` | Only if job JSON merge drops unknown keys — fix merge. | data |
| `src/ui/api/api_jobs.py` | PATCH/GET exposes `cover_letter` shape for editor (if not already). | ui |

## Stage 1: Trace write path

**Done when:** Documented list of functions from Anthropic response → `job_data` on disk (in plan **Revisions** after code inspection).

1. Grep `cover_letter` across `src/`.
2. Add missing merge in the single canonical save function.

## Stage 2: Trace read path

**Done when:** `get_job` JSON matches what `builder` and React editor read.

1. Hit `/api/jobs/<id>` (or relevant route) and verify JSON shape manually.

## Stage 3: Dispatch order

**Done when:** Cover letter task does not run before prerequisite state from **AST-301** / **AST-302**.

1. Inspect `dispatch_tasks` trigger_state values after **AST-302** lands; adjust only if this branch still owns sequencing.

## Self-Assessment

**Scope — `MAJOR-CHANGE`**  
Crosses core + API + dispatch configuration.

**Conf — `LOW`**  
Depends on multiple upstream tickets landing first.

**Risk — `HIGH`**  
Silent data loss if merge mishandles `artifacts`.

## Self-review vs ASTRAL_CODE_RULES

§2.4 batch claims unchanged; only artifact payload shape.

---

## Review (build)

**Branch:** `ftr/AST-369`  
**Commit:** (see Linear build comment)

**Revisions:** Resume-first cover letter via `_run_cover_letter_for_job` after resume chain; `CANDIDATE_REVIEW` dispatch for `craft_job_cover_letter`; shares `persist_job_artifact_from_parsed` with AST-371.
