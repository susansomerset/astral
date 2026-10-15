# AST-2223 — Candidate meteorite edit — config, core, API

- **Linear:** [AST-2223](https://linear.app/astralcareermatch/issue/AST-2223)
- **Parent:** [AST-2216](https://linear.app/astralcareermatch/issue/AST-2216) — Make meteorite text editable (not versioned)
- **Publish ref:** `sub/AST-2216/AST-2223-candidate-meteorite-edit`

Server half of candidate meteorite edit: one config block (locked `LANDED`, editable columns, pick-list = every `METEORITE_STATES` key minus locked, default save state `CHECK_UNIQUE`), a core save that overwrites supplied fields without versioning / pipeline side-effects, and an authenticated PUT plus detail-GET edit envelope so React never hard-codes states. Ships parent AC 1 (server half), 2–11, 13. Does **not** own `MeteoriteDetailModal.tsx` or `JobsMeteorites.tsx` (sibling AST-2224).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | New `CANDIDATE_METEORITE_EDIT_CONFIG` + load-time asserts | utils |
| `src/core/meteorite.py` | `is_meteorite_editable` + `save_candidate_meteorite_edit`; reuse `_normalize_apply_paste_content` | core |
| `src/ui/api/api_meteorite.py` | PUT `/api/meteorites/<id>`; detail GET gains edit envelope from config/core | ui |

Do **not** edit: `src/data/database.py` (AC 9 — no schema), `src/ui/frontend/**` (sibling AST-2224), `apply_paste` / Slack paste tests, `tests/`, bible, `METEORITE_STATES` priors, `stage_meteorite` / scrape / land / Telescope entry points.

## Stage 1: Config block

**Done when:** `import src.utils.config` succeeds; `CANDIDATE_METEORITE_EDIT_CONFIG` exposes locked states, editable fields, state options, and default save state with the asserts below; `python3 -m py_compile src/utils/config.py` passes.

1. In `src/utils/config.py`, immediately after the `METEORITE_STATES` closed-set / prior asserts (after the `for _ms, _mcfg in METEORITE_STATES.items():` loop that ends ~line 3252, before `METEORITE_INGRESS_DISPATCH_CONFIG`), add:

```python
# AST-2223: candidate overwrite edit on non-landed meteorite rows (Jobs → Meteorites modal).
# Not versioned — plain update_meteorite; pick-list is every registry key minus locked.
CANDIDATE_METEORITE_EDIT_CONFIG = {
    "locked_states": ("LANDED",),
    "editable_fields": (
        "state",
        "content",
        "link",
        "job_title",
        "employer_name",
        METEORITE_CONFIG["electronic_contact_column"],
    ),
    "state_options": tuple(
        s for s in METEORITE_STATES if s not in ("LANDED",)
    ),
    "default_save_state": "CHECK_UNIQUE",
}
_cme = CANDIDATE_METEORITE_EDIT_CONFIG
assert all(s in METEORITE_STATES for s in _cme["locked_states"])
assert all(s in METEORITE_STATES for s in _cme["state_options"])
assert _cme["default_save_state"] in _cme["state_options"]
assert set(_cme["locked_states"]).isdisjoint(_cme["state_options"])
assert set(_cme["state_options"]) == set(METEORITE_STATES) - set(_cme["locked_states"])
assert "state" in _cme["editable_fields"] and "content" in _cme["editable_fields"]
assert METEORITE_CONFIG["electronic_contact_column"] in _cme["editable_fields"]
```

⚠️ **Decision:** `state_options` is built as every `METEORITE_STATES` key minus `locked_states` (ticket Scope), including error / retry / `DUPLICATE` / `NOT_A_JOB` / `ABANDONED`. Candidate override is intentional (same as human reset priors); do not filter to “happy path” states only.

2. Do not put `LANDED` / `CHECK_UNIQUE` / `NEW` literals into `api_meteorite.py` or hard-code those lists in core — core and API read `_cme` keys only. The config block itself is the allowed home for those literals (AC 11).

## Stage 2: Core edit + editability helper

**Done when:** `is_meteorite_editable(row)` is true iff `row["state"]` is not in `CANDIDATE_METEORITE_EDIT_CONFIG["locked_states"]` (claimed/`batch_id` does **not** flip the flag — AC 1 only keys on `LANDED`; claim is a save-time 409). `save_candidate_meteorite_edit` refuses the cases below without writing, warns once via `_warn_item`, and on success writes one `update_meteorite` with normalized/trimmed fields, clears `error` + emits `_meteorite_state_info` only when state changes, and never calls `stage_meteorite` / Ruth / `do_task` / scrape / Telescope. `python3 -m py_compile src/core/meteorite.py` passes.

1. In `src/core/meteorite.py`, add `CANDIDATE_METEORITE_EDIT_CONFIG` to the existing `from src.utils.config import (` block.

2. Immediately after `apply_paste` (after its return, before `_resolve_slack_dm_channel_for_candidate`), add:

```python
def is_meteorite_editable(row: Optional[dict]) -> bool:
    """True when the row's state is not in CANDIDATE_METEORITE_EDIT_CONFIG locked_states."""
    if not row:
        return False
    locked = CANDIDATE_METEORITE_EDIT_CONFIG["locked_states"]
    return (row.get("state") or "") not in locked


def save_candidate_meteorite_edit(meteorite_id: int, fields: dict) -> dict:
    """Overwrite candidate-supplied meteorite fields. No pipeline side-effects (AST-2223)."""
    ...
```

3. Implement `save_candidate_meteorite_edit` as follows (literal control flow — do not invent extra gates):

   a. `row = get_meteorite(meteorite_id)`. If missing → `_warn_item(f"meteorite {meteorite_id}", "not found", "This candidate edit is not saving")` → `return {"ok": False, "error": "not_found"}`.

   b. `cid = row.get("candidate_id")`. Who string for later warns: `f"meteorite {meteorite_id} for {cid}"`.

   c. If `row.get("state")` in `CANDIDATE_METEORITE_EDIT_CONFIG["locked_states"]` → warn why `landed` / locked, next step `"This candidate edit is not saving"` → `return {"ok": False, "error": "locked"}`.

   d. If `row.get("batch_id")` is not `None` and not `""` → warn why `claimed` (`batch_id` held), same next step → `return {"ok": False, "error": "claimed"}`. (stat.batch.claim-process-release — never write a held claim-queue row.)

   e. If `fields` is not a `dict` → treat as bad_field (or API guarantees dict; core may `return {"ok": False, "error": "bad_field"}` after warn).

   f. `editable = set(CANDIDATE_METEORITE_EDIT_CONFIG["editable_fields"])`. For any key in `fields` not in `editable` → warn why `field not editable: <key>` → `return {"ok": False, "error": "bad_field"}`.

   g. Build `to_write: dict = {}`. For each `(key, value)` in `fields.items()`:
      - If `key == "content"`: `normalized = _normalize_apply_paste_content(value if isinstance(value, str) else "")`. If not `normalized` → warn `empty content` → `return {"ok": False, "error": "empty_content"}`. Set `to_write["content"] = normalized`. Debug-log the raw pasted body only via `logger.debug` (stat.logging.debug) — never put paste text on info/warning.
      - Elif `key == "state"`: `state = value if isinstance(value, str) else ""`. If `state` not in `CANDIDATE_METEORITE_EDIT_CONFIG["state_options"]` → warn `state not in pick-list: <state>` → `return {"ok": False, "error": "bad_state"}`. Set `to_write["state"] = state`.
      - Else (link / job_title / employer_name / electronic_contact): coerce to str (None → `""`), `.strip()`, set `to_write[key] =` trimmed string.

   h. ⚠️ **Decision:** Every successful save **must** include `content` and `state` in `fields` (modal always sends the full editable set). If either key is missing after the loop → warn `content and state required` → `return {"ok": False, "error": "bad_field"}`. Do not invent defaults in core (default `CHECK_UNIQUE` is a UI/pre-select concern from the detail GET).

   i. `from_state = row.get("state")`. `state_changing = ("state" in to_write) and (to_write["state"] != from_state)`. If `state_changing`: set `to_write["error"] = None`.

   j. `update_meteorite(meteorite_id, **to_write)` once. Do not touch `prior_states`. Do not insert `agent_data`. Do not call `stage_meteorite`, classify, `do_task`, scrape, or Telescope.

   k. If `state_changing`: `_meteorite_state_info(meteorite_id, to_write["state"], from_state=from_state)` (stat.logging.info.entity — existing helper; batch token stays `-` when no dispatch ContextVar).

   l. Re-`get_meteorite(meteorite_id)` and `return {"ok": True, "meteorite": updated_row}`.

4. Leave `apply_paste` byte-identical in behavior (AC 10). Shared normalizer only.

## Stage 3: API PUT + detail edit envelope

**Done when:** `GET /api/meteorites/<id>` returns the existing detail shape plus top-level `editable`, `editable_fields`, `state_options`, `default_save_state` from config/helper (LANDED → `editable: false`; any other state → `true`; lists/default always from config). `PUT /api/meteorites/<id>` with JSON body maps core outcomes to 200/400/404/409 as below, returns the same detail+envelope projection on 200, emits exactly one completing info line on 200 matching AC 13, stays silent at info on GET, logs unexpected exceptions once at the route as 500. `rg -n '"NEW"|"LANDED"|"CHECK_UNIQUE"' src/ui/api/api_meteorite.py` shows no new literals vs `origin/dev`. `python3 -m py_compile src/ui/api/api_meteorite.py` passes.

1. In `src/ui/api/api_meteorite.py`:
   - Import `is_meteorite_editable`, `save_candidate_meteorite_edit` from `src.core.meteorite`.
   - Import `CANDIDATE_METEORITE_EDIT_CONFIG` from `src.utils.config` (alongside existing imports).

2. Add a private helper (same file):

```python
def _detail_payload(row: dict) -> dict:
    cfg = CANDIDATE_METEORITE_EDIT_CONFIG
    return {
        "sections": list(JOBS_METEORITES_MODAL_SECTIONS),
        "meteorite": _project_meteorite(row, _DETAIL_KEYS),
        "editable": is_meteorite_editable(row),
        "editable_fields": list(cfg["editable_fields"]),
        "state_options": list(cfg["state_options"]),
        "default_save_state": cfg["default_save_state"],
    }
```

⚠️ **Decision:** Edit meta lives as **top-level** JSON keys next to `sections` / `meteorite` (not nested under `meteorite`), so sibling AST-2224 can read the envelope without inventing field names. Keys are exactly: `editable`, `editable_fields`, `state_options`, `default_save_state`.

3. Change `meteorite_detail` success return to `return jsonify(_detail_payload(row))`. Keep 404 / 500 paths unchanged (still no completing info on GET — stat.logging.info.api). Prefer using `row.get("candidate_id") or "-"` in the existing exception log instead of hard-coded `"-"`.

4. Add route **after** the detail GET:

```python
@meteorite_bp.route("/meteorites/<int:meteorite_id>", methods=["PUT"])
@require_auth
def meteorite_candidate_edit(meteorite_id: int):
    """Candidate overwrite edit for one meteorite (AST-2223)."""
    route = f"/api/meteorites/{meteorite_id}"
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON object required"}), 400
    try:
        result = save_candidate_meteorite_edit(meteorite_id, data)
        ...
    except Exception as exc:
        # logger.exception with candidate_id or "-", route, type, exc, next step; return 500 JSON
```

5. Map `result` (no write on failure — core already warned):

| `result["error"]` / ok | HTTP | JSON body |
|------------------------|------|-----------|
| `ok` True | 200 | `_detail_payload(result["meteorite"])` |
| `not_found` | 404 | `{"error": "meteorite not found"}` |
| `locked` | 409 | `{"error": "meteorite is landed and not editable"}` |
| `claimed` | 409 | `{"error": "meteorite is claimed by a running batch"}` |
| `bad_field` | 400 | `{"error": "one or more fields are not editable"}` |
| `bad_state` | 400 | `{"error": "state is not in the editable pick-list"}` |
| `empty_content` | 400 | `{"error": "content is empty after normalization"}` |

6. On HTTP 200 only, after building the payload, emit (stat.logging.info.api / AC 13):

```python
logger.info(
    "%s | api %s completed: PUT %s",
    result["meteorite"].get("candidate_id") or "-",
    route,
    200,
)
```

Do **not** emit that info line on 4xx/5xx. Do **not** log pasted content at info.

7. Unexpected exception in the `try`: `logger.exception` once with candidate (from a pre-call `get_meteorite` if useful, else `"-"`), route, exc type/message, and next-step line (`Returning 500; meteorite unchanged`) — matching the detail GET failure shape (stat.logging.error). Return `jsonify({"error": "meteorite edit failed"}), 500`.

## Execution contract

- Stages in order; one commit per stage on the epic worktree; push `origin/sub/AST-2216/AST-2223-candidate-meteorite-edit` after each stage.
- Do not add files, touch `database.py`, or implement the React modal.
- Ambiguity / drift → comment on **parent** AST-2216 with the Stage-blocked template and stop.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2223
**Overall:** APPROVED
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Publish ref:** `sub/AST-2216/AST-2223-candidate-meteorite-edit` @ `e9dcf73b3fe9ad27ea730b0578abfbe1c3946b93`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.batch.claim-process-release | A | | |
| stat.logging.info.api | A | | |
| stat.logging.info.entity | A | | |
| stat.logging.warning | A | | |
| stat.logging.error | A | | |
| stat.logging.debug | A | | |

## Traceability

| AC | Plan coverage |
|----|----------------|
| 1 (server) | Stage 3: `_detail_payload` + `is_meteorite_editable`; AC 1 React `rg` negative → N/A (AST-2224) |
| 2 | Stage 2j (no pipeline calls); Stage 3 PUT 200 |
| 3 | Stage 2g normalize/trim + `update_meteorite` |
| 4 | Stage 2i `error` clear only when `state_changing` |
| 5 | Stage 2f reject keys outside `editable_fields` |
| 6 | Stage 2c locked row → 409; Stage 2g `LANDED` ∉ `state_options` → 400 |
| 7 | Stage 2d `batch_id` held → 409 |
| 8 | Stage 2g empty normalized content → 400 |
| 9 | Execution contract (no `database.py`); Stage 2j no `agent_data` |
| 10 | Stage 2.4 leave `apply_paste` unchanged |
| 11 | Stage 1 config block + asserts; Stage 3 `rg` / config reads only |
| 12 | N/A — sibling AST-2224 owns modal AC |
| 13 | Stage 3.6 single `logger.info` on PUT 200 only |

## Findings

### discuss — Canon Scope gap (not scored)

- **Location:** Parent Canon Scope / AST-2223 Citations
- **Finding:** `astral.config.config-source-of-truth` plainly governs the new `CANDIDATE_METEORITE_EDIT_CONFIG` block and load-time asserts, but it is not on this child’s frozen directive list (only batch + logging statutes are).
- **Recommendation:** Archie may amend Canon Scope at Discussion if she wants Radia’s pass to score config SOT explicitly; the plan text already matches parent Technical scope on config-as-source.

### acceptable — Tests named in AC but not staged

- **Location:** Plan stages vs parent AC 2–11 component tests
- **Finding:** Stages end at compile/`py_compile` gates; Betty’s manifest will own AC-shaped component tests per workflow.
- **Recommendation:** No plan change required for validate-plan; ensure `qa-child` maps each AC to a test.

## R6 notes (no additional fix-now)

- Definition fidelity: Files Changed ⊆ ticket `## Scope`; excludes frontend and `database.py` as declared.
- `editable` true for claimed-but-non-`LANDED` rows matches parent AC 1 (claim refusal is save-time 409 per AC 7).
- Stage 2h (require `content` + `state` on every save) is a deliberate API contract for the modal envelope; aligns with sibling #2 sending the full editable set.
- Estimate confirm `3 — agree` matches scope and staged decomposition.

context_tokens≈42000

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-2216/AST-2223-candidate-meteorite-edit`  
**Product tip:** `b3e6dcef3` — Stages 1–3 (`CANDIDATE_METEORITE_EDIT_CONFIG`; `is_meteorite_editable` + `save_candidate_meteorite_edit`; PUT `/api/meteorites/<id>` + detail edit envelope)

**Stages:**
1. `a10875d16` — config block + load-time asserts
2. `b8495ddde` — core edit + editability helper
3. `b3e6dcef3` — API PUT + detail GET envelope

**Checks:** `py_compile` on changed `.py` files; `rg` AC11 clean (no NEW/LANDED/CHECK_UNIQUE literals in `api_meteorite.py`); `validate-sub-log --stage=build` ok.

**Tests:** Betty at Code Complete (`qa-child`) — engineers do not land test-tree changes.
