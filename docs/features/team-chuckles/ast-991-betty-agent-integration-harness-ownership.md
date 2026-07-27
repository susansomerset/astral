# AST-991 — Betty agent: integration harness ownership

- **Linear:** [AST-991](https://linear.app/astralcareermatch/issue/AST-991/betty-agent-integration-harness-ownership-betty-monitors-integration)
- **Parent:** [AST-989](https://linear.app/astralcareermatch/issue/AST-989/betty-monitors-integration-tests-agent-skills)
- **Publish ref:** `origin/sub/AST-989/AST-991-betty-agent-integration-harness-ownership`
- **Summary:** Update Betty’s agent identity/standards wording so reading `betty-AGENTS.md` alone makes clear she owns ongoing GHA integration-harness green and integration-test drift of **existing** scenarios, parallel to component test-tree / bible ownership. Does **not** rewrite QA skill procedure steps (AST-992), invent new integration coverage, or fix AST-988’s harness red.

## UAT fitness

- **AC restored:** Parent AC1 — “Reading Betty’s agent content alone makes clear she owns ongoing GHA integration-harness green and integration-test drift alongside the component test tree.” Parent AC4 — “After host install of the updated agent/skills, a Betty session following those docs would treat a drifted **existing** integration scenario as her authority the same way she treats a broken component test.” (This child delivers the agent-content half of AC4; skills half is AST-992.)
- **Correct outcome:** A reader of installed Betty agent content knows GHA harness green + drift of existing integration scenarios are Betty’s concern, same class of authority as a broken component test — not a Foundation one-off and not “someone else’s problem.”
- **Sibling check:** AST-992 owns QA skill / intake-handoff **procedure** for revise-vs-`[qa-handoff]`. This plan must not edit `qa-child` or other skills. Engineer skills stay untouched except any one-line cross-ref would belong on the skills child, not here. Verified by Files Changed = `betty-AGENTS.md` (+ this plan) only.
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done. (N/A as symptom — this is ownership wording. Shipping a vague “Betty cares about CI” line without stating harness green + existing-scenario drift authority is also not done.)
- **Wrong fix rejected:** Rewriting `qa-child` / inventing new integration scenarios / fixing AST-988 harness red / expanding AST-915–927 coverage are out of scope. Correct fix is identity/standards prose in `betty-AGENTS.md` only.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/agents/betty-AGENTS.md` | Extend identity/standards so harness green + existing integration-scenario drift are explicit Betty ownership, parallel to test tree / bible | agents (team-chuckles) |
| `docs/features/team-chuckles/ast-991-betty-agent-integration-harness-ownership.md` | This plan | docs |

**Commit homes:** `betty-AGENTS.md` edit + commit in **`team-chuckles`** (`~/.cursor/agents/betty-AGENTS.md` is installed from that tree via `install.sh`). Plan doc only on this astral **`origin/sub/AST-989/AST-991-betty-agent-integration-harness-ownership`**.

**Out of scope (do not touch):**

- `~/team-chuckles/skills/qa-child/**` and any other Betty skill procedure (AST-992)
- Engineer skills (`build-child` / `test-child` / `resolve-child`)
- Astral `src/**`, `tests/**`, `docs/test-bible/**`, GHA workflow YAML
- AST-988 harness repair; AST-915 / AST-927 coverage expansion
- Joan `integration-operator` / Railway post-deploy skill

---

## Stage 1: Betty agent ownership wording

**Done when:** Reading `~/team-chuckles/agents/betty-AGENTS.md` alone states (1) ongoing GHA integration-harness green is Betty’s concern and (2) drift of **existing** integration scenarios is her authority parallel to the component test tree; the file still does not contain QA procedure steps (revise-vs-handoff how-to).

1. Open `~/team-chuckles/agents/betty-AGENTS.md` (source of truth; not the epic worktree `AGENTS.md`).
2. Replace the opening paragraph (currently: owns test design / manifests / `docs/test-bible/**`; engineers run via `test-child`) with this exact text:

```markdown
You are **Betty**. You own test design, manifests, and `docs/test-bible/**` (per-component test bible; Betty sole writer). You also own ongoing health of the GitHub Actions integration harness (keeping it green is your ongoing concern, not a one-off Foundation firefight) and own **integration-test drift** the same way you own the component test tree: when product work invalidates an **existing** integration scenario, that drift is your authority to notice and repair — same class of concern as a broken component test. Do **not** invent new integration coverage as this persona’s default deliverable (coverage expansion stays other epics). Engineers run tests via `test-child`.
```

3. Immediately after the **Standards** section’s existing paragraph (bible README / no product commits / engineers do not commit bible), append this exact paragraph (still under **Standards** — do not create a new top-level skill-procedure section):

```markdown
**Integration harness (ownership, not procedure):** GHA integration-harness green and drift of **existing** integration scenarios are Betty concerns parallel to the component test tree and bible. How to revise scenarios, keep the bible map honest for the integration tier, and when to return a product bug to the engineer live in `qa-child` — this agent file states **who owns** them; it does not rewrite QA skill steps.
```

4. Do **not** change **Identity**, **Workspace guard**, **Queue**, or **Out-of-scope** sections in this ticket (leave Linear MCP, worktree, publish, queue statuses, and `@susan` escalate wording as-is).
5. Do **not** edit any skill under `~/team-chuckles/skills/`.

⚠️ **Decision:** Ownership lives in the agent opening + one Standards ownership note; procedure stays out so AST-992 can own skill steps without rewriting identity again.

---

## Stage 2: Install verify + team-chuckles commit

**Done when:** Host install surfaces the new wording under `~/.cursor/agents/betty-AGENTS.md`, and the change is committed on `team-chuckles` `main` (or the branch build-child uses for that repo — follow existing Team Chuckles commit habit: commit only `agents/betty-AGENTS.md`).

1. From `~/team-chuckles`, run `./install.sh` (or confirm `link_tree agents` already links `betty-AGENTS.md` so a re-link refreshes `~/.cursor/agents/betty-AGENTS.md`).
2. Confirm by read: `~/.cursor/agents/betty-AGENTS.md` contains both “GitHub Actions integration harness” and “existing integration scenario” (or the exact phrases from Stage 1).
3. Confirm by grep that `~/team-chuckles/skills/qa-child/SKILL.md` was **not** modified in this ticket’s working tree.
4. Commit in **`team-chuckles`** only `agents/betty-AGENTS.md`:

   `code(AST-991): Betty agent owns GHA integration harness drift`

5. Code Complete note for Chuckles/hosts: re-run `./install.sh` (or agents link) so seeded Betty sessions see the update. Epic worktree `AGENTS.md` for engineer handoffs is unrelated — do not seed Betty persona into engineer epic trees for this ticket.

---

## Execution contract

- This ticket only — AST-991 agent identity/standards.
- Literal Stage 1 text; if `betty-AGENTS.md` structure has drifted (no opening paragraph / no Standards section), stop and comment on **AST-991** (not parent).
- No Astral product behavior change; no GHA YAML; no test-tree edits.
- Plan doc stays on astral publish ref; agent file commits on `team-chuckles`.

## Self-Assessment

**Scope:** `minor` — one Betty persona markdown file in team-chuckles plus this plan doc.

**Conf:** `high` — target file is short and known; AC maps 1:1 to opening + Standards ownership note; sibling skills explicitly excluded.

**Risk:** `low` — docs-only persona wording; worst case Betty identity under- or over-claims until AST-992 adds procedure, with no product runtime impact.

## Self-review vs ASTRAL_CODE_RULES

- §1.1 in-scope only — satisfied (betty-AGENTS.md + plan; no `src/` / `tests/` / skills).
- No config / batch / state-machine / import / naming statutes apply to persona markdown.
- Boundaries match parent: no AST-988 fix, no new coverage, no second QA persona.

## Review (build stub)

**Publish ref:** `origin/sub/AST-989/AST-991-betty-agent-integration-harness-ownership`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `2f7dafa` | Plan doc on astral sub |
| 1–2 | `team-chuckles@8570636` | `betty-AGENTS.md` harness green + existing integration-scenario drift ownership; install verified; qa-child untouched |

**Built:** `~/team-chuckles/agents/betty-AGENTS.md` — identity/standards ownership only; no skill procedure.
**Tip:** astral plan + stub (this commit); agent on `team-chuckles` `main` @ `8570636`.
