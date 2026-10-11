# AST-2134 — Roster company scrapes and admin preview on telescope_data

**Parent:** [AST-2130 — Create a new table telescope_data](https://linear.app/astralcareermatch/issue/AST-2130)
**Ticket:** [AST-2134](https://linear.app/astralcareermatch/issue/AST-2134)
**Publish ref:** `origin/sub/AST-2130/AST-2134-roster-telescope-data`

Roster's company writers stop putting page text into `company_data`: the coat-check handlers (`_fetch_nav_links`, `_fetch_prefilter_notes`, `_fetch_website_content`), the single-company `prefilter_company` path and the three `job_list_visible` writers keep their captures through gazer's AST-2132 API and store row ids; the PJL merge stores `{url, id, links_id}` per page from the ids gazer's `fetch_job_pages` already puts on each record. Every roster reader (homepage presence check, batch prefilter block, upshot block, select-job-page PJL assembly / nav links, TRY_LINKS ledger) and `get_company_data` read through one resolve helper, so they produce today's text from either shape — legacy text or row ids — and `pjl_nav_links` is rebuilt on read from the page ledger. The admin ad-hoc preview resolves company ids via gazer and reads the job description through AST-2133's composed-JD function.

## Scope check

This ticket's `## Scope` names two files: `src/core/roster.py` (writers → gazer keep calls + row ids; PJL merge `{url, row id}`; readers resolve via gazer; `get_company_data` resolves before coat-check) and `src/ui/api/api_admin.py` (`_build_adhoc_live_content` company branch resolves via gazer; job branch uses the composed-JD function). Every stage edits only those two files. Not edited: `gazer.py` (AST-2132), `tracker.py` / `consult.py` / `api_jobs.py` (AST-2133), `database.py` / `config.py` (AST-2131), the migration script (AST-2135), tests / bible (Betty).

## Canon

`stat.logging.debug`, `stat.logging.warning`, `stat.logging.error`, `stat.logging.info.entity`. Consequences for this ticket:

- **debug:** every new call into a gazer function logs `Calling <fn>: [...]` / `Response from <fn>: ...` at `logger.debug` with full values — no truncation, no `if debug` gate. Existing `Calling get_visible_text` / `Calling extract_site_page_list` lines at the replaced call sites are renamed to the gazer function now called.
- **warning:** a missing `telescope_data` row is already warned once inside `gazer.resolve_telescope_value`; roster and admin add **no** second warning.
- **error:** no new `try/except`. Existing handlers (`logger.exception` in the coat-check handlers, per-page culture / PJL catches) stay as they are and now also cover the keep call, which raises on DB errors (AST-2132 decision).
- **info.entity:** existing `_entity_info(short_name, "company", "nav_links saved" / "website_content saved" / "prefilter_notes saved", …)` lines are kept unchanged; no new info lines.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/roster.py` | Config import; new helpers `_company_candidate_id`, `_resolve_company_value`, `_resolved_pjl_pages`, `_rebuilt_pjl_nav_links`, `_resolved_company_data`, `_keep_job_list_visible`; readers `_company_homepage_ready`, `_run_batch_company_prefilter`, `company_upshot_batch`, `run_select_job_page_dispatch`, `_find_job_page_from_assembled` (TRY_LINKS ledger); `get_company_data`; `_merge_pjl_scrape_record`; writers `_fetch_nav_links`, `_fetch_prefilter_notes`, `_fetch_website_content`, `prefilter_company`, `_apply_prefilter_decoded_company_outcome`, `_finalize_joblist_identified`, `_finalize_joblist_titles_after_chain`, `_finalize_joblist_titles_select_only` | core |
| `src/ui/api/api_admin.py` | Config import; `_build_adhoc_live_content` company branch (resolve ids, strip culture page text) and job branch (composed JD) | ui |

## Stage 0: Drift check (no commit)

**Done when:** every item below holds on HEAD after `sync-child.sh`, or the builder has stopped and posted the 🛑 comment on AST-2130.

1. `src/core/gazer.py` exports `is_telescope_id`, `keep_telescope_data(candidate_id, url, data_type, content)`, `keep_page_scrape(candidate_id, url, scrape) -> (text_id, links_id)`, `scrape_visible_text_and_keep(candidate_id, url, *, context=None) -> (text, final_url, row_id)`, `scrape_page_links_and_keep(candidate_id, url, *, context=None) -> (urls, row_id)`, `resolve_telescope_value(value)` with the behavior in its docstring (id → content or None; list of `{url, id, …}` → `{url, content, …}`, other keys kept, gone rows dropped, empty → None; anything else unchanged).
2. `gazer.fetch_job_pages_batch` puts `visible_text_id` / `page_links_id` on each record before `_merge_pjl_scrape_record`, and saves `pjl_assembled_content` / `pjl_nav_links` as `None`.
3. `src.utils.config.TELESCOPE_DATA_CONFIG` has `data_types` and `company_data_id_keys` = (`homepage_text`, `nav_links`, `website_content`, `job_list_visible`, `pjl_scrape_pages`).
4. `src/core/roster.py` functions named in **Files Changed** exist with the bodies this plan quotes (line numbers may shift).
5. **Stage 5 only:** `src/core/tracker.py` defines `compose_job_description(job) -> str` (AST-2133). If it is absent when Stages 1–4 are done, publish Stages 1–4 and **stop before Stage 5** with the 🛑 comment ("AST-2133 not merged on ftr") — do not stub it.

## Stage 1: Read path — one resolve helper, every roster reader

**Done when:** `roster.py` compiles; a scratch check on a temp DB (see **Verification**) shows `_resolved_company_data` returns a legacy-text blob unchanged (except `pjl_nav_links` rebuilt only when it is `None`/absent), resolves an id blob to the same text, and `get_company_data(company, "website_content")` with a deleted row calls the coat-check handler without changing `company_data` (AC 11).

1. Add `TELESCOPE_DATA_CONFIG` to the `from src.utils.config import (...)` block (alphabetical, after `TASK_CONFIG`).
2. Directly **above** `def _company_homepage_ready(`, add (lazy gazer imports — gazer imports roster at module load):

   ```python
   def _company_candidate_id(company: Dict[str, Any]) -> Optional[str]:
       """candidate_id for telescope_data rows; coat-check callers may pass a partial company dict."""
       return company.get("candidate_id") or (get_company(company.get("short_name") or "") or {}).get("candidate_id")


   def _resolve_company_value(key: str, value: Any) -> Any:
       """Stored company_data value -> the shape readers used before AST-2130 (AST-2134).
       Row ids resolve via gazer; legacy text passes through; a gone capture resolves to None."""
       from src.core.gazer import resolve_telescope_value  # lazy: gazer imports roster
       if key == "pjl_scrape_pages":
           return _resolved_pjl_pages(value)
       logger.debug("Calling resolve_telescope_value: [key=%s value=%s]", key, value)
       resolved = resolve_telescope_value(value)
       logger.debug("Response from resolve_telescope_value: %s", resolved)
       if key == "website_content" and isinstance(resolved, list):
           # Kept captures are raw; the pre-AST-2130 blob stored each page stripped.
           resolved = [
               {**p, "content": str(p.get("content") or "").strip()} if isinstance(p, dict) else p
               for p in resolved
           ]
       return resolved


   def _resolved_pjl_pages(pages: Any) -> Optional[list]:
       """pjl_scrape_pages -> [{url, visible_text, enumerated_nav_links?}] (today's row shape).
       {url, id, links_id} rows resolve via gazer; legacy text rows pass through; gone captures drop."""
       from src.core.gazer import resolve_telescope_value  # lazy: gazer imports roster
       logger.debug("Calling resolve_telescope_value: [key=pjl_scrape_pages value=%s]", pages)
       out: List[Dict[str, Any]] = []
       for row in resolve_telescope_value(pages) or []:
           if not isinstance(row, dict) or "content" not in row:
               out.append(row)  # legacy text row
               continue
           page: Dict[str, Any] = {"url": row.get("url") or "", "visible_text": str(row["content"] or "").strip()}
           links = resolve_telescope_value(row["links_id"]) if row.get("links_id") else ""
           if str(links or "").strip():
               page["enumerated_nav_links"] = str(links).strip()
           out.append(page)
       logger.debug("Response from resolve_telescope_value: %s", out)
       return out or None


   def _rebuilt_pjl_nav_links(cdata: dict) -> str:
       """pjl_nav_links as fetch_job_pages built it before AST-2130: each current candidate URL's ledger
       page links, candidate order, deduped. A ledger row only changes on a successful scrape, so this
       equals the run-built value (fresh links on success, last-known links on a failed re-scrape)."""
       by_key = {
           normalize_link(p.get("url") or ""): p
           for p in (cdata.get("pjl_scrape_pages") or []) if isinstance(p, dict)
       }
       urls: List[str] = []
       for u in cdata.get(ROSTER_CONFIG["select_job_page"]["pjl_url_data_key"]) or []:
           page = by_key.get(normalize_link(u))
           if page:
               link_map = parse_enumerate_array(page.get("enumerated_nav_links") or "")
               urls.extend(link_map[k] for k in sorted(link_map))
       return _merge_pjl_nav_links("", urls)


   def _resolved_company_data(cdata: dict) -> dict:
       """Copy of company_data with telescope row ids resolved and pjl_nav_links rebuilt when not stored (AST-2134)."""
       out = dict(cdata or {})
       for key in TELESCOPE_DATA_CONFIG["company_data_id_keys"]:
           if out.get(key) is not None:
               out[key] = _resolve_company_value(key, out[key])
       if out.get("pjl_nav_links") is None and out.get("pjl_scrape_pages"):
           out["pjl_nav_links"] = _rebuilt_pjl_nav_links(out)
       return out
   ```

   `_rebuilt_pjl_nav_links` and `_resolved_company_data` reference `_merge_pjl_nav_links` (defined later in the module) at call time only — no reorder needed.
3. `_company_homepage_ready`: replace `return len((cd.get("homepage_text") or "").strip()) > 0` with
   `return len((_resolve_company_value("homepage_text", cd.get("homepage_text")) or "").strip()) > 0`.
4. `_run_batch_company_prefilter`, in the `normalized.append({...})` dict: `"company_data": company.get("company_data") or {},` → `"company_data": _resolved_company_data(company.get("company_data") or {}),`. `assemble` and the `nav_links = (input_company.get("company_data") or {}).get("nav_links") or ""` line then read resolved text unchanged.
5. `company_upshot_batch`, in the `rows = [...]` dict: `"company_data": c.get("company_data") or {},` → `"company_data": _resolved_company_data(c.get("company_data") or {}),`. `_upshot_culture_text` is unchanged.
6. `run_select_job_page_dispatch`: `cdata = (company.get("company_data") or {}) if company else {}` → `cdata = _resolved_company_data(company.get("company_data") or {}) if company else {}`. `_pjl_maps_from_company_data` (assembles from resolved pages when `pjl_assembled_content` is empty) and `_nav_links_for_try_links` are unchanged.
7. `_find_job_page_from_assembled`, decomposed TRY_LINKS branch: `cdata = (company_row.get("company_data") or {}) if company_row else {}` → `cdata = _resolved_company_data(company_row.get("company_data") or {}) if company_row else {}`. Only `pjl_url_key` is saved from there, so no resolved text is written back.
8. `get_company_data`: replace

   ```python
       if key in company_data and company_data[key] is not None:
           return company_data[key]
   ```

   with

   ```python
       if key in company_data and company_data[key] is not None:
           value = company_data[key]
           if key in TELESCOPE_DATA_CONFIG["company_data_id_keys"]:
               # Row ids resolve via gazer; a deleted capture (None) falls through to fetch-on-missing (AC 11).
               value = _resolve_company_value(key, value)
           if value is not None:
               return value
   ```

   Update the docstring's first line to: `Return company_data[key] (telescope row ids resolved to content), fetching on-demand if missing (coat-check pattern).`

⚠️ **Decision:** One resolve path (`_resolve_company_value` / `_resolved_company_data`) for every reader instead of per-call-site edits — the readers' existing text-handling code then stays byte-for-byte as it is, which is what AC 6 / parent AC 7 require.

⚠️ **Decision:** Stored `pjl_assembled_content` / `pjl_nav_links` text (pre-AST-2130 blobs) is still used when present; rebuild happens only when the key is absent / `None` (gazer now writes `None`). A legacy `""` `pjl_nav_links` is kept as `""` so legacy output stays identical.

⚠️ **Decision:** `website_content` pages are stripped on read. Legacy blobs stored stripped text (strip is idempotent); kept captures are raw (`scrape_visible_text_and_keep`), so stripping keeps reader output identical across both shapes.

## Stage 2: PJL merge stores `{url, id, links_id}`

**Done when:** a scratch `_merge_pjl_scrape_record([], record)` with `visible_text_id` / `page_links_id` on the record returns `[{"url", "id", "links_id"}]`; an errored or empty record still leaves the prior pages unchanged; a same-URL record replaces in place.

1. In `_merge_pjl_scrape_record`, replace

   ```python
       row: Dict[str, Any] = {"url": new_record["url"], "visible_text": text}
       enum_nav = (new_record.get("enumerated_nav_links") or "").strip()
       if enum_nav:
           row["enumerated_nav_links"] = enum_nav
   ```

   with

   ```python
       # Page text and links live in telescope_data; the ledger keeps the row ids gazer kept them under (AST-2134).
       row: Dict[str, Any] = {"url": new_record["url"], "id": new_record.get("visible_text_id")}
       if new_record.get("page_links_id"):
           row["links_id"] = new_record["page_links_id"]
   ```

   Update the docstring's first line to: `Upsert a PJL capture {url, id, links_id?} by normalize_link (AST-1995 / AST-2134): replace in place, else append.` The error / empty-text guard and the replace-or-append loop are unchanged.

⚠️ **Decision:** One ledger entry per page carries both ids (`id` = VISIBLE_TEXT row, `links_id` = PAGE_LINKS row). `resolve_telescope_value` resolves `id` and keeps `links_id` as an extra key, which `_resolved_pjl_pages` resolves — no second list to keep in step.

## Stage 3: Company writers keep captures and store row ids

**Done when:** scratch runs on a temp DB with Telescope stubbed (see **Verification**) leave `nav_links`, `website_content` (`[{url, id}]`) and `job_list_visible` id-shaped, each resolving to a `telescope_data` row whose `candidate_id` is the company's; `prefilter_company` stores `nav_links` as an id; handler return values are the same text / `[{url, content}]` as before.

1. Directly **below** `_resolved_company_data`, add:

   ```python
   def _keep_job_list_visible(short_name: str, url: str, text: str) -> Optional[str]:
       """Keep the selected job-list page text in telescope_data; return the row id job_list_visible stores (AST-2134)."""
       from src.core.gazer import keep_telescope_data  # lazy: gazer imports roster
       candidate_id = _company_candidate_id({"short_name": short_name})
       logger.debug("Calling keep_telescope_data: [candidate_id=%s url=%s text=%s]", candidate_id, url, text)
       row_id = keep_telescope_data(candidate_id, url, TELESCOPE_DATA_CONFIG["data_types"]["VISIBLE_TEXT"], text)
       logger.debug("Response from keep_telescope_data: %s", row_id)
       return row_id
   ```

2. `job_list_visible` writers — store the id, using the selected page URL already in scope as `job_site_url`:
   - `_finalize_joblist_identified`: `save_company_data(short_name, {"job_list_visible": vis_save})` → `save_company_data(short_name, {"job_list_visible": _keep_job_list_visible(short_name, job_site_url, vis_save)})`.
   - `_finalize_joblist_titles_after_chain`: `extra_cd["job_list_visible"] = vis_save` → `extra_cd["job_list_visible"] = _keep_job_list_visible(short_name, job_site_url, vis_save)`.
   - `_finalize_joblist_titles_select_only`: `extra["job_list_visible"] = vis_save` → `extra["job_list_visible"] = _keep_job_list_visible(short_name, job_site_url, vis_save)`.
3. `_fetch_nav_links`: replace the `try:` body down to `return nav_links` with:

   ```python
       from src.core.gazer import scrape_page_links_and_keep  # lazy: gazer imports roster
       try:
           logger.debug("Calling scrape_page_links_and_keep: url=%s", company_website)
           async with create_browser_context() as context:
               url_list, row_id = await scrape_page_links_and_keep(
                   _company_candidate_id(company), company_website, context=context
               )
           logger.debug("Response from scrape_page_links_and_keep: urls=%s row_id=%s", url_list, row_id)
           if not url_list:
               return None
           save_company_data(short_name, {"nav_links": row_id})
           _entity_info(short_name, "company", "nav_links saved", len(url_list))
           return enumerate_array("", url_list)
   ```

   (the `except ValueError` / `except Exception` blocks stay). Docstring: `Coat-check handler for nav_links. Scrapes + keeps the homepage link list, saves its row id, returns the enumerated links.`
4. `_fetch_prefilter_notes`:
   - Add `from src.core.gazer import scrape_page_links_and_keep, scrape_visible_text_and_keep  # lazy: gazer imports roster` and `candidate_id = _company_candidate_id(company)` right after the `if not short_name or not company_website: return None` guard.
   - Replace the three lines `logger.debug("Calling get_visible_text: …")` / `visible_text = await get_visible_text(company_website)` / `logger.debug("Response from get_visible_text: …")` with:
     ```python
             logger.debug("Calling scrape_visible_text_and_keep: url=%s", company_website)
             visible_text, _, _ = await scrape_visible_text_and_keep(candidate_id, company_website)
             logger.debug("Response from scrape_visible_text_and_keep: %s", visible_text)
     ```
   - In the nav block: before `try:` add `nav_links_id = None`; replace `url_list = await extract_site_page_list(company_website, max_depth=1, verify=False)` with `url_list, nav_links_id = await scrape_page_links_and_keep(candidate_id, company_website)` preceded by `logger.debug("Calling scrape_page_links_and_keep: url=%s", company_website)` and followed by `logger.debug("Response from scrape_page_links_and_keep: urls=%s row_id=%s", url_list, nav_links_id)`.
   - `if enumerated_nav_links: data_to_save["nav_links"] = enumerated_nav_links` → `if nav_links_id: data_to_save["nav_links"] = nav_links_id`. The prompt (`parts`) and `_hydrate_prefilter_pjl_urls(..., enumerated_nav_links)` keep using the text.
5. `_fetch_website_content`: right before `logger.debug("Beginning culture page scrape loop …")` add `from src.core.gazer import scrape_visible_text_and_keep  # lazy: gazer imports roster` and `candidate_id = _company_candidate_id(company)`; after `pages = []` add `refs = []`. In the loop replace

   ```python
                       text = await get_visible_text(url=url, context=context)
                       logger.debug("Response from get_visible_text: url=%s text=%s", url, text)
                       if text and text.strip():
                           pages.append({"url": url, "content": text.strip()})
   ```

   with

   ```python
                       logger.debug("Calling scrape_visible_text_and_keep: url=%s", url)
                       text, _, row_id = await scrape_visible_text_and_keep(candidate_id, url, context=context)
                       logger.debug("Response from scrape_visible_text_and_keep: url=%s text=%s row_id=%s", url, text, row_id)
                       if text and text.strip():
                           pages.append({"url": url, "content": text.strip()})
                           refs.append({"url": url, "id": row_id})
   ```

   and `save_company_data(short_name, {"website_content": pages})` → `save_company_data(short_name, {"website_content": refs})`. `return pages` is unchanged. Docstring line 3: `Scrapes + keeps selected pages, saves [{url, id}], returns [{url, content}].`
6. `_apply_prefilter_decoded_company_outcome`: add keyword parameter `nav_links_id: Optional[str] = None` after `nav_links_from_data: str = "",`; replace

   ```python
       if nav_links_from_data:
           data_to_save["nav_links"] = nav_links_from_data
   ```

   with

   ```python
       # Blob holds the telescope row id; nav_links_from_data is the resolved text for PJL hydration (AST-2134).
       if nav_links_id:
           data_to_save["nav_links"] = nav_links_id
   ```
7. `prefilter_company`: directly after `scrape = await scrape_company_homepage_content(...)` (before the `if scrape.get("error"):` check, so bot walls / partial captures are kept too) add:

   ```python
           from src.core.gazer import keep_page_scrape  # lazy: gazer imports roster
           candidate_id = _company_candidate_id({"short_name": short_name})
           logger.debug("Calling keep_page_scrape: [candidate_id=%s url=%s scrape=%s]", candidate_id, scrape["company_website"], scrape)
           _, nav_links_id = keep_page_scrape(candidate_id, scrape["company_website"], scrape)
           logger.debug("Response from keep_page_scrape: nav_links_id=%s", nav_links_id)
   ```

   and pass `nav_links_id=nav_links_id,` in the `_apply_prefilter_decoded_company_outcome(...)` call after `nav_links_from_data=enumerated_nav_links,`. `_run_batch_company_prefilter` passes no id.
8. Re-grep: `rg -n "get_visible_text|extract_site_page_list" src/core/roster.py`. Both are still used elsewhere in roster (`jobs_found_process_job_site`, `_fetch_job_links_content`); if either import becomes unused, remove it from the import block.

⚠️ **Decision:** The batch prefilter path no longer re-saves `nav_links`. It read that value from the blob, so today's write was a same-value no-op; writing the resolved text back would put page text in the blob (AC 5).

⚠️ **Decision:** `job_list_visible` keeps a new VISIBLE_TEXT row (url = selected page) rather than pointing at the PJL page's row. The value can come from a TRY_LINKS / JOBS_FOUND scrape that has no ledger row, and one rule for all three writers needs no id plumbing through `visible_map`.

⚠️ **Decision:** `candidate_id` comes from the company row (`_company_candidate_id`), matching gazer's writers and AST-2135's export, not from the dispatch `ctx`.

## Stage 4: Admin preview — company branch

**Done when:** for one company in the temp DB, `_build_adhoc_live_content` for `prefilter_company`, `select_job_page` and `gaze` returns byte-identical strings before and after that company's blob keys are swapped to row ids (AC 6, see **Verification**).

1. Add `TELESCOPE_DATA_CONFIG` to the `from src.utils.config import (...)` block in `src/ui/api/api_admin.py` (alphabetical position).
2. In `_build_adhoc_live_content`, after `from src.utils.formatting import enumerate_array`, add `from src.core.gazer import resolve_telescope_value  # telescope_data reads go through gazer (AST-2134)`.
3. Company branch: directly after `cdata = company.get("company_data", {}) or {}`, add:

   ```python
           # Telescope row ids resolve via gazer; legacy text passes through unchanged (AST-2134).
           logger.debug("Calling resolve_telescope_value: [company=%s company_data=%s]", entity_id, cdata)
           cdata = {
               k: (resolve_telescope_value(v) if k in TELESCOPE_DATA_CONFIG["company_data_id_keys"] else v)
               for k, v in cdata.items()
           }
           logger.debug("Response from resolve_telescope_value: %s", cdata)
   ```
4. Gaze / other company tasks: `"\n\n".join(f"=== {p.get('url','')} ===\n{p.get('content','')}" for p in wc if p.get("content"))` → `"\n\n".join(f"=== {p.get('url','')} ===\n{str(p.get('content') or '').strip()}" for p in wc if p.get("content"))` (same strip-on-read rule as roster; legacy text is already stripped).
5. Job branch, `requires_company` block: `wc = (company.get("data") or {}).get("website_content") or ""` → `wc = resolve_telescope_value((company.get("data") or {}).get("website_content")) or ""`, and apply the same `str(p.get('content') or '').strip()` change to its join.

⚠️ **Decision:** `pjl_scrape_pages` resolves to gazer's `{url, content, links_id}` shape here; the admin preview does not read it (`select_job_page` previews `nav_links` only — AST-485 note), so no PJL row-shape helper is duplicated in the UI layer.

## Stage 5: Admin preview — job branch reads the composed JD (needs AST-2133)

**Done when:** Stage 0 item 5 holds; `git grep -n -E "\.get\((jd_key|[\"']job_description[\"'])" -- src/core src/ui/api ':!src/core/tracker.py'` returns nothing (parent AC 8); a job with no telescope reference previews exactly its stored `job_description`.

1. In the job branch of `_build_adhoc_live_content`, add `from src.core.tracker import compose_job_description` at the top of the `if entity_type == "job":` block.
2. `qualify_meteorite`: delete `jd_key = TRACKER_CONFIG["job_data_keys"]["job_description"]`; `f"CONTENT:\n{(job.get('job_data') or {}).get(jd_key, '') or ''}"` → `f"CONTENT:\n{compose_job_description(job)}"`.
3. Single-entity: `jd = job_data.get("job_description") or job_data.get("raw_job_listing") or ""` → `jd = compose_job_description(job) or job_data.get("raw_job_listing") or ""`.
4. If `TRACKER_CONFIG` is now unused in `api_admin.py` (`rg -n TRACKER_CONFIG src/ui/api/api_admin.py`), remove it from the config import block.

## Verification (scratch, never the live DB)

`data/astral.db` is a symlink to Susan's live DB. Scratch scripts live in `/tmp/AST-2134/` (not committed; `debug/` is cursorignored) and set `os.environ["ASTRAL_DB_DIR"] = "/tmp/AST-2134/db"` **before** importing any `src.*` module. Seed with `cp data/astral.db /tmp/AST-2134/db/astral.db`, then `ensure_all_upsert_registry_schemas_at_startup()`. Telescope is never called: stub `src.core.gazer.get_visible_text` / `src.core.gazer.extract_site_page_list` (and `roster.create_browser_context` with a no-op async context manager) via monkeypatch.

- **AC 5 (Stage 3):** pick a company with `nav_links` / `culture_links_to_explore` in the temp DB; run `_fetch_nav_links`, `_fetch_website_content`, and one `_finalize_joblist_identified` call with stubs; `json_extract(company_data, '$.nav_links')`, `'$.website_content'` entries' `id`, `'$.job_list_visible'` are uuid-shaped and each resolves via `get_telescope_data`. Merge check per Stage 2.
- **AC 6 (Stage 1 + 4):** record `_build_adhoc_live_content` for `prefilter_company`, `select_job_page`, `gaze` and `_resolved_company_data` output for one company with text blobs; in the temp DB only, replace that company's `homepage_text` / `nav_links` / `job_list_visible` with `keep_telescope_data(...)` ids of the same text, `website_content` with `[{url, id}]`, `pjl_scrape_pages` with `{url, id, links_id}`, and set `pjl_assembled_content` / `pjl_nav_links` to `None`; re-run — all strings byte-identical (select-job-page live content via `_pjl_maps_from_company_data` + `_build_select_job_page_live_content` on the resolved data).
- **AC 11 (Stage 1):** delete the `telescope_data` row(s) behind that company's `website_content` in the temp DB; snapshot `company_data`; call `get_company_data(company, "website_content")` with `_COATCHECK_HANDLERS["website_content"]` monkeypatched to a stub that records the call and returns a sentinel; the stub is called, no exception, `company_data` unchanged.

## Lint / compile gate (every stage commit)

- `python3 -m py_compile src/core/roster.py src/ui/api/api_admin.py`
- `ruff check` finding count must not exceed baseline: `src/core/roster.py` **324**, `src/ui/api/api_admin.py` **46** (`origin/ftr/AST-2130-telescope-data`). Fix new findings in touched lines only.

## Boundaries

No gazer changes (AST-2132), no composed-JD implementation (AST-2133 — Stage 5 only calls it), no data move or blob clearing (AST-2135), no tests or bible (Betty).

## Flags for Chuckles / Archie (not acted on)

- **Dependency:** Stage 5 calls `tracker.compose_job_description` (AST-2133, currently Plan Ready). AST-2134 is "After #2" only on the parent; it needs a blockedBy on AST-2133 for Stage 5, or Stage 5 waits per Stage 0 item 5.
- **Un-kept roster scrapes outside this Scope:** `_fetch_job_links_content` (TRY_LINKS retry + JOBS_FOUND), `jobs_found_process_job_site`'s `get_visible_text`, and `_scrape_list_page_dom_for_parse` still scrape without keeping. Parent Functional scope 3 says every pipeline scrape that returns visible text or links is kept; this ticket's Scope does not name them.
- **Pre-existing:** the admin `requires_company` block reads `company.get("data")`, not `company_data`, so its company context is probably always empty. Kept as-is (resolve wrapped around it) — out of scope to fix.

## Estimate

Confirm Chuckles estimate: 5 — agree.

## Joan validate

[plan-rubric]
**Ticket:** AST-2134
**Overall:** APPROVED
**Corpus:** 26c4e86a4d08addcefdbc3be68116703fedf6762 (canon tree at `56c4455`; `docs/canon-index.md` absent on ref)
**Publish ref:** `origin/sub/AST-2130/AST-2134-roster-telescope-data` @ `56c4455ebcd4f5056c726e8bee3c86202a2bf1c1`

## Canon scores

stat.logging.debug | A |
stat.logging.warning | A |
stat.logging.error | A |
stat.logging.info.entity | A |

## Traceability

AC5 (roster-written keys per Boundaries) → Stage 2 (`pjl_scrape_pages` `{url, id, links_id}`) + Stage 3 (`nav_links`, `website_content`, `job_list_visible`, `prefilter_company` `nav_links` id); `homepage_text` after `fetch_website` is gazer (AST-2132), not this ticket — N/A here. AC6 → Stage 1 (`_resolved_company_data` / readers) + Stage 4 (admin company preview + strip-on-read); migration “after clear” side is AST-2135 — fresh-write / id-swap parity only on this child. AC7 (parent AC11 — delete row, no blob surgery) → Stage 1 `get_company_data` resolve + fall-through to coat-check.

### discuss — Stage 5 depends on AST-2133

- **Location:** Stage 0 item 5; Stage 5; `## Flags`.
- **Finding:** `compose_job_description` and parent AC8 grep close only when Stage 5 lands after AST-2133 merge on `ftr`; plan gates with 🛑 stop after Stages 1–4 if missing.
- **Recommendation:** Ensure Linear `blockedBy` AST-2133 → AST-2134 for Stage 5 (or equivalent merge order); do not stub composer in roster/admin.

### discuss — Pipeline scrapes not named in Scope

- **Location:** `## Flags` (TRY_LINKS / JOBS_FOUND / list-page DOM paths).
- **Finding:** Parent functional item 3 (“every pipeline scrape… kept”) vs this Scope omitting `_fetch_job_links_content`, `jobs_found_process_job_site`, `_scrape_list_page_dom_for_parse`.
- **Recommendation:** Archie/product call whether a follow-up child or scope amendment is needed; not a plan defect for the two files named on the ticket.

### discuss — Child AC 5 quote vs Boundaries

- **Location:** Ticket AC 5 (mentions `homepage_text` / `fetch_website`) vs `## Boundaries` (“roster-written keys”).
- **Finding:** Plan and Verification correctly scope AC5 to roster coat-check / PJL / job-list writers; gazer homepage ids are AST-2132.
- **Recommendation:** UAT scripts for AST-2134 should use Boundaries slice, not full parent AC5 alone.

### acceptable — Admin company resolve vs roster `_resolved_pjl_pages`

- **Location:** Stage 4 step 3 (per-key `resolve_telescope_value`) vs Stage 1 `_resolved_pjl_pages`.
- **Finding:** AC6 admin tasks (`prefilter_company`, `select_job_page`, `gaze`) do not assemble from `pjl_scrape_pages`; PJL ledger shape is roster-internal until a preview needs it.
- **Recommendation:** If a future admin task reads `pjl_scrape_pages`, reuse roster helper or shared resolve — out of scope here.

### acceptable — No `## Self-assessment` block

- **Location:** Plan structure (`## Estimate` confirm only).
- **Finding:** Five stages + `/tmp` verification matrix carry complexity; not blocking.

**R6 (summary):** Two-file scope matches ticket. Central resolve path, writer→gazer keep, PJL merge ids, `get_company_data` AC11 behavior, and admin preview parity are definition-faithful for the roster/admin slice. Lazy gazer imports respect ownership (no direct `database` telescope calls from roster/admin). DRY via one `_resolve_company_value` / `_resolved_company_data`. No `fix-now` gaps.

context_tokens≈72000

## Review

- **Branch:** `origin/sub/AST-2130/AST-2134-roster-telescope-data`
- **Stage 0:** drift check clean for items 1–4. Item 5 (`tracker.compose_job_description`) was absent on the first pass, so Stages 1–4 were published and the build stopped (🛑 on AST-2130). After AST-2133 merged to ftr (`c27d6f159`), it is present, and Stage 5 was built after `sync-child`.
- **Stage 1:** `eca3d2560`. `TELESCOPE_DATA_CONFIG` import; helpers `_company_candidate_id`, `_resolve_company_value`, `_resolved_pjl_pages`, `_rebuilt_pjl_nav_links`, `_resolved_company_data` (and `_keep_job_list_visible`, which Stage 3 uses); the readers `_company_homepage_ready`, batch prefilter normalize, `company_upshot_batch`, `run_select_job_page_dispatch`, TRY_LINKS `cdata`; `get_company_data` resolves id keys and treats a gone row as fetch-on-missing. Three other `company_data` reads (vet discovery, parse dispatch, parse batch) touch only non-telescope keys and are unchanged.
- **Stage 2:** `1b926c531`. `_merge_pjl_scrape_record` stores `{url, id, links_id?}`. Its only caller is gazer's `fetch_job_pages_batch`.
- **Stage 3:** `6d6e8b3a1`. `_fetch_nav_links`, `_fetch_prefilter_notes`, `_fetch_website_content` (`[{url, id}]` saved, `[{url, content}]` returned), `prefilter_company` (`keep_page_scrape` before the error check; `nav_links_id` → `_apply_prefilter_decoded_company_outcome`); the three `job_list_visible` writers use `_keep_job_list_visible`. `get_visible_text` / `extract_site_page_list` imports are still used elsewhere and were kept.
- **Stage 4:** `a25c7d188`. Admin company branch resolves id keys via gazer; culture pages are stripped on read; `requires_company` website_content is resolved.
- **Stage 5:** `10e8fa422`. Admin `qualify_meteorite` and the single-entity JD read `compose_job_description`; `jd_key` and the unused `TRACKER_CONFIG` import are removed. The AC 8 grep returns nothing.
- **Canon self-correction:** `5bceff4a7` adds `Calling` / `Response` debug lines on the composed-JD calls, the admin `requires_company` resolve and the PJL `links_id` resolve (`stat.logging.debug`).
- **Verify:** `py_compile` OK on both files; ruff `roster.py` 324 / `api_admin.py` 46 (= ftr baseline). New `Optional`/`Dict` and lazy-import ordering findings on touched lines were fixed in place. Scratch checks ran in `/tmp/AST-2134/` on a temp DB copy (`ASTRAL_DB_DIR` set before imports; the harness asserts `DB_PATH` is under `/tmp`), with Telescope stubbed. The live DB has no company rows, so synthetic companies were seeded into the copy only.
  - Stage 1: legacy blob unchanged; id blob resolves to the same text; `pjl_nav_links` rebuilt equal; AC 11 (deleted `website_content` row → coat-check handler called, `company_data` unchanged).
  - Stage 2: merge shape, error/empty keep prior, same-URL replace in place.
  - Stage 3 (AC 5): `nav_links`, `website_content`, `job_list_visible`, prefilter-notes `nav_links` and `prefilter_company` `nav_links` are uuid-shaped and resolve to rows carrying the company's `candidate_id`; handler returns are unchanged.
  - Stage 4 (AC 6): admin `prefilter_company` / `select_job_page` / `gaze` and roster select-job-page live content are byte-identical before and after the id swap.
  - Stage 5: no reference → exactly the stored `job_description`; a reference → the composed JD; `raw_job_listing` fallback; `qualify_meteorite` block.
- **No new tests**. Coverage is Betty's (qa-child).


## Radia review

[code-rubric]
**Ticket:** AST-2134
**Publish ref:** `08691b03651bfdb65218b97a2cd4c4008967043a` (`origin/sub/AST-2130/AST-2134-roster-telescope-data`)
**Corpus:** `0d01e20d2b313a4e35cf3d07434b6cd69f615768`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.debug | A | | |
| stat.logging.warning | A | | |
| stat.logging.error | A | | |
| stat.logging.info.entity | A | | |

## Column diff vs plan stage

(aligned) — Joan: debug / warning / error / **info.entity** all **A**; code review matches (including post-review `5bceff4a7` debug on compose/resolve paths).

## Frame diff

- [ ] **AC5 (roster-written keys):** `nav_links`, `website_content` (`[{url,id}]`), `job_list_visible`, prefilter `nav_links` are uuid ids resolving to rows with company `candidate_id`; derived `pjl_assembled_content` / `pjl_nav_links` not rebuilt on write (`NULL` / rebuild-on-read) — Boundaries slice, not full parent AC5 (`homepage_text` = gazer AST-2132).
- [ ] **AC6:** Admin `prefilter_company` / `select_job_page` / `gaze` + roster select-job-page live content byte-identical text blob vs id blob (scratch / `TestAst2134*`).
- [ ] **AC7 (parent AC11 — delete row):** Deleted `telescope_data` behind `website_content` → `company_data` unchanged; `get_company_data` falls through to coat-check (no raise).

## Findings

### fix-now

(none)

### discuss

- **Pipeline scrapes not in Scope @susan:** Plan Flags list `_fetch_job_links_content`, `jobs_found_process_job_site`, `_scrape_list_page_dom_for_parse` still scrape without keep — parent functional “every pipeline scrape kept” vs this ticket’s two-file Scope. **Default:** Ship AST-2134 as scoped; open a follow-up child or parent amendment only if product wants those paths kept — not `resolve-child` scope creep.
- **Child AC5 wording vs Boundaries:** Ticket AC5 quotes `homepage_text` / `fetch_website`; roster Boundaries limit AC5 to roster writers. **Default:** UAT scripts use Boundaries + Verification matrix, not the full parent AC5 script alone.

### advisory

- **Sibling diff carry:** Three-dot diff vs `origin/dev` includes AST-2131–2133 stack (`gazer.py`, `tracker.py`, `consult.py`, …) — expected on stacked subs; AST-2134 product is `roster.py` + `api_admin.py` (+ Betty tests).
- **Plan §Boundaries vs qa-child:** `test_roster.py` (+304 lines), `test_api_admin.py` (+87), bible § AST-2134 — overrides “No tests or bible.”
- **Issue doc `## Review`:** “No new tests” is stale vs tip (Betty manifest on branch).
- **`_fetch_prefilter_notes`:** `scrape_visible_text_and_keep` keeps VISIBLE_TEXT in DB but only `nav_links_id` is stored in `company_data` (visible row id discarded) — satisfies roster key AC5; may leave unreferenced telescope rows (parent storage policy, not a Boundaries defect).
- **`requires_company` / `company.get("data")`:** Pre-existing empty `website_content` path in admin LIKE branch; this ticket wraps resolve on that field without fixing the key — unchanged behavior, plan Flags.

## Notes (Canon Scope — not scored)

- **Ownership:** No `save_telescope_data` / `get_telescope_data` in `roster.py` or `api_admin.py`; writers use gazer `keep_*` / `scrape_*_and_keep`; readers use `resolve_telescope_value` / `compose_job_description` (lazy imports).
- **AC8 closure:** JD grep outside `tracker` is **empty** on tip (Stage 5).
- **Stage 5 dependency:** Built after AST-2133 on `ftr` per issue doc stop/resume — appropriate.

## What’s solid

- Central resolve: `_resolve_company_value`, `_resolved_pjl_pages`, `_resolved_company_data`, `get_company_data` resolve + AC11 fall-through when resolve returns `None`.
- Writers: coat-check handlers and prefilter use gazer keep/scrape wrappers; `job_list_visible` via `_keep_job_list_visible`; PJL ledger `{url, id, links_id?}` from gazer record ids.
- Admin: company branch resolves `TELESCOPE_DATA_CONFIG["company_data_id_keys"]`; job branch uses `compose_job_description`; culture list strip aligned with roster.
- Logging: `Calling` / `Response` `logger.debug` on keep/resolve/compose paths; `_entity_info` on save paths; culture per-page failures still `logger.exception` with company pipe + continue.

## Recommended actions (downstream — not for Radia)

- Chuckles: append artifact, `docs(AST-2134): Radia review — clean`, post slim upshot, **Review Posted** → datt **PROCEED** to **User Testing**.
- UAT: AC5/6/7 per Boundaries; defer un-kept scrape paths to product follow-up (discuss default).
- Optional: refresh stale build `## Review` test line when appending.

context_tokens≈36000

---

`[code-rubric] PROCEED (Commit: 08691b0) roster admin telescope resolve`
