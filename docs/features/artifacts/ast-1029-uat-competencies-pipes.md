# UAT: competencies separators print as pipes

**Linear:** [AST-1029](https://linear.app/astralcareermatch/issue/AST-1029/uat-competencies-separators-print-as-pipes)
**Parent:** [AST-1019](https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies) — Take 2: Resume Render Format discrepancies
**Publish ref:** `origin/sub/AST-1019/AST-1029-uat-competencies-pipes`

Session Resume Paste → Parse → Open HTML shows Core Competencies joined with `|` (e.g. `AI-Assisted Delivery | Cross-Functional Execution | …`) instead of golden / fixture `•` bullets. Shared builder `_emit_body_sections_html` HTML-escapes `core_competencies` / `prior_experience` into `<p class="competencies-list">` with **no** separator rewrite — pipes arrive from `craft_resume_base`. AST-1027 already softened competencies to “prefer paste separators… rather than rewriting to `|`”, but that still allows the model to invent `|` when enriching from LinkedIn / strengths. Harden the prompt: **require** bullet joins and **forbid** pipe separators.

## UAT fitness

- **AC restored:** Parent AC (quoted on the bug): *“Susan can verify by eye against the desired HTML for every laundry-list item; no judgment call on ‘close enough.’”* / *“Structure already owned by AST-993 … Core Competencies one competencies list … nested `__` / `~~` markers end-to-end.”*
- **Correct outcome:** `.competencies-list` text uses `•` separators matching the golden / fixture treatment (with NBSP where `__` markers require after AST-1027 preserve + builder expand) — not `|`.
- **Sibling check:** AST-1020 competencies CSS (uppercase / letter-spacing) unchanged. AST-1027 marker preserve still required. AST-1028 title/tagline split unchanged. Prior Experience uses the same `.competencies-list` markup — separator rules must stay consistent for that string when present. Verify: no CSS edits; builder competencies emit remains escape-only (no CSS `content:` fake bullets).
- **Not sufficient:** Removing a stacktrace / 5xx alone is **not** done — DOM text must show bullets, not pipes.
- **Wrong fix rejected:** CSS `content:` / `::before` fake bullets while leaving `|` in the DOM; fixing only session surface and skipping base / job-tailored (all share `_emit_html_document`); rewriting competency **wording** rather than separators.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | `craft_resume_base` `cache_prompt`: harden `### core_competencies` (and align `### prior_experience`) — require `•` joins, forbid `|` separators | data/admin (repo JSON → startup apply) |

**Out of scope (do not touch):** `src/core/builder.py` competencies CSS or inventing CSS pseudo-bullets (AST-1020); marker digraph rules beyond separator choice (AST-1027); title/tagline (AST-1028); rewriting competency phrases; `tests/`, bible (Betty).

## Root cause (plan-time)

`_emit_body_sections_html` for `core_competencies` / `prior_experience` does `html.escape(str(text))` into `<p class="competencies-list">` — no `|`→`•` transform. After AST-1027, `### core_competencies` says *prefer* paste separators and *rather than* rewriting to `" | "` — soft language; the model still emits `|` when synthesizing/enriching (UAT Actual). Parent fixture / golden use `•` (often with `__` around tokens). Repo JSON applies at bootstrap via `apply_repo_admin_json_at_startup` — no new `database.py` migration.

## Stage 1: Harden competencies / prior separator rules in `craft_resume_base`

**Done when:** The repo `craft_resume_base` `cache_prompt` requires Core Competencies (and Prior Experience when present) to use `•` item separators — never `|` — whether copying from paste or synthesizing/enriching; paste `__` / `~~` / marked `•` forms are still preserved (AST-1027); file is valid JSON; only the `craft_resume_base` entry’s `cache_prompt` string changes for this stage.

1. In `data/admin/agent_task.json`, locate `"task_key": "craft_resume_base"` and edit its `cache_prompt` (surgical text — do not rewrite experience job-array, tagline, marker-preserve global rules, or unrelated segments).
2. **`### core_competencies`** — replace the soft “Prefer separators… rather than rewriting to `" | "`” sentence(s) with this meaning (wording may be tightened; must include these requirements):
   - Present as a **single string**.
   - Item separator is the bullet character `•` (plain ` • ` between items, or paste forms such as `__•__` / `__` around tokens + `•` — preserve markers when present).
   - **Do not** use `|` (pipe) as an item separator — not `" | "`, not bare `|`.
   - When the paste already uses `•` / marked bullets, copy those separators (and `__` / `~~`) unchanged.
   - When enriching or synthesizing a list (e.g. from LinkedIn strengths with evidence), **join with ` • `**, never `|`.
   - Still: evidence-backed only; keyword/phrase list; do not invent competencies; preserve `__` / `~~` when in the paste.
3. **`### prior_experience`** — ensure the condensed prior line uses the same bullet convention when listing roles (example already uses `•`); add an explicit **do not use `|` as separators** line so Prior Experience stays consistent with `.competencies-list` styling. Keep empty-string-when-absent behavior.
4. **QUALITY CHECKLIST** — add a bullet: `core_competencies` (and `prior_experience` when non-empty) use `•` separators, not `|`.
5. Do **not** change `_emit_body_sections_html` / CSS in `src/core/builder.py`.
6. Do **not** edit other `task_key` rows.
7. Do **not** edit `tests/` or bible — Betty owns assertions after Code Complete.
   ⚠️ **Decision:** Prompt harden only (not builder `|`→`•` rewrite, not CSS fake bullets). Emit is already faithful; soft “prefer” from AST-1027 left a pipe default for enrichment. Deterministic DOM fidelity for already-piped JSON would need a builder normalize — reject for this ticket to keep Single-Component / sibling pattern; if UAT still shows pipes after deploy+re-parse, escalate rather than silently adding emit rewrite mid-build. Startup applies repo JSON — no new migration.

## Stage 2: Builder emit lock + three-surface proof (manual / build verification)

**Done when:** With in-memory content whose `core_competencies` string already uses `•` separators, session / base / job-tailored HTML shows those bullets inside `.competencies-list` (escaped). Confirm builder does not introduce `|`. Negative note: in-memory content that still contains `|` will still render pipes (documents parse harden is required). Spike dumps only under `debug/spikes/AST-1029/` if used — never commit; never repo-root `artifacts/`.

1. During **build-child**, confirm `git diff` does **not** touch `src/core/builder.py` competencies emit / CSS.
2. Exercise session builder with `core_competencies` like `AI-Assisted Delivery • Cross-Functional Execution • Risk and Dependency Management` — expect that text (HTML-escaped) in `.competencies-list`, no `|`.
3. Note for UAT: after deploy/restart so startup applies repo JSON, re-run Session Resume Paste Parse → Open HTML; `.competencies-list` must use bullets, not pipes.
4. If Stage 1 prompt text cannot be applied without breaking JSON / `{$RESPONSE_SCHEMA}`, **stop**, comment on **bug** AST-1029 with the Stage blocked template, and wait.

## Self-Assessment

**Scope:** `Single-Component` — `craft_resume_base` `cache_prompt` text in `data/admin/agent_task.json` only; builder competencies emit left intact.

**Conf:** `high` — UAT Actual is `|` in `.competencies-list`; builder is escape-only; soft prefer language still names `" | "` as the thing not to rewrite to, which leaves pipe as the enrichment default.

**Risk:** `Medium` — prompt change hits all `craft_resume_base` consumers; over-strict wording could fight a rare paste that intentionally uses `|` inside a competency phrase — mitigated by forbidding `|` as **item separators** (space-pipe-space / pipe between items), not rewriting arbitrary characters inside phrases; checklist focuses on separators.

## Code Rules self-review

- §1.3 DRY: one shared emit path remains; prompt stops feeding it pipe-joined lists.
- §1.1 / scope isolation: no CSS; no builder separator rewrite; no AST-1020 chrome edits.
- §2.1: prompt lives in repo admin JSON (existing AST-782 path).
- §3.6: spikes under `debug/spikes/AST-1029/` only if used.
- Engineer test-tree ban: no `tests/` or bible edits.
