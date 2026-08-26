# AST-1493 — METEORITE company state + stem ensure + track detection

**Linear:** [AST-1493](https://linear.app/astralcareermatch/issue/AST-1493/meteorite-company-state-stem-ensure-track-detection-create-meteorite)  
**Parent:** [AST-1484](https://linear.app/astralcareermatch/issue/AST-1484/create-meteorite-companies-per-email-address) — Create meteorite companies per email address  
**Publish ref:** `sub/AST-1484/AST-1493-meteorite-company-state-stem-ensure-track`

Register `COMPANY_STATES["METEORITE"]` (roster-inert like `IGNORE`), flip `METEORITE_CONFIG["company_state"]` to it, expand lazy-ensure so a Ruth (or caller) stem + candidate idempotently yields `{stem}-{candidate_id}` in **METEORITE**, and broaden meteorite-track detection to company state plus the legacy `meteorite-` short_name prefix. Style D on ensure when `debug=True`. Does **not** own Ruth stem discernment or inbox/gaze land wiring (siblings AST-1494 / AST-1495).

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/utils/config.py` — modified — `COMPANY_STATES` METEORITE; `METEORITE_CONFIG` company_state + stem templates + meteorite-self literal.
- `src/core/meteorite.py` — modified — ensure by stem+candidate into METEORITE; broaden track detection via company state (+ legacy prefix); Style D on ensure.

All Files Changed / Stages stay inside that set.

**Out of scope (siblings / later):**

- Ruth land/`qualify_meteorite` enrichment prompts + RESPONSE stem field — **AST-1494** (`consult.py` / `agent.py` / TASK_CONFIG stem units).
- Inbox / `gaze_email` / `gazer` CONTENT→stem wiring; `create_meteorite_job` / `land_meteorite` attach-when-stem-present units; optional METEORITE company list/nav — **AST-1495** (shared `meteorite.py` land/create attach only; not ensure/track owned here).
- Bulk migration of historical `IGNORE` `meteorite-{candidate}` rows (parent AC / this ticket AC7 — leave in place).
- `src/data/database.py` claim SQL (prefix exclusion stays for legacy `meteorite-%`; new stem companies are roster-inert via empty `COMPANY_STATES["METEORITE"]` batch criteria — no claim trigger).
- `JOBS_RECOMMENDED_METEORITE_SECTION["company_prefix"]` / Recommended UI partition (still prefix-based; email-stem short_names are an AST-1495 / follow-on UI concern, not this ticket).

**Depends on:** nothing blocked — Bang !! first child; siblings wait on this ensure/track API.

**AC partition (this ticket):** Parent AC1 (METEORITE state + new placeholders), AC2–AC4 (ensure shapes for email / meteorite-self / slug stems — API ready; Ruth/inbox supply stem later), AC6 (default `meteorite-{candidate}` still ensured, now in METEORITE), AC7 (no bulk migrate), AC8 (Style D on ensure). Parent AC5 (email land attach under ensured company) → AST-1495. Track carve-out half of parent AC6 → this ticket’s `is_meteorite_company` widening.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `COMPANY_STATES["METEORITE"] = {}`; flip `METEORITE_CONFIG["company_state"]` → `"METEORITE"`; add stem template keys + `meteorite_self` / default-stem literals; asserts | utils |
| `src/core/meteorite.py` | Optional `stem=` on `ensure_meteorite_company`; format via config templates into METEORITE; widen `is_meteorite_company` (state + legacy prefix); Style D stem/company/create-vs-reuse | core |

## Stage 1: Config — METEORITE company state + stem templates

**Done when:** `COMPANY_STATES` contains `METEORITE` with empty config `{}` (no `batch_criteria` — roster-inert twin of `IGNORE`). `METEORITE_CONFIG["company_state"]` is `"METEORITE"` and passes the existing `assert … in COMPANY_STATES`. Stem template / self / default-stem literals exist and are asserted so default stem + template equals today’s `meteorite-{candidate_id}` shape. No core or UI changes yet.

1. In `src/utils/config.py`, inside `COMPANY_STATES`, add immediately after `"IGNORE": {},`:

```python
    "METEORITE": {},  # AST-1493: roster-inert meteorite placeholders (stem-keyed); no batch_criteria
```

⚠️ **Decision:** Empty `{}` like `IGNORE` — parent Functional scope #1 and Architectural note: METEORITE is roster-inert (no gaze/prefilter claim criteria). Do **not** add `METEORITE` edges to `ASTRAL_CONFIG["company_state_transitions"]`; companies are **created into** METEORITE via ensure/`save_company`, same as today’s IGNORE placeholders — not transitioned there by roster.

2. In `METEORITE_CONFIG` (same block as today’s `short_name_prefix` / `short_name_template` / `company_state`), keep existing keys and change / add:

| Key | Value | Role |
|-----|--------|------|
| `company_state` | `"METEORITE"` (was `"IGNORE"`) | New inserts from ensure |
| `short_name_prefix` | `"meteorite-"` (unchanged) | Legacy track fallback + DB claim exclusion readers |
| `short_name_template` | `"meteorite-{candidate_id}"` (unchanged) | Default / no-stem shape; keep for existing readers |
| `stem_short_name_template` | `"{stem}-{candidate_id}"` | Format with `stem=` + `candidate_id=` |
| `default_stem` | `"meteorite"` | Slack/Contact / callers that omit stem |
| `meteorite_self_stem` | `"meteorite-self"` | Literal Ruth may return (sibling AST-1494); ensure treats like any other stem |

Update the block comment above `METEORITE_CONFIG` to note AST-1493: company state METEORITE + stem-keyed short_names; lazy-ensure still never bulk-seeds at server start.

3. After the existing `assert METEORITE_CONFIG["company_state"] in COMPANY_STATES`, add asserts (same style as neighboring METEORITE_CONFIG asserts):

```python
assert METEORITE_CONFIG["stem_short_name_template"].format(
    stem=METEORITE_CONFIG["default_stem"],
    candidate_id="{candidate_id}",
) == METEORITE_CONFIG["short_name_template"]
assert isinstance(METEORITE_CONFIG["meteorite_self_stem"], str) and METEORITE_CONFIG["meteorite_self_stem"]
assert METEORITE_CONFIG["meteorite_self_stem"] == "meteorite-self"
assert isinstance(METEORITE_CONFIG["default_stem"], str) and METEORITE_CONFIG["default_stem"]
assert "METEORITE" in COMPANY_STATES
assert COMPANY_STATES["METEORITE"] == {}
```

4. Do **not** change `JOBS_RECOMMENDED_METEORITE_SECTION`, TASK_CONFIG, NAV, or other config blocks in this stage.

## Stage 2: Core — stem ensure + track predicate + Style D

**Done when:** `ensure_meteorite_company(candidate_id, *, stem=None, debug=False)` idempotently ensures `{stem}-{candidate_id}` (default stem → `meteorite-{candidate_id}`) in **METEORITE** on insert; existing rows are returned unchanged (no IGNORE→METEORITE rewrite). `is_meteorite_company(short_name)` is true for `METEORITE`-state companies and for legacy `meteorite-` prefix rows. With `debug=True`, ensure emits Style D index + detail including stem, short_name, and create-vs-reuse; with `debug=False`, no new debug-contract lines. `create_meteorite_job` / `land_meteorite` keep calling ensure **without** stem (default path) so Slack/Contact and current land continue to use `meteorite-{candidate}` — now inserted in METEORITE.

1. Update `src/core/meteorite.py` module docstring: METEORITE company state; stem-keyed ensure; track = company state METEORITE **or** legacy `short_name_prefix`; land/create still default-stem until AST-1495 wires stem attach.

2. Replace `is_meteorite_company` body with:

```python
def is_meteorite_company(short_name: Optional[str]) -> bool:
    """True on METEORITE-state companies or legacy meteorite- prefix (AST-1152 / AST-1493)."""
    if not short_name:
        return False
    sn = str(short_name)
    prefix = METEORITE_CONFIG["short_name_prefix"]
    if sn.startswith(prefix):
        return True
    row = get_company(sn)
    if row is None:
        return False
    return (row.get("state") or "") == METEORITE_CONFIG["company_state"]
```

⚠️ **Decision:** Prefix check first (no DB) covers historical `IGNORE` `meteorite-{candidate}` rows that this epic does not restated. State check covers new stem short_names (`alice@example.com-somerset`, `meteorite-self-somerset`, `{slug}-somerset`) that do **not** start with `meteorite-`. Callers (`consult.qualify_job_listings`, `gazer` title-pattern skip) keep passing `job["company"]` — signature unchanged. METEORITE_* **job** states already bypass title-pattern via not being `NEW` / via GDL state registries; this ticket does not add a parallel job-state helper (scope: company track predicate).

3. Expand `ensure_meteorite_company`:

```python
def ensure_meteorite_company(
    candidate_id: str,
    *,
    stem: Optional[str] = None,
    debug: bool = False,
) -> dict[str, Any]:
```

Concrete steps inside the function:

a. Strip `candidate_id`; raise `ValueError("candidate_id is required")` if empty (unchanged).  
b. Resolve stem: `(stem or "").strip()` → if empty, use `METEORITE_CONFIG["default_stem"]`. Do **not** special-case `meteorite_self_stem` beyond using it as the stem string when the caller passes that literal (Ruth/sibling passes it; ensure is stem-agnostic).  
c. Build `short_name = METEORITE_CONFIG["stem_short_name_template"].format(stem=resolved_stem, candidate_id=candidate_id)`.  
d. `get_company(short_name)` — if present: Style D outcome `"already-present"` when `debug=True` (detail: `candidate_id=…`, `stem=…`); return `{"short_name", "inserted": False, "company"}` **without** changing `state` (leave-in-place for IGNORE-era rows).  
e. Else `save_company(short_name=…, state=METEORITE_CONFIG["company_state"], company_name=METEORITE_CONFIG["company_name"], company_data=dict(METEORITE_CONFIG["company_data"]), candidate_id=candidate_id)` — same fields as today, new state. Re-`get_company`; raise `RuntimeError` if missing (unchanged).  
f. Style D when `debug=True`: `func="meteorite.ensure_meteorite_company"`, `index=1`, `total=1`, `identifier=short_name`, outcome `"inserted"` or `"already-present"`; `debug_detail` lines must include `candidate_id=…` and `stem=…` (and may include `company_state=…` on insert). No Style D / no new contract lines when `debug=False`.

4. Leave `create_meteorite_job` and `land_meteorite` calling `ensure_meteorite_company(candidate_id, debug=debug)` **without** `stem=` (default stem). Do **not** add stem kwargs to land/create in this ticket — AST-1495 owns attach-when-stem-present.

5. Do **not** import consult at module top; do **not** touch gazer/inbox/api.

## Execution contract

- Stages in order; steps in order within a stage.
- One commit per stage on the epic worktree, then `git push origin HEAD:sub/AST-1484/AST-1493-meteorite-company-state-stem-ensure-track`.
- No files outside the Files Changed table.
- Ambiguity / drift → stop, comment on **parent** AST-1484 with the Stage blocked format from plan-child, wait.
- Test tree / bible: Betty only — engineer does not edit `tests/` or `docs/test-bible/**`.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Review (build stub)

**Publish ref:** `origin/sub/AST-1484/AST-1493-meteorite-company-state-stem-ensure-track`
**Plan path:** `docs/features/meteorite/ast-1493-meteorite-company-state-stem-ensure-track.md`

**Built tip:** `ea0a20ea2fdfd6c84081455efb8192c7d1aa5e37` (`ea0a20ea`)

| Stage | Commit | Summary |
|-------|--------|----------|
| 1 | `4deacb6c` | COMPANY_STATES METEORITE + stem templates / company_state flip |
| 2 | `ea0a20ea` | stem `ensure_meteorite_company` + state/prefix `is_meteorite_company` + Style D |

**Betty note:** ensure/track + METEORITE-state carve-outs for `tests/component/core/test_meteorite.py` (and any prefix-only track tests) deferred to qa-child (engineer test-tree ban).

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1493
**Overall:** APPROVED
**Publish ref:** `sub/AST-1484/AST-1493-meteorite-company-state-stem-ensure-track` @ `fc70680fd29b42cbd8230c109cfba5d211c4a026`

## Traceability
AC1→S1; AC2–AC4→S2 `ensure_meteorite_company(stem=)` API; AC5→S2 `is_meteorite_company` state+prefix; AC6→S2 default-stem ensure (new inserts METEORITE); AC7→S2 leave-in-place on existing IGNORE rows; AC8→S2 Style D on ensure; parent AC5 (email attach)→AST-1495 out of scope.

## Findings

### discuss
- **Location:** Plan doc (top-level sections)
- **Finding:** No `## Self-Assessment` (conf / blast-radius / risk axes) — plan-child usually carries one.
- **Recommendation:** Optional add before build; not blocking — stages and scope gate are explicit.

### discuss
- **Location:** Parent Architectural definition — New patterns proposed
- **Finding:** “METEORITE company state + stem-keyed placeholders” is flagged at parent; no `status: proposed` catalog entry yet.
- **Recommendation:** Archie catalog follow-up is parent-tracked; child correctly cites `pattern.config.config-block` + `pattern.state.entity-state-transitions` for implementation shape.

### acceptable
- **Location:** Scope gate — `JOBS_RECOMMENDED_METEORITE_SECTION`
- **Finding:** Recommended UI partition stays prefix-based; stem-keyed short_names won’t appear there until AST-1495 / follow-on.
- **Recommendation:** Plan documents deferral; aligns with child partition.

context_tokens≈42000

## Radia review

# Radia review — AST-1493

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1493  
**Publish ref:** `origin/sub/AST-1484/AST-1493-meteorite-company-state-stem-ensure-track` @ `cedbfa6815506ba49e9af79aa59398e0ca9933a6`  
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | diff does not touch agent/LLM confidence paths |
| astral.agent.do-task-delegation | scoped | not-applicable | no do_task / agent dispatch changes |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade-vector paths |
| astral.batch.batch-id-first | scoped | not-applicable | no batch runner / batch_id emission |
| astral.batch.batch-id-format | scoped | not-applicable | no batch_id formatting |
| astral.batch.claim-process-release | scoped | not-applicable | no claim/process/release batch helpers |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no entity agent-responses writes |
| astral.config.config-source-of-truth | scoped | conforms | METEORITE state + stem literals live in `METEORITE_CONFIG` / `COMPANY_STATES`; callers read config |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets or env-specific config added |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug artifacts |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no spike files |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch seed changes |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no run_next / chain changes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single issue doc `docs/features/meteorite/ast-1493-…md` |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commit `be1dc566` touches tests + test-bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer commits `4deacb6c` / `ea0a20ea` are `src/` only; tests landed via Betty |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | no new external integration; pre-existing `playwright` import unchanged |
| astral.layers.import-direction | scoped | conforms | `core` → `data` / `utils` only; no UI or utils→data bend |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no `scripts/` changes |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | no `src/ui/` changes |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check / entity_data paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult render-verdict paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no API/auth surface |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | no seed JSON changes |
| astral.seed.archie-catalog-wins | scoped | not-applicable | no catalog/seed contention |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | ensure remains lazy on demand, not boot bulk |
| astral.seed.define-approved | scoped | not-applicable | no define/seed workflow |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no operator seed rows |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage-join seed paths |
| astral.standards.data-raises-caller-logs | scoped | conforms | no new logging inside `src/data/` |
| astral.standards.database-header-inventory | scoped | not-applicable | no schema / migration / `database.py` changes |
| astral.standards.debug-contract-gated | scoped | conforms | Style D index/detail emitted only when `debug=True` via `get_logger` helpers |
| astral.standards.dry-and-focused-functions | scoped | conforms | stem resolution + track predicate are focused; no duplicate config literals in core |
| astral.standards.in-scope-only | scoped | conforms | product diff limited to `src/utils/config.py` + `src/core/meteorite.py` per scope gate |
| astral.standards.logging-via-utils | scoped | conforms | uses `get_logger` / `set_debug_flag`; no `print()` or stdlib logging |
| astral.standards.names-not-ticket-ids | scoped | conforms | runtime identifiers are config-driven (`METEORITE`, stem templates) |
| astral.standards.no-cross-contamination | scoped | conforms | no sibling AST-1494/1495 consult/inbox/land wiring smuggled in |
| astral.standards.no-hardcoded-sets | scoped | conforms | company state and stem shapes read from `METEORITE_CONFIG` / `COMPANY_STATES` |
| astral.standards.public-then-helpers | scoped | conforms | public ensure/track API unchanged in shape; no helper reorder issues |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | `config.py` diff does not import `data` |
| astral.state.core-decides-transitions | scoped | conforms | companies created in core via `save_company` with config state; no ad hoc transition map bypass |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job transition registry edits |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no multi-hop runner added |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend files |
| astral.ui.naming-conventions | scoped | not-applicable | no UI naming surface |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server worker config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | tip `cedbfa68` is `merge-tests(AST-1493)` atop Betty test SHA |
| orch.git.commit-vocabulary | universal | conforms | `code` / `test` / `docs` / `merge-tests` vocabulary respected |
| orch.git.flow-direction-inviolable | universal | conforms | work on `sub/AST-1484/AST-1493-…` vs `origin/dev` |
| orch.git.ftr-sub-topology | universal | conforms | child publish ref under parent segment |
| orch.git.merge-on-checkout | universal | conforms | no merge/checkout violations in diff |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | linear stage commits; merge-tests only |
| orch.git.no-dev-agent-branches | universal | conforms | no agent-named branches in diff |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1484 epic worktree pattern |
| orch.git.three-permanent-branches | universal | conforms | diff base `origin/dev` |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no product-policy overrides in diff |
| orch.pipeline.plan-is-bible | universal | conforms | implementation matches staged plan (config then core) |
| orch.pipeline.project-scoped-queues | universal | conforms | Meteorite child scoped correctly |
| orch.pipeline.status-gates-skill-entry | universal | conforms | reviewed at Tests Passed per pipeline |
| orch.roles.archie-approves-statutes | universal | conforms | no statute authoring in diff |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns `tests/` + bible revisions |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee remains Ada |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | engineer through Tests Passed; review is Radia recommend-only |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path commits observed |

**Active-set count:** 64 rows scored from registry § Harvested corpus table (registry header cites 65; no additional active row opened for this diff).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.config.config-block | conforms | `METEORITE_CONFIG` extended with stem templates, literals, and startup asserts; callers consume config |
| pattern.state.entity-state-transitions | conforms | `COMPANY_STATES["METEORITE"]` registered roster-inert; creation via ensure/`save_company`, not transition-map edges (plan carve-out mirrors IGNORE) |

## Plan adherence

- **Stage 1 (config):** `COMPANY_STATES["METEORITE"] = {}`; `company_state` flipped to `"METEORITE"`; `stem_short_name_template`, `default_stem`, `meteorite_self_stem` added with asserts tying default stem to legacy `short_name_template`. No out-of-scope config blocks touched.
- **Stage 2 (core):** `ensure_meteorite_company(..., stem=None, debug=False)` formats `{stem}-{candidate_id}`, inserts into METEORITE, leave-in-place on existing rows. `is_meteorite_company` widened to prefix-first then METEORITE state lookup. `create_meteorite_job` / `land_meteorite` still call ensure without `stem=`.
- **Scope / siblings:** No AST-1494 Ruth stem units, no AST-1495 inbox/land attach, no `database.py` claim SQL, no Recommended UI partition changes.
- **Estimate (5):** Footprint matches — two product files, focused API surface, Betty test/bible follow-on.
- **Tests / bible:** Betty manifest aligns with plan ACs (email/self/slug stems, leave-in-place IGNORE, prefix+state track, Style D stem detail, create path METEORITE honesty).

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Location:** Joan validate attachment (`docs/features/meteorite/ast-1493-…md`)
- **Finding:** Joan verdict is APPROVED but carries no `Excluded` statute table.
- **Recommendation:** Straggler check N/A; note `no plan-rubric Excluded table attached` — not blocking.

- **Location:** `src/core/meteorite.py` — `is_meteorite_company`
- **Finding:** Non-`meteorite-` short_names now incur a `get_company` read on the state path.
- **Recommendation:** Acceptable for current callers (`consult`, `gazer` batch contexts). If a hot path emerges later, consider caching — out of scope here.

- **Location:** Parent architectural note (issue doc Findings §discuss)
- **Finding:** “METEORITE company state + stem-keyed placeholders” pattern not yet in approved catalog as `proposed`.
- **Recommendation:** Parent-tracked Archie catalog follow-up; implementation correctly uses existing approved patterns.

## What's solid

- Config-owned stem shapes with asserts prevent template drift from legacy `meteorite-{candidate_id}`.
- Leave-in-place IGNORE rows (AC7) is explicit in code and tested.
- Style D on ensure is properly gated, uses `debug_index` 1/1 + multi-line `debug_detail` (`candidate_id`, `stem`, `company_state` on insert).
- Cross-ticket boundary held: land/create remain default-stem until AST-1495.

## Frame diff

- New roster-inert company state `METEORITE` in `COMPANY_STATES`.
- New inserts from `ensure_meteorite_company` land in `METEORITE` (was `IGNORE` for new rows only).
- `ensure_meteorite_company` accepts optional `stem=`; short_name built from `stem_short_name_template`.
- `is_meteorite_company` predicate widened: legacy `meteorite-` prefix **or** persisted company state `METEORITE`.

## Notes

- Diff reviewed: `origin/dev...origin/sub/AST-1484/AST-1493-meteorite-company-state-stem-ensure-track` (7 files; product + Betty tests/bible + issue doc).
- Engineer product tip: `ea0a20ea`; publish tip after merge-tests: `cedbfa68`.
- C7 complete — Chuckles may append to issue doc, push `docs(AST-1493): Radia review — clean`, post slim upshot, advance to **Review Posted** → **User Testing** (no fix-now items).

context_tokens≈55000
