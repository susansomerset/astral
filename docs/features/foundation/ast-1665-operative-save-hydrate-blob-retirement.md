<!-- linear-archive: AST-1665 archived 2026-09-24 -->

## Linear archive (AST-1665)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1665/operative-save-hydrate-blob-retirement-migrate-candidate  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-1645 — Migrate candidate_data.context.writing_preferences to use the artifact table  
**Blocked by / blocks / related:** parent: AST-1645; blocks: AST-1666

### Description

## What this implements

Wire Writing Preferences through candidate operative `plain_text` validation plus `get_candidate_current` hydrate on GET; intercept API PUT for operative save; stop durable library SoT writes for `context.writing_preferences`. No backfill helper. Does not own React chrome. After #1.

## Citations

`patt.artifact.write-operative`; `patt.artifact.read-current`; `patt.artifact.manage-catalog`; `astral.standards.in-scope-only`; `stat.logging.info.entity`; `stat.logging.info.api`; `stat.logging.error`

## Scope

- [X] `src/core/candidate.py` — operative validation for `plain_text`; hydrate overlay; gate library merge for `context.writing_preferences`.
- [X] `src/ui/api/api_candidate.py` — PUT intercept plus GET hydrate for Writing Preferences.

## Acceptance criteria

- [X] 4\. Operative round-trip — save creates current artifact row; second save retires prior.
- [X] 5\. Blob not SoT on write — operative save_artifact, not library-merge alone.
- [X] 6\. No backfill required — legacy blob until re-save; no bulk migrate.

## Boundaries

