# Operative save, hydrate, blob retirement

**Linear:** [AST-1649](https://linear.app/astralcareermatch/issue/AST-1649)
**Parent:** [AST-1647](https://linear.app/astralcareermatch/issue/AST-1647) — Migrate candidate bio summary to use the artifact table and remove from candidate profile page
**Publish ref:** `sub/AST-1647/AST-1649-operative-save-hydrate-blob-retirement`

Wire bio summary through the same candidate operative `plain_text` validation + hydrate-on-GET and API PUT intercept Strengths already uses; stop durable library SoT writes for `context.bio_summary`. No backfill helper. No React chrome or catalog/nav (siblings Ada / Katherine). Depends on catalog sibling [AST-1648](https://linear.app/astralcareermatch/issue/AST-1648) — `candidate.context.bio_summary` is already on `origin/ftr/AST-1647-migrate-bio-summary-artifact` and this publish-ref tip after sync.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/core/candidate.py` — extend operative validation/hydrate/library-gate for `context.bio_summary` / `candidate.context.bio_summary`.
- `src/ui/api/api_candidate.py` — PUT intercept + GET hydrate for bio summary.

Every Files Changed row and every Stage step stays inside those two files. No `config.py`, no React, no `database.py`, no other context keys, no pin/read-operative bio-summary surface, no bulk migrate.

**Already on tip (do not re-invent):**

- `plain_text` body validation in `save_candidate_data` str-path (AST-1633).
- Identical-to-current no-op before `save_artifact` (AST-1635) — applies to all catalog str-path keys including bio summary once called.
- Strengths library gate / hydrate / PUT intercept / entity+api info / PUT `logger.exception` with type+message (AST-1633 + Joan fix).

This ticket **extends** those paths for `bio_summary` / `candidate.context.bio_summary` only.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Module constant + docstring; extend dict-path library gate to strip `context.bio_summary`; `hydrate_operative_bio_summary_for_response` + call from `get_candidate`; entity info on bio_summary operative save | core |
| `src/ui/api/api_candidate.py` | PUT `/data`: pop `context.bio_summary`, library-merge remainder, then operative save; GET detail hydrate bio summary; api info when bio-summary PUT completes | ui |

**Out of this ticket (do not touch):** `src/utils/config.py` (sibling Ada / AST-1648); `CandidateBioSummary.tsx` / `routes.tsx` / `ContextTextPage.tsx` (sibling Katherine — existing PUT `{ context: { bio_summary } }` keeps working via intercept once page lands); `ArtifactEditor`; `database.py`; other context leaves; `tests/` / `docs/test-bible/**`.

## Stage 1: Core — library gate, hydrate, entity log

**Done when:** `save_candidate_data(cid, "candidate.context.bio_summary", "hello")` inserts a current artifact row whose `artifact_data` is `"hello"` (existing `plain_text` validate + AST-1635 identical no-op unchanged); a second save with a different string returns a new uuid and prior row is not current; identical re-save returns the same uuid with no new row; `get_candidate` overlays current bio summary onto `candidate_data.context.bio_summary` when a row exists and leaves the legacy blob alone on miss; dict-path `save_candidate_data(cid, {"context": {"bio_summary": "x", "priorities": "y"}})` does not persist `bio_summary` into the library blob (priorities still merge; `strengths` still stripped as today).

1. In `src/core/candidate.py` module docstring **In-scope** / operative bullets, add one line that bio summary uses the same operative save + `get_candidate_current` hydrate path with catalog key `candidate.context.bio_summary` (cite AST-1649). Keep the existing Strengths / base_resume lines.

2. Immediately after `_STRENGTHS_ARTIFACT_KEY = "candidate.context.strengths"`, add:

```python
_BIO_SUMMARY_ARTIFACT_KEY = "candidate.context.bio_summary"
# Catalog-owned context leaves — never durable library-merge SoT (AST-1633 / AST-1649).
_CONTEXT_OPERATIVE_LEAVES = frozenset({"strengths", "bio_summary"})
```

⚠️ **Decision:** Closed frozenset next to the two catalog constants — one strip site for all operative context leaves. Do not hardcode `bio_summary` in a second independent `if` that duplicates the Strengths strip.

3. **Do not** change the existing `plain_text` validation branch or the AST-1635 identical-to-current gate. Bio summary rides those paths via catalog `body_shape: "plain_text"`.

4. In the str-path, after a successful `database.save_artifact(...)` (assign-then-return already present), extend the entity info emission so bio summary also logs (`stat.logging.info.entity`). Keep Strengths behavior:

```python
        if artifact_key == _STRENGTHS_ARTIFACT_KEY:
            logger.info(
                "%s | candidate %s: %s (batch: %s)",
                candidate_id,
                "strengths artifact saved",
                new_uuid,
                "-",
            )
        elif artifact_key == _BIO_SUMMARY_ARTIFACT_KEY:
            logger.info(
                "%s | candidate %s: %s (batch: %s)",
                candidate_id,
                "bio_summary artifact saved",
                new_uuid,
                "-",
            )
        return new_uuid
```

Do **not** emit entity info on the identical-body no-op return (same rule as Strengths / AST-1635). Do **not** add entity info for `base_resume` or other keys.

5. Replace the Strengths-only dict-path strip with the closed-set strip (same location — after contact uniqueness / before `steps = []`):

```python
    # AST-1633 / AST-1649: catalog owns these context leaves — never library-merge SoT.
    ctx = blob_merge.get("context")
    if isinstance(ctx, dict):
        cleaned = {k: v for k, v in ctx.items() if k not in _CONTEXT_OPERATIVE_LEAVES}
        if cleaned:
            blob_merge["context"] = cleaned
        else:
            blob_merge.pop("context", None)
```

Do **not** raise when a gated leaf is present — strip silently. Other context keys pass through.

6. Add `hydrate_operative_bio_summary_for_response(candidate_id: str, cd: dict) -> None` immediately after `hydrate_operative_strengths_for_response`:

```python
def hydrate_operative_bio_summary_for_response(candidate_id: str, cd: dict) -> None:
    """Overlay operative current bio summary into candidate_data.context (display only).

    Miss → leave legacy context.bio_summary blob untouched (parent AC8 / ticket AC6 migration window).
    Hit → write current string onto context.bio_summary for the editor contract.
    """
    if not isinstance(cd, dict):
        return
    body = get_candidate_current(candidate_id, _BIO_SUMMARY_ARTIFACT_KEY)
    if body is None:
        return
    if not isinstance(body, str):
        return
    ctx = cd.get("context")
    if not isinstance(ctx, dict):
        ctx = {}
        cd["context"] = ctx
    ctx["bio_summary"] = body
```

⚠️ **Decision:** On miss, **do not** pop/clear `context.bio_summary` (same migration-window choice as Strengths; unlike base_resume hydrate, which strips blob on miss). Parent AC8 / ticket AC6: legacy blob until re-save; no coat-check.

7. In `get_candidate`, immediately after the existing `hydrate_operative_strengths_for_response(candidate_id, cd)` call, add:

```python
    hydrate_operative_bio_summary_for_response(candidate_id, cd)
```

**Verify (hand):** with a candidate that has no bio_summary artifact, hydrate leaves legacy blob alone. After Stage 2, full round-trip.

## Stage 2: API — PUT intercept + GET hydrate + logging

**Done when:** `PUT /api/candidates/<id>/data` with body `{"context": {"bio_summary": "alpha"}}` creates/rotates a current `bio_summary` artifact row; library `candidate_data.context.bio_summary` is not the SoT for that write; `GET /api/candidates/<id>` returns `candidate_data.context.bio_summary` equal to the current artifact string when a row exists; sibling context keys (e.g. `priorities`) in the same PUT still library-merge; Strengths PUT path unchanged; no React files changed.

1. In `src/ui/api/api_candidate.py`, in the `from src.core.candidate import (` block, add `hydrate_operative_bio_summary_for_response` next to the existing Strengths hydrate import. Logger / `get_logger` already present — do not re-add.

2. In `get_candidate_detail`, immediately after the existing `hydrate_operative_strengths_for_response(candidate_id, cd)` call, add:

```python
    hydrate_operative_bio_summary_for_response(candidate_id, cd)
```

(Idempotent with `get_candidate`'s hydrate — same double-call pattern as Strengths / base_resume.)

3. In `update_candidate_data`, replace the Strengths-only context pop at the start of `if body:` with a dual-leaf pop (Strengths first, then bio summary). Initialize `bio_summary_saved = False` next to the existing `strengths_saved = False` (outside the try, same scope).

```python
            strengths_body = None
            bio_summary_body = None
            ctx = body.get("context")
            if isinstance(ctx, dict) and "strengths" in ctx:
                strengths_body = ctx.pop("strengths")
            if isinstance(ctx, dict) and "bio_summary" in ctx:
                bio_summary_body = ctx.pop("bio_summary")
            if isinstance(ctx, dict) and not ctx:
                body.pop("context", None)
```

Keep `bio_summary_body` even when it is `""` so operative validation can raise — do not special-case empty here.

⚠️ **Decision:** One empty-`context` cleanup after both pops. Same `ctx` reference; Strengths order preserved for minimal diff vs AST-1633.

4. After the existing Strengths operative-save block (`if strengths_body is not None: ...`), add the bio-summary twin:

```python
            if bio_summary_body is not None:
                save_candidate_data(
                    candidate_id,
                    "candidate.context.bio_summary",
                    bio_summary_body,
                )
                bio_summary_saved = True
```

Place this so it still runs when the PUT is bio-summary-only (body emptied after pop) — same “Strengths-only PUT leaves body empty” pattern already in the handler.

⚠️ **Decision:** Catalog key string literal at the API call site matches Strengths (`"candidate.context.bio_summary"`). Do not import `_BIO_SUMMARY_ARTIFACT_KEY` from candidate (leading-underscore private).

5. On the success path of `update_candidate_data` (after the try succeeds, near the existing `if strengths_saved:` api info), if `bio_summary_saved`, emit one api info line (`stat.logging.info.api`):

```python
    if bio_summary_saved:
        logger.info(
            "%s | api %s completed: PUT %s",
            candidate_id,
            f"/api/candidates/{candidate_id}/data",
            200,
        )
```

Keep the existing `if strengths_saved:` block unchanged. A PUT that saves both may emit two api info lines — acceptable (one progress line per leaf that completed).

6. **Do not** rewrite the existing `except Exception as e:` `logger.exception(...)` block — it already includes `type(e).__name__`, `e`, and “returning 400” (`stat.logging.error`). Bio-summary ValueErrors ride the same handler.

7. Do **not** edit React. When Katherine’s Bio Summary page lands, `ContextTextPage` PUT `{ context: { bio_summary: draft } }` lands operative rows via this intercept; GET hydrate feeds `candidate_data.context.bio_summary`.

**Verify (hand):**

```bash
# After save via PUT (use a real candidate_id):
python3 -c "
from src.data import database
row = database.get_current_artifact('candidate', '<id>', 'bio_summary')
assert row and row['artifact_data'] == '<saved string>'
"
# Second distinct save → new artifact_uuid; prior current=0
# Identical re-save → same uuid (AST-1635 no-op)
```

## Execution contract

- Execute steps in order within a stage; stages in order; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files, touch Ada/Katherine scopes, register other context keys, or add a backfill/migrate script.
- On ambiguity or drift — stop, comment on parent AST-1647 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `patt.artifact.write-operative` | pattern — read in full; bio summary via `save_candidate_data` str-path → `save_artifact` (identical no-op already shared) |
| `patt.artifact.read-current` | pattern — read in full; hydrate via `get_candidate_current` |
| `patt.artifact.manage-catalog` | pattern — read in full; retire blob authority for registered bio_summary key only (catalog entry from AST-1648) |
| `astral.standards.in-scope-only` | statute — bio summary only; two named files |
| `stat.logging.info.entity` | statute — entity info on bio_summary operative save |
| `stat.logging.info.api` | statute — api info when bio-summary PUT completes |
| `stat.logging.error` | statute — exception once at PUT handler (already present; do not regress) |

## Traceability

- Parent/child AC4 (operative round-trip) → Stage 1 §§4–6 + Stage 2 §§3–4 + verify
- Parent/child AC5 (blob not SoT on write) → Stage 1 §5 + Stage 2 §§3–4
- Parent/child AC6 / parent AC8 (no backfill; legacy until re-save) → Stage 1 §6 miss path
- Sibling freeze (parent AC9) → scope gate; no other `ARTIFACT_CONFIG` keys
- Editor reload (parent AC7, Katherine) → Stage 1 §§6–7 + Stage 2 §2 (UI sibling unchanged)

## Review (build stub)

**Built:** `origin/sub/AST-1647/AST-1649-operative-save-hydrate-blob-retirement` @ `0a0af4bc01caaa0158ec39b0ce8812a045f2ed58`.

**Stages delivered:**
- Stage 1: library gate + hydrate + entity log — `fecec8815e0a6a86c269d8d47d44e3ebf8580024`.
- Stage 2: PUT intercept + GET hydrate + api info — `0a0af4bc01caaa0158ec39b0ce8812a045f2ed58`.

**Betty:** at **Code Complete** — cover operative bio_summary round-trip + retire prior current, identical-body no-op (shared AST-1635), dict-path strips `context.bio_summary` (and still strips strengths), hydrate overlays current / leaves legacy on miss, PUT pop+operative path, GET hydrate leaf, empty bio_summary → 400.

## Joan validate

```
[plan-rubric]
**Ticket:** AST-1649
**Overall:** APPROVED
**Corpus:** fc0c368e59
**Publish-ref tip:** f98540691b55e1538054b325ac76ebd171b1168e

## Canon scores

| Id | Grade | Effort | One-line |
|----|-------|--------|----------|
| patt.artifact.write-operative | A | | |
| patt.artifact.read-current | A | | |
| patt.artifact.manage-catalog | A | | |
| astral.standards.in-scope-only | A | | |
| stat.logging.info.entity | A | | |
| stat.logging.info.api | A | | |
| stat.logging.error | A | | |

## Traceability

AC4→S1:4–6,S2:3–4 · AC5→S1:5,S2:3–4 · AC6→S1:6(miss) · Parent AC1–3/7/9/10→N/A (AST-1648/1650) · Parent AC8→S1:6 (legacy blob until re-save)

## Findings

### acceptable

- **Location:** Plan preamble / Execution contract
- **Finding:** Build assumes AST-1648 catalog key `candidate.context.bio_summary` is on the synced epic tip before operative paths run.
- **Recommendation:** Engineer syncs `origin/ftr/AST-1647-migrate-bio-summary-artifact` (or waits for Ada merge) before Stage 1 — already documented; not a plan defect.

context_tokens≈52000
```

**Summary:** AST-1649 is **APPROVED**. The plan faithfully clones the AST-1633 Strengths operative pattern for bio summary across exactly two scoped files: library-gate strip via `_CONTEXT_OPERATIVE_LEAVES`, str-path save (reusing `plain_text` + AST-1635 identical no-op), hydrate-on-miss preserving legacy blob (AC6/AC8), PUT intercept + GET hydrate, and entity/api logging matching existing Strengths blocks. All seven canon ids grade **A**; no fix-now or discuss blockers. Status **Plan Ready**, zero `[plan-discuss]` rounds.
