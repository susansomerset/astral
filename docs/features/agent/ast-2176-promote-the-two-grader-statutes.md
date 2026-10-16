# AST-2176 — Promote the two grader statutes

- **Linear:** [AST-2176](https://linear.app/astralcareermatch/issue/AST-2176) · parent [AST-2172](https://linear.app/astralcareermatch/issue/AST-2172) (Enforced structured output for rubric graders)
- **Publish ref:** `origin/sub/AST-2172/AST-2176-promote-grader-statutes`
- **Assignee:** Katherine

This child moves `stat.agent.grade-vector-validation` and `stat.agent.confidence-bounds` from `canon/directives/draft/` to `canon/directives/active/`, which puts them in force (`canon/canon_clerk.py` only serves `active/`). It also rewords the `confidence-bounds` sanctioned `{A-F}0` → `X0` exception so it names the structured hydrate rather than `_decode_payload`, because AST-2172 deletes that function. There is no product code and no test work. It blocks every sibling: canon has to be in force before #2–#6 plan against it, and Susan approves the reworded text (below) before AST-2177 plans.

## Findings that shape this plan

Both were verified with a dry run against a throwaway copy of `canon/` (`CANON_ROOT=<tmp>`); the worktree was not touched.

1. **A plain move fails AC 10b.** `canon_clerk._read_directive` takes the id from the frontmatter `id:` field and only falls back to the filename stem when `id:` is absent. Both drafts carry the pre-v2 id (`id: astral.agent.grade-vector-validation`, `id: astral.agent.confidence-bounds`). After a plain move, `canon_clerk.py index` lists `astral.agent.*` and not `stat.agent.*`. With `id:` changed to the filename stem, it lists both `stat.agent.*` ids and `expand stat.agent.grade-vector-validation stat.agent.confidence-bounds` resolves 2.
2. **`_decode_payload` appears twice in `confidence-bounds`, not once.** Line 21 is the `# Statement` sentence the ticket names. Line 32 is a `### Conforming` example bullet. AC 10b (`rg -n '_decode_payload' canon/directives/active` returns nothing) cannot pass unless both are reworded.

Everything else in the drafts is left alone: the pre-v2 frontmatter fields (`tier`, `checkable`, `status`, `source_docs`) and section headings (`# Statement` / `# Rationale` / `# Examples`). The clerk tolerates the pre-v2 shape (kind, scope and point all fall back), and the parent's Technical scope says "No other wording changes."

## Proposed wording — for Susan's approval (before AST-2177 plans)

The hydrate's module is fixed by the parent's Component scope (`src/core/grade_schema.py`, AST-2178 / child #3). Its function name is Hedy's call, so the wording names the module and not a function. That way canon doesn't go stale again when #3 names the function.

### Edit A — `# Statement`, sanctioned-exception sentence (line 21)

**Before:**

> One sanctioned exception at decode: the encoded grade decoder (`_decode_payload`, non-vet paths) rewrites a letter segment written with confidence `0` (`{A-F}0`) to `X0`, rather than failing the line.

**After:**

> One sanctioned exception at hydrate: the structured grade hydrate (`src/core/grade_schema.py`, non-vet paths) rewrites a letter grade returned with confidence `0` (`{A-F}0`) to `X0`, rather than failing the entity.

Word-level delta: `at decode` → `at hydrate`; `the encoded grade decoder (`_decode_payload`, …)` → `the structured grade hydrate (`src/core/grade_schema.py`, …)`; `letter segment written` → `letter grade returned` (a tool reply has no segments); `failing the line` → `failing the entity` (a structured reply has no line; failures are per entity, per the parent's Functional scope 8). `non-vet paths`, `{A-F}0`, `X0` and every other sentence in the Statement stay as written.

### Edit B — `### Conforming`, second bullet (line 32)

**Before:**

> - `_decode_payload` turns encoded `CFC0` into `{"grade": "X", "confidence": 0}`; the row is no signal and the line is not a decode failure.

**After:**

> - The structured grade hydrate turns tool input `"CF": {"grade": "C", "confidence": 0}` into `{"grade": "X", "confidence": 0}`; the row is no signal and the entity is not a decode failure.

⚠️ **Decision:** Reword Edit B rather than deleting the bullet. AC 10b forces a change here, and the ticket's "one sentence amended" undercounts the occurrences. Rewording keeps the only conforming example for the sanctioned exception, and it is the same kind of change as Edit A in the same in-scope file. If Susan prefers to delete the bullet, Stage 2 step 4 becomes "delete line 32" and nothing else changes.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `canon/directives/draft/stat.agent.grade-vector-validation.md` → `canon/directives/active/stat.agent.grade-vector-validation.md` | `git mv`; frontmatter `id:` + `approved_at:` | canon |
| `canon/directives/draft/stat.agent.confidence-bounds.md` → `canon/directives/active/stat.agent.confidence-bounds.md` | `git mv`; frontmatter `id:` + `approved_at:`; Edits A and B | canon |

No other file. Explicitly **not** touched (they're out of scope, and not served by the clerk or owned by a sibling):
- `canon/statutes/astral/agent/astral.agent.*.md` are the legacy pre-v2 copies. They aren't in `directives/active/`, so the clerk never serves them.
- `canon/statutes/HARVEST.md` and `canon/docs/DIRECTIVE-ANATOMY.md` §2 still mention the `astral.agent.*` ids. These are historical/explanatory only.
- `src/core/agent.py:429` has a comment naming `astral.agent.confidence-bounds`. That file belongs to AST-2180 (child #5), which deletes the decoder around it.

## Stage 1: Move both drafts to active (rename only)

**Done when:** `git show --stat HEAD` shows exactly two renames at 100% similarity, `draft/` → `active/`, and no content change.

`canon/docs/DIRECTIVE-ANATOMY.md` §1: "Activating or retiring a directive is a `git mv` in its own commit." So this stage is renames only.

1. In the epic worktree `/home/susan/astral-AST-2172/`, run:
   ```bash
   git mv canon/directives/draft/stat.agent.grade-vector-validation.md canon/directives/active/stat.agent.grade-vector-validation.md
   git mv canon/directives/draft/stat.agent.confidence-bounds.md canon/directives/active/stat.agent.confidence-bounds.md
   ```
2. Check: `git status --short` lists exactly two `R` lines, the two above, and nothing else staged.
3. Commit: `git commit -m "code(AST-2176): canon — promote stat.agent.grade-vector-validation + stat.agent.confidence-bounds to active"`.
4. Publish per build-child (`git push origin HEAD:sub/AST-2172/AST-2176-promote-grader-statutes`).

Between Stage 1 and Stage 2 the index transiently lists `astral.agent.*`. Stage 2 fixes that, and nothing plans against this sub in between.

## Stage 2: Frontmatter ids, approval date, and the confidence-bounds rewording

**Done when:** all three AC 10b checks in step 6 pass and `git diff HEAD~1 --stat` touches only the two `active/` files.

1. In `canon/directives/active/stat.agent.grade-vector-validation.md`, line 2: change `id: astral.agent.grade-vector-validation` to `id: stat.agent.grade-vector-validation`.
2. In `canon/directives/active/stat.agent.confidence-bounds.md`, line 2: change `id: astral.agent.confidence-bounds` to `id: stat.agent.confidence-bounds`.
3. In `canon/directives/active/stat.agent.confidence-bounds.md`, line 21: replace the **Before** text of Edit A with its **After** text, character for character. Every other sentence on that line stays byte-identical.
4. In `canon/directives/active/stat.agent.confidence-bounds.md`, line 32: replace the **Before** bullet of Edit B with its **After** bullet, character for character.
5. In **both** files, change `approved_at: "2026-07-23"` to `approved_at: "2026-10-12"`. Leave `approved_by: Archie` as it is.

   ⚠️ **Decision:** The parent's Technical scope asks for "Archie approval recorded in frontmatter". `approved_by: Archie` is already there, but dated 2026-07-23, before the promotion decision and before the reworded text. `2026-10-12` is the date of the parent's "Decisions from Discussion (Susan, 2026-10-12)", where promotion was approved. If Susan's wording approval on AST-2176 lands on a later date and she wants that date instead, she says so on AST-2176 and the builder uses it. No other frontmatter field changes.
6. Verify AC 10b (these are the commands named in the AC):
   ```bash
   python3 canon/canon_clerk.py index | rg -n '^stat\.agent\.(grade-vector-validation|confidence-bounds)  '   # expect 2 lines
   python3 canon/canon_clerk.py index | rg -c 'astral\.agent\.'                                          # expect 0 (rg exit 1)
   rg -n '_decode_payload' canon/directives/active                                                      # expect no output (rg exit 1)
   python3 canon/canon_clerk.py expand stat.agent.grade-vector-validation stat.agent.confidence-bounds \
     | python3 -c 'import json,sys; assert json.load(sys.stdin)["resolved"] == 2'                        # expect exit 0
   ```
   If any check fails, stop and comment on AST-2172. Don't adapt.
7. Lint/compile gate (there's no Python change; this confirms the clerk still parses the whole active corpus): `python3 canon/canon_clerk.py index > /dev/null && echo ok`.
8. Commit: `git commit -am "code(AST-2176): canon — stat.agent ids, approval date, confidence-bounds names the structured hydrate"`. Check first with `git status --short` that only the two `active/` files are modified.
9. Publish per build-child (`git push origin HEAD:sub/AST-2172/AST-2176-promote-grader-statutes`).

## Notes for reviewers (non-normative)

- Pre-commit hooks are not installed in this epic worktree (known installer bug with git worktrees). Don't try to install them. This ticket touches neither `tests/` nor the bible.
- `grade-vector-validation`'s Statement still names `TASK_CONFIG` / `do_task`. It's unchanged here because the ticket says "No other wording changes" and its id/scope doesn't name a deleted function. If Joan or Susan wants it modernized, that's a separate ask.
- `origin/ftr/AST-2172` didn't exist on origin at plan time (`sync-child.sh` skipped it). That's harmless for this ticket, which is first in the chain.

## Estimate

Confirm Chuckles estimate: 1 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-2176
**Overall:** APPROVED
**Corpus:** 0d01e20d2b313a4e35cf3d07434b6cd69f615768
**Publish ref:** `origin/sub/AST-2172/AST-2176-promote-grader-statutes` @ `c2700dfb0`

## Canon scores

Ticket **Citations:** `none` (dispatch-parent: bootstrap child; scored on AC 10b, not a frozen Radia list). No R3 rows — roll-up N/A.

Adversarial read of the **promoted directive text the plan commits to** (vs parent AST-2172 canon Technical scope, Functional scope §4/§8, AC 10b):

| Subject | Grade | Effort | One-line |
|---------|-------|--------|----------|
| `stat.agent.confidence-bounds` (Edits A+B + id/frontmatter) | B | — | AC-driven second edit is right; module path + “decode failure” in example need Archie/Susan eyes |
| `stat.agent.grade-vector-validation` (move + id only) | A | — | |

## Traceability

**10b** → Stage 1 (`git mv` both drafts → `active/`) + Stage 2 (frontmatter `id:` → `stat.agent.*`, Edits A+B, `approved_at`, step 6 clerk/`rg` checks). No orphan stages; parent AC 1–11 / 10a are N/A for this child.

## Findings

### discuss

- **Location:** Plan “Proposed wording” / Edit A — `src/core/grade_schema.py` in Statement  
  **Finding:** Parent Technical scope names the hydrate module in Component scope (#3) but the statute body will cite a **file path** instead of a function or neutral “structured grade hydrate.” Reasonable anti-drift vs deleted `_decode_payload`, but statutes usually avoid path literals unless Archie wants `code_refs` discipline.  
  **Recommendation:** Archie chooses: keep module path (plan default), generic hydrate wording only, or frontmatter `code_refs` + shorter Statement.

- **Location:** Edit B — reword vs delete (plan ⚠️ Decision)  
  **Finding:** AC 10b requires clearing **both** `_decode_payload` hits (draft lines 21 and 32); parent dispatch text still says “one sentence amended” while parent AC 10b is the stricter gate. Plan correctly rewords the conforming bullet; deleting it would drop the only worked example for the sanctioned exception.  
  **Recommendation:** Susan: reword (plan) vs delete bullet; Chuckles may align child **Scope** text on AST-2176 with “two occurrences” so dispatch doesn’t contradict the plan.

- **Location:** Stage 2 step 5 — `approved_at: "2026-10-12"`, `approved_by: Archie` unchanged  
  **Finding:** Promotion date tracks Discussion (2026-10-12); **reworded** Statement/example is new normative text. `approved_by: Archie` is present but predates the hydrate wording. Parent requires Archie approval in frontmatter; ticket also requires **Susan** wording approval before #2 plans.  
  **Recommendation:** Archie signs final sentence text (separate from Joan); Susan signs proposed block in plan; builder uses Susan’s date if it slips past 2026-10-12 (plan already allows).

- **Location:** Edit B after text — “the entity is not a **decode** failure”  
  **Finding:** Statement moves to “hydrate” / “entity”; example still uses decode vocabulary while downstream may keep `decode_failures` keys (parent AC 5–6). Not necessarily wrong, but mixed metaphor.  
  **Recommendation:** Archie optional polish: “hydrate/check failure” vs keep “decode failure” for continuity with existing keys/logs.

### acceptable

- **Location:** Files Changed — out-of-scope references  
  **Finding:** `astral.agent.*` remains in legacy `canon/statutes/`, HARVEST/DIRECTIVE-ANATOMY, test-bible/history, and `src/core/agent.py:429` comment (`astral.agent.confidence-bounds`). Clerk serves only `directives/active/`; plan defers agent comment to AST-2180. No AC 10b violation.  
  **Recommendation:** None for this child.

- **Location:** Stage 1 → Stage 2 gap  
  **Finding:** Transient index shows `astral.agent.*` ids after rename-only commit; plan forbids planning against the sub in between. Matches DIRECTIVE-ANATOMY §1 (activate in own commit).  
  **Recommendation:** Execute as written.

- **Location:** Stage 1/2 commit subjects `code(AST-2176):`  
  **Finding:** Canon-only touches; some repos use `docs()` for canon. Low process variance.  
  **Recommendation:** Builder may follow epic convention; not a plan defect.

- **Location:** `grade-vector-validation` body — `TASK_CONFIG` / `do_task`  
  **Finding:** Pre-v2 wording; parent “No other wording changes.” Parent FS §3–§8 describe structured graders; statute still describes post-schema `do_task` validation — siblings #3/#5 must reconcile in implementation, not in this promotion.  
  **Recommendation:** Note for later epic pass; out of AST-2176 scope.

### fix-now

(none)

## R5 / R6 (condensed)

- Parent **Functional scope §4** and **AC 10b**: plan delivers `stat.agent.*` in clerk index, zero `_decode_payload` under `canon/directives/active`, expand resolves both ids (step 6).  
- **Technical scope** “one modified sentence” vs two edits: resolved by child AC 10b and plan Findings §1 — not a plan error.  
- **Id-line `astral.agent.*` → `stat.agent.*`:** Required for AC; `_read_directive` uses frontmatter `id:` (plan Finding 1 verified against clerk).  
- **Edit A accuracy:** Matches current non-vet behavior (`agent.py` letter+conf 0 → X0, AST-2124) and parent hydrate direction; `non-vet paths` preserved.  
- **Edit B accuracy:** `CFC0` ↔ `"CF": {grade C, conf 0}` → `X0` is faithful to AST-2124 semantics on the future structured path.  
- Self-assessment / estimate 1: honest for two-commit canon work.  
- Plan Discuss: **0** completed rounds; status **Plan Ready**, assignee Joan — gate satisfied.

**Archie must decide:** statute cites **module path** vs neutral hydrate naming; **Edit B** keep vs delete; optional **decode vs hydrate** wording in example; **frontmatter approval** moment for reworded text relative to Susan’s wording OK.

context_tokens≈42000

## Review (build)

**Built @ `b7ab22030`** — `origin/sub/AST-2172/AST-2176-promote-grader-statutes`

Stage 1 (`2c57d7ba0`): `git mv` both drafts → `canon/directives/active/` (pure renames). Stage 2 (`b7ab22030`): frontmatter `id:` → `stat.agent.*`, `approved_at: "2026-10-12"` on both, Edits A + B exactly as approved on AST-2182. AC 10b checks (plan Stage 2 step 6) all pass: index lists both `stat.agent.*` ids, zero `astral.agent.*`, zero `_decode_payload` under `active/`, `expand` resolves 2. No product code, no tests.

## Radia review

[code-rubric]

**Ticket:** AST-2176  
**Publish ref:** `673e6cd4e3deaae1a9447524244882d8efbadbb1` (`origin/sub/AST-2172/AST-2176-promote-grader-statutes`)  
**Corpus:** `b7ab2203048ce0beb2869a12200ab7fa696c8066` (last commit touching `canon/`; worktree `canon/` clean — not DIRTY)  
**Overall:** CLEAN  

## Canon scores

Frozen list empty (Linear **Citations:** `none` — bootstrap child; AC 10b is the engineering gate, not a frozen Radia directive list). No directive ids to score; not §5.3 ESCALATE (explicit empty scope, same posture as Joan validate).

## Column diff vs plan stage

(aligned) — Joan recorded no R3 rows; adversarial plan read graded promoted **text** (`confidence-bounds` B, `grade-vector-validation` A). Tip canon matches Stage 2 Edits A+B, frontmatter `stat.agent.*` ids, and `approved_at: "2026-10-12"` as documented (“exactly as approved on AST-2182”). No plan-stage vs diff divergence on the empty frozen list.

## Frame diff

- [ ] **Scope** (Linear Description): change “one sentence amended” → “`confidence-bounds` Statement + Conforming example reworded (two `_decode_payload` removals); `grade-vector-validation` move + id only” so dispatch text matches AC 10b and the landed diff.

## Findings

### fix-now

(none)

### discuss

(none) — Joan’s plan-stage wording / approval threads are reflected in the built active directives; AST-2182 is recorded as the approval anchor in the build stub. Remaining statute polish (module path vs neutral hydrate, “decode failure” phrasing in Edit B, `TASK_CONFIG`/`do_task` in `grade-vector-validation`) is epic follow-up for siblings #3/#5 or a separate canon pass, not a blocker on this promotion slice.

### advisory

- **Location:** `origin/dev...673e6cd4e` history — commit `673e6cd4e` `sync(dev): origin/dev`  
  **Finding:** Tip history merges current `origin/dev` (includes AST-2173/2174 search stack). Three-dot diff vs `origin/dev` for this review is still **canon + docs only**; Betty manifest item 5 holds (`git diff origin/dev -- src/ tests/` empty on tip).  
  **Recommendation:** Treat as epic hygiene; no AST-2176 product scope leak.

- **Location:** `canon/directives/active/stat.agent.confidence-bounds.md` — Edit B bullet  
  **Finding:** Statement uses “hydrate” / “entity”; conforming example still says “decode failure” (Joan noted mixed metaphor vs future `decode_failures` keys).  
  **Recommendation:** Optional Archie polish later; default: leave as shipped.

- **Location:** `canon/directives/active/stat.agent.grade-vector-validation.md` — `# Statement`  
  **Finding:** Still names `TASK_CONFIG` / `do_task` (pre-v2 body unchanged per plan). Siblings must reconcile with structured grader work; out of this child’s boundaries.  
  **Recommendation:** Note for AST-2178/AST-2180 planning; not fix-now here.

- **Location:** Out-of-scope `astral.agent.*` references (legacy `canon/statutes/`, HARVEST, `src/core/agent.py` comment)  
  **Finding:** Clerk serves only `directives/active/`; AC 10b satisfied.  
  **Recommendation:** AST-2180 owns agent comment cleanup per plan.

- **Location:** Commits `2c57d7ba0`, `b7ab22030` — message prefix `code(AST-2176):`  
  **Finding:** Canon-only touches; some epics use `docs()` for canon.  
  **Recommendation:** Process variance only.

## What's solid

- **Stage 1** (`2c57d7ba0`): pure `draft/` → `active/` renames for both statutes.  
- **Stage 2** (`b7ab22030`): `id:` → `stat.agent.*`, `approved_at: "2026-10-12"`, Edits A+B match the approved plan block; no `_decode_payload` under `canon/directives/active/`.  
- **AC 10b (re-run on worktree @ tip):** index lists both `stat.agent.*` lines; `expand` resolves `2`; draft paths absent; `astral.agent.*` absent from clerk index; `rg` clean on `active/`.  
- **Boundaries:** no `src/**` or `tests/**` delta vs `origin/dev` on tip; Betty docs-acceptance manifest in `docs/test-bible/README.md` matches executed checks.  
- **Estimate:** confirmed **1** — footprint fits two-commit canon + docs.

## Recommended actions (downstream only — not executed here)

- Chuckles: append this artifact to `docs/features/agent/ast-2176-promote-the-two-grader-statutes.md`, `docs(AST-2176): Radia review — clean`, push `sub/AST-2172/AST-2176-promote-grader-statutes`, post slim upshot `--as radia`, **Review Posted** → datt **PROCEED** toward **User Testing** (no `resolve-child` code fixes from this review).  
- Optional: tick **Frame diff** Scope row on Linear after Susan confirms wording gate for AST-2177 is satisfied via AST-2182.

context_tokens≈28000

