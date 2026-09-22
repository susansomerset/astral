# AST-1701 — Job source_entity schema + config SSOT + manual backfill SQL

**Linear:** [AST-1701](https://linear.app/astralcareermatch/issue/AST-1701/job-source-entity-schema-config-ssot-manual-backfill-sql)  
**Parent:** [AST-1640](https://linear.app/astralcareermatch/issue/AST-1640/job-source-entity-parent-meteoritecompany-candidate-facing-link) — Job source_entity parent (meteorite|company) + candidate-facing link  
**Publish ref:** `sub/AST-1640/AST-1701-job-source-entity-schema-config-ssot-manual-backfill-sql`

Config + job-table foundation for the locked source-entity parent model: every job has required ingest parent (`company` | `meteorite` + id), optional real employer `company_id`, candidate resolution when the parent is a meteorite row, and a Susan-runnable SQL backfill — with **no** boot/seed auto-UPDATE of job parents. Land/tracker write semantics and UI stay with siblings.

## UAT fitness

- **AC restored:** Parent Functional scope items this child owns — (1) every job has required ingest parent `source_entity_type` ∈ {`company`,`meteorite`} plus non-empty `source_entity_id`; (2) prefer-repurpose / single SoT for parent/track (no parallel `gazed` authority); (3) nullable real employer `company_id` (never a fake `meteorite-*` parent); (7) manual backfill only — ship SQL Susan can run; do not seed automatic migration on boot. Child AC1/AC2 (ticket Description) are the concrete fail tests for those sentences.
- **Correct outcome:** After Susan runs the shipped backfill (and for all new rows written through updated `save_job`), every job row exposes parent type in (`company`,`meteorite`) with non-empty parent id; optional `company_id` is a real employer or NULL; boot/seed alone never rewrites existing job parents.
- **Sibling check:** #2 (tracker/land writes), #3 (breadcrumb authorship calling #1 helpers), #4 (track routing + jobs API/UI) still consume this SSOT — verified by: config helpers are the only closed set; `save_job` / dedupe accept meteorite parent + optional `company_id`; breadcrumb format + timezone clock live only in `config.py`; no land/UI changes in this ticket.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Auto-UPDATE of `job.source` / parents inside `_ensure_job_schema` or `SEED_CONFIG` would “fix” empty parents without Susan’s operator step and violates parent Functional scope item 7 and child AC1 (boot must not rewrite). Leaving `gazed` as a live write authority beside `source_entity_*` fails child AC2.

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/utils/config.py` — source-entity type literals / validators; repurpose or retire `JOB_SOURCES` per Functional scope; breadcrumb format + timezone clock helpers; `METEORITE_CONFIG` keys that still force placeholder company parents
- `src/data/database.py` — job schema for `source_entity_type`/`source_entity_id` (via repurposed `source` or new columns), nullable `company_id` replacing required `company`; candidate_id resolution when parent is meteorite; save/get/list/dedupe helpers + header inventory; **operator SQL backfill script** (docs or `data/` SQL file — not auto-run seed)

Technical (same ticket): config closed set `company` | `meteorite`; migrate `gazed`→`company` when repurposing `job.source`; breadcrumb format string + clock shape; database required parent fields after backfill; nullable `company_id`; `_resolve_job_candidate_id` (or successor) from meteorite when parent is meteorite; writers/dedupe accept meteorite parent + optional `company_id`; backfill artifact via `meteorite.astral_job_id` (and gazed defaults); **not** invoked from `SEED_CONFIG` / boot.

All Files Changed / Stages below stay inside that set. Out of scope (siblings): `tracker.py` / `meteorite.py` land writes, `consult.py` / `gazer.py` track rewires, `api_jobs.py` / `JobsJobDetail.tsx`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Replace `JOB_SOURCES` gazed\|meteorite SSOT with `SOURCE_ENTITY_TYPES` company\|meteorite + validators; thin aliases so pre-#2 imports keep importing; breadcrumb format + timezone clock helpers; retarget `METEORITE_CONFIG` parent-type key off placeholder-as-job-parent | utils |
| `src/data/database.py` | Repurpose `job.source` as parent/track SoT (`company`\|`meteorite`); add `source_entity_id`; rename `company` → nullable `company_id` (table rebuild); resolve `candidate_id` from meteorite when parent is meteorite; update `save_job` / identity / header inventory; **no** content UPDATE on ensure | data |
| `data/sql/ast_1701_job_source_entity_backfill.sql` | Susan-runnable backfill only (not imported by `SEED_CONFIG` / startup) | data/sql |

## Stage 1: Config — source-entity SSOT + breadcrumb helpers

**Done when:** `SOURCE_ENTITY_TYPES` is the closed write set (`company`, `meteorite`); validators and transition helper match company→meteorite (gazed retired as a write value); breadcrumb format + timezone clock helpers exist for #3; `METEORITE_CONFIG` no longer treats a placeholder company short_name as the job parent SoT key. No database changes yet.

1. In `src/utils/config.py` module header inventory, replace the `JOB_SOURCES` one-liner with `SOURCE_ENTITY_TYPES` (parent/track SoT: `company` | `meteorite`; AST-1701) and note breadcrumb helpers.

2. Replace the AST-1469 `JOB_SOURCES` block (currently `gazed` / `meteorite`) with:

```python
# AST-1701: job ingest parent + analysis track SoT (repurposed job.source column).
# company = gazer/employer parent; meteorite = meteorite staging-row parent.
SOURCE_ENTITY_TYPES = ["company", "meteorite"]
SOURCE_ENTITY_TYPE_COMPANY = "company"
SOURCE_ENTITY_TYPE_METEORITE = "meteorite"
SOURCE_ENTITY_TYPE_DEFAULT = SOURCE_ENTITY_TYPE_COMPANY  # insert default when caller omits type

assert SOURCE_ENTITY_TYPE_DEFAULT in SOURCE_ENTITY_TYPES
assert SOURCE_ENTITY_TYPE_METEORITE in SOURCE_ENTITY_TYPES

# Temporary aliases for pre-AST-1702 callers (tracker still imports JOB_SOURCE_* until sibling #2).
# Do not add "gazed" back — writers emit company|meteorite only.
JOB_SOURCES = SOURCE_ENTITY_TYPES
JOB_SOURCE_DEFAULT = SOURCE_ENTITY_TYPE_DEFAULT
JOB_SOURCE_METEORITE = SOURCE_ENTITY_TYPE_METEORITE
```

3. Replace `is_valid_job_source` / `validate_job_source` / `job_source_transition_allowed` bodies to validate against `SOURCE_ENTITY_TYPES`. Transition rules: unset/blank → any allowed type OK; same value OK; `company` → `meteorite` OK; `meteorite` → `company` forbidden. Keep the three function **names** (aliases for #2) so `tracker.py` import sites still resolve until sibling #2 renames call sites. Add parallel names that are the SSOT docs for this epic:

```python
def is_valid_source_entity_type(value: object) -> bool: ...
def validate_source_entity_type(value: object) -> None: ...
def source_entity_type_transition_allowed(from_type: Optional[str], to_type: str) -> bool: ...
```

Implement the `is_valid_job_source` / `validate_job_source` / `job_source_transition_allowed` trio as one-line wrappers calling the new names (no duplicated logic).

4. In `METEORITE_CONFIG`, rename key `"job_source"` → `"source_entity_type"` with value `SOURCE_ENTITY_TYPE_METEORITE`. Update the assert that currently checks `METEORITE_CONFIG["job_source"]`. Keep `short_name_prefix` / `short_name_template` / `stem_short_name_template` (sibling #2 still calls `ensure_meteorite_company` until it stops using them as **job** parents) — add a one-line comment that those templates are **not** job `source_entity_id` / parent after AST-1640; job parent for meteorite track is the meteorite row id.

5. Add breadcrumb SSOT immediately after the source-entity block (or beside `METEORITE_CONFIG` if that keeps meteorite literals together — prefer next to source-entity types):

```python
# AST-1701: email breadcrumb for no-URL meteorite.link outcomes (authored by sibling #3).
# Shape: From:<email> M/D H:MM <timezone> To:<email>
JOB_LINK_BREADCRUMB_FORMAT = "From:{from_email} {clock} To:{to_email}"
# IANA zone → short label for the clock segment (Manage Candidate contact.timezone options).
CONTACT_TIMEZONE_CLOCK_LABELS = {
    "": "UTC",
    "America/New_York": "Eastern",
    "America/Chicago": "Central",
    "America/Denver": "Mountain",
    "America/Los_Angeles": "Pacific",
    "America/Anchorage": "Alaska",
    "Pacific/Honolulu": "Hawaii",
}
```

6. Add two helpers (same module, near the other validators — not in `src/data/`):

- `format_contact_timezone_clock(dt, timezone_key: str) -> str` — interpret `dt` as aware UTC (or naive-as-UTC), convert into the IANA zone from `timezone_key` (empty/`None` → UTC), format `M/D H:MM` with 24-hour hour **without** leading zero on month/day (e.g. `9/17 14:05`), append a space and the label from `CONTACT_TIMEZONE_CLOCK_LABELS` (unknown IANA → use the raw IANA string as the label). Use `zoneinfo.ZoneInfo`.
- `format_job_link_breadcrumb(from_email: str, to_email: str, clock: str) -> str` — return `JOB_LINK_BREADCRUMB_FORMAT.format(from_email=..., clock=..., to_email=...)`.

No `logger.debug` required in these pure formatters (no loops / callee dumps). Do not add `print` or `logger.info("[DEBUG] …")`.

⚠️ **Decision:** Prefer-repurpose of physical column `job.source` (Stage 2) over drop+add `source_entity_type` column — parent Functional scope prefers repurpose; AC2 is satisfied when values are only `company`|`meteorite` and `JOB_SOURCES` is no longer a gazed-authority set. Python SSOT names are `SOURCE_ENTITY_TYPES` / `source_entity_type_*` helpers; the DB column name stays `source` until a later epic renames it.

## Stage 2: Database — schema reshape + writers/dedupe

**Done when:** Job DDL exposes repurposed `source` (`company`|`meteorite`), required-after-backfill `source_entity_id`, and nullable `company_id` (no NOT NULL `company`); `_resolve_job_candidate_id` (or successor) resolves from the meteorite row when parent type is meteorite; `save_job` / identity helpers accept meteorite parent + optional `company_id`; `_ensure_job_schema` performs **DDL only** (no UPDATE of parent fields). Operator SQL file not required yet.

1. In `src/data/database.py` header inventory for `job`, replace the `company` / `source (gazed|meteorite)` wording with: `source_entity` parent via columns `source` (`company`|`meteorite`; AST-1701 repurpose of AST-1469) + `source_entity_id` (company `short_name` or meteorite `id` as text); nullable `company_id` (real employer `short_name`, never placeholder parent); `candidate_id` required.

2. In `_ensure_job_schema`, after existing ALTER-add loops, ensure columns:

| Column | DDL | Notes |
|--------|-----|-------|
| `source` | already present | semantic repurpose only — **no** UPDATE gazed→company here |
| `source_entity_id` | `TEXT` | ADD COLUMN if missing |
| `company_id` | `TEXT` | added via rebuild below |

3. **Rename `company` → `company_id` and drop NOT NULL** using the same table-rebuild pattern as `_apply_board_schema_sunset` / `job_next` (SQLite cannot DROP NOT NULL in place reliably). On ensure, when `PRAGMA table_info(job)` still has a column named `company` and lacks `company_id`:

   - Build `job_next` with column list matching current job columns except `company` → `company_id TEXT` (nullable, no NOT NULL).
   - `INSERT INTO job_next (…) SELECT …` mapping `company` → `company_id`.
   - Drop `job`, rename `job_next` → `job`.
   - Recreate `_JOB_IDENTITY_UNIQUE_INDEX` as  
     `ON job (company_id, job_title, company_job_id)`  
     with the same WHERE guards (`company_job_id` / `job_title` non-null/non-blank).  
   - Update `_is_job_identity_unique_violation` to look for `job.company_id` instead of `job.company`.

   If `company_id` already exists and `company` is gone, skip rebuild.

4. Replace `_resolve_job_candidate_id` with a successor that takes parent context:

```python
def _resolve_job_candidate_id(
    conn,
    *,
    source_entity_type: Optional[str],
    source_entity_id: Optional[str],
    company_id: Optional[str],
    candidate_id: Optional[str],
) -> str:
```

Rules (explicit `candidate_id` always wins when non-blank):

- If `source_entity_type == SOURCE_ENTITY_TYPE_METEORITE`: look up `meteorite.candidate_id` where `CAST(meteorite.id AS TEXT) = source_entity_id` (or integer compare if `source_entity_id` digits-only — prefer text compare on `id`). Raise `ValueError("candidate_id required")` if missing.
- Elif `source_entity_type == SOURCE_ENTITY_TYPE_COMPANY`: look up `company.candidate_id` where `short_name = source_entity_id` (fallback: `company_id` if `source_entity_id` blank — should not happen on insert after validation). Raise if missing.
- Else (legacy row during ensure before backfill / callers still passing only employer): if `company_id` set, resolve via `company.short_name = company_id` as today; else raise.

Import `SOURCE_ENTITY_TYPE_*` / `validate_source_entity_type` (or existing `validate_job_source` wrappers) from config — same import block that already pulls `JOB_SOURCE_DEFAULT`.

5. Update `save_job` signature and behavior:

- Parameters: keep `source=` as the parent-type write (values `company`|`meteorite`); add `source_entity_id: Optional[str] = None`, `company_id: Optional[str] = None`. Deprecate passing employer via `company=` — accept `company=` as a **temporary alias** that sets `company_id` when `company_id` is None (so pre-#2 tracker keeps compiling); do not document `company` as the parent.
- **INSERT:** require `state`; require parent type (`source` default `SOURCE_ENTITY_TYPE_DEFAULT` / `JOB_SOURCE_DEFAULT`) and non-empty `source_entity_id` after strip; `company_id` optional (NULL allowed). Validate type via `validate_source_entity_type`. Resolve `candidate_id` via the successor in step 4. INSERT columns: `company_id`, `source`, `source_entity_id`, … — never write placeholder short_names into `source`/`source_entity_id`.
- **UPDATE:** allow setting `source`, `source_entity_id`, `company_id` when provided; re-resolve `candidate_id` when parent fields or `candidate_id`/`company_id` change.
- Docstring: state that `source` is parent/track SoT (`company`|`meteorite`); `source_entity_id` is required on insert; `company_id` is optional real employer.

6. Update `get_job_id_by_identity` to take `company_id` (rename param from `company`) and query `company_id = ?`.

7. Update `_job_row_to_dict` / any SELECT helpers that alias `company` so returned dicts expose `company_id`, `source`, `source_entity_id`. If a compatibility key `company` is still read by pre-#2 code paths inside `database.py` only, set `company` = `company_id` in the dict **only when** needed for in-module helpers — do not add UI serialization here.

8. Dedupe helpers `find_candidate_job_by_company_job_id` / `find_candidate_job_by_job_link` / `find_meteorite_dedupe_match` already key on `candidate_id` + job fields — leave match SQL as-is (they already ignore employer column). Confirm they still `SELECT *` and round-trip via `_job_row_to_dict` after the rename.

9. **Hard rule:** do not add any `UPDATE job SET source …` / parent backfill inside `_ensure_job_schema`, startup, or `SEED_CONFIG`. Comment `# AST-1701: DDL-only — parent content backfill is data/sql/ast_1701_… (operator)`.

⚠️ **Decision:** Physical column stays named `source` (prefer-repurpose); Python/docs call it source_entity_type. `company` → `company_id` nullable via rebuild so NOT NULL is actually dropped. Temporary `company=` kwarg alias on `save_job` avoids forcing tracker edits into this ticket’s scope.

## Stage 3: Operator SQL backfill (Susan-runnable)

**Done when:** `data/sql/ast_1701_job_source_entity_backfill.sql` exists, is not referenced from `SEED_CONFIG` / boot, and documents the exact UPDATE sequence Susan runs against `astral.db`.

1. Create `data/sql/` if missing. Add `data/sql/ast_1701_job_source_entity_backfill.sql` with a header comment:

```
-- AST-1701 operator backfill — run manually (sqlite3 astral.db < this file).
-- NOT imported by SEED_CONFIG / _ensure_job_schema / server startup.
-- Run AFTER AST-1701 DDL has been applied (app boot once is enough for DDL).
```

2. SQL steps (single file, ordered):

   a. **Meteorite-linked jobs** (prefer `meteorite.astral_job_id`):  
      `UPDATE job SET source = 'meteorite', source_entity_id = CAST(m.id AS TEXT), company_id = CASE WHEN job.company_id LIKE 'meteorite-%' OR … stem placeholder … THEN NULL ELSE job.company_id END FROM meteorite m WHERE m.astral_job_id = job.astral_job_id`  
      (SQLite form: `UPDATE job SET … WHERE astral_job_id IN (SELECT astral_job_id FROM meteorite WHERE astral_job_id IS NOT NULL)` with correlated subselects for `source_entity_id` / nulling placeholders).  
      Null `company_id` when it matches `METEORITE_CONFIG` placeholder shapes: `company_id LIKE 'meteorite-%'` OR `company_id LIKE '%-' || candidate_id` only when that row is a known meteorite stem company — **keep it simple:** null when `company_id LIKE 'meteorite-%'` OR when `company_id` equals `meteorite.candidate_id`-suffixed stems that appear as `short_name` on companies with `state = 'METEORITE'`. Minimum required by AC: null obvious `meteorite-%` placeholders; do not invent employer names.

   b. **Remaining jobs still `source IS NULL` / `source = 'gazed'` / blank `source_entity_id`:** set `source = 'company'`, `source_entity_id = company_id` (employer short_name already on the row after rename), leave `company_id` as-is when it is not a `meteorite-%` placeholder (else NULL and leave `source_entity_id` from a non-placeholder if present — if both were placeholder-only and no meteorite link, set `source = 'company'` and `source_entity_id` to the old short_name **only if** it is not `meteorite-%`; if the only handle was a placeholder and no meteorite link exists, leave a trailing SELECT diagnostic comment for Susan rather than inventing a meteorite id).

   c. Final verification queries (SELECT-only, commented as “expect 0 rows”):  
      - jobs where `source NOT IN ('company','meteorite')` OR `source IS NULL` OR `trim(source_entity_id) = ''`  
      - jobs where `source = 'gazed'`

3. Grep gate for the implementer (record in the Linear stage comment is enough — do not add CI): confirm `SEED_CONFIG` and startup paths do **not** reference `ast_1701_job_source_entity_backfill.sql` or `UPDATE job SET source` for parent migration.

## Estimate

Confirm Chuckles estimate: 5 — agree

Schema rebuild + writer contract + operator SQL with no boot side effects matches a 5 (migration/backfill risk, multi-file config+data, known pattern from AST-1469).

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1640/AST-1701-job-source-entity-schema-config-ssot-manual-backfill-sql`.
- Do not edit `tracker.py`, `meteorite.py`, `consult.py`, `gazer.py`, or UI in this ticket.
- Do not add auto parent UPDATE on ensure/boot/SEED.
- When a step is ambiguous or the tree has drifted — stop and comment on **parent** AST-1640 with the Stage blocked template; do not improvise.

## Joan validate

[plan-rubric]
**Ticket:** AST-1701
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `sub/AST-1640/AST-1701-job-source-entity-schema-config-ssot-manual-backfill-sql` @ `fb0827d5ebba38a70ed3e1723a882a008bd63d09`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-criteria | X | | No dispatch_task claim shape or criteria literals — plan is config + job DDL/writers + operator SQL only |
| stat.logging.debug | A | | Stage 1 forbids debug/print in pure formatters; Stage 2 keeps `src/data/` free of debug noise per statute |

## Traceability

AC1 → Stages 2–3 (nullable `company_id` + required parent columns on `save_job`; DDL-only ensure; Susan-runnable `data/sql/ast_1701_job_source_entity_backfill.sql`; no `SEED_CONFIG`/boot parent UPDATE). AC2 → Stages 1–2 (`SOURCE_ENTITY_TYPES` retires `gazed` as write authority; prefer-repurpose physical `job.source`; single SoT). Stages 1–3 → parent Functional scope items 1–2, 3, 7 (child partition); parent AC3–9 N/A — siblings #2–#4.

## Findings

### acceptable

- **Location:** Linear assignee
- **Finding:** Ticket assignee is Ada Lovelace, not Joan — Chuckles spawn overrides for this pass; restore implementer per §8 after upshot.
- **Recommendation:** None for plan content.

### discuss

- **Location:** Canon Scope / Citations
- **Finding:** `patt.entity.batch-criteria` is on the frozen list but grades **X** for this footprint — pattern governs `dispatch_task`-sourced claim criteria, not job schema/config SSOT. Likely forward-looking for sibling #4 track routing or inherited from parent partition; mis-selection observation only.
- **Recommendation:** Archie may drop or retain at Discussion; no plan change required for #1.

- **Location:** Stage 2 / `save_job` INSERT (step 5)
- **Finding:** INSERT hard-requires non-empty `source_entity_id`, while pre-#2 `tracker.py` callers still pass `company=` only (gazed create at ~L113). `company=` alias fills `company_id`, not parent id. On `ftr` after #1 merges and before #2, gazed inserts likely fail validation even though resolver step 4 has a company lookup fallback.
- **Recommendation:** Consider INSERT bridge: when `source_entity_type` is `company` (default) and `source_entity_id` is omitted, default `source_entity_id` from `company_id` — keeps epic ordering safe without widening scope into tracker edits. Meteorite-parent writes still correctly wait for #2.

- **Location:** Stage 3 / SQL step 2b
- **Finding:** Placeholder-only rows with no meteorite link defer to a diagnostic SELECT comment rather than inventing ids — honest operator step, but Susan must run verification queries; edge-case volume unknown until backfill.
- **Recommendation:** Implementer records row counts in stage comment; no plan rewrite unless backfill rehearsal finds mass orphans.

### fix-now

(none)

context_tokens≈42000


## Review

- **Build tip:** `origin/sub/AST-1640/AST-1701-job-source-entity-schema-config-ssot-manual-backfill-sql` @ `753c41bde1eb6ebcb1aa11cf9c6f4510edba45d2`
- **Stages:** config SSOT → job schema/writers → operator SQL `data/sql/ast_1701_job_source_entity_backfill.sql`

## Radia review

[code-rubric]

**Ticket:** AST-1701  
**Publish ref:** `6d2a084b31bc1f54f8127ea3346eb5b9d26c938b` (`origin/sub/AST-1640/AST-1701-job-source-entity-schema-config-ssot-manual-backfill-sql`)  
**Corpus:** `fc0c368e5927a57f1561c057ce9a0ff4abe1fb13`  
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-criteria | X | | No `dispatch_task` claim shape or criteria literals — config SSOT, job DDL/writers, operator SQL only |
| stat.logging.debug | A | | No new `logger.debug`/`print` in `src/data/database.py` or pure AST-1701 formatters in `src/utils/config.py` |

## Column diff vs plan stage

(aligned) — Joan graded `patt.entity.batch-criteria` **X** and `stat.logging.debug` **A**; code review matches on both.

## Frame diff

(none) — Description **Acceptance criteria** / **Boundaries** rows already checked and satisfied by the tip.

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Location:** `tests/component/utils/test_config.py`, `docs/test-bible/utils/config.md` (merge-tests tip)  
  **Finding:** `merge-tests(AST-1701)` merged `origin/tests` and carries AST-1688/1691/1698 bible+test hunks alongside AST-1701. Product diff is cleanly scoped to `src/utils/config.py`, `src/data/database.py`, and `data/sql/ast_1701_job_source_entity_backfill.sql`; the extra test/bible rows are Betty merge-tests noise, not sibling product code.  
  **Recommendation:** No resolve-child action; note for epic rollup awareness only.

- **Location:** `data/sql/ast_1701_job_source_entity_backfill.sql` step 2b / orphan diagnostic  
  **Finding:** Placeholder-only rows with no meteorite link remain without invented parent ids; commented orphan SELECT is the operator follow-up Joan flagged at plan.  
  **Recommendation:** Susan runs verification queries after manual backfill; row counts belong in operator notes, not code changes here.

- **Location:** Canon Scope / Citations  
  **Finding:** `patt.entity.batch-criteria` on the frozen list grades **X** for this footprint (same Joan observation).  
  **Recommendation:** Archie may drop at Discussion on a future ticket; no action for AST-1701 resolve-child.

## What's solid

- **Stage 1:** `SOURCE_ENTITY_TYPES` (`company`|`meteorite`) replaces gazed write authority; thin `JOB_SOURCES` aliases; `METEORITE_CONFIG["source_entity_type"]`; breadcrumb format + timezone clock helpers match plan.  
- **Stage 2:** `company` → nullable `company_id` rebuild; `source_entity_id` column; meteorite/company `_resolve_job_candidate_id`; `save_job` INSERT bridge (`company=` → `company_id` → default `source_entity_id` for company parent) addresses Joan’s pre-#2 tracker ordering concern; `_job_row_to_dict` in-module `company` compat; identity index on `company_id`; ensure is DDL-only (no `UPDATE job SET source` in `database.py`).  
- **Stage 3:** Operator SQL ships with meteorite-link + gazed/unset backfill + verification comments; `SEED_CONFIG` grep gate covered by `TestAst1701SourceEntitySchema::test_operator_sql_artifact_not_in_seed_config`.  
- **Tests:** Manifest classes `TestAst1701SourceEntityTypes` and `TestAst1701SourceEntitySchema` assert closed set, bridge, meteorite cid resolve, gazed rejection, DDL-only ensure, and seed isolation.

## Recommended actions (downstream — not Radia lane)

- Chuckles: append this artifact to the issue doc, commit `docs(AST-1701): Radia review — clean`, push sub ref, post slim upshot `--as radia`, move to **Review Posted**.  
- datt: **PROCEED** → **User Testing** (no resolve-child round).  
- Susan: run `data/sql/ast_1701_job_source_entity_backfill.sql` manually after DDL boot before UAT parent checks on existing rows.

context_tokens≈48000

## Bug: AST-1706 — get_job_batch JOIN on company_id

Orphaned fix child of AST-1705. AST-1701 renamed `job.company` → nullable `company_id` but left `get_job_batch`'s employer JOIN on the retired column. Canon for this delta inherits AST-1701 Citations (`patt.entity.batch-criteria`; `stat.logging.debug`) — this footprint does not touch claim-criteria literals or add logging.

### As-is

`qualify_meteorite` (and any other job-batch dispatch) claims a batch, then `tracker.get_new_job_batch` → `database.get_job_batch` runs `SELECT j.*, c.job_site FROM job j LEFT JOIN company c ON j.company = c.short_name WHERE j.batch_id = ?`. After the AST-1701 table rebuild, `job.company` does not exist, so SQLite raises `OperationalError: no such column: j.company`, the dispatcher truncates the batch, and qualify never runs.

### To-be

`get_job_batch` joins employer on `j.company_id = c.short_name`, returns the same job dicts (via `_job_row_to_dict`) plus `job_site` when `company_id` matches a company row, and `qualify_meteorite` batches proceed without a schema OperationalError. Rows with NULL `company_id` still return with `job_site` NULL (LEFT JOIN).

### Repro

1. Boot against a DB whose `job` table already has `company_id` and no `company` column (post–AST-1701 `_ensure_job_schema` / rebuild).
2. Insert (or land) at least one job in a claimable state with a non-empty `batch_id` (or claim via `get_new_job_batch` / dispatcher for `qualify_meteorite`).
3. Call `database.get_job_batch(<that batch_id>)` (or let dispatcher claim → load).
4. Observe: `OperationalError: no such column: j.company` at `database.py` `get_job_batch` execute of the JOIN on `j.company`.

Concrete log shape from production (2026-09-17): dispatcher starts `qualify_meteorite` batch `qualify_meteorite-3cb6fd14-7596-44bb-897b-87d4879af3d3` → `tracker.get_new_job_batch` → `database.get_job_batch` → `_with_conn` fails on the `j.company` JOIN → dispatcher truncates the batch.

### Root cause

AST-1701 Stage 2 rebuilt `job` (`company` → nullable `company_id`) and updated writers/identity/`_job_row_to_dict`, but the live SQL string inside `get_job_batch` still predicates `ON j.company = c.short_name`. That is the only remaining `j.company` column reference in product SQL on this tree.

### Proposed change

In `src/data/database.py`, function `get_job_batch` (`_with_conn`), change the single execute string:

- From: `LEFT JOIN company c ON j.company = c.short_name`
- To: `LEFT JOIN company c ON j.company_id = c.short_name`

Leave `_job_row_to_dict`'s existing `company_id` → `company` in-module compat alias unchanged. Do not touch `tracker.py`, claim/clear batch helpers, or schema ensure. No new files.

Smoke for make-fix / test-fix: call `get_job_batch` against a migrated DB with (a) a job whose `company_id` matches `company.short_name` and that company has `job_site` set → row returns without OperationalError and includes `job_site`; (b) a job with `company_id` NULL → row returns, `job_site` is NULL.

### Blast radius

- Call path: `dispatcher` → `tracker.get_new_job_batch` / `tracker.get_job_batch` → `database.get_job_batch` — every job-batch dispatch (`qualify_meteorite` and any other task that claims jobs by `batch_id`).
- Shared: `_job_row_to_dict` still shapes returned dicts; JOIN only adds `job_site` from `company`.
- Out of this fix's Scope: `tracker.py` string match on `"job.company"` in an error message (~L70) is not live SQL and is not in AST-1706 Component/Technical scope — leave alone unless a later ticket widens scope.
- Tests: any coverage that exercised `get_job_batch` against a post-rename schema would have failed open; Betty/fix-board decide whether a targeted repro test is required.

### What must still hold

- AST-1701: physical column remains `company_id` (nullable); no resurrection of `job.company` NOT NULL; ensure stays DDL-only (no parent content UPDATE).
- `get_job_batch` still returns full job records for `batch_id` with `job_data` / `state_history` parsed, plus `job_site` when the employer JOIN hits.
- `_job_row_to_dict` compat (`company` = `company_id` when `company` absent) remains for in-module / pre-#2 readers.
- `stat.logging.debug`: no new `logger.debug` / `print` in this one-line fix.
- No change to claim criteria, `clear_job_batch`, or source-entity parent fields (`source` / `source_entity_id`).

## Bug: AST-1772 — print resume/cover without company short name

Orphaned fix child of AST-1763 (mini-parent bug; no UAT ancestor epic). AST-1701 made `job.company_id` nullable and denormalized `job.candidate_id` (AST-1598), but `builder.build_resume` / `build_cover_letter` still hard-require `job.get("company")` before load. Print HTML entry path (AST-1117 routes / JAR fetch-then-blob) is fine — ownership resolve in builder is the lagging consumer. Canon for this delta: no frozen Canon Scope on AST-1772; keep `stat.logging.debug` discipline (no new debug/print noise in `src/core/builder.py`); do not invent UI business rules.

### As-is

On Recommended (`/jobs/recommended`), Print Resume / Print Cover Letter call `GET /candidate/resume|<job_id>` / `cover/<job_id>` → `builder.build_resume` / `build_cover_letter`. Those functions gate on `job.get("company")` and raise `ValueError("Job missing company short name")` when the employer short name is missing/null. After AST-1701, meteorite (and other) jobs can have null `company_id` / compat `company` while `candidate_id` is already on the job row. `api_resume_html` forwards that `ValueError` as JSON `{"error":"Job missing company short name"}`; the print tab shows that JSON instead of HTML.

### To-be

Print Resume and Print Cover Letter render the job's resume/cover HTML whenever the owning candidate can be resolved — prefer denormalized `job.candidate_id`, fall back to `company` / `company_id` → `get_company` → `candidate_id` only when the direct field is absent. Missing employer short name alone must not hard-fail print. Raise a clear ownership error only when neither path resolves a candidate. Company-parent jobs with a real employer still print unchanged.

### Repro

1. Open `/jobs/recommended` as candidate `somerset` (or any session whose jobs include a row with non-blank `candidate_id` and null `company_id` / `company` — typical post–AST-1701 meteorite job).
2. Open JAR for that job → **Print Resume** (or **Print Cover Letter**).
3. Observe new tab body: `{"error":"Job missing company short name"}` (cover path same string), not printable HTML.
4. Control: same Print actions on a company-parent job with non-null `company_id` still return HTML today — must keep working after the fix.

Diagnostic timestamp from parent AST-1763: `2026-09-21T23:53:39.335Z`, route `/jobs/recommended`, message `Job missing company short name`.

### Root cause

`build_resume` and `build_cover_letter` still use the pre–AST-1701 ownership chain (`company` short name → `get_company` → `company.candidate_id`) and treat a missing/null `job.company` as a hard error before ever reading `job.candidate_id`. Tracker already prefers `job.candidate_id` in `_candidate_id_for_job`; builder print entry points never adopted that preference.

### Proposed change

All edits in `src/core/builder.py` only. Leave `tracker._candidate_id_for_job`, `api_resume_html.py`, `JobAnalysisReportModal.tsx`, and `build_*_from_job` unchanged.

1. Add a private helper `_owning_candidate_id_from_job(job: Dict[str, Any]) -> Optional[str]` next to the other builder load helpers. Behavior (mirror `tracker._candidate_id_for_job`, but on the already-loaded job dict — no second `get_job`):
   - If `job.get("candidate_id")` is a non-blank `str`, return `strip()` of it.
   - Else take `company_key = job.get("company")` (compat alias of nullable `company_id` from `_job_row_to_dict`). If it is a non-blank `str`, `database.get_company(company_key.strip())`; if that row has a non-blank `candidate_id`, return it as `str`.
   - Else return `None` (null/blank employer with no denormalized `candidate_id`, missing company row, or company row without `candidate_id`).

2. In `build_resume`, after `tracker_mod.get_job(job_id)` succeeds, **replace** the block from `company_key = job.get("company")` through the `"Company … has no candidate_id"` raise with:
   - `candidate_id = _owning_candidate_id_from_job(job)`
   - If falsy: `_emit_builder_failure(..., message=...)` then `raise ValueError("Job has no resolvable owning candidate")` — do **not** raise `"Job missing company short name"`.
   - Keep the existing `candidate_mod.get_candidate(str(candidate_id))` / `"Candidate not found: …"` path and the `build_resume_from_job(...)` return unchanged.

3. In `build_cover_letter`, apply the **identical** ownership-resolve replacement (same helper, same new error string, same keep of candidate-not-found + `build_cover_letter_from_job`).

4. Do not wire builder to call `tracker._candidate_id_for_job` (would re-fetch the job); do not change tracker's company fallback. No schema / FE / route changes.

Smoke for make-fix / test-fix: (a) job with `candidate_id="somerset"` and `company_id`/`company` null → `build_resume` / `build_cover_letter` return HTML (or the real missing-artifact error if pins empty — never `"Job missing company short name"`); (b) job with real `company_id` and no denormalized `candidate_id` but company row has `candidate_id` → still prints; (c) job with neither resolvable path → `ValueError("Job has no resolvable owning candidate")` forwarded by `api_resume_html` as JSON `error`.

### Blast radius

- Call path: JAR Print Resume / Print Cover Letter → `api_resume_html` → `build_resume` / `build_cover_letter` → (unchanged) `build_*_from_job`.
- Any other caller of `build_resume` / `build_cover_letter` by job id (preview materials, direct `/candidate/resume|cover/<id>`) gets the same ownership resolve.
- Shared: `tracker._candidate_id_for_job` stays the SoT preference for tracker-internal use; builder helper intentionally duplicates the preference on the in-memory job to avoid a second DB read and a cross-module private call.
- Out of scope (explicit): HTML emit, FE print buttons, `job` DDL, tracker land/writes.
- Tests: existing builder tests that assert `"Job missing company short name"` will need Betty/fix-board attention; product tree must not invent that string for null-employer + present `candidate_id` jobs after the fix.

### What must still hold

- AST-1701: `company_id` remains nullable; `_job_row_to_dict` `company` compat alias remains; no resurrection of required employer short name on job.
- AST-1598: denormalized `job.candidate_id` is a valid ownership source for print.
- AST-1117 / AST-605: Print still opens Flask HTML via `/candidate/resume|<id>` and `/candidate/cover/<id>` (pin-resolved bodies via existing `build_*_from_job`); routing/proxy unchanged.
- Company-parent jobs with a resolvable employer still print resume and cover letter.
- Real `"Job not found"` / `"Candidate not found"` errors remain; only the ownership-resolve hard-fail string changes when neither `candidate_id` nor company lookup works.
- `stat.logging.debug`: no new `logger.debug` / `print` in this builder change; keep existing `_emit_builder_failure` on the new raise path.

## Threads (generated — epic_registry mirror)

_(generated from epic registry — do not hand-edit; edits are overwritten)_

### Team

| Agent | Role | Thread |
|--------|-------|--------|
| Ada | engineer | `/home/susan/.cursor/chats/0f76620d650d7b1640f39ad155da7742/eca3082c-eb7a-4df1-a3ff-bc48066b98d4/store.db` |
| Betty | qa | `/home/susan/.cursor/chats/2d0fa47271e47a831e103b336fb3fbc8/04a57f8a-59bf-4e90-bc97-473c1037bbed/store.db` |
| Radia | review | `/home/susan/.cursor/chats/0f76620d650d7b1640f39ad155da7742/cc622d7a-465e-4f5d-a272-25a1fda6b285/store.db` |

### Git

| Ticket | `origin/…` |
|--------|------------|
| AST-1705 (parent) | ftr/AST-1705-qualify-meteorite-is-failing |
| AST-1706 | sub/AST-1705/AST-1706-fix-get-job-batch-company-id |

**Epic worktree:** `astral-AST-1705/` — one active sub checked out at a time.
