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
