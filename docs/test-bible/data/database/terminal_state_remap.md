# Terminal State Remap

**Test module:** `tests/component/data/database/test_terminal_state_remap.py`

_(Coverage map and manifest blocks appended by Betty `qa-child`.)_

### AST-2087 · AST-2073 (persisted-row remap for retired terminal names)

**Publish:** `origin/sub/AST-2073/AST-2087-terminal-state-remap`. Plan: `docs/features/foundation/ast-2087-persisted-row-remap-for-retired-terminal-names.md`.

Operator-only remap of entity `state` and `dispatch_task.trigger_state` off AST-2086's `RETIRED_TERMINAL_STATE_MAP`. Single-target names map directly. Multi-target names resolve from the row's last `state_history` predecessor (trigger state, `_RETRY` stripped, or a `<TRIGGER>.<hop>` label → live `agent_task.run_next`), with a `dispatch_task` tie-break on shared triggers; meteorite `LINK_EXPIRED` resolves from the `scrape_<status>` prefix in `error`. Bare per-task families widen to any task whose bare error is registered. Unresolved rows → `skipped`; dead / unknown states → `unregistered`; neither is written. Writes only `state` / `trigger_state` — never `state_history`, `state_changed_at`, `updated_at`; never runs schema-ensure (the test fixture does).

| Area | Source | Component tests |
| --- | --- | --- |
| Predecessor (from_state, prior to_state, last landing, bad JSON / none) | `src/data/database.py` `_terminal_predecessor` | **`TestAst2087TerminalPredecessor`** |
| Resolution rules (single, trigger + `_RETRY`, company from_state, bare-family widening + non-widening, hop label → run_next / no target, shared-trigger tie-break own / NULL candidate / ambiguous, page-status prefix, unresolvable) | `_resolve_retired_terminal_state` | **`TestAst2087ResolutionRules`** |
| AC 9 contract: dry run writes nothing; execute write surface byte-stable; retired left == skipped per table; dead states untouched + counted; AC 8 live notify row; idempotent | `_terminal_state_remap_conn` | **`TestAst2087RemapContract`** |
| dispatch_task: catalog trigger not a target / no catalog default → skipped; registered triggers not scanned | `_terminal_state_remap_conn` | **`TestAst2087DispatchTaskRemap`** |
| Public wrapper + CLI (dry run default, `--execute`) | `migrate_terminal_state_names`, `scripts/migrations/migrate_terminal_state_names.py` | **`TestAst2087PublicWrapperAndCli`** |

All lines and branches of the new remap block are covered (`database.py` is not on `LOCKED_AT_100`).

**Broken / obsolete:** none — the diff is additive plus one comment reword; `tests/component/data` + `tests/component/scripts` failure set equals `origin/ftr/AST-2073-revise-terminal-states` (64 failed + 2 collection errors, pre-existing).

**Integration:** none.

## QA test manifest

1. `tests/component/data/database/test_terminal_state_remap.py` — all 37 pass (5 classes above).
2. No-regression: `tests/component/data` + `tests/component/scripts` failure set must equal the ftr baseline (no new failures).
3. AC 8 / AC 9 on real data stay an operator step on a **copy** (`ASTRAL_DB_DIR=/tmp/… python3 scripts/migrations/migrate_terminal_state_names.py [--execute]`), never `data/astral.db`; the component tests pin the same assertions on seeded rows.

Notes (no action required): meteorite `SCRAPE_ERROR` rows landed from the old `BOT_BLOCKED` claim stay in `skipped` (plan Out of scope). The plan's `python …` commands need `python3` on hosts without `python-is-python3`.

```bash
./scripts/testing/run_component_tests.sh tests/component/data/database/test_terminal_state_remap.py -q
./scripts/testing/run_component_tests.sh
```

**Bible shasum (after publish):** `git show origin/sub/AST-2073/AST-2087-terminal-state-remap:docs/test-bible/data/database/terminal_state_remap.md | shasum` · same for `docs/test-bible/data/database.md`
