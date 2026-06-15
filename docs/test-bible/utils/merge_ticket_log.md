# Merge Ticket Log

**Test module:** `tests/component/utils/test_merge_ticket_log.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/utils/merge_ticket_log.py` | `tests/component/utils/test_merge_ticket_log.py` | no |
| `scripts/append_merge_ticket_log.py` | CLI exercised indirectly via `append_merge_ticket_log` | no |

---

### AST-681

Append-only JSON log under `data/merge_ticket_log.json`; sole writer is `append_merge_ticket_log` (CLI) invoked by finish-up `record-landed-parent.sh` (AST-683). Read path returns oldest-first file order; deploy status reverses for API. Finish-up shell wiring: `dev/record_landed_parent.md`.

| Behavior | Tests |
| --- | --- |
| Missing file → `[]` | `TestReadMergeTicketLog::test_read_empty_when_missing` |
| File order preserved on read | `TestReadMergeTicketLog::test_read_returns_file_order` |
| Non-array JSON → `ValueError` | `TestReadMergeTicketLog::test_read_rejects_non_array` |
| Append normalizes id + ISO timestamp | `TestAppendMergeTicketLog::test_append_and_read_preserves_order` |
| Invalid ticket id → `ValueError` | `TestAppendMergeTicketLog::test_append_rejects_invalid_id` |
| Append-only — no truncation | `TestAppendMergeTicketLog::test_append_never_truncates` |

**Manifest pytest gate (AST-681):**

```bash
.venv/bin/python -m pytest tests/component/utils/test_merge_ticket_log.py -q
```
