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

## Radia review

[code-rubric]

**Ticket:** AST-1784  
**Publish ref:** `bb0e9e739908cb00303917a6bdbfbf1f4063cce0` (`origin/sub/AST-1783/AST-1784-stage-meteorite-linked-title-prompts`)  
**Corpus:** `2ac86c3f693409c364f8630a97198c8dbfa9c6f3`  
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.task.daisy-chain | A | | |
| stat.logging.debug | X | | catalog + fixture only; no `src/**` edits on tip |
| stat.logging.info.entity | X | | no `src/core/meteorite.py` or other entity-logging paths |

## Column diff vs plan stage

(aligned) — Joan: `patt.task.daisy-chain` A, `stat.logging.debug` X, `stat.logging.info.entity` X; same on diff review.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

- **Location:** `origin/dev...origin/sub/AST-1783/AST-1784-stage-meteorite-linked-title-prompts` (full three-dot diff)  
  **Finding:** Product commit `2deef118` is correctly scoped to `data/admin/agent_task.json` + `docs/uat-fixtures/AST-756/expected-agent_task.json`. `merge-tests` (`bb0e9e73`) also lands ~900 lines of sibling test/bible work (AST-1782, AST-1780, AST-1781, AST-1779, AST-1769) on this publish ref — same epic parallel-test pattern as AST-1755.  
  **Recommendation:** Accept as workflow side effect; run only Betty’s AST-1784 manifest on this tip, not zero-arg harness.

- **Location:** `tests/component/core/test_repo_admin_json.py::TestAst1773StageEmployerNameAndReviewDuplicateCatalog`  
  **Finding:** `test_stage_employer_name_prompts_never_invent` and `test_fixture_catalog_byte_lockstep` still require `## EMPLOYER NAME (optional)` / `employer_name` in admin and whole-file fixture twin. This tip intentionally omits employer prompts in admin (plan Decision) and uses surgical `stage_meteorite` field lockstep only. Those tests would fail if run.  
  **Recommendation:** No action on AST-1784 — bible § AST-1784 already excludes `TestAst1773…`; ensure test-child manifest stays narrow. Employer product belongs on AST-1773’s own publish ref.

- **Location:** `docs/uat-fixtures/AST-756/expected-agent_task.json` (`stage_meteorite` row)  
  **Finding:** Fixture `cache_prompt` / `user_prompt` no longer carry tip-ahead `## EMPLOYER NAME` / `employer_name` text (replaced with title-as-href lockstep to admin). Whole-file twin still drifts on `review_duplicate_meteorite` and other rows — plan-acknowledged, not a regression.  
  **Recommendation:** Accept per plan Decision; do not re-introduce employer copy in this child.

### advisory

- **Location:** `docs/test-bible/core/repo_admin_json.md` § AST-1784  
  **Finding:** Duplicate `## QA test manifest` header blocks (lines ~658 and ~681); shasum lines still say “record after publish.”  
  **Recommendation:** Chuckles stamps shasums on doc writeback; optional bible tidy is Betty’s lane, not blocking.

- **Location:** `tests/component/core/test_repo_admin_json.py::TestAst1529…` / `TestAst1755…`  
  **Finding:** Whole-file byte-equality asserts removed in favor of surgical `stage_meteorite` prompt-field lockstep — necessary hygiene aligned with plan and bible.  
  **Recommendation:** None.

## What's solid

- `## TITLE-AS-HREF (linked job titles)` appended verbatim after `## JOB TITLE (optional)`; `user_prompt` matches plan literal (title-as-href → `link_list` / `single_jd_with_more`; `job_link` from href; role-naming `job_title`; generic CTA omit; never invent).
- Prior sections preserved: OUTCOMES (six literals), HEADER / BREADCRUMB, ELECTRONIC CONTACT, JOB TITLE subject-prefer.
- No `$RESPONSE_SCHEMA` in `cache_prompt`, `user_prompt`, or `nocache_prompt`.
- `STAGE_METEORITE_CONFIG["outcomes"]` length 6 unchanged; no `src/**` edits on tip.
- Admin ↔ fixture `stage_meteorite` `cache_prompt` / `user_prompt` byte-equal (verified locally).
- `TestAst1784StageMeteoriteLinkedTitlePrompts` locks acceptance gates from plan Stage 1 verification script.
- `patt.task.daisy-chain`: teaches URL + optional title at classify stage in the same Ruth response — no parallel HTML harvester or re-derive path; map preference correctly deferred to AST-1785.
- Betty manifest (`repo_admin_json.md` § AST-1784) scopes pytest to `TestAst1784…`, `TestAst1755…`, `TestAst1529…` — consistent with Tests Passed.

