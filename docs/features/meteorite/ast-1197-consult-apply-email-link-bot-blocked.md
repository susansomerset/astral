# AST-1197 — Consult apply: email-link QUALIFY, BOT_BLOCKED, FAILED_QUALIFY park, Style D

**Linear:** [AST-1197](https://linear.app/astralcareermatch/issue/AST-1197/consult-apply-email-link-qualify-bot-blocked-failed-qualify-park-style)
**Parent:** [AST-1188](https://linear.app/astralcareermatch/issue/AST-1188/errors-for-qualify-meteorite-dispatch-task) — Errors for qualify_meteorite dispatch task
**Publish ref:** `origin/sub/AST-1188/AST-1197-consult-apply-email-link-bot-blocked`

After AST-1195 (schema nulls + **BOT_BLOCKED** registry) and AST-1196 (`agent_task` synthesize / subject / empty-string fail rows): wire `qualify_meteorite` **assemble** so Ruth sees email CONTENT, and **process** so per-row outcomes land correctly — synthesized `email-…` links may **METEORITE_QUALIFIED** (http + empty-`company_job_id` gates waived for that prefix); Cloudflare/challenge JD → **BOT_BLOCKED**; no-title/no-subject → **METEORITE_FAILED_QUALIFY**; mixed chunks do not all-ERROR; `debug=True` Style D records link/title source and bot/fail reasons. Does **not** own schema/registry rename (AST-1195) or `agent_task` prompt authoring (AST-1196).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `TASK_CONFIG["qualify_meteorite"]`: `email_link_prefix`, `bot_blocked_state`; append two Cloudflare interstitial phrases to `TRACKER_CONFIG["jd_classifier"]["bot_signals"]` so `_classify_jd` hits `bot_threshold` (2) on the parent-captured challenge body | utils |
| `src/core/consult.py` | `qualify_meteorite` assemble CONTENT label; process: bot → **BOT_BLOCKED**, `email-` waivers, Style D detail (`html.unescape` subject probe) | core |
| `src/ui/api/api_admin.py` | Ad-hoc `qualify_meteorite` assemble lockstep with consult (hand-edit twin; see Stage 2 Decision) | ui |

No `agent_task` / `data/admin` edits, no `JOB_STATES` rename work, no `tests/` / bible (Betty after Code Complete).

## Stage 1: Config — email-link prefix + bot-blocked state + challenge signals

**Done when:** `TASK_CONFIG["qualify_meteorite"]` exposes `email_link_prefix == "email-"` and `bot_blocked_state == "BOT_BLOCKED"`; both new bot_signal strings are in `TRACKER_CONFIG["jd_classifier"]["bot_signals"]`; `python3 -c "from src.utils import config"` succeeds; and the Stage 1 verification snippet below prints `classify=bot` for the parent-captured challenge body (not `missing`). No consult/apply behavior changes yet.

1. In `src/utils/config.py` `TASK_CONFIG["qualify_meteorite"]`, after the existing orchestration keys (`fail_state` / `error_state` / `min_jd_chars` cluster), add:

```python
"email_link_prefix": "email-",  # AST-1197: synthesized link; waive http + empty company_job_id gates
"bot_blocked_state": "BOT_BLOCKED",  # AST-1197: challenge/Cloudflare JD → universal bot state (AST-1195)
```

2. Immediately after the existing module-level asserts on `qualify_meteorite` `job_link` / `job_title` `required is False` (near `config.py:973-975`, still inside the post-`TASK_CONFIG` assert cluster — **before** `JOB_STATES` is defined), add **only**:

```python
assert TASK_CONFIG["qualify_meteorite"]["email_link_prefix"] == "email-"
assert TASK_CONFIG["qualify_meteorite"]["bot_blocked_state"] == "BOT_BLOCKED"
```

Do **not** reference `JOB_STATES` at this anchor — it is defined ~1,200 lines later (`config.py:2173+`); asserting it here raises `NameError` at import and takes down every `src.utils.config` importer.

3. After the `JOB_STATES` literal (immediately after the `"BOT_BLOCKED": {"prior_states": ["PASSED_JOBLIST", "METEORITE_NEW"]}` entry / near other registry asserts around `config.py:2185`), add:

```python
assert "BOT_BLOCKED" in JOB_STATES
assert "METEORITE_NEW" in JOB_STATES["BOT_BLOCKED"]["prior_states"]
```

These facts are already true from AST-1195; the asserts are a placement-correct import gate for this child.

4. In `TRACKER_CONFIG["jd_classifier"]["bot_signals"]`, append **both** of these strings (keep every existing signal unchanged, including `"Cloudflare Ray ID"` / `"Just a moment"`):

```python
"Additional Verification Required",       # AST-1197: parent AC challenge phrase
"Troubleshooting Cloudflare Errors",      # AST-1197: co-occurs on captured interstitial; 2nd hit for bot_threshold
```

`_classify_jd` counts casefold substring hits and returns `"bot"` only when `bot_hits >= bot_threshold` (`bot_threshold` is **2** at `config.py:3432`). A single new phrase is not enough: the parent-captured challenge body (`Additional Verification Required\nYour Ray ID for this request is a26948de4d78f005 … Troubleshooting Cloudflare Errors …`) matches **0** of today’s signals (`"Cloudflare Ray ID"` ≠ `"Your Ray ID for this request is …"`), and with only `"Additional Verification Required"` would score **1** → still `"missing"` (short collapsed length < `min_meaningful_chars`). Both new phrases must be present so that body scores **≥ 2** → `"bot"`.

5. **Verification (run in the epic worktree after the edits; do not commit the snippet):**

```python
from src.core.gazer import _classify_jd
body = (
    "Additional Verification Required\n"
    "Your Ray ID for this request is a26948de4d78f005\n"
    "Troubleshooting Cloudflare Errors"
)
assert _classify_jd(body) == "bot", _classify_jd(body)
print("classify=bot")
```

⚠️ **Decision — widen shared `jd_classifier.bot_signals` (2-hit route), not a meteorite-local decisive list:** Reuse `_classify_jd` / `bot_threshold` as-is. Adding enough phrases from the real interstitial meets AC4 without a new config shape. **Deliberate widening:** `jd_classifier` is shared with gazer/roster `fetch_jd` classification — these phrases also change scrape-time bot detection there. That is intended (universal **BOT_BLOCKED** epic) and is **not** a meteorite-only knob. Rejected alternative: a threshold-1 “decisive signal” list consulted only on the qualify path — more surface for one captured body, and would fork detection from gazer.

⚠️ **Decision — prefix + bot state in TASK_CONFIG:** Apply recognition of `email-` and the destination state id must not be inline magic strings in `consult.py` (`astral.standards.no-hardcoded-sets` / config-source-of-truth).

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

⚠️ **Decision — leave assemble duplication as hand-edit twins (in-scope-only):** Today `consult.py` and `api_admin.py` already mirror the row format byte-for-byte via comment discipline. Extracting a shared builder from `consult` for `api_admin` to call would make lockstep structural and score better on `astral.standards.dry-and-focused-functions`, but it expands the diff into a pre-existing duplication cleanup outside the ticket’s apply/gate surface. **Keep both copies; edit both in this stage; Done-when still requires byte-for-byte equality.** Do not invent a third shared helper module.

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
- Subject probe: if `email-subject` markup is present, take the first `<h1>…</h1>` inner text; else `""`.
- **Unescape before compare:** `subject = html.unescape(raw_subject).strip()` (stdlib `html.unescape`). Inbox create stores the wrapper via `html.escape(subject, quote=True)` (`inbox.py` / `INBOX_CREATE_JOB_CONFIG["subject_html_template"]`), so subjects with `&`, `'`, `"`, `<`, `>` land as entities (`Sales &amp; Marketing Lead`) while Ruth returns the unescaped title — equality without unescape falsely reports `title_source=content`.
- Optionally collapse internal whitespace on both sides before compare (`" ".join(s.split())`) so minor spacing drift does not flip the label.
- `title_source = "subject"` when `job_title` and subject are both non-empty and the normalized strings match casefold; elif `job_title`: `"content"`; else `"neither"`.

Use a tiny local helper inside `qualify_meteorite` (or module-private `_qualify_meteorite_email_subject(html: str) -> str`) with `re` + `html.unescape` — **no** BeautifulSoup import in consult for this (gazer already owns HTML soup on ingest). Prefer `re.search(r'class="email-subject"[^>]*>.*?<h1>(.*?)</h1>', input_jd, re.I|re.S)` or equivalent; on no match return `""`.

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

**Conf:** `high` — siblings shipped schema + prompts; Joan R1 closed the bot_threshold/assert-placement gaps; remaining apply work is gate order + Style D.

**Risk:** `Medium` — wrong bot/email gate order could QUALIFY challenge pages or park real email-JD rows on FAILED/ERROR; shared `bot_signals` widening also affects gazer scrape classification (intentional). Envelope ERROR path left intentional for true `do_task` failures.

## Code-rules check

- §1.3 / `astral.standards.dry-and-focused-functions` — reuse `_classify_jd` and `_resolve_company_job_id`; small subject probe helper only. Assemble twin left duplicated by explicit in-scope-only Decision (Stage 2).
- §1.4 / `astral.standards.no-hardcoded-sets` — `email_link_prefix` + `bot_blocked_state` in TASK_CONFIG; bot signals stay on `jd_classifier` (widened, not forked).
- §1.5.1 / `astral.standards.debug-contract-gated` — Style D only when `debug=True` via existing logger helpers; subject probe uses `html.unescape`.
- §2.1 / `astral.config.config-source-of-truth` — knobs in config; no new parallel registries / decisive-signal list.
- §2.4 / `astral.batch.claim-process-release` — still claim → `_run_batch_consult` → per-row process → release; no claim API changes.
- §2.6 / `astral.state.core-decides-transitions` + `astral.state.job-prior-states-enforced` — core chooses **BOT_BLOCKED** / fail / pass; priors already allow `METEORITE_NEW` → **BOT_BLOCKED** (AST-1195).
- §3.3 imports — lazy `from src.core.gazer import _classify_jd` inside process (existing consult↔gazer pattern).
- Out of scope: `astral.agent.do-task-delegation` prompt text (AST-1196); schema required flags (AST-1195).

## Revisions

Revision 1 — 2026-08-06
Driven by: Joan `[plan-discuss] round=1 concern` (plan-rubric REVISE) — fix-now bot_threshold unmet on captured Cloudflare body; fix-now `JOB_STATES` asserts before definition; discuss `html.unescape` subject probe; discuss assemble DRY vs in-scope-only.
Changes: Stage 1 appends both `"Additional Verification Required"` and `"Troubleshooting Cloudflare Errors"`, documents 2-hit threshold + shared-classifier widening Decision, adds captured-body `classify=bot` verification; splits TASK_CONFIG vs `JOB_STATES` assert placement; Stage 3 subject probe uses `html.unescape` (+ optional whitespace collapse); Stage 2 records Decision to keep hand-edit assemble twins.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1188/AST-1197-consult-apply-email-link-bot-blocked`
**Plan path:** `docs/features/meteorite/ast-1197-consult-apply-email-link-bot-blocked.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `ee71b044` | `email_link_prefix` / `bot_blocked_state` + two Cloudflare `bot_signals` + asserts |
| 2 | `c77f1fed` | assemble `CONTENT:` label + api_admin lockstep |
| 3 | `cca4fb1c` | process: bot → **BOT_BLOCKED**, `email-` QUALIFY waivers, Style D title/link source |

**Tip:** `cca4fb1c` on `origin/sub/AST-1188/AST-1197-consult-apply-email-link-bot-blocked`

## Review (code-rubric.v1)

[code-rubric.v1] revision=1

**Rubric:** code-rubric.v1
**Ticket:** AST-1197
**Overall:** CLEAN
**Diff:** `origin/dev...origin/sub/AST-1188/AST-1197-consult-apply-email-link-bot-blocked`, own footprint isolated at `e3e14af1..c081ae0e` (post-plan tip through Betty's `merge-tests` tip) — the wider three-dot diff also carries already-reviewed sibling work (AST-1189/1190/1191/1192/1193, each `resolve(...): — clean`) merged onto `origin/ftr` ahead of this child; none of that is AST-1197's own change.

**Files (own footprint):** `src/core/consult.py`, `src/ui/api/api_admin.py`, `src/utils/config.py` (code); `docs/test-bible/core/consult.md`, `docs/test-bible/core/gazer.md`, `docs/test-bible/ui/api/api_admin.md`, `docs/test-bible/utils/config.md`, `tests/component/core/test_consult.py`, `tests/component/core/test_gazer.py`, `tests/component/ui/api/test_api_admin.py`, `tests/component/utils/test_config.py` (tests/bible); `docs/features/meteorite/ast-1197-consult-apply-email-link-bot-blocked.md` (plan).

## Frame diff

Layers = {core, ui, utils, docs}. Paths = the footprint above. Change types = {modify} only. Full active-set swept: 65 leaves — 18 universal + 47 scoped considered, 4 scoped not-applicable (`astral.debug.no-repo-root-artifacts-dir`, `astral.layers.scripts-exempt-from-layer-rules`, `astral.standards.database-header-inventory`, `astral.ui.frontend-file-placement` — no `artifacts/`, `scripts/`, `src/data/**`, or `src/ui/frontend/**` in this footprint). All 61 applicable statutes score `conforms`. No `fix-now`, no `discuss`.

**Plan adherence:** Implementation matches the Revision-1 plan stage-for-stage — `email_link_prefix`/`bot_blocked_state` knobs + two Cloudflare `bot_signals` phrases (Stage 1), `CONTENT:` assemble relabel in lockstep across `consult.py`/`api_admin.py` (Stage 2), bot-gate-before-content-fail + `email-` waivers + Style D title/link source (Stage 3).

**Verified independently (not just taken on the plan's word):**
- `_classify_jd` on the shipped `bot_signals` list scores the parent-captured challenge body at 2 hits (`Additional Verification Required`, `Troubleshooting Cloudflare Errors`) → `"bot"`, confirming Joan's round=1 fix-now is actually closed in code, not just in plan prose.
- `assert "BOT_BLOCKED" in JOB_STATES` / `assert "METEORITE_NEW" in JOB_STATES["BOT_BLOCKED"]["prior_states"]` land at `config.py:2284-2285`, after the `JOB_STATES` literal opens at `config.py:2173`; the `TASK_CONFIG` pair stays at `config.py:980-981`. Confirmed by byte offset, not just line-number eyeballing — no `NameError` risk.
- The shipped helper is `_qualify_meteorite_email_subject(html_body: str)`, not the plan-prose's `(html: str)` — the engineer sidestepped Joan's stdlib-`html`-shadowing `discuss` finding by parameter naming rather than `import html as html_module`; either fix is valid and this one is in the code.
- `api_admin.py`'s ad-hoc assemble line is byte-for-byte identical in shape to `consult.py`'s (`{idx:03d}: job_link: {...}\nCONTENT:\n{...}`), satisfying the recorded hand-edit-twins Decision's Done-when.
- Role/path separation across the three `code(AST-1197)` commits (src/ only), the `docs(AST-1197)` build-stub commit (plan file only), and the `test(AST-1197)` + `merge-tests(AST-1197)` commits (tests/ + docs/test-bible/ only) — no cross-contamination.

No blockers. `code-rubric.v1` verdict: **CLEAN**.

— Radia

## Resolution

**Date:** 2026-08-06  
**Review tip:** `3c651ebb` (`docs(AST-1197): Radia review — clean`) — **Overall: CLEAN**

No fix-now or discuss items. No product or test-tree changes on resolve.

