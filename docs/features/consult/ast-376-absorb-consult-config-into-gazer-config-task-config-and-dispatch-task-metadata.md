# AST-376 — Absorb `CONSULT_CONFIG` into `GAZER_CONFIG`, `TASK_CONFIG`, and `dispatch_task` metadata

<!-- linear-archive: AST-376 archived 2026-06-03 -->

## Linear archive (AST-376)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-376/absorb-consult-config-into-gazer-config-task-config-and-dispatch-task  
**Status at archive:** Done  
**Project:** Astral Consult  
**Assignee:** unassigned  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## **Problem**

`CONSULT_CONFIG` overlaps responsibilities with `TASK_CONFIG` (agent task definition) and `dispatch_task` (when/for which `trigger_state` a step runs). That split is easy to misread (e.g. `consult_do` → `grade_do`) and encourages duplicate knobs (`fallback_batch_size` vs `batch_size`, threshold vs `score_floor`).

## **Direction**

1. `TASK_CONFIG`
   Own **orchestration that is invariant across input states** for a given agent task: pass/fail/error job states, `save_prefix`, `rubric_artifact`, `requires_company`, scrape `error_states`, qualify `min_job_title_length`, etc. — aligned with the idea that `NO_OPENINGS` vs `TO_WATCH` and **retry lanes** only change **claim state**, not **verdict rules**.
2. `dispatch_task`
   Own **schedule + claim**: `trigger_state`, `freq_hrs`, `batch_size`, `score_floor`, `candidate_id`, flags. Single precedence story vs `TASK_CONFIG` defaults.
3. `GAZER_CONFIG` (new)
   Own **gazer-only** steps today leaning on `CONSULT_CONFIG`: `validate_title`, `scrape_jd`, and any gaze batch defaults — clean separation from job **consult** scoring.
4. **Remove** `CONSULT_CONFIG` after call sites (`consult.py`, `gazer.py`, dispatcher scoring helpers, admin) read from the above.

## **Scope / notes**

* Inventory every `CONSULT_CONFIG[...]` read and map to `TASK_CONFIG`, `dispatch_task`, or `GAZER_CONFIG`.
* Resolve `pass_threshold` vs `dispatch_task.score_floor` so one rule is authoritative.
* Add `TASK_CONFIG` entries where keys exist only in `CONSULT_CONFIG` today (e.g. `validate_title`) if needed.
* Update `ASTRAL_CODE_RULES` config section list when `CONSULT_CONFIG` is removed.

## **Acceptance criteria**

* No remaining imports or dict lookups of `CONSULT_CONFIG` in runtime code.
* Dispatch + gazer + consult tests (or manual checklist) pass for: title validate, qualify, scrape JD, evaluate JD, consult do/get/like, and roster company flows unchanged in behavior.
* Docs describe the three-way split: `TASK_CONFIG` (task + outcomes), `dispatch_task` (when/who/which state), `GAZER_CONFIG` (gazer batch).

### Comments

#### chuckles — 2026-05-25T00:28:53.422Z
## Landed on origin/dev — Chuckles

- **Merge note:** `git merge origin/ftr/AST-376-…` conflicted in `config.py` — epic already on local `dev` via **prep-uat §8** + post-UAT fixes (`c46852b5`, `917b08b7`). Aborted redundant merge; pushed tested **`dev`** tip.
- Pushed **`origin/dev`** (`df52079f` → **`917b08b7`**, 37 commits — includes AST-376 rollup plus prior prep-uat integration on this line)
- Deleted **`origin/ftr/AST-376-absorb-consult-config-into-gazer-config-task-config-and-dispatch-task-metadata`**
- Moved to **Done** (were PR Ready): **AST-376** (parent), **AST-466**, **AST-467**, **AST-468**
- UAT sub-issues **474–476** were already **Done**

Push tip: **`917b08b7`**

**Engineers — merge before your next skill** (`orientation-astral` § Merge integration line):

```bash
git fetch origin
git checkout dev-<agent>
git merge origin/dev
```

Do **not** rebase `origin/dev` onto `dev-<agent>` unless Susan directs.

— Chuckles

