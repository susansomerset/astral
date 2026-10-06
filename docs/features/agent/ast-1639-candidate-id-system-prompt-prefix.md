<!-- linear-archive: AST-1639 archived 2026-09-24 -->

## Linear archive (AST-1639)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1639/candidate-id-system-prompt-prefix-prefix-every-agent-system-prompt  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** ada  
**Priority / estimate:** None / 3  
**Parent:** AST-1638 — Prefix every agent system prompt with the candidate ID for model-agnostic cache isolation  
**Blocked by / blocks / related:** parent: AST-1638

### Description

## What this implements

Owns prepending `[astral-<id>]` as leading system-prompt content at the shared agent assembly chokepoint (do_task, run_adhoc, preview/store parity) and fail-closed when candidate id is missing. Does not own DeepSeek/Anthropic `user_id` metadata, Contact transport, or AST-1637 chatbot triage.

## Citations

`stat.logging.debug`, `stat.logging.error`

## Scope

- [X] `src/core/agent.py` — **modified** — at the shared seven-segment assembly chokepoint (and matching preview/store), prepend `[astral-<id>]` as the leading system-prompt content using the call’s Astral candidate id; fail closed when the id is missing. Call sites that already pass `candidate_id` into the provider keep doing so for timesheets only — no DeepSeek/`user_id` wiring in this epic.
- [X] `src/core/agent.py` / `_assemble_blocks_seven_segment`: accept the call’s candidate id; require it non-empty; make the first system text block’s content begin with `[astral-<id>]` (id substituted) before the resolved `system_content`, so the assembled `system` payload diverges per candidate from byte zero; cache A–D / nocache / live / user segments stay after that leading system content unchanged; raise when candidate id is missing/blank.
- [X] `src/core/agent.py` / `do_task` and `run_adhoc`: pass the existing candidate id into assembly so both provider branches inherit the prefix; do not add provider-specific isolation parameters; do not allow a successful send without a candidate id.
- [X] `src/core/agent.py` / `preview_prompt` (and stored prompt-block system text when agent_data is written for the hop): show the same `[astral-<id>]`-prefixed system text the wire call would send, so operators are not previewing an un-prefixed prompt.
- [X] No changes under `src/external/deepseek.py` / `src/external/anthropic.py` for isolation metadata in this epic.

## Acceptance criteria

- [X] Candidate-scoped `do_task`: with Astral candidate id `somerset`, the first system text block sent to the provider begins with the exact characters `[astral-somerset]` before any prior system prompt body. Fail if that literal prefix is missing, mistyped, appears only after shared system/cache text, or only in user/nocache/live segments.
- [X] Provider-agnostic: the same leading `[astral-<id>]` prefix is present whether the active provider is DeepSeek or Anthropic. Fail if only one provider path gets the prefix.
- [X] Preview parity: `preview_prompt` system text for the same task/candidate begins with the same `[astral-<id>]` prefix as the assembled wire system block. Fail if preview omits the prefix while the live call includes it.
- [X] Privacy: the `<id>` inside the prefix is the Astral candidate id only. Fail if `rg` on the new prefix path shows name, email, Slack handle/username, or similar contact fields as the id source.
- [X] No vendor isolation field as the mechanism: this epic does not add DeepSeek `user_id` or Anthropic `metadata.user_id` for cache isolation. Fail if the shipped diff’s primary isolation change is those request fields rather than system-prompt leading content.
- [X] Shared chokepoint: Contact/Slack (and other channels) do not implement a parallel prefix outside `src/core/agent.py` assembly. Fail if a second prefix implementation appears under `src/core/contact.py` / chatbot / external clients.
- [X] Missing candidate id: `_assemble_blocks_seven_segment` / `do_task` / `run_adhoc` fail closed (raise / unsuccessful result) when candidate id is missing or blank — no omit and no sentinel. Fail if a send succeeds with an empty/missing candidate id and no `[astral-…]` prefix.

## Boundaries

