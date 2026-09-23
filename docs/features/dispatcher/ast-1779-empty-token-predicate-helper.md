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
