<!-- linear-archive: AST-555 archived 2026-06-15 -->

## Linear archive (AST-555)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-555/agent-ad-hoc-navigation-rename-improve-quality-of-debug-logging  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** katherine  
**Priority / estimate:** None / —  
**Parent:** AST-538 — Improve Quality of Debug Logging  
**Blocked by / blocks / related:** parent: AST-538

### Description

## What this implements

Rename NAV_CONFIG sidebar Anthropic Ad Hoc → Agent Ad Hoc.

## Acceptance criteria

5 from parent.

## Boundaries

No debug helper work.

## Git branch (authoritative)

Per orientation-astral: parent `ftr/ast-538-improve-quality-of-debug-logging`, child `sub/AST-538/<child-id>-<slug>`.

### Comments

#### betty — 2026-06-03T03:05:05.993Z
**Rollup bible reconcile (Betty)** — publish ref updated for `rollup-child` FF into `origin/ftr/ast-538-improve-quality-of-debug-logging`.

- Merged ftr §7.13zs (**AST-554**) unchanged; §7.13zt (**AST-555** nav rename) immediately after (no duplicate §7.13zs heading).
- **`origin/sub/AST-538/AST-555-agent-ad-hoc-nav-rename` @ `ba9b693c`**
- **`docs/ASTRAL_TEST_BIBLE.md` shasum:** `cc04f52acd559e0ae2e47d4d3f074108d5eb23a6780c75bbe884d16682283adf`
- Verified: `git merge origin/sub/…` into ftr tip is **fast-forward** on bible.
- Manifest / product unchanged. Status remains **User Testing**.

— Betty

#### betty — 2026-06-03T03:01:02.535Z
**Bible republish (rollup-child reconcile)**

`origin/sub/AST-538/AST-555-agent-ad-hoc-nav-rename` @ **`d5f54931`** — **`docs/ASTRAL_TEST_BIBLE.md`** shasum **`35280f8a71d371e227f0a0b4a191929fd57f99c6`**

**Layout (matches `origin/ftr/ast-538-improve-quality-of-debug-logging` after AST-554 rollup):**
- **§7.13zs** — **AST-554** (blocker; already on ftr)
- **§7.13zt** — **AST-555** (this ticket; was wrongly **§7.13zs** on sub → rollup conflict)

**Manifest** (unchanged — Katherine already green @ User Testing):

1. `./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_nav_config_admin_agent_ad_hoc_label`
2. `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx`

@Chuckles — **`rollup-child AST-555`** can retry; bible merge into **`origin/ftr/ast-538-improve-quality-of-debug-logging`** should fast-forward.

— Betty

#### radia — 2026-06-03T00:37:29.112Z
**Review** (`origin/dev...origin/sub/AST-538/AST-555-agent-ad-hoc-nav-rename`)

**fix-now:** none

**discuss:** none

**advisory:**
- `NAV_CONFIG` Admin item + `AdminAnthropicAdHoc` `<h1>` → **Agent Ad Hoc**; path `/admin/anthropic_ad_hoc` unchanged — matches plan and parent AST-538 AC #5.
- `test_nav_config_admin_agent_ad_hoc_label` + Vitest page tests lock the rename; no scope bleed into AST-554/557 debug work.
- Self-assessment (`scope-minor`, `conf-high`, `risk-low`) matches the diff footprint.

