<!-- linear-archive: AST-1664 archived 2026-09-24 -->

## Linear archive (AST-1664)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1664/catalog-plain-text-shape-reuse-writing-preferences-token-migrate  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / 1  
**Parent:** AST-1645 — Migrate candidate_data.context.writing_preferences to use the artifact table  
**Blocked by / blocks / related:** parent: AST-1645; blocks: AST-1665

### Description

## What this implements

Register `candidate.context.writing_preferences` in `ARTIFACT_CONFIG` reusing the existing `plain_text` shape, flip `TOKEN_SOURCES["WRITING_PREFERENCES"]` to artifact plus `artifact_key`, lock startup asserts (add key to closed set; remove from sibling-freeze-out list). Does not own UI or hydrate.

## Citations

`patt.artifact.manage-catalog`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `stat.logging.info` / `stat.logging.debug` as touched

## Scope

`src/utils/config.py` — new catalog entry plus asserts; `TOKEN_SOURCES["WRITING_PREFERENCES"]` flip.

## Acceptance criteria

- [X] 1\. Catalog key present — assert `candidate.context.writing_preferences` in ARTIFACT_CONFIG.
- [X] 2\. plain_text shape reused — body_shape == plain_text.
- [X] 3\. Token is artifact-typed — WRITING_PREFERENCES source_type artifact + artifact_key.
- [X] 4\. Sibling freeze — `backstory` / `ideal_day` remain absent; `writing_preferences` removed from freeze-out (priorities/deal_breakers/bio_summary already cataloged by their own epics — not asserted absent).

## Boundaries

