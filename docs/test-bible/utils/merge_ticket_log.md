# Merge Ticket Log

**Test module:** `tests/component/utils/test_merge_ticket_log.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `src/utils/merge_ticket_log.py` | `tests/component/utils/test_merge_ticket_log.py` | no |
| `scripts/append_merge_ticket_log.py` | CLI exercised indirectly via `append_merge_ticket_log` | no |

---

### AST-681

Prep-uat records parent ids in `data/merge_ticket_log.json`; sole writer is `append_merge_ticket_log` (CLI) via `record-landed-parent.sh`. Same parent re-landed updates `recorded_at` only. Read path returns oldest-first file order; deploy status reverses for API. Shell wiring: `dev/record_landed_parent.md`.

| Behavior | Tests |
| --- | --- |
| Missing file → `[]` | `TestReadMergeTicketLog::test_read_empty_when_missing` |
| File order preserved on read | `TestReadMergeTicketLog::test_read_returns_file_order` |
| Non-array JSON → `ValueError` | `TestReadMergeTicketLog::test_read_rejects_non_array` |
| Append normalizes id + ISO timestamp | `TestAppendMergeTicketLog::test_append_and_read_preserves_order` |
| Invalid ticket id → `ValueError` | `TestAppendMergeTicketLog::test_append_rejects_invalid_id` |
| Distinct ids accumulate | `TestAppendMergeTicketLog::test_append_never_truncates` |
| Same id → update timestamp, no duplicate | `TestAppendMergeTicketLog::test_append_same_id_updates_timestamp_no_duplicate` |

**Manifest pytest gate (AST-681):**

```bash
.venv/bin/python -m pytest tests/component/utils/test_merge_ticket_log.py -q
```
