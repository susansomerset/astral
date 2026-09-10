# Rename plural drafts + example enrichment

**Linear:** [AST-1628](https://linear.app/astralcareermatch/issue/AST-1628/rename-plural-drafts-example-enrichment-update-pattartifacts)
**Parent:** [AST-1626](https://linear.app/astralcareermatch/issue/AST-1626/update-pattartifacts-directives-with-code-examples) — update patt.artifacts.* directives with code examples
**Publish ref:** `sub/AST-1626/AST-1628-rename-plural-drafts-example-enrichment`

After sibling AST-1627 (five core singular drafts — this ticket does **not** re-edit those): rename the former plural draft ids (`artifacts` segment) → singular `patt.artifact.*` (paths + frontmatter `id`), add harvested `# Examples`, and sweep **docs** cites of the old plural paths. Docs-only; no product/runtime code; no draft→`active/` promotion.

## Explicit scope gate

Ticket **## Scope** names:

- `canon/directives/draft/patt.artifact.ui-consistency.md` — **renamed from** former plural draft path — body preserved + Examples for `bodyShape` editor + leaf save/reload; frontmatter `id: patt.artifact.ui-consistency`
- `canon/directives/draft/patt.artifact.traceability.md` — **renamed from** former plural draft path — body preserved + Examples for live `source_artifact_ids` seed recording; frontmatter `id: patt.artifact.traceability`; still-unimplemented agent/task lineage labeled illustrative
- In-repo cite sweep — `docs/features/**` (and any other **non-banned** docs that hard-path the plural filenames). **Not** `src/**` comment edits (AC4: empty `git diff origin/dev -- src/`). **Not** engineer edits to `tests/` or `docs/test-bible/**` (Betty owns those at Code Complete / `qa-child`).

Every row in **Files Changed** is one of those engineer-owned paths (plus this plan doc). Every Stage step is rename / Examples / docs cite rewrite of the kind Scope describes.

**Out of this ticket (do not touch):** the five core drafts (`manage-catalog`, `write-operative`, `read-current`, `read-operative`, `no-coat-check`); `src/**`; `tests/**`; draft→`active/` promotion; inventing helpers not on `origin/dev`; expanding agent/task lineage as if already product-wired.

**Sibling gate:** AST-1627 owns the five core drafts only. This ticket does not depend on merging AST-1627 for file content (those paths are disjoint), but epic order is “after #1.” Do not re-open or amend AST-1627’s Examples.

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `canon/directives/draft/patt.artifact.ui-consistency.md` | **Rename from** former plural draft path (ui-consistency) + frontmatter id singular + `# Examples` | canon/draft |
| `canon/directives/draft/patt.artifact.traceability.md` | **Rename from** former plural draft path (traceability) + frontmatter id singular + `# Examples` | canon/draft |
| `docs/features/**` (former plural-path hits only) | Replace hard-path / id cites of the former plural draft ids → singular `patt.artifact.*` | docs |


**Betty-owned (not engineer `code()`):** update plural path / id strings under `docs/test-bible/**` and any `tests/**` path that hard-codes the former plural draft filenames for ui-consistency / traceability under `canon/directives/draft/` (known today: `docs/test-bible/frontend/pages.md`, `docs/test-bible/data/database/artifacts.md`, `docs/test-bible/core/candidate.md`, `tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx`). List those paths in the Code Complete note / plan Review stub so Betty’s manifest can retarget them.

**Explicitly not in engineer diff:** `src/core/tracker.py`, `src/data/database.py`, `src/ui/frontend/src/components/ArtifactEditor.tsx` — they contain plural id mentions in comments/docstrings; leaving them is required by AC4 (no `src/` diff). Do **not** “helpfully” rewrite those comments this ticket.

## Stage 1: Rename + Examples — `ui-consistency`

**Done when:** Former plural ui-consistency draft path is gone; singular `canon/directives/draft/patt.artifact.ui-consistency.md` exists with frontmatter `id: patt.artifact.ui-consistency`; Abstract / Arc / Applications / Exceptions / Implementation headings remain; a new `# Examples` section (after `# Implementation`, before `# OPEN QUESTIONS / DECISIONS`) has ≥1 fenced block showing `bodyShape` into `ArtifactEditor` and leaf save/reload for the pilot; no `src/` / `tests/` changes.

1. From epic worktree on this publish ref, `git mv` the former plural ui-consistency draft file under `canon/directives/draft/` to `patt.artifact.ui-consistency.md` (only the `artifacts` → `artifact` filename segment).

2. In the singular file frontmatter, set exactly:

```yaml
id: patt.artifact.ui-consistency
```

Leave `kind`, `scope`, and `point` otherwise unchanged (still points at `ArtifactEditor.tsx` / pages).

3. Grep the renamed file for the former plural id string (the `artifacts` segment form) — there should be none left in body/frontmatter after the id change. Do **not** rewrite Abstract/Arc/Applications/Exceptions/Implementation normative bullets except where a bullet literally embeds that old plural **id string** (replace that id string only).

4. Insert `# Examples` between `# Implementation` and `# OPEN QUESTIONS / DECISIONS`.

5. Prose lead (1–2 sentences): page passes catalog `body_shape` as the `bodyShape` prop; pilot hardcodes the literal matching `ARTIFACT_CONFIG["candidate.artifacts.base_resume"]["body_shape"]` — no new frontend catalog fetch.

6. Fenced block — **page → editor** (harvest from `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx` + `ArtifactEditor.tsx`):

```tsx
// ArtifactsBaseResumeContent — pilot body_shape resume_content, leaf base_resume
<ArtifactEditor
  bodyShape="resume_content"
  artifactKey="base_resume"
  /* existing craft taskKey / load+save props unchanged */
/>
```

7. Fenced or prose **save/reload** — Save still PUTs `{ artifacts: { base_resume: dictPayload } }` via the existing candidate data API; GET / hydrate reloads the current leaf (operative hydrate already on the candidate path). Do **not** invent a client-side `artifact_id` field or a parallel storage key.

8. Adjacent **do not:** do not fork a second base-resume-only editor component when `bodyShape` is `resume_content`; do not add a frontend `ARTIFACT_CONFIG` fetch this ticket.

9. Do **not** edit `ArtifactEditor.tsx` or any page under `src/ui/frontend/`.

## Stage 2: Rename + Examples — `traceability`

**Done when:** Former plural traceability draft path is gone; singular `patt.artifact.traceability.md` exists with `id: patt.artifact.traceability`; law headings intact; `# Examples` shows live `source_artifact_ids` on generative/job write when the column/kwarg exists; agent/task lineage called out as still draft-only / illustrative; no `src/` / `tests/` changes.

1. `git mv` the former plural traceability draft file under `canon/directives/draft/` to `patt.artifact.traceability.md` (only the `artifacts` → `artifact` filename segment).

2. Frontmatter:

```yaml
id: patt.artifact.traceability
```

3. Replace any remaining body string that still uses the former plural id (`artifacts` segment) with `patt.artifact.traceability`. Keep Abstract/Arc/Applications/Exceptions/Implementation content otherwise; do **not** promote the draft or claim full agent/task wire is live.

4. Insert `# Examples` between `# Implementation` and `# OPEN QUESTIONS / DECISIONS`.

5. Prose: **Live today** — `database.save_artifact(..., source_artifact_ids=...)` persists a JSON array of seed `artifact_uuid` strings on the new row (AST-1588 / job_resume→base_resume citation via `tracker.save_job_artifact`). **Still draft / illustrative** — versioned `agent_id` + versioned `agent_task_id` lineage and full token-catalog harvest are **not** product-wired; examples must not invent those columns as live APIs.

6. Fenced block — **seed ids on write** (harvest from `tracker.save_job_artifact` / `database.save_artifact`):

```python
# Live: optional seed pins on the new artifact row (list[str] artifact_uuid)
new_uuid = database.save_artifact(
    entity_type,
    entity_id,
    artifact_type,
    body,
    source_artifact_ids=seed_uuids,  # e.g. [current base_resume uuid]; default []
)
# Job wrapper: tracker.save_job_artifact(...) auto-cites current base_resume for
# job.artifacts.job_resume; other keys pass source_artifact_ids through.
```

7. Adjacent **do not / illustrative:** do not treat versioned agent / agent_task columns as shipped in this draft’s examples; label any such snippet `ILLUSTRATIVE — not on origin/dev` if included at all (prefer omitting agent/task fences entirely and stating the gap in one prose sentence).

8. Do **not** edit `src/data/database.py` or `src/core/tracker.py`.

## Stage 3: Docs cite sweep (`docs/features/**`) + verify

**Done when:** Every hard-path / id cite of the former plural draft ids under `docs/features/` on this tip is updated to the singular form; plural draft files are absent; singular files exist with matching frontmatter ids and `# Examples` fences; `git diff origin/dev -- src/ tests/` is empty; five core AST-1627 drafts are unmodified on this branch vs what sync brought in (no accidental edits).

1. Run a cite inventory on the worktree (do not invent extra scopes): search `docs/features/` for the former plural id strings (the `patt.artifacts.` + `ui-consistency` / `traceability` forms).

2. For **each** hit under `docs/features/`, replace former plural id/path → singular `patt.artifact.ui-consistency` / `patt.artifact.traceability` (and the matching `canon/directives/draft/…` paths). Historical plan prose that describes “created plural id at AST-1577” may keep a **one-line historical note** if needed for honesty, but prefer updating the live path/id so agents following feature docs land on the singular file. Do not rewrite unrelated stages of old plans beyond the cite string/path.

3. Re-run the inventory — **zero** remaining former-plural id/path hits for those two drafts under `docs/features/`.

4. **Do not** edit `docs/test-bible/**` or `tests/**` — leave plural strings there for Betty. **Do not** edit `src/**` comment cites.

5. **Verify (builder checklist — docs-acceptance; no invented product `test()`):**

```bash
# AC1 — plural draft filenames gone; singular present + frontmatter ids
python3 - <<'PY'
from pathlib import Path
d = Path('canon/directives/draft')
# former plural filenames use the 'artifacts' segment
for leaf in ('ui-consistency', 'traceability'):
    assert not (d / f'patt.artifacts.{leaf}.md').exists(), leaf
    s = d / f'patt.artifact.{leaf}.md'
    assert s.is_file(), leaf
    assert f'id: patt.artifact.{leaf}' in s.read_text().splitlines()[1] or \
           f'id: patt.artifact.{leaf}' in s.read_text()
print('AC1 ok')
PY
rg -n '^id: patt\.artifact\.(ui-consistency|traceability)$' \
  canon/directives/draft/patt.artifact.ui-consistency.md \
  canon/directives/draft/patt.artifact.traceability.md

# AC2 — fences under Examples
rg -n '```|^# Examples' \
  canon/directives/draft/patt.artifact.ui-consistency.md \
  canon/directives/draft/patt.artifact.traceability.md

# AC3 — docs/features cite sweep clean for former plural ids
rg -n 'patt\.artifacts\.(ui-consistency|traceability)' docs/features/ || true
# expect exit 1 / no matches

# AC4 — no product/runtime diff
git diff origin/dev -- src/ tests/

# Sibling — five core drafts not edited this ticket
git diff origin/dev -- \
  canon/directives/draft/patt.artifact.manage-catalog.md \
  canon/directives/draft/patt.artifact.write-operative.md \
  canon/directives/draft/patt.artifact.read-current.md \
  canon/directives/draft/patt.artifact.read-operative.md \
  canon/directives/draft/patt.artifact.no-coat-check.md
# expect empty on this publish tip unless origin/dev already has AST-1627
# (if ftr later rolls AST-1627, still do not modify those files in AST-1628 commits)
```

6. In the plan’s eventual **Review (build)** stub, list Betty’s known retarget paths (test-bible + the one frontend test that `resolve`s the plural draft path) so `qa-child` can update them.

⚠️ **Decision:** Engineer cite sweep is **`docs/features/**` only**. `docs/test-bible/**` and `tests/**` stay Betty’s (test-tree ban). `src/**` plural mentions in comments stay untouched to satisfy AC4 empty product diff — parent’s “docs cites only” clause.

⚠️ **Decision:** Place Examples in a new `# Examples` section after `# Implementation`, same convention as AST-1627, so law sections stay authoritative.

## Estimate

Confirm Chuckles estimate: 2 — agree

## Joan validate

[plan-rubric]
**Ticket:** AST-1628
**Overall:** APPROVED
**Corpus:** 7a40a9e0de4324d0d1c4d56abc52b13d3c297715 (canon tree on `origin/dev`; `canon_clerk.py` absent — clerk sha unavailable)
**Publish ref:** `sub/AST-1626/AST-1628-rename-plural-drafts-example-enrichment` @ `a2431a0e660a271df1f4e7cc38b90c654ed3311c`

## Canon scores

patt.artifact.ui-consistency | A | |
patt.artifact.traceability | A | |
astral.standards.in-scope-only | A | |
astral.standards.names-not-ticket-ids | A | |

## Traceability

AC1→Stages 1–2 + S3 `test`/`rg` frontmatter checks; AC2→Stages 1–2 `# Examples` fences + S3 `rg` fence check; AC3→Stage 3 `docs/features/**` sweep (engineer) + Betty handoff list for `docs/test-bible/**` / `tests/**` (see discuss); AC4→Explicit scope gate + S3 `git diff origin/dev -- src/ tests/`; parent AC1/AC6 (examples + singular rename)→Stages 1–2; parent AC3 (no product diff)→AC4 + explicit `src/**` comment freeze; parent AC5 (write/read do-not)→N/A for these two drafts — plan supplies ui-consistency do-not + traceability live-vs-illustrative boundary anyway.

## Findings

### discuss

- **Location:** Ticket AC3 vs Stage 3 / Files Changed
- **Finding:** Child AC3 text requires cite updates in `docs/features` **and** `test-bible` **and** draft comments. Plan limits engineer work to `docs/features/**` and defers `docs/test-bible/**` + `tests/**` to Betty at Code Complete (with paths named). Parent definition’s cite sweep also names test-bible but qualifies code-comment work as docs-cites-only (no `src/` edits) — plan matches parent intent, not the child AC’s undifferentiated wording.
- **Recommendation:** Accept for Plan Approved under standard test-tree ownership; ensure `qa-child` manifest retargets the listed test-bible + component test paths before User Testing closes AC3.

- **Location:** Linear assignee at fetch
- **Finding:** Status `Plan Ready` but assignee is Ada (not Joan). Procedural handoff for Chuckles only — does not affect plan fidelity.
- **Recommendation:** Chuckles restores implementer after posting upshot per §8.

### acceptable

- **Location:** Stage 3 step 2 — historical plural-id prose in older feature plans (e.g. AST-1577)
- **Finding:** Sweep may leave one-line historical notes where honesty requires, while retargeting live cites to singular paths.
- **Recommendation:** Prefer singular path/id on all agent-followable cites; keep historical plural mentions only where they document past decision text.

context_tokens≈42000

## Review (build)

**Built @ `f9cabdcd6bb418fa1c47208e7f0f33e3ade28bd1`** — `origin/sub/AST-1626/AST-1628-rename-plural-drafts-example-enrichment`

Stages 1–3 landed: singular `patt.artifact.ui-consistency` / `patt.artifact.traceability` drafts with `# Examples`; `docs/features/**` plural-id cite sweep. No `src/` product diff (Betty may retarget `tests/**` cites).

**Betty retarget (qa-child):** `docs/test-bible/frontend/pages.md`, `docs/test-bible/data/database/artifacts.md`, `docs/test-bible/core/candidate.md`, `tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx` — former plural draft path/id strings.

## Radia review

[code-rubric]
**Ticket:** AST-1628
**Publish ref:** `c949645742d55fe9ac3e7e6502e47e2267ba639a` (`origin/sub/AST-1626/AST-1628-rename-plural-drafts-example-enrichment`)
**Corpus:** `7a40a9e0de4324d0d1c4d56abc52b13d3c297715` (canon tree on `origin/dev`; `canon_clerk.py` absent — clerk sha / `corpus_dirty` unavailable)
**Overall:** CLEAN

## Canon scores

patt.artifact.ui-consistency | A | |
patt.artifact.traceability | A | |
astral.standards.in-scope-only | A | |
astral.standards.names-not-ticket-ids | A | |

## Column diff vs plan stage

(aligned)

## Frame diff

(none)

## Findings

### discuss

- **Location:** `docs/features/foundation/ast-1577-ui-consistency-base-resume-editor.md` — Stage 1 Decision callout
- **Finding:** Mechanical cite sweep left a self-contradictory line: `Pattern id is patt.artifact.ui-consistency (plural artifacts) … — not patt.artifact.ui-consistency` (same id twice; “plural” note stale).
- **Recommendation:** `resolve-child` or a follow-up docs pass should rewrite that Decision block to honest historical prose (e.g. “was plural at AST-1577; renamed singular at AST-1628”) or delete the callout.

- **Location:** Linear AC4 vs plan / Betty manifest
- **Finding:** Ticket AC4 text says no `src/` / `tests/` diff; publish tip has **no `src/` diff** but Betty landed a **4-line cite retarget** in `tests/component/frontend/pages/test_ArtifactsBaseResumeContent.test.tsx` (`test(AST-1628)` + `merge-tests`). Plan and Betty manifest explicitly authorized this; behavior unchanged.
- **Recommendation:** Accept for User Testing under standard test-tree ownership; optionally clarify Linear AC4 wording on the parent/child to match plan (“no `src/`; Betty may retarget test-tree cites”).

### advisory

- **Location:** Issue doc `## Review (build)` stub @ `f9cabdcd`
- **Finding:** States “No `src/` / `tests/` diff” — inaccurate after Betty `merge-tests`; `src/` is still empty.
- **Recommendation:** Chuckles corrects stub when appending this review.

- **Location:** `docs/test-bible/README.md` AST-1628 block
- **Finding:** `**Bible shasum (after publish):**` is still a command placeholder (`ac998e34…` computable on tip).
- **Recommendation:** Doc hygiene only; manifest content otherwise matches Betty’s retarget pass.

- **Location:** `src/ui/frontend/src/components/ArtifactEditor.tsx`, `src/core/tracker.py`
- **Finding:** Plural `patt.artifacts.*` id strings remain in comments — intentional per plan AC4 / explicit `src/**` comment freeze.
- **Recommendation:** No action this ticket; optional future comment sweep is out of scope.

## Notes

- **Cite sweep:** `docs/features/**` clean for `patt.artifacts.ui-consistency` / `patt.artifacts.traceability`; `docs/test-bible/**` + Vitest retargeted; remaining plural strings are the AST-1627 sibling-gate historical line in bible README, manifest `test ! -f` guards, and frozen `src/` comments.
- **Sibling gate:** Five core AST-1627 drafts show zero diff vs `origin/dev` on this tip — AST-1628 did not re-edit them.
- **Epic ancestry:** Branch carries AST-1627 bible manifest block via shared `merge-tests` history; canon product for AST-1627 is not in this three-dot diff.

## What's solid

- AC1: plural draft paths gone; singular `patt.artifact.ui-consistency` / `patt.artifact.traceability` exist with matching frontmatter ids.
- AC2: both drafts have `# Examples` with live harvested shapes (`bodyShape` / `ArtifactEditor`; `database.save_artifact(..., source_artifact_ids=...)` with live-vs-illustrative boundary).
- AC3: `docs/features/**` cite sweep complete; Betty retargeted `docs/test-bible/{frontend/pages,data/database/artifacts,core/candidate}.md` + AST-1577 Vitest draft assert.
- Law headings intact on both renamed drafts.
- Estimate **2** fits docs-only rename + examples + cite sweep footprint.

## Plan adherence (§5.4)

- **Plan fidelity:** Stages 1–3 delivered; Examples-after-Implementation convention matches AST-1627.
- **Estimate footprint:** Estimate 2 appropriate.
- **Cross-ticket scope:** AST-1627 five-core drafts untouched; no `src/` product diff.
- **Database / SQL:** N/A.

context_tokens≈42000
