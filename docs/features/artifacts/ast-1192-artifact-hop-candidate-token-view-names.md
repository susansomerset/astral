# AST-1192 — Artifact hop candidate token view (names)

**Linear:** https://linear.app/astralcareermatch/issue/AST-1192/artifact-hop-candidate-token-view-names-issues-while-running  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1163/issues-while-running-anticipate-scan  
**Publish ref:** `sub/AST-1163/AST-1192-artifact-hop-candidate-token-view-names`

After AST-1014, `TOKEN_SOURCES` name tokens (`{$FIRST_NAME}`, `{$LAST_NAME}`, `{$FULL_NAME}`, pronouns) walk **columns** on `build_candidate_token_view`, not the raw `candidate_data` JSON blob. Artifact hop runtime (`do_task` for `anticipate_scan` / shared BUILD_ARTIFACTS chain) and Manage Tasks preview (`preview_task_prompt`) still pass the raw blob, so name tokens resolve empty despite populated `first`/`last` columns. This ticket wires those two resolve paths to the walkable token view and adds debug-gated found/recorded lines for name-token outcomes. Does **not** own ANALYSIS_* vector↔rubric match parity (AST-1193).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | In `do_task`, build `cd` via `build_candidate_token_view` from the full candidate row (load by `astral_candidate_id` when ctx is a dispatch raft without columns); keep company_search_terms overlay; Style D found/recorded for name-token outcomes when `debug=True` | core |
| `src/core/candidate.py` | In `preview_task_prompt`, set `cd = build_candidate_token_view(candidate)` instead of `candidate.get("candidate_data")` so Manage Tasks preview matches runtime | core |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| `_format_analysis_phase_text` / ANALYSIS_* match parity | AST-1193 |
| Provider timeout / blank `error=` / zero-token hardening | AST-1164 |
| `TOKEN_SOURCES` / `JOB_TOKEN_CONFIG` key declarations | already on baseline (AST-1014 / AST-513) |
| `tracker._candidate_data_for_job` resume-structure callers (library blob shape) | leave blob-shaped — do not convert that helper to a token view |
| Admin `_resolve_agent_preview_candidate` / `_enrich_tasks` / `_resolve_adhoc` | already on token view (AST-1014 resolve) |
| Prompt prose in Manage Tasks | out of scope |
| `tests/`, `docs/test-bible/**` | Betty |

## Stage 1: `do_task` feeds token view + name-token debug

**Done when:** A `do_task("anticipate_scan", …)` (or any shared artifact hop) with `ctx` carrying `astral_candidate_id` for a candidate whose `first`/`last` columns are non-empty substitutes non-empty `{$FIRST_NAME}` / `{$LAST_NAME}` (no empty-token warnings for those names). With `debug=True`, Style D found/recorded lines show name-token outcomes for that candidate. Mid-chain `run_next` hops reuse the same `ctx` path (no second wiring).

1. In `src/core/agent.py`, inside `do_task`, **replace** the current token-dict construction:

   ```python
   cd = (ctx.get("candidate_data") or {}) if ctx else (candidate_data or {})
   ```

   with a helper (module-private, placed near other `do_task` helpers — e.g. after `_job_context_for_call`) named `_token_view_for_do_task`:

   ```python
   def _token_view_for_do_task(
       ctx: Optional[Dict[str, Any]],
       candidate_data: Optional[Dict[str, Any]],
   ) -> dict:
       """Walkable resolve_tokens dict: name columns + library blobs (AST-1192 / AST-1014)."""
   ```

2. `_token_view_for_do_task` behavior (literal):

   a. Lazy-import (cycle break — same pattern as existing `do_task` candidate imports; include the in-code cycle-break comment):

      ```python
      # Lazy import breaks agent↔candidate cycle (candidate imports agent paths).
      from src.core.candidate import build_candidate_token_view, get_candidate
      ```

   b. Resolve candidate id: `cid = str((ctx or {}).get("astral_candidate_id") or "").strip()`.

   c. **Preferred — load full row by id:** If `cid` is non-empty, call `get_candidate(cid)`. If a row is returned, `return build_candidate_token_view(row)`.

   d. **Full-row ctx (intake / candidate-entity paths):** Else if `ctx` is a dict and `isinstance(ctx.get("candidate_data"), dict)` and (`"first" in ctx` or `"last" in ctx` or `"full" in ctx`), `return build_candidate_token_view(ctx)`.

   e. **Already a token view:** Else if `candidate_data` is a dict and (`"first" in candidate_data` or `"contact" in candidate_data`) and `"candidate_data" not in candidate_data`, return `dict(candidate_data)` (caller already passed a view — e.g. admin paths that forward a view into `candidate_data=`).

   f. **Fallback:** Else return `dict(candidate_data or (ctx or {}).get("candidate_data") or {})` — raw blob / empty; name columns unavailable (preserves pre-fix behavior when no candidate id/row).

   ⚠️ **Decision:** Load by `astral_candidate_id` rather than calling `build_candidate_token_view` on the dispatch `task_ctx`. Dispatch rafts (consult `_run_dispatch_chain_jobs`) inject the **blob** as `candidate_data` and set `astral_candidate_id` but do **not** copy `first`/`last` columns onto `ctx` — viewing that raft would still yield empty names.

   ⚠️ **Decision:** Do **not** change `tracker._candidate_data_for_job` to return a token view. That helper feeds resume-structure / artifact merge paths that expect library-blob shape (`artifacts.base_resume` under the JSON blob). Token-view cutover stays at the resolve boundary (`do_task` / preview).

