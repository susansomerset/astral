<!-- linear-archive: AST-1632 archived 2026-09-24 -->

## Linear archive (AST-1632)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1632/catalog-plain-text-shape-strengths-token-migrate-candidate  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1629 — Migrate candidate_data.context.strengths to use the artifact table  
**Blocked by / blocks / related:** parent: AST-1629; blocks: AST-1633

### Description

## What this implements

Register `candidate.context.strengths` in `ARTIFACT_CONFIG` with `body_shape: "plain_text"`, add `BUILD_CONFIG["artifact_shapes"]["plain_text"]` (raw string), flip `TOKEN_SOURCES["STRENGTHS"]` to artifact + `artifact_key`, lock startup asserts. Does not own UI or hydrate.

## Citations

`patt.artifact.manage-catalog`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `stat.logging.info` / `stat.logging.debug` as touched

## Scope

`src/utils/config.py` — new catalog entry + asserts; `plain_text` artifact_shapes entry; `TOKEN_SOURCES["STRENGTHS"]` flip.

## Acceptance criteria

1. **Catalog key present** — `python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'candidate.context.strengths' in ARTIFACT_CONFIG"` exits 0.
2. **plain_text shape** — `python3 -c "from src.utils.config import ARTIFACT_CONFIG, BUILD_CONFIG; assert ARTIFACT_CONFIG['candidate.context.strengths']['body_shape']=='plain_text'; assert 'plain_text' in BUILD_CONFIG['artifact_shapes']"` exits 0.
3. **Token is artifact-typed** — `python3 -c "from src.utils.config import TOKEN_SOURCES; s=TOKEN_SOURCES['STRENGTHS']; assert s['source_type']=='artifact' and s['artifact_key']=='candidate.context.strengths'"` exits 0.

## Boundaries

Does not own UI, hydrate, API PUT intercept, or blob retirement (siblings). Does not migrate other context keys.

## Notes for planning

Citations as above. First catalog key on `plain_text` shape — template for later context migrations.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1629-migrate-strengths-artifact-table`, child `sub/AST-1629/<this-id>-catalog-plain-text-strengths-token`. Created at dispatch-parent.

### Comments

#### radia — 2026-09-14T23:34:16.647Z
[code-rubric] PROCEED (Commit: f0c27497390d) config catalog clean

#### betty — 2026-09-14T23:31:18.702Z
origin/sub/AST-1629/AST-1632-catalog-plain-text-strengths-token @ f0c27497390d605c53c0f4cabae0e168c6dd5158 · strengths catalog tests

#### joan — 2026-09-14T23:24:25.069Z
[plan-rubric] PROCEED (Commit: 12d49988) config catalog slice clean

#### ada — 2026-09-14T23:22:27.042Z
`origin/sub/AST-1629/AST-1632-catalog-plain-text-strengths-token` @ `12d49988f6295cc4e5e6909842d6b38934d08452` · plan ready config

---

# Catalog + plain_text shape + STRENGTHS token

**Linear:** [AST-1632](https://linear.app/astralcareermatch/issue/AST-1632)
**Parent:** [AST-1629](https://linear.app/astralcareermatch/issue/AST-1629) — Migrate candidate_data.context.strengths to use the artifact table
**Publish ref:** `sub/AST-1629/AST-1632-catalog-plain-text-strengths-token`

Register `candidate.context.strengths` in `ARTIFACT_CONFIG` with `body_shape: "plain_text"`, add `BUILD_CONFIG["artifact_shapes"]["plain_text"]` as a raw-string body contract (not a field map), flip `TOKEN_SOURCES["STRENGTHS"]` to `source_type: "artifact"` with `artifact_key: "candidate.context.strengths"`, and lock startup asserts. Config-only — no UI, hydrate, API intercept, or blob retirement (siblings).

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/utils/config.py` — new catalog entry + asserts; `plain_text` artifact_shapes entry; `TOKEN_SOURCES["STRENGTHS"]` flip.

Every Files Changed row and every Stage step stays inside that one file. No `candidate.py`, no `api_candidate.py`, no React, no `database.py`, no other context keys, no resolve_tokens behavior change beyond what the typed registry already drives at import.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `plain_text` to `BUILD_CONFIG["artifact_shapes"]`; register `candidate.context.strengths` in `ARTIFACT_CONFIG` + closed-set / per-entry / sibling-freeze asserts; flip `TOKEN_SOURCES["STRENGTHS"]` to artifact + `artifact_key`; widen `_artifact_tokens` assert; update module docstring inventory | utils |

