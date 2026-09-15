# Operative save, hydrate, blob retirement

**Linear:** [AST-1655](https://linear.app/astralcareermatch/issue/AST-1655)
**Parent:** [AST-1642](https://linear.app/astralcareermatch/issue/AST-1642) — Migrate candidate_data.context.deal_breakers to use the artifact table
**Publish ref:** `sub/AST-1642/AST-1655-operative-save-hydrate-blob-retirement`

Wire Deal Breakers through the existing candidate operative `plain_text` validation and `get_candidate_current` hydrate on GET; intercept API PUT so Deal Breakers saves call `save_candidate_data(candidate_id, "candidate.context.deal_breakers", body)` (retire+insert, with AST-1635 identical-body no-op already on the shared str-path); stop durable library-merge SoT writes for `context.deal_breakers`. No backfill helper. No React chrome (sibling Katherine). Depends on catalog sibling [AST-1654](https://linear.app/astralcareermatch/issue/AST-1654) (on `origin/ftr/AST-1642-migrate-deal-breakers-artifact-table`). Mirror [AST-1633](https://linear.app/astralcareermatch/issue/AST-1633) guidelines — do not rederive `plain_text` validation.

## UAT fitness

- **AC restored:** Parent AC4 — "Operative round-trip — Save Deal Breakers via Deal Breakers UI/API; `database.get_current_artifact('candidate', <id>, 'deal_breakers')` returns a row whose `artifact_data` matches the saved string; a second save creates a new uuid and retires prior `current=1`." Parent AC5 — "Blob not SoT on write — Successful Deal Breakers save calls operative `save_artifact`; does not rely on library-merge of `context.deal_breakers` alone." Parent AC6 — "No backfill required — Candidates with only legacy blob Deal Breakers and no artifact row still load that blob (or empty) until re-save; no bulk migration job ships."
- **Correct outcome:** After PUT with Deal Breakers text, a current `deal_breakers` artifact row holds that string; GET/`get_candidate` overlays it onto `candidate_data.context.deal_breakers` for the editor contract; a second save with different text rotates current; legacy blob-only candidates still show blob text until first operative save.
- **Sibling check:** AST-1654 catalog + `DEAL_BREAKERS` token already on parent ftr (`candidate.context.deal_breakers` / `plain_text` / artifact-typed token) — verified on sync tip. AST-1656 owns React `CandidateDealBreakers.tsx` only — existing PUT `{ context: { deal_breakers } }` keeps working via this ticket's intercept without UI changes. Strengths operative path (AST-1633) stays intact.
- **Not sufficient:** Removing a stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Library-merge-only write of `context.deal_breakers` (or clearing the leaf without an artifact row) fails AC4/AC5. Re-implementing `plain_text` validation or touching `config.py` / React / `database.py` invents sibling scope. Coat-check or bulk backfill violates parent AC6 / non-goals.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/core/candidate.py` — operative validation for `plain_text`; hydrate overlay; gate library merge for `context.deal_breakers`.
- `src/ui/api/api_candidate.py` — PUT intercept plus GET hydrate for Deal Breakers.

Every Files Changed row and every Stage step stays inside those two files. No `config.py`, no React, no `database.py`, no other context keys, no pin/read-operative Deal Breakers surface, no bulk migrate.

**Reuse (do not re-add):** AST-1633 already shipped the shared `plain_text` str-path validation and AST-1635 identical-to-current no-op on `save_candidate_data` str-path. This ticket wires Deal Breakers onto that path — do not duplicate the `elif entry["body_shape"] == "plain_text"` block.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Module docstring + `_DEAL_BREAKERS_ARTIFACT_KEY`; entity info on Deal Breakers operative save; strip `context.deal_breakers` on dict-path library merge; `hydrate_operative_deal_breakers_for_response`; call from `get_candidate` | core |
| `src/ui/api/api_candidate.py` | Import hydrate; PUT `/data`: pop `context.deal_breakers`, library-merge remainder, then operative save; GET detail hydrate Deal Breakers; api info when Deal Breakers PUT completes | ui |

**Out of this ticket (do not touch):** `src/utils/config.py` (sibling Ada AST-1654); `CandidateDealBreakers.tsx` / `ContextTextPage.tsx` (sibling Katherine AST-1656 — existing PUT `{ context: { deal_breakers } }` keeps working via intercept); `ArtifactEditor`; `database.py`; other context leaves; `tests/` / `docs/test-bible/**`; Strengths operative wiring (leave as-is).

## Stage 1: Core — Deal Breakers hydrate, library gate, entity log

**Done when:** `save_candidate_data(cid, "candidate.context.deal_breakers", "hello")` inserts a current artifact row whose `artifact_data` is `"hello"` (reuses existing `plain_text` validate + AST-1635 no-op); a second save with a different string returns a new uuid and prior row is not current; identical re-save returns the same uuid without retire; `get_candidate` overlays current Deal Breakers onto `candidate_data.context.deal_breakers` when a row exists and leaves the legacy blob alone on miss; dict-path `save_candidate_data(cid, {"context": {"deal_breakers": "x", "priorities": "y"}})` does not persist `deal_breakers` into the library blob (priorities still merge; strengths strip from AST-1633 still works).

1. In `src/core/candidate.py` module docstring **In-scope** / operative bullets, after the Strengths line, add one line that Deal Breakers uses the same operative save + `get_candidate_current` hydrate path with catalog key `candidate.context.deal_breakers` (cite AST-1655). Do not rewrite base_resume or Strengths bullets.

2. Immediately below `_STRENGTHS_ARTIFACT_KEY`, add:

```python
_DEAL_BREAKERS_ARTIFACT_KEY = "candidate.context.deal_breakers"
```

⚠️ **Decision:** Module constant matches Strengths / base_resume pilot style — single closed catalog string.

3. Do **not** add or edit the `plain_text` validation branch — it already exists (AST-1633). Empty / non-str bodies still raise `ValueError("plain_text body must be a non-empty string")` for Deal Breakers via that shared branch.

4. In the str-path, after a successful `database.save_artifact(...)` (the existing assign-then-return), extend the Strengths-only entity info so Deal Breakers also logs (`stat.logging.info.entity`):

```python
        if artifact_key == _STRENGTHS_ARTIFACT_KEY:
            logger.info(
                "%s | candidate %s: %s (batch: %s)",
                candidate_id,
                "strengths artifact saved",
                new_uuid,
                "-",
            )
        elif artifact_key == _DEAL_BREAKERS_ARTIFACT_KEY:
            logger.info(
                "%s | candidate %s: %s (batch: %s)",
                candidate_id,
                "deal_breakers artifact saved",
                new_uuid,
                "-",
            )
```

Do **not** emit entity info on the AST-1635 identical-body no-op return path (same rule as Strengths). Do **not** add entity info for `base_resume` or other keys on this ticket.

5. In the **dict-path** of `save_candidate_data`, immediately after the existing AST-1633 Strengths library gate block, gate durable library SoT for Deal Breakers:

```python
    # AST-1655: catalog owns context.deal_breakers — never library-merge that leaf.
    ctx = blob_merge.get("context")
    if isinstance(ctx, dict) and "deal_breakers" in ctx:
        cleaned = {k: v for k, v in ctx.items() if k != "deal_breakers"}
        if cleaned:
            blob_merge["context"] = cleaned
        else:
            blob_merge.pop("context", None)
```

Do **not** raise when `deal_breakers` is present — strip silently. Leave the Strengths strip block untouched (run both; order Strengths then Deal Breakers). Other context keys pass through.

6. Add `hydrate_operative_deal_breakers_for_response(candidate_id: str, cd: dict) -> None` immediately after `hydrate_operative_strengths_for_response`:

```python
def hydrate_operative_deal_breakers_for_response(candidate_id: str, cd: dict) -> None:
    """Overlay operative current Deal Breakers into candidate_data.context (display only).

    Miss → leave legacy context.deal_breakers blob untouched (parent AC6 migration window).
    Hit → write current string onto context.deal_breakers for the editor contract.
    """
    if not isinstance(cd, dict):
        return
    body = get_candidate_current(candidate_id, _DEAL_BREAKERS_ARTIFACT_KEY)
    if body is None:
        return
    if not isinstance(body, str):
        return
    ctx = cd.get("context")
    if not isinstance(ctx, dict):
        ctx = {}
        cd["context"] = ctx
    ctx["deal_breakers"] = body
```

⚠️ **Decision:** On miss, **do not** pop/clear `context.deal_breakers` (same as Strengths hydrate; unlike base_resume). Parent AC6: legacy blob until re-save; no coat-check fetch.

7. In `get_candidate`, immediately after `hydrate_operative_strengths_for_response(candidate_id, cd)`, add:

```python
    hydrate_operative_deal_breakers_for_response(candidate_id, cd)
```

**Verify (hand):** with a candidate that has no deal_breakers artifact, hydrate leaves legacy blob alone. After Stage 2, full round-trip.

## Stage 2: API — PUT intercept + GET hydrate + logging

**Done when:** `PUT /api/candidates/<id>/data` with body `{"context": {"deal_breakers": "alpha"}}` creates/rotates a current `deal_breakers` artifact row; library `candidate_data.context.deal_breakers` is not the SoT for that write; `GET /api/candidates/<id>` returns `candidate_data.context.deal_breakers` equal to the current artifact string when a row exists; sibling context keys in the same PUT still library-merge; Strengths PUT path unchanged; no React files changed.

1. In `src/ui/api/api_candidate.py`, in the `from src.core.candidate import (` block, add `hydrate_operative_deal_breakers_for_response` next to the Strengths hydrate import. Logger / `get_logger` already present — do not re-add.

2. In `get_candidate_detail`, immediately after `hydrate_operative_strengths_for_response(candidate_id, cd)`, add:

```python
    hydrate_operative_deal_breakers_for_response(candidate_id, cd)
```

(Idempotent with `get_candidate`'s hydrate — same double-call pattern as Strengths / base_resume.)

3. In `update_candidate_data`, next to the existing Strengths intercept (same `if body:` block), intercept Deal Breakers the same way:

```python
        deal_breakers_body = None
        deal_breakers_saved = False
        # … after strengths pop (or combined with it on the same ctx):
        ctx = body.get("context")
        if isinstance(ctx, dict) and "deal_breakers" in ctx:
            deal_breakers_body = ctx.pop("deal_breakers")
            if not ctx:
                body.pop("context", None)
```

Initialize `deal_breakers_saved = False` next to `strengths_saved = False` at the top of the handler (outside try, same placement as Strengths). Keep `deal_breakers_body` even when it is `""` so operative validation can raise — do not special-case empty here.

⚠️ **Decision:** If Strengths and Deal Breakers both appear in one PUT, pop both before library merge; each gets its own operative save. Prefer reading `ctx` once and popping both leaves, then `body.pop("context")` when empty — fewer duplicate `get`s; behavior must match sequential pops.

4. After the existing Strengths operative save block (still inside `if body:`), when `deal_breakers_body is not None`, call operative save:

```python
            if deal_breakers_body is not None:
                save_candidate_data(
                    candidate_id,
                    "candidate.context.deal_breakers",
                    deal_breakers_body,
                )
                deal_breakers_saved = True
```

⚠️ **Decision:** Catalog key string literal at the API call site matches Strengths (`"candidate.context.deal_breakers"`). Do not import `_DEAL_BREAKERS_ARTIFACT_KEY` from candidate (leading-underscore private).

5. On the success path of `update_candidate_data` (after the try succeeds, beside the existing Strengths api info), if `deal_breakers_saved`, emit one api info line (`stat.logging.info.api`):

```python
    if deal_breakers_saved:
        logger.info(
            "%s | api %s completed: PUT %s",
            candidate_id,
            f"/api/candidates/{candidate_id}/data",
            200,
        )
```

Do **not** emit this info for GETs or for PUTs that did not touch Deal Breakers. Strengths info line stays as-is (both may fire on a combined PUT).

6. Do **not** change the existing `except Exception as e:` `logger.exception` format — it already includes `type(e).__name__` and `e` (AST-1633 / Joan fix). Confirm it remains; no edit required unless somehow missing.

7. Do **not** edit React. Existing `ContextTextPage` PUT `{ context: { deal_breakers: draft } }` lands operative rows via this intercept; GET hydrate feeds the same `candidate_data.context.deal_breakers` leaf the page already reads (AST-1656 may retarget later; intercept is enough for AC4–6).

**Verify (hand):**

```bash
# After save via PUT (use a real candidate_id):
python3 -c "
from src.data import database
row = database.get_current_artifact('candidate', '<id>', 'deal_breakers')
assert row and row['artifact_data'] == '<saved string>'
"
# Second save with different body → new artifact_uuid; prior current=0
# Identical body → same uuid (AST-1635 shared no-op)
```

## Execution contract

- Execute steps in order within a stage; stages in order; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files, touch Ada/Katherine scopes, register other context keys, or add a backfill/migrate script.
- On ambiguity or drift — stop, comment on parent AST-1642 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `patt.artifact.write-operative` | pattern — read in full; Deal Breakers via `save_candidate_data` str-path → `save_artifact` (identical no-op already shared) |
| `patt.artifact.read-current` | pattern — read in full; hydrate via `get_candidate_current` |
| `patt.artifact.manage-catalog` | pattern — read in full; retire blob authority for registered Deal Breakers key only |
| `astral.standards.in-scope-only` | statute — Deal Breakers only; two named files |
| `stat.logging.info.entity` | statute — entity info on Deal Breakers operative save |
| `stat.logging.info.api` | statute — api info when Deal Breakers PUT completes |
| `stat.logging.error` | statute — exception once at PUT handler (already present; confirm) |

## Traceability

- Parent/child AC4 (operative round-trip) → Stage 1 §§4 + Stage 2 §§3–4 + verify (shared plain_text + AST-1635 no-op)
- Parent/child AC5 (blob not SoT on write) → Stage 1 §5 + Stage 2 §§3–4
- Parent/child AC6 (no backfill; legacy until re-save) → Stage 1 §6 miss path
- Editor reload (parent AC6 for UI) → Stage 1 §§6–7 + Stage 2 §2 (Katherine UI unchanged this ticket)
- Sibling freeze / catalog ownership → Ada AST-1654 on ftr; this ticket does not touch `ARTIFACT_CONFIG`
