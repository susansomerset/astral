# AST-2041 — Autosave resume artifacts for base and job resumes

<!-- linear-archive: AST-2041 archived 2026-10-16 -->

## Linear archive (AST-2041)

**Archived:** 2026-10-16  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-2041/autosave-resume-artifacts-for-base-and-job-resumes  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** blocks: AST-2046

### Description

The Save button gets hidden with scroll. Please remove the save button and autosave with changes.

## As-is

On **Artifacts → Base Resume Content** and on the **Job Analysis Report → Job Resume** tab, the shared `ArtifactEditor` puts its Cancel and Save buttons in the page header (`dep-header`). Once the operator scrolls down through the section panels, that header scrolls away, so Save is out of reach. Edits are not saved until Save is clicked. The editor does have a 2-second debounced autosave already, but it only runs for the free-form criteria/rubric pages. Structure mode (base resume) and job persistence (job resume) are excluded, so those two pages fall back to the explicit header Save/Cancel.

## To-be

On both resume editors, body edits save themselves after the operator pauses typing, using the same debounced autosave the criteria pages use. There is no Save button, and the header shows the existing status text ("Saving..." / "Unsaved changes" / "All changes saved") instead. After **Generate/Regenerate**, the Save/Cancel pair stays. That is an accept-or-reject step for unreviewed generated content, and the no-silent-persist rule from AST-905 still applies. Leaving the page while edits are dirty still flushes them, which the unmount autosave already does.

## Proposed steps

1. In `ArtifactEditor.handleChange`, widen the autosave gate from free-form editors only to any editor whose bodies are editable and that is not in Generate review. That covers structure mode and job persistence.
2. In the header, show Save/Cancel only while in Generate review (`inReview`). Otherwise show the status text the criteria pages already use.
3. **Open question for Susan, about versioning:** each base-resume Save retires the `current` `astral_artifacts` row and inserts a new one (AST-1353). A 2-second autosave would add a version row every time typing pauses. Choose one: (a) accept that, (b) use a longer debounce for these two pages (needs your approval of the number), or (c) autosave the live blob only and snapshot on leave/blur. The job resume PUT path needs the same check.
4. **Open question for Susan, about scope:** should the structure-row **Save sections** button on Base Resume Content (title/format/enabled/page break/reorder) autosave too? Or does this ticket cover section *body* edits only? Save sections sits below the panel list and doesn't scroll away the same way.
5. Update the `ArtifactEditor` and `ArtifactsBaseResumeContent` component tests that currently click the header Save on these paths.

## Component scope

* `src/ui/frontend/src/components/ArtifactEditor.tsx`: **modified**. It owns the autosave gate, the header Save/Cancel rendering, and the structure-row Save sections button. The whole fix lives here.
* `src/ui/frontend/src/pages/ArtifactsBaseResumeContent.tsx`: **modified only if** Save sections is in scope (step 4). It owns `saveStructure` / `persistStructureRows` for structure rows.
* `src/ui/frontend/src/components/JobAnalysisReportModal.tsx`: **probably unchanged**. It passes `jobPersistence` with `onSaved: load`. A reload after every autosave may need softening if it disrupts typing.
* `src/core/candidate.py` / `src/data/database.py`: **modified only if** option (c) in step 3 is chosen. They own the save path that writes the `astral_artifacts` snapshot.

## Technical scope

* `ArtifactEditor.tsx`: modify `handleChange` so its autosave condition keys off body editability and not-in-review, instead of `tabChromeEditable`. Modify the header render so Save/Cancel show only in review mode. The reason is to make the resume editors use the existing debounced-save mechanism rather than adding a new one.
* `ArtifactsBaseResumeContent.tsx` (conditional): modify the structure-row change handler to debounce into the existing persist function in place of the Save sections button, so structure edits stop depending on a manual click.
* Backend save path (conditional, option c only): modify the base/job resume save so the live blob write is separate from the `astral_artifacts` version snapshot. Without that, autosave cadence would multiply version history.

## Ancestor candidates

- [X] [AST-1459](https://linear.app/astralcareermatch/issue/AST-1459): Resume editor is not working properly. This epic set the current explicit Save/Cancel on structure and job-persistence modes for both surfaces, with "do not rely on structure-mode autosave" in its plan (archived).
- [ ] [AST-1480](https://linear.app/astralcareermatch/issue/AST-1480): Restore structure-mode resume section body edit loop. Child of AST-1459 that built the load → edit → Save loop and kept Save sections separate from body Save (archived).
- [ ] [AST-1577](https://linear.app/astralcareermatch/issue/AST-1577): UI-consistency shape for the standardized base resume editor. It refactored `ArtifactEditor` / `ArtifactsBaseResumeContent` for `resume_content` save via the candidate API (archived).
- [ ] [AST-1353](<https://linear.app/astralcareermatch/issue/AST-1353>): Save Base Resume writes base_resume snapshot. It is the source of the version-row-per-save behavior that autosave would multiply (archived).
- [ ] [AST-553](<https://linear.app/astralcareermatch/issue/AST-553>): Structure-driven resume draft tabs in the Job Analysis Report. It introduced the job resume editor and its save round trip.
- [ ] [AST-1544](https://linear.app/astralcareermatch/issue/AST-1544): Job Resume Content still not editable. It made the job resume tab editable/savable like base resume (archived).

### Comments

#### chuckles — 2026-10-08T20:50:50.172Z
@susan Ready for UAT. The PR is attached. [AST-2051](https://linear.app/astralcareermatch/issue/AST-2051) (autosave fix) and [AST-2056](https://linear.app/astralcareermatch/issue/AST-2056) (tests) are both reviewed clean and merged on `ftr`.

Before you merge:
- 3 frontend tests already fail on `origin/dev`, unrelated to this fix: 2 JAR "Print Resume" tests (AST-1546 / AST-1350) can't find the button, and the AST-1577 ui-consistency test still reads `canon/directives/draft/patt.artifact.ui-consistency.md`, which has moved to `active/`. Nobody owns these yet. File them with `[bug]` if you want them fixed.
- Process issue: Betty's qa-fix `sync-child.sh --stay` step leaves merge commits on `tests`, and `validate-tests-branch` rejects them on push. She worked around it safely, but every qa-fix run will hit this until the skill is fixed.

When you're happy, move this to PR Ready and assign Chuckles, and finish-up will land it.

#### chuckles — 2026-10-08T20:31:09.900Z
Fix child [AST-2051](https://linear.app/astralcareermatch/issue/AST-2051) filed (Ada). The two open questions were skipped, so it follows your approved To-be: (a) same 2s autosave as the criteria pages, accepting one `astral_artifacts` version row per autosave, and **Save sections** stays as-is (section body edits only). Comment here if you want either changed before it's built.

---

_Implementation detail may live in git history on `origin/dev`._
