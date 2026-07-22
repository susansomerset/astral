# AST-924 — Add Plan Discuss state + transition rules

- **Linear:** [AST-924](https://linear.app/astralcareermatch/issue/AST-924/add-plan-discuss-state-transition-rules)
- **Parent:** [AST-911](https://linear.app/astralcareermatch/issue/AST-911/linear-issue-types-and-states-safe-change-mechanics-plan-discuss)
- **Publish ref:** `origin/sub/AST-911/AST-924-plan-discuss-state`
- **Summary:** Add Linear state **Plan Discuss** between Plan Ready and Plan Approved; wire enter/exit transitions, tagged 2-round-trip / Archie escalation mechanics; execute **AST-923**’s migration checklist live (v1→v2); update rollcall + touched watcher/skill gates; prove on a canary child. Does **not** invent inventory/checklist (AST-923) or plan-rubric content (AST-928).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| Linear Team Chuckles workflow | Create state named exactly `Plan Discuss` (`started`), position between Plan Ready and Plan Approved | Linear workspace |
| `~/team-chuckles/skills/rollcall/state_vocabulary.json` | Bump `version` **1→2**; insert `"Plan Discuss"` in `states` immediately after `"Plan Ready"` | team-chuckles / rollcall |
| `~/team-chuckles/skills/rollcall/watch_rules/define.json` | `state_vocabulary_version`: **2** (no Plan Discuss in exclusives) | watcher config |
| `~/team-chuckles/skills/rollcall/watch_rules/datt.json` | `state_vocabulary_version`: **2** | watcher config |
| `~/team-chuckles/skills/rollcall/watch_rules/fix.json` | `state_vocabulary_version`: **2** | watcher config |
| `~/team-chuckles/skills/rollcall/watch_rules/wrap.json` | `state_vocabulary_version`: **2** | watcher config |
| `~/team-chuckles/skills/rollcall/watch_rules/check.json` | `state_vocabulary_version`: **2**; add `"Plan Discuss"` to `linear.states` (after `"Plan Ready"`) | watcher config |
| `~/team-chuckles/skills/rollcall/watch_linear.py` | Add `"Plan Discuss"` to `_CHECK_ASSIGNEE_STATES`; remove stale `"In Review"` from that frozenset (Radia AST-923 advisory); no `_WATCHER_EXCLUSIVE` ownership of Plan Discuss | watcher runtime |
| `~/team-chuckles/skills/rollcall/rollcall_table.py` | `STATUS_SORT["Plan Discuss"]=2`, shift Plan Approved→3 … User Testing→9; `action()` maps Plan Discuss → Chuck column `validate-plan` (same as Plan Ready) | rollcall-action |
| `~/team-chuckles/skills/rollcall/SKILL.md` | Document Plan Discuss action row (`Chuck` → `valid-pl`) | skill-gate |
| `~/team-chuckles/skills/validate-plan/SKILL.md` | Gate Plan Ready **and** Plan Discuss; REVISE → Plan Discuss + tagged concern; round-cap / Archie escalate; re-validate on Plan Discuss | skill-gate |
| `~/team-chuckles/skills/plan-child/SKILL.md` | Document Plan Discuss → Todo re-plan exit; engineer reply path while status is Plan Discuss (patch plan + tagged reply; do not self-move to Plan Approved) | skill-gate |
| `~/team-chuckles/skills/build-child/SKILL.md` | Explicit: queue/status gate remains **Plan Approved** only — Plan Discuss is not buildable | skill-gate |
| `~/team-chuckles/skills/check-linear/SKILL.md` | Plan Discuss assignee threads are in inbox scope (already via check states once added); note `[plan-discuss]` engineer reply expectation | skill-gate |
| `~/team-chuckles/skills/do-all-the-things/SKILL.md` | validate-plan sweeps include **Plan Discuss** as well as Plan Ready | skill-gate |
| `~/team-chuckles/agents/handoff-table.md` | Add row: Plan Discuss → engineer persona / `engineer.sh` (same as Todo / Plan Approved) | handoff-table |
| `~/team-chuckles/skills/seed-agents-md/SKILL.md` | List Plan Discuss → engineer seed alongside Plan Approved | skill-gate |
| `~/team-chuckles/docs/linear-state-consumers.md` | Bump header vocabulary version to **2**; add Plan Discuss inventory touches; new **Plan Discuss** transition subsection; update Plan Ready / Plan Approved exit/enter lines | docs |
| `~/team-chuckles/docs/linear-state-migration-checklist.md` | Append **Live run log (AST-924)** with checklist steps checked + canary result | docs |
| `docs/ASTRAL_TEAM_WORKFLOW.md` | Insert Plan Discuss row in “Linear status → skill” table | astral docs |
| `docs/ASTRAL_CODE_RULES.md` §4.3 | Replace stale Backlog→…→In Review list with current Team Chuckles pipeline names including Plan Discuss (name-only; no state ids) | astral docs |
| `docs/features/team-chuckles/ast-924-add-plan-discuss-state-transition-rules.md` | This plan | astral docs |

**Commit homes:** tooling + skill/doc edits under **`team-chuckles`**; astral law/workflow + this plan on **`astral-AST-911/`** publish ref. Same split as AST-923.

**Out of scope:**

- Plan-rubric / statute content Joan will eventually apply (**AST-928** / **AST-916**).
- Replacing Chuckles with a Joan Linear identity / `linear-joan` MCP (**AST-910**) — until then Chuckles **is** the Joan actor for validate-plan / Plan Discuss.
- Astral product `JOB_STATES` / `COMPANY_STATES` / `src/**`.
- Inventing a second migration checklist — execute AST-923’s file as written (order fixed).

---

## Mechanical rules (binding — implement exactly)

### Actors

| Role | Who (runtime) | Notes |
|------|----------------|-------|
| **Joan** (validator) | Chuckles (`susan+chuckles@…`, `linear-chuckles` / `validate-plan`) | AST-910 will later give Joan a persona; **do not** wait on it. Comments signed `— Chuckles`. |
| **Engineer** | Ada / Hedy / Katherine | Remains Linear **assignee** through Plan Discuss. Never assign Chuckles/Joan on the child. |
| **Archie** | Susan (`susan@susansomerset.com`) | Alias only in public prose; assignee flip targets Susan. Escalate comments `@susan`. |

### Comment tags (first line of the comment body)

| Tag line | Who posts | Meaning |
|----------|-----------|---------|
| `[plan-discuss] round=<N> concern` | Joan (Chuckles) | Starts round **N** (N is 1 or 2). Body = findings. |
| `[plan-discuss] round=<N> reply` | Engineer | Completes round **N**. Body = what changed in the plan (path + short delta). |
| `[plan-discuss] escalate` | Joan (Chuckles) | Cap hit or mid-loop product escalate. Body must include `@susan` and why. |

### What counts as one round trip

1. Joan posts `[plan-discuss] round=N concern` (and status is **Plan Discuss**).
2. Engineer posts `[plan-discuss] round=N reply` for the **same N**.

That pair = **one completed round**. Cap = **2** completed rounds.

### Who moves state

| From → To | Who | When |
|-----------|-----|------|
| Plan Ready → Plan Approved | Joan (`validate-plan` APPROVED) | Unchanged happy path. |
| Plan Ready → Plan Discuss | Joan (`validate-plan` REVISE) | **Any** REVISE from Plan Ready. Post `[plan-discuss] round=1 concern` in the same pass. Engineer stays assignee. |
| Plan Ready → Plan Ready | Joan (`validate-plan` ESCALATE) | Product/architecture escalate **before** entering Plan Discuss: status stays Plan Ready; assignee → Susan; `@susan` in comment. (Unchanged ESCALATE path.) |
| Plan Discuss → Plan Approved | Joan (`validate-plan` APPROVED) | After engineer reply (or on re-check with no fix-now left). |
| Plan Discuss → Plan Discuss | Joan (`validate-plan` REVISE, completed rounds &lt; 2) | Post `[plan-discuss] round=<N+1> concern`; do **not** start round 3. |
| Plan Discuss → Plan Discuss + Archie | Joan | When Joan would open round **3**, or REVISE after **2** completed rounds, or ESCALATE during Plan Discuss: post `[plan-discuss] escalate`, assignee → Susan; **status stays Plan Discuss** until Archie resolves. |
| Plan Discuss → Todo | Joan | Verdict is re-plan (plan must be rewritten from scratch / definition mismatch). Comment states re-plan; engineer then runs `plan-child` from Todo. |
| Plan Discuss → * | Engineer | **Must not** move to Plan Approved. May only revise the plan doc + tagged reply (or ask Joan for Todo via comment if they believe re-plan is required — Joan moves Todo). |

⚠️ **Decision:** REVISE from Plan Ready **always** enters Plan Discuss (replaces the old “stay Plan Ready” REVISE path). Keeps one discuss loop and makes the 2-round cap enforceable. Pure patch-and-resubmit is still Plan Discuss with typically one round.

⚠️ **Decision:** Plan Discuss is **not** a `_WATCHER_EXCLUSIVE` owner. Inbox visibility is via `check` only. No define/datt/fix/wrap claim.

⚠️ **Decision:** Rollcall action for Plan Discuss mirrors Plan Ready (`Chuck` → `validate-plan`) so Chuckles/datt re-sweeps see the waiting validator column.

### Cap / Archie (observable)

After engineer’s `[plan-discuss] round=2 reply`, Joan’s next `validate-plan` pass may only:

- **APPROVED** → Plan Approved, or
- **escalate** → `[plan-discuss] escalate` + assignee Susan (Archie), status Plan Discuss.

Opening `round=3 concern` is **forbidden**.

---

## Stage 1: Create Linear state + pause watchers

**Done when:** Team Chuckles has a workflow state named exactly `Plan Discuss` (type `started`, position between Plan Ready and Plan Approved); tmux session `chuck` is stopped and `pgrep -af watch_linear` is empty.

1. On the chuckles host, pause watchers per checklist step 1:

```bash
tmux kill-session -t chuck 2>/dev/null || true
pgrep -af watch_linear || true   # must be empty
```

2. Create the Linear state with GraphQL (prefer `LINEAR_KEY_CURSOR` / Chuckles). Team id for Team Chuckles (`AST`) is `a453f85c-871c-4d50-8a82-cf857750a526`. Position = midpoint of current Plan Ready and Plan Approved positions (query `workflowStates` first; as of plan time Plan Ready ≈ `-1076.64`, Plan Approved ≈ `-553.13` → use approximately `-815`).

```graphql
mutation {
  workflowStateCreate(input: {
    teamId: "a453f85c-871c-4d50-8a82-cf857750a526"
    name: "Plan Discuss"
    type: started
    position: -815
  }) { success workflowState { id name type position } }
}
```

Consumers must **not** store the returned `id` — name-only law.

3. If the mutation fails with permission/auth: stop, comment on **AST-911** with `🛑 Stage 1 blocked` asking Susan to create the state in Linear UI (exact name `Plan Discuss`, type started, between Plan Ready and Plan Approved). Do not continue vocabulary bump until the name exists in `workflowStates`.

4. Commit home: no git yet (Linear-only + pause). Proceed to Stage 2 in the same build session.

---

## Stage 2: Vocabulary v2 + watcher configs/runtime

**Done when:** `state_vocabulary.json` is version **2** and includes `"Plan Discuss"` after `"Plan Ready"`; all five `watch_rules/*.json` declare `state_vocabulary_version: 2`; `check.json` lists Plan Discuss; `_CHECK_ASSIGNEE_STATES` includes Plan Discuss and omits `"In Review"`; `_load_rule` smoke passes for all five rules; deliberate version mismatch still raises.

1. Edit `~/team-chuckles/skills/rollcall/state_vocabulary.json`: set `"version": 2`; insert `"Plan Discuss"` immediately after `"Plan Ready"` in `states` (leave all other names unchanged).

2. Set `"state_vocabulary_version": 2` on all five files under `~/team-chuckles/skills/rollcall/watch_rules/`.

3. In `check.json` `linear.states`, insert `"Plan Discuss"` immediately after `"Plan Ready"`.

4. In `watch_linear.py` `_CHECK_ASSIGNEE_STATES`: add `"Plan Discuss"`; remove `"In Review"`. Do **not** add Plan Discuss to any `_WATCHER_EXCLUSIVE` frozenset. Do **not** add it to `_NEVER_WATCH_STATES` or `_MENTION_EXCLUDE`.

5. Smoke from `~/team-chuckles/skills/rollcall/` (same scripts as AST-923 Stage 1): load all five rules; then deliberate `state_vocabulary_version: 999` must raise.

6. Commit in **team-chuckles**: `code(AST-924): vocabulary v2 + Plan Discuss watcher gates`.

---

## Stage 3: Skills, rollcall, handoff, inventory, astral law

**Done when:** Every file in the Files Changed table for skills/rollcall/handoff/docs is updated to the mechanical rules above; inventory documents Plan Discuss enter/exit; astral workflow + §4.3 list Plan Discuss.

1. **`validate-plan/SKILL.md`** — rewrite gates and §6–§8 outcomes to match Mechanical rules:
   - Status gate: accept **`Plan Ready`** or **`Plan Discuss`** (else stop).
   - On **Plan Ready** + REVISE: `save_issue` status → **Plan Discuss**; comment `[plan-discuss] round=1 concern` + findings; assignee unchanged (engineer).
   - On **Plan Discuss**: count completed rounds by scanning comments for matching concern/reply pairs (`round=1` and `round=2`). If REVISE and completed &lt; 2: post next `concern` with `round=<completed+1>`; stay Plan Discuss. If REVISE and completed ≥ 2: escalate path (no round=3). APPROVED → Plan Approved. Re-plan → Todo.
   - Do **not** add plan-rubric statute checks (AST-928). Keep existing adversarial checklist content.
   - Description/header: mention Plan Discuss between Plan Ready and Plan Approved; Joan actor = Chuckles until AST-910.

2. **`plan-child/SKILL.md`** — add a short “Plan Discuss” note: engineer does **not** move status to Plan Approved; when status is Plan Discuss and Joan posted a concern, revise the plan on publish ref, push, post `[plan-discuss] round=N reply`. When Joan moved ticket to Todo, run full plan-child from Todo as today.

3. **`build-child/SKILL.md`** — one explicit sentence: status gate remains **Plan Approved** only; refuse Plan Discuss.

4. **`check-linear/SKILL.md`** — note that Plan Discuss children with unanswered `[plan-discuss] … concern` expect an engineer reply (or hand to validate-plan / datt); do not invent pipeline status moves in check-linear.

5. **`do-all-the-things/SKILL.md`** — wherever validate-plan sweeps **Plan Ready**, also include **Plan Discuss**.

6. **`rollcall_table.py`**: insert `"Plan Discuss": 2` in `STATUS_SORT`; renumber `"Plan Approved": 3`, `"Code Complete": 4`, `"Tests Ready": 5`, `"Tests Passed": 6`, `"Review Posted": 7`, `"In Progress": 8`, `"User Testing": 9`. In `action()`, treat Plan Discuss like Plan Ready (Chuck column gets `validate-plan`).

7. **`rollcall/SKILL.md`** — add Plan Discuss row to the action mapping table (`Chuck` → `valid-pl`).

8. **`agents/handoff-table.md`** — add `| Plan Discuss | Ada / Hedy / Katherine | same engineer file | engineer.sh |` after Todo (or beside Plan Approved).

9. **`seed-agents-md/SKILL.md`** — mention Plan Discuss → engineer seed.

10. **`docs/linear-state-consumers.md`** — set vocabulary version **2**; update rows for vocabulary, check.json, watch_linear, rollcall_table, validate-plan, plan-child, build-child, handoff-table, seed-agents-md, do-all-the-things, check-linear as needed; add **### Plan Discuss** transition subsection using the Mechanical rules; amend Plan Ready exit (REVISE → Plan Discuss) and Plan Approved enter (from Plan Ready or Plan Discuss APPROVED).

11. **`docs/ASTRAL_TEAM_WORKFLOW.md`** — in the status→skill table, after Plan Ready insert:

    `| Plan Discuss | Chuckles (Joan actor) + engineer | tagged discuss loop (`validate-plan` / plan reply); cap 2 → Archie (Susan); exit Plan Approved or Todo |`

    Amend Plan Ready exit line to mention Plan Discuss on REVISE.

12. **`docs/ASTRAL_CODE_RULES.md` §4.3** — replace the stale one-line state list with the current Team Chuckles pipeline **names** (Backlog, Discussion, Todo, In Progress, Plan Ready, Plan Discuss, Plan Approved, Code Complete, Tests Ready, Tests Passed, Review Posted, User Testing, PR Ready, Done, plus cancel/archive/duplicate as terminal taxonomy). Keep “Blocked is a label” and Done=merged meaning. Still name-only — no ids.

13. Commit in **team-chuckles**: `code(AST-924): Plan Discuss skill + rollcall + inventory`. Commit on **astral** epic worktree (workflow + §4.3 only): `code(AST-924): Plan Discuss in workflow + §4.3`. Publish astral tip to `origin/sub/AST-911/AST-924-plan-discuss-state`.

---

## Stage 4: Install, resume, canary

**Done when:** `./install.sh` has run on chuckles host; watchers resumed; `_load_rule` smoke green; a canary child has exercised Plan Discuss (at least one concern/reply round) **and** the Archie escalate path is observable (escalate comment + assignee Susan); zero stalled-watcher incidents for Plan Discuss (no version crash loop, no exclusive-owner fight, check watcher loads).

1. Checklist step 5: `cd ~/team-chuckles && ./install.sh`.

2. Checklist step 6: `bash -l ~/team-chuckles/skills/wake-up-chuck-linux.sh`. Confirm `watch_linear` processes are up and not restart-looping.

3. Re-run `_load_rule` smoke for all five rules.

4. **Canary** (create under parent AST-911 or Team Chuckles; title `AST-924 canary — Plan Discuss`; assignee Hedy or Ada; start in **Todo** then move artificially as needed — do **not** burn a real product child):
   a. Ensure a plan doc path exists (minimal stub on a throwaway publish ref **or** reuse a disposable description-only issue with no git — prefer a real sub if dispatch already seeded one; otherwise create Linear issue + mark canary in title).
   b. Move canary to **Plan Ready**, run validate-plan REVISE path → must land **Plan Discuss** with `[plan-discuss] round=1 concern`.
   c. Post `[plan-discuss] round=1 reply` as engineer; re-run validate-plan REVISE → `round=2 concern`.
   d. Post `round=2 reply`; re-run validate-plan REVISE → must **escalate** (`[plan-discuss] escalate`, assignee Susan), **not** `round=3`.
   e. As Archie/Susan (or Chuckles simulating with Susan’s key only if Susan pre-approved — otherwise leave assignee Susan and note in live-run log that Archie resolution is manual): move canary → **Todo** or **Plan Approved** to clear it; cancel/archive canary when done.
   f. Confirm during b–d: no watcher crash; `check` can see Plan Discuss; rollcall renders Plan Discuss with Chuck `valid-pl` action.

5. Append **Live run log (AST-924)** to `~/team-chuckles/docs/linear-state-migration-checklist.md`: each checklist step 1–7 with timestamp + result; canary issue id; note “zero stalled-watcher incidents” or list any incident (if any incident: stop and comment on AST-911 — do not mark AC met).

6. Commit in **team-chuckles**: `code(AST-924): migration live-run log + canary`. Push team-chuckles `main`. Publish any astral stub updates to the publish ref.

---

## Execution contract

- Execute stages in order. Do not reorder migration checklist steps 1–7.
- Do not add plan-rubric content. Do not invent a second inventory.
- Name-only state matching everywhere — never persist Plan Discuss’s Linear id in configs.
- If Linear state create fails, or watchers crash-loop after resume, or canary shows a stalled watcher — stop and comment on **AST-911** with the `🛑 Stage N blocked` format.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — new Linear workflow state plus vocabulary v2 cutover across watcher configs/runtime, validate-plan transition semantics, rollcall, handoff, inventory, and astral workflow/§4.3; first live use of AST-923’s migration checklist.

**Conf:** `Medium` — AST-923 inventory/checklist and dry-run worksheet remove rediscovery risk; remaining uncertainty is Linear `workflowStateCreate` permissions on the host key and canary logistics under live watchers.

**Risk:** `HIGH` — a bad vocabulary/watcher cutover can stall all Chuckles watchers; wrong exclusive ownership or missing check-state would strand Plan Discuss tickets; round-cap bugs could infinite-loop validate-plan or skip Archie.

## Self-review vs ASTRAL_CODE_RULES

- §1.1 — team-chuckles + astral workflow/§4.3 only; no product `src/` state machines.
- §1.4 / §2.1 — vocabulary file remains single source for watcher version + names; bump is explicit.
- §2.6 — N/A for JOB_STATES; Linear pipeline transitions are skill-documented, name-keyed.
- §3.3 — no new astral layer imports.
- §4.3 — intentionally updated in Stage 3 so law matches live vocabulary (fixes stale In Review list as part of this additive cutover).

## Review (build stub)

**Publish ref:** `origin/sub/AST-911/AST-924-plan-discuss-state`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `b192ccc` | Plan doc on astral sub |
| 1 | Linear only | Created `Plan Discuss` workflow state; paused `chuck` |
| 2 | `team-chuckles@96baecf` | vocabulary v2 + watcher gates |
| 3 | `team-chuckles@d15a0d9` + astral `a456b82` | skills/rollcall/inventory + workflow/§4.3 |
| 4 | `team-chuckles@99534f8` | install/resume; canary AST-954; live-run log |

**Tip:** astral publish ref after stub commit below; tooling on `team-chuckles` `main` @ `99534f8`.

**Canary:** AST-954 — Plan Discuss 2-round + Archie escalate path; zero stalled-watcher incidents.
