# ast-288: Consult Uses Agent Model — Code Review

**Branch:** `<agent>/ast-288-consult-uses-agent-model`
**Commits reviewed:** 5
**Reviewer:** Chuckles

---

## Overall Assessment

**Ship it.** Most of the heavy lifting was already done in AST-287. This ticket is cleanup, fixes, and a data model refinement. No functional risks — all changes are straightforward and the syntax fix resolves a production crash.

---

## Commit `37d98a0` — Plan document

Initial plan committed. Accurately described the scope: AST-287 already plumbed model params through `do_task`, so consult.py needed no changes. Plan identified the stale comment and renamed task key as the only real work items.

---

## Commit `49f4591` — Fix stale comment + renamed task key

`**src/external/anthropic.py`:** Stale comment on line 37 referencing `ASTRAL_CONFIG["api"]` (which was removed in AST-287) replaced with accurate description of how model params flow from agent records.

`**src/core/candidate.py`:** `do_task(task_key="parse_resume", ...)` updated to `"parse_resume_text"` matching the TASK_CONFIG rename from the 287 config reorg. Docstring updated to match. Without this fix, `parse_candidate_resume()` would raise `ValueError("Unknown task_key: parse_resume")` at runtime.

Clean, minimal, correct.

---

## Commit `6de19a6` — Fix unclosed brace in TASK_CONFIG

`**src/utils/config.py`:** The `craft_application_responses` entry (last entry in TASK_CONFIG) was missing its closing `},`. The `}` on what was line 420 closed the entire `TASK_CONFIG` dict instead of the entry dict, causing `SyntaxError: '{' was never closed` — a production crash on deploy.

One-character fix (added trailing comma). Root cause: the config reorg in the 287 merge introduced new stub entries (`craft_job_resume`, `craft_job_cover_letter`, `craft_application_responses`) and the last one was missing the trailing comma on its closing brace. Python's parser doesn't catch this at the dict level until it hits the `def` keyword after the dict.

**Lesson:** Always run `python3 -c "import ast; ast.parse(open('file').read())"` on config files before merging — the linter doesn't always catch unclosed containers in large dicts.

---

## Commit `02a9f68` — Rename bio_upshot → bio_summary, move to context

`**src/utils/config.py`:**

- `TOKEN_SOURCES`: `BIO_UPSHOT` → `BIO_SUMMARY`, path changed from `artifacts.bio_upshot` to `context.bio_summary`. This is a breaking change for any prompts using `{$BIO_UPSHOT}` — they need to switch to `{$BIO_SUMMARY}`. No existing prompts use either token yet (the `bootstrap_candidate_context` task is new), so no breakage in practice.
- `TASK_CONFIG["bootstrap_candidate_context"]` response_schema: `bio_upshot` field renamed to `bio_summary`.

`**src/data/database.py`:**

- Added `_migrate_bio_upshot_to_summary()`: scans all candidate rows, moves `artifacts.bio_upshot` to `context.bio_summary` if present. Idempotent — skips rows where `context.bio_summary` already exists. Called from `_migrate_candidate_data_structure()` so it runs on next boot.

The relocation makes semantic sense: `bio_summary` is candidate-provided data that can optionally be seeded by AI, not a pure AI artifact. It belongs alongside `strengths`, `priorities`, and `deal_breakers` in context.

---

## Cross-cutting concerns

**No consult.py changes.** The ticket's acceptance criteria asked for explicit model param passing in consult.py. This is already satisfied by `do_task`'s internal design — the caller passes a `task_key`, and `do_task` resolves the agent, reads model params from the agent row, and threads them through `_fetch_response_from_content` → `_send_and_parse`. No consult.py code change needed.

**No tests added.** Consistent with codebase conventions — no test infrastructure exists for these layers.

---

## Summary of actionable items


| #   | Severity | Location    | Issue                                                                      |
| --- | -------- | ----------- | -------------------------------------------------------------------------- |
| 1   | Note     | `config.py` | Any future prompts using `{$BIO_UPSHOT}` must use `{$BIO_SUMMARY}` instead |
| 2   | Note     | Process     | Add syntax validation step before merging config changes with large dicts  |


None are blockers. Both are informational.

---

## Commit `202f684` — Profile page rewrite, TabBar extraction, Script Sandbox stub

Big commit — 7 files, +236/−65 — but the pieces are independent and each is clean.

### `src/ui/frontend/src/components/TabbedTextArea.tsx` (new file, 67 lines)

