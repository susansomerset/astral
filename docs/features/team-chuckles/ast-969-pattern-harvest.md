# AST-969 — Initial astral pattern harvest

- **Linear:** [AST-969](https://linear.app/astralcareermatch/issue/AST-969/initial-astral-pattern-harvest-pattern-libraries-citable-reusable)
- **Parent:** [AST-913](https://linear.app/astralcareermatch/issue/AST-913/pattern-libraries-citable-reusable-logic-catalog)
- **Publish ref:** `origin/sub/AST-913/AST-969-pattern-harvest`
- **Summary:** Decompose the common astral change shapes into approved pattern files under the AST-925 `canon/patterns/` layout; wire `related_statutes` to existing `canon/statutes/` ids; add a harvest crosswalk; exercise one real proposed → approved cycle on a harvest entry. Does **not** redefine pattern schema/AUTHORING field contracts (AST-925), touch product runtime, or wire define-parent / review consumers (AST-914 / rubrics).

## Prerequisite (binding)

AST-925 must have landed its Stage 1–2 deliverables on the tree this sub builds from (normally via `git merge origin/ftr/AST-913-pattern-libraries` after Chuckles `merge-child(AST-925)`). Before Stage 1 of **this** ticket:

1. Confirm these paths exist and match AST-925 SCHEMA frontmatter contract: `canon/patterns/SCHEMA.md`, `canon/patterns/AUTHORING.md`, `canon/patterns/README.md`, and the exemplar `canon/patterns/batch/pattern.batch.entity-claim-process-release.md` (`status: approved`).
2. If any are missing: **stop**. Comment on parent AST-913 with the Stage blocked template — do not invent schema, exemplars, or alternate layout.

⚠️ **Decision:** Plan this ticket now (Todo → Plan Ready) while AST-925 is already User Testing and rolled onto `origin/ftr`; **build-child** still re-checks the prerequisite above. Do not redefine or “improve” SCHEMA fields during harvest.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `canon/patterns/HARVEST.md` | New — AC cite map + crosswalk of every harvested pattern (incl. already-landed AST-925 exemplar) | docs / patterns |
| `canon/patterns/AUTHORING.md` | Amend reserved top-level names to include `HARVEST.md` (one-line extension; no field/lifecycle rewrite) | docs / patterns |
| `canon/patterns/README.md` | Extend corpus index: harvested catalog table + link to `HARVEST.md` (keep SCHEMA/AUTHORING links; preserve Exemplars, add `## Harvested corpus`) | docs / patterns |
| `canon/patterns/state/pattern.state.entity-state-transitions.md` | New — propose then approve (lifecycle exercise) | docs / patterns |
| `canon/patterns/batch/pattern.batch.entity-agent-responses.md` | New — approved harvest entry | docs / patterns |
| `canon/patterns/config/pattern.config.config-block.md` | New — approved harvest entry | docs / patterns |
| `canon/patterns/layers/pattern.layers.import-discipline.md` | New — approved harvest entry | docs / patterns |
| `canon/patterns/ui/pattern.ui.admin-endpoint.md` | New — approved harvest entry | docs / patterns |
| `docs/features/team-chuckles/ast-969-pattern-harvest.md` | This plan | docs / features |

**Out of scope (do not touch):**

- `canon/patterns/SCHEMA.md` field definitions / enums (read-only; AST-925).
- `canon/patterns/AUTHORING.md` lifecycle prose beyond the reserved-name line for `HARVEST.md`.
- The AST-925 exemplar file `canon/patterns/batch/pattern.batch.entity-claim-process-release.md` (do not rewrite; crosswalk only).
- Any `canon/statutes/**` (read-only for `related_statutes` ids).
- Any `src/**`, `tests/**`, hooks, CI, skills under `~/.cursor/skills/`, or consumer wiring (AST-914 / Review Rubrics).
- Extra patterns not listed in **Pattern inventory** (no coat-check, no render-verdict, no dispatch-task mega-pattern beyond the inventory rows).

⚠️ **Decision:** Extend AST-925’s reserved top-level set under `canon/patterns/` by **exactly one** new file: `HARVEST.md`. Mirrors AST-921’s statute harvest register. No other new top-level names.

---

## Mechanical rules (binding — implement exactly)

### Schema / format

Every new pattern file MUST obey `canon/patterns/SCHEMA.md` and AST-925 file format:

1. YAML frontmatter with **all** required keys (`id`, `name`, `status`, `proposed_in`, `approved_by`, `approved_at`, `canonical_refs`, `related_statutes`, `supersedes`, `superseded_by`).
2. Body in order: `# Problem`, `# Solution shape`, `## When not to use` (≥1 bullet), optional `## Notes`.
3. Filename = `{id}.md` under the matching domain folder.
4. Path ↔ id alignment: `canon/patterns/<domain>/<id>.md`.
5. **Do not paste long code** into Solution shape — pointers + short invariants only; use `canonical_refs`.
6. Approved entries must have ≥1 `canonical_refs` and prefer ≥1 `related_statutes` when a matching statute exists.
7. `proposed_in: AST-913` on every new harvest entry (parent that expands the pattern set).
8. `supersedes: null`, `superseded_by: null` unless an inventory row says otherwise.

### Already landed (AST-925) — do not recreate

| id | path |
|----|------|
| `pattern.batch.entity-claim-process-release` | `batch/pattern.batch.entity-claim-process-release.md` |

Record this id in `HARVEST.md` as `status: already-landed (AST-925)` with AC mapping to **new batch task**; do not modify the file.

### Domains (folders to create as needed)

Under `canon/patterns/`: `batch` (exists), `state`, `config`, `layers`, `ui`.

Do not invent additional domain folder names in this ticket.

### AC → pattern cite map (must appear in `HARVEST.md`)

| define-parent change shape | Pattern id(s) to cite |
|----------------------------|------------------------|
| new batch task | `pattern.batch.entity-claim-process-release` |
| new entity state transition | `pattern.state.entity-state-transitions` |
| new admin endpoint | `pattern.ui.admin-endpoint` |
| new config block | `pattern.config.config-block` |

Supporting harvest packages (also citable; not the four AC phrases above):

| Supporting package | Pattern id |
|--------------------|------------|
| entity agent_responses | `pattern.batch.entity-agent-responses` |
| layer / import discipline | `pattern.layers.import-discipline` |

⚠️ **Decision:** Map AC “new batch task” to the existing AST-925 exemplar (`pattern.batch.entity-claim-process-release`) rather than inventing a second batch mega-pattern. Parent harvest list already treats claim/process/release as that package; config-side work for new tasks cites `pattern.config.config-block` when a new `TASK_CONFIG` / config block is part of the ticket.

### Lifecycle exercise (binding)

AUTHORING already documents propose → Archie approve. This ticket must **exercise** it once in git history:

1. Stage 2 lands `pattern.state.entity-state-transitions` with `status: proposed`, `approved_by: null`, `approved_at: null` (canonical_refs may be non-empty while proposed).
2. Stage 3 flips **that same file** to `status: approved`, `approved_by: Archie`, `approved_at: "<UTC date of Stage 3 commit YYYY-MM-DD>"` without changing `id` / path / `proposed_in`.

Other harvest entries in Stage 3 may land directly as `approved` with lineage filled (same posture as the AST-925 exemplar) — only the state pattern must show the two-commit propose→approve cycle.

---

## Pattern inventory (complete set for this ticket)

Create **exactly** the patterns marked `create`. Skip `already-landed`. Do not add patterns not listed here.

| Action | id | domain | Source (CODE_RULES) | related_statutes (exact ids) | canonical_refs (exact path + symbol) | Body gist |
|--------|----|--------|---------------------|------------------------------|--------------------------------------|-----------|
| already-landed | `pattern.batch.entity-claim-process-release` | batch | §2.4 | (on file) | (on file) | (AST-925) |
| create | `pattern.state.entity-state-transitions` | state | §2.6 | `astral.state.no-daisy-chain-in-run`, `astral.state.core-decides-transitions`, `astral.state.job-prior-states-enforced` | `src/core/tracker.py` / `transition_job_state`; `src/core/candidate.py` / `transition_candidate_state`; `src/utils/config.py` / `JOB_STATES`; `docs/ASTRAL_CODE_RULES.md` / `§2.6` | **Problem:** Entities must move between registered states without daisy-chaining a full pipeline in one run, and without data layer choosing next states. **Solution:** Core decides target state from config registries (`JOB_STATES` / company/candidate transition maps); data/tracker accept the target as a parameter; one dispatch cycle = one transition step (except documented `run_next` carve-out). **When not:** Multi-step “finish the whole funnel” in one runner; data-layer hardcoding next state; treating runtime hop labels as registry keys outside the documented carve-out. |
| create | `pattern.batch.entity-agent-responses` | batch | §2.4.1 | `astral.batch.entity-agent-responses-latest-only` | `src/core/agent.py` / `_store_agent_response`; `src/core/roster.py` / `dedupe_agent_responses_latest`; `docs/ASTRAL_CODE_RULES.md` / `§2.4.1` | **Problem:** Callers need a lightweight latest-only pointer from entity rows to `agent_data` without bloating the entity or retaining every historical ref. **Solution:** After successful `do_task`, upsert one `agent_responses` entry per `task_key` (latest wins); keep full blocks in `agent_data`. **When not:** Persisting full prompt/response blobs on the entity row; appending unbounded history on the entity; writing refs on failed `do_task`. |
| create | `pattern.config.config-block` | config | §2.1 | `astral.config.config-source-of-truth`, `astral.standards.no-hardcoded-sets` | `src/utils/config.py` / `TASK_CONFIG`; `docs/ASTRAL_CODE_RULES.md` / `§2.1` | **Problem:** New behavior-driving values and task definitions get scattered as magic sets/literals across layers. **Solution:** Add or extend a named block in `src/utils/config.py` (e.g. `TASK_CONFIG`, state registries); secrets/env-specific stay in `os.environ`; callers read config — do not redefine the set inline. **When not:** Putting secrets in config literals; inventing a second source of truth in UI/React; env `.get()` fallbacks for required secrets. |
| create | `pattern.layers.import-discipline` | layers | §2.5 / §3.3 | `astral.layers.import-direction`, `astral.layers.core-vs-external-bright-line` | `docs/ASTRAL_CODE_RULES.md` / `§3.3`; `docs/ASTRAL_CODE_RULES.md` / `§2.5` | **Problem:** Cross-layer imports and I/O ownership blur, creating cycles and untestable core. **Solution:** Honor the import direction table (ui→core/utils; core→data/external/utils; external/data→utils; utils pure except the logging late-import carve-out); external owns I/O, core owns orchestration. **When not:** ui importing data/external; utils importing core; copying the logging `utils→data` late-import elsewhere. |
| create | `pattern.ui.admin-endpoint` | ui | §2.9 / §3.2 | `astral.patterns.require-auth-on-protected-endpoints`, `astral.layers.ui-config-driven-business-logic` | `src/ui/api/api_admin.py` / `admin_config` (representative protected admin route); `src/ui/auth.py` / `require_auth`; `docs/ASTRAL_CODE_RULES.md` / `§2.9` | **Problem:** New admin HTTP surfaces need a consistent auth + thin-API shape without burying business rules in React. **Solution:** Add routes on the admin blueprint with `@require_auth`; keep business rules config-driven and resolved in the API layer; React renders the resolved response. **When not:** Open admin mutators without auth; putting eligibility/state rules only in the frontend; calling data/external from ui. |

**Count check:** `create` rows = **5** new pattern files. `already-landed` = **1**. Total patterns in HARVEST crosswalk = **6**.

⚠️ **Decision:** Cite the existing private helper `_store_agent_response` in `src/core/agent.py` — that is the upsert entry point used after `do_task`. Do not invent a public wrapper in this ticket (docs-only harvest).

---

## Stage 1: Harvest register + README / AUTHORING pointers

**Done when:** `canon/patterns/HARVEST.md` exists with the AC cite map and a crosswalk table covering all 6 inventory rows (1 already-landed + 5 create, create rows marked pending until Stages 2–3); `AUTHORING.md` reserved top-level list includes `HARVEST.md`; `README.md` links to `HARVEST.md` and has a `## Harvested corpus` section that says create rows land in Stages 2–3 (Exemplar section for the AST-925 entry remains).

1. Write `canon/patterns/HARVEST.md` containing:
   - Purpose one-liner (AST-969 harvest register; schema stays in SCHEMA.md).
   - The **AC → pattern cite map** table from Mechanical rules (exact ids).
   - A **Crosswalk** table with columns: `Status`, `id`, `domain`, `path`, `source` (CODE_RULES §), notes. Include the already-landed row as `already-landed (AST-925)`. List the five create ids as `pending (AST-969)` with intended paths.
   - Short note: propose→approve lifecycle prose lives in AUTHORING; this ticket exercises it on `pattern.state.entity-state-transitions`.
2. In `canon/patterns/AUTHORING.md`, amend the reserved top-level names bullet/list to include `HARVEST.md` alongside `README.md`, `SCHEMA.md`, `AUTHORING.md`. Do not rewrite lifecycle tables or id rules.
3. In `canon/patterns/README.md`:
   - Add a link to `HARVEST.md` near the SCHEMA/AUTHORING links.
   - Add `## Harvested corpus` stating full AC map lives in HARVEST.md; Stage 1 leaves create rows pending; Exemplars table still lists only the AST-925 entry until Stage 3.

**Commit message:** `code(AST-969): pattern HARVEST register + README/AUTHORING pointers`

---

## Stage 2: Propose state-transition pattern (lifecycle exercise)

**Done when:** `canon/patterns/state/pattern.state.entity-state-transitions.md` exists with valid SCHEMA frontmatter, `status: proposed`, `proposed_in: AST-913`, `approved_by: null`, `approved_at: null`, body sections present, `related_statutes` and `canonical_refs` matching the inventory row (canonical_refs non-empty allowed while proposed).

1. Create domain folder `canon/patterns/state/` if needed.
2. Write `canon/patterns/state/pattern.state.entity-state-transitions.md` per inventory row with **`status: proposed`** (not approved yet).
3. Do **not** create the other four harvest files in this stage.
4. Do **not** flip any status to approved in this stage.
5. Optionally update HARVEST.md crosswalk row for this id from `pending` to `proposed (AST-969)` — if you do, keep it in this same commit.

**Commit message:** `code(AST-969): propose pattern.state.entity-state-transitions`

---

## Stage 3: Approve state pattern + land remaining harvest + finalize indexes

**Done when:** All five create patterns exist as `status: approved` with `approved_by: Archie`, `approved_at` = Stage 3 commit UTC date, inventory `related_statutes` / `canonical_refs` / body gists satisfied; HARVEST.md crosswalk shows all six rows landed (no `pending`); README `## Harvested corpus` (and/or Exemplars) lists all six ids with status `approved` and relative paths; AC cite map still correct.

1. Update `canon/patterns/state/pattern.state.entity-state-transitions.md`: set `status: approved`, `approved_by: Archie`, `approved_at: "<UTC date of this commit YYYY-MM-DD>"`. Keep `id`, path, `proposed_in: AST-913`, and body intent.
2. Create the four remaining files with **`status: approved`** from the start (lineage filled — same as AST-925 exemplar posture):
   - `canon/patterns/batch/pattern.batch.entity-agent-responses.md`
   - `canon/patterns/config/pattern.config.config-block.md`
   - `canon/patterns/layers/pattern.layers.import-discipline.md`
   - `canon/patterns/ui/pattern.ui.admin-endpoint.md`
3. Finalize `canon/patterns/HARVEST.md` crosswalk: every create row `create (AST-969)` (or equivalent landed status); no `pending` rows.
4. Update `canon/patterns/README.md` harvested/exemplar tables so all six pattern ids appear with `approved` and paths.
5. Do **not** edit `canon/patterns/SCHEMA.md` or rewrite AUTHORING lifecycle beyond what Stage 1 already did.
6. Do **not** edit `src/**`, statutes corpus, or law docs.

**Commit message:** `code(AST-969): approve state pattern + harvest remaining astral patterns`

---

## Execution contract

- Execute stages in order; one commit per stage on epic worktree; publish each commit to `origin/sub/AST-913/AST-969-pattern-harvest`.
- Do not add files, domains, pattern ids, or SCHEMA keys beyond this plan.
- Ambiguity or drift → stop; comment on **parent** AST-913 with the Stage N blocked template from plan-child.
- No product runtime code. No tests. No hook/CI implementation. No consumer procedure edits.

---

## Self-Assessment

**Scope:** `Single-Component` — confined to `canon/patterns/` harvest files (+ HARVEST/README/AUTHORING pointer amend) and this plan doc; no `src/`, tests, statute corpus edits, or consumer wiring.

**Conf:** `high` — AST-925 schema/layout/lifecycle are on `origin/ftr`; harvest targets and AC cite phrases are explicit; inventory pins ids, statutes, refs, and the one propose→approve exercise so build-child has no layout judgment calls.

**Risk:** `Medium` — wrong cite map or missing AC pattern would block AST-914 define-parent citations and force a follow-up harvest, but nothing in production runtime executes these files yet.

## Self-review vs ASTRAL_CODE_RULES

- §1.3 DRY / §2.1 config / §2.4 batch / §2.6 state / §3.3 imports: N/A to product code — harvest **cites** those sections and related statutes; does not duplicate runtime logic.
- §3.6: patterns live under `canon/patterns/` (committed product docs), not `debug/spikes/` or repo-root `artifacts/`.
- §4.2: plan lives at `docs/features/team-chuckles/ast-969-pattern-harvest.md` (Team Chuckles → `team-chuckles`).
- Engineer test-tree ban respected (no intentional `tests/` or bible edits in plan stages; merge-only test paths from ftr are outside this plan’s Files Changed).
- Boundaries honored: no SCHEMA field redefinition; no statute redefinition; no AST-914 consumer wiring.

## Review

- **Publish ref:** `origin/sub/AST-913/AST-969-pattern-harvest`
- **Build commits:** Stage 1 `code(AST-969): pattern HARVEST register + README/AUTHORING pointers` (`c4cf17f`); Stage 2 `code(AST-969): propose pattern.state.entity-state-transitions` (`e109512`); Stage 3 `code(AST-969): approve state pattern + harvest remaining astral patterns` (`181c192`)
- **Tip at Code Complete:** `a36336e384a7fa79c3a2f4fc8302c7c968fd7ab0` (review stub; Stage 3 harvest at `181c192`)

### Radia — code-rubric.v1 (`[code-rubric] revision=1`)

- **Publish tip reviewed:** (post-docs) see Linear comment SHA
- **Overall:** DISCUSS
- **What’s solid:** HARVEST AC cite map + 6-row crosswalk; AUTHORING reserved-name includes `HARVEST.md` only; five create patterns match inventory (`related_statutes` / `canonical_refs` / body sections); Stage 2→3 propose→approve on `pattern.state.entity-state-transitions`; SCHEMA + AST-925 exemplar untouched by `code(AST-969)`.
- **Issues**
  - **discuss (C4 straggler):** Joan excluded `astral.git.engineer-test-tree-ban`; Betty’s bible README brings it in-scope. Statute verdict **conforms**.
- **Recommended actions:** No product fix; proceed resolve-child / User Testing after acknowledging straggler.
