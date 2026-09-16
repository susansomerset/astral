# AST-1672 — DISCOVERED + resolve registry SSOT

**Linear:** https://linear.app/astralcareermatch/issue/AST-1672  
**Parent:** [AST-1670](https://linear.app/astralcareermatch/issue/AST-1670) — Split inflow website resolve into CSE fetch + find_company_website dispatch  
**Publish ref:** `sub/AST-1670/AST-1672-discovered-resolve-registry-ssot`

Config/SSOT only for the inflow website-resolve split: introduce company `DISCOVERED` as the pre-vet land state, retarget discovery land + vet claim triggers to it, reshape `INFLOW_CONFIG["resolve"]` into a CSE-only fetch hop on `DISCOVERED` (waiting `WEBSITE_REVIEW`, persisted hit-list key, no inline AI key), wire `WEBSITE_REVIEW` waiting transitions, and register schedulable `resolve_website` (`agent_task=find_company_website`) so siblings can implement CSE fetch (AST-1673) and AI apply (AST-1674) without inventing literals.

**Canon Scope (frozen at Plan Approved):** `patt.entity.batch-criteria`, `stat.logging.debug`  
**Corpus note (plan-time):** patterns read in full; `stat.logging.debug` is id-only until build expand — this ticket adds no `logger.debug` call sites (config-only).

## Explicit scope gate

Ticket **## Scope** names only `src/utils/config.py`. Every row in Files Changed and every stage step stays inside that file. No `roster.py` / `consult.py` / `dispatcher.py` / `database.py` edits (siblings AST-1673 / AST-1674). No Somerset / `dispatch_tasks` row inserts (parent AC ops gate).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `DISCOVERED`; cut over discovery land + vet triggers; reshape `INFLOW_CONFIG["resolve"]`; register CSE hit-list key; wire `WEBSITE_REVIEW` transitions + `batch_criteria`; register schedulable `resolve_website`; remove resolve/vet outcomes from `NEW` | utils |

## Stage 1: Company state + transition SSOT

**Done when:** `COMPANY_STATES` includes `DISCOVERED` with claimable `batch_criteria.sort_by`; `WEBSITE_REVIEW` has the same so admin defaults can derive sort; `SYSTEM_CONFIG["company_state_transitions"]` encodes vet / CSE / AI edges on `DISCOVERED` / `WEBSITE_REVIEW` and no longer lists resolve or vet outcomes off `NEW`.

1. In `COMPANY_STATES`, insert `"DISCOVERED": {"batch_criteria": {"sort_by": "updated_at"}}` immediately after `"NEW"` (same criteria shape as `NEW` — claim order only; no `limit` unless a later sibling needs one).
2. Change `"WEBSITE_REVIEW": {}` to `"WEBSITE_REVIEW": {"batch_criteria": {"sort_by": "updated_at"}}` so `_dispatch_sort_by_for("company", "WEBSITE_REVIEW")` succeeds for `resolve_website` admin defaults (`patt.entity.batch-criteria`: sort lives on state criteria, not a literal in the claim caller).
3. In `SYSTEM_CONFIG["company_state_transitions"]`, **remove** these three tuples (resolve + vet outcomes leave the `NEW` branch):
   - `("NEW", "WEBSITE_FOUND")`
   - `("NEW", "NO_WEBSITE")`
   - `("NEW", "VET_FAILED")`
4. In the same list, **add** (place with the other early company edges, near the former `NEW` block / after `IMPORTED` edges):
   - `("DISCOVERED", "WEBSITE_FOUND")` — vet pass
   - `("DISCOVERED", "VET_FAILED")` — vet fail
   - `("DISCOVERED", "WEBSITE_REVIEW")` — CSE fetch with ≥1 hit
   - `("DISCOVERED", "NO_WEBSITE")` — CSE fetch with zero hits
   - `("WEBSITE_REVIEW", "WEBSITE_FOUND")` — `resolve_website` success
   - `("WEBSITE_REVIEW", "NO_WEBSITE")` — `resolve_website` decline / empty website
5. Leave existing `("IMPORTED", "WEBSITE_REVIEW")` (and other non-inflow edges) unchanged.

⚠️ **Decision:** `NEW` keeps its `COMPANY_STATES` entry and `batch_criteria` for any legacy rows, but loses all three outbound transition tuples in this pass. Inflow no longer creates or claims `NEW` after AST-1673/vet cutover; do not invent replacement `NEW` → … edges here.

## Stage 2: INFLOW_CONFIG land / vet / CSE-fetch reshape

**Done when:** discovery exposes land state `DISCOVERED`; vet claim trigger is `DISCOVERED` in both the vet block and the discovery mirror key; `INFLOW_CONFIG["resolve"]` is CSE-only on `DISCOVERED` with waiting + hit-list keys and no `ai_task_key`.

1. In `INFLOW_CONFIG["discovery"]`, add `"land_state": "DISCOVERED"` (literal sibling AST-1673 will read instead of hard-coded `state="NEW"` in roster). Keep `dispatch_trigger_state`: `"ACTIVE_SEARCH"` and other discovery CSE limits unchanged.
2. In `INFLOW_CONFIG["discovery"]`, change `"vet_dispatch_trigger_state"` from `"NEW"` to `"DISCOVERED"` (keep the key; do not delete the mirror — existing readers may still use it).
3. In `INFLOW_CONFIG["vet"]`, change `"dispatch_trigger_state"` from `"NEW"` to `"DISCOVERED"`. Leave `task_key`, `pass_state`, `fail_state`, `blurb_data_key`, grade frozensets, and `grade_vector_code` unchanged.
4. In `TASK_CONFIG["vet_inflow_discovery"]`, change `"trigger_state"` from `"NEW"` to `"DISCOVERED"` so schedulable admin defaults and `_dispatch_trigger_state_for_task_key` stay aligned with `INFLOW_CONFIG["vet"]`.
5. Replace `INFLOW_CONFIG["resolve"]` with this exact key set (CSE limits unchanged; fetch-hop only):

```python
"resolve": {
    "max_results": 20,
    "date_restrict_days": None,
    "task_key": "inflow_resolve_website",
    "dispatch_trigger_state": "DISCOVERED",
    "waiting_state": "WEBSITE_REVIEW",
    "pass_state": "WEBSITE_REVIEW",   # ≥1 CSE hit → waiting
    "fail_state": "NO_WEBSITE",        # zero CSE hits → terminal
    "hit_list_data_key": "inflow_resolve_website_hits",
},
```

6. **Delete** `"ai_task_key"` from the resolve block. Do not leave a deprecated alias.

⚠️ **Decision:** Removing `ai_task_key` will `KeyError` today’s `roster.resolve_company_website` until AST-1673 rewrites the CSE hop. That interim breakage on a partial epic tip is accepted — do not add a shim key; siblings own the runners.

7. In `ROSTER_CONFIG["company_data_keys"]`, add `"inflow_resolve_website_hits": "inflow_resolve_website_hits"` with an inline comment that this is explicit storage for the CSE hit list (no coat-check fetch handler) — same registration style as `job_list_visible`. The string must equal `INFLOW_CONFIG["resolve"]["hit_list_data_key"]`.

## Stage 3: Schedulable `resolve_website` + dispatch helpers

**Done when:** `dispatch_task_admin_defaults("resolve_website")` returns company / `WEBSITE_REVIEW`; `inflow_resolve_website` defaults claim `DISCOVERED`; `find_company_website` remains agent-only (`trigger_state` None); no inline AI key remains on the fetch hop config.

1. Add a `TASK_CONFIG` entry `"resolve_website"` immediately after `"find_company_website"` (Phase C company roster block) with:

```python
"resolve_website": {
    "response_schema": {
        "task_success": {"type": "bool", "required": True},
        "website": {"type": "str", "required": True},
    },
    "response_format": "json",
    "context_format": "find_company_website_{index}",  # reuse existing prompt indexing
    "entity_type": "company",
    "requires_candidate_key": True,
    "trigger_state": "WEBSITE_REVIEW",
    "agent_task": "find_company_website",
    "pass_state": "WEBSITE_FOUND",
    "fail_state": "NO_WEBSITE",
},
```

Leave `"find_company_website"` itself unchanged (`trigger_state`: `None` — agent identity, not a Scheduled Action key).

2. Add `"resolve_website"` to `_DISPATCH_COMPANY_ENTITY_TASK_KEYS` (alongside `inflow_resolve_website` / `vet_inflow_discovery`).
3. In `_dispatch_trigger_state_for_task_key`, keep the `inflow_resolve_website` branch reading `INFLOW_CONFIG["resolve"]["dispatch_trigger_state"]` (now `DISCOVERED`). Add an explicit branch before the generic `TASK_CONFIG` fallback:

```python
if task_key == "resolve_website":
    return "WEBSITE_REVIEW"
```

(Literal matches `TASK_CONFIG["resolve_website"]["trigger_state"]` — explicit so helper-resolvable discovery stays consistent if someone clears TASK_CONFIG.trigger_state later.)

4. Do **not** add `resolve_website` to `_DISPATCH_BATCH_CALL_MODE_ONE` (batch_call_mode stays `0`, same as `inflow_resolve_website`).
5. Confirm `inflow_resolve_website` remains **absent** from `TASK_CONFIG` (helper-resolvable fetch only — AST-960 / AST-1214). Do not promote it to an agent identity.
6. Add module-level asserts after `INFLOW_CONFIG` (or next to existing METEORITE/INFLOW asserts) that lock the cutover:

```python
assert "DISCOVERED" in COMPANY_STATES
assert COMPANY_STATES["DISCOVERED"]["batch_criteria"]["sort_by"] == "updated_at"
assert COMPANY_STATES["WEBSITE_REVIEW"]["batch_criteria"]["sort_by"] == "updated_at"
assert INFLOW_CONFIG["discovery"]["land_state"] == "DISCOVERED"
assert INFLOW_CONFIG["discovery"]["vet_dispatch_trigger_state"] == "DISCOVERED"
assert INFLOW_CONFIG["vet"]["dispatch_trigger_state"] == "DISCOVERED"
assert INFLOW_CONFIG["resolve"]["dispatch_trigger_state"] == "DISCOVERED"
assert INFLOW_CONFIG["resolve"]["waiting_state"] == "WEBSITE_REVIEW"
assert INFLOW_CONFIG["resolve"]["hit_list_data_key"] == "inflow_resolve_website_hits"
assert "ai_task_key" not in INFLOW_CONFIG["resolve"]
assert ROSTER_CONFIG["company_data_keys"]["inflow_resolve_website_hits"] == INFLOW_CONFIG["resolve"]["hit_list_data_key"]
assert TASK_CONFIG["resolve_website"]["agent_task"] == "find_company_website"
assert TASK_CONFIG["resolve_website"]["trigger_state"] == "WEBSITE_REVIEW"
assert TASK_CONFIG["vet_inflow_discovery"]["trigger_state"] == "DISCOVERED"
```

7. Import-time sanity: after edits, `python -c "from src.utils import config"` must succeed (assert block + no KeyError on dispatch helper probes below). Manually verify in the same shell:

```python
from src.utils.config import dispatch_task_admin_defaults, INFLOW_CONFIG, TASK_CONFIG
assert dispatch_task_admin_defaults("inflow_resolve_website")["trigger_state"] == "DISCOVERED"
assert dispatch_task_admin_defaults("vet_inflow_discovery")["trigger_state"] == "DISCOVERED"
assert dispatch_task_admin_defaults("resolve_website") == {
    "entity_type": "company",
    "trigger_state": "WEBSITE_REVIEW",
    "sort_by": "updated_at",
    "batch_call_mode": 0,
}
assert TASK_CONFIG["find_company_website"]["trigger_state"] is None
```

## Out of scope (do not touch)

- CSE search / persist / `do_task` removal in `roster.resolve_company_website` — **AST-1673**
- `resolve_website` apply runner / consult routing for AI hop — **AST-1674**
- `require_empty_website` claim SQL / dispatcher special-case move — **AST-1673**
- Adding Somerset (or any candidate) `dispatch_tasks` rows for either SA — parent ops gate

## Execution contract

- Stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1670/AST-1672-discovered-resolve-registry-ssot`.
- Do not add files outside the Files Changed table.
- If a referenced symbol moved or an assert fights an unexpected consumer in `config.py` itself — stop and comment on **AST-1670** with the Stage blocked template. Do not patch sibling modules to make config import.

## Estimate

Confirm Chuckles estimate: 5 — revise to 3 because this is a single-file config/SSOT cutover of a known fetch-then-AI hop pattern (no schema migration, no new pattern, no product runners).

## Joan validate

[plan-rubric]
**Ticket:** AST-1672
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `sub/AST-1670/AST-1672-discovered-resolve-registry-ssot` @ `2564468910143de059c710c8b479ee14beeb1011`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-criteria | A | | |
| stat.logging.debug | X | | config-only; no `logger.debug` call sites planned |

## Traceability

1→S1+S2.1 (`DISCOVERED` state + `land_state`) | 2→S2.2–S2.4+S3 asserts (`vet`/`vet_inflow_discovery` trigger `DISCOVERED`) | 3→S3 (`resolve_website` TASK_CONFIG + `_DISPATCH_COMPANY_ENTITY_TASK_KEYS` + `dispatch_task_admin_defaults`); parent AC3–5/7–8→N/A (siblings AST-1673/AST-1674); parent AC9→Out of scope ops gate

## Findings

### discuss

- **Canon Scope gap:** `astral.config.config-source-of-truth` plainly governs a config-only SSOT ticket but is absent from the frozen list. Plan behavior is compliant (all literals land in `config.py`); Archie may amend Canon Scope at Discussion for comparability with Radia's pass on siblings.
- **Location:** Stage 2 ⚠️ Decision (remove `ai_task_key`)
- **Finding:** Deleting `INFLOW_CONFIG["resolve"]["ai_task_key"]` will `KeyError` today's `roster.resolve_company_website` until AST-1673 lands.
- **Recommendation:** Accepted as documented epic sequencing; ensure AST-1673 merges promptly after this child.

### acceptable

- **Location:** Stage 1 step 3 (remove `NEW` outbound transitions)
- **Finding:** `NEW` retains `batch_criteria` but loses all three outbound transition tuples with no replacement edges.
- **Recommendation:** Consistent with inflow cutover intent; legacy `NEW` rows are out of this child's scope and should be handled operationally or in AST-1673 if any remain.

context_tokens≈42000
