# AST-1036 — Simple Resume Parse function
**Component:** administrator  
**Children:** AST-1037, AST-1038  
**Linear archived:** AST-1036 2026-08-05; AST-1037 2026-08-05; AST-1038 2026-08-05  

## Ledger

| when (PT) | ticket | phase | sha | subject |
|---|---|---|---|---|
| 2026-07-29 08:15 | AST-1037 | docs | `4f35545bb` | docs(AST-1037): plan — Ruth simple session-resume parse task |
| 2026-07-29 08:20 | AST-1037 | docs | `fd31b3b43` | docs(AST-1037): plan revise — normalize keys in config |
| 2026-07-29 08:46 | AST-1037 | code | `80ea40e78` | code(AST-1037): Ruth simple_resume_parse task + shared schema normalize keys |
| 2026-07-29 08:46 | AST-1037 | docs | `9eef1b183` | docs(AST-1037): build review stub tip |
| 2026-07-29 08:51 | AST-1037 | test | `545225d45` | test(AST-1037): Ruth simple_resume_parse catalog + shared schema coverage |
| 2026-07-29 08:51 | AST-1037 | merge-tests | `46e493a96` | merge-tests(AST-1037): origin/tests 545225d45280c6ee75591ea4442d4488ca1f9b6c |
| 2026-07-29 08:56 | AST-1037 | docs | `151cd9a8c` | docs(AST-1037): Radia review — findings |
| 2026-07-29 08:57 | AST-1037 | docs | `5f14c5e7d` | docs(AST-1037): Radia review — tip SHA |
| 2026-07-29 08:58 | AST-1037 | resolve | `10d1866ff` | resolve(AST-1037): — clean |
| 2026-07-29 09:02 | AST-1038 | docs | `a81c4939e` | docs(AST-1038): plan — wire Session Resume Parse to Ruth task |
| 2026-07-29 09:07 | AST-1038 | code | `2cf538f4a` | code(AST-1038): wire session resume parse to simple_resume_parse |
| 2026-07-29 09:07 | AST-1038 | docs | `d37b16b8e` | docs(AST-1038): build review stub tip |
| 2026-07-29 09:09 | AST-1038 | test | `b088c35de` | test(AST-1038): session parse wires to Ruth simple_resume_parse |
| 2026-07-29 09:09 | AST-1038 | merge-tests | `772afdc4f` | merge-tests(AST-1038): origin/tests b088c35de0f02c7deee2ac2d35314ae1a3f11312 |
| 2026-07-29 09:12 | AST-1038 | docs | `054d26cfc` | docs(AST-1038): Radia review — findings |
| 2026-07-29 09:12 | AST-1038 | docs | `1c62a5eab` | docs(AST-1038): Radia review — tip SHA |
| 2026-07-29 09:13 | AST-1038 | resolve | `c83290867` | resolve(AST-1038): — clean |
| 2026-07-29 09:15 | AST-1036 | prep-uat | `5278c3fed` | prep-uat(AST-1036): rebuild merge ticket log |
| 2026-08-05 14:55 | AST-1037 | docs | `12863b3eb` | docs(AST-1037): archive Linear issue content |
| 2026-08-05 14:55 | AST-1038 | docs | `d9401cabc` | docs(AST-1038): archive Linear issue content |
| 2026-08-05 14:58 | AST-1036 | docs | `fb4c2565e` | docs(AST-1036): archive Linear issue content |

## Epic — AST-1036
_Archived: 2026-08-05 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1036/simple-resume-parse-function · Status at archive: Archive · Project: Astral Administrator · Assignee: chuckles · Priority / estimate: High / — · Blocked by / blocks / related: —_

### Purpose

Session Resume Paste is a stop-gap Admin workbench until the full resume generation pipeline ships. Today Parse still runs Judith’s full `craft_resume_base` hop — expensive “think and rewrite” work for what is really rote paste→JSON shaping. This epic swaps that hop to Ruth (Little brain) with a much simpler parse prompt so Susan can keep using Paste → Parse → Open HTML without burning big-brain tokens on translation.

### Functional scope

