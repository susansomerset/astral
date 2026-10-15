# AST-2221 — Base resume chain registry and seed prompts

**Linear:** [AST-2221](https://linear.app/astralcareermatch/issue/AST-2221)
**Parent:** [AST-1201](https://linear.app/astralcareermatch/issue/AST-1201) — We need a daisy chain to generate the base resume content
**Publish ref:** `sub/AST-1201/AST-2221-base-resume-chain-registry-and-seed-prompts`

Registers the nine-hop base-resume daisy chain in `TASK_CONFIG` / `CANDIDATE_STATES` / `CANDIDATE_STAGE_DISPATCH`, generalizes the three candidate-stage config resolvers so every stage entry (not only `requested_artifacts`) resolves, and seeds nine basic `agent_task` rows linked by `run_next`. After this ticket the chain is fully defined in config and seed but not yet runnable by the stage runner (sibling AST-2222 owns core).

## Explicit scope gate

This ticket's **Scope** names only:

* `src/utils/config.py` — nine hops, chain tuple + error states, CANDIDATE_STATES ERROR entries, `requested_resume` stage entry, stage-generic resolvers
* `data/admin/agent_task.json` — nine new current rows with basic prompts and `run_next`

No `src/core/*`. No prompt polish beyond the brief one-liners. No `contact.title_patterns` → artifact migration.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Register nine TASK_CONFIG hops + schemas; `BASE_RESUME_CHAIN_TASK_KEYS` / error tuple; ERROR states; `requested_resume` stage; generalize three resolvers | utils |
| `data/admin/agent_task.json` | Nine new current Candidate Artifacts rows with basic `user_prompt` and `run_next` chain | data |

## Stage 1: Chain registry in `config.py`

**Done when:** All six ticket Acceptance criteria that are pure-config (AC 1–2, 4–6) pass via the `python -c` one-liners on the ticket; `import src.utils.config` succeeds with no assert failures.

1. In `src/utils/config.py`, immediately after `CANDIDATE_CRAFT_CHAIN_ERROR_STATES` (~line 299), add the base-resume chain sibling tuples (Functional scope order, exact keys):

```python
# Base resume chain (REQUESTED_RESUME entry shape_the_story, run_next order). AST-2221.
BASE_RESUME_CHAIN_TASK_KEYS = (
    "shape_the_story",
    "draft_resume_experiences",
    "draft_supporting_sections",
    "draft_highlights",
    "draft_core_competencies",
    "draft_professional_summary",
    "draft_keywords",
    "draft_resume_base",
    "draft_title_patterns",
)
BASE_RESUME_CHAIN_ERROR_STATES = tuple(error_state_for(k) for k in BASE_RESUME_CHAIN_TASK_KEYS)
```

2. Add nine `TASK_CONFIG` entries (place them after the existing craft-rubric block / before Phase C company prompts is fine — keep them together as one contiguous block with an `# AST-2221 base resume chain` comment). Every entry shares this shell:

* `entity_type`: `"candidate"` (literal — AC 1 asserts this; do **not** copy craft hops' `None`)
* `requires_candidate_key`: `True`
* `response_format`: `"json"`
* `trigger_state`: `None` (stage trigger lives on `CANDIDATE_STAGE_DISPATCH`, not per hop)

Per-hop `response_schema` (and extras):

| task_key | response_schema | notes |
|----------|-----------------|-------|
| `shape_the_story` | `{"story": {"type": "str", "required": True}}` | story narrative |
| `draft_resume_experiences` | `{"experience": _EXPERIENCE_JOB_ARRAY_FIELD}` | reuse the **same object** `_EXPERIENCE_JOB_ARRAY_FIELD` (not a copy of its dict) |
| `draft_supporting_sections` | `education_certifications`, `technical_skills`, `prior_experience`, `publications` — each `{"type": "str", "required": False}` | factual supporting sections; all optional so a hop can omit irrelevant ones |
| `draft_highlights` | `{"highlights": {"type": "str", "required": True}}` | 5–7 highlights as one string (same consumer shape as craft-base `highlights`) |
| `draft_core_competencies` | `{"core_competencies": {"type": "str", "required": True}}` | |
| `draft_professional_summary` | `{"professional_summary": {"type": "str", "required": True}}` | predicate-only prose; schema is still a string |
| `draft_keywords` | `{"keywords": {"type": "str", "required": True}}` | short keyword list; assembler (sibling) maps into `candidate_tagline` |
| `draft_resume_base` | **`_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` by reference** — assign `response_schema: _CRAFT_RESUME_BASE_RESPONSE_SCHEMA` (object identity; AC 2 `is` check). Also set `artifact_key`: `"candidate.artifacts.base_resume"` | do not copy/duplicate the schema dict |
| `draft_title_patterns` | `{"title_patterns": {"type": "str", "required": True}}` | consumer contract = `contact.title_patterns` (newline-separated regexes). Sibling may coerce a list→newline-joined string at persist time; this ticket only registers the str schema |

⚠️ **Decision:** Intermediate hop field names mirror `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` keys where they overlap (`experience`, `highlights`, `core_competencies`, `professional_summary`) so the assembler hop and later Fable prompt work have a single vocabulary. `keywords` stays its own key (not `candidate_tagline`) because the hop RESPONSE is chain context until `draft_resume_base` writes the artifact. `story` is chain-only (like contemplate/anticipate).

3. Extend the per-hop `error_state` assignment loop (~line 1336) to include the new chain:

```python
for _hop in (*BUILD_ARTIFACTS_CHAIN_TASK_KEYS, *CANDIDATE_CRAFT_CHAIN_TASK_KEYS, *BASE_RESUME_CHAIN_TASK_KEYS):
    TASK_CONFIG[_hop]["error_state"] = error_state_for(_hop)
```

4. In `CANDIDATE_STATES`, after the existing craft-chain ERROR dict-unpack (the `**{s: ... for s in CANDIDATE_CRAFT_CHAIN_ERROR_STATES}` block), add a second unpack for base-resume ERROR states. Priors are **`REQUESTED_RESUME` only** (ticket Scope — do not add `REQUESTED_ARTIFACTS`):

```python
**{
    s: {"prior_states": ["REQUESTED_RESUME"], "progress_rank": 4}
    for s in BASE_RESUME_CHAIN_ERROR_STATES
},
```

Do **not** change `REQUESTED_RESUME`'s own `prior_states`.

5. Add `requested_resume` to `CANDIDATE_STAGE_DISPATCH` alongside `requested_artifacts`:

```python
CANDIDATE_STAGE_DISPATCH = {
    "requested_artifacts": {
        "task_key": "craft_get_rubric",
        "trigger_state": "REQUESTED_ARTIFACTS",
        "pass_state": "ARTIFACTS_READY",
        "auto_mode": False,
    },
    "requested_resume": {
        "task_key": "shape_the_story",
        "trigger_state": "REQUESTED_RESUME",
        "pass_state": "RESUME_READY",
        "auto_mode": False,
    },
}
```

Keep / extend the existing assert so **every** stage entry's `task_key` is in `TASK_CONFIG` (e.g. loop `CANDIDATE_STAGE_DISPATCH.values()`). The existing `auto_mode` falsy assert already covers all entries.

6. Generalize the three resolvers that hardcode `CANDIDATE_STAGE_DISPATCH["requested_artifacts"]`:

* **`_dispatch_trigger_state_for_task_key`**: replace the single `if task_key == CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["task_key"]` branch with a loop over `CANDIDATE_STAGE_DISPATCH.values()` — when `task_key == entry["task_key"]`, return `entry["trigger_state"]`.
* **`_dispatch_entity_type_for_task_key`**: replace the `task_key == …["requested_artifacts"]["task_key"]` half of the `inflow_discovery` / craft-entry condition with the same stage-entry membership check (any stage entry `task_key` → `"candidate"`). Keep the `inflow_discovery` arm.
* **`is_valid_candidate_batch_claim_state`**: replace the single `stage_trigger = CANDIDATE_STAGE_DISPATCH["requested_artifacts"]["trigger_state"]` equality with membership in `{e["trigger_state"] for e in CANDIDATE_STAGE_DISPATCH.values()}` so `REQUESTED_RESUME.<hop>` labels validate the same way `REQUESTED_ARTIFACTS.<hop>` already does. Update the docstring to say every stage trigger, not only `REQUESTED_ARTIFACTS`.

⚠️ **Decision:** Only **entry** hops are resolved through `CANDIDATE_STAGE_DISPATCH` (same as today for `craft_get_rubric`). Mid-chain hops keep `trigger_state: None` and are not required to resolve via `_dispatch_trigger_state_for_task_key` — AC 6 only asserts `shape_the_story`. Mid-chain claim/resume is the sibling.

7. Verify locally (exit 0) before committing:

```bash
python -c "from src.utils.config import TASK_CONFIG as T; ks=['shape_the_story','draft_resume_experiences','draft_supporting_sections','draft_highlights','draft_core_competencies','draft_professional_summary','draft_keywords','draft_resume_base','draft_title_patterns']; assert all(T[k]['entity_type']=='candidate' and T[k]['response_schema'] for k in ks)"
python -c "from src.utils import config as c; t=c.TASK_CONFIG['draft_resume_base']; assert t['response_schema'] is c._CRAFT_RESUME_BASE_RESPONSE_SCHEMA and t['artifact_key']=='candidate.artifacts.base_resume'"
python -c "from src.utils.config import TASK_CONFIG, error_state_for, CANDIDATE_STATES; ks=['shape_the_story','draft_resume_experiences','draft_supporting_sections','draft_highlights','draft_core_competencies','draft_professional_summary','draft_keywords','draft_resume_base','draft_title_patterns'];
assert all(TASK_CONFIG[k]['error_state']==error_state_for(k) and 'REQUESTED_RESUME' in CANDIDATE_STATES[error_state_for(k)]['prior_states'] for k in ks)"
python -c "from src.utils.config import CANDIDATE_STAGE_DISPATCH; assert CANDIDATE_STAGE_DISPATCH['requested_resume']=={'task_key':'shape_the_story','trigger_state':'REQUESTED_RESUME','pass_state':'RESUME_READY','auto_mode':False}"
python -c "from src.utils.config import _dispatch_trigger_state_for_task_key, _dispatch_entity_type_for_task_key; assert _dispatch_trigger_state_for_task_key('shape_the_story')=='REQUESTED_RESUME' and _dispatch_entity_type_for_task_key('shape_the_story')=='candidate'"
```

Also confirm `craft_get_rubric` still resolves to `REQUESTED_ARTIFACTS` / `candidate` (no regression on the existing stage).

## Stage 2: Seed nine `agent_task` rows

**Done when:** Walking `run_next` from `shape_the_story` (current rows only) yields exactly the nine keys in Functional scope order and ends at empty `run_next`; each row has a non-empty `user_prompt` and an `agent_id` present in `data/admin/agent.json` (AC 3).

1. In `data/admin/agent_task.json`, append **nine new objects** (do not edit any existing row). Match the field set used by current Candidate Artifacts rows:

* `task_key` / `task_name`: the hop key
* `task_key_uuid`: a fresh UUID4 string per row (generate nine new ones; do not reuse craft UUIDs)
* `task_group_name`: `"Candidate Artifacts"`
* `task_group_order`: `"2000"` (same group as craft hops)
* `task_seq`: `20` through `28` in hop order (sits after craft `craft_joblist_rubric` seq `15`; avoids colliding with `0`/`0.1`/`1`–`7`)
* `current`: `1`
* `agent_id`: use existing ids only — assign as follows (all present in `data/admin/agent.json`):
  * `shape_the_story` → `principal_recruiter_estelle`
  * `draft_resume_experiences`, `draft_supporting_sections`, `draft_highlights`, `draft_core_competencies`, `draft_professional_summary`, `draft_keywords`, `draft_resume_base` → `content_writer_judith`
  * `draft_title_patterns` → `principal_recruiter_estelle`
* `system_prompt`, `cache_prompt`, `cache_prompt_b`, `cache_prompt_c`, `cache_prompt_d`, `nocache_prompt`: `""` (basic seed; Susan will refine in Fable)
* `updated_at`: `"2026-10-15 00:00:00"` (fixed stamp for the seed batch)
* `run_next`: chain in Functional scope order; terminal hop empty string:

| task_key | run_next |
|----------|----------|
| `shape_the_story` | `draft_resume_experiences` |
| `draft_resume_experiences` | `draft_supporting_sections` |
| `draft_supporting_sections` | `draft_highlights` |
| `draft_highlights` | `draft_core_competencies` |
| `draft_core_competencies` | `draft_professional_summary` |
| `draft_professional_summary` | `draft_keywords` |
| `draft_keywords` | `draft_resume_base` |
| `draft_resume_base` | `draft_title_patterns` |
| `draft_title_patterns` | `""` |

2. Set each `user_prompt` to a **one-paragraph basic instruction** taken from the parent Original brief (paraphrase allowed only to make a complete sentence; no multi-section Manage Tasks essays):

| task_key | user_prompt (exact text to seed) |
|----------|----------------------------------|
| `shape_the_story` | `Think about this candidate and the story their resume should tell that differentiates them.` |
| `draft_resume_experiences` | `Review existing content and revise experience elements bullet points to emphasize the story.` |
| `draft_supporting_sections` | `Create supporting sections for the candidate, such as education, technical skills, publications, whatever is relevant and factual about the candidate from the provided information.` |
| `draft_highlights` | `Generate a set of 5-7 bullet points of notable achievements and successes. Where possible, use facts from the existing resume.` |
| `draft_core_competencies` | `Define a set of distinctive core competencies that may use commonly expected keywords for this type of role.` |
| `draft_professional_summary` | `A declarative description of the candidate, predicate only, that describes what the candidate does well and why.` |
| `draft_keywords` | `SHORT list of keywords to be embedded in the pdf metadata.` |
| `draft_resume_base` | `Taking ALL of the pieces together, smooth out the wrinkles of the story, clarify where needed, and assemble all the pieces for the candidate to review and revise.` |
| `draft_title_patterns` | `LONG list of possible title pattern matches for this candidate that this resume would suit.` |

3. Verify AC 3 with a short script (exit 0): load current rows, walk `run_next` from `shape_the_story`, assert the nine-key order, empty terminal `run_next`, non-empty prompts, and every `agent_id` ∈ `agent.json`.

## Out of scope (do not touch)

* `src/core/candidate.py`, `src/core/dispatcher.py`, `src/core/consult.py` — sibling
* Migrating `contact.title_patterns` into the artifact table
* Prompt quality beyond the basic seed text above
* Changing `REQUESTED_RESUME` priors or Manage Candidates UI

## Estimate

Confirm Chuckles estimate: 3 — agree


## Joan validate

[plan-rubric]
**Ticket:** AST-2221
**Overall:** APPROVED
**Corpus:** b7ab2203048ce0beb2869a12200ab7fa696c8066
**Publish ref:** `sub/AST-1201/AST-2221-base-resume-chain-registry-and-seed-prompts` @ `65663db21d092d76b672e7843a68f44ca3c60b6c`

## Canon scores

patt.task.daisy-chain | A | | |
patt.task.dispatch-retry | A | | |
stat.dispatch.entity-state-bound | A | | |

## Traceability

AC1→Stage 1 §2–7 verify; AC2→Stage 1 `draft_resume_base` row + verify; AC3→Stage 2 §1–3; AC4→Stage 1 §3–4 + verify; AC5→Stage 1 §5 + verify; AC6→Stage 1 §6 + verify (craft_get_rubric regression called out in §7)

## Findings

#### discuss

- **Location:** Linear AST-2221 — frozen list slug vs corpus id
- **Finding:** Ticket cites `stat.dispatch.entity-state-bound`; corpus id is `astral.dispatch.entity-state-bound` (`canon_clerk expand` fails on the cited slug). Scored against the active statute body on this ref; Archie may normalize the frozen slug for Radia comparability.
- **Recommendation:** Optional Canon Scope / Citations amend to `astral.dispatch.entity-state-bound`; not blocking build.

#### discuss

- **Location:** Canon Scope (frozen list) vs `src/utils/config.py`
- **Finding:** `astral.config.config-source-of-truth` plainly governs new TASK_CONFIG / stage tuples but is absent from the three-id frozen list (same pattern as AST-1672 sibling note).
- **Recommendation:** Archie may amend parent/child Canon Scope at Discussion; do not widen the list in flight.

#### acceptable

- **Location:** Procedure §1 — assignee
- **Finding:** Status `Plan Ready` but assignee is Ada Lovelace, not Joan; spawn prompt explicitly requested this validate pass.
- **Recommendation:** Chuckles restores implementer after posting; no plan change.

#### acceptable

- **Location:** Explicit scope gate / Out of scope
- **Finding:** Plan files and stages match child `## Scope` only (`config.py`, `agent_task.json`); core runtime, title-pattern migration, and prompt polish are explicitly deferred to AST-2222 / out of scope — aligned with parent partition.
- **Recommendation:** None.

#### acceptable

- **Location:** Stage 1 §6 — resolver generalization
- **Finding:** Plan generalizes the three resolvers via `CANDIDATE_STAGE_DISPATCH` iteration and documents mid-chain hops as sibling-owned (AC6 entry-hop only) — consistent with `patt.task.daisy-chain` (config framework, no hop-specific chain manager code in this ticket).
- **Recommendation:** None.

### R6 checklist (summary)

- Definition fidelity: implements child slice of parent Functional/Technical scope; no `src/core/*`; parent end-to-end AC 7–14 correctly out of this child's AC set.
- DRY / scope: reuses `_EXPERIENCE_JOB_ARRAY_FIELD`, `_CRAFT_RESUME_BASE_RESPONSE_SCHEMA` by reference; mirrors existing BUILD_ARTIFACTS / CANDIDATE_CRAFT chain tuple pattern; no sibling scope creep.
- Self-assessment: Estimate `3 — agree` matches two-stage config+seed footprint.
- Plan Discuss: zero completed `[plan-discuss]` rounds; status `Plan Ready`.

context_tokens≈24000

## Review (build stub)

**Publish ref:** `origin/sub/AST-1201/AST-2221-base-resume-chain-registry-and-seed-prompts`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `65663db21` | Plan doc |
| Joan | `cd90b642f` | validate — plan approved |
| 1 | `4052fca21` | Register nine hops, chain/ERROR states, `requested_resume`, stage-generic resolvers |
| 2 | `1bf9eea06` | Seed nine Candidate Artifacts `agent_task` rows + `run_next` |

**Tip:** `1bf9eea06`

AC 1–6 verified locally via the ticket `python -c` one-liners (plus `craft_get_rubric` regression and `REQUESTED_RESUME.<hop>` claim-label check). No `src/core/*`.
