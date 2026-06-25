# AST-472 — Strip spaces, hyphens and colons from encoded agent responses before parsing.

<!-- linear-archive: AST-472 archived 2026-06-15 -->

## Linear archive (AST-472)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-472/strip-spaces-hyphens-and-colons-from-encoded-agent-responses-before  
**Status at archive:** Done  
**Project:** Astral Boards  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Despite our best efforts, the agents are still inserting characters to make their response more readable (fair, but annoying).  

Please insert a simple replace for the first segment (codes, grades and confidence) to replace " ", "-", or ":" in case the agent tries to be helpful.  

For example:

| 5/24/26, 2:47:10 PM | **ERROR** | src.core.agent | do_task decode failed. task_key='evaluate_jd' error=\[evaluate_jd\] unexpected trailing content in grades-only line: '000|DT A5|GC B4|RT A5|RS B4|SA A5|CS A5|ET A5|JD A4' |
| -- | -- | -- | -- |
| 5/24/26, 2:47:10 PM | **INFO** | src.core.consult | \[DEBUG\] ========== evaluate_jd_batch END ========== |
| 5/24/26, 2:47:10 PM | **INFO** | src.external.anthropic | \[DEBUG\] send_to_anthropic('evaluate_jd'): 1.9s | stop_reason=end_turn |
| 5/24/26, 2:47:10 PM | **INFO** | src.external.anthropic | \[DEBUG\] tokens: fresh=4750 cache_read=0 cache_write=0 output=64 |
| 5/24/26, 2:47:10 PM | **INFO** | src.core.consult | \[DEBUG\] evaluate_jd: got 1 job objects back | tokens: input=4750 cached=0 output=64 |
| 5/24/26, 2:47:10 PM | **INFO** | src.core.consult | Senior Technical Program Manager, Product -> PASSED_JD |
| 5/24/26, 2:47:10 PM | **INFO** | src.core.consult | \[DEBUG\] evaluate_jd: processed=1 passed=1 failed=0 bad_grades=0 missing=0 fabricated=0 |
| 5/24/26, 2:47:10 PM | **INFO** | src.core.consult | \[DEBUG\] ========== evaluate_jd_batch END ========== |
| 5/24/26, 2:47:10 PM | **INFO** | src.external.anthropic | \[DEBUG\] send_to_anthropic('evaluate_jd'): 1.9s | stop_reason=end_turn |
| 5/24/26, 2:47:10 PM | **INFO** | src.external.anthropic | \[DEBUG\] tokens: fresh=4460 cache_read=0 cache_write=0 output=66 |
| 5/24/26, 2:47:10 PM | **ERROR** | src.core.agent | do_task decode failed. task_key='evaluate_jd' error=\[evaluate_jd\] unexpected trailing content in grades-only line: '000|DT A5|GC A4|RT A5|RS A5|SA A4|CS A5|ET A5|JD A4' |
| 5/24/26, 2:47:10 PM | **INFO** | src.core.consult | \[DEBUG\] ========== evaluate_jd_batch END ========== |
| 5/24/26, 2:47:10 PM | **INFO** | src.external.anthropic | \[DEBUG\] send_to_anthropic('evaluate_jd'): 2.4s | stop_reason=end_turn |


Be careful not to parse out spaces and characters from meta-data returned.

I expect this to require fewer than 5 lines of code in agent.py, so let me know if I am mistaken.

### Comments

#### chuckles — 2026-05-25T04:34:52.893Z
## do-all-the-things — run complete

**Parent:** AST-472
**Children:**
- AST-483 — Normalize grades segment whitespace in agent decode — **User Testing** — Ada

### Completed path
- Dispatch (1 child → Ada), branches on origin
- plan-astral (Ada) → validate-plan **APPROVED**
- check-linear (dev inbox pass)
- build-astral (Ada → Code Complete)
- qa-astral (Betty → Tests Ready; narrow manifest)
- test-astral (Ada `[qa-handoff]` → Betty §5b cleared → Ada **Tests Passed**)
- check-linear (Betty + dev passes)
- review-astral (Radia → **Review Posted** on AST-483)
- resolve-astral (Ada → **User Testing**)
- rollup-child (sub → ftr @ **43edf0ac**)
- prep-uat: parent **User Testing** @ Susan; local **`dev`** **a533f528**; child **sub** deleted

