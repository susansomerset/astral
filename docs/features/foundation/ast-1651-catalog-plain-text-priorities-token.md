# Catalog + plain_text shape reuse + PRIORITIES token

**Linear:** [AST-1651](https://linear.app/astralcareermatch/issue/AST-1651)
**Parent:** [AST-1641](https://linear.app/astralcareermatch/issue/AST-1641) — Migrate candidate_data.context.priorities to use the artifact table
**Publish ref:** `sub/AST-1641/AST-1651-catalog-plain-text-priorities-token`

Register `candidate.context.priorities` in `ARTIFACT_CONFIG` reusing the existing `plain_text` body shape (AST-1632 / AST-1629), flip `TOKEN_SOURCES["PRIORITIES"]` to `source_type: "artifact"` with `artifact_key: "candidate.context.priorities"`, and lock startup asserts (closed key set + remove Priorities from the context sibling-freeze list). Config-only — no UI, hydrate, API intercept, or blob retirement (siblings AST-1652 / AST-1653).

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/utils/config.py` — new catalog entry plus asserts; `TOKEN_SOURCES["PRIORITIES"]` flip.

Every Files Changed row and every Stage step stays inside that one file. No `candidate.py`, no `api_candidate.py`, no React, no `database.py`, no other context keys, no new `artifact_shapes` entry (`plain_text` already exists), no `resolve_tokens` behavior change beyond what the typed registry already drives at import.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Register `candidate.context.priorities` in `ARTIFACT_CONFIG` + closed-set / per-entry asserts; drop that key from the context sibling-freeze loop; flip `TOKEN_SOURCES["PRIORITIES"]` to artifact + `artifact_key`; widen `_artifact_tokens` assert; update module docstring inventory | utils |

**Out of this ticket (do not touch):** operative `plain_text` validation / hydrate / library gate (AST-1652); API PUT intercept + GET hydrate; Priorities ContextTextPage wiring (AST-1653); `ArtifactEditor`; `database.py`; other context leaves; `BUILD_CONFIG["artifact_shapes"]["plain_text"]` (already present); `tests/` / `docs/test-bible/**`.

## Stage 1: Priorities catalog key + PRIORITIES token

**Done when:** `import src.utils.config` succeeds; ticket AC1–AC4 one-liners exit 0; `_artifact_tokens == {"BASE_RESUME", "STRENGTHS", "PRIORITIES"}`.

1. In `src/utils/config.py` module docstring **Config sections:** list, update the existing `ARTIFACT_CONFIG` inventory line to include the Priorities key (keep SoT wording; add AST-1651 citation; keep Strengths / prior cites):

```
  ARTIFACT_CONFIG — versioned artifact registry keyed by entity._data path (entity, candidate_scoped, body_shape, ingestion_owner); keys = candidate.artifacts.base_resume, job.artifacts.job_resume, job.artifacts.cover_letter, candidate.context.strengths, candidate.context.priorities; SoT in config — callers import ARTIFACT_CONFIG (AST-1573 / AST-1575 / AST-1576 / AST-1590 / AST-1632 / AST-1651)
```

2. Do **not** add or edit `BUILD_CONFIG["artifact_shapes"]["plain_text"]`. It must already equal `"raw_string"` from AST-1632. If it is missing at build time, stop and comment on parent AST-1641 — do not invent a second shape.

⚠️ **Decision:** Reuse the existing `plain_text` → `"raw_string"` sentinel. Parent Technical scope and ticket Notes forbid a new shape entry.

3. In `ARTIFACT_CONFIG = { ... }`, keep the four existing keys unchanged and **add** (immediately after `candidate.context.strengths`):

```python
    "candidate.context.priorities": {
        "entity_type": "candidate",
        "candidate_scoped": True,
        # Name into BUILD_CONFIG["artifact_shapes"]["plain_text"] (raw string body).
        "body_shape": "plain_text",
        # Candidate owns first-row ingestion for Priorities (UI/API operative save — sibling).
        "ingestion_owner": "candidate",
    },
```

⚠️ **Decision:** Metadata key set matches Strengths / pilot (`entity_type`, `candidate_scoped`, `body_shape`, `ingestion_owner`) — no new catalog metadata fields. `ingestion_owner: "candidate"` matches parent Technical scope.

4. Replace the closed key-set assert with:

```python
assert set(ARTIFACT_CONFIG.keys()) == {
    "candidate.artifacts.base_resume",
    "job.artifacts.job_resume",
    "job.artifacts.cover_letter",
    "candidate.context.strengths",
    "candidate.context.priorities",
}
```

5. Update the **context sibling freeze** loop: remove `"candidate.context.priorities"` from the tuple; keep the other four frozen. Refresh the comment to cite this ticket / parent AC8:

```python
# Sibling context leaves stay out of the catalog until their own epics (parent AC8 / AST-1651).
for _ctx_sibling in (
    "candidate.context.deal_breakers",
    "candidate.context.backstory",
    "candidate.context.ideal_day",
    "candidate.context.writing_preferences",
):
    assert _ctx_sibling not in ARTIFACT_CONFIG
```

Keep the existing job-blob sibling absence loop unchanged.

6. Immediately after the existing `_st` per-entry asserts (and before the finalize / JAR assert block), add Priorities per-entry asserts:

```python
_pr = ARTIFACT_CONFIG["candidate.context.priorities"]
assert _pr["entity_type"] == "candidate"
assert _pr["entity_type"] in ENTITY_TYPES
assert _pr["candidate_scoped"] is True
assert isinstance(_pr["candidate_scoped"], bool)
assert _pr["body_shape"] == "plain_text"
assert _pr["body_shape"] in BUILD_CONFIG["artifact_shapes"]
assert BUILD_CONFIG["artifact_shapes"]["plain_text"] == "raw_string"
assert _pr["ingestion_owner"] == "candidate"
assert set(_pr.keys()) == {
    "entity_type",
    "candidate_scoped",
    "body_shape",
    "ingestion_owner",
}
```

7. Flip `TOKEN_SOURCES["PRIORITIES"]` from data_field to artifact. Replace the current one-liner with:

```python
    "PRIORITIES": {
        "source": "candidate",
        "path": "context.priorities",
        "source_type": "artifact",
        "artifact_key": "candidate.context.priorities",
    },
```

Keep `source` / `path` (hydrate overlay leaf for siblings; same pattern as `STRENGTHS` / `BASE_RESUME`). Do **not** add `serialize` — plain string, not resume section JSON.

⚠️ **Decision:** Leave other remaining context tokens (`DEAL_BREAKERS`, `BACKSTORY`, …) as `data_field`. Only Priorities flips on this ticket. Strengths stays artifact (already shipped).

8. Update the artifact-token closed-set assert near the bottom of the TOKEN_SOURCES block:

```python
assert TOKEN_SOURCES["PRIORITIES"]["source_type"] == "artifact"
assert TOKEN_SOURCES["PRIORITIES"]["artifact_key"] == "candidate.context.priorities"
_artifact_tokens = {
    name for name, spec in TOKEN_SOURCES.items() if spec["source_type"] == "artifact"
}
assert _artifact_tokens == {"BASE_RESUME", "STRENGTHS", "PRIORITIES"}
```

Keep the existing `BASE_RESUME` / `STRENGTHS` linkage asserts. The generic `for _token_name, _spec in TOKEN_SOURCES.items()` loop already requires `artifact_key in ARTIFACT_CONFIG` for artifact rows — do not duplicate that logic elsewhere.

9. Do **not** edit `resolve_tokens`, candidate operative save, API, or UI. Do **not** add logger calls in config (logging citations are id-only for this config-only slice — no new info/debug surfaces).

**Verify (hand):**

```bash
python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'candidate.context.priorities' in ARTIFACT_CONFIG"
python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert ARTIFACT_CONFIG['candidate.context.priorities']['body_shape']=='plain_text'"
python3 -c "from src.utils.config import TOKEN_SOURCES; s=TOKEN_SOURCES['PRIORITIES']; assert s['source_type']=='artifact' and s['artifact_key']=='candidate.context.priorities'"
python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'candidate.context.deal_breakers' not in ARTIFACT_CONFIG and 'candidate.context.backstory' not in ARTIFACT_CONFIG and 'candidate.context.ideal_day' not in ARTIFACT_CONFIG and 'candidate.context.writing_preferences' not in ARTIFACT_CONFIG"
```

## Execution contract

- Execute steps in order; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files, touch siblings' scopes, or invent catalog keys beyond `candidate.context.priorities`.
- On ambiguity or drift — stop, comment on parent AST-1641 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 1 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `patt.artifact.manage-catalog` | pattern — read in full; register Priorities; closed catalog |
| `astral.config.config-source-of-truth` | statute — catalog / shape / token live in config |
| `astral.standards.no-hardcoded-sets` | statute — closed key/shape membership via asserts |
| `stat.logging.info` | id-only — no new logging surface this ticket |
| `stat.logging.debug` | id-only — no new logging surface this ticket |

## Joan validate

[plan-rubric]
**Ticket:** AST-1651
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `sub/AST-1641/AST-1651-catalog-plain-text-priorities-token` @ `1e1b67943d96acb3c972238a396536d979cf837b`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.manage-catalog | A | | |
| astral.config.config-source-of-truth | A | | |
| astral.standards.no-hardcoded-sets | A | | |
| stat.logging.info | X | | config-only slice; no new info surfaces (Stage 1 §9) |
| stat.logging.debug | X | | config-only slice; no new debug surfaces (Stage 1 §9) |

## Traceability

AC1→S1§3-4; AC2→S1§2-3,6; AC3→S1§7-8; AC4→S1§5 — parent AC5–9 N/A (operative/hydrate/API/UI owned by AST-1652/AST-1653).

## Findings

None.

### R6 — Definition fidelity (checklist)

- Plan implements child **## Scope** only (`src/utils/config.py`); explicit scope gate present; no out-of-scope files in Files Changed or Stages.
- All four child acceptance criteria have concrete Stage 1 steps and verify one-liners.
- Mirrors AST-1632 (Strengths) catalog/token pattern: adds `candidate.context.priorities`, removes it from sibling-freeze loop, reuses existing `plain_text` shape (correctly does **not** re-add `BUILD_CONFIG["artifact_shapes"]["plain_text"]`), flips `TOKEN_SOURCES["PRIORITIES"]` with `source`/`path` retained like `STRENGTHS`.
- Operative save, hydrate, API intercept, blob retirement, and UI correctly deferred to siblings per ticket boundaries.
- Self-assessment: `Confirm Chuckles estimate: 1 — agree` is honest for a single-file closed-assert change.
- Plan Discuss rounds completed: **0** (status Plan Ready; no `[plan-discuss]` thread).

context_tokens≈52000

## Review (build stub)

**Built:** `origin/sub/AST-1641/AST-1651-catalog-plain-text-priorities-token` @ `ded632db5cfe3f05658db73b84b348f49ab64157`.

**Stages delivered:**
- Stage 1: `candidate.context.priorities` catalog + `PRIORITIES` artifact token — `ded632db5cfe3f05658db73b84b348f49ab64157`.

**Betty:** at **Code Complete** — cover ARTIFACT_CONFIG closed set + Priorities metadata, context sibling freeze without priorities, `TOKEN_SOURCES["PRIORITIES"]` artifact_key linkage, `_artifact_tokens == {"BASE_RESUME", "STRENGTHS", "PRIORITIES"}`.

## Radia review

[code-rubric]
**Ticket:** AST-1651
**Publish ref:** `09ea76f5fdaf89cd5111ead3ab442e2d61869aa2`
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.manage-catalog | A | | |
| astral.config.config-source-of-truth | A | | |
| astral.standards.no-hardcoded-sets | A | | |
| stat.logging.info | X | | config-only slice; no new info surfaces |
| stat.logging.debug | X | | config-only slice; no new debug surfaces |

## Column diff vs plan stage

(aligned)

## Frame diff

(none)

## Findings

### discuss

- **Cross-ticket scope on publish ref.** Branch history includes `90a33f94 test(AST-1648): bio_summary catalog + BIO_SUMMARY token + profile/nav`, which adds `TestAst1648CatalogBioSummaryTokenProfileNav` (~90 lines) and an AST-1648 `docs/test-bible/utils/config.md` block. The same bible append also documents AST-1654 (deal_breakers parallel epic). None of this is AST-1651 product work; `config.py` on this tip still has `BIO_SUMMARY` as `data_field` with no `candidate.context.bio_summary` catalog key. The AST-1648 class is `skipif`-gated and harmless here, but the diff carries sibling-epic test/bible footprint that the ticket **## Explicit scope gate** and **Out of this ticket** rows exclude for the engineer slice. Worth a Chuckles/Susan call on whether parallel-epic scaffolding stays on the sub branch until `merge-child` or should be stripped before UT.

### advisory

- **Plan vs pipeline scope wording.** Engineer plan scoped **only** `src/utils/config.py`; Betty's `TestAst1651CatalogPlainTextPrioritiesToken` + bible manifest are correct pipeline additions and mirror AST-1632. The AST-1648/AST-1654 artifacts above are the divergence — not the AST-1651 test class itself.
- **Canon clerk resolution.** `patt.artifact.manage-catalog`, `astral.config.config-source-of-truth`, and `astral.standards.no-hardcoded-sets` do not resolve via `canon_clerk expand` (active corpus only). Scored from `canon/directives/draft/patt.artifact.manage-catalog.md` and `canon/statutes/astral/{config,standards}/` mirrors — same `corpus_sha` Joan used; not a scope gap.
- **Bible shasum placeholders** in the appended manifest blocks still read `*(filled after publish)*` — Betty hygiene, not a canon block.

## What's solid

- `src/utils/config.py` delivers Stage 1 exactly: `candidate.context.priorities` registered with `plain_text` reuse (no new `artifact_shapes` entry), closed `ARTIFACT_CONFIG` key set, priorities removed from sibling-freeze loop, per-entry `_pr` asserts, `TOKEN_SOURCES["PRIORITIES"]` flipped to `artifact` + `artifact_key`, `_artifact_tokens == {"BASE_RESUME", "STRENGTHS", "PRIORITIES"}`, module docstring inventory updated.
- `TestAst1651CatalogPlainTextPrioritiesToken` covers catalog metadata, sibling freeze, and token linkage; shared `TestAst1590` / `TestAst1596` helpers updated to the new closed sets and counts (21 / 3 / 27).
- `TestAst1632` freeze list correctly drops `priorities`; sibling assertion pivots to `DEAL_BREAKERS` still-`data_field`.
- No new logging, no `resolve_tokens` / API / UI / `database.py` touches in product diff.

## Recommended actions (for Chuckles — not Radia)

- Append this artifact to the issue doc; commit `docs(AST-1651): Radia review — clean` on `origin/sub/AST-1641/AST-1651-catalog-plain-text-priorities-token`.
- Post slim upshot via `linear_proxy --as radia`; advance to **Review Posted** → datt **§3h** PROCEED path (no `resolve-child` product work from canon).
- If Susan wants a leaner sub tip: discuss stripping `90a33f94` AST-1648 test/bible hunks from this branch vs keeping skipif merge-hygiene for parallel epics.

context_tokens≈58000