**Doc:** [ast-555 plan + Radia review](https://github.com/susansomerset/astral/blob/sub/AST-538/AST-555-agent-ad-hoc-nav-rename/docs/features/foundation/ast-555-agent-ad-hoc-navigation-rename-improve-quality-of-debug-logging.md) @ `216c9865`

#### betty — 2026-06-03T00:23:50.527Z
**Manifest**

1. `./scripts/testing/run_component_tests.sh tests/component/ui/api/test_api_system.py::TestSystemAuthRoutes::test_nav_config_admin_agent_ad_hoc_label`
2. `cd src/ui/frontend && npm run test:component -- ../../../tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx`

**Coverage:** Plan step 3 (Vitest `"Agent Ad Hoc"` assertions) + **`GET /api/nav_config`** Admin label at **`/admin/anthropic_ad_hoc`**. See **`docs/ASTRAL_TEST_BIBLE.md` §7.13zs**.

**Publish:** `origin/sub/AST-538/AST-555-agent-ad-hoc-nav-rename` @ **`2007f266`** (tests **`317ad9e9`**, bible **`2007f266`**).

**Bible shasum on publish ref:** `e79be1f0e11dd511bc0ef71fb0129107416aa2ea`

#### katherine — 2026-06-02T22:31:13.626Z
Plan: `docs/features/foundation/ast-555-agent-ad-hoc-navigation-rename-improve-quality-of-debug-logging.md`

https://github.com/susansomerset/astral/blob/sub/AST-538/AST-555-agent-ad-hoc-nav-rename/docs/features/foundation/ast-555-agent-ad-hoc-navigation-rename-improve-quality-of-debug-logging.md

Published: `origin/sub/AST-538/AST-555-agent-ad-hoc-nav-rename` @ `78fa6424`

**Self-Assessment**
- **Scope:** `minor` — Three files with label/title string updates only; no routing or API changes.
- **Conf:** `high` — Exact edit sites identified; matches established NAV_CONFIG rename pattern.
- **Risk:** `low` — Cosmetic labels only; no runtime pipeline or data-layer impact.

Parent AC #5 (sidebar **Agent Ad Hoc**); route `/admin/anthropic_ad_hoc` unchanged per AST-538.

---

# Agent Ad Hoc navigation rename (Improve Quality of Debug Logging)

**Linear:** [AST-555](https://linear.app/astralcareermatch/issue/AST-555/agent-ad-hoc-navigation-rename-improve-quality-of-debug-logging)

**Parent:** [AST-538 — Improve Quality of Debug Logging](https://linear.app/astralcareermatch/issue/AST-538/improve-quality-of-debug-logging)

**Feature ref:** Parent integration `ftr/ast-538-improve-quality-of-debug-logging` (origin). **Publish ref:** `sub/AST-538/AST-555-agent-ad-hoc-nav-rename` (origin only — orientation-astral branch law).

**Summary**

Rename user-visible **Anthropic Ad Hoc** labels to **Agent Ad Hoc** in sidebar navigation and on the admin workbench page, satisfying parent acceptance criterion #5. Route path, component filename, and API paths stay unchanged unless Susan requests a URL rename later.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `NAV_CONFIG` Admin item: `"Anthropic Ad Hoc"` → `"Agent Ad Hoc"` (path unchanged: `/admin/anthropic_ad_hoc`) | utils |
| `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx` | Page `<h1>` text: `"Agent Ad Hoc"` | ui |
| `tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx` | Both `getByText` assertions: `"Agent Ad Hoc"` | tests |

**Explicitly out of scope (do not touch):**

- `src/utils/logging.py`, debug helpers, `ASTRAL_CODE_RULES.md` debug section (**AST-554**).
- Dispatcher / roster / consult debug instrumentation (**AST-557** and other backfill children).
- `review-astral` skill (**AST-556**).
- `routes.tsx` path `admin/anthropic_ad_hoc`, component name `AdminAnthropicAdHoc`, API `/api/admin/adhoc/*`.
- Docs under `docs/features/` except this plan file.

---

## Stage 1: Navigation and page title rename

**Done when:** `GET /api/nav_config` (with auth + candidate context as today) includes an Admin item labeled **Agent Ad Hoc** at `/admin/anthropic_ad_hoc`; opening that route shows page heading **Agent Ad Hoc**; `npm run test` (or Betty manifest subset) passes `test_AdminAnthropicAdHoc.test.tsx`.

1. In `src/utils/config.py`, locate the Admin group in `NAV_CONFIG` (approx. line 1963). Change only the `label` on the item with `"path": "/admin/anthropic_ad_hoc"` from `"Anthropic Ad Hoc"` to `"Agent Ad Hoc"`. Do **not** change `path`, group order, or `enabled`/`visible` gates.

2. In `src/ui/frontend/src/pages/AdminAnthropicAdHoc.tsx`, change the `<h1>` inner text from `Anthropic Ad Hoc` to `Agent Ad Hoc`. Do **not** rename the file, default export, or any API payload fields.

3. In `tests/component/frontend/pages/test_AdminAnthropicAdHoc.test.tsx`, replace both occurrences of `screen.getByText("Anthropic Ad Hoc")` with `screen.getByText("Agent Ad Hoc")` (lines ~52 and ~74). No other assertion changes.

4. **Manual check (Susan UAT note for build comment):** With app running and a candidate selected, confirm Admin sidebar shows **Agent Ad Hoc** and the page title matches. Route URL remains `/admin/anthropic_ad_hoc`.

⚠️ **Decision:** Page `<h1>` is updated even though the ticket Description names only `NAV_CONFIG`, so the opened page matches the sidebar label (parent AC #5: “Sidebar shows **Agent Ad Hoc**”; users who click the nav item also see consistent branding). URL and module names stay `anthropic_ad_hoc` per parent boundary (“route path may stay … unless Susan wants a URL change”).

---

## Self-Assessment

**Scope:** `minor` — Three files, string label changes only; no new routes or APIs.

**Conf:** `high` — Exact strings and locations are known; mirrors prior nav rename plans (e.g. AST-457).

**Risk:** `low` — Mislabel would be cosmetic only; no dispatch, data, or auth behavior changes.

---

## Rules review (ASTRAL_CODE_RULES)

| Rule | Assessment |
|------|------------|
| §1.3 DRY | No duplicate nav definitions; single `NAV_CONFIG` source. |
| §2.1 config | Label change only in `NAV_CONFIG`; no new config blocks. |
| §3.3 imports | No import changes. |
| §3.5 naming | Page stays in flat `pages/`; component file name unchanged (historical `Anthropic` prefix). |
| §2.4 / §2.6 | Not applicable. |

No conflicts requiring `conf-!!-NONE`.

---

## Radia review (review-astral)

**Diff:** `origin/dev...origin/sub/AST-538/AST-555-agent-ad-hoc-nav-rename` · product `b73c986f` · tests `317ad9e9` · bible `2007f266`

### What's solid

- Plan fidelity: `NAV_CONFIG` Admin label, `AdminAnthropicAdHoc` `<h1>`, and Vitest assertions all rename to **Agent Ad Hoc**; `/admin/anthropic_ad_hoc` path and module names unchanged per AST-538 boundary.
- **§2.1** single source: sidebar label comes only from `NAV_CONFIG`; page title matches nav for UAT consistency (documented plan decision).
- Scope hygiene: no `logging.py`, debug backfill, `ASTRAL_CODE_RULES`, or `review-astral` skill edits on this branch.
- Betty manifest: `test_nav_config_admin_agent_ad_hoc_label` locks API payload; bible §7.13zu documents narrowed run.

### Issues

| Severity | Location | Finding |
| --- | --- | --- |
| — | — | None (fix-now / discuss). |

### Recommended actions

| Action | Owner | Notes |
| --- | --- | --- |
| **resolve-astral** | Katherine | No code changes required; optional doc cherry-pick of this review section if useful on `dev-kath`. |
| **UAT** | Susan | Confirm Admin sidebar + page title **Agent Ad Hoc**; URL still `/admin/anthropic_ad_hoc`. |

---

## Resolution (resolve-astral)

**Date:** 2026-06-03 · **Engineer:** Katherine · **Review:** Radia @ `216c9865` on `origin/sub/AST-538/AST-555-agent-ad-hoc-nav-rename`

- **fix-now / discuss:** None — product at `b73c986f`, tests `317ad9e9`, bible `2007f266` already match plan and parent AST-538 AC #5.
- **Changes landed:** Radia review section cherry-picked via merge of publish ref; this Resolution section only (no additional product or test-tree edits).
- **§9a:** Publish ref merges cleanly into `origin/dev` and `origin/ftr/ast-538-improve-quality-of-debug-logging`.
- **Next:** **User Testing** — Susan UAT on sidebar label + page `<h1>`; route `/admin/anthropic_ad_hoc` unchanged.
