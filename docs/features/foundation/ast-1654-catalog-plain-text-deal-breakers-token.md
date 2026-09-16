# Catalog + plain_text shape reuse + DEAL_BREAKERS token

**Linear:** [AST-1654](https://linear.app/astralcareermatch/issue/AST-1654)
**Parent:** [AST-1642](https://linear.app/astralcareermatch/issue/AST-1642) — Migrate candidate_data.context.deal_breakers to use the artifact table
**Publish ref:** `sub/AST-1642/AST-1654-catalog-plain-text-deal-breakers-token`

Register `candidate.context.deal_breakers` in `ARTIFACT_CONFIG` reusing the existing `plain_text` shape (already added by AST-1632 — do not re-add the shape), flip `TOKEN_SOURCES["DEAL_BREAKERS"]` to `source_type: "artifact"` with `artifact_key: "candidate.context.deal_breakers"`, widen closed-set / per-entry / artifact-token asserts, and drop Deal Breakers from the context-sibling freeze list. Config-only — no UI, hydrate, API intercept, or blob retirement (siblings). Mirror AST-1632 guidelines.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/utils/config.py` — new catalog entry plus asserts; `TOKEN_SOURCES["DEAL_BREAKERS"]` flip; remove Deal Breakers from context-sibling freeze assert.

Every Files Changed row and every Stage step stays inside that one file. No `candidate.py`, no `api_candidate.py`, no React, no `database.py`, no other context keys, no new `artifact_shapes` entry, no `resolve_tokens` behavior change beyond what the typed registry already drives at import.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Register `candidate.context.deal_breakers` in `ARTIFACT_CONFIG` + closed-set / per-entry asserts; drop that key from context-sibling freeze; flip `TOKEN_SOURCES["DEAL_BREAKERS"]` to artifact + `artifact_key`; widen `_artifact_tokens` assert; update module docstring inventory | utils |

**Out of this ticket (do not touch):** operative `plain_text` validation / hydrate / library gate (sibling #2); API PUT intercept + GET hydrate; Deal Breakers ContextTextPage wiring (sibling #3); `ArtifactEditor`; `database.py`; other context leaves; `BUILD_CONFIG["artifact_shapes"]["plain_text"]` (already present); `tests/` / `docs/test-bible/**`.

## Stage 1: Deal Breakers catalog key + DEAL_BREAKERS token

**Done when:** `import src.utils.config` succeeds; ticket AC1–AC4 one-liners exit 0; priorities/backstory/ideal_day/writing_preferences remain absent from `ARTIFACT_CONFIG`; `_artifact_tokens == {"BASE_RESUME", "STRENGTHS", "DEAL_BREAKERS"}`.

1. In `src/utils/config.py` module docstring **Config sections:** list, update the existing `ARTIFACT_CONFIG` inventory line to include the Deal Breakers key (keep SoT wording; cite AST-1654 alongside AST-1632):

```
  ARTIFACT_CONFIG — versioned artifact registry keyed by entity._data path (entity, candidate_scoped, body_shape, ingestion_owner); keys = candidate.artifacts.base_resume, job.artifacts.job_resume, job.artifacts.cover_letter, candidate.context.strengths, candidate.context.deal_breakers; SoT in config — callers import ARTIFACT_CONFIG (AST-1573 / AST-1575 / AST-1576 / AST-1590 / AST-1632 / AST-1654)
```

2. Do **not** add or edit `BUILD_CONFIG["artifact_shapes"]["plain_text"]`. It already exists as `"raw_string"` from AST-1632. Reuse it by name only.

⚠️ **Decision:** Reuse — never rederive. Parent Purpose and ticket Notes: copy Strengths guidelines; `plain_text` is already the proven shape. Adding a second shape or renaming would fail AC2.

3. In `ARTIFACT_CONFIG = { ... }`, keep the four existing keys unchanged and **add** after `candidate.context.strengths`:

```python
    "candidate.context.deal_breakers": {
        "entity_type": "candidate",
        "candidate_scoped": True,
        # Name into BUILD_CONFIG["artifact_shapes"]["plain_text"] (raw string body).
        "body_shape": "plain_text",
        # Candidate owns first-row ingestion for Deal Breakers (UI/API operative save — sibling).
        "ingestion_owner": "candidate",
    },
```

⚠️ **Decision:** Metadata key set matches Strengths / the pilot (`entity_type`, `candidate_scoped`, `body_shape`, `ingestion_owner`) — no new catalog metadata fields. `ingestion_owner: "candidate"` matches parent Technical scope and Strengths ownership for candidate-scoped UI content.

4. Replace the closed key-set assert with:

```python
assert set(ARTIFACT_CONFIG.keys()) == {
    "candidate.artifacts.base_resume",
    "job.artifacts.job_resume",
    "job.artifacts.cover_letter",
    "candidate.context.strengths",
    "candidate.context.deal_breakers",
}
```

Keep the existing job-blob sibling absence loop unchanged. Replace the **context sibling freeze** loop so Deal Breakers is **removed** from the absent list (parent AC8 / this ticket AC4) while the other four stay frozen:

```python
# Sibling context leaves stay out of the catalog until their own epics (parent AC8 / AST-1654).
# Deal Breakers is registered above — no longer asserted absent.
for _ctx_sibling in (
    "candidate.context.priorities",
    "candidate.context.backstory",
    "candidate.context.ideal_day",
    "candidate.context.writing_preferences",
):
    assert _ctx_sibling not in ARTIFACT_CONFIG
```

5. Immediately after the existing `_st` per-entry asserts (and before the finalize / JAR assert block), add Deal Breakers per-entry asserts mirroring `_st`:

```python
_db = ARTIFACT_CONFIG["candidate.context.deal_breakers"]
assert _db["entity_type"] == "candidate"
assert _db["entity_type"] in ENTITY_TYPES
assert _db["candidate_scoped"] is True
assert isinstance(_db["candidate_scoped"], bool)
assert _db["body_shape"] == "plain_text"
assert _db["body_shape"] in BUILD_CONFIG["artifact_shapes"]
assert BUILD_CONFIG["artifact_shapes"]["plain_text"] == "raw_string"
assert _db["ingestion_owner"] == "candidate"
assert set(_db.keys()) == {
    "entity_type",
    "candidate_scoped",
    "body_shape",
    "ingestion_owner",
}
```

6. Flip `TOKEN_SOURCES["DEAL_BREAKERS"]` from data_field to artifact. Replace the current one-liner with:

```python
    "DEAL_BREAKERS": {
        "source": "candidate",
        "path": "context.deal_breakers",
        "source_type": "artifact",
        "artifact_key": "candidate.context.deal_breakers",
    },
```

Keep `source` / `path` (hydrate overlay leaf for siblings; same pattern as `STRENGTHS` / `BASE_RESUME` keeping `path`). Do **not** add `serialize` — plain string, not resume section JSON.

⚠️ **Decision:** Leave other context tokens (`PRIORITIES`, `BACKSTORY`, …) as `data_field`. Only Deal Breakers flips on this ticket. Strengths stays artifact-typed (pre-existing).

7. Update the sole-artifact-token assert near the bottom of the TOKEN_SOURCES block:

```python
assert _artifact_tokens == {"BASE_RESUME", "STRENGTHS", "DEAL_BREAKERS"}
```

Add (same style as the existing STRENGTHS pair):

```python
assert TOKEN_SOURCES["DEAL_BREAKERS"]["source_type"] == "artifact"
assert TOKEN_SOURCES["DEAL_BREAKERS"]["artifact_key"] == "candidate.context.deal_breakers"
```

The generic `for _token_name, _spec in TOKEN_SOURCES.items()` loop already requires `artifact_key in ARTIFACT_CONFIG` for artifact rows — do not duplicate that logic elsewhere.

8. Do **not** edit `resolve_tokens`, candidate operative save, API, or UI. Do **not** add logger calls in config (logging citations are id-only for this config-only slice — no new info/debug surfaces).

**Verify (hand):**

```bash
python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'candidate.context.deal_breakers' in ARTIFACT_CONFIG"
python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert ARTIFACT_CONFIG['candidate.context.deal_breakers']['body_shape']=='plain_text'"
python3 -c "from src.utils.config import TOKEN_SOURCES; s=TOKEN_SOURCES['DEAL_BREAKERS']; assert s['source_type']=='artifact' and s['artifact_key']=='candidate.context.deal_breakers'"
python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'candidate.context.priorities' not in ARTIFACT_CONFIG and 'candidate.context.backstory' not in ARTIFACT_CONFIG and 'candidate.context.ideal_day' not in ARTIFACT_CONFIG and 'candidate.context.writing_preferences' not in ARTIFACT_CONFIG and 'candidate.context.deal_breakers' in ARTIFACT_CONFIG"
```

## Execution contract

- Execute steps in order; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files, touch siblings' scopes, or invent catalog keys beyond `candidate.context.deal_breakers`.
- Do not re-add `plain_text` to `artifact_shapes` or change its `"raw_string"` sentinel.
- On ambiguity or drift — stop, comment on parent AST-1642 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 1 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `patt.artifact.manage-catalog` | pattern — read in full; register Deal Breakers; closed catalog; retire blob authority deferred to siblings |
| `astral.config.config-source-of-truth` | statute — catalog / token live in config |
| `astral.standards.no-hardcoded-sets` | statute — closed key/shape membership via asserts |
| `stat.logging.info` | id-only — no new logging surface this ticket |
| `stat.logging.debug` | id-only — no new logging surface this ticket |

## Joan validate

[plan-rubric]
**Ticket:** AST-1654
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** ca2d61cc77f32fccdb256257180a419e811a6607

## Canon scores

patt.artifact.manage-catalog | A | | Register-only slice: `candidate.context.deal_breakers` catalog entry reuses `plain_text`; STRENGTHS/BASE_RESUME pattern; read/write/blob-retire correctly deferred to siblings
astral.config.config-source-of-truth | A | | Catalog entry, token flip, closed-set and per-entry asserts confined to `src/utils/config.py`
astral.standards.no-hardcoded-sets | A | | Closed `ARTIFACT_CONFIG` key set, `_db` per-entry asserts, context sibling-absence loop, `_artifact_tokens == {"BASE_RESUME", "STRENGTHS", "DEAL_BREAKERS"}`
stat.logging.info | X | | id-only; config-only slice adds no `logger.info` surfaces
stat.logging.debug | X | | id-only; config-only slice adds no `logger.debug` surfaces

## Traceability

AC1→S1·3-4 | AC2→S1·2-3 | AC3→S1·6-7 | AC4→S1·4 | parent AC4–7, AC9→N/A (sibling #2/#3 scope)

## Findings

### acceptable

- **Location:** `src/utils/config.py` — `TOKEN_SOURCES["DEAL_BREAKERS"]` + `resolve_tokens`
- **Finding:** Flipping `DEAL_BREAKERS` to `source_type: "artifact"` is typing/registry-only at import; `resolve_tokens` still walks `path: "context.deal_breakers"` until sibling #2 wires operative hydrate and blob retirement. Plan documents this explicitly (step 8) and mirrors AST-1632 precedent.
- **Recommendation:** No plan change; sibling #2 owns runtime artifact overlay.

### discuss (Canon Scope gap — do not score)

- **Location:** Parent Canon Scope vs child frozen list
- **Finding:** `astral.standards.in-scope-only` governs this config-only slice (explicit scope gate is present and honored) but is absent from the child's frozen five-id list.
- **Recommendation:** Archie may amend at Discussion if cross-child comparability matters; plan already demonstrates in-scope behavior.

### acceptable

- **Location:** Canon clerk resolution
- **Finding:** `canon_clerk expand` serves `directives/active/` only; three frozen ids (`patt.artifact.manage-catalog`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`) were scored from repo statute/pattern files at the epic worktree, not clerk payload.
- **Recommendation:** Corpus hygiene is downstream; grades above cite those files' Statement/Examples.

## R6 checklist (summary)

Definition fidelity: pass — single-file scope gate matches ticket `## Scope`; mirrors AST-1632 (reuses existing `plain_text` shape, does not re-add `artifact_shapes` entry); no sibling file creep.
DRY / scope: pass — copies proven Strengths registration pattern; defers operative/API/UI to siblings.
Self-assessment: pass — `!!` child with explicit Decision callouts; Estimate confirm line present; no `!!-NONE` conf gap.

context_tokens≈52000

## Review (build stub)

**Built:** `origin/sub/AST-1642/AST-1654-catalog-plain-text-deal-breakers-token` @ `571526008e1350442ed5e0a48e2bf45c8ee6ea1e`.

**Stages delivered:**
- Stage 1: `candidate.context.deal_breakers` catalog + `DEAL_BREAKERS` artifact token (reuse `plain_text`) — `571526008e1350442ed5e0a48e2bf45c8ee6ea1e`.

**Betty:** at **Code Complete** — cover ARTIFACT_CONFIG closed set + Deal Breakers metadata, context sibling freeze without deal_breakers, `TOKEN_SOURCES["DEAL_BREAKERS"]` artifact_key linkage, `_artifact_tokens == {"BASE_RESUME", "STRENGTHS", "DEAL_BREAKERS"}`.

## Radia review

[code-rubric]
**Ticket:** AST-1654
**Publish ref:** 7814d07d8704e4733cad36f6b2a9c6d85915af0c
**Corpus:** 4a0e30e37a6c5898021b2e5718787edfb1b6c37a · `canon_clerk expand` unknown for three frozen ids (draft pattern + scoped statutes under `canon/directives/draft/` and `canon/statutes/astral/`); scored from repo files at publish tip
**Overall:** CLEAN

## Canon scores

patt.artifact.manage-catalog | A | | Register-only slice: `candidate.context.deal_breakers` catalog entry reuses `plain_text`; STRENGTHS/BASE_RESUME pattern; read/write/blob-retire correctly deferred to siblings
astral.config.config-source-of-truth | A | | Catalog entry, token flip, closed-set and per-entry asserts confined to `src/utils/config.py`
astral.standards.no-hardcoded-sets | A | | Closed `ARTIFACT_CONFIG` key set, `_db` per-entry asserts, context sibling-absence loop, `_artifact_tokens == {"BASE_RESUME", "STRENGTHS", "DEAL_BREAKERS"}`
stat.logging.info | X | | id-only; config-only slice adds no `logger.info` surfaces
stat.logging.debug | X | | id-only; config-only slice adds no `logger.debug` surfaces

## Column diff vs plan stage

(aligned)

## Frame diff

(none)

## Findings

### advisory

- **Location:** `src/utils/config.py` — `TOKEN_SOURCES["DEAL_BREAKERS"]` + `resolve_tokens`
- **Finding:** Flipping `DEAL_BREAKERS` to `source_type: "artifact"` is typing/registry-only at import; `resolve_tokens` still walks `path: "context.deal_breakers"` until sibling #2 wires operative hydrate and blob retirement. Plan documents this explicitly (Stage 1 step 8) and mirrors AST-1632 precedent.
- **Recommendation:** No action on AST-1654; sibling owns runtime artifact overlay.

### advisory

- **Location:** Canon clerk resolution
- **Finding:** `canon_clerk expand` serves `canon/directives/active/` only; three frozen ids (`patt.artifact.manage-catalog`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`) were scored from repo statute/pattern files at the epic worktree, not clerk payload.
- **Recommendation:** Corpus hygiene is downstream; grades above cite those files' Statement/Examples.

## What's solid

- Stage 1 plan steps 1–8 delivered verbatim in `config.py`: module docstring inventory cites AST-1654; `plain_text` shape reused (not re-added); full Deal Breakers catalog metadata; closed key-set assert; context sibling freeze with `deal_breakers` removed from absent list; per-entry `_db` asserts mirroring `_st`; `DEAL_BREAKERS` token flip with explicit linkage asserts; `_artifact_tokens` widened to three artifact tokens.
- Betty manifest coverage is tight: `TestAst1654CatalogPlainTextDealBreakersToken` plus revised `TestAst1590JobArtifactCatalogKeys` / `TestAst1596TokenCatalogSourceTypeTyping` counts and getters match publish tip.
- Plan AC1–AC4 one-liners (Stage 1 verify block) align with delivered config state.

## Scope notes (not findings)

- Product diff is `src/utils/config.py` only (+217 plan doc on branch). `tests/component/utils/test_config.py` and `docs/test-bible/utils/config.md` are expected qa-child / Betty pipeline artifacts; plan explicit scope gate names build scope as config-only.
- `merge-tests(AST-1654)` tip also carries skipif-gated `TestAst1648*` / `TestAst1651*` forward-compat classes and parallel bible sections from `origin/tests`; they do not run on this tip and do not change product behavior — documented in bible AST-1654 section.
- Estimate **1** fits: single-file config registration + targeted test revisions.
- **Canon Scope observation (Joan plan carry-forward):** `astral.standards.in-scope-only` governs this slice but is absent from the frozen five-id list; diff honors the plan's explicit scope gate — no new off-scope product files.

## Recommended actions

- Chuckles: append artifact, commit `docs(AST-1654): Radia review — clean`, post slim upshot, move to **Review Posted**.
- datt: **PROCEED** → **User Testing** (no resolve-child round needed).

---
