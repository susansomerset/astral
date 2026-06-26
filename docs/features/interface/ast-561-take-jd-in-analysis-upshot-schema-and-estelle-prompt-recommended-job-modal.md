<!-- linear-archive: AST-561 archived 2026-06-15 -->

## Linear archive (AST-561)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-561/take-jd-in-analysis-upshot-schema-and-estelle-prompt-recommended-job  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-499 — Recommended Job Modal  
**Blocked by / blocks / related:** parent: AST-499; blocks: AST-565; related: AST-480; related: AST-313

### Description

## What this implements

Extend the `analysis_upshot` consult contract so the JD phase has Estelle's per-phase thoughts in the same shape as DO/GET/LIKE: add `take_jd` to the JSON schema, update the Estelle prompt, and persist via the existing analysis_upshot dispatch and `job_data` path ([AST-480](https://linear.app/astralcareermatch/issue/AST-480) area). No React or report UI in this ticket.

## Acceptance criteria

10. `take_jd` is persisted by analysis_upshot task and rendered on the JD tab.

(Data contract from parent: Add `take_jd` to `analysis_upshot` schema and Estelle prompt so JD phase has the same "thoughts above vectors" shape as DO/GET/LIKE. Report UX is the contract; do not invent fields only in React.)

## Boundaries

* Does **not** build the Recommended Job Report modal (sibling Katherine).
* Does **not** implement **Generate Artifacts** / **Cancel** API or UI (sibling Hedy).
* Does **not** change consult scoring, dispatch batching, or graders beyond schema/prompt/persist for `take_jd`.

## Notes for planning

