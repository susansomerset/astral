# AST-453 — Explicit cache block references for tasks

<!-- linear-archive: AST-453 archived 2026-06-15 -->

## Linear archive (AST-453)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-453/explicit-cache-block-references-for-tasks  
**Status at archive:** Done  
**Project:** Astral Agent  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-450; related: AST-313

### Description

## Purpose

The Agent component assembles prompts for every `do_task` call. Today, cross-hop reuse when `run_next` chains tasks relies on an implicit mapping from a caller’s legacy prompt fields into chain tokens, which does not match how operators need to author prompts: each hop should store up to five cached segments (system plus four cache blocks), plus no-cache and user content, and downstream hops should reference the **caller’s resolved segment text** by explicit token names—not by inferred slot remapping.

This feature is a permanent enhancement to prompt assembly, persistence, Manage Tasks editing, token resolution, and chain pass-through. It is not an Artifacts feature; artifact pipelines may use it like any other chained tasks, but scope and design are Agent-only.

## Functional scope

* **Universal** `agent_task` **shape.** Every task row gains persistent storage for all seven segments: system prompt, cache blocks A–D, no-cache block, and user prompt. This replaces the legacy single `cache_prompt` field as the only cache slot. Existing row content is migrated or mapped so consult/roster and other tasks keep working until an operator edits them (for example legacy `cache_prompt` → cache block A).
* **Manage Tasks segment layout.** The task edit experience presents segments in this fixed order, using the same editing components as today: System Prompt; Cache Block A; Cache Block B; Cache Block C; Cache Block D; No Cache Block; User Prompt. Each segment is independently editable, saved, and reloaded.
* **Five cached segments at runtime.** When a task runs, non-empty system prompt and cache blocks A–D are each sent as separate cached API content. Non-empty no-cache and user segments are sent without cache control.
* **Caller chain tokens (downstream hops only).** When a task is invoked via `run_next` from a prior hop, its prompt text may reference the caller’s **resolved** segment contents using these tokens only:
  * `{$CALLER_SYSTEM}`
  * `{$CALLER_CACHE_A}` through `{$CALLER_CACHE_D}`
  * `{$CALLER_RESPONSE}` (prior hop’s agent output, text or serialized structured response)

  Tokens are registered in the config-driven token list for Manage Tasks tooling. Admin preview and production resolution use the same set.

  **Not valid tokens:** `{$NO_CACHE_BLOCK}`, `{$USER_PROMPT}`, and other “caller no-cache / caller user” references are intentionally excluded—downstream prompts do not inherit those slots via tokens.
* **Explicit inheritance only; no automatic slot replacement.** Updating what flows forward in a cache block (for example putting the new resume draft into cache block A for the next hop) is done only by what the operator types in that segment in Manage Tasks—such as placing `{$CALLER_RESPONSE}` in cache block A—with **no** automatic overwrite of cache slots by task key and **no** fallback mapping when a token is absent. Missing or empty caller values resolve per existing token rules (empty string; no silent substitution from legacy slots).
* `run_next` **pass-through.** After a successful hop, the next task receives `chain_context` built from the caller’s **resolved** segment strings (after token substitution on the caller) plus `{$CALLER_RESPONSE}`. The callee places those values into its own local segments via the caller tokens above; local segment layout remains the operator’s choice.

## Boundaries

* **Agent scope only.** Prompt assembly, `agent_task` persistence, `resolve_tokens`, `do_task` / `preview_prompt`, and Manage Tasks (plus admin preview endpoints that mirror production). No tracker artifact persistence, job UI, or Artifacts-project deliverables.
* **No pipeline choreography in code.** Chain order and hop count remain `run_next` in the database and operator-authored prompt content only—no step lists, pipeline registries, or task-key-driven cache promotion.
* **Not prompt copy authoring.** Writing specific multi-hop prompt text for any product area is out of scope; this ticket delivers the segment model and caller tokens.
* **Ad Hoc Anthropic page** out of scope unless parity is required for the same token set.
* **Must not break** non-chained `do_task` callers or consult/roster dispatch. Supersedes the implicit AST-304 mapping that assigned `{$CACHE_BLOCK_A}`–`D` from legacy system/cache/no-cache/live; migration must document behavior for tasks not yet re-authored to caller tokens.
* **Config-driven tokens** per ASTRAL_CODE_RULES §2.1. `{$SELECTED_AGENT}` and other existing non-caller tokens remain for current-hop resolution where already used.

## Acceptance criteria

