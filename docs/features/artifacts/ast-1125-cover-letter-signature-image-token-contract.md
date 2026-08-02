# AST-1125 — Cover-letter SIGNATURE_IMAGE token contract

**Linear:** [AST-1125](https://linear.app/astralcareermatch/issue/AST-1125/cover-letter-signature-image-token-contract-support-signature-image-as)  
**Parent:** [AST-1123](https://linear.app/astralcareermatch/issue/AST-1123/support-signature-image-as-a-token-in-the-cover-letter) — Support Signature_Image as a token in the cover letter  
**Publish ref:** `origin/sub/AST-1123/AST-1125-cover-letter-signature-image-token-contract`  
**Unblocks:** [AST-1126](https://linear.app/astralcareermatch/issue/AST-1126/cover-html-emit-token-replace-and-stop-auto-above) — Cover HTML emit (Hedy)

Register a cover-only `{$SIGNATURE_IMAGE}` **render** contract in `BUILD_CONFIG` so cover HTML emit can resolve the candidate’s existing signature image at the token position. This is **not** an LLM prompt token (`TOKEN_SOURCES` / `resolve_tokens`) and does **not** change HTML emit or profile upload.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | Add `BUILD_CONFIG["cover_letter_render_tokens"]` with `SIGNATURE_IMAGE` contract; add thin accessor `get_cover_letter_render_token` | utils |

**Out of scope (do not touch):**

| Item | Owner |
|------|--------|
| Cover HTML token replace / stop auto-above / Style D debug on emit | AST-1126 |
| Resume (base / job / session) HTML emit | excluded — resume must ignore this contract |
| `TOKEN_SOURCES` / `resolve_tokens` / Manage Tasks token pickers | excluded — binary image must not inject into prompts |
| Candidate Profile signature-image upload/validation UI | excluded |
| New signature-image storage field | excluded — reuse `contact.cover_letter_signature_image` |
| `tests/` / `docs/test-bible/**` | Betty |

## Stage 1: BUILD_CONFIG cover render-token contract

**Done when:** `BUILD_CONFIG["cover_letter_render_tokens"]["SIGNATURE_IMAGE"]` exists with the fields below; `get_cover_letter_render_token("SIGNATURE_IMAGE")` returns that dict; `"SIGNATURE_IMAGE"` is **absent** from `TOKEN_SOURCES` / `get_tokens()`; `python3 -m py_compile src/utils/config.py` passes.

1. In `src/utils/config.py`, inside `BUILD_CONFIG`, immediately after the `"session_cover_letter"` block (before the closing `}` of `BUILD_CONFIG`), add:

```python
    # AST-1125: cover HTML render tokens (NOT TOKEN_SOURCES / resolve_tokens).
    # Emit (AST-1126) reads this contract; resume builders must ignore it.
    "cover_letter_render_tokens": {
        "SIGNATURE_IMAGE": {
            "literal": "{$SIGNATURE_IMAGE}",
            "surfaces": ["cover_letter"],
            "source": "candidate",
            "path": "contact.cover_letter_signature_image",
            "value_kind": "safe_image_src",
            # Parent OQ1: no token in signature content → omit image (no fallback insert).
            "absent_token_policy": "omit",
            "missing_or_rejected_image_policy": "omit",
        },
    },
```

2. Immediately after the `BUILD_CONFIG = { ... }` closing brace (near other BUILD helpers such as `resume_artifact_compound_state`), add:

```python
def get_cover_letter_render_token(name: str) -> dict:
    """Return BUILD_CONFIG cover render-token contract for ``name``.

    Raises KeyError when ``name`` is not registered. Cover HTML emit (AST-1126)
    must use this (or the same BUILD_CONFIG path) — do not hardcode the literal
    or candidate path. Not part of TOKEN_SOURCES / resolve_tokens.
    """
    return BUILD_CONFIG["cover_letter_render_tokens"][name]
```

3. Do **not** add `SIGNATURE_IMAGE` (or `{$SIGNATURE_IMAGE}`) to `TOKEN_SOURCES`.
4. Do **not** change `resolve_tokens`, `get_tokens`, `get_manage_tasks_chain_tokens`, or `get_manage_agents_tokens`.
5. Do **not** edit `src/core/builder.py`, session/job cover emit, resume emit, UI, or Candidate Profile.
6. Do **not** invent a new storage key — path stays `contact.cover_letter_signature_image` (same field as today’s profile signature image after AST-1014 contact migration).

⚠️ **Decision:** Live in `BUILD_CONFIG`, not `TOKEN_SOURCES`. `TOKEN_SOURCES` feeds `resolve_tokens()` for LLM prompt text; a data-URL / image src must never be injected into prompts. `BUILD_CONFIG` already owns artifact **rendering** tokens (module header). Sibling AST-1126 consumes this contract for cover emit only.

⚠️ **Decision:** `surfaces: ["cover_letter"]` is the cover-only gate for AC3. Resume builders do not read `cover_letter_render_tokens`. Emit must check surface / only import this helper on cover paths — resume code stays untouched on this ticket.

⚠️ **Decision:** Policies `absent_token_policy` / `missing_or_rejected_image_policy` are declared here so emit does not invent product rules. Actual replacement and removal of auto-above prepend are AST-1126.

## Integration note for AST-1126 (not this ticket)

Emit should:

1. Read `tok = get_cover_letter_render_token("SIGNATURE_IMAGE")`.
2. Search cover signature text for `tok["literal"]`.
3. If present: resolve candidate blob at `tok["path"]` through existing `_safe_image_src`; on accept replace the literal with a safe `<img>`; on reject/missing apply `missing_or_rejected_image_policy` (`omit` — remove literal, no broken img).
4. If absent: apply `absent_token_policy` (`omit` — no auto-insert between closing and name).
5. Stop unconditional image prepend above the signature block (parent OQ2).
6. Leave resume HTML paths alone.

## Self-Assessment

**Scope — `Single-Component`**  
One `BUILD_CONFIG` sub-block plus one accessor in `src/utils/config.py`; no core/ui/data changes.

**Conf — `high`**  
Mirrors the AST-365 / AST-1024 pattern of registering a contract in config ahead of emit; path already exists on contact; deliberate non-registration in `TOKEN_SOURCES` is explicit in the ticket.

**Risk — `low`**  
Config-only. Wrong path would blank the image once emit lands (easy to spot); accidental `TOKEN_SOURCES` registration would be the high-risk mistake and is forbidden by Stage 1 step 3.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|--------|
| §2.1 / `astral.config.config-source-of-truth` | Token literal, path, surfaces, and omit policies live only in `BUILD_CONFIG["cover_letter_render_tokens"]`. |
| §1.4 / `astral.standards.no-hardcoded-sets` | Accessor + config block are the set; emit must not invent a parallel literal. |
| §1.3 DRY | No second validator; emit reuses `_safe_image_src` (sibling). |
| §3.3 import direction | utils only; no core/ui edits. |
| §3.5 naming | `cover_letter_render_tokens` / `get_cover_letter_render_token` / `SIGNATURE_IMAGE` snake/SCREAMING aligned with `TOKEN_SOURCES` key style for the name, but separate registry. |
| `astral.standards.in-scope-only` | Cover render contract only; resume/profile/emit excluded. |
| `astral.standards.debug-contract-gated` | Not applicable this ticket (emit owns Style D). |

## Review (stub — build-child)

**Branch:** `sub/AST-1123/AST-1125-cover-letter-signature-image-token-contract`  
**Code:** `314f39e1`

**Shipped**

- `BUILD_CONFIG["cover_letter_render_tokens"]["SIGNATURE_IMAGE"]` — literal, cover-only surfaces, `contact.cover_letter_signature_image`, omit policies.
- `get_cover_letter_render_token(name)` accessor for emit (AST-1126).
- `SIGNATURE_IMAGE` not in `TOKEN_SOURCES` / `get_tokens()`.

## Radia review — code-rubric.v1

`[code-rubric] revision=1`  
**Overall:** DISCUSS (C4 stragglers only — no product fix-now)  
**Publish tip reviewed:** `26bfa458ac6eae4fabbd94cf22c602afe6192c0f` (`origin/sub/AST-1123/AST-1125-cover-letter-signature-image-token-contract`)  
**Baseline:** `origin/dev`

### What’s solid

- Stage 1 plan matches `src/utils/config.py` literally: `cover_letter_render_tokens.SIGNATURE_IMAGE` fields + `get_cover_letter_render_token`.
- `SIGNATURE_IMAGE` absent from `TOKEN_SOURCES` / `get_tokens()`; `resolve_tokens` leaves the literal untouched.
- Cover-only gate encoded as `surfaces: ["cover_letter"]`; omit policies encode parent OQ1 for AST-1126.
- Engineer product commit is utils-only; Betty owns test/bible; one `merge-tests(AST-1125)`.

### Findings

**discuss (C4 straggler):** Joan excluded `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` at plan time (Files Changed = utils only). Code-time three-dot diff includes the plan doc + Betty test tree, so those statutes score in-scope and **conform**. No product action — acknowledge and continue.

### Recommended actions

- Ada: no `fix-now` product work. On resolve-child, acknowledge the three C4 stragglers (expected docs + Betty expansion) and move to User Testing.
- AST-1126: consume `get_cover_letter_render_token("SIGNATURE_IMAGE")` only on cover emit paths.

## Resolution

**Date:** 2026-08-02  
**Ref:** Radia `[code-rubric] revision=1` Overall DISCUSS (no fix-now)

- **fix-now:** none — product tip unchanged (`314f39e1` / publish through Radia docs tip).
- **discuss (C4 stragglers):** Acknowledged. `astral.debug.spikes-under-debug-dir`, `astral.docs.features-single-file-per-ticket`, and `astral.git.engineer-test-tree-ban` were plan-time exclusions (Files Changed = utils); code-time three-dot diff correctly expands to plan doc + Betty test tree and those statutes **conform**. No product patch.
- **advisory:** Betty `test(AST-1120)` baseline drift noted; out of AST-1125 product scope.
