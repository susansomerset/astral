# AST-686 — UAT: Proposed importance explainer text for manual paste

**Linear:** [AST-686 — UAT: Proposed importance explainer text for manual paste](https://linear.app/astralcareermatch/issue/AST-686/uat-proposed-importance-explainer-text-for-manual-paste-update)  
**Parent:** [AST-655](https://linear.app/astralcareermatch/issue/AST-655/update-criteria-prompts-to-specify-the-importance-and-explain-what) (AC reference only)  
**Publish ref:** `origin/sub/AST-655/AST-686-uat-proposed-importance-explainer-text-for-manual-paste`  
**Project:** Team Astral

## Summary

Susan UAT on **AST-655**: **AST-678** shipped the shared importance explainer as a **`database.py` auto-migration** instead of a **copy/paste-ready artifact**. **AST-685** reverted that migration. This UAT bug delivers the **proposed explainer prose** as a **standalone text file outside `src/`** plus the **same text in the Linear ticket description** for Susan approval. Susan will **manually paste** the approved block into **Manage Tasks** `user_prompt` for all six **`craft_*_rubric`** tasks — **no** product code, migrations, or `agent_task` mutation.

**Source prose:** [AST-678 plan](ast-678-craft-rubric-importance-explainer-prompts.md) Stage 1 (authoritative draft); multiplier literals verified against `ASTRAL_CONFIG["consult_importance"]["multipliers"]` in `src/utils/config.py` (read-only reference — **do not edit config**).

**Builds on:** [AST-685 plan](ast-685-uat-revert-ast-678-agent-task-auto-migration.md) — auto-migration removed; this ticket is the **additive** manual-delivery path only.

---

## Files Changed (planned)

| File | Change | Layer | Owner |
|------|--------|-------|-------|
| `docs/consult/craft-rubric-importance-explainer-proposed.txt` | **New** — standalone proposed explainer (copy/paste source) | docs | Engineer |
| Linear **AST-686** description | Append **`## PROPOSED importance explainer`** with link to file + identical body | Linear | Engineer (build) |

**Out of scope:** `src/**` (including `database.py`), `tests/**`, `docs/test-bible/**`, `TASK_CONFIG` / response_schema (**AST-676**), UI task key (**AST-677**), production `push_tables_to_prod.py`, automatic prompt patching.

---

## Stage 1: Standalone explainer file + Linear PROPOSED section

**Done when:** `docs/consult/craft-rubric-importance-explainer-proposed.txt` exists with the exact prose below; `rg '678|ast678|_apply_ast678' docs/consult/` — no matches; `git diff` shows **no** paths under `src/`; Linear **AST-686** description contains **`## PROPOSED importance explainer`** whose body is **byte-identical** to the file (excluding the file’s optional trailing newline).

1. Create directory `docs/consult/` if missing.

2. Create **`docs/consult/craft-rubric-importance-explainer-proposed.txt`** with **exactly** this content (shared across all six rubric craft tasks — do not vary by stage):

   ```text
   ## Vector importance (1–10)

   Each criterion you return is a scoring **vector**. Assign every vector an integer **`importance`** from **1** (lowest priority) to **10** (highest priority). You **must** return `importance` on **every** criterion in your JSON — do not omit it or leave priority implicit.

   Spread importance meaningfully when vectors differ in how much they should move the consult score. Avoid assigning **5** to every vector when priorities clearly differ.

   ### Weight multipliers (importance → score contribution)

   Importance scales each vector's contribution to the overall consult score:

   - 1 → 30% of baseline
   - 2 → 49%
   - 3 → 68%
   - 4 → 87%
   - 5 → 106% (baseline)
   - 6 → 125%
   - 7 → 144%
   - 8 → 163%
   - 9 → 182%
   - 10 → 200%

   These match the runtime table in `ASTRAL_CONFIG["consult_importance"]` (AST-358 / AST-429).

   ### How importance combines with grades and confidence at scoring time

   At runtime each vector receives a letter grade (**A–D**, plus **F** and **X**) and a **confidence** integer **1–5**. Consult scoring combines all three:

   - **Counted vectors** contribute: `(equal base share among counted vectors) × (grade density) × (importance multiplier) × (confidence multiplier)`.
   - **Grade density** uses universal letter values (A highest, D lowest) times the confidence multiplier (1 → 0%, 2 → 25%, 3 → 50%, 4 → 75%, 5 → 100% of grade value).
   - **F** with confidence **2–5** is a **dealbreaker** — the rubric fails immediately regardless of other vectors.
   - **X** (cannot evaluate) and **confidence 1** vectors are **excluded** from the scored numerator (they do not add points; remaining vectors share the base).
   - The summed contribution is normalized to a **0–10** consult score and compared to the stage pass threshold.

   Return `importance` as an integer field **1–10** alongside `label` and `content` on each criterion object.
   ```

   ⚠️ **Decision:** **Omit** the `<!-- AST-678_VECTOR_IMPORTANCE -->` HTML comment that AST-678 used for migration idempotency — Susan’s paste artifact is clean prompt prose, not a DB marker.

3. At top of the `.txt` file (before `## Vector importance`), add a **3-line paste guide** comment block using `#` prefix lines (Susan strips or keeps as she prefers):

   ```text
   # AST-655 / AST-686 — proposed shared importance explainer (manual paste)
   # Paste into Manage Tasks → user_prompt for each craft_*_rubric task, immediately BEFORE {$RESPONSE_SCHEMA}
   # Tasks: craft_prefilter_rubric, craft_joblist_rubric, craft_jobdesc_rubric, craft_get_rubric, craft_do_rubric, craft_like_rubric
   ```

4. **`git add docs/consult/craft-rubric-importance-explainer-proposed.txt` only**; **`git commit -m "code(AST-686): add proposed craft rubric importance explainer for manual paste"`** on epic worktree; publish to **`origin/sub/AST-655/AST-686-uat-proposed-importance-explainer-text-for-manual-paste`**.

5. Via Linear MCP **`save_issue`** on **AST-686**, **append** to the existing description (preserve **What failed / Expected / Repro / Boundaries**):

   ```markdown
   ## PROPOSED importance explainer

   **Copy/paste source:** [`docs/consult/craft-rubric-importance-explainer-proposed.txt`](https://github.com/susansomerset/astral/blob/sub/AST-655/AST-686-uat-proposed-importance-explainer-text-for-manual-paste/docs/consult/craft-rubric-importance-explainer-proposed.txt)

   Paste into **Manage Tasks** → **`user_prompt`** for all six **`craft_*_rubric`** tasks, immediately **before** `{$RESPONSE_SCHEMA}`. Identical text on every task.

   <paste the file body here — same bytes as the .txt file, excluding the three `#` guide lines at the top>
   ```

   Replace `<paste the file body here…>` with the **exact** explainer prose from step 2 (not the `#` guide lines).

   ⚠️ **Decision:** Description carries inline prose **and** links the repo file — satisfies ticket AC #2 (“updated or linked with the **same PROPOSED text**”).

---

## QA manifest (Betty — after Stage 1 `code()` lands on publish ref)

**Done when:** File exists; no `src/` diff on publish ref for this ticket; Linear description contains PROPOSED block.

1. Assert **`docs/consult/craft-rubric-importance-explainer-proposed.txt`** exists on publish ref and multiplier lines match `ASTRAL_CONFIG["consult_importance"]["multipliers"]` (30%…200% table).

2. **`rg -n '678|ast678|_apply_ast678|database\.py' docs/consult/`** — no matches.

3. **`git diff origin/ftr/AST-655-update-criteria-prompts-to-specify-the-importance-and-explain-what..origin/sub/AST-655/AST-686-uat-proposed-importance-explainer-text-for-manual-paste -- src/`** — empty (no product changes on this sub).

4. Optional smoke: open Linear **AST-686** — **`## PROPOSED importance explainer`** present; body matches file (excluding `#` guide lines).

**Engineer test-child (happy path):** items 2–3 only (no pytest collection required unless Betty adds one).

---

## Execution contract

- Execute **Stage 1** in order; one `code(AST-686)` commit (`.txt` only) + Linear description update; publish to **`origin/sub/AST-655/AST-686-uat-proposed-importance-explainer-text-for-manual-paste`**.
- **Do not** touch `src/`, `tests/`, or `docs/test-bible/**`.
- Blocking ambiguity → `🛑` comment on **AST-686** per plan-child execution contract.

---

## Self-Assessment

**Scope:** `minor` — One new file under `docs/consult/` plus Linear description append; no product layers.

**Conf:** `high` — Prose is already specified in AST-678 plan and multiplier table matches live config; delivery mechanism only.

**Risk:** `low` — Docs + Linear text only; worst case Susan rejects prose wording before paste — no runtime regression path.

---

## ASTRAL_CODE_RULES self-review

| Rule | Assessment |
|------|------------|
| §2.1 config | No config edits; file **references** `ASTRAL_CONFIG["consult_importance"]` in prose only. |
| §3.6 local docs | Explainer lives under **`docs/consult/`** — not `src/`, not gitignored `debug/`. |
| §1.3 DRY | Single `.txt` source; Linear description duplicates for approval UX (ticket AC), not a second authoring surface. |

No conflicts flagged.

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-655/AST-686-uat-proposed-importance-explainer-text-for-manual-paste`  
**Product commit:** `ab6c83e9` — Stage 1: `docs/consult/craft-rubric-importance-explainer-proposed.txt` (paste guide + shared explainer prose); Linear **AST-686** description appended with **`## PROPOSED importance explainer`**.

**Local verification:** `rg '678|ast678|_apply_ast678|database\.py' docs/consult/` — no matches; no `src/` paths in commit.

**Susan path:** Review PROPOSED block on Linear or open the `.txt` file; after approval, paste into Manage Tasks `user_prompt` for all six `craft_*_rubric` tasks before `{$RESPONSE_SCHEMA}` — manual only, no deploy script in this ticket.

---

## Radia review (AST-686)

**Ref:** `origin/sub/AST-655/AST-686-uat-proposed-importance-explainer-text-for-manual-paste` @ `317d1141`  
**Baseline:** `origin/dev`

### What's solid

| Area | Notes |
|------|-------|
| **Stage 1 / plan** | `ab6c83e9` adds **only** `docs/consult/craft-rubric-importance-explainer-proposed.txt` — 3-line `#` paste guide + shared explainer prose; no `AST-678_VECTOR_IMPORTANCE` marker. |
| **Ticket AC #2** | Linear **AST-686** description has **`## PROPOSED importance explainer`**, GitHub link to file, and inline prose matching file body (excluding `#` guide lines). |
| **Multiplier fidelity** | Weight table (30%…200%) matches `ASTRAL_CONFIG["consult_importance"]["multipliers"]` in `config.py` (0.30…2.00). |
| **Boundaries** | No `src/` in `code(AST-686)`; `rg '678|ast678|_apply_ast678|database.py' docs/consult/` — no matches. |
| **Betty manifest** | `bec76850` registers docs-only audit manifest in test-bible README — no pytest required per plan. |

### Issues

None **fix-now**.

### Advisory

- Publish ref includes merged sibling work (**AST-685** revert, **AST-687**/**AST-688** tests) from epic rollup — not AST-686 deliverables; no conflict with docs-only scope.

### Recommended actions

| Severity | Action |
|----------|--------|
| — | Ada: none — proceed **resolve-child** if no open **discuss** threads. |
| — | Susan: review PROPOSED prose on Linear or in `.txt`; after approval, manual paste into all six `craft_*_rubric` Manage Tasks prompts. |
