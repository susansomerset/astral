# AST-2069 — Upshot states, task registration, and agent_task rows

- **Ticket:** [AST-2069](https://linear.app/astralcareermatch/issue/AST-2069)
- **Parent:** [AST-2054 — Company Upshot - new task](https://linear.app/astralcareermatch/issue/AST-2054)
- **Publish ref:** `sub/AST-2054/AST-2069-upshot-states-registration` (origin only)
- **Canon Scope:** `patt.entity.batch-criteria`, `patt.task.dispatch-retry`, `stat.dispatch.entity-state-bound`

This ticket registers everything the two new company hops need, with no runtime behavior.
It adds the `GET_UPSHOT` / `UPSHOT_READY` / `ERROR_UPSHOT` company states, reroutes every
transition and configured pass state that used to land in `WATCH` so it lands in `GET_UPSHOT`,
and registers two dispatch task keys: the telescope culture-page fetch at `GET_UPSHOT` and
Estelle's `company_upshot` at `UPSHOT_READY`. It also adds the `company_upshot` storage key and
seeds both `agent_task` rows. The hop code itself (gazer batch, roster batch, consult routing,
and the switch from hardcoded `"WATCH"` writes in `roster.py`) is
[AST-2070](https://linear.app/astralcareermatch/issue/AST-2070). Display is
[AST-2071](https://linear.app/astralcareermatch/issue/AST-2071).

⚠️ **Decision (fetch task key name):** the ticket never names the `GET_UPSHOT` fetch task key.
This plan names it **`fetch_company_culture_pages`**. It's the company-entity twin of the
job-side `fetch_culture_pages` and follows the `fetch_<thing>` convention of `fetch_website` /
`fetch_job_pages`. That one string is used as the dispatch task key, the `GAZER_CONFIG` key, and
the `agent_task.task_key` / `task_name`. AST-2070 consumes it from config.

⚠️ **Decision (interim WATCH gap):** once this ticket lands alone, parse/locate success config
says `GET_UPSHOT`, but `roster.py` still hardcodes `"WATCH"` until AST-2070 lands. That's
expected. Both ship together on `ftr/AST-2054-company-upshot`, and nothing reaches `dev` until
`prep-uat`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `TASK_CONFIG["company_upshot"]`; `COMPANY_STATES` adds `GET_UPSHOT`, `UPSHOT_READY`, `ERROR_UPSHOT`; `ROSTER_CONFIG` pass states → `GET_UPSHOT`, new `company_upshot` block, new `company_data_keys["company_upshot"]`; `GAZER_CONFIG["fetch_company_culture_pages"]`; dispatch registration (`_DISPATCH_BATCH_CALL_MODE_ONE`, `_DISPATCH_COMPANY_ENTITY_TASK_KEYS`, `_dispatch_trigger_state_for_task_key`); `company_state_transitions` reroute + new pairs | utils |
| `data/admin/agent_task.json` | Two appended rows: `fetch_company_culture_pages` (telescope) and `company_upshot` (Estelle) | data (seed) |

No other files. No tests, no bible (`tests/` and `docs/test-bible/**` are Betty's).

## Stage 1: Company states, transitions, and roster/gazer config

**Done when:** `python3 -c "from src.utils.config import COMPANY_STATES as S;print('GET_UPSHOT' in S,'UPSHOT_READY' in S)"`
prints `True True`, the transitions check in step 9 prints `OK`, and
`ROSTER_CONFIG["parse_job_list"]["pass_state"] == "GET_UPSHOT"`.

All edits are in `src/utils/config.py`.

1. **`COMPANY_STATES`**: insert these two entries immediately **before** the existing
   `"WATCH": {...}` line (currently right after `"TO_WATCH"`):

   ```python
       # AST-2054: upshot hops between locate/parse success and WATCH.
       "GET_UPSHOT": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
       "UPSHOT_READY": {
           "batch_criteria": {"limit": 10, "sort_by": "updated_at"},
           "retry_state": retry_of("UPSHOT_READY"),
       },
   ```

   Then add this line immediately **after** the existing `"ERROR_GAZE": {},` (last entry):

   ```python
       "ERROR_UPSHOT": {},
   ```

   ⚠️ **Decision:** `limit: 10` / `sort_by: "updated_at"` match the sibling company hop
   states (`PREFILTER_PASSED`, `JOBLIST_IDENTIFIED`, `HOMEPAGE_READY`). These are admin
   defaults only. Per `patt.entity.batch-criteria`, the live claim shape comes from the
   `dispatch_task` row. `retry_of(...)` is already defined above `COMPANY_STATES`, because
   `HOMEPAGE_READY` uses it.

2. **`ROSTER_CONFIG["locate_job_page"]`**: change `"pass_states": ["WATCH"],` to
   `"pass_states": ["GET_UPSHOT"],`.

3. **`ROSTER_CONFIG["parse_job_list"]`**: change `"pass_state": "WATCH",` to
   `"pass_state": "GET_UPSHOT",`.

4. **`ROSTER_CONFIG`**: insert a new block immediately **after** the `"parse_job_list": {...},`
   block and **before** `"scrape_readiness"`:

   ```python
       # AST-2054: Estelle company upshot hop. Retry once via UPSHOT_READY_RETRY, then ERROR_UPSHOT.
       "company_upshot": {
           "task_key": "company_upshot",
           "dispatch_trigger_state": "UPSHOT_READY",
           "pass_state": "WATCH",
           "retry_state": retry_of("UPSHOT_READY"),
           "error_state": "ERROR_UPSHOT",
       },
   ```

5. **`ROSTER_CONFIG["company_data_keys"]`**: add as the **last** entry (after
   `"selected_pjl_url": "selected_pjl_url",`):

   ```python
           # AST-2054: Estelle prose upshot (display-only). No coat-check handler — explicit storage only.
           "company_upshot": "company_upshot",
   ```

6. **`GAZER_CONFIG`**: insert immediately **after** the `"fetch_job_pages": {...},` block and
   **before** the `# Same string as ROSTER_CONFIG["gaze"]...` comment:

   ```python
       # AST-2054: company culture-page fetch before the Estelle upshot. Always advances to pass_state.
       "fetch_company_culture_pages": {
           "fallback_batch_size": 10,   # config default only; dispatch_task.batch_size wins
           "trigger_state": "GET_UPSHOT",
           "pass_state": "UPSHOT_READY",
       },
   ```

   ⚠️ **Decision:** `trigger_state` is included (precedent: `fetch_relative_jd`) so
   `_dispatch_trigger_state_for_task_key` reads it from config in Stage 2 instead of a literal.
   No `fail_state`: per parent Functional scope #2, this hop never fails a company out.

7. **`company_state_transitions`** (in `ASTRAL_CONFIG`): replace these five existing tuples **in
   place**, keeping their position in the list:

   | Existing line | Becomes |
   |---|---|
   | `("TO_WATCH", "WATCH"),` | `("TO_WATCH", "GET_UPSHOT"),` |
   | `("JOBS_FOUND", "WATCH"),` | `("JOBS_FOUND", "GET_UPSHOT"),` |
   | `("PREFILTER_PASSED", "WATCH"),` | `("PREFILTER_PASSED", "GET_UPSHOT"),` |
   | `("JOBLIST_IDENTIFIED", "WATCH"),` | `("JOBLIST_IDENTIFIED", "GET_UPSHOT"),` |
   | `(retry_of("JOBLIST_IDENTIFIED"), "WATCH"),` | `(retry_of("JOBLIST_IDENTIFIED"), "GET_UPSHOT"),` |

8. **`company_state_transitions`**: append these lines at the **end** of the list (after
   `(retry_of("JOBLIST_IDENTIFIED"), "COULD_NOT_PARSE_JOBLIST"),`, before the closing `],`):

   ```python
           # AST-2054: upshot hops. WATCH → GET_UPSHOT is Susan's manual re-run via company state controls.
           ("WATCH", "GET_UPSHOT"),
           ("GET_UPSHOT", "UPSHOT_READY"),
           ("UPSHOT_READY", "WATCH"),
           ("UPSHOT_READY", retry_of("UPSHOT_READY")),
           ("UPSHOT_READY", "ERROR_UPSHOT"),
           (retry_of("UPSHOT_READY"), "WATCH"),
           (retry_of("UPSHOT_READY"), "ERROR_UPSHOT"),
   ```

   ⚠️ **Decision:** `("UPSHOT_READY", "ERROR_UPSHOT")` is declared because
   `patt.task.dispatch-retry` § When this doesn't apply sends a pre-provider empty-token
   failure **straight** to the configured `error_state`, skipping the retry companion.

9. **Verify Stage 1** (from the repo root):

   ```bash
   python3 -m py_compile src/utils/config.py
   python3 -c "from src.utils.config import COMPANY_STATES as S;print('GET_UPSHOT' in S,'UPSHOT_READY' in S)"
   python3 -c "
   from src.utils.config import ASTRAL_CONFIG as C, ROSTER_CONFIG as R, retry_of
   t=C['company_state_transitions']
   bad=[p for p in t if p[1]=='WATCH' and p[0] not in ('UPSHOT_READY',retry_of('UPSHOT_READY'))]
   need=[('WATCH','GET_UPSHOT'),('GET_UPSHOT','UPSHOT_READY'),('UPSHOT_READY','WATCH')]
   assert not bad, bad; assert all(p in t for p in need)
   assert R['parse_job_list']['pass_state']=='GET_UPSHOT' and R['locate_job_page']['pass_states']==['GET_UPSHOT']
   print('OK')"
   ```

   Expected output: `True True`, then `OK`. If the transitions list isn't at
   `ASTRAL_CONFIG['company_state_transitions']`, **stop and comment**. Don't hunt for another
   import path.

**Commit:** `code(AST-2069): upshot company states, transitions, roster/gazer config`

## Stage 2: TASK_CONFIG entry and dispatch registration

**Done when:** for both new keys, `_dispatch_entity_type_for_task_key` returns `company`,
`_dispatch_trigger_state_for_task_key` returns `GET_UPSHOT` / `UPSHOT_READY`, and
`dispatch_task_admin_defaults` returns without a `KeyError`.

All edits are in `src/utils/config.py`.

1. **`TASK_CONFIG`**: insert immediately **after** the `"prefilter_company": {...},` entry
   (it ends with `"trigger_state": None,` / `},`) and **before** `"select_job_page": {`:

   ```python
       # AST-2054: Estelle company upshot — one call per batch; saved to company_data.company_upshot.
       # Routing lives in ROSTER_CONFIG["company_upshot"] (defined below TASK_CONFIG, so literals here).
       "company_upshot": {
           "response_format": "json",
           "response_schema": {
               "companies": {
                   "type": "list", "required": True,
                   "items_schema": {
                       "company_id": {"type": "str", "required": True},
                       "upshot": {"type": "str", "required": True},
                   },
               },
           },
           "context_format": "company_upshot_{index}",
           "entity_type": "company",
           "requires_candidate_key": True,
           "trigger_state": "UPSHOT_READY",
           "pass_state": "WATCH",
           "error_state": "ERROR_UPSHOT",
       },
   ```

   ⚠️ **Decision:** no `scored` flag. Nothing grades the upshot, so it must stay out of
   `_TRANSITION_STATES_USED_BY_SCORED_TASKS` and the score-floor claim. `error_state` is the
   **terminal** `ERROR_UPSHOT`. Per `patt.task.dispatch-retry` Arc 4, AST-2070's router checks
   whether the current state already ends in `_RETRY` before choosing
   `retry_of("UPSHOT_READY")` or this error state.

2. **`_DISPATCH_BATCH_CALL_MODE_ONE`**: add `"company_upshot"` to the frozenset. Append it to the
   last line, so it becomes:
   `"meteorite_like", "vet_inflow_discovery", "parse_job_list", "company_upshot",`

3. **`_DISPATCH_COMPANY_ENTITY_TASK_KEYS`**: add both keys. The last line becomes:
   `"resolve_website", "fetch_company_culture_pages", "company_upshot",`

4. **`_dispatch_trigger_state_for_task_key`**: insert these two branches immediately **after**
   the existing `select_job_page` branch (the line
   `return ROSTER_CONFIG["select_job_page"]["dispatch_trigger_state"]`):

   ```python
       if task_key == "company_upshot":
           return ROSTER_CONFIG["company_upshot"]["dispatch_trigger_state"]
       if task_key == "fetch_company_culture_pages":
           return GAZER_CONFIG["fetch_company_culture_pages"]["trigger_state"]
   ```

5. **Verify Stage 2:**

   ```bash
   python3 -m py_compile src/utils/config.py
   python3 -c "
   from src.utils.config import _dispatch_entity_type_for_task_key as E, _dispatch_trigger_state_for_task_key as T, dispatch_task_admin_defaults as D
   for k,ts in (('fetch_company_culture_pages','GET_UPSHOT'),('company_upshot','UPSHOT_READY')):
       assert E(k)=='company' and T(k)==ts, (k,E(k),T(k))
       d=D(k); print(k, d)
   assert D('company_upshot')['batch_call_mode']==1 and D('fetch_company_culture_pages')['batch_call_mode']==0
   print('OK')"
   ```

   Expected: two lines with `entity_type: 'company'`, `sort_by: 'updated_at'`, the matching
   trigger state, then `OK`.

6. **Lint:** `ruff check src/utils/config.py --statistics`. The `origin/dev` baseline is
   **94** findings. Pass = **≤ 94** and no finding on a line this ticket added
   (`ruff check src/utils/config.py --output-format concise`, then compare against
   `git diff -U0 origin/dev -- src/utils/config.py`). Don't fix pre-existing findings.

**Commit:** `code(AST-2069): company_upshot TASK_CONFIG and dispatch registration`

## Stage 3: agent_task rows

**Done when:** `data/admin/agent_task.json` has a `company_upshot` row with `agent_id`
`principal_recruiter_estelle` whose prompt contains `200 words`, and a `telescope` row for
`fetch_company_culture_pages`. `git diff` on the file shows only added lines.

1. Append the two rows **at the end** of the top-level JSON list, in this order. Do it with
   Python so formatting is preserved. The file round-trips byte-identically through
   `json.dumps(d, indent=2, ensure_ascii=False) + "\n"` (verified at plan time):

   ```python
   import json
   p = "data/admin/agent_task.json"
   d = json.load(open(p, encoding="utf-8"))
   assert not {r["task_key"] for r in d} & {"fetch_company_culture_pages", "company_upshot"}
   d.append(FETCH_ROW); d.append(UPSHOT_ROW)
   open(p, "w", encoding="utf-8").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
   ```

   Run it as a one-off command, not a committed script. Use the literal dicts below, keys in
   this alphabetical order, matching every existing row:

   **`FETCH_ROW`** (shape mirrors the `fetch_job_pages` row):

   ```json
   {
     "agent_id": "telescope",
     "cache_prompt": "",
     "cache_prompt_b": "",
     "cache_prompt_c": "",
     "cache_prompt_d": "",
     "current": 1,
     "nocache_prompt": "",
     "run_next": "",
     "system_prompt": "",
     "task_group_name": "Company Roster",
     "task_group_order": "3000",
     "task_key": "fetch_company_culture_pages",
     "task_key_uuid": "6d5e353f-e86c-4f53-aafa-44f0d1726fa5",
     "task_name": "fetch_company_culture_pages",
     "task_seq": 10,
     "updated_at": "2026-10-08 23:00:00",
     "user_prompt": ""
   }
   ```

   **`UPSHOT_ROW`**: same 17 keys. Values:

   | Key | Value |
   |---|---|
   | `agent_id` | `"principal_recruiter_estelle"` |
   | `cache_prompt` | the **cache_prompt text** below |
   | `cache_prompt_b` | `"## {$FIRST_NAME}'s Bio Summary\n{$BIO_SUMMARY}"` (identical to `prefilter_company`'s `cache_prompt_b`) |
   | `cache_prompt_c`, `cache_prompt_d`, `nocache_prompt`, `run_next`, `system_prompt` | `""` |
   | `current` | `1` |
   | `task_group_name` | `"Company Roster"` |
   | `task_group_order` | `"3000"` |
   | `task_key`, `task_name` | `"company_upshot"` |
   | `task_key_uuid` | `"d29d7af9-c238-4385-b01a-7b1f297b10da"` |
   | `task_seq` | `11` |
   | `updated_at` | `"2026-10-08 23:00:00"` |
   | `user_prompt` | `"Hi, Estelle!\n\nHere are some companies {$FIRST_NAME} is about to start watching. Please write an upshot for each one, following the instructions provided.\n\nThanks much!\n"` |

   ⚠️ **Decision:** `task_seq` 10 and 11 follow the current Company Roster maximum (9,
   `recheck_no_openings`). Existing rows aren't renumbered. The UUIDs were minted at plan time
   so the seed is deterministic. Don't regenerate them.

   **cache_prompt text** (exact; `\n` = newline):

   ```text
   ## AGENT MESSAGE

   {$SELECTED_AGENT}

   ## INSTRUCTIONS

   You're writing a short **company upshot** for {$FIRST_NAME} for each company below. {$FIRST_NAME} is about to start watching these companies for job openings, and will read your upshot when reviewing their watch list.

   Each company has its own block, labeled by index (`000`, `001`, …). A block gives you the company's `company_id`, the text from its homepage, text from its culture pages when we have them, and Grace's prefilter grades with her reasons. Culture pages are sometimes missing. Work from what you have.

   For each company, write one prose upshot that covers:

   - what the company is and what it does, in plain terms
   - why it's worth keeping an eye on for {$FIRST_NAME}, given the bio summary provided

   Rules:

   1. Keep every upshot **under 200 words**.
   2. Write prose in your own voice, addressed to {$FIRST_NAME}. Don't paste grades, vector codes or rubric tables. Grace's grades and reasons are input, not output.
   3. Don't decide whether {$FIRST_NAME} should watch the company. That's already decided, and every company gets an upshot.
   4. Stick to what the content supports. If the content is thin, say less rather than guess.
   5. Return exactly one entry per input company, using the `company_id` from its block unchanged. Don't add, skip or invent companies.

   KEEP IT CONCISE and use line breaks for readability. Let your points breathe rather than delivering a wall of text.

   ## PAYLOAD

   Your `agent_payload` is one JSON object with this shape:

   {"companies": [{"company_id": "<company_id from the block>", "upshot": "<prose upshot, under 200 words>"}]}

   We appreciate you!

   -The Astral Team
   ```

   The stored value is that text exactly, lines joined with `\n`, no trailing newline. The
   fenced block's first line `## AGENT MESSAGE` is the first character of the value.

2. **Verify Stage 3:**

   ```bash
   python3 -c "
   import json; d={r['task_key']:r for r in json.load(open('data/admin/agent_task.json'))}
   u=d['company_upshot']; f=d['fetch_company_culture_pages']
   assert u['agent_id']=='principal_recruiter_estelle' and '200 words' in u['cache_prompt']
   assert all(t in u['cache_prompt']+u['cache_prompt_b'] for t in ('{\$SELECTED_AGENT}','{\$FIRST_NAME}','{\$BIO_SUMMARY}'))
   assert f['agent_id']=='telescope' and f['task_group_name']=='Company Roster'
   assert len(u)==len(f)==17
   print('OK')"
   git diff --stat origin/dev -- data/admin/agent_task.json
   git diff origin/dev -- data/admin/agent_task.json | grep '^-[^-]' && echo 'UNEXPECTED REMOVALS' || echo 'additions only'
   ```

   Expected: `OK`, then `additions only`. If anything other than added lines shows up,
   **stop and comment**.

**Commit:** `code(AST-2069): agent_task rows for company culture fetch and company_upshot`

## Acceptance criteria → stage map

| Ticket AC | Verified in |
|---|---|
| 1. States registered | Stage 1 step 9 |
| 2. Transitions declare the new path | Stage 1 step 9 |
| 3. Task rows exist | Stage 3 step 2 |
| 4. Dispatch-registrable | Stage 2 step 5 |

## Out of scope (do not touch)

- `src/core/roster.py` hardcoded `state="WATCH"` writes, `src/core/gazer.py`, `src/core/consult.py`: AST-2070.
- `src/ui/**`: AST-2071.
- `dispatch_task` DB rows: Susan/admin creates the live schedule rows. No seed or migration here.
- Renaming or deleting any existing state, task key, or `agent_task` row.

## Estimate

Confirm Chuckles estimate: 3 — revise to 2 because it's config-only registration across known registries plus one authored prompt, with no runtime code or schema change.

## Joan validate

[plan-rubric]
**Ticket:** AST-2069
**Overall:** APPROVED
**Corpus:** 2d1b73da19cf1d14276e5c26f52b37aa8047d159
**Publish ref:** `origin/sub/AST-2054/AST-2069-upshot-states-registration` @ `812c7e6cd3d632d1b3c66a7e9d44ad02249630e8`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-criteria | A | | |
| patt.task.dispatch-retry | A | | |
| stat.dispatch.entity-state-bound | A | | |

## Traceability

AC 1–2 → Stage 1; AC 4 → Stage 2; AC 3 → Stage 3. Parent AC 5–8 / 11–14 N/A (runtime hops, grades, API/UI — AST-2070/2071). Parent AC 9–10 align with child AC 3–4.

## Findings

**acceptable** — `fetch_company_culture_pages` is a documented plan decision (parent never named the GET_UPSHOT fetch key); mirrors `fetch_job_pages` / `fetch_relative_jd` registration and is called out for AST-2070 consumption.

**acceptable** — Interim mismatch: `ROSTER_CONFIG` pass states → `GET_UPSHOT` while `roster.py` still hardcodes `"WATCH"` until AST-2070. Plan bounds this to epic `ftr` rollup before `dev`; consistent with registration-only scope.

**discuss** — Live `dispatch_task` rows are explicitly out of scope (Susan/admin). Config + `agent_task.json` seed satisfy AC 4 at import time; ops must still create schedule rows before ticks claim the new hops — same class of gap as other roster registrations, worth a single prep-uat reminder, not a plan defect.

**acceptable** — Stage 1 transition check matches current `origin/dev` surface: exactly five `(X,"WATCH")` tuples to reroute; appended upshot path + `ERROR_UPSHOT` terminal state follow `ERROR_GAZE` / `retry_of` precedents.

**Definition fidelity (R6):** Two files only; no runtime/core/UI creep. TASK_CONFIG `company_upshot` omits `scored` (per plan) so score-floor claim paths stay untouched. GAZER hop has no `fail_state` (parent Functional #2). Self-assessment / estimate note is reasonable; Linear already shows estimate 2.

context_tokens≈38000

## Review

- **Branch:** `sub/AST-2054/AST-2069-upshot-states-registration`
- **Stage 1:** `8a8ec1ccc` — `GET_UPSHOT` / `UPSHOT_READY` / `ERROR_UPSHOT` states; five `(X, "WATCH")` transitions rerouted to `GET_UPSHOT` plus the upshot pairs; locate/parse pass states → `GET_UPSHOT`; `ROSTER_CONFIG["company_upshot"]`, `company_data_keys["company_upshot"]`, `GAZER_CONFIG["fetch_company_culture_pages"]`
- **Stage 2:** `fc5fa9549` — `TASK_CONFIG["company_upshot"]`; both keys in `_DISPATCH_COMPANY_ENTITY_TASK_KEYS`, `company_upshot` in `_DISPATCH_BATCH_CALL_MODE_ONE`, trigger branches in `_dispatch_trigger_state_for_task_key`
- **Stage 3:** `4f9942662` — `agent_task.json` rows `fetch_company_culture_pages` (telescope, seq 10) and `company_upshot` (Estelle, seq 11); additions only
- **Build notes:**
  - All plan verify commands pass (ticket AC 1–4).
  - `ruff check src/utils/config.py`: 94 findings, identical by code+message to `origin/dev` — none new.
  - `origin/dev` picked up Susan's `agent_task.json` content update (`048d297b5`) before build; round-trip, key set and Company Roster `task_seq` re-verified unchanged.
  - Live `dispatch_task` schedule rows for the two keys still need creating (Joan's discuss note) — out of scope here.
  - No tests touched; coverage is Betty's `qa-child`.

## Radia review

[code-rubric]

**Ticket:** AST-2069  
**Publish ref:** `d1d08657a42e3a4baea4b6a258458640af342880` (`origin/sub/AST-2054/AST-2069-upshot-states-registration`)  
**Corpus:** `2d1b73da19cf1d14276e5c26f52b37aa8047d159`  
**Overall:** CLEAN  

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.entity.batch-criteria | A | | |
| patt.task.dispatch-retry | A | | |
| stat.dispatch.entity-state-bound | A | | |

## Column diff vs plan stage

(aligned) — Joan: all three **A**; same here.

## Frame diff

- [ ] **Boundaries / prep-uat:** Live `dispatch_task` schedule rows for `fetch_company_culture_pages` and `company_upshot` exist (or are created in the same epic UT window) — seed `agent_task.json` + `config.py` registration alone does not schedule ticks.

## Findings

**fix-now** — (none)

**discuss**

- **Cross-ticket publish ref (@susan):** Three-dot diff vs `origin/dev` includes **AST-2071 display product** (`src/ui/api/api_companies.py`, `JobAnalysisReportModal.tsx`, `CompanyDetailModal.tsx`) and the AST-2071 plan/review doc, after `sync(publish-ref): origin/sub/AST-2054/AST-2071-upshot-display` and `sync(ftr): origin/ftr/AST-2054-company-upshot`. AST-2069 plan §Out of scope explicitly excludes `src/ui/**` (AST-2071). **Question:** Is an integrated sub/ftr tip the intended review surface for child **2069**, or should Radia/merge-child treat **2069-owned** deltas (`config.py`, `agent_task.json`) as the ticket boundary? **Default:** Proceed on the integrated tip for epic rollup; keep per-child Linear/docs traceability on each sub ref; do not peel 2071 off 2069 mid-pipeline unless Susan wants isolated child reviews.

- **Ops / dispatch_task (@susan):** Joan noted live `dispatch_task` rows remain admin-created (out of scope here). AC4 is satisfied at config import/registry level; ticks will not claim the new hops until schedule rows exist. **Default:** Create or verify both rows during prep-uat / before Susan UT on the epic host — same class as other roster registrations.

**advisory**

- **sibling doc carry:** `docs/features/roster/ast-2071-show-the-company-upshot-in-the-report-and-company-detail.md` (Radia-clean artifact) appears in this three-dot diff — expected from ftr/2071 sync, not 2069 plan scope.
- **sibling test carry (expected):** Betty `merge-tests` + pass-state mock updates in `test_roster.py` / `test_config.py` align config `GET_UPSHOT` with existing roster tests; `TestAst2069UpshotRegistration` covers AC1–4 on registration only.
- **Interim runtime gap (plan-bounded):** `ROSTER_CONFIG` pass targets `GET_UPSHOT` while `roster.py` still hardcodes `"WATCH"` until AST-2070 — documented in plan; not a defect on this ticket.

### Plan fidelity (§5.4)

- **Stage 1:** States `GET_UPSHOT` / `UPSHOT_READY` / `ERROR_UPSHOT`; five `(X,"WATCH")` → `(X,"GET_UPSHOT")`; upshot transition pairs including manual `WATCH` → `GET_UPSHOT`; locate/parse pass → `GET_UPSHOT`; `company_upshot` roster block + `company_data_keys`; `GAZER_CONFIG["fetch_company_culture_pages"]` with `trigger_state` / `pass_state`, no `fail_state`.
- **Stage 2:** `TASK_CONFIG["company_upshot"]` (JSON schema, `UPSHOT_READY` → `WATCH`, `ERROR_UPSHOT`); dispatch frozensets + `_dispatch_trigger_state_for_task_key` branches for both keys.
- **Stage 3:** `agent_task.json` — two appended rows only (telescope fetch + Estelle prompt with 200-word cap and template tokens).
- Tests/bible: registration assertions and WATCH→GET_UPSHOT mock alignment match config surface; no `src/core/roster.py` / gazer runtime in diff.

### Estimate footprint (§5.4)

Confirm **2** (revised from 3) — config + seed + authored prompt; footprint fits.

## What's solid

- `test_only_upshot_hop_enters_watch` encodes the intended transition contract (only upshot hop lands in `WATCH`).
- Retry pattern mirrors `HOMEPAGE_READY` / `JOBLIST_IDENTIFIED` (`retry_of("UPSHOT_READY")`, `ERROR_UPSHOT` terminal).
- Fetch task key `fetch_company_culture_pages` is consistently wired across gazer config, dispatch registry, and `agent_task`.

## Recommended actions (downstream — not Radia)

- Chuckles: append artifact, `docs(AST-2069): Radia review — clean`, post slim upshot, **Review Posted** → datt **PROCEED** toward UT when epic gates allow.
- Susan/prep-uat: frame-diff checkbox on live `dispatch_task` rows; confirm integrated-tip policy for sibling 2071 on 2069 ref if she wants isolated child reviews later.
- AST-2070: roster hardcoded `WATCH` writes remain the runtime follow-up (already planned).

context_tokens≈38000
