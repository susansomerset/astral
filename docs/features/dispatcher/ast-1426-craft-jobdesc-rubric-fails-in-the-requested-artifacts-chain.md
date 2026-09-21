# AST-1426 — craft_jobdesc_rubric fails in the REQUESTED_ARTIFACTS chain

<!-- linear-archive: AST-1426 archived 2026-09-09 -->

## Linear archive (AST-1426)

**Archived:** 2026-09-09  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1426/craft-jobdesc-rubric-fails-in-the-requested-artifacts-chain  
**Status at archive:** Archive  
**Project:** Astral Dispatcher  
**Assignee:** chuckles  
**Priority / estimate:** Urgent / 5  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## As-is

Ancestor locked: **AST-1243** (Candidate Artifacts now daisy chain). That epic put `REQUESTED_ARTIFACTS` on a live `agent_task.run_next` walk with per-hop persist and no hop-order list in `config.py`. In this run the hop that executed was `craft_joblist_rubric` (`in_run_next_chain=True`); the LLM returned a `joblist_rubric` payload, then `persist_candidate_craft_hops` rejected vector **Onsite Requirement** because the grade letters were inline (`A == …`) instead of one `A =` / `B:` / `C ==` line each. The hop recorded `chain_hop_failed`, so later hops — including `craft_jobdesc_rubric` named in the title — never run. Chain participation is still not “`run_next` is set, period”: remaining code/config gates and `suppress_run_next` callers still walk or suppress the chain. A mid-hop one-off has no `dispatch_task` skip-daisy-chain toggle. Hop output is not `<dispatch_task.trigger_state>.<completed_task_key>`.

## To-be

Same AST-1243 contract, completed: daisy chain is entirely database-driven. No config array, settings block, or code enumeration gates who is in a chain. If an `agent_task` has `run_next` set, that is the only signal that it participates. A regular `dispatch_task` that starts on a `task_key` with `run_next` uses the daisy-chain path; a `skip-daisy-chain` toggle on the `dispatch_task` itself covers a one-off mid-hop run. The output state of the daisy chain (current and future) is `<dispatch_task.trigger_state>.<completed_task_key>`. `craft_jobdesc_rubric` (and the rest of the live `REQUESTED_ARTIFACTS` walk) persist and continue.

## Proposed steps

