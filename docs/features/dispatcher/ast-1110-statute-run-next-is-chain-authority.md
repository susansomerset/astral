# Statute — run_next is chain authority

**Linear:** [AST-1110](https://linear.app/astralcareermatch/issue/AST-1110/statute-run-next-is-chain-authority-hard-coded-daisy-chain-in-configpy)  
**Parent:** [AST-1109](https://linear.app/astralcareermatch/issue/AST-1109/hard-coded-daisy-chain-in-configpy) — Hard-coded daisy chain in config.py  
**Publish ref:** `sub/AST-1109/AST-1110-statute-run-next-is-chain-authority`

Land Archie-approved statute `astral.dispatch.run-next-is-chain-authority` (config must not shadow DB-owned `agent_task.run_next` chain membership / hop succession), register it in the statute corpus, point CODE_RULES at it, and add a **proposed** catalog entry `pattern.dispatch.run-next-chain-authority` for sibling remediations. No product routing, config frozenset deletes, or boot SQL in this child — those are AST-1111 / AST-1112 / AST-1113.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `canon/statutes/astral/dispatch/astral.dispatch.run-next-is-chain-authority.md` | New active scoped statute (SCHEMA + AUTHORING) | docs/canon |
| `canon/statutes/README.md` | Add harvested-corpus row; bump active count 57→58 | docs/canon |
| `canon/statutes/HARVEST.md` | Add crosswalk row; bump Counts | docs/canon |
| `canon/patterns/dispatch/pattern.dispatch.run-next-chain-authority.md` | New **proposed** pattern (SCHEMA + AUTHORING) | docs/canon |
| `canon/patterns/README.md` | Add harvested-corpus row; note proposed status | docs/canon |
| `canon/patterns/HARVEST.md` | Add crosswalk row for the proposed pattern | docs/canon |
| `docs/ASTRAL_CODE_RULES.md` | Pointer to new statute at §2.6.0 (+ one clarifying sentence) | docs |

## Stage 1: Canon statute `astral.dispatch.run-next-is-chain-authority`

**Done when:** Active statute file exists at the SCHEMA path; README harvested table + HARVEST crosswalk list it; id is `astral.dispatch.run-next-is-chain-authority`; active corpus count text is **58**.

1. Create `canon/statutes/astral/dispatch/astral.dispatch.run-next-is-chain-authority.md` with YAML frontmatter (all SCHEMA keys, no extras):

```yaml
---
id: astral.dispatch.run-next-is-chain-authority
title: run_next is dispatch chain authority
tier: scoped
checkable: judgment
status: active
applies_when:
  layers: ["core", "utils"]
  paths: ["src/core/**", "src/utils/config.py"]
  change_types: ["add", "modify"]
source_docs:
  - docs/features/dispatcher/ast-1110-statute-run-next-is-chain-authority.md
  - docs/ASTRAL_CODE_RULES.md
supersedes: null
superseded_by: null
approved_by: Archie
approved_at: "2026-07-31"
---
```

2. Body sections in SCHEMA order (use this text verbatim):

   - `# Statement` — When `agent_task.run_next` already encodes a dispatch multi-hop chain, config must not define a parallel allowed-key set, hop-order list, or membership frozenset that restates that chain’s membership or succession. Chain membership and hop succession for those flows come from current `agent_task.run_next` rows (and helpers that read them). Config may still name graduation maps, trigger registries, task specs, and other true config-owned catalogs that do **not** duplicate `run_next` topology. Putting such a shadow list in `config.py` does **not** satisfy `astral.standards.no-hardcoded-sets`.

   - `## Rationale` — Config frozensets that copy `run_next` look statute-compliant while drifting from the live database topology and inventing carve-outs (e.g. excluding a hop from a membership set). The documented §2.6.0 carve-out already uses `run_next`; shadow lists create a second authority and hide that drift.

   - `## Examples` / `### Conforming` —
     - Hop-label claim/graduation helpers that derive parent/child eligibility from `agent_task.run_next` (e.g. `_agent_task_parents_with_run_next`, `_current_agent_task_run_next`) without consulting a config hop-membership frozenset.
     - Config that owns `DISPATCH_CHAIN_TERMINAL_GRADUATION` / trigger→registry maps without listing every hop task key as chain membership.

   - `### Violating` —
     - `JOB_ARTIFACT_ENTRY_TASK_KEYS` (or any wrapper) used as authority for which consult hops are “in” the job-artifact chain while `run_next` already encodes those hops.
     - `BUILD_CONFIG.resume_artifact_chain.hop_task_keys` / `_RESUME_ARTIFACT_HOP_TASK_KEYS` used as authority for resume/artifact hop succession instead of `run_next`.
     - `CANDIDATE_STAGE_DISPATCH[…]["craft_task_keys"]` used as authority for craft daisy-chain succession instead of `run_next`.

   - Optional `## Notes` — Does not delete the named shadows (AST-1111–AST-1113). Does not change Manage Tasks UI, `dispatch_tasks` uniqueness, or AUTO/CLICK semantics. Complements `astral.state.no-daisy-chain-in-run` (carve-out exists) by requiring the carve-out’s **data** be the membership authority. Archie approved working id on parent AST-1109 Architectural definition (2026-07-31); statute body lands with this child.

3. In `canon/statutes/README.md`, add a harvested-corpus table row for `astral.dispatch.run-next-is-chain-authority` immediately after the existing `astral.dispatch.seed-auto-false` row (same table columns/style), path `` `astral/dispatch/astral.dispatch.run-next-is-chain-authority.md` ``. Bump the active-statute count text from **57** to **58**.

4. In `canon/statutes/HARVEST.md`, add one crosswalk row after the `astral.dispatch.seed-auto-false` create row:

   `| create (AST-1110) | \`astral.dispatch.run-next-is-chain-authority\` | scoped | judgment | AST-1109 / AST-1110 | \`astral/dispatch/astral.dispatch.run-next-is-chain-authority.md\` |`

   Update the **Counts** line so the AST-1110 create is included and the total active mappings read **58** (e.g. keep prior create tallies and add `; 1 created by AST-1110; 58 total active mappings in this register`).

⚠️ **Decision:** Domain folder remains `dispatch` (already created by AST-1098). `approved_by: Archie` / `approved_at: 2026-07-31` per parent Architectural definition naming this working id + AUTHORING lifecycle (same pattern as AST-1098 / `astral.dispatch.seed-auto-false`). Do **not** invent a second statute id; do **not** amend `astral.state.no-daisy-chain-in-run` or `astral.standards.no-hardcoded-sets` bodies in this child — the new statute is the boundary clarification.

## Stage 2: Proposed pattern `pattern.dispatch.run-next-chain-authority`

**Done when:** Pattern file exists at SCHEMA path with `status: proposed`; patterns README + HARVEST list it; no `approved` claim.

1. Create directory `canon/patterns/dispatch/` if missing.
2. Create `canon/patterns/dispatch/pattern.dispatch.run-next-chain-authority.md` with YAML frontmatter (all SCHEMA keys, no extras):

```yaml
---
id: pattern.dispatch.run-next-chain-authority
name: run_next as dispatch chain authority
status: proposed
proposed_in: AST-1109
approved_by: null
approved_at: null
canonical_refs:
  - path: src/core/agent.py
    symbol: _current_agent_task_run_next
  - path: src/utils/config.py
    symbol: _agent_task_parents_with_run_next
  - path: docs/ASTRAL_CODE_RULES.md
    symbol: "§2.6.0"
related_statutes:
  - astral.dispatch.run-next-is-chain-authority
  - astral.state.no-daisy-chain-in-run
  - astral.config.config-source-of-truth
  - astral.standards.no-hardcoded-sets
supersedes: null
superseded_by: null
---
```

3. Body sections in SCHEMA order (use this text verbatim):

   - `# Problem` — Dispatch multi-hop membership and succession get restated as config frozensets / hop-order lists that drift from live `agent_task.run_next` rows and invent carve-outs.

   - `# Solution shape` — Treat current `agent_task.run_next` as the authority for chain membership and hop succession on job/candidate dispatch chains that already use the §2.6.0 carve-out. Read succession via existing helpers (`_current_agent_task_run_next`, `_agent_task_parents_with_run_next`, and claim/graduation helpers that already follow `run_next`). Config may own graduation maps and trigger registries; it must not restate hop sets. Point at `canonical_refs` — do not paste large code into this catalog entry. Sibling anomaly remediations (AST-1111–AST-1113) delete the named shadows end-to-end against `astral.dispatch.run-next-is-chain-authority`.

   - `## When not to use` —
     - True config-owned catalogs that are not `run_next` topology (grades, normalize gates, `TASK_CONFIG` specs, seed AUTO defaults).
     - Replacing the §2.6.0 hop-label claim/graduation path with a new config list.
     - Depending on this pattern id for implementation until `status: approved` (AUTHORING).

   - Optional `## Notes` — Lands as `proposed` from AST-1109 / AST-1110. Archie may approve later; remediations bind to the statute first. Does not own AST-1108 seed cleanup.

4. In `canon/patterns/README.md`:
   - Add a harvested-corpus table row for this id with `status` **proposed** and path `` `dispatch/pattern.dispatch.run-next-chain-authority.md` ``.
   - Update the prose that currently says “All six catalog entries below are `status: approved`” so it remains accurate (e.g. note six approved plus this proposed entry, or count approved vs proposed explicitly — do not claim this entry is approved).

5. In `canon/patterns/HARVEST.md`, add one Crosswalk row:

   `| create (AST-1110) | \`pattern.dispatch.run-next-chain-authority\` | dispatch | \`dispatch/pattern.dispatch.run-next-chain-authority.md\` | AST-1109 | proposed — run_next chain authority; not yet Archie-approved |`

   Optionally add one Supporting / AC cite-map line that dispatch chain membership remediations cite this id **after** Archie approves — or leave AC cite map unchanged until approved (prefer: leave the AC cite map table unchanged; note in Crosswalk only).

⚠️ **Decision:** Land pattern as **`proposed`**, not `approved`. Parent Architectural definition requires Archie approval before implementation depends on the catalog id; AUTHORING forbids depending on proposed ids. Sibling remediations cite the **statute** (Stage 1) as binding; the pattern is the affirmative catalog note. Do **not** flip to approved in this child without an explicit Archie Linear comment naming this pattern id.

## Stage 3: CODE_RULES pointer

**Done when:** `docs/ASTRAL_CODE_RULES.md` cites `astral.dispatch.run-next-is-chain-authority` at §2.6.0 with one clarifying sentence; no other sections rewritten; no product code touched.

1. In `docs/ASTRAL_CODE_RULES.md`, under `#### 2.6.0 Dispatch run_next chains (AST-848)`, immediately after the existing `**Narrative (not a statute):** …` line (or immediately before the prose paragraph that starts “Within a **single** `do_task` invocation”), insert:

   `**Statute:** \`astral.dispatch.run-next-is-chain-authority\``

2. In the same §2.6.0 subsection, after the existing carve-out prose paragraph (the one ending with roster/consult / company batches), add exactly one clarifying sentence:

   `Config must not define parallel hop-membership or hop-order lists that restate chains already encoded in \`agent_task.run_next\` — see statute \`astral.dispatch.run-next-is-chain-authority\`.`

3. Do **not** edit §1.4, §2.1 body catalogs, or other statutes’ files. Do **not** change `src/**`.

⚠️ **Decision:** Single pointer at §2.6.0 (the carve-out home) rather than scattering new **Statute:** lines under §1.4 / §2.1 — those statutes stay as-is; the new statute is the loophole ban. Sibling tickets perform the deletes.

## Execution contract

- Stages in order; one commit per stage on the epic worktree sub branch; publish to `origin/<publish-ref>` after each stage per build-child.
- No files outside the Files Changed table.
- Ambiguity or codebase drift → stop and comment on **parent** AST-1109 with the Stage N blocked template.
- Leave consult/dispatcher/craft routing, frozenset deletes, boot SQL, Manage Tasks UI, and AST-1108 untouched.

## Self-Assessment

**Scope:** `Single-Component` — one new statute + register, one proposed pattern + register, and a CODE_RULES pointer. No `src/**` product changes.

**Conf:** `high` — mirrors AST-1098 statute landing + patterns AUTHORING propose lifecycle; parent already named both ids; violating examples are the three named shadows on tip.

**Risk:** `Medium` — wrong statute wording could mis-bind sibling remediations or over-ban legitimate config catalogs; landing the pattern as `approved` without Archie would violate AUTHORING; forgetting README/HARVEST register leaves Joan/Radia corpus incomplete.

## Self-review vs ASTRAL_CODE_RULES

- **§2.6.0 / no-daisy-chain-in-run:** Statute complements the carve-out (membership must match `run_next` data); does not remove or rewrite hop-label rules.
- **§2.1 / config-source-of-truth / pattern.config.config-block:** Clarifies when config must **not** duplicate DB topology; does not move true config catalogs out of `config.py`.
- **§1.4 / no-hardcoded-sets:** Explicitly states a config shadow of `run_next` is not a conforming “put it in config” escape.
- **§1.1 / in-scope-only:** No anomaly deletes, no boot SQL, no AST-1108.
- **Statute AUTHORING / orch.roles.archie-approves-statutes:** `status: active` + `approved_by: Archie`; pattern stays `proposed`.
- **No conflict requiring conf-!!-NONE.**
