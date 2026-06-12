# Astral Consult — project orientation

- **Linear project:** *Astral Consult*
- **This folder:** `docs/features/consult/`
- **Ticket IDs:** Consult work is **not** one contiguous AST block; use Linear as canonical. Historic examples in this folder include **AST-288** through **AST-359** and ad-hoc slugs (e.g. `response-schema-envelope-plan.md`).

## Working rules (mirror artifacts; tune per Linear)

Adapt these to match how Consult tickets are *actually* labeled in Linear. Until then, treat as **defaults**:

- Single Linear seat: use labels for assignment among **Ada**, **Hedy**, **Katherine**, **Susan**, and **Betty** when bugfix ownership is explicit. **Radia** is review-only — she finds **`Tests Passed`** work for **`e-review-linear`** via Linear **status + project** filters, not a **Radia** routing label (**b-build-linear** keeps the engineer label on the ticket through **`Code Complete`** for **Betty**).
- **Plan Ready:** keep the **engineer owner** label so the board shows who is blocked after plan review — same spirit as artifacts (**do not** swap owner to Susan for visibility alone).
- **Plan Approved:** engineer label should already be correct; remove **Susan** if it was added only for visibility.
- **Code Complete** (**b-build-linear**): **keep** the implementing engineer label (**Ada** / **Hedy** / **Katherine**). Do **not** swap it to **Radia**. Name the implementer in a **comment** (e.g. `Built by Ada.`) so Radia knows who receives review feedback. Preserve Conf / Risk / Scope (and **Feature** if used).
- **Review Posted** (**e-review-linear**): ensure the engineer label matches comments; remove **Radia** if still present (**legacy**). Preserve Conf / Risk / Scope.
- **Testing / resolve:** follow **f-resolve-linear** (or Consult’s equivalent) for assignee and label cleanup.
- Sign Linear comments with engineer name (e.g. **— Ada**).
- Parent/child splits: cite `Owner: PARENT>CHILD` in comments when work is split.

## Team mapping (default; adjust if Consult differs)

- **Ada / Hedy / Katherine:** implementation owners (same rough split as org norms — Consult-heavy logic often touches `consult.py` + `config.py` + `agent.py`).
- **Susan:** product/prompt acceptance and ambiguous scope calls.
- **Radia:** code review only — **e-review-linear**, diff vs `dev`, no direct code commits on the reviewed branch.
- **Betty:** bugfix branches from **astral-betty** / `worktree/betty`, same review-before-merge-to-local-`dev` pattern as other engineers.

## Radia (code review)

Same workflow family as Artifacts:

- Run **e-review-linear** from **astral/** (or **astral-radia**); compare **`origin/<branch>`** vs **`origin/dev`** after **`git fetch`** (see that SKILL for fallbacks).
- Append findings to the **combined feature doc** for the ticket (What’s solid, issues, recommended actions) — for **new** tickets prefer **one** `ast-NNN-slug.md` file (see below); for legacy split files, use the `-review` doc or a agreed section header.
- Post a short Linear summary with a link to the doc.

## Document conventions (this folder)

**Target shape (match artifacts):**

- One primary file per ticket: `ast-<id>-<kebab-topic>.md`
- Inside that file, use **headings** for lifecycle: Plan → Radia review → Resolution / implementation notes, instead of scattering across three filenames.

**Legacy shape (keep until merged):**

- Older work may use `ast-NNN-topic-plan.md` + `ast-NNN-topic-review.md`. When you next touch a ticket, **merge** into a single `ast-NNN-kebab.md` if practical.

**Cross-ticket architecture** (no single Linear id): `kebab-descriptive-name.md` is fine (e.g. `response-schema-envelope-plan.md`).

**Front matter block (recommended)** — paste at top of new feature docs:

```markdown
# AST-NNN — Short Title

**Linear:** [AST-NNN](https://linear.app/…/AST-NNN/…) — short slug  
**Project:** _(Consult — confirm)_  
**Priority / estimate:** … / …  
**Blocks / blocked by:** _(from Linear relations)_
```

Then follow [FEATURE_DOC_TEMPLATE.md](FEATURE_DOC_TEMPLATE.md) for body sections.

## Dependency highlights

*Maintain a short bullet list here once Susan defines the Consult dependency spine (e.g. encoded responses → grading density → dispatch records). Until then, use Linear `blockedBy` / `relatedTo` as canonical.*

## Pointers

- Architecture overview: [project_description.md](project_description.md)
- Assignment / epic diagram: *add `consult-dependency-overview.md` or link a Linear view when ready*
- Astral orientation (workflow, MCP, Artifacts notes): `~/.cursor/skills/0-agent-orientation/SKILL.md`; diagram: `docs/features/artifacts/unified-assignment-diagram.md`

