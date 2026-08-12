<!-- linear-archive: AST-1144 archived 2026-08-11 -->

## Linear archive (AST-1144)

**Archived:** 2026-08-11  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1144/uat-parse-meteorite-email-rejects-jobsmetadata-dict-expects-str  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-1128 — gaze_email — candidate-bound dispatch (redesign)  
**Blocked by / blocks / related:** parent: AST-1128

### Description

<!-- uat-validate: stacktrace -->

## What failed

Running candidate-bound `gaze_email` for somerset on a bound html_links inbox message, Ruth `parse_meteorite_email` returned jobs with `metadata` as objects (`{"company":…,"location":…}`). Validation failed:

`do_task validation failed. task_key='parse_meteorite_email' error=jobs[0]: Field 'metadata' must be str, got dict`

Runner logged `ruth_fail=…` and `gaze_email.run … -> error` with `total_errors=1`, `total_passed=0` — no METEORITE_NEW create / archive for that message.

Susan also asked: why wasn’t this caught by test coverage?

## Expected

Bound html_links mail whose Ruth parse yields job links (with optional company/location metadata) validates, scrapes/creates **METEORITE_NEW** (or per-candidate dedupe skip), and archives — same AST-1087 ingest outcomes under the candidate-bound runner.

## Repro

1. Ensure somerset has a `gaze_email` dispatch row and an inbox message From-bound to somerset whose body is HTML with Dice (or similar) job links.
2. Run that somerset `gaze_email` row with debug on.
3. Observe `parse_meteorite_email` validation error on `jobs[].metadata` dict vs str, and message left unprocessed / error outcome.

## Parent AC (quoted inline)

> Bound in-scope message shapes still produce the AST-1087 ingest outcomes for that candidate (**METEORITE_NEW** / archive / ignore rules as already established for bound mail); a single run does not advance jobs into qualify/GDL.

> With `debug=True`, each candidate run, each considered message, and each create/skip/archive/trash/ignore outcome is visible in Style D (found + recorded); with `debug=False`, no new debug noise from this path.

## Diagnosis

* **Hypothesis:** `TASK_CONFIG["parse_meteorite_email"]` schema types `jobs[].metadata` as `str`, but the live Ruth prompt / model returns structured `metadata` objects (company/location). Validation rejects the payload before the runner can scrape/create. Coverage likely asserts config shape only, not a realistic Ruth payload with dict metadata through do_task/gaze_email.
* **Correct outcome:** html_links parse with job links + company/location metadata succeeds end-to-end into METEORITE_NEW (or all-duplicate archive) for that candidate; debug shows found + recorded, not ruth_fail validation.
* **Wrong fix to avoid:** swallow the validation error and continue with empty jobs; delete/loosen all schema checks; leave message forever without fixing the contract; “no more stacktrace” without successful ingest when links are present.
* **Related siblings / contracts:** AST-1136 runner; AST-1089 `parse_meteorite_email` schema/prompt; Betty must add a failing-shape → fixed-shape regression so dict metadata cannot regress silently.

## Acceptance criteria

- [X] Bound html_links Ruth payloads with `jobs[].metadata` as a dict validate under `parse_meteorite_email` and the candidate-bound runner can create/archive (Parent AC ingest outcomes).
- [X] Schema/prompt contract documents optional object metadata (`company` / `location`); AST-756 fixture stays byte-identical to repo `agent_task.json`.
- [X] Debug path still Style D gated; no qualify/GDL daisy-chain in the same run.

## Boundaries

* This bug does **not** change: From→candidate bind rules, Avail count wiring, unbound retention policy, Manage Email Land Meteorite (AST-1129), qualify/GDL hops.
* "No more stacktrace / no more error" alone is **not** done — Parent AC + Correct outcome must hold.

## In scope

- [X] `astral.config.config-source-of-truth` — `jobs[].metadata` type lives on `TASK_CONFIG["parse_meteorite_email"]` (`src/utils/config.py`).
- [X] `astral.agent.do-task-delegation` — fix validation contract so existing `do_task` / gaze_email path can succeed (no new API assembly).
- [X] `astral.seed.archie-catalog-wins` / seed fixture lock — prompt clarity on Archie-named `parse_meteorite_email`; `docs/uat-fixtures/AST-756/expected-agent_task.json` byte-identical.
- [X] `astral.state.no-daisy-chain-in-run` — still stop at METEORITE_NEW after parse succeeds.
- [X] `astral.standards.in-scope-only` — schema + prompt/fixture only; no Avail/bind/UI.

