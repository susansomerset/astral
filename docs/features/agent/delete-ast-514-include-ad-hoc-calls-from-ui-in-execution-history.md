# AST-514 — Include Ad Hoc calls (from UI) in Execution History

<!-- linear-archive: AST-514 archived 2026-06-15 -->

## Linear archive (AST-514)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-514/include-ad-hoc-calls-from-ui-in-execution-history  
**Status at archive:** Done  
**Project:** Astral Agent  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Operators use **Execution History** to audit every meaningful agent call: cost, status, dispatcher logs, and stored prompt/response blocks. **Task dispatch** (scheduler **Auto**, background loops, and **Scheduled Actions Run**) already appears with **plain** task names. **Other Susan-initiated UI runs** — workbench tests, artifact **Generate**, board-search craft, and similar product flows — must be equally visible and **labeled distinctly** so experiments and craft generation are not confused with dispatch traffic. This feature closes that observability gap with consistent ledger, logs, and prompt/response inspection.

## Functional scope

* **Task column prefixes** (all **dispatch** rows stay **unprefixed**):
  * `adhoc-<task_key>` — **Test** from admin **Anthropic Ad Hoc** only (workbench task selection; editable prompts).
  * `user-<task_key>` — **Product UI buttons** that trigger a **real provider call** outside the dispatch runner, including at minimum:
    * **Artifacts** **Generate / Regenerate** (candidate generate endpoints for craft and related artifact tasks).
    * **Board Searches** craft **Generate** (board-search generate endpoints).
    * **Any current or future non-dispatch UI control** that invokes the agent stack with a provider call — same recording rules when added.
  * **Plain** `task_key` — **All dispatch**: background scheduler, **Auto**, and **Scheduled Actions manual Run** (Susan confirmed: dispatch stays plain whether triggered from admin or automation).
* **Recording parity** for every in-scope `adhoc-` and `user-` call: `dispatch_ledger` row, `log_batch_id` for app logs, stored prompt/response blocks inspectable from Execution History, terminal status, and cost — same affordances as dispatch batches today.
* **Ledger visibility:** Rows appear for the relevant candidate within existing Execution History filters.
* **Provider parity:** Anthropic and DeepSeek where the UI supports both.

## Boundaries

* **Preview-only is out of scope** — assembly with **no** provider call (Ad Hoc **Preview**, read-only task prompt preview) does not create a row.
* **Dispatch unchanged** — scheduler semantics, batch locking, multi-entity counts, ledger `task_key` labeling, and **Run** / **Auto** behavior stay as today (plain task names only).
* **Forward-only labeling** — existing ledger rows keep their stored `task_key` as-is; `user-` / `adhoc-` apply to **new** runs after ship (no migration or relabel).
* **No retroactive backfill** of older runs.
* **Does not replace runner UIs** — Ad Hoc, Artifacts, and Board Searches remain where work is triggered; Execution History is audit-only.
* **Must not break** existing dispatch rows (today filter, Skip Checks, log expand, prompt modal).
* **Saving generated content to candidate artifacts** is **out of scope** — remains Artifacts **Save**; this ticket is Execution History observability only.

## Acceptance criteria

1. **Ad Hoc Test** success → row with **Task** = `adhoc-<task_key>`, logs, prompt inspection, cost, terminal success.
2. **Ad Hoc Test** failure → row with **Task** = `adhoc-<task_key>`, terminal failure (never silent).
3. **Artifacts Generate / Regenerate** success → **Task** = `user-<task_key>` with full inspectability.
4. Same paths on failure → **Task** = `user-<task_key>`, terminal failure.
5. **Board Searches** craft **Generate** success/failure → **Task** = `user-<task_key>` with same inspectability.
6. **Scheduled Actions Run** and **background dispatch** for the same task → **plain** `task_key` (no `user-` or `adhoc-` prefix), behavior unchanged.
7. **Preview-only** does not create a row.
8. Expanding in-scope `adhoc-` / `user-` rows shows logs when emitted; prompt inspection shows stored blocks for that batch.

