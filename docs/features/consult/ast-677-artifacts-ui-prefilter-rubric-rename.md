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
