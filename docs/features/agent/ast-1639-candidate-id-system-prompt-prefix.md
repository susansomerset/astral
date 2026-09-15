# AST-1639 — Candidate-id system-prompt prefix

- **Linear:** [AST-1639](https://linear.app/astralcareermatch/issue/AST-1639)
- **Parent:** [AST-1638](https://linear.app/astralcareermatch/issue/AST-1638)
- **Publish ref:** `sub/AST-1638/AST-1639-candidate-id-system-prompt-prefix`

Every agent call that goes through shared seven-segment assembly must diverge at token zero by candidate: the first system text block begins with the literal prefix `[astral-<id>]` (Astral candidate id only) before any resolved system body or cache A–D. Isolation is structural (prefix match), not DeepSeek `user_id` / Anthropic `metadata.user_id`. Missing/blank candidate id fails closed. Preview and stored SYSTEM agent_data rows show the same prefixed system text the wire call sends.

## Scope gate

This ticket’s **## Scope** names only `src/core/agent.py` (assembly chokepoint, `do_task` / `run_adhoc` pass-through, `preview_prompt` + stored prompt-block system text). No edits under `src/external/deepseek.py`, `src/external/anthropic.py`, `src/core/contact.py`, chatbot, or other channels. Every Files Changed row and every Stage step stays inside that file and those kinds of changes.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/core/agent.py` | Add candidate-id lead helper; require id in `_assemble_blocks_seven_segment` / `_assemble_blocks`; prefix first system block; wire `do_task`, `run_adhoc`, workbench store, `preview_prompt` for parity; fail closed when id missing/blank | core |

Do **not** edit: `src/external/**`, `src/core/contact.py`, chatbot modules, `src/utils/config.py`, `tests/`, bible, or any second prefix implementation outside `agent.py`.

## Canon (this ticket)

- `stat.logging.debug` — any new debug joints stay ungated `logger.debug` (Calling / Response); do not log name/email/Slack handle as a stand-in for the candidate id; the opaque id string is fine in existing candidate= debug lines.
- `stat.logging.error` — do not add a new error log at the raise site for missing id; raise (or return unsuccessful) and let the existing handler log once with facts + traceback if it catches.

## Stage 1: Prefix at assembly + call-site / store / preview parity

**Done when:** With candidate id `somerset`, the first system text block passed to either provider begins with the exact characters `[astral-somerset]` before the prior system body; `preview_prompt`’s `system` value and the SYSTEM content passed to `_store_prompt_blocks` use that same prefixed string; blank/missing candidate id raises or returns unsuccessful before any provider send; no DeepSeek/`user_id` or Anthropic metadata isolation fields are added.

1. In `src/core/agent.py`, immediately above `_assemble_blocks_seven_segment`, add:

   ```python
   def _system_text_with_candidate_prefix(system_content: str, candidate_id: Optional[str]) -> str:
       """Leading cache-isolation marker: first system bytes are ``[astral-<id>]`` then body."""
       cid = (candidate_id or "").strip()
       if not cid:
           raise ValueError(
               "candidate id required for agent system prompt "
               "(no omit / no sentinel — every agent call must carry an Astral candidate id)"
           )
       return f"[astral-{cid}]{system_content}"
   ```

   ⚠️ **Decision:** No separator (space/newline) between `]` and the resolved body — AC requires the first system block to **begin with** the exact characters `[astral-<id>]` before any prior system prompt body. Strip only the id; do not strip `system_content`. Id source is always the Astral candidate id argument/ctx field — never name, email, or Slack handle.

2. Change `_assemble_blocks_seven_segment` signature to require keyword `candidate_id: Optional[str]` (placed after `skip_cache` or with the other kwargs — keep all existing kwargs). At the start of the body, before building `system_block`:

   ```python
   system_for_wire = _system_text_with_candidate_prefix(system_content, candidate_id)
   ```

   Use `system_for_wire` (not raw `system_content`) for:
   - `system_block["text"]`
   - `_track("system_prompt", …)`

   Leave cache A–D / nocache / live / user segment construction unchanged. Do not put the prefix into user-role blocks or into cache slot text.

3. Update `_assemble_blocks` (legacy wrapper) to accept `candidate_id: Optional[str] = None` and pass it through to `_assemble_blocks_seven_segment`. Callers inside this file that still use the legacy wrapper must pass the same id; if none exist, the default still fails closed when assembly runs with a blank id.

4. In `do_task`, at the existing `candidate_id = ctx.get("astral_candidate_id") if ctx else None` site (~1812): keep reading from `ctx["astral_candidate_id"]` only (privacy — do not substitute contact fields). Before `_assemble_blocks_seven_segment` (~2052):

   - Pass `candidate_id=candidate_id` into `_assemble_blocks_seven_segment`.
   - When calling `_store_prompt_blocks`, pass  
     `system_content=_system_text_with_candidate_prefix(system_content, candidate_id)`  
     so the stored SYSTEM row matches the wire first system block. Do **not** double-prefix: assembly prefixes internally from the unresolved body; store uses the helper once on the same unresolved `system_content` variable already in scope.
   - If `_system_text_with_candidate_prefix` / assembly raises `ValueError` for missing id **before** the provider await: do not call `send_to_anthropic` / `send_to_deepseek`. Prefer letting the `ValueError` propagate (caller/dispatcher handles) **or**, if this call site is already inside a path that must return a result dict, return  
     `{"success": False, "error": <str(exc)>, "api_response": None, "parsed_response": None, "timesheet": {}}`  
     without sending. ⚠️ **Decision:** Prefer **raise** from the helper/assembly and do not add a new `logger.exception` at the raise site (`stat.logging.error` — handler logs once). Only convert to an unsuccessful dict if an immediate surrounding `try` in `do_task` already swallows other pre-send failures the same way; do not invent a new soft-omit path.

5. In `run_adhoc`, pass `candidate_id=candidate_id` into `_assemble_blocks_seven_segment`. Missing/blank id must raise via the helper before either `send_to_deepseek` or `send_to_anthropic` — both provider branches inherit the prefix from the shared assembly call (provider-agnostic AC).

6. In `run_adhoc_workbench_test`, the `_store_prompt_blocks(... system_content=system_content ...)` call runs **before** `run_adhoc`. Change that store call to  
   `system_content=_system_text_with_candidate_prefix(system_content, candidate_id)`  
   so workbench SYSTEM rows match what `run_adhoc` will send after assembly prefixes again from the same unresolved body + id. Do not change ledger / timesheet / external client code.

7. In `preview_prompt`, after resolving `system_out` (and before the return dict):

   - Resolve the Astral candidate id from `candidate_data` only, in this order:  
     `(cd.get("_astral_candidate_id") or cd.get("astral_candidate_id") or "")`  
     (same opaque id `do_task` / candidate preview already stamp onto `cd` — see `candidate.py` setting `_astral_candidate_id`). Do **not** read name/email/Slack fields.
   - Set `system_out = _system_text_with_candidate_prefix(system_out, cid)` so the returned `"system"` key begins with the same `[astral-<id>]` prefix the wire assembly would send for that body + id.
   - Missing/blank id → same `ValueError` (fail closed; no un-prefixed preview).

8. Confirm by reading the diff (no code outside this file): no DeepSeek `user_id` / Anthropic `metadata.user_id` isolation wiring; no parallel prefix under contact/chatbot/external.

## Execution contract

- Execute steps in order; do not skip, reorder, or expand scope.
- Do not touch `tests/` or bible — Betty owns fallout from the new `candidate_id` assembly kwarg.
- If a referenced helper/signature has drifted, stop and comment on the **parent** Linear issue with the Stage blocked template — do not improvise.

## Estimate

Confirm Chuckles estimate: 3 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1639
**Overall:** APPROVED
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Publish ref:** `sub/AST-1638/AST-1639-candidate-id-system-prompt-prefix` @ `66a47e732d1554093d82b70c8434d9d2aa7e2039`

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.debug | A | | Plan adds no gated debug joints; id source stays opaque Astral candidate id only |
| stat.logging.error | A | | Missing-id path raises without a new `logger.exception` at the raise site |

## Traceability

AC1→Stage 1 (steps 1–4, shared assembly first system block); AC2→Stage 1 (steps 4–5, both provider branches via `_assemble_blocks_seven_segment`); AC3→Stage 1 (steps 4, 6–7, store + `preview_prompt` parity); AC4→Stage 1 (step 1 decision + step 7 id resolution from `_astral_candidate_id` / `astral_candidate_id` only); AC5→Stage 1 (step 8, no external `user_id` / metadata isolation); AC6→Scope gate + single `agent.py` chokepoint throughout; AC7→Stage 1 (helper raise + `do_task` / `run_adhoc` / preview fail-closed).

## Findings

### acceptable

- **Location:** Stage 1 step 4 (`do_task` pre-send failure shape)
- **Finding:** Step 4 allows either `ValueError` propagation or an unsuccessful result dict when an enclosing `try` already swallows pre-send failures.
- **Recommendation:** Implementer should prefer **raise** per plan; dict return only where an existing same-shape handler is already present — not a plan defect.

Gate checks: **Plan Ready**, assignee Joan, parent AST-1638, zero `[plan-discuss]` rounds. Canon list frozen at two citations (`stat.logging.debug`, `stat.logging.error`) — both **A**. Plan stays inside ticket `## Scope` (`src/core/agent.py` only); maps all seven parent/child AC bullets to Stage 1; single helper avoids duplicate prefix logic; store vs wire double-prefix risk is explicitly handled (unresolved body + one helper application at store sites; assembly prefixes internally). `preview_prompt` id path aligns with `candidate.py` stamping `_astral_candidate_id`. Betty-owned test fallout for new `candidate_id` kwarg is declared in Execution contract — appropriate.

context_tokens≈32000

---
