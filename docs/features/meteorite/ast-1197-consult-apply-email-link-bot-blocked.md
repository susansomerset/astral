<!-- linear-archive: AST-1197 archived 2026-08-14 -->

## Linear archive (AST-1197)

**Archived:** 2026-08-14  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1197/consult-apply-email-link-qualify-bot-blocked-failed-qualify-park-style  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1188 — Errors for qualify_meteorite dispatch task  
**Blocked by / blocks / related:** parent: AST-1188

### Description

## What this implements

After schema/BOT_BLOCKED registry and agent_task instructions: assemble includes email body for Ruth; accept synthesized `email-…` links for QUALIFY; challenge/Cloudflare JD → **BOT_BLOCKED**; no-subject/no-title → **METEORITE_FAILED_QUALIFY**; mixed-batch per-row outcomes; Style D debug. Does not own universal state rename or agent_task authoring (siblings).

## In scope

- [X] `astral.batch.claim-process-release` — still claim → `_run_batch_consult` → per-row process → release; no claim API changes
- [X] `astral.state.core-decides-transitions` — consult process chooses **BOT_BLOCKED** / **METEORITE_FAILED_QUALIFY** / **METEORITE_QUALIFIED**
- [X] `astral.state.job-prior-states-enforced` — transitions use registry ids already allowing `METEORITE_NEW` → **BOT_BLOCKED** (AST-1195)
- [X] `astral.standards.debug-contract-gated` — Style D per-job headers + detail only when `debug=True`
- [X] `astral.standards.no-hardcoded-sets` — `email_link_prefix` + `bot_blocked_state` in `TASK_CONFIG`; bot signals on `jd_classifier`
- [X] `astral.config.config-source-of-truth` — apply knobs live in `config.py`; no parallel registries
- [X] `astral.standards.dry-and-focused-functions` — reuse `_classify_jd` / `_resolve_company_job_id`; small subject probe only
- [X] `astral.standards.in-scope-only` — assemble/process + admin lockstep + config knobs only

## Considered but excluded

- [X] `astral.agent.do-task-delegation` / `agent_task` prompt authoring — AST-1196 (catalog row already shipped)
- [X] Schema `job_link`/`job_title` nullability + `JD_SCRAPE_FAIL_BOT` → **BOT_BLOCKED** registry/UI rename — AST-1195
- [X] `astral.agent.grade-vector-validation` / `astral.agent.confidence-bounds` — not a graded task
- [X] `astral.patterns.render-verdict-orchestrates-consult` / coat-check — untouched
- [X] `astral.layers.core-vs-external-bright-line` — no new external I/O; lazy gazer classify reuse only
- [X] `astral.ui.*` / frontend TS — admin assemble string lockstep only (no React)
- [X] `tests/` / bible — Betty after Code Complete
- [X] `orch.*` — universal orchestration statutes stay off per-child lists
- [X] Live Gmail re-fetch / new `job_data` email key — parent forbids separate pre-Ruth plumbing; CONTENT = stored `job_description`

## Acceptance criteria

1. [x] Mixed chunk with some null `job_link`/`job_title` and some full http extracts: good rows **QUALIFY**; others follow synthesize/subject/fail/bot rules; chunk does **not** all-ERROR. (apply portion.)
2. [x] No ATS link + usable JD in email content: Ruth returns `email-<originalsender>-<timestamp>`; row can **METEORITE_QUALIFIED** (http gate waived for that prefix). (apply portion.)
3. [x] No title and no subject → **METEORITE_FAILED_QUALIFY** (not QUALIFIED, not whole-batch ERROR).
4. [x] Cloudflare / challenge JD body → **BOT_BLOCKED** (not **METEORITE_QUALIFIED**). (apply portion.)
5. [x] Genuine unparseable envelope → **METEORITE_ERROR_QUALIFY**.
6. [x] `debug=True` shows per-job Style D headers + detail for link/title source and bot-block/fail reasons.

## Boundaries

