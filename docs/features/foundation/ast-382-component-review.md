# Plan: AST-382 — Component Review (rubric campaign)

**Linear:** https://linear.app/astralcareermatch/issue/AST-382/component-review  
**Feature branch:** `betty/ast-382-component-review`

## Summary

This ticket owns the **structured `src/` rubric review** described in the issue body: drive `debug/code_review_scorecard.md` and `debug/code_review_notes.md` (append-only) until every in-scope source file is graded, then **close the remediation gap** exclusively through linked child issues (**AST-384–AST-388** and any future splits Susan adds). This plan does **not** duplicate implementation steps from children; it defines **orchestration, definition of done, and handoff rules**.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `debug/code_review_scorecard.md` | Append rows only (never rewrite header/table history) | debug |
| `debug/code_review_notes.md` | Append sections per file reviewed | debug |
| `docs/features/foundation/ast-382-component-review.md` | This plan | docs |
| `docs/ASTRAL_CODE_RULES.md` | Optional one-line pointer to rubric location if Susan wants single canonical link (only if Susan approves doc churn in same PR as campaign wrap-up) | docs |

No production Python changes on **AST-382** itself unless Susan explicitly expands scope; code fixes belong to **AST-384–388** / **AST-321** / **AST-383** per notes.

## Stage 1: Campaign inventory and ordering

**Done when:** There is a single ordered checklist of `src/` files (and `src/ui/frontend` TSX where in scope) not yet present on the scorecard, with no duplicates.

1. Parse `debug/code_review_scorecard.md` for existing filenames in the data column (skip header rows).
2. Build inventory from `git ls-files 'src/**/*.py'`, `git ls-files 'src/ui/frontend/src/**/*.{tsx,ts}'` (adjust globs to match repo after UI move), excluding generated paths if any.
3. Subtract already-scored files; sort remainder: **data → external → utils → core → ui API → ui frontend** (bottom-up dependency intuition) unless a file is explicitly unblocked earlier.
4. If inventory is empty, skip to Stage 3 (closure).

## Stage 2: Execute rubric passes (append-only artifacts)

**Done when:** For each file in Stage 1 inventory, scorecard has one new row and notes have a section (findings or “No findings”).

1. For each file, run the rubric in the parent issue description: applicable vectors only; B/C/D/F require line-level snippets + notes + Linear scope line per existing notes convention.
2. Append to `code_review_scorecard.md` and `code_review_notes.md` only — never delete historical rows.
3. When findings map to an existing child (**B1→384, B2→385, E1→386, G1→387, logging.py B2+D2→388**), end the file section’s **Linear** line naming that child (match style already in `code_review_notes.md`).

## Stage 3: Child ticket hygiene and parent closure

**Done when:** Every open finding in notes has a corresponding open Linear child or accepted deferral comment from Susan; parent **AST-382** can move to **Done** only after children that block “zero B2 in UI for non-admin” (per product priority) are resolved or explicitly waived.

1. Reconcile `debug/code_review_notes.md` against Linear: if a vector cites **AST-321** or **AST-383**, do not spawn duplicate tickets; reference those.
2. If new vectors appear that do not fit **384–388**, add a **short** Linear comment on **AST-382** listing proposed new ticket titles — **stop** for Susan split before coding.
3. Close **AST-382** when: scorecard covers full inventory, and Susan agrees remaining work is entirely owned by children / AST-321 / AST-383.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — Cross-cutting process across entire `src/` tree and shared debug artifacts; “change” is organizational and documentary rather than a single module.

**Conf:** `high` — Child split already exists for main vectors; rubric text is authoritative in the Linear issue.

**Risk:** `Medium` — Mis-routing findings to wrong child ticket wastes implementer time; mitigated by strict vector→ticket mapping in notes.

## Plan vs ASTRAL_CODE_RULES

Process-only ticket; code changes occur on children. Any optional `ASTRAL_CODE_RULES.md` pointer must not contradict §1.1 in-scope rules.