## Recommended actions (Chuckles downstream — not Radia)

1. Append this artifact to `docs/features/meteorite/ast-1784-stage-meteorite-linked-title-prompts.md`; commit `docs(AST-1784): Radia review — clean`; push.
2. Post slim upshot via `linear_proxy --as radia save-comment`; move to **Review Posted**.
3. datt §3h: **PROCEED** → **User Testing** (no `resolve-child` fix-now items).

---

`[code-rubric] PROCEED (Commit: bb0e9e73) title-as-href prompts clean`

context_tokens≈28000

## Bug: AST-1796 — Combo email: mixed JD + job-link array of meteorites

### As-is

Combo emails that mix an inline job description with separate job links are not classified into an array of mixed meteorites (some link-only, some with full JD content — and a link when available). Ruth is steered toward `single_jd_with_more` (one jobs item) or a pure `multi_jd_inline` / `link_list` shape that drops half of the landables.

### To-be

Stage classify instructions accommodate that combo shape and return an array of meteorites covering both kinds: jobs with links, and jobs with full JD contents (plus link when present). Existing six closed outcomes only — no seventh outcome string.

### Repro

1. Ingress blob shaped like Susan's sample: one (or more) original JD bodies inline in the email **plus** one or more separate http(s) job-page URLs (not merely a single "more" URL glued onto one JD).
2. Run live `stage_meteorite` classify on that blob.
3. **Broken:** outcome collapses to `single_jd_with_more` (one jobs item) or `link_list`/`multi_jd_inline` that omits either the full JD landable(s) or the separate link landable(s) — staged meteorite count ≠ number of distinct landables.
4. **Fixed:** classify returns `multi_jd_inline` with `jobs.length` equal to the distinct landables: each full JD → item with `jd_text` (and `job_link` when that posting has a URL); each separate job URL not already tied to a JD item → item with `job_link` and empty/omitted `jd_text`. Map inserts that many meteorite rows; http `job_link` items land on the scrape path (AST-1785).

### Root cause

1. **Prompts:** `multi_jd_inline` currently forbids `job_link`; `link_list` requires a URL on every item; `single_jd_with_more` is defined as **one** jobs item. A combo blob therefore has no taught path that returns a **mixed** `jobs[]` array under the closed six outcomes.
2. **Map (blocks link-only rows under a text outcome):** In `_map_classify_jobs_to_meteorite_rows`, text outcomes with empty `jd_text` fall back to the full `ingress_blob` (AST-1756). A link-only jobs item under `multi_jd_inline` would therefore get the entire email as `content` instead of a link-only scrap.

### Proposed change

Parent epic **Component / Technical scope** is the bound (UAT-batch). Touch only those files; keep six outcomes; no `$RESPONSE_SCHEMA` in prompts.

1. **`data/admin/agent_task.json`** — `stage_meteorite` row:

   - In `## OUTCOMES` bullet **3. multi_jd_inline**, replace the current "leave job_link empty" rule with: return one jobs item per landable in the blob; each original JD gets `jd_text`; when a posting URL is present for that JD, also set `job_link`; when the blob also has separate job-page URLs that are not the body of an inline JD, add one jobs item per such URL with `job_link` set and `jd_text` omitted/empty. Still set the same `from_email` / `to_email` / `sent_at` on every jobs item for this outcome. Do **not** invent a seventh outcome.
   - Leave bullets 1–2 and 4–6 otherwise intact (including `single_jd_with_more` = one JD + one "more" URL as **one** jobs item — that shape is not the multi-link combo).
   - Append a new section after `## TITLE-AS-HREF (linked job titles)` with this literal heading and rules:

```
## COMBO (inline JD + separate job links)

When CONTENT mixes one or more original job descriptions inline with one or more separate job-page URLs (a recruiter "here is the JD, and also these other openings" email), classify as multi_jd_inline and return one jobs item per distinct landable — do not collapse into single_jd_with_more, and do not drop either the JD bodies or the separate links.

- Each original JD body → one jobs item with that text in jd_text; set job_link when that same posting also has an http(s) URL; omit job_link when the JD has no posting URL.
- Each separate job-page URL that is not already represented as the job_link on a JD item → one jobs item with that URL as job_link and jd_text omitted/empty (never invent JD text for a bare link).
- Title-as-href anchors that are themselves the job titles remain under ## TITLE-AS-HREF (prefer link_list / single_jd_with_more as that section already teaches). Pure URL lists stay link_list. A single JD plus exactly one "more" URL with no other separate links may still be single_jd_with_more.

Never invent URLs or JD text. Keep electronic-contact, breadcrumb header, JOB TITLE, and EMPLOYER NAME rules.
```

   - Update `user_prompt` to add one sentence after the title-as-href sentence (keep all existing sentences):  
     `When CONTENT mixes inline JD body text with separate job-page URLs, classify as multi_jd_inline and return one jobs item per landable (jd_text for JD bodies; job_link for separate URLs; both when a JD has its own URL); do not collapse to a single jobs item.`
   - Do not insert `$RESPONSE_SCHEMA`. Leave `nocache_prompt` / `system_prompt` / empty cache slots unchanged.

2. **`docs/uat-fixtures/AST-756/expected-agent_task.json`** — surgical lockstep: set `stage_meteorite` `cache_prompt` and `user_prompt` to the exact same strings as admin after step 1 (same discipline as AST-1784 Stage 1 §4).

3. **`src/core/meteorite.py`** — in `_map_classify_jobs_to_meteorite_rows`, text-outcome branch (`text_source_ref_outcomes`): when `jd_text` is empty/blank **and** the jobs item has an http(s) `job_link` (`_is_http_url`), do **not** fall back to `ingress_blob`; use empty content (`""` or `None` consistent with URL-outcome rows that have no jd_text) and set `link` to that `job_link` (AST-1785 preference already applies). Keep the existing ingress-blob fallback only when there is **no** http(s) `job_link` (classic text landable with blank Ruth `jd_text`). Do not change URL-outcome mapping, breadcrumb helper call sites beyond this skip, or invent a parallel HTML harvester.

⚠️ **Decision:** Teach combo under existing `multi_jd_inline` (not a seventh outcome, not `link_list`) because URL outcomes require http `job_link` on every jobs item and combo may include an unlinked JD body; AST-1785 already prefers http `job_link` over breadcrumb on text outcomes once the prompt returns mixed items.

### Blast radius

- `stage_meteorite` catalog + AST-756 fixture twin (Betty prompt / lockstep tests for AST-1784 / AST-1755 / AST-1529 may need a combo assertion — Betty owns test-tree).
- `_map_classify_jobs_to_meteorite_rows` text path: classic blank-`jd_text` + no-link emails must still get ingress-blob fallback (AST-1756); only the http-link + blank-`jd_text` case changes.
- AST-1785 map preference and scrape-state path remain the consumer of http `job_link` on text outcomes — do not re-implement preference elsewhere.
- Title-as-href / employer / job_title / electronic-contact prompt sections must remain; combo section must not contradict TITLE-AS-HREF for pure title-link blobs.

### What must still hold

- Six closed `STAGE_METEORITE_CONFIG["outcomes"]` literals; no `$RESPONSE_SCHEMA` in `stage_meteorite` prompts (parent AC2–AC3 / AST-1784).
- Title-as-href teaching (AST-1784) and fixture lockstep of `stage_meteorite` prompt fields remain.
- Text landable with **no** http `job_link` still gets email breadcrumb (parent AC6 / AST-1785).
- http `job_link` on a jobs item still wins over breadcrumb and uses scrape path (parent AC4–AC5 / AST-1785).
- Bare URL-list and Dice-style `link_list` / `single_jd_with_more` shapes do not regress (parent AC7).
- AST-1756 ingress-blob fallback for blank `jd_text` on text outcomes **without** http `job_link` still holds.
