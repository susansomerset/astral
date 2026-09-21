# AST-1283 — Grade_do is erroring

<!-- linear-archive: AST-1283 archived 2026-08-17 -->

## Linear archive (AST-1283)

**Archived:** 2026-08-17  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-1283/grade-do-is-erroring  
**Status at archive:** Archive  
**Project:** Astral Consult  
**Assignee:** susan  
**Priority / estimate:** Urgent / —  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

## Purpose

Staging meteorite Do grading is burning LLM calls and then failing the whole batch: encoded grades decode, but grade-reason hydration aborts because the candidate’s Do rubric criteria resolve empty (`owner=grade_do`, `criteria_codes=[]`). Jobs that already cleared meteorite JD never get a scored Do pass/fail. Restore Do grading so a populated Do rubric hydrates and scores; fail closed and visibly when Do criteria are truly missing.

## Functional scope

1. **Do rubric criteria resolve for meteorite Do (and standard Do)** — For `meteorite_grade_do` / `grade_do`, the same table-backed Do rubric used for vectors and feedback must be non-empty at hydrate/score time when the candidate has Do criteria. The staging failure mode (`grade reason hydration failed: rubric criteria missing or empty` plus `empty_expected_codes` with empty `criteria_codes` / `uuid_codes`) must not occur for a candidate whose Do rubric is populated.
2. **Empty Do rubric fails closed** — If Do criteria are genuinely missing, the batch must not look like a successful Do completion. Jobs land on the configured error/retry path for that hop; operators see a clear missing-rubric outcome (not a silent “COMPLETED with errors” after a full model round-trip that cannot be applied).
3. **Debug visibility on the empty-criteria path** — With `debug=True`, log candidate, owner task, rubric artifact, and criteria/uuid code sets (found vs recorded) at the point of failure under the AST-538 Style D / `|` detail contract.
4. **Staging UAT for somerset** — Re-run meteorite Do on staging for somerset after the fix: jobs move to scored Do pass/fail (or honest missing-rubric failure if criteria are still absent), not wholesale hydration errors after a successful decode.

## Architectural definition

* **Patterns to reuse**
  * `pattern.batch.entity-claim-process-release` — missing/empty rubric is a process failure inside claim → process → release; release still clears the batch.
  * `pattern.state.entity-state-transitions` — error/retry destinations stay on registered job states via core/config, not ad-hoc dispatcher writes.
  * `pattern.config.config-block` — `rubric_artifact` / owner mapping for `do_rubric` → `grade_do` (including meteorite twin consumers) stays config-driven.
* **New patterns proposed** — none.
* **Applicable statutes**
  * `astral.patterns.render-verdict-orchestrates-consult` (idiom successor) — hydrate/score/apply stay on the consult verdict path.
  * `astral.state.core-decides-transitions` — missing-rubric vs scored outcomes chosen in core.
  * `astral.agent.grade-vector-validation` — vector set only meaningful when live Do criteria exist.
  * `astral.standards.debug-contract-gated` — empty-criteria detail only when `debug=True`.
  * `astral.batch.claim-process-release` — batch claim/clear honesty on failure.
  * `universal` product-code set — DRY criteria load shared by hydrate, score, and feedback; no meteorite-only fork that skips Do rubric.

## Boundaries

* Does **not** redesign Do rubric content, craft prompts, or importance weights.
* Does **not** reopen AST-1150 incompleteness→retry policy (missing **vectors** in a decoded line); this ticket is empty **criteria** at hydrate time.
* Does **not** change `_render_score` math or score_floor semantics (adjacent: AST-1277 on Foundation).
* Does **not** own Get/Like rubric emptiness unless the same Do-owner lookup bug is proven shared — default scope is Do / `do_rubric` / `grade_do`.
* Does **not** treat a deliberate empty Do rubric as a scored pass.

## Acceptance criteria

1. On staging (or equivalent) for a candidate with a populated Do rubric, a `meteorite_grade_do` batch that returns a complete encoded grade set hydrates reasons and produces per-job scored Do pass/fail transitions — zero `grade reason hydration failed: rubric criteria missing or empty` for that run.
2. For a candidate with no current Do rubric criteria, the Do batch does not report a successful apply; every claimed job ends on the configured error/retry destination for that hop, and debug logs show empty criteria/uuid codes with candidate + owner + artifact.
3. Vector-feedback capture for owner `grade_do` no longer skips solely because `criteria_codes=[]` / `uuid_codes=[]` when the Do rubric is populated for that candidate.
4. Standard `grade_do` (non-meteorite) still hydrates from the same `do_rubric` / `grade_do` owner when criteria exist — no twin-only regression.