#### chuckles — 2026-05-25T00:21:07.632Z
**UAT follow-up (local `dev`):**

- **AST-474:** Already satisfied on local UAT `dev` — `_DISPATCH_TASK_TRIGGER_SEED` mirrors `database._DISPATCH_TASK_SEED` (incl. `recheck_no_openings`, `gaze_board`). No code change needed here.
- **AST-475:** Already satisfied — `test_board_sourced_qualify_evaluate.py` present on local `dev`.
- **AST-476:** Fixed in latest commit on local `dev` — `consult.py` uses `resolve_dispatch_task_config_key`; removed `_CONSULT_PROMPT_DISPATCH`.

Still to cherry-pick to `origin/ftr/AST-376-…` when Susan wants clean ftr lines.

— Chuckles

#### chuckles — 2026-05-25T00:18:24.621Z
## Radia UAT reality-check — `origin/ftr/AST-376-…` @ `6d65c78c`

**Scope:** Parent **AST-376** definition + child plans **466 / 467 / 468** vs composite code on the rolled-up **ftr** branch (not local prep-uat `dev`, which is ahead and includes boards/471 merges).

**Baseline:** `git diff origin/dev...origin/ftr/AST-376-absorb-consult-config-into-gazer-config-task-config-and-dispatch-task-metadata` (three-dot; `origin/dev` = `df52079f`).

---

### Parent acceptance criteria

| Criterion | Verdict |
|-----------|--------|
| No `CONSULT_CONFIG` in runtime `src/` | **PASS** — Stage 6 landed on ftr in `6d65c78c` |
| `gazer.py` / `consult.py` use `GAZER_CONFIG` / `TASK_CONFIG` | **PASS** |
| `dispatcher` / `database` / `api_admin` use config helpers | **PASS** |
| Docs: three-way split + `pass_threshold` vs `score_floor` | **PASS** — `ASTRAL_CODE_RULES` §2.1 updated; no shim language |
| Component tests green at publish | **PASS** (924 at prep-uat); branch-coverage gate unchanged |

---

### Child ticket stage checklist

**AST-466 (466 stages 1–5):** **PASS** — `GAZER_CONFIG`, TASK orchestration fields, `RUBRIC_ARTIFACT_KEYS` derivation, rules doc. Stage 3 shim **superseded** by Stage 6 removal (expected on final composite).

**AST-467 (467 stages 1–4):** **PASS** with **discuss** carryover — `gazer.py`/`consult.py` clean; `test_consult.py` migrated. `_consult_orchestration` uses local `_CONSULT_PROMPT_DISPATCH` instead of `resolve_dispatch_task_config_key` (plan preferred config helper). `render_verdict` rubric-missing message still brackets **dispatch** key (`consult_*`) not orchestration key.

**AST-468 (468 stages 1–6):** **PASS** with **fix-now gap** — helpers wired; shim removed; ast438 + migration script updated. **`DISPATCH_TASK_SEED_KEYS` drift** vs `database._DISPATCH_TASK_SEED` (see sub-issue).

---

### Issues → new sub-issues (for UAT discussion)

| Sev | Topic | Action |
|-----|-------|--------|
| **fix-now** | `DISPATCH_TASK_SEED_KEYS` lists `find_job_page` (not in DB seed) and omits `recheck_no_openings` | Sub-issue filed — affects `trigger_state_used_by_scored_dispatch_task` seed walk (AST-468 Stage 1 invariant). **Local UAT `dev` already uses `_DISPATCH_TASK_TRIGGER_SEED` mirror** from prep-uat merge; cherry-pick candidate for ftr. |
| **discuss** | `ASTRAL_TEST_BIBLE` §7.13w cites `test_board_sourced_qualify_evaluate.py` but file **absent on ftr** | Sub-issue filed — restore test or update bible. File **exists on local UAT `dev`**. |
| **discuss** | Duplicate `consult_*` → `grade_*` map in `consult.py` vs `config.py` | Sub-issue filed — DRY / single source. |
| **advisory** | ftr diff includes `agent.py` / `tracker.py` changes beyond 466–468 plan boundaries (board_search / chain token parity commits) | **Explained:** integration fixes during 466/471 rollup (`fix(AST-466): restore consult board_search…`, AST-471 substrate). No separate ticket unless Susan wants scope doc refresh. |
| **advisory** | Local UAT `dev` (`c46852b5+`) ahead of ftr on boards/471 + seed sync | Expected after prep-uat §8 merge; fixes may land on `dev` first then cherry-pick to ftr per Susan's workflow. |

