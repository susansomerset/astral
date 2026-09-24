<!-- linear-archive: AST-1659 archived 2026-09-24 -->

## Linear archive (AST-1659)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1659/operative-save-hydrate-blob-retirement-migrate-candidate  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** hedy  
**Priority / estimate:** None / 3  
**Parent:** AST-1643 — Migrate candidate_data.context.ideal_day to use the artifact table  
**Blocked by / blocks / related:** parent: AST-1643; blocks: AST-1660

### Description

## What this implements

Wire Ideal Day through candidate operative `plain_text` validation plus `get_candidate_current` hydrate on GET; intercept API PUT for operative save; stop durable library SoT writes for `context.ideal_day`. No backfill helper. Does not own React chrome. After #1.

## Citations

`patt.artifact.write-operative`; `patt.artifact.read-current`; `patt.artifact.manage-catalog`; `astral.standards.in-scope-only`; `stat.logging.info.entity`; `stat.logging.info.api`; `stat.logging.error`

## Scope

`src/core/candidate.py` — operative validation for `plain_text`; hydrate overlay; gate library merge for `context.ideal_day`. `src/ui/api/api_candidate.py` — PUT intercept plus GET hydrate for Ideal Day.

## Acceptance criteria

- [X] 4\. **Operative round-trip** — Save Ideal Day via Ideal Day UI/API; `database.get_current_artifact('candidate', <id>, 'ideal_day')` returns matching string; second save new uuid + retire prior current.
- [X] 5\. **Blob not SoT on write** — Successful Ideal Day save calls operative `save_artifact`; does not rely on library-merge alone.
- [X] 6\. **No backfill required** — No bulk migrate-all; legacy blob until re-save.

## Boundaries

