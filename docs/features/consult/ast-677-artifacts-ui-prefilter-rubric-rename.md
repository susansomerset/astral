<!-- linear-archive: AST-677 archived 2026-06-23 -->

## Linear archive (AST-677)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-677/artifacts-ui-prefilter-rubric-task-rename-update-criteria-prompts-to  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-655 — update criteria prompts to specify the importance and explain what that means  
**Blocked by / blocks / related:** parent: AST-655

### Description

## What this implements

Update Artifacts UI and any frontend/API client references so **Company Watch Criteria** invokes **craft_prefilter_rubric** instead of **craft_company_prefilter**, consistent with the backend rename in **AST-656**.

## Acceptance criteria

1. **Generate** on Company Watch Criteria invokes the renamed task successfully.

## Boundaries

* Does **not** change TASK_CONFIG or backend rename (blocked by **AST-656**).
* Does **not** update admin prompt bodies (**AST-658**).

## Notes for planning

* Primary surface: Company Watch Criteria Artifacts page taskKey.
* Grep for `craft_company_prefilter` under frontend and UI-adjacent paths.

## Git branch (authoritative)

Child `sub/AST-655/AST-657-artifacts-ui-prefilter-rubric-rename`. Blocked by **AST-656** for merge/integration order.

### Comments

#### radia — 2026-06-15T19:02:30.287Z
**Review** — `origin/dev...origin/sub/AST-655/AST-677-artifacts-ui-prefilter-rubric-rename` @ **`27f2a582`**

