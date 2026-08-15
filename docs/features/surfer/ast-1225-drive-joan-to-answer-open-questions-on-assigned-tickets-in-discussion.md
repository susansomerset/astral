# AST-1225 — Drive Joan to answer open questions on assigned tickets in discussion

<!-- linear-archive: AST-1225 archived 2026-08-14 -->

## Linear archive (AST-1225)

**Archived:** 2026-08-14  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1225/drive-joan-to-answer-open-questions-on-assigned-tickets-in-discussion  
**Status at archive:** Archive  
**Project:** Astral Surfer  
**Assignee:** chuckles  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1169; related: AST-1224

### Description

## Execution plan

1. **Mint Joan chat for** [AST-1224](https://linear.app/astralcareermatch/issue/AST-1224/joan-is-in-charge) — In `$ASTRAL_MAIN`, create a dedicated Cursor chat for Joan (not the global validate-plan session). Persist that chat UUID as the Linear **Thread** label on [AST-1224](https://linear.app/astralcareermatch/issue/AST-1224/joan-is-in-charge) (use Thread helpers / label APIs that do not wipe other labels — never `save_issue` `labelIds` / `labels` replace).
2. **Seed Joan's brief on** [AST-1224](https://linear.app/astralcareermatch/issue/AST-1224/joan-is-in-charge) — Prompt Joan (via that Thread) to: list Astral Surfer tickets currently **assignee = Joan** and **status = Discussion**; for each, read Description + open questions / Risks; write recommended answers from her own judgment as a Linear comment (signed as Joan via `linear-joan`); keep each ticket in **Discussion**; reassign each answered ticket to **Susan**.
3. **Known Discussion targets (snapshot at plan time)** — At least [AST-1167](https://linear.app/astralcareermatch/issue/AST-1167/stytch-session-in-a-browser-extension-context-validate-and-decide) (Stytch session / extension) and [AST-1169](https://linear.app/astralcareermatch/issue/AST-1169/surfer-batch-durable-worklist-state-and-batch-scoped-intake) (Surfer batch durable worklist). Re-query at implement time; do not invent scope beyond what is assigned to Joan in Discussion.
4. **Drive / wait** — Call-wait on Joan until she finishes the pass (or surfaces blockers). Chuckles does not answer the open questions himself and does not move tickets out of Discussion.
5. **Close the loop on** [AST-1225](https://linear.app/astralcareermatch/issue/AST-1225/drive-joan-to-answer-open-questions-on-assigned-tickets-in-discussion) — Comment on [AST-1225](https://linear.app/astralcareermatch/issue/AST-1225/drive-joan-to-answer-open-questions-on-assigned-tickets-in-discussion) with the Thread UUID recorded on [AST-1224](https://linear.app/astralcareermatch/issue/AST-1224/joan-is-in-charge) and the list of tickets Joan reassigned to Susan; move [AST-1225](https://linear.app/astralcareermatch/issue/AST-1225/drive-joan-to-answer-open-questions-on-assigned-tickets-in-discussion) to **Done** (or leave a one-line blocked note if Joan cannot run).

## Done when

* [AST-1224](https://linear.app/astralcareermatch/issue/AST-1224/joan-is-in-charge) has a live Thread UUID pointing at the Joan chat used for this pass.
* Every Astral Surfer ticket that was assignee Joan + Discussion at start of the pass has Joan's recommended answers posted and is reassigned to Susan, still Discussion.
* [AST-1225](https://linear.app/astralcareermatch/issue/AST-1225/drive-joan-to-answer-open-questions-on-assigned-tickets-in-discussion) is Done (or explicitly blocked with `@susan`).

## Risks / open questions

* Task skill normally bans Joan headless spawns; this Task **explicitly** overrides that for a one-shot Joan judgment pass (Susan-directed).
* Do not confuse this Thread with `~/.config/team-chuckles/joan-session.json` (validate-plan global) — [AST-1224](https://linear.app/astralcareermatch/issue/AST-1224/joan-is-in-charge) gets its own Thread per Susan.
* If Joan has zero Discussion tickets at implement time, stop and `@susan` rather than inventing work.

---

## Original brief

This is unconventional, but I want you to spawn a new chat with Joan, and record that chat UUID as a Thread label in ticket [AST-1224](https://linear.app/astralcareermatch/issue/AST-1224/joan-is-in-charge), then ask her to read the tickets assigned to her in the Discussion stage and provide answers to the open questions based on her own judgment.  Then have her reassign the tickets to me, still in Discussion, so I can see what she comes up with.

### Comments

#### chuckles — 2026-08-07T18:18:16.046Z
Joan woken on Thread `46763084-9807-437d-998e-7a45fd6f25e5`; Susan-blocker Task pattern applied — created AST-1261, AST-1262 (see AST-1224). Closing this drive ticket.

— Chuckles

#### chuckles — 2026-08-07T18:15:51.084Z
Waking Joan on Thread `46763084-9807-437d-998e-7a45fd6f25e5` for AST-1224.

— Chuckles

#### susan — 2026-08-07T18:15:00.703Z
@chuckles Please wake Joan and let her know I need her on 1224?

#### chuckles — 2026-08-07T05:49:00.244Z
Joan unblock pass complete on Thread `46763084-9807-437d-998e-7a45fd6f25e5`. Summary on AST-1224: needs Susan for AST-1194 captures (gates 1168/1171/1172/1169); handed Chuckles AST-1170, AST-1172, AST-1247. Closing this drive ticket.

— Chuckles

#### chuckles — 2026-08-07T05:16:35.174Z
[check-linear] Stuck = label `stuck-mcp` + AST-1185 wave parked on Joan Plan Discuss escalate (assignee was Susan). Product call just landed on parent — not an MCP outage from here (linear-chuckles up).

— Chuckles

#### susan — 2026-08-07T05:00:25.076Z
@chuckles Something is going wrong.  What is it?

#### chuckles — 2026-08-07T04:30:58.757Z
Kicking Joan on Thread `46763084-9807-437d-998e-7a45fd6f25e5` for new AST-1224 unblock brief.

— Chuckles

#### susan — 2026-08-07T04:10:52.579Z
@chuckles More work for poor Joan on 1224.

#### chuckles — 2026-08-07T01:33:09.529Z
Joan green-lit on AST-1224; assigned Surfer Todo set to Chuckles (except AST-1224). Closing this drive ticket.

— Chuckles

#### chuckles — 2026-08-07T01:31:03.833Z
Kicking Joan on Thread `46763084-9807-437d-998e-7a45fd6f25e5` for new AST-1224 brief (holistic re-review / green-light).

— Chuckles

#### susan — 2026-08-07T01:30:44.288Z
@chuckles Please let joan know there's new work on 1224 for her.

#### chuckles — 2026-08-07T01:26:02.064Z
Joan idle; zero Surfer Discussion left on Joan. Done-when met — closing.

— Chuckles

#### chuckles — 2026-08-07T01:25:11.500Z
Joan pass on Thread `46763084-9807-437d-998e-7a45fd6f25e5`: started AST-1224; answered + reassigned to Susan (still Discussion): AST-1167, AST-1169, AST-1171, AST-1172, AST-1173, AST-1174, AST-1187. AST-1224 remains assignee Joan (Todo). Keeping AST-1225 In Progress per your keep-open ask — say when to Done.

— Chuckles

#### chuckles — 2026-08-07T01:25:07.101Z
[check-linear] In Progress — Joan update pass done (started AST-1224; Surfer Discussion answered → Susan)

#### chuckles — 2026-08-07T01:25:06.085Z
[check-linear] In Progress — kept open for Joan

#### chuckles — 2026-08-07T01:22:09.279Z
Keeping In Progress while Joan works.

— Chuckles

#### chuckles — 2026-08-07T01:21:45.241Z
Resuming Joan on AST-1224 Thread `46763084-9807-437d-998e-7a45fd6f25e5` — Surfer tickets assigned to her, starting with AST-1224. Keeping this Task In Progress.

— Chuckles

#### susan — 2026-08-07T01:20:58.217Z
@chuckles Please ask Joan to look at the tickets assigned to her on this project for updates, starting with 1224.

#### susan — 2026-08-07T01:19:27.378Z
@chuckles Let's keep this open while Joan is still working.

#### chuckles — 2026-08-07T01:11:42.269Z
Joan Thread on AST-1224: `46763084-9807-437d-998e-7a45fd6f25e5` (dedicated; global joan-session untouched). Joan answered + reassigned to Susan (still Discussion): AST-1167, AST-1169.

— Chuckles

#### chuckles — 2026-08-07T01:07:12.256Z
[check-linear] Todo — task skill Defaults + Archie override landed; watcher Todo prompt no longer hard-bans persona/datt

#### susan — 2026-08-07T01:06:01.425Z
@chuckles Task runs should not hard-ban any action as long as they are explicitly approved by Archie (Susan) (me).  Please update the hard-ban language in the skill.

#### chuckles — 2026-08-07T01:04:19.096Z
@susan Blocked on implement: approved execution plan step 1–4 requires minting/spawning a Joan chat and call-waiting her judgment pass on Discussion tickets. This `[task]` run hard-bans Joan (and other persona) headless spawns, and MCP stays `linear-chuckles` only so I cannot act as Joan myself. Need a clear override: (A) allow Joan spawn for this Task, or (B) rewrite Done-when so Chuckles answers open questions solo / without Joan.

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