1. All `agent_task` rows persist seven segments; Manage Tasks shows them in order (system, cache A–D, no-cache, user); save and reload round-trip correctly.
2. A task with content in system and cache A–D sends up to five distinct cached API blocks (empty segments omitted); no-cache and user content are not cached.
3. In a two-hop `run_next` chain, callee prompts using `{$CALLER_SYSTEM}`, `{$CALLER_CACHE_A}`–`{$CALLER_CACHE_D}`, and `{$CALLER_RESPONSE}` resolve to the caller’s resolved segment text and response; distinct marker strings in each caller segment prove each token.
4. `{$NO_CACHE_BLOCK}` and `{$USER_PROMPT}` are not registered as resolvable tokens (and do not appear as selectable chain tokens in Manage Tasks tooling).
5. A three-hop chain where hop 2’s cache block A text explicitly contains `{$CALLER_RESPONSE}` passes the hop-2 response into hop 3’s resolved `{$CALLER_CACHE_A}` with no automatic task-key overwrite and no fallback from other slots.
6. Admin prompt preview matches production for caller tokens on at least one chained task.
7. At least one existing non-chained task whose content was only migrated from legacy fields (single cache → cache A) still runs successfully without manual re-authoring.
8. `python3 -m py_compile` and affected component tests for token resolution and chain context pass.

## Dependencies and blockers

* **AST-303** (Done) — `run_next` daisy-chain in `do_task`.
* **AST-304** (Done) — chain context and token registry; superseded for inheritance semantics by caller-prefixed tokens in this ticket.
* **AST-305** (Done) — per-task `system_prompt` column.
* **AST-306** (Done) — `run_next` on `agent_task` and Manage Tasks UI.

None blocking start. Related work in other projects (for example prompt authoring elsewhere) is not a dependency.

## Open questions

None.

### Comments

#### chuckles — 2026-05-23T21:24:49.244Z
## Landed on origin/dev — Chuckles

- Merged `origin/ftr/AST-453-explicit-cache-block-references-for-tasks` → local `dev` (already at tip from prep-uat) → pushed `origin/dev`
- Deleted `origin/ftr/AST-453-explicit-cache-block-references-for-tasks`
- Moved to **Done** (were PR Ready): AST-453, AST-454, AST-455, AST-456

Push tip: `394fa9bb`

— Chuckles

#### chuckles — 2026-05-23T21:19:04.184Z
## Landed on origin/dev — Chuckles

- Merged `origin/ftr/AST-453-explicit-cache-block-references-for-tasks` → local `dev` (already at tip from prep-uat) → pushed `origin/dev`
- Deleted `origin/ftr/AST-453-explicit-cache-block-references-for-tasks`
- Moved to **Done** (were PR Ready): AST-453, AST-454, AST-455, AST-456

Push tip: `394fa9bb`

— Chuckles

#### chuckles — 2026-05-23T20:39:53.695Z
## do-all-the-things — run complete

**Parent:** AST-453
**Children:**
- AST-454 — agent_task seven-segment persistence — **User Testing** — Ada
- AST-455 — caller tokens and five-segment prompt assembly — **User Testing** — Ada
- AST-456 — Manage Tasks seven-segment UI — **User Testing** — (assignee unset in Linear; built by Ada on shared branch)

### Completed path
- Dispatch (3 children, `ftr` + `sub/*` branches)
- plan-astral (Ada planned all three)
- validate-plan (APPROVED ×3)
- check-linear
- build-astral (454 → 455 → 456 Code Complete)
- qa-astral (Betty → Tests Ready)
- test-astral (454/455 Ada; 456 Katherine — all Tests Passed)
- review-astral (Radia — Review Posted, 0 fix-now)
- resolve-astral (User Testing on all children)
- **prep-uat** — merged into `origin/ftr/AST-453-…` @ `394fa9bb`; local `dev` fast-forwarded; `sub/*` deleted

### Stalled / needs Susan
- **AST-453** → **User Testing** — your UAT queue (checklist posted above)
- **AST-456** Linear assignee still flaky via MCP — set Katherine or Ada if you care for card hygiene
- **`origin/dev`** not pushed — push after UAT or say **finish-up AST-453**

### prep-uat
- **Success** — parent ready for UAT on local `dev` and `origin/ftr/AST-453-explicit-cache-block-references-for-tasks`

— Chuckles

#### chuckles — 2026-05-23T20:39:50.264Z
## UAT Ready — Chuckles

All 3 child branches merged into parent branch; child `sub/*` branches deleted.

**Parent branch:** `origin/ftr/AST-453-explicit-cache-block-references-for-tasks` @ `394fa9bb`
**Local dev:** fast-forwarded to same tip (not pushed to `origin/dev`).

### Manual test checklist

