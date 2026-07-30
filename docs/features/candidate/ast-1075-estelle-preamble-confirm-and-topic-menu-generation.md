# AST-1075 — Estelle preamble confirm and Topic Menu generation

**Linear (this ticket):** https://linear.app/astralcareermatch/issue/AST-1075/estelle-preamble-confirm-and-topic-menu-generation-topic-menu  
**Parent:** https://linear.app/astralcareermatch/issue/AST-953/topic-menu-generation  

**Publish ref (origin):** `sub/AST-953/AST-1075-estelle-preamble-confirm-and-topic-menu-generation`  
**Parent integration ref:** `ftr/AST-953-topic-menu-generation`

Ship Topic Menu **step 1**: Estelle presents a confirmable preamble summary (“Anything here you would change?”), the candidate accepts or corrects, then **pure-Estelle** generation persists a valid Topic Menu (closed `informs`, status triad via AST-1074 helpers). This ticket owns Estelle `agent_task`s, `do_task` orchestration, thin API, and the intake UI handoff after mechanical preamble — not the AST-1074 model itself, not later satisfaction turns, not REQUIRED/ALL_TOPICS_READY hops.

**Depends on:** AST-1074 (`TOPIC_MENU_CONFIG` + `get_topic_menu` / `validate_topic` / `save_topic_menu`) already on `origin/ftr/AST-953-topic-menu-generation` (User Testing). Merge that ftr tip before build. AST-952 mechanical preamble packet (raw materials in `context`) is on `origin/dev`.

**Caller contract from AST-1074:** always call `save_topic_menu(..., revise=True)` (default) so regenerated menus retire dropped topic ids instead of wiping history. Never pass `revise=False` unless the incoming list already includes every retired row to keep.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `TOPIC_MENU_GEN_CONFIG` (task keys, confirm outcomes, packet field list, UI copy keys); add two `TASK_CONFIG` entries; expose gen config on `ui_config` | utils |
| `data/admin/agent_task.json` | Two new Estelle rows: preamble confirm + Topic Menu generate | data (repo admin JSON) |
| `src/core/candidate.py` | Preserve optional `preamble_confirmed_at` on topic_menu normalize/validate/save path; helper to mark confirmed without wiping topics | core |
| `src/core/intake.py` | `build_preamble_packet_snapshot`, `run_topic_menu_preamble_confirm`, `generate_topic_menu_from_preamble` (+ debug Style D) | core |
| `src/ui/api/api_intake.py` | `POST …/topic-menu/confirm` and `POST …/topic-menu/generate` thin wrappers | ui |
| `src/ui/api/api_system.py` | Include `TOPIC_MENU_GEN_CONFIG` (UI-safe subset) under `ui_config` next to `preamble` | ui |
| `src/ui/frontend/src/components/IntakeTopicMenuPanel.tsx` | New panel: Estelle confirm turn(s) → Accept → generate → show menu summary | ui |
| `src/ui/frontend/src/pages/CandidateIntake.tsx` | After preamble complete → `topic_menu` phase (not auto-open legacy Estelle chat); keep active-session resume → chat | ui |
| `src/ui/frontend/src/App.css` | Minimal styles for the confirm/generate panel (match IntakePreamblePanel density) | ui |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Document optional `preamble_confirmed_at` on `topic_menu` | docs |

No `tests/` / bible edits (Betty after Code Complete). No candidate state-machine hops. No changes to Ruth preamble validate or `PREAMBLE_CONFIG` copy. Do **not** rewrite `intake_initiate_candidate` / `intake_candidate_response` / `intake_build_request` prompts in this ticket — legacy chat remains for **active session resume** only.

---

## Stage 1: Config — `TOPIC_MENU_GEN_CONFIG` + `TASK_CONFIG`

**Done when:** `TOPIC_MENU_GEN_CONFIG` is importable with stable task keys and confirm outcomes; `TASK_CONFIG` has matching entries with response schemas; module asserts bind task keys and outcomes; `get_task_keys()` includes both new keys. No agent_task JSON or core/UI yet.

1. In `src/utils/config.py`, immediately **after** the `TOPIC_MENU_CONFIG` asserts, add:

