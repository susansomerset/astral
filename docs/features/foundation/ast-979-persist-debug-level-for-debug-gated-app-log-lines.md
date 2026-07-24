# AST-979 — Persist DEBUG level for debug-gated app_log lines

**Linear:** [AST-979 — Persist DEBUG level for debug-gated app_log lines](https://linear.app/astralcareermatch/issue/AST-979/persist-debug-level-for-debug-gated-app-log-lines-add-level-debug-to)  
**Parent:** [AST-976 — Add level "DEBUG" to app_log table](https://linear.app/astralcareermatch/issue/AST-976/add-level-debug-to-app_log-table)  
**Publish ref:** `origin/sub/AST-976/AST-979-persist-debug-level-for-debug-gated-app-log-lines`

Debug-gated backend emissions (`debug_index` / `debug_detail` / `debug_detail_block` / `test`) currently call `Logger.info`, so `_DatabaseLogHandler` stores them as `level=INFO` in `app_log` and they are indistinguishable from ordinary production INFO. This ticket corrects **stored severity only**: when `debug_flag=True`, those helpers emit at Python `DEBUG` and the DB handler persists `level=DEBUG`; when `debug_flag=False` they still emit nothing; ordinary `info` / `warning` / `error` paths and the late-import `add_log_entry` flush stay unchanged. Execution History Level-list UI is **AST-980** (out of scope).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/logging.py` | Emit debug-gated helpers at DEBUG; raise named-logger level when `debug_flag=True`; set `_DatabaseLogHandler` level to DEBUG so records are not dropped; update docstrings that still say INFO | utils |

No other files. Do **not** edit `src/data/database.py` (`add_log_entry` already accepts free-text `level`; `app_log.level` is `TEXT`). Do **not** edit Execution History UI (`AdminPerformanceMonitor.tsx` — AST-980). Do **not** mass-migrate grandfathered `logger.info("[DEBUG] …")` call sites. Do **not** change AST-538 message shape (`format_debug_index_header`, `DEBUG_DETAIL_PREFIX`, truncation).

## Stage 1: Persist debug-gated lines as DEBUG

**Done when:** With a `_PrefixedLogger` that has `debug_flag=True`, calling `debug_index` / `debug_detail` / `debug_detail_block` / `test` produces buffered handler entries whose `level` is the string `DEBUG` (and after `flush_log_buffer`, matching `app_log` rows). The same calls with `debug_flag=False` produce no entries. A plain `logger.info("…")` still buffers/persists as `INFO`. WARNING/ERROR unchanged. Late import of `add_log_entry` inside `_flush_buffer` is preserved.

1. In `src/utils/logging.py`, in `_PrefixedLogger.set_debug_flag`, after assigning `self._debug_flag = flag`:
   - When `flag` is `True`, call `self._logger.setLevel(logging.DEBUG)` so `Logger.debug` / `isEnabledFor(DEBUG)` succeed on that named logger (root stays at INFO via existing `basicConfig` — do **not** raise the root logger to DEBUG; that would flood third-party `httpcore` / similar DEBUG).
   - When `flag` is `False`, if `self._logger.level == logging.DEBUG`, call `self._logger.setLevel(logging.INFO)` so a later non-debug use of the same named logger does not leak bare `.debug()` emissions into `app_log`.
2. In `_PrefixedLogger.__init__`, after storing `self._logger`, call `self.set_debug_flag(debug_flag)` (instead of only assigning `self._debug_flag`) so `get_logger(..., debug_flag=True)` applies the same level rule as an explicit `set_debug_flag(True)`.
3. In `_PrefixedLogger.test`, replace `self._logger.info(f"[ ~ ] {message}")` with `self._logger.debug(f"[ ~ ] {message}")` (keep the `[ ~ ]` prefix and the `if self._debug_flag:` gate).
4. In `_PrefixedLogger.debug_index`, replace `self._logger.info(format_debug_index_header(...))` with `self._logger.debug(format_debug_index_header(...))`. Keep the `if not self._debug_flag: return` gate and the keyword-only header args. Update the method docstring from “at INFO” to “at DEBUG”.
5. In `_PrefixedLogger.debug_detail`, replace `self._logger.info(f"{DEBUG_DETAIL_PREFIX}{message}")` with `self._logger.debug(f"{DEBUG_DETAIL_PREFIX}{message}")`. Keep the gate and `DEBUG_DETAIL_PREFIX`. Update the docstring if it implies INFO.
6. Leave `debug_detail_block` as a loop over `debug_detail` (no separate emit). Leave `_PrefixedLogger.debug` as-is (already uses `Logger.debug` with `[ ~ ]`).
7. In `get_logger`, change `_db_handler_instance.setLevel(logging.INFO)` to `_db_handler_instance.setLevel(logging.DEBUG)` so DEBUG records reach `emit` → buffer → `add_log_entry`. Do **not** move or remove the late import of `add_log_entry` inside `_flush_buffer`. Do **not** change `_FLUSH_THRESHOLD`, buffer shape (`level` / `logger_name` / `message` / `batch_id`), stderr failure paths, or `flush_log_buffer`.
8. Update any adjacent comments/docstrings in this file that claim debug-contract helpers log at INFO (module docstring usage block may stay as call-shape examples; method docs must match DEBUG).

⚠️ **Decision:** Fix severity at the `_PrefixedLogger` emit site + handler threshold only — not by remapping message text in `_DatabaseLogHandler`, not by sniffing `DEBUG_DETAIL_PREFIX` / `[ ~ ]`, and not by changing `add_log_entry`. Handler already stores `record.levelname`; once helpers use `Logger.debug`, persisted level is `DEBUG` with no schema change.

⚠️ **Decision:** Include `.test()` in the INFO→DEBUG switch. It is the same `debug_flag` gate as the AST-538 contract helpers and today also pollutes INFO in `app_log`; leaving it on INFO would leave a second debug-gated path mis-labeled. Grandfathered `logger.info("[DEBUG] …")` call sites outside this file stay untouched per parent boundaries.

⚠️ **Decision:** Raise **only** the named module logger when `debug_flag=True`; keep root `basicConfig(level=logging.INFO)`. Propagation still delivers DEBUG records to the root-attached `_DatabaseLogHandler` and stdout handler without enabling third-party DEBUG.

## Self-Assessment

**Scope:** `Single-Component` — one utils module (`src/utils/logging.py`); no data schema, no UI, no call-site backfill.

**Conf:** `high` — root cause is local (helpers call `info`; handler `setLevel(INFO)`); `add_log_entry` already accepts `level` as free text; AST-538 gating and late-import flush path stay intact.

**Risk:** `Medium` — logging is process-wide; wrong root-level change would flood logs, and failing to lower the handler would drop DEBUG entirely (silent AC miss). Mitigated by explicit “do not raise root” and handler `setLevel(DEBUG)` steps.

## Code rules self-review

- **§1.3 DRY:** Single emit-site change on existing helpers; no duplicated severity mapping in the handler.
- **§1.5 / late import:** `_flush_buffer` late import of `add_log_entry` unchanged; still the only utils→data path.
- **§1.5.1 debug contract:** Gating, header shape, `|` detail prefix, and truncation unchanged; only Python/storage severity corrected.
- **§2.1 config:** No new config keys (severity is logging stdlib, not TASK_CONFIG).
- **§2.4 / §2.6:** N/A (no batch claim / state machine).
- **§3.3 imports:** No new cross-layer imports.
- **§3.5 naming:** Existing method names retained.
