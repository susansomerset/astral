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
| `src/ui/api/api_surfer.py` | Append authenticated `GET /<candidate_id>/surfer/resume_decision` on the existing AST-1235 `surfer_bp` (`url_prefix="/api/candidates"`) | ui |

**No changes expected:** `src/ui/server.py` (`surfer_bp` already registered on `origin/dev`), `surfer_batch` schema / pointer / URL outcome writers (**AST-1229**), search-page create (**AST-1230**), mid-run remaining-work HTTP query (**AST-1231**), extension wake/prompt (**AST-1250**), login-wall wait (**AST-1251**), pacing (**AST-1236** — its `/api/surfer` blueprint is a divergence AST-1174 must settle; this ticket does not create or rename that blueprint), cancel/discard (**AST-1176**), `tests/` / bible (Betty after Code Complete).

⚠️ **Decision — consume AST-1229; do not reimplement persistence:** After `sync-child.sh`, `get_active_surfer_batch`, `database.get_surfer_batch`, `SURFER_BATCH_CONFIG`, and `_is_terminal_status` / URL outcome terminal flags must exist (from **AST-1229**, rolled up via `origin/dev` or `origin/ftr/AST-1177` once Chuckles merges). If they are missing at build start, **stop and comment on the parent** — do not invent a parallel batch table or pointer.

⚠️ **Decision — remaining URL list ships on this decision payload for AST-1250:** Parent says this epic consumes AST-1169 remaining-work answers. Remaining URLs = worklist entries whose `outcome` is **non-terminal** per `SURFER_BATCH_CONFIG["url_outcomes"][outcome]["terminal"]` (same vocabulary AST-1229 established). This ticket returns `remaining_urls` + `remaining_count` on the resume-decision response so AST-1250 can continue fan-out under the same `batch_id` without a second round-trip. That is **not** AST-1231's mid-run remaining-work GET (progress during an active fan-out) — do **not** add a second remaining-work route here. If at build time `src/core/surfer.py` already exports a public remaining-work helper from AST-1231, **call that helper** instead of duplicating the filter; still return the list on this decision payload.

⚠️ **Decision — pin absolute URL to `origin/dev` AST-1235 blueprint:** On `origin/dev`, `src/ui/api/api_surfer.py` is the Surfer **consent** blueprint: `Blueprint("surfer", __name__, url_prefix="/api/candidates")`, already registered in `server.py`. Absolute endpoint for this ticket: **`GET /api/candidates/<candidate_id>/surfer/resume_decision`**. Do **not** invent `/api/surfer/…`, do **not** create a second blueprint, and do **not** nest `/candidates/` under the existing prefix (that would yield `/api/candidates/candidates/…`). AST-1250 builds its wake offer against this absolute URL.

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

**Done when:** Calling `decide_surfer_batch_resume` for a candidate with a RUNNING batch that has non-terminal URLs returns `resume_allowed=True` with `remaining_count` / `remaining_urls` / `age_phrase` / filled `offer_message`; a candidate with no active batch returns `resume_allowed=False` and `offer_message=None`; a non-terminal batch with `remaining_count == 0` returns `resume_allowed=False` (no `"0 left"` offer); an explicit foreign `batch_id` raises `PermissionError`; unknown `batch_id` raises `LookupError`; terminal batch (explicit id or cleared pointer) never sets `resume_allowed=True`; with `debug=True`, contract logs show found + recorded; `python3 -m py_compile src/core/surfer.py` succeeds.

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
      - If `remaining_count == 0` while status is still non-terminal: return the **denied** payload (step 3g) with `batch_id` / `status` from the row, `remaining_count=0`, `remaining_urls=[]`, `offer_message=None`. Do **not** offer `"…(0 left)"` and do **not** invent a forced COMPLETED transition here (AST-1229 owns auto-complete). Rationale: AST-1250 must not start fan-out over an empty worklist; a true zero-remaining RUNNING row is an edge, not a resume offer.
   e. Age (only when offering): parse `batch["started_at"]` as UTC `"%Y-%m-%d %H:%M:%S"` (AST-1229 format). `age_seconds = max(0, int((now_utc - started).total_seconds()))`. Resolve `age_phrase` via `_age_phrase(age_seconds)` (helper below). Format `offer_message` with `SURFER_RESUME_CONFIG["offer_message_template"].format(age_phrase=..., remaining_count=...)`.
   f. **Allowed** return shape (exact keys) — only when non-terminal **and** `remaining_count > 0`:

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

   For an explicit terminal batch **or** zero-remaining non-terminal edge, fill `batch_id` and `status` from the row so the client can see why; leave age/offer null.

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

⚠️ **Decision — path-scoped ownership (acknowledged limit):** With no `batch_id`, any authenticated caller who knows a `candidate_id` can read that candidate's active batch decision (including `remaining_urls`). This matches the house posture today (`@require_auth` + sibling Surfer consent routes trust the path id the same way). This ticket does **not** bind Stytch `g.user` to candidate ownership. Ticket language "owner-scoped" means **batch ownership vs path candidate** (foreign `batch_id` → 403), not caller-to-candidate binding.

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

**Done when:** `GET /api/candidates/<candidate_id>/surfer/resume_decision` with a valid Bearer returns the core decision JSON; unauthenticated → 401; unknown candidate → 404; foreign `batch_id` query → 403; unknown `batch_id` → 404; route lives on the existing AST-1235 `surfer_bp`; UI imports core + utils only (never data/external); `python3 -m py_compile src/ui/api/api_surfer.py` succeeds; `src/ui/server.py` is untouched.

