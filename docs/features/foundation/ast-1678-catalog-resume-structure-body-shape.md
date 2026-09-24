<!-- linear-archive: AST-1678 archived 2026-09-24 -->

## Linear archive (AST-1678)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1678/catalog-resume-structure-body-shape-move-candidate-dataartifactsresume  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** ada  
**Priority / estimate:** None / 2  
**Parent:** AST-1677 — Move candidate_data.artifacts.resume_structure to artifact table  
**Blocked by / blocks / related:** parent: AST-1677; blocks: AST-1679

### Description

## What this implements

Register `candidate.artifacts.resume_structure` in `ARTIFACT_CONFIG` and add the structure dict `body_shape` under `BUILD_CONFIG["artifact_shapes"]` with closed-set asserts. Does not wire operative save/hydrate or job drafting consumers (after this, #2/#3). No React.

## Citations

`patt.artifact.manage-catalog`; `astral.config.config-source-of-truth`; `astral.standards.no-hardcoded-sets`; `astral.standards.in-scope-only`

## Scope

`src/utils/config.py` — `ARTIFACT_CONFIG["candidate.artifacts.resume_structure"]` plus closed-set asserts; new `BUILD_CONFIG["artifact_shapes"]["resume_structure"]` (or equivalent named shape) for the structure dict contract; Persistence comment / any freeze-absent assert that still treats structure as non-catalog updated.

## Acceptance criteria

- [X] **Catalog key present** — `python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'candidate.artifacts.resume_structure' in ARTIFACT_CONFIG"` exits 0. Fail: KeyError/AssertionError or key absent.
- [X] **Body shape is structure, not resume_content/plain_text** — `python3 -c "from src.utils.config import ARTIFACT_CONFIG, BUILD_CONFIG; e=ARTIFACT_CONFIG['candidate.artifacts.resume_structure']; assert e['body_shape'] not in ('resume_content','plain_text','cover_letter'); assert e['body_shape'] in BUILD_CONFIG['artifact_shapes']"` exits 0. Fail: shape reused from body/letter/plain_text or missing from `artifact_shapes`.
- [X] **Scope fence** — `rg -n "candidate\.artifacts\.resume_structure" src/utils/config.py` shows the registration; no new `job.artifacts.resume_structure` (or other new catalog keys) appear in `ARTIFACT_CONFIG`. Fail: extra keys registered this epic.

## Boundaries

- [X] Does not own operative save/hydrate (#2) or job drafting consumer rewires (#3). Does not touch React.

## Notes for planning

Catalog-only; mirror AST-1661 / AST-1632 shape registration for a new `candidate.artifacts.*` key with a new body_shape (not plain_text).

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1677-move-resume-structure-artifact-table`, child `sub/AST-1677/AST-1678-catalog-resume-structure-body-shape`. Created at dispatch-parent.

## QA test manifest

1. Primary resume_structure catalog + shape + job fence: `tests/component/utils/test_config.py::TestAst1678CatalogResumeStructureBodyShape`
2. Revised ARTIFACT_CONFIG closed set: `tests/component/utils/test_config.py::TestAst1590JobArtifactCatalogKeys::test_artifact_config_has_pilot_and_job_keys`
3. Revised TOKEN_SOURCES typing + counts: `tests/component/utils/test_config.py::TestAst1596TokenCatalogSourceTypeTyping`
4. Tip-drift freeze/token revisions: `TestAst1632CatalogPlainTextStrengthsToken` · `TestAst1648CatalogBioSummaryTokenProfileNav` · `TestAst1651CatalogPlainTextPrioritiesToken` · `TestAst1654CatalogPlainTextDealBreakersToken` · `TestAst1658CatalogPlainTextIdealDayToken` · `TestAst1661CatalogPlainTextBackstoryToken` · `TestAst1664CatalogPlainTextWritingPreferencesToken`
5. Job sibling fence: `tests/component/utils/test_config.py::TestAst1602RetireJobBodyReplicaConfigAuthority::test_sibling_blobs_stay_out_of_artifact_config`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1678CatalogResumeStructureBodyShape \
  tests/component/utils/test_config.py::TestAst1590JobArtifactCatalogKeys::test_artifact_config_has_pilot_and_job_keys \
  tests/component/utils/test_config.py::TestAst1596TokenCatalogSourceTypeTyping \
  tests/component/utils/test_config.py::TestAst1632CatalogPlainTextStrengthsToken \
  tests/component/utils/test_config.py::TestAst1648CatalogBioSummaryTokenProfileNav \
  tests/component/utils/test_config.py::TestAst1651CatalogPlainTextPrioritiesToken \
  tests/component/utils/test_config.py::TestAst1654CatalogPlainTextDealBreakersToken \
  tests/component/utils/test_config.py::TestAst1658CatalogPlainTextIdealDayToken \
  tests/component/utils/test_config.py::TestAst1661CatalogPlainTextBackstoryToken \
  tests/component/utils/test_config.py::TestAst1664CatalogPlainTextWritingPreferencesToken \
  tests/component/utils/test_config.py::TestAst1602RetireJobBodyReplicaConfigAuthority::test_sibling_blobs_stay_out_of_artifact_config \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum (publish tip):**

* `docs/test-bible/utils/config.md` — `2ecf177f6998925b837826924c668a8f4b28d598  -`

### Comments

#### betty — 2026-09-16T17:03:33.676Z
[check-linear]
Squashed publish tip onto ftr — exactly one `merge-tests(AST-1678):`; kept `test`/`code`/`docs`/`resolve`; AST-1673/1674 still absent.
`origin/sub/AST-1677/AST-1678-catalog-resume-structure-body-shape` @ `07a7a21a1c57e1596d18d571c75e92261879dd29` · Ada reassigned.

#### chuckles — 2026-09-16T17:01:21.248Z
[merge-child] blocked: duplicate merge-tests(AST-1678) on sub — count=2 (amend on tests, one merge-tests only).

@Betty White — squash/amend on astral-tests so origin/sub/AST-1677/AST-1678-catalog-resume-structure-body-shape has exactly one merge-tests(AST-1678):; keep test(AST-1678): and product commits; reassign Ada when tip validates.

#### betty — 2026-09-16T16:59:37.932Z
[check-linear]
Republished tip with first-parent `test(AST-1678):` + single `merge-tests(AST-1678):` (reuses origin/tests `5ba62d8b` content; AST-1673/1674 still stripped).
`origin/sub/AST-1677/AST-1678-catalog-resume-structure-body-shape` @ `31823ce50d940bd1fd0ae0b00f8de1dbe4475041` · Ada reassigned — sync-child onto refreshed ftr then merge-child.

#### chuckles — 2026-09-16T16:57:49.993Z
[merge-child] blocked: validate-sub-log missing test(AST-1678): on publish tip (Betty's strip left merge-tests subject without the test() commit); also sub not stacked on refreshed origin/ftr/AST-1677-move-resume-structure-artifact-table after refresh-ftr.

@Betty White — republish tip with a real `test(AST-1678):` commit (content already in tree) + single `merge-tests(AST-1678):`.
@Ada Lovelace — after Betty, sync-child merge origin/ftr/AST-1677-move-resume-structure-artifact-table and republish so sub stacks on ftr.

#### betty — 2026-09-16T16:53:41.819Z
[check-linear]
Stripped AST-1673/AST-1674 test commits from publish tip; tree is AST-1678 product + config test/bible only.
`origin/sub/AST-1677/AST-1678-catalog-resume-structure-body-shape` @ `228b3fe9732c240855387f3ab4d60d92245ff8d9` · Ada reassigned for resolve-child §9a

#### ada — 2026-09-16T16:50:30.927Z
[qa-handoff]
@Betty White

Radia fix-now (Review Posted): AST-1670 sibling test commits are on this publish ref and must come off.

- Commits: `ac4ca9b7` `test(AST-1673)`, `5c9d57bd` `test(AST-1674)` (reachable via `merge-tests(AST-1678)` / origin/tests tip)
- Paths (~340 lines vs origin/dev): `tests/component/core/test_roster.py`, `tests/component/core/test_dispatcher.py`, `tests/component/data/database/test_dispatch_tasks.py`, `docs/test-bible/core/roster.md`
- Not on AST-1678 QA manifest or plan scope (config-only). Product `src/utils/config.py` slice is clean — Ada cannot strip test-tree paths.

Need: republish a clean tip on `origin/sub/AST-1677/AST-1678-catalog-resume-structure-body-shape` with only AST-1678 product + config test/bible rows (keep `fb8f265b` / `5ba62d8b` / config bible); land AST-1673/1674 on their own `origin/sub/AST-1670/...` refs. After cleanup, reassign Ada so resolve-child can re-run §9a and move to User Testing.

#### radia — 2026-09-16T16:49:22.709Z
[code-rubric] REVIEW (Commit: fb99d850) AST-1670 tests on branch

#### betty — 2026-09-16T16:44:40.638Z
`origin/sub/AST-1677/AST-1678-catalog-resume-structure-body-shape` @ `3ec9142a1a3dd266eea11710a8ae87146c60768b` · catalog tests ready

#### joan — 2026-09-16T16:31:49.884Z
[plan-rubric] PROCEED (Commit: 9155ada) config-only catalog slice

#### ada — 2026-09-16T16:28:43.687Z
`origin/sub/AST-1677/AST-1678-catalog-resume-structure-body-shape` @ `9155ada1e3bdf61e2c605f05b62da006dbbc5613` · catalog shape planned

---

# Catalog + resume_structure body shape

**Linear:** [AST-1678](https://linear.app/astralcareermatch/issue/AST-1678)
**Parent:** [AST-1677](https://linear.app/astralcareermatch/issue/AST-1677) — Move candidate_data.artifacts.resume_structure to artifact table
**Publish ref:** `sub/AST-1677/AST-1678-catalog-resume-structure-body-shape`

Register `candidate.artifacts.resume_structure` in `ARTIFACT_CONFIG` and add a new `BUILD_CONFIG["artifact_shapes"]["resume_structure"]` body-shape contract for the existing structure dict (sections catalog + optional accent), with closed-set / per-entry asserts and Persistence-comment / freeze updates so structure is no longer treated as non-catalog. Config-only — no operative save/hydrate, no job drafting consumers, no React. Mirror AST-1632 (new shape + catalog key) / AST-1661 guidelines for the catalog slice; body_shape must **not** be `resume_content`, `plain_text`, or `cover_letter`.

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/utils/config.py` — `ARTIFACT_CONFIG["candidate.artifacts.resume_structure"]` plus closed-set asserts; new `BUILD_CONFIG["artifact_shapes"]["resume_structure"]` (or equivalent named shape) for the structure dict contract; Persistence comment / any freeze-absent assert that still treats structure as non-catalog updated.

Every Files Changed row and every Stage step stays inside that one file. No `candidate.py`, no `agent.py`, no `api_candidate.py`, no `consult.py`, no `tracker.py`, no React, no `database.py`, no `TOKEN_SOURCES` flips, no other catalog keys, no operative validate/save/hydrate.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `resume_structure` to `BUILD_CONFIG["artifact_shapes"]`; register `candidate.artifacts.resume_structure` in `ARTIFACT_CONFIG` + closed-set / per-entry asserts; fence `job.artifacts.resume_structure` absent; update Persistence comment on `RESUME_STRUCTURE_*` block; update module docstring inventory | utils |

**Out of this ticket (do not touch):** operative structure validation / hydrate / library gate (sibling #2 AST-1679); craft/parse / agent craft-persist land (AST-1679); API PUT intercept + GET hydrate (AST-1679); job drafting `RESUME_SECTION_CATALOG` / tracker filter rewires (sibling #3 AST-1680); React; `database.py`; `TOKEN_SOURCES`; other `ARTIFACT_CONFIG` keys; `tests/` / `docs/test-bible/**`.

## Stage 1: `resume_structure` shape + catalog key

**Done when:** `import src.utils.config` succeeds; ticket AC1–AC3 one-liners exit 0; `job.artifacts.resume_structure` is absent from `ARTIFACT_CONFIG`; no other new catalog keys appear beyond the closed set that now includes `candidate.artifacts.resume_structure`.

1. In `src/utils/config.py` module docstring **Config sections:** list, update the existing `ARTIFACT_CONFIG` inventory line to include the resume_structure key (keep SoT wording; cite AST-1678 alongside prior catalog tickets; keep every already-registered key including `candidate.context.writing_preferences`):

```
  ARTIFACT_CONFIG — versioned artifact registry keyed by entity._data path (entity, candidate_scoped, body_shape, ingestion_owner); keys = candidate.artifacts.base_resume, candidate.artifacts.resume_structure, job.artifacts.job_resume, job.artifacts.cover_letter, candidate.context.strengths, candidate.context.priorities, candidate.context.deal_breakers, candidate.context.bio_summary, candidate.context.backstory, candidate.context.ideal_day, candidate.context.writing_preferences; SoT in config — callers import ARTIFACT_CONFIG (AST-1573 / AST-1575 / AST-1576 / AST-1590 / AST-1632 / AST-1648 / AST-1651 / AST-1654 / AST-1658 / AST-1661 / AST-1664 / AST-1678)
```

2. In `BUILD_CONFIG["artifact_shapes"]`, immediately after the existing `"plain_text": "raw_string"` entry (still inside the `artifact_shapes` dict), add:

```python
        # AST-1678: structure dict body — sections catalog + optional accent_color.
        # Value is NOT a field-keyed schema (unlike resume_content / cover_letter) and NOT plain_text.
        # Operative validation (sibling AST-1679) gates on body_shape == "resume_structure"
        # and reuses normalize_resume_structure — not shape.items().
        "resume_structure": "structure_dict",
```

⚠️ **Decision:** Shape key name is `resume_structure` (ticket preferred name). Shape value is the string sentinel `"structure_dict"`, mirroring AST-1632's `"plain_text": "raw_string"` pattern — membership (`"resume_structure" in BUILD_CONFIG["artifact_shapes"]`) is what AC2 / per-entry `body_shape in artifact_shapes` asserts need. Do **not** reuse `resume_content`, `plain_text`, or `cover_letter`. Do **not** embed `RESUME_STRUCTURE_DEFAULT` or a field map here; sibling #2 owns `normalize_resume_structure` / dict rules.

3. In `ARTIFACT_CONFIG = { ... }`, keep every existing key unchanged and **add** immediately after `candidate.artifacts.base_resume`:

```python
    "candidate.artifacts.resume_structure": {
        "entity_type": "candidate",
        "candidate_scoped": True,
        # Name into BUILD_CONFIG["artifact_shapes"]["resume_structure"] (structure dict contract).
        "body_shape": "resume_structure",
        # Candidate owns first-row ingestion for structure (UI/API operative save — sibling AST-1679).
        "ingestion_owner": "candidate",
    },
```

⚠️ **Decision:** Metadata key set matches the pilot / context leaves (`entity_type`, `candidate_scoped`, `body_shape`, `ingestion_owner`) — no new catalog metadata fields. `ingestion_owner: "candidate"` matches parent Technical scope and `base_resume` ownership for candidate-scoped UI content.

4. Replace the closed key-set assert with (exact membership — no extras):

```python
assert set(ARTIFACT_CONFIG.keys()) == {
    "candidate.artifacts.base_resume",
    "candidate.artifacts.resume_structure",
    "job.artifacts.job_resume",
    "job.artifacts.cover_letter",
    "candidate.context.strengths",
    "candidate.context.priorities",
    "candidate.context.deal_breakers",
    "candidate.context.bio_summary",
    "candidate.context.backstory",
    "candidate.context.ideal_day",
    "candidate.context.writing_preferences",
}
```

5. Extend the existing job-blob sibling absence loop so it also fences the job-side structure key (ticket AC3 / parent scope fence). Keep every existing sibling string; **add** `"job.artifacts.resume_structure"` to the tuple:

```python
# Sibling job blob keys stay out of the catalog (parent AC / AST-1590 AC2 / AST-1678 AC3).
for _sibling in (
    "notes",
    "resume_content",
    "proposed_answers",
    "application_responses",
    "job.artifacts.notes",
    "job.artifacts.resume_content",
    "job.artifacts.proposed_answers",
    "job.artifacts.application_responses",
    "job.artifacts.resume_structure",
):
    assert _sibling not in ARTIFACT_CONFIG
```

Leave the (currently empty) context-sibling freeze loop as-is — all listed context leaves are already cataloged; this ticket does not add or remove context keys.

6. Immediately after the existing `_br` per-entry asserts (and before `_jr = ...`), add resume_structure per-entry asserts mirroring `_br` / `_st` style:

```python
_rs = ARTIFACT_CONFIG["candidate.artifacts.resume_structure"]
assert _rs["entity_type"] == "candidate"
assert _rs["entity_type"] in ENTITY_TYPES
assert _rs["candidate_scoped"] is True
assert isinstance(_rs["candidate_scoped"], bool)
assert _rs["body_shape"] == "resume_structure"
assert _rs["body_shape"] not in ("resume_content", "plain_text", "cover_letter")
assert _rs["body_shape"] in BUILD_CONFIG["artifact_shapes"]
assert BUILD_CONFIG["artifact_shapes"]["resume_structure"] == "structure_dict"
assert _rs["ingestion_owner"] == "candidate"
assert set(_rs.keys()) == {
    "entity_type",
    "candidate_scoped",
    "body_shape",
    "ingestion_owner",
}
```

7. Update the Persistence comment immediately above `RESUME_STRUCTURE_CONTACT_SECTION_IDS` so it no longer reads as blob-only SoT. Replace:

```python
# Per-candidate resume section catalog (AST-517 / AST-1303).
# Persistence: artifacts.resume_structure. Extra ids are per-candidate;
# this list is not a closed extra catalog.
```

with:

```python
# Per-candidate resume section catalog (AST-517 / AST-1303).
# Persistence SoT after AST-1677 catalog cutover: candidate.artifacts.resume_structure
# (ARTIFACT_CONFIG — registered AST-1678). Library blob artifacts.resume_structure remains
# interim until sibling operative save/hydrate (AST-1679). Extra ids are per-candidate;
# this list is not a closed extra catalog.
```

Do **not** rename, move, or rewrite the `RESUME_STRUCTURE_*` constants / `RESUME_STRUCTURE_DEFAULT` themselves — only the Persistence comment.

8. Do **not** edit `save_candidate_data`, `normalize_resume_structure`, API, consult, tracker, agent craft-persist, or UI. Do **not** flip any `TOKEN_SOURCES` row. Do **not** add logger calls in config (no logging citations on this ticket's Canon Scope — config-only slice).

**Verify (hand):**

```bash
python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'candidate.artifacts.resume_structure' in ARTIFACT_CONFIG"
python3 -c "from src.utils.config import ARTIFACT_CONFIG, BUILD_CONFIG; e=ARTIFACT_CONFIG['candidate.artifacts.resume_structure']; assert e['body_shape'] not in ('resume_content','plain_text','cover_letter'); assert e['body_shape'] in BUILD_CONFIG['artifact_shapes']"
python3 -c "from src.utils.config import ARTIFACT_CONFIG; assert 'job.artifacts.resume_structure' not in ARTIFACT_CONFIG"
rg -n "candidate\.artifacts\.resume_structure" src/utils/config.py
```

## Execution contract

- Execute steps in order; one stage → one `code()` commit on the epic worktree, then push `origin/<publish-ref>`.
- Do not add files, touch siblings' scopes, or invent catalog keys beyond `candidate.artifacts.resume_structure`.
- Do not reuse `resume_content` / `plain_text` / `cover_letter` as this key's `body_shape`; do not invent a second structure shape name if `resume_structure` is already in `artifact_shapes`.
- On ambiguity or drift — stop, comment on parent AST-1677 with the Stage blocked template, wait.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Canon Scope (this ticket)

| Id | Role |
|----|------|
| `patt.artifact.manage-catalog` | pattern — read in full; register `candidate.artifacts.resume_structure`; closed catalog; blob retirement deferred to siblings |
| `astral.config.config-source-of-truth` | statute — catalog key + body_shape live in config |
| `astral.standards.no-hardcoded-sets` | statute — closed key/shape membership via asserts |
| `astral.standards.in-scope-only` | statute — resume_structure catalog slice only; no sibling surfaces |

## Joan validate

```
[plan-rubric]
**Ticket:** AST-1678
**Overall:** APPROVED
**Corpus:** fc0c368e59 · ticket ids not in clerk roster (resolved from worktree draft/statute paths)
**Publish ref:** sub/AST-1677/AST-1678-catalog-resume-structure-body-shape @ 9155ada1e3bdf61e2c605f05b62da006dbbc5613

## Canon scores

patt.artifact.manage-catalog | A | | Register half only: ARTIFACT_CONFIG entry, closed-set asserts, sibling fence; read/write/blob-retire explicitly deferred to AST-1679 per partitioned epic
astral.config.config-source-of-truth | A | | Catalog key + body_shape confined to src/utils/config.py BUILD_CONFIG/ARTIFACT_CONFIG
astral.standards.no-hardcoded-sets | A | | Closed key-set assert, per-entry _rs asserts, job.artifacts.resume_structure absence loop
astral.standards.in-scope-only | A | | Explicit scope gate; single file; operative/API/React/consult/tracker fenced out

## Traceability

AC1→Stage 1 §2-4,8 verify; AC2→Stage 1 §2,6,8 verify; AC3→Stage 1 §4-5,8 verify | Parent functional scope §1 (catalog resume_structure) + parent AC1/2/9 via child slice only; parent AC3-8 N/A (siblings AST-1679/AST-1680)

## Findings

### acceptable — canon infrastructure
- **Location:** canon_clerk roster
- **Finding:** Ticket's four cited ids are not in `canon/directives/active/` yet; expand fails; bodies read from draft/statute paths in worktree.
- **Recommendation:** No plan change; clerk migration is out of AST-1678 scope. Scores based on resolved directive text.

context_tokens≈28000
```

## Review (build stub)

**Built:** `origin/sub/AST-1677/AST-1678-catalog-resume-structure-body-shape` @ `fb8f265bc7b03e828dff1c9a76093b7e281b4a86`.

**Stages delivered:**
- Stage 1: `BUILD_CONFIG["artifact_shapes"]["resume_structure"]` sentinel (`structure_dict`) + `ARTIFACT_CONFIG["candidate.artifacts.resume_structure"]` registration; closed-set / per-entry asserts; `job.artifacts.resume_structure` fence; Persistence comment update.

**Betty:** at **Code Complete** — cover ARTIFACT_CONFIG closed set includes `candidate.artifacts.resume_structure`; body_shape is `resume_structure` (not resume_content/plain_text/cover_letter) and in artifact_shapes; `job.artifacts.resume_structure` absent; shape sentinel `structure_dict`.

## Radia review

```
[code-rubric]
**Ticket:** AST-1678
**Publish ref:** fb99d85089595bdfc720a0ee8aa66702b9cbe2b6
**Corpus:** fc0c368e59 · ticket ids not in `canon_clerk` active roster (bodies resolved from `canon/statutes/` + `canon/directives/draft/` per Joan)
**Overall:** FIX-NOW

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.manage-catalog | A | | |
| astral.config.config-source-of-truth | A | | |
| astral.standards.no-hardcoded-sets | A | | |
| astral.standards.in-scope-only | D | 2 | `tests/component/core/*`, `test_dispatch_tasks.py`, `docs/test-bible/core/roster.md` carry AST-1673/AST-1674 commits |

## Column diff vs plan stage

- `astral.standards.in-scope-only`: Joan **A** → Radia **D** — plan fenced single-file catalog slice; publish ref includes two AST-1670-child test commits (~340 lines) not on this ticket's QA manifest

## Frame diff

(none)

## Findings

### fix-now

- **Location:** `origin/sub/AST-1677/AST-1678-catalog-resume-structure-body-shape` commits `ac4ca9b7`, `5c9d57bd`
- **Finding:** AST-1670 sibling work (`test(AST-1673)`, `test(AST-1674)`) landed on the AST-1678 publish ref before the catalog code commit. Touches `tests/component/core/test_roster.py`, `test_dispatcher.py`, `tests/component/data/database/test_dispatch_tasks.py`, and `docs/test-bible/core/roster.md` (AST-1673/1674 sections). None of this is in AST-1678's QA manifest or plan scope gate.
- **Recommendation:** Revert or strip those two commits from the sub branch; land AST-1673/1674 on their own `origin/sub/AST-1670/...` refs. Replay only AST-1678 commits (`fb8f265b` catalog code, `5ba62d8b` tests, docs/bible for config).

### advisory

- **Location:** `canon/canon_clerk.py expand`
- **Finding:** All four frozen ids fail clerk expand (`unknown directive id`). Joan and this review resolved from statute/draft paths — scores are reproducible at `fc0c368e59` but not via the supported expand path until clerk migration lands.
- **Recommendation:** No AST-1678 product change; track clerk roster migration separately (out of ticket scope).

## What's solid

- **Product slice is clean:** `src/utils/config.py` is the only `src/` file in the diff; matches Stage 1 plan exactly.
- `BUILD_CONFIG["artifact_shapes"]["resume_structure"] = "structure_dict"` with AST-1678 comments.
- `ARTIFACT_CONFIG["candidate.artifacts.resume_structure"]` metadata matches pilot pattern (`entity_type`, `candidate_scoped`, `body_shape: resume_structure`, `ingestion_owner: candidate`).
- Closed key-set assert, `_rs` per-entry asserts, `job.artifacts.resume_structure` sibling fence, Persistence comment update — all per plan.
- `TestAst1678CatalogResumeStructureBodyShape` covers shape sentinel, catalog metadata, and job-side absence.
- Betty manifest tip-drift revisions in `test_config.py` (BACKSTORY/IDEAL_DAY artifact tokens, empty `_CTX_SIBLINGS`) align with merged tip and manifest lines 3–4.

## Recommended actions (for Chuckles / resolve-child — not Radia)

1. **Branch hygiene:** Remove `ac4ca9b7` + `5c9d57bd` from `sub/AST-1677/AST-1678-catalog-resume-structure-body-shape`; republish tip.
2. **Re-run manifest** after cleanup to confirm green on AST-1678 lines only.
3. **Proceed on catalog substance** once branch contains only AST-1678 product + config test/bible rows — no resolve-child product edits expected for the config slice itself.

---

**Slim Linear upshot (Chuckles posts via `linear_proxy --as radia`):**

```
[code-rubric] REVIEW (Commit: fb99d850) AST-1670 tests on branch
```

context_tokens≈38000
```

## Resolution

**Date:** 2026-09-16  
**Tip:** `origin/sub/AST-1677/AST-1678-catalog-resume-structure-body-shape` @ `228b3fe9732c240855387f3ab4d60d92245ff8d9` (Betty clean republish after `[qa-handoff]`).

| Finding | Action |
|---------|--------|
| **fix-now** — AST-1673/AST-1674 test commits on publish ref | Betty stripped them; tip tree is AST-1678 product (`fb8f265b`) + config test/bible (`70d1350a` / `5ba62d8b`) + Radia review docs only. `ac4ca9b7` / `5c9d57bd` not ancestors of tip. No product code change this resolve. |
| **advisory** — canon_clerk expand | No change (out of ticket scope). |

**§9a:** dry-run merge into `origin/dev` clean; dry-run into `origin/ftr/AST-1677-move-resume-structure-artifact-table` clean.
