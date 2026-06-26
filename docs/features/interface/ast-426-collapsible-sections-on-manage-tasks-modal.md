# AST-426 — Collapsible sections on Manage Tasks Modal

<!-- linear-archive: AST-426 archived 2026-06-15 -->

## Linear archive (AST-426)

**Archived:** 2026-06-15  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-426/collapsible-sections-on-manage-tasks-modal  
**Status at archive:** Done  
**Project:** Astral Interface  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

When information is presented in sections as they are on the manage tasks modals, those sections must also support zero expanded sections.  

We had an issue on the criteria screens, but it is appearing again on the modals.

Please verify that the component used is consistent/inheriting for those two styles of use, and both support zero expanded sections.

### Comments

#### chuckles — 2026-05-17T22:22:50.953Z
**finish-up follow-up:** **AST-427** moved to **PR Ready** (Katherine stays assignee). Workflow updated — **finish-up** always moves children to **PR Ready** with the parent, not only the parent ticket.

— Chuckles

#### chuckles — 2026-05-17T22:20:45.790Z
## Landed on origin/dev — Chuckles

Susan requested **finish-up** in chat (ticket was still **User Testing** on Linear — move **PR Ready** / **Done** when you are ready for board hygiene).

- Work was already on local **dev** from **prep-uat**; merge of `origin/ftr/AST-426-collapsible-sections-on-manage-tasks-modal` was **up to date**
- Pushed **`origin/dev`** → `29f863ac` (includes **AST-427** rollup via parent merge)
- Deleted **`origin/ftr/AST-426-collapsible-sections-on-manage-tasks-modal`**

**AST-427** child branch was already removed at prep-uat.

— Chuckles

#### chuckles — 2026-05-17T22:19:11.788Z
## UAT Ready — Chuckles

All **1** child branch merged into parent branch; child branch deleted.

**Parent branch:** `origin/ftr/AST-426-collapsible-sections-on-manage-tasks-modal`

**Merged in order:**
1. **AST-427** — Collapsible sections on Manage Tasks Modal: zero expanded sections (`sub/AST-426/AST-427-collapsible-sections-on-manage-tasks-modal` — **deleted**)

**Verify on parent:** merge `f8b2e7ce`, AST-427 feat `0329f7a1` and downstream docs/tests.

**Local `dev`:** merged (prep-uat §8). Restart the app if it is running, then test Manage Tasks — edit modal should allow all prompt panels collapsed.

If testing fails on `dev`:
```bash
git reset --hard origin/dev
```

— Chuckles

#### chuckles — 2026-05-17T21:31:41.359Z
## Dispatch — Chuckles

Dispatched **1** child ticket from approved bug **AST-426**.

| Ticket | Title | Assigned to | Branch | Blocked by |
|--------|-------|-------------|--------|------------|
| AST-427 | Collapsible sections: zero expanded sections | Katherine | ftr/AST-427 | — |

**Assignment rationale:**
- **Katherine:** React UI — `CollapsiblePanel` / Manage Tasks modal (`AdminTaskPrompts.tsx`) vs criteria consumers; align behavior for zero expanded sections.

Parent → **In Progress**, assignee **Chuckles** (coordination). Implementation on **AST-427**.

**Git (authoritative — ignore Linear `gitBranchName`):**
- Parent: `origin/ftr/AST-426`
- Child: `origin/ftr/AST-427`

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
