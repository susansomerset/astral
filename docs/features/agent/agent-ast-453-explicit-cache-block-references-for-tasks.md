# AST-453 — Explicit cache block references for tasks

**Component:** agent  
**Children:** AST-454, AST-455, AST-456  
**Linear archived:** AST-453 2026-06-15

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-05-23 13:04 | AST-454 | declared | `f8b263d10` | feat(AST-454): persist seven prompt segments on agent_task |

## Epic — AST-453

_Archived: 2026-06-15 · Linear URL: https://linear.app/astralcareermatch/issue/AST-453/explicit-cache-block-references-for-tasks · Status at archive: Done · Project: Astral Agent · Assignee: susan · Priority / estimate: None / — · Blocked by / blocks / related: related: AST-450; related: AST-313_

### Purpose

The Agent component assembles prompts for every `do_task` call. Today, cross-hop reuse when `run_next` chains tasks relies on an implicit mapping from a caller’s legacy prompt fields into chain tokens, which does not match how operators need to author prompts: each hop should store up to five cached segments (system plus four cache blocks), plus no-cache and user content, and downstream hops should reference the **caller’s resolved segment text** by explicit token names—not by inferred slot remapping.

This feature is a permanent enhancement to prompt assembly, persistence, Manage Tasks editing, token resolution, and chain pass-through. It is not an Artifacts feature; artifact pipelines may use it like any other chained tasks, but scope and design are Agent-only.

### Functional scope

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

### Boundaries

* **Agent scope only.** Prompt assembly, `agent_task` persistence, `resolve_tokens`, `do_task` / `preview_prompt`, and Manage Tasks (plus admin preview endpoints that mirror production). No tracker artifact persistence, job UI, or Artifacts-project deliverables.
* **No pipeline choreography in code.** Chain order and hop count remain `run_next` in the database and operator-authored prompt content only—no step lists, pipeline registries, or task-key-driven cache promotion.
* **Not prompt copy authoring.** Writing specific multi-hop prompt text for any product area is out of scope; this ticket delivers the segment model and caller tokens.
* **Ad Hoc Anthropic page** out of scope unless parity is required for the same token set.
* **Must not break** non-chained `do_task` callers or consult/roster dispatch. Supersedes the implicit AST-304 mapping that assigned `{$CACHE_BLOCK_A}`–`D` from legacy system/cache/no-cache/live; migration must document behavior for tasks not yet re-authored to caller tokens.
* **Config-driven tokens** per ASTRAL_CODE_RULES §2.1. `{$SELECTED_AGENT}` and other existing non-caller tokens remain for current-hop resolution where already used.

### Acceptance criteria

1. All `agent_task` rows persist seven segments; Manage Tasks shows them in order (system, cache A–D, no-cache, user); save and reload round-trip correctly.
2. A task with content in system and cache A–D sends up to five distinct cached API blocks (empty segments omitted); no-cache and user content are not cached.
3. In a two-hop `run_next` chain, callee prompts using `{$CALLER_SYSTEM}`, `{$CALLER_CACHE_A}`–`{$CALLER_CACHE_D}`, and `{$CALLER_RESPONSE}` resolve to the caller’s resolved segment text and response; distinct marker strings in each caller segment prove each token.
4. `{$NO_CACHE_BLOCK}` and `{$USER_PROMPT}` are not registered as resolvable tokens (and do not appear as selectable chain tokens in Manage Tasks tooling).
5. A three-hop chain where hop 2’s cache block A text explicitly contains `{$CALLER_RESPONSE}` passes the hop-2 response into hop 3’s resolved `{$CALLER_CACHE_A}` with no automatic task-key overwrite and no fallback from other slots.
6. Admin prompt preview matches production for caller tokens on at least one chained task.
7. At least one existing non-chained task whose content was only migrated from legacy fields (single cache → cache A) still runs successfully without manual re-authoring.
8. `python3 -m py_compile` and affected component tests for token resolution and chain context pass.

### Dependencies and blockers

* **AST-303** (Done) — `run_next` daisy-chain in `do_task`.
* **AST-304** (Done) — chain context and token registry; superseded for inheritance semantics by caller-prefixed tokens in this ticket.
* **AST-305** (Done) — per-task `system_prompt` column.
* **AST-306** (Done) — `run_next` on `agent_task` and Manage Tasks UI.

None blocking start. Related work in other projects (for example prompt authoring elsewhere) is not a dependency.

### Open questions

None.

### do-all-the-things — run complete

**Parent:** AST-453
**Children:**
- AST-454 — agent_task seven-segment persistence — **User Testing** — Ada
- AST-455 — caller tokens and five-segment prompt assembly — **User Testing** — Ada
- AST-456 — Manage Tasks seven-segment UI — **User Testing** — (assignee unset in Linear; built by Ada on shared branch)

#### Completed path

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

#### Stalled / needs Susan

- **AST-453** → **User Testing** — your UAT queue (checklist posted above)
- **AST-456** Linear assignee still flaky via MCP — set Katherine or Ada if you care for card hygiene
- **`origin/dev`** not pushed — push after UAT or say **finish-up AST-453**

#### prep-uat

- **Success** — parent ready for UAT on local `dev` and `origin/ftr/AST-453-explicit-cache-block-references-for-tasks`

### UAT Ready — Chuckles

All 3 child branches merged into parent branch; child `sub/*` branches deleted.

