# AST-469 — Roster locate/parse split: run_next, JOB_LIST_VISIBLE, JOBS_FOUND path

- **Linear (this ticket):** [AST-469](https://linear.app/astralcareermatch/issue/AST-469/roster-locateparse-split-run-next-job-list-visible-jobs-found-path)
- **Feature ref (publish target on origin):** `sub/AST-461/AST-469-roster-locateparse-split-run-next-job-list-visible-jobs-found-path` *(child of **AST-461**; **`ftr/AST-469`** is not used.)*
- **Parent (reference only — orchestration acceptance):** [AST-461](https://linear.app/astralcareermatch/issue/AST-461/split-roster-locate-and-parse-job-list-run-next-job-list-cache)

## Summary

Today **`find_job_page` → `_check_parse_results`** calls **`select_job_page`** (Anthropic) and, on **`JOBLIST_TITLES`**, immediately invokes **`_fetch_parse_job_list`** on culled DOM in the same Python flow. **`parse_job_list` never runs via `run_next`**, and job-list visible text is not persisted nor passed as an explicit **`{$JOB_LIST_VISIBLE}`** token for the parse hop.

This ticket separates **locate/confirm** (through **`select_job_page`**) from **parse** (**`parse_job_list`**), wires **`agent_task.run_next`** from **`select_job_page`** to **`parse_job_list`**, and threads **visible listing text + culled DOM** into the parse hop without reusing **`select_job_page` Live content** as the TASK block. It persists **`job_list_visible`** (`company_data`) only when locate confirms titles (not **`NO_OPENINGS`** / **`JOBLIST_NO_JOBS`**), clears that cache on **`NO_OPENINGS`** outcomes so **`JOBS_FOUND`** reopen paths never ingest stale listings, and implements **`JOBS_FOUND`**: fresh Playwright on **`job_site`**, confirm list page (titles / no-jobs / hard failures), then the same **`run_next` parse path** — no reuse of dormant cached visible text while the row was **`NO_OPENINGS`**.

⚠️ **Decision:** **`do_task`'s `run_next` reuses parent `live_content` for the child hop.** `select_job_page` feeds enumerated PJL text; **`parse_job_list`** needs **culled HTML** as TASK live content plus **`{$JOB_LIST_VISIBLE}`** from **`chain_context`**. Rosters registers **`ctx["resolve_run_next_live"]`** — a **`callable(parsed)`** that returns either **`Tuple[Optional[str], Optional[str]]` = (culled_dom, visible_text)** or **`str` culled_dom only** (legacy-style). **`agent.do_task`** invokes it at **`run_next`**, sets inner **`live_content`** from nonempty culled DOM (else fallback to parent **`live_content`**), merges **`JOB_LIST_VISIBLE`** into **`hop_ctx`** when the second tuple element is a nonempty **`str`.** No **`agent` → `roster`** imports.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add **`JOB_LIST_VISIBLE`** **`TOKEN_SOURCES`** (`source: "chain"`). Set **`COMPANY_STATES["JOBS_FOUND"]["batch_criteria"]`** to mirror **`TO_WATCH`** (**`limit` + `sort_by`**). Extend **`company_data_keys`** with **`job_list_visible`**. Extend **`ROSTER_CONFIG["locate_job_page"]["dispatch_input_states"]`** to **`("TO_WATCH", "JOBS_FOUND")`** (list style consistent with repo). | utils |
| `src/core/agent.py` | **`run_next` branch:** **`resolver = ctx.get("resolve_run_next_live")`**; if **`callable`**, **`raw = resolver(parsed)`**; **`if isinstance(raw, tuple)` and **`len(raw) == 2`**: unwrap DOM + visible; **`elif isinstance(raw, str)`**: DOM only. Nonempty stripped DOM → child **`live_content`**; nonempty visible → **`hop_ctx["JOB_LIST_VISIBLE"]`** after **`_chain_tokens_for_next_hop`**. Absent **`resolver`**: identical to **`origin/dev`**. | core |
| `src/core/roster.py` | Extend **`_fetch_job_links_content`** with **`visible_map`**. **`find_job_page` / `_check_parse_results`:** **`JOBLIST_TITLES`** flows through **`await do_task("select_job_page", ..., ctx={"resolve_run_next_live": resolver})`** (no inline **`_fetch_parse_job_list`**); outer return is **`parse_job_list`** when **`run_next`** is set. Keep validation + **`_save_company` / `save_company_data` / `transition_company_state`** aligned with **`origin/dev`**. Strip **`job_list_visible`** on **`JOBLIST_NO_JOBS`**; persist on title success path. **`JOBS_FOUND`:** new **`run_company_task`** helper — scrape **`job_site`** (fresh Playwright), single-page **`PAGE 1`** assembly, **`resolver` maps `{1}`**; do not inject **`{$JOB_LIST_VISIBLE}`** from DB for this chain. | core |
| `src/data/database.py` | *(Optional bounded scope)* **`UPDATE`-style migration inside existing schema ensure**, same pattern as **`NO_OPENINGS` → `recheck_no_openings`**, to set **`run_next='parse_job_list'`** where **`task_key='select_job_page'`** and **`run_next` blank** — iff Susan approves touching **`agent_task` defaults** (**not forbidden** by this ticket's **dispatch_tasks** boundary). If migration is undesirable, substitute a **blocking comment** tick for Admin **Manage Tasks**: **`select_job_page.run_next`** must **`parse_job_list`** or **`run_next` chain is inert.** | data |
| `tests/component/core/test_agent.py` | Assert tuple **`resolve_run_next_live`** feeds child **`live_content`** + **`{$JOB_LIST_VISIBLE}`** (**mock **`send_to_anthropic`**, stubs per existing **`test_agent`** patterns**). | tests |
| `tests/component/core/test_roster.py` | Update **`find_job_page` / `_check_parse_results`** tests to **`AsyncMock(do_task)`** returning shapes for **chained** parse (outer result is parse hop). Add **`JOBS_FOUND`** **`run_company_task`** path smoke test (**redirect**, **titles → WATCH**, **404 / dead page → existing error states**) — reuse monkeypatch **`create_browser_context`/`get_visible_text`**/`**get_page**`/`**extract_\***`** patterns already in **`test_locate_job_page_paths` / **`recheck`**. Extend **`dispatch_input_states`** expectations if exercised. | tests |

## Stage 1: Token registry + agent `run_next` plumbing — child `live_content` + `JOB_LIST_VISIBLE`

**Done when:** **`{$JOB_LIST_VISIBLE}`** resolves from **`chain_context`**; **`run_next` child hop** gets correct **`live_content`** + visible token when **`resolve_run_next_live`** present; code paths without **`resolver`** match **`origin/dev`**.

1. In **`src/utils/config.py`**, **`TOKEN_SOURCES`**, add **`"JOB_LIST_VISIBLE": {"source": "chain"}`** with **`CALLER_*`** chain entries.

2. In **`src/core/agent.py`**, **`run_next` block (**after parent hop success**, **`parsed_response` validated**) — **`select_job_page` is primary consumer**, pattern is generic:**
   - Build **`hop_ctx = _chain_tokens_for_next_hop(...)`** (existing).
   - **`raw = None`**. If **`ctx`** and **`callable(ctx.get("resolve_run_next_live"))`**: **`raw = ctx["resolve_run_next_live"](parsed_response)`**.
   - If **`isinstance(raw, tuple)` and **`len(raw) == 2`**: **`dom_next, vis_next = raw`**; **`dom_next = (dom_next or "").strip()`**, **`vis_next = (vis_next or "").strip()`**; if **`vis_next`**: **`hop_ctx["JOB_LIST_VISIBLE"] = vis_next`**; **`child_live = dom_next if dom_next else live_content`**.
   - **`Elif isinstance(raw, str)`**: **`child_live = raw.strip() or live_content`** (DOM-only legacy).
   - **`Else`**: **`child_live = live_content`**.
   - **`merged_ctx = _merge_chain_context_for_next_hop(chain_context, hop_ctx)`** then **`await do_task(next_key, live_content=child_live, ..., chain_context=merged_ctx)`** (**other kwargs unchanged**).

⚠️ **Decision:** Tuple form is the **roster default**; string-only return remains for tests or simple chains.

### Self-review (Stage 1 vs ASTRAL_CODE_RULES)

- **§3.3:** Rosters (**core**) feeds **`agent` via **`ctx`**; **`agent`** does not import **`roster`**.
- **§2.1:** New literal token registration only in **`config.py`**.

---

## Stage 2: PJL maps + refactor `find_job_page` locate→parse boundary

**Done when:** **`find_job_page` never invokes **`_fetch_parse_job_list`** on **`JOBLIST_TITLES`**; **`select_job_page` → `parse_job_list`** runs via DB **`run_next`** + **`resolve_run_next_live`** (**tuple DOM + visible**). **`TO_WATCH`** outcomes (**states / `company_data`**) match **`origin/dev`** on equivalent fixtures.

1. **`_fetch_job_links_content`:** return **`Tuple[..., visible_map]`** — **`visible_map[i]`** = stripped visible text **`extract_visible_text`**.

2. **`find_job_page`** + TRY_LINK: unpack/pass **`visible_map`**.

3. **Resolver (**`Callable[[Any], Union[Tuple[Optional[str], Optional[str]], str]]`**)**: **factory** (**e.g.** **`make_locate_parse_resolver(dom_map, visible_map)`**) reads **`parsed["selected_page"]`**, **`job_titles`**, **`dom_full = dom_map.get(sp)`**, outputs **`("\n".join(find_job_containers(dom_full, titles)), visible_map.get(sp, "").strip())`**. Prefer **`def`** over **`lambda`**. Stateless — no **`save_company`** in resolver.

4. **`NO_OPENINGS` / `JOBLIST_NO_JOBS`**: after merges, **`job_list_visible`** explicitly removed (**helper **`_company_data_strip_keys`** or **`pop`** on the merged **`company_data`** dict**).

5. **`JOBLIST_TITLES`**:
   - **`await do_task("select_job_page", ..., ctx={..., "resolve_run_next_live": resolver})`**; fold **`_fetch_select_job_page`** into this path (**avoid double Anthropic`).
   - **`parse_result`** = **`do_task` return (**outer **`parse_job_list`**). On failure → same **`CANNOT_PARSE_JOB_SITE`** / **`error_states`** paths as **`_fetch_parse_job_list`** today.
   - On success → same container/tag/`job_ids` validation, **`transition WATCH`**, **`job_list_visible`** from tuple[1] (must match scrape).

⚠️ **Decision:** Duplicate validation logic **verbatim** — keep **`parse_job_list_notes`** grep-friendly.

### Self-review (Stage 2)

- **§2.4 **`batch_id`**: unchanged — same **`dispatch` batch envelopes **`do_task` chain**.
- **§2.8 coat-check**: add **`company_data_keys["job_list_visible"]`** documenting key only — **handler optional** (**not lazy fetch** requirement); **explicit `NOT_IMPLEMENTED`** comment if **`get_company_data` dispatch** untouched.

---

## Stage 3: `JOBS_FOUND` path + config dispatch union

**Done when:** **`run_company_task(..., input_state="JOBS_FOUND")`** scrapes **`job_site`**, runs **`select_job_page` + `parse_job_list` via **`run_next`**, and lands in the same terminal states as multi-page locate for equivalent AI outcomes (**`WATCH`**, **`NO_OPENINGS`**, **`NO_JOBLIST`**, **`CANNOT_PARSE_JOB_SITE`**, etc. — **map single-page scrape failures explicitly in code comments + tests**).

1. **`COMPANY_STATES["JOBS_FOUND"]`** = **`{"batch_criteria": {"limit": 10, "sort_by": "updated_at"}}`** (**mirrors **`TO_WATCH`**). **`scan_interval_hours` omitted** (**same ambiguity as **`IMPORTED`**/`{}`** — explicit limit/sort parity with **`TO_WATCH`** per dispatcher expectations.**)

2. **`ROSTER_CONFIG["locate_job_page"]["dispatch_input_states"]`** append **`JOBS_FOUND`**.

3. **`run_company_task`**: **`elif input_state=="JOBS_FOUND":`** **`await jobs_found_...`**; treat **`pass_states`/failures **`like locate branch** (**reuse **`pass_states`** list **`["WATCH"]`** from **`locate`** config).

⚠️ **Boundary (#469): Do not edit `dispatch_tasks` seed rows.** Until follow-up **`dispatch`** row (**`JOBS_FOUND`**) exists, **automated AUTO dispatch will not pull **`JOBS_FOUND` companies** — **coverage via direct **`run_company_task`** invocation** or **Susan/UI manual Run** once row added out-of-band.

⚠️ **Decision:** **`NO_OPENINGS` recheck** remains Playwright‑only (**AST-460**) — untouched.

---

## Stage 4: Tests + **`agent_task` `run_next`**

**Done when:** Component tests updated green; **`select_job_page` row **`run_next=parse_job_list`** in dev DB (**migration or documented manual**).

1. Migrate / Admin (`Stage 4` depends on **`Stage 2` completeness** verification).

2. Execute **`pytest tests/component/core/test_agent.py`** / **`tests/component/core/test_roster.py`** affected subsets + full **`test_roster`** if fast.

---

## Self-Assessment

**Scope:** `Single-Component` — touches **`agent`** **`run_next`**, **`roster`** discovery/parse orchestration, and **`config`** tokens/states (**no UI** HTML beyond incidental).

**Conf:** `Medium` — tuple **`resolver`** + **`JOBS_FOUND`** single-page branching must mirror multi-page **`_check_parse_results`**, but patterns (**`find_job_containers`, validation**) already exist.

**Risk:** `Medium` — regressions strand companies in **`WATCH`/bad parse`; mitigated by lifting validation verbatim and extending tests.

---

## Self-review vs ASTRAL_CODE_RULES (whole plan)

| Rule | Conflict? |
|------|-----------|
| **§1.3 DRY** | Resolver closures share one **`_build_culled_dom(parsed, dom_map)`** helper in **`roster.py`** — mandated. |
| **§2.1 config** | States, tokens, dispatch_input_states in **`config.py`**. |
| **§2.4 batch processing** | No row lock semantics change inside **`dispatcher`**. |
| **§2.6 state machine** | Rosters **`transition_company_state`** only (**no data-layer decision drift**). |
| **§3.3 imports** | **`agent`↔️`utils`**, **`roster→agent`**. |
| **§3.5 naming** | Snake_case **`job_list_visible`** in DB; TOKEN **`JOB_LIST_VISIBLE` uppercase. |

**Token / chain alignment:** **`get_manage_tasks_chain_tokens`** picks all **`TOKEN_SOURCES`** with **`source=='chain'`** — **`JOB_LIST_VISIBLE`** appears automatically for Manage Tasks pickers (**verify UI filter doesn't exclude arbitrary names — if blocked, grep admin React**).


---

## Execution contract (for the developer agent)

The plan is binding per **`plan-astral`** defaults: **`run_next` **`parse_job_list` must execute before company **`WATCH` transition** — **never skip **`select_job_page` success validations** (**container presence**)**. **Questions **→ **Linear comment on **`AST-461`** parent** per skill template.**

---

## Boundary echo (ticket)

- **`dispatch_tasks`** default rows: **follow-up adds **`JOBS_FOUND` row**.
- **`AST-460`**, **`AST-179`**, **`AST-180`**: **not in scope.**

---

## Review stub (post-build — build-astral §11)

No PR opened from this lane per workflow; architect opens PR at **PR Ready** after **UAT**.

| Item | Value |
|------|-------|
| **Integration branch** | `dev-hedy` |
| **Feat commit (`dev-hedy`)** | `4a43ce98d048e47c87501574f1890c3cfeba7816` |
| **Publish ref** | `origin/sub/AST-461/AST-469-roster-locateparse-split-run-next-job-list-visible-jobs-found-path` |
| **Canonical publish tip** | Recorded with **`resolve-astral`** closing comment on **AST-469** (**parent AST-461**); supersedes one-off **`8cf428a7`** reviewer snapshot rows above. |
| **Notes** | Stub retained for integration-branch context; authoritative SHAs migrate with **`origin/sub/…`** as **`qa-astral`**, **`review-astral`**, and **`resolve-astral`** land. |

## Review

**Diff:** three-dot **`origin/dev...origin/sub/AST-461/AST-469-roster-locateparse-split-run-next-job-list-visible-jobs-found-path`** @ publish tip **`8cf428a7`**.

Radia scanned plan fidelity (parent **AST-461** roster split + **JOBS_FOUND** lane), **`ASTRAL_CODE_RULES`** layering / batch / roster patterns, and the rubric-aligned checks where touched (`run_next`, roster dispatch, swallowed errors / logging).

### What's solid

- **`run_next` gating** for **`select_job_page`** only proceeds on **`JOBLIST_TITLES`**; **`resolve_run_next_live`** supplies **`JOB_LIST_VISIBLE`** + culled TASK **`live_content`**, with **empty-dom chain suppression** so **`parse_job_list`** cannot inherit the wrong parent PJL blob.
- **`resolve_run_next_live`** errors **`logger.exception(...)` then fall back — not a silent **`except: pass`** (aligns **D2** visibility expectations).
- Roster refactor keeps **`select_job_page` → `parse_job_list`** on the success path via **`do_task`** chaining; **`run_next_parent_parsed`** preserves **`select`** payload after the parse hop resolves.
- **`job_list_visible`**: persists on **`WATCH`** finalize when **`visible_map`** has rows; **`_strip_company_data_keys`** clears stale cache on **`JOBLIST_NO_JOBS`** and at **`JOBS_FOUND`** scrape entry.
- **`_apply_ast469_select_job_page_run_next_migration`** validates **`run_next`** against the task graph before **UPDATE**.
- Tests + **`ASTRAL_TEST_BIBLE`** § **7.13tb** trace **`JOB_LIST_VISIBLE`**, **`make_locate_parse_resolver`**, and **`JOBS_FOUND`** **`run_company_task`** routing.

### Issues

| Severity | Topic | Detail |
| --- | --- | --- |
| **discuss** | Cross-ticket surface | **`config.py`** adds **AST-468**‑labeled helpers around dispatch trigger ↔ scored-task detection (`dispatch_task_key_is_scored`, `trigger_state_used_by_scored_dispatch_task`, seed mirror). Not described in **AST-469** ticket body or staged plan headings — confirm intentional coupling vs peeling to **`AST-468`** / a small prep commit for traceability. |
| **advisory** | Plan stub hygiene | **`## Review stub`** integration row still references **`dev-hedy`** / an older **`Feat commit`**; update when archiving the lane so historians are not confused. |

### Recommended actions

| Priority | Owner | Action |
| --- | --- | --- |
| P2 | Hedy | If **AST-468** helpers are accidental ride-along here, relocate or annotate in **Linear** so **`resolve-astral`** diffs stay ticket-pure per **§ Boundary echo**. |
| P3 | Hedy | Refresh **`## Review stub`** table (**integration branch**, **feat SHA**) at **Done** — or rely on **`ftr/AST-469`** cherry-picks + **`8cf428a7`** publish tip as authoritative. |

---

## Resolution (resolve-astral)

**Date:** 2026-05-23 (**Review Posted → User Testing** close).

**Integration line before manifest:** **`dev-hedy`** merged **`origin/dev`** (already up to date), then **`origin/sub/AST-461/AST-469-roster-locateparse-split-run-next-job-list-visible-jobs-found-path`** (already up to date). Betty manifest § **7.13tb** slice re-run: **26/26** **`pytest`** pass (`.venv/bin/python3.12`, **`PYTHONPATH=$PWD`**).

| Radia bucket | Outcome |
| --- | --- |
| **Cherry-pick **`10462b8b`** (`origin/ftr/AST-469`)** | Applied on **`dev-hedy`** as **`docs(AST-469): Radia review — …`** (`review-astral §6` handoff). |
| **fix-now** | **0** — no product deltas on this lane. |
| **discuss — AST‑468‑labeled **`config`** helpers (`dispatch_task_key_is_scored`, `trigger_state_used_by_scored_dispatch_task`)** | **Intentionally bundled** on this AST-469 integration line so **`consult`/`gazer`** imports and **`test_config`** / **`test_api_admin`** manifest sanity slices (`qa-astral` **`[qa-handoff]`**) keep passing without a peeled prep ticket. Peel / ticket-purity is optional follow-up (**AST-468** or Susan direction), not blocking **prep-uat**. |
| **advisory — stub hygiene** | **`## Review stub`** table patched with **`Canonical publish tip`** row; reviewer diff snapshot **`8cf428a7`** left in **`## Review`** header for archaeology. Closing SHA lives in Linear **`resolve-astral`** comment. |