```python
# AST-1075: Estelle preamble confirm + Topic Menu generation (persistence = AST-1074).
TOPIC_MENU_GEN_CONFIG = {
    "confirm_task_key": "topic_menu_preamble_confirm",
    "generate_task_key": "topic_menu_generate",
    "confirm_outcomes": ("continue", "accepted"),
    "confirm_outcome_field": "outcome",
    # Live packet fields Estelle must see (from candidate_data.context / contact).
    "packet_context_keys": (
        "raw_resume",
        "raw_profile",
        "raw_sample",
        "bio_summary",
        "backstory",
        "strengths",
        "priorities",
        "deal_breakers",
    ),
    "packet_contact_keys": (
        "preferred_name",
        "title_patterns",
    ),
    # Library paths Estelle may patch on revise (whitelist only).
    "patchable_context_keys": (
        "raw_resume",
        "raw_profile",
        "raw_sample",
        "bio_summary",
        "backstory",
        "strengths",
        "priorities",
        "deal_breakers",
    ),
    "estelle_agent_id": "principal_recruiter_estelle",
    # UI copy (exposed via ui_config).
    "ui": {
        "panel_title": "Confirm preamble with Estelle",
        "accept_label": "Looks good — generate Topic Menu",
        "send_label": "Send to Estelle",
        "placeholder": "Tell Estelle what to change, or accept below.",
        "generating_label": "Estelle is building your Topic Menu…",
        "done_title": "Topic Menu ready",
    },
}
```

2. Asserts immediately after the block:

   - `confirm_task_key` / `generate_task_key` are distinct non-empty `str`.
   - `confirm_outcomes == ("continue", "accepted")`.
   - Every `packet_context_keys` / `patchable_context_keys` entry is in `CANDIDATE_LIBRARY_CONFIG["context_keys"]`.
   - `estelle_agent_id == "principal_recruiter_estelle"` (same id as existing intake Estelle `agent_task` rows — do **not** use the stale `INTAKE_CONFIG["estelle_agent_id"]` `X00_estelle_recruiter` literal for new rows).

⚠️ **Decision:** New config block `TOPIC_MENU_GEN_CONFIG` rather than expanding `TOPIC_MENU_CONFIG`. Persistence catalog stays AST-1074-owned; generation/confirm orchestration keys stay here so Ada’s model contract does not churn when prompts/UI copy change.

⚠️ **Decision:** Confirm outcomes are `continue` | `accepted` (not Valid/Try Again). Ruth already owns Valid/Try Again for mechanical preamble; Estelle confirm is a different conversation.

3. In `TASK_CONFIG`, after `preamble_validate_response`, add:

```python
"topic_menu_preamble_confirm": {
    "response_schema": {
        "assistant_message": {"type": "str", "required": True},
        "outcome": {"type": "str", "required": True},
        "library_patches": {"type": "dict", "required": False},
    },
    "response_format": "json",
    "context_format": "topic_menu_confirm_{index}",
    "entity_type": "candidate",
    "requires_candidate_key": True,
    "trigger_state": None,
},
"topic_menu_generate": {
    "response_schema": {
        "topics": {"type": "list", "required": True},
        "informs_coverage_confirmed": {"type": "bool", "required": True},
        "informs_covered": {"type": "list", "required": True},
    },
    "response_format": "json",
    "context_format": "topic_menu_generate_{index}",
    "entity_type": "candidate",
    "requires_candidate_key": True,
    "trigger_state": None,
},
```

4. Assert `TOPIC_MENU_GEN_CONFIG["confirm_task_key"]` and `["generate_task_key"]` are both in `TASK_CONFIG`.

5. Do **not** add `dispatch_tasks` rows — both tasks are on-demand (API/UI), not scheduler batches.

---

## Stage 2: Repo `agent_task` rows — Estelle only

**Done when:** `data/admin/agent_task.json` has two new objects with the exact task keys from Stage 1, `agent_id` == `TOPIC_MENU_GEN_CONFIG["estelle_agent_id"]`, prompts that force the schemas above and the closed informs vocabulary, and no other agent/persona rows changed.

1. Append two objects to `data/admin/agent_task.json` (fresh `task_key_uuid` each via `uuid.uuid4()`; `updated_at` = current UTC `YYYY-MM-DD HH:MM:SS`; unused cache slots `""`; `current` = `1`; `run_next` = `""`; `system_prompt` = `""` — persona lives on the Estelle agent row).

### Row A — `topic_menu_preamble_confirm`