- [X] Does not own catalog/token flip (#1) or React chrome (#3).

## Notes for planning

Citations as above. After catalog sibling.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1643-migrate-ideal-day-artifact-table`, child `sub/AST-1643/<this-id>-operative-save-hydrate-blob-retirement`. Created at dispatch-parent.

### Comments

#### radia — 2026-09-16T00:15:30.495Z
[code-rubric] PROCEED (Commit: c5a6c1bf9a98a026ddedfb23aaa83960aeb7fb64) Ideal Day operative clean

#### betty — 2026-09-16T00:12:46.160Z
[check-linear]
Cleared [qa-handoff]: retargeted Ideal Day (and sibling Strengths/Bio Summary/Deal Breakers) library-sibling asserts from `priorities` → `backstory` after merge(dev) made priorities operative.
`origin/sub/AST-1643/AST-1659-operative-save-hydrate-blob-retirement` @ `c5a6c1bf` · reassigned Hedy for test-child

#### hedy — 2026-09-16T00:09:47.457Z
[qa-handoff]
@Betty White

Manifest (bible § AST-1659) red after sync merged `origin/dev` (priorities epic now on tip).

Command:
```bash
python3 -m pytest \
  tests/component/core/test_candidate.py::TestAst1659IdealDayOperativeSaveHydrate \
  tests/component/ui/api/test_api_candidate.py::TestAst1659IdealDayOperativeApi \
  -q --tb=short
```

Result: 2 failed / 12 passed.

Failures (test/manifest vs tip contract — not Ideal Day product bugs):

1. `TestAst1659IdealDayOperativeSaveHydrate::test_dict_path_strips_ideal_day_and_strengths_keeps_siblings`
   - Asserts `priorities` survives dict-path library merge as the non-operative sibling.
   - On tip after `merge(dev)`, `priorities` is in `_CONTEXT_OPERATIVE_LEAVES` / `ARTIFACT_CONFIG`, so the leaf is stripped and `save_candidate` is never called (`save.call_args` is None).

2. `TestAst1659IdealDayOperativeApi::test_put_strips_ideal_day_keeps_sibling_context`
   - Comment in test: "priorities stays library-merge on this tip (not catalogued)."
   - PUT `{ideal_day, priorities}` now pops both for operative save; library `context.priorities` is not written.

Product Ideal Day paths (round-trip, retire, hydrate miss/hit, empty 400) are green. Please retarget sibling leaf to a still-non-operative context key (e.g. `backstory`) or assert priorities operative too.

Publish tip after merge: `origin/sub/AST-1643/AST-1659-operative-save-hydrate-blob-retirement` @ `5237c122`

#### betty — 2026-09-16T00:06:48.876Z
`origin/sub/AST-1643/AST-1659-operative-save-hydrate-blob-retirement` @ `f68f37c6` · Ideal Day operative tests

#### joan — 2026-09-15T23:58:02.031Z
[plan-rubric] PROCEED (Commit: d5f9e7ae) operative hydrate wired

#### hedy — 2026-09-15T23:56:03.950Z
`origin/sub/AST-1643/AST-1659-operative-save-hydrate-blob-retirement` @ `d5f9e7ae` · Ideal Day operative plan

---

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

## Review (build stub)

**Built:** `origin/sub/AST-1643/AST-1659-operative-save-hydrate-blob-retirement` @ `d5dfc8c274727f0306e3efe1fbd61f38f7ae4c53`.

**Stages delivered:**
- Stage 1: library gate + hydrate + entity log — `5e05726a44723116c6be044633971c285335dd3a`.
- Stage 2: PUT intercept + GET hydrate + api info — `d5dfc8c274727f0306e3efe1fbd61f38f7ae4c53`.

**Betty:** at **Code Complete** — cover operative Ideal Day round-trip + retire prior current, identical-body no-op (shared AST-1635), dict-path strips `context.ideal_day` (and still strips strengths / bio_summary / deal_breakers), hydrate overlays current / leaves legacy on miss, PUT pop+operative path, GET hydrate leaf, empty ideal_day → 400.

## Joan validate

[plan-rubric]
**Ticket:** AST-1659
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref tip:** `d5f9e7aee248854e92ce1fc55386a9612dc4e475` (`origin/sub/AST-1643/AST-1659-operative-save-hydrate-blob-retirement`)

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

AC4→Stage 1 §§4–6 + Stage 2 §§3–4 + verify; AC5→Stage 1 §5 + Stage 2 §§3–4; AC6→Stage 1 §6 miss path; parent AC7 (no backfill)→Stage 1 §6; parent AC8→scope gate (no `ARTIFACT_CONFIG` edits); parent AC6 (editor reload)→N/A — AST-1660 UI sibling.

## Findings

None (`fix-now` / `discuss`).

**R6 notes (acceptable):** Plan extends proven Strengths/bio_summary mechanics (`_CONTEXT_OPERATIVE_LEAVES`, hydrate-on-miss preserves legacy blob, PUT pop→operative save, entity+api info, existing `logger.exception`) for `ideal_day` only; explicit scope gate limits to `candidate.py` + `api_candidate.py`; catalog prerequisite on AST-1658 documented with build-block stop; migration-window hydrate matches parent AC6/AC7 and `read-current` migration exception; no second validate path or config registration in this slice.

context_tokens≈48000

## Radia review

[code-rubric]
**Ticket:** AST-1659
**Publish ref:** c5a6c1bf9a98a026ddedfb23aaa83960aeb7fb64
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

### fix-now

(none)

### discuss

(none)

### advisory

- **Location:** Three-dot diff vs `origin/dev` — `src/utils/config.py`, `docs/features/foundation/ast-1658-catalog-plain-text-ideal-day-token.md`
- **Finding:** Diff includes AST-1658 catalog + token registration (sibling Ada) because the branch stacks `merge(ftr)` / `merge(dev)` ahead of land. AST-1659 `code()` commits touch only `src/core/candidate.py` and `src/ui/api/api_candidate.py`.
- **Recommendation:** No AST-1659 product fix; Chuckles/merge-child ordering only. Prerequisite `candidate.context.ideal_day ∈ ARTIFACT_CONFIG` is satisfied on tip.

- **Location:** `src/core/candidate.py` — `_CONTEXT_OPERATIVE_LEAVES`
- **Finding:** Plan text froze `{strengths, bio_summary, ideal_day}`; publish tip after `merge(dev)` union is `{strengths, bio_summary, priorities, deal_breakers, ideal_day}`. Ideal Day addition is correct; extra leaves are dev union, not a second strip site.
- **Recommendation:** Betty already retargeted sibling asserts to `backstory` as library-merge peer; no AST-1659 change needed.

- **Location:** `src/ui/api/api_candidate.py` — success-path api info
- **Finding:** `ideal_day_saved` emits its own `stat.logging.info.api` line per plan; strengths/priorities/deal_breakers/bio_summary share one combined block from merged dev tip. A PUT saving multiple operative leaves may emit multiple lines — plan-acceptable.
- **Recommendation:** None on this ticket.

- **Location:** `docs/test-bible/core/candidate.md` / `api_candidate.md` § AST-1659 bible shasum
- **Finding:** Shasum lines still `*(filled after publish)*`.
- **Recommendation:** Chuckles sync on writeback — not a code gate.

- **Location:** Canon clerk / frozen list resolution
- **Finding:** `patt.artifact.*` draft patterns and `astral.standards.in-scope-only` scored from repo files at epic worktree; `canon_clerk expand` does not serve those ids.
- **Recommendation:** Corpus hygiene downstream; no scope gap on frozen list.

## Notes

- **Scope divergence (expected):** Product authorship is two files (`5e05726a` Stage 1 core, `d5dfc8c2` Stage 2 API). `tests/`, `docs/test-bible/**`, and stacked sibling `config.py` appear in the three-dot diff vs `origin/dev` — Betty `merge-tests` + epic union merges, not AST-1659 scope creep in `code()` commits.
- **Estimate footprint:** Confirm **3** points still fits (core hydrate/gate + API intercept + manifest tests).

## What's solid

- Stage 1: `_IDEAL_DAY_ARTIFACT_KEY`, `_CONTEXT_OPERATIVE_LEAVES` widened with `ideal_day`, `hydrate_operative_ideal_day_for_response` (miss preserves legacy blob), `get_candidate` hydrate call, entity info on operative save — mirrors bio_summary pattern.
- Stage 2: PUT pop `context.ideal_day` → str-path `save_candidate_data(..., "candidate.context.ideal_day", body)`; GET detail hydrate; `ideal_day_saved` api info; existing `logger.exception` handler unchanged for ValueError → 400.
- `TestAst1659IdealDayOperativeSaveHydrate` + `TestAst1659IdealDayOperativeApi` cover round-trip, retire+insert, AST-1635 identical no-op, dict-path strip, hydrate hit/miss, empty → 400; AST-1365 library-merge test revised to strip semantics.
- Blob retirement on write: operative leaves stripped from dict-path library merge; API intercept prevents durable `context.ideal_day` SoT.

## Recommended actions

(none downstream — artifact complete)

context_tokens≈42000
