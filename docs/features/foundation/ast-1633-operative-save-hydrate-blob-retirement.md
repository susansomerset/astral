<!-- linear-archive: AST-1633 archived 2026-09-24 -->

## Linear archive (AST-1633)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1633/operative-save-hydrate-blob-retirement-migrate-candidate  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / 5  
**Parent:** AST-1629 — Migrate candidate_data.context.strengths to use the artifact table  
**Blocked by / blocks / related:** parent: AST-1629; blocks: AST-1634

### Description

## What this implements

Wire Strengths through candidate operative `plain_text` validation + `get_candidate_current` hydrate on GET; intercept API PUT for operative save; stop durable library SoT writes for `context.strengths`. No backfill helper. Does not own React chrome. After catalog sibling.

## Citations

`patt.artifact.write-operative`; `patt.artifact.read-current`; `patt.artifact.manage-catalog`; `astral.standards.in-scope-only`; `stat.logging.info.entity`; `stat.logging.info.api`; `stat.logging.error`

## Scope

`src/core/candidate.py` — operative validation for `plain_text`; hydrate overlay; gate library merge for `context.strengths`. `src/ui/api/api_candidate.py` — PUT intercept + GET hydrate for Strengths.

## Acceptance criteria

- [X] 4\. **Operative round-trip** — Save Strengths via Strengths UI/API; `database.get_current_artifact('candidate', <id>, 'strengths')` returns matching string; second save new uuid + retire prior current.
- [X] 5\. **Blob not SoT on write** — Successful Strengths save calls operative `save_artifact`; does not rely on library-merge alone.
- [X] 6\. **No backfill required** — No bulk migrate-all; legacy blob until re-save.
- [X] 7\. **Sibling freeze** — no other context keys in `ARTIFACT_CONFIG`.

## Boundaries

- [X] Does not own catalog/token registration (sibling Ada). Does not own React ContextTextPage (sibling Katherine). No legacy blob backfill.

## Notes for planning

After catalog sibling. Logging statutes on touched entity/api paths.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1629-migrate-strengths-artifact-table`, child `sub/AST-1629/<this-id>-operative-save-hydrate-blob-retirement`. Created at dispatch-parent.

### Comments

#### radia — 2026-09-14T23:51:45.702Z
[code-rubric] PROCEED (Commit: 4f4475e9ac55) operative save clean

#### betty — 2026-09-14T23:48:56.444Z
origin/sub/AST-1629/AST-1633-operative-save-hydrate-blob-retirement @ 4f4475e9 · strengths operative tests

#### joan — 2026-09-14T23:41:44.298Z
[plan-rubric] PROCEED (Commit: 797e0cd5) operative hydrate path clean

#### hedy — 2026-09-14T23:39:29.711Z
`origin/sub/AST-1629/AST-1633-operative-save-hydrate-blob-retirement` @ `797e0cd5195ab2c9eb7a20ce694b44db599b3189` · plan ready

---

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

## Review (build stub)

**Built:** `origin/sub/AST-1629/AST-1633-operative-save-hydrate-blob-retirement` @ `20d3e95d509e80d5c1cbaf8e09b893815d683060`.

**Stages delivered:**
- Stage 1: plain_text validate + hydrate + library gate — `bce5e8ce15f41f9d827b1259e24a05484728d4d6`.
- Stage 2: PUT intercept + GET hydrate + logging (Joan exception format) — `20d3e95d509e80d5c1cbaf8e09b893815d683060`.

**Betty:** at **Code Complete** — cover operative `plain_text` validation (non-empty string), Strengths `save_artifact` round-trip + retire prior current, dict-path strips `context.strengths`, hydrate overlays current / leaves legacy on miss, PUT pop+operative path, GET hydrate leaf.

## Joan validate

```
[plan-rubric]
**Ticket:** AST-1633
**Overall:** APPROVED
**Corpus:** 0b920f4e7dfc842c1032277aa99ac34e1bd0f9b9
**Publish ref tip:** 797e0cd5195ab2c9eb7a20ce694b44db599b3189

## Canon scores

patt.artifact.write-operative | A | | Stage 1 str-path → validate → save_artifact retire+insert; returns uuid; mirrors base_resume pilot
patt.artifact.read-current | A | | get_candidate_current + hydrate overlay on GET/get_candidate; miss leaves legacy blob per parent AC7 (documented §6)
patt.artifact.manage-catalog | A | | Retires Strengths library SoT: API pop + dict-path strip; depends on catalog sibling already on ftr
astral.standards.in-scope-only | A | | Two scoped files only; explicit scope gate; no config/React/database/backfill
stat.logging.info.entity | A | | Stage 1 §4 pipe on Strengths operative save only
stat.logging.info.api | A | | Stage 2 §5 one info line when Strengths PUT completes 200
stat.logging.error | C | 2 | Stage 2 §6 — handler exception log omits exc type/message in the format string (traceback only)

## Traceability

AC4→Stage 1 §§3–4 + Stage 2 §§3–4 + verify; AC5→Stage 1 §5 + Stage 2 §§3–4; AC6→Stage 1 §6 miss path; AC7→scope gate (no new catalog keys); parent AC6 editor reload→Stage 1 §§6–7 + Stage 2 §2 (UI sibling unchanged).

