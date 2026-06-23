<!-- linear-archive: AST-517 archived 2026-06-15 -->

## Linear archive (AST-517)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-517/per-candidate-resume-structure-storage-and-craft-resume-base-candidate  
**Status at archive:** Done  
**Project:** Astral Candidate  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-477 — Candidate Resume Structure  
**Blocked by / blocks / related:** parent: AST-477; blocks: AST-519; blocks: AST-518

### Description

## What this implements

Persist a **candidate-owned section catalog** on the candidate record (extend `candidate_data.artifacts` per parent open Q1). Each section has stable id, display title, enabled flag, and order. Contact/header fields and accent color live on structure (not editable by job resume crafting agents; job_data stores snapshot contact for historical job resumes per parent Q4–Q5). Update `craft_resume_base` so the agent task response includes structure and content keys aligned to that catalog. New candidates get a sensible default structure; existing legacy `base_resume` keyed to global `base_resume_structure` is addressed by regeneration (no automated migration ticket — Susan Q3).

## Acceptance criteria

1. A test candidate can have a custom section list (e.g. three sections with custom titles) saved on their record.
2. A second candidate with a different section catalog does not affect the first.

## Boundaries

* Does **not** implement Base Resume Content UI tabs — sibling Katherine ticket.
* Does **not** change resume HTML builder merge logic — sibling Ada builder ticket.
* Does **not** implement full AST-300 job pipeline.
* Cover letter remains separate artifact shape (`Subject`, `Letter` per parent Q6) — only document contracts here if task schemas touch cover.

## Notes for planning

* Read `src/utils/config.py` `DATA_SHAPES`, `TASK_CONFIG["craft_resume_base"]`, `src/core/candidate.py` craft path.
* Deprecate or shim global `base_resume_structure` as driver for **persistence**; UI/builder siblings consume resolved per-candidate view.
* Align with AST-296 BUILD_CONFIG / AST-294 builder docs in `docs/features/artifacts/`.

## Git branch (authoritative)

Per **orientation-astral** § Branch law: parent `ftr/AST-477-candidate-resume-structure`, child `sub/AST-477/<child-segment>`. Created at dispatch.

### Comments

#### radia — 2026-05-28T23:28:11.134Z
**Diff:** `origin/dev...origin/sub/AST-477/AST-517-per-candidate-resume-structure-storage-and-craft-resume-base`

### Plan fidelity
- `RESUME_STRUCTURE_*` defaults, `craft_resume_base` schema `resume_structure` first, `normalize_resume_structure` / `resolve_resume_structure` / `split_craft_resume_base_payload`, and `parse_candidate_resume` dual-blob persist match the combined plan (Stages 1–4).
- `CANDIDATE_DATA_MODEL.md` documents `artifacts.resume_structure` vs `base_resume` content keys.
- Self-Assessment scope (`Single-Component`, config + core only) matches the diff footprint.

### ASTRAL_CODE_RULES
- **§2.1 / §1.4:** Section catalog and defaults live in `config.py`; core consumes constants — good.
- **§3.3:** `candidate.py` imports data + utils only; no UI/external — good.
- **§1.3 DRY:** Single default blob + shared normalize/resolve/split path — good.

### discuss
- **`resolve_resume_structure` (`candidate.py`):** `except ValueError: pass` on corrupt stored structure falls back to default (covered by `test_resolve_falls_back_to_default_when_invalid`). Intentional resilience, but no in-code note — add a one-line comment tying fallback to legacy/corrupt blob handling so D2 silent-failure rubric readers know it is bounded.
- **`tests/component/core/test_candidate.py` + `tests/component/utils/test_config.py`:** Publish ref includes `TestNormalizeCompanySearchTermsOnSave`, `TestCompanySearchTermsLines`, and config classes for **AST-513/480/492/507/504/505/506/508/510** without matching product code on this ref (manifest correctly narrows to `TestAst517*` only). Full-file pytest on this branch will fail collection or assertions — strip or move to owning tickets before prep-uat merge so `ftr/AST-477-*` stays green on broad runs.

### advisory
- **`split_craft_resume_base_payload`:** Missing/empty agent `resume_structure` → config default (plan Stage 3) — acceptable; ensure prompt authors know structure is required going forward.

#### betty — 2026-05-28T23:11:31.735Z
## QA test manifest (AST-517)

