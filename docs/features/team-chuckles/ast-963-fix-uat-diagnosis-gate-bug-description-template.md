# AST-963 — fix-uat diagnosis gate + bug Description template (Deep think UAT issues)

- **Linear:** [AST-963](https://linear.app/astralcareermatch/issue/AST-963/fix-uat-diagnosis-gate-bug-description-template-deep-think-uat-issues)
- **Parent:** [AST-961](https://linear.app/astralcareermatch/issue/AST-961/deep-think-uat-issues)
- **Publish ref:** `origin/sub/AST-961/AST-963-fix-uat-diagnosis-gate-bug-description-template`
- **Summary:** Teach Chuckles’ `fix-uat` skill to diagnose each UAT problem against quoted parent AC before filing, expand the mandatory bug Description with a Diagnosis block (plus stacktrace HTML marker for later stages), and widen the one-shot parent `get_issue` token-scope so Purpose / AC / Boundaries / related child titles can feed that diagnosis without re-reading the parent comment megathread. Skills/docs only — no Astral product code.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/skills/fix-uat/SKILL.md` | Token-scope Do row for parent `get_issue`; Do-not row for full validate-plan; new §2.5 Diagnosis gate; replace Description template + filing rules (Draft A1–A3) | skill (team-chuckles) |
| `docs/features/team-chuckles/ast-963-fix-uat-diagnosis-gate-bug-description-template.md` | This plan | docs |

**Exempt / out of scope (sibling tickets):**

| Ticket | Owns |
|--------|------|
| AST-964 | `plan-child` §0a **UAT fitness** section |
| AST-965 | Thin validate §5.5/§6b wiring, Exception line naming §6b, pipeline order `plan → uat-thin → build` |

**Commit homes:** skill edit + commit in **`team-chuckles`** (symlink `~/.cursor/skills/fix-uat` already points there). Plan doc only on this astral **`origin/sub/AST-961/AST-963-fix-uat-diagnosis-gate-bug-description-template`**. Do not edit `plan-child`, `validate-plan`, or `do-all-the-things` in this ticket. Do not touch Astral `src/` / `tests/`.

---

## Stage 1: Token-scope table (Draft A1 — this ticket’s slice)

**Done when:** The Chuckles token-scope table’s parent `get_issue` **Do** cell allows Purpose / Acceptance criteria / Boundaries / Related children titles for diagnosis, and the **Do not** cell no longer blanket-bans the skill name `validate-plan` (full epic review still banned). No §6b / thin-validate Exception text yet.

1. In `~/team-chuckles/skills/fix-uat/SKILL.md`, under **## Chuckles token scope (mandatory)**, replace the **Do** cell that currently says:

   > **`get_issue`** parent **once** at start — use **status + assignee + project** fields only; ignore Description in reasoning

   with exactly this intent (wording may be tightened for table fit, but must keep every bolded concept):

   - **`get_issue`** parent **once** at start — use **status + assignee + project**, plus **Purpose / Acceptance criteria / Boundaries / Related children titles** for diagnosis and AC quotes only. Do not re-read the full parent comment thread.

2. In the same table, replace the **Do not** cell that currently lists bare **`validate-plan`**, **`audit-linear`**, **`do-all-the-things`** with:

   - **Full** `validate-plan` epic review, `audit-linear`, `do-all-the-things`

   Do **not** add an Exception / §6b / “UAT-thin” line here — that is AST-965.

⚠️ **Decision:** Narrow the validate-plan ban to **full epic** review now so parent AC6’s “no longer blanket-bans validate-plan” can land with #1’s wording, without inventing thin-validate procedure that #3 owns. AST-965 adds the Exception pointing at its new §6b.

---

## Stage 2: Diagnosis gate §2.5 (Draft A2)

**Done when:** A new **### 2.5 Diagnosis gate (mandatory before filing)** exists between §2 (Collect problems / Open questions) and §3 (File bugs), with the prompt table, ambiguity rule, and stacktrace-shaped marker instruction from Draft A2.

1. After the **Open questions** paragraph in §2 (the block that ends with stdout `AST-PPP fix-uat blocked: open questions on parent.`), insert a new subsection **before** `### 3. File bugs (mini define)`:

```markdown
### 2.5 Diagnosis gate (mandatory before filing)

For **each** problem, Chuckles must answer these **before** `save_issue`.
Stacktraces / exceptions / 5xx / console errors are **evidence**, not the job.

| Prompt | Required answer |
|--------|-----------------|
| **Symptom** | What Susan saw (quote stacktrace / UI / API once) |
| **Broken AC** | Exact parent AC sentence(s) this violates — quoted. If none apply, stop → open question `@susan` (AC may be wrong/incomplete) |
| **Hypothesis** | Likely cause in product terms (missing data, wrong branch, contract break with sibling X) — not "exception was thrown" |
| **Correct outcome** | What the user should experience if the epic + siblings are right |
| **Wrong fix to avoid** | e.g. swallow/catch-all, delete log path, return empty success, bypass sibling contract |

**Ambiguity rule:** If Chuckles cannot pick a single AC-tied hypothesis (could be "implementation bug" **or** "AC incomplete"), do **not** file — `[fix-uat]` on parent, `@susan`, stop (same as open questions).

**Stacktrace-shaped trigger** (used later for thin validate): problem text or Susan comment contains a stacktrace, exception type/message, HTTP 5xx, or "traceback". Mark the bug Description with `<!-- uat-validate: stacktrace -->` HTML comment on its own line under the title block so later stages can detect without re-parsing prose.
```

2. Keep the HTML comment string exactly `<!-- uat-validate: stacktrace -->` (AST-965 will detect this marker). Do not implement thin-validate spawn logic in this ticket.

⚠️ **Decision:** Place the marker instruction in §2.5 (filing-time) even though thin validate is AST-965 — #3 needs a stable detector string on newly filed bugs; this ticket owns introducing that string.

---

## Stage 3: Description template + filing rules (Draft A3)

**Done when:** The mandatory Description template under §3 includes **Diagnosis** and the expanded **Boundaries** ban on “no more stacktrace alone,” and filing rules require Diagnosis / escalate when Diagnosis cannot be filled.

1. Replace the entire **Description template (mandatory — copy structure, fill in):** fenced block under §3 with:

```markdown
## What failed
<observed behavior — quote UI copy, route, or API response if relevant>

## Expected
<what should happen for the user>

## Repro
1. …
2. …
_(Becomes the **Quick re-test** block on the parent `[fix-uat]` handoff comment — steps only, no full epic regression.)_

## Parent AC (quoted inline)
> <paste the exact acceptance-criterion sentence(s) from the parent — do not write "see AST-539 AC #7" or "see parent Description">

## Diagnosis
- **Hypothesis:** …
- **Correct outcome:** …
- **Wrong fix to avoid:** …
- **Related siblings / contracts:** <child ids or "none" — what must still hold after the fix>

## Boundaries
- This bug does **not** change: …
- "No more stacktrace / no more error" alone is **not** done — Parent AC + Correct outcome must hold.
```

2. When the problem is stacktrace-shaped (§2.5 trigger), the filed Description must also include, on its own line near the top of the Description body (immediately after any leading blank line / before `## What failed`):

   `<!-- uat-validate: stacktrace -->`

3. Under **Filing rules:**, keep existing bullets (`project` / `parentId` mandatory; quote AC; pull AC at file time; repro stands alone). **Add** these bullets:

   - Diagnosis block is **mandatory**. Symptom-only bugs are invalid.
   - If Susan pasted only a stacktrace, Chuckles still fills Diagnosis from parent AC + related children; if he cannot, escalate `@susan` (do not file).
   - Explicitly forbid treating “no more stacktrace / no more error” as done — Parent AC + Correct outcome in Diagnosis must hold (same sentence as Boundaries).

4. Do **not** change §4 Dispatch git, §5 Per bug pipeline order, §6 Re-prep, Token visibility, Output, or Watcher in this ticket.

---

## Stage 4: Verify and commit (team-chuckles)

**Done when:** Grep/read confirms Diagnosis gate, template, token-scope, and marker string; skill change is committed and pushed on **team-chuckles**; plan doc already on astral publish ref from `plan-child`.

1. Grep `~/team-chuckles/skills/fix-uat/SKILL.md` for:
   - `### 2.5 Diagnosis gate`
   - `## Diagnosis`
   - `<!-- uat-validate: stacktrace -->`
   - `Wrong fix to avoid`
   - `No more stacktrace`
   - Absence of live §6b / `UAT-THIN VALIDATE` / thin-validate spawn procedure (those belong to AST-965)
2. Confirm token-scope **Do** mentions Purpose / Acceptance criteria / Boundaries / Related children titles.
3. Confirm token-scope **Do not** says **Full** `validate-plan` epic review (not a bare `validate-plan` ban of the whole skill).
4. Commit in **`team-chuckles`** only the fix-uat skill file (do not stage unrelated dirty files such as `skills/rollcall/active_label.py` if still modified):  
   `code(AST-963): fix-uat diagnosis gate + UAT bug Description template`
5. Push team-chuckles to its origin. Host already symlinks `~/.cursor/skills/fix-uat` → this directory; no `install.sh` change required unless the symlink is missing (then note Code Complete: re-run `./install.sh`).
6. Append a short **Review** stub to this plan doc on the astral publish ref after build (build-child §10), listing what landed.

---

## Execution contract

- Execute stages in order; one coherent skill commit in team-chuckles covering Stages 1–3 (Stage 4 verifies + publishes).
- Do not edit AST-964 / AST-965 files or invent thin-validate pipeline steps.
- If `fix-uat/SKILL.md` structure has drifted so §2 / §3 headings no longer match this plan, stop and comment on **AST-961** with the 🛑 Stage blocked format.
- No Astral product behavior change.

---

## Self-Assessment

**Scope:** `Single-Component` — one skill file (`fix-uat/SKILL.md`) plus this plan doc; process/docs only.

**Conf:** `high` — parent Draft A1–A3 is the binding text; current skill already has token-scope table, §2/§3, and a Description template to replace in place.

**Risk:** `Medium` — wrong or missing Diagnosis gate would let symptom-only UAT bugs keep shipping; wrong token-scope could either starve diagnosis of AC quotes or re-open megathread reads. Mitigated by copying Draft A2/A3 literally and leaving thin-validate to AST-965.

## Self-review vs ASTRAL_CODE_RULES

- §1.1 Scope and Isolation — only `fix-uat` skill + plan doc; siblings explicitly exempt.
- §4.2 Documentation — single plan file under `docs/features/team-chuckles/`.
- No product layers (§2–3) touched; DRY/config/batch/state-machine rules N/A for skill markdown.
- No conflict with engineer test-tree ban — no `tests/` edits.

## Review (build stub)

**Publish ref:** `origin/sub/AST-961/AST-963-fix-uat-diagnosis-gate-bug-description-template`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `f26eadf` | Plan doc on astral sub |
| 1–3 | `team-chuckles@fb6cbbd` | Token-scope AC diagnosis; §2.5 Diagnosis gate + stacktrace marker; Description template + filing rules |

**Built:** `~/team-chuckles/skills/fix-uat/SKILL.md` — Draft A1–A3 only; no thin-validate / UAT fitness.
**Tip:** astral plan + stub (this commit); skill on `team-chuckles` `main` @ `fb6cbbd`.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-961/AST-963-fix-uat-diagnosis-gate-bug-description-template` @ `d5e421d`  
**Skill (reviewed SHA):** `team-chuckles@fb6cbbd` (`skills/fix-uat/SKILL.md`) — not later `main` tip (AST-965 sits on top).

### What's solid

| Area | Notes |
| --- | --- |
| Plan fidelity | Stages 1–3 match Draft A1–A3: token-scope Do for Purpose/AC/Boundaries/related titles; Do-not narrowed to **Full** `validate-plan` epic review; §2.5 Diagnosis gate + ambiguity escalate; Description `## Diagnosis` + “No more stacktrace” Boundaries/filing ban; marker `<!-- uat-validate: stacktrace -->` exactly. |
| AC coverage | Child AC1–4 satisfied at `fb6cbbd`. No thin-validate / §6b / UAT-THIN procedure in that SHA (AST-965). |
| Scope / Self-Assessment | Single-Component skills+plan; Conf high / Risk Medium match footprint. No `src/` / `tests/` on astral publish tip. |
| Rules | §1.1 isolation + §4.2 docs; product layers / §5f / §5g N/A. |
| Betty | Docs-only grep/read manifest — out of Radia edit scope; bible README entry matches. |

### Issues

None (**fix-now** / **discuss**).

### Recommended actions

| Severity | Item |
| --- | --- |
| — | None. |

**Verdict:** Clean — `resolve-child` may proceed (no product/skill fixes required beyond this `docs()` commit).

## Resolution

**Date:** 2026-07-23  
**Radia:** Clean — no fix-now / discuss items ([Linear](https://linear.app/astralcareermatch/issue/AST-963/fix-uat-diagnosis-gate-bug-description-template-deep-think-uat-issues)).  
**Action:** No product or skill changes. Intake Radia `docs(AST-963)` @ `c718d76`. Publish `resolve(AST-963): — clean`.
