# AST-921 — Harvest astral law docs into the statute corpus

- **Linear:** [AST-921](https://linear.app/astralcareermatch/issue/AST-921/harvest-astral-law-docs-into-the-statute-corpus-systemic-statutes-law)
- **Parent:** [AST-912](https://linear.app/astralcareermatch/issue/AST-912/systemic-statutes-law-docs-graduate-to-a-statute-harness)
- **Publish ref:** `origin/sub/AST-912/AST-921-harvest-astral-law-docs`
- **Summary:** Decompose `docs/ASTRAL_CODE_RULES.md`, `docs/ASTRAL_GIT_WORKFLOW.md`, and `docs/ASTRAL_TEAM_WORKFLOW.md` into one-file-per-statute entries under the AST-920 layout (`docs/statutes/orchestration|astral/<domain>/`), classify leftovers as narrative in `docs/statutes/HARVEST.md`, set `checkable` for hook/ci candidates, and update the three law docs to cite statute ids. Does **not** redefine schema/AUTHORING (AST-920), wire Joan/validate-plan/Radia consumers (AST-910 / AST-916), or implement hooks/CI.

## Prerequisite (binding)

AST-920 must have landed its Stage 1–2 deliverables on the tree this sub builds from (normally via `git merge origin/ftr/AST-912-systemic-statutes` after Chuckles `merge-child(AST-920)`). Before Stage 1 of **this** ticket:

1. Confirm these paths exist and match AST-920 plan frontmatter contract: `docs/statutes/SCHEMA.md`, `docs/statutes/AUTHORING.md`, `docs/statutes/README.md`, and the five exemplar statute files listed in AST-920.
2. If any are missing: **stop**. Comment on parent AST-912 with the Stage blocked template — do not invent schema, exemplars, or alternate layout.

⚠️ **Decision:** Plan this ticket now (Todo → Plan Ready) while AST-920 is still mid-pipeline; **build-child** is gated on the prerequisite above. Do not redefine or “improve” SCHEMA fields during harvest.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `docs/statutes/HARVEST.md` | New — crosswalk of every harvested rule + narrative leftovers register | docs / statutes |
| `docs/statutes/README.md` | Extend corpus index: full statute table + link to HARVEST.md (keep SCHEMA/AUTHORING links; preserve exemplar section, add `## Harvested corpus`) | docs / statutes |
| `docs/statutes/orchestration/**/*.md` | New orch.* statutes per **Statute inventory** (skip ids already created by AST-920) | docs / statutes |
| `docs/statutes/astral/**/*.md` | New astral.* statutes per **Statute inventory** (skip AST-920 exemplars) | docs / statutes |
| `docs/ASTRAL_CODE_RULES.md` | Cite statute ids at each harvested rule; mark narrative sections per HARVEST.md | docs |
| `docs/ASTRAL_GIT_WORKFLOW.md` | Same citation / narrative treatment | docs |
| `docs/ASTRAL_TEAM_WORKFLOW.md` | Same citation / narrative treatment | docs |
| `docs/features/team-chuckles/ast-921-harvest-astral-law-docs.md` | This plan | docs / features |

**Out of scope (do not touch):**

- `docs/statutes/SCHEMA.md` field definitions / enums (read-only; AST-920).
- `docs/statutes/AUTHORING.md` lifecycle rules (read-only except a one-line pointer at the top that harvest completeness lives in `HARVEST.md` — only if AUTHORING currently lacks any harvest pointer; if it already points at AST-921, leave body unchanged).
- The five AST-920 exemplar files (do not rewrite; crosswalk only).
- Any `src/**`, `tests/**`, hooks, CI, skills under `~/.cursor/skills/`, or consumer wiring (AST-910 / AST-916 / AST-928).
- Pattern catalog (AST-913).

⚠️ **Decision:** Extend AST-920’s reserved top-level set under `docs/statutes/` by **exactly one** new file: `HARVEST.md`. No other new top-level names.

---

## Mechanical rules (binding — implement exactly)

### Schema / format

Every new statute file MUST obey `docs/statutes/SCHEMA.md` and AST-920 file format:

1. YAML frontmatter with **all** required keys (`id`, `title`, `tier`, `checkable`, `status`, `applies_when` + nested keys, `source_docs`, `supersedes`, `superseded_by`, `approved_by`, `approved_at`).
2. Body in order: `# Statement`, `## Rationale`, `## Examples` (`### Conforming`, `### Violating`), optional `## Notes`.
3. Filename = `{id}.md` under the matching namespace/domain folder.
4. `status: active`, `approved_by: Archie`, `approved_at: "<UTC date of that stage’s commit YYYY-MM-DD>"`, `supersedes: null`, `superseded_by: null` unless the inventory row says otherwise.
5. `source_docs` lists the law doc path(s) the rule came from (always include the primary doc for that inventory row).

### Already landed (AST-920) — do not recreate

| id | path |
|----|------|
| `orch.pipeline.plan-is-bible` | `orchestration/pipeline/` |
| `orch.roles.archie-approves-statutes` | `orchestration/roles/` |
| `astral.layers.import-direction` | `astral/layers/` |
| `astral.git.engineer-test-tree-ban` | `astral/git/` |
| `astral.batch.batch-id-first` | `astral/batch/` |

Record these five in `HARVEST.md` as `status: already-landed (AST-920)` with source sections; do not modify their files.

### Domains (folders to create as needed)

Under `orchestration/`: `pipeline`, `roles`, `git`, `linear`  
Under `astral/`: `standards`, `config`, `agent`, `batch`, `layers`, `state`, `patterns`, `ui`, `debug`, `docs`, `git`

Do not invent additional domain folder names in this ticket.

### Citation format in law docs

When updating a law doc section that maps to a statute, add a single bold citation line immediately under the section heading (or under the bullet that is the rule), using:

```markdown
**Statute:** `astral.example.id`
```

Multiple statutes under one heading: one citation line per statute, adjacent to the corresponding bullet/paragraph. Do **not** bulk-delete law doc prose. Narrative-only sections get:

```markdown
**Narrative (not a statute):** see `docs/statutes/HARVEST.md` § Narrative leftovers — <row key>
```

### `checkable` assignment rules (no hook/CI implementation)

| `checkable` | Use when |
|-------------|----------|
| `hook` | Path/role bans or structural git/layout rules already (or clearly) enforceable at pre-commit |
| `ci` | Signature/lint/static patterns enforceable in CI later (batch APIs, import direction class, naming) |
| `judgment` | Everything else (design patterns, process gates, soft architecture rules) |

Inventory rows below already pick `checkable` — do not reclassify during build.

---

## Statute inventory (complete set for this ticket)

Create **exactly** the statutes in the tables below that are marked `create`. Skip `already-landed`. Do not add statutes not listed here.

### A. `docs/ASTRAL_CODE_RULES.md` → `astral/*`

| Action | id | domain | tier | checkable | Source § | Statement gist |
|--------|----|--------|------|-----------|----------|----------------|
| create | `astral.standards.in-scope-only` | standards | scoped | judgment | 1.1 | Touch only what this doc or a module header explicitly scopes; do not expand scope silently |
| create | `astral.standards.database-header-inventory` | standards | scoped | judgment | 1.1 | Data layer may use only tables listed in `database.py` header inventory; add/change requires design + header update |
| create | `astral.standards.no-cross-contamination` | standards | scoped | judgment | 1.1 | Do not import/depend on code or data outside the layered structure |
| create | `astral.standards.dry-and-focused-functions` | standards | scoped | judgment | 1.3 | Honor DRY; keep functions focused; extract helpers for complex logic |
| create | `astral.standards.public-then-helpers` | standards | scoped | judgment | 1.3 | Public functions first, then helpers; group by responsibility with section comments |
| create | `astral.standards.no-hardcoded-sets` | standards | scoped | ci | 1.4 | State lists/enums/allowed sets live in `config.py`; no inline magic sets; magic numbers → named constants |
| create | `astral.standards.logging-via-utils` | standards | scoped | judgment | 1.5 | Backend logging goes through `src/utils/logging.py` |
| create | `astral.standards.data-raises-caller-logs` | standards | scoped | judgment | 1.5 | Data layer raises, does not log; core raises domain exceptions; dispatcher logs batches; UI returns JSON errors |
| create | `astral.standards.utils-data-late-import-only` | standards | scoped | hook | 1.5 | Only approved `utils → data` path is late-import inside logging DB flush; do not copy elsewhere |
| create | `astral.standards.debug-contract-gated` | standards | scoped | judgment | 1.5.1 | Debug-contract lines only when `debug=True`; use `_PrefixedLogger` helpers + truncation rules; no data-layer debug noise |
| create | `astral.config.config-source-of-truth` | config | scoped | judgment | 2.1 | Behavior-driving non-secret values live as literals in `config.py` (organized blocks), not scattered |
| create | `astral.config.secrets-and-env-specific-from-environ` | config | scoped | ci | 2.1 | Secrets and env-specific values via `os.environ["KEY"]` with no `.get()`/fallback; crash if missing |
| create | `astral.config.pass-threshold-vs-score-floor` | config | scoped | judgment | 2.1 | `pass_threshold` grades after run; `score_floor` gates dispatch eligibility — neither replaces the other |
| create | `astral.agent.do-task-delegation` | agent | scoped | judgment | 2.2 | Core calls `do_task` for AI work; does not assemble Anthropic call params or perform I/O itself |
| create | `astral.agent.grade-vector-validation` | agent | scoped | judgment | 2.3.1 | After schema pass, graded tasks validate expected vectors and grades in `{A,B,C,D,F,X}` |
| create | `astral.agent.confidence-bounds` | agent | scoped | judgment | 2.3.2 | Graded rows carry integer confidence per CODE_RULES bounds; scoring treats conf `1` as no signal |
| already-landed | `astral.batch.batch-id-first` | batch | — | — | 2.4 | (AST-920) |
| create | `astral.batch.claim-process-release` | batch | scoped | judgment | 2.4 | Entity batches use claim → process → release with `batch_id`; never select-by-state without batch lock |
| create | `astral.batch.batch-id-format` | batch | scoped | judgment | 2.4 | `batch_id` format `f"{task_key}-{uuid}"` (or function context prefix for non-dispatch) |
| create | `astral.batch.entity-agent-responses-latest-only` | batch | scoped | judgment | 2.4.1 | After successful `do_task`, upsert latest-only `agent_responses` ref by `task_key`; history stays in `agent_data` |
| create | `astral.layers.core-vs-external-bright-line` | layers | scoped | judgment | 2.5 | External owns I/O; core owns orchestration/business logic |
| already-landed | `astral.layers.import-direction` | layers | — | — | 3.3 | (AST-920) |
| create | `astral.layers.ui-config-driven-business-logic` | layers | scoped | judgment | 3.2 | UI conditional behavior is config-declared and resolved in API layer; React must not duplicate business rules |
| create | `astral.layers.scripts-exempt-from-layer-rules` | layers | scoped | judgment | 3.3 | `scripts/` may import any layer; not a runtime concern |
| create | `astral.state.no-daisy-chain-in-run` | state | scoped | judgment | 2.6 | No automatic multi-state daisy-chain across a single dispatch run (except documented `run_next` carve-out in 2.6.0) |
| create | `astral.state.core-decides-transitions` | state | scoped | judgment | 2.6 | Core decides next state; data/tracker accept target state as parameter only |
| create | `astral.state.job-prior-states-enforced` | state | scoped | judgment | 2.6.2 | Job transitions enforce `JOB_STATES.prior_states` via tracker |
| create | `astral.patterns.render-verdict-orchestrates-consult` | patterns | scoped | judgment | 2.7 | Per-job consult lifecycle goes through `render_verdict`; dispatcher does not call tracker directly |
| create | `astral.patterns.coat-check-never-store-empty` | patterns | scoped | judgment | 2.8 | Coat-check handlers must not store empty/failed values; `None` means retry later |
| create | `astral.patterns.require-auth-on-protected-endpoints` | patterns | scoped | judgment | 2.9 | Protected UI endpoints use `@require_auth`; open endpoints omit it deliberately |
| create | `astral.ui.frontend-file-placement` | ui | scoped | ci | 3.5 | Frontend files live in the prescribed flat dirs (`components/`, `pages/`, `lib/`, etc.) — no extra subdir trees |
| create | `astral.ui.naming-conventions` | ui | scoped | ci | 3.5 | PascalCase React components; snake_case routes and API paths |
| create | `astral.ui.single-gunicorn-worker` | ui | scoped | judgment | 3.5 | Production uses single gunicorn worker because scheduler is per-worker |
| create | `astral.debug.spikes-under-debug-dir` | debug | scoped | hook | 3.6 | Spike/R&D output under `debug/spikes/<issue-id>/…` only; never commit `debug/` |
| create | `astral.debug.no-repo-root-artifacts-dir` | debug | scoped | hook | 3.6 | Do not create repo-root `artifacts/`; spike `--out` defaults to `debug/spikes/…` |
| create | `astral.docs.features-single-file-per-ticket` | docs | scoped | judgment | 4.2 | Feature docs live in `docs/features/<project>/<slug>.md` — not `.cursor/plans/` |

**applies_when defaults for astral rows unless noted:**  
`layers`/`paths` chosen to match the rule (e.g. standards/config/agent/batch/state/patterns → `src/**` with relevant layers; ui → `src/ui/**`; debug → `debug/**` + scripts paths as needed; docs → `docs/features/**`). Use `change_types: ["any"]` except debug/hook path bans which use `["add","modify","delete"]`.

### B. `docs/ASTRAL_GIT_WORKFLOW.md` → `orchestration/git` + `astral/git`

| Action | id | domain folder | tier | checkable | Source § | Statement gist |
|--------|----|---------------|------|-----------|----------|----------------|
| create | `orch.git.three-permanent-branches` | orchestration/git | universal | judgment | Permanent branches | Only `main`/`dev`/`tests` are permanent on origin |
| create | `orch.git.flow-direction-inviolable` | orchestration/git | universal | judgment | Permanent branches | Flow is `dev→ftr→sub`, `tests→sub`, `sub→ftr→dev`, `dev→main`; `tests` never merges to `dev`/`main` and `dev` never merges to `tests` |
| create | `orch.git.ftr-sub-topology` | orchestration/git | universal | judgment | Feature branch topology | Parent = `ftr/<id>-<slug>`; child = `sub/<parent>/<child>-<slug>`; Chuckles creates refs at dispatch — agents never create `ftr/`/`sub/` |
| create | `orch.git.one-epic-worktree-per-parent` | orchestration/git | universal | judgment | Worktrees | One `<reponame>-<parent-id>/` epic worktree per parent; subs are branches checked out one at a time |
| create | `orch.git.commit-vocabulary` | orchestration/git | universal | judgment | Complete commit vocabulary | Use only the ten named commit types with listed owners; no new `feat()`/`fix()`/`push-tests()` on new work |
| create | `orch.git.merge-on-checkout` | orchestration/git | universal | judgment | Merge on checkout | On every `sub/*` checkout in epic worktree: fetch, checkout sub, merge `origin/ftr/<parent-segment>` |
| create | `orch.git.betty-merge-tests-one-sha` | orchestration/git | universal | judgment | merge-tests | Betty delivers exactly one `origin/tests` SHA per child via one `merge-tests()` commit on the sub |
| create | `orch.git.no-cherry-pick-rebase-force` | orchestration/git | universal | hook | What never happens | No cherry-pick onto branches; no rebase of origin-pushed branches; no force-push to origin |
| create | `orch.git.no-dev-agent-branches` | orchestration/git | universal | hook | What never happens | No `dev-<agent>` branches local or on origin |
| create | `orch.roles.pre-commit-path-bans` | orchestration/roles | universal | hook | Pre-commit hooks by role | Role hooks block engineer test-tree paths, Betty `src/`+`docs/features/`, Radia `src/`+`tests/` |
| already-landed | `astral.git.engineer-test-tree-ban` | astral/git | — | — | What never happens / TEAM | (AST-920) |
| create | `astral.git.betty-no-src-or-features` | astral/git | scoped | hook | What never happens | Betty must not commit to `src/` or `docs/features/` (except `merge-tests` merge commit on sub) |

### C. `docs/ASTRAL_TEAM_WORKFLOW.md` → `orchestration/*`

| Action | id | domain | tier | checkable | Source § | Statement gist |
|--------|----|--------|------|-----------|----------|----------------|
| already-landed | `orch.pipeline.plan-is-bible` | pipeline | — | — | (skills / plan contract) | (AST-920) |
| create | `orch.pipeline.project-scoped-queues` | pipeline | universal | judgment | Project scope | Engineer plan/build/test/resolve queues filter to session Linear project unless Susan passes an explicit ticket id |
| create | `orch.pipeline.status-gates-skill-entry` | pipeline | universal | judgment | Linear status → skill | Enter each pipeline skill only from its listed Linear status (Todo→plan, Plan Approved→build, …) |
| create | `orch.pipeline.call-susan-for-product-decisions` | pipeline | universal | judgment | CALL SUSAN | Product/priority/cross-feature contracts escalate `@susan` in Linear — do not invent missing decisions |
| create | `orch.roles.betty-owns-test-tree` | roles | universal | judgment | Test ownership | Only Betty commits test-tree paths; engineers `[qa-handoff]` instead of patching tests/bible |
| already-landed | `orch.roles.archie-approves-statutes` | roles | — | — | (AST-920) | (AST-920) |
| create | `orch.roles.chuckles-never-ticket-assignee` | roles | universal | judgment | Roles | Chuckles coordinates but is never the Linear assignee on child implementation tickets |
| create | `orch.roles.engineer-assignee-through-resolve` | roles | universal | judgment | Roles / happy path | Implementing engineer remains assignee through resolve / child User Testing |

**Count check:** `create` rows above = **51** new statute files (34 CODE_RULES + 11 GIT + 6 TEAM). `already-landed` = 5. Total enforceable mappings in HARVEST.md crosswalk = **56** (plus narrative rows).

---

## Narrative leftovers (must appear in `HARVEST.md`)

Classify **all** of the following as narrative (not statutes). Do not invent statutes for them in this ticket.

| Key | Source | Why narrative |
|-----|--------|---------------|
| `code-rules-1.2-imports-pointer` | CODE_RULES §1.2 | Pointer into §3.3; covered by `astral.layers.import-direction` |
| `code-rules-2.1-config-block-catalog` | CODE_RULES §2.1 block bullets | Catalog of current keys — descriptive inventory, not a separate enforceable rule per block |
| `code-rules-2.4-dispatcher-pseudocode` | CODE_RULES §2.4 code sample | Illustrative; claim/process/release + batch-id statutes cover the rule |
| `code-rules-2.6.0-run-next-carveout-detail` | CODE_RULES §2.6.0 | Detailed carve-out prose under `astral.state.no-daisy-chain-in-run` Notes — keep law prose, no extra statute |
| `code-rules-2.6.1-3-entity-examples` | CODE_RULES §2.6.1–2.6.3 | Examples of company/job/candidate flows — illustrative |
| `code-rules-2.7-encoded-consult-detail` | CODE_RULES §2.7 encoded paragraph | Feature-specific detail; pointer to consult feature docs |
| `code-rules-2.8-coat-check-key-table` | CODE_RULES §2.8 table | Current key registry — data, not a rule (rule is never-store-empty) |
| `code-rules-3.1-directory-tree` | CODE_RULES §3.1 | Descriptive tree snapshot |
| `code-rules-3.2-dispatch-pipeline-table` | CODE_RULES §3.2 PW/AI/DB table | Descriptive task matrix |
| `code-rules-3.4-html-cull-config` | CODE_RULES §3.4 | Config location notes; no separate statute beyond config-source-of-truth |
| `code-rules-3.5-dev-workflow-ports` | CODE_RULES §3.5 | Dev port/process how-to |
| `code-rules-3.5-scheduler-endpoint-list` | CODE_RULES §3.5 | Endpoint inventory |
| `code-rules-3.7-boards-sunset` | CODE_RULES §3.7 | Historical sunset archive |
| `code-rules-4.1-stale-branching` | CODE_RULES §4.1 | **Stale** — superseded by `ASTRAL_GIT_WORKFLOW.md`; do not harvest as active statutes |
| `code-rules-4.3-state-name-list` | CODE_RULES §4.3 | Name list duplicated from TEAM happy-path table — keep as narrative index |
| `git-reference-graph` | GIT_WORKFLOW Reference graph | Pointer-only |
| `git-skills-map` | GIT_WORKFLOW Skills map | Index into skills |
| `git-chuckles-hygiene-tmp-branches` | GIT_WORKFLOW Chuckles git hygiene | Operator script detail; covered by no-dev-agent / flow statutes at rule level |
| `git-child-strict-sequential-prose` | GIT_WORKFLOW Child sub-issue sequencing | Keep law prose; orchestration of dispatch timing is Chuckles skill-owned — cite under Notes of `orch.git.ftr-sub-topology` rather than a separate hard statute if it would conflict with parallel datt; **still list as narrative** in HARVEST (do not create `orch.git.children-strictly-sequential`) |
| `team-orientation-pointer` | TEAM Orientation | Points at orientation skill |
| `team-git-and-branches-pointers` | TEAM Git and branches | Points at orientation / CODE_RULES §3.6 — no new rule |
| `team-happy-path-table` | TEAM Linear status → skill | Table is the index behind `orch.pipeline.status-gates-skill-entry` — table itself stays narrative |
| `team-roles-table-detail` | TEAM Roles table | Role roster detail behind role statutes |

⚠️ **Decision:** CODE_RULES §4.1 is explicitly **not** harvested into active statutes. Law-doc Stage marks it narrative/stale and points readers at GIT_WORKFLOW + `orch.git.*` ids.

⚠️ **Decision:** Do **not** create a statute asserting “children are strictly sequential.” Record that GIT_WORKFLOW sentence as narrative leftover so parallel dispatch skills are not forced to violate a harvested universal.

---

## Stage 0: Prerequisite gate (no commit if failing)

**Done when:** AST-920 schema + five exemplars are present on the checked-out sub after `git fetch` + `git merge origin/dev` + `git merge origin/ftr/AST-912-systemic-statutes`, Merge-clean gate `BEHIND=0` vs `origin/dev`, and `origin/dev` is ancestor of `HEAD`.

1. Run the merges and Merge-clean gate per orientation.
2. Verify the prerequisite file list in **Prerequisite (binding)**.
3. If missing → stop and comment on **AST-912** (parent). Do not start Stage 1.

No commit for a pure no-op gate. If merges produce a merge commit, that commit is allowed before Stage 1.

---

## Stage 1: `HARVEST.md` + README index scaffolding

**Done when:** `docs/statutes/HARVEST.md` exists with (a) a full crosswalk table of every inventory row (`create` + `already-landed`) including id, source doc+§, checkable, tier, path, and (b) the **Narrative leftovers** table verbatim from this plan; `docs/statutes/README.md` links to `HARVEST.md` and has an empty or “pending Stage 2–4” `## Harvested corpus` section placeholder.

1. Create `docs/statutes/HARVEST.md` with short purpose blurb, then `## Crosswalk`, then `## Narrative leftovers`.
2. Update `README.md`: add link to `HARVEST.md`; add `## Harvested corpus` placeholder stating stages 2–4 fill the table.
3. Do not create statute files yet.

**Commit message:** `code(AST-921): HARVEST crosswalk + README scaffold`

---

## Stage 2: Harvest CODE_RULES → `astral/*` statutes

**Done when:** Every `create` row in inventory **section A** exists as a valid statute file; none of the AST-920 exemplar files were modified; each new file passes a manual frontmatter key presence check against SCHEMA.

1. Create domain folders under `docs/statutes/astral/` as needed: `standards`, `config`, `agent`, `batch`, `layers`, `state`, `patterns`, `ui`, `debug`, `docs`.
2. For each section A `create` row, write `{id}.md` with Statement/Rationale/Examples faithful to the cited CODE_RULES section (one enforceable rule per file). Set `source_docs: ["docs/ASTRAL_CODE_RULES.md"]`.
3. Do not create statutes for narrative leftover keys.

**Commit message:** `code(AST-921): harvest CODE_RULES into astral statutes`

---

## Stage 3: Harvest GIT_WORKFLOW + TEAM_WORKFLOW → `orchestration/*` + remaining `astral/git`

**Done when:** Every `create` row in inventory **sections B and C** exists; AST-920 exemplars untouched.

1. Create `docs/statutes/orchestration/git/` and `orchestration/linear/` only if a create row needs them (this inventory uses `git`, `roles`, `pipeline` — **do not** create an empty `linear/` folder).
2. Write each section B/C `create` statute. `source_docs` = the matching law doc path (`ASTRAL_GIT_WORKFLOW.md` or `ASTRAL_TEAM_WORKFLOW.md`). For dual-mentioned test-tree ownership, prefer the primary source listed in the inventory row; may list both paths in `source_docs`.
3. Universal-tier rows in B/C must use `tier: universal`.

**Commit message:** `code(AST-921): harvest GIT + TEAM workflow into orch statutes`

---

## Stage 4: Finalize README corpus index + HARVEST paths

**Done when:** `README.md` `## Harvested corpus` lists **every** active statute under `docs/statutes/**` (AST-920 exemplars + all AST-921 creates) with columns `id | tier | checkable | path`; `HARVEST.md` crosswalk `path` column matches reality; count of `create` files on disk = 51.

1. Replace the Stage 1 placeholder with the full table (include exemplars).
2. Fix any HARVEST.md path typos discovered while listing files.
3. No law-doc edits yet.

**Commit message:** `code(AST-921): index harvested statute corpus in README`

---

## Stage 5: Update the three law docs to cite statute ids

**Done when:** Each harvested rule site in the three law docs carries a `**Statute:** \`id\`` citation; each narrative leftover site carries a `**Narrative (not a statute):**` line pointing at the HARVEST.md row key; CODE_RULES §4.1 is marked narrative/stale with pointers to GIT_WORKFLOW + relevant `orch.git.*` ids; law docs are **not** bulk-deleted.

1. Edit `docs/ASTRAL_CODE_RULES.md` per citation format + narrative markers.
2. Edit `docs/ASTRAL_GIT_WORKFLOW.md` likewise.
3. Edit `docs/ASTRAL_TEAM_WORKFLOW.md` likewise.
4. Do not remove substantive rule prose — citations annotate; they replace nothing except clearly stale procedural steps inside §4.1 where a short stale banner is required:

   At the top of CODE_RULES §4.1, insert a banner that §4.1 branching instructions are superseded by `docs/ASTRAL_GIT_WORKFLOW.md` and the `orch.git.*` statutes, and mark the old numbered workflow as historical narrative.

**Commit message:** `code(AST-921): cite statute ids from law docs`

---

## Execution contract

- Execute stages in order on epic worktree `astral-AST-912/` with `sub/AST-912/AST-921-harvest-astral-law-docs` checked out.
- After each stage commit: `git push origin HEAD:sub/AST-912/AST-921-harvest-astral-law-docs`.
- Do not add statutes, domains, namespaces, or top-level files beyond this plan.
- Do not implement hooks/CI; only classify `checkable`.
- Ambiguity, missing AST-920 prerequisite, or inventory/doc conflict → stop; comment on **parent AST-912** with the Stage N blocked template from plan-child.
- No `src/**` or test-tree edits.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — fifty-one new statute files across `docs/statutes/`, a new `HARVEST.md`, README index update, and citation edits to all three astral law docs; schema itself unchanged.

**Conf:** `Medium` — AST-920 schema/exemplars are specified and inventoried here, but AST-920 is not yet merged to ftr at plan time, and harvest grain (one rule per statute) is pinned by this inventory rather than proven against Joan consumers.

**Risk:** `Medium` — incomplete or mis-grained harvest would leave Joan/validate-plan/Radia (AST-910 / AST-916) without citable coverage or with false universals; runtime product code is untouched.

## Self-review vs ASTRAL_CODE_RULES

- §1.3 / §2.1 / §2.4 / §2.6 / §3.3: harvested as statutes, not reimplemented in code; plan does not add runtime duplicates.
- §3.6: corpus stays under `docs/statutes/` (committed); no `debug/spikes` or repo-root `artifacts/`.
- §4.1: explicitly classified narrative/stale — aligns harvest with GIT_WORKFLOW authority.
- §4.2: plan path `docs/features/team-chuckles/ast-921-harvest-astral-law-docs.md` matches Team Chuckles → `team-chuckles`.
- Engineer test-tree ban respected (no `tests/` or bible edits).
- No SCHEMA key invention — conflicts with AST-920 would be `conf-!!-NONE`; none found against the published AST-920 plan.
