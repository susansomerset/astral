# AST-1163 — Issues while running anticipate_scan
**Component:** artifacts  
**Children:** AST-1192, AST-1193  
**Linear archived:** AST-1163 2026-08-07; AST-1192 2026-08-07; AST-1193 2026-08-07

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-08-05 16:08 | AST-1192 | docs | `1b9a5383e` | docs(AST-1192): plan — artifact hop candidate token view (names) |
| 2026-08-05 16:08 | AST-1193 | docs | `4ec1524d3` | docs(AST-1193): plan — ANALYSIS token vector↔rubric match parity |
| 2026-08-05 16:16 | AST-1192 | code | `0ab2f6a86` | code(AST-1192): do_task candidate token view + name-token debug |
| 2026-08-05 16:16 | AST-1193 | docs | `e3a207bc0` | docs(AST-1193): plan discuss r1 — snapshot fallback for ANALYSIS match |
| 2026-08-05 16:16 | AST-1193 | docs | `f133877f4` | docs(AST-1193): plan discuss r1 — snapshot fallback for ANALYSIS match |
| 2026-08-05 16:17 | AST-1192 | code | `08d9a966f` | code(AST-1192): preview_task_prompt uses candidate token view |
| 2026-08-05 16:17 | AST-1192 | docs | `f6a8ea8c5` | docs(AST-1192): review stub after build |
| 2026-08-05 16:20 | AST-1192 | merge-tests | `641251866` | merge-tests(AST-1192): origin/tests 8d2ea872e35dd7b5e81207097772c0ad3b53a3a0 |
| 2026-08-05 16:20 | AST-1192 | test | `8d2ea872e` | test(AST-1192): artifact hop candidate token view name coverage |
| 2026-08-05 16:25 | AST-1193 | code | `5a7b1f39b` | code(AST-1193): shared _find_rubric_criterion for scoring helpers |
| 2026-08-05 16:26 | AST-1193 | code | `29c1af565` | code(AST-1193): ANALYSIS live/snapshot match + debug found/recorded |
| 2026-08-05 16:26 | AST-1193 | docs | `32eb9f7f6` | docs(AST-1193): build review stub |
| 2026-08-05 16:28 | AST-1192 | docs | `18338efe4` | docs(AST-1192): Radia review — discuss |
| 2026-08-05 16:29 | AST-1193 | merge-tests | `64ea1d86f` | merge-tests(AST-1193): origin/tests d15b790fa7b681b3206a77a2346e0993c6d760a7 |
| 2026-08-05 16:29 | AST-1193 | test | `d15b790fa` | test(AST-1193): ANALYSIS live/snapshot match + debug coverage |
| 2026-08-05 16:31 | AST-1192 | resolve | `e47718916` | resolve(AST-1192): — findings addressed |
| 2026-08-05 16:35 | AST-1193 | docs | `b91302dd8` | docs(AST-1193): Radia review — clean |
| 2026-08-05 16:37 | AST-1193 | resolve | `11675a0d2` | resolve(AST-1193): — clean |
| 2026-08-05 16:38 | AST-1163/1193 | merge-resume | `e6d3505c3` | merge-resume(AST-1193): stack sub onto ftr/AST-1163-anticipate-scan-token-context |
| 2026-08-07 18:26 | AST-1192 | docs | `3f3fa4e98` | docs(AST-1192): archive Linear issue content |
| 2026-08-07 18:26 | AST-1193 | docs | `ba6bc5bc5` | docs(AST-1193): archive Linear issue content |
| 2026-08-07 18:28 | AST-1163 | docs | `b01b04cf5` | docs(AST-1163): archive Linear issue content |

_One row is cross-ticket noise from a different family: `test(AST-1210): lock evaluate_meteorite twin contract + restore AST-1193 parity` (2026-08-05 23:51) — a later AST-1210 test-tree commit (`docs/features/interface/`) whose subject restores parity with AST-1193's shipped behavior but is not this family's own work; omitted from the table above._

## Epic — AST-1163
_Archived: 2026-08-07 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1163/issues-while-running-anticipate-scan · Status at archive: Archive · Project: Astral Artifacts · Assignee: chuckles · Priority / estimate: Urgent / — · Blocked by / blocks / related: related: AST-1162; related: AST-1161_

### Purpose

`anticipate_scan` is the entry hop of the resume artifact chain. A recent run showed empty candidate name tokens and empty / unusable ANALYSIS phase tokens because grade vectors could not be matched to the candidate's live rubric — so the hop went to the LLM without identity or consult recap. Until those prompt inputs resolve correctly, Generate Artifacts cannot produce a trustworthy ATS keyword scan. This epic restores correct candidate-name and ANALYSIS token context for that hop (and sibling artifact hops that share the same resolve path). Provider timeout / blank-error / zero-token hardening for the same hop is **AST-1164** (related), deferred until name + vector context is understood.

### Functional scope

* Artifact `do_task` hops (starting with `anticipate_scan`) resolve `{$FIRST_NAME}`, `{$LAST_NAME}`, and related candidate identity tokens from the same authoritative name fields the rest of the product uses after the contact/name-columns cutover — when the candidate has names set, those tokens are non-empty in the prompts that reference them.
* `{$ANALYSIS_JD}`, `{$ANALYSIS_DO}`, `{$ANALYSIS_GET}`, and `{$ANALYSIS_LIKE}` format every persisted consult grade vector using the **same** label-or-code resolution rules as consult scoring against the candidate's live rubric for that phase (CONSIDER / rubric blob / ANALYSIS RESULT). Prompt assembly for artifact hops matches other agent calls — vectors scoring accepts must not be silently skipped in the ANALYSIS token formatter, leaving the token empty while grades exist.
* With `debug=True` on the touched backend resolve/format path: log what was **found** and what was **recorded** per step (candidate id, name-token outcomes, per-phase grade count vs formatted vector count). Index headers use universal `index N/M` + primary identifier + outcome (Style D); working detail lines use the contract prefix (two spaces, pipe, two spaces); payloads >50 lines use first 15 / `<n lines omitted>` / last 15. Backend only.

### Architectural definition