**Counts:** fix-now **1** · discuss **2** · advisory **2** · parent AC **PASS** with tracked gaps.

Sub-issues created under **AST-376** for the three actionable rows.

— Radia (via Chuckles orchestration)

#### chuckles — 2026-05-25T00:15:59.141Z
**[check-linear]** Option **C** done — `CONSULT_CONFIG` shim removed for UAT.

Susan chose option C during UAT: delete `_build_consult_config_shim()` and `CONSULT_CONFIG` now that **467/468** call sites use `TASK_CONFIG` / `GAZER_CONFIG` + `resolve_dispatch_task_config_key` only.

**Commits**
- Local UAT **`dev`**: `c46852b5`
- **`origin/ftr/AST-376-absorb-consult-config-…`**: `6d65c78c` (cherry-pick; ftr has no `test_board_sourced_qualify_evaluate.py`)

**Verification**
- `rg CONSULT_CONFIG src/ tests/ scripts/*.py` → **0** (feature plan docs still mention it historically)
- **924** component tests passed (branch-coverage gate unchanged on `config.py` / `roster.py`)

**Not pushed:** `origin/dev` — still Susan's call after UAT / finish-up.

— Chuckles

#### chuckles — 2026-05-24T23:55:55.006Z
[check-linear]

**Short answer: we don’t need it.** You’re right to flag this — parent **AST-376** acceptance criteria are **not fully met** on local `dev` @ `0081d062` / **`ftr/376`** @ `6ec41fdd`.

### Why the shim is still in `config.py`

1. **AST-466** introduced `_build_consult_config_shim()` + `CONSULT_CONFIG` as a **transitional** view over `TASK_CONFIG` + `GAZER_CONFIG`.
2. **AST-467** migrated `consult.py` / `gazer.py` off it (done).
3. **AST-468** Stages 1–5 moved `dispatcher.py`, `database.py`, `api_admin.py` to `resolve_dispatch_task_config_key` / `dispatch_task_key_is_scored` / `trigger_state_used_by_scored_dispatch_task` (done).
4. **AST-468 Stage 6 (hard gate)** — delete `CONSULT_CONFIG`, `_build_consult_config_shim`, and use the fixed `consult_*` → `grade_*` map only — **was never executed** on the publish tip. Plan doc explicitly deferred Stage 6 while 467 was in flight; 467 landed but Stage 6 didn’t follow.
5. **prep-uat §8 merge** kept the orphaned shim block when resolving `config.py` vs boards/471 (dispatch helpers on dev already use `_CONSULT_TASK_TO_AGENT_TASK`, not the shim).

### Current runtime state (local `dev`)

```bash
rg CONSULT_CONFIG src/   # → config.py only (shim definition + module docstring)
```

No other **`src/`** module imports or reads `CONSULT_CONFIG`. The ~75-line builder is **dead code** except **tests** (`test_config.py` asserts `CONSULT_CONFIG["consult_like"]["pass_state"]`).

### What “done” looks like for AST-376

Per **AST-468** Stage 6 + parent AC:
- Delete `_build_consult_config_shim` + `CONSULT_CONFIG`
- Update module docstring + **ASTRAL_TEST_BIBLE** §7.13w (remove “shim until 468” wording)
- Point tests at `TASK_CONFIG["grade_like"]["pass_state"]` (or grade keys generally)
- `rg CONSULT_CONFIG src/` → **zero**

### Recommendation

This is **not** a design choice to keep the shim — it’s **incomplete Stage 6**. Options:

- **A)** @Ada quick **resolve** on **`ftr/376`** (Stage 6 only, ~small diff) while parent stays **User Testing**
- **B)** Susan accepts as known gap + **follow-up ticket** before **finish-up**
- **C)** Susan says strip it now on **`ftr/376`** + local `dev` during UAT