1. **Blueprint file (pinned to `origin/dev`):** `src/ui/api/api_surfer.py` **already exists** as the AST-1235 Surfer consent module (`Blueprint("surfer", __name__, url_prefix="/api/candidates")`, with `_debug_flag()` and consent GET/PUT). **Append** the resume route to that file. Update the module docstring to mention AST-1245 alongside AST-1235. Keep consent routes untouched. Do **not** create a new blueprint, do **not** change `url_prefix`, do **not** invent an `/api/surfer` module (AST-1236's divergent prefix is out of scope here).

2. Add route (exact path and method — absolute URL after prefix = `/api/candidates/<candidate_id>/surfer/resume_decision`):

```python
@surfer_bp.route(
    "/<candidate_id>/surfer/resume_decision",
    methods=["GET"],
)
@require_auth
def resume_decision(candidate_id: str):
    batch_id = request.args.get("batch_id")  # optional
    try:
        payload = decide_surfer_batch_resume(
            candidate_id,
            batch_id=batch_id,
            debug=_debug_flag(),
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

Add `from src.core.surfer import decide_surfer_batch_resume` to the existing imports (keep `get_candidate` / consent imports as they are).

⚠️ **Decision — absolute URL `GET /api/candidates/<candidate_id>/surfer/resume_decision`:** Matches sibling consent routes (`/<candidate_id>/surfer/consent`) on the same blueprint. AST-1250 must call this exact path.

⚠️ **Decision — GET, not POST:** Decision is read-only; avoids implying a mutation. Accept/decline POSTs belong to AST-1250 if needed later.

⚠️ **Decision — reuse `_debug_flag()` (DRY / §1.3):** Do **not** inline `request.args.get("debug")…`. Call the module's existing `_debug_flag()`, which already routes through `ui_llm_debug(explicit_debug=…)` like the consent handlers.

3. **Do not edit `src/ui/server.py`.** `surfer_bp` is already imported and registered on `origin/dev`.

4. Verify Stage 3:

```bash
PYTHONPATH=src ~/astral/.venv/bin/python -m py_compile src/ui/api/api_surfer.py
PYTHONPATH=src ~/astral/.venv/bin/python -c "
from ui.api import api_surfer
assert hasattr(api_surfer, 'resume_decision')
assert api_surfer.surfer_bp.url_prefix == '/api/candidates'
"
```

(HTTP smoke is Betty/UAT — do not add tests here.)

**Ritual:** `code(AST-1245): GET resume_decision on AST-1235 surfer_bp`

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- Completes a stage on the epic worktree, commits, and publishes to `origin/sub/AST-1177/AST-1245-dangling-batch-resume-decision` before the next stage.

## Self-Assessment

**Scope:** `Single-Component` — one config block, one core decision function on the existing Surfer module, one authenticated GET appended to the existing AST-1235 `api_surfer.py` blueprint; no extension UI, no schema change, no `server.py` touch.

**Conf:** `high` — route is pinned to the real `origin/dev` blueprint (`/api/candidates` + `/<candidate_id>/surfer/…`); remaining-list ownership and zero-remaining deny are explicit; AST-1229 dependency still gated by Preflight.

**Risk:** `Medium` — a wrong foreign-batch check or terminal-status offer would leak another candidate's worklist or re-prompt completed runs; path-scoped (not caller-scoped) ownership is an acknowledged house-posture limit; dispatcher claim paths are untouched.

## CODE_RULES self-review

- **§1.3 DRY / public-then-helpers:** Stage 2 places `decide_surfer_batch_resume` with other public Surfer entrypoints; age/remaining helpers below. Stage 3 reuses `_debug_flag()` (no inline duplicate).
- **§2.1 config:** Offer copy + age buckets in `SURFER_RESUME_CONFIG`; terminal vocab stays in `SURFER_BATCH_CONFIG` (no hardcoded status/outcome sets).
- **§2.4 batch-id-first:** Data reads go through existing `get_surfer_batch(batch_id)` / `get_active_surfer_batch`; no new claim/clear.
- **§2.6 / `astral.state.core-decides-transitions`:** Core decides `resume_allowed`; UI only maps exceptions to HTTP. No status transition in this ticket.
- **§2.9 / `astral.patterns.require-auth-on-protected-endpoints`:** `@require_auth` on the route.
- **§3.2 / `astral.layers.import-direction`:** UI → core + utils only; no UI → data.
- **§1.5.1 debug contract:** Gated `debug_index` / `debug_detail` only when `debug=True` (via `_debug_flag()` → core).
- **No staleness:** Asserted by config Decision + Files Changed exclusions.

No unresolved statute conflicts; Conf is not `!!-NONE`.

## Revisions

Revision 1 — 2026-08-07
Driven by: Joan `[plan-discuss] round=1 concern` (REVISE) — Stage 3 route vs `origin/dev` AST-1235 blueprint; duplicate debug-flag parsing; remaining_urls / zero-remaining / path-scoped ownership discuss items; drop unused `server.py` row.
Changes: Absolute URL pinned to `GET /api/candidates/<candidate_id>/surfer/resume_decision` on existing `surfer_bp` (`url_prefix="/api/candidates"`); Stage 3 appends only, reuses `_debug_flag()`, leaves `server.py` untouched; `remaining_urls` explicitly owned here for AST-1250 (not AST-1231 mid-run GET); zero-remaining RUNNING denies offer; path-scoped ownership limit acknowledged; Conf → high.