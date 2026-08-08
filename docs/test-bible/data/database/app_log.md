# App Log

**Test module:** `tests/component/data/database/test_app_log.py`

### Coverage map

| Area | Source | Component tests |
| --- | --- | --- |
| Append + batch/level list filter | `src/data/database.py` (`add_log_entry`, `list_log_entries`) | `TestAddLogEntry`, `TestListLogEntries` |
| Integer AUTOINCREMENT PK (fresh + migrate + write) | same (`_ensure_app_log_schema`, `add_log_entry`) | `TestAst1266IntegerPk` |

### AST-1266 · AST-1263

**Scope:** `app_log` integer `AUTOINCREMENT` PK on fresh DBs; TEXT→INTEGER rebuild (drop leftover `app_log_new` first); `add_log_entry` omits client UUID; Execution History `LogEntry.id` typed `number` (mock ids numeric). Does **not** rename column, touch `logging.py` late-import, or change other tables’ PKs.

| AC | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| 1 | Fresh `app_log` → `id INTEGER PRIMARY KEY AUTOINCREMENT` | `src/data/database.py` `_ensure_app_log_schema` | `TestAst1266IntegerPk::test_fresh_schema_integer_autoincrement_pk` |
| 2 | Legacy TEXT PK rebuild; payload preserved; new writes succeed | same | `test_migrates_text_pk_preserving_payload`; `test_leftover_app_log_new_does_not_brick_rebuild`; `test_already_integer_is_noop` |
| 3 | Insert without client UUID; list filter still works; EH keys numeric ids | `database.py` `add_log_entry` / `list_log_entries`; `AdminPerformanceMonitor.tsx` | `test_write_assigns_distinct_positive_ints_without_client_id`; existing `TestListLogEntries`; FE page mocks use numeric `id` |
| 4 | No other table PK changed | Files Changed scope | (scope gate — only `app_log` + EH type) |
| 5 | Late-import `_flush_buffer` → `add_log_entry` unchanged | `src/utils/logging.py` (read-only) | docs-acceptance grep below |

**Broken / obsolete revised:** Execution History Vitest log fixtures used string UUID-like `id` values — updated to JSON numbers to match Stage 2 `LogEntry.id: number`.

**AST-1266** narrowed run:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_app_log.py \
  -q
```

```bash
cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/pages/test_AdminPerformanceMonitor.test.tsx \
  -t "loads ledger rows|AST-840 log level filter|expands hop-scoped logs"
```

**AC5 docs-acceptance (required):** on publish tip,

```bash
rg -n "_flush_buffer|add_log_entry" src/utils/logging.py
```

Expect late `from src.data.database import add_log_entry` **inside** `_flush_buffer` only (no module-top data import; buffer dict keys `level` / `logger_name` / `message` / `batch_id` only).

**Pass criterion:** pytest + Vitest green on manifest lines + AC5 grep — not zero-arg harness / branch-lock gate.
