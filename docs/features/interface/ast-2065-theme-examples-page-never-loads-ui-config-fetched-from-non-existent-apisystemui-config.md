# AST-2065 — Theme Examples page never loads (UI config fetched from non-existent /api/system/ui_config)

<!-- linear-archive: AST-2065 archived 2026-10-16 -->

## Linear archive (AST-2065)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2065/theme-examples-page-never-loads-ui-config-fetched-from-non-existent  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** ada  
**Priority / estimate:** None / 1  
**Parent:** AST-2042 — User Theme  
**Blocked by / blocks / related:** parent: AST-2042

### Description

## Susan's report

\[fix\]

The Theme Examples page is not loading and not emitting console errors.

## As-is

Tools → Theme Examples stays on "Loading..." with no console error. `src/ui/frontend/src/lib/uiConfig.ts` `loadUiConfig` fetches `/api/system/ui_config`, but `system_bp` is `url_prefix="/api"`, so only `/api/ui_config` exists. The SPA fallback returns HTML, so `themes` is never present. The page test mocks the same wrong URL, which is why it passed.

## To-be

`loadUiConfig` fetches `/api/ui_config`, Theme Examples renders its four palette panels, and the page test mocks the real URL so it would have caught this. (`ArtifactEditor.tsx` and `ArtifactsBaseResumeContent.tsx` call the same wrong path, and that bug predates this epic. In scope only if `plan-fix` judges it the same one-line fix.)

## Suggested engineer

Ada Lovelace — owner of [AST-2047](https://linear.app/astralcareermatch/issue/AST-2047) (theme registry, `App.css` palettes, Theme Examples page, `uiConfig.ts`).

### Comments

#### chuckles — 2026-10-08T23:17:35.936Z
Radia fix-now (`data/admin/agent*.json`) overridden: both files at the sub tip are identical to `origin/dev` — they came in through the required `sync(dev)` merge, since ftr is 2 commits behind dev. Merging into ftr just catches it up to dev; the ftr→dev PR shows no change. Product delta is the 3 URL swaps only. → User Testing.

#### radia — 2026-10-08T23:17:34.580Z
[code-rubric] REVIEW (Commit: 081e70f34) Drop data/admin from sub tip

#### betty — 2026-10-08T23:08:00.543Z
[bug-repro]
`origin/sub/AST-2042/AST-2065-ui-config-url` @ `788d48fdf` · repro lands red, awaits fix

#### joan — 2026-10-08T22:56:52.029Z
[board-joan]  CANON: OK

#### betty — 2026-10-08T22:56:35.529Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/{components,pages}.md — broken tests + missing coverage — 12 files mock only `/api/system/ui_config` and stop matching once the URL is fixed (components: test_ArtifactEditor, test_ContextTextPage, test_JobTitleText, test_ListPage, test_ListPage_listTableLayout, test_ListPage_ui_config_fail; pages: page-mocks.ts, test_AdminThemeExamples, test_ArtifactsBaseResumeContent, test_CompaniesWatchHistory, test_CompaniesWatchList, test_JobsJobDetail) — retarget to `/api/ui_config`; and no test pins the real path (every mock reused the wrong URL, which is how this survived since AST-647) — add a repro guard that `loadUiConfig` requests `/api/ui_config` and no frontend source references `/api/system/ui_config`.

#### ada — 2026-10-08T22:55:49.803Z
`origin/sub/AST-2042/AST-2065-ui-config-url` @ `68d6a6463` · fetch /api/ui_config, three callers

---

_Implementation detail may live in git history on `origin/dev`._
