# Astral Git Workflow

Authoritative git workflow for Astral. Supersedes all prior branch law in `orientation-astral`, Joan `git-*` skills, and related pipeline skills. **If a skill disagrees with this document, this document wins.**

**Test corpus:** `docs/test-bible/` (per-component tree; monolith `docs/ASTRAL_TEST_BIBLE.md` retained until AST-598 Radia review).

---

## Permanent branches

Three permanent branches on `origin`. Nothing else is permanent.

| Branch | Owner | Purpose |
|--------|-------|---------|
| `main` | Susan | Production |
| `dev` | Chuckles | Integration |
| `tests` | Betty | Cumulative test corpus |

Flow direction is strictly one-way:

```
dev   → ftr → sub   (work flows down at dispatch)
tests → sub         (Betty merge-tests)
sub   → ftr → dev   (integration flows up)
dev   → main        (release only)
```

`tests` never merges into `dev` or `main` directly. `dev` never merges into `tests`. These directions are inviolable.

---

## Feature branch topology

Every Linear parent maps to exactly one `ftr/` branch. Every child sub-issue maps to exactly one `sub/` branch. Both exist only on `origin` — not as persistent local branch names outside the active ftr worktree.

| Kind | Pattern | Example |
|------|---------|---------|
| Parent feature | `ftr/<ticket-id>-<title-slug>` | `ftr/AST-777-cure-common-cold` |
| Child sub-issue | `sub/<parent-id>/<child-id>-<title-slug>` | `sub/AST-777/AST-779-pray-for-a-miracle` |
| Ad-hoc (no ticket) | `adhoc/<did-this-thing>` | `adhoc/themed-user-prompt` |

Chuckles creates all `ftr/` and `sub/` refs at dispatch. No agent creates them independently.

---

## Worktrees

Assume repo folder name **`<reponame>`** (today: `astral`). Siblings under the parent directory (e.g. `/Users/susan/chuckles/`):

| Pattern | Example | Branch context | Owner | Lifespan |
|---------|---------|----------------|-------|----------|
| `<reponame>/` | `astral/` | `dev` | Chuckles / Susan | Permanent |
| `<reponame>-tests/` | `astral-tests/` | `tests` | Betty | Permanent |
| `<reponame>-<IssueID>/` | `astral-AST-593/` | active `sub/*` | child assignee | Ephemeral — per parent epic |

**Subs get branches, not worktrees.** One **epic worktree** per in-flight parent. Chuckles checks out **one sub-branch at a time** in that worktree.

**Multiple unrelated parents** may be in flight — each gets its own `<reponame>-<parent-id>/` worktree.

Example layout:

```
/Users/susan/chuckles/astral                 ← dev (integration)
/Users/susan/chuckles/astral-tests           ← tests (Betty)
/Users/susan/chuckles/astral-AST-777         ← sub/AST-777/AST-779 checked out now
/Users/susan/chuckles/astral-AST-888         ← unrelated parent, parallel in flight
```

### AGENTS.md and hooks (Chuckles at every handoff)

Chuckles **seeds `AGENTS.md`** in the ftr worktree at **each Linear status handoff** — plan, build, test, review, resolve, etc. **One agent persona in the worktree at a time.** The assigned engineer (or Betty/Radia) works there until that stage completes; Chuckles rewrites `AGENTS.md` before the next role touches the tree.

At ftr worktree creation Chuckles also installs the **pre-commit hook** for the active role.

### Pre-commit hooks by role

Structural enforcement — not prose rules.

| Role | Blocked paths |
|------|---------------|
| Engineer (Ada, Hedy, Katherine) | `tests/`, `docs/ASTRAL_TEST_BIBLE.md`, `docs/test-bible/**` |
| Betty | `src/`, `docs/features/` |
| Radia | `src/`, `tests/` |

Violations fail at commit time with a clear error.

---

## Child sub-issue sequencing

Children are strictly sequential. Child N+1 is not dispatched until Child N has `merge-child()` into `ftr/`. No simultaneous children on the same parent.

---

## Canonical commit sequence

Every sub-branch follows this sequence. Ticket ID in every subject is mandatory.

### Clean sub (no blocking)

```
plan(AST-NNN)         ← engineer
code(AST-NNN)         ← engineer: implementation complete
merge-tests(AST-NNN)   ← Betty: deliver origin/tests <sha> to origin/sub
test(AST-NNN)         ← engineer: src changes to make tests pass
docs(AST-NNN)         ← Radia: — clean OR — findings
resolve(AST-NNN)      ← engineer: — clean OR — findings addressed
```

