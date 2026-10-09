# Debug Logging

**Test module:** `tests/component/utils/test_debug_logging.py`

### AST-554 (parent AST-538)

**AST-538 (parent):** Mandatory backend debug contract in **`docs/ASTRAL_CODE_RULES.md`** §1.5.1, shared emission API on **`_PrefixedLogger`** (`debug_index`, `debug_detail`, `debug_detail_block`), pure **`truncate_debug_content`** / **`format_debug_index_header`**. Parent AC **7** — Betty tests **gating + truncation math only** (no log-string golden files). Operational backfill (**inflow_discovery** per-index traces, AC 2/4 spot-check) is **AST-557**; nav rename **AST-555**; **review-astral** rubric **AST-556**.

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-554** | Constants, truncation helper, index header formatter, debug-gated emission (severity corrected to **DEBUG** by **AST-979**) | `src/utils/logging.py`, `docs/ASTRAL_CODE_RULES.md` §1.5.1 | **`TestTruncateDebugContent`**, **`TestFormatDebugIndexHeader`**, **`TestPrefixedLoggerDebugGating`** in **`test_debug_logging.py`**; regression **`test_logging_batch.py`** |

**AST-554** narrowed run (pytest-only — python-only child; avoids Vitest tail / **AST-511** cross-ticket noise on engineer worktrees):

```bash
.venv/bin/python -m pytest tests/component/utils/test_debug_logging.py tests/component/utils/test_logging_batch.py -q
```

**`[qa-handoff]` return (2026-06-03):** Ada **`test-astral`** — `run_component_tests.sh` with trailing paths still invoked full Vitest on **`dev-ada`**; manifest uses direct **`pytest`** gate (13 tests). Harness on **`dev-betty`** skips Vitest when trailing paths are set (**Appendix A** in [README](../README.md)).

### AST-979 · AST-976

**AST-976 (parent):** Add level **DEBUG** to `app_log` so Execution History can filter debug-gated lines. **AST-979** corrects **stored severity only**: debug-gated helpers (`debug_index` / `debug_detail` / `debug_detail_block` / `test`) emit via `Logger.debug` when `debug_flag=True`; named logger raised to DEBUG (root stays INFO); `_DatabaseLogHandler.setLevel(DEBUG)` so records reach the buffer / `add_log_entry`. Ordinary INFO/WARNING/ERROR unchanged. Execution History Level-list UI is **AST-980** (out of scope).

| Child | Behavior | Sources | Manifest tests |
| --- | --- | --- | --- |
| **AST-979** | Persist DEBUG for debug-gated helpers; silence when flag False; INFO stays INFO; WARNING/ERROR unchanged; named-logger level restore | `src/utils/logging.py` | **`TestPrefixedLoggerDebugGating`** (revised — caplog DEBUG + `levelname`); **`TestAst979DebugLevelPersistence`** in **`test_debug_logging.py`**; regression **`test_logging_batch.py`** |

**AST-979** narrowed run:

```bash
.venv/bin/python -m pytest tests/component/utils/test_debug_logging.py tests/component/utils/test_logging_batch.py -q
```

**Console format:** off-Railway stdout is `%(levelname)s %(name)s: %(message)s`; on Railway (`RAILWAY_ENVIRONMENT`) stdout is one JSON object per line with `level` (`debug`/`info`/`warn`/`error`) + `message`, plus top-level `batch_id` / `candidate_id` when those contextvars are set (omitted, never null, when unset; AST-1988). **`TestAst1988RailwayJsonIds`**. `_DatabaseLogHandler` stays `%(message)s` — `level` and `logger_name` are `app_log` columns. **`TestConsoleFormat`**, **`TestAst1778RailwayConsoleTransport`**.

### AST-1778 · AST-1777

