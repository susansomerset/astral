# AST-663 — Per-component test bible migration (Restructure ASTRAL_TEST_BIBLE.md into per-component bible files)

<!-- linear-archive: AST-663 archived 2026-06-23 -->

## Linear archive (AST-663)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-663/per-component-test-bible-migration-restructure-astral-test-biblemd  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-598 — Restructure ASTRAL_TEST_BIBLE.md into per-component bible files  
**Blocked by / blocks / related:** parent: AST-598; blocks: AST-664

### Description

## What this implements

Replace the monolith `docs/ASTRAL_TEST_BIBLE.md` with `docs/test-bible/` mirroring `tests/component/` (full mirror of every test module). Add `docs/test-bible/README.md` for cross-cutting standards (§2, §6, §6c, §7.12, appendix — not integration tests). Relocate §7.13 ticket blocks into component files as `### AST-NNN` headers. Split `data/database/` per cluster; `frontend/` as folder-level bible files. Update `docs/ASTRAL_TEAM_WORKFLOW.md`, `docs/ASTRAL_GIT_WORKFLOW.md`, pre-commit hooks, and script comments to reference `docs/test-bible/**`. Delete the monolith only after Radia `review-child` confirms the tree is complete.

## Acceptance criteria

1. Searchable equivalence: every monolith section appears somewhere under `docs/test-bible/`.
2. Full mirror: each `tests/component/**/test_*.py` has a documented home under matching `docs/test-bible/` paths.
3. `docs/test-bible/README.md` is sufficient for an agent to find the right component file without the deleted monolith.
4. `docs/ASTRAL_TEAM_WORKFLOW.md` and `docs/ASTRAL_GIT_WORKFLOW.md` reference `docs/test-bible/`, not the monolith.
5. Radia review-child on this branch documents completeness before monolith delete.
6. After deletion, active workflow docs do not instruct agents to edit `docs/ASTRAL_TEST_BIBLE.md`.

## Boundaries

* Does not update `~/.cursor/skills/` or `betty-AGENTS.md` — sibling **Agent skill updates** ticket.
* No product code under `src/`; no test assertion changes except hook/script path strings.
* No semantic rewrite of manifest rows — split, relocate, re-header only.
* Betty sole writer of bible content; engineers do not commit `docs/test-bible/**`.

## Notes for planning

Use parent definition for structure decisions (README standards vs component files, database clusters, frontend folder shape). Radia gate required before monolith delete.

## Git branch (authoritative)

Per **orientation** § Branch law: parent `ftr/ast-598-restructure-astral_test_biblemd-into-per-component-bible`, child `sub/AST-598/<child-segment>`. Created at dispatch-parent.

### Comments

#### betty — 2026-06-15T04:56:01.144Z
`[check-linear]`

**Sub log hygiene (merge-child §2b):** removed duplicate **`merge-tests(AST-663)`** — rewound to pre-delivery tip `f364aa1a`, single merge of **`origin/tests` `49bbab76`**.

**Publish:** `origin/sub/AST-598/AST-663-per-component-test-bible-migration` @ **`82b672fc`** (`merge-tests(AST-663): origin/tests 49bbab76`). **`merge-tests` count = 1**. Did not touch **`ftr/`**.

Chuckles can re-run **`merge-child AST-663`**.

#### radia — 2026-06-15T02:46:26.773Z
**Review** — `origin/dev...origin/sub/AST-598/AST-663-per-component-test-bible-migration` (tip `a121f957`). AST-663-owned commits: `7c6a806c` (tree migration), `49bbab76` (README/gitignore). Monolith delete correctly **not** in this diff.

## Solid (bible migration)

- **`docs/test-bible/README.md`** — layer index, retired § map, cross-cutting standards (§2, §4a, §6/6c, §7.12, appendix). Sufficient entry point without the monolith.
- **Full mirror:** 61 `tests/component/**/test_*.py` modules → documented home under `docs/test-bible/` (0 gaps). 67 component files; `data/database/` cluster split matches test tree.
- **§7.13 relocation:** 70 `### AST-NNN` manifest blocks in the tree; workflow docs (`ASTRAL_GIT_WORKFLOW.md`, `ASTRAL_TEAM_WORKFLOW.md`) and monolith banner point agents at `docs/test-bible/`.
- **Scripts:** `run_component_tests.sh` / `check_frontend_coverage.py` comment paths updated.

## Pre-monolith-delete checklist (Betty — not engineer)

Monolith still authoritative for three rows **not** yet split into the tree:

| Monolith | Target |
| --- | --- |
| §7.13d **AST-486** inline (`TestTrackerFacades…`) | `docs/test-bible/core/tracker.md` or `consult.md` |
| §7.13zzna **AST-656 / AST-662** | `docs/test-bible/frontend/hooks.md` + `pages.md` |

Until those land in `docs/test-bible/`, AC §1 “searchable equivalence” is not complete for delete.

**Advisory (Betty):** Frontend folder bibles use wrong **Test tree:** headers (`tests/component/pages/` etc.) — should be `tests/component/frontend/…` in `components.md`, `pages.md`, `hooks.md`, `lib.md`, `contexts.md`. Manifest rows inside those files use correct paths.

## Cross-ticket / publish-ref noise (advisory)

Three-dot diff vs `origin/dev` also carries **merge-tests** lineage outside AST-663’s two doc commits: `src/core/bootstrap.py`, `AdminDataManagement.tsx` / `AdminManageCandidates.tsx` (themed confirm), AST-657 test hunks removed, monolith AST-657 row dropped. Not AST-663 implementation scope; do **not** treat as engineer **fix-now** on this ticket.