I did **not** delete product code in this pass (orchestration-only). Say which option you want.

— Chuckles

#### susan — 2026-05-24T23:54:42.160Z
Why does CONSULT_CONFIG still exist in config.py?  I thought the purpose of this ticket was to completely remove it, dividing its anatomy between gazer and task?  Please justify why we still need this code:

```python
# ---------------------------------------------------------------------------
# CONSULT_CONFIG: transitional shim built from TASK_CONFIG + GAZER_CONFIG (AST-466).
# Authoritative orchestration literals live there; callers still use this dict until AST-467/468.
# ---------------------------------------------------------------------------
def _build_consult_config_shim() -> Dict[str, Any]:
    """Fresh dicts per outer key — do not reuse TASK_CONFIG sub-dict references (test monkeypatch)."""
    ql = TASK_CONFIG["qualify_job_listings"]
    ej = TASK_CONFIG["evaluate_jd"]
    g_do = TASK_CONFIG["grade_do"]
    g_get = TASK_CONFIG["grade_get"]
    g_like = TASK_CONFIG["grade_like"]
    vt = GAZER_CONFIG["validate_title"]
    sj_raw = GAZER_CONFIG["scrape_jd"]
    return {
        "qualify_job_listings": {
            "fallback_batch_size": ql["fallback_batch_size"],
            "pass_state": ql["pass_state"],
            "fail_state": ql["fail_state"],
            "error_state": ql["error_state"],
            "min_job_title_length": ql["min_job_title_length"],
            "rubric_artifact": ql["rubric_artifact"],
        },
        "validate_title": {
            "fallback_batch_size": vt["fallback_batch_size"],
            "pass_state": vt["pass_state"],
            "fail_state": vt["fail_state"],
        },
        "scrape_jd": {
            "fallback_batch_size": sj_raw["fallback_batch_size"],
            "pass_state": sj_raw["pass_state"],
            "fail_state": sj_raw["fail_state"],
            "error_states": list(sj_raw["error_states"]),
        },
        "evaluate_jd": {
            "fallback_batch_size": ej["fallback_batch_size"],
            "pass_state": ej["pass_state"],
            "fail_state": ej["fail_state"],
            "error_state": ej["error_state"],
            "rubric_artifact": ej["rubric_artifact"],
            "min_jd_chars": ej["min_jd_chars"],
            "not_ready_state": ej["not_ready_state"],
        },
        "consult_do": {
            "agent_task": "grade_do",
            "pass_state": g_do["pass_state"],
            "fail_state": g_do["fail_state"],
            "error_state": g_do["error_state"],
            "fallback_batch_size": g_do["fallback_batch_size"],
            "save_prefix": g_do["save_prefix"],
            "pass_threshold": g_do["pass_threshold"],
            "rubric_artifact": g_do["rubric_artifact"],
        },
        "consult_get": {
            "agent_task": "grade_get",
            "pass_state": g_get["pass_state"],
            "fail_state": g_get["fail_state"],
            "error_state": g_get["error_state"],
            "fallback_batch_size": g_get["fallback_batch_size"],
            "save_prefix": g_get["save_prefix"],
            "pass_threshold": g_get["pass_threshold"],
            "rubric_artifact": g_get["rubric_artifact"],
        },
        "consult_like": {
            "agent_task": "grade_like",
            "pass_state": g_like["pass_state"],
            "fail_state": g_like["fail_state"],
            "error_state": g_like["error_state"],
            "fallback_batch_size": g_like["fallback_batch_size"],
            "save_prefix": g_like["save_prefix"],
            "pass_threshold": g_like["pass_threshold"],
            "rubric_artifact": g_like["rubric_artifact"],
            "requires_company": g_like["requires_company"],
        },
    }


CONSULT_CONFIG = _build_consult_config_shim()
```

#### chuckles — 2026-05-24T23:50:47.836Z
## UAT Ready — Chuckles

