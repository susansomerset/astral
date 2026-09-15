# Operative save, hydrate, blob retirement

**Linear:** [AST-1652](https://linear.app/astralcareermatch/issue/AST-1652)
**Parent:** [AST-1641](https://linear.app/astralcareermatch/issue/AST-1641) — Migrate candidate_data.context.priorities to use the artifact table
**Publish ref:** `sub/AST-1641/AST-1652-operative-save-hydrate-blob-retirement`

Wire Priorities through the existing candidate operative `plain_text` path and `get_candidate_current` hydrate on GET; intercept API PUT so Priorities saves call `save_candidate_data(candidate_id, "candidate.context.priorities", body)` (retire+insert, identical no-op already shared); stop durable library-merge SoT writes for `context.priorities`. No backfill helper. No React chrome (sibling Katherine / AST-1653). Depends on catalog sibling [AST-1651](https://linear.app/astralcareermatch/issue/AST-1651) (`candidate.context.priorities` in `ARTIFACT_CONFIG`).

## UAT fitness

- **AC restored:** Parent/child AC4 — Save Priorities via Priorities UI/API; `database.get_current_artifact('candidate', <id>, 'priorities')` returns a row whose `artifact_data` matches the saved string; a second save (changed body) creates a new uuid and retires prior `current=1`. Parent/child AC5 — Successful Priorities save calls operative `save_artifact`; does not rely on library-merge of `context.priorities` alone. Parent/child AC6 — No bulk migrate-all; legacy blob until re-save.
- **Correct outcome:** After save, the current Priorities artifact row is the source of truth; GET/`get_candidate` overlays that string onto `candidate_data.context.priorities` for the editor contract; a changed second save rotates versions; candidates with only a legacy blob still show that blob (or empty) until they re-save.
- **Sibling check:** AST-1651 catalog key + `TOKEN_SOURCES["PRIORITIES"]` artifact typing remain authoritative (config untouched here). Strengths operative path (`context.strengths` pop/hydrate/save) still holds — Priorities is additive, not a rewrite of Strengths. AST-1653 React chrome stays out of this ticket; existing `ContextTextPage` PUT `{ context: { priorities } }` works via the API intercept once wired.
- **Not sufficient:** Removing a stacktrace / 5xx / exception alone is **not** done — durable SoT must be the artifact row.
- **Wrong fix rejected:** Deep-merging `context.priorities` into the library blob (or an in-place `UPDATE` of an existing artifact uuid) fails AC4–AC5. Symptom-only “PUT returns 200” without `get_current_artifact` matching the saved string is wrong.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/core/candidate.py` — operative validation for `plain_text`; hydrate overlay; gate library merge for `context.priorities`.
- `src/ui/api/api_candidate.py` — PUT intercept + GET hydrate for Priorities.

Every Files Changed row and every Stage step stays inside those two files. No `config.py`, no React, no `database.py`, no other context keys, no pin/read-operative Priorities surface, no bulk migrate.

⚠️ **Decision (reuse):** `plain_text` str-path validation and AST-1635 identical-to-current no-op already live in `save_candidate_data` from the Strengths epic. This ticket does **not** re-add those branches — Priorities rides the shared path once the catalog key exists. Scope’s “operative validation for `plain_text`” is satisfied by reuse + Priorities-key logging/hydrate/gate, not a second validator.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | `_PRIORITIES_ARTIFACT_KEY`; entity info on Priorities operative save; `hydrate_operative_priorities_for_response`; call from `get_candidate`; strip `context.priorities` on dict-path library merge (alongside Strengths) | core |
| `src/ui/api/api_candidate.py` | PUT `/data`: pop `context.priorities`, library-merge remainder, then operative save; GET detail hydrate Priorities; api info when Priorities PUT completes | ui |

**Out of this ticket (do not touch):** `src/utils/config.py` (sibling Ada / AST-1651); `CandidatePriorities.tsx` / `ContextTextPage.tsx` (sibling Katherine / AST-1653 — existing PUT `{ context: { priorities } }` keeps working via intercept); `ArtifactEditor`; `database.py`; other context leaves; `tests/` / `docs/test-bible/**`.

**Build precondition:** `ARTIFACT_CONFIG` must contain `candidate.context.priorities` (AST-1651). If missing after `sync-child.sh` (e.g. `origin/ftr/AST-1641` not yet carrying the catalog tip), stop and comment on parent AST-1641 — do not invent the catalog entry here.

## Stage 1: Core — hydrate, library gate, Priorities save log

**Done when:** `save_candidate_data(cid, "candidate.context.priorities", "hello")` inserts a current artifact row whose `artifact_data` is `"hello"`; a second save with a different string returns a new uuid and prior row is not current; identical re-save returns the same uuid (shared AST-1635 gate); `get_candidate` overlays current Priorities onto `candidate_data.context.priorities` when a row exists and leaves the legacy blob alone on miss; dict-path `save_candidate_data(cid, {"context": {"priorities": "x", "deal_breakers": "y"}})` does not persist `priorities` into the library blob (`deal_breakers` still merges); Strengths strip behavior unchanged.

1. In `src/core/candidate.py` module docstring **In-scope** / operative bullets, after the Strengths line, add one line that Priorities uses the same operative save + `get_candidate_current` hydrate path with catalog key `candidate.context.priorities` (cite AST-1652). Do not rewrite base_resume or Strengths bullets.

2. Immediately after `_STRENGTHS_ARTIFACT_KEY` / `hydrate_operative_strengths_for_response`, add:

```python
_PRIORITIES_ARTIFACT_KEY = "candidate.context.priorities"


def hydrate_operative_priorities_for_response(candidate_id: str, cd: dict) -> None:
    """Overlay operative current Priorities into candidate_data.context (display only).

    Miss → leave legacy context.priorities blob untouched (parent AC7 / ticket AC6 migration window).
    Hit → write current string onto context.priorities for the editor contract.
    """
    if not isinstance(cd, dict):
        return
    body = get_candidate_current(candidate_id, _PRIORITIES_ARTIFACT_KEY)
    if body is None:
        return
    if not isinstance(body, str):
        return
    ctx = cd.get("context")
    if not isinstance(ctx, dict):
        ctx = {}
        cd["context"] = ctx
    ctx["priorities"] = body
```

⚠️ **Decision:** On miss, **do not** pop/clear `context.priorities` (same migration-window rule as Strengths hydrate). Parent AC7 / ticket AC6: legacy blob until re-save; no coat-check fetch.

3. In `get_candidate`, immediately after the existing `hydrate_operative_strengths_for_response(candidate_id, cd)` call, add:

```python
    hydrate_operative_priorities_for_response(candidate_id, cd)
```

4. In the **dict-path** of `save_candidate_data`, extend the existing AST-1633 Strengths library gate so **both** catalog-owned leaves are stripped. Replace the Strengths-only filter with:

```python
    # AST-1633 / AST-1652: catalog owns context.strengths + context.priorities — never library-merge those leaves.
    ctx = blob_merge.get("context")
    if isinstance(ctx, dict) and ("strengths" in ctx or "priorities" in ctx):
        cleaned = {
            k: v for k, v in ctx.items() if k not in ("strengths", "priorities")
        }
        if cleaned:
            blob_merge["context"] = cleaned
        else:
            blob_merge.pop("context", None)
```

Do **not** raise when `priorities` is present — strip silently. Other context keys pass through. Do **not** remove the Strengths strip — widen it.

5. In `save_candidate_data` **str-path**, after a successful `database.save_artifact(...)` (the existing assign-then-return), extend the entity info emit so Priorities also logs (`stat.logging.info.entity`). Keep the Strengths branch; add Priorities:

```python
        if artifact_key == _STRENGTHS_ARTIFACT_KEY:
            logger.info(
                "%s | candidate %s: %s (batch: %s)",
                candidate_id,
                "strengths artifact saved",
                new_uuid,
                "-",
            )
        elif artifact_key == _PRIORITIES_ARTIFACT_KEY:
            logger.info(
                "%s | candidate %s: %s (batch: %s)",
                candidate_id,
                "priorities artifact saved",
                new_uuid,
                "-",
            )
        return new_uuid
```

Do **not** emit this info on the identical-body no-op return (above `save_artifact`). Do **not** re-implement `plain_text` validation or the AST-1635 current compare — already present.

**Verify (hand):** with a candidate that has no priorities artifact, hydrate leaves blob alone. After Stage 2, full round-trip.

## Stage 2: API — PUT intercept + GET hydrate + logging

**Done when:** `PUT /api/candidates/<id>/data` with body `{"context": {"priorities": "alpha"}}` creates/rotates a current `priorities` artifact row; library `candidate_data.context.priorities` is not the SoT for that write; `GET /api/candidates/<id>` returns `candidate_data.context.priorities` equal to the current artifact string when a row exists; sibling context keys in the same PUT still library-merge; Strengths PUT path unchanged; no React files changed.

1. In `src/ui/api/api_candidate.py`, in the `from src.core.candidate import (` block, add `hydrate_operative_priorities_for_response`.

2. In `get_candidate_detail`, immediately after the existing `hydrate_operative_strengths_for_response(candidate_id, cd)` call, add:

```python
    hydrate_operative_priorities_for_response(candidate_id, cd)
```

(Idempotent with `get_candidate`'s hydrate — same pattern as Strengths double-call today.)

3. In `update_candidate_data`, next to the Strengths pop (same `if body:` block, before artifacts handling), intercept Priorities the same way:

```python
            priorities_body = None
            ctx = body.get("context")
            if isinstance(ctx, dict) and "priorities" in ctx:
                priorities_body = ctx.pop("priorities")
                if not ctx:
                    body.pop("context", None)
```

Initialize `priorities_saved = False` next to `strengths_saved = False` at the top of the handler. Keep `priorities_body` even when it is `""` so operative validation can raise — do not special-case empty here.

⚠️ **Decision:** If both `strengths` and `priorities` appear in the same PUT `context`, pop each leaf independently (Strengths block already pops `strengths`; this block pops `priorities` from whatever `context` remains). Order: keep Strengths pop first, then Priorities pop (or combine into one pass that pops both) — either is fine as long as both leaves leave `body` before library `save_candidate_data`. Prefer one combined pop for clarity:

```python
            strengths_body = None
            priorities_body = None
            ctx = body.get("context")
            if isinstance(ctx, dict):
                if "strengths" in ctx:
                    strengths_body = ctx.pop("strengths")
                if "priorities" in ctx:
                    priorities_body = ctx.pop("priorities")
                if not ctx:
                    body.pop("context", None)
```

Replace the Strengths-only pop with this combined block — do not leave two sequential pops that race on an empty `context`.

4. After the existing Strengths operative save block (`if strengths_body is not None: ...`), when `priorities_body is not None`, call operative save:

```python
            if priorities_body is not None:
                save_candidate_data(
                    candidate_id,
                    "candidate.context.priorities",
                    priorities_body,
                )
                priorities_saved = True
```

⚠️ **Decision:** Catalog key string literal at the API call site matches the Strengths pattern. Do not import `_PRIORITIES_ARTIFACT_KEY` from candidate (leading-underscore private).

5. On the success path of `update_candidate_data`, extend the existing Strengths api info so Priorities also emits when saved (`stat.logging.info.api`). Replace the Strengths-only gate with:

```python
    if strengths_saved or priorities_saved:
        logger.info(
            "%s | api %s completed: PUT %s",
            candidate_id,
            f"/api/candidates/{candidate_id}/data",
            200,
        )
```

One info line when either (or both) leaf saves completed — do not emit two identical lines. Do **not** emit for GETs or for PUTs that touched neither leaf.

6. Do **not** edit the existing `except Exception as e:` `logger.exception(...)` — AST-1633/Joan already land the correct `stat.logging.error` format (`type(e).__name__`, `e`, next-step). Touching Priorities in this handler does not require a second exception log.

7. Do **not** edit React. Existing `ContextTextPage` PUT `{ context: { priorities: draft } }` lands operative rows via this intercept; GET hydrate feeds the same `candidate_data.context.priorities` leaf the page already reads (AST-1653 only retargets chrome if needed).

**Verify (hand):**

```bash
# After save via PUT (use a real candidate_id):
python3 -c "
from src.data import database
row = database.get_current_artifact('candidate', '<id>', 'priorities')
assert row and row['artifact_data'] == '<saved string>'
"
# Second save with a *different* string → new artifact_uuid; prior current=0
# Identical re-save → same uuid (AST-1635 shared gate)
```

## Execution contract

- Execute steps in order within a stage; stages in order; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files, touch Ada/Katherine scopes, register other context keys, or add a backfill/migrate script.
- On ambiguity or drift — stop, comment on parent AST-1641 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `patt.artifact.write-operative` | pattern — read in full; Priorities via `save_candidate_data` str-path → `save_artifact` (shared plain_text + identical no-op) |
| `patt.artifact.read-current` | pattern — read in full; hydrate via `get_candidate_current` |
| `patt.artifact.manage-catalog` | pattern — read in full; retire blob authority for registered Priorities key only |
| `astral.standards.in-scope-only` | statute — Priorities only; two named files |
| `stat.logging.info.entity` | statute — entity info on Priorities operative save |
| `stat.logging.info.api` | statute — api info when Priorities (or Strengths) PUT completes |
| `stat.logging.error` | statute — exception once at PUT handler (already present; do not duplicate) |

## Traceability

- Parent/child AC4 (operative round-trip) → Stage 1 §§2–5 + Stage 2 §§3–4 + verify
- Parent/child AC5 (blob not SoT on write) → Stage 1 §4 + Stage 2 §§3–4
- Parent/child AC6 / parent AC7 (no backfill; legacy until re-save) → Stage 1 §2 miss path
- Parent AC8 (sibling freeze) → scope gate; no other `ARTIFACT_CONFIG` keys
- Editor reload (parent AC6) → Stage 1 §§2–3 + Stage 2 §2 (Katherine UI unchanged this ticket)
