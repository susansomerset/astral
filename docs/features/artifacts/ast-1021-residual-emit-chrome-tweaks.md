# Residual emit / chrome tweaks (Take 2: Resume Render Format discrepancies)

**Linear:** [AST-1021](https://linear.app/astralcareermatch/issue/AST-1021/residual-emit-chrome-tweaks-take-2-resume-render-format-discrepancies)
**Parent:** [AST-1019](https://linear.app/astralcareermatch/issue/AST-1019/take-2-resume-render-format-discrepancies) — Take 2: Resume Render Format discrepancies
**Publish ref:** `origin/sub/AST-1019/AST-1021-residual-emit-chrome-tweaks`

Cosmetic document-chrome adjustments the stylesheet sibling cannot fix: document `<title>` must be `{candidate_name} Resume` (single space; no em/en dashes) across the shared builder family; ATS `<meta name="description">` must stay candidate-specific from the AST-993/AST-1010 field-derived template (do **not** force the golden HTML’s example Product Manager / Cloud Platforms meta string); plus only emit-level `white-space` / class leftovers that CSS cannot paint. Does **not** rework AST-993 structural contracts, does **not** own embedded stylesheet golden parity ([AST-1020](https://linear.app/astralcareermatch/issue/AST-1020/embedded-stylesheet-golden-parity-take-2-resume-render-format) — already on `origin/ftr/ast-1019-take-2-resume-render-format-discrepancies`), and does **not** rewrite resume content.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/builder.py` | Fix `_emit_html_document` document `<title>` to `{name} Resume`; leave meta template as field-derived; apply only concrete residual emit chrome fixes found in Stage 3 (if any) | core |

**Out of scope (do not touch):** embedded `<style>` / `BUILD_CONFIG["default_style"]` tokens (AST-1020); header `Name • Title` / contact string join / marker vocabulary (AST-1010 / AST-1007); experience / education / skills / prior **markup** (AST-1008 / AST-1009); cover-letter HTML; external `styles07.css`; Manage Tasks prompts; `tests/`, bible (Betty).

## Current baseline (post–AST-1020 on ftr)

Inspected on epic worktree after `git merge origin/dev` + `git merge origin/ftr/ast-1019-take-2-resume-render-format-discrepancies`:

1. **Document `<title>` (must change):** `_emit_html_document` currently builds
   `html.escape(f"{render.get('candidate_name', '')} — Resume".strip() or "Resume")`
   — em dash between name and `Resume`. Empty name also fails the `or "Resume"` fallback because `"— Resume"` is truthy after strip. Parent / child AC require `{candidate_name} Resume` (space, no dashes), not `SomersetResume` and not `{name} — Resume`.
2. **Meta description (must keep):** When `candidate_name`, `candidate_title`, and `candidate_tagline` are all non-empty, emit already uses
   `Resume of {name}, {title}, specializing in {tagline}`
   with `html.escape` on the full content and omit-on-partial. The literal meta string in the desired HTML is structure-only — **do not** replace this template with that fixed example text.
3. **Stylesheet / structural emit:** Golden CSS + class names for body sections already land via AST-1020 / AST-993 stack. This ticket does not re-open those contracts.

## Stage 1: Document `<title>` → `{name} Resume`

**Done when:** For any render dict passed into `_emit_html_document` (via `build_session_base_resume`, `build_base_resume`, and `build_resume_from_job`), the HTML `<title>` text is `{candidate_name} Resume` when `candidate_name` is non-empty after strip, and exactly `Resume` when name is empty/missing — with no em dash (`—`), en dash (`–`), or hyphenated `SomersetResume`-style concatenation; value is HTML-escaped.

1. In `src/core/builder.py` `_emit_html_document`, replace the current `title_esc = …` line (today: `f"{render.get('candidate_name', '')} — Resume".strip() or "Resume"`) with construction from the already-computed `name_raw` (same strip source used for meta / h1):
   ```python
   title_esc = html.escape(f"{name_raw} Resume" if name_raw else "Resume")
   ```
2. Do **not** invent a last-name-only or camelCase title (no `SomersetResume`).
3. Do **not** put the title suffix / template into `BUILD_CONFIG` for this ticket.
   ⚠️ **Decision:** Keep the title string inline next to the existing meta template (same helper). Parent AC states the exact shape `{candidate_name} Resume`; `BUILD_CONFIG["default_style"]["type_scale"]["document_title"]` is CSS sizing metadata, not the HTML `<title>` text — do not overload it.
4. Do **not** change the `<title>…</title>` placement in the head template (stays after viewport meta, before `{meta_tag}` and `<style>`).
5. Do **not** edit `tests/` or bible — Betty owns assertions after Code Complete.

## Stage 2: Meta description — lock field-derived template (no golden-literal force)

**Done when:** Meta emit still matches the AST-1010 / parent laundry-list item 2 contract: content `Resume of {name}, {title}, specializing in {tagline}` only when all three of `name_raw` / `title_raw` / `tagline_raw` are non-empty; otherwise no `<meta name="description">`; values come from the paste/render fields (marker-applied strings already in `render`); the golden HTML’s example meta string about Product Manager / Cloud Platforms is **never** hardcoded.

1. In `src/core/builder.py` `_emit_html_document`, **read** the existing `meta_tag` block (the `if name_raw and title_raw and tagline_raw:` path). Confirm it still builds exactly:
   ```python
   meta_esc = html.escape(
       f"Resume of {name_raw}, {title_raw}, specializing in {tagline_raw}"
   )
   meta_tag = f'\n  <meta name="description" content="{meta_esc}" />'
   ```
2. **Do not change** that template, the omit-when-partial rule, escape order, or meta tag placement relative to `<title>` / `<style>`, unless Stage 1’s edit accidentally disturbed them — if disturbed, restore Stage 2 behavior to the contract above.
3. **Do not** assign the golden fixture’s literal `content="Resume of Susan Somerset, Senior Technical Product Manager / Program Manager specializing in Cloud Platforms, Agile Delivery, SaaS, and Healthcare."` (or any fixed paste-independent string) as the emit output.
   ⚠️ **Decision:** Meta work on this ticket is a **lock / no-force** pass, not a rewrite. AST-1010 already shipped the correct field-derived template; child AC 8 exists to prevent Take 2 from “matching” the desired HTML by hardcoding its example meta. If the inspected baseline already matches step 1, Stage 2 produces **no code diff** beyond Stage 1’s title line (still verify during build).

## Stage 3: Residual white-space / class emit leftovers (CSS cannot fix)

**Done when:** Against the shared `_emit_html_document` head + header chrome (and only emit attributes CSS cannot supply), either (a) no residual gaps remain beyond Stage 1 title, documented by the verification in Stage 4, or (b) any concrete leftover listed below is fixed in `builder.py` only. No AST-993 structural contract rework.

1. During **build-child**, after Stage 1–2, re-read the HTML template and header emit inside `_emit_html_document` (the `<header class="header">` / `<h1>` / `<div class="contact"><span>…</span></div>` block only — not section body emitters owned by AST-1008/1009).
2. Compare that chrome to parent laundry-list **document chrome** items 1–2 and child AC 7–10. Treat as **in-scope residual** only when **all** of the following are true:
   - It is emit markup / attribute / class-name on an element this helper already owns (document title, meta, h1 join already shipped, single contact span wrapper).
   - Golden CSS from AST-1020 cannot produce the desired look without the markup change.
   - Fixing it does **not** change experience / education / skills / prior section structure, marker vocabulary, or stylesheet rules.
3. **Pre-declared residual inventory from planning (authoritative):**
   | Gap | Disposition |
   |-----|-------------|
   | `<title>` `{name} — Resume` / empty-name `— Resume` | **Fix in Stage 1** |
   | Meta forced to golden example string | **Forbidden — Stage 2 lock** |
   | Contact multi-span vs single `<span>` | **No change** — desired HTML uses one contact `<span>`; AST-1020 CSS already has `.contact span { white-space: nowrap }` for that shape |
   | Meta tag order after `</style>` in desired HTML | **No change** — not in child AC; AST-1010 placement after `<title>` remains |
   | Body section class / role / education / skills markup | **Out of scope** — AST-993 / AST-1008 / AST-1009 / AST-1020 |
4. If build discovers a **new** residual that meets step 2 but is **not** in the table above, **stop**, comment on **parent** AST-1019 with the Stage blocked template (propose the markup delta), and wait — do not invent scope.
5. If the table’s dispositions cover everything found, Stage 3 adds **no further edits**.

## Stage 4: Three-surface chrome verification (manual / build verification)

**Done when:** With in-memory content that supplies non-empty `candidate_name`, `candidate_title`, `candidate_tagline`, and `candidate_contact_detail`, each of `build_session_base_resume`, `build_base_resume`, and `build_resume_from_job` produces HTML whose `<title>` is `{candidate_name} Resume` (space, no dash characters between name and Resume), whose `<meta name="description">` matches `Resume of {name}, {title}, specializing in {tagline}` from those fields (not the golden example Product Manager / Cloud Platforms string when title/tagline differ), and whose header/contact chrome class names match the existing shared builder (`header` / single contact `span`). Repeat once with empty `candidate_name` → `<title>Resume</title>`. Spike dumps only under `debug/spikes/AST-1021/` if used — never commit; never repo-root `artifacts/`.

1. During **build-child**, exercise the three public builders (REPL or ad-hoc under `debug/spikes/AST-1021/`).
2. String-check `<title>…</title>` and meta content on all three surfaces; confirm no `—` / `–` between name and `Resume` in the title.
3. Confirm one surface with a **non-golden** title/tagline still emits field-derived meta (proves AC 8).
4. If Stage 1–3 assumptions fail against current helpers, **stop**, comment on **parent** AST-1019 with the Stage blocked template, and wait — do not improvise.

## Self-Assessment

**Scope:** `minor` — one document-title construction line in `src/core/builder.py` `_emit_html_document`, plus an explicit meta lock / residual no-op inventory; no config or UI layer changes.

**Conf:** `high` — title bug and required shape are visible in current source; meta template already matches AST-1010 / parent AC; stylesheet sibling landed on ftr; residual table is closed at plan time.

**Risk:** `low` — wrong title string is cosmetic browser-tab / PDF chrome only; meta lock prevents regressing ATS description; body structure and stylesheet stay untouched.

## Code Rules self-review

- §1.3 DRY: title and meta remain the single path inside `_emit_html_document`; all three public resume builders already share it — no second document template.
- §1.1 / scope isolation: no stylesheet rewrite; no AST-993 structural emit changes; no cover letter; no Manage Tasks prompts.
- §1.4 / §2.1: no new magic sets; title shape stays a literal AC string (Decision); do not overload `type_scale.document_title` CSS metadata.
- §2.4 / §2.6: N/A.
- §3.3: core only; no new imports.
- §3.5 naming: unchanged field keys (`candidate_name` / `candidate_title` / `candidate_tagline`).
- §3.6: spikes under `debug/spikes/AST-1021/` only if used; never commit; never repo-root `artifacts/`.
- Engineer test-tree ban: no `tests/` or bible edits — Betty owns assertions after Code Complete.
- Sibling scope: AST-1020 owns CSS; this ticket owns title + meta lock + residual emit chrome only.

## Review (build stub)

**Publish ref:** `origin/sub/AST-1019/AST-1021-residual-emit-chrome-tweaks`
**Plan path:** `docs/features/artifacts/ast-1021-residual-emit-chrome-tweaks.md`

| Stage | Commit | Summary |
|-------|--------|---------|
| 1 | `712bd324` | Document `<title>` → `{name} Resume` (empty → `Resume`) |
| 2–3 | — | Meta lock verified unchanged; residual inventory no further edits |
| 4 | — | Three-surface session/base/job + empty-name title checks (build verify) |

**Tip:** `712bd324` on `origin/sub/AST-1019/AST-1021-residual-emit-chrome-tweaks`

## Review (Radia — code-rubric.v1)

[code-rubric] revision=1
**Rubric:** code-rubric.v1
**Ticket:** AST-1021
**Publish ref tip (pre-docs):** `517faa964e4b670dd3f5332ef029b4ab0e6b610a`
**Overall:** DISCUSS

### What’s solid

- Stage 1: `<title>` is `{name_raw} Resume` / empty → `Resume`; em-dash + broken empty-name fallback gone.
- Stage 2–3: meta field-derived template unchanged (lock); residual inventory no further edits.
- Engineer footprint is the one title line in `_emit_html_document`; Betty owns tests via one `merge-tests(AST-1021)`.

### Issues / findings

**discuss (straggler):** Joan excluded several statutes against plan Files Changed; three-dot diff vs `origin/dev` brings in plan/docs/test/config history (incl. AST-1020). Each scores **conforms** — no product fix.

### Recommended actions

- Engineer: acknowledge stragglers (no code change). resolve-child → User Testing when clear.

## Resolution

**Date:** 2026-07-29  
**Outcome:** clean — no product code changes.

Acknowledged Radia’s **discuss (straggler)** items (Joan-excluded statutes brought in-scope by three-dot diff vs `origin/dev`, including AST-1020 history). Each **conforms** in substance. No **fix-now** items. Publish tip after resolve remains product + Betty + Radia stack on `origin/sub/AST-1019/AST-1021-residual-emit-chrome-tweaks`.
