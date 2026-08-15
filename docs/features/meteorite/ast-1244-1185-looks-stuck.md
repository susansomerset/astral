# AST-1244 — 1185 looks stuck.

<!-- linear-archive: AST-1244 archived 2026-08-14 -->

## Linear archive (AST-1244)

**Archived:** 2026-08-14  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1244/1185-looks-stuck  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1215; related: AST-1182; related: AST-1214; related: AST-1183; related: AST-1185; related: AST-1184

### Description

## Execution plan

Unstick parent **AST-1185** (In Progress, assignee Susan, label `stuck-mcp`). Blockers **AST-1183** / **AST-1184** are already User Testing. Wave stopped on child **AST-1214** (Plan Discuss, Joan `[plan-discuss] escalate`, assignee Susan). **AST-1215** still Todo, blocked by 1214.

Archie product call (on AST-1185, 2026-08-07) — confirmed understood:

* **Never hide** dispatch/task keys (rejects Joan option 1).
* `parse_meteorite_email` is misnamed; the live identity is the meteorite-email hop. It should be a **candidate** entity: available-count = Astral Gmail ping; when messages exist for the candidate on the `dispatch_task` row, load them into live content and send to Ruth. Not a separate forever-orphan from that hop.
* Further rename target: `catch_meteorite_email`.
* Reject filled-form-then-400 for that key (rejects Joan option 3).

Archie answers on this Task (folded in):

* `catch_meteorite_email` **naming:** treat as a **fix on the original rename ticket** (AST-1182 / gaze_email→meteorite-email rename path) — do not open a new discussion epic or burn another plan-discuss loop.
* **Candidate entity + Gmail available-count:** Archie expects this already on Scheduled Actions — **no new product code** for that behavior under this unstick; only catalog/picker honesty so we do not ship a silent eighth dead-end key.

When this Task moves Todo → Chuckles implements:

1. Comment on **AST-1185** confirming the call above; clear the open escalate path.
2. On **AST-1214**: post Archie disposition (no hide; no ship-400; eighth key = rename+honesty via the AST-1182 fix path, not admin-hidden / not dead-end picker). Restore implementer **Ada**. Ada revises plan (eight-key Done-when + Betty contract) and re-queues Joan validate-plan.
3. File/land the `catch_meteorite_email` rename as a **fix on AST-1182** (or its child rename tip) — not a new define/datt epic. Keep AST-1214 scoped to Admin catalog/API honesty only (do not absorb mailbox redesign).
4. Reassign parent **AST-1185** → Chuckles (Archie unblock for datt). Do **not** re-set Active/chuckles. Clear `stuck-mcp` once the wave can run.
5. Resume **do-all-the-things** / datt on AST-1185: AST-1214 plan revise → Joan → build; then AST-1215; merge-child / prep-uat when children reach User Testing.

## Done when

* AST-1214 has an Archie-resolved escalate comment and is no longer stalled on Susan for Joan’s three options.
* AST-1185 assignee is Chuckles and the datt/wave path can run again without the Plan Discuss escalate gate.
* This Task can move Done (or User Testing only if Archie wants a verify pass).

## Risks / open questions

* none — Archie closed the rename-ownership and available-count questions on this Task.

---

## Original brief

Please tell me what we need to do to unstick it, now that I have addressed the confusion.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
