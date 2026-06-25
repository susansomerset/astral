# Record Landed Parent (prep-uat)

**Test module:** `tests/component/scripts/test_record_landed_parent.py`

## Coverage map

| Source | Test file | Branch lock |
| --- | --- | --- |
| `scripts/git/record-landed-parent.sh` | `tests/component/scripts/test_record_landed_parent.py` | no |
| `scripts/git/prep-uat-land.sh` (wiring) | static text guard in same module | no |
| `scripts/git/merge-parent.sh` | must **not** call record helper | static guard in same module |

**Existing coverage (no rerun required for AST-683 manifest):** `scripts/append_merge_ticket_log.py` and `src/utils/merge_ticket_log.py` — see `utils/merge_ticket_log.md` (AST-681).

---

### AST-683 / AST-693

After successful **`prep-uat-land.sh`** ftr land push, **`record-landed-parent.sh`** appends the parent epic id via AST-681 CLI, commits `data/merge_ticket_log.json`, and pushes `dev`. **Re-prep-uat** of the same parent updates **`recorded_at`** only (no duplicate row). **`merge-parent.sh` / finish-up** does **not** record — Susan needs the deploy env label during UAT, not after ship.

| Behavior | Tests |
| --- | --- |
| Append + commit in temp repo | `TestRecordLandedParent::test_record_landed_parent_appends_and_commits` |
| Missing append CLI → `BLOCKED` | `TestRecordLandedParent::test_record_landed_parent_missing_append_script_blocks` |
| `prep-uat-land.sh` invokes helper after push | `TestPrepUatLandShell::test_prep_uat_land_shell_wires_record_helper_after_push` |
| `merge-parent.sh` does not invoke helper | `TestMergeParentShell::test_merge_parent_shell_does_not_record_merge_ticket_log` |
| Same ticket id → timestamp update, no duplicate | `TestAppendMergeTicketLog::test_append_same_id_updates_timestamp_no_duplicate` |

---

### AST-800

Prep-uat **`record-landed-parent.sh`** invokes **`scripts/rebuild_merge_ticket_log.py`** (full log rebuild) — replaces append-only path (AST-683). See **`dev/record_landed_parent.md`**.

| Behavior | Tests |
| --- | --- |
| Shell wires rebuild, not append | `TestRecordLandedParentShell::test_record_landed_parent_wires_rebuild_not_append` |
| Rebuild stub + commit in temp repo | `TestRecordLandedParent::test_record_landed_parent_rebuilds_and_commits` |
| Missing rebuild CLI → `BLOCKED` | `TestRecordLandedParent::test_record_landed_parent_missing_rebuild_script_blocks` |

**Manifest pytest gate:**

```bash
.venv/bin/python -m pytest \
  tests/component/external/test_linear.py \
  tests/component/core/test_deploy_status.py \
  tests/component/scripts/test_record_landed_parent.py \
  -q
```
