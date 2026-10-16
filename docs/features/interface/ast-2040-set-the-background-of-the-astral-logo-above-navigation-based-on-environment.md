# AST-2040 — Set the background of the Astral Logo above navigation based on environment

<!-- linear-archive: AST-2040 archived 2026-10-16 -->

## Linear archive (AST-2040)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2040/set-the-background-of-the-astral-logo-above-navigation-based-on  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Execution plan

1. **Config** — `src/utils/config.py` `ASTRAL_CONFIG`: add `"logo_background_by_deploy_env": {"staging": "#a651f1", "local": "#ed22bb"}` with a short comment. Keys are lowercase `ASTRAL_DEPLOY_ENV` values; **production is intentionally absent** → current color (no override). Add an import-time assert that every value is a `#rrggbb` hex string.
2. **Resolver** — `src/utils/deploy_status.py`: add `logo_background() -> str | None` that reads the existing `ASTRAL_DEPLOY_ENV` (same strip + case-insensitive match as `is_local_deploy_env`) and returns the config color, or `None` for production / unset / any unmapped env.
3. **API** — `src/ui/api/api_system.py` `/api/ui_config` (already `@require_auth`, already the SPA config bag): add `"logo_background": logo_background()` to the payload. No new endpoint; `/api/nav_config` stays a bare list (JobsHomeRedirect also reads it), `/api/deploy_status` is admin-only so non-admins would miss the color.
4. **Frontend** — `src/ui/frontend/src/components/NavigationShell.tsx`: fetch `/api/ui_config` once after auth resolves; when `logo_background` is a non-empty string, set `style={{ backgroundColor }}` on the `.sidebar-logo` div only. `null` → no inline style → today's look. Fetch failure → silent fallback to today's look (no error banner for chrome).
5. **Tests** — component tests: `deploy_status.logo_background` (staging / local / production / unset / case-insensitive), `/api/ui_config` carries `logo_background`, and `test_NavigationShell.test.tsx` asserts the inline background lands on `.sidebar-logo` (and not on the `nav` / shell) when set, absent when `null`. Update `docs/test-bible` entries for those files.
6. **Ship** — compile + lint (`ruff`, `tsc`, `eslint`, frontend build), run the touched component tests, commit on `dev`, push.

## Done when

* `ASTRAL_DEPLOY_ENV=staging` → the logo block background is `#a651f1`; `local` → `#ed22bb`; `production` (or unset / unknown) → unchanged from today.
* Only the `.sidebar-logo` container changes — nav menu, sidebar, and page backgrounds untouched (desktop and drawer).
* Colors live in `ASTRAL_CONFIG` in `config.py`; env read reuses `ASTRAL_DEPLOY_ENV`; no new env var.
* Touched tests green; compile + lint clean.

## Risks / open questions

* none

---

## Original brief

Production: current color

Staging: a651f1

Local: ed22bb

Only the background for the logo, not the entire nav menu or screen.  Reuse the env variable that indicates the environment, and store these color settings in ASTRAL_CONFIG in [config.py](<http://config.py>)

### Comments

#### chuckles — 2026-10-08T17:20:14.889Z
@susan Shipped to `dev` in `b8f45f7a1`. The sidebar logo block is `#a651f1` on staging and `#ed22bb` locally. Production, or an unset/unknown `ASTRAL_DEPLOY_ENV`, keeps today's color. The colors live in `ASTRAL_CONFIG["logo_background_by_deploy_env"]` and reach the frontend through `/api/ui_config`. Build and lint are clean, with no new eslint or ruff findings.

The engineer pre-commit hook blocks `tests/` and `docs/test-bible/` here, so the test and bible changes aren't on `dev`. They're parked at `~/patches/AST-2040-tests-and-bible.patch` and apply cleanly with `git apply --check`. That's 3 `NavigationShell` cases, 9 `deploy_status.logo_background` cases, and 3 `/api/ui_config` cases, all green locally. Betty, or a nod from you, needs to land them.

To verify: open staging and check that only the logo block above the nav turns purple.

---

_Implementation detail may live in git history on `origin/dev`._
