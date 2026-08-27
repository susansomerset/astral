# AST-1494 — Ruth company-stem discernment (sender / self / slug)

**Linear:** [AST-1494](https://linear.app/astralcareermatch/issue/AST-1494/ruth-company-stem-discernment-sender-self-slug-create-meteorite)  
**Parent:** [AST-1484](https://linear.app/astralcareermatch/issue/AST-1484/create-meteorite-companies-per-email-address) — Create meteorite companies per email address  
**Publish ref:** `sub/AST-1484/AST-1494-ruth-company-stem-discernment`

Land / `qualify_meteorite` enrichment: Ruth returns a **company stem** from CONTENT — original sender email, literal `meteorite-self` (candidate’s own non-forwarded message), or a job-link slug — so sibling ensure/attach can build `{stem}-{candidate_id}` in **METEORITE**. This ticket owns TASK_CONFIG schema + prompt catalog + RESPONSE mapping only. Does **not** own `ensure_meteorite_company` / track predicate (**AST-1493**) or inbox/gaze land wiring / attach (**AST-1495**).

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/core/consult.py` / `src/core/agent.py` — modified — enrichment invoke + RESPONSE mapping for company stem.
- `src/utils/config.py` — modified — TASK_CONFIG / schema / prompt literals for the stem field only (shared file; units not owned by #1).
- Catalog / `agent_task` row updates as plan chooses within this child.

All Files Changed / Stages stay inside that set.

**Out of scope (siblings / later):**

- `COMPANY_STATES["METEORITE"]`, `METEORITE_CONFIG` company_state / stem templates / `ensure_meteorite_company(stem=)` / `is_meteorite_company` — **AST-1493** (User Testing; already on `origin/ftr/AST-1484-create-meteorite-companies-per-email-address`).
- Inbox / `gaze_email` / `gazer` CONTENT supply; `create_meteorite_job` / `land_meteorite` attach-when-stem-present — **AST-1495**.
- Core forward/autoforward **header parsers** — parent law: Ruth decides from CONTENT.
- Bulk migration of historical IGNORE placeholders.

**Depends on:** AST-1493 tip available on the epic line before build (Bang !). Build must see `METEORITE_CONFIG["meteorite_self_stem"]` == `"meteorite-self"` (do **not** re-define that literal in TASK_CONFIG). If missing after `sync-child.sh`, merge `origin/ftr/AST-1484-create-meteorite-companies-per-email-address` (or the published AST-1493 tip) on the epic worktree, then continue — do not invent parallel self-stem keys.

**AC partition (this ticket):** Parent AC2–AC4 as **Ruth returns the stem string** that #1’s ensure templates consume (`alice@example.com`, `meteorite-self`, `{slug}`). End-to-end ensure+attach under that company is proven when AST-1495 wires land — this ticket’s Done when is RESPONSE field present + mapped on enrich output + prompts teach the three cases.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add optional `company_stem` to `qualify_meteorite` items_schema + TASK_CONFIG field-name literal + asserts | utils |
| `data/admin/agent_task.json` | Update current `qualify_meteorite` cache/user prompts for stem discernment | catalog |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Byte-identical twin of repo `agent_task.json` (AST-786) | docs |
| `src/core/consult.py` | Map `company_stem` in `enrich_meteorite_land_packet`; Style D on land + dispatch qualify when `debug=True` | core |
| `src/core/agent.py` | Module / `do_task` docstring: land enrich RESPONSE may include `company_stem` (schema-validated; no new decode path) | core |

## Stage 1: Config — `company_stem` on `qualify_meteorite`

**Done when:** `TASK_CONFIG["qualify_meteorite"]["response_schema"]["jobs"]["items_schema"]` includes optional `company_stem` (`type: str`, `required: False`). A TASK_CONFIG literal names the RESPONSE key (single source for consult mapping). Asserts lock schema + key string. No consult/agent/catalog edits yet.

1. In `src/utils/config.py`, inside `TASK_CONFIG["qualify_meteorite"]["response_schema"]["jobs"]["items_schema"]`, after the existing `employer_name` entry, add:

```python
                    # AST-1494: Ruth company short_name stem (sender email / meteorite-self / job-link slug)
                    "company_stem":    {"type": "str", "required": False},
```

2. On the same `qualify_meteorite` task dict (sibling to `email_link_prefix` / `bot_blocked_state`), add:

```python
        "company_stem_response_key": "company_stem",  # AST-1494: RESPONSE + enrich map key
```

⚠️ **Decision:** Field name lives in TASK_CONFIG (this ticket’s Scope). The **value** `meteorite-self` stays `METEORITE_CONFIG["meteorite_self_stem"]` from AST-1493 — consult/prompts **read** that config key; do not duplicate the string in TASK_CONFIG.

3. After the existing `employer_name` required-False assert (~line 1039), add:

```python
assert TASK_CONFIG["qualify_meteorite"]["response_schema"]["jobs"]["items_schema"]["company_stem"]["required"] is False
assert TASK_CONFIG["qualify_meteorite"]["company_stem_response_key"] == "company_stem"
assert TASK_CONFIG["qualify_meteorite"]["company_stem_response_key"] in (
    TASK_CONFIG["qualify_meteorite"]["response_schema"]["jobs"]["items_schema"]
)
```

4. Do **not** edit `METEORITE_CONFIG`, `COMPANY_STATES`, NAV, or other TASK_CONFIG tasks in this stage.

## Stage 2: Catalog — Ruth stem discernment prompts

**Done when:** Current `qualify_meteorite` row in `data/admin/agent_task.json` instructs Ruth to return `company_stem` with the three cases below; `docs/uat-fixtures/AST-756/expected-agent_task.json` is byte-identical to the repo JSON; `updated_at` on that row is refreshed to the build date (ISO-like string matching neighboring rows’ style).

1. In `data/admin/agent_task.json`, find the object with `"task_key": "qualify_meteorite"` and `"current": 1`. Edit **`cache_prompt`** so the field list includes `company_stem`, and add a short **COMPANY STEM** subsection with these rules (wording may be tightened for length; meaning must not change):

   - Return `company_stem` on **each** jobs item (may be empty string / omit when none of the cases apply).
   - **Priority (first match wins):**
     1. Message is from the **candidate** (match From / apparent author against the candidate’s known emails in tokens / CONTEXT) **and** is **not** a forward of someone else’s mail → return exactly the literal from config consumers: `meteorite-self` (same string as `METEORITE_CONFIG["meteorite_self_stem"]`).
     2. Else an **original sender email** is discernible in CONTENT (forwarded/alert/recruiter From, not the candidate) → return that email address as the stem (lowercase local@domain; no display-name wrapper).
     3. Else a **usable job-link slug** is available (from `job_link` or URL in CONTENT): a short path segment suitable as a company short_name fragment — **not** a full URL, **not** a UUID, prefer lowercase hyphenated slug — return that slug.
     4. Else omit / empty `company_stem` (caller will use default stem).
   - Core does **not** parse forward headers; decide from CONTENT only.
   - Keep existing fields: `company_job_id`, `job_title`, `job_link`, `jd_text`, `employer_name` (optional).

2. Edit **`user_prompt`** on the same row so it asks for `company_stem` alongside the other fields (one sentence delta is enough).

3. Set `"updated_at"` on that row to a current UTC timestamp string consistent with other catalog rows.

4. Sync the UAT twin:

```bash
cp data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json
cmp -s data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json && echo OK
```

⚠️ **Decision:** Prompt + schema together teach Ruth; do **not** add a second agent_task / new task_key. Land enrich and dispatch qualify already share `qualify_meteorite`.

## Stage 3: Consult mapping + agent docstring

**Done when:** `enrich_meteorite_land_packet` includes `company_stem` on each successful out job (Ruth value stripped; empty when absent). Dispatch `qualify_meteorite` Style D (debug only) mentions stem when present. `agent.py` documents that land enrich RESPONSE may carry `company_stem` under schema validation. No ensure/attach calls. `debug=False` adds no new debug-contract lines.

1. In `src/core/consult.py`, inside `enrich_meteorite_land_packet`, after resolving `employer_name` for each scrap row:

   a. Read `stem_key = TASK_CONFIG["qualify_meteorite"]["company_stem_response_key"]`.  
   b. `ruth_stem = (rj.get(stem_key) or "").strip() if isinstance(rj.get(stem_key), str) else ""`.  
   c. Append `"company_stem": ruth_stem` to each `out_jobs` dict (same level as `employer_name`).  
   d. Style D detail (existing `debug=True` block): append `company_stem={ruth_stem!r}` (or `company_stem=yes/no` + value — prefer the stripped value in the detail line).

⚠️ **Decision:** Empty stem is fine — AST-1495 / ensure default_stem handles omit. Do **not** call `ensure_meteorite_company` here. Do **not** rewrite scrap CONTENT or invent From headers.

2. In `qualify_meteorite`’s inner `process` (dispatch path), when `debug=True` and the job passes content gates (the success Style D block that already logs `company_job_id` / title / link / jd_chars), also log `company_stem` from `response_job` via the same `company_stem_response_key` (stripped). Do **not** persist stem onto `parsed_job` / `initialize_job` in this ticket (attach ownership is AST-1495). Fail/bot paths need no stem detail.

3. In `src/core/agent.py` module docstring (after the AST-1470 land-enrich paragraph), add one short paragraph:

   - AST-1494: `qualify_meteorite` RESPONSE items may include optional `company_stem` (TASK_CONFIG schema); land enrich maps it in consult; `do_task` validation is unchanged schema path — no new decode helper.

4. Do **not** change `_validate_response_schema` / Anthropic client / soft-coerce beyond what existing optional-str handling already does.

## Execution contract

- Stages in order; steps in order within a stage.
- One commit per stage on the epic worktree, then `git push origin HEAD:sub/AST-1484/AST-1494-ruth-company-stem-discernment`.
- No files outside the Files Changed table.
- Ambiguity / drift → stop, comment on **parent** AST-1484 with the Stage blocked format from plan-child, wait.
- Test tree / bible: Betty only — engineer does not edit `tests/` or `docs/test-bible/**`.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Traceability

- Parent AC2 (email stem) → Stage 2 priority #2 + Stage 3 map → ensure shape owned by AST-1493/1495.
- Parent AC3 (`meteorite-self`) → Stage 2 priority #1 + Stage 1 key; literal from AST-1493 `meteorite_self_stem`.
- Parent AC4 (slug stem) → Stage 2 priority #3 + Stage 3 map.
- Parent AC5 (land attach) → out of scope → AST-1495.
- Schema / prompt persist → Stages 1–2 (`pattern.agent.prompt-persist-before-provider` via existing `do_task`); RESPONSE map → Stage 3 (`pattern.batch.entity-agent-responses`).

## Joan validate

[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1494
**Overall:** APPROVED
**Publish ref:** `sub/AST-1484/AST-1494-ruth-company-stem-discernment` @ `bf82f210ddde37aac5bb2111b9bc0bc80041a2ca`

## Traceability
AC2→S2 priority #2 + S3 map; AC3→S2 priority #1 + S1 key (`meteorite-self` via AST-1493 literal, not TASK_CONFIG); AC4→S2 priority #3 + S3 map; parent AC5 (land attach under ensured company)→AST-1495 out of scope; ensure/track→AST-1493 dependency noted in Scope gate.

## Findings

### discuss
- **Location:** Plan traceability — `pattern.agent.prompt-persist-before-provider`
- **Finding:** Catalog entry is still `status: proposed` (not `approved`); plan cites it via existing `do_task` sequencing only.
- **Recommendation:** Citation hygiene — same precedent as AST-1470 Joan pass; no new persist work required in this child.

### discuss
- **Location:** Plan doc (top-level sections)
- **Finding:** No `## Self-Assessment` (conf / blast-radius).
- **Recommendation:** Optional add; stages, scope gate, and AC partition are explicit enough to build.

### acceptable
- **Location:** Files Changed — `docs/uat-fixtures/AST-756/expected-agent_task.json`
- **Finding:** Not verbatim in ticket `## Scope`, but follows established AST-786 catalog-twin pattern for `agent_task.json` edits.
- **Recommendation:** Keep — matches repo convention and `test_repo_admin_json` expectations.

### acceptable
- **Location:** Stage 3 — dispatch `qualify_meteorite` `process`
- **Finding:** Stem logged on debug success only; not persisted on `parsed_job` / `initialize_job`.
- **Recommendation:** Correct partition — attach/ensure wiring is AST-1495; dispatch path jobs already have a `company` row.

context_tokens≈55000

## Review (build stub)

**Publish ref:** `origin/sub/AST-1484/AST-1494-ruth-company-stem-discernment`
**Plan path:** `docs/features/meteorite/ast-1494-ruth-company-stem-discernment.md`

**Built tip:** `317f3dc8660bb12a94def58976dffa0ba7ed4e75` (`317f3dc8`)

| Stage | Commit | Summary |
|-------|--------|---------|
| — | `merge-resume` | stack on `origin/ftr/AST-1484` (AST-1493 dependency) |
| 1 | `bd565711` | `company_stem` schema + `company_stem_response_key` |
| 2 | `83257745` | Ruth `qualify_meteorite` prompts + AST-756 fixture twin |
| 3 | `317f3dc8` | land enrich map + dispatch debug stem + agent docstring |

**Betty note:** component tests for schema, catalog, enrich map deferred to qa-child.


## Radia review

# Radia review — AST-1494

[code-rubric] revision=1  
**Rubric:** code-rubric.v1  
**Ticket:** AST-1494  
**Publish ref:** `origin/sub/AST-1484/AST-1494-ruth-company-stem-discernment` @ `60f0d40e6b79c177f4252be907ef1aaa96e0b6ac`  
**Overall:** CLEAN

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no confidence-bound paths touched |
| astral.agent.do-task-delegation | scoped | conforms | land enrich still delegates to existing `do_task` / schema validation |
| astral.agent.grade-vector-validation | scoped | not-applicable | `qualify_meteorite` stem field is non-grade extract |
| astral.batch.batch-id-first | scoped | not-applicable | no batch_id contract changes |
| astral.batch.batch-id-format | scoped | not-applicable | no batch_id formatting |
| astral.batch.claim-process-release | scoped | not-applicable | no claim/process/release helpers |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no entity latest-ref write semantics changed |
| astral.config.config-source-of-truth | scoped | conforms | `company_stem` schema + `company_stem_response_key` live in `TASK_CONFIG` |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no secrets/env literals |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug artifacts |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no spikes |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch seed edits |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no run_next changes |
| astral.docs.features-single-file-per-ticket | scoped | conforms | single issue doc for AST-1494 |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty commit `e05aca66` touches tests + test-bible only |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer commits (`bd565711`, `83257745`, `317f3dc8`) touch only planned `src/` + catalog |
| astral.layers.core-vs-external-bright-line | scoped | conforms | no new external I/O; consult/agent mapping only |
| astral.layers.import-direction | scoped | conforms | `consult`/`agent` → `utils` config reads; no layer bends |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no `scripts/` changes |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | no UI changes |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no render-verdict paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no API/auth surface |
| astral.seed.agent-tables-in-repo-json | scoped | conforms | `qualify_meteorite` catalog row updated in `data/admin/agent_task.json` |
| astral.seed.archie-catalog-wins | scoped | conforms | catalog edit follows repo JSON + AST-756 twin sync |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no boot seed paths |
| astral.seed.define-approved | scoped | not-applicable | no define workflow |
| astral.seed.operator-rows-stay-deleted | scoped | not-applicable | no operator-row deletes |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage-join seed |
| astral.standards.data-raises-caller-logs | scoped | conforms | no new data-layer logging |
| astral.standards.database-header-inventory | scoped | not-applicable | no schema/migration |
| astral.standards.debug-contract-gated | scoped | conforms | stem detail appended only inside existing `debug=True` blocks |
| astral.standards.dry-and-focused-functions | scoped | conforms | stem read/map is minimal; key from `TASK_CONFIG` |
| astral.standards.in-scope-only | scoped | conforms | engineer product footprint matches Files Changed table |
| astral.standards.logging-via-utils | scoped | conforms | uses existing `get_logger` / `debug_detail` |
| astral.standards.names-not-ticket-ids | scoped | conforms | runtime field `company_stem` is config-named |
| astral.standards.no-cross-contamination | scoped | conforms | no ensure/attach/inbox wiring (AST-1493/1495 boundaries held) |
| astral.standards.no-hardcoded-sets | scoped | conforms | RESPONSE key read via `company_stem_response_key`; asserts lock shape |
| astral.standards.public-then-helpers | scoped | conforms | enrich output change is inline in public enrich path |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | config diff does not import `data` |
| astral.state.core-decides-transitions | scoped | conforms | stem not persisted on job row; no ad hoc state writes |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job transition registry edits in this ticket |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no multi-hop runner added |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend |
| astral.ui.naming-conventions | scoped | not-applicable | no UI naming |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no worker config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | tip `60f0d40e` is `merge-tests(AST-1494)` |
| orch.git.commit-vocabulary | universal | conforms | `code` / `test` / `docs` / `merge-tests` / `merge-resume` vocabulary |
| orch.git.flow-direction-inviolable | universal | conforms | child `sub/AST-1484/AST-1494-…` vs `origin/dev` |
| orch.git.ftr-sub-topology | universal | conforms | stacked on `ftr/AST-1484` after AST-1493 dependency merge |
| orch.git.merge-on-checkout | universal | conforms | `merge-resume` + `sync(dev)` present; no violations |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | linear stage commits |
| orch.git.no-dev-agent-branches | universal | conforms | publish ref is `sub/…` |
| orch.git.one-epic-worktree-per-parent | universal | conforms | AST-1484 epic pattern |
| orch.git.three-permanent-branches | universal | conforms | baseline `origin/dev` |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no product-policy overrides in diff |
| orch.pipeline.plan-is-bible | universal | conforms | three stages match plan (config → catalog → consult map) |
| orch.pipeline.project-scoped-queues | universal | conforms | Meteorite child scoped correctly |
| orch.pipeline.status-gates-skill-entry | universal | conforms | reviewed at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | no statute authoring |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns tests/bible |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | assignee remains Hedy |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | engineer through Tests Passed |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path product commits |

**Active-set count:** 64 rows from registry § Harvested corpus (header cites 65; no additional active row opened for this diff).

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| pattern.config.config-block | conforms | optional `company_stem` + `company_stem_response_key` added to `TASK_CONFIG["qualify_meteorite"]` with asserts |
| pattern.batch.entity-agent-responses | conforms | enrich maps RESPONSE field onto packet output; no new entity-ref persistence mechanics |
| pattern.agent.prompt-persist-before-provider | needs-discussion | cited in plan traceability but catalog `status: proposed` — Joan precedent; no new persist sequencing in this diff |

## Plan adherence

- **Stage 1:** `company_stem` optional str in `items_schema`; `company_stem_response_key` literal; asserts match plan. No `METEORITE_CONFIG` edits in engineer commits.
- **Stage 2:** `qualify_meteorite` `cache_prompt` gains COMPANY STEM rules (candidate-self → email → slug → empty); `user_prompt` asks for `company_stem`; `updated_at` refreshed; AST-756 twin synced.
- **Stage 3:** `enrich_meteorite_land_packet` maps stripped Ruth stem onto each `out_jobs` item; land debug detail includes `company_stem={…!r}`; dispatch success debug appends stem when non-empty; `agent.py` docstring documents optional RESPONSE field. No `ensure_meteorite_company` / attach calls.
- **Scope / siblings:** AST-1493 dependency merged via `merge-resume`; AST-1495 attach wiring correctly deferred.
- **Estimate (3):** Footprint fits — config + catalog + thin consult/agent map + Betty tests.
- **Tests:** Betty covers schema asserts, catalog twin, enrich map/strip/debug, dispatch debug stem.

## Findings

### fix-now

(none)

### discuss

- **Location:** Plan traceability — `pattern.agent.prompt-persist-before-provider`
- **Finding:** Pattern remains `status: proposed`; plan cites it for existing `do_task` sequencing only.
- **Recommendation:** Citation hygiene / parent catalog follow-up (Joan already flagged). Not blocking — implementation does not claim new persist behavior.

### advisory

- **Location:** `data/admin/agent_task.json` commit `83257745`
- **Finding:** Git diff shows ~48 hunks, but parsed JSON differs on only the `qualify_meteorite` current row; remainder is `ensure_ascii=True` re-serialize (em-dash/arrow escapes), semantically identical.
- **Recommendation:** Accept for this ticket; future catalog edits should touch only the target row to keep review noise down.

- **Location:** Three-dot diff vs `origin/dev`
- **Finding:** Publish ref includes stacked AST-1493 product + docs (Radia PROCEED `cedbfa68`) and unrelated test-only commits (AST-1486/1502/1504) not in AST-1494 scope gate.
- **Recommendation:** AST-1494 engineer commits are scope-clean; full-branch diff is expected epic-line topology.

- **Location:** Joan validate attachment
- **Finding:** APPROVED with no `Excluded` statute table.
- **Recommendation:** Note `no plan-rubric Excluded table attached` — not blocking.

## What's solid

- Config key indirection (`company_stem_response_key`) with asserts prevents schema/map drift.
- Enrich always emits `company_stem` key (empty string when Ruth omits) — ready for AST-1495 attach.
- Dispatch debug stem is gated, non-empty only, and does not persist onto job rows (correct partition).
- Ruth prompt teaches three stem cases without duplicating `meteorite-self` in `TASK_CONFIG`.
- Betty tests lock map, strip, debug detail, and dispatch debug paths.

## Frame diff

- `qualify_meteorite` RESPONSE schema gains optional `company_stem`.
- Ruth catalog prompts teach sender / self / slug stem discernment from CONTENT.
- `enrich_meteorite_land_packet` output jobs carry `company_stem` from Ruth RESPONSE.
- Dispatch `qualify_meteorite` success debug may include `company_stem` when present.

## Notes

- Engineer product tip: `317f3dc8`; publish tip after merge-tests: `60f0d40e`.
- C7 complete — Chuckles may append to issue doc, push `docs(AST-1494): Radia review — clean`, post slim upshot, advance to **Review Posted** → **User Testing**.

context_tokens≈62000

---

```
[code-rubric] PROCEED (Commit: 60f0d40e) Ruth stem discernment clean
```
