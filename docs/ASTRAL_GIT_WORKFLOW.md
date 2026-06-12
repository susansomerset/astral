# Astral Git Workflow

Authoritative git workflow for Astral. Supersedes all prior branch law in `orientation-astral`, Joan `git-*` skills, and related pipeline skills. **If a skill disagrees with this document, this document wins.**

**Test corpus:** `docs/ASTRAL_TEST_BIBLE.md` (monolith until AST-598 breakdown lands).

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
tests → sub         (Betty merges in at declared SHA)
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
| Engineer (Ada, Hedy, Katherine) | `tests/`, `docs/ASTRAL_TEST_BIBLE.md` |
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
push-tests(AST-NNN)   ← Betty: deliver origin/tests <sha> to origin/sub
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
push-tests(AST-NNN)   ← Betty
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
| `push-tests()` | **Betty** | Yes | Merge her `origin/tests` SHA into sub; push `origin/sub` |
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

`origin/tests` is Betty's permanent branch — single source of truth for all test code and `docs/ASTRAL_TEST_BIBLE.md` updates. Betty works in the permanent **`astral-tests`** worktree on local `tests` tracking `origin/tests`.

### Betty's workflow

1. **Local commit** on `tests` in `astral-tests` (test-lane files only).
2. **`git push origin tests`** — publish test corpus to `origin/tests`.
3. **`push-tests(AST-NNN)`** — from `astral-tests`, integrate that commit onto the sub-branch and push `origin/sub/<parent>/<child>`:
   - `git fetch origin`
   - Check out the sub-branch locally (in `astral-tests` worktree — temporary checkout).
   - `git merge <sha>` where `<sha>` is Betty's commit from step 1 (already on `origin/tests`).
   - Commit message: `push-tests(AST-NNN): origin/tests <sha>`.
   - `git push origin HEAD:sub/<parent>/<child>`.
   - Return to local `tests` branch in `astral-tests`.
4. **Engineer** resumes in the **ftr worktree** — checks out the sub-branch at the `push-tests()` tip from origin (merge-on-checkout from `ftr` as usual).
5. **Engineer** runs tests, fixes `src/` only, commits `test(AST-NNN)`, pushes `origin/sub/...`.

Betty **never** uses the ftr worktree. She references `origin/sub/...` read-only during planning (step 1 prep); step 3 is the only write to the sub-branch, and she does it from `astral-tests`.

### `push-tests()` vs `merge-tests()`

Git mechanism is **`merge` + `push`** — Betty merges her `origin/tests` SHA into the sub-branch, then pushes. Functionally the same as a merge. **`push-tests()`** is the preferred commit name because it describes Betty's job (deliver tests to the sub) rather than the git verb. Use **`push-tests()`** in the vocabulary; do not use `merge-tests()`.

Betty owns the SHA — she created it in step 1. No Linear comment chain for handoff.

### Why SHA, not branch tip

Betty may be ahead on `origin/tests` writing tests for the next ticket. Merging branch tip would pull tests for unbuilt work. The SHA pins the merge to exactly what is ready for this ticket.

`git merge <sha>` is a true merge, not a cherry-pick.

---

## Chuckles-owned merges

| Commit | Operation |
|--------|-----------|
| `merge-child(AST-NNN)` | sub → ftr |
| `merge-parent(AST-NNN)` | ftr → dev |

Before `merge-child()`, Chuckles validates the sub-branch log:

- `plan()` present
- `code()` present
- `merge-tests()` present → **`push-tests()`** present
- `test()` present
- `docs()` with `— clean` or `— findings`
- `resolve()` with matching state
- If `park-wip()`: paired `merge-resume()`
- No commits to blocked paths (hooks enforce)

Failure → Chuckles posts on the Linear ticket; no merge.

---

## Engineer-owned merges

| Commit | Operation |
|--------|-----------|
| `merge-resume(AST-NNN)` | ftr into sub after unblocking |
| merge on checkout | ftr into sub whenever sub is checked out |

### Merge on checkout (mandatory)

Whenever Chuckles checks out a sub-branch in the ftr worktree:

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
| `push-tests()` | **Betty** | Yes | Deliver `origin/tests` SHA to `origin/sub` |
| `test()` | Engineer | Yes | Src changes — tests pass |
| `docs()` | Radia | Yes | Review — clean or findings |
| `resolve()` | Engineer | Yes | Review loop closed |
| `merge-child()` | Chuckles | Yes | Sub → ftr |
| `merge-parent()` | Chuckles | Yes | Ftr → dev |

Ten commit types. One owner each.

---

## What never happens

- `dev-<agent>` branches (local or on origin)
- Cherry-pick onto any branch
- Rebase of any branch pushed to origin
- Force-push to any branch on origin
- Simultaneous child subs on the same parent
- Engineer commits to `tests/` or `docs/ASTRAL_TEST_BIBLE.md`
- Betty commits to `src/` or `docs/features/` (except `push-tests()` merge commit on sub)
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
| `merge-parent` / `prep-uat` | Ftr → dev; prep-uat pushes `origin/dev` |

Joan `git-store-*` cherry-pick skills are **retired**.