**Parent branch:** `origin/ftr/AST-453-explicit-cache-block-references-for-tasks` @ `394fa9bb`
**Local dev:** fast-forwarded to same tip (not pushed to `origin/dev`).

#### Manual test checklist

1. Restart app on local **`dev`**.
2. **Manage Tasks (AST-456):** Open Admin → Manage Tasks → edit any task. Confirm panels in order: System → Cache A–D → No cache → User.
3. Enter distinct marker text in each segment; Save; reopen modal — all seven round-trip.
4. **Persistence (AST-454):** PUT includes `cache_prompt_b|c|d`; legacy tasks with only old `cache_prompt` still load (content in Cache A).
5. **Caller tokens (AST-455):** Token picker shows `{$CALLER_SYSTEM}`, `{$CALLER_CACHE_A}`–`D`, `{$CALLER_RESPONSE}` — not `{$NO_CACHE_BLOCK}` / `{$USER_PROMPT}`.
6. **Preview:** Open preview on a task; confirm segment tabs match populated blocks.
7. **Chain (optional):** Two-hop `run_next` with marker strings in caller segments; callee resolves caller tokens (see AST-455 acceptance criteria).
8. **Regression:** Run `./scripts/testing/run_component_tests.sh` — should stay green (847 pytest + 206 Vitest per Ada’s pass).

##### ada — 2026-05-23T20:35:06.407Z

[check-linear] §0a blocked: `git rebase origin/dev` on `dev-ada` stops on add/add conflict in `docs/features/administrator/ast-438-production-readiness-admin-prompt-and-rubric-diagnostic.md` (replay of 3ee9e102); aborted; still `dev-ada...origin/dev` ahead 83 — need Susan/Chuckles on reconcile/merge strategy for that doc vs `origin/dev`. §0b/@ada Team Astral union 32 issues (+ Astral Agent narrower pass unioned); AST-453/454/455/456 in set. §2–§4 (happy path family): no actionable thread on 454/455/456 needing Ada reply after latest engineer activity this pass. Workspace: `/Users/susan/chuckles/astral-ada`, on `dev-ada`.

##### betty — 2026-05-23T20:32:27.504Z

[check-linear]

**blocked: §0a (`dev-betty` vs `origin/dev`)** — `git fetch` then `git rebase origin/dev` on `dev-betty` stops on **merge conflict** in `tests/component/core/test_agent.py` while replaying stacked history (first failing replayed commit message referenced **AST-450** seven-segment align). Ran **`git rebase --abort`**; **`dev-betty`** left as before (still diverged from **`origin/dev-betty`** per local status). Integration branch is **not** cleanly rebased onto **`origin/dev`** until Susan/Chuckles/engineer resolves that conflict (merge vs selective rebase).

**§0b `@betty` (Team Astral)** — `list_issues` query **`@betty`**, **`includeArchived: true`**, **`hasNextPage` false** → **48** ids; union orchestrator gaps **AST-453**, **AST-455** → **50** ids intended for **`list_comments`** sweep.

**§1 assignee add-on** — Betty **`list_issues`** with **`assignee`** filter failed from this MCP client (invalid JSON serialization for `me`). By thread read, **Astral Agent** children **AST-454** / **AST-455** / **AST-456** stay on **Ada** / **Katherine** — no Betty-assignee backlog on that trio for inbox.

**Orchestrator scope (parent + AST-454 / AST-455 / AST-456)** — **`list_comments`** on all four: latest activity is **Tests Passed** handoffs (**Ada** on 454–456 stack; **Katherine** on **AST-456**) after Betty **Tests Ready** manifests; **no** new markdown **`@betty`** and **no** peer question clearly expecting Betty’s reply **after** Betty’s QA posts. Nothing to patch under check-linear here.

**Extra union sample** — Comment threads on early alphabet hits (**AST-297** … **AST-385**) reviewed in this pass: mentions of “Betty” are role/manifest citations, not open **`@betty`** nags needing a_reply in this inbox pass.

**§6** — Did **not** run **`qa-astral`**, **`test-astral`**, or **`review-astral`** (per check-linear skill; next stage when Susan names it).

##### hedy — 2026-05-23T20:32:06.983Z

[check-linear]

- **§0a blocked:** `git rebase origin/dev` on **`dev-hedy`** conflicts replaying **`src/core/tracker.py`** and **`src/utils/config.py`** (first failing replay: AST-302 feat). **`git rebase --abort`** — integration branch **not** synced with **`origin/dev`** until Susan/Chuckles picks merge vs conflict resolution strategy.

- **Session scope — Astral Agent parent + children:** **`list_comments`** on **AST-453**, **AST-454**, **AST-455**, **AST-456**. Latest posts are Ada/Betty/Katherine **Tests Passed** handoffs (≈ **2026-05-23 20:27–20:29Z**); **no `@hedy`** and **no** question clearly expecting Hedy after **this** ticket’s prior **`[check-linear]`** (dispatch assigns **454–455 → Ada**, **456 → Katherine**; Chuckles notes **Hedy not on dispatch**).

- **§0b / §1 union (Team Astral `@hedy` issue search ∪ explicit AST-454/455/456):** **36** unique ids — **full `list_comments` (paginated, no `hasNextPage` remainder)** on **all 36**. **No** actionable item under §2 (nothing **not by Hedy** that is both after Hedy’s latest **`[check-linear]`** on that issue where present **and** **`@hedy`** / clearly directed at Hedy). Notable non-actionable noise: legacy tickets where Linear **`@hedy` search** hits **“Hedy”** in descriptions (e.g. artifacts parents) without a new mention in-thread.

