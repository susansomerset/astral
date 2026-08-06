# AST-1196 — agent_task: synthesize email link + subject title

**Linear:** [AST-1196](https://linear.app/astralcareermatch/issue/AST-1196/agent-task-synthesize-email-link-subject-title-errors-for-qualify)
**Parent:** [AST-1188](https://linear.app/astralcareermatch/issue/AST-1188/errors-for-qualify-meteorite-dispatch-task) — Errors for qualify_meteorite dispatch task
**Publish ref:** `origin/sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject`

Update the current Ruth `qualify_meteorite` `agent_task` instructions so that when CONTENT has a usable job description but no ATS/http job URL, Ruth returns a synthesized `job_link` of the form `email-<originalsender>-<timestamp>`; when CONTENT has no title but an email subject is present, Ruth uses that subject as `job_title`; original sender is discerned from email CONTENT (never the candidate mailbox); ads / unrelated non-JD content are failed via **empty-string** fields (never JSON `null` / omit on required keys); every input row returns exactly one response object with a positional `astral_job_id`. Does **not** own schema nullability / **BOT_BLOCKED** registry (AST-1195) or consult assemble/apply / http-gate / `company_job_id` waiver / Style D (AST-1197).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | Rewrite `qualify_meteorite` `cache_prompt` (+ short `user_prompt` touch); bump `updated_at` — **only this row** | data |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Surgical update of the existing `qualify_meteorite` row’s prompts/`updated_at` to match catalog — **no whole-file `cp`** | docs |

**No changes expected:** `src/utils/config.py`, `src/core/consult.py`, `src/core/agent.py`, `src/core/dispatcher.py`, `src/ui/**`, other `agent_task` rows, `tests/` / bible (Betty after Code Complete). Do **not** hand-edit the live DB — startup `apply_repo_admin_json` ships the row. Do **not** absorb pre-existing catalog↔fixture drift (missing rows / other tasks’ prompts) into this ticket.

## Stage 1: `qualify_meteorite` prompt — email-link synthesize + subject title

**Done when:** The current `qualify_meteorite` catalog row instructs Ruth to (a) synthesize `email-<originalsender>-<timestamp>` when there is no usable http(s) ATS/job link but CONTENT holds a real JD, (b) use SUBJECT as `job_title` when content has no title, (c) never use the candidate mailbox as original sender, (d) fail ads/unrelated content with **empty-string** `job_title` / `job_link` / `jd_text` (omit only optional `company_job_id`), (e) return **exactly one object per numbered CONTENT row** with positional `astral_job_id` (`000`, `001`, …) — never drop a row; the AST-756 fixture’s `qualify_meteorite` row matches those same three fields; no other catalog or fixture rows change in the commit.

1. **Pre-edit snapshots (gate against silent multi-row edits):** before changing anything, copy both files:

```bash
cp data/admin/agent_task.json /tmp/agent_task.pre-ast-1196.json
cp docs/uat-fixtures/AST-756/expected-agent_task.json /tmp/expected-agent_task.pre-ast-1196.json
```

2. In `data/admin/agent_task.json`, locate the single object with `task_key == "qualify_meteorite"` and `current == 1`. Do **not** change `task_key`, `task_key_uuid`, `agent_id`, `task_group_*`, `task_seq`, `task_name`, empty prompt slots (`system_prompt`, `cache_prompt_b/c/d`, `nocache_prompt`, `run_next`), or any other row.

3. Replace **`cache_prompt`** with the following text (exact contract — keep markdown `## INSTRUCTIONS` heading; flat JSON string value, `\n` newlines as neighboring rows do):

```text
## INSTRUCTIONS

Each item is a METEORITE job that already holds raw or visible text (email body, recruiter forward, or Playwright-fetched page text) — NOT a normal job-board listing scrape. CONTENT may include subject/headers/body so you can read sender, subject, and JD.

### Row contract (binding)
CONTENT rows are numbered `000:`, `001:`, … Return exactly one jobs[] object per input row, in the same order. Never drop a row — unusable rows come back with empty-string fields, not omitted. Echo that row's 3-digit index as astral_job_id (`"000"`, `"001"`, …). Never invent UUIDs for astral_job_id. Never omit astral_job_id. Never use JSON null for astral_job_id. Positional identity is required so apply can bind rows when job_link is "" or an email- token.

Return JSON with a jobs list. For each row always include these string fields (use "" when a rule says empty — never JSON null, never omit a required key):
- astral_job_id: the 3-digit CONTENT index for this row (`"000"`, `"001"`, …). Required. Always.
- company_job_id: employer external job UUID when knowable from an ATS/http link; otherwise omit the key or use "" (do not invent a fake UUID). This field is optional.
- job_title: authoritative title (see title rules)
- job_link: primary job URL or synthesized email- token (see link rules)
- jd_text: authoritative visible job-description text when the CONTENT is a real JD; otherwise ""

### Link rules
- Prefer a real http(s) ATS / job-posting URL from CONTENT when one exists → use that as job_link.
- When there is NO usable http(s) job URL but CONTENT contains a real job description → set job_link to exactly:
  email-<originalsender>-<timestamp>
  where:
  - <originalsender> is the original sender's email address discerned from CONTENT (From / forwarded-from / original recruiter). Lowercase; strip display names and angle brackets; keep @ and dots. NEVER use the candidate's own mailbox address as <originalsender>.
  - <timestamp> is the message Date / sent time visible in CONTENT, formatted UTC compact YYYYMMDDTHHMMSSZ (example: 20260805T224603Z). If no Date/sent time is visible, use 00000000T000000Z (same shape: eight digits, T, six digits, Z).
- Do NOT synthesize an email- link for ads, marketing blasts, newsletters, or unrelated non-JD content.

### Title rules
- Prefer a job title stated in the JD / body content.
- When content has no title but an email SUBJECT is present in CONTENT → use that subject as job_title.
- When there is no title in content AND no usable subject → set job_title to "" (empty string). Do not invent a title. Do not use JSON null. Do not omit the key.

### Fail / unusable content
- Ads, marketing, unrelated non-JD content, or pages with no usable job description → still return the row (same position / astral_job_id). Fail it by setting job_title="", job_link="", and jd_text="" (empty strings). You may omit company_job_id. Do not synthesize email- links for these. Do not emit JSON null for astral_job_id, job_title, job_link, or jd_text — null/omit on those keys aborts schema validation for the whole chunk. Do not omit the row.
- Do not emit grade vectors. Usable extracts = filled fields per rules above; unusable rows use empty-string fields (apply layer parks FAILED — not your concern here).
- Always return valid JSON only (no markdown fences).
```

⚠️ **Decision — empty string, never null/omit on required fields:** `agent.py` treats `required and val is None` (including omitted keys via `.get()` → `None`) as a schema miss that aborts `do_task` for the whole chunk — the parent Purpose bug. `jd_text` and `astral_job_id` stay `required: True` even after AST-1195 (sibling only nulls `job_link`/`job_title`). Empty string `""` passes the type/required check and still fails apply content gates. Instruct empty strings for fail/ads and for no-title/no-subject on `job_title`/`job_link`/`jd_text`. `company_job_id` remains `required: False` — omit or `""` is fine.

⚠️ **Decision — positional `astral_job_id` + never drop rows:** Assemble excludes real UUIDs from live CONTENT and numbers rows `000:`, `001:`, …. Binding uses positional echoes first (`_bind_response_jobs_to_claimed`); length mismatch bails the whole positional pass, and `job_link=""` / `email-…` cannot fall back via `_bind_response_jobs_by_job_link`. Dropping an ads row (or omitting `astral_job_id`) sends siblings to **METEORITE_ERROR_QUALIFY**, contradicting parent ads→**FAILED_QUALIFY** and AC7. Instruction: one object per input row, same order, echo the 3-digit index.

⚠️ **Decision — prompts only on the catalog row:** Ticket Notes say instructions-only on the `qualify_meteorite` `agent_task` record. Do **not** add `email-` prefix / timestamp format literals to `TASK_CONFIG` or a new config block here; AST-1197 owns apply recognition of the `email-` prefix. The instruction string matches parent Functional scope literally (`email-<originalsender>-<timestamp>`).

⚠️ **Decision — original sender from CONTENT, never candidate mailbox:** Parent Boundaries forbid treating the candidate email as original sender. Ruth discerns From / forwarded-from / originating recruiter from the email body/headers in assemble CONTENT (assemble wiring is AST-1197; prompts assume that content is present).

⚠️ **Decision — fail ads via empty-string fields, not a new response key:** Apply parks **METEORITE_FAILED_QUALIFY**. Do **not** invent a `fail_reason` field or grade vectors. Do **not** ask AST-1195 to null `jd_text` from this child — if that ever becomes necessary, raise it on AST-1188.

⚠️ **Decision — timestamp format `YYYYMMDDTHHMMSSZ`:** Compact UTC from Date/sent time in CONTENT. No-Date fallback is `00000000T000000Z` (same shape as the example — not fourteen bare zeros).

⚠️ **Decision — omit/empty `company_job_id` on synthesized links:** AST-1127 already made `company_job_id` optional; inventing a UUID for `email-` links would poison dedupe. Keep http-ATS UUID extract behavior when a real link exists.

⚠️ **Note for AST-1197 (not this child):** Today’s apply gate order is empty `company_job_id` → title length → `job_link.startswith("http")` → jd length. A synthesized `email-…` link yields empty resolved `company_job_id` before the http check runs, so end-to-end AC2 QUALIFY needs AST-1197 to waive **that** gate (and the http gate) for the `email-` prefix — not invent a UUID here.

4. Replace **`user_prompt`** with:

```text
Qualify these meteorite jobs. Follow the cache instructions: one jobs[] object per numbered CONTENT row (echo astral_job_id as 000/001/…; never drop a row); http(s) job_link when present; else email-<originalsender>-<timestamp> for real JDs with no ATS link; subject as job_title when content has no title; fail ads/unrelated with empty-string job_title/job_link/jd_text (never JSON null). Return astral_job_id, company_job_id, job_title, job_link, and jd_text for each row.
```

5. Set `updated_at` on that same row to the current UTC timestamp string matching neighboring rows (`YYYY-MM-DD HH:MM:SS`).

6. **Surgical fixture sync (no whole-file `cp`):** in `docs/uat-fixtures/AST-756/expected-agent_task.json`, find the object with `task_key == "qualify_meteorite"` and `current == 1` and set its `cache_prompt`, `user_prompt`, and `updated_at` to the **exact same strings** as the catalog row just edited. Do **not** `cp` the whole catalog over the fixture. Do **not** add missing fixture rows (`evaluate_meteorite`, `craft_evaluate_meteorite_rubric`) or rewrite other tasks’ prompts — that pre-existing drift is out of scope for AST-1196.

⚠️ **Decision — leave inherited fixture drift alone:** On current `origin/dev` / parent tip the catalog has 53 current rows and the AST-756 fixture 51 (fixture missing `evaluate_meteorite` + `craft_evaluate_meteorite_rubric`) plus ~13 shared rows with unrelated prompt drift. A blind `cp` would absorb all of that under this ticket’s name. Byte-identity of the two files is **unreachable** without a labeled re-baseline — escalate that to Chuckles on **AST-1188** (not this child). This stage only keeps the `qualify_meteorite` row’s three edited fields in lockstep.

7. **Post-edit gates:** only `qualify_meteorite` may differ from each pre-edit snapshot:

```bash
python3 - <<'PY'
import json

def current_by_key(path):
    return {r["task_key"]: r for r in json.load(open(path)) if r.get("current") == 1}

for label, pre_path, post_path in (
    ("catalog", "/tmp/agent_task.pre-ast-1196.json", "data/admin/agent_task.json"),
    ("fixture", "/tmp/expected-agent_task.pre-ast-1196.json", "docs/uat-fixtures/AST-756/expected-agent_task.json"),
):
    pre, post = current_by_key(pre_path), current_by_key(post_path)
    assert set(pre) == set(post), f"{label} row set changed: {set(pre)^set(post)}"
    changed = [k for k in pre if pre[k] != post[k]]
    assert changed == ["qualify_meteorite"], f"{label} unexpected changed rows: {changed}"
    print(f"OK {label} diff confined to qualify_meteorite")
PY
```

8. Do **not** edit `qualify_job_listings`, `parse_meteorite_email`, or any other task row. Do **not** edit `TASK_CONFIG["qualify_meteorite"]` response_schema / pass/fail/error states. Do **not** edit `consult.py` assemble/process (AST-1197). Do **not** rename **BOT_BLOCKED** / touch `JD_SCRAPE_FAIL_BOT` (AST-1195). Do **not** edit `tests/` — Betty’s AST-786 gate (`tests/component/core/test_repo_admin_json.py` asserting `len(rows) == 48` against a frozen key set) is already stale at 53 catalog rows; that is a **`[qa-handoff]` for Betty at Tests Ready**, not an engineer fix.

**Done when (recheck):**

```bash
python3 - <<'PY'
import json

def qm(path):
    rows = json.load(open(path))
    return next(r for r in rows if r.get("task_key") == "qualify_meteorite" and r.get("current") == 1)

cat = qm("data/admin/agent_task.json")
fix = qm("docs/uat-fixtures/AST-756/expected-agent_task.json")
for label, row in ("catalog", cat), ("fixture", fix):
    cp = row["cache_prompt"]
    up = row["user_prompt"]
    assert "email-<originalsender>-<timestamp>" in cp, label
    assert "NEVER use the candidate's own mailbox address as <originalsender>" in cp, label
    assert "exactly one jobs[] object per input row" in cp, label
    assert "3-digit index as astral_job_id" in cp, label
    assert 'astral_job_id:' in cp and '"000"' in cp, label
    assert 'set job_title to "" (empty string)' in cp or 'job_title to ""' in cp, label
    assert 'job_title="", job_link="", and jd_text=""' in cp, label
    assert "Do not omit the row" in cp or "Never drop a row" in cp, label
    assert "never JSON null" in cp or "Do not emit JSON null" in cp or "never JSON null" in up, label
    assert "00000000T000000Z" in cp, label
    assert "YYYYMMDDTHHMMSSZ" in cp, label
    assert "email-<originalsender>-<timestamp>" in up, label
    assert "one jobs[] object per numbered CONTENT row" in up or "astral_job_id as 000/001" in up, label
assert cat["cache_prompt"] == fix["cache_prompt"]
assert cat["user_prompt"] == fix["user_prompt"]
assert cat["updated_at"] == fix["updated_at"]
print("OK qualify_meteorite prompts + surgical fixture lockstep")
PY
```

## Self-Assessment

**Scope:** `minor` — one Ruth catalog row (`qualify_meteorite` prompts) plus surgical fixture field lockstep for that row; no `src/` product logic; no whole-file fixture re-baseline.

**Conf:** `high` — parent Functional scope and Joan round-1/2 fix-nows pin empty-string vs null, positional `astral_job_id`, never-drop-row binding, and surgical fixture sync.

**Risk:** `Medium` — omitting `astral_job_id` or dropping ads rows would re-create whole-chunk **METEORITE_ERROR_QUALIFY** (parent Purpose / AC7); empty-string + one-row-per-input wording are the mitigations. End-to-end QUALIFY still needs AST-1195 schema nulls + AST-1197 apply (including `company_job_id` / http waiver for `email-` links).

## Rules check (plan vs ASTRAL_CODE_RULES)

- §2.1 / `astral.config.config-source-of-truth` — no new behavior literals in config; instructions stay on the `agent_task` row (ticket boundary). Apply-side `email-` recognition remains AST-1197.
- §2.2 / `astral.agent.do-task-delegation` — still `do_task(qualify_meteorite)`; prompts ship via catalog / `apply_repo_admin_json`; no core Anthropic assembly.
- §1.1 / `astral.standards.in-scope-only` — prompts + surgical fixture fields only; no schema/state/apply creep into AST-1195 / AST-1197; no silent multi-row fixture absorption.
- §1.3 / `astral.standards.dry-and-focused-functions` — no new Python helpers.
- §1.4 / `astral.standards.no-hardcoded-sets` — no new Python state/enum sets; prompt tokens are instruction text, not a parallel registry.
- `astral.seed.agent-tables-in-repo-json` — row ships via repo JSON; no live-DB hand-edit.
- §3.3 imports — N/A (no `src/` edits).
- §3.5 naming — keep `task_key` / `task_name` `qualify_meteorite` (AST-1107 equality).
- Engineer test-tree ban — no `tests/` / bible edits; stale AST-786 `len==48` gate is Betty `[qa-handoff]`.

## Revisions

Revision 1 — 2026-08-05
Driven by: Joan `[plan-discuss] round=1 concern` (plan-rubric REVISE) — fix-now empty-string vs null/omit on required fields; fix-now forbid blind fixture `cp` / absorb inherited drift; discuss stronger Done-when assertions.
Changes: Fail/title rules + user_prompt require empty strings and forbid JSON null/omit on `job_title`/`job_link`/`jd_text`; Files Changed + Stage 1 steps switch to surgical fixture field lockstep with pre/post catalog diff gate; Done-when asserts operative clauses; note AST-786 stale `len==48` as Betty qa-handoff; escalate full fixture re-baseline to Chuckles on AST-1188; Layer cells `data`/`docs`; Risk self-assessment updated for instruction-directed chunk-abort.

Revision 2 — 2026-08-05
Driven by: Joan `[plan-discuss] round=2 concern` (plan-rubric REVISE) — fix-now enumerate required `astral_job_id`; fix-now one-row-per-input / never-drop for bind; discuss fixture pre/post gate; discuss `company_job_id` gate note for AST-1197; discuss timestamp fallback shape.
Changes: Prompt adds Row contract + `astral_job_id` always-include with positional `000`/`001`/…; fail path must still return the row; fallback timestamp `00000000T000000Z`; fixture snapshot gate mirrors catalog; Note for AST-1197 on empty-`company_job_id` before http; Done-when/user_prompt/Risk updated for binding abort risk.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject`
**Plan path:** `docs/features/meteorite/ast-1196-agent-task-synthesize-email-link-subject.md`

**Built tip:** `925178e6b1bf3da7fbb7447ca7da14358ae3a254` (`925178e6`)

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `925178e6` | qualify_meteorite cache/user prompts: email-link synthesize, subject title, empty-string fails, positional astral_job_id; surgical fixture lockstep |

### code-rubric.v1 verdict

[code-rubric] revision=1

**Rubric:** code-rubric.v1
**Ticket:** AST-1196
**Publish ref:** `9ec956e8` (`origin/sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject`)
**Overall:** CLEAN

Full active corpus (65 leaves — 18 universal + 47 scoped) swept in-session against this ticket's own diff footprint: `git diff origin/ftr/AST-1188-errors-for-qualify-meteorite-dispatch-task...origin/sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject` (paths `data/admin/agent_task.json`, `docs/uat-fixtures/AST-756/expected-agent_task.json`, `docs/features/meteorite/ast-1196-agent-task-synthesize-email-link-subject.md`, `docs/test-bible/core/repo_admin_json.md`, `tests/component/core/test_repo_admin_json.py`; change_types `{add, modify}`). Zero `src/` paths in this diff, so the entire `src/**`-scoped standards/state/layers/UI/batch/seed block is `not-applicable` on path; 6 scoped statutes apply and score `conforms` (`astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, `astral.git.betty-no-src-or-features`, `astral.git.engineer-test-tree-ban`, `astral.seed.define-approved`, `astral.seed.agent-tables-in-repo-json`); all 18 universal score `conforms`. No violations, no stragglers.

**Layer-mapping note (same gap Joan flagged at plan time):** `data/admin/**` isn't in the code-rubric's literal layer table (`src/data/**`→`data`; nothing maps top-level `data/`), so under a strict reading it contributes no layer and `astral.seed.agent-tables-in-repo-json` (layers `[core,data,utils]`) would score `not-applicable` despite its path (`data/admin/**`) matching. I scored it under the permissive reading Joan used at plan time (`data/admin` → `data` layer) so the directly-relevant statute isn't silently dropped by a rubric-table gap; verdict is `conforms` either way since there's nothing in this diff to violate it against (catalog row ships via repo JSON, no live-DB edit).

## Plan adherence

Verified mechanically, not just by reading the prose: (1) diffing `data/admin/agent_task.json` at `origin/ftr/AST-1188-...` vs the sub tip — exactly one `current==1` row changed (`qualify_meteorite`), matching Stage 1's pre/post snapshot gate; (2) same check on the AST-756 fixture — exactly one row changed there too, and `cache_prompt`/`user_prompt`/`updated_at` are byte-identical between catalog and fixture at the tip (no whole-file `cp`, no absorbed 53↔51 drift); (3) ran the plan's own Done-when assertion script against the shipped `cache_prompt`/`user_prompt` — all 13 substring checks pass, including the fragile never-candidate-mailbox sentence and the `00000000T000000Z` fallback shape Joan's round-2 review demanded. Both of Joan's round-1/round-2 fix-nows (empty-string vs null/omit; blind-`cp` fixture absorption) and both round-2 fix-nows (`astral_job_id` enumerated; never-drop row contract) are present verbatim in the shipped prompt, not just in the plan's prose.

**Pattern conformance:** cited In-scope ids `astral.git.engineer-test-tree-ban` conforms (engineer's `code(AST-1196)` commit touches only `data/admin/` + `docs/uat-fixtures/`, never `tests/`/`docs/test-bible/`). `astral.config.config-source-of-truth`, `astral.agent.do-task-delegation`, `astral.standards.in-scope-only`, `astral.standards.dry-and-focused-functions`, `astral.standards.no-hardcoded-sets` all score `not-applicable` on this diff (their path predicate is `src/**`; this child touches zero `src/` files) — same "mechanically excluded, scored in spirit" situation Joan already called out at plan time; nothing to add. **Advisory (recurring, not fix-now/discuss):** `pattern.config.config-block` / `pattern.batch.entity-claim-process-release` under Considered-but-excluded again aren't ids in the active corpus (no `pattern.*` namespace — same slip flagged on AST-1195's review); likely meant `astral.config.config-source-of-truth` / `astral.batch.claim-process-release`.

**What's solid:** Betty's Tests Ready fix for the stale AST-786 `len(rows)==48` gate replaces whole-file byte-identity with a catalog key-set lock (53 rows) plus a dedicated `TestAst1196QualifyMeteoritePromptContract` class that checks the shipped prompt text directly — closing exactly the gate the plan flagged as `[qa-handoff]` rather than an engineer `tests/` edit.

## Frame diff

(none) — implementation matches the plan doc's Files Changed / Stage 1 as written; no adds or moves applied to this description.

context_tokens≈75000

— Radia

---

## Resolution

**Date:** 2026-08-06  
**Review tip:** `e086bb26` (`docs(AST-1196): Radia review — clean`) — **Overall: CLEAN**

No fix-now or discuss items. Radia verified Stage 1 mechanically (single-row catalog/fixture diffs, Done-when assertions on shipped prompts, Joan R1/R2 fix-nows present in prompt text). Frame diff: none.

**Advisory noted (description only):** Considered-but-excluded `pattern.config.config-block` / `pattern.batch.entity-claim-process-release` are not active-corpus ids — corrected on Linear to `astral.config.config-source-of-truth` / `astral.batch.claim-process-release` (sibling-owned; still excluded for this child).

No product or test-tree changes on resolve.
