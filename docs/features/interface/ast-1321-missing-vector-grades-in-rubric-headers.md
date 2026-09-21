# AST-1321 — Missing Vector Grades in Rubric headers

<!-- linear-archive: AST-1321 archived 2026-08-19 -->

## Linear archive (AST-1321)

**Archived:** 2026-08-19  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1321/missing-vector-grades-in-rubric-headers  
**Status at archive:** Archive  
**Project:** Astral Interface  
**Assignee:** chuckles  
**Priority / estimate:** High / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

```
<div class="collapsible-panel is-expanded"><div class="collapsible-panel-header"><button type="button" class="icon-control" aria-expanded="true" aria-label="Collapse section">▼</button><div class="collapsible-panel-label-wrap" tabindex="0" role="button" aria-expanded="true" aria-label="Section title; use chevron or Enter/Space to expand when collapsed">JD Analysis</div><div class="collapsible-panel-metadata"><div class="recommended-report-phase-grade-row"><span class="recommended-report-phase-grade-cell"><span class="grade-dot dot-b" title="Based on the candidate's bio provided, this job could be a good fit for them.">B</span><div class="confidence-bullets" aria-hidden="true"><span class="confidence-bullet confidence-bullet--on"></span><span class="confidence-bullet confidence-bullet--on"></span><span class="confidence-bullet confidence-bullet--on"></span><span class="confidence-bullet confidence-bullet--on"></span><span class="confidence-bullet"></span></div></span></div></div></div><div class="collapsible-panel-body"><div><p class="job-analysis-upshot-body">This is a staffing-agency listing, so the actual employer is hidden, but the JD itself is detailed and credible. It calls for a Senior TPM who can juggle product ownership, program management, and heavy external-partner liaison. The requirements are sharp—5+ years of TPM experience, healthcare or life sciences background, Agile delivery, and exposure to data platforms and AI/ML. That tells you the client knows what they need and isn't asking for a generic warm body.

There's an administrative element (SOW tracking, compliance reports), but it's balanced by strategic ownership of backlogs and initiatives. The language around AI/ML and regulated environments suggests a setting where your recent work—the AI recruiting pipeline, the GDPR and HIPAA compliance runs—would be directly applicable. The biggest blind spot is that you can't see the company's health or culture from this sheet alone; treat that as an open question.</p><div class="analysis-header"><div class="analysis-row"><div class="analysis-heading"><div class="analysis-grade-block"><span class="grade-dot dot-a">A</span><div class="confidence-bullets" aria-hidden="true"><span class="confidence-bullet confidence-bullet--on"></span><span class="confidence-bullet confidence-bullet--on"></span><span class="confidence-bullet confidence-bullet--on"></span><span class="confidence-bullet confidence-bullet--on"></span><span class="confidence-bullet confidence-bullet--on"></span></div></div><span class="analysis-vector">Embedded/Firmware/Hardware Domain</span><button class="analysis-rubric-link">show rubric</button></div><div class="analysis-reason">JD's domain is clearly software (SaaS, cloud, web, mobile) and not embedded/firmware/hardware, e.g. 'SaaS platform for enterprise workflows'</div></div><div class="analysis-row"><div class="analysis-heading"><div class="analysis-grade-block"><span class="grade-dot dot-x">X</span><div class="confidence-bullets" aria-hidden="true"><span class="confidence-bullet"></span><span class="confidence-bullet"></span><span class="confidence-bullet"></span><span class="confidence-bullet"></span><span class="confidence-bullet"></span></div></div><span class="analysis-vector">International/Global Scope</span><button class="analysis-rubric-link">show rubric</button></div><div class="analysis-reason">Cannot determine geographic scope from JD</div></div><div class="analysis-row"><div class="analysis-heading"><div class="analysis-grade-block"><span class="grade-dot dot-a">A</span><div class="confidence-bullets" aria-hidden="true"><span class="confidence-bullet confidence-bullet--on"></span><span class="confidence-bullet confidence-bullet--on"></span><span class="confidence-bullet confidence-bullet--on"></span><span class="confidence-bullet confidence-bullet--on"></span><span class="confidence-bullet confidence-bullet--on"></span></div></div><span class="analysis-vector">ML/Data Science Individual Contributor Role</span><button class="analysis-rubric-link">show rubric</button></div><div class="analysis-reason">JD is clearly a TPM, program manager, or technical leadership role, not an IC data science role, e.g. 'Technical Program Manager, Machine Learning'</div></div><div class="analysis-row"><div class="analysis-heading"><div class="analysis-grade-block"><span class="grade-dot dot-x">X</span><div class="confidence-bullets" aria-hidden="true"><span class="confidence-bullet"></span><span class="confidence-bullet"></span><span class="confidence-bullet"></span><span class="confidence-bullet"></span><span class="confidence-bullet"></span></div></div><span class="analysis-vector">Onsite Requirement</span><button class="analysis-rubric-link">show rubric</button></div><div class="analysis-reason">Cannot determine any location or work model from JD — no address, no remote/hybrid mention</div></div><div class="analysis-row"><div class="analysis-heading"><div class="analysis-grade-block"><span class="grade-dot dot-x">X</span><div class="confidence-bullets" aria-hidden="true"><span class="confidence-bullet"></span><span class="confidence-bullet"></span><span class="confidence-bullet"></span><span class="confidence-bullet"></span><span class="confidence-bullet"></span></div></div><span class="analysis-vector">Pre-PMF Startup Without Product Validation</span><button class="analysis-rubric-link">show rubric</button></div><div class="analysis-reason">Cannot determine product stage or company maturity from JD</div></div><div class="analysis-row"><div class="analysis-heading"><div class="analysis-grade-block"><span class="grade-dot dot-b">B</span><div class="confidence-bullets" aria-hidden="true"><span class="confidence-bullet confidence-bullet--on"></span><span class="confidence-bullet confidence-bullet--on"></span><span class="confidence-bullet confidence-bullet--on"></span><span class="confidence-bullet confidence-bullet--on"></span><span class="confidence-bullet"></span></div></div><span class="analysis-vector">Quality Check</span><button class="analysis-rubric-link">show rubric</button></div><div class="analysis-reason">This is a valid job description with full details of the role and requirements, but limited information about the company the candidate would be working for.</div></div><div class="analysis-row"><div class="analysis-heading"><div class="analysis-grade-block"><span class="grade-dot dot-b">B</span><div class="confidence-bullets" aria-hidden="true"><span class="confidence-bullet confidence-bullet--on"></span><span class="confidence-bullet confidence-bullet--on"></span><span class="confidence-bullet confidence-bullet--on"></span><span class="confidence-bullet confidence-bullet--on"></span><span class="confidence-bullet"></span></div></div><span class="analysis-vector">5 - Gut Check (GC)</span><button class="analysis-rubric-link">show rubric</button></div><div class="analysis-reason">Based on the candidate's bio provided, this job could be a good fit for them.</div></div></div></div></div></div>
```

