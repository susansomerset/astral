<!-- linear-archive: AST-1779 archived 2026-10-02 -->

## Linear archive (AST-1779)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1779/empty-token-predicate-helper-dispatch-validation  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1766 — Dispatch Validation  
**Blocked by / blocks / related:** parent: AST-1766; blocks: AST-1781; blocks: AST-1780

### Description

## What this implements

Owns the shared empty-render helper in config (all prompt fields + agent system; candidate-scoped scoring; ignore chain; extension seam for future entity contexts). Does not own API gates, force-off persistence, version hooks, or React.

## Citations

`astral.dispatch.entity-state-bound`; patterns: none for the helper itself (`no established pattern applies` beyond `TOKEN_SOURCES` / `resolve_tokens` reuse).

## Scope

`src/utils/config.py` — new empty-render helper over `TOKEN_SOURCES` / `resolve_tokens` across all `agent_task` prompt segments plus agent system text; scores candidate-scoped tokens only; ignores `source: chain`; optional entity-context extension seam for later entity types.

## Acceptance criteria

- [X] Predicate **A** (candidate-scoped): helper returns `empty_render: true` / `empty_tokens` when a referenced candidate-source or candidate-backed artifact token resolves to `""` for that candidate; list field name frozen as `empty_render` for sibling #2 `GET /api/admin/dispatch_tasks` enrichment. **Fail:** flag missing, or `false` while such a token resolves blank.
- [X] The empty-render helper ignores `source: chain`, does **not** treat empty `source: job` (or other non-candidate entity) tokens as a failing check in this epic, and exposes an extension point (`entity_contexts`) so a later epic can score other entity types without replacing the helper. **Fail:** job emptiness flips the flag true in this epic’s behavior, or the helper is a sealed candidate-only function with no documented extension seam.
- [X] Candidate-scoped tokens all non-empty → `empty_render: false` even when prompts also reference job tokens that would be blank without a job context (AUTO/Run enablement subject to sibling #2/#4 + existing API-key / Sweep rules). **Fail:** controls disabled solely because job tokens are empty.

## Boundaries

Does not own API gates, force-off persistence, version hooks (siblings #2/#3), or React (sibling #4).

## Notes for planning

Parent AST-1766 definition is authoritative. Candidate-scoped only this epic; leave room for entity-type expansion.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1766-dispatch-validation`, child `sub/AST-1766/AST-1779-empty-token-predicate-helper`. Created at dispatch-parent.

## QA test manifest

1. Blank candidate → empty_render: `tests/component/utils/test_config.py::TestAst1779EmptyRenderForPrompts::test_blank_candidate_token_sets_empty_render`
2. Job ignored without seam: `tests/component/utils/test_config.py::TestAst1779EmptyRenderForPrompts::test_filled_candidate_ignores_blank_job_without_entity_contexts`
3. Chain never scored: `tests/component/utils/test_config.py::TestAst1779EmptyRenderForPrompts::test_chain_only_never_scores`
4. Job entity_contexts seam: `tests/component/utils/test_config.py::TestAst1779EmptyRenderForPrompts::test_job_seam_via_entity_contexts`
5. warn_on_empty quiet: `tests/component/utils/test_config.py::TestAst1779EmptyRenderForPrompts::test_warn_on_empty_false_suppresses_empty_warning`
6. Text tolerance + order: `tests/component/utils/test_config.py::TestAst1779EmptyRenderForPrompts::test_none_empty_and_non_str_texts_and_order`
7. Rubric seam: `tests/component/utils/test_config.py::TestAst1779EmptyRenderForPrompts::test_rubric_scored_only_via_entity_contexts`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1779EmptyRenderForPrompts \
  -q
```

**Bible shasum (publish tip):**

* `docs/test-bible/utils/config.md` — `f1eb18591b1dadc37aa399cb85319f830ca298d8`

**Publish tip:** `origin/sub/AST-1766/AST-1779-empty-token-predicate-helper` @ `b2e9b13bf861fbe122632f29ab8337c3fbc7c0f8`

### Comments

#### radia — 2026-09-23T01:32:23.749Z
[code-rubric] PROCEED (Commit: b2e9b13b) empty-render helper clean

#### betty — 2026-09-23T01:29:01.072Z
`origin/sub/AST-1766/AST-1779-empty-token-predicate-helper` @ `b2e9b13b` · empty-render manifest

#### joan — 2026-09-23T01:22:08.122Z
[plan-rubric] PROCEED (Commit: 8a6488d039f0f6243602e75312b9b5a8a8113231) helper plan clean

#### ada — 2026-09-23T01:19:54.369Z
`origin/sub/AST-1766/AST-1779-empty-token-predicate-helper` @ `8a6488d039f0f6243602e75312b9b5a8a8113231` · empty-render helper planned

---

# AST-1779 — Empty-token predicate helper

- **Linear:** https://linear.app/astralcareermatch/issue/AST-1779
- **Parent:** AST-1766 — Dispatch Validation
- **Publish ref:** `sub/AST-1766/AST-1779-empty-token-predicate-helper`

Shared empty-render predicate in `config.py`: scan prompt texts (all `agent_task` prompt segments plus agent system text) for `{$TOKEN}` names, score **candidate-scoped** tokens via existing `TOKEN_SOURCES` / `resolve_tokens`, ignore `source: chain`, do not fail on empty job/other non-candidate entity tokens in this epic, and leave an optional entity-context extension seam so later epics can score other entity types without replacing the helper. Does not own API enrichment, AUTO/Run gates, version hooks, or React (siblings #2–#4).

## UAT fitness

- **AC restored:** Parent AST-1766 AC 1, 9, and 10 (this child’s AC 1–3): “Predicate **A** (candidate-scoped): for a row whose prompts (all `agent_task` prompt fields + agent system) reference a candidate-source or candidate-backed artifact token that resolves to `""` for that row’s candidate, … an explicit boolean … that is `true` for empty-render”; “The empty-render helper ignores `source: chain`, does **not** treat empty `source: job` (or other non-candidate entity) tokens as a failing check in this epic, and exposes an extension point …”; “A row whose candidate-scoped tokens all resolve non-empty keeps AUTO and Run/Sweep enabled … even if prompts also reference job tokens that would be blank without a job context.”
- **Correct outcome:** Callers (sibling #2 list enrichment / gates; sibling #3 revalidation) get a reliable `empty_render` boolean plus the token names that scored blank, so operators only lose AUTO/Run when **candidate-scoped** prompt fills would actually be empty for that row’s candidate — not when job/chain tokens are blank at admin-list time.
- **Sibling check:** #2 (`api_admin` list flag + AUTO/Run 400 + force AUTO off) and #3 (agent_task / artifact version hooks) and #4 (UI disable) all consume this helper’s return shape / field name `empty_render`; they must not reimplement token scoring. Verified by this plan freezing the helper signature and the list-row field name; siblings wire only.
- **Not sufficient:** Removing empty-token log noise alone, or returning a hardcoded `false`, is not done — the predicate must detect real blank candidate-scoped resolutions.
- **Wrong fix rejected:** Sealing a candidate-only helper with no extension seam (fails AC 9 / child AC 2). Treating empty `source: job` (or rubric/pronoun/config/chain) as a fail in this epic’s default call path (fails AC 9–10). Building a second token map beside `TOKEN_SOURCES` / `resolve_tokens` (violates parent Architectural definition).

## Explicit scope gate

Ticket **## Scope** covers only:

- `src/utils/config.py` — new empty-render helper over `TOKEN_SOURCES` / `resolve_tokens` across all `agent_task` prompt segments plus agent system text; scores candidate-scoped tokens only; ignores `source: chain`; optional entity-context extension seam for later entity types.

No other files. Do not edit `api_admin.py`, `database.py`, `candidate.py`, or `AdminScheduledActions.tsx`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `warn_on_empty` to `resolve_tokens`; add `empty_render_for_prompts` helper (+ thin docstring contract for sibling field name `empty_render`) | utils |

## Stage 1: Quiet resolve + empty-render helper

**Done when:** `empty_render_for_prompts` is importable from `src.utils.config`. Given prompt texts that reference `{$FIRST_NAME}` and a candidate token view where `first` is `""`, the helper returns `{"empty_render": True, "empty_tokens": ["FIRST_NAME"]}` (order of names: first-seen across texts). The same texts with a non-empty `first` and an additional `{$VISIBLE_JD}` reference return `empty_render: False` when `entity_contexts` is omitted or has no `"job"` entry. Texts that only reference `{$CALLER_RESPONSE}` / other `source: chain` tokens return `empty_render: False`. Passing `entity_contexts={"job": {}}` with a `{$VISIBLE_JD}` reference returns `empty_render: True` and includes `VISIBLE_JD` in `empty_tokens` (extension seam). Calling `resolve_tokens` with default kwargs still emits empty-token WARNINGs as today; the helper’s internal resolves do not.

1. In `src/utils/config.py`, on `resolve_tokens`, add keyword-only argument `warn_on_empty: bool = True` after the existing keyword-only hop args (`chain_entry`, `parent_task_key`, `parent_caller_summary`). Gate **every** existing `_log.warning(...)` inside `_replace` that fires because a token resolved empty / unresolved on this path behind `if warn_on_empty:` — candidate empty, chain empty, job empty, rubric unresolved/missing-id. Do **not** change substitution results. Default `True` preserves current call-site behavior.

2. Immediately after `resolve_tokens` (before `validate_value`), add:

   ```python
   def empty_render_for_prompts(
       prompt_texts: list[str] | tuple[str, ...] | None,
       candidate_data: dict,
       task_key: str,
       *,
       entity_contexts: dict[str, dict[str, str]] | None = None,
   ) -> dict:
   ```

   Contract (document in the docstring; sibling #2 maps this onto each `dispatch_task` list row):

   - Returns `{"empty_render": bool, "empty_tokens": list[str]}`.
   - `empty_render` is `True` iff `empty_tokens` is non-empty.
   - `empty_tokens` is ordered-unique token names that **scored** and resolved to exactly `""` (no `.strip()` — match parent AC’s `""`).
   - List / gate API field name for the boolean is **`empty_render`** (sibling #2; this ticket only defines the name so the epic stays consistent).

3. Implementation rules for `empty_render_for_prompts` (literal — do not invent alternate scanners):

   - Treat `prompt_texts is None` as no texts. Skip non-str / empty-string entries (same tolerance as `list_artifact_keys_in_prompt_texts`).
   - Collect referenced names by scanning each text with existing `_TOKEN_RE` (`\{\$([A-Z_]+)\}`), preserving first-seen order across texts (same uniqueness style as `list_artifact_keys_in_prompt_texts`).
   - For each name, look up `TOKEN_SOURCES.get(name)`. If missing → skip (forward-compat; leave unrecognized placeholders alone, same as `resolve_tokens`).
   - **Score** a name only when:
     - `spec["source"] == "candidate"` (covers candidate `data_field` and candidate-backed `artifact` rows), **or**
     - `entity_contexts` is a dict and `spec["source"]` is a key in `entity_contexts` (extension seam — e.g. `"job"`).
   - **Never score** when `spec["source"] == "chain"` (even if somehow present under `entity_contexts`).
   - **Do not score** `pronoun`, `rubric`, `config`, `output_type`, or any other source that is neither `candidate` nor a key present in `entity_contexts`.
   - For a scored name, resolve with a single-token template and `warn_on_empty=False`:

     ```python
     resolved = resolve_tokens(
         "{$" + name + "}",
         candidate_data or {},
         task_key,
         chain_context=None,
         job_context=(entity_contexts or {}).get("job") if spec["source"] == "job" else None,
         warn_on_empty=False,
     )
     ```

     For non-`job` entity sources supplied via `entity_contexts`, pass them the same way only if `resolve_tokens` already has a matching kwarg today — **today only `job_context` exists**. Do **not** add new `resolve_tokens` context kwargs in this ticket. If `spec["source"]` is in `entity_contexts` but is not `"job"`, still treat the name as scored and resolve via `resolve_tokens("{$NAME}", …)` with `warn_on_empty=False` and no extra context (value will be `""` until a later epic extends `resolve_tokens`); document that limitation in a one-line comment on the helper. This keeps the seam callable without inventing a second resolver.
   - If `resolved == ""`, append `name` to `empty_tokens` (skip if already present).
   - Return `{"empty_render": bool(empty_tokens), "empty_tokens": empty_tokens}`.

4. Callers of the helper (not this ticket) are responsible for assembling the text list from the current `agent_task` row plus agent system content, in this order when they have the rows:

   - `agent_task["system_prompt"]`
   - `agent_task["cache_prompt"]`, `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d`
   - `agent_task["nocache_prompt"]`
   - `agent_task["user_prompt"]`
   - agent `system` / system-prompt field (whatever sibling #2 already loads for preview — same string they would pass through `resolve_tokens` today)

   This ticket does **not** load DB rows. Document the expected text set in the helper docstring as “all prompt segments the caller intends to gate (typically every `agent_task` prompt column + agent system text).”

⚠️ **Decision:** Field name is `empty_render` (not `prompts_empty` / `token_gap`) — short, matches parent wording “empty-render”, and is the boolean siblings put on the list row and gates.

⚠️ **Decision:** Score via per-token `resolve_tokens("{$NAME}", …, warn_on_empty=False)` rather than re-walking paths — honors parent “no second token map”, keeps `serialize: resume_sections_json` / artifact behavior identical to runtime fills, and avoids WARNING spam when sibling #2 enriches every Scheduled Actions poll.

⚠️ **Decision:** Exact `== ""` after resolve — no whitespace strip. Parent AC says resolves to `""`; stripping would invent a stricter gate than the runtime substitution check.

⚠️ **Decision:** Default epic call path omits `entity_contexts` (or passes `None`) so empty job tokens never flip `empty_render`. Sibling #2/#3 must not pass a job context for this epic’s gates.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1779
**Overall:** APPROVED
**Corpus:** 2ac86c3f693409c364f8630a97198c8dbfa9c6f3
**Publish ref:** `8a6488d039f0f6243602e75312b9b5a8a8113231`

## Canon scores

| slug | grade | effort | note |
|------|-------|--------|------|
| astral.dispatch.entity-state-bound | A | | |

## Traceability

AC1→Stage 1 (`empty_render` / `empty_tokens` contract; field name frozen for sibling #2 list enrichment); AC2→Stage 1 (scoring rules: `source==candidate` only by default, chain never scored, `entity_contexts` extension seam); AC3→Stage 1 (done-when: non-empty candidate tokens + `{$VISIBLE_JD}` without job context → `empty_render: False`). Parent AC 1, 9, 10 → Stage 1; parent AC 2–8 out of child Scope (siblings #2–#4).

## Findings

### discuss — Canon Scope gap (do not score)

- **Severity:** discuss
- **Location:** Ticket Citations vs plan footprint
- **Finding:** `astral.standards.in-scope-only` plainly governs a single-file config helper but is absent from the frozen one-id list.
- **Recommendation:** Plan is compliant via `## Explicit scope gate` (config.py only). Archie may amend Canon Scope at Discussion for Radia comparability; no plan change required.

### acceptable — UAT fitness block on non-UAT child

- **Severity:** acceptable
- **Location:** `## UAT fitness`
- **Finding:** Section present though this is not UAT-thin mode; content correctly maps parent AC 1/9/10 and sibling boundaries.
- **Recommendation:** None.

context_tokens≈18500

## Review (build stub)

**Publish ref:** `origin/sub/AST-1766/AST-1779-empty-token-predicate-helper`
**Tip:** `09e353f5`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `09e353f5` | `warn_on_empty` on `resolve_tokens` + `empty_render_for_prompts` |

## Radia review

[code-rubric]
**Ticket:** AST-1779
**Publish ref:** b2e9b13bf861fbe122632f29ab8337c3fbc7c0f8
**Corpus:** 2ac86c3f693409c364f8630a97198c8dbfa9c6f3
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.dispatch.entity-state-bound | A | | |

## Column diff vs plan stage

(aligned) — Joan graded `astral.dispatch.entity-state-bound` **A** at validate-plan; code review agrees. Diff touches `config.py` only for product logic; no `dispatch_task` `entity_type` / `trigger_state` / claim-path changes; candidate-scoped helper aligns with parent dispatch-validation intent without violating entity-binding law.

## Frame diff

(none)

## Findings

### discuss — Cross-ticket scope (AST-1769 on AST-1779 branch)

- **Severity:** discuss
- **Location:** `tests/component/ui/api/test_api_jobs.py::TestJobsRoutes::test_detail_related_meteorite_source_entity_fallback`, `docs/test-bible/ui/api/api_jobs.md` § AST-1769; commit `f17a5e30`
- **Finding:** Branch carries AST-1769 bug-repro test + bible section merged via `merge-tests`, but no `src/ui/api/api_jobs.py` product change. Plan `## Explicit scope gate` limits product edits to `config.py`. Test asserts `related_meteorite` non-null via `get_meteorite(source_entity_id)` fallback that is not implemented on this tip — would fail if `test_api_jobs.py` suite (or CI breadth) runs it; absent from AST-1779 QA manifest so `test-child` stayed green.
- **Recommendation:** Chuckles/engineer decide before UT rollup: drop `f17a5e30` from this sub tip, or accept as epic worktree spill and ensure AST-1769 make-fix lands before broad test runs. Not a canon violation; scope hygiene for merge-child / prep-uat.

### discuss — Canon Scope gap (do not score; Joan raised at plan)

- **Severity:** discuss
- **Location:** Ticket Citations vs plan footprint
- **Finding:** `astral.standards.in-scope-only` plainly governs single-file helper scope but is absent from the frozen one-id list. Plan gate + actual `config.py`-only product diff are compliant.
- **Recommendation:** Archie may amend Canon Scope at Discussion for Radia comparability; no plan or code change required for AST-1779.

### advisory — Candidate-backed artifact token path untested

- **Severity:** advisory
- **Location:** `tests/component/utils/test_config.py::TestAst1779EmptyRenderForPrompts`
- **Finding:** AC1 / parent wording covers candidate-backed **artifact** tokens; manifest tests use `FIRST_NAME` / `FULL_NAME` (`data_field` paths) only. Implementation scores `source == "candidate"` (includes artifact rows) via `resolve_tokens`, so behavior is likely correct but unproven for e.g. a `serialize: resume_sections_json` blank.
- **Recommendation:** Optional follow-up test in resolve-child or sibling wiring; not blocking helper contract for siblings #2–#4.

## What's solid

- `warn_on_empty` gates every empty/unresolved `_log.warning` path in `resolve_tokens`; default `True` preserves existing call-site behavior.
- `empty_render_for_prompts` matches plan contract: `{"empty_render", "empty_tokens"}`, `_TOKEN_RE` scan, first-seen order, chain never scored, job ignored without `entity_contexts`, job/rubric seams via `entity_contexts`, per-token quiet `resolve_tokens` probe (no second token map).
- Seven manifest tests in `TestAst1779EmptyRenderForPrompts` map 1:1 to plan done-when / AC1–AC3; bible entry added.
- Estimate **3** fits AST-1779 footprint (config helper + component tests + bible).

## Recommended actions (Chuckles downstream — not Radia)

1. Append this verdict to `docs/features/dispatcher/ast-1779-empty-token-predicate-helper.md` and push `docs(AST-1779): Radia review — clean` on `origin/sub/AST-1766/AST-1779-empty-token-predicate-helper`.
2. Post slim upshot via `linear_proxy --as radia save-comment`.
3. Move to **Review Posted**; datt routes PROCEED → User Testing path per §3h.
4. Resolve AST-1769 spill (discuss finding) before broad CI or ftr rollup if full `test_api_jobs.py` is in gate.

```
[code-rubric] PROCEED (Commit: b2e9b13b) empty-render helper clean
```

context_tokens≈28000

## Resolution

**2026-09-23** — `resolve(AST-1779): — clean` after Radia **CLEAN** / `[code-rubric] PROCEED` @ `b2e9b13b` (intake tip `5fd9d792`).

- **Fix-now:** none.
- **Discuss (AST-1769 spill on this sub):** no product change on AST-1779. Left on tip for Chuckles at merge-child / prep-uat — do not rewrite history here; Radia’s recommendation stands (drop spill or land AST-1769 make-fix before broad `test_api_jobs` gates).
- **Discuss (Canon Scope gap):** no change — Joan/Radia both “no plan or code change required.”
- **Advisory (artifact token path untested):** deferred — would be Betty test-tree; product already scores `source == "candidate"` via `resolve_tokens` (includes artifact rows). Not blocking siblings #2–#4.

## Bug: AST-2000 — Runtime empty token is an error: no model call, entity to error_state

- **Linear:** https://linear.app/astralcareermatch/issue/AST-2000 (fix child of orphaned bug [AST-1986](https://linear.app/astralcareermatch/issue/AST-1986), its mini-parent)
- **Publish ref:** `sub/AST-1986/AST-2000-runtime-empty-token-error` · **ftr:** `ftr/AST-1986-runtime-empty-token-error`
- **Canon:** `astral.dispatch.entity-state-bound` (corpus `e1f2699fad44e4083e39a9a066cc87cae494ad51`) — no `dispatch_task` row, `entity_type`, `trigger_state` or claim-helper change; every destination below is an existing registered state. `astral.standards.in-scope-only` — every file below is in AST-2000 `## Scope` (Joan: valid statute; the clerk's `unknown directive id` is an index gap). `patt.task.dispatch-retry` — this plan routes `empty_tokens` failures **around** the `_RETRY` holding by Susan's ruling; the canon carve-out is sibling **[AST-2005](https://linear.app/astralcareermatch/issue/AST-2005)**, not this ticket.
- **Tests / bible:** sibling **[AST-2006](https://linear.app/astralcareermatch/issue/AST-2006)** (Betty) owns every new test and the rewrite of `TestDoTask::test_mid_chain_empty_caller_skips_api`. This ticket touches no `tests/` or bible files.
- **Binding inputs:** AST-1986 As-is / To-be / Proposed steps / `## Decisions (answered by Susan)` and Susan's AST-1986 comment (2026-10-06 05:25): *"Do not retry. Just go straight to error state (even for midhops). … a retry will not resolve the problem. The problem is with our data, not the agent's response."* AST-2000 `## Scope`.

### As-is

1. **Runtime:** inside `do_task`, a token that resolves empty only logs one `WARNING` per token from `resolve_tokens`, and the prompt is **sent to the model anyway** with the blank in place. The only runtime guard is AST-530's `_mid_chain_empty_caller_tokens` (mid-chain `{$CALLER_*}` only; logs `WARNING`, returns `success: False` with no marker).
2. **Routing:** callers treat that `success: False` like any other technical failure — `consult._consult_batch_fail_dest` prefers the entity's retry holding (`*_RETRY`); the dispatch-chain job batch only releases the claim (entity stays at its hop label); roster prefilter batch goes to `HOMEPAGE_READY_RETRY`; select_job_page writes `NO_JOBLIST`; parse_job_list writes `JOBLIST_IDENTIFIED_RETRY` / `COULD_NOT_PARSE_JOBLIST` / `CANNOT_PARSE_JOB_SITE`; candidate requested-artifacts goes to `REQUESTED_ARTIFACTS_RETRY` or holds the hop label counted as `total_failed`; intake writes the ledger with `total_failed=1`.
3. **Probe:** `GET /api/admin/tasks` → `_enrich_tasks` resolves every task's system + cache blocks with a candidate but no job and `warn_on_empty` at its default, so every `source: job` token logs `Token {$…} resolved to empty (job_context, task=…)` on every Manage Tasks load (the five `anticipate_scan` lines in the AST-1986 report).

### To-be

1. **Runtime** (`do_task`): if **any** token the outgoing prompt references resolves empty — candidate, job, rubric, config, output_type, or chain incl. `{$CALLER_*}` on **any** hop, entry included — the prompt is **not sent**. One `ERROR` line names the task, the entity and every empty token; no per-token `WARNING`s on this path. `do_task` returns the existing failure shape plus `empty_tokens` / `empty_token_task`.
2. **Routing:** the entity goes **straight** to a terminal error state — the task's configured `error_state`, mid-chain hops included. **Never** a `_RETRY` holding, **never** left at its input / hop-label state. Where the configured `error_state` is itself a retry holding, or the flow has none, it goes to the terminal error state the existing code for that flow already uses (named per path below). Counted as an **error**, never as `failed`.
3. **Probe** (`_enrich_tasks`): silent. **Admin preview** (`/api/admin/tasks/<task>/preview`): unchanged — still warns, still renders.

### Repro

Fixtures only (no seeded DB). All three run against the current tip and show the defect:

1. **Probe noise** — `_enrich_tasks("somerset")` with a candidate whose token view is populated and `data/admin/agent_task.json`'s `anticipate_scan` row (system prompt references `{$VISIBLE_JD}`, `{$ANALYSIS_JD}`, `{$ANALYSIS_DO}`, `{$ANALYSIS_GET}`, `{$ANALYSIS_LIKE}`). `caplog` at WARNING captures exactly five `resolved to empty (job_context, task=anticipate_scan)` records. **Expected after fix:** zero.
2. **Runtime blank sent** — monkeypatch `_resolve_task_prompts` to return `agent_row = {"content": "", "model_id": <routable>}` and `agent_task_row = {"system_prompt": "Deal breakers: {$DEAL_BREAKERS}", "user_prompt": "Go", ...}`; call `do_task("<any TASK_CONFIG key with response_schema>", index="job-1", ctx={"candidate_data": {...deal_breakers: ""...}, "candidate_api_keys": {<server>: "k"}})` with the provider call stubbed. **Today:** the provider stub is called with `"Deal breakers: "`. **Expected after fix:** stub not called; result `success is False`, `empty_tokens == ["DEAL_BREAKERS"]`, `empty_token_task == <task_key>`; exactly one ERROR record, no `resolved to empty` WARNING.
3. **Retry detour** — `_run_batch_consult` for a `grade_do` job fixture `{"astral_job_id": "j1", "state": "<primary state whose JOB_STATES entry has retry_state>"}` with `do_task` stubbed to return `{"success": False, "error": "x", "empty_tokens": ["VISIBLE_JD"], "empty_token_task": "grade_do"}`. **Today:** `j1` transitions to its `retry_state` and `retried == 1`. **Expected after fix:** `j1` transitions to `FAILED_TECHNICAL_DO` (`grade_do`'s `error_state`), `retried == 0`, so the dispatcher summary counts it under `total_errors`.

### Root cause

`resolve_tokens` has no way to hand empties back to the caller — it can only warn — so `do_task` cannot tell that the text it is about to send is incomplete, and returns no marker that downstream routing could key on. Every dispatcher therefore treats an incomplete prompt as a transient agent failure (retry holding / judgment state / hold / `failed` count), although a retry renders the same blank — the defect is in our data, not the agent's response — and the list probe shares the runtime resolver's warning default.

### Proposed change

Eight edits, in this order. Every file is in AST-2000 `## Scope`; nothing else changes.

**1. `src/utils/config.py` — `resolve_tokens` collector.**

- Add keyword-only `empty_tokens: Optional[list] = None` after `warn_on_empty`. Docstring line: `empty_tokens: when a list, append each recognized token name whose substituted value is blank (str.strip() == ""), ordered-unique, and suppress the per-token WARNINGs (AST-2000 runtime guard).`
- Implementation (no change to `_replace`'s branches or substitution results):
  - First line of the body: `if empty_tokens is not None: warn_on_empty = False`.
  - Wrap the substitution:

    ```python
    def _collect(match: re.Match) -> str:
        out = _replace(match)
        name = match.group(1)
        # Unrecognized names stay literal — not "empty" (forward-compat contract above).
        if name in TOKEN_SOURCES and not out.strip() and name not in empty_tokens:
            empty_tokens.append(name)
        return out
    return _TOKEN_RE.sub(_collect if empty_tokens is not None else _replace, text)
    ```
- Covers every source (`candidate`, `job`, `chain` incl. `CALLER_*` on entry and mid-chain, `rubric`, `config`, `output_type`, `pronoun`). Default call (`empty_tokens=None`) is byte-identical to today, so admin preview, `empty_render_for_prompts` and every other caller are untouched.

**2. `src/core/agent.py` — keyword-only pass-throughs.** Add `warn_on_empty: bool = True` and `empty_tokens: Optional[list] = None` (keyword-only, after `parent_caller_summary`) to `resolved_agent_content`, `_chain_context` and `resolved_task_system`; each forwards both unchanged to the `resolve_tokens` / `resolved_agent_content` call it already makes. No other behavior change.

**3. `src/core/agent.py` — `do_task` runtime guard.**

- Compute once, before `_cc = _chain_context(...)`:
  - `_empties: Dict[str, list] = {seg: [] for seg in ("selected_agent", "system", "user", "cache_a", "cache_b", "cache_c", "cache_d", "nocache")}`
  - `_selects_agent = any("{$SELECTED_AGENT}" in s for s in _task_prompt_texts(agent_task_row, None).values())` (existing helper: raw `system`/`user`/`cache_a`–`cache_d`/`nocache`/`live` texts).
- `_chain_context(..., warn_on_empty=False, empty_tokens=_empties["selected_agent"] if _selects_agent else None)` — agent content is only sent when a prompt injects `{$SELECTED_AGENT}` (or as the system fallback, which `resolved_task_system` collects itself), so its blanks only count then.
- Pass `empty_tokens=_empties[<seg>]` into `resolved_task_system` (`"system"`) and each of the six `resolve_tokens` segment calls (`"user"`, `"cache_a"`…`"cache_d"`, `"nocache"`).
- After the existing `intake_prompt_snapshot` block, drop the collectors of segments the snapshot replaced (they are not sent): `cache_a`–`cache_d` always when `snap` applied; `system` when `"system" in snap`; `nocache` when `"nocache" in snap`.
- Merge the remaining collectors ordered-unique in segment order above into `empty_names: list[str]`.
- **Replace** the whole `if not chain_entry:` AST-530 block (the `segment_texts` dict, the `_mid_chain_empty_caller_tokens` call and its `WARNING` + return) with:

  ```python
  if empty_names:
      # AST-2000: an incomplete prompt is never sent — one ERROR, no per-token WARNINGs.
      logger.error(
          "%s | %s skipped — empty tokens %s\n  This call is not going out",
          index or candidate_id or "-",
          task_key,
          ", ".join(empty_names),
      )
      return _with_harvest({
          "success": False,
          "error": f"Empty tokens: {', '.join(empty_names)} (task={task_key})",
          "empty_tokens": empty_names,
          "empty_token_task": task_key,
          "api_response": None,
          "parsed_response": None,
          "timesheet": {},
      })
  ```
- Delete the now-unreferenced `_mid_chain_empty_caller_tokens` function. Keep `_referenced_caller_tokens` (still used by `_task_references_caller_tokens`) and the `"Required caller token"` entry in `_HOP_FAILURE_RESPONSE_PREFIXES` (old stored rows may still carry it).
- Position is unchanged from the AST-530 guard: after the API-key check, before `_build_context` / `_open_run_next_hop_ledger` — so no provider call, no hop ledger, no agent_data PROMPT row.
- Mid-chain hops: the inner `do_task` returns this dict and `_run_next` returns `inner` unchanged, so `empty_tokens` / `empty_token_task` reach the entry caller with the **failing hop's** task key.

**4. `src/core/consult.py` — one destination helper + four call sites.** Jobs only.

- New helper next to `_consult_batch_fail_dest`:

  ```python
  def _empty_token_fail_dest(*error_states: Optional[str]) -> str:
      """AST-2000: empty-token do_task → first configured non-retry error_state, else FAILED_TECHNICAL.
      Never a _RETRY holding — a retry renders the same blank (data defect, not an agent goof)."""
      for es in error_states:
          es = (es or "").strip()
          if es and not retry_base(es):
              return es
      return "FAILED_TECHNICAL"
  ```

  `FAILED_TECHNICAL` is the terminal `_consult_batch_fail_dest` already returns when a failure has nowhere else to go; it is a registered `JOB_STATES` entry with `prior_states: None` (valid from any state, incl. hop labels).
- **`_run_analysis_upshot_batch`** (`success: False` branch, after the balance-refusal check): `if result.get("empty_tokens"):` → `_transition_job_state_for_task(task_key, [aid], _empty_token_fail_dest(task_cfg.get("error_state")))`; `errors += 1`; `continue`. Destination: **`FAILED_TECHNICAL`** for both `analysis_upshot` and `meteorite_upshot` (their `error_state`s `PASSED_LIKE_RETRY` / `METEORITE_PASSED_LIKE_RETRY` are retry holdings — the same `FAILED_TECHNICAL` `_consult_batch_fail_dest` sends them to out of that holding today).
- **`render_verdict`** (`success: False` branch, after balance refusal): `if result.get("empty_tokens"):` → `dest = _empty_token_fail_dest(error_state)`; `_transition_job_state_for_task(agent_task, [astral_job_id], dest)`; return `{"success": False, "to_state": dest, "error": result.get("error")}`. Destinations: the orchestration cfg's `error_state` (`FAILED_TECHNICAL_DO` / `_GET` / `_LIKE`, `METEORITE_FAILED_TECHNICAL_*`, …). `run_consult_task`'s single-row summary already counts a non-retry `to_state` as `total_errors: 1`.
- **`_run_batch_consult`** (envelope `success: False`, after balance refusal): `if result.get("empty_tokens"):` → `_transition_job_state_for_task(task_key, astral_ids, _empty_token_fail_dest(error_state))` (one call — single destination for the whole batch); return `{"success": False, "error": result.get("error"), "passed": 0, "failed": 0, "total": len(jobs), "retried": 0}`. Covers every Pattern-A batch through this scaffold (qualify → `ERROR_QUALIFY_JOB_LISTINGS` / `METEORITE_ERROR_QUALIFY`, evaluate → `ERROR_EVALUATE_JD` / `METEORITE_ERROR_EVALUATE_JD`, grade_* and encoded alias Do/Get → their `FAILED_TECHNICAL_*`).
- **`_run_dispatch_chain_job_batch`** (`success: False` branch): before the existing `release_job_dispatch_claim` + `errors += 1`, `if result.get("empty_tokens"):` → `dest = _empty_token_fail_dest(TASK_CONFIG.get(result.get("empty_token_task") or "", {}).get("error_state"), TASK_CONFIG.get(dispatch_task_key, {}).get("error_state"))`; `try: tracker.transition_job_state([aid], dest)` `except ValueError: tracker.transition_job_state([aid], "FAILED_TECHNICAL")`. Then the existing release + count run unchanged. Order: **failing hop's** `error_state` (mid-chain included — e.g. `ERROR_BUILD_ARTIFACTS` for any artifact hop), then the entry dispatch task's, then `FAILED_TECHNICAL` (hops with no `error_state`: `draft_cover_letter`, `check_cover_letter`, `finalize_cover_letter`, `propose_application_responses`). The transition is valid from a hop label (`_job_state_matches_prior` accepts `<trigger>:<hop>` when the trigger is in `prior_states`); the `ValueError` fallback is the any-state terminal, so the job never stays at its hop label.
- These `consult` branches log at most `logger.debug("empty_tokens route aid=%s dest=%s", …)` — the single ERROR line is `do_task`'s. Do not call `_warn_job` / `_log_fail_dest` on these branches.

**5. `src/core/roster.py` — audited; three changes.** Companies have no `TASK_CONFIG` `error_state`; the flow's `ROSTER_CONFIG[<flow>]["error_state"]` / terminal is the configured one. Company error states carry no `prior_states`, so every transition below is valid.

- **Prefilter batch** (`_run_batch_company_prefilter`, `do_task` `success: False` branch after balance refusal): `if result.get("empty_tokens"):` → `transition_company_state(sn, cfg["error_state"])` for each company → **`ERROR_PREFILTER`** (`cfg` = `ROSTER_CONFIG["prefilter"]`, already in scope); return `{"passed": 0, "failed": 0, "total": len(companies), "retried": 0}` so the dispatcher counts them as errors.
- **select_job_page** (`_find_job_page_from_assembled`, `if not res.get("success")` branch, before the `NO_JOBLIST` save): `if res.get("empty_tokens"):` → `err_st = ROSTER_CONFIG["locate_job_page"]["error_state"]`; `transition_company_state(short_name, err_st)`; return `{"short_name": short_name, "state": err_st, "job_site": company_website, "response_type": "SELECT_FAILED", "error": res.get("error")}` — **no** `state_held`, **no** `NO_JOBLIST` save. Destination: **`ERROR_LOCATE_JOB_PAGE`** — the locate / select flow's configured `error_state` (`select_job_page`'s `ROSTER_CONFIG` entry has none), already used by `jobs_found_process_job_site` for `SCRAPE_FAIL`. Both callers count it under `total_errors` via their existing `result.get("error")` branch (PJL_READY dispatch; JOBS_FOUND locate re-transitions to the same `ERROR_LOCATE_JOB_PAGE`, idempotent). Also covers a chained `parse_job_list` hop (its failure returns through select's `do_task`).
- **parse_job_list** (`_fetch_parse_job_list`): when `response.get("empty_tokens")`, return `{"empty_tokens": response["empty_tokens"], "error": response.get("error")}` instead of `{}` (skip `save_company_data` notes). Each caller checks first, `if parsed.get("empty_tokens"):`, with no `_save_company`:
  - `run_parse_job_list_dispatch` (JOBLIST_IDENTIFIED / `_RETRY`) → `transition_company_state(short_name, parse_cfg["terminal_fail_state"])` → **`COULD_NOT_PARSE_JOBLIST`** (the terminal `_parse_dispatch_failure_state` already uses out of the retry trigger; `parse_job_list` has no `error_state`); return `{"short_name": short_name, "state": "COULD_NOT_PARSE_JOBLIST", "error": parsed.get("error")}`. The dispatcher checks `result.get("error")` before `ok_states`, so it counts `total_errors`, not passed.
  - `_finalize_joblist_titles_select_only` (inside the locate / select flow) → same as select_job_page above: **`ERROR_LOCATE_JOB_PAGE`**, return with `"error"`.
- **No change (audited):** single prefilter `_prefilter_fail` (an empty-token result has no `api_response` / `raw_response`, so `_prefilter_api_failure_is_retryable` is already False → `ERROR_PREFILTER`); `vet_inflow_discovery_company(_batch)`, `find_company_website`, the prefilter-notes helper, `_fetch_select_job_page` — these return or raise an error with no state write; their callers have no configured error state for these flows and do not route to a retry holding.

**6. `src/core/candidate.py` — `run_requested_artifacts_dispatch`.** Before the existing `raise RuntimeError(...)`: `if response and response.get("empty_tokens"):` → `err = CANDIDATE_STATES[registered_base(CANDIDATE_STATES, bare_trigger) or bare_trigger]["error_state"]`; `transition_candidate_state(candidate_id, err)`; `logger.debug(...)`; return `{**zero, "total_processed": 1, "total_errors": 1}`. Destination: **`REQUESTED_ARTIFACTS_ERROR`** (or **`REQUESTED_RESUME_ERROR`** for that stage) — mid-chain included; the edge is valid from the trigger, its hop label (`_candidate_state_allowed` parses hop labels) and its `_RETRY` (`state_prior_states` derives retry edges). Guard the lookup with the existing `is_registered_state(CANDIDATE_STATES, bare_trigger)` check; an unregistered trigger falls through to today's `raise` path (it has no error state to name). `craft_resume_base` (`parse_candidate_resume`) audited — no state write, no change.

**7. `src/core/intake.py` — ledger counts.** In both `do_task` failure branches (preamble validation and the intake task run), when `result and result.get("empty_tokens")`, write `total_errors=1` instead of `total_failed=1` on the `update_dispatch_ledger` call (status stays `"FAILED"` — the ledger's only failure status; no new vocabulary). Intake has no entity state routing; everything else unchanged.

**8. `src/ui/api/api_admin.py` — `_enrich_tasks` probe silent.** Add `warn_on_empty=False` to its four resolves: `_chain_context(...)`, `resolved_task_system(...)`, the agent-content `resolve_tokens(...)`, and the cache-block `resolve_tokens(...)` loop. Token counts and `task_ready` unchanged. `preview` route untouched.

**Audited, no change:** `src/core/contact.py` (conversational turn, no entity state). `src/core/meteorite.py` — see decision below.

⚠️ **Decision:** "Empty" = substituted value `.strip() == ""` (whitespace-only is as blank in the sent prompt as `""`). Matches AST-530's runtime check this generalizes; the AST-1779 Run/AUTO predicate keeps its exact `== ""` (untouched).

⚠️ **Decision:** Fold AST-530's `_mid_chain_empty_caller_tokens` into the new guard rather than keep both — the collector sees every empty `{$CALLER_*}` the AST-530 check saw, so keeping it would be dead code, and its WARNING / no-marker return contradicts Susan's "error, not retry". Test rewrite → AST-2006.

⚠️ **Decision (Susan, binding):** `empty_tokens` never routes through `_RETRY` and never leaves the entity at its input / hop-label state. Fallback terminals, all existing: jobs → `FAILED_TECHNICAL` (when the configured `error_state` is a retry holding or unset); companies → the flow's `ROSTER_CONFIG` `error_state` / `terminal_fail_state`; candidates → the stage's `CANDIDATE_STATES` `error_state`. Canon carve-out → AST-2005.

⚠️ **Decision:** `src/core/meteorite.py` unchanged. Its `do_task` callers act on `meteorite` staging rows, not dispatch entities in a retry/error registry: land enrich leaves rows at `READY` (only successor `LANDED`), review-duplicate leaves them at `CHECK_UNIQUE` (only successors `READY` / `DUPLICATE`), stage already maps failures through `run_stage_meteorite`'s existing `SCRAPE_ERROR` / `total_errors` arms. `METEORITE_STATES` has no error state reachable from `READY` or `CHECK_UNIQUE`, and Susan's instruction is to not invent states. If she wants those rows terminal too, it needs a new registered state — a separate ticket.

⚠️ **Decision:** `{$SELECTED_AGENT}` content counts only when a prompt segment references `{$SELECTED_AGENT}` — otherwise agent content is never sent and its blanks would fail tasks spuriously.

### Blast radius

- **Every `do_task` call.** Any live prompt with a genuinely blank token now fails instead of sending, and the entity lands in a terminal error state an operator must clear. Most likely trigger: a candidate with an empty content field (Deal Breakers, Ideal Day, …) — Susan: "candidate content fields are NOT OPTIONAL". Also any task whose prompt references a `source: job` token but is called without a job context, or a `config` / `output_type` token whose resolver returns `""`.
- **Mid-chain:** a job partway through an artifact chain moves from its hop label to `ERROR_BUILD_ARTIFACTS` (or the entry's error / `FAILED_TECHNICAL`) instead of holding the label for a later reclaim.
- **Tests that assume current behavior** (AST-2006, Betty): `core/agent` `TestDoTask::test_mid_chain_empty_caller_skips_api` (pins the deleted AST-530 contract); tests asserting per-token `resolved to empty` WARNINGs from `do_task` or `_enrich_tasks`; consult / roster / candidate / intake routing tests only where a stub sets `empty_tokens` (generic `success: False` routing is unchanged). Betty: shared `_agent_rows` fixture carries no tokens and `TestResolveTokens` / `TestAst1779*` use default args — no broad fallout expected.
- **Canon:** `patt.task.dispatch-retry` "always applies" / "failure never stays in state" — carve-out in AST-2005. `stat.logging.error` vs a configured-miss WARNING for the single guard line — Joan rated this secondary and resolved by the same carve-out naming the guard as a pre-provider terminal.
- **Shared modules:** `resolve_tokens` (all callers — default path unchanged), `resolved_task_system` / `_chain_context` / `resolved_agent_content` (signatures gain keyword-only defaults; preview unchanged).
- **Siblings / ancestors:** AST-1780 Run/AUTO gate and AST-1779 `empty_render_for_prompts` unchanged (admin-time predicate; runtime guard is stricter by design). [AST-1987](https://linear.app/astralcareermatch/issue/AST-1987) (Railway log fields) is separate.
- **Known limitation:** `_chain_context` runs without a collector (but quiet) when no segment references `{$SELECTED_AGENT}` — agent content is not sent in that case. Preview helpers (`simulated_chain_context_for_preview`, `preview_prompt`) keep default warnings by design.

### What must still hold

- AST-1779 AC 1–3: `empty_render_for_prompts` contract, field name `empty_render`, candidate-only scoring by default, `entity_contexts` seam, chain never scored — untouched.
- `resolve_tokens` default call (no `empty_tokens`, `warn_on_empty=True`) emits exactly today's WARNINGs and substitutions — admin preview (`/api/admin/tasks/<task>/preview`) still warns and renders.
- `_enrich_tasks` token counts, `task_ready`, RSC count (AST-1978) unchanged — only its logging goes quiet.
- Fully populated prompts: `do_task` behavior byte-identical (provider called, hop ledger, harvest, chain).
- Every **non**-empty-token failure keeps today's routing: `_RETRY` holdings per `patt.task.dispatch-retry`, provider balance refusal / call-budget holds, hop-label success writes, AST-1298 claim release on raise.
- No schema change, no new state; no `dispatch_task` row change (`astral.dispatch.entity-state-bound`).

### Joan fix-board — AST-2000

[board-joan]  CANON: REVISE
What: patt.task.dispatch-retry — record AST-2000 carve-out (empty_tokens: skip _RETRY detour; input-state hold when error_state unset/retry-holding) — plan contradicts “always applies” + “failure never stays in state”

context_tokens≈24000

**`astral.standards.in-scope-only`:** Valid active harvest statute at `canon/statutes/astral/standards/astral.standards.in-scope-only.md`. A canon-clerk `expand: unknown directive id` is a tooling/index gap, not a missing id. For this pass, scope is the AST-2000 plan’s explicit eight-file list; no conflict with “touch only what’s scoped” assuming Linear `## Scope` matches that list.

**Comment body (for Chuckles → `linear_proxy --as joan save-comment`):**

```
[board-joan]  CANON: REVISE
What: patt.task.dispatch-retry — record AST-2000 carve-out (empty_tokens: skip _RETRY detour; input-state hold when error_state unset/retry-holding) — plan contradicts “always applies” + “failure never stays in state”

context_tokens≈24000
```

**Stdout:**

```
AST-2000 board-joan done — CANON: REVISE — dispatch-retry carve-out.
```

---

**Rationale (not for Linear):**

- **`astral.dispatch.entity-state-bound`:** Conforms. No `dispatch_task` / claim-helper / registry-pair edits; transitions use existing configured states only (plan “What must still hold”).
- **`astral.standards.in-scope-only`:** Conforms if ticket scope matches the named files; no silent creep beyond the plan block.
- **`patt.task.dispatch-retry`:** Conflicts. The pattern says it **always** applies and that a failure **must not** remain in the same state, while AST-2000 routes `empty_tokens` **around** retry holdings (`_empty_token_fail_dest` treats retry-base `error_state` as “none”) and explicitly allows **stay at input state** + reclaim (select/parse paths, upshot tasks, no `error_state`). That needs a documented exception (F3 `validate-plan` fix mode), not silent implementation.
- **Logging (`stat.logging.error` / `stat.logging.warning`):** Secondary tension — configured miss without throw is normally WARNING, but `do_task` uses one ERROR for the guard; acceptable if the dispatch-retry carve-out names empty-token as a pre-provider terminal guard. Not ESCALATE: Susan’s decisions are in-plan; this is canon text, not an open architecture fork.

### Joan fix-board round 2 — AST-2000

[board-joan]  CANON: OK

context_tokens≈28000

**Rationale (not for Linear):**

**Round 1 vs revised plan:** Susan’s binding rule is reflected in To-be §2 and `_empty_token_fail_dest` / roster paths: no `_RETRY`, no hop-label or input-state hold for dispatch entities (jobs → configured terminal or `FAILED_TECHNICAL`; companies → `ROSTER_CONFIG` terminals; candidates → stage `error_state`). That removes the round-1 product conflict with `patt.task.dispatch-retry` (“failure never stays in state”) for everything this ticket actually routes.

**`patt.task.dispatch-retry` + AST-2005:** The remaining corpus gap is the **carve-out** (empty_tokens skip the retry companion; pre-provider data defect). The plan no longer implements the old “stay and reclaim” shape Joan flagged; it assigns the statute/pattern edit to sibling **AST-2005**. For fix-board on **AST-2000** only, that split is correct — this child does not need to land canon text, and the proposed product change is not a silent violation once AST-2005 is in the lane (blocked-after-2000 ordering is Chuckles’ graph, not a second REVISE on this plan).

**`astral.dispatch.entity-state-bound` / `astral.standards.in-scope-only`:** Still conform — registered states only, no `dispatch_task` / schema invention, eight-file scope unchanged.

**Meteorite (Ada’s flagged decision):** Leaving `meteorite.py` unchanged means some `do_task` empty-token failures can still leave staging rows at `READY` / `CHECK_UNIQUE` with no registered error transition. That is a **documented product boundary** (no reachable `METEORITE_STATES` error from those labels; follow-up ticket if Susan wants terminals), not a conflict with harvest statutes cited here or with `patt.task.dispatch-retry` as written (dispatch-entity retry machine). It does **not** warrant ESCALATE on AST-2000 unless Susan reopens scope to invent states — the plan states that explicitly.

**Logging:** Single `do_task` ERROR for the guard remains; blast radius already ties secondary `stat.logging.*` wording to AST-2005 — no new canon blocker on this revision.

**AST-2006:** Test/bible work stays out of Joan’s product canon question for this pass.

### Radia review — AST-2000

**Diff base:** `origin/ftr/AST-1986-runtime-empty-token-error...origin/sub/AST-1986/AST-2000-runtime-empty-token-error` (15 files; plan’s eight-file product set **plus** AST-1995 PJL/gazer carry)  
**Corpus:** `e1f2699fad44e4083e39a9a066cc87cae494ad51`  
**Overall:** FIX-NOW  

## Fix-specific checks

- **[bug-repro]** not applicable — qa-fix did not run; clean board opt-out. Sibling **AST-2006** owns tests; absence not scored as a defect per spawn brief.
- **## What must still hold** — **OK** for AST-2000 wiring on the eight-file plan footprint (1779 predicate/default `resolve_tokens`, preview warnings, enrich counts/`task_ready`, non-`empty_tokens` failure routing, no new states/`dispatch_task` rows). **Not OK** for publish-ref hygiene (sibling product/tests on this tip — see findings).

## Canon scores

| # | slug | grade | effort | one-line |
|---|------|-------|--------|----------|
| 1 | astral.dispatch.entity-state-bound | A | | No `dispatch_task` / claim-helper edits; job/company/candidate transitions use existing registry states only (`_empty_token_fail_dest`, roster terminals, stage `error_state`). |
| 2 | astral.standards.in-scope-only | D | 2 | `src/core/gazer.py` + tracker plan/bible/tests for **AST-1995** PJL re-scrape on this sub tip; plan says eight files only and no `tests/**`. |

## Column diff vs plan stage

no plan-stage validate-plan table for AST-2000 (Joan fix-board round 2 on product canon only, in issue doc)

## Frame diff

(none)

## Findings

### fix-now

- **Cross-ticket product on AST-2000 publish ref** — `src/core/gazer.py` (AST-1995: re-scrape all PJL URLs, nav carry-forward, `pjl_nav_links` rebuild). Not in `## Bug: AST-2000` eight-file list (“nothing else changes”). **Default:** drop gazer + AST-1995 doc/test hunks from `sub/AST-1986/AST-2000-runtime-empty-token-error` (or move to AST-1995 sub) before Review Posted / UT; land AST-2000 product slice alone.

- **Tests/bible on wrong ticket** — `tests/component/core/test_gazer.py`, `test_gazer_scrape_failure.py`, `test_roster.py` (AST-1995 PJL upsert), `docs/test-bible/core/gazer.md`, `roster.md`, `docs/features/tracker/ast-1595-…md`. Plan assigns all AST-2000 tests to **AST-2006**; this is scope creep beyond “sibling test carry” (product `gazer.py` is not carry). **Default:** same as above — strip from this tip.

- **Susan binding: empty_tokens → terminal, never `_RETRY`** — `src/core/candidate.py` `run_requested_artifacts_dispatch` (~3674–3708): `empty_tokens` branch calls `transition_candidate_state(candidate_id, err_state)` with **no** `try`/`except ValueError`. A `ValueError` falls into the broad `except Exception` and `_requested_stage_failure_target` / `retry_base(target)` — **can route to a retry holding**, contradicting Susan’s rule (Ada’s edge). Consult’s `_run_dispatch_chain_job_batch` already uses `try`/`except ValueError` → `FAILED_TECHNICAL`. **Default:** wrap the empty-token transition like consult (`try` / `except ValueError`: log + return `total_errors=1` with best-effort terminal, or re-raise only after ensuring no retry path).

### discuss

- **@susan — meteorite staging unchanged (plan decision)** — `do_task` empty-token failures from meteorite land/stage/review can still leave rows at `READY` / `CHECK_UNIQUE` with no registered error transition. Documented in plan; not a violation of the **frozen** two-id list; **AST-2005** owns `patt.task.dispatch-retry` carve-out wording.  
  **Default:** accept plan boundary unless you reopen scope for new `METEORITE_STATES` terminals.

### advisory

- Core AST-2000 implementation on scoped files aligns with plan: `resolve_tokens` collector, `do_task` guard (after API-key check, before provider/ledger), `_empty_token_fail_dest` + consult/roster/intake/`api_admin` `_enrich_tasks` `warn_on_empty=False`, `_locate_empty_token_error` for locate flow.
- `patt.task.dispatch-retry` corpus gap intentionally deferred to **AST-2005**; not on frozen list — not ESCALATE here.

## What’s solid

- Runtime guard: one `logger.error`, `empty_tokens` / `empty_token_task`, no provider call when `empty_names` non-empty.
- Job batch empty-token path: `retried: 0`, `_empty_token_fail_dest` skips retry-base `error_state`s; dispatch chain `ValueError` → `FAILED_TECHNICAL`.
- Intake ledger uses `total_errors` when `empty_tokens` present.

## Notes for Chuckles

- **Gate:** REVIEW (fix-now findings; C7 artifact complete).
- **Parent:** AST-1986 orphaned mini-parent, live `ftr/AST-1986-runtime-empty-token-error`; merge path per fix-intake, not re-derived here.
- **Downstream only:** append verdict to issue doc, push `docs(AST-2000): Radia review — findings`, post slim upshot `--as radia`, **Review Posted** → `resolve-child` (scope strip + candidate transition hardening).

context_tokens≈32000

**Chuckles note:** the AST-1995 gazer/tests "spill" was a stale-ftr artifact. AST-1995 is already on origin/dev, the sub had synced dev, and the ftr was behind. ftr fast-forwarded to origin/dev; ftr...sub is now exactly the 8 planned files. Only the candidate empty-token transition guard remains fix-now.

### Resolution — AST-2000

**2026-10-06** — `resolve(AST-2000): — findings addressed` after Radia **FIX-NOW**.

- **Fix-now (candidate empty-token transition):** `src/core/candidate.py` `run_requested_artifacts_dispatch` — the `empty_tokens` branch now wraps `transition_candidate_state(candidate_id, err_state)` in `try/except ValueError` (covers `IllegalCandidateTransition`, a `ValueError` subclass). On a raise it logs one WARNING (`skipped error_state …`, same shape as `_apply_dispatch_chain_hop_failure`) and returns `total_errors: 1` — it can no longer fall into the broad `except` whose `_requested_stage_failure_target` may pick a `_RETRY` holding. Mirrors consult `_run_dispatch_chain_job_batch`'s guarded transition.
- **Fix-now (AST-1995 gazer / tests / bible "spill") — void:** stale-ftr diff artifact (Chuckles note above). AST-1995 is on `origin/dev`; `ftr/AST-1986-runtime-empty-token-error` was fast-forwarded to `origin/dev`, and `ftr...sub` is now exactly the eight planned product files. No gazer or test-tree change made.
- **Discuss (meteorite staging unchanged):** Default taken — plan boundary stands; no `METEORITE_STATES` terminal invented. Reopen only if Susan wants new meteorite error states (separate ticket).
- **Advisory:** none actionable.
- **Tests:** none on this ticket — sibling [AST-2006](https://linear.app/astralcareermatch/issue/AST-2006) (incl. a case for this guarded candidate branch).
- **Docs-acceptance:** no test-tree delivery on this sub (no `test(AST-2000):` / `merge-tests(AST-2000):`) — Betty board TESTS: OK; all AST-2000 tests land on sibling [AST-2006](https://linear.app/astralcareermatch/issue/AST-2006).

## Bug: AST-2005 — dispatch-retry carve-out for empty-token data failures

- **Linear:** https://linear.app/astralcareermatch/issue/AST-2005 (canon-gap sibling of [AST-2000](https://linear.app/astralcareermatch/issue/AST-2000), mini-parent [AST-1986](https://linear.app/astralcareermatch/issue/AST-1986); filed from Joan's round-1 `[board-joan] CANON: REVISE`)
- **Publish ref:** `sub/AST-1986/AST-2005-dispatch-retry-carve-out` · **ftr:** `ftr/AST-1986-runtime-empty-token-error` (AST-2000 already merged there)
- **Explicit scope (AST-2005 `## Scope`):** `canon/directives/active/patt.task.dispatch-retry.md` only — canon text edit; no product code, tests or schema.
- **Precedent:** AST-1846 landed its `stat.logging.*` carve-out as a single `docs(AST-1846): canon — …` commit (`e1f2699fa`). Same shape here.
- **Binding:** Susan on AST-1986 (2026-10-06 05:25) — *"Do not retry. Just go straight to error state (even for midhops). This is because we retry in the event that an agent goofed up, but in this case specifically a retry will not resolve the problem. The problem is with our data, not the agent's response."*

### As-is

`patt.task.dispatch-retry` § "When this doesn't apply" reads only `THIS PATTERN ALWAYS APPLIES (even with daisy-chain tasks.)`, and Arc 4 requires every first failure to go to the `_RETRY` companion. AST-2000 (merged on the ftr) routes a `do_task` `empty_tokens` failure **straight** to the configured `error_state`, skipping `_RETRY`, mid-chain hops included — so the shipped routing contradicts the pattern as written (Joan round 1: "plan contradicts 'always applies'").

### To-be

The pattern names one exception: a **pre-provider data failure** — `do_task` found a token in the outgoing prompt that resolves empty, so the prompt was never sent (`empty_tokens` on the result). That entity skips the `_RETRY` companion and goes straight to the task's configured `error_state` (or the flow's existing terminal error state when the configured one is a `_RETRY` holding or absent), mid-chain hops included. Arc 5 ("A FAILURE DOES NOT PERSIST IN STATE") still holds, unchanged. Every other failed attempt follows the pattern exactly as today, daisy-chain tasks included.

### Repro

Read-only canon check — no fixture needed:

```bash
python3 canon/canon_clerk.py expand patt.task.dispatch-retry
```

**Today:** body's `# When this doesn't apply` is the single line `- THIS PATTERN ALWAYS APPLIES (even with daisy-chain tasks.)`; nothing licenses AST-2000's `_empty_token_fail_dest` / consult / roster / candidate empty-token branches skipping `_RETRY`. **After:** the same section names the empty-token exception and keeps "always applies" for every other failure.

### Root cause

The pattern's premise (Abstract: *"Sometimes the agents return malformed or invalid responses"*) is that a failure is an agent goof a second attempt can fix. An empty runtime token is a defect in our data, detected before any agent call; a retry renders the identical blank prompt. The pattern had no way to say so, so the only literal reading forced a pointless `_RETRY` hop that Susan has ruled out.

### Proposed change

**One file:** `canon/directives/active/patt.task.dispatch-retry.md`. Frontmatter (`id`, `kind`, `scope`, `point`), Abstract, Arc and Canonical implementation are **unchanged**. Replace the body of `# When this doesn't apply` — currently the single bullet `- THIS PATTERN ALWAYS APPLIES (even with daisy-chain tasks.)` — with exactly:

```markdown
# When this doesn't apply

- **Pre-provider data failure — empty runtime tokens.** When `do_task` finds a
  token in the outgoing prompt that resolves empty, the prompt is never sent and
  the result carries `empty_tokens`. The fault is in our data, not the agent's
  response, so a retry would render the same blank prompt. That entity skips
  the `_RETRY` companion and goes **straight** to the task's configured
  `error_state` — mid-chain hops included. When the configured `error_state` is
  itself a `_RETRY` holding, or the flow configures none, it goes to the
  terminal error state that flow already uses (e.g. `FAILED_TECHNICAL`). Arc 5
  still holds: the entity never stays in its trigger, hop-label or input state.
- Every other failed attempt: THIS PATTERN ALWAYS APPLIES (even with
  daisy-chain tasks.)
```

Publish as one commit on the publish ref, AST-1846 shape: `docs(AST-2005): canon — patt.task.dispatch-retry empty-token data-failure carve-out`. Verify after edit: `python3 canon/canon_clerk.py expand patt.task.dispatch-retry` exits 0 and serves the new section (no frontmatter churn → no clerk index change).

⚠️ **Decision:** Narrow carve-out keyed on the `empty_tokens` marker, not a general "any data failure" clause. Susan's ruling is about this failure; a broader clause would license skipping `_RETRY` for failures nobody has ruled on. Future data-failure classes amend this bullet deliberately.

⚠️ **Decision:** No ticket id in the canon text — the bullet names the observable contract (`do_task` / `empty_tokens`) so it stays true after the ticket archives. Traceability lives here and in the commit subject.

⚠️ **Decision (for the board) — meteorite staging is NOT written into the carve-out.** AST-2000's documented boundary leaves `meteorite` staging rows at `READY` / `CHECK_UNIQUE` after an empty-token failure because `METEORITE_STATES` has no error state reachable from either (`READY` → `LANDED` only; `CHECK_UNIQUE` → `READY` / `DUPLICATE` only). Read against Arc 5 ("A FAILURE DOES NOT PERSIST IN STATE") that is a **non-conformance**, but it is **pre-existing and not empty-token-specific** — those meteorite callers leave rows in place on *every* `do_task` failure today (e.g. review-duplicate "stays CHECK_UNIQUE for retry"). Options considered:
  1. **Silent (chosen):** carve-out keeps Arc 5 absolute; meteorite staging stays a recorded known gap (here + AST-2000 plan), to be closed by a follow-up that registers meteorite error states — Susan to file if she wants it. Canon does not bless the gap.
  2. Name it as a known gap inside canon — puts a transient defect into durable law; rejected.
  3. Add "stays in state when no error state is registered" — directly contradicts Arc 5 and Susan's "never stays"; rejected.
  Board: if Joan rules canon must acknowledge it, option 2's wording would be one extra bullet; no product change either way.

### Blast radius

- **Canon readers:** Joan (`validate-plan` / `fix-board`) and Radia (`review-fix` / `review-child`) score `patt.task.dispatch-retry` from this text. AST-2000's empty-token branches (`consult._empty_token_fail_dest` + call sites, roster `ERROR_PREFILTER` / `_locate_empty_token_error` / parse terminal, candidate stage `error_state`) become conformant; nothing else changes grade.
- **Product / tests:** none on this ticket. AST-2000 product is already on the ftr; tests are sibling [AST-2006](https://linear.app/astralcareermatch/issue/AST-2006).
- **Clerk:** body-only edit; `id` / `kind` / `scope` / `point` unchanged, so `canon_clerk.py index` output is unchanged and `expand` serves the new body. `corpus_sha` moves on merge (expected — reviewers record the new sha).
- **Related canon:** `stat.logging.error` already says ERROR when the entity lands in an error / terminal state — consistent with `do_task`'s single ERROR guard line; no edit (Joan rated the logging tension secondary, resolved by this carve-out naming the guard as pre-provider and terminal).

### What must still hold

- Arc 1–5 text unchanged; **Arc 5 absolute** — no failure persists in state, carve-out included.
- Agent-response failures (malformed / invalid / missing response, decode / validation failures) keep the two-attempt `_RETRY` → `error_state` route, daisy-chain tasks included.
- Frontmatter unchanged; the clerk serves the directive (`expand` exit 0).
- No product, test, bible or schema change on this ticket.