- [X] Does **not** own DeepSeek/Anthropic `user_id` / `metadata.user_id` isolation wiring. Does **not** own Contact transport or AST-1637 chatbot triage.

## Notes for planning

Citations: `stat.logging.debug`, `stat.logging.error`. Prefix shape locked: `[astral-<id>]`. Every agent call has a candidate id — fail closed if missing.

## Git branch (authoritative)

Per **orientation § Branch law**: parent `ftr/AST-1638-prefix-every-agent-system-prompt-with-the-candidate-id`, child `sub/AST-1638/AST-1639-candidate-id-system-prompt-prefix`. Created at dispatch-parent.

## QA test manifest

1. New prefix suite: `tests/component/core/test_agent.py::TestAst1639CandidateIdSystemPrefix`
2. Fail-closed revision: `tests/component/core/test_agent.py::TestAst820VectorFeedbackDebugTrace::test_do_task_fail_closed_when_candidate_id_missing`
3. Revised assemble / preview / adhoc smoke: `TestPromptHelpers::test_builds_context_and_assembles_blocks`, `TestAssembleBlocks::test_builds_cached_and_minimal_blocks`, `TestAgentDataHelpers::test_preview_prompt_resolves_blocks`, `TestRunAdhoc`

```bash
./scripts/testing/run_component_tests.sh \
  tests/component/core/test_agent.py::TestAst1639CandidateIdSystemPrefix \
  tests/component/core/test_agent.py::TestAst820VectorFeedbackDebugTrace::test_do_task_fail_closed_when_candidate_id_missing \
  tests/component/core/test_agent.py::TestPromptHelpers::test_builds_context_and_assembles_blocks \
  tests/component/core/test_agent.py::TestAssembleBlocks::test_builds_cached_and_minimal_blocks \
  tests/component/core/test_agent.py::TestAgentDataHelpers::test_preview_prompt_resolves_blocks \
  tests/component/core/test_agent.py::TestRunAdhoc \
  -q
```

**Pass criterion:** pytest green on manifest lines — not zero-arg harness / branch-lock gate.

**Bible shasum:** `docs/test-bible/core/agent.md` — `0e28ccc252775df1c0562f07fb505566fbdcfd29`

### Comments

#### radia — 2026-09-15T03:25:24.672Z
[code-rubric] PROCEED (Commit: 0546f9dd) prefix chokepoint clean

#### betty — 2026-09-15T03:22:17.179Z
`origin/sub/AST-1638/AST-1639-candidate-id-system-prompt-prefix` @ `0546f9dd` · prefix suite ready

#### joan — 2026-09-15T03:10:37.593Z
[plan-rubric] PROCEED (Commit: 66a47e73) clean prefix chokepoint plan

#### ada — 2026-09-15T03:08:18.346Z
`origin/sub/AST-1638/AST-1639-candidate-id-system-prompt-prefix` @ `66a47e73` · candidate-id prefix plan

---

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

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-1638/AST-1639-candidate-id-system-prompt-prefix`  
**Product commits:**  (Stage 1 — candidate-id system-prompt prefix)

`_system_text_with_candidate_prefix` at shared `_assemble_blocks_seven_segment`; `do_task` / `run_adhoc` / workbench store / `preview_prompt` parity; fail-closed on missing id. No external `user_id` / metadata isolation.

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

## Radia review

[code-rubric]
**Ticket:** AST-1639
**Publish ref:** `0546f9dd89def51f131e03e5ff0222be52ddfc56` (`origin/sub/AST-1638/AST-1639-candidate-id-system-prompt-prefix`)
**Corpus:** fc0c368e5927a57f1561c057ce9a0ff4abe1fb13
**Overall:** CLEAN

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.debug | A | | |
| stat.logging.error | A | | |

## Column diff vs plan stage

(aligned) — Joan graded both directives **A**; code review matches.

## Frame diff

(none)

## Findings

### fix-now

(none)

### discuss

(none)

### advisory

- **Location:** `tests/component/core/test_agent.py` — `TestAst1450RunAdhocWorkbench` (`test_success_completes_ledger_and_stores_blocks`, etc.)
- **Finding:** Workbench `_store_prompt_blocks` now receives prefixed `system_content` per Stage 1 step 6, but existing workbench tests assert ledger/dispatch fields only — not that `store_kw["system_content"]` begins with `[astral-<id>]`.
- **Recommendation:** Optional follow-up test row for stored SYSTEM parity (AC3 stored-row half); product path in `run_adhoc_workbench_test` is correct on read-through.

- **Location:** Diff footprint vs plan `## Scope`
- **Finding:** Product scope stayed `src/core/agent.py` only; `tests/component/core/test_agent.py` and `docs/test-bible/core/agent.md` also changed (Betty `merge-tests` + manifest). Expected workflow divergence, not a canon defect.
- **Recommendation:** No action — note for traceability only.