## Dependencies and blockers

* Adjacent shipped context (not blockers): AST-1222 / AST-1221 (meteorite Do alias), AST-1150 family (incomplete grade sets → retry).
* Do not overlap AST-1277 (score_floor / pass_threshold) beyond shared consult apply entry points.

## Open questions

1. On staging Artifacts for **somerset** → Do job criteria: are criteria rows visible and non-empty, or is that page empty? (Populated UI ⇒ lookup/resolution bug; empty UI ⇒ craft/save/persistence also in scope, or staging data repair plus prevent recurrence.)

## Proposed child tickets

#### 1!: **Restore Do rubric criteria for meteorite/standard Do apply - Ada**

Find and fix why `owner=grade_do` / `do_rubric` resolves empty for somerset while encoded Do grades still decode; `meteorite_grade_do` and `grade_do` must load the same current criteria for hydrate, score, and feedback when Do criteria exist. Does **not** own empty-rubric operator messaging beyond making load correct.
**Citations:** `pattern.config.config-block`, `astral.patterns.render-verdict-orchestrates-consult`, `astral.agent.grade-vector-validation`

#### 2: **Empty Do rubric fail-closed + debug - Hedy**

After #1: when Do criteria are truly missing, fail closed on the consult apply path (configured error/retry for the hop); with `debug=True`, Style D index + `|` detail for candidate/owner/artifact/code sets. Does **not** own criteria persistence/craft.
**Citations:** `pattern.batch.entity-claim-process-release`, `pattern.state.entity-state-transitions`, `astral.state.core-decides-transitions`, `astral.standards.debug-contract-gated`

---

## Original brief

