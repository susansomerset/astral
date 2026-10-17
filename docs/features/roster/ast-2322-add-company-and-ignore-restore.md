# AST-2322 — Add company and IGNORE restore

- **Linear:** [AST-2322](https://linear.app/astralcareermatch/issue/AST-2322)
- **Parent:** [AST-2318](https://linear.app/astralcareermatch/issue/AST-2318)
- **Publish ref:** `sub/AST-2318/AST-2322-add-company-and-ignore-restore`

Candidate Watch List gains an add-company form (name, website, Careers Page URL → `job_site`) that creates a candidate-scoped company in `TEST_WATCH` with an auto-derived collision-safe `short_name`. Ignored-page restore moves `IGNORE` → `TEST_WATCH` (not straight to `WATCH`). Sibling AST-2319 already registered `TEST_WATCH`, the four transitions, and the `test_watch` dispatch producer; this ticket only creates/restores into that hop. Does not own Watch List columns, dates toggle, count modal, or dropping the Retry Scrape button chrome (sibling AST-2321).

## Explicit scope gate

Ticket **Scope** names exactly these files/kinds: `src/core/roster.py` (new/modified create function), `src/ui/api/api_companies.py` (new add-company route; modified bulk/single transitions from config), `CompaniesWatchList.tsx` (add-company affordance only), `CompaniesIgnored.tsx` (restore-to-TEST_WATCH). No `config.py` edits — `ignored_list_to_state` stays `"TO_WATCH"` in the manifest; the Ignored page posts `"TEST_WATCH"` directly. No column redesign on Watch List.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/roster.py` | New `add_company_for_test_watch` (+ name→slug helper) creating a candidate-owned company in `TEST_WATCH` with Careers URL on `job_site` | core |
| `src/ui/api/api_companies.py` | New `POST /api/companies/add`; modify `bulk_state` to use `transition_company_state` and reject pairs absent from `ASTRAL_CONFIG["company_state_transitions"]`; completion `logger.info` on both mutating routes | ui |
| `src/ui/frontend/src/pages/CompaniesWatchList.tsx` | Add-company affordance (Modal + ListPage `actions`) with Careers Page URL field; no column/bulk chrome changes | ui |
| `src/ui/frontend/src/pages/CompaniesIgnored.tsx` | Restore bulk action posts `to_state: "TEST_WATCH"`; relabel control | ui |

## Stages

### Stage 1: Core create — candidate company → TEST_WATCH

**Done when:** Calling `add_company_for_test_watch(candidate_id, company_name, company_website, job_site)` inserts one company row scoped to that `candidate_id`, with `job_site` equal to the Careers Page URL string, `company_website` set, `company_name` set to the submitted name, `state == "TEST_WATCH"`, and a `short_name` derived from the name that matches `^[a-z0-9_]+$`. A second call with the same name for the same candidate gets a suffixed slug (`{base}_2`, …) when the base is taken. Empty name, website, or Careers URL raises `ValueError`.

1. In `src/core/roster.py`, immediately after `_INFLOW_SLUG_RE` (near `_slug_from_discovery_url`), add:

   ```python
   def _slug_from_company_name(name: str) -> str:
       slug = re.sub(r"[^a-z0-9]+", "_", (name or "").strip().lower()).strip("_")
       return slug
   ```

2. In the same module, add `def add_company_for_test_watch(candidate_id: str, company_name: str, company_website: str, job_site: str) -> str:` that:

   - Strips `candidate_id`, `company_name`, `company_website`, `job_site`. If any is empty after strip, raise `ValueError` with a short message naming the missing field.
   - Builds `base = _slug_from_company_name(company_name)`. If `base` is empty or not matched by `_INFLOW_SLUG_RE`, raise `ValueError("invalid short_name from company name")`.
   - Collision-safe pick: try `base`, then `f"{base}_{n}"` for `n` in `range(2, 100)`. Skip a candidate slug when `get_company(candidate_slug)` exists. If none free, raise `ValueError("short_name collision")`.
   - Call `save_company(short_name=chosen, state="TEST_WATCH", company_name=company_name, company_website=company_website, job_site=job_site, candidate_id=candidate_id)`.
   - Do **not** write `company_data["selected_pjl_url"]` — AST-2319’s validate already falls through to `job_site`.
   - Do **not** call `transition_company_state` on create (initial land is `save_company` with `TEST_WATCH`).
   - Return the chosen `short_name`.

⚠️ **Decision:** Slug from **company name**, not website domain — ticket Notes say auto-derive from company name. Reuse `_INFLOW_SLUG_RE` so inflow/add share the same short_name charset.

⚠️ **Decision:** Do not edit `build_state_ui_manifest()["ignored_list_to_state"]` (still `"TO_WATCH"`). That key lives in `config.py`, which is outside this ticket’s Scope. Stage 3 posts `"TEST_WATCH"` from the Ignored page instead. AST-2319 left the manifest key for the restore sibling; Scope partition put restore UI here without `config.py`.

### Stage 2: API — add route + transition-bound bulk_state

**Done when:** `POST /api/companies/add` with JSON `{candidate_id, company_name, company_website, job_site}` returns `201` and `{"short_name": ..., "state": "TEST_WATCH"}` for a valid body, `400` when any required field is missing/empty or core raises `ValueError`, and emits one completion `logger.info` line. `POST /api/companies/bulk_state` updates via `transition_company_state`, rejects a `(from_state, to_state)` pair not present in `ASTRAL_CONFIG["company_state_transitions"]` with `400`, still accepts `IGNORE`→`TEST_WATCH` and `WATCH`→`IGNORE`, and rejects `WATCH`→`WEBSITE_FOUND` (Watch List retry) because that pair is not in the transition table. Both mutating routes log once at completion per `stat.logging.info.api`.

1. In `src/ui/api/api_companies.py`, import `get_logger` from `src.utils.logging`, `ASTRAL_CONFIG` from `src.utils.config`, and `add_company_for_test_watch` + `transition_company_state` from `src.core.roster`. Add `logger = get_logger(__name__)`.

2. Add a named route **before** `/<short_name>` (same band as `/import`):

   ```python
   @companies_bp.route("/add", methods=["POST"])
   @require_auth
   def add_company():
   ```

   Body keys: `candidate_id`, `company_name`, `company_website`, `job_site` (Careers Page URL). If `candidate_id` or any of the three strings is missing/blank after strip → `400` `{"error": "..."}`. Call `add_company_for_test_watch(...)`. On `ValueError` → `400` with `str(exc)`. On success → `201` `{"short_name": sn, "state": "TEST_WATCH"}` and:

   ```python
   logger.info("%s | api %s completed: POST %s", candidate_id, "/api/companies/add", 201)
   ```

3. Replace the body of `bulk_state` so that for each `short_name` in `short_names`:

   - Load the company via `get_company(sn)`; skip missing rows (do not count them as updated).
   - Let `from_state = str(company.get("state") or "")`.
   - If `(from_state, to_state)` is not in `ASTRAL_CONFIG["company_state_transitions"]`, return `400` `{"error": f"transition not allowed: {from_state} -> {to_state}"}` immediately (no partial commit after the first illegal pair — process validation before any write, i.e. validate all pairs first, then apply).
   - On allowed pairs, call `transition_company_state(sn, to_state)` and count successes.
   - After all updates, `logger.info("%s | api %s completed: POST %s", "-", "/api/companies/bulk_state", 200)` and return `{"updated": updated}`.

⚠️ **Decision:** Pre-validate every requested row’s `(from_state, to_state)` against the transition list before any `transition_company_state` call, so a mixed illegal batch does not partially apply. Source of allowed pairs is config only — no hardcoded IGNORE/WATCH allowlist in the route beyond what AST-2319 registered.

⚠️ **Decision:** Rejecting `WATCH`→`WEBSITE_FOUND` at the API is this ticket’s “no Watch List retry bulk” (Scope). Sibling AST-2321 still owns removing the Retry Scrape **button**; until that lands, the button may 400 — that is correct under the transition table.

### Stage 3: Watch List add form + Ignored restore

**Done when:** On Watch List, with a candidate selected, the user can open an Add Company UI, submit Name + Website + Careers Page URL, and see a success toast; the new company exists in `TEST_WATCH` for that candidate (verify via API or DB). On Ignored, “Restore” (or equivalent) bulk action posts `to_state: "TEST_WATCH"` and companies leave the Ignored list (state is no longer `IGNORE`). Watch List column set and existing bulk action labels/buttons other than the new add affordance are unchanged by this ticket.

1. In `src/ui/frontend/src/pages/CompaniesWatchList.tsx`, mirror the New List import pattern:

   - State: `addOpen`, form fields `companyName`, `companyWebsite`, `jobSite` (Careers Page URL), reuse existing `toast` / `load`.
   - Pass `actions={<button className="btn primary" onClick={() => setAddOpen(true)}>Add Company</button>}` to `ListPage` (same `actions` slot as `CompaniesNewList` Import CSV).
   - Modal title `"Add Company"`; three labeled inputs: **Company Name**, **Website**, **Careers Page URL** (label text exactly that for the third field). Submit calls `POST /api/companies/add` with JSON `{ candidate_id: selectedId, company_name, company_website, job_site }` where `job_site` is the Careers Page URL value.
   - On `201`, toast success including returned `short_name`, close modal, clear fields, `load()`. On failure, toast error.
   - Do **not** change `columns`, dates toggle, count clicks, or bulk action list (leave Retry Scrape / Set to Ignore as-is for sibling AST-2321).

2. In `src/ui/frontend/src/pages/CompaniesIgnored.tsx`:

   - Change `handleMoveToWatch` to post `to_state: "TEST_WATCH"` (literal). Stop reading `manifest.company.bulk_transitions.ignored_list_to_state` for this action (that key remains `"TO_WATCH"` in config until a later ticket owns `config.py`).
   - Relabel the bulk action from `"Move to Watch"` to `"Restore to Test Watch"`.
   - Update the success toast to say companies were restored to test watch (not “moved to watch list”).
   - Keep using `bulk_state`; do not invent a second restore endpoint.

## Estimate

Confirm Chuckles estimate: 3 — agree
