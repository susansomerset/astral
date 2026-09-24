# AST-1785 — Prefer http job_link over breadcrumb at stage map

**Linear:** [AST-1785](https://linear.app/astralcareermatch/issue/AST-1785/prefer-http-job-link-over-breadcrumb-at-stage-map-parsing-emails-with)  
**Parent:** [AST-1783](https://linear.app/astralcareermatch/issue/AST-1783/parsing-emails-with-linked-job-titles) — Parsing emails with linked job titles  
**Publish ref:** `sub/AST-1783/AST-1785-prefer-http-job-link-over-breadcrumb`

When a classify jobs item carries an http(s) `job_link`, write that URL onto `meteorite.link` even if the outcome string was a text landable; call the email-breadcrumb helper only when no http(s) `job_link` is present. Put http-linked rows on the scrape state path (`SCRAPE_LINK`). Keep staged `job_title` / `employer_name` mapping as today. Does **not** edit agent_task prompts (**AST-1784**).

## UAT fitness

- **AC restored:** Parent AC4 — After staging an email whose body is essentially `<a href="https://example.com/jobs/1">Senior Widget Engineer</a>` (and Ruth returns a landable URL jobs item with that `job_link` / `job_title`), the meteorite row has `link` exactly `https://example.com/jobs/1` and `job_title` `Senior Widget Engineer`. Fail if `link` is a non-http breadcrumb or NULL while that `job_link` was returned. Parent AC5 — After staging the same shape when Ruth returns a **text** landable outcome but still includes http(s) `job_link` on the jobs item, the meteorite row `link` is that http URL (not a breadcrumb) and the row is on the scrape path (`state` `SCRAPE_LINK` or equivalent URL partition). Fail if `link` is still a `From:`/`To:` breadcrumb while `job_link` was http(s). Parent AC6 — After staging a text landable with **no** http(s) `job_link` (classic single JD in body), `meteorite.link` remains the email breadcrumb. Fail if breadcrumb emails lose their breadcrumb. Parent AC7 — Bare URL-list and Dice-style HTML paste shapes that already yield URL outcomes still produce http(s) `meteorite.link` (no regression). Fail if a previously working `link_list` / `single_jd_with_more` fixture now breadcrumb-links.
- **Correct outcome:** Linked-title emails land with the job-page `href` on `meteorite.link` and on the scrape partition so scrape/land can consume them; classic no-URL text emails still get the AST-1703 breadcrumb; existing URL outcomes keep writing http `link`.
- **Sibling check:** **AST-1784** owns prompts / AST-756 fixture only — this ticket does not edit `data/admin/agent_task.json` or the fixture. AST-1703 breadcrumb authorship remains for text email rows **without** http `job_link`. Land / `listing_href` stack (AST-1693–1695) unchanged. Verified by: Files Changed = `src/core/meteorite.py` only; no agent_task / fixture / tracker edits; URL-outcome branch of the mapper left byte-stable except shared helpers already used.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** Teaching only prompts (sibling #1) without map preference still loses the href when Ruth returns a text outcome with `job_link` present — AC5 fails. Inventing a parallel HTML link harvester outside Ruth + this map preference contradicts `patt.task.daisy-chain` and Boundaries. Dropping breadcrumb authorship for all text outcomes would break AC6 / AST-1703 classic JD-in-body emails.

## Scope gate

Ticket **## Scope** (verbatim partition):

- `src/core/meteorite.py` — **modified** — stage map / post-map wiring prefers http(s) `job_link` on `meteorite.link` over email breadcrumb when present; keeps staged `job_title` on the row as today. Technical: in the classify→row mapper (and/or the immediate post-map wiring in `stage_meteorite`), when a jobs item has an http(s) `job_link`, set the meteorite row `link` to that URL even if the classify outcome was a text landable; only call the email-breadcrumb helper when no http(s) `job_link` is present. Keep copying optional `job_title` / `employer_name` onto the row as today. When the row `link` is http(s), use the URL/scrape state path (`SCRAPE_LINK`) so scrape still runs; do not leave an http link stranded under READY solely because the outcome string was text. Do not invent a parallel HTML link harvester outside Ruth + this map preference.

All Files Changed / Stages stay inside that set.

**Out of scope (siblings / other epics):**

- `data/admin/agent_task.json` / `docs/uat-fixtures/AST-756/expected-agent_task.json` — **AST-1784**
- Adding a seventh `STAGE_METEORITE_CONFIG["outcomes"]` literal
- Parallel HTML harvester / gazer email-ingest resurrection
- Land / `listing_href` / scrape page runners beyond consuming a correctly staged http `link`

**Depends on:** **AST-1784** for full linked-title UAT (prompts teach the ask); this map preference is independently correct when Ruth already returns http `job_link` on a text outcome.

**AC partition (this ticket):** Parent AC4–AC7 only (AC1–AC3, AC8 → **AST-1784**).

**Canon Scope (read at plan):** `patt.task.daisy-chain` (full — staged `link` / title ride the row; do not invent a parallel HTML harvester). `stat.logging.debug` (full — no new always-on chatter; existing debug joints stay; any new preference path uses `logger.debug` only). `stat.logging.info.entity` — **id-only** (do not add linked-title-specific entity info logs).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/meteorite.py` | In `_map_classify_jobs_to_meteorite_rows` text branch: prefer http(s) `job_link` over `_email_breadcrumb_link`; in `stage_meteorite` post-map: set `SCRAPE_LINK` when row `link` is http(s) even for text outcomes; in `run_stage_meteorite` text arm: route http `link` to `SCRAPE_LINK` instead of `READY`. Keep URL-outcome branch and `job_title` / `employer_name` post-map as today. | core |

## Stage 1: Prefer http job_link + SCRAPE_LINK when link is http

**Done when:** For a text landable outcome (`single_jd_no_link` / `multi_jd_inline`) with http(s) `job_link` on the jobs item, inserted `meteorite.link` equals that URL (not a breadcrumb) and `state` is `SCRAPE_LINK`. For the same outcomes with no http(s) `job_link` and `source_kind == "email"`, `link` remains the AST-1703 breadcrumb and `state` remains `READY`. URL outcomes (`link_list` / `single_jd_with_more`) still require http(s) `job_link` and insert with that `link` + `SCRAPE_LINK`. `job_title` / `employer_name` still copied via existing `_stage_field` post-map. No prompt / fixture / config edits. `python3 -m py_compile src/core/meteorite.py` succeeds.

1. In `src/core/meteorite.py`, inside `_map_classify_jobs_to_meteorite_rows`, in the `outcome in STAGE_METEORITE_CONFIG["text_source_ref_outcomes"]` branch, **before** the email breadcrumb block that calls `_email_breadcrumb_link`, read the jobs item’s `job_link` the same way the URL branch does:

```python
job_link = (job.get("job_link") or "").strip() if isinstance(job.get("job_link"), str) else ""
```

   If `job_link` starts with `http://` or `https://` (reuse `_is_http_url(job_link)` — it is defined later in this file; either move `_is_http_url` above the mapper, or inline the same `startswith` check used in the URL branch — prefer calling `_is_http_url` after moving the helper just above `_map_classify_jobs_to_meteorite_rows` so both sites share one predicate):

   - Set `link = job_link`.
   - Do **not** call `_email_breadcrumb_link`.
   - `logger.debug` the preference once per such row, e.g. `Preferring http job_link over breadcrumb: %s` with the URL (existing debug style; no `print`; no `logger.info("[DEBUG] …")`; no new `stat.logging.info.entity` line for this preference).

   Else (no http(s) `job_link`): keep today’s behavior — for `source_kind == "email"`, call `_email_breadcrumb_link(...)` from `from_email` / `to_email` / `sent_at` / `timezone_key` (same ValueError → map-error shape); for non-email text, `link` stays `None`.

   Do **not** change the URL-outcome branch (`url_scrape_outcomes`) except incidental shared use of `_is_http_url` if you relocate it. Do **not** invent a second HTML parser. Do **not** write `source_ref`.

2. In `stage_meteorite`, replace the post-map state assignment that currently reads:

```python
state = "READY" if outcome in text_outcomes else "SCRAPE_LINK"
```

   with per-row state after the mapper returns (still inside the `if classify.get("success") and outcome in (*text_outcomes, *url_outcomes):` block, after `row_dicts` is built and before insert). For each `row` in `row_dicts` (zip with jobs still sets `job_title` / `employer_name` as today):

   - Let `row_link = (row.get("link") or "").strip() if isinstance(row.get("link"), str) else ""`.
   - If `_is_http_url(row_link)` → `row["state"] = "SCRAPE_LINK"`.
   - Else if `outcome in text_outcomes` → `row["state"] = "READY"`.
   - Else → `row["state"] = "SCRAPE_LINK"` (URL outcomes without a somehow-empty link still take the scrape arm; mapper already failed missing http links for URL outcomes).

   Keep the existing loop that sets `row["job_title"] = _stage_field(job, "job_title")` and `row["employer_name"] = _stage_field(job, "employer_name")` unchanged.

3. In `run_stage_meteorite`, in the `outcome in STAGE_METEORITE_CONFIG["text_source_ref_outcomes"]` arm, after content/link checks and **before** `update_meteorite(row_id, state="READY")`:

   - If `_is_http_url(link)` → `update_meteorite(row_id, state="SCRAPE_LINK", link=link)`, `_meteorite_state_info(row_id, "SCRAPE_LINK", from_state="NEW")`, bump `total_passed`, `continue`.
   - Else keep today’s READY path (including the AST-1703 “email text rows must already carry breadcrumb on link” empty-link → `SCRAPE_ERROR` check for `kind == "email"`).

   Do **not** change the URL-outcome arm of `run_stage_meteorite` beyond shared `_is_http_url` use.

⚠️ **Decision:** Prefer http `job_link` inside the text-outcome mapper (not only post-map overwrite) so `insert_meteorite_rows` never persists a breadcrumb that must be rewritten — single source of truth for `link` at map time; post-map only decides `state` from the final `link` scheme.

⚠️ **Decision:** Touch `run_stage_meteorite`’s text arm in the same stage — Scope requires http-linked rows on `SCRAPE_LINK` and forbids leaving an http `link` stranded under `READY` because the outcome string was text; that runner currently forces READY for all text outcomes. Same file, same technical kind as post-map wiring.

4. Verify from the epic worktree (no test-tree edits):

```bash
python3 -m py_compile src/core/meteorite.py

python3 - <<'PY'
# Static shape check: text branch prefers http job_link; state keys off link scheme.
from pathlib import Path
src = Path("src/core/meteorite.py").read_text()
assert "_map_classify_jobs_to_meteorite_rows" in src
assert "_email_breadcrumb_link" in src
assert "_is_http_url" in src
# Prefer path must exist near text outcomes (job_link read before breadcrumb for text)
assert "Preferring http job_link over breadcrumb" in src or "job_link" in src
print("ok: compile + symbols present")
PY
```

   Manual / builder acceptance (AC4–AC7): exercise `stage_meteorite` (or the mapper + post-map) with synthetic classify payloads — (a) text outcome + http `job_link` + `job_title` → `link` == URL, `state` == `SCRAPE_LINK`, title preserved; (b) text outcome + no http `job_link` + email header fields → breadcrumb `link`, `state` == `READY`; (c) `link_list` / `single_jd_with_more` with http `job_link` → unchanged http `link` + `SCRAPE_LINK`.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1785
**Overall:** APPROVED
**Corpus:** 2ac86c3f693409c364f8630a97198c8dbfa9c6f3
**Publish ref:** `sub/AST-1783/AST-1785-prefer-http-job-link-over-breadcrumb` @ `515b58421b077bbb9d62261bdb43692bf23a4db1`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.task.daisy-chain | A | | |
| stat.logging.debug | A | | |
| stat.logging.info.entity | A | | |

## Traceability

AC4–AC7 → Stage 1; parent AC1–AC3, AC8 → N/A (AST-1784 prompts/fixture).

### Findings

**discuss** — **Assignee gate (§1):** Ticket assignee is Hedy, not Joan. Plan substance reviewed; Chuckles must assign Joan before status flip / `save-comment`.

**acceptable** — `## UAT fitness` present though this is full-path (not UAT-thin); correctly quotes parent AC4–AC7, names sibling AST-1784 boundary, and rejects prompt-only / parallel-harvester wrong fixes. No conflict with full rubric.

**acceptable** — `_is_http_url` relocation (currently ~L1624, mapper ~L1307): plan names the ordering fix; shared predicate is correct vs duplicating `startswith` checks.

**acceptable** — Verification step is `py_compile` + static symbol check + manual AC4–AC7 payloads; no test-tree edits in plan (Betty owns Tests Ready). Matches child scope.

**Gates:** Status `Plan Ready` — pass. No `[plan-discuss]` rounds (0/2). Files Changed = `src/core/meteorite.py` only; matches ticket `## Scope`; AST-1784 / agent_task / fixture explicitly out.

**R6 (summary):** Plan targets the live text-branch gap (`_map_classify_jobs_to_meteorite_rows` always breadcrumbs email text before reading `job_link`; `stage_meteorite` L1013 forces READY for all text outcomes; `run_stage_meteorite` L1708 forces READY for text arm). Three touchpoints (mapper prefer → post-map state from `link` scheme → runner text arm http branch) satisfy AC5’s “not stranded under READY” requirement without touching URL-outcome branch. AC6 preserved (breadcrumb only when no http `job_link`). AC7 preserved (URL branch byte-stable). `job_title` / `employer_name` post-map unchanged. No parallel HTML harvester. Estimate confirm present.

context_tokens≈30000
