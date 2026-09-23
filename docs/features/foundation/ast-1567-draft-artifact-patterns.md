# AST-1567 — Draft Artifact patterns

<!-- linear-archive: AST-1567 archived 2026-09-22 -->

## Linear archive (AST-1567)

**Archived:** 2026-09-22  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1567/draft-artifact-patterns  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** susan  
**Priority / estimate:** None / —  
**Parent:** AST-1566 — Draft versioned artifacts pattern  
**Blocked by / blocks / related:** parent: AST-1566

### Description

## Execution plan

**Parent: **[AST-1566](https://linear.app/astralcareermatch/issue/AST-1566) — versioned artifacts pattern epic.

**Pass:** Single **Fable** session — draft all five interdependent `patt.artifact.*` files in one response. Land on `dev` under `canon/directives/draft/`. **No product code.**

**Model:** Claude **Fable** (thinking). Fallback: **o3** or **Opus thinking** if Fable unavailable in Joan APIs.

### Chuckles steps (when Susan returns Todo)

1. Pull audit summaries from [AST-1563](https://linear.app/astralcareermatch/issue/AST-1563), [AST-1564](https://linear.app/astralcareermatch/issue/AST-1564), [AST-1565](https://linear.app/astralcareermatch/issue/AST-1565) — use as given; do not re-derive.
2. Run **system prompt** + **task prompt** below against those inputs (codebase access only where critical; **no **`scripts/` or `debug/`).
3. Write five markdown files to `canon/directives/draft/` on `$ASTRAL_MAIN` / `dev`; commit + push.
4. Post file list + commit SHA on this ticket; assign Susan for review.

### Five deliverables

| File | Role |
| -- | -- |
| `patt.artifact.manage-catalog` | Process for new artifact keys (no key inventory in prose) |
| `patt.artifact.write-operative` | Writes + `current` flag semantics |
| `patt.artifact.read-operative` | Pinned row by key + ids |
| `patt.artifact.read-current` | Current row for UI edit path |
| `patt.artifact.no-coat-check` | Anti-pattern — no lazy fetch-if-missing |

Each file: frontmatter + §1 Abstract → §2 Arc → §3 Applications → §4 Exceptions → §5 Implementation → §6 OPEN QUESTIONS / DECISIONS.

## Done when

* Five draft files committed on `origin/dev` under `canon/directives/draft/`.
* Susan approves in-thread or requests revision on this ticket.

## Risks / open questions

* **Fable slug** — confirm at Todo before run.
* **Interdependency** — partial drafts useless; one session, all five.
* **§6 blocks** — Susan resolves open questions before ratification to `active/`.

---

## Original brief

*(Susan-approved spec — 2026-09-01)*

### System prompt (canon architect)

```
You are the Astral canon architect writing engineering directives.  
These directives are injected with Linear issues to complement the scope and constraints of a code change, whether it's a new feature or a bug or a refactor.  

Canon layout (origin/claude-canon-revision on dev):
- canon/directives/active/   — ratified patterns and statutes
- canon/directives/draft/    — proposed patterns awaiting review

Directive kinds:
- **pattern** (patt.*): reusable architectural rules — how to implement a class of change consistently. Agents and engineers cite these during plan/build/review.
- **statute** (stat.*): hard platform law — narrower, enforceable constraints referenced by patterns.

Your outputs are used directly in software engineering lifecycles. Implementing agents will decide how to code a change based on these documents. Because they are invoked early in the agent exchange, they are echoed through the context in every turn, therefore, they are intended to be concise and clear, but their composition is not cursory but deeply considered and robust to support all known use cases (see the parent ticket for examples). Be precise, concise, and operational. 

Each pattern file uses YAML frontmatter (id, kind:"pattern", scope:[related src files], point:<10-12 word upshot of the pattern for indexed references>) then:
§1 Abstract
§2 Arc — numbered lifecycle stages before / during / after
§3 Applications — when to apply
§4 Exceptions — when not to apply
§5 Implementation — rules, data definitions, architectural stipulations for today's SQLite platform
§6 OPEN QUESTIONS / DECISIONS

Forbidden in pattern prose:
- Do NOT enumerate artifact type/key names (entity names as examples are OK).
- Do NOT list ARTIFACT_CONFIG keys or other config.py values — describe process, not inventories.
- Do NOT presume extant code is "accepted exceptions" to the pattern, all anomalous code will be revised according to this pattern definition.
```

### Task prompt (single session — all five files)

```
Draft five interdependent pattern files for the Astral Artifacts. Write all five in one response because read-operative, read-current, write-operative, manage-catalog, and no-coat-check cross-reference each other.

Files (canon/directives/draft/):
1. patt.artifact.manage-catalog — how artifact keys are managed; how to implement a NEW key (e.g. a ticket "Support candidate.artifacts.base_resume") without listing existing keys
2. patt.artifact.write-operative — write to artifacts table with artifact key + entity_id + candidate_id; current-flag updates
3. patt.artifact.read-operative — fetch pinned row by artifact key + candidate_id + entity_id (replaces get_<entity>_data json abstraction for operative reads)
4. patt.artifact.read-current — fetch current content by artifact key + candidate_id (UI edit path: read-current then write-operative on save)
5. patt.artifact.no-coat-check — anti-pattern: no lazy fetch-if-missing; use component/state ingestion instead

Inputs: AST-1563/1564/1565 audit findings (job_data, company_data, candidate_data consumers); grades pin runtime artifact_id; editable UI blobs live in artifacts table.

Rules:
- Requirements-first — do not grandfather legacy blob reads or coat-check as approved exceptions
- Preserve agent_data RESPONSE and replicate it as a first version of operative artifacts
- Feasible symbols only (save_artifact, get_current_artifact, direct table query by key + ids)
- Migration/backfill out of scope
- Be brief — each file should be compact canon, not an essay
- DO NOT re-derive the analysis provided in the audit tickets. Access the code base ONLY AS IS CRITICAL to your objective.
- DO NOT consider any content relating to scripts/ or debug/ code to be in scope.

Notes:
Versioning semantics for artifacts table: same as agent_task — retire prior row (current=0), insert new UUID row (current=1).
Coat-check / lazy fetch-if-missing is obsolete — see no-coat-check anti-pattern.

Deliver: five complete markdown files ready to land under canon/directives/draft/.
```

### Comments

#### chuckles — 2026-09-02T03:35:03.071Z
[check-linear] User Testing — five implementation Tasks drafted under AST-1566, Discussion, assignee you:

AST-1568 manage-catalog → AST-1569 write-operative → AST-1570 read-current + AST-1571 read-operative (parallel) → AST-1572 no-coat-check (@susan)

#### susan — 2026-09-02T03:32:28.984Z
That's perfect!  Now I think we need to create related issues to make the necessary code changes to comply with each pattern individually.  Would you care to draft them in Discussion and assign them to me?  One ticket per pattern, and the dependency chain is fairly obvious. @chuckles

#### chuckles — 2026-09-02T03:27:14.377Z
[check-linear] User Testing — **`dev`**, not `claude-canon-revision` and no `ftr/AST-1566`.

Per AST-1566 plan: draft patterns land in `canon/directives/draft/` on **`dev`**. That is where the three commits already are (`c0b93237`, `ff021741`, `e2cdc373`). **`origin/claude-canon-revision`** was template reference only (`canon/directives/active/` shape). This is a Type=Task docs pass — no epic worktree / no `ftr/` branch.

When you ratify, we promote draft → `canon/directives/active/` on **`dev`** (or you can redirect if you want canon work isolated on `claude-canon-revision` instead — say the word).

#### susan — 2026-09-02T03:25:59.723Z
@chuckles are we committing to the claude-canon-revision branch, or to a branch for 1566.

#### chuckles — 2026-09-02T02:09:05.301Z
[check-linear] User Testing — all four remaining patt Implementation sections revised @ e2cdc373 (@susan)

#### susan — 2026-09-02T02:07:42.308Z
@chuckles did you review the others as well?

#### chuckles — 2026-09-02T01:47:04.649Z
[check-linear] User Testing — manage-catalog Implementation revised @ ff021741 (@susan)

#### susan — 2026-09-02T01:45:35.315Z
@chuckles i am confused about the implementation steps. It seems to be describing the steps for writing the pattern, not implementing a catalog entry. Can you quality check and revise the content in a new commit, please?

#### chuckles — 2026-09-01T22:48:50.472Z
[check-linear] User Testing — five draft patt links attached on ticket (@susan)

#### susan — 2026-09-01T22:47:38.516Z
@chuckles please add github links to the new files.

#### chuckles — 2026-09-01T21:49:51.519Z
Five draft patterns on `dev` @ `c0b93237`:

- `canon/directives/draft/patt.artifact.manage-catalog.md`
- `canon/directives/draft/patt.artifact.write-operative.md`
- `canon/directives/draft/patt.artifact.read-operative.md`
- `canon/directives/draft/patt.artifact.read-current.md`
- `canon/directives/draft/patt.artifact.no-coat-check.md`

Ready for your review.

#### chuckles — 2026-09-01T21:47:00.033Z
[check-linear] Discussion — agreed: manage-catalog rename, §6 open questions, agent_data RESPONSE rule, audit-as-given + no scripts/debug scope; hand Todo when ready (@susan)

#### susan — 2026-09-01T21:45:49.817Z
@chuckles Confirm you agree with the changes I have made above?

---

_Implementation detail may live in git history on `origin/dev`._
