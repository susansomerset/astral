<!-- linear-archive: AST-295 archived 2026-06-03 -->

## Linear archive (AST-295)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-295/add-split-to-list-to-formattingpy  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** hedy  
**Priority / estimate:** Low / 1  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Add split_to_list(value: str, delimiter: str = ',') -> list\[str\] to src/utils/formatting.py. Splits string on delimiter, strips whitespace from each token, filters empty strings. Used by [builder.py](<http://builder.py>) to parse comma-separated agent output fields such as critical_keywords from grade_get. Delimiter defaults to comma; caller can override for future use.

### Comments

#### susan — 2026-04-29T03:26:53.030Z
Merged to `dev` (squash): `3b77f5c1fe67799a986e44022c9568631a00d52e`

PR: https://github.com/susansomerset/astral/pull/119

#### susan — 2026-04-29T03:22:25.008Z
I can't really test this, but I looked at the code.

#### susan — 2026-04-29T03:11:21.999Z
Review feedback resolved. Branch `chuckles/ast-295-add-split_to_list-to-formattingpy` is ready for testing. Commit: `7266bd868c5db8fe5aef90f97e24d00f4d8749e3`

Changes: explicit non-empty `delimiter` guard + docstring on `split_to_list`; **Resolution** section appended to `docs/features/artifacts/ast-295-add-split-to-list-to-formattingpy.md`. Advisory tests deferred (no pytest/utils harness in repo yet).

**Push:** `git push origin chuckles/ast-295-add-split_to_list-to-formattingpy` did not run from this agent (GitHub unreachable); push locally if the commit is not on origin yet.

#### susan — 2026-04-29T03:05:52.689Z
**Code review posted** (AST-295)

**Counts:** 0 fix-now · 1 discuss · 1 advisory

**Combined doc:** [docs/features/artifacts/ast-295-add-split-to-list-to-formattingpy.md](https://github.com/susansomerset/astral/blob/chuckles/ast-295-add-split_to_list-to-formattingpy/docs/features/artifacts/ast-295-add-split-to-list-to-formattingpy.md)

**Discuss:** Empty `delimiter` → `str.split` raises; document or guard if delimiter is ever dynamic.

**Advisory:** Add unit tests when the artifacts/utils test layout exists.

#### susan — 2026-04-29T03:03:46.379Z
**Build complete (local commits)**

- **Branch:** `chuckles/ast-295-add-split_to_list-to-formattingpy`
- **Feature commit:** `f4dc7a978ef7d3e0234faa0d1c19ca8301531148` (`split_to_list` in `src/utils/formatting.py`; removed legacy `-plan` stub; tracked combined plan doc)
- **Docs commit:** `fb9fd10` — review stub on `docs/features/artifacts/ast-295-add-split-to-list-to-formattingpy.md`

`git push -u origin chuckles/ast-295-add-split_to_list-to-formattingpy` did **not** run from the agent (GitHub unreachable). Please push from your machine. `git pull origin dev` was also skipped for the same reason — reconcile with `origin/dev` before push if needed.

#### susan — 2026-04-29T03:02:11.515Z
Label review (build agent): **agree on all three** — `scope-minor`, `conf-high`, and `risk-low` match the plan and self-assessment (single utils helper, ticket-specified behavior, artifact-only blast radius).

#### susan — 2026-04-29T02:55:55.972Z
**Plan (skill run)** — `docs/features/artifacts/ast-295-add-split-to-list-to-formattingpy.md`

**Self-assessment**
- **Scope — minor:** One utils helper plus a thin `builder.py` call-site when that file exists; no DB/dispatch/schema.
- **Conf — high:** Ticket specifies split/strip/drop-empty and default comma; standard parsing pattern.
- **Risk — low:** Bad parsing affects artifact keyword lists only, not core consult state or scoring.

**Note:** `git fetch && git rebase origin/main` could not be run from the agent environment (GitHub unreachable); please run locally before build.

Labels applied: `scope-minor`, `conf-high`, `risk-low`. Status → **Plan Ready**.

---

# AST-295 — Add `split_to_list()` to `formatting.py`

**Linear:** [AST-295](https://linear.app/astralcareermatch/issue/AST-295/add-split-to-list-to-formattingpy)  
**Project:** Astral Artifacts → `docs/features/artifacts/`  
**Branch workflow:** Implement on `dev` per `ASTRAL_CODE_RULES.md` §4.1 (Linear branch names are labels only).

## Agent environment (step 3)

`git fetch origin && git rebase origin/main` was **not** executed successfully from this session (GitHub host unreachable via SSH from the agent sandbox). Before implementation, run locally:

`git checkout dev && git fetch origin && git rebase origin/main`

---

## Plan

1. **Add `split_to_list(value: str, delimiter: str = ",") -> list[str]`** in `src/utils/formatting.py`.
   - Split `value` on `delimiter`.
   - `strip()` each token; omit tokens that are empty after strip (so `"a,,b"` → `["a", "b"]`, `"  "` → `[]`).
   - For `value` that is not a string, either document as caller responsibility or coerce to `str` only if existing helpers in the same file establish that pattern — **default: require `str`** (ticket signature) and callers pass `str`.
   - Place near other small string helpers (after `value_to_str` / before HTML helpers is reasonable) with a one-line comment that this is for delimited agent fields (e.g. comma-separated keywords).

2. **Consumer: `builder.py`** (when present on `dev`, per ticket and artifacts track).
   - Replace any ad hoc `x.split(",")` + strip + filter for agent output fields such as **`critical_keywords`** from **`grade_get`**-sourced strings with `split_to_list(...)`.
   - Use default comma unless a field spec defines another delimiter; pass `delimiter=` only when needed.

3. **Verification**
   - Quick REPL or minimal script check if no automated test module exists yet for `formatting.py`.
   - If a test layout exists by implementation time, add focused cases: empty, whitespace-only, extra commas, custom delimiter, tokens with internal spaces (should be preserved after strip).

### Files changed (expected)

| File | Change |
|------|--------|
| `src/utils/formatting.py` | New `split_to_list` |
| `builder.py` (path TBD when landed from AST-294 / AST-298 work) | Use helper for `critical_keywords` and any identical parsing |

### Flagged decisions

- **`builder.py` not in tree** on current `dev` snapshot: implement and land **`split_to_list` first**; wire `builder.py` in the same PR or the next artifacts PR that introduces the parser — whichever matches how AST-294/298 merge. No speculative new file from this plan alone.

---

## Rule check (`ASTRAL_CODE_RULES.md`)

| Section | Check |
|---------|--------|
| §1.3 DRY | One shared helper; no copy-paste split/strip loops in multiple call sites once `builder` exists. |
| §2.1 config | No new config keys; delimiter is a parameter with a literal default, not a policy table. |
| §2.4 batch | N/A — string utility, no dispatch. |
| §2.6 state machine | N/A. |
| §3.3 imports | `formatting.py` stays utils-only (already must not import `config`). |
| §3.5 naming | `snake_case` function name per ticket. |

**Conflicts:** None identified; plan is implementable as written.

---

## Self-Assessment

**Scope — `minor`**  
Touches one utils module plus a thin call-site change in `builder.py` when that file exists; no schema, DB, or dispatch changes.

**Conf — `high`**  
The behavior is fully specified in the Linear description (split, strip, drop empty, default comma); same pattern as common CSV-token parsing elsewhere.

**Risk — `low`**  
Wrong parsing would mis-display or mis-rank keywords in artifact output, but would not corrupt core job state or consult scoring; scope is limited to presentation / builder input handling.

---

## Review

**Commit:** `f4dc7a978ef7d3e0234faa0d1c19ca8301531148`  
**Branch:** `<agent>/ast-295-add-split_to_list-to-formattingpy`  
**Reviewed:** 2026-04-29

---

## What's Solid

- **Plan fidelity:** `split_to_list(value: str, delimiter: str = ",") -> list[str]` matches the ticket (comma default equivalent to `','`). Split → strip per token → drop empties is implemented as a single list comprehension; cases like `"a,,b"` and all-whitespace behave as specified.
- **Placement:** Sits after the small string helpers block (`format_grade_display`) and before `parse_text` / HTML work, aligned with the plan’s “before HTML helpers” guidance.
- **Deferred consumer:** No `builder.py` wiring in this diff — matches the plan’s explicit “land helper first” / AST-294+298 dependency note; no speculative call sites.
- **§3.3 (imports):** No new imports; helper uses only `str.split` / `str.strip`. `formatting.py` stays utils-pure relative to core/data/external.
- **§1.3 (DRY):** One shared helper for the comma-separated keyword pattern; ready for `builder.py` when that lands.
- **§2.1 (config):** Delimiter is a parameter with a literal default — no new config surface.
- **§3.5 (naming):** `snake_case` name per ticket.
- **Docs housekeeping:** Stub `ast-295-add-split-to-list-to-formatting-py-plan.md` removed in favor of this single combined doc under `docs/features/artifacts/`, consistent with §4.2.

---

## Issues

### Issue 1 — Empty `delimiter` at runtime raises `ValueError` (discuss)

In Python 3, `"x".split("")` raises `ValueError: empty separator`. Typed default `","` is safe for normal use; if a future caller passes `delimiter` from config or agent data without validation, failure mode is a hard exception rather than an empty list.

**Recommendation:** Either document “delimiter must be non-empty” in the docstring, or validate and raise a domain-clear error (or return `[]` — product choice).

---

### Issue 2 — No automated tests in this diff (advisory)

The plan called out optional REPL check or tests “if a test layout exists.” This diff only adds the helper. Low risk given the trivial logic, but regression protection would help once the artifacts test harness exists.

---

## Recommended Actions

| # | Severity | Action |
|---|----------|--------|
| 1 | Discuss | Decide whether empty `delimiter` should be documented, rejected with a clear error, or handled — so dynamic callers do not trip `str.split` unexpectedly. |
| 2 | Advisory | When the artifacts / utils test module exists, add cases: empty string, whitespace-only, repeated commas, custom delimiter, internal spaces preserved after strip. |

---

## Resolution

### Issue 1 (Discuss) — empty `delimiter`

**Decision:** Reject with an explicit `ValueError` before calling `str.split`, and document the contract in the docstring so callers passing config/agent-derived delimiters get a clear failure instead of Python’s built-in empty-separator error.

**Code:** `src/utils/formatting.py` — `split_to_list` now checks `if not delimiter:` and raises `ValueError("split_to_list: delimiter must be non-empty")`.

### Issue 2 (Advisory) — automated tests

**Status:** Deferred. Repo has no `pytest` layout or `tests/` package for `src/utils`; scripts under `scripts/test_*.py` are integration-style. When a utils/unit harness exists, add cases called out in review (empty input, whitespace-only, repeated commas, custom delimiter, internal spaces after strip).