- **§6:** Not invoking **`plan-astral`** / **`build-astral`** / **`test-astral`** / **`resolve-astral`** / **`qa-astral`** / **`review-astral`** from this pass.

**Next:** Unblock **`dev-hedy` ↔ `origin/dev`** per workspace guard; orchestrator **`do-all-the-things`** / stage skills when Susan names them.

##### hedy — 2026-05-23T19:59:56.243Z

[check-linear]

- **§0a blocked:** `git checkout dev-hedy && git rebase origin/dev` failed replaying stacked history — merge conflicts in `src/core/tracker.py` and `src/utils/config.py` (first conflicted commit in replay: feat AST-302 job state machine). Ran `git rebase --abort`; branch restored.
- **Child-list assignee queue (AST-454 / AST-455 / AST-456):** Dispatch assigns **Ada** on **454**–**455** and **Manage Tasks UI** child per parent thread — **none** are **Hedy**, so there is **no Hedy assignee backlog** on that list for this skill pass (per orchestrator “children only”; skipped other Astral Agent tickets).
- **Threads scanned:** **AST-453**, **AST-454**, **AST-455**, **AST-456** — latest activity is plan validation / dispatch; **no** open comment requiring Hedy reply or `[check-linear]` action (no `@hedy` in markdown bodies on those threads).
- **`@hedy` search:** Team Astral query returned hits mostly from descriptions (“Hedy” literal); sampled threads — no pending `@hedy` mention backlog needing code/doc edits here.

**Next:** Resolve `dev-hedy` vs `origin/dev` integration (merge or manual conflict resolution), or reassign if Hedy should own a child.

##### chuckles — 2026-05-23T19:46:37.049Z

Definition updated from your inline answers in the Description:

- **Scope:** Agent prompt assembly only (not Artifacts); universal seven-segment `agent_task` shape.
- **Chain tokens:** `{$CALLER_SYSTEM}`, `{$CALLER_CACHE_A}`–`D`, `{$CALLER_RESPONSE}` only; no `{$NO_CACHE_BLOCK}` / `{$USER_PROMPT}`.
- **Inheritance:** explicit Manage Tasks text only (e.g. `{$CALLER_RESPONSE}` in cache A); no task-key auto-replace, no fallback.
- **Open questions:** cleared.

If the Description looks right, you’re already **Todo + Chuckles** — ready for dispatch when you say so.

##### chuckles — 2026-05-23T19:34:08.745Z

Definition draft ready for review. Key decisions made:
- Explicit seven-segment Manage Tasks model (system + cache A–D + no-cache + user) replaces implicit legacy-slot→chain-token mapping; chain pass-through uses resolved segment content.
- Builds on done chain work (AST-303/304/305/306/450); does not add pipeline step lists (AST-450 dumb-chain rule preserved).
- **6 open questions** (token naming, cache-slot replacement semantics, legacy migration, advise vs guide task key, project split for dispatch).

Please review the Description and comment with changes or approval.

---

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-454 — Explicit cache block references for tasks: agent_task seven-segment persistence

#### Summary

Persist all seven Manage Tasks prompt segments in `agent_task`: system prompt (existing `system_prompt`), four independent cache segments (legacy `cache_prompt` is **semantic slot A** plus new columns for slots B–D), no-cache (`nocache_prompt`), and user (`user_prompt`). Ship schema migration (`ALTER ADD` for cache B/C/D only), versioning rules that treat **any** segment edit as prompt content versioning, expanded admin read/write APIs, and list-row metadata lengths so Manage Tasks / admin list stay consistent. Legacy rows keep working: historical `cache_prompt` text stays in **cache block A**. Runtime Anthropic assembly and caller tokens belong to **AST-455**; React panels belong to **AST-456**.

#### Stage 1: Schema and migration

**Done when:** Fresh DB creates full column set; upgraded DB picks up three new TEXT columns default `''`; `PRAGMA table_info(agent_task)` shows `cache_prompt` + `_b/_c/_d`.

1. Update the **bullet** for `agent_task` in **`src/data/database.py`** header (first ~40 lines inventory) documenting seven semantic segments: `system_prompt`, `cache_prompt` (block A), `cache_prompt_b/c/d` (blocks B–D), `nocache_prompt`, `user_prompt`, plus existing `run_next`, `agent_id`, versioning columns.
2. In `_ensure_agent_task_schema`, after existing `system_prompt` migration block, for each of `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d` missing from `PRAGMA table_info`, execute `ALTER TABLE agent_task ADD COLUMN <name> TEXT NOT NULL DEFAULT ''` then `conn.commit()`.
3. **No destructive table rebuild** unless an existing SQLite file contains an unmigrated anomaly—reuse the same ALTER pattern as `run_next`/`system_prompt`.
4. `python3 -m py_compile src/data/database.py`

⚠️ **Decision:** Database column naming uses `cache_prompt` as slot A instead of renaming to `cache_prompt_a` to avoid rewriting every INSERT in migration history and all foreign tooling; semantics are spelled in the inventory comment only.

---

#### Stage 2: `save_agent_task` semantics and versioning

**Done when:** Any change among the seven segments OR among `user_prompt`/`cache_prompt`/`*_b`/`*_c`/`*_d`/`nocache_prompt`/`system_prompt` bumps a new row version (current=1) like today’s **content versioning** branch; purely `agent_id` / `run_next` metadata updates behave like today.

