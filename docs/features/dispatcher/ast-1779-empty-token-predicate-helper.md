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

### Joan fix-board — AST-2005

[board-joan]  CANON: OK

context_tokens≈32000

### Meteorite gap — explicit rule (for the board)

**Canon does not need to mention the meteorite gap** for this ticket. Ada’s “silent” choice is correct.

`patt.task.dispatch-retry` is the dispatch-entity retry pattern (trigger / `_RETRY` / `error_state` on job, company, and candidate registries). The proposed carve-out names the observable product contract AST-2000 already implements for those routers: `do_task` returns `empty_tokens` → skip `_RETRY` → terminal `error_state` (or flow fallback). Meteorite staging (`READY` / `CHECK_UNIQUE`, no reachable error label) is **not** licensed or excused by this bullet; it is also **not** empty-token-specific (those callers already leave rows in place on many failures). Putting that gap in canon (option 2) would bake a transient registry hole into durable law; option 3 would gut Arc 5 and Susan’s ruling. Traceability stays in the feature plan + AST-2000 boundary, not in `patt.task.dispatch-retry.md`.

If Susan later wants meteorite empty-token failures terminal, that is **new registered states + product routing** — a separate ticket, not an amendment to this carve-out.

---

**Rationale (not for Linear):**

- **Self-fit:** Proposed `# When this doesn't apply` text matches Susan’s AST-1986 binding, Joan round-1 gap, and merged AST-2000 behavior (`empty_tokens` only, narrow, no ticket id in canon).
- **Arc 5:** Read with pattern scope: empty-token failures on **dispatch-routed** entities must not persist at trigger / hop / input; the carve-out’s terminal routing satisfies that. Do not read the closing Arc-5 sentence as a guarantee for every `do_task` consumer (meteorite).
- **Other directives:** No conflict requiring edits to `stat.logging.error` / `stat.logging.warning` or `astral.dispatch.entity-state-bound`; body-only clerk path is as described.
- **Scope:** `patt.task.dispatch-retry.md` only — conforms to `astral.standards.in-scope-only` for this child.

**docs-acceptance — AST-2005:** canon-only (Betty TESTS: OK — no test/bible reads `patt.task.dispatch-retry`). Check on publish tip: `canon_clerk.py expand patt.task.dispatch-retry` exit 0 serving the new `# When this doesn't apply` section; `canon_clerk.py index` exit 0, unchanged (body-only edit). No test() delivery owed.

### Radia review — AST-2005

**Diff base:** `origin/ftr/AST-1986-runtime-empty-token-error...origin/sub/AST-1986/AST-2005-dispatch-retry-carve-out` (2 paths: `canon/directives/active/patt.task.dispatch-retry.md` + plan-fix doc append; no `src/**`, no `tests/**`)  
**Corpus:** `2344ae3265b15125a8f4a655946fcfe66b3e1def` (moved from ftr’s `e1f2699fa…`; `corpus_dirty`: false on clerk `expand` at review time)  
**Overall:** CLEAN  

## Fix-specific checks

- **[bug-repro]** not applicable — qa-fix did not run; Betty TESTS: OK; canon-only ticket.
- **## What must still hold** — OK: Abstract, Arc 1–5, Canonical implementation, and frontmatter untouched in the canon diff; `# When this doesn't apply` matches the plan verbatim; no product/test/bible/schema hunks.

## Canon scores

| # | slug | grade | effort | one-line |
|---|------|-------|--------|----------|
| 1 | patt.task.dispatch-retry | A | | Carve-out names `do_task` / `empty_tokens`, skip `_RETRY`, straight to `error_state` / flow terminal, mid-chain; retains “always applies” for all other failures; aligns with Susan’s binding rule and AST-2000 on ftr. |

## Column diff vs plan stage

no plan-stage validate-plan scores for AST-2005 (Joan fix-board **CANON: OK** recorded in issue doc)

## Frame diff

(none)

## Findings

### advisory

- Tip commit subject `test(AST-2005): docs-acceptance…` documents clerk grep/sanity only; diff has no test-tree files — consistent with plan and Betty OK.
- Meteorite staging gap intentionally **not** in canon text per Joan board rule in spawn brief — **not** scored as a defect; traceability stays in AST-2000 / AST-2005 plan blocks.
- After this lands on ftr/dev, re-read `patt.task.dispatch-retry` when scoring AST-2000 product should show conform (carve-out was the round-1 gap).

## What’s solid

- Body-only edit; `python3 canon/canon_clerk.py expand patt.task.dispatch-retry` serves the new section (verified read-only).
- Narrow `empty_tokens` marker (no ticket id, no generic “data failure” license).
- Precedent commit present on branch: `docs(AST-2005): canon — patt.task.dispatch-retry empty-token data-failure carve-out`.

## Notes for Chuckles

- **Gate:** PROCEED — artifact complete → **Review Posted** → fix-lane clean shortcut to **User Testing** (no `resolve-child` unless you hold for process).
- **Parent:** AST-1986 orphaned mini-parent, live `ftr/AST-1986-runtime-empty-token-error`.

context_tokens≈22000

## Bug: AST-2006 — Runtime empty-token guard tests + bible

- **Linear:** https://linear.app/astralcareermatch/issue/AST-2006 (test-gap child of orphaned bug [AST-1986](https://linear.app/astralcareermatch/issue/AST-1986), its mini-parent; sibling of [AST-2000](https://linear.app/astralcareermatch/issue/AST-2000) product and [AST-2005](https://linear.app/astralcareermatch/issue/AST-2005) canon, both merged on the ftr)
- **Publish ref:** `sub/AST-1986/AST-2006-empty-token-guard-tests` · **ftr:** `ftr/AST-1986-runtime-empty-token-error`
- **Canon:** `astral.dispatch.entity-state-bound` (inherited from AST-1779) — tests pin destinations that are existing registered states only; no `dispatch_task` / claim fixture change. `patt.task.dispatch-retry` (carve-out landed by AST-2005) is the rule the routing tests assert: `empty_tokens` → never `_RETRY`, never stays.
- **Explicit scope:** AST-2006 `## Scope` — `tests/component/**` and `docs/test-bible/**` only. **Betty lands every file in qa-fix**; this block plans what must be covered and the `[bug-repro]`. No product source change.
- **Binding inputs:** AST-2000 `### To-be` / `### Proposed change` (above, as shipped), Betty's fix-board round-1 `TESTS: REVISE` and her round-2 note in AST-2006's Description, Susan's AST-1986 ruling ("Do not retry. Just go straight to error state (even for midhops).").

### As-is

