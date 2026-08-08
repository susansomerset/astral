# AST-1270 — Nested draft_job_resume contract (prompt + normalize/validate)

**Linear:** https://linear.app/astralcareermatch/issue/AST-1270/nested-draft-job-resume-contract-prompt-normalizevalidate-draft-job  
**Parent:** https://linear.app/astralcareermatch/issue/AST-1268/draft-job-resume-response-schema-is-wrong  
**Publish ref:** `sub/AST-1268/AST-1270-nested-draft-job-resume-contract`

`draft_job_resume` already asks Judith for a nested envelope (`agent_payload.resume` + sibling `deviations`), but runtime normalize/validate still treats the outer key `resume` as a catalog section id and whitelists via `resolve_resume_structure` / enabled catalog ids. This ticket unwraps `agent_payload.resume` before section checks, switches the whitelist to the candidate’s current `artifacts.base_resume` section keys, allows `deviations` as sibling metadata (no retention work), and keeps the Manage Tasks seed on that nested shape with no flat-only or “experience must be a string” contradiction. Does **not** own deviations persistence (**AST-1271**), debug whitelist trail (**AST-1272**), HTML chrome, or AST-1201 / AST-1205.

## Diagnosis (why the nested sample fails today)

Verified against `normalize_draft_job_resume_agent_payload` / `validate_draft_job_resume_payload` in `src/core/candidate.py` and the parent brief sample:

1. Manage Tasks seed (`data/admin/agent_task.json` → `draft_job_resume.user_prompt`) already shows nested `agent_payload.resume` + `deviations` — prompt and validator disagree; the model followed the prompt.
2. Normalize’s nest loop promotes children from `content` / `section_content` / `base_resume` only (`_CRAFT_RESUME_CONTENT_DICT_KEYS`). It does **not** unwrap `resume`, so `resume` remains a top-level `agent_payload` key.
3. Validate iterates every non-metadata key on `agent_payload` against `enabled_resume_section_ids(resolve_resume_structure(cd))`. `resume` is not a section id → `Unknown resume section key 'resume' (not in candidate catalog: …)` — exact parent failure.
4. Whitelist source is structure catalog (default when `artifacts.resume_structure` is missing), not `artifacts.base_resume` keys. Parent contract: whitelist = current base resume section keys so candidates without a persisted structure blob still validate when base keys match.
5. `_DRAFT_JOB_RESUME_METADATA_KEYS` is a module frozenset and does not include `deviations`. Even after unwrap, `deviations` would be treated as an unknown section unless allowlisted as metadata.
6. `_resume_payload_body` in `tracker.py` walks flat `agent_payload` string/experience keys only. After a correct unwrap, persist gates see section bodies; without unwrap (or if a caller feeds raw nested JSON), nested bodies are invisible and a `deviations` list is skipped only because it is not a string — harden by preferring `.resume` when present so resume parsers never treat envelope keys as section content.

⚠️ **Decision:** Nested envelope is authoritative. Normalize **pops** `agent_payload[nested_resume_key]` when it is a dict and merges its entries onto `agent_payload` before section validation. Flat payloads (no nest key) remain accepted for AST-594-era callers. Whitelist = keys of `artifacts.base_resume` that are members of `RESUME_STRUCTURE_KNOWN_SECTION_IDS` (drops `accent_color` and other non-section junk). Nest key name, metadata key set (including `deviations`), and the existing `resume_section_payload` flag live on `TASK_CONFIG["draft_job_resume"]` — no new inline frozensets in core.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | On `TASK_CONFIG["draft_job_resume"]`: nest unwrap key + payload metadata keys (incl. `deviations`) | utils |
| `src/core/candidate.py` | Unwrap nested resume; whitelist from `base_resume` keys; read metadata/nest names from TASK_CONFIG | core |
| `src/core/tracker.py` | `_resume_payload_body`: when nested resume dict present, take section bodies from it only | core |
| `data/admin/agent_task.json` | Align `draft_job_resume` user_prompt nested example; experience matches base value types | data seed |

**Out of files (siblings / boundaries):**

| File / area | Owner |
|-------------|-------|
| Persist / retain `deviations` as hop or artifact metadata | AST-1271 |
| Style D debug whitelist / unwrap / accept-reject trail | AST-1272 |
| HTML builders / cover-letter hops / craft-base parse | out of epic |
| AST-1201 base-resume daisy chain / AST-1205 approve artifacts | related, not this child |
| `tests/`, `docs/test-bible/**` | Betty |

## Stage 1: TASK_CONFIG nest + metadata contract