## Engineer resolve-child

No product **fix-now**. After Betty closes the three-row gap, follow-on can delete monolith per parent AST-598 (sibling AST-664 skills).

#### betty — 2026-06-15T02:31:07.787Z
`[check-linear]`

Cleared Ada's **`[qa-handoff]`** — **Check 3 (full mirror)** fixed.

**Root cause:** `.gitignore` pattern `AGENTS.md` (unanchored) ignored `docs/test-bible/data/database/agents.md` on case-insensitive macOS — file existed locally but never reached git.

**Fix:**
- `.gitignore` → `/AGENTS.md` (repo root only)
- Added `docs/test-bible/data/database/agents.md` — **`### AST-492 · AST-495 · AST-491`** cluster slice for `test_agents.py` + narrow manifest; full epic block remains in `docs/test-bible/ui/api/api_admin.md`

**Publish:** `origin/sub/AST-598/AST-663-per-component-test-bible-migration` @ `a121f957` (`merge-tests(AST-663): origin/tests 49bbab76`)

**Mirror:** `docs/test-bible/data/database/` now **18** `*.md` ↔ **18** `test_*.py` cluster modules.

Assignee → **Ada** for **`test-child`** re-run. Status stays **Tests Ready**.

#### ada — 2026-06-15T02:15:28.512Z
`[qa-handoff]`

@Betty White — docs-only manifest verification on `origin/sub/AST-598/AST-663-per-component-test-bible-migration` @ `4df2df8f` (merged clean on epic worktree).

**Checks 1, 2, 4, 5:** PASS
- Tree present (`docs/test-bible/`, README, monolith pointer)
- `grep -r '^### AST-' docs/test-bible | wc -l` → **72**
- README shasum matches publish ref: `c9650b0e0b06dc98332b52ac12556116396087fb`
- §6c + §7.12 present in README
- `ASTRAL_GIT_WORKFLOW.md` + `ASTRAL_TEAM_WORKFLOW.md` reference `docs/test-bible/**`

**Check 3 — full mirror:** FAIL (test/bible gap, not product)

`tests/component/data/database/` has **18** `test_*.py` cluster modules; `docs/test-bible/data/database/` has **17** `*.md` files.

Missing bible home:

| Test module | Expected bible path |
| --- | --- |
| `tests/component/data/database/test_agents.py` | `docs/test-bible/data/database/agents.md` |

`diff` of cluster stems confirms only `agents` is absent (`_README.md` excluded). `test_agents.py` is referenced in `docs/test-bible/ui/api/api_admin.md` manifest rows but has no per-cluster stub like the other database files (e.g. `agent_data.md`).

Frontend folder-level mirror OK (`root.md` covers `test_App.test.tsx` / `test_routes.test.tsx`).

Please add `docs/test-bible/data/database/agents.md` (stub + any §7.13 content routed from monolith for `test_agents.py`), republish to `origin/sub/AST-598/AST-663-per-component-test-bible-migration`, and reassign Ada for re-run.

#### betty — 2026-06-15T02:13:31.326Z
## QA test manifest (AST-663 — docs-only migration)

**Publish:** `origin/sub/AST-598/AST-663-per-component-test-bible-migration` @ `4df2df8f` (`merge-tests(AST-663): origin/tests 7c6a806c`)

**Bible tree:** `docs/test-bible/README.md` shasum on publish ref: `c9650b0e0b06dc98332b52ac12556116396087fb`

**Scope delivered:**
- 68 markdown files under `docs/test-bible/` (full mirror of `tests/component/**/test_*` + frontend folder-level files)
- Standards in `docs/test-bible/README.md` (§2, §4a, §6/§6c, §7.12, fixtures, Appendix A, retired § map)
- 72 former §7.13* blocks → `### AST-NNN` headers in routed component files
- `docs/ASTRAL_TEAM_WORKFLOW.md` + `docs/ASTRAL_GIT_WORKFLOW.md` → `docs/test-bible/**`
- Harness comments in `scripts/testing/run_component_tests.sh`, `check_frontend_coverage.py`
- Engineer pre-commit hook blocks `docs/test-bible/**`
- Monolith **retained** with AST-598 pointer (delete gated on Radia **review-child**)

### Manifest (verification — no pytest/Vitest required)

1. **Tree present:** `test -d docs/test-bible && test -f docs/test-bible/README.md && test -f docs/ASTRAL_TEST_BIBLE.md`
2. **Ticket block count:** `grep -r '^### AST-' docs/test-bible | wc -l` → 72
3. **Full mirror:** every `tests/component/**/test_*` module has a bible home (Python per-module; frontend folder-level)
4. **Standards spot-check:** README includes §6c routed-page rules and §7.12 branch-lock list
5. **Workflow spot-check:** `ASTRAL_GIT_WORKFLOW.md` + `ASTRAL_TEAM_WORKFLOW.md` reference `docs/test-bible/`

**Not in scope:** agent skills (AST-664); monolith delete (post-Radia)

— Betty

#### betty — 2026-06-15T02:13:05.698Z
**Correction:** `docs/test-bible/README.md` shasum on publish ref @ `4df2df8f`: `c9650b0e0b06dc98332b52ac12556116396087fb`

---

_Implementation detail may live in git history on `origin/dev`._
