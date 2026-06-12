# AST-365 — [AST-310] resolve_tokens: {$COVER_LETTER_SIGNATURE}

**Linear:** [AST-365](https://linear.app/astralcareermatch/issue/AST-365/ast-310-resolve-tokens-dollarcover-letter-signature)  
**Parent epic:** [AST-310](https://linear.app/astralcareermatch/issue/AST-310/cover-letter-signature-profile-fields) — Cover Letter Signature — Profile Fields  
**Feature branch:** `<agent>/ast-365-ast-310-resolve_tokens-cover_letter_signature`

Add **`{$COVER_LETTER_SIGNATURE}`** to **`TOKEN_SOURCES`** so **`resolve_tokens()`** substitutes multiline signature text from **`candidate_data`** for **`craft_job_cover_letter`** and downstream artifact prompts. **AST-310** owns profile schema + UI persistence; **AST-365** owns the **token registry + resolution behavior** (empty string vs warn-only, same pattern as other profile tokens).

⚠️ **Decision:** Dot-path is **`profile.cover_letter_signature`** (string). If **AST-310** finalizes a different key (e.g. nested under `profile.signatures`), update this plan’s **Revision** before build — implementer **stops** if DB/UI path and plan disagree.

---

## Files changed (planned)

| File | Change | Layer |
|------|--------|--------|
| `src/utils/config.py` | One new **`TOKEN_SOURCES`** entry `COVER_LETTER_SIGNATURE` with `"source": "candidate"`, `"path": "profile.cover_letter_signature"` (placed with other **profile** keys). Optionally extend **`get_tokens()`** / admin meta if Manage Tasks lists tokens from registry — follow existing pattern for new tokens. | utils |
| `tests/` or `scripts/` | **If** repo has tests for `resolve_tokens`, add one case for populated + empty signature; else document manual verification in PR. | tests |

---

## Stage 1 — Registry entry

**Done when:** `{$COVER_LETTER_SIGNATURE}` in a test string resolves to profile value when `candidate_data["profile"]["cover_letter_signature"]` is set; resolves to empty when absent (same warning behavior as other empty candidate tokens per existing `resolve_tokens`).

1. In `src/utils/config.py`, add the **`TOKEN_SOURCES`** row for **`COVER_LETTER_SIGNATURE`** as specified above.
2. Run `python3 -m py_compile src/utils/config.py`.

---

## Stage 2 — Coordination check with **AST-310**

**Done when:** Comment on **AST-310** or **AST-365** Linear thread confirms path matches saved profile JSON shape (or plan **Revision** recorded).

1. Read **AST-310** issue / plan (when present) for the exact **`candidate_data`** shape written by the UI.
2. If mismatch, append **`## Revisions`** here and adjust **`path`** in Stage 1 instructions before **b-build-linear**.

---

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|--------|
| §2.1 config | Token lives only in **`TOKEN_SOURCES`** — no parallel string elsewhere. |
| §3.3 | `config.py` only; no core imports from UI. |

---

## Self-Assessment

**Scope — `Single-Component`**  
Single registry entry + optional test; touches **`config.py`** only unless tests live elsewhere.

**Conf — `high`**  
Straightforward mirror of existing profile tokens.

**Risk — `Medium`**  
Wrong path yields blank signatures in cover-letter prompts; easy to spot in QA.

## Review (stub — b-build-linear)

**Branch:** `chuckles/ast-365-ast-310-resolve_tokens-cover_letter_signature`  
**Commit:** `2d7bbe8b`

**Shipped**

- **`TOKEN_SOURCES["COVER_LETTER_SIGNATURE"]`** → `candidate` path **`profile.cover_letter_signature`** (multiline string; empty/absent → same warning path as other profile tokens in **`resolve_tokens`**).
- **`get_tokens()`** unchanged — derives from registry keys.

**Stage 2 (coordination):** Plan path matches **AST-310** / **AST-366** intent (`profile.cover_letter_signature`); if UI persists a different key, record a **Revision** before merge.
