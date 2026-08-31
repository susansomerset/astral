# AST-1529 — stage_meteorite catalog + config literals

**Linear:** [AST-1529](https://linear.app/astralcareermatch/issue/AST-1529/stage-meteorite-catalog-config-literals-generalize-meteorite-ingress)  
**Parent:** [AST-1527](https://linear.app/astralcareermatch/issue/AST-1527/generalize-meteorite-ingress-point) — Generalize Meteorite Ingress Point  
**Publish ref:** `sub/AST-1527/AST-1529-stage-meteorite-catalog-config`

Closed-outcome Ruth hop vocabulary for ingress classify: `TASK_CONFIG["stage_meteorite"]`, named `STAGE_METEORITE_CONFIG` (six outcome literals + source-ref prefix map), and a live `agent_task` row that teaches those outcomes. Retires live `meteorite_email` parse_modes / shared mailbox↔parse task_key coupling so `METEORITE_EMAIL_MAILBOX_CONFIG.task_key` stays the poller only. Does **not** implement core stage orchestration (**AST-1530**) or caller cutover (**AST-1531**).

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/utils/config.py` — **modified** — add `stage_meteorite` TASK_CONFIG + stage config block (closed outcome literals, source-handle / source-ref prefix kinds); split mailbox `meteorite_email` from retired parse coupling (`METEORITE_EMAIL_PARSE_CONFIG` / shared task_key assert).
- `data/admin/agent_task.json` — **modified** — add `stage_meteorite` catalog row (prompts + schema lockstep with TASK_CONFIG); retire live `meteorite_email` parse prompts so parse and stage are not both live.
- `src/utils/config.py` — **new** TASK_CONFIG[`stage_meteorite`] response schema (outcome enum + job scrap fields); **new** stage config block for the six outcome literals and source-ref prefix map; **modified** / **retire** `METEORITE_EMAIL_PARSE_CONFIG` parse_modes coupling and the assert that mailbox task_key equals parse task_key; keep `METEORITE_EMAIL_MAILBOX_CONFIG.task_key` as `meteorite_email`.
- `data/admin/agent_task.json` — **new** `stage_meteorite` row (system/user prompts teaching the six outcomes); **modified** retire or empty parse-mode prompts on `meteorite_email` so only stage is the classify hop.

All Files Changed / Stages stay inside that set.

**Out of scope (siblings):**

- Public stage entry / scrap map / `land_meteorite` call — **AST-1530** (`meteorite.py` / `consult.py` / optional `agent.py` wire).
- Mailbox `_handle_bound`, inbox Land / `fetch_email`, `contact_land_meteorite` cutover — **AST-1531**.
- Rewrites of `land_meteorite` or `qualify_meteorite`.
- `docs/uat-fixtures/AST-756/expected-agent_task.json` twin — **not** in this ticket’s Scope (statute note: fixture may mirror; seed SSOT is `data/admin/agent_task.json`). Betty syncs the twin at **qa-child** if component tests require it; do **not** edit the fixture in this build.

**Depends on:** none (Bang !! — first child). Sibling **AST-1530** consumes this catalog.

**AC partition (this ticket):** Parent AC7 only — `TASK_CONFIG` / `agent_task` expose `stage_meteorite` with the six outcome literals; live `meteorite_email` parse_modes classify is not also live; mailbox poller key remains `meteorite_email`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `STAGE_METEORITE_CONFIG` + `TASK_CONFIG["stage_meteorite"]`; retire `TASK_CONFIG["meteorite_email"]` Ruth parse entry; strip `parse_modes` + mailbox↔parse shared-task_key assert from `METEORITE_EMAIL_PARSE_CONFIG`; keep mailbox fold helpers; inventory comments | utils |
| `data/admin/agent_task.json` | Add live `stage_meteorite` Ruth row (prompts teach six outcomes); keep `meteorite_email` row empty / non-live (no parse prompts, no `agent_id`) | catalog |

## Stage 1: Config — `STAGE_METEORITE_CONFIG` + `TASK_CONFIG["stage_meteorite"]` + retire parse coupling

**Done when:** `STAGE_METEORITE_CONFIG` exposes the six outcome literals and source-ref prefix map; `TASK_CONFIG["stage_meteorite"]` exists with outcome `enum` lockstepped to those literals and a jobs scrap schema; `TASK_CONFIG` has **no** live `meteorite_email` Ruth parse entry; `METEORITE_EMAIL_PARSE_CONFIG` has **no** `parse_modes` and **no** assert tying mailbox `task_key` to parse `task_key`; `METEORITE_EMAIL_MAILBOX_CONFIG["task_key"] == "meteorite_email"`; `python3 -m py_compile src/utils/config.py` succeeds (repo venv if needed: `~/astral/.venv/bin/python`).

1. In `src/utils/config.py` header inventory (near the `METEORITE_EMAIL_MAILBOX_CONFIG` / `METEORITE_EMAIL_PARSE_CONFIG` bullets), add a bullet for `STAGE_METEORITE_CONFIG` — closed outcome literals + source-ref prefixes for ingress classify (`stage_meteorite`). Update the `METEORITE_EMAIL_PARSE_CONFIG` bullet to say it is a **retired fold stub** (legacy admin / `_resolve_task_prompts` fallback only) — **not** a live Ruth parse modes catalog.

2. Immediately **after** `METEORITE_EMAIL_MAILBOX_CONFIG` asserts (and **before** the current `METEORITE_EMAIL_PARSE_CONFIG` block), insert:

```python
# AST-1529: closed-outcome ingress classify (stage_meteorite). Outcome strings and
# source-ref prefixes are config SSOT — core/prompts must not invent parallel sets.
STAGE_METEORITE_CONFIG = {
    "task_key": "stage_meteorite",
    "outcomes": (
        "single_jd_no_link",
        "single_jd_with_more",
        "multi_jd_inline",
        "link_list",
        "not_job_content",
        "not_original_posting",
    ),
    # source kind → prefix for synthesized job_link / company_job_id when no ATS URL.
    "source_ref_prefixes": {
        "email": "email-",
        "slack": "slack-",
        "paste": "paste-",
    },
    # Partitions for AST-1530 scrap map (same literal strings as outcomes — not a second vocabulary).
    "landable_outcomes": (
        "single_jd_no_link",
        "single_jd_with_more",
        "multi_jd_inline",
        "link_list",
    ),
    "text_source_ref_outcomes": (
        "single_jd_no_link",
        "multi_jd_inline",
    ),
    "url_scrape_outcomes": (
        "single_jd_with_more",
        "link_list",
    ),
    "skip_outcomes": (
        "not_job_content",
        "not_original_posting",
    ),
}
```

3. Immediately after that dict, add asserts (exact membership / disjoint partitions):

- `STAGE_METEORITE_CONFIG["task_key"] == "stage_meteorite"`
- `len(STAGE_METEORITE_CONFIG["outcomes"]) == 6`
- `set(STAGE_METEORITE_CONFIG["landable_outcomes"]) | set(STAGE_METEORITE_CONFIG["skip_outcomes"]) == set(STAGE_METEORITE_CONFIG["outcomes"])`
- `set(STAGE_METEORITE_CONFIG["landable_outcomes"]).isdisjoint(STAGE_METEORITE_CONFIG["skip_outcomes"])`
- `set(STAGE_METEORITE_CONFIG["text_source_ref_outcomes"]) | set(STAGE_METEORITE_CONFIG["url_scrape_outcomes"]) == set(STAGE_METEORITE_CONFIG["landable_outcomes"])`
- `set(STAGE_METEORITE_CONFIG["text_source_ref_outcomes"]).isdisjoint(STAGE_METEORITE_CONFIG["url_scrape_outcomes"])`
- `STAGE_METEORITE_CONFIG["source_ref_prefixes"]["email"] == "email-"`
- `set(STAGE_METEORITE_CONFIG["source_ref_prefixes"]) == {"email", "slack", "paste"}`
- every prefix value is a non-empty `str` ending with `"-"`

4. In `TASK_CONFIG`, **delete** the entire `"meteorite_email": { ... }` entry (the Ruth parse schema under that key — AST-1089/1212). Do **not** leave a dual live parse + stage TASK_CONFIG pair.

5. In the same region (immediately after `"qualify_meteorite"` is fine), add:

```python
# AST-1529: ingress classify — candidate-bound blob + source handle; not a job claim queue.
"stage_meteorite": {
    "response_format": "json",
    "output_type": "fields",
    "scored": False,
    "response_schema": {
        "outcome": {
            "type": "str",
            "required": True,
            # enum assigned after STAGE_METEORITE_CONFIG (lockstep) — see below
        },
        "jobs": {
            "type": "list",
            "required": True,
            "items_schema": {
                "job_title": {"type": "str", "required": False},
                "job_link": {"type": "str", "required": False},
                "company_job_id": {"type": "str", "required": False},
                "jd_text": {"type": "str", "required": False},
                "employer_name": {"type": "str", "required": False},
            },
        },
    },
    "context_format": "stage_meteorite_{index}",
    "entity_type": None,
    "requires_candidate_key": True,
    "trigger_state": None,
    "agent_task": "stage_meteorite",
},
```

6. Immediately after the `STAGE_METEORITE_CONFIG` asserts (step 3), wire enum + TASK_CONFIG lockstep:

```python
TASK_CONFIG["stage_meteorite"]["response_schema"]["outcome"]["enum"] = list(
    STAGE_METEORITE_CONFIG["outcomes"]
)
assert TASK_CONFIG["stage_meteorite"]["agent_task"] == STAGE_METEORITE_CONFIG["task_key"]
assert TASK_CONFIG["stage_meteorite"]["requires_candidate_key"] is True
assert TASK_CONFIG["stage_meteorite"]["entity_type"] is None
assert TASK_CONFIG["stage_meteorite"]["trigger_state"] is None
assert TASK_CONFIG["stage_meteorite"]["scored"] is False
assert list(TASK_CONFIG["stage_meteorite"]["response_schema"]["outcome"]["enum"]) == list(
    STAGE_METEORITE_CONFIG["outcomes"]
)
assert "meteorite_email" not in TASK_CONFIG
```

⚠️ **Decision — enum after named block:** `TASK_CONFIG` is defined above the meteorite named-block region. Assign `outcome["enum"]` from `STAGE_METEORITE_CONFIG["outcomes"]` after that block exists (same pattern as other late locksteps). Do **not** duplicate the six strings as a second module-level tuple.

⚠️ **Decision — outcome partitions in `STAGE_METEORITE_CONFIG`:** Parent types 1–4 land / 5–6 skip and text vs URL scrap paths are the same six literals, partitioned for AST-1530. Putting partitions here keeps `astral.standards.no-hardcoded-sets` for sibling core; this ticket still only owns the vocabulary block.

⚠️ **Decision — remove `TASK_CONFIG["meteorite_email"]`:** AC7 requires parse_modes classify not also live. Empty `agent_task` prompts alone leave a callable TASK_CONFIG schema. Deleting the TASK_CONFIG entry makes `stage_meteorite` the only Ruth classify hop. Mailbox identity stays `METEORITE_EMAIL_MAILBOX_CONFIG["task_key"] == "meteorite_email"`.

7. Replace `METEORITE_EMAIL_PARSE_CONFIG` so it is a **fold stub only** (keep the symbol name — `agent.py` / `api_admin` / `dispatcher` still import `is_meteorite_email_mailbox_task_key` / `METEORITE_EMAIL_PARSE_CONFIG`; those files are **out of scope**):

```python
# AST-1529: parse_modes Ruth classify RETIRED — live classify is stage_meteorite.
# Stub retained for admin mailbox fold + agent._resolve_task_prompts legacy fallback.
METEORITE_EMAIL_PARSE_CONFIG = {
    "task_key": "meteorite_email",
    "legacy_agent_task_key": "parse_meteorite_email",
    "admin_entity_type": "candidate",
}
```

8. Replace the old PARSE asserts with:

- `METEORITE_EMAIL_PARSE_CONFIG["task_key"] == "meteorite_email"`
- `METEORITE_EMAIL_PARSE_CONFIG["legacy_agent_task_key"] == "parse_meteorite_email"`
- `METEORITE_EMAIL_PARSE_CONFIG["admin_entity_type"] == "candidate"`
- `"parse_modes" not in METEORITE_EMAIL_PARSE_CONFIG`
- **Do not** assert `METEORITE_EMAIL_MAILBOX_CONFIG["task_key"] == METEORITE_EMAIL_PARSE_CONFIG["task_key"]` (retire that coupling). Both may still equal `"meteorite_email"` independently; mailbox assert `METEORITE_EMAIL_MAILBOX_CONFIG["task_key"] == "meteorite_email"` already exists — leave it.

9. Leave `is_meteorite_email_mailbox_task_key` reading `METEORITE_EMAIL_PARSE_CONFIG["task_key"]` / `legacy_agent_task_key` unchanged in behavior. Leave `dispatch_task_admin_defaults` meteorite fold that uses `METEORITE_EMAIL_PARSE_CONFIG["admin_entity_type"]` unchanged.

10. Update any remaining comments in `config.py` that say AST-1090 callers pass `PARSE_MODE:` / `parse_modes` as live guidance — mark historical / retired; point live classify at `STAGE_METEORITE_CONFIG` / `stage_meteorite`.

11. Compile gate: `python3 -m py_compile src/utils/config.py` (or `~/astral/.venv/bin/python -m py_compile …`). Import-smoke if env secrets are present: `from src.utils import config as c` then assert the Done-when predicates above.

## Stage 2: Catalog — `stage_meteorite` agent_task row + keep `meteorite_email` non-live

**Done when:** `data/admin/agent_task.json` has a current `stage_meteorite` row with `agent_id` `college_intern_ruth`, non-empty prompts that name exactly the six `STAGE_METEORITE_CONFIG["outcomes"]` strings, `task_name`/`task_key` `stage_meteorite`, Meteorite Review grouping; `meteorite_email` row remains without parse prompts and without `agent_id` (not a live classify hop); JSON still parses as a non-empty list.

1. In `data/admin/agent_task.json`, **append** (or insert among Meteorite Review rows) a new object:

| Field | Value |
|-------|--------|
| `task_key` | `stage_meteorite` |
| `task_name` | `stage_meteorite` |
| `task_key_uuid` | new random UUID4 string (same shape as sibling rows) |
| `agent_id` | `college_intern_ruth` |
| `task_group_name` | `Meteorite Review` |
| `task_group_order` | `4500` |
| `task_seq` | `2.0` (before `qualify_meteorite` at `2.5`) |
| `current` | `1` |
| `run_next` | `""` |
| `updated_at` | ISO UTC now at implement time |
| `system_prompt` | `""` (match `qualify_meteorite` — instructions live in cache/user) |
| `cache_prompt` / `user_prompt` | per steps 2–3 |
| `cache_prompt_b`–`d`, `nocache_prompt` | `""` |

2. **`cache_prompt`** (single string) must teach, in order:

- Role: classify one candidate-bound ingress blob (email HTML / Slack paste / inspector dump / forward). Return **exactly one** `outcome` from the closed set — never invent outcome strings.
- List the six outcomes with the parent meanings (verbatim labels):
  1. `single_jd_no_link` — one original JD in the blob; no posting URL worth scraping → one jobs item; `job_link` / `company_job_id` will be source-refs (caller synthesizes); put visible JD in `jd_text`.
  2. `single_jd_with_more` — one JD plus a best “more” / posting URL → one jobs item; that URL in `job_link`; optional blob text in `jd_text`; `company_job_id` may be omitted (source-ref later).
  3. `multi_jd_inline` — several original JDs inline, no scrape list → one jobs item per JD; source-ref identity; `jd_text` per item.
  4. `link_list` — series of job-page URLs → one jobs item per URL with that URL as `job_link`.
  5. `not_job_content` — not job content → `jobs: []`; do not invent scraps.
  6. `not_original_posting` — reply/thread/noise about a job already in play → `jobs: []`.
- Source-ref rule: do **not** invent UUIDs; do **not** use company homepages as `job_link` when the outcome is a text/source-ref type; do not scrape.
- Do not emit grade vectors. Do not call this `meteorite_email` / parse_modes.

⚠️ **Decision — outcome strings in prompts:** Prompts must spell the six literals **exactly** as in `STAGE_METEORITE_CONFIG["outcomes"]` (config remains SSOT; prompts teach the same strings). Do not use “type 1” / ticket ids as outcome labels (`astral.standards.names-not-ticket-ids`).

3. **`user_prompt`** (one string): Instruct Ruth to read CONTENT, return JSON with `outcome` + `jobs` matching the schema; pick exactly one closed outcome; empty `jobs` for skip outcomes; no grade vectors.

4. Confirm the existing `meteorite_email` row stays **non-live**: `agent_id` `""`, `system_prompt` / `user_prompt` / `cache_prompt*` / `nocache_prompt` all empty (already true on tip — do not restore PARSE_MODE prompts). `task_seq` may stay `999`.

5. Do **not** add `parse_meteorite_email` back. Do **not** edit `docs/uat-fixtures/AST-756/expected-agent_task.json` (out of Scope).

6. Validate: `python3 -c 'import json; json.load(open("data/admin/agent_task.json"))'` and a one-liner that finds `task_key == "stage_meteorite"` with `agent_id == "college_intern_ruth"` and all six outcome substrings present in `cache_prompt`.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish to `origin/sub/AST-1527/AST-1529-stage-meteorite-catalog-config` after each stage (build-child).
- No files outside the Files Changed table.
- Ambiguity / drift → stop, comment on **parent** AST-1527 with the Stage blocked format from plan-child, wait.
- Do not implement AST-1530/1531 behavior in this ticket.

## Estimate

Confirm Chuckles estimate: 5 — agree

Config + Ruth prompt catalog for six outcomes on a known pattern (AST-1089 lineage); no core orchestration in this child.

## Joan validate

```text
[plan-rubric]
**Rubric:** plan-rubric
**Ticket:** AST-1529
**Overall:** APPROVED
**Publish ref:** `origin/sub/AST-1527/AST-1529-stage-meteorite-catalog-config` @ `ca0a28c2724652c4ba4108299f57387a84b5512a`

## Traceability
AC7 → Stage 1 (`STAGE_METEORITE_CONFIG`, `TASK_CONFIG["stage_meteorite"]`, retire `meteorite_email` TASK_CONFIG + `parse_modes` coupling) + Stage 2 (`agent_task` `stage_meteorite` row, `meteorite_email` stays non-live); mailbox poller `meteorite_email` preserved via `METEORITE_EMAIL_MAILBOX_CONFIG`.

## Findings

### acceptable — `STAGE_METEORITE_CONFIG` partition keys (`landable_outcomes`, `text_source_ref_outcomes`, `url_scrape_outcomes`, `skip_outcomes`)
Partition tuples reuse the same six literals for AST-1530 scrap-map wiring. Slightly beyond the ticket Scope prose (“six outcome literals and source-ref prefix map”), but same vocabulary, asserted disjointness, and explicitly owned as config SSOT for the sibling — not a second invented set. No plan change required.

### acceptable — No `## Self-assessment` section
Catalog-only child on a known AST-1089 lineage; Estimate confirm line present. Honest complexity signal without a formal self-assessment block.

context_tokens≈28000
```

## Review (build stub)

**Publish ref:** `origin/sub/AST-1527/AST-1529-stage-meteorite-catalog-config`
**Plan path:** `docs/features/meteorite/ast-1529-stage-meteorite-catalog-config.md`

**Built tip:** `25bde8541e88952db1b56f538c9f89bafe0084e4` (`25bde854`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `87a1bfa2` | `STAGE_METEORITE_CONFIG` + `TASK_CONFIG["stage_meteorite"]`; retire parse_modes / mailbox↔parse assert; drop `TASK_CONFIG["meteorite_email"]` |
| 2 | `25bde854` | `agent_task` `stage_meteorite` Ruth row; `meteorite_email` stays non-live |

**Betty note:** AST-756 fixture twin intentionally out of Scope — sync at qa-child if component tests require it.


## Radia review

`[code-rubric] revision=2`  
**Rubric:** code-rubric.v2  
**Ticket:** AST-1529  
**Publish ref:** `origin/sub/AST-1527/AST-1529-stage-meteorite-catalog-config` @ `9925c5d159df706ef80b7b87dd5b5228a6937c44`  
**Overall:** CLEAN  

**Diff baseline:** `origin/dev...origin/sub/AST-1527/AST-1529-stage-meteorite-catalog-config` (10 paths; engineer `src/utils/config.py` + `data/admin/agent_task.json`; Betty merge-tests: component tests, test-bible, AST-756 fixture twin)

## Statutes checked

| id | tier | verdict | one-line |
|----|------|---------|----------|
| astral.agent.confidence-bounds | scoped | not-applicable | no `src/core/agent` logic changes |
| astral.agent.do-task-delegation | scoped | not-applicable | no `do_task` / delegation changes |
| astral.agent.grade-vector-validation | scoped | not-applicable | no grade-vector paths touched |
| astral.batch.batch-id-first | scoped | not-applicable | no batch-id paths |
| astral.batch.batch-id-format | scoped | not-applicable | no batch-id format changes |
| astral.batch.claim-process-release | scoped | not-applicable | no dispatcher/claim helpers changed |
| astral.batch.entity-agent-responses-latest-only | scoped | not-applicable | no entity-agent-responses paths |
| astral.config.config-source-of-truth | scoped | conforms | `STAGE_METEORITE_CONFIG` + `TASK_CONFIG["stage_meteorite"]` added as named config blocks; parse stub retained |
| astral.config.secrets-and-env-specific-from-environ | scoped | not-applicable | no env/secret surface changes |
| astral.debug.no-repo-root-artifacts-dir | scoped | not-applicable | no debug artifact paths |
| astral.debug.spikes-under-debug-dir | scoped | not-applicable | no spike files |
| astral.dispatch.seed-auto-false | scoped | not-applicable | no dispatch seed changes |
| astral.dispatch.run-next-is-chain-authority | scoped | not-applicable | no `run_next` wiring |
| astral.docs.features-single-file-per-ticket | scoped | conforms | plan doc is the single AST-1529 feature file |
| astral.git.betty-no-src-or-features | scoped | conforms | Betty lane owns tests/bible/fixture; engineer build stayed on config + catalog |
| astral.git.engineer-test-tree-ban | scoped | conforms | engineer commits limited to `src/utils/config.py` + `data/admin/agent_task.json` |
| astral.layers.core-vs-external-bright-line | scoped | not-applicable | utils-only product change |
| astral.layers.import-direction | scoped | conforms | no new cross-layer imports |
| astral.layers.scripts-exempt-from-layer-rules | scoped | not-applicable | no `scripts/` changes |
| astral.layers.ui-config-driven-business-logic | scoped | not-applicable | no UI changes |
| astral.idioms.coat-check-never-store-empty | scoped | not-applicable | no coat-check paths |
| astral.idioms.render-verdict-orchestrates-consult | scoped | not-applicable | no consult/render paths |
| astral.idioms.require-auth-on-protected-endpoints | scoped | not-applicable | no API auth surface |
| astral.seed.agent-tables-in-repo-json | scoped | conforms | live `stage_meteorite` Ruth row; non-empty `agent_task.json`; `meteorite_email` stays poller shell |
| astral.seed.archie-catalog-wins | scoped | conforms | repo JSON is SSOT; fixture twin lockstep test added |
| astral.seed.boot-only-not-hot-path | scoped | not-applicable | no boot/hot-path wiring |
| astral.seed.define-approved | scoped | not-applicable | no new seed catalog |
| astral.seed.operator-rows-stay-deleted | scoped | conforms | no operator-row resurrection |
| astral.seed.other-via-coverage-join | scoped | not-applicable | no coverage-join paths |
| astral.standards.data-raises-caller-logs | scoped | not-applicable | no data-layer changes |
| astral.standards.database-header-inventory | scoped | not-applicable | no `src/data/**` changes |
| astral.standards.debug-contract-gated | scoped | not-applicable | no `debug=` emission added |
| astral.standards.dry-and-focused-functions | scoped | conforms | focused config/catalog delta |
| astral.standards.in-scope-only | scoped | conforms | matches AC7 partition; no AST-1530/1531 orchestration smuggled |
| astral.standards.logging-via-utils | scoped | conforms | no `print`/raw logging in diff |
| astral.standards.names-not-ticket-ids | scoped | conforms | six outcome literals are semantic names; prompts teach literals not ticket ids |
| astral.standards.no-cross-contamination | scoped | conforms | meteorite ingress vocabulary isolated to new block |
| astral.standards.no-hardcoded-sets | scoped | conforms | outcomes/partitions/prefixes live in `STAGE_METEORITE_CONFIG`; enum lockstep wired |
| astral.standards.public-then-helpers | scoped | conforms | named public config block + asserts |
| astral.standards.utils-data-late-import-only | scoped | not-applicable | no new utils→data imports |
| astral.state.core-decides-transitions | scoped | not-applicable | no state-machine edits |
| astral.state.job-prior-states-enforced | scoped | not-applicable | no job-state edits |
| astral.state.no-daisy-chain-in-run | scoped | not-applicable | no `run()` chain edits |
| astral.ui.frontend-file-placement | scoped | not-applicable | no frontend files |
| astral.ui.naming-conventions | scoped | not-applicable | no UI naming surface |
| astral.ui.single-gunicorn-worker | scoped | not-applicable | no server config |
| orch.git.betty-merge-tests-one-sha | universal | conforms | `merge-tests(AST-1529)` present on tip |
| orch.git.commit-vocabulary | universal | conforms | `code`/`docs`/`test`/`merge-tests` vocabulary respected |
| orch.git.flow-direction-inviolable | universal | conforms | sub on ftr topology |
| orch.git.ftr-sub-topology | universal | conforms | publish ref matches child pattern |
| orch.git.merge-on-checkout | universal | conforms | no checkout violations in diff |
| orch.git.no-cherry-pick-rebase-force | universal | conforms | no forbidden git ops in artifact |
| orch.git.no-dev-agent-branches | universal | conforms | no agent dev branches |
| orch.git.one-epic-worktree-per-parent | universal | conforms | review in `astral-AST-1527` worktree |
| orch.git.three-permanent-branches | universal | conforms | diff vs `origin/dev` only |
| orch.pipeline.call-susan-for-product-decisions | universal | conforms | no unresolved product forks |
| orch.pipeline.plan-is-bible | universal | conforms | implementation matches both plan stages |
| orch.pipeline.project-scoped-queues | universal | conforms | n/a to diff |
| orch.pipeline.status-gates-skill-entry | universal | conforms | reviewed at Tests Passed |
| orch.roles.archie-approves-statutes | universal | conforms | n/a |
| orch.roles.betty-owns-test-tree | universal | conforms | Betty owns test/bible/fixture delta |
| orch.roles.chuckles-never-ticket-assignee | universal | conforms | n/a |
| orch.roles.engineer-assignee-through-resolve | universal | conforms | Ada assignee preserved |
| orch.roles.pre-commit-path-bans | universal | conforms | no banned-path commits observed |

**Straggler (C4):** Joan plan-rubric APPROVED attached; no Excluded-statute list — no stragglers.

## Pattern conformance

| id | verdict | one-line |
|----|---------|----------|
| none cited | — | Plan has no "Patterns to reuse" line; diff shape matches uncited `pattern.config.config-block` (named block + asserts + TASK_CONFIG lockstep) |

## Plan adherence

**Stage 1 (config):** Delivers `STAGE_METEORITE_CONFIG` with six outcomes, source-ref prefixes, and asserted landable/text/url/skip partitions; adds `TASK_CONFIG["stage_meteorite"]` with jobs scrap schema and late enum lockstep; removes `TASK_CONFIG["meteorite_email"]`; retires `parse_modes` and mailbox↔parse task_key assert while keeping `METEORITE_EMAIL_MAILBOX_CONFIG["task_key"] == "meteorite_email"` and fold stub behavior.

**Stage 2 (catalog):** Live `stage_meteorite` Ruth row (`college_intern_ruth`, `task_seq` 2.0, Meteorite Review 4500); all six outcome literals present in `cache_prompt`; `meteorite_email` row non-live (`agent_id` empty, prompts empty, `task_seq` 999); `qualify_meteorite` at 2.5.

**Estimate (5):** Footprint matches — config block + catalog row + Betty test/bible/fixture fold; no core orchestration.

**Cross-ticket boundaries:** No `meteorite.py` / `consult.py` / inbox cutover (AST-1530/1531). AST-756 fixture sync landed via Betty merge-tests (plan build note said defer; qa-child path is correct).

**C6 lenses (§5a–g):** No layer/import/logging/debug/external violations in changed `src/utils/config.py`. No silent failure or fallback concerns introduced.

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

1. **`src/core/agent.py` comment drift (out of diff):** `_resolve_task_prompts` still comments that "TASK_CONFIG key is meteorite_email" (AST-1212). Harmless on this tip but misleading after AST-1529 — suggest AST-1530/1531 tidy to `stage_meteorite` when callers cut over.

2. **Prompt wording vs plan verbatim:** Plan step cited `Do not call this meteorite_email / parse_modes`; catalog ships `This is not meteorite_email / parse_modes.` — intent met; `TestAst1529StageMeteoriteCatalogRow` OR-assert covers it.

3. **Epic merge ordering:** Removing `TASK_CONFIG["meteorite_email"]` means any future `do_task("meteorite_email")` call fails at `TASK_CONFIG.get` before prompts. No such caller on this tip (`meteorite_email` runner uses direct land/scrape, not Ruth `do_task`). Siblings AST-1530/1531 should land before any revived Ruth-parse path on ftr.

## What's solid

- Config SSOT pattern is textbook: single vocabulary block, exhaustive asserts, enum wired from block not duplicated inline.
- Parse retirement is clean: `parse_modes` gone, fold stub preserved for admin/`_resolve_task_prompts`, mailbox poller identity untouched.
- Betty coverage is tight: config shell, catalog row, schema validation, fixture lockstep, superseded AST-1089/1144 tests retired/skipped appropriately.

## Frame diff

- `src/utils/config.py`: add `STAGE_METEORITE_CONFIG`; replace `TASK_CONFIG["meteorite_email"]` with `TASK_CONFIG["stage_meteorite"]`; strip `METEORITE_EMAIL_PARSE_CONFIG["parse_modes"]` + shared task_key assert; update header inventory comments.
- `data/admin/agent_task.json`: add live `stage_meteorite` Ruth row; keep `meteorite_email` non-live poller shell; adjust Meteorite Review sequencing (`stage_meteorite` 2.0, `qualify_meteorite` 2.5).
- Betty merge-tests: component tests + test-bible + `docs/uat-fixtures/AST-756/expected-agent_task.json` lockstep.

context_tokens≈42000
