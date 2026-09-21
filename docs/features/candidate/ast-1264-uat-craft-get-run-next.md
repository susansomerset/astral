<!-- linear-archive: AST-1264 archived 2026-08-17 -->

## Linear archive (AST-1264)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1264/uat-craft-get-rubric-run-next-does-not-continue-to-craft-do-rubric  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-1243 — Candidate Artifacts now daisy chain  
**Blocked by / blocks / related:** parent: AST-1243

### Description

## What failed

On UAT for candidate `somerset` in `REQUESTED_ARTIFACTS`, dispatch ran `craft_get_rubric` successfully (LLM success, criteria persisted to `get_rubric`), but the daisy chain stopped there. Susan’s observation: `run_next` **for** `craft_do_rubric` **did not run.**

Log evidence (abbrev.): `do_task(craft_get_rubric).persist_candidate_craft … -> recorded` after a successful DeepSeek hop; no subsequent `craft_do_rubric` hop. Adjacent detail in the same run: `_capture_rubric_vector_feedback` reported `vector feedback unparseable` / `reason=unknown_code` (crafted codes TI/DC/… vs expected owner codes CR/GW/…).

## Expected

After `craft_get_rubric` succeeds, live `agent_task.run_next` continues the candidate artifacts chain (`craft_do_rubric` next, then the rest of the chain) with hop-visible execution history like `BUILD_ARTIFACTS`, persisting each hop until terminal graduation to `ARTIFACTS_READY`.

## Repro

1. Put a candidate in `REQUESTED_ARTIFACTS` with a dispatch task whose opening hop is `craft_get_rubric` (candidate entity).
2. Run the dispatch batch with debug on (or watch Railway/app logs).
3. Confirm `craft_get_rubric` completes and persists.
4. Observe whether `craft_do_rubric` (and later hops) appear in execution history / logs via `run_next`.

## Parent AC (quoted inline)

> 5. With the candidate in `REQUESTED_ARTIFACTS` and dispatch running, execution history shows the daisy chain progressing hop-by-hop comparably to `BUILD_ARTIFACTS`.

> 6. On successful completion, candidate is in `ARTIFACTS_READY` (or the configured success state) and each chain rubric’s new content is visible and editable under Artifacts nav.

> 8. No craft-rubric hop sequencing list is introduced in `config.py`; succession remains `agent_task.run_next`, and per-hop persistence matches the `BUILD_ARTIFACTS` job-artifact persist posture.

## Diagnosis

* **Hypothesis:** After a successful `craft_get_rubric` persist on the candidate `REQUESTED_ARTIFACTS` path, `do_task` does not recurse/`run_next` into `craft_do_rubric` (possible abort or suppress around vector-feedback `unknown_code`, candidate hop-label/claim path, or a remaining `suppress_run_next` / non–§2.6.0 path). Opening hop alone is not a complete chain.
* **Correct outcome:** Opening hop + every live `run_next` successor runs and persists; operator sees hop progression in execution history; terminal hop graduates to `ARTIFACTS_READY` with all chain rubrics populated.
* **Wrong fix to avoid:** Hard-coding hop order in `config.py`; treating “no stacktrace / get_rubric saved” as done; swallowing vector-feedback errors without restoring succession; inventing a second chain model beside `agent_task.run_next`.
* **Related siblings / contracts:** AST-1252 (dispatch chain + persist + retire wrappers); AST-1253 (Generate/Regenerate handoff — must still land on `REQUESTED_ARTIFACTS`). Live seed: `craft_get_rubric` → `craft_do_rubric` → …

## In scope

- [X] `pattern.dispatch.run-next-chain-authority` — restore live `agent_task.run_next` succession after `craft_get_rubric`
- [X] `astral.dispatch.run-next-is-chain-authority` — neuter fossil AST-1113 hardcoded craft edges; repo JSON remains chain authority
- [X] `astral.seed.boot-only-not-hot-path` — schema-ensure must not rewrite craft `run_next` (AST-1108 species)
- [X] `astral.state.no-daisy-chain-in-run` — succession only via documented `do_task` `run_next` carve-out
- [X] `astral.standards.debug-contract-gated` — Style D detail when candidate-craft persist hop has empty/invalid next
- [X] `astral.standards.in-scope-only` / `astral.standards.no-cross-contamination` / `astral.standards.dry-and-focused-functions` / `astral.standards.data-raises-caller-logs`

## Considered but excluded

- [X] `astral.ui.frontend-file-placement` / `astral.ui.naming-conventions` — Generate/Regenerate is AST-1253; no UI in this bug
- [X] Hop-order / sequencing lists in `config.py` — forbidden by parent AC8
- [X] Vector-feedback owner-code taxonomy / `unknown_code` — adjacent noise; capture already non-fatal
- [X] Resume daisy-chain / `craft_resume_base` automation — out of epic scope
- [X] `tests/` / `docs/test-bible/**` — Betty after Code Complete

## Boundaries

* This bug does **not** change Generate/Regenerate UI copy (AST-1253).
* This bug does **not** daisy-chain resume generation.
* "No more error in the log" alone is **not** done — Parent AC + Correct outcome must hold (full `run_next` succession).

## Git branch (authoritative)

Per orientation § Branch law / dispatch-parent §5c: seed `sub/AST-1243/<this-id>-uat-craft-get-run-next` from `origin/ftr/AST-1243-candidate-artifacts-now-daisy-chain`.

### Comments

#### chuckles — 2026-08-07T21:11:20.042Z
[merge-child] blocked: git pull merge on sub — `Merge remote-tracking branch` in ftr..sub (e.g. 11ab829d). Rewrite tip onto `origin/ftr/AST-1243-candidate-artifacts-now-daisy-chain`, cherry-pick only AST-1264 labeled commits, force-with-lease push `origin/sub/AST-1243/AST-1264-uat-craft-get-run-next`.