## Considered but excluded

- [X] AST-1136 runner filter / unbound Trash / `last_email_check` — unchanged once validation passes (`src/core/gaze_email.py`).
- [X] Avail / provision / null-shell — AST-1134 / AST-1135.
- [X] Manage Email Land Meteorite UI — AST-1129.
- [X] Swallowing validation / emptying jobs / deleting schema checks — Wrong fix.
- [X] Engineer inventing test-tree coverage — Betty owns dict-metadata regression at Code Complete.

## Notes for planning

Plan: `docs/features/meteorite/ast-1144-uat-parse-meteorite-email-metadata-dict-str.md`.

## Git branch (authoritative)

`origin/sub/AST-1128/AST-1144-uat-parse-meteorite-email-metadata-dict-str` — ignore Linear `gitBranchName`.

### Comments

#### chuckles — 2026-08-02T22:27:15.255Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

`e0b4807f Merge remote-tracking branch 'origin/dev' into sub/AST-1128/AST-1144-…` must not stay on the publish tip. Reset to pre-pull tip (`b8d8772d`), merge `origin/ftr/AST-1128-gaze-email-candidate-bound-dispatch-redesign`, force-push publish ref. No product code change.

@Katherine Johnson

— Chuckles

#### radia — 2026-08-02T22:24:39.308Z
[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1144
**Publish ref:** `origin/sub/AST-1128/AST-1144-uat-parse-meteorite-email-metadata-dict-str` tip `0abc2c8e6fd9aa381541549e4fff57d3452e951f`
**Overall:** DISCUSS

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| `astral.agent.confidence-bounds` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.agent.do-task-delegation` | scoped | conforms | existing do_task validation path; no new API assembly |
| `astral.agent.grade-vector-validation` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.batch.batch-id-first` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.batch.batch-id-format` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.batch.claim-process-release` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.batch.entity-agent-responses-latest-only` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.config.config-source-of-truth` | scoped | conforms | metadata type lives on TASK_CONFIG parse_meteorite_email |
| `astral.config.pass-threshold-vs-score-floor` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.config.secrets-and-env-specific-from-environ` | scoped | conforms | no secrets moved into config |
| `astral.debug.no-repo-root-artifacts-dir` | scoped | conforms | no repo-root artifacts/ directory in this child |
| `astral.debug.spikes-under-debug-dir` | scoped | conforms | features docs are ticket plans, not spike dumps |
| `astral.dispatch.run-next-is-chain-authority` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.dispatch.seed-auto-false` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.docs.features-single-file-per-ticket` | scoped | conforms | ast-1144 plan doc present under docs/features/meteorite/ |
| `astral.git.betty-no-src-or-features` | scoped | conforms | Betty test commits avoid src/features |
| `astral.git.engineer-test-tree-ban` | scoped | conforms | code() has no tests/; Betty owns regression |
| `astral.layers.core-vs-external-bright-line` | scoped | conforms | no Gmail/external I/O on this child |
| `astral.layers.import-direction` | scoped | conforms | no new layer imports on this child |
| `astral.layers.scripts-exempt-from-layer-rules` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.layers.ui-config-driven-business-logic` | scoped | conforms | no React business-rule invent on this child |
| `astral.patterns.coat-check-never-store-empty` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.patterns.render-verdict-orchestrates-consult` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.patterns.require-auth-on-protected-endpoints` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.seed.agent-tables-in-repo-json` | scoped | conforms | agent_task.json remains repo catalog source |
| `astral.seed.archie-catalog-wins` | scoped | conforms | prompt edit on Archie-named parse_meteorite_email; fixture lock |
| `astral.seed.boot-only-not-hot-path` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.seed.define-approved` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.seed.operator-rows-stay-deleted` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.seed.other-via-coverage-join` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.standards.data-raises-caller-logs` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.standards.database-header-inventory` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.standards.debug-contract-gated` | scoped | conforms | no new debug surfaces on this child |
| `astral.standards.dry-and-focused-functions` | scoped | conforms | minimal schema+prompt change; no parallel validator |
| `astral.standards.in-scope-only` | scoped | conforms | code() is schema+prompt+fixture only |
| `astral.standards.logging-via-utils` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.standards.names-not-ticket-ids` | scoped | conforms | no ticket-id product identifiers; AST-1144 only in comments |
| `astral.standards.no-cross-contamination` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.standards.no-hardcoded-sets` | scoped | conforms | schema type flip only; no new carve-out sets |
| `astral.standards.public-then-helpers` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.standards.utils-data-late-import-only` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.state.core-decides-transitions` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.state.job-prior-states-enforced` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.state.no-daisy-chain-in-run` | scoped | conforms | no qualify/GDL added; METEORITE_NEW path unchanged |
| `astral.ui.frontend-file-placement` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.ui.naming-conventions` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `astral.ui.single-gunicorn-worker` | scoped | conforms | no violation observed on three-dot tip vs origin/dev |
| `orch.git.betty-merge-tests-one-sha` | universal | conforms | single merge-tests(AST-1144) SHA on sub tip |
| `orch.git.commit-vocabulary` | universal | conforms | plan/code/docs/test/merge-tests vocabulary on sub |
| `orch.git.flow-direction-inviolable` | universal | conforms | publish stays on origin/sub child ref |
| `orch.git.ftr-sub-topology` | universal | conforms | sub/AST-1128/AST-1144-… matches parent Git table |
| `orch.git.merge-on-checkout` | universal | conforms | no illegal merge/rebase recipe in this child |
| `orch.git.no-cherry-pick-rebase-force` | universal | conforms | no cherry-pick/rebase/force on publish tip |
| `orch.git.no-dev-agent-branches` | universal | conforms | no agent-named branches; epic worktree sub tip |
| `orch.git.one-epic-worktree-per-parent` | universal | conforms | review on astral-AST-1128 epic worktree |
| `orch.git.three-permanent-branches` | universal | conforms | no new permanent branches |
| `orch.pipeline.call-susan-for-product-decisions` | universal | conforms | UAT bug fix follows Diagnosis; no product invent |
| `orch.pipeline.plan-is-bible` | universal | conforms | Stage 1 schema+prompt+fixture lock matches plan |
| `orch.pipeline.project-scoped-queues` | universal | conforms | Meteorite child AST-1144 only |
| `orch.pipeline.status-gates-skill-entry` | universal | conforms | review-child entered at Tests Passed |
| `orch.roles.archie-approves-statutes` | universal | conforms | no new statute authorship on this child code() |
| `orch.roles.betty-owns-test-tree` | universal | conforms | test()+merge-tests own tests/bible; code() is schema/prompt/fixture |
| `orch.roles.chuckles-never-ticket-assignee` | universal | conforms | Chuckles not assignee |
| `orch.roles.engineer-assignee-through-resolve` | universal | needs-discussion | assignee is Radia at Tests Passed; implementer usually stays through Review Posted |
| `orch.roles.pre-commit-path-bans` | universal | conforms | engineer code() avoided banned test-tree paths |

## Pattern conformance

none cited

## Plan adherence

Stage 1 matches Files Changed: schema `dict`, prompt object wording, AST-756 fixture byte-identical to `data/admin/agent_task.json` (verified). Wrong-fix paths rejected (no swallow/empty jobs). `code(AST-1144)` is the three planned files only; three-dot vs `origin/dev` also carries sibling epic history (multi merge-base).

## Findings

**discuss:** Assignee is Radia at Tests Passed (`orch.roles.engineer-assignee-through-resolve`). Confirm whether that was intentional for review handoff or restore the implementer for resolve-child.

## What's solid

`metadata: dict` unblocks Ruth html_links objects; catalog prompt + fixture lock; Betty dict regression. No fix-now on the product change.

## Notes

no plan-rubric verdict attached

context_tokens≈42000

#### betty — 2026-08-02T22:21:33.904Z
## QA test manifest

`origin/sub/AST-1128/AST-1144-uat-parse-meteorite-email-metadata-dict-str` @ `32434707`
`merge-tests(AST-1144): origin/tests 78fc4acb6a893dfca32ab7c8ab48dfaa381ace8a`

### Gaps (new — dict-metadata regression)

1. `tests/component/utils/test_config.py::TestAst1144ParseMeteoriteEmailMetadataDict` — `jobs[].metadata` schema type `dict`, optional
2. `tests/component/core/test_agent.py::TestAst1144ParseMeteoriteEmailMetadataDict` — realistic html_links payload: dict metadata validates; str rejected; omitted ok
3. `tests/component/core/test_gaze_email.py::TestAst1090RunGazeEmail::test_html_links_dict_metadata_still_creates` — bound runner create/archive with dict metadata
4. `tests/component/core/test_repo_admin_json.py::TestAst1144ParseMeteoriteEmailMetadataPrompt` — prompt documents optional metadata object; AST-756 fixture byte-lock

### Broken / obsolete

None — AST-1089 shell asserts still hold (did not lock metadata type).

### Run

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1144ParseMeteoriteEmailMetadataDict \
  tests/component/core/test_agent.py::TestAst1144ParseMeteoriteEmailMetadataDict \
  tests/component/core/test_gaze_email.py::TestAst1090RunGazeEmail::test_html_links_dict_metadata_still_creates \
  tests/component/core/test_repo_admin_json.py::TestAst1144ParseMeteoriteEmailMetadataPrompt \
  -q
```

### Bible shasums (on publish tip)

- `docs/test-bible/utils/config.md` `7ce7a44583c609da5ba9a03ad31e49a82f0ad9cc`
- `docs/test-bible/core/agent.md` `b763e5dfb56d56b6c82e89e2680b9634aaa8765e`
- `docs/test-bible/core/gaze_email.md` `409977fec7cda8cbd167a95148039764ee15dc4d`
- `docs/test-bible/core/repo_admin_json.md` `0581fdb8845e8d6029ee5e9fe2a5e2f4804f667e`

context_tokens≈92000

#### katherine — 2026-08-02T22:18:54.581Z
`origin/sub/AST-1128/AST-1144-uat-parse-meteorite-email-metadata-dict-str` @ `5fa7f62f` — Betty: add dict `jobs[].metadata` regression through do_task/gaze_email (Diagnosis).

context_tokens≈12000

#### joan — 2026-08-02T22:17:04.327Z
[validate-plan uat-thin]
**Ticket:** AST-1144
**Overall:** APPROVED

## UAT-thin checklist

- [x] Plan cites Parent AC (quoted ingest outcomes + Style D debug in ## UAT fitness), not symptom-only
- [x] Stage 1 achieves Correct outcome: `jobs[].metadata` schema `str`→`dict` + prompt documents optional `{company?, location?}` so validation passes and candidate-bound runner can create/archive — not merely silence the NameError/validation line
- [x] Wrong fixes rejected (swallow validation / empty jobs; delete/loosen all schema checks; leave message forever; “no more stacktrace” without ingest) — plan implements single-type `dict` + prompt clarity only
- [x] No catch-and-ignore / delete-log-path / empty-success / bypass
- [x] Sibling check: AST-1136 runner / unbound / stamp unchanged; AST-1089 task key/modes stay; AST-1129 benefits from same `do_task` contract; Betty owns dict-metadata regression post Code Complete
- [x] Boundaries respected: no bind/Avail/unbound retention/Land Meteorite UI/qualify-GDL; no `gaze_email.py` edits

## Notes

## UAT fitness present. Conf high / Risk Medium honest (live UAT shows dict; prompt+schema aligned; runner already uses `job_link` only).

context_tokens≈16000

— Joan

#### joan — 2026-08-02T22:01:57.078Z
[validate-plan uat-thin]
**Ticket:** AST-1144
**Overall:** blocked — not assigned to Joan

Status is Plan Ready, but assignee is Katherine Johnson, not Joan. Chuckles must assign Joan before validate-plan can run.

context_tokens≈12000

— Joan

#### katherine — 2026-08-02T21:58:30.567Z
Plan published on `origin/sub/AST-1128/AST-1144-uat-parse-meteorite-email-metadata-dict-str` @ `4d93f54d`.

**Plan:** https://github.com/susansomerset/astral/blob/sub/AST-1128/AST-1144-uat-parse-meteorite-email-metadata-dict-str/docs/features/meteorite/ast-1144-uat-parse-meteorite-email-metadata-dict-str.md

**Self-assessment**
- **Scope:** minor — one schema field type (`jobs[].metadata` str→dict) + prompt/fixture sync; no runner/Avail/UI.
- **Conf:** high — failure names the exact schema field; agent already validates `dict`; runner only needs validation to pass for scrape/create.
- **Risk:** Medium — wrong type flip could reject rare string metadata; mitigated by live UAT dict evidence + prompt documenting object shape.

---

# AST-1144 — UAT: parse_meteorite_email rejects jobs[].metadata dict (expects str)

**Linear:** [AST-1144](https://linear.app/astralcareermatch/issue/AST-1144/uat-parse-meteorite-email-rejects-jobsmetadata-dict-expects-str)
**Parent:** [AST-1128](https://linear.app/astralcareermatch/issue/AST-1128/gaze-email-candidate-bound-dispatch-redesign) — gaze_email — candidate-bound dispatch (redesign)
**Publish ref:** `origin/sub/AST-1128/AST-1144-uat-parse-meteorite-email-metadata-dict-str`

UAT bug: candidate-bound `gaze_email` for somerset hit Ruth `parse_meteorite_email` validation `jobs[0]: Field 'metadata' must be str, got dict` when the model returned structured company/location metadata. Align the TASK_CONFIG schema (and prompt wording) with the live object shape so html_links ingest can reach METEORITE_NEW / archive again. Does **not** change bind/Avail/unbound retention/Land Meteorite/qualify hops.

## UAT fitness

- **AC restored:** “Bound in-scope message shapes still produce the AST-1087 ingest outcomes for that candidate (**METEORITE_NEW** / archive / ignore rules as already established for bound mail); a single run does not advance jobs into qualify/GDL.” Also: “With `debug=True`, each candidate run, each considered message, and each create/skip/archive/trash/ignore outcome is visible in Style D (found + recorded); with `debug=False`, no new debug noise from this path.”
- **Correct outcome:** Bound html_links mail whose Ruth parse yields job links (with optional company/location metadata objects) validates, scrapes/creates **METEORITE_NEW** (or per-candidate dedupe skip), and archives; debug shows found + recorded, not `ruth_fail` validation.
- **Sibling check:** AST-1136 runner three-way filter / unbound Trash / `last_email_check` stamp unchanged — only the parse contract for `jobs[].metadata` changes so `_handle_bound` can consume a successful `parsed_response`. AST-1089 task key / modes / `requires_candidate_key` stay. AST-1129 Land Meteorite reuse path benefits from the same schema fix (same `do_task`). Verify by running somerset `gaze_email` (or component fixture with dict metadata) without touching Avail/provision.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Swallowing validation and continuing with empty `jobs`; deleting/loosening all schema checks; leaving the message forever without fixing the contract; “no more stacktrace” without successful ingest when links are present.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `TASK_CONFIG["parse_meteorite_email"].response_schema.jobs.items_schema.metadata` type `str` → `dict` | utils |
| `data/admin/agent_task.json` | Clarify `html_links` prompt: `metadata` is optional object `{company?, location?}` | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Byte-identical copy after prompt edit (AST-786 seed gate) | docs |

No `src/core/gaze_email.py` / dispatcher / Avail / React / Gmail changes. No engineer edits under `tests/` / bible (Betty adds dict-metadata regression at Code Complete per Diagnosis).

## Stage 1: Schema + prompt contract for dict metadata

**Done when:** `do_task` validation accepts a `parse_meteorite_email` payload whose `jobs[].metadata` is a dict (e.g. `{"company":"…","location":"…"}`); prompt documents that object shape; AST-756 fixture matches repo `agent_task.json`; runner still only needs `job_link` for scrape/create (metadata remains optional advisory).

1. In `src/utils/config.py` inside `TASK_CONFIG["parse_meteorite_email"]["response_schema"]["jobs"]["items_schema"]`, change:

   ```python
   "metadata": {"type": "str", "required": False},
   ```

   to:

   ```python
   "metadata": {"type": "dict", "required": False},
   ```

   ⚠️ **Decision — type `dict`, not loosen/remove:** `src/core/agent.py` `_validate_schema_object_fields` already accepts `type` in `("object", "dict")` for mapping values. Live Ruth returns structured company/location objects; AST-1089’s `str` typing was the mismatch. Prefer `dict` (same literal as `resume_structure` / `job_data` peers). Do **not** accept both str and dict in one field (validator is single-type). Do **not** skip schema validation.

2. Do **not** change `job_link` / `job_title` / top-level `parse_mode` / `jd_link` / `content_text` types. Do **not** add nested `items_schema` on `metadata` (validator does not recurse object field maps today; optional free-form dict is enough for company/location).

3. In `data/admin/agent_task.json`, on the `current: 1` row `task_key == "parse_meteorite_email"`, edit **only** the `cache_prompt` html_links sentence that currently says `return \`{job_link, job_title?, metadata?}\` in \`jobs\`` so it documents the object shape, e.g. return `{job_link, job_title?, metadata?}` where optional `metadata` is an object with optional string fields `company` / `location` (omit `metadata` when unknown). Keep subject_body section and “JSON only / no qualify fields” rules unchanged.

   ⚠️ **Decision — prompt clarity, not a second parse mode:** Prompt already invited unstructured `metadata?`; Ruth filled objects. Document the object so the catalog matches the schema; do not invent a new TASK_CONFIG key or PARSE_MODE.

4. Copy the updated `data/admin/agent_task.json` bytes to `docs/uat-fixtures/AST-756/expected-agent_task.json` so they remain identical (same AST-786 / catalog gate as AST-1089 Stage 2).

5. Do **not** edit `src/core/gaze_email.py` — `_handle_bound` already uses only `job.get("job_link")` for html_links ingest; once validation passes, create/archive resumes. Do **not** coerce/stringify metadata in `agent.py`. Do **not** change From-bind, Avail, unbound retention, or Land Meteorite UI.

**Done when (recheck):**

```bash
python3 -c "from src.utils import config as c; m=c.TASK_CONFIG['parse_meteorite_email']['response_schema']['jobs']['items_schema']['metadata']; assert m['type']=='dict' and m.get('required') is False"
python3 -c "import json; a=open('data/admin/agent_task.json','rb').read(); b=open('docs/uat-fixtures/AST-756/expected-agent_task.json','rb').read(); assert a==b"
python3 -m py_compile src/utils/config.py
```

Betty (post Code Complete): add a regression that feeds a realistic Ruth payload with `jobs[].metadata` as a dict through `do_task` / gaze_email path so this cannot regress to `type: str` silently (Diagnosis — engineer does not invent that test here).

## Self-Assessment

**Scope:** `minor` — one schema field type + prompt/fixture sync for `parse_meteorite_email`; no runner/Avail/UI surfaces.

**Conf:** `high` — failure string names the exact schema field; agent already validates `dict`; runner ignores metadata content and only needs validation to pass.

**Risk:** `Medium` — wrong type flip could reject string metadata if any caller still emits str; mitigated by live UAT evidence (dict) + prompt documenting object. Ingest path unblocked when links present.

## Rules check (plan vs ASTRAL_CODE_RULES)

- §2.1 / `astral.config.config-source-of-truth` — response schema stays in `TASK_CONFIG`.
- §2.2 / `astral.agent.do-task-delegation` — still `do_task`; no new Anthropic assembly in core.
- `astral.standards.in-scope-only` — schema/prompt/fixture only; no Avail/bind/Land Meteorite.
- `astral.state.no-daisy-chain-in-run` — still METEORITE_NEW only after parse succeeds.
- Seed/catalog: prompt edit stays on Archie-named `parse_meteorite_email`; fixture byte-lock preserved.

## Review

**Publish ref:** `origin/sub/AST-1128/AST-1144-uat-parse-meteorite-email-metadata-dict-str`
**Tip:** `32434707dbab3e758d082da1fbaee4b01682a17c`
**Overall:** DISCUSS

[code-rubric] revision=1 — Radia full-set sweep vs `origin/dev...origin/sub/AST-1128/AST-1144-uat-parse-meteorite-email-metadata-dict-str`.

### What's solid

- Stage 1 matches plan: `jobs[].metadata` type `str` → `dict` on `TASK_CONFIG["parse_meteorite_email"]`; html_links prompt documents optional `{company?, location?}` object; AST-756 fixture byte-identical to `data/admin/agent_task.json`.
- Betty added dict-metadata regression (`do_task` validates dict; rejects str). No runner/Avail/UI creep in `code(AST-1144)`.

### Issues

**discuss:** Linear assignee is Radia at Tests Passed (`orch.roles.engineer-assignee-through-resolve`). Implementer should usually remain assignee through Review Posted / resolve. Confirm handoff (leave Radia vs restore engineer) before resolve-child.

### Recommended actions

- No fix-now on the schema/prompt fix. Restore engineer assignee for resolve if that was unintentional.

## Resolution

**Date:** 2026-08-02  
**Review tip:** `0abc2c8e` · **Overall:** DISCUSS (no fix-now)

**discuss — assignee Radia at Tests Passed:** Closed for resolve. Linear assignee is **Katherine Johnson** (implementer) through Review Posted / this resolve; no product change. Transient Radia assignee at review handoff does not require further action.

**fix-now:** none.
