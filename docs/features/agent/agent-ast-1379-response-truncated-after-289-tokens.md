# AST-1379 — Response truncated after 289 tokens?

**Component:** agent  
**Children:** AST-1380, AST-1383  
**Linear archived:** AST-1379 2026-08-31; AST-1380 2026-08-31; AST-1383 2026-08-31

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-14 17:49 | AST-1380 | docs | `45bb9982d` | plan-fix — craft_get_rubric truncation hole |
| 2026-08-14 17:52 | AST-1380 | code | `64042fb23` | craft rubric thinking-off + failure RESPONSE banner |
| 2026-08-14 17:55 | AST-1380 | docs | `bdd310d4d` | docs-acceptance — test work on sibling gap AST-1383 |
| 2026-08-14 17:55 | AST-1380 | docs | `d5ef26eba` | Radia review-fix DISCUSS — gap AST-1383 owns test debt |
| 2026-08-14 17:55 | AST-1383 | docs | `bdd310d4d` | docs-acceptance — test work on sibling gap AST-1383 |
| 2026-08-14 17:55 | AST-1383 | docs | `d5ef26eba` | Radia review-fix DISCUSS — gap AST-1383 owns test debt |
| 2026-08-14 17:57 | AST-1383 | docs | `190870f4c` | plan-fix — craft truncation test gap |
| 2026-08-14 18:00 | AST-1383 | merge-tests | `8dceeec4b` | origin/tests ba7195aac4adbfe742aa3e9b215f0ef546342ee8 |
| 2026-08-14 18:00 | AST-1383 | test | `ba7195aac` | bug-repro — craft thinking-off + Provider-failed RESPONSE banner |
| 2026-08-14 18:04 | AST-1383 | docs | `e02156d4e` | Radia review-fix CLEAN |
| 2026-08-14 18:05 | AST-1383 | docs | `8c9edcca2` | Resolution — vocabulary code() + clean resolve |
| 2026-08-14 18:05 | AST-1383 | resolve | `a07015e3a` | — clean |
| 2026-08-14 18:05 | AST-1383 | code | `d2f38916e` | no product delta — gap is test/bible only |
| 2026-08-14 18:06 | AST-1379 | docs | `1e38a18f2` | mirror epic registry Threads |
| 2026-08-14 18:15 | AST-1383 | test | `21136c84d` | strip orphan AST-1383 agent test/bible from publish tip |
| 2026-08-31 14:15 | AST-1380 | docs | `509ff5fb3` | archive Linear issue content |
| 2026-08-31 14:15 | AST-1383 | docs | `d735c11b5` | archive Linear issue content |
| 2026-08-31 14:19 | AST-1379 | docs | `1df1f36f2` | archive Linear issue content |

## Epic — AST-1379

_Archived: 2026-08-31 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1379/response-truncated-after-289-tokens · Status at archive: Archive · Project: Astral Agent · Assignee: chuckles · Priority / estimate: Urgent / —_

### As-is

`craft_get_rubric` for candidate `abrams` (batch `craft_get_rubric-ff19fa20-5f6d-469c-a1bf-5c09b4574948`) stores a RESPONSE whose `block_data` cuts mid-criteria string after ~289 tokens (`token_size: 289`). `agent_performance.status` is `success` with a full `vector_reviews` list, but `agent_payload.criteria` is incomplete JSON (first criterion `content` ends mid-sentence). Downstream parse/use sees truncated rubric output treated like a finished hop.

### To-be

A successful `craft_get_rubric` RESPONSE is complete, parseable JSON with every crafted criterion fully written — or the hop fails loudly under the existing `max_tokens` / unusable-response failure class instead of persisting a truncated payload as success.

### Proposed steps

1. Confirm whether this run hit provider `stop_reason=max_tokens` (or equivalent) and what `max_tokens` / brain setting `do_task` actually sent for this hop (AST-903 shipped a `CRAFT_RUBRIC_MAX_TOKENS=32000` floor for craft rubric UI keys — check regression or a path that bypasses it).
2. If the floor is skipped or undercut on this entry path, restore/apply it for `craft_get_rubric` (and sibling craft rubric keys if the same hole exists).
3. Ensure truncated JSON cannot land as `agent_performance.status=success` + partial `agent_payload` — hard-fail before persist when stop is max_tokens / content is unterminated, matching AST-903's provider gate.
4. Re-run `craft_get_rubric` for `abrams` (or equivalent) and verify a full criteria array persists with RESPONSE `token_size` well above a mid-vector cut.

### Evidence (filing dump, condensed)

* Title symptom: response truncated after 289 tokens.
* `task_key`: `craft_get_rubric`
* `entity_id`: `abrams`
* RESPONSE `agent_data_id`: `craft_get_rubric-ff19fa20-5f6d-469c-a1bf-5c09b4574948-response-86ff123a40218dbb`
* RESPONSE `token_size`: `289`
* Cut point (first criterion `content`): ends at `…even though no title` mid-grade row; remaining criteria never written.