| Field | Value |
|-------|--------|
| `task_key` | `topic_menu_preamble_confirm` |
| `agent_id` | `principal_recruiter_estelle` |
| `task_name` | `Topic Menu Preamble Confirm` |
| `task_group_name` | `Topic Menu` |
| `task_group_order` | `2000` |
| `task_seq` | `1` |
| `cache_prompt` (or the repo’s primary cache-A field used by other Estelle intake rows) | See prompt body below |
| `user_prompt` | Short turn instruction pointing at CONTENT + requiring the JSON envelope |

**cache_prompt body (required behaviors):**

- You are Estelle confirming the candidate’s **preamble packet** before inventing a Topic Menu.
- Live CONTENT includes a `PREAMBLE_PACKET` JSON snapshot and optional `CANDIDATE_MESSAGE`.
- First turn (empty/absent candidate message): summarize the packet in plain language, then ask exactly: **Anything here you would change?** Set `outcome` to `continue`.
- Later turns: if the candidate accepts (e.g. “looks good”, “nothing to change”), set `outcome` to `accepted` and keep `assistant_message` as a brief acknowledgment.
- If the candidate requests changes: set `outcome` to `continue`, put allowed field updates in `library_patches` as `{"context": {<key>: <str>, ...}}` using **only** keys from the closed patchable list (raw_resume, raw_profile, raw_sample, bio_summary, backstory, strengths, priorities, deal_breakers). Omit `library_patches` or use `{}` when nothing to write. Re-summarize and re-ask the same confirm question.
- Never invent new library keys. Never generate a Topic Menu in this task.
- `agent_payload.outcome` must be exactly `continue` or `accepted`.

### Row B — `topic_menu_generate`

| Field | Value |
|-------|--------|
| `task_key` | `topic_menu_generate` |
| `agent_id` | `principal_recruiter_estelle` |
| `task_name` | `Generate Topic Menu` |
| `task_group_name` | `Topic Menu` |
| `task_group_order` | `2000` |
| `task_seq` | `2` |

**cache_prompt body (required behaviors):**

- Pure Estelle authorship: invent a directed Topic Menu from the confirmed `PREAMBLE_PACKET` in CONTENT. No config template of seed topics.
- Each topic object **must** include: `id` (stable non-empty string), `name`, `ask`, `required` (boolean), `informs` (non-empty list).
- `informs` entries may **only** be drawn from: `rubrics`, `base_resume`, `strengths`, `priorities`, `deal_breakers`, `backstory`. One topic may list multiple informs. Do not invent target kinds (reject `like_rubric`, `candidate_bio`, etc.).
- Every topic must be directed and answerable in a few minutes (one focused ask — not a multi-hour life story dump).
- Default topic status is applied by code (`open`); Estelle may omit `status`.
- Set `informs_coverage_confirmed` to `true` only after you have checked that every topic has at least one allowed informs target and that the menu as a whole reasonably covers the informs you intend (one ask may cover many). Set `informs_covered` to the unique list of informs targets that appear across topics (subset of the closed catalog).
- Return `topics` as a JSON array (may be empty only if truly impossible — core will reject empty).

2. Do **not** edit Ruth’s `preamble_validate_response` row or legacy intake Estelle chat rows.

---

## Stage 3: Topic Menu envelope — `preamble_confirmed_at`

**Done when:** `normalize_topic_menu` / `validate_topic_menu` / `save_topic_menu` preserve optional `preamble_confirmed_at` (non-empty `str`); a small helper can stamp confirm time without retiring topics; `CANDIDATE_DATA_MODEL.md` documents the field.

1. In `src/core/candidate.py`, extend `normalize_topic_menu`:

   - Keep existing `topics` coercion.
   - If `raw` is a `dict` and `raw.get("preamble_confirmed_at")` is a non-empty `str` after strip, include `"preamble_confirmed_at": <stripped>` on the returned dict; otherwise omit the key (do not invent nulls).

2. Extend `validate_topic_menu` to copy `preamble_confirmed_at` from the normalized menu onto the returned dict when present (topics validation unchanged).

3. Extend `revise_topic_menu` so the returned dict keeps `preamble_confirmed_at` from **existing** when present (incoming may refresh it if provided as non-empty str — prefer incoming when both set).

4. `save_topic_menu` already persists whatever `validate`/`revise` returns — ensure the stored object still includes the meta key when set. No change to default `revise=True`.