1. Restart app on local **`dev`**.
2. **Manage Tasks (AST-456):** Open Admin → Manage Tasks → edit any task. Confirm panels in order: System → Cache A–D → No cache → User.
3. Enter distinct marker text in each segment; Save; reopen modal — all seven round-trip.
4. **Persistence (AST-454):** PUT includes `cache_prompt_b|c|d`; legacy tasks with only old `cache_prompt` still load (content in Cache A).
5. **Caller tokens (AST-455):** Token picker shows `{$CALLER_SYSTEM}`, `{$CALLER_CACHE_A}`–`D`, `{$CALLER_RESPONSE}` — not `{$NO_CACHE_BLOCK}` / `{$USER_PROMPT}`.
6. **Preview:** Open preview on a task; confirm segment tabs match populated blocks.
7. **Chain (optional):** Two-hop `run_next` with marker strings in caller segments; callee resolves caller tokens (see AST-455 acceptance criteria).
8. **Regression:** Run `./scripts/testing/run_component_tests.sh` — should stay green (847 pytest + 206 Vitest per Ada’s pass).

— Chuckles

#### ada — 2026-05-23T20:35:06.407Z
[check-linear] §0a blocked: `git rebase origin/dev` on `dev-ada` stops on add/add conflict in `docs/features/administrator/ast-438-production-readiness-admin-prompt-and-rubric-diagnostic.md` (replay of 3ee9e102); aborted; still `dev-ada...origin/dev` ahead 83 — need Susan/Chuckles on reconcile/merge strategy for that doc vs `origin/dev`. §0b/@ada Team Astral union 32 issues (+ Astral Agent narrower pass unioned); AST-453/454/455/456 in set. §2–§4 (happy path family): no actionable thread on 454/455/456 needing Ada reply after latest engineer activity this pass. Workspace: `/Users/susan/chuckles/astral-ada`, on `dev-ada`.

#### betty — 2026-05-23T20:32:27.504Z
[check-linear]

**blocked: §0a (`dev-betty` vs `origin/dev`)** — `git fetch` then `git rebase origin/dev` on `dev-betty` stops on **merge conflict** in `tests/component/core/test_agent.py` while replaying stacked history (first failing replayed commit message referenced **AST-450** seven-segment align). Ran **`git rebase --abort`**; **`dev-betty`** left as before (still diverged from **`origin/dev-betty`** per local status). Integration branch is **not** cleanly rebased onto **`origin/dev`** until Susan/Chuckles/engineer resolves that conflict (merge vs selective rebase).

**§0b `@betty` (Team Astral)** — `list_issues` query **`@betty`**, **`includeArchived: true`**, **`hasNextPage` false** → **48** ids; union orchestrator gaps **AST-453**, **AST-455** → **50** ids intended for **`list_comments`** sweep.

**§1 assignee add-on** — Betty **`list_issues`** with **`assignee`** filter failed from this MCP client (invalid JSON serialization for `me`). By thread read, **Astral Agent** children **AST-454** / **AST-455** / **AST-456** stay on **Ada** / **Katherine** — no Betty-assignee backlog on that trio for inbox.

**Orchestrator scope (parent + AST-454 / AST-455 / AST-456)** — **`list_comments`** on all four: latest activity is **Tests Passed** handoffs (**Ada** on 454–456 stack; **Katherine** on **AST-456**) after Betty **Tests Ready** manifests; **no** new markdown **`@betty`** and **no** peer question clearly expecting Betty’s reply **after** Betty’s QA posts. Nothing to patch under check-linear here.

**Extra union sample** — Comment threads on early alphabet hits (**AST-297** … **AST-385**) reviewed in this pass: mentions of “Betty” are role/manifest citations, not open **`@betty`** nags needing a_reply in this inbox pass.

**§6** — Did **not** run **`qa-astral`**, **`test-astral`**, or **`review-astral`** (per check-linear skill; next stage when Susan names it).

#### hedy — 2026-05-23T20:32:06.983Z
[check-linear]

- **§0a blocked:** `git rebase origin/dev` on **`dev-hedy`** conflicts replaying **`src/core/tracker.py`** and **`src/utils/config.py`** (first failing replay: AST-302 feat). **`git rebase --abort`** — integration branch **not** synced with **`origin/dev`** until Susan/Chuckles picks merge vs conflict resolution strategy.

- **Session scope — Astral Agent parent + children:** **`list_comments`** on **AST-453**, **AST-454**, **AST-455**, **AST-456**. Latest posts are Ada/Betty/Katherine **Tests Passed** handoffs (≈ **2026-05-23 20:27–20:29Z**); **no `@hedy`** and **no** question clearly expecting Hedy after **this** ticket’s prior **`[check-linear]`** (dispatch assigns **454–455 → Ada**, **456 → Katherine**; Chuckles notes **Hedy not on dispatch**).