* **Patterns to reuse** — `pattern.config.config-block` (token registry / JOB_TOKEN_CONFIG remain config authority; no parallel token maps); `pattern.batch.entity-claim-process-release` (artifact hop stays claim/process/release; no new dispatch lifecycle); `pattern.dispatch.run-next-chain-authority` (`run_next` / hop order unchanged — fix resolve inputs, not chain topology).
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.config.config-source-of-truth` (TOKEN_SOURCES / JOB_TOKEN_CONFIG); `astral.standards.debug-contract-gated` (debug contract above); `astral.standards.in-scope-only`; `astral.standards.no-cross-contamination`; `astral.standards.dry-and-focused-functions`; `astral.standards.logging-via-utils`; `astral.standards.data-raises-caller-logs`; `astral.layers.import-direction`; `astral.agent.do-task-delegation` (prompt assembly stays in `do_task`); `astral.agent.grade-vector-validation` (ANALYSIS formatter uses the same vector match rules as consult scoring); `astral.batch.claim-process-release`; `astral.dispatch.run-next-is-chain-authority`; `astral.patterns.coat-check-never-store-empty` (do not persist empty failed ANALYSIS / hollow prompt outputs as if successful).

### Boundaries

* Does **not** re-author `anticipate_scan` prompt prose in Manage Tasks (Susan's prompts stay).
* Does **not** harden provider timeouts, blank `error=`, or `stop=?` / zero-token response classification — that is **AST-1164** (related).
* Does **not** add hollow-context fail-fast / long-wait gates in this epic; Susan wants name + missing-vector causes understood first (provider wait may or may not be related).
* Does **not** change consult grading persistence keys, pass/fail thresholds, or job state machine topology.
* Does **not** regenerate or rewrite candidate rubrics; it aligns ANALYSIS formatting with the live rubric and match rules consult scoring already uses.
* Does **not** expand schedulability of `anticipate_scan` (still chain-hop, not a default Scheduled Action).
* Must not break other artifact hops that share the same token resolve / job_context builders (`contemplate_job` and later hops).
* Sibling UT work on signature spacing (**AST-1161** / **AST-1162**) is out of scope.

### Acceptance criteria

1. For a candidate with non-empty first/last name columns, running `anticipate_scan` (or Manage Tasks preview for that task with the same candidate) substitutes non-empty `{$FIRST_NAME}` and `{$LAST_NAME}` — no empty-token warnings for those names on that run.
2. For a job with persisted JD/DO/GET/LIKE grades whose vectors match the candidate's live rubric under the same label-or-code rules consult scoring uses, each corresponding `{$ANALYSIS_*}` token is non-empty and includes CONSIDER / rubric blob / ANALYSIS RESULT for those vectors — no per-vector "no rubric criterion" skip that empties the token while grades exist.
3. A debug-gated run of the fixed path shows per-index found/recorded lines for candidate identity and each ANALYSIS phase (counts of grades vs formatted vectors).
4. Susan can reproduce: after #1–#2 land, a Generate Artifacts / `anticipate_scan` run on a candidate with names and complete consult grades no longer logs empty `{$FIRST_NAME}` / `{$LAST_NAME}` or empty `{$ANALYSIS_*}` from unmatchable vectors (any remaining failure is outside this epic — e.g. **AST-1164** provider path).

### Dependencies and blockers

* Baseline: AST-513 (ANALYSIS job tokens), AST-1014 (name columns + token view), AST-595/AST-597 (BUILD_ARTIFACTS hop states / mid-chain), AST-1150/AST-1155 (rubric completeness / incomplete grades) — already shipped; this epic fixes runtime wiring/parity against that baseline.
* **Related (not blocking):** **AST-1164** — provider timeout / empty-error / zero-token hardening for the same hop; deferred until name + vector issues are understood.
* No open Linear blockers. Parallel Artifacts UT: **AST-1161** (signature spacing) — no functional dependency.

### Open questions

none.

### Proposed child tickets

**1: Artifact hop candidate token view (names) — Ada** — Ensure artifact `do_task` / preview resolve paths feed the walkable candidate token view (name columns + library blobs) so `{$FIRST_NAME}` / `{$LAST_NAME}` (and siblings) resolve for `anticipate_scan` and shared hops; include debug found/recorded for name-token outcomes on the touched path. Does **not** own ANALYSIS formatter matching (#2).
**Citations:** `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.agent.do-task-delegation`; `astral.standards.debug-contract-gated`; `astral.standards.in-scope-only`.

**2: ANALYSIS token vector↔rubric match parity — Hedy** — Make ANALYSIS_* job-token formatting resolve grade vectors against live rubric criteria with the **same** label-or-code matching rules consult scoring already uses (prompt assembly parity across agent calls), so persisted grades produce non-empty formatted ANALYSIS tokens; include debug found/recorded for per-phase grade vs formatted counts. Does **not** own candidate name view (#1).
**Citations:** `astral.agent.grade-vector-validation`; `astral.config.config-source-of-truth`; `astral.standards.dry-and-focused-functions`; `astral.standards.debug-contract-gated`; `astral.patterns.coat-check-never-store-empty`.

### Original brief

```
LLM deepseek task=anticipate_scan 1425.7s stop=? tokens in=0 out=0
do_task(anticipate_scan) provider call failed batch_id=anticipate_scan-bc0b3279-bde7-4c7e-a895-156ca2fa7b4a error=
_format_analysis_phase_text: no rubric criterion for vector 'Compensation' (phase=ANALYSIS_JD)
_format_analysis_phase_text: no rubric criterion for vector 'Domain & Role Type Exclusions' (phase=ANALYSIS_JD)
_format_analysis_phase_text: no rubric criterion for vector 'Program Scope' (phase=ANALYSIS_JD)
_format_analysis_phase_text: no rubric criterion for vector 'Remote/Location Policy' (phase=ANALYSIS_JD)
_format_analysis_phase_text: no rubric criterion for vector 'Technical Scope' (phase=ANALYSIS_JD)
_format_analysis_phase_text: no rubric criterion for vector 'AI/ML Product Integration' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Autonomy & Creative Latitude' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Cloud Platform & Architecture Depth' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Cross-Functional Scope' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Company Stage Fit' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Delivery Framework Ownership' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Healthcare Domain Expertise' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Meaningful Work & Utilization' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Remote-First Requirement' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Structure-from-Chaos Need' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Team Culture & Respect' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Technical Hands-On Partnership' (phase=ANALYSIS_DO)
_format_analysis_phase_text: no rubric criterion for vector 'Keyword / ATS Match' (phase=ANALYSIS_GET)
_format_analysis_phase_text: no rubric criterion for vector 'Credential & Certification Alignment' (phase=ANALYSIS_GET)
_format_analysis_phase_text: no rubric criterion for vector 'Domain/Sector Credibility' (phase=ANALYSIS_GET)
_format_analysis_phase_text: no rubric criterion for vector 'Education Level Match' (phase=ANALYSIS_GET)
_format_analysis_phase_text: no rubric criterion for vector 'Role Type Fit (IC vs. Manager vs. Consultant)' (phase=ANALYSIS_GET)
_format_analysis_phase_text: no rubric criterion for vector 'Scope & Scale Signaling' (phase=ANALYSIS_GET)
_format_analysis_phase_text: no rubric criterion for vector 'Technical Depth vs. Management Breadth' (phase=ANALYSIS_GET)
_format_analysis_phase_text: no rubric criterion for vector 'Work Model & Geographic Compatibility' (phase=ANALYSIS_GET)
_format_analysis_phase_text: no rubric criterion for vector 'Chaos-to-Structure Mandate' (phase=ANALYSIS_LIKE)
_format_analysis_phase_text: no rubric criterion for vector 'Compensation & Practical Fit' (phase=ANALYSIS_LIKE)
_format_analysis_phase_text: no rubric criterion for vector 'Domain Fit: Healthcare, SaaS, Cloud' (phase=ANALYSIS_LIKE)
_format_analysis_phase_text: no rubric criterion for vector 'Gut Instinct: Would She Brag?' (phase=ANALYSIS_LIKE)
_format_analysis_phase_text: no rubric criterion for vector 'Growth & Learning Trajectory' (phase=ANALYSIS_LIKE)
_format_analysis_phase_text: no rubric criterion for vector 'Mission & Impact Alignment' (phase=ANALYSIS_LIKE)
_format_analysis_phase_text: no rubric criterion for vector 'Meaningful Work & Utilization' (phase=ANALYSIS_LIKE)
_format_analysis_phase_text: no rubric criterion for vector 'Remote-First Authenticity' (phase=ANALYSIS_LIKE)
_format_analysis_phase_text: no rubric criterion for vector 'Team Culture & Respect' (phase=ANALYSIS_LIKE)
_format_analysis_phase_text: no rubric criterion for vector 'Technical Hands-On Partnership' (phase=ANALYSIS_LIKE)
Token {$FIRST_NAME} resolved to empty (path=first, task=anticipate_scan)
Token {$LAST_NAME} resolved to empty (path=last, task=anticipate_scan)
Token {$FIRST_NAME} resolved to empty (path=first, task=anticipate_scan)
Token {$FIRST_NAME} resolved to empty (path=first, task=anticipate_scan)
Token {$FIRST_NAME} resolved to empty (path=first, task=anticipate_scan)
Token {$FIRST_NAME} resolved to empty (path=first, task=anticipate_scan)
Token {$FIRST_NAME} resolved to empty (path=first, task=anticipate_scan)
Token {$FIRST_NAME} resolved to empty (path=first, task=anticipate_scan)
Token {$ANALYSIS_DO} resolved to empty (job_context, task=anticipate_scan)
Token {$FIRST_NAME} resolved to empty (path=first, task=anticipate_scan)
Token {$FIRST_NAME} resolved to empty (path=first, task=anticipate_scan)
```

#### Comments

##### hedy — 2026-08-05T23:17:12.589Z
AST-1193 plan-discuss r1 note (no status change asked):

Parent-log ANALYSIS empties are **not** explained by code-vs-label match alone — vectors are full labels. Formatter loads live `rubric_criteria_for_task` only and ignores job-carried `*_rubric` snapshots (AST-1063). Plan Stage 3 on AST-1193: live first, then snapshot identity + live content-by-code, so AC4 can land without regenerating rubrics. Override on the child if that decision is wrong.

##### chuckles — 2026-08-03T22:38:04.557Z
@susan

1. Which candidate id + job id produced the pasted log (so UAT can replay the exact hollow-token case)?
2. Is the DeepSeek ~24m / `tokens in=0 out=0` provider failure **in scope** as its own hardening, or **out of scope** once hollow name/ANALYSIS context fails fast (treat long empty provider waits as a symptom)?
3. Confirm product rule: ANALYSIS token vector matching must use the **same** label-or-code resolution rules as consult scoring (vs requiring grades to store full live labels only).

— Chuckles

### Files changed (plan vs actual)

_No product commit trail on the parent — the epic worktree only carries a `merge-resume(AST-1193)` stack-onto commit (2026-08-05 16:38) and the `docs(AST-1163)` archive commit. Implementation landed entirely via the two sub-issues below._

## Sub-issues

### AST-1192 — Artifact hop candidate token view (names)
_Archived: 2026-08-07 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1192/artifact-hop-candidate-token-view-names-issues-while-running · Status at archive: Archive · Project: Astral Artifacts · Assignee: ada · Priority / estimate: None / — · Blocked by / blocks / related: parent: AST-1163_

#### What this implements

Ensure artifact `do_task` / preview resolve paths feed the walkable candidate token view (name columns + library blobs) so `{$FIRST_NAME}` / `{$LAST_NAME}` (and siblings) resolve for `anticipate_scan` and shared hops; include debug found/recorded for name-token outcomes on the touched path. Does **not** own ANALYSIS formatter matching (sibling).

#### Acceptance criteria

- [X] For a candidate with non-empty first/last name columns, running `anticipate_scan` (or Manage Tasks preview for that task with the same candidate) substitutes non-empty `{$FIRST_NAME}` and `{$LAST_NAME}` — no empty-token warnings for those names on that run.
- [X] A debug-gated run of the fixed path shows per-index found/recorded lines for candidate identity (name-token outcomes).
- [X] Susan can reproduce: after this child lands, a Generate Artifacts / `anticipate_scan` run on a candidate with names no longer logs empty `{$FIRST_NAME}` / `{$LAST_NAME}` from missing token-view wiring.

#### Boundaries

Does **not** own ANALYSIS_* vector↔rubric match parity (sibling). Does **not** harden provider timeouts / blank errors (**AST-1164**). Does **not** re-author prompt prose.

#### In scope / considered but excluded

In scope: `pattern.config.config-block` (TOKEN_SOURCES / existing token registry remain config authority; no parallel token maps); `astral.config.config-source-of-truth` (name paths stay on TOKEN_SOURCES; no hardcoded path sets in core); `astral.agent.do-task-delegation` (prompt assembly / resolve stays in `do_task` — token-view cutover at resolve boundary); `astral.standards.debug-contract-gated` (Style D found/recorded for name-token outcomes only when `debug=True`); `astral.standards.in-scope-only` (only artifact hop + Manage Tasks preview resolve wiring for names); `astral.standards.dry-and-focused-functions` (reuse `build_candidate_token_view`; one private helper for row-vs-raft); `astral.standards.logging-via-utils` (debug via `_PrefixedLogger` helpers); `astral.layers.import-direction` (lazy candidate import inside `agent.py` — existing cycle break); `astral.standards.no-cross-contamination` (do not convert `_candidate_data_for_job` blob consumers to token view).

Considered but excluded: `astral.agent.grade-vector-validation` (ANALYSIS formatter match parity is AST-1193's `_format_analysis_phase_text`); `astral.patterns.coat-check-never-store-empty` (hollow ANALYSIS / provider failure persistence is AST-1193 / AST-1164); `astral.batch.claim-process-release` (no new dispatch lifecycle; hop claim path unchanged); `astral.dispatch.run-next-is-chain-authority` (`run_next` / hop order unchanged); `astral.debug.no-repo-root-artifacts-dir` (no spike/debug file output in this ticket); `astral.git.engineer-test-tree-ban` (no `tests/` or bible edits — Betty).

#### Notes for planning

Name columns + `build_candidate_token_view` cutover (AST-1014) is the baseline — wire artifact hops to that view. Root cause: `do_task` and `preview_task_prompt` still pass raw `candidate_data` blobs; dispatch rafts set `astral_candidate_id` without copying `first`/`last` onto ctx.

#### Files Changed (planned)

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

#### Stage 1: `do_task` feeds token view + name-token debug

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

#### Stage 2: Manage Tasks preview uses the same token view

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

#### Self-Assessment

**Scope:** `Single-Component` — two core resolve entry points (`do_task`, `preview_task_prompt`) cut over to the existing AST-1014 token view; no new modules, no config keys, no UI.

**Conf:** `high` — root cause is the empty-name log (`path=first` / `path=last` against a blob that has no top-level `first`/`last`); admin preview already demonstrates the correct `build_candidate_token_view` pattern.

**Risk:** `Medium` — `do_task` is shared by all agent hops; wrong view construction could blank contact/context tokens. Mitigated by loading the full candidate row (same helper admin uses) and leaving `_candidate_data_for_job` blob consumers untouched.

#### Rules check (ASTRAL_CODE_RULES)

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

#### Plan review — Joan (plan-rubric.v1, APPROVED)

**Traceability:** AC1→S1 (`do_task`) + S2 (`preview_task_prompt`) — both surfaces AC1 names; AC2→S1 step 4 (Style D found/recorded for candidate identity); AC3→S1+S2 (Susan's replay). Parent AC2 and the ANALYSIS half of parent AC3/AC4 are N/A–boundary ("Does not own ANALYSIS_* vector↔rubric match parity (sibling)"). No orphan stages: S1→parent Functional scope bullets 1 and 3, S2→AC1's "or Manage Tasks preview" clause. Considered: full active corpus swept (65 leaves — 18 universal + 30 scoped considered, 17 scoped excluded on layer/path predicates). All considered statutes score `conforms`.

**Verification notes:** The cutover's central risk is that `build_candidate_token_view` returns a **narrow** 8-key dict (`src/core/candidate.py:70-84`: `first`, `last`, `full`, `pronouns`, `contact`, `context`, `artifacts`, `_astral_candidate_id`), so replacing the raw blob as `cd` could blank tokens on every agent hop — which the parent forbids ("Must not break other artifact hops that share the same token resolve / job_context builders"). Joan checked every candidate-source consumer against that key set: every `TOKEN_SOURCES` candidate dot-path resolves under `contact.*`, `context.*`, or `artifacts.*`, plus top-level `first` / `last` / `full` (`src/utils/config.py:5102-5138`) — nothing walks a top-level blob key the view drops; `format_base_resume_for_token` / `resolve_resume_structure` are view-safe; `build_job_token_context` (`src/core/consult.py:840-865`) uses only `cd["_astral_candidate_id"]`, `_format_analysis_phase_text(..., cd)`, and `resolve_resume_structure(cd)` — view-safe. So the change is **strictly additive** for token resolution. It also fixes a second live bug as a side effect: `_pronoun_preference_key` reads top-level `pronouns` (`src/utils/config.py:5272-5278`, moved to a column by AST-1014), which the raw blob no longer carries, so `{$THEY}` / `{$THEIR}` / etc. have been silently falling back to the default on every `do_task` path — inside this child's "(and siblings)" identity-token scope, not scope creep, flagged so Betty and Radia expect the change.

Root cause and the two edit sites match the plan exactly: `src/core/agent.py:1856` `cd = (ctx.get("candidate_data") or {}) if ctx else (candidate_data or {})`, then the `requires_candidate_key` check at 1858 and the `company_search_terms` overlay at 1862-1870; and `src/core/candidate.py:1392` `cd = candidate.get("candidate_data") or {}` with the overlay at 1402-1408 already doing `cd = dict(cd)`. The load-bearing assumption — that `ctx` carries `astral_candidate_id` on the artifact dispatch path — holds: `src/core/consult.py:2198-2199` derives `candidate_data` via `tracker._candidate_data_for_job(aid)`, which resolves job→company→`candidate_id`→row (`src/core/tracker.py:129-147`) and returns `{}` when that chain breaks (caller skips the job on empty); lines 2214-2218 then set `astral_candidate_id` from the same derivation, so any job that actually reaches `do_task` has it — branch (c) fires. Branch (f) correctly preserves today's behavior for the deliberately synthetic ctx at `src/core/candidate.py:2362` ("no astral_candidate_id — do not load a real candidate").

**Findings (all `discuss`):**
- The `requires_candidate_key` guard goes quiet. Branches (c) and (d) always return a populated-shape dict, so `if task_config.get("requires_candidate_key") and not cd` (`src/core/agent.py:1858`) can no longer fire once a row loads — even when that row's blob is empty, i.e. an all-empty view. Losing that warning in the exact failure family this epic exists to surface is worth avoiding: consider testing a meaningful field (any of `first` / `contact` / `context` non-empty) rather than dict truthiness.
- Make the chosen branch visible at UAT. The debug line reports whether names came out empty but not which of (c)–(f) produced the view. `astral_candidate_id` and `candidate_data` are derived independently; they agree today, but if they ever diverge (a batch row without `company`) the helper silently falls back to (f) with no signal beyond "empty — name tokens." One branch tag on the `found` detail line makes that a one-line diagnosis instead of a re-run.
- Branches (d)/(e) hardcode the view's key names (`"first" in ctx` / `"contact" in candidate_data` / `"candidate_data" not in candidate_data`) to detect shape at a distance — if the view's keys change, these branches misroute silently. A tiny is-view predicate beside the helper in `candidate.py` would keep the shape contract in one place.

**Acceptable (not a finding):** Loading the candidate row per `do_task` adds a DB read per hop, including each `run_next` hop — deliberate, mirrors the existing refresh-per-hop pattern, negligible beside an LLM call.

Self-assessment affirmed: `Risk: Medium` for touching shared `do_task` is right; leaving `_candidate_data_for_job` blob consumers untouched is the correct call (feeds resume-structure paths that need blob shape). `Conf: high` is earned; the empty-name warnings name `path=first` / `path=last` against a blob that structurally cannot carry them.

#### QA test manifest — Betty

**Publish:** `origin/sub/AST-1163/AST-1192-artifact-hop-candidate-token-view-names` @ `64125186` · **Betty SHA:** `origin/tests` `8d2ea872`

Classification — existing coverage (bible-backed): AST-1014 token-view / library (`TestAst1014CandidateLibrary`) remains the baseline for `build_candidate_token_view` itself, not re-run as this ticket's acceptance. Broken / obsolete: none — additive resolve-boundary cutover; `_candidate_data_for_job` blob consumers unchanged, no existing integration scenario asserted artifact-hop name-token wiring. Gaps covered this pass: helper branches + `do_task` name resolve on dispatch raft + Style D found/recorded + Manage Tasks preview columns→names.

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1192TokenViewForDoTask \
  tests/component/core/test_candidate.py::TestPreviewTaskPrompt::test_preview_resolves_names_from_columns_not_blob \
  -q
```

