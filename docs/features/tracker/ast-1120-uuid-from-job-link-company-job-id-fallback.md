# AST-1120 — UUID-from-job_link company_job_id fallback before qualify empty-id gate

**Linear:** [AST-1120](https://linear.app/astralcareermatch/issue/AST-1120/uuid-from-job-link-company-job-id-fallback-before-qualify-empty-id)
**Parent:** [AST-1119](https://linear.app/astralcareermatch/issue/AST-1119/fallback-for-company-job-id) — Fallback for company job id
**Publish ref:** `origin/sub/AST-1119/AST-1120-uuid-from-job-link-company-job-id-fallback`

When Ruth’s `qualify_meteorite` parse omits `company_job_id`, the empty-id content gate fails even if a UUID-shaped path segment already sits in `job_link`. This ticket owns the resolve rule (AI wins; else UUID path segment from `job_link`; else empty) and wires it immediately before that gate only — so empty-AI + UUID-in-`job_link` jobs can continue to title/link/JD gates and record a stable external id. Does **not** own Style D found/recorded source logging (**AST-1121**), meteorite create paths, `job_site`, or `qualify_job_listings`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `TRACKER_CONFIG["uuid_path_segment_pattern"]` (UUID-shaped full-segment regex) | utils |
| `src/utils/formatting.py` | Add pure `uuid_path_segment_from_url(url, segment_pattern) -> Optional[str]` | utils |
| `src/core/consult.py` | Add `_resolve_company_job_id`; call it in `qualify_meteorite` `process` immediately before the empty-`company_job_id` gate | core |

No `tests/` / bible / React / data / external / meteorite create / `qualify_job_listings` / debug source logging. Do **not** edit AST-1121’s plan or branch.

## Stage 1: Config pattern + pure URL UUID path helper

**Done when:** `TRACKER_CONFIG` exposes a UUID path-segment regex; `formatting.uuid_path_segment_from_url` returns the rightmost matching path segment (or `None`); neither touches consult apply yet.

1. In `src/utils/config.py`, inside `TRACKER_CONFIG` (after `jd_min_chars` / before or after `jd_prune_rules` — keep the block readable; do not invent a second top-level config dict), add:

```python
    # AST-1120: full path-segment match for UUID-shaped external job ids in job_link.
    "uuid_path_segment_pattern": (
        r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    ),
```

Assert once near other TRACKER asserts if the file already has them for this block; otherwise add a single module-level assert after `TRACKER_CONFIG`:

```python
assert TRACKER_CONFIG["uuid_path_segment_pattern"].startswith("^")
```

⚠️ **Decision — pattern in `TRACKER_CONFIG`, not a Dice host allowlist:** Parent + `astral.standards.no-hardcoded-sets` require UUID shape via config/shared helper constants, not ad-hoc host lists. No `job_site` / vendor gate in this epic.

2. In `src/utils/formatting.py` (pure utils — **must not** import `config.py`; that module already imports formatting), add:

```python
def uuid_path_segment_from_url(url: str, segment_pattern: str) -> Optional[str]:
    """Return the rightmost path segment that fullmatches segment_pattern, else None."""
```

Concrete behavior (execute literally):

- If `(url or "").strip()` is empty → return `None`.
- `from urllib.parse import urlparse, unquote` (module-level imports preferred if not already present).
- `parsed = urlparse(url.strip())`.
- Split `parsed.path` on `/`; skip empty segments.
- Walk segments **right-to-left**; for each, `candidate = unquote(segment).strip()`; if `re.fullmatch(segment_pattern, candidate)` → return `candidate` unchanged (do **not** force lowercase).
- Ignore query string and fragment entirely (never scrape `?…` / `#…` for the id).
- If no segment matches → return `None`.
- Invalid / relative URLs: still parse path; if no match → `None` (do not raise).

⚠️ **Decision — rightmost matching path segment:** Dice/profile URLs put the resource UUID as the last path token; when multiple UUID-shaped segments exist, the last is the job/resource id. Query/fragment junk is out of scope for substring dedupe safety.

⚠️ **Decision — pattern passed as argument:** `formatting.py` must stay free of `config` imports; callers pass `TRACKER_CONFIG["uuid_path_segment_pattern"]`.

**Done when (recheck):** `python3 -c` imports `TRACKER_CONFIG["uuid_path_segment_pattern"]` and `uuid_path_segment_from_url`; Dice example `https://www.dice.com/company-profile/9f704ad3-7a18-506a-bd5e-6a84e73b7c00` returns that UUID; a URL with no UUID path segment returns `None`; `python3 -m py_compile` on both files succeeds.

## Stage 2: Resolve helper + wire before qualify_meteorite empty-id gate

**Done when:** Non-empty AI `company_job_id` is never overwritten; empty AI + UUID-in-`job_link` fills `company_job_id` before the empty-id fail; empty AI + no UUID still fails with `fail_reason = "empty company_job_id"`; meteorite create and other gates unchanged.

1. In `src/core/consult.py`, near other private helpers above `qualify_meteorite` (public functions stay first; helpers grouped — §1.3), add:

```python
def _resolve_company_job_id(ai_company_job_id: str, job_link: str) -> str:
    """Prefer non-empty AI company_job_id; else UUID path segment from job_link; else ''."""
```

Concrete body:

- `ai = (ai_company_job_id or "").strip()` — if non-empty, **return `ai` immediately** (do not inspect `job_link`, do not replace with a URL UUID even when different).
- `link = (job_link or "").strip()` — if empty, return `""`.
- `from src.utils.formatting import uuid_path_segment_from_url` (add to existing formatting import at top if preferred).
- `fallback = uuid_path_segment_from_url(link, TRACKER_CONFIG["uuid_path_segment_pattern"])`.
- Return `fallback` if truthy, else `""`.

⚠️ **Decision — one resolve helper in consult, extract pure in formatting:** Introduces proposed `pattern.identity.url-uuid-path-external-id-fallback` on the agreed apply surface without a parallel ingest path. AST-1121 may reuse `_resolve_company_job_id` / `uuid_path_segment_from_url` for source classification; this ticket does **not** add found-source Style D lines.

2. In `qualify_meteorite`’s nested `process(input_job, response_job, cfg)`, **immediately after** the existing strips of `company_job_id` / `job_title` / `job_link` / `jd_text` and **immediately before** `fail_reason = None` / the `if not company_job_id:` empty-id gate, replace the bare AI strip assignment path as follows:

- Keep reading AI fields exactly as today:

```python
company_job_id = (response_job.get("company_job_id") or "").strip()
job_title = (response_job.get("job_title") or "").strip()
job_link = (response_job.get("job_link") or "").strip()
jd_text = (response_job.get("jd_text") or "").strip()
```

- Compute the fallback URL (response link first, else input row link — never company `job_site`):

```python
link_for_id = job_link or (input_job.get("job_link") or "").strip()
company_job_id = _resolve_company_job_id(company_job_id, link_for_id)
```

- Leave the rest of `process` unchanged: empty-id fail still uses `fail_reason = "empty company_job_id"` and the same `cfg["fail_state"]` transition; title / `job_link` http / `jd_text` gates unchanged; success `parsed_job["company_job_id"]` uses the resolved value; existing debug/info lines may show the resolved id (do **not** add AI-vs-UUID source labels — **AST-1121**).

⚠️ **Decision — `link_for_id` = response `job_link` else input `job_link`:** Assemble sends the DB row’s link to Ruth; if the model empties `job_link` while omitting `company_job_id`, the ingest URL still carries the UUID. Never read company `job_site`. Recording of `job_link` on the job row still uses response `job_link` as today (this ticket does not change the link gate or recorded link field).

⚠️ **Decision — wire only in `qualify_meteorite` `process`:** Parent AC + Boundaries: apply surface is the empty-`company_job_id` content gate only. Do not touch `create_meteorite_job`, gazer ingest, or `qualify_job_listings`.

**Done when (recheck):** Manual trace of the three AC paths in `process` logic:

1. AI `company_job_id="abc"` + Dice UUID in link → recorded `"abc"`.
2. AI empty + Dice URL → recorded UUID; does not set `fail_reason = "empty company_job_id"`.
3. AI empty + `https://example.com/jobs/no-uuid-here` → still `empty company_job_id` fail.

`python3 -m py_compile` on `src/core/consult.py` succeeds. No new debug-contract source lines.

## Self-Assessment

**Scope:** `Single-Component` — config literal + one pure formatting helper + one consult resolve helper wired at a single gate in `qualify_meteorite`.

**Conf:** `high` — gate and fields already exist in `consult.qualify_meteorite`; change is a deterministic prefer-AI-else-UUID strip before the existing empty check, reusing claim/process/release unchanged.

**Risk:** `Medium` — wrong UUID selection or overwriting AI ids would poison `company_job_id` substring dedupe and identity triples; mitigated by AI-first rule, path-segment-only UUID fullmatch, and no create-path edits.

## Rules check (ASTRAL_CODE_RULES)

| Rule | Status |
|------|--------|
| §1.3 DRY / public-then-helpers | Resolve once in `_resolve_company_job_id`; extract once in formatting; helpers below publics in consult |
| §1.4 / §2.1 no-hardcoded-sets / config SoT | UUID regex lives in `TRACKER_CONFIG`; formatting takes pattern arg |
| §1.5.1 debug-contract-gated | **Out of scope** — no new found/recorded source logging (AST-1121) |
| §2.4 claim-process-release | Fallback inside existing qualify `process`; no parallel claim path |
| §2.4.1 entity-agent-responses | AI value still from RESPONSE decode; fallback is post-decode apply only |
| §2.6 state machine | Same `fail_state` / `pass_state` transitions; no new states |
| §3.3 import direction | `consult` → `utils` only for helper; `formatting` stays pure (no config import) |
| §3.6 spikes | N/A — no spike deliverables |

No plan conflicts requiring `conf-!!-NONE`.

## Review

**Publish ref:** `origin/sub/AST-1119/AST-1120-uuid-from-job-link-company-job-id-fallback`
**Tip:** `ba8254f2`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `ab433398` | `TRACKER_CONFIG["uuid_path_segment_pattern"]` + `formatting.uuid_path_segment_from_url` |
| 2 | `ba8254f2` | `_resolve_company_job_id` + wire before `qualify_meteorite` empty-id gate |