1. Extend `save_agent_task` kwargs with optional `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d` (same typing style as existing cache fields—`Optional[str]` coerced via `existing` pattern).
2. Widen SELECT of current row to read all seven segments plus `task_key_uuid`, `agent_id`, `run_next`.
3. On insert for new tasks, set new columns to `(x or "").strip()` or `''` consistent with sibling fields.
4. Compute `content_changed` as inequality on **pairwise** normalized strings for: `user_prompt`, `cache_prompt`, `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d`, `nocache_prompt`, `system_prompt` (match existing strip rules: `system_prompt` uses `.strip()` when comparing like current code).
5. Copy `run_next` / `agent_id` behavior unchanged from current implementation.
6. Metadata-only branch: allow updating new cache columns via `UPDATE` when `content_changed` is false ONLY if introducing new kwargs `None`-means-no-op matches today—that is, unchanged.
7. `python3 -m py_compile src/data/database.py`

---

#### Stage 3: `list_candidate_tasks` and sync

**Done when:** List rows expose char lengths useful to admin `_enrich_tasks`; `sync_agent_tasks` inserts include new columns defaulted empty.

1. Extend `SELECT` in `list_candidate_tasks` with `LENGTH(cache_prompt_b|c|d)` as `cache_prompt_b_len`, `cache_prompt_c_len`, `cache_prompt_d_len`.
2. In `sync_agent_tasks` INSERT tuple, extend column list matching fresh CREATE semantics (seven empty prompt fields plus system/run_next defaults).
3. `python3 -m py_compile src/data/database.py`

---

#### Stage 4: Admin API payload

**Done when:** `GET /api/admin/tasks/<task_key>` JSON includes keys `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d` from `get_agent_task`; `PUT` accepts same keys (`body.get(...)`) forwarded to `save_agent_task`; miss keys → pass `None` so **no unintended wipe** consistent with PUT today.

1. Extend `database.save_agent_task(...)` invocation in **`update_task`** with `cache_prompt_b=body.get("cache_prompt_b"), ...`.
2. Grep codebase for **`save_agent_task(`** beyond this file—update any callers in the **same Astral codebase** touched by this ticket (typically none else); if spike scripts cite old signature, defer—spikes exempt but must compile if touched.
3. `python3 -m py_compile src/ui/api/api_admin.py`

---

#### Stage 5: `_enrich_tasks` cache metrics alignment

**Done when:** List API remains backward-compatible keys; admins see realistic cache mass when multiple cache slots populated.

1. Compute `cache_raw_total = sum(LENGTH(...))`-equivalent server-side via `database.list_candidate_tasks` new len fields (`cache_prompt_len` + `_b/_c/_d`).
2. For `$`-token cleanliness, build `combined_cache_probe = concatenate(resolve_tokens(blockA), …, resolve_tokens(blockD))` using real `resolve_tokens` per block with same `cd`, `task_key`, `_cc` as today’s single-block path; `task_ready` false if **any** block still has unresolved `{$TOKEN}` pattern (reuse same regex as line ~180).
3. `parsed_cache_tokens = len(combined_cache_probe) // CHARS_PER_TOKEN` when `task_ready`.
4. `total_cache = system_tokens + parsed_cache_tokens` when `task_ready` else fall back to `system_tokens + base_cache_tokens` using **raw** sum of four cache lengths (document in code comment **two-line** why approx is acceptable when unresolved tokens).
5. `python3 -m py_compile src/ui/api/api_admin.py`

---

#### Stage 6: Runtime build handoff note (no `agent.py` edits here)

**Done when:** Plan doc states explicitly: **AST-455** must read `cache_prompt_b/c/d` from `agent_task_row`; until then production only uses block A in `do_task`—acceptable intermediate because **this ticket** only promises persistence + admin API per child scope.

1. Add a short **Handoff to AST-455** bullet in a Linear comment at Code Complete (builder), not in this plan body.

---

#### Self-Assessment

**Scope:** `MAJOR-CHANGE` — Touches authoritative `database.py` schema + admin task API contract; multiple integration points but one vertical slice (persistence).

**Conf:** `Medium` — Follows existing `save_agent_task` versioning and ALTER patterns; multi-column versioning is detailed but not novel.

**Risk:** `Medium` — Migration mis-ordered ALTER or missed INSERT column tuple causes runtime DB errors for admin saves; mitigated by compile check + Betty tests on affected paths later.

---

#### Plan vs `ASTRAL_CODE_RULES.md`

| Section | Compliance |
|---------|-------------|
| §1.3 DRY | Reuse `_ensure_agent_task_schema` ALTER cascade; extend `save_agent_task` branches instead of duplicate upsert helpers. |
| §2.1 config | Do **not** add prompt text to `config.py`; segmentation is DB-backed per parent spec. |
| §2.4 batch processing | Not applicable—no dispatcher changes. |
| §2.6 state machine | Not applicable—no transitions. |
| §3.3 imports | Database changes only touch data + thin API (allowed). |
| §3.5 naming | Column names lowercase snake per existing `agent_task` fields. |

No conflicts forcing `conf-!!-NONE`.

---

#### Review (implementation stub)

Built by Ada (`dev-ada`). Product commits on `origin/sub/AST-453/AST-454-explicit-cache-block-references-for-tasks-agent-task-seven-segment-persistence` via cherry-pick; update the commit hash(es) below after publish.