- [X] Does not own React chrome (sibling #3). Depends on catalog/token from #1.

## Notes for planning

Citations as above. Reuse AST-1629 Strengths operative/hydrate path.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### radia — 2026-09-16T00:47:07.043Z
[code-rubric] PROCEED (Commit: 7ae6c3d9) operative save hydrate clean

#### betty — 2026-09-16T00:44:28.759Z
`origin/sub/AST-1645/AST-1665-operative-save-hydrate-blob-retirement` @ `7ae6c3d9` · WP operative hydrate tests

#### joan — 2026-09-16T00:33:43.242Z
[plan-rubric] PROCEED (Commit: d9f6408a8f5f4b035ab01f384e1612db2ed89095) Writing Preferences operative plan

#### hedy — 2026-09-16T00:31:34.306Z
`origin/sub/AST-1645/AST-1665-operative-save-hydrate-blob-retirement` @ `d9f6408a8f5f4b035ab01f384e1612db2ed89095` · plan ready

---

# Operative save, hydrate, blob retirement

**Linear:** [AST-1665](https://linear.app/astralcareermatch/issue/AST-1665)
**Parent:** [AST-1645](https://linear.app/astralcareermatch/issue/AST-1645) — Migrate candidate_data.context.writing_preferences to use the artifact table
**Publish ref:** `sub/AST-1645/AST-1665-operative-save-hydrate-blob-retirement`

Wire Writing Preferences through the same candidate operative `plain_text` validation + hydrate-on-GET and API PUT intercept Strengths / Ideal Day already use; stop durable library SoT writes for `context.writing_preferences`. No backfill helper. No React chrome or catalog/token (siblings Ada / Katherine). Depends on catalog sibling [AST-1664](https://linear.app/astralcareermatch/issue/AST-1664) — `candidate.context.writing_preferences` is already on this tip after `sync-child` merged `origin/ftr/AST-1645-migrate-writing-preferences-artifact-table` (union with Ideal Day catalog). Mirror [AST-1633](https://linear.app/astralcareermatch/issue/AST-1633) / [AST-1659](https://linear.app/astralcareermatch/issue/AST-1659) — do not rederive `plain_text` validation.

## UAT fitness

- **AC restored:** Parent AC4 — "Operative round-trip — save creates current artifact row; second save retires prior." (full parent wording: Save Writing Preferences via Writing Preferences UI/API; `database.get_current_artifact('candidate', <id>, 'writing_preferences')` returns a row whose `artifact_data` matches the saved string; a second save creates a new uuid and retires prior `current=1`.) Parent AC5 — "Blob not SoT on write — operative save_artifact, not library-merge alone." Parent AC6 — "No backfill required — legacy blob until re-save; no bulk migrate."
- **Correct outcome:** After PUT with Writing Preferences text, a current `writing_preferences` artifact row holds that string; GET/`get_candidate` overlays it onto `candidate_data.context.writing_preferences` for the editor contract; a second save with different text rotates current; identical re-save no-ops (AST-1635); legacy blob-only candidates still show blob text until first operative save.
- **Sibling check:** AST-1664 catalog + `WRITING_PREFERENCES` token already on tip (`candidate.context.writing_preferences` / `plain_text` / artifact-typed token) — verified after ftr merge. AST-1666 owns React `CandidateWritingPreferences.tsx` only — existing PUT `{ context: { writing_preferences } }` keeps working via this ticket's intercept without UI changes. Strengths / priorities / deal_breakers / bio_summary / ideal_day operative paths stay intact except Writing Preferences is added to `_CONTEXT_OPERATIVE_LEAVES`.
- **Not sufficient:** Removing a stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Library-merge-only write of `context.writing_preferences` (or clearing the leaf without an artifact row) fails AC4/AC5. Re-implementing `plain_text` validation or touching `config.py` / React / `database.py` invents sibling scope. Coat-check or bulk backfill violates parent AC6 / non-goals.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/core/candidate.py` — operative validation for `plain_text`; hydrate overlay; gate library merge for `context.writing_preferences`.
- `src/ui/api/api_candidate.py` — PUT intercept plus GET hydrate for Writing Preferences.

Every Files Changed row and every Stage step stays inside those two files. No `config.py`, no React, no `database.py`, no other context keys, no pin/read-operative Writing Preferences surface, no bulk migrate.

**Already on tip (do not re-invent):**

- `plain_text` body validation in `save_candidate_data` str-path (AST-1633).
- Identical-to-current no-op before `save_artifact` (AST-1635) — applies to all catalog str-path keys including Writing Preferences once called.
- Shared `_CONTEXT_OPERATIVE_LEAVES` frozenset strip + per-leaf hydrate / PUT intercept / entity+api info / PUT `logger.exception` with type+message (AST-1633 … AST-1659).

This ticket **extends** those paths for `writing_preferences` / `candidate.context.writing_preferences` only.

**Catalog prerequisite:** Before Stage 1 hand-verify, `from src.utils.config import ARTIFACT_CONFIG; assert "candidate.context.writing_preferences" in ARTIFACT_CONFIG` must exit 0 (true on tip after ftr merge). If missing at **build-child** start — stop, comment on parent AST-1645 with Stage blocked (catalog sibling not on tip); do **not** register the key in this ticket.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Module docstring + `_WRITING_PREFERENCES_ARTIFACT_KEY`; add `writing_preferences` to `_CONTEXT_OPERATIVE_LEAVES`; entity info on Writing Preferences operative save; `hydrate_operative_writing_preferences_for_response` + call from `get_candidate` | core |
| `src/ui/api/api_candidate.py` | Import hydrate; PUT `/data`: pop `context.writing_preferences`, library-merge remainder, then operative save; GET detail hydrate Writing Preferences; api info when Writing Preferences PUT completes | ui |

**Out of this ticket (do not touch):** `src/utils/config.py` (sibling Ada AST-1664 — already merged onto tip); `CandidateWritingPreferences.tsx` / `ContextTextPage.tsx` (sibling Katherine AST-1666 — existing PUT `{ context: { writing_preferences } }` keeps working via intercept); `ArtifactEditor`; `database.py`; other context leaves; `tests/` / `docs/test-bible/**`; existing Strengths / Ideal Day operative wiring (leave as-is except frozenset membership).

## Stage 1: Core — Writing Preferences hydrate, library gate, entity log

**Done when:** `save_candidate_data(cid, "candidate.context.writing_preferences", "hello")` inserts a current artifact row whose `artifact_data` is `"hello"` (reuses existing `plain_text` validate + AST-1635 no-op); a second save with a different string returns a new uuid and prior row is not current; identical re-save returns the same uuid without retire; `get_candidate` overlays current Writing Preferences onto `candidate_data.context.writing_preferences` when a row exists and leaves the legacy blob alone on miss; dict-path `save_candidate_data(cid, {"context": {"writing_preferences": "x", "backstory": "y"}})` does not persist `writing_preferences` into the library blob (`backstory` still merges; strengths / ideal_day strip still works).

1. In `src/core/candidate.py` module docstring **In-scope** / operative bullets, after the Ideal Day line, add one line that Writing Preferences uses the same operative save + `get_candidate_current` hydrate path with catalog key `candidate.context.writing_preferences` (cite AST-1665). Do not rewrite base_resume or other leaf bullets.

2. Immediately below `_IDEAL_DAY_ARTIFACT_KEY`, add:

```python
_WRITING_PREFERENCES_ARTIFACT_KEY = "candidate.context.writing_preferences"
```

Update the `_CONTEXT_OPERATIVE_LEAVES` frozenset (same comment block) to include `"writing_preferences"`:

```python
# Catalog-owned context leaves — never durable library-merge SoT (AST-1633 / … / AST-1659 / AST-1665).
_CONTEXT_OPERATIVE_LEAVES = frozenset(
    {"strengths", "bio_summary", "priorities", "deal_breakers", "ideal_day", "writing_preferences"}
)
```

⚠️ **Decision:** Extend the existing closed frozenset — one strip site for all operative context leaves. Do not add a second independent `if` that duplicates the strip.

3. Do **not** add or edit the `plain_text` validation branch — it already exists (AST-1633). Empty / non-str bodies still raise `ValueError("plain_text body must be a non-empty string")` for Writing Preferences via that shared branch.

4. In the str-path, after a successful `database.save_artifact(...)` (the existing assign-then-return), extend the entity info chain so Writing Preferences also logs (`stat.logging.info.entity`), after the Ideal Day branch:

```python
        elif artifact_key == _WRITING_PREFERENCES_ARTIFACT_KEY:
            logger.info(
                "%s | candidate %s: %s (batch: %s)",
                candidate_id,
                "writing_preferences artifact saved",
                new_uuid,
                "-",
            )
```

Do **not** emit entity info on the AST-1635 identical-body no-op return path (same rule as Strengths / Ideal Day). Do **not** add entity info for `base_resume` or other keys on this ticket.

5. Do **not** rewrite the dict-path strip block — adding `"writing_preferences"` to `_CONTEXT_OPERATIVE_LEAVES` is the entire library gate. Confirm the existing strip still runs before `steps = []` and silently removes gated leaves (no raise).

6. Add `hydrate_operative_writing_preferences_for_response(candidate_id: str, cd: dict) -> None` immediately after `hydrate_operative_ideal_day_for_response`:

```python
def hydrate_operative_writing_preferences_for_response(candidate_id: str, cd: dict) -> None:
    """Overlay operative current Writing Preferences into candidate_data.context (display only).

    Miss → leave legacy context.writing_preferences blob untouched (parent AC6 migration window).
    Hit → write current string onto context.writing_preferences for the editor contract.
    """
    if not isinstance(cd, dict):
        return
    body = get_candidate_current(candidate_id, _WRITING_PREFERENCES_ARTIFACT_KEY)
    if body is None:
        return
    if not isinstance(body, str):
        return
    ctx = cd.get("context")
    if not isinstance(ctx, dict):
        ctx = {}
        cd["context"] = ctx
    ctx["writing_preferences"] = body
```

⚠️ **Decision:** On miss, **do not** pop/clear `context.writing_preferences` (same as Strengths / Ideal Day hydrate; unlike base_resume). Parent AC6: legacy blob until re-save; no coat-check fetch.

7. In `get_candidate`, immediately after `hydrate_operative_ideal_day_for_response(candidate_id, cd)`, add:

```python
    hydrate_operative_writing_preferences_for_response(candidate_id, cd)
```

**Verify (hand):** with a candidate that has no writing_preferences artifact, hydrate leaves legacy blob alone. After Stage 2, full round-trip.

## Stage 2: API — PUT intercept + GET hydrate + logging

**Done when:** `PUT /api/candidates/<id>/data` with body `{"context": {"writing_preferences": "alpha"}}` creates/rotates a current `writing_preferences` artifact row; library `candidate_data.context.writing_preferences` is not the SoT for that write; `GET /api/candidates/<id>` returns `candidate_data.context.writing_preferences` equal to the current artifact string when a row exists; sibling context keys in the same PUT still library-merge when not catalog-owned; Strengths / Ideal Day PUT paths unchanged; no React files changed.

1. In `src/ui/api/api_candidate.py`, in the `from src.core.candidate import (` block, add `hydrate_operative_writing_preferences_for_response` next to the Ideal Day hydrate import. Logger / `get_logger` already present — do not re-add.

2. In `get_candidate_detail`, immediately after `hydrate_operative_ideal_day_for_response(candidate_id, cd)`, add:

```python
    hydrate_operative_writing_preferences_for_response(candidate_id, cd)
```

(Idempotent with `get_candidate`'s hydrate — same double-call pattern as Strengths / Ideal Day / base_resume.)

3. In `update_candidate_data`, extend the context pop inside `if body:` to also pop Writing Preferences. Initialize `writing_preferences_saved = False` next to `ideal_day_saved = False` (outside the try, same scope).

```python
            writing_preferences_body = None
            # … alongside existing leaf body locals …
            ctx = body.get("context")
            if isinstance(ctx, dict):
                # existing pops for strengths / priorities / deal_breakers / bio_summary / ideal_day …
                if "writing_preferences" in ctx:
                    writing_preferences_body = ctx.pop("writing_preferences")
                if not ctx:
                    body.pop("context", None)
```

Keep `writing_preferences_body` even when it is `""` so operative validation can raise — do not special-case empty here.

⚠️ **Decision:** Prefer reading `ctx` once and popping all operative leaves (including Writing Preferences), then `body.pop("context")` when empty — matches current tip structure. Behavior must match sequential pops.

4. After the existing Ideal Day operative-save block (`if ideal_day_body is not None: ...`), add the Writing Preferences twin:

```python
            if writing_preferences_body is not None:
                save_candidate_data(
                    candidate_id,
                    "candidate.context.writing_preferences",
                    writing_preferences_body,
                )
                writing_preferences_saved = True
```

Place this so it still runs when the PUT is Writing-Preferences-only (body emptied after pop) — same “leaf-only PUT leaves body empty” pattern already in the handler.

⚠️ **Decision:** Catalog key string literal at the API call site matches Strengths / Ideal Day (`"candidate.context.writing_preferences"`). Do not import `_WRITING_PREFERENCES_ARTIFACT_KEY` from candidate (leading-underscore private).

5. On the success path of `update_candidate_data` (after the try succeeds, immediately after the existing `if ideal_day_saved:` api info block), if `writing_preferences_saved`, emit one api info line (`stat.logging.info.api`):

```python
    if writing_preferences_saved:
        logger.info(
            "%s | api %s completed: PUT %s",
            candidate_id,
            f"/api/candidates/{candidate_id}/data",
            200,
        )
```

Do **not** emit this info for GETs or for PUTs that did not touch Writing Preferences. Existing Strengths-group OR / Ideal Day info lines stay as-is (a multi-leaf PUT may emit multiple api info lines — acceptable).

6. Do **not** change the existing `except Exception as e:` `logger.exception` format — it already includes `type(e).__name__` and `e` (AST-1633 / Joan fix). Confirm it remains; no edit required unless somehow missing.

7. Do **not** edit React. Existing `ContextTextPage` PUT `{ context: { writing_preferences: draft } }` lands operative rows via this intercept; GET hydrate feeds the same `candidate_data.context.writing_preferences` leaf the page already reads (AST-1666 may retarget later; intercept is enough for AC4–6).

**Verify (hand):**

```bash
# After save via PUT (use a real candidate_id):
python3 -c "
from src.data import database
row = database.get_current_artifact('candidate', '<id>', 'writing_preferences')
assert row and row['artifact_data'] == '<saved string>'
"
# Second save with different body → new artifact_uuid; prior current=0
# Identical body → same uuid (AST-1635 shared no-op)
```

## Execution contract

- Execute steps in order within a stage; stages in order; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files, touch Ada/Katherine scopes, register other context keys, or add a backfill/migrate script.
- On ambiguity or drift — stop, comment on parent AST-1645 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `patt.artifact.write-operative` | pattern — read in full; Writing Preferences via `save_candidate_data` str-path → `save_artifact` (identical no-op already shared) |
| `patt.artifact.read-current` | pattern — read in full; hydrate via `get_candidate_current` |
| `patt.artifact.manage-catalog` | pattern — read in full; retire blob authority for registered Writing Preferences key only (catalog entry from AST-1664) |
| `astral.standards.in-scope-only` | statute — Writing Preferences only; two named files |
| `stat.logging.info.entity` | statute — entity info on Writing Preferences operative save |
| `stat.logging.info.api` | statute — api info when Writing Preferences PUT completes |
| `stat.logging.error` | statute — exception once at PUT handler (already present; confirm) |

## Traceability

- Parent/child AC4 (operative round-trip) → Stage 1 §§4 + Stage 2 §§3–4 + verify (shared plain_text + AST-1635 no-op)
- Parent/child AC5 (blob not SoT on write) → Stage 1 §§2+5 + Stage 2 §§3–4
- Parent/child AC6 (no backfill; legacy until re-save) → Stage 1 §6 miss path
- Editor reload (parent AC6 for UI) → Stage 1 §§6–7 + Stage 2 §2 (Katherine UI unchanged this ticket)
- Sibling freeze / catalog ownership → Ada AST-1664 on ftr (merged); this ticket does not touch `ARTIFACT_CONFIG`

## Review (build stub)

**Built:** `origin/sub/AST-1645/AST-1665-operative-save-hydrate-blob-retirement` @ `1781c083a2f7c94477051d0d168127945ff30341`.

**Stages delivered:**
- Stage 1: Writing Preferences hydrate + library gate + entity log — `774d2e777e8a421cdbcc31c87e478c91de9ec7e2`.
- Stage 2: PUT intercept + GET hydrate + api info — `1781c083a2f7c94477051d0d168127945ff30341`.

**Betty:** at **Code Complete** — cover operative `plain_text` validation reuse for Writing Preferences (non-empty string), `save_artifact` round-trip + retire prior current, identical-body no-op (AST-1635 shared), dict-path strips `context.writing_preferences` via `_CONTEXT_OPERATIVE_LEAVES`, hydrate overlays current / leaves legacy on miss, PUT pop+operative path, GET hydrate leaf; Strengths / Ideal Day paths unchanged.

## Joan validate

[plan-rubric]
**Ticket:** AST-1665
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `sub/AST-1645/AST-1665-operative-save-hydrate-blob-retirement` @ `d9f6408a8f5f4b035ab01f384e1612db2ed89095`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.write-operative | A | | |
| patt.artifact.read-current | A | | |
| patt.artifact.manage-catalog | A | | |
| astral.standards.in-scope-only | A | | |
| stat.logging.info.entity | A | | |
| stat.logging.info.api | A | | |
| stat.logging.error | A | | |

## Traceability

AC4→S1§§2-5+S2§§3-4+verify; AC5→S1§§2+5+S2§§3-4; AC6→S1§6 miss-path — parent editor-reload AC6 via hydrate (S1§§6-7,S2§2); UI chrome N/A (AST-1666); parent AC1–3/AC8–9 N/A (catalog AST-1664 / UI #3).

## Findings

None.

### R6 — Definition fidelity (checklist)

- Scope limited to `candidate.py` + `api_candidate.py`; explicit scope gate; build precondition on AST-1664 catalog key (satisfied on tip).
- Faithfully mirrors AST-1659 / AST-1652 operative path: extends `_CONTEXT_OPERATIVE_LEAVES` with `writing_preferences`; reuses shared `plain_text` str-path + AST-1635 identical no-op; `hydrate_operative_writing_preferences_for_response` parallels Ideal Day / Strengths (miss→legacy blob / hit→overlay); dict-path strip via frozenset; PUT pop + operative save + GET hydrate follow existing Ideal Day intercept pattern.
- UAT fitness cites AC4–AC6, names correct outcome vs symptom-only fixes, rejects library-merge-only / config / React / backfill wrong paths.
- Entity/api info logging matches shipped Ideal Day format; error handler left as single `logger.exception` at route (confirm-only, no edit).
- Self-assessment `Confirm Chuckles estimate: 3 — agree` is honest for two-file Strengths-pattern wiring.
- Plan Discuss rounds completed: **0**.

context_tokens≈58000

## Radia review

[code-rubric]
**Ticket:** AST-1665
**Publish ref:** `7ae6c3d918cd314180e06553ac925f33151d7ab1`
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.write-operative | A | | |
| patt.artifact.read-current | A | | |
| patt.artifact.manage-catalog | A | | |
| astral.standards.in-scope-only | A | | |
| stat.logging.info.entity | A | | |
| stat.logging.info.api | A | | |
| stat.logging.error | A | | |

## Column diff vs plan stage

(aligned)

## Frame diff

(none)

## Findings

### discuss

- **Publish-ref three-dot diff vs ticket scope gate.** `origin/dev...origin/sub/AST-1645/AST-1665-operative-save-hydrate-blob-retirement` is 11 files / ~811 lines; AST-1665 engineer commits (`774d2e77`, `1781c083`) touch only `src/core/candidate.py` and `src/ui/api/api_candidate.py` (+62 lines product). The wider diff carries prerequisite **AST-1664** catalog work (`src/utils/config.py`, `docs/features/foundation/ast-1664-*.md`) via `merge(ftr): union writing_preferences catalog with ideal_day tip`, plus Betty `merge-tests` and `2abd0400` stripping parallel-epic AST-1659 bible pollution. Expected epic stacking on a dependent child — not engineer scope creep — but Chuckles should note at merge-child that the three-dot diff is wider than the explicit two-file gate.

### advisory

- **Parallel-epic bible hygiene:** `2abd0400 test(AST-1661): strip AST-1659 Ideal Day pollution from publish tip` and net bible deletions (e.g. AST-1655 deal_breakers block removed) reflect tip-alignment cleanup on a union branch, not AST-1665 product logic.

## What's solid

- Stage 1 + 2 deliver the AST-1659 mirror faithfully: `_WRITING_PREFERENCES_ARTIFACT_KEY`; `writing_preferences` added to `_CONTEXT_OPERATIVE_LEAVES` (single frozenset strip site); `hydrate_operative_writing_preferences_for_response` (miss → legacy blob untouched / hit → overlay); `get_candidate` + `get_candidate_detail` hydrate; PUT pop + operative `save_candidate_data("candidate.context.writing_preferences", …)`; shared `plain_text` str-path validation + AST-1635 identical no-op (entity info only after real `save_artifact`, not on no-op return).
- Blob retirement (AC5/AC6): dict-path strips `writing_preferences` from library merge; operative row is SoT; legacy blob preserved on hydrate miss.
- Logging matches shipped Ideal Day / Strengths pipes: entity `writing_preferences artifact saved` chain; api info on `writing_preferences_saved`; existing `logger.exception` with `type(e).__name__` + `e` unchanged at PUT handler.
- Betty coverage (`TestAst1665WritingPreferencesOperativeSaveHydrate`, `TestAst1665WritingPreferencesOperativeApi`) exercises plain_text reject, save/retire, identical no-op, dict strip, hydrate hit/miss, PUT round-trip, sibling `backstory` library-merge, GET hydrate — integration correctly none.

## Recommended actions

- Chuckles: append artifact, `docs(AST-1665): Radia review — clean`, post slim upshot, → **Review Posted** → datt **PROCEED** to User Testing.

context_tokens≈62000
