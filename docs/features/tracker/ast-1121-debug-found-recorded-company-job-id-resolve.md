# AST-1121 — Debug found/recorded for company_job_id resolve

**Linear:** [AST-1121](https://linear.app/astralcareermatch/issue/AST-1121/debug-foundrecorded-for-company-job-id-resolve-fallback-for-company)
**Parent:** [AST-1119](https://linear.app/astralcareermatch/issue/AST-1119/fallback-for-company-job-id) — Fallback for company job id
**Publish ref:** `origin/sub/AST-1119/AST-1121-debug-found-recorded-company-job-id-resolve`

After AST-1120’s resolve rule, the touched `qualify_meteorite` `debug=True` apply path already emits Style D index + `|` detail with resolved/recorded `company_job_id` values, but does **not** label **how** the id was found. This ticket adds found-source observability only: `AI` vs `UUID-from-job_link` vs `neither`, the `job_link` used when falling back, and recorded `company_job_id`. No resolve-rule or gate-behavior change.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/consult.py` | In `qualify_meteorite` `process`, classify found source from pre-resolve AI strip + post-resolve id; enrich existing `debug=True` fail/pass `|` detail lines (and keep Style D `debug_index`) | core |

No `tests/` / bible / config / formatting / meteorite create / `qualify_job_listings` / resolve-rule edits. Do **not** change `_resolve_company_job_id` return semantics or empty-id gate outcomes.

## Stage 1: Found-source Style D detail on qualify_meteorite apply

**Done when:** With `debug=True`, each processed job’s Style D `|` detail shows `source=AI` | `source=UUID-from-job_link` | `source=neither`; when source is `UUID-from-job_link`, detail includes the `job_link` used for fallback (`link_for_id`); pass path still shows recorded `company_job_id`; `debug=False` adds no new lines; resolve/gate behavior unchanged.

1. In `src/core/consult.py`, inside `qualify_meteorite`’s nested `process(input_job, response_job, cfg)`, **keep** the AST-1120 resolve wire exactly as it is today:

```python
company_job_id = (response_job.get("company_job_id") or "").strip()
job_title = (response_job.get("job_title") or "").strip()
job_link = (response_job.get("job_link") or "").strip()
jd_text = (response_job.get("jd_text") or "").strip()
link_for_id = job_link or (input_job.get("job_link") or "").strip()
company_job_id = _resolve_company_job_id(company_job_id, link_for_id)
```

Before calling `_resolve_company_job_id`, bind the pre-resolve AI strip to a local (do not change what is passed into resolve):

```python
ai_company_job_id = (response_job.get("company_job_id") or "").strip()
# … job_title / job_link / jd_text strips unchanged …
link_for_id = job_link or (input_job.get("job_link") or "").strip()
company_job_id = _resolve_company_job_id(ai_company_job_id, link_for_id)
```

⚠️ **Decision — classify from AI strip + resolved id, do not change `_resolve_company_job_id` signature:** AST-1120 already owns prefer-AI-else-UUID-else-empty. Source labels are derived for debug only: non-empty `ai_company_job_id` → `AI`; else non-empty resolved `company_job_id` → `UUID-from-job_link`; else `neither`. Recomputing via `uuid_path_segment_from_url` is unnecessary and would drift if resolve ever gains another branch.

2. Still inside `process`, after resolve and **only for use under existing `if debug:` blocks**, compute:

```python
if ai_company_job_id:
    id_source = "AI"
elif company_job_id:
    id_source = "UUID-from-job_link"
else:
    id_source = "neither"
```

Literal label strings must be exactly `AI`, `UUID-from-job_link`, and `neither` (parent AC / sibling plan wording).

3. Enrich the **existing** content-fail `debug_detail` (still under `if fail_reason:` / `if debug:`) so the `|` line includes found source and, when falling back, the link used. Replace the current fail detail string with one built as follows (keep `gate=` / title / link / jd_chars already present):

- Always include `found source={id_source}` and `company_job_id={company_job_id!r}` (resolved value, same as today).
- When `id_source == "UUID-from-job_link"` **or** `id_source == "neither"`, also include `fallback_job_link={link_for_id!r}` (the URL consulted for UUID fallback — response `job_link` else input `job_link`).
- When `id_source == "AI"`, do **not** require `fallback_job_link=` (AI won; fallback was not used). Other existing fields (`gate=`, `title=`, `link=`, `jd_chars=`) stay.

Concrete fail detail shape (single `debug_detail` call; one line):

```python
# AI fail (other gates) example fragments:
#   gate=… found source=AI company_job_id='…' title=… link=… jd_chars=…
# UUID fallback then other-gate fail:
#   gate=… found source=UUID-from-job_link fallback_job_link='…' company_job_id='…' …
# neither (empty-id fail):
#   gate=empty company_job_id found source=neither fallback_job_link='…' company_job_id='' …
```

Keep the existing `debug_index` header on the fail path (same `func` / identifier / outcome). Do **not** add a second index header.

4. Enrich the **existing** pass-path `debug_detail` (after `initialize_job` + `get_job` recorded snapshot) the same way:

- Keep `debug_index` as today.
- Prefixed found half: `found source={id_source}` then, if `id_source` is `UUID-from-job_link`, `fallback_job_link={link_for_id!r}`, then existing found fields (`company_job_id`, `title`, `link`, `jd_chars`).
- Keep the `|` recorded half exactly as today (`recorded company_job_id=… title=… link=… jd_chars=…`).
- When `id_source == "AI"`, omit `fallback_job_link=`.
- When `id_source == "neither"` cannot occur on the pass path after a successful empty-id gate — do not special-case pass for `neither`.

⚠️ **Decision — extend existing Style D lines, do not add parallel debug surfaces:** Input-job Style D at the top of `qualify_meteorite` stays untouched. Only the per-job apply `process` fail/pass details gain source labels. No new `logger.info("[DEBUG]")`, no config keys, no changes when `debug=False`.

⚠️ **Decision — `fallback_job_link` is `link_for_id`, not company `job_site`:** Matches AST-1120’s resolve input. Response `job_link` used for the http gate / recorded link is still logged as today’s `link=`; `fallback_job_link=` is only the URL fed to resolve when source is not `AI`.

5. Do **not** edit `_resolve_company_job_id`, `uuid_path_segment_from_url`, `TRACKER_CONFIG`, meteorite create, or `qualify_job_listings`. Do **not** change fail_reason strings, state transitions, or `parsed_job` contents.

**Done when (recheck):** Manual trace under `debug=True`:

1. AI non-empty → detail has `found source=AI` and `recorded company_job_id` matching AI; no `fallback_job_link=`.
2. AI empty + UUID in `link_for_id` → `found source=UUID-from-job_link`, `fallback_job_link=` that URL, recorded id = UUID.
3. AI empty + no UUID → fail detail `found source=neither` + `fallback_job_link=`; still `gate=empty company_job_id`.
4. `debug=False` → no new contract lines (existing non-debug `logger.info` paths unchanged).

`python3 -m py_compile src/core/consult.py` succeeds.

## Self-Assessment

**Scope:** `minor` — one apply-path debug enrichment in `consult.qualify_meteorite` `process`; no new modules or resolve behavior.

**Conf:** `high` — AST-1120 already wires resolve and Style D found/recorded values; this ticket only labels source from the pre-resolve AI strip + resolved id using parent AC vocabulary.

**Risk:** `low` — observability only under `debug=True`; wrong labels would mislead operators but cannot change gate outcomes if resolve call and fail/pass branches stay untouched.

## Code Rules check

| Rule | Notes |
|------|-------|
| §1.5.1 debug-contract-gated | New/changed detail only inside existing `if debug:` blocks; Style D index + `\|` detail; no ungated noise |
| §1.3 DRY / public-then-helpers | No new public API; classification is three locals next to existing debug blocks (not a second resolve implementation) |
| §2.1 config | No new config — labels are fixed AC vocabulary |
| §3.3 imports | No new imports required |
| in-scope-only | Touched surface = `qualify_meteorite` apply debug only; resolve rule remains AST-1120 |

## Statute frame (Linear description)

**In scope**

- [ ] `astral.standards.debug-contract-gated` — Style D found source + recorded `company_job_id` (and fallback `job_link` when used) on touched `qualify_meteorite` apply path when `debug=True`

**Considered but excluded**

- [ ] Resolve rule / empty-id gate wire — AST-1120 owns `_resolve_company_job_id` and gate placement; this ticket must not change outcomes
- [ ] Meteorite create / gazer ingest leaving `company_job_id` empty — out of Boundaries
- [ ] `qualify_job_listings` — parent forbids expansion; no empty-id content fail gate there today
- [ ] Company `job_site` / non-`job_link` URLs — never used for fallback or fallback debug link

## Review

**Publish ref:** `origin/sub/AST-1119/AST-1121-debug-found-recorded-company-job-id-resolve`
**Tip (pre-review):** `2ea3894d` (`merge-tests` + Betty coverage)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `2fc5bbe7` | Style D found source + optional `fallback_job_link` on `qualify_meteorite` apply fail/pass |
| tests | `9b31527c` / `2ea3894d` | Betty Style D source-label coverage + `merge-tests` |

### Radia — code-rubric.v1 (`[code-rubric] revision=1`)

**Overall:** DISCUSS (C4 stragglers only; no product fix-now)

**What's solid**
- Labels `AI` / `UUID-from-job_link` / `neither` from pre-resolve AI strip + resolved id; no second resolve path.
- Enrichment only inside existing `if debug:` `debug_index` / `debug_detail` (pass keeps `|` recorded half); `debug=False` unchanged.
- Resolve/gate outcomes untouched; no create / `job_site` / `qualify_job_listings` creep.

**Issues**
- **discuss (straggler):** Joan plan-time Excluded → in-scope on tip vs `origin/dev` (mostly sibling AST-1120 + plan/tests on tip): `astral.debug.spikes-under-debug-dir`, `astral.dispatch.seed-auto-false`, `astral.docs.features-single-file-per-ticket`, `astral.git.engineer-test-tree-ban`, `astral.layers.ui-config-driven-business-logic`, `astral.seed.agent-tables-in-repo-json`, `astral.seed.archie-catalog-wins`, `astral.seed.operator-rows-stay-deleted`, `astral.seed.other-via-coverage-join`, `astral.standards.utils-data-late-import-only`, `astral.ui.single-gunicorn-worker` — all scored `conforms`; no product action.

**Recommended actions**
- Resolve-child: no code changes required for stragglers.