5. Add `mark_topic_menu_preamble_confirmed(candidate_id: str, *, when: str | None = None, debug: bool = False) -> dict`:

   - `when` default = UTC `YYYY-MM-DD HH:MM:SS` (same style as intake ledger timestamps).
   - Load via `get_topic_menu`; set `preamble_confirmed_at`; persist with `save_candidate_data(candidate_id, {_topic_menu_key(): menu}, debug=debug)` using the **full** normalized menu (topics list included) so deep-merge cannot drop topics.
   - Style D when `debug=True`: `func="candidate.mark_topic_menu_preamble_confirmed"`, found then recorded (1/2, 2/2), identifier=`candidate_id`.

6. In `CANDIDATE_DATA_MODEL.md` under `### topic_menu`, document optional `preamble_confirmed_at` stamped by AST-1075 after Estelle confirm accepts.

---

## Stage 4: Core orchestration — confirm + generate

**Done when:** `src/core/intake.py` exposes public async callables that build the packet snapshot, run Estelle confirm turns (applying whitelisted patches), gate generation on confirm, validate/filter topics against `TOPIC_MENU_CONFIG`, and `save_topic_menu(..., revise=True)`; `debug=True` emits Style D found/recorded lines on both paths.

1. Imports: `TOPIC_MENU_CONFIG`, `TOPIC_MENU_GEN_CONFIG`; from `src.core.candidate` import `get_topic_menu`, `validate_topic`, `validate_topic_menu`, `save_topic_menu`, `mark_topic_menu_preamble_confirmed`, `save_candidate_data`, `get_candidate`, `build_candidate_token_view` (if useful for name display — optional).

2. Add `build_preamble_packet_snapshot(candidate_id: str) -> dict`:

   - Load candidate; raise `ValueError` if missing.
   - Read `candidate_data.context` / `contact` dicts (empty dict if missing).
   - Return:

```python
{
    "context": {k: str(context.get(k) or "") for k in TOPIC_MENU_GEN_CONFIG["packet_context_keys"]},
    "contact": {k: str(contact.get(k) or "") for k in TOPIC_MENU_GEN_CONFIG["packet_contact_keys"]},
}
```

   - Gate for “Valid preamble packet exists”: require `context["raw_resume"].strip()` non-empty (same bar as CandidateIntake before Estelle). If empty, raise `ValueError("preamble packet incomplete: raw_resume required")`.

3. Add `_apply_library_patches(candidate_id: str, patches: Any, *, debug: bool = False) -> list[str]`:

   - If `patches` is not a `dict`, return `[]`.
   - Only honor `patches.get("context")` when it is a `dict`.
   - For each key/value: key must be in `TOPIC_MENU_GEN_CONFIG["patchable_context_keys"]`; value must be `str`; skip empty after strip only if you are clearing — **Decision:** allow non-empty strings only (reject empty wipe via Estelle patch); collect applied keys.
   - `save_candidate_data(candidate_id, {"context": applied_map}, debug=debug)`.
   - Return list of applied keys.

4. Add `async def run_topic_menu_preamble_confirm(candidate_id: str, candidate_message: str | None = None, *, debug: bool = False) -> dict`:

   - Build packet via `build_preamble_packet_snapshot`.
   - `live_content` = JSON string:

```json
{"PREAMBLE_PACKET": <snapshot>, "CANDIDATE_MESSAGE": <str or "">}
```

   - Ledger + `do_task` pattern: mirror `validate_preamble_answer` / `_run_intake_task` (batch_id prefix `topic-menu-confirm-`, entity_type `candidate`, `task_key=TOPIC_MENU_GEN_CONFIG["confirm_task_key"]`, `ctx=candidate`, `index=candidate_id`, `debug=debug`).
   - On failure: return `{"success": False, "error": <str>, "batch_id": ..., "outcome": None, "assistant_message": None, "applied_patches": []}`.
   - On success: parse `parsed_response`; require non-empty `assistant_message` str; require `outcome` in `TOPIC_MENU_GEN_CONFIG["confirm_outcomes"]`.
   - If `library_patches` present, apply via `_apply_library_patches`.
   - If `outcome == "accepted"`: call `mark_topic_menu_preamble_confirmed(candidate_id, debug=debug)`.
   - Debug Style D (`func="run_topic_menu_preamble_confirm"`): found with outcome token; detail lines for message trunc + applied patch keys; recorded on accept stamp.
   - Return `{"success": True, "outcome": outcome, "assistant_message": msg, "applied_patches": [...], "batch_id": ..., "error": None, "packet": <snapshot after patches re-read or pre-patch — Decision: re-read snapshot after patches so UI can show updated packet>}`.

