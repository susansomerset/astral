# AST-1378 — feedback rubric returned on a craft prompt

<!-- linear-archive: AST-1378 archived 2026-08-31 -->

## Linear archive (AST-1378)

**Archived:** 2026-08-31  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1378/feedback-rubric-returned-on-a-craft-prompt  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

On a `craft_*` rubric run (`craft_get_rubric` for `abrams`), the model returns a craft `criteria` payload **and** a feedback-style `agent_performance.vector_reviews` list (compact codes like `TRRACAVK`, `YERACAVK`, …) — i.e. rubric feedback on the rubric it just developed. Craft prompts should author criteria only; feedback reviews belong on grade/evaluate consumers, not on craft.

## To-be

`craft_*` rubric responses deliver complete `agent_payload.criteria` (and whatever craft envelope status fields craft needs) **without** emitting rubric-feedback `vector_reviews`. Feedback compact codes are reserved for grading/evaluate tasks that score an existing rubric against a job — not for the craft pass that invents the vectors.

## Proposed steps

1. Confirm where craft is taught to emit `vector_reviews` (shared `RUBRIC_FEEDBACK_CONFIG` / prompt suffix, craft `response_schema`, or AST-724 “twelve rubric-backed keys include craft” capture contract).
2. Split craft vs grade contracts: craft schema/prompts omit feedback reviews; grade/evaluate keep them.
3. Stop treating craft SUCCESS as a vector-feedback capture source (or no-op capture when `task_key` is `craft_*`) so a model that still leaks codes cannot persist craft-as-feedback.
4. Re-run `craft_get_rubric` on `abrams` and confirm the envelope has criteria and no feedback `vector_reviews`.

## Evidence (original report)

```
[abrams]
{
  "agent_performance": {
    "status": "success",
    "failure_note": "",
    "vector_reviews": [
      "TRRACAVK",
      "YERACAVK",
      "DGRACAVK",
      "SPRACAVK",
      "TLRACAVK",
      "REROCAVK",
      "DMRACAVK",
      "SCRACAVK",
      "LORACAVK",
      "RGRACAVK",
      "LARACAVK"
    ]
  },
  "agent_payload": {
    "criteria": [
      {
        "label": "Title Line Reads as This Role, Not That One",
        "code": "TR",
        "content": "POV: Recruiter's first two seconds reading her title line against the JD's role name.\nA == The JD's role is a Research Assistant, Research Associate, or Imaging/Research Technician in a neuroimaging or neuroscience lab, and her leading titles — 'Neuroimaging Research Assistant' as headline plus the most recent 'Graduate Student Researcher, Functional Neuroimaging' at USC — read as a direct match the recruiter recognizes without translation\nB == The JD's role is adjacent rather than exact — 'Imaging Analyst,' 'Research Data Specialist,' 'Lab Technician' — where her functional neuroimaging QC and analysis bullets let a recruiter complete the map in one step even though no title
```

## **craft_get_rubric-ff19fa20-5f6d-469c-a1bf-5c09b4574948**

```
[2026-08-15 00:34:56] INFO src.core.agent: run_next chain entry: task=craft_get_rubric batch_id=craft_get_rubric-ff19fa20-5f6d-469c-a1bf-5c09b4574948
[2026-08-15 00:34:56] INFO src.external.deepseek: LLM deepseek task=craft_get_rubric 414.0s stop=max_tokens tokens in=3882 out=31999
[2026-08-15 00:34:56] ERROR src.external.deepseek: LLM deepseek task=craft_get_rubric 414.0s error=Generation truncated (max_tokens) before complete JSON
[2026-08-15 00:34:56] ERROR src.core.agent: do_task(craft_get_rubric) provider call failed batch_id=craft_get_rubric-ff19fa20-5f6d-469c-a1bf-5c09b4574948 error=Generation truncated (max_tokens) before complete JSON
```

### Comments

#### chuckles — 2026-08-15T00:48:02.177Z
Restated per your note — not a token-cap bug. Craft returned feedback reviews (`TRRACAVK` et al.) on the rubric it just crafted; that must not happen on `craft_*`.

Ancestor candidates (ranked — pick / ask / reject):

1. **AST-724** (Archive, Auditor) — *runtime vector feedback capture*. Designed capture across **consumer + craft** (“twelve rubric-backed task keys”); most direct ownership of craft emitting/persisting `vector_reviews`.
2. **AST-378** (Archive) — parent epic for runtime rubric validation / feedback; AC that every rubric-backed agent task returns per-vector feedback (Relevance/Clarity/Verdict) — the policy craft is currently following.
3. **AST-859** (Archive) — `RUBRIC_FEEDBACK_CONFIG.prompt_suffix` / compact-code example wiring; likely how craft prompts get taught the feedback wire shape.
4. **AST-725** (Archive) — Admin Vector Feedback treats craft run keys as feedback writers via `CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY` expansion (downstream of the same craft-as-feedback assumption).

Prior menu (AST-903 / AST-900 / AST-1377 / AST-1191) retired for this bug — those were the max_tokens misread.

#### susan — 2026-08-15T00:46:27.379Z
This bug is unrelated to the cap.  It has to do with the fact that the agent responded with a feedback rubric "`TRRACAVK`" for the rubric it just developed, and it should not be responding with rubric feedback on craft-\* prompts.  Please restate to reflect that.

#### chuckles — 2026-08-15T00:38:59.753Z
Ancestor candidates (ranked — pick one, ask about one, or reject the set):

1. **AST-903** (Archive, Consult) — *UAT: craft_get_rubric JSON parse Unterminated string*. Exact prior: Get craft truncated mid-`criteria[].content` with `agent_performance`/`vector_reviews` envelope; shipped 32k floor + JSON `max_tokens` hard-fail. This log looks like that ceiling biting again (`out=31999`).
2. **AST-900** (Archive) — parent of AST-903; original “craft get rubric did not populate” epic that owned this failure family.
3. **AST-1377** / parent **AST-1376** (live Foundation) — explicitly parked `craft_*_rubric max_tokens / truncated JSON` as out of epic; useful “we knew this was still open” pointer, not the ownership ancestor.
4. **AST-1191** (artifacts) — hop-failure / timesheet trail around `max_tokens` classes; adjacent surfacing, not the craft-Get truncation root.

No git seed / no plan-fix until you move this to Todo (or name a different ancestor and bounce it back).

---

_Implementation detail may live in git history on `origin/dev`._
