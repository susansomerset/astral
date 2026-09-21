# AST-1509 — file_cache is only supported with oauth2client<4.0.0

<!-- linear-archive: AST-1509 archived 2026-09-09 -->

## Linear archive (AST-1509)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1509/file-cache-is-only-supported-with-oauth2client400  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Low / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Error found in railway staging deploy logs.

## As-is

Railway staging deploy logs show `file_cache is only supported with oauth2client<4.0.0` (from `googleapiclient.discovery_cache`) whenever the app builds the Gmail API client — e.g. on boot when dispatch tasks touch inbox/Gmail. The line adds noise to deploy logs and can appear at error severity in Railway's log UI even though it is informational third-party chatter, not an Astral failure.

## To-be

Staging deploy logs should not emit the oauth2client `file_cache` discovery-cache message when Gmail clients are built; Gmail I/O behavior stays unchanged.

## Proposed steps

1. In `src/external/gmail.py`, pass `cache_discovery=False` to `googleapiclient.discovery.build()` inside `_build_service()` — the standard fix when using `google-auth` instead of legacy `oauth2client`.
2. Optionally mirror the `anthropic.py` / `deepseek.py` pattern: set `googleapiclient.discovery_cache` logger to WARNING at module import as belt-and-suspenders if any sibling loggers still leak.
3. Redeploy staging and confirm the message is gone from Railway deploy logs on boot and on a Gmail-touching dispatch run.

## Component scope

* `src/external/gmail.py` — modified: `_build_service()` must stop triggering discovery file-cache initialization that logs the oauth2client warning; this is the only Gmail API client builder in-repo.

## Technical scope

* `src/external/gmail.py` — modified function `_build_service()`: add `cache_discovery=False` to the existing `build("gmail", "v1", credentials=...)` call so googleapiclient skips file-based discovery caching (incompatible with current auth stack). Optionally add module-level logger level adjustment for `googleapiclient.discovery_cache` following the existing external-client quieting pattern in `src/external/anthropic.py`.

## Ancestor candidates

- [ ] AST-1093 — Gnarly looking deploy logs on railway (archived; parent Boundaries explicitly excluded oauth2client `file_cache` noise — closest thematic ancestor if reviving deploy-log hygiene under that lineage)
- [ ] AST-1128 — gaze-email candidate-bound dispatch redesign (meteorite; gaze_email runs trigger Gmail client build and produce this log line in UAT notes)
- [ ] no ancestor candidate found (fresh orphaned mini-epic — deploy-log third-party noise only)

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
