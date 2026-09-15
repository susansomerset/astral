# Operative save, hydrate, blob retirement

**Linear:** [AST-1659](https://linear.app/astralcareermatch/issue/AST-1659)
**Parent:** [AST-1643](https://linear.app/astralcareermatch/issue/AST-1643) — Migrate candidate_data.context.ideal_day to use the artifact table
**Publish ref:** `sub/AST-1643/AST-1659-operative-save-hydrate-blob-retirement`

Wire Ideal Day through the same candidate operative `plain_text` validation + hydrate-on-GET and API PUT intercept Strengths / bio summary already use; stop durable library SoT writes for `context.ideal_day`. No backfill helper. No React chrome or catalog/token (siblings Ada / Katherine). Depends on catalog sibling [AST-1658](https://linear.app/astralcareermatch/issue/AST-1658) — `candidate.context.ideal_day` must be in `ARTIFACT_CONFIG` before Stage 1 verify (sibling tip: `origin/sub/AST-1643/AST-1658-catalog-plain-text-ideal-day-token`; `origin/ftr/AST-1643` not published yet at plan time).

## UAT fitness

- **AC restored:** Parent AC4 — Save Ideal Day via Ideal Day UI/API; `database.get_current_artifact('candidate', <id>, 'ideal_day')` returns a row whose `artifact_data` matches the saved string; a second save creates a new uuid and retires prior `current=1`. Parent AC5 — Successful Ideal Day save calls operative `save_artifact`; does not rely on library-merge of `context.ideal_day` alone. Parent AC6 (ticket AC6 / parent “No backfill required”) — No bulk migrate-all; legacy blob until re-save.
- **Correct outcome:** After Ideal Day save, the editor contract leaf `candidate_data.context.ideal_day` reflects the current artifact string on GET; the durable SoT is the artifacts row (retire+insert on change), not the library blob.
- **Sibling check:** Catalog + `IDEAL_DAY` token typing stay on AST-1658 (config only). React / ContextTextPage wire-up stays on AST-1660. Strengths / bio_summary operative paths remain unchanged except Ideal Day is added to the shared `_CONTEXT_OPERATIVE_LEAVES` strip set. Sibling freeze (priorities / deal_breakers / backstory / writing_preferences) stays unregistered — this ticket does not touch `ARTIFACT_CONFIG`.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Library-merge-only PUT for Ideal Day (AC5 fail); inventing a second Ideal-Day-only validate path instead of riding existing `plain_text` + AST-1635 identical no-op; clearing legacy blob on hydrate miss (breaks no-backfill window); registering Ideal Day in config here (Ada’s ticket).

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/core/candidate.py` — operative validation for `plain_text`; hydrate overlay; gate library merge for `context.ideal_day`.
- `src/ui/api/api_candidate.py` — PUT intercept plus GET hydrate for Ideal Day.

Every Files Changed row and every Stage step stays inside those two files. No `config.py`, no React, no `database.py`, no other context keys, no pin/read-operative Ideal Day surface, no bulk migrate.

**Already on tip (do not re-invent):**

- `plain_text` body validation in `save_candidate_data` str-path (AST-1633).
- Identical-to-current no-op before `save_artifact` (AST-1635) — applies to all catalog str-path keys including Ideal Day once called.
- Strengths + bio_summary library gate / hydrate / PUT intercept / entity+api info / PUT `logger.exception` with type+message (AST-1633 / AST-1649 + Joan fix).

This ticket **extends** those paths for `ideal_day` / `candidate.context.ideal_day` only.

**Catalog prerequisite:** Before Stage 1 hand-verify, `from src.utils.config import ARTIFACT_CONFIG; assert "candidate.context.ideal_day" in ARTIFACT_CONFIG` must exit 0. If missing at **build-child** start — stop, comment on parent AST-1643 with Stage blocked (catalog sibling not on tip); do **not** register the key in this ticket.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Module constant + docstring; extend `_CONTEXT_OPERATIVE_LEAVES` with `ideal_day`; `hydrate_operative_ideal_day_for_response` + call from `get_candidate`; entity info on Ideal Day operative save | core |
| `src/ui/api/api_candidate.py` | PUT `/data`: pop `context.ideal_day`, library-merge remainder, then operative save; GET detail hydrate Ideal Day; api info when Ideal Day PUT completes | ui |

**Out of this ticket (do not touch):** `src/utils/config.py` (sibling Ada / AST-1658); `CandidateIdealDay.tsx` / `ContextTextPage.tsx` (sibling Katherine — existing PUT `{ context: { ideal_day } }` keeps working via intercept once page lands); `ArtifactEditor`; `database.py`; other context leaves; `tests/` / `docs/test-bible/**`.

## Stage 1: Core — library gate, hydrate, entity log

**Done when:** `save_candidate_data(cid, "candidate.context.ideal_day", "hello")` inserts a current artifact row whose `artifact_data` is `"hello"` (existing `plain_text` validate + AST-1635 identical no-op unchanged); a second save with a different string returns a new uuid and prior row is not current; identical re-save returns the same uuid with no new row; `get_candidate` overlays current Ideal Day onto `candidate_data.context.ideal_day` when a row exists and leaves the legacy blob alone on miss; dict-path `save_candidate_data(cid, {"context": {"ideal_day": "x", "priorities": "y"}})` does not persist `ideal_day` into the library blob (priorities still merge; `strengths` / `bio_summary` still stripped as today).

1. In `src/core/candidate.py` module docstring **In-scope** / operative bullets, add one line that Ideal Day uses the same operative save + `get_candidate_current` hydrate path with catalog key `candidate.context.ideal_day` (cite AST-1659). Keep the existing Strengths / bio summary / base_resume lines.

2. Immediately after `_BIO_SUMMARY_ARTIFACT_KEY = "candidate.context.bio_summary"`, add:

```python
_IDEAL_DAY_ARTIFACT_KEY = "candidate.context.ideal_day"
```

Widen the existing closed frozenset (do **not** invent a second strip site):

```python
# Catalog-owned context leaves — never durable library-merge SoT (AST-1633 / AST-1649 / AST-1659).
_CONTEXT_OPERATIVE_LEAVES = frozenset({"strengths", "bio_summary", "ideal_day"})
```

⚠️ **Decision:** Same frozenset pattern as AST-1649 — one strip site for all operative context leaves. Do not hardcode `ideal_day` in a second independent `if`.

3. **Do not** change the existing `plain_text` validation branch or the AST-1635 identical-to-current gate. Ideal Day rides those paths via catalog `body_shape: "plain_text"`.

4. In the str-path, after a successful `database.save_artifact(...)` (assign-then-return already present), extend the entity info emission so Ideal Day also logs (`stat.logging.info.entity`). Keep Strengths / bio_summary behavior:

```python
        elif artifact_key == _IDEAL_DAY_ARTIFACT_KEY:
            logger.info(
                "%s | candidate %s: %s (batch: %s)",
                candidate_id,
                "ideal_day artifact saved",
                new_uuid,
                "-",
            )
```

Place this as a third branch after the existing `_BIO_SUMMARY_ARTIFACT_KEY` `elif` (same `if` / `elif` chain). Do **not** emit entity info on the identical-body no-op return. Do **not** add entity info for `base_resume` or other keys.

5. **Do not** rewrite the dict-path strip block — widening `_CONTEXT_OPERATIVE_LEAVES` in step 2 is sufficient. Confirm the existing loop still uses `k not in _CONTEXT_OPERATIVE_LEAVES`.

6. Add `hydrate_operative_ideal_day_for_response(candidate_id: str, cd: dict) -> None` immediately after `hydrate_operative_bio_summary_for_response`:

```python
def hydrate_operative_ideal_day_for_response(candidate_id: str, cd: dict) -> None:
    """Overlay operative current Ideal Day into candidate_data.context (display only).

    Miss → leave legacy context.ideal_day blob untouched (parent AC6 / ticket AC6 migration window).
    Hit → write current string onto context.ideal_day for the editor contract.
    """
    if not isinstance(cd, dict):
        return
    body = get_candidate_current(candidate_id, _IDEAL_DAY_ARTIFACT_KEY)
    if body is None:
        return
    if not isinstance(body, str):
        return
    ctx = cd.get("context")
    if not isinstance(ctx, dict):
        ctx = {}
        cd["context"] = ctx
    ctx["ideal_day"] = body
```

⚠️ **Decision:** On miss, **do not** pop/clear `context.ideal_day` (same migration-window choice as Strengths / bio summary; unlike base_resume hydrate, which strips blob on miss). Parent AC6 / ticket AC6: legacy blob until re-save; no coat-check.

7. In `get_candidate`, immediately after the existing `hydrate_operative_bio_summary_for_response(candidate_id, cd)` call, add:

```python
    hydrate_operative_ideal_day_for_response(candidate_id, cd)
```

**Verify (hand):** with a candidate that has no ideal_day artifact, hydrate leaves legacy blob alone. After Stage 2, full round-trip.

## Stage 2: API — PUT intercept + GET hydrate + logging

**Done when:** `PUT /api/candidates/<id>/data` with body `{"context": {"ideal_day": "alpha"}}` creates/rotates a current `ideal_day` artifact row; library `candidate_data.context.ideal_day` is not the SoT for that write; `GET /api/candidates/<id>` returns `candidate_data.context.ideal_day` equal to the current artifact string when a row exists; sibling context keys (e.g. `priorities`) in the same PUT still library-merge; Strengths / bio_summary PUT paths unchanged; no React files changed.

1. In `src/ui/api/api_candidate.py`, in the `from src.core.candidate import (` block, add `hydrate_operative_ideal_day_for_response` next to the existing Strengths / bio_summary hydrate imports. Logger / `get_logger` already present — do not re-add.

2. In `get_candidate_detail`, immediately after the existing `hydrate_operative_bio_summary_for_response(candidate_id, cd)` call, add:

```python
    hydrate_operative_ideal_day_for_response(candidate_id, cd)
```

(Idempotent with `get_candidate`'s hydrate — same double-call pattern as Strengths / bio summary / base_resume.)

3. In `update_candidate_data`, extend the context pop at the start of `if body:` to also pop Ideal Day. Initialize `ideal_day_saved = False` next to the existing `strengths_saved` / `bio_summary_saved` (outside the try, same scope).

```python
            strengths_body = None
            bio_summary_body = None
            ideal_day_body = None
            ctx = body.get("context")
            if isinstance(ctx, dict) and "strengths" in ctx:
                strengths_body = ctx.pop("strengths")
            if isinstance(ctx, dict) and "bio_summary" in ctx:
                bio_summary_body = ctx.pop("bio_summary")
            if isinstance(ctx, dict) and "ideal_day" in ctx:
                ideal_day_body = ctx.pop("ideal_day")
            if isinstance(ctx, dict) and not ctx:
                body.pop("context", None)
```

Keep `ideal_day_body` even when it is `""` so operative validation can raise — do not special-case empty here.

⚠️ **Decision:** One empty-`context` cleanup after all pops. Same `ctx` reference; Strengths / bio_summary order preserved for minimal diff vs AST-1649.

4. After the existing bio-summary operative-save block (`if bio_summary_body is not None: ...`), add the Ideal Day twin:

```python
            if ideal_day_body is not None:
                save_candidate_data(
                    candidate_id,
                    "candidate.context.ideal_day",
                    ideal_day_body,
                )
                ideal_day_saved = True
```

Place this so it still runs when the PUT is Ideal-Day-only (body emptied after pop) — same “leaf-only PUT leaves body empty” pattern already in the handler.

⚠️ **Decision:** Catalog key string literal at the API call site matches Strengths / bio summary (`"candidate.context.ideal_day"`). Do not import `_IDEAL_DAY_ARTIFACT_KEY` from candidate (leading-underscore private).

5. On the success path of `update_candidate_data` (after the try succeeds, near the existing `if bio_summary_saved:` api info), if `ideal_day_saved`, emit one api info line (`stat.logging.info.api`):

```python
    if ideal_day_saved:
        logger.info(
            "%s | api %s completed: PUT %s",
            candidate_id,
            f"/api/candidates/{candidate_id}/data",
            200,
        )
```

Keep the existing `if strengths_saved:` / `if bio_summary_saved:` blocks unchanged. A PUT that saves multiple operative leaves may emit multiple api info lines — acceptable (one progress line per leaf that completed).

6. **Do not** rewrite the existing `except Exception as e:` `logger.exception(...)` block — it already includes `type(e).__name__`, `e`, and “returning 400” (`stat.logging.error`). Ideal Day ValueErrors ride the same handler.

7. Do **not** edit React. When Katherine’s Ideal Day page lands, `ContextTextPage` PUT `{ context: { ideal_day: draft } }` lands operative rows via this intercept; GET hydrate feeds `candidate_data.context.ideal_day`.

**Verify (hand):**

```bash
# After save via PUT (use a real candidate_id):
python3 -c "
from src.data import database
row = database.get_current_artifact('candidate', '<id>', 'ideal_day')
assert row and row['artifact_data'] == '<saved string>'
"
# Second distinct save → new artifact_uuid; prior current=0
# Identical re-save → same uuid (AST-1635 no-op)
```

## Execution contract

- Execute steps in order within a stage; stages in order; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files, touch Ada/Katherine scopes, register other context keys, or add a backfill/migrate script.
- On ambiguity or drift — stop, comment on parent AST-1643 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `patt.artifact.write-operative` | pattern — read in full; Ideal Day via `save_candidate_data` str-path → `save_artifact` (identical no-op already shared) |
| `patt.artifact.read-current` | pattern — read in full; hydrate via `get_candidate_current` |
| `patt.artifact.manage-catalog` | pattern — read in full; retire blob authority for registered Ideal Day key only (catalog entry from AST-1658) |
| `astral.standards.in-scope-only` | statute — Ideal Day only; two named files |
| `stat.logging.info.entity` | statute — entity info on Ideal Day operative save |
| `stat.logging.info.api` | statute — api info when Ideal Day PUT completes |
| `stat.logging.error` | statute — exception once at PUT handler (already present; do not regress) |

## Traceability

- Parent/child AC4 (operative round-trip) → Stage 1 §§4–6 + Stage 2 §§3–4 + verify
- Parent/child AC5 (blob not SoT on write) → Stage 1 §5 + Stage 2 §§3–4
- Parent/child AC6 / parent AC6–7 (no backfill; legacy until re-save) → Stage 1 §6 miss path
- Sibling freeze (parent AC8) → scope gate; no other `ARTIFACT_CONFIG` keys
- Editor reload (parent AC6, Katherine AST-1660) → Stage 1 §§6–7 + Stage 2 §2 (UI sibling unchanged)