3. In `do_task`, set `cd = _token_view_for_do_task(ctx, candidate_data)` **before** the existing `requires_candidate_key` empty check and **before** the company_search_terms overlay block. Keep the overlay as today: when `candidate_id` is set, `cd = dict(cd)`, set `cd["_astral_candidate_id"]`, merge `artifacts.company_search_terms` via `company_search_terms_joined_text`. (Overlay still uses the existing lazy import of `company_search_terms_joined_text` — do not duplicate that import into the new helper unless consolidating is trivial and keeps one cycle-break comment.)

4. When `debug=True`, after `_jc` / `_cc` are built and inside the existing `if debug:` block that already emits job_context token lines (near `job_context tokens=…`), add Style D name-token found/recorded (backend only; no new ungated logs):

   - One `debug_index` via `_do_task_debug_logger(debug)`:
     - `func="do_task.candidate_token_view"`
     - `index=1`, `total=1` (single candidate identity for this hop; do not invent batch counters)
     - `identifier` = `str(candidate_id or cd.get("_astral_candidate_id") or "")`
     - `outcome` = `"success — name tokens"` when both `str(cd.get("first") or "").strip()` and `str(cd.get("last") or "").strip()` are non-empty; else `"partial — name tokens"` when exactly one is non-empty; else `"empty — name tokens"` when both empty (or no view).
   - `debug_detail` lines (contract prefix via helper):
     - `found first=<nonempty|empty> last=<nonempty|empty> full=<nonempty|empty>`
     - `recorded FIRST_NAME=<repr of cd first or ''> LAST_NAME=<repr of cd last or ''> FULL_NAME=<repr of cd full or ''>`
   - Emit **only** when `debug=True`. Do not log full prompts. Do not touch ANALYSIS phase debug (AST-1193).

5. Do **not** alter `run_next` recursion arguments — child hops already pass the same `ctx`; the new helper runs again at the top of each `do_task` and rebuilds the view (idempotent). Do **not** change hop order, `run_next`, claim/process/release, or prompt prose.

## Stage 2: Manage Tasks preview uses the same token view

**Done when:** `preview_task_prompt` for a task whose prompts reference `{$FIRST_NAME}` / `{$LAST_NAME}` (e.g. `anticipate_scan`) against a candidate with non-empty name columns returns substituted non-empty names in the resolved segment text (same walkable view as Stage 1).

1. In `src/core/candidate.py` `preview_task_prompt`, **replace**:

   ```python
   cd = candidate.get("candidate_data") or {}
   ```

   with:

   ```python
   cd = build_candidate_token_view(candidate)
   ```

   (`build_candidate_token_view` is already defined in this module — no new import.)

2. Keep the existing `astral_job_id` → `build_job_token_context(job, cd, …)` call and the company_search_terms overlay on `cd` unchanged — they already mutate a dict copy; ensure overlay still does `cd = dict(cd)` before writing `_astral_candidate_id` / `artifacts` (same as today after the view is built).

3. Do **not** change `preview_prompt` / `simulated_chain_context_for_preview` signatures — they already accept the walkable `candidate_data` dict; callers that already pass a token view (admin agent preview) stay correct.

## Self-Assessment

**Scope:** `Single-Component` — two core resolve entry points (`do_task`, `preview_task_prompt`) cut over to the existing AST-1014 token view; no new modules, no config keys, no UI.

**Conf:** `high` — root cause is the empty-name log (`path=first` / `path=last` against a blob that has no top-level `first`/`last`); admin preview already demonstrates the correct `build_candidate_token_view` pattern.

**Risk:** `Medium` — `do_task` is shared by all agent hops; wrong view construction could blank contact/context tokens. Mitigated by loading the full candidate row (same helper admin uses) and leaving `_candidate_data_for_job` blob consumers untouched.

## Rules check (ASTRAL_CODE_RULES)

