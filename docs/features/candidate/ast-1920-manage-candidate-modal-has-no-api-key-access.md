# AST-1920 — Manage Candidate modal has no api_key access

<!-- linear-archive: AST-1920 archived 2026-10-08 -->

## Linear archive (AST-1920)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1920/manage-candidate-modal-has-no-api-key-access  
**Status at archive:** Archive  
**Project:** Astral Candidate  
**Assignee:** hedy  
**Priority / estimate:** Medium / —  
**Parent:** AST-1851 — Support OpenRouter API models for agent work  
**Blocked by / blocks / related:** parent: AST-1851; related: AST-1851

### Description

The text fields that were there for candidate api keys are now gone, adn the old values that were saved in the staging database are now gone.

---

## As-is

Opening **Manage Candidates → Edit** for a candidate shows no API key text fields at all. Keys that were saved on staging before the latest [AST-1851](https://linear.app/astralcareermatch/issue/AST-1851/support-openrouter-api-models-for-agent-work) deploy no longer show up as set.

What the code on `origin/dev` actually does ([AST-1901](https://linear.app/astralcareermatch/issue/AST-1901/candidate-keys-api-keys-json-array-of-server-key-on-the-candidate), the bug fix inside [AST-1878](https://linear.app/astralcareermatch/issue/AST-1878/agent-model-field-per-platform-candidate-keys-support-openrouter-api)):

* **The fields aren't broken. They only appear once you choose a server.** `AdminManageCandidates.tsx` renders one key field for each **stored** entry in the candidate's `api_keys` array. Below those is an **"Add API key for…"** dropdown, built from `GET /api/admin/agents/models`. A candidate with no stored keys therefore shows *zero* text fields and only that dropdown. This was AST-1901's to-be ("no four fixed slots"). The [AST-1880](https://linear.app/astralcareermatch/issue/AST-1880/admin-model-brain-pickers-per-platform-keys-invalid-on-missing-key) version showed one field per catalog server every time.
* **The old values were dropped on purpose by schema setup.** `_ensure_candidate_schema` now runs `DROP TABLE IF EXISTS candidate_key`, with no copy into `candidate.api_keys` (an AST-1497 DDL-only decision, documented in the AST-1901 patch: "keys are re-entered in Manage Candidates"). Every per-server key entered during AST-1878/1880 UAT was deleted when staging booted on the new code.
* **The pre-epic Anthropic keys are probably still in the database.** The legacy `candidate.candidate_api_key` column (AST-242) was kept in the DDL. Since AST-1878 nothing reads or writes it, so those values should still be sitting there.

## To-be

**Decided (Susan, 2026-10-01): option 1, the UI.** The Edit modal shows one API key field for **every** server in the model catalog, whether or not a key is set. Stored entries show "(set — leave blank to keep current)" with Show / Clear. Unset servers show an empty field. No server is hidden behind the "Add API key for…" dropdown, which reverses AST-1901's "no fixed slots" for the UI only. The `api_keys` array storage, the PUT contract (only changed rows, `""` = remove), and the `candidate_api_keys` hydrate contract all stay as they are.

**Out of scope (Susan, option 1 only):** recovering the dropped `candidate_key` rows, or carrying legacy `candidate_api_key` values into `api_keys`. Keys are re-entered by hand.

## Proposed steps

1. In `AdminManageCandidates.tsx`, build `keyRows` from the full `keyServers` catalog (`/api/admin/agents/models`, deduped by server, catalog order). Mark a row `stored` when the candidate's `api_keys` has that server.
2. Remove the "Add API key for…" picker, the `addedServers` state, and the unsaved-row **Remove** button. They have nothing to do once every server already has a row.
3. Save payload: send only servers whose field was typed into (set/replace) or marked Clear (`""`). Omit `api_keys` when nothing changed. Same contract as today.
4. Update the Manage Candidates entry in the frontend test bible (Betty), and the AST-1878 doc's `## Bug: AST-1901` UI note via plan-fix.

## Component scope

* `src/ui/frontend/src/pages/AdminManageCandidates.tsx`: modified. The Edit modal's key rows and the "Add API key for…" picker live here. This is the only product file.
* `docs/test-bible/frontend/pages.md`: modified (Betty). The Manage Candidates page entry describes the AST-1901 picker behavior and has to describe one field per catalog server instead.

## Technical scope

* `AdminManageCandidates.tsx`: modified component logic. The `keyRows` derivation changes from stored + added servers to the whole server catalog. The `addedServers` state, the `addableServers` picker and the unsaved-row Remove handler are deleted. The save-payload builder iterates catalog servers instead of stored + added. No API, data-layer, or type-contract change: the `Candidate.api_keys` shape `[{server, label}]` stays as it is.
* `docs/test-bible/frontend/pages.md`: a modified bible entry for the Manage Candidates modal key rows.

## Suggested engineer

Hedy (owns AST-1878 / AST-1901 on AST-1851, where the key UI and storage landed).

## Ancestor candidates

- [X] [AST-1851](https://linear.app/astralcareermatch/issue/AST-1851/support-openrouter-api-models-for-agent-work): Support OpenRouter API models for agent work. This is the **live** parent (User Testing), so the bug could be re-filed as a UAT-batch sibling instead of an orphan.
- [ ] [AST-1901](https://linear.app/astralcareermatch/issue/AST-1901/candidate-keys-api-keys-json-array-of-server-key-on-the-candidate): Candidate keys: `api_keys` JSON array, remove `candidate_key` table and fixed slots (User Testing, Hedy). This is the change that removed the fixed fields and dropped `candidate_key`. Doc: `docs/features/agent/ast-1878-agent-model-field-per-platform-candidate-keys.md` § Bug: [AST-1901](https://linear.app/astralcareermatch/issue/AST-1901/candidate-keys-api-keys-json-array-of-server-key-on-the-candidate)
- [ ] [AST-1878](https://linear.app/astralcareermatch/issue/AST-1878/agent-model-field-per-platform-candidate-keys-support-openrouter-api): Agent model field + per-platform candidate keys (User Testing, Hedy). This made the legacy `candidate_api_key` column dark and introduced `candidate_key`. Same doc.
- [ ] [AST-1880](https://linear.app/astralcareermatch/issue/AST-1880/admin-model-brain-pickers-per-platform-keys-invalid-on-missing-key): Admin model + brain pickers, per-platform keys (User Testing, Ada). This is where the one-field-per-server modal came from. Doc: `docs/features/agent/ast-1880-admin-model-pickers-platform-keys.md`
- [ ] **AST-242**: Manage Candidates API key (original single key field + `candidate_api_key` column; the ticket is archived). Doc: `docs/features/administrator/ast-242-manage-candidates-api-key.md`

### Comments

#### radia — 2026-10-01T02:19:31.822Z
[code-rubric] PROCEED (Commit: 711621d1b) catalog key fields restored

CLEAN: no fix-now, no discuss. The repro test pins the to-be and would fail on the pre-fix picker. What must still hold: OK (AST-1901 storage and PUT contract, AC 2 no literals, no plaintext, AC 12 candidate half). Advisory: staging keys still need re-entering by hand (out of scope). Full review is appended to the AST-1878 doc § Bug: AST-1920.

#### betty — 2026-10-01T02:16:54.417Z
[bug-repro]
`origin/sub/AST-1851/AST-1920-manage-candidate-key-fields` @ `74087971d` · repro lands red, awaits fix

`test_AdminManageCandidates.test.tsx`: the main CRUD test is rewritten and two AST-1920 tests are added. All 3 are red on the pre-fix tree because only stored entries render. The AST-1901 picker and Remove tests are retired. Manifest: `docs/test-bible/frontend/pages.md` § QA test manifest (AST-1920). A sim of the plan-fix change goes green (22 passed, tsc clean).

#### joan — 2026-10-01T02:15:02.004Z
[board-joan]  CANON: OK

Frontend-only (`AdminManageCandidates.tsx`). AST-1901 storage, the PUT `[{server, key}]` contract and `candidate_api_keys` are unchanged, and labels stay catalog-driven (AC 2). No statute or pattern requires the picker UI. Full findings are appended to the AST-1878 doc § Bug: AST-1920.

#### betty — 2026-10-01T02:14:42.058Z
[board-betty] TESTS: REVISE
What: docs/test-bible/frontend/pages.md § AST-1901 — broken tests + missing repro coverage — `test_AdminManageCandidates.test.tsx` asserts the picker the fix removes. The main CRUD test uses `addKeyPicker` / `pickerOptions` and a "DeepSeek API key (new)" row. "AST-1901: no keys … full picker" and "AST-1901: Remove drops an unsaved row …" assert the picker, "(new)" rows and Remove. All three break. No test covers the repro: one field per catalog server (deduped, catalog order) for `api_keys: []` and for a partial set, "(set …)" with Clear versus "(not set)" with Show only, a stored server missing from the catalog still rendered and clearable, and Save sending only changed rows as `[{server, key}]` (omitted when unchanged).

#### hedy — 2026-10-01T02:13:38.224Z
`origin/sub/AST-1851/AST-1920-manage-candidate-key-fields` @ `015f3b4ff` · one field per server

#### susan — 2026-10-01T02:10:52.325Z
reparent it.

#### chuckles — 2026-10-01T02:10:00.019Z
@susan I've narrowed the Description to option 1 (UI only, one key field per catalog server). Scope is now `AdminManageCandidates.tsx` plus the frontend test-bible page.

**Blocked on tooling, not on product.** The orphaned path has to **create** a `fix` child and add a **related** link to AST-1851. `linear_proxy.py` can't do either: it has get, save (state, assignee, description, estimate), comment, and labels, but no issue create and no relation create. I won't fall back to raw GraphQL, so no git refs have been created.

Two ways forward:

1. **Re-parent it (my pick).** Set this bug's parent to **AST-1851** in Linear, add a line `## Suggested engineer: Hedy` (or say so here), set it back to **Discussion**, and assign it to me. `bug-find` §0 then seeds `sub/AST-1851/AST-1920-…` from the live `ftr/AST-1851-support-openrouter-api-models`, and `bug-fix` runs it single-ticket into the epic that's already in UAT. No child create needed. It also avoids shipping a fix to `dev` separately from an unfinished epic.
2. **Stay orphaned.** Add `create-issue` (with `--parent`/`--project`/`--assignee`/`--label`) and `relate` to `linear_proxy.py` in team-chuckles. After that, reassign to me.

#### susan — 2026-10-01T02:07:57.328Z
At this point, just 1 is the bug (the UI).

#### chuckles — 2026-10-01T02:06:00.297Z
@susan two things before anyone touches git. Nothing has been branched, filed, or spawned yet.

**1. Which To-be?** None of options 1–4 is picked, and `## Component scope` / `## Technical scope` change with the choice: the UI only, the data carry-forward only, both, or a staging repro of the dropdown. If plan-fix gets all four, it has to guess. Reply with a number, or edit the To-be section down to the one you want.

**2. You checked AST-1851, the live parent. Do you want this as a UAT-batch sibling?** `ftr/AST-1851-support-openrouter-api-models` is still open, and so are all six of its `sub/*` branches (the epic is at User Testing). The orphaned path makes a fresh `ftr` off `dev` and finishes straight to `dev`, which would ship separately from an epic that hasn't finished UAT. The other option is to set this bug's parent to **AST-1851**, with a `## Suggested engineer` of Hedy (she owns AST-1878 and AST-1901, where both the drop and the UI change landed). It then runs as a single-ticket fix and merges into the epic's own `ftr`. I can't set `parentId` with my tooling, so it has to be set in Linear.

When both are answered, reassign to me and I'll run whichever path applies.

---

_Implementation detail may live in git history on `origin/dev`._