## What's solid

- `_system_text_with_candidate_prefix` is the single chokepoint: strips id only, no separator before body, `ValueError` with no new `logger.exception` at the raise site (`stat.logging.error`).
- `_assemble_blocks_seven_segment` prefixes the first system block and `_track("system_prompt", …)` before cache A–D; cache/user segments stay unprefixed.
- `do_task` passes `candidate_id` into assembly; store uses the helper once on the unresolved body (no double-prefix); missing/blank id raises before `send_to_*` (`test_do_task_fail_closed_when_candidate_id_missing`).
- `run_adhoc` and `preview_prompt` wired; id resolution uses `_astral_candidate_id` / `astral_candidate_id` only.
- `TestAst1639CandidateIdSystemPrefix` covers helper, assemble, preview, both providers, and fail-closed adhoc/preview paths.
- No `user_id` / `metadata.user_id` isolation added; no files outside the four-file diff (`agent.py`, plan doc, bible, tests).

## Recommended actions (downstream — not executed here)

- Chuckles: append this artifact to `docs/features/agent/ast-1639-candidate-id-system-prompt-prefix.md`, commit `docs(AST-1639): Radia review — clean`, push sub-branch, post slim upshot `--as radia`, move to **Review Posted**.
- datt: **PROCEED** → `resolve-child` optional (no fix-now); engineer may tick Frame diff (none proposed) and advance to **User Testing** when ready.
- Betty (optional): add one workbench store assertion for prefixed `system_content` if Susan wants explicit AC3 stored-row coverage beyond code review.

context_tokens≈28000

---

## Bug: AST-1990 — candidate-id system prefix is idempotent (never stack `[astral-<id>]`)

- **Linear:** [AST-1990](https://linear.app/astralcareermatch/issue/AST-1990) · orphaned mini-parent [AST-1985](https://linear.app/astralcareermatch/issue/AST-1985)
- **Publish ref:** `sub/AST-1985/AST-1990-candidate-prefix-dedupe` (ftr `ftr/AST-1985-candidate-prefix-dedupe`, off `origin/dev`)
- **Scope (AST-1990 `## Scope`):** `src/core/agent.py` — modify `_system_text_with_candidate_prefix` only; no call-site signature changes, no new tables/fields. Tests are Betty's.
- **Canon:** `stat.logging.debug`, `stat.logging.error` — fix adds no log lines; the missing-id `ValueError` stays log-free at the raise site.

### As-is

`_system_text_with_candidate_prefix` (`src/core/agent.py` ~L1169, Stage 1 step 1 above) always returns `f"[astral-{cid}]{system_content}"` and never checks for a marker that's already there. Any path that feeds already-prefixed system text back in adds another copy, on the wire and in the stored SYSTEM `agent_data` row. Observed in AST-1985: the system prompt began `[astral-somerset][astral-somerset][astral-somerset][astral-somerset][astral-somerset]NOTE: Please see ...`.

### To-be

Exactly one `[astral-<cid>]` at byte zero, however many times the text passes through preview, store, or assembly. Wire, `preview_prompt` `"system"`, and the stored SYSTEM row stay byte-identical (AST-1639 AC3 parity). Missing/blank candidate id still raises `ValueError` before any send.

### Repro

Pure-function fixture (no DB needed):

```python
from src.core.agent import _system_text_with_candidate_prefix as f

once = f("NOTE: Please see ...", "somerset")
assert once == "[astral-somerset]NOTE: Please see ..."      # passes today
assert f(once, "somerset") == once                           # FAILS today: "[astral-somerset][astral-somerset]NOTE..."
assert f("[astral-somerset]" * 5 + "NOTE: Please see ...", "somerset") == once   # FAILS today: six markers
```

How it happens in the app: the workbench Test sends `preview_prompt`'s already-prefixed `system` back into `run_adhoc_workbench_test` / `run_adhoc`. The store call (Stage 1 step 6) and assembly (Stage 1 step 2) each prepend again. Re-running from a stored SYSTEM `agent_data` row does the same. Each round trip adds one more marker.

### Root cause

The helper assumes its input is always the un-prefixed resolved body. Stage 1's "do not double-prefix" contract was enforced only by call-site discipline (store and assembly both start from the same raw `system_content`). Nothing enforced it at the chokepoint, so text that was already prefixed upstream (preview output, stored rows) gets prefixed again on every pass.

### Proposed change

Single file, single function: `src/core/agent.py` / `_system_text_with_candidate_prefix`. `re` is already imported (L26).

1. Directly above the helper, add a module-level compiled pattern:

   ```python
   # Leading run of AST-1639 cache-isolation markers, any id, no separators between them.
   _CANDIDATE_PREFIX_RUN_RE = re.compile(r"^(?:\[astral-[^\]]*\])+")
   ```

2. In the helper, keep the `cid` strip and `ValueError` block **unchanged and first** (fail closed before touching the body). Replace the return with:

   ```python
   # Idempotent: drop any existing leading marker run (any id) so re-fed text gets exactly one.
   body = _CANDIDATE_PREFIX_RUN_RE.sub("", system_content, count=1)
   return f"[astral-{cid}]{body}"
   ```

   Update the docstring to say it's idempotent: any leading `[astral-…]` run is replaced by exactly one `[astral-<cid>]`.

3. Call sites stay as they are: assembly (L1203), `do_task` store (L2245), `preview_prompt` (L3037), workbench store (L3199). Once the helper is idempotent, applying it twice at the store sites does nothing extra.

⚠️ **Decision (Susan-approved, AST-1985 Proposed step 1):** strip **any** leading run of markers, whatever id they carry (`[astral-<other>]` included). A stale marker for a different candidate gets replaced by the current `cid`, not kept. Step 2's "same id only" option is not used.

⚠️ **Decision — exact match shape:** literal `[astral-`, then zero or more non-`]` characters, then `]`, repeated, anchored at byte zero only. No whitespace is skipped before or between markers, because Stage 1 emits none (no separator between `]` and body). Text with leading whitespace, or a marker somewhere in the middle of the body, is left alone and still gets one marker prepended. The body after the run is not stripped or trimmed (Stage 1 step 1 decision: strip only the id).

⚠️ **Decision — input type:** `system_content` stays `str`, as the signature says. Every caller passes a `str` (`resolved_task_system` / `resolve_tokens` return `str`). No `or ""` coercion is added, so behavior for valid input doesn't change.

### Blast radius

- **Only callers:** the four sites listed in step 3, all in `src/core/agent.py`. No other module builds the marker (AST-1639 AC6 still holds). Contact (`src/core/contact.py` ~L1157) only passes `astral_candidate_id` through to `do_task`; it doesn't touch the prefix.
- **Behavior change for un-prefixed input:** none. Output is byte-identical to today, so existing `TestAst1639CandidateIdSystemPrefix` assertions on single-pass output keep passing.
- **Behavior change for prefixed input:** existing markers collapse to one. A body that legitimately starts with literal `[astral-…]` text would lose it. No template does that today. Note: `src/utils/logging.py`'s `[astral-log]` strings are stderr log tags, not system prompts.
- **Tests (Betty, via fix-board):** the AST-1990 ticket asks for new idempotence cases in `TestAst1639CandidateIdSystemPrefix`: one already-prefixed input and one five-times-prefixed input, each producing a single marker. Use the Repro asserts above. Nothing existing asserts the stacked behavior, as far as code reading shows.
- **Stored data:** existing SYSTEM `agent_data` rows that already have stacked markers aren't rewritten (no migration, per ticket Boundaries). Re-running from one now produces a single marker.

### What must still hold

- AST-1639 AC1/AC2: first system block sent to DeepSeek and Anthropic begins with exactly `[astral-<cid>]`, before cache A–D, user, nocache, and live segments.
- AST-1639 AC3: wire system text, `preview_prompt["system"]`, and stored SYSTEM `system_content` are byte-identical for the same body and id, now including when the input was already prefixed.
- AST-1639 AC4: the id comes only from the Astral candidate id argument or ctx field. The strip regex never reads or emits contact fields.
- AST-1639 AC7: missing/blank `candidate_id` raises `ValueError` before any provider send, even when `system_content` already carries a marker. Fail closed; never pass an existing marker through when there's no id.
- No separator between `]` and body; body after the marker run is byte-for-byte untouched.
- `stat.logging.error`: no new `logger.error` / `logger.exception` at the raise site. `stat.logging.debug`: no new log lines.
- Existing `TestAst1639CandidateIdSystemPrefix` stays green.


## Fix-board Joan findings (AST-1990)

## [board-joan] verdict (for Chuckles → `linear_proxy --as joan save-comment`)

```
[board-joan]  CANON: OK
```

## Triage notes

Read `## Bug: AST-1990` on `origin/sub/AST-1985/AST-1990-candidate-prefix-dedupe` (`docs/features/agent/ast-1639-candidate-id-system-prompt-prefix.md`). Scope is one helper in `src/core/agent.py`: strip a leading run of `[astral-…]` markers, then emit exactly one `[astral-<cid>]`; `ValueError` on missing id unchanged and still without a new log at the raise site.

**Corpus:** No `docs/canon-index.md` on this ref (same as other fix-board passes). Skimmed `canon/docs/DIRECTIVES-DIRECTORY.md` overlap for `agent.py` / logging / prefix-shaped strings; resolved the ticket’s frozen citations `stat.logging.debug` and `stat.logging.error` from `canon/directives/active/`.

**Logging statutes:** Proposed change adds no `logger.debug` / `logger.error` / `logger.exception` at the helper. That matches `stat.logging.debug` (no new gated joints) and `stat.logging.error` (detection site raises; handler logs once — unchanged).

**Prefix / AST-1639:** In-force directives do not define the AST-1639 wire marker, idempotence, or “same-id vs any-id” strip policy. That behavior lives in the archived AST-1639 feature ACs and this plan-fix patch (including Susan-approved strip-any-leading-run and fail-closed-before-body). The fix closes a chokepoint gap vs double-prefixing; it does not contradict an active statute or pattern. No new carve-out or statute edit is required for F3.

**ESCALATE not warranted:** Architectural choices (strip any id, regex shape, no migration for stacked rows) are already recorded in the patch; they are product/plan decisions, not unset canon intent.

**Chuckles branch hint:** If Betty is **OK**, lane can go **Plan Approved → make-fix** with no F3. If Betty is **REVISE** (new idempotence tests per patch), still **OK** here → Plan Discuss + **qa-fix** only.

---

```text
AST-1990 board-joan done — CANON: OK.
```


**Chuckles routing (orphaned bug-fix):** Betty TESTS: REVISE → sibling test gap child; Joan CANON: OK. AST-1990 proceeds to make-fix on product only.


## Radia review (AST-1990)

**Ticket:** AST-1990  
**Publish ref:** `origin/sub/AST-1985/AST-1990-candidate-prefix-dedupe` @ `2b0b74f0012a39b75f23099bc35b7b16c298e7bb`  
**Corpus:** `e1f2699fad44e4083e39a9a066cc87cae494ad51`  
**Overall:** CLEAN  

**Diff base:** `origin/ftr/AST-1985-candidate-prefix-dedupe...origin/sub/AST-1985/AST-1990-candidate-prefix-dedupe` (product: `src/core/agent.py` only; plan-fix + board notes in `docs/features/agent/ast-1639-candidate-id-system-prompt-prefix.md`).

## Fix-specific checks

- **[bug-repro]** not applicable — clean board opt-out. Betty **TESTS: REVISE** routed idempotence coverage to sibling **AST-1992** (`origin/sub/AST-1985/AST-1992-candidate-prefix-dedupe-tests`, not in this diff). Spawn notes: Ada verified six idempotence tests pass against this tip; no `[bug-repro]` on AST-1990.
- **## What must still hold — OK** — Traced plan-fix list against shipped helper:
  - **AC1/AC2:** `_assemble_blocks_seven_segment` still sets first system block via `_system_text_with_candidate_prefix`; cache/user segments unchanged. Unprefixed input is byte-identical to pre-fix; prefixed input collapses to one marker at byte zero.
  - **AC3:** Same helper at assembly (~L1212), `do_task` store (~L2254), `preview_prompt` (~L3046), workbench store (~L3208); idempotent helper makes double application at store+assembly safe.
  - **AC4:** Strip uses only `system_content` + `candidate_id` argument; regex does not read ctx/contact fields.
  - **AC7:** `cid` strip + `ValueError` remain **before** `_CANDIDATE_PREFIX_RUN_RE.sub`; prefixed body with blank id still fails closed (no pass-through of markers).
  - **No separator / body preservation:** Still `f"[astral-{cid}]{body}"`; `sub` removes only anchored leading marker run; no trim on remainder.
  - **Logging:** No new `logger.*` in diff; raise site unchanged (no `logger.exception` at detection).
  - **Existing `TestAst1639CandidateIdSystemPrefix`:** Blast radius claim holds for single-pass paths; idempotence asserts deferred to AST-1992 per lane split (advisory below, not a regression in this product diff).

## Canon scores

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| stat.logging.debug | A | | No new debug joints; helper change is pure string/id logic |
| stat.logging.error | A | | Missing-id path still raises without logging at the raise site |

## Column diff vs plan stage

(aligned) — Joan **[board-joan] CANON: OK** on the AST-1990 patch matches both **A** grades; no separate validate-plan per-id table on this bug patch.

## Frame diff

(none)

## Findings

**fix-now:** (none)

**discuss:** (none)

**advisory:**

- **Sibling test carry:** Idempotence cases from plan **Repro** / fix-board are not committed on this publish ref; they live on **AST-1992**. Product fix is still reviewable without them per board opt-out; merge AST-1992 (or equivalent) before treating idempotence as repo-guarded on `dev`.
- **Docs in diff:** Large `## Bug: AST-1990` append is plan-fix/board artifact, not product scope creep.
- **Pre-existing failures:** Spawn notes 40× `test_agent.py` failures on pre-fix commit — out of scope for this three-dot diff; do not attribute to AST-1990.

## What's solid

Implementation matches **Proposed change** verbatim: module-level `_CANDIDATE_PREFIX_RUN_RE`, fail-closed block unchanged and first, idempotent strip-then-prepend, docstring updated. Scope stays one helper; call sites untouched. Regex `^(?:\[astral-[^\]]*\])+` with `count=1` removes an entire stacked leading run in one substitution — matches Susan-approved “strip any leading run” decision.


**docs-acceptance:** test/bible delivery for this fix lives on sibling gap AST-1992 (Betty qa-fix); no test() on this product sub.


## Radia review (AST-1992)

**Ticket:** AST-1992  
**Publish ref:** `origin/sub/AST-1985/AST-1992-candidate-prefix-dedupe-tests` @ `149518fb1ae2d605a0801153ebcf6a6488d912da`  
**Corpus:** `e1f2699fad44e4083e39a9a066cc87cae494ad51`  
**Overall:** CLEAN  

**Diff base:** `origin/ftr/AST-1985-candidate-prefix-dedupe...origin/sub/AST-1985/AST-1992-candidate-prefix-dedupe-tests` — **78 lines**, `tests/component/core/test_agent.py` (+45), `docs/test-bible/core/agent.md` (+33). No `src/**`.

**Status gate:** Spawn prompt **Tests Passed** / assignee Ada — trusted.

## Fix-specific checks

### [bug-repro] — OK

Betty thread + bible manifest name **four** repro nodes (red on pre-fix `cc256733f`, green with AST-1990 `2b0b74f00` per Ada). Block comment `# AST-1990 [bug-repro]:` precedes the new tests; assertions call **real** `agent_mod._system_text_with_candidate_prefix` / `_assemble_blocks_seven_segment`, not reimplemented strip logic.

| Test | Pins (concrete) | Pre-fix fail? |
|------|-----------------|---------------|
| `test_helper_already_prefixed_input_keeps_one_marker` | Exact `NOTE: Please see ...` / `[astral-somerset]…`; `f(once, "somerset") == once` | Yes — stacks second marker |
| `test_helper_five_stacked_markers_collapse_to_one` | 5× `[astral-somerset]` + body → single marker | Yes — six markers |
| `test_helper_other_id_leading_marker_replaced_by_current_cid` | `[astral-other]BODY` → `[astral-somerset]BODY`; mixed run → one marker | Yes — keeps stale/other ids |
| `test_assemble_already_prefixed_system_keeps_one_marker` | Wire `system_blocks[0]["text"]` and `runtime[0]["system_prompt"]["content"]` == `[astral-somerset]shared-sys` | Yes — double prefix on re-fed assembly |

Not tautologies; tied to AST-1990 **## To-be** / **Repro** fixtures.

**Also added (guards, not repro-first):** `test_helper_non_leading_marker_left_in_body` (byte-zero-only strip; green pre/post-fix), `test_helper_blank_id_raises_even_when_body_already_prefixed` (AC7 with marker in body). Correctly documented in bible as pre/post green guards.

### ## What must still hold (AST-1990 plan-fix) — OK

Tests **encode** the listed invariants without weakening existing class nodes:

- **AC1/AC2 / separator:** Existing `test_helper_prefixes_without_separator`, `test_assemble_first_system_block_leads_with_prefix`, provider tests unchanged in diff.
- **AC3:** New assemble-on-prefixed-input node; existing preview/store parity tests untouched.
- **AC4:** Cases use opaque ids (`somerset`, `other`, `x`) only.
- **AC7:** New prefixed-body + blank id cases plus existing `test_helper_rejects_blank_or_whitespace_id`.
- **Logging statutes:** No product/logging changes in diff.
- **Class stays green:** Manifest runs full `TestAst1639CandidateIdSystemPrefix` (13 nodes with fix merged — Ada).

## Canon scores

**Notes:** Linear **Description** has **no frozen `## Citations` list** (Boundaries: “Joan CANON: OK — no canon gap” for this test-only gap). Nothing in diff touches `src/**` logging.

| slug | grade | effort | one-line |
|------|-------|--------|----------|
| *(no frozen list on ticket)* | — | | Test/bible-only delivery; product canon scored on AST-1990 |

If process requires rows: treat as **N/A** — not mis-selected product statutes; no **ESCALATE** (Joan already OK’d gap at board).

## Column diff vs plan stage

no plan-stage scores attached (gap child; board Betty REVISE / Joan CANON OK on AST-1990)

## Frame diff

(none)

## Findings

**fix-now:** (none)

**discuss:** (none)

**advisory:**

- **Branch stack vs ftr:** Publish ref **tip still has pre-fix** `_system_text_with_candidate_prefix` (no `_CANDIDATE_PREFIX_RUN_RE`). Four `[bug-repro]` nodes **fail** on sub alone; **pass** when AST-1990 product is on the tree (Ada: via ftr @ `2b0b74f00`). Chuckles landing to `dev` must **include AST-1990 product + this sub** (or merge ftr then sub) so CI matches test-fix proof.
- **merge-tests:** Tip commit `149518fb1` merges `origin/tests` resync (`e2412644`); three-dot vs ftr shows only AST-1992 test/bible deltas — expected Betty/Ada workflow; not cross-ticket **product** scope.
- **Bible wording:** New `### AST-1992` section (accurate) vs Scope line “§ AST-1639 entries gain” (slightly imprecise) — doc nit only.

## What's solid

Repro matches plan **Repro** asserts and Susan-approved **any-id** strip. Guards cover regex anchor (leading space, mid-body marker) and fail-closed with prefixed body. Bible table + manifest align with six new nodes and full-class run command.


---

## Bug: AST-1992 — idempotence tests for candidate-id system prefix (test gap, retroactive)

- **Linear:** [AST-1992](https://linear.app/astralcareermatch/issue/AST-1992) · mini-parent [AST-1985](https://linear.app/astralcareermatch/issue/AST-1985) · product fix [AST-1990](https://linear.app/astralcareermatch/issue/AST-1990)
- **Publish ref:** `sub/AST-1985/AST-1992-candidate-prefix-dedupe-tests`
- **Retroactive:** written after the fact for the sub-log gate. Gap child opened from `[board-betty] TESTS: REVISE` on AST-1990; it never ran plan-fix/make-fix.

### As-is

`TestAst1639CandidateIdSystemPrefix` had no idempotence coverage: nothing asserted that already-prefixed system text comes out with exactly one `[astral-<cid>]`, so the AST-1985 stacking bug had no test guarding it.

### To-be

The class covers re-fed and stacked input on both the helper and the assembly paths, plus guard tests for the regex anchor and fail-closed behavior. Bible § AST-1992 lists the nodes and the manifest.

### Repro

`[bug-repro]` nodes Betty landed in `tests/component/core/test_agent.py::TestAst1639CandidateIdSystemPrefix`:
- `test_helper_already_prefixed_input_keeps_one_marker`
- `test_helper_five_stacked_markers_collapse_to_one`
- `test_helper_other_id_leading_marker_replaced_by_current_cid`
- `test_assemble_already_prefixed_system_keeps_one_marker`

Verified red→green (AST-1992 test-fix):
- **Red:** pre-fix `src/core/agent.py` @ `cc256733f` gave 4 failed, 9 passed. The two guard tests (`test_helper_non_leading_marker_left_in_body`, `test_helper_blank_id_raises_even_when_body_already_prefixed`) pass both before and after the fix.
- **Green:** synced tip with AST-1990 `2b0b74f00` gave 4/4, and the full class passed 13/13.

### Root cause

AST-1639's suite only asserted single-pass output. The double-prefix contract was enforced by call-site discipline, so no test ever fed already-prefixed text back in.

### Proposed change

Test tree and bible only, Betty-owned, already landed (`37574314a`, merged via `merge-tests`):
- six new nodes in `TestAst1639CandidateIdSystemPrefix`;
- `docs/test-bible/core/agent.md` § AST-1992 and its manifest.

No product `src/` change; the product fix is AST-1990.

### Blast radius

`tests/component/core/test_agent.py` (one class) and `docs/test-bible/core/agent.md` (one section). Existing AST-1639 nodes are unchanged. Nothing else in `test_agent.py` asserts stacking.

### What must still hold

- Full `TestAst1639CandidateIdSystemPrefix` stays green with AST-1990 merged.
- The 4 repro nodes stay red against a non-idempotent helper.
- The AST-1990 `## What must still hold` invariants are unaffected.