1. `TestAst1192TokenViewForDoTask` — `_token_view_for_do_task` load-by-id / full-row ctx / already-view / raw-blob fallback; `anticipate_scan` dispatch raft substitutes `{$FIRST_NAME}`/`{$LAST_NAME}`; `debug=True` Style D `do_task.candidate_token_view` found/recorded.
2. `test_preview_resolves_names_from_columns_not_blob` — `preview_task_prompt` resolves names from columns when blob has none.

Pass criterion: pytest green on the two paths above — not zero-arg harness / branch-lock gate. Bible: `docs/test-bible/core/agent.md` @ `04a061bba871fdddce61c0df9908d76d51acf3db`.

#### Build review — Radia (code-rubric.v1, DISCUSS)

**Publish ref:** `64125186` · **Build tip:** `08d9a966fb4db7dd013eb419cb0912588b3575e0`

Full active corpus (63 leaves — 18 universal + 45 scoped) swept against `git diff origin/dev...origin/sub/AST-1163/AST-1192-artifact-hop-candidate-token-view-names`. No violations. `src/` footprint is exactly the two planned files (`agent.py` +57/-1, `candidate.py` +2/-1); `_candidate_data_for_job` / `tracker.py` correctly untouched. Role boundaries clean per commit (`code()` → `src/` only, `test()` → `tests/`+`docs/test-bible/` only, `docs()` → `docs/features/` only). Implementation matches the plan doc literally — `_token_view_for_do_task` branch order (id-load → full-row ctx → already-view → raw fallback), overlay sequencing preserved, Style D `do_task.candidate_token_view` found/recorded gated under existing `if debug:` block, `preview_task_prompt` one-line swap with no new import. Joan's `plan-rubric.v1` r1 (APPROVED) is attached; her 3 `discuss` items are carried forward below since the shipped code still exhibits them as described (her 4th point, DB-read-per-hop, she marked `acceptable` — concur).