## Findings

### discuss

- **Location:** Stage 2 §6 / `update_candidate_data` except
- **Finding:** `logger.exception("%s | api update_candidate_data failed — returning 400", candidate_id)` satisfies once-at-handler and next-step, but `stat.logging.error` Do examples include `type(exc).__name__` and `exc` in the message body, not only traceback.
- **Recommendation:** At build, extend the format string per statute Do (`… %s: %s … returning 400`, type(e), e) — mechanical tweak.

### acceptable

- **Location:** Stage 1 §6 / `patt.artifact.read-current`
- **Finding:** Miss path keeps legacy `context.strengths` blob instead of empty contract — diverges from pattern default but matches parent AC7 / epic no-backfill window; plan documents explicitly.
- **Recommendation:** None — definition-faithful migration window.

### acceptable

- **Location:** Canon clerk
- **Finding:** Four frozen ids (`patt.artifact.*`, `astral.standards.in-scope-only`) outside clerk `active/` roster; scored from draft/statute files at epic worktree.
- **Recommendation:** No plan change.

context_tokens≈38000
```

## Radia review

```
[code-rubric]
**Ticket:** AST-1633
**Publish ref:** 4f4475e9ac55349f67fcfc805639706b56c86927
**Corpus:** 0b920f4e7dfc842c1032277aa99ac34e1bd0f9b9
**Overall:** CLEAN

## Canon scores

patt.artifact.write-operative | A | | Str-path `plain_text` validate → `save_artifact` retire+insert; returns uuid; mirrors base_resume pilot
patt.artifact.read-current | A | | `get_candidate_current` + `hydrate_operative_strengths_for_response` on `get_candidate` and GET detail; hit overlays current string
patt.artifact.manage-catalog | A | | Retires Strengths library SoT: API pop + dict-path strip; operative row is authoritative on write
astral.standards.in-scope-only | A | | Product commits confined to `candidate.py` + `api_candidate.py`; catalog dependency from sibling AST-1632 on branch tip
stat.logging.info.entity | A | | Strengths operative save emits pipe-format entity info only for `_STRENGTHS_ARTIFACT_KEY`
stat.logging.info.api | A | | One api info line when Strengths PUT completes 200, after successful handler path
stat.logging.error | A | | Handler `logger.exception` includes `type(e).__name__`, `e`, and next-step “returning 400” — Joan’s plan-stage gap closed at build

## Column diff vs plan stage

stat.logging.error | Joan C/2 → Radia A | Build extended except format string per statute Do (`type(e).__name__`, `e` in message body)

## Frame diff

(none)

## Findings

### advisory

- **Location:** `src/core/candidate.py` — `_STRENGTHS_ARTIFACT_KEY` placement
- **Finding:** Constant is defined at module line ~1511 but referenced in `save_candidate_data` at ~800. Python late-binding makes this runtime-safe; plan preferred placement near `_PILOT_BASE_RESUME_ARTIFACT_KEY` or above the hydrate helper.
- **Recommendation:** Optional style tidy in a future pass; not a canon or AC blocker.

### advisory

- **Location:** `hydrate_operative_strengths_for_response` / `patt.artifact.read-current`
- **Finding:** Miss path preserves legacy `context.strengths` blob instead of empty contract — diverges from pattern default but matches parent AC7 / no-backfill migration window; plan documents explicitly.
- **Recommendation:** None for AST-1633; expected until operator re-save.

### advisory

- **Location:** Canon clerk / frozen list
- **Finding:** Four frozen ids (`patt.artifact.*`, `astral.standards.in-scope-only`) live outside clerk `active/` roster; scored from draft/statute files at epic worktree.
- **Recommendation:** Corpus hygiene downstream; scores from those files' Statement/Examples.

## What's solid

- Stage 1 + Stage 2 plan delivered: `plain_text` validation (non-empty string), operative save with retire+insert, dict-path `context.strengths` strip, hydrate overlay / legacy-on-miss, PUT pop+operative intercept, GET detail hydrate, empty-strengths → 400.
- Betty manifest coverage is thorough: `TestAst1633StrengthsOperativeSaveHydrate` (core round-trip, retire, dict strip, hydrate hit/miss) and `TestAst1633StrengthsOperativeApi` (PUT/GET, sibling context merge, empty 400).
- Joan’s `stat.logging.error` discuss item resolved in `20d3e95d` — exception log now carries live facts plus traceback.

## Scope notes (not findings)

- Three-dot diff vs `origin/dev` includes AST-1632 catalog commits (`config.py`, sibling tests/bible) stacked on the epic branch; AST-1633 product commits touch only the two scoped files.
- `tests/` and `docs/test-bible/**` changes are expected Betty pipeline artifacts.
- Estimate **5** fits operative save + hydrate + API intercept + targeted test/bible updates.

## Recommended actions

- Chuckles: append artifact, commit `docs(AST-1633): Radia review — clean`, post slim upshot, move to **Review Posted**.
- datt: **PROCEED** → **User Testing** (no resolve-child round needed).

