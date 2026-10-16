# AST-2182 — Unblock AST-2176: approve reworded confidence-bounds statute text

<!-- linear-archive: AST-2182 archived 2026-10-16 -->

## Linear archive (AST-2182)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2182/unblock-ast-2176-approve-reworded-confidence-bounds-statute-text  
**Status at archive:** Archive  
**Project:** Astral Agent  
**Assignee:** unassigned  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-2172; blocks: AST-2176; related: AST-2177

### Description

**Need:** your sign-off on the reworded `stat.agent.confidence-bounds` text before [AST-2176](https://linear.app/astralcareermatch/issue/AST-2176) builds (and therefore before [AST-2177](https://linear.app/astralcareermatch/issue/AST-2177) plans against it).

Joan validated the plan with prejudice: **PROCEED**, no fix-now. Full plan + Joan findings: `docs/features/agent/ast-2176-promote-the-two-grader-statutes.md` on `sub/AST-2172/AST-2176-promote-grader-statutes`.

`_decode_payload` appears **twice** in the draft (not once), so AC 10b needs two edits.

### Edit A — Statement, line 21

**Before:**

> One sanctioned exception at decode: the encoded grade decoder (`_decode_payload`, non-vet paths) rewrites a letter segment written with confidence `0` (`{A-F}0`) to `X0`, rather than failing the line.

**After:**

> One sanctioned exception at hydrate: the structured grade hydrate (`src/core/grade_schema.py`, non-vet paths) rewrites a letter grade returned with confidence `0` (`{A-F}0`) to `X0`, rather than failing the entity.

### Edit B — Conforming example, line 32

**Before:**

> * `_decode_payload` turns encoded `CFC0` into `{"grade": "X", "confidence": 0}`; the row is no signal and the line is not a decode failure.

**After:**

> * The structured grade hydrate turns tool input `"CF": {"grade": "C", "confidence": 0}` into `{"grade": "X", "confidence": 0}`; the row is no signal and the entity is not a decode failure.

### Calls Joan flagged as yours

1. **Module path in canon:** keep `src/core/grade_schema.py` in the Statement (plan default, since AST-2178 hasn't named the function yet), or neutral "structured grade hydrate" wording only, or move the path to frontmatter `code_refs`.
2. **Edit B:** reword (plan default) or delete the bullet.
3. **Example vocabulary:** keep "not a decode failure" (matches existing `decode_failures` keys) or change to "hydrate failure".
4. **Approval date:** frontmatter `approved_at` becomes `2026-10-12` with `approved_by: Archie` unchanged; the builder will use your sign-off date if it's later.

Reply here with "approved as written" or your edits — the agents will place the text in the repo; you do not need to push. Move this ticket to **Done** when answered.

Neither [AST-2176](https://linear.app/astralcareermatch/issue/AST-2176) nor the parent [AST-2172](https://linear.app/astralcareermatch/issue/AST-2172) is assigned to you; this gate blocks both until it's Done.

### Comments

#### susan — 2026-10-12T23:41:22.007Z
I approve all of Joan's recommendations.  Please proceed.

---

_Implementation detail may live in git history on `origin/dev`._
