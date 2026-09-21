# AST-1512 — Suppress gmail discovery_cache log noise (file_cache is only supported with oauth2client<4.0.0)

<!-- linear-archive: AST-1512 archived 2026-09-09 -->

## Linear archive (AST-1512)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1512/suppress-gmail-discovery-cache-log-noise-file-cache-is-only-supported  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** katherine  
**Priority / estimate:** None / 2  
**Parent:** AST-1509 — file_cache is only supported with oauth2client<4.0.0  
**Blocked by / blocks / related:** parent: AST-1509

### Description

## What this implements

Suppress the `googleapiclient.discovery_cache` `file_cache is only supported with oauth2client<4.0.0` log line emitted when building the Gmail API client on Railway staging deploy, without changing Gmail I/O behavior.

## Scope

## Component scope

- [X] `src/external/gmail.py` — modified: `_build_service()` must stop triggering discovery file-cache initialization that logs the oauth2client warning; this is the only Gmail API client builder in-repo.

## Technical scope

- [X] `src/external/gmail.py` — modified function `_build_service()`: add `cache_discovery=False` to the existing `build("gmail", "v1", credentials=...)` call so googleapiclient skips file-based discovery caching (incompatible with current auth stack).
- [X] Module-level logger level adjustment for `googleapiclient.discovery_cache` following the existing external-client quieting pattern in `src/external/anthropic.py`.

## Git branch (authoritative)

Per orientation § Branch law: parent `ftr/AST-1509-suppress-gmail-discovery-cache-log-noise`, child `sub/AST-1509/<child-segment>`.

### Comments

#### radia — 2026-08-26T23:47:28.301Z
[code-rubric] PROCEED (Commit: d2a68e99) Gmail discovery_cache log suppressed

#### betty — 2026-08-26T23:43:08.860Z
[bug-repro]
origin/sub/AST-1509/AST-1512-suppress-gmail-discovery-cache-log-noise @ a94d6447 · repro lands red, awaits fix

#### joan — 2026-08-26T23:41:47.899Z
[board-joan] CANON: OK — third-party logger quieting matches existing `anthropic.py` external-layer precedent; no statute/pattern update required.

#### betty — 2026-08-26T23:32:05.122Z
[board-betty] TESTS: REVISE
What: docs/test-bible/external/gmail.md — no cache_discovery=False pin — _build_service build kwargs

#### chuckles — 2026-08-26T23:31:04.789Z
origin/sub/AST-1509/AST-1512-suppress-gmail-discovery-cache-log-noise @ a33160e1893316705792b9537cd33d2b4e284d7f · Gmail cache log plan

---

_Implementation detail may live in git history on `origin/dev`._
