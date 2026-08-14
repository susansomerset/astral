<!-- linear-archive: AST-1196 archived 2026-08-14 -->

## Linear archive (AST-1196)

**Archived:** 2026-08-14  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1196/agent-task-synthesize-email-link-subject-title-errors-for-qualify  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1188 — Errors for qualify_meteorite dispatch task  
**Blocked by / blocks / related:** parent: AST-1188; blocks: AST-1197

### Description

## What this implements

Update `qualify_meteorite` `agent_task` instructions: construct `email-<originalsender>-<timestamp>` when no ATS link; use subject as title when content has none; discern original sender from email content (never candidate email); fail ads/unrelated content. Does not own schema/state registry or consult apply (siblings).

## Acceptance criteria

- [X] 2. No ATS link + usable JD in email content: Ruth returns `email-<originalsender>-<timestamp>`; row can **METEORITE_QUALIFIED** (http gate waived for that prefix). (instruction portion.)
- [X] 3. No title in content but subject present: recorded title is the subject; can **QUALIFY** when other gates pass. (instruction portion.)

## Boundaries

Does not own schema/BOT_BLOCKED registry or consult assemble/apply.

## In scope

- [X] `astral.config.config-source-of-truth` — no new behavior literals in config; instruction contract lives on the `qualify_meteorite` `agent_task` catalog row
- [X] `astral.agent.do-task-delegation` — prompts ship via catalog / `apply_repo_admin_json`; still `do_task(qualify_meteorite)`; no core Anthropic assembly
- [X] `astral.standards.in-scope-only` — prompts + AST-756 fixture only; no schema/state/apply
- [X] `astral.standards.dry-and-focused-functions` — no new Python helpers
- [X] `astral.standards.no-hardcoded-sets` — no new Python state/enum sets; prompt tokens are instruction text
- [X] `astral.git.engineer-test-tree-ban` — no tests/bible in engineer commits

## Considered but excluded

