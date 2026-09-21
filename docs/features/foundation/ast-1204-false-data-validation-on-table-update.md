# AST-1204 — false data validation on table update

<!-- linear-archive: AST-1204 archived 2026-08-14 -->

## Linear archive (AST-1204)

**Archived:** 2026-08-14  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1204/false-data-validation-on-table-update  
**Status at archive:** Archive  
**Project:** Astral Foundation  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Admin Data Management rejects a self-consistent `agent_task` paste because `run_next` is validated only against `TASK_CONFIG`, not against task keys present in the same paste (or the live `agent_task` catalog). Susan hit `run_next must be a configured task_key, got 'revise_cover_letter'` on `/admin/data_management` while the paste itself defined `revise_cover_letter` as a `task_key`. Operators need to update chain topology and prompts via Copy Output upsert without false rejects when the chain is internally complete.

## Functional scope

1. **Batch-aware** `run_next` **membership on Data Management upsert** — When pasting `agent_task` rows through Data Management / Copy Output upsert, a non-empty `run_next` is accepted when its target is a `task_key` in the same paste and/or already present as a current `agent_task` row (subject to Open questions on whether `TASK_CONFIG` remains an additional hard gate).
2. **Same membership rule on single-row task saves** — Manage Tasks / other `agent_task` save paths that call the same `run_next` validator use the same membership rule so paste and single-row edit do not disagree.
3. **Keep real guards** — Self-loops and cyclic `run_next` graphs still reject. Truly dangling targets (absent from the allowed membership set) still reject.
4. **Honest rejection message** — When a target is rejected, the operator-visible error names what membership set was checked (so "configured" is not misleading when the row exists in the paste).

## Architectural definition

* **Patterns to reuse** — `pattern.dispatch.run-next-chain-authority` (proposed; bind to statute): succession/membership for dispatch chains follows live `agent_task.run_next`, not a parallel config hop list; this epic aligns upsert validation with that authority for catalog membership of chain targets. `pattern.ui.admin-endpoint`: Data Management stays a thin authenticated admin surface; membership rules live in data/core, not React.
* **New patterns proposed** — none.
* **Applicable statutes** — `astral.dispatch.run-next-is-chain-authority` (do not treat `TASK_CONFIG` alone as chain-membership authority when `agent_task` already encodes the hops); `astral.config.config-source-of-truth` (`TASK_CONFIG` still owns schemas/specs — see Open questions); `astral.standards.data-raises-caller-logs` (validator raises; admin API returns JSON error); `astral.standards.in-scope-only`; `astral.layers.import-direction`; universal product set as applicable (`astral.standards.dry-and-focused-functions`, `astral.standards.no-cross-contamination`).

## Boundaries

* Does **not** register new hop keys (`revise_job_resume`, `revise_cover_letter`, `approve_artifacts`, etc.) in `TASK_CONFIG` or change artifact-chain runtime behavior — that is Artifacts / config work if Susan confirms those keys are intentional (Open question 2).
* Does **not** change repo-JSON startup/revert exact-apply semantics beyond sharing the corrected `run_next` membership helper if those paths already call it.
* Does **not** redesign Data Management UI, Copy Output format, or agent prompt content in the paste.
* Does **not** weaken cycle or self-loop checks.
* Does **not** change dispatch execution, claim/graduation, or §2.6.0 hop labeling beyond validation-at-persist.

## Acceptance criteria

1. Pasting Susan’s self-consistent Job Artifacts `agent_task` JSON (or an equivalent fixture where every non-empty `run_next` names a `task_key` present in the same paste) through Data Management succeeds without `run_next must be a configured task_key, got 'revise_cover_letter'`.
2. Pasting a row whose `run_next` names a key absent from the paste and absent from the allowed membership set still fails with an error that names the missing target and the membership rule in plain language.
3. A `run_next` self-loop still fails; a cyclic chain among pasted/current rows still fails.
4. A single-row Manage Tasks save that sets `run_next` to a target allowed under the same membership rule succeeds; a dangling target still fails.
5. No change to unrelated table upserts (non-`agent_task` Copy Output paths behave as today).

