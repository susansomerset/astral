# AST-582 — UAT: Archive intake session to candidate_data.intakes_old

<!-- linear-archive: AST-582 archived 2026-06-23 -->

## Linear archive (AST-582)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-582/uat-archive-intake-session-to-candidate-dataintakes-old  
**Status at archive:** Done  
**Project:** Astral Candidate  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-539 — Candidate Intake Chat Session  
**Blocked by / blocks / related:** parent: AST-539

### Description

## Repro (Susan UAT AST-539 @ `699c5d04`)

Reopening **Intake** with an active session — no **Start Over** for fast UAT iteration.

## Expected

When candidate has an **active** intake session, **Start Over** archives current session onto `candidate_data.intakes_old` (append `{conversation thread}` entries; keep Execution History).

Deactivate/supersede active `candidate_intake_session`; expose API for UI (archive + fresh create).

## Boundaries

Does not regress **558/559**. Parent: AST-539.

### Comments

#### radia — 2026-06-05T20:16:36.727Z
**Diff:** `origin/dev...origin/sub/AST-539/AST-582-archive-intake-to-intakes-old` @ `aabdbf1e` (product+tests); review doc @ `875c4a55`.

**Plan fidelity:** Matches stages 1–4 — `session_status_archived`, `_append_intakes_old` read-append-write, `archive_active_intake_session`, `POST /api/candidates/{id}/intake/sessions/active/archive`, pytest `-k archive` (6 green). UI deferred to **AST-583** per scope.

**§3.3 layering:** `api_intake.py` → `src.core.intake` only; core uses `database` / `get_candidate` / `save_candidate_data` / `INTAKE_CONFIG`. No UI→data bend.

**Parent UAT intent:** Archive appends `transcript` to `candidate_data.intakes_old`; session row → **ARCHIVED**; `get_active_intake_session` filters `ACTIVE` only — ledger/`agent_data` untouched.

**advisory:** Pre-existing `POST …/sessions` can still create a second **ACTIVE** row if caller skips archive (**AST-583** Start Over will archive first). Not a regression from this diff.

**fix-now:** none — proceed to `resolve-astral`.

**Review doc:** [ast-582 plan + Radia review](https://github.com/susansomerset/astral/blob/875c4a55/docs/features/candidate/ast-582-uat-archive-intake-session-to-candidate-data-intakes-old.md#review-radia)

#### betty — 2026-06-05T20:14:30.415Z
**Bible shasum (publish ref):** `3744ee94ff7e051ec411fedbfffddeecafd3d14c579d75042ff296567f8972e5`

— Betty

#### betty — 2026-06-05T20:14:27.937Z
## QA test manifest (AST-582)

**Publish ref:** `origin/sub/AST-539/AST-582-archive-intake-to-intakes-old` @ `aabdbf1e`

**`docs/ASTRAL_TEST_BIBLE.md` shasum (publish ref):** run `git show origin/sub/AST-539/AST-582-archive-intake-to-intakes-old:docs/ASTRAL_TEST_BIBLE.md | shasum -a 256` on engineer tree after merge.

### Manifest

1. **Core archive behavior** — `tests/component/core/test_intake.py` class `TestIntakeArchive`:
   - `test_archive_active_session_appends_intakes_old_and_clears_active`
   - `test_archive_raises_when_no_active_session`
   - `test_second_archive_appends_second_entry`
2. **API route** — `tests/component/ui/api/test_api_intake.py`:
   - `test_archive_active_requires_auth`
   - `test_archive_active_404_when_none`
   - `test_archive_active_200_shape`
3. **Regression (AST-558 / AST-559)** — full intake pytest files unchanged semantics:
   - `tests/component/core/test_intake.py`
   - `tests/component/ui/api/test_api_intake.py`

### Narrowed run (§7.13zr AST-582)

```bash
.venv/bin/python -m pytest tests/component/core/test_intake.py -k archive -q
.venv/bin/python -m pytest tests/component/ui/api/test_api_intake.py -k archive -q
```

### Full gate

```bash
.venv/bin/python -m pytest tests/component/core/test_intake.py tests/component/ui/api/test_api_intake.py -q
```

**Note:** Product shipped without planned tests; Betty added manifest per plan Stages 3–4. No React (AST-583).

— Betty

#### chuckles — 2026-06-05T20:11:41.738Z
## Plan validation — APPROVED

Plan aligns with Susan UAT (archive thread to `candidate_data.intakes_old`, ARCHIVED status, Execution History untouched). Scope is backend-only; AST-583 owns UI. List append pattern correctly avoids `_deep_merge` list replacement.

**Verdict:** APPROVED → Plan Approved.

— Chuckles

#### ada — 2026-06-05T20:11:16.468Z
Plan: [`docs/features/candidate/ast-582-uat-archive-intake-session-to-candidate-data-intakes-old.md`](https://github.com/susansomerset/astral/blob/sub/AST-539/AST-582-archive-intake-to-intakes-old/docs/features/candidate/ast-582-uat-archive-intake-session-to-candidate-data-intakes-old.md) @ `0fc8b84b`

**Scope:** `Single-Component` — backend only (`INTAKE_CONFIG` ARCHIVED status, `archive_active_intake_session`, `POST …/sessions/active/archive`, component tests); Katherine **AST-583** owns Continue/Start Over UI.

**Conf:** `high` — Susan’s parent-thread spec (`intakes_old` append + supersede active session, keep Execution History) maps directly onto existing **AST-558** session store/API patterns.

**Risk:** `Medium` — touches intake session lifecycle and `candidate_data` blob append semantics; plan keeps ledger/`agent_data` intact and leaves **558/559** create/turn/build paths unchanged.

---

_Implementation detail may live in git history on `origin/dev`._