Pattern conformance: `astral.config.config-source-of-truth`, `astral.agent.do-task-delegation`, `astral.standards.debug-contract-gated`, `astral.standards.in-scope-only`, `astral.standards.dry-and-focused-functions`, `astral.standards.logging-via-utils`, `astral.layers.import-direction`, `astral.standards.no-cross-contamination` all score `conforms`. `pattern.config.config-block` (also cited) does not resolve to any id in the active corpus — stale shorthand, advisory only, not a block.

**Findings (discuss, confirmed present as shipped — same 3 Joan flagged at plan time):**
- `requires_candidate_key` guard goes quiet (branches (c)/(d) always return a populated-shape dict).
- No branch tag on the debug `found` line (which of the 4 branches produced the view is not surfaced).
- Branches (d)/(e) hardcode `build_candidate_token_view`'s key names to detect shape at a distance.

**What's solid:** Debug contract textbook — gated, `index 1/1` correctly not inventing a batch counter, `found`/`recorded` via `DEBUG_DETAIL_PREFIX` helpers, no full-blob logging. Cycle-break comment on the lazy `candidate` import is accurate. `_candidate_data_for_job` boundary honored exactly as planned. Frame diff: none — implementation matches the plan doc's Files Changed / Stage 1 / Stage 2 as written.