5. Add `async def generate_topic_menu_from_preamble(candidate_id: str, *, debug: bool = False) -> dict`:

   - Require `get_topic_menu(candidate_id).get("preamble_confirmed_at")` — if missing, raise `ValueError("preamble not confirmed; run confirm accept first")` (do not call Estelle).
   - Build packet snapshot (post-confirm library).
   - `live_content` = JSON `{"PREAMBLE_PACKET": <snapshot>, "INFORMS_CATALOG": list(TOPIC_MENU_CONFIG["informs"])}`.
   - `do_task` with `TOPIC_MENU_GEN_CONFIG["generate_task_key"]` (ledger prefix `topic-menu-generate-`).
   - On agent failure: return success False with error/batch_id.
   - Parse: require `informs_coverage_confirmed is True` (bool); require `informs_covered` is a `list` (may be empty only if topics empty — still fail empty menu later).
   - For each element of `topics`:
     - If not a `dict`, skip (debug_detail count).
     - Ensure `status` defaults to `TOPIC_MENU_CONFIG["default_status"]` when missing.
     - Try `validate_topic(topic)`; on `ValueError`, skip that topic and debug_detail the reason (do **not** accept topics with empty/illegal informs).
   - If zero topics survive: return success False, error `"no valid topics after informs validation"`.
   - Build `{"topics": <validated list>}` (preserve existing `preamble_confirmed_at` by loading current menu and setting it on the outgoing dict before save).
   - `saved = save_topic_menu(candidate_id, outgoing, revise=True, debug=debug)`.
   - Debug Style D (`func="generate_topic_menu_from_preamble"`): found (raw topic count / coverage flag); recorded (stored open/ready/retired counts via saved menu).
   - Return `{"success": True, "menu": saved, "batch_id": ..., "rejected_topic_count": N, "error": None}`.

⚠️ **Decision:** Generation is gated on persisted `preamble_confirmed_at`, not on a UI-only flag — regenerations after refresh still require a prior accept (caller may re-run confirm).  

⚠️ **Decision:** Soft-drop invalid Estelle topics rather than failing the whole menu when at least one valid topic remains; hard-fail only when none remain or coverage flag is not true.  

⚠️ **Decision:** Do **not** call `save_topic_menu(..., revise=False)`.

---

## Stage 5: Thin API + ui_config

**Done when:** Two authenticated intake routes exist; `GET` ui_config includes UI copy + task key names needed by the panel; no business logic in the blueprint beyond validation/HTTP mapping.

1. In `src/ui/api/api_system.py`, where `preamble` is already exposed, add:

```python
"topic_menu_gen": {
    "ui": TOPIC_MENU_GEN_CONFIG["ui"],
    "confirm_outcomes": list(TOPIC_MENU_GEN_CONFIG["confirm_outcomes"]),
},
```

   (Import `TOPIC_MENU_GEN_CONFIG`. Do **not** expose full prompts.)

2. In `src/ui/api/api_intake.py`:

   - Import the two new core callables.
   - `POST /<candidate_id>/topic-menu/confirm`  
     Body JSON: optional `{"message": "<str>"}` (absent/empty = first Estelle turn).  
     `asyncio.run(run_topic_menu_preamble_confirm(..., candidate_message=..., debug=_debug_flag()))`.  
     Map `ValueError` → 400; missing candidate → 404; success False with agent error → 500 + `error` / `batch_id` (same shape as preamble validate).  
     200 body: success payload from core (assistant_message, outcome, applied_patches, packet, batch_id).

   - `POST /<candidate_id>/topic-menu/generate`  
     No body required.  
     `asyncio.run(generate_topic_menu_from_preamble(..., debug=_debug_flag()))`.  
     Same error mapping; 200 returns `{success, menu, batch_id, rejected_topic_count}`.

3. Both routes: `@require_auth`; use existing `_debug_flag()`.

---

## Stage 6: Intake UI — confirm → generate after preamble

**Done when:** Completing mechanical preamble opens Estelle confirm (not legacy `IntakeChatModal`); Accept runs generate and shows a short Topic Menu summary; active-session **Continue** still opens legacy chat unchanged.

