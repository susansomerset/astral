# AST-368 — [AST-301] do_task cover-letter chain + token integration

**Linear:** [AST-368](https://linear.app/astralcareermatch/issue/AST-368/ast-301-do-task-cover-letter-chain-token-integration)  
**Parent epic:** [AST-301](https://linear.app/astralcareermatch/issue/AST-301/build-cover-letter-artifact) — Build Cover Letter Artifact  
**Feature branch:** `<agent>/ast-368-ast-301-do_task-cover-letter-chain-token-integration`

Wire the **cover-letter artifact pipeline** so **`do_task`** chains ( **AST-303** ) resolve **`{$WRITING_PREFERENCES}`** (candidate context token, already in `TOKEN_SOURCES`) and **`{$COVER_LETTER_SIGNATURE}`** ( **AST-365** ) across hops with the same **`chain_context`** / **`ctx`** rules as **AST-370** / **AST-303** Revision 1. **AST-301** owns product sequencing and persistence targets; **AST-368** owns **core** correctness for token + cache handoff.

⚠️ **Decision:** **AST-365** must be merged to `dev` before this branch merges (signature token in `resolve_tokens`). **AST-310** profile fields land with **AST-365** / UI sibling — blocked-by in Linear. **AST-303** + **AST-304** same gate as **AST-370**.

---

## Files changed (planned)

| File | Change | Layer |
|------|--------|--------|
| `src/core/agent.py` | Reuse or extend the same **chain_context merge** path as **AST-370** so cover-letter hops see prior hop output + cache blocks; no duplicate merge logic — **extract shared helper** if **AST-370** already added one. | core |
| `src/utils/config.py` | **Only if** `TOKEN_SOURCES` / `WRITING_PREFERENCES` path needs a job-scoped variant for cover tasks — default **no change** (token already `"source": "candidate"`). | utils |

---

## Stage 1 — Dependency gate

**Done when:** `origin/dev` includes **AST-303**, **AST-304**, **AST-365** (signature token); grep `COVER_LETTER_SIGNATURE` in `TOKEN_SOURCES`.

1. Merge/rebase `origin/dev` until gates satisfied.
2. Confirm `craft_job_cover_letter` (or the **TASK_CONFIG** key **AST-301** names as first hop) exists or **stop** with 🛑 comment on **AST-301** / **AST-368** — do not invent task keys.

---

## Stage 2 — Token path validation

**Done when:** Static test or script: `resolve_tokens` on cover-letter task prompts with representative `candidate_data` + optional `chain_context` yields non-empty `{$WRITING_PREFERENCES}` and `{$COVER_LETTER_SIGNATURE}` when profile fields populated.

1. Add **unit tests** under repo’s existing test layout (or document manual steps if no `pytest` layout) that call `resolve_tokens(..., chain_context=...)` for strings containing `{$WRITING_PREFERENCES}` and `{$COVER_LETTER_SIGNATURE}`.
2. Empty signature: assert behavior matches **AST-365** / **AST-310** (warn + empty string or leave literal — match implemented **AST-365** spec exactly).

---

## Stage 3 — `run_next` chain smoke for cover letter

**Done when:** Two-hop `run_next` chain for cover-letter tasks (per **AST-301** plan) runs in dev/staging with **same** `batch_id` and correct **final** `parsed_response` shape for persistence layer **AST-301** defines.

1. Configure **Manage Tasks** `run_next` for the two hop keys **AST-301** specifies (or use test DB rows).
2. Invoke the **entry** async function **AST-301** names (or temporary test harness calling `do_task` twice if entry not landed) — **do not** wire dispatcher here unless **AST-301** execution doc assigns it.

---

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|--------|
| §1.3 DRY | Share chain merge helper with **AST-370**; one implementation. |
| §2.4 batch | Same `log_batch_id` across cover-letter hops. |
| §2.6 | Cover chain does not transition job states by itself. |
| §3.3 | Core only imports allowed layers. |

**Conflicts:** If **AST-370** helper is not merged yet, **Stage 2** may duplicate — prefer landing **AST-370** first or merging both in one integration PR with a single helper.

---

## Self-Assessment

**Scope — `scope-MAJOR-CHANGE`**  
Cross-cuts `agent.py` chain behavior and test coverage for artifact pipeline.

**Conf — `Medium`**  
Ordering against **AST-365**/**AST-370**/**AST-301** docs.

**Risk — `HIGH`**  
Token misses produce wrong cover letters; batch audit gaps.