### Sub with blocking (park-wip / merge-resume pair)

`park-wip` and `merge-resume` may repeat before `code()`.

```
plan(AST-NNN)
park-wip(AST-NNN)      ← blocked; work on origin
merge-resume(AST-NNN)  ← engineer: merge ftr into sub after unblock
code(AST-NNN)
merge-tests(AST-NNN)   ← Betty
test(AST-NNN)
docs(AST-NNN)
resolve(AST-NNN)
```

### Mandatory vs conditional

| Commit | Owner | Mandatory | Condition |
|--------|-------|-----------|-----------|
| `plan()` | Engineer | Yes | Always |
| `park-wip()` | Engineer | No | Blocked only |
| `merge-resume()` | Engineer | No | Paired with each `park-wip()` |
| `code()` | Engineer | Yes | Implementation complete |
| `merge-tests()` | **Betty** | Yes | Merge her `origin/tests` SHA into sub; push `origin/sub` |
| `test()` | Engineer | Yes | Src fixes for manifest green |
| `docs()` | Radia | Yes | Always — clean or findings |
| `resolve()` | Engineer | Yes | Always — clean or addressed |

`docs()` / `resolve()` message conventions:

```
docs(AST-NNN): Radia review — clean
docs(AST-NNN): Radia review — findings

resolve(AST-NNN): — clean
resolve(AST-NNN): — findings addressed
```

---

## The tests branch

`origin/tests` is Betty's permanent branch — single source of truth for all test code and **`docs/test-bible/**`** updates (and transitional edits to the monolith until AST-598 retirement). Betty works in the permanent **`astral-tests`** worktree on local `tests` tracking `origin/tests`.

### Betty's workflow

1. **Local commit** on `tests` in `astral-tests` (test-lane files only).
2. **`./scripts/git/validate-tests-branch.sh`** — must pass before push.
3. **`git push origin tests`** — publish test corpus to `origin/tests`.
4. **`merge-tests(AST-NNN)`** — from `astral-tests`, integrate that commit onto the sub-branch and push `origin/sub/<parent>/<child>`:
   - `git fetch origin`
   - Check out the sub-branch locally (in `astral-tests` worktree — temporary checkout).
   - `git merge <sha>` where `<sha>` is **the single** Betty commit for this ticket from step 1 (already on `origin/tests`).
   - Commit message: `merge-tests(AST-NNN): origin/tests <sha>`.
   - `git push origin HEAD:sub/<parent>/<child>`.
   - Return to local `tests` branch in `astral-tests`.
5. **Engineer** resumes in the **ftr worktree** — checks out the sub-branch at the `merge-tests()` tip from origin (merge-on-checkout from `ftr` as usual).
6. **Engineer** runs tests, fixes `src/` only, commits `test(AST-NNN)`, pushes `origin/sub/...`.

Betty **never** uses the ftr worktree. She references `origin/sub/...` read-only during planning (step 1 prep); step 3 is the only write to the sub-branch, and she does it from `astral-tests`.

### `merge-tests()` — one SHA, one merge

Git mechanism is **`merge` + `push`** — Betty merges her `origin/tests` SHA into the sub-branch, then pushes. **`merge-tests()`** is the canonical commit name on the sub-branch.

**One delivery per ticket.** Betty declares exactly **one** SHA per child ticket and produces exactly **one** `merge-tests(AST-NNN): origin/tests <sha>` on `origin/sub/...`. If she revises tests on `origin/tests`, amend or squash on `tests` **before** merging to the sub — **never** push twice and merge twice for the same ticket (that interleaves test SHAs and duplicate merge commits on the sub log).

Betty owns the SHA — she created it in step 1. No Linear comment chain for handoff.

### Why SHA, not branch tip

Betty may be ahead on `origin/tests` writing tests for the next ticket. Merging branch tip would pull tests for unbuilt work. The SHA pins the merge to exactly what is ready for this ticket.

`git merge <sha>` is a true merge, not a cherry-pick.

---

## Chuckles-owned merges

| Commit | Operation |
|--------|-----------|
| `merge-child(AST-NNN)` | sub → ftr |
| `finish-up(AST-NNN)` | ftr → dev (parent close after PR Ready) |

**Internal only:** `scripts/git/merge-parent.sh` is invoked by `finish-up-land.sh` as a land helper — agents and operators run the **`finish-up`** skill, not `merge-parent` as a skill or commit name.

Before `merge-child()`, Chuckles validates the sub-branch log:

- `plan()` present
- `code()` present
- `merge-tests()` present — **exactly one** per child id
- `test()` present
- `docs()` with `— clean` or `— findings`
- `resolve()` with matching state
- If `park-wip()`: paired `merge-resume()`
- No commits to blocked paths (hooks enforce)
- No **`Merge remote-tracking branch`** (git pull on sub)

**Script (mandatory):** `./scripts/git/validate-sub-log.sh <publish-ref> [child-id]` — called by **`merge-child.sh`**.

Failure → Chuckles posts on the Linear ticket; no merge.

---

## Engineer-owned merges

| Commit | Operation |
|--------|-----------|
| `merge-resume(AST-NNN)` | ftr into sub after unblocking |
| merge on checkout | ftr into sub whenever sub is checked out |

### Merge on checkout (mandatory)

Whenever the **engineer** (or Chuckles seeding the epic worktree) checks out a **`sub/*`** branch in **`<reponame>-<parent-id>/`**:

```bash
git fetch origin
git checkout sub/<parent>/<child-slug>
git merge origin/ftr/<parent-segment>
```

No-op if ftr unchanged; mandatory every time.

---

## Complete commit vocabulary

| Commit type | Owner | Mandatory | Meaning |
|-------------|-------|-----------|---------|
| `plan()` | Engineer | Yes | Plan doc written |
| `code()` | Engineer | Yes | Implementation complete |
| `park-wip()` | Engineer | Conditional | Blocked — parked on origin |
| `merge-resume()` | Engineer | Conditional | Ftr merged after unblock |
| `merge-tests()` | **Betty** | Yes | Deliver `origin/tests` SHA to `origin/sub` |
| `test()` | Engineer | Yes | Src changes — tests pass |
| `docs()` | Radia | Yes | Review — clean or findings |
| `resolve()` | Engineer | Yes | Review loop closed |
| `merge-child()` | Chuckles | Yes | Sub → ftr |
| `finish-up()` | Chuckles | Yes | Ftr → dev (parent close; after Susan sets PR Ready) |

Ten commit types. One owner each.

**Deprecated on new work:** `feat()`, `fix()`, and `push-tests()` — use `code()` (build), `test()` (test-child src fixes), and `merge-tests()` (Betty delivery) instead.

---

## Chuckles git hygiene

Chuckles merge scripts (`refresh-ftr.sh`, `merge-child.sh`) use ephemeral `tmp-refresh-*` / `tmp-merge-child-*` local branch names. Those branches must be deleted when the script exits — they must **never** appear on `origin` or linger in `git log` decorations.

**Never push to origin:** `worktree/*`, `tmp-*`, `tmp-fix-*`. Prune strays: `./scripts/git/prune-remote-scratch-refs.sh` (use `--dry-run` first).

Epic worktrees check out **`origin/ftr/<parent-segment>`** (see **`agent-worktrees.sh epic-create`**), not legacy **`worktree/AST-NNN`** branch names.

Legacy `worktree/<IssueID>` refs on **origin** should be deleted. Only `sub/*`, `ftr/*`, `dev`, `tests`, and `main` should matter in day-to-day history.

## What never happens

- `dev-<agent>` branches (local or on origin)
- Cherry-pick onto any branch
- Rebase of any branch pushed to origin
- Force-push to any branch on origin
- Simultaneous child subs on the same parent
- Engineer commits to `tests/`, `docs/ASTRAL_TEST_BIBLE.md`, or `docs/test-bible/**`
- Betty commits to `src/` or `docs/features/` (except `merge-tests()` merge commit on sub)
- `tests` merging into `dev` or `main`
- Any agent creating `ftr/` or `sub/` refs
- `merge-child()` before Chuckles validates commit sequence
- Two agents' personas in one ftr worktree at the same time

---

## Reference graph

See team process doc or Chuckles onboarding for the full multi-sub / UAT-bug example graph. Day-to-day work uses the commit vocabulary above.

---

## Skills map

Executable procedures live in global Cursor skills under `~/.cursor/skills/`. Each stage skill links here for law; it owns steps only.

| Skill | Primary delta |
|-------|----------------|
| `orientation` | Cheat sheet + pointer here |
| `dispatch-parent` | Epic worktree create, branch seed, `seed-agents-md` + hook |
| `plan-child` … `resolve-child` | Sub-branch commit sequence |
| `qa-child` / Betty test stage | `origin/tests` workflow |
| `merge-child` | Pre-merge validation; sub → ftr |
| `finish-up` / `prep-uat` | finish-up lands ftr → `origin/dev` (parent close); prep-uat pushes `origin/dev` for staging UAT |

Joan `git-store-*` cherry-pick skills are **retired**.
