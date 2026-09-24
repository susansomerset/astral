# AST-1738 — Manage Candidates Slack username dropdown shows no users

<!-- linear-archive: AST-1738 archived 2026-09-24 -->

## Linear archive (AST-1738)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1738/manage-candidates-slack-username-dropdown-shows-no-users  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** hedy  
**Priority / estimate:** None / —  
**Parent:** AST-1636 — Bind new Slack contacts to existing candidates by metadata before creating a prospect  
**Blocked by / blocks / related:** parent: AST-1636

### Description

## Susan report (verbatim)

\[bug\] When I open the Manage Candidate modal, when I click on the Slack username dropdown, I expect to see a list of all users on the astral slack workspace, but I don't see any. Thus, I am unable to assign known users to their candidate records.

## As-is

On Manage Candidates add/edit, the Slack username dropdown opens empty — no selectable Slack users — so known workspace users cannot be bound to candidate records.

## To-be

The Slack username dropdown lists the unbound Slack users available for binding (workspace members/guests not already on a candidate) so an admin can assign a known Slack identity to the candidate.

## Suggested engineer

Hedy Lamarr ([AST-1668](https://linear.app/astralcareermatch/issue/AST-1668/contact-unbound-list-knownunknown-resolve-bind-new-slack-contacts-to) unbound list + admin GET; empty dropdown most likely empty/failed pool from Contact API — Katherine [AST-1669](https://linear.app/astralcareermatch/issue/AST-1669/manage-candidates-slack-bind-dropdown-bind-new-slack-contacts-to) owns the dropdown UI surface if the GET is fine).

## Parent

[AST-1636](https://linear.app/astralcareermatch/issue/AST-1636/bind-new-slack-contacts-to-existing-candidates-by-metadata-before)

## Proposed change (make-fix)

- [X] `src/external/slack.py` — `list_workspace_members()` via paginated `users.list` (humans only; bots/deleted excluded)
- [X] `src/core/contact.py` — `list_unbound_slack_users` calls members, not posters; same bind filter
- [X] Unbound GET shape / `@require_admin` unchanged; no Manage Candidates UI change

## QA test manifest

1. **\[bug-repro\]** `tests/component/core/test_contact.py::TestAst1738UnboundMembersNotPosters`
2. Revised filter stub: `tests/component/core/test_contact.py::TestAst1668UnboundAndRecognition::test_list_unbound_omits_bound_ids`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_contact.py::TestAst1738UnboundMembersNotPosters \
  tests/component/core/test_contact.py::TestAst1668UnboundAndRecognition::test_list_unbound_omits_bound_ids \
  -q
```

**Pass criterion (test-fix):** repro red→green after make-fix; revised filter stays green.

**Bible shasum:** `docs/test-bible/core/contact.md` — `8d36d4b3acdff08b04751171a17fff9cf872c7d2`

### Comments

#### radia — 2026-09-21T00:33:03.101Z
[code-rubric] PROCEED (Commit: 60c2c4f2) unbound members fix clean

#### betty — 2026-09-21T00:28:00.324Z
[bug-repro]
`origin/sub/AST-1636/AST-1738-manage-candidates-slack-dropdown-empty` @ `019123b5` · repro lands red, awaits fix

#### betty — 2026-09-21T00:25:08.671Z
[board-betty] TESTS: REVISE
What: docs/test-bible/core/contact.md — broken test — TestAst1668UnboundAndRecognition stubs list_workspace_posters; missing members helper + empty-poster≠empty-unbound repro

#### hedy — 2026-09-21T00:23:46.323Z
`origin/sub/AST-1636/AST-1738-manage-candidates-slack-dropdown-empty` @ `ca9133de33c172c1c8e1afc34b3e9eb964bda15a` · unbound members plan

---

_Implementation detail may live in git history on `origin/dev`._
