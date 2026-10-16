# AST-2185 — Unblock AST-2177: provider spike API keys (ASTRAL_SPIKE_KEY_*) or OK to reorder stages

<!-- linear-archive: AST-2185 archived 2026-10-16 -->

## Linear archive (AST-2185)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2185/unblock-ast-2177-provider-spike-api-keys-astral-spike-key-or-ok-to  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-2172; blocks: AST-2177

### Description

[AST-2177](https://linear.app/astralcareermatch/issue/AST-2177) can't start building until its first step runs: a provider spike that checks which grader models support forced structured output. That script calls four providers directly and reads its keys from environment variables. None of the four are set where the agents run, and the local database has no real provider keys to use in their place.

**Needed (choose one):**

1. Export these four variables in the environment the build agent launches from: `ASTRAL_SPIKE_KEY_OPENROUTER`, `ASTRAL_SPIKE_KEY_KIMI`, `ASTRAL_SPIKE_KEY_DEEPSEEK`, `ASTRAL_SPIKE_KEY_ANTHROPIC`. Ada then runs the spike first.
2. Run the spike yourself with the keys set: `cd ~/astral-AST-2172 && python3 debug/spikes/AST-2177/spike_tool_choice.py`. Ada continues from the `debug/spikes/AST-2177/results.json` it writes.
3. Reply "OK stages 2–3 first". Ada builds the config text and the nine prompt rows first, since neither needs the spike, and the capability values from the spike land last. This changes the order in the approved plan.

Reply here. You don't need to push anything. Move this ticket to **Done** when the keys or answer are in, and the pipeline resumes on its own.

Neither AST-2177 nor the parent [AST-2172](https://linear.app/astralcareermatch/issue/AST-2172) is assigned to you. AST-2177 stays with Ada, and both tickets are blocked by this one.

### Comments

#### susan — 2026-10-13T00:08:17.085Z
No. Just use existing keys.

---

_Implementation detail may live in git history on `origin/dev`._