**Branch:** `sub/AST-453/AST-454-explicit-cache-block-references-for-tasks-agent-task-seven-segment-persistence`

**Commits:** `f8b263d10e5bce455269ed9c173a2ca175957f7a` (product `feat(AST-454)` cherry-picked to this sub ref)

#### Review

**Diff:** `git diff origin/dev...origin/ftr/AST-454` · **Baseline tip (pre-this-doc):** `69f69c17f455fcbf0bffe53c79457e8d805765b7`

##### What’s solid

- `agent_task` inventory + `_ensure_agent_task_schema` ALTERs for `cache_prompt_b|c|d`; v1 → v2 INSERT column list aligns with bindings.
- Versioning expands to all seven segments; stripping rules for cache B/C/D via `_strip_seg` match plan; dropping ad-hoc `system_prompt` updates on non-versioning UPDATE path matches “system changes version” semantics.
- `list_candidate_tasks` length aggregates feed `_enrich_tasks` joined probe (`\n---\n`) and `task_ready` / approximate `total_cache` behavior documented in-admin.
- `update_task` passes through optional B/C/D with `None` → leave-untouched parity with PUT semantics.

##### Issues

None **fix-now**. No rubric-aligned blockers (**ASTRAL_CODE_RULES** §1 / database bind review).

##### Recommended actions

| Priority | Audience | Action |
|----------|-----------|--------|
| Advisory | UAT / operators | Smoke one migrated legacy task (single `cache_prompt` only) round-trip GET/PUT/admin list enrichment per AC2. |

---

#### Resolution

**Date:** 2026-05-23

**Versus Radia (`review-astral`, Linear comment thread):**

