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
