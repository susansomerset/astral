<!-- linear-archive: AST-299 archived 2026-06-03 -->

## Linear archive (AST-299)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-299/writing-preferences-candidate-profile-field  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** susan  
**Priority / estimate:** Medium / 2  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-313

### Description

Add freeform writing_preferences textarea to the candidate profile UI. Stored in candidate_data.context. Injected into artifact generation task prompts via the {$WRITING_PREFERENCES} parsable token. Susan controls which task prompts consume the token. Examples: 'NO EM DASHES', 'never use the word wheelhouse'.

### Comments

#### chuckles — 2026-05-18T19:09:21.782Z
## Landed on origin/dev — Chuckles

- Merged `origin/ftr/AST-299-writing-preferences-candidate-profile-field` → local `dev` → pushed `origin/dev` (product commits were already on `origin/dev`; branch added resolution doc)
- Deleted `origin/ftr/AST-299-writing-preferences-candidate-profile-field`
- Standalone ticket — no children

Push tip: `a867ea5d`

— Chuckles

#### katherine — 2026-05-16T22:49:00.371Z
Moved to **User Testing** (assignee @Susan Somerset). Merge `origin/ftr/AST-299` into local `dev` when ready. Branch tip: `a04c3d83`. — Katherine

#### katherine — 2026-05-16T22:39:09.984Z
Review feedback resolved (branch-law correction). Branch `ftr/AST-299` ready for UAT merge. Commit: `a04c3d83` — Katherine

- Radia: 0 fix-now; resolution doc on `origin/ftr/AST-299`.
- Status unchanged (**Review Posted**); prep-uat when siblings ready.

#### katherine — 2026-05-16T21:33:17.578Z
Review feedback resolved. Branch `katherine/ast-299-writing-preferences-candidate-profile-field` ready for UAT merge. Commit: `49101178` — Katherine

- Radia: 0 fix-now; resolution doc on branch.
- Status unchanged (**Review Posted**) per resolve-astral; prep-uat when siblings ready.

#### radia — 2026-05-16T21:16:14.223Z
## Radia review — AST-299

**Git:** Direct-to-dev — no `origin/chuckles/ast-299-…` ref in local clone; reviewed **`df9c922b`** (feat) + **`671870e7`** (test, shared with AST-365) on `origin/dev`.

| Bucket | Count |
|--------|------:|
| fix-now | 0 |
| discuss | 0 |
| advisory | 1 |

**Solid:** `CandidateWritingPreferences` reuses `ContextTextPage` / `context.writing_preferences`; `NAV_CONFIG` + route wired; `TOKEN_SOURCES.WRITING_PREFERENCES` → `context.writing_preferences`; component test asserts resolver. Plan scope (UI + token, no TASK_CONFIG edits) matches diff.

**Advisory:** 200×80 / validation N/A here; keep prompt authoring out of this ticket per plan.

— Radia

#### katherine — 2026-05-16T20:25:33.972Z
Katherine (test-astral) — manifest green on `dev-kath` @ `origin/dev` (no product fixes; feature branch absent on origin).

**Commands:**
1. `/Users/susan/chuckles/astral/.venv/bin/python -m pytest tests/component/utils/test_config.py::TestResolveTokens::test_resolves_writing_preferences_from_context` — pass
2. `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/components/test_ContextTextPage.test.tsx` — 8 passed

**Branch:** implementation on `origin/dev`; `katherine/ast-299-…` not on origin (retroactive merge).

#### betty — 2026-05-16T16:02:38.212Z
QA manifest by Betty.

**Integration:** `origin/dev` + test commits on `origin/dev-betty`.

**Manifest:**
1. `tests/component/utils/test_config.py::TestResolveTokens::test_resolves_writing_preferences_from_context`
2. `tests/component/frontend/components/test_ContextTextPage.test.tsx` (Writing Preferences page uses `ContextTextPage`)

**Commits (dev-betty):** `671870e7` — WRITING_PREFERENCES token (shared commit with AST-365)

— Betty

#### chuckles — 2026-05-16T15:44:41.484Z
## [retroactive-pipeline] — Chuckles

Implementation is **already on `origin/dev`** from the emergency integration merge. **Do not re-implement.**

Next step: **`astral-qa-plan`** (Betty) from **Code Complete** — manifest + test bible only, then hand off to the implementing engineer for **`astral-test`**.

Susan board cleanup 2026-05-16.

— Chuckles

#### chuckles — 2026-05-14T02:36:25.677Z
Built by Chuckles.

- **Branch:** `chuckles/ast-299-writing-preferences-candidate-profile-field`
- **Commits:** `df9c922b` (Writing Preferences page + nav), `b20fe381` (plan doc stub)

Note: no prior `origin/chuckles/ast-299-…` plan branch — feature branch created from `origin/dev` on first push.

Radia: **c-review-linear** when ready.

#### chuckles — 2026-05-14T02:36:01.624Z
Label review: agree on all three — **scope-Single-Component**, **conf-high**, **risk-Medium** match the plan self-assessment (reuse `ContextTextPage` + existing `TOKEN_SOURCES` / `resolve_tokens` path).

— Chuckles (b-build-linear)

#### susan — 2026-05-04T21:37:21.981Z
**Plan doc:** `docs/features/artifacts/ast-299-writing-preferences-candidate-profile-field.md`

**Self-assessment:**
- **Scope — Single-Component:** Profile textarea + `resolve_tokens` branch for `{$WRITING_PREFERENCES}`.
- **Conf — high:** Straightforward reuse of existing candidate save + token patterns.
- **Risk — Medium:** Resolver must be empty-safe; prompt wiring stays Susan-owned (AST-313).

GitHub: https://github.com/susansomerset/astral/blob/chuckles/ast-299-writing-preferences-candidate-profile-field/docs/features/artifacts/ast-299-writing-preferences-candidate-profile-field.md

— Katherine (a-plan-linear)

---

# Writing Preferences — Candidate Profile Field

**Linear:** https://linear.app/astralcareermatch/issue/AST-299/writing-preferences-candidate-profile-field  
**Feature branch:** `chuckles/ast-299-writing-preferences-candidate-profile-field`

Add **`writing_preferences`** freeform textarea on candidate profile UI; persist to **`candidate_data.context.writing_preferences`** (or exact path Susan locks in **AST-302** data model). Token **`{$WRITING_PREFERENCES}`** resolved in **`resolve_tokens()`** when **AST-304** plumbing already supports new token names — add resolver branch consistent with existing `{$...}` pattern. Susan selects which **TASK_CONFIG** prompts include the token (out of scope here — only ensure token resolves when present).

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/frontend/src/pages/` (candidate profile module) | Textarea + label; wire to candidate save API same as other profile fields. | ui |
| `src/core/` (token resolution) | Map `{$WRITING_PREFERENCES}` → string from candidate context; empty string if unset. | core |
| `src/utils/config.py` | If token list is enumerated in config, add key — else follow existing `resolve_tokens` registration pattern. | utils |
| `src/ui/frontend/src/App.css` | Profile field spacing. | ui |

Locate exact profile page file via `grep writing_preferences` / profile routes before implementing.

---

## Stage 1: Data path

**Done when:** Save/load round-trips `writing_preferences` with existing `PUT /api/candidates/:id/data` (or dedicated endpoint if project uses one — follow existing profile field pattern literally).

---

## Stage 2: Token resolver

**Done when:** Unit or smoke path: `resolve_tokens(..., candidate=...)` replaces token with stored text; escapes/length limits per **AST-304** rules if any.

---

## Stage 3: Verify

**Done when:** `py_compile` on changed `.py`; `tsc` clean.

---

## Execution contract

Do not modify **TASK_CONFIG** prompt bodies unless this ticket explicitly includes Susan’s prompt edits (default: **no**).

---

## Self-Assessment

**Scope — `Single-Component`**  
Profile UI + small core token addition.

**Conf — `high`**  
Pattern matches other `candidate_data.context` fields + parsable tokens.

**Risk — `Medium`**  
Token leakage into wrong prompts is config authoring risk; resolver must not throw on missing field.

---

## Self-review vs ASTRAL_CODE_RULES

§2.1; §3.3 core vs ui boundaries. **Conflicts:** none.

---

## Review stub (build)

Built by Chuckles.

- **Branch:** `chuckles/ast-299-writing-preferences-candidate-profile-field`
- **Implementation commit:** `df9c922b`

---

## Radia review (2026-05-16)

| Bucket | Items |
|--------|-------|
| fix-now | 0 |
| discuss | 0 |
| advisory | 1 — prompt authoring / 200×80 N/A; out of scope per plan |

---

## Resolution (2026-05-16, Katherine)

No product changes required. Radia review: **0 fix-now**. Betty manifest green on `origin/dev` (pytest + vitest). Implementation lives on `origin/dev` (`df9c922b`, `671870e7`). Ready for `prep-uat` merge when sibling children are at **Review Posted**.
