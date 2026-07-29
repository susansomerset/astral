# UAT: `<no bullet>` lead emitted as list item

**Linear:** [AST-1030](https://linear.app/astralcareermatch/issue/AST-1030/uat-no-bullet-lead-emitted-as-list-item)
**Parent:** [AST-1019](https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies) — Take 2: Resume Render Format discrepancies
**Publish ref:** `origin/sub/AST-1019/AST-1030-uat-no-bullet-lead`

Session Resume Paste → Parse → Open HTML folds the Somerset Consulting `<no bullet>` lead into the role `<ul>` as the first `<li>`, with no preceding `<p class="role-description">`. Shared `_emit_experience_jobs_html` / `_split_role_accomplishments` already treat lines starting with `BUILD_CONFIG["experience_role_layout"]["lead_line_prefix"]` (`<no bullet>`) as lead paragraphs and all other non-empty lines as bullets — AST-1008 coverage proves that path when the prefix is present in `accomplishments`. `craft_resume_base` experience instructions never mention preserving the literal `<no bullet>` marker, so parse drops or normalizes it and the lead becomes an ordinary bullet line. Fix the parse prompt so lead lines keep the prefix.

## UAT fitness

- **AC restored:** Parent AC (quoted on the bug): *“Experience roles, education indent/credentials, and Technical Skills category grid match golden spacing/typography (items 7–9).”* / *“Structure already owned by AST-993 … Experience role articles (compact title/location, optional lead paragraph, bullets) …”* / *“Susan can verify by eye against the desired HTML for every laundry-list item; no judgment call on ‘close enough.’”*
- **Correct outcome:** Under a role with a paste `<no bullet>…` lead, HTML shows `<p class="role-description">…</p>` (prefix stripped at emit) **outside** `<ul>`, then `<ul><li>…` only for genuine achievement bullets. The literal `<no bullet>` string must not appear in HTML.
- **Sibling check:** AST-1008 / AST-993 role layout and `lead_line_prefix` contract unchanged. AST-1020 role CSS spacing unchanged. AST-1027 marker preserve still applies inside lead/bullet text. Verify: no CSS “first-li looks like a paragraph” hacks; `_split_role_accomplishments` / emit logic unchanged unless Stage 1 proves a genuine emit bug.
- **Not sufficient:** Removing a stacktrace / 5xx alone is **not** done — lead must be a non-`<li>` paragraph in source.
- **Wrong fix rejected:** CSS unstyling the first `<li>` while leaving lead text inside `<ul>`; dropping the lead; inventing a new marker syntax beyond existing `<no bullet>`.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `data/admin/agent_task.json` | `craft_resume_base` `cache_prompt`: `### experience` / `accomplishments` — preserve literal `<no bullet>` prefix on lead lines | data/admin (repo JSON → startup apply) |

**Out of scope (do not touch):** `src/core/builder.py` role emit / `_split_role_accomplishments` (already correct when prefix present); AST-1020 role CSS; new marker digraphs; `tests/`, bible (Betty).

## Root cause (plan-time)

In `_split_role_accomplishments`, only lines with `startswith(lead_prefix)` (`<no bullet>`) become `.role-description`; every other non-empty line becomes `<li>`. Parent Original-brief paste uses `<no bullet>Solo practice…` under Somerset Consulting. `### experience` in `craft_resume_base` describes `accomplishments` as “paragraph and/or bullets… organize into the field, do not rewrite” but **never** requires keeping the literal `<no bullet>` token — so the model emits a plain first paragraph/line and emit treats it as a bullet. Repo JSON applies at bootstrap via `apply_repo_admin_json_at_startup` — no new `database.py` migration.

**Git hygiene:** This child’s `origin/sub/…` must stay rooted on current `origin/ftr/ast-1019-take-2-resume-render-format-discrepancies` with only AST-1030 vocabulary commits. Do **not** leave subjects matching `Merge remote-tracking branch` (validate-sub-log / merge-child gate — see AST-1029 hygiene).

## Stage 1: Preserve `<no bullet>` in `craft_resume_base` experience accomplishments

**Done when:** The repo `craft_resume_base` `cache_prompt` `### experience` section requires that when the resume/paste marks a role lead with `<no bullet>`, that exact prefix remains on the corresponding line(s) inside that job’s `accomplishments` string (newline-separated from following bullets); ordinary bullet lines have no such prefix; file is valid JSON; only the `craft_resume_base` entry’s `cache_prompt` string changes for this stage.

1. In `data/admin/agent_task.json`, locate `"task_key": "craft_resume_base"` and edit its `cache_prompt` (surgical text — do not rewrite job-array field list, marker-preserve globals, competencies/tagline rules from siblings).
2. Under **`### experience`**, extend the `accomplishments` field description and/or Rules with this meaning (wording may be tightened; must include these requirements):
   - `accomplishments` is one newline-separated text block for that role.
   - When the paste/resume has a `<no bullet>…` lead line for the role, copy that line into `accomplishments` **including the literal prefix** `<no bullet>` (then the rest of the lead sentence). Do **not** strip, paraphrase away, or replace the marker.
   - Following achievement bullets are additional lines **without** the `<no bullet>` prefix.
   - Do **not** invent a `<no bullet>` lead when the paste has none.
   - The HTML builder turns prefixed lines into `.role-description` and other lines into `<li>` — the marker must survive parse for that split to work.
3. **QUALITY CHECKLIST** — add a bullet: when the paste uses `<no bullet>` on a role lead, that prefix appears unchanged on the corresponding `accomplishments` line(s).
4. Do **not** change `src/core/builder.py` `_split_role_accomplishments` / `_emit_experience_jobs_html` / `lead_line_prefix` config unless Stage 2 finds a genuine emit bug (then **stop** and escalate on AST-1030).
5. Do **not** edit other `task_key` rows.
6. Do **not** edit `tests/` or bible — Betty owns assertions after Code Complete.
   ⚠️ **Decision:** Prompt preserve only (not builder heuristics that treat the first accomplishments line as a lead without the marker, not CSS first-`<li>` restyle). Emit contract is already AST-1008-correct when the prefix is present; inventing “first line is always lead” would mis-classify roles that have only bullets. Startup applies repo JSON — no new migration.

## Stage 2: Builder emit lock + three-surface proof (manual / build verification)

**Done when:** With in-memory experience job array whose Somerset-style `accomplishments` starts with `<no bullet>Solo practice…` then bullet lines, session / base / job-tailored HTML shows `.role-description` for the lead and `<li>` only for bullets; `<no bullet>` absent from HTML. Confirm builder split/emit source unchanged from pre-ticket tip. Spike dumps only under `debug/spikes/AST-1030/` if used — never commit; never repo-root `artifacts/`.

1. During **build-child**, confirm `git diff` does **not** touch `src/core/builder.py` role emit helpers.
2. Exercise session builder with the AST-1008-style Somerset job blob (prefix present) — expect `.role-description` then `<ul><li>…`.
3. Negative check: same lead text **without** `<no bullet>` prefix still becomes first `<li>` — documents that parse preserve is required; do not add first-line heuristics.
4. Note for UAT: after deploy/restart so startup applies repo JSON, re-run Session Resume Paste Parse → Open HTML on the parent fixture; Somerset lead must be a paragraph, not a list item.
5. If Stage 1 prompt text cannot be applied without breaking JSON / `{$RESPONSE_SCHEMA}`, **stop**, comment on **bug** AST-1030 with the Stage blocked template, and wait.

## Self-Assessment

**Scope:** `Single-Component` — `craft_resume_base` `cache_prompt` text in `data/admin/agent_task.json` only; builder role lead/bullet split left intact.

**Conf:** `high` — builder + AST-1008 already implement `<no bullet>` → `.role-description`; prompt never mentions the marker; UAT Actual matches stripped prefix → all `<li>`.

**Risk:** `Medium` — prompt change hits all `craft_resume_base` consumers; model might over-apply `<no bullet>` — mitigated by “only when paste has it” and “do not invent” language.

## Code Rules self-review

- §1.3 DRY: one shared split/emit path remains; prompt stops destroying its lead marker input.
- §1.1 / scope isolation: no CSS; no AST-1020 spacing edits; no new marker syntax.
- §2.1: prompt lives in repo admin JSON (existing AST-782 path); `lead_line_prefix` stays config-driven.
- §3.6: spikes under `debug/spikes/AST-1030/` only if used.
- Engineer test-tree ban: no `tests/` or bible edits.
