# AST-1513 — Reject duplicate Do rubric codes (meteorite_grade_do is failing)

<!-- linear-archive: AST-1513 archived 2026-09-09 -->

## Linear archive (AST-1513)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1513/reject-duplicate-do-rubric-codes-meteorite-grade-do-is-failing  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1510 — meteorite_grade_do is failing  
**Blocked by / blocks / related:** parent: AST-1510

### Description

## What this implements

Fix the somerset Do rubric **duplicate **`TP` **code collision** so `meteorite_grade_do` / `grade_do` decode a complete grade set (Hands-On Technical Partnership With Engineers present once; Speaking Truth to Power With Diplomacy not duplicated). Parent bug AST-1510; ancestor context AST-723 (rubric_vector authority).

## Scope

## Component scope

* `src/core/candidate.py` — modified if adding duplicate-code validation on rubric save/sync — reject or warn when two current `rubric_vector` rows for the same owner share a code.
* `src/core/consult.py` — modified only if hardening `_vector_labels_map` to detect/log duplicate codes instead of silent last-wins (diagnostic).
* `src/core/agent.py` — modified only if decode should fail fast on duplicate codes in one line (optional; data fix may be sufficient).
* **Somerset rubric data** (via Artifacts UI / `rubric_vector` rows) — modified — reassign duplicate `TP` so HT and TP are distinct codes (primary fix if collision is data-only).

## Technical scope

* `src/core/candidate.py`: optional new validation in rubric sync/save path — when building criteria from `rubric_vector` rows, raise or surface duplicate `code` values for one `(candidate_id, task_key)` owner before persist. — **done** (`_assert_unique_rubric_codes` in `normalize_rubric_artifacts_on_save`)
* `src/core/consult.py`: optional `_vector_labels_map` change — detect duplicate codes in input list and log/raise Style D detail under `debug=True` instead of silent last-wins overwrite. — **done** (warning + first-wins map; `debug_detail` when `debug=True`)
* `src/core/agent.py`: optional decode guard — if the same two-char code appears twice in one encoded line, treat as incomplete/retry with explicit duplicate-code detail (AST-1155 retry path). — **done** (`_decode_payload` duplicate segment check)
* **Rubric data**: reassign the colliding vector's code (likely HT vs TP) so `_vector_labels_map` and the model prompt agree on eleven unique codes. — **staging ops** (Artifacts save on somerset; not product code)

## Acceptance criteria

1. Somerset Do rubric has unique two-letter codes for every vector (HT and TP distinct). — **pending staging data fix**
2. A somerset `meteorite_grade_do` batch decodes and applies scored pass/fail without incomplete-grade error for missing HT. — **pending staging data fix + re-run**
3. Duplicate code assignment is rejected or surfaced at save/sync (product guard), not silent last-wins only. — **done**

## Boundaries

Does not reopen AST-1150 retry-routing policy. Does not change `_render_score` math for complete grade sets. vector_reviews wire-format parse failures are secondary unless they block scoring.

### Comments

#### radia — 2026-08-27T00:04:34.871Z
[code-rubric] PROCEED (Commit: 3d8eae67) duplicate rubric code guards clean

#### betty — 2026-08-26T23:59:44.545Z
[bug-repro]
origin/sub/AST-1510/AST-1513-reject-duplicate-do-rubric-codes @ ca88ef5e · repro lands red, awaits fix

#### joan — 2026-08-26T23:56:43.692Z
[board-joan] CANON: OK

Scoped statutes and patterns: no canon update required. Save-time duplicate-code guard and `_vector_labels_map` collision diagnostics extend existing grade-vector-validation and data-raises-caller idioms without conflicting with embedded-wins-on-code (preserved in What must still hold).

#### betty — 2026-08-26T23:46:50.859Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/candidate.md — no duplicate rubric-code save guard — repro-first test for do_rubric duplicate TP → ValueError/400 before sync; docs/test-bible/core/consult.md — _vector_labels_map duplicate-code collision (HT/TP last-wins → incomplete grade set) untested; optional docs/test-bible/core/agent.md — _decode_payload duplicate segment guard if Step 4 lands

#### hedy — 2026-08-26T23:45:36.894Z
`origin/sub/AST-1510/AST-1513-reject-duplicate-do-rubric-codes` @ `946f8031` · duplicate TP guard + HT fix

---

_Implementation detail may live in git history on `origin/dev`._
