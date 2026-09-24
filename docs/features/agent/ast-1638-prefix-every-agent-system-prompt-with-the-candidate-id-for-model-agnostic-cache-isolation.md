# AST-1638 — Prefix every agent system prompt with the candidate ID for model-agnostic cache isolation

<!-- linear-archive: AST-1638 archived 2026-09-24 -->

## Linear archive (AST-1638)

**Archived:** 2026-09-24  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1638/prefix-every-agent-system-prompt-with-the-candidate-id-for-model  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** chuckles  
**Priority / estimate:** None / 3  
**Parent:** —  
**Blocked by / blocks / related:** related: AST-1637

### Description

## Purpose

Multiple candidates hit Astral agents at once (Contact/Slack and every other channel that drives `do_task`). Vendor-specific isolation knobs (e.g. DeepSeek `user_id`) are not equivalent across providers and must not be the primary guarantee. This epic isolates candidates by structure: the Astral candidate ID becomes the leading content of every agent system prompt so prefix-based caches diverge at token zero on DeepSeek, Anthropic, and any future provider that caches by identical prefix.

## Functional scope

* On every agent call, put that call’s Astral candidate ID as the leading content of the system prompt — before any shared or stable system text and before cache segments A–D — using the literal prefix shape `[astral-<id>]` (angle brackets denote the id value, not characters to emit).
* Apply the same prefix rule for both DeepSeek and Anthropic (and any future provider routed through the shared agent assembly path) — isolation comes from prefix divergence, not from a vendor-only request field.
* Carry whatever type the Astral candidate ID currently is (string today; UUID later) without special-casing the identifier shape inside `<id>`.
* Use only the opaque Astral candidate ID for this prefix — never name, email, Slack handle, or other privacy-sensitive contact fields.
* Cover all integrations that already go through shared agent prompt assembly (task hops, ad-hoc, preview, Contact/chatbot, future channels) without per-channel forks.
* Require a candidate id on every agent call — there is no omit/sentinel path; a missing id is a caller defect and must fail closed at assembly.
* Do not implement DeepSeek `user_id` / Anthropic `metadata.user_id` as the isolation mechanism for this epic (explicitly superseded by the prefix approach).

## Component scope

* `src/core/agent.py` — **modified** — at the shared seven-segment assembly chokepoint (and matching preview/store), prepend `[astral-<id>]` as the leading system-prompt content using the call’s Astral candidate id; fail closed when the id is missing. Call sites that already pass `candidate_id` into the provider keep doing so for timesheets only — no DeepSeek/`user_id` wiring in this epic.

## Technical scope

* `src/core/agent.py` / `_assemble_blocks_seven_segment`: accept the call’s candidate id; require it non-empty; make the first system text block’s content begin with `[astral-<id>]` (id substituted) before the resolved `system_content`, so the assembled `system` payload diverges per candidate from byte zero; cache A–D / nocache / live / user segments stay after that leading system content unchanged; raise when candidate id is missing/blank.
* `src/core/agent.py` / `do_task` and `run_adhoc`: pass the existing candidate id into assembly so both provider branches inherit the prefix; do not add provider-specific isolation parameters; do not allow a successful send without a candidate id.
* `src/core/agent.py` / `preview_prompt` (and stored prompt-block system text when agent_data is written for the hop): show the same `[astral-<id>]`-prefixed system text the wire call would send, so operators are not previewing an un-prefixed prompt.
* No changes under `src/external/deepseek.py` / `src/external/anthropic.py` for isolation metadata in this epic.

## Architectural definition