## Dependencies and blockers

none.

## Open questions

none. (Susan 2026-05-28: **forward-only**; product UI provider calls → `user-`; workbench Test → `adhoc-`; **dispatch stays plain**.)

---

## Original brief

Right now, execution History only shows results for task-dispatch calls.  We need to add the ad hoc calls as well so we can view logs and prompt contents for those just as we do for dispatched calls.

### Comments

#### hedy — 2026-05-28T23:44:04.318Z
[check-linear]

**Session scope:** Parent **AST-514** / Astral Agent — assigned child ids **(none)**.

**§0a:** `dev-hedy` @ `/Users/susan/chuckles/astral-hedy`; `git fetch origin`, `checkout dev-hedy`, `merge origin/dev` — already up to date. Gate: **BEHIND=0**, `origin/dev` ancestor of **HEAD**.

**§0b:** `@hedy` team search (250, no status filter); Astral Agent project `@hedy` query; **14d** fallback (`updatedAt -P14D`, team-wide 250) — union is mostly historical branch-name hits, not comment @-mentions. Full threads on **AST-514**, children **AST-515** / **AST-521**, and Hedy-assignee roster children **AST-505** / **AST-506** / **AST-508** — **0** actionable comments (no `@hedy` or directed-at-Hedy replies after prior agent passes; latest parent activity is Betty **AST-521** QA manifest @ `2026-05-28T23:40`).

**§1:** Assignee-me — **AST-505**, **AST-506**, **AST-508** (User Testing); **AST-294**, **AST-479**, **AST-501**–**503** (Done). None require inbox action.

**Pipeline:** Inbox quiet; no plan/build/test/resolve from this pass. **AST-515** User Testing; **AST-521** Tests Passed (Ada → Radia/resolve track).

#### katherine — 2026-05-28T23:43:18.077Z
[check-linear]

**Inbox (parent AST-514 / Astral Agent):** `@katherine` issue search (team + Astral Agent project), fallback via recent project activity, full threads on **AST-514**, children **AST-515** / **AST-521**, and prior mention hits in session. **0** actionable comments — nothing `@katherine` or directed at Katherine needing reply or small fix after Katherine's **AST-521** `[check-linear]` @ `2026-05-28T23:34` (Betty QA manifest @ `23:40` is Ada **`test-astral`** handoff, no `@katherine`).

**§0a (`astral-kath` / `dev-kath`):** `git fetch origin`, `checkout dev-kath`, `merge origin/dev` — **merge-clean** (`BEHIND=0`, `origin/dev` ancestor of `HEAD`).

**§1:** `assignee = me` MCP query errored this pass; orchestrator assigned ids **(none)** — no Katherine-assignee tickets in Astral Agent scope.

**Session scope:** Idle — no publish merge or pipeline skills from this pass. **AST-521** **Tests Passed** (Ada); **AST-515** **User Testing** (Ada).

#### ada — 2026-05-28T23:43:13.178Z
[check-linear]

**Session scope:** Parent **AST-514** / Astral Agent — assigned child ids **(none)**.

**§0a:** `dev-ada` @ `/Users/susan/chuckles/astral-ada`; `git fetch origin`, `checkout dev-ada`, `merge origin/dev` — already up to date. Gate: **BEHIND=0**, `origin/dev` ancestor of **HEAD**.

**§0b:** `@ada` issue search (team + Astral Agent project); assignee **Ada Lovelace** union. Full threads on **AST-514**, children **AST-515** / **AST-521**, and other @ada / assignee hits — **0** actionable comments (nothing `@ada` or directed at Ada needing reply or small fix after Ada’s prior `[check-linear]` on **AST-521** @ `2026-05-28T23:35` and **AST-520** @ `23:17`). Betty’s **AST-521** QA manifest @ `23:40` is pipeline handoff, not inbox work.

