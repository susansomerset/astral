# Astral Git Workflow

Authoritative git workflow for Astral. Supersedes all prior branch law in `orientation-astral`, Joan `git-*` skills, and related pipeline skills. **If a skill disagrees with this document, this document wins.**

**Test corpus:** `docs/test-bible/` (per-component tree; monolith `docs/ASTRAL_TEST_BIBLE.md` retained until AST-598 Radia review).

---

## Permanent branches

**Statute:** `orch.git.three-permanent-branches`
**Statute:** `orch.git.flow-direction-inviolable`

Two permanent branches on `origin`. Nothing else is permanent.

| Branch | Owner | Purpose |
|--------|-------|---------|
| `main` | Archie | Production |
| `dev` | Chuckles | Integration — product code **and** the cumulative test corpus (`tests/`, `docs/test-bible/`) |

`tests` is **retired** (AST-2107 follow-up). It stays on origin as frozen history; nothing is pushed to it or merged from it. It used to give every test two routes onto a sub (Betty's `merge-tests` and `dev`), and the two copies drifted into conflicts and silent test deletions.

Flow direction is strictly one-way:

```
dev   → ftr → sub   (work flows down at dispatch / sync-child)
sub   → ftr → dev   (integration flows up: merge-child, finish-up)
dev   → main        (release only)
```

Tests and the bible ride the same path as product code: Betty commits them on the sub. One path, one copy of every test.

---

## Feature branch topology

**Statute:** `orch.git.ftr-sub-topology`

Every Linear parent maps to exactly one `ftr/` branch. Every child sub-issue maps to exactly one `sub/` branch. Both exist only on `origin` — not as persistent local branch names outside the active ftr worktree.

| Kind | Pattern | Example |
|------|---------|---------|
| Parent feature | `ftr/<ticket-id>-<title-slug>` | `ftr/AST-777-cure-common-cold` |
| Child sub-issue | `sub/<parent-id>/<child-id>-<title-slug>` | `sub/AST-777/AST-779-pray-for-a-miracle` |
| Ad-hoc (no ticket) | `adhoc/<did-this-thing>` | `adhoc/themed-user-prompt` |

Chuckles creates all `ftr/` and `sub/` refs at dispatch. No agent creates them independently.

---

## Worktrees

**Statute:** `orch.git.one-epic-worktree-per-parent`

Assume repo folder name **`<reponame>`** (today: `astral`). Siblings under the parent directory (e.g. `/Users/susan/chuckles/`):

| Pattern | Example | Branch context | Owner | Lifespan |
|---------|---------|----------------|-------|----------|
| `<reponame>/` | `astral/` | `dev` | Chuckles / Archie | Permanent |
| `<reponame>-<IssueID>/` | `astral-AST-593/` | active `sub/*` | child assignee | Ephemeral — per parent epic |

**Subs get branches, not worktrees.** One **epic worktree** per in-flight parent. Chuckles checks out **one sub-branch at a time** in that worktree.

**Multiple unrelated parents** may be in flight — each gets its own `<reponame>-<parent-id>/` worktree.

Example layout:

```
/Users/susan/chuckles/astral                 ← dev (integration)
/Users/susan/chuckles/astral-AST-777         ← sub/AST-777/AST-779 checked out now
/Users/susan/chuckles/astral-AST-888         ← unrelated parent, parallel in flight
```

### AGENTS.md and hooks (Chuckles at every handoff)

Chuckles **seeds `AGENTS.md`** in the ftr worktree at **each Linear status handoff** — plan, build, test, review, resolve, etc. **One agent persona in the worktree at a time.** The assigned engineer (or Betty/Radia) works there until that stage completes; Chuckles rewrites `AGENTS.md` before the next role touches the tree.

At ftr worktree creation Chuckles also installs the **pre-commit hook** for the active role.

### Pre-commit hooks by role

**Statute:** `orch.roles.pre-commit-path-bans`

Structural enforcement — not prose rules.

| Role | Blocked paths |
|------|---------------|
| Engineer (Ada, Hedy, Katherine) | `tests/`, `docs/ASTRAL_TEST_BIBLE.md`, `docs/test-bible/**` |
| Betty | `src/`, `docs/features/` |
| Radia | `src/`, `tests/` |

Violations fail at commit time with a clear error.

**Merge commits** (a `sync-child` merge on a sub): a role-blocked path may be staged only when it is byte-identical to `HEAD`, `MERGE_HEAD`, or git's own clean auto-merge of that path — the merge takes a side, it never edits another role's files. Resolve such a conflict by taking one side whole (`git checkout origin/dev -- <path>`). `--no-verify` is never needed and never allowed.

---

## Child sub-issue sequencing

**Narrative (not a statute):** see `canon/statutes/HARVEST.md` § Narrative leftovers — `git-child-strict-sequential-prose`

Children are strictly sequential. Child N+1 is not dispatched until Child N has `merge-child()` into `ftr/`. No simultaneous children on the same parent.

---

## Canonical commit sequence

**Statute:** `orch.git.commit-vocabulary`

Every sub-branch follows this sequence. Ticket ID in every subject is mandatory.

### Clean sub (no blocking)

```
plan(AST-NNN)         ← engineer
code(AST-NNN)         ← engineer: implementation complete
test(AST-NNN)         ← Betty: tests + bible, committed on the sub
test(AST-NNN)         ← engineer: src changes to make tests pass (only if needed)
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
test(AST-NNN)          ← Betty
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
| `test()` (test tree) | **Betty** | Yes\* | Tests + `docs/test-bible/**` committed on the sub; revisions are further additive commits |
| `test()` (src) | Engineer | Conditional | Src fixes for manifest green — only when the manifest needed product changes |
| `docs()` | Radia | Yes | Always — clean or findings |
| `resolve()` | Engineer | Yes | Always — clean or addressed |

\* Betty's test-tree delivery is optional when the child is **docs-acceptance** (`test()` / `code()` / `docs()` subject contains that phrase). `validate-sub-log.sh` enforces this. A commit never carries both test-tree and `src/` changes. Subs dispatched before this change may still carry a legacy `merge-tests()` delivery; the validator accepts it.

`docs()` / `resolve()` message conventions:

```
docs(AST-NNN): Radia review — clean
docs(AST-NNN): Radia review — findings

resolve(AST-NNN): — clean
resolve(AST-NNN): — findings addressed
```

---

## Betty's test delivery

**Statute:** `orch.git.betty-tests-on-sub` (supersedes the retired `orch.git.betty-merge-tests-one-sha`)

Betty works in the parent's **epic worktree** on the child's sub — the same checkout the engineer uses, never at the same time (Chuckles seeds `betty-AGENTS.md` + the `betty` hook at the Code Complete handoff; `datt_trace` holds a per-worktree lock for each spawn).

1. `sync-child.sh <publish-ref> --ftr <parent-segment> --worktree <epic-worktree>` — the sub now has `dev`, the rolled-up ftr, and the engineer's code.
2. Write / revise tests and the bible against exactly that tree.
3. Commit `test(AST-NNN): …` (or `docs(AST-NNN): test bible — …`) — test-tree paths only (the `betty` hook blocks `src/` and `docs/features/`).
4. `git push origin HEAD:sub/<parent>/<child>`. Non-fast-forward → re-run `sync-child.sh`, push again.
5. **Engineer** re-runs `sync-child.sh`, runs the manifest, fixes `src/` only, commits `test(AST-NNN)` if anything changed, pushes.

Revisions (a `[qa-handoff]` return, a review finding) are new additive commits. There is no "one delivery" limit, so there is never a reason to rewrite a sub.

## Chuckles-owned merges

| Commit | Operation |
|--------|-----------|
| `merge-child(AST-NNN)` | sub → ftr |
| `finish-up(AST-NNN)` | ftr → dev (parent close after PR Ready) |

**Internal only:** `scripts/git/merge-parent.sh` is invoked by `finish-up-land.sh` as a land helper — agents and operators run the **`finish-up`** skill, not `merge-parent` as a skill or commit name.

Before `merge-child()`, Chuckles validates the sub-branch log:

- `plan()` present (alias: `docs(AST-NNN): plan — …` from plan-child)
- `code()` present
- Betty's test delivery present — a `test()`/`docs()` commit touching `tests/` or `docs/test-bible/` (or a legacy `merge-tests()`) — **except docs-acceptance**
- `test()` present
- No single commit changing both `src/` and test-tree paths
- `docs()` with `— clean` or `— findings`
- `resolve()` with matching state
- If `park-wip()`: paired `merge-resume()`
- No commits to blocked paths (hooks enforce)
- No **`Merge remote-tracking branch`** (git pull on sub)

The validator judges only commits on the sub that are on neither `origin/ftr` nor `origin/dev`, so dev history never counts against a sub. `merge-child.sh` merges `origin/dev` into ftr first when ftr is behind.

**Docs-acceptance:** when a `test(AST-NNN):`, `code(AST-NNN):` or `docs(AST-NNN):` subject contains **`docs-acceptance`** (no test-tree delivery), the test delivery is not required. Do not invent a Betty delivery to satisfy the gate.

**Script (mandatory):** `./scripts/git/validate-sub-log.sh <publish-ref> [child-id] [ftr-ref]` — called by **`merge-child.sh`**.

Failure → Chuckles posts on the Linear ticket; no merge.

---

## Engineer-owned merges

| Commit | Operation |
|--------|-----------|
| `merge-resume(AST-NNN)` | ftr into sub after unblocking |
| merge on checkout | ftr into sub whenever sub is checked out |

### Merge on checkout (mandatory)

**Statute:** `orch.git.merge-on-checkout`

Whenever the **engineer** (or Chuckles seeding the epic worktree) checks out a **`sub/*`** branch in **`<reponame>-<parent-id>/`**:

```bash
git fetch origin
git checkout sub/<parent>/<child-slug>
git merge origin/ftr/<parent-segment>
```

No-op if ftr unchanged; mandatory every time.

---

## Complete commit vocabulary

**Statute:** `orch.git.commit-vocabulary`

| Commit type | Owner | Mandatory | Meaning |
|-------------|-------|-----------|---------|
| `plan()` | Engineer | Yes | Plan doc written |
| `code()` | Engineer | Yes | Implementation complete |
| `park-wip()` | Engineer | Conditional | Blocked — parked on origin |
| `merge-resume()` | Engineer | Conditional | Ftr merged after unblock |
| `test()` | **Betty** / Engineer | Yes\* | Betty: tests + bible on the sub. Engineer: src changes so tests pass. Never both in one commit (\*Betty's skipped when docs-acceptance) |
| `docs()` | Radia | Yes | Review — clean or findings |
| `resolve()` | Engineer | Yes | Review loop closed |
| `merge-child()` | Chuckles | Yes | Sub → ftr |
| `finish-up()` | Chuckles | Yes | Ftr → dev (parent close; after Archie sets PR Ready (Linear: Susan)) |

Nine commit types, plus the `sync(dev|ftr|publish-ref): …` merge subjects written by `sync-child.sh`, `merge-child.sh` and `refresh-ftr.sh` (scripts never use git's default merge message).

**Deprecated on new work:** `feat()`, `fix()`, `push-tests()`, and `merge-tests()` — use `code()` (build) and `test()` (Betty's tests on the sub; engineer src fixes) instead.

---

## Chuckles git hygiene

**Narrative (not a statute):** see `canon/statutes/HARVEST.md` § Narrative leftovers — `git-chuckles-hygiene-tmp-branches`

Chuckles merge scripts (`refresh-ftr.sh`, `merge-child.sh`) use ephemeral `tmp-refresh-*` / `tmp-merge-child-*` local branch names. Those branches must be deleted when the script exits — they must **never** appear on `origin` or linger in `git log` decorations.

**Never push to origin:** `worktree/*`, `tmp-*`, `tmp-fix-*`. Prune strays: `./scripts/git/prune-remote-scratch-refs.sh` (use `--dry-run` first).

Epic worktrees check out **`origin/ftr/<parent-segment>`** (see **`agent-worktrees.sh epic-create`**), not legacy **`worktree/AST-NNN`** branch names.

Legacy `worktree/<IssueID>` refs on **origin** should be deleted. Only `sub/*`, `ftr/*`, `dev`, `tests`, and `main` should matter in day-to-day history.

## What never happens

**Statute:** `orch.git.no-cherry-pick-rebase-force`
**Statute:** `orch.git.no-dev-agent-branches`
**Statute:** `astral.git.engineer-test-tree-ban`
**Statute:** `astral.git.betty-no-src-or-features`

- `dev-<agent>` branches (local or on origin)
- Cherry-pick onto any branch
- Rebase of any branch pushed to origin
- Force-push to any branch on origin
- Simultaneous child subs on the same parent
- Engineer commits to `tests/`, `docs/ASTRAL_TEST_BIBLE.md`, or `docs/test-bible/**` (a merge commit may carry them only byte-identical to a parent)
- Betty commits to `src/` or `docs/features/` (same merge-commit rule)
- Anything pushed to or merged from the retired `tests` branch
- `--no-verify` on any commit
- Any agent creating `ftr/` or `sub/` refs
- `merge-child()` before Chuckles validates commit sequence
- Two agents' personas in one ftr worktree at the same time

---

## Reference graph

**Narrative (not a statute):** see `canon/statutes/HARVEST.md` § Narrative leftovers — `git-reference-graph`

See team process doc or Chuckles onboarding for the full multi-sub / UAT-bug example graph. Day-to-day work uses the commit vocabulary above.

---

## Skills map

**Narrative (not a statute):** see `canon/statutes/HARVEST.md` § Narrative leftovers — `git-skills-map`

Executable procedures live in global Cursor skills under `~/.cursor/skills/`. Each stage skill links here for law; it owns steps only.

| Skill | Primary delta |
|-------|----------------|
| `orientation` | Cheat sheet + pointer here |
| `dispatch-parent` | Epic worktree create, branch seed, `seed-agents-md` + hook |
| `plan-child` … `resolve-child` | Sub-branch commit sequence |
| `qa-child` / `qa-fix` | Betty's tests committed on the sub |
| `merge-child` | Pre-merge validation; sub → ftr |
| `finish-up` / `prep-uat` | finish-up lands ftr → `origin/dev` (parent close); prep-uat pushes `origin/dev` for staging UAT |

Joan `git-store-*` cherry-pick skills are **retired**.
