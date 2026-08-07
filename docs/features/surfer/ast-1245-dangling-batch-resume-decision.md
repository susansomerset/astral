# AST-1245 — Dangling-batch resume decision API

**Linear:** [AST-1245](https://linear.app/astralcareermatch/issue/AST-1245/dangling-batch-resume-decision-api-resume-an-interrupted-batch)
**Parent:** [AST-1177](https://linear.app/astralcareermatch/issue/AST-1177/resume-an-interrupted-batch) — Resume an interrupted batch
**Publish ref:** `origin/sub/AST-1177/AST-1245-dangling-batch-resume-decision`

Authenticated, owner-scoped server decision: whether this candidate has a non-terminal Surfer batch, what remains and how old it is (enough to speak plainly in the offer), and whether resume is allowed; reject foreign batch ids. Config-driven offer copy. No expiry or staleness logic — batches remain offerable indefinitely (parent Open question 2). Does **not** own the extension wake/prompt UI or login-wall wait (siblings AST-1250 / AST-1251); does **not** own worklist persistence (**AST-1169** / **AST-1229**).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `SURFER_RESUME_CONFIG` (offer template + age-phrase buckets); document in module header | utils |
| `src/core/surfer.py` | Add `decide_surfer_batch_resume` (+ age/remaining helpers); `debug` threaded with contract logs | core |
| `src/ui/api/api_surfer.py` | Authenticated `GET …/resume_decision` thin wrapper over core (create blueprint if missing) | ui |
| `src/ui/server.py` | Register `surfer_bp` only if this ticket creates the blueprint (skip if already registered) | ui |

**No changes expected:** `surfer_batch` schema / pointer / URL outcome writers (**AST-1229**), search-page create (**AST-1230**), batch-scoped intake HTTP remaining-work query (**AST-1231**), extension wake/prompt (**AST-1250**), login-wall wait (**AST-1251**), pacing (**AST-1236**), cancel/discard (**AST-1176**), `tests/` / bible (Betty after Code Complete).

⚠️ **Decision — consume AST-1229; do not reimplement persistence:** After `sync-child.sh`, `get_active_surfer_batch`, `database.get_surfer_batch`, `SURFER_BATCH_CONFIG`, and `_is_terminal_status` / URL outcome terminal flags must exist (from **AST-1229**, rolled up via `origin/dev` or `origin/ftr/AST-1177` once Chuckles merges). If they are missing at build start, **stop and comment on the parent** — do not invent a parallel batch table or pointer.

⚠️ **Decision — remaining work from URL outcomes, not a new HTTP remaining-work route:** Parent says this epic consumes AST-1169 remaining-work answers. Remaining URLs = worklist entries whose `outcome` is **non-terminal** per `SURFER_BATCH_CONFIG["url_outcomes"][outcome]["terminal"]` (same vocabulary AST-1229 established; same definition AST-1231's mid-run remaining-work query must use). If at build time `src/core/surfer.py` already exports a public remaining-work helper from AST-1231 (name TBD on that plan), **call that helper** instead of duplicating the filter. Do **not** add a second remaining-work GET route here.

## Preflight (before Stage 1)

**Done when:** Epic worktree has AST-1229 Surfer batch surfaces importable; plan file is the only intentional change so far.

1. Re-run `~/.cursor/scripts/git/sync-child.sh sub/AST-1177/AST-1245-dangling-batch-resume-decision --ftr AST-1177 --worktree /home/susan/astral-AST-1177/`.
2. Verify:

```bash
~/astral/.venv/bin/python -c "
from src.core.surfer import get_active_surfer_batch
from src.utils.config import SURFER_BATCH_CONFIG
assert 'statuses' in SURFER_BATCH_CONFIG and 'url_outcomes' in SURFER_BATCH_CONFIG
assert SURFER_BATCH_CONFIG['candidate_data_lifecycle_key'] == 'active_surfer_batch_id'
print('ok', sorted(SURFER_BATCH_CONFIG['statuses']))
"
```

3. If import fails: **stop**, comment on **AST-1177** with the import error — need AST-1229 on the integration line. Do not proceed to Stage 1.

## Stage 1: `SURFER_RESUME_CONFIG`

**Done when:** `SURFER_RESUME_CONFIG` is importable with the keys below; module docstring lists the block; asserts pass; `python3 -m py_compile src/utils/config.py` succeeds; no staleness / expiry keys added anywhere.

1. In `src/utils/config.py` module docstring `Config sections:`, add:
   `SURFER_RESUME_CONFIG — Surfer dangling-batch resume offer copy + age-phrase buckets (AST-1245)`.
2. Place the block **after** `SURFER_BATCH_CONFIG` (and its asserts) when that block is present; if `SURFER_PACING_CONFIG` sits between other Surfer blocks, keep resume config adjacent to `SURFER_BATCH_CONFIG` (resume consumes batch vocab, not pacing). Add:

```python
# AST-1245: dangling-batch resume offer (server decision + copy). No expiry window.
SURFER_RESUME_CONFIG = {
    # Placeholders: {age_phrase}, {remaining_count}. Core fills both; UI does not rewrite.
    "offer_message_template": (
        "Looks like we didn't finish a batch from {age_phrase} — "
        "want to keep going? ({remaining_count} left)"
    ),
    # First bucket with age_seconds >= min_seconds wins. List MUST be sorted
    # descending by min_seconds (asserted below). Static "phrase" OR
    # "phrase_template" + "unit_seconds" (n = max(1, age_seconds // unit_seconds)).
    "age_phrase_buckets": [
        {"min_seconds": 30 * 86400, "phrase": "over a month ago"},
        {
            "min_seconds": 14 * 86400,
            "phrase_template": "{n} weeks ago",
            "unit_seconds": 7 * 86400,
        },
        {"min_seconds": 7 * 86400, "phrase": "a week ago"},
        {
            "min_seconds": 2 * 86400,
            "phrase_template": "{n} days ago",
            "unit_seconds": 86400,
        },
        {"min_seconds": 86400, "phrase": "a day ago"},
        {
            "min_seconds": 2 * 3600,
            "phrase_template": "{n} hours ago",
            "unit_seconds": 3600,
        },
        {"min_seconds": 3600, "phrase": "an hour ago"},
        {
            "min_seconds": 2 * 60,
            "phrase_template": "{n} minutes ago",
            "unit_seconds": 60,
        },
        {"min_seconds": 0, "phrase": "just now"},
    ],
}

_resume_buckets = SURFER_RESUME_CONFIG["age_phrase_buckets"]
assert isinstance(SURFER_RESUME_CONFIG["offer_message_template"], str)
assert "{age_phrase}" in SURFER_RESUME_CONFIG["offer_message_template"]
assert "{remaining_count}" in SURFER_RESUME_CONFIG["offer_message_template"]
assert isinstance(_resume_buckets, list) and _resume_buckets
assert all(
    isinstance(b.get("min_seconds"), (int, float)) and b["min_seconds"] >= 0
    for b in _resume_buckets
)
assert all(
    ("phrase" in b) ^ ("phrase_template" in b)
    for b in _resume_buckets
), "each age bucket needs exactly one of phrase / phrase_template"
assert all(
    "unit_seconds" in b and b["unit_seconds"] > 0
    for b in _resume_buckets
    if "phrase_template" in b
)
_mins = [b["min_seconds"] for b in _resume_buckets]
assert _mins == sorted(_mins, reverse=True), (
    "SURFER_RESUME_CONFIG age_phrase_buckets must be descending by min_seconds"
)
assert _mins[-1] == 0, "final age bucket must cover age_seconds >= 0"
```

⚠️ **Decision — separate `SURFER_RESUME_CONFIG`, not keys on `SURFER_BATCH_CONFIG`:** Batch status/outcome vocab is AST-1229; offer copy and age phrasing are this epic's UX contract. Folding them would force AST-1229 revisits when copy changes.

⚠️ **Decision — no staleness / expiry keys:** Parent Open question 2 settled. Do not add `stale_after_hours`, expiry sweep, or a third terminal status in this ticket or this config block.

⚠️ **Decision — age phrasing is config-only:** Core must not hardcode English age strings. Bucket list is the single source; copy edits do not require a code change beyond config.

3. Verify Stage 1:

```bash
~/astral/.venv/bin/python -c "
from src.utils.config import SURFER_RESUME_CONFIG
assert '{age_phrase}' in SURFER_RESUME_CONFIG['offer_message_template']
assert SURFER_RESUME_CONFIG['age_phrase_buckets'][-1]['min_seconds'] == 0
"
~/astral/.venv/bin/python -m py_compile src/utils/config.py
```

**Ritual:** `code(AST-1245): SURFER_RESUME_CONFIG offer copy + age buckets`

## Stage 2: Core `decide_surfer_batch_resume`

**Done when:** Calling `decide_surfer_batch_resume` for a candidate with a RUNNING batch that has non-terminal URLs returns `resume_allowed=True` with `remaining_count` / `remaining_urls` / `age_phrase` / filled `offer_message`; a candidate with no active batch returns `resume_allowed=False` and `offer_message=None`; an explicit foreign `batch_id` raises `PermissionError`; unknown `batch_id` raises `LookupError`; terminal batch (explicit id or cleared pointer) never sets `resume_allowed=True`; with `debug=True`, contract logs show found + recorded; `python3 -m py_compile src/core/surfer.py` succeeds.

1. In `src/core/surfer.py`, keep **public functions first**, helpers below (`astral.standards.public-then-helpers`). Add imports as needed: `SURFER_RESUME_CONFIG` from config; `datetime`/`timezone` already present for `started_at` parsing.

2. Add public entrypoint (exact signature):

```python
def decide_surfer_batch_resume(
    candidate_id: str,
    batch_id: Optional[str] = None,
    *,
    debug: bool = False,
) -> Dict[str, Any]:
    """Owner-scoped resume decision for a dangling Surfer batch (AST-1245).

    Returns a plain dict (never mutates batch status). Raises:
      ValueError — missing candidate_id / candidate not found
      LookupError — explicit batch_id not found
      PermissionError — explicit batch_id owned by another candidate
    """
```

3. Behavior (literal — do not invent alternate branches):

   a. `logger.set_debug_flag(debug)`. Strip `candidate_id`; if empty raise `ValueError("candidate_id is required")`. If `get_candidate(cid)` is `None`, raise `ValueError(f"Candidate not found: {cid}")`.
   b. Resolve the batch row:
      - If `batch_id` is provided (non-empty after strip): `database.get_surfer_batch(bid)`. If `None`, raise `LookupError(f"surfer_batch not found: {bid}")`. If `str(batch["candidate_id"]) != cid`, raise `PermissionError(f"foreign surfer_batch: {bid}")`.
      - If `batch_id` omitted / empty: `batch = get_active_surfer_batch(cid, debug=debug)` (may be `None`).
   c. If `batch is None` **or** `_is_terminal_status(str(batch.get("status") or ""))`: return the **denied** payload (step 3e) with `batch_id` set to the looked-up id when an explicit terminal row was loaded, else `None`. Do **not** offer resume for COMPLETED / CANCELLED (AC3).
   d. Compute remaining:
      - Prefer an existing public remaining-work helper from AST-1231 if present on the module at build time.
      - Otherwise: `remaining_urls = [entry["url"] for entry in (batch.get("urls") or []) if not _is_terminal_url_outcome(str((entry or {}).get("outcome") or ""))]`, preserving worklist order. Skip entries missing `url`.
      - `remaining_count = len(remaining_urls)`.
      - If `remaining_count == 0` while status is still non-terminal: still allow resume (`resume_allowed=True`) — delivered-but-unresolved URLs are non-terminal outcomes so they already appear in remaining; a true empty remaining with RUNNING is an edge AST-1229 auto-complete should normally prevent. Do **not** invent a forced COMPLETED transition here.
   e. Age: parse `batch["started_at"]` as UTC `"%Y-%m-%d %H:%M:%S"` (AST-1229 format). `age_seconds = max(0, int((now_utc - started).total_seconds()))`. Resolve `age_phrase` via `_age_phrase(age_seconds)` (helper below). Format `offer_message` with `SURFER_RESUME_CONFIG["offer_message_template"].format(age_phrase=..., remaining_count=...)`.
   f. **Allowed** return shape (exact keys):

```python
{
    "resume_allowed": True,
    "batch_id": batch["batch_id"],
    "status": batch["status"],
    "started_at": batch["started_at"],
    "age_seconds": age_seconds,
    "age_phrase": age_phrase,
    "remaining_count": remaining_count,
    "remaining_urls": remaining_urls,
    "offer_message": offer_message,
}
```

   g. **Denied** return shape (exact keys — same key set, nulls/zeros as below):

```python
{
    "resume_allowed": False,
    "batch_id": batch_id_or_none,
    "status": status_or_none,
    "started_at": None,
    "age_seconds": None,
    "age_phrase": None,
    "remaining_count": 0,
    "remaining_urls": [],
    "offer_message": None,
}
```

   For an explicit terminal batch, fill `batch_id` and `status` from the row so the client can see why; leave age/offer null.

4. Helpers (below public section):

   - `_age_phrase(age_seconds: int) -> str` — walk `SURFER_RESUME_CONFIG["age_phrase_buckets"]` in list order; first bucket with `age_seconds >= min_seconds` wins. If bucket has `phrase`, return it. If `phrase_template`, compute `n = max(1, int(age_seconds // unit_seconds))` and return `phrase_template.format(n=n)`.
   - Reuse existing `_is_terminal_status` / `_is_terminal_url_outcome`; do **not** compare to the string literals `"COMPLETED"` / `"CANCELLED"` / `"success"` for business rules.

5. Debug contract (`debug=True` only):
   - One `debug_index` header for the decision (style D): function context `decide_surfer_batch_resume`, `index 1/1`, primary id = `candidate_id` (and batch_id when known), ` -> ` outcome `resume_allowed` true/false.
   - Working detail lines (`debug_detail`): pointer/batch found or missing; status; remaining_count; age_seconds / age_phrase; whether foreign/terminal/denied path applied; final `offer_message` (or `None`).
   - No new `logger.info("[DEBUG] …")`. No debug emission when `debug=False`.

⚠️ **Decision — read-only decision; no accept/decline mutation:** Sibling AST-1250 owns yes/no UX and restarting fan-out. This function never calls `transition_surfer_batch_status` and never clears the pointer. Declining is a no-op by construction.

⚠️ **Decision — `PermissionError` for foreign batch ids:** Distinct from `LookupError` (unknown) and `ValueError` (bad candidate). UI maps these to 403 / 404 / 400 without parsing free-form ownership prose.

⚠️ **Decision — optional `batch_id` validates ownership even when it is also the active pointer:** Always compare `batch["candidate_id"]` to the path candidate when an explicit id is supplied. Do not trust the client.

6. Verify Stage 2 (compile + a minimal in-process check if a candidate/batch fixture is awkward without Betty — compile is mandatory):

```bash
~/astral/.venv/bin/python -m py_compile src/core/surfer.py
~/astral/.venv/bin/python -c "
from src.core import surfer
assert hasattr(surfer, 'decide_surfer_batch_resume')
"
```

**Ritual:** `code(AST-1245): decide_surfer_batch_resume core decision`

## Stage 3: Authenticated `resume_decision` GET

**Done when:** `GET /api/surfer/candidates/<candidate_id>/resume_decision` with a valid Bearer returns the core decision JSON; unauthenticated → 401; unknown candidate → 404; foreign `batch_id` query → 403; unknown `batch_id` → 404; blueprint registered; UI imports core + utils only (never data/external); `python3 -m py_compile src/ui/api/api_surfer.py` succeeds.

1. **Blueprint file:**
   - If `src/ui/api/api_surfer.py` already exists (e.g. AST-1236 pacing route): **append** the resume route; keep existing `pacing_config` untouched; update the module docstring to mention AST-1245.
   - If missing: create the file with:

```python
"""Surfer extension API (AST-1245 resume decision; later Surfer routes may join)."""

from flask import Blueprint, jsonify, request

from ui.auth import require_auth
from src.core.surfer import decide_surfer_batch_resume

surfer_bp = Blueprint("surfer", __name__, url_prefix="/api/surfer")
```

2. Add route (exact path and method):

```python
@surfer_bp.route(
    "/candidates/<candidate_id>/resume_decision",
    methods=["GET"],
)
@require_auth
def resume_decision(candidate_id: str):
    debug = str(request.args.get("debug", "")).lower() in ("1", "true", "yes")
    batch_id = request.args.get("batch_id")  # optional
    try:
        payload = decide_surfer_batch_resume(
            candidate_id,
            batch_id=batch_id,
            debug=debug,
        )
    except ValueError as e:
        msg = str(e)
        if msg.startswith("Candidate not found"):
            return jsonify({"error": msg}), 404
        return jsonify({"error": msg}), 400
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    return jsonify(payload), 200
```

⚠️ **Decision — path under `/api/surfer/candidates/<candidate_id>/…`:** Candidate-scoped like meteorite (`/api/candidates/<id>/meteorite/…`) but kept on the Surfer blueprint namespace introduced by AST-1236. Do not hang this off `api_admin` or `api_candidate`.

⚠️ **Decision — GET, not POST:** Decision is read-only; GET matches pacing_config and avoids implying a mutation. Accept/decline POSTs belong to AST-1250 if needed later.

⚠️ **Decision — `debug` query flag only:** Mirror intake's explicit debug query (`debug=1|true|yes`). Do not invent a body.

3. **Server registration** — only if this ticket created `api_surfer.py` and `surfer_bp` is not already registered. In `src/ui/server.py`, next to other API blueprints (after `meteorite_bp` is fine):

```python
from ui.api.api_surfer import surfer_bp  # noqa: E402
app.register_blueprint(surfer_bp)
```

If `surfer_bp` is already imported/registered, leave `server.py` unchanged.

4. Verify Stage 3:

```bash
PYTHONPATH=src ~/astral/.venv/bin/python -m py_compile src/ui/api/api_surfer.py
PYTHONPATH=src ~/astral/.venv/bin/python -c "
from ui.api.api_surfer import surfer_bp
rules = [str(r) for r in surfer_bp.deferred_functions]  # existence smoke
from ui.api import api_surfer
assert hasattr(api_surfer, 'resume_decision')
"
```

(HTTP smoke is Betty/UAT — do not add tests here.)

**Ritual:** `code(AST-1245): GET resume_decision authenticated route`

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- Completes a stage on the epic worktree, commits, and publishes to `origin/sub/AST-1177/AST-1245-dangling-batch-resume-decision` before the next stage.

## Self-Assessment

**Scope:** `Single-Component` — one config block, one core decision function on the existing Surfer module, one authenticated GET on the Surfer blueprint; no extension UI and no schema change.

**Conf:** `Medium` — AST-1229 surfaces and path patterns are clear, but this branch may still be waiting on AST-1169 rollup at build time, and remaining-work may land as a shared helper from AST-1231 mid-flight (plan already routes that fork).

**Risk:** `Medium` — a wrong foreign-batch check or terminal-status offer would leak another candidate's worklist or re-prompt completed runs; dispatcher claim paths are untouched so regression surface outside Surfer is low if the plan is followed.

## CODE_RULES self-review

- **§1.3 DRY / public-then-helpers:** Stage 2 places `decide_surfer_batch_resume` with other public Surfer entrypoints; age/remaining helpers below.
- **§2.1 config:** Offer copy + age buckets in `SURFER_RESUME_CONFIG`; terminal vocab stays in `SURFER_BATCH_CONFIG` (no hardcoded status/outcome sets).
- **§2.4 batch-id-first:** Data reads go through existing `get_surfer_batch(batch_id)` / `get_active_surfer_batch`; no new claim/clear.
- **§2.6 / `astral.state.core-decides-transitions`:** Core decides `resume_allowed`; UI only maps exceptions to HTTP. No status transition in this ticket.
- **§2.9 / `astral.patterns.require-auth-on-protected-endpoints`:** `@require_auth` on the route.
- **§3.2 / `astral.layers.import-direction`:** UI → core + utils only; no UI → data.
- **§1.5.1 debug contract:** Gated `debug_index` / `debug_detail` only when `debug=True`.
- **No staleness:** Asserted by config Decision + Files Changed exclusions.

No unresolved statute conflicts; Conf is not `!!-NONE`.
