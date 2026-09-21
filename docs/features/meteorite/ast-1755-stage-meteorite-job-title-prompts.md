# AST-1755 — stage_meteorite job_title prompts

**Linear:** [AST-1755](https://linear.app/astralcareermatch/issue/AST-1755/stage-meteorite-job-title-prompts-stage-email-meteorite-enhancements)  
**Parent:** [AST-1753](https://linear.app/astralcareermatch/issue/AST-1753/stage-email-meteorite-enhancements) — stage_email_meteorite enhancements  
**Publish ref:** `sub/AST-1753/AST-1755-stage-meteorite-job-title-prompts`

Teach `stage_meteorite` agent_task prompts to ask Ruth for optional `job_title` on each landable jobs item (prefer subject when it names the role; omit when unknown; never invent). Keep `$RESPONSE_SCHEMA` out of those prompts. Confirm `TASK_CONFIG` already has optional `job_title` — do not invent or edit schema. Does **not** own stage content fallback (**AST-1756**) or land → job title wiring (**AST-1757**).

## Scope gate

Ticket **## Scope** (verbatim partition):

- `data/admin/agent_task.json` — **modified** — `stage_meteorite` cache/user prompts instruct optional `job_title` (subject-prefer); do not add `$RESPONSE_SCHEMA`. Technical: update `stage_meteorite` prompt text so each landable jobs item may include optional `job_title`, preferring subject-line titles when present; keep the six closed outcomes and existing electronic-contact / breadcrumb instructions; leave `$RESPONSE_SCHEMA` absent from those prompts.

All Files Changed / Stages stay inside that set.

**Out of scope (siblings / other epics):**

- `src/core/meteorite.py` stage map `jd_text` → ingress-blob fallback — **AST-1756**
- `src/core/meteorite.py` land paths passing `job_title=` into `tracker.save_meteorite_job` — **AST-1757**
- `src/utils/config.py` / `TASK_CONFIG["stage_meteorite"]["response_schema"]` — schema field already present and optional; **confirm only**, do not invent or edit
- Changing the six closed outcome literals
- Logging edits (`stat.logging.debug` / `stat.logging.info.entity` are id-only for this child)

**Depends on:** none (Bang `!` with sibling #2). Sibling **AST-1757** is after this child for full end-to-end title UAT.

**AC partition (this ticket):** Parent AC1–AC4 only (AC5–6 → AST-1756; AC7–9 → AST-1757).

**Canon Scope (read at plan):** `patt.task.daisy-chain` (full — title must be askable at stage so the meteorite row can carry it through later hops; this ticket only teaches the ask, does not invent a parallel extract). `stat.logging.debug`, `stat.logging.info.entity` — **id-only** (no logging code in this ticket’s file).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | Extend `stage_meteorite` `cache_prompt` (+ `user_prompt` touch) for optional subject-prefer `job_title`; forbid invention; keep six outcomes + electronic-contact / breadcrumb sections; never insert `$RESPONSE_SCHEMA` | catalog |

## Stage 1: Confirm schema (read-only) + prompt text

**Done when:** `TASK_CONFIG["stage_meteorite"]["response_schema"]["jobs"]["items_schema"]["job_title"]["required"] is False` (no config edit); `stage_meteorite` `cache_prompt` / `user_prompt` instruct optional `job_title` with subject preference and never-invent; neither prompt field contains `$RESPONSE_SCHEMA`; six outcome names and existing electronic-contact / breadcrumb instructions remain; JSON remains valid.

1. **Confirm only (no file edit):** from the epic worktree, run:

```bash
python3 -c 'from src.utils.config import TASK_CONFIG; s=TASK_CONFIG["stage_meteorite"]["response_schema"]["jobs"]["items_schema"]["job_title"]; assert s.get("required") is False; print(s)'
```

If this assert fails, **stop** and comment on the Linear **parent** with the Stage-blocked template — do not invent a schema field in this ticket (Scope does not include `config.py`).

2. In `data/admin/agent_task.json`, locate the object with `"task_key": "stage_meteorite"`. Edit **`cache_prompt`** only by **appending** a new section after the existing `## ELECTRONIC CONTACT (resume send)` block (do not rewrite OUTCOMES, HEADER / BREADCRUMB FIELDS, or ELECTRONIC CONTACT). Append exactly this section (literal text):

```
## JOB TITLE (optional)

For every jobs item you return on landable outcomes (single_jd_no_link, single_jd_with_more, multi_jd_inline, link_list), include optional job_title when you can tell what the role is called.

Prefer the email (or ingress) subject line when it names the role. If the subject does not name a role, use an explicit title already present in the JD/body. If the title is unknown, omit job_title or return an empty string.

Never invent titles. Never guess a role name from vague marketing copy.
```

3. Update the same row’s **`user_prompt`** to (replace the whole string):

```
Read CONTENT. Return JSON with outcome (exactly one closed outcome literal) and jobs (scrap fields per outcome; empty list for not_job_content and not_original_posting). For single_jd_no_link and multi_jd_inline, each jobs item must include from_email, to_email, and sent_at (bare emails; peel inner headers on forwards). Include optional electronic_contact per item (prefer metadata; never invent addresses). Include optional job_title per landable jobs item when the role name is known (prefer subject when it names the role; omit when unknown; never invent). Do not emit grade vectors.
```

4. Leave `nocache_prompt`, `system_prompt`, and `cache_prompt_b`/`_c`/`_d` unchanged (empty). Do **not** insert `$RESPONSE_SCHEMA` (or any full schema dump) into any `stage_meteorite` prompt field.

5. Verify acceptance gates from the epic worktree:

```bash
rg -n 'job_title' data/admin/agent_task.json
# Expect matches inside the stage_meteorite prompt text (cache_prompt / user_prompt), not only unrelated tasks.

python3 - <<'PY'
import json
from pathlib import Path
row = next(r for r in json.loads(Path("data/admin/agent_task.json").read_text()) if r.get("task_key") == "stage_meteorite")
for k in ("cache_prompt", "user_prompt", "nocache_prompt"):
    t = row.get(k) or ""
    assert "$RESPONSE_SCHEMA" not in t, k
    if k in ("cache_prompt", "user_prompt"):
        assert "job_title" in t, k
print("stage_meteorite prompts OK")
PY

python3 -c 'from src.utils.config import TASK_CONFIG; s=TASK_CONFIG["stage_meteorite"]["response_schema"]["jobs"]["items_schema"]["job_title"]; assert s.get("required") is False'
python3 -c 'import json; json.load(open("data/admin/agent_task.json"))'
```

⚠️ **Decision:** Prompt-only change; reuse the existing optional `job_title` schema key already on `items_schema`. Do not rename, require, or relocate the field — parent AC3 and Scope both say confirm, not invent.

⚠️ **Decision:** Append a dedicated `## JOB TITLE (optional)` section rather than folding title rules into OUTCOME bullets — mirrors AST-1688’s electronic-contact section pattern and keeps the six outcome definitions untouched.

**AC4 note (no code in this ticket):** Existing stage→row map in `src/core/meteorite.py` already copies Ruth `job_title` onto the meteorite row (`row["job_title"] = _stage_field(job, "job_title")`). After this prompt change, a landable classify that returns `"job_title": "Senior Widget Engineer"` is expected to persist that string on the meteorite column via that existing map. Do **not** edit `meteorite.py` here; if the map is missing at build time, stop and escalate (Scope boundary / sibling ownership).

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

**Ticket:** AST-1755
**Overall:** APPROVED
**Corpus:** 2ac86c3f693409c364f8630a97198c8dbfa9c6f3
**Publish ref:** `sub/AST-1753/AST-1755-stage-meteorite-job-title-prompts` @ `6e0c12f24581ec372a9ba159d6009a0e3566df1b`

### Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.task.daisy-chain | A | | |
| stat.logging.debug | X | | catalog-only ticket; directive territory is `src/**` |
| stat.logging.info.entity | X | | no `src/core/meteorite.py` edits in this child |

### Traceability

AC1→Stage 1 §2–3 + verify §5; AC2→Stage 1 §4 + verify §5; AC3→Stage 1 §1 + verify §5; AC4→Stage 1 AC4 note (existing `_stage_field` row map; no `meteorite.py` edit in scope)

### Findings

#### acceptable

- **Location:** Stage 1 AC4 note  
- **Finding:** AC4 (meteorite row `job_title` after a landable classify) is satisfied by prompt change plus the existing stage map at `_stage_field(job, "job_title")` in `src/core/meteorite.py`; the plan correctly forbids editing that file here and names the sibling boundary.  
- **Recommendation:** None required for plan approval; Betty may still attach a behavioral check at Tests Ready if the bible already covers stage→row title persistence.

#### discuss

- **Location:** Stage 1 Done when / verify §5  
- **Finding:** Verification steps are prompt- and schema-gates only; AC4 has no named manual or automated row-persistence check in the stage Done-when block (only the AC4 note).  
- **Recommendation:** Optional: add one Done-when bullet pointing engineers to replay a landable classify fixture or parent UAT step for AC4 — not blocking because mechanism and code path are documented and present on `origin/sub/…/AST-1755…`.

### R6 checklist (summary)

- Definition fidelity: plan matches child Scope (`data/admin/agent_task.json` only); parent AC1–AC4 addressed; siblings AST-1756/AST-1757 explicitly excluded.  
- DRY / scope: no duplicate extract path; no scope creep into `meteorite.py` or schema invention.  
- Self-assessment: Estimate confirm `2 — agree` matches a single-file prompt append + user_prompt replace.  
- Plan Discuss: status `Plan Ready`, assignee Joan, zero completed `[plan-discuss]` rounds.

context_tokens≈18500

## Review (build stub)

**Publish ref:** `origin/sub/AST-1753/AST-1755-stage-meteorite-job-title-prompts`
**Plan path:** `docs/features/meteorite/ast-1755-stage-meteorite-job-title-prompts.md`

**Built tip:** `bdc024c56789cb28368068116e4a194d0a544a96` (`bdc024c5`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `bdc024c5` | `stage_meteorite` cache/user prompts: optional subject-prefer `job_title`; no `$RESPONSE_SCHEMA` |

**Betty note:** Prompt-only; AC4 relies on existing `_stage_field(job, "job_title")` map — no `meteorite.py` edit in this child.

## Radia review

**Ticket:** AST-1755
**Publish ref:** `8a33800380d51d618efaba96c549f9b4ce4b5511` (`origin/sub/AST-1753/AST-1755-stage-meteorite-job-title-prompts`)
**Corpus:** `2ac86c3f693409c364f8630a97198c8dbfa9c6f3`
**Overall:** CLEAN

### Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.task.daisy-chain | A | | |
| stat.logging.debug | X | | catalog-only; no `src/**` edits |
| stat.logging.info.entity | X | | no `src/core/meteorite.py` edits |

### Column diff vs plan stage

(aligned) — Joan scored **A** / **X** / **X**; same on diff review.

### Frame diff

(none)

### Findings

#### fix-now

(none)

#### discuss

- **Location:** `data/admin/agent_task.json` (whole-file diff vs `origin/dev`)
- **Finding:** Plan scoped Stage 1 to `stage_meteorite` `cache_prompt` append + `user_prompt` replace only. The diff also normalizes Unicode em-dashes (`\u2014`) to ASCII hyphens (`-`) across ~46 unrelated prompt strings (intake, contact, qualify, roster vet, etc.) so the AST-756 whole-file fixture twin stays byte-lockstep. Cosmetic and semantically neutral, but blast radius is the full catalog, not one task row.
- **Recommendation:** Accept as merge/fixture side effect or narrow in a follow-up if Susan wants prompt-only diffs on catalog tickets; not blocking AC1–AC4.

- **Location:** `tests/component/core/test_meteorite.py::TestAst1756IngressBlobJdTextFallback`, `docs/features/meteorite/ast-1756-*.md`, `docs/test-bible/core/meteorite.md` § AST-1756
- **Finding:** Sibling **AST-1756** artifacts ride this publish ref via `merge-tests`, but `src/core/meteorite.py` on this tip has no `ingress_blob` — those tests would `TypeError` if run outside the AST-1755 manifest. AST-1755 manifest correctly omits them; **Tests Passed** is valid.
- **Recommendation:** No action on AST-1755; ensure AST-1756 product tip lands on its own ref before that manifest runs end-to-end.

#### advisory

- **Location:** `tests/component/core/test_repo_admin_json.py::TestAst1529StageMeteoriteCatalogRow`
- **Finding:** Grouping asserts revised (`Meteorite Review` / `4500` / `2.0` → `Land Meteorite` / `4200` / `1`) to match live catalog already on `origin/dev`; bible documents the revision. Necessary test hygiene, not AST-1755 product scope.
- **Recommendation:** None.

- **Location:** `docs/test-bible/core/repo_admin_json.md` § AST-1755
- **Finding:** Bible shasum lines still say “record after publish.”
- **Recommendation:** Chuckles stamps on doc writeback.

### What's solid

- `stage_meteorite` prompts match plan literals: `## JOB TITLE (optional)` appended after electronic-contact section; `user_prompt` exact match; all six closed outcomes + breadcrumb + electronic-contact blocks preserved.
- No `$RESPONSE_SCHEMA` in `cache_prompt`, `user_prompt`, or `nocache_prompt`.
- Schema confirm holds: `job_title` `required: False` in `TASK_CONFIG` (no `config.py` edit).
- `TestAst1755StageMeteoriteJobTitlePrompts` locks prompt text + AST-756 whole-file twin; manifest reuses `TestAst1713StageSavesRuthRow::test_scrape_link_http_and_ruth_fields` for AC4 row persist without touching `meteorite.py`.
- No `src/core/meteorite.py` changes — sibling **AST-1756** / **AST-1757** boundaries respected.
- `patt.task.daisy-chain` scope met: teaches optional `job_title` at classify stage for same-pass row carry-through; no parallel extract path.

context_tokens≈32000
