# AST-489 — Google CSE integration and spike script

- **Linear (this ticket):** [AST-489](https://linear.app/astralcareermatch/issue/AST-489/google-cse-integration-and-spike-script-use-company-search-criteria-to)
- **Feature ref (publish target on `origin`):** `sub/AST-488/AST-489-google-cse-integration-and-spike-script` *(child of **AST-488**; **`ftr/AST-489`** is not used.)*
- **Parent (reference only — orchestration acceptance):** [AST-488](https://linear.app/astralcareermatch/issue/AST-488/use-company-search-criteria-to-search-for-companies-using-google-cse)

## Summary

Add a **thin Google Custom Search JSON API** client under **`src/external/`** that accepts a free-text query plus an optional per-call result cap and optional site-restriction list, reads **`GOOGLE_CSE_API_KEY`** and **`GOOGLE_CSE_ID`** from the environment (**`os.environ[...]`**, no fallbacks — §2.1), and returns normalized hits (**title, URL, snippet**). Add a **committed spike script** under **`scripts/spikes/`** that runs **non-interactively**, uses **hardcoded exemplar queries** and **domain restrictions** from the ticket description, calls the integration only (no dispatcher, roster DB, or UI), and prints one block of results per configured run so Susan can judge quality on the console.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/google_cse.py` | New module: one public function to execute a CSE search and return structured hits; HTTP via existing **`requests`** dependency; no import-time dependency on **`dispatcher`**, **`roster`**, **`database`**, or **`src.ui`**. | external |
| `scripts/spikes/ast489_google_cse_company_search_spike.py` | New runnable CLI (**`if __name__ == "__main__"`**): hardcoded queries + domain scenarios, calls **`google_cse`**, prints **`title` / `url` / `snippet`** per hit; **`sys.exit(1)`** with a **non-empty** stderr/stdout error line on missing env or API failure. | scripts (exempt layer rules) |

**Spike output:** default **no** `--out` path required; script prints to stdout only. Any future optional file output must default to **`debug/spikes/AST-489/…`** if added later — not in MVP for this plan.

## Stage 1: `google_cse` external client

**Done when:** A Python caller can **`import src.external.google_cse`** without starting batch work; calling the public search function with valid env and a test query returns a **list of dicts** (or small dataclass instances) with **`title`**, **`url`**, **`snippet`** strings; missing env vars or HTTP/API errors raise **`RuntimeError`** with an explicit message (**never** returns “success” with an empty list **when the API reported an error object or non-2xx HTTP**). A **successful** search that genuinely returns zero organic items may return an empty list (**that is not a “failure”** unless the JSON includes an **`error`** envelope from Google).

1. Create **`src/external/google_cse.py`** with a module docstring stating: Google Custom Search JSON API v1 only; external layer; **no logging** here (per §2.5 / §3.2); callers and the spike script surface human-facing errors.

2. Add module-level constants (not magic strings inline):
   - **`GOOGLE_CSE_API_URL = "https://www.googleapis.com/customsearch/v1"`**
   - **`_DEFAULT_REQUEST_TIMEOUT_SEC = 60`** (single named timeout for all `requests.get` calls in this module)

3. Define a **`TypedDict`** **`GoogleCseHit`** (or equivalent) with keys **`title`**, **`url`**, **`snippet`** — all **`str`**. Mapping from Google’s JSON: for each item in **`response["items"]`**, set **`url`** from **`link`**, **`title`** from **`title`**, **`snippet`** from **`snippet`**, using **`""`** if a key is absent.

4. Implement **`search_google_cse(query: str, *, max_results: int = 10, site_filters: Sequence[str] | None = None) -> list[GoogleCseHit]`** as the **only** public symbol (export via **`__all__`**):
   - **Credentials (start of function body):** **`api_key = os.environ["GOOGLE_CSE_API_KEY"]`** and **`cx = os.environ["GOOGLE_CSE_ID"]`**. Let **`KeyError`** propagate **or** wrap once in **`RuntimeError("`… missing GOOGLE_CSE_API_KEY …`")`** — either is acceptable as long as the message names **both** variable names expected in **`env.example`**.
   - **Query assembly:** Start from **`query.strip()`**. If empty after strip, raise **`ValueError("empty query")`** (spike will not pass empty strings). If **`site_filters`** is non-**None** and non-empty, append a balanced **`(site:… OR site:…)`** group: for each entry **`s`** in **`site_filters`**, use **`site:`** + **`s.strip()`** inside the group (entries are host/path fragments exactly as Constants below — no extra slashes invented by the builder). Insert this group **before** submitting to Google by concatenating onto the **`q`** parameter as a trailing token: **`f"{base} ({site_clause})"`** where **`site_clause`** is **`" OR ".join(f"site:{token}" for token in normalized_filters)`**.
   - **Pagination / `max_results`:**
     - Custom Search **`num`** request parameter **must respect Google’s documented per-request ceiling (≤ 10)**. Use **`min(10, remaining)`** for each HTTP call.
     - If **`max_results == 0`**: treat as **unbounded** relative to caller — keep requesting successive pages using Google’s **`nextStartIndex`** returned in **`queries.nextPage`** in the parsed JSON (**or**, if **`nextPage` absent**, stop after the first page whose **`items` list is empty). **Do not** cap page count with an arbitrary constant; stop only on natural API termination (no next page, empty items, or duplicate **`start`** seen).
     - If **`max_results > 0`**: stop when accumulated hits **≥** **`max_results`**, slice the return list down to exactly **`max_results`** if the last page over-fetched.
     - Use the **`start`** query parameter (1-based index from API docs) for pagination; initialize **`start=1`**, then advance using **`nextStartIndex`** when present, else break.
   - **HTTP:** **`requests.get(GOOGLE_CSE_API_URL, params={...}, timeout=_DEFAULT_REQUEST_TIMEOUT_SEC)`**.
   - **Non-2xx:** raise **`RuntimeError`** including HTTP status code and **up to ~500 chars** of **`response.text`** (decode safely).
   - **2xx body:** **`response.json()`** inside **`try`**; on JSON failure raise **`RuntimeError`** explaining invalid JSON.
   - If parsed JSON contains top-level **`"error"`** with **`message`** / **`code`**, raise **`RuntimeError`** including those strings (**do not** return `[]` for that condition).
   - Otherwise append **`items`** into the accumulator hits list, continuing pagination per the rules above.

5. **`site_filters` canonical tokens for spike (Constants in spike file, referenced by plan)** — spike passes these literal strings into **`search_google_cse`**:
   - LinkedIn **company pages (not `/jobs`):** **`linkedin.com/company`**
   - **`crunchbase.com`**
   - **`builtin.com`**
   - **`wellfound.com`**
   - **`indeed.com`**

⚠️ **Decision:** **Lazy env read inside **`search_google_cse`** only** (not gmail-style import-time asserts) so the web app **can import the repo** without CSE secrets until something calls search; the spike hits the function immediately and fails loudly per AC3.

⚠️ **Decision:** Use **`requests`** only (already in **`requirements.txt`**) — no new dependencies.

## Stage 2: Spike script

**Done when:** With valid **`GOOGLE_CSE_*`** env vars, **`python3 scripts/spikes/ast489_google_cse_company_search_spike.py`** from repo root prints **at least one page of hits** for **each** of the three exemplar queries as separate sections; without credentials or on API error it exits **non-zero** and prints an explicit error message; each printed hit includes **title, URL, snippet** on separate lines (or clearly labeled one-liners). Collectively, the script runs **at least one** search whose **`site_filters`** include **LinkedIn company** and **at least one** search whose **`site_filters`** include **one of** Crunchbase / Builtin / Wellfound / Indeed (job / careers aggregators per ticket).

1. Create **`scripts/spikes/ast489_google_cse_company_search_spike.py`** following the **`ast438_*.py`** pattern: shebang, docstring, **`Path(__file__).resolve().parent.parent.parent`** → **`sys.path.insert(0, str(_ROOT))`**, then import **`from src.external.google_cse import search_google_cse`**.

2. Define **`EXEMPLAR_QUERIES`** as a **tuple of three strings** copied **verbatim** from the ticket body:
   - **`healthtech SaaS platform "Series B" OR "Series C" remote`**
   - **`healthcare software platform integration company 2024 2025`**
   - **`clinical data platform SaaS company remote-first`**

3. Define **`RUNS`** as a **list of dicts** (or parallel tuples) with **`query`**, **`site_filters`**, **`max_results`** where:
   - **`max_results`** is **`10`** for every run (default per ticket).
   - There are **≥3** runs — **one per exemplar query** — so each exemplar appears in **at least one** run’s **`query`** field exactly.
   - **At least one** run uses **`site_filters=("linkedin.com/company",)`** (alone or with others).
   - **At least one different** run uses **`site_filters`** that include **`indeed.com`** or **`wellfound.com`** (job/careers aggregators) **without** being the same run as the pure-LinkedIn-only requirement if you choose to combine filters in one run, **or** satisfy the “additional domain” requirement on a separate run — simplest: **Run A** query[0] + LinkedIn only; **Run B** query[1] + **`("crunchbase.com", "builtin.com")`**; **Run C** query[2] + **`("wellfound.com", "indeed.com")`**. Adjust ordering if needed; **do not** drop an exemplar.

4. Implement **`main() -> None`**:
   - Loop **`RUNS`** in order. For each, print a header line with **query + site_filters + max_results**, then call **`search_google_cse`** inside **`try`/`except Exception`**. On exception: print **`f"ERROR: {exc}"`** to **stderr**, **`sys.exit(1)`** immediately (AC3 — no “empty success”).
   - For each hit dict: print **`Title:`**, **`URL:`**, **`Snippet:`** (or equivalent unambiguous labels) with blank line between hits.
   - If a run returns **zero** hits but **no** exception: print a **high-visibility WARNING** line to stderr that names the query + filters (**do not** print a fabricated hit). **`sys.exit`** stays **`0`** in that case — AC3 applies to **credentials / HTTP / API error JSON**, not to a legitimate empty organic result set. If Susan sees repeated zeros for exemplars, escalate on the ticket (queries or CSE config), not silent success pretending there were hits.

### Self-review (ASTRAL_CODE_RULES)

- **§1.3 / §2.5:** External module stays I/O-only; spike is **`scripts/`** exempt.
- **§2.1:** Secrets strictly from **`os.environ[...]`** inside **`search_google_cse`** (and optional **`KeyError`** wrap); no literals for keys in **`config.py`** (not needed — env-only secrets).
- **§2.4 / §2.6:** Out of scope — no dispatcher, batches, or state transitions (ticket **Boundaries**).
- **§3.3:** **`external`** imports **`typing`**, **`os`**, **`requests`** only — **not** **`utils`** unless a future refactor shares a helper (not in this plan).
- **§3.6:** Spike script is **committed code**; its **console output** is not written under **`docs/features/`**; optional future **`--out`** would default to **`debug/spikes/AST-489/`** only.

## Execution contract (for the developer agent)

Per **`plan-astral`**: execute stages in order; **do not** add dispatcher hooks, **`dispatch_tasks`**, DB writes, UI, Estelle, or company-name parsing; **do not** add new **`pip`** dependencies.

## Self-Assessment

**Scope:** `Single-Component` — One new external module plus one spike script; no core/data/ui edits.

**Conf:** `Medium` — Google CSE JSON fields and pagination are familiar, but empty-hit vs API-error distinction and unbounded pagination must match this plan literally.

**Risk:** `low` — Isolated code path; failure only affects callers of **`search_google_cse`** and the spike script.

## Self-Assessment justifications (required)

- **Scope:** Product paths are **`src/external/google_cse.py`** and **`scripts/spikes/ast489_google_cse_company_search_spike.py`**; Betty added **`tests/component/external/test_google_cse.py`** and an **`ASTRAL_TEST_BIBLE.md`** row per **`qa-astral`** (not “only two files” end-to-end).
- **Conf:** API pagination and error envelopes are specified here; if Google changes JSON shape, stop and comment rather than improvising parsers.
- **Risk:** No shared hot paths; worst case is a mis-invoked external helper or noisy spike output — no production batch impact.

---

## Review stub (post-build — build-astral §11)

No PR opened from this lane per workflow; architect opens PR at **PR Ready** after **UAT**.

| Item | Value |
|------|-------|
| **Integration branch** | `dev-ada` |
| **Feat commit (`dev-ada`)** | `8ff8f91e391dece91848c973d2e54145eb99c4d3` |
| **Publish ref** | `origin/sub/AST-488/AST-489-google-cse-integration-and-spike-script` |
| **Notes** | Component lane: **`test(AST-489)`** on **`tests/component/external/test_google_cse.py`** + bible §7.13b (Betty). Spike output stays console-only (**`§3.6`**). |

## Review

**Reviewed tip:** `11b855e279490fc26831fa2dfd0b631119b10bcc` — three-dot **`origin/dev`…`origin/sub/AST-488/AST-489-google-cse-integration-and-spike-script`** (Radia doc-only follow-up appended on this publish ref afterward; see Linear **AST-489** for the doc commit SHA).

### What’s solid

- **Plan fidelity:** `search_google_cse` implements lazy `GOOGLE_*` env reads with explicit **`RuntimeError`** on missing secrets, **`ValueError`** on empty stripped query, balanced **`site:`** OR-clauses, **`num`** capped at 10 per request, **`max_results == 0`** pagination via **`queries.nextPage`/`startIndex`** with **`seen_starts`** loop guard, **`RuntimeError`** on non-2xx / invalid JSON / non-object root / API **`error`** object / non-list **`items`**, and **`[]`** only for genuine zero-organic shapes.
- **Ticket boundaries:** No dispatcher, **`dispatch_tasks`**, DB writes, UI, roster wiring, Estelle, or company-name ingest; spike imports **`search_google_cse`** only.
- **Layers (§2.5 / §3.3, rubric B2):** External module stays I/O-only with **`requests`**; no **`get_logger`**, no **`src.data`**; spike **`print`**/`stderr` is **`scripts/`**-scoped.
- **AC3 semantics:** Spike **`sys.exit(1)`** on integration failures; WARNING + continue on organic zero-hit runs matches the shipped plan’s clarification (credentials/API vs empty results).
- **Tests + bible:** `tests/component/external/test_google_cse.py` covers credential gaps, HTTP/JSON/error-envelope/item-shape paths, filter assembly, and pagination branches; **`ASTRAL_TEST_BIBLE.md`** maps the lane.

### Issues

| Severity | Topic | Location | Notes |
|----------|--------|----------|-------|
| advisory | Self-Assessment vs footprint | § **Self-Assessment justifications** | **Resolved 2026-05-25:** wording now includes component tests + bible. |
| advisory | Review stub “tests untouched” | **Review stub** table | **Resolved 2026-05-25:** **Notes** row documents Betty’s test + bible delivery. |
| advisory | Spike `except Exception` | `scripts/spikes/ast489_google_cse_company_search_spike.py` | Surfaces **`ERROR:`** + exit 1 (not swallowed); **`noqa`** is honest—optional tighten to **`RuntimeError`/`ValueError`** if you want a narrower taxonomy. |
| advisory | Silent skip of bad `site_filters` entries | `search_google_cse` | **`Sequence`** accepts non-**`str`**; non-strings are skipped (see tests). **Resolved 2026-05-25:** `search_google_cse` docstring documents skip behavior for callers. |

### Recommended actions

1. No **fix-now** items identified; **`resolve-astral`** can proceed on engineer line per usual.
2. **Done (2026-05-25):** Review stub, Self-Assessment justifications, and `site_filters` docstring reconciled with Radia’s advisory items.

---

## Resolution (resolve-astral)

**2026-05-25 (Ada)** — Radia **`review-astral`**: **fix-now** none. Addressed **advisory** doc drift: **Self-Assessment justifications** and **Review stub** **Notes** now reflect **`test(AST-489)`** + **`ASTRAL_TEST_BIBLE.md`** §7.13b; **Issues** table updated; **`search_google_cse`** docstring notes that non-**`str`** **`site_filters`** entries are skipped. Left spike **`except Exception`** advisory as-is (explicit **`ERROR:`** + **`sys.exit(1)`**, documented in review).

**Publish ref:** `origin/sub/AST-488/AST-489-google-cse-integration-and-spike-script`