**Out of this ticket (do not touch):** operative `plain_text` validation / hydrate / library gate (sibling after #1); API PUT intercept + GET hydrate; Strengths ContextTextPage wiring; `ArtifactEditor`; `database.py`; other context leaves; `tests/` / `docs/test-bible/**`.

## Stage 1: `plain_text` shape + Strengths catalog key + STRENGTHS token

**Done when:** `import src.utils.config` succeeds; ticket AC1–AC3 one-liners exit 0; sibling context keys are absent from `ARTIFACT_CONFIG`; `_artifact_tokens == {"BASE_RESUME", "STRENGTHS"}`.

1. In `src/utils/config.py` module docstring **Config sections:** list, update the existing `ARTIFACT_CONFIG` inventory line to include the Strengths key (keep SoT wording; cite AST-1632):

```
  ARTIFACT_CONFIG — versioned artifact registry keyed by entity._data path (entity, candidate_scoped, body_shape, ingestion_owner); keys = candidate.artifacts.base_resume, job.artifacts.job_resume, job.artifacts.cover_letter, candidate.context.strengths; SoT in config — callers import ARTIFACT_CONFIG (AST-1573 / AST-1575 / AST-1576 / AST-1590 / AST-1632)
```

2. In `BUILD_CONFIG["artifact_shapes"]`, immediately after the existing `"cover_letter": { ... }` entry (still inside the `artifact_shapes` dict), add:

```python
        # AST-1632: raw string body — value is NOT a field-keyed schema (unlike resume_content / cover_letter).
        # Operative validation (sibling) gates on body_shape == "plain_text", not shape.items().
        "plain_text": "raw_string",
```

⚠️ **Decision:** Shape value is the string sentinel `"raw_string"`, not a one-field dict and not a `{type, required}` field map. Parent Technical scope: raw string body contract. Membership (`"plain_text" in BUILD_CONFIG["artifact_shapes"]`) is what AC2 / per-entry `body_shape in artifact_shapes` asserts need; sibling #2 owns `isinstance(blob, str)` rules.

3. In `ARTIFACT_CONFIG = { ... }`, keep the three existing keys unchanged and **add**:

```python
    "candidate.context.strengths": {
        "entity_type": "candidate",
        "candidate_scoped": True,
        # Name into BUILD_CONFIG["artifact_shapes"]["plain_text"] (raw string body).
        "body_shape": "plain_text",
        # Candidate owns first-row ingestion for Strengths (UI/API operative save — sibling).
        "ingestion_owner": "candidate",
    },
```

⚠️ **Decision:** Metadata key set matches the pilot (`entity_type`, `candidate_scoped`, `body_shape`, `ingestion_owner`) — no new catalog metadata fields. `ingestion_owner: "candidate"` matches parent Technical scope and base_resume ownership for candidate-scoped UI content.

4. Replace the closed key-set assert with:

```python
assert set(ARTIFACT_CONFIG.keys()) == {
    "candidate.artifacts.base_resume",
    "job.artifacts.job_resume",
    "job.artifacts.cover_letter",
    "candidate.context.strengths",
}
```

Keep the existing job-blob sibling absence loop unchanged. Immediately after that loop (still before `_br = ...`), add a **context sibling freeze** loop (parent AC8 / this ticket Boundaries — Strengths only):

```python
# Sibling context leaves stay out of the catalog until their own epics (parent AC8 / AST-1632).
for _ctx_sibling in (
    "candidate.context.priorities",
    "candidate.context.deal_breakers",
    "candidate.context.backstory",
    "candidate.context.ideal_day",
    "candidate.context.writing_preferences",
):
    assert _ctx_sibling not in ARTIFACT_CONFIG
```

5. Immediately after the existing `_cl` per-entry asserts (and before the finalize / JAR assert block), add Strengths per-entry asserts:

```python
_st = ARTIFACT_CONFIG["candidate.context.strengths"]
assert _st["entity_type"] == "candidate"
assert _st["entity_type"] in ENTITY_TYPES
assert _st["candidate_scoped"] is True
assert isinstance(_st["candidate_scoped"], bool)
assert _st["body_shape"] == "plain_text"
assert _st["body_shape"] in BUILD_CONFIG["artifact_shapes"]
assert BUILD_CONFIG["artifact_shapes"]["plain_text"] == "raw_string"
assert _st["ingestion_owner"] == "candidate"
assert set(_st.keys()) == {
    "entity_type",
    "candidate_scoped",
    "body_shape",
    "ingestion_owner",
}
```

6. Flip `TOKEN_SOURCES["STRENGTHS"]` from data_field to artifact. Replace the current one-liner with:

```python
    "STRENGTHS": {
        "source": "candidate",
        "path": "context.strengths",
        "source_type": "artifact",
        "artifact_key": "candidate.context.strengths",
    },
```

Keep `source` / `path` (hydrate overlay leaf for siblings; same pattern as `BASE_RESUME` keeping `path`). Do **not** add `serialize` — plain string, not resume section JSON.

⚠️ **Decision:** Leave other context tokens (`PRIORITIES`, `DEAL_BREAKERS`, …) as `data_field`. Only Strengths flips on this ticket.

7. Update the sole-artifact-token assert near the bottom of the TOKEN_SOURCES block:

```python
assert _artifact_tokens == {"BASE_RESUME", "STRENGTHS"}
```

Optionally add (same style as the existing BASE_RESUME pair):

```python
assert TOKEN_SOURCES["STRENGTHS"]["source_type"] == "artifact"
assert TOKEN_SOURCES["STRENGTHS"]["artifact_key"] == "candidate.context.strengths"
```

The generic `for _token_name, _spec in TOKEN_SOURCES.items()` loop already requires `artifact_key in ARTIFACT_CONFIG` for artifact rows — do not duplicate that logic elsewhere.

8. Do **not** edit `resolve_tokens`, candidate operative save, API, or UI. Do **not** add logger calls in config (logging citations are id-only for this config-only slice — no new info/debug surfaces).

**Verify (hand):**

```bash
python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'candidate.context.strengths' in ARTIFACT_CONFIG"
python3 -c "from src.utils.config import ARTIFACT_CONFIG, BUILD_CONFIG; assert ARTIFACT_CONFIG['candidate.context.strengths']['body_shape']=='plain_text'; assert 'plain_text' in BUILD_CONFIG['artifact_shapes']"
python3 -c "from src.utils.config import TOKEN_SOURCES; s=TOKEN_SOURCES['STRENGTHS']; assert s['source_type']=='artifact' and s['artifact_key']=='candidate.context.strengths'"
```

## Execution contract

- Execute steps in order; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files, touch siblings' scopes, or invent catalog keys beyond `candidate.context.strengths`.
- On ambiguity or drift — stop, comment on parent AST-1629 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `patt.artifact.manage-catalog` | pattern — read in full; register Strengths; closed catalog |
| `astral.config.config-source-of-truth` | statute — catalog / shape / token live in config |
| `astral.standards.no-hardcoded-sets` | statute — closed key/shape membership via asserts |
| `stat.logging.info` | id-only — no new logging surface this ticket |
| `stat.logging.debug` | id-only — no new logging surface this ticket |

## Joan validate

[plan-rubric]
**Ticket:** AST-1632
**Overall:** APPROVED
**Corpus:** 0b920f4e7dfc842c1032277aa99ac34e1bd0f9b9
**Publish ref tip:** 12d49988f6295cc4e5e6909842d6b38934d08452

## Canon scores

patt.artifact.manage-catalog | A | | Register-only slice matches epic partition; closed catalog + sibling freeze; read/write/retire correctly deferred to siblings per Boundaries
astral.config.config-source-of-truth | A | | All catalog/shape/token changes confined to config.py blocks
astral.standards.no-hardcoded-sets | A | | Closed key set, per-entry asserts, artifact-token set, context sibling-absence loops mirror existing config patterns
stat.logging.info | X | | id-only; Stage 1 §8 explicitly defers — no new logging surfaces in config-only slice
stat.logging.debug | X | | id-only; same deferral — no new debug surfaces

## Traceability

AC1→Stage 1 §3–4+verify; AC2→Stage 1 §2+§5+verify; AC3→Stage 1 §6–7+verify; parent AC4–9 N/A (operative save, hydrate, blob retirement, editor reload, backfill, sibling freeze UI — sibling tickets #2/#3).

## Findings

### acceptable

- **Location:** Canon clerk / ticket list
- **Finding:** `canon_clerk expand` serves only `canon/directives/active/` (12 ids). Three frozen ids (`patt.artifact.manage-catalog`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`) live under draft/statutes paths and were scored from repo files at the epic worktree, not clerk payload.
- **Recommendation:** No plan change. Corpus hygiene is Archie/Chuckles territory; scores above are from those files' Statement/Examples.

### acceptable

- **Location:** Stage 1 §6 / resolve_tokens
- **Finding:** Flipping `STRENGTHS` to `source_type: artifact` does not change `resolve_tokens` runtime (still walks `path` until sibling hydrate overlays `context.strengths`). Plan documents this explicitly and bounds resolve_tokens out of scope.
- **Recommendation:** None for this ticket; sibling #2 owns hydrate + blob retirement per parent partition.

context_tokens≈22000

## Review (build stub)

**Built:** `origin/sub/AST-1629/AST-1632-catalog-plain-text-strengths-token` @ `bd7411988e4df0a614706be9bcc4a63ddc9f99dd`.

**Stages delivered:**
- Stage 1: `plain_text` shape + `candidate.context.strengths` catalog + `STRENGTHS` artifact token — `bd7411988e4df0a614706be9bcc4a63ddc9f99dd`.

**Betty:** at **Code Complete** — cover ARTIFACT_CONFIG closed set + Strengths metadata, `plain_text` == `raw_string`, context sibling freeze, `TOKEN_SOURCES["STRENGTHS"]` artifact_key linkage, `_artifact_tokens == {"BASE_RESUME", "STRENGTHS"}`.

## Radia review

[code-rubric]
**Ticket:** AST-1632
**Publish ref:** f0c27497390d605c53c0f4cabae0e168c6dd5158
**Corpus:** 0b920f4e7dfc842c1032277aa99ac34e1bd0f9b9
**Overall:** CLEAN

## Canon scores

patt.artifact.manage-catalog | A | | Register-only slice: `candidate.context.strengths` catalog entry, `plain_text` shape, STRENGTHS artifact token; read/write/retire correctly deferred per Boundaries
astral.config.config-source-of-truth | A | | Catalog, shape sentinel, token flip, and all asserts confined to `src/utils/config.py`
astral.standards.no-hardcoded-sets | A | | Closed ARTIFACT_CONFIG key set, per-entry `_st` asserts, context sibling-absence loop, `_artifact_tokens == {"BASE_RESUME", "STRENGTHS"}`
stat.logging.info | X | | id-only; config-only slice adds no `logger.info` surfaces
stat.logging.debug | X | | id-only; config-only slice adds no `logger.debug` surfaces

## Column diff vs plan stage

(aligned)

## Frame diff

(none)

## Findings

### advisory

- **Location:** `src/utils/config.py` — `TOKEN_SOURCES["STRENGTHS"]` + `resolve_tokens`
- **Finding:** Flipping `STRENGTHS` to `source_type: "artifact"` is typing/registry-only today; `resolve_tokens` still walks `path: "context.strengths"` (same as pre-flip). Plan documents this and bounds operative hydrate + blob retirement to sibling tickets.
- **Recommendation:** No action on AST-1632; sibling owns runtime artifact overlay.

### advisory

- **Location:** Canon clerk / frozen list resolution
- **Finding:** `canon_clerk expand` serves `canon/directives/active/` only; three frozen ids (`patt.artifact.manage-catalog`, `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets`) were scored from repo statute/pattern files at the epic worktree, not clerk payload.
- **Recommendation:** Corpus hygiene is downstream; scores above are from those files' Statement/Examples.

## What's solid

- Stage 1 plan steps 1–8 delivered verbatim in `config.py`: `plain_text: "raw_string"`, full Strengths catalog metadata, closed key-set assert, context sibling freeze, per-entry `_st` asserts, STRENGTHS token flip with explicit linkage asserts, module docstring inventory update.
- Betty manifest coverage is tight: `TestAst1632CatalogPlainTextStrengthsToken` plus revised `TestAst1590JobArtifactCatalogKeys` / `TestAst1596TokenCatalogSourceTypeTyping` counts and getters.
- AC1–AC3 one-liners exit 0 against publish tip.

## Scope notes (not findings)

- Product diff is `src/utils/config.py` only; `tests/component/utils/test_config.py` and `docs/test-bible/utils/config.md` are expected qa-child / Betty pipeline artifacts.
- Estimate **2** fits: single-file config registration + targeted test revisions.

## Recommended actions

- Chuckles: append artifact, commit `docs(AST-1632): Radia review — clean`, post slim upshot, move to **Review Posted**.
- datt: **PROCEED** → **User Testing** (no resolve-child round needed).