All **3** child branches were already on **`origin/ftr/AST-376-absorb-consult-config-into-gazer-config-task-config-and-dispatch-task-metadata`** (466/467/468 rolled up by Ada). **`sub/*` branches deleted** earlier this session.

**Parent branch:** `origin/ftr/AST-376-absorb-consult-config-into-gazer-config-task-config-and-dispatch-task-metadata` @ `6ec41fdd`

**Local `dev` merge:** `0081d062` — prep-uat §8 (11-file conflict resolution vs boards/471 integration; **924** component tests pass; branch-coverage gate only).

Merged children (already on ftr before prep-uat):
1. **AST-466** — GAZER_CONFIG + TASK_CONFIG orchestration + CONSULT shim
2. **AST-467** — gazer.py / consult.py call sites
3. **AST-468** — dispatcher, database, admin resolution helpers

**Deleted from origin:**
- `sub/AST-376/AST-466-absorb-consult-config-gazer-config-and-task-config-orchestration-fields`
- `sub/AST-376/AST-467-absorb-consult-config-migrate-gazer-py-and-consult-py-call-sites`
- `sub/AST-376/AST-468-absorb-consult-config-dispatcher-database-admin-resolution-and-removal`

Local **`dev`** already merged. Restart the app if running, then test.

**Engineers — after finish-up and `origin/dev` push:** merge **`origin/dev`** into **`dev-<agent>`** per **orientation-astral § Merge integration line**.

## Manual test steps

1. **Config sanity** — In Python shell or admin: confirm `GAZER_CONFIG` keys (`validate_title`, `scrape_jd`, `gaze`) and `TASK_CONFIG` grade_* orchestration fields exist; `CONSULT_CONFIG` shim still builds from them (runtime `src/` should not import `CONSULT_CONFIG` except `config.py` until fully removed).
2. **Title validate** — Ingest a job with invalid title → `INVALID_TITLE`; valid title → proceeds toward qualify.
3. **Qualify / scrape / evaluate JD** — Run dispatch chain on a test job through `VALID_TITLE` → `PASSED_JOBLIST` → `JD_READY` → `PASSED_JD` (manifest: `test_consult.py`, `test_gazer.py`).
4. **Consult do/get/like** — Score-gated steps respect `pass_threshold` vs dispatch `score_floor` (see **ASTRAL_CODE_RULES** §2.1); LIKE requires company when configured.
5. **Board search gaze (471 + consult routing)** — Active board search row (`state=ACTIVE`) runs `process_gaze_board_batch` via `run_consult_task` / dispatcher `gaze_board`; failures set `ERROR`, success returns `ACTIVE`.
6. **Admin dispatch helpers** — Manage Tasks / adhoc preview for scored tasks resolves `consult_*` → `grade_*` keys without errors.
7. **Roster company flows** — `recheck_no_openings` / `locate_job_page` unchanged vs pre-376 behavior.

If testing fails on `dev`:
```bash
git fetch origin && git reset --hard origin/dev
```

— Chuckles

#### chuckles — 2026-05-24T03:40:24.506Z
## Branch orchestration — policy landed + AST-376 status

**New process (skills + AGENTS.md):**
- **`rollup-child`** — merge each **User Testing** child **`sub/* → ftr/*`** in **`blockedBy`** order; keep **`sub/*`** until **`prep-uat`**.
- **`publish_ref_stale.py AST-376`** — rollcall / do-all-the-things gate when **dev+N ≥ 15**.
- **`dispatch-linear` §2c** — hot-file overlap check before parallel epics.
- Engineers on sibling WIP: **`merge origin/ftr/<parent>`** on **`dev-<agent>`** after **`merge origin/dev`** + own **`sub/*`**.
- **No partial cherry-picks to `origin/dev`** during active parent (exception: Susan hotfix comment).

**STALE report (now):**
```
466  on_ftr   dev+69
467  on_ftr   dev+69
468  NOT_ON_FTR   dev+69
```

**rollup-child AST-468 attempted:** merge **`sub/468` → `ftr/`** (466+467 already on ftr @ `5bc57dd3`) — **same 5 conflicts** as prep-uat:
- `docs/ASTRAL_CODE_RULES.md`
- `docs/ASTRAL_TEST_BIBLE.md`
- `src/core/tracker.py`
- `src/utils/config.py`
- `tests/component/ui/api/test_api_admin.py`