```
<div><br></div><div><br><div class="gmail_quote gmail_quote_container"><div dir="ltr" class="gmail_attr">---------- Forwarded message ---------<br>From: <span dir="auto">&lt;<a href="mailto:astral.career.match@gmail.com">astral.career.match@gmail.com</a>&gt;</span><br>Date: Sat, Aug 8, 2026 at 11:52 AM<br>Subject: [staging/Somerset] meteorite_grade_do COMPLETED: 6 error(s) / 6 processed | meteorite_grade_do-67f0a259-06dd-4a71-9e3a-f69cdc132da5<br>To:  &lt;<a href="mailto:susan%2Bastral@susansomerset.com">susan+astral@susansomerset.com</a>&gt;<br></div><br><br>2026-08-08 18:52:11  [WARNING]<br>
[meteorite_grade_do/meteorite_grade_do-67f0a259-06dd-4a71-9e3a-f69cdc132da5]<br>
batch finished COMPLETED with errors — processed=6 passed=0 failed=0<br>
errors=6<br>
2026-08-08 18:52:11  [DEBUG]   | loop stop: max_runs reached<br>
max_runs=1 run_count=1<br>
2026-08-08 18:52:11  [DEBUG]   | iteration 1 summary processed=6<br>
passed=0 failed=0 errors=6 accumulated={&#39;total_processed&#39;: 6,<br>
&#39;total_passed&#39;: 0, &#39;total_failed&#39;: 0, &#39;total_errors&#39;: 6}<br>
2026-08-08 18:52:11  [DEBUG]   | runner returned<br>
summary={&#39;total_processed&#39;: 6, &#39;total_passed&#39;: 0, &#39;total_failed&#39;: 0,<br>
&#39;total_errors&#39;: 6}<br>
2026-08-08 18:52:11  [DEBUG]   | batch end summary={&#39;total_processed&#39;:<br>
6, &#39;total_passed&#39;: 0, &#39;total_failed&#39;: 0, &#39;total_errors&#39;: 6}<br>
2026-08-08 18:52:11  [ERROR]  [meteorite_grade_do] grade reason<br>
hydration failed: rubric criteria missing or empty; cannot hydrate<br>
grade reasons<br>
2026-08-08 18:52:11  [DEBUG]   | task_key=meteorite_grade_do<br>
batch_id=meteorite_grade_do-67f0a259-06dd-4a71-9e3a-f69cdc132da5<br>
success=True<br>
2026-08-08 18:52:11  [DEBUG]  do_task index 1/1<br>
meteorite_grade_do_batch_meteorite_grade_do-67f0a259-06dd-4a71-9e3a-f69cdc132da5<br>
-&gt; completed<br>
2026-08-08 18:52:11  [INFO]  do_task(meteorite_grade_do) completed<br>
successfully batch_id=meteorite_grade_do-67f0a259-06dd-4a71-9e3a-f69cdc132da5<br>
index=meteorite_grade_do_batch_meteorite_grade_do-67f0a259-06dd-4a71-9e3a-f69cdc132da5<br>
2026-08-08 18:52:11  [DEBUG]   | agent_data_write block_type=RESPONSE<br>
outcome=new_content<br>
agent_data_id=meteorite_grade_do-67f0a259-06dd-4a71-9e3a-f69cdc132da5-response-ab03a1f697afdbf6<br>
ref_agent_data_id=None<br>
2026-08-08 18:52:11  [DEBUG]   | skip reason=empty_expected_codes<br>
candidate=somerset owner=grade_do criteria_codes=[] uuid_codes=[]<br>
2026-08-08 18:52:11  [DEBUG]  _capture_rubric_vector_feedback index<br>
1/1 meteorite_grade_do -&gt; vector feedback capture skipped<br>
2026-08-08 18:52:11  [DEBUG]  [ ~ ] [meteorite_grade_do] decode line<br>
pos=5 astral_job_id=fcbed3d5-5efb-4bfc-b30e-51f116d178f9<br>
segments=[&#39;ERB4&#39;, &#39;MEB4&#39;, &#39;PGA4&#39;, &#39;WAB4&#39;, &#39;MWB4&#39;, &#39;KOB4&#39;, &#39;QCB4&#39;] -&gt;<br>
[{&#39;vector&#39;: &#39;ER&#39;, &#39;grade&#39;: &#39;B&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;ME&#39;,<br>
&#39;grade&#39;: &#39;B&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;PG&#39;, &#39;grade&#39;: &#39;A&#39;,<br>
&#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;WA&#39;, &#39;grade&#39;: &#39;B&#39;, &#39;confidence&#39;: 4},<br>
{&#39;vector&#39;: &#39;MW&#39;, &#39;grade&#39;: &#39;B&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;KO&#39;,<br>
&#39;grade&#39;: &#39;B&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;QC&#39;, &#39;grade&#39;: &#39;B&#39;,<br>
&#39;confidence&#39;: 4}]<br>
2026-08-08 18:52:11  [DEBUG]  [ ~ ] [meteorite_grade_do] decode line<br>
pos=4 astral_job_id=01523c41-f156-49d6-98ff-2e80f4d7c5fc<br>
segments=[&#39;ERD4&#39;, &#39;MED4&#39;, &#39;PGD4&#39;, &#39;WAD4&#39;, &#39;MWD4&#39;, &#39;KOD4&#39;, &#39;QCD4&#39;] -&gt;<br>
[{&#39;vector&#39;: &#39;ER&#39;, &#39;grade&#39;: &#39;D&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;ME&#39;,<br>
&#39;grade&#39;: &#39;D&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;PG&#39;, &#39;grade&#39;: &#39;D&#39;,<br>
&#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;WA&#39;, &#39;grade&#39;: &#39;D&#39;, &#39;confidence&#39;: 4},<br>
{&#39;vector&#39;: &#39;MW&#39;, &#39;grade&#39;: &#39;D&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;KO&#39;,<br>
&#39;grade&#39;: &#39;D&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;QC&#39;, &#39;grade&#39;: &#39;D&#39;,<br>
&#39;confidence&#39;: 4}]<br>
2026-08-08 18:52:11  [DEBUG]  [ ~ ] [meteorite_grade_do] decode line<br>
pos=3 astral_job_id=38028a31-aed3-406a-9490-264ed217a9dc<br>
segments=[&#39;ERB4&#39;, &#39;MEB4&#39;, &#39;PGA4&#39;, &#39;WAB4&#39;, &#39;MWB4&#39;, &#39;KOB4&#39;, &#39;QCB4&#39;] -&gt;<br>
[{&#39;vector&#39;: &#39;ER&#39;, &#39;grade&#39;: &#39;B&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;ME&#39;,<br>
&#39;grade&#39;: &#39;B&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;PG&#39;, &#39;grade&#39;: &#39;A&#39;,<br>
&#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;WA&#39;, &#39;grade&#39;: &#39;B&#39;, &#39;confidence&#39;: 4},<br>
{&#39;vector&#39;: &#39;MW&#39;, &#39;grade&#39;: &#39;B&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;KO&#39;,<br>
&#39;grade&#39;: &#39;B&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;QC&#39;, &#39;grade&#39;: &#39;B&#39;,<br>
&#39;confidence&#39;: 4}]<br>
2026-08-08 18:52:11  [DEBUG]  [ ~ ] [meteorite_grade_do] decode line<br>
pos=2 astral_job_id=238dab27-7c06-44d3-ac14-9ed95a003387<br>
segments=[&#39;ERB4&#39;, &#39;MEB4&#39;, &#39;PGA4&#39;, &#39;WAB4&#39;, &#39;MWB4&#39;, &#39;KOB4&#39;, &#39;QCB4&#39;] -&gt;<br>
[{&#39;vector&#39;: &#39;ER&#39;, &#39;grade&#39;: &#39;B&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;ME&#39;,<br>
&#39;grade&#39;: &#39;B&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;PG&#39;, &#39;grade&#39;: &#39;A&#39;,<br>
&#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;WA&#39;, &#39;grade&#39;: &#39;B&#39;, &#39;confidence&#39;: 4},<br>
{&#39;vector&#39;: &#39;MW&#39;, &#39;grade&#39;: &#39;B&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;KO&#39;,<br>
&#39;grade&#39;: &#39;B&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;QC&#39;, &#39;grade&#39;: &#39;B&#39;,<br>
&#39;confidence&#39;: 4}]<br>
2026-08-08 18:52:11  [DEBUG]  [ ~ ] [meteorite_grade_do] decode line<br>
pos=1 astral_job_id=9d7ca0b9-b027-4782-a55c-c9264285e6fc<br>
segments=[&#39;ERB4&#39;, &#39;MEB4&#39;, &#39;PGA4&#39;, &#39;WAB4&#39;, &#39;MWB4&#39;, &#39;KOB4&#39;, &#39;QCB4&#39;] -&gt;<br>
[{&#39;vector&#39;: &#39;ER&#39;, &#39;grade&#39;: &#39;B&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;ME&#39;,<br>
&#39;grade&#39;: &#39;B&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;PG&#39;, &#39;grade&#39;: &#39;A&#39;,<br>
&#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;WA&#39;, &#39;grade&#39;: &#39;B&#39;, &#39;confidence&#39;: 4},<br>
{&#39;vector&#39;: &#39;MW&#39;, &#39;grade&#39;: &#39;B&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;KO&#39;,<br>
&#39;grade&#39;: &#39;B&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;QC&#39;, &#39;grade&#39;: &#39;B&#39;,<br>
&#39;confidence&#39;: 4}]<br>
2026-08-08 18:52:11  [DEBUG]  [ ~ ] [meteorite_grade_do] decode line<br>
pos=0 astral_job_id=c7471b55-dc71-4301-b593-04a687ee91d4<br>
segments=[&#39;ERD4&#39;, &#39;MED4&#39;, &#39;PGD4&#39;, &#39;WAD4&#39;, &#39;MWD4&#39;, &#39;KOD4&#39;, &#39;QCD4&#39;] -&gt;<br>
[{&#39;vector&#39;: &#39;ER&#39;, &#39;grade&#39;: &#39;D&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;ME&#39;,<br>
&#39;grade&#39;: &#39;D&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;PG&#39;, &#39;grade&#39;: &#39;D&#39;,<br>
&#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;WA&#39;, &#39;grade&#39;: &#39;D&#39;, &#39;confidence&#39;: 4},<br>
{&#39;vector&#39;: &#39;MW&#39;, &#39;grade&#39;: &#39;D&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;KO&#39;,<br>
&#39;grade&#39;: &#39;D&#39;, &#39;confidence&#39;: 4}, {&#39;vector&#39;: &#39;QC&#39;, &#39;grade&#39;: &#39;D&#39;,<br>
&#39;confidence&#39;: 4}]<br>
2026-08-08 18:52:11  [DEBUG]   |<br>
005|ERB4|MEB4|PGA4|WAB4|MWB4|KOB4|QCB4|Rate not listed<br>
2026-08-08 18:52:11  [DEBUG]   |<br>
004|ERD4|MED4|PGD4|WAD4|MWD4|KOD4|QCD4|Technical Architect role, not<br>
TPM<br>
2026-08-08 18:52:11  [DEBUG]   |<br>
003|ERB4|MEB4|PGA4|WAB4|MWB4|KOB4|QCB4|Rate not listed<br>
2026-08-08 18:52:11  [DEBUG]   |<br>
002|ERB4|MEB4|PGA4|WAB4|MWB4|KOB4|QCB4|Rate $60-65/hr meets floor<br>
2026-08-08 18:52:11  [DEBUG]   |<br>
001|ERB4|MEB4|PGA4|WAB4|MWB4|KOB4|QCB4|Rate $65-70/hr meets floor<br>
2026-08-08 18:52:11  [DEBUG]   |<br>
000|ERD4|MED4|PGD4|WAD4|MWD4|KOD4|QCD4|Rate $35-45/hr below $50 floor<br>
2026-08-08 18:52:11  [DEBUG]   | encoded_payload<br>
task_key=meteorite_grade_do lines=6 chars=384<br>
2026-08-08 18:52:11  [DEBUG]   | }<br>
2026-08-08 18:52:11  [DEBUG]   |   &quot;agent_payload&quot;:<br>
&quot;000|ERD4|MED4|PGD4|WAD4|MWD4|KOD4|QCD4|Rate $35-45/hr below $50<br>
floor\n001|ERB4|MEB4|PGA4|WAB4|MWB4|KOB4|QCB4|Rate $65-70/hr meets<br>
floor\n002|ERB4|MEB4|PGA4|WAB4|MWB4|KOB4|QCB4|Rate $60-65/hr meets<br>
floor\n003|ERB4|MEB4|PGA4|WAB4|MWB4|KOB4|QCB4|Rate not<br>
listed\n004|ERD4|MED4|PGD4|WAD4|MWD4|KOD4|QCD4|Technical Architect<br>
role, not TPM\n005|ERB4|MEB4|PGA4|WAB4|MWB4|KOB4|QCB4|Rate not listed&quot;<br>
2026-08-08 18:52:11  [DEBUG]   |   },<br>
2026-08-08 18:52:11  [DEBUG]   |     ]<br>
2026-08-08 18:52:11  [DEBUG]   |       &quot;QCRROVK&quot;<br>
2026-08-08 18:52:11  [DEBUG]   |       &quot;KORAOVK&quot;,<br>
2026-08-08 18:52:11  [DEBUG]   |       &quot;MWRAOVK&quot;,<br>
2026-08-08 18:52:11  [DEBUG]   |       &quot;WARAOVK&quot;,<br>
2026-08-08 18:52:11  [DEBUG]   |       &quot;PGRAOVK&quot;,<br>
2026-08-08 18:52:11  [DEBUG]   |       &quot;MERAOVK&quot;,<br>
2026-08-08 18:52:11  [DEBUG]   |       &quot;ERRAOVK&quot;,<br>
2026-08-08 18:52:11  [DEBUG]   |     &quot;vector_reviews&quot;: [<br>
2026-08-08 18:52:11  [DEBUG]   |     &quot;status&quot;: &quot;success&quot;,<br>
2026-08-08 18:52:11  [DEBUG]   |   &quot;agent_performance&quot;: {<br>
2026-08-08 18:52:11  [DEBUG]   | {<br>
2026-08-08 18:52:11  [DEBUG]   | raw_response<br>
task_key=meteorite_grade_do lines=15 chars=617<br>
2026-08-08 18:52:11  [DEBUG]   | agent_data_write block_type=TASK<br>
outcome=ref_existing<br>
agent_data_id=meteorite_grade_do-67f0a259-06dd-4a71-9e3a-f69cdc132da5-task-63c1aa28695b2c5c<br>
ref_agent_data_id=&#39;meteorite_grade_do-3491069e-656a-465f-990c-dba4c91127c6-task-d340450ebd34cf92&#39;<br>
2026-08-08 18:52:11  [DEBUG]   | agent_data_write block_type=NO_CACHE<br>
outcome=new_content<br>
agent_data_id=meteorite_grade_do-67f0a259-06dd-4a71-9e3a-f69cdc132da5-no_cache-20d0cbaa305047f6<br>
ref_agent_data_id=None<br>
2026-08-08 18:52:11  [DEBUG]   | agent_data_write block_type=CACHE_A<br>
outcome=ref_existing<br>
agent_data_id=meteorite_grade_do-67f0a259-06dd-4a71-9e3a-f69cdc132da5-cache_a-4b11024605cdc079<br>
ref_agent_data_id=&#39;meteorite_grade_do-3491069e-656a-465f-990c-dba4c91127c6-cache_a-dc95aa4ec675cc4c&#39;<br>
2026-08-08 18:52:11  [DEBUG]   | agent_data_write block_type=SYSTEM<br>
outcome=ref_existing<br>
agent_data_id=meteorite_grade_do-67f0a259-06dd-4a71-9e3a-f69cdc132da5-system-858a45b71f13f345<br>
ref_agent_data_id=&#39;evaluate_meteorite-6debb71e-68b7-47ad-89a6-6e0e8a3d50e9-system-5e36a161dcd9ac2f&#39;<br>
2026-08-08 18:52:11  [DEBUG]   | }<br>
2026-08-08 18:52:11  [DEBUG]   |   &quot;agent_payload&quot;:<br>
&quot;000|ERD4|MED4|PGD4|WAD4|MWD4|KOD4|QCD4|Rate $35-45/hr below $50<br>
floor\n001|ERB4|MEB4|PGA4|WAB4|MWB4|KOB4|QCB4|Rate $65-70/hr meets<br>
floor\n002|ERB4|MEB4|PGA4|WAB4|MWB4|KOB4|QCB4|Rate $60-65/hr meets<br>
floor\n003|ERB4|MEB4|PGA4|WAB4|MWB4|KOB4|QCB4|Rate not<br>
listed\n004|ERD4|MED4|PGD4|WAD4|MWD4|KOD4|QCD4|Technical Architect<br>
role, not TPM\n005|ERB4|MEB4|PGA4|WAB4|MWB4|KOB4|QCB4|Rate not listed&quot;<br>
2026-08-08 18:52:11  [DEBUG]   |   },<br>
2026-08-08 18:52:11  [DEBUG]   |     ]<br>
2026-08-08 18:52:11  [DEBUG]   |       &quot;QCRROVK&quot;<br>
2026-08-08 18:52:11  [DEBUG]   |       &quot;KORAOVK&quot;,<br>
2026-08-08 18:52:11  [DEBUG]   |       &quot;MWRAOVK&quot;,<br>
2026-08-08 18:52:11  [DEBUG]   |       &quot;WARAOVK&quot;,<br>
2026-08-08 18:52:11  [DEBUG]   |       &quot;PGRAOVK&quot;,<br>
2026-08-08 18:52:11  [DEBUG]   |       &quot;MERAOVK&quot;,<br>
2026-08-08 18:52:11  [DEBUG]   |       &quot;ERRAOVK&quot;,<br>
2026-08-08 18:52:11  [DEBUG]   |     &quot;vector_reviews&quot;: [<br>
2026-08-08 18:52:11  [DEBUG]   |     &quot;status&quot;: &quot;success&quot;,<br>
2026-08-08 18:52:11  [DEBUG]   |   &quot;agent_performance&quot;: {<br>
2026-08-08 18:52:11  [DEBUG]   | {<br>
2026-08-08 18:52:11  [DEBUG]   | response_preview:<br>
2026-08-08 18:52:11  [DEBUG]   | vendor=deepseek-v4-pro tokens<br>
fresh=8615 cache_read=5248 cache_write=0 output=307<br>
2026-08-08 18:52:11  [DEBUG]   | provider=deepseek<br>
model=deepseek-v4-pro task=meteorite_grade_do duration=6.3s<br>
stop_reason=end_turn<br>
2026-08-08 18:52:11  [DEBUG]  send_to_deepseek index 1/1<br>
meteorite_grade_do -&gt; success<br>
2026-08-08 18:52:11  [INFO]  LLM deepseek task=meteorite_grade_do 6.3s<br>
stop=end_turn tokens in=8615 out=307<br>
2026-08-08 18:52:11  [DEBUG]   | blocks system=2 user=2<br>
runtime_prompt_segments=4<br>
2026-08-08 18:52:11  [DEBUG]   | llm_params provider=deepseek<br>
brain_setting=Medium model=deepseek-v4-pro max_tokens=16000 temp=0.3<br>
skip_cache=False candidate_id=somerset<br>
2026-08-08 18:52:11  [INFO]  [DEBUG] do_task(&#39;meteorite_grade_do&#39;):<br>
brain_setting=Medium provider=deepseek model=deepseek-v4-pro<br>
max_tokens=16000 temp=0.3 skip_cache=False candidate=somerset<br>
2026-08-08 18:52:11  [DEBUG]   | recorded FIRST_NAME=&#39;Susan&#39;<br>
LAST_NAME=&#39;Somerset&#39; FULL_NAME=&#39;Susan Somerset&#39;<br>
2026-08-08 18:52:11  [DEBUG]   | found first=nonempty last=nonempty<br>
full=nonempty branch=load_by_id<br>
2026-08-08 18:52:11  [DEBUG]  do_task.candidate_token_view index 1/1<br>
somerset -&gt; success — name tokens<br>
2026-08-08 18:52:11  [DEBUG]   | task_key=meteorite_grade_do<br>
batch_id=meteorite_grade_do-67f0a259-06dd-4a71-9e3a-f69cdc132da5<br>
index=meteorite_grade_do_batch_meteorite_grade_do-67f0a259-06dd-4a71-9e3a-f69cdc132da5<br>
in_run_next_chain=False<br>
2026-08-08 18:52:11  [DEBUG]  do_task index 1/1<br>
meteorite_grade_do_batch_meteorite_grade_do-67f0a259-06dd-4a71-9e3a-f69cdc132da5<br>
-&gt; task start<br>
2026-08-08 18:52:11  [INFO]  run_next chain entry:<br>
task=meteorite_grade_do<br>
batch_id=meteorite_grade_do-67f0a259-06dd-4a71-9e3a-f69cdc132da5<br>
2026-08-08 18:52:11  [DEBUG]   | alias=meteorite_grade_do<br>
content_master=grade_do orchestration=TASK_CONFIG[meteorite_grade_do]<br>
prompts=agent_task[grade_do]<br>
2026-08-08 18:52:11  [DEBUG]  do_task(meteorite_grade_do) index 1/1<br>
meteorite_grade_do_batch_meteorite_grade_do-67f0a259-06dd-4a71-9e3a-f69cdc132da5<br>
-&gt; alias_resolve<br>
2026-08-08 18:52:11  [DEBUG]   |<br>
batch_id=meteorite_grade_do-67f0a259-06dd-4a71-9e3a-f69cdc132da5<br>
batch_states=[&#39;METEORITE_PASSED_JD_RETRY&#39;] batch_chunk_index=None<br>
astral_ids=[&#39;c7471b55-dc71-4301-b593-04a687ee91d4&#39;,<br>
&#39;9d7ca0b9-b027-4782-a55c-c9264285e6fc&#39;,<br>
&#39;238dab27-7c06-44d3-ac14-9ed95a003387&#39;,<br>
&#39;38028a31-aed3-406a-9490-264ed217a9dc&#39;,<br>
&#39;01523c41-f156-49d6-98ff-2e80f4d7c5fc&#39;,<br>
&#39;fcbed3d5-5efb-4bfc-b30e-51f116d178f9&#39;]<br>
2026-08-08 18:52:11  [DEBUG]<br>
consult._run_batch_consult(meteorite_grade_do) index 1/1<br>
meteorite_grade_do -&gt; batch start n=6<br>
2026-08-08 18:52:11  [DEBUG]   | meteorite_grade_do<br>
batch_id=meteorite_grade_do-67f0a259-06dd-4a71-9e3a-f69cdc132da5<br>
claimed=6 agent_task=meteorite_grade_do<br>
2026-08-08 18:52:11  [DEBUG]   | entity_type=job<br>
trigger_state=METEORITE_PASSED_JD state=&#39;METEORITE_PASSED_JD_RETRY&#39;<br>
2026-08-08 18:52:11  [DEBUG]  dispatcher._run_unified index 6/6<br>
fcbed3d5-5efb-4bfc-b30e-51f116d178f9 -&gt; claimed<br>
2026-08-08 18:52:11  [DEBUG]   | entity_type=job<br>
trigger_state=METEORITE_PASSED_JD state=&#39;METEORITE_PASSED_JD_RETRY&#39;<br>
2026-08-08 18:52:11  [DEBUG]  dispatcher._run_unified index 5/6<br>
01523c41-f156-49d6-98ff-2e80f4d7c5fc -&gt; claimed<br>
2026-08-08 18:52:11  [DEBUG]   | entity_type=job<br>
trigger_state=METEORITE_PASSED_JD state=&#39;METEORITE_PASSED_JD_RETRY&#39;<br>
2026-08-08 18:52:11  [DEBUG]  dispatcher._run_unified index 4/6<br>
38028a31-aed3-406a-9490-264ed217a9dc -&gt; claimed<br>
2026-08-08 18:52:11  [DEBUG]   | entity_type=job<br>
trigger_state=METEORITE_PASSED_JD state=&#39;METEORITE_PASSED_JD_RETRY&#39;<br>
2026-08-08 18:52:11  [DEBUG]  dispatcher._run_unified index 3/6<br>
238dab27-7c06-44d3-ac14-9ed95a003387 -&gt; claimed<br>
2026-08-08 18:52:11  [DEBUG]   | entity_type=job<br>
trigger_state=METEORITE_PASSED_JD state=&#39;METEORITE_PASSED_JD_RETRY&#39;<br>
2026-08-08 18:52:11  [DEBUG]  dispatcher._run_unified index 2/6<br>
9d7ca0b9-b027-4782-a55c-c9264285e6fc -&gt; claimed<br>
2026-08-08 18:52:11  [DEBUG]   | entity_type=job<br>
trigger_state=METEORITE_PASSED_JD state=&#39;METEORITE_PASSED_JD_RETRY&#39;<br>
2026-08-08 18:52:11  [DEBUG]  dispatcher._run_unified index 1/6<br>
c7471b55-dc71-4301-b593-04a687ee91d4 -&gt; claimed<br>
2026-08-08 18:52:11  [DEBUG]   | task_key=meteorite_grade_do<br>
batch_id=meteorite_grade_do-67f0a259-06dd-4a71-9e3a-f69cdc132da5<br>
batch_call_mode=True dispatch batch_size=10 claim_cap=6<br>
claim_states=[&#39;METEORITE_PASSED_JD&#39;, &#39;METEORITE_PASSED_JD_RETRY&#39;]<br>
2026-08-08 18:52:11  [DEBUG]  dispatcher._run_unified index 1/1<br>
job/METEORITE_PASSED_JD -&gt; claimed 6 entity/entities<br>
2026-08-08 18:52:11  [DEBUG]   | batch_size=10<br>
batch_id=meteorite_grade_do-67f0a259-06dd-4a71-9e3a-f69cdc132da5<br>
entity_type=&#39;job&#39; trigger_state=&#39;METEORITE_PASSED_JD&#39;<br>
2026-08-08 18:52:11  [DEBUG]  dispatcher._run_task index 1/1<br>
meteorite_grade_do -&gt; running batch<br>
2026-08-08 18:52:11  [DEBUG]   | available=6 effective_min=1<br>
max_runs=1 draining=False<br>
entity_batch_id=meteorite_grade_do-67f0a259-06dd-4a71-9e3a-f69cdc132da5<br>
2026-08-08 18:52:11  [DEBUG]  dispatcher._run_dispatch_loop index 1/1<br>
meteorite_grade_do -&gt; loop iteration 1 starting<br>
2026-08-08 18:52:11  [INFO]  Dispatching meteorite_grade_do — 6<br>
available, batch<br>
meteorite_grade_do-67f0a259-06dd-4a71-9e3a-f69cdc132da5<br>
</div></div>
```

### Comments

#### chuckles — 2026-08-08T19:52:50.852Z
@susan

1. On staging Artifacts for **somerset** → Do job criteria: are criteria rows visible and non-empty, or is that page empty?

— Chuckles

---

_Implementation detail may live in git history on `origin/dev`._