* **Patterns to reuse** — `no established pattern applies` (in-force patterns are batch claim/process, daisy-chain hops, and dispatch-retry — none govern system-prompt prefix isolation).
* **New patterns proposed** — none (single assembly-chokepoint convention; not a multi-step arc). If Archie later wants this named as catalog law, amend at Discussion — do not invent an id here.
* **Applicable statutes**
  * [`stat.logging.debug`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.debug.md>) — debug-gated prompt/assembly detail stays Style D; do not log PII as a stand-in for the candidate id.
  * [`stat.logging.error`](<https://github.com/susansomerset/astral/blob/dev/canon/directives/active/stat.logging.error.md>) — assembly/provider failures continue to log once at the handler with live facts + traceback.

## Acceptance criteria

1. Candidate-scoped `do_task`: with Astral candidate id `somerset`, the first system text block sent to the provider begins with the exact characters `[astral-somerset]` before any prior system prompt body. Fail if that literal prefix is missing, mistyped, appears only after shared system/cache text, or only in user/nocache/live segments.
2. Provider-agnostic: the same leading `[astral-<id>]` prefix is present whether the active provider is DeepSeek or Anthropic. Fail if only one provider path gets the prefix.
3. Preview parity: `preview_prompt` system text for the same task/candidate begins with the same `[astral-<id>]` prefix as the assembled wire system block. Fail if preview omits the prefix while the live call includes it.
4. Privacy: the `<id>` inside the prefix is the Astral candidate id only. Fail if `rg` on the new prefix path shows name, email, Slack handle/username, or similar contact fields as the id source.
5. No vendor isolation field as the mechanism: this epic does not add DeepSeek `user_id` or Anthropic `metadata.user_id` for cache isolation. Fail if the shipped diff’s primary isolation change is those request fields rather than system-prompt leading content.
6. Shared chokepoint: Contact/Slack (and other channels) do not implement a parallel prefix outside `src/core/agent.py` assembly. Fail if a second prefix implementation appears under `src/core/contact.py` / chatbot / external clients.
7. Missing candidate id: `_assemble_blocks_seven_segment` / `do_task` / `run_adhoc` fail closed (raise / unsuccessful result) when candidate id is missing or blank — no omit and no sentinel. Fail if a send succeeds with an empty/missing candidate id and no `[astral-…]` prefix.

## Open questions

none

## Proposed child tickets

#### 1: **Candidate-id system-prompt prefix - Ada**

Owns prepending `[astral-<id>]` as leading system-prompt content at the shared agent assembly chokepoint (do_task, run_adhoc, preview/store parity) and fail-closed when candidate id is missing. Does not own DeepSeek/Anthropic `user_id` metadata, Contact transport, or AST-1637 chatbot triage.
**Citations:** `stat.logging.debug`, `stat.logging.error`
**Scope:** \* `src/core/agent.py` — **modified** — at the shared seven-segment assembly chokepoint (and matching preview/store), prepend `[astral-<id>]` as the leading system-prompt content using the call’s Astral candidate id; fail closed when the id is missing. Call sites that already pass `candidate_id` into the provider keep doing so for timesheets only — no DeepSeek/`user_id` wiring in this epic. \* `src/core/agent.py` / `_assemble_blocks_seven_segment`: accept the call’s candidate id; require it non-empty; make the first system text block’s content begin with `[astral-<id>]` (id substituted) before the resolved `system_content`, so the assembled `system` payload diverges per candidate from byte zero; cache A–D / nocache / live / user segments stay after that leading system content unchanged; raise when candidate id is missing/blank. \* `src/core/agent.py` / `do_task` and `run_adhoc`: pass the existing candidate id into assembly so both provider branches inherit the prefix; do not add provider-specific isolation parameters; do not allow a successful send without a candidate id. \* `src/core/agent.py` / `preview_prompt` (and stored prompt-block system text when agent_data is written for the hop): show the same `[astral-<id>]`-prefixed system text the wire call would send, so operators are not previewing an un-prefixed prompt. \* No changes under `src/external/deepseek.py` / `src/external/anthropic.py` for isolation metadata in this epic.
**Estimate: 3**

**Monolith check:** Functional scope has 7 capabilities; 1 child intentional — one inseparable vertical slice at the shared assembly chokepoint (prefix must ship with preview/store parity and fail-closed missing-id in the same UAT).
**Scope partition check:** sole Component unit (`src/core/agent.py`) and all Technical bullets claimed by child #1 only.

---

## Original brief

## Problem

Multiple candidates interact with Astral agents concurrently (e.g. several candidates messaging Estelle in parallel Slack threads). We want deterministic per-candidate cache isolation across whichever model platform we're using, without depending on platform-specific parameters that may not exist or behave the same way everywhere.

## Investigation

Looked at how the two platforms we're likely to use actually isolate/cache:

* **DeepSeek**: cache hits are pure byte-for-byte prefix matching starting from token zero. DeepSeek also documents a `user_id` request parameter tied to KVCache isolation, content-safety isolation, and scheduling isolation.
* **Anthropic (Claude)**: caching is also prefix-based — reuses the beginning of a request only if identical to a previously cached version — but is opt-in via explicit cache-breakpoint markers. Anthropic's `metadata.user_id` field is documented as general request metadata, not a specific cache-isolation guarantee the way DeepSeek's is.

## Decision

Rather than relying on a platform-specific `user_id`/`metadata` parameter (which is DeepSeek-specific in its isolation guarantee and not guaranteed equivalent elsewhere), isolate candidates structurally: **put the Astral candidate ID as the leading content of every agent system prompt**, before any shared/stable content.

Since cache hits on every platform we've checked require identical prefixes from the start, putting the candidate ID first means every candidate's request diverges immediately at the prefix level — isolation falls out of the prefix-matching mechanism itself, on any model platform, without needing a separate per-platform parameter.

* Use the existing Astral candidate ID (currently a string; will become a UUID in the future — the field should just carry whatever the current identifier type is without special-casing).
* This applies to all Astral agent calls across integrations (Contact/Slack, and any future channels), not just the two-tier chatbot work in [AST-1637](https://linear.app/astralcareermatch/issue/AST-1637/two-tier-chatbot-agent-little-brain-triage-with-candidate-summary).
* This is model-agnostic by design — works the same way whether the call goes to DeepSeek, Anthropic, or any future model provider, since it relies only on prefix divergence rather than a vendor-specific isolation feature.

## Out of scope / superseded

An earlier version of this ticket proposed passing the candidate ID via DeepSeek's `user_id` parameter specifically. That approach is not being pursued as the primary mechanism — it's redundant once the candidate ID leads the prompt prefix, since prefix divergence alone already guarantees isolation on every platform checked so far.

### Comments

#### susan — 2026-09-15T02:53:11.342Z
I already answered your questions.

#### chuckles — 2026-09-15T02:27:25.143Z
@susan
1. Exact leading string format for the candidate-id prefix (e.g. raw id + newline, `astral_candidate_id: <id>\n`, or another literal shape)?
2. When a call has no candidate id (true non-candidate ad-hoc / system hop) — omit the prefix, or use a fixed non-PII sentinel?

#### chuckles — 2026-09-15T02:10:24.979Z
@susan
1. Exact leading string format for the candidate-id prefix (e.g. raw id + newline, `astral_candidate_id: <id>\n`, or another literal shape)?
2. When a call has no candidate id (true non-candidate ad-hoc / system hop) — omit the prefix, or use a fixed non-PII sentinel?

---

_Implementation detail may live in git history on `origin/dev`._
