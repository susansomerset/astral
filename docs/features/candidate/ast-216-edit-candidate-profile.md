# AST-216 — Edit Candidate Profile

<!-- linear-archive: AST-216 archived 2026-06-03 -->

## Linear archive (AST-216)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-216/edit-candidate-profile  
**Status at archive:** Done  
**Project:** Astral Candidate  
**Assignee:** susan  
**Priority / estimate:** High / 8  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Candidate provides contact information, pastes resume text and LinkedIn profile text. Grace automatically parses the resume into structured candidate_data fields. State advances from NEW to PROFILE_READY on completion.

**Acceptance Criteria:**

**Candidate Table Schema (new table):**

* astral_candidate_id: UUID (PK, generated at insert)
* first: TEXT (required)
* last: TEXT (required)
* contact_email: TEXT (required — Astral's outbound email, may differ from resume email)
* state: TEXT (candidate state machine, default NEW)
* candidate_data: JSON blob (all candidate content, see below)
* created_at, updated_at, state_changed_at: TIMESTAMP

**candidate_data initial shape:**

* display_email: TEXT (optional, resume-facing email)
* phone: TEXT (optional)
* location: TEXT (optional)
* github: TEXT (optional)
* linkedin_url: TEXT (optional)
* resume_raw: TEXT (full text paste of resume)
* linkedin_raw: TEXT (full text paste of LinkedIn profile)
* resume_summary: TEXT (populated by Parse Resume)
* resume_competencies: array (populated by Parse Resume)
* resume_experiences: array (populated by Parse Resume)
* resume_previous_experience: array (populated by Parse Resume)
* resume_education_certifications: array (populated by Parse Resume)
* resume_skills: array (populated by Parse Resume)
* strengths: array (populated in survey, initially empty)
* priorities: array (populated in survey, initially empty)
* deal_breakers: array (populated in survey, initially empty)
* backstory: array (populated in survey, initially empty)

**Company Table Update:**

* Add candidate_id FK (one-to-many: one candidate has many companies)
* All company analysis (prefilter decisions, scores, notes) is candidate-scoped
* Bootstrap migration: assign existing company rows to candidate_id=1 (Susan)

**Profile Screen (UI — Candidate > Profile):**

* DetailsEditPage component
* Fields: first, last, contact_email, display_email, phone, location, github, linkedin_url
* Two large textarea fields: resume_raw, linkedin_raw
* Save triggers Parse Resume automatically (no separate button)
* On successful parse: candidate_data populated with resume sections, state → PROFILE_READY
* If parse fails: save contact info anyway, surface error, allow retry

**Parse Resume (automatic on save):**

* Fires do_task with task_key="parse_resume" (new task in AGENT_CONFIG)
* live_content: resume_raw text
* Grace returns structured JSON matching resume section shape above
* candidate_data updated with parsed fields via merge
* Follows same do_task pattern as all other Consult tasks (ASTRAL_CODE_RULES 2.2)
* Response schema defined in AGENT_CONFIG for validation

**State Transition:**

* NEW → PROFILE_READY (on successful profile save + parse)
* PROFILE_READY unlocks: Companies nav appears (greyed → active), Strengths nav item activates

**Nav Gating:**

* NEW state: Only Profile is active in Candidate nav. All other Candidate items visible but greyed/disabled. Companies and Jobs sections hidden entirely.
* PROFILE_READY: Companies section appears and is active. Strengths unlocks.

**Bootstrap Migration:**

* Script in scripts/migrations/ to seed candidate_id=1 from existing data/candidate/ files
* Assigns all existing company rows to candidate_id=1
* Idempotent: safe to run multiple times

**Database:**

* candidate table: INSERT new record (admin creates via Manage Candidates)
* candidate table: UPDATE candidate_data, state, updated_at, state_changed_at
* company table: ALTER to add candidate_id FK
* [database.py](<http://database.py>) header inventory updated per ASTRAL_CODE_RULES 1.1

# Edit Candidate Profile

**Scope:** Create the candidate table, add candidate_id FK to company table, and build all database CRUD functions.

* CREATE TABLE candidate (astral_candidate_id UUID PK, first, last, contact_email, state TEXT default 'NEW', candidate_data JSON, created_at, updated_at, state_changed_at)
* ALTER TABLE company ADD COLUMN candidate_id TEXT (FK to candidate)
* Index on company.candidate_id
* Database functions: save_candidate, get_candidate, update_candidate, update_candidate_data, get_candidate_for_entity
* get_candidate_for_entity resolves candidate_id from entity chain: given "job"/astral_job_id or "company"/short_name, walks the FK to return candidate_id
* Schema flags: \_candidate_schema_ensured, \_company_candidate_fk_ensured
* Update [database.py](<http://database.py>) module docstring header inventory per ASTRAL_CODE_RULES 1.1
* Add CANDIDATE_STATES ordered list to [config.py](<http://config.py>) following COMPANY_STATES pattern

**Layer:** src/data/database.py, src/utils/config.py

## Metadata

* URL: [AST-221](https://linear.app/astralcareermatch/issue/AST-221/candidate-table-schema-and-database-functions)
* Identifier: [AST-221](https://linear.app/astralcareermatch/issue/AST-221/candidate-table-schema-and-database-functions)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Candidate](https://linear.app/astralcareermatch/project/astral-candidate-f048b61dbb2c). Process of reviewing, interviewing, revising and reformatting the candidate base resume and context files.
* Created: 2026-02-28T21:13:13.754Z
* Updated: 2026-03-01T03:40:49.418Z

---

# Edit Candidate Profile

**Scope:** Create src/core/candidate.py with orchestration functions for candidate operations.

* create_candidate(first, last, contact_email) -- calls save_candidate, returns candidate
* get_candidate(candidate_id) -- fetch with all data
* update_candidate_profile(candidate_id, profile_fields) -- update contact fields + candidate_data, trigger parse_resume if resume_raw present
* transition_candidate_state(candidate_id, to_state) -- validate linear progression (can only advance one step), update state + state_changed_at
* get_candidate_state(candidate_id) -- returns current state string
* Import rules: imports from src/data/database, src/external/anthropic, src/utils/config only

**Layer:** src/core/candidate.py

## Metadata

* URL: [AST-222](https://linear.app/astralcareermatch/issue/AST-222/candidate-core-layer)
* Identifier: [AST-222](https://linear.app/astralcareermatch/issue/AST-222/candidate-core-layer)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Candidate](https://linear.app/astralcareermatch/project/astral-candidate-f048b61dbb2c). Process of reviewing, interviewing, revising and reformatting the candidate base resume and context files.
* Created: 2026-02-28T21:13:14.749Z
* Updated: 2026-03-01T03:40:49.349Z

---

# Edit Candidate Profile

**Scope:** Add parse_resume task definition to AGENT_CONFIG and create placeholder task prompt file.

* New task parse_resume in AGENT_CONFIG ([config.py](<http://config.py>))
* system_prompt: job_analyst_grace.txt (existing Grace persona)
* task_prompt: ja_parse_resume.txt (placeholder with instructions skeleton)
* cached_blocks: none (resume text is live_content)
* response_format: json
* response_schema: { resume_summary: str, resume_competencies: list, resume_experiences: list, resume_previous_experience: list, resume_education_certifications: list, resume_skills: list }
* Placeholder task prompt file at data/agents/\_taskprompts/ja_parse_resume.txt
* Task prompt content (.txt) is Admin responsibility; sub-issue defines config entry + schema only

**Layer:** src/utils/config.py, data/agents/\_taskprompts/

## Metadata

* URL: [AST-223](https://linear.app/astralcareermatch/issue/AST-223/parse-resume-agent-config-task)
* Identifier: [AST-223](https://linear.app/astralcareermatch/issue/AST-223/parse-resume-agent-config-task)
* Status: Done
* Priority: Medium
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Candidate](https://linear.app/astralcareermatch/project/astral-candidate-f048b61dbb2c). Process of reviewing, interviewing, revising and reformatting the candidate base resume and context files.
* Created: 2026-02-28T21:13:15.977Z
* Updated: 2026-03-01T03:40:49.313Z

---

# Edit Candidate Profile

**Scope:** Build parse_candidate_resume function in core/candidate.py that calls do_task and merges results into candidate_data.

* parse_candidate_resume(candidate_id) in src/core/candidate.py
* Fetches candidate, gets resume_raw from candidate_data
* Calls do_task("parse_resume", live_content=resume_raw) -- no index needed (not entity-scoped)
* On success: merges parsed sections into candidate_data via update_candidate_data, transitions NEW -> PROFILE_READY
* On failure: saves contact info anyway (partial save), returns error dict for UI
* Audits AI response via add_agent_response_entry (same pattern as render_verdict)

**Layer:** src/core/candidate.py

## Metadata

* URL: [AST-224](https://linear.app/astralcareermatch/issue/AST-224/parse-resume-core-orchestration)
* Identifier: [AST-224](https://linear.app/astralcareermatch/issue/AST-224/parse-resume-core-orchestration)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Candidate](https://linear.app/astralcareermatch/project/astral-candidate-f048b61dbb2c). Process of reviewing, interviewing, revising and reformatting the candidate base resume and context files.
* Created: 2026-02-28T21:13:16.959Z
* Updated: 2026-03-01T03:40:49.279Z

---

# Edit Candidate Profile

**Scope:** Create Flask Blueprint for candidate CRUD endpoints, register in [server.py](<http://server.py>).

* New Blueprint ui/api/candidate.py with url_prefix="/api/candidates"
* Register in ui/server.py alongside existing blueprints
* Endpoints (all @require_auth):
  * GET /api/candidates -- list all candidates (for Manage Candidates ListPage)
  * GET /api/candidates/<id> -- single candidate with full candidate_data
  * POST /api/candidates -- create new candidate (from Manage Candidates modal)
  * PUT /api/candidates/<id>/profile -- update profile fields, triggers parse_resume on save if resume_raw changed
  * GET /api/candidates/<id>/state -- returns current state (for nav gating)
* Error handling: 404 for unknown candidate, 400 for validation errors, 500 for parse failures
* Response format: JSON, consistent with existing API patterns

**Layer:** ui/api/candidate.py, ui/server.py

## Metadata

* URL: [AST-225](https://linear.app/astralcareermatch/issue/AST-225/candidate-api-endpoints-blueprint)
* Identifier: [AST-225](https://linear.app/astralcareermatch/issue/AST-225/candidate-api-endpoints-blueprint)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Candidate](https://linear.app/astralcareermatch/project/astral-candidate-f048b61dbb2c). Process of reviewing, interviewing, revising and reformatting the candidate base resume and context files.
* Created: 2026-02-28T21:13:18.124Z
* Updated: 2026-03-01T03:40:49.248Z

---

# Edit Candidate Profile

**Scope:** Wire Profile.tsx to real API endpoints and update DATA_SHAPES to match actual candidate schema.

* Update Profile.tsx to fetch candidate data from GET /api/candidates/<id> (hardcoded id=1 initially)
* Save calls PUT /api/candidates/<id>/profile
* Surface parse errors if resume parse fails (toast or inline error)
* Loading state while fetching
* Update DATA_SHAPES candidates.detail.profile in [config.py](<http://config.py>): first, last, contact_email, display_email, phone, location, github, linkedin_url, resume_raw (textarea), linkedin_raw (textarea)
* DetailsEditPage component already built and wired

**Layer:** ui/frontend/src/pages/Candidate/Profile.tsx, src/utils/config.py

## Metadata

* URL: [AST-226](https://linear.app/astralcareermatch/issue/AST-226/profile-screen-wiring-de-stub)
* Identifier: [AST-226](https://linear.app/astralcareermatch/issue/AST-226/profile-screen-wiring-de-stub)
* Status: Done
* Priority: High
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Candidate](https://linear.app/astralcareermatch/project/astral-candidate-f048b61dbb2c). Process of reviewing, interviewing, revising and reformatting the candidate base resume and context files.
* Created: 2026-02-28T21:13:19.124Z
* Updated: 2026-03-01T03:40:49.217Z

---

# Edit Candidate Profile

**Scope:** Create idempotent migration script to seed candidate_id=1 from existing data/candidate/ files and assign all company rows.

* New script scripts/migrations/bootstrap_candidate.py
* Reads existing data/candidate/ files: resume_base.txt, linkedinprofile.txt, private_history.txt
* Seeds candidate record (astral_candidate_id=1, first="Susan", last="Somerset", state="LIVE_PROMPTS")
* Populates candidate_data with file contents as resume_raw, linkedin_raw, etc.
* Updates all existing company rows: SET candidate_id = 1
* Idempotent: checks for existing candidate before insert, safe to re-run

**Layer:** scripts/migrations/

## Metadata

* URL: [AST-227](https://linear.app/astralcareermatch/issue/AST-227/bootstrap-migration-script)
* Identifier: [AST-227](https://linear.app/astralcareermatch/issue/AST-227/bootstrap-migration-script)
* Status: Done
* Priority: Medium
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Candidate](https://linear.app/astralcareermatch/project/astral-candidate-f048b61dbb2c). Process of reviewing, interviewing, revising and reformatting the candidate base resume and context files.
* Created: 2026-02-28T21:13:20.127Z
* Updated: 2026-03-01T03:40:49.182Z

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