Merge aborted; **`ftr/` unchanged**.

**Recommended finish for this epic (legacy — predates publish refresh):**
1. @susan resolve those 5 files on **`origin/ftr/AST-376-…`** (468 into 466+467 tip), push.
2. **`prep-uat AST-376`** — harness on ftr, local **`dev`**, parent → **User Testing** / Susan.
3. **Next epic:** refresh each **`sub/*` from `origin/dev`** at **Code Complete** + **User Testing** before **`rollup-child`** so **dev+69** does not recur.

— Chuckles

#### chuckles — 2026-05-24T02:39:56.485Z
## do-all-the-things pipeline update

**Completed this session (ordered steps):**
1. Betty §5b ×3 on **AST-467** — syntax fix, AST-466 merge onto 467 sub, pytest path forwarding, `invalid_title` asserts, narrowed-runbook gate skip
2. Hedy **test-astral** → **Tests Passed** (publish tip `ca2104ed`)
3. Radia **review-astral** → **Review Posted** (fix-now 0)
4. Hedy **resolve-astral** → **User Testing**

**Children rollup-safe:** AST-466, AST-467, AST-468 all **User Testing**.

**prep-uat AST-376:** **blocked** — AST-468 merge conflict after 466+467 landed on parent `ftr/` (see comment above). Parent still **In Progress** / Chuckles.

**Next:** Susan resolves `ftr/` conflicts for 468, then re-run `prep-uat AST-376`.

— Chuckles

#### chuckles — 2026-05-24T02:39:42.763Z
prep-uat merge conflict — child branch **AST-468** conflicts with the parent branch after merging siblings **AST-466** and **AST-467**.

Conflict is in:
- `docs/ASTRAL_CODE_RULES.md`
- `docs/ASTRAL_TEST_BIBLE.md`
- `src/core/tracker.py`
- `src/utils/config.py`
- `tests/component/ui/api/test_api_admin.py`

**Already merged to `origin/ftr/AST-376-absorb-consult-config-into-gazer-config-task-config-and-dispatch-task-metadata`:**
1. AST-466 ✓
2. AST-467 ✓

**Blocked:** AST-468 merge aborted (no commit).

@susan — please resolve conflicts on the parent branch (466+467 tip), push, then re-run `prep-uat AST-376` for the remaining child or merge AST-468 manually.

— Chuckles

#### chuckles — 2026-05-24T02:13:35.478Z
## do-all-the-things — resume update (post-interrupt)

**Parent:** AST-376

### Current children
| Ticket | Status | Assignee | Notes |
|--------|--------|----------|-------|
| AST-466 | **User Testing** | Ada | resolve complete; publish tip `027ceffc` |
| AST-468 | **User Testing** | Ada | resolve complete; publish tip `7b36058b` |
| AST-467 | **Tests Ready** | Betty | Hedy test-astral → **[qa-handoff]** (SyntaxError in test_consult.py @ `9b476a2d`; publish tip missing AST-466 `GAZER_CONFIG` in config.py) |

### Resume path completed this session
- Betty §5b cleared (466/468) → Ada **Tests Passed**
- Radia **Review Posted** (466/468) → Ada **resolve** → **User Testing**
- Hedy **build** 467 (466 sub merge override) → Betty **qa-astral** → **Tests Ready**
- Hedy **test-astral** 467 → **blocked**, qa-handoff to Betty

### Next
1. Betty: check-linear §5b on AST-467 — fix test typo + ensure publish tip includes AST-466 config surface (or manifest matches tip)
2. Hedy: retest when Betty reassigns
3. Radia → resolve → **User Testing** for 467
4. **prep-uat** when all three siblings **User Testing**

### Integration-line debt (unchanged)
- `dev-ada` / `dev-hedy` / `dev-betty` still diverge from `origin/dev` — merge conflicts on boards/agent paths. Publish refs are authoritative for UAT merge; engineers rebase integration line per orientation-astral after finish-up.

— Chuckles