**Done when:** `TASK_CONFIG["draft_job_resume"]` declares the nest key and metadata key set used by normalize/validate. No behavior change yet until Stage 2 reads them.

1. In `src/utils/config.py`, inside `TASK_CONFIG["draft_job_resume"]` (keep existing `response_schema`, `response_format`, `resume_section_payload`, entity/chain fields), add:

   ```python
   "nested_resume_key": "resume",
   "payload_metadata_keys": (
       "astral_job_id",
       "company",
       "title",
       "task_success",
       "deviations",
   ),
   ```

2. Do **not** put section id lists, base_resume paths, or prompt prose in this stage. Do **not** add a second config block for the same literals.

3. Leave `_DRAFT_JOB_RESUME_METADATA_KEYS` in `candidate.py` untouched until Stage 2 replaces reads with TASK_CONFIG (avoid a half-migrated dual source).

## Stage 2: Normalize unwrap + base_resume whitelist + deviations metadata

**Done when:** The parent nested sample shape validates when `resume` section keys ⊆ that candidate’s `artifacts.base_resume` known section keys and values are well-typed (experience prose string **or** job array). `resume` is never reported as an unknown section key after normalize. True unknown keys **inside** `resume` still fail with a clear unknown-key message. Candidates with no persisted `artifacts.resume_structure` still pass when base_resume keys match. `deviations` is skipped as metadata (not validated as a section). Flat (no nest) payloads still validate against the same base_resume whitelist.

1. In `src/core/candidate.py`, add a small helper (public or module-private — place with the other draft helpers, public-then-helpers order):

   ```python
   def draft_job_resume_allowed_section_keys(candidate_data: dict) -> list[str]:
       """Section keys from artifacts.base_resume ∩ RESUME_STRUCTURE_KNOWN_SECTION_IDS."""
   ```

   Implementation rules:
   - Read `candidate_data["artifacts"]["base_resume"]`; non-dict / missing → return `[]`.
   - Return sorted keys where `key in RESUME_STRUCTURE_KNOWN_SECTION_IDS` (import/use the existing config tuple — do not copy a parallel section-id tuple).
   - Do **not** call `resolve_resume_structure` / `enabled_resume_section_ids` for this whitelist.

2. Change `normalize_draft_job_resume_agent_payload(parsed)`:
   - Resolve `task_cfg = TASK_CONFIG["draft_job_resume"]`, `nest_key = task_cfg["nested_resume_key"]`, `meta = set(task_cfg["payload_metadata_keys"])`.
   - Resolve `inner` as today (`agent_payload` dict or the parsed dict itself).
   - **Unwrap:** if `inner.get(nest_key)` is a `dict`, `block = inner.pop(nest_key)` then for each `(sid, val)` in `block.items()`, set `inner[sid] = val` (resume body wins on key clash with a pre-existing top-level section key).
   - If `inner.get(nest_key)` is present and **not** a dict, leave it in place — Stage 2 validate will fail it as an unknown/disallowed key (or add an explicit error string in validate: `f"{nest_key!r} must be an object of resume sections"` when the key remains and is not a dict). Prefer the explicit error in `validate_draft_job_resume_payload` after normalize.
   - Keep existing `resume_structure` flatten, `_CRAFT_RESUME_CONTENT_DICT_KEYS` promote, coercions, and `_apply_draft_job_resume_section_aliases` — but when skipping metadata keys in those loops, use `meta` from TASK_CONFIG (include `deviations`), not the old module frozenset.
   - Remove the module-level `_DRAFT_JOB_RESUME_METADATA_KEYS` frozenset once all reads use TASK_CONFIG (delete the constant; do not leave a stale duplicate). Keep `_DRAFT_JOB_RESUME_CONSULT_KEYS` as today unless it already lives in config (leave consult reject set as-is for this ticket).

3. Change `validate_draft_job_resume_payload(parsed, candidate_data)`:
   - Call normalize first (unchanged order).
   - Resolve `inner` / `payload` as today.
   - After normalize, if `nest_key` is still in `payload` and is not a dict: return `f"{nest_key!r} must be an object of resume sections"`.
   - `allowed = set(draft_job_resume_allowed_section_keys(candidate_data))`.
   - If `not allowed`: return `"candidate has no base_resume section keys"` (replace the old “no enabled resume sections” path for this validator).
   - For each `key, val` in `payload.items()`:
     - Skip if `key in meta` or `key == "resume_structure"`.
     - Keep consult-key rejection via `_DRAFT_JOB_RESUME_CONSULT_KEYS`.
     - If `key not in allowed`: return `f"Unknown resume section key '{key}' (not in candidate base_resume keys: {sorted(allowed)})"`.
     - Keep existing experience job-array **or** prose string typing rules (AST-997 / AST-594) and other section string coercion.
   - Keep `pin_experience_job_facts_from_base(payload, candidate_data)` at the end.
   - Do **not** drop or persist `deviations` — leave the value on the payload for AST-1271.