- **Fix-now:** none (counts 0). No product deltas required for acceptance of that review bucket.
- **Discuss / Advisory:** Acknowledged — UAT/operators should smoke one migrated legacy-only-cache-A task GET/PUT + list enrichment (AC2 advisory); deferred to Susan’s batch UAT, not gated on further code here.
- **Plan doc:** Radia’s **`docs(AST-454): Radia review — seven-segment persistence`** landed from `origin/ftr/AST-454` (**`b8c89791`**) onto `dev-ada`; this section records closure from **resolve-astral** before **User Testing**. **Publish ref:** **`origin/ftr/AST-454`** (Cherry picks for prep-uat vs parent **AST-453**).

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/data/database.py` | Extend `agent_task` header inventory; `_ensure_agent_task_sc | `f8b263d10` |
| ✓ | `src/ui/api/api_admin.py` | `update_task`: accept/pass `cache_prompt_b`, `cache_prompt_c | `f8b263d10` |

### AST-455 — Explicit cache block references for tasks: caller tokens and five-segment prompt assembly

#### Summary

Upgrade `do_task` / `preview_prompt` / admin preview so **up to five** Anthropic `system` blocks carry `cache_control` ephemerally: resolved `system_prompt` plus each non-empty cache block A–D from `agent_task` (columns `cache_prompt`, `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d` per **AST-454**). No-cache and user segments stay **non-cached** user-message blocks. Replace AST-304’s implicit `CACHE_BLOCK_*` chain slot remapping with **caller-prefixed** tokens `CALLER_SYSTEM`, `CALLER_CACHE_A`–`CALLER_CACHE_D`, `CALLER_RESPONSE` in `TOKEN_SOURCES` / `chain_context`; remove `CACHE_BLOCK_A`–`CACHE_BLOCK_D` entries. Build `chain_context` for the next hop only from those caller-resolved strings plus response—**no** automatic promotion of callee no-cache/user into chain keys. Admin preview must match production for at least one multi-hop `run_next` chain when optional chain simulation query params are supplied.

#### Stage 1: Config token registry

**Done when:** `resolve_tokens('{$CALLER_SYSTEM}', ..., chain={'CALLER_SYSTEM':'xy'})` yields `xy`; `{$CACHE_BLOCK_A}` untouched (not in TOKEN_SOURCES) remains literal `{...}` substring per forward-compat rule existing in `resolve_tokens` for unknown names—or confirm current behavior strips nothing.

1. Implement registry edits exactly as Files table; preserve alphabetical sort in `get_tokens()` consumer behavior—**new** `get_manage_tasks_chain_tokens()` **only** for Manage Tasks picker surface.
2. Ensure **no** `NO_CACHE_BLOCK` or `USER_PROMPT` keys exist in `TOKEN_SOURCES` (parent AC4).
3. `python3 -m py_compile src/utils/config.py`

---

#### Stage 2: Assembly + storage

**Done when:** Non-empty cache B/C/D produce distinct API system blocks **and** distinct `agent_data` rows labeled `CACHE_B`/`CACHE_C`/`CACHE_D` when `store_agent_data` path exercised.

1. Factor assembly from `_assemble_blocks` into `_assemble_blocks_seven_segment(system_text, caches: tuple[str|None, …4], nocache_text, live_text, user_text, …)` returning same tuple shape `(system_blocks, user_blocks, runtime_prompt, no_cache_prompt_tokens, no_cache_live_tokens)` **with** runtime_prompt ledger entries labeled per block consistently (`cache_a`, etc.)—maintain cardinality rules for tests expecting list shape (extend labels in obvious pattern).
2. **Do not** inject hardcoded headings like `--- CACHED CONTEXT ---` into **cached** segments unless parent issue demands—parent says separate cached API blocks; operators own visible separators inside DB text.
3. For **no-cache** + **live** segments, reuse existing prefix strings (`--- ADDITIONAL CONTEXT ---`, `--- CONTENT ---`) verbatim to avoid churn.
4. Update `_store_prompt_blocks` signatures to accept optional `cache_b_text`, … or a list—store each with proper `BLOCK_TYPES` enum strings already defined.
5. `python3 -m py_compile src/core/agent.py`

---

#### Stage 3: `do_task` resolution + chain pass-through

**Done when:** Two-hop chain with markers in each caller segment flows into callee `{$CALLER_*}` expansions; missing chain keys log-and-empty like today’s chain branch.

1. After loading `agent_task_row`, compute:
   - `raw_system`, `raw_ca`, `raw_cb`, `raw_cc`, `raw_cd`, `raw_nocache`, `raw_user` from DB keys `system_prompt`, `cache_prompt`, `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d`, `nocache_prompt`, `user_prompt` (`.get` safe if column absent pre-454 merge—post 454 required).
2. Resolve in order: `system_content = resolve_tokens(raw_system, …)` using `_cc`; same for each cache block and nocache/user (chain_context available for callee tokens on **this** hop).
3. Feed **resolved** `system_content` + four cache resolved strings into assembly (None/empty → skip block).
4. Replace `_chain_tokens_for_next_hop` body: map **only** `CALLER_SYSTEM` = `system_content`, `CALLER_CACHE_A` = resolved cache A string, …, `CALLER_RESPONSE` from parsed output using existing JSON/string rules in current function.
5. Remove assignment to legacy `CACHE_BLOCK_*` keys entirely.
6. **Three-hop explicit test scenario (manual + unit if permitted without touching `tests/`):** builder proves hop2 cache A contains `{$CALLER_RESPONSE}` text so hop3 sees it via `CALLER_CACHE_A`—document replication steps in Code Complete comment (Betty may formalize).
7. `python3 -m py_compile src/core/agent.py`

⚠️ **Decision:** Non-chained runs pass `chain_context=None`; callee tokens empty → warnings only; **no** silent fallback to legacy slot mapping.

---

#### Stage 4: Admin preview parity

**Done when:** `GET /api/admin/tasks/<task_key>/preview?candidate_id=…&chain_sim=1` (exact param names chooser in implementation) returns JSON including **per-segment** resolved strings matching `preview_prompt` / `do_task` ordering for at least: `system`, `cache_a`, `cache_b`, `cache_c`, `cache_d`, `nocache`, `user` keys (add keys only if non-empty to reduce payload bloat **or** always include—pick one in code and document here in Revisions if changed).

**Revisions:** Always include segment keys (`cache_a`…`cache_d`, legacy `cache` = A). Multi-hop simulation: **`chain_sim=1`** (`true`/`yes` accepted) plus optional **`simulate_parent=<task_key>`**, **`simulate_parsed=<payload>`**, and overlays **`chain_ctx_<TOKENNAME>=`** (example: `chain_ctx_CALLER_RESPONSE=...`).

1. Implement **optional** multi-hop simulation: when query includes parent task key + marker payload OR when `simulate_caller_*` args present, build `chain_context` dict without calling Anthropic (mirror `do_task` resolution for caller hop only).
2. Reuse `preview_prompt` core by lifting shared resolver into private helper if needed to avoid duplication >10 lines.
3. `python3 -m py_compile src/ui/api/api_admin.py src/core/candidate.py`

---

#### Stage 5: Timesheet / token accounting sanity

**Done when:** `no_cache_prompt_tokens` / `no_cache_live_tokens` still computed from character lengths of **non-cached** segments only; cached segments continue contributing via Anthropic cache fields—**no** double counting after split.

1. Recompute `no_cache_prompt_tokens` using `len(nocache_content)+len(user_content)` chars // `CHARS_PER_TOKEN` matching old formula scope (live separate).
2. `python3 -m py_compile src/core/agent.py`

---

#### Self-Assessment

**Scope:** `MAJOR-CHANGE` — Core `do_task` assembly + global token registry + admin preview contract.

**Conf:** `Medium` — Clear parent spec; careful ordering of resolve vs chain merge prevents subtle bugs.

**Risk:** `HIGH` — Regression on consult dispatch + artifact chains if assembly or chain_context wrong; requires strict compile + Betty integration tests post-build.

---

#### Plan vs `ASTRAL_CODE_RULES.md`

| Section | Compliance |
|---------|------------|
| §1.3 DRY | Shared preview/resolution helper if duplication emerges; keep assembly in `agent.py`. |
| §2.1 config | Token registry lives in `config.py`; no secret env. |
| §2.4 batch | Unaffected. |
| §2.6 state machine | Unaffected. |
| §3.3 imports | UI → core only for preview helper usage. |

No `conf-!!-NONE`.

---

#### Review (implementation stub)

Built by Ada (`dev-ada`). Cherry-picked to **`origin/sub/AST-453/AST-455-explicit-cache-block-references-for-tasks-caller-tokens-and-five-segment-prompt-assembly`**; update commit hash(es) below after publish.

**Branch:** `sub/AST-453/AST-455-explicit-cache-block-references-for-tasks-caller-tokens-and-five-segment-prompt-assembly`

**Commits:** `c62bff946fb0b1a6cbc392b5ec4434dffd959b6e` (product `feat(AST-455)` on `dev-ada`; cherry-pick to this sub ref)

#### Review

**Diff:** `git diff origin/dev...origin/ftr/AST-455` · **Code tip reviewed (pre-this-doc):** `39a5ae4d489880fb9bf27f2f4771c3acf94e9653`

##### What’s solid

- `TOKEN_SOURCES`: `CACHE_BLOCK_*` retired; caller keys + `tests/component/utils/test_config.py` prove legacy `{$CACHE_BLOCK_A}` stays literal (**D3**/forward-compat as planned).
- `get_manage_tasks_chain_tokens()` aggregates all `chain` entries; excludes nonexistent `NO_CACHE_BLOCK`/`USER_PROMPT` keys (**AC surface** aligned).
- `_assemble_blocks_seven_segment`, `_store_prompt_blocks`, and `do_task` read four DB cache columns consistently; `_chain_tokens_for_next_hop` maps **resolved** plaintext only (**AST-454** handoff satisfied).
- `preview_prompt` + `preview_task_prompt`/`simulated_chain_context_for_preview` + `/tasks/meta/chain_tokens` and query-driven chain simulation mirror plan Stage 4; UI layer stays thin Flask wiring.

##### Issues

None **fix-now**. Accepted tolerances cite plan + comments: omission of injected `--- CACHED CONTEXT ---` on cached segments is **explicit Stage 2** (“operators own separators”).

##### Recommended actions

| Sev | Audience | Finding |
| --- |----------|---------|
| **discuss** | Prompt authors | Cached Anthropic payloads no longer prepend `--- CACHED CONTEXT ---`; delimiter must live in segment text where operators still want it. |
| **discuss** | Operators | Migrate any lingering `{$CACHE_BLOCK_*}` references to `{$CALLER_*}`; literals otherwise stay unresolved (**ASTRAL_TEST_BIBLE §7.13o**). |
| Advisory | Historical docs | Feature docs under `docs/features/artifacts/` still describe AST-304 `CACHE_BLOCK_*` wiring—expected archival drift alongside AST-455. |

---

#### Resolution

**Date:** 2026-05-23

**Versus Radia (`review-astral`, Linear comment thread):**

- **Fix-now:** none (counts 0). No targeted product changes landed in this **`resolve-astral`** pass — reviewed tip (**`39a5ae4d`**) matched plan tolerances documented above.
- **Discuss (Radia buckets 2 × non-blocking):** Noted without code churn — prompts that relied on historically injected separators must fold delimiters into stored segment copy; callers must migrate `{$CACHE_BLOCK_*}` → `{$CALLER_*}` (`§7.13o`). UAT/playbook outreach is operator/Susan-facing, outside this cherry-pick.
- **Advisory (historical `docs/features/artifacts/` drift):** Logged — no doc sweep here (archival drift only per review).
- **Plan doc:** Radia’s **`docs(AST-455): Radia review …`** from `origin/ftr/AST-455` (**`77c1bfd8`**) merged to `dev-ada`; **`## Resolution`** closes **Review Posted**. **Publish ref:** **`origin/ftr/AST-455`**. Parent **AST-453**.

