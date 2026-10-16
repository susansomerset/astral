# AST-2055 — Contact Estelle can currently add a meteorite directly to the job table

<!-- linear-archive: AST-2055 archived 2026-10-16 -->

## Linear archive (AST-2055)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2055/contact-estelle-can-currently-add-a-meteorite-directly-to-the-job  
**Status at archive:** Archive  
**Project:** Astral Contact  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Please make sure Estelle can only add meteorites, rather than using the old meteorite ingress path directly to job.

## As-is

Estelle has a contact-task markup verb, `~~/create_contact_meteorite <url or text>~~` (registered in `CONTACT_TASK_CONFIG["create_contact_meteorite"]` in `src/utils/config.py`, and listed for her in every turn prompt under "Available contact tasks"). Its handler is `src.core.meteorite.create_contact_meteorite`. That function scrapes the link with gazer, or takes pasted text, and then calls `create_meteorite_job`. `create_meteorite_job` **writes a** `job` **row immediately**, so the meteorite stage and land pipeline never runs. This is the old AST-1517 ingress path, still live alongside the new AST-2032 path (`@Estelle /add-job` → `insert_slack_meteorite`, which writes a raw `NEW` meteorite).

Checked against the access rules in To-be, this is what Contact Estelle can do today (`origin/dev` `2fd5c63e7`):

| \# | Surface | Path | Touches | Rule |
| -- | -- | -- | -- | -- |
| 1 | `create_contact_meteorite` task | `CONTACT_TASK_CONFIG` → `create_meteorite_job` | **writes** `job` | ❌ violates (this bug) |
| 2 | `save_candidate_profile` / `save_candidate_contact` skills | `CONTACT_CONFIG["skills"]` → `run_contact_skill` → `save_candidate_data` | **writes** `candidate` (name, contact.\*) | ❌ violates (candidate is read-only) |
| 3 | `/add-job` command | `insert_slack_meteorite` | inserts `meteorite` (NEW) | ✅ allowed, but stores raw text (only Slack link unwrap) |
| 4 | `land_calls` in her turn output | `contact_land_meteorite` → `stage_meteorite` | inserts `meteorite` rows | ✅ allowed, but stores raw text |
| 5 | BOT_BLOCKED paste recovery | `try_meteorite_apply_paste_from_slack` / `land_calls` → `apply_paste` | updates `meteorite.content` | ✅ allowed, but stores raw candidate paste |
| 6 | `get_job_by_pattern` / `get_job_data` / `get_company_data` / `get_candidate_data` tasks | `src.core.tracker` | reads | ✅ read-only |
| 7 | `gazer_scrape` task | `src.core.gazer` | external fetch, no platform write | ✅ |
| 8 | Channel gate | `_handle_slack_event_body` | `message` is DM-only; `app_mention` (including `/add-job`) is accepted in **any** channel, public included | ⚠️ To-be says private channel |

No sanitization library exists in the backend today (`requirements.txt` has `beautifulsoup4`, which is a parser, not a sanitizer). No Contact path writes artifact or `rubric_vector` content today.

## To-be

Contact Estelle's platform access is a pinhole:

* **Write:** `meteorite` (insert, plus the existing BOT_BLOCKED → READY content update), artifact table content, and `rubric_vector` content (versioned content). Never `job`.
* **Read-only:** `job`, `company`, `candidate`, `agent_data`.
* **Sanitized:** anything she sends to be saved to the platform, whether it comes from her or from a candidate paste, goes through a **best-practice sanitization library, not homegrown code**.
* **Private channel:** she acts in DMs and private channels only (per the original brief: "a NEW state record in meteorite with sanitized data from the Slack user in a private channel").

Susan's words: "She can only add to the meteorite table, not to the job table. She has read-only access to job, company, candidate, agent_data. She has write access to artifact table content and rubric_vector content (because that content is versioned). Anything she sends to be saved to the platform (either by her or by a candidate paste) must pipe through a best-practice sanitization library, not a homegrown option."

## Proposed steps

1. **Close the** `job` **leak:** remove `create_contact_meteorite` from `CONTACT_TASK_CONFIG`, and delete the function with its AST-1517 docstring index line. `create_meteorite_job` stays, because gazer's email ingress (not Contact) still uses it. The read tasks and `gazer_scrape` stay.
2. **Close the** `candidate` **write:** remove the `save_candidate_profile` / `save_candidate_contact` skills. That leaves `CONTACT_CONFIG["skills"]` empty, so drop the prompt's ACL skill section and the `skill_calls` execution from `run_contact_estelle_turn`, and adjust the skills asserts in config, including the `allowed_paths` subset assert.
3. **Sanitize with a library:** add `nh3` (Python bindings for Rust `ammonia`, the maintained successor to the deprecated `bleach`) to `requirements.txt`. Put one sanitize helper on the meteorite write side. Every Contact-originated meteorite write calls it before saving: `insert_slack_meteorite` payload, the `contact_land_meteorite` blob, and `apply_paste` text from Slack. Settings such as allowed tags (likely none, so plain text) are plan-fix's call.
4. **Private-channel gate:** in `_handle_slack_event_body`, accept `app_mention` only when the channel type is `im` or `group` (private). A public-channel mention gets no command, no turn and no save. The allowed types live in `CONTACT_CONFIG`.
5. **Keep the pinhole closed:** add an import-time assert in `config.py` that no Contact command or task handler path names `create_meteorite_job`, or any other non-read handler outside `src.core.meteorite`.
6. Betty owns the test blast radius: about 21 `create_contact_meteorite` references, plus the skills/`skill_calls` tests (AST-1071) and the `app_mention` channel tests.

**Not touched (assumptions to veto):** `resolve_slack_user` still stamps `contact.slack_username` on a bound candidate (AST-1105 identity binding). That is Contact platform code, not something Estelle sends. Agent_data rows from her turns are platform audit logging, not her writes.

## Component scope

* `requirements.txt`: modified. Adds `nh3`, the sanitization library the To-be requires.
* `src/utils/config.py`: modified. Remove `create_contact_meteorite` from `CONTACT_TASK_CONFIG`. Remove the two Contact skills and adjust their asserts. Add the allowed channel types to `CONTACT_CONFIG`. Add the pinhole assert.
* `src/core/meteorite.py`: modified. Delete `create_contact_meteorite`. Add the shared sanitize helper, and call it in `insert_slack_meteorite` and `apply_paste`.
* `src/external/slack.py`: modified. New read-only helper wrapping Slack `conversations.info`, so the private-channel gate can tell DM / private / public apart (`app_mention` events carry no `channel_type`, and modern private channels use `C…` ids like public ones). Amended at AST-2061's `[scope-gate]`.
* `src/core/contact.py`: modified. Drop the skill ACL prompt section and `skill_calls` execution. Sanitize the `contact_land_meteorite` blob. Add the private-channel gate in `_handle_slack_event_body`.

## Technical scope

* `requirements.txt`: new dependency `nh3`, pinned like its neighbors.
* `src/utils/config.py`: removed config entries (one contact task, two skills), removed or adjusted asserts that reference the deleted skills, a new `CONTACT_CONFIG` field for the allowed Slack channel types, and a new import-time assert guarding Contact handler paths.
* `src/core/meteorite.py`: deleted function `create_contact_meteorite`. New function: a sanitize helper wrapping `nh3`, so there is one library-backed sanitize point. Modified functions `insert_slack_meteorite` and `apply_paste`, which sanitize text before the write.
* `src/external/slack.py`: new function, a read-only channel-type lookup over `conversations.info` (`is_im` / `is_mpim` / `is_private`). The `_handle_slack_event_body` gate calls it for `app_mention` events and fails closed when the lookup fails. No new Slack scopes are needed (`channels:read` / `groups:read` are already granted, AST-1814).
* `src/core/contact.py`: modified function `run_contact_estelle_turn` (no skill ACL section, no `skill_calls` loop). Modified function `contact_land_meteorite` (sanitized blob into `stage_meteorite`). Modified function `_handle_slack_event_body` (channel-type gate ahead of the command intercept and the turn). `run_contact_skill` and its helpers may become dead code to delete; plan-fix's call.

## Ancestor candidates

- [X] AST-1517 — Create contact meteorite (`docs/features/contact/ast-1517-create-contact-meteorite.md`). It introduced `create_contact_meteorite` → `create_meteorite_job`, the leaking path.
- [ ] AST-1071 — Contact config ACL entity-save skills (`docs/features/contact/ast-1071-contact-config-acl-entity-save-skills.md`). It introduced the `save_candidate_*` skills that step 2 removes.
- [ ] [AST-2032](https://linear.app/astralcareermatch/issue/AST-2032/let-estelle-post-a-meteorite-from-slack) — Let Estelle post a meteorite from Slack ([AST-2034](https://linear.app/astralcareermatch/issue/AST-2034/raw-new-meteorite-insert-stage-hop-classify-let-estelle-post-a) `insert_slack_meteorite` / [AST-2035](https://linear.app/astralcareermatch/issue/AST-2035/contact-command-registry-add-job-intercept-let-estelle-post-a) `/add-job` intercept). The blessed NEW path; owner of the sanitize and channel-gate surfaces.
- [ ] AST-1631 — Describe the current scope of Astral Contact functionality as-is (`docs/features/contact/ast-1631-describe-the-current-scope-of-astral-contact-functionality-as-is.md`). The Contact surface inventory to refresh.
- [ ] AST-1515 — Contact task config markup parse dispatch (`docs/features/contact/ast-1515-contact-task-config-markup-parse-dispatch.md`). It owns `CONTACT_TASK_CONFIG` / `run_contact_task_dispatch`.
- [ ] AST-1471 / AST-1531 — Meteorite intake API contact land path (`land_calls` → `contact_land_meteorite` → `stage_meteorite`). Sanitize point for step 3.
- [ ] AST-1561 — BOT_BLOCKED Estelle recovery via `apply_paste` (`docs/features/meteorite/ast-1561-bot-blocked-estelle-recovery-apply-paste.md`). Sanitize point for step 3.
- [ ] AST-1414 — Estelle needs to be able to use our endpoints (`docs/features/contact/ast-1414-estelle-needs-to-be-able-to-use-our-endpoints.md`). This is the umbrella for Estelle's tool surface.

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