* **Dedicated simple parse task.** Introduce a Ruth-owned agent task whose job is only to map pasted resume text into the existing session-resume JSON contract (structure + content fields the Paste screen and Open HTML already consume). The prompt instructs mechanical field placement — not rewrite, enrichment, LinkedIn synthesis, or “improve the resume.”
* **Session Resume Parse uses Ruth.** The Admin Session Resume Paste Parse path invokes that Ruth/Little task instead of Judith’s craft-base task. Success and failure responses stay compatible with the current paste screen and Open HTML flow (no candidate bind, no durable artifact write).
* **Paste-faithful mechanical rules stay in the simple prompt.** Rules already proven on this screen — preserve `__` / `~~` markers, competency bullet joins (not pipes), title vs tagline placement, and `<no bullet>` lead markers — remain explicit parse instructions so Open HTML quality does not regress when leaving Judith’s craft prompt.
* **Candidate craft path unchanged.** Candidate-bound resume craft / generation that uses Judith `craft_resume_base` keeps using that task and persona. This epic only changes the Admin session stop-gap path.
* **Observability.** Admin session parse continues to record cost/ledger visibility for the hop. When `debug=True`, the parse hop logs Style D found|recorded detail (index headers plus DEBUG_DETAIL_PREFIX working lines; long payloads truncated per Code Rules) — not only pass/fail.

### Architectural definition

* **Patterns to reuse**
  * `pattern.config.config-block` — new task definition and response schema live in `TASK_CONFIG` / repo agent_task seed; no inline magic sets.
  * `pattern.ui.admin-endpoint` — keep the existing Admin parse route thin; core owns the task swap; `@require_admin` / auth shape unchanged.
  * `pattern.layers.import-discipline` — UI calls Admin API; core calls `do_task`; no layer skipping.
* **New patterns proposed** — none.
* **Applicable statutes**
  * `astral.config.config-source-of-truth` — task key, schema, and brain/persona wiring from config + admin agent_task rows.
  * `astral.agent.do-task-delegation` — session parse still reaches the model only via `do_task`.
  * `astral.patterns.require-auth-on-protected-endpoints` — Admin parse remains auth-gated.
  * `astral.layers.ui-config-driven-business-logic` — React stays a caller; task choice is core/config.
  * `astral.layers.import-direction` — honor layer import direction on touched files.
  * `astral.standards.in-scope-only` — do not retouch unrelated craft/generation surfaces.
  * `astral.standards.debug-contract-gated` — Style D only when `debug=True` on touched backend debug paths.
  * `astral.standards.dry-and-focused-functions` / `astral.standards.public-then-helpers` — keep the session-parse entry focused; extract only if the wire forces it.
  * `astral.standards.no-hardcoded-sets` — no new inline enum/sets for task keys or schema.
  * `astral.standards.logging-via-utils` — logging through utils logger helpers.
  * `astral.docs.features-single-file-per-ticket` — one plan doc per child.

### Boundaries

* Does **not** replace or re-persona Judith `craft_resume_base` for candidate artifact generation / Manage Tasks craft flows.
* Does **not** implement the full resume generation pipeline this screen is bridging toward.
* Does **not** change Open HTML builder behavior, paste-page chrome, or session localStorage keys unless a tiny contract tweak is required to keep Parse→HTML working (prefer zero UI change).
* Does **not** change Session Cover Letter or other Admin session tools.
* Does **not** invent a new free-form JSON shape that breaks Open HTML or “View Parsed JSON.”
* Does **not** weaken paste-faithful mechanical rules already expected on this stop-gap screen.
* Adjacent in flight: Artifacts UAT children still tuning Judith craft-base prompts (e.g. under [AST-1019](https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies)) — those remain craft-base work; this epic moves **session** parse off that task onto Ruth.

### Acceptance criteria

1. From Admin **Session Resume Paste**, Parse runs a Ruth (Little) task — not Judith craft-base — and still returns structure-keyed JSON the screen already understands.
2. A successful Parse → Open HTML path still works without binding to the selected candidate and without writing candidate/job artifacts for the paste.
3. Dispatch/cost ledger for the Admin session-parse hop still records the run against the session sentinel path (same operational visibility Susan has today).
4. Paste-faithful mechanics remain observable on a known fixture: `__` / `~~` survive into content for HTML expand; competencies are not pipe-joined; specialty/keyword text lands in tagline (not mashed into title); `<no bullet>` leads remain lead markers for HTML.
5. Candidate-bound `craft_resume_base` / Judith craft behavior is unchanged when exercised outside this Admin session path.
6. With debug on, the session-parse hop emits Style D index + detail (found|recorded), not summary-only noise; with debug off, no new debug-contract lines.

### Dependencies and blockers

none.