@Ada Lovelace

— Chuckles

#### radia — 2026-08-07T21:08:05.414Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1264
**Publish ref:** `origin/sub/AST-1243/AST-1264-uat-craft-get-run-next` @ `16de1579` (docs commit) / code tip `ec8456a5`
**Overall:** FIX-NOW

Full 65-statute sweep run in-session. `ftr/AST-1243-candidate-artifacts-now-daisy-chain` (AST-1252 + AST-1253) already landed on `origin/dev` before this branch cut, so `origin/dev...` is clean scope: this ticket's full contribution is `src/core/agent.py` + `src/data/database.py`.

## Stage 1 (migration neuter) — solid

`_apply_ast1113_craft_run_next_chain_migration` neutered to a bare `return`, docstring names repo JSON as authority, mirrors the AST-1108/AST-469/AST-834 no-op species exactly. Call site kept in `_ensure_agent_task_schema`. No replacement hop list anywhere. Betty's tests directly assert the no-op and lock the actual root cause (hot-path stomp bypassing `_validate_run_next_graph_acyclic`).

## Stage 2 (succession fix) — root cause fixed, one required sub-behavior is dead code

The primary reported bug (get→do stall) **is fixed correctly**: parent re-injects live `CALLER_*` onto `merged_ctx`; the child's `chain_context` (= `merged_ctx`) already carries those tokens, so `_live_caller` is `True` and `_hydrate_caller_chain_context` is skipped entirely — no `hydr_err`, chain continues. Confirmed by `test_persist_craft_reinjects_caller_on_recurse` / `test_persist_craft_skips_hydrate_when_live_caller`.

