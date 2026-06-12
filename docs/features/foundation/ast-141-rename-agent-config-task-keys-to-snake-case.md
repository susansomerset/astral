# AST-141 — Rename AGENT_CONFIG Task Keys to snake_case

<!-- linear-archive: AST-141 archived 2026-06-03 -->

## Linear archive (AST-141)

**Archived:** 2026-06-03  
**Linear URL:** https://linear.app/astralcareermatch/issue/AST-141/rename-agent-config-task-keys-to-snake-case  
**Status at archive:** Done  
**Project:** Astral Foundation  
**Assignee:** susan  
**Priority / estimate:** Medium / 2  
**Parent:** —  
**Blocked by / blocks / related:** —

### Description

Rename all camelCase task keys in AGENT_CONFIG to snake_case per coding standards. Update all references in core and CLI code.

**Acceptance Criteria:**

**Renames:**

* checkJobList to check_job_list
* scoreGET to score_get
* scoreDO to score_do
* scoreLIKE to score_like
* prefilter_company: already snake_case, no change
* find_job_site: already snake_case, no change
* vet_job_list: already snake_case, no change
* parse_job_list: already snake_case, no change

**New tasks (already snake_case):**

* evaluate_jd
* select_culture_pages

**Update all references:**

* AGENT_CONFIG keys in [config.py](<http://config.py>)
* do_task(task_key=...) calls in core files
* Any CLI or test code referencing task keys

**Layer:** src/utils/config.py + all referencing files

# Rename AGENT_CONFIG Task Keys to snake_case

**Scope:** checkJobList to check_job_list, scoreGET to score_get, scoreDO to score_do, scoreLIKE to score_like; leave prefilter_company, find_job_site, vet_job_list, parse_job_list; update do_task(task_key=...) and any CLI/test refs.

**Ref:** consult-features Renames; ASTRAL_CODE_RULES 2.1.

## Metadata

* URL: [AST-170](https://linear.app/astralcareermatch/issue/AST-170/sub-rename-task-keys-in-config-and-update-references)
* Identifier: [AST-170](https://linear.app/astralcareermatch/issue/AST-170/sub-rename-task-keys-in-config-and-update-references)
* Status: Done
* Priority: Medium
* Assignee: Unassigned
* Labels: subissue
* Project: [Astral Infrastructure](https://linear.app/astralcareermatch/project/astral-infrastructure-8a6fd1dff6b8).
* Created: 2026-02-10T21:45:27.368Z
* Updated: 2026-02-20T01:27:17.210Z

### Comments

_No comments._

---

_Implementation detail may live in git history on `origin/dev`._