1. No test or bible entry covers the AST-2000 runtime guard: nothing asserts that `do_task` withholds a prompt with a blank token, returns `empty_tokens` / `empty_token_task`, or logs one ERROR; nothing exercises `resolve_tokens(empty_tokens=[...])`; no routing test stubs a `do_task` result carrying `empty_tokens`.
2. `TestDoTask::test_mid_chain_empty_caller_skips_api` (`tests/component/core/test_agent.py:1816`) pins the deleted AST-530 contract (`"CALLER_SYSTEM" in error`) **and already fails before AST-2000** on its fixture: `do_task` hydrates caller context first (`_hydrate_caller_chain_context`, `agent.py` ~2028), the test stubs no entity row, so it returns `"job not found: job-1 (hop='evaluate_jd')"` before any guard runs (observed in AST-2000 test-fix on the pre-fix tree `2cfcf9e7` and on the ftr tip).
3. `_enrich_tasks` probe silence (AST-2000 edit 8) has no assertion; the existing `test_api_admin.py` `empty_tokens` cases cover the AST-1779/1819 admin-time predicate field, not logging.

### To-be

Every AST-2000 behavior in `### To-be` 1–3 is pinned by a component test and described in the matching bible page; the AST-530 test asserts the new contract and passes; one `[bug-repro]` is red on `origin/dev` and green on `origin/ftr/AST-1986-runtime-empty-token-error`.

### Repro

Verified on refs (read-only):

- `origin/dev`: `src/core/agent.py` still defines and calls `_mid_chain_empty_caller_tokens` (lines 695 / 2162); `resolve_tokens` has `warn_on_empty` but **no** `empty_tokens` keyword; `consult.py` / `roster.py` / `candidate.py` / `intake.py` have zero `empty_tokens` references. An entry-hop prompt with a blank non-caller token is therefore sent to the provider.
- ftr: `consult._empty_token_fail_dest` (1555), `roster._locate_empty_token_error` (2212), the `do_task` guard and the collector are present.
- `pytest tests/component/core/test_agent.py::TestDoTask::test_mid_chain_empty_caller_skips_api` → fails `job not found: job-1` on both trees.

### Root cause

AST-2000 was planned with tests split to this sibling (fix-board round 1), so the product landed with no coverage, and the one adjacent test was already broken by an earlier hydration change (AST-1264-era caller hydration) that its fixture never stubbed.

### Proposed change

All files are Betty's (qa-fix). Exact class/function names are her call; the assertions below are the bar. Shared conventions: stub the provider (`send_to_anthropic` `AsyncMock`) and assert `not called` for "no model call"; `caplog` for log assertions; stub `do_task` with `{"success": False, "error": "Empty tokens: X (task=T)", "empty_tokens": ["X"], "empty_token_task": "T"}` for routing tests.

**1. `[bug-repro]` — `tests/component/core/test_agent.py`, new `do_task` entry-hop guard test (AST-2000 Repro 2).**
`_resolve_task_prompts` → `_agent_rows()` with `system_prompt = "Deal breakers: {$DEAL_BREAKERS}"`; `ctx` candidate data with `deal_breakers: ""`; provider stubbed. Assert: provider **not called**; `success is False`; `empty_tokens == ["DEAL_BREAKERS"]`; `empty_token_task == <task_key>`; exactly **one** ERROR record containing the task key and `DEAL_BREAKERS`; **zero** `resolved to empty` WARNINGs. **Red on `origin/dev`** (provider called, no `empty_tokens` key — dev has no general guard), **green on the ftr**. Tag the qa-fix handoff `[bug-repro]` with this node id.

