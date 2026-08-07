# AST-1247 — Batch outcome totals

**Linear:** [AST-1247](https://linear.app/astralcareermatch/issue/AST-1247/batch-outcome-totals-batch-completion-report-outcome-totals-and-the)
**Parent:** [AST-1180](https://linear.app/astralcareermatch/issue/AST-1180/batch-completion-report-outcome-totals-and-the-new-jobs-notification) — Batch completion report — outcome totals and the new-jobs notification
**Publish ref:** `origin/sub/AST-1180/AST-1247-batch-outcome-totals`

Owner-scoped read that reports a finished Surfer batch's four outcome totals (new, duplicate, not recognized, failed) — always computed in full from the batch worklist URL outcomes, never from a second tally store — plus config-driven notification copy, which supporting totals the payload exposes for display, and a server-built In Review URL. Does **not** render the notification (sibling **AST-1249**), does **not** own the batch record (**AST-1169** / **AST-1229**), and does **not** own cancel/keep/discard UX (**AST-1176**).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Extend `SURFER_BATCH_CONFIG["url_outcomes"]` with report terminal keys; add `SURFER_COMPLETION_CONFIG` (copy, supporting-totals list, In Review path + public-origin env name); module docstring | utils |
| `env.example` | Document `ASTRAL_PUBLIC_ORIGIN` (required for absolute In Review URL) | docs |
| `src/core/surfer.py` | Add `get_surfer_batch_completion_report` (+ small helpers); Style D debug on the summary path | core |
| `src/ui/api/api_surfer.py` | Authenticated `GET /api/surfer/batches/<batch_id>/completion` (create blueprint if absent) | ui |
| `src/ui/server.py` | Register `surfer_bp` if this ticket creates `api_surfer.py` | ui |

**No changes expected:** `src/data/database.py` schema / aggregate count columns (do **not** add `company_job_scan`-style totals on `surfer_batch`); extension / toast rendering (**AST-1249**); discard / cancel routes (**AST-1240** / **AST-1242**); `tests/` / bible (Betty after Code Complete).

## Pre-build dependency gate (before Stage 1 code)

**Done when:** Builder can name the live AST-1229 symbols below on the tip after `sync-child.sh` (or STOP — do not invent the batch entity).

1. `SURFER_BATCH_CONFIG` exists with `statuses`, `url_outcomes`, `initial_status`, `initial_url_outcome`.
2. `src/core/surfer.py` exists with public functions that load batches only via `database.get_surfer_batch` / `database.update_surfer_batch` (no core name `get_surfer_batch`).
3. `surfer_batch` rows carry `urls` as a list of `{url, outcome, updated_at}` and a `status` from config.
4. If any of the above are missing after sync (AST-1169 product not yet on this line / `origin/dev`) → **STOP**, comment on **AST-1247** naming the missing symbols. Do **not** re-implement the Surfer batch entity and do **not** self-cherry-pick from sibling worktrees.

⚠️ **Settlement — totals source (parent planning note):** There are **no** aggregate total columns on `surfer_batch` (AST-1229 deliberately stores the worklist, not gazer-style `new`/`duplicates` ints). This ticket **counts** `urls[].outcome` in core. Do not introduce a second store of counts.

⚠️ **Settlement — URL outcome vocabulary:** AST-1229 shipped coarse terminal outcomes `success` / `failed`. Parent AC2 needs four report categories that partition a completed worklist. This ticket extends `url_outcomes` with `new`, `duplicate`, `not_recognized` (all `terminal: True`) and keeps `failed`. It **removes** `success` (or leaves it absent from report keys and asserts it is gone). Writer contract for **AST-1231** / intake resolution: when classification/ingest resolves a batch URL, set exactly one of `new` | `duplicate` | `not_recognized` | `failed` — never `success`. If tip still contains writers that set `success`, STOP and comment naming them rather than silently remapping.

## Stage 1: Config — report outcomes + `SURFER_COMPLETION_CONFIG`

**Done when:** `SURFER_BATCH_CONFIG["url_outcomes"]` includes the four report terminals (+ existing non-terminals and `discarded` if AST-1240 already landed); `SURFER_COMPLETION_CONFIG` is importable with the keys below; asserts pass; `env.example` documents `ASTRAL_PUBLIC_ORIGIN`; `python3 -m py_compile src/utils/config.py` succeeds (repo venv: `~/astral/.venv/bin/python`).

1. In `src/utils/config.py` module docstring `Config sections:`, add:
   `SURFER_COMPLETION_CONFIG — Surfer batch completion report copy, supporting-totals display, In Review path (AST-1247)`.

2. In `SURFER_BATCH_CONFIG["url_outcomes"]`, apply this vocabulary (preserve `pending` / `delivered`; preserve `discarded` if already present from AST-1240):

```python
    "url_outcomes": {
        "pending": {"terminal": False},
        "delivered": {"terminal": False},
        # Report terminals (AST-1247) — partition a COMPLETED worklist (AC2).
        "new": {"terminal": True},
        "duplicate": {"terminal": True},
        "not_recognized": {"terminal": True},
        "failed": {"terminal": True},
        # "discarded": {"terminal": True},  # only if AST-1240 already added it — do not delete
    },
```

   - **Remove** the `"success"` key if present.
   - Keep `initial_url_outcome` as `"pending"`.
   - Existing AST-1229 asserts over `terminal` bools remain valid; add:

```python
_SURFER_REPORT_OUTCOMES = ("new", "duplicate", "not_recognized", "failed")
assert all(k in SURFER_BATCH_CONFIG["url_outcomes"] for k in _SURFER_REPORT_OUTCOMES)
assert all(SURFER_BATCH_CONFIG["url_outcomes"][k]["terminal"] for k in _SURFER_REPORT_OUTCOMES)
assert "success" not in SURFER_BATCH_CONFIG["url_outcomes"]
```

3. Immediately after `SURFER_BATCH_CONFIG` asserts (or after `SURFER_PROGRESS_CONFIG` if that block sits between — place `SURFER_COMPLETION_CONFIG` next to other Surfer blocks), add:

```python
# ---------------------------------------------------------------------------
# SURFER_COMPLETION_CONFIG: completion notification payload (AST-1247 / AST-1180).
# Server always computes all four totals; supporting_totals controls which of the
# three non-new totals appear in display_totals / message (Open question 2).
# new is never configurable away. Copy uses "added", never "ready to review".
# ---------------------------------------------------------------------------
SURFER_COMPLETION_CONFIG = {
    # Absolute In Review link = os.environ[public_origin_env].rstrip("/") + in_review_path
    "public_origin_env": "ASTRAL_PUBLIC_ORIGIN",
    "in_review_path": "/jobs/in_review",  # must match NAV_CONFIG Jobs → In Review path
    # Which supporting totals may appear in display_totals / message extras.
    # Allowed values: subset of ("duplicate", "not_recognized", "failed") — never "new".
    "supporting_totals": ["duplicate", "not_recognized", "failed"],
    "copy": {
        # {new} required. Used when totals["new"] > 0.
        "with_new": "{new} new jobs added",
        # Plain zero-new case (AC3) — not a success framing with a zero.
        "no_new": "No new jobs added",
        # Optional clause appended when supporting_totals is non-empty and counts > 0.
        # Placeholders: {duplicate}, {not_recognized}, {failed} — only include keys
        # that are in supporting_totals when formatting (omit zero counts).
        "supporting_clause": (
            " ({duplicate} duplicates, {not_recognized} not recognized, {failed} failed)"
        ),
    },
}
```

4. Asserts (literal intent):

```python
_scc = SURFER_COMPLETION_CONFIG
assert _scc["public_origin_env"] == "ASTRAL_PUBLIC_ORIGIN"
assert _scc["in_review_path"] == "/jobs/in_review"
assert "new" not in _scc["supporting_totals"]
assert set(_scc["supporting_totals"]).issubset({"duplicate", "not_recognized", "failed"})
assert "{new}" in _scc["copy"]["with_new"]
assert "ready to review" not in _scc["copy"]["with_new"].lower()
assert "ready to review" not in _scc["copy"]["no_new"].lower()
assert "added" in _scc["copy"]["with_new"].lower()
for _k in ("with_new", "no_new", "supporting_clause"):
    assert isinstance(_scc["copy"][_k], str) and _scc["copy"][_k].strip()
# Cross-check NAV path when NAV_CONFIG is available in this file:
assert any(
    item.get("path") == _scc["in_review_path"]
    for group in NAV_CONFIG
    for item in group.get("items", [])
)
```

   If `NAV_CONFIG` is defined **above** this block, use that assert. If `NAV_CONFIG` is defined **below**, place the NAV cross-check assert immediately after `NAV_CONFIG` instead (do not reorder NAV).

5. In `env.example`, after the deploy / public-host notes (near `ASTRAL_RAILWAY_TEST_HOST_URL` is fine), add:

```bash
# Public web origin for candidate-facing absolute links (Surfer completion In Review URL — AST-1247).
# No trailing slash. Required when serving GET /api/surfer/batches/<id>/completion.
# Local: http://localhost:5173   Railway: https://<your-railway-public-host>
ASTRAL_PUBLIC_ORIGIN=http://localhost:5173
```

6. Verify:

```bash
~/astral/.venv/bin/python -c "
from src.utils.config import SURFER_BATCH_CONFIG, SURFER_COMPLETION_CONFIG
assert 'new' in SURFER_BATCH_CONFIG['url_outcomes']
assert 'success' not in SURFER_BATCH_CONFIG['url_outcomes']
assert 'new' not in SURFER_COMPLETION_CONFIG['supporting_totals']
"
~/astral/.venv/bin/python -m py_compile src/utils/config.py
```

⚠️ **Decision — extend URL outcomes in place, no aggregate columns:** Parent forbids a second count store. The four report keys **are** the terminal worklist outcomes for a completed run. Auto-complete (`requires_all_urls_terminal`) continues to key off `terminal: True` flags — all four report outcomes qualify.

⚠️ **Decision — `supporting_totals` is display-only:** Core always returns full `totals` with all four keys. `display_totals` / message extras honor `supporting_totals`. Changing config must change the message without code or extension rebuild (AC10); debug and `totals` stay complete (AC10).

⚠️ **Decision — In Review absolute URL via env origin + config path:** Path is the same everywhere (`/jobs/in_review`); origin is environment-specific → `os.environ[SURFER_COMPLETION_CONFIG["public_origin_env"]]` with **no** `.get()` / no fallback (crash if missing when building the URL). Sibling **AST-1249** renders the link; this ticket supplies `in_review_url` in the payload.

**Ritual:** `code(AST-1247): SURFER_COMPLETION_CONFIG + report url_outcomes`

## Stage 2: Core — `get_surfer_batch_completion_report`

**Done when:** Given an owned COMPLETED batch whose every URL outcome is one of the four report keys, the function returns `ready=True` with full `totals` (sum == `len(urls)`), `display_totals` filtered by config, a rendered `message`, and `in_review_url`; zero-new uses `copy["no_new"]` (AC3); RUNNING / incomplete worklist returns `ready=False` with `reason="incomplete"` and no message (AC5); CANCELLED with any `discarded` URL outcome returns `ready=False` with `reason="discarded"` (AC6 discard); CANCELLED without discarded returns `ready=True` with totals counted only over URLs whose outcomes are in the four report keys (AC6 keep); foreign `candidate_id` raises with `.error_code = "surfer_batch_not_owned"` (AC7); `debug=True` emits Style D found + reported headers; `debug=False` emits no Style D; `py_compile` succeeds.

1. In `src/core/surfer.py`, import `SURFER_COMPLETION_CONFIG` alongside `SURFER_BATCH_CONFIG`. Add `import os` if not present.

2. Add public function **above** the helpers section:

```python
def get_surfer_batch_completion_report(
    batch_id: str,
    candidate_id: str,
    *,
    debug: bool = False,
) -> Dict[str, Any]:
    """Owner-scoped completion summary for a Surfer batch (AST-1247).

    Returns one of:
      {"ready": False, "reason": "incomplete"|"discarded"|"not_found", "batch_id": ...}
      {"ready": True, "batch_id", "status", "totals", "display_totals",
       "message", "in_review_url", "has_new_jobs"}

    Raises:
      ValueError with .error_code:
        surfer_batch_not_owned — candidate_id does not own the batch
        surfer_batch_not_found — missing batch (also acceptable as ready=False reason;
          pick raise for API 404 mapping consistency with discard — prefer raise)
        surfer_batch_totals_incoherent — COMPLETED batch has non-report outcomes
    """
```

3. Behavior (literal order):

   - Strip/validate non-empty `batch_id` and `candidate_id`; else `ValueError`.
   - `logger.set_debug_flag(debug)`.
   - `batch = database.get_surfer_batch(batch_id)`; missing → `ValueError` + `.error_code = "surfer_batch_not_found"`.
   - Ownership: if `str(batch.get("candidate_id") or "") != candidate_id.strip()` → `ValueError` + `.error_code = "surfer_batch_not_owned"`.
   - Let `urls = list(batch.get("urls") or [])`, `status = str(batch.get("status") or "")`.
   - **Debug found:** when `debug=True`, one index header (`func="surfer.get_surfer_batch_completion_report"`, `index=1`, `total=1`, `identifier=batch_id`, `outcome="found"`) plus detail lines: `candidate_id`, `status`, `len(urls)`, and each URL's `outcome`.
   - **Discard gate (AC6):** if any URL outcome equals the config key `"discarded"` (only when that key exists in `SURFER_BATCH_CONFIG["url_outcomes"]`), return `{"ready": False, "reason": "discarded", "batch_id": batch_id}` (no message / no totals). Do not treat CANCELLED alone as discard — keep vs discard is the discarded URL outcome (AST-1240).
   - **Incomplete gate (AC5):** if status is non-terminal (`not _is_terminal_status(status)`) **or** any URL outcome is non-terminal (`not _is_terminal_url_outcome(...)`), return `{"ready": False, "reason": "incomplete", "batch_id": batch_id}`.
     - Exception for CANCELLED keep: status is terminal CANCELLED, URLs may still include `pending` (never visited). For CANCELLED **without** discarded outcomes, **skip** the "any non-terminal URL → incomplete" rule; instead count only URLs whose outcomes are in `_report_outcome_keys()` (defined below). Pending/delivered left after cancel-keep are omitted from totals (they were not "kept").
   - **Count totals:** initialize `totals = {k: 0 for k in _report_outcome_keys()}`. For each URL entry included in the count set:
     - COMPLETED: every URL must be counted; outcome must be in report keys — else raise `ValueError` + `.error_code = "surfer_batch_totals_incoherent"`.
     - CANCELLED keep: only URLs with report-key outcomes.
     - Increment `totals[outcome]`.
   - COMPLETED integrity (AC2): `sum(totals.values()) == len(urls)`.
   - `display_totals = {"new": totals["new"]}` then for each key in `SURFER_COMPLETION_CONFIG["supporting_totals"]` in config order, add `display_totals[key] = totals[key]`.
   - `has_new_jobs = totals["new"] > 0`.
   - **Message:** if `has_new_jobs`: start from `copy["with_new"].replace("{new}", str(totals["new"]))`; else use `copy["no_new"]` (do **not** substitute a zero into `with_new`). If `supporting_totals` is non-empty, build the supporting clause by taking `copy["supporting_clause"]` and replacing each `{name}` for `name in supporting_totals` with `str(totals[name])`; append that clause to the message **only when** at least one supporting total is `> 0`. If all supporting counts are 0, do not append the clause.
   - **`in_review_url`:** `origin = os.environ[SURFER_COMPLETION_CONFIG["public_origin_env"]]` (no `.get`); `path = SURFER_COMPLETION_CONFIG["in_review_path"]`; `in_review_url = origin.rstrip("/") + path` (path already starts with `/`).
   - **Debug reported:** when `debug=True`, index header `outcome="reported"` with detail: `ready=True`, full `totals`, `display_totals`, `message`, `in_review_url`.
   - Return the ready dict.

4. Helpers (below public API):

```python
def _report_outcome_keys() -> tuple[str, ...]:
    return ("new", "duplicate", "not_recognized", "failed")

def _cancel_status_name() -> str:
    # Unique terminal status with requires_all_urls_terminal False (CANCELLED).
    ...
```

   Prefer reusing an existing `_cancel_status` helper if AST-1240 already added one under that name — do not duplicate. If absent, add `_cancel_status_name` only if needed for status comparison; comparison should use `_is_terminal_status` + `not requires_all_urls_terminal` rather than the literal `"CANCELLED"` string when branching keep vs complete. For COMPLETED detection use `_auto_complete_status()` equality (already in module).

5. Do **not** write to the database in this function (read-only). Do **not** call discard/transition.

6. `~/astral/.venv/bin/python -m py_compile src/core/surfer.py`.

⚠️ **Decision — CANCELLED keep vs discard:** Discard is detected by any URL outcome `discarded` (AST-1240), not by a second batch status. Keep = CANCELLED + no discarded outcomes → report what resolved. Incomplete RUNNING (or non-terminal URLs while still RUNNING) → no summary.

⚠️ **Decision — message assembly stays in core:** `astral.layers.ui-config-driven-business-logic` — UI returns what core computed; it does not format strings or filter totals.

**Ritual:** `code(AST-1247): get_surfer_batch_completion_report`

## Stage 3: Authenticated completion GET

**Done when:** `GET /api/surfer/batches/<batch_id>/completion?candidate_id=<owner>` with a valid Bearer returns 200 and the core dict; missing/invalid session → 401; foreign owner → 403; unknown batch → 404; missing `candidate_id` → 400; incomplete/discarded ready=False still 200 with body (extension polls until ready or gives up — sibling owns UX); `debug` query threads into core; blueprint registered; `py_compile` succeeds.

1. **If** `src/ui/api/api_surfer.py` does **not** exist on the tip, create it:

```python
"""Surfer candidate-facing API (AST-1247 completion; siblings may add progress/discard)."""

from flask import Blueprint, g, jsonify, request

from ui.auth import require_auth
from src.core.surfer import get_surfer_batch_completion_report
from src.utils.deploy_status import ui_llm_debug
from src.utils.logging import get_logger

logger = get_logger(__name__)

surfer_bp = Blueprint("surfer", __name__, url_prefix="/api/surfer")


def _debug_flag() -> bool:
    return ui_llm_debug(
        explicit_debug=request.args.get("debug", "").lower() in ("1", "true", "yes")
    )
```

   If the file **already** exists (progress / pacing / discard from siblings), reuse its blueprint, `_debug_flag` (or equivalent), and logger — add only the completion route + import.

2. Add route:

```python
@surfer_bp.route("/batches/<batch_id>/completion", methods=["GET"])
@require_auth
def surfer_batch_completion(batch_id: str):
    bid = (batch_id or "").strip()
    candidate_id = (request.args.get("candidate_id") or "").strip()
    if not bid:
        return jsonify({"error": "batch_id is required"}), 400
    if not candidate_id:
        return jsonify({"error": "candidate_id is required"}), 400
    debug = _debug_flag()
    try:
        report = get_surfer_batch_completion_report(
            bid, candidate_id, debug=debug
        )
    except ValueError as e:
        code = getattr(e, "error_code", None)
        if code == "surfer_batch_not_found":
            return jsonify({"error": str(e)}), 404
        if code == "surfer_batch_not_owned":
            return jsonify({"error": str(e)}), 403
        return jsonify({"error": str(e)}), 400
    except KeyError as e:
        # Missing ASTRAL_PUBLIC_ORIGIN
        logger.warning("[api_surfer] completion misconfigured: %s", e)
        return jsonify({"error": f"server misconfigured: {e}"}), 500
    except Exception as e:
        logger.warning("[api_surfer] completion failed batch_id=%s: %s", bid, e)
        return jsonify({"error": str(e)}), 502
    return jsonify(report), 200
```

   Do **not** use `g.user` to invent `candidate_id` — request supplies it; ownership is enforced in core against the batch row (same pattern as AST-1240 discard body `candidate_id`).

3. If this ticket created `api_surfer.py`, register in `src/ui/server.py` next to the other blueprint imports/registers:

```python
from ui.api.api_surfer import surfer_bp  # noqa: E402
...
app.register_blueprint(surfer_bp)
```

4. `~/astral/.venv/bin/python -m py_compile src/ui/api/api_surfer.py src/ui/server.py`.

⚠️ **Decision — thin UI, auth on route:** `pattern.ui.admin-endpoint` shape (thin authenticated route over core) without admin-blueprint placement — candidate-facing under `/api/surfer`. `astral.patterns.require-auth-on-protected-endpoints`.

⚠️ **Decision — incomplete/discarded are 200 + `ready: false`:** Keeps polling simple for AST-1249; 403/404 reserved for authz/missing. Do not 204.

**Ritual:** `code(AST-1247): GET surfer batch completion`

## Consumer contract (for AST-1249 — not implemented here)

Extension / notification sibling:

1. Poll or fetch `GET /api/surfer/batches/<batch_id>/completion?candidate_id=<id>` after the batch leaves the active/finishing surface.
2. If `ready` is false and `reason` is `incomplete`, keep waiting / stay on finishing.
3. If `reason` is `discarded`, show nothing (AC6).
4. If `ready` is true, render `message` and link `in_review_url` (new tab). Do **not** recompute totals or pick which supporting counts matter — use `message` / `display_totals` as sent.
5. Do **not** bake notification strings into the extension bundle.

## Writer contract (for AST-1231 / intake — not implemented here)

When a batch-scoped page resolves, set the URL outcome to exactly one of: `new`, `duplicate`, `not_recognized`, `failed`. Map from page_intake / ingest:

| Intake result | URL outcome |
|---------------|-------------|
| Listing created (`outcome=created`) | `new` |
| Listing duplicate | `duplicate` |
| Not recognized / not job-related | `not_recognized` |
| Classification or ingest hard failure | `failed` |

Do not write `success`. Do not invent a parallel totals table.

## Self-Assessment

**Scope:** Single-Component — config + one core read on `src/core/surfer.py` + one authenticated Surfer GET; no schema change and no extension render.

**Conf:** Medium — AST-1229 worklist shape is settled on `origin/sub/AST-1169/…`, but this tip still lacks Surfer until deps land (pre-build gate), and removing `success` requires intake writers to use the four report keys before COMPLETED UAT of AC2.

**Risk:** Medium — wrong incomplete/discard gates or a second count store would lie about finished runs / keep-vs-discard; authz bugs would leak another candidate's summary (AC7).

## Rules check (plan-child §8)

- **§1.3 DRY:** Totals counted once in core; message formatting once; UI does not re-filter.
- **§2.1 config:** Named `SURFER_COMPLETION_CONFIG`; outcome vocabulary in `SURFER_BATCH_CONFIG`; public origin via environ name in config (no hardcoded host); no hardcoded supporting-total sets in branches.
- **§2.4 batch:** `batch_id` first on the route and core signature; no dispatcher claim/release involvement.
- **§2.6 state:** Read-only; does not transition batch or job state.
- **§3.3 imports:** UI → core + utils only; core → data + utils; no ui→data.
- **§3.5 naming:** `get_surfer_batch_completion_report`, `/completion`, `SURFER_COMPLETION_CONFIG`.
- **§1.5.1 debug:** Style D only when `debug=True`; found + reported headers with working detail.
- **§1.4 / no-hardcoded-sets:** Report keys and supporting list live in config; core iterates config/report tuple helpers, does not scatter string sets in UI.
