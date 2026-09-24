# AST-1684 — Reply-to emails in meteorite when single_jd_no_link

<!-- linear-archive: AST-1684 archived 2026-09-24 -->

## Linear archive (AST-1684)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1684/reply-to-emails-in-meteorite-when-single-jd-no-link  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

When meteorite ingress has no usable posting URL — text lands (`single_jd_no_link`, `multi_jd_inline`) or a link scrape that ends **BOT_BLOCKED** / otherwise unusable — operators still need somewhere electronic to send the resume. This epic asks Ruth (`stage_meteorite`) for the best electronic contact from **message metadata** (and context), and stores it on the **meteorite** staging row — not on the job — so bot-blocked notify, paste recovery, and later UI (AST-1685) can use it without inventing an apply URL.

## Functional scope

1. **Ruth returns best electronic resume contact** — On stage for text outcomes (`single_jd_no_link`, `multi_jd_inline`) and for link outcomes that may later bot-block, Ruth returns the best electronic contact to send the resume, preferring **email metadata** (Reply-To / From and equivalent source metadata) because the body rarely includes it; she may also use JD/context when metadata is empty. She must not invent contacts.
2. **Persist on the meteorite row** — Contact is stored on the `meteorite` table (config-named column / field), not in job `job_data` and not only as `company_stem`.
3. **When contact matters** — Contact is required for operator reply when there is no usable link: text source-ref outcomes, **BOT_BLOCKED**, or otherwise no apply URL. Successful link scrapes may still carry contact from stage but land does not depend on it.
4. **Map through classify fan-out** — Stage → `insert_meteorite_rows` / updates keep contact on the row through READY / BOT_BLOCKED; it is not dropped the way optional display fields are today.
5. **Soft-fail on persist** — If writing contact fails after an otherwise good classify/land transition, **warn and continue** (quick-turnaround; do not fail the row solely for missing contact write).
6. **Debug observability** — When `debug=True`, Style D shows contact returned vs recorded on the meteorite row; no new debug-contract noise when `debug=False`.

## Component scope

* `src/utils/config.py` — **modified** — `stage_meteorite` response schema gains electronic-contact field(s); METEORITE_CONFIG / STAGE_METEORITE_CONFIG gains the meteorite-column / response-key literal(s); text outcomes stay the closed `text_source_ref_outcomes` set (include `multi_jd_inline`).
* `data/admin/agent_task.json` — **modified** — `stage_meteorite` prompts: best electronic contact to send the resume; **must use metadata**; empty when undeterminable; lockstep with TASK_CONFIG.
* `src/data/database.py` — **modified** — meteorite schema + insert/update allowlist for the new contact field (header inventory / ensure path as plan chooses).
* `src/core/meteorite.py` — **modified** — classify→row map and BOT_BLOCKED / land paths carry contact onto the meteorite row; soft-fail warn on persist miss; Style D when debug.
* `src/core/consult.py` — **modified** only if stage invoke mapping must forward the new response key(s); otherwise untouched.
* `src/core/agent.py` — **modified** only if schema validation needs a one-line wire; otherwise untouched.

Out of scope: writing contact onto job / `job_data`; Recommended / JobDetail UI (AST-1685); changing the six stage outcome literals; inventing apply URLs; bulk backfill of old meteorite rows; rewriting `qualify_meteorite` `company_stem` (company provenance stays separate).

## Technical scope

* `config.py` — Add optional electronic-contact field(s) on `TASK_CONFIG["stage_meteorite"].response_schema.jobs.items_schema`; add config key literal(s) for the meteorite column / response key; keep outcome enum unchanged; ensure prompts/docs name `single_jd_no_link` and `multi_jd_inline`.
* `agent_task.json` — Teach metadata-first electronic contact for resume send; forbid invention.
* `database.py` — New meteorite column + `_UPDATE_METEORITE_ALLOWED` / insert path so contact can be written at NEW fan-out and updated later.
* `meteorite.py` — Map Ruth contact into row dicts for text and link fan-out; preserve contact into BOT_BLOCKED; on persist failure log warning and continue; Style D when debug.
* `consult.py` / `agent.py` — Only if stage invoke or validator must name the new keys.

## Architectural definition