Related context (not blockers): [AST-986](https://linear.app/astralcareermatch/issue/AST-986/session-parse-api-no-persist-no-candidate-bind-save-resume-pdf) / [AST-987](https://linear.app/astralcareermatch/issue/AST-987/admin-session-resume-paste-page-html-new-tab-save-resume-pdf) (session parse API + paste page, Done); [AST-1019](https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies) family (Judith craft-base / render UAT — parallel, session path will stop depending on craft-base).

### Open questions

none.

### Proposed child tickets

**1!: Ruth simple session-resume parse task — Ada.** Add the dedicated Little/Ruth agent task and `TASK_CONFIG` entry for paste→JSON only (mechanical field mapping; no craft/translate). Seed the repo agent_task so Manage Tasks / startup apply pick it up. Same response contract the session paste path already expects. Does **not** wire Admin Session Resume Parse yet — that is #2. Does **not** change Judith `craft_resume_base`.
Citations: `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.agent.do-task-delegation`; `astral.standards.no-hardcoded-sets`.

**2: Wire Session Resume Parse to Ruth task — Ada.** After #1: point Admin session resume parse (core + thin Admin route contract) at the new Ruth task instead of `craft_resume_base`. Preserve no-persist / no-candidate-bind behavior, ledger visibility, and Style D debug on the hop. Leave candidate craft on Judith. Prefer no Paste UI change.
Citations: `pattern.ui.admin-endpoint`; `pattern.layers.import-discipline`; `astral.patterns.require-auth-on-protected-endpoints`; `astral.layers.ui-config-driven-business-logic`; `astral.standards.debug-contract-gated`; `astral.standards.in-scope-only`.

### Original brief

Let's replace the AI call on the Session Resume Parse screen to a similar but MUCH SIMPLER prompt that sends text to Ruth (little brain) to parse the text into JSON, not think through and translate. This screen is a stop-gap measure until we have the full generation pipeline completed. Let's not waste big-brain tokens on rote translation to JSON.

#### Comments

_2 chuckles comments (2026-07-29): agent thread-id housekeeping only — reminting colliding `.cursor/chats` store.db UUIDs for the epic's Ada / Betty / Radia rows. No product content; skipped per archive rules._

### Files changed (plan vs actual)

_No epic-level plan file list. Epic commits are merge-log housekeeping (`5278c3fed`) and the Linear archive (`fb4c2565e`); implementation landed under the sub-issues below._

_Implementation detail may live in git history on `origin/dev`._

## Sub-issues

### AST-1037 — Ruth simple session-resume parse task
_Archived: 2026-08-05 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1037/ruth-simple-session-resume-parse-task-simple-resume-parse-function · Status at archive: Archive · Project: Astral Administrator · Assignee: ada · Priority / estimate: None / — · Parent: AST-1036 · Blocked by / blocks / related: parent AST-1036; blocks AST-1038_

#### What this implements

* Ruth/Little agent task + `TASK_CONFIG` entry for paste→JSON only (mechanical field mapping; no craft/translate)
* Seed repo `agent_task` so Manage Tasks / startup apply pick it up
* Same response contract the session paste path already expects

#### Acceptance criteria

- [X] From Admin Session Resume Paste, Parse can run a Ruth (Little) task — not Judith craft-base — and return structure-keyed JSON the screen already understands *(this child: Ruth task + schema; wiring → AST-1038)*
- [X] Paste-faithful mechanics on a known fixture: `__` / `~~` survive into content; competencies not pipe-joined; specialty/keyword text in tagline (not mashed into title); `<no bullet>` leads remain lead markers
- [X] Candidate-bound `craft_resume_base` / Judith craft behavior unchanged outside this Admin session path

#### Boundaries

- [X] Does not wire Admin Session Resume Parse / `run_session_resume_parse` → AST-1038
- [X] Does not change Judith `craft_resume_base` persona or candidate craft path
- [X] Does not change Open HTML builder or paste-page chrome

#### Notes for planning

In scope citations: `pattern.config.config-block`; `astral.config.config-source-of-truth`; `astral.agent.do-task-delegation`; `astral.standards.no-hardcoded-sets`; `astral.docs.features-single-file-per-ticket`; `astral.git.engineer-test-tree-ban`.

Ada self-assessment (plan `4f35545b` → revised `fd31b3b4`): Scope Single-Component — utils shared schema + normalize-key frozenset + `TASK_CONFIG` entry, repo `agent_task` seed/fixture, and `agent.py` membership gate against that frozenset; no Admin route or Judith craft path edits. Conf high — reuses the existing craft-base response contract, Ruth agent row, AST-786 fixture-sync pattern, and the established normalize hook; AST-1038 owns the parse wire. Risk low — new catalog key is unused until AST-1038; shared schema reference cannot silently diverge; Judith `craft_resume_base` prompts and meta stay put.

#### Stage 1: Shared schema + `TASK_CONFIG["simple_resume_parse"]`

**Done when:** `TASK_CONFIG` exposes `simple_resume_parse` with the same response field set as `craft_resume_base`, keyed from one shared schema constant; `craft_resume_base` behavior/meta unchanged except the schema dict is referenced via that constant.

1. In `src/utils/config.py`, immediately above the `TASK_CONFIG = {` assignment (after `_RESUME_ARTIFACT_HOP_TASK_KEYS`), introduce a module-level constant `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` whose value is **exactly** the current `craft_resume_base["response_schema"]` dict body (same keys, types, required flags, and `experience: _EXPERIENCE_JOB_ARRAY_FIELD`).
2. Immediately after it, add:

```python
_CRAFT_RESUME_NORMALIZE_TASK_KEYS = frozenset({
    "craft_resume_base",
    "simple_resume_parse",
})
```

3. Change `TASK_CONFIG["craft_resume_base"]["response_schema"]` to reference `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` (no field edits; no meta edits — keep `response_format`, `context_format`, `entity_type`, `requires_candidate_key`, `trigger_state` as today).
4. Insert a new `TASK_CONFIG` entry **immediately after** `"craft_resume_base"`:

```python
"simple_resume_parse": {
    "response_schema": _CRAFT_RESUME_BASE_RESPONSE_SCHEMA,
    "response_format": "json",
    "context_format": "simple_resume_parse_{index}",
    "entity_type": None,
    "requires_candidate_key": False,
    "trigger_state": None,
},
```

⚠️ **Decision:** Allowed normalize-gate membership lives in `config.py` (§1.4 / `astral.standards.no-hardcoded-sets`). Growing the set later is a config-only change — not another `agent.py` edit.
⚠️ **Decision:** `task_key` is **`simple_resume_parse`** (matches the epic name). Sibling AST-1038 calls this key from `run_session_resume_parse`.
⚠️ **Decision:** `requires_candidate_key: False` — Admin session sentinel path (no candidate bind). Callers may still pass synthetic `ctx.candidate_data` for token resolution but are not required to supply `astral_candidate_key`. Judith `craft_resume_base` stays `requires_candidate_key: True`.
⚠️ **Decision:** Share one schema object between `craft_resume_base` and `simple_resume_parse` so the session paste / Open HTML contract cannot drift between the two catalog keys.

#### Stage 2: Repo `agent_task` seed + AST-756 fixture sync

**Done when:** `data/admin/agent_task.json` contains a current `simple_resume_parse` row for Ruth; `docs/uat-fixtures/AST-756/expected-agent_task.json` is byte-identical to the repo file; Judith `craft_resume_base` row unchanged.

1. In `data/admin/agent_task.json`, append one new object (existing rows untouched):

| Field | Value |
|-------|--------|
| `task_key_uuid` | `046ffb1c-9708-49af-9380-56d85136066b` |
| `task_key` | `simple_resume_parse` |
| `current` | `1` |
| `agent_id` | `college_intern_ruth` |
| `run_next` | `""` |
| `system_prompt` / `cache_prompt_b` / `c` / `d` | `""` |
| `task_group_order` | `"2000"` |
| `task_group_name` | `Candidate Artifacts` |
| `task_seq` | `6` |
| `task_name` | `Simple Resume Parse` |
| `updated_at` | ISO UTC timestamp at edit time |

2. `user_prompt` (short, Ruth-addressed): map the pasted resume text into the JSON schema only; no rewrite, enrichment, LinkedIn synthesis, or "improve the resume"; respond with valid JSON only (no markdown fences / preamble).
3. `cache_prompt` — the mechanical instruction block. It **must** include all of the following paste-faithful rules (lift wording from the current `craft_resume_base` `cache_prompt` — do not invent new markers):
   - Preserve typography digraphs `__` and `~~` literally in every section string (including nested experience fields); do not expand/replace them (HTML builder expands later).
   - `core_competencies` (and `prior_experience` when present): single string; separators are `•` / paste forms such as `__•__` — **never** `|` pipes.
   - Specialty / keyword / focus lines → `candidate_tagline`, **not** folded into `candidate_title`.
   - When the paste has a `<no bullet>…` role lead, copy that line into `accomplishments` **including** the literal `<no bullet>` prefix; do not invent the prefix when absent.
   - Field inventory matches the shared schema: `resume_structure`, `candidate_name`, `candidate_title`, `candidate_contact_detail`, optional `candidate_tagline`, `professional_summary`, `core_competencies`, `experience` (job array), optional `prior_experience`, optional `education_certifications`, optional `technical_skills`.
   - For `resume_structure`: if the paste does not imply a custom catalog, return the default structure shape the session path already uses — do not invent unrelated section ids.
   - Explicitly **forbid** Judith craft-base synthesis: do not blend LinkedIn/bio/backstory; do not invent competencies, roles, or taglines; empty string / omit optional fields when the paste has no material.
4. `nocache_prompt`:

```text
RESUME PASTE TEXT:
{$STARTING_RESUME_TEXT}
```

5. Sync the UAT fixture byte-for-byte: `cp data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json` then `cmp -s` the two.

⚠️ **Decision:** Group under **Candidate Artifacts** / order `2000` / seq `6` (next to `craft_resume_base` seq `5`) so Manage Tasks shows the pair together without inventing a new task group.

#### Stage 3: `do_task` normalize hook via config membership set

**Done when:** both `agent.py` sites that special-case `task_key == "craft_resume_base"` before schema validation instead run `normalize_craft_resume_base_agent_payload` when `task_key in _CRAFT_RESUME_NORMALIZE_TASK_KEYS` (imported from config alongside `TASK_CONFIG`).

1. In `src/core/agent.py`, extend the existing `from src.utils.config import …` that already pulls `TASK_CONFIG` so it also imports `_CRAFT_RESUME_NORMALIZE_TASK_KEYS`.
2. Find every occurrence (two today — sync + async validation paths) of:

```python
if task_key == "craft_resume_base":
    from src.core.candidate import normalize_craft_resume_base_agent_payload
    normalize_craft_resume_base_agent_payload(parsed)
```

3. Change each condition to `if task_key in _CRAFT_RESUME_NORMALIZE_TASK_KEYS:`. Keep the same lazy import and call. Do **not** rename `normalize_craft_resume_base_agent_payload`; do **not** inline `("craft_resume_base", "simple_resume_parse")` in `agent.py`.

⚠️ **Decision:** This is catalog usability for the shared JSON shape, **not** Admin Session Resume Parse wiring — `run_session_resume_parse` still calls `craft_resume_base` until AST-1038.

#### Stage 4: Compile check (plan-owned files only)

`python3 -m compileall -q src/utils/config.py src/core/agent.py`; then assert `simple_resume_parse` is in `TASK_CONFIG` and shares the exact `response_schema` object with `craft_resume_base`. No edits under `tests/`.

#### Revisions

Revision 1 — 2026-07-29. Driven by Joan `[plan-discuss] round=1 concern`: Stage 3 originally used an inline `task_key in ("craft_resume_base", "simple_resume_parse")` membership set in `agent.py`, which violates `astral.standards.no-hardcoded-sets` / §1.4 (allowed-value sets must live in `config.py`; growing the set later would re-touch `agent.py`). Fix: Stage 1 adds `_CRAFT_RESUME_NORMALIZE_TASK_KEYS` in `config.py`; Stage 3 gates the normalize call via that constant; Files Changed + Code Rules check updated to match. Joan re-review: **APPROVED** (tip `fd31b3b4`).

#### Comments

_Plan-rubric (Joan, ×2) and code-rubric (Radia) full statute sweeps (~90 rows each, near-entirely "conforms / Untouched") collapsed. Substance below._

**Joan — 2026-07-29T15:18:21.824Z — plan-rubric.v1 revision 1 — REVISE.** One `fix-now`: the Stage 3 inline membership set (see Revisions above). `acceptable`: wire portion deferred to AST-1038 with clear Boundaries; shared schema object identity prevents contract drift; `requires_candidate_key: False` correct vs Judith `True`; AST-756 fixture byte-sync required; Self-assessment Single-Component / high / low honest.

**Joan — 2026-07-29T15:21:52.983Z — plan-rubric.v1 revision 1 — APPROVED.** Plan Discuss round 1 complete; prior fix-now addressed (`_CRAFT_RESUME_NORMALIZE_TASK_KEYS` now in `config.py`). No `fix-now`, no `discuss`. Stage→definition traceability recorded for all 6 parent ACs (ACs 2, 3, 6 = N/A this child, owned by AST-1038).

**Betty — 2026-07-29T15:52:09.747Z — test manifest.** `origin/sub/AST-1036/AST-1037-ruth-simple-session-resume-parse-task` @ `46e493a9` (`merge-tests(AST-1037): origin/tests 545225d4`):
1. `tests/component/utils/test_config.py::TestAst1037SimpleResumeParseConfig` — shared schema object identity, `requires_candidate_key` False, craft-base meta unchanged, `_CRAFT_RESUME_NORMALIZE_TASK_KEYS`
2. `tests/component/core/test_repo_admin_json.py::TestAst786AgentTaskRepoJsonSeed` — revised frozenset includes `simple_resume_parse`; fixture byte-identical; startup apply 39
3. `tests/component/core/test_repo_admin_json.py::TestAst1037SimpleResumeParseCatalogRow` — Ruth seed + paste-faithful prompt rules; Judith `craft_resume_base` unchanged
4. `tests/component/core/test_agent.py::TestAst1037NormalizeGateMembership` — `do_task` gate uses config frozenset (not inline craft-only)

Bible shasums on publish tip: `docs/test-bible/core/agent.md` `22eb8effe9ce52bc033a6f3dd5024c40a5384117`; `docs/test-bible/core/repo_admin_json.md` `7ae32692f9d0f80fd06c9d6e80cb1dc6beb76886`; `docs/test-bible/utils/config.md` `1deede1ce9de9dbfc56f5b4a5a7b2c9516fb3c5d`; `docs/test-bible/data/database/agent_tasks.md` `bc9982144153ff1aaf89de064e37be04d95a5b1b`.

**Radia — 2026-07-29T15:56:42.378Z — code-rubric.v1 revision 1 — DISCUSS.** Publish ref `151cd9a8` on `origin/sub/AST-1036/AST-1037-ruth-simple-session-resume-parse-task`. No `fix-now`. Three `discuss` items, all "C4 straggler": Joan had Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` at plan time on a paths-miss basis; the code-rubric sweep on the three-dot tip brings them in-scope (feature doc now under `docs/features/**`; Betty `tests/` + bible in tip) — substance still **conforms** in every case, no product fix. Advisory: leading-underscore `_CRAFT_RESUME_NORMALIZE_TASK_KEYS` imported across modules matches the existing `_CRAFT_*` schema-constant convention. What's solid: shared schema identity, config-owned normalize membership, paste-faithful Ruth prompt, Judith row untouched, no Admin wire smuggle.

#### Resolution

**2026-07-29 — Ada (`resolve-child`).** fix-now: none. discuss (C4 stragglers): acknowledged — substance conforms (plan doc is not a spike; single feature file; engineer `code()` SHA `80ea40e7` clean of the test tree; Betty authored the test/bible SHAs). advisory: cross-module import of `_CRAFT_RESUME_NORMALIZE_TASK_KEYS` left as planned. Product tip unchanged from review tip `151cd9a8`; the resolve commit is appendix only.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/utils/config.py` | Extract shared `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA`; add `_CRAFT_RESUME_NORMALIZE_TASK_KEYS`; add `TASK_CONFIG["simple_resume_parse"]` | `80ea40e78` |
| ✓ | `data/admin/agent_task.json` | Add `simple_resume_parse` row (`college_intern_ruth`, mechanical prompt, paste-faithful rules) | `80ea40e78` |
| ✓ | `docs/uat-fixtures/AST-756/expected-agent_task.json` | Byte-identical copy after the new row (AST-786 seed gate) | `80ea40e78` |
| ✓ | `src/core/agent.py` | Gate `normalize_craft_resume_base_agent_payload` via `_CRAFT_RESUME_NORMALIZE_TASK_KEYS` | `80ea40e78` |
| | _tests_ | — | `545225d45` — 3 test file(s) + 4 test-bible file(s) |

### AST-1038 — Wire Session Resume Parse to Ruth task
_Archived: 2026-08-05 · Linear URL: https://linear.app/astralcareermatch/issue/AST-1038/wire-session-resume-parse-to-ruth-task-simple-resume-parse-function · Status at archive: Archive · Project: Astral Administrator · Assignee: ada · Priority / estimate: None / — · Parent: AST-1036 · Blocked by / blocks / related: parent AST-1036_

#### What this implements

After the Ruth simple session-resume parse task lands: point Admin session resume parse (core + thin Admin route contract) at the new Ruth task instead of `craft_resume_base`. Preserve no-persist / no-candidate-bind behavior, ledger visibility, and Style D debug on the hop. Leave candidate craft on Judith. Prefer no Paste UI change.

Citations: `pattern.ui.admin-endpoint`; `pattern.layers.import-discipline`; `astral.patterns.require-auth-on-protected-endpoints`; `astral.layers.ui-config-driven-business-logic`; `astral.standards.debug-contract-gated`; `astral.standards.in-scope-only`.

#### Acceptance criteria

1. From Admin **Session Resume Paste**, Parse runs a Ruth (Little) task — not Judith craft-base — and still returns structure-keyed JSON the screen already understands.
2. A successful Parse → Open HTML path still works without binding to the selected candidate and without writing candidate/job artifacts for the paste.
3. Dispatch/cost ledger for the Admin session-parse hop still records the run against the session sentinel path (same operational visibility Susan has today).
4. Candidate-bound `craft_resume_base` / Judith craft behavior is unchanged when exercised outside this Admin session path.
5. With debug on, the session-parse hop emits Style D index + detail (found|recorded), not summary-only noise; with debug off, no new debug-contract lines.

#### Boundaries

* Does **not** author the Ruth agent_task / TASK_CONFIG entry — sibling owns that.
* Does **not** change Judith `craft_resume_base` for candidate craft.
* Does **not** change Open HTML builder; prefer zero Paste UI change.

#### Notes for planning

After AST-1037. Wire `run_session_resume_parse` (+ Admin route) to the new task key.

**Prerequisite:** this sub must already include AST-1037 product tip via `origin/ftr/ast-1036-simple-resume-parse-function` (merge-on-checkout) — `TASK_CONFIG["simple_resume_parse"]`, the Ruth `agent_task` seed, and `_CRAFT_RESUME_NORMALIZE_TASK_KEYS` must exist before Stage 1.

Ada self-assessment (plan `a81c4939`): Scope Single-Component — one core call-site swap (+ docstring/error string) and a thin Admin docstring; no catalog/seed/UI work. Conf high — AST-1037 already delivered the Ruth task, shared schema, and normalize membership; AST-986 established the session sentinel / response contract this ticket only re-keys. Risk low — candidate Judith craft paths stay on `craft_resume_base`; session response shape unchanged; a wrong key would fail `do_task` / schema immediately rather than silently corrupt candidates.

#### Stage 1: Core wire — `run_session_resume_parse` → Ruth

**Done when:** `run_session_resume_parse` calls `do_task` with `simple_resume_parse`; success/error JSON shapes and ledger sentinel behavior unchanged; `parse_candidate_resume` / `run_candidate_artifact_generation` still use `craft_resume_base`.

1. In `src/core/candidate.py`, locate `run_session_resume_parse` (AST-986 session paste path). Keep validation, `default_resume_structure()`, synthetic `ctx` (no `astral_candidate_id`), ledger (`ledger_task_key = "user-session-parse-resume"`, `candidate_id="session"`), `log_batch_id`, `asyncio.run(do_task(...))`, `split_craft_resume_base_payload`, Style D `debug_index` / `debug_detail` / `_debug_experience_jobs`, and `finally` flush — **do not** redesign those.
2. Change the `do_task` call from `task_key="craft_resume_base",` to `task_key="simple_resume_parse",`. Keep `live_content=paste`, `index=batch_id`, `ctx=ctx`, `debug=debug` unchanged.
3. Update the function docstring to say paste is parsed via `simple_resume_parse` (Ruth / Little), not `craft_resume_base`.
4. Update the non-dict failure string from `"craft_resume_base returned non-dict parsed_response"` to `"simple_resume_parse returned non-dict parsed_response"` (same HTTP 500 shape).
5. **Forbidden in this stage:** editing `parse_candidate_resume`, `run_candidate_artifact_generation`, `_persist_craft_dispatch_success`, `TASK_CONFIG`, `agent_task` seeds, or any React file. Grep after edit must still show `task_key="craft_resume_base"` in those candidate craft paths.

⚠️ **Decision:** Use the literal `TASK_CONFIG` key `"simple_resume_parse"` at this single call site (same pattern as the prior `"craft_resume_base"` literal). Do **not** add a config block for one caller; do **not** invent a second session-parse entrypoint.
⚠️ **Decision:** Keep reusing `split_craft_resume_base_payload` / `normalize_craft_resume_base_agent_payload` (via the do_task normalize frozenset). Shared schema identity means the session response contract (`resume_structure` / `base_resume` / `parsed_response`) does not change for the Paste UI or Open HTML.

#### Stage 2: Admin route docstring (thin contract unchanged)

**Done when:** `POST /api/admin/session_resume/parse` still validates body, calls `run_session_resume_parse`, returns `(body, status)` unchanged; docstring no longer claims craft-base. Update only the `session_resume_parse` docstring in `src/ui/api/api_admin.py` from "paste → craft_resume_base …" to "paste → simple_resume_parse (Ruth) …". No route path, `@require_admin`, request-field, or response-handling change.

⚠️ **Decision:** Prefer zero Paste UI change — React already posts `resume_text` and consumes `success` / `resume_structure` / `base_resume` / `parsed_response`; the wire is core-only.

#### Stage 3: Compile check (plan-owned files only)

`python3 -m compileall -q src/core/candidate.py src/ui/api/api_admin.py`; optional venv sanity that `simple_resume_parse` is in `TASK_CONFIG`. No edits under `tests/`.

#### Comments

_Plan-rubric (Joan) and code-rubric (Radia) full statute sweeps collapsed; substance below._

**Joan — 2026-07-29T16:05:28.333Z — plan-rubric.v1 revision 1 — APPROVED.** First Plan Ready pass, tip `a81c4939`; blocked-by AST-1037 Plan Approved, merge-on-checkout precondition stated. No `fix-now`, no `discuss`. `acceptable`: single `task_key="simple_resume_parse"` literal at the existing call site (catalog key authored in AST-1037, not a growing membership set); reuse of `split_craft_resume_base_payload` / normalize frozenset keeps the Paste / Open HTML contract; docstring-only Admin change = zero Paste UI; Self-assessment honest. Stage→definition traceability recorded for all 5 child ACs.

**Betty — 2026-07-29T16:09:47.290Z — test manifest.** `origin/sub/AST-1036/AST-1038-wire-session-resume-parse-to-ruth-task` @ `772afdc4` (`merge-tests(AST-1038): origin/tests b088c35d`):
1. `tests/component/core/test_candidate.py::TestAst1038SessionResumeWire` — `run_session_resume_parse` → `simple_resume_parse`; Judith craft paths still `craft_resume_base`
2. `tests/component/core/test_candidate.py::TestAst986SessionResumeParse` — revised `task_key` + non-dict error string; session sentinel / no-persist / Style D unchanged
3. `tests/component/ui/api/test_api_admin.py::TestAst986SessionResumeParseApi` — thin Admin route contract unchanged (docstring-only product)

Bible shasum on publish tip: `docs/test-bible/core/candidate.md` `bc5bf0948d71c3f1a733a448a912fa2e327978d9`.

**Radia — 2026-07-29T16:12:34.376Z — code-rubric.v1 revision 1 — DISCUSS.** Publish ref `1c62a5ea`. No `fix-now`. Four `discuss` items, all "C4 straggler": Joan Excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, and `astral.standards.utils-data-late-import-only` at plan time on paths-miss; the three-dot tip (rolled AST-1037 `src/utils/config.py` + feature docs + Betty tests/bible) brings them in-scope — substance **conforms** in every case. What's solid: thin Ruth wire; auth + Style D + sentinel ledger preserved; Judith craft untouched in this child's `code()` SHA.

#### Resolution

**2026-07-29 — Ada (`resolve-child`).** fix-now: none. discuss (C4 stragglers): acknowledged — code-rubric correctly brought the four Excluded statutes in-scope once feature docs / Betty tests / the rolled AST-1037 `config.py` landed on the three-dot tip; substance conforms; no product or test-tree edits. Product tip unchanged from review tip `1c62a5ea`; the resolve commit is appendix only.

#### Files changed (plan vs actual)

| | file | planned | actual |
|---|---|---|---|
| ✓ | `src/core/candidate.py` | `run_session_resume_parse`: `do_task` `task_key` → `simple_resume_parse`; docstring + non-dict error string; leave ledger / synthetic ctx / Style D / split helpers | `2cf538f4a` |
| ✓ | `src/ui/api/api_admin.py` | Docstring on `session_resume_parse` only — still thin `@require_admin` → `run_session_resume_parse` | `2cf538f4a` |
| | _tests_ | — | `b088c35de` — 1 test file + 1 test-bible file |
