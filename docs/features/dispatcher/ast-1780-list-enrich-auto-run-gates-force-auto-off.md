<!-- linear-archive: AST-1780 archived 2026-10-02 -->

## Linear archive (AST-1780)

**Archived:** 2026-10-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1780/list-enrich-autorun-gates-force-auto-off-dispatch-validation  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** hedy  
**Priority / estimate:** None / 5  
**Parent:** AST-1766 — Dispatch Validation  
**Blocked by / blocks / related:** parent: AST-1766; blocks: AST-1782

### Description

## What this implements

Owns Scheduled Actions list enrichment, AUTO-on / Run API 400 gates, and persisting AUTO off when a row is non-executable. After #1. Does not own `agent_task` / artifact version hooks (sibling #3) or React (sibling #4).

## Citations

`astral.dispatch.entity-state-bound`, `stat.logging.info.api`, `stat.logging.warning`, `stat.logging.error`; patterns: none (`no established pattern applies`; mirror `_candidate_dispatch_api_key_error`).

## Scope

`src/ui/api/api_admin.py` — list enrichment boolean; create/update AUTO-on + `run_dtask` gates; force AUTO off when enrichment shows empty-render.

## Acceptance criteria

- [X] Predicate **A** (candidate-scoped): for a row whose prompts reference a candidate-source or candidate-backed artifact token that resolves to `""` for that row’s candidate, `GET /api/admin/dispatch_tasks` includes an explicit boolean on that row that is `true` for empty-render. **Fail:** flag missing, or `false` while such a token resolves blank.
- [X] `PUT …/dispatch_tasks/<id>` with `auto_mode: true` on a failing row returns HTTP 400 and does not persist AUTO on. **Fail:** 200 with AUTO stored on.
- [X] `POST …/dispatch_tasks/<id>/run` on a failing row returns HTTP 400 with `started: false` (or equivalent) and does not start the thread. **Fail:** thread starts or `started: true`.
- [X] A row that was AUTO on becomes AUTO off after list enrichment / revalidation once empty-render is true (persisted). **Fail:** `auto_mode` remains on after enrichment when the flag is true. (List-enrichment force-off path; version-hook revalidation remains sibling #3.)
- [X] A row whose candidate-scoped tokens all resolve non-empty keeps AUTO and Run/Sweep enabled (subject to existing API-key and Sweep/min_count rules), even if prompts also reference job tokens that would be blank without a job context. **Fail:** controls disabled solely because job tokens are empty.

## Boundaries

- [X] Does not own the predicate helper (sibling #1), `agent_task` / artifact version hooks (sibling #3), or React disable wiring (sibling #4).

## Notes for planning

After #1. Mirror `_candidate_dispatch_api_key_error` gate shape.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1766-dispatch-validation`, child `sub/AST-1766/AST-1780-list-enrich-auto-run-gates-force-auto-off`. Created at dispatch-parent.

## QA test manifest

1. List force off: `tests/component/ui/api/test_api_admin.py::TestAst1780EmptyRenderListGatesForceOff::test_list_sets_empty_render_and_forces_auto_off`
2. List keeps AUTO: `tests/component/ui/api/test_api_admin.py::TestAst1780EmptyRenderListGatesForceOff::test_list_empty_render_false_keeps_auto`
3. Create 400: `tests/component/ui/api/test_api_admin.py::TestAst1780EmptyRenderListGatesForceOff::test_create_auto_on_empty_render_400`
4. PUT 400: `tests/component/ui/api/test_api_admin.py::TestAst1780EmptyRenderListGatesForceOff::test_put_auto_on_empty_render_400`
5. Run 400: `tests/component/ui/api/test_api_admin.py::TestAst1780EmptyRenderListGatesForceOff::test_run_empty_render_400_started_false`
6. Helper None: `tests/component/ui/api/test_api_admin.py::TestAst1780EmptyRenderListGatesForceOff::test_error_helper_none_when_evaluate_false`
7. Revised run success: `tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_scheduler_and_run_controls`
8. Revised create AUTO: `tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_create_dispatch_task_auto_mode_success`
9. Revised update AUTO: `tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_update_dispatch_task_scored_score_floor_and_auto_mode_success`

```bash
./scripts/testing/run_component_tests.sh   tests/component/ui/api/test_api_admin.py::TestAst1780EmptyRenderListGatesForceOff   tests/component/ui/api/test_api_admin.py::TestDispatchTasks::test_scheduler_and_run_controls   tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_create_dispatch_task_auto_mode_success   tests/component/ui/api/test_api_admin.py::TestApiAdminBranchGaps::test_update_dispatch_task_scored_score_floor_and_auto_mode_success   -q
```

**Bible shasum (publish tip):**

* `docs/test-bible/ui/api/api_admin.md` — `abe45f830bb58ee1585f059eb400e21c03900e06`

**Publish tip:** `origin/sub/AST-1766/AST-1780-list-enrich-auto-run-gates-force-auto-off` @ `acb25c82`

### Comments

#### hedy — 2026-09-23T02:00:13.118Z
`origin/sub/AST-1766/AST-1780-list-enrich-auto-run-gates-force-auto-off` @ `c2690426` · stacked on ftr

#### radia — 2026-09-23T01:58:24.471Z
[code-rubric] PROCEED (Commit: acb25c82) list gates and force-off clean

#### betty — 2026-09-23T01:55:42.175Z
`origin/sub/AST-1766/AST-1780-list-enrich-auto-run-gates-force-auto-off` @ `acb25c82` · empty_render gates manifest

#### hedy — 2026-09-23T01:51:37.291Z
`origin/sub/AST-1766/AST-1780-list-enrich-auto-run-gates-force-auto-off` @ `3f1ff2eb` · tip rebuilt for Betty (1779 base + AST-1780-only)

#### betty — 2026-09-23T01:48:33.500Z
@susan — suspected scope issue: `origin/sub/AST-1766/AST-1780-list-enrich-auto-run-gates-force-auto-off` tip includes sibling AST-1781 product before this child’s own gates are reviewed.

Evidence:
- Tip history has `sync(publish-ref): origin/sub/.../AST-1781-…` then `code(AST-1781): empty-render revalidate helpers + force AUTO off` landing `src/data/database.py` (+218 / revalidate helpers), then `code(AST-1780)` on top.
- Ticket Scope / plan Explicit scope gate: `api_admin.py` only — “Do not edit … `database.py`”; sibling #3 (version hooks) is AST-1781 and blockedBy this child, not the other way around.
- `code(AST-1780)` itself is in-scope (`api_admin.py` only +113). The out-of-scope surface is the AST-1781 commits baked into this publish tip.

Recommendation: rebuild / force the 1780 tip from AST-1779 tip + only `code(AST-1780)` / docs for this child (strip 1781 sync + `code(AST-1781)`), then Betty resumes qa-child. Do not advance to Tests Ready until the tip matches Scope.

#### joan — 2026-09-23T01:42:18.789Z
[plan-rubric] PROCEED (Commit: 8d65b7fbe0ef8074e538c809ed9f56e90e27a692) API gates plan clean

#### hedy — 2026-09-23T01:39:38.474Z
`origin/sub/AST-1766/AST-1780-list-enrich-auto-run-gates-force-auto-off` @ `8d65b7fb` · plan ready

---

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
| Hedy | engineer | `/home/susan/.cursor/chats/c09ef93331882a7375376d0a6349d142/3c823846-3d8c-4c32-a5ff-5264cff2a9e8/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/dbfade24-93b0-4932-9c98-c9c58943de8f/store.db` |
| Radia | review | `/home/susan/.cursor/chats/c09ef93331882a7375376d0a6349d142/61687e80-1df3-4a29-b2a9-ef3821ca4958/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-2013 (parent) | ftr/AST-2013-rubric-dup-dispatch-gate |
| AST-2091 | sub/AST-2013/AST-2091-rubric-dup-dispatch-gate |

**Epic worktree:** `astral-AST-2013/` — one active sub checked out at a time.

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

## Bug: AST-1795 — Gap: assert no-agent empty_render soft-miss warning silence

Gap child of AST-1793 from `[board-betty] TESTS: REVISE` on AST-1794. Scope is **test + bible only** (this ticket’s `## Scope`). Product silence of the ValueError soft-miss `logger.warning` is sibling **AST-1794** (`api_admin.py`); do not re-plan or re-implement that delta here. Soft-miss **return** coverage already lives in `TestAst1791NoPromptValueErrorEmptyRender` (AST-1792); this gap adds the missing **silence** assertion Betty flagged.

### As-is

`TestAst1791NoPromptValueErrorEmptyRender::test_evaluate_valueerror_no_agent_task_empty_render_false` (and list/run siblings) assert ValueError → `empty_render: false` / gates allow, but **do not** assert that the soft-miss path skips `logger.warning` with the `no prompts to validate` / no-agent_id message. Bible § AST-1792 has no node for warning silence. Pre-AST-1794 product still emits that warning on every soft-miss evaluate; nothing fails red for the noise.

### To-be

Component coverage (and bible row) that drives the real soft-miss branch **and** asserts no soft-miss warning: when `_dispatch_empty_render_prompt_texts` raises `ValueError` and a candidate exists, `_evaluate_dispatch_empty_render` returns `empty_render: false` **and** `logger.warning` is **not** called with a message containing `no prompts to validate` (the AST-1791 soft-miss warning text). Tests are **red** against pre-AST-1794 product (warning still emitted) and **green** after AST-1794 lands. Existing AST-1792 return/gate assertions stay as-is.

### Repro

1. On a tip **with** AST-1791 soft-miss→false but **without** AST-1794 silence: same stubs as `test_evaluate_valueerror_no_agent_task_empty_render_false` (`get_candidate` present, `_dispatch_empty_render_prompt_texts` raises `ValueError`) plus a spy on `admin_mod.logger.warning` → return is already `{"empty_render": False, …}` but `logger.warning` was called with text including `no prompts to validate`.
2. Same setup after AST-1794 → return unchanged **and** `logger.warning` not called for that soft-miss (no call whose formatted message / args contain `no prompts to validate`).
3. Contrast (must still pass / not assert silence): blank `candidate_id` or missing candidate still warn — out of this gap’s Scope.

### Root cause

AST-1792 proved the fail-open return. AST-1794’s delta is log-only; Betty’s board note: return covered, silence of `no prompts to validate` warning not asserted — no `[bug-repro]` to prove the silence flip.

### Proposed change

**Files only (Scope gate):**

| File | Change |
|------|--------|
| `tests/component/ui/api/test_api_admin.py` | New case under `TestAst1791NoPromptValueErrorEmptyRender` (or sibling class `TestAst1794NoPromptValueErrorSilent` in the same module) |
| `docs/test-bible/ui/api/api_admin.md` | Extend § AST-1792 / add § AST-1795 under the AST-1780 empty-render cluster with the new node id |

**Do not edit** `src/ui/api/api_admin.py`, `src/utils/config.py`, or React — AST-1794 owns product.

1. **Helper unit (primary `[bug-repro]`):** `test_evaluate_valueerror_soft_miss_no_warning`
   - Reuse `_stub_no_agent_task_prompts` (or identical stubs): candidate present; `_dispatch_empty_render_prompt_texts` raises `ValueError` (e.g. `No agent_task row for '…'` or no-`agent_id` wording — any `_resolve_task_prompts`-style message).
   - **Do not** monkeypatch `_evaluate_dispatch_empty_render`.
   - Spy `admin_mod.logger.warning` (MagicMock or list-append monkeypatch).
   - Call `_evaluate_dispatch_empty_render("c1", "gaze")` (or `stage_email_meteorite`).
   - Assert return `{"empty_render": False, "empty_tokens": []}` (keeps AST-1791 invariant).
   - Assert **no** `logger.warning` invocation whose message / joined args contain the substring `no prompts to validate` (the soft-miss warning AST-1794 removes). Prefer also `assert mock_warning.call_count == 0` on this stub path — only the soft-miss branch runs, so any warning is noise.
   - Red on pre-AST-1794 (warning still fired); green after AST-1794 silence.

2. **Do not require** new list/run HTTP cases solely for silence — list/run already exercise the same evaluate path; the helper unit is the board’s missing coverage. Optional: one assert in the existing helper test that folds silence into `test_evaluate_valueerror_no_agent_task_empty_render_false` is acceptable **only if** that keeps a clear `[bug-repro]` that fails pre-AST-1794; prefer a dedicated method so AST-1792’s return repro stays historically clear.

3. **Bible** (`docs/test-bible/ui/api/api_admin.md`):
   - Add a short § AST-1795 (under / beside § AST-1792) naming the new node id + one-line note: AST-1794 — ValueError soft-miss stays `empty_render: false` **and** emits no `no prompts to validate` warning.
   - Add QA manifest line for the new `[bug-repro]` test.
   - Keep AST-1780 / AST-1792 rows; do not mark them obsolete.
   - **Integration:** none — do not invent new integration scenarios.

4. **Implementer lane:** land tests + bible on `astral-tests` / publish to this gap’s `origin/sub/…` per qa-fix / Betty ownership of the test tree — engineer `make-fix` must not edit `tests/` or `docs/test-bible/**`. Tag the primary helper silence test `[bug-repro]` when qa-fix runs against AST-1794.

⚠️ **Decision:** Spy the module logger used by `_evaluate_dispatch_empty_render` (`admin_mod.logger`), not a global root logger — match production `get_logger` binding in `api_admin.py`.

⚠️ **Decision:** Fail-closed warning paths (blank / missing `candidate_id`, unexpected `Exception`) stay out of this gap — board asked only for soft-miss silence.

### Blast radius

- Sibling AST-1794 product tip must be on the line under test for green; red proves pre-silence. Coordinated via parent `ftr/AST-1793-…` / sync — do not change AST-1794’s `api_admin.py` here.
- Existing `TestAst1791NoPromptValueErrorEmptyRender` return/list/run cases unchanged in intent; only additive silence coverage.
- AST-1781 database revalidation hooks remain out of scope.

### What must still hold

- ValueError soft-miss still returns `empty_render: false` (AST-1791 / AST-1792 assertions).
- When prompts load and a blank candidate-scoped token is scored, `empty_render: true` / AUTO-Run 400 / force-off still pass (existing AST-1780 tests).
- Blank/`candidate_id` miss and unexpected `Exception` remain fail-closed with their existing logs (product; this gap does not assert those).
- No product `src/` edits on this tip; bible remains the manifest source; no invented integration tier.


## Review-fix findings (AST-1795)

**Overall: CLEAN / PROCEED** — `[bug-repro]` `test_evaluate_valueerror_soft_miss_no_warning` pins silence of `no prompts to validate` warning on ValueError soft-miss; return still `empty_render: false`. Closes AST-1794 board TESTS:REVISE. Advisory only: § AST-1792 bible row still labels the return test `[bug-repro]` (manifest already demoted); bible shasum placeholder.

## Docs-Acceptance (AST-1795)

Test/bible gap only — product silence on sibling AST-1794 / ftr.

_Product silence: sibling AST-1794 / ftr. Test delivery: merge-tests(AST-1795)._

## Bug: AST-1854 — Admin token resolves use the hydrated candidate view

Orphaned fix child of AST-1852 (mini-parent off `origin/dev`; no ancestor box checked). Scope gate is this ticket's own `## Scope` (copied from the bug Component/Technical scope) — `src/ui/api/api_admin.py` `_evaluate_dispatch_empty_render`, `_enrich_tasks`, ad hoc run handler (`_resolve_adhoc`): swap the candidate loader only. Product only; tests/bible are Betty's. This is the "operative artifact token view" divergence Radia flagged as discuss on AST-1780 (and carried forward on AST-1791), now surfaced in UAT.

### As-is

Scheduled Actions flags `craft_do_rubric` for candidate somerset as `empty_render: true` with `IDEAL_DAY` in `empty_tokens` (AUTO forced off, AUTO-on / Run 400), even though somerset has a current Ideal Day. `_evaluate_dispatch_empty_render`, `_enrich_tasks`, and `_resolve_adhoc` each load the candidate with raw `database.get_candidate(...)` and pass it straight to `build_candidate_token_view`, so no operative artifact rows are overlaid.

### To-be

All three admin call sites load the candidate with the hydrated `src.core.candidate.get_candidate` (operative artifact rows overlaid onto `candidate_data.context`, legacy blob kept on artifact miss) before `build_candidate_token_view` — the same view the runtime path builds (`src/core/agent.py` ~456–474). Somerset's `craft_do_rubric` validates `empty_render: false`; a candidate with neither a current Ideal Day artifact nor a legacy `context.ideal_day` blob still gets `empty_render: true` / `IDEAL_DAY` in `empty_tokens`.

### Repro

Fixture shape (no SQL seed — persistence is file/JSON / artifacts rows via existing helpers):

1. Candidate `c1` whose `candidate_data.context` has **no** `ideal_day` key (post-AST-1659 save popped it), and a current operative Ideal Day artifact for `c1` (`get_candidate_current("c1", <ideal day artifact key>)` returns a non-empty string, e.g. `"Deep work mornings, collaborative afternoons."`).
2. An `agent_task` for `craft_do_rubric` whose prompt text references `{$IDEAL_DAY}`; a `dispatch_task` row `{candidate_id: "c1", task_key: "craft_do_rubric", auto_mode: 1}`.
3. As-is: `_evaluate_dispatch_empty_render("c1", "craft_do_rubric")` → `{"empty_render": True, "empty_tokens": [... "IDEAL_DAY" ...]}`; `GET /api/admin/dispatch_tasks` forces `auto_mode` → 0; `POST …/run` → 400 "Prompt tokens resolve empty…". Task Manager (`_enrich_tasks("c1")`) and ad hoc preview/test for `c1` likewise resolve `{$IDEAL_DAY}` to `""`.
4. To-be: same fixture → `empty_render: False`, `auto_mode` stays 1, Run not blocked by empty-render; Task Manager / ad hoc resolve `{$IDEAL_DAY}` to the artifact string.
5. Contrast (must still fail): candidate `c2` with no Ideal Day artifact and no legacy `context.ideal_day` → `empty_render: True`, `IDEAL_DAY` in `empty_tokens`.
6. Contrast (must still pass): candidate `c3` with legacy `context.ideal_day` blob and no artifact row → `empty_render: False` (hydrate miss leaves the blob untouched).

### Root cause

Since the AST-1643 migration (AST-1659 blob retirement / AST-1660 Ideal Day wire-up), a UI-saved Ideal Day (and the other migrated context artifacts: base resume, resume structure, strengths, priorities, deal breakers, bio summary, backstory, writing preferences) lives only in the artifacts table. The hydrated loader `src.core.candidate.get_candidate` overlays those rows onto `candidate_data.context`; raw `database.get_candidate` does not. AST-1780 Stage 1 step 4 literally named `database.get_candidate` + `build_candidate_token_view` (pre-migration assumption), and `_enrich_tasks` / `_resolve_adhoc` predate the migration with the same raw read. `{$IDEAL_DAY}` walks `context.ideal_day`, finds nothing, and `empty_render_for_prompts` scores it blank.

### Proposed change

All edits in `src/ui/api/api_admin.py` only. Do **not** edit `src/utils/config.py` (`resolve_tokens` / `empty_render_for_prompts`), `src/core/candidate.py` (`get_candidate`, `hydrate_operative_*`, `build_candidate_token_view`), or `src/core/agent.py`.

1. **Import:** add `get_candidate` to the existing `from src.core.candidate import (` block (today lines 37–41, alongside `build_candidate_token_view`). Bare name, same import style as `src/core/agent.py`. No module-level name collision — `api_admin.py` only references the raw loader as `database.get_candidate`.

2. **`_evaluate_dispatch_empty_render(candidate_id, task_key)`** (today ~line 2025): replace `cand = database.get_candidate(cid)` with `cand = get_candidate(cid)`. Everything else byte-for-byte unchanged: blank-`cid` warning + `empty_render: True`; `if not cand:` warning + `empty_render: True` (hydrated loader returns `None` on the same miss); `cd = build_candidate_token_view(cand)`; silent `ValueError` soft-miss pass (AST-1791/1794); `logger.exception` fail-closed; `empty_render_for_prompts(texts, cd, tk, entity_contexts=None)`.

3. **`_enrich_tasks(candidate_id)`** (today ~line 385): replace `database.get_candidate(candidate_id) if candidate_id else None` with `get_candidate(candidate_id) if candidate_id else None`. Leave the `build_candidate_token_view(candidate) if candidate else {}` line and the AST-1014 comment as-is.

4. **`_resolve_adhoc(body)`** (ad hoc run handler, today ~line 1583): replace `candidate = database.get_candidate(candidate_id)` with `candidate = get_candidate(candidate_id)`. `candidate` is also used later in the handler (API key override etc.); the hydrated row carries the same top-level columns (`database.get_candidate` row + `candidate_data` overlay only), so downstream reads are unaffected.

5. No new function, table, field, log line, cap, or cache. Three one-token loader swaps + one import name.

⚠️ **Decision:** Hydration placement mirrors the raw call exactly — `_evaluate_dispatch_empty_render` keeps the load **outside** its `try`, as today. An artifact-read exception propagates the same way a DB read exception already does; no new catch/fail-open added (out of scope, and would change AST-1780 fail-closed behavior).

⚠️ **Decision:** Swap covers all migrated context artifacts the hydrated loader overlays, not just Ideal Day — that is what "same view as runtime" means; no per-token special-casing.

### Blast radius

- `_evaluate_dispatch_empty_render` feeds `list_dtasks` enrichment + force AUTO off, create/update AUTO-on 400, and `run_dtask` 400 — all three flip to the hydrated view together. React (`AdminScheduledActions.tsx`) trusts `row.empty_render`; no edit.
- `_enrich_tasks` → Task Manager token counts / cache threshold; `_resolve_adhoc` → `adhoc_preview` / `adhoc_test`. Values for artifact-only candidates change from `""` to the operative string (intended).
- Per-candidate cost: each load now also runs the nine `hydrate_operative_*` artifact reads (`list_dtasks` calls eval once per row). Same cost runtime already pays; no cap/cache added per Susan's no-shortcuts rule.
- AST-1781 `database._token_view_for_empty_render` revalidation hooks already overlay operative current — this fix converges list/gate with those hooks (Radia's AST-1780 discuss item).
- **Tests (Betty's lane):** 11 references in `tests/component/ui/api/test_api_admin.py` stub `admin_mod.database.get_candidate`. The hydrated loader calls `database.get_candidate` on the same `src.data.database` module object, so those stubs still take effect — but the hydrate helpers then call `get_candidate_current` against the test DB. Tests that stub only the raw loader may need an artifact-read stub (or stub `admin_mod.get_candidate` directly). Engineer does not edit `tests/`.
- Out of Scope, not changed: `_resolve_agent_preview_candidate` (~line 175, agent preview) also uses raw `database.get_candidate` → `build_candidate_token_view`; same divergence class. `_candidate_dispatch_api_key_error` (~line 2075) reads the API-key column only — unaffected by artifacts. Flag for Susan/Chuckles if agent preview should follow in a separate delta.

### What must still hold

- Blank `candidate_id` / missing candidate → `empty_render: True` with existing warnings (AST-1780 / AST-1791 decisions).
- Prompt-load `ValueError` → silent `{"empty_render": False, "empty_tokens": []}` (AST-1791 / AST-1794).
- Unexpected evaluation exceptions → `logger.exception` + fail-closed.
- Referenced candidate-scoped token truly blank (no artifact, no legacy blob) → `empty_render: True`; AUTO-on / Run 400; list force-off (AST-1766 AC1, AC3–5).
- Legacy-blob-only candidates still resolve (hydrate miss leaves the blob).
- `entity_contexts=None` — job tokens alone never flip the flag (AST-1780 AC5).
- API-key gate runs first and is independent of empty-render.
- No edits outside `api_admin.py`; `config.py` resolve semantics, `hydrate_operative_*`, and `agent.py` untouched.

## Joan fix-board — AST-1854

Fix-board Joan pass on **AST-1854** (`plan-fix` § Bug: AST-1854 on `origin/sub/AST-1852/AST-1854-dispatch-gate-hydrated-candidate`).

**Triage:** Three loader swaps (`database.get_candidate` → `get_candidate`) in `_evaluate_dispatch_empty_render`, `_enrich_tasks`, and `_resolve_adhoc` align admin token resolution with the runtime path. That **conforms** to `patt.artifact.read-current` intent (current operative bodies, not stale blob-only context) and `astral.dispatch.entity-state-bound` (still entity/candidate-bound; blank/missing candidate behavior unchanged). No in-force statute requires raw DB reads for empty-render or Task Manager/ad hoc resolves. AST-1780’s written `database.get_candidate` step is a **feature-plan decision**, same class as Joan’s **CANON: OK** on AST-1791 — not a canon contradiction. Logging statutes untouched (no new `logger.info` / route spam). Out-of-scope `_resolve_agent_preview_candidate` is a separate product delta, not an Archie canon halt.

---

BEGIN-VERDICT

[board-joan]  CANON: OK

END-VERDICT

```text
AST-1854 board-joan done — CANON: OK.
```

## Radia review — AST-1854

[code-rubric]

**Ticket:** AST-1854  
**Publish ref:** `b5a72977af962d9e8fdd8b797e0e5e9444898f4c` (`origin/sub/AST-1852/AST-1854-dispatch-gate-hydrated-candidate`)  
**Diff base:** `origin/ftr/AST-1852-dispatch-gate-hydrated-candidate...origin/sub/AST-1852/AST-1854-dispatch-gate-hydrated-candidate` (product delta: `src/ui/api/api_admin.py` + plan-fix patch in issue doc)  
**Corpus:** `bd68954dc854ca80fca1fc391821dff9ff288a7a` (canon tree at publish ref; no `docs/canon-index.md` on this ref — ids resolved from `canon/**` on same tip)  
**Overall:** CLEAN  

**Status gate:** Spawn prompt `Tests Passed` / assignee Hedy — trusted; no re-fetch block.

## Fix-specific checks

**[bug-repro]** not applicable — `[board-betty] TESTS: REVISE` on AST-1854; repro-first coverage owned by sibling **AST-1855** (`origin/sub/AST-1852/AST-1855-dispatch-gate-hydrated-candidate` @ `6c083f3c`, red at ftr `3dd7f249`, green with this fix overlaid per spawn prompt). No qa-fix / no `[bug-repro]` on this tip; valid board opt-out for the product child (same lane pattern as AST-1791 → AST-1792).

**## What must still hold — OK** — traced against tip `api_admin.py` + unchanged branches around the three swaps:

| Item | Verdict |
|------|---------|
| Blank `candidate_id` / missing candidate → `empty_render: True` + existing warnings | Unchanged guards before/after `get_candidate(cid)` |
| Prompt-load `ValueError` → silent `empty_render: False` | `try`/`except ValueError` block untouched |
| Unexpected evaluation exceptions → `logger.exception` + fail-closed | `except Exception` block untouched |
| Truly blank candidate-scoped token → fail gates | Still `empty_render_for_prompts` on hydrated `cd` |
| Legacy-blob-only (hydrate miss leaves blob) | `get_candidate` behavior unchanged; plan § Repro c3 still holds for `ideal_day` |
| `entity_contexts=None` | Unchanged call |
| API-key gate independent of empty-render | `_candidate_dispatch_api_key_error` still raw `database.get_candidate` (column-only); runs before empty-render on Run |
| No edits outside `api_admin.py` for product | Diff is import + three loader swaps only (+ issue doc) |

## Canon scores

*(Frozen **Canon Scope** on Linear AST-1854 description: **none** — same process gap as other fix children. Scored **fix-board Joan overlap** from plan-fix § Bug: AST-1854 / `## Joan fix-board — AST-1854`; logging statutes noted **id-only** — no logging lines added or changed in diff.)*

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.read-current | A | | Admin token paths use `get_candidate` → operative current overlay before `build_candidate_token_view` |
| astral.dispatch.entity-state-bound | A | | Evaluation remains per dispatch row `candidate_id`; blank/missing candidate still fail-closed |
| stat.logging.info.api | A | | (id-only) No new route/info spam |
| stat.logging.warning | A | | (id-only) Existing warning paths on blank/miss candidate unchanged |
| stat.logging.error | A | | (id-only) `logger.exception` fail-closed path unchanged |

## Column diff vs plan stage

(aligned) — No `validate-plan` fix-mode per-id table for AST-1854. Fix-board Joan `[board-joan] CANON: OK` triage matches code review on the two substantive ids above; no Joan-high / Radia-low divergence.

## Frame diff

(none)

## Findings

### discuss — Canon Scope missing on ticket (process)

- **Severity:** discuss  
- **Location:** Linear Description vs fix-lane Radia comparability  
- **Finding:** No `Canon Scope (frozen at plan)` block on AST-1854; scored Joan fix-board overlap only (AST-1847 / AST-1821 precedent).  
- **Recommendation:** Archie may add a frozen list for future fix bugs; not a product defect on this tip.  
- **Default:** Ship on overlap triage; no engineer recall for Description alone.

### discuss — Test coverage deferred to AST-1855

- **Severity:** discuss  
- **Location:** `[board-betty] TESTS: REVISE` / spawn handoff  
- **Finding:** No hydrated-view `[bug-repro]` on this tip; sibling AST-1855 owns artifact-only Ideal Day gate assertions + contrasts.  
- **Recommendation:** Not **fix-now** on Hedy’s product patch; UAT should still exercise somerset / `craft_do_rubric` per parent AST-1852 To-be.  
- **Default:** Merge product after PROCEED; land tests via AST-1855 before treating repro-first bar closed.

### advisory — Agent preview still raw loader (approved out of scope)

- **Severity:** advisory  
- **Location:** `_resolve_agent_preview_candidate` (~L175) — still `database.get_candidate`  
- **Finding:** Same divergence class as pre-fix empty-render; explicitly out of Susan-approved scope.  
- **Recommendation:** Separate ticket if UAT wants preview parity; do not expand AST-1854.

### advisory — Legacy blob-only `base_resume` in admin

- **Severity:** advisory  
- **Location:** Full `get_candidate` overlay (all nine `hydrate_operative_*`), not Ideal Day alone  
- **Finding:** Legacy-only `base_resume` blob without artifact row can read blank in admin after this fix — **same as runtime** (`hydrate_operative_base_resume_for_response` strips stale blob on miss). Susan flagged as known behavior to weigh, not a scope change.  
- **Recommendation:** UAT awareness only; aligns with plan ⚠️ Decision (“all migrated context artifacts the hydrated loader overlays”).

### advisory — Pre-existing `test_api_admin.py` failures

- **Severity:** advisory  
- **Location:** Hedy `test-fix` comment — 5 failures identical on `origin/dev`  
- **Finding:** Not introduced by AST-1854; not a Radia block on this diff.

## What's solid

- Diff matches plan-fix **Proposed change** exactly: one import name + three `database.get_candidate` → `get_candidate` swaps in `_evaluate_dispatch_empty_render`, `_enrich_tasks`, `_resolve_adhoc`; no caps, caches, or new helpers.  
- Hydration stays **outside** the `try` in `_evaluate_dispatch_empty_render` per plan decision (fail-closed semantics preserved vs AST-1780).  
- Scope gate honored: no `config.py`, `candidate.py`, `agent.py`, or React edits.  
- Estimate **2** fits the footprint.  
- Converges admin list/gate/Task Manager/ad hoc with runtime token view — addresses UAT somerset / `IDEAL_DAY` root cause from plan § Root cause.

## Recommended actions (Chuckles — read-only for Radia)

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** | **Normal** — AST-1852 mini-parent with `origin/ftr/AST-1852-dispatch-gate-hydrated-candidate` (not Done-orphan / not straight-to-dev) | Append artifact → `docs(AST-1854): Radia review — clean` on publish ref → post slim upshot `--as radia` → **Review Posted** → `do-all-the-things` §3h clean-review shortcut → **User Testing** (`resolve-child` skipped). |

1. Do **not** block product on AST-1855 test gap (parallel to AST-1791 / AST-1792).  
2. Track AST-1855 for `[bug-repro]` / bible REVISE closure.  
3. Optional follow-up ticket for `_resolve_agent_preview_candidate` only if Susan wants preview parity.

context_tokens≈9500

---

**Slim upshot (Chuckles → `linear_proxy --as radia save-comment`):**

```
[code-rubric] PROCEED (Commit: b5a72977) Three hydrated loader swaps clean
```

#### Chuckles disposition (AST-1854)

Clean review: Review Posted → User Testing via the clean-review shortcut (resolve-child skipped). Merged into the mini-parent ftr.

Docs-acceptance on this tip: no test-tree delivery here — tests and bible land on gap sibling AST-1855.

## Bug: AST-1855 — Gap: artifact-only Ideal Day repro for the dispatch empty-render gate

Gap child of AST-1852 from `[board-betty] TESTS: REVISE` on AST-1854. Scope is **test + bible only** (this ticket's `## Scope`): `tests/component/ui/api/test_api_admin.py`, `docs/test-bible/ui/api/api_admin.md`. Product loader swap is sibling **AST-1854** (`api_admin.py`, `origin/sub/AST-1852/AST-1854-dispatch-gate-hydrated-candidate` @ `b5a72977`); do not re-plan or re-implement it here. This gap ref carries AST-1854's plan doc commits only (`sync(AST-1855)` absorb of `b01b1ce8`) — **not** its product commit — so the gap tip stays test-tree only and its own `api_admin.py` is the pre-fix product.

### As-is

Every empty-render test either monkeypatches `_evaluate_dispatch_empty_render` (`TestAst1780EmptyRenderListGatesForceOff`) or stubs raw `admin_mod.database.get_candidate` **and** `admin_mod.build_candidate_token_view` (`TestAst1791NoPromptValueErrorEmptyRender._stub_no_agent_task_prompts`). None drives the real loader → artifact overlay → token view → `empty_render_for_prompts` chain, so reverting AST-1854 to the raw `database.get_candidate` read would leave the suite green. Bible §§ AST-1780 / AST-1792 / AST-1795 have no node for an artifact-only context value.

### To-be

A three-candidate `[bug-repro]` class drives `_evaluate_dispatch_empty_render` through the real hydrated loader, with only the DB edges stubbed: `c1` (Ideal Day only in artifacts) → `empty_render: False` — **red** on pre-fix product (gap tip / `origin/ftr/AST-1852-dispatch-gate-hydrated-candidate` `api_admin.py`), **green** on `b5a72977`; `c2` (no artifact, no legacy blob) → `empty_render: True`, `empty_tokens == ["IDEAL_DAY"]`; `c3` (legacy `context.ideal_day` only) → `empty_render: False`. The existing `admin_mod.database.get_candidate` stubs stay green on `b5a72977`.

### Repro

1. Pre-fix product (`api_admin.py` as on this gap tip): `_evaluate_dispatch_empty_render("c1", "craft_do_rubric")` with `database.get_candidate("c1")` → row whose `candidate_data.context` has no `ideal_day`, `database.get_current_artifact("candidate", "c1", "ideal_day")` → `{"artifact_data": "Deep work mornings, collaborative afternoons."}`, prompt texts `["Ideal day: {$IDEAL_DAY}"]` → returns `{"empty_render": True, "empty_tokens": ["IDEAL_DAY"]}` (raw row, no overlay — `get_current_artifact` is never called).
2. Same stubs on `b5a72977` → `{"empty_render": False, "empty_tokens": []}` (hydrated loader overlays the artifact onto `context.ideal_day`).
3. `c2` / `c3` return the same values on both trees (contrasts — they pin that the fix neither blanks a legacy blob nor fills a truly empty Ideal Day).

### Root cause

AST-1780 QA stubbed the evaluate helper (wiring only); AST-1792/1795 stubbed the raw loader **and** the token view to isolate the ValueError soft-miss. No test left the loader + `build_candidate_token_view` + `resolve_tokens` chain real, so the raw-vs-hydrated read (AST-1854's defect) was invisible to the suite.

### Proposed change

**Files only (Scope gate):**

| File | Change |
|------|--------|
| `tests/component/ui/api/test_api_admin.py` | New class `TestAst1854HydratedCandidateEmptyRender` directly after `TestAst1791NoPromptValueErrorEmptyRender`; existing tests edited only per step 3's red rule |
| `docs/test-bible/ui/api/api_admin.md` | New § AST-1855 under the AST-1780 empty-render cluster (after § AST-1795) |

**Do not edit** `src/ui/api/api_admin.py`, `src/core/candidate.py`, or `src/utils/config.py` — AST-1854 owns product.

1. **Class + stub helper** — `TestAst1854HydratedCandidateEmptyRender`, docstring `"""AST-1855 / AST-1854: dispatch empty-render reads the hydrated candidate (artifact overlay), no eval / loader / token-view monkeypatch."""`. Static helper `_stub_hydrated_candidates(monkeypatch)`:

   - `admin_mod.database.get_candidate` → `lambda cid: _rows()[cid]` where `_rows()` builds **fresh** dicts per call (the hydrated loader mutates `candidate_data` in place), keyed by id:

     ```python
     {
         "c1": {"astral_candidate_id": "c1", "first": "Ada", "last": "Lovelace",
                "candidate_data": {"context": {}}},
         "c2": {"astral_candidate_id": "c2", "first": "Bea", "last": "Blank",
                "candidate_data": {"context": {}}},
         "c3": {"astral_candidate_id": "c3", "first": "Cy", "last": "Legacy",
                "candidate_data": {"context": {"ideal_day": "Legacy blob ideal day."}}},
     }
     ```

   - `admin_mod.database.get_current_artifact` → `lambda entity_type, entity_id, artifact_type: {"artifact_data": "Deep work mornings, collaborative afternoons."} if (entity_id, artifact_type) == ("c1", "ideal_day") else None`. Patching the attribute on `admin_mod.database` patches `src.data.database` itself, which `src.core.candidate.get_candidate_current` also calls — so this one stub answers all nine `hydrate_operative_*` reads hermetically (no repo `data/astral.db` access).
   - `admin_mod._dispatch_empty_render_prompt_texts` → `lambda tk: ["Ideal day: {$IDEAL_DAY}"]` (single candidate-scoped token, so `empty_tokens` is exactly `["IDEAL_DAY"]` when blank).
   - **Must not** monkeypatch: `admin_mod.get_candidate`, `admin_mod.build_candidate_token_view`, any `hydrate_operative_*`, `get_candidate_current`, `empty_render_for_prompts`, `resolve_tokens`, `_evaluate_dispatch_empty_render`, `_candidate_dispatch_empty_render_error`. Stubbing any of these hides the defect.

2. **Three test methods** (separate methods, not parametrize — keeps the `[bug-repro]` node id stable and distinct from its contrasts, same precedent as AST-1795):

   - `test_evaluate_artifact_only_ideal_day_empty_render_false` — `# [bug-repro] red on pre-AST-1854 (raw row → IDEAL_DAY blank); green after hydrated loader.` Assert `admin_mod._evaluate_dispatch_empty_render("c1", "craft_do_rubric") == {"empty_render": False, "empty_tokens": []}` and `admin_mod._candidate_dispatch_empty_render_error("c1", "craft_do_rubric") is None`.
   - `test_evaluate_no_ideal_day_anywhere_empty_render_true` — assert `_evaluate_dispatch_empty_render("c2", "craft_do_rubric") == {"empty_render": True, "empty_tokens": ["IDEAL_DAY"]}` and `"IDEAL_DAY" in _candidate_dispatch_empty_render_error("c2", "craft_do_rubric")`.
   - `test_evaluate_legacy_blob_ideal_day_empty_render_false` — assert `_evaluate_dispatch_empty_render("c3", "craft_do_rubric") == {"empty_render": False, "empty_tokens": []}`.

   Red/green gate for qa-fix: node 1 **fails** with this gap tip's own `api_admin.py` (pre-fix, = `origin/ftr/AST-1852-dispatch-gate-hydrated-candidate`) and **passes** with `b5a72977`'s `api_admin.py`; nodes 2–3 pass on both.

3. **Existing `admin_mod.database.get_candidate` stubs — run, don't pre-edit.** Classification on `b5a72977`:

   - **Unaffected (stub returns `None` → hydrated loader returns before any artifact read, or the call site stays raw):** `TestAdminConfigAndAgents` agent-preview stubs (~lines 177, 190 — `_resolve_agent_preview_candidate` stays raw per AST-1854 scope), `TestEnrichTasks` `None` stubs (~290, 317, 339), `TestBackfillAndCandidateKey` api-key stubs (~1745–1749 — `_candidate_dispatch_api_key_error` stays raw), `TestApiAdminBranchGaps` (~1792, ~1942), `TestAst1412EnrichTaskLens` (~3289).
   - **Now reach hydrate reads (row-returning stub on a swapped path):** `TestEnrichTasks::test_enrich_tasks_covers_agent_and_cache_branches` (~243), `TestAdhocHelpers::test_adhoc_entities_and_resolve` (~1481), `TestAdhocHelpers::test_resolve_adhoc_job_entity_resolves_visible_jd_token` (~1496), and the four `TestAst1791NoPromptValueErrorEmptyRender` tests via `_stub_no_agent_task_prompts` (~3834). None of these fixtures carry `artifacts.base_resume` or any context leaf their assertions depend on, so they are expected green.
   - Run the whole module on `b5a72977` product. Edit an existing test **only if it goes red**, and then only by adding `monkeypatch.setattr(admin_mod.database, "get_current_artifact", lambda *a: None)` to that test (or to `_stub_no_agent_task_prompts`). No other changes to existing cases.

4. **Bible** (`docs/test-bible/ui/api/api_admin.md`, new § AST-1855 after § AST-1795):
   - Table rows for the three node ids; `[bug-repro]` tag on `test_evaluate_artifact_only_ideal_day_empty_render_false` only.
   - One-line note: AST-1854 — dispatch empty-render loads the hydrated candidate (operative artifact overlay); only `database.get_candidate` / `database.get_current_artifact` / prompt texts stubbed.
   - QA manifest: the three new nodes + the seven row-returning existing tests from step 3 (re-run guard).
   - Keep § AST-1780 / AST-1792 / AST-1795 rows unchanged. **Integration:** none.

5. **Implementer lane:** Betty lands tests + bible on `astral-tests` and publishes to `origin/sub/AST-1852/AST-1855-dispatch-gate-hydrated-candidate-tests` per qa-fix. Engineers do not edit `tests/` or `docs/test-bible/**`.

⚠️ **Decision:** Stub at the DB edges (`database.get_candidate`, `database.get_current_artifact`) rather than seeding `sqlite_in_memory` artifact rows — keeps the full product chain (hydrated loader → `hydrate_operative_*` → `build_candidate_token_view` → `resolve_tokens` → `empty_render_for_prompts`) real while staying hermetic and independent of artifact-save helpers.

⚠️ **Decision:** One `_evaluate_dispatch_empty_render` repro is the gate (Betty's board note) — `_enrich_tasks` / `_resolve_adhoc` share the same one-token loader swap; no separate repro nodes for them.

### Blast radius

- **Hermeticity (discuss):** `tests/component/ui/conftest.py` DB isolation (`sqlite_in_memory` / `seeded_db`) is opt-in and `tests/conftest.py` defaults `ASTRAL_DB_DIR` to the repo `data/`. On `b5a72977`, the seven row-returning tests in step 3 now call `database.get_current_artifact` against that default DB (nine reads per load). Expected green (fixture ids like `c1` have no rows), but non-hermetic; step 3 stubs only on red, per Scope ("existing cases change only if needed"). Susan may prefer the `get_current_artifact → None` stub on all seven regardless.
- **Legacy base resume (discuss, AST-1854 product — not this gap):** `hydrate_operative_base_resume_for_response` **pops** legacy `artifacts.base_resume` on artifact miss (AST-1659 blob retirement), unlike the context leaves, which keep the legacy blob. So on `b5a72977` a candidate with only a legacy `base_resume` blob now reads blank in the admin gate / Task Manager / ad hoc — matching runtime (`agent.py` already hydrates), but narrower than AST-1854's "legacy-blob-only candidates still resolve" line, which holds for Ideal Day (and the other context leaves) only. No test in this gap asserts base-resume behavior.
- New class is additive; `TestAst1780…` / `TestAst1791…` intent unchanged.
- Sibling AST-1854 product must be on the line under test for green; merge-child order AST-1854 → AST-1855.

### What must still hold

- Blank / missing `candidate_id` and candidate miss → `empty_render: True` (AST-1780 / AST-1791) — covered by existing product; not re-asserted here.
- Prompt-load `ValueError` → silent `empty_render: False` (AST-1791 / AST-1794) — `TestAst1791…` stays green.
- Truly blank candidate-scoped token → `empty_render: True` with the token named (node 2).
- Legacy `context.ideal_day` blob still resolves (node 3).
- `entity_contexts=None`; no second list boolean; no product `src/` edits on this tip; no invented integration tier.

## Joan fix-board — AST-1855

Fix-board Joan pass on **AST-1855** (test + bible gap only; product stays on sibling AST-1854). Joan’s single question is whether the plan-fix **requires or conflicts with** in-force canon. This patch adds component tests and bible rows that exercise the real hydrated-loader → token-view → `empty_render_for_prompts` chain via DB-edge stubs only; it does not edit `src/`, statutes, or patterns. The asserted outcomes (artifact-only Ideal Day passes, truly blank fails, legacy blob passes) match `patt.artifact.read-current` / migration intent, not a new exception. Blast-radius discuss items (hermetic `get_current_artifact`, base-resume pop vs AST-1854 wording) are product/UAT scope on AST-1854, not canon edits this gap must land.

BEGIN-VERDICT

[board-joan]  CANON: OK

END-VERDICT

```text
AST-1855 board-joan done — CANON: OK.
```

## Radia review — AST-1855

[code-rubric]

**Ticket:** AST-1855  
**Publish ref:** `4bbeabff46cbc6bc51db807b81bdeb7ad12a5a9f` (`origin/sub/AST-1852/AST-1855-dispatch-gate-hydrated-candidate-tests`)  
**Diff base:** `origin/ftr/AST-1852-dispatch-gate-hydrated-candidate` @ `ac9c93b6` (AST-1854 product already on ftr) → gap delta: issue doc + bible + `test_api_admin.py` only — **no `src/**`**  
**Corpus:** `bd68954dc854ca80fca1fc391821dff9ff288a7a` (canon tree at publish ref)  
**Overall:** CLEAN  

**Status gate:** `Tests Passed` / Hedy — trusted.

## Fix-specific checks

**[bug-repro] OK** — `TestAst1854HydratedCandidateEmptyRender::test_evaluate_artifact_only_ideal_day_empty_render_false` is tagged and pins **concrete To-be** from plan § Repro / AST-1854:

- Asserts `{"empty_render": False, "empty_tokens": []}` and `_candidate_dispatch_empty_render_error(...) is None` for `c1` with **empty** `context` but `get_current_artifact("candidate", "c1", "ideal_day")` returning operative body.
- **Not tautological:** leaves `admin_mod.get_candidate` (core hydrated loader), all `hydrate_operative_*`, `build_candidate_token_view`, `resolve_tokens`, and `empty_render_for_prompts` **unstubbed**; only DB edges + `_dispatch_empty_render_prompt_texts` (same isolation pattern as AST-1792/1795).
- **Plausibly red pre-fix:** on raw `database.get_candidate` path, `get_current_artifact` is never consulted → `{$IDEAL_DAY}` blank → `True` / `["IDEAL_DAY"]` (Betty `@ 6c083f3c` red at `3dd7f249`; Hedy red→green at `4bbeabff`; matches plan red/green gate).
- **Contrast nodes** `c2` / `c3` lock blank vs legacy-blob behavior so the repro is not “always false.”

**## What must still hold — OK** (plan-fix § AST-1855):

| Item | Verdict |
|------|---------|
| Truly blank token → `True` + token named | `test_evaluate_no_ideal_day_anywhere_empty_render_true` |
| Legacy `context.ideal_day` → `False` | `test_evaluate_legacy_blob_ideal_day_empty_render_false` |
| AST-1791 soft-miss path stays green | Four `get_current_artifact → None` additions in `_stub_no_agent_task_prompts` / related |
| No product `src/` on this diff | Confirmed (`--name-only` = docs + tests only) |
| No integration invented | Bible § AST-1855 says none |

## Canon scores

*(Frozen **Canon Scope** on Linear AST-1855: **none** — test/bible gap; scored fix-board Joan overlap.)*

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.read-current | A | | Repro asserts artifact-table Ideal Day flows through real hydrate → gate pass |
| astral.dispatch.entity-state-bound | A | | Per-candidate `c1`/`c2`/`c3` eval; no cross-candidate pooling in tests |

## Column diff vs plan stage

(aligned) — Fix-board Joan `[board-joan] CANON: OK`; no validate-plan per-id table. Betty’s REVISE ask (stub all seven row-returning paths with `get_current_artifact → None`) is **implemented** in diff — not a Radia/engineer gap.

## Frame diff

(none)

## Findings

### advisory — sibling test carry: `TestAst1830SweepHrsAdminApi`

- **Severity:** advisory  
- **Location:** `test_api_admin.py` diff (~19 cases), `merge-tests`  
- **Finding:** AST-1830 Done on `origin/dev`; not AST-1855 scope. `skipif(not hasattr(admin_mod, "_parse_sweep_hrs"))` limits blast on older tips. Hedy attribution comment matches spawn prompt.  
- **Recommendation:** Do not score as cross-ticket **fix-now**; no Radia action.

### advisory — Bible sequencing line vs current ftr

- **Severity:** advisory  
- **Location:** `docs/test-bible/ui/api/api_admin.md` § AST-1855 — “product not on ftr yet”  
- **Finding:** `origin/ftr/AST-1852…` @ `ac9c93b6` now includes AST-1854 product; pass criterion (“green with AST-1854 on tree”) is satisfied on ftr+sub merge. Wording is slightly stale, not a test defect.  
- **Recommendation:** Optional docs tidy in docs-acceptance; not **fix-now** for `resolve-child`.

### advisory — Pre-existing module failures

- **Severity:** advisory  
- **Location:** Hedy test-fix — 5 failures identical on `origin/dev`  
- **Finding:** Outside AST-1855 manifest; unchanged.

### discuss — Canon Scope missing (process)

- **Severity:** discuss  
- **Finding:** No frozen list on Linear; Joan overlap scored only.  
- **Default:** Ship; Archie may add list for comparability later.

## What's solid

- Delivers exactly what `[board-betty] TESTS: REVISE` on AST-1854 asked for: real hydrated-loader chain, three candidates, bible § AST-1855 + manifest (10/10 per Hedy).  
- Hermeticity: proactive `get_current_artifact` stubs on the seven row-returning swapped-path tests (Betty board call) — avoids env-dependent greens against repo `data/astral.db`.  
- Closes repro-first bar for AST-1854 board REVISE when merged onto ftr that already carries `b5a72977`/`ac9c93b6` product.  
- Estimate **2** fits.

## Recommended actions (Chuckles)

| Gate | Parent shape | Next action |
|------|--------------|-------------|
| **PROCEED** | Normal — AST-1852 + `ftr/AST-1852-dispatch-gate-hydrated-candidate` | Append artifact → `docs(AST-1855): Radia review — clean` → post slim upshot `--as radia` → **Review Posted** → §3h clean-review → **User Testing** (`resolve-child` skipped). Merge gap sub onto ftr after UT if not already stacked. |

context_tokens≈7200

---

**Slim upshot (Chuckles → `linear_proxy --as radia save-comment`):**

```
[code-rubric] PROCEED (Commit: 4bbeabff) Bug-repro pins hydrated gate
```

#### Chuckles disposition (AST-1855)

Clean review (discuss items only, default ship): Review Posted → User Testing via the clean-review shortcut (resolve-child skipped). AST-1854's product fix is on ftr @ ac9c93b6, so the tests run green on ftr without a scratch overlay.

## Bug: AST-2091 — Block Auto/Run on duplicate or empty rubric

`fix` child of orphaned mini-parent bug AST-2013 (`ftr/AST-2013-rubric-dup-dispatch-gate`, fresh off `origin/dev`). Extends this doc's Stage 1 (list enrichment + force AUTO off) and Stage 2 (AUTO-on / Run 400 gates) with one more reason source, the same way AST-1880 added the missing-API-key reason. Scope is this ticket's `## Scope` (copied verbatim from AST-2013): `src/core/candidate.py`, `src/ui/api/api_admin.py`, `src/core/dispatcher.py`; `AdminScheduledActions.tsx` unchanged. No Canon Scope on the ticket or parent — ids stay unresolved; flag for the board, not a blocker for this plan.

### As-is

A Scheduled Actions row is Invalid only for empty prompt tokens (AST-1780 / AST-1819) or a missing platform API key (AST-1880). Nothing checks the rubric behind a scored task. Somerset's `do_rubric` has two current `TP` rows, both labelled `Hands-On Technical Partnership With Engineers`, so `meteorite_grade_do` shows as valid, AUTO stays on, and the job runs. `_vector_labels_map` (`consult.py`) logs `duplicate rubric codes: TP→[…]` and keeps the first. Both grading runs for job `bf81c81e-15e7-4ef2-b61b-e6181a9b8891` came back all `X`, and the AST-1760 guard sent the job to `METEORITE_FAILED_TECHNICAL_DO` (batch `meteorite_grade_do-78b67658-…`, `error:1`). Separately, `dispatcher.run_task` has no validation gate at all. The tick loop keeps spawning an AUTO row until someone loads Scheduled Actions and the list enrichment turns AUTO off.

### To-be

A rubric-backed row (its `task_key`'s `TASK_CONFIG` entry names a `rubric_artifact`) is **Invalid** when the candidate's current rubric for that artifact has **duplicate vector codes** (same code after `strip().upper()`) or is **empty** (zero current criteria). An Invalid row behaves exactly like an empty-token row:

- `empty_render: true`, and the reason is in `invalid_reason`, so AUTO and Run/Sweep are disabled and the tooltip names the problem.
- AUTO-on create and update return 400, and so does Run.
- An AUTO-on row is forced off on list load with a warning.
- `run_task` refuses to start the job and also forces AUTO off, so the scheduler stops without a page load.

Re-saving the rubric runs AST-2008's uptick (`TP` → `TX`), and the row is valid again on the next list load.

### Repro

Fixture: astral persistence is file/JSON, so the repro is a stubbed rubric read, not a seeded DB row. Stub `src.data.database.list_rubric_vectors(candidate_id, owner_task_key, current_only=True)` so that `("somerset", "grade_do")` returns:

```python
[
    {"code": "TP", "label": "Hands-On Technical Partnership With Engineers", "content": "…", "importance": 8},
    {"code": "TP", "label": "Hands-On Technical Partnership With Engineers", "content": "…", "importance": 8},
    {"code": "SA", "label": "Systems Architecture", "content": "…", "importance": 7},
]
```

and `("empty_cand", "grade_do")` returns `[]`. A dispatch row has `candidate_id="somerset"`, `task_key="meteorite_grade_do"`, `auto_mode=1`, and a valid key and tokens.

1. `GET /api/admin/dispatch_tasks`. Today the row has `empty_render: false`, `invalid_reason: ""`, and `auto_mode: 1`. After the fix it has `empty_render: true`, `invalid_reason: "Rubric 'do_rubric' has duplicate vector codes: TP"`, and `auto_mode: 0` (persisted).
2. `POST /api/admin/dispatch_tasks/<id>/run`. Today it returns 200 `{"started": true}`. After the fix it returns 400 `{"error": "Rubric 'do_rubric' has duplicate vector codes: TP", "started": false}`.
3. `dispatcher.run_task(<id>)` with `auto_mode=1`. Today it returns `True` and spawns the thread. After the fix it returns `False`, spawns no thread, and calls `update_dispatch_task(<id>, auto_mode=0)`.
4. The same row with `candidate_id="empty_cand"` follows steps 1–3 with the reason `Rubric 'do_rubric' is empty for this candidate.`

### Root cause

The dispatch validity gate (AST-1766 / AST-1780 / AST-1880) only checks prompt rendering and the platform key. The rubric's integrity is never part of "executable". The only duplicate-code handling is AST-1513's first-wins warning at decode time, which is too late, and AST-2008's uptick, which runs on save and doesn't repair rows already stored. `dispatcher.run_task`, the scheduler's spawn point, delegates all validity to the admin list, so a stored bad rubric keeps sweeping on AUTO.

### Proposed change

1. **`src/core/candidate.py`: new `rubric_dispatch_error(candidate_id, task_key) -> Optional[str]`**, placed directly after `rubric_criteria_for_task` (which it calls). It is a pure read with no writes. `TASK_CONFIG` and `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY` are already imported here.
   - `rk = (TASK_CONFIG.get((task_key or "").strip()) or {}).get("rubric_artifact")` and `owner = RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY.get(rk) if rk else None`. This resolves aliases the same way `consult._rubric_criteria_for_cfg` does: `meteorite_grade_do` → `do_rubric` → `grade_do`, `meteorite_like` → `like_rubric` → `grade_like`.
   - ⚠️ **Do not** use `config.rubric_owner_task_key()`. It also maps `craft_*_rubric` tasks to owners, and gating a craft task on an empty rubric would block the very task that creates the rubric. No `craft_*` key carries `rubric_artifact`, which I verified against `TASK_CONFIG` on this tip: the rubric-backed keys are `prefilter_company`, `qualify_job_listings`, `evaluate_jd`, `evaluate_meteorite`, `grade_do`, `grade_get`, `grade_like`, `meteorite_grade_do`, `meteorite_grade_get`, and `meteorite_like`.
   - Return `None` when `owner` is falsy (the task isn't rubric-backed) or `str(candidate_id or "").strip()` is blank. A blank candidate already fails `_candidate_dispatch_api_key_error`, so this helper doesn't duplicate that reason.
   - `criteria = rubric_criteria_for_task(cid, owner)`. This is the same list consult grades with, including the embedded QC/GC/RC merges, so evaluate/prefilter rubrics are never empty.
   - Empty (`not criteria`) → `f"Rubric '{rk}' is empty for this candidate."`
   - Duplicates: count `str(c.get("code") or "").strip().upper()` over dict items, skipping blank codes (sync assigns `V{idx}` to those, matching the uptick's blank-code rule). If any code appears more than once → `f"Rubric '{rk}' has duplicate vector codes: {', '.join(sorted(dupes))}"`. The codes are upper-cased and comma-separated, which is the ticket's tooltip example.
   - Otherwise return `None`.

2. **`src/ui/api/api_admin.py`: add `rubric_dispatch_error` to the existing `from src.core.candidate import (…)` block.**
   - **`list_dtasks`** (the AST-1780 block after `key_err`):
     - `rubric_err = rubric_dispatch_error(row.get("candidate_id"), row.get("task_key") or "")`.
     - `row["empty_render"] = bool(er.get("empty_render")) or bool(key_err) or bool(rubric_err)`.
     - `row["invalid_reason"] = key_err or rubric_err or ""`.
     - In the force-off branch, `why = key_err or rubric_err or (<existing tokens text>)`.
     - The precedence is key, then rubric, then tokens. This keeps AST-1880's key-first rule, and the tooltip (`invalid_reason || tokens`) shows the rubric reason ahead of the token list. `empty_tokens` is unchanged.
   - **`create_dtask`** (the `auto_mode` branch): after the `_candidate_dispatch_api_key_error` check and before `_candidate_dispatch_empty_render_error`, add `err = rubric_dispatch_error(data.get("candidate_id"), task_key)` and return `jsonify({"error": err}), 400` if it's set.
   - **`update_dtask`** (the `updates.get("auto_mode") == 1` branch): add the same check at the same position, using `rubric_dispatch_error(cid, effective_task_key)`.
   - **`run_dtask`**: add the same check at the same position (after the key check, before empty-render), returning `jsonify({"error": err, "started": False}), 400`.

3. **`src/core/dispatcher.py`, `run_task`**: right after `if not task: return False` and before the `available_count` enrichment, add:

   ```python
   # late: avoid cycle with candidate → dispatcher (module-top import)
   from src.core.candidate import rubric_dispatch_error
   rubric_err = rubric_dispatch_error(task.get("candidate_id"), task.get("task_key") or "")
   if rubric_err:
       forced = bool(task.get("auto_mode"))
       if forced:
           _db_update_dispatch_task(task_id, auto_mode=0)
       logger.warning(
           "%s | dispatch_task id=%s task_key=%r %s — not started%s",
           task.get("candidate_id") or "-", task_id, task.get("task_key"), rubric_err,
           ", AUTO forced off" if forced else "",
       )
       return False
   ```

   - This applies to both callers: the tick loop (`_tick_loop` → `run_task`) and admin Run. Admin Run already returns 400 earlier, so the second check there is redundant but harmless.
   - The late import follows the existing `_tick_loop` precedent, because `candidate.py` imports `dispatcher` at module top.
   - It is only a rubric gate. Do **not** move the key or empty-render checks into `run_task`; that is outside this ticket's scope.

4. **`AdminScheduledActions.tsx`: no change.** It already disables on `empty_render` and shows `invalid_reason` first.

5. **Data (staging, not code):** after deploy, re-save somerset's Do rubric in Artifacts. AST-2008 renames the duplicate `TP` → `TX` and retires the extra row. Then re-run `meteorite_grade_do` for `bf81c81e…` from `METEORITE_PASSED_JD`.

⚠️ **Decision:** "Empty" means `rubric_criteria_for_task` returns `[]`, which is the list grading uses after the embedded merges. It is not the raw `rubric_vector` row count.

⚠️ **Decision:** The duplicate check keys on code only, not code plus label. `_vector_labels_map` also needs a label to count a pair, but a duplicate code with a blank label is still a broken rubric, so code only is a superset of what decode warns on.

⚠️ **Decision:** No try/except around the rubric read in `list_dtasks`, which matches `_candidate_dispatch_api_key_error`. No caching of the per-row read either: optimizations need Susan's sign-off.

### Blast radius

- **Live AUTO rows (production behavior):** on the first list load or scheduler tick after deploy, every AUTO row on a rubric-backed task whose candidate has an empty rubric (`qualify_job_listings`, `grade_*`, `meteorite_grade_*`, `meteorite_like`) or a duplicate-code rubric is forced off with a warning. That is intended, but Susan should expect AUTO to flip off on more than somerset's `meteorite_grade_do`.
- **`list_dtasks` cost:** one extra `list_rubric_vectors` read per rubric-backed row per list load, on top of the existing per-row empty-render and key reads.
- **Tests (Betty, fix-board):** `tests/component/ui/api/test_api_admin.py` (115 references to rubric-backed task keys) and `tests/component/core/test_dispatcher.py` (128) build rows on those keys. Any case that puts AUTO on, runs the row, lists rows with AUTO on, or calls `run_task` without a seeded rubric will now see Invalid, 400, or `False` and go red. Those cases need `rubric_dispatch_error` stubbed to `None` (`admin_mod.rubric_dispatch_error`, plus `src.core.candidate.rubric_dispatch_error` for the late import in `dispatcher`) or a seeded rubric. Betty owns that call; engineers do not edit `tests/`.
- **Shared reads:** `rubric_criteria_for_task` is unchanged. Consult, hydrate, and token resolution see no difference.
- **Sibling paths not gated:** craft tasks, non-rubric tasks, and mailbox Avail rows (`_meteorite_email_due_tasks`) all get `None`, so they behave exactly as before.

### What must still hold

- **AST-2008:** `_uptick_duplicate_rubric_codes` and `apply_rubric_vectors_save` are unchanged. A re-save still repairs duplicates, and the row turns valid on the next list load.
- **AST-1513:** `_vector_labels_map` keeps its first-wins decode and its `duplicate rubric codes` warning. The helper does not call it or change it.
- **AST-1760:** all-X routing and the `_render_score` math are untouched.
- **AST-1791 / AST-1794:** a task with no agent prompts is still a silent `empty_render: False` soft-miss from `_evaluate_dispatch_empty_render`. The rubric reason is a separate source and only fires for rubric-backed tasks.
- **AST-1880:** a missing key still wins `invalid_reason` and is the first 400 on create, update, and Run.
- **AST-1819:** `empty_tokens` is unchanged, so the token tooltip still shows when no key or rubric reason applies.
- **No new response fields, tables, job states, or `TASK_CONFIG` keys** (Technical scope).

### Joan fix-board (AST-2091)

```
[board-joan]  CANON: OK
```

**Reasoning:** Read the `## Bug: AST-2091` plan-fix block (gates via `rubric_dispatch_error`, same shape as AST-1780 / AST-1880: `empty_render` + `invalid_reason`, key-first 400s, list force-off, plus `run_task` refuse + AUTO off). No Canon Scope on the ticket; roster skim used `canon/statutes/README.md` and paths touched (`api_admin.py`, `candidate.py`, `dispatcher.py`).

Overlapping in-force scoped statutes do not need edits:

- **`astral.dispatch.entity-state-bound`** — Still per-row `candidate_id` / task_key evaluation; no fake entity pairs or catalog override.
- **`astral.agent.grade-vector-validation`** — `do_task` response vectors; not rubric row integrity before dispatch.
- **`astral.dispatch.seed-auto-false`** — Forcing AUTO off on bad rubrics is operator/runtime behavior, not seed inserting AUTO true.
- **`astral.layers.import-direction`** — Late `candidate` import inside `run_task` breaks an existing `candidate`→`dispatcher` cycle (same class as prior dispatch patterns); not the utils→data late-import carve-out.
- **Logging** — `logger.warning` on scheduler skip matches dispatcher skip semantics; no new route `info` spam.

AST-1513 first-wins decode and AST-2008 save uptick stay untouched; no active statute says duplicate/empty rubrics must remain AUTO-runnable. Plan ⚠️ decisions (empty = `rubric_criteria_for_task`, code-only dupes) are product choices in the doc, not ambiguous canon intent — **ESCALATE** not warranted.

Optional F3 note only: if Susan later wants this gate written into corpus law, that would be new scoped statute authoring (Archie), not required because this plan contradicts existing statutes.

```text
AST-2091 board-joan done — CANON: OK.
```

context_tokens≈18500

### Radia review-fix (AST-2091)

[code-rubric]

**Ticket:** AST-2091  
**Publish ref:** `origin/sub/AST-2013/AST-2091-rubric-dup-dispatch-gate` @ `64bcc193539e35a7789ec2c030107abe805f4b48`  
**Diff base:** `origin/ftr/AST-2013-rubric-dup-dispatch-gate` @ `823d376050014ec3899fa14eee376c75008691e8` (merge-base = ftr tip)  
**Corpus:** `2d1b73da19cf1d14276e5c26f52b37aa8047d159`  
**Overall:** CLEAN  

## Canon scores

Frozen list **empty** (AST-2091 description has no **Citations:** / Canon Scope; parent AST-2013 same — locked at Discussion). No directive rows to score; not a §5.3 ESCALATE (Joan fix-board `[board-joan] CANON: OK` roster skim; plan does not contradict in-force scoped statutes).

## Column diff vs plan stage

`no plan-stage scores attached` — Joan fix-board only (no `validate-plan` canon table for this bug).

## Frame diff

(none)

## Fix-specific checks

**[bug-repro] OK** — Betty’s F4 bar cleared (`test(AST-2091)` @ `f00854439`, merge-tests @ `2d6cd8eea`). Assertions pin plan **To-be** strings and behavior, not tautologies:

- `TestAst2091RubricDispatchError` — exact reasons (`Rubric 'do_rubric' has duplicate vector codes: TP`, empty message), alias `meteorite_grade_do` → `grade_do`, craft/non-rubric never read DB, key-first blank candidate.
- `TestAst2091RubricDispatchGate` — list `empty_render` / `invalid_reason` / forced `auto_mode: 0`, create/put/run **400** with plan errors, key-before-rubric precedence, rubric before token reason on Run.
- `TestAst2091RunTaskRubricGate` — `run_task` → `False`, no thread, `auto_mode=0` when AUTO on; manual row no DB write; craft/non-rubric still start.

Would fail pre-fix ftr (no `rubric_dispatch_error`, list/run/`run_task` green on duplicate TP fixture).

**## What must still hold — OK**

| Item | Check |
|------|--------|
| AST-2008 uptick / `apply_rubric_vectors_save` | No edits in diff |
| AST-1513 `_vector_labels_map` | Untouched (`consult.py` not in diff) |
| AST-1760 all-X / `_render_score` | Untouched |
| AST-1791 / AST-1794 soft-miss | Rubric is additive `invalid_reason` source; rubric-backed only |
| AST-1880 key-first | `invalid_reason` and 400 chain: key → rubric → tokens; tested |
| AST-1819 `empty_tokens` | Still from `_evaluate_dispatch_empty_render` only |
| No new API fields / `TASK_CONFIG` | Reuses `empty_render` + `invalid_reason` only |

## Findings

### advisory — publish-ref history vs product footprint

`git diff ftr…sub` includes many `docs/features/**` archive commits and `sync(dev): origin/dev` on the sub tip; **product** delta is only `src/core/candidate.py`, `src/ui/api/api_admin.py`, `src/core/dispatcher.py` plus AST-2091 tests/bible (9 paths). Not cross-ticket **product** scope (§5.4). Chuckles: when landing this orphaned mini-parent fix, be aware doc-archive commits ride the branch — no Radia action on product.

### advisory — sibling test carry

`merge-tests(AST-2091)` + qa-fix stub sweep (`rubric_dispatch_error → None` in existing AUTO/run/`run_task` cases in `test_api_admin.py`) — expected §5.4 pattern.

### advisory — Canon Scope (off-list)

Joan board named `astral.layers.import-direction`, `astral.dispatch.entity-state-bound`, `astral.dispatch.seed-auto-false`, etc. Not on frozen list by design; late `rubric_dispatch_error` import in `run_task` matches plan and existing cycle break. Optional future statute for “bad rubric not AUTO-runnable” is Archie/product, not this review.

## What's solid

- Single shared helper `rubric_dispatch_error` wired list → create/update AUTO-on → Run → `run_task`, matching AST-1780/AST-1880 shape.
- `TASK_CONFIG.rubric_artifact` + `RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY` (not `rubric_owner_task_key()`) preserves craft tasks.
- Plan fidelity: three scoped files, no `AdminScheduledActions.tsx` change.

## Recommended actions (Chuckles — not Radia)

| Gate | Parent shape | Next |
|------|----------------|------|
| **PROCEED** (C7 complete) | Normal (AST-2013 live; diff vs `ftr/AST-2013-rubric-dup-dispatch-gate`) | Append artifact → `docs(AST-2091): Radia review — clean` on publish ref → post slim upshot `--as radia` → **Review Posted** → `do-all-the-things` §3h clean-review shortcut → **User Testing** (`resolve-child` skipped). |
| UAT (optional) | — | Plan step 5: re-save somerset Do rubric in Artifacts after deploy; spot-check AUTO forced off on other live bad rubrics per Blast radius. |

context_tokens≈22000

```
[code-rubric] PROCEED (Commit: 64bcc193) Rubric gate matches plan
```

## Bug: AST-2103 — Score rubric tokens at the dispatch empty-render call site

`fix` child of orphaned mini-parent bug AST-2020 (`ftr/AST-2020-rubric-gate-call-site`). Scope is this ticket's own `## Scope`: `src/ui/api/api_admin.py`, function `_evaluate_dispatch_empty_render` only — supply the `rubric` entity-context key to `empty_render_for_prompts`. No ancestor box checked; this doc is the one that introduced `_evaluate_dispatch_empty_render` (AST-1854 / AST-2091 precedent). Canon Scope on the ticket: none — ids id-only for the board (`astral.dispatch.entity-state-bound`).

> **⚠️ Headline — this change is a no-op on the current tip.** The ticket was filed on the premise that AST-2092 was not on `origin/dev`. It is now: PR #278 (`16875ec91`, AST-2019) carries `5ff29d792` `code(AST-2092)` onto `origin/dev`, and `sync-child` fast-forwarded this publish ref to dev (`3d9f1d1e5`) at plan time. AST-2091 (`64bcc1935`, `rubric_dispatch_error`) is also on dev and independently gates the exact AST-2020 symptom. The step below is correct with or without AST-2092 and composes with no double-scoring, but on this tip it changes no output. See the ⚠️ Decision at the end of **Proposed change**.

### As-is

Ticket As-is (pre-AST-2092 / pre-AST-2091): `_evaluate_dispatch_empty_render` calls `empty_render_for_prompts(texts, cd, tk, entity_contexts=None)`; that helper scored only `source: candidate`, so an empty `{$RUBRIC_VECTORS}` (and the AST-1405 pins `DO_RUBRIC` / `GET_RUBRIC` / `JD_RUBRIC` / `LIKE_RUBRIC` / `PREFILTER_RUBRIC`) validated `empty_render: false`. abrams' `qualify_job_listings` stayed AUTO, claimed 2 jobs, `agent.do_task` refused ("Empty tokens: RUBRIC_VECTORS"), both routed to `ERROR_QUALIFY_JOB_LISTINGS`.

As-is **on this tip** (verified at plan time): the symptom no longer reproduces. `empty_render_for_prompts` scores `source: rubric` by default (AST-2092), so `_evaluate_dispatch_empty_render` already returns `{"empty_render": True, "empty_tokens": ["RUBRIC_VECTORS", …]}` for a candidate with no current joblist rubric. Independently, `rubric_dispatch_error` (AST-2091) returns `"Rubric 'joblist_rubric' is empty for this candidate."` for `qualify_job_listings` and is wired into `list_dtasks`, create/update AUTO-on, `run_dtask`, and `dispatcher.run_task`.

### To-be

A `source: rubric` token that resolves empty for the row's candidate makes the row `empty_render: true` with that token in `empty_tokens`; AST-1780 list enrichment forces AUTO off; Invalid tooltip names the reason (AST-1819 / AST-1880 / AST-2091 precedence); AUTO-on / Run return 400; no jobs are claimed. Holds on this tip today; this ticket makes `_evaluate_dispatch_empty_render`'s rubric scoring explicit at the call site so it does not depend on the helper's default.

### Repro

Fixture (no DB seed — stub the rubric read; same shape AST-2094's `[bug-repro]` uses):

```python
import src.core.candidate as c
from src.utils.config import empty_render_for_prompts
cd = {"_astral_candidate_id": "abrams", "first": "A"}
texts = ["Rubric: {$RUBRIC_VECTORS} pin {$DO_RUBRIC}"]
c.rubric_criteria_for_token = lambda cid, owner: []          # no current rubric
empty_render_for_prompts(texts, cd, "qualify_job_listings", entity_contexts=None)
empty_render_for_prompts(texts, cd, "qualify_job_listings", entity_contexts={"rubric": {}})
```

| Tree | `entity_contexts=None` | `entity_contexts={"rubric": {}}` |
|------|------------------------|-----------------------------------|
| pre-`5ff29d792` (`ftr` before sync, `d62d88edc`) | `{"empty_render": False, "empty_tokens": []}` — **the bug** | `{"empty_render": True, "empty_tokens": ["RUBRIC_VECTORS", "DO_RUBRIC"]}` |
| this tip (`3d9f1d1e5`, AST-2092 on) | `{"empty_render": True, "empty_tokens": ["RUBRIC_VECTORS", "DO_RUBRIC"]}` | identical |

Filled rubric (`lambda cid, owner: [{"code": "TP", "label": "x"}]`) → `{"empty_render": False, "empty_tokens": []}` in all four cells. Both this-tip rows were executed at plan time.

### Root cause

The rubric tokens are candidate-keyed (`resolve_tokens` reads `rubric_vector` rows off the token view's `_astral_candidate_id` + owner task), but AST-1779 classed `source: rubric` as an `entity_contexts`-only source and AST-1780's call site passed `entity_contexts=None`, so the gate never scored them. AST-2092 fixed the classification in the helper; AST-2091 added a separate rubric-integrity gate. The call site itself still documents the old assumption.

### Proposed change

One edit, `src/ui/api/api_admin.py` only. Do **not** edit `src/utils/config.py`, `src/core/candidate.py`, `src/core/dispatcher.py`, or any caller.

1. **`_evaluate_dispatch_empty_render(candidate_id, task_key)`**, final line (today line 2053):
   - From: `return empty_render_for_prompts(texts, cd, tk, entity_contexts=None)`
   - To:

     ```python
     # Rubric tokens are candidate-keyed (resolver reads cd["_astral_candidate_id"]); the
     # value is unused — only key presence opts source: rubric into scoring (AST-1779 seam).
     # Job/other entity sources stay out: job tokens alone never flip the gate (AST-1780 AC5).
     return empty_render_for_prompts(texts, cd, tk, entity_contexts={"rubric": {}})
     ```
   - Everything above it byte-for-byte unchanged: blank-`cid` / candidate-miss warnings + `empty_render: True`, hydrated `get_candidate` (AST-1854), `build_candidate_token_view`, silent `ValueError` soft-miss (AST-1791/1794), `logger.exception` fail-closed.
2. No new function, import, field, log line, cache, or cap. `_candidate_dispatch_empty_render_error`, `list_dtasks`, `create_dtask`, `update_dtask`, `run_dtask` pick it up unchanged.

**Composition with AST-2092 (no conflict, no double-scoring):**
- Different files: AST-2092 touched only `config.py`; this touches only the `api_admin.py` call line. No merge conflict either way.
- `empty_render_for_prompts` gate is `source not in ("candidate", "rubric") and source not in contexts` (post-2092) / `source != "candidate" and source not in contexts` (pre-2092). `{"rubric": {}}` admits rubric under both; post-2092 it is redundant. Each token name is resolved once (`seen` set), so a token is never scored or listed twice.
- `contexts["rubric"]` is never read (only `contexts.get("job")` is) — `{}` vs any other value is irrelevant; `"job"` is deliberately **not** added.

**Composition with AST-2091:** independent reason source. On `list_dtasks`, `empty_render` is already `er OR key_err OR rubric_err`; `empty_tokens` comes only from `er` and already carries `RUBRIC_VECTORS` on this tip. On AUTO-on / Run, `rubric_dispatch_error` runs **before** `_candidate_dispatch_empty_render_error`, so for `qualify_job_listings` the 400 body is AST-2091's `"Rubric 'joblist_rubric' is empty for this candidate."`, not the ticket To-be's `"Prompt tokens resolve empty…"`. That ordering is AST-2091's and out of this ticket's scope; unchanged here.

⚠️ **Decision (for Chuckles / Susan before fix-board):** with AST-2092 on dev and on this ref, step 1 is a **no-op** — identical return values for every input on this tip. Two honest paths:
- **(a) Ship step 1** as belt-and-suspenders: the call site states its own rubric contract and survives a future revert/narrowing of the helper default. Cost: one line + comment; make-fix / test-fix are trivial (existing AST-2094 + AST-1780/1791/1854 tests cover it; no new `[bug-repro]` can go red on this tip).
- **(b) Cancel AST-2103 / close AST-2020 as fixed by AST-2092 + AST-2091** (both on `origin/dev`); no product edit.
Plan is written for (a) per the spawn instruction ("plan the call-site change … state plainly if it becomes a no-op"); (b) needs no further engineer work.

### Blast radius

- Callers of `_evaluate_dispatch_empty_render`: `list_dtasks` (enrich + force AUTO off), `create_dtask` / `update_dtask` AUTO-on, `run_dtask`, via `_candidate_dispatch_empty_render_error`. On this tip: no behavior change. On a pre-2092 tree: every rubric-token-bearing task (incl. any `craft_*` prompt that references `{$RUBRIC_VECTORS}` or a pin, via `rubric_owner_task_key`) would gain the same flag AST-2092 already introduced — identical set, not a superset.
- Not touched: `dispatcher.run_task` (AST-2091 rubric gate only; no empty-render gate there), AST-1781 revalidation hooks (`database._token_view_for_empty_render` / `_force_auto_off_if_empty_render` call `empty_render_for_prompts` themselves and now score rubric via AST-2092's default).
- Tests (Betty's lane): `TestAst1780EmptyRenderListGatesForceOff` monkeypatches the evaluator — unaffected. AST-1792/1795/1855 classes stub `_dispatch_empty_render_prompt_texts` with candidate-only tokens — unaffected. AST-2094's `TestAst1779EmptyRenderForPrompts` rubric-by-default tests are on the helper — unaffected. Any test asserting `empty_render_for_prompts` was called with `entity_contexts=None` would go red (none found by name at plan time; Betty to confirm). Engineers do not edit `tests/`.

### What must still hold

- AST-1779: `empty_render_for_prompts` signature and default unchanged; chain never scored; job only via the seam.
- AST-1780 AC5: job tokens alone never flip the gate — `"job"` stays out of `entity_contexts`.
- AST-1791 / AST-1794: prompt-load `ValueError` → silent `{"empty_render": False, "empty_tokens": []}`.
- AST-1780: blank/missing candidate → `empty_render: True` + existing warnings; unexpected exceptions → `logger.exception` + fail-closed.
- AST-1854: hydrated `get_candidate` load stays outside the `try`.
- AST-1880 / AST-2091: 400 precedence key → rubric → tokens; `invalid_reason` key-first then rubric; `empty_tokens` sourced only from `_evaluate_dispatch_empty_render`.
- Filled rubric → `empty_render: False` (no false positive).


### AST-2103 — Joan fix-board

[board-joan]  CANON: OK

**Read:** `## Bug: AST-2103` in `docs/features/dispatcher/ast-1780-list-enrich-auto-run-gates-force-auto-off.md` (plan-fix six sections; publish ref `sub/AST-2020/AST-2103-rubric-gate-call-site`, plan context commit `fd31c854b`). Roster overlap: `astral.dispatch.entity-state-bound` (`canon/directives/active/stat.dispatch.entity-state-bound.md`); ticket Canon Scope **none** (board cites that id informally only). No pattern ids on parent scope.

**The one question:** Does the proposed change conflict with or require updating any directive **in force**?

**No.** Canon does not prescribe `entity_contexts=None` vs `{"rubric": {}}` on `_evaluate_dispatch_empty_render`. That contract is AST-1779 / AST-1780 feature plan and bible, same class as AST-2092’s helper default change (prior fix-board **CANON: OK** on `ast-1779` doc). This ticket only makes the call site explicit in `api_admin.py`; it does **not** edit `empty_render_for_prompts` signature or default (`## What must still hold`).

- **`astral.dispatch.entity-state-bound`:** Still satisfied. Per-row `candidate_id` / task_key evaluation; no `dispatch_task`, `entity_type`, `trigger_state`, or claim-path edits. Rubric scoring remains candidate-keyed via existing resolver/`cd`; omitting `"job"` from `entity_contexts` matches plan AC5 intent and does not relax entity-binding law.

- **No statute/pattern amend:** On current tip the edit is a documented no-op (AST-2092 default + AST-2091 gate already fix the symptom). Belt-and-suspenders at the call site does not introduce a new corpus carve-out or contradict in-force text.

**Not ESCALATE:** The (a) ship vs (b) cancel choice in **Proposed change** is lane routing for Chuckles/Susan, not ambiguous statute intent or unbounded architectural precedent.


### AST-2103 — Radia review

```
[code-rubric]

**Ticket:** AST-2103  
**Publish ref:** `origin/sub/AST-2020/AST-2103-rubric-gate-call-site` @ `ad073edebe8648994baa8291115d150b5abf2950`  
**Diff base:** `origin/ftr/AST-2020-rubric-gate-call-site` @ `d62d88edc281f4a479187fb47951cfa90404fa62` (merge-base = ftr tip)  
**Corpus:** `f3186d4c58d889a3a2767e51874a11dd942f002b`  
**Overall:** CLEAN  

## Canon scores

Frozen list **empty** (AST-2103 description: **Citations:** none / no Canon Scope block — same as AST-2091 / AST-1854 fix children). No directive rows to score; not a §5.3 **ESCALATE** (Joan fix-board `[board-joan] CANON: OK`; one-line call-site change does not contradict in-force scoped statutes on the touched path).

## Column diff vs plan stage

`no plan-stage scores attached` — Joan fix-board only (no `validate-plan` canon table for this bug).

## Frame diff

(none)

## Fix-specific checks

**[bug-repro] not applicable — clean board opt-out** — fix-board **TESTS: OK**; no `qa-fix` / no `[bug-repro]` on this ticket (plan documents that on the current tip no repro can flip red post-AST-2092). Existing AST-2094 / AST-1780 family tests cover helper + gate behavior.

**## What must still hold — OK**

| Item | Check |
|------|--------|
| AST-1779 — helper signature/default; chain unscored; job via seam only | `empty_render_for_prompts` in `config.py` untouched; call passes only `{"rubric": {}}` |
| AST-1780 AC5 — job alone never flips gate | `"job"` not added to `entity_contexts` |
| AST-1791 / AST-1794 — prompt `ValueError` soft-miss | `try`/`except ValueError` path above return unchanged |
| AST-1780 — blank/missing candidate + fail-closed on unexpected errors | Early returns + `logger.exception` path unchanged |
| AST-1854 — hydrated `get_candidate` outside `try` | `get_candidate` still before `try` |
| AST-1880 / AST-2091 — key → rubric → tokens; `empty_tokens` from evaluator only | Additive seam only; no change to `_candidate_dispatch_empty_render_error` or rubric gate ordering |
| Filled rubric → not false positive | Same resolver/`cd`; explicit rubric key matches AST-1779 manifest intent |

## Findings

### advisory — publish-ref history vs product footprint

`git diff origin/ftr/AST-2020-rubric-gate-call-site...origin/sub/AST-2020/AST-2103-rubric-gate-call-site` is large (dev sync + sibling epics AST-2019/AST-2013/AST-2015/AST-2042, tests, docs). **Product delta for AST-2103** is commit `ad073edeb` only: `src/ui/api/api_admin.py` (+4/−1 in `_evaluate_dispatch_empty_render`). Not cross-ticket **product** smuggling for this ticket (§5.4). Chuckles: when merging/stacking AST-2020, treat carried history like AST-2091 advisory — no Radia action on the one-line fix.

### advisory — sibling test carry

`merge-tests` / AST-2094 / AST-2091 / AST-2090 rows on the publish ref — expected §5.4 pattern; out of AST-2103 scope.

### advisory — Canon Scope (off-list)

Joan board cited `astral.dispatch.entity-state-bound` informally; not on frozen list by design. Change stays per-row `candidate_id`/`task_key` evaluation via existing `cd` and AST-1779 seam; no dispatch_task / claim-path edits. Matches board triage.

### advisory — behavioral no-op on tip

Plan **Proposed change** documents identical outputs with AST-2092 on dev; diff is belt-and-suspenders at the call site. UAT may not observe a delta — acceptable per plan path (a).

## What's solid

- Plan fidelity: single edit in `_evaluate_dispatch_empty_render` exactly as specified (comment explains candidate-keyed rubric + AC5).
- Composes with AST-2092 (redundant admit) and AST-2091 (independent reason) per plan composition notes.
- No tests asserting `entity_contexts=None` on this call site (grep clean).

## Recommended actions (Chuckles — not Radia)

| Gate | Parent shape | Next |
|------|----------------|------|
| **PROCEED** (C7 complete) | AST-2020 mini-parent with **live** `ftr/AST-2020-rubric-gate-call-site` (ftr tip = merge-base) | Append artifact → `docs(AST-2103): Radia review — clean` on publish ref → post slim upshot `--as radia` → **Review Posted** → `do-all-the-things` §3h clean-review shortcut → **User Testing** (`resolve-child` skipped). |
| UAT (optional) | — | Spot-check list row `empty_render` / AUTO-off on candidate with empty joblist rubric; expect same as pre-fix tip (no-op) unless AST-2092 reverted in env. |

context_tokens≈12000
```

```
[code-rubric] PROCEED (Commit: ad073ede) Call-site rubric seam explicit
```


### AST-2103 — test routing

docs-acceptance: fix-board `[board-betty] TESTS: OK` — no qa-fix, no new tests. Existing AST-2092 / AST-2094 `TestAst1779EmptyRenderForPrompts` coverage (including the `entity_contexts={"rubric": {}}` case) already pins this behavior; the call-site change is a verified no-op on the current tip.

### AST-2020 — epic registry Threads (mirror)

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/44df6ed17f933d3a939581634566a7fc/266932a9-ef4b-4b88-9df8-355722246ab5/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/3e21e535-8623-47ca-bb6e-707d27404871/store.db` |
| Radia | review | `/home/susan/.cursor/chats/44df6ed17f933d3a939581634566a7fc/e8749e93-07fa-4f0d-a856-0d00e57a4b83/store.db` |
| Joan | validate | `f9f2c4dd-c376-47b8-bbb3-37859aa99d63` |

Git (deleted at finish-up): parent `ftr/AST-2020-rubric-gate-call-site`, AST-2103 `sub/AST-2020/AST-2103-rubric-gate-call-site`, epic worktree `astral-AST-2020/`.