**Publish ref:** `origin/sub/AST-477/AST-517-per-candidate-resume-structure-storage-and-craft-resume-base` @ `4a18c97b`

**`docs/ASTRAL_TEST_BIBLE.md` shasum (publish ref):** `5a57fb23f766bd9d3e435bfb4f308b4f98dbbc36eab8e738d618de2f37545b6c`

Run from repo root on **`dev-ada`**, replay **`git merge origin/dev`** then **`git merge origin/sub/AST-477/AST-517-per-candidate-resume-structure-storage-and-craft-resume-base`** before **`test-astral`**.

1. `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst517ResumeStructureConfig`
2. `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestStringifyResponseSchema::test_builds_schema_example_envelope`
3. `./scripts/testing/run_component_tests.sh tests/component/core/test_candidate.py::TestAst517ResumeStructure`
4. `./scripts/testing/run_component_tests.sh tests/component/core/test_candidate.py::TestParseCandidateResume`
5. `./scripts/testing/run_component_tests.sh tests/component/core/test_candidate.py::TestParseCandidateResumeExtended`

**Coverage notes:** Revised **`TestParseCandidateResume`** mocks — **`craft_resume_base`** payloads must use known section ids + **`resume_structure`** (obsolete **`headline`** key dropped). **§7.13zl** in bible.

**Acceptance mapping:**
- AC1 custom section catalog persisted → **`TestAst517ResumeStructure::test_parse_persists_custom_structure_per_candidate`**
- AC2 candidate isolation → same test (independent **`resume_structure`** per row)

— Betty

#### ada — 2026-05-28T22:59:34.406Z
Plan doc: https://github.com/susansomerset/astral/blob/sub/AST-477/AST-517-per-candidate-resume-structure-storage-and-craft-resume-base/docs/features/candidate/ast-517-per-candidate-resume-structure-storage-and-craft-resume-base.md

**Self-Assessment**
- **Scope — Single-Component:** Config literals plus `candidate.py` parse/persist helpers and one model doc — no UI or builder.
- **Conf — Medium:** Clear patterns, but agents must return `resume_structure`; deep validation lives in normalize helpers, not agent.py.
- **Risk — Medium:** Wrong default section ids/orders would break downstream AST-518/519; isolated to candidate artifact JSON.

---

# AST-517 — Per-candidate resume structure storage and craft_resume_base

