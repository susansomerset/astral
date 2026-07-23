# AST-919 — Joan persona — statute validator AGENTS + handoff

- **Linear:** [AST-919](https://linear.app/astralcareermatch/issue/AST-919/joan-persona-statute-validator-agents-handoff-agent-roles-joan-reborn)
- **Parent:** [AST-910](https://linear.app/astralcareermatch/issue/AST-910/agent-roles-joan-reborn-as-statute-validator-archie-identity)
- **Publish ref:** `origin/sub/AST-910/AST-919-joan-persona-statute-validator`
- **Summary:** Land Joan as the statute-validator persona in team-chuckles: `joan-AGENTS.md`, handoff/seed wiring at plan-validation touchpoints, Linear/Cursor `linear-joan` identity, per-child assignee + scoped prompts, considered-and-excluded comment artifact shape, and a single global Joan thread with context-size reporting gated by `MAX_JOAN_CONTEXT`. Does **not** own Archie identity (AST-922), Todo-grab (AST-958), statute authoring (AST-912/920), or plan-rubric content (AST-916/928).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/agents/joan-AGENTS.md` | **New** Joan persona (domain, never-list, Linear identity, context-size footer, skills) | agents |
| `~/team-chuckles/agents/handoff-table.md` | Plan Ready / Plan Discuss rows when assignee is Joan → `joan-AGENTS.md`; assignee→file map + no pre-commit hook | agents |
| `~/team-chuckles/agents/chuckles-AGENTS.md` | Add Joan to Team table; Chuckles **spawns** Joan for validate-plan (no longer Joan actor) | agents |
| `~/team-chuckles/skills/seed-agents-md/SKILL.md` | Joan assignee → seed `joan-AGENTS.md`; **no** pre-commit hook install for Joan | skill |
| `~/team-chuckles/skills/validate-plan/SKILL.md` | Who = Joan (`linear-joan`); assignee flips; statute eval + considered-and-excluded section; context footer; retire “Chuckles Joan actor until AST-910” | skill |
| `~/team-chuckles/skills/do-all-the-things/SKILL.md` | Steps 3/5: spawn/resume **global Joan** thread (not inline Chuckles validate-plan); `MAX_JOAN_CONTEXT` replace procedure | skill |
| `~/team-chuckles/skills/orientation/SKILL.md` | Joan on roster; confirm never-list (no git / no product / no `git-store-*`); skill-index Joan row | skill |
| `~/team-chuckles/skills/plan-child/SKILL.md` | Plan Discuss reply path: Joan (not “Chuckles validate-plan”) posts concerns; engineer reply unchanged | skill |
| `~/team-chuckles/config/joan.json` | **New** tracked config: `MAX_JOAN_CONTEXT` (tokens) | config |
| `~/team-chuckles/docs/UBUNTU_SETUP.md` | `LINEAR_KEY_JOAN` row | docs |
| `~/team-chuckles/scripts/export-chuckles-env.sh` | Export `LINEAR_KEY_JOAN` in the key list | scripts |
| `~/team-chuckles/scripts/setup-server.sh` | Comment/template line for `LINEAR_KEY_JOAN=` | scripts |
| `~/team-chuckles/docs/linear-state-consumers.md` | Handoff / seed / validate-plan / datt inventory notes for Joan assignee at Plan Ready / Plan Discuss | docs |
| `~/.cursor/mcp.json` | Add `linear-joan` MCP server block (host-local; both Mac + chuckles hosts) | host config |
| `docs/ASTRAL_TEAM_WORKFLOW.md` | Plan Ready / Plan Discuss actor → Joan (statute validator); Chuckles spawns | astral docs |
| `docs/features/team-chuckles/ast-919-joan-persona-statute-validator.md` | This plan | astral docs |

**Commit homes:** team-chuckles edits on **`team-chuckles` `main`**; astral law doc + this plan on **`origin/sub/AST-910/AST-919-joan-persona-statute-validator`**. Same split as AST-933 / AST-924.

**Out of scope (do not touch):**

- Archie identity table / public-name sweep (**AST-922**).
- Todo-grab assignee Chuckles (**AST-958**).
- Statute corpus authoring / schema (**AST-912** / **AST-920** / **AST-921**) — Joan may **cite** `canon/statutes/**` when present.
- Plan-rubric scoring content / Review Rubrics (**AST-916** / **AST-928**).
- Plan Discuss *state machine* redesign (**AST-924** already shipped) — only replace Chuckles-as-Joan actor with real Joan + assignee flips named below.
- Product `src/**`, `tests/**`, astral-tests.
- Reviving `git-store-*` / `JOAN_SESSION` / Joan git authority (forbidden).

**Ops prerequisite (not code):** Linear user **Joan Clarke** (`susan+joan@susansomerset.com`, displayName `joan`) already exists. Cursor-team membership for Joan + `LINEAR_KEY_JOAN` API key must exist on Mac + chuckles host before end-to-end assignment/MCP works. If missing at build/test time: Linear comment `@susan` ops; do not invent a fake key.

---

## Binding decisions (planner — do not re-litigate in build)

⚠️ **Decision — Override AST-924 “never assign Joan”:** AST-910 AC requires children **can be assigned to Linear Joan** for per-child statute evaluation. At validate-plan entry (Plan Ready or Joan’s turn on Plan Discuss), Chuckles **assigns the child to Joan**, seeds `joan-AGENTS.md`, then spawns/resumes Joan. After Joan’s pass, assignee returns to the **implementing engineer** (or Susan on Archie escalate) per the transition table below. Engineer Plan Discuss **reply** always runs with engineer assignee (unchanged).

⚠️ **Decision — Global Joan thread (not Team-table row):** One host-local session file `~/.config/team-chuckles/joan-session.json` with shape `{"thread_uuid":"<cursor-chat-uuid>"}`. **Not** parent Description `## Team` (that table stays engineer/Betty/Radia). Single shared Joan conversation across children; each spawn prompt still scopes Joan to **one child id**.

⚠️ **Decision — Context gate:** Tracked `~/team-chuckles/config/joan.json`:

```json
{
  "MAX_JOAN_CONTEXT": 120000,
  "unit": "tokens"
}
```

Joan reports `context_tokens≈N` on every Linear comment she posts (and on skill stdout). **Chuckles** (orchestrator), before the **next** Joan `--resume`, reads the latest Joan-reported `N` from the child’s thread (or session footer). If `N > MAX_JOAN_CONTEXT`: `agent create-chat` → write new UUID to `joan-session.json` → first-spawn Joan on the new thread (do **not** `--resume` the oversized UUID). Context-size reset only — no calendar rotation.

⚠️ **Decision — datt steps 3/5 become Joan spawns:** Replace “Chuckles runs validate-plan inline” with headless `agent -p … --resume "${JOAN_THREAD}"` (after transcript-exists gate + context gate). Chuckles still **owns** the orchestration step (assign, seed, spawn, wait, read outcome); Joan owns the adversarial review body.

⚠️ **Decision — Rubric content stays thin here:** validate-plan keeps the existing adversarial checklist. Add a required **Considered and excluded** comment section listing statute ids under `canon/statutes/**` that Joan selected vs skipped (one-line reason each). Full scoring rubrics = AST-916/928 — do not invent grade vectors here. If the corpus directory is empty/missing, Joan posts `considered: (none — corpus not present)` and still runs the existing checklist.

⚠️ **Decision — No Joan pre-commit hook:** Joan never commits product or team-chuckles from the epic worktree during validate-plan. `seed-agents-md` copies `joan-AGENTS.md` only; skips `install-hook.sh`.

---

## Assignee / state transitions (Joan identity — binding)

| From → To | Who moves | Assignee after move |
|-----------|-----------|---------------------|
| (enter validate-plan on Plan Ready / Plan Discuss) | Chuckles | → **Joan** (then spawn) |
| Plan Ready → Plan Approved | Joan | → implementing engineer |
| Plan Ready → Plan Discuss (REVISE) | Joan | → implementing engineer |
| Plan Ready → Plan Ready (ESCALATE) | Joan | → Susan |
| Plan Discuss → Plan Approved | Joan | → implementing engineer |
| Plan Discuss → Plan Discuss (REVISE, rounds &lt; 2) | Joan | → implementing engineer |
| Plan Discuss → Plan Discuss + Archie escalate | Joan | → Susan |
| Plan Discuss → Todo (REPLAN) | Joan | → implementing engineer |

Comment tags from AST-924 stay; sign Joan comments `— Joan` (not `— Chuckles`).

---

## Stage 1: Joan AGENTS + config + handoff/seed

**Done when:** `agents/joan-AGENTS.md` and `config/joan.json` exist; handoff-table + seed-agents-md map Joan assignee → that file with no hook; `install.sh`’s existing `link_tree agents` will expose `joan-AGENTS.md` under `~/.cursor/agents/` after reinstall (no install.sh logic change required unless a file is missing — verify by running install and `test -f ~/.cursor/agents/joan-AGENTS.md`).

1. Create `~/team-chuckles/config/joan.json` exactly as in the Decision above (`MAX_JOAN_CONTEXT: 120000`, `unit: "tokens"`).
2. Create `~/team-chuckles/agents/joan-AGENTS.md` with this structure (Radia-length, concrete):
   - Header: `# Joan — Statute Validator`
   - Role: adversarial plan validation + per-child statute relevance; Plan Discuss counterpart.
   - **Linear:** `linear-joan` only. `get_user` `me` → Joan (`susan+joan@susansomerset.com`) or stop.
   - **Worktree:** read-only on epic `<reponame>-<parent-id>/` (or `$ASTRAL_MAIN` for plan reads via `git show origin/<publish-ref>:…`). **Never** commit; **never** push; **never** `git-store-*` / `JOAN_SESSION`.
   - **Skills:** `validate-plan` (primary), `orientation` (read), `check-linear` only if explicitly assigned inbox work for Joan — default is validate-plan only.
   - **Domain:** statute relevance for the **single child** named in the spawn prompt; validate plan vs parent definition + `docs/ASTRAL_CODE_RULES.md` + selected statutes under `canon/statutes/**`; Plan Discuss tagged concerns; **Considered and excluded** artifact in the Linear comment.
   - **Never-list (must match orientation):** no git authority; no product `src/` edits; no test-tree edits; no revival of retired Joan git-operator paths; no sibling/parent scope beyond the named child; no Archie identity table work; no Todo-grab changes.
   - **Context footer (mandatory):** every Linear comment Joan posts ends with a final line exactly: `context_tokens≈<integer>` (her best estimate of current conversation tokens). Stdout of validate-plan also prints that line once at end.
3. Update `~/team-chuckles/agents/handoff-table.md`:
   - Status table: keep engineer rows for Plan Discuss / Plan Approved when assignee is engineer.
   - Add explicit rule: when Linear **assignee is Joan** and status is **Plan Ready** or **Plan Discuss**, seed `joan-AGENTS.md`, pre-commit hook = **none**.
   - Assignee→file map: add `| Joan | agents/joan-AGENTS.md |`.
4. Update `~/team-chuckles/skills/seed-agents-md/SKILL.md`:
   - When-list: note Chuckles assigns Joan before validate-plan spawn; seed Joan then.
   - Procedure table: Joan → `joan-AGENTS.md`, hook column `—` (skip `install-hook.sh`).
   - Never: do not seed Joan into `$ASTRAL_MAIN/AGENTS.md` (Chuckles only).
5. Update `~/team-chuckles/agents/chuckles-AGENTS.md` Team section: add Joan row (`validate-plan` / statute validator; global thread). Behavior: Chuckles spawns Joan for Plan Ready / Plan Discuss validation — Chuckles is **not** the Joan actor.

## Stage 2: validate-plan + plan-child actor flip

**Done when:** A reader of `validate-plan` alone knows Joan runs it via `linear-joan`, assignee flips per the table above, comments include Considered and excluded + `context_tokens≈N`, and “Chuckles Joan actor until AST-910” language is gone.

1. Rewrite `~/team-chuckles/skills/validate-plan/SKILL.md` frontmatter + **Who runs this** to **Joan** (`linear-joan`, email `susan+joan@susansomerset.com`). Confirm `AGENTS.md` header `# Joan — Statute Validator` when running inside an epic worktree seeded for Joan.
2. Replace identity gate: `get_user` on **`linear-joan`**, not `linear-chuckles`.
3. Keep Plan Ready / Plan Discuss gates, round-cap 2, verdict set (APPROVED / REVISE / REPLAN / ESCALATE), and AST-924 comment tags.
4. Add **§ Statute relevance (per child):**
   - Prompt/skill must name exactly one `<ticket-id>`; refuse to evaluate siblings.
   - Scan `canon/statutes/**/*.md` (skip `README.md` / `SCHEMA.md` / `AUTHORING.md` / `HARVEST.md` unless they are the only files — prefer leaf statute files). Select statutes relevant to this child’s plan Files Changed + stages; exclude the rest with reasons.
   - Comment section (required when posting findings **or** when APPROVED with notes; on APPROVED zero findings, still post a short comment that contains only Considered and excluded + context footer — **exception to** “APPROVED zero findings → no comment”, because the AC requires statute evaluation posts):

```
## Considered and excluded
**Considered:** `astral….id` — reason
**Excluded:** `orch….id` — reason
context_tokens≈12345
```

5. Wire assignee transitions from the binding table into §8 Update Linear (Joan performs `save_issue` assignee flips).
6. Sign findings `— Joan`. Remove Active-label chuckles ownership from Joan’s procedure — Chuckles retains `active_label.py` around the **spawn** in datt; Joan does not set/clear Active unless already specified for escalate paths that Chuckles owned — **keep Active management on Chuckles in datt**, not inside Joan validate-plan (avoids double-clear). Delete Joan-side `active_label.py set/clear` steps that currently sit in validate-plan; document “Chuckles owns Active around Joan spawn.”
7. In `~/team-chuckles/skills/plan-child/SKILL.md` Plan Discuss section: replace “Joan (Chuckles `validate-plan`)” with “Joan (`validate-plan`)”; engineer reply path unchanged (engineer stays assignee for reply).

## Stage 3: do-all-the-things Joan spawn + context replace

**Done when:** datt steps 3 and 5 instruct Chuckles to assign Joan, seed, gate context, `--resume` global Joan thread with a single-child scoped prompt, and wait — not run validate-plan inline.

1. In `~/team-chuckles/skills/do-all-the-things/SKILL.md`, change the “orchestrator steps … validate-plan … inline” rule: **validate-plan is a Joan headless spawn**; dispatch / prep-uat / summary remain inline Chuckles.
2. Add **§ Joan session (global)** near Team-table §3c:
   - Path: `~/.config/team-chuckles/joan-session.json`.
   - If missing/empty: `agent create-chat` → write `thread_uuid`.
   - Before every Joan `--resume`: `thread_transcript.py exists` (same as §3d); on miss → `[thread-missing]` on parent, stop (never fork).
   - Before every Joan `--resume`: read latest `context_tokens≈N` from Joan’s last comment on the **current** child if present; else treat as `0`. If `N >` `MAX_JOAN_CONTEXT` from `config/joan.json`: create-chat, overwrite session file, first-spawn template only.
3. Steps 3 and 5 procedure (per Plan Ready / Plan Discuss child in sweep order):
   1. `save_issue` assignee → Joan.
   2. `seed-agents-md` for Joan in epic worktree.
   3. Context + transcript gates.
   4. Spawn:

```bash
agent -p --trust --approve-mcps --force --model auto \
  --resume "${JOAN_THREAD}" \
  "Run ~/.cursor/skills/validate-plan/SKILL.md for <ticket-id> only. Scope: this child only — do not evaluate siblings or parent epic remainder. Epic worktree=<path>. Publish ref from parent Git table. Report context_tokens≈N on every Linear comment."
```

   5. `wait`; on completion Chuckles continues pipeline (assignee already restored by Joan per Stage 2).
4. Prompt must include the child id and the scope sentence above (AC: prompts constrain Joan to the provided child).

## Stage 4: Host identity wiring + orientation + astral workflow + consumers

**Done when:** `linear-joan` is documented and added to mcp.json; env export/setup docs list `LINEAR_KEY_JOAN`; orientation + ASTRAL_TEAM_WORKFLOW name Joan as statute validator; linear-state-consumers notes Joan handoff.

1. Append to `~/.cursor/mcp.json` (exact server block; mirror other personas):

```json
"linear-joan": {
  "command": "npx",
  "args": [
    "-y",
    "mcp-remote",
    "https://mcp.linear.app/mcp",
    "--header",
    "Authorization:Bearer ${env:LINEAR_KEY_JOAN}"
  ]
}
```

   Apply on **both** Mac and chuckles hosts (scp per UBUNTU_SETUP). Do not commit `mcp.json` into astral.
2. `docs/UBUNTU_SETUP.md`: add `LINEAR_KEY_JOAN` next to other persona keys.
3. `scripts/export-chuckles-env.sh`: include `LINEAR_KEY_JOAN` in the exported key list.
4. `scripts/setup-server.sh`: add commented `export LINEAR_KEY_JOAN=` template line beside other keys.
5. `skills/orientation/SKILL.md`: roster Joan (statute validator; `linear-joan`; never assignee long-term on build stages; validate-plan owner). Confirm **What never happens** still lists Joan/`git-store-*`/`JOAN_SESSION` as git bans (persona exists; git authority does not).
6. `docs/ASTRAL_TEAM_WORKFLOW.md` (astral publish ref): Plan Ready / Plan Discuss rows — Joan validates (Chuckles spawns); engineer remains assignee except during Joan’s validate pass.
7. `docs/linear-state-consumers.md`: update handoff-table / seed-agents-md / validate-plan / datt rows to mention Joan assignee at Plan Ready / Plan Discuss during validate pass.

## Stage 5: Grep gates + install verify

**Done when:** Grep shows no live “Chuckles (Joan actor until AST-910)” / “Never assign … Joan” contradictions in the files this ticket edits; install exposes joan AGENTS; team-chuckles commit pushed; astral plan already on publish ref.

1. From `~/team-chuckles` run:

```bash
rg -n 'Joan actor until AST-910|Never assign Chuckles/Joan|Never assign.*Joan on the child' \
  skills/validate-plan/SKILL.md skills/do-all-the-things/SKILL.md skills/plan-child/SKILL.md \
  agents/chuckles-AGENTS.md agents/handoff-table.md agents/joan-AGENTS.md
```

   Expected: **empty** (AST-924 text in other historical docs may remain only if not edited — do not expand scope to rewrite AST-924 plan docs in astral history).

2. Confirm never-list still bans git for Joan:

```bash
rg -n 'git-store|JOAN_SESSION|no git authority' agents/joan-AGENTS.md skills/orientation/SKILL.md
```

   Expected: hits are **bans** / never-list only.

3. Run `~/team-chuckles/install.sh`; `test -f ~/.cursor/agents/joan-AGENTS.md` and `test -f ~/.cursor/agents/handoff-table.md`.

4. Commit on **team-chuckles** `main` with message `code(AST-919): Joan persona statute-validator + validate-plan wiring`. Push `origin/main` for team-chuckles.

5. Astral publish ref already has this plan; Stage 4 astral `ASTRAL_TEAM_WORKFLOW.md` commit on epic worktree: `code(AST-919): Joan validates Plan Ready/Discuss` then `git push origin HEAD:sub/AST-910/AST-919-joan-persona-statute-validator`.

---

## Execution contract

- Stages in order; this ticket only.
- Do not invent Archie table, Todo-grab, or rubric grade vectors.
- Do not give Joan git publish paths.
- If `LINEAR_KEY_JOAN` or Cursor Joan membership is missing, stop with `@susan` ops on **AST-919** (not silent skip).
- If validate-plan Active-label ownership conflicts with datt after Stage 2 step 6, stop and comment on **AST-910** with Stage N blocked format — do not leave double Active clear.

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — new persona + handoff/seed + validate-plan ownership flip + datt spawn/context-gate + host MCP/env wiring across team-chuckles and a small astral workflow touch.

**Conf:** `Medium` — Linear Joan user exists and parent AC is explicit, but Cursor-team/`LINEAR_KEY_JOAN` ops and the AST-924→AST-910 assignee override need live proof at build; rubric depth correctly deferred.

**Risk:** `Medium` — wrong spawn/assignee wiring would stall Plan Ready→Approved or strand children on Joan; git never-list mistakes would reintroduce retired Joan operator paths.

## Self-review vs ASTRAL_CODE_RULES

- §1.1 in-scope only — boundaries list siblings; no `src/` / tests.
- §2.1 config — `MAX_JOAN_CONTEXT` lives in team-chuckles `config/joan.json` (ops tooling), not astral `src/utils/config.py` (correct: not product runtime).
- §3.3 / batch / state machine — N/A (no product layers).
- Orientation never-list — Joan persona must restate no git / no product / no `git-store-*`.
- Docs path `docs/features/team-chuckles/` — satisfied.

## Review (build stub)

**Publish ref:** `origin/sub/AST-910/AST-919-joan-persona-statute-validator`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `f58e718` | Plan doc on astral sub |
| 1–5 | `team-chuckles@3c26552` | Joan AGENTS + config, handoff/seed, validate-plan ownership, datt §3e, orientation/MCP/env docs |
| astral | _(this commit)_ | `ASTRAL_TEAM_WORKFLOW.md` Joan rows + this stub |

**Tip:** astral publish ref after this commit; skill deliverables on `team-chuckles` `main` @ `3c26552`.

**Ops:** `LINEAR_KEY_JOAN` not set on this host yet — `@susan` to add key + Cursor-team Joan before live validate-plan MCP works. `~/.cursor/mcp.json` already has `linear-joan` block.