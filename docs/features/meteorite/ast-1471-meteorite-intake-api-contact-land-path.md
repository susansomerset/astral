# AST-1471 — Meteorite intake API + Contact land path

**Linear:** [AST-1471](https://linear.app/astralcareermatch/issue/AST-1471/meteorite-intake-api-contact-land-path-meteorite-component)  
**Parent:** [AST-1457](https://linear.app/astralcareermatch/issue/AST-1457/meteorite-component) — Meteorite component  
**Publish ref:** `sub/AST-1457/AST-1471-meteorite-intake-api-contact-land-path`

Authenticated listing intake API wraps `land_meteorite` (AST-1470) and returns the same outcome shape. Contact/Estelle scrap path calls `land_meteorite` via a Contact-layer sync wrapper (no parallel create). Inbox/`fetch_email`/gaze retarget is AST-1472.

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/ui/api/api_meteorite.py` (listing intake)
- `src/core/contact.py` (call `land_meteorite`)
- `tests/component/ui/api/test_api_meteorite.py` — Betty owns the test-tree; engineer does not edit (pre-commit ban). Listed so qa-child knows the contract surface.

All Files Changed / Stages stay inside that set. **Out of scope (siblings):** `config.py` / `database.py` / Tracker (AST-1469); `land_meteorite` core / consult enrich (AST-1470 — already on `origin/ftr/AST-1457-meteorite-component`); inbox `fetch_email` / `gaze_email` / gazer / dispatcher / `api_inbox` (AST-1472). Do **not** edit `meteorite.py`, `config.py`, or inbox modules.

**Depends on:** AST-1470 `land_meteorite` + AST-1469 land outcome keys — present after sync with `origin/ftr/AST-1457-meteorite-component` (use `--ftr AST-1457-meteorite-component`, not bare `AST-1457`).

**AC partition:** Parent AC1 Contact portion + AC7 listing intake API. Inbox half of AC1 / AC6 / AC8 → AST-1472.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/ui/api/api_meteorite.py` | Listing intake endpoint wrapping `asyncio.run(land_meteorite(...))`; retarget legacy HTML create route to land; `@require_auth`; return land outcome shape | ui |
| `src/core/contact.py` | Public `contact_land_meteorite` sync wrapper; Estelle turn injects land instructions + runs `land_calls` via that wrapper | core |
| `tests/component/ui/api/test_api_meteorite.py` | Betty / qa-child — intake + auth + outcome-shape coverage | tests |

## Stage 1: API — listing intake wraps `land_meteorite`

**Done when:** Authenticated `POST` listing intake under the meteorite blueprint calls `land_meteorite` with scraps (or legacy `html_body`→text) and returns JSON matching core’s land shape (`outcome`, `outcomes`, `company`, `company_inserted`, `error`). No `create_meteorite_job` import remains in `api_meteorite.py`. Unauthenticated requests 401. Missing candidate maps to 404 when land reports not-found. `debug=False` adds no new debug-contract lines from this thin wrapper.

1. Update `src/ui/api/api_meteorite.py` module docstring: listing intake wraps `land_meteorite`; no email I/O; no admin React surface in this ticket.

2. Replace `from src.core.meteorite import create_meteorite_job` with `from src.core.meteorite import land_meteorite`. Add `import asyncio` (same pattern as `api_inbox.py` / `api_intake.py`).

3. Add helper **`_land_request_payload(data: dict) -> dict`** that builds kwargs for `land_meteorite` from JSON body:
   - Prefer `scraps` when it is a non-empty list of dicts → pass `scraps=…`.
   - Else pass top-level `text`, `job_link`, `employer_name` (strip strings; omit empty).
   - Legacy: if `html_body` is a non-empty string and no scrap/text/link body was supplied, set `text=html_body.strip()` so old AST-1042 callers still land.
   - `debug = bool(data.get("debug", False))`.
   - Do **not** invent enrichment or dedupe rules in UI — only map fields.

4. Add route **`POST /api/candidates/<candidate_id>/meteorite/land`** with `@require_auth` (not `@require_admin` — parent cites listing intake as authenticated adapter; match existing meteorite create auth posture):

```python
@meteorite_bp.route("/candidates/<candidate_id>/meteorite/land", methods=["POST"])
@require_auth
def meteorite_land(candidate_id: str):
    data = request.get_json(silent=True) or {}
    kwargs = _land_request_payload(data)
    try:
        result = asyncio.run(land_meteorite(candidate_id, **kwargs))
    except ValueError as e:
        # Programmer misuse from land (e.g. scraps wrong type) — 400
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.warning("[api_meteorite] land failed candidate_id=%s: %s", candidate_id, e)
        return jsonify({"error": str(e)}), 502
    return _land_http_response(result)
```

5. Add helper **`_land_http_response(result: dict)`** — status from rollup `outcome` using `METEORITE_CONFIG` land keys (import `METEORITE_CONFIG` from `src.utils.config`):
   - `land_outcome_created` → **201**
   - `land_outcome_duplicate_skip` or `land_outcome_superseded` → **200**
   - `land_outcome_error` → if `error` string starts with `candidate not found` → **404**; else → **400**
   - Body JSON (same outcome shape as core — parent AC7):

```python
{
    "outcome": result.get("outcome"),
    "outcomes": result.get("outcomes") or [],
    "company": result.get("company"),
    "company_inserted": bool(result.get("company_inserted")),
    "error": result.get("error"),
}
```

   Do **not** nest the full job blob unless already present inside each `outcomes[]` entry from Tracker — pass through as returned.

6. **Retarget** existing `POST /candidates/<candidate_id>/meteorite/jobs` (`meteorite_create_job`) to the same land path: parse body via `_land_request_payload`, `asyncio.run(land_meteorite(...))`, return `_land_http_response`. Remove all `create_meteorite_job` calls and the AST-1042 201 flat `{astral_job_id, company, state, …}` response shape from this module.

   ⚠️ **Decision — one land shape everywhere:** Legacy `/meteorite/jobs` returns the land outcome shape (not the old create flat fields). Callers that still expect AST-1042 keys must read `outcomes[0].astral_job_id` / top-level `company`. Prefer `/meteorite/land` for new adapters; keep `/jobs` as a thin alias so there is no parallel create in this API.

7. Do **not** register new blueprints in `server.py` (meteorite_bp already registered). Do **not** add React UI.

## Stage 2: Contact — Estelle/Slack scrap path → `land_meteorite`

**Done when:** `contact_land_meteorite(...)` is a public sync entry that `asyncio.run`s `land_meteorite` and returns its dict. Estelle turn live_content documents `land_calls`; when Estelle emits `land_calls`, Contact invokes that wrapper (with bound `astral_candidate_id`) and records results on the turn dict. No Gmail/inbox imports. No `create_meteorite_job`. No edits to `CONTACT_CONFIG` / `config.py` (out of Scope — land is not a candidate_data ACL skill).

1. In `src/core/contact.py` module docstring, note AST-1471: Contact scrap path lands via `contact_land_meteorite` → `land_meteorite`.

2. Late-import `land_meteorite` **inside** the wrapper (avoid load-order surprises with meteorite/consult). Add:

```python
def contact_land_meteorite(
    astral_candidate_id: str,
    *,
    scraps: Optional[List[Dict[str, Any]]] = None,
    text: Optional[str] = None,
    job_link: Optional[str] = None,
    employer_name: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """Contact/Estelle sync entry to land_meteorite (AST-1471)."""
    from src.core.meteorite import land_meteorite
    return asyncio.run(
        land_meteorite(
            astral_candidate_id,
            scraps=scraps,
            text=text,
            job_link=job_link,
            employer_name=employer_name,
            debug=debug,
        )
    )
```

   Ensure `asyncio` is already imported at module top (it is — Estelle turn uses it). Add `Optional`, `List`, `Dict`, `Any` to typing imports if missing for the new signature.

3. In `run_contact_estelle_turn`, after the “## Available Contact skills (ACL)” block and **before** `## Conversation`, append a short land instruction block (same live_content injection pattern as skills — prose lives here, not a new CONTACT_CONFIG skill):

```
## Land meteorite (job scraps)
When the candidate shares a job listing (link and/or text), emit land_calls as a
JSON list. Each item may be either:
  - {"scraps": [ {"text": "...", "job_link": "...", "employer_name": "..."}, ... ]}
  - {"text": "...", "job_link": "...", "employer_name": "..."}  (single scrap)
Omit land_calls when none. Do not invent job content.
```

   ⚠️ **Decision — not a CONTACT_CONFIG skill:** Entity-save skills only merge allowlisted `candidate_data` paths. Landing a job is a different verb; wiring it as `land_calls` beside `skill_calls` keeps Scope inside `contact.py` without inventing a config.py skill ACL row (config is AST-1469’s partition).

4. After the existing `skill_calls` loop (step e), process `land_calls`:

```python
land_results = []
raw_land = parsed.get("land_calls") if isinstance(parsed, dict) else None
land_items = raw_land if isinstance(raw_land, list) else []
for item in land_items:
    if not isinstance(item, dict):
        continue
    if not (isinstance(astral_candidate_id, str) and astral_candidate_id.strip()):
        land_results.append({"ok": False, "error": "no_candidate"})
        continue
    try:
        if isinstance(item.get("scraps"), list) and item["scraps"]:
            land_out = contact_land_meteorite(
                astral_candidate_id, scraps=item["scraps"], debug=debug
            )
        else:
            land_out = contact_land_meteorite(
                astral_candidate_id,
                text=item.get("text") if isinstance(item.get("text"), str) else None,
                job_link=item.get("job_link") if isinstance(item.get("job_link"), str) else None,
                employer_name=(
                    item.get("employer_name")
                    if isinstance(item.get("employer_name"), str)
                    else None
                ),
                debug=debug,
            )
        land_results.append({"ok": True, "result": land_out})
    except Exception as exc:
        land_results.append({"ok": False, "error": str(exc)})
```

5. Include `"land_results": land_results` on the turn return dict (alongside `skill_results`). Extend Style D recorded detail (`debug=True` only) with `land_calls={len(land_items)} land_ok={count}` — no new contract lines when `debug=False`.

6. Do **not** change `handle_slack_event` / Events HTTP beyond whatever flows through `run_contact_estelle_turn` already. Do **not** import Gmail/inbox.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish to `origin/sub/AST-1457/AST-1471-meteorite-intake-api-contact-land-path`.
- Do not add files outside Files Changed. Do not edit `tests/` (Betty).
- If `land_meteorite` is missing after sync, stop and comment on **parent AST-1457** — do not reimplement land.
- On ambiguity or drift: stop, comment on parent with Stage blocked template.

## Estimate

Confirm Chuckles estimate: 3 — agree
