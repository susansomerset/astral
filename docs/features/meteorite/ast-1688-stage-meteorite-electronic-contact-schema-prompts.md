<!-- linear-archive: AST-1688 archived 2026-09-24 -->

## Linear archive (AST-1688)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1688/stage-meteorite-electronic-contact-schema-prompts-reply-to-emails-in  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1684 — Reply-to emails in meteorite when single_jd_no_link  
**Blocked by / blocks / related:** parent: AST-1684; blocks: AST-1689

### Description

## What this implements

Owns config response-key / column literals and `agent_task` prompts: metadata-first best electronic contact for resume send on text outcomes (`single_jd_no_link`, `multi_jd_inline`) and for link rows that may bot-block. Does **not** own DB column wiring or row map persist (sibling #2).

## Citations

`patt.task.daisy-chain`; `stat.logging.debug`, `stat.logging.info`.

## Scope

`src/utils/config.py` — **modified** — `stage_meteorite` response schema gains electronic-contact field(s); METEORITE_CONFIG / STAGE_METEORITE_CONFIG gains the meteorite-column / response-key literal(s); text outcomes stay the closed `text_source_ref_outcomes` set (include `multi_jd_inline`). `data/admin/agent_task.json` — **modified** — `stage_meteorite` prompts: best electronic contact to send the resume; **must use metadata**; empty when undeterminable; lockstep with TASK_CONFIG. `config.py` — Add optional electronic-contact field(s) on `TASK_CONFIG["stage_meteorite"].response_schema.jobs.items_schema`; add config key literal(s) for the meteorite column / response key; keep outcome enum unchanged; ensure prompts/docs name `single_jd_no_link` and `multi_jd_inline`. `agent_task.json` — Teach metadata-first electronic contact for resume send; forbid invention.

## Acceptance criteria

- [X] 1\. `TASK_CONFIG["stage_meteorite"].response_schema.jobs.items_schema` includes the config-named electronic-contact field(s) — fail if schema still only has job_title/job_link/company_job_id/jd_text/employer_name.
- [X] 2\. `agent_task` / prompts for `stage_meteorite` instruct metadata-first best electronic contact for resume send — fail if prompts omit metadata or tell Ruth to invent addresses.

## Boundaries

- [X] Does not own DB column / allowlist / insert path (sibling #2). Does not map contact onto meteorite rows. Does not touch job `job_data` or Recommended UI (AST-1685).

## Notes for planning

Bang `!` — blocks sibling #2. Estimate 3.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1684-reply-to-emails-in-meteorite-when-single-jd-no-link`, child `sub/AST-1684/AST-1688-stage-meteorite-electronic-contact-schema-prompts`. Created at dispatch-parent.

## QA test manifest

1. Electronic-contact schema + literals: `tests/component/utils/test_config.py::TestAst1688StageMeteoriteElectronicContactConfig`
2. Prior stage shell: `tests/component/utils/test_config.py::TestAst1529StageMeteoriteConfig`
3. Catalog prompts + fixture twin: `tests/component/core/test_repo_admin_json.py::TestAst1688StageMeteoriteElectronicContactPrompts`
4. Prior catalog + fixture lockstep: `tests/component/core/test_repo_admin_json.py::TestAst1529StageMeteoriteCatalogRow`
5. Whole-file fixture identity: `tests/component/core/test_repo_admin_json.py::TestAst1494QualifyMeteoriteCompanyStemCatalog::test_fixture_byte_identical_to_catalog`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/utils/test_config.py::TestAst1688StageMeteoriteElectronicContactConfig \
  tests/component/utils/test_config.py::TestAst1529StageMeteoriteConfig \
  tests/component/core/test_repo_admin_json.py::TestAst1688StageMeteoriteElectronicContactPrompts \
  tests/component/core/test_repo_admin_json.py::TestAst1529StageMeteoriteCatalogRow \
  tests/component/core/test_repo_admin_json.py::TestAst1494QualifyMeteoriteCompanyStemCatalog::test_fixture_byte_identical_to_catalog \
  -q
```

**Bible shasum (publish tip** `30f3c1ce`**):**

* `docs/test-bible/utils/config.md` — `5593842b845479d66009f8eb7f13d3c7fc6e2cc4`
* `docs/test-bible/core/repo_admin_json.md` — `c763b154f7654dc92d170fae24adbf339f537e38`

### Comments

#### radia — 2026-09-16T22:38:10.354Z
[code-rubric] PROCEED (Commit: 30f3c1ce) schema prompts lockstep clean

#### betty — 2026-09-16T22:32:58.427Z
`origin/sub/AST-1684/AST-1688-stage-meteorite-electronic-contact-schema-prompts` @ `30f3c1ce` · electronic_contact coverage ready

#### joan — 2026-09-16T22:25:39.390Z
[plan-rubric] PROCEED (Commit: 0b5620015d08c02ec1f13fac440c31051a7be8cd) schema prompts lockstep

#### ada — 2026-09-16T22:23:31.338Z
`origin/sub/AST-1684/AST-1688-stage-meteorite-electronic-contact-schema-prompts` @ `0b5620015d08c02ec1f13fac440c31051a7be8cd` · plan ready

---

# AST-1688 — stage_meteorite electronic-contact schema + prompts

**Linear:** [AST-1688](https://linear.app/astralcareermatch/issue/AST-1688/stage-meteorite-electronic-contact-schema-prompts-reply-to-emails-in)  
**Parent:** [AST-1684](https://linear.app/astralcareermatch/issue/AST-1684/reply-to-emails-in-meteorite-when-single-jd-no-link) — Reply-to emails in meteorite when single_jd_no_link  
**Publish ref:** `sub/AST-1684/AST-1688-stage-meteorite-electronic-contact-schema-prompts`

Add config-owned electronic-contact field(s) on `stage_meteorite` Ruth response schema and matching METEORITE / STAGE_METEORITE key literals, and teach `agent_task` prompts to return a metadata-first best electronic contact for resume send (empty when undeterminable; never invent). Does **not** wire DB columns, row map, or persist (sibling **AST-1689**).

## UAT fitness

- **AC restored:** Parent AC1 — `TASK_CONFIG["stage_meteorite"].response_schema.jobs.items_schema` includes the config-named electronic-contact field(s) — fail if schema still only has job_title/job_link/company_job_id/jd_text/employer_name. Parent AC2 — `agent_task` / prompts for `stage_meteorite` instruct metadata-first best electronic contact for resume send — fail if prompts omit metadata or tell Ruth to invent addresses.
- **Correct outcome:** After classify, each returned `jobs[]` item may carry a non-invented `electronic_contact` string when Reply-To / From (or equivalent labeled source metadata already present in the ingress blob) or JD/context makes a resume-send address determinable; text outcomes `single_jd_no_link` / `multi_jd_inline` and link outcomes that may later bot-block are in scope for the field; empty/omit when nothing is determinable.
- **Sibling check:** **AST-1689** owns meteorite column + classify→row map/persist + soft-fail warn + Style D. This ticket only publishes the response-key / column **literals** and prompts; AST-1689 must read those same config keys (not hardcode a parallel string). Parent AC3–8 and job_data / Recommended UI stay out of this child.
- **Not sufficient:** Removing a stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Putting contact onto job `job_data`, inventing addresses in prompts, changing the six outcome literals, or implementing DB/map/persist in this child (those belong to AST-1689 / AST-1685).

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/utils/config.py` — **modified** — `stage_meteorite` response schema gains electronic-contact field(s); METEORITE_CONFIG / STAGE_METEORITE_CONFIG gains the meteorite-column / response-key literal(s); text outcomes stay the closed `text_source_ref_outcomes` set (include `multi_jd_inline`).
- `data/admin/agent_task.json` — **modified** — `stage_meteorite` prompts: best electronic contact to send the resume; **must use metadata**; empty when undeterminable; lockstep with TASK_CONFIG.
- `config.py` — Add optional electronic-contact field(s) on `TASK_CONFIG["stage_meteorite"].response_schema.jobs.items_schema`; add config key literal(s) for the meteorite column / response key; keep outcome enum unchanged; ensure prompts/docs name `single_jd_no_link` and `multi_jd_inline`.
- `agent_task.json` — Teach metadata-first electronic contact for resume send; forbid invention.

All Files Changed / Stages stay inside that set.

**Out of scope (siblings / other epics):**

- `database.py` meteorite column / allowlist / insert — **AST-1689**
- `meteorite.py` classify→row map, BOT_BLOCKED preserve, soft-fail warn, Style D — **AST-1689**
- `consult.py` / `agent.py` invoke or validator wires — **AST-1689** only if needed; not this ticket
- job `job_data` / Recommended / JobDetail UI — **AST-1685**
- Changing the six `STAGE_METEORITE_CONFIG["outcomes"]` literals
- Fetching new Gmail headers (e.g. Reply-To) in `gmail.py` — not in Scope; email ingress already wraps From/To/Subject/Date into the blob via `strip_extract_email_html`

**Depends on:** none (Bang `!` — blocks sibling **AST-1689**).

**AC partition (this ticket):** Parent AC1 and AC2 only.

**Canon Scope (read at plan):** `patt.task.daisy-chain` (full — contact is carried on the meteorite row through stage→scrape→land / bot-blocked hops by sibling; this ticket must not invent a parallel re-derive path in prompts). `stat.logging.debug`, `stat.logging.info` — **id-only** here (no logging code in this ticket’s files).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `electronic_contact` optional field on `stage_meteorite` jobs `items_schema`; add response-key + meteorite-column literals on `STAGE_METEORITE_CONFIG` / `METEORITE_CONFIG`; lockstep asserts; leave outcome enum / `text_source_ref_outcomes` unchanged | utils |
| `data/admin/agent_task.json` | Extend `stage_meteorite` `cache_prompt` (+ short `user_prompt` touch) for metadata-first electronic contact; forbid invention; keep six outcomes named including `single_jd_no_link` / `multi_jd_inline` | catalog |

## Stage 1: Config literals + response schema field

**Done when:** `TASK_CONFIG["stage_meteorite"].response_schema.jobs.items_schema` includes optional `electronic_contact` keyed by `STAGE_METEORITE_CONFIG["electronic_contact_response_key"]`; `METEORITE_CONFIG["electronic_contact_column"]` equals that same string; outcome `enum` and `text_source_ref_outcomes` (`single_jd_no_link`, `multi_jd_inline`) are unchanged; `python3 -m py_compile src/utils/config.py` succeeds (repo venv if needed).

1. In `src/utils/config.py` header inventory comment for `STAGE_METEORITE_CONFIG`, append that it also owns the electronic-contact **response-key** literal for `stage_meteorite` (AST-1688). In the `METEORITE_CONFIG` inventory bullet, append that it owns the meteorite-table **column** name literal for electronic contact (AST-1688; consumed by AST-1689).

2. In `METEORITE_CONFIG` (near `employer_name_job_data_key`), add:

```python
    # AST-1688: meteorite-row column for best electronic resume contact (sibling AST-1689 writes it).
    "electronic_contact_column": "electronic_contact",
```

3. In `STAGE_METEORITE_CONFIG`, after `skip_outcomes` (before the closing `}`), add:

```python
    # AST-1688: Ruth jobs[] JSON key for best electronic resume contact (lockstep with items_schema).
    "electronic_contact_response_key": "electronic_contact",
```

4. In `TASK_CONFIG["stage_meteorite"]["response_schema"]["jobs"]["items_schema"]`, after `employer_name`, add:

```python
                    # AST-1688: best electronic contact to send the resume (metadata-first; optional)
                    "electronic_contact": {"type": "str", "required": False},
```

⚠️ **Decision:** One optional string field named `electronic_contact` (not a nested object, not separate reply_to/from keys). Ruth returns the single best address for resume send; sibling AST-1689 stores that one column. Matches parent “best electronic contact” singular.

5. Immediately after the existing `STAGE_METEORITE_CONFIG` / `TASK_CONFIG["stage_meteorite"]` asserts (near the outcome-enum lockstep block), add:

```python
assert STAGE_METEORITE_CONFIG["electronic_contact_response_key"] == "electronic_contact"
assert METEORITE_CONFIG["electronic_contact_column"] == STAGE_METEORITE_CONFIG[
    "electronic_contact_response_key"
]
assert (
    STAGE_METEORITE_CONFIG["electronic_contact_response_key"]
    in TASK_CONFIG["stage_meteorite"]["response_schema"]["jobs"]["items_schema"]
)
assert (
    TASK_CONFIG["stage_meteorite"]["response_schema"]["jobs"]["items_schema"][
        STAGE_METEORITE_CONFIG["electronic_contact_response_key"]
    ]["required"]
    is False
)
# Outcome vocabulary and text source-ref partition unchanged (AST-1529).
assert "single_jd_no_link" in STAGE_METEORITE_CONFIG["text_source_ref_outcomes"]
assert "multi_jd_inline" in STAGE_METEORITE_CONFIG["text_source_ref_outcomes"]
```

Do **not** change `outcomes`, `landable_outcomes`, `text_source_ref_outcomes`, `url_scrape_outcomes`, or `skip_outcomes`.

## Stage 2: agent_task prompts — metadata-first electronic contact

**Done when:** `data/admin/agent_task.json` row `task_key == "stage_meteorite"` teaches metadata-first best electronic contact on jobs items, forbids invention, still names all six outcomes including `single_jd_no_link` and `multi_jd_inline`; `user_prompt` mentions the `electronic_contact` field; JSON remains valid.

1. In `data/admin/agent_task.json`, locate the object with `"task_key": "stage_meteorite"`. Edit **`cache_prompt`** only by **appending** a new section after the existing `## SOURCE-REF RULES` block (do not rewrite the six OUTCOMES or SOURCE-REF RULES). Append exactly this section (literal text):

```
## ELECTRONIC CONTACT (resume send)

For every jobs item you return (text outcomes single_jd_no_link / multi_jd_inline, and link outcomes single_jd_with_more / link_list that may later be unusable), set electronic_contact to the best electronic address to send the resume.

Prefer message metadata already present in the ingress blob (labeled From / To / Reply-To / equivalent header lines) over body text — the body rarely carries a usable resume address. If metadata has nothing determinable, you may use an explicit address in the JD/context. If still undeterminable, omit electronic_contact or return an empty string.

Never invent addresses, never guess domains, never copy the candidate's own address as the employer contact.
```

2. Update the same row’s **`user_prompt`** to (replace the whole string):

```
Read CONTENT. Return JSON with outcome (exactly one closed outcome literal) and jobs (scrap fields per outcome, including optional electronic_contact per item; empty list for not_job_content and not_original_posting). Prefer metadata for electronic_contact; never invent addresses. Do not emit grade vectors.
```

3. Do **not** change `agent_id`, `task_group_name`, `task_group_order`, `task_seq`, `run_next`, or other rows. Do **not** edit `docs/uat-fixtures/**` in this ticket (Betty owns fixture twin at qa-child if needed).

4. Validate JSON: `python3 -c "import json; json.load(open('data/admin/agent_task.json'))"`.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1684/AST-1688-stage-meteorite-electronic-contact-schema-prompts`.
- Do not add files outside the Files Changed table.
- Do not implement AST-1689 persist/map/DB work.
- On ambiguity or codebase drift: stop, comment on **parent** AST-1684 with the Stage blocked format, wait.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1688
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref tip:** `0b5620015d08c02ec1f13fac440c31051a7be8cd` (`sub/AST-1684/AST-1688-stage-meteorite-electronic-contact-schema-prompts`)

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.task.daisy-chain | A | | Stage captures `electronic_contact` in Ruth response; prompts forbid invention/re-derive; persist/map deferred to AST-1689 per Scope gate |
| stat.logging.debug | X | | id-only on ticket; no logging code in Files Changed (`config.py`, `agent_task.json`) |
| stat.logging.info | X | | id-only on ticket; no logging code in Files Changed |

## Traceability

AC1 → Stage 1 · AC2 → Stage 2 · parent AC3–9 N/A (AST-1689 / AST-1685 / out-of-scope per plan Scope gate + UAT fitness)

## Findings

### discuss

- **Location:** Stage 2 `## ELECTRONIC CONTACT` prompt text; Scope gate “Fetching new Gmail headers (e.g. Reply-To) in `gmail.py` — not in Scope”
- **Finding:** Prompt names Reply-To as preferred metadata, but live email ingress (`strip_extract_email_html`) wraps **From/To/Subject/Date** only — Reply-To is not in today’s blob unless added elsewhere.
- **Recommendation:** Acceptable for this child (AC1–AC2 only): metadata-first + forbid-invention still holds via From/To. Flag for epic follow-on if parent AC3 Reply-To cases must pass before header ingest lands; do not block AST-1688 on gmail work.

### acceptable

- **Location:** Stage 1 `METEORITE_CONFIG["electronic_contact_column"]` literal
- **Finding:** Column name published here for AST-1689 lockstep even though DB wiring is sibling-owned — matches parent partition and plan sibling check.
- **Recommendation:** None; correct bang-first handoff.

## R6 checklist (summary)

- Definition fidelity: child owns config literals + prompts only; no DB/map/persist/UI creep.
- Scope gate: Files Changed = `config.py` + `agent_task.json` only; out-of-scope rows explicit.
- DRY: reuses existing STAGE_METEORITE / METEORITE lockstep assert pattern; no parallel vocabulary.
- Self-assessment: Estimate confirm line present; stages are concrete with done-when gates.
- Plan Discuss rounds: 0 completed (Plan Ready first pass).

context_tokens≈42000

## Review (build stub)

**Publish ref:** `origin/sub/AST-1684/AST-1688-stage-meteorite-electronic-contact-schema-prompts`
**Plan path:** `docs/features/meteorite/ast-1688-stage-meteorite-electronic-contact-schema-prompts.md`

**Built tip:** `04aba196e1f3fac4df537e0d13ce40786931e5db` (`04aba196`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `fc3de690` | `electronic_contact` on `stage_meteorite` items_schema; STAGE/METEORITE config literals + asserts |
| 2 | `04aba196` | `agent_task` stage_meteorite metadata-first electronic_contact prompts (surgical; no catalog-wide rewrite) |

**Betty note:** AST-756 / uat-fixtures twin intentionally out of Scope — sync at qa-child if component tests require it.

## Radia review

[code-rubric]
**Ticket:** AST-1688
**Publish ref:** `30f3c1ce2025c5acf3f071a36939162245f4fdf3`
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.task.daisy-chain | A | | |
| stat.logging.debug | X | | |
| stat.logging.info | X | | |

## Column diff vs plan stage

(aligned) — Joan: `patt.task.daisy-chain` A, `stat.logging.debug` X, `stat.logging.info` X; code review matches on all three.

## Frame diff

(none)

## Findings

### discuss

- **Location:** `data/admin/agent_task.json` `stage_meteorite` `cache_prompt` § ELECTRONIC CONTACT; plan Scope gate (“Fetching new Gmail headers (e.g. Reply-To) in `gmail.py` — not in Scope”)
- **Finding:** Prompt names Reply-To as preferred metadata, but live email ingress (`strip_extract_email_html` / `INBOX_CREATE_JOB_CONFIG["subject_html_template"]`) wraps **From / To / Subject / Date** only — Reply-To is not in today’s blob unless added elsewhere.
- **Recommendation:** Acceptable for this child (AC1–AC2 only): metadata-first + forbid-invention still holds via From/To (and explicit JD/context fallback). Flag for parent epic / AST-1689 UAT if Reply-To–driven cases must pass before header ingest lands; do not block AST-1688 on `gmail.py` work.

### advisory

- **Location:** `feea51d2` → `04aba196` commit pair on `data/admin/agent_task.json`
- **Finding:** Stage 2’s first commit reformatted the whole catalog (~92-line diff); the follow-up commit narrowed to `stage_meteorite` only (~90-line revert/re-apply). Tip + `TestAst1494QualifyMeteoriteCompanyStemCatalog::test_fixture_byte_identical_to_catalog` confirm whole-file byte identity is restored.
- **Recommendation:** No action on tip; worth remembering for future catalog edits — surgical row edit only.

## What's solid

- `TASK_CONFIG["stage_meteorite"].response_schema.jobs.items_schema` gains optional `electronic_contact`; `STAGE_METEORITE_CONFIG["electronic_contact_response_key"]` and `METEORITE_CONFIG["electronic_contact_column"]` are lockstep with module-level asserts — sibling AST-1689 can consume literals without parallel strings.
- Six outcome literals and `text_source_ref_outcomes` (`single_jd_no_link`, `multi_jd_inline`) unchanged; new asserts explicitly guard that partition.
- `agent_task.json` `stage_meteorite` prompts match plan Stage 2 verbatim (metadata-first, forbid invention, names text + link outcomes).
- Component tests cover schema literals, `_validate_response_schema` omit/string/empty paths, prompt content, and AST-756 fixture twin sync (Betty path; plan had deferred fixture to qa-child).
- Diff stays inside ticket partition: `config.py` + `agent_task.json` product surface only; no DB/map/persist/UI creep.

## Recommended actions

- Chuckles: append artifact, commit `docs(AST-1688): Radia review — clean`, post slim upshot, move to **Review Posted** → datt **PROCEED** path to **User Testing** (no fix-now items).
- Epic follow-on (not AST-1688): if parent AC requires Reply-To specifically, track header ingest separately; prompts already allow “equivalent header lines” once blob carries them.

context_tokens≈38000