#### Files changed (plan vs actual)  _(no commit trail — plan only)_

| | file | planned | actual |
|---|---|---|---|
| · | `src/utils/config.py` | `TOKEN_SOURCES`: remove `CACHE_BLOCK_A`–`D`; add `CALLER_SYS | — |
| · | `src/core/agent.py` | Replace `_assemble_blocks` usage with a new helper (e.g. `_a | — |
| · | `src/core/candidate.py` | `preview_task_prompt`: support optional query-driven chain s | — |
| · | `src/ui/api/api_admin.py` | `task_tokens`: return `get_manage_tasks_chain_tokens()` inst | — |

### AST-456 — Explicit cache block references for tasks: Manage Tasks seven-segment UI

#### Summary

Extend **Manage Tasks** (`src/ui/frontend/src/pages/AdminTaskPrompts.tsx`) so each task exposes **seven** ordered editors: **System Prompt** → **Cache Block A** → **Cache Block B** → **Cache Block C** → **Cache Block D** → **No Cache Block** → **User Prompt**. Reuse `TokenTextarea` / `TabbedTextArea` / `CollapsiblePanel` patterns already on the screen. Persist through admin REST PUT with fields from **AST-454** (`cache_prompt` as slot A plus `cache_prompt_b|c|d`). Token picker consumes **chain-safe** registry from **`/api/admin/tasks/meta/tokens`** (or dedicated endpoint emitted in **AST-455**) so operators never see phantom `{$NO_CACHE_BLOCK}` / `{$USER_PROMPT}` selectable entries—those literals stay impossible if absent server-side.

#### Stage 1: Types and modal edit state wiring

**Done when:** TypeScript builds (`npx tsc -b --noEmit`); modal tracks seven strings independently.

1. Extend `AgentTask` with optional `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d` strings (mirror server).
2. Add React state mirrors `editCacheB`, … initialized from `full_task` fetch (`GET task` returns complete row once modal opens—already pattern for system/user/cache).
3. Expand `TabKey` / preview unions to `'cache_b'|'cache_c'|'cache_d'` etc.
4. Map tab order exactly per parent enumerated list—**numbers in UI labels** acceptable (`Cache Block B`).

---

#### Stage 2: Fetch + save payloads

**Done when:** Save issues single PUT including all seven fields plus existing keys; reloading modal shows persisted text.

1. Modify save handler assembling JSON body `{ system_prompt, user_prompt, cache_prompt, cache_prompt_b, cache_prompt_c, cache_prompt_d, nocache_prompt, … }`.
2. Guard: missing server fields ⇒ treat as empty string on read.
3. On successful save, toast + `loadAll()` like today.

