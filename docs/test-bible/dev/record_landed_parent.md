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

After successful `merge-parent.sh` ftr land push, `record-landed-parent.sh` appends the parent epic id via AST-681 CLI, commits `data/merge_ticket_log.json`, and pushes `dev`. **AST-693** supersedes the “prep-uat unwired” note — see **AST-693** below.

| Behavior | Tests |
| --- | --- |
| Append + commit in temp repo | `TestRecordLandedParent::test_record_landed_parent_appends_and_commits` |
| Missing append CLI → `BLOCKED` | `TestRecordLandedParent::test_record_landed_parent_missing_append_script_blocks` |
| `merge-parent.sh` invokes helper | `TestMergeParentShell::test_merge_parent_shell_references_record_helper` |

**Manifest pytest gate (AST-683):**

```bash
.venv/bin/python -m pytest tests/component/scripts/test_record_landed_parent.py -q
```

---

### AST-693

**AST-675 UAT fix:** Staging showed static env label because `data/merge_ticket_log.json` on `dev` was empty — AST-691 interactivity requires non-empty `merge_tickets`. Bootstrap in-repo log (via append CLI) plus wire `prep-uat-land.sh` to call `record-landed-parent.sh` after land push (same parent-id extraction as `merge-parent.sh`). No UI/API shape changes.

| Behavior | Tests |
| --- | --- |
| `merge_tickets` reversed + empty log | existing **`test_deploy_status.py`** — **`test_merge_tickets_most_recent_first`**, **`test_merge_tickets_empty_when_log_empty`** |
| Append/read log | existing **`test_merge_ticket_log.py`** (AST-681) |
| Record helper append + commit | existing **`TestRecordLandedParent::test_record_landed_parent_appends_and_commits`** |
| `prep-uat-land.sh` invokes record helper after push | **`TestPrepUatLandShell::test_prep_uat_land_shell_wires_record_helper_after_push`** |
| Hover tooltip when API returns tickets | existing **AST-691** **`test_AdminDeployFooter.test.tsx`** rows (regression) |

**Manifest pytest gate (AST-693):**

```bash
.venv/bin/python -m pytest \
  tests/component/utils/test_deploy_status.py \
  tests/component/utils/test_merge_ticket_log.py \
  tests/component/scripts/test_record_landed_parent.py \
  -q

cd src/ui/frontend && npm run test:component -- \
  ../../../tests/component/frontend/components/test_AdminDeployFooter.test.tsx
```