* **Patterns to reuse**
  * [`patt.entity.batch-processing`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.entity.batch-processing.md>) — ingress/notify claims process claimed meteorite rows and release; contact persist must not invent a side queue.
  * [`patt.task.daisy-chain`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/patt.task.daisy-chain.md>) — stage → scrape → land / bot-blocked hops stay resume-safe; contact is carried on the row, not re-derived by skipping stage.
* **New patterns proposed**
  * none — meteorite-row electronic-contact field local to ingress; promote later only if reused.
* **Applicable statutes**
  * [`stat.logging.debug`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>) — Style D for returned vs recorded contact when debug is on.
  * [`stat.logging.info`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.md>) — always-on progress stays succinct if any.
  * [`stat.logging.info.entity`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.info.entity.md>) — entity progress id-pipe type/event if land/notify emits info.
  * [`stat.logging.warning`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.warning.md>) — **warn and continue** when contact persist fails after an otherwise good transition.

Active corpus otherwise has no config/agent/seed statutes in force; do not cite retired harvest ids as law.

## Acceptance criteria

1. `TASK_CONFIG["stage_meteorite"].response_schema.jobs.items_schema` includes the config-named electronic-contact field(s) — fail if schema still only has job_title/job_link/company_job_id/jd_text/employer_name.
2. `agent_task` / prompts for `stage_meteorite` instruct metadata-first best electronic contact for resume send — fail if prompts omit metadata or tell Ruth to invent addresses.
3. Given classify `single_jd_no_link` or `multi_jd_inline` with Reply-To/From (or equivalent) in source metadata, Ruth returns that contact and the meteorite row stores it — fail if outcome is text source-ref and metadata had an address but the meteorite row contact field is empty after fan-out.
4. Given a link outcome that transitions to **BOT_BLOCKED**, the meteorite row still has stage-captured contact when metadata had one — fail if BOT_BLOCKED row contact is empty while stage returned non-empty contact.
5. Contact is **not** written into job `job_data` by this epic — fail if `save_meteorite_job` / landed job gains a new contact key from this work.
6. When contact persist raises/fails after an otherwise successful classify insert or state transition, the path **warns and continues** (row not failed solely for contact write) — fail if the only error is contact persist and the row is marked failed/ERROR solely for that.
7. When nothing determinable, empty/omit contact and ingress still succeeds — fail if land/classify aborts solely because contact is empty.
8. With `debug=True`, Style D mentions contact returned vs recorded on the meteorite row; with `debug=False`, no new Style D contact lines — fail if debug=False emits them.
9. Recommended / JobDetail UI unchanged — fail if this epic’s diff touches those solely to display contact (AST-1685).

## Open questions

none

## Proposed child tickets

#### 1!: **stage_meteorite electronic-contact schema + prompts - Ada**

