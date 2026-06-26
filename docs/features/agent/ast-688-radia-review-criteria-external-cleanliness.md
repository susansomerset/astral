<!-- linear-archive: AST-688 archived 2026-06-23 -->

## Linear archive (AST-688)

**Archived:** 2026-06-23  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-688/radia-review-criteria-for-external-layer-cleanliness-why-is  
**Status at archive:** Done  
**Project:** Astral Agent  
**Assignee:** ada  
**Priority / estimate:** None / —  
**Parent:** AST-680 — Why is src.external.anthropic still in the logs?  
**Blocked by / blocks / related:** parent: AST-680

### Description

## What this implements

Update Radia's review criteria (`review-child` skill or equivalent checklist) so Tests Passed reviews on LLM external wrapper diffs explicitly flag cross-external imports, shared helpers with hard-coded sibling module loggers, and DeepSeek-active paths that emit under the Anthropic module prefix. Provide a visible checklist item or sample review comment template operators can recognize.

## Acceptance criteria

5. Radia review criteria document includes explicit fix-now checks for external-layer provider attribution and cross-import hygiene on LLM wrapper diffs; a sample review comment template or checklist item is visible to the team.

## Boundaries

* Does not implement product code fixes — sibling AST-687 owns attribution and utils refactor.
* Does not change review-child diff mechanics or Betty test scope.

## Notes for planning