#### chuckles — 2026-05-24T01:05:50.807Z
## do-all-the-things — run complete

**Parent:** AST-376
**Children:**
- AST-466 — GAZER_CONFIG and TASK_CONFIG orchestration fields — **Tests Ready** — Betty
- AST-467 — migrate gazer.py and consult.py call sites — **Plan Approved** — Hedy
- AST-468 — dispatcher, database, admin resolution and removal — **Tests Ready** — Betty

### Completed path
- **Dispatch:** 3 children created; `ftr/` + `sub/` branches on origin
- **plan-astral:** All three plans landed on publish refs
- **validate-plan:** AST-466/468 approved; AST-467 revised (consult_* → grade_* mapping) then approved
- **build-astral:** AST-466 + AST-468 → **Code Complete** and published; AST-467 blocked at pre-flight (AST-466 not on Hedy integration line at build time — now published at `c1c2d874`)
- **qa-astral:** AST-466 + AST-468 → **Tests Ready** with Betty manifests

### Stalled / needs Susan
- **AST-466 / AST-468:** **Tests Ready** — Ada `[qa-handoff]` to Betty: ~10 manifest failures (AST-455 token/preview drift) + AST-468 `test_api_admin.py` `NameError: cfg` (test bug). Betty owns fix; reassign Ada when green.
- **AST-467:** **Plan Approved** — build never started (466 prerequisite). **Unblock:** Hedy rebases `dev-hedy`, merges `origin/sub/AST-376/AST-466-…` (or equivalent), then **build-astral** AST-467. Note: accidental `origin/dev-hedy` push during plan revision — delete remote branch if unwanted.
- **astral-kath:** `dev-kath` mid-interactive-rebase on AST-457 doc conflict — unrelated to this epic but blocks Kath §0a.

### prep-uat
- **Skipped / blocked** — no child at **User Testing**. Siblings still **Tests Ready** and **Plan Approved**.

### After finish-up (Susan)
- Engineers **rebase** `dev-<agent>` onto `origin/dev` per **orientation-astral § Rebase integration line** — **not** `git merge origin/dev`

— Chuckles

#### chuckles — 2026-05-24T00:26:10.152Z
## Dispatch — Chuckles

Dispatched 3 child tickets from the approved definition.

| Ticket | Title | Assigned to | Branch | Blocked by |
|--------|-------|-------------|--------|------------|
| AST-466 | GAZER_CONFIG and TASK_CONFIG orchestration fields | Ada | sub/AST-376/AST-466-absorb-consult-config-gazer-config-and-task-config-orchestration-fields | — |
| AST-467 | migrate gazer.py and consult.py call sites | Hedy | sub/AST-376/AST-467-absorb-consult-config-migrate-gazer-py-and-consult-py-call-sites | AST-466 |
| AST-468 | dispatcher, database, admin resolution and removal | Ada | sub/AST-376/AST-468-absorb-consult-config-dispatcher-database-admin-resolution-and-removal | AST-466 |

Assignment rationale:
- Ada: config.py schema + dispatcher/database/admin plumbing (primary domain)
- Hedy: gazer.py + consult.py + tracker batch flows
- Katherine: not assigned this dispatch

Susan can override any assignment by reassigning the child ticket directly.
Parent moves to In Progress. prep-uat will merge child branches and hand the parent branch to Susan when all children reach Review Posted.

**Git (authoritative — ignore Linear `gitBranchName`):**
- Parent: `origin/ftr/AST-376-absorb-consult-config-into-gazer-config-task-config-and-dispatch-task-metadata`
- Children: `origin/sub/AST-376/AST-466-absorb-consult-config-gazer-config-and-task-config-orchestration-fields`, `origin/sub/AST-376/AST-467-absorb-consult-config-migrate-gazer-py-and-consult-py-call-sites`, `origin/sub/AST-376/AST-468-absorb-consult-config-dispatcher-database-admin-resolution-and-removal`

Plan attachments should use  
`https://github.com/susansomerset/astral/blob/<sub-ref-or-ftr-ref>/docs/features/...`  
after **plan-astral** lands the plan doc.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