* Align with [AST-313](https://linear.app/astralcareermatch/issue/AST-313) artifact pipeline prompt patterns.
* Katherine's report consumes `take_jd` on the JD tab after this lands.

## Git branch (authoritative)

Per **orientation-astral** branch law: parent `ftr/AST-499-recommended-job-modal`, child `sub/AST-499/<ticket-id>-take-jd-analysis-upshot-schema-estelle-prompt`. Created at dispatch-linear.

### Comments

#### radia — 2026-06-03T03:02:15.149Z
**Review Posted** — `origin/dev...origin/sub/AST-499/AST-561-take-jd-analysis-upshot-schema-estelle-prompt` @ `74746cbe` (build `ecc6be1e`, tests `0ddf2b24`).

**Plan doc:** [ast-561-take-jd…](https://github.com/susansomerset/astral/blob/sub/AST-499/AST-561-take-jd-analysis-upshot-schema-estelle-prompt/docs/features/interface/ast-561-take-jd-in-analysis-upshot-schema-and-estelle-prompt-recommended-job-modal.md#radia-review-ast-561) — Radia review section.

### fix-now
None.

### discuss
- **AST-499 AC #10** (“rendered on JD tab”) — correctly deferred to **AST-565**; this ticket only adds schema + prompt + persist path.
- Plan Stage 2 described build-time `save_agent_task`; ship uses idempotent **`_apply_ast561_analysis_upshot_take_jd_migration`** (same family as AST-469). Acceptable; **`_AST561_ANALYSIS_UPSHOT_USER_PROMPT_SEED`** is fallback when live prompts are empty.

### advisory
- Betty’s bible commit on publish tip also carries **§7.13zq/zs/zv** (sibling manifests) — integration-line sync, not AST-561 product scope.
- Migration patches **`user_prompt`** / **`nocache_prompt`** only; spot-check Manage Tasks if JSON keys live solely in **`cache_prompt*`** segments on a prod DB.

### §3 rubric
- **§2.1** config: `take_jd` required on `analysis_upshot` only — pass.
- **§B2** layers: data migration + utils config; no UI/core drift — pass.
- **§D2**: migration `sqlite3.Error` → return matches schema-ensure tradeoff — justified.

**Ada:** `resolve-astral` — no product edits expected; dry-run merge with `origin/dev`, then **User Testing**.

#### radia — 2026-06-03T03:01:59.697Z
**Review** — `origin/dev...origin/sub/AST-499/AST-561-take-jd-analysis-upshot-schema-estelle-prompt` (tip `74746cbe` after review doc).

**fix-now:** none.

**discuss**
- Parent **AST-499** AC #10 (“rendered on JD tab”) is **AST-565** only; this ticket correctly stops at persist + prompt/schema.

**advisory**
- `docs/ASTRAL_TEST_BIBLE.md` on `0ddf2b24` also adds **§7.13zq/zs/zv** (sibling manifests) — integration-line bible sync, not **AST-561** product scope.
- Migration updates `user_prompt` / `nocache_prompt` only; if JSON key lists live only in `cache_prompt*` segments, spot-check Manage Tasks post-deploy.

**Plan / rules:** `take_jd` in `TASK_CONFIG["analysis_upshot"]["response_schema"]` (§2.1); idempotent `_apply_ast561_analysis_upshot_take_jd_migration` matches **AST-469** silent-return pattern; no `consult` / UI / dispatch diff; `tracker.save_job_data` wholesale persist unchanged.

**Doc:** `docs/features/interface/ast-561-take-jd-in-analysis-upshot-schema-and-estelle-prompt-recommended-job-modal.md` (Radia review section) @ `74746cbe`.

**Ada:** `resolve-astral` — no product edits expected from this review.

#### betty — 2026-06-03T02:55:17.499Z
**Tests Ready** — manifest for `test-astral` on `origin/sub/AST-499/AST-561-take-jd-analysis-upshot-schema-estelle-prompt` @ `0ddf2b24`.

1. `python3 -m pytest tests/component/utils/test_config.py::TestAst480AnalysisUpshotConfig -q`  
   (or `./scripts/testing/run_component_tests.sh` with the same node id — harness uses project venv)

**Scope:** Backend-only (**AST-561**). **`take_jd`** required on `TASK_CONFIG["analysis_upshot"]["response_schema"]`; prompt migration in `database.py`. No frontend/parser changes this ticket (**AST-565** owns `analysisUpshot.ts` + JD tab).

**Optional regression** (same spine as §7.13y — mocks do not schema-validate synthesis JSON):  
`tests/component/core/test_consult.py::TestRunConsultTaskRoutes::test_routes_passed_like_to_analysis_upshot_batch`

`docs/ASTRAL_TEST_BIBLE.md` on publish ref: `974da744e2d6b17992e1013f8fe4dc99616d66f8` (§7.13zw).

#### ada — 2026-06-02T22:34:11.193Z
Plan: `docs/features/interface/ast-561-take-jd-in-analysis-upshot-schema-and-estelle-prompt-recommended-job-modal.md`

GitHub: https://github.com/susansomerset/astral/blob/sub/AST-499/AST-561-take-jd-analysis-upshot-schema-estelle-prompt/docs/features/interface/ast-561-take-jd-in-analysis-upshot-schema-estelle-prompt-recommended-job-modal.md

Publish: `origin/sub/AST-499/AST-561-take-jd-analysis-upshot-schema-estelle-prompt` @ `4232822b`

**Self-Assessment**

- **Scope:** `Single-Component` — One `TASK_CONFIG` schema field and one `agent_task` prompt version for `analysis_upshot`; no consult router or UI in this ticket.
- **Conf:** `high` — Same pattern as AST-480 (`take_*` strings + existing `_run_analysis_upshot_batch` persist).
- **Risk:** `Medium` — Prompt/schema mismatch would strand jobs on `PASSED_LIKE_RETRY` or ship empty `take_jd` until prompt tuning; Katherine (AST-565) depends on the field being populated.

---

# AST-561 — take_jd in analysis_upshot schema and Estelle prompt (Recommended Job Modal)

**Parent:** [AST-499 — Recommended Job Modal](https://linear.app/astralcareermatch/issue/AST-499/recommended-job-modal)  
**Publish ref (origin only):** `sub/AST-499/AST-561-take-jd-analysis-upshot-schema-estelle-prompt`  
**Linear:** [AST-561](https://linear.app/astralcareermatch/issue/AST-561/take-jd-in-analysis-upshot-schema-and-estelle-prompt-recommended-job)

Extend the existing **`analysis_upshot`** consult contract so the JD phase has Estelle's per-phase narrative in the same shape as DO/GET/LIKE: add **`take_jd`** to **`TASK_CONFIG["analysis_upshot"]["response_schema"]`**, update the **`analysis_upshot`** Manage Tasks prompt so the model emits it, and rely on the existing **`_run_analysis_upshot_batch`** path to persist under **`job_data.analysis_upshot`**. **No React**, report shell, or dispatch changes in this ticket — **AST-565** (Katherine) consumes **`take_jd`** on the JD tab after this lands.

## Prerequisite

**AST-480** / **AST-479** are **Done** on the integration line: **`analysis_upshot`** dispatch at **`PASSED_LIKE`**, JSON persist → **`RECOMMENDED`**, schema already has **`take_do`**, **`take_get`**, **`take_like`**, **`whole_jd_upshot`**, segments, questions, caveats. If **`TASK_CONFIG["analysis_upshot"]`** or **`get_agent_task("analysis_upshot")`** is missing, **stop** and comment on **AST-561** — do not invent parallel task keys.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add **`take_jd`** to **`TASK_CONFIG["analysis_upshot"]["response_schema"]`** (`str`, required), adjacent to the other **`take_*`** keys | utils |
| `src/data/database.py` | Version **`agent_task`** row **`task_key="analysis_upshot"`** via **`save_agent_task`** (prompt prose only — no schema DDL) | data |

**Explicitly out of scope (ticket boundaries):**

| Area | Owner / note |
|------|----------------|
| `src/ui/frontend/src/lib/analysisUpshot.ts`, `JobAnalysisReportModal.tsx`, report tabs | **AST-565** (Katherine) — parent AC #10 "rendered on JD tab" is satisfied there, not here |
| `src/core/consult.py` | No runner change — **`tracker.save_job_data(..., {"analysis_upshot": parsed})`** already stores the full validated dict |
| `tests/`, `docs/ASTRAL_TEST_BIBLE.md` | **Betty** / **`qa-astral`** after **Code Complete** (mirror **`take_jd`** in config + parser tests) |
| Dispatch seeds, **`JOB_STATES`**, graders | Unchanged |

**Spike / Playwright:** none.

---

## Stage 1: Config — `take_jd` in response_schema

**Done when:** `TASK_CONFIG["analysis_upshot"]["response_schema"]` includes **`take_jd`** as a required string; `python3 -m py_compile src/utils/config.py` passes; a grep of **`response_schema`** for **`analysis_upshot`** shows **`take_jd`** before **`take_do`** (same ordering as DO/GET/LIKE for readability).

1. In **`src/utils/config.py`**, inside **`TASK_CONFIG["analysis_upshot"]["response_schema"]`**, add immediately before **`take_get`** (or immediately after **`take_like`** — keep all four **`take_*`** keys grouped):

   ```python
   "take_jd": {"type": "str", "required": True},
   ```

2. Do **not** change **`pass_state`**, **`error_state`**, **`scored`**, dispatch seeds, or any other task keys.

⚠️ **Decision:** **`take_jd`** is required on every successful synthesis (empty string is still a string — validation passes; substantive content is prompt-enforced, same as **`take_do`** today). **`whole_jd_upshot`** remains the job-level summary; **`take_jd`** is JD-phase "Estelle's Thoughts" for the report tab (parent **AST-499**), not a rename of **`whole_jd_upshot`**.

---

## Stage 2: Estelle prompt — `analysis_upshot` agent_task

**Done when:** The current **`agent_task`** row for **`analysis_upshot`** instructs the model to return JSON including **`take_jd`** with the same intent as **`take_do`** / **`take_get`** / **`take_like`** (candidate-facing JD-phase narrative above rubric vectors in the eventual report). A dry read of the updated **`user_prompt`** (and **`nocache_prompt`** if that segment lists output keys) shows **`take_jd`** documented next to the other takes and distinguished from **`whole_jd_upshot`**.

1. Call **`database.get_agent_task("analysis_upshot")`**. If **`None`**, **stop** with **🛑** on **AST-561**: Manage Tasks row missing — Susan must seed **`analysis_upshot`** before build continues (same gate as **AST-480** / **AST-313** workflow).

2. Read the current **`user_prompt`** (and **`nocache_prompt`** if it enumerates JSON keys). Locate where **`take_do`**, **`take_get`**, and **`take_like`** are defined (tone, length, audience = candidate, "thoughts above vectors" framing per parent **AST-499**).

3. Add **`take_jd`** instructions by **mirroring** the DO/GET/LIKE take wording for the **JD** phase:
   - One string field **`take_jd`** in the top-level JSON object.
   - Content: Estelle's JD-phase thoughts (what matters about fit to the listing / role definition from the candidate's perspective), not a repeat of **`whole_jd_upshot`** (job summary) and not rubric vector regurgitation.
   - Align with **AST-313** artifact-pipeline prompt style: direct, second-person or candidate-addressed prose as existing takes use — **copy the pattern, do not invent a new voice**.

4. If the prompt lists required JSON keys explicitly, add **`take_jd`** to that list in the same bullet/line style as **`take_do`**.

5. Persist via **`database.save_agent_task("analysis_upshot", user_prompt=<updated>, nocache_prompt=<updated if step 3 touched it>, ...)`**:
   - Pass **`agent_id`**, **`system_prompt`**, **`cache_prompt`**, **`cache_prompt_b|c|d`**, **`run_next`** from the fetched row unchanged (use the existing values from **`get_agent_task`** — **`None`** kwargs mean "leave untouched" only when omitting keys; for a prompt-only edit, pass the unchanged segments explicitly from the row dict so versioning compares correctly).
   - **Do not** add a repo file containing full prompt text unless Susan directs — the authoritative store is **`agent_task`** in SQLite (Manage Tasks / **AST-454** versioning).

6. **Optional verification (manual, not pytest):** After deploy to a dev DB with a **`PASSED_LIKE`** fixture job, one **`analysis_upshot`** run should produce **`job_data.analysis_upshot.take_jd`** as a non-empty string when the model follows the prompt. If empty strings appear in production, treat as prompt tuning — **not** a code change in this ticket.

⚠️ **Decision:** Prompt update ships in the **same commit** as config (**Stage 1 + 2 one commit** on **`dev-ada`** during **build-astral**) so schema validation and model instructions land together; partial deploy (schema without prompt) would spike **`PASSED_LIKE_RETRY`** rates.

---

## Stage 3: Verification (no test-tree edits)

**Done when:** `python3 -m py_compile src/utils/config.py` passes; grep confirms **`take_jd`** only appears in **`analysis_upshot`** schema (not duplicated on other tasks); **`consult.py`** batch path still references **`TASK_CONFIG["analysis_upshot"]`** unchanged.

1. Run **`python3 -m py_compile src/utils/config.py`**.
2. Grep **`take_jd`** under **`src/`** — expect **`config.py`** only until **AST-565** / Betty test updates.
3. Confirm **`_run_analysis_upshot_batch`** still saves **`parsed`** wholesale — no edit required.

**Handoff notes (comment on AST-561 at Code Complete, plain text):**

- **AST-565:** add **`take_jd`** to **`AnalysisUpshot`**, **`parseAnalysisUpshot`**, JD tab "Estelle's Thoughts" block above vectors.
- **Betty:** extend **`TestAst480AnalysisUpshotConfig`** (or sibling) and **`test_analysisUpshot.test.ts`** fixtures with **`take_jd`**.

---

## Execution contract (for the developer agent)

Per **plan-astral** / **build-astral**: execute **Stage 1 → 2 → 3** in order; **one commit** on **`dev-ada`** containing config + prompt versioning, subject includes **`AST-561`**, then **`git-store-code-commit`** to **`origin/sub/AST-499/AST-561-take-jd-analysis-upshot-schema-estelle-prompt`**. Do not edit **`tests/`**. Do not edit frontend files. If **`get_agent_task("analysis_upshot")`** is missing or prompt segments cannot be loaded, **stop** — **🛑** on **AST-561**, wait for Susan.

---

## Self-Assessment

**Scope:** `Single-Component` — Touches **`TASK_CONFIG`** for one task and versions one **`agent_task`** prompt row; no consult router, dispatch, or UI.

**Conf:** `high` — Reuses the established **AST-480** schema + persist pattern; **`take_jd`** is a fourth parallel string field and prompt bullet.

**Risk:** `Medium` — A weak or missing prompt instruction causes validation failures (**`PASSED_LIKE_RETRY`**) or empty **`take_jd`** on new **`RECOMMENDED`** jobs until prompt tuning; config-only deploy without prompt edit would break synthesis.

---

## Self-review against ASTRAL_CODE_RULES

- **§1.3 DRY:** Reuse existing **`analysis_upshot`** task and **`save_agent_task`** versioning; no second synthesis path.
- **§2.1 config:** **`take_jd`** lives only in **`TASK_CONFIG["analysis_upshot"]["response_schema"]`**.
- **§2.4 batch:** No batch semantics change.
- **§2.6 state machine:** No new transitions.
- **§3.3 imports:** Prompt edit calls **`database.save_agent_task`** from the build commit (same pattern as Manage Tasks PUT) — **`data`** layer only; no new **`core` → `ui`** edges.

**§3.5 naming:** Field **`take_jd`** matches **`take_do`** / **`take_get`** / **`take_like`** prefix convention.

---

## Prompt snippet (append to `user_prompt` key list / JD section)

Use this verbatim intent when editing the live **`user_prompt`** (adapt only for tense/format to match surrounding paragraphs):

> **`take_jd`** (string, required): Estelle's thoughts for the **JD** phase — candidate-facing narrative explaining what stands out about this job listing and role definition after JD consult, in the same voice and depth as **`take_do`**, **`take_get`**, and **`take_like`**. Place JD-phase rubric context in mind but do not dump raw grades. This is **not** **`whole_jd_upshot`** (overall job summary).

---

## Radia review (AST-561)

**Baseline:** `git diff origin/dev...origin/sub/AST-499/AST-561-take-jd-analysis-upshot-schema-estelle-prompt`  
**Publish tip:** `0ddf2b24` (build `ecc6be1e`, test/bible `0ddf2b24`)

### What's solid

- **`take_jd`** is a required `str` on **`TASK_CONFIG["analysis_upshot"]["response_schema"]`**, grouped with the other **`take_*`** keys and ordered before **`take_get`** (matches plan Stage 1).
- **`_apply_ast561_analysis_upshot_take_jd_migration`** is idempotent (early exit when **`take_jd`** already appears in **`user_prompt`** or **`nocache_prompt`**), versions via **`_save_agent_task_on_connection`**, and follows the same **`sqlite3.Error` → return** pattern as **`_apply_ast469_*`** (§D2 tradeoff: schema-ensure path must not brick startup).
- Prompt prose distinguishes **`take_jd`** from **`whole_jd_upshot`** and mirrors DO/GET/LIKE “thoughts above vectors” intent; empty DB prompts get the full seed template.
- Ticket boundaries held on the product commits: no **`consult.py`**, UI, or dispatch edits; **`tracker.save_job_data(..., {"analysis_upshot": parsed})`** still persists the full validated dict.
- **`TestAst480AnalysisUpshotConfig::test_ast561_response_schema_includes_take_jd`** and bible **§7.13zw** on the publish tip align with the manifest Betty documented.

### Issues

| Severity | Location | Finding |
| --- | --- | --- |
| — | — | No **fix-now** items. |
| **discuss** | Parent **AST-499** AC #10 | “Rendered on the JD tab” is intentionally **AST-565** (Katherine); this ticket only supplies the persisted field — confirm Susan accepts deferral (plan already says so). |
| **advisory** | `docs/ASTRAL_TEST_BIBLE.md` on `0ddf2b24` | Test commit also documents **§7.13zq/zs/zv** (sibling **AST-549/551/552/562** manifests). Fine for integration-line bible sync; not part of **AST-561** code diff. |
| **advisory** | `agent_task` **`cache_prompt*`** segments | Migration patches **`user_prompt`** / **`nocache_prompt`** only (per plan). If a live DB lists JSON keys solely in cache segments, spot-check Manage Tasks after deploy. |

### Recommended actions

| Owner | Action |
| --- | --- |
| **Ada** | **`resolve-astral`**: no product edits expected from this review; dry-run merge with **`origin/dev`** per skill §9a, then **User Testing**. |
| **Katherine / AST-565** | Wire **`take_jd`** in **`analysisUpshot.ts`** + JD tab “Estelle's Thoughts” above vectors. |
| **Susan / ops** | Optional: one **`PASSED_LIKE` → `analysis_upshot`** run on dev to confirm non-empty **`take_jd`** after prompt tuning (empty string still passes schema). |

**Rubric:** Plan fidelity and **§2.1** config authority **pass**; no **B2** layer violations in diff; migration silent-return matches established data-layer pattern.

---

## Resolution (2026-06-03)

| Field | Value |
|-------|-------|
| Publish ref | `origin/sub/AST-499/AST-561-take-jd-analysis-upshot-schema-estelle-prompt` |
| Product tip (pre-resolve) | `74746cbe` (build `ecc6be1e`, tests `0ddf2b24`) |
| Radia doc | `74746cbe` (on publish ref; merged onto `dev-ada` via attach merge) |

**vs Radia review:** **fix-now:** none. **Discuss:** Parent **AST-499** AC #10 (“rendered on JD tab”) deferred to **AST-565** — accepted per plan boundaries. Build-time `save_agent_task` vs idempotent `_apply_ast561_analysis_upshot_take_jd_migration` — accepted (AST-469 family). **Advisory:** bible §7.13zq/zs/zv sibling sync and `cache_prompt*` spot-check — no code change.

**Product changes:** None — happy path.

**§9a:** Publish ref dry-run clean into `origin/dev` and `origin/ftr/AST-499-recommended-job-modal`.

**Outcome:** **User Testing** — assignee Ada (implementer unchanged). **AST-565** consumes `take_jd` on JD tab.

---