4. Do **not** add Style D debug logging here (AST-1272). Do **not** change `do_task` call sites beyond what already invokes these helpers (`resume_section_payload` path stays).

## Stage 3: Resume body path ignores envelope keys

**Done when:** `_resume_payload_body` returns only section bodies from the nested `resume` object when that object is present; `deviations` and the nest key itself never appear as section content. Flat already-unwrapped payloads behave as today.

1. In `src/core/tracker.py`, update `_resume_payload_body(parsed)`:
   - Resolve `body` from `agent_payload` or `parsed` as today.
   - Read `nest_key = TASK_CONFIG["draft_job_resume"]["nested_resume_key"]`.
   - If `body.get(nest_key)` is a `dict`, set `body = body[nest_key]` for section extraction only (do not mutate the original parsed object).
   - Build `out` as today: string values + experience job arrays only.
   - Do **not** copy `deviations` or other metadata into `out`.

2. No changes to `save_job_artifact_resume_content` filtering beyond what the updated body helper feeds. No HTML/builder edits.

## Stage 4: Manage Tasks seed — nested contract only

**Done when:** Repo seed `data/admin/agent_task.json` row `task_key == "draft_job_resume"` instructs the nested `agent_payload.resume` + `deviations` shape; there is no flat-only envelope example; experience wording matches base value types (string or job array), not “must be a single string.”

1. Edit only the `draft_job_resume` row’s `user_prompt` JSON example / surrounding sentences:
   - Keep the nested envelope:
     ```text
     "agent_payload": {
       "resume": { ...exactly the same keys and value types as the provided base resume... },
       "deviations": ["instruction skipped and why"]
     }
     ```
   - Replace the clause `experience remains a single string formatted like the base` with wording that experience (and every other key) keeps the **same value type as the provided base resume** (prose string or job array for `experience`).
   - Do **not** add a second example where section keys sit flat on `agent_payload` without `resume`.
   - Keep existing instruction bullets (claims trace to materials, deviations for skipped brief items, writing instructions, etc.) unless a sentence contradicts the nested contract — then fix that sentence only.
   - Do **not** edit other task_key rows in this ticket.

2. Repo admin JSON is applied at startup (`apply_repo_admin_json_at_startup`); no separate DB migration script.

## Execution contract

The plan is binding. The agent:

- Executes steps in order within a stage, and stages in order.
- Does not skip, reorder, combine, or expand steps.
- Does not add files, modules, configs, or dependencies that aren't in the plan.
- When a step is ambiguous, contradicts another step, references something that doesn't exist, or fails when executed literally — **stops, comments on the Linear parent issue, and waits.**
- Completes each stage on the epic worktree, commits, publishes to `origin/sub/AST-1268/AST-1270-nested-draft-job-resume-contract`, then continues.

## Self-Assessment

**Scope:** `Single-Component` — `TASK_CONFIG` literals + `candidate.py` draft normalize/validate + thin `_resume_payload_body` harden + one Manage Tasks seed row.

**Conf:** `high` — Failure mode is reproduced by the parent sample against current normalize/validate; fix is unwrap + whitelist source swap + metadata allowlist, reusing existing experience typing.

**Risk:** `Medium` — Wrong whitelist (e.g. still requiring resume_structure, or including non-section base keys) would reject valid drafts or accept junk keys; botched unwrap would leave `resume` as a section key and keep the parent outage.

## Code rules check

- §1.3 DRY: one unwrap path in normalize; whitelist helper shared by validate; tracker reads the same nest key from TASK_CONFIG.
- §1.4 / §2.1 / `astral.standards.no-hardcoded-sets` / `pattern.config.config-block`: nest key + metadata keys on `TASK_CONFIG["draft_job_resume"]`; section id universe stays `RESUME_STRUCTURE_KNOWN_SECTION_IDS`.
- §2.2 / `astral.agent.do-task-delegation`: no new Anthropic call shape; `do_task` keeps calling existing normalize/validate hooks.
- §1.5.1: no new debug-contract lines (AST-1272).
- §3.3 imports: core → utils only for config; no ui/data import changes.
- Boundaries: no deviations retention, no debug trail, no test-tree edits.