- [X] Does not own UI or hydrate (siblings #2/#3). No other context leaves.

## Notes for planning

Citations as above. Copy AST-1629 Strengths catalog path; remove writing_preferences from sibling-freeze-out list.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/<parent-segment>`, child `sub/<parent-id>/<child-segment>`. Created at dispatch-parent.

### Comments

#### radia — 2026-09-16T00:26:04.911Z
[code-rubric] PROCEED (Commit: 99067f07) config catalog clean

#### betty — 2026-09-16T00:21:26.844Z
`origin/sub/AST-1645/AST-1664-catalog-plain-text-writing-preferences-token` @ `99067f07` · catalog WP token tests

#### joan — 2026-09-16T00:13:01.138Z
[plan-rubric] PROCEED (Commit: 1beaa024e0fbe2db1a5922510df96930f99fca6e) Writing Preferences catalog plan

#### ada — 2026-09-16T00:11:00.254Z
`origin/sub/AST-1645/AST-1664-catalog-plain-text-writing-preferences-token` @ `1beaa024e0fbe2db1a5922510df96930f99fca6e` · plan ready

---

# Catalog + plain_text shape reuse + WRITING_PREFERENCES token

**Linear:** [AST-1664](https://linear.app/astralcareermatch/issue/AST-1664)
**Parent:** [AST-1645](https://linear.app/astralcareermatch/issue/AST-1645) — Migrate candidate_data.context.writing_preferences to use the artifact table
**Publish ref:** `sub/AST-1645/AST-1664-catalog-plain-text-writing-preferences-token`

Register `candidate.context.writing_preferences` in `ARTIFACT_CONFIG` reusing the existing `plain_text` body shape (AST-1632 — do not re-add the shape), flip `TOKEN_SOURCES["WRITING_PREFERENCES"]` to `source_type: "artifact"` with `artifact_key: "candidate.context.writing_preferences"`, widen closed-set / per-entry / artifact-token asserts, and drop Writing Preferences from the context-sibling freeze list. Config-only — no UI, hydrate, API intercept, or blob retirement (siblings AST-1665 / AST-1666). Copy the AST-1632 / AST-1651 catalog path.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/utils/config.py` — new catalog entry plus asserts; `TOKEN_SOURCES["WRITING_PREFERENCES"]` flip.

Every Files Changed row and every Stage step stays inside that one file. No `candidate.py`, no `api_candidate.py`, no React, no `database.py`, no other context keys, no new `artifact_shapes` entry (`plain_text` already exists), no `resolve_tokens` behavior change beyond what the typed registry already drives at import.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Register `candidate.context.writing_preferences` in `ARTIFACT_CONFIG` + closed-set / per-entry asserts; drop that key from the context sibling-freeze loop; flip `TOKEN_SOURCES["WRITING_PREFERENCES"]` to artifact + `artifact_key`; widen `_artifact_tokens` assert; update module docstring inventory | utils |

**Out of this ticket (do not touch):** operative `plain_text` validation / hydrate / library gate (sibling #2); API PUT intercept + GET hydrate; Writing Preferences ContextTextPage wiring (sibling #3); `ArtifactEditor`; `database.py`; other context leaves; `BUILD_CONFIG["artifact_shapes"]["plain_text"]` (already present); `tests/` / `docs/test-bible/**`.

## Stage 1: Writing Preferences catalog key + WRITING_PREFERENCES token

**Done when:** `import src.utils.config` succeeds; ticket AC1–AC3 one-liners exit 0; `backstory` / `ideal_day` remain absent from `ARTIFACT_CONFIG`; `_artifact_tokens` includes `WRITING_PREFERENCES` alongside the pre-existing artifact tokens.

1. In `src/utils/config.py` module docstring **Config sections:** list, update the existing `ARTIFACT_CONFIG` inventory line to include the Writing Preferences key (keep SoT wording and every key already listed; add AST-1664 citation):

```
  ARTIFACT_CONFIG — versioned artifact registry keyed by entity._data path (entity, candidate_scoped, body_shape, ingestion_owner); keys = candidate.artifacts.base_resume, job.artifacts.job_resume, job.artifacts.cover_letter, candidate.context.strengths, candidate.context.priorities, candidate.context.deal_breakers, candidate.context.bio_summary, candidate.context.writing_preferences; SoT in config — callers import ARTIFACT_CONFIG (AST-1573 / AST-1575 / AST-1576 / AST-1590 / AST-1632 / AST-1648 / AST-1651 / AST-1664)
```

2. Do **not** add or edit `BUILD_CONFIG["artifact_shapes"]["plain_text"]`. It must already equal `"raw_string"` from AST-1632. If it is missing at build time, stop and comment on parent AST-1645 — do not invent a second shape.

⚠️ **Decision:** Reuse the existing `plain_text` → `"raw_string"` sentinel. Parent Purpose and ticket Notes: copy Strengths guidelines; `plain_text` is already the proven shape. Adding a second shape or renaming would fail AC2.

3. In `ARTIFACT_CONFIG = { ... }`, keep every existing key unchanged and **add** immediately after `candidate.context.bio_summary` (last context leaf currently registered):

```python
    "candidate.context.writing_preferences": {
        "entity_type": "candidate",
        "candidate_scoped": True,
        # Name into BUILD_CONFIG["artifact_shapes"]["plain_text"] (raw string body).
        "body_shape": "plain_text",
        # Candidate owns first-row ingestion for Writing Preferences (UI/API operative save — sibling).
        "ingestion_owner": "candidate",
    },
```

⚠️ **Decision:** Metadata key set matches Strengths / Priorities / pilot (`entity_type`, `candidate_scoped`, `body_shape`, `ingestion_owner`) — no new catalog metadata fields. `ingestion_owner: "candidate"` matches parent Technical scope.

4. Replace the closed key-set assert with the unique set that includes Writing Preferences (and every key already registered on this tip — do not drop parallel-epic keys):

```python
assert set(ARTIFACT_CONFIG.keys()) == {
    "candidate.artifacts.base_resume",
    "job.artifacts.job_resume",
    "job.artifacts.cover_letter",
    "candidate.context.strengths",
    "candidate.context.priorities",
    "candidate.context.deal_breakers",
    "candidate.context.bio_summary",
    "candidate.context.writing_preferences",
}
```

⚠️ **Decision:** Parent/child AC4 text at define time listed priorities/deal_breakers as frozen siblings. Those keys (and bio_summary) already landed via their own epics on `origin/dev`. This ticket must **not** assert them absent and must **not** delete them. Sibling-freeze duty for AST-1664 is: remove `writing_preferences` from the absence loop; keep asserting `backstory` and `ideal_day` absent; register no other new context leaf.

5. Update the **context sibling freeze** loop: remove `"candidate.context.writing_preferences"` from the tuple; keep `backstory` and `ideal_day` frozen. Refresh the comment to cite this ticket:

```python
# Sibling context leaves stay out of the catalog until their own epics (parent AC8 / AST-1664).
# Writing Preferences registered above — no longer asserted absent.
# Priorities / Deal Breakers / Bio Summary registered by their own epics — not in this loop.
for _ctx_sibling in (
    "candidate.context.backstory",
    "candidate.context.ideal_day",
):
    assert _ctx_sibling not in ARTIFACT_CONFIG
```

Keep the existing job-blob sibling absence loop unchanged.

6. Immediately after the existing `_bs` (bio_summary) per-entry asserts (and before the finalize / JAR assert block), add Writing Preferences per-entry asserts mirroring `_st` / `_bs`:

```python
_wp = ARTIFACT_CONFIG["candidate.context.writing_preferences"]
assert _wp["entity_type"] == "candidate"
assert _wp["entity_type"] in ENTITY_TYPES
assert _wp["candidate_scoped"] is True
assert isinstance(_wp["candidate_scoped"], bool)
assert _wp["body_shape"] == "plain_text"
assert _wp["body_shape"] in BUILD_CONFIG["artifact_shapes"]
assert BUILD_CONFIG["artifact_shapes"]["plain_text"] == "raw_string"
assert _wp["ingestion_owner"] == "candidate"
assert set(_wp.keys()) == {
    "entity_type",
    "candidate_scoped",
    "body_shape",
    "ingestion_owner",
}
```

7. Flip `TOKEN_SOURCES["WRITING_PREFERENCES"]` from data_field to artifact. Replace the current one-liner (keep its existing location among context tokens — do not relocate the key) with:

```python
    "WRITING_PREFERENCES": {
        "source": "candidate",
        "path": "context.writing_preferences",
        "source_type": "artifact",
        "artifact_key": "candidate.context.writing_preferences",
    },
```

Keep `source` / `path` (hydrate overlay leaf for siblings; same pattern as `STRENGTHS` / `PRIORITIES` / `BASE_RESUME`). Do **not** add `serialize` — plain string, not resume section JSON.

⚠️ **Decision:** Leave remaining context tokens that are still `data_field` (`BACKSTORY`, `IDEAL_DAY`, …) as `data_field`. Only `WRITING_PREFERENCES` flips on this ticket. Pre-existing artifact tokens (`STRENGTHS`, `PRIORITIES`, `DEAL_BREAKERS`, `BIO_SUMMARY`, `BASE_RESUME`) stay as already typed.

8. Update the artifact-token closed-set assert near the bottom of the TOKEN_SOURCES block, and add explicit linkage asserts (same style as STRENGTHS / PRIORITIES):

```python
assert TOKEN_SOURCES["WRITING_PREFERENCES"]["source_type"] == "artifact"
assert TOKEN_SOURCES["WRITING_PREFERENCES"]["artifact_key"] == "candidate.context.writing_preferences"
_artifact_tokens = {
    name for name, spec in TOKEN_SOURCES.items() if spec["source_type"] == "artifact"
}
assert _artifact_tokens == {
    "BASE_RESUME",
    "STRENGTHS",
    "PRIORITIES",
    "DEAL_BREAKERS",
    "BIO_SUMMARY",
    "WRITING_PREFERENCES",
}
```

Place the two `WRITING_PREFERENCES` linkage asserts next to the existing per-token pairs (after `BIO_SUMMARY`); keep the `_artifact_tokens` computation where it already lives — only widen the expected set. The generic `for _token_name, _spec in TOKEN_SOURCES.items()` loop already requires `artifact_key in ARTIFACT_CONFIG` for artifact rows — do not duplicate that logic elsewhere.

9. Do **not** edit `resolve_tokens`, candidate operative save, API, or UI. Do **not** add logger calls in config (logging citations are id-only for this config-only slice — no new info/debug surfaces).

**Verify (hand):**

```bash
python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'candidate.context.writing_preferences' in ARTIFACT_CONFIG"
python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert ARTIFACT_CONFIG['candidate.context.writing_preferences']['body_shape']=='plain_text'"
python3 -c "from src.utils.config import TOKEN_SOURCES; s=TOKEN_SOURCES['WRITING_PREFERENCES']; assert s['source_type']=='artifact' and s['artifact_key']=='candidate.context.writing_preferences'"
python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'candidate.context.backstory' not in ARTIFACT_CONFIG and 'candidate.context.ideal_day' not in ARTIFACT_CONFIG"
```

## Execution contract

- Execute steps in order; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files, touch siblings' scopes, or invent catalog keys beyond `candidate.context.writing_preferences`.
- Do not re-add `plain_text` to `artifact_shapes` or change its `"raw_string"` sentinel.
- On ambiguity or drift — stop, comment on parent AST-1645 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 1 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `patt.artifact.manage-catalog` | pattern — read in full; register Writing Preferences; closed catalog |
| `astral.config.config-source-of-truth` | statute — catalog / shape / token live in config |
| `astral.standards.no-hardcoded-sets` | statute — closed key/shape membership via asserts |
| `stat.logging.info` | id-only — no new logging surface this ticket |
| `stat.logging.debug` | id-only — no new logging surface this ticket |

## Joan validate

```
[plan-rubric]
**Ticket:** AST-1664
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `sub/AST-1645/AST-1664-catalog-plain-text-writing-preferences-token` @ `1beaa024e0fbe2db1a5922510df96930f99fca6e`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.manage-catalog | A | | |
| astral.config.config-source-of-truth | A | | |
| astral.standards.no-hardcoded-sets | A | | |
| stat.logging.info | X | | config-only slice; no new info surfaces (Stage 1 §9) |
| stat.logging.debug | X | | config-only slice; no new debug surfaces (Stage 1 §9) |

## Traceability

AC1→S1§3-4; AC2→S1§2-3,6; AC3→S1§7-8; AC4→S1§5 — parent AC4–9 N/A (operative/hydrate/API/UI owned by AST-1665/AST-1666).

## Findings

### discuss

- **Stale child AC4 wording on Linear Description.** Ticket AC4 still reads “no priorities/deal_breakers/ideal_day/backstory keys,” but `priorities`, `deal_breakers`, and `bio_summary` already register on the ftr tip via parallel epics. Plan correctly narrows sibling-freeze duty to `backstory` / `ideal_day` absent, removes `writing_preferences` from the freeze loop, and verify one-liners match that interpretation (S1§5, Verify block). Recommend Archie amend child AC4 text to match plan Decision §4 — not a plan defect.

### R6 — Definition fidelity (checklist)

- Plan implements child **## Scope** only (`src/utils/config.py`); explicit scope gate present; no out-of-scope files in Files Changed or Stages.
- All four child acceptance criteria have concrete Stage 1 steps and hand-verify one-liners.
- Mirrors AST-1632 / AST-1651 catalog/token pattern: adds `candidate.context.writing_preferences`, removes it from sibling-freeze loop, reuses existing `plain_text` shape (correctly does **not** re-add `BUILD_CONFIG["artifact_shapes"]["plain_text"]`), flips `TOKEN_SOURCES["WRITING_PREFERENCES"]` with `source`/`path` retained like `STRENGTHS` / `PRIORITIES` / `BIO_SUMMARY`.
- Operative save, hydrate, API intercept, blob retirement, and UI correctly deferred to siblings per ticket boundaries.
- Self-assessment: `Confirm Chuckles estimate: 1 — agree` is honest for a single-file closed-assert change.
- Plan Discuss rounds completed: **0** (status Plan Ready).

context_tokens≈48000
```

## Review (build stub)

**Built:** `origin/sub/AST-1645/AST-1664-catalog-plain-text-writing-preferences-token` @ `427a4977097662eaed9694a9a042f920418e9e73`.

**Stages delivered:**
- Stage 1: `candidate.context.writing_preferences` catalog + `WRITING_PREFERENCES` artifact token — `427a4977097662eaed9694a9a042f920418e9e73`.

**Betty:** at **Code Complete** — cover ARTIFACT_CONFIG closed set + Writing Preferences metadata, context sibling freeze (`backstory` / `ideal_day` absent), `TOKEN_SOURCES["WRITING_PREFERENCES"]` artifact_key linkage, `_artifact_tokens` includes `WRITING_PREFERENCES`.

## Radia review

```
[code-rubric]
**Ticket:** AST-1664
**Publish ref:** `99067f07bf82c51839191bf6045e3881aac46a1e`
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.manage-catalog | A | | |
| astral.config.config-source-of-truth | A | | |
| astral.standards.no-hardcoded-sets | A | | |
| stat.logging.info | X | | |
| stat.logging.debug | X | | |

## Column diff vs plan stage

(aligned)

## Frame diff

- [ ] **Acceptance criteria (AC4):** Narrow sibling-freeze duty to `backstory` / `ideal_day` absent; `priorities`, `deal_breakers`, and `bio_summary` already register on the ftr tip via parallel epics — child Description AC4 still reads the define-time “no priorities/deal_breakers/…” wording Joan flagged at plan validate.

## Findings

### discuss

- **Publish-ref diff breadth vs ticket scope.** `origin/dev...origin/sub/AST-1645/AST-1664-catalog-plain-text-writing-preferences-token` is 8 files / ~941 lines: AST-1664 product work is confined to `src/utils/config.py` (+ plan doc), but `merge-tests(AST-1664)` also carries Betty commits for **AST-1659** (Ideal Day operative tests in `tests/component/core/test_candidate.py`, `tests/component/ui/api/test_api_candidate.py`, and bible) and **AST-1661** (Backstory catalog tests/bible). Expected `merge-tests` hygiene on a parallel epic, not AST-1664 product smuggling — but worth Chuckles noting at merge-child that the three-dot diff is wider than the child’s explicit scope gate.

- **Stale child AC4 on Linear Description** (carried from Joan plan validate): plan + verify one-liners correctly interpret sibling-freeze as `backstory` / `ideal_day` only; Linear Description checklist text still lags.

### advisory

- **Incidental closed-set cleanup:** diff removes a duplicate `"candidate.context.deal_breakers"` entry in the `ARTIFACT_CONFIG` keys assert (present on `origin/dev`); correct, unrelated to Writing Preferences registration.

## What's solid

- `src/utils/config.py` delivers Stage 1 verbatim: `candidate.context.writing_preferences` catalog entry (`plain_text` / `ingestion_owner: candidate`), sibling-freeze loop drops `writing_preferences` while keeping `backstory` / `ideal_day` absent, `WRITING_PREFERENCES` flips to `source_type: artifact` with `artifact_key` + widened `_artifact_tokens` closed set; module docstring inventory updated; no `artifact_shapes` re-add; no `resolve_tokens` / operative / API / UI edits.
- Mirrors AST-1632 / AST-1651 catalog-token path; `resolve_tokens` still resolves via retained `path` overlay (same as STRENGTHS / BIO_SUMMARY) until operative sibling lands.
- Betty manifest (`TestAst1664CatalogPlainTextWritingPreferencesToken` + revised AST-1590 / AST-1596 / sibling-freeze classes) matches the config delta; integration correctly none.

## Recommended actions

- Chuckles: append artifact, `docs(AST-1664): Radia review — clean`, post slim upshot, → **Review Posted** → datt **PROCEED** path to User Testing (no fix-now canon items).
- Archie (optional, non-blocking): amend child Description AC4 to match plan sibling-freeze interpretation.

context_tokens≈55000
```