context_tokens≈32000
```

## Bug: AST-1635 — Do not save a new artifact version when body is identical to current

### As-is

Operative Strengths save via `save_candidate_data` str-path always calls `database.save_artifact` (retire prior `current=1`, insert new uuid) even when the validated body is identical to the existing current row's `artifact_data`. Re-saving unchanged Strengths text creates a useless new version.

### To-be

When the body being saved is identical to the current artifact version for that catalog key, do not retire+insert — leave the existing `current` row in place and return its `artifact_uuid`. When the body differs (or there is no current row), keep today's retire+insert behavior.

### Repro

1. Candidate has a current Strengths artifact with body `"alpha"`.
2. PUT `/api/candidates/<id>/data` with `{"context": {"strengths": "alpha"}}` (same string), or call `save_candidate_data(cid, "candidate.context.strengths", "alpha")`.
3. Observe: new `artifact_uuid`, prior row `current=0`, new row `current=1` with the same `"alpha"` body.

Fixture shape (core):

```python
# After one successful operative save of "alpha":
uid1 = save_candidate_data(cid, "candidate.context.strengths", "alpha")
uid2 = save_candidate_data(cid, "candidate.context.strengths", "alpha")  # identical
# As-is: uid2 != uid1 and prior current retired.
# To-be: uid2 == uid1; still exactly one current=1 row for strengths.
```

### Root cause

`save_candidate_data` str-path (AST-1633 Stage 1) validates then unconditionally invokes `database.save_artifact`. There is no compare-to-current gate. Parent epic Component scope marks `database.py` **untouched**, so the no-op belongs in the entity operative wrapper — not a data-layer change.

### Proposed change

In `src/core/candidate.py`, inside `save_candidate_data` **str-path**, after body_shape validation and after `artifact_type = artifact_key.rsplit(".", 1)[-1]`, **before** `database.save_artifact(...)`:

1. Load the current row:

```python
        current_row = database.get_current_artifact(
            entry["entity_type"], candidate_id, artifact_type
        )
```

2. If `current_row is not None` and `current_row.get("artifact_data") == blob`, return the existing pin without writing:

```python
        if current_row is not None and current_row.get("artifact_data") == blob:
            return current_row.get("artifact_uuid")
```

⚠️ **Decision:** Equality is Python `==` on deserialized `artifact_data` vs the already-validated `blob` (plain_text string or resume_content dict). No extra normalize/strip — `plain_text` validation still requires non-empty after strip, but stored value is compared as passed. Applies to **all** candidate catalog str-path keys (shared operative path in `candidate.py`), not a Strengths-only `if` — matches bug wording; stays inside `candidate.py` (parent Component scope). Do **not** edit `database.py` (parent: untouched). Do **not** change `api_candidate.py` — PUT still calls operative save; core no-op is enough.

3. On the no-op return path: do **not** emit the Strengths `logger.info` entity line (that line stays only after a real `save_artifact` insert). On a real insert path, behavior unchanged (including Strengths info log).

4. When `current_row` is missing or `artifact_data != blob`, fall through to existing `save_artifact` + Strengths log + return new uuid.

No React, no config, no `database.py`, no other context keys.

### Blast radius

- `save_candidate_data` str-path also serves `candidate.artifacts.base_resume` — identical base_resume re-save will likewise skip a new version (same gate; desired shared-path behavior).
- Job/tracker `save_job_artifact` is **out of this bug** (parent Component scope for this UAT fix is candidate operative; do not widen to tracker/database).
- Betty's AST-1633 tests that assert "second save → new uuid" use a **different** body (`alpha` → `beta`); those must still pass. A new identical-body case will need qa-fix / board attention if TESTS: REVISE.
- API PUT success + hydrate still hold; editor reload AC unchanged.

### What must still hold

- Parent/AST-1633 AC4 when body **changes**: second save still new uuid + prior `current` retired (not in-place UPDATE).
- Parent AC5: successful Strengths save still goes through operative `save_artifact` when the body is new or changed — not library-merge alone.
- Parent AC6/AC7: no backfill; legacy blob on hydrate miss unchanged.
- Parent AC8 sibling freeze: no other context keys registered.
- Empty / non-str `plain_text` still raises `ValueError` before any current compare.
- First save (no current row) still inserts a new current version.

## Radia review (AST-1635)

[code-rubric]
**Ticket:** AST-1635
**Publish ref:** 8aa1291cca7944badd3cbf2953a83f194499a815
**Overall:** CLEAN
**Parent shape:** Normal (diff base `origin/ftr/AST-1629-migrate-strengths-artifact-table`)

### Canon scores
patt.artifact.write-operative | A | identical-body no-op gate + draft pattern update

### Fix-specific checks
- **[bug-repro]** OK — TestAst1635IdenticalArtifactNoOp asserts uid2==uid1 / single current / history==1
- **## What must still hold** — OK (seven items)

### discuss
- Issue description had no frozen Canon Scope table; scored from board + validate-plan fix-mode. Not a merge blocker.

### Recommended actions
PROCEED → Review Posted → User Testing (resolve-child skipped).
