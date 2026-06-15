# Record Landed Parent (finish-up)

**Test module:** `tests/component/scripts/test_record_landed_parent.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `scripts/git/record-landed-parent.sh` | `tests/component/scripts/test_record_landed_parent.py` | no |
| `scripts/git/merge-parent.sh` (wiring) | static text guard in same module | no |

**Existing coverage (no rerun required for AST-683 manifest):** `scripts/append_merge_ticket_log.py` and `src/utils/merge_ticket_log.py` — see `utils/merge_ticket_log.md` (AST-681).

---

### AST-683

After successful `merge-parent.sh` ftr land push, `record-landed-parent.sh` appends the parent epic id via AST-681 CLI, commits `data/merge_ticket_log.json`, and pushes `dev`. `prep-uat-land.sh` must remain unwired.

| Behavior | Tests |
| --- | --- |
| Append + commit in temp repo | `TestRecordLandedParent::test_record_landed_parent_appends_and_commits` |
| Missing append CLI → `BLOCKED` | `TestRecordLandedParent::test_record_landed_parent_missing_append_script_blocks` |
| `merge-parent.sh` invokes helper | `TestMergeParentShell::test_merge_parent_shell_references_record_helper` |

**Manifest pytest gate (AST-683):**

```bash
.venv/bin/python -m pytest tests/component/scripts/test_record_landed_parent.py -q
```
