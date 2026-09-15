# Catalog + BIO_SUMMARY token + profile/nav config

**Linear:** [AST-1648](https://linear.app/astralcareermatch/issue/AST-1648)
**Parent:** [AST-1647](https://linear.app/astralcareermatch/issue/AST-1647) — Migrate candidate bio summary to use the artifact table and remove from candidate profile page
**Publish ref:** `sub/AST-1647/AST-1648-catalog-bio-summary-token-profile-nav`

Register `candidate.context.bio_summary` in `ARTIFACT_CONFIG` reusing the existing `plain_text` body shape from AST-1632, flip `TOKEN_SOURCES["BIO_SUMMARY"]` to `source_type: "artifact"` with `artifact_key: "candidate.context.bio_summary"`, lock startup asserts (including sibling context freeze), delete the candidate profile `DATA_SHAPES` Bio Summary section, and add a Candidate `NAV_CONFIG` leaf for Bio Summary. Config-only — no hydrate, API intercept, or React pages (siblings AST-1649 / AST-1650).

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/utils/config.py` — new catalog entry + asserts; `TOKEN_SOURCES["BIO_SUMMARY"]` flip; delete `DATA_SHAPES["candidates"]["detail"]["profile"]` Bio Summary section (`context.bio_summary`); add `NAV_CONFIG` Candidate item `{label: "Bio Summary", path: "/candidate/bio_summary"}`.

Every Files Changed row and every Stage step stays inside that one file. No `candidate.py`, no `api_candidate.py`, no React, no `database.py`, no other context keys, no new `artifact_shapes` entry (reuse AST-1632 `plain_text`), no `INTAKE_CONFIG`, no resolve_tokens behavior change beyond what the typed registry already drives at import.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Register `candidate.context.bio_summary` in `ARTIFACT_CONFIG` + closed-set / per-entry asserts; keep sibling-freeze loop (still excludes bio_summary from the absent list — it becomes registered); flip `TOKEN_SOURCES["BIO_SUMMARY"]` to artifact + `artifact_key`; widen `_artifact_tokens`; delete profile Bio Summary `DATA_SHAPES` section; add Candidate `NAV_CONFIG` leaf; update module docstring inventory | utils |

**Out of this ticket (do not touch):** operative `plain_text` validation / hydrate / library gate (AST-1649); API PUT intercept + GET hydrate (AST-1649); `CandidateBioSummary.tsx` / `routes.tsx` (AST-1650); `CandidateProfile.tsx` / `ContextTextPage.tsx` / `ArtifactEditor.tsx`; `database.py`; other context leaves; `INTAKE_CONFIG`; `tests/` / `docs/test-bible/**`.

## Stage 1: Bio Summary catalog + BIO_SUMMARY token + profile/nav config

**Done when:** `import src.utils.config` succeeds; ticket AC1–AC4 and nav AC7 one-liners exit 0; sibling context keys remain absent from `ARTIFACT_CONFIG`; `_artifact_tokens == {"BASE_RESUME", "STRENGTHS", "BIO_SUMMARY"}`; profile `DATA_SHAPES` has no Bio Summary section / `context.bio_summary` field; Candidate nav includes Bio Summary → `/candidate/bio_summary`.

1. In `src/utils/config.py` module docstring **Config sections:** list, update the existing `ARTIFACT_CONFIG` inventory line to include the bio summary key (keep SoT wording; cite AST-1648 alongside AST-1632):

```
  ARTIFACT_CONFIG — versioned artifact registry keyed by entity._data path (entity, candidate_scoped, body_shape, ingestion_owner); keys = candidate.artifacts.base_resume, job.artifacts.job_resume, job.artifacts.cover_letter, candidate.context.strengths, candidate.context.bio_summary; SoT in config — callers import ARTIFACT_CONFIG (AST-1573 / AST-1575 / AST-1576 / AST-1590 / AST-1632 / AST-1648)
```

2. In `ARTIFACT_CONFIG = { ... }`, keep the four existing keys unchanged and **add** (immediately after `candidate.context.strengths`):

```python
    "candidate.context.bio_summary": {
        "entity_type": "candidate",
        "candidate_scoped": True,
        # Reuse BUILD_CONFIG["artifact_shapes"]["plain_text"] (raw string) — do not invent a second shape.
        "body_shape": "plain_text",
        # Candidate owns first-row ingestion for Bio Summary (UI/API operative save — sibling AST-1649).
        "ingestion_owner": "candidate",
    },
```

⚠️ **Decision:** Metadata key set matches Strengths / pilot (`entity_type`, `candidate_scoped`, `body_shape`, `ingestion_owner`) — no new catalog metadata fields. `body_shape: "plain_text"` reuses the existing `"raw_string"` sentinel from AST-1632; do **not** add or rename a shape.

3. Replace the closed key-set assert with:

```python
assert set(ARTIFACT_CONFIG.keys()) == {
    "candidate.artifacts.base_resume",
    "job.artifacts.job_resume",
    "job.artifacts.cover_letter",
    "candidate.context.strengths",
    "candidate.context.bio_summary",
}
```

Keep the existing job-blob sibling absence loop unchanged. Keep the **context sibling freeze** loop unchanged — it must still assert absence of:

```python
(
    "candidate.context.priorities",
    "candidate.context.deal_breakers",
    "candidate.context.backstory",
    "candidate.context.ideal_day",
    "candidate.context.writing_preferences",
)
```

Do **not** add `candidate.context.bio_summary` to that absence loop (it is now registered). Do **not** register any of those five sibling keys.

4. Immediately after the existing `_st` per-entry asserts (and before the finalize / JAR assert block), add Bio Summary per-entry asserts:

```python
_bs = ARTIFACT_CONFIG["candidate.context.bio_summary"]
assert _bs["entity_type"] == "candidate"
assert _bs["entity_type"] in ENTITY_TYPES
assert _bs["candidate_scoped"] is True
assert isinstance(_bs["candidate_scoped"], bool)
assert _bs["body_shape"] == "plain_text"
assert _bs["body_shape"] in BUILD_CONFIG["artifact_shapes"]
assert BUILD_CONFIG["artifact_shapes"]["plain_text"] == "raw_string"
assert _bs["ingestion_owner"] == "candidate"
assert set(_bs.keys()) == {
    "entity_type",
    "candidate_scoped",
    "body_shape",
    "ingestion_owner",
}
```

5. Flip `TOKEN_SOURCES["BIO_SUMMARY"]` from data_field to artifact. Replace the current one-liner (still at its existing dict location — do not relocate the key among other tokens) with:

```python
    "BIO_SUMMARY": {
        "source": "candidate",
        "path": "context.bio_summary",
        "source_type": "artifact",
        "artifact_key": "candidate.context.bio_summary",
    },
```

Keep `source` / `path` (hydrate overlay leaf for siblings; same pattern as `STRENGTHS` / `BASE_RESUME` keeping `path`). Do **not** add `serialize` — plain string, not resume section JSON.

⚠️ **Decision:** Leave other context tokens (`PRIORITIES`, `DEAL_BREAKERS`, …) as `data_field`. Only `BIO_SUMMARY` flips on this ticket. `STRENGTHS` stays as already flipped by AST-1632.

6. Update the sole-artifact-token assert near the bottom of the TOKEN_SOURCES block:

```python
assert _artifact_tokens == {"BASE_RESUME", "STRENGTHS", "BIO_SUMMARY"}
```

Add (same style as the existing BASE_RESUME / STRENGTHS pairs):

```python
assert TOKEN_SOURCES["BIO_SUMMARY"]["source_type"] == "artifact"
assert TOKEN_SOURCES["BIO_SUMMARY"]["artifact_key"] == "candidate.context.bio_summary"
```

The generic `for _token_name, _spec in TOKEN_SOURCES.items()` loop already requires `artifact_key in ARTIFACT_CONFIG` for artifact rows — do not duplicate that logic elsewhere.

7. In `DATA_SHAPES["candidates"]["detail"]["profile"]`, **delete** the entire section dict whose `"label"` is `"Bio Summary"` and whose only field is `context.bio_summary` (the block currently between Contact and Sample Cover Letter). Leave Sample Cover Letter and every other profile section untouched. Do **not** edit other `bio_summary` mentions outside this profile section (INTAKE / required-field lists stay — Boundaries: no `INTAKE_CONFIG` / other-context migration).

8. In `NAV_CONFIG`, under the group `"label": "Candidate"`, add immediately after the existing Strengths item:

```python
            {"label": "Bio Summary", "path": "/candidate/bio_summary"},
```

⚠️ **Decision:** Place Bio Summary with the other context leaves, right after Strengths (both are `plain_text` context artifacts). Do not reorder unrelated Candidate items. Do not add React routes here — AST-1650 owns the page + `routes.tsx`.

9. Do **not** edit `resolve_tokens`, candidate operative save, API, or UI. Do **not** add logger calls in config (logging citations are id-only for this config-only slice — no new info/debug surfaces). Do **not** invent a second `artifact_shapes` entry.

**Verify (hand):**

```bash
python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'candidate.context.bio_summary' in ARTIFACT_CONFIG"
python3 -c "from src.utils.config import ARTIFACT_CONFIG, BUILD_CONFIG; assert ARTIFACT_CONFIG['candidate.context.bio_summary']['body_shape']=='plain_text'; assert BUILD_CONFIG['artifact_shapes']['plain_text']=='raw_string'"
python3 -c "from src.utils.config import TOKEN_SOURCES; s=TOKEN_SOURCES['BIO_SUMMARY']; assert s['source_type']=='artifact' and s['artifact_key']=='candidate.context.bio_summary'"
python3 -c "from src.utils.config import DATA_SHAPES; p=DATA_SHAPES['candidates']['detail']['profile']; assert not any(s.get('label')=='Bio Summary' or any(f.get('key')=='context.bio_summary' for f in s.get('fields',[])) for s in p)"
python3 -c "from src.utils.config import NAV_CONFIG; c=next(g for g in NAV_CONFIG if g['label']=='Candidate'); assert any(i.get('label')=='Bio Summary' and i.get('path')=='/candidate/bio_summary' for i in c['items'])"
python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert not any(k.endswith(s) for s in ('.priorities','.deal_breakers','.backstory','.ideal_day','.writing_preferences') for k in ARTIFACT_CONFIG)"
```

## Execution contract

- Execute steps in order; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files, touch siblings' scopes, or invent catalog keys beyond `candidate.context.bio_summary`.
- On ambiguity or drift — stop, comment on parent AST-1647 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `patt.artifact.manage-catalog` | pattern — read in full; register Bio Summary; closed catalog |
| `astral.config.config-source-of-truth` | statute — catalog / token / nav / DATA_SHAPES live in config |
| `astral.standards.no-hardcoded-sets` | statute — closed key/shape membership via asserts |
| `stat.logging.info` | id-only — no new logging surface this ticket |
| `stat.logging.debug` | id-only — no new logging surface this ticket |

## Joan validate

[plan-rubric]
**Ticket:** AST-1648
**Overall:** APPROVED
**Corpus:** fc0c368e59
**Publish-ref tip:** 8815aefbc13d17e3f64c93f12e97a4cacf5f19d6

## Canon scores

| Id | Grade | Effort | One-line |
|----|-------|--------|----------|
| patt.artifact.manage-catalog | A | | |
| astral.config.config-source-of-truth | A | | |
| astral.standards.no-hardcoded-sets | A | | |
| stat.logging.info | X | | Config-only slice; no new info logging surfaces — id-only citation correct |
| stat.logging.debug | X | | Config-only slice; no new debug surfaces — id-only citation correct |

## Traceability

AC1→S1:2–3 · AC2→S1:2,4 · AC3→S1:5–6 · AC4→S1:7 · AC7(nav)→S1:8 · AC5(sibling freeze)→S1:3,9 · Parent AC4/5/8→N/A (AST-1649) · Parent AC7(page/route)/AC10→N/A (AST-1650)

## Findings

### acceptable

- **Location:** Plan header / Stage 1
- **Finding:** Plan cites AST-1632 for `plain_text` reuse; parent epic cites AST-1629 — same Strengths cutover lineage, not a scope conflict.
- **Recommendation:** Optional editorial alignment only; no plan change required.

context_tokens≈42000

**Summary:** AST-1648 is **APPROVED**. The plan is a faithful, config-only slice: one file (`src/utils/config.py`), mirrors the AST-1632 Strengths pattern for catalog entry, closed-set asserts, `BIO_SUMMARY` artifact flip, profile removal, and nav leaf. Boundaries to AST-1649/AST-1650 are explicit. All five canon ids score A or X; no fix-now, discuss, or escalate items. Status was **Plan Ready** with zero `[plan-discuss]` rounds.

## Review (build stub)

**Built:** `origin/sub/AST-1647/AST-1648-catalog-bio-summary-token-profile-nav` @ `fc963ea12e9c69ad9791825fd164117be10b932a`.

**Stages delivered:**
- Stage 1: `candidate.context.bio_summary` catalog + `BIO_SUMMARY` artifact token + profile Bio Summary removed + Candidate nav leaf — `fc963ea12e9c69ad9791825fd164117be10b932a`.

**Betty:** at **Code Complete** — cover ARTIFACT_CONFIG closed set + Bio Summary metadata, `plain_text` == `raw_string` reuse, context sibling freeze (priorities/deal_breakers/backstory/ideal_day/writing_preferences absent), `TOKEN_SOURCES["BIO_SUMMARY"]` artifact_key linkage, `_artifact_tokens == {"BASE_RESUME", "STRENGTHS", "BIO_SUMMARY"}`, profile DATA_SHAPES Bio Summary gone, NAV_CONFIG Candidate Bio Summary → `/candidate/bio_summary`.