I thought we fixed this issue a while back?  It's really important to see all the grades from a scan.  It would be a ticket involving using the job_data as the source for the column headers and content, not the candidate's current rubric.  In fact, it still works fine for the gazer-sourced jobs, just not for the meteorites.  That's a clue.

Also, the Analysis tab defaults with Job Description analysis expanded.  Please collapse all sections for the Analysis tab (other tab is fine)

### Comments

#### susan — 2026-08-12T04:44:11.526Z
1063 is the winner.

#### chuckles — 2026-08-12T04:40:13.120Z
**Resumed (Susan):** more recent candidate; memory of matching vectors to the *current candidate* rubric rather than the *job's* rubric.

**As-is:** On Recommended Job Analysis, phase section headers miss the full per-vector grade row from the scan (grades only clear after expand); works for gazer-sourced jobs, fails for meteorites — clue that headers/content are keyed off the wrong rubric epoch (live candidate vs job-carried). JD Analysis also opens expanded by default.

**To-be:** Headers (and body) source vector set from the analysis-time / job_data rubric so every graded vector shows in the collapsed header row for meteorites too; all Analysis-tab sections start collapsed (other tabs unchanged).

**Candidates (ranked — pick one or ask about any):**
1. `docs/features/artifacts/ast-1193-analysis-token-vector-rubric-match-parity.md` (AST-1193) — newest fit for "match to current candidate rubric": live label-or-code first, then job-carried `*_rubric` snapshot (AST-1063) when live drifts. Token/consult side, not the header UI itself.
2. `docs/features/interface/ast-1063-job-carried-rubric-hydration-for-list-columns.md` (AST-1063) — closest to Description wording: persist/surface analysis-time `*_rubric` on job_data; headers/columns must not use live candidate rubric. List-column focus, but same job-vs-live law + meteorite gap if snapshot missing.
3. `docs/features/interface/ast-1059-issue-with-the-rubric-grade-displays-on-the-jobs-list-pages.md` (AST-1059) — parent epic of 1063/1064; same "job-carried hydration, not live candidate rubric" product law.
4. `docs/features/interface/ast-950-analysis-tab-grades-confidence.md` (AST-950) — prior suggestion; Analysis tab header grade+confidence UI + JD default-expanded. Still plausible for the display/collapse half; weaker on gazer-vs-meteorite / rubric-source mismatch.

Already discussed #4 last round; #1–#3 are the fresher / rubric-source set for this pass.

#### chuckles — 2026-08-12T04:26:11.568Z
**Candidate ancestor:** `docs/features/interface/ast-950-analysis-tab-grades-confidence.md`

**As-is:** On the Recommended Job Analysis tab, phase section headers do not show the full per-vector grade row from the scan (so grades are only readable after expanding into the body rubric); JD Analysis also opens expanded by default.

**To-be:** Every graded vector’s grade (with confidence) is visible in the Analysis tab section headers so the full scan can be read collapsed; all Analysis tab sections start collapsed (JD included). Other tabs unchanged.

#### susan — 2026-08-12T04:25:36.064Z
Can you look for a more recent candidate? I remember something about trying to match the vectors to the CURRENT candidate rubric, rather than the JOB's rubric details.

#### chuckles — 2026-08-12T04:21:35.606Z
**Candidate ancestor:** `docs/features/interface/ast-950-analysis-tab-grades-confidence.md` (AST-950 — Analysis tab grades/confidence; header row should show grade icons + confidence for every graded vector).

**As-is:** On the Analysis tab, rubric/section headers are missing the per-vector grade display from a scan (Susan expected those grades visible), and JD Analysis opens expanded by default.

**To-be:** Every graded vector's grade shows in the Analysis rubric/section headers for the scan, and all Analysis-tab sections default collapsed (other tabs unchanged).

---

_Implementation detail may live in git history on `origin/dev`._
