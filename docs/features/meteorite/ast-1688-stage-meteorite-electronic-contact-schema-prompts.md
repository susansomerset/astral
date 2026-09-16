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