Two exports: generic `TabBar<K>` (tab-switching strip) and `TabbedTextArea` (TabBar + textarea per tab). `TabBar` is typed with a generic key parameter so it slots into both string-keyed (TaskPrompts) and index-keyed (Profile) use cases without casting. `TabbedTextArea` tracks active tab by numeric index internally and maps to/from the generic `TabBar` via `String(i)` / `Number(k)` — straightforward and correct. Uses existing `getByPath` from `FormFields` for dot-path value resolution.

One observation: the `useState` import is only used by `TabbedTextArea`, not by `TabBar`. If `TabBar` is ever extracted to its own file, the import won't follow — but that's a non-issue today.

### `src/ui/frontend/src/pages/Candidate/Profile.tsx` (+91/−13 → rewrote)

Replaced generic `DetailsEditPage` wrapper with a custom layout: 2-column contact grid (first 4 fields left, next 4 right) plus `TabbedTextArea` for the remaining DATA_SHAPES sections. The old code passed `data` to `DetailsEditPage` and let it manage edits; the new code owns `values` state directly via a local `set(key, value)` helper and a dedicated `handleCancel` that resets to `fetched.data`. This is the right move — the profile page has bespoke layout needs (tabbed textareas, disabled resume field) that a generic form wrapper can't accommodate.

The hardcoded `slice(0, 4)` / `slice(4, 8)` for splitting contact fields into two columns is coupled to the current DATA_SHAPES structure — if someone adds a 9th contact field, it silently falls off the grid. Worth noting but acceptable since the shape definition is co-maintained.

Resume lock logic (`disabled: isResume && hasBaseResume`) checks `artifacts.base_resume` existence to disable editing of `context.starting_resume_text`. Correct behavior — once the resume has been parsed into a structured base resume, the raw input text shouldn't be casually editable.

### `src/ui/frontend/src/pages/Admin/TaskPrompts.tsx` (−44/+14 → net −30 lines)

Replaced two inline tab-bar implementations (edit modal, preview modal) with `TabBar` from the new component. The old code had identical inline `<button>` blocks with 13-line inline style objects duplicated in two places. The refactor removes ~60 lines of inline styles and replaces them with 6 lines each — clean dedup. The `TAB_LABELS` / `PREVIEW_LABELS` records were converted from `Record<K, string>` to `{ key: K; label: string }[]` arrays to match the `Tab<K>` interface. Good call — the array form preserves tab order explicitly instead of relying on object key insertion order.

### `src/utils/config.py` — DATA_SHAPES + NAV_CONFIG

**DATA_SHAPES:** Profile sections reordered from [Contact, Resume, LinkedIn, Cover Letter] to [Contact, Bio Summary, Sample Cover Letter, LinkedIn Profile Text, Original Resume Text]. Labels updated to be more descriptive. `bio_summary` added as a new section — this aligns with the `bio_upshot → bio_summary` rename from commit `02a9f68`.

**NAV_CONFIG:** Added `Script Sandbox` nav entry under Admin. Routes to `/admin/script_sandbox`.

### `src/ui/frontend/src/routes.tsx` + `NavigationShell.tsx` + `App.css`

**routes.tsx:** Added `script_sandbox` route pointing at the existing `StubPage` component — placeholder for future work.

**NavigationShell.tsx:** Added `<span className="nav-footer-spacer" />` at the bottom of the `<nav>`. This is an 80px invisible block that prevents the last nav items from being hidden behind any fixed-position footer popups.

**App.css:** +54 lines — `profile-contact-grid` (2-column CSS grid), full `tabbed-ta-`* class family (bar, tab, active state, textarea sizing, disabled styling), and the nav footer spacer. All use existing CSS custom properties (`--border`, `--accent-gold`, `--text-primary`, etc.). The tab styling matches the inline styles that were removed from TaskPrompts, so visual consistency is preserved.

---

## Updated actionable items


| #   | Severity | Location            | Issue                                                                                                                                      |
| --- | -------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Note     | `config.py`         | Any future prompts using `{$BIO_UPSHOT}` must use `{$BIO_SUMMARY}` instead                                                                 |
| 2   | Note     | Process             | Add syntax validation step before merging config changes with large dicts                                                                  |
| 3   | Note     | `Profile.tsx:75-76` | Contact field column split hardcoded to `slice(0,4)` / `slice(4,8)` — will silently drop fields if DATA_SHAPES grows past 8 contact fields |


None are blockers.