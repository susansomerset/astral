# AST-1282 — parse_meteorite_email failing

<!-- linear-archive: AST-1282 archived 2026-08-19 -->

## Linear archive (AST-1282)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1282/parse-meteorite-email-failing  
**Status at archive:** Archive  
**Project:** Astral Meteorite  
**Assignee:** cursorapp  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

```
dispatcher._dispatch_one index 1/1 parse_meteorite_email -> task start
 | candidate_id=somerset available_count=0 entity_batch_id=parse_meteorite_email-338076bd-39d1-4dbc-a470-ae760bfb6373 mode=CLICK run_next_chain=False entity_type='candidate' trigger_state=None
Dispatching parse_meteorite_email — 0 available, batch parse_meteorite_email-338076bd-39d1-4dbc-a470-ae760bfb6373
dispatcher._run_dispatch_loop index 1/1 parse_meteorite_email -> skipped — below min_count
 | available=0 effective_min=1 is_auto=False
Skipping parse_meteorite_email: 0 available (min_count=1)
[parse_meteorite_email] thread exited and cleared from registry
127.0.0.1 - - [08/Aug/2026 11:18:16] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
127.0.0.1 - - [08/Aug/2026 11:18:16] "GET /api/admin/scheduler/thread_status HTTP/1.1" 200 -
```

The Avail count is 2 on the scheduled_actions screen.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