Owns config response-key / column literals and `agent_task` prompts: metadata-first best electronic contact for resume send on text outcomes and for link rows that may bot-block. Does **not** own DB column wiring or row map persist (after #1 → #2).

**Citations:** `patt.task.daisy-chain`; `stat.logging.debug`, `stat.logging.info`.

**Scope:** `src/utils/config.py` — **modified** — `stage_meteorite` response schema gains electronic-contact field(s); METEORITE_CONFIG / STAGE_METEORITE_CONFIG gains the meteorite-column / response-key literal(s); text outcomes stay the closed `text_source_ref_outcomes` set (include `multi_jd_inline`). `data/admin/agent_task.json` — **modified** — `stage_meteorite` prompts: best electronic contact to send the resume; **must use metadata**; empty when undeterminable; lockstep with TASK_CONFIG. `config.py` — Add optional electronic-contact field(s) on `TASK_CONFIG["stage_meteorite"].response_schema.jobs.items_schema`; add config key literal(s) for the meteorite column / response key; keep outcome enum unchanged; ensure prompts/docs name `single_jd_no_link` and `multi_jd_inline`. `agent_task.json` — Teach metadata-first electronic contact for resume send; forbid invention.

**Estimate: 3**

#### 2: **Meteorite-row contact column + map/persist soft-fail - Hedy**

After #1: database column + allowlist; map Ruth contact into `insert_meteorite_rows` / updates through text fan-out and BOT_BLOCKED; warn-and-continue on persist failure; Style D when debug. Does **not** own job_data or Recommended UI.

**Citations:** `patt.entity.batch-processing`, `patt.task.daisy-chain`; `stat.logging.debug`, `stat.logging.info`, `stat.logging.info.entity`, `stat.logging.warning`.

**Scope:** `src/data/database.py` — **modified** — meteorite schema + insert/update allowlist for the new contact field (header inventory / ensure path as plan chooses). `src/core/meteorite.py` — **modified** — classify→row map and BOT_BLOCKED / land paths carry contact onto the meteorite row; soft-fail warn on persist miss; Style D when debug. `src/core/consult.py` — **modified** only if stage invoke mapping must forward the new response key(s); otherwise untouched. `src/core/agent.py` — **modified** only if schema validation needs a one-line wire; otherwise untouched. `database.py` — New meteorite column + `_UPDATE_METEORITE_ALLOWED` / insert path so contact can be written at NEW fan-out and updated later. `meteorite.py` — Map Ruth contact into row dicts for text and link fan-out; preserve contact into BOT_BLOCKED; on persist failure log warning and continue; Style D when debug. `consult.py` / `agent.py` — Only if stage invoke or validator must name the new keys.

**Estimate: 5**

**Monolith check:** Functional scope has 6 capabilities; 2 children — catalog/prompt vs DB+map persist; UI deferred to AST-1685.

**Scope partition check:** config + agent_task → child 1; database + meteorite + optional consult/agent → child 2; no double-claim; tracker/job out of scope.

---

## Original brief

When the meteorite is a single jd with no link, we must ask the ai agent to provide the email address or other contact information determinable by the meteorite metadata and context.

### Comments

#### chuckles — 2026-09-16T23:08:19.697Z
AST-1689 REVIEW — merge-child blocked; recalling @Betty White for duplicate merge-tests(AST-1689) count=3.

#### hedy — 2026-09-16T22:47:35.495Z
Stage 1 unblocked: re-synced with origin/ftr/AST-1684-reply-to-emails-in-meteorite-when-single-jd-no-link (registry parent_ftr; short --ftr AST-1684 missed the slug). Proceeding with build-child.

#### hedy — 2026-09-16T22:47:14.332Z
🛑 Stage 1 blocked: AST-1688 electronic_contact config literals missing after sync

Step: Stage 1 preflight — assert METEORITE_CONFIG["electronic_contact_column"] and STAGE_METEORITE_CONFIG["electronic_contact_response_key"] after sync-child.sh

Issue: sync-child exited ok but origin/ftr/AST-1684 is not on origin yet (parent not published). HEAD after merge origin/dev has neither key (KeyError). Literals live only on origin/sub/AST-1684/AST-1688-stage-meteorite-electronic-contact-schema-prompts. Plan forbids hardcoding parallel strings in AST-1689.

Proposed resolutions:
1. Chuckles merge-child AST-1688 → publish origin/ftr/AST-1684-…, then re-spawn build-child AST-1689 (sync-child will attach ftr).
2. Temporarily publish parent ftr tip that includes AST-1688 so sync-child can merge it.
3. Need guidance if another integration path is preferred (do not self-cherry-pick AST-1688 onto this sub).

#### chuckles — 2026-09-16T21:42:42.249Z
@susan

1. **Linear project** — AST-1684 has no project set; confirm **Astral Meteorite** (extract+persist) vs something else? (UI sibling AST-1685 is Astral Interface.)
2. **Contact vocabulary** — Reply-to email only, or also phone / LinkedIn / freeform “other contact” string? Preferred `job_data` key name(s)?
3. **Outcome scope** — Strictly `single_jd_no_link` only, or all `text_source_ref_outcomes` (`single_jd_no_link` + `multi_jd_inline`)?
4. **Header vs body** — May Ruth use email Reply-To / From when present in metadata, or only addresses visible in JD body / pasted context? (Bind historically ignored Reply-To for candidate binding — this is a different use.)
5. **Overlap with `company_stem`** — Keep reply-contact as a separate job field even when stem is already an email, or allow stem-only when they match?
6. **Soft-fail** — If contact persist fails after a successful land write of JD text, warn-and-continue or fail the land row?

---

_Implementation detail may live in git history on `origin/dev`._
