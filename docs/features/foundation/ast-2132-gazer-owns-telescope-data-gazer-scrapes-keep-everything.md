# AST-2132 — Gazer owns telescope_data; gazer scrapes keep everything

**Parent:** [AST-2130 — Create a new table telescope_data](https://linear.app/astralcareermatch/issue/AST-2130)
**Ticket:** [AST-2132](https://linear.app/astralcareermatch/issue/AST-2132)
**Publish ref:** `origin/sub/AST-2130/AST-2132-gazer-telescope-owner`

Makes gazer the owner of `telescope_data` (table + data functions shipped by AST-2131). Gazer gains a small public API — keep one scrape result, two scrape-and-keep wrappers around the Telescope visible-text and link-list calls, a page-scrape keep for roster's page-contract helpers, and a legacy-tolerant resolve helper — and its own writers switch to it: `fetch_website` stores `homepage_text` / `nav_links` as row ids, `fetch_job_pages` keeps every PJL page and stops writing the derived `pjl_assembled_content` / `pjl_nav_links`, `fetch_jd` (and the relative-link JD fetch, which shares its save path) stores the scraped-JD reference instead of JD text, and the culture-cache checks resolve ids. Every scrape that returns text or links is kept, bot walls and failed gates included. Composed-JD readers (AST-2133) and roster writers / readers (AST-2134) consume this API; they are not built here.

## Scope check

This ticket's `## Scope` names one file: `src/core/gazer.py` — new scrape-and-keep functions, new resolve helper, modified `fetch_website_batch` / `fetch_job_pages_batch` (store row ids), modified JD save path in `fetch_jd` (gates on pruned text; store reference), modified culture-cache checks. Every stage below edits only `src/core/gazer.py`. `src/data/database.py`, `src/utils/config.py`, `src/core/roster.py`, `src/core/tracker.py`, `src/external/telescope.py` and `service/telescope/**` are **not** edited.

## Canon

`stat.logging.debug`, `stat.logging.warning`, `stat.logging.error`, `stat.logging.info.entity` (`canon/directives/active/`; `docs/canon-index.md` is absent on this ref). Binding consequences here:

- New gazer functions log `Calling <fn>: [...]` / `Response from <fn>: ...` at `logger.debug` around each data-layer and Telescope call — full payloads, no truncation, no `if debug` gate.
- Missing `telescope_data` rows on resolve: one `logger.warning` naming the ids and the consequence. No new `logger.exception` / `logger.error` — data-layer errors propagate to the callers' existing handlers (data raises, the handler logs once).
- New success lines on the modified writers use the `<entity_id> | <entity_type> <event>: <detail> (batch: <batch_id>)` shape.
- Existing legacy `debug_index` / `debug_detail` calls in touched functions are left as they are (not converted in this ticket).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/gazer.py` | Imports; module docstring; telescope API (`is_telescope_id`, `keep_telescope_data`, `keep_page_scrape`, `scrape_visible_text_and_keep`, `scrape_page_links_and_keep`, `resolve_telescope_value`); `_apply_jd_gates`, `fetch_jd_batch`, `fetch_relative_jd_batch`, `fetch_website_batch`, `fetch_job_pages_batch`, `fetch_culture_pages_batch`, `fetch_company_culture_pages_batch` | core |

## Stage 0: Drift check (no commit)

**Done when:** every item below holds on the synced sub, or the builder has stopped and commented.

1. `src/data/database.py` defines `save_telescope_data(candidate_id, url, data_type, content)` (returns the new uuid string) and `get_telescope_data_for_ids(telescope_data_ids)` (returns `{id: plain content}`, missing ids omitted). (Use the shell — `src/data/` is hidden from Cursor file tools.)
2. `src/utils/config.py` defines `TELESCOPE_DATA_CONFIG["data_types"]` with keys `VISIBLE_TEXT` and `PAGE_LINKS`, and `TRACKER_CONFIG["job_data_keys"]["jd_telescope_data_id"]`.
3. `src/core/gazer.py` still has: `_apply_jd_gates` with the two `save_job_data(aid, {jd_key: text})` calls; `fetch_website_batch` building `data_to_save = {"homepage_text": visible_text}`; `fetch_job_pages_batch` saving `pjl_scrape_pages` / `pjl_assembled_content` / `pjl_nav_links`; `fetch_culture_pages_batch` reading `recorded = cd.get("website_content")`; `fetch_company_culture_pages_batch` reading `found = cd.get("website_content")`.
4. `src/external/telescope.py`: `get_visible_text(url=None, *, context=None, page=None, return_final_url=False)` returns `(text, final_url)` when `return_final_url=True`; `extract_site_page_list(url=None, max_depth=1, debug=False, verify=False, context=None, page=None)` returns a list of URL strings.
5. `src/utils/formatting.py` exports `enumerate_array(label, array, ...)`.
6. Record the ruff baseline: `ruff check src/core/gazer.py | tail -1` → planner measured **67** on both this sub and `origin/dev`.

If any item does not hold, **stop** and post the 🛑 comment on AST-2130. Do not adapt.

## Stage 1: Gazer telescope API

**Done when:** `src/core/gazer.py` compiles; a scratch check against a temp DB shows `keep_telescope_data` returns a uuid and stores one row with the given `candidate_id` / `url` / `data_type`, empty content returns `None` and stores nothing, and `resolve_telescope_value` returns the right shape for a row id, a missing id, a `[{url, id}]` list, a legacy `[{url, content}]` list, legacy text, and `None`.

1. Imports in `src/core/gazer.py`:
   - In the `from src.data.database import (...)` block add `get_telescope_data_for_ids,` and `save_telescope_data,` (keep the block's existing order style).
   - In the `from src.utils.config import (...)` block add `TELESCOPE_DATA_CONFIG,`.
   - In the `from src.external.telescope import (...)` block add `extract_site_page_list,`.
   - In the `from src.utils.formatting import (...)` block add `enumerate_array,`.
2. Module docstring: append to the `In-scope:` list (after `ingest_meteorite_jobs_from_email_html (AST-1061 gazer-reads-email)`) a line:
   `telescope_data owner (AST-2132): keep_telescope_data, keep_page_scrape, scrape_visible_text_and_keep, scrape_page_links_and_keep, resolve_telescope_value — the only core caller of the telescope_data data functions.`
3. Directly after `_log = get_logger(__name__)`, add:
   ```python
   # AST-2132: gazer owns telescope_data. Row ids are uuid4 strings (database.save_telescope_data).
   _TELESCOPE_ID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
   _VISIBLE_TEXT = TELESCOPE_DATA_CONFIG["data_types"]["VISIBLE_TEXT"]
   _PAGE_LINKS = TELESCOPE_DATA_CONFIG["data_types"]["PAGE_LINKS"]
   ```
4. Directly after `is_bot_wall` (before `_classify_jd`), add a `# ---- telescope_data (AST-2132) ----` comment and these functions, in this order:
   ```python
   def is_telescope_id(value: Any) -> bool:
       """True when value is a telescope_data row id (uuid-shaped str), not legacy scraped text."""
       return isinstance(value, str) and bool(_TELESCOPE_ID_RE.match(value))


   def keep_telescope_data(
       candidate_id: Optional[str], url: str, data_type: str, content: str,
   ) -> Optional[str]:
       """Store one scrape result in telescope_data and return its row id; None when content is blank.

       data_type is passed through unchecked (free text by design). Links are stored as the
       enumerated string readers use today, so resolving an id never needs the type.
       DB errors propagate to the caller's existing failure path."""
       if not (content or "").strip():
           return None
       _log.debug(
           "Calling save_telescope_data: [candidate_id=%s url=%s data_type=%s content=%s]",
           candidate_id, url, data_type, content,
       )
       row_id = save_telescope_data(candidate_id, url, data_type, content)
       _log.debug("Response from save_telescope_data: %s", row_id)
       return row_id


   def keep_page_scrape(
       candidate_id: Optional[str], url: str, scrape: Dict[str, Any],
   ) -> Tuple[Optional[str], Optional[str]]:
       """Keep a page-contract scrape (roster scrape_company_homepage_content / _scrape_pjl_page result):
       visible_text as VISIBLE_TEXT, enumerated_nav_links as PAGE_LINKS. Returns (text_id, links_id)."""
       return (
           keep_telescope_data(candidate_id, url, _VISIBLE_TEXT, scrape.get("visible_text") or ""),
           keep_telescope_data(candidate_id, url, _PAGE_LINKS, scrape.get("enumerated_nav_links") or ""),
       )


   async def scrape_visible_text_and_keep(
       candidate_id: Optional[str], url: str, *, context: Any = None,
   ) -> Tuple[str, str, Optional[str]]:
       """Telescope visible text for url, kept in telescope_data. Returns (text, final_url, row_id).
       Scrape errors propagate — callers already route them."""
       _log.debug("Calling get_visible_text: [url=%s]", url)
       text, final_url = await get_visible_text(url=url, context=context, return_final_url=True)
       _log.debug("Response from get_visible_text: final_url=%s text=%s", final_url, text)
       text = text or ""
       return text, final_url or url, keep_telescope_data(candidate_id, url, _VISIBLE_TEXT, text)


   async def scrape_page_links_and_keep(
       candidate_id: Optional[str], url: str, *, context: Any = None,
   ) -> Tuple[List[str], Optional[str]]:
       """Telescope link list for url (depth 1, unverified — roster's nav_links fetch shape), kept in
       telescope_data as the enumerated list. Returns (urls, row_id). Scrape errors propagate."""
       _log.debug("Calling extract_site_page_list: [url=%s]", url)
       urls = await extract_site_page_list(url, max_depth=1, verify=False, context=context) or []
       _log.debug("Response from extract_site_page_list: %s", urls)
       enumerated = enumerate_array("", urls) if urls else ""
       return urls, keep_telescope_data(candidate_id, url, _PAGE_LINKS, enumerated)


   def resolve_telescope_value(value: Any) -> Any:
       """Stored blob value -> content in today's shape; legacy text tolerant.

       Row id -> that row's content (text, or enumerated links), None when the row is gone.
       List -> each {url, id, ...} entry becomes {url, content, ...} (other keys kept); entries
       without a row id (legacy {url, content}) pass through; entries whose row is gone drop;
       an empty result is None so fetch-on-missing callers re-scrape.
       Anything else (legacy text, None, dict) is returned unchanged."""
       if is_telescope_id(value):
           ids = [value]
       elif isinstance(value, list):
           ids = [e["id"] for e in value if isinstance(e, dict) and is_telescope_id(e.get("id"))]
       else:
           return value
       _log.debug("Calling get_telescope_data_for_ids: %s", ids)
       rows = get_telescope_data_for_ids(ids)
       _log.debug("Response from get_telescope_data_for_ids: %s", rows)
       missing = [i for i in ids if i not in rows]
       if missing:
           _log.warning(
               "telescope_data %s missing — resolving without them; fetch-on-missing callers re-scrape",
               missing,
           )
       if isinstance(value, str):
           return rows.get(value)
       out = []
       for e in value:
           if not (isinstance(e, dict) and is_telescope_id(e.get("id"))):
               out.append(e)
           elif e["id"] in rows:
               out.append({**{k: v for k, v in e.items() if k != "id"}, "content": rows[e["id"]]})
       return out or None
   ```
5. `python3 -m py_compile src/core/gazer.py`; ruff count ≤ baseline (see Lint gate).
6. Scratch check (`debug/spikes/AST-2132/stage1.py`, not committed): set `ASTRAL_DB_DIR` to a temp dir, call `ensure_all_upsert_registry_schemas_at_startup()`, then verify the **Done when** cases, including `resolve_telescope_value([{"url": "u1", "id": <id>}, {"url": "u2", "content": "legacy"}, {"url": "u3", "id": <deleted id>}])` → `[{"url": "u1", "content": ...}, {"url": "u2", "content": "legacy"}]` plus one warning.

⚠️ **Decision:** PAGE_LINKS content is the **enumerated string** (`enumerate_array("", urls)`, today's `nav_links` shape), not a JSON list. AST-2131 left serialization to this ticket; enumerated text lets `resolve_telescope_value` stay type-agnostic and keeps reader output byte-identical (parent AC 6). `parse_enumerate_array` recovers the URLs.

⚠️ **Decision:** Blank content (`""` / whitespace) is not kept and returns `None` — the parent's rule is "every scrape that **returns** visible text or a link list". A failed scrape that returned nothing has nothing to keep.

⚠️ **Decision:** `keep_telescope_data` does not catch DB errors. Today a failed `save_company_data` / `save_job_data` propagates to the batch's existing handler; keeping is the same class of write, so it takes the same path (one log, at the handler) instead of a new per-call catch.

⚠️ **Decision:** The row's `url` is the URL the caller asked Telescope for (job link, company website, PJL URL), not a redirect target — except the relative-JD path, where the click-through's resolved `final_url` is the only absolute URL (Stage 2).

⚠️ **Decision:** `keep_page_scrape` keeps the **result** of roster's page-contract helpers instead of gazer re-implementing them. `scrape_company_homepage_content` and `_scrape_pjl_page` carry redirect, infra-error and download-skip rules that must not be duplicated, and they live in `roster.py` (AST-2134's file). `scrape_visible_text_and_keep` / `scrape_page_links_and_keep` wrap the two Telescope calls core uses on their own (`get_visible_text`, `extract_site_page_list`).

## Stage 2: JD save path stores the scraped-JD reference

**Done when:** `fetch_jd_batch` on a stubbed scrape (scratch check) keeps one `VISIBLE_TEXT` row per job with the job's `candidate_id` and `job_link` — on pass, on `closed` / `bot` classification, and on too-short text — and, on pass and classified outcomes, `job_data` gains `jd_telescope_data_id` = that row id while `job_data.job_description` is unchanged; job states are exactly what they were before this change for the same text.

1. `_apply_jd_gates`: add keyword-only parameter `telescope_data_id: Optional[str]` after `classified_states`. Replace the `jd_key = ...` line with
   `ref_key = TRACKER_CONFIG["job_data_keys"]["jd_telescope_data_id"]`.
   - Classified branch: replace the comment and `save_job_data(aid, {jd_key: text})` with
     `# Reference the kept capture so the bad page stays inspectable; job_description (preamble) is untouched`
     `save_job_data(aid, {ref_key: telescope_data_id})`.
   - Pass branch: replace `save_job_data(aid, {jd_key: text})` with `save_job_data(aid, {ref_key: telescope_data_id})`, and the write-back `job["job_data"][jd_key] = text` with `job["job_data"][ref_key] = telescope_data_id` (keep the existing write-back comment).
   - Docstring: replace "Saves the JD and transitions the job." with "Stores the scraped-JD reference (telescope_data row id of the raw capture) — never JD text; job_description stays the preamble (AST-2130) — and transitions the job." Gates (collapse → empty → prune → min_chars → classify) are unchanged and still run on the pruned text.
2. `fetch_jd_batch._scrape_one`: replace `text = await get_visible_text(url=job_link)` with
   `text, _, row_id = await scrape_visible_text_and_keep(job.get("candidate_id"), job_link)` (same `try` / `except` block, unchanged). Add `telescope_data_id=row_id` to the `_apply_jd_gates(...)` call. In the `if gated:` branch, before `passed += 1`, add
   `_log.info("%s | job %s: %s (batch: %s)", aid, "JD kept", pass_state, batch_id)`.
3. `fetch_relative_jd_batch._fetch_one`: directly after the `try` / `except` around `click_through_visible_text` (i.e. before the `final_url.startswith(...)` check), add
   `row_id = keep_telescope_data(job.get("candidate_id"), final_url, _VISIBLE_TEXT, text)`, and add `telescope_data_id=row_id` to its `_apply_jd_gates(...)` call.
4. `get_visible_text` stays imported (meteorite email path still uses it).
5. `python3 -m py_compile src/core/gazer.py`; ruff gate.
6. Scratch check (`debug/spikes/AST-2132/stage2.py`): temp DB with one job row; monkeypatch `gazer.get_visible_text`, `gazer.check_connectivity`, `gazer.transition_job_state` to stubs; run `fetch_jd_batch` with ok / closed / bot / short texts and confirm the **Done when** lines via SQL.

⚠️ **Decision:** The stored row holds the **raw** capture (pre-collapse, pre-prune). AST-2133's composed-JD reader applies collapse + prune on read (its Scope), so storing pruned text would prune twice.

⚠️ **Decision:** `fetch_relative_jd_batch` changes with `fetch_jd` because `_apply_jd_gates` is their shared save path (AST-2025). Leaving it on JD text would need a second save mode in the shared gate and would leave one pipeline scrape un-kept (parent Purpose: "every pipeline scrape is kept").

⚠️ **Decision:** Classified (closed / bot / cookie / missing) jobs also get the reference. Today they get the bad text saved as the JD; referencing the kept capture keeps that inspectability and the same displayed JD once AST-2133 composes it. Empty / too-short jobs get no reference (today they get no JD text either); their capture is still kept.

## Stage 3: Company writers store row ids

**Done when:** a scratch `fetch_website_batch` run (stubbed `scrape_company_homepage_content`) leaves `json_extract(company_data,'$.homepage_text')` and `'$.nav_links'` uuid-shaped, each resolving to a `telescope_data` row (`VISIBLE_TEXT` / `PAGE_LINKS`) whose `candidate_id` equals the company's; a bot-walled homepage is still kept. A scratch `fetch_job_pages_batch` run (stubbed `_scrape_pjl_page`) keeps a `VISIBLE_TEXT` (+ `PAGE_LINKS` when links exist) row per scraped page — bot walls included — and leaves `pjl_assembled_content` and `pjl_nav_links` NULL.

1. `fetch_website_batch._fetch_one_inner`: directly after `scrape = await scrape_company_homepage_content(...)` and before `dest = _fetch_website_fail_destination(...)`, add
   ```python
   # Keep every capture — bot walls included — before routing (AST-2132).
   text_id, links_id = keep_page_scrape(company.get("candidate_id"), scrape["company_website"], scrape)
   ```
   On the success path replace
   `data_to_save: Dict[str, Any] = {"homepage_text": visible_text}` / `if nav_links: data_to_save["nav_links"] = nav_links`
   with
   `data_to_save: Dict[str, Any] = {"homepage_text": text_id}` / `if links_id: data_to_save["nav_links"] = links_id`.
   Keep the `visible_text` / `nav_links` / `nav_count` locals (debug lines use them). After `transition_company_state(short_name, pass_state)` add
   `_log.info("%s | company %s: %s (batch: %s)", short_name, "homepage kept", pass_state, batch_id)`.
2. `fetch_job_pages_batch._fetch_one`:
   - After `cd = ...`, add `candidate_id = company.get("candidate_id")`.
   - Delete the `prior_by_key = ...` line (and its comment) and `run_nav_urls: List[str] = []`.
   - Directly after `record = await _scrape_pjl_page(url, browser_context, debug=debug)` (before the bot-wall check), add
     ```python
     text_id, links_id = keep_page_scrape(candidate_id, record["url"], record)
     # Row ids ride on the record for the PJL merge (AST-2134 reshapes pjl_scrape_pages to {url, id}).
     record = {**record, "visible_text_id": text_id, "page_links_id": links_id}
     ```
   - Delete the `if not record.get("error") and ...: run_nav_urls.extend(...) else: prior ...` block (including its comment) that follows `_merge_pjl_scrape_record`.
   - Delete `assembled = _assemble_pjl_content(pjl_pages)` and its comment; change the `save_company_data` payload to
     ```python
     {
         "pjl_scrape_pages": pjl_pages,
         # Derived on read from pjl_scrape_pages (AST-2134); None clears copies written before AST-2130.
         "pjl_assembled_content": None,
         "pjl_nav_links": None,
     }
     ```
   - In the `if pjl_pages:` branch, after `passed += 1`, add
     `_log.info("%s | company %s: %s (batch: %s)", short_name, "job pages kept", f"{len(pjl_pages)} page(s) -> {pass_state}", batch_id)`.
3. Imports: remove `_assemble_pjl_content` and `_merge_pjl_nav_links` from the `from src.core.roster import (...)` block, and `normalize_link` and `parse_enumerate_array` from the `from src.utils.formatting import (...)` block — after step 2 nothing in gazer uses them (planner grep: their only uses are the deleted lines). Re-grep before deleting; if any other use remains, keep that import.
4. `python3 -m py_compile src/core/gazer.py`; ruff gate.
5. Scratch check (`debug/spikes/AST-2132/stage3.py`): temp DB with one company (`candidate_id` set, `possible_joblist_links` set); stub `check_connectivity`, `create_batch_browser_session` / `create_browser_context` (async context managers yielding `None`), `scrape_company_homepage_content`, `_scrape_pjl_page`, `transition_company_state`; confirm the **Done when** lines via SQL.

⚠️ **Decision:** `pjl_scrape_pages` keeps today's row shape in this ticket. The `{url, id}` reshape is the "PJL merge" in AST-2134's Scope (`_merge_pjl_scrape_record` in `roster.py`), so this ticket hands it the ids on the scrape record (`visible_text_id`, `page_links_id`) and AST-2134's merge stores them. Parent AC 5's `pjl_scrape_pages` clause is met when AST-2134 lands.

⚠️ **Decision:** `pjl_assembled_content` / `pjl_nav_links` are written as `None` (not left alone) so a company re-fetched after this change cannot keep serving a stale pre-change copy; `json_extract` reads NULL either way (AC 5). Their rebuild-on-read is AST-2134's.

## Stage 4: Culture-cache checks resolve ids

**Done when:** with `company_data.website_content` = `[{url, id}]` whose rows hold bot-wall text, `fetch_culture_pages_batch` routes the job to `bot_blocked_state` (cached) and `fetch_company_culture_pages_batch` reports `cached`; with readable rows, the job passes as cached; with legacy `[{url, content}]` data, behavior is unchanged.

1. `fetch_culture_pages_batch`: change `recorded = cd.get("website_content")` to `recorded = resolve_telescope_value(cd.get("website_content"))`. In the coat-check branch, change `if _website_content_bot_walled(content):` to `if _website_content_bot_walled(resolve_telescope_value(content)):` (leave `company...["website_content"] = content` and the `if content:` test as they are).
2. `fetch_company_culture_pages_batch`: change `found = cd.get("website_content")` to `found = resolve_telescope_value(cd.get("website_content"))`, and inside the `try`, `found = await get_company_data(company, "website_content")` to `found = resolve_telescope_value(await get_company_data(company, "website_content"))`.
3. `_website_content_is_recorded`, `_website_content_bot_walled`, `_website_content_debug_summary` are unchanged (they read the resolved `[{url, content}]` shape).
4. `python3 -m py_compile src/core/gazer.py`; ruff gate.
5. Scratch check (`debug/spikes/AST-2132/stage4.py`): temp DB, stubbed `check_connectivity` / `transition_job_state` / `transition_company_state`; cover the three **Done when** cases.

⚠️ **Decision:** The coat-check result is resolved too, so these checks are correct both before AST-2134 (roster's `get_company_data` returns the raw blob value) and after (it returns resolved content — `resolve_telescope_value` passes resolved / legacy shapes through unchanged).

## AC traceability

- **AC 3** (every scrape kept, with candidate): Stage 3 step 1 (`fetch_website` → `VISIBLE_TEXT` + `PAGE_LINKS`, company `candidate_id`); Stage 2 step 2 (`fetch_jd` keeps at scrape time, before any gate, so bot-walled / closed jobs still add their row).
- **AC 4** (gazer only owner): only `gazer.py` imports `save_telescope_data` / `get_telescope_data_for_ids`; no edit to `src/external/telescope.py` or `service/telescope`. Builder runs both AC 4 commands before the last commit.
- **AC 5** (gazer-written keys): `homepage_text` / `nav_links` ids — Stage 3 step 1; `pjl_assembled_content` / `pjl_nav_links` NULL — Stage 3 step 2. `pjl_scrape_pages` `{url, id}` — AST-2134 (merge) from ids this ticket supplies; `website_content` is written by roster's coat-check — AST-2134.

## Integration notes (siblings — reference only, not planned here)

- **AST-2133:** the scraped JD is `job_data["jd_telescope_data_id"]` → raw capture; `job_description` is never written by gazer. After a self-heal `fetch_jd_batch`, the in-memory job carries the reference (not JD text). Classified jobs carry a reference too.
- **AST-2134:** use `keep_telescope_data` / `keep_page_scrape` / `scrape_visible_text_and_keep` / `scrape_page_links_and_keep` / `resolve_telescope_value` / `is_telescope_id` (lazy import from `src.core.gazer`, as `_first_bot_walled_page` does). `scrape_company_homepage_content` and `_scrape_pjl_page` must stay non-keeping — gazer already keeps their results in `fetch_website` / `fetch_job_pages`; the prefilter homepage call site keeps via `keep_page_scrape`. The PJL merge reads `visible_text_id` / `page_links_id` off the record. Today's `pjl_nav_links` was built only from this run's candidate URLs (plus prior links for those URLs on failed re-scrape); a rebuild from the whole `pjl_scrape_pages` ledger would also include pages for URLs no longer in `possible_joblist_links`.
- **Interim ftr state:** between this merge and AST-2133 / AST-2134, roster / tracker readers see row ids where they expect text. Merge order is blockedBy and UAT waits for all children, so nothing ships in that state.

## Flags for Chuckles / Archie (not acted on)

- **Not kept, not in this Scope:** `contact_task_gazer_scrape` (visible text + links for Estelle's contact task — no company / job entity), the meteorite email link scrape (parent out-of-scope), and `scrape_one` (job-list DOM; DOM is not stored).
- **Re-fetched legacy jobs:** a job whose `job_description` already holds an old scraped JD, if sent back through `fetch_jd` after this lands, will compose as old text (now "preamble") + new capture. The parent treats existing `job_description` as valid preamble; flagging in case Archie wants a guard.

## Lint / compile gate (every stage commit)

- `python3 -m py_compile src/core/gazer.py`
- `ruff check src/core/gazer.py` — finding count must not exceed the Stage 0 baseline (67). Fix any new finding on lines this ticket touched; do not clean up pre-existing findings.

## Boundaries

No `database.py` / `config.py` changes (AST-2131 shipped them). No composed-JD reader, `get_job_data`, consult, job API or modal changes (AST-2133). No roster writers / readers, `get_company_data`, PJL merge or admin preview changes (AST-2134). No data move (AST-2135). No tests or bible edits (Betty).

## Estimate

Confirm Chuckles estimate: 5 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2132
**Overall:** APPROVED
**Corpus:** 26c4e86a4d08addcefdbc3be68116703fedf6762 (canon tree at publish tip; `docs/canon-index.md` absent on ref)
**Publish ref:** `origin/sub/AST-2130/AST-2132-gazer-telescope-owner` @ `f9f18dcc0265cc3999e0c516cd3744ddc3c70bed`

## Canon scores

stat.logging.debug | A |
stat.logging.warning | A |
stat.logging.error | A |
stat.logging.info.entity | X |

## Traceability

AC3 → Stage 1 (`keep_*` / `scrape_*_and_keep`), Stage 2 (`fetch_jd_batch` + `fetch_relative_jd_batch` keep before gates), Stage 3 (`fetch_website_batch` / `fetch_job_pages_batch` keep every capture with `candidate_id`); AC4 → Scope + Stages 1–4 (only `gazer.py` imports `save_telescope_data` / `get_telescope_data_for_ids`; no telescope client/service edits; builder runs grep commands per plan); AC5 → Stage 3 (`homepage_text` / `nav_links` ids, `pjl_assembled_content` / `pjl_nav_links` NULL) plus ticket Boundaries for gazer-written keys — `website_content` write and `pjl_scrape_pages` `{url,id}` ledger shape deferred to AST-2134 (Stage 4 resolves ids for culture-cache reads only).

### acceptable — AC 5 wording vs child Boundaries

- **Location:** Ticket AC 5 (full parent quote) vs `## Boundaries` / plan `## AC traceability`.
- **Finding:** Observable AC 5 for this child is the gazer-writer subset (`homepage_text`, `nav_links`, derived PJL fields cleared); `website_content` and `{url,id}` on `pjl_scrape_pages` are explicitly AST-2134, with ids carried on scrape records here.
- **Recommendation:** UAT for AST-2132 should use the Boundaries slice, not the full parent AC 5 script alone.

### discuss — `contact_task_gazer_scrape` not kept

- **Location:** `## Flags for Chuckles / Archie`.
- **Finding:** Parent Purpose says every pipeline visible-text / link-list scrape is stored; plan excludes Estelle contact-task scrapes (no entity `candidate_id`). Flag is honest; product call is Archie's if that path counts as pipeline.
- **Recommendation:** No plan block; resolve at parent/UAT if Susan cares.

### acceptable — `stat.logging.info.entity` on frozen list

- **Location:** Canon scores X; plan `## Canon` pipe-shaped `_log.info` on modified writers.
- **Finding:** Directive `applies_when.paths` lists roster/consult/candidate/meteorite only — not `gazer.py`. Plan still adopts the pipe family for new success lines (good operator grep); compliance with this id is not territorially applicable.
- **Recommendation:** Optional parent Canon Scope tweak later; do not widen AST-2132's list in flight.

### acceptable — Interim ftr reader mismatch

- **Location:** `## Integration notes`.
- **Finding:** Between this child and AST-2133/2134, blobs may hold row ids while readers still expect text; plan documents blockedBy merge order — consistent with epic workflow.

### acceptable — No `## Self-assessment` block

- **Location:** Plan structure (`## Estimate` confirm only).
- **Finding:** Stages 0–4 + scratch checks carry complexity; not blocking.

**R6 (summary):** Single-file scope holds. Stage 0 gates on AST-2131 symbols present on the sub (`save_telescope_data` at `database.py`). Ownership model (core→data only via gazer), keep-before-route for bot walls, raw capture + `jd_telescope_data_id`, enumerated PAGE_LINKS, and resolve tolerance match parent functional items 2–3 for the gazer slice. No `fix-now` gaps.

context_tokens≈52000

## Review

- **Branch:** `origin/sub/AST-2130/AST-2132-gazer-telescope-owner`
- **Stage 0:** drift check clean — `save_telescope_data` / `get_telescope_data_for_ids` / `ensure_all_upsert_registry_schemas_at_startup` in `database.py`; `TELESCOPE_DATA_CONFIG["data_types"]` + `jd_telescope_data_id` in config; gazer call sites as planned; ruff baseline 67.
- **Stage 1:** `e48c71fb7` — telescope API (`is_telescope_id`, `keep_telescope_data`, `keep_page_scrape`, `scrape_visible_text_and_keep`, `scrape_page_links_and_keep`, `resolve_telescope_value`). New annotations use builtin generics (`str | None`, `dict[...]`) so ruff stays at baseline.
- **Stage 2:** `dc4ca951d` — `_apply_jd_gates` stores `jd_telescope_data_id`; `fetch_jd_batch` scrapes via `scrape_visible_text_and_keep`; `fetch_relative_jd_batch` keeps its click-through capture.
- **Stage 3:** `fd2b906f8` — `fetch_website_batch` keeps before routing, stores `homepage_text` / `nav_links` ids; `fetch_job_pages_batch` keeps each page (ids on the record), writes `pjl_assembled_content` / `pjl_nav_links` as `None`; unused imports dropped.
- **Stage 4:** `ab54313c3` — culture-cache checks resolve ids.
- **Verify:** `py_compile` OK; ruff 66 (baseline 67). Scratch checks (temp `ASTRAL_DB_DIR`, stubbed Telescope / transitions — under `/tmp`, `debug/` is cursorignored): Stage 1 keep / blank / resolve shapes incl. missing row; Stage 2 ok / closed / bot / short — 4 VISIBLE_TEXT rows with job `candidate_id`, refs on ok + classified only, `job_description` preamble untouched, states unchanged; Stage 3 homepage / nav ids resolve to rows with company `candidate_id`, bot-walled homepage + PJL kept, derived PJL fields `None`; Stage 4 bot-walled ids → bot state (cached), readable ids + legacy pass cached. AC 4: both commands empty.
- **Existing tests (Betty):** across every test file referencing gazer, 11 new failures vs untouched ftr (145 pre-existing reds there), all in `tests/component/core/test_gazer.py` and all asserting the pre-AST-2130 contract: `TestFetchWebsiteBatch` ×2 (`homepage_text` text, not id), `TestAst882HomepageReadyWfrSkip::test_scrapes_wfr_even_when_homepage_text_present` (same), `TestFetchJobPagesBatch` ×5 (`pjl_assembled_content` / `pjl_nav_links` strings), `TestFetchJdBatch::test_routes_classified_failures_and_passes` and `TestAst2025FetchRelativeJdBatch` ×2 (`get_visible_text` mocked as a bare string — wrapper now asks `return_final_url=True`; `job_description` key; gate kwargs without `telescope_data_id`).
- **No new tests** — coverage is Betty's (qa-child).