- [X] `astral.state.job-prior-states-enforced` / `astral.state.core-decides-transitions` — no JOB_STATES / transition edits (AST-1195 / AST-1197)
- [X] `astral.config.config-source-of-truth` / **BOT_BLOCKED** rename — AST-1195 (registry; not this child's prompt row)
- [X] `astral.batch.claim-process-release` / consult assemble+apply / Style D — AST-1197
- [X] `astral.standards.debug-contract-gated` — no debug logging changes
- [X] `astral.standards.database-header-inventory` — no table changes
- [X] `astral.batch.*` — no claim/process/release edits
- [X] `astral.agent.grade-vector-validation` / `astral.agent.confidence-bounds` — not a graded task
- [X] `astral.patterns.render-verdict-orchestrates-consult` / coat-check — untouched
- [X] `astral.layers.*` / `astral.ui.*` — no layer or UI edits
- [X] `orch.*` — universal orchestration statutes stay off per-child lists

## Notes for planning

Instructions only on the qualify_meteorite agent_task record. Fail/ads/no-title rows must use empty-string fields (never JSON null/omit on required keys — schema abort). Return exactly one jobs[] object per numbered CONTENT row with positional `astral_job_id` (`000`/`001`/…); never drop a row. Fixture sync is surgical on the `qualify_meteorite` row only; do not absorb catalog↔fixture drift (escalate re-baseline on AST-1188).

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1188-errors-for-qualify-meteorite-dispatch-task`, child `sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject`. Created at dispatch-parent.

### Comments

#### katherine — 2026-08-06T00:13:04.734Z
merge-child unblock: dropped forbidden tip `Merge remote-tracking branch 'origin/dev'…` (`e4c3d140`). Restacked with `git fetch` + `git merge origin/ftr/AST-1188-errors-for-qualify-meteorite-dispatch-task` as `merge-resume(AST-1196)` @ `f5a7f7a8`. `validate-sub-log.sh` → ok. Status remains **User Testing**.

#### chuckles — 2026-08-06T00:11:40.290Z
[merge-child] blocked: git pull merge on sub — tip `e4c3d140` is `Merge remote-tracking branch 'origin/dev' into sub/...` (forbidden). Also `origin/ftr/AST-1188-errors-for-qualify-meteorite-dispatch-task` is not an ancestor of the publish ref.

@Katherine Johnson — restack `sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject` onto current `origin/ftr/AST-1188-errors-for-qualify-meteorite-dispatch-task` with `git fetch && git merge origin/ftr/...` (no `git pull` / no `Merge remote-tracking branch`), keep resolve tip clean, push publish ref. Then Chuckles will re-run merge-child.

— Chuckles

#### radia — 2026-08-06T00:06:25.397Z
[code-rubric] revision=1

**Rubric:** code-rubric.v1
**Ticket:** AST-1196
**Publish ref:** `e086bb26` (`origin/sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject`)
**Overall:** CLEAN

Full active corpus (65 leaves — 18 universal + 47 scoped) swept in-session against this ticket's own diff footprint: `git diff origin/ftr/AST-1188-errors-for-qualify-meteorite-dispatch-task...origin/sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject` (paths `data/admin/agent_task.json`, `docs/uat-fixtures/AST-756/expected-agent_task.json`, `docs/features/meteorite/ast-1196-agent-task-synthesize-email-link-subject.md`, `docs/test-bible/core/repo_admin_json.md`, `tests/component/core/test_repo_admin_json.py`; change_types `{add, modify}`). Zero `src/` paths in this diff, so the entire `src/**`-scoped standards/state/layers/UI/batch/seed block is `not-applicable` on path; 6 scoped statutes apply and score `conforms` (`astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.betty-no-src-or-features`, `astral.git.engineer-test-tree-ban`, `astral.seed.define-approved`, `astral.seed.agent-tables-in-repo-json`); all 18 universal score `conforms`. No violations, no stragglers.

**Layer-mapping note (same gap Joan flagged at plan time):** `data/admin/**` isn't in the code-rubric's literal layer table (`src/data/**`→`data`; nothing maps top-level `data/`), so under a strict reading it contributes no layer and `astral.seed.agent-tables-in-repo-json` (layers `[core,data,utils]`) would score `not-applicable` despite its path (`data/admin/**`) matching. I scored it under the permissive reading Joan used at plan time (`data/admin` → `data` layer) so the directly-relevant statute isn't silently dropped by a rubric-table gap; verdict is `conforms` either way since there's nothing in this diff to violate it against (catalog row ships via repo JSON, no live-DB edit).

## Plan adherence

Verified mechanically, not just by reading the prose: (1) diffing `data/admin/agent_task.json` at `origin/ftr/AST-1188-...` vs the sub tip — exactly one `current==1` row changed (`qualify_meteorite`), matching Stage 1's pre/post snapshot gate; (2) same check on the AST-756 fixture — exactly one row changed there too, and `cache_prompt`/`user_prompt`/`updated_at` are byte-identical between catalog and fixture at the tip (no whole-file `cp`, no absorbed 53↑51 drift); (3) ran the plan's own Done-when assertion script against the shipped `cache_prompt`/`user_prompt` — all 13 substring checks pass, including the fragile never-candidate-mailbox sentence and the `00000000T000000Z` fallback shape Joan's round-2 review demanded. Both of Joan's round-1/round-2 fix-nows (empty-string vs null/omit; blind-`cp` fixture absorption) and both round-2 fix-nows (`astral_job_id` enumerated; never-drop row contract) are present verbatim in the shipped prompt, not just in the plan's prose.

**Pattern conformance:** cited In-scope id `astral.git.engineer-test-tree-ban` conforms (engineer's `code(AST-1196)` commit touches only `data/admin/` + `docs/uat-fixtures/`, never `tests/`/`docs/test-bible/`). `astral.config.config-source-of-truth`, `astral.agent.do-task-delegation`, `astral.standards.in-scope-only`, `astral.standards.dry-and-focused-functions`, `astral.standards.no-hardcoded-sets` all score `not-applicable` on this diff (their path predicate is `src/**`; this child touches zero `src/` files) — same "mechanically excluded, scored in spirit" situation Joan already called out at plan time; nothing to add. **Advisory (recurring, not fix-now/discuss):** `pattern.config.config-block` / `pattern.batch.entity-claim-process-release` under Considered-but-excluded again aren't ids in the active corpus (no `pattern.*` namespace — same slip flagged on AST-1195's review); likely meant `astral.config.config-source-of-truth` / `astral.batch.claim-process-release`.

**What's solid:** Betty's Tests Ready fix for the stale AST-786 `len(rows)==48` gate replaces whole-file byte-identity with a catalog key-set lock (53 rows) plus a dedicated `TestAst1196QualifyMeteoritePromptContract` class that checks the shipped prompt text directly — closing exactly the gate the plan flagged as `[qa-handoff]` rather than an engineer `tests/` edit.

## Frame diff

(none) — implementation matches the plan doc's Files Changed / Stage 1 as written; no adds or moves applied to this description.

context_tokens≈75000

— Radia

#### betty — 2026-08-05T23:57:51.205Z
Tests Ready — run on `origin/sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject` @ `9ec956e8` (`merge-tests(AST-1196): origin/tests 26ad05f0cdf9aa16f2c91297a14fb681fcae20fb`).

**Manifest**
1. `tests/component/core/test_repo_admin_json.py::TestAst1196QualifyMeteoritePromptContract` — email-link / subject-title / empty-string / positional `astral_job_id` contract + surgical fixture lockstep
2. `tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed` — revised catalog lock **53** current keys + startup apply (whole-file byte-identity retired)
3. `tests/component/core/test_repo_admin_json.py::TestAst1060QualifyMeteoriteCatalogRow` — Ruth shell fields still present
4. `tests/component/core/test_repo_admin_json.py::TestAst1107TaskNameEqualsTaskKey` — revised fixture check (no whole-file bytes)
5. `tests/component/core/test_repo_admin_json.py::TestAst1144ParseMeteoriteEmailMetadataPrompt` — `parse_meteorite_email` row lockstep
6. `tests/component/core/test_repo_admin_json.py::TestAst1154GradedTaskCompletenessPrompts` — per-key fixture marker lock

**Narrowed pytest**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_repo_admin_json.py::TestAst1196QualifyMeteoritePromptContract \
  tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed \
  tests/component/core/test_repo_admin_json.py::TestAst1060QualifyMeteoriteCatalogRow \
  tests/component/core/test_repo_admin_json.py::TestAst1107TaskNameEqualsTaskKey \
  tests/component/core/test_repo_admin_json.py::TestAst1144ParseMeteoriteEmailMetadataPrompt \
  tests/component/core/test_repo_admin_json.py::TestAst1154GradedTaskCompletenessPrompts \
  -q
```

**Bible shasum** (`origin/sub/…`)
- `docs/test-bible/core/repo_admin_json.md` `f598ab7bee63f9fd42b452dead2dcdbac2a40d72`

**Broken / revised:** AST-786 `len==48` + catalog↔fixture byte-identity; sibling whole-file fixture locks on AST-1107 / AST-1144 / AST-1154. Full AST-756 re-baseline (fixture missing `evaluate_meteorite` + `craft_evaluate_meteorite_rubric`) remains parent **AST-1188** follow-up — not absorbed here.

**Integration:** none revised.

— Betty

#### joan — 2026-08-05T23:49:16.441Z
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1196
**Overall:** APPROVED
**Publish ref tip:** `origin/sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject` @ `47c6dd7f`

## Traceability

AC2→S1 (Link rules); AC3→S1 (Title rules); parent Functional scope "Ads / unrelated content → Ruth fails → **METEORITE_FAILED_QUALIFY**"→S1 Fail section; new S1 Row contract→parent Purpose ("weak rows do not force whole-chunk **METEORITE_ERROR_QUALIFY**"). Parent AC1/AC4–AC8 remain N/A–boundary for this child (AST-1195 / AST-1197). One stage, no orphans.

**Considered:** 65 leaves; 18 universal + 2 scoped considered, all `conforms`; 45 scoped excluded on layer/path predicates. Files Changed table is unchanged from revision 1 (`data` / `docs`, same two paths, same change type), and `canon/` plus `docs/ASTRAL_CODE_RULES.md` are byte-identical between this ref and the tree I swept, so the considered/excluded set carries over unchanged. No statute scores `violates`.

## Both round-2 fix-nows are closed, and I checked the mechanism rather than the prose

**`astral_job_id`** now leads the always-include list as `Required. Always.` with the positional rule, is restated in the binding Row contract, is repeated in the Fail section ("Do not emit JSON null for astral_job_id, job_title, job_link, or jd_text"), and appears in `user_prompt`. The value shape is right where it has to be: `assemble` emits `f"{i:03d}: …"`, so `"000"` is what Ruth sees, and `_bind_response_jobs_to_claimed` rebinds on `re.fullmatch(r"\d{1,3}", aid)` — `"000"` matches, so the echoed index lands on the positional path rather than being mistaken for a fabricated id.

**Never-drop** is stated three times where it matters — Row contract, Fail section ("still return the row (same position / astral_job_id)" + "Do not omit the row"), and `user_prompt` — and the Decision block records *why* (length mismatch bails the whole positional pass; `job_link=""` and `email-…` tokens cannot use the AST-1133 link fallback). That is the reasoning I was checking for, not just the sentence.

**I executed the plan's own Done-when assertions against the prompt text the plan specifies.** All 13 substring checks pass on `cache_prompt` and `user_prompt` as written — including the fragile one, the never-candidate-mailbox sentence, which matches exactly because the prompt uses straight apostrophes throughout (no typographic `’` to silently break the compare). This plan will not strand `test-child` on a gate that cannot go green, which is the usual way a well-intentioned assertion block turns into churn.

**The mirrored fixture gate is satisfiable.** I confirmed the AST-756 fixture does contain a `current == 1` `qualify_meteorite` row with all three target keys, and it is currently byte-identical to the catalog row (both 530-char `cache_prompt`, both `updated_at 2026-07-30 00:54:55`). So the surgical three-field sync starts from lockstep and the `changed == ["qualify_meteorite"]` assertion can actually hold on both files. Inherited drift is exactly the two missing rows (`evaluate_meteorite`, `craft_evaluate_meteorite_rubric`), which the pre/post gates correctly ignore because they compare each file against its own snapshot rather than against each other.

Discuss items 4 and 5 are handled as asked: the AST-1197 note names the real gate order, and the fallback timestamp is `00000000T000000Z` in both the prompt and the Decision block.

## Findings

**1. `discuss` — one more robustness note for AST-1197, offered only so it is not rediscovered in apply.** Positional binding keys off list **position**, not off the echoed digits: `_bind_response_jobs_to_claimed` assigns `claimed_ids[i]` to response index `i` and never reads the `"002"` value. So a response that is complete but reordered would mis-bind, and a response that is short bails the whole positional pass. Your prompt closes both by instructing same-order and never-drop, which is everything this child can do from instruction text. If AST-1197 ever wants belt-and-braces, the echoed 3-digit index is available as a bind key in `consult.py` — their file, their call, and explicitly **not** a change to make here. Does not block.

**2. `acceptable`** — Self-assessment is honest and has tracked reality across all three revisions: `Risk: Medium` now names the actual mechanism (omitted `astral_job_id` or dropped rows → whole-chunk `METEORITE_ERROR_QUALIFY`, parent Purpose / AC7) rather than a vague "Ruth might misbehave." `Scope: minor` is accurate — still two files, one row, three fields, no `src/`. `Conf: high` is earned at this point. The prompt remains a superset of the live row (METEORITE framing, output fields, "Do not emit grade vectors"), `task_name == task_key` holds for AST-1107, boundaries against AST-1195 / AST-1197 are restated in step 8, and Betty's stale AST-786 `len(rows) == 48` gate is still correctly flagged as a `[qa-handoff]` rather than an engineer `tests/` edit.

No `fix-now` findings. R1–R6 pass, R7 satisfied by this comment. Status → **Plan Approved**.

context_tokens≈130000

— Joan

#### katherine — 2026-08-05T23:46:34.601Z
[plan-discuss] round=2 reply

Revised plan @ `47c6dd7f` on `origin/sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject`:
https://github.com/susansomerset/astral/blob/sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject/docs/features/meteorite/ast-1196-agent-task-synthesize-email-link-subject.md

**fix-now 1 (`astral_job_id`):** Always-include list now leads with required `astral_job_id` — echo the CONTENT 3-digit index (`"000"`/`"001"`/…); never invent UUID, never null/omit.

**fix-now 2 (never-drop / bind):** New **Row contract** — exactly one `jobs[]` object per numbered CONTENT row, same order; unusable rows return with empty-string fields, not omitted. Fail section restates "Do not omit the row." Done-when + user_prompt assert the binding sentences. Rationale: positional bind bails on length mismatch; `job_link=""` / `email-…` cannot use link fallback.

**discuss 3:** Fixture pre/post snapshot gate now mirrors the catalog (both must change only `qualify_meteorite`).

**discuss 4:** Added Note for AST-1197 — apply’s empty-`company_job_id` gate fires before http for `email-…` links; AC2 QUALIFY needs that waiver too (not this child).

**discuss 5:** No-Date timestamp fallback is now `00000000T000000Z` (same `YYYYMMDDTHHMMSSZ` shape).

**Scope / Conf / Risk:** still `minor` / `high` / `Medium` — Risk now also names dropped-row / missing-`astral_job_id` chunk ERROR.

#### joan — 2026-08-05T23:43:15.044Z
[plan-discuss] round=2 concern
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1196
**Overall:** REVISE
**Publish ref tip:** `origin/sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject` @ `6e43d5b9`

## Traceability

AC2→S1 (Link rules); AC3→S1 (Title rules); parent Functional scope "Ads / unrelated content → Ruth fails → **METEORITE_FAILED_QUALIFY**"→S1 Fail section. Parent AC1/AC4–AC8 are N/A–boundary for this child ("Does not own schema/BOT_BLOCKED registry or consult assemble/apply" — AST-1195 / AST-1197). One stage, no orphans.

**Considered:** 65 leaves re-swept against the revised Files Changed table — 18 universal + 2 scoped considered, all `conforms`; 45 scoped excluded on layer/path predicates. The round-1 layer-enum ambiguity is resolved: the cells now read `data` and `docs`, both in the statute enum, and the considered/excluded set is identical to what I scored under the stricter reading last round. No statute scores `violates`; both fix-nows below are R6 definition fidelity (missing steps) traced to parent Purpose / AC7.

## Round-1 items — both resolved, and I verified the reasoning rather than the wording

`fix-now 1` (null/omit → empty string) is genuinely closed. I re-read the validator: `_validate_schema_object_fields` checks `required and val is None`, then `if type_spec == "str" and not isinstance(val, str)` — `""` is a `str` and there is no min-length check anywhere in that path, so empty strings pass and reach `process`. `jd_text` is still `{"type": "str", "required": True}` in `TASK_CONFIG["qualify_meteorite"]`, confirming the plan's premise that it is outside AST-1195's remit. `fix-now 2` is closed too — the pre/post snapshot gate asserting `changed == ["qualify_meteorite"]` is exactly the right shape, and escalating the 53↔51 re-baseline to Chuckles on AST-1188 rather than absorbing it is the correct call.

What the revision surfaced is that empty-string fail rows have a second-order consequence on **row identity**, which is where both new fix-nows live.

## Findings

**1. `fix-now` — `astral_job_id` is `required: True` and is the one required key the new instruction does not enumerate.**

Stage 1's prompt says: "Return JSON with a jobs list. For each astral_job_id always include these string fields (use "" when a rule says empty — never JSON null, never omit a required key)" — then lists `company_job_id`, `job_title`, `job_link`, `jd_text`. `astral_job_id` itself is absent from that list, but the schema has it as `{"type": "str", "required": True}`, and AST-1195's remit is `job_link` / `job_title` only, so it stays required after that sibling lands.

A reader of that paragraph can reasonably conclude the four bullets *are* the required set. If Ruth ever drops the key on one row, the validator returns `jobs[N]: Missing required field 'astral_job_id'`, `do_task` fails the envelope, and `_run_batch_consult` sends the whole chunk to `error_state` — `METEORITE_ERROR_QUALIFY` for every sibling job. That is the parent Purpose bug with a different field name in the message, and AC7 reserves that state for genuine unparseable envelopes.

The risk is not hypothetical in shape, only in field: the live incident aborted on `jobs[0]: Missing required field 'job_link'`. This ticket's whole job is to close the required-field null/omit holes in this prompt; leaving one required key out of the enumerated contract leaves the last one open.

**Recommendation:** add `astral_job_id` to the always-include list, with the position rule: it is the 3-digit index of the row as numbered in CONTENT (`000`, `001`, …), never invented, never omitted, never `null`.

**2. `fix-now` — `job_link=""` on fail rows removes the only fallback that can bind those rows back to a job, so ads land on ERROR instead of FAILED_QUALIFY.**

Ruth never sees real `astral_job_id` values — `assemble` deliberately excludes them ("astral_job_id excluded from live content — position map in decode/response") and emits `000: job_link: …`. Binding back happens in two passes:

- `_bind_response_jobs_to_claimed` rebinds position echoes (`""` or `\d{1,3}`) to claimed ids **by index**, but bails entirely on `if len(response_jobs) != len(claimed_ids): return`.
- `_bind_response_jobs_by_job_link` (AST-1133) is the fallback for rows carrying a non-digit fabricated id — it matches on `normalize_link(rj["job_link"])` and skips any row where that normalizes empty.

Fail rows now carry `job_link=""` by instruction, so they have no link to bind on. Two consequences follow. If Ruth drops an ads row instead of returning it — and "fail this row" is readable that way — the length check fails and the positional pass bails for the **entire response**, not just that row; every row then depends on link matching, and the dropped row is `missing`. Unbound / missing rows go to `_transition_batch_consult_failures(..., error_state)`, and since `JOB_STATES["METEORITE_NEW"]` has no `retry_state`, `_consult_batch_fail_dest` returns `METEORITE_ERROR_QUALIFY`. Ads content parking on ERROR contradicts parent Functional scope (ads → **METEORITE_FAILED_QUALIFY**) and AC7.

Worth noting the same mechanism applies to the success path this child exists to enable: a synthesized `email-…` token will not `normalize_link`-match the claimed row's stored link either, so **positional identity is the only reliable binding for email rows** once this prompt ships.

Good news on likelihood: in the live 14-job run Ruth echoed `"000"`, `"001"`, … `"009"` and returned one row per input, and the 4-job chunk bound cleanly to real UUIDs. The mechanism works today because Ruth is cooperative. Round 1's lesson was to make the wording correct independent of Ruth's goodwill, and this is the same shape.

**Recommendation:** state the row contract explicitly in the prompt — return **exactly one object per input row, in the same order as the numbered CONTENT rows**, echoing that row's 3-digit index as `astral_job_id`; never drop a row (unusable rows come back with empty-string fields, not omitted). Add a Done-when assertion for that sentence alongside the existing ones. Instruction text only, same catalog row, no `src/` and no sibling scope.

**3. `discuss` — the pre/post gate guards the catalog; the fixture has only prose.** Done-when claims "no other catalog or fixture rows change in the commit," and step 7's snapshot proves it for `data/admin/agent_task.json`. Nothing mechanical covers `docs/uat-fixtures/AST-756/expected-agent_task.json`, which is the file where an accidental wholesale write would do the damage round 1 was about. Mirroring the snapshot for the fixture is four lines and makes the claim self-enforcing.

**4. `discuss` — the apply gate that actually blocks an `email-…` row first is `company_job_id`, not the http check.** The Decision block credits `min_job_title_length` / `min_jd_chars` for parking fails. In `consult.py` the order is `if not company_job_id` → title length → `job_link.startswith("http")` → jd length. For a synthesized `email-` link, `_resolve_company_job_id("", "email-…")` finds no UUID path segment and returns `""`, so the row fails on `"empty company_job_id"` before the http gate is ever reached. Harmless for the fail path — FAILED_QUALIFY either way — but it means AC2's end-to-end QUALIFY needs AST-1197 to waive **that** gate too, not just the http one. Not yours to fix and not a reason to widen this child; the plan's omit/`""` guidance on `company_job_id` is right (inventing a UUID would poison dedupe). Worth one line in the plan so it reaches Hedy rather than being rediscovered in apply.

**5. `discuss` — the timestamp fallback does not match its own declared shape.** The rule says UTC compact `YYYYMMDDTHHMMSSZ` (example `20260805T224603Z`), and the no-Date fallback is `00000000000000Z` — fourteen zeros with no `T`. Nothing parses it today, so it costs nothing now; `00000000T000000Z` keeps every `email-…` token one shape for whatever AST-1197 does with it.

**6. `acceptable`** — Self-assessment stays honest and improved: `Risk: Medium` now names instruction-directed chunk-abort as the danger rather than framing it as Ruth misbehaving. `Conf: high` is defensible. The prompt is still a superset of the live row (METEORITE framing, four output fields, "Do not emit grade vectors" all retained), and `task_name == task_key` is preserved for AST-1107. The `[qa-handoff]` note for Betty's stale AST-786 `len(rows) == 48` gate is recorded in the right place.

context_tokens≈112000

— Joan

#### katherine — 2026-08-05T23:35:01.402Z
[plan-discuss] round=1 reply

Revised plan @ `6e43d5b9` on `origin/sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject`:
https://github.com/susansomerset/astral/blob/sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject/docs/features/meteorite/ast-1196-agent-task-synthesize-email-link-subject.md

**fix-now 1 (null/omit → empty string):** Fail / title / user_prompt now require `job_title=""`, `job_link=""`, `jd_text=""` — never JSON null, never omit those keys. Notes that `jd_text` stays `required: True` after AST-1195; empty string passes schema and still fails apply mins. `company_job_id` omit/`""` unchanged.

**fix-now 2 (blind cp):** Dropped whole-file `cp`. Stage now surgically updates only the fixture’s `qualify_meteorite` `cache_prompt` / `user_prompt` / `updated_at`, with a pre/post catalog diff gate that only `qualify_meteorite` may change. Inherited 53↔51 drift + other-task prompt drift left alone; full re-baseline escalated to Chuckles on AST-1188. Named Betty’s stale AST-786 `len(rows)==48` gate as `[qa-handoff]` at Tests Ready (no engineer `tests/` edit).

**discuss 3:** Done-when now asserts the never-candidate-mailbox sentence, empty-string fail clause, and catalog↔fixture field lockstep for that row.

**Scope / Conf / Risk:** still `minor` / `high` / `Medium` — Risk now names instruction-directed chunk-abort as the Medium case.

#### joan — 2026-08-05T23:32:18.866Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1196
**Overall:** REVISE
**Publish ref tip:** `origin/sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject` @ `99c4edb7`

## Traceability

AC2→S1 Link rules (steps 1–3); AC3→S1 Title rules. Stage 1's fail/ads section traces to parent Functional scope ("Ads / unrelated content → Ruth fails → METEORITE_FAILED_QUALIFY"). Parent AC1/AC4–AC8 are N/A–boundary for this child ("Does not own schema/BOT_BLOCKED registry or consult assemble/apply" — AST-1195 / AST-1197). One stage, no orphans.

**Considered:** 65 leaves swept. 18 universal considered (all `conforms`) + 2 scoped considered, 45 scoped excluded on layer/path predicates. **Layer-cell note (rubric §Matching algorithm step 1):** the Files Changed Layer cell `data/admin` is not in the statute layer enum and is not in the free-text mapping table, so the rubric would have me treat it as `docs`. I scored under **both** the `data` and `docs` readings so nothing was silently skipped; the considered/excluded set is identical either way except `astral.seed.agent-tables-in-repo-json`, which I considered under the stricter `data` reading (verdict `conforms` — rows ship via repo JSON + `apply_repo_admin_json`, and the plan explicitly forbids hand-editing the live DB). `astral.seed.define-approved` also `conforms` (parent definition directs this child's instruction rewrite; Open questions: none).

Worth recording because it reads backwards at first glance: **`astral.git.engineer-test-tree-ban` is excluded, not violated.** Its path list is `tests/**`, `docs/test-bible/**`, `docs/ASTRAL_TEST_BIBLE.md`, `scripts/test_*.py`, `scripts/testing/**` — `docs/uat-fixtures/**` is not in it, so editing the AST-756 fixture is legitimately Katherine's to do. Same for `orch.roles.pre-commit-path-bans` / `orch.roles.betty-owns-test-tree` (`conforms`). Four statutes the ticket lists **In scope** — `astral.standards.in-scope-only`, `astral.config.config-source-of-truth`, `astral.agent.do-task-delegation`, `astral.standards.no-hardcoded-sets` — are mechanically **excluded** here because their path predicate is `src/**` and this child touches no `src/` path. I scored them in spirit anyway and all four conform; the fix-nows below are R6 definition fidelity, not statute violations.

## Findings

**1. `fix-now` — the fail/ads instruction tells Ruth to emit `null` on a field that is still `required`, which re-creates this epic's headline bug.**

Stage 1's Fail section says: "fail this row: **empty/null** job_title, job_link, and jd_text (and **omit** company_job_id)". Title rules likewise say "leave job_title **empty / null**". Those three words are not interchangeable to the validator:

```
src/core/agent.py:1557-1563
required = field_spec.get("required", False)
if required and val is None:
    return f"Missing required field '{field_name}'"
if val is None:
    continue
```

`None` **and an omitted key** both hit that branch (`obj.get()` returns `None`), which aborts `do_task` for the whole chunk — exactly the parent Purpose ("Ruth returned JSON `null` for required `job_link` / `job_title`… schema aborted the whole `do_task` and batch-errored every job in the chunk"). An **empty string passes**, because `""` is a `str` and the validator applies no min-length check.

Now the field that matters: `src/utils/config.py` `TASK_CONFIG["qualify_meteorite"].response_schema.jobs.items_schema` has `jd_text` at **`"required": True"`**, and AST-1195's remit per the parent is "Allow null/omit **`job_link`/`job_title`**" — `jd_text` is **not** in that sibling's scope. So a `null`/omitted `jd_text` on an ad row aborts the chunk and sends every sibling job to **METEORITE_ERROR_QUALIFY**, breaking parent AC1 ("chunk does **not** all-ERROR") and AC7 (ERROR reserved for unparseable envelopes) — the precise failure this epic exists to kill.

This is not a theoretical sequencing worry, and that is what makes it fix-now rather than discuss: catalog rows go live via `apply_repo_admin_json` at startup, so this prompt takes effect as soon as the row lands, whatever order the siblings merge in.

**Recommendation:** say **empty string** explicitly, and drop "null" and "omit" for any field that remains `required: True` after AST-1195 — concretely `jd_text` (and `job_link`/`job_title` too, so the wording is correct independent of sibling landing order; `company_job_id` is `required: False`, so omit is genuinely fine there and your guidance on it is correct). Empty strings also route correctly end-to-end without any new mechanism, since `min_job_title_length: 5` and `min_jd_chars: 40` are already on that TASK_CONFIG row for the apply-side gate. If you conclude `jd_text` must become nullable too, that is an AST-1195 scope change — raise it on AST-1188 rather than widening this child.

**2. `fix-now` — the blind `cp` would commit a large pre-existing fixture drift under this ticket's name, and the plan's own recheck would report OK.**

Step 5 is `cp data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json`, and the Done-when asserts `a == b`. But the two files are **already far apart on the base**, not just by your prompt edit. On `origin/dev` and on `origin/ftr/AST-1188-…` alike:

- catalog **53 rows**, fixture **51 rows** — fixture is missing `evaluate_meteorite` and `craft_evaluate_meteorite_rubric` entirely
- **13** shared rows differ in `cache_prompt` / `user_prompt` / `nocache_prompt` (`craft_*_rubric`, `grade_do`, `grade_get`, `grade_like`, `meteorite_like`, `evaluate_jd`, `craft_company_search_terms`, `craft_resume_base`)

None of that is yours — it pre-dates this branch. But a wholesale `cp` folds two added rows and thirteen unrelated prompt bodies into AST-1196's commit, and because the recheck only asserts byte-identity **after** the copy, it prints OK and hides it. Radia then reviews a prompt ticket whose diff is mostly other people's prompts.

**Recommendation:** constrain the sync so it can only carry your row. Capture the catalog before the edit and assert the only differing `task_key` between pre- and post-edit is `qualify_meteorite`; then either (a) leave the inherited drift alone, note in the plan that byte-identity is unreachable without absorbing it, and escalate to Chuckles on AST-1188 for a labeled re-baseline, or (b) get explicit approval to re-baseline here and say so in the plan and commit message. Silent absorption is the one option to avoid.

Related, and explicitly **not** yours to fix: Betty's AST-786 gate asserts `len(rows) == 48` against a frozen key set (`tests/component/core/test_repo_admin_json.py`), which is stale at 53 rows today and will stay red no matter what you do here. The plan should name that so `test-child` does not tempt anyone into editing `tests/` — it is a `[qa-handoff]` for Betty at Tests Ready.

**3. `discuss` — the Done-when substring assertions are weaker than the contract they guard.** `"SUBJECT" in cp or "subject" in cp` and `"ads" in cp.lower()` pass on almost any prose containing those words, so a prompt that mangles the actual rules could still go green. Since this recheck is the ticket's only verification (no `src/` behavior to exercise), consider asserting the operative clauses instead — the exact `email-<originalsender>-<timestamp>` token (already good), the never-candidate-mailbox sentence, and the empty-string wording from finding 1.

**4. `acceptable`** — I diffed the replacement against the live row (`data/admin/agent_task.json`, `qualify_meteorite`, `current == 1`, 530-char `cache_prompt`) and the new text is a **superset**: it keeps the "METEORITE job … raw or visible text … NOT a normal job-board listing scrape" framing, the same four output fields, and "Do not emit grade vectors". Nothing load-bearing is dropped, which is the main risk in a full prompt rewrite. Keeping `task_name == task_key` also holds AST-1107's assertion, and leaving `response_format` alone on the row is right since TASK_CONFIG governs it.

Self-assessment reads honestly — `Risk: Medium` naming "synthesize `email-` for ads" is adjacent to finding 1, though it frames the danger as Ruth misbehaving rather than the instruction itself directing a chunk-aborting `null`. `Conf: high` is defensible on the instruction contract, which the parent does pin literally.

context_tokens≈128000

— Joan

#### katherine — 2026-08-05T23:26:28.594Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject/docs/features/meteorite/ast-1196-agent-task-synthesize-email-link-subject.md

`origin/sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject` @ `99c4edb74fa96c7385a66b3d536a8f2fe54a139d`

**Scope:** `minor` — one Ruth catalog row (`qualify_meteorite` prompts) plus AST-756 fixture byte-sync; no `src/` product logic.

**Conf:** `high` — parent Functional scope and child Notes pin the instruction contract; prior meteorite plans (AST-1060 / AST-1089 / AST-1144) establish the catalog + fixture pattern.

**Risk:** `Medium` — bad prompt wording can invent candidate-mailbox senders, synthesize `email-` for ads, or skip subject-as-title; end-to-end QUALIFY still needs AST-1195 schema nulls + AST-1197 apply, but the instruction portion is verifiable from catalog text alone.

---

# AST-1196 — agent_task: synthesize email link + subject title

**Linear:** [AST-1196](https://linear.app/astralcareermatch/issue/AST-1196/agent-task-synthesize-email-link-subject-title-errors-for-qualify)
**Parent:** [AST-1188](https://linear.app/astralcareermatch/issue/AST-1188/errors-for-qualify-meteorite-dispatch-task) — Errors for qualify_meteorite dispatch task
**Publish ref:** `origin/sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject`

Update the current Ruth `qualify_meteorite` `agent_task` instructions so that when CONTENT has a usable job description but no ATS/http job URL, Ruth returns a synthesized `job_link` of the form `email-<originalsender>-<timestamp>`; when CONTENT has no title but an email subject is present, Ruth uses that subject as `job_title`; original sender is discerned from email CONTENT (never the candidate mailbox); ads / unrelated non-JD content are failed via **empty-string** fields (never JSON `null` / omit on required keys); every input row returns exactly one response object with a positional `astral_job_id`. Does **not** own schema nullability / **BOT_BLOCKED** registry (AST-1195) or consult assemble/apply / http-gate / `company_job_id` waiver / Style D (AST-1197).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | Rewrite `qualify_meteorite` `cache_prompt` (+ short `user_prompt` touch); bump `updated_at` — **only this row** | data |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Surgical update of the existing `qualify_meteorite` row’s prompts/`updated_at` to match catalog — **no whole-file `cp`** | docs |

**No changes expected:** `src/utils/config.py`, `src/core/consult.py`, `src/core/agent.py`, `src/core/dispatcher.py`, `src/ui/**`, other `agent_task` rows, `tests/` / bible (Betty after Code Complete). Do **not** hand-edit the live DB — startup `apply_repo_admin_json` ships the row. Do **not** absorb pre-existing catalog↔fixture drift (missing rows / other tasks’ prompts) into this ticket.

## Stage 1: `qualify_meteorite` prompt — email-link synthesize + subject title

**Done when:** The current `qualify_meteorite` catalog row instructs Ruth to (a) synthesize `email-<originalsender>-<timestamp>` when there is no usable http(s) ATS/job link but CONTENT holds a real JD, (b) use SUBJECT as `job_title` when content has no title, (c) never use the candidate mailbox as original sender, (d) fail ads/unrelated content with **empty-string** `job_title` / `job_link` / `jd_text` (omit only optional `company_job_id`), (e) return **exactly one object per numbered CONTENT row** with positional `astral_job_id` (`000`, `001`, …) — never drop a row; the AST-756 fixture’s `qualify_meteorite` row matches those same three fields; no other catalog or fixture rows change in the commit.

1. **Pre-edit snapshots (gate against silent multi-row edits):** before changing anything, copy both files:

```bash
cp data/admin/agent_task.json /tmp/agent_task.pre-ast-1196.json
cp docs/uat-fixtures/AST-756/expected-agent_task.json /tmp/expected-agent_task.pre-ast-1196.json
```

2. In `data/admin/agent_task.json`, locate the single object with `task_key == "qualify_meteorite"` and `current == 1`. Do **not** change `task_key`, `task_key_uuid`, `agent_id`, `task_group_*`, `task_seq`, `task_name`, empty prompt slots (`system_prompt`, `cache_prompt_b/c/d`, `nocache_prompt`, `run_next`), or any other row.

3. Replace **`cache_prompt`** with the following text (exact contract — keep markdown `## INSTRUCTIONS` heading; flat JSON string value, `\n` newlines as neighboring rows do):

```text
## INSTRUCTIONS

Each item is a METEORITE job that already holds raw or visible text (email body, recruiter forward, or Playwright-fetched page text) — NOT a normal job-board listing scrape. CONTENT may include subject/headers/body so you can read sender, subject, and JD.

### Row contract (binding)
CONTENT rows are numbered `000:`, `001:`, … Return exactly one jobs[] object per input row, in the same order. Never drop a row — unusable rows come back with empty-string fields, not omitted. Echo that row's 3-digit index as astral_job_id (`"000"`, `"001"`, …). Never invent UUIDs for astral_job_id. Never omit astral_job_id. Never use JSON null for astral_job_id. Positional identity is required so apply can bind rows when job_link is "" or an email- token.

Return JSON with a jobs list. For each row always include these string fields (use "" when a rule says empty — never JSON null, never omit a required key):
- astral_job_id: the 3-digit CONTENT index for this row (`"000"`, `"001"`, …). Required. Always.
- company_job_id: employer external job UUID when knowable from an ATS/http link; otherwise omit the key or use "" (do not invent a fake UUID). This field is optional.
- job_title: authoritative title (see title rules)
- job_link: primary job URL or synthesized email- token (see link rules)
- jd_text: authoritative visible job-description text when the CONTENT is a real JD; otherwise ""

### Link rules
- Prefer a real http(s) ATS / job-posting URL from CONTENT when one exists → use that as job_link.
- When there is NO usable http(s) job URL but CONTENT contains a real job description → set job_link to exactly:
  email-<originalsender>-<timestamp>
  where:
  - <originalsender> is the original sender's email address discerned from CONTENT (From / forwarded-from / original recruiter). Lowercase; strip display names and angle brackets; keep @ and dots. NEVER use the candidate's own mailbox address as <originalsender>.
  - <timestamp> is the message Date / sent time visible in CONTENT, formatted UTC compact YYYYMMDDTHHMMSSZ (example: 20260805T224603Z). If no Date/sent time is visible, use 00000000T000000Z (same shape: eight digits, T, six digits, Z).
- Do NOT synthesize an email- link for ads, marketing blasts, newsletters, or unrelated non-JD content.

### Title rules
- Prefer a job title stated in the JD / body content.
- When content has no title but an email SUBJECT is present in CONTENT → use that subject as job_title.
- When there is no title in content AND no usable subject → set job_title to "" (empty string). Do not invent a title. Do not use JSON null. Do not omit the key.

### Fail / unusable content
- Ads, marketing, unrelated non-JD content, or pages with no usable job description → still return the row (same position / astral_job_id). Fail it by setting job_title="", job_link="", and jd_text="" (empty strings). You may omit company_job_id. Do not synthesize email- links for these. Do not emit JSON null for astral_job_id, job_title, job_link, or jd_text — null/omit on those keys aborts schema validation for the whole chunk. Do not omit the row.
- Do not emit grade vectors. Usable extracts = filled fields per rules above; unusable rows use empty-string fields (apply layer parks FAILED — not your concern here).
- Always return valid JSON only (no markdown fences).
```

⚠️ **Decision — empty string, never null/omit on required fields:** `agent.py` treats `required and val is None` (including omitted keys via `.get()` → `None`) as a schema miss that aborts `do_task` for the whole chunk — the parent Purpose bug. `jd_text` and `astral_job_id` stay `required: True` even after AST-1195 (sibling only nulls `job_link`/`job_title`). Empty string `""` passes the type/required check and still fails apply content gates. Instruct empty strings for fail/ads and for no-title/no-subject on `job_title`/`job_link`/`jd_text`. `company_job_id` remains `required: False` — omit or `""` is fine.

⚠️ **Decision — positional `astral_job_id` + never drop rows:** Assemble excludes real UUIDs from live CONTENT and numbers rows `000:`, `001:`, …. Binding uses positional echoes first (`_bind_response_jobs_to_claimed`); length mismatch bails the whole positional pass, and `job_link=""` / `email-…` cannot fall back via `_bind_response_jobs_by_job_link`. Dropping an ads row (or omitting `astral_job_id`) sends siblings to **METEORITE_ERROR_QUALIFY**, contradicting parent ads→**FAILED_QUALIFY** and AC7. Instruction: one object per input row, same order, echo the 3-digit index.

⚠️ **Decision — prompts only on the catalog row:** Ticket Notes say instructions-only on the `qualify_meteorite` `agent_task` record. Do **not** add `email-` prefix / timestamp format literals to `TASK_CONFIG` or a new config block here; AST-1197 owns apply recognition of the `email-` prefix. The instruction string matches parent Functional scope literally (`email-<originalsender>-<timestamp>`).

⚠️ **Decision — original sender from CONTENT, never candidate mailbox:** Parent Boundaries forbid treating the candidate email as original sender. Ruth discerns From / forwarded-from / originating recruiter from the email body/headers in assemble CONTENT (assemble wiring is AST-1197; prompts assume that content is present).

⚠️ **Decision — fail ads via empty-string fields, not a new response key:** Apply parks **METEORITE_FAILED_QUALIFY**. Do **not** invent a `fail_reason` field or grade vectors. Do **not** ask AST-1195 to null `jd_text` from this child — if that ever becomes necessary, raise it on AST-1188.

⚠️ **Decision — timestamp format `YYYYMMDDTHHMMSSZ`:** Compact UTC from Date/sent time in CONTENT. No-Date fallback is `00000000T000000Z` (same shape as the example — not fourteen bare zeros).

⚠️ **Decision — omit/empty `company_job_id` on synthesized links:** AST-1127 already made `company_job_id` optional; inventing a UUID for `email-` links would poison dedupe. Keep http-ATS UUID extract behavior when a real link exists.

⚠️ **Note for AST-1197 (not this child):** Today’s apply gate order is empty `company_job_id` → title length → `job_link.startswith("http")` → jd length. A synthesized `email-…` link yields empty resolved `company_job_id` before the http check runs, so end-to-end AC2 QUALIFY needs AST-1197 to waive **that** gate (and the http gate) for the `email-` prefix — not invent a UUID here.

4. Replace **`user_prompt`** with:

```text
Qualify these meteorite jobs. Follow the cache instructions: one jobs[] object per numbered CONTENT row (echo astral_job_id as 000/001/…; never drop a row); http(s) job_link when present; else email-<originalsender>-<timestamp> for real JDs with no ATS link; subject as job_title when content has no title; fail ads/unrelated with empty-string job_title/job_link/jd_text (never JSON null). Return astral_job_id, company_job_id, job_title, job_link, and jd_text for each row.
```

5. Set `updated_at` on that same row to the current UTC timestamp string matching neighboring rows (`YYYY-MM-DD HH:MM:SS`).

6. **Surgical fixture sync (no whole-file `cp`):** in `docs/uat-fixtures/AST-756/expected-agent_task.json`, find the object with `task_key == "qualify_meteorite"` and `current == 1` and set its `cache_prompt`, `user_prompt`, and `updated_at` to the **exact same strings** as the catalog row just edited. Do **not** `cp` the whole catalog over the fixture. Do **not** add missing fixture rows (`evaluate_meteorite`, `craft_evaluate_meteorite_rubric`) or rewrite other tasks’ prompts — that pre-existing drift is out of scope for AST-1196.

⚠️ **Decision — leave inherited fixture drift alone:** On current `origin/dev` / parent tip the catalog has 53 current rows and the AST-756 fixture 51 (fixture missing `evaluate_meteorite` + `craft_evaluate_meteorite_rubric`) plus ~13 shared rows with unrelated prompt drift. A blind `cp` would absorb all of that under this ticket’s name. Byte-identity of the two files is **unreachable** without a labeled re-baseline — escalate that to Chuckles on **AST-1188** (not this child). This stage only keeps the `qualify_meteorite` row’s three edited fields in lockstep.

7. **Post-edit gates:** only `qualify_meteorite` may differ from each pre-edit snapshot:

```bash
python3 - <<'PY'
import json

def current_by_key(path):
    return {r["task_key"]: r for r in json.load(open(path)) if r.get("current") == 1}

for label, pre_path, post_path in (
    ("catalog", "/tmp/agent_task.pre-ast-1196.json", "data/admin/agent_task.json"),
    ("fixture", "/tmp/expected-agent_task.pre-ast-1196.json", "docs/uat-fixtures/AST-756/expected-agent_task.json"),
):
    pre, post = current_by_key(pre_path), current_by_key(post_path)
    assert set(pre) == set(post), f"{label} row set changed: {set(pre)^set(post)}"
    changed = [k for k in pre if pre[k] != post[k]]
    assert changed == ["qualify_meteorite"], f"{label} unexpected changed rows: {changed}"
    print(f"OK {label} diff confined to qualify_meteorite")
PY
```

8. Do **not** edit `qualify_job_listings`, `parse_meteorite_email`, or any other task row. Do **not** edit `TASK_CONFIG["qualify_meteorite"]` response_schema / pass/fail/error states. Do **not** edit `consult.py` assemble/process (AST-1197). Do **not** rename **BOT_BLOCKED** / touch `JD_SCRAPE_FAIL_BOT` (AST-1195). Do **not** edit `tests/` — Betty’s AST-786 gate (`tests/component/core/test_repo_admin_json.py` asserting `len(rows) == 48` against a frozen key set) is already stale at 53 catalog rows; that is a **`[qa-handoff]` for Betty at Tests Ready**, not an engineer fix.

**Done when (recheck):**

```bash
python3 - <<'PY'
import json

def qm(path):
    rows = json.load(open(path))
    return next(r for r in rows if r.get("task_key") == "qualify_meteorite" and r.get("current") == 1)

cat = qm("data/admin/agent_task.json")
fix = qm("docs/uat-fixtures/AST-756/expected-agent_task.json")
for label, row in ("catalog", cat), ("fixture", fix):
    cp = row["cache_prompt"]
    up = row["user_prompt"]
    assert "email-<originalsender>-<timestamp>" in cp, label
    assert "NEVER use the candidate's own mailbox address as <originalsender>" in cp, label
    assert "exactly one jobs[] object per input row" in cp, label
    assert "3-digit index as astral_job_id" in cp, label
    assert 'astral_job_id:' in cp and '"000"' in cp, label
    assert 'set job_title to "" (empty string)' in cp or 'job_title to ""' in cp, label
    assert 'job_title="", job_link="", and jd_text=""' in cp, label
    assert "Do not omit the row" in cp or "Never drop a row" in cp, label
    assert "never JSON null" in cp or "Do not emit JSON null" in cp or "never JSON null" in up, label
    assert "00000000T000000Z" in cp, label
    assert "YYYYMMDDTHHMMSSZ" in cp, label
    assert "email-<originalsender>-<timestamp>" in up, label
    assert "one jobs[] object per numbered CONTENT row" in up or "astral_job_id as 000/001" in up, label
assert cat["cache_prompt"] == fix["cache_prompt"]
assert cat["user_prompt"] == fix["user_prompt"]
assert cat["updated_at"] == fix["updated_at"]
print("OK qualify_meteorite prompts + surgical fixture lockstep")
PY
```

## Self-Assessment

**Scope:** `minor` — one Ruth catalog row (`qualify_meteorite` prompts) plus surgical fixture field lockstep for that row; no `src/` product logic; no whole-file fixture re-baseline.

**Conf:** `high` — parent Functional scope and Joan round-1/2 fix-nows pin empty-string vs null, positional `astral_job_id`, never-drop-row binding, and surgical fixture sync.

**Risk:** `Medium` — omitting `astral_job_id` or dropping ads rows would re-create whole-chunk **METEORITE_ERROR_QUALIFY** (parent Purpose / AC7); empty-string + one-row-per-input wording are the mitigations. End-to-end QUALIFY still needs AST-1195 schema nulls + AST-1197 apply (including `company_job_id` / http waiver for `email-` links).

## Rules check (plan vs ASTRAL_CODE_RULES)

- §2.1 / `astral.config.config-source-of-truth` — no new behavior literals in config; instructions stay on the `agent_task` row (ticket boundary). Apply-side `email-` recognition remains AST-1197.
- §2.2 / `astral.agent.do-task-delegation` — still `do_task(qualify_meteorite)`; prompts ship via catalog / `apply_repo_admin_json`; no core Anthropic assembly.
- §1.1 / `astral.standards.in-scope-only` — prompts + surgical fixture fields only; no schema/state/apply creep into AST-1195 / AST-1197; no silent multi-row fixture absorption.
- §1.3 / `astral.standards.dry-and-focused-functions` — no new Python helpers.
- §1.4 / `astral.standards.no-hardcoded-sets` — no new Python state/enum sets; prompt tokens are instruction text, not a parallel registry.
- `astral.seed.agent-tables-in-repo-json` — row ships via repo JSON; no live-DB hand-edit.
- §3.3 imports — N/A (no `src/` edits).
- §3.5 naming — keep `task_key` / `task_name` `qualify_meteorite` (AST-1107 equality).
- Engineer test-tree ban — no `tests/` / bible edits; stale AST-786 `len==48` gate is Betty `[qa-handoff]`.

## Revisions

Revision 1 — 2026-08-05
Driven by: Joan `[plan-discuss] round=1 concern` (plan-rubric REVISE) — fix-now empty-string vs null/omit on required fields; fix-now forbid blind fixture `cp` / absorb inherited drift; discuss stronger Done-when assertions.
Changes: Fail/title rules + user_prompt require empty strings and forbid JSON null/omit on `job_title`/`job_link`/`jd_text`; Files Changed + Stage 1 steps switch to surgical fixture field lockstep with pre/post catalog diff gate; Done-when asserts operative clauses; note AST-786 stale `len==48` as Betty qa-handoff; escalate full fixture re-baseline to Chuckles on AST-1188; Layer cells `data`/`docs`; Risk self-assessment updated for instruction-directed chunk-abort.

Revision 2 — 2026-08-05
Driven by: Joan `[plan-discuss] round=2 concern` (plan-rubric REVISE) — fix-now enumerate required `astral_job_id`; fix-now one-row-per-input / never-drop for bind; discuss fixture pre/post gate; discuss `company_job_id` gate note for AST-1197; discuss timestamp fallback shape.
Changes: Prompt adds Row contract + `astral_job_id` always-include with positional `000`/`001`/…; fail path must still return the row; fallback timestamp `00000000T000000Z`; fixture snapshot gate mirrors catalog; Note for AST-1197 on empty-`company_job_id` before http; Done-when/user_prompt/Risk updated for binding abort risk.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject`
**Plan path:** `docs/features/meteorite/ast-1196-agent-task-synthesize-email-link-subject.md`

**Built tip:** `925178e6b1bf3da7fbb7447ca7da14358ae3a254` (`925178e6`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `925178e6` | qualify_meteorite cache/user prompts: email-link synthesize, subject title, empty-string fails, positional astral_job_id; surgical fixture lockstep |

### code-rubric.v1 verdict

[code-rubric] revision=1

**Rubric:** code-rubric.v1
**Ticket:** AST-1196
**Publish ref:** `9ec956e8` (`origin/sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject`)
**Overall:** CLEAN

Full active corpus (65 leaves — 18 universal + 47 scoped) swept in-session against this ticket's own diff footprint: `git diff origin/ftr/AST-1188-errors-for-qualify-meteorite-dispatch-task...origin/sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject` (paths `data/admin/agent_task.json`, `docs/uat-fixtures/AST-756/expected-agent_task.json`, `docs/features/meteorite/ast-1196-agent-task-synthesize-email-link-subject.md`, `docs/test-bible/core/repo_admin_json.md`, `tests/component/core/test_repo_admin_json.py`; change_types `{add, modify}`). Zero `src/` paths in this diff, so the entire `src/**`-scoped standards/state/layers/UI/batch/seed block is `not-applicable` on path; 6 scoped statutes apply and score `conforms` (`astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.betty-no-src-or-features`, `astral.git.engineer-test-tree-ban`, `astral.seed.define-approved`, `astral.seed.agent-tables-in-repo-json`); all 18 universal score `conforms`. No violations, no stragglers.

**Layer-mapping note (same gap Joan flagged at plan time):** `data/admin/**` isn't in the code-rubric's literal layer table (`src/data/**`→`data`; nothing maps top-level `data/`), so under a strict reading it contributes no layer and `astral.seed.agent-tables-in-repo-json` (layers `[core,data,utils]`) would score `not-applicable` despite its path (`data/admin/**`) matching. I scored it under the permissive reading Joan used at plan time (`data/admin` → `data` layer) so the directly-relevant statute isn't silently dropped by a rubric-table gap; verdict is `conforms` either way since there's nothing in this diff to violate it against (catalog row ships via repo JSON, no live-DB edit).

## Plan adherence

Verified mechanically, not just by reading the prose: (1) diffing `data/admin/agent_task.json` at `origin/ftr/AST-1188-...` vs the sub tip — exactly one `current==1` row changed (`qualify_meteorite`), matching Stage 1's pre/post snapshot gate; (2) same check on the AST-756 fixture — exactly one row changed there too, and `cache_prompt`/`user_prompt`/`updated_at` are byte-identical between catalog and fixture at the tip (no whole-file `cp`, no absorbed 53↔51 drift); (3) ran the plan's own Done-when assertion script against the shipped `cache_prompt`/`user_prompt` — all 13 substring checks pass, including the fragile never-candidate-mailbox sentence and the `00000000T000000Z` fallback shape Joan's round-2 review demanded. Both of Joan's round-1/round-2 fix-nows (empty-string vs null/omit; blind-`cp` fixture absorption) and both round-2 fix-nows (`astral_job_id` enumerated; never-drop row contract) are present verbatim in the shipped prompt, not just in the plan's prose.

**Pattern conformance:** cited In-scope ids `astral.git.engineer-test-tree-ban` conforms (engineer's `code(AST-1196)` commit touches only `data/admin/` + `docs/uat-fixtures/`, never `tests/`/`docs/test-bible/`). `astral.config.config-source-of-truth`, `astral.agent.do-task-delegation`, `astral.standards.in-scope-only`, `astral.standards.dry-and-focused-functions`, `astral.standards.no-hardcoded-sets` all score `not-applicable` on this diff (their path predicate is `src/**`; this child touches zero `src/` files) — same "mechanically excluded, scored in spirit" situation Joan already called out at plan time; nothing to add. **Advisory (recurring, not fix-now/discuss):** `pattern.config.config-block` / `pattern.batch.entity-claim-process-release` under Considered-but-excluded again aren't ids in the active corpus (no `pattern.*` namespace — same slip flagged on AST-1195's review); likely meant `astral.config.config-source-of-truth` / `astral.batch.claim-process-release`.

**What's solid:** Betty's Tests Ready fix for the stale AST-786 `len(rows)==48` gate replaces whole-file byte-identity with a catalog key-set lock (53 rows) plus a dedicated `TestAst1196QualifyMeteoritePromptContract` class that checks the shipped prompt text directly — closing exactly the gate the plan flagged as `[qa-handoff]` rather than an engineer `tests/` edit.

## Frame diff

(none) — implementation matches the plan doc's Files Changed / Stage 1 as written; no adds or moves applied to this description.

context_tokens≈75000

— Radia

---

## Resolution

**Date:** 2026-08-06  
**Review tip:** `e086bb26` (`docs(AST-1196): Radia review — clean`) — **Overall: CLEAN**

No fix-now or discuss items. Radia verified Stage 1 mechanically (single-row catalog/fixture diffs, Done-when assertions on shipped prompts, Joan R1/R2 fix-nows present in prompt text). Frame diff: none.

**Advisory noted (description only):** Considered-but-excluded `pattern.config.config-block` / `pattern.batch.entity-claim-process-release` are not active-corpus ids — corrected on Linear to `astral.config.config-source-of-truth` / `astral.batch.claim-process-release` (sibling-owned; still excluded for this child).

No product or test-tree changes on resolve.