1. Add `src/ui/frontend/src/components/IntakeTopicMenuPanel.tsx`:

   - Props: `candidateId`, `onDone: () => void`, `onCancel: () => void`.
   - On mount: `POST …/topic-menu/confirm` with empty body; show `assistant_message` (loading + error toast patterns from `IntakePreamblePanel`).
   - Text area + **Send** → confirm with `{message}`; append/replace Estelle message from response; if `outcome === "accepted"`, enable/auto-run generate (see next).
   - **Looks good — generate Topic Menu** button: if last outcome is not `accepted`, call confirm with message `"Looks good — nothing to change."` (or empty accept path — **Decision:** button first POSTs confirm with that fixed accept phrase if needed, then always POSTs generate once `outcome === "accepted"` / after confirm returns accepted). Simpler path: Accept button POSTs `{message: "Looks good — nothing to change."}`; if response `outcome !== "accepted"`, show Estelle’s reply and do not generate; if accepted, immediately POST generate.
   - While generating, show `ui.generating_label`.
   - On generate success: list topic `name` + `required` + `informs.join(", ")` (read-only); primary button closes via `onDone`.
   - Read labels from `ui_config.topic_menu_gen.ui` (fetch once via existing ui_config load pattern used by preamble — if CandidateIntake/App already caches config, reuse; else `GET /api/ui_config` once in the panel).

2. Update `CandidateIntake.tsx`:

   - Extend `IntakePhase` with `"topic_menu"`.
   - `handlePreambleComplete`: keep materials state for possible legacy use, but `setPhase("topic_menu")` instead of `"chat"`.
   - Render `IntakeTopicMenuPanel` inside the same wide Modal when `phase === "topic_menu"`.
   - `onDone` / cancel → `goProfile()`.
   - Leave `handleResumeContinue` → `chat` unchanged (AST-539 resume path).

3. `App.css`: add a small block (`.intake-topic-menu-panel`, message bubble, topic list) consistent with preamble panel spacing — no new design system, no card soup.

⚠️ **Decision:** New starts after AST-952 preamble go Topic Menu confirm/generate; they do **not** auto-enter the legacy Estelle interview that fills bio via `ready_to_build`. Active session resume still uses legacy chat so AST-539 surfaces do not regress mid-flight. Optional later ticket can retire legacy chat entirely.

---

## Self-Assessment

**Scope:** `MAJOR-CHANGE` — new Estelle agent tasks + TASK_CONFIG, core confirm/generate orchestration, intake API, and CandidateIntake phase wiring; persistence helpers only extended for confirm meta.

**Conf:** `high` — mirrors AST-1015 Ruth `do_task` + thin API, AST-1074 `save_topic_menu(revise=True)` caller contract, and IntakePreamblePanel handoff patterns already on this tip; parent Open questions: none.

**Risk:** `Medium` — bad prompts/schemas could produce empty/invalid menus or patch the wrong library fields (mitigated by whitelist + `validate_topic` drop); changing post-preamble navigation away from legacy chat could surprise UAT that still expects Estelle interview (mitigated by keeping active-session resume → chat and documenting the new-start path).

---

## Code Rules check

- **§2.1 / config-source-of-truth / no-hardcoded-sets:** task keys, confirm outcomes, patchable keys, informs catalog (via `TOPIC_MENU_CONFIG`) live in config; core reads config, not inline frozensets of informs.
- **§2.2 / do-task-delegation:** confirm + generate call `do_task` only; no direct Anthropic from intake/UI.
- **§3.3 import direction:** UI → core callables; core → agent/candidate/data/utils; no UI → database.
- **§3.2 ui-config-driven:** panel labels from `TOPIC_MENU_GEN_CONFIG["ui"]` via ui_config; no business validation in React beyond empty-message UX.
- **debug-contract-gated:** Style D only when `debug=True` on confirm/generate/mark-confirmed paths.
- **§1.3 DRY:** reuse `_run_intake_task` ledger pattern or extract shared helper if duplication exceeds ~15 lines — prefer calling existing `_run_intake_task` for generate/confirm with the new task keys rather than a third copy of ledger code.
- **Out of scope enforced:** no satisfaction turns, no state hops, no AST-1074 informs catalog edits, no `tests/` edits, no rewrite of legacy intake chat prompts.
