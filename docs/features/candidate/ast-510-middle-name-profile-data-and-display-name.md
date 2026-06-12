# AST-510 — Middle name profile data and display name (Add Middle name to the candidate profile)

<!-- linear-archive: AST-510 archived 2026-06-03 -->

## Linear archive (AST-510)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-510/middle-name-profile-data-and-display-name-add-middle-name-to-the  
**Status at archive:** Canceled  
**Project:** Astral Candidate  
**Assignee:** Ada Lovelace  
**Priority / estimate:** No priority / —  
**Parent:** AST-509  
**Blocked by / blocks / related:** blocks AST-511

### Description

## What this implements

Add optional middle name to candidate profile storage and the product's display-name pipeline: register the field in the candidate data contract, expose it for prompt token resolution, and compose full name as `First Middle Last` (whole middle name, per Susan) when middle is set in resume and cover letter rendering.

## Acceptance criteria

1. A candidate profile can store a middle name value that round-trips through save and reload.
2. When middle name is set, generated resume and cover letter output that shows the candidate's name from profile includes the middle name in the full displayed name.
3. When middle name is empty, name display and existing first/last-only behavior match current production behavior.
4. Existing candidates without a middle name require no migration action to continue working.

## Boundaries

* Does not add Candidate Profile or Admin UI fields — sibling **Katherine** ticket.
* Does not auto-populate middle name from resume parsing.
* Does not change first/last required validation.

## Notes for planning

* Key: `profile.middle` (snake_case per `docs/features/candidate/CANDIDATE_DATA_MODEL.md`).
* Update DATA_SHAPES contact section field order: first → middle → last.
* Add `{$MIDDLE_NAME}` token alongside existing first/last tokens.
* Display format: full middle name, not abbreviated initial.

## Git branch (authoritative)

Per `orientation-astral` **§ Branch law**: parent `ftr/AST-509-add-middle-name-to-the-candidate-profile`, child `sub/AST-509/AST-510-middle-name-profile-data-and-display-name`. Created at **dispatch-linear**.

### Comments

#### Ada Lovelace — 2026-05-27T23:52:29.769Z

Plan: `docs/features/candidate/ast-510-middle-name-profile-data-and-display-name.md`

https://github.com/susansomerset/astral/blob/sub/AST-509/AST-510-middle-name-profile-data-and-display-name/docs/features/candidate/ast-510-middle-name-profile-data-and-display-name.md

**Self-Assessment**
- **Scope:** `scope-Single-Component` — config contract + formatting helper + builder name join + doc/tests only; UI is AST-511.
- **Conf:** `conf-high` — mirrors existing TOKEN_SOURCES / DATA_SHAPES / `_apply_profile_to_render_dict` patterns with explicit sibling boundaries.
- **Risk:** `risk-Medium` — name composition affects all profile-driven resume print headers; small diff but user-visible.

Three stages: (1) CANDIDATE_DATA_MODEL + DATA_SHAPES + MIDDLE_NAME token, (2) `profile_display_name` + builder, (3) component tests including merge round-trip.

#### Betty White — 2026-05-28T00:02:32.904Z

**Manifest** — run on `origin/sub/AST-509/AST-510-middle-name-profile-data-and-display-name` @ `3bdfee5a`

`docs/ASTRAL_TEST_BIBLE.md` shasum on publish ref: `fe345871f8ccfa9397dec920503517accc714e4e`

1. `./scripts/testing/run_component_tests.sh tests/component/utils/test_formatting.py::TestProfileDisplayName`
2. `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestGetTokens`
3. `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestResolveTokens::test_resolves_middle_name_token`
4. `./scripts/testing/run_component_tests.sh tests/component/utils/test_config.py::TestAst510MiddleNameConfig`
5. `./scripts/testing/run_component_tests.sh tests/component/core/test_builder.py::TestBuilderHelpers::test_applies_profile_middle_to_candidate_name`
6. `./scripts/testing/run_component_tests.sh tests/component/core/test_builder.py::TestBuilderHelpers::test_build_resume_from_job_emits_middle_name_in_html`
7. `./scripts/testing/run_component_tests.sh tests/component/core/test_candidate.py::TestAst510ProfileMiddleRoundTrip`

Or single narrowed run from bible §7.13zi:

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_formatting.py::TestProfileDisplayName \
  tests/component/utils/test_config.py::TestGetTokens \
  tests/component/utils/test_config.py::TestResolveTokens::test_resolves_middle_name_token \
  tests/component/utils/test_config.py::TestAst510MiddleNameConfig \
  tests/component/core/test_builder.py::TestBuilderHelpers::test_applies_profile_middle_to_candidate_name \
  tests/component/core/test_builder.py::TestBuilderHelpers::test_build_resume_from_job_emits_middle_name_in_html \
  tests/component/core/test_candidate.py::TestAst510ProfileMiddleRoundTrip
```

Coverage map: §7.13zi — `profile_display_name`, `MIDDLE_NAME` token, DATA_SHAPES field order, builder resume `<h1>`, `save_candidate_data` merge round-trip. No UI tests (AST-511 scope).

#### Radia Perlman — 2026-05-28T00:15:12.770Z

**Review** — `origin/dev...origin/sub/AST-509/AST-510-middle-name-profile-data-and-display-name`

### What's solid
- **Plan fidelity:** `profile.middle` in `DATA_SHAPES["candidates"]["detail"]["profile"]` (first → middle → last), `TOKEN_SOURCES["MIDDLE_NAME"]`, `CANDIDATE_DATA_MODEL.md` aligned; no Admin / `list.manage` scope.
- **§1.3 DRY:** single `profile_display_name` in `formatting.py`; builder uses it in `_apply_profile_to_render_dict` without duplicating join logic.
- **§2.1 config:** field and token only in `config.py` as documented.
- **§3.3 imports:** `formatting.py` has no config import; builder → utils import matches existing pattern.
- **Display semantics:** full middle name; whitespace-only middle skipped; empty profile preserves artifact `candidate_name` (guard unchanged).
- **Boundaries:** no UI, no migration, no cover-letter body rewrite (matches plan decision).
- **Tests:** helper, token resolution, shape field order, builder HTML, merge round-trip per bible §7.13zi.

### fix-now / discuss
None.

### Advisory
Doc commit on publish ref: `4ae0c804` — cherry-pick onto `dev-ada` if you want the plan review section locally.

**→ `resolve-astral`**

---

Implementation was built on publish ref `sub/AST-509/AST-510-middle-name-profile-data-and-display-name` but **never landed on `origin/dev`** — parent AST-509 canceled as pipeline proof-of-concept (2026-05-28).
