<!-- linear-archive: AST-1658 archived 2026-09-24 -->

## Linear archive (AST-1658)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1658/catalog-plain-text-shape-reuse-ideal-day-token-migrate-candidate  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / 1  
**Parent:** AST-1643 — Migrate candidate_data.context.ideal_day to use the artifact table  
**Blocked by / blocks / related:** parent: AST-1643; blocks: AST-1659

### Description

## What this implements

Register `candidate.context.ideal_day` in `ARTIFACT_CONFIG` reusing the existing `plain_text` shape, flip `TOKEN_SOURCES["IDEAL_DAY"]` to artifact plus `artifact_key`, lock startup asserts (add key to closed set; remove from sibling-freeze-out list). Does not own UI or hydrate.

## Citations

`patt.artifact.manage-catalog`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `stat.logging.info` / `stat.logging.debug` as touched

## Scope

`src/utils/config.py` — new catalog entry plus asserts; `TOKEN_SOURCES["IDEAL_DAY"]` flip.

## Acceptance criteria

- [X] **Catalog key present** — `python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'candidate.context.ideal_day' in ARTIFACT_CONFIG"` exits 0.
- [X] **plain_text shape reused** — `python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert ARTIFACT_CONFIG['candidate.context.ideal_day']['body_shape']=='plain_text'"` exits 0.
- [X] **Token is artifact-typed** — `python3 -c "from src.utils.config import TOKEN_SOURCES; s=TOKEN_SOURCES['IDEAL_DAY']; assert s['source_type']=='artifact' and s['artifact_key']=='candidate.context.ideal_day'"` exits 0.
- [X] **Sibling freeze** — `ARTIFACT_CONFIG` has no priorities/deal_breakers/backstory/writing_preferences keys.

## Boundaries

- [X] Does not own UI, hydrate, API PUT intercept, or blob retirement (siblings). Does not migrate other context keys.

## Notes for planning

Citations as above. Reuses AST-1629 `plain_text` shape — no new shape entry.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1643-migrate-ideal-day-artifact-table`, child `sub/AST-1643/<this-id>-catalog-plain-text-ideal-day-token`. Created at dispatch-parent.

### Comments

#### radia — 2026-09-15T23:52:19.795Z
[code-rubric] PROCEED (Commit: c5af9cdc1f30718067f897182d655c6aebe78117) Ideal Day catalog clean

#### betty — 2026-09-15T23:48:50.845Z
`origin/sub/AST-1643/AST-1658-catalog-plain-text-ideal-day-token` @ `c5af9cdc` · Ideal Day catalog tests

#### joan — 2026-09-15T23:39:57.908Z
[plan-rubric] PROCEED (Commit: 4083cd81) Ideal Day catalog flip

#### ada — 2026-09-15T23:37:20.705Z
`origin/sub/AST-1643/AST-1658-catalog-plain-text-ideal-day-token` @ `4083cd8134bef9aa12911e9a368ab7ea0fd65af3` · plan published

---

# Catalog + plain_text shape reuse + IDEAL_DAY token

**Linear:** [AST-1658](https://linear.app/astralcareermatch/issue/AST-1658)
**Parent:** [AST-1643](https://linear.app/astralcareermatch/issue/AST-1643) — Migrate candidate_data.context.ideal_day to use the artifact table
**Publish ref:** `sub/AST-1643/AST-1658-catalog-plain-text-ideal-day-token`

Register `candidate.context.ideal_day` in `ARTIFACT_CONFIG` reusing the existing `plain_text` body shape from AST-1632, flip `TOKEN_SOURCES["IDEAL_DAY"]` to `source_type: "artifact"` with `artifact_key: "candidate.context.ideal_day"`, and lock startup asserts (add key to closed set; remove it from the context sibling-freeze-out list). Config-only — no UI, hydrate, API intercept, or blob retirement (siblings AST-1659 / AST-1660).

## UAT fitness

- **AC restored:** Parent AC1 — `candidate.context.ideal_day` present in `ARTIFACT_CONFIG`. Parent AC2 — entry `body_shape == "plain_text"` and `plain_text` already in `BUILD_CONFIG["artifact_shapes"]`. Parent AC3 — `TOKEN_SOURCES["IDEAL_DAY"]` is `source_type: "artifact"` with `artifact_key: "candidate.context.ideal_day"`. Parent AC8 — `ARTIFACT_CONFIG` has no priorities / deal_breakers / backstory / writing_preferences keys.
- **Correct outcome:** Ideal Day is a registered catalog key on the proven `plain_text` path; `{$IDEAL_DAY}` is typed as an artifact token bound to that key. Sibling context leaves stay unregistered.
- **Sibling check:** `candidate.context.strengths` and `candidate.context.bio_summary` remain registered (AST-1632 / AST-1648). Freeze loop still asserts absence of priorities / deal_breakers / backstory / writing_preferences. No new `artifact_shapes` entry. Operative save / hydrate / UI stay on AST-1659 / AST-1660.
- **Not sufficient:** Removing a stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Inventing a second Ideal-Day-only shape, flipping Ideal Day without catalog registration (token assert would fail), or registering sibling context keys in this pass — all violate manage-catalog + parent AC8 / this ticket Boundaries.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/utils/config.py` — new catalog entry plus asserts; `TOKEN_SOURCES["IDEAL_DAY"]` flip.

