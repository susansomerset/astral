<!-- linear-archive: AST-310 archived 2026-06-03 -->

## Linear archive (AST-310)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-310/cover-letter-signature-profile-fields  
**Status at archive:** Done  
**Project:** Astral Artifacts  
**Assignee:** hedy  
**Priority / estimate:** Medium / 2  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Add two new fields to candidate_data.profile: cover_letter_signature (text, multiline — e.g. 'Susan A. Somerset\\nAwesome Possum') and cover_letter_signature_image (uploaded JPG). Both surface on the Candidate Profile page. cover_letter_signature exposed as {$COVER_LETTER_SIGNATURE} token in resolve_tokens(). craft_job_cover_letter prompt injects signature via token — never writes it from scratch. [builder.py](<http://builder.py>) renders signature text + image in the cover letter letterSignoff block.

### Comments

#### chuckles — 2026-05-18T20:00:32.803Z
## Landed on origin/dev — Chuckles

- `origin/ftr/AST-310-cover-letter-signature-profile-fields` was **already contained in** `origin/dev` (includes AST-365/366/367 product + `fix(AST-366)` via PR #141). Merge → *Already up to date*. **No push**.
- Deleted `origin/ftr/AST-310-cover-letter-signature-profile-fields`
- Deleted `sub/AST-310/AST-365-ast-310-resolve-tokens-cover-letter` and `sub/AST-310/AST-366-ast-310-candidate-profile-signature-text` (docs-only tips not on dev; product already on `dev`)
- Parent → **PR Ready**
- Children: **AST-365** PR Ready (unchanged), **AST-366** **Done** (unchanged), **AST-367** → **PR Ready**

`origin/dev` tip: `f842e065`

— Chuckles

#### chuckles — 2026-05-16T15:44:28.176Z
## Parent status — Chuckles

Moved parent to **In Progress**: child tickets are in mixed pipeline states. Susan/Chuckles board cleanup 2026-05-16.

— Chuckles

#### susan — 2026-05-06T19:43:35.182Z
[check-linear]

Thread reviewed for Hedy queue pass (after **Plan ready** handoff).

- **Plan ready** comment documents `docs/features/artifacts/ast-310-cover-letter-signature-profile-fields.md` on `chuckles/ast-310-cover-letter-signature-profile-fields` (commit `d5b150b5`); builder scope correctly called out as **AST-367**.
- No new question, blocker, or request in that comment beyond the posted plan; no repo action taken from this pass.

Action: no-op.

— Hedy (check-linear)

#### susan — 2026-05-04T21:34:20.380Z
**Plan ready (a-plan-linear / Hedy)**

- **Doc:** `docs/features/artifacts/ast-310-cover-letter-signature-profile-fields.md` on branch `chuckles/ast-310-cover-letter-signature-profile-fields`.
- **Commit:** `d5b150b5`
- **Self-assessment:** Scope **Single-Component** — config + DATA_SHAPES + TOKEN_SOURCES + `craft_job_cover_letter` prompt guard + `CANDIDATE_DATA_MODEL.md`; builder deferred to **AST-367**. Conf **Medium** — must stay aligned with AST-309 schema + AST-367 field names. Risk **Medium** — prompt/token mistakes could leak invented sign-offs.
- **GitHub:** https://github.com/susansomerset/astral/blob/chuckles/ast-310-cover-letter-signature-profile-fields/docs/features/artifacts/ast-310-cover-letter-signature-profile-fields.md

— Hedy (plan-linear)

#### susan — 2026-05-04T21:30:49.018Z
[check-linear] · **step 6.1 — a-plan-linear (queue mode, Hedy)**

🛑 **Planner blocked — split ownership vs single queue ticket**

**Step:** a-plan-linear step 1 (first Todo + Hedy, `orderBy: updatedAt`) returned **AST-310** after this session’s `[check-linear]` bumped `updatedAt`.

**Issue:** Linear thread (2026-04-29) already split work: **AST-365** (Ada, `resolve_tokens`), **AST-366** (Katherine, profile UI + upload), **AST-367** (Hedy, `builder.py` letterSignoff). The parent **AST-310** description still reads as a single vertical slice (profile + token + builder). Writing one binding execution plan on **`chuckles/ast-310-cover-letter-signature-profile-fields`** for all lanes would contradict that split and branch ownership.

**Proposed resolutions:**
1. Susan confirms **AST-310** stays the umbrella: I produce one **coordination plan** (sequencing + contracts only; per-child tickets get their own plan docs on their branches), **or**
2. Re-order / re-label so the **first Hedy Todo** for queue planning is **AST-367** (or another single-owner ticket), **or**
3. Susan passes an explicit ticket id for the next **a-plan-linear** run.

**Step 6.2–6.4:** **e-push-linear** — 0 issues **PR Ready** + Hedy; **d-resolve-linear** — 0 **Review Posted** + Hedy; **b-build-linear** — 0 **Plan Approved** + Hedy (no runs).

— Hedy

#### susan — 2026-05-04T21:30:04.608Z
[check-linear]

**Queue:** Hedy · Astral Artifacts (2026-04-29 pass)

- **Thread:** Your split comment (AST-365 Ada / AST-366 Katherine / **AST-367 Hedy** for `builder.py` letterSignoff) — read; no implementation requested on **AST-310** itself from this thread.
- **Action:** None in repo; **AST-367** is the Hedy-owned builder slice when that ticket is planned/approved.

— Hedy (check-linear)

#### susan — 2026-04-29T17:47:26.029Z
**Split for label-based assignment** (single Linear seat):
- **AST-365** — `{$COVER_LETTER_SIGNATURE}` in `resolve_tokens` (**Ada**, blocked by **AST-304**)
- **AST-366** — Candidate Profile fields + upload (**Katherine**)
- **AST-367** — `builder.py` letterSignoff text + image (**Hedy**)

Labels **Ada** / **Hedy** / **Katherine** on Team Astral mark ownership.

---

# AST-310 — Cover Letter Signature — Profile Fields

**Linear:** [AST-310](https://linear.app/astralcareermatch/issue/AST-310/cover-letter-signature-profile-fields)  
**Feature branch:** `<agent>/ast-310-cover-letter-signature-profile-fields` (Linear `gitBranchName`)

## Summary

Add **`candidate_data.profile.cover_letter_signature`** (multiline text) and **`candidate_data.profile.cover_letter_signature_image`** (string: URL or `data:image/jpeg;base64,...` until a dedicated upload control exists). Surface both on the **Candidate Profile** DATA_SHAPES contract so the React profile page can edit them. Register **`{$COVER_LETTER_SIGNATURE}`** in **`TOKEN_SOURCES`** so **`resolve_tokens`** injects the text sign-off into **`craft_job_cover_letter`** prompts — the model must never invent the sign-off prose. **HTML rendering** of sign-off + image in print output is **AST-367** (same epic, separate plan/branch).

⚠️ **Decision — scope split vs Linear sub-issues:** Linear maps **Ada → AST-365** (token-only duplicate), **Katherine → AST-366** (rich upload UI), **Hedy → AST-367** (builder). **This ticket’s branch** lands **DATA_SHAPES + TOKEN_SOURCES + TASK_CONFIG prompt text + data-model doc** only. If **AST-365** merges first with an identical `TOKEN_SOURCES` row, **rebase and drop duplicate** in a single commit resolving the conflict in favor of one definition. **Binary image upload widget** beyond a `text` field is explicitly **AST-366** unless Katherine’s work is already on `dev` — then this plan’s Stage 1 may narrow to documentation-only for the image field.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `DATA_SHAPES["candidates"]["detail"]["profile"]` — new subsection or fields for the two keys; `TOKEN_SOURCES["COVER_LETTER_SIGNATURE"]`; `TASK_CONFIG["craft_job_cover_letter"]` prompt strings include literal `{$COVER_LETTER_SIGNATURE}` instruction block. | utils |
| `docs/features/candidate/CANDIDATE_DATA_MODEL.md` | Document the two `profile` keys and the new token in the profile + token tables. | docs |

## Stage 1: DATA_SHAPES — profile contract

**Done when:** Candidate Profile API serves two new field defs; saving via existing profile save path persists strings under `profile` without stripping keys.

1. In `src/utils/config.py` inside `DATA_SHAPES["candidates"]["detail"]["profile"]`, add a new grouped block **"Cover letter sign-off"** (or append to **Contact Information** if you prefer fewer sections — pick one layout and document it in the Stage 1 commit message).
2. Add field `{"key": "profile.cover_letter_signature", "label": "Cover letter signature (text)", "type": "textarea"}`.
3. Add field `{"key": "profile.cover_letter_signature_image", "label": "Cover letter signature image", "type": "text"}` with **help text in `label`** suffix `"(URL or data URL; full upload UI = AST-366)"` so operators know the v1 constraint.
4. Verify `FormFields.tsx` union type `"text" | "textarea" | "select" | "toggle"` — if `Field` type in TS must be updated for any new type, extend it in the **same** Stage 1 commit only if you introduced a new `type` literal; otherwise keep `text` / `textarea` only.

## Stage 2: TOKEN_SOURCES + resolve_tokens registry

**Done when:** `get_tokens()` includes `COVER_LETTER_SIGNATURE`; `resolve_tokens("{$COVER_LETTER_SIGNATURE}", cd, "craft_job_cover_letter")` returns the multiline string from `profile.cover_letter_signature` (empty string if missing, with existing warning style for empty candidate tokens).

1. In `TOKEN_SOURCES`, add `"COVER_LETTER_SIGNATURE": {"source": "candidate", "path": "profile.cover_letter_signature"}` adjacent to other profile entries.
2. No code change inside `resolve_tokens` body is required if the registry entry follows the existing `candidate` + `path` pattern.

## Stage 3: craft_job_cover_letter prompt guardrails

**Done when:** Every prompt string on the `craft_job_cover_letter` task that asks the model for letter body explicitly includes a short **system or user** instruction that the closing sign-off is **only** what appears after token resolution of `{$COVER_LETTER_SIGNATURE}` and the model **must not** fabricate a name block or valediction beyond the structured JSON fields defined for the artifact (body / re_line per **AST-309**).

1. Locate the full `TASK_CONFIG["craft_job_cover_letter"]` entry (prompt blocks, `user_prompt`, `cache_prompt`, `nocache_prompt`, `response_schema`, etc. — mirror whatever keys exist on `dev` at implementation time).
2. Inject a single clearly delimited paragraph (ASCII, no smart quotes) in the **user** or **nocache** prompt (whichever is the primary instruction channel for this task) containing the literal substring `{$COVER_LETTER_SIGNATURE}` so `do_task` resolves it before the API call.
3. Do **not** change `response_schema` here if **AST-309** owns the structured `cover_letter` object — if `response_schema` is still a stub on `dev`, add a **Linear comment** on AST-310 pointing at AST-309 dependency rather than guessing schema keys in this ticket.

## Stage 4: Candidate data model doc

**Done when:** `CANDIDATE_DATA_MODEL.md` profile table lists both keys with token column `{$COVER_LETTER_SIGNATURE}` for the text field and “—” for the image (no token unless Susan requests one later).

1. Add two rows under `### profile`.
2. Cross-link **AST-367** for print HTML.

## Self-Assessment

**Scope — `Single-Component`**  
Config + DATA_SHAPES + one TASK_CONFIG entry + one markdown doc; no `builder.py`, no Flask, no dispatcher.

**Conf — `Medium`**  
`TASK_CONFIG` / prompt assembly is load-bearing; must align with **AST-309** artifact schema and with **AST-367** field names for `profile.cover_letter_signature_image`.

**Risk — `Medium`**  
Wrong prompt wording could let the model overwrite sign-off in free text; empty token must remain safe.

## Self-review vs ASTRAL_CODE_RULES

| Rule | Check |
|------|-------|
| §2.1 config | All new literals in `config.py` / `DATA_SHAPES` / `TOKEN_SOURCES` / `TASK_CONFIG`. |
| §1.3 DRY | Reuse `TOKEN_SOURCES` pattern; do not duplicate resolve logic. |
| §3.3 imports | No new imports from `ui` or `core` into `config.py` beyond existing graph. |

## Revisions

**Revision 1 — 2026-04-29**  
Driven by: Linear thread split (AST-365 / AST-366 / AST-367).  
Changes: Builder rendering removed from this ticket’s execution surface; confined to profile + token + prompt + doc.