#### Comments


##### chuckles — 2026-08-15T00:42:10.867Z

Ancestor candidates (ranked — pick one, ask about one, or reject the set):

1. **AST-903** (parent **AST-900**) — strongest match. Prior UAT: `craft_get_rubric` truncated mid-`criteria[].content`, `Unterminated string` / success-shaped payload. Shipped `CRAFT_RUBRIC_MAX_TOKENS=32000` floor + provider JSON `max_tokens` hard-fail. This looks like a regression or a path that misses that floor.
2. **AST-1377** / parent **AST-1376** — live neighbor. Plan explicitly parked `craft_do_rubric max_tokens / truncated JSON` as **out of epic**; same symptom family named next to current agent_data ensure work.
3. **AST-1190** (parent **AST-1164**, archived) — empty/unusable provider response surfacing; shares `max_tokens` failure vocabulary with the craft truncate path, but owns hollow/empty classification not craft token budget.
4. **AST-1191** (parent **AST-1164**, archived) — artifact hop failure release + debug trail for provider failures including `max_tokens`; downstream handling, not the truncate root.
5. **AST-1368** — wires Ideal Day into craft prompts including `craft_get_rubric`; same task key, different problem (prompt tokens, not RESPONSE truncation).

Reply with a pick (or “none / orphan mini-parent”) and reassign Chuckles when ready; move to Todo to release bug-fix.

---

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-1380 — Fix craft_get_rubric RESPONSE truncation (289-token cut)

_Archived: 2026-08-31 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1380/fix-craft-get-rubric-response-truncation-289-token-cut · Status at archive: Archive · Project: Astral Agent · Assignee: ada · Priority / estimate: None / 3 · Blocked by / blocks / related: parent: AST-1379_

#### What this implements

Restore complete `craft_get_rubric` JSON output (or hard-fail on truncation) so a RESPONSE cannot land as success with a mid-criteria cut after ~289 tokens. Confirm whether AST-903's `CRAFT_RUBRIC_MAX_TOKENS` floor / provider `max_tokens` hard-fail still applies on this entry path; fix the hole if the floor is skipped or undercut.

#### Acceptance criteria

- [X] A `craft_get_rubric` hop that would otherwise truncate mid-`criteria[].content` either completes with full parseable JSON or fails under the existing `max_tokens` / unusable-response failure class — never `agent_performance.status=success` with partial payload.
- [X] The path that produced batch `craft_get_rubric-ff19fa20-5f6d-469c-a1bf-5c09b4574948` for candidate `abrams` (RESPONSE `token_size: 289`) applies the craft-rubric token floor (or equivalent budget) so a full criteria array can be written.
- [X] Re-run (or equivalent fixture) shows a complete criteria array persisted, not a mid-grade-row cut.

#### Proposed change (make-fix)

- [X] Confirm hop / hole: AST-903 floor + max_tokens hard-fail still present; abrams signature matches thinking-budget starvation (Atlas Big) + success-shaped failure RESPONSE.
- [X] Decision A: force DeepSeek `thinking=False` for `CRAFT_RUBRIC_UI_TASK_KEYS` in `do_task` (shared max_tokens with JSON answer).
- [X] Prefix provider-failure RESPONSE audit bodies (`Provider failed …`) so raw `agent_performance.status=success` envelopes are not mistaken for finished hops.
- [X] AST-903 floor + provider JSON max_tokens hard-fail left intact; generate/REQUESTED_ARTIFACTS still fail closed on `success=False`.

#### Boundaries

* Does not redesign GET rubric grading semantics or craft prompt prose except as required for token/budget correctness.
* Does not own unrelated hollow/empty provider classification (AST-1190) or hop-release debug trail (AST-1191) beyond consuming existing failure classes.
* Does not revive archived AST-903 as a parent — this is a fresh mini-epic off `origin/dev`.
* Betty TESTS:REVISE → sibling gap AST-1383 (tests not landed here).

#### Notes for planning

* Bug parent: AST-1379 (orphaned mini-parent). Approved ancestor context: AST-903 (`docs/features/consult/ast-903-uat-craft-get-json-parse.md`) — prior craft_get truncate + `CRAFT_RUBRIC_MAX_TOKENS=32000` + JSON max_tokens hard-fail. Ticket archived; no related-issue link.
* Neighbor AST-1377 explicitly parked `craft_do_rubric max_tokens / truncated JSON` as out of epic.
* As-is/to-be/proposed steps live on AST-1379 Description.

##### Comments


###### radia — 2026-08-15T00:55:22.804Z

[review-fix] DISCUSS (no fix-now)