**Pipeline:** Inbox quiet; no `plan-astral` / `build-astral` / `test-astral` / `resolve-astral` from this pass. **AST-521** is **Tests Passed** (assignee Ada); **AST-515** **User Testing**; parent still **In Progress** until **AST-521** lands.

#### betty — 2026-05-28T23:43:09.327Z
[check-linear]

**Session scope:** Parent **AST-514** / Astral Agent — assigned child ids **AST-515**, **AST-521**.

**§0a:** `dev-betty` @ `/Users/susan/chuckles/astral-betty`; `git fetch origin`, `checkout dev-betty`, `merge origin/dev` — already up to date. Gate: **BEHIND=0**, `origin/dev` ancestor of **HEAD**.

**§0b:** `@betty` issue search (team + Astral Agent project); **14d** Team Astral activity scan — union is mostly historical `betty/ast-*` branch-name hits, not comment @-mentions. Full threads on **AST-514**, **AST-515**, **AST-521** — **0** actionable comments (no `@betty` or directed-at-Betty replies after prior agent passes).

**§1:** `assignee = me` MCP query errored this pass; no Betty-assignee tickets identified in session project scan.

**§5b:** **Tests Ready** — team-wide and Astral Agent project: **0** issues. Assigned **AST-515** / **AST-521** scanned: neither is **Tests Ready**; latest comments are Radia review (**515**) and Betty QA manifest (**521**) — no **`[qa-handoff]`** to clear.

**Pipeline:** Inbox quiet; no manifest/test/bible work. **AST-515** **User Testing** (Ada); **AST-521** **Tests Passed** (Ada → **`review-astral`**).

#### betty — 2026-05-28T23:34:57.029Z
[check-linear]

**Session scope:** Parent **AST-514** / Astral Agent — assigned child ids **(none)**.

**§0a:** `dev-betty` @ `/Users/susan/chuckles/astral-betty`; `git fetch origin`, `checkout dev-betty`, `merge origin/dev` — already up to date. Gate: **BEHIND=0**, `origin/dev` ancestor of **HEAD**.

**§0b:** `@betty` issue search (team + Astral Agent project); **14d** fallback via recent Team Astral activity. Union is mostly historical branch-name hits; full threads on **AST-514**, **AST-515**, **AST-521**, **AST-477** — **0** actionable comments (no `@betty` or directed-at-Betty replies after prior agent passes; latest **AST-477** activity is Chuckles `@susan` rollup-blocked note).

**§1:** `assignee = me` MCP query errored this pass; no Betty-assignee tickets identified in Astral Agent project scan.

**§5b:** **Tests Ready** — team-wide and Astral Agent project: **0** issues. No latest-comment **`[qa-handoff]`** to clear.

**Pipeline:** Inbox quiet; no manifest/test/bible work. **AST-521** is **Plan Approved** (Ada → build); publish ref noted for future **qa-astral** when **Code Complete**.

#### chuckles — 2026-05-28T23:30:57.477Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-514 (parent) | `ftr/AST-514-include-ad-hoc-calls-from-ui-in-execution-history` |
| AST-515 (adhoc — User Testing) | `sub/AST-514/AST-515-ad-hoc-workbench-test-runs-in-execution-history` (merged to ftr) |
| AST-521 (user- — Todo) | `sub/AST-514/AST-521-product-ui-user-prefix-in-execution-history` |

Follow-on dispatch for **`user-`** scope. **AST-515** remains on ftr @ `40a54c69`.

— Chuckles

#### chuckles — 2026-05-28T23:21:35.515Z
@susan Definition updated for **`user-`** UI runs (Artifacts Generate, Board Search craft generate) alongside **`adhoc-`** (AST-515). Parent is **not** UAT-complete until the follow-on child lands.

1. **Forward-only vs relabel** — keep existing plain `craft_*` ledger rows as-is, or one-time migration to `user-<task_key>`?
2. **Other UI runners** — any buttons beyond Ad Hoc Test, Artifacts Generate, Board Search generate, and scheduler Run that should get **`user-`**?

