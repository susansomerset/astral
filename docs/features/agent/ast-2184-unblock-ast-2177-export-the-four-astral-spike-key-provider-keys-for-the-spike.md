# AST-2184 — Unblock AST-2177: export the four ASTRAL_SPIKE_KEY_* provider keys for the spike

<!-- linear-archive: AST-2184 archived 2026-10-16 -->

## Linear archive (AST-2184)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2184/unblock-ast-2177-export-the-four-astral-spike-key-provider-keys-for  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-2172; blocks: AST-2177

### Description

**Needed:** four provider API keys available to the headless build of [AST-2177](https://linear.app/astralcareermatch/issue/AST-2177), so Ada can run the approved Stage 1 provider spike (forced `tool_choice` probes per grader model).

* `ASTRAL_SPIKE_KEY_OPENROUTER`
* `ASTRAL_SPIKE_KEY_KIMI`
* `ASTRAL_SPIKE_KEY_DEEPSEEK`
* `ASTRAL_SPIKE_KEY_ANTHROPIC`

**Why:** the local DB has no real provider keys, and the approved plan reads spike keys from env only (debug-only script under `debug/spikes/`, never committed, never read by `src/`). None of the four are set in the watcher environment today, so the build would stop at Stage 1.

**Please do not paste the keys here.** Add them as `KEY=value` lines to `~/.config/team-chuckles/env` on the chuckles host, re-run `~/.cursor/scripts/install-systemd-wake.sh` (regenerates `systemd.env`) and restart the wake service so spawned agents inherit them. Then move this ticket to **Done** — that is the only release signal.

Neither the child nor the parent is assigned to you; Ada keeps [AST-2177](https://linear.app/astralcareermatch/issue/AST-2177) and Chuckles keeps [AST-2172](https://linear.app/astralcareermatch/issue/AST-2172).

Also on the plan for your eyes (Joan discuss items, non-blocking): OpenRouter grader capability defaults to `None` (only spiked models are selectable as graders until more are spiked); `prefilter_company` rule 5 ("Match the output schema exactly…") is dropped.

### Comments

#### susan — 2026-10-13T00:07:37.230Z
No. Just use the regular keys. Don't create noise.

---

_Implementation detail may live in git history on `origin/dev`._
