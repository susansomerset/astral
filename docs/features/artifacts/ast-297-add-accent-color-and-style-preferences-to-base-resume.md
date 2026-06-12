<!-- linear-archive: AST-297 archived 2026-06-03 -->

## Linear archive (AST-297)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-297/add-accent-color-and-style-preferences-to-base-resume-artifact  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** susan  
**Priority / estimate:** Medium / 3  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Extend candidate_data.artifacts.base_resume to carry style preferences alongside resume content: accent_color (hex, chosen from a curated dark palette) and an optional default_style override map. Add accent color picker to the Base Resume modal page header (ArtifactsBaseResumeContent.tsx) — renders a row of dark palette swatches, stores selection to candidate_data.artifacts.base_resume.accent_color. BUILD_CONFIG.default_style defines the palette. [builder.py](<http://builder.py>) merges candidate accent_color over the config default at render time. No other style fields exposed to candidate for now.

### Comments

#### chuckles — 2026-05-18T19:09:20.725Z
## Landed on origin/dev — Chuckles

- Merged `origin/ftr/AST-297-add-accent-color-and-style-preferences` → local `dev` (already present from prep-uat) → pushed `origin/dev`
- Deleted `origin/ftr/AST-297-add-accent-color-and-style-preferences`
- Standalone ticket — no children

Push tip: `a867ea5d` (includes AST-299 finish-up merge in same push)

— Chuckles

#### chuckles — 2026-05-18T19:00:26.768Z
## UAT Ready — Chuckles

**AST-297** is a **standalone** ticket (no child branches). prep-uat = merge feature branch into local `dev` only.

**Parent/feature branch:** `origin/ftr/AST-297-add-accent-color-and-style-preferences` (4 commits ahead of prior `dev` tip)

**Merged into local `dev`:** prep-uat §8 — merge commit on `dev`. No `sub/*` branches to delete.

Restart the app if it is running, then test accent palette on Base Resume.

If testing fails on `dev`:
```
git reset --hard origin/dev
```

— Chuckles

#### katherine — 2026-05-16T23:06:49.685Z
Review feedback resolved. Branch `ftr/AST-297` ready for prep-uat. Commit: `d8118004` — Katherine

- Radia: 0 fix-now; **discuss** closed (palette via `ui_config`); **advisory** — `default_style` deferred.
- **User Testing** — merge `origin/ftr/AST-297` into local `dev` when exercising.

#### radia — 2026-05-16T22:42:49.770Z
## review-astral (Radia)

**Diff:** `origin/dev...origin/ftr/AST-297`

**Summary:** Accent palette + Base Resume swatches look good. **0 fix-now** · **1 discuss** · **1 advisory**

- **discuss:** Plan mentioned `/api/shapes` for palette; shipped via `ui_config` extension — OK if Susan confirms endpoint.
- **advisory:** `default_style` not in diff — confirm deferred.

**Doc commit:** `d8185297` on `origin/ftr/AST-297` — `docs/features/artifacts/ast-297-add-accent-color-and-style-preferences-to-base-resume.md`

— Radia

#### katherine — 2026-05-16T22:41:10.178Z
Tests passed by Katherine (test-astral).

**Integration:** `origin/ftr/AST-297` @ `8302ff58` (merged onto `dev-kath` for run).

**Commands (Betty manifest, in order):**
1. `python3 -m pytest tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_ui_config_includes_base_resume_accent_palette -q` → **1 passed**
2. `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx` → **2 passed**

**Product fixes:** none required.

**Published:** no new commits (feature tip unchanged @ `8302ff58`).

— Katherine

#### betty — 2026-05-16T21:54:49.693Z
**[qa-astral] branch correction** — canonical ref is **`origin/ftr/AST-297`** @ `8302ff58` (not `katherine/ast-297-…`). Prior comment’s legacy branch name is obsolete; use **`ftr/AST-297`** for **test-astral**.

— Betty

#### betty — 2026-05-16T21:42:32.629Z
QA manifest by Betty.

**Integration:** `origin/katherine/ast-297-add-accent-color-and-style-preferences-to-base-resume` + product on branch tip.

**Manifest (run in order):**
1. `tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_ui_config_includes_base_resume_accent_palette`
2. `tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx`

**Commits (dev-betty → feature branch):** `6aef66e2` — accent palette + swatch save RTL

— Betty

#### katherine — 2026-05-16T21:36:03.329Z
Label review: agree on all three (scope-Single-Component, conf-Medium, risk-low).

Built by Katherine.
- **Branch:** `katherine/ast-297-add-accent-color-and-style-preferences-to-base-resume`
- **Changes:** `BUILD_CONFIG.accent_palette`, `GET /api/system/ui_config` → `base_resume_accent_palette`, swatch row on Base Resume page, persist `artifacts.base_resume.accent_color` via existing candidate data PUT.
- **Verify:** `py_compile` + `tsc -b --noEmit` clean.

— Katherine (build-astral)

#### chuckles — 2026-05-16T21:29:50.967Z
## Plan Review — Chuckles

**Verdict: APPROVED**

Plan is faithful to the definition. No findings. ASTRAL_CODE_RULES compliance confirmed. Self-assessment is honest (conf-Medium, risk-low).

**Note:** Implementation already on `origin/dev` ([retroactive-pipeline] C2). Advance pipeline per cleanup checklist; use `build-astral` only if further product work remains.

— Chuckles

#### susan — 2026-05-04T21:37:19.555Z
**Plan doc:** `docs/features/artifacts/ast-297-add-accent-color-and-style-preferences-to-base-resume.md`

**Self-assessment:**
- **Scope — Single-Component:** `config.py` palette + `ArtifactsBaseResumeContent.tsx` + CSS (+ optional small API for server-driven palette).
- **Conf — Medium:** One explicit decision: single source for palette exposed to the client.
- **Risk — low:** Visual preference only; easy to revert.

GitHub: https://github.com/susansomerset/astral/blob/chuckles/ast-297-add-accent-color-and-style-preferences-to-base-resume/docs/features/artifacts/ast-297-add-accent-color-and-style-preferences-to-base-resume.md

— Katherine (a-plan-linear)

---

# Add Accent Color and Style Preferences to Base Resume Artifact

**Linear:** https://linear.app/astralcareermatch/issue/AST-297/add-accent-color-and-style-preferences-to-base-resume-artifact  
**Feature branch:** `<agent>/ast-297-add-accent-color-and-style-preferences-to-base-resume`

Extend **`candidate_data.artifacts.base_resume`** with **`accent_color`** (hex from curated dark palette) and optional **`default_style`** overrides. **`ArtifactsBaseResumeContent.tsx`** header: swatch row + persistence via existing candidate `PUT /api/candidates/:id/data` pattern. Palette literals live in **`src/utils/config.py`** (e.g. `BUILD_CONFIG.default_style` / nested palette block per ticket wording) — not inline hex arrays in TSX.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `BASE_RESUME_STYLE_CONFIG` or extend `BUILD_CONFIG` with `accent_palette: string[]` + optional default map. | utils |
| `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` | Swatch UI in `dep-header` beside title; load/save `accent_color` / `default_style` keys inside artifacts payload. | ui |
| `src/ui/frontend/src/App.css` | Swatch row, selected ring, focus styles. | ui |
| `src/ui/api/api_candidate.py` (or existing save path) | Only if validation needed server-side for hex format — otherwise rely on client + existing PUT. | ui |

---

## Stage 1: Config palette

**Done when:** Palette is a named constant list in `config.py`; TypeScript imports palette via new `GET /api/...` **or** duplicate read from shapes endpoint if one exists — **prefer single API** that exposes palette from config to avoid drift (add minimal endpoint if none exists: e.g. `/api/shapes` extension vs new `/api/style-palette` — pick one in ⚠️ Decision below).

⚠️ **Decision:** Expose palette through **`/api/shapes`** extension **or** static import from generated JSON — **do not** duplicate hex list in TS and Python; choose **server-driven** list returned once on page load.

---

## Stage 2: UI swatches + save

**Done when:** Selecting swatch updates local state, debounced/autosave consistent with **ArtifactEditor** pattern; reload restores selection.

1. Read current `ArtifactsBaseResumeContent` / parent wrapper — only touch base resume page.
2. Persist under `artifacts.base_resume.accent_color` as string `#RRGGBB` uppercase.
3. Optional `default_style` map: use JSON editor sub-region or compact key-value UI per product sketch in Linear — if ambiguous, **stop and comment**.

---

## Stage 3: Verify

**Done when:** `npx tsc -b --noEmit`; manual: pick swatch, refresh, value persists.

---

## Execution contract

No new DB tables; only `candidate_data` JSON paths already used by artifacts save.

---

## Self-Assessment

**Scope — `Single-Component`**  
Config block + one artifacts page + CSS (+ optional tiny API read).

**Conf — `Medium`**  
Palette source-of-truth placement needs one clear decision.

**Risk — `low`**  
Wrong color affects display only until reset; no dispatch impact.

---

## Self-review vs ASTRAL_CODE_RULES

§1.4 no magic colors in TSX — all palette in config. §3.5 CSS TOC. **Conflicts:** none.

---

## Radia review (review-astral 2026-05-16)

**Diff:** `origin/dev...origin/ftr/AST-297`

### What's solid

- `BUILD_CONFIG.accent_palette` is the single source of truth; exposed via `/api/ui_config` as `base_resume_accent_palette` (§1.4 / G1).
- `ArtifactsBaseResumeContent` validates hex, persists `artifacts.base_resume.accent_color` through existing candidate `PUT`, accessible swatch UI + component test + `test_api_system`.
- Scope matches **Single-Component** self-assessment (palette + one page + CSS).

### Issues

| Severity | Item |
|----------|------|
| **discuss** | Plan Stage 1 preferred `/api/shapes` for palette; implementation uses `ui_config` extension — acceptable server-driven list; confirm Susan is fine with the endpoint choice. |
| **advisory** | Optional `default_style` from the Linear ticket is **not** in this diff — defer to a follow-up or confirm out of scope. |

### Recommended actions

| Action | Owner |
|--------|-------|
| None blocking | — |
| Confirm `default_style` deferred or open child ticket | Susan / Katherine |

**Counts:** 0 fix-now · 1 discuss · 1 advisory

— Radia

---

## Resolution (2026-05-16, Katherine)

No product changes required. **Discuss:** palette ships via `GET /api/system/ui_config` → `base_resume_accent_palette` (server-driven from `BUILD_CONFIG.accent_palette`); acceptable vs plan’s `/api/shapes` option. **Advisory:** `default_style` deferred — out of scope for this ticket; open follow-up if Susan wants candidate-facing style overrides. Betty manifest green on `origin/ftr/AST-297` (`8302ff58`). Ready for **prep-uat** / Susan UAT on `ftr/AST-297`.
