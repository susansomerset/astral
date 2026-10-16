# AST-2253 — Search credentials from the candidate

Linear: [AST-2253](https://linear.app/astralcareermatch/issue/AST-2253/search-credentials-from-the-candidate-manage-candidate-secrets-in-railway)
Parent: [AST-2246](https://linear.app/astralcareermatch/issue/AST-2246/manage-candidate-secrets-in-railway)
Publish ref: `sub/AST-2246/AST-2253-search-candidate-secrets`

CSE search and timesheet receipt fetch use the candidate's search secrets. `search_google_cse` takes the key and engine id from the caller. Hydrate already puts those values on `candidate_api_keys` under catalog ids `google_cse_api_key` and `google_cse_id`. This ticket does not write Railway variables, status rows, or the Admin page, and it does not change the CSE vendor.

## Scope check

This ticket's Scope names:

- `src/external/google_cse.py` — credentials come from the caller, not `GOOGLE_CSE_*`
- `src/core/timesheets.py` — stop the empty-key stub; resolve the search secret the same way as an LLM key
- `src/core/roster.py` — `resolve_company_website` and `run_inflow_discovery_batch` pass the candidate's key and engine id; warn with candidate id and secret id, not the value, when one is missing
- `scripts/spikes/ast489_google_cse_company_search_spike.py` — call the client with an explicit key and engine id, not process-wide `GOOGLE_CSE_*`

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/external/google_cse.py` | `search_google_cse` takes `api_key` and `cx`. Delete the `os.environ` reads and the unused `os` import. | external |
| `src/core/timesheets.py` | Timesheet fetch looks up `google_cse_api_key` and skips with the existing missing-key warning when it is absent. | core |
| `src/core/roster.py` | Both CSE call sites pass the hydrated secrets or warn and do not call. | core |
| `scripts/spikes/ast489_google_cse_company_search_spike.py` | Required `--api-key` and `--cx`, passed into the client. Unpack `result["hits"]`. | scripts |

## Stage 1: CSE client takes caller credentials

**Done when:** `search_google_cse` has no `os.environ` read, and a call with `api_key` and `cx` is what reaches the HTTP `key` and `cx` params. A blank `api_key` or `cx` raises `ValueError` before any HTTP call.

1. In `src/external/google_cse.py`, delete `import os`.
2. Change `search_google_cse` to:

```python
def search_google_cse(
    query: str,
    *,
    api_key: str,
    cx: str,
    max_results: int = 10,
    site_filters: Sequence[str] | None = None,
    days: int | None = None,
    pace_detail: Callable[[str], None] | None = None,
) -> GoogleCseSearchResult:
```

3. Replace the docstring sentence `Credentials: GOOGLE_CSE_API_KEY and GOOGLE_CSE_ID via os.environ (no fallbacks).` with `Credentials: caller passes api_key and cx. This function does not read the environment.`
4. Delete the `try` / `os.environ["GOOGLE_CSE_API_KEY"]` / `os.environ["GOOGLE_CSE_ID"]` / `KeyError` block. After `require_controlled_external_io("google_cse.search_google_cse")`, if `not (api_key or "").strip()` or `not (cx or "").strip()`, raise `ValueError("api_key and cx are required")`. Do not log. The existing `params["key"]` and `params["cx"]` keep using those arguments.
5. Do not change `get_receipt`. It still ignores its `api_key` argument.

## Stage 2: Timesheet fetch uses the catalog key

**Done when:** A `google_cse` timesheet group with no `candidate_api_keys["google_cse_api_key"]` logs the missing-key warning and does not call `get_receipt`. A present key is passed as the second argument. The code does not pass `""`.

1. In `run_fetch_timesheet` in `src/core/timesheets.py`, delete the branch that sets `key = _api_key_for_server(cid, provider) or ""` when `provider == TIMESHEET_SEARCH_SERVER_ID`.
2. For every provider, including `TIMESHEET_SEARCH_SERVER_ID`, resolve the key then warn and skip when it is missing. The lookup id for `TIMESHEET_SEARCH_SERVER_ID` is the catalog id `"google_cse_api_key"`. Every other provider keeps `_api_key_for_server(cid, provider)`.

```python
secret_id = "google_cse_api_key" if provider == TIMESHEET_SEARCH_SERVER_ID else provider
key = _api_key_for_server(cid, secret_id)
if not key:
    logger.warning(
        "fetch_timesheet | candidate %s has no API key for server %s — skipping %s id(s)",
        cid, secret_id, len(ids),
    )
    summary["total_failed"] += len(ids)
    continue
```

3. Do not log `key`. Do not read `GOOGLE_CSE_API_KEY` or `GOOGLE_CSE_ID`.

⚠️ **Decision:** The timesheet receipt path has one key argument. That key is catalog id `google_cse_api_key`. The engine id is not a `get_receipt` input. `get_receipt` stays a stub that ignores the key.

## Stage 3: Roster passes both secrets

**Done when:** `resolve_company_website` and `run_inflow_discovery_batch` call `search_google_cse` with `api_key` and `cx` from that candidate's hydrated `candidate_api_keys`. If either secret is missing, each missing id is one `logger.warning` with the candidate id and the secret id, the value is not logged, and `search_google_cse` is not called.

1. In `src/core/roster.py`, add this helper above `resolve_company_website`. Use `database.get_candidate` (that parse path already runs `hydrate_candidate_secrets`). Import `get_candidate` on the existing `src.data.database` import.

```python
def _search_credentials(candidate_id: str) -> tuple[str, str] | None:
    """(api_key, cx) from hydrated candidate_api_keys, or None after a warning per missing id."""
    cid = (candidate_id or "").strip()
    row = get_candidate(cid) if cid else None
    keys = (row or {}).get("candidate_api_keys") or {}
    found = {
        "google_cse_api_key": keys.get("google_cse_api_key") or "",
        "google_cse_id": keys.get("google_cse_id") or "",
    }
    missing = [secret_id for secret_id, value in found.items() if not value]
    if not missing:
        return found["google_cse_api_key"], found["google_cse_id"]
    for secret_id in missing:
        logger.warning(
            "%s secret %s is missing — this search is not running",
            cid or "-",
            secret_id,
        )
    return None
```

2. In `resolve_company_website`, immediately before the `logger.debug("Calling search_google_cse: query=%r", query)` line, set `cid = (entity.get("candidate_id") or "").strip()` and `creds = _search_credentials(cid)`. If `creds` is `None`, return `{"success": False, "state": None, "error": None}` and do not call `search_google_cse`. Otherwise unpack `api_key, cx = creds` and pass `api_key=api_key, cx=cx` into the existing `search_google_cse` call. Leave the `except (RuntimeError, ValueError)` handler as it is.
3. In `run_inflow_discovery_batch`, at the start of the `for term in terms` loop, before `logger.debug("Calling search_google_cse: query=%r", term)`, call `creds = _search_credentials(candidate_id)`. If `creds` is `None`, add `1` to `errors` and `continue`. Otherwise unpack and pass `api_key` and `cx` into that loop's `search_google_cse` call. Leave the existing `except` handler as it is.

⚠️ **Decision:** Both call sites re-read through `database.get_candidate` so the map is the hydrated one (`google_cse_api_key` / `google_cse_id`), including when the company row only has `candidate_id`.

## Stage 4: Spike passes explicit arguments

**Done when:** `scripts/spikes/ast489_google_cse_company_search_spike.py` has no read of `GOOGLE_CSE_API_KEY` or `GOOGLE_CSE_ID`. Running it without `--api-key` and `--cx` exits from argparse. A run with both flags passes those strings into `search_google_cse` and prints `result["hits"]`.

1. Add required arguments to `parse_args`:

```python
parser.add_argument("--api-key", required=True, help="CSE API key passed to search_google_cse.")
parser.add_argument("--cx", required=True, help="CSE engine id passed to search_google_cse.")
```

2. Change `run_search` to take `api_key: str` and `cx: str`, and call:

```python
result = search_google_cse(
    query,
    api_key=api_key,
    cx=cx,
    max_results=max_results,
    site_filters=site_filters or None,
    days=days,
)
hits = result["hits"]
```

3. Pass `args.api_key` and `args.cx` from `main` into every `run_search` call, including the built-in exemplar runs.
4. Replace the module docstring usage block so the examples include `--api-key` and `--cx`, and delete the sentence that says to set `GOOGLE_CSE_API_KEY` and `GOOGLE_CSE_ID` in the environment. Leave `load_dotenv` as it is. Do not read those two env names in this file.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2253
**Overall:** APPROVED
**Corpus:** 65a2864973ecf09fd57732c2cfc9a4e1ff3e0b91
**Publish ref:** `sub/AST-2246/AST-2253-search-candidate-secrets` @ `f599dc3b639c5493ae9b5d4086929df17c64b6ff`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.warning | A | | |
| new candidate-secret pattern (pending Archie) | B | | |

## Traceability

`6 → Stages 1–3 (search_google_cse has no GOOGLE_CSE_* reads; roster/timesheet paths pass hydrated google_cse_api_key / google_cse_id); Stage 4 keeps spike off process env`

## Findings

### discuss — Canon Scope gap

- **Severity:** discuss
- **Location:** Stage 3 — `_search_credentials` uses `database.get_candidate`
- **Finding:** `astral.layers.import-direction` and `astral.standards.data-raises-caller-logs` are not on the frozen Citations list. Core → data import is conforming; warnings live in core, not data.
- **Recommendation:** Archie may amend Canon Scope for Radia parity; do not score off-list here.

### discuss — Pattern not in corpus

- **Severity:** discuss
- **Location:** Citations / Stages 1–3
- **Finding:** Candidate-secret pattern still pending Archie with no canon file.
- **Recommendation:** Plan matches epic intent (caller-supplied CSE credentials keyed off hydrate catalog ids).

### discuss — Missing creds behavior on resolve hop

- **Severity:** discuss
- **Location:** Stage 3 step 2 — `creds is None` → `success: False`, `state: None`, `error: None`
- **Finding:** No CSE call and warnings already emitted; company may remain in a pre-search state without a new transition.
- **Recommendation:** Acceptable if product treats missing search secrets like “search did not run”; confirm in UAT that this matches dispatch expectations (not a plan rewrite).

### acceptable — All `search_google_cse` call sites covered

- **Severity:** acceptable
- **Location:** Files Changed vs repo
- **Finding:** Production callers are only `roster.py` (two sites) and the AST-489 spike; plan updates all three. No orphan caller left on `GOOGLE_CSE_*` inside the client after Stage 1.
- **Recommendation:** None.

### acceptable — Roster + spike in scope

- **Severity:** acceptable
- **Location:** Linear `## Scope` vs parent child #4 bullet list
- **Finding:** Ticket Scope explicitly includes `roster.py` and the spike; plan matches Linear, not only the shorter parent dispatch blurb.
- **Recommendation:** None.

### acceptable — Depends on AST-2251 hydrate

- **Severity:** acceptable
- **Location:** Stage 3 helper
- **Finding:** Assumes `candidate_api_keys` carries `google_cse_api_key` / `google_cse_id` after hydrate.
- **Recommendation:** Land status/hydrate sibling before this child.

context_tokens≈52000

[plan-rubric] PROCEED (Commit: f599dc3) Candidate CSE credentials plan

## Review stub (build-child)

**Built:** `ae8d354d6c0ccdbfbab3c2836328f91aa0446c7a` on `sub/AST-2246/AST-2253-search-candidate-secrets`

CSE client `1f1760f87`. Timesheet lookup `75be4ede9`. Roster call sites `387447915`. Spike flags `ae8d354d6`. No test-tree edits. Missing search secrets warn with candidate id and secret id and do not include the value.

## Radia review

[code-rubric]
**Ticket:** AST-2253
**Publish ref:** `420ea9e36a333ce1534faf42b3aca9bd25275326` (`origin/sub/AST-2246/AST-2253-search-candidate-secrets`)
**Corpus:** `65a2864973ecf09fd57732c2cfc9a4e1ff3e0b91`
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.warning | A | | |
| new candidate-secret pattern (pending Archie) | A | | |

## Column diff vs plan stage

| slug | Joan | Radia | note |
|------|------|-------|------|
| new candidate-secret pattern (pending Archie) | B | A | Plan-stage B reflected pending corpus; diff delivers AC 6 (caller credentials, hydrate catalog ids on roster/timesheet paths). |

(stat.logging.warning: aligned at A)

## Frame diff

- [x] **Acceptance criteria — AC 6:** Confirm no production `search_google_cse` caller remains on process-wide `GOOGLE_CSE_*` (client + roster + spike only).
- [x] **Plan Stage 3 — missing creds on `resolve_company_website`:** UAT confirms `success: False`, `state: None`, `error: None` with warnings only is acceptable when search secrets are unset (Joan discuss).

## Findings

### advisory — Epic rollup in three-dot diff

- **Location:** Diff vs `origin/dev` includes AST-2250–2251 product/tests/docs (`railway.py`, `database.py`, `candidate.py`, migration script, etc.)
- **Finding:** Publish ref stacks prior siblings; expected for serial epic children on one sub tip.
- **Recommendation:** Note once in the issue doc; score AST-2253 only on Scope files (`google_cse.py`, `timesheets.py`, `roster.py`, AST-489 spike).

### advisory — Off-list statutes (do not score)

- **Location:** `_search_credentials` → `get_candidate`; warnings in `roster.py` / `timesheets.py`
- **Finding:** `astral.layers.import-direction` and `astral.standards.data-raises-caller-logs` are not on the frozen Citations list; warnings stay in core, data does not log on read.
- **Recommendation:** Archie may widen parent Canon Scope; do not insert ids on this pass.

### discuss — Missing search creds on website resolve

- **Severity:** discuss
- **Location:** `resolve_company_website` when `_search_credentials` returns `None`
- **Finding:** No CSE call; per-id warnings already emitted; return shape leaves company without a new transition.
- **Question (@susan):** Is this equivalent to “search did not run” for dispatch/UAT?
- **Default:** Treat as acceptable soft skip (same as Joan plan finding); no code change unless UAT shows companies stuck in a state that needs an explicit error transition.

### advisory — Inflow loop re-fetches creds per term

- **Location:** `run_inflow_discovery_batch` — `_search_credentials(candidate_id)` inside `for term in terms`
- **Finding:** Matches plan Stage 3 step 3; redundant DB reads but within ticket scope.
- **Recommendation:** None unless a later perf pass wants caching (out of scope).

## What's solid

- **`search_google_cse`:** No `os` / `os.environ`; blank `api_key` or `cx` → `ValueError` before HTTP; params use caller arguments (`tests/component/external/test_google_cse.py` asserts env vars are not used when caller passes keys).
- **`timesheets.py`:** `google_cse` provider uses catalog id `google_cse_api_key` via `_api_key_for_server`; missing key uses existing warning shape and skips (no empty-key stub).
- **`roster.py`:** `_search_credentials` warns per missing secret id without values; both CSE sites pass `api_key` and `cx` into `search_google_cse`.
- **Spike:** Required `--api-key` / `--cx`; unpacks `result["hits"]`; docstring examples updated.
- **Tests:** `TestAst2253SearchCredentials`, revised timesheet/CSE tests, roster autouse fixture to avoid breaking legacy mocks.

## Recommended actions (downstream only — not in Radia lane)

- Chuckles: append this artifact to `docs/features/foundation/ast-2253-search-candidate-secrets.md`, commit `docs(AST-2253): Radia review — clean`, post slim upshot `--as radia`, move to **Review Posted**.
- UAT: tick frame-diff rows; if Susan is silent on the resolve-hop **Default**, proceed without blocking.

```
[code-rubric] PROCEED (Commit: 420ea9e) Candidate CSE from hydrate
```

context_tokens≈42000

## Resolution

2026-10-16 — Radia overall CLEAN. No fix-now items. No product edits.

Discuss "Missing search creds on website resolve": Susan had not answered. Took the finding **Default** — soft skip stays (`success: False`, `state: None`, `error: None`, warnings only, no CSE call). No code change.

Advisory: three-dot diff includes sibling AST-2250–2251; this child is scored on `google_cse.py`, `timesheets.py`, `roster.py`, and the AST-489 spike only. Off-list statutes stay off the citation list. Inflow re-fetch per term stays as Stage 3 wrote it. Frame-diff AC 6 and Stage 3 rows ticked. Production `search_google_cse` callers are roster (two sites) and the spike; the client does not read `GOOGLE_CSE_API_KEY` / `GOOGLE_CSE_ID`.
