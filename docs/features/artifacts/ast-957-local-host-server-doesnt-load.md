# AST-957 — Local host server doesn't load

<!-- linear-archive: AST-957 archived 2026-08-02 -->

## Linear archive (AST-957)

**Archived:** 2026-08-02  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-957/local-host-server-doesnt-load  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Local Flask will not boot because `bootstrap` still inventories `DISPATCH_SCHEDULABLE_TASK_KEYS` and requires each of those keys to resolve via `dispatch_task_admin_defaults` → `TASK_CONFIG`. [AST-856](https://linear.app/astralcareermatch/issue/AST-856/check-cover-letter-not-recognized-as-a-valid-task-key) / [AST-955](https://linear.app/astralcareermatch/issue/AST-955/align-scheduled-actions-save-with-task-key-picker-check-cover-letter) removed that frozenset as the **Save** membership gate and made `TASK_CONFIG` the Save/SoT rule — but the written [AST-955](https://linear.app/astralcareermatch/issue/AST-955/align-scheduled-actions-save-with-task-key-picker-check-cover-letter) decision **left the frozenset intact for bootstrap / form enrichment**. That leftover parallel list is why `fetch_jd` (present on the frozenset, absent from `TASK_CONFIG`) still kills local start. This epic finishes the SoT cleanup: bootstrap must not depend on a second curated allowlist.

## Functional scope

* Stop bootstrap runtime coupling from requiring membership in / successful defaults for every key in `DISPATCH_SCHEDULABLE_TASK_KEYS`.
* Local Flask starts cleanly without adding gazer/roster keys to `TASK_CONFIG` solely to appease that leftover inventory loop.
* Retire or narrow remaining uses of `DISPATCH_SCHEDULABLE_TASK_KEYS` that reintroduce a second membership rule (bootstrap inventory; admin form enrichment only if it still treats the frozenset as a required catalog). Prefer `TASK_CONFIG` (and existing per-key helpers / request trigger) as the single membership rule — consistent with [AST-856](https://linear.app/astralcareermatch/issue/AST-856/check-cover-letter-not-recognized-as-a-valid-task-key).
* Preserve [AST-856](https://linear.app/astralcareermatch/issue/AST-856/check-cover-letter-not-recognized-as-a-valid-task-key) Save behavior: any registered catalog key (e.g. `check_cover_letter`) still saves when outside any former “schedulable” set.

## Boundaries

* Does **not** reverse [AST-856](https://linear.app/astralcareermatch/issue/AST-856/check-cover-letter-not-recognized-as-a-valid-task-key) / [AST-955](https://linear.app/astralcareermatch/issue/AST-955/align-scheduled-actions-save-with-task-key-picker-check-cover-letter) Save acceptance for registered catalog keys.
* Does **not** change gazer/roster/inflow **runtime** fetch behavior or retire/rename task keys.
* Does **not** mean “stuff `fetch_jd` into `TASK_CONFIG` so the old frozenset stays happy” — that was the wrong direction.
* Does **not** redesign Scheduled Actions UI beyond what removing the parallel inventory requires.
* Config remains source of truth (Code Rules §2.1).

## Acceptance criteria

1. Clean local Flask launch stays up — no bootstrap error about a schedulable key missing from `TASK_CONFIG`.
2. Bootstrap no longer fails because a key is in `DISPATCH_SCHEDULABLE_TASK_KEYS` but not in `TASK_CONFIG`.
3. Scheduled Actions Save for `check_cover_letter` ([AST-856](https://linear.app/astralcareermatch/issue/AST-856/check-cover-letter-not-recognized-as-a-valid-task-key)) still succeeds.
4. Automated coverage: boot/coupling green without requiring the gap keys (`fetch_jd`, etc.) to be forced into `TASK_CONFIG` for bootstrap’s sake; [AST-856](https://linear.app/astralcareermatch/issue/AST-856/check-cover-letter-not-recognized-as-a-valid-task-key) Save regression remains.

## Dependencies and blockers

* [AST-856](https://linear.app/astralcareermatch/issue/AST-856/check-cover-letter-not-recognized-as-a-valid-task-key) / [AST-955](https://linear.app/astralcareermatch/issue/AST-955/align-scheduled-actions-save-with-task-key-picker-check-cover-letter) (User Testing): Save gate removed; frozenset **intentionally** kept for bootstrap/form enrichment in the [AST-955](https://linear.app/astralcareermatch/issue/AST-955/align-scheduled-actions-save-with-task-key-picker-check-cover-letter) plan — this epic owns finishing or reversing that leftover.
* none otherwise.

## Open questions

none.

## Schedulable list status (answer to Susan)

* [AST-856](https://linear.app/astralcareermatch/issue/AST-856/check-cover-letter-not-recognized-as-a-valid-task-key) removed using `DISPATCH_SCHEDULABLE_TASK_KEYS` as the **Save** allowlist — it did **not** delete the frozenset from config.
* [AST-955](https://linear.app/astralcareermatch/issue/AST-955/align-scheduled-actions-save-with-task-key-picker-check-cover-letter) plan Decision (explicit): leave the frozenset for **bootstrap inventory** and form enrichment; only stop using it as Save membership.
* So: not fully removed; **kept on purpose in that ticket’s scope**. Persistence in bootstrap is exactly that scoped leftover — and yes, relative to “`TASK_CONFIG` is the only membership rule,” that leftover is what we missed finishing. The crash list is still that frozenset in `src/utils/config.py`, consumed by `src/core/bootstrap.py`.

## Files to touch

| File | Why |
| -- | -- |
| `src/core/bootstrap.py` | Stop inventory loop over `DISPATCH_SCHEDULABLE_TASK_KEYS` (or replace with TASK_CONFIG-only coupling). |
| `src/utils/config.py` | Delete or narrow `DISPATCH_SCHEDULABLE_TASK_KEYS` and any helpers that still treat it as a required second catalog. |
| `src/ui/api/api_admin.py` | Form enrichment still references the frozenset — align with TASK_CONFIG-only rule. |
| `tests/component/utils/test_config.py` | Drop/adjust assertions that require schedulable frozenset ⊆ TASK_CONFIG for boot. |
| `tests/component/ui/api/test_api_admin.py` | Keep [AST-856](https://linear.app/astralcareermatch/issue/AST-856/check-cover-letter-not-recognized-as-a-valid-task-key) Save regression; adjust any frozenset-inventory tests. |

## Proposed child tickets

| # | Working title | What it delivers | Agent | Sequencing |
| -- | -- | -- | -- | -- |
| 1 | Drop bootstrap schedulable-frozenset inventory | Bootstrap no longer walks `DISPATCH_SCHEDULABLE_TASK_KEYS`; local boot green; [AST-856](https://linear.app/astralcareermatch/issue/AST-856/check-cover-letter-not-recognized-as-a-valid-task-key) Save unchanged; frozenset deleted or non-gating. Does not own gazer runtime fetch. | Ada | — |

Monolith check: Functional scope has 4 capabilities; one child intentional — bootstrap + frozenset retirement + [AST-856](https://linear.app/astralcareermatch/issue/AST-856/check-cover-letter-not-recognized-as-a-valid-task-key) regression ship atomically for “server loads.”

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| [AST-957](https://linear.app/astralcareermatch/issue/AST-957/local-host-server-doesnt-load) (parent) | ftr/AST-957-local-host-server-doesnt-load |
| [AST-960](https://linear.app/astralcareermatch/issue/AST-960/drop-bootstrap-schedulable-frozenset-inventory-local-host-server) | sub/AST-957/AST-960-drop-bootstrap-schedulable-frozenset-inventory |

**Epic worktree:** `astral-AST-957/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during `do-all-the-things` / `fix-uat`. **datt resume:** read this table for child agent `--resume` ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Ada | engineer | fbfda19f-8057-46ba-98cb-2e89f598a62e |
| Betty | qa | 42544071-44d1-44ac-b0a1-d01ed3310b94 |
| Radia | review | c6243e3a-b18e-41b2-9b3e-5c1ed12dba17 |

---

## Original brief

```
flask-api http://localhost:5001 (Ctrl-C to stop)
tip: vite live-reload at http://localhost:5173 — launch.sh --vite
Stytch auth configured: env=test project_id=project-test-3c7ad997-81ae-4ca1-…
Traceback (most recent call last):
  File "/Users/susan/chuckles/astral/src/core/bootstrap.py", line 38, in _validate_runtime_coupling
    dispatch_task_admin_defaults(key)
  File "/Users/susan/chuckles/astral/src/utils/config.py", line 1530, in dispatch_task_admin_defaults
    raise KeyError(f"dispatch_task_admin_defaults: unknown task_key {tk!r}")
KeyError: "dispatch_task_admin_defaults: unknown task_key 'fetch_jd'"

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/Users/susan/chuckles/astral/src/ui/server.py", line 65, in <module>
    bootstrap_runtime()
  File "/Users/susan/chuckles/astral/src/core/bootstrap.py", line 46, in bootstrap_runtime
    _validate_runtime_coupling()
  File "/Users/susan/chuckles/astral/src/core/bootstrap.py", line 40, in _validate_runtime_coupling
    raise RuntimeError(
RuntimeError: bootstrap: dispatch schedulable key 'fetch_jd' missing from TASK_CONFIG
```

### Comments

#### chuckles — 2026-07-23T02:45:02.693Z
[check-linear] Todo — frozenset still in config+bootstrap; waiting OQ1 (@susan)

Yes: AST-856/955 removed it as Save membership only. `DISPATCH_SCHEDULABLE_TASK_KEYS` still exists in `config.py` and bootstrap still inventories it (`bootstrap.py` loop). That leftover is this ticket — confirm OQ1 (drop frozenset inventory vs register missing keys).

— Chuckles

#### chuckles — 2026-07-23T02:32:54.373Z
@susan

AST-856 did **not** delete `DISPATCH_SCHEDULABLE_TASK_KEYS` — it stopped using it as the **Save** gate. AST-955’s written Decision **kept** the frozenset for bootstrap / form enrichment. That’s why bootstrap still walks it and why `fetch_jd` on that list (not in `TASK_CONFIG`) kills boot.

Relative to “TASK_CONFIG is the only membership rule,” yes — finishing that leftover was out of AST-856 scope and belongs here. Definition flipped: **remove bootstrap’s frozenset inventory**, not stuff `fetch_*` into `TASK_CONFIG`.

Need your confirm on Open question 1.

[check-linear] Discussion — frozenset leftover = AST-955 scoped keep; OQ1 (@susan)

— Chuckles

#### susan — 2026-07-23T02:30:47.343Z
@chuckles Once again, didn't we EXPLICITLY remove DISPATCH_SCHEDULABLE_TASK_KEYS as a list from config? Why would it need to persist in bootstrap?  Did we miss it in the scoping of the ticket?

#### chuckles — 2026-07-23T02:21:53.600Z
@susan

Bootstrap walks **`DISPATCH_SCHEDULABLE_TASK_KEYS`** from `src/utils/config.py` (imported in `bootstrap.py` → `_validate_runtime_coupling`). The `fetch_*` names come from that frozenset — not from GAZER scan. Each schedulable key not in `TASK_CONFIG` then hits `dispatch_task_admin_defaults` and blows up. Noted in Description.

[check-linear] Discussion — bootstrap list = DISPATCH_SCHEDULABLE_TASK_KEYS (@susan)

— Chuckles

#### susan — 2026-07-23T02:19:26.476Z
@chuckles Thanks, but what list is bootstrap.py working from that it's getting the fetch\* tasks?

#### chuckles — 2026-07-23T02:15:16.760Z
[check-linear] Discussion — schedulable≠registered; files listed in description (@susan)

— Chuckles

#### susan — 2026-07-23T01:40:05.024Z
@chuckles Help me understand the distinction between "schedulable" and "registered"?  That sounds synonymy.  Specifically, list in the issue description the files that need to be touched.

#### susan — 2026-07-23T00:56:23.594Z
Help me understand the distinction between "schedulable" and "registered"?  That sounds synonymy.  Specifically, list in the issue description the files that need to be touched.

#### chuckles — 2026-07-23T00:47:36.389Z
[check-linear] Discussion — definition rewritten as AST-856 catalog SoT completion (register missed schedulable keys); waiting Todo (@susan)

#### susan — 2026-07-23T00:43:15.260Z
@chuckles I think you're going the wrong way here.  If boot is failing because it's looking for fetch_jd in a canonical config list, then that was missed from the scope of [AST-856](https://linear.app/astralcareermatch/issue/AST-856/check-cover-letter-not-recognized-as-a-valid-task-key) to remove the redundant check-safes versus using the task_config array as the source of truth.

#### chuckles — 2026-07-23T00:38:42.029Z
@susan

1. Coupling direction — **(A)** register the schedulable-but-catalog-missing keys in the task catalog so one membership rule covers Save + bootstrap, or **(B)** keep them outside the catalog and restore bootstrap/admin-default resolution for schedulable-only keys without weakening AST-856 Save acceptance for catalog-only keys like `check_cover_letter`?
2. Project home — **Astral Roster**, **Astral Foundation**, or **Astral Artifacts**?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