Every Files Changed row and every Stage step stays inside that one file. No `candidate.py`, no `api_candidate.py`, no React, no `database.py`, no other context keys, no new `artifact_shapes` entry (reuse AST-1632 `plain_text`), no `DATA_SHAPES` / `NAV_CONFIG` edits (Ideal Day already has a Candidate nav leaf and page — AST-1660 owns wire-up only), no resolve_tokens behavior change beyond what the typed registry already drives at import.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Register `candidate.context.ideal_day` in `ARTIFACT_CONFIG` + closed-set / per-entry asserts; remove Ideal Day from context sibling-freeze-out list; flip `TOKEN_SOURCES["IDEAL_DAY"]` to artifact + `artifact_key`; widen `_artifact_tokens`; update module docstring inventory | utils |

**Out of this ticket (do not touch):** operative `plain_text` validation / hydrate / library gate (sibling #2); API PUT intercept + GET hydrate (sibling #2); `CandidateIdealDay.tsx` / ContextTextPage wire-up (sibling #3); `ArtifactEditor.tsx`; `database.py`; other context leaves; `DATA_SHAPES` / `NAV_CONFIG`; `tests/` / `docs/test-bible/**`.

## Stage 1: Ideal Day catalog + IDEAL_DAY token

**Done when:** `import src.utils.config` succeeds; ticket AC1–AC4 one-liners exit 0; sibling context keys (priorities / deal_breakers / backstory / writing_preferences) remain absent from `ARTIFACT_CONFIG`; `_artifact_tokens == {"BASE_RESUME", "STRENGTHS", "BIO_SUMMARY", "IDEAL_DAY"}`.

1. In `src/utils/config.py` module docstring **Config sections:** list, update the existing `ARTIFACT_CONFIG` inventory line to include the Ideal Day key (keep SoT wording; cite AST-1658 alongside AST-1632 / AST-1648):

```
  ARTIFACT_CONFIG — versioned artifact registry keyed by entity._data path (entity, candidate_scoped, body_shape, ingestion_owner); keys = candidate.artifacts.base_resume, job.artifacts.job_resume, job.artifacts.cover_letter, candidate.context.strengths, candidate.context.bio_summary, candidate.context.ideal_day; SoT in config — callers import ARTIFACT_CONFIG (AST-1573 / AST-1575 / AST-1576 / AST-1590 / AST-1632 / AST-1648 / AST-1658)
```

2. In `ARTIFACT_CONFIG = { ... }`, keep the five existing keys unchanged and **add** (immediately after `candidate.context.bio_summary`):

```python
    "candidate.context.ideal_day": {
        "entity_type": "candidate",
        "candidate_scoped": True,
        # Reuse BUILD_CONFIG["artifact_shapes"]["plain_text"] (raw string) — do not invent a second shape.
        "body_shape": "plain_text",
        # Candidate owns first-row ingestion for Ideal Day (UI/API operative save — sibling).
        "ingestion_owner": "candidate",
    },
```

⚠️ **Decision:** Metadata key set matches Strengths / Bio Summary / pilot (`entity_type`, `candidate_scoped`, `body_shape`, `ingestion_owner`) — no new catalog metadata fields. `body_shape: "plain_text"` reuses the existing `"raw_string"` sentinel from AST-1632; do **not** add or rename a shape.

3. Replace the closed key-set assert with:

```python
assert set(ARTIFACT_CONFIG.keys()) == {
    "candidate.artifacts.base_resume",
    "job.artifacts.job_resume",
    "job.artifacts.cover_letter",
    "candidate.context.strengths",
    "candidate.context.bio_summary",
    "candidate.context.ideal_day",
}
```

Keep the existing job-blob sibling absence loop unchanged. Update the **context sibling freeze** loop so Ideal Day is **removed** from the absence list (it is now registered). The loop must still assert absence of:

```python
(
    "candidate.context.priorities",
    "candidate.context.deal_breakers",
    "candidate.context.backstory",
    "candidate.context.writing_preferences",
)
```

Do **not** leave `candidate.context.ideal_day` in that absence loop. Do **not** register any of those four sibling keys.

4. Immediately after the existing `_bs` per-entry asserts (and before the finalize / JAR assert block), add Ideal Day per-entry asserts:

```python
_id = ARTIFACT_CONFIG["candidate.context.ideal_day"]
assert _id["entity_type"] == "candidate"
assert _id["entity_type"] in ENTITY_TYPES
assert _id["candidate_scoped"] is True
assert isinstance(_id["candidate_scoped"], bool)
assert _id["body_shape"] == "plain_text"
assert _id["body_shape"] in BUILD_CONFIG["artifact_shapes"]
assert BUILD_CONFIG["artifact_shapes"]["plain_text"] == "raw_string"
assert _id["ingestion_owner"] == "candidate"
assert set(_id.keys()) == {
    "entity_type",
    "candidate_scoped",
    "body_shape",
    "ingestion_owner",
}
```

⚠️ **Decision:** Local binding name `_id` (Ideal Day) — mirrors `_st` / `_bs` short locals. Do not reuse `_id` elsewhere in this block.

5. Flip `TOKEN_SOURCES["IDEAL_DAY"]` from data_field to artifact. Replace the current one-liner (still at its existing dict location among context tokens — do not relocate the key) with:

```python
    "IDEAL_DAY": {
        "source": "candidate",
        "path": "context.ideal_day",
        "source_type": "artifact",
        "artifact_key": "candidate.context.ideal_day",
    },
```

Keep `source` / `path` (hydrate overlay leaf for siblings; same pattern as `STRENGTHS` / `BIO_SUMMARY` / `BASE_RESUME` keeping `path`). Do **not** add `serialize` — plain string, not resume section JSON.

⚠️ **Decision:** Leave other still-blob context tokens (`PRIORITIES`, `DEAL_BREAKERS`, `BACKSTORY`, `WRITING_PREFERENCES`) as `data_field`. Only `IDEAL_DAY` flips on this ticket. `STRENGTHS` / `BIO_SUMMARY` stay as already flipped.

6. Update the sole-artifact-token assert near the bottom of the TOKEN_SOURCES block:

```python
assert _artifact_tokens == {"BASE_RESUME", "STRENGTHS", "BIO_SUMMARY", "IDEAL_DAY"}
```

Add (same style as the existing BASE_RESUME / STRENGTHS / BIO_SUMMARY pairs):

```python
assert TOKEN_SOURCES["IDEAL_DAY"]["source_type"] == "artifact"
assert TOKEN_SOURCES["IDEAL_DAY"]["artifact_key"] == "candidate.context.ideal_day"
```

The generic `for _token_name, _spec in TOKEN_SOURCES.items()` loop already requires `artifact_key in ARTIFACT_CONFIG` for artifact rows — do not duplicate that logic elsewhere.

7. Do **not** edit `resolve_tokens`, candidate operative save, API, UI, `DATA_SHAPES`, or `NAV_CONFIG`. Do **not** add logger calls in config (logging citations are id-only for this config-only slice — no new info/debug surfaces). Do **not** invent a second `artifact_shapes` entry.

**Verify (hand):**

```bash
python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'candidate.context.ideal_day' in ARTIFACT_CONFIG"
python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert ARTIFACT_CONFIG['candidate.context.ideal_day']['body_shape']=='plain_text'"
python3 -c "from src.utils.config import TOKEN_SOURCES; s=TOKEN_SOURCES['IDEAL_DAY']; assert s['source_type']=='artifact' and s['artifact_key']=='candidate.context.ideal_day'"
python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert not any(k.endswith(s) for s in ('.priorities','.deal_breakers','.backstory','.writing_preferences') for k in ARTIFACT_CONFIG)"
```

## Execution contract

- Execute steps in order; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files, touch siblings' scopes, or invent catalog keys beyond `candidate.context.ideal_day`.
- On ambiguity or drift — stop, comment on parent AST-1643 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 1 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `patt.artifact.manage-catalog` | pattern — read in full; register Ideal Day; closed catalog |
| `astral.config.config-source-of-truth` | statute — catalog / token live in config |
| `astral.standards.no-hardcoded-sets` | statute — closed key/shape membership via asserts |
| `stat.logging.info` | id-only — no new logging surface this ticket |
| `stat.logging.debug` | id-only — no new logging surface this ticket |

## Joan validate

[plan-rubric]
**Ticket:** AST-1658
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref tip:** `4083cd8134bef9aa12911e9a368ab7ea0fd65af3` (`origin/sub/AST-1643/AST-1658-catalog-plain-text-ideal-day-token`)

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.manage-catalog | A | | |
| astral.config.config-source-of-truth | A | | |
| astral.standards.no-hardcoded-sets | A | | |
| stat.logging.info | X | | config-only slice; plan explicitly defers new info surfaces |
| stat.logging.debug | X | | config-only slice; plan explicitly defers new debug surfaces |

## Traceability

AC1→Stage 1; AC2→Stage 1; AC3→Stage 1; AC4→Stage 1; parent AC4–7, AC9→N/A (operative save/hydrate/UI — siblings AST-1659/AST-1660).

## Findings

None (`fix-now` / `discuss`).

**R6 notes (acceptable):** Plan mirrors existing `_st` / `_bs` per-entry assert pattern for `_id`; explicit scope gate confines work to `src/utils/config.py`; sibling freeze loop update is spelled out; `TOKEN_SOURCES["IDEAL_DAY"]` flip matches `STRENGTHS` / `BIO_SUMMARY` artifact shape; `_artifact_tokens` widen is explicit. `patt.artifact.manage-catalog` is scored from draft text (not yet in `canon_clerk` roster) — appropriate for this ticket's frozen list.

context_tokens≈32000

## Review (build stub)

**Built:** `origin/sub/AST-1643/AST-1658-catalog-plain-text-ideal-day-token` @ `a0d9f811ba6c6e9d0b220c94eb283baa5caf5b90`.

**Stages delivered:**
- Stage 1: `candidate.context.ideal_day` catalog + `IDEAL_DAY` artifact token — `a0d9f811ba6c6e9d0b220c94eb283baa5caf5b90`.

**Betty:** at **Code Complete** — cover ARTIFACT_CONFIG closed set + Ideal Day metadata, `plain_text` == `raw_string` reuse, context sibling freeze (priorities/deal_breakers/backstory/writing_preferences absent; ideal_day registered), `TOKEN_SOURCES["IDEAL_DAY"]` artifact_key linkage, `_artifact_tokens == {"BASE_RESUME", "STRENGTHS", "BIO_SUMMARY", "IDEAL_DAY"}`.

## Radia review

[code-rubric]
**Ticket:** AST-1658
**Publish ref:** c5af9cdc1f30718067f897182d655c6aebe78117
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.manage-catalog | A | | |
| astral.config.config-source-of-truth | A | | |
| astral.standards.no-hardcoded-sets | A | | |
| stat.logging.info | X | | config-only slice; no new `logger.info` surfaces |
| stat.logging.debug | X | | config-only slice; no new `logger.debug` surfaces |

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

- **Location:** `src/utils/config.py` — `TOKEN_SOURCES["IDEAL_DAY"]` + `resolve_tokens`
- **Finding:** Flipping `IDEAL_DAY` to `source_type: "artifact"` is typing/registry-only on this tip; `resolve_tokens` still walks `path: "context.ideal_day"` (same pattern as STRENGTHS / BIO_SUMMARY pre-operative). Plan bounds operative save, hydrate, and blob retirement to AST-1659 / AST-1660.
- **Recommendation:** No action on AST-1658; siblings own runtime artifact overlay.

- **Location:** `merge-tests` tip — `tests/component/core/test_candidate.py`, `tests/component/ui/api/test_api_candidate.py`
- **Finding:** `merge-tests(AST-1658)` landed AST-1652 / AST-1655 operative test classes (`TestAst1652PrioritiesOperativeApi`, `TestAst1655DealBreakersOperativeSaveHydrate`, etc.) but this tip's `src/core/candidate.py` has no `hydrate_operative_priorities_for_response` / `hydrate_operative_deal_breakers_for_response`. Betty manifest correctly scopes test-child to `test_config.py` only (green). Running the merged classes directly would fail.
- **Recommendation:** Downstream hygiene only — Chuckles/Betty may add parallel-epic `skipif` guards on merge or leave as manifest-scoped; not a product gate for this ticket.

- **Location:** `docs/test-bible/utils/config.md` § AST-1658 bible shasum
- **Finding:** Issue doc bible shasum line still `*(filled after publish)*`.
- **Recommendation:** Chuckles can sync on writeback — not a code gate.

- **Location:** Canon clerk / frozen list resolution
- **Finding:** `canon_clerk expand` does not serve `patt.artifact.manage-catalog`, `astral.config.config-source-of-truth`, or `astral.standards.no-hardcoded-sets` (draft pattern + `canon/statutes/` paths). Scored from repo files at epic worktree, not clerk payload.
- **Recommendation:** Corpus hygiene is downstream; no scope gap on the frozen list.

## Notes

- **Scope divergence (expected):** Product diff is confined to `src/utils/config.py` per plan Stage 1. `tests/component/utils/test_config.py`, `docs/test-bible/utils/config.md`, and `merge-tests` revisions to core/api test files + bible are Betty pipeline artifacts — not sibling product scope creep in `src/`.
- **Estimate footprint:** Confirm **1** point still fits; product surface is single-file catalog registration + token flip.

## What's solid

- Stage 1 delivered verbatim: `candidate.context.ideal_day` catalog entry (`plain_text` / `raw_string` reuse), closed six-key `ARTIFACT_CONFIG` set, full `_id` per-entry asserts, context sibling freeze loop (ideal_day removed; priorities / deal_breakers / backstory / writing_preferences still absent), `IDEAL_DAY` artifact flip with explicit linkage asserts, `_artifact_tokens == {"BASE_RESUME", "STRENGTHS", "BIO_SUMMARY", "IDEAL_DAY"}`, module docstring inventory cites AST-1658.
- `TestAst1658CatalogPlainTextIdealDayToken` locks catalog metadata, sibling freeze, token linkage, and plain_text shape reuse; prior AST-1590 / AST-1596 / AST-1365 / AST-1632 / AST-1648 tests revised for the new closed sets on this tip.
- Plan hand one-liners (AC1–AC4) match publish tip config state.

## Recommended actions

(none downstream — artifact complete)

context_tokens≈38000