### Stalled / needs Susan
- **prep-uat §6 full harness:** zero-arg `run_component_tests.sh` / Vitest still fail on **`origin/dev`** baseline (LOCKED_AT_100 / frontend provider) — **not** AST-472 product; narrow pytest gate for AST-483 is green on ftr.
- **prep-uat §6.5 `audit-linear`:** not run this pass — spot-check only; parent scope matches ftr composite (`agent.py` + targeted test).
- **local `dev`:** was 10 commits ahead of `origin/dev` before prep-uat; bible merge conflict resolved with ftr side for UAT rollup.
- **Radia discuss:** publish tip includes bible **§7.13y–za** for sibling tickets AST-479–482 — confirm intentional on sub branch vs split before **finish-up**.

### prep-uat
- **Success** (with harness caveat above). Manual test steps in prior comment on this ticket.

### After finish-up (Susan)
- Engineers **merge** `origin/dev` into `dev-<agent>` per **orientation-astral** merge integration line — **not** `git rebase origin/dev`.

— Chuckles

#### chuckles — 2026-05-25T04:34:43.066Z
## Manual test steps

1. Restart the app if it is already running (so `dev` picks up `src/core/agent.py`).
2. Trigger **`evaluate_jd`** (or the consult path that produced the log errors in the parent description) on a job that previously failed decode with spaced grade tokens, e.g. a grades-only line shaped like `0|DT A5|GC B4|…`.
3. Confirm logs show **no** `do_task decode failed` / `unexpected trailing content in grades-only line` for that payload.
4. Confirm decoded grades match the compact form (vectors + letter grades) and downstream consult still marks the job **PASSED_JD** when appropriate.
5. On a **`grades_meta`** line, confirm metadata fields (e.g. job title with interior spaces) are **unchanged** — normalization must not strip spaces from fragments classified as meta.

`origin/ftr/AST-472-strip-spaces-hyphens-and-colons-from-encoded-agent-responses-before-parsing` @ **43edf0ac** · local **`dev`** merged (**a533f528**). Child **`sub/AST-472/AST-483-…`** deleted from origin after rollup.

**Harness note:** Narrow pytest gate for AST-483 is green on the ftr tip; full `run_component_tests.sh` still hits unrelated Vitest / `LOCKED_AT_100` drift on `origin/dev` — use the steps above for UAT, not the zero-arg component harness.

— Chuckles

#### hedy — 2026-05-25T04:27:33.600Z
[check-linear]

- **§0a** (`/Users/susan/chuckles/astral-hedy`, `dev-hedy`): `git fetch origin` → checkout `dev-hedy` → `git merge origin/dev` — OK, already up to date with `origin/dev`. Unstaged local edit noted on `src/ui/api/api_admin.py` before this pass.
- **`AGENTS.md`:** no file at workspace `/Users/susan/chuckles/astral-hedy` (glob search).
- **§0b** (`linear-hedy`, **displayName** `hedy`): `list_issues` `query: "@Hedy Lamarr"`, `team: Team Astral`, `includeArchived: true`, `limit: 250` — **`hasNextPage: false`**, **41** issues; Astral Boards query repeated and union taken per skill. Harness sometimes rejects `list_issues(assignee: …)` JSON — workaround: mention searches plus thread spot-checks (**AST-483** reads clean).
- **§2 actionable** (not me, **`@hedy`** / directed, after latest my `[check-linear]` if any): **none** on **AST-472** / **AST-483** (**AST-483** latest is **Ada** after Betty clearance; **Tests Passed**).
- **Orchestrator:** **`assigned_issue_ids` ∅** → no publish merge into `dev-hedy`, no `test-astral` (§6).
- **§6:** **`[check-linear] blocked:`** none.

#### chuckles — 2026-05-25T04:06:41.881Z
## Dispatch — Chuckles

Dispatched 1 child ticket from the approved definition.

| Ticket | Title | Assigned to | Branch | Blocked by |
|--------|-------|-------------|--------|------------|
| AST-483 | Normalize grades segment whitespace in agent decode (Strip spaces, hyphens and colons from encoded agent responses before parsing.) | Ada | sub/AST-472/AST-483-normalize-grades-segment-whitespace-in-agent-decode | — |

Assignment rationale:
- Ada: `src/core/agent.py` decode path — agent runtime domain.
- Hedy: not assigned this dispatch.
- Katherine: not assigned this dispatch.

Susan can override any assignment by reassigning the child ticket directly.
Parent moves to In Progress. prep-uat will merge child branches and hand the parent branch to Susan when all children reach Review Posted.

**Git (authoritative — ignore Linear `gitBranchName`):**
- Parent: `origin/ftr/AST-472-strip-spaces-hyphens-and-colons-from-encoded-agent-responses-before-parsing`
- Children: `origin/sub/AST-472/AST-483-normalize-grades-segment-whitespace-in-agent-decode`

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