Decision A (craft-rubric DeepSeek thinking off) + provider-failure RESPONSE banner look solid; AST-903 max_tokens floor/gates untouched.

Process discuss: hop-confirm paper trail missing; TESTS:REVISE lives on sibling gap AST-1383 (not this sub). Chuckles taking clean-review → User Testing; gap must ship before parent finish-up.

###### joan — 2026-08-15T00:50:26.164Z

[board-joan]  CANON: OK

context_tokens≈12000

###### betty — 2026-08-15T00:50:24.169Z

[board-betty] TESTS: REVISE
What: docs/test-bible/core/agent.md — missing coverage — Decision A thinking-off / truncated success RESPONSE for craft rubrics (AST-903 floor+max_tokens gate present; abrams path uncovered)

###### ada — 2026-08-15T00:49:13.093Z

`origin/sub/AST-1379/AST-1380-fix-craft-get-rubric-truncation` @ `45bb9982d062149a5a9ed5bd218d60524f7e149c` · truncation hole planned

---

_Implementation detail may live in git history on `origin/dev`._

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| + unplanned | `src/core/agent.py` | — | `64042fb23` |

### AST-1383 — Gap: craft rubric truncated-success RESPONSE coverage (agent bible/tests)

_Archived: 2026-08-31 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1383/gap-craft-rubric-truncated-success-response-coverage-agent-bibletests · Status at archive: Archive · Project: Astral Agent · Assignee: ada · Priority / estimate: None / 2 · Blocked by / blocks / related: parent: AST-1379_

#### What this implements

Close the test/bible gap flagged by fix-board `[board-betty] TESTS: REVISE` on AST-1380: add coverage in `docs/test-bible/core/agent.md` (and matching component tests) for Decision A — thinking-off / truncated success RESPONSE on craft rubrics (AST-903 floor + max_tokens gate present; abrams-shaped path uncovered).

#### Acceptance criteria

- [X] Bible + tests cover craft rubric RESPONSE truncation treated as success / thinking-off path named in Betty's board verdict.
- [X] A repro-shaped case exists for truncated craft_get_rubric RESPONSE (`token_size` mid-criteria cut) that fails pre-fix and passes once AST-1380's product fix lands (or documents the hard-fail gate).
- [X] Publish to this child's `sub/*` only (Betty/astral-tests conventions via fix-lane stages as applicable).

#### Proposed change (make-fix)

- [X] No product code — AST-1380 Decision A + failure banner already on tip (`64042fb2` ancestor).
- [X] Betty bible + `TestAst1380CraftRubricThinkingOffAndFailureBanner` on sub via `merge-tests(AST-1383)` @ `8dceeec4`.
- [X] `[bug-repro]` class green against current tip (3 passed).

#### Boundaries

* Does not re-implement the product fix on AST-1380; lands test/bible work only.
* Does not change canon (Joan board was CANON: OK).

#### Notes for planning

* Source verdict: AST-1380 `[board-betty] TESTS: REVISE` — docs/test-bible/core/agent.md — Decision A thinking-off / truncated success RESPONSE for craft rubrics.
* Sibling fix child: AST-1380. Ancestor doc: docs/features/consult/ast-903-uat-craft-get-json-parse.md.

##### Comments


###### ada — 2026-08-15T01:05:40.672Z

`origin/sub/AST-1379/AST-1383-gap-craft-get-truncation-tests` @ `8c9edcca26b2e7867db7b327c25d87ca79cb1ce0` · validate-sub-log ok

###### radia — 2026-08-15T01:04:29.196Z

[review-fix] CLEAN

Gap bible + Decision A / failure-banner tests lock AST-1380. [bug-repro] OK. No product delta. → User Testing (clean-review shortcut).

###### ada — 2026-08-15T01:02:18.955Z

`origin/sub/AST-1379/AST-1383-gap-craft-get-truncation-tests` @ `8dceeec4` · repro green, no product delta

###### betty — 2026-08-15T01:01:10.165Z

[bug-repro]
`origin/sub/AST-1379/AST-1383-gap-craft-get-truncation-tests` @ `8dceeec4` · repro lands red, awaits fix

###### betty — 2026-08-15T00:58:20.258Z

[board-betty] TESTS: REVISE
What: docs/test-bible/core/agent.md — missing coverage — Decision A thinking-off + Provider-failed RESPONSE banner (AST-903 suite only; gap not landed yet)

###### joan — 2026-08-15T00:58:08.815Z

[board-joan]  CANON: OK

context_tokens≈8000

###### ada — 2026-08-15T00:57:42.989Z

`origin/sub/AST-1379/AST-1383-gap-craft-get-truncation-tests` @ `190870f4c334d1abebc01e32c9569c7d8e0eb15d` · test gap planned

---

_Implementation detail may live in git history on `origin/dev`._