- [X] Does not own schema/BOT_BLOCKED registry rename or agent_task authoring. After AST-1195 and AST-1196.

## Notes for planning

Assemble must include email body content so Ruth can discern sender/subject/JD.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1188-errors-for-qualify-meteorite-dispatch-task`, child `sub/AST-1188/AST-1197-consult-apply-email-link-bot-blocked`. Created at dispatch-parent.

### Comments

#### chuckles — 2026-08-06T00:47:41.097Z
[merge-child] blocked: git pull merge on sub — use: git fetch && git merge origin/ftr/<parent-segment>

Offenders in `origin/ftr..origin/sub/AST-1188/AST-1197-consult-apply-email-link-bot-blocked`:
- `e3e14af1` Merge remote-tracking branch 'origin/dev' into sub/…
- `4deeca76` Merge remote-tracking branch 'origin/ftr/AST-1188-…' into sub/…

@Hedy Lamarr — rewrite those off the publish tip (prefer `merge-resume(AST-1197): stack sub onto ftr/…` / sync-child style; no `Merge remote-tracking branch` subjects). Stay User Testing. Republish `origin/sub/AST-1188/AST-1197-consult-apply-email-link-bot-blocked`.

— Chuckles

#### radia — 2026-08-06T00:44:27.532Z
[code-rubric] revision=1

**Rubric:** code-rubric.v1
**Ticket:** AST-1197
**Overall:** CLEAN
**Diff:** `origin/dev...origin/sub/AST-1188/AST-1197-consult-apply-email-link-bot-blocked`, own footprint isolated at `e3e14af1..c081ae0e` (post-plan tip through Betty's `merge-tests` tip) — the wider three-dot diff also carries already-reviewed sibling work (AST-1189/1190/1191/1192/1193, each `resolve(...): — clean`) merged onto `origin/ftr` ahead of this child; none of that is AST-1197's own change.

**Files (own footprint):** `src/core/consult.py`, `src/ui/api/api_admin.py`, `src/utils/config.py` (code); `docs/test-bible/core/consult.md`, `docs/test-bible/core/gazer.md`, `docs/test-bible/ui/api/api_admin.md`, `docs/test-bible/utils/config.md`, `tests/component/core/test_consult.py`, `tests/component/core/test_gazer.py`, `tests/component/ui/api/test_api_admin.py`, `tests/component/utils/test_config.py` (tests/bible); plan doc (build stub).

## Frame diff

Layers = {core, ui, utils, docs}. Paths = the footprint above. Change types = {modify} only. Full active-set swept: 65 leaves — 18 universal + 47 scoped considered, 4 scoped not-applicable (`astral.debug.no-repo-root-artifacts-dir`, `astral.layers.scripts-exempt-from-layer-rules`, `astral.standards.database-header-inventory`, `astral.ui.frontend-file-placement` — no `artifacts/`, `scripts/`, `src/data/**`, or `src/ui/frontend/**` in this footprint). All 61 applicable statutes score `conforms`. No `fix-now`, no `discuss`.

**Plan adherence:** Implementation matches the Revision-1 plan stage-for-stage — `email_link_prefix`/`bot_blocked_state` knobs + two Cloudflare `bot_signals` phrases (Stage 1), `CONTENT:` assemble relabel in lockstep across `consult.py`/`api_admin.py` (Stage 2), bot-gate-before-content-fail + `email-` waivers + Style D title/link source (Stage 3).

**Verified independently (not taken on the plan's word):**
- `_classify_jd` on the shipped `bot_signals` list scores the parent-captured challenge body at 2 hits (`Additional Verification Required`, `Troubleshooting Cloudflare Errors`) → `"bot"` — confirms Joan's round=1 fix-now is closed in code, not just plan prose.
- `assert "BOT_BLOCKED" in JOB_STATES` / prior-state assert land at `config.py:2284-2285`, after `JOB_STATES` opens at `config.py:2173`; the `TASK_CONFIG` pair stays at `config.py:980-981` — verified by byte offset. No `NameError` risk.
- Shipped helper is `_qualify_meteorite_email_subject(html_body: str)`, not the plan-prose's `(html: str)` — sidesteps Joan's stdlib-`html`-shadowing `discuss` by parameter naming.
- `api_admin.py`'s ad-hoc assemble line is byte-for-byte identical in shape to `consult.py`'s — satisfies the recorded hand-edit-twins Decision's Done-when.
- Role/path separation clean across `code(AST-1197)` (src/ only), `docs(AST-1197)` (plan file only), `test(AST-1197)`/`merge-tests(AST-1197)` (tests/ + docs/test-bible/ only).

No blockers. **CLEAN.**

— Radia

#### betty — 2026-08-06T00:38:21.598Z
Tests Ready — run on `origin/sub/AST-1188/AST-1197-consult-apply-email-link-bot-blocked` @ `c081ae0e` (`merge-tests(AST-1197): origin/tests c42f73be04d482aa16cdd99c8304960b4275da6e`).

**Manifest**
1. `tests/component/core/test_consult.py::TestAst1197QualifyMeteoriteApply` — CONTENT assemble; `email-` QUALIFY waiver; challenge → **BOT_BLOCKED**; short title → **METEORITE_FAILED_QUALIFY**; Style D `link_source`/`title_source` + unescape
2. `tests/component/core/test_consult.py::TestAst1133QualifyMeteoriteListCreated::test_debug_detail_includes_link_source_input` — revised (`link_source=http-input`)
3. `tests/component/core/test_consult.py::TestAst1062QualifyMeteorite` — existing content gates still green
4. `tests/component/utils/test_config.py::TestAst1197QualifyMeteoriteApplyKnobs` — `email_link_prefix` / `bot_blocked_state` / challenge `bot_signals`
5. `tests/component/core/test_gazer.py::TestAst1197ChallengeBotSignals` — captured interstitial → `bot`
6. `tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_build_adhoc_live_content_qualify_meteorite` — `CONTENT:` lockstep

**Narrowed pytest**
```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_consult.py::TestAst1197QualifyMeteoriteApply \
  tests/component/core/test_consult.py::TestAst1133QualifyMeteoriteListCreated::test_debug_detail_includes_link_source_input \
  tests/component/core/test_consult.py::TestAst1062QualifyMeteorite \
  tests/component/utils/test_config.py::TestAst1197QualifyMeteoriteApplyKnobs \
  tests/component/core/test_gazer.py::TestAst1197ChallengeBotSignals \
  tests/component/ui/api/test_api_admin.py::TestAdhocHelpers::test_build_adhoc_live_content_qualify_meteorite \
  -q
```

**Bible shasums** (`origin/sub/…`)
- `docs/test-bible/core/consult.md` `41758007974a0dab093d88d478d2dc8bdbda4af2`
- `docs/test-bible/utils/config.md` `6189d1367f671aa28b6913e6843f6c006c0898e3`
- `docs/test-bible/core/gazer.md` `d07604d3e4690e33ae6d01c4541dcc79933a3863`
- `docs/test-bible/ui/api/api_admin.md` `ad194b32fadd7cecf5a736fced465cf1ac56b627`

**Broken / revised:** AST-1133 `link_source=input` → `http-input`.

**Integration:** none revised.

— Betty

#### joan — 2026-08-06T00:30:22.752Z
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1197
**Overall:** APPROVED
**Publish ref tip:** `origin/sub/AST-1188/AST-1197-consult-apply-email-link-bot-blocked` @ `37fad7c8`

## Traceability

AC1→S3.5–7; AC2→S1+S3.1/5/6; AC3→S3.5; AC4→S1.4–5+S3.4; AC5→S3.7 (envelope path unchanged); AC6→S3.3/4/5/6. S2 maps to parent Functional scope “Assemble sends email message body content to Ruth”. Parent AC3 / AC6 stay N/A–boundary for this child (AST-1196 / AST-1195). No unmapped child AC, no orphan stages.

**Considered:** Files Changed still resolves to the same three files and layers (`src/utils/config.py` utils, `src/core/consult.py` core, `src/ui/api/api_admin.py` ui; `modify`), so the matching algorithm yields the identical sets as round=1 — 65 leaves: 18 universal + 40 scoped considered, 7 scoped excluded on layer/path predicates. All considered statutes score `conforms`; `astral.standards.dry-and-focused-functions` moves from `needs-discussion` to `conforms` now that the assemble twin is a recorded Decision rather than an unexamined duplication. Scored in-session per R7.

## Round=1 fix-nows — verified closed

**fix-now 1 (bot threshold) — closed, and I re-ran the numbers rather than taking the reply's word for it.** I rebuilt `_classify_jd`'s full decision chain (closed → bot → cookie → missing) from the signal lists and thresholds at this tip, added the plan's two new phrases, and ran the exact challenge body captured in the parent's failing run:

| input | verdict | bot hits |
|--|--|--|
| full captured `jd_text` | **`bot`** | 2 (`Additional Verification Required`, `Troubleshooting Cloudflare Errors`) |
| the plan's own Stage 1 snippet | **`bot`** | 2 |

No `closed_signal` preempts the bot branch (16 closed signals, none present), so the ordering works in the plan's favour rather than by luck, and both phrases are genuinely absent from today's 16-entry list — they are additions, not no-ops. Stage 1's Done-when now requires that `classify=bot` check to pass before the stage closes, which is the part that makes this durable. The shared-corpus widening is recorded as a deliberate Decision naming the gazer/roster side effect, and Risk now mentions it too.

**fix-now 2 (assert placement) — closed.** The two `TASK_CONFIG` asserts stay at the post-`TASK_CONFIG` cluster (`config.py:975-977` at this tip, drifted two lines by the `origin/dev` merge, which the plan's “near” phrasing absorbs), and the two `JOB_STATES` asserts move after the registry literal with an explicit “do not reference `JOB_STATES` at this anchor” warning carrying the reason. There is a natural home there: the literal closes at `config.py:2276` and is immediately followed by existing registry asserts including `assert METEORITE_CONFIG["job_create_state"] in JOB_STATES` (`config.py:2279`), so the plan's “near other registry asserts” pointer is accurate.

**discuss 3 (subject probe) — taken.** `html.unescape` before the casefold compare, plus optional whitespace collapse, with the reason recorded inline. **discuss 4 (assemble DRY) — answered as asked:** kept as hand-edit twins under `astral.standards.in-scope-only`, with the rejected alternative written down.

## Findings

**1. `discuss` — the suggested helper signature shadows the module the step tells you to call.**

Stage 3 step 3 offers `_qualify_meteorite_email_subject(html: str) -> str` and, in the same step, instructs `html.unescape(raw_subject)`. Inside a function whose parameter is named `html`, that call resolves against the `str` argument and raises `AttributeError: 'str' object has no attribute 'unescape'`. `consult.py` also does not import `html` today (it imports `json` and `re` only), so the stage needs the stdlib import added regardless. `src/core/inbox.py:13` already handles exactly this collision with `import html as html_module` — following that precedent, or simply renaming the parameter to `raw` / `input_jd`, resolves both halves. Flagging rather than blocking because the failure is immediate and loud on the first debug run, not a silent wrong result.

**2. `discuss` — one locator in Stage 1 step 3 contradicts its own leading clause.** The step says “After the `JOB_STATES` literal” (correct) but parenthesizes “immediately after the `"BOT_BLOCKED": {…}` entry”, which is *inside* the dict literal at `config.py:2187` — an assert placed there is a `SyntaxError`. The leading clause and the “near other registry asserts” pointer both aim at the right spot, so this is a wording tightening: drop the parenthetical or replace it with “after the literal's closing brace, beside the existing `METEORITE_CONFIG` registry asserts”.

**3. `acceptable`** — The assemble duplication across `consult.py` and `api_admin.py` survives as a recorded in-scope-only Decision with Done-when byte-for-byte equality. That was the ask; noting it so Radia reads it as a decision.

**4. `acceptable`** — Per-row `debug_index(index=1, total=1)` keeps today's shape rather than universal `index N/M`; the input-inventory loop does emit proper `N/M`. Pre-existing.

**5. `acceptable`** — Lazy `from src.core.gazer import _classify_jd` imports a module-private helper, consistent with established practice (`gaze_email.py:22`, `consult.py:232/569/2186`, `roster.py`). Carried from round=1.

**6. `acceptable`** — Stage 1 step 5's verification snippet is explicitly marked “do not commit”, so it leaves no repo artifact and stays clear of the `debug/` placement statutes.

## Closing verification

Re-confirmed at this tip (the branch merged `origin/dev`, so I re-read rather than trusting round=1):

- **AC2 identity path intact:** `_identity_triple_complete` needs both `company_job_id` and title non-empty, and `idx_job_identity_unique` is a partial index excluding NULL/empty triples, so an `email-` row with empty `company_job_id` still saves cleanly under the waiver.
- **BOT_BLOCKED priors still include `METEORITE_NEW`** (`config.py:2187`), so the new transition cannot `ValueError`.
- **Assemble contract unchanged:** 0-based `enumerate`, matching AST-1196's shipped `000:`/`001:` CONTENT row contract and the positional-echo requirement that `_bind_response_jobs_to_claimed` relies on.
- **Layers clean:** utils/core/ui with no upward imports; the admin assemble string stays in the API layer per §3.2.
- **Self-assessment honest:** `Single-Component` / `high` / `Medium`, with Risk now naming the shared-classifier widening as an intended consequence.

No `fix-now` outstanding. Plan Discuss closes after one completed round with both fix-nows evidenced closed. → **Plan Approved.**

context_tokens≈128000

— Joan

#### hedy — 2026-08-06T00:27:26.659Z
[plan-discuss] round=1 reply

Plan tip: `37fad7c8` — https://github.com/susansomerset/astral/blob/sub/AST-1188/AST-1197-consult-apply-email-link-bot-blocked/docs/features/meteorite/ast-1197-consult-apply-email-link-bot-blocked.md

**fix-now 1 (bot_threshold):** Took the 2-hit shared-classifier route. Stage 1 now appends both `"Additional Verification Required"` and `"Troubleshooting Cloudflare Errors"` (the co-occurring phrases on the parent-captured interstitial). Documented that a single phrase leaves `_classify_jd` at 1 hit → `missing` → FAILED_QUALIFY. Added Done-when verification snippet that must print `classify=bot` on that body. Explicit Decision: deliberate widening of shared `jd_classifier` (also affects gazer scrape), not a meteorite-local decisive list.

**fix-now 2 (JOB_STATES asserts):** Split placement — TASK_CONFIG asserts stay at the 973-975 cluster; `JOB_STATES` / `METEORITE_NEW` prior asserts move after the `JOB_STATES` literal (~2185).

**discuss 3 (subject probe):** Stage 3 subject probe now `html.unescape`s the `<h1>` capture (and optional whitespace collapse) before casefold compare against Ruth’s title.

**discuss 4 (assemble DRY):** Recorded Decision to keep hand-edit twins in consult + api_admin (in-scope-only); Done-when still requires byte-for-byte equality.

Status left **Plan Discuss** for re-validate.

#### joan — 2026-08-06T00:25:42.225Z
[plan-discuss] round=1 concern
[plan-rubric] revision=1

**Rubric:** plan-rubric.v1
**Ticket:** AST-1197
**Overall:** REVISE
**Publish ref tip:** `origin/sub/AST-1188/AST-1197-consult-apply-email-link-bot-blocked` @ `6fe5730b`

## Traceability

AC1→S3.5–7; AC2→S1+S3.1/5/6; AC3→S3.5; AC4→S1+S3.4 — **AC4 unmet, see finding 1**; AC5→S3.7 (envelope path unchanged); AC6→S3.3/4/5/6 — partially degraded, see finding 3. S2 (assemble CONTENT + admin lockstep) maps to parent Functional scope “Assemble sends email message body content to Ruth” and the ticket’s Notes for planning. Parent AC3 (subject-as-title) and AC6 (`JD_SCRAPE_FAIL_BOT` gone) are N/A–boundary for this child (Katherine AST-1196 / Ada AST-1195). No orphan stages.

**Considered:** full active corpus swept via the rubric matching algorithm against the three planned files (`src/utils/config.py` utils, `src/core/consult.py` core, `src/ui/api/api_admin.py` ui; change_types `modify`) — 65 leaves: 18 universal + 40 scoped considered, 7 scoped excluded on layer/path predicates (`data` / `docs` / `scripts` layers, `tests/**`, `debug/**`, `src/ui/frontend/**`). Every considered statute scores `conforms` except `astral.standards.dry-and-focused-functions` (`needs-discussion`, finding 4). Both fix-nows are R5/R6 fidelity rather than statute violations. Recorded in-session per R7.

## Findings

**1. `fix-now` — The bot gate cannot fire on the challenge page this epic was written for: `_classify_jd` needs two signal hits, and Stage 1 adds one.**

Stage 3 step 4 routes only `_classify_jd(...) == "bot"` to **BOT_BLOCKED**, and Stage 1 step 3 adds the single phrase `"Additional Verification Required"` to `TRACKER_CONFIG["jd_classifier"]["bot_signals"]`. But `_classify_jd` is threshold-based, not phrase-based (`src/core/gazer.py:129-131`):

```python
bot_hits = sum(1 for s in cfg.get("bot_signals", []) if s.lower() in text_lower)
if bot_hits >= cfg.get("bot_threshold", 2):
    return "bot"
```

`bot_threshold` is **2** (`config.py:3432`). I ran the classifier's own logic over the exact challenge body captured in the parent's failing run (AST-1188 Description, the `"jd_text": "Additional Verification Required\nYour Ray ID for this request is a26948de4d78f005 … Troubleshooting Cloudflare Errors …"` row):

| | result |
|--|--|
| bot signal hits today | **0** |
| bot signal hits after Stage 1 | **1** (`Additional Verification Required`) |
| `bot_threshold` | 2 → **not** `bot` |
| collapsed length | 156 chars, vs `min_meaningful_chars` 500 |
| `_classify_jd` verdict after Stage 1 | **`missing`** |

So that page classifies `missing`, and Stage 3 step 4 explicitly says cookie/closed/**missing** stay on the fail path — it lands on **METEORITE_FAILED_QUALIFY**, not **BOT_BLOCKED**. Ticket AC4 and parent AC5 are unmet on the precise payload that motivated them.

Worth noting the plan's premise is also off in a smaller way: Stage 1's Decision says to “keep existing Cloudflare / ‘Just a moment’ / Ray ID signals unchanged” as though they already cover this page. The literal signal is `"Cloudflare Ray ID"`, and this body says `"Your Ray ID for this request is …"` and `"Troubleshooting Cloudflare Errors"` as separate strings — hence 0 hits today.

**Recommendation:** make the plan state explicitly how a single-phrase challenge reaches `bot`, and verify it against that captured body rather than by inspection. Two shapes both work — your call which fits the corpus better: add a config'd decisive-signal list (threshold 1) consulted on this path, or add enough of the phrases actually present in real Cloudflare interstitials (e.g. `"Troubleshooting Cloudflare Errors"` alongside `"Additional Verification Required"`) that the existing 2-hit threshold is genuinely met. If you take the second route, please note in the plan that `jd_classifier` is shared with gazer/roster scraping, so the added phrases change classification there too — that is a deliberate widening, not a meteorite-local knob.

**2. `fix-now` — Stage 1 step 2 puts `JOB_STATES` asserts ~1,200 lines before `JOB_STATES` exists; `config.py` would fail to import.**

Step 2 says to add all four asserts “immediately after the existing module-level asserts on `qualify_meteorite` `job_link` / `job_title` `required is False`.” Those asserts live at `config.py:973-975`, right after the `TASK_CONFIG` literal (which opens at line 179). `JOB_STATES` is not defined until `config.py:2173`. So these two lines:

```python
assert "BOT_BLOCKED" in JOB_STATES
assert "METEORITE_NEW" in JOB_STATES["BOT_BLOCKED"]["prior_states"]
```

raise `NameError: name 'JOB_STATES' is not defined` at import time, which takes down every importer of `src.utils.config` — the whole app, not just this task. Stage 1's own Done-when (`python3 -c "from src.utils import config"` succeeds) would fail, so you would catch it in the stage, but `orch.pipeline.plan-is-bible` means the text gets executed as written, and this is a one-line fix in the plan rather than a debugging detour.

**Recommendation:** keep the two `TASK_CONFIG` asserts at the 973-975 anchor and place the two `JOB_STATES` asserts after the `JOB_STATES` literal (after `config.py:2185`, near the existing registry assertions). Both facts they assert are true today — `"BOT_BLOCKED": {"prior_states": ["PASSED_JOBLIST", "METEORITE_NEW"]}` is at `config.py:2185` from AST-1195 — so this is purely placement.

**3. `discuss` — The subject probe compares Ruth's title against HTML-**escaped** subject text, so `title_source` will report `content` for many genuine subject titles.**

Stage 3 step 3 sets `title_source = "subject"` only when `job_title.casefold() == subject.casefold()`, where `subject` is scraped out of the stored `<header class="email-subject"><h1>…</h1></header>`. That wrapper is written by `src/core/inbox.py:139` from `INBOX_CREATE_JOB_CONFIG["subject_html_template"]`, and the subject is inserted as `html.escape(subject, quote=True)` (`inbox.py:138`). Ruth reads the rendered text and returns the unescaped title, so any subject containing `&`, `'`, `"`, `<` or `>` — `"Sales & Marketing Lead"` is the common case — stores as `Sales &amp; Marketing Lead` and fails the equality. The row still lands on the right state; only the AC6 debug attribution is wrong, and wrong in the direction that hides subject-sourced titles.

**Recommendation:** `html.unescape(...)` the probe result before the casefold compare (and consider comparing on collapsed whitespace). Your regex itself is fine — I checked it against the real template and `class="email-subject"[^>]*>.*?<h1>(.*?)</h1>` matches `<header class="email-subject"><h1>…</h1></header>`.

**4. `discuss` — the assemble row format is duplicated in `consult.py` and `api_admin.py`, and Stage 2 edits both copies by hand.**

`astral.standards.dry-and-focused-functions` scores `needs-discussion` here: today's two builders already have to match byte-for-byte (`consult.py:1720-1727` vs `api_admin.py:1227-1230`, held together by a comment), and Stage 2's Done-when asks for byte-for-byte equality again after both change. Since `ui` may import `core`, exposing the row builder from `consult` and calling it from `api_admin` would make the lockstep structural instead of aspirational. I am not asking you to take it — `astral.standards.in-scope-only` is a fair reason to leave a pre-existing duplication alone — but please record the choice in the plan so it is a decision rather than an oversight.

**5. `acceptable`** — Per-row `debug_index(index=1, total=1)` keeps today's shape rather than the universal `index N/M` of §1.5.1; the input-inventory loop at the top of `qualify_meteorite` does emit proper `N/M`. Pre-existing, and in-scope-only argues for leaving it.

**6. `acceptable`** — The lazy `from src.core.gazer import _classify_jd` imports a module-private helper across modules. That is established practice in this codebase (`gaze_email.py:22` imports `_meteorite_fetch_link_visible_text` from gazer; `consult.py` imports agent privates at 232/569/2186; `roster.py` imports consult privates), so it is consistent rather than novel — noting it so Radia does not re-litigate it.

## Verification notes (checks that came back clean)

Recording these so the revision and the later code review do not repeat them:

- **The `CONTENT:` relabel really is in lockstep with the shipped prompt.** AST-1196's `qualify_meteorite` `cache_prompt` on the epic ftr ref says “`CONTENT` rows are numbered `000:`, `001:`” and “CONTENT may include subject/headers/body so you can read sender, subject, and JD.” Today's assemble emits `job_description:`, so Stage 2 closes a real prompt/content mismatch rather than churning a label.
- **Row numbering stays 0-based.** Today's assemble uses `enumerate(jobs)` and the plan keeps it, matching the prompt's `000:` contract and `api_admin`'s `len(lines):03d`. Nothing shifts the position map.
- **Step 8's positional-bind premise is correct.** `_bind_response_jobs_to_claimed` (`consult.py:419-429`) has an ordered branch that rewrites empty or `\d{1,3}` id echoes by position when counts match, and the shipped prompt mandates that echo precisely so apply can bind rows whose `job_link` is `""` or an `email-` token. Leaving `_bind_response_jobs_by_job_link` alone is right.
- **The new `.startswith` calls cannot hit `None`.** `ruth_link`, `input_link`, `job_title` and `jd_text` are all built as `(response_job.get(...) or "").strip()` today (`consult.py:1733-1737`), so AST-1195's nullable fields arrive as `""`.
- **AC2's identity premise holds.** `initialize_job` only runs the collision lookup when `_identity_triple_complete(cid, title)` — both non-empty (`tracker.py:44-49`) — and `idx_job_identity_unique` is a **partial** index that excludes NULL/empty `company_job_id` or `job_title` (`database.py:1461`, AST-732). So an `email-` row with empty `company_job_id` saves cleanly; there is no hidden `IntegrityError`/silent-delete path waiting for the waiver.
- **The BOT_BLOCKED transition will not `ValueError`.** Priors already include `METEORITE_NEW` (`config.py:2185`).
- **AC1's schema dependency is satisfied by siblings.** `jd_text` stays `required: True` by design; the shipped prompt explicitly instructs empty strings for unusable rows and warns that null/omit aborts the chunk, which is what keeps a mixed chunk from all-ERRORing.
- **Layers are clean.** utils/core/ui touched with no upward imports; the admin assemble string is built in the API layer, which is where §3.2 / `astral.layers.ui-config-driven-business-logic` puts resolved logic — no React involvement.

The diagnosis is right where it matters: the gate order really does fail empty `company_job_id` before the http check (`consult.py:1761-1770`), so a synthesized `email-…` link can never reach QUALIFY today, and there is no bot branch at all in `qualify_meteorite.process`. Scoping to config knobs + assemble/process + the admin mirror is the correct surface, and `Risk: Medium` names the right hazard. Fix findings 1 and 2 and this is close.

context_tokens≈108000

— Joan

#### hedy — 2026-08-06T00:17:32.382Z
Plan: https://github.com/susansomerset/astral/blob/sub/AST-1188/AST-1197-consult-apply-email-link-bot-blocked/docs/features/meteorite/ast-1197-consult-apply-email-link-bot-blocked.md (`6fe5730b`)

**Scope:** Single-Component — `qualify_meteorite` assemble/process in `consult.py`, admin assemble lockstep, TASK_CONFIG / jd_classifier knobs.

**Conf:** high — AST-1195/1196 shipped schema + prompts; apply gaps are known gate order (empty `company_job_id` before http) and missing bot branch; `_classify_jd` + empty-cid `initialize_job` already exist.

**Risk:** Medium — wrong bot/email gate order could QUALIFY challenge pages or park real email-JD rows on FAILED/ERROR; envelope ERROR path left intentional for true `do_task` failures.

---

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