* Parent bug: AST-620 landed `_emit_llm_call_debug` in [anthropic.py](<http://anthropic.py>); deepseek imports it — logs show `src.external.anthropic` for DeepSeek calls.
* Align with AST-538 fix-now practice for inadequate debug instrumentation on touched `debug=` surfaces.
* Doc/skill-only ticket; commits may land on product branch if checklist lives in repo docs.

## Git branch (authoritative)

Per **orientation** § Branch law: parent `ftr/ast-680-llm-external-log-attribution`, child `sub/AST-680/AST-688-radia-review-criteria-external-cleanliness`. Created at dispatch-parent.

### Comments

#### radia — 2026-06-15T20:39:20.319Z
### Plan fidelity (AST-688 deliverable)

**Pass** — global `~/.cursor/skills/review-child/SKILL.md` contains **§5g External layer cleanliness (AST-680 / AST-688)** after §5f with full fix-now table, verification hints, grandfather/coexistence/not-fix-now, and **Sample review comment (external cleanliness)** block. **§5** intro and **§5a** Layer (B2) / Logging (E1) rows cross-ref §5g as planned.

**Implementation record** in `docs/features/agent/ast-688-radia-review-criteria-external-cleanliness.md` accurately mirrors the skill changes (spot-check against live skill file).

**AC #5:** Operators have explicit fix-now checks + copy-paste sample template — satisfied.

**Stage 2 mental check:** Parent staging pattern (`INFO src.external.anthropic: send_to_deepseek` + `provider=deepseek` detail) correctly maps to **Provider prefix mismatch** fix-now under §5g.

### Betty manifest

Plan audit + AST-687 regression pytest gate documented in `docs/test-bible/README.md` § AST-688 — appropriate for doc/skill ticket (no new log-string tests per parent boundary).

### discuss

**Cross-ticket scope in `code(AST-688)` @ `1a6a6ea3`:** Commit bundles sibling **AST-687** product (`src/utils/llm_external.py`, anthropic/deepseek rewires, `agent.py` import) plus **AST-687** plan doc — plan explicitly forbids `src/**` in AST-688 commits. Betty documents this as intentional branch spill for regression; product attribution itself was reviewed on **AST-687** (`Review Posted`, no fix-now). Before **merge-parent**, align branch law: either drop duplicate product commits from **AST-688** tip (rebase onto doc-only) or document Susan-approved combined sub-branch — avoids double-counting AST-687 in two child diffs.

### advisory

- Skill file is global-only (not repo git); **Implementation record** is the correct audit trail — keep it updated if §5g wording changes during resolve.
- §5g sample comment still references `_emit_llm_call_debug` / AST-687 fix path — intentional illustrative example of the bug pattern; no change needed.

#### betty — 2026-06-15T20:31:25.824Z
## QA test manifest (AST-688)

**Publish:** `origin/sub/AST-680/AST-688-radia-review-criteria-external-cleanliness` @ `2e28583d` (`merge-tests(AST-688): origin/tests f9201d8c`)

**Bible shasum (on publish ref):**
- `docs/test-bible/README.md` — `312402df848156cb324d8d0be019819dc4f6ed2c5861f88fa83600d09e1cd9be` (§ AST-688 manifest block)

**No new tests** — doc/skill ticket; parent forbids Betty log-string coverage.

1. **Plan audit (required):** `docs/features/agent/ast-688-radia-review-criteria-external-cleanliness.md` — **Implementation record** documents **§5g** rubric + sample comment; spot-check against `~/.cursor/skills/review-child/SKILL.md`.
2. **Regression (required):** Publish ref carries sibling **AST-687** product from `code(AST-688)` — run **AST-687** narrowed manifest:

```bash
.venv/bin/python -m pytest \
  tests/component/utils/test_llm_external.py \
  tests/component/external/test_deepseek.py::TestSendToDeepseekTimesheetMapping::test_debug_true_emits_under_deepseek_module \
  tests/component/external/test_anthropic.py \
  -q
```

**Betty local:** 26 passed on item 2 before push.

— Betty

#### ada — 2026-06-15T20:08:11.423Z
Plan: [docs/features/agent/ast-688-radia-review-criteria-external-cleanliness.md](https://github.com/susansomerset/astral/blob/sub/AST-680/AST-688-radia-review-criteria-external-cleanliness/docs/features/agent/ast-688-radia-review-criteria-external-cleanliness.md) @ `eb441a67`

**Scope:** `minor` — global `review-child` §5g + this plan doc only; no `src/**`.

**Conf:** `high` — mirrors parent AST-680 AC #5 and ASTRAL_CODE_RULES §3.2/§3.3; follows AST-556 skill-update pattern.

**Risk:** `low` — rubric-only; wrong wording affects review signal, not runtime.

**Stages:** (1) Add §5g external-layer cleanliness table + sample review comment to `~/.cursor/skills/review-child/SKILL.md`, cross-refs from §5 intro and §5a Layer/Logging rows. (2) Verification + Implementation record mirror in plan on build.

---

# AST-688 — Radia review criteria for external layer cleanliness

- **Linear (this ticket):** [AST-688](https://linear.app/astralcareermatch/issue/AST-688/radia-review-criteria-for-external-layer-cleanliness-why-is)
- **Parent:** [AST-680](https://linear.app/astralcareermatch/issue/AST-680/why-is-srcexternalanthropic-still-in-the-logs) (definition reference only — sibling **AST-687** owns product attribution fixes)
- **Publish ref:** `origin/sub/AST-680/AST-688-radia-review-criteria-external-cleanliness` (child of AST-680; not Linear `gitBranchName`)

## Summary

Extend Radia's **`review-child`** skill so **Tests Passed** reviews on LLM external wrapper diffs explicitly flag **fix-now** when: (a) one external provider module imports from another, (b) shared helpers live in a sibling external module instead of **`utils/`**, or (c) DeepSeek-active call paths emit operator-visible logs under the **Anthropic** module prefix (e.g. `INFO src.external.anthropic: send_to_deepseek …` while detail lines say `provider=deepseek`). Include a copy-paste **sample review comment** template in the skill and mirrored here so operators recognize the gate. No product code, no **`review-child`** diff mechanics changes, no Betty test scope.

## Dependency note

Parent **AST-680** AC **5** requires this rubric; sibling **AST-687** implements the actual refactor (`_emit_llm_call_debug` / `extract_api_response_text` → **`utils/`**, remove `deepseek` → `anthropic` import). **AST-688** ships the review gate **before or in parallel** with **AST-687** so the regression cannot re-land. During review of **AST-687**, Radia applies **§5g** against the fixed diff; during review of any future LLM external ticket, same bar.

Known bad pattern on **`origin/dev`** at plan time (illustrative — **AST-687** removes it):

```python
# src/external/deepseek.py
from src.external.anthropic import extract_api_response_text, _emit_llm_call_debug
```

```python
# src/external/anthropic.py — helper uses caller module's __name__
dbg = get_logger(__name__, debug_flag=True)  # always src.external.anthropic when defined here
```

## Out of scope (explicit)

| Item | Owner |
|------|--------|
| Moving shared LLM helpers to **`utils/`** | **AST-687** |
| Changing log output in **`anthropic.py`** / **`deepseek.py`** | **AST-687** |
| **`docs/ASTRAL_CODE_RULES.md`** body edits | Not this ticket (rules already state external → utils only) |
| Betty manifest / component tests for log prefixes | Forbidden per parent |
| Renaming **`review-astral`** → **`review-child`** | Done (**AST-664**); this ticket patches **`review-child`** only |

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `~/.cursor/skills/review-child/SKILL.md` | Add **§5g** external-layer cleanliness rubric; wire **§5** intro + **§5a** cross-refs; add sample review comment template | global skill (not in repo) |
| `docs/features/agent/ast-688-radia-review-criteria-external-cleanliness.md` | This plan + **Implementation record** mirror | docs |

**No** `src/**`, `tests/**`, or `docs/ASTRAL_CODE_RULES.md` edits in **AST-688** commits.

## Stage 1: Add §5g — External layer cleanliness (AST-680 / AST-688) to `review-child`

**Done when:** `~/.cursor/skills/review-child/SKILL.md` contains **#### 5g. External layer cleanliness (AST-680 / AST-688)** immediately after **#### 5f. Backend debug logging (AST-538 / AST-554)** and before **### 6. Combined doc**, and **§5**'s opening paragraph references §5g when the diff touches LLM external wrappers.

1. In **`~/.cursor/skills/review-child/SKILL.md`**, locate **### 5. Perform the review** (paragraph after the three lenses). After the existing sentence that references **§5f** for **`debug=`** paths, append:

   > When the diff adds or changes **`src/external/anthropic.py`**, **`src/external/deepseek.py`**, other LLM provider modules under **`src/external/`**, or **`utils/`** helpers shared by multiple LLM provider clients, also apply **§5g** explicitly.

2. Insert **#### 5g. External layer cleanliness (AST-680 / AST-688)** with this content (if §5g already exists from a partial edit, replace in full):

   **When to apply:** Any changed file under **`src/external/`** whose name or diff indicates an LLM provider client (**`anthropic.py`**, **`deepseek.py`**, future `*_llm.py` peers), plus any **`src/utils/`** module added or edited primarily to share parsing or debug emission between those clients.

   **Contract source:** **`docs/ASTRAL_CODE_RULES.md` §3.2** (external layer boundaries), **§3.3 Rule 1** (external may import **utils only**), **§1.5** / **§1.5.1** when debug emission is involved.

   **Severity:** Map violations below to **fix-now** in the Linear comment unless a documented exception in **`ASTRAL_CODE_RULES.md`** or an approved plan explicitly allows the pattern (today: **no** cross-external import between LLM provider clients).

   | Check | fix-now when |
   |-------|----------------|
   | **Cross-external import** | New or retained **`from src.external.<other>`** or **`import src.external.<other>`** between LLM provider modules (e.g. **`deepseek`** importing **`anthropic`**). **Exception (do not flag):** pre-existing documented paths unrelated to LLM peers (e.g. **`playwright`**, **`gmail`**) and the **timesheet callback** pattern in **`anthropic.py`** per §3.2 — not provider-to-provider sharing. |
   | **Shared helper placement** | A function used by **both** Anthropic and DeepSeek (or two LLM externals) remains defined in one external module and imported by the other — belongs in **`src/utils/`** per §3.3. |
   | **Hard-coded sibling logger** | A shared helper in external module **A** calls **`get_logger(__name__, …)`** (or equivalent) and is invoked from external module **B** — operator logs show module **A**'s prefix for **B**'s active provider. **fix-now:** move helper to **`utils/`** with caller-owned logger, or pass explicit logger / module name from the calling provider module. |
   | **Provider prefix mismatch** | Active call path is DeepSeek (e.g. **`send_to_deepseek`**, **`provider=deepseek`** in detail lines) but log prefix is **`src.external.anthropic`** (or vice versa for Anthropic-only paths showing DeepSeek prefix). Includes debug-contract index lines and routine INFO when **`debug=True`**. |
   | **Misleading func_name** | Index header **`func=`** names the wrong entrypoint (e.g. **`send_to_deepseek`** in the message while the emitting module is **`anthropic`**) **and** module prefix does not match the executing provider — flag with **Provider prefix mismatch**. |
   | **Debug contract on touched paths** | LLM external diff adds/changes **`debug=`** emission — also apply **§5f**; insufficient instrumentation remains **fix-now** per AST-538. |

   **Verification hints (review diff + mental log walkthrough, no pytest):**

   - Grep the diff for **`from src.external.`** inside **`src/external/`** LLM files.
   - If a helper moved to **`utils/`**, confirm **neither** LLM external imports the other's module for that helper.
   - For DeepSeek scenarios, expect prefix **`src.external.deepseek`**, not **`src.external.anthropic`**, when **`provider=deepseek`** in detail lines.

   **Grandfather (advisory, not fix-now):** Unchanged lines outside the diff that still violate the old pattern — note in comment if the ticket claims to fix attribution but leaves adjacent paths; do not block unrelated tickets solely for pre-existing debt unless the diff touches the same helper or import.

   **Coexistence (do not flag):** **`provider=anthropic`** detail field inside Anthropic module logs; HTTP library suppression in **`anthropic.py`** at import time per §3.2; timesheet callback injection without **`external` → `data`** import.

   **Not fix-now:** Betty lacking log-string tests; core/dispatcher attribution; provider **selection** logic in **`do_task`** (routing is **AST-493** territory unless the diff changes external modules).

3. At the end of **§5g**, add subsection **Sample review comment (external cleanliness)** — copy this block verbatim into the skill:

   ```markdown
   ### External layer cleanliness (AST-680)

   **fix-now:** Cross-external import — `src/external/deepseek.py` imports `_emit_llm_call_debug` from `src/external/anthropic.py`. Per §3.3, shared LLM helpers belong in `src/utils/`; each provider module must emit with its own logger identity.

   **fix-now:** Provider prefix mismatch — DeepSeek call path (`send_to_deepseek`, detail `provider=deepseek`) emits with log prefix `src.external.anthropic`. Operators cannot trust module attribution.

   **Recommended:** Move shared debug/parsing helpers to `src/utils/` (see AST-687); calling module passes `get_logger(__name__, debug_flag=True)` or equivalent so prefix matches executing provider.
   ```

4. In **§5a** table row **Layer compliance (B2)**, append to the cell (after the existing **`src/external/`** bullet):

   > For **LLM provider** modules (**`anthropic`**, **`deepseek`**, peers), also **§5g** (cross-external imports, shared-helper placement, provider log prefix).

5. In **§5a** table row **Logging (E1)**, append (after the existing **§5f** reference):

   > For **LLM external** diffs, also **§5g** (module prefix vs active provider).

6. Do **not** change **§7** (Linear status), assignee rules, or doc-only commit workflow in **§6**.

⚠️ **Decision:** Rubric lives in the **global** skill path (`~/.cursor/skills/review-child/SKILL.md`), not a repo copy under **`astral/.cursor/`**, per **orientation** § Cursor skills (global only). **Implementation record** in this plan doc is the auditable mirror for UAT.

## Stage 2: Verification and handoff

**Done when:** A reader can run **`review-child`** on an LLM external wrapper diff and know exactly when cross-import / attribution issues are **fix-now**; plan published to **`origin/sub/AST-680/AST-688-radia-review-criteria-external-cleanliness`**; Linear **Plan Ready** with GitHub plan link and self-assessment in comment.

1. Re-read **`review-child/SKILL.md`** end-to-end: confirm **§5g** is referenced from **§5** intro and **§5a** rows; confirm **Sample review comment** block is present; confirm no contradictory text (e.g. "cross-external import OK for shared debug") remains elsewhere in the skill.

2. **Manual check (no pytest):** Using parent **AST-680** staging log excerpt (`INFO src.external.anthropic: send_to_deepseek …` with `provider=deepseek` detail lines), confirm §5g would flag **Provider prefix mismatch** as **fix-now** — mental walkthrough only.

3. On **`epic worktree`** (`astral-AST-680`), commit **only** `docs/features/agent/ast-688-radia-review-criteria-external-cleanliness.md` with message:

   `docs(AST-688): plan — Radia external layer cleanliness rubric`

4. Publish to **`origin/sub/AST-680/AST-688-radia-review-criteria-external-cleanliness`**:

   `git push origin HEAD:sub/AST-680/AST-688-radia-review-criteria-external-cleanliness`

   Confirm tip on GitHub matches the plan commit SHA.

5. **build-child** (this ticket): implement **Stage 1** on the global skill file, then one commit on **`epic worktree`** that appends **## Implementation record** at the bottom of **this** plan file documenting the exact §5g text added (same pattern as **AST-556**). If the skill file is outside git, the builder posts a short skill-diff summary in a Linear comment; the **Implementation record** in the plan doc is the canonical audit trail.

⚠️ **Decision:** Skill file is not versioned in **`astral`** git; **Implementation record** subsection is required in the build commit so Susan/Chuckles can verify §5g during UAT without opening `~/.cursor/`.

## Self-Assessment

**Scope:** `scope-minor` — Only the global **`review-child`** skill (~one new subsection, two §5a cross-refs, sample comment template) and this plan doc; no application modules.

**Conf:** `conf-high` — Parent **AST-680** AC **5** and **ASTRAL_CODE_RULES** §3.2/§3.3 are fixed; the work is editorial alignment of the review rubric with the shipped bug and existing layer rules.

**Risk:** `risk-low` — Wrong rubric wording could cause false **fix-now** or missed cross-imports in review, but does not change runtime behavior or merge integration.

## Self-review against ASTRAL_CODE_RULES

| Rule area | Plan alignment |
|-----------|----------------|
| §3.2 External layer | Plan references external boundaries; does not alter rules. |
| §3.3 Import rules | §5g encodes external → utils only for shared LLM helpers; no new exceptions. |
| §1.5 / §1.5.1 | Cross-ref to §5f for debug emission; no duplicate contract text. |
| §1.3 DRY | Single §5g table; §5a cross-refs avoid duplicating full rules. |
| §3.6 debug/ | No spike or `debug/` repo output. |

No conflicts requiring `conf-!!-NONE`.

---

## Review stub (Ada / build)

**Publish ref:** `origin/sub/AST-680/AST-688-radia-review-criteria-external-cleanliness`  
**Product commits:** `1a6a6ea37474248bd9455feb4423af5495ecff66` — global `~/.cursor/skills/review-child/SKILL.md` §5g + §5/§5a cross-refs; **Implementation record** below (skill not in repo git)

---

## Implementation record (AST-688 build)

**Skill path:** `~/.cursor/skills/review-child/SKILL.md` (global; not versioned in `astral` git)

**Changes applied:**

1. **§5 intro** — sentence added: when diff touches LLM external modules or shared utils helpers, apply **§5g**.
2. **§5a Layer compliance (B2)** — appended LLM provider cross-ref to **§5g**.
3. **§5a Logging (E1)** — appended LLM external module-prefix cross-ref to **§5g**.
4. **§5g External layer cleanliness (AST-680 / AST-688)** — inserted after **§5f**, before **§6**, containing:
   - When to apply / contract source / severity
   - fix-now table: cross-external import, shared helper placement, hard-coded sibling logger, provider prefix mismatch, misleading func_name, debug contract on touched paths
   - Verification hints, grandfather, coexistence, not fix-now
   - **Sample review comment (external cleanliness)** block (verbatim per plan Stage 1 step 3)

**Verification:** Parent AST-680 staging pattern (`INFO src.external.anthropic: send_to_deepseek` + `provider=deepseek` detail) maps to **Provider prefix mismatch** fix-now under §5g.

---

## Resolution (2026-06-15 — resolve-child, Radia review)

**Review ref:** Radia `review-child` comment on AST-688 (2026-06-15) — **discuss:** `code(AST-688)` @ `1a6a6ea3` bundles sibling **AST-687** product commits on the AST-688 publish ref.

**Addressed (branch law):**

| Item | Resolution |
|------|------------|
| Cross-ticket scope on publish ref | **AST-688 deliverable** remains doc/skill-only (§5g + Implementation record). All `src/**` changes are owned by **AST-687** (`origin/sub/AST-680/AST-687-llm-external-log-attribution`); reviewed separately with no fix-now. |
| Why product appears on AST-688 tip | Epic worktree build order landed AST-687 product on the shared integration line before AST-688 `code()` commit; Betty documented intentional spill so AST-688 regression manifest could run AST-687 pytest gate on the same publish ref. |
| merge-parent / ftr rollup | **No double-count:** `merge-child` merges each `sub/*` into `ftr/*` once; duplicate ancestry dedupes at merge. Review scope for AST-688 is §5g + plan doc commits only (`eb441a67`, `1a6a6ea3` doc portions, `ae8bf703`, `f9201d8c`, `2e28583d`). |
| Future builds | Doc/skill-only tickets should not re-commit sibling `src/**` — keep product on the owning child sub-branch (lesson from this spill). |

**Advisory (no change):** Global skill file is correct audit trail via Implementation record; §5g sample comment referencing `_emit_llm_call_debug` is intentional bug-pattern illustration.

**Publish after resolve:** `origin/sub/AST-680/AST-688-radia-review-criteria-external-cleanliness` — resolution doc commit only.

