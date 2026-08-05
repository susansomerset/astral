# AST-1196 — agent_task: synthesize email link + subject title

**Linear:** [AST-1196](https://linear.app/astralcareermatch/issue/AST-1196/agent-task-synthesize-email-link-subject-title-errors-for-qualify)
**Parent:** [AST-1188](https://linear.app/astralcareermatch/issue/AST-1188/errors-for-qualify-meteorite-dispatch-task) — Errors for qualify_meteorite dispatch task
**Publish ref:** `origin/sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject`

Update the current Ruth `qualify_meteorite` `agent_task` instructions so that when CONTENT has a usable job description but no ATS/http job URL, Ruth returns a synthesized `job_link` of the form `email-<originalsender>-<timestamp>`; when CONTENT has no title but an email subject is present, Ruth uses that subject as `job_title`; original sender is discerned from email CONTENT (never the candidate mailbox); ads / unrelated non-JD content are failed via **empty-string** fields (never JSON `null` / omit on required keys). Does **not** own schema nullability / **BOT_BLOCKED** registry (AST-1195) or consult assemble/apply / http-gate waiver / Style D (AST-1197).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | Rewrite `qualify_meteorite` `cache_prompt` (+ short `user_prompt` touch); bump `updated_at` — **only this row** | data |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Surgical update of the existing `qualify_meteorite` row’s prompts/`updated_at` to match catalog — **no whole-file `cp`** | docs |

**No changes expected:** `src/utils/config.py`, `src/core/consult.py`, `src/core/agent.py`, `src/core/dispatcher.py`, `src/ui/**`, other `agent_task` rows, `tests/` / bible (Betty after Code Complete). Do **not** hand-edit the live DB — startup `apply_repo_admin_json` ships the row. Do **not** absorb pre-existing catalog↔fixture drift (missing rows / other tasks’ prompts) into this ticket.

## Stage 1: `qualify_meteorite` prompt — email-link synthesize + subject title

**Done when:** The current `qualify_meteorite` catalog row instructs Ruth to (a) synthesize `email-<originalsender>-<timestamp>` when there is no usable http(s) ATS/job link but CONTENT holds a real JD, (b) use SUBJECT as `job_title` when content has no title, (c) never use the candidate mailbox as original sender, (d) fail ads/unrelated content with **empty-string** `job_title` / `job_link` / `jd_text` (omit only optional `company_job_id`); the AST-756 fixture’s `qualify_meteorite` row matches those same three fields; no other catalog or fixture rows change in the commit.

1. **Pre-edit snapshot (gate against silent multi-row edits):** before changing anything, copy the catalog to a temp path for later diff:

```bash
cp data/admin/agent_task.json /tmp/agent_task.pre-ast-1196.json
```

2. In `data/admin/agent_task.json`, locate the single object with `task_key == "qualify_meteorite"` and `current == 1`. Do **not** change `task_key`, `task_key_uuid`, `agent_id`, `task_group_*`, `task_seq`, `task_name`, empty prompt slots (`system_prompt`, `cache_prompt_b/c/d`, `nocache_prompt`, `run_next`), or any other row.

3. Replace **`cache_prompt`** with the following text (exact contract — keep markdown `## INSTRUCTIONS` heading; flat JSON string value, `\n` newlines as neighboring rows do):

```text
## INSTRUCTIONS

Each item is a METEORITE job that already holds raw or visible text (email body, recruiter forward, or Playwright-fetched page text) — NOT a normal job-board listing scrape. CONTENT may include subject/headers/body so you can read sender, subject, and JD.

Return JSON with a jobs list. For each astral_job_id always include these string fields (use "" when a rule says empty — never JSON null, never omit a required key):
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
  - <timestamp> is the message Date / sent time visible in CONTENT, formatted UTC compact YYYYMMDDTHHMMSSZ (example: 20260805T224603Z). If no Date/sent time is visible, use 00000000000000Z.
- Do NOT synthesize an email- link for ads, marketing blasts, newsletters, or unrelated non-JD content.

### Title rules
- Prefer a job title stated in the JD / body content.
- When content has no title but an email SUBJECT is present in CONTENT → use that subject as job_title.
- When there is no title in content AND no usable subject → set job_title to "" (empty string). Do not invent a title. Do not use JSON null. Do not omit the key.

### Fail / unusable content
- Ads, marketing, unrelated non-JD content, or pages with no usable job description → fail this row by setting job_title="", job_link="", and jd_text="" (empty strings). You may omit company_job_id. Do not synthesize email- links for these. Do not emit JSON null for job_title, job_link, or jd_text — null/omit on those keys aborts schema validation for the whole chunk.
- Do not emit grade vectors. Usable extracts = filled fields per rules above; unusable rows use empty-string fields (apply layer parks FAILED via existing min_job_title_length / min_jd_chars gates — not your concern here).
- Always return valid JSON only (no markdown fences).
```

⚠️ **Decision — empty string, never null/omit on required fields:** `agent.py` treats `required and val is None` (including omitted keys via `.get()` → `None`) as a schema miss that aborts `do_task` for the whole chunk — the parent Purpose bug. `jd_text` stays `required: True` even after AST-1195 (sibling only nulls `job_link`/`job_title`). Empty string `""` passes the type/required check and still fails apply content gates (`min_job_title_length: 5`, `min_jd_chars: 40`). Instruct empty strings for fail/ads and for no-title/no-subject; say the same for `job_link`/`job_title` so the wording is correct whether or not AST-1195 has landed. `company_job_id` remains `required: False` — omit or `""` is fine.

⚠️ **Decision — prompts only on the catalog row:** Ticket Notes say instructions-only on the `qualify_meteorite` `agent_task` record. Do **not** add `email-` prefix / timestamp format literals to `TASK_CONFIG` or a new config block here; AST-1197 owns apply recognition of the `email-` prefix. The instruction string matches parent Functional scope literally (`email-<originalsender>-<timestamp>`).

⚠️ **Decision — original sender from CONTENT, never candidate mailbox:** Parent Boundaries forbid treating the candidate email as original sender. Ruth discerns From / forwarded-from / originating recruiter from the email body/headers in assemble CONTENT (assemble wiring is AST-1197; prompts assume that content is present).

⚠️ **Decision — fail ads via empty-string fields, not a new response key:** Apply parks **METEORITE_FAILED_QUALIFY**. Do **not** invent a `fail_reason` field or grade vectors. Do **not** ask AST-1195 to null `jd_text` from this child — if that ever becomes necessary, raise it on AST-1188.

⚠️ **Decision — timestamp format `YYYYMMDDTHHMMSSZ`:** Compact UTC from Date/sent time in CONTENT so the token is stable and parse-friendly. Fallback `00000000000000Z` when Date is absent (still satisfies the `email-…` shape for AC2 instruction portion; uniqueness/dedupe is apply-layer).

⚠️ **Decision — omit/empty `company_job_id` on synthesized links:** AST-1127 already made `company_job_id` optional; inventing a UUID for `email-` links would poison dedupe. Keep http-ATS UUID extract behavior when a real link exists.

4. Replace **`user_prompt`** with:

```text
Qualify these meteorite jobs. Follow the cache instructions: http(s) job_link when present; else email-<originalsender>-<timestamp> for real JDs with no ATS link; subject as job_title when content has no title; fail ads/unrelated with empty-string job_title/job_link/jd_text (never JSON null). Return company_job_id, job_title, job_link, and jd_text for each astral_job_id.
```

5. Set `updated_at` on that same row to the current UTC timestamp string matching neighboring rows (`YYYY-MM-DD HH:MM:SS`).

6. **Surgical fixture sync (no whole-file `cp`):** in `docs/uat-fixtures/AST-756/expected-agent_task.json`, find the object with `task_key == "qualify_meteorite"` and `current == 1` and set its `cache_prompt`, `user_prompt`, and `updated_at` to the **exact same strings** as the catalog row just edited. Do **not** `cp` the whole catalog over the fixture. Do **not** add missing fixture rows (`evaluate_meteorite`, `craft_evaluate_meteorite_rubric`) or rewrite other tasks’ prompts — that pre-existing drift is out of scope for AST-1196.

⚠️ **Decision — leave inherited fixture drift alone:** On current `origin/dev` / parent tip the catalog has 53 current rows and the AST-756 fixture 51 (fixture missing `evaluate_meteorite` + `craft_evaluate_meteorite_rubric`) plus ~13 shared rows with unrelated prompt drift. A blind `cp` would absorb all of that under this ticket’s name. Byte-identity of the two files is **unreachable** without a labeled re-baseline — escalate that to Chuckles on **AST-1188** (not this child). This stage only keeps the `qualify_meteorite` row’s three edited fields in lockstep.

7. **Post-edit catalog gate:** only `qualify_meteorite` may differ from the pre-edit snapshot:

```bash
python3 - <<'PY'
import json
pre = {r["task_key"]: r for r in json.load(open("/tmp/agent_task.pre-ast-1196.json")) if r.get("current") == 1}
post = {r["task_key"]: r for r in json.load(open("data/admin/agent_task.json")) if r.get("current") == 1}
assert set(pre) == set(post), f"row set changed: {set(pre)^set(post)}"
changed = [k for k in pre if pre[k] != post[k]]
assert changed == ["qualify_meteorite"], f"unexpected changed rows: {changed}"
print("OK catalog diff confined to qualify_meteorite")
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
    assert 'set job_title to "" (empty string)' in cp or 'job_title to ""' in cp, label
    assert 'job_title="", job_link="", and jd_text=""' in cp or 'job_title="", job_link="", and jd_text=' in cp, label
    assert "never JSON null" in cp or "Do not emit JSON null" in cp or "never JSON null" in up, label
    assert "YYYYMMDDTHHMMSSZ" in cp, label
    assert "email-<originalsender>-<timestamp>" in up, label
    assert "empty-string" in up or "empty string" in up.lower() or "never JSON null" in up, label
assert cat["cache_prompt"] == fix["cache_prompt"]
assert cat["user_prompt"] == fix["user_prompt"]
assert cat["updated_at"] == fix["updated_at"]
print("OK qualify_meteorite prompts + surgical fixture lockstep")
PY
```

## Self-Assessment

**Scope:** `minor` — one Ruth catalog row (`qualify_meteorite` prompts) plus surgical fixture field lockstep for that row; no `src/` product logic; no whole-file fixture re-baseline.

**Conf:** `high` — parent Functional scope and child Notes pin the instruction contract; Joan round-1 fix-nows pin empty-string vs null and surgical fixture sync; prior meteorite plans establish the catalog edit pattern.

**Risk:** `Medium` — instructing JSON `null`/omit on still-required fields would re-create the whole-chunk schema abort (parent Purpose); empty-string wording + surgical fixture sync are the mitigations. End-to-end QUALIFY still needs AST-1195 schema nulls + AST-1197 apply.

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