---

#### Stage 3: Preview tabs + token picker

**Done when:** Preview modal shows tabs for populated segments parity with server keys returned from preview endpoint (**AST-455** expands keys)—if backend returns fewer keys pre-merge, gates behind optional chaining stub is **disallowed**—coordinate merge order via Linear comment **if** sibling pending.

1. When opening preview after AST-455 ships, iterate ordered list of segment keys expecting new API shape documented in sibling plan.
2. `TokenTextarea`: load allowed tokens endpoint per **Decision** below.

⚠️ **Decision:** Prefer dedicated `chain_tokens` endpoint from AST-455; if unavailable during build window, temporarily filter forbidden names client-side and post `[qa-handoff]` to Betty if mismatch suspected.

---

#### Stage 4: Layout + accessibility regressions spot-check

**Done when:** No React console errors opening modal; collapsed panels reopen on same task edit.

1. Respect `ADMIN_TASK_PROMPTS_DEFAULT_PANEL_LS` keyed by logical tab—but expand allowed stored values accordingly or migrate stale localStorage gracefully (silent fallback `'user'` if unknown key).
2. Keep `runNextGraphIsAcyclic` unaffected.

---

#### Self-Assessment

**Scope:** `Single-Component` — One React module + minor API glue.

**Conf:** `high` — Mirrors existing Manage Tasks UX; sibling tickets define payloads.

**Risk:** `Medium` — Token list drift if API not coordinated with AST-455; mitigated by integration handoff ordering (AST-454 before UI save testing).

---

#### Plan vs `ASTRAL_CODE_RULES.md`

| Section | Compliance |
|---------|-------------|
| §3.5 UI stack | Maintain config-driven REST; avoid duplicating resolver logic client-side beyond filtering. |

No conf-!!-NONE.

---

#### Revisions / implementation notes

**Stage 3 (token picker):** `AdminTaskPrompts` loads `/api/admin/tasks/meta/tokens` and `/api/admin/tasks/meta/chain_tokens` (AST-455); merges uniquely and sorts A–Z for `TokenTextarea`. If `chain_tokens` responds non-OK, merge uses `meta/tokens` only.

**Preview tabs:** Ordered per parent segments; **`cache_a`** from preview API with legacy **`cache`** fallback for block A only.

---

#### Review (implementation stub)

Built by Ada (`dev-ada`). Cherry-pick to **`origin/sub/AST-453/AST-456-explicit-cache-block-references-for-tasks-manage-tasks-seven-segment-ui`**; update hashes after publish.

**Branch:** `sub/AST-453/AST-456-explicit-cache-block-references-for-tasks-manage-tasks-seven-segment-ui`

**Commits:** `1532eaa6c72317efbd4ec5840b1e7466375154f9` (product `feat(AST-456)` on `dev-ada`); commit immediately after **may** carry `docs(AST-456)` plan stub — cherry-pick both when present onto this ref.

#### Review

**Diff:** `git diff origin/dev...origin/ftr/AST-456` · **Code tip reviewed (pre-this-doc):** `55ca2cc6fcb8c6b0b973ee02815949b8e10f299a`

##### What’s solid

- Seven collapsible editors follow parent ordering (system → cache A–D → no-cache → user); save payload emits all AST-454 fields alongside existing keys (`AdminTaskPrompts.tsx`).
- `mergedAdminTokenAutocomplete` pulls `/tasks/meta/tokens` + `/tasks/meta/chain_tokens`; non-OK chain endpoint gracefully falls back (**Revisions § Stage 3**).
- Preview tabs match backend keys with `previewField()` bridging `cache`→`cache_a` (**AST-455** compatibility).

##### Issues

None **fix-now**; no **`src/ui`** `data`/`external` leakage or hardcoded forbidden chain token names (**G1** / registry stays server-side).

##### Recommended actions

| Priority | Audience | Action |
|----------|-----------|--------|
| Advisory | UAT | Rotate default expanded panel dropdown across all seven tabs after shipping to confirm persisted `ADMIN_TASK_PROMPTS_DEFAULT_PANEL_LS` stays valid (unknown keys ignored; default panel falls back to **user**, matching `readDefaultEditPanel`). |

---

#### Resolution

**Date:** 2026-05-23

**Versus Radia (`review-astral`, Linear comment thread):**

- **Fix-now:** none (counts 0). No UI code changes needed for this **`resolve-astral`** pass.
- **Advisory:** UAT/default-panel **`readDefaultEditPanel`** persistence spot-check deferred to Susan’s **`prep-uat` / batched smoke** alongside other Manage Tasks regressions (`§ Review` Recommended actions unchanged in product).
- **Plan doc:** Radia’s **`docs(AST-456): Radia review …`** from `origin/ftr/AST-456` (**`64059250`**) merged to `dev-ada`; **`## Resolution`** advances ticket toward **User Testing**. **Publish ref:** **`origin/ftr/AST-456`**. Parent **AST-453**.

#### Files changed (plan vs actual)  _(no commit trail — plan only)_

| | file | planned | actual |
|---|---|---|---|
| · | `src/ui/frontend/src/pages/AdminTaskPrompts.tsx` | d`; refactor tab typing from four tabs to seven (`TabKey` un | — |
| · | `src/ui/api/api_admin.py` | If AST-455 added `tasks/meta/chain_tokens`, consume it for t | — |
