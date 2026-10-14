# AST-2210 — Context command registry and Estelle prompts

**Linear:** [AST-2210](https://linear.app/astralcareermatch/issue/AST-2210)
**Parent:** [AST-2206](https://linear.app/astralcareermatch/issue/AST-2206) — Contact /draft-<context> skills with /save- and /show-
**Publish ref:** `origin/sub/AST-2206/AST-2210-registry-estelle-prompts`

This ticket ships all of the configuration for the epic, and no handler code. In `src/utils/config.py` it adds a suffix-keyed registry (`CONTACT_CONTEXT_COMMAND_CONFIG`) for the six context pieces. Each row maps the command suffix to its `ARTIFACT_CONFIG` key, its draft task key, and a label. The 18 `draft-` / `save-` / `show-` entries in `CONTACT_CONFIG["commands"]` are generated from that registry crossed with a per-verb template, so no command id is ever hand-listed. The ticket also adds three optional command fields (`payload_optional`, `artifact_key`, `private_channel_only`) and their asserts, two reply texts (the refusal outside private channels and the unmapped-channel reply), six draft `TASK_CONFIG` entries plus one revise entry, a draft-thread config block naming the revise task, and the pinhole amendment (Contact may write meteorites and artifact versions, nothing else). In `data/admin/agent_task.json` it adds six `principal_recruiter_estelle` draft rows, each with a **Good examples** and a **Bad examples** section (mock text that Susan edits later), and one `contact_recruiter_estelle` revise row. The config imports cleanly with all 18 commands registered. Their handlers resolve as "unavailable" until siblings #2 ([AST-2211](https://linear.app/astralcareermatch/issue/AST-2211)) and #3 ([AST-2212](https://linear.app/astralcareermatch/issue/AST-2212)) land. That is expected.

## Scope gate

The ticket's `## Scope` names two files, and every row below is one of them:

- `src/utils/config.py`: the context-command registry that generates the 18 entries, the new optional command fields and their asserts, the refusal and unmapped reply texts, the draft and revise `TASK_CONFIG` entries, the draft-thread config (revise task key), and the pinhole amendment, including correcting the AST-2061 "no write skills" comments. The module-header inventory line for `CONTACT_CONFIG` is updated to name the registry. That is documentation of the same change, in the same file.
- `data/admin/agent_task.json`: six new `principal_recruiter_estelle` draft rows and one new `contact_recruiter_estelle` revise row.

**Not in this ticket:** any handler (`src/core/candidate.py` is #2, `src/core/contact.py` is #3), the channel lookup, the history fetch, and the runner changes. The text amendment to `canon/directives/active/patt.contact.command-intercept.md` (the parent's amendments a/b/c) is also out: no `canon/` file is in this ticket's Scope. This ticket carries the **config side** of those amendments: the `payload_optional`, `artifact_key`, and `private_channel_only` fields. Who edits the canon text is Chuckles/Archie's call, not something this build does.

## Contract with siblings #2 (Hedy) and #3 (Katherine)

Config names the handler paths, so these names are fixed here, and #2 and #3 must use the same spelling.

⚠️ **Decision: handler dotted paths.**

| Verb | Handler | Owner | Pinhole kind |
|------|---------|-------|--------------|
| `show-` | `src.core.candidate.contact_command_show_context` | #2 Hedy | `read artifact` |
| `save-` | `src.core.candidate.contact_command_save_context` | #2 Hedy | `write artifact` |
| `draft-` | `src.core.contact.contact_command_draft_context` | #3 Katherine | `read artifact (LLM draft, no artifact write)` |

All six suffixes share one handler per verb. That is why the entry carries `artifact_key`: a handler cannot find "its" row by handler path the way `contact_command_check_status` does.

⚠️ **Decision: command-entry field names and meaning.**

- `payload_optional: True` is set on every `draft-` and `show-` entry. It is absent on `save-` entries, and absent means `False`. #3's runner skips the empty-payload usage short-circuit when it is `True`.
- `artifact_key: "<ARTIFACT_CONFIG key>"` is on all 18. #3's runner passes it to the handler as the keyword argument **`artifact_key=`**, alongside the existing `source_id=`, `thread_ts=`, and `debug=`.
- `private_channel_only: True` is on all 18. #3 resolves the candidate from the channel mapping and posts the refusal everywhere else.
- `reply_placement: "always_no_share"` is on `draft-` entries only, per Technical scope.

⚠️ **Decision: draft task lookup.** #3's draft handler gets `artifact_key` and finds its draft task with `CONTACT_CONTEXT_COMMAND_CONFIG`. It picks the one row whose `artifact_key` matches and reads `draft_task`. An import-time assert guarantees one artifact key per row, so that lookup is unambiguous.

⚠️ **Decision: reply text keys** (in `CONTACT_CONFIG`): `private_channel_only_reply_text` and `unmapped_channel_reply_text`.

⚠️ **Decision: task keys and response fields.**

- Draft tasks: `draft_context_strengths`, `draft_context_deal_breakers`, `draft_context_priorities`, `draft_context_ideal_day`, `draft_context_bio_summary`, `draft_context_backstory`. Response: `draft` (str, required), `note` (str, optional).
- Revise task: `contact_draft_revise`, named by `CONTACT_DRAFT_THREAD_CONFIG["revise_task_key"]`. Response: `reply` (str, required), `revised_draft` (str, optional).

**Integration note for #2 (not a change here):** this ticket's Scope adds no config text for the `/show-` "nothing saved yet" line or the `/save-` ack. If #2 wants those config-owned, that is a scope question on #2's ticket.

**Interim behavior until #2 and #3 land (on ftr only, never dev):** the current `_run_contact_command` does not read `payload_optional`. So `@Estelle /show-strengths` with no payload posts the usage reply, and `/save-strengths <text>` resolves no handler (`handler_unavailable` warning, then the hear-ack). It acts on the sender's candidate only in theory, because no handler exists to run. Nothing writes.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Header inventory line for `CONTACT_CONFIG`. New `_CONTACT_DRAFT_RESPONSE_SCHEMA`. Seven new `TASK_CONFIG` entries. New `CONTACT_CONTEXT_COMMAND_CONFIG` + asserts. New `_CONTACT_CONTEXT_COMMAND_VERBS`. Two new `CONTACT_CONFIG` reply texts + asserts. Corrected skills comment. Extended commands comment. 18 generated command entries. Command-loop asserts for the three optional fields. New `CONTACT_DRAFT_THREAD_CONFIG` + assert. Three new pinhole rows, an amended write-kind assert, and a corrected pinhole comment. Artifact-key assert after `ARTIFACT_CONFIG`. | utils |
| `data/admin/agent_task.json` | Seven appended rows (six `principal_recruiter_estelle` drafts, one `contact_recruiter_estelle` revise). | data (repo admin JSON) |

No other file is touched. `tests/` and `docs/test-bible/**` are Betty's.

## Stage 0: Baseline (no commit)

**Done when:** the baseline failure list is saved under `debug/spikes/ast-2210/`.

1. On the clean synced tree, run:

   ```bash
   mkdir -p debug/spikes/ast-2210
   python3 -m pytest tests/component/utils/test_config.py tests/component/core/test_contact.py -q -p no:cacheprovider 2>&1 | grep -E '^(FAILED|ERROR)' | sort > debug/spikes/ast-2210/baseline.txt
   wc -l debug/spikes/ast-2210/baseline.txt
   ```

   At plan time, `test_config.py` alone had 26 pre-existing failures (for example `TestAst1955PlainAgentSettings::*`). Those are not this ticket's. Stages 1–2 compare against this file.

## Stage 1: `src/utils/config.py`: registry, generated commands, fields, texts, tasks, pinhole

**Done when:** all of the following hold.

- `python3 -c "import src.utils.config"` exits 0.
- Ticket AC 1 prints exactly the 18 ids.
- Ticket AC 2's grep prints nothing.
- `python3 -c "from src.utils.config import CONTACT_CONFIG as C; e=C['commands']['draft-' + 'ideal-day']; print(e['handler'], e['payload_optional'], e['private_channel_only'], e['artifact_key'], e['reply_placement'])"` prints `src.core.contact.contact_command_draft_context True True candidate.context.ideal_day always_no_share`.
- `python3 -c "from src.utils.config import _CONTACT_PINHOLE_HANDLERS as P; print(P['src.core.candidate.contact_command_save_context'])"` prints `write artifact`.
- `/add-job` and `/check-status` entries are unchanged: `git diff` shows no `-` lines inside them.

1. **Header inventory.** In the module docstring, replace the line that starts `  CONTACT_CONFIG  — Contact listen + debug flags` with:

   ```
     CONTACT_CONFIG  — Contact listen + debug flags, Slack env-name contracts, skills ACL, Slack commands registry incl. 18 context commands generated from CONTACT_CONTEXT_COMMAND_CONFIG (AST-1066 / AST-1206 / AST-2035 / AST-2206; distinct from TASK_CONFIG)
   ```

2. **Draft response schema.** Directly after the closing `})` of `_CRAFT_RESUME_NORMALIZE_TASK_KEYS = frozenset({ … })`, add:

   ```python

   # AST-2206: shared by the six draft_context_* tasks (principal Estelle drafts one context piece).
   _CONTACT_DRAFT_RESPONSE_SCHEMA: Dict[str, Any] = {
       "draft": {"type": "str", "required": True},
       "note": {"type": "str", "required": False},
   }
   ```

3. **TASK_CONFIG entries.** Inside `TASK_CONFIG`, add these seven entries immediately after the closing `},` of the `"contact_estelle_turn": { … }` entry, before the closing `}` of `TASK_CONFIG`. ⚠️ **Decision:** no `artifact_key` on any of them. `agent.do_task` reads `TASK_CONFIG[...]["artifact_key"]` for its auto-land / craft-persist branches, and drafting must never save.

   ```python
       # AST-2206: principal Estelle drafts one candidate context piece from the Slack channel
       # history + resume/profile. Drafting never saves (no artifact_key on purpose).
       "draft_context_strengths": {
           "print_label": "Draft Context: Strengths",
           "response_format": "json",
           "response_schema": _CONTACT_DRAFT_RESPONSE_SCHEMA,
           "entity_type": None,
           "requires_candidate_key": True,
           "trigger_state": None,
           "task_type": "CRAFT",
           "agent_task": "draft_context_strengths",
       },
       "draft_context_deal_breakers": {
           "print_label": "Draft Context: Deal Breakers",
           "response_format": "json",
           "response_schema": _CONTACT_DRAFT_RESPONSE_SCHEMA,
           "entity_type": None,
           "requires_candidate_key": True,
           "trigger_state": None,
           "task_type": "CRAFT",
           "agent_task": "draft_context_deal_breakers",
       },
       "draft_context_priorities": {
           "print_label": "Draft Context: Priorities",
           "response_format": "json",
           "response_schema": _CONTACT_DRAFT_RESPONSE_SCHEMA,
           "entity_type": None,
           "requires_candidate_key": True,
           "trigger_state": None,
           "task_type": "CRAFT",
           "agent_task": "draft_context_priorities",
       },
       "draft_context_ideal_day": {
           "print_label": "Draft Context: Ideal Day",
           "response_format": "json",
           "response_schema": _CONTACT_DRAFT_RESPONSE_SCHEMA,
           "entity_type": None,
           "requires_candidate_key": True,
           "trigger_state": None,
           "task_type": "CRAFT",
           "agent_task": "draft_context_ideal_day",
       },
       "draft_context_bio_summary": {
           "print_label": "Draft Context: Bio Summary",
           "response_format": "json",
           "response_schema": _CONTACT_DRAFT_RESPONSE_SCHEMA,
           "entity_type": None,
           "requires_candidate_key": True,
           "trigger_state": None,
           "task_type": "CRAFT",
           "agent_task": "draft_context_bio_summary",
       },
       "draft_context_backstory": {
           "print_label": "Draft Context: Backstory",
           "response_format": "json",
           "response_schema": _CONTACT_DRAFT_RESPONSE_SCHEMA,
           "entity_type": None,
           "requires_candidate_key": True,
           "trigger_state": None,
           "task_type": "CRAFT",
           "agent_task": "draft_context_backstory",
       },
       # AST-2206: contact Estelle's turn in a /draft-<context> thread — prose reply, revised draft
       # only when asked. Named by CONTACT_DRAFT_THREAD_CONFIG["revise_task_key"].
       "contact_draft_revise": {
           "print_label": "Contact Draft Revise",
           "response_format": "json",
           "response_schema": {
               "reply": {"type": "str", "required": True},
               "revised_draft": {"type": "str", "required": False},
           },
           "entity_type": None,
           "requires_candidate_key": True,
           "trigger_state": None,
           "task_type": "CHAT",
           "agent_task": "contact_draft_revise",
       },
   ```

   ⚠️ **Decision:** the six draft entries are hand-listed, not generated. Technical scope lists them as "new `TASK_CONFIG` entries", and the registry's spec'd assert ("every task key is in `TASK_CONFIG`") only means something if they're declared separately. Only the 18 *command* entries must be generated (AC 2).

4. **Registry + verb template.** Directly **above** the comment block that opens `# CONTACT_CONFIG: Astral Contact / Estelle foundation (AST-1066 / AST-1043).` (the `# ----…` line before it), add:

   ```python
   # ---------------------------------------------------------------------------
   # CONTACT_CONTEXT_COMMAND_CONFIG (AST-2206): Contact context commands — /draft-, /save-,
   # /show-<suffix> for six candidate context pieces. Keyed by command suffix (the token after
   # the verb). Each row names the ARTIFACT_CONFIG key the commands act on, the TASK_CONFIG draft
   # task principal Estelle runs, and the label used in command descriptions. The 18
   # CONTACT_CONFIG["commands"] entries are generated from this block x _CONTACT_CONTEXT_COMMAND_VERBS;
   # never hand-list them. The artifact-key assert sits after ARTIFACT_CONFIG (defined later).
   # ---------------------------------------------------------------------------
   CONTACT_CONTEXT_COMMAND_CONFIG = {
       "strengths": {
           "artifact_key": "candidate.context.strengths",
           "draft_task": "draft_context_strengths",
           "label": "strengths",
       },
       "dealbreakers": {
           "artifact_key": "candidate.context.deal_breakers",
           "draft_task": "draft_context_deal_breakers",
           "label": "deal breakers",
       },
       "priorities": {
           "artifact_key": "candidate.context.priorities",
           "draft_task": "draft_context_priorities",
           "label": "priorities",
       },
       "ideal-day": {
           "artifact_key": "candidate.context.ideal_day",
           "draft_task": "draft_context_ideal_day",
           "label": "ideal day",
       },
       "bio-summary": {
           "artifact_key": "candidate.context.bio_summary",
           "draft_task": "draft_context_bio_summary",
           "label": "bio summary",
       },
       "backstory": {
           "artifact_key": "candidate.context.backstory",
           "draft_task": "draft_context_backstory",
           "label": "backstory",
       },
   }
   for _ctx_suffix, _ctx_meta in CONTACT_CONTEXT_COMMAND_CONFIG.items():
       assert _ctx_suffix.split() == [_ctx_suffix] and not _ctx_suffix.startswith("/"), _ctx_suffix
       for _field in ("artifact_key", "draft_task", "label"):
           assert isinstance(_ctx_meta.get(_field), str) and _ctx_meta[_field].strip(), (_ctx_suffix, _field)
       assert _ctx_meta["draft_task"] in TASK_CONFIG, _ctx_suffix
   # One artifact key per row — the draft handler finds its draft_task by the entry's artifact_key.
   assert len({_m["artifact_key"] for _m in CONTACT_CONTEXT_COMMAND_CONFIG.values()}) == len(
       CONTACT_CONTEXT_COMMAND_CONFIG
   )
   # Per-verb template for the generated context commands; {label} / {suffix} are filled per row.
   # draft-/show- run on an empty payload (payload_optional); save- keeps the usage reply for one.
   _CONTACT_CONTEXT_COMMAND_VERBS = {
       "draft": {
           "handler": "src.core.contact.contact_command_draft_context",
           "mode": "code",
           "description": "Draft {label} for this channel's candidate from the channel history, resume, and profile. Nothing is saved.",
           "usage_reply_text": "Usage: @Estelle /draft-{suffix}",
           "payload_optional": True,
           # The draft (and its discussion) always threads under the command message.
           "reply_placement": "always_no_share",
       },
       "save": {
           "handler": "src.core.candidate.contact_command_save_context",
           "mode": "code",
           "description": "Save the text after the command as this channel's candidate's new current {label}.",
           "usage_reply_text": "Usage: @Estelle /save-{suffix} <text>",
       },
       "show": {
           "handler": "src.core.candidate.contact_command_show_context",
           "mode": "code",
           "description": "Show this channel's candidate's currently saved {label}.",
           "usage_reply_text": "Usage: @Estelle /show-{suffix}",
           "payload_optional": True,
       },
   }

   ```

5. **Reply texts.** In `CONTACT_CONFIG`, directly after the `"unknown_recognition_reply_text": …,` line, add:

   ```python
       # AST-2206: reply to a private_channel_only command posted outside a private channel (a DM,
       # or an @mention in a public channel). Nothing else runs.
       "private_channel_only_reply_text": "I can only do that in the candidate's private channel.",
       # AST-2206: reply to a private_channel_only command in a private channel that no candidate's
       # contact.slack_channel_id names. No handler runs.
       "unmapped_channel_reply_text": "This channel isn't linked to a candidate yet.  Let's check with @susan",
   ```

6. **Skills comment.** Replace the line `    # AST-2061: Estelle has no write skills — candidate is read-only to Contact.` with:

   ```python
       # AST-2061: no Estelle write skills — this map stays empty. Contact's only writes are pinhole
       # command handlers: meteorites, and /save-<context> artifact versions (AST-2206).
   ```

7. **Commands comment.** Directly after the existing line `    # Optional reply_placement overrides thread_response for this command's replies (AST-2144).` (the last comment line above `"commands": {`), add:

   ```python
       # AST-2206 optional fields: payload_optional (an empty payload runs the handler instead of the
       # usage reply); artifact_key (handed to the handler as the artifact_key= kwarg);
       # private_channel_only (runs only in a mapped private channel, on that channel's candidate;
       # anywhere else private_channel_only_reply_text posts and nothing runs).
   ```

8. **Generated entries.** In `CONTACT_CONFIG["commands"]`, after the closing `},` of the `"check-status": { … }` entry and before the closing `},` of `"commands"`, add:

   ```python
           # AST-2206: 18 context commands generated from CONTACT_CONTEXT_COMMAND_CONFIG x verbs.
           **{
               f"{_verb}-{_suffix}": {
                   **_verb_meta,
                   "description": _verb_meta["description"].format(label=_ctx["label"]),
                   "usage_reply_text": _verb_meta["usage_reply_text"].format(suffix=_suffix),
                   "artifact_key": _ctx["artifact_key"],
                   "private_channel_only": True,
               }
               for _suffix, _ctx in CONTACT_CONTEXT_COMMAND_CONFIG.items()
               for _verb, _verb_meta in _CONTACT_CONTEXT_COMMAND_VERBS.items()
           },
   ```

9. **Reply-text asserts.** Directly after `assert isinstance(CONTACT_CONFIG["unknown_recognition_reply_text"], str) and …`, add:

   ```python
   assert isinstance(CONTACT_CONFIG["private_channel_only_reply_text"], str) and CONTACT_CONFIG["private_channel_only_reply_text"].strip()
   assert isinstance(CONTACT_CONFIG["unmapped_channel_reply_text"], str) and CONTACT_CONFIG["unmapped_channel_reply_text"].strip()
   ```

10. **Optional-field asserts.** Inside the `for _cmd_id, _cmd_meta in CONTACT_CONFIG["commands"].items():` loop, directly after the two-line `if "reply_placement" in _cmd_meta:` check and before `assert _cmd_id not in CONTACT_CONFIG["skills"], _cmd_id`, add:

    ```python
        # AST-2206: optional context-command fields.
        for _flag in ("payload_optional", "private_channel_only"):
            if _flag in _cmd_meta:
                assert isinstance(_cmd_meta[_flag], bool), (_cmd_id, _flag)
        if "artifact_key" in _cmd_meta:
            assert isinstance(_cmd_meta["artifact_key"], str) and _cmd_meta["artifact_key"].strip(), _cmd_id
    ```

11. **Draft-thread config.** Directly after `assert CONTACT_ESTELLE_CONFIG["turn_context_text_max_chars"] > 0` and before `# CONTACT_TASK_CONFIG: allowlisted Contact task keys`, add:

    ```python

    # AST-2206: Contact draft thread — an @mention reply in a thread rooted at a /draft-<context>
    # command runs this task (contact Estelle) instead of CONTACT_ESTELLE_CONFIG["task_key"].
    CONTACT_DRAFT_THREAD_CONFIG = {
        "revise_task_key": "contact_draft_revise",
    }
    assert CONTACT_DRAFT_THREAD_CONFIG["revise_task_key"] in TASK_CONFIG
    ```

12. **Pinhole.** Replace this block:

    ```python
    # AST-2061 pinhole: every Contact command/task handler must be listed here, keyed by dotted path.
    # Writes are meteorite-only (never create_meteorite_job / job / candidate); everything else reads.
    ```

    with the following. The first line must stay byte-identical: `test_pinhole_assert_rejects_job_writer` splices on that anchor and requires exactly one occurrence.

    ```python
    # AST-2061 pinhole: every Contact command/task handler must be listed here, keyed by dotted path.
    # Contact writes only meteorites ("write meteorite", src.core.meteorite.*) and artifact versions
    # ("write artifact", AST-2206) — never create_meteorite_job / job / candidate rows; the rest reads.
    ```

    Then add these three rows inside `_CONTACT_PINHOLE_HANDLERS`, after `"src.core.tracker.contact_task_get_candidate_data": "read candidate",`:

    ```python
        "src.core.candidate.contact_command_show_context": "read artifact",
        "src.core.candidate.contact_command_save_context": "write artifact",
        "src.core.contact.contact_command_draft_context": "read artifact (LLM draft, no artifact write)",
    ```

    Then replace the write-kind assert:

    ```python
    assert all(
        _h.startswith("src.core.meteorite.") for _h, _kind in _CONTACT_PINHOLE_HANDLERS.items()
        if _kind.startswith("write")
    )
    ```

    with:

    ```python
    assert all(
        (_kind.startswith("write meteorite") and _h.startswith("src.core.meteorite."))
        or _kind.startswith("write artifact")
        for _h, _kind in _CONTACT_PINHOLE_HANDLERS.items()
        if _kind.startswith("write")
    )
    ```

    Leave the following `for _h in … : assert _h in _CONTACT_PINHOLE_HANDLERS, …` loop unchanged.

13. **Artifact-key assert.** Directly after the closing `}` of `assert set(ARTIFACT_CONFIG.keys()) == { … }`, add:

    ```python
    # AST-2206: every context command acts on a registered artifact (registry defined above CONTACT_CONFIG).
    for _ctx_suffix, _ctx_meta in CONTACT_CONTEXT_COMMAND_CONFIG.items():
        assert _ctx_meta["artifact_key"] in ARTIFACT_CONFIG, _ctx_suffix
    ```

14. **Compile, lint, verify.**

    ```bash
    python3 -m py_compile src/utils/config.py
    ruff check src/utils/config.py
    python3 -c "import src.utils.config"
    python3 -c "from src.utils.config import CONTACT_CONFIG as c; print(sorted(k for k in c['commands'] if k.split('-',1)[0] in ('draft','save','show')))"
    grep -nE '"(draft|save|show)-(strengths|dealbreakers|priorities|ideal-day|bio-summary|backstory)"' src/utils/config.py
    python3 -m pytest tests/component/utils/test_config.py tests/component/core/test_contact.py -q -p no:cacheprovider 2>&1 | grep -E '^(FAILED|ERROR)' | sort > debug/spikes/ast-2210/after-stage1.txt
    comm -13 debug/spikes/ast-2210/baseline.txt debug/spikes/ast-2210/after-stage1.txt
    ```

    Compare only the lint findings on lines this stage added; pre-existing findings elsewhere in the file are not this ticket's. The `comm` output (new failures) must be **exactly** `FAILED tests/component/utils/test_config.py::TestAst2061ContactPinholeConfig::test_every_contact_handler_in_pinhole`, or empty if Betty already updated it. That test still asserts every `write` kind is under `src.core.meteorite.` (lines ~3587–3589), and the parent spec deliberately amends that rule. It is Betty's to update at `qa-child`, and ticket AC 4 is satisfied at `test-child`. Name it in the Code Complete comment. **Any other new failure → stop and comment on the parent.**

15. Commit: `git add src/utils/config.py && git commit -m "code(AST-2210): context command registry, generated commands, draft/revise tasks, pinhole"`, then `git push origin HEAD:sub/AST-2206/AST-2210-registry-estelle-prompts`.

## Stage 2: `data/admin/agent_task.json`: six draft rows, one revise row

**Done when:**

- The AC 3 check below prints `AC3 OK`.
- The row check prints `ROWS OK`.
- `git diff data/admin/agent_task.json | grep -E '^-[^-]'` prints nothing (additions only).

The file round-trips byte-identically through `json.dumps(rows, indent=2, ensure_ascii=False) + "\n"` (verified at plan time). Rows are appended by a throwaway script, so the diff is pure additions.

1. Create `debug/spikes/ast-2210/add_agent_task_rows.py` (gitignored, never committed). It:
   - loads `data/admin/agent_task.json` and asserts that re-dumping it reproduces the file text exactly (abort otherwise);
   - asserts none of the seven `task_key`s below already exist;
   - builds the seven rows from the tables and texts below, each row as `dict(sorted(row.items()))` (existing rows have alphabetically ordered keys);
   - appends them in table order and writes `json.dumps(rows, indent=2, ensure_ascii=False) + "\n"`.

   Every row has these fixed fields: `cache_prompt`, `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d`, `nocache_prompt`, `run_next` = `""`; `current` = `1`; `task_name` = the row's `task_key`; `task_group_name` = `"Contact Estelle"`; `task_group_order` = `"6000"`; `updated_at` = `"2026-10-14 20:00:00"`.

   ⚠️ **Decision:** all seven rows join the existing **Contact Estelle** group (order `6000`, where `contact_estelle_turn` is seq 1). They are only ever invoked from Contact, and grouping them keeps Manage Tasks tidy.

   | task_key | agent_id | task_seq | task_key_uuid | system_prompt | user_prompt |
   |----------|----------|----------|---------------|---------------|-------------|
   | `draft_context_strengths` | `principal_recruiter_estelle` | 2 | `96a2ed37-aaf1-4710-9df5-afece9f5609a` | DRAFT_SYSTEM | DRAFT_USER(strengths) |
   | `draft_context_deal_breakers` | `principal_recruiter_estelle` | 3 | `306927ca-f88b-485c-bcc7-3dfb2952fdde` | DRAFT_SYSTEM | DRAFT_USER(deal breakers) |
   | `draft_context_priorities` | `principal_recruiter_estelle` | 4 | `bda0b634-7a6f-4eda-a8c4-f936f31ad651` | DRAFT_SYSTEM | DRAFT_USER(priorities) |
   | `draft_context_ideal_day` | `principal_recruiter_estelle` | 5 | `a6915db1-e5d6-4eae-8ace-00434f8456ec` | DRAFT_SYSTEM | DRAFT_USER(ideal day) |
   | `draft_context_bio_summary` | `principal_recruiter_estelle` | 6 | `b4cdb83f-2414-4655-9216-2afada63d4aa` | DRAFT_SYSTEM | DRAFT_USER(bio summary) |
   | `draft_context_backstory` | `principal_recruiter_estelle` | 7 | `8dcbde8b-0d2a-4492-bf6f-64b7d9ccbd31` | DRAFT_SYSTEM | DRAFT_USER(backstory) |
   | `contact_draft_revise` | `contact_recruiter_estelle` | 8 | `27b785f5-e260-4aff-9700-60ee3427cbc3` | REVISE_SYSTEM | REVISE_USER |

2. **DRAFT_SYSTEM** (identical on all six draft rows), verbatim:

   ```text
   You are Estelle drafting one piece of a candidate's Astral context.

   Respond with ONE JSON object only (no markdown fences) using the standard two-key envelope:
   - agent_performance: status, optional failure_note, optional admin_aside
   - agent_payload: draft (required string), optional note

   agent_performance.status must be exactly one of: success | failure | concern.
   - success: you produced a draft.
   - failure: the source material is too thin to draft honestly; set failure_note, and put one plain sentence saying what is missing in agent_payload.draft.
   - concern: you drafted, but something in the material should be flagged to Astral admins; set admin_aside to one short sentence. Do NOT put the admin aside in draft or note.

   agent_payload.draft is the exact text that would be saved: plain text, no markdown headings, no JSON, no preamble such as "Here is a draft". It is posted to Slack as-is.
   agent_payload.note is optional: one or two sentences to Susan and the candidate about what you leaned on or what is missing. Omit it when there is nothing worth saying.
   ```

3. **DRAFT_USER(label)**: this skeleton, with `<TITLE>`, `<LABEL>`, `<GUIDANCE>`, `<GOOD>`, `<BAD>` replaced from the per-context section below. Verbatim:

   ```text
   ## Draft: <TITLE>

   {$SELECTED_AGENT}

   ## Source material

   The CONTENT block holds everything Astral knows about {$FIRST_NAME}: the full history of {$THEIR} private Slack channel (every top-level post and every thread reply, from {$FIRST_NAME}, Susan, and you), {$THEIR} raw resume and LinkedIn profile, {$THEIR} current profile and context, and the currently saved <LABEL> (empty when nothing is saved yet).

   Use all of it. When the channel and the resume disagree, trust what {$FIRST_NAME} said in the channel. When a saved version exists, keep what is still true and improve the rest; don't discard {$FIRST_NAME}'s own words without a reason.

   ## What <LABEL> is

   <GUIDANCE>

   ## Good examples

   <GOOD>

   ## Bad examples

   <BAD>

   ## Output

   Return the envelope only. agent_payload.draft is the <LABEL> text itself, exactly as it would be saved.
   ```

   Per-context replacements (mock examples; Susan edits them later in Manage Tasks):

   **strengths** — `<TITLE>` = `Strengths`, `<LABEL>` = `strengths`

   `<GUIDANCE>`:
   ```text
   What {$FIRST_NAME} is genuinely strong at. Four to seven short lines, one strength per line, each a specific capability with the evidence behind it. Flat text, newline-separated; no bullet characters, no JSON array. Specific beats flattering: name the kind of problem, the setting, and the proof.
   ```
   `<GOOD>`:
   ```text
   Example:
   Untangles legacy data pipelines under regulatory constraint; rebuilt a bank's KYC feed without a single missed filing.
   Translates between engineers and compliance officers so neither side has to learn the other's language.
   Stays calm and methodical when a launch is on fire; people bring her the incident nobody else wants.
   ```
   `<BAD>`:
   ```text
   - "Detail-oriented team player with excellent communication skills." Generic; it could describe anyone.
   - "Python, SQL, leadership." A skills list, not strengths; no evidence behind any of it.
   - "The best product manager in the industry." Flattery the record can't back.
   ```

   **dealbreakers** — `<TITLE>` = `Deal Breakers`, `<LABEL>` = `deal breakers`

   `<GUIDANCE>`:
   ```text
   {$FIRST_NAME}'s hard nos: the conditions under which {$THEY} would turn down an offer no matter the pay. Three to six short lines, one per line, stated plainly and concretely. Include only what {$FIRST_NAME} actually said or clearly showed; a preference is not a deal breaker.
   ```
   `<GOOD>`:
   ```text
   Example:
   No roles requiring more than two days a week in an office.
   No companies whose core product is ad-tech or gambling.
   No pure people-management roles with no hands-on work.
   ```
   `<BAD>`:
   ```text
   - "Doesn't want a toxic culture." Everyone says this; it filters nothing.
   - "Prefers a startup." A preference, not a hard no.
   - "Won't work for less than she deserves." Vague; no line a recruiter can apply.
   ```

   **priorities** — `<TITLE>` = `Priorities`, `<LABEL>` = `priorities`

   `<GUIDANCE>`:
   ```text
   What {$FIRST_NAME} is optimizing for in the next role, most important first. Three to six short lines, each a concrete thing {$THEY} want and, where the material shows it, why. Flat text, newline-separated.
   ```
   `<GOOD>`:
   ```text
   Example:
   Ownership of a product area end to end, not a slice of someone else's roadmap.
   A team that ships weekly; she burned out on eighteen-month release cycles.
   A mission in health or climate; she wants to be able to explain her work to her kids.
   ```
   `<BAD>`:
   ```text
   - "Growth, impact, and work-life balance." Buzzwords with no content.
   - "A great company with great people." Says nothing a search can use.
   - "Remote, 401k match, unlimited PTO, equity." A benefits checklist, not what drives the choice.
   ```

   **ideal-day** — `<TITLE>` = `Ideal Day`, `<LABEL>` = `ideal day`

   `<GUIDANCE>`:
   ```text
   A short sketch of {$FIRST_NAME}'s ideal workday in the next role: what {$THEY}'re doing, with whom, and in what rhythm. One paragraph of four to seven sentences, third person, present tense. Concrete activities, not adjectives.
   ```
   `<GOOD>`:
   ```text
   Example:
   Dana starts the morning with an hour of uninterrupted modeling before anyone needs her. Late morning she pairs with an engineer on why a forecast drifted. After lunch she walks a finance partner through the numbers in plain English, then spends the afternoon on next quarter's question. She logs off at six knowing which decision her work changed that day.
   ```
   `<BAD>`:
   ```text
   - "An ideal day would be productive, collaborative, and fulfilling." Adjectives, no day.
   - "9:00 email. 9:30 standup. 10:00 meetings." A calendar, not a picture of the work.
   - "Working from a beach in Bali." A fantasy, not a workday.
   ```

   **bio-summary** — `<TITLE>` = `Bio Summary`, `<LABEL>` = `bio summary`

   `<GUIDANCE>`:
   ```text
   A two-to-four sentence profile blurb for {$FIRST_NAME}'s Profile screen, in first or third person, whichever reads cleaner for this person. Who {$THEY} are professionally, what {$THEY}'re known for, and what {$THEY}'re looking for next.
   ```
   `<GOOD>`:
   ```text
   Example:
   Dana is a data scientist who turns messy operational data into forecasts finance teams actually trust. Over nine years at two logistics companies she built the demand models that set staffing for 40 warehouses. She's looking for a mission-driven team where analytics shapes decisions, not slide decks.
   ```
   `<BAD>`:
   ```text
   - "Results-driven professional with a proven track record of success." Resume filler.
   - "Dana was born in Ohio and went to State University, then..." A biography, not a profile.
   - A six-sentence paragraph. Too long; the blurb is two to four sentences.
   ```

   **backstory** — `<TITLE>` = `Backstory`, `<LABEL>` = `backstory`

   `<GUIDANCE>`:
   ```text
   {$FIRST_NAME}'s career arc as narrative: where {$THEY} came from, how {$THEY} got here, and what drives {$THEM}. Two to four short paragraphs of flat prose in third person, past to present. Keep the turning points and the reasons behind them; skip the job-by-job inventory.
   ```
   `<GOOD>`:
   ```text
   Example:
   Dana started in warehouse operations, scheduling shifts by spreadsheet and noticing how often the forecast was wrong. She taught herself Python on night shifts to fix it, and her model got her pulled onto the analytics team.

   Nine years later she leads forecasting for a regional logistics company. What still drives her is the moment a frontline manager stops guessing because the numbers finally make sense.
   ```
   `<BAD>`:
   ```text
   - "2015-2017: Ops Associate, Acme. 2017-2020: Analyst, Acme." A resume, not a story.
   - "Dana has always been passionate about data." A claim with no arc.
   - "Started in ops; learned Python; promoted." A list; backstory is prose.
   ```

4. **REVISE_SYSTEM**, verbatim:

   ```text
   You are Estelle in a Slack thread discussing your draft of one piece of a candidate's Astral context.

   Respond with ONE JSON object only (no markdown fences) using the standard two-key envelope:
   - agent_performance: status, optional failure_note, optional admin_aside
   - agent_payload: reply (required string), optional revised_draft

   agent_performance.status must be exactly one of: success | failure | concern.
   - success: the turn completed normally; admin_aside optional.
   - failure: you could not perform the turn; set failure_note.
   - concern: the user appears to be struggling or having a negative experience; set admin_aside to one short sentence for Astral admins. Do NOT put the admin aside in reply.

   User-visible text goes ONLY in agent_payload.reply and agent_payload.revised_draft. Never copy admin_aside into either.
   ```

5. **REVISE_USER**, verbatim:

   ```text
   ## Draft thread

   {$SELECTED_AGENT}

   ## Instructions

   Live content is the draft thread: which context piece is being drafted, the whole thread transcript (your original draft first, then every reply from {$FIRST_NAME}, Susan, and you), and the currently saved version of that piece. The latest message is the one that @mentioned you.

   Answer it the way you would in conversation: short, natural prose in your own voice. If they ask a question, answer it honestly, including disagreeing when you think the draft already has it right. Don't repeat the whole draft unless asked.

   Only when the latest message asks you to change, rewrite, cut, or add to the draft, put the full revised text in agent_payload.revised_draft: the complete piece, ready to save, not a diff. Otherwise omit revised_draft.

   You can't save anything yourself. When they're happy with it, remind them they can save it with the /save- command for this piece followed by the text.
   ```

6. Run the script once: `python3 debug/spikes/ast-2210/add_agent_task_rows.py`.

7. **Verify.**

   ```bash
   python3 - <<'EOF'
   import json
   from src.utils.config import TASK_CONFIG, CONTACT_CONTEXT_COMMAND_CONFIG, CONTACT_DRAFT_THREAD_CONFIG
   rows = {r["task_key"]: r for r in json.load(open("data/admin/agent_task.json"))}
   drafts = [m["draft_task"] for m in CONTACT_CONTEXT_COMMAND_CONFIG.values()]
   assert all("Good examples" in rows[k]["user_prompt"] and "Bad examples" in rows[k]["user_prompt"] for k in drafts)
   print("AC3 OK")
   assert all(rows[k]["agent_id"] == "principal_recruiter_estelle" for k in drafts)
   rk = CONTACT_DRAFT_THREAD_CONFIG["revise_task_key"]
   assert rows[rk]["agent_id"] == "contact_recruiter_estelle"
   assert all(k in TASK_CONFIG for k in drafts + [rk])
   assert not any("<" + t + ">" in rows[k]["user_prompt"] for k in drafts for t in ("TITLE", "LABEL", "GUIDANCE", "GOOD", "BAD"))
   print("ROWS OK")
   EOF
   git diff data/admin/agent_task.json | grep -E '^-[^-]'
   python3 -m pytest tests/component/utils/test_config.py tests/component/core/test_contact.py -q -p no:cacheprovider 2>&1 | grep -E '^(FAILED|ERROR)' | sort > debug/spikes/ast-2210/after-stage2.txt
   comm -13 debug/spikes/ast-2210/after-stage1.txt debug/spikes/ast-2210/after-stage2.txt
   ```

   The last `comm` must print nothing. Any new failure → stop and comment on the parent.

8. Commit: `git add data/admin/agent_task.json && git commit -m "code(AST-2210): Estelle draft_context_* and contact_draft_revise agent_task rows"`, then `git push origin HEAD:sub/AST-2206/AST-2210-registry-estelle-prompts`.

## Canon alignment (plan-stage)

- **`patt.contact.command-intercept`**: every new command is a registry row in `CONTACT_CONFIG["commands"]` with a `src.core.*` handler path, `mode: "code"`, a `description`, and a `usage_reply_text`. The existing shape, mode, skills-collision, and `CONTACT_TASK_CONFIG`-collision asserts all run over the generated entries unchanged. No command id is written as a literal anywhere: ids come from `f"{verb}-{suffix}"` (AC 2). The new optional fields are the config half of the parent's requested amendments (a) payload-optional, (b) per-entry artifact key, and (c) private-channel-only. Runner behavior for them is #3's job, and the canon text edit is out of this Scope (see Scope gate).
- **`stat.logging.debug`**: this ticket adds no runtime functions, loops, or callee calls (import-time config and JSON prompt rows only), so it places no `logger.debug` call sites. The statute's Calling/Response duty lands on #2/#3's handlers.

## Acceptance trace

| Ticket AC | Where satisfied |
|-----------|-----------------|
| 1 Command set | Stage 1 steps 4, 8; verified Stage 1 step 14 |
| 2 Generated, not hand-listed | Stage 1 step 8; grep in step 14 |
| 3 Prompt example sections | Stage 2 steps 3, 7 |
| 4 Pinhole | Stage 1 step 12. Import + kinds verified in step 14; `pytest -k pinhole` goes green once Betty updates `test_every_contact_handler_in_pinhole` (qa-child) |

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2210
**Overall:** APPROVED
**Corpus:** 0d01e20d2b313a4e35cf3d07434b6cd69f615768
**Publish ref:** `origin/sub/AST-2206/AST-2210-registry-estelle-prompts` @ `5a00807408ce5680a82368e666696feb85b8abc8`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.contact.command-intercept | A | | |
| stat.logging.debug | X | | Import-time config + `agent_task.json` only; no new `src/**` callables or log sites in this child |

## Traceability

AC1→Stage 1 (4,8,14); AC2→Stage 1 (8,14); AC3→Stage 2 (3,7); AC4→Stage 1 (12,14) with pinhole pytest green at qa-child/test-child per plan acceptance table

## Findings

### acceptable

- **Location:** Plan § Scope gate / Canon alignment  
  **Finding:** Parent-requested `patt.contact.command-intercept` canon text amendments (a–c) are explicitly out of this child’s file scope; the plan carries the config half (`payload_optional`, `artifact_key`, `private_channel_only`) and documents the #3 runner contract.  
  **Recommendation:** No plan change; Chuckles/Archie track pattern doc updates on the epic, not blocking #1 build.

- **Location:** Child AC 4 vs Stage 1 step 14  
  **Finding:** AC 4 requires `pytest -k pinhole` to pass at ticket done; Stage 1 may leave `test_every_contact_handler_in_pinhole` red until Betty amends the meteorite-only write assert at qa-child.  
  **Recommendation:** Keep the documented baseline/`comm` gate and name the pending test in the Code Complete comment as the plan already requires.

### discuss

- **Location:** Plan interim behavior (Stage 1 contract §)  
  **Finding:** Until AST-2212, `payload_optional` is inert in the runner, so `/show-*` and `/draft-*` still hit usage replies on ftr — intentional but easy to misread as a config bug during #1-only UAT.  
  **Recommendation:** Optional one-line in implementer notes; not blocking approval.

context_tokens≈42000

## Review

**Built:** `origin/sub/AST-2206/AST-2210-registry-estelle-prompts` @ `fb7588e7d` (Stage 1 `53b61e3db`, Stage 2 `fb7588e7d`).

**Implementer notes:**
- **Expected red test:** `TestAst2061ContactPinholeConfig::test_every_contact_handler_in_pinhole` still asserts every `write` kind is under `src.core.meteorite.`; the amended rule adds `write artifact`. Betty updates it at qa-child (AC 4). It is the only new failure vs baseline.
- **Interim on ftr (Joan's discuss note):** until AST-2212, `payload_optional` is inert in the runner, so `/show-*` and `/draft-*` with no payload post the usage reply. That is expected, not a config bug.
- **Baseline run per file:** `tests/component/core/test_contact.py` fails collection locally (`ModuleNotFoundError: asyncpg`, environment, pre-existing), which aborts a combined pytest run; Stage 0–2 comparisons ran each file separately. Baseline: 26 `test_config.py` failures + that collection error, unchanged.
- **Row script location:** the editor refuses writes under gitignored `debug/`, so the throwaway append script ran from `/tmp` (never committed). Output verified by the plan's AC3/ROWS checks; JSON diff is additions only.
- **Lint:** `ruff` delta is one finding, UP006 on `_CONTACT_DRAFT_RESPONSE_SCHEMA: Dict[str, Any]`, written as the plan specifies and matching the file's 39 existing `Dict` annotations.
