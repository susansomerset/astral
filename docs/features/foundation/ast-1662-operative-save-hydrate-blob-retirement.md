# Operative save, hydrate, blob retirement

**Linear:** [AST-1662](https://linear.app/astralcareermatch/issue/AST-1662)
**Parent:** [AST-1644](https://linear.app/astralcareermatch/issue/AST-1644) — Migrate candidate_data.context.backstory to use the artifact table
**Publish ref:** `sub/AST-1644/AST-1662-operative-save-hydrate-blob-retirement`

Wire Backstory through the same candidate operative `plain_text` validation + hydrate-on-GET and API PUT intercept Strengths / bio summary / Ideal Day already use; stop durable library SoT writes for `context.backstory`. No backfill helper. No React chrome or catalog/token (siblings Ada / Katherine). Depends on catalog sibling [AST-1661](https://linear.app/astralcareermatch/issue/AST-1661) — `candidate.context.backstory` must be in `ARTIFACT_CONFIG` before Stage 1 verify (sibling tip: `origin/sub/AST-1644/AST-1661-catalog-plus-backstory-token`; parent ftr tip: `origin/ftr/AST-1644-migrate-backstory-artifact-table`). Mirror AST-1633 / AST-1659 for the Strengths→Backstory leaf swap.

## UAT fitness

- **AC restored:** Parent AC4 — Save Backstory via Backstory UI/API; `database.get_current_artifact('candidate', <id>, 'backstory')` returns a row whose `artifact_data` matches the saved string; a second save creates a new uuid and retires prior `current=1`. Parent AC5 — Successful Backstory save calls operative `save_artifact`; does not rely on library-merge of `context.backstory` alone. Parent AC6 / ticket AC6 — Candidates with only legacy blob Backstory and no artifact row still load that blob (or empty) until re-save; no bulk migration job ships.
- **Correct outcome:** After Backstory save, the editor contract leaf `candidate_data.context.backstory` reflects the current artifact string on GET; the durable SoT is the artifacts row (retire+insert on change; identical-body no-op per AST-1635), not the library blob.
- **Sibling check:** Catalog + `BACKSTORY` token typing stay on AST-1661 (config only). React / ContextTextPage wire-up stays on AST-1663. Strengths / priorities / deal_breakers / bio_summary / ideal_day operative paths remain unchanged except Backstory is added to the shared `_CONTEXT_OPERATIVE_LEAVES` strip set. This ticket does not touch `ARTIFACT_CONFIG`.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Library-merge-only PUT for Backstory (AC5 fail); inventing a second Backstory-only validate path instead of riding existing `plain_text` + AST-1635 identical no-op; clearing legacy blob on hydrate miss (breaks no-backfill window); registering Backstory in config here (Ada’s ticket).

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/core/candidate.py` — operative validation for `plain_text`; hydrate overlay; gate library merge for `context.backstory`.
- `src/ui/api/api_candidate.py` — PUT intercept plus GET hydrate for Backstory.

Every Files Changed row and every Stage step stays inside those two files. No `config.py`, no React, no `database.py`, no other context keys, no pin/read-operative Backstory surface, no bulk migrate.

**Already on tip (do not re-invent):**

- `plain_text` body validation in `save_candidate_data` str-path (AST-1633).
- Identical-to-current no-op before `save_artifact` (AST-1635) — applies to all catalog str-path keys including Backstory once called.
- Strengths / priorities / deal_breakers / bio_summary / ideal_day library gate / hydrate / PUT intercept / entity+api info / PUT `logger.exception` with type+message (AST-1633 / AST-1649 / AST-1652 / AST-1655 / AST-1659 + Joan fix).

This ticket **extends** those paths for `backstory` / `candidate.context.backstory` only.

**Catalog prerequisite:** Before Stage 1 hand-verify, `from src.utils.config import ARTIFACT_CONFIG; assert "candidate.context.backstory" in ARTIFACT_CONFIG` must exit 0. If missing at **build-child** start — stop, comment on parent AST-1644 with Stage blocked (catalog sibling not on tip); do **not** register the key in this ticket. Prefer `sync-child.sh … --ftr AST-1644-migrate-backstory-artifact-table` (registry `parent_ftr`; not the short segment `AST-1644`) so `origin/ftr/AST-1644-migrate-backstory-artifact-table` lands — do not cherry-pick.

⚠️ **Decision / known sync conflict:** At plan time, `origin/dev` already carries Ideal Day catalog (`candidate.context.ideal_day`) while parent ftr carries Backstory (`candidate.context.backstory`) from AST-1661. Merging that ftr onto a tip that already includes `origin/dev` conflicts in `src/utils/config.py` plus Betty's `tests/component/utils/test_config.py` / `docs/test-bible/utils/config.md` (and related candidate API tests). Resolution is **union both leaves** (keep Ideal Day + add Backstory) — not “take ours” or “take theirs”. Product `config.py` union is in engineer scope for the sync merge commit; if the pre-commit test-tree ban blocks resolving Betty files, stop and `@susan` / Chuckles — do not invent new tests.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/candidate.py` | Module constant + docstring; extend `_CONTEXT_OPERATIVE_LEAVES` with `backstory`; `hydrate_operative_backstory_for_response` + call from `get_candidate`; entity info on Backstory operative save | core |
| `src/ui/api/api_candidate.py` | PUT `/data`: pop `context.backstory`, library-merge remainder, then operative save; GET detail hydrate Backstory; api info when Backstory PUT completes | ui |

**Out of this ticket (do not touch):** `src/utils/config.py` (sibling Ada / AST-1661); `CandidateBackstory.tsx` / `ContextTextPage.tsx` (sibling Katherine AST-1663 — existing PUT `{ context: { backstory } }` keeps working via intercept once page lands); `ArtifactEditor`; `database.py`; other context leaves; `tests/` / `docs/test-bible/**`.

## Stage 1: Core — library gate, hydrate, entity log

**Done when:** `save_candidate_data(cid, "candidate.context.backstory", "hello")` inserts a current artifact row whose `artifact_data` is `"hello"` (existing `plain_text` validate + AST-1635 identical no-op unchanged); a second save with a different string returns a new uuid and prior row is not current; identical re-save returns the same uuid with no new row; `get_candidate` overlays current Backstory onto `candidate_data.context.backstory` when a row exists and leaves the legacy blob alone on miss; dict-path `save_candidate_data(cid, {"context": {"backstory": "x", "writing_preferences": "y"}})` does not persist `backstory` into the library blob (`writing_preferences` still merges when present; `strengths` / `bio_summary` / `ideal_day` / etc. still stripped as today).

1. In `src/core/candidate.py` module docstring **In-scope** / operative bullets, add one line that Backstory uses the same operative save + `get_candidate_current` hydrate path with catalog key `candidate.context.backstory` (cite AST-1662). Keep the existing Strengths / priorities / deal_breakers / bio summary / Ideal Day / base_resume lines.

2. Immediately after `_IDEAL_DAY_ARTIFACT_KEY = "candidate.context.ideal_day"`, add:

```python
_BACKSTORY_ARTIFACT_KEY = "candidate.context.backstory"
```

Widen the existing closed frozenset (do **not** invent a second strip site):

```python
# Catalog-owned context leaves — never durable library-merge SoT (AST-1633 / AST-1649 / AST-1652 / AST-1655 / AST-1659 / AST-1662).
_CONTEXT_OPERATIVE_LEAVES = frozenset(
    {"strengths", "bio_summary", "priorities", "deal_breakers", "ideal_day", "backstory"}
)
```

⚠️ **Decision:** Same frozenset pattern as AST-1649 / AST-1659 — one strip site for all operative context leaves. Do not hardcode `backstory` in a second independent `if`.

3. **Do not** change the existing `plain_text` validation branch or the AST-1635 identical-to-current gate. Backstory rides those paths via catalog `body_shape: "plain_text"`.

4. In the str-path, after a successful `database.save_artifact(...)` (assign-then-return already present), extend the entity info emission so Backstory also logs (`stat.logging.info.entity`). Keep existing leaf branches:

```python
        elif artifact_key == _BACKSTORY_ARTIFACT_KEY:
            logger.info(
                "%s | candidate %s: %s (batch: %s)",
                candidate_id,
                "backstory artifact saved",
                new_uuid,
                "-",
            )
```

Place this as a new branch after the existing `_IDEAL_DAY_ARTIFACT_KEY` `elif` (same `if` / `elif` chain). Do **not** emit entity info on the identical-body no-op return. Do **not** add entity info for `base_resume` or other keys.

5. **Do not** rewrite the dict-path strip block — widening `_CONTEXT_OPERATIVE_LEAVES` in step 2 is sufficient. Confirm the existing loop still uses `k not in _CONTEXT_OPERATIVE_LEAVES`.

6. Add `hydrate_operative_backstory_for_response(candidate_id: str, cd: dict) -> None` immediately after `hydrate_operative_ideal_day_for_response`:

```python
def hydrate_operative_backstory_for_response(candidate_id: str, cd: dict) -> None:
    """Overlay operative current Backstory into candidate_data.context (display only).

    Miss → leave legacy context.backstory blob untouched (parent AC6 / ticket AC6 migration window).
    Hit → write current string onto context.backstory for the editor contract.
    """
    if not isinstance(cd, dict):
        return
    body = get_candidate_current(candidate_id, _BACKSTORY_ARTIFACT_KEY)
    if body is None:
        return
    if not isinstance(body, str):
        return
    ctx = cd.get("context")
    if not isinstance(ctx, dict):
        ctx = {}
        cd["context"] = ctx
    ctx["backstory"] = body
```

⚠️ **Decision:** On miss, **do not** pop/clear `context.backstory` (same migration-window choice as Strengths / Ideal Day; unlike base_resume hydrate, which strips blob on miss). Parent AC6 / ticket AC6: legacy blob until re-save; no coat-check.

7. In `get_candidate`, immediately after the existing `hydrate_operative_ideal_day_for_response(candidate_id, cd)` call, add:

```python
    hydrate_operative_backstory_for_response(candidate_id, cd)
```

**Verify (hand):** with a candidate that has no backstory artifact, hydrate leaves legacy blob alone. After Stage 2, full round-trip.

## Stage 2: API — PUT intercept + GET hydrate + logging

**Done when:** `PUT /api/candidates/<id>/data` with body `{"context": {"backstory": "alpha"}}` creates/rotates a current `backstory` artifact row; library `candidate_data.context.backstory` is not the SoT for that write; `GET /api/candidates/<id>` returns `candidate_data.context.backstory` equal to the current artifact string when a row exists; sibling context keys (e.g. `writing_preferences`) in the same PUT still library-merge; Strengths / Ideal Day / other operative PUT paths unchanged; no React files changed.

1. In `src/ui/api/api_candidate.py`, in the `from src.core.candidate import (` block, add `hydrate_operative_backstory_for_response` next to the existing Ideal Day / Strengths hydrate imports. Logger / `get_logger` already present — do not re-add.

2. In `get_candidate_detail`, immediately after the existing `hydrate_operative_ideal_day_for_response(candidate_id, cd)` call, add:

```python
    hydrate_operative_backstory_for_response(candidate_id, cd)
```

(Idempotent with `get_candidate`'s hydrate — same double-call pattern as Strengths / Ideal Day / base_resume.)

3. In `update_candidate_data`, extend the context pop at the start of `if body:` to also pop Backstory. Initialize `backstory_saved = False` next to the existing `ideal_day_saved` (outside the try, same scope).

```python
            strengths_body = None
            priorities_body = None
            deal_breakers_body = None
            bio_summary_body = None
            ideal_day_body = None
            backstory_body = None
            ctx = body.get("context")
            if isinstance(ctx, dict):
                if "strengths" in ctx:
                    strengths_body = ctx.pop("strengths")
                if "priorities" in ctx:
                    priorities_body = ctx.pop("priorities")
                if "deal_breakers" in ctx:
                    deal_breakers_body = ctx.pop("deal_breakers")
                if "bio_summary" in ctx:
                    bio_summary_body = ctx.pop("bio_summary")
                if "ideal_day" in ctx:
                    ideal_day_body = ctx.pop("ideal_day")
                if "backstory" in ctx:
                    backstory_body = ctx.pop("backstory")
                if not ctx:
                    body.pop("context", None)
```

Keep `backstory_body` even when it is `""` so operative validation can raise — do not special-case empty here.

⚠️ **Decision:** One empty-`context` cleanup after all pops. Same `ctx` reference; existing leaf order preserved for minimal diff vs AST-1659; Backstory last among operative context pops.

4. After the existing Ideal Day operative-save block (`if ideal_day_body is not None: ...`), add the Backstory twin:

```python
            if backstory_body is not None:
                save_candidate_data(
                    candidate_id,
                    "candidate.context.backstory",
                    backstory_body,
                )
                backstory_saved = True
```

Place this so it still runs when the PUT is Backstory-only (body emptied after pop) — same “leaf-only PUT leaves body empty” pattern already in the handler.

⚠️ **Decision:** Catalog key string literal at the API call site matches Strengths / Ideal Day (`"candidate.context.backstory"`). Do not import `_BACKSTORY_ARTIFACT_KEY` from candidate (leading-underscore private).

5. On the success path of `update_candidate_data` (after the try succeeds, near the existing `if ideal_day_saved:` api info), if `backstory_saved`, emit one api info line (`stat.logging.info.api`):

```python
    if backstory_saved:
        logger.info(
            "%s | api %s completed: PUT %s",
            candidate_id,
            f"/api/candidates/{candidate_id}/data",
            200,
        )
```

Keep the existing combined `if strengths_saved or …` and `if ideal_day_saved:` blocks unchanged. A PUT that saves multiple operative leaves may emit multiple api info lines — acceptable (one progress line per leaf group that completed).

6. **Do not** rewrite the existing `except Exception as e:` `logger.exception(...)` block — it already includes `type(e).__name__`, `e`, and “returning 400” (`stat.logging.error`). Backstory ValueErrors ride the same handler.

7. Do **not** edit React. When Katherine’s Backstory page lands (AST-1663), `ContextTextPage` PUT `{ context: { backstory: draft } }` lands operative rows via this intercept; GET hydrate feeds `candidate_data.context.backstory`.

**Verify (hand):**

```bash
# After save via PUT (use a real candidate_id):
python3 -c "
from src.data import database
row = database.get_current_artifact('candidate', '<id>', 'backstory')
assert row and row['artifact_data'] == '<saved string>'
"
# Second distinct save → new artifact_uuid; prior current=0
# Identical re-save → same uuid (AST-1635 no-op)
```

## Execution contract

- Execute steps in order within a stage; stages in order; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files, touch Ada/Katherine scopes, register other context keys, or add a backfill/migrate script.
- On ambiguity or drift — stop, comment on parent AST-1644 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `patt.artifact.write-operative` | pattern — read in full; Backstory via `save_candidate_data` str-path → `save_artifact` (identical no-op already shared) |
| `patt.artifact.read-current` | pattern — read in full; hydrate via `get_candidate_current` |
| `patt.artifact.manage-catalog` | pattern — read in full; retire blob authority for registered Backstory key only (catalog entry from AST-1661) |
| `astral.standards.in-scope-only` | statute — Backstory only; two named files |
| `stat.logging.info.entity` | statute — entity info on Backstory operative save |
| `stat.logging.info.api` | statute — api info when Backstory PUT completes |
| `stat.logging.error` | statute — exception once at PUT handler (already present; do not regress) |

## Traceability

- Parent/child AC4 (operative round-trip) → Stage 1 §§4–6 + Stage 2 §§3–4 + verify
- Parent/child AC5 (blob not SoT on write) → Stage 1 §5 + Stage 2 §§3–4
- Parent/child AC6 / parent AC6–7 (no backfill; legacy until re-save) → Stage 1 §6 miss path
- Sibling freeze (parent AC8 — no new non-Backstory keys from this epic) → scope gate; no `ARTIFACT_CONFIG` edits
- Editor reload (parent AC6, Katherine AST-1663) → Stage 1 §§6–7 + Stage 2 §2 (UI sibling unchanged)

## Joan validate

```
[plan-rubric]
**Ticket:** AST-1662
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `ff23384079fb204a3501a8dfa57d6710755c1565` (`origin/sub/AST-1644/AST-1662-operative-save-hydrate-blob-retirement`)

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

AC4→Stage 1 (§§4–6) + Stage 2 (§§3–4) + verify; AC5→Stage 1 §5 + Stage 2 §§3–4 (pop + operative save, no library SoT); AC6→Stage 1 §6 miss path (legacy blob untouched); parent AC6 editor reload→Stage 1 §§6–7 + Stage 2 §2 (hydrate only — Katherine AST-1663 owns UI); parent AC1–AC3, AC8–AC9→N/A (AST-1661 / AST-1663 siblings).

## Findings

### acceptable — prerequisite / merge hygiene

- **Location:** Explicit scope gate — catalog prerequisite + ftr/dev sync conflict
- **Finding:** Plan correctly blocks build without AST-1661 catalog on tip and documents Ideal Day (dev) + Backstory (ftr) `config.py` union on sync — not feature scope creep, but engineers must resolve merge conflicts without registering keys here.
- **Recommendation:** Follow plan's `sync-child.sh` + union decision at build-child; stop per Stage blocked template if Betty test-tree files block pre-commit.

### acceptable — migration-window hydrate

- **Location:** Stage 1 §6 Decision
- **Finding:** Miss path leaves legacy `context.backstory` blob in place — same Strengths / Ideal Day precedent; satisfies child AC6 (no backfill) without coat-check fetch.
- **Recommendation:** None.

context_tokens≈38000
```

## Review (build stub)

**Built:** `origin/sub/AST-1644/AST-1662-operative-save-hydrate-blob-retirement` @ `bd8d2d5a0cfcc005b851f8509f90e0e129984d8f`.

**Stages delivered:**
- Stage 1: library gate + hydrate + entity log — `b3576294e1848cdbb49364b9788d082c89ff288f`.
- Stage 2: PUT intercept + GET hydrate + api info — `bd8d2d5a0cfcc005b851f8509f90e0e129984d8f`.


**Scope fix:** stripped Writing Preferences operative path from this publish-ref (Betty gate) — `writing_preferences` library-merges again; Backstory-only remains.
**Betty:** at **Code Complete** — cover operative Backstory round-trip + retire prior current, identical-body no-op (shared AST-1635), dict-path strips `context.backstory` (and still strips strengths / bio_summary / ideal_day / writing_preferences), hydrate overlays current / leaves legacy on miss, PUT pop+operative path, GET hydrate leaf, empty backstory → 400.

## Radia review

```
[code-rubric]
**Ticket:** AST-1662
**Publish ref:** `b59121e46e9aeed8f69560e4b7033dd67b9be5cb` (`origin/sub/AST-1644/AST-1662-operative-save-hydrate-blob-retirement`)
**Corpus:** `fc0c368e5927a57f1561c057ce9a0ff4abe1fb13`
**Overall:** FIX-NOW

## Canon scores

| Id | Grade | Effort | One-line |
|----|-------|--------|----------|
| patt.artifact.write-operative | A | | |
| patt.artifact.read-current | A | | |
| patt.artifact.manage-catalog | A | | |
| astral.standards.in-scope-only | D | 2 | `5b2facb4` strips AST-1665 writing_preferences operative paths |
| stat.logging.info.entity | A | | |
| stat.logging.info.api | A | | |
| stat.logging.error | A | | |

## Column diff vs plan stage

| Id | Joan | Radia | Note |
|----|------|-------|------|
| astral.standards.in-scope-only | A | D | Plan scoped Backstory-only two files; commit `5b2facb4` deletes Writing Preferences operative/hydrate/PUT intercept |

## Frame diff

- [ ] `ftr`→`dev` union keeps **all three** context catalog keys landed on dev: `candidate.context.ideal_day`, `candidate.context.backstory`, `candidate.context.writing_preferences` — plan union was Ideal Day + Backstory, not Backstory replacing Writing Preferences
- [ ] AST-1665 operative paths (`_CONTEXT_OPERATIVE_LEAVES`, hydrate, PUT intercept) restored on dev merge after backstory lands — or explicit parent-epic ordering documents intentional temporary regression on sub tip only

## Findings

### fix-now

- **Location:** `src/utils/config.py` (tip vs `origin/dev`); `TOKEN_SOURCES["WRITING_PREFERENCES"]`; `ARTIFACT_CONFIG` closed set
- **Finding:** Three-dot diff vs dev **removes** `candidate.context.writing_preferences` from `ARTIFACT_CONFIG`, drops per-entry `_wp` asserts, and demotes `WRITING_PREFERENCES` from `artifact` → `data_field`. `origin/dev` already ships AST-1664 catalog + AST-1665 operative paths for Writing Preferences. Tip unions backstory + ideal_day only — merge to dev would regress a landed parallel epic.
- **Recommendation:** At `merge-child` / ftr→dev, union catalog + token typing for backstory **and** writing_preferences (and ideal_day); do not ship this config resolution as-is onto dev.

- **Location:** `src/core/candidate.py`, `src/ui/api/api_candidate.py` — commit `5b2facb4`
- **Finding:** Engineer commit explicitly strips Writing Preferences operative save, hydrate, PUT pop/intercept, and entity log — outside ticket scope gate (Backstory-only; plan: other operative paths unchanged). Build stub documents Betty gate cleanup after ftr/dev merge picked up AST-1665 paths prematurely.
- **Recommendation:** Acceptable **on isolated sub tip** only if merge restores AST-1665 paths on dev; otherwise revert strip and resolve slot collision via proper ftr union ordering, not deletion of sibling operative code.

### discuss

- **Location:** Three-dot diff stat (9 files, ~1395 lines) vs explicit scope gate (two product files)
- **Finding:** Wider diff carries expected epic stacking: AST-1661 catalog prerequisite (`7e34dc65`, ftr sync `824ec0ea`), Betty `merge-tests`, parallel-epic bible blocks (AST-1665 skipif, AST-1661 config). Engineer Stage 1–2 product commits (`b3576294`, `bd8d2d5a`) touch only `candidate.py` + `api_candidate.py` as planned.
- **Recommendation:** Chuckles notes at merge-child; not engineer replan.

- **Location:** `docs/features/foundation/ast-1662-operative-save-hydrate-blob-retirement.md` build stub — "Scope fix: stripped Writing Preferences operative"
- **Finding:** Documented intentional tip cleanup mirrors AST-1665's parallel-epic strip pattern; rationale is sound for **sub-branch isolation** but conflicts with dev-ready merge hygiene above.
- **Recommendation:** Frame-diff rows above before UT on parent ftr.

### advisory

- **Location:** `canon/canon_clerk.py expand` for `patt.artifact.*` draft ids
- **Finding:** Same draft-vs-active roster gap as AST-1661; scored from `canon/directives/draft/` bodies @ `fc0c368e`.
- **Recommendation:** Corpus hygiene — no block on backstory slice scoring.

- **Location:** `TestAst1665*` skipif (`writing_preferences` not in `ARTIFACT_CONFIG`)
- **Finding:** Parallel-epic test pattern correct — suites skip on this tip, run when catalog present.
- **Recommendation:** None.

## What's solid

- Backstory operative slice matches plan Stages 1–2: `_BACKSTORY_ARTIFACT_KEY`, `_CONTEXT_OPERATIVE_LEAVES` widened with `backstory`, `hydrate_operative_backstory_for_response` (miss preserves legacy blob), `get_candidate` + `get_candidate_detail` hydrate calls, PUT pop → `save_candidate_data("candidate.context.backstory", …)`, `backstory_saved` api info line.
- Entity/api logging follows existing Strengths/Ideal Day pipe templates (`stat.logging.info.entity` / `stat.logging.info.api`); `logger.exception` PUT handler unchanged (`stat.logging.error`).
- `TestAst1662BackstoryOperativeSaveHydrate` / `TestAst1662BackstoryOperativeApi` cover plain_text reject, retire+insert, AST-1635 identical no-op, dict-path strip with `writing_preferences` library sibling, hydrate hit/miss, empty → 400 — aligned with `docs/test-bible/core/candidate.md` and `docs/test-bible/ui/api/api_candidate.md` § AST-1662.
- `plain_text` validate + AST-1635 identical no-op reused via catalog str-path — no second validate path invented.

## Recommended actions (downstream — not executed here)

1. `resolve-child` / Chuckles: document dev-merge union requirement (backstory + ideal_day + writing_preferences) before parent UT; restore AST-1665 operative if this ref merges toward dev.
2. Re-run AST-1662 manifest after merge resolution.
3. Optional: parent AST-1644 comment on parallel-epic slot collision policy if strips become routine.
```