— Chuckles

#### chuckles — 2026-05-28T22:20:58.589Z
## Manual test steps

1. Restart the app on local **`dev`** if it is already running.
2. Select a candidate with a timezone set (Execution History defaults to today in that TZ).
3. Open **Anthropic Ad Hoc** → choose task **`evaluate_jd`** (or another task), pick an entity, run **Test** (real provider call).
4. Open **Execution History** → confirm a new row with **Task** = `adhoc-evaluate_jd` (or matching `adhoc-<task_key>`), terminal success status, cost if billed, counts consistent with a single run (1 processed / 1 pass or fail as appropriate).
5. Expand that row → confirm log lines appear when the run logged during the call.
6. Click the batch id / prompt inspection → confirm SYSTEM / cache / user / live / RESPONSE blocks are populated.
7. Run **Preview** only on the same workbench setup → confirm **no** new Execution History row.
8. Trigger a failed **Test** (e.g. bad key or forced failure) → confirm a row with `adhoc-<task_key>` and **FAILED** status (not missing).
9. Open an older **dispatch** row → confirm **Task** has no `adhoc-` prefix; expand logs and prompt inspection still work.

`origin/ftr/AST-514-include-ad-hoc-calls-from-ui-in-execution-history` @ `40a54c69` · local **`dev`** merged (prep-uat §8). Child **`sub/AST-514/AST-515-…`** deleted on origin.

Reset local dev to central: `git fetch origin && git reset --hard origin/dev`

— Chuckles

#### katherine — 2026-05-28T22:01:19.286Z
[check-linear]

**Inbox (parent AST-514 / Astral Agent):** Scanned `@katherine` issue search (team + project), full threads on **AST-514**, child **AST-515**, and Katherine-assignee / recent mention candidates (**AST-513**, **AST-504**, **AST-481**). **0** actionable comments — nothing `@katherine` or directed at Katherine needing a reply or small fix after Katherine’s **AST-513** `[check-linear]` @ `2026-05-28T21:10`.

**§0a (`astral-kath` / `dev-kath`):** `git fetch origin`, `checkout dev-kath`, `merge origin/dev` — **merge-clean** (`BEHIND=0`, `origin/dev` ancestor of `HEAD`). Prior inbox pass reported merge conflicts; **not** reproduced this run.

**Session scope:** **Your assigned issue ids: (none)** — no ticket-specific publish merge or pipeline work from this pass. **AST-515** is **Plan Approved**, assignee **Ada** (`origin/sub/AST-514/AST-515-ad-hoc-workbench-test-runs-in-execution-history`); parent **AST-514** assignee Chuckles — Katherine pipeline queue idle per happy path.

#### hedy — 2026-05-28T22:01:09.988Z
[check-linear]

**Inbox (parent AST-514 / Astral Agent):** `@hedy` issue search (team + project), fallback scan (`updatedAt -P14D`), full threads on **AST-514**, child **AST-515**, and Hedy-assignee roster children (**AST-505**–**508**). **0** actionable comments — nothing `@hedy` or directed at Hedy needing reply or small fix after prior agent posts.

**§0a:** `dev-hedy` @ `/Users/susan/chuckles/astral-hedy`; merged `origin/dev` cleanly — `BEHIND=0`, `merge-clean: yes`.

**Session scope:** Orchestrator assigned issue ids **(none)** — no `plan-astral` / `build-astral` / `test-astral` / `resolve-astral` from this pass. **AST-515** is **Plan Approved**, assignee **Ada** (publish ref `origin/sub/AST-514/AST-515-ad-hoc-workbench-test-runs-in-execution-history`).

#### chuckles — 2026-05-28T21:57:41.275Z
## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
|--------|------------|
| AST-514 (parent) | ftr/AST-514-include-ad-hoc-calls-from-ui-in-execution-history |
| AST-515 | sub/AST-514/AST-515-ad-hoc-workbench-test-runs-in-execution-history |

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
