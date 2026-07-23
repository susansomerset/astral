# AST-964 — plan-child UAT fitness (Deep think UAT issues)

- **Linear:** [AST-964](https://linear.app/astralcareermatch/issue/AST-964/plan-child-uat-fitness-deep-think-uat-issues)
- **Parent:** [AST-961](https://linear.app/astralcareermatch/issue/AST-961/deep-think-uat-issues)
- **Publish ref:** `origin/sub/AST-961/AST-964-plan-child-uat-fitness`
- **Summary:** Extend `plan-child` §0a so every FIX-UAT / `UAT:` plan patch must include a **UAT fitness** section (AC restored, correct outcome, sibling check, “stacktrace gone ≠ done,” wrong fix rejected) immediately after the summary and before Files Changed; Plan Ready without it is invalid. Planner stops and asks Chuckles to re-file if the bug Description lacks Diagnosis / Parent AC quotes — does not invent AC. Skills/docs only.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/team-chuckles/skills/plan-child/SKILL.md` | Append Draft B UAT fitness block to §0a; add Structure placement rule for UAT plans | skill (team-chuckles) |
| `docs/features/team-chuckles/ast-964-plan-child-uat-fitness.md` | This plan | docs |

**Exempt / out of scope:**

| Ticket | Owns |
|--------|------|
| AST-963 | `fix-uat` diagnosis gate + bug Description template |
| AST-965 | validate-plan UAT-thin + fix-uat thin-validate trigger |

**Commit homes:** skill edit + commit in **`team-chuckles`** (`~/.cursor/skills/plan-child` is a symlink). Plan doc only on this astral **`origin/sub/AST-961/AST-964-plan-child-uat-fitness`**. Do not edit `fix-uat`, `validate-plan`, or Astral `src/` / `tests/`.

---

## Stage 1: Append UAT fitness to §0a (Draft B)

**Done when:** §0a ends with the mandatory **UAT fitness** requirements and the planner re-file rule from Draft B; existing §0a read/skip bullets are unchanged.

1. In `~/team-chuckles/skills/plan-child/SKILL.md`, locate **`### 0a. UAT bug fast path (\`FIX-UAT MODE\`)`**. Keep the existing five bullets (Read orientation Branch law, Read ticket/parent/plan, Skip six skills, ASTRAL_CODE_RULES relevant-only, `--resume` reuse) unchanged.
2. Immediately after those bullets (still under §0a, before **`### 1. Resolve which ticket(s) to plan`**), append this block verbatim in intent (heading level and bolding as shown):

```markdown
### 0a. UAT bug fast path (`FIX-UAT MODE`) — continued

**UAT fitness (mandatory in the plan patch for every `UAT:` / FIX-UAT MODE ticket):**

Before Stages, the plan doc **must** include this section (reject Plan Ready without it):

## UAT fitness

- **AC restored:** <quote the Parent AC sentence(s) from the bug Description this change satisfies>
- **Correct outcome:** <from bug Diagnosis — user-visible success, not "error gone">
- **Sibling check:** <related children / contracts from bug Diagnosis — still hold? how verified?>
- **Not sufficient:** Removing the stacktrace / exception / 5xx alone is **not** done.
- **Wrong fix rejected:** <why the obvious symptom patch is wrong, or "N/A — hypothesis matches AC and no safer alternative">

Planner rule: if the bug Description lacks Diagnosis / Parent AC quotes, **stop** and comment on the **bug** (not parent) asking Chuckles to re-file — do not invent AC.
```

⚠️ **Decision:** Use a “— continued” subheading under the same §0a rather than renumbering §1+, so existing skill cross-refs to §0a / §1 stay stable. Content must match Draft B; do not soften “reject Plan Ready without it.”

---

## Stage 2: Structure placement rule (Draft B)

**Done when:** Under **#### Structure**, UAT plans are required to place **UAT fitness** immediately after the summary paragraph and before **Files Changed**.

1. In the same file, under **#### Structure**, after the **Header** bullet list (Title / Linear link / Publish ref / One-paragraph summary) and **before** the **`Files Changed (planned)`** heading, add one rule paragraph (or short bullet list) that states:

   - When the ticket title starts with **`UAT:`** **or** the spawn prompt says **`FIX-UAT MODE`**, the plan doc **must** include **`## UAT fitness`** immediately after the summary paragraph and **before** **Files Changed**.
   - Plan Ready without that section is **invalid** (same gate as §0a continued).

2. Do not reorder or rewrite the rest of Structure (Files Changed table example, Stages, Done when, Decisions).

---

## Stage 3: Verify and commit (team-chuckles)

**Done when:** Grep confirms UAT fitness language and “stacktrace alone is not done”; skill committed/pushed on team-chuckles; no validate-plan / fix-uat edits.

1. Grep `~/team-chuckles/skills/plan-child/SKILL.md` for:
   - `## UAT fitness`
   - `AC restored`
   - `Not sufficient`
   - `do not invent AC`
   - Placement rule tying `UAT:` / `FIX-UAT MODE` to fitness before Files Changed
2. Confirm no new validate-plan / fix-uat procedure was introduced.
3. Commit in **`team-chuckles`** only the plan-child skill file (do not stage unrelated dirty files):  
   `code(AST-964): plan-child mandatory UAT fitness for FIX-UAT plans`
4. Push team-chuckles to its origin. Symlink already covers `~/.cursor/skills/plan-child`.
5. Append a short **Review** stub to this plan doc on the astral publish ref after build (build-child §10).

---

## Execution contract

- Stages in order; one skill commit covering Stages 1–2 (Stage 3 verifies + publishes).
- Do not absorb AST-963 Diagnosis template or AST-965 thin-validate into this skill.
- If §0a / Structure headings have drifted so insertion points are missing, stop and comment on **AST-961** with the 🛑 Stage blocked format.
- No Astral product behavior change.

---

## Self-Assessment

**Scope:** `Single-Component` — one skill file (`plan-child/SKILL.md`) plus this plan doc.

**Conf:** `high` — parent Draft B is the binding text; §0a and Structure exist and have clear append/insert points.

**Risk:** `Medium` — omitting or weakening UAT fitness would let symptom-only UAT plans reach Plan Ready again; mitigated by copying Draft B literally and dual placement (§0a + Structure).

## Self-review vs ASTRAL_CODE_RULES

- §1.1 Scope and Isolation — only `plan-child` + plan doc; siblings exempt.
- §4.2 Documentation — single plan under `docs/features/team-chuckles/`.
- Product layer rules (§2–3) N/A for skill markdown.
- No `tests/` edits.

## Review (build stub)

**Publish ref:** `origin/sub/AST-961/AST-964-plan-child-uat-fitness`

| Stage | Commit | Summary |
|-------|--------|---------|
| plan | `8ff3854` | Plan doc on astral sub |
| 1–2 | `team-chuckles@8a74376` | §0a UAT fitness continued + Structure placement before Files Changed |

**Built:** `~/team-chuckles/skills/plan-child/SKILL.md` — Draft B only; no fix-uat / validate-plan edits.
**Tip:** astral plan + stub (this commit); skill on `team-chuckles` `main` @ `8a74376`.

## Review (Radia)

**Diff:** `origin/dev...origin/sub/AST-961/AST-964-plan-child-uat-fitness` @ `3eb58b4`  
**Skill (reviewed SHA):** `team-chuckles@8a74376` (`skills/plan-child/SKILL.md`).

### What's solid

| Area | Notes |
| --- | --- |
| Plan fidelity | Stages 1–2 = Draft B: §0a “— continued” with mandatory `## UAT fitness` (AC restored / Correct outcome / Sibling check / Not sufficient / Wrong fix rejected) + re-file / do-not-invent-AC; Structure placement after summary before Files Changed; Plan Ready without it invalid. Existing §0a five bullets untouched. |
| AC coverage | Child AC3–4 met at `8a74376` (“stacktrace alone ≠ done” via **Not sufficient**). No fix-uat / validate-plan / thin-validate smuggle (AST-963/965). |
| Scope / Self-Assessment | Single-Component skills+plan; Conf high / Risk Medium match +18-line skill footprint. No `src/` / `tests/` on astral tip. |
| Rules | §1.1 / §4.2; product / §5f / §5g N/A. |
| Betty | Docs-only grep/read manifest — out of Radia edit scope; bible README entry matches. |

### Issues

None (**fix-now** / **discuss**).

### Recommended actions

| Severity | Item |
| --- | --- |
| — | None. |

**Verdict:** Clean — `resolve-child` may proceed (no product/skill fixes required beyond this `docs()` commit).
