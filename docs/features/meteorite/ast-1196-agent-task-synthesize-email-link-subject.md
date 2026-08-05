# AST-1196 — agent_task: synthesize email link + subject title

**Linear:** [AST-1196](https://linear.app/astralcareermatch/issue/AST-1196/agent-task-synthesize-email-link-subject-title-errors-for-qualify)
**Parent:** [AST-1188](https://linear.app/astralcareermatch/issue/AST-1188/errors-for-qualify-meteorite-dispatch-task) — Errors for qualify_meteorite dispatch task
**Publish ref:** `origin/sub/AST-1188/AST-1196-agent-task-synthesize-email-link-subject`

Update the current Ruth `qualify_meteorite` `agent_task` instructions so that when CONTENT has a usable job description but no ATS/http job URL, Ruth returns a synthesized `job_link` of the form `email-<originalsender>-<timestamp>`; when CONTENT has no title but an email subject is present, Ruth uses that subject as `job_title`; original sender is discerned from email CONTENT (never the candidate mailbox); ads / unrelated non-JD content are failed (empty/unusable fields). Does **not** own schema nullability / **BOT_BLOCKED** registry (AST-1195) or consult assemble/apply / http-gate waiver / Style D (AST-1197).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | Rewrite `qualify_meteorite` `cache_prompt` (+ short `user_prompt` touch); bump `updated_at` | data/admin |
| `docs/uat-fixtures/AST-756/expected-agent_task.json` | Byte-identical copy after the prompt edit (AST-786 seed gate) | docs |

**No changes expected:** `src/utils/config.py`, `src/core/consult.py`, `src/core/agent.py`, `src/core/dispatcher.py`, `src/ui/**`, other `agent_task` rows, `tests/` / bible (Betty after Code Complete). Do **not** hand-edit the live DB — startup `apply_repo_admin_json` ships the row.

## Stage 1: `qualify_meteorite` prompt — email-link synthesize + subject title

**Done when:** The current `qualify_meteorite` catalog row instructs Ruth to (a) synthesize `email-<originalsender>-<timestamp>` when there is no usable http(s) ATS/job link but CONTENT holds a real JD, (b) use SUBJECT as `job_title` when content has no title, (c) never use the candidate mailbox as original sender, (d) fail ads/unrelated content via empty/unusable fields; AST-756 fixture is byte-identical to repo `agent_task.json`; no other task rows change.

1. In `data/admin/agent_task.json`, locate the single object with `task_key == "qualify_meteorite"` and `current == 1`. Do **not** change `task_key`, `task_key_uuid`, `agent_id`, `task_group_*`, `task_seq`, `task_name`, empty prompt slots (`system_prompt`, `cache_prompt_b/c/d`, `nocache_prompt`, `run_next`), or any other row.

2. Replace **`cache_prompt`** with the following text (exact contract — keep markdown `## INSTRUCTIONS` heading; flat JSON string value, `\n` newlines as neighboring rows do):

```text
## INSTRUCTIONS

Each item is a METEORITE job that already holds raw or visible text (email body, recruiter forward, or Playwright-fetched page text) — NOT a normal job-board listing scrape. CONTENT may include subject/headers/body so you can read sender, subject, and JD.

Return JSON with a jobs list. For each astral_job_id provide:
- company_job_id: employer external job UUID when knowable from an ATS/http link; otherwise omit or empty string (do not invent a fake UUID)
- job_title: authoritative title (see title rules)
- job_link: primary job URL or synthesized email- token (see link rules)
- jd_text: authoritative visible job-description text when the CONTENT is a real JD

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
- When there is no title in content AND no usable subject → leave job_title empty / null (do not invent a title).

### Fail / unusable content
- Ads, marketing, unrelated non-JD content, or pages with no usable job description → fail this row: empty/null job_title, job_link, and jd_text (and omit company_job_id). Do not synthesize email- links for these.
- Do not emit grade vectors. Usable extracts = filled fields per rules above; unusable rows use empty/null fields (apply layer parks FAILED — not your concern here).
- Always return valid JSON only (no markdown fences).
```

⚠️ **Decision — prompts only on the catalog row:** Ticket Notes say instructions-only on the `qualify_meteorite` `agent_task` record. Do **not** add `email-` prefix / timestamp format literals to `TASK_CONFIG` or a new config block here; AST-1197 owns apply recognition of the `email-` prefix. The instruction string matches parent Functional scope literally (`email-<originalsender>-<timestamp>`).

⚠️ **Decision — original sender from CONTENT, never candidate mailbox:** Parent Boundaries forbid treating the candidate email as original sender. Ruth discerns From / forwarded-from / originating recruiter from the email body/headers in assemble CONTENT (assemble wiring is AST-1197; prompts assume that content is present).

⚠️ **Decision — fail ads via empty fields, not a new response key:** Schema/apply siblings own nullability and **METEORITE_FAILED_QUALIFY** parking. Instructions tell Ruth to leave fields empty/null for ads/unrelated content and never synthesize `email-` for those rows. Do **not** invent a `fail_reason` field or grade vectors.

⚠️ **Decision — timestamp format `YYYYMMDDTHHMMSSZ`:** Compact UTC from Date/sent time in CONTENT so the token is stable and parse-friendly. Fallback `00000000000000Z` when Date is absent (still satisfies the `email-…` shape for AC2 instruction portion; uniqueness/dedupe is apply-layer).

⚠️ **Decision — omit/empty `company_job_id` on synthesized links:** AST-1127 already made `company_job_id` optional; inventing a UUID for `email-` links would poison dedupe. Keep http-ATS UUID extract behavior when a real link exists.

3. Replace **`user_prompt`** with:

```text
Qualify these meteorite jobs. Follow the cache instructions: http(s) job_link when present; else email-<originalsender>-<timestamp> for real JDs with no ATS link; subject as job_title when content has no title; fail ads/unrelated with empty fields. Return company_job_id, job_title, job_link, and jd_text for each astral_job_id.
```

4. Set `updated_at` on that same row to the current UTC timestamp string matching neighboring rows (`YYYY-MM-DD HH:MM:SS`).

5. Copy bytes so the seed fixture matches the repo catalog (AST-786 gate — same as AST-1089 / AST-1144):

```bash
cp data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json
cmp -s data/admin/agent_task.json docs/uat-fixtures/AST-756/expected-agent_task.json && echo OK
```

6. Do **not** edit `qualify_job_listings`, `parse_meteorite_email`, or any other task row. Do **not** edit `TASK_CONFIG["qualify_meteorite"]` response_schema / pass/fail/error states. Do **not** edit `consult.py` assemble/process (AST-1197). Do **not** rename **BOT_BLOCKED** / touch `JD_SCRAPE_FAIL_BOT` (AST-1195).

**Done when (recheck):**

```bash
python3 - <<'PY'
import json
rows = json.load(open("data/admin/agent_task.json"))
row = next(r for r in rows if r.get("task_key") == "qualify_meteorite" and r.get("current") == 1)
cp = row["cache_prompt"]
assert "email-<originalsender>-<timestamp>" in cp
assert "NEVER use the candidate" in cp or "never the candidate" in cp.lower() or "NEVER use the candidate's own mailbox" in cp
assert "SUBJECT" in cp or "subject" in cp
assert "ads" in cp.lower() or "Ads" in cp
assert "YYYYMMDDTHHMMSSZ" in cp
up = row["user_prompt"]
assert "email-<originalsender>-<timestamp>" in up
a = open("data/admin/agent_task.json", "rb").read()
b = open("docs/uat-fixtures/AST-756/expected-agent_task.json", "rb").read()
assert a == b, "AST-756 fixture must be byte-identical to data/admin/agent_task.json"
print("OK qualify_meteorite prompts + fixture")
PY
```

## Self-Assessment

**Scope:** `minor` — one Ruth catalog row (`qualify_meteorite` prompts) plus AST-756 fixture byte-sync; no `src/` product logic.

**Conf:** `high` — parent Functional scope and child Notes pin the instruction contract; prior meteorite plans (AST-1060 / AST-1089 / AST-1144) establish the exact catalog + fixture pattern.

**Risk:** `Medium` — bad prompt wording can push Ruth to invent candidate-mailbox senders, synthesize `email-` for ads, or skip subject-as-title; apply sibling (AST-1197) and schema nulls (AST-1195) must land for end-to-end AC, but this ticket’s instruction portion is verifiable from the catalog text alone.

## Rules check (plan vs ASTRAL_CODE_RULES)

- §2.1 / `astral.config.config-source-of-truth` — no new behavior literals in config; instructions stay on the `agent_task` row (ticket boundary). Apply-side `email-` recognition remains AST-1197.
- §2.2 / `astral.agent.do-task-delegation` — still `do_task(qualify_meteorite)`; prompts ship via catalog / `apply_repo_admin_json`; no core Anthropic assembly.
- §1.1 / `astral.standards.in-scope-only` — prompts + fixture only; no schema/state/apply creep into AST-1195 / AST-1197.
- §1.3 / `astral.standards.dry-and-focused-functions` — no new Python helpers.
- §1.4 / `astral.standards.no-hardcoded-sets` — no new Python state/enum sets; prompt tokens are instruction text, not a parallel registry.
- §3.3 imports — N/A (no `src/` edits).
- §3.5 naming — keep `task_key` / `task_name` `qualify_meteorite` (AST-1107 equality).
- Engineer test-tree ban — no `tests/` / bible edits.
