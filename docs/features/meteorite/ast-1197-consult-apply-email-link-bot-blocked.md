# AST-1197 — Consult apply: email-link QUALIFY, BOT_BLOCKED, FAILED_QUALIFY park, Style D

**Linear:** [AST-1197](https://linear.app/astralcareermatch/issue/AST-1197/consult-apply-email-link-qualify-bot-blocked-failed-qualify-park-style)
**Parent:** [AST-1188](https://linear.app/astralcareermatch/issue/AST-1188/errors-for-qualify-meteorite-dispatch-task) — Errors for qualify_meteorite dispatch task
**Publish ref:** `origin/sub/AST-1188/AST-1197-consult-apply-email-link-bot-blocked`

After AST-1195 (schema nulls + **BOT_BLOCKED** registry) and AST-1196 (`agent_task` synthesize / subject / empty-string fail rows): wire `qualify_meteorite` **assemble** so Ruth sees email CONTENT, and **process** so per-row outcomes land correctly — synthesized `email-…` links may **METEORITE_QUALIFIED** (http + empty-`company_job_id` gates waived for that prefix); Cloudflare/challenge JD → **BOT_BLOCKED**; no-title/no-subject → **METEORITE_FAILED_QUALIFY**; mixed chunks do not all-ERROR; `debug=True` Style D records link/title source and bot/fail reasons. Does **not** own schema/registry rename (AST-1195) or `agent_task` prompt authoring (AST-1196).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `TASK_CONFIG["qualify_meteorite"]`: `email_link_prefix`, `bot_blocked_state`; add `"Additional Verification Required"` to `TRACKER_CONFIG["jd_classifier"]["bot_signals"]` | utils |
| `src/core/consult.py` | `qualify_meteorite` assemble CONTENT label; process: bot → **BOT_BLOCKED**, `email-` waivers, Style D detail | core |
| `src/ui/api/api_admin.py` | Ad-hoc `qualify_meteorite` assemble lockstep with consult | ui |

No `agent_task` / `data/admin` edits, no `JOB_STATES` rename work, no `tests/` / bible (Betty after Code Complete).

## Stage 1: Config — email-link prefix + bot-blocked state + challenge signal

**Done when:** `TASK_CONFIG["qualify_meteorite"]` exposes `email_link_prefix == "email-"` and `bot_blocked_state == "BOT_BLOCKED"`; `TRACKER_CONFIG["jd_classifier"]["bot_signals"]` contains `"Additional Verification Required"`; `python3 -c "from src.utils import config"` succeeds. No consult/apply behavior changes yet.

1. In `src/utils/config.py` `TASK_CONFIG["qualify_meteorite"]`, after the existing orchestration keys (`fail_state` / `error_state` / `min_jd_chars` cluster), add:

```python
"email_link_prefix": "email-",  # AST-1197: synthesized link; waive http + empty company_job_id gates
"bot_blocked_state": "BOT_BLOCKED",  # AST-1197: challenge/Cloudflare JD → universal bot state (AST-1195)
```

2. Immediately after the existing module-level asserts on `qualify_meteorite` `job_link` / `job_title` `required is False`, add:

```python
assert TASK_CONFIG["qualify_meteorite"]["email_link_prefix"] == "email-"
assert TASK_CONFIG["qualify_meteorite"]["bot_blocked_state"] == "BOT_BLOCKED"
assert "BOT_BLOCKED" in JOB_STATES
assert "METEORITE_NEW" in JOB_STATES["BOT_BLOCKED"]["prior_states"]
```

3. In `TRACKER_CONFIG["jd_classifier"]["bot_signals"]`, append the string `"Additional Verification Required"` (parent AC names this challenge phrase; keep existing Cloudflare / “Just a moment” / Ray ID signals unchanged).

⚠️ **Decision — prefix + bot state in TASK_CONFIG, signals stay on jd_classifier:** Apply recognition of `email-` and the destination state id must not be inline magic strings in `consult.py` (`astral.standards.no-hardcoded-sets` / config-source-of-truth). Bot **detection** reuses the existing `TRACKER_CONFIG["jd_classifier"]` corpus via `_classify_jd` (AST-1195 already pointed gazer at **BOT_BLOCKED**); this stage only adds the missing parent-named challenge phrase. Do **not** invent a parallel meteorite-only signal list.

## Stage 2: Assemble — CONTENT includes stored email / JD body (+ admin lockstep)

**Done when:** `consult.qualify_meteorite` assemble emits numbered rows with `job_link:` plus a `CONTENT:` block whose body is the job’s stored `job_data[job_description]` (email HTML with subject wrapper for body-ingest, or scraped visible text for link-ingest); `api_admin` ad-hoc `qualify_meteorite` live_content builder matches that shape byte-for-byte for the same jobs; no process/gate changes yet.

1. In `src/core/consult.py` inside `qualify_meteorite`, replace the assemble closure so each row is:

```text
{iii}: job_link: {job_link}
CONTENT:
{job_description}
```

Concrete implementation (same `jd_key` as today):

```python
def assemble(jobs):
    lines = [
        f"{i:03d}: job_link: {j.get('job_link') or ''}\n"
        f"CONTENT:\n{(j.get('job_data') or {}).get(jd_key, '') or ''}"
        for i, j in enumerate(jobs)
    ]
    return "METEORITE JOBS:\n" + "\n".join(lines)
```

2. In `src/ui/api/api_admin.py` ad-hoc assemble branch for `task_key == "qualify_meteorite"`, change the per-job line builder to the **identical** `CONTENT:` shape (keep `METEORITE JOBS:` prefix and `len(lines):03d` indexing). Comment remains “lockstep with consult.qualify_meteorite assemble”.

⚠️ **Decision — no new job_data key / no second email fetch:** Parent Functional scope and Boundaries say assemble sends the email body Ruth needs and forbid a separate pre-Ruth plumbing child. Body-mode create already stores stripped email HTML (AST-1049 subject wrapper + body) under `job_data["job_description"]`; link-mode stores Playwright visible text there. Relabeling the assemble field from `job_description:` → `CONTENT:` aligns with AST-1196 prompt language (`CONTENT` / subject-in-content) without inventing storage. Do **not** re-fetch Gmail in consult.

⚠️ **Decision — do not parse SUBJECT into a separate assemble field:** Ruth’s agent_task already instructs subject-as-title when content has no title; the subject lives inside the email HTML header when present. A second parsed `subject:` line would duplicate AST-1049 structure and risk drift. Style D title-source inference (Stage 3) may read the subject from input HTML for debug only.

## Stage 3: Process — BOT_BLOCKED, email- QUALIFY waivers, FAILED_QUALIFY, Style D

**Done when:** For a claimed **METEORITE_NEW** row in `qualify_meteorite.process`: (a) input or Ruth `jd_text` classified `bot` by `_classify_jd` → transition **BOT_BLOCKED** (not QUALIFIED / not FAILED_QUALIFY); (b) `job_link` starting with `cfg["email_link_prefix"]` skips empty-`company_job_id` and `startswith("http")` fails, and with title+jd floors met reaches **METEORITE_QUALIFIED** via existing `initialize_job` + `pass_state`; (c) empty/short title (no-subject/no-title) → **METEORITE_FAILED_QUALIFY**; (d) non-http non-email link or short jd → **METEORITE_FAILED_QUALIFY**; (e) `debug=True` Style D headers + `|` detail include `link_source`, `title_source`, and bot/fail reasons; (f) process never raises on weak rows — mixed chunks keep per-row outcomes (envelope ERROR path unchanged in `_run_batch_consult`).

1. At the top of the `process` closure in `qualify_meteorite` (after reading response fields), keep existing link resolution, then extend it so synthesized email links are first-class:

```python
email_prefix = cfg["email_link_prefix"]
# Ruth http(s) wins; else Create-time ATS URL; else Ruth email- / other token.
if ruth_link.startswith("http"):
    job_link = ruth_link
    link_source = "http-AI"
elif input_link.startswith("http"):
    job_link = input_link
    link_source = "http-input"
elif ruth_link.startswith(email_prefix):
    job_link = ruth_link
    link_source = "email-synthesized"
else:
    job_link = ruth_link
    link_source = "neither"
```

2. Resolve `company_job_id` via existing `_resolve_company_job_id` (unchanged). Keep `id_source` labels as today (`AI` / `UUID-from-job_link` / `neither`).

3. **Title source (debug / detail only)** — derive from input CONTENT, do not change `job_title`:

- Read `input_jd = ((input_job.get("job_data") or {}).get(jd_key, "") or "")`.
- Subject probe: if `email-subject` markup is present, take the first `<h1>…</h1>` inner text stripped; else `""`.
- `title_source = "subject"` when `job_title` and subject are both non-empty and `job_title.casefold() == subject.casefold()`; elif `job_title`: `"content"`; else `"neither"`.

Use a tiny local helper inside `qualify_meteorite` (or module-private `_qualify_meteorite_email_subject(html: str) -> str`) with `re` / string find — **no** BeautifulSoup import in consult for this (gazer already owns HTML soup on ingest). Prefer `re.search(r'class="email-subject"[^>]*>.*?<h1>(.*?)</h1>', input_jd, re.I|re.S)` or equivalent; on no match return `""`.

4. **Bot / challenge gate (before content fails)** — lazy-import and call gazer’s classifier:

```python
from src.core.gazer import _classify_jd  # lazy: same pattern as other consult→gazer imports
```

- If `_classify_jd(input_jd) == "bot"` **or** (`jd_text` non-empty and `_classify_jd(jd_text) == "bot"`):
  - `to_state = cfg["bot_blocked_state"]`  # **BOT_BLOCKED**
  - `_transition_job_state_for_task(task_key, [aid], to_state)`
  - When `debug`: Style D `debug_index` outcome `f"bot block -> {to_state}"` + `debug_detail` with `gate=bot_classification`, `link_source=…`, `title_source=…`, `company_job_id=…`, `title=…`, `link=…`, `jd_chars=…`
  - When not debug: `logger.info` with job title/aid → `to_state [bot_classification]`
  - `return to_state`
- Do **not** map cookie/closed/missing classifications to **BOT_BLOCKED** — only `"bot"`. Other weak content continues to content fail gates → **METEORITE_FAILED_QUALIFY**.

⚠️ **Decision — classify input JD and Ruth jd_text; bot only:** Link-ingest Cloudflare pages land in `job_data["job_description"]` before Ruth runs; Ruth may empty `jd_text` on non-JD (AST-1196 fail instruction), which would miss **BOT_BLOCKED** if we only classified the response. Checking input first preserves parent AC5. Checking response catches echo-through challenge text. Cookie/closed/missing stay fail_state — parent only requires bot/challenge → **BOT_BLOCKED**, and AST-1195 already set `BOT_BLOCKED` priors to include `METEORITE_NEW`.

⚠️ **Decision — bot before email-/title fails:** A challenge page must not park on **METEORITE_FAILED_QUALIFY** or QUALIFY via an `email-` waiver. Bot is a human-attention state on the universal id.

5. **Content fail gates** — replace the current ordered checks with:

```python
is_email_link = job_link.startswith(email_prefix)
fail_reason = None
if not company_job_id and not is_email_link:
    fail_reason = "empty company_job_id"
elif len(job_title) < min_title:
    fail_reason = f"title too short len={len(job_title)} min={min_title}"
elif not job_link.startswith("http") and not is_email_link:
    fail_reason = f"job_link not http/email: {job_link!r}"
elif len(jd_text) < min_jd:
    fail_reason = f"jd_text too short len={len(jd_text)} min={min_jd}"
```

On `fail_reason`: transition `cfg["fail_state"]` (**METEORITE_FAILED_QUALIFY**); Style D / info logging as today, but include `link_source`, `title_source`, and `gate={fail_reason}` in the detail line.

⚠️ **Decision — waive empty company_job_id for email- only (AST-1196 note):** Today’s gate order fails empty `company_job_id` before the http check, so a synthesized `email-…` link never reaches QUALIFY. Waive that gate and the http gate when `job_link.startswith(email_prefix)`. Do **not** invent a UUID for identity — `initialize_job` only enforces identity collision when both `company_job_id` and title are non-empty; empty `company_job_id` + title + `email-` link is a legal save (AST-1127 optional company_job_id).

6. **Pass path** — unchanged structure: build `parsed_job` with `company_job_id`, `job_title`, `job_link`, `jd_key: jd_text`; `tracker.initialize_job`; on collision return `fail_state`; else transition `cfg["pass_state"]` (**METEORITE_QUALIFIED**). When `debug`, Style D detail must include `link_source`, `title_source`, found vs recorded fields (keep existing recorded re-read via `tracker.get_job`).

7. Do **not** change `_run_batch_consult` envelope ERROR routing — genuine unparseable / `do_task` failure still → **METEORITE_ERROR_QUALIFY** for the chunk (parent AC7 / ticket AC5). Per-row process must not raise on weak rows so mixed chunks keep independent outcomes (parent AC1).

8. Do **not** edit `_bind_response_jobs_by_job_link` — positional bind (AST-1196) is the primary path for `email-` / empty links; claim-time links are usually http or empty, so email- tokens will not match input links.

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1188/AST-1197-consult-apply-email-link-bot-blocked`.
- Do not edit `data/admin/agent_task.json`, `JOB_STATES` rename consumers (already AST-1195), frontend TS, or `tests/`.
- If a step is ambiguous or the codebase has drifted — stop and comment on **parent** AST-1188 with the standard blocked format.

## Self-Assessment

**Scope:** `Single-Component` — `qualify_meteorite` assemble/process in `consult.py`, matching admin assemble, plus TASK_CONFIG / jd_classifier knobs in `config.py`.

**Conf:** `high` — siblings shipped schema + prompts; apply gaps are the known gate order (`company_job_id` before http) and missing bot branch; `_classify_jd` + `initialize_job` empty-cid behavior already exist.

**Risk:** `Medium` — wrong bot/email gate order could QUALIFY challenge pages or park real email-JD rows on FAILED/ERROR; Style D is debug-only. Envelope ERROR path left intentional for true `do_task` failures.

## Code-rules check

- §1.3 / `astral.standards.dry-and-focused-functions` — reuse `_classify_jd` and `_resolve_company_job_id`; small subject probe helper only.
- §1.4 / `astral.standards.no-hardcoded-sets` — `email_link_prefix` + `bot_blocked_state` in TASK_CONFIG; bot signals stay on `jd_classifier`.
- §1.5.1 / `astral.standards.debug-contract-gated` — Style D only when `debug=True` via existing logger helpers.
- §2.1 / `astral.config.config-source-of-truth` — knobs in config; no new parallel registries.
- §2.4 / `astral.batch.claim-process-release` — still claim → `_run_batch_consult` → per-row process → release; no claim API changes.
- §2.6 / `astral.state.core-decides-transitions` + `astral.state.job-prior-states-enforced` — core chooses **BOT_BLOCKED** / fail / pass; priors already allow `METEORITE_NEW` → **BOT_BLOCKED** (AST-1195).
- §3.3 imports — lazy `from src.core.gazer import _classify_jd` inside process (existing consult↔gazer pattern).
- Out of scope: `astral.agent.do-task-delegation` prompt text (AST-1196); schema required flags (AST-1195).