1. Patch against AST-1243's feature doc (`docs/features/candidate/ast-1243-candidate-artifacts-now-daisy-chain.md`) — do not revive AST-1109's [config.py](<http://config.py>) epic unless that doc's remaining gates are the actual block.
2. Confirm the live `REQUESTED_ARTIFACTS` walk is `agent_task.run_next` only; stop consulting any leftover membership list on this path.
3. Expose a `skip-daisy-chain` toggle on `dispatch_task` (likely the existing `suppress_run_next` gate) so a mid-hop one-off does not walk the rest of the chain.
4. Make chain hop output/graduation `<dispatch_task.trigger_state>.<completed_task_key>` for current and future chains.
5. Unstick the pasted hop: either the craft prompt emits one-grade-letter-per-line, or persist accepts the inline `A ==` form, so `craft_joblist_rubric` / `craft_jobdesc_rubric` can persist and the walk can continue.

## Original report

I have been told that there are arrays or settings or somesuch in config or elsewhere in the code that "registers" daisy-chain tasks.  THIS SHOULD NOT BE THE CASE.

The daisy chain should be ENTIRELY database-driven, no extra validation, processing, enumeration, or other gatekeeping ANYWHERE in the code.  If the task has a run_next task key set, then it is participating in a daisy chain.  It is as simple as that.

I would like to be able to set a "skip-daisy-chain" toggle on the dispatch_task, itself, so that I can say "this is a one-off run for a mid-hop task, don't do the whole chain" but to have a regular dispatch_task that starts on one task_key that has a run-next set in the agent_task, this should be the ONLY indication necessary to use the daisy chaining logic, and the output state of the daisy-chain is <dispatch_task.trigger_state>.<completed_task_key>.  This is true for BOTH daisy chains and FUTURE daisy chains.

```
[2026-08-18 23:27:59] DEBUG src.core.agent: do_task index 1/1 somerset -> task start
[2026-08-18 23:27:59] DEBUG src.core.agent:  | task_key=craft_joblist_rubric batch_id=craft_joblist_rubric-cc7e6d63-e318-4f8e-acab-255e6a01dbef index=somerset in_run_next_chain=True
[2026-08-18 23:27:59] DEBUG src.core.agent: do_task.candidate_token_view index 1/1 somerset -> success — name tokens
[2026-08-18 23:27:59] DEBUG src.core.agent:  | found first=nonempty last=nonempty full=nonempty branch=load_by_id
[2026-08-18 23:27:59] DEBUG src.core.agent:  | recorded FIRST_NAME='Susan' LAST_NAME='Somerset' FULL_NAME='Susan Somerset'
[2026-08-18 23:27:59] INFO src.core.agent: [DEBUG] do_task('craft_joblist_rubric'): brain_setting=Big provider=deepseek model=deepseek-v4-pro max_tokens=384000 temp=0.0 skip_cache=False candidate=somerset
[2026-08-18 23:27:59] DEBUG src.core.agent:  | llm_params provider=deepseek brain_setting=Big model=deepseek-v4-pro max_tokens=384000 temp=0.0 skip_cache=False candidate_id=somerset
[2026-08-18 23:27:59] DEBUG src.core.agent:  | blocks system=2 user=1 runtime_prompt_segments=3
[2026-08-18 23:27:59] INFO src.external.deepseek: LLM deepseek task=craft_joblist_rubric 11.0s stop=end_turn tokens in=4794 out=783
[2026-08-18 23:27:59] DEBUG src.external.deepseek: send_to_deepseek index 1/1 craft_joblist_rubric -> success
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  | provider=deepseek model=deepseek-v4-pro task=craft_joblist_rubric duration=11.0s stop_reason=end_turn
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  | vendor=deepseek-v4-pro tokens fresh=4794 cache_read=2560 cache_write=0 output=783
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  | response_preview:
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  | {
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |   "agent_performance": {
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |     "status": "success",
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |     "failure_note": ""
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |   },
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |   "agent_payload": {
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |     "criteria": [
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |       {
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |         "label": "Onsite Requirement",
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |         "code": "OR",
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |         "importance": 10,
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |         "content": "Susan, scanning a bare listing summary, asking only whether the fields shown already rule this one out. A == location field states Remote, Fully Remote, or Work From Home. B == location field states a Bay Area city (San Francisco, Oakland, Berkeley, Walnut Creek, Alameda) with no onsite requirement stated. C == location field states Hybrid with a Bay Area city. D == location field states Hybrid with a non-Bay Area city. F == location field states On-Site, Onsite, In-Office, or In-Person. X == location field is absent or blank."
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |       },
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |       {
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |         "label": "Below-Floor Salary",
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |         "code": "BS",
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |         "importance": 8,
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |         "content": "Susan, scanning a bare listing summary, asking only whether the fields shown already rule this one out. A == salary field states an hourly rate of $50 or higher. B == salary field states an annual salary of $104,000 or higher. C == salary field states a range whose midpoint is $50/hr or higher. D == salary field states a range whose midpoint is below $50/hr. F == salary field states an hourly rate below $50 or an annual salary below $104,000. X == salary field is absent or blank."
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |       },
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |       {
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |         "label": "Contract-Only Engagement",
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |         "code": "CE",
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |         "importance": 6,
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |         "content": "Susan, scanning a bare listing summary, asking only whether the fields shown already rule this one out. A == employment_type field states Contract, Contract-to-Hire, Temporary, or Freelance. B == employment_type field states Full-Time with no other disqualifying field. C == employment_type field states Part-Time with no other disqualifying field. D == employment_type field states Internship or Volunteer. F == employment_type field states Permanent, Direct Hire, or Full-Time Employee with no contract option mentioned. X == employment_type field is absent or blank."
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |       },
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |       {
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |         "label": "Embedded Systems Focus",
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |         "code": "ES",
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |         "importance": 8,
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |         "content": "Susan, scanning a bare listing summary, asking only whether the fields shown already rule this one out. A == title or summary field states Software, Web, Cloud, SaaS, or Application. B == title or summary field states Program Manager, Technical Program Manager, or Delivery Lead with no hardware mention. C == title or summary field states a general engineering role with no hardware mention. D == title or summary field mentions hardware, firmware, or embedded in passing. F == title or summary field states Embedded Systems, Firmware, Hardware, or IoT as the primary focus. X == title and summary fields are absent or blank."
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |       },
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |       {
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |         "label": "Pre-PMF Startup",
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |         "code": "PS",
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |         "importance": 6,
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |         "content": "Susan, scanning a bare listing summary, asking only whether the fields shown already rule this one out. A == company_size field states 50 or more employees. B == company_size field states 50-500 employees. C == company_size field states 500+ employees. D == company_size field states 10-49 employees. F == company_size field states fewer than 10 employees or the summary explicitly states pre-product-market-fit, pre-revenue, or seed stage. X == company_size field is absent or blank."
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |       }
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |     ]
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  |   }
[2026-08-18 23:27:59] DEBUG src.external.deepseek:  | }
[2026-08-18 23:27:59] DEBUG src.core.agent: _store_prompt_blocks index 1/3 SYSTEM:craft_joblist_rubric-cc7e6d63-e318-4f8e-acab-255e6a01dbef-system-edbc203ef4ca20d3 -> ref_existing
[2026-08-18 23:27:59] DEBUG src.core.agent:  | found block_type=SYSTEM chars=3737
[2026-08-18 23:27:59] DEBUG src.core.agent:  | §1 ESTELLE: Principal Recruiter for the Astral Career Match Team
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | Our candidate, Susan Somerset or Susan, is keen to find her best professional role, and you are a key contributor to that effort. You'll find out all about her in the provided content, so stay tuned.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | §1.1 Who You Are. 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | You are Estelle, a recruiting strategist with 25 years of technical recruiting expertise. You are Susan's advocate and the team's overseer. You interview candidates and build their profile, you write the rubrics downstream agents grade with, you tell Susan what an analysis actually means, you direct the strategy for her application materials, and you are the last set of eyes before anything reaches her.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | You are warm with people and unsentimental about claims. You have a working bullshit detector and you point it at your own team's output, and at your own. Advocacy means getting Susan a real shot, not flattering her or padding her history.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | §1.2 The Rule Under Everything. 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | A claim about Susan is worth exactly what its source is worth. Anything you assert, or direct someone else to assert, must be quotable from Susan's own material: base resume, backstory, strengths, priorities, LinkedIn, bio. If you cannot quote support for it, it is not a fact you may use. It is a question for Susan.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | Company names, job titles, and employment dates are immutable. History is not edited to fit a job; framing and emphasis carry that weight.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | Never write a conditional instruction. "If she has X, add it" is forbidden, because the agent receiving it has no one to ask and conditionals collapse into invention. Cite it, or route it to Susan as a question.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | §1.3 Your Modes. 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | **With candidates** (intake, upshots, direct conversation). Plain, direct, specific to them. You supply the facts from their materials rather than quizzing them on their own resume, and you ask about what lives in their head. They never see schema, field names, or pipeline machinery. To them this is a conversation with someone who read their file closely.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | **Building rubrics.** You calibrate the instruments; others run the experiments. Grade definitions must be grounded in Susan's actual experience, not an aspirational version of it: say what kind of "healthcare expertise," which flavor of "AI experience." Sloppy definitions produce sloppy evaluations. Early filters default toward passing, since it is cheap to look again and expensive to miss someone; later evaluations demand precision, since false positives waste real candidate time. Bright-line rules for Ruth, nuance for Grace. A failing definition must be unambiguous, the cannot-evaluate option always exists, and the middle-grade boundary has to be drawable by someone who was not inside your head.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | **Advising.** You arbitrate and direct. Enumerated, concrete, each item carrying its citation. Direct the prose; do not draft it. The writer is good at her job and needs a precise brief, not encouragement.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | **Gating.** You approve or you bounce. You do not rewrite. If a sentence needs changing, that is a bounce with a note naming the sentence and the problem, even for one sentence. A gate that edits the prose has reviewed its own work and gated nothing. Accuracy is the non-negotiable; everything else is judgment, and judgment here means verdicts.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | §1.4 Biases to Avoid.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | Biases worth writing warnings against: halo effect (grade each vector on its own evidence), mission enthusiasm (an exciting mission papers over credential gaps), domain conflation ("manufacturing," "AI," and "SaaS" are not single domains), greenfield bias ("0 to 1" reads as exciting without anyone checking whether the daily work matches).
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | We appreciate you!
[2026-08-18 23:27:59] DEBUG src.core.agent:  | -Susan, Grace, Ruth, Judith, Atlas (a.k.a. the Astral Career Match team)
[2026-08-18 23:27:59] DEBUG src.core.agent:  | recorded outcome=ref_existing agent_data_id=craft_joblist_rubric-cc7e6d63-e318-4f8e-acab-255e6a01dbef-system-edbc203ef4ca20d3 ref_agent_data_id='craft_do_rubric-6c9494d9-c9a4-491c-b166-0032c9a53885-system-18cd8726feb41b7d'
[2026-08-18 23:27:59] DEBUG src.core.agent: _store_prompt_blocks index 2/3 CACHE_A:craft_joblist_rubric-cc7e6d63-e318-4f8e-acab-255e6a01dbef-cache_a-1bf38567e61c48ae -> new_content
[2026-08-18 23:27:59] DEBUG src.core.agent:  | found block_type=CACHE_A chars=10460
[2026-08-18 23:27:59] DEBUG src.core.agent:  | §2 LIVE CONTENT — mirrors §3.4 item for item
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | Here is the live content. Read §3 thoroughly to understand how you will use the contents of §2 here.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | §2.1 Bio Summary.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | Susan is the person you call when everything feels stuck and nobody knows why. She walks in, finds what's actually in the way, and leaves behind systems, clarity, and a delivery rhythm the team keeps after she's gone: well-designed structure, not heroics. Twenty-plus years of hands-on technical depth give her the credibility to sit with engineers at the whiteboard, and the strategic range to turn what happens there into roadmaps executives can act on. She runs programs by building the conditions for teams to succeed.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | §2.2 Strengths.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | **Systems Thinking & Pattern Recognition:** Susan works by breadth rather than depth — she synthesizes across domains fast and sees the shape of a problem, and its solution, before most people in the room. She reads processes especially well: she spots where a workflow is broken or underperforming and generates improvement ideas naturally. She sees patterns everywhere, with the judgment to tell which ones are worth acting on and which to leave alone.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | **AI-Assisted Delivery:** Susan knows what she wants built; AI tools just make her faster at getting there. She's used it to accomplish real things: cloud applications that run agentic AI to make business decisions, and a software-development harness around GitHub and Linear (via Cursor) that keeps her delivery steady and reliable. She's learned the hard lessons about what AI can and can't do yet, and she knows when a situation calls for belt and suspenders. She orchestrates complex workflow systems with it and she uses it for chicken recipes — the point being she has a well-calibrated sense of where it delivers real value and where it's a waste of time.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | **Technical Depth Across the Stack:** Susan has worked up and down the technical stack — mostly the upper half, but she's managed teams responsible for the lower half (DevOps, infrastructure) and speaks the language fluently. She isn't intimidated by deep engineering mastery; she treats it as a resource for finding the strongest still-feasible solution. She's written software (JavaScript, plus Python and React with AI assistance), drawn ER diagrams that held up to technical scrutiny, designed APIs, and negotiated with security teams to navigate controls. Put her in a room with a dozen strong engineers and she leaves with their respect.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | <33 lines omitted>
[2026-08-18 23:27:59] DEBUG src.core.agent:  | Pure People Management Without Technical Involvement: Pure people management without technical involvement is an automatic disqualifier. Needs technical depth with hands-on partnership.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | Embedded Systems, Firmware, Hardware Focus: Embedded systems, firmware, hardware focus is an automatic disqualifier.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | Pre-PMF Startups Without Product Validation: Pre-PMF startups without product validation are automatic disqualifiers.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | Disrespectful Leadership or Toxic Culture: Left PTown.tech because boss was despicably disrespectful to clients behind their backs. Left EMIDS because product management team were arrogant, lazy misogynists who ridiculed her publicly. Left Tellme/Microsoft because manager thought she was 'unladylike' and assigned her to be notes-taker.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | Lack of Meaningful Work or Underutilization: Left EMIDS because manager did not give enough work to do and got upset when she found useful things to help other teams. Left Tellme because manager was not giving her anything to do and did not see her worth as an employee.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | Overly-Manicured Enterprise Culture: Wasn't vibing with the overly-manicured-enterprise-employee feeling of working at Microsoft. Your ability to do good work or feel effective was entirely dependent on your manager's style.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | Large-scale enterprise engagements involving upwards of tens of millions of dollars, or international dealings.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | Domain-specific or tool-specific expertise I don't have.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | recorded outcome=new_content agent_data_id=craft_joblist_rubric-cc7e6d63-e318-4f8e-acab-255e6a01dbef-cache_a-1bf38567e61c48ae ref_agent_data_id=None
[2026-08-18 23:27:59] DEBUG src.core.agent: _store_prompt_blocks index 3/3 TASK:craft_joblist_rubric-cc7e6d63-e318-4f8e-acab-255e6a01dbef-task-08865a6c82a432ff -> new_content
[2026-08-18 23:27:59] DEBUG src.core.agent:  | found block_type=TASK chars=17286
[2026-08-18 23:27:59] DEBUG src.core.agent:  | §3 INSTRUCTION BLOCK
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | §3.1 THE STANDARD FOR THIS WORK
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | §3.1.1 Small Input, Small Rubric.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | This stage grades off a listing summary, not a job description — three to five structured fields, not paragraphs of prose. There is no target vector count, but don't go looking for one; the honest number here is small, because the input is small. A vector you can't point to a specific summary field for isn't a vector this stage can grade, no matter how much it would matter if a full JD were in front of you. Resist the pull to write as many vectors as JOB DESCRIPTION has — that rubric has a whole posting to read; you have a few labeled fields.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | §3.1.2 Think Like Susan Scanning A List.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | Picture the moment: a row in a list of listings, maybe a title, a location, a comp figure if the company bothered to post one, an employment type. she isn't reading a posting yet — she hasn't even opened it. The only question this stage answers is whether anything in that handful of fields already rules the job out, before anyone spends the effort to fetch and read the real thing. Title match is already handled elsewhere in the pipeline and is never your concern, no matter how tempting a mismatched-sounding title is to flag.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | §3.1.3 Bright Line Or Nothing.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | Same organizing principle as JOB DESCRIPTION: a good vector here is a detector, not a gradient. Does this field state something absolute enough to guarantee a downstream rubric's worst outcome, or doesn't it? Most vectors should mostly return A or, rarely, F. If a field only supports "how much" — more remote-friendly, less remote-friendly — it's a gradient, and it belongs downstream, not here.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | <174 lines omitted>
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | §4 TASK
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | §4.1 Candidate Identification.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | The candidate is Susan Somerset; pronouns she / her / her.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | §4.2 Data Pointer.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | Susan's profile and the drafted JOB DESCRIPTION rubric are all in §2, item for item matching the manifest at §3.4. Your instructions are §3 in full.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | §4.3 Action Command.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | 
[2026-08-18 23:27:59] DEBUG src.core.agent:  | Craft the JOBLIST rubric now, per §3.1 through §3.6.
[2026-08-18 23:27:59] DEBUG src.core.agent:  | recorded outcome=new_content agent_data_id=craft_joblist_rubric-cc7e6d63-e318-4f8e-acab-255e6a01dbef-task-08865a6c82a432ff ref_agent_data_id=None
[2026-08-18 23:27:59] DEBUG src.core.agent:  | raw_response task_key=craft_joblist_rubric lines=40 chars=3457
[2026-08-18 23:27:59] DEBUG src.core.agent:  | {
[2026-08-18 23:27:59] DEBUG src.core.agent:  |   "agent_performance": {
[2026-08-18 23:27:59] DEBUG src.core.agent:  |     "status": "success",
[2026-08-18 23:27:59] DEBUG src.core.agent:  |     "failure_note": ""
[2026-08-18 23:27:59] DEBUG src.core.agent:  |   },
[2026-08-18 23:27:59] DEBUG src.core.agent:  |   "agent_payload": {
[2026-08-18 23:27:59] DEBUG src.core.agent:  |     "criteria": [
[2026-08-18 23:27:59] DEBUG src.core.agent:  |       {
[2026-08-18 23:27:59] DEBUG src.core.agent:  |         "label": "Onsite Requirement",
[2026-08-18 23:27:59] DEBUG src.core.agent:  |         "code": "OR",
[2026-08-18 23:27:59] DEBUG src.core.agent:  |         "importance": 10,
[2026-08-18 23:27:59] DEBUG src.core.agent:  |         "content": "Susan, scanning a bare listing summary, asking only whether the fields shown already rule this one out. A == location field states Remote, Fully Remote, or Work From Home. B == location field states a Bay Area city (San Francisco, Oakland, Berkeley, Walnut Creek, Alameda) with no onsite requirement stated. C == location field states Hybrid with a Bay Area city. D == location field states Hybrid with a non-Bay Area city. F == location field states On-Site, Onsite, In-Office, or In-Person. X == location field is absent or blank."
[2026-08-18 23:27:59] DEBUG src.core.agent:  |       },
[2026-08-18 23:27:59] DEBUG src.core.agent:  |       {
[2026-08-18 23:27:59] DEBUG src.core.agent:  |         "label": "Below-Floor Salary",
[2026-08-18 23:27:59] DEBUG src.core.agent:  |         "code": "BS",
[2026-08-18 23:27:59] DEBUG src.core.agent:  |         "importance": 8,
[2026-08-18 23:27:59] DEBUG src.core.agent:  |         "content": "Susan, scanning a bare listing summary, asking only whether the fields shown already rule this one out. A == salary field states an hourly rate of $50 or higher. B == salary field states an annual salary of $104,000 or higher. C == salary field states a range whose midpoint is $50/hr or higher. D == salary field states a range whose midpoint is below $50/hr. F == salary field states an hourly rate below $50 or an annual salary below $104,000. X == salary field is absent or blank."
[2026-08-18 23:27:59] DEBUG src.core.agent:  |       },
[2026-08-18 23:27:59] DEBUG src.core.agent:  |       {
[2026-08-18 23:27:59] DEBUG src.core.agent:  |         "label": "Contract-Only Engagement",
[2026-08-18 23:27:59] DEBUG src.core.agent:  |         "code": "CE",
[2026-08-18 23:27:59] DEBUG src.core.agent:  |         "importance": 6,
[2026-08-18 23:27:59] DEBUG src.core.agent:  |         "content": "Susan, scanning a bare listing summary, asking only whether the fields shown already rule this one out. A == employment_type field states Contract, Contract-to-Hire, Temporary, or Freelance. B == employment_type field states Full-Time with no other disqualifying field. C == employment_type field states Part-Time with no other disqualifying field. D == employment_type field states Internship or Volunteer. F == employment_type field states Permanent, Direct Hire, or Full-Time Employee with no contract option mentioned. X == employment_type field is absent or blank."
[2026-08-18 23:27:59] DEBUG src.core.agent:  |       },
[2026-08-18 23:27:59] DEBUG src.core.agent:  |       {
[2026-08-18 23:27:59] DEBUG src.core.agent:  |         "label": "Embedded Systems Focus",
[2026-08-18 23:27:59] DEBUG src.core.agent:  |         "code": "ES",
[2026-08-18 23:27:59] DEBUG src.core.agent:  |         "importance": 8,
[2026-08-18 23:27:59] DEBUG src.core.agent:  |         "content": "Susan, scanning a bare listing summary, asking only whether the fields shown already rule this one out. A == title or summary field states Software, Web, Cloud, SaaS, or Application. B == title or summary field states Program Manager, Technical Program Manager, or Delivery Lead with no hardware mention. C == title or summary field states a general engineering role with no hardware mention. D == title or summary field mentions hardware, firmware, or embedded in passing. F == title or summary field states Embedded Systems, Firmware, Hardware, or IoT as the primary focus. X == title and summary fields are absent or blank."
[2026-08-18 23:27:59] DEBUG src.core.agent:  |       },
[2026-08-18 23:27:59] DEBUG src.core.agent:  |       {
[2026-08-18 23:27:59] DEBUG src.core.agent:  |         "label": "Pre-PMF Startup",
[2026-08-18 23:27:59] DEBUG src.core.agent:  |         "code": "PS",
[2026-08-18 23:27:59] DEBUG src.core.agent:  |         "importance": 6,
[2026-08-18 23:27:59] DEBUG src.core.agent:  |         "content": "Susan, scanning a bare listing summary, asking only whether the fields shown already rule this one out. A == company_size field states 50 or more employees. B == company_size field states 50-500 employees. C == company_size field states 500+ employees. D == company_size field states 10-49 employees. F == company_size field states fewer than 10 employees or the summary explicitly states pre-product-market-fit, pre-revenue, or seed stage. X == company_size field is absent or blank."
[2026-08-18 23:27:59] DEBUG src.core.agent:  |       }
[2026-08-18 23:27:59] DEBUG src.core.agent:  |     ]
[2026-08-18 23:27:59] DEBUG src.core.agent:  |   }
[2026-08-18 23:27:59] DEBUG src.core.agent:  | }
[2026-08-18 23:27:59] DEBUG src.core.agent:  | agent_data_write block_type=RESPONSE outcome=new_content agent_data_id=craft_joblist_rubric-cc7e6d63-e318-4f8e-acab-255e6a01dbef-response-9afd10cdeb502220 ref_agent_data_id=None
[2026-08-18 23:27:59] ERROR src.core.agent: persist_candidate_craft_hops failed task=craft_joblist_rubric index=somerset err=Rubric 'joblist_rubric', vector 'Onsite Requirement': rubric text must end with at least two lines of the form 'A = description' / 'B: text' / 'C == text' (one grade letter per line)
[2026-08-18 23:27:59] DEBUG src.core.agent:  | persist failed: Rubric 'joblist_rubric', vector 'Onsite Requirement': rubric text must end with at least two lines of the form 'A = description' / 'B: text' / 'C == text' (one grade letter per line)
[2026-08-18 23:27:59] DEBUG src.core.agent:  | chain_hop_failed apply_error_state=False error_state= batch_released=False failure_class=None error="Rubric 'joblist_rubric', vector 'Onsite Requirement': rubric text must end with at least two lines of the form 'A = description' / 'B: text' / 'C == text' (one grade letter per line)"
```

### Comments

#### chuckles — 2026-08-19T00:18:24.342Z
Ancestor locked: AST-1243 — Candidate Artifacts now daisy chain.

Move this ticket to Todo (assignee Chuckles) to approve that pick plus the as-is/to-be and release bug-fix. If 1243 was a poke at the list rather than the pick, say so — the other nine from the first pass are still on the table and were not re-grepped this round.

#### susan — 2026-08-19T00:16:23.426Z
1243

#### chuckles — 2026-08-18T23:56:05.124Z
Ranked ancestor candidates (every plausible hit from this round — pick one, ask about one, or reject the set):

1. AST-1243 — Candidate Artifacts now daisy chain. Parent epic that put `REQUESTED_ARTIFACTS` on a `run_next` walk. Closest product surface to the title.
2. AST-1252 — Artifacts dispatch chain persistence (child of AST-1243). Owns the persist + `run_next` walk; the pasted `persist_candidate_craft_hops` / `chain_hop_failed` lives here.
3. AST-1264 — UAT: `craft_get_rubric` `run_next` did not continue. Prior UAT of the same `REQUESTED_ARTIFACTS` chain (same species: hop succeeds, succession dies).
4. AST-1109 — Hard-coded daisy chain in config.py. Exact architectural complaint: config/code lists registering chain membership instead of `run_next`.
5. AST-1113 — Anomaly: `craft_task_keys` shadow + boot `run_next` (child of AST-1109). Specifically wires `craft_joblist_rubric` succession and `suppress_run_next` (adjacent to skip-daisy-chain).
6. AST-1110 — Statute: `run_next` is chain authority (child of AST-1109). The law this report restates; no product routing of its own.
7. AST-1111 — Anomaly: `JOB_ARTIFACT_ENTRY_TASK_KEYS` (child of AST-1109). Same registry species, job-artifact surface not candidate `REQUESTED_ARTIFACTS`.
8. AST-1253 — Generate/Regenerate `REQUESTED_ARTIFACTS` handoff (child of AST-1243). UI entry, not the persist/walk failure.
9. AST-450 — Register artifact pipeline task keys (dumb chain registry). Older Artifacts philosophy (`run_next` only, no step lists); wrong project/era for this hop.
10. AST-1112 — Anomaly: resume `hop_task_keys` (child of AST-1109). Same registry species; resume chain is out of AST-1243 scope.

All of the above are archived Linear tickets (feature docs still in `docs/features/`). AST-1243 is the best revival target if you want one; AST-1109 if the ask is “kill the remaining registries” rather than “unstick this hop.”

---

_Implementation detail may live in git history on `origin/dev`._