**fix-now — dead/unreachable fallback branch (this is Revision 1's own named fix-now):** the plan requires *"on `hydr_err`, if incoming `chain_context` still has any non-empty CALLER token, fall back to `effective_chain_context = chain_context`."* As coded (`src/core/agent.py` ~2006–2036), the `else:` branch that calls `_hydrate_caller_chain_context` is only reached when `_live_caller` (`_persist_craft and any(chain_context.get(k) for k in CALLER_HOP_TOKEN_NAMES)`) was already `False`. The `hydr_err` check re-evaluates that *identical* expression against the *same*, unmutated `chain_context` (`_hydrate_caller_chain_context` only reads its `chain_context` arg, per lines 881–907; no `await` in between) — so it's guaranteed `False` again. The fallback line can never execute; that path always falls through to the pre-existing hard `success=False` return. Betty's own two hydrate tests reflect the gap: one covers "live caller from the start → skip," the other "no live caller → hydrate fails → hard fail" — there's no (and, given this structure, can't be a) third "recovered via fallback" test.

**Recommend:** either drop the dead fallback block (the skip-hydrate path already covers the real recurse scenario — rescope the "fail-open" language to that case) or, if a genuine fallback is still wanted for hops reached some other way, source it from the actual re-injected data rather than re-checking the same unmutated `chain_context`.

Debug additions (`candidate_craft_persisted`-gated succession-stopped details) are correctly scoped. Non-`persist_candidate_craft_hops` callers (jobs, etc.) are unaffected — hydrate-or-fail semantics unchanged outside this ticket's scope.

## Plan adherence / boundaries

Files Changed matches exactly (2 files, no `config.py` hop list, no UI, no tests/bible from the engineer). Self-Assessment `Risk: HIGH` was earned — the dead fallback above is exactly the subtlety that flag was warning about. No cross-ticket scope creep (AST-1253 UI, resume daisy-chain, vector-feedback taxonomy, `agent_task.json` all untouched as planned).

## Pattern conformance

`pattern.dispatch.run-next-chain-authority` — conforms; succession stays on `agent_task.run_next` / repo JSON, no parallel hop list.

## Frame diff

(none — ticket description accurately describes the bug and fix scope)

context_tokens≈35000

— Radia

#### betty — 2026-08-07T21:00:33.334Z
## QA test manifest (AST-1264)

**Publish:** `origin/sub/AST-1243/AST-1264-uat-craft-get-run-next` @ `ec8456a5` (`merge-tests(AST-1264): origin/tests eaf4467a`)

### Broken / obsolete (revised this pass)
1. `TestAst1113CraftRunNextChainMigration` — migration now **no-op** (must not rewrite craft `run_next` / invent successors)

### Manifest
1. `tests/component/data/database/test_agent_tasks.py::TestAst1113CraftRunNextChainMigration`
2. `tests/component/core/test_agent.py::TestAst1264CandidateCraftSuccession`

### Narrowed run
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/data/database/test_agent_tasks.py::TestAst1113CraftRunNextChainMigration \
  tests/component/core/test_agent.py::TestAst1264CandidateCraftSuccession \
  -q
```

### Bible shasum (`origin/sub/…`)
- `docs/test-bible/core/agent.md` `e079094e0dae30c26edfdc611c0ad4a3f4c8515c84ee1c59e124d288ff6d407e`
- `docs/test-bible/core/candidate.md` `a75d4b23027b1049fbbcd1b18d69ef4270a62847e1b1ae9f2e7ff341401e74e2`
- `docs/test-bible/data/database/agent_tasks.md` `b87535d0c01eff4f9342aa0704b66b80a37559b077e6e787e10f9c7ce266089b`
- `docs/test-bible/utils/config.md` `0d4908e397aa1785b7aaf719f6996bb292618255ec5785a755c4f9374744f2e6`

**Integration:** none revised.

#### joan — 2026-08-07T20:53:30.787Z
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1264
**Overall:** APPROVED
**Publish ref tip:** `sub/AST-1243/AST-1264-uat-craft-get-run-next` @ `382834dd`

## Traceability

AC5→S1+S2; AC8→S1; AC9→S2 (Style D detail on stopped succession); AC6→explicitly deferred to UAT re-test with stated rationale. No orphan stages.

**Considered:** 51 (18 universal + 33 scoped); 14 scoped excluded on layer/path predicates. Scored in-session per R7. Plan layers `{data, core}`, Files Changed unchanged — no `violates` remaining.

## The fix-now is closed at the right place

Stage 2 now lands on the abort instead of beside it, and I checked the new anchors rather than the delta note. The revised step 2 targets the child hydration block at ~2004–2024 and gates on `(ctx or {}).get("persist_candidate_craft_hops")` — that works, because `ctx` is a `do_task` parameter (line 1925) and the recurse passes `ctx=ctx` (line 3097), so the child invocation genuinely sees the flag. I also confirmed there is only **one** `_hydrate_caller_chain_context` call inside `do_task` (line 2006), so the single site the plan patches is the whole exposure; `_hydrate_resume_entry_chain_context` has no call site on this path.

The two remedies are correctly ordered. Skipping hydration when live CALLER tokens are already present is the primary fix, and keeping the parent-side re-inject is what makes that possible — without it there would be no live tokens for the child to skip on. The `hydr_err` fall-back is belt-and-braces behind the same predicate, so with the re-inject in place it should never fire; that is fine as defensive depth, and it fails in the safe direction. Preserving the hard failure when there are **no** live CALLER tokens is the right call and keeps the existing contract for every caller that omits the flag.

The token-precedence claim is corrected rather than quietly dropped — the Diagnosis now states that `_merge_hydrated_caller_context` overwrites incoming CALLER with hydrated values. Stage 1's diagnosis picked up `astral.seed.boot-only-not-hot-path`, the AST-1108 precedent, and the raw-`UPDATE` bypass of `_validate_run_next_graph_acyclic`, all of which match what I verified in the tree. And the Stage 2 "Done when" is now outcome-shaped — `craft_do_rubric` proceeds when upstream agent_data is absent or empty — instead of asserting the contents of a dict, which was the specific thing that would have let a green stage sit on an unfixed bug.

AC6 took the second option I offered: UAT re-test owns terminal `ARTIFACTS_READY` and rubric visibility, with the reason stated. Appropriate — graduation is AST-1252's shipped behavior and cannot be exercised until succession works.

## Findings

No `fix-now`. One `discuss`, one `acceptable`:

### discuss — fail-open restores succession but could mask a thin audit trail, which is what AC5 actually asks for

Hydration fails when there is no stored agent_data RESPONSE row for the upstream hop on that entity, or when the stored hop's caller payload is empty (line 906). After Stage 2, the candidate craft chain proceeds regardless. That is the correct behavior for succession — but if the underlying reason those rows were missing is that hops on this path are not landing `agent_data` with `entity_id` set, then the chain will complete while execution history stays sparse. Parent AC5 is specifically "execution history shows the daisy chain progressing **hop-by-hop** comparably to `BUILD_ARTIFACTS`," so a chain that finishes without visible hops satisfies the bug's headline and misses the AC.

This is not a plan defect — you cannot diagnose why agent_data was missing until succession is restored, and the Style D detail in step 3 is the right instrument. **Recommendation:** carry one line into the UAT re-test so it checks that execution history shows all eight hops, not merely that the candidate reached `ARTIFACTS_READY`. Non-blocking.

### acceptable — the skip and fall-back branches share a predicate

Step 2 skips hydration when any non-empty CALLER token is present, then specifies a `hydr_err` fall-back conditioned on the same "any non-empty CALLER token" test. Given the parent re-inject, the skip always wins and the fall-back is unreachable. Harmless and arguably good defence, but worth knowing so nobody implements only the fall-back and expects it to catch the live case. Related nuance, also harmless: "any non-empty" is looser than "every referenced token present" — it makes no practical difference here because `_caller_chain_context_from_hop_agent_ref` rebuilds tokens through the same `_chain_tokens_for_next_hop` from the same inputs, so hydration cannot populate a token the live path left empty.

## Notes

Both stages now do real work at verified sites. Stage 1 removes a corrective, hot-path migration whose `craft_get_rubric` → `craft_like_rubric` edge is exactly Susan's symptom, which `astral.seed.boot-only-not-hot-path` independently requires and which AST-1108 already did for three sibling functions in the same file. Stage 2 removes the early `success=False` that would stop the chain even with the topology corrected. Those are two genuinely independent failure points on the same hop, which is why fixing only one would have produced a partial UAT result — worth remembering when the re-test runs, since a pass now depends on both.

The plan still resists all four of the bug's named wrong fixes: no config hop list, no treating "get saved / no exception" as done, no swallowing the vector-feedback `unknown_code` noise, and no second chain walker. Scoping every behavior change to `persist_candidate_craft_hops` keeps job `BUILD_ARTIFACTS` on today's hydrate-or-fail semantics, which is the containment that makes a `HIGH` risk plan approvable.

Self-assessment is honest and improved. `Risk: HIGH` is right and the risk line now names the real hazard — fail-open must stay gated, and empty CALLER plus `hydr_err` must still hard-fail. `Conf: high` is earned now that both fix sites are read out of source rather than hypothesised.

Status → **Plan Approved**.

context_tokens≈120000

— Joan

#### ada — 2026-08-07T20:51:05.729Z
[plan-discuss] round=1 reply

Plan revised on `origin/sub/AST-1243/AST-1264-uat-craft-get-run-next` @ `382834dd`.

**fix-now:** Stage 2 now fixes the child hydration abort — skip hydrate when live CALLER already present under `persist_candidate_craft_hops`; on `hydr_err` fall back to live tokens instead of `success=False`. Re-inject before recurse kept so the child actually receives those tokens. Done when asserts craft_do proceeds when upstream agent_data is absent/empty.

**Stage 1:** Diagnosis cites `astral.seed.boot-only-not-hot-path`, AST-1108 precedent, and raw UPDATE bypass of acyclic validate; neuter steps unchanged.

**discuss AC6:** UAT re-test owns terminal ARTIFACTS_READY / full rubric visibility after succession is restored.

Status stays Plan Discuss for Joan re-sweep.

#### joan — 2026-08-07T20:49:13.425Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1
**Rubric:** plan-rubric.v1
**Ticket:** AST-1264
**Overall:** REVISE
**Publish ref tip:** `sub/AST-1243/AST-1264-uat-craft-get-run-next` @ `3bf470c5`

## Traceability

AC5→S1+S2; AC8→S1; AC9→S2 (debug detail on stopped succession); AC6→unmapped (see discuss). No orphan stages.

**Considered:** 51 (18 universal + 33 scoped); 14 scoped excluded on layer/path predicates. Scored in-session per R7. Plan layers `{data, core}`.

**Mode note:** title starts with `UAT:` and the plan carries `## UAT fitness`, but the Description does not contain the `<!-- uat-validate: stacktrace -->` marker, so the UAT-thin predicate is not satisfied and I ran the full R1–R7 path. Nothing was penalized for it — this plan has a Files Changed table with layers, staged steps, self-assessment and a rules check, so it satisfies both modes' inputs. Flagging only so the fix-uat template can be fixed if the marker was meant to be there.

## Diagnosis 1 is real, and better supported than the plan argues

I went looking for the fossil and it is worse than described. `_apply_ast1113_craft_run_next_chain_migration` (`src/data/database.py:5041`) hard-codes a near-reversed topology against the live seed:

| fossil edge | live `agent_task.json` |
|---|---|
| `craft_get_rubric` → `craft_like_rubric` | `craft_get_rubric` → `craft_do_rubric` |
| `craft_do_rubric` → `craft_get_rubric` | `craft_do_rubric` → `craft_like_rubric` |
| `craft_prefilter_rubric` → `""` | `craft_prefilter_rubric` → `craft_company_search_terms` |

It has no `craft_evaluate_meteorite_rubric` edge at all, it is corrective rather than one-shot (it `UPDATE`s whenever the live value differs from its hardcoded expectation, so it re-stomps forever), and it is called from `_ensure_agent_task_schema` (line 5181) which is a per-process hot path reached from roughly ten call sites. `craft_get_rubric` → `craft_like_rubric` is precisely Susan's symptom that **`craft_do_rubric` did not run**.

Two supports the plan doesn't claim and should. First, the statute is not just `run-next-is-chain-authority` — it is `astral.seed.boot-only-not-hot-path`, which is in the considered set and whose **Violating** example is, verbatim, "a prompt-seed helper inside schema ensure on every connection open." The pre-fix code violates it; Stage 1 brings it into conformance. Second, the closest precedent is not AST-469/834 posture but **AST-1108**, three functions directly above this one (`_apply_ast776/822/880_...`), all neutered to bare `return` with a comment naming this exact failure: "Prior AST-776/822/880 migrations ran from `_ensure_agent_task_schema` once per process … the three overwrote each other forever." AST-1113 is the same species and was missed in that sweep.

Worth adding to the plan because it changes Stage 1 from a judgment call into a required correction: the migration writes `run_next` via raw `conn.execute("UPDATE agent_task SET run_next = …")` and `conn.commit()`, which **bypasses `_validate_run_next_graph_acyclic`**. So the one guard that would catch a malformed chain does not see these writes at all.

## Findings

### fix-now — Stage 2 does not fix the abort it diagnoses; the re-injected tokens are discarded before they are ever read

Diagnosis 2 is correct, and I confirmed the mechanism structurally rather than taking it as a hypothesis. `craft_get_rubric` references **no** CALLER tokens (it is the chain head); `craft_do_rubric` references **`CALLER_RESPONSE`**. On the get→do recurse, line 3074 sets `merged_ctx["_hop_parent_task_key"] = task_key`, so in the child invocation:

> `parent_for_hydration = (chain_context or {}).get("_hop_parent_task_key")` — truthy
> `if parent_for_hydration and index and entity_type_pre:`
>  `if _task_references_caller_tokens(agent_task_row, live_content):` — true for `craft_do_rubric`
>   `hydrated, hydr_err = _hydrate_caller_chain_context(…)`
>   `if hydr_err:`
>    `return {"success": False, "error": hydr_err, …}`

That early return (`src/core/agent.py:2014–2021`) fires **before** any LLM call and before the hop ledger, which is exactly "chain stopped after get, with little hop noise." `_hydrate_caller_chain_context` can fail two ways that both apply here — no stored agent_data for the upstream hop on that entity, or a stored hop whose caller payload is empty (line 906).

The problem is what Stage 2 proposes to do about it. Re-applying `caller_only_hop` onto `merged_ctx` just before `await do_task(effective_next, …)` changes neither half of that path:

- **The hydration gate does not consider whether CALLER tokens are already present.** It keys on `_hop_parent_task_key` + `index` + `entity_type` + whether the child's prompt references CALLER tokens. All four remain true with live tokens attached, so hydration still runs.
- **On `hydr_err` the function returns before the merge.** `_merge_hydrated_caller_context` at line 2022 is never reached, so the live tokens the plan carefully preserved are thrown away at line 2015.

Stage 2's "Done when" only asserts that `merged_ctx` still carries the CALLER values at recurse time. That can be fully satisfied while the chain still stops in exactly the same place — which makes it a green stage over an unfixed bug, and the bug's own Boundaries say "no more error in the log" alone is not done.

The parenthetical is also backwards in the other direction: the plan says "hydration may still run; live tokens win on overlap," but `_merge_hydrated_caller_context` (lines 915–917) copies hydrated CALLER keys **over** the incoming ones, so hydrated wins. On the happy path that is immaterial — `_caller_chain_context_from_hop_agent_ref` rebuilds the tokens by calling the same `_chain_tokens_for_next_hop` with the same inputs, so live and hydrated are the same values by construction — but the plan should not assert a precedence the code contradicts.

**Recommendation:** put the fix where the abort is. Either gate hydration to skip when the incoming context already carries populated CALLER tokens (`_is_chain_entry` / `_caller_key_status` already express that shape), or on `hydr_err` fall back to the incoming live tokens and continue instead of returning `success=False`. Then the Stage 2 "Done when" can assert the thing that matters — with the upstream agent_data row absent or empty, `craft_do_rubric` still runs from live tokens — rather than asserting the contents of a dict. Keep the `persist_candidate_craft_hops` gate; scoping the new behavior to the candidate craft path is the right call and keeps job chains on today's semantics.

One thing in the plan's favour worth keeping: this change makes the code honest about itself. Line 3085 already logs `caller_hydration=live_llm parent=…` on every recurse while the code strips every CALLER token one line earlier and forces a database round-trip. Passing live tokens is what that debug line has been claiming all along.

### discuss — AC6 is quoted in the bug but no stage demonstrates it

The bug quotes parent AC6 (`ARTIFACTS_READY` on completion, content visible under Artifacts nav) and the UAT fitness "Correct outcome" ends with "terminal success graduates to `ARTIFACTS_READY` with all chain rubrics populated." Both stages stop at succession; neither "Done when" reaches the terminal hop. Graduation is existing AST-1252 behavior (`dispatch_chain_graduate_on_terminal`), so I am not asking you to own it — but it has never been exercised, because the chain has never gotten past hop one. **Recommendation:** one line either mapping AC6 to a full-chain run in Stage 2's Done when (candidate ends in `ARTIFACTS_READY` with all eight hops recorded), or stating explicitly that AC6 verification belongs to the UAT re-test rather than this plan.

### acceptable — Stage 1's "usually re-applies" hedge

The Diagnosis says repo JSON "usually re-applies at bootstrap afterward." Given `_agent_task_schema_ensured` is a per-process module global and ensure is reachable from many entry points, the ordering genuinely varies by process, so the hedge is honest. It does not need resolving: neutering is correct regardless of whether the fossil won on Susan's particular run, and `astral.seed.boot-only-not-hot-path` requires it either way. Noting so nobody reads the hedge as doubt about Stage 1.

## Notes

The shape of this plan is right. It resists all four of the bug's named wrong fixes — no config hop list, no treating "get saved / no exception" as done, no swallowing the vector-feedback `unknown_code` noise (correctly identified as adjacent, since `_capture_rubric_vector_feedback` returns without failing the hop), and no second chain walker. Stage 1 is a genuine root-cause fix with statute backing stronger than the plan claims. The Stage 2 debug addition is well placed — emitting Style D detail when a successful candidate-craft persist hop has empty or invalid `effective_next` is exactly the observability that would have made this UAT self-diagnosing.

What blocks is that Stage 2's code change lands one layer away from the failure. The diagnosis is right and the referents are exact — `caller_only_hop` (3066), the `CALLER_HOP_TOKEN_NAMES` pop loop (3076–3077), and the recurse (3092) are all where the plan says — but the abort happens in the child invocation at 2014, not in the parent's recurse setup, and nothing in Stage 2 reaches it.

Self-assessment: `Risk: HIGH` is correct and I am glad it is not `Medium`. `Conf: high` is a little generous — the fossil half deserves it, but the succession half asserts a token-precedence behavior that the merge helper contradicts, which is the kind of thing `high` should have caught. Scope `Single-Component` is fair for two files.

context_tokens≈108000

— Joan

#### ada — 2026-08-07T20:41:47.359Z
Plan published on `origin/sub/AST-1243/AST-1264-uat-craft-get-run-next` @ `3bf470c5`.

[Plan doc](https://github.com/susansomerset/astral/blob/sub/AST-1243/AST-1264-uat-craft-get-run-next/docs/features/candidate/ast-1264-uat-craft-get-run-next.md)

**Scope:** Single-Component — neuter fossil AST-1113 craft `run_next` migration (`database.py`); keep live CALLER_* across `persist_candidate_craft_hops` recurse + debug empty succession (`agent.py`).

**Conf:** high — migration hardcodes `craft_get_rubric` → `craft_like_rubric` (skips do); repo JSON already has get→do; AST-1252 worker already omits `suppress_run_next`.

**Risk:** HIGH — wrong succession leaves REQUESTED_ARTIFACTS after a single hop or skips Do; CALLER re-inject must stay gated on the candidate craft persist flag.

---

# UAT: craft_get_rubric run_next does not continue to craft_do_rubric

**Linear:** [AST-1264](https://linear.app/astralcareermatch/issue/AST-1264/uat-craft-get-rubric-run-next-does-not-continue-to-craft-do-rubric)  
**Parent:** [AST-1243](https://linear.app/astralcareermatch/issue/AST-1243/candidate-artifacts-now-daisy-chain) — Candidate Artifacts now daisy chain  
**Publish ref:** `sub/AST-1243/AST-1264-uat-craft-get-run-next`

UAT on candidate `somerset` in `REQUESTED_ARTIFACTS` completed `craft_get_rubric` (persist recorded) but never entered `craft_do_rubric`. Restore live `agent_task.run_next` succession for the candidate artifacts dispatch path so the chain continues hop-by-hop after the opening hop.

## UAT fitness

- **AC restored:** Parent AST-1243 AC5 — “With the candidate in `REQUESTED_ARTIFACTS` and dispatch running, execution history shows the daisy chain progressing hop-by-hop comparably to `BUILD_ARTIFACTS`.” Parent AC6 — “On successful completion, candidate is in `ARTIFACTS_READY` … and each chain rubric’s new content is visible and editable under Artifacts nav.” Parent AC8 — “No craft-rubric hop sequencing list is introduced in `config.py`; succession remains `agent_task.run_next` …”
- **Correct outcome:** After `craft_get_rubric` succeeds and persists, `do_task` recurses into `craft_do_rubric` (then the rest of the live seed chain) with hop-visible execution history; terminal success graduates to `ARTIFACTS_READY` with all chain rubrics populated.
- **Sibling check:** AST-1252 native `do_task` + `persist_candidate_craft_hops` (no `suppress_run_next` on dispatch) remains the entry model — this ticket does not reintroduce a manual hop walk or wrapper keys. AST-1253 Generate/Regenerate handoff still only moves the candidate to `REQUESTED_ARTIFACTS` (unchanged). Live seed topology stays `craft_get_rubric` → `craft_do_rubric` → … (repo JSON authority).
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Hard-coding hop order in `config.py`; treating “get_rubric saved / no exception” as done; swallowing vector-feedback `unknown_code` noise as the fix (capture already returns without failing the hop); inventing a second chain model beside `agent_task.run_next`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/data/database.py` | Neuter `_apply_ast1113_craft_run_next_chain_migration` (bare `return`, same species as AST-1108 / AST-469 / AST-834) so schema-ensure cannot rewrite craft `run_next` away from repo JSON | data |
| `src/core/agent.py` | Candidate-craft path: pass live `CALLER_*` into recurse **and** skip/fail-open hydration when those live tokens are already present; Style D debug when a successful candidate-craft persist hop has empty / invalid `effective_next` | core |

**Out of this ticket’s file list (do not touch):** `config.py` hop lists, Generate/Regenerate UI (AST-1253), `tests/` / bible (Betty), resume daisy-chain, vector-feedback owner-code taxonomy, `data/admin/agent_task.json` craft topology (already correct on tip: `craft_get_rubric` → `craft_do_rubric`).

## Diagnosis (planner)

1. **Fossil migration stomps succession (root cause for skipped `craft_do_rubric`).** `_apply_ast1113_craft_run_next_chain_migration` (`database.py`) hard-codes a near-reversed topology vs live seed — notably `craft_get_rubric` → `craft_like_rubric` (skips do) and `craft_do_rubric` → `craft_get_rubric`. It is **corrective** (re-`UPDATE`s whenever live differs), called from `_ensure_agent_task_schema` (per-process hot path, many call sites), and writes via raw `conn.execute` + `conn.commit()` that **bypass `_validate_run_next_graph_acyclic`**. That is exactly the **Violating** shape of `astral.seed.boot-only-not-hot-path` (“prompt-seed helper inside schema ensure on every connection open”). Closest precedent is **AST-1108** (three migrations directly above this one already neutered for the same forever-overwrite failure); AST-1113 was missed in that sweep. Repo JSON usually re-applies at bootstrap afterward, but ordering varies by process — neuter regardless. Matches Susan’s symptom that **`craft_do_rubric` did not run**.
2. **Hydration abort on the child hop (same-invocation succession).** After a successful hop, `do_task` strips `CALLER_*` from `merged_ctx`, sets `_hop_parent_task_key`, and recurses. `craft_do_rubric` references `CALLER_RESPONSE`; the child always enters `_hydrate_caller_chain_context` when that parent key is set. On `hydr_err` (`agent.py` ~2014–2021) the child returns `success=False` **before** LLM / hop ledger — chain stops after get with little hop noise. **Re-injecting CALLER onto `merged_ctx` alone does not fix this:** the hydration gate does not check whether CALLER is already populated, and on `hydr_err` the function returns before `_merge_hydrated_caller_context`. Fix must land at the hydration abort (skip when live CALLER already present, and/or fall back to live tokens on `hydr_err`), scoped to `persist_candidate_craft_hops`. Note: `_merge_hydrated_caller_context` overwrites incoming CALLER with hydrated values (hydrated wins on overlap) — do not claim the opposite.

Vector-feedback `unknown_code` / `unparseable` on get is adjacent noise only — `_capture_rubric_vector_feedback` returns without failing the hop.

**AC6:** Terminal `ARTIFACTS_READY` + full rubric visibility is existing AST-1252 graduation/persist behavior. This plan restores succession so a full chain can complete; **AC6 verification belongs to the UAT re-test** after Code Complete / Tests Passed (not a compile-time Done when on these stages).

## Stage 1: Neuter AST-1113 craft run_next migration

**Done when:** `_apply_ast1113_craft_run_next_chain_migration` is a no-op (`return` only, docstring notes superseded by repo JSON / live seed headed by `craft_get_rubric`, cites AST-1108 / `astral.seed.boot-only-not-hot-path`); `rg '_apply_ast1113_craft_run_next_chain_migration' src/data/database.py` still shows the call site in `_ensure_agent_task_schema` (keep the hook, empty body); no new hop-order list in `config.py`; `python3 -m py_compile src/data/database.py` succeeds.

1. In `src/data/database.py`, replace the body of `_apply_ast1113_craft_run_next_chain_migration` with an immediate `return` (mirror AST-1108 / `_apply_ast469_select_job_page_run_next_migration`). Update the docstring: AST-1113’s hardcoded craft succession is retired — `data/admin/agent_task.json` applied at bootstrap is the sole craft `run_next` authority (`astral.dispatch.run-next-is-chain-authority`); schema-ensure must not rewrite prompt/chain edges (`astral.seed.boot-only-not-hot-path`).
2. Do **not** delete the call from `_ensure_agent_task_schema` (keeps the migration slot visible). Do **not** add a replacement hardcoded chain. Do **not** edit `data/admin/agent_task.json` in this ticket.

⚠️ **Decision:** Neuter rather than rewrite the migration to the current seed chain — a second hardcoded list would drift again and still violate boot-only-not-hot-path. Repo JSON already encodes `craft_get_rubric` → `craft_do_rubric` → ….

## Stage 2: Live CALLER on candidate-craft recurse + hydration fail-open + debug

**Done when:** With `(ctx or {}).get("persist_candidate_craft_hops")` truthy, a successful `craft_get_rubric` hop that has non-empty live CALLER tokens from `_chain_tokens_for_next_hop` can recurse into `craft_do_rubric` **even when upstream agent_data for that hop is absent or empty** (hydration skipped or `hydr_err` falls back to live tokens — child does **not** return `success=False` solely for hydration miss); job / non-persist paths keep today’s hydrate-or-fail semantics; when persist_candidate_craft just recorded success and `effective_next` is empty or not in `TASK_CONFIG`, `debug=True` emits a Style D detail naming `task_key` and `planned_next` / reason; UI `suppress_run_next` path unchanged; `python3 -m py_compile src/core/agent.py` succeeds.

1. In `src/core/agent.py`, in the `run_next` dispatch block (after `hop_ctx = _chain_tokens_for_next_hop(...)` and the existing `caller_only_hop` / `non_caller_hop` split, before `await do_task(effective_next, …)`):
   - If `(ctx or {}).get("persist_candidate_craft_hops")` and `effective_next`: after the existing loop that `pop`s `CALLER_HOP_TOKEN_NAMES` from `merged_ctx`, **re-apply** each non-empty value from `caller_only_hop` whose key is in `CALLER_HOP_TOKEN_NAMES` onto `merged_ctx` (so the child invocation actually receives live CALLER — matches the existing `caller_hydration=live_llm` debug claim).
2. In the **child** hydration block near the top of `do_task` (where `parent_for_hydration` + `_hydrate_caller_chain_context` run, ~2004–2024), when `(ctx or {}).get("persist_candidate_craft_hops")` is truthy:
   - If incoming `chain_context` already has any non-empty `CALLER_HOP_TOKEN_NAMES` value (same shape `_caller_key_status` inspects): **skip** `_hydrate_caller_chain_context` and keep `effective_chain_context = chain_context`.
   - Else run hydrate as today; on `hydr_err`, if incoming `chain_context` still has any non-empty CALLER token, **fall back** to `effective_chain_context = chain_context` and continue (do not return `success=False`); only return the hard failure when there are no live CALLER tokens to fall back to.
   - Do **not** change hydrate-or-fail for callers that omit `persist_candidate_craft_hops`.
3. When persist_candidate_craft just succeeded and later `not effective_next` or `effective_next not in TASK_CONFIG`, if `debug=True`, emit `debug_detail` explaining succession stopped (`planned_next=…`, `suppress_run_next=…`, or `invalid_child=…`).
4. Do **not** set `suppress_run_next` on the dispatch worker. Do **not** add hop sequencing in config. Do **not** change vector-feedback capture.

⚠️ **Decision:** Fix at the hydration abort (skip / fail-open), not only at the parent recurse setup. Re-inject remains necessary so live tokens exist for the child to skip/fall back on. Scoped to `persist_candidate_craft_hops` so job `BUILD_ARTIFACTS` hydration semantics stay unchanged.

## Execution contract

- Stages in order; one commit per stage on the epic worktree sub; publish to `origin/sub/AST-1243/AST-1264-uat-craft-get-run-next` after each stage per build-child.
- No files outside the Files Changed table.
- Ambiguity or drift → stop and comment on **parent** AST-1243 with the Stage N blocked template.
- Betty owns test/bible updates after Code Complete — engineer does not patch `tests/`.

## Revisions

### Revision 1 — 2026-08-07
Driven by: Joan `[plan-discuss] round=1 concern` (plan-rubric.v1 REVISE @ `3bf470c5`).
Changes:
- **fix-now:** Stage 2 now fixes the child hydration abort (skip when live CALLER present; fall back on `hydr_err`) — re-inject alone was insufficient because hydrate still runs and returns before merge.
- **Stage 1:** Strengthened diagnosis — `astral.seed.boot-only-not-hot-path`, AST-1108 precedent, raw UPDATE bypasses acyclic validate; neuter rationale unchanged.
- **discuss AC6:** Explicitly UAT re-test owns terminal `ARTIFACTS_READY` / full rubric visibility after succession is restored.
- Corrected token-precedence note: hydrated overwrites incoming on merge.

## Self-Assessment

**Scope:** `Single-Component` — data-layer migration neuter plus a narrow `do_task` succession/hydration hardening for the candidate craft persist flag; no new modules or UI.

**Conf:** `high` — fossil migration edges and the hydration early-return are both readable in source; Joan confirmed the Stage 2 abort site; AST-1252 worker already omits `suppress_run_next`.

**Risk:** `HIGH` — wrong succession leaves REQUESTED_ARTIFACTS after a single hop or skips Do; hydration fail-open must stay gated on `persist_candidate_craft_hops` so job chains do not change; empty CALLER + hydr_err must still hard-fail.

## Rules check

- **§2.6.0 / `astral.dispatch.run-next-is-chain-authority`:** Neuter hardcoded migration; succession stays `agent_task.run_next` / repo JSON — no config hop list.
- **`astral.seed.boot-only-not-hot-path`:** Stage 1 removes prompt/chain rewrite from schema-ensure hot path.
- **`astral.state.no-daisy-chain-in-run`:** Still uses the documented `do_task` `run_next` carve-out only.
- **§1.3 DRY / in-scope-only:** No second chain walker; no AST-1253 UI; vector-feedback taxonomy out of scope.
- **Betty test-tree ban:** No `tests/` / bible edits in this plan.
- **No conflict requiring conf-!!-NONE.**

## Review

**Publish ref:** `origin/sub/AST-1243/AST-1264-uat-craft-get-run-next`  
**Tip:** `02bed622`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `6b00f250` | neuter AST-1113 craft run_next hot-path migration |
| 2 | `02bed622` | live CALLER re-inject; hydrate skip/fail-open; succession debug |

## Radia review

[code-rubric] revision=1

**Rubric:** code-rubric.v1
**Publish ref tip:** `ec8456a5`
**Overall:** FIX-NOW

**Full-set sweep:** all 65 active statutes scored in-session (18 universal + 47 scoped). `origin/dev...origin/sub/AST-1243/AST-1264-uat-craft-get-run-next` is already clean scope for this ticket — `ftr/AST-1243-candidate-artifacts-now-daisy-chain` (AST-1252 + AST-1253) landed on `origin/dev` before this branch was cut, so the two-file diff (`src/core/agent.py`, `src/data/database.py`) is this ticket's full and only contribution.

**Stage 1 — solid:** `_apply_ast1113_craft_run_next_chain_migration` neutered to a bare `return` with a docstring naming repo JSON as authority, mirroring the AST-1108/AST-469/AST-834 no-op species exactly. Call site kept in `_ensure_agent_task_schema` (migration slot stays visible). No replacement hop list added anywhere. `python3 -m py_compile` clean. Betty's tests directly assert the no-op (wrong links left untouched, no ghost rows invented, source body is `return`-only) — good regression lock on the actual root cause (hot-path stomp bypassing `_validate_run_next_graph_acyclic`).

**Stage 2 — root-cause fix confirmed, but one required sub-behavior is dead code:**

- The primary reported bug (get→do stall) is fixed correctly: the parent's re-injection of live `CALLER_*` onto `merged_ctx` (gated on `persist_candidate_craft_hops` + `effective_next`) means the child's `chain_context` (passed as `merged_ctx` into the recursive `do_task` call) already carries live CALLER tokens, so the child's `_live_caller` check is `True` and `_hydrate_caller_chain_context` is skipped entirely — no `hydr_err` early-return, chain continues. Confirmed by `test_persist_craft_reinjects_caller_on_recurse` and `test_persist_craft_skips_hydrate_when_live_caller`.

- **fix-now — dead/unreachable fallback branch (Stage 2 step 2, Revision 1's own fix-now):** The plan (and Joan's round-1 revision) explicitly require: *"on `hydr_err`, if incoming `chain_context` still has any non-empty CALLER token, fall back to `effective_chain_context = chain_context`."* As coded (`src/core/agent.py` ~2006–2036), the `else:` branch that calls `_hydrate_caller_chain_context` is only reached when `_live_caller` (`_persist_craft and any(chain_context.get(k) for k in CALLER_HOP_TOKEN_NAMES)`) was already `False`. The `hydr_err` branch re-evaluates the *identical* expression against the *same* `chain_context` — which is never mutated between the two checks (no `await`, and `_hydrate_caller_chain_context` only reads its `chain_context` argument, per `src/core/agent.py:881-907`) — so it is guaranteed to evaluate `False` again. The fallback `effective_chain_context = chain_context` at line ~2028 can never execute; that scenario always falls through to the pre-existing hard `success=False` return. Betty's own test suite reflects this gap: `test_persist_craft_hydrate_hard_fails_without_live_caller` exercises "no live caller → hydrate fails → hard fail," and `test_persist_craft_skips_hydrate_when_live_caller` exercises "live caller from the start → hydrate skipped" — there is no (and, given the current structure, cannot be a) third test for "no live caller initially, hydrate fails, tokens recovered for fallback," because that branch is unreachable. Recommend: either drop the dead fallback block (skip-hydrate already covers the real recurse path — re-scope the plan's "fail-open" language to the skip case only) or, if a genuine fallback is still wanted for hops reached via a path other than direct parent re-inject (e.g. resumed/retried hops where `chain_context` might legitimately differ from what was checked), source the fallback from the actual re-inject data (`hop_ctx`/`caller_only_hop` equivalent) rather than re-checking the same unmutated `chain_context`.

- Debug additions (`candidate_craft_persisted` gating the two new `debug_detail` succession-stopped lines) are correctly scoped and match Stage 2 step 3 — fires only after a real persist, on both the clean-terminal (`planned_next` empty) and invalid-child paths.

- Non-`persist_candidate_craft_hops` paths (jobs, etc.) are unaffected: `_persist_craft` short-circuits `_live_caller` to `False` unconditionally, so hydrate-or-fail semantics are unchanged for every caller outside this ticket's scope.

**Plan adherence:** Files Changed table matches exactly (2 files, no config.py hop list, no UI, no tests/bible from the engineer). Self-Assessment `Risk: HIGH` was earned — the dead fallback above is exactly the kind of subtlety that risk flag was warning about. No `!!-NONE` conflict.

**Cross-ticket boundary:** No AST-1253 UI touched; no resume daisy-chain; no vector-feedback taxonomy changes; `data/admin/agent_task.json` untouched as planned.

**Pattern conformance:** `pattern.dispatch.run-next-chain-authority` — conforms; succession stays on `agent_task.run_next` / repo JSON, no parallel hop list introduced anywhere (config.py untouched).

## Frame diff

(none — ticket description accurately describes the bug and fix scope)

context_tokens≈31000

— Radia

## Resolution

**Date:** 2026-08-07  
**Publish tip before resolve:** `16de1579` (`docs(AST-1264): Radia review — findings`)

| Finding | Disposition |
|---------|-------------|
| fix-now (dead/unreachable `hydr_err` fallback) | Fixed — removed the unreachable fallback; fail-open is the `_live_caller` skip path after parent re-inject. No-live-caller + hydrate miss still hard-fails. |
