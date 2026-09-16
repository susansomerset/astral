# Prompt-token source-pin harvest helper

**Linear:** [AST-1698](https://linear.app/astralcareermatch/issue/AST-1698)
**Parent:** [AST-1579](https://linear.app/astralcareermatch/issue/AST-1579) — Capture deduped source-artifact-id array on derived-artifact write
**Publish ref:** `sub/AST-1579/AST-1698-prompt-token-source-pin-harvest-helper`

Ship the reusable prompt-time harvest: parse `{$TOKEN}` names from one agent run’s prompt texts, classify via `TOKEN_SOURCES.source_type == "artifact"`, resolve each catalog key to the then-current `artifact_uuid` for the run’s candidate, dedupe, and expose that list on the `do_task` result. No job_data sibling writes, no `save_*` signature changes, no consult / craft-land persist (parent children #2 / #3 own those).

## Explicit scope gate

Ticket **## Scope** names exactly:

- `src/utils/config.py` — reuse `_TOKEN_RE` / `TOKEN_SOURCES` / `get_artifact_key_for_token` / by-`source_type` getters; add parse-only helper(s) that list artifact catalog keys referenced by prompt text(s). No DB / resolve I/O.
- `src/core/agent.py` — after task prompts are known for the run, invoke harvest; attach the deduped UUID list on the run result / context so later siblings can read it without re-parsing.
- `src/core/candidate.py` — current-`artifact_uuid`-by-catalog-key helper (body-only `get_candidate_current` is not enough).

Every row in **Files Changed** is one of those three paths. Technical kinds covered: config parse helper; agent harvest entry + attach on `do_task`; candidate UUID-by-key read-current wrapper. No consult persist, no save-signature threading, no tracker touch, no draft-traceability edit, no new `ARTIFACT_CONFIG` / `TOKEN_SOURCES` rows.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add parse helper(s): scan prompt text(s) with existing `_TOKEN_RE`, keep `source_type == "artifact"` names, map to `artifact_key` via `get_artifact_key_for_token` | utils |
| `src/core/candidate.py` | Add `get_candidate_current_artifact_uuid(candidate_id, artifact_key) -> Optional[str]` (read-current row → `artifact_uuid`, or `None` on miss) | core |
| `src/core/agent.py` | Add reusable `harvest_source_artifact_ids(...)`; call it in `do_task` after prompt texts are known; set `result["source_artifact_ids"]` (always a `list`, empty when nothing resolved) | core |

**Out of this ticket (do not touch):** `src/core/consult.py` job_data siblings; `save_candidate_data` / `save_job_artifact` / `database.save_artifact` signatures or call sites; `src/core/tracker.py`; `canon/directives/draft/patt.artifact.traceability.md`; new `ARTIFACT_CONFIG` / `TOKEN_SOURCES` entries; `tests/` / `docs/test-bible/**` (Betty).

## Stage 1: Config parse helper (no I/O)

**Done when:** A public helper in `src/utils/config.py` returns the ordered unique `ARTIFACT_CONFIG` keys for every `{$TOKEN}` in the given text(s) whose `TOKEN_SOURCES` row has `source_type == "artifact"`. Non-artifact names, unknown names, and names absent from `TOKEN_SOURCES` are ignored. No database imports. Importing `src.utils.config` still succeeds.

1. In `src/utils/config.py`, immediately after `get_artifact_key_for_token` (currently ~line 6627), add:

```python
def list_artifact_keys_in_prompt_texts(*texts: str) -> list[str]:
    """Return ordered-unique ARTIFACT_CONFIG keys for {$TOKEN} names in ``texts``.

    Uses ``_TOKEN_RE`` and ``TOKEN_SOURCES`` / ``get_artifact_key_for_token`` —
    no hard-coded pinnable-token allowlist. Non-artifact and unknown names are
    skipped. Empty / None texts are ignored.
    """
```

2. Implementation (literal behavior):
   - Initialize an empty `list` and an empty `set` for seen keys.
   - For each `text` in `texts`: if not a non-empty `str`, continue; else for each `_TOKEN_RE.finditer(text)` match, let `name = match.group(1)`.
   - `spec = TOKEN_SOURCES.get(name)`; if `spec` is missing or `spec.get("source_type") != "artifact"`, continue.
   - `key = get_artifact_key_for_token(name)`; if `key` already in the seen set, continue; else add to seen and append to the result list.
   - Return the result list.

⚠️ **Decision:** Dedupe at **catalog-key** level in this helper (first-seen order). UUID-level `set()` semantics remain the agent harvest step’s contract (AC1); key-level unique avoids duplicate read-current calls for two `{$BASE_RESUME}` in one run. Do **not** invent a parallel frozenset of token names — classification is only `TOKEN_SOURCES.source_type`.

3. Do not change `_TOKEN_RE`, `TOKEN_SOURCES`, `TOKEN_SOURCE_TYPES`, `get_tokens_by_source_type`, or `get_artifact_key_for_token` signatures.

## Stage 2: Candidate current-uuid-by-key helper

**Done when:** `get_candidate_current_artifact_uuid(candidate_id, artifact_key)` returns the current row’s `artifact_uuid` string for a candidate-scoped catalog key, or `None` when no current row exists. Same validation raises as `get_candidate_current` for bad key / missing candidate id. Does not return body bytes.

1. In `src/core/candidate.py`, immediately after `get_candidate_current` (currently ~line 1541), add:

```python
def get_candidate_current_artifact_uuid(
    candidate_id: str, artifact_key: str
) -> Optional[str]:
    """Current-read ``artifact_uuid`` for a catalog key (patt.artifact.read-current).

    Same ARTIFACT_CONFIG / candidate_scoped / entity resolve as
    ``get_candidate_current``, but returns ``artifact_uuid`` (or None on miss)
    instead of ``artifact_data``. Never reads candidate_data blobs. No coat-check.
    """
```

2. Implementation: copy the validation + `database.get_current_artifact(...)` call from `get_candidate_current` (same `entry`, `cid`, `artifact_type` derivation). On `row is None`, return `None`. Otherwise return `row.get("artifact_uuid")` (may be `None` if the column is missing — treat missing the same as miss for harvest callers by returning only a non-empty `str`; if `artifact_uuid` is missing/empty, return `None`).

⚠️ **Decision:** Do **not** refactor `get_candidate_current` to call this helper in this ticket (avoids risking hydrate callers). Duplication of the ~15-line resolve preamble is acceptable; a later DRY ticket can merge them. Import direction unchanged: `candidate` → `database` + `config` only.

3. Do not change `get_candidate_current`, `save_candidate_data`, or any hydrate helpers.

## Stage 3: Agent harvest entry + attach on `do_task`

**Done when:** Calling `harvest_source_artifact_ids` with texts containing two `{$BASE_RESUME}` and a candidate that has a current `candidate.artifacts.base_resume` row returns a one-element list of that row’s `artifact_uuid`. With no current row, returns `[]`. `do_task` sets `result["source_artifact_ids"]` to that list (always present as a `list` on returns that occur after prompt texts are known). Grep of harvest/parse sites shows reuse of `_TOKEN_RE` / `get_artifact_key_for_token` / `source_type` — no new pinnable-token allowlist.

1. In `src/core/agent.py` imports from `src.utils.config`, add `list_artifact_keys_in_prompt_texts` next to the existing `_TOKEN_RE` / token imports.

2. Add a module-level helper (near `_task_prompt_texts` / `_referenced_caller_tokens`, ~line 857):

```python
def harvest_source_artifact_ids(
    *texts: str,
    candidate_id: Optional[str] = None,
) -> list[str]:
    """Deduped current artifact_uuid pins for artifact-typed {$TOKEN}s in ``texts``.

    Parse/classify via config ``list_artifact_keys_in_prompt_texts``; resolve each
    key with ``get_candidate_current_artifact_uuid``. Missing candidate_id or
    missing current rows omit that id (no coat-check, no invent). Order = first
    successful resolve; UUID duplicates collapsed (set semantics).
    """
```

3. Implementation:
   - If `(candidate_id or "").strip()` is empty: return `[]` (do not call candidate).
   - `keys = list_artifact_keys_in_prompt_texts(*texts)`.
   - Import `get_candidate_current_artifact_uuid` from `src.core.candidate` **inside the function** or at module top only if it does not create a cycle — prefer a **late import inside the function** if `candidate` already imports anything from `agent` (today it does not; either is fine; late import is safer).
   - Build `out: list[str] = []` and `seen: set[str] = set()`.
   - For each `key` in `keys`: call `get_candidate_current_artifact_uuid(candidate_id, key)`; on `ValueError` from unknown / non-candidate-scoped key, **omit** that key (do not fail the run); on `None`/empty, omit; on a non-empty uuid string, if not in `seen`, add and append.
   - Return `out`.

⚠️ **Decision:** Unknown / non-candidate-scoped catalog keys are **omitted**, not raised, so harvest never aborts `do_task`. Today every artifact-typed `TOKEN_SOURCES` key is candidate-scoped `candidate.*`; job-scoped generative tokens are not in `TOKEN_SOURCES` as `artifact` yet. Job entity resolve is **out of scope** for this child.

4. In `do_task`, after `agent_row, agent_task_row = _resolve_task_prompts(task_key)` succeeds and `live_content` is known, compute harvest texts **once** and stash in a local:

```python
_system_unresolved = (
    (agent_task_row.get("system_prompt") or "").strip()
    or (agent_row.get("content") or "")
)
_harvest_texts = (
    _system_unresolved,
    agent_task_row.get("user_prompt") or "",
    agent_task_row.get("cache_prompt") or "",
    agent_task_row.get("cache_prompt_b") or "",
    agent_task_row.get("cache_prompt_c") or "",
    agent_task_row.get("cache_prompt_d") or "",
    agent_task_row.get("nocache_prompt") or "",
    live_content or "",
)
source_artifact_ids = harvest_source_artifact_ids(
    *_harvest_texts, candidate_id=candidate_id
)
```

⚠️ **Decision:** System slot uses the same unresolved base as `resolved_task_system` (`system_prompt` or agent `content`), not bare `_task_prompt_texts()["system"]` alone — so tokens that live only on agent `content` when `system_prompt` is empty are still harvested. Scan **unresolved** templates (with `{$TOKEN}`), never post-`resolve_tokens` strings and never `intake_prompt_snapshot` overrides.

5. Place the harvest call **after** `_resolve_task_prompts` and **before** the Anthropic/DeepSeek send (right after unresolved prompts are available is fine; do not wait until after the API returns). Keep the local `source_artifact_ids` for the rest of the function.

6. Attach on the run result:
   - Immediately after `result = await send_to_anthropic(...)` / `send_to_deepseek(...)` (where `result["runtime_prompt"] = runtime_prompt` is set, ~line 2151), also set `result["source_artifact_ids"] = list(source_artifact_ids)`.
   - For every **early `return {...}`** that happens **after** harvest was computed (e.g. mid-chain empty caller guard ~line 2015, provider failure path that returns `result`, validation failure dicts, terminal `return result`), include `"source_artifact_ids": list(source_artifact_ids)` on that dict **or** set it on `result` before return. Early returns that happen **before** harvest (e.g. hydrate failure before prompts) leave the key **absent** — siblings must treat missing as “harvest not run”; prefer computing harvest as early as practical after prompts exist so most paths include it.
   - Concrete rule for the builder: compute harvest immediately after `_resolve_task_prompts` + having `agent_row` (before hydrate / chain guards if those still have access to `agent_task_row` — they do). Then **every** subsequent return path in `do_task` must carry `source_artifact_ids` (copy the list). If a return path is easy to miss, set a small local helper:

```python
def _with_harvest(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload["source_artifact_ids"] = list(source_artifact_ids)
    return payload
```

   and wrap dict returns after harvest — but do **not** invent new keys beyond `source_artifact_ids`.

7. Do **not** pass `source_artifact_ids` into `save_candidate_data`, `save_job_artifact`, `tracker.save_job_data`, or consult. Do **not** change preview/`assemble` helpers unless a shared internal already owns the same unresolved texts and the builder would otherwise duplicate — default: **`do_task` only**.

8. Sanity greps the builder must satisfy before Code Complete (AC2):

```bash
grep -n 'list_artifact_keys_in_prompt_texts\|harvest_source_artifact_ids\|get_artifact_key_for_token\|_TOKEN_RE' src/utils/config.py src/core/agent.py
# Fail if harvest classification invents a new frozenset/tuple of pinnable token names.
```

## Execution contract

- Execute stages in order; one commit per stage on the epic worktree; publish each to `origin/sub/AST-1579/AST-1698-prompt-token-source-pin-harvest-helper`.
- Do not add files outside **Files Changed**.
- Ambiguity or codebase drift → stop and comment on parent AST-1579 with the Stage blocked template from plan-child.
- Test-tree ban: no edits under `tests/` or `docs/test-bible/**`.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1698
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `sub/AST-1579/AST-1698-prompt-token-source-pin-harvest-helper` @ `ecc25c13a79d6a795701f5c821023b6609c506ff`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| patt.artifact.traceability | A | | |
| patt.artifact.read-current | A | | |
| patt.artifact.manage-catalog | A | | |
| patt.config.config-block | A | | |
| astral.config.config-source-of-truth | A | | |
| astral.standards.no-hardcoded-sets | A | | |
| astral.standards.dry-and-focused-functions | B | | |
| astral.layers.import-direction | A | | |

## Traceability

AC1→S3§3-6; AC2→S1§2, S3§8; parent AC3–7 N/A (consult sibling persist + craft-land wiring owned by AST-1699/AST-1700).

## Findings

### discuss

- **Canon Scope gap (parent only):** `astral.standards.data-raises-caller-logs` governs harvest miss semantics (omit id, no invent) but is absent from this child’s frozen Citations list. Plan behavior matches the statute; Archie may amend Canon Scope at Discussion if she wants Radia’s column comparable on that id — not a plan defect.
- **`intake_prompt_snapshot` vs unresolved harvest (S3§4 Decision):** Plan harvests DB unresolved templates and explicitly skips `intake_prompt_snapshot` overrides. For `intake_*` tasks where snap replaces slot text sent to the provider, harvested pins could diverge from tokens actually in the live prompt if snap-only differs from DB rows. Acceptable if intake paths never embed artifact-typed tokens solely via snap; flag for builder awareness — siblings #2/#3 should treat missing/`[]` harvest on intake edge cases consistently.

### acceptable

- **Bounded `get_candidate_current` preamble duplication (S2§2):** Plan defers refactoring `get_candidate_current` to call the new UUID helper in this ticket to avoid hydrate blast radius; honest tradeoff, one harvest entry point still centralizes parse+resolve for callers.
- **`do_task` return-path surface area (S3§6):** Many post-harvest return dicts; `_with_harvest` wrapper and explicit “every path after harvest” rule are adequate plan guidance — implementation audit belongs to build/Radia, not a plan gap.

### R6 — Definition fidelity (checklist)

- Plan implements child **## Scope** only; **Explicit scope gate** present; Files Changed = three scoped paths; out-of-scope rows (consult, save signatures, tracker, draft traceability, tests) explicitly banned.
- Child AC1–AC2 have concrete Stage steps and grep verify (S3§8).
- Boundaries honored: no job_data siblings, no `save_*` threading, no sibling #2/#3 work.
- Self-assessment `Confirm Chuckles estimate: 3 — agree` is honest for three ordered stages across config parse, candidate UUID helper, and agent harvest attach.
- Plan Discuss rounds completed: **0** (status Plan Ready).

context_tokens≈52000