**Linear:** [AST-517](https://linear.app/astralcareermatch/issue/AST-517/per-candidate-resume-structure-storage-and-craft-resume-base-candidate)  
**Parent:** [AST-477](https://linear.app/astralcareermatch/issue/AST-477/candidate-resume-structure) — Candidate Resume Structure  
**Publish ref:** `origin/sub/AST-477/AST-517-per-candidate-resume-structure-storage-and-craft-resume-base`  
**Project:** Astral Candidate

## Summary

Persist a **candidate-owned resume section catalog** on the candidate record at `candidate_data.artifacts.resume_structure` (per parent AST-477 Q1). Each section has stable id, display title, enabled flag, order, and whether job-level resume agents may edit it. Accent color lives on structure (AST-477 Q5). Update `craft_resume_base` / `parse_candidate_resume` so agent responses include normalized structure plus content keys aligned to that catalog. New candidates receive a config default when structure is missing; legacy `base_resume.accent_color` and global `DATA_SHAPES["candidates"]["detail"]["base_resume_structure"]` remain as **read shims** only — not persistence drivers.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `RESUME_STRUCTURE_DEFAULT`, `RESUME_STRUCTURE_KNOWN_SECTION_IDS`, `RESUME_STRUCTURE_CONTACT_SECTION_IDS`; extend `TASK_CONFIG["craft_resume_base"]["response_schema"]` with `resume_structure`; comment deprecating global `base_resume_structure` as persistence source. | utils |
| `src/core/candidate.py` | Helpers: default/normalize/resolve structure; split agent payload into structure + content; update `parse_candidate_resume` persistence. | core |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Document `artifacts.resume_structure` blob and boundaries vs `artifacts.base_resume`. | docs |

**Out of scope (sibling tickets):** Base Resume Content UI tabs (AST-519 Katherine), builder merge (AST-518), full AST-300 pipeline, automated legacy migration (Susan Q3: regenerate base resume manually).

## Data contract — `artifacts.resume_structure`

Stored under `candidate_data.artifacts.resume_structure`:

```python
{
    "accent_color": "#1A1A2E",  # optional; must be in BUILD_CONFIG["accent_palette"] when set
    "sections": {
        "<section_id>": {
            "id": "<section_id>",           # same as dict key
            "title": "Human display title",
            "enabled": True,
            "order": 0,                     # int; lower renders first among body sections
            "job_agent_editable": False,    # False for contact/header trio per AST-477 Q4
        },
        ...
    },
}
```

**Section ids** must be keys in `RESUME_STRUCTURE_KNOWN_SECTION_IDS` (subset of resume keys in `BUILD_CONFIG["supported_sections"]`, excluding cover-letter logical sections). Sections dict is **id-keyed** (not an ordered list).

**Content** stays in `artifacts.base_resume` as `{section_id: str, ...}` string values only — no `accent_color` on `base_resume` after this ticket (read legacy `base_resume.accent_color` only in resolve helpers for candidates not yet regenerated).

⚠️ **Decision:** Contact/header fields (`candidate_name`, `candidate_title`, `candidate_contact_detail`) are **sections in the catalog** with `job_agent_editable: false`. Job agents still **snapshot** contact strings into `job_data.artifacts.resume_content` at job save time (AST-518 implements filtering/snapshot; this ticket defines the flags and structure shape they consume).

## Stage 1: Config defaults and craft_resume_base schema

**Done when:** `RESUME_STRUCTURE_DEFAULT` exists with all nine current resume section ids from `DATA_SHAPES["candidates"]["detail"]["base_resume_structure"]`, default titles matching today's labels, all `enabled: true`, orders matching legacy builder body order (contact trio order 0–2, then `professional_summary` … `technical_skills` as in `builder._RESUME_BODY_KEYS`), contact trio `job_agent_editable: false`, all other sections `job_agent_editable: true`. `TASK_CONFIG["craft_resume_base"]["response_schema"]` includes required `resume_structure` (`type: "dict"`) plus existing content string fields unchanged.

1. In `src/utils/config.py`, after `BUILD_CONFIG` (or adjacent resume constants), add:
   - `RESUME_STRUCTURE_KNOWN_SECTION_IDS`: tuple of allowed section id strings (resume body + header keys only).
   - `RESUME_STRUCTURE_CONTACT_SECTION_IDS`: `("candidate_name", "candidate_title", "candidate_contact_detail")`.
   - `RESUME_STRUCTURE_DEFAULT`: full default structure dict as specified above; `accent_color` omitted (builder/config palette default applies until user/agent sets one).
2. In `TASK_CONFIG["craft_resume_base"]["response_schema"]`, add `"resume_structure": {"type": "dict", "required": True}` as the **first** field entry (content keys remain the existing nine strings).
3. Add a comment above `DATA_SHAPES["candidates"]["detail"]["base_resume_structure"]` stating it is the **legacy global tab template** until AST-519 serves per-candidate structure; persistence authority is `artifacts.resume_structure`.

## Stage 2: Core helpers — normalize, resolve, split agent payload

**Done when:** Unit-callable functions exist in `candidate.py`; invalid structure raises `ValueError` with safe messages; resolve never returns empty sections.

1. In `src/core/candidate.py`, add module-level helpers (public functions first, then helpers per §1.3):
   - `default_resume_structure() -> dict` — returns deep copy of `RESUME_STRUCTURE_DEFAULT`.
   - `normalize_resume_structure(raw: dict) -> dict` — validate `sections` is a dict; each key ∈ `RESUME_STRUCTURE_KNOWN_SECTION_IDS`; required subfields `id`, `title`, `enabled`, `order`, `job_agent_editable`; coerce types; reject unknown ids; if `accent_color` present, require `#RRGGBB` uppercase and membership in `BUILD_CONFIG["accent_palette"]` (case-insensitive compare, store uppercase).
   - `resolve_resume_structure(candidate_data: dict) -> dict` — return normalized `artifacts.resume_structure` if present; else `default_resume_structure()` with legacy shim: if `artifacts.base_resume.accent_color` is valid hex, copy into resolved structure's `accent_color`.
   - `split_craft_resume_base_payload(parsed: dict) -> tuple[dict, dict]` — extract `resume_structure` from payload (or `{}`), normalize via `normalize_resume_structure` (on failure re-raise); build `content` dict containing only keys present in both payload and normalized structure's enabled section ids, string values only; strip `resume_structure` and non-content keys from content dict.
2. Do **not** import `ui` or `external`.

## Stage 3: Persist structure + content from craft_resume_base

**Done when:** `parse_candidate_resume` writes both blobs; existing success/error behavior unchanged; second candidate's structure does not affect first (acceptance criteria 1–2 satisfied by data isolation on separate candidate rows).

1. In `parse_candidate_resume`, after successful `do_task`, call `split_craft_resume_base_payload(parsed)`.
2. If payload omits `resume_structure` or it normalizes empty, use `default_resume_structure()` and proceed (no silent partial structure).
3. `database.save_candidate(candidate_id, candidate_data={"artifacts": {"resume_structure": structure, "base_resume": content}}, merge=True)` in one merge — replaces prior `base_resume` content keys from this run, does not wipe other artifact keys.
4. Leave `run_candidate_artifact_generation` return value unchanged (`parsed_response` still full agent payload for frontend review until AST-519); **do not** auto-save structure on generate-only POST — only `parse_candidate_resume` and explicit candidate data PUT paths persist structure in this ticket.

⚠️ **Decision:** Regenerate path only — no DB migration. Candidates without `resume_structure` resolve via `default_resume_structure()` + accent shim until Susan re-runs parse/generate.

## Stage 4: Document candidate_data model

**Done when:** `CANDIDATE_DATA_MODEL.md` lists `artifacts.resume_structure` with field table and notes that `base_resume` keys must match enabled section ids from structure.

1. In `docs/features/candidate/CANDIDATE_DATA_MODEL.md`, under **artifacts**, add `resume_structure` row and a short subsection describing the blob shape and relationship to `base_resume`.

## Self-Assessment

**Scope — `Single-Component`**  
Changes concentrate in `config.py` and `candidate.py` plus one doc file; no UI or builder edits in this ticket.

**Conf — `Medium`**  
Patterns are clear (config literals + candidate helpers), but agent prompt authors must start returning `resume_structure` — validation is shallow at agent layer and deep in `normalize_resume_structure`.

**Risk — `Medium`**  
Incorrect default ids or orders would break AST-518 builder filtering and Katherine's AST-519 UI; contained to candidate artifact JSON, not dispatch.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|-------|
| §1.3 DRY | Single `RESUME_STRUCTURE_DEFAULT`; resolve/split helpers reused by parse path. |
| §1.4 | Section ids and defaults in config; no magic id lists in core. |
| §2.1 Config | All catalogs and default structure in `config.py`. |
| §2.4 Batch | N/A — candidate not batch-processed. |
| §2.6 State machine | N/A — no new transitions. |
| §3.3 Imports | Core → data, utils only. |
| §3.5 Naming | snake_case helpers; `resume_structure` blob key. |

**Conflicts:** None blocking. Residual: global `DATA_SHAPES.base_resume_structure` remains until AST-519 — documented as legacy.

## Review

| Field | Value |
|-------|-------|
| Branch | `origin/sub/AST-477/AST-517-per-candidate-resume-structure-storage-and-craft-resume-base` |
| Status | Review Posted — Radia 2026-05-28 |

## Resolution

**Resolved:** 2026-05-28 (Ada)

| Radia item | Action |
|------------|--------|
| **fix-now** | None — plan fidelity and ASTRAL_CODE_RULES sign-off on publish ref @ `4a18c97b`. |
| **discuss** — `resolve_resume_structure` `ValueError` fallback | One-line comment in `candidate.py` tying bounded fallback to corrupt/legacy blob handling (test `test_resolve_falls_back_to_default_when_invalid`). |
| **discuss** — orphan cross-ticket test classes on publish ref | Deferred to Betty / **AST-519** prep-uat cleanup; Betty manifest narrows to `TestAst517*` only — not blocking this ticket. |
| **advisory** — missing agent `resume_structure` → default | Accepted; prompt authors must return structure going forward. |

**Publish ref:** `origin/sub/AST-477/AST-517-per-candidate-resume-structure-storage-and-craft-resume-base` · Betty manifest green · §9a clean.

## Execution contract

- Execute stages in order; one commit per stage on `dev-ada`, cherry-pick publish per build-astral.
- Do not edit `builder.py`, React artifacts pages, or job persist helpers in this ticket.
- Ambiguity on cover letter key rename (`Subject`/`Letter` vs `re_line`/`body`) — **stop and comment on AST-477**; out of scope here.