#### Resolution (2026-08-05)

Resolve-child vs `[code-rubric] revision=1` (DISCUSS):

1. **discuss / requires_candidate_key** — Guard now uses `_candidate_identity_material_present(cd)` (non-empty `first`/`last`/`full`, or non-empty string values under `contact`/`context`) instead of dict truthiness, so an all-empty 8-key view still warns.
2. **discuss / branch tag** — Style D `found` detail appends `branch=<load_by_id|full_row_ctx|already_view|raw_blob>` from `_token_view_branch_last` set in `_token_view_for_do_task`.
3. **discuss / shape probes** — `is_candidate_token_view` + `is_candidate_row_with_name_columns` live beside `build_candidate_token_view` in `candidate.py`; helper branches (d)/(e) use those predicates.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/agent.py` | `_token_view_for_do_task` helper; wire before `requires_candidate_key` check + overlay; Style D found/recorded | `0ab2f6a86` — +57/-1; discuss-3 fixes (identity-material guard, branch tag, shape predicates) folded in before resolve |
| ✓ | `src/core/candidate.py` | `preview_task_prompt` → `build_candidate_token_view(candidate)` | `08d9a966f` — +2/-1 |
| | _tests_ | helper branches / dispatch-raft name resolve / Style D / preview names | `8d2ea872e` — `TestAst1192TokenViewForDoTask` + `test_preview_resolves_names_from_columns_not_blob`; bible `docs/test-bible/core/agent.md` |

### AST-1193 — ANALYSIS token vector↔rubric match parity
_Archived: 2026-08-07 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1193/analysis-token-vectorrubric-match-parity-issues-while-running · Status at archive: Archive · Project: Astral Artifacts · Assignee: hedy · Priority / estimate: — · Blocked by / blocks / related: parent: AST-1163_

#### What this implements

Make `{$ANALYSIS_JD}` / `{$ANALYSIS_DO}` / `{$ANALYSIS_GET}` / `{$ANALYSIS_LIKE}` format every persisted consult grade vector into a non-empty CONSIDER / rubric blob / ANALYSIS RESULT block for artifact hops (starting with `anticipate_scan`). Prefer the live rubric via the **same** label-or-code match scoring already uses; when live misses a full-label vector that still appears on the job-carried analysis-time `*_rubric` snapshot (AST-1063), resolve identity from that snapshot and pull `content` from live by code so grades that already passed scoring are not silently skipped. Add debug-gated found/recorded counts per ANALYSIS phase. Does **not** own candidate name token view (**AST-1192**), provider timeout hardening (**AST-1164**), or rubric regeneration.

#### Diagnosis (why `'Compensation'` misses today)

Verified in code against the parent log (~35 full human labels across all four ANALYSIS phases — not 2-char codes):

1. **`_format_analysis_phase_text`** (`consult.py`) loads criteria only from live `rubric_criteria_for_task(cid, owner)`. It never reads the job-carried `jd_rubric` / `do_rubric` / `get_rubric` / `like_rubric` snapshots that `render_verdict` / evaluate batch already persist via `_rubric_snapshot_for_job_data` (AST-1063).
2. Match today is **label-only** (stripped). Scoring helpers `_lookup_rubric_reason_for_grade` / `_importance_for_label` already accept stripped label **or** uppercased code (AST-707). That drift is real and worth fixing for code-shaped vectors, but **every** unmatched vector in the parent log is a full label (`'Compensation'`, `'Program Scope'`, …). The code disjunct cannot fire for those strings (`_CODE_SUFFIX` / `_vector_labels_map` treat codes as two letters). **Stage 1 alone is a no-op for the observed run.**
3. Grades that persisted through AST-1155 `_require_complete_grade_set` had vectors equal to the **then-live** rubric labels. A 100% miss against **now-live** criteria (with non-empty criteria — otherwise the formatter returns `""` before per-vector warnings) fits **post-grade rubric label change** (or a different current criteria set for that owner), not code-vs-label formatting.
4. Snapshots intentionally **omit `content`** (list-header shape). So snapshot-only formatting cannot supply the rubric blob; content must still come from live (by code) when possible.

Local `data/astral.db` in this worktree has zero jobs/candidates — diagnosis is from code + parent log shapes, not a live row dump.

⚠️ **Decision (AC4 delivery):** Prefer live label-or-code first. On miss, match the grade vector to the job-carried phase `*_rubric` snapshot by the same label-or-code helper; use snapshot `label`/`code` for identity; resolve `content` from live by code (or label). If live has no content for that code, still emit `CONSIDER: {title}\n\nANALYSIS RESULT: …` so the token is non-empty. Do **not** regenerate rubrics. Do **not** invent fuzzy label matching. (Escalate path rejected for this plan: parent AC4 requires the reproduce case to stop logging empty ANALYSIS from these unmatchable vectors; snapshot identity + live content is the mismatch class that closes it without rewriting `rubric_vector`.)

#### Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Add shared `_find_rubric_criterion`; refactor scoring helpers; ANALYSIS formatter: live label-or-code + snapshot fallback + live content-by-code; phase iteration from `JOB_TOKEN_CONFIG["analysis_phases"]`; Style D found/recorded via local debug logger handle | core |
| `src/core/agent.py` | Pass `debug` from `do_task` into `_job_context_for_call` → `build_job_token_context(..., debug=debug)` | core |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| Candidate name / `build_candidate_token_view` / `{$FIRST_NAME}` / `{$LAST_NAME}` | AST-1192 |
| Provider timeout / blank `error=` / zero-token classification | AST-1164 |
| `JOB_TOKEN_CONFIG` phase key declarations / grades_key / owner task keys | unchanged (read-only) |
| Rubric regeneration / `rubric_vector` writes / widening `_rubric_snapshot_for_job_data` to store `content` | out of epic |
| `_grade_set_vector_diff` / IncompleteGradeSetError / pass thresholds | out of scope |
| Manage Tasks prompt prose | out of epic |
| `tests/`, `docs/test-bible/**` | Betty |

#### Stage 1: Shared label-or-code criterion lookup (DRY — not the AC4 fix alone)

**Done when:** Scoring helpers and the ANALYSIS formatter share one `_find_rubric_criterion` with the AST-707 predicate. A grade whose `vector` is a 2-char code that scoring would accept matches via this helper. **This stage does not by itself close AC4 for the parent log** (full-label vectors); Stage 3 does.

1. In `src/core/consult.py`, immediately after `_strip_code`, add:

   ```python
   def _find_rubric_criterion(rubric_criteria: list, vector_label: str):
       """Return the criterion dict matching vector by stripped label or code (AST-707 / AST-1193)."""
       target = _strip_code((vector_label or "").strip())
       t_upper = target.upper()
       for item in rubric_criteria or []:
           if not isinstance(item, dict):
               continue
           lab = _strip_code(str(item.get("label") or "").strip())
           code = str(item.get("code") or "").strip().upper()
           if lab != target and code != t_upper:
               continue
           return item
       return None
   ```

   Match rules must be **byte-for-byte** the same predicate as today's loops in `_lookup_rubric_reason_for_grade` and `_importance_for_label`. Do **not** add fuzzy / casefold label matching or substring match.

2. In `_lookup_rubric_reason_for_grade`, replace the open match loop with `_find_rubric_criterion(rubric_criteria, vector_label)`. Keep grade-description resolution and `ValueError` messages unchanged.

3. In `_importance_for_label`, replace the open match loop with `_find_rubric_criterion(rubric_criteria, vector_label)`. Keep importance / default / `ValueError` behavior.

4. Do **not** yet change `_format_analysis_phase_text` beyond what Stage 3 specifies (Stage 3 owns the formatter body). Stage 1 may leave the formatter on the old loop until Stage 3 lands in the same build sequence — implement Stage 1 helpers first, then Stage 3 switches the formatter to the shared finder + snapshot path in one coherent edit if committing stages separately: **Stage 1 commit = helper + scoring refactors only; Stage 3 commit = formatter.**

#### Stage 2: Debug found/recorded per ANALYSIS phase + wire from `do_task`

**Done when:** A `do_task` hop with `debug=True` that builds job token context emits Style D per-index headers for each ANALYSIS phase with found grade counts vs recorded vector counts. `debug=False` emits **no** new debug-contract lines and **does not** lower the shared `src.core.consult` module logger's debug state.

1. Change `build_job_token_context` signature to:

   ```python
   def build_job_token_context(
       job: Dict[str, Any], candidate_data: dict, *, candidate_id: str = "", debug: bool = False
   ) -> Dict[str, str]:
   ```

2. Debug handle rule (single instruction — no alternatives): obtain a **local** logger for contract lines with `log = get_logger(__name__, debug_flag=debug)` (same pattern as other gated helpers). Emit `log.debug_index` / `log.debug_detail` only through that handle. **Do not** call `logger.set_debug_flag(debug)` (or `False`) inside `build_job_token_context` or `_format_analysis_phase_text` — that setter lowers the shared module logger from DEBUG to INFO when `debug=False` and would clobber other consult debug runs in-process.

3. Change `_format_analysis_phase_text` to accept `*, debug: bool = False, job_id: str = ""`. Pass `debug=debug` and `job_id=str(job.get("astral_job_id") or "")` from the builder. Inside the formatter, use the same local-handle rule: `log = get_logger(__name__, debug_flag=debug)`.

4. Phase list authority: in `build_job_token_context`, replace the hardcoded `("ANALYSIS_JD", "ANALYSIS_DO", "ANALYSIS_GET", "ANALYSIS_LIKE")` iteration with:

   ```python
   phase_tokens = tuple((JOB_TOKEN_CONFIG.get("analysis_phases") or {}).keys())
   ```

   Use `phase_tokens` for both formatting and debug `index`/`total` (`total=len(phase_tokens)`). Meteorite override continues to mutate owner/artifact for `ANALYSIS_JD` only inside the formatter — it does not change the key set.

5. After computing the joined blocks string for a phase (including early-return empty cases), when `debug=True`, emit via the local handle:

   - `log.debug_index(func="_format_analysis_phase_text", index=<1-based among phase_tokens>, total=len(phase_tokens), identifier=f"{job_id}:{phase_token}", outcome="formatted" if text else "empty")`
   - `log.debug_detail(f"found_grades={found} recorded_vectors={recorded} live_criteria={n_live} snapshot_criteria={n_snap}")`

   Counts:
   - **found_grades:** grade dicts with non-empty stripped `vector`
   - **recorded_vectors:** CONSIDER blocks appended
   - **live_criteria** / **snapshot_criteria:** lengths of the lists used for that phase (0 when missing)
   - Early exits still emit index + detail when `debug=True`

   Counts only — no full blobs / token text.

6. In `src/core/agent.py`: add `debug: bool = False` to `_job_context_for_call`; pass `debug=debug` into the builder; at the `do_task` call site pass `debug=debug`.

7. Preview / adhoc callers may keep default `debug=False`. Do not invent UI debug toggles.

8. Coat-check: do **not** persist empty ANALYSIS strings into job_data / artifacts as success.

#### Stage 3: ANALYSIS formatter — live first, snapshot identity fallback (AC4)

**Done when:** For a job with persisted `*_grades` and matching phase `*_rubric` snapshot labels (even when live criteria labels have drifted), each `{$ANALYSIS_*}` token is non-empty and includes CONSIDER / ANALYSIS RESULT for those vectors. Live label-or-code hits still use live `content`. Debug counts from Stage 2 show `recorded_vectors` tracking found grades on that path.

1. In `_format_analysis_phase_text`, keep meteorite phase-cfg merge and grades load. Derive snapshot key from `grades_key`: if `grades_key` ends with `"_grades"`, snapshot key is `grades_key[:-7] + "_rubric"` (e.g. `do_grades` → `do_rubric`, `jd_grades` → `jd_rubric`). Read `snapshot = job_data.get(snapshot_key)`; treat non-list as `[]`.

2. Load live `rubric_criteria` via `rubric_criteria_for_task(cid, owner)` when owner + cid present; else `[]`. **Remove** the early `if not rubric_criteria: return ""` — empty live must not abort formatting when grades + snapshot can still produce blocks. Keep early `return ""` only for missing phase cfg or empty/non-list grades.

3. For each grade dict with non-empty `vector_label`:

   a. `criterion = _find_rubric_criterion(live_criteria, vector_label)`  
   b. If `criterion is None` and snapshot is a non-empty list: `snap_row = _find_rubric_criterion(snapshot, vector_label)`  
      - If `snap_row` is not None: set `title = str(snap_row.get("label") or vector_label).strip()` and `code = str(snap_row.get("code") or "").strip()`; then `criterion = _find_rubric_criterion(live_criteria, code) if code else None` to obtain live `content` (and prefer live label for title when that live hit exists). If live content lookup misses, keep `criterion = None` but still treat as a **snapshot identity hit** (see c).  
   c. Emit rules:
      - **Live hit (a):** `title = str(criterion.get("label") or vector_label).strip()`; `rubric_blob = str(criterion.get("content") or "").strip()`; append CONSIDER / blob / ANALYSIS RESULT as today.
      - **Snapshot identity hit with live content (b with live criterion):** same block shape using live content; title from live label if present else snapshot label.
      - **Snapshot identity hit without live content:** append  
        `CONSIDER: {title}\n\nANALYSIS RESULT: {letter} ({conf_s} confidence)`  
        (blank line where blob would be — token still non-empty; title from snapshot).
      - **Neither live nor snapshot:** keep existing warning  
        `"_format_analysis_phase_text: no rubric criterion for vector %r (phase=%s)"`  
        and `continue`.

4. Letter / confidence formatting and `\n\n` join unchanged.

5. Pass `job_data` snapshot path only — do **not** widen `_rubric_snapshot_for_job_data` to persist `content` in this ticket.

6. `build_job_token_context` iterates `phase_tokens` from Stage 2 and passes `debug` / `job_id` into the formatter.

#### Self-Assessment

**Scope:** `Single-Component` — `consult.py` ANALYSIS formatting + shared criterion finder + snapshot fallback; thin `debug` thread through `agent._job_context_for_call`.

**Conf:** `Medium` — Stage 1 DRY is certain; AC4 delivery rests on job-carried `*_rubric` snapshots existing for the failing jobs (AST-1063 write path) and on snapshot labels still matching persisted grade vectors after live drift. If a job lacks `*_rubric`, fallback cannot help and that case needs a separate escalate.

**Risk:** `Medium` — snapshot fallback can attach a live content blob by code after label drift (intended); wrong-code collisions would mis-attach content, same class of risk as scoring's code match. Emitting CONSIDER without blob when live content is gone is weaker context but still non-empty (AC4).

#### Code rules check

- §1.3 DRY: one `_find_rubric_criterion` for scoring, live ANALYSIS, and snapshot lists.
- §1.5.1 debug-contract-gated: local `get_logger(..., debug_flag=debug)` only; never lower shared module debug via `set_debug_flag(False)`.
- §1.4 / §2.1: phase iteration from `JOB_TOKEN_CONFIG["analysis_phases"]` keys; no second hardcoded phase tuple / magic `total=4`.
- §2.3.1: formatter consumes persisted grades; no decode/validation change.
- Coat-check: no new empty ANALYSIS persistence.
- Boundaries: no name-token work, no AST-1164, no rubric regeneration, no test-tree edits.

#### Revisions

Revision 1 — 2026-08-05  
Driven by: Joan `[plan-discuss] round=1 concern` (fix-now: label-or-code alone is a no-op for full-label parent-log vectors / AC4; discuss: `set_debug_flag(False)` clobber; discuss: hardcoded phase tuple + `total=4`).  
Changes: Added Diagnosis + AC4 Decision (live first, job-carried `*_rubric` snapshot identity fallback, live content-by-code). Stage 1 scoped as DRY only. Stage 2 uses local debug logger handle (never lower shared flag) and phase keys from `JOB_TOKEN_CONFIG`. New Stage 3 implements snapshot fallback. Conf `high` → `Medium`.

#### Build review — Radia (code-rubric.v1, CLEAN)

**Publish ref:** `64ea1d86` · **Tip:** `29c1af56`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `5a7b1f39` | Shared `_find_rubric_criterion`; scoring helpers refactored |
| 2–3 | `29c1af56` | ANALYSIS live-first + `*_rubric` snapshot fallback; Style D found/recorded; `do_task` debug thread |

Full active corpus (63 leaves — 18 universal + 45 scoped) swept in-session against `git diff origin/dev...origin/sub/AST-1163/AST-1193-analysis-token-vector-rubric-match-parity`. No violations, no stragglers. `src/` footprint is exactly the two planned files (`consult.py` +112/-49 net, `agent.py` +6/-2); role boundaries clean per commit.

**Plan adherence:** Implementation matches Stage 1–3 literally — `_find_rubric_criterion` placed immediately after `_strip_code`, both scoring helpers refactored onto it with behavior byte-for-byte preserved (first-match-then-decide, unchanged `ValueError` messages), `_format_analysis_phase_text` live-first / snapshot-identity-fallback / live-content-by-code / blob-less-but-nonempty exactly per Stage 3 step 3's four emit rules, `phase_tokens` sourced from `JOB_TOKEN_CONFIG["analysis_phases"]` (no second hardcoded tuple, no `total=4`), debug via a **local** `get_logger(__name__, debug_flag=debug)` handle only (grepped the diff for `set_debug_flag` — zero hits). Joan's `plan-rubric.v1` r1 verdict (APPROVED) is attached with 2 open `discuss` items from her final pass — both closed by the shipped code, not carried forward:

- Her snapshot-key-derivation-coupling discuss is answered directly: `_analysis_phase_rubric_snapshot_key`'s docstring states "Couples to `grades_key == f\"{save_prefix}_grades\"` — same stem both sides today" — exactly the comment she suggested "so the next person's life [is] easier."
- Her residual-AC4-precondition discuss (snapshot absent on pre-AST-1063 jobs) isn't a code gap — it's a UAT-time question already instrumented via the `snapshot_criteria=` debug count Stage 2 emits, per her own escalate-path framing.

**Pattern conformance:** all cited ids (`astral.agent.grade-vector-validation`, `astral.config.config-source-of-truth`, `astral.standards.dry-and-focused-functions`, `astral.standards.debug-contract-gated`, `astral.patterns.coat-check-never-store-empty`, `astral.standards.logging-via-utils`, `astral.standards.in-scope-only`) score `conforms` via the full sweep. `grade-vector-validation`'s literal statement (do_task schema/grade-value validation) isn't touched by this diff — the citation covers the plan's extended reading (grade-vector *matching* for rendering), which Joan's traceability already accepted at Plan Approved; noting the stretch for the record, not as a finding.

**Cross-ticket note (not a finding):** this branch inherited `test(AST-1192)` / `test(AST-1189)` / `test(AST-1190)` commits via `merge-tests` (stacked-sibling test lineage in this epic worktree) but none of AST-1192's `src/` changes — `tests/component/core/test_agent.py::TestAst1192TokenViewForDoTask` would fail standalone on this branch's `agent.py` (no `_token_view_for_do_task` here). Expected/by-design until `merge-child` lands both siblings on `ftr/AST-1163` in order; not something AST-1193's own diff introduced or can fix.

**What's solid:** Debug contract textbook — `index`/`total` from the config-authority phase map, `found_grades`/`recorded_vectors`/`live_criteria`/`snapshot_criteria` counts only (no blob spam), early-return paths still emit when `debug=True`. Snapshot-fallback emit shape is byte-identical to the existing block string with `rubric_blob == ""`, so the "blob-less but non-empty" path shares one code path rather than forking — exactly what Joan flagged as load-bearing for AC4. Frame diff: none — implementation matches the plan doc's Files Changed / Stage 1 / Stage 2 / Stage 3 as written.

#### Resolution

**Date:** 2026-08-05  
**Radia:** `[code-rubric] revision=1` — **Overall: CLEAN** (no fix-now / discuss / advisory to land).  
**Action:** No product changes. Resolution commit records intake of Radia's doc-only review tip and §9a clean before User Testing.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/consult.py` | Stage 1 `_find_rubric_criterion` + scoring refactor; Stage 2 debug thread + phase-key authority; Stage 3 live-first/snapshot-fallback/live-content-by-code formatter | `5a7b1f39b` (Stage 1, +40/-40) + `29c1af565` (Stages 2–3, +107/-… net across both files) |
| ✓ | `src/core/agent.py` | Thread `debug` from `do_task` into `_job_context_for_call` → `build_job_token_context(..., debug=debug)` | `29c1af565` (+8/-… ) |
| | _tests_ | ANALYSIS live/snapshot match + debug coverage | `d15b790fa` — `test(AST-1193): ANALYSIS live/snapshot match + debug coverage`; bible per Betty manifest |
