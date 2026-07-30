# UAT: __ markers not 1:1 &nbsp; in HTML emit

**Linear:** [AST-1027](https://linear.app/astralcareermatch/issue/AST-1027/uat-markers-not-11-andnbsp-in-html-emit)
**Parent:** [AST-1019](https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies) — Take 2: Resume Render Format discrepancies
**Publish ref:** `origin/sub/AST-1019/AST-1027-uat-markers-nbsp`

Session Resume Paste → Parse → Open HTML loses `__` / `~~` digraphs because `craft_resume_base` instructs the model to strip them (`__` → space, `~~` → hyphen). Shared `_resume_site_markers` then never sees `__`, so only the legacy `" • "` → `"\u00a0• "` rule runs — matching the UAT Actual (nbsp left of `•`, regular spaces elsewhere, including `Jira Align`). Fix the parse prompt so markers survive into content; builder expand already converts `__` → NBSP / `~~` → non-breaking hyphen on all three surfaces.

## UAT fitness

- **AC restored:** Parent AC (quoted on the bug): *“Pasting the Original-brief input fixture through Session Resume Paste Parse → Open HTML yields an embedded `<style>` that carries the golden rules… — verifiable in HTML source and print/preview.”* / *“Susan can verify by eye against the desired HTML for every laundry-list item; no judgment call on ‘close enough.’”* / *“Structure already owned by AST-993 (must remain correct under the new styles): … nested `__` / `~~` markers end-to-end.”*
- **Correct outcome:** After Parse → Open HTML on the fixture paste, HTML text nodes show NBSP (`\u00a0` / `&nbsp;` in serialized source) everywhere the paste had `__`, and non-breaking hyphens where it had `~~` — e.g. `Jira\u00a0•\u00a0Confluence` for `__•__` joins and `Jira\u00a0Align` for `Jira__Align` — matching golden contact/skills nbsp treatment.
- **Sibling check:** AST-1020 stylesheet unchanged (CSS-only). AST-1021 title/meta emit unchanged. AST-993 / AST-1007 marker contract in `_resume_site_markers` unchanged (still `__` → `\u00a0`, `~~` → `\u2011`, `" • "` → `"\u00a0• "`). Verify by string-search: no CSS edits; builder marker helper body unchanged; Open HTML still uses shared builders.
- **Not sufficient:** Removing a stacktrace / 5xx alone is **not** done — markers must be 1:1 in HTML source.
- **Wrong fix rejected:** CSS `white-space` hacks, or a surface-local post-hoc replace that skips shared builders / leaves `craft_resume_base` still stripping `__`. Builder expand is already correct when `__` is present; the bug is parse destroying digraphs before emit.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | `craft_resume_base` `cache_prompt`: preserve `__` / `~~` in section strings; stop instructing strip-to-space/hyphen; align skills/prior/contact segment rules with paste-faithful separators | data/admin (repo JSON → startup apply) |

**Out of scope (do not touch):** `src/core/builder.py` `_resume_site_markers` substitutions (AST-1007 contract); embedded stylesheet (AST-1020); document title / meta (AST-1021); inventing new marker digraphs; CSS-only “looks close” patches; `tests/`, bible (Betty).

## Root cause (plan-time)

In `data/admin/agent_task.json` → `craft_resume_base` → `cache_prompt`, **FORMATTING RULES (GLOBAL)** item 1 currently says: strip `__` (replace with space) and `~~` (replace with hyphen). Quality checklist requires “All formatting codes stripped clean.” Session parse uses that prompt (`run_session_resume_parse` → `do_task("craft_resume_base")`). After strip, `_resume_site_markers` cannot expand `__`; the asymmetric `" • "` legacy rule alone produces the UAT Actual pattern. Repo JSON is applied at bootstrap (`apply_repo_admin_json_at_startup` → retires current `agent_task` rows and loads `data/admin/agent_task.json`), so updating the JSON is the deploy path — no separate `database.py` migration required for this ticket.

## Stage 1: Preserve `__` / `~~` in `craft_resume_base` cache_prompt

**Done when:** The repo `craft_resume_base` `cache_prompt` no longer tells the model to replace `__` with space or `~~` with hyphen; it explicitly requires those digraphs to be copied into section string values (and experience job string fields) when present in the resume/paste; checklist no longer demands “formatting codes stripped clean” for `__`/`~~`; skills/contact/prior instructions do not force rewriting marked `•` separators into `|` when the paste uses bullets + markers. File is valid JSON; only the `craft_resume_base` entry’s `cache_prompt` string changes (plus any minimal segment-instruction sentences listed below).

1. In `data/admin/agent_task.json`, locate the object with `"task_key": "craft_resume_base"` and edit its `cache_prompt` string as follows (surgical text edits inside the existing prompt — do not rewrite unrelated segment synthesis rules).
2. **FORMATTING RULES (GLOBAL) item 1** — replace the current strip rule with this meaning (wording may be tightened for clarity, but must include these requirements):
   - Still strip `!` line prefixes and markdown headers (`#…`).
   - **Preserve** the two-character digraphs `__` and `~~` **literally** in every section string value (including nested experience job fields). Do **not** replace `__` with a space or `~~` with a hyphen. The HTML builder expands them later (`__` → NBSP, `~~` → non-breaking hyphen).
   - Still no HTML tags or markdown emphasis syntax in values — digraphs `__` / `~~` are typography markers, not markdown.
3. **QUALITY CHECKLIST** — remove or rewrite the bullet “All formatting codes stripped clean” so it instead requires: when the resume/paste contains `__` or `~~`, those digraphs appear unchanged in the corresponding JSON string values.
4. **Segment instructions that currently fight markers** (edit only these sentences as needed):
   - **`technical_skills`:** Stop requiring items separated by `" | "` when the paste uses `•` / `__•__`. Require: preserve category lines and item separators **from the resume/paste** (including `__`, `~~`, and `•`); do not rewrite marked bullet separators into pipes.
   - **`prior_experience`:** Remove “stripped of formatting codes”; preserve `__` / `~~` / `•` from the paste line.
   - **`candidate_contact_detail`:** When the paste uses `__•__` (or `__` around contact parts), preserve those digraphs in the single contact string; do not expand them to ordinary spaces. (Plain `" • "` joins remain OK when the paste has no markers.)
   - **`core_competencies`:** Prefer paste separators; if the paste uses marked `•` / `__`, preserve them rather than forcing `" | "`.
5. Do **not** change `_resume_site_markers` in `src/core/builder.py`.
6. Do **not** edit other `task_key` rows in `agent_task.json`.
7. Do **not** edit `tests/` or bible — Betty owns assertions after Code Complete.
   ⚠️ **Decision:** Prompt preserve + existing shared builder expand (not a builder rewrite). Diagnosis matches: expand looks “incomplete” only because parse destroyed digraphs first. Parent epic forbids Manage Tasks *redesign*; this is a one-rule + checklist + separator-faithfulness patch on `craft_resume_base` only. Startup `apply_repo_admin_json_at_startup` publishes the JSON into DB — no new migration function.

## Stage 2: Builder contract lock + three-surface proof (manual / build verification)

**Done when:** With in-memory content that still contains `__` / `~~` (as after a correct parse), `build_session_base_resume` / `build_base_resume` / `build_resume_from_job` HTML shows NBSP for every `__` and non-breaking hyphen for every `~~` on skills/contact/competencies-style strings (same shared `_emit_html_document` path). Confirm `_resume_site_markers` source is unchanged from pre-ticket tip. Spike dumps only under `debug/spikes/AST-1027/` if used — never commit; never repo-root `artifacts/`.

1. During **build-child**, confirm `git diff` does **not** touch `src/core/builder.py` marker helpers.
2. Exercise `_resume_site_markers` / session builder with the bug sample skill line containing `Jira__•__Confluence` and `Jira__Align` — expect `\u00a0` on both sides of `__•__` and between `Jira`/`Align`.
3. Note for UAT: after deploy/restart so startup applies repo JSON, re-run Session Resume Paste Parse → Open HTML on the parent fixture; HTML source must show 1:1 `__` → NBSP (not ordinary spaces on word joins).
4. If Stage 1 prompt text cannot be applied without breaking JSON / schema tokens (`{$RESPONSE_SCHEMA}` must remain), **stop**, comment on **bug** AST-1027 with the Stage blocked template, and wait.

## Self-Assessment

**Scope:** `Single-Component` — `craft_resume_base` `cache_prompt` text in `data/admin/agent_task.json` only; builder marker expand left intact.

**Conf:** `high` — UAT Actual matches “`__` stripped then asymmetric `" • "` rule”; prompt line explicitly orders that strip; startup applies repo JSON.

**Risk:** `Medium` — prompt change affects all `craft_resume_base` consumers (session paste and candidate craft); wrong wording could leave markers stripped or reintroduce markdown noise — mitigated by explicit preserve language and narrow file scope.

## Code Rules self-review

- §1.3 DRY: one shared expand path remains `_resume_site_markers`; prompt stops destroying its inputs.
- §1.1 / scope isolation: no CSS; no AST-1021 chrome; no new marker syntax.
- §2.1: prompt lives in repo admin JSON (existing AST-782 path), not new config magic.
- §3.6: spikes under `debug/spikes/AST-1027/` only if used.
- Engineer test-tree ban: no `tests/` or bible edits.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1019/AST-1027-uat-markers-nbsp`
**Plan path:** `docs/features/artifacts/ast-1027-uat-markers-nbsp.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `eedc91e4` | `craft_resume_base` cache_prompt preserves `__` / `~~`; paste-faithful separators |
| 2 | — | Builder markers unchanged; session expand proof for sample skill/contact lines |

**Tip:** `eedc91e4` on `origin/sub/AST-1019/AST-1027-uat-markers-nbsp`

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1027
**Publish ref tip (pre-docs):** `b16675cd6ff0d0fbfa26f0ba7c1e0e143304967d`
**Overall:** CLEAN

### What’s solid

- Stage 1: `craft_resume_base` `cache_prompt` preserves `__` / `~~`; checklist no longer demands strip-clean; skills/contact/prior/competencies keep paste separators.
- Builder `_resume_site_markers` untouched (three-dot has no `src/` product delta for this ticket’s intent).
- Semantic JSON diff is only that one `cache_prompt` field (other task rows equal after parse).

### Issues / findings

None (fix-now / discuss).

### Recommended actions

resolve-child → User Testing.

## Resolution

**2026-07-29** — Radia **CLEAN**; no fix-now / discuss items.

- Product tip remains `eedc91e4` (`craft_resume_base` preserve `__`/`~~`).
- Intake: Radia `docs(AST-1027)` @ `f8f0f324` on `origin/sub/AST-1019/AST-1027-uat-markers-nbsp`.
- No product or test-tree changes on resolve.

**UAT note:** restart/deploy so startup applies repo `agent_task.json`, then Session Resume Paste → Parse → Open HTML on the fixture; expect 1:1 `__` → `&nbsp;`.
