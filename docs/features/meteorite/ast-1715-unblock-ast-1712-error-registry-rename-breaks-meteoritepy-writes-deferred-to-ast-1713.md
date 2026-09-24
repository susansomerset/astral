# AST-1715 — Unblock AST-1712: ERROR registry rename breaks meteorite.py writes deferred to AST-1713

<!-- linear-archive: AST-1715 archived 2026-09-24 -->

## Linear archive (AST-1715)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1715/unblock-ast-1712-error-registry-rename-breaks-meteoritepy-writes  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Execution plan

Susan chose widen [AST-1712](https://linear.app/astralcareermatch/issue/AST-1712/mailbox-key-and-classify-state-map-rework-meteorite-email). This task does the paperwork and the plan-doc edit only. It does not edit `src/core/meteorite.py`, does not edit `tests/`, does not take [AST-1712](https://linear.app/astralcareermatch/issue/AST-1712/mailbox-key-and-classify-state-map-rework-meteorite-email) off Ada, and does not change [AST-1711](https://linear.app/astralcareermatch/issue/AST-1711/rework-meteorite-email).

1. In the epic worktree `/home/susan/astral-AST-1711` (already on `sub/AST-1711/AST-1712-mailbox-key-and-classify-state-map`), amend `docs/features/meteorite/ast-1712-mailbox-key-and-classify-state-map.md` only. Add one stage: retarget the existing failure writes in `src/core/meteorite.py` from `ERROR` to `SCRAPE_ERROR`. Delete the out-of-scope line that says do not edit `meteorite.py`. Commit that doc on the same sub ref and push `origin/sub/AST-1711/AST-1712-mailbox-key-and-classify-state-map`. No product code, no `tests/`, no `ftr/` move.
2. Writes to retarget (membership check in `update_meteorite` — state must be a `METEORITE_STATES` key; no prior check, so `SCRAPE_ERROR` from `NEW` or `READY` is legal):
   * `run_stage_meteorite`: `missing classify_outcome`, `skip outcome on row`, `missing link`, `missing content`, `missing breadcrumb link`, `unhandled classify_outcome`
   * `run_scrape_meteorite`: `missing link`, and the fallback `status_map.get(page_status, "ERROR")`
   * `run_land_meteorite`: empty-content `READY` → `missing content` (empty `BOT_BLOCKED` still skips), and land-failed
   * Leave log lines such as `This row is ERROR`. Those are not state writes.
3. Update the [AST-1712](https://linear.app/astralcareermatch/issue/AST-1712/mailbox-key-and-classify-state-map-rework-meteorite-email) Linear description to match: `src/core/meteorite.py` is in scope for that literal retarget only. Add acceptance: `rg -n 'state="ERROR"' src/core/meteorite.py` prints nothing, and the scrape fallback default is not `"ERROR"`. Registry rename and mailbox key stay as already built. Then set [AST-1712](https://linear.app/astralcareermatch/issue/AST-1712/mailbox-key-and-classify-state-map-rework-meteorite-email) to **Plan Approved**. Assignee stays Ada. Do not spawn Joan — she already approved the registry slice; this add is Susan's widen, not a new plan round.
4. Update the [AST-1713](https://linear.app/astralcareermatch/issue/AST-1713/stage-meteorite-saves-the-ruth-row-rework-meteorite-email) description: remove the clause that stage/scrape/land failure writes change `ERROR` to `SCRAPE_ERROR`, and remove the acceptance criterion that is only `rg state="ERROR"` on `meteorite.py`. Leave the rest (Ruth save, `NOT_A_JOB` / `NEW_EMAIL_ERROR`, consult removal, insert state). State stays Todo. Assignee stays Hedy. She still replaces **stage** outcomes with `SCRAPE_LINK` / `READY` / `NOT_A_JOB` / `NEW_EMAIL_ERROR`. She does not retarget scrape or land `SCRAPE_ERROR` writes again.
5. Do not change [AST-1711](https://linear.app/astralcareermatch/issue/AST-1711/rework-meteorite-email) (stays In Progress, Chuckles). Do not reassign [AST-1712](https://linear.app/astralcareermatch/issue/AST-1712/mailbox-key-and-classify-state-map-rework-meteorite-email). Do not run datt from this task. Ada's next Plan Approved pass on the parent wave does the `meteorite.py` edit.

## Done when

* The [AST-1712](https://linear.app/astralcareermatch/issue/AST-1712/mailbox-key-and-classify-state-map-rework-meteorite-email) plan doc on `origin/sub/AST-1711/AST-1712-mailbox-key-and-classify-state-map` names the `meteorite.py` retarget and no longer forbids editing that file.
* [AST-1712](https://linear.app/astralcareermatch/issue/AST-1712/mailbox-key-and-classify-state-map-rework-meteorite-email) description matches that stage, status is Plan Approved, assignee is Ada.
* [AST-1713](https://linear.app/astralcareermatch/issue/AST-1713/stage-meteorite-saves-the-ruth-row-rework-meteorite-email) no longer owns the `ERROR` → `SCRAPE_ERROR` retarget; status Todo, assignee Hedy.
* [AST-1711](https://linear.app/astralcareermatch/issue/AST-1711/rework-meteorite-email) is still In Progress, assignee Chuckles.

## Risks / open questions

* `tests/component/core/test_meteorite.py::TestAst1703EmailBreadcrumb::test_stage_email_text_blank_link_errors` expects `ERROR` and currently gets `NEW` because the rejected `ERROR` write leaves the inserted row at `NEW`. After Ada writes `SCRAPE_ERROR`, that assertion fails the other way. Same for the other meteorite tests that hardcode `state == "ERROR"` on these paths. Product slice does not edit `tests/`. Ada must not put `ERROR` back to satisfy them. Betty flips those assertions on the next qa of [AST-1712](https://linear.app/astralcareermatch/issue/AST-1712/mailbox-key-and-classify-state-map-rework-meteorite-email).
* none on the decision — widen is already chosen.

---

## Original brief

Betty found the registry rename of scrape-failure ERROR to SCRAPE_ERROR in METEORITE_STATES is not shippable alone. update_meteorite rejects states not in that registry, and src/core/meteorite.py still writes state="ERROR". Those writes are AST-1713's scope, and [AST-1713](https://linear.app/astralcareermatch/issue/AST-1713/stage-meteorite-saves-the-ruth-row-rework-meteorite-email) is blocked by [AST-1712](https://linear.app/astralcareermatch/issue/AST-1712/mailbox-key-and-classify-state-map-rework-meteorite-email), so they cannot land first. Writer test tests/component/core/test_meteorite.py::TestAst1703EmailBreadcrumb::test_stage_email_text_blank_link_errors expects ERROR and gets NEW. Same break on the other state="ERROR" paths in stage, scrape, and land.

Need one answer:

* Widen [AST-1712](https://linear.app/astralcareermatch/issue/AST-1712/mailbox-key-and-classify-state-map-rework-meteorite-email) so this slice also retargets those [meteorite.py](<http://meteorite.py>) writes from ERROR to SCRAPE_ERROR, and [AST-1713](https://linear.app/astralcareermatch/issue/AST-1713/stage-meteorite-saves-the-ruth-row-rework-meteorite-email) does not redo them. Or
* Keep the writes on [AST-1713](https://linear.app/astralcareermatch/issue/AST-1713/stage-meteorite-saves-the-ruth-row-rework-meteorite-email), and move the ERROR to SCRAPE_ERROR registry rename onto [AST-1713](https://linear.app/astralcareermatch/issue/AST-1713/stage-meteorite-saves-the-ruth-row-rework-meteorite-email), so [AST-1712](https://linear.app/astralcareermatch/issue/AST-1712/mailbox-key-and-classify-state-map-rework-meteorite-email) only adds the new states and the mailbox key.

Reply here or attach the file. The agents will place it in the repo; you do not need to push. Move this to Done when provided.

Susan's answer: widen [AST-1712](https://linear.app/astralcareermatch/issue/AST-1712/mailbox-key-and-classify-state-map-rework-meteorite-email) to resolve the change.  @chuckles take it from here!

Neither [AST-1712](https://linear.app/astralcareermatch/issue/AST-1712/mailbox-key-and-classify-state-map-rework-meteorite-email) nor [AST-1711](https://linear.app/astralcareermatch/issue/AST-1711/rework-meteorite-email) is assigned to you. [AST-1712](https://linear.app/astralcareermatch/issue/AST-1712/mailbox-key-and-classify-state-map-rework-meteorite-email) stays with Ada. [AST-1711](https://linear.app/astralcareermatch/issue/AST-1711/rework-meteorite-email) stays In Progress with Chuckles.

### Comments

#### chuckles — 2026-09-19T22:10:50.470Z
[check-linear] answered — Done still blocked the parent and this slice. Those two relations are removed.

#### susan — 2026-09-19T22:09:03.507Z
@chuckles WHY IS THIS STOPPING THE PROGRESS?

#### chuckles — 2026-09-19T20:27:09.487Z
[check-linear] Discussion — execution plan is on this ticket; Todo + Chuckles runs the widen (@susan)

#### susan — 2026-09-19T20:24:44.452Z
@chuckles Susan's answer: widen [AST-1712](https://linear.app/astralcareermatch/issue/AST-1712/mailbox-key-and-classify-state-map-rework-meteorite-email) to resolve the change. @chuckles take it from here!

---

_Implementation detail may live in git history on `origin/dev`._
