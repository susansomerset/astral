# Operative save, hydrate, blob retirement

**Linear:** [AST-1633](https://linear.app/astralcareermatch/issue/AST-1633)
**Parent:** [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629) — Migrate candidate_data.context.strengths to use the artifact table
**Publish ref:** `sub/AST-1629/AST-1633-operative-save-hydrate-blob-retirement`

Wire Strengths through candidate operative `plain_text` validation and `get_candidate_current` hydrate on GET; intercept API PUT so Strengths saves call `save_candidate_data(candidate_id, "candidate.context.strengths", body)` (retire+insert); stop durable library-merge SoT writes for `context.strengths`. No backfill helper. No React chrome (sibling Katherine). Depends on catalog sibling [AST-1632](https://linear.app/astralcareermatch/issue/AST-1632) (already on `origin/ftr`).

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/core/candidate.py` — operative validation for `plain_text`; hydrate overlay; gate library merge for `context.strengths`.
- `src/ui/api/api_candidate.py` — PUT intercept + GET hydrate for Strengths.

Every Files Changed row and every Stage step stays inside those two files. No `config.py`, no React, no `database.py`, no other context keys, no pin/read-operative Strengths surface, no bulk migrate.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | `plain_text` body validation on str-path save; `hydrate_operative_strengths_for_response`; call it from `get_candidate`; strip `context.strengths` on dict-path library merge; entity info log on Strengths operative save | core |
| `src/ui/api/api_candidate.py` | PUT `/data`: pop `context.strengths`, library-merge remainder, then operative save; GET detail hydrate Strengths; api info + exception logging on touched PUT path | ui |

**Out of this ticket (do not touch):** `src/utils/config.py` (sibling Ada); `CandidateStrengths.tsx` / `ContextTextPage.tsx` (sibling Katherine — existing PUT `{ context: { strengths } }` keeps working via intercept); `ArtifactEditor`; `database.py`; other context leaves; `tests/` / `docs/test-bible/**`.

## Stage 1: Core — plain_text validate, hydrate, library gate

**Done when:** `save_candidate_data(cid, "candidate.context.strengths", "hello")` inserts a current artifact row whose `artifact_data` is `"hello"`; a second save with a different string returns a new uuid and prior row is not current; `get_candidate` overlays current Strengths onto `candidate_data.context.strengths` when a row exists and leaves the legacy blob alone on miss; dict-path `save_candidate_data(cid, {"context": {"strengths": "x", "priorities": "y"}})` does not persist `strengths` into the library blob (priorities still merge).

1. In `src/core/candidate.py` module docstring **In-scope** / operative bullets, add one line that Strengths uses the same operative save + `get_candidate_current` hydrate path with catalog key `candidate.context.strengths` (cite AST-1633). Do not rewrite the base_resume bullets.

2. Near the existing `_PILOT_BASE_RESUME_ARTIFACT_KEY` constant (or immediately above the new hydrate helper if that constant is far from Stage work), add:

```python
_STRENGTHS_ARTIFACT_KEY = "candidate.context.strengths"
```

⚠️ **Decision:** Module constant matches the base_resume pilot style — single closed catalog string, no hardcoding the leaf in multiple places beyond `rsplit` inside existing helpers.

3. In `save_candidate_data` **str-path** (the `isinstance(data_or_artifact_key, str)` branch), after the existing `resume_content` validation block and **before** `artifact_type = artifact_key.rsplit(...)`, add a `plain_text` branch:

```python
        elif entry["body_shape"] == "plain_text":
            # AST-1633: raw string body (BUILD_CONFIG sentinel "raw_string" — validate type here).
            if not isinstance(blob, str) or not blob.strip():
                raise ValueError("plain_text body must be a non-empty string")
```

Do **not** iterate `shape.items()` — sibling catalog set `BUILD_CONFIG["artifact_shapes"]["plain_text"] = "raw_string"` (string sentinel, not a field map). Leave the existing `resume_content` branch unchanged. Other shapes continue to fall through to `database.save_artifact` as today.

⚠️ **Decision:** Non-empty after strip. Empty textarea save fails closed with ValueError (UI toast) — no silent skip and no library fallback write. Clearing Strengths without a dedicated clear API is out of scope.

4. Still in the str-path, after a successful `database.save_artifact(...)` return value is known, when `artifact_key == _STRENGTHS_ARTIFACT_KEY`, emit one entity info line (`stat.logging.info.entity`) then return the uuid:

```python
        new_uuid = database.save_artifact(
            entry["entity_type"], candidate_id, artifact_type, blob
        )
        if artifact_key == _STRENGTHS_ARTIFACT_KEY:
            logger.info(
                "%s | candidate %s: %s (batch: %s)",
                candidate_id,
                "strengths artifact saved",
                new_uuid,
                "-",
            )
        return new_uuid
```

Refactor the existing bare `return database.save_artifact(...)` into assign-then-return so the Strengths log can run without duplicating the save call. Do **not** add entity info for `base_resume` or other keys on this ticket.

5. In the **dict-path** of `save_candidate_data`, after contact uniqueness / before `steps = []` (or immediately before `save_kwargs` is built — wherever `blob_merge` is finalized), gate durable library SoT for Strengths:

```python
    # AST-1633: catalog owns context.strengths — never library-merge that leaf.
    ctx = blob_merge.get("context")
    if isinstance(ctx, dict) and "strengths" in ctx:
        cleaned = {k: v for k, v in ctx.items() if k != "strengths"}
        if cleaned:
            blob_merge["context"] = cleaned
        else:
            blob_merge.pop("context", None)
```

Do **not** raise when `strengths` is present — strip silently (same spirit as API pop + company_search_terms del). Other context keys pass through.

6. Add `hydrate_operative_strengths_for_response(candidate_id: str, cd: dict) -> None` next to `hydrate_operative_base_resume_for_response`:

```python
def hydrate_operative_strengths_for_response(candidate_id: str, cd: dict) -> None:
    """Overlay operative current Strengths into candidate_data.context (display only).

    Miss → leave legacy context.strengths blob untouched (parent AC7 migration window).
    Hit → write current string onto context.strengths for the editor contract.
    """
    if not isinstance(cd, dict):
        return
    body = get_candidate_current(candidate_id, _STRENGTHS_ARTIFACT_KEY)
    if body is None:
        return
    if not isinstance(body, str):
        return
    ctx = cd.get("context")
    if not isinstance(ctx, dict):
        ctx = {}
        cd["context"] = ctx
    ctx["strengths"] = body
```

⚠️ **Decision:** On miss, **do not** pop/clear `context.strengths` (unlike base_resume hydrate, which strips blob on miss). Parent AC7 / ticket AC6: legacy blob until re-save; no coat-check fetch — just leave whatever is already in `cd`.

7. In `get_candidate`, immediately after the existing `hydrate_operative_base_resume_for_response(candidate_id, cd)` call, add:

```python
    hydrate_operative_strengths_for_response(candidate_id, cd)
```

**Verify (hand):** with a candidate that has no strengths artifact, PUT is not required yet — call hydrate mentally: blob left alone. After Stage 2, full round-trip.

## Stage 2: API — PUT intercept + GET hydrate + logging

**Done when:** `PUT /api/candidates/<id>/data` with body `{"context": {"strengths": "alpha"}}` creates/rotates a current `strengths` artifact row; library `candidate_data.context.strengths` is not the SoT for that write; `GET /api/candidates/<id>` returns `candidate_data.context.strengths` equal to the current artifact string when a row exists; sibling context keys in the same PUT still library-merge; no React files changed.

1. In `src/ui/api/api_candidate.py`, add imports:

```python
from src.utils.logging import get_logger
```

and, in the `from src.core.candidate import (` block, add `hydrate_operative_strengths_for_response`. Then:

```python
logger = get_logger(__name__)
```

near the other module-level setup (after imports).

2. In `get_candidate_detail`, immediately after the existing `hydrate_operative_base_resume_for_response(candidate_id, cd)` call, add:

```python
    hydrate_operative_strengths_for_response(candidate_id, cd)
```

(Idempotent with `get_candidate`'s hydrate — same pattern as base_resume double-call today.)

3. In `update_candidate_data`, **before** the `if body:` / artifacts handling (or at the start of the `if body:` block, before library `save_candidate_data`), intercept Strengths the same way base_resume is popped from artifacts:

```python
        strengths_body = None
        strengths_saved = False
        ctx = body.get("context")
        if isinstance(ctx, dict) and "strengths" in ctx:
            strengths_body = ctx.pop("strengths")
            if not ctx:
                body.pop("context", None)
```

Keep `strengths_body` even when it is `""` so operative validation (Stage 1) can raise — do not special-case empty here.

4. After the existing library `save_candidate_data(candidate_id, body, replace=False, debug=ui_llm_debug())` (and after the base_resume operative save block), when `strengths_body is not None`, call operative save:

```python
                if strengths_body is not None:
                    save_candidate_data(
                        candidate_id,
                        "candidate.context.strengths",
                        strengths_body,
                    )
                    strengths_saved = True
```

⚠️ **Decision:** Catalog key string literal at the API call site matches the base_resume pattern (`TASK_CONFIG[...]["artifact_key"]` for pilot; Strengths has no craft task — use the closed catalog key `"candidate.context.strengths"` directly). Do not import `_STRENGTHS_ARTIFACT_KEY` from candidate (leading-underscore private).

5. On the success path of `update_candidate_data` (after the try succeeds, before or when returning the updated candidate JSON), if `strengths_saved`, emit one api info line (`stat.logging.info.api`):

```python
        if strengths_saved:
            logger.info(
                "%s | api %s completed: PUT %s",
                candidate_id,
                f"/api/candidates/{candidate_id}/data",
                200,
            )
```

Place this where the handler is about to return 200 with the updated candidate (same function, after successful persist). Do **not** emit this info for GETs or for PUTs that did not touch Strengths.

6. In the existing `except Exception as e:` of `update_candidate_data`, **before** the pending-rubric re-stash / `return jsonify(...)`, add (`stat.logging.error`):

```python
        logger.exception(
            "%s | api update_candidate_data failed — returning 400",
            candidate_id,
        )
```

One exception log at the handler; do not log-and-re-raise; data/core continue to raise without logging.

7. Do **not** edit React. Existing `ContextTextPage` PUT `{ context: { strengths: draft } }` lands operative rows via this intercept; GET hydrate feeds the same `candidate_data.context.strengths` leaf the page already reads.

**Verify (hand):**

```bash
# After save via PUT (use a real candidate_id):
python3 -c "
from src.data import database
row = database.get_current_artifact('candidate', '<id>', 'strengths')
assert row and row['artifact_data'] == '<saved string>'
"
# Second save → new artifact_uuid; prior current=0
```

## Execution contract

- Execute steps in order within a stage; stages in order; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files, touch Ada/Katherine scopes, register other context keys, or add a backfill/migrate script.
- On ambiguity or drift — stop, comment on parent AST-1629 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 5 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `patt.artifact.write-operative` | pattern — read in full; Strengths via `save_candidate_data` str-path → `save_artifact` |
| `patt.artifact.read-current` | pattern — read in full; hydrate via `get_candidate_current` |
| `patt.artifact.manage-catalog` | pattern — read in full; retire blob authority for registered Strengths key only |
| `astral.standards.in-scope-only` | statute — Strengths only; two named files |
| `stat.logging.info.entity` | statute — entity info on Strengths operative save |
| `stat.logging.info.api` | statute — api info when Strengths PUT completes |
| `stat.logging.error` | statute — exception once at PUT handler |

## Traceability

- Parent/child AC4 (operative round-trip) → Stage 1 §§3–4 + Stage 2 §§3–4 + verify
- Parent/child AC5 (blob not SoT on write) → Stage 1 §5 + Stage 2 §§3–4
- Parent/child AC6 / parent AC7 (no backfill; legacy until re-save) → Stage 1 §6 miss path
- Parent/child AC7 / parent AC8 (sibling freeze) → scope gate; no other `ARTIFACT_CONFIG` keys
- Editor reload (parent AC6) → Stage 1 §6–7 + Stage 2 §2 (Katherine UI unchanged)