**2. `tests/component/core/test_agent.py` — rewrite `TestDoTask::test_mid_chain_empty_caller_skips_api`.**
Fix the fixture path: `monkeypatch.setattr(agent_mod, "_hydrate_caller_chain_context", lambda *a, **k: ({"CALLER_SYSTEM": "", "CALLER_RESPONSE": "x"}, None))` (same seam the AST-1264 tests at ~8378 patch; `_merge_hydrated_caller_context` keeps the hydrated blank). Assert: provider not called; `success is False`; `empty_tokens == ["CALLER_SYSTEM"]`; `empty_token_task == "evaluate_jd"` (the **hop's** key); one ERROR; no `"Required caller token"` text. Drop the `"CALLER_SYSTEM" in error` substring as the primary assertion.

**3. `tests/component/core/test_agent.py` — guard edges.**
- Fully populated prompt → provider called once, no `empty_tokens` key (byte-identical path).
- Whitespace-only value (`"  "`) counts as empty.
- `{$SELECTED_AGENT}` rule: blank agent content with **no** segment referencing `{$SELECTED_AGENT}` → provider called; with a reference → guarded.
- Intake snapshot: a blank in a segment the `intake_prompt_snapshot` replaces does not trigger the guard.

**4. `tests/component/utils/test_config.py` — `resolve_tokens` collector.**
- `empty_tokens=[]` collects blank recognized names, ordered-unique across repeats, for at least candidate + job + chain (`CALLER_*`) sources.
- Collector path emits **no** per-token WARNING (implies `warn_on_empty=False`).
- Unrecognized `{$NOT_A_TOKEN}` stays literal and is **not** collected.
- Default call (no `empty_tokens`) output and WARNINGs unchanged — existing `TestAst1779*` / `TestResolveTokens` keep passing.

**5. `tests/component/core/test_consult.py` — straight to terminal, never `_RETRY`.**
- `_empty_token_fail_dest`: first non-retry wins; retry-only / `None` → `"FAILED_TECHNICAL"`; order respected (hop before entry).
- `_run_batch_consult` (AST-2000 Repro 3): job at a primary state with a `retry_state` → transitions to the task `error_state` (e.g. `grade_do` → `FAILED_TECHNICAL_DO`), `retried == 0`, never the retry state.
- `_run_analysis_upshot_batch`: `error_state` is a retry holding → `FAILED_TECHNICAL`; `errors` incremented.
- `render_verdict`: returns `to_state == error_state`, transitions there.
- `_run_dispatch_chain_job_batch` mid-chain: `empty_token_task` = a hop with an `error_state` → that state (e.g. `ERROR_BUILD_ARTIFACTS`); hop with none → entry's `error_state`; transition raising `ValueError` → `FAILED_TECHNICAL`; claim released; `errors += 1`; job never left at the hop label.
- Control: a generic `success: False` (no `empty_tokens`) still routes via `_consult_batch_fail_dest` to the retry holding.

**6. `tests/component/core/test_roster.py` — company terminals.**
- Prefilter batch → every company `ERROR_PREFILTER`; summary `retried == 0`.
- `_find_job_page_from_assembled` select failure with `empty_tokens` → `ERROR_LOCATE_JOB_PAGE`, `"error"` key present, **no** `NO_JOBLIST` save, no `state_held`.
- `_finalize_joblist_titles_select_only` → `ERROR_LOCATE_JOB_PAGE`.
- `_fetch_parse_job_list` returns `{"empty_tokens", "error"}` (no notes save); `run_parse_job_list_dispatch` from `JOBLIST_IDENTIFIED` **and** `JOBLIST_IDENTIFIED_RETRY` → `COULD_NOT_PARSE_JOBLIST`, `"error"` in result.

**7. `tests/component/core/test_candidate.py` — requested-artifacts.**
- `run_requested_artifacts_dispatch`, `empty_tokens` response → `REQUESTED_ARTIFACTS_ERROR` (and `REQUESTED_RESUME_ERROR` for the resume stage); `total_errors == 1`; no `_RETRY` transition; no `RuntimeError`.
- Hardening (resolve-child): `transition_candidate_state` raises `ValueError` → one WARNING (`skipped error_state …`), result still `total_errors == 1`, no retry transition, no raise.

**8. `tests/component/core/test_intake.py` — ledger counts.** Both `do_task` failure branches with `empty_tokens` → `update_dispatch_ledger(..., total_errors=1)`, **no** `total_failed=1`; status `"FAILED"`. Control: non-empty-token failure still writes `total_failed=1`.

**9. `tests/component/ui/api/test_api_admin.py` — probe silent.** `_enrich_tasks` for a task whose prompt references `source: job` tokens with a candidate and no job → **zero** `resolved to empty` WARNINGs; token counts / `task_ready` unchanged. Control: `/api/admin/tasks/<task>/preview` path still warns (default `warn_on_empty`).

**10. Bible (`docs/test-bible/**`)** — one `### AST-2006 · AST-2000 (bug)` section per page, manifest lines naming the nodes above: `utils/config.md` (4), `core/agent.md` (1–3, `[bug-repro]` called out), `core/consult.md` (5), `core/roster.md` (6), `core/candidate.md` (7), `core/intake.md` (8), `ui/api/api_admin.md` (9). Meteorite: no entry (AST-2000 boundary, Betty round 2).

⚠️ **Decision:** One `[bug-repro]` (item 1), not one per call site. The defect is "a blank prompt goes out"; the routing items are coverage that is red on dev by construction (helpers don't exist there) and would make a noisy repro set.

⚠️ **Decision:** Item 2 rewrites the AST-530 test in place rather than deleting it — mid-chain `CALLER_*` on a hop is the one case item 1 doesn't reach, and it pins `empty_token_task` = the hop's key, which `_run_dispatch_chain_job_batch` routing depends on.

⚠️ **Decision:** The 157 pre-existing component failures (identical set on pre-fix `2cfcf9e7` and the ftr, AST-2000 test-fix) are **out of scope**; only `test_mid_chain_empty_caller_skips_api` from that set is fixed here, because the ticket names it.

### Blast radius

- Test tree and bible only, seven test files + seven bible pages above. No `src/**`, schema, canon.
- Shared fixtures: `_agent_rows` / `_batch_entities` reused, not changed; if Betty adds a token-bearing helper, scope it to the new tests so other `TestDoTask` cases stay token-free.
- Pre-existing failing set must not grow (compare against the 157-node baseline).

### What must still hold

- `[bug-repro]` red on `origin/dev`, green on the ftr; all new/rewritten nodes green on the ftr.
- Existing `TestAst1779*`, `TestResolveTokens`, `test_api_admin.py` `empty_tokens` predicate cases unchanged and green (default `resolve_tokens` path untouched).
- Generic (non-`empty_tokens`) failure routing assertions keep expecting `_RETRY` holdings — the carve-out is narrow.
- No product source edits on this sub.

### Joan fix-board — AST-2006

[board-joan]  CANON: OK

context_tokens≈35000

**Rationale (not for Linear):**

AST-2006 is **tests + `docs/test-bible/**` only**; no `canon/**` or product edits. The plan asserts behavior already shipped on the ftr and licensed by **AST-2005** (`empty_tokens` → skip `_RETRY`, straight to terminal / flow fallback). Routing tests pin **existing** registered states only — consistent with **`astral.dispatch.entity-state-bound`**. No statute or pattern text needs amending, carving out, or restating in the bible.

Omitting meteorite coverage matches the **AST-2005 / AST-2000** boundary (gap documented in product plan, not canon). **`[bug-repro]`** and bible sections **describe** the contract for Betty’s manifest; they are not directive authoring. Control cases that keep generic `success: False` on `_RETRY` holdings preserve the narrow carve-out vs normal agent failures.

### Radia review — AST-2006

**Corpus:** `2344ae3265b15125a8f4a655946fcfe66b3e1def` (unchanged on this sub; AST-2005 canon already on ftr)  
**Overall:** CLEAN  

## Fix-specific checks

- **[bug-repro]** **OK** — `TestAst2006DoTaskEmptyTokenGuard::test_bug_repro_entry_hop_blank_token_is_not_sent` exercises **real** `do_task` (not a stubbed `empty_tokens` dict): blank `{$DEAL_BREAKERS}` via `_resolve_task_prompts` + ctx, provider `send_to_anthropic` **not called**, `success is False`, `empty_tokens == ["DEAL_BREAKERS"]`, `empty_token_task == "evaluate_jd"`, exactly one ERROR containing task + token, zero `resolved to empty` WARNINGs. Pins AST-2000 To-be §1 / Repro 2; would fail on dev (provider sends `"Deal breakers: "`). Not tautological.
- **## What must still hold** — **OK**: no product edits; `[bug-repro]` + routing nodes documented red-on-dev / green-on-ftr in bible; `TestAst1779*` / default `resolve_tokens` control in collector test; generic-failure controls keep `_RETRY` (`test_run_batch_consult_generic_failure_still_retries`, intake `generic_control` → `total_failed`).

## Canon scores

| # | slug | grade | effort | one-line |
|---|------|-------|--------|----------|
| 1 | astral.dispatch.entity-state-bound | A | | Routing tests assert existing registry destinations only (`FAILED_TECHNICAL_DO`, `ERROR_BUILD_ARTIFACTS`, `ERROR_PREFILTER`, `REQUESTED_ARTIFACTS_ERROR`, etc.); no `dispatch_task` / claim-helper fixture churn. |

## Column diff vs plan stage

no plan-stage validate-plan table for AST-2006 (Joan fix-board **CANON: OK** in issue doc)

## Frame diff

(none)

## Findings

### advisory

- **Process (spawn brief):** `merge-tests(AST-2006)` is a single-commit test-tree delivery; three-dot diff shows no AST-2001/AST-2004 spill — only AST-2006 tests/bible/plan.
- **Coverage map:** Plan items 1–10 reflected in `TestAst2006*` classes + rewritten `test_mid_chain_empty_caller_skips_api` (hydration stub, `empty_token_task` = hop key); candidate `test_invalid_edge_warns_and_still_counts_error` matches ftr product `ValueError` guard (no retry via broad `except`).
- **Repro flip:** Engineer attestation on tip commit (`bug-repro` red on `origin/dev`, green on ftr); Radia did not re-run pytest in this pass.

## What’s solid

- Routing suite encodes Susan’s rule: `retried == 0`, terminal `error_state` / flow fallback, never hop-label hold (`dispatch_chain_mid_hop`, `select` / parse terminals, `REQUESTED_ARTIFACTS_RETRY` → `REQUESTED_ARTIFACTS_ERROR`).
- `_enrich_tasks` silent vs `preview_prompt` still warns (control).
- Bible `### AST-2006 · AST-2000` sections + manifest item 1 list all new nodes; `[bug-repro]` called out on `core/agent.md`.

## Notes for Chuckles

- **Gate:** PROCEED — artifact complete → **Review Posted** → clean-review shortcut to **User Testing**.
- **Parent:** AST-1986 orphaned mini-parent, `ftr/AST-1986-runtime-empty-token-error` (AST-2000 + AST-2005 already there).

context_tokens≈28000

## Bug: AST-2092 — score rubric tokens in the Scheduled Actions empty-render gate

- **Linear:** https://linear.app/astralcareermatch/issue/AST-2092 (fix child of orphaned bug [AST-2019](https://linear.app/astralcareermatch/issue/AST-2019), its mini-parent)
- **Publish ref:** `sub/AST-2019/AST-2092-rubric-empty-render-gate` · **ftr:** `ftr/AST-2019-rubric-empty-render-gate`
- **Canon:** `astral.dispatch.entity-state-bound` (inherited from AST-1779; no `dispatch_task` row, `entity_type`, `trigger_state` or claim-helper change), `astral.standards.in-scope-only` (one product file, below). AST-2019 cites no canon of its own.
- **Explicit scope (AST-2092 `## Scope`):** `src/utils/config.py` `empty_render_for_prompts` (product, whole fix); `tests/component/utils/test_config.py` (Betty-owned; planned below, landed by Betty). No `api_admin.py` change.
- **Reverses one AST-1779 rule:** Stage 1 step 3's "**Do not score** `pronoun`, `rubric`, `config` …" — for `rubric` only. Every other AST-1779 rule stands.

### As-is

`empty_render_for_prompts` scores `source: candidate` by default and any other source only when it is a key in `entity_contexts`. All six `source: rubric` tokens (`RUBRIC_VECTORS`, `GET_RUBRIC`, `DO_RUBRIC`, `LIKE_RUBRIC`, `JD_RUBRIC`, `PREFILTER_RUBRIC`) are therefore skipped. `api_admin._evaluate_dispatch_empty_render` always passes `entity_contexts=None`, so a candidate with no current `rubric_vector` rows for a task's owner shows that dispatch row **valid**. AUTO/Run then claims entities, and `do_task`'s AST-2000 runtime guard refuses the prompt (`Empty tokens: RUBRIC_VECTORS`). That's Abrams' `qualify_job_listings` batch: 10 jobs claimed, all routed to `ERROR_QUALIFY_JOB_LISTINGS`.

### To-be

Rubric tokens are scored by default, like candidate tokens: rubric rows are keyed per candidate (`candidate_id` + owner task), so they are candidate-scoped data. A candidate whose rubric for a task's owner is empty gets `empty_render: True` with the rubric token in `empty_tokens`. Scheduled Actions shows the row Invalid (tooltip names the token), forces AUTO off, and refuses AUTO-on / Run with 400. Nothing gets claimed. `chain` is still never scored; `job` (and every other non-candidate, non-rubric source) is still scored only via `entity_contexts`.

### Repro

Fixture only (rubric rows come from `database.list_rubric_vectors`; stub the resolver entry). Run against tip `823d37605`:

```python
import src.core.candidate as c
from src.utils import config as cfg
view = {"first": "Abrams", "last": "", "full": "Abrams", "pronouns": "", "contact": {},
        "context": {}, "artifacts": {}, "_astral_candidate_id": "cand-abrams"}  # build_candidate_token_view shape
c.rubric_criteria_for_token = lambda cid, owner: []          # no current rubric_vector rows
cfg.resolve_tokens("{$RUBRIC_VECTORS}", view, "qualify_job_listings", warn_on_empty=False)  # → ""
cfg.empty_render_for_prompts(["Rubric:\n{$RUBRIC_VECTORS}"], view, "qualify_job_listings")
```

**Today:** `{"empty_render": False, "empty_tokens": []}`, although the token renders `""`. **Expected after fix:** `{"empty_render": True, "empty_tokens": ["RUBRIC_VECTORS"]}`. With the stub returning one criterion, the result is `{"empty_render": False, "empty_tokens": []}`, both before and after the fix.

### Root cause

The default scoring filter in `empty_render_for_prompts` (`if source != "candidate" and source not in contexts: continue`) treats `rubric` as a non-candidate entity source. AST-1779 excluded it deliberately, but `resolve_tokens`' rubric branch resolves solely from the candidate view (`_astral_candidate_id`) and the task's rubric owner (`rubric_owner_task_key(task_key)`, or the token's pinned `owner_task_key`). It needs no entity context, so the admin-time predicate already has everything it needs to score it.

### Proposed change

**One file, one function:** `src/utils/config.py` → `empty_render_for_prompts`.

1. Replace the default-scoring filter:

   ```python
               # Score candidate + rubric always (rubric_vector rows are keyed per candidate +
               # owner task; resolve_tokens reads them off the candidate view's
               # _astral_candidate_id — AST-2092); other sources only via entity_contexts seam.
               if source not in ("candidate", "rubric") and source not in contexts:
                   continue
   ```

   Everything else in the function stays as it is: the `chain` early `continue` (before this filter), the `seen` dedupe, `job_context` only for `source == "job"`, the single-token `resolve_tokens(..., chain_context=None, warn_on_empty=False)` probe, the exact `resolved == ""` test, and the return shape. Rubric tokens go through that same probe; no new resolver and no rubric-specific code.

2. Update the docstring's scoring sentence to: ``Scores ``source: candidate`` and ``source: rubric`` always (rubric rows are candidate-keyed — AST-2092); scores other ``TOKEN_SOURCES`` ``source`` values only when that key is present in ``entity_contexts`` (extension seam). Never scores ``source: chain``.`` Leave the rest of the docstring alone.

No change to `resolve_tokens`, `TOKEN_SOURCES`, `api_admin.py`, `do_task` or schema. List enrich (`GET /api/admin/dispatch_tasks`), the PUT AUTO-on gate and the POST run gate all call `_evaluate_dispatch_empty_render` → `empty_render_for_prompts`, so they pick up the change unchanged.

**Test delta, Betty-owned** (`tests/component/utils/test_config.py`, `TestAst1779EmptyRenderForPrompts`). Engineer test-tree ban applies; Betty lands these:

- **Flip** `test_rubric_scored_only_via_entity_contexts`: its first assertion (default call → `empty_render: False` for `{$GET_RUBRIC}` with no `_astral_candidate_id`) becomes `{"empty_render": True, "empty_tokens": ["GET_RUBRIC"]}`. The `entity_contexts={"rubric": {}}` assertion stays `True`. Rename is Betty's call.
- **`[bug-repro]`** (AC 1): the Repro above. Monkeypatch `src.core.candidate.rubric_criteria_for_token` → `[]`, use a token view with `_astral_candidate_id`, task `qualify_job_listings`, `{$RUBRIC_VECTORS}`, and assert `{"empty_render": True, "empty_tokens": ["RUBRIC_VECTORS"]}`. Red on the pre-fix tip, green after.
- **AC 3:** same fixture with the stub returning one criterion → `{"empty_render": False, "empty_tokens": []}`.
- **AC 4 controls:** the existing `test_chain_only_never_scores`, `test_filled_candidate_ignores_blank_job_without_entity_contexts` and `test_job_seam_via_entity_contexts` must still pass unchanged.

⚠️ **Decision: an unresolvable rubric owner counts as empty.** A task whose prompt carries `{$RUBRIC_VECTORS}` while `rubric_owner_task_key(task_key)` is `None` resolves `""` today and is flagged. That matches the AST-2000 runtime guard, which would refuse the same prompt (`"".strip() == ""`), so the Invalid flag tells the truth about what Run would do. Today no row hits this: all eight seeded consumers that reference `{$RUBRIC_VECTORS}` (`qualify_job_listings`, `grade_get` / `_do` / `_like`, `evaluate_jd`, `evaluate_meteorite`, `meteorite_like`, `prefilter_company`) resolve an owner. A missing `_astral_candidate_id` is the same case (`""` → flagged); in the admin path it can't happen, because `_evaluate_dispatch_empty_render` returns early with no candidate.

⚠️ **Decision: no new exception handling.** Rubric scoring adds the predicate's first DB read (`database.list_rubric_vectors(..., current_only=True)`, one per distinct rubric token per row evaluation). `_evaluate_dispatch_empty_render` calls the helper outside its `try`, so a DB error now surfaces on list enrich / gates instead of being swallowed. That's the same unguarded read `do_task` already makes at runtime, and the DB serving the dispatch list is the same one. Adding a `try` here (or a cache / limit) would be a pattern nobody approved, and `api_admin.py` is out of scope. If Susan wants a soft-miss there, that's a separate ticket.

⚠️ **Decision: `PREFILTER_RUBRIC` is in, though the ticket doesn't name it.** It is `source: rubric` in `TOKEN_SOURCES`, and the change is keyed on the source, not on token names. Per the To-be, *every* rubric-sourced token gets scored.

### Blast radius

- **Who can newly flip to Invalid:** dispatch rows whose prompts reference a rubric token and whose candidate has no current rows for that owner. In practice that means owners `qualify_job_listings` and `grade_get` / `grade_do` / `grade_like` (incl. `meteorite_like` → `grade_like`). Owners `prefilter_company`, `evaluate_jd` and `evaluate_meteorite` never resolve empty, because `rubric_criteria_for_task` merges the embedded RC / QC / GC criteria. No `craft_*_rubric` prompt references a rubric token (checked `data/admin/agent_task.json`), so crafting a missing rubric is never blocked by this gate.
- **Operator-visible:** rows that currently run, but whose rubric is empty, will show Invalid and lose AUTO on the next list load (AST-1780 force-off). That's the intended outcome. They were already failing at runtime into `ERROR_*`.
- **Cost:** one `list_rubric_vectors` query per distinct rubric token per dispatch row each time Scheduled Actions enriches or gates. No limit or cache is added (not approved).
- **Shared code:** `empty_render_for_prompts` has one product caller (`api_admin._evaluate_dispatch_empty_render`), and AST-1780 / AST-1819 consume its output shape, which is unchanged. `resolve_tokens` is untouched, so the AST-2000 runtime guard and admin preview are unaffected.
- **Tests that assume the old rule:** `TestAst1779EmptyRenderForPrompts::test_rubric_scored_only_via_entity_contexts` (flip above). `test_api_admin.py` empty-render cases only matter if a fixture prompt carries a rubric token. Betty should confirm in qa-fix; they're outside AST-2092 scope.
- **Operator step (not code, from the ticket):** craft/approve Abrams' joblist rubric (`craft_joblist_rubric`), then reset the 10 `ERROR_QUALIFY_JOB_LISTINGS` jobs to `NEW`.

### What must still hold

- AST-1779 contract: return shape `{"empty_render": bool, "empty_tokens": list[str]}`, field name `empty_render`, first-seen order, exact `== ""` (no strip), `warn_on_empty=False` probes (no WARNING spam on list polls).
- `source: chain` is never scored, even when it's under `entity_contexts`. `source: job` is scored only via `entity_contexts`. `pronoun`, `config` and `output_type` are still unscored by default.
- Candidate tokens are scored exactly as today (AST-1779 AC 1, 3).
- AST-1780 / AST-1819 gate behavior is unchanged apart from rubric tokens now appearing in `empty_tokens`; no `api_admin.py` edit.
- `do_task` runtime refusal and `ERROR_*` routing (AST-2000) are untouched. No new resolver, `TOKEN_SOURCES` entry, schema, or dispatch-row change.

## Bug: AST-2094 — rubric empty-render gate tests + bible (test gap for AST-2092)

- **Linear:** https://linear.app/astralcareermatch/issue/AST-2094 (test-gap child of mini-parent [AST-2019](https://linear.app/astralcareermatch/issue/AST-2019); sibling of [AST-2092](https://linear.app/astralcareermatch/issue/AST-2092), merged on `origin/ftr/AST-2019-rubric-empty-render-gate` @ `4bf928114`)
- **Publish ref:** `sub/AST-2019/AST-2094-rubric-empty-render-gate-tests` · **ftr:** `ftr/AST-2019-rubric-empty-render-gate`
- **Canon:** none cited (AST-2094 `## Citations`: test tree + bible only). Tests pin the AST-2092 contract; no directive text involved.
- **Explicit scope (AST-2094 `## Scope`):** `tests/component/utils/test_config.py` (`TestAst1779EmptyRenderForPrompts` only) and `docs/test-bible/utils/config.md` (AST-1779 entry). **Betty lands both files in qa-fix**; this block plans the bar. No `src/**` change.
- **Binding input:** Betty's `[board-betty] TESTS: REVISE` on AST-2092 (verbatim in AST-2094's Description), plus the AST-2092 block above (`### Proposed change` → *Test delta*).

### As-is

On the ftr tip `4bf928114` (AST-2092 merged), `TestAst1779EmptyRenderForPrompts::test_rubric_scored_only_via_entity_contexts` **fails**. Its first assertion pins the AST-1779 rule (`{$GET_RUBRIC}` default call → `{"empty_render": False, "empty_tokens": []}`), but the product now returns `{"empty_render": True, "empty_tokens": ["GET_RUBRIC"]}`. No test covers the AST-2092 bug itself: an empty rubric for a candidate that *has* an `_astral_candidate_id`. The bible's AST-1779 table row "Rubric scored only via `entity_contexts`" and manifest line 7 both describe the old rule.

### To-be

`TestAst1779EmptyRenderForPrompts` pins rubric-by-default scoring:
- the flipped seam test is green;
- a `[bug-repro]` for empty `{$RUBRIC_VECTORS}` on `qualify_job_listings` is red before AST-2092 and green on the ftr;
- a one-criterion control (AC 3) is green on both.

The bible's AST-1779 entry and manifest name all three nodes. Class result on the ftr: 9 passed, 0 failed (6 untouched + 1 flipped + 2 new).

### Repro

Verified on the ftr tip `4bf928114` (AST-2092 test-fix run):

```bash
/home/susan/astral/.venv/bin/python -m pytest "tests/component/utils/test_config.py::TestAst1779EmptyRenderForPrompts" -q
# → 1 failed, 6 passed — test_rubric_scored_only_via_entity_contexts:
#   {'empty_render': True, 'empty_tokens': ['GET_RUBRIC']} != {'empty_render': False, 'empty_tokens': []}
```

The missing-repro half is the AST-2092 `### Repro` above. Pre-fix `823d37605` returns `{"empty_render": False, "empty_tokens": []}` for an empty `RUBRIC_VECTORS`; the ftr returns `{"empty_render": True, "empty_tokens": ["RUBRIC_VECTORS"]}`.

### Root cause

AST-2092 reversed one AST-1779 rule (rubric now scored by default). Fix-board routed the test/bible delta here, so the product landed with the pinned test still asserting the old contract and with no repro.

### Proposed change

All of it is Betty's (qa-fix). Exact names are her call; the assertions below are the bar. Conventions: `cfg` = `src.utils.config` (existing module alias in `test_config.py`). Stub the rubric read with `monkeypatch.setattr("src.core.candidate.rubric_criteria_for_token", lambda cid, owner: <list>)`. That attribute works because `resolve_tokens`' rubric branch imports it from `src.core.candidate` at call time. No DB, no `database.list_rubric_vectors` stub needed.

**1. Flip `test_rubric_scored_only_via_entity_contexts`** (`tests/component/utils/test_config.py`, `TestAst1779EmptyRenderForPrompts`).
- The default-call assertion becomes `== {"empty_render": True, "empty_tokens": ["GET_RUBRIC"]}`. The fixture is unchanged (`{"first": "Ada"}`, no `_astral_candidate_id` → resolves `""`; `self._TASK` = `grade_get`).
- The `entity_contexts={"rubric": {}}` assertion stays `{"empty_render": True, "empty_tokens": ["GET_RUBRIC"]}` (seam still accepted, same result).
- Update the inline comment: rubric is scored by default (AST-2092); the seam still scores it.
- **Rename** to `test_rubric_scored_by_default_and_via_entity_contexts`, since the old name now states the reverse of the contract.

**2. `[bug-repro]` — new `test_empty_rubric_vectors_sets_empty_render`** (same class, AC 1).
- Fixture: a `build_candidate_token_view`-shaped dict with `_astral_candidate_id: "cand-abrams"`, e.g. `{"first": "Abrams", "last": "", "full": "Abrams", "pronouns": "", "contact": {}, "context": {}, "artifacts": {}, "_astral_candidate_id": "cand-abrams"}`.
- Task: `"qualify_job_listings"` (own rubric owner, no embedded-criteria merge, so `[]` really renders `""`). Do not use `self._TASK`.
- Stub `rubric_criteria_for_token` → `[]`.
- Call: `cfg.empty_render_for_prompts(["Rubric:\n{$RUBRIC_VECTORS}"], view, "qualify_job_listings")`.
- Assert `== {"empty_render": True, "empty_tokens": ["RUBRIC_VECTORS"]}`.
- **Red on pre-fix `823d37605`** (`False`, `[]`), **green on the ftr**. Tag the qa-fix handoff `[bug-repro]` with this node id.

**3. AC 3 control — new `test_filled_rubric_vectors_validates`** (same class).
- Same fixture and task as item 2, with the stub returning one criterion, e.g. `[{"code": "T1", "label": "Title fit", "importance": 5}]`.
- Assert `== {"empty_render": False, "empty_tokens": []}`. Green on both trees: it guards against over-flagging, so it isn't a repro.

**4. Bible — `docs/test-bible/utils/config.md`, `### AST-1779 · AST-1766` section.**
- **Prose (summary paragraph):** change "candidate-scoped empty-render predicate" so it reads that the predicate scores `source: candidate` **and `source: rubric`** by default (rubric rows are candidate-keyed — AST-2092), and that other sources are scored only via `entity_contexts`. The chain and job wording is unchanged.
- **Table:** replace the row `Rubric scored only via entity_contexts` → `Rubric scored by default (and via entity_contexts)` → `…::test_rubric_scored_by_default_and_via_entity_contexts`. Add two rows: `Empty RUBRIC_VECTORS → empty_render [bug-repro] (AST-2092)` → `…::test_empty_rubric_vectors_sets_empty_render`, and `Filled RUBRIC_VECTORS → valid (AST-2092 AC 3)` → `…::test_filled_rubric_vectors_validates`.
- **Manifest:** line 7 points at the renamed node. Add lines 8 (`[bug-repro]`) and 9 (control). The run command stays the whole class.
- **Broken / obsolete:** one line noting the AST-2092 flip of the old line-7 node (renamed, assertion inverted).

⚠️ **Decision: rename the flipped test** rather than keep the old name. `…_scored_only_via_entity_contexts` would pin a reversed contract under a false name, and the bible row has to change anyway. If Betty prefers a stable node id, keeping the name is acceptable *only* if its docstring/comment states the new contract. Bible and manifest must match whichever she picks.

⚠️ **Decision: stub `rubric_criteria_for_token`, not `database.list_rubric_vectors`.** It's the resolver entry `resolve_tokens` calls, it matches Betty's verdict, and it skips the per-owner embedded-criteria merge (irrelevant for `qualify_job_listings`). Prefer `monkeypatch` over assigning the module attribute directly, so the stub can't leak into other tests.

⚠️ **Decision: no `test_api_admin.py` change.** Betty's verdict: its empty-render cases stub prompt texts with no rubric tokens, so they're unaffected (confirmed: identical pass/fail sets pre/post AST-2092 in that file).

### Blast radius

- Two files, both Betty's: `tests/component/utils/test_config.py` (one class) and `docs/test-bible/utils/config.md` (one section). No `src/**`, canon or integration change.
- Other `test_config.py` classes are untouched. The 28 pre-existing reds in `test_config.py` + `test_api_admin.py` (identical on `823d37605` and the ftr, AST-2092 test-fix) are out of scope and must not grow.
- The monkeypatch is scoped to each new test; no shared fixture changes.

### What must still hold

- The other six `TestAst1779EmptyRenderForPrompts` tests are unchanged and green: candidate blank, job ignored without seam, chain never scored, job seam, `warn_on_empty` quiet, text tolerance/order.
- `[bug-repro]` red on `823d37605`, green on `origin/ftr/AST-2019-rubric-empty-render-gate`. Control green on both.
- No product source edits on this sub; the engineer's make-fix is a no-product-src marker.

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/eb1070acfeb025b5dc68043424798744/9ab40e5f-23a8-4a58-ba7c-7e05c1a4756b/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/5d4ca2d8-52dc-4e20-baf9-7b9aa29f4583/store.db` |
| Radia | review | `/home/susan/.cursor/chats/eb1070acfeb025b5dc68043424798744/31d8f277-f2d6-4373-b1ba-3d134bccbe77/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-2019 (parent) | ftr/AST-2019-rubric-empty-render-gate |
| AST-2092 | sub/AST-2019/AST-2092-rubric-empty-render-gate |
| AST-2094 | sub/AST-2019/AST-2094-rubric-empty-render-gate-tests |

**Epic worktree:** `astral-AST-2019/` — one active sub checked out at a time.

## Joan fix-board — AST-2092

```text
[board-joan]  CANON: OK
```

```text
AST-2092 board-joan done — CANON: OK.
```

## Reasoning

**Read:** `## Bug: AST-2092` on `origin/sub/AST-2019/AST-2092-rubric-empty-render-gate` (plan-fix patch); roster skim for overlap with `config.py` / dispatch validation; resolved **`astral.dispatch.entity-state-bound`** (`canon/directives/active/stat.dispatch.entity-state-bound.md`) and **`astral.standards.in-scope-only`** (`canon/statutes/astral/standards/astral.standards.in-scope-only.md`) as cited in the patch.

**The one question:** Does the proposed change conflict with or require updating any **directive in force**?

**No.** Active statutes/patterns do not encode AST-1779’s “do not score `rubric` by default” rule. That rule lives in the **AST-1779 feature plan** and test-bible (`test_rubric_scored_only_via_entity_contexts`), not in the canon corpus. Grep over `canon/directives` shows no `empty_render`, `empty_render_for_prompts`, or admin-time rubric-scoring law.

- **`astral.dispatch.entity-state-bound`:** Still satisfied. The fix only changes default scoring in `empty_render_for_prompts`; no `dispatch_task` row, `entity_type`, `trigger_state`, or claim-path edits. Aligning the admin predicate with candidate-keyed rubric resolution does not violate entity-binding law.

- **`astral.standards.in-scope-only`:** Conforms. Product footprint is `src/utils/config.py` → one function + docstring, as scoped.

Reversing AST-1779 **plan/test** contract is intentional and documented in the AST-2092 patch (rubric rows are per-candidate; matches AST-2000 runtime refusal). That is **not** a statute/pattern amend — Betty’s test/bible updates cover the behavioral contract; no F3 canon landing required from this triage pass.

**Not ESCALATE:** Blast radius and operator impact are bounded in the patch (owners that can flip Invalid, no `api_admin` change, DB read tradeoff called out). No ambiguous statute intent or new corpus precedent — correction of admin vs runtime mismatch.

context_tokens≈18500

## Radia review — AST-2092

[code-rubric]
**Ticket:** AST-2092
**Publish ref:** `5ff29d79214b2f6bf5e7e526ac102ac2c98baf1d` (`origin/sub/AST-2019/AST-2092-rubric-empty-render-gate`)
**Corpus:** `2d1b73da19cf1d14276e5c26f52b37aa8047d159`
**Overall:** CLEAN

**Diff base:** `origin/ftr/AST-2019-rubric-empty-render-gate...origin/sub/AST-2019/AST-2092-rubric-empty-render-gate` (2 files: `src/utils/config.py` product; `docs/features/dispatcher/ast-1779-empty-token-predicate-helper.md` plan-fix + board notes).

## Canon scores

| id | grade | effort | one-line |
|----|-------|--------|----------|
| astral.dispatch.entity-state-bound | A | | Scoring filter only in `empty_render_for_prompts`; no `dispatch_task` / claim-path / registry edits. |
| astral.standards.in-scope-only | A | | Product change confined to one function + docstring in `config.py`; no `api_admin.py` or out-of-scope refactors. |

## Column diff vs plan stage

no plan-stage validate-plan scores attached (Joan **fix-board CANON: OK** only; no per-id validate-plan table for AST-2092)

## Frame diff

(none)

## Fix-specific checks

- **[bug-repro]:** not applicable — clean board opt-out; Betty **TESTS: REVISE** routed contract/test work to sibling **AST-2094**; no `[bug-repro]` on this publish ref.
- **## What must still hold — OK**
  - Return shape, `empty_render` key, first-seen `seen` dedupe, `resolved == ""` (no strip), `warn_on_empty=False` probes: unchanged below the filter edit.
  - `source == "chain"` still `continue`s before the scoring filter; job still gated on `entity_contexts`; non-(candidate|rubric) sources still require `contexts` keys — `pronoun` / `config` / `output_type` remain unscored by default.
  - Candidate path unchanged (`"candidate"` in the always-score tuple).
  - No `api_admin.py`, `resolve_tokens`, `TOKEN_SOURCES`, `do_task`, or schema edits in diff.
  - Rubric tokens use the same `resolve_tokens` probe as other scored sources (DB read path already used at runtime per plan decision).

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Sibling test carry (expected):** Plan-fix lists Betty-owned deltas in `tests/component/utils/test_config.py` (flip `test_rubric_scored_only_via_entity_contexts`, `[bug-repro]`, AC 3/4). This sub tip has **no** `tests/**` changes; **AST-2094** owns the failing contract flip noted at test-fix. Product fix here is complete relative to engineer scope; full AST-1779 test contract green waits on that sibling, not a Radia block on AST-2092.
- **UT ordering:** Ticket **blocks AST-2094**; Chuckles can run clean-review shortcut to **User Testing** for the predicate behavior while tests land on the blocked sibling per lane split.

## What's solid

- Diff matches **## Proposed change** verbatim (filter + docstring only).
- Aligns admin predicate with candidate-keyed rubric resolution and AST-2000 runtime refusal without widening blast radius beyond documented owners.

## Note for Chuckles (post-review branching)

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (C7 complete) | Normal mini-parent (**AST-2019**, live `ftr/AST-2019-rubric-empty-render-gate` — not orphaned-to-dev) | → **Review Posted** → `do-all-the-things` §3h clean-review shortcut → **User Testing** directly; **resolve-child** skipped |

context_tokens≈14000

### Chuckles adjudication

Clean (PROCEED, no fix-now / discuss). Clean-review shortcut (do-all-the-things §3h) → User Testing.

### Test routing — AST-2092

docs-acceptance: no test-tree delivery on this ticket. fix-board `[board-betty] TESTS: REVISE` was routed to the gap sibling AST-2094 (rubric empty-render gate tests + bible), which lands its own `test()` / `merge-tests` on ftr.

## Joan fix-board — AST-2094

```text
[board-joan]  CANON: OK
```

```text
AST-2094 board-joan done — CANON: OK.
```

## Reasoning

**Read:** `## Bug: AST-2094` on `origin/sub/AST-2019/AST-2094-rubric-empty-render-gate-tests` @ `6401a0987` (plan-fix only on publish tip). Joan pass question: does **`### Proposed change`** conflict with or require updating any **directive in force**?

**No.** Scope is **`tests/component/utils/test_config.py`** (`TestAst1779EmptyRenderForPrompts` only) and **`docs/test-bible/utils/config.md`** (AST-1779 section). **No `src/**`, no `canon/**`. Ticket cites **no canon**; work pins the already-landed AST-2092 product contract (rubric scored by default), not statute text.

- **Roster skim:** Nothing in active `stat.*` / `patt.*` governs empty-render scoring rules or test-bible wording. AST-1779’s old “rubric only via `entity_contexts`” rule lived in feature plan + bible/tests, same as AST-2092 board conclusion.
- **Bible edits** (prose, table rows, manifest) document behavior for Betty/qa-fix; they are **not** corpus directives and do not amend `astral.dispatch.entity-state-bound`, `astral.standards.in-scope-only`, or any other in-force id.
- **Not REVISE:** No statute/pattern needs a carve-out or restatement for flipping/renaming tests or syncing the bible to AST-2092.
- **Not ESCALATE:** Test-gap sibling with bounded blast radius; product precedent was AST-2092 + Susan’s lane split to AST-2094.

context_tokens≈22000

## Radia review — AST-2094

[code-rubric]
**Ticket:** AST-2094
**Publish ref:** `b3d69a189f0d0ffc1a3a29a33c271902e7223ba0` (`origin/sub/AST-2019/AST-2094-rubric-empty-render-gate-tests`)
**Corpus:** `2d1b73da19cf1d14276e5c26f52b37aa8047d159`
**Overall:** CLEAN

**Diff base (scored):** `origin/ftr/AST-2019-rubric-empty-render-gate...origin/sub/AST-2019/AST-2094-rubric-empty-render-gate-tests`, **scoped to ticket footprint** — `tests/component/utils/test_config.py`, `docs/test-bible/utils/config.md`, plus plan-fix doc block in `docs/features/dispatcher/ast-1779-empty-token-predicate-helper.md`.

**Drift note (not a finding):** The unscoped three-dot diff shows ~77 files (many `docs/features/**` archive lines from `sync(dev)` on the publish ref). `git diff origin/dev...origin/sub/AST-2019/AST-2094-rubric-empty-render-gate-tests` collapses to **4 files** (2092 product on ftr + 2094 tests/bible/plan). **`src/**` delta vs ftr is empty (0 bytes)** — matches `code(AST-2094): no product src` and **## What must still hold**.

## Canon scores

Frozen list: **(none cited)** — AST-2094 Description / plan-fix: test tree + bible only; no directive ids to score. Joan **fix-board CANON: OK** (no statute/pattern amend required for test-gap work).

## Column diff vs plan stage

no plan-stage validate-plan scores attached (Joan **fix-board CANON: OK** only)

## Frame diff

(none)

## Fix-specific checks

- **[bug-repro] OK** — `test_empty_rubric_vectors_sets_empty_render` (first-line comment `[bug-repro] AST-2092 AC1`):
  - Pins **concrete** `{"empty_render": True, "empty_tokens": ["RUBRIC_VECTORS"]}` on `qualify_job_listings` with `_astral_candidate_id`, `Rubric:\n{$RUBRIC_VECTORS}`, and `monkeypatch` stub `rubric_criteria_for_token` → `[]`.
  - Matches AST-2092 **## To-be** / **### Repro** (not tautological; not duplicating product filter logic alone).
  - Would be **red** on pre-fix `823d37605` (`False`, `[]`) and **green** with AST-2092 on ftr — repro-first contract satisfied.
- **## What must still hold — OK**
  - Single hunk in `TestAst1779EmptyRenderForPrompts` only; six control tests (candidate blank, job/chain, seam, warn quiet, order) **unchanged** in diff.
  - Flipped + renamed `test_rubric_scored_by_default_and_via_entity_contexts` aligns default and seam assertions with AST-2092.
  - AC3 control `test_filled_rubric_vectors_validates` asserts non-flag path with one criterion.
  - No `src/**` on sub vs ftr; bible § AST-1779 prose/table/manifest/broken line match **### Proposed change** item 4.

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Publish-ref hygiene:** `sync(dev)` / archive doc commits sit on the sub tip ahead of Betty’s `test()` + `merge-tests`; score and footprint use **ftr…sub** scoped to tests/bible/plan only — do **not** treat bulk `docs/features/**` archive deltas as AST-2094 scope or cross-ticket product smuggle.
- **Lane split closed:** AST-2092 product on ftr + AST-2094 tests/bible completes Betty’s **TESTS: REVISE** routing from AST-2092 board.

## What's solid

- Plan fidelity: rename, flip, two new nodes, monkeypatch target, bible manifest lines 7–9, and obsolete note all match plan-fix bar.
- `[bug-repro]` is the Abrams / `RUBRIC_VECTORS` path from the product ticket, not the GET_RUBRIC seam-only flip alone.

## Note for Chuckles (post-review branching)

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** (C7 complete) | Normal mini-parent (**AST-2019**, live ftr) | → **Review Posted** → `do-all-the-things` §3h clean-review shortcut → **User Testing**; **resolve-child** skipped |

context_tokens≈15000

### Chuckles adjudication

Clean (PROCEED, no fix-now / discuss). sync(dev) drift on the publish ref is not ticket scope (origin/dev...sub collapses to the 2092 product + 2094 tests/bible/plan). Clean-review shortcut (do-all-the-things §3h) → User Testing.
