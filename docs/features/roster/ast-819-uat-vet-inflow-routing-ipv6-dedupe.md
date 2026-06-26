# AST-819 — UAT: vet_inflow routing + IPv6 URL dedupe crash

- **Linear:** [AST-819](https://linear.app/astralcareermatch/issue/AST-819/uat-vet-inflow-routing-ipv6-dedupe)
- **Parent:** [AST-815](https://linear.app/astralcareermatch/issue/AST-815/get-vet-inflow-discovery-to-work)
- **Publish ref:** `origin/sub/AST-815/AST-819-uat-vet-inflow-routing-ipv6-dedupe`
- **UAT bug of:** [AST-815](https://linear.app/astralcareermatch/issue/AST-815/get-vet-inflow-discovery-to-work) — Susan re-test 2026-06-26 03:00 after AST-817 prep-uat
- **Related:** [AST-817](https://linear.app/astralcareermatch/issue/AST-817) (consult company vet routing — merged on `origin/ftr/AST-815-vet-inflow-discovery-routing` @ `fe6edd7`)

Susan re-tested **vet_inflow_discovery** after AST-817 prep-uat. Scheduler claimed company `4chealthin_org` (`entity_type=company`, `task_key=vet_inflow_discovery`, `batch_size=1`) but execution entered **`run_inflow_discovery_batch`** (14 stale CSE terms) and crashed with **`ValueError: Invalid IPv6 URL`** in **`_normalize_company_url_for_dedupe`**. Parent AC requires company vet activity (`vet_inflow_discovery_company`), not discovery CSE logs.

**Root cause (two defects):**

1. **Routing (AST-817):** Stale **`consult.run_consult_task`** company branch forced **`vet_inflow_discovery`** into **`run_inflow_discovery_batch`**. Fix landed in **AST-817** on **`ftr`** — this bug branch inherits it; build must **verify** and must **not** reintroduce the block.
2. **IPv6 / malformed URL (new):** **`normalize_url`** → **`urlparse`** raises **`ValueError`** on malformed bracketed hosts (e.g. `http://[::1`, `https://[invalid-ipv6]/path`). **`_normalize_company_url_for_dedupe`** does not catch this; a bad CSE hit URL or blurb pipe segment crashes the whole batch.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | Verify only — no `vet_inflow_discovery` company mis-route (AST-817 regression guard) | core |
| `src/core/roster.py` | Harden **`_normalize_company_url_for_dedupe`** — catch **`ValueError`**, return `""` | core |

**Out of scope:** `src/utils/config.py`, `src/data/database.py` dispatch seed (Susan's log shows `entity_type=company`), **`inflow_discovery`** candidate CSE logic, **`inflow_resolve_website`**, mechanical vet prompt (AST-776), Betty tests.

## Stage 1: Verify AST-817 consult routing on this branch (no code unless regression)

**Done when:** `rg vet_inflow_discovery src/core/consult.py` returns zero matches; `run_inflow_discovery_batch` appears only under `entity_type == "candidate"`; company vet falls through to `run_company_task`.

1. From repo root:
   ```bash
   rg -n "vet_inflow_discovery" src/core/consult.py
   ```
   Expect **exit 1** (no matches).

2. Confirm **`run_inflow_discovery_batch`** is referenced **only** inside the **`if entity_type == "candidate":`** branch (~lines 2014–2017 today on **`ftr`** tip).

3. Confirm company branch tail is unchanged:
   ```python
   return await roster.run_company_task(
       input_state, entities[0], batch_id, ctx, debug,
       dispatch_task_key=dispatch_task_key,
   )
   ```
   for all company keys including **`vet_inflow_discovery`** — no special-case before this return.

4. **If** step 1 finds a `vet_inflow_discovery` company early-return block (AST-817 regression): delete it per **`docs/features/roster/ast-817-vet-inflow-company-routing.md` Stage 1 — then continue to Stage 2. **If** steps 1–3 pass: **no consult commit**; proceed to Stage 2 only.

⚠️ **Decision:** Do not add a second consult routing path — AST-817 surgical deletion is the fix; this UAT ticket only guards against regression.

## Stage 2: Harden `_normalize_company_url_for_dedupe` against malformed URLs

**Done when:** `_normalize_company_url_for_dedupe("http://[::1")` and `_normalize_company_url_for_dedupe("https://[invalid-ipv6]/path")` return `""` without raising; valid URLs (e.g. `https://www.Acme.com/jobs/`) unchanged.

1. In **`src/core/roster.py`**, edit **`_normalize_company_url_for_dedupe`** (~line 192):

   Replace the body after the empty-string guard with a **`try`/`except ValueError`** wrapper around **`normalize_url(u)`** and **`urlparse(n)`**:

   ```python
   def _normalize_company_url_for_dedupe(url: str) -> str:
       """Host-level URL key for roster ingest dedupe (strip www. after normalize_url)."""
       u = (url or "").strip()
       if not u:
           return ""
       try:
           n = normalize_url(u)
           parsed = urlparse(n)
       except ValueError:
           return ""
       netloc = parsed.netloc or ""
       if netloc.startswith("www."):
           netloc = netloc[4:]
       path = parsed.path.rstrip("/") if parsed.path else ""
       out = f"{parsed.scheme.lower() if parsed.scheme else 'https'}://{netloc}{path}"
       if parsed.query:
           out += f"?{parsed.query}"
       return out
   ```

2. **Do not** change **`_slug_from_discovery_url`**, **`_candidate_company_urls`**, **`record_inflow_discovery_hit`**, or **`run_inflow_discovery_batch`** loop logic — callers already skip when norm is empty (`if not norm`, `if not norm or norm in seen_urls`).

3. Run **`python3 -m py_compile src/core/roster.py`**.

⚠️ **Decision:** Catch **`ValueError` only** (what **`urlparse`** / **`ipaddress`** raise for malformed IPv6) — not broad **`Exception`** — so unexpected bugs still surface.

## Stage 3: Regression verification + UAT checklist

**Done when:** Grep + manual sanity checks pass; Betty manifest documented in review stub.

1. Shell sanity (build agent, before commit):
   ```bash
   python3 -c "
   from src.core.roster import _normalize_company_url_for_dedupe as n
   assert n('https://www.Acme.com/jobs/') == 'https://acme.com/jobs'
   assert n('http://[::1') == ''
   assert n('https://[invalid-ipv6]/path') == ''
   print('ok')
   "
   ```

2. Re-run step 1 from Stage 1 (consult routing guard).

3. **Betty test gate (do not edit tests in build):** document component scenarios:
   - `tests/component/core/test_roster.py::TestAst776VetInflowDiscoveryCompany::test_consult_routes_company_vet_via_run_company_task` (routing regression)
   - New or extended case: `_normalize_company_url_for_dedupe` returns `""` for malformed IPv6 without raise

4. **Susan UAT (after deploy):**
   - Candidate **somerset**, **vet_inflow_discovery** `available ≥ 1`, `batch_size=1`, `run_count=1`, `debug=True`
   - Manual **Run** or AUTO tick on company `4chealthin_org` (or next eligible **NEW** + blurb row)
   - Logs show **`vet_inflow_discovery_company`** / blurb vet index headers — **not** `run_inflow_discovery_batch` stale-term CSE loop
   - Batch completes without **`ERROR dispatch.scheduler: ... crashed`**
   - Pass → **WEBSITE_FOUND** or reject → **VET_FAILED**

## Self-Assessment

**Scope:** `minor` — one defensive guard in **`roster._normalize_company_url_for_dedupe`** plus consult routing verification (AST-817 already on **`ftr`** base).

**Conf:** `high` — Susan's traceback pinpoints both failure modes; AST-817 fix pattern is proven; IPv6 repro is confirmed locally (`urlparse` raises **`ValueError`** on `http://[::1`).

**Risk:** `Medium` — dedupe helper is shared across discovery ingest and blurb URL collection; returning `""` for unparseable URLs changes behavior from crash → skip (intended per AC #3).

## ASTRAL_CODE_RULES self-review

| Rule | Plan alignment |
|------|----------------|
| §1.3 DRY | Single try/except in existing helper — no duplicate normalizers |
| §2.4 batch | Malformed URL → skip dedupe entry, batch continues |
| §2.6 state machine | Unchanged — vet transitions stay in **`vet_inflow_discovery_company`** |
| §3.3 imports | No new imports |
| §3.5 naming | No new public symbols |

No conflicts flagged.

## QA review stub (Betty @ Code Complete)

| Scenario | File | Expected test |
|----------|------|---------------|
| Consult company vet → `run_company_task` | `src/core/consult.py` | `::TestAst776VetInflowDiscoveryCompany::test_consult_routes_company_vet_via_run_company_task` |
| Malformed IPv6 URL dedupe safe | `src/core/roster.py` | `::test_normalize_company_url_*` (extend or add malformed-IPv6 case) |
| Valid URL dedupe unchanged | `src/core/roster.py` | `::test_normalize_company_url_strips_www` |

**Narrowed run (suggested):**
```bash
tests/component/core/test_roster.py::TestAst776VetInflowDiscoveryCompany::test_consult_routes_company_vet_via_run_company_task \
tests/component/core/test_roster.py -k "normalize_company_url"
```

## Build review stub

**Publish ref:** `origin/sub/AST-815/AST-819-uat-vet-inflow-routing-ipv6-dedupe`

**Built:** `_normalize_company_url_for_dedupe` catches `ValueError` on malformed IPv6 URLs (returns `""`). AST-817 consult routing verified on branch base — no consult change.

**Test-child (Hedy):** Betty manifest green @ `9a130a6` — 3 passed, no product fixes.

**Susan UAT:**
- `vet_inflow_discovery` Run → company vet logs, not CSE stale-term loop
- No scheduler crash from `Invalid IPv6 URL`
- Pass → WEBSITE_FOUND or reject → VET_FAILED