- **§0b / §1 union (Team Astral `@hedy` issue search ∪ explicit AST-454/455/456):** **36** unique ids — **full `list_comments` (paginated, no `hasNextPage` remainder)** on **all 36**. **No** actionable item under §2 (nothing **not by Hedy** that is both after Hedy’s latest **`[check-linear]`** on that issue where present **and** **`@hedy`** / clearly directed at Hedy). Notable non-actionable noise: legacy tickets where Linear **`@hedy` search** hits **“Hedy”** in descriptions (e.g. artifacts parents) without a new mention in-thread.

- **§6:** Not invoking **`plan-astral`** / **`build-astral`** / **`test-astral`** / **`resolve-astral`** / **`qa-astral`** / **`review-astral`** from this pass.

**Next:** Unblock **`dev-hedy` ↔ `origin/dev`** per workspace guard; orchestrator **`do-all-the-things`** / stage skills when Susan names them.

#### hedy — 2026-05-23T19:59:56.243Z
[check-linear]

- **§0a blocked:** `git checkout dev-hedy && git rebase origin/dev` failed replaying stacked history — merge conflicts in `src/core/tracker.py` and `src/utils/config.py` (first conflicted commit in replay: feat AST-302 job state machine). Ran `git rebase --abort`; branch restored.
- **Child-list assignee queue (AST-454 / AST-455 / AST-456):** Dispatch assigns **Ada** on **454**–**455** and **Manage Tasks UI** child per parent thread — **none** are **Hedy**, so there is **no Hedy assignee backlog** on that list for this skill pass (per orchestrator “children only”; skipped other Astral Agent tickets).
- **Threads scanned:** **AST-453**, **AST-454**, **AST-455**, **AST-456** — latest activity is plan validation / dispatch; **no** open comment requiring Hedy reply or `[check-linear]` action (no `@hedy` in markdown bodies on those threads).
- **`@hedy` search:** Team Astral query returned hits mostly from descriptions (“Hedy” literal); sampled threads — no pending `@hedy` mention backlog needing code/doc edits here.

**Next:** Resolve `dev-hedy` vs `origin/dev` integration (merge or manual conflict resolution), or reassign if Hedy should own a child.

#### chuckles — 2026-05-23T19:48:59.970Z
## Dispatch — Chuckles

Dispatched 3 child tickets from the approved definition.

| Ticket | Title | Assigned to | Branch | Blocked by |
|--------|-------|-------------|--------|------------|
| AST-454 | agent_task seven-segment persistence | Ada | sub/AST-453/AST-454-explicit-cache-block-references-for-tasks-agent-task-seven-segment-persistence | — |
| AST-455 | caller tokens and five-segment prompt assembly | Ada | sub/AST-453/AST-455-explicit-cache-block-references-for-tasks-caller-tokens-and-five-segment-prompt-assembly | AST-454 |
| AST-456 | Manage Tasks seven-segment UI | Katherine | sub/AST-453/AST-456-explicit-cache-block-references-for-tasks-manage-tasks-seven-segment-ui | AST-454 |

Assignment rationale:
- Ada: data layer, `do_task` assembly, caller tokens, admin API runtime (primary Agent domain).
- Katherine: Manage Tasks seven-segment UI.
- Hedy: not assigned this dispatch.

**Git (authoritative):**
- Parent: `origin/ftr/AST-453-explicit-cache-block-references-for-tasks`
- Children: `origin/sub/AST-453/AST-454-…`, `AST-455-…`, `AST-456-…`

— Chuckles

#### chuckles — 2026-05-23T19:46:37.049Z
Definition updated from your inline answers in the Description:

- **Scope:** Agent prompt assembly only (not Artifacts); universal seven-segment `agent_task` shape.
- **Chain tokens:** `{$CALLER_SYSTEM}`, `{$CALLER_CACHE_A}`–`D`, `{$CALLER_RESPONSE}` only; no `{$NO_CACHE_BLOCK}` / `{$USER_PROMPT}`.
- **Inheritance:** explicit Manage Tasks text only (e.g. `{$CALLER_RESPONSE}` in cache A); no task-key auto-replace, no fallback.
- **Open questions:** cleared.

If the Description looks right, you’re already **Todo + Chuckles** — ready for dispatch when you say so.

— Chuckles

#### chuckles — 2026-05-23T19:34:08.745Z
Definition draft ready for review. Key decisions made:
- Explicit seven-segment Manage Tasks model (system + cache A–D + no-cache + user) replaces implicit legacy-slot→chain-token mapping; chain pass-through uses resolved segment content.
- Builds on done chain work (AST-303/304/305/306/450); does not add pipeline step lists (AST-450 dumb-chain rule preserved).
- **6 open questions** (token naming, cache-slot replacement semantics, legacy migration, advise vs guide task key, project split for dispatch).

Please review the Description and comment with changes or approval.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
