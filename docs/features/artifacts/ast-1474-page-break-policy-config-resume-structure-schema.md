# AST-1474 — Page-break policy config and resume_structure schema

**Linear:** [AST-1474](https://linear.app/astralcareermatch/issue/AST-1474)
**Parent:** [AST-1462](https://linear.app/astralcareermatch/issue/AST-1462) — Create and position page break
**Publish ref:** `sub/AST-1462/AST-1474-page-break-policy-config-resume-structure-schema`

Adds config-owned page-break policy tokens with keep-block-together as the default for every known (and extra) structure section; extends `normalize_resume_structure` / `RESUME_STRUCTURE_DEFAULT` / GET `/resume_structure` catalog so sections persist and expose `page_break_policy`. Does **not** emit print CSS (AST-1475) or build React controls (AST-1476).

## Scope gate

Ticket **## Scope** covers only:

- `src/utils/config.py` — allowed tokens, keep-together default map, catalog literals
- `src/core/candidate.py` — validate / normalize / default the new field
- `src/ui/api/api_candidate.py` — catalog payload for policies

Every file and change kind below matches that Scope. Out of scope: `builder.py`, React, `BUILD_CONFIG["supported_sections"][*]["page_break_policy"]` rewrites, tests/bible.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `RESUME_STRUCTURE_PAGE_BREAK_*` tokens, labels, default, per-known-id default map; set `page_break_policy` on every `RESUME_STRUCTURE_DEFAULT` section | utils |
| `src/core/candidate.py` | Import new config names; coerce/validate `page_break_policy` in `normalize_resume_structure`; default on hydrate/ingest append helpers | core |
| `src/ui/api/api_candidate.py` | Import new config names; add policy fields to GET catalog; include `page_break_policy` on each `all_sections` row | ui |

## Decisions (binding)

⚠️ **Decision:** Field name is `page_break_policy` (same key already used under `BUILD_CONFIG["supported_sections"]`) so structure rows, catalog, and later builder emit share one name.

⚠️ **Decision:** Operator-allowed token set is exactly three strings (parent Functional scope: flow / new page before / keep together):

| Token | Meaning |
|-------|---------|
| `normal` | Flow uninterrupted across pages |
| `page_break_before` | Force a new printed page before this section |
| `avoid_split` | Keep this section block together |

Default for **every** section (known + extra) when absent or when writing `RESUME_STRUCTURE_DEFAULT` is **`avoid_split`**. Do **not** copy the mixed `BUILD_CONFIG["supported_sections"]` policies into structure defaults (those still include `keep_with_next` / `normal` and are not this epic’s operator contract).

⚠️ **Decision:** Do **not** add `keep_with_next` to the structure allowed set. It remains a `BUILD_CONFIG` literal only. Structure persistence / catalog / normalize accept only the three tokens above. AST-1475 maps those three to print CSS; it does not need `keep_with_next` on structure rows.

⚠️ **Decision:** Do **not** edit `BUILD_CONFIG["supported_sections"][*]["page_break_policy"]` in this ticket. Legacy builder hard-code `#prior-experience { page-break-before: always }` and BUILD_CONFIG emit hints are AST-1475.

⚠️ **Decision:** Catalog exposes both a flat token list and human labels (config-owned) so AST-1476 does not hardcode enum strings or display copy (`astral.standards.no-hardcoded-sets` / `astral.layers.ui-config-driven-business-logic`).

## Stage 1: Config catalog literals

**Done when:** `RESUME_STRUCTURE_*` page-break constants exist next to the existing structure catalog in `config.py`; every section in `RESUME_STRUCTURE_DEFAULT["sections"]` carries `"page_break_policy": "avoid_split"`; no product callers required yet.

1. In `src/utils/config.py`, immediately after `RESUME_STRUCTURE_BODY_FORMATS` (before `RESUME_STRUCTURE_DEFAULT_FORMAT_BY_ID` is fine; keep the page-break block contiguous with other `RESUME_STRUCTURE_*` names), add:

```python
RESUME_STRUCTURE_PAGE_BREAK_POLICIES = (
    "normal",
    "page_break_before",
    "avoid_split",
)
RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT = "avoid_split"
RESUME_STRUCTURE_PAGE_BREAK_POLICY_LABELS = {
    "normal": "Flow uninterrupted",
    "page_break_before": "New page before",
    "avoid_split": "Keep block together",
}
```

2. After `RESUME_STRUCTURE_KNOWN_SECTION_IDS` is defined, add the keep-together default map (every known id → default):

```python
RESUME_STRUCTURE_PAGE_BREAK_DEFAULT_BY_ID = {
    sid: RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT
    for sid in RESUME_STRUCTURE_KNOWN_SECTION_IDS
}
```

3. In `RESUME_STRUCTURE_DEFAULT["sections"]`, add `"page_break_policy": RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT` to **every** section dict (contact + body + historical optional — all eleven rows).

4. Do **not** change `BUILD_CONFIG`, `DATA_SHAPES`, craft schemas, or any other config family.

## Stage 2: Normalize / default in candidate.py

**Done when:** `normalize_resume_structure` always writes a validated `page_break_policy` on each section row; missing/blank → default; unknown token → `ValueError`; hydrate and legacy-ingest append helpers stamp the default so GET never returns a section without the field.

1. In `src/core/candidate.py` imports from `src.utils.config`, add:
   - `RESUME_STRUCTURE_PAGE_BREAK_POLICIES`
   - `RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT`
   - (import `RESUME_STRUCTURE_PAGE_BREAK_DEFAULT_BY_ID` only if a step below uses it; prefer the single default constant for coerce)

2. In `normalize_resume_structure`, after `format` handling and before `out["sections"][sid] = row`, resolve policy:

   - Read `raw_policy = spec.get("page_break_policy")`.
   - If `raw_policy` is `None` or a blank string (after strip when `str`): set `policy = RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT`.
   - Else require `isinstance(raw_policy, str)` and `raw_policy in RESUME_STRUCTURE_PAGE_BREAK_POLICIES`; otherwise raise `ValueError` with a message naming the section id and listing `list(RESUME_STRUCTURE_PAGE_BREAK_POLICIES)` (same style as the format error).
   - Set `row["page_break_policy"] = policy`.
   - Apply for **all** section ids including contact and extras (no contact skip).

3. In `ingest_legacy_label_content_base_resume` → `_append_missing_section`, when building the new section dict, include `"page_break_policy": RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT` alongside `format`.

4. In `hydrate_resume_structure_from_base_resume` → `_append_missing`, when building `row`, include `"page_break_policy": RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT`.

5. Optional harden (same stage, same file): in hydrate, after `_fix_body_format` (or inside `_ensure_sid` when the section already exists), if `spec.get("page_break_policy")` is missing/blank/not in the allowed tuple, set `spec["page_break_policy"] = RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT` so read-only hydrate of pre-epic blobs shows keep-together without requiring Save. Do **not** call `normalize_resume_structure` from hydrate (hydrate stays non-raising for display).

6. Do **not** change `prepare_resume_structure_sections_for_save` beyond what already `dict(spec)`-copies — Save continues to pass the field through; normalize on the PUT path remains the validator.

7. Do **not** edit `builder.py`, tracker emit, or React.

## Stage 3: GET catalog + all_sections payload

**Done when:** `GET /api/candidates/<id>/resume_structure` returns catalog page-break fields and each `all_sections[]` row includes the section’s resolved `page_break_policy` string.

1. In `src/ui/api/api_candidate.py`, import:
   - `RESUME_STRUCTURE_PAGE_BREAK_POLICIES`
   - `RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT`
   - `RESUME_STRUCTURE_PAGE_BREAK_POLICY_LABELS`
   - `RESUME_STRUCTURE_PAGE_BREAK_DEFAULT_BY_ID`

2. In `get_candidate_resume_structure`, extend the `catalog` dict with exactly:

```python
"page_break_policies": list(RESUME_STRUCTURE_PAGE_BREAK_POLICIES),
"page_break_policy_labels": dict(RESUME_STRUCTURE_PAGE_BREAK_POLICY_LABELS),
"page_break_policy_default": RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT,
"page_break_policy_defaults": dict(RESUME_STRUCTURE_PAGE_BREAK_DEFAULT_BY_ID),
```

3. In the `all_sections.append({...})` loop, add:

```python
"page_break_policy": (
    spec["page_break_policy"]
    if isinstance(spec.get("page_break_policy"), str)
    and spec["page_break_policy"] in RESUME_STRUCTURE_PAGE_BREAK_POLICIES
    else RESUME_STRUCTURE_PAGE_BREAK_POLICY_DEFAULT
),
```

4. Do **not** add new routes. Do **not** change PUT merge logic beyond what already runs `normalize_resume_structure` on `arts["resume_structure"]` (that path already persists whatever normalize writes, including the new field).

## Out of scope (siblings)

| Sibling | Owns |
|---------|------|
| AST-1475 (Hedy) | `builder.py` print `@media` from structure policies; `.role` keep-together; gate `#prior-experience` always-break |
| AST-1476 (Katherine) | ArtifactEditor / ResumeStructureEditor / JAR dropdown + Save UX |

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1474
**Overall:** APPROVED
**Publish ref:** `sub/AST-1462/AST-1474-page-break-policy-config-resume-structure-schema` @ `56eecd88`

## Traceability
AC1→Stages 1–2 (config `avoid_split` on all `RESUME_STRUCTURE_DEFAULT` rows + normalize coerce); AC2→Stages 2–3 (persist via normalize on PUT + GET `catalog`/`all_sections`); parent AC2/3/5/6 and end-to-end print CSS→siblings N/A for this child's Scope.

## Findings

### discuss — Missing `## Self-assessment`
- **Location:** plan doc (after `## Estimate`)
- **Finding:** No self-assessment / confidence block; other artifact plans carry one.
- **Recommendation:** Optional add before build — low risk here because stages, scope gate, and binding Decisions are already explicit.

### discuss — Child AC1 names print CSS
- **Location:** ticket AC1 vs plan Out of scope
- **Finding:** AC1 text says “in print CSS”; this slice delivers schema/defaults only; print emit is AST-1475.
- **Recommendation:** Ada should treat AC1 as satisfied at this layer when defaults persist `avoid_split` everywhere including `prior_experience`; full AC1 UAT waits on Hedy.

### acceptable — Hydrate soft-default vs normalize strict-validate
- **Location:** Stage 2 step 5
- **Finding:** Hydrate may silently stamp default policy for legacy blobs; PUT/Save still validates via `normalize_resume_structure`.
- **Recommendation:** Matches stated intent for read-only display of pre-epic data.

context_tokens≈18500

## Review

- **Publish ref:** `sub/AST-1462/AST-1474-page-break-policy-config-resume-structure-schema`
- **Tip:** `7c53225a`
- **Files:** `src/utils/config.py`, `src/core/candidate.py`, `src/ui/api/api_candidate.py`

## Radia review

# Radia review — AST-1474

`[code-rubric] revision=2`  
**Rubric:** code-rubric.v2  
**Ticket:** AST-1474  
**Publish ref:** `sub/AST-1462/AST-1474-page-break-policy-config-resume-structure-schema` @ `f150166d`  
**Overall:** FIX-NOW

---

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | No agent prompt/confidence-surface edits in AST-1474 slice; sibling agent.py churn is out-of-scope contamination |
| astral.agent.do-task-delegation | scoped | not-applicable | AST-1474 slice does not touch do_task delegation; sibling dispatch edits are contamination |
| astral.agent.grade-vector-validation | scoped | not-applicable | No rubric-vector validation changes in AST-1474 slice |
| astral.batch.batch-id-first | scoped | not-applicable | No batch-id claim path edits in AST-1474 slice |
| astral.batch.batch-id-format | scoped | not-applicable | No batch-id format changes |
| astral.batch.claim-process-release | scoped | not-applicable | AST-1474 slice does not edit claim/release helpers |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | No entity-agent-responses column/lookup changes in slice |
| astral.config.config-source-of-truth | scoped | conforms | `RESUME_STRUCTURE_PAGE_BREAK_*` literals live in `config.py` as planned |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | No env/secret lookups added |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | No debug artifact paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | No spike files |
| astral.dispatch.seed-auto-false | scoped | not-applicable | No seed/dispatch-task seeding in slice |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | AST-1474 slice does not touch run_next; sibling candidate dispatch edits are contamination |
| astral.docs.features-single-file-per-ticket | scoped | conforms | Plan doc path matches ticket slug |
| astral.git.betty-no-src-or-features | scoped | not-applicable | Radia read-only |
| astral.git.engineer-test-tree-ban | scoped | not-applicable | Radia read-only |
| astral.layers.core-vs-external-bright-line | scoped | conforms | AST-1474 slice stays core/utils/ui-api; no external imports |
| astral.layers.import-direction | scoped | conforms | `api_candidate.py` imports config from utils only; `candidate.py` imports config constants at module top |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | No `scripts/**` changes |
| astral.layers.ui-config-driven-business-logic | scoped | conforms | GET catalog exposes policy tokens/labels/defaults for AST-1476 — no React hardcoding |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | No coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | No consult/render paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | AST-1474 slice does not add routes; sibling auth churn is contamination |
| astral.seed.agent-tables-in-repo-json | scoped | not-applicable | No seed JSON edits in slice |
| astral.seed.archie-catalog-wins | scoped | not-applicable | No seed catalog conflicts in slice |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | No boot/seed hot-path edits |
| astral.seed.define-approved | scoped | not-applicable | No define/seed work |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | No seed row resurrection |
| astral.seed.other-via-coverage-join | scoped | not-applicable | No coverage-join seed logic |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | AST-1474 slice does not touch data layer |
| astral.standards.database-header-inventory | scoped | not-applicable | AST-1474 slice does not touch `database.py` |
| astral.standards.debug-contract-gated | scoped | not-applicable | No new `debug=` emission in slice |
| astral.standards.dry-and-focused-functions | scoped | conforms | AST-1474 helpers (`_fill_page_break_policy`) are localized; sibling duplicate import is contamination |
| astral.standards.in-scope-only | scoped | violates | Publish-ref tip diff touches 43 `src/**` files; plan Scope gate allows 3 |
| astral.standards.logging-via-utils | scoped | conforms | AST-1474 slice adds no `print()` / raw logging |
| astral.standards.names-not-ticket-ids | scoped | conforms | Config symbols are domain-named, not ticket-prefixed |
| astral.standards.no-cross-contamination | scoped | conforms | AST-1474 slice imports stay inside layered `src/` tree |
| astral.standards.no-hardcoded-sets | scoped | conforms | Policy tuple + labels in `config.py`; normalize validates against config tuple |
| astral.standards.public-then-helpers | scoped | conforms | New constants precede use sites; hydrate helper is nested appropriately |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | No utils→data late imports in slice |
| astral.state.core-decides-transitions | scoped | not-applicable | AST-1474 slice does not edit state transitions |
| astral.state.job-prior-states-enforced | scoped | not-applicable | Job state machine untouched in slice |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | AST-1474 slice does not touch dispatch runners |
| astral.ui.frontend-file-placement | scoped | not-applicable | AST-1474 slice has no frontend files; sibling React edits are contamination |
| astral.ui.naming-conventions | scoped | conforms | New config keys follow existing `RESUME_STRUCTURE_*` naming |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | No server worker config changes in slice |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1474)` present at tip |
| orch.git.commit-vocabulary | universal | conforms | Commits use `code`/`test`/`docs`/`merge-tests` vocabulary |
| orch.git.flow-direction-inviolable | universal | violates | `sync(publish-ref)` pulled `origin/sub/AST-1464/AST-1477-*` and `AST-1478-*` onto AST-1462 child ref |
| orch.git.ftr-sub-topology | universal | violates | Wrong-parent sibling product+test code on `sub/AST-1462/AST-1474-*` publish ref |
| orch.git.merge-on-checkout | universal | conforms | `sync(dev)` commit present; merge-base warning noted under discuss |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | No evidence of cherry-pick/rebase/force on reviewed ref |
| orch.git.no-dev-agent-branches | universal | conforms | Publish ref follows `sub/<parent>/<child>-<slug>` |
| orch.git.one-epic-worktree-per-parent | universal | conforms | Review run from `astral-AST-1462` worktree |
| orch.git.three-permanent-branches | universal | conforms | Diff anchored to `origin/dev` baseline |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | No unresolved product-policy fork in AST-1474 slice |
| orch.pipeline.plan-is-bible | universal | violates | Plan Scope gate = 3 files; branch tip includes Jobs UI (1477/1478), dispatch, auth, admin, builder |
| orch.pipeline.project-scoped-queues | universal | conforms | Single-ticket review invocation |
| orch.pipeline.status-gates-skill-entry | universal | conforms | Spawn at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | No statute corpus edits |
| orch.roles.betty-owns-test-tree | universal | conforms | Tests landed via `test`/`merge-tests` commits, not engineer src edits |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | N/A to code diff |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada remains assignee at Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | Radia read-only |

**Notes:** Joan plan-rubric verdict attached (APPROVED @ `56eecd88`); no `## Considered and excluded` / Excluded statute list in attachment — straggler check N/A.

---

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| *(none cited)* | — | Plan and parent Architectural definition cite no catalog patterns |

---

## Plan adherence

**AST-1474 isolated commit (`7c53225a`, +71 lines, 3 files)** matches Stages 1–3 and all binding Decisions:

- `RESUME_STRUCTURE_PAGE_BREAK_POLICIES` / labels / default / per-id map in `config.py`
- `avoid_split` on all eleven `RESUME_STRUCTURE_DEFAULT` sections including `prior_experience`
- `normalize_resume_structure` coerce/validate with `ValueError` on bad tokens
- Legacy ingest + hydrate append stamp default; hydrate `_fill_page_break_policy` soft-defaults pre-epic blobs with in-code comment
- GET `/resume_structure` catalog + `all_sections[].page_break_policy` per plan
- `BUILD_CONFIG["supported_sections"]` untouched; no `builder.py` / React in slice
- Estimate **2** fits the isolated footprint

**Publish-ref tip (`f150166d`) does not adhere:** `sync(publish-ref)` commits merged AST-1464 siblings AST-1477 and AST-1478 (product + tests) onto this AST-1462 child branch. Three-dot diff vs `origin/dev` reports **43 `src/**` files** (+1610/−423 lines) and merge-base warning (`multiple merge bases, using 0fa5bc81`). AST-1474 cannot be signed off at tip without branch cleanup.

**Test bible (read-only):** Betty’s AST-1474 manifests in `docs/test-bible/core/candidate.md`, `utils/config.md`, `ui/api/api_candidate.md` align with the isolated slice. `test(AST-1474)` @ `5f1051cf` covers config constants, normalize/hydrate/ingest, GET catalog/`all_sections`, PUT persist, and rejects `keep_with_next`.

---

## Findings

### fix-now — Cross-ticket contamination on publish ref

- **Location:** branch tip `f150166d`; commits `4bd4ed9e`, `bd61e4a7`, `080604f2`, `d47122f2`, `d4bfa409`
- **Finding:** Publish ref includes product and test code from **AST-1477** and **AST-1478** (parent **AST-1464**), not AST-1462. Visible in `JobsRecommended.tsx`, `RecommendedJobReportHeader.tsx`, `useInPlaceLiveRefresh.ts`, etc., plus `test(AST-1477)` on this branch.
- **Recommendation:** Strip wrong-parent `sync(publish-ref)` merges from `sub/AST-1462/AST-1474-*` so tip contains only AST-1474 product (`7c53225a`) + AST-1474 tests (`5f1051cf`) + doc/test merge. Siblings should publish on their own `sub/AST-1464/*` refs and land on `ftr/AST-1462` via `merge-child`, not via cross-sync onto a peer child ref.

### fix-now — Scope gate violation (`astral.standards.in-scope-only`, `orch.pipeline.plan-is-bible`)

- **Location:** `git diff origin/dev...origin/sub/AST-1462/AST-1474-page-break-policy-config-resume-structure-schema -- 'src/**'`
- **Finding:** Plan Scope gate limits to `config.py`, `candidate.py`, `api_candidate.py`. Branch tip also changes `agent.py`, `tracker.py`, `database.py`, `builder.py`, auth, admin API, and 20+ React files — all out of AST-1474 scope.
- **Recommendation:** Resolve via branch cleanup above before Review Posted / UT routing.

### fix-now — Duplicate import (sibling contamination)

- **Location:** `src/data/database.py` (branch diff vs `origin/dev`)
- **Finding:** `is_valid_candidate_batch_claim_state` imported twice in the same `from src.utils.config import` block.
- **Recommendation:** Drop duplicate line when sibling dispatch work is on its own ref; not introduced by `7c53225a`.

### discuss — Merge-base / dev integration drift

- **Location:** three-dot diff `origin/dev...origin/sub/AST-1462/AST-1474-*`
- **Finding:** Git warns `multiple merge bases, using 0fa5bc81` (AST-1467-era). `0acde3bd sync(dev)` exists but full diff still spans epic-scale `docs/features/**` churn. Downstream `merge-child` / `prep-uat` may hit painful reconcile.
- **Recommendation:** Chuckles confirm epic worktree merge-clean gate against current `origin/dev` before `resolve-child` round — separate from AST-1474 code quality.

### advisory — AST-1474 slice is sound

- **Location:** `7c53225a` (`src/utils/config.py`, `src/core/candidate.py`, `src/ui/api/api_candidate.py`)
- **Finding:** Isolated AST-1474 implementation is plan-faithful: config-owned tokens, `avoid_split` default everywhere, strict normalize on PUT, soft hydrate default with comment, catalog payload for AST-1476. Layer imports clean; no debug/logging violations; defensive GET fallback matches plan.
- **Recommendation:** After publish-ref cleanup, re-review tip — expect **PROCEED** on statute/pattern/plan checks for the slice alone.

### advisory — Prior Joan discuss items still valid

- **Location:** issue doc `## Findings` (self-assessment absent; AC1 names print CSS)
- **Finding:** Unchanged from Joan validate; low risk given explicit binding Decisions.
- **Recommendation:** No block.

---

## What's solid

- Config-as-source-of-truth for page-break policy tokens and labels
- Normalize error messages mirror existing `format` validation style
- Hydrate soft-default vs PUT strict-validate split is documented in-code and matches plan Stage 2 step 5
- Betty tests cover happy path, legacy coercion, invalid token rejection, and catalog shape

## Recommended actions (Chuckles — not Radia)

1. Reset or rewrite `sub/AST-1462/AST-1474-page-break-policy-config-resume-structure-schema` to drop AST-1464 sibling syncs; tip should be AST-1474-only product + tests (+ `merge-tests` if needed).
2. Re-run `review-child` on cleaned tip (or accept advisory above if diff vs `origin/dev` for the three scoped files is unchanged).
3. Route AST-1477/AST-1478 through their own publish refs and `merge-child` onto `ftr/AST-1462`.
4. Before `resolve-child`, run merge-clean gate vs current `origin/dev` given merge-base warning.

---

## Frame diff

| Field | Prior (issue doc stub) | This review |
|-------|------------------------|-------------|
| Tip SHA | `7c53225a` | `f150166d` |
| Product files | 3 (listed) | 43 `src/**` on branch diff — only 3 belong to AST-1474 |
| Tests | not yet at stub | `5f1051cf` AST-1474 + `080604f2` AST-1477 (wrong ticket) |
| Verdict | stub only | FIX-NOW (branch contamination); AST-1474 slice CLEAN |

context_tokens≈42000

---

```
[code-rubric] REVIEW (Commit: f150166d) wrong-parent sync on publish ref
```
