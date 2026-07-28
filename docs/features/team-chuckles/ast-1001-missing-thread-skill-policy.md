# AST-1001 — Missing-thread skill policy (Decommission handling of missing thread)

- **Linear:** [AST-1001](https://linear.app/astralcareermatch/issue/AST-1001/missing-thread-skill-policy-decommission-handling-of-missing-thread)
- **Parent:** [AST-999](https://linear.app/astralcareermatch/issue/AST-999/decommission-handling-of-missing-thread)
- **Publish ref:** `origin/sub/AST-999/AST-1001-missing-thread-skill-policy`
- **Summary:** Rewrite Team Chuckles orchestration skill/docs prose so a missing local chat `store.db` for an already-recorded UUID means: document the lookup path + UUID, apply label `missing thread`, mint a new chat on this host, persist the replacement UUID in the same authoritative slot, and continue as first-spawn — not “other host / laptop / do not create-chat.” Does not edit transcript helpers or `watch_linear` (sibling AST-1002).

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/skills/do-all-the-things/SKILL.md` | Rewrite §3d miss exit, create-chat allow list, §3e Joan miss step, §6 thread-missing blocker block | docs / skill |
| `~/team-chuckles/skills/orientation/SKILL.md` | Rewrite “Thread transcripts are local only” paragraph to recover-and-continue | docs / skill |
| `~/team-chuckles/skills/rollcall/WAKE_CHEATSHEET.md` | Rewrite “Before `--resume`” row: miss → comment + label + mint + continue (not skip/never-fork) | docs / skill |
| `~/team-chuckles/agents/chuckles-AGENTS.md` | Extend Behavior bullets: miss policy + label is diagnostic (not forever-skip) | docs / agents |
| `~/team-chuckles/CHUCKLES_QUICKREF.md` | One miss-outcome line under Agent chats | docs |
| `docs/features/team-chuckles/ast-1001-missing-thread-skill-policy.md` | This plan | docs |

**Repos (sibling AST-1002 owns runtime):**

- `~/team-chuckles/skills/rollcall/thread_transcript.py`
- `~/team-chuckles/skills/rollcall/watch_linear.py`
- `~/team-chuckles/skills/rollcall/datt_trace.py` (busy path stays “never create-chat for busy”; do not touch)
- Astral product `src/`, `tests/`, `docs/test-bible/**`
- Historical plan docs under `docs/features/**` that quote old `[thread-missing]` comments
- `validate-plan/SKILL.md` (no miss-gate language today — leave alone)
- Engineer/Betty/Radia/Joan `*-AGENTS.md` (Chuckles AGENTS only per ticket list)

**Commit home:** skill/agent/quickref edits land in **`team-chuckles`** (then host `install.sh` if needed). Plan doc only on this astral **`sub/*`** ref.

**Sequencing note:** After this ticket, skill prose describes the target contract. Helpers/watcher still implement laptop-block until AST-1002. That split is intentional — do not “fix” helpers under this ticket to match the new prose.

## Binding miss contract (apply everywhere live procedure mentions a miss)

When a required chat UUID is **already recorded** (parent Thread label, parent `## Team` row, or Joan session file) and local `store.db` is absent:

1. **Comment** on the parent (or ticket the gate is acting for): state **where** the gate looked and **which** UUID was expected.
   - Parent Thread: look path = `$CHUCKLES_CHAT_ROOT/<uuid>/store.db` (name the resolved root).
   - Child Team UUID: look path = the Team glob resolution (`~/.cursor/chats/*/<uuid>/store.db` / `exists --team` path output).
   - Joan: look path for the UUID in `~/.config/team-chuckles/joan-session.json`.
2. Apply Linear label **`missing thread`** (existing label; do not invent a new name).
3. **`agent create-chat`** on this host → get a new UUID.
4. **Persist** the new UUID in the **same authoritative place** the old one lived (replace Thread UUID / Team row Thread cell / Joan session `thread_uuid`).
5. **Continue** as first-spawn / new-thread for that work (old chat history is not recovered).
6. Do **not** tell Susan to run from the laptop / other host. Do **not** instruct “do not create-chat / do not `--resume`” as the miss outcome.
7. Label **`missing thread`** is **diagnostic visibility only** after recovery — prose must not teach sticky forever-skip solely because the label remains (AST-1002 removes quiet-skip; skills must not re-teach it).

**Still forbidden / unchanged:**

- First-time Team row mint when **no** row exists yet (§3c) — keep as legitimate first `create-chat`.
- Cursor **`agent_busy` / call-wait / `[agent-busy-timeout]`** — still **never** `create-chat` for busy; still **not** `[thread-missing]`.
- Active / Thread label safety — still never `save_issue labelIds` for Active/Thread maintenance.
- Dual-host history sync — still out of scope (new thread starts fresh).

## Stage 1: `do-all-the-things` §3d + create-chat allow list

**Done when:** §3d exit **1** and the surrounding “When `create-chat` is allowed” / “Never overwrite…” lines teach recover-and-continue per the Binding miss contract; laptop-block / “do not create-chat on miss” instructions are gone from this section.

1. In `~/team-chuckles/skills/do-all-the-things/SKILL.md` §3d, keep the path table and `exists` / `path` / `exists --team` command examples (lookup mechanics unchanged).
2. Replace the Exit **1** row. New action sequence (binding):
   - Post parent comment naming look path + UUID (tag `[thread-missing]`; until AST-1002 rewrites `comment-body`, compose the comment to match the Binding miss contract — do **not** paste the old “run from Susan's MacBook / do not create-chat” wording as the required body).
   - Run `label-missing` / attach **`missing thread`**.
   - `agent create-chat` → persist replacement UUID in the authoritative slot for this gate (parent Thread vs Team row).
   - Continue as first-spawn / new-thread (`JOAN_SPAWN`-style first for that session). Do **not** clear Active solely to abandon the wave as a host mismatch; proceed with the new UUID.
   - Stdout may note recovery (e.g. `AST-PPP recovered: thread missing — minted <new-uuid>`), **not** `blocked: thread missing — run from <peer-host>`.
3. Rewrite **When `create-chat` is allowed** to include: missing local `store.db` for an **already recorded** parent/Team/Joan UUID (recover path above), in addition to §3c missing Team row and §2c throwaway drone.
4. Delete or invert the line **“Not allowed: … or missing local `store.db` for a UUID already on Linear”** so miss-for-recorded-UUID is explicitly **allowed** via recover.
5. Replace **“Never overwrite an existing Team / Thread UUID because the chat store is missing locally”** with: on miss, **do** replace the authoritative UUID with the newly minted one after comment + label (history is not portable; continuing requires a new local store).
6. Update the **Watcher (`watch_linear`)** one-liner in §3d to state the target policy: on miss → comment (deduped) + `missing thread` + mint + persist + proceed; label is not forever-skip. Note runtime lands in AST-1002 — do not edit `watch_linear.py` here.

⚠️ **Decision:** Keep `[thread-missing]` as the comment tag for visibility/dedupe continuity. Change only the **outcome** (recover vs stop), not the tag name.

## Stage 2: `do-all-the-things` §3e Joan gate + §6 blocker

**Done when:** Joan miss step and §6 “Thread transcript missing” teach the same recover path; §6 no longer lists laptop-block / do-not-create-chat as the miss outcome.

1. In §3e step 3 (“Transcript gate (§3d) on `JOAN_THREAD`…”): replace “On miss → `[thread-missing]` on parent; stop (never fork)” with: on miss → Binding miss contract (comment + label + `create-chat` → overwrite Joan session file `thread_uuid` → set `JOAN_SPAWN=first` → continue). Same pattern as the existing context-cap replace in step 4, plus miss comment/label.
2. In §6, replace the entire **“Thread transcript missing on this host”** numbered block (currently: keep Chuckles assignee, `comment-body` with MacBook `@susan`, stdout blocked, do not create-chat) with a short pointer: miss handling is **§3d recover** — not a product/Archie blocker and not “run from laptop.” Do not assign Susan for a miss alone.
3. Leave the **Cursor conversation busy** block unchanged (still do not create-chat for busy).

## Stage 3: orientation + WAKE_CHEATSHEET + AGENTS + QUICKREF

**Done when:** Grep across the five in-scope files finds no live instruction that a miss means stop / other host / do not create-chat / never fork; each file that previously taught the old gate now teaches Binding miss contract (or points at §3d).

1. In `~/team-chuckles/skills/orientation/SKILL.md`, replace the paragraph starting **“Thread transcripts are local only…”** with: transcripts are still host-local (no cross-host sync); before `--resume`, run `thread_transcript.py exists`; on miss → document look path + UUID, label `missing thread`, `create-chat`, persist replacement UUID, continue as first-spawn — **never** treat miss as “run on the other host / do not create-chat.” Point at **do-all-the-things §3d**.
2. In `~/team-chuckles/skills/rollcall/WAKE_CHEATSHEET.md`, rewrite the **Before `--resume`** table row: Missing → `[thread-missing]` comment (look path + UUID) + label `missing thread` + mint `create-chat` + persist + proceed. Explicitly drop “skip (never fork create-chat)”. Keep “Not the same as Cursor `agent_busy`”.
3. In `~/team-chuckles/agents/chuckles-AGENTS.md` Behavior:
   - Extend the **Thread chats** bullet: on miss → comment (look path + UUID) + `missing thread` + mint + persist + continue; not laptop-block.
   - Add one bullet: **`missing thread` label** = eyes-open / test awareness only after recovery — do not treat it as permanent spawn suppress in skill procedure (AST-1002 owns watcher quiet-skip removal).
4. In `~/team-chuckles/CHUCKLES_QUICKREF.md` under **Agent chats**, after the `exists` / `path` commands, add one line: miss on recorded UUID → comment look path+UUID, label `missing thread`, mint+persist, continue (see datt §3d). Do not add helper-implementation detail.

## Stage 4: Grep gate + team-chuckles commit + install note

**Done when:** Grep over the five in-scope files is clean for retired live miss vocabulary; skill commit exists on `team-chuckles`; Code Complete comment notes `install.sh`.

1. From `~/team-chuckles`, run:

```bash
rg -n -i 'do not.*create-chat|never.*create-chat|other host|run from.*laptop|MacBook.*orchestration|stop.*never fork|never fork|run from <peer|blocked: thread missing' \
  skills/do-all-the-things/SKILL.md \
  skills/orientation/SKILL.md \
  skills/rollcall/WAKE_CHEATSHEET.md \
  agents/chuckles-AGENTS.md \
  CHUCKLES_QUICKREF.md
```

2. Allowed leftovers only if clearly about **busy** (`agent_busy` / call-wait / timeout) or historical “Busy ≠ missing” contrast — not miss-outcome instructions. Zero hits for laptop/other-host miss outcomes and “never fork / do not create-chat” as miss policy.
3. Commit in **`team-chuckles`** with message shaped like `code(AST-1001): missing-thread skill policy — recover not laptop-block`. Do not commit astral product code from that repo.
4. Note in the Code Complete Linear comment: host effect requires `~/team-chuckles/install.sh` (or equivalent symlink refresh) on chuckles — commit alone does not reload `~/.cursor/skills` / agents if install copies rather than symlinks for AGENTS.
5. Do **not** edit `thread_transcript.py` / `watch_linear.py` even if grep still finds old laptop strings there — that is AST-1002.

## Execution contract

- Execute stages in order; do not expand into helper/watcher code or sibling AST-1002 scope.
- If a line is ambiguous between historical note and live procedure, stop and comment on **AST-999** with the Stage N blocked format — do not guess.
- Skill prose may describe watcher/helper behavior that AST-1002 will implement; do not implement it here.
- Plan doc commits stay on astral `origin/sub/AST-999/AST-1001-missing-thread-skill-policy` only.

## Self-Assessment

**Scope:** `Single-Component` — five Team Chuckles orchestration prose files (datt, orientation, wake cheatsheet, Chuckles AGENTS, quickref) plus this plan; no astral `src/` and no helper/watcher Python.

**Conf:** `high` — parent AST-999 and this ticket’s AC spell the miss vocabulary; current files contain the exact laptop-block / never-fork instructions to replace; sibling split with AST-1002 is explicit in the Description.

**Risk:** `Medium` — wrong prose could re-teach forever-skip or blur busy vs miss (operators/drones follow skills literally); mitigated by Binding miss contract + busy carve-out left intact + grep gate. Runtime still blocks until AST-1002, so production behavior does not flip on this ticket alone.

## Rules self-review (ASTRAL_CODE_RULES)

- §1.3 DRY: Binding miss contract stated once; stages reference it instead of inventing divergent miss flows per file.
- §2.1 / §2.4 / §2.6: N/A — no config, batch, or product state machine.
- §3.3 imports / §3.5 naming: N/A — markdown/skills only; label name `missing thread` and tag `[thread-missing]` preserved.
- §3.6 debug/spikes: N/A.
- No conflicts requiring `conf-!!-NONE`.
