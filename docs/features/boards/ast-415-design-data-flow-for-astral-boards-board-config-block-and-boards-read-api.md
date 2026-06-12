# AST-415 — Design data flow for Astral Boards: BOARD_CONFIG block and boards read API

**Linear:** [AST-415 — Design data flow for Astral Boards: BOARD_CONFIG block and boards read API](https://linear.app/astralcareermatch/issue/AST-415/design-data-flow-for-astral-boards-board-config-block-and-boards-read)  
**Parent:** [AST-379 — Astral Boards](https://linear.app/astralcareermatch/issue/AST-379)  
**Feature ref:** `sub/AST-379/AST-415-design-data-flow-for-astral-boards` (origin only)

## Summary

Introduce engineer-owned **`BOARD_CONFIG`** in `src/utils/config.py` (no board table) and a **read-only** HTTP API listing **adopted** boards (`adopted: true`). Normative entry shape lives in **`docs/features/boards/board-config-entry.schema.md`**. First production key may be **`a16z`** after **AST-414** spike approval; this ticket ships the **block + API** even if only zero or one adopted key lands initially.

---

## Execution contract

Execute stages in order. Do not add `board_search` table, `gaze_board` ingest, or UI editors. If **AST-414** `a16z` draft is not Susan-approved, ship **`BOARD_CONFIG`** with **no** `adopted: true` keys (or a single stub with `adopted: false` only) and document in Linear — do not block the API on spike completion.

---

## Files changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `docs/features/boards/board-config-entry.schema.md` | Normative schema (created in plan-astral) | docs |
| `src/utils/config.py` | Add `BOARD_CONFIG` + `list_adopted_boards()` / `get_board_entry()` helpers | utils |
| `src/ui/api/api_boards.py` | New blueprint: list + detail read endpoints | ui |
| `src/ui/server.py` | `register_blueprint(boards_bp)` | ui |

No `src/core/gazer.py` changes, no DB migrations, no frontend in this ticket.

---

## Stage 1: Schema doc + config block skeleton

**Done when:** `BOARD_CONFIG` exists in `config.py`, imports cleanly, and schema doc matches ticket fields.

1. Ensure `docs/features/boards/board-config-entry.schema.md` matches ticket + **AST-414** v3 promotion rules (already committed with plan).
2. In `src/utils/config.py`, after existing large config dicts (near `CONSULT_CONFIG` / `TASK_CONFIG` — follow file locality), add:

```python
BOARD_CONFIG: dict[str, dict] = {
    # Example research slot — remove or set adopted:true after AST-414 approval:
    # "a16z": { ... transcribed from approved spike ... },
}
```

3. Each entry must include keys from schema: `label`, `entry_url`, `adopted`, `parse_instructions`, `search_criteria_schema`, `criteria_param_map`, `craft_task_key`, `scrape_mode`.
4. Add helpers in the same file (no new module):

```python
def list_adopted_boards() -> list[dict]:
    """Return [{board_key, label, entry_url, scrape_mode, craft_task_key}, ...] for adopted:true only."""

def get_board_entry(board_key: str) -> dict | None:
    """Return full entry if board_key exists and adopted:true; else None."""
```

5. `parse_instructions` may be `{}` until spike JSON is transcribed; `search_criteria_schema` may be minimal `{"type": "object", "properties": {}}` for first key.

⚠️ **Decision:** `craft_task_key` reuses existing `craft_joblist_rubric` for first board unless **AST-414** plan already added a board-specific craft key — do not duplicate `TASK_CONFIG` craft rows in this ticket.

---

## Stage 2: Read API

**Done when:** Authenticated `GET /api/boards` and `GET /api/boards/<board_key>` return expected JSON; non-adopted keys 404 on detail.

1. Create `src/ui/api/api_boards.py`:

```python
boards_bp = Blueprint("boards", __name__, url_prefix="/api/boards")
```

2. `GET /api/boards` — `@require_auth` from `ui.auth`:
   - Call `list_adopted_boards()`.
   - Return `jsonify(rows)` — array sorted by `board_key` ascending.

3. `GET /api/boards/<board_key>` — `@require_auth`:
   - `get_board_entry(board_key)`; if `None`, `jsonify({"error": "not found"}), 404`.
   - Response body: `{ "board_key": <key>, **entry }` including `parse_instructions`, `search_criteria_schema`, `criteria_param_map` (operator contract for downstream gaze — still read-only).

4. Do **not** expose `adopted: false` keys on either route.

---

## Stage 3: Register blueprint

**Done when:** Server starts and routes appear in Flask route map.

1. In `src/ui/server.py`, after `jobs_bp` registration:

```python
from ui.api.api_boards import boards_bp
app.register_blueprint(boards_bp)
```

2. `python3 -m py_compile src/ui/api/api_boards.py src/utils/config.py`

---

## Stage 4: Manual verification + Linear handoff

**Done when:** Linear comment documents curl results; ticket → **Code Complete** per build-astral.

1. With dev server running and auth cookie/header per local setup:
   - `GET /api/boards` → `[]` or one object when `a16z` adopted.
   - `GET /api/boards/a16z` → 404 when not adopted; 200 with fields when adopted.
2. Post Linear comment: adopted keys shipped, example response shape, link to schema doc path on branch.

---

## Self-Assessment

### Scope

**scope-Single-Component** — touches `config.py`, one new API module, and server registration only.

### Conf

**conf-Medium** — schema is new but pattern-matches existing config-as-source-of-truth and Flask blueprints; `a16z` content depends on **AST-414** approval.

### Risk

**risk-low** — read-only paths; mis-published `parse_instructions` only affects future ingest tickets, not existing job pipeline.

---

## Self-review vs ASTRAL_CODE_RULES

- §2.1 config as source of truth — satisfied (`BOARD_CONFIG`, no table).
- §3.3 imports — API imports `src.utils.config` helpers only; no `database` from UI except existing patterns.
- No spike artifacts committed under `docs/features/boards/` beyond schema + this plan.

---

## Review

_Build stub — Radia appends findings at Review Posted._

## Radia review

**Reviewed:** `origin/dev`…`origin/sub/AST-379/AST-415-design-data-flow-for-astral-boards`

### What's solid
| Area | Notes |
|------|--------|
| Scope | `BOARD_CONFIG` registry helpers; read-only `GET /api/boards` list + detail; adopted-only filter; schema doc; component tests. |
| Boundaries | No `board_search`, gazer, or ingest — correct for step 1. |
| B2 | `api_boards` → `config` + `ui.auth` only. |

### Issues
| Severity | Item |
|----------|------|
| **fix-now** | 0 |
| **discuss** | 1 — `BOARD_CONFIG` is `{}` on branch (valid per plan); **416+** need adopted keys before creates work. Malformed adopted entries could 500 on list — engineer-registry risk only. |
| **advisory** | 1 — Tests could assert list payload omits heavy fields (`parse_instructions`); optional hardening. |

### Recommended actions
| Action | Owner |
|--------|--------|
| Cherry-pick doc commit | Ada |
| Land adopted board keys from spikes (**AST-414** / Phase 4) in follow-on config commits | Ada / Susan |

## Resolution

**2026-05-22 — Review Posted → User Testing (Ada)**

- **fix-now:** none — Radia review confirmed 0 product defects.
- **Action:** Merged Radia doc commit `fa205861` on `sub/AST-379/AST-415-design-data-flow-for-astral-boards`; no additional product commits.
- **Discuss:** empty `BOARD_CONFIG` until **AST-414** is expected per plan; downstream **416+** waits on adopted keys.
