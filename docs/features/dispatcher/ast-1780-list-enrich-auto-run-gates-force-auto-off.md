# AST-1780 — List enrich, AUTO/Run gates, force AUTO off

- **Linear:** https://linear.app/astralcareermatch/issue/AST-1780
- **Parent:** AST-1766 — Dispatch Validation
- **Publish ref:** `sub/AST-1766/AST-1780-list-enrich-auto-run-gates-force-auto-off`

Wire sibling #1’s `empty_render_for_prompts` into Scheduled Actions admin API: enrich `GET /api/admin/dispatch_tasks` with boolean `empty_render`, reject AUTO-on create/update and `POST …/run` with HTTP 400 when the flag would be true, and persist AUTO off when list enrichment finds a row already AUTO-on with empty-render. Does not own the helper (AST-1779), version-hook revalidation (AST-1781), or React disable wiring (AST-1782).

## Explicit scope gate

Ticket **## Scope** covers only:

- `src/ui/api/api_admin.py` — list enrichment boolean; create/update AUTO-on + `run_dtask` gates; force AUTO off when enrichment shows empty-render.

No other files. Do not edit `src/utils/config.py`, `src/data/database.py`, `src/core/candidate.py`, or `AdminScheduledActions.tsx`. Import and call `empty_render_for_prompts` from config (shipped by AST-1779); do not reimplement token scoring.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_admin.py` | Shared empty-render eval helpers; `list_dtasks` enrichment + force AUTO off; create/update AUTO-on + `run_dtask` 400 gates beside `_candidate_dispatch_api_key_error` | ui |

## Stage 1: Eval helpers + list enrichment + force AUTO off

**Done when:** `GET /api/admin/dispatch_tasks` returns every non-hidden row with an `empty_render` boolean. For a row whose current `agent_task` + agent system texts reference a candidate-scoped token that resolves to `""` for that row’s candidate, `empty_render` is `true`. If that row’s `auto_mode` was on, after the response the DB row has `auto_mode` off and the JSON row reflects `auto_mode` falsy. A row whose candidate-scoped tokens all resolve non-empty has `empty_render: false` even when prompts also mention job tokens (no `entity_contexts` passed). No create/update/run gate changes yet.

1. In `src/ui/api/api_admin.py`, extend the existing `from src.utils.config import (` block to also import `empty_render_for_prompts`. Extend the existing `from src.core.agent import (` block to also import `_resolve_task_prompts` (same private-helper import style as `_chain_context` / `_decode_payload` already used in this file).

2. Immediately above `_candidate_dispatch_api_key_error` (scheduler / per-task thread control section), add three private helpers:

   ```python
   def _dispatch_empty_render_prompt_texts(task_key: str) -> list[str]:
       """Raw prompt segments for empty-render gating (AST-1780 / AST-1779 order)."""
       ...

   def _evaluate_dispatch_empty_render(
       candidate_id: Optional[str], task_key: str
   ) -> dict:
       """Return empty_render_for_prompts result; never raises for soft misses."""
       ...

   def _candidate_dispatch_empty_render_error(
       candidate_id: Optional[str], task_key: str
   ) -> Optional[str]:
       """If set, return a user-facing message; AUTO/Run need non-empty candidate-scoped fills."""
       ...
   ```

3. Implement `_dispatch_empty_render_prompt_texts(task_key)` literally:

   - Call `agent_row, agent_task_row = _resolve_task_prompts(task_key)` (raises `ValueError` on missing agent_task / agent_id / agent — caller handles).
   - Build the text list in this order (AST-1779 caller contract):
     1. `agent_task_row.get("system_prompt") or ""`
     2. `cache_prompt`, `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d`
     3. `nocache_prompt`
     4. `user_prompt`
     5. Agent system text: **only when** `(agent_task_row.get("system_prompt") or "").strip()` is empty, append `agent_row.get("content") or ""`. When task `system_prompt` is non-empty, runtime uses it instead of agent `content` (`resolved_task_system`) — do **not** append unused agent `content` (avoids false `empty_render` from tokens that never wire).
   - Return that list (helper skips non-str / empty entries itself).

4. Implement `_evaluate_dispatch_empty_render(candidate_id, task_key)`:

   - If `(candidate_id or "").strip()` is empty → `logger.warning` with who/why (dispatch_task task_key + “no candidate_id; treating as empty_render”) and return `{"empty_render": True, "empty_tokens": []}`.
   - `cand = database.get_candidate(candidate_id)`; if missing → warning (candidate_id + task_key + “candidate not found; treating as empty_render”) and return `{"empty_render": True, "empty_tokens": []}`.
   - `cd = build_candidate_token_view(cand)`.
   - Try `_dispatch_empty_render_prompt_texts(task_key)`; on `ValueError` → warning (candidate_id, task_key, reason from `str(exc)`) and return `{"empty_render": True, "empty_tokens": []}`.
   - On any other `Exception` → `logger.exception` with candidate_id, task_key, facts + “Leaving empty_render true for this row”, then return `{"empty_render": True, "empty_tokens": []}`.
   - Otherwise call and return:

     ```python
     empty_render_for_prompts(texts, cd, (task_key or "").strip(), entity_contexts=None)
     ```

     Never pass a job (or other) `entity_contexts` map for this epic’s gates (AST-1779 / parent AC 9–10).

5. Implement `_candidate_dispatch_empty_render_error(candidate_id, task_key)`:

   - `result = _evaluate_dispatch_empty_render(candidate_id, task_key)`.
   - If `result.get("empty_render")` is falsy → return `None`.
   - Else return a single user-facing string. If `empty_tokens` is non-empty:

     ```text
     Prompt tokens resolve empty for this candidate (cannot Auto/Run): TOKEN1, TOKEN2
     ```

     If soft-miss left `empty_tokens` empty but `empty_render` true:

     ```text
     Cannot Auto/Run: prompts could not be validated for empty-render on this candidate/task.
     ```

6. In `list_dtasks`, inside the existing `for row in rows:` enrichment loop (after `available_count` / `always_visible_under_avail_gt0` are set, before the loop ends), add:

   - `er = _evaluate_dispatch_empty_render(row.get("candidate_id"), row.get("task_key") or "")`
   - `row["empty_render"] = bool(er.get("empty_render"))`
   - If `row["empty_render"]` and `row.get("auto_mode")` is truthy (SQLite may store `1` / `True`):
     - `update_dispatch_task(row["id"], auto_mode=0)` (already imported via dispatcher).
     - Set `row["auto_mode"] = 0` (or `False` — match whatever type other rows already expose from `list_dispatch_tasks`; prefer the same integer `0` the DB uses so the list payload stays consistent).
     - `logger.warning` per forced-off row: candidate_id, task_key, dispatch id, and why (`empty_render`; include `empty_tokens` when present) — product consequence: AUTO forced off.
   - Do **not** add `logger.info` for the GET list itself (`stat.logging.info.api`: idempotent GET that returns current state is not progress). Force-off is the soft per-item miss → warning only.

⚠️ **Decision:** Fail closed when evaluation cannot run (missing candidate / agent_task / agent / unexpected throw) — `empty_render: true` + warning (or exception log). Matches epic intent: do not leave AUTO/Run open when we cannot prove fills.

⚠️ **Decision:** Agent `content` is included in prompt texts only when task `system_prompt` is blank — matches runtime `resolved_task_system`, avoids false positives from unused agent-default tokens.

⚠️ **Decision:** List field name is exactly `empty_render` (frozen by AST-1779). Do not add a second boolean under another name. `empty_tokens` may appear only inside warning/error strings, not as a required list-row field (AC asks for the boolean).

## Stage 2: AUTO-on create/update + run_dtask 400 gates

**Done when:** `POST /api/admin/dispatch_tasks` and `PUT /api/admin/dispatch_tasks/<id>` with `auto_mode: true` on an empty-render row return HTTP 400 and do not persist AUTO on (create never inserts AUTO on; update leaves prior `auto_mode`). `POST …/run` on such a row returns HTTP 400 with `started: false` and does not call `run_task`. API-key gate still runs first (unchanged). Rows that pass empty-render still proceed subject to existing API-key / Sweep rules.

1. In `create_dtask`, immediately after the existing `_candidate_dispatch_api_key_error` block that runs when `bool(data.get("auto_mode", False))` (today ~lines 1118–1121), still inside that `if` (AUTO-on only):

   ```python
   err = _candidate_dispatch_empty_render_error(
       data.get("candidate_id"), task_key
   )
   if err:
       return jsonify({"error": err}), 400
   ```

   Use the already-normalized `task_key` variable from earlier in the handler. Do not evaluate empty-render when AUTO is off on create.

2. In `update_dtask`, immediately after the existing `_candidate_dispatch_api_key_error` block inside `if updates.get("auto_mode") == 1:` (today ~lines 1308–1312), still inside that `if`:

   ```python
   err = _candidate_dispatch_empty_render_error(
       cid, effective_task_key
   )
   if err:
       return jsonify({"error": err}), 400
   ```

   `cid` is already `row.get("candidate_id")`; `effective_task_key` is already computed earlier in the handler (covers task_key change in the same PUT). Do not gate when AUTO is being turned off or left unchanged.

3. In `run_dtask`, immediately after the existing `_candidate_dispatch_api_key_error` check (today ~lines 1942–1944), before `run_task(...)`:

   ```python
   err = _candidate_dispatch_empty_render_error(
       row.get("candidate_id"), row.get("task_key") or ""
   )
   if err:
       return jsonify({"error": err, "started": False}), 400
   ```

   Mirror the API-key response shape (`started: False` on 400).

4. Do **not** add route-level `logger.info` completion lines for these 400 paths (`stat.logging.info.api` is for successful completing work). Soft reject → no warning spam beyond what `_evaluate_dispatch_empty_render` already emitted if evaluation failed; a clean empty-render reject does not need an extra warning (the 400 body is the operator signal). Unexpected exceptions in create/update/run remain on existing handler paths / `stat.logging.error` if you wrap new code in try/except — prefer letting the helpers absorb soft misses so the route stays exception-light.

⚠️ **Decision:** Gate shape mirrors `_candidate_dispatch_api_key_error` exactly (Optional[str] → 400 JSON `error`) so sibling #4 / operators see one consistent AUTO/Run refusal class. Empty-render runs **after** the API-key check so a missing key still wins the first error message.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Traceability

| AC | Stage |
|----|-------|
| 1 list boolean `empty_render` | Stage 1 |
| 2 PUT AUTO-on → 400 | Stage 2 |
| 3 POST run → 400 `started: false` | Stage 2 |
| 4 force AUTO off on enrichment | Stage 1 |
| 5 job tokens alone do not flip flag | Stage 1 (`entity_contexts=None`) |
| Parent create AUTO-on gate (same class as PUT) | Stage 2 |
| Sibling #3 revalidation hooks | out of scope (AST-1781) |
| Sibling #4 React disable | out of scope (AST-1782) |

## Joan validate

[plan-rubric]
**Ticket:** AST-1780
**Overall:** APPROVED
**Corpus:** 2ac86c3f693409c364f8630a97198c8dbfa9c6f3
**Publish ref:** `8d65b7fbe0ef8074e538c809ed9f56e90e27a692`

## Canon scores

| slug | grade | effort | note |
|------|-------|--------|------|
| astral.dispatch.entity-state-bound | A | | |
| stat.logging.info.api | A | | |
| stat.logging.warning | A | | |
| stat.logging.error | A | | |

## Traceability

AC1→Stage 1 (`empty_render` on each list row); AC2→Stage 2 (PUT `auto_mode: true` → 400); AC3→Stage 2 (`POST …/run` → 400 `started: false`); AC4→Stage 1 (force AUTO off during list enrichment; revalidation half → AST-1781); AC5→Stage 1 (`entity_contexts=None`). Parent AC 1, 3–5, 10 → Stages 1–2; parent AC 2, 6–8 → out of scope (siblings #3–#4). Parent POST create AUTO-on → Stage 2 (same gate class as PUT).

## Findings

### discuss — Canon Scope gap (do not score)

- **Severity:** discuss
- **Location:** Ticket Citations vs plan footprint
- **Finding:** `astral.standards.in-scope-only` plainly governs a single-file API slice but is absent from the frozen four-id list.
- **Recommendation:** Plan is compliant via `## Explicit scope gate` (`api_admin.py` only). Archie may amend Canon Scope at Discussion for Radia comparability; no plan change required.

### acceptable — AC4 partition across siblings

- **Severity:** acceptable
- **Location:** Child AC 4 / `## Traceability`
- **Finding:** AC wording covers list enrichment and revalidation; this plan implements only the list-enrichment force-off path (Stage 1). AST-1781 is expected to reuse the same eval helpers for version-hook revalidation.
- **Recommendation:** None for this ticket; ensure AST-1781 plan imports/calls the shared helpers rather than re-scoring.

### acceptable — Prompt-text assembly vs AST-1779 caller note

- **Severity:** acceptable
- **Location:** Stage 1 step 3 / Decision on agent `content`
- **Finding:** Plan correctly omits unused agent `content` when task `system_prompt` is non-empty, matching `resolved_task_system` runtime behavior and avoiding false positives — tighter than the generic AST-1779 caller bullet list.
- **Recommendation:** None.

context_tokens≈24000

## Review (build stub)

**Publish ref:** `origin/sub/AST-1766/AST-1780-list-enrich-auto-run-gates-force-auto-off`
**Tip:** `40e999ba`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1–2 | `40e999ba` | `empty_render` list enrich + force AUTO off; create/update/run gates |

## Radia review

[code-rubric]
**Ticket:** AST-1780
**Publish ref:** acb25c8295999a3ea13873d2c7828b80c7a341c8
**Corpus:** 2ac86c3f693409c364f8630a97198c8dbfa9c6f3
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| astral.dispatch.entity-state-bound | A | | |
| stat.logging.info.api | A | | |
| stat.logging.warning | A | | |
| stat.logging.error | A | | |

## Column diff vs plan stage

(aligned) — Joan graded all four ids **A** at validate-plan; code review agrees on every row.

## Frame diff

(none)

## Findings

### discuss — Operative artifact token view vs sibling #3 revalidation

- **Severity:** discuss
- **Location:** `src/ui/api/api_admin.py::_evaluate_dispatch_empty_render` — `build_candidate_token_view(cand)` only
- **Finding:** List enrichment / gates score tokens from the library candidate view without operative-current overlay. AST-1781 revalidation hooks use `database._token_view_for_empty_render` + `get_current_artifact` overlay. Same candidate row can yield different `empty_render` on list poll vs post–artifact-rotate revalidation until library pins catch up.
- **Recommendation:** Epic awareness for UAT — not a plan violation (Stage 1 step 4 names `build_candidate_token_view` literally). If operators report list/gate vs hook mismatch on artifact-backed tokens, consider sharing the operative overlay or hydrating before eval in a follow-up; no resolve-child work required unless UAT surfaces it.

### discuss — AC4 partition across siblings (Joan raised at plan)

- **Severity:** discuss
- **Location:** Child AC 4 / `## Traceability`
- **Finding:** AC wording covers list enrichment and revalidation; this ticket implements only the list-enrichment force-off path. AST-1781 owns version-hook revalidation (implemented separately in `database.py`, not by importing these api_admin helpers).
- **Recommendation:** Acceptable split — ensure epic UAT exercises both paths; no AST-1780 code change on this tip.

### discuss — Canon Scope gap (do not score; Joan raised at plan)

- **Severity:** discuss
- **Location:** Ticket Citations vs plan footprint
- **Finding:** `astral.standards.in-scope-only` plainly governs a single-file API slice but is absent from the frozen four-id list. Plan scope gate + implementation honor it (`api_admin.py` only for product logic).
- **Recommendation:** Archie may amend Canon Scope for Radia comparability; no plan defect.

### discuss — Epic rollup files on sub tip (not AST-1780 product scope)

- **Severity:** discuss
- **Location:** Full branch diff vs `origin/dev` also includes `src/utils/config.py` + tests (AST-1779), `src/data/database.py` + `src/core/candidate.py` + tests (AST-1781), AST-1769 bug-repro spill
- **Finding:** AST-1780 product footprint is confined to `api_admin.py`, `test_api_admin.py`, and bible (~323 lines). Integration-line merge of sibling #1 helper is expected dependency.
- **Recommendation:** Chuckles/merge-child hygiene before ftr rollup — not a canon violation for AST-1780 implementation quality.

### advisory — Component tests mock eval path

- **Severity:** advisory
- **Location:** `tests/component/ui/api/test_api_admin.py::TestAst1780EmptyRenderListGatesForceOff`
- **Finding:** List and gate tests monkeypatch `_evaluate_dispatch_empty_render` / `_candidate_dispatch_empty_render_error` rather than exercising real `empty_render_for_prompts` + agent_task prompts + candidate data. Wiring and HTTP shapes are verified; token-resolution integration is delegated to AST-1779 tests.
- **Recommendation:** Acceptable for component tier per manifest; optional follow-up integration scenario only if bible tier demands it.

### advisory — No explicit AC5 job-token-alone list test

- **Severity:** advisory
- **Location:** QA manifest / `TestAst1780EmptyRenderListGatesForceOff`
- **Finding:** AC5 (job tokens alone must not disable AUTO/Run) is enforced by `entity_contexts=None` in `_evaluate_dispatch_empty_render` but has no dedicated list/gate test analogous to AST-1779/1781 `VISIBLE_JD` cases.
- **Recommendation:** Low risk given helper contract; optional advisory test in resolve-child if Susan wants belt-and-suspenders.

## What's solid

- Stage 1: `_dispatch_empty_render_prompt_texts` matches plan order and omits unused agent `content` when task `system_prompt` is non-empty; `_evaluate_dispatch_empty_render` fail-closed with per-miss `logger.warning` and `logger.exception` only on unexpected throws; `list_dtasks` sets `empty_render`, persists `auto_mode=0`, updates JSON row, warns per forced-off row; no GET `logger.info`.
- Stage 2: create/update AUTO-on gates and `run_dtask` 400 with `started: false` mirror `_candidate_dispatch_api_key_error` shape; API-key check still runs first; clean empty-render reject has no extra warning spam.
- Revised manifest tests (`test_scheduler_and_run_controls`, create/update AUTO success) updated to stub `_candidate_dispatch_empty_render_error` → `None`.
- Estimate **5** fits single-file API slice + six new tests + bible.
- Scope gate honored: no edits to `config.py`, `database.py`, `candidate.py`, or React.

## Recommended actions (Chuckles downstream — not Radia)

1. Append this verdict to `docs/features/dispatcher/ast-1780-list-enrich-auto-run-gates-force-auto-off.md` and push `docs(AST-1780): Radia review — clean` on `origin/sub/AST-1766/AST-1780-list-enrich-auto-run-gates-force-auto-off`.
2. Post slim upshot via `linear_proxy --as radia save-comment`.
3. Move to **Review Posted**; datt routes PROCEED per §3h.
4. Track operative-view divergence (discuss) during epic UAT alongside AST-1781 — escalate only if operators see list/gate vs hook mismatch on artifact-backed tokens.

## Bug: AST-1791 — Default validation TRUE when no prompts/keys

Orphaned fix child of AST-1790 (mini-parent off `origin/dev`; Done ancestor AST-1766). Scope gate is this ticket’s own `## Scope` (copied from the bug Component/Technical scope) — `api_admin.py` soft-miss branch only; `config.py` / React unchanged unless this plan says otherwise.

### As-is

`_evaluate_dispatch_empty_render` treats every soft miss as `empty_render: true`, including when `_dispatch_empty_render_prompt_texts` / `_resolve_task_prompts` raises `ValueError` (no `agent_task` row, no `agent_id`, missing agent). Non-agent `dispatch_task` rows (no prompts / no expected tokens) therefore get `empty_render: true` on list enrichment, force AUTO off, and HTTP 400 on AUTO-on / Run — even though nothing in prompts expects a candidate token fill.

### To-be

Validation defaults to pass (`empty_render: false`, empty `empty_tokens`) when there are **no prompts to validate** (prompt-load `ValueError`). Disable AUTO/Run only when prompts load and `empty_render_for_prompts` reports candidate-scoped tokens that resolve blank (tokens expected and missing). Missing / blank `candidate_id` and unexpected evaluation exceptions stay fail-closed.

### Repro

1. Fixture shape (file/JSON persistence — no SQL seed): a `dispatch_task` row with a real `candidate_id` (candidate exists and has an API key) and a `task_key` that has **no** current `agent_task` row (non-agent keys such as gaze / `recheck_no_openings`-class tasks from AST-537).
2. `GET /api/admin/dispatch_tasks` → that row’s `empty_render` is `true`; if `auto_mode` was on, enrichment forces it off.
3. `PUT` with `auto_mode: true` or `POST …/run` → HTTP 400 with body mentioning prompts could not be validated / empty-render.
4. Contrast (still broken after fix would be a regression): same candidate, `task_key` whose `agent_task` prompts reference `{$FIRST_NAME}` (or another candidate-scoped token) that resolves to `""` → must remain `empty_render: true` and gated.

### Root cause

AST-1780 Stage 1 step 4 / Decision explicitly **fail-closed** on “cannot prove fills” — including missing `agent_task`. That conflates “prompts reference tokens that are blank” with “there are no prompts / no agent_task to score.” Predicate intent (AST-1766 AC1 / AST-1779) is blank **referenced** candidate-scoped tokens; no prompts ⇒ nothing expected ⇒ should not disable.

### Proposed change

All edits in `src/ui/api/api_admin.py` only. Do **not** edit `src/utils/config.py` or `AdminScheduledActions.tsx`.

1. **`_evaluate_dispatch_empty_render(candidate_id, task_key)`** — change only the `ValueError` branch after `_dispatch_empty_render_prompt_texts(tk)`:

   - On `ValueError` (raised by `_resolve_task_prompts`: no `agent_task` row, empty `agent_id`, or agent not found): `logger.warning` with who/why (candidate_id, task_key, `str(exc)`) stating that prompts could not be loaded and **validation passes** (no expected tokens to score) — not “treating as empty_render”. Return `{"empty_render": False, "empty_tokens": []}`.
   - Leave these branches **unchanged** (still `empty_render: True`, empty `empty_tokens`, existing warning / exception text):
     - blank / missing `candidate_id`
     - `database.get_candidate` miss
     - any other `Exception` (`logger.exception` + “Leaving empty_render true for this row”)
   - Successful prompt load → still `return empty_render_for_prompts(texts, cd, tk, entity_contexts=None)` unchanged.

2. **`_candidate_dispatch_empty_render_error`** — no message change required for the no-prompt case: after step 1, that path returns `empty_render` falsy so this helper returns `None` (AUTO/Run allowed). Keep the existing two user-facing strings for remaining `empty_render` true cases (`empty_tokens` non-empty vs soft-miss with empty `empty_tokens` — the latter now only covers no-`candidate_id` / candidate-missing / unexpected Exception).

3. **`src/utils/config.py` / `empty_render_for_prompts`** — **unchanged**. Helper already returns `empty_render: false` when no scored tokens are blank (including empty / all-blank `prompt_texts`). Policy for “cannot load prompts” lives in the api_admin soft-miss branch, not the helper.

4. **Logging statutes:** ValueError path remains a per-item `logger.warning` (`stat.logging.warning` who/why); do not add route-level `logger.info` (`stat.logging.info.api`). Unexpected throws stay `logger.exception` + fail-closed.

⚠️ **Decision:** Blank `candidate_id` and missing candidate stay fail-closed. Product intent for non-agent rows is “no prompts,” not “no candidate” — `astral.dispatch.entity-state-bound` / AST-1766 still require a real `candidate_id` on every row; API-key gate already blocks Run/Auto without a candidate. Unexpected `Exception` stays fail-closed (not a “no prompts” soft miss).

⚠️ **Decision:** All `_resolve_task_prompts` `ValueError` reasons share one fail-open return — do not special-case “No agent_task row” vs missing `agent_id` / agent. Scope treats “cannot load prompt texts” as no prompts to validate at this gate.

### Blast radius

- Same helper feeds `list_dtasks` enrichment + force AUTO off, create/update AUTO-on 400, and `run_dtask` 400 — one branch change flips all three surfaces; UI (`AdminScheduledActions.tsx`) already trusts `row.empty_render` (AST-1782) and needs no edit.
- AST-1781 (`database.py` / `candidate.py` revalidation + `_force_auto_off_if_empty_render`) does **not** call `_evaluate_dispatch_empty_render`; out of this bug’s Scope. If those hooks independently treat missing agent_task as force-off, that is a separate delta — do not expand this fix into `database.py`.
- Component tests that monkeypatch `_evaluate_dispatch_empty_render` / `_candidate_dispatch_empty_render_error` (AST-1780) are unaffected; any test that asserted real ValueError → `empty_render: true` would need Betty’s lane, not this engineer patch.
- `empty_render_for_prompts` callers elsewhere keep current semantics.

### What must still hold

- When prompts load and a referenced candidate-scoped token resolves `""`, `empty_render` stays `true`; AUTO-on / Run still 400; list still force-off AUTO (AST-1780 Stage 1–2 / AST-1766 AC1, AC3–5).
- Job / non-candidate tokens alone still must not flip the flag (`entity_contexts=None`) (AST-1766 AC9–10 / AST-1780 AC5).
- Chain tokens still ignored (AST-1779).
- Blank `candidate_id` / missing candidate still `empty_render: true` (entity-state-bound; not this bug’s carve-out).
- Unexpected evaluation exceptions still fail-closed with `logger.exception`.
- No second list boolean name; no client-side `resolve_tokens` / `TOKEN_SOURCES` (AST-1782).
- API-key gate (`_candidate_dispatch_api_key_error`) still runs and is independent of empty-render.


## Fix-board Joan findings (AST-1791)

**Verdict: CANON: OK** — AST-1780 fail-closed-on-ValueError was a plan Decision, not an in-force statute. Fix restores AST-1766 intent inside `api_admin.py`; `empty_render_for_prompts` untouched. Note: AST-1781 hooks may still force-off on missing agent_task (out of scope).


## Review-fix findings (AST-1791)

## Fix-specific checks

**[bug-repro]** not applicable — board REVISE (Betty) routed real-path coverage to sibling AST-1792; issue Notes state qa-fix skipped on this tip; no `[bug-repro]` in diff. Product fix is a two-line branch flip; AST-1780 tests monkeypatch eval and would not catch this path anyway (plan-fix Blast radius).

**## What must still hold — OK** — all seven plan-fix items verified against diff:
- Blank-token / gated AUTO-on / Run / force-off path untouched (successful load still calls `empty_render_for_prompts`).
- `entity_contexts=None` unchanged.
- Blank `candidate_id` / missing candidate still `empty_render: true`.
- Unexpected `Exception` still `logger.exception` + fail-closed.
- No new list field / no React / API-key gate unchanged.

## Findings

### discuss — Canon Scope gap (inherited; do not score)

- **Severity:** discuss
- **Location:** Ticket Citations vs `api_admin.py`-only fix footprint
- **Finding:** `astral.standards.in-scope-only` plainly governs this slice but is absent from the scored four-id list (same gap Joan raised at AST-1780 plan).
- **Recommendation:** Plan scope + diff honor it (`api_admin.py` only). Archie may amend Canon Scope; no product defect.

### discuss — Test coverage deferred to AST-1792

- **Severity:** discuss
- **Location:** `[board-betty] TESTS: REVISE` / Notes for planning
- **Finding:** Betty flagged missing real-path test for ValueError soft-miss → `empty_render: false`. No qa-fix / `[bug-repro]` on this tip; sibling AST-1792 owns the gap.
- **Recommendation:** Not fix-now on this engineer patch; track AST-1792 for repro-first bar. UAT should still spot-check non-agent rows per plan-fix Repro step 4 contrast case.

### discuss — AST-1781 hook divergence (out of scope; plan acknowledges)

- **Severity:** discuss
- **Location:** plan-fix Blast radius
- **Finding:** `database.py` / `candidate.py` revalidation may still force AUTO off on missing `agent_task` independently of this api_admin fix.
- **Recommendation:** Separate delta if UAT surfaces it; do not expand AST-1791 into `database.py`.

### advisory — Operative token view (inherited from AST-1780 Radia)

- **Severity:** advisory
- **Location:** `_evaluate_dispatch_empty_render` successful path — `build_candidate_token_view` only
- **Finding:** Unchanged by this fix; list vs AST-1781 hook mismatch on artifact-backed tokens remains an epic UAT awareness item.
- **Recommendation:** None for resolve-child on AST-1791.

## What's solid

- Diff isolates exactly the plan-fix delta: `ValueError` from `_dispatch_empty_render_prompt_texts` now returns `{"empty_render": False, "empty_tokens": []}` with who/why `logger.warning`; all other branches untouched.
- `_candidate_dispatch_empty_render_error` needs no edit — falsy eval correctly yields `None` for AUTO/Run on no-prompt rows.
- Scope gate honored: product code only in `api_admin.py`; `config.py` / React untouched.
- Estimate **3** fits a single-branch policy correction.
- Logging: no new route `logger.info`; soft miss stays warning; unexpected throws stay `logger.exception`.

## Recommended actions (Chuckles downstream — not Radia)

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** | Normal (AST-1790 In Progress; diff base `origin/ftr/AST-1790-default-validation-no-prompts`) | Append artifact → `docs(AST-1791): Radia review — clean` on publish ref → post slim upshot `--as radia` → **Review Posted** → `do-all-the-things` §3h clean-review shortcut → **User Testing** directly (`resolve-child` skipped). |

1. Append this verdict to `docs/features/dispatcher/ast-1780-list-enrich-auto-run-gates-force-auto-off.md`.
2. Post slim upshot via `linear_proxy --as radia save-comment`.
3. Do **not** block on AST-1792 test gap for this product fix.


## Docs-Acceptance (AST-1791)

Test-tree / [bug-repro] owned by sibling gap AST-1792 (fix-board TESTS: REVISE). No merge-tests on this tip.

## Bug: AST-1792 — Gap: no-prompt ValueError → empty_render false (tests)

Gap child of AST-1790 from `[board-betty] TESTS: REVISE` on AST-1791. Scope is **test + bible only** (this ticket’s `## Scope`). Product soft-miss → pass is sibling **AST-1791** (`api_admin.py`); do not re-plan or re-implement that delta here.

### As-is

`TestAst1780EmptyRenderListGatesForceOff` monkeypatches `_evaluate_dispatch_empty_render` / `_candidate_dispatch_empty_render_error`, so the ValueError soft-miss branch inside `_evaluate_dispatch_empty_render` is never exercised. Bible § AST-1780 has no node for “no agent_task / prompt-load ValueError → `empty_render: false`.” Pre-AST-1791 product returns `empty_render: true` on that path; nothing asserts the post-fix pass.

### To-be

Component coverage (and bible rows) that drive the real soft-miss branch: when `_dispatch_empty_render_prompt_texts` raises `ValueError` (no `agent_task` / cannot load prompts) and a candidate exists, `_evaluate_dispatch_empty_render` returns `empty_render: false` — list does not force AUTO off, and AUTO-on / Run are not 400’d for empty-render. Tests are **red** against pre-AST-1791 product and **green** after AST-1791 lands. Existing monkeypatched AST-1780 wiring tests stay as-is.

### Repro

1. On a tip **without** AST-1791’s ValueError→false change: call `_evaluate_dispatch_empty_render("c1", "no_agent_task_key")` with `database.get_candidate` returning a row and `_dispatch_empty_render_prompt_texts` raising `ValueError("No agent_task row for '…'")` → today returns `{"empty_render": True, …}`.
2. Same setup after AST-1791 → must return `{"empty_render": False, "empty_tokens": []}`.
3. List row with `auto_mode: 1`, same ValueError soft-miss on the live evaluate path → must keep `auto_mode` and set `empty_render: false` (pre-fix forces off).

### Root cause

AST-1780 QA deliberately stubbed the eval helper (wiring-only). That left the soft-miss policy untested; when AST-1791 flips ValueError from fail-closed to fail-open, there is no `[bug-repro]` to prove the flip.

### Proposed change

**Files only (Scope gate):**

| File | Change |
|------|--------|
| `tests/component/ui/api/test_api_admin.py` | New cases under `TestAst1780EmptyRenderListGatesForceOff` (or a sibling class `TestAst1791NoPromptValueErrorEmptyRender` in the same module) |
| `docs/test-bible/ui/api/api_admin.md` | Extend § AST-1780 (or add § AST-1791 / AST-1792 under it) with the new node ids |

**Do not edit** `src/ui/api/api_admin.py`, `src/utils/config.py`, or React — AST-1791 owns product.

1. **Helper unit (primary `[bug-repro]`):** `test_evaluate_valueerror_no_agent_task_empty_render_false`
   - Stub `admin_mod.database.get_candidate` → minimal candidate dict for `"c1"`.
   - Stub `admin_mod._dispatch_empty_render_prompt_texts` to **raise** `ValueError("No agent_task row for 'gaze'")` (or any `_resolve_task_prompts`-style message).
   - **Do not** monkeypatch `_evaluate_dispatch_empty_render`.
   - Assert `admin_mod._evaluate_dispatch_empty_render("c1", "gaze") == {"empty_render": False, "empty_tokens": []}`.
   - Assert `_candidate_dispatch_empty_render_error("c1", "gaze") is None`.
   - Red on pre-AST-1791 (expects True / non-None error); green after AST-1791.

2. **List enrich (same soft-miss, HTTP surface):** `test_list_valueerror_no_prompts_keeps_auto`
   - Same candidate + `_dispatch_empty_render_prompt_texts` → ValueError stubs; real `_evaluate_dispatch_empty_render`.
   - `list_dispatch_tasks` returns one row (`id`, `candidate_id: "c1"`, `task_key`, `auto_mode: 1`); hide-set empty; track `update_dispatch_task`.
   - `GET /api/admin/dispatch_tasks` → `empty_render is False`, `auto_mode == 1`, no force-off update.
   - Stub whatever else list enrichment already needs (same patterns as `test_list_empty_render_false_keeps_auto`) but **never** replace `_evaluate_dispatch_empty_render`.

3. **Run gate allow (optional but preferred if cheap):** `test_run_valueerror_no_prompts_allowed`
   - `get_dispatch_task` → `{candidate_id: "c1", task_key: …}`; `_candidate_dispatch_api_key_error` → `None`; same ValueError stub on `_dispatch_empty_render_prompt_texts`; real empty-render error helper.
   - `POST …/run` → not 400 for empty-render; `run_task` called (or at least not blocked by empty-render message). If create/PUT AUTO-on is cheaper than run, one AUTO-on success path with the same stub is enough instead of all three gates.

4. **Bible** (`docs/test-bible/ui/api/api_admin.md` § AST-1780):
   - Add table rows + QA manifest lines for the new test node ids.
   - One-line note: AST-1791 / AST-1790 — prompt-load `ValueError` soft-miss → `empty_render: false` (no monkeypatch of `_evaluate_dispatch_empty_render`).
   - Keep existing AST-1780 monkeypatched wiring rows; do not mark them obsolete.
   - **Integration:** none — do not invent new integration scenarios.

5. **Implementer lane:** land tests + bible on `astral-tests` / publish to this gap’s `origin/sub/…` per qa-fix / Betty ownership of the test tree — engineer `make-fix` must not edit `tests/` or `docs/test-bible/**`. Tag the primary helper test handoff `[bug-repro]` when qa-fix runs against AST-1791.

⚠️ **Decision:** Prefer stubbing `_dispatch_empty_render_prompt_texts` (raises `ValueError`) over full agent_task DB fixtures — isolates the soft-miss branch Betty flagged without re-testing AST-1779 token scoring.

⚠️ **Decision:** Blank `candidate_id` / missing-candidate fail-closed paths stay covered only by existing product behavior / optional future tests — **out of this gap’s Scope** (board asked only for no-prompt ValueError → false).

### Blast radius

- Sibling AST-1791 product tip must be on the line under test for green; red proves pre-fix. Coordinated via parent `ftr/AST-1790-…` / sync — do not change AST-1791’s `api_admin.py` here.
- Existing `TestAst1780EmptyRenderListGatesForceOff` monkeypatched cases unchanged — still validate wiring when the helper is stubbed.
- AST-1781 database revalidation hooks remain out of scope (same as AST-1791 blast note).

### What must still hold

- When prompts load and a blank candidate-scoped token is scored, `empty_render: true` / AUTO-Run 400 / force-off still pass (existing AST-1780 tests).
- Job tokens alone still must not flip the flag (`entity_contexts=None`).
- Blank/`candidate_id` miss and unexpected `Exception` remain fail-closed in product (AST-1791 decisions) — this gap does not assert those branches unless already covered.
- No second list boolean; no client-side token resolution.
- Bible remains the manifest source for AST-1780 + this gap; no invented integration tier.


## Review-fix findings (AST-1792)

## Fix-specific checks

**[bug-repro] OK** — `TestAst1791NoPromptValueErrorEmptyRender::test_evaluate_valueerror_no_agent_task_empty_render_false` is tagged `[bug-repro]` and pins concrete To-be values:
- Does **not** monkeypatch `_evaluate_dispatch_empty_render`.
- Stubs `database.get_candidate` + `_dispatch_empty_render_prompt_texts` → `ValueError("No agent_task row for 'gaze'")`.
- Asserts `{"empty_render": False, "empty_tokens": []}` and `_candidate_dispatch_empty_render_error(...) is None`.
- Would fail pre-AST-1791 (`empty_render: True`); passes with AST-1791 product already on `ftr` base.

List + Run companions (`test_list_valueerror_no_prompts_keeps_auto`, `test_run_valueerror_no_prompts_allowed`) exercise real eval on HTTP surfaces without replacing the helper — matches plan-fix optional Run gate preference.

**## What must still hold — OK**
- Existing `TestAst1780EmptyRenderListGatesForceOff` monkeypatched wiring cases untouched (additive class only).
- No product edits; no second boolean; no integration tier invented (bible says none).
- Blank-candidate / unexpected-Exception fail-closed branches correctly out of gap scope per plan-fix Decision.

## Findings

### discuss — Cross-epic merge-tests spill on publish ref (not AST-1792 scope)

- **Severity:** discuss
- **Location:** Full `ftr…sub` diff (~1122 lines) vs scoped ticket footprint (~178 lines)
- **Finding:** `merge-tests(AST-1792)` / prior commits land AST-1786/1787/1788/1789 test+bible suites (`test_contact.py`, `test_slack.py`, `test_AdminManageCandidates.test.tsx`, `test_api_contact.py`, `test_config.py`, four bible files) — unrelated Manage Candidates Slack epic, not AST-1790 validation scope.
- **Recommendation:** AST-1792 **scoped** work is clean; Chuckles should attribute merge-tests spill to correct tickets at ftr rollup and not treat AST-1792 as owner of AST-1786-family coverage. Not fix-now on the gap tests themselves.

### advisory — Optional AUTO-on create/PUT success path omitted

- **Severity:** advisory
- **Location:** plan-fix Proposed change step 3
- **Finding:** Plan marked create/PUT AUTO-on success as optional if Run is covered; Run + list + helper repro are present.
- **Recommendation:** None — plan satisfied.

## What's solid

- Scoped delta matches plan-fix exactly: new `TestAst1791NoPromptValueErrorEmptyRender` class, bible § AST-1792 under § AST-1780, plan-fix doc appended.
- Stub strategy isolates ValueError soft-miss without re-testing AST-1779 token scoring (per plan Decision).
- Estimate **2** fits ~80-line test class + bible rows; merge-tests spill is integration-line hygiene, not ticket footprint.
- No `src/ui/api/api_admin.py` change on this diff (AST-1791 product already on `ftr`).

## Recommended actions (Chuckles downstream — not Radia)

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** | Normal (AST-1790 In Progress) | Append artifact → `docs(AST-1792): Radia review — clean` on publish ref → post slim upshot `--as radia` → **Review Posted** → `do-all-the-things` §3h → **User Testing** directly (`resolve-child` skipped). |

1. Append this verdict to `docs/features/dispatcher/ast-1780-list-enrich-auto-run-gates-force-auto-off.md`.
2. Post slim upshot via `linear_proxy --as radia save-comment`.
3. Note merge-tests AST-1786 spill for rollup attribution — does not block UT on gap coverage.


## Docs-Acceptance (AST-1792)

Test/bible gap only — no product `src/` delivery; product soft-miss fix lives on AST-1791 / ftr.

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Hedy | engineer | `/home/susan/.cursor/chats/ebc0c3e8168c224834285a014fcaf396/f8ce3ca4-89f5-4981-8633-5ad49c069fa1/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/b70c6a80-337d-47a1-bdc0-a4a8c725cfe2/store.db` |
| Radia | review | `/home/susan/.cursor/chats/ebc0c3e8168c224834285a014fcaf396/54435071-678e-4245-9266-f1aaed714193/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1790 (parent) | ftr/AST-1790-default-validation-no-prompts |
| AST-1791 | sub/AST-1790/AST-1791-default-validation-no-prompts |
| AST-1792 | sub/AST-1790/AST-1792-no-prompt-valueerror-empty-render-tests |

**Epic worktree:** `astral-AST-1790/` — one active sub checked out at a time.

## Bug: AST-1794 — Silence no-agent empty_render warning

Orphaned fix child of AST-1793 (mini-parent off `origin/dev`; no ancestor box checked). Scope gate is this ticket’s own `## Scope` (copied from the bug Component/Technical scope) — `api_admin.py` ValueError soft-miss **logging** only; `config.py` / React unchanged. Residual noise after AST-1791 flipped that branch to `empty_render: false` while keeping `logger.warning`.

### As-is

List enrichment for mailbox / non-agent dispatch rows (e.g. `stage_email_meteorite`, agent n/a) correctly returns `empty_render: false` after AST-1791, but the ValueError branch in `_evaluate_dispatch_empty_render` still emits `logger.warning` with text like `agent_task '…' has no agent_id assigned. Configure via Manage Tasks.; no prompts to validate, empty_render false` — one noise line per candidate poll. Operators read it as an error.

### To-be

When prompt-load raises `ValueError` (intentional no agent / no prompts to score), evaluation still returns `{"empty_render": False, "empty_tokens": []}` and does **not** emit a warning or error log for that soft miss. Blank/`candidate_id` miss and unexpected `Exception` keep their existing `logger.warning` / `logger.exception` fail-closed paths.

### Repro

1. Fixture / live shape: a `dispatch_task` row with a real `candidate_id` and `task_key` that cannot load prompts via `_resolve_task_prompts` (e.g. `stage_email_meteorite` with empty / n/a `agent_id`, or no current `agent_task` row).
2. Trigger list enrichment (`GET /api/admin/dispatch_tasks` or Scheduled Actions refresh for that candidate).
3. As-is: row has `empty_render: false` (AUTO/Run allowed), but logs show `ui.api.api_admin: … | dispatch empty_render task_key='…' — …; no prompts to validate, empty_render false`.
4. To-be: same `empty_render: false` / gates; **no** empty-render warning line for that ValueError soft miss. Contrast: blank `candidate_id` or missing candidate still warns and stays `empty_render: true`.

### Root cause

AST-1791’s Proposed change kept a per-item `logger.warning` on the ValueError → pass path (`stat.logging.warning` who/why). That was appropriate when the branch was fail-closed (“treating as empty_render”); after the flip to intentional pass for no-prompts, the same warning reads as a misconfiguration error on every poll for n/a-agent mailbox tasks.

### Proposed change

All edits in `src/ui/api/api_admin.py` only. Do **not** edit `src/utils/config.py` or `AdminScheduledActions.tsx`.

1. **`_evaluate_dispatch_empty_render(candidate_id, task_key)`** — change only the `except ValueError as exc:` block after `_dispatch_empty_render_prompt_texts(tk)` (today ~lines 1992–2001):

   - **Remove** the `logger.warning(...)` call (the message that interpolates `exc` and ends with `no prompts to validate, empty_render false`).
   - **Keep** the return exactly: `{"empty_render": False, "empty_tokens": []}`.
   - Optional: leave a brief inline comment that ValueError here is intentional soft-miss (no prompts) — silent pass; do not reintroduce a warning.
   - Do **not** change the `exc` binding if unused after removal — drop `as exc` if the exception value is no longer referenced.

2. Leave these branches **byte-for-byte unchanged** (still log + fail-closed):

   - blank / missing `candidate_id` → `logger.warning` + `empty_render: True`
   - `database.get_candidate` miss → `logger.warning` + `empty_render: True`
   - any other `Exception` → `logger.exception` + `empty_render: True`
   - successful prompt load → `return empty_render_for_prompts(...)` unchanged

3. **`_candidate_dispatch_empty_render_error`**, list enrichment, create/update/run gates — **unchanged** (they already treat `empty_render: false` as allow).

4. **Logging statutes:** this is deliberate silence on a non-problem soft miss — do not replace the removed warning with `logger.info` / `logger.debug` / `logger.error`. Fail-closed paths keep `stat.logging.warning` / exception logging as today. Do not add route-level `logger.info` (`stat.logging.info.api`).

⚠️ **Decision:** All `_resolve_task_prompts` `ValueError` reasons stay one silent fail-open return (same carve-out as AST-1791) — do not special-case “No agent_task row” vs empty `agent_id` / missing agent for logging either.

### Blast radius

- Same helper feeds list enrichment, AUTO-on 400, and Run 400 — return value already correct; only log volume changes for n/a-agent / no-prompt rows.
- UI (`AdminScheduledActions.tsx`) unchanged — already trusts `empty_render`.
- AST-1781 database revalidation hooks remain out of Scope (same as AST-1791).
- AST-1792 / component tests that assert ValueError → `empty_render: false` stay valid; they do not require absence of logs unless Betty adds that later. Engineer must not edit `tests/` / bible on this ticket.

### What must still hold

- ValueError soft-miss still returns `empty_render: false` (AST-1791 / AST-1790 intent) — AUTO/Run still allowed; list does not force AUTO off for that reason alone.
- When prompts load and a referenced candidate-scoped token resolves `""`, `empty_render` stays `true`; gates and force-off still apply (AST-1780 / AST-1766 AC1, AC3–5).
- Blank `candidate_id` / missing candidate still `empty_render: true` with existing warnings.
- Unexpected evaluation exceptions still fail-closed with `logger.exception`.
- Job / non-candidate tokens alone still must not flip the flag (`entity_contexts=None`).
- API-key gate remains independent of empty-render.
- No edits outside `api_admin.py` for this delta.


## Fix-board Joan findings (AST-1794)

**Verdict: CANON: OK** — ValueError soft-miss is a pass, not a failed item (`stat.logging.warning` Resolution #4). Silencing the warning aligns with statute; fail-closed branches keep warning/exception logging. No statute update needed.


## Review-fix findings (AST-1794)

## Fix-specific checks

**[bug-repro] fix-now** — `[board-betty] TESTS: REVISE` is uncleared on this tip. `TestAst1791NoPromptValueErrorEmptyRender` asserts `{"empty_render": False, "empty_tokens": []}` (and list/run wiring) but **does not** assert absence of the `no prompts to validate, empty_render false` warning. No `[bug-repro]` node with `caplog` (or equivalent) pins To-be log silence; nothing in a qa-fix thread explains skip. Pre-fix ftr branch logged `logger.warning` on every ValueError soft-miss — a real repro would fail red there and green after this product commit. Betty’s board ask is the right bar for this bug; engineer plan correctly forbids `tests/` edits — **qa-fix** (or a gap child) must land the assertion before UT treats the REVISE as closed.

**## What must still hold — OK** — all seven plan-fix items verified against diff:
- ValueError soft-miss still `{"empty_render": False, "empty_tokens": []}`.
- Successful prompt load still `empty_render_for_prompts(..., entity_contexts=None)`.
- Blank `candidate_id` / missing candidate still `logger.warning` + `empty_render: true` (lines 1974–1988 untouched).
- Unexpected `Exception` still `logger.exception` + fail-closed (1996–2004 untouched).
- No replacement info/debug/error on soft-miss path; fail-closed paths keep warning/exception logging.
- API-key gate / React / `config.py` untouched.
- Product delta only in `api_admin.py` (+ plan-fix doc).

## Findings

### fix-now — [bug-repro] / board REVISE uncleared

- **Severity:** fix-now (test bar — Betty lane, not product `resolve-child`)
- **Location:** `tests/component/ui/api/test_api_admin.py` `TestAst1791NoPromptValueErrorEmptyRender`; `[board-betty] TESTS: REVISE` on AST-1794
- **Finding:** Board flagged missing coverage for warning silence; tip reached Tests Passed with no qa-fix diff and no caplog assertion. Product fix is correct but the repro-first contract for a REVISE-flagged fix is not met.
- **Recommendation:** Spawn **qa-fix** (extend `TestAst1791…` + bible row) or file a gap child; do not block on engineer `resolve-child` for `api_admin.py`.

### discuss — Canon Scope gap (inherited; do not score)

- **Severity:** discuss
- **Location:** Ticket Citations vs `api_admin.py`-only footprint
- **Finding:** `astral.standards.in-scope-only` governs this slice but is absent from the scored four-id list (same gap Joan raised at AST-1780 / AST-1791).
- **Recommendation:** Plan scope + diff honor it. Archie may amend Canon Scope; no product defect.

### discuss — Board REVISE vs plan-fix Blast radius

- **Severity:** discuss
- **Location:** plan-fix `### Blast radius` vs `[board-betty] TESTS: REVISE`
- **Finding:** Plan says log absence “unless Betty adds that later”; Betty added via board REVISE on this ticket, but no qa-fix landed before Tests Passed.
- **Recommendation:** Lane hygiene — reconcile REVISE closure (qa-fix) with engineer no-test rule; not a product revert.

### advisory — AST-1781 hook divergence (out of scope; inherited)

- **Severity:** advisory
- **Location:** plan-fix Blast radius / AST-1791 Radia carry-forward
- **Finding:** `database.py` / `candidate.py` revalidation may still force AUTO off independently; unchanged by this logging-only delta.
- **Recommendation:** Separate delta if UAT surfaces it.

## What's solid

- Diff isolates exactly plan-fix: remove ValueError-branch `logger.warning`, keep fail-open return, drop unused `exc`, add intentional soft-miss comment (AST-1794).
- Fail-closed branches byte-for-byte preserved on ftr base.
- No `logger.info` / `logger.debug` / `logger.error` substitute on soft-miss path.
- Scope gate honored: product only `api_admin.py`; estimate **2** fits.
- Joan fix-board `CANON: OK` aligns with `stat.logging.warning` Resolution #4.

## Recommended actions (Chuckles downstream — not Radia)

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **REVIEW** (test bar fix-now; product clean) | Normal (AST-1793 In Progress; diff base `origin/ftr/AST-1793-no-agent-empty-render-warning`) | Append artifact → `docs(AST-1794): Radia review — findings` on publish ref → post slim upshot `--as radia` → **Review Posted** → route **qa-fix** / gap for caplog `[bug-repro]` (Betty lane) → re-test → second Radia pass or UT once REVISE closed. **Do not** use §3h clean-review shortcut until bug-repro bar clears. `resolve-child` on product not expected. |

1. Append this verdict to `docs/features/dispatcher/ast-1780-list-enrich-auto-run-gates-force-auto-off.md`.
2. Post slim upshot via `linear_proxy --as radia save-comment`.
3. Spawn qa-fix for Betty’s board item (warning silence in `TestAst1791NoPromptValueErrorEmptyRender`) before User Testing.

**Chuckles note:** `[board-betty] TESTS: REVISE` owned by sibling gap AST-1795 (qa-fix landed `[bug-repro]`). Product tip docs-acceptance — no merge-tests on AST-1794.



## Docs-Acceptance (AST-1794)

Test-tree / [bug-repro] owned by sibling gap AST-1795 (fix-board TESTS: REVISE). No merge-tests on this tip.