| Rule | Notes |
|------|-------|
| §1.1 in-scope-only | Only name/token-view wiring + debug on touched resolve paths; ANALYSIS parity and provider hardening excluded |
| §1.3 DRY | Reuse `build_candidate_token_view`; one private helper in `agent.py` for row-vs-raft resolution |
| §1.5 / §1.5.1 debug | New lines only when `debug=True`; Style D index + `\|` detail; no `[DEBUG]` info spam |
| §2.1 config | No new token maps; `TOKEN_SOURCES` remains authority |
| §2.4 batch | No new claim/process/release lifecycle |
| §2.6 state machine | Unchanged |
| §3.3 imports | Lazy `candidate` import inside helper / existing `do_task` cycle break; `candidate.py` Stage 2 needs no new cross-layer import |
| §3.5 naming | `_token_view_for_do_task` private helper; public APIs unchanged |

## Review

**Publish ref:** `sub/AST-1163/AST-1192-artifact-hop-candidate-token-view-names`  
**Build tip:** `08d9a966fb4db7dd013eb419cb0912588b3575e0`

### code-rubric.v1 verdict

[code-rubric] revision=1

**Rubric:** code-rubric.v1
**Ticket:** AST-1192
**Publish ref:** `64125186` (`origin/sub/AST-1163/AST-1192-artifact-hop-candidate-token-view-names`)
**Overall:** DISCUSS

Full active corpus (63 leaves — 18 universal + 45 scoped) swept in-session against `git diff origin/dev...origin/sub/AST-1163/AST-1192-artifact-hop-candidate-token-view-names` (diff layers `{core, docs}`; paths `src/core/agent.py`, `src/core/candidate.py`, `docs/features/**`, `docs/test-bible/**`, `tests/**`; change_types `{add, modify}`). No violations. `src/` footprint is exactly the two planned files (`agent.py` +57/-1, `candidate.py` +2/-1); `_candidate_data_for_job` / `tracker.py` correctly untouched per the plan's stated boundary. Role boundaries clean per commit: `code(AST-1192)` touches only `src/`, `test(AST-1192)` only `tests/`+`docs/test-bible/`, `docs(AST-1192)` only `docs/features/`.

**Plan adherence:** Implementation matches the plan doc literally — `_token_view_for_do_task` branch order (id-load → full-row ctx → already-view → raw fallback), overlay sequencing preserved, Style D `do_task.candidate_token_view` found/recorded gated under existing `if debug:` block, `preview_task_prompt` one-line swap with no new import. Joan's `plan-rubric.v1` verdict (r1, APPROVED) is attached; her 3 `discuss` items are carried forward below since the shipped code still exhibits them as described (her 4th point, DB-read-per-hop, she marked `acceptable` — concur, negligible next to the LLM call).

**Pattern conformance:** `astral.config.config-source-of-truth`, `astral.agent.do-task-delegation`, `astral.standards.debug-contract-gated`, `astral.standards.in-scope-only`, `astral.standards.dry-and-focused-functions`, `astral.standards.logging-via-utils`, `astral.layers.import-direction`, `astral.standards.no-cross-contamination` — all cited in the ticket's "In scope" list and covered `conforms` via the full sweep. `pattern.config.config-block` (also cited) does not resolve to any id in the active `canon/statutes/**` corpus — `not-cited`/stale shorthand, likely meant as the same `config-source-of-truth` reference already listed; advisory only, not a block.

**Findings:**

- **discuss** — `requires_candidate_key` guard goes quiet. Branches (c)/(d) of `_token_view_for_do_task` always return the full 8-key view shape once a row loads, so `if task_config.get("requires_candidate_key") and not cd:` (`src/core/agent.py`) can no longer fire even when every value in that view is empty. Confirmed present as shipped — same as Joan flagged at plan time. Consider testing a meaningful field (`first`/`contact`/`context` non-empty) instead of dict truthiness.
- **discuss** — No branch tag on the debug `found` line. `do_task.candidate_token_view`'s `debug_detail` reports name-token emptiness but not which of the helper's 4 branches produced the view, so a future `astral_candidate_id`/`candidate_data` divergence (e.g. a batch row missing `company`) would silently fall to the raw-blob branch with no signal beyond "empty — name tokens." Confirmed present as shipped.
- **discuss** — Branches (d)/(e) hardcode `build_candidate_token_view`'s key names (`"first" in ctx`, `"contact" in candidate_data`, `"candidate_data" not in candidate_data`) to detect shape at a distance. If the view's keys change, these probes misroute silently. A small is-view predicate beside the helper in `candidate.py` would keep the shape contract in one place. Confirmed present as shipped.

**What's solid:** Debug contract is textbook — gated under the existing `if debug:` block, `index 1/1` (correctly not inventing a batch counter for a single candidate identity), `found`/`recorded` lines via the `DEBUG_DETAIL_PREFIX` helpers, no full-blob logging. Cycle-break comment on the lazy `candidate` import is accurate (`candidate.py:23` really does import from `agent.py`). `_candidate_data_for_job` / `tracker.py` boundary honored exactly as the plan required.

## Frame diff

(none) — implementation matches the plan doc's Files Changed / Stage 1 / Stage 2 as written; no adds or moves applied to this description.

context_tokens≈58000

— Radia
