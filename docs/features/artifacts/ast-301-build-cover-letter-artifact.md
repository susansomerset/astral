# Build Cover Letter Artifact

**Linear:** https://linear.app/astralcareermatch/issue/AST-301/build-cover-letter-artifact  
**Feature branch:** `<agent>/ast-301-build-cover-letter-artifact`

Daisy-chain **`do_task()`** pipeline producing **`job_data.artifacts.cover_letter`** (shape in **`BUILD_CONFIG.artifact_shapes`**), sharing cached context with **AST-300** resume pipeline, consuming **`{$WRITING_PREFERENCES}`** (**AST-299**). Trigger at **`RECOMMENDED`** after resume pipeline completes per **AST-369**/**AST-368** child work. **AST-300** blocks this ticket.

---

## Files Changed (planned)

| File | Change | Layer |
|------|--------|-------|
| `src/utils/config.py` | `artifact_shapes.cover_letter`; pipeline step list; token wiring refs. | utils |
| `src/core/agent.py` | Cover-letter chain driver; shared-cache reads from resume pipeline outputs. | core |
| `src/core/dispatcher.py` | Dispatch trigger ordering after resume (with **AST-369**). | core |
| `src/core/tracker.py` | Persist `cover_letter` blob; transitions with **AST-302**. | core |
| `src/ui/frontend` (AST-307) | Tab/editor for cover letter draft/final. | ui |

---

## Stage 1: Shapes + tasks

**Done when:** `BUILD_CONFIG.artifact_shapes.cover_letter` defined; `TASK_CONFIG` entries exist for each chain step.

1. Mirror **AST-300** plan’s config pattern (single ordered step list + shapes).
2. Wire **`{$WRITING_PREFERENCES}`** placeholder only where **AST-299** stores context (document token name in `TASK_CONFIG` prompts — Susan edits prompts in **AST-313**).

---

## Stage 2: do_task chain

**Done when:** Chain runs after resume artifact present; failures land in configured error states.

1. Implement after **AST-303/304** merge; reuse daisy-chain helper from resume side where DRY allows (§1.3).
2. No contact fields in model output — **builder** injects profile data at render (**Hedy** child).

---

## Stage 3: Persistence + dispatch (AST-369)

**Done when:** **AST-369** merged; verify `job_data.artifacts.cover_letter` write path.

---

## Stage 4: Token integration (AST-368)

**Done when:** **AST-368** merged; `resolve_tokens` includes chain tokens for cover letter prompts.

---

## Stage 5: UI (AST-307)

**Done when:** Report modal shows cover letter section bound to `job_data.artifacts.cover_letter`.

---

## Stage 6: Verify

**Done when:** `py_compile` clean; RECOMMENDED job runs resume then cover letter; candidate can edit in UI.

---

## Execution contract

Stop at any dependency boundary if upstream branch not merged; comment on **AST-301** with blocker.

---

## Self-Assessment

**Scope — `MAJOR-CHANGE`**  
Cross-layer pipeline + UI like **AST-300**.

**Conf — `LOW`**  
Heavy dependency stack (**AST-300**, **AST-368**, **AST-369**, **AST-302**, **AST-303**, **AST-304**, **AST-299**).

**Risk — `HIGH`**  
Same class as resume pipeline — data corruption / wrong dispatch order.

---

## Self-review vs ASTRAL_CODE_RULES

§2.1 config single source; §2.4 batch id; §3.3 imports respected. **Conflicts:** none once shapes align with **AST-300** cache sharing design.
