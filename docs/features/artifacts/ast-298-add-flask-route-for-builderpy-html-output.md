<!-- linear-archive: AST-298 archived 2026-06-03 -->

## Linear archive (AST-298)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-298/add-flask-route-for-builderpy-html-output  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** susan  
**Priority / estimate:** Medium / 2  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-307

### Description

Add /candidate/resume/<job_id> and /candidate/resume/base routes to the Flask API (ui/api/). Each route calls builder.build_resume(job_id) or builder.build_base_resume(candidate_id), returns rendered HTML with Content-Type text/html. Frontend opens the route in a new browser tab (window.open). No React rendering involved — pure HTML response designed for browser print-to-PDF. Requires auth.

### Comments

#### hedy — 2026-05-16T23:07:42.425Z
Review feedback resolved. Product on `origin/dev` (`228ca38e`); plan Resolution on `dev-hedy` (`13076361`). Ready for **prep-uat** (retroactive — no `ftr/AST-298`). Parent **AST-294** — Hedy

#### hedy — 2026-05-16T22:49:56.651Z
Review feedback resolved (re-confirm). Product on `origin/dev`; plan Resolution appended on `dev-hedy` @ `13076361`. Radia **0 fix-now**. — Hedy

#### hedy — 2026-05-16T21:36:34.060Z
Review feedback resolved. Branch `hedy/ast-298-add-flask-route-for-builderpy-html-output` ready for UAT merge. Commit: cfa13d16 — Hedy

Radia fix-now: 0 (doc Resolution appended on `dev-hedy`).

#### radia — 2026-05-16T21:16:17.046Z
## Radia review — AST-298

**Git:** Direct-to-dev; reviewed **`228ca38e`** + **`9e2ad034`** on `origin/dev`.

| Bucket | Count |
|--------|------:|
| fix-now | 0 |
| discuss | 0 |
| advisory | 0 |

**Solid:** `api_resume_html.py` stays thin — `@require_auth`, delegates to `build_resume` / `build_base_resume`, HTML mimetype, 400/404 mapping. Blueprint registered in `server.py`. Component tests cover auth, missing `candidate_id`, happy path, ValueError→404.

**Layer:** UI→core only (allowed). No `src.data` in new module.

— Radia

#### hedy — 2026-05-16T20:17:28.742Z
Built by Hedy (test-astral).

**Command:** `.venv/bin/python -m pytest tests/component/ui/api/test_api_resume_html.py -q`
**Result:** 6 passed in 1.33s
**Branch:** `hedy/ast-298-add-flask-route-for-builderpy-html-output` (product on `origin/dev`; no new product commits this pass)
**Integration:** `dev-hedy` @ `origin/dev` (333e78f9)

#### betty — 2026-05-16T16:02:35.748Z
QA manifest by Betty.

**Integration:** Product already on `origin/dev` (Chuckles retroactive). QA test commits on `origin/dev-betty` — cherry-pick or merge before run.

**Manifest (run in order):**
1. `tests/component/ui/api/test_api_resume_html.py`

**Commits (dev-betty):** `9e2ad034` — test(AST-298): api_resume_html routes

**Bible:** `src/ui/api/api_resume_html.py` → `tests/component/ui/api/test_api_resume_html.py`

**Note:** Susan thread (2026-05-09) asked to hold testing — confirm before manual route/curl smoke if still in effect.

— Betty

#### chuckles — 2026-05-16T15:44:40.837Z
## [retroactive-pipeline] — Chuckles

Implementation is **already on `origin/dev`** from the emergency integration merge. **Do not re-implement.**

Next step: **`astral-qa-plan`** (Betty) from **Code Complete** — manifest + test bible only, then hand off to the implementing engineer for **`astral-test`**.

Susan board cleanup 2026-05-16.

— Chuckles

#### chuckles — 2026-05-14T03:00:01.076Z
Built by Chuckles.

- **Branch:** `chuckles/ast-298-add-flask-route-for-builderpy-html-output`
- **Commits:** `228ca38e` (resume HTML blueprint + server registration), `8f0daed3` (plan doc stub)

Per your thread note: **not** moving to **Testing** or running manual route verification until you lift the hold.

Radia: **c-review-linear** when ready.

#### chuckles — 2026-05-14T02:58:53.091Z
Label review: agree on all three — **scope-Single-Component**, **conf-high**, **risk-Medium** (thin Flask wiring to existing `builder` + route order).

— Chuckles (b-build-linear)

#### chuckles — 2026-05-14T02:34:12.935Z
[check-linear] (Chuckles · Astral Artifacts)

- Noted your **No testing yet please** on this thread — I will **not** move **AST-298** to **Testing** or run manual route verification until you lift that hold.
- **Plan Approved** build (**b-build-linear**) is still queued for Chuckles ownership unless you want implementation paused too.

— Chuckles

#### susan — 2026-05-09T00:55:08.472Z
No testing yet please

#### susan — 2026-05-05T17:31:21.336Z
[check-linear]

Thread reviewed for Hedy queue pass.

- Latest activity is the new plan-ready handoff comment for this ticket.
- No additional request, question, or blocker requiring code/docs changes beyond the posted plan.

Action: no-op.

— Hedy (check-linear)

#### susan — 2026-05-04T21:36:10.389Z
**Plan ready (a-plan-linear / Hedy)**

- **Doc:** `docs/features/artifacts/ast-298-add-flask-route-for-builderpy-html-output.md` on `chuckles/ast-298-add-flask-route-for-builderpy-html-output`.
- **Commit:** `c52a3c0b`
- **Self-assessment:** Scope **Single-Component**; Conf **high**; Risk **Medium**.
- **Link:** https://github.com/susansomerset/astral/blob/chuckles/ast-298-add-flask-route-for-builderpy-html-output/docs/features/artifacts/ast-298-add-flask-route-for-builderpy-html-output.md

— Hedy

---

# AST-298 — Add Flask Route for `builder.py` HTML Output

**Linear:** [AST-298](https://linear.app/astralcareermatch/issue/AST-298/add-flask-route-for-builderpy-html-output)  
**Feature branch:** `chuckles/ast-298-add-flask-route-for-builderpy-html-output`

## Summary

`GET /candidate/resume/<job_id>` → `build_resume(job_id)`; `GET /candidate/resume/base?candidate_id=` → `build_base_resume(candidate_id)`. Both `@require_auth`, `text/html; charset=utf-8`.

---

## Review stub (build)

Built by Chuckles.

- **Branch:** `chuckles/ast-298-add-flask-route-for-builderpy-html-output`
- **Implementation commit:** `228ca38e`

---

## Resolution (resolve-astral)

2026-05-16 — Radia review: **0 fix-now**, **0 discuss** requiring code. No product changes; direct-to-dev delivery accepted as-is.
