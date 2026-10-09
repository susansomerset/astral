# AST-1902 — Candidate Contact Detail is truncated after email

<!-- linear-archive: AST-1902 archived 2026-10-08 -->

## Linear archive (AST-1902)

**Archived:** 2026-10-08  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1902/candidate-contact-detail-is-truncated-after-email  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** chuckles  
**Priority / estimate:** Medium / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

The `job_resume` artifact saves the full `candidate_contact_detail` (`hire@susansomerset.com • 415-745-5238 • linkedin.com/in/susansomerset • California, USA (PST)`), but the rendered resume HTML header shows only the email: `<div class="contact"><span>hire@susansomerset.com</span></div>`. The cause is `_apply_contact_to_render_dict` in `src/core/builder.py` (added by AST-1014). Both `build_resume_from_job` and `build_base_resume` call it after content is loaded. It **overwrites** `render["candidate_contact_detail"]` with a string rebuilt from the candidate's `contact` library blob, using `contact_email`/`reply_email`, `phone`, `linkedin_url`, `github`, and `location`. It overwrites whenever at least one of those fields is non-empty. The candidate's stored contact blob most likely has only the email filled in (or has phone, LinkedIn, and location under keys the builder doesn't read), so the richer saved string gets replaced by a one-item string. I couldn't check this against production data because the local `data/astral.db` only has test candidates.

## To-be

The rendered resume header shows the full contact line the candidate actually has: email • phone • LinkedIn • location. A partially filled contact blob must never silently replace a more complete saved `candidate_contact_detail`.

## Proposed steps

1. Confirm the live candidate's `contact` blob: which of `contact_email` / `phone` / `linkedin_url` / `location` are actually filled in. This tells us whether the problem is the data or the code.
2. Product call (Susan): which source wins for the header contact line?
   * **(a)** The saved artifact's `candidate_contact_detail`, when non-empty, wins. The contact blob is only a fallback when the artifact has none.
   * **(b)** The contact blob stays authoritative (AST-1014 intent). The fix is populating the blob (Profile/contact UI) and/or merging: the blob fields fill in, but the builder never emits fewer parts than the saved string.
3. Change `_apply_contact_to_render_dict` to match the choice. Update the two call sites only if the signature changes.
4. Add a builder test: saved full contact line + email-only blob → header shows the full line (for option a), or the matching assertion for option b.

## Component scope

`src/core/builder.py` — modified. `_apply_contact_to_render_dict` is where the saved contact line gets overwritten. Its callers `build_resume_from_job` and `build_base_resume` are in the same file.
`src/utils/config.py` — possibly modified, only if option (b) needs a config-declared contact-part order or precedence flag instead of the hard-coded field list.
`tests/component/core/test_builder.py` — modified, through Betty (test tree): extend `TestAst1014BuilderContact` with the partial-blob regression.

## Technical scope

`src/core/builder.py`: modify the `_apply_contact_to_render_dict` function so it no longer unconditionally replaces a non-empty `render["candidate_contact_detail"]` with a string built from fewer parts. Either keep the artifact value when present (a), or merge blob parts with the saved value (b). This is the single point where the header contact line is decided for both job and base resume renders.
`src/utils/config.py` (option b only): possibly a new config field declaring contact-part order/precedence, so the builder isn't hard-coding which blob keys make up the line (config-source-of-truth).
`tests/component/core/test_builder.py`: a new test in the existing AST-1014 builder-contact class, locking the regression.

## Ancestor candidates

- [X] AST-1014 — contact/context/artifacts library (`docs/features/candidate/ast-1014-contact-context-artifacts-library.md`): introduced `_apply_contact_to_render_dict` and the blob-overwrites-render behavior (plan step 8)
- [ ] AST-1010 — header/contact + ATS meta + embedded styles (`docs/features/artifacts/ast-1010-header-contact-meta-styles.md`): owns the header contact span composition in `_emit_html_document`
- [ ] AST-294 — [builder.py](<http://builder.py>) resume and cover letter renderer (`docs/features/artifacts/ast-294-build-builderpy-resume-and-cover-letter-renderer.md`): original builder/render contract
- [ ] AST-1065 — update candidate UI for contact info (`docs/features/interface/ast-1065-update-candidate-ui-for-contact-info.md`): relevant if the root cause is an under-populated contact blob (option b)

---

## Original report

Saved contact detail for job_resume: `hire@susansomerset.com • 415-745-5238 • linkedin.com/in/susansomerset • California, USA (PST)`

this is the html output:

```
 <header class="header">
    <h1>Susan Somerset • Technical Program Manager (Product-Focused)</h1>
    <div class="contact"><span>hire@susansomerset.com</span></div>
  </header>
```

### Comments

#### chuckles — 2026-09-30T23:50:35.147Z
@susan PR #199 is ready, but check this before you merge it: the ftr picked up AST-1901's tests and bible (`test(AST-1901)` bug-repro for the candidate `api_keys` JSON array) from the shared `origin/tests` branch during Betty's qa-fix on AST-1905. AST-1901's product change is only on `ftr/AST-1851`, not on dev. If #199 merges first, dev gets roughly 33 failing tests in `test_candidates.py`, `test_api_candidate.py`, `test_candidate.py` and `test_AdminManageCandidates.test.tsx` until AST-1851 lands again. Two clean options: merge AST-1851's ftr first and I refresh this one, or merge #199 knowing those tests fail until then.

Also found along the way, not caused by this bug: 21 component tests already fail on dev (among them `TestAst1514AdviseResumeBriefJsonPayload`, `TestAst1259CandidateBatchApi`, `TestAst1584GetOperativeBaseResume`). And `ensure_component_venv.sh` only looks for Python 3.10–3.12, while this host has only 3.14.

---

_Implementation detail may live in git history on `origin/dev`._
