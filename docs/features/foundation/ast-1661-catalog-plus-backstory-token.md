# Catalog plus BACKSTORY token

**Linear:** [AST-1661](https://linear.app/astralcareermatch/issue/AST-1661)
**Parent:** [AST-1644](https://linear.app/astralcareermatch/issue/AST-1644) — Migrate candidate_data.context.backstory to use the artifact table
**Publish ref:** `sub/AST-1644/AST-1661-catalog-plus-backstory-token`

Register `candidate.context.backstory` in `ARTIFACT_CONFIG` reusing the existing `plain_text` shape (already added by AST-1632 — do not re-add the shape), flip `TOKEN_SOURCES["BACKSTORY"]` to `source_type: "artifact"` with `artifact_key: "candidate.context.backstory"`, widen closed-set / per-entry / artifact-token asserts, and drop Backstory from the context-sibling freeze list. Config-only — no UI, hydrate, API intercept, or blob retirement (siblings). Mirror AST-1632 / AST-1654 guidelines for the catalog/token slice.

## UAT fitness

- **AC restored:** Parent AC1 — Catalog key present (`candidate.context.backstory` in `ARTIFACT_CONFIG`). Parent AC2 — `plain_text` shape reused (no new shape; not `resume_content` / `cover_letter`). Parent AC3 — Token is artifact-typed (`TOKEN_SOURCES["BACKSTORY"]` has `source_type=="artifact"` and `artifact_key=="candidate.context.backstory"`). Parent AC8 — Sibling freeze: priorities / ideal_day / writing_preferences stay out of `ARTIFACT_CONFIG` (Backstory itself is in the catalog after this epic).
- **Correct outcome:** `{$BACKSTORY}` is typed as an artifact catalog key bound to `candidate.context.backstory` with `body_shape: "plain_text"`; import-time asserts lock the closed catalog and freeze remaining unmigrated context leaves.
- **Sibling check:** AST-1662 owns operative save / hydrate / blob retirement; AST-1663 owns `CandidateBackstory.tsx` ContextTextPage wire-up. Pre-landed catalog keys (`strengths`, `deal_breakers`, `bio_summary`) and their artifact tokens stay registered — this ticket only adds Backstory. Verified by closed key-set assert + freeze loop after removing only `candidate.context.backstory`.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Inventing a second body shape, routing Backstory through `resume_content` / `cover_letter`, editing `candidate.py` / API / React on this ticket, or unregistering already-migrated siblings (`deal_breakers`, `bio_summary`) to force a stale AC8 wording — all rejected. Catalog + token flip in `config.py` is the AC-matching slice.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/utils/config.py` — new catalog entry plus asserts; `TOKEN_SOURCES["BACKSTORY"]` flip; sibling-freeze list update for Backstory.

Every Files Changed row and every Stage step stays inside that one file. No `candidate.py`, no `api_candidate.py`, no React, no `database.py`, no other context keys, no new `artifact_shapes` entry, no `resolve_tokens` behavior change beyond what the typed registry already drives at import.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Register `candidate.context.backstory` in `ARTIFACT_CONFIG` + closed-set / per-entry asserts; drop that key from context-sibling freeze; flip `TOKEN_SOURCES["BACKSTORY"]` to artifact + `artifact_key`; widen `_artifact_tokens` assert; update module docstring inventory | utils |

**Out of this ticket (do not touch):** operative `plain_text` validation / hydrate / library gate (sibling #2 AST-1662); API PUT intercept + GET hydrate; Backstory ContextTextPage wiring (sibling #3 AST-1663); `ArtifactEditor`; `database.py`; other context leaves; `BUILD_CONFIG["artifact_shapes"]["plain_text"]` (already present); `tests/` / `docs/test-bible/**`.

## Stage 1: Backstory catalog key + BACKSTORY token

**Done when:** `import src.utils.config` succeeds; ticket AC1–AC3 one-liners exit 0; priorities / ideal_day / writing_preferences remain absent from `ARTIFACT_CONFIG`; `_artifact_tokens == {"BASE_RESUME", "STRENGTHS", "DEAL_BREAKERS", "BIO_SUMMARY", "BACKSTORY"}`.

1. In `src/utils/config.py` module docstring **Config sections:** list, update the existing `ARTIFACT_CONFIG` inventory line to include the Backstory key (keep SoT wording; cite AST-1661 alongside prior catalog tickets):

```
  ARTIFACT_CONFIG — versioned artifact registry keyed by entity._data path (entity, candidate_scoped, body_shape, ingestion_owner); keys = candidate.artifacts.base_resume, job.artifacts.job_resume, job.artifacts.cover_letter, candidate.context.strengths, candidate.context.deal_breakers, candidate.context.bio_summary, candidate.context.backstory; SoT in config — callers import ARTIFACT_CONFIG (AST-1573 / AST-1575 / AST-1576 / AST-1590 / AST-1632 / AST-1654 / AST-1648 / AST-1661)
```

2. Do **not** add or edit `BUILD_CONFIG["artifact_shapes"]["plain_text"]`. It already exists as `"raw_string"` from AST-1632. Reuse it by name only.

⚠️ **Decision:** Reuse — never rederive. Parent Purpose and ticket Notes: copy Strengths / Deal Breakers guidelines; `plain_text` is already the proven shape. Adding a second shape or renaming would fail AC2.

3. In `ARTIFACT_CONFIG = { ... }`, keep the six existing keys unchanged and **add** after `candidate.context.bio_summary`:

```python
    "candidate.context.backstory": {
        "entity_type": "candidate",
        "candidate_scoped": True,
        # Name into BUILD_CONFIG["artifact_shapes"]["plain_text"] (raw string body).
        "body_shape": "plain_text",
        # Candidate owns first-row ingestion for Backstory (UI/API operative save — sibling).
        "ingestion_owner": "candidate",
    },
```

⚠️ **Decision:** Metadata key set matches Strengths / Deal Breakers / Bio Summary / the pilot (`entity_type`, `candidate_scoped`, `body_shape`, `ingestion_owner`) — no new catalog metadata fields. `ingestion_owner: "candidate"` matches parent Technical scope and prior context-leaf ownership for candidate-scoped UI content.

4. Replace the closed key-set assert with:

```python
assert set(ARTIFACT_CONFIG.keys()) == {
    "candidate.artifacts.base_resume",
    "job.artifacts.job_resume",
    "job.artifacts.cover_letter",
    "candidate.context.strengths",
    "candidate.context.deal_breakers",
    "candidate.context.bio_summary",
    "candidate.context.backstory",
}
```

Keep the existing job-blob sibling absence loop unchanged. Replace the **context sibling freeze** loop so Backstory is **removed** from the absent list (parent AC8 / this ticket AC4) while the remaining unmigrated leaves stay frozen:

```python
# Sibling context leaves stay out of the catalog until their own epics (parent AC8 / AST-1661).
# Backstory is registered above — no longer asserted absent.
# deal_breakers / bio_summary already registered by prior epics — do not re-freeze them.
for _ctx_sibling in (
    "candidate.context.priorities",
    "candidate.context.ideal_day",
    "candidate.context.writing_preferences",
):
    assert _ctx_sibling not in ARTIFACT_CONFIG
```

⚠️ **Decision:** Parent AC8 / ticket AC4 prose still lists `deal_breakers` among forbidden keys (copy-paste from Strengths). Tree already has `candidate.context.deal_breakers` and `candidate.context.bio_summary` from AST-1654 / AST-1648. This ticket must **not** unregister those keys. Hand-verify AC4 as: priorities / ideal_day / writing_preferences absent; Backstory present; leave deal_breakers / bio_summary registered.

5. Immediately after the existing `_bs` per-entry asserts (and before the finalize / JAR assert block), add Backstory per-entry asserts mirroring `_st` / `_db` / `_bs`:

```python
_bk = ARTIFACT_CONFIG["candidate.context.backstory"]
assert _bk["entity_type"] == "candidate"
assert _bk["entity_type"] in ENTITY_TYPES
assert _bk["candidate_scoped"] is True
assert isinstance(_bk["candidate_scoped"], bool)
assert _bk["body_shape"] == "plain_text"
assert _bk["body_shape"] in BUILD_CONFIG["artifact_shapes"]
assert BUILD_CONFIG["artifact_shapes"]["plain_text"] == "raw_string"
assert _bk["ingestion_owner"] == "candidate"
assert set(_bk.keys()) == {
    "entity_type",
    "candidate_scoped",
    "body_shape",
    "ingestion_owner",
}
```

6. Flip `TOKEN_SOURCES["BACKSTORY"]` from data_field to artifact. Replace the current one-liner with:

```python
    "BACKSTORY": {
        "source": "candidate",
        "path": "context.backstory",
        "source_type": "artifact",
        "artifact_key": "candidate.context.backstory",
    },
```

Keep `source` / `path` (hydrate overlay leaf for siblings; same pattern as `STRENGTHS` / `DEAL_BREAKERS` / `BASE_RESUME` keeping `path`). Do **not** add `serialize` — plain string, not resume section JSON.

⚠️ **Decision:** Leave other still-blob context tokens (`PRIORITIES`, `IDEAL_DAY`, `WRITING_PREFERENCES`) as `data_field`. Only Backstory flips on this ticket. Strengths / Deal Breakers / Bio Summary stay artifact-typed (pre-existing).

7. Update the sole-artifact-token assert near the bottom of the TOKEN_SOURCES block:

```python
assert _artifact_tokens == {
    "BASE_RESUME",
    "STRENGTHS",
    "DEAL_BREAKERS",
    "BIO_SUMMARY",
    "BACKSTORY",
}
```

Add (same style as the existing STRENGTHS / DEAL_BREAKERS / BIO_SUMMARY pairs):

```python
assert TOKEN_SOURCES["BACKSTORY"]["source_type"] == "artifact"
assert TOKEN_SOURCES["BACKSTORY"]["artifact_key"] == "candidate.context.backstory"
```

The generic `for _token_name, _spec in TOKEN_SOURCES.items()` loop already requires `artifact_key in ARTIFACT_CONFIG` for artifact rows — do not duplicate that logic elsewhere.

8. Do **not** edit `resolve_tokens`, candidate operative save, API, or UI. Do **not** add logger calls in config (logging citations are id-only for this config-only slice — no new info/debug surfaces).

**Verify (hand):**

```bash
python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'candidate.context.backstory' in ARTIFACT_CONFIG"
python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert ARTIFACT_CONFIG['candidate.context.backstory']['body_shape']=='plain_text'"
python3 -c "from src.utils.config import TOKEN_SOURCES; s=TOKEN_SOURCES['BACKSTORY']; assert s['source_type']=='artifact' and s['artifact_key']=='candidate.context.backstory'"
python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'candidate.context.priorities' not in ARTIFACT_CONFIG and 'candidate.context.ideal_day' not in ARTIFACT_CONFIG and 'candidate.context.writing_preferences' not in ARTIFACT_CONFIG and 'candidate.context.backstory' in ARTIFACT_CONFIG"
```

## Execution contract

- Execute steps in order; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files, touch siblings' scopes, or invent catalog keys beyond `candidate.context.backstory`.
- Do not re-add `plain_text` to `artifact_shapes` or change its `"raw_string"` sentinel.
- On ambiguity or drift — stop, comment on parent AST-1644 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 1 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `patt.artifact.manage-catalog` | pattern — read in full; register Backstory; closed catalog; retire blob authority deferred to siblings |
| `astral.config.config-source-of-truth` | statute — catalog / token live in config |
| `astral.standards.no-hardcoded-sets` | statute — closed key/shape membership via asserts |
| `stat.logging.info` | id-only — no new logging surface this ticket |
| `stat.logging.debug` | id-only — no new logging surface this ticket |

## Joan validate

[plan-rubric]
**Ticket:** AST-1661
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `8397ea1cb326687928c93e7cb4c1b30d79d3a40c` (`origin/sub/AST-1644/AST-1661-catalog-plus-backstory-token`)

## Canon scores

| Id | Grade | Effort | One-line |
|----|-------|--------|----------|
| patt.artifact.manage-catalog | A | | |
| astral.config.config-source-of-truth | A | | |
| astral.standards.no-hardcoded-sets | A | | |
| stat.logging.info | X | | id-only — config-only slice; no new info surfaces planned |
| stat.logging.debug | X | | id-only — config-only slice; no new debug surfaces planned |

## Traceability

AC1→Stage 1 (catalog key + closed-set assert); AC2→Stage 1 (reuse `plain_text`, no new shape); AC3→Stage 1 (TOKEN_SOURCES flip + per-token asserts); AC4→Stage 1 step 4 (freeze loop — priorities/ideal_day/writing_preferences absent; backstory present); parent AC4–AC7, AC9→N/A (AST-1662/AST-1663 siblings); parent AC8→Stage 1 step 4 (with documented deal_breakers/bio_summary carve-out).

## Findings

### acceptable — procedural

- **Location:** Linear assignee
- **Finding:** Ticket is `Plan Ready` with assignee Ada Lovelace, not Joan. Chuckles should assign Joan before spawn in the normal path; validation proceeded per explicit spawn.
- **Recommendation:** Chuckles restores implementer after posting upshot per §8.

### discuss — ticket AC4 wording vs tree reality

- **Location:** Ticket Description AC4 vs Stage 1 step 4 Decision
- **Finding:** Child AC4 prose still forbids `deal_breakers` in `ARTIFACT_CONFIG`, but the tree already registers `candidate.context.deal_breakers` and `candidate.context.bio_summary` (AST-1654 / AST-1648). Plan correctly hand-verifies priorities/ideal_day/writing_preferences absent and does not unregister migrated siblings.
- **Recommendation:** Optional Description cleanup at Discussion — plan already documents the carve-out; no plan revision required.

### acceptable — epic sequencing

- **Location:** Stage 1 / UAT fitness sibling check
- **Finding:** BACKSTORY flips to `artifact` before AST-1662 wires hydrate — same catalog-first split as AST-1632/AST-1654 precedent; plan explicitly defers operative/hydrate to sibling #2.
- **Recommendation:** None — mirror pattern is intentional.

context_tokens≈22000
