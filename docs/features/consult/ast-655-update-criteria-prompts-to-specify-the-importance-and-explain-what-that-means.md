# AST-655 — update criteria prompts to specify the importance and explain what that means

<!-- linear-archive: AST-655 archived 2026-06-23 -->

## Linear archive (AST-655)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-655/update-criteria-prompts-to-specify-the-importance-and-explain-what  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-447

### Description

## Purpose

Consult scoring already uses per-vector **importance** (1–10) together with universal letter grades and confidence ([AST-359](https://linear.app/astralcareermatch/issue/AST-359), [AST-358](https://linear.app/astralcareermatch/issue/AST-358)/[AST-429](https://linear.app/astralcareermatch/issue/AST-429)). The Artifacts UI collects and displays importance, and save-path normalization defaults missing values to 5 — but the **craft rubric** AI tasks still only require `label` and `content` in their response schema, and their prompts do not teach the model what importance means or how it affects scores. Susan wants rubrics **authored by the model** to arrive with sensible, differentiated importance values instead of silent defaults, so consult scores reflect candidate priorities from first generation.

## Functional scope

* **Author one shared importance explainer** suitable for insertion into admin-managed craft-rubric prompts — **identical text** across all rubric craft tasks (the scoring math does not vary by stage). It must describe, in plain language:
  * That each criterion (vector) carries an integer **importance** from **1** (lowest weight) to **10** (highest weight).
  * The configured **weight mapping** from importance to scoring multiplier (currently 1→30% through 10→200% of baseline — the same table consult uses at runtime).
  * How importance combines at scoring time with **letter grades** (universal A–D values), **confidence** (1–5 density multiplier), and rubric pass/fail behavior (**F** halts the rubric; **X** excludes the vector from the score).
  * That the model must **assign** an importance per criterion it returns — not leave it implicit — and should spread values meaningfully across vectors (avoid assigning 5 to everything when priorities differ).
* **Rename** the company prefilter craft task from **craft_company_prefilter** to **craft_prefilter_rubric**, and update all references so generate paths, token wiring, and admin task rows use the new key consistently.
* **Update admin prompts** for all six rubric craft tasks — company prefilter (renamed), job list, job description, get, do, and like criteria — so each instructs the model to return `importance` on every criterion using the shared explainer above. Prompt bodies live in the agent-task store (Manage Tasks); local and deployed environments must both receive the updated text.
* **Extend task response validation** for all six craft rubric tasks so each item in the `criteria` list **requires** an integer `importance` in 1–10 (same bounds as rubric artifact normalization). A craft run that omits or invalidates importance fails validation like any other schema violation.
* **Preserve existing artifact behavior** on save and in the criteria editor: generated importance flows into the UI; manual edits and normalization rules already in place continue to apply after generation. The stored artifact key for company prefilter criteria remains unchanged; only the craft task key is renamed.

## Boundaries

* Does **not** change consult scoring math, grade validation, or pass thresholds — already landed.
* Does **not** change rubric UI layout, sorting, or importance picker behavior — already landed ([AST-359](https://linear.app/astralcareermatch/issue/AST-359)).
* Does **not** require bulk re-generation of existing candidate rubrics; only new and user-triggered **Generate** runs must satisfy the new contract.
* Does **not** address what happens when a user later changes importance on saved rubrics and historical job scores ([AST-447](https://linear.app/astralcareermatch/issue/AST-447), [AST-448](https://linear.app/astralcareermatch/issue/AST-448)) — separate discussion tickets.
* Does **not** add admin UI to edit the multiplier table; table remains config-driven per Code Rules §2.1.

## Acceptance criteria

1. **craft_company_prefilter** is renamed to **craft_prefilter_rubric** everywhere the craft task key is referenced; **Generate** on Company Watch Criteria invokes the renamed task successfully.
2. All six rubric craft tasks share the same importance explainer in prompt text and explicitly instruct the model to return `importance` per criterion.
3. Task response schema for all six requires `importance` (integer, 1–10) on every `criteria` item; missing or out-of-range values fail the craft task with a clear validation error.
4. **Generate** on any rubric criteria Artifacts page (including Company Watch) returns criteria rows that include model-chosen importance values visible in the editor before save.
5. After save, persisted artifact rows retain those importance values (not replaced solely by the default of 5 unless the model omitted them — which should no longer pass validation).
6. Regenerating one rubric does not alter other rubric artifacts or consult runtime grading for jobs already scored.

## Dependencies and blockers

* [AST-359](https://linear.app/astralcareermatch/issue/AST-359) — importance on rubric vectors (UI + normalization): **Done**.
* [AST-358](https://linear.app/astralcareermatch/issue/AST-358) / [AST-429](https://linear.app/astralcareermatch/issue/AST-429) — scoring consumes importance: **Done**.
* none.

## Open questions

none.

---

## Original brief

Please draft an explanation of the importance factors for vectors, including their weights and how the factor is used with the runtime grades and confidence scores.

Then update the config to expect that importance factor to be returned with craft_*_rubric tasks.

### Comments

#### chuckles — 2026-06-15T21:31:15.648Z
[fix-uat] UAT fixes landed — ready for re-test

| Bug | What changed |
| --- | --- |
| **AST-685** | Revert AST-678 agent_task auto-migration (update criteria prompts to specify the importance and explain what that means) |
| **AST-686** | Proposed importance explainer text for manual paste (update criteria prompts to specify the importance and explain what that means) |

### Quick re-test (this fix wave only)

Confirm we understood each issue — **not** a full epic regression pass.

**AST-685** — _Revert AST-678 agent_task auto-migration (update criteria prompts to specify the importance and explain what that means)_
- **Issue reported:** AST-678 landed an automatic `agent_task` migration in `database.py` that inserts the importance explainer into all six rubric craft prompts at schema init. Susan UAT: she wanted a **standalone text file** she could copy/paste via **Manage Tasks** — not product code that mutates p
- **Should now:** Remove AST-678 migration code, related tests, and bible entries from the epic branch. `agent_task` prompt bodies return to pre-678 behavior until Susan manually pastes approved text via the admin UI.
- **Quick check (this fix only):**
  1. Open Manage Tasks (or inspect local DB after app start).
  2. Observe craft rubric task prompts already contain `AST-678_VECTOR_IMPORTANCE` marker text without manual edit.
  3. Susan expected to paste explainer herself — not have migration inject it.

**AST-686** — _Proposed importance explainer text for manual paste (update criteria prompts to specify the importance and explain what that means)_
- **Issue reported:** Team shipped AST-678 as a DB migration instead of delivering **proposed explainer prose** Susan could review and paste into Manage Tasks herself.
- **Should now:** 1. A **standalone text file outside** `src/` (e.g. under `docs/` or project root) containing the shared importance explainer draft.
- **Quick check (this fix only):**
  1. Susan UAT on AST-655 — no copy/paste-ready explainer artifact exists.
  2. After this bug lands: open the text file, confirm identical explainer suitable for all six `craft_*_rubric` tasks.

Local `dev` merged via prep-uat. Staging should reflect the fixes above.

— Chuckles

#### chuckles — 2026-06-15T19:30:25.314Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-655 (parent) | ftr/AST-655-update-criteria-prompts-to-specify-the-importance-and-explain-what |
| AST-685 | sub/AST-655/AST-685-uat-revert-ast-678-agent-task-auto-migration |
| AST-686 | sub/AST-655/AST-686-uat-proposed-importance-explainer-text-for-manual-paste |

**Epic worktree:** `astral-AST-655/`

**Parent:** AST-655

**blockedBy:** AST-686 → AST-685

— Chuckles

#### susan — 2026-06-15T19:28:22.087Z
Oh dear, this is deeply wrong.  I wanted just a text file generated outside of the source code that I could copy and paste with the UI to explain the importance factor.

Please revert 678, then provide a subissue whose description includes the drafted content PROPOSED to be used, and if approved, I will manually update data in the database to include that explanatory text.

#### chuckles — 2026-06-15T18:09:35.787Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-655 (parent) | ftr/AST-655-update-criteria-prompts-to-specify-the-importance-and-explain-what |
| AST-676 | sub/AST-655/AST-676-rename-prefilter-rubric-and-importance-schema |
| AST-677 | sub/AST-655/AST-677-artifacts-ui-prefilter-rubric-rename |
| AST-678 | sub/AST-655/AST-678-craft-rubric-importance-explainer-prompts |

**Epic worktree:** `astral-AST-655/` — one active sub checked out at a time.

**Parent:** AST-655

**blockedBy:** AST-677, AST-678 → AST-676

— Chuckles

#### chuckles — 2026-06-15T17:44:15.894Z
@susan

1. Should **craft_company_prefilter** receive the same prompt explainer and required `importance` field, or stay label+content only?
2. Should the five rubrics share one **identical** importance explainer block in prompts, or should each rubric type include a short stage-specific sentence (e.g. job-list vs like-job priorities)?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
