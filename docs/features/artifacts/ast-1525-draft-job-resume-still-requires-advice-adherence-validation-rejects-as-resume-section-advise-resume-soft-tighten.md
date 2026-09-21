# AST-1525 — draft_job_resume still requires advice_adherence; validation rejects as resume section (Advise resume soft tighten)

<!-- linear-archive: AST-1525 archived 2026-09-09 -->

## Linear archive (AST-1525)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1525/draft-job-resume-still-requires-advice-adherence-validation-rejects-as  
**Status at archive:** Archive  
**Project:** Astral Artifacts  
**Assignee:** susan  
**Priority / estimate:** None / 2  
**Parent:** AST-1460 — Advise resume needs a coded list for clear adherence  
**Blocked by / blocks / related:** parent: AST-1460

### Description

## Susan's report (verbatim)

[bug]

```
Include one `advice_adherence` entry for every RESUME BRIEF code — exactly once each.

Output one JSON object, nothing else:
{
  "agent_performance": {"status": "success | failure", "failure_note": ""},
  "agent_payload": {
    "resume": { ...exactly the same keys and value types as the provided base resume; `experience` is an ordered array of job objects with `company`, `title`, `dates`, `location`, `accomplishments`... },
    "advice_adherence": [{"code": "R1", "status": "applied|skipped", "note": "how incorporated or why skipped"}, ...]
  }
}
```

resulted in:

```
[c70ca220-a6a5-4625-8e3f-b731e2aba685]
Validation failed: Unknown resume section key 'advice_adherence' (not in candidate base_resume keys: ['candidate_contact_detail', 'candidate_name', 'candidate_tagline', 'candidate_title', 'core_competencies', 'education_certifications', 'experience', 'highlights', 'prior_experience', 'professional_summary', 'technical_skills'])
```

## As-is

After the soft-tighten UAT, Judith's `draft_job_resume` path still surfaces an `advice_adherence` contract (prompt/schema text), and validation treats `advice_adherence` as an unknown resume section key — the hop fails.

## To-be

Draft hop uses the soft freeform `notes` contract (no `advice_adherence` in prompt/schema), and validation does not treat notes/adherence metadata as a resume section key, so a successful draft hop can complete.

## Suggested engineer

Hedy Lamarr (AST-1524 — Soft numbered-prose advise + draft notes prompts)

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