**Parent:** [AST-1777](https://linear.app/astralcareermatch/issue/AST-1777/logging-levels). **Publish:** `origin/sub/AST-1777/AST-1778-railway-faithful-console-transport-in-get-logger`.

Railway-faithful console transport in `get_logger`: product console always on **stdout**; when `RAILWAY_ENVIRONMENT` is set, `_RailwayJsonFormatter` emits JSON `level`+`message` (WARNING→`warn`, CRITICAL→`error`); off-Railway keeps plain `LEVEL name: message`. `_DatabaseLogHandler` / `_db_handler_stderr` unchanged. Telescope / call-site rewrites out of scope; gunicorn is out of scope except the `gunicorn.access` quiet filter (§ AST-2078).

| Area | Source | Component tests |
| --- | --- | --- |
| Railway JSON level map | `src/utils/logging.py` | **`TestAst1778RailwayConsoleTransport::test_railway_json_formatter_maps_levels`** |
| stderr console → stdout | same | **`…::test_ensure_repoints_stderr_handler_to_stdout`** |
| Formatter branch on env | same | **`…::test_apply_formatter_switches_on_railway_env`** |
| Off-Railway plain emit | same | **`…::test_off_railway_emit_is_plain_stdout_shape`** + **`TestConsoleFormat`** |
| On-Railway JSON emit | same | **`…::test_on_railway_emit_is_json_with_level`** |
| app_log columns hold (AC5) | same | **`…::test_db_buffer_levels_unchanged_when_on_railway`** + **`TestAst979DebugLevelPersistence`** |

**Broken / obsolete this pass:** bible console note said “stdout/stderr” plain only — revised for Railway JSON branch. Prior **`TestConsoleFormat`** / AST-979 DB assertions still hold (plain formatter + message-only DB).

**Integration:** none — no existing `tests/integration/` scenario asserts console transport.

### AST-1988 · AST-1987 (bug-repro — Railway JSON ids)

**Tests landed under gap sibling AST-1991.** `_RailwayJsonFormatter.format` adds top-level `batch_id` / `candidate_id` from `log_batch_id` / `log_candidate_id` when truthy; unset or `""` leaves the batch-less line byte-identical to the AST-1778 shape (omit, never null). Opener set/clear pairing lives in [`logging_batch.md`](logging_batch.md) § AST-1988.

| Area | Source | Component tests |
| --- | --- | --- |
| Both ids set → whole-dict equality | `src/utils/logging.py` | **`TestAst1988RailwayJsonIds::test_formatter_adds_batch_and_candidate_when_set`** (**bug-repro**) |
| Batch only → no `candidate_id` key | same | **`…::test_formatter_batch_only_omits_candidate`** |
| Both `None` → exact pre-fix string | same | **`…::test_formatter_unset_is_byte_identical`** |
| Both `""` → exact pre-fix string | same | **`…::test_formatter_blank_ids_omitted`** |
| On-Railway emit through `get_logger` carries ids | same | **`…::test_on_railway_emit_carries_ids`** |

**Broken / obsolete:** none — `TestAst1778RailwayConsoleTransport` asserts by key with the contextvars unset.

**Integration:** none.

### AST-2078 · AST-2074 (gap sibling AST-2079 — gunicorn.access quiet filter)

**Tests landed under gap sibling AST-2079.** Logger-level `_QuietAccessFilter` on `gunicorn.access` drops records whose atom `U` (gunicorn's single Mapping log arg) is in `RAILWAY_CONFIG["access_log_quiet_paths"]` (default `("/api/deploy_status",)`, exact path, any status); non-Mapping args pass. Attached once in `get_logger` (`_quiet_access_filter_attached`); root level, root handlers and product loggers untouched. Records are hand-built with a plain dict — no gunicorn import. Tests never reset the attach-once flag (process-global logger) and check `Logger.filter` by truthiness (3.12+ returns the record). Red on pre-fix `39bbf7afd` / `origin/dev` `267a19496`: rows 1, 3, 5.

| Area | Source | Component tests |
| --- | --- | --- |
| Poll path record dropped | `src/utils/logging.py` | **`TestAst2078GunicornAccessQuietFilter::test_deploy_status_access_record_dropped`** (**bug-repro**) |
| Other path kept | same | **`…::test_other_access_record_kept`** |
| Quiet list read from config | `src/utils/logging.py`, `src/utils/config.py` | **`…::test_quiet_paths_read_from_railway_config`** |
| Non-Mapping args kept | `src/utils/logging.py` | **`…::test_non_mapping_args_kept`** |
| Attached exactly once | same | **`…::test_filter_attached_once`** |
| Product INFO / root level / root handlers unaffected | same | **`…::test_product_info_and_root_unaffected`** |

**Broken / obsolete:** none.

**Integration:** none — no integration scenario runs gunicorn.

## QA test manifest

1. Railway level map: `tests/component/utils/test_debug_logging.py::TestAst1778RailwayConsoleTransport::test_railway_json_formatter_maps_levels`
2. stderr → stdout: `tests/component/utils/test_debug_logging.py::TestAst1778RailwayConsoleTransport::test_ensure_repoints_stderr_handler_to_stdout`
3. Formatter env branch: `tests/component/utils/test_debug_logging.py::TestAst1778RailwayConsoleTransport::test_apply_formatter_switches_on_railway_env`
4. Off-Railway plain: `tests/component/utils/test_debug_logging.py::TestAst1778RailwayConsoleTransport::test_off_railway_emit_is_plain_stdout_shape`
5. On-Railway JSON warn: `tests/component/utils/test_debug_logging.py::TestAst1778RailwayConsoleTransport::test_on_railway_emit_is_json_with_level`
6. DB hold on Railway: `tests/component/utils/test_debug_logging.py::TestAst1778RailwayConsoleTransport::test_db_buffer_levels_unchanged_when_on_railway`
7. Plain formatter regression: `tests/component/utils/test_debug_logging.py::TestConsoleFormat`
8. DEBUG persistence regression: `tests/component/utils/test_debug_logging.py::TestAst979DebugLevelPersistence`
9. Batch summary regression: `tests/component/utils/test_logging_batch.py`
10. AC6 grep gate (docs-acceptance style — no new raw `logging.getLogger` / `basicConfig` under `src/` outside `utils/logging.py`):

```bash
rg -n 'logging\.getLogger|basicConfig' src/ --glob '!**/utils/logging.py'
```

(Glob fixed in AST-2079 — `!utils/logging.py` did not exclude `src/utils/logging.py`.) Expect no new product emit paths from this tip vs `origin/dev` (transport-only in `src/utils/logging.py`).

11. AST-1988 Railway JSON ids (bug-repro #1): `tests/component/utils/test_debug_logging.py::TestAst1988RailwayJsonIds`
12. AST-2078 gunicorn.access quiet filter (bug-repro): `tests/component/utils/test_debug_logging.py::TestAst2078GunicornAccessQuietFilter`

```bash
.venv/bin/python -m pytest \
  tests/component/utils/test_debug_logging.py::TestAst1778RailwayConsoleTransport \
  tests/component/utils/test_debug_logging.py::TestConsoleFormat \
  tests/component/utils/test_debug_logging.py::TestAst979DebugLevelPersistence \
  tests/component/utils/test_debug_logging.py::TestAst1988RailwayJsonIds \
  tests/component/utils/test_debug_logging.py::TestAst2078GunicornAccessQuietFilter \
  tests/component/utils/test_logging_batch.py \
  -q
```

**Pass criterion:** pytest green on items 1–9, 11, 12 + AC6 grep clean — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):** fill after `merge-tests` —
- `docs/test-bible/utils/debug_logging.md`
