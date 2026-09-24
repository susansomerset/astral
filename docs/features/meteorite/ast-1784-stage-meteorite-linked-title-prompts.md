# AST-1784 — stage_meteorite linked-title prompts

**Linear:** [AST-1784](https://linear.app/astralcareermatch/issue/AST-1784/stage-meteorite-linked-title-prompts-parsing-emails-with-linked-job)  
**Parent:** [AST-1783](https://linear.app/astralcareermatch/issue/AST-1783/parsing-emails-with-linked-job-titles) — Parsing emails with linked job titles  
**Publish ref:** `sub/AST-1783/AST-1784-stage-meteorite-linked-title-prompts`

Teach `stage_meteorite` agent_task prompts to classify title-as-href emails as URL landables (`link_list` / `single_jd_with_more`), set `job_link` from the anchor href and optional `job_title` from role-naming anchor text (omit for generic CTAs; never invent). Lockstep the AST-756 expected `agent_task` fixture for those prompts. Does **not** own map breadcrumb-vs-http preference (**AST-1785**). Does **not** add a seventh outcome.

## Scope gate

Ticket **## Scope** (verbatim partition):

- `data/admin/agent_task.json` — **modified** — `stage_meteorite` cache/user prompts teach title-as-href → `job_link` from href + `job_title` from role-naming anchor text; keep the six closed outcomes; no `$RESPONSE_SCHEMA` in prompts. `docs/uat-fixtures/AST-756/expected-agent_task.json` — **modified** — lockstep expected catalog text with the `stage_meteorite` prompt edits. Technical: update `stage_meteorite` prompt instructions so title-as-href blobs are classified as URL landables (`link_list` / `single_jd_with_more` as appropriate), each jobs item sets `job_link` from the anchor href and optional `job_title` from role-naming anchor text (omit title for generic CTAs; never invent); keep electronic-contact, breadcrumb header fields, and JOB TITLE subject-prefer rules for other shapes; leave `$RESPONSE_SCHEMA` absent. Mirror the same wording in the UAT catalog fixture.

All Files Changed / Stages stay inside that set.

**Out of scope (siblings / other epics):**

- `src/core/meteorite.py` stage map / post-map http `job_link` over breadcrumb — **AST-1785**
- Adding a seventh `STAGE_METEORITE_CONFIG["outcomes"]` literal
- Land / `listing_href` / scrape runners
- Logging edits (`stat.logging.debug` / `stat.logging.info.entity` are id-only for this child)

**Depends on:** none (Bang `!` with sibling **AST-1785**). Sibling is after this child for full linked-title UAT.

**AC partition (this ticket):** Parent AC1–AC3 and AC8 only (AC4–AC7 → **AST-1785** map preference + scrape path).

**Canon Scope (read at plan):** `patt.task.daisy-chain` (full — URL + title must be askable at stage so the meteorite row can carry them through later hops; this ticket only teaches the ask, does not invent a parallel HTML harvester). `stat.logging.debug`, `stat.logging.info.entity` — **id-only** (no logging code in this ticket’s files).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | Append `## TITLE-AS-HREF (linked job titles)` to `stage_meteorite` `cache_prompt`; update `user_prompt` for title-as-href → `job_link` / role-naming `job_title`; keep six outcomes + electronic-contact / breadcrumb / JOB TITLE subject-prefer; never insert `$RESPONSE_SCHEMA` | catalog |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Surgical lockstep: set `stage_meteorite` `cache_prompt` and `user_prompt` to the exact same strings as `data/admin/agent_task.json` after the catalog edit | uat-fixture |

## Stage 1: Title-as-href prompts + AST-756 lockstep

**Done when:** `stage_meteorite` `cache_prompt` / `user_prompt` instruct title-as-href → URL landables (`link_list` / `single_jd_with_more`), `job_link` from href, optional `job_title` from role-naming anchor text (omit generic CTAs; never invent); electronic-contact, breadcrumb, and JOB TITLE subject-prefer sections remain for other shapes; neither prompt field contains `$RESPONSE_SCHEMA`; six outcome names unchanged; `STAGE_METEORITE_CONFIG["outcomes"]` still length 6; fixture `stage_meteorite` `cache_prompt` / `user_prompt` byte-equal admin; both JSON files remain valid.

1. In `data/admin/agent_task.json`, locate the object with `"task_key": "stage_meteorite"`. Edit **`cache_prompt`** only by **appending** a new section after the existing `## JOB TITLE (optional)` block (do not rewrite OUTCOMES, HEADER / BREADCRUMB FIELDS, ELECTRONIC CONTACT, or JOB TITLE). Append exactly this section (literal text):

```
## TITLE-AS-HREF (linked job titles)

When CONTENT shows one or more job titles that are themselves hyperlinks to job pages (HTML like <a href="https://…">Senior Widget Engineer</a>, or equivalent markdown / visible "title is the link" shapes), classify as a URL landable — do not treat those as text landables (single_jd_no_link / multi_jd_inline).

- Several title-as-href anchors → outcome link_list; one jobs item per anchor.
- One inline JD plus a separate title-linked / "more" posting URL → outcome single_jd_with_more; that posting URL is job_link.
- A single title-as-href with no separate inline JD body → outcome link_list with one jobs item.

For each such jobs item:
- Set job_link to the anchor's http(s) href (never invent URLs; never substitute a company homepage).
- Set job_title to the anchor's visible text when that text names a role. If the anchor text is only a generic CTA (e.g. Apply, View job, Click here), omit job_title or return an empty string — still return the href as job_link. Never invent titles.

Bare URL lists and rich HTML page pastes that already map to link_list / single_jd_with_more stay unchanged. Electronic-contact and breadcrumb header rules stay unchanged. For landable shapes that are not title-as-href, keep the ## JOB TITLE (optional) subject-prefer rules.
```

2. Update the same row’s **`user_prompt`** to (replace the whole string):

```
Read CONTENT. Return JSON with outcome (exactly one closed outcome literal) and jobs (scrap fields per outcome; empty list for not_job_content and not_original_posting). For single_jd_no_link and multi_jd_inline, each jobs item must include from_email, to_email, and sent_at (bare emails; peel inner headers on forwards). Include optional electronic_contact per item (prefer metadata; never invent addresses). Include optional job_title per landable jobs item when the role name is known (prefer subject when it names the role; omit when unknown; never invent). When job titles are themselves hyperlinks to job pages (title-as-href), classify as link_list or single_jd_with_more; set job_link from the href and job_title from role-naming anchor text (omit title for generic CTAs; never invent). Do not emit grade vectors.
```

3. Leave `nocache_prompt`, `system_prompt`, and `cache_prompt_b`/`_c`/`_d` unchanged (empty). Do **not** insert `$RESPONSE_SCHEMA` (or any full schema dump) into any `stage_meteorite` prompt field. Do **not** add, rename, or remove any of the six closed outcome literals in OUTCOMES.

4. In `docs/uat-fixtures/AST-756/expected-agent_task.json`, locate the object with `"task_key": "stage_meteorite"`. Set that row’s **`cache_prompt`** and **`user_prompt`** to the **exact same strings** now present on the admin catalog row (surgical field copy — do not whole-file `cp` the catalog over the fixture; do not add/remove other fixture rows in this ticket).

⚠️ **Decision:** Append a dedicated `## TITLE-AS-HREF (linked job titles)` section rather than rewriting OUTCOME bullets — mirrors AST-1755 / AST-1688 section pattern; keeps the six outcome definitions byte-stable while teaching the new ingress shape.

⚠️ **Decision:** Repo `data/admin/agent_task.json` is SSOT for `stage_meteorite` prompt text. On `origin/dev` the AST-756 fixture row already drifts ahead of admin (fixture has `## EMPLOYER NAME (optional)` + `review_duplicate_meteorite` from AST-1773 tests; admin does not). This ticket’s AC8 lockstep requires `stage_meteorite` `cache_prompt` / `user_prompt` to match admin after the title-as-href edit — surgical overwrite of those two fixture fields is required. Do **not** re-introduce employer / review_duplicate text in this child (out of Scope). If Betty’s older twin asserts fail, that is `[qa-handoff]` / a separate bug — not scope invention here.

5. Verify acceptance gates from the epic worktree:

```bash
rg -n 'href|title-as-href|anchor|job_link' data/admin/agent_task.json
# Expect matches inside stage_meteorite cache_prompt / user_prompt for the title-as-href instructions.

python3 - <<'PY'
import json
from pathlib import Path

def stage(path):
    return next(r for r in json.loads(Path(path).read_text()) if r.get("task_key") == "stage_meteorite")

admin = stage("data/admin/agent_task.json")
fix = stage("docs/uat-fixtures/AST-756/expected-agent_task.json")
for k in ("cache_prompt", "user_prompt", "nocache_prompt"):
    t = admin.get(k) or ""
    assert "$RESPONSE_SCHEMA" not in t, k
if True:
    cp, up = admin["cache_prompt"], admin["user_prompt"]
    assert "title-as-href" in cp and "TITLE-AS-HREF" in cp
    assert "job_link" in cp and "job_title" in cp
    assert "link_list" in cp and "single_jd_with_more" in cp
    assert "generic CTA" in cp or "Apply" in cp
    assert "title-as-href" in up
    assert admin["cache_prompt"] == fix["cache_prompt"]
    assert admin["user_prompt"] == fix["user_prompt"]
    for name in (
        "single_jd_no_link",
        "single_jd_with_more",
        "multi_jd_inline",
        "link_list",
        "not_job_content",
        "not_original_posting",
    ):
        assert name in cp
print("stage_meteorite title-as-href prompts + fixture lockstep OK")
PY

python3 -c 'from src.utils.config import STAGE_METEORITE_CONFIG; assert len(STAGE_METEORITE_CONFIG["outcomes"])==6'
python3 -c 'import json; json.load(open("data/admin/agent_task.json")); json.load(open("docs/uat-fixtures/AST-756/expected-agent_task.json"))'
```

**AC note (no code in this ticket):** Parent AC4–AC7 (breadcrumb vs http `job_link` on the meteorite row, scrape-path partition) belong to **AST-1785**. After this prompt change, Ruth is expected to return URL landable jobs items with `job_link` / optional `job_title` for title-as-href blobs; map preference is sibling-owned. Do **not** edit `meteorite.py` here.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1784
**Overall:** APPROVED
**Corpus:** 2ac86c3f693409c364f8630a97198c8dbfa9c6f3
**Publish ref:** `sub/AST-1783/AST-1784-stage-meteorite-linked-title-prompts` @ `32a02ade7210947e22a91ee24aacae98d2355472`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.task.daisy-chain | A | | |
| stat.logging.debug | X | | id-only; plan touches catalog + fixture only, no `src/**` |
| stat.logging.info.entity | X | | id-only; no `src/core/meteorite.py` or other entity logging paths |

## Traceability

AC1–AC4 → Stage 1; parent AC4–AC7 → N/A (AST-1785 map/scrape path).

### Findings

**acceptable** — `## Stage 1` Decision (fixture drift): Plan acknowledges AST-756 fixture row drifts from admin on employer/review_duplicate fields outside this child's scope; surgical `cache_prompt`/`user_prompt` copy is the correct AC8 interpretation. `[qa-handoff]` escape hatch if Betty's broader twin asserts fire is honest, not scope creep.

**Gates:** Status `Plan Ready`, assignee Joan — pass. No `[plan-discuss]` rounds in thread (0/2).

**R6 (summary):** Plan matches child `## Scope` (two files only); parent AC partition AC1–3 + AC8 explicit; six-outcome / no-`$RESPONSE_SCHEMA` / no-`meteorite.py` boundaries clear; append-not-rewrite pattern matches prior meteorite prompt tickets; Estimate confirm present.

context_tokens≈22000

## Review (build stub)

**Publish ref:** `origin/sub/AST-1783/AST-1784-stage-meteorite-linked-title-prompts`
**Plan path:** `docs/features/meteorite/ast-1784-stage-meteorite-linked-title-prompts.md`

**Built tip:** `2deef11805fc10f6491dc7cb3d6a0054e321d506` (`2deef118`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `2deef118` | `stage_meteorite` cache/user prompts: title-as-href → URL landables; AST-756 surgical lockstep; no `$RESPONSE_SCHEMA` |

**Betty note:** Prompt + fixture only. Map http `job_link` over breadcrumb is **AST-1785**. Pre-existing fixture employer/review_duplicate drift intentionally overwritten on `stage_meteorite` prompt fields per plan Decision — `[qa-handoff]` if broader twin asserts fire.