## Dependencies and blockers

none.

## Open questions

1. Should a non-empty `run_next` still **require** membership in `TASK_CONFIG` in addition to paste/catalog `task_key` presence (runtime schemas live there), or is paste/catalog presence enough at persist time with runtime failure deferred if config is missing?
2. Are `revise_job_resume`, `revise_cover_letter`, and `approve_artifacts` intentional new hop keys (needing a separate Artifacts/`TASK_CONFIG` registration ticket), or should the paste keep using existing keys such as `finalize_job_resume` / `finalize_cover_letter` / terminal empty `run_next`?

## Proposed child tickets

#### 1!: **Batch-aware run_next membership validation - Ada**

Owns correcting `run_next` membership for Data Management Copy Output upsert and the shared save-path validator so same-paste / live `agent_task` targets are not false-rejected; keeps self-loop and cycle checks; updates the operator-visible error text. Does **not** own new `TASK_CONFIG` hop registration (Open question 2).
**Citations:** `astral.dispatch.run-next-is-chain-authority`, `pattern.dispatch.run-next-chain-authority`, `astral.standards.data-raises-caller-logs`, `astral.config.config-source-of-truth`

#### 2: **Manage Tasks parity + regression lock - Katherine**

After #1: confirm Manage Tasks single-row save uses the same membership helper; add focused regression coverage for self-consistent paste success, dangling reject, and cycle/self-loop reject. Does **not** change UI chrome beyond error string already owned in #1.
**Citations:** `pattern.ui.admin-endpoint`, `astral.standards.in-scope-only`, `astral.standards.data-raises-caller-logs`

---

## Original brief

```
Astral error diagnostic
timestamp: 2026-08-06T03:55:07.389Z
message: run_next must be a configured task_key, got 'revise_cover_letter'
route: /admin/data_management
astral_candidate_id: somerset
```

Tried updating the agent_task table with the following content:

```
[
  {
    "agent_id": "ats_expert_atlas",
    "cache_prompt": "** {$FIRST_NAME}'s Base Resume Content\n\n{$BASE_RESUME}",
    "cache_prompt_b": "",
    "cache_prompt_c": "",
    "cache_prompt_d": "",
    "current": 1,
    "nocache_prompt": "",
    "run_next": "contemplate_job",
    "system_prompt": "NOTE: Please see \"AGENT MESSAGE\" below for your system context prompt and instructions. Please review all of the following content thoroughly before proceeding with your work.\n\n** CANDIDATE\nOur candidate is {$FIRST_NAME} {$LAST_NAME}.\n\n{$BIO_SUMMARY}\n\n### {$FIRST_NAME}'s Strengths\n{$STRENGTHS}\n\n### {$FIRST_NAME}'s Priorities\n{$PRIORITIES}\n\n### {$FIRST_NAME}'s Deal Breakers\n{$DEAL_BREAKERS}\n\n### {$FIRST_NAME}'s Back Story\n{$BACKSTORY}\n\n(See below for {$FIRST_NAME}'s base resume contents.)\n\n* JOB DESC & PRIOR ANALYSIS\nNow, take a look at this job we found for {$FIRST_NAME}.\n\n### JOB DESCRIPTION FROM THE COMPANY SITE\n{$VISIBLE_JD}\n\n### JOB DESCRIPTION ANALYSIS RESULTS\n{$ANALYSIS_JD}\n\n### \"DO\" ANALYSIS RESULTS\n{$ANALYSIS_DO}\n\n### \"GET\" ANALYSIS RESULTS\n{$ANALYSIS_GET}\n\n## \"LIKE\" ANALYSIS RESULTS\n{$ANALYSIS_LIKE}",
    "task_group_name": "Job Artifacts",
    "task_group_order": "5000",
    "task_key": "anticipate_scan",
    "task_key_uuid": "9ecda403-06fc-496d-a9f8-029b264011b3",
    "task_name": "anticipate_scan",
    "task_seq": 1,
    "updated_at": "2026-08-05 00:00:00",
    "user_prompt": "## AGENT MESSAGE\n\n{$SELECTED_AGENT}\n\n## INSTRUCTIONS\n\nBefore you touch keywords, read this JD the way the person screening it will: ten seconds, one question in mind, \"is this the person?\" The GET/DO/LIKE analysis tells you what's true about fit. Your job is the gap between what's true and what this resume shows a stranger in a hurry.\n\nProduce a single text block with three labeled sections:\n\nSCREENER'S OBJECTIONS\nRanked. The reasons a screener passes on this resume for THIS role: not generic weaknesses, but the objections this specific document raises against this specific JD (identity mismatch, seniority read, rate assumptions, domain doubt). For each: one line naming the objection, one line on what would honestly neutralize it. The #1 objection is the thing Estelle and Judith must solve; say so plainly.\n\nMUST PROVE\nThe two or three things the screener must see proven on first skim to shortlist the candidate. For each, cite where the base resume already proves it, proves it weakly, or fails to. Quote actual resume language.\n\nKEYWORDS\nTwo tiers, no third:\n- REAL: terms from the JD the candidate can honestly claim. For each, cite the base-resume or candidate-context line that supports it. These are reframing targets.\n- GAP: terms the candidate cannot honestly claim. These may be addressed in the cover letter as honest trade-offs, or surfaced to the candidate; they must NEVER appear as resume claims. Do not suggest workarounds. Name the gap and move on.\n\nThis contract matters: downstream agents will treat REAL as permission and GAP as prohibition. A keyword you cannot support with a citation goes in GAP, full stop.\n\nClose with your honest read, two sentences max: where does this application stand, and what single change moves it most?"
  },
  {
    "agent_id": "content_writer_judith",
    "cache_prompt": "** {$FIRST_NAME}'s Base Resume Content\n\n{$BASE_RESUME}\n\n** Atlas's Outside Read\n\n{$CALLER_RESPONSE}",
    "cache_prompt_b": "",
    "cache_prompt_c": "",
    "cache_prompt_d": "",
    "current": 1,
    "nocache_prompt": "",
    "run_next": "advise_job_resume",
    "system_prompt": "{$CALLER_SYSTEM}",
    "task_group_name": "Job Artifacts",
    "task_group_order": "5000",
    "task_key": "contemplate_job",
    "task_key_uuid": "be58d346-8a94-4712-9058-23d8d4b8f1e6",
    "task_name": "contemplate_job",
    "task_seq": 2,
    "updated_at": "2026-08-05 00:00:00",
    "user_prompt": "## AGENT MESSAGE\n\n{$SELECTED_AGENT}\n\n## INSTRUCTIONS\n\nHi Judith,\n\nBefore anyone drafts anything for {$FIRST_NAME}, sit with this job. Imagine you are {$FIRST_NAME}, meeting the hiring manager for coffee before the formal process starts: casual, curious, no pressure. You've read the JD and Atlas's outside read. What would you actually want to talk about?\n\nThink it through in natural, conversational prose (no bullets, no headers), covering:\n\nWhat's the real problem behind this opening? Read between the lines: what's broken, growing, or changing? Ground your read in the JD's own phrasing: what it repeats, what it protests too much about, what's oddly specific.\n\nWhat caught your attention: the detail that made you think \"oh, that's interesting\"?\n\nWhat would you want to ask the hiring manager, if you could ask anything?\n\nWhere does {$FIRST_NAME}'s background genuinely not match? Name it, don't spin it.\n\nOne discipline while you think: keep fact and speculation separate. Facts come from the JD and the candidate's materials. Everything else, your read on their org, your guess at their pain, say it like a guess (\"I'd bet...\", \"my guess is...\"). Downstream agents may not present your speculation as fact, so label it honestly.\n\nThen close with four commitments, clearly labeled, one or two sentences each:\n\nTHESIS: the one observation specific to this company and role that could not appear in a letter to anyone else. If your thesis would survive a find-and-replace of the company name, it isn't one; dig again.\nSTORY: the one story from {$FIRST_NAME}'s actual background that proves the thesis or lands hardest, and why this one.\nQUESTION: the one genuine question worth exploring in the letter.\nGAPS: the honest gaps worth addressing, or \"none worth ink.\"\n\nThis becomes the creative brief for the resume summary and the cover letter. Make it something worth executing.\n\nWe appreciate you!\n-The Astral Team"
  },
  {
    "agent_id": "principal_recruiter_estelle",
    "cache_prompt": "{$CALLER_CACHE_A}",
    "cache_prompt_b": "** Judith's Coffee-Chat Brief\n\n{$CALLER_RESPONSE}",
    "cache_prompt_c": "",
    "cache_prompt_d": "",
    "current": 1,
    "nocache_prompt": "",
    "run_next": "draft_job_resume",
    "system_prompt": "{$CALLER_SYSTEM}",
    "task_group_name": "Job Artifacts",
    "task_group_order": "5000",
    "task_key": "advise_job_resume",
    "task_key_uuid": "9be0c361-4e7e-441d-86ba-5fe00d2e070e",
    "task_name": "advise_job_resume",
    "task_seq": 3,
    "updated_at": "2026-08-05 00:00:00",
    "user_prompt": "## AGENT MESSAGE\n\n{$SELECTED_AGENT}\n\n## INSTRUCTIONS\n\nHi Estelle,\n\nJudith has thought it through; Atlas has given the outside read. Now arbitrate and direct.\n\nHARD RULES. These bind everything you write below:\n1. Company names, job titles, and employment dates are immutable: byte-identical to the base resume. Overqualification worries get handled in the cover letter, never by editing history.\n2. Every addition or reframe you direct must cite its source: quote the line from the base resume, backstory, strengths, priorities, or LinkedIn that supports it. If you cannot quote support, it goes on the ASK CANDIDATE list, not in the resume.\n3. No conditional instructions. \"If she has X, add it\" is forbidden; Judith has no one to ask mid-draft. Either you cite it or you route it to ASK CANDIDATE.\n4. Atlas's GAP keywords never become resume claims. REAL keywords only, woven where the cited experience already lives.\n\nProduce three sections:\n\nRESUME BRIEF\nEnumerated, concrete instructions: what to promote, cut, reorder, reframe, each with its citation. Reframing means new emphasis on true content, not new content. Solve Atlas's #1 objection first.\n\nCOVER LETTER DIRECTION\nRatify or veto Judith's THESIS, STORY, and QUESTION, one line of reasoning each. If you veto, propose the replacement and its grounding. Add your tone read and gap handling. Direct the prose; do not draft it.\n\nASK CANDIDATE\nAnything that would strengthen this application if true but lacks a citation. Phrase each as a direct question the candidate can answer in one line.\n\nJudith is good at her job; she needs a precise brief, not encouragement."
  },
  {
    "agent_id": "content_writer_judith",
    "cache_prompt": "{$CALLER_CACHE_A}",
    "cache_prompt_b": "{$CALLER_CACHE_B}",
    "cache_prompt_c": "** Estelle's Brief\n\n{$CALLER_RESPONSE}",
    "cache_prompt_d": "",
    "current": 1,
    "nocache_prompt": "",
    "run_next": "check_job_resume",
    "system_prompt": "{$CALLER_SYSTEM}",
    "task_group_name": "Job Artifacts",
    "task_group_order": "5000",
    "task_key": "draft_job_resume",
    "task_key_uuid": "7d5d16dd-6465-4a97-a16f-de55a56b8e55",
    "task_name": "draft_job_resume",
    "task_seq": 4,
    "updated_at": "2026-08-05 00:00:00",
    "user_prompt": "## AGENT MESSAGE\n\n{$SELECTED_AGENT}\n\n## INSTRUCTIONS\n\nHi Judith,\n\nTime to revise the resume. You have the base resume, Estelle's brief, Atlas's read, and your own coffee-chat thinking.\n\nFollow Estelle's brief, except where it conflicts with these rules, which always win:\n- Every claim traces to the candidate's actual materials. Same company names, same titles, same dates, same metrics. \"Built onboarding for 12 engineering teams\" never becomes \"designed enterprise onboarding systems.\"\n- If a brief instruction lacks support in the candidate's materials, skip it and record it under deviations. Do not improvise a compromise claim.\n- When in doubt, understate.\n- The WRITING INSTRUCTIONS provided in your context apply to every word of resume prose.\n\nThe professional summary is prose with a voice: let your coffee-chat THESIS shape its through-line. The rest is bullets: active voice, strong verbs, concrete details, no buzzword soup.\n\nOutput one JSON object, nothing else:\n{\n  \"agent_performance\": {\"status\": \"success | failure\", \"failure_note\": \"\"},\n  \"agent_payload\": {\n    \"resume\": { ...exactly the same keys and value types as the provided base resume; experience remains a single string formatted like the base... },\n    \"deviations\": [\"instruction skipped and why\"]\n  }\n}\nNo new keys, no restructuring. A changed structure fails validation and your work is lost."
  },
  {
    "agent_id": "job_analyst_grace",
    "cache_prompt": "{$CALLER_CACHE_A}",
    "cache_prompt_b": "{$CALLER_CACHE_B}",
    "cache_prompt_c": "{$CALLER_CACHE_C}",
    "cache_prompt_d": "** Judith's Draft for {$FIRST_NAME}'s application to this job\n\n{$CALLER_RESPONSE}",
    "current": 1,
    "nocache_prompt": "",
    "run_next": "revise_job_resume",
    "system_prompt": "{$CALLER_SYSTEM}",
    "task_group_name": "Job Artifacts",
    "task_group_order": "5000",
    "task_key": "check_job_resume",
    "task_key_uuid": "0b9369bd-65ac-49f1-8104-e0faf28e30ef",
    "task_name": "check_job_resume",
    "task_seq": 5,
    "updated_at": "2026-08-05 00:00:00",
    "user_prompt": "Hi Grace,\n\nJudith has revised the resume for this application. Verify every factual claim against the candidate's source materials.\n\nValid sources, in order of authority: base resume, backstory, strengths, priorities, LinkedIn, bio. All are in your context. A claim supported by ANY of them passes; cite which one, quoting the supporting line verbatim. Quote carefully: never attribute backstory text to the base resume or vice versa.\n\nFlag:\n- Invented claims: no source supports them.\n- Upgraded claims: \"contributed to\" became \"led\"; \"supported\" became \"owned.\"\n- Mutated identity: any company name, job title, or employment date that differs from the base resume by even a character.\n- Dropped content: base-resume content this JD explicitly asks for that the revision lost.\n- Keyword stuffing: JD terms inserted where the cited experience does not live.\n\nNot your scope: style, structure, or word choice within accurate claims.\n\nOutput one JSON object exactly:\n{\n  \"agent_performance\": {\"status\": \"success | failure\", \"failure_note\": \"\"},\n  \"agent_payload\": {\n    \"verdict\": \"clean | issues_found\",\n    \"discrepancies\": [\n      {\"severity\": \"high | medium | low\", \"location\": \"\", \"revised_text\": \"\", \"source_check\": {\"document\": \"\", \"quote\": \"\", \"supports\": false}, \"issue\": \"\", \"required_fix\": \"\"}\n    ]\n  }\n}\nVerdict \"clean\" with an empty discrepancies array if everything checks out. The software parsing this response has no tolerance for extra keys or commentary."
  },
  {
    "agent_id": "content_writer_judith",
    "cache_prompt": "{$CALLER_CACHE_A}",
    "cache_prompt_b": "{$CALLER_CACHE_B}",
    "cache_prompt_c": "{$CALLER_CACHE_C}",
    "cache_prompt_d": "{$CALLER_CACHE_D}",
    "current": 1,
    "nocache_prompt": "** Grace's Fact-Check\n\n{$CALLER_RESPONSE}",
    "run_next": "draft_cover_letter",
    "system_prompt": "{$CALLER_SYSTEM}",
    "task_group_name": "Job Artifacts",
    "task_group_order": "5000",
    "task_key": "revise_job_resume",
    "task_key_uuid": "addb139b-24f6-4e20-80ea-cea9ffbe02a6",
    "task_name": "revise_job_resume",
    "task_seq": 6,
    "updated_at": "2026-08-05 00:00:00",
    "user_prompt": "Hi Judith,\n\nGrace's fact-check is below. Produce the final resume by applying it to your draft.\n\nFor each discrepancy, exactly one of two actions:\n1. FIX: revert to what the source supports, or cut the claim.\n2. DEFEND: keep your text and quote the candidate-context line that supports it (Grace can miss a source or misattribute one).\n\nNo third option, and no new content: this pass may only fix, defend, or restore base-resume language. The WRITING INSTRUCTIONS still apply; this is also the pass to catch any banned characters.\n\nOutput one JSON object exactly:\n{\n  \"agent_performance\": {\"status\": \"success | failure\", \"failure_note\": \"\"},\n  \"agent_payload\": {\n    \"resume\": { ...same keys and value types as the base resume... },\n    \"dispositions\": [{\"discrepancy_location\": \"\", \"action\": \"fixed | defended\", \"note\": \"\"}],\n    \"ask_candidate\": [\"surviving questions from Estelle's brief\"]\n  }\n}"
  },
  {
    "agent_id": "content_writer_judith",
    "cache_prompt": "** Final Resume Content (approved for this application)\n\n{$CALLER_RESPONSE}",
    "cache_prompt_b": "{$CALLER_CACHE_B}",
    "cache_prompt_c": "{$CALLER_CACHE_C}",
    "cache_prompt_d": "",
    "current": 1,
    "nocache_prompt": "",
    "run_next": "check_cover_letter",
    "system_prompt": "{$CALLER_SYSTEM}",
    "task_group_name": "Job Artifacts",
    "task_group_order": "5000",
    "task_key": "draft_cover_letter",
    "task_key_uuid": "a286b9f1-435d-4aa3-b609-2903eabb777b",
    "task_name": "draft_cover_letter",
    "task_seq": 7,
    "updated_at": "2026-08-05 00:00:00",
    "user_prompt": "You are writing a cover letter as {$FIRST_NAME} {$LAST_NAME}. It must sound like {$THEY} wrote it: a sharp, specific letter no other applicant could send, about no other job.\n\nYour creative brief is your own coffee-chat commitments as ratified by Estelle: the THESIS, the STORY, the QUESTION, the GAPS. The thesis is the letter's spine. If you find yourself writing a letter that would survive swapping the company name, stop and reread the brief.\n\nThe WRITING_STYLE observations in your context show {$FIRST_NAME}'s actual words with notes on the moves. Match the moves and the register, never the topics. The WRITING INSTRUCTIONS are non-negotiable.\n\nIngredients. The letter needs all of these, in whatever order serves the thesis; there is no fixed structure, and the four-beat cover letter is exactly what we are not writing:\n- The story, concretely: what was broken, what {$THEY} did, what happened. Metrics only if the final resume has them.\n- The question, explored: show you're already thinking about it, don't just ask it.\n- Why {$FIRST_NAME}: one paragraph at most.\n- Gaps, only if the brief says so: honest trade-off framing (\"You won't find X in my background. What I bring instead is Y.\"), never spin.\n- A close in {$THEIR} voice that fits this company. One plain sentence beats boilerplate.\n\nAccuracy: every metric matches the final resume and its original context; every fact traces to the candidate's materials; every company name spelled correctly. Tell the brief's story, not a substitute.\n\nHard limits: under 300 words. Match the JD's energy without mimicking its jargon.\n\nOutput one JSON object exactly:\n{\n  \"agent_performance\": {\"status\": \"success | failure\", \"failure_note\": \"\"},\n  \"agent_payload\": {\"re_line\": \"\", \"body\": \"\", \"signature\": \"{$FIRST_NAME} {$LAST_NAME}\"}\n}\nThe signature is the candidate's name, nothing more: no titles. The body contains no header block, no date, no address.\n\nGut check before output: would a hiring manager remember this tomorrow? Does it sound like a person? Would {$FIRST_NAME} actually send it?"
  },
  {
    "agent_id": "job_analyst_grace",
    "cache_prompt": "{$CALLER_CACHE_A}",
    "cache_prompt_b": "== COVER LETTER DRAFT\n\n{$CALLER_RESPONSE}",
    "cache_prompt_c": "",
    "cache_prompt_d": "",
    "current": 1,
    "nocache_prompt": "",
    "run_next": "revise_cover_letter",
    "system_prompt": "{$CALLER_SYSTEM}",
    "task_group_name": "Job Artifacts",
    "task_group_order": "5000",
    "task_key": "check_cover_letter",
    "task_key_uuid": "75931a6a-820a-4286-911c-1e48fdbca9dc",
    "task_name": "check_cover_letter",
    "task_seq": 8,
    "updated_at": "2026-08-05 00:00:00",
    "user_prompt": "Hi Grace,\n\nEvaluate the cover letter draft for accuracy only.\n\nVerify every factual claim against the candidate's source materials (base resume, backstory, strengths, priorities, LinkedIn, bio), the final resume, and the JD. Pay particular attention to attribution: a real metric attached to the wrong company or the wrong project is a fabrication. For each issue, quote the source that supports or contradicts the claim and name the document.\n\nStyle, tone, and structure are not your scope.\n\nOutput one JSON object exactly:\n{\n  \"agent_performance\": {\"status\": \"success | failure\", \"failure_note\": \"\"},\n  \"agent_payload\": {\n    \"verdict\": \"clean | issues_found\",\n    \"issues\": [{\"severity\": \"high | medium | low\", \"claim\": \"\", \"source_check\": {\"document\": \"\", \"quote\": \"\", \"supports\": false}, \"required_fix\": \"\"}]\n  }\n}"
  },
  {
    "agent_id": "content_writer_judith",
    "cache_prompt": "{$CALLER_CACHE_A}",
    "cache_prompt_b": "{$CALLER_CACHE_B}",
    "cache_prompt_c": "** Grace's Fact-Check\n\n{$CALLER_RESPONSE}",
    "cache_prompt_d": "",
    "current": 1,
    "nocache_prompt": "",
    "run_next": "approve_artifacts",
    "system_prompt": "{$CALLER_SYSTEM}",
    "task_group_name": "Job Artifacts",
    "task_group_order": "5000",
    "task_key": "revise_cover_letter",
    "task_key_uuid": "b0826b04-e940-4cc4-80ac-9cf6d2e3e98b",
    "task_name": "revise_cover_letter",
    "task_seq": 9,
    "updated_at": "2026-08-05 00:00:00",
    "user_prompt": "Hi Judith,\n\nGrace's fact-check on your letter is below. Produce the final letter.\n\nSame discipline as the resume pass: for each issue, FIX (correct to what the source supports) or DEFEND (quote the candidate-context line Grace missed). Keep the THESIS, the STORY, and the QUESTION intact unless an issue makes them untrue; accuracy repairs change facts, not voice. Stay under 300 words. The WRITING INSTRUCTIONS apply; scan for banned characters before you output.\n\nOutput one JSON object exactly:\n{\n  \"agent_performance\": {\"status\": \"success | failure\", \"failure_note\": \"\"},\n  \"agent_payload\": {\n    \"re_line\": \"\", \"body\": \"\", \"signature\": \"{$FIRST_NAME} {$LAST_NAME}\",\n    \"dispositions\": [{\"claim\": \"\", \"action\": \"fixed | defended\", \"note\": \"\"}]\n  }\n}"
  },
  {
    "agent_id": "principal_recruiter_estelle",
    "cache_prompt": "{$CALLER_CACHE_A}",
    "cache_prompt_b": "** Final Cover Letter\n\n{$CALLER_RESPONSE}",
    "cache_prompt_c": "",
    "cache_prompt_d": "",
    "current": 1,
    "nocache_prompt": "",
    "run_next": "",
    "system_prompt": "{$CALLER_SYSTEM}",
    "task_group_name": "Job Artifacts",
    "task_group_order": "5000",
    "task_key": "approve_artifacts",
    "task_key_uuid": "7cecea99-9a55-40e4-8dca-ff872a151751",
    "task_name": "approve_artifacts",
    "task_seq": 10,
    "updated_at": "2026-08-05 00:00:00",
    "user_prompt": "Hi Estelle,\n\nThe full artifact set is in front of you: final resume, final cover letter, and the dispositions from both fact-check rounds. You are the last gate before this lands in {$FIRST_NAME}'s feed. You approve or you bounce; you do not rewrite. If prose needs changing, that is a bounce with a note, even for one sentence.\n\nRun these checks:\n\n1. ONE TRUE STORY: do the resume and letter tell the same story about the same person? Headline, signature, claims, and emphasis must cohere, and both must square with the base resume.\n2. IMMUTABLES: company names, job titles, employment dates, byte-identical to the base resume. Any drift is an automatic bounce.\n3. MECHANICAL: no placeholder text (anything like [Company Name]), no characters banned by the WRITING INSTRUCTIONS, letter under 300 words, no header block inside the letter body.\n4. THESIS: the letter contains an observation specific to this company. If the letter would survive a company-name swap, bounce it; \"generic letter\" is a defect, not a style choice.\n5. DISPOSITIONS: every fact-check discrepancy shows as fixed or defended-with-citation. Undefended survivors are a bounce.\n6. APPLICATION QUESTIONS: scan the JD text for explicit application questions. If present, draft responses (max 255 characters each, accurate, in the candidate's voice per WRITING_STYLE). If none, return an empty array without commentary.\n\nOutput one JSON object exactly:\n{\n  \"agent_performance\": {\"status\": \"success | failure\", \"failure_note\": \"\"},\n  \"agent_payload\": {\n    \"verdict\": \"approved | bounce\",\n    \"bounce\": {\"target\": \"revise_job_resume | revise_cover_letter | none\", \"notes\": [\"specific and actionable\"]},\n    \"application_question_responses\": [{\"question\": \"\", \"response\": \"\"}],\n    \"ask_candidate\": [\"consolidated open questions for {$FIRST_NAME}\"],\n    \"reviewer_note\": \"two sentences max for the candidate's feed\"\n  }\n}\n\nAccuracy is the non-negotiable; everything else is judgment. But judgment here means verdicts, not edits."
  }
]
```

### Comments

#### chuckles — 2026-08-06T04:02:24.884Z
@susan

1. Should non-empty `run_next` still require `TASK_CONFIG` membership in addition to paste/catalog `task_key` presence, or is paste/catalog enough at persist time?
2. Are `revise_job_resume` / `revise_cover_letter` / `approve_artifacts` intentional new hop keys (separate Artifacts/`TASK_CONFIG` ticket), or should the paste use existing `finalize_*` keys?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
