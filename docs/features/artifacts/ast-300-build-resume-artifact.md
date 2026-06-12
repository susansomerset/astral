# Build Resume Artifact

**Linear:** https://linear.app/astralcareermatch/issue/AST-300/build-resume-artifact  
**Feature branch:** `<agent>/ast-300-build-resume-artifact`

Daisy-chain **`do_task()`** pipeline that produces **job-scoped** structured JSON resume content in **`job_data.artifacts.resume_content`**, shape from **`BUILD_CONFIG.artifact_shapes`** (see **AST-296**). Early passes cache base resume text in agent cache slots; a **promotion** step replaces that slot with revised content so later agents never read stale text. Trigger when job reaches **`RECOMMENDED`** (exact trigger wiring in **AST-371** with tracker). **AST-370** owns do_task/token chain plumbing; **AST-371** owns persistence + dispatch trigger. This parent plan is the **integration contract** Katherine uses to validate end-to-end behavior and UI surfaces (**AST-307** tabbed editor consumes `resume_content`).

**Blocks:** **AST-301** (cover letter). **Blocked by:** **AST-296**, **AST-302**, **AST-303**, **AST-304**, **AST-371** (and **AST-370** for chain). **Related:** **AST-313**, **AST-308**.

---

## Files Changed (planned) — integration touchpoints

| File | Change | Layer |
|------|--------|-------|
| `docs/features/artifacts/ast-300-build-resume-artifact.md` | This plan (updated as children land). | docs |
| `src/utils/config.py` | `BUILD_CONFIG.artifact_shapes.resume_content` keys; `TASK_CONFIG` / `CONSULT_CONFIG` entries for each chain step (names per **AST-313** authoring). | utils |
| `src/core/agent.py` | Daisy-chain steps per **AST-303**; cache promotion per ticket spec. | core |
| `src/core/dispatcher.py` | Dispatch row for RECOMMENDED → resume pipeline batch (pattern with **AST-371**). | core |
| `src/core/tracker.py` | Read/write `job_data.artifacts.resume_content`; transition guardrails with **AST-302** states. | core |
| `src/data/database.py` | Only if **AST-371** requires schema for `job_data` blob shape — follow child plan, not duplicate here. | data |
| `ui/frontend` (Job Analysis path) | Read-only display + edit save path for draft vs final per **AST-307** plan. | ui |

Exact modules per **AST-370** / **AST-371** child plans — if a path is owned solely by a child, **do not** edit it from this branch without coordinating; this parent ticket may close after children merge and Katherine runs acceptance.

---

## Stage 1: Config and shapes (post–AST-296)

**Done when:** `artifact_shapes.resume_content` exists and matches JSON schema agreed with builder; task keys registered.

1. After **AST-296** on `dev`, add **`BUILD_CONFIG.artifact_shapes["resume_content"]`** structure per product spec (fields, required keys — no contact fields; builder injects profile contact per ticket).
2. Register pipeline **`TASK_CONFIG`** tasks (Susan-authored prompts in **AST-313**); each step lists `response_schema` / `vectors` as needed.

⚠️ **Decision:** Chain task keys and order are **single ordered list** in config (e.g. `RESUME_PIPELINE_STEPS` constant next to shapes) so dispatcher and `do_task` loop share one source of truth.

---

## Stage 2: do_task daisy-chain (post–AST-303/304)

**Done when:** One batch run walks all steps; each step reads prior step output from agent_data / structured parse; promotion replaces cache slot after designated step index.

1. Implement chain driver in **`agent.py`** (or module called from it) following **AST-303** pattern with **AST-304** tokens for cross-step references.
2. Implement **cache promotion** at the index specified in config after “base resume draft” step completes successfully.
3. On any step failure, land job in **`error_state`** from `CONSULT_CONFIG` / `TASK_CONFIG` for that step — no partial `resume_content` publish unless spec says otherwise.

---

## Stage 3: Persistence + trigger (AST-371)

**Done when:** Job in `RECOMMENDED` is claimed by resume pipeline dispatch; `resume_content` JSON written atomically with `batch_id`.

1. Merge **AST-371** implementation first when ready; this stage is **verification only** on parent branch: run one integration test path in dev/staging.
2. Confirm **`job_data.artifacts.resume_content`** matches shape; confirm idempotency if dispatch retries.

---

## Stage 4: Child AST-370 merge + token QA

**Done when:** `do_task` chain matches **AST-370** acceptance checklist (link in Linear).

1. Rebase/merge **AST-370** branch; resolve conflicts in `agent.py` / token resolver only with Ada’s intent preserved.
2. Run targeted **`py_compile`** and one dry-run batch in dev environment if available.

---

## Stage 5: UI handoff (AST-307)

**Done when:** Job Analysis Report shows resume draft tab populated from `job_data.artifacts.resume_content`; candidate edits round-trip per **AST-307** plan.

1. Coordinate field names with **AST-307** plan doc — no duplicate JSON paths.
2. Katherine validates UI + save flows after backend merged.

---

## Stage 6: Verify

**Done when:** End-to-end: job hits `RECOMMENDED` → pipeline runs → draft appears in report → candidate edit → final state written per **AST-302**.

1. `python3 -m py_compile` on all changed `.py`.
2. Manual or scripted integration checklist in Linear comment.

---

## Execution contract (for the developer agent)

Execute in order; if **AST-303**/`304`/`371`/`370` not on `dev`, **stop at the stage boundary** and comment on **AST-300** with blocking issue id — do not half-merge.

---

## Self-Assessment

**Scope — `MAJOR-CHANGE`**  
Config, core agent/dispatcher/tracker, database possibly, and UI integration across multiple tickets.

**Conf — `LOW`**  
Many upstream tickets must land first; sequencing and merge conflict risk are the main unknowns until dependencies are green.

**Risk — `HIGH`**  
Bad pipeline logic corrupts `job_data` or fires wrong dispatch waves; high blast radius on hiring data.

---

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|-------|
| §2.1 | All literals in `config.py`; no env fallbacks for non-secrets. |
| §2.4 | Dispatch uses `batch_id` pattern from **AST-371** / dispatcher norms. |
| §3.3 | Core → data/external only through allowed imports. |

**Conflicts:** None once dependency tickets’ plans agree on `job_data` path names.