Plan: [`docs/features/consult/ast-677-artifacts-ui-prefilter-rubric-rename.md`](https://github.com/susansomerset/astral/blob/sub/AST-655/AST-677-artifacts-ui-prefilter-rubric-rename/docs/features/consult/ast-677-artifacts-ui-prefilter-rubric-rename.md) (Review section appended)

### fix-now

None.

### discuss

None.

### advisory

| Location | Finding |
|----------|---------|
| Branch diff vs `origin/dev` | Includes sibling epic commits (**AST-676** config/validator, **AST-674** roster tests, **AST-679** deploy footer) from ftr integration. AST-677 product footprint remains one TSX `taskKey` line + Betty page test — not scope creep on this ticket. |
| `ArtifactsCompanyWatchCriteria` Generate | May still fail schema validation until **AST-678** prompts emit `importance` — expected per plan Self-Assessment Risk; rename is correct regardless. |
| Linear description | Git branch line says `AST-657`; publish ref is `sub/AST-655/AST-677-artifacts-ui-prefilter-rubric-rename`. |

### What's solid

- **`ArtifactsCompanyWatchCriteria.tsx`:** `taskKey="craft_prefilter_rubric"`; `artifactKey="company_prefilter"` unchanged — matches Stage 1.
- **`grep craft_company_prefilter src/ui/frontend/`** — zero matches.
- **§3.3 / §3.2:** UI-only; no new cross-layer imports.
- **§2.1:** Literal task key matches backend `TASK_CONFIG` (**AST-676**); same pattern as other Artifacts pages.
- **Test:** `AST-677: Generate POSTs craft_prefilter_rubric` covers AC1 (POST path via Regenerate).

**Recommended:** Proceed to **resolve-child** (no product changes required).

#### betty — 2026-06-15T18:54:57.525Z
## QA test manifest — AST-677

**Publish ref:** `origin/sub/AST-655/AST-677-artifacts-ui-prefilter-rubric-rename` @ `6941bc19` (`merge-tests(AST-677): origin/tests 008b297c`)

### 1. Existing coverage (bible-backed)

| # | Test | Why |
| --- | --- | --- |
| 1 | `tests/component/utils/test_config.py::TestAst676CraftRubricSchema` | Backend **`craft_prefilter_rubric`** key + shared rubric schema (**AST-676** regression) |
| 2 | `tests/component/core/test_agent.py::TestResponseSchemaBranches::test_ast676_int_bounds_and_bool_rejection` | **`importance`** validation at **`do_task`** (**AST-676** regression) |
| 3 | `tests/component/core/test_agent.py::TestResponseSchemaBranches::test_ast676_craft_rubric_criteria_schema` | Shared rubric criteria schema (**AST-676** regression) |

### 2. Broken / obsolete tests

None — page had only a render smoke test; no assertions referenced **`craft_company_prefilter`**.

### 3. Gaps (new this pass)

| # | Test | AC |
| --- | --- | --- |
| 4 | `tests/component/frontend/pages/test_ArtifactsCompanyWatchCriteria.test.tsx` — **`renders company watch criteria editor`** | §6c routed page + first-paint mocks |
| 5 | Same file — **`AST-677: Generate POSTs craft_prefilter_rubric`** | AC1 — **Generate** POST **`/api/candidates/{id}/generate/craft_prefilter_rubric`** |

### Narrowed run

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_ArtifactsCompanyWatchCriteria.test.tsx
```

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst676CraftRubricSchema \
  tests/component/core/test_agent.py::TestResponseSchemaBranches::test_ast676_int_bounds_and_bool_rejection \
  tests/component/core/test_agent.py::TestResponseSchemaBranches::test_ast676_craft_rubric_criteria_schema
```

### Bible

- `docs/test-bible/frontend/pages.md` — **`### AST-677 · AST-655`** block
- shasum @ publish ref: `00b2f8fd1f6e5ed96082365d2f30162dbc98d03efd52f5ae614b822ac1883190`

#### ada — 2026-06-15T18:31:08.486Z
Plan: [`docs/features/consult/ast-677-artifacts-ui-prefilter-rubric-rename.md`](https://github.com/susansomerset/astral/blob/sub/AST-655/AST-677-artifacts-ui-prefilter-rubric-rename/docs/features/consult/ast-677-artifacts-ui-prefilter-rubric-rename.md) on `origin/sub/AST-655/AST-677-artifacts-ui-prefilter-rubric-rename` @ `3748e9b9`.

**Scope:** `minor` — one `taskKey` prop in `ArtifactsCompanyWatchCriteria.tsx`; no backend or `ArtifactEditor` changes.

**Conf:** `high` — AST-676 already renamed the backend task; grep shows only this UI file still uses the old key.

**Risk:** `low` — isolated Generate path on one Artifacts page; prompt `importance` failures until AST-678 are expected epic sequencing, not this rename.

---

# AST-677 — Artifacts UI prefilter rubric task rename

**Linear:** [AST-677](https://linear.app/astralcareermatch/issue/AST-677/artifacts-ui-prefilter-rubric-task-rename-update-criteria-prompts-to)  
**Parent:** [AST-655](https://linear.app/astralcareermatch/issue/AST-655/update-criteria-prompts-to-specify-the-importance-and-explain-what)  
**Publish ref:** `origin/sub/AST-655/AST-677-artifacts-ui-prefilter-rubric-rename`  
**Project:** Team Astral

## Summary

Update the Company Watch Criteria Artifacts page so **Generate** calls **`craft_prefilter_rubric`** instead of the removed **`craft_company_prefilter`** task key. Backend rename and schema validation landed in **AST-676**; stored artifact key **`company_prefilter`** is unchanged. This ticket is UI-only — one `taskKey` prop update plus a grep verification step.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/ArtifactsCompanyWatchCriteria.tsx` | Change `taskKey` prop from `craft_company_prefilter` to `craft_prefilter_rubric` | ui |

**Out of scope (sibling tickets):** `src/utils/config.py` / `TASK_CONFIG` (**AST-676**), admin prompt DB bodies (**AST-678**), `ArtifactEditor.tsx` (generic — no change needed), historical docs under `docs/features/**` that mention the old task key.

## Stage 1: Company Watch Criteria taskKey rename

**Done when:** `grep craft_company_prefilter src/ui/frontend/` returns zero matches; Company Watch Criteria **Generate** POSTs to `/api/candidates/{id}/generate/craft_prefilter_rubric` (via `ArtifactEditor` `taskKey` prop); `artifactKey="company_prefilter"` is unchanged.

1. In `src/ui/frontend/src/pages/ArtifactsCompanyWatchCriteria.tsx`, change the `ArtifactEditor` `taskKey` prop from `"craft_company_prefilter"` to `"craft_prefilter_rubric"`. Keep `title="Company Watch Criteria"` and `artifactKey="company_prefilter"` exactly as today.

   Before:

   ```tsx
   return <ArtifactEditor title="Company Watch Criteria" artifactKey="company_prefilter" taskKey="craft_company_prefilter" />
   ```

   After:

   ```tsx
   return <ArtifactEditor title="Company Watch Criteria" artifactKey="company_prefilter" taskKey="craft_prefilter_rubric" />
   ```

2. Run `grep -r craft_company_prefilter src/ui/frontend/` from repo root. Expect **no output**. If any other frontend file still references the old key, stop and comment on **AST-677** — do not expand scope beyond what grep finds without a Linear comment.

3. Do **not** edit `src/ui/frontend/src/components/ArtifactEditor.tsx`. It already passes `taskKey` through to `POST /api/candidates/${selectedId}/generate/${taskKey}` (line ~378); no wrapper or alias layer is required.

⚠️ **Decision:** No new config entry or shared constant for this single page — matches existing Artifacts pages (each passes its `taskKey` string literal to `ArtifactEditor`). Centralizing task keys in frontend config is out of scope for this rename-only ticket.

## Self-Assessment

**Scope:** `minor` — One React page file; a single string prop change on an existing `ArtifactEditor` wrapper.

**Conf:** `high` — **AST-676** already renamed the backend task; grep confirms only this UI file still references the old key; change mirrors every other Artifacts page pattern.

**Risk:** `low` — Wrong `taskKey` breaks Generate on one page only; no dispatch, database, or shared core paths affected. Full rubric Generate may still fail until **AST-678** prompt bodies emit `importance` — that is expected epic sequencing, not a regression from this rename.

## Self-Review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §3.3 imports / layers | UI page only; no new imports or cross-layer calls. |
| §3.5 naming | No new files; existing PascalCase page name unchanged. |
| §2.1 config | Task key lives in backend `TASK_CONFIG` (**AST-676**); UI passes the canonical key string — no duplicate business logic in React. |
| §3 UI business logic | No visibility or state logic added; `ArtifactEditor` remains the render/generate shell. |
| §1.3 DRY | Reuses existing `ArtifactEditor`; no new abstractions. |

No conflicts — plan is safe to implement as written.

## Built

**Built:** `code(AST-677): point Company Watch Criteria Generate at craft_prefilter_rubric`  
**Branch:** `origin/sub/AST-655/AST-677-artifacts-ui-prefilter-rubric-rename` @ `93a0d8ec`

## Review

| Field | Value |
|-------|-------|
| Branch | `origin/sub/AST-655/AST-677-artifacts-ui-prefilter-rubric-rename` |
| Tip (reviewed) | `00398468` |
| Baseline | `origin/dev` (three-dot diff) |
| Status | Review Posted (Radia) |

### What's solid

- Plan Stage 1 lands exactly: `ArtifactsCompanyWatchCriteria.tsx` `taskKey` → `craft_prefilter_rubric`; `artifactKey="company_prefilter"` and title unchanged.
- `grep craft_company_prefilter src/ui/frontend/` is clean — no stale frontend references.
- §3.3 / §3.2 layer compliance: one-line UI wrapper only; no new imports, no `src/data` / `src/external` from frontend.
- §2.1 config: UI passes canonical backend key string; no duplicate task registry in React (matches other Artifacts pages).
- Betty manifest: `AST-677: Generate POSTs craft_prefilter_rubric` asserts POST `/api/candidates/{id}/generate/craft_prefilter_rubric` via `ArtifactEditor` Regenerate flow.

### Issues

| Severity | Location | Finding |
|----------|----------|---------|
| advisory | epic sequencing | Rubric **Generate** may still fail `_validate_response_schema` until **AST-678** prompt bodies emit `importance` — documented in Self-Assessment Risk; rename-only ticket does not fix that. |
| advisory | Linear AST-677 description | Git branch line cites `AST-657` slug; authoritative publish ref is `sub/AST-655/AST-677-artifacts-ui-prefilter-rubric-rename`. |

### Recommended actions

| Item | Owner | Action |
|------|-------|--------|
| — | — | **No fix-now items.** Proceed to **resolve-child**. |
| Prompt bodies | AST-678 | Ensure craft rubric prompts emit `importance` so Generate passes post-rename. |

## Resolution (`resolve-child`)

**Date:** 2026-06-15

**Against:** Radia `review-child` § **Review** on `origin/sub/AST-655/AST-677-artifacts-ui-prefilter-rubric-rename` @ **`27f2a582`**.

**Product / plan**

- **`fix-now`:** None — `ArtifactsCompanyWatchCriteria.tsx` `taskKey` → `craft_prefilter_rubric`, Betty page test, and Radia review doc are as-reviewed; no product commits in this resolve pass.
- **Discuss:** None.
- **Advisory — sibling epic commits on diff:** Accepted — ftr integration carries **AST-676** / **AST-674** / **AST-679** siblings; AST-677 delta remains one TSX line + page test.
- **Advisory — Generate until AST-678:** Accepted per Self-Assessment Risk — schema validation may fail until prompt bodies emit `importance`; rename is correct regardless.

**Integration:** §9a dry-runs vs **`origin/dev`** and **`origin/ftr/AST-655-update-criteria-prompts-to-specify-the-importance-and-explain-what`** — both clean before **User Testing**.
