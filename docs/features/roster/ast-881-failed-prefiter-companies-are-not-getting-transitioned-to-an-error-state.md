# AST-881 — failed prefiter companies are not getting transitioned to an error state

<!-- linear-archive: AST-881 archived 2026-07-29 -->

## Linear archive (AST-881)

**Archived:** 2026-07-29  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-881/failed-prefiter-companies-are-not-getting-transitioned-to-an-error  
**Status at archive:** Archive  
**Project:** Astral Roster  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Prefilter is chewing the same companies over and over: technical failures (for example grade-reason hydration) land them in the retry holding state, dispatch claims them again, and monitor keeps alerting on the same stuck set. The product contract for prefilter technical failure is already one automatic retry, then a terminal error state — this epic makes that contract hold so the queue stops looping and Susan can see which companies need attention.

## Functional scope

* On a retryable prefilter technical failure (decode, grade-reason hydration, missing/invalid parse, or equivalent API-body failure paths) from the primary prefilter-eligible company state, the company moves to the established prefilter retry holding state (`WEBSITE_FOUND_RETRY`) exactly once.
* On a further prefilter failure for a company already in that retry holding state — whether the same retryable technical class or a hard/system failure — the company moves to the established prefilter error state (`ERROR_PREFILTER`) and leaves the automatic prefilter claim pool.
* Batch summaries and monitor auto-run error reporting reflect companies that exhausted the single retry and landed in the error state, rather than an unbounded retry pool of the same ids.
* When prefilter runs with debug enabled, each company outcome records what was found and what state was written (retry vs error), using the backend debug contract (distinct index headers with `index N/M`, primary company identifier, and outcome; working detail lines prefixed with `|`).

## Boundaries

* Does not change successful evaluate outcomes: `PREFILTER_PASSED`, `PREFILTER_FAILED`, or `NO_PREFILTER_JOBLISTS` for companies that complete a clean prefilter evaluate.
* Does not redesign `fetch_website` infra retry (covered elsewhere) or other roster stages’ retry/error maps.
* Does not require fixing LLM grade quality or malformed vector labels as a deliverable — those failures still follow one-retry-then-error.
* Does not add new company states beyond the established prefilter retry and error states.
* Does not require a one-time production data migration unless Susan later asks for cleanup of companies already stuck in retry; steady-state routing is the scope.
* Must not break the legitimate single automatic retry for first-strike technical failures.

## Acceptance criteria

1. A company that fails prefilter for a retryable technical reason while in the primary prefilter-eligible state is observable in `WEBSITE_FOUND_RETRY` afterward.
2. The same company, claimed again from `WEBSITE_FOUND_RETRY` and failing prefilter again, is observable in `ERROR_PREFILTER` afterward — not still in `WEBSITE_FOUND_RETRY`.
3. Companies in `ERROR_PREFILTER` are not re-claimed by automatic prefilter dispatch on later scheduler loops.
4. Re-running prefilter against a set that previously produced repeated monitor alerts for the same technical failures no longer leaves those companies cycling forever in `WEBSITE_FOUND_RETRY`; after one retry they are in `ERROR_PREFILTER`.
5. Companies that evaluate cleanly still reach the same pass / fail / no-joblists outcomes as today.

## Dependencies and blockers

none.

## Open questions

none.

## Git (authoritative — ignore Linear `gitBranchName`)

| Ticket | `origin/…` |
| -- | -- |
| AST-881 (parent) | ftr/AST-881-prefilter-retry-to-error |
| AST-882 | sub/AST-881/AST-882-prefilter-one-retry-error |

**Epic worktree:** `astral-AST-881/` — one active sub checked out at a time.

## Team (authoritative — headless `--resume` thread ids)

Populated by Chuckles during do-all-the-things / fix-uat. datt resume: read this table for child agent --resume ids — not chat memory or local files.

| Agent | Role | Thread |
| -- | -- | -- |
| Hedy | engineer | acb629ad-6869-4b9a-a995-f6de960690d0 |
| Betty | qa | 9d4f22fe-f9de-4a00-8ea2-2e48f4ade8ea |
| Radia | review | 8e64aab8-e147-4016-85b7-f91a5359a468 |

---

## Original brief

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
