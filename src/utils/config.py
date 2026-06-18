# -*- coding: utf-8 -*-
"""
Centralized configuration for ASTRAL.

Required environment variables (set in Railway / .env):
  PORT                  — Railway-provided port for the web server
  ASTRAL_DB_DIR         — Persistent volume mount path (e.g. /data). Defaults to repo data/ locally.
  ASTRAL_ENCRYPTION_KEY — Encryption key for candidate API keys at rest
  ASTRAL_ALLOWED_IPS    — Comma-separated list of allowed IP addresses for UI access
  ANTHROPIC_API_KEY     — Fallback Anthropic API key (candidates carry their own)

Config sections:
  ASTRAL_CONFIG   — paths, state machines, batch settings
  RAILWAY_CONFIG  — gunicorn deployment settings (workers, timeout)
  AGENT_CONFIG    — Anthropic model catalog (pricing, defaults)
  TASK_CONFIG     — task definitions (schemas, grading, job consult orchestration fields)
  COMPANY_STATES  — company state list + batch criteria
  CANDIDATE_STATES — candidate state progression
  ROSTER_CONFIG   — roster-specific (prefilter, locate_job_page, parse_job_list)
  GAZER_CONFIG    — gazer batch steps (validate_title, scrape_jd, gaze)
  JOB_STATES      — job state list + prior_states / retry_state per state
  TRACKER_CONFIG  — tracker-specific (ingest, jd processing)
  NAV_CONFIG      — UI navigation structure
  DATA_SHAPES     — UI data contracts per entity
  BUILD_CONFIG    — artifact rendering tokens, section metadata, JSON shape contracts
  AUTH_CONFIG     — Stytch credentials and admin user lists (AST-609)
  MERGE_TICKET_LOG_CONFIG — append-only parent epic land history (AST-675/681)
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Optional

from dotenv import load_dotenv

from src.utils.logging import get_logger

load_dotenv()  # Load .env if present — no-op in production where Railway sets vars directly

_log = get_logger(__name__)

# Project root directory (src/utils/config.py -> src/utils -> src -> project root)
_PROJECT_ROOT = Path(__file__).parent.parent.parent

# DB directory: persistent volume on Railway, repo data/ locally.
# Set ASTRAL_DB_DIR to a persistent mount path in production (e.g. /data).
_DB_DIR = Path(os.environ["ASTRAL_DB_DIR"])

# ---------------------------------------------------------------------------
# BASE_SCHEMA: universal response envelope. Every agent response is:
#   { "agent_performance": { status, failure_note }, "agent_payload": { ...task fields... } }
# _validate_response_schema checks agent_performance first, then validates
# agent_payload against the task's response_schema. do_task unwraps agent_payload
# so downstream code sees a flat dict of task fields.
# ---------------------------------------------------------------------------
BASE_SCHEMA = {
    "status": {"type": "str", "required": True, "enum": ["success", "failure"]},
    "failure_note": {"type": "str", "required": False},
}

# Post-decode jobs[] item for grade_do / grade_get / grade_like (grades_encoded_notes).
_ENCODED_CONSULT_JOB_ITEM_SCHEMA = {
    "astral_job_id": {"type": "str", "required": True},
    "grades": {
        "type": "list",
        "required": True,
        "items_schema": {
            "vector": {"type": "str", "required": True},
            "grade": {"type": "str", "required": True},
            "confidence": {"type": "int", "required": True},
        },
    },
    "notes": {"type": "str", "required": False},
}

_CRAFT_RUBRIC_CRITERION_ITEMS_SCHEMA: Dict[str, Dict[str, Any]] = {
    "label": {"type": "str", "required": True},
    "content": {"type": "str", "required": True},
    "importance": {"type": "int", "required": True, "min": 1, "max": 10},
}
_CRAFT_RUBRIC_CRITERIA_RESPONSE_SCHEMA: Dict[str, Dict[str, Any]] = {
    "criteria": {
        "type": "list",
        "required": True,
        "items_schema": _CRAFT_RUBRIC_CRITERION_ITEMS_SCHEMA,
    },
}

# ---------------------------------------------------------------------------
# TASK_CONFIG: code-owned task definitions. Prompt content (system_prompt,
# task_prompt, cached_blocks, uncached_blocks) now lives in the agent_task
# table, managed via the Manage Tasks admin screen.
# ---------------------------------------------------------------------------
TASK_CONFIG = {
    # PREP CANDIDATE ARTIFACTS PROMPTS
    # CRAFT RESUME BASE - Judith 3
    "craft_resume_base": {
        "phase": "A. Candidate Context",
        "seq": 1,
        "response_schema": {
            "resume_structure": {"type": "dict", "required": True},
            "candidate_name": {"type": "str", "required": True},
            "candidate_title": {"type": "str", "required": True},
            "candidate_contact_detail": {"type": "str", "required": True},
            "professional_summary": {"type": "str", "required": True},
            "core_competencies": {"type": "str", "required": True},
            "experience": {"type": "str", "required": True},
            "prior_experience": {"type": "str", "required": False},
            "education_certifications": {"type": "str", "required": False},
            "technical_skills": {"type": "str", "required": False},
        },
        "response_format": "json",
        "context_format": "parse_resume_{index}",
        "entity_type": None,
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    # BOOTSTRAP CANDIDATE CONTEXT - Estelle 3
    "bootstrap_candidate_context": {
        "phase": "A. Candidate Context",
        "seq": 2,
        "response_schema": {
            "bio_summary": {"type": "str", "required": True},
            "strengths": {"type": "str", "required": True},
            "priorities": {"type": "str", "required": True},
            "deal_breakers": {"type": "str", "required": True},
            "backstory": {"type": "str", "required": True},
        },
        "response_format": "json",
        "context_format": "bootstrap_{index}",
        "entity_type": None,
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    "intake_initiate_candidate": {
        "phase": "A. Candidate Intake",
        "seq": 1,
        "response_schema": {
            "ready_to_build": {"type": "bool", "required": True},
            "assistant_message": {"type": "str", "required": True},
        },
        "response_format": "json",
        "context_format": "intake_{index}",
        "entity_type": "candidate",
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    "intake_candidate_response": {
        "phase": "A. Candidate Intake",
        "seq": 2,
        "response_schema": {
            "ready_to_build": {"type": "bool", "required": True},
            "assistant_message": {"type": "str", "required": True},
        },
        "response_format": "json",
        "context_format": "intake_{index}",
        "entity_type": "candidate",
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    "intake_build_request": {
        "phase": "A. Candidate Intake",
        "seq": 3,
        "response_schema": {
            "context.bio_summary": {"type": "str", "required": True},
            "context.backstory": {"type": "str", "required": True},
            "context.strengths": {"type": "str", "required": True},
            "context.priorities": {"type": "str", "required": True},
            "context.deal_breakers": {"type": "str", "required": True},
            "profile.title_patterns": {"type": "str", "required": True},
            "company_search_terms": {"type": "str", "required": True},
        },
        "response_format": "json",
        "context_format": "intake_build_{index}",
        "entity_type": "candidate",
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    # Phase B. Candidate Artifacts
    "craft_prefilter_rubric": {
        "phase": "B. Candidate Artifacts",
        "seq": 1,
        "response_schema": _CRAFT_RUBRIC_CRITERIA_RESPONSE_SCHEMA,
        "response_format": "json",
        "entity_type": None,
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    "craft_joblist_rubric": {
        "phase": "B. Candidate Artifacts",
        "seq": 2,
        "response_schema": _CRAFT_RUBRIC_CRITERIA_RESPONSE_SCHEMA,
        "response_format": "json",
        "entity_type": None,
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    "craft_jobdesc_rubric": {
        "phase": "B. Candidate Artifacts",
        "seq": 3,
        "response_schema": _CRAFT_RUBRIC_CRITERIA_RESPONSE_SCHEMA,
        "response_format": "json",
        "entity_type": None,
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    "craft_get_rubric": {
        "phase": "B. Candidate Artifacts",
        "seq": 4,
        "response_schema": _CRAFT_RUBRIC_CRITERIA_RESPONSE_SCHEMA,
        "response_format": "json",
        "entity_type": None,
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    "craft_do_rubric": {
        "phase": "B. Candidate Artifacts",
        "seq": 5,
        "response_schema": _CRAFT_RUBRIC_CRITERIA_RESPONSE_SCHEMA,
        "response_format": "json",
        "entity_type": None,
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    "craft_like_rubric": {
        "phase": "B. Candidate Artifacts",
        "seq": 6,
        "response_schema": _CRAFT_RUBRIC_CRITERIA_RESPONSE_SCHEMA,
        "response_format": "json",
        "entity_type": None,
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    "craft_company_search_terms": {
        "phase": "B. Candidate Artifacts",
        "seq": 8,
        "response_schema": {
            "search_terms": {"type": "str", "required": True},
        },
        "response_format": "json",
        "entity_type": None,
        "requires_candidate_key": True,
        "trigger_state": None,
    },

    # Phase C. Company Roster
    # VET COMPANY PROMPT - Estelle 3
    "find_company_website": {
        "phase": "C. Company Roster",
        "seq": 1,
        "response_schema": {
            "task_success": {"type": "bool", "required": True},
            "website": {"type": "str", "required": True},
        },
        "response_format": "json",
        "context_format": "find_company_website_{index}",
        "entity_type": "company",
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    "prefilter_company": {
        "phase": "C. Company Roster",
        "seq": 2,
        "response_format": "json",
        "output_type": "grades_encoded_prefilter_links",
        "scored": True,
        "grades_key": "prefilter_grades",
        "rubric_artifact": "company_prefilter",
        "pass_threshold": 0.0,
        "pass_state": "PREFILTER_PASSED",
        "fail_state": "PREFILTER_FAILED",
        "response_schema": {
            "jobs": {
                "type": "list", "required": True,
                "items_schema": {
                    "grades": {
                        "type": "list", "required": True,
                        "items_schema": {
                            "vector": {"type": "str", "required": True},
                            "grade": {"type": "str", "required": True},
                            "confidence": {"type": "int", "required": True},
                            "reason": {"type": "str", "required": False},
                        },
                    },
                    "possible_job_links": {"type": "list", "required": False},
                    "culture_links_to_explore": {"type": "list", "required": False},
                },
            },
        },
        "context_format": "prefilter_{index}",
        "entity_type": "company",
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    "select_job_page": {
        "phase": "C. Company Roster",
        "seq": 4,
        "response_schema": {
            "selected_page": {"type": "int", "required": True},
            "response_type": {"type": "str", "required": True},
            "job_titles": {"type": "list", "required": False},
            "no_jobs_message": {"type": "str", "required": False},
            "try_links": {"type": "list", "required": False},
            "scrape_issue_summary": {"type": "str", "required": False},
            "scrape_issue_evidence": {"type": "str", "required": False},
        },
        "response_format": "json",
        "context_format": "select_job_page_{index}",
        "entity_type": "company",
        "requires_candidate_key": False,
        "trigger_state": None,
    },
    "parse_job_list": {
        "phase": "C. Company Roster",
        "seq": 6,
        "response_schema": {
            "job_container": {"type": "str", "required": True},
            "job_tag": {"type": "str", "required": True},
            "job_ids": {"type": "list", "required": True},
        },
        "response_format": "json",
        "context_format": "parse_job_list_{index}",
        "entity_type": "company",
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    "vet_inflow_discovery": {
        "phase": "C. Company Roster",
        "seq": 7,
        "response_schema": {
            "results": {
                "type": "list",
                "required": True,
                "items_schema": {
                    "hit_index": {"type": "int", "required": True},
                    "action": {"type": "str", "required": True},
                    "short_name": {"type": "str", "required": False},
                    "website": {"type": "str", "required": False},
                },
            },
        },
        "response_format": "json",
        "context_format": "vet_inflow_discovery_{index}",
        "entity_type": "candidate",
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    # Phase D. Run Time Job Analysis
    # RUNTIME JOB VETTING PROMPTS - Ruth 1
    "qualify_job_listings": {
        "phase": "D. Job Analysis",
        "seq": 1,
        "response_format": "json",          # outer envelope is JSON; agent_payload is a compact encoded string
        "output_type": "grades_encoded_meta",
        "scored": True,
        "grades_key": "joblist_grades",
        "rubric_artifact": "joblist_rubric",
        "response_schema": {
            "jobs": {
                "type": "list", "required": True,
                "items_schema": {
                    "astral_job_id":  {"type": "str", "required": True},
                    "grades":         {"type": "list", "required": True,
                                       "items_schema": {
                                           "vector": {"type": "str", "required": True},
                                           "grade":  {"type": "str", "required": True},
                                           "confidence": {"type": "int", "required": True},
                                       }},
                    "company_job_id": {"type": "str", "required": False},
                    "job_title":      {"type": "str", "required": False},
                    "job_link":       {"type": "str", "required": False},
                    "job_data":       {"type": "dict", "required": False},
                },
            },
        },
        "fallback_batch_size": 30,
        # DB dispatch_task.batch_size overrides; below is config default only.
        "pass_state": "PASSED_JOBLIST",
        "fail_state": "FAILED_JOBLIST",
        "error_state": "ERROR_QUALIFY_JOB_LISTINGS",
        "min_job_title_length": 5,
        "context_format": "qualify_job_listings_{index}",
        "entity_type": "job",
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    # EVALUATE JD - Grace 2
    "evaluate_jd": {
        "phase": "D. Job Analysis",
        "seq": 2,
        "response_format": "json",          # outer envelope is JSON; agent_payload is a compact encoded string
        "output_type": "grades_encoded",
        "scored": True,
        "grades_key": "jd_grades",
        "rubric_artifact": "jobdesc_rubric",
        "response_schema": {
            "jobs": {
                "type": "list", "required": True,
                "items_schema": {
                    "astral_job_id": {"type": "str", "required": True},
                    "grades":        {"type": "list", "required": True,
                                      "items_schema": {
                                          "vector": {"type": "str", "required": True},
                                          "grade":  {"type": "str", "required": True},
                                          "confidence": {"type": "int", "required": True},
                                      }},
                },
            },
        },
        "fallback_batch_size": 10,
        "pass_state": "PASSED_JD",
        "fail_state": "FAILED_JD",
        "error_state": "ERROR_EVALUATE_JD",
        "min_jd_chars": 80,
        "not_ready_state": "PASSED_JOBLIST",
        "context_format": "evaluate_jd_{index}",
        "entity_type": "job",
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    # RUNTIME JOB ANALYSIS PROMPTS
    # DO ANALYSIS - Grace 2
    "grade_do": {
        "phase": "D. Job Analysis",
        "seq": 3,
        "scored": True,
        "grades_key": "do_grades",
        "rubric_artifact": "do_rubric",
        "response_format": "json",
        "output_type": "grades_encoded_notes",
        "response_schema": {
            "jobs": {
                "type": "list",
                "required": True,
                "items_schema": _ENCODED_CONSULT_JOB_ITEM_SCHEMA,
            },
        },
        "fallback_batch_size": 10,
        "pass_state": "PASSED_DO",
        "fail_state": "FAILED_DO",
        "error_state": "FAILED_TECHNICAL_DO",
        "save_prefix": "do",
        "pass_threshold": 6.0,
        "grading_mode": "scored",
        "context_format": "grade_do_{index}",
        "entity_type": "job",
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    # GET ANALYSIS - Atlas 3 (needs ATS recommendations, so higher caliber model)
    "grade_get": {
        "phase": "D. Job Analysis",
        "seq": 4,
        "scored": True,
        "grades_key": "get_grades",
        "rubric_artifact": "get_rubric",
        "response_format": "json",
        "output_type": "grades_encoded_notes",
        "response_schema": {
            "jobs": {
                "type": "list",
                "required": True,
                "items_schema": _ENCODED_CONSULT_JOB_ITEM_SCHEMA,
            },
        },
        "fallback_batch_size": 10,
        "pass_state": "PASSED_GET",
        "fail_state": "FAILED_GET",
        "error_state": "FAILED_TECHNICAL_GET",
        "save_prefix": "get",
        "pass_threshold": 6.0,
        "grading_mode": "scored",
        "context_format": "grade_get_{index}",
        "entity_type": "job",
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    # LIKE ANALYSIS - Grace 2
    "grade_like": {
        "phase": "D. Job Analysis",
        "seq": 5,
        "scored": True,
        "grades_key": "like_grades",
        "rubric_artifact": "like_rubric",
        "response_format": "json",
        "output_type": "grades_encoded_notes",
        "response_schema": {
            "jobs": {
                "type": "list",
                "required": True,
                "items_schema": _ENCODED_CONSULT_JOB_ITEM_SCHEMA,
            },
        },
        "fallback_batch_size": 10,
        "pass_state": "PASSED_LIKE",
        "fail_state": "FAILED_LIKE",
        "error_state": "FAILED_TECHNICAL_LIKE",
        "save_prefix": "like",
        "pass_threshold": 6.0,
        "requires_company": True,
        "grading_mode": "scored",
        "context_format": "grade_like_{index}",
        "entity_type": "job",
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    # JAR synthesis upshot — Opus/json (AST-480). Dispatch score_floor only; Chuckles/board: persist under job_data.analysis_upshot.
    "analysis_upshot": {
        "phase": "D. Job Analysis",
        "seq": 6,
        "scored": True,
        "response_format": "json",
        "response_schema": {
            "take_jd": {"type": "str", "required": True},
            "take_get": {"type": "str", "required": True},
            "take_do": {"type": "str", "required": True},
            "take_like": {"type": "str", "required": True},
            "whole_jd_upshot": {"type": "str", "required": True},
            "segment_upshots": {
                "type": "list",
                "required": True,
                "items_schema": {
                    "segment_key": {"type": "str", "required": True},
                    "upshot": {"type": "str", "required": True},
                },
            },
            "candidate_questions": {
                "type": "list",
                "required": True,
                "items_schema": {"text": {"type": "str", "required": True}},
            },
            "caveats": {
                "type": "list",
                "required": True,
                "items_schema": {"text": {"type": "str", "required": True}},
            },
        },
        "pass_state": "RECOMMENDED",
        "error_state": "PASSED_LIKE_RETRY",
        "context_format": "analysis_upshot_{index}",
        "entity_type": "job",
        "requires_candidate_key": True,
        "requires_company": True,
        "agent_task": "analysis_upshot",
        "trigger_state": None,
    },

    # Phase E. Job Artifacts — dumb chain registry (AST-450). Ordering is agent_task.run_next
    # in Admin only. Prompt authors: caller chain tokens {$CALLER_CACHE_A}–{$CALLER_CACHE_D} / AST-455; avoid
    # duplicating --- CACHED CONTEXT --- in child prompts (AST-303). Details: AST-313.
    "anticipate_scan": {
        "phase": "E. Job Artifacts",
        "seq": 1,
        "print_label": "Anticipate Scan",
        "response_schema": {
            "astral_job_id": {"type": "str", "required": False},
            "company": {"type": "str", "required": False},
            "title": {"type": "str", "required": False},
        },
        "entity_type": "job",
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    "contemplate_job": {
        "phase": "E. Job Artifacts",
        "seq": 2,
        "response_schema": {
            "astral_job_id": {"type": "str", "required": False},
            "company": {"type": "str", "required": False},
            "title": {"type": "str", "required": False},
        },
        "entity_type": "job",
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    "advise_job_resume": {
        "phase": "E. Job Artifacts",
        "seq": 3,
        "response_schema": {
            "astral_job_id": {"type": "str", "required": False},
            "company": {"type": "str", "required": False},
            "title": {"type": "str", "required": False},
        },
        "entity_type": "job",
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    # Structure-keyed resume draft hop (AST-551 / AST-594); section bodies validated at runtime.
    "draft_job_resume": {
        "phase": "E. Job Artifacts",
        "seq": 4,
        "response_schema": {
            "astral_job_id": {"type": "str", "required": False},
            "company": {"type": "str", "required": False},
            "title": {"type": "str", "required": False},
        },
        "response_format": "json",
        "resume_section_payload": True,
        "entity_type": "job",
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    "check_job_resume": {
        "phase": "E. Job Artifacts",
        "seq": 5,
        "response_schema": {
            "astral_job_id": {"type": "str", "required": False},
            "company": {"type": "str", "required": False},
            "title": {"type": "str", "required": False},
        },
        "entity_type": "job",
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    "finalize_job_resume": {
        "phase": "E. Job Artifacts",
        "seq": 6,
        "response_schema": {
            "candidate_name": {"type": "str", "required": False},
            "candidate_title": {"type": "str", "required": False},
            "candidate_contact_detail": {"type": "str", "required": False},
            "professional_summary": {"type": "str", "required": False},
            "core_competencies": {"type": "str", "required": False},
            "experience": {"type": "str", "required": False},
            "prior_experience": {"type": "str", "required": False},
            "education_certifications": {"type": "str", "required": False},
            "technical_skills": {"type": "str", "required": False},
        },
        "entity_type": "job",
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    "draft_cover_letter": {
        "phase": "E. Job Artifacts",
        "seq": 7,
        "nocache_prompt": (
            "Return JSON only. Fields re_line and body are required prose from you. "
            "Leave signature empty — the server injects {$COVER_LETTER_SIGNATURE} at build time; "
            "do not invent a closing name block or valediction in signature."
        ),
        "response_schema": {
            "astral_job_id": {"type": "str", "required": False},
            "company": {"type": "str", "required": False},
            "title": {"type": "str", "required": False},
            "re_line": {"type": "str", "required": True},
            "body": {"type": "str", "required": True},
            "signature": {"type": "str", "required": False},
        },
        "entity_type": "job",
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    "check_cover_letter": {
        "phase": "E. Job Artifacts",
        "seq": 8,
        "response_schema": {
            "astral_job_id": {"type": "str", "required": False},
            "company": {"type": "str", "required": False},
            "title": {"type": "str", "required": False},
        },
        "entity_type": "job",
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    "finalize_cover_letter": {
        "phase": "E. Job Artifacts",
        "seq": 9,
        "response_schema": {
            "re_line": {"type": "str", "required": False},
            "body": {"type": "str", "required": False},
            "signature": {"type": "str", "required": False},
        },
        "entity_type": "job",
        "requires_candidate_key": True,
        "trigger_state": None,
    },
    "propose_application_responses": {
        "phase": "E. Job Artifacts",
        "seq": 10,
        "response_schema": {
            "astral_job_id": {"type": "str", "required": False},
            "company": {"type": "str", "required": False},
            "title": {"type": "str", "required": False},
        },
        "entity_type": "job",
        "requires_candidate_key": True,
        "trigger_state": None,
    },
}


# ---------------------------------------------------------------------------
# CONFIDENCE_* — AST-357: per-grade confidence for density scoring & prompts.
# Multipliers keyed 1–5 (admin-tunable). Descriptions duplicated in output_types
# payload text by design (low churn; avoids token-in-token indirection).
# ---------------------------------------------------------------------------
CONFIDENCE_MULTIPLIERS = {1: 0.0, 2: 0.25, 3: 0.5, 4: 0.75, 5: 1.0}

# AST-358 / AST-428: universal letter grades; AST-429 consumes for density.
GRADE_VALUES = {"A": 7, "B": 6, "C": 3, "D": 0}
MAX_GRADE_VALUE = max(GRADE_VALUES.values())
RUBRIC_TOTAL = 3000
def grade_value(letter: str) -> int:
    key = (letter or "").strip().upper()
    if key not in GRADE_VALUES:
        raise ValueError(f"Unknown grade letter: {letter!r}")
    return GRADE_VALUES[key]


CONFIDENCE_DESCRIPTIONS = {
    5: "The source explicitly states it.",
    4: "The source strongly suggests it.",
    3: "The source hints about it.",
    2: "The source makes a vague reference.",
    1: "The source doesn't say it out loud, but it's possible.",
}

# Workflow state for saved board searches (claims use ACTIVE only; AST-471 / §2.4).
BOARD_SEARCH_STATES = ("ACTIVE", "INACTIVE", "ERROR")


# Board feature metadata (criteria shape contracts).
BOARDS_CONFIG: Dict[str, Any] = {
    "board_search": {
        "criteria_version": 1,
        "save_modes": ("criteria", "deeplink"),
    },
    "ingest": {
        "initial_state": "NEW",
        "placeholder_company_prefix": "__board__",
    },
    "gaze_board": {
        "batch_size": 5,
        # Mirror COMPANY_STATES WATCH gaze cadence (AST-482).
        "scan_interval_hours": 24,
        "claim_status": "active",
        "running_status": "running",
    },
}

# Adopted board profiles (AST-415). Engineer-owned registry — no board table.
BOARD_CONFIG: Dict[str, Dict[str, Any]] = {'a16z': {'label': 'a16z Jobs', 'entry_url': 'https://jobs.a16z.com/jobs', 'adopted': True, 'parse_instructions': {'container': 'div.job-list', 'job_tag': 'div.job-list-job', 'job_link': "div.job-list-job h2.job-list-job-title a[href*='gh_jid=']", 'title': 'h2.job-list-job-title a', 'company': 'a.job-list-job-company-link', 'posted': 'span.job-list-badge-posted', 'notes': 'a16z /jobs board (Consider) as of spike: one card root is .job-list-job; title lives in h2.job-list-job-title a; apply link often has gh_jid=. Fragile if Consider renames classes — re-verify against results_visible.txt + DOM. This run had zero job cards after filters; selectors match DOM structure from populated searches but were not re-counted on cards this session.'}, 'search_criteria_schema': {'type': 'object', 'properties': {'title_query': {'type': 'string'}, 'work_mode': {'type': 'string'}, 'max_listing_age': {'type': 'string'}}, 'additionalProperties': False}, 'criteria_param_map': {'title_query': {'widget_id': 'w-00002', 'page_label': 'Search by title', 'lookup_pattern': 'free_text'}, 'work_mode': {'widget_id': 'w-00009', 'page_label': 'All jobs', 'lookup_pattern': 'select_option'}, 'max_listing_age': {'widget_id': 'w-00010', 'page_label': 'Anytime', 'lookup_pattern': 'select_option'}}, 'craft_task_key': 'craft_board_search_criteria', 'scrape_mode': 'interactive', 'widgets': {'w-00001': {'id': 'w-00001', 'label': 'w-00001', 'subtitle': '', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.locator("#header-menu-button")', 'css_path_hint': '#header-menu-button'}, 'w-00002': {'id': 'w-00002', 'label': 'Search by title', 'subtitle': '', 'kind': 'textbox', 'interaction': 'text_entry', 'locator_playwright': 'page.get_by_placeholder("Search by title")', 'css_path_hint': 'input.search-input-field', 'lookup': {'pattern': 'free_text', 'options': []}}, 'w-00003': {'id': 'w-00003', 'label': 'Roles', 'subtitle': 'Enter roles', 'kind': 'button', 'interaction': 'block_tray', 'locator_playwright': 'page.get_by_role(\'button\', name="Roles\\nEnter roles")', 'css_path_hint': 'button.block-tray-toggle', 'lookup': {'pattern': 'typeahead', 'options': [{'value': 'Engineer', 'label': 'Engineer'}, {'value': 'Software Engineer', 'label': 'Software Engineer'}, {'value': 'Sales', 'label': 'Sales'}, {'value': 'Account Executive', 'label': 'Account Executive'}, {'value': 'Marketing', 'label': 'Marketing'}, {'value': 'Senior Software Engineer', 'label': 'Senior Software Engineer'}, {'value': 'Mechanical Engineer', 'label': 'Mechanical Engineer'}, {'value': 'Solutions Architect', 'label': 'Solutions Architect'}, {'value': 'Marketing Manager', 'label': 'Marketing Manager'}, {'value': 'Frontend Engineer', 'label': 'Frontend Engineer'}]}}, 'w-00004': {'id': 'w-00004', 'label': 'Skills', 'subtitle': 'Enter skills', 'kind': 'button', 'interaction': 'block_tray', 'locator_playwright': 'page.get_by_role(\'button\', name="Skills\\nEnter skills")', 'css_path_hint': 'button.block-tray-toggle', 'lookup': {'pattern': 'typeahead', 'options': [{'value': 'Artificial Intelligence', 'label': 'Artificial Intelligence'}, {'value': 'Infrastructure', 'label': 'Infrastructure'}, {'value': 'Python', 'label': 'Python'}, {'value': 'Quality Assurance', 'label': 'Quality Assurance'}, {'value': 'Analytics', 'label': 'Analytics'}, {'value': 'Grant Writing', 'label': 'Grant Writing'}, {'value': 'Networking Technologies', 'label': 'Networking Technologies'}, {'value': '3D', 'label': '3D'}, {'value': 'Computer Vision', 'label': 'Computer Vision'}, {'value': 'Machine Learning', 'label': 'Machine Learning'}]}}, 'w-00005': {'id': 'w-00005', 'label': 'Location', 'subtitle': 'Enter locations', 'kind': 'button', 'interaction': 'block_tray', 'locator_playwright': 'page.get_by_role(\'button\', name="Location\\nEnter locations")', 'css_path_hint': 'button.block-tray-toggle', 'lookup': {'pattern': 'typeahead', 'options': [{'value': 'United States', 'label': 'United States'}, {'value': 'San Francisco Bay Area', 'label': 'San Francisco Bay Area'}, {'value': 'Europe', 'label': 'Europe'}, {'value': 'New York', 'label': 'New York'}, {'value': 'Orange County, California Area', 'label': 'Orange County, California Area'}, {'value': 'New York City Area', 'label': 'New York City Area'}, {'value': 'United Kingdom', 'label': 'United Kingdom'}, {'value': 'Texas', 'label': 'Texas'}, {'value': 'Greater Los Angeles Area', 'label': 'Greater Los Angeles Area'}, {'value': 'Latin America', 'label': 'Latin America'}]}}, 'w-00006': {'id': 'w-00006', 'label': 'Company Stage', 'subtitle': 'Enter stages', 'kind': 'button', 'interaction': 'block_tray', 'locator_playwright': 'page.get_by_role(\'button\', name="Company Stage\\nEnter stages")', 'css_path_hint': 'button.block-tray-toggle', 'lookup': {'pattern': 'select_pill', 'options': [{'value': 'Seed funded', 'label': 'Seed'}, {'value': 'Series A', 'label': 'Series A'}, {'value': 'Growth', 'label': 'Growth (Series B or later)'}, {'value': '1-10', 'label': '1–10 employees'}, {'value': '10-100', 'label': '10–100 employees'}, {'value': '100-1000', 'label': '100–1000 employees'}, {'value': '1000-undefined', 'label': '1000+ employees'}]}}, 'w-00007': {'id': 'w-00007', 'label': 'Industry', 'subtitle': 'Enter industries', 'kind': 'button', 'interaction': 'block_tray', 'locator_playwright': 'page.get_by_role(\'button\', name="Industry\\nEnter industries")', 'css_path_hint': 'button.block-tray-toggle', 'lookup': {'pattern': 'typeahead', 'options': [{'value': 'Enterprise', 'label': 'Enterprise'}, {'value': 'American Dynamism', 'label': 'American Dynamism'}, {'value': 'AI', 'label': 'AI'}, {'value': 'Consumer', 'label': 'Consumer'}, {'value': 'Fintech', 'label': 'Fintech'}, {'value': 'Bio + Health', 'label': 'Bio + Health'}, {'value': 'Crypto/Web', 'label': 'Crypto/Web'}, {'value': 'Games', 'label': 'Games'}]}}, 'w-00008': {'id': 'w-00008', 'label': 'Salary', 'subtitle': 'Select...', 'kind': 'button', 'interaction': 'block_tray', 'locator_playwright': 'page.get_by_role(\'button\', name="Salary\\nSelect...")', 'css_path_hint': 'button.block-tray-toggle', 'lookup': {'pattern': 'salary_range_slider', 'options': [], 'panel_inner_text': 'Set salary range\n0\n-\n500,000\nUSD per year\n0\n500k\nUSD\nYear'}}, 'w-00009': {'id': 'w-00009', 'label': 'All jobs', 'subtitle': '', 'kind': 'button', 'interaction': 'inline_tray', 'locator_playwright': 'page.get_by_role(\'button\', name="All jobs")', 'css_path_hint': 'button.inline-tray-toggle', 'lookup': {'pattern': 'select_option', 'options': [{'value': 'Remote', 'label': 'Remote'}, {'value': 'Hybrid', 'label': 'Hybrid'}, {'value': 'Remote or Hybrid', 'label': 'Remote or Hybrid'}, {'value': 'All jobs', 'label': 'All jobs'}]}}, 'w-00010': {'id': 'w-00010', 'label': 'Anytime', 'subtitle': '', 'kind': 'button', 'interaction': 'inline_tray', 'locator_playwright': 'page.get_by_role(\'button\', name="Anytime")', 'css_path_hint': 'button.inline-tray-toggle', 'lookup': {'pattern': 'select_option', 'options': [{'value': 'Past 24 hours', 'label': 'Past 24 hours'}, {'value': 'Past 7 days', 'label': 'Past 7 days'}, {'value': 'Past 30 days', 'label': 'Past 30 days'}, {'value': 'Past 3 months', 'label': 'Past 3 months'}, {'value': 'Past 12 months', 'label': 'Past 12 months'}, {'value': 'Anytime', 'label': 'Anytime'}]}}, 'w-00011': {'id': 'w-00011', 'label': 'Show more jobs', 'subtitle': '', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Show more jobs")', 'css_path_hint': 'button.button'}, 'w-00012': {'id': 'w-00012', 'label': 'Back to top', 'subtitle': '', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Back to top")', 'css_path_hint': 'button.boards-pagination-back-to-top'}}, 'search_keys': {'Search by title': {'widget_id': 'w-00002', 'options': [], 'locator_playwright': 'page.get_by_placeholder("Search by title")', 'lookup_pattern': 'free_text'}, 'Roles': {'widget_id': 'w-00003', 'options': [{'value': 'Engineer', 'label': 'Engineer'}, {'value': 'Software Engineer', 'label': 'Software Engineer'}, {'value': 'Sales', 'label': 'Sales'}, {'value': 'Account Executive', 'label': 'Account Executive'}, {'value': 'Marketing', 'label': 'Marketing'}, {'value': 'Senior Software Engineer', 'label': 'Senior Software Engineer'}, {'value': 'Mechanical Engineer', 'label': 'Mechanical Engineer'}, {'value': 'Solutions Architect', 'label': 'Solutions Architect'}, {'value': 'Marketing Manager', 'label': 'Marketing Manager'}, {'value': 'Frontend Engineer', 'label': 'Frontend Engineer'}], 'locator_playwright': 'page.get_by_role(\'button\', name="Roles\\nEnter roles")', 'lookup_pattern': 'typeahead', 'subtitle': 'Enter roles'}, 'Skills': {'widget_id': 'w-00004', 'options': [{'value': 'Artificial Intelligence', 'label': 'Artificial Intelligence'}, {'value': 'Infrastructure', 'label': 'Infrastructure'}, {'value': 'Python', 'label': 'Python'}, {'value': 'Quality Assurance', 'label': 'Quality Assurance'}, {'value': 'Analytics', 'label': 'Analytics'}, {'value': 'Grant Writing', 'label': 'Grant Writing'}, {'value': 'Networking Technologies', 'label': 'Networking Technologies'}, {'value': '3D', 'label': '3D'}, {'value': 'Computer Vision', 'label': 'Computer Vision'}, {'value': 'Machine Learning', 'label': 'Machine Learning'}], 'locator_playwright': 'page.get_by_role(\'button\', name="Skills\\nEnter skills")', 'lookup_pattern': 'typeahead', 'subtitle': 'Enter skills'}, 'Location': {'widget_id': 'w-00005', 'options': [{'value': 'United States', 'label': 'United States'}, {'value': 'San Francisco Bay Area', 'label': 'San Francisco Bay Area'}, {'value': 'Europe', 'label': 'Europe'}, {'value': 'New York', 'label': 'New York'}, {'value': 'Orange County, California Area', 'label': 'Orange County, California Area'}, {'value': 'New York City Area', 'label': 'New York City Area'}, {'value': 'United Kingdom', 'label': 'United Kingdom'}, {'value': 'Texas', 'label': 'Texas'}, {'value': 'Greater Los Angeles Area', 'label': 'Greater Los Angeles Area'}, {'value': 'Latin America', 'label': 'Latin America'}], 'locator_playwright': 'page.get_by_role(\'button\', name="Location\\nEnter locations")', 'lookup_pattern': 'typeahead', 'subtitle': 'Enter locations'}, 'Company Stage': {'widget_id': 'w-00006', 'options': [{'value': 'Seed funded', 'label': 'Seed'}, {'value': 'Series A', 'label': 'Series A'}, {'value': 'Growth', 'label': 'Growth (Series B or later)'}, {'value': '1-10', 'label': '1–10 employees'}, {'value': '10-100', 'label': '10–100 employees'}, {'value': '100-1000', 'label': '100–1000 employees'}, {'value': '1000-undefined', 'label': '1000+ employees'}], 'locator_playwright': 'page.get_by_role(\'button\', name="Company Stage\\nEnter stages")', 'lookup_pattern': 'select_pill', 'subtitle': 'Enter stages'}, 'Industry': {'widget_id': 'w-00007', 'options': [{'value': 'Enterprise', 'label': 'Enterprise'}, {'value': 'American Dynamism', 'label': 'American Dynamism'}, {'value': 'AI', 'label': 'AI'}, {'value': 'Consumer', 'label': 'Consumer'}, {'value': 'Fintech', 'label': 'Fintech'}, {'value': 'Bio + Health', 'label': 'Bio + Health'}, {'value': 'Crypto/Web', 'label': 'Crypto/Web'}, {'value': 'Games', 'label': 'Games'}], 'locator_playwright': 'page.get_by_role(\'button\', name="Industry\\nEnter industries")', 'lookup_pattern': 'typeahead', 'subtitle': 'Enter industries'}, 'Salary': {'widget_id': 'w-00008', 'options': [], 'locator_playwright': 'page.get_by_role(\'button\', name="Salary\\nSelect...")', 'lookup_pattern': 'salary_range_slider', 'panel_inner_text': 'Set salary range\n0\n-\n500,000\nUSD per year\n0\n500k\nUSD\nYear', 'subtitle': 'Select...'}, 'All jobs': {'widget_id': 'w-00009', 'options': [{'value': 'Remote', 'label': 'Remote'}, {'value': 'Hybrid', 'label': 'Hybrid'}, {'value': 'Remote or Hybrid', 'label': 'Remote or Hybrid'}, {'value': 'All jobs', 'label': 'All jobs'}], 'locator_playwright': 'page.get_by_role(\'button\', name="All jobs")', 'lookup_pattern': 'select_option'}, 'Anytime': {'widget_id': 'w-00010', 'options': [{'value': 'Past 24 hours', 'label': 'Past 24 hours'}, {'value': 'Past 7 days', 'label': 'Past 7 days'}, {'value': 'Past 30 days', 'label': 'Past 30 days'}, {'value': 'Past 3 months', 'label': 'Past 3 months'}, {'value': 'Past 12 months', 'label': 'Past 12 months'}, {'value': 'Anytime', 'label': 'Anytime'}], 'locator_playwright': 'page.get_by_role(\'button\', name="Anytime")', 'lookup_pattern': 'select_option'}}}, 'heavybit': {'label': 'Heavybit Jobs', 'entry_url': 'https://www.heavybit.com/jobs', 'adopted': True, 'parse_instructions': {'container': 'main', 'job_tag': '[id^="collapsible-trigger-"]', 'job_link': '[id^="collapsible-trigger-"]', 'title': '[id^="collapsible-trigger-"]', 'company': '[id^="collapsible-trigger-"]', 'posted': '', 'notes': 'Heavybit /jobs: job rows are collapsible triggers; title/company/location in trigger visible_text. Phase 2 had no filter trays.'}, 'search_criteria_schema': {'type': 'object', 'properties': {'title_query': {'type': 'string'}}, 'additionalProperties': False}, 'criteria_param_map': {'title_query': {'widget_id': 'w-00002', 'page_label': 'SEARCH FOR TITLES, THEMES, KEYWORDS...', 'lookup_pattern': 'free_text'}}, 'craft_task_key': 'craft_board_search_criteria', 'scrape_mode': 'interactive', 'widgets': {'w-00001': {'id': 'w-00001', 'label': '⌘ + K', 'subtitle': '', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="\\u2318 + K")', 'css_path_hint': 'button.flex'}, 'w-00002': {'id': 'w-00002', 'label': 'SEARCH FOR TITLES, THEMES, KEYWORDS...', 'subtitle': '', 'kind': 'textbox', 'interaction': 'text_entry', 'locator_playwright': 'page.get_by_placeholder("SEARCH FOR TITLES, THEMES, KEYWORDS...")', 'css_path_hint': 'input.search', 'lookup': {'pattern': 'free_text', 'options': []}}, 'w-00003': {'id': 'w-00003', 'label': 'Senior Solutions Engineer', 'subtitle': 'EUROPE', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Senior Solutions Engineer")', 'css_path_hint': '#collapsible-trigger-1779051491603'}, 'w-00004': {'id': 'w-00004', 'label': 'Senior Front-end Engineer', 'subtitle': 'EUROPE', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Senior Front-end Engineer")', 'css_path_hint': '#collapsible-trigger-1779051491605'}, 'w-00005': {'id': 'w-00005', 'label': 'Senior Customer Support Engineer', 'subtitle': 'USA', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Senior Customer Support Engineer")', 'css_path_hint': '#collapsible-trigger-1779051491607'}, 'w-00006': {'id': 'w-00006', 'label': 'Senior Cloud Infrastructure Engineer', 'subtitle': 'EUROPE', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Senior Cloud Infrastructure Engineer")', 'css_path_hint': '#collapsible-trigger-1779051491608'}, 'w-00007': {'id': 'w-00007', 'label': 'Lead Bazel Engineer', 'subtitle': 'EUROPE', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Lead Bazel Engineer")', 'css_path_hint': '#collapsible-trigger-1779051491608'}, 'w-00008': {'id': 'w-00008', 'label': 'Senior Backend Engineer', 'subtitle': 'EUROPE', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Senior Backend Engineer")', 'css_path_hint': '#collapsible-trigger-1779051491609'}, 'w-00009': {'id': 'w-00009', 'label': 'SDR', 'subtitle': 'NEW YORK, NEW YORK, UNITED STATES', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="SDR")', 'css_path_hint': '#collapsible-trigger-1779051491609'}, 'w-00010': {'id': 'w-00010', 'label': 'Sales Development Representative', 'subtitle': 'NEW YORK, NEW YORK, UNITED STATES', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Sales Development Representative")', 'css_path_hint': '#collapsible-trigger-1779051491610'}, 'w-00011': {'id': 'w-00011', 'label': 'Product Marketing Manager', 'subtitle': 'NEW YORK, NEW YORK, UNITED STATES', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Product Marketing Manager")', 'css_path_hint': '#collapsible-trigger-1779051491610'}, 'w-00012': {'id': 'w-00012', 'label': 'IT Specialist', 'subtitle': 'NEW YORK, NEW YORK, UNITED STATES', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="IT Specialist")', 'css_path_hint': '#collapsible-trigger-1779051491611'}, 'w-00013': {'id': 'w-00013', 'label': 'Senior Backend Engineer - AI Platform ()', 'subtitle': 'DUBLIN, DUBLIN, IRELAND', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Senior Backend Engineer - AI Platform ()")', 'css_path_hint': '#collapsible-trigger-1779051491611'}, 'w-00014': {'id': 'w-00014', 'label': 'Senior Enterprise Account Executive - DMV', 'subtitle': 'REMOTE - US', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Senior Enterprise Account Executive - DMV")', 'css_path_hint': '#collapsible-trigger-1779051491613'}, 'w-00015': {'id': 'w-00015', 'label': 'Senior Product Designer (Contract)', 'subtitle': 'REMOTE', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Senior Product Designer (Contract)")', 'css_path_hint': '#collapsible-trigger-1779051491613'}, 'w-00016': {'id': 'w-00016', 'label': 'Account Director - Chicago', 'subtitle': 'US CENTRAL (REMOTE)', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Account Director - Chicago")', 'css_path_hint': '#collapsible-trigger-1779051491614'}, 'w-00017': {'id': 'w-00017', 'label': 'Strategic Account Executive - Large Enterprise', 'subtitle': 'NEW YORK CITY, NEW YORK, UNITED STATES', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Strategic Account Executive - Large Enterprise")', 'css_path_hint': '#collapsible-trigger-1779051491614'}, 'w-00018': {'id': 'w-00018', 'label': 'ENTER EMAIL', 'subtitle': '', 'kind': 'textbox', 'interaction': 'text_entry', 'locator_playwright': 'page.get_by_placeholder("ENTER EMAIL")', 'css_path_hint': '#email', 'lookup': {'pattern': 'free_text', 'options': []}}, 'w-00019': {'id': 'w-00019', 'label': 'w-00019', 'subtitle': '', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.locator("button.absolute")', 'css_path_hint': 'button.absolute'}}, 'search_keys': {'SEARCH FOR TITLES, THEMES, KEYWORDS...': {'widget_id': 'w-00002', 'options': [], 'locator_playwright': 'page.get_by_placeholder("SEARCH FOR TITLES, THEMES, KEYWORDS...")', 'lookup_pattern': 'free_text'}, 'ENTER EMAIL': {'widget_id': 'w-00018', 'options': [], 'locator_playwright': 'page.get_by_placeholder("ENTER EMAIL")', 'lookup_pattern': 'free_text'}}}, 'general-catalyst': {'label': 'General Catalyst Jobs', 'entry_url': 'https://jobs.generalcatalyst.com/jobs', 'adopted': True, 'parse_instructions': {'container': 'main', 'job_tag': 'a[href*="/jobs/"], a[href*="positions"]', 'job_link': 'a[href*="/jobs/"], a[href*="positions"]', 'title': 'a[href*="/jobs/"], a[href*="positions"]', 'company': '', 'posted': '', 'notes': "General Catalyst / Getro jobs board: listings are link clusters under 'Showing N jobs'; company/location often in sibling text nodes. Re-verify selectors."}, 'search_criteria_schema': {'type': 'object', 'properties': {'title_query': {'type': 'string'}, 'work_mode': {'type': 'string'}}, 'additionalProperties': False}, 'criteria_param_map': {'title_query': {'widget_id': 'w-00001', 'page_label': 'Job title, company or keyword', 'lookup_pattern': 'free_text'}, 'work_mode': {'widget_id': 'w-00002', 'page_label': 'Location', 'lookup_pattern': 'free_text'}}, 'craft_task_key': 'craft_board_search_criteria', 'scrape_mode': 'interactive', 'widgets': {'w-00001': {'id': 'w-00001', 'label': 'Job title, company or keyword', 'subtitle': '', 'kind': 'textbox', 'interaction': 'text_entry', 'locator_playwright': 'page.get_by_placeholder("Job title, company or keyword")', 'css_path_hint': '#:R5b6il6:', 'lookup': {'pattern': 'free_text', 'options': []}}, 'w-00002': {'id': 'w-00002', 'label': 'Location', 'subtitle': '', 'kind': 'textbox', 'interaction': 'text_entry', 'locator_playwright': 'page.get_by_placeholder("Location")', 'css_path_hint': '#:Rtb6il6:', 'lookup': {'pattern': 'free_text', 'options': []}}, 'w-00003': {'id': 'w-00003', 'label': 'Open location filter', 'subtitle': '', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Open location filter")', 'css_path_hint': 'button.sc-aXZVg'}, 'w-00004': {'id': 'w-00004', 'label': 'Job function', 'subtitle': '', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Job function")', 'css_path_hint': 'div.sc-aXZVg'}, 'w-00005': {'id': 'w-00005', 'label': 'Seniority', 'subtitle': '', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Seniority")', 'css_path_hint': 'div.sc-aXZVg'}, 'w-00006': {'id': 'w-00006', 'label': 'Salary', 'subtitle': '', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Salary")', 'css_path_hint': 'div.sc-aXZVg'}, 'w-00007': {'id': 'w-00007', 'label': 'Industry', 'subtitle': '', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Industry")', 'css_path_hint': 'div.sc-aXZVg'}, 'w-00008': {'id': 'w-00008', 'label': 'Company stage', 'subtitle': '', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Company stage")', 'css_path_hint': 'div.sc-aXZVg'}, 'w-00009': {'id': 'w-00009', 'label': 'Company size', 'subtitle': '', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Company size")', 'css_path_hint': 'div.sc-aXZVg'}, 'w-00010': {'id': 'w-00010', 'label': 'Sector', 'subtitle': '', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Sector")', 'css_path_hint': 'div.sc-aXZVg'}, 'w-00011': {'id': 'w-00011', 'label': 'Company', 'subtitle': '', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Company")', 'css_path_hint': 'div.sc-aXZVg'}, 'w-00012': {'id': 'w-00012', 'label': 'Create job alert', 'subtitle': '', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Create job alert")', 'css_path_hint': 'button.sc-eqUAAy'}, 'w-00013': {'id': 'w-00013', 'label': 'Your email', 'subtitle': '', 'kind': 'textbox', 'interaction': 'text_entry', 'locator_playwright': 'page.get_by_placeholder("Your email")', 'css_path_hint': '#:rh:-email', 'lookup': {'pattern': 'free_text', 'options': []}}, 'w-00014': {'id': 'w-00014', 'label': 'Get alerts', 'subtitle': '', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Get alerts")', 'css_path_hint': 'button.sc-eqUAAy'}, 'w-00015': {'id': 'w-00015', 'label': 'Load more', 'subtitle': '', 'kind': 'button', 'interaction': 'button', 'locator_playwright': 'page.get_by_role(\'button\', name="Load more")', 'css_path_hint': 'button.sc-eqUAAy'}}, 'search_keys': {'Job title, company or keyword': {'widget_id': 'w-00001', 'options': [], 'locator_playwright': 'page.get_by_placeholder("Job title, company or keyword")', 'lookup_pattern': 'free_text'}, 'Location': {'widget_id': 'w-00002', 'options': [], 'locator_playwright': 'page.get_by_placeholder("Location")', 'lookup_pattern': 'free_text'}, 'Your email': {'widget_id': 'w-00013', 'options': [], 'locator_playwright': 'page.get_by_placeholder("Your email")', 'lookup_pattern': 'free_text'}}}}


def list_adopted_boards() -> list:
    """Return [{board_key, label, entry_url, scrape_mode, craft_task_key}, ...] for adopted:true only."""
    rows = []
    for board_key in sorted(BOARD_CONFIG.keys()):
        entry = BOARD_CONFIG[board_key]
        if not entry.get("adopted"):
            continue
        rows.append({
            "board_key": board_key,
            "label": entry["label"],
            "entry_url": entry["entry_url"],
            "scrape_mode": entry["scrape_mode"],
            "craft_task_key": entry["craft_task_key"],
        })
    return rows


def get_board_entry(board_key: str) -> Optional[Dict[str, Any]]:
    """Return full entry if board_key exists and adopted:true; else None."""
    entry = BOARD_CONFIG.get(board_key)
    if not entry or not entry.get("adopted"):
        return None
    return dict(entry)


def get_task_keys() -> list:
    """Return list of all task keys defined in TASK_CONFIG."""
    return list(TASK_CONFIG.keys())


# ---------------------------------------------------------------------------
# BLOCK_TYPES: content block type enum for agent_data table.
# Maps to the prompt assembly structure in src/core/agent.py.
# ---------------------------------------------------------------------------
BLOCK_TYPES = [
    "SYSTEM", "CACHE_A", "CACHE_B", "CACHE_C", "CACHE_D", "NO_CACHE",
    "TASK", "RESPONSE", "FEEDBACK",
]

# ---------------------------------------------------------------------------
# ENTITY_TYPES: valid entity type strings used across agent_data, dispatch_ledger,
# agent_responses, and config. Single source of truth — add new types here.
# ---------------------------------------------------------------------------
ENTITY_TYPES = ["candidate", "company", "job"]


# ---------------------------------------------------------------------------
# GRADE_COLORS: hex colors for grade letter badges in the UI.
# Sourced from the Astral HTML report stylesheet.
# ---------------------------------------------------------------------------
GRADE_COLORS = {
    "A": "#28a745",
    "B": "#ffc107",
    "C": "#fd7e14",
    "D": "#dc3545",
    "F": "#8b0000",
    "X": "#a78bfa",
}


# ---------------------------------------------------------------------------
# COMPANY_STATES: list of company states + state config per state.
# Keys are state names; value is state config (may include "batch_criteria": {limit, sort_by, scan_interval_hours}) or {}.
# ---------------------------------------------------------------------------
COMPANY_STATES = {
    "IMPORTED": {},
    "NEW": {"batch_criteria": {"sort_by": "updated_at"}},
    "WEBSITE_FOUND": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
    "WEBSITE_FOUND_RETRY": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
    "HOMEPAGE_READY": {
        "batch_criteria": {"limit": 10, "sort_by": "updated_at"},
        "retry_state": "WEBSITE_FOUND_RETRY",
    },
    "NO_WEBSITE": {},
    "WEBSITE_REVIEW": {},
    "PREFILTER_PASSED": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
    "PJL_READY": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
    "JOBLIST_IDENTIFIED": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
    "JOBLIST_IDENTIFIED_RETRY": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
    "COULD_NOT_PARSE_JOBLIST": {},
    "PREFILTER_PASSED_RETRY": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
    "NO_PJL_SELECTED": {},
    "PREFILTER_FAILED": {},
    "NO_PREFILTER_JOBLISTS": {},
    "TO_WATCH": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
    "WATCH": {"batch_criteria": {"limit": 10, "sort_by": "last_scan_at", "scan_interval_hours": 24}},
    "IGNORE": {},
    "PREFILTER_UNKNOWN": {},
    "HARD_PARSE": {},
    "NO_OPENINGS": {"batch_criteria": {"limit": 10, "sort_by": "last_scan_at", "scan_interval_hours": 24}},
    "JOBS_FOUND": {"batch_criteria": {"limit": 10, "sort_by": "updated_at"}},
    "NO_JOBLIST": {},
    "CANNOT_PARSE_JOB_SITE": {},
    "CANNOT_READ_WEBSITE": {},
    "BOT_BLOCK": {},
    "ERROR_PREFILTER": {},
    "ERROR_LOCATE_JOB_PAGE": {},
    "JOBSITE_SCRAPE_ISSUE": {},
    "ERROR_GAZE": {},
}

# ---------------------------------------------------------------------------
# CANDIDATE_STATES: candidate state list. Linear progression through profile
# setup, context completion, content generation, and live prompt availability.
# ---------------------------------------------------------------------------
CANDIDATE_STATES = {
    "NEW": {},
    "PROFILE_READY": {},
    "CONTEXT_READY": {},
    "LIVE_PROMPTS": {},
    "DELETED": {},
}

INTAKE_CONFIG = {
    "estelle_agent_id": "X00_estelle_recruiter",
    "session_status_active": "ACTIVE",
    "session_status_built": "BUILT",
    "session_status_archived": "ARCHIVED",
    "initiate_poll_interval_ms": 3000,
    "initiate_failure_message": (
        "We could not start the interview. Close Intake and use Start Over to try again."
    ),
    "build_field_paths": [
        "context.bio_summary",
        "context.backstory",
        "context.strengths",
        "context.priorities",
        "context.deal_breakers",
        "profile.title_patterns",
        "company_search_terms",
    ],
}

# ---------------------------------------------------------------------------
# ROSTER_CONFIG: roster-specific. prefilter, locate_job_page, parse_job_list, ats_vendor_patterns.
# ---------------------------------------------------------------------------
ROSTER_CONFIG = {
    "prefilter": {
        "task_key": "prefilter_company",
        "input_state": "HOMEPAGE_READY",
        "pass_state": "PREFILTER_PASSED",
        "fail_state": "PREFILTER_FAILED",
        "pass_states": ["PREFILTER_PASSED", "TO_WATCH"],
        "legacy_pass_state": "TO_WATCH",
        "legacy_fail_state": "IGNORE",
        "legacy_pass_states": ["TO_WATCH"],
        "retry_state": "WEBSITE_FOUND_RETRY",
        "error_state": "ERROR_PREFILTER",
        "no_pjl_state": "NO_PREFILTER_JOBLISTS",
        "pjl_url_data_key": "possible_joblist_links",
    },
    "locate_job_page": {
        "input_state": "TO_WATCH",
        # JOBS_FOUND only — decomposed PJL pipeline uses fetch_job_pages → select_job_page → parse_job_list.
        "dispatch_input_states": ["JOBS_FOUND"],
        "pass_states": ["WATCH"],
        "error_state": "ERROR_LOCATE_JOB_PAGE",
        "scrape_issue_state": "JOBSITE_SCRAPE_ISSUE",
        "max_depth": 2,
    },
    "select_job_page": {
        "dispatch_trigger_state": "PJL_READY",
        "pass_states": ["JOBLIST_IDENTIFIED", "PREFILTER_PASSED_RETRY"],
        "retry_state": "PREFILTER_PASSED_RETRY",
        "identified_state": "JOBLIST_IDENTIFIED",
        "exhausted_state": "NO_PJL_SELECTED",
        "pjl_url_data_key": "possible_joblist_links",
        "selected_pjl_url_key": "selected_pjl_url",
    },
    "parse_job_list": {
        "dispatch_trigger_state": "JOBLIST_IDENTIFIED",
        "retry_trigger_state": "JOBLIST_IDENTIFIED_RETRY",
        "pass_state": "WATCH",
        "retry_state": "JOBLIST_IDENTIFIED_RETRY",
        "terminal_fail_state": "COULD_NOT_PARSE_JOBLIST",
        "selected_pjl_url_key": "selected_pjl_url",
    },
    "scrape_readiness": {
        "max_wait_ms": 20000,
        "poll_interval_ms": 500,
        "stability_polls": 2,
        "min_visible_chars": 400,
        "min_listing_hits": 1,
        "run_load_all_jobs": True,
        "load_all_jobs_after_ms": 3000,
        "listing_selectors": [
            "[class*='job-list']",
            "[class*='JobList']",
            "[class*='job-listing']",
            "[class*='opening']",
            "[data-testid*='job']",
            "a[href*='/job']",
            "a[href*='/jobs/']",
            "li[class*='job']",
            "article[class*='job']",
        ],
    },
    "gaze": {
        "error_state": "ERROR_GAZE",
    },
    "company_data_keys": {
        "homepage_text": "homepage_text",
        "nav_links": "nav_links",
        "parse_instructions": "parse_instructions",
        "website_content": "website_content",
        "prefilter_company_notes": "prefilter_company_notes",
        "prefilter_score": "prefilter_score",
        # AST-469: persisted job-list visible text (select confirm path). No coat-check handler — explicit storage only.
        "job_list_visible": "job_list_visible",
        "jobsite_scrape_issue_summary": "jobsite_scrape_issue_summary",
        "jobsite_scrape_issue_evidence": "jobsite_scrape_issue_evidence",
        "possible_joblist_links": "possible_joblist_links",
        "pjl_scrape_pages": "pjl_scrape_pages",
        "pjl_assembled_content": "pjl_assembled_content",
        "pjl_nav_links": "pjl_nav_links",
        "selected_pjl_url": "selected_pjl_url",
    },
    "culture_pages": {
        "max_pages": 6,
    },
    "ats_vendor_patterns": {
        "clearcompany": r"clearcompany\.com",
        "greenhouse": r"boards\.greenhouse\.io|greenhouse\.io",
        "lever": r"jobs\.lever\.co|lever\.co",
        "workday": r"workday\.com|myworkdayjobs\.com",
        "ashby": r"jobs\.ashbyhq\.com",
        "bamboohr": r"bamboohr\.com",
        "icims": r"icims\.com",
        "taleo": r"taleo\.(net|com)",
        "jazz": r"applytojob\.com",
        "jobvite": r"jobvite\.com|jobs\.jobvite\.com",
        "smartrecruiters": r"smartrecruiters\.com",
        "breezy": r"breezy\.hr",
        "recruitee": r"recruitee\.com",
    },
}


def roster_scrape_readiness_config() -> Dict[str, Any]:
    """Return ROSTER_CONFIG['scrape_readiness'] with optional env overrides."""
    cfg = dict(ROSTER_CONFIG.get("scrape_readiness") or {})
    for key, env_name in (
        ("max_wait_ms", "ROSTER_SCRAPE_READINESS_MAX_WAIT_MS"),
        ("poll_interval_ms", "ROSTER_SCRAPE_READINESS_POLL_INTERVAL_MS"),
    ):
        raw = os.environ.get(env_name, "").strip()
        if raw.isdigit():
            cfg[key] = int(raw)
    return cfg


# Phase 1 roster inflow discovery (AST-505): CSE search limits, vet task keys, weekly cadence.
INFLOW_CONFIG = {
    "discovery": {
        "max_results_per_query": 100,
        "date_restrict_days": 7,
        "dispatch_freq_hrs": 168,
        "scan_interval_hours": 168,  # per-term last_scan_at staleness (AST-525); not dispatch_task.last_run_at
        "dispatch_trigger_state": "LIVE_PROMPTS",
        "task_key": "inflow_discovery",
        "vet_task_key": "vet_inflow_discovery",
    },
    "resolve": {
        "max_results": 20,
        "date_restrict_days": None,
        "task_key": "inflow_resolve_website",
        "ai_task_key": "find_company_website",
        "dispatch_trigger_state": "NEW",
    },
}

# ---------------------------------------------------------------------------
# GAZER_CONFIG: gazer-batch steps (validate_title, scrape_jd, gaze). Mirrors orchestration for
# gazer-owned paths until gazer.py reads this block directly (AST-467). ROSTER_CONFIG["gaze"]
# duplicates error_state intentionally — semantic twin must stay literal-identical here.
# ---------------------------------------------------------------------------
GAZER_CONFIG = {
    "validate_title": {
        "fallback_batch_size": 30,
        "pass_state": "VALID_TITLE",
        "fail_state": "INVALID_TITLE",
    },
    "scrape_jd": {
        "fallback_batch_size": 10,
        "pass_state": "JD_READY",
        "fail_state": "JD_SCRAPE_FAIL",
        "error_states": [
            "JD_SCRAPE_FAIL_COOKIE",
            "JD_SCRAPE_FAIL_BOT",
            "JD_SCRAPE_FAIL_MISSING",
            "JD_SCRAPE_FAIL_CLOSED",
        ],
    },
    "fetch_website": {
        "fallback_batch_size": 10,
        "pass_state": "HOMEPAGE_READY",
        "fail_state": "CANNOT_READ_WEBSITE",
    },
    "fetch_job_pages": {
        "fallback_batch_size": 10,
        "pass_state": "PJL_READY",
        "fail_state": "JOBSITE_SCRAPE_ISSUE",
        "fetch_job_pages_trigger_states": ["PREFILTER_PASSED", "PREFILTER_PASSED_RETRY"],
    },
    # Same string as ROSTER_CONFIG["gaze"]["error_state"] ("ERROR_GAZE").
    "gaze": {
        "error_state": "ERROR_GAZE",
    },
}


# Rubric artifact keys validated on candidate save (trailing grade table + grade_descriptions).
RUBRIC_ARTIFACT_KEYS = frozenset(
    TASK_CONFIG[tk]["rubric_artifact"]
    for tk in (
        "qualify_job_listings",
        "evaluate_jd",
        "grade_do",
        "grade_get",
        "grade_like",
    )
)

# Rubric criteria lists (importance + grade tables) — consult rubrics plus company_prefilter (AST-359).
RUBRIC_CRITERIA_ARTIFACT_KEYS = RUBRIC_ARTIFACT_KEYS | frozenset({"company_prefilter"})

# AST-723: artifact UI keys → rubric_vector owner task_key (consumer tasks, not craft_*).
RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY: Dict[str, str] = {
    "company_prefilter": "prefilter_company",
    "joblist_rubric": "qualify_job_listings",
    "jobdesc_rubric": "evaluate_jd",
    "do_rubric": "grade_do",
    "get_rubric": "grade_get",
    "like_rubric": "grade_like",
}
CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY: Dict[str, str] = {
    "craft_prefilter_rubric": "company_prefilter",
    "craft_joblist_rubric": "joblist_rubric",
    "craft_jobdesc_rubric": "jobdesc_rubric",
    "craft_get_rubric": "get_rubric",
    "craft_do_rubric": "do_rubric",
    "craft_like_rubric": "like_rubric",
}
_RUBRIC_OWNER_TASK_BY_CONSUMER_TASK_KEY = frozenset(RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY.values())


def rubric_owner_task_key(task_key: str) -> Optional[str]:
    """Return rubric_vector owner task_key for a consumer or craft rubric task."""
    if task_key in _RUBRIC_OWNER_TASK_BY_CONSUMER_TASK_KEY:
        return task_key
    artifact = CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY.get(task_key)
    if artifact:
        return RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY.get(artifact)
    return None


def task_keys_for_rubric_owner(owner_task_key: str) -> frozenset[str]:
    """Run task_keys that write vector_feedback for this rubric owner (consumer + craft)."""
    if not owner_task_key:
        return frozenset()
    keys = {owner_task_key}
    for craft, artifact in CRAFT_RUBRIC_TASK_TO_ARTIFACT_KEY.items():
        if RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY.get(artifact) == owner_task_key:
            keys.add(craft)
    return frozenset(keys)


def rubric_owner_task_key_choices() -> tuple[str, ...]:
    """Sorted owner task_keys for Admin Vector Feedback task filter."""
    return tuple(sorted(RUBRIC_OWNER_TASK_BY_ARTIFACT_KEY.values()))


# AST-707: embedded company_prefilter vectors — merged before candidate artifact criteria (embedded wins on code).
EMBEDDED_COMPANY_PREFILTER_CRITERIA: tuple[dict, ...] = (
    {
        "code": "RC",
        "label": "Reality Check",
        "importance": 8,
        "content": (
            "Reality Check — assess whether the company is real and operating as represented.\n"
            "A = clearly real and verifiable\n"
            "B = appears real with minor gaps\n"
            "C = mixed signals; legitimacy uncertain\n"
            "D = significant doubt about reality or representation\n"
            "E = strong evidence of misrepresentation\n"
            "F = not a real company or clearly fraudulent"
        ),
        "grade_descriptions": [
            {"grade": "A", "description": "Company is clearly real, active, and independently verifiable."},
            {"grade": "B", "description": "Company appears real with minor verification gaps."},
            {"grade": "C", "description": "Mixed signals; legitimacy uncertain."},
            {"grade": "D", "description": "Significant doubt the company is real or operating as represented."},
            {"grade": "E", "description": "Strong evidence of misrepresentation or shell entity."},
            {"grade": "F", "description": "Not a real company or clearly fraudulent."},
        ],
    },
)

# AST-595: resume artifact chain hop order (canonical copy also in BUILD_CONFIG['resume_artifact_chain']).
RESUME_ARTIFACT_COMPOUND_PREFIX = "BUILD_ARTIFACTS."
_RESUME_ARTIFACT_HOP_TASK_KEYS = (
    "anticipate_scan",
    "contemplate_job",
    "advise_job_resume",
    "draft_job_resume",
    "check_job_resume",
    "finalize_job_resume",
)


def _resume_artifact_compound_state_for_hop(task_key: str) -> str:
    return f"{RESUME_ARTIFACT_COMPOUND_PREFIX}{task_key}"


def _all_resume_artifact_compound_state_names() -> tuple[str, ...]:
    return tuple(_resume_artifact_compound_state_for_hop(tk) for tk in _RESUME_ARTIFACT_HOP_TASK_KEYS)


def _resume_artifact_compound_job_states() -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    keys = _RESUME_ARTIFACT_HOP_TASK_KEYS
    for i, tk in enumerate(keys):
        cs = _resume_artifact_compound_state_for_hop(tk)
        out[cs] = {
            "prior_states": (
                ["RECOMMENDED"]
                if i == 0
                else [_resume_artifact_compound_state_for_hop(keys[i - 1])]
            ),
        }
    return out


_ALL_RESUME_ARTIFACT_COMPOUND_STATES = _all_resume_artifact_compound_state_names()

# ---------------------------------------------------------------------------
# JOB_STATES: job state registry.
# Keys are state names; value is state config with:
#   prior_states: list of valid predecessor states, or None for unrestricted entry
#   retry_state:  state to hold jobs with invalid/missing output for a second attempt (batch tasks only)
# ---------------------------------------------------------------------------
JOB_STATES = {
    "NEW":                    {"prior_states": None},                                            # unrestricted — ingested from job board scans
    "VALID_TITLE":            {"prior_states": ["NEW"],                "retry_state": "VALID_TITLE_RETRY"},
    "INVALID_TITLE":          {"prior_states": ["NEW"]},
    "VALID_TITLE_RETRY":      {"prior_states": ["VALID_TITLE"]},                                 # qualify_job_listings retry holding state
    "PASSED_JOBLIST":         {"prior_states": ["VALID_TITLE", "VALID_TITLE_RETRY", "JD_READY", "JD_READY_RETRY"]},
    "FAILED_JOBLIST":         {"prior_states": ["VALID_TITLE", "VALID_TITLE_RETRY"]},
    "FAILED_TECHNICAL":       {"prior_states": None},                                            # generic technical failure
    "JD_READY":               {"prior_states": ["PASSED_JOBLIST"],    "retry_state": "JD_READY_RETRY"},
    "JD_SCRAPE_FAIL":         {"prior_states": ["PASSED_JOBLIST"]},
    "JD_SCRAPE_FAIL_COOKIE":  {"prior_states": ["PASSED_JOBLIST"]},
    "JD_SCRAPE_FAIL_BOT":     {"prior_states": ["PASSED_JOBLIST"]},
    "JD_SCRAPE_FAIL_MISSING": {"prior_states": ["PASSED_JOBLIST"]},
    "JD_SCRAPE_FAIL_CLOSED":  {"prior_states": ["PASSED_JOBLIST"]},
    "JD_READY_RETRY":         {"prior_states": ["JD_READY"]},                                   # evaluate_jd retry holding state
    "PASSED_JD":              {"prior_states": ["JD_READY", "JD_READY_RETRY"]},
    "FAILED_JD":              {"prior_states": ["JD_READY", "JD_READY_RETRY"]},
    "PASSED_DO":              {"prior_states": ["PASSED_JD"]},
    "FAILED_DO":              {"prior_states": ["PASSED_JD"]},
    "FAILED_TECHNICAL_DO":    {"prior_states": ["PASSED_JD"]},
    "PASSED_GET":             {"prior_states": ["PASSED_DO"]},
    "FAILED_GET":             {"prior_states": ["PASSED_DO"]},
    "FAILED_TECHNICAL_GET":   {"prior_states": ["PASSED_DO"]},
    # LIKE needs company website; scrape can fail after GET (not only from DO).
    "NEED_WEBSITE_CONTENT":   {"prior_states": ["PASSED_DO", "PASSED_GET"]},
    # AST-479: consult_like success queues here for analysis_upshot (sibling); not auto-promoted to BUILD_ARTIFACTS.
    "PASSED_LIKE":            {"prior_states": ["PASSED_GET"]},
    # Holding state after a post-LIKE synthesis technical failure (sibling batch); consult_like API errors stay FAILED_TECHNICAL_LIKE.
    "PASSED_LIKE_RETRY":      {"prior_states": ["PASSED_LIKE"]},
    # Upshot succeeded — candidate-facing "recommended" until UI moves job into artifact build (separate epic).
    "RECOMMENDED":            {"prior_states": ["PASSED_LIKE", "PASSED_LIKE_RETRY", *_ALL_RESUME_ARTIFACT_COMPOUND_STATES]},
    **_resume_artifact_compound_job_states(),
    "BUILD_FAILED":           {"prior_states": list(_ALL_RESUME_ARTIFACT_COMPOUND_STATES)},
    # AST-311/312: return-to-review from skipped and post-outcome states
    "CANDIDATE_REVIEW":       {"prior_states": ["RECOMMENDED", *_ALL_RESUME_ARTIFACT_COMPOUND_STATES, "BUILD_FAILED", "CANDIDATE_SKIPPED", "CANDIDATE_APPLIED", "CANDIDATE_INTERVIEW", "CANDIDATE_REJECTED", "CANDIDATE_GHOSTED"]},
    "CANDIDATE_APPLIED":      {"prior_states": ["CANDIDATE_REVIEW", "CANDIDATE_APPLIED", "CANDIDATE_INTERVIEW", "CANDIDATE_REJECTED", "CANDIDATE_GHOSTED", *_ALL_RESUME_ARTIFACT_COMPOUND_STATES, "RECOMMENDED"]},
    "CANDIDATE_INTERVIEW":    {"prior_states": ["CANDIDATE_REVIEW", "CANDIDATE_APPLIED", "CANDIDATE_INTERVIEW", "CANDIDATE_REJECTED", "CANDIDATE_GHOSTED"]},
    "CANDIDATE_REJECTED":     {"prior_states": ["CANDIDATE_REVIEW", "CANDIDATE_APPLIED", "CANDIDATE_INTERVIEW", "CANDIDATE_REJECTED", "CANDIDATE_GHOSTED"]},
    "CANDIDATE_GHOSTED":      {"prior_states": ["CANDIDATE_REVIEW", "CANDIDATE_APPLIED", "CANDIDATE_INTERVIEW", "CANDIDATE_REJECTED", "CANDIDATE_GHOSTED"]},
    "FAILED_LIKE":            {"prior_states": ["PASSED_GET"]},
    "FAILED_TECHNICAL_LIKE":  {"prior_states": ["PASSED_GET"]},
    "ERROR_QUALIFY_JOB_LISTINGS": {"prior_states": None},
    "ERROR_EVALUATE_JD":      {"prior_states": None},
    "CANDIDATE_SKIPPED":      {"prior_states": ["CANDIDATE_REVIEW", *_ALL_RESUME_ARTIFACT_COMPOUND_STATES, "RECOMMENDED"]},
}

# Recommended jobs list + nav counts — post-synthesis / review surfaces (AST-479); not pre-upshot PASSED_LIKE.
RECOMMENDED_JOB_STATES = ["RECOMMENDED", *_ALL_RESUME_ARTIFACT_COMPOUND_STATES, "CANDIDATE_REVIEW"]

JOB_BUILD_ARTIFACT_CLEAR_KEYS = (
    "resume_content",
    "cover_letter",
    "application_responses",
)

_JOBS_RECOMMENDED_CANCEL_BUILD_ACTION = {
    "action_key": "cancel_build",
    "label": "Cancel",
    "method": "POST",
    "path_suffix": "cancel_artifact_build",
}

JOBS_RECOMMENDED_PRIMARY_ACTIONS = {
    "RECOMMENDED": [
        {
            "action_key": "generate_artifacts",
            "label": "Generate Artifacts",
            "method": "POST",
            "path_suffix": "generate_artifacts",
        },
    ],
    **{
        cs: [_JOBS_RECOMMENDED_CANCEL_BUILD_ACTION]
        for cs in _ALL_RESUME_ARTIFACT_COMPOUND_STATES
    },
    "CANDIDATE_REVIEW": [
        {
            "action_key": "apply",
            "label": "Apply",
            "method": "CLIENT",
            "path_suffix": "job_link",
        },
    ],
}

assert all(state in RECOMMENDED_JOB_STATES for state in JOBS_RECOMMENDED_PRIMARY_ACTIONS)

JOBS_RECOMMENDED_REPORT_PHASE_TABS = [
    {"tab_id": "phase_jd", "nav_label": "JD", "grades_field": "jd_grades", "take_key": "take_jd"},
    {"tab_id": "phase_do", "nav_label": "DO", "grades_field": "do_grades", "take_key": "take_do"},
    {"tab_id": "phase_get", "nav_label": "GET", "grades_field": "get_grades", "take_key": "take_get"},
    {"tab_id": "phase_like", "nav_label": "LIKE", "grades_field": "like_grades", "take_key": "take_like"},
]

JOBS_RECOMMENDED_ARTIFACT_TABS = [
    {
        "tab_id": "artifact_resume",
        "nav_label": "Resume",
        "artifact_key": "resume_content",
        "shapes_key": None,
        "use_resume_structure": True,
    },
    {
        "tab_id": "artifact_cover",
        "nav_label": "Cover Letter",
        "artifact_key": "cover_letter",
        "shapes_key": "cover_letter",
        "use_resume_structure": False,
    },
    {
        "tab_id": "artifact_application",
        "nav_label": "Application",
        "artifact_key": "application_responses",
        "shapes_key": None,
        "use_resume_structure": False,
    },
]

# Ordered state lists for Jobs UI views (single source of truth for API, nav counts, frontend).
IN_REVIEW_STATES = [
    "NEW", "VALID_TITLE", "VALID_TITLE_RETRY", "PASSED_JOBLIST", "JD_READY", "JD_READY_RETRY",
    "PASSED_JD", "PASSED_DO", "PASSED_GET", "PASSED_LIKE", "PASSED_LIKE_RETRY",
]
# PASSED_* rows waiting on a scored dispatch step: claim uses latest_score >= score_floor.
# UI treats misses as Skipped while DB state stays PASSED (see api_jobs skipped / in_review).
PASSED_SCORE_GATED_STATES = frozenset({"PASSED_JD", "PASSED_DO", "PASSED_GET", "PASSED_LIKE"})


def dispatch_claim_uses_score_floor(trigger_state: Optional[str]) -> bool:
    """True when job claim should filter latest_score >= dispatch_task.score_floor.

    Distinct from trigger_state_used_by_scored_dispatch_task (task grading / TASK_CONFIG)
    and dispatch_task_key_is_scored (task_key catalog). Input triggers such as VALID_TITLE
    run a scored task but entities lack latest_score until that step completes (AST-586).
    """
    if trigger_state is None:
        return False
    ts = str(trigger_state).strip()
    if not ts or ts.endswith("_RETRY"):
        return False
    if ts in PASSED_SCORE_GATED_STATES:
        return True
    return ts in _TRANSITION_STATES_USED_BY_SCORED_TASKS


def dispatch_claim_states(trigger_state: Optional[str], entity_type: str) -> List[str]:
    """States a dispatch row claims and counts (primary + companion *_RETRY when configured)."""
    if trigger_state is None:
        return []
    ts = str(trigger_state).strip()
    if not ts:
        return []
    if ts.endswith("_RETRY"):
        return [ts]
    companion = f"{ts}_RETRY"
    if entity_type == "job" and companion in JOB_STATES:
        return [ts, companion]
    if entity_type == "company" and companion in COMPANY_STATES:
        return [ts, companion]
    return [ts]


# task_key values that may appear on dispatch_task rows (admin defaults + schema backfill).
DISPATCH_SCHEDULABLE_TASK_KEYS = frozenset({
    "prefilter", "fetch_website", "fetch_job_pages", "select_job_page", "parse_job_list",
    "recheck_no_openings", "gaze", "gaze_board",
    "inflow_discovery", "inflow_resolve_website",
    "validate_title", "qualify_job_listings", "scrape_jd", "evaluate_jd",
    "consult_do", "consult_get", "consult_like", "analysis_upshot",
    "contemplate_job", "draft_cover_letter",
})

_DISPATCH_BATCH_CALL_MODE_ONE = frozenset({
    "prefilter", "qualify_job_listings", "evaluate_jd", "consult_do", "consult_get",
    "consult_like", "gaze_board",
})

_DISPATCH_COMPANY_ENTITY_TASK_KEYS = frozenset({
    "prefilter", "fetch_website", "fetch_job_pages", "select_job_page", "parse_job_list",
    "recheck_no_openings", "gaze", "inflow_resolve_website",
})

_CONSULT_TASK_TO_AGENT_TASK: Dict[str, str] = {
    "consult_do": "grade_do",
    "consult_get": "grade_get",
    "consult_like": "grade_like",
}


def resolve_dispatch_task_config_key(task_key: str) -> str:
    """Map dispatch `task_key` to the TASK_CONFIG entry (consult batch prompts → grading keys)."""
    tk = (task_key or "").strip()
    return _CONSULT_TASK_TO_AGENT_TASK.get(tk, tk)


def _dispatch_trigger_state_for_task_key(task_key: str) -> str:
    if task_key == "prefilter":
        return ROSTER_CONFIG["prefilter"]["input_state"]
    if task_key == "parse_job_list":
        return ROSTER_CONFIG["parse_job_list"]["dispatch_trigger_state"]
    if task_key == "select_job_page":
        return ROSTER_CONFIG["select_job_page"]["dispatch_trigger_state"]
    if task_key == "recheck_no_openings":
        return "NO_OPENINGS"
    if task_key == "gaze":
        return "WATCH"
    if task_key == "gaze_board":
        return "ACTIVE"
    if task_key == "inflow_discovery":
        return INFLOW_CONFIG["discovery"]["dispatch_trigger_state"]
    if task_key == "inflow_resolve_website":
        return INFLOW_CONFIG["resolve"]["dispatch_trigger_state"]
    if task_key == "validate_title":
        return "NEW"
    if task_key == "qualify_job_listings":
        return "VALID_TITLE"
    if task_key == "scrape_jd":
        return "PASSED_JOBLIST"
    if task_key == "fetch_job_pages":
        states = GAZER_CONFIG["fetch_job_pages"].get("fetch_job_pages_trigger_states") or ["PREFILTER_PASSED"]
        return states[0]
    if task_key == "fetch_website":
        return "WEBSITE_FOUND"
    if task_key == "evaluate_jd":
        return "JD_READY"
    if task_key == "consult_do":
        return "PASSED_JD"
    if task_key == "consult_get":
        return "PASSED_DO"
    if task_key == "consult_like":
        return "PASSED_GET"
    if task_key == "analysis_upshot":
        return "PASSED_LIKE"
    if task_key in resume_artifact_hop_task_keys():
        return resume_artifact_compound_state(task_key)
    if task_key == "draft_cover_letter":
        return "CANDIDATE_REVIEW"
    if task_key not in DISPATCH_SCHEDULABLE_TASK_KEYS:
        raise KeyError(f"dispatch trigger_state: unknown task_key {task_key!r}")
    cfg = TASK_CONFIG.get(task_key)
    if cfg and cfg.get("trigger_state") is not None:
        return str(cfg["trigger_state"])
    resolved = TASK_CONFIG.get(resolve_dispatch_task_config_key(task_key)) or {}
    nrs = resolved.get("not_ready_state")
    if isinstance(nrs, str) and nrs.strip():
        return nrs.strip()
    raise KeyError(f"dispatch trigger_state: no rule for task_key {task_key!r}")


def _dispatch_entity_type_for_task_key(task_key: str) -> str:
    if task_key == "prefilter" or task_key in _DISPATCH_COMPANY_ENTITY_TASK_KEYS:
        return "company"
    if task_key == "gaze_board":
        return "board_search"
    if task_key == "inflow_discovery":
        return "candidate"
    cfg = TASK_CONFIG.get(task_key) or TASK_CONFIG.get(resolve_dispatch_task_config_key(task_key)) or {}
    et = cfg.get("entity_type")
    if isinstance(et, str) and et.strip():
        return et.strip()
    if task_key in (
        "validate_title", "scrape_jd", "qualify_job_listings", "evaluate_jd",
        "consult_do", "consult_get", "consult_like", "analysis_upshot",
        "contemplate_job", "draft_cover_letter",
    ):
        return "job"
    raise KeyError(f"dispatch entity_type: no rule for task_key {task_key!r}")


def _dispatch_sort_by_for(entity_type: str, trigger_state: str) -> str:
    if entity_type == "job":
        if trigger_state in PASSED_SCORE_GATED_STATES:
            return "latest_score"
        if trigger_state in ("BUILD_ARTIFACTS", "CANDIDATE_REVIEW") or trigger_state.startswith(
            RESUME_ARTIFACT_COMPOUND_PREFIX
        ):
            return "state_changed_at"
        if trigger_state not in JOB_STATES:
            raise KeyError(f"dispatch sort_by: unknown job trigger_state {trigger_state!r}")
        return "updated_at"
    if entity_type == "company":
        bc = (COMPANY_STATES.get(trigger_state) or {}).get("batch_criteria") or {}
        sort_by = bc.get("sort_by")
        if not sort_by:
            raise KeyError(f"dispatch sort_by: company state {trigger_state!r} missing batch_criteria.sort_by")
        return str(sort_by)
    if entity_type == "board_search":
        return "last_scan_at"
    if entity_type == "candidate":
        return "updated_at"
    raise KeyError(f"dispatch sort_by: unknown entity_type {entity_type!r}")


def _dispatch_batch_call_mode_for(task_key: str) -> int:
    return 1 if task_key in _DISPATCH_BATCH_CALL_MODE_ONE else 0


def dispatch_task_admin_defaults(task_key: str) -> Dict[str, Any]:
    """Admin + DB insert defaults for dispatch_task columns. Raises KeyError if task_key is not schedulable."""
    tk = (task_key or "").strip()
    if tk not in DISPATCH_SCHEDULABLE_TASK_KEYS:
        raise KeyError(f"dispatch_task_admin_defaults: task_key {tk!r} not schedulable")
    entity_type = _dispatch_entity_type_for_task_key(tk)
    trigger_state = _dispatch_trigger_state_for_task_key(tk)
    return {
        "entity_type": entity_type,
        "trigger_state": trigger_state,
        "sort_by": _dispatch_sort_by_for(entity_type, trigger_state),
        "batch_call_mode": _dispatch_batch_call_mode_for(tk),
    }


def dispatch_task_key_is_scored(task_key: str) -> bool:
    rk = resolve_dispatch_task_config_key(task_key)
    return bool((TASK_CONFIG.get(rk) or {}).get("scored"))


def _task_config_transition_strings(tc: Dict[str, Any]) -> FrozenSet[str]:
    vals: list[str] = []
    for key in ("pass_state", "fail_state", "error_state", "not_ready_state"):
        v = tc.get(key)
        if isinstance(v, str) and v.strip():
            vals.append(v.strip())
    for v in tc.get("error_states") or ():
        if isinstance(v, str) and v.strip():
            vals.append(v.strip())
    return frozenset(vals)


_TRANSITION_STATES_USED_BY_SCORED_TASKS = frozenset(
    st
    for cfg in TASK_CONFIG.values()
    if cfg.get("scored")
    for st in _task_config_transition_strings(cfg)
)


def trigger_state_used_by_scored_dispatch_task(trigger_state: Optional[str]) -> bool:
    """True when this dispatch queue trigger attaches to a graded step (AST-468 wiring; database import)."""
    if trigger_state is None:
        return False
    ts = str(trigger_state).strip()
    if not ts:
        return False
    if ts.endswith("_RETRY"):
        return False

    for dk in DISPATCH_SCHEDULABLE_TASK_KEYS:
        if dispatch_task_admin_defaults(dk)["trigger_state"] == ts and dispatch_task_key_is_scored(dk):
            return True

    # Outcomes that scored tasks emit (e.g. PASSED_JOBLIST is qualify_job_listings pass_state).
    return ts in _TRANSITION_STATES_USED_BY_SCORED_TASKS


SKIPPED_STATES = [
    "INVALID_TITLE",
    "FAILED_JOBLIST", "JD_SCRAPE_FAIL",
    "JD_SCRAPE_FAIL_COOKIE", "JD_SCRAPE_FAIL_BOT", "JD_SCRAPE_FAIL_MISSING", "JD_SCRAPE_FAIL_CLOSED",
    "FAILED_JD", "FAILED_TECHNICAL",
    "FAILED_DO", "FAILED_TECHNICAL_DO",
    "FAILED_GET", "FAILED_TECHNICAL_GET",
    "NEED_WEBSITE_CONTENT",
    "FAILED_LIKE", "FAILED_TECHNICAL_LIKE",
    "ERROR_QUALIFY_JOB_LISTINGS", "ERROR_EVALUATE_JD",
    "CANDIDATE_SKIPPED",
]

# ---------------------------------------------------------------------------
# UI state manifest (AST-387 G1): labels + transition targets for Flask/React.
# Keys must exist on JOB_STATES / COMPANY_STATES / CANDIDATE_STATES as noted.
# ---------------------------------------------------------------------------
JOBS_SKIPPED_BELOW_DISPATCH_KEY = "__BELOW_DISPATCH_FLOOR__"
JOBS_SKIPPED_BELOW_DISPATCH_LABEL = "Below dispatch score floor"

JOBS_IN_REVIEW_UI_SECTIONS = [
    {"state": "NEW", "label": "New"},
    {"state": "VALID_TITLE", "label": "Valid Title"},
    {"state": "VALID_TITLE_RETRY", "label": "Valid Title (retry)"},
    {"state": "PASSED_JOBLIST", "label": "Passed Job List"},
    {"state": "JD_READY", "label": "JD Ready"},
    {"state": "JD_READY_RETRY", "label": "JD Ready (retry)"},
    {"state": "PASSED_JD", "label": "Passed Job Description"},
    {"state": "PASSED_DO", "label": "Passed DO"},
    {"state": "PASSED_GET", "label": "Passed GET"},
    {"state": "PASSED_LIKE", "label": "Passed LIKE"},
    {"state": "PASSED_LIKE_RETRY", "label": "LIKE upshot (retry)"},
]

JOBS_RECOMMENDED_UI_SECTIONS = [
    {"state": "RECOMMENDED", "label": "Recommended"},
    *[
        {"state": cs, "label": "In Progress"}
        for cs in _ALL_RESUME_ARTIFACT_COMPOUND_STATES
    ],
    {"state": "CANDIDATE_REVIEW", "label": "Ready"},
]

JOBS_RECOMMENDED_PHASE_SCORE_COLUMNS = [
    {"field": "jd_score", "label": "JD"},
    {"field": "do_score", "label": "DO"},
    {"field": "get_score", "label": "GET"},
    {"field": "like_score", "label": "LIKE"},
]

assert all(row["state"] in RECOMMENDED_JOB_STATES for row in JOBS_RECOMMENDED_UI_SECTIONS)

JOBS_SKIPPED_SECTION_ORDER = [
    "FAILED_LIKE",
    "FAILED_TECHNICAL_LIKE",
    "FAILED_GET",
    "FAILED_TECHNICAL_GET",
    "FAILED_DO",
    "FAILED_TECHNICAL_DO",
    "NEED_WEBSITE_CONTENT",
    "FAILED_JD",
    "FAILED_TECHNICAL",
    "FAILED_JOBLIST",
    "INVALID_TITLE",
    "JD_SCRAPE_FAIL",
    "JD_SCRAPE_FAIL_COOKIE",
    "JD_SCRAPE_FAIL_BOT",
    "JD_SCRAPE_FAIL_MISSING",
    "JD_SCRAPE_FAIL_CLOSED",
    "ERROR_QUALIFY_JOB_LISTINGS",
    "ERROR_EVALUATE_JD",
    "CANDIDATE_SKIPPED",
]

JOBS_SKIPPED_SECTION_LABELS = {
    "FAILED_JOBLIST": "Failed Job List",
    "FAILED_JD": "Failed Job Description",
    "FAILED_TECHNICAL": "Failed Technical",
    "FAILED_GET": "Failed GET",
    "FAILED_TECHNICAL_GET": "Failed Technical GET",
    "FAILED_DO": "Failed DO",
    "FAILED_TECHNICAL_DO": "Failed Technical DO",
    "NEED_WEBSITE_CONTENT": "Need Website Content",
    "FAILED_LIKE": "Failed LIKE",
    "FAILED_TECHNICAL_LIKE": "Failed Technical LIKE",
}

# Which `job[...]` grade blob to read for rubric columns (keys ⊆ JOB_STATES).
JOBS_IN_REVIEW_GRADE_FIELD = {
    "VALID_TITLE_RETRY": "joblist_grades",
    "PASSED_JOBLIST": "joblist_grades",
    "JD_READY": "jd_grades",
    "JD_READY_RETRY": "jd_grades",
    "PASSED_JD": "jd_grades",
    "PASSED_DO": "do_grades",
    "PASSED_GET": "get_grades",
    "PASSED_LIKE": "like_grades",
    "PASSED_LIKE_RETRY": "like_grades",
}
JOBS_SKIPPED_GRADE_FIELD = {
    "FAILED_JOBLIST": "joblist_grades",
    "FAILED_JD": "jd_grades",
    "FAILED_GET": "get_grades",
    "FAILED_DO": "do_grades",
    "FAILED_LIKE": "like_grades",
}
JOBS_UI_GRADE_RUBRIC = {
    "joblist_grades": "joblist_rubric",
    "jd_grades": "jobdesc_rubric",
    "do_grades": "do_rubric",
    "get_grades": "get_rubric",
    "like_grades": "like_rubric",
}

for _row in JOBS_RECOMMENDED_REPORT_PHASE_TABS:
    assert _row["grades_field"] in JOBS_UI_GRADE_RUBRIC


def build_state_ui_manifest() -> Dict[str, Any]:
    """Single JSON blob for GET /api/state_ui_manifest (G1 — no parallel TS state vocabulary)."""
    in_review_allowed = set(IN_REVIEW_STATES)
    in_review_sections = [row for row in JOBS_IN_REVIEW_UI_SECTIONS if row["state"] in in_review_allowed]

    skipped_order = [s for s in JOBS_SKIPPED_SECTION_ORDER if s in JOB_STATES]
    skipped_labels = {
        s: JOBS_SKIPPED_SECTION_LABELS.get(s, s.replace("_", " ").title()) for s in skipped_order
    }

    gen_states = ["CONTEXT_READY", "LIVE_PROMPTS"]
    assert all(s in CANDIDATE_STATES for s in gen_states)

    bulk_company = {
        "inactive_list_to_state": "WEBSITE_FOUND",
        "ignored_list_to_state": "TO_WATCH",
        "watch_list_ignore_to_state": "IGNORE",
        "watch_list_ack_to_state": "WEBSITE_FOUND",
    }
    assert all(v in COMPANY_STATES for v in bulk_company.values())

    grade_field = {**JOBS_IN_REVIEW_GRADE_FIELD, **JOBS_SKIPPED_GRADE_FIELD}
    assert all(k in JOB_STATES for k in grade_field)

    recommended_sections = [
        row for row in JOBS_RECOMMENDED_UI_SECTIONS if row["state"] in RECOMMENDED_JOB_STATES
    ]

    return {
        "jobs": {
            "in_review_sections": in_review_sections,
            "grade_field_by_job_state": grade_field,
            "grade_rubric_by_field": dict(JOBS_UI_GRADE_RUBRIC),
            "skipped": {
                "below_dispatch_key": JOBS_SKIPPED_BELOW_DISPATCH_KEY,
                "below_dispatch_label": JOBS_SKIPPED_BELOW_DISPATCH_LABEL,
                "section_order": skipped_order,
                "section_labels": skipped_labels,
                "bulk_retry_to_state": "NEW",
            },
            "detail": {"already_skipped_state": "CANDIDATE_SKIPPED"},
            "recommended": {
                "sections": recommended_sections,
                "phase_score_columns": list(JOBS_RECOMMENDED_PHASE_SCORE_COLUMNS),
                "primary_actions_by_state": {
                    state: list(actions)
                    for state, actions in JOBS_RECOMMENDED_PRIMARY_ACTIONS.items()
                },
                "report_phase_tabs": list(JOBS_RECOMMENDED_REPORT_PHASE_TABS),
                "report_artifact_tabs": list(JOBS_RECOMMENDED_ARTIFACT_TABS),
                "report_fixed_tabs": [
                    {"tab_id": "summary", "nav_label": "Job Summary"},
                    {"tab_id": "jd_full", "nav_label": "Job Description"},
                ],
            },
        },
        "candidate": {"artifact_generate_states": gen_states},
        "company": {
            "watch_readonly_states": ["WATCH"],
            "bulk_transitions": bulk_company,
        },
    }


# ---------------------------------------------------------------------------
# TRACKER_CONFIG: tracker-specific. ingest, state machine, (future: flows).
# ---------------------------------------------------------------------------
TRACKER_CONFIG = {
    "ingest": {
        "initial_state": "NEW",  # state for newly ingested jobs (must be a key in JOB_STATES)
    },
    "job_data_keys": {
        "job_description": "job_description",  # coat-check: fetch via playwright if missing
    },
    "jd_min_chars": 200,  # scraped JDs shorter than this are discarded (not saved) as junk
    "jd_prune_rules": [{"prune_text":"{$JOB_TITLE}", "prune_type":"head"},
                    {"prune_text":"apply for this ", "prune_type":"tail"}, 
                    {"prune_text":"equal opportunity", "prune_type":"tail"}],
    # Signals used by _classify_jd() in gazer.py to route bad scrape captures to typed error states.
    # Order within each list is irrelevant; order of checks in _classify_jd() is: closed→bot→cookie→missing.
    "jd_classifier": {
        "closed_signals": [
            "no longer available",
            "no longer accepting",
            "position has been filled",
            "this job is no longer",
            "this position is no longer",
            "job posting has expired",
            "this role has been filled",
            "posting has been removed",
            "this listing has expired",
            "this opportunity is no longer",
            "expired job",
            "job is closed",
            "position is closed",
            "job has been closed",
            "this position has been closed",
            "posting is no longer active",
        ],
        "bot_signals": [
            # LinkedIn auth wall — scraper bounced to sign-in page
            "New to LinkedIn? Join now",
            "Sign in with Email",
            # Generic anti-bot / access-denied pages
            "Access Denied",
            "enable JavaScript",
            "verify you are human",
            "checking your browser",
            "DDoS protection",
            "Cloudflare Ray ID",
            "Please enable cookies",
            "Why have I been blocked",
            "cf-browser-verification",
            "Just a moment",
            "Please turn JavaScript on",
            "security check",
            "unusual traffic",
            "automated request",
        ],
        "cookie_signals": [
            "We value your privacy",
            "we use cookies",
            "cookie policy",
            "CookieYes sets this cookie",
            "Customize Consent Preferences",
            "Necessary cookies are required",
            "Accept all",
            "Reject all",
            "technologies such as cookies",
            "utilizes technologies such as cookies",
            "uses cookies to enable",
            "Privacy Notice",
            "Manage Preferences",
        ],
        "min_meaningful_chars": 500,   # collapsed-whitespace length below this → JD_SCRAPE_FAIL_MISSING
        "cookie_threshold":       3,   # signal hits ≥ this → cookie wall regardless of length
        "cookie_short_threshold": 1,   # signal hits ≥ this AND len < cookie_short_max → cookie
        "cookie_short_max":     400,
        "bot_threshold":          2,   # signal hits ≥ this → bot block
        "date_pattern_threshold": 5,   # ≥ this date-stamp matches → job board listing → missing
    },
}

# ---------------------------------------------------------------------------
# MERGE_TICKET_LOG_CONFIG: append-only parent epic land history (AST-675/681).
# Shipped in-repo; prep-uat appends via scripts/append_merge_ticket_log.py.
# ---------------------------------------------------------------------------
MERGE_TICKET_LOG_CONFIG = {
    "log_path": _PROJECT_ROOT / "data" / "merge_ticket_log.json",
}

# ---------------------------------------------------------------------------
# ASTRAL_CONFIG: code-related. Paths, API, state machines, batch settings.
# Grouped by consumer for migration clarity.
# ---------------------------------------------------------------------------
ASTRAL_CONFIG = {
    # --- Paths (anthropic, database, roster) ---
    # data_dir: repo-shipped files (prompts, candidate source files). Always in-tree.
    # db_dir: where astral.db lives. Overridden via ASTRAL_DB_DIR on Railway for persistence.
    "data_dir": _PROJECT_ROOT / "data",
    "db_dir": _DB_DIR,
    "agents_dir": _PROJECT_ROOT / "data" / "agents",
    "system_prompts_dir": _PROJECT_ROOT / "data" / "agents" / "_systemprompts",
    "task_prompts_dir": _PROJECT_ROOT / "data" / "agents" / "_taskprompts",
    "candidate_dir": _PROJECT_ROOT / "data" / "candidate",
    "companies_dir": _PROJECT_ROOT / "data" / "companies",  # TODO: DELETE when prefilter script migrates

    # --- Playwright/HTML (playwright) ---
    "html_cull": {
        "allowed_tags": ['a', 'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'section', 'article', 'main', 'table', 'tr', 'td', 'th'],
        "banner_patterns": ['cookie', 'consent', 'banner', 'modal', 'newsletter', 'subscribe', 'chat', 'intercom'],
        "hidden_class_patterns": ['hide', 'hidden', 'd-none', 'visually-hidden', 'sr-only'],
        "strip_attributes": ['style', 'srcset'],
        "strip_on_attrs": True,
    },
    "cookie_dismiss_selectors": [
        'button:has-text("Accept All")',
        'button:has-text("Allow All")',
        'button:has-text("Accept")',
        'button:has-text("I Accept")',
        'button:has-text("Agree")',
        'button:has-text("Confirm")',
        '[id*="accept-all"]',
        '[id*="cookie-accept"]',
        '[class*="accept-all"]',
        'button[id*="cookie"]',
        'button[class*="cookie"]',
    ],
    "cookie_fuzzy_accept_keywords": ["accept", "allow", "agree", "confirm", "ok", "got it"],
    "cookie_selfheal_url_threshold": 5,

    # --- DB (database) ---
    "db_retry": {
        "max_attempts": 3,
        "base_delay_seconds": 0.5,
        "max_delay_seconds": 5.0,
    },

    # --- Gazer (gazer) ---
    "gazer": {
        "scan_state": "WATCH",
        "concurrent_batch_size": 5,
    },

    # --- Dispatcher (dispatcher) ---
    "tick_rate_minutes": 3,           # how often the scheduler wakes to check which AUTO tasks are due
    "max_auto_threads": 3,            # max concurrent AUTO task threads; CLICK threads are excluded from this limit
    "dispatch_timeout_seconds": 3600, # AUTO task timeout (60 min); CLICK tasks run unbounded
    # Outbound probe before batch claim (stdlib HTTP in src.utils.network — not Playwright).
    "dispatch_network_check_url": "https://www.anthropic.com/",
    "dispatch_network_check_timeout_seconds": 30,
    "cache_warm_delay_seconds": 1.0,  # seconds to wait after first concurrent call before firing the rest, allowing cache to commit

    # --- Monitor (monitor) ---
    "support_email": "susan+astral@susansomerset.com",

    # --- Prompt prefix (anthropic) ---
    # Prepended to the user prompt on every API call. Tells agents the date/time
    # and instructs them on the response envelope format.
    "prompt_prefix": (
        "Your JSON response must use the two-key envelope, one is the agent_performance, the "
        "other is the agent_payload.  This is very important.  agent_performance refers ONLY "
        "to your ability to perform your task.  It has nothing to do with the payload at all, "
        "just whether or not you were prevented for some reason to perform your task.  NEVER "
        "use \"failed\" because everything in your payload did not pass for some reason, "
        "the software will think your prompt is broken and we will wastefully replicate "
        "the prompt to troubleshoot a non-existent issue.  If the status is truly \"failure\", use "
        "\"failure_note\" to explain the legitimate issue.\n\nThe agent_payload is the complete "
        "response that the software can parse per the required output schema."
    ),

    # --- Company state machine (gazer, database, roster) ---
    # State list lives in COMPANY_STATES; transitions here.
    "company_state_transitions": [
        ("IMPORTED", "WEBSITE_FOUND"),
        ("IMPORTED", "NO_WEBSITE"),
        ("IMPORTED", "WEBSITE_REVIEW"),
        ("NEW", "WEBSITE_FOUND"),
        ("NEW", "NO_WEBSITE"),
        ("WEBSITE_FOUND", "TO_WATCH"),
        ("WEBSITE_FOUND", "IGNORE"),
        ("WEBSITE_FOUND", "PREFILTER_PASSED"),
        ("WEBSITE_FOUND", "PREFILTER_FAILED"),
        ("WEBSITE_FOUND", "NO_PREFILTER_JOBLISTS"),
        ("WEBSITE_FOUND", "WEBSITE_FOUND_RETRY"),
        ("WEBSITE_FOUND", "ERROR_PREFILTER"),
        ("WEBSITE_FOUND", "HOMEPAGE_READY"),
        ("WEBSITE_FOUND", "CANNOT_READ_WEBSITE"),
        ("WEBSITE_FOUND_RETRY", "HOMEPAGE_READY"),
        ("WEBSITE_FOUND_RETRY", "CANNOT_READ_WEBSITE"),
        ("WEBSITE_FOUND_RETRY", "TO_WATCH"),
        ("WEBSITE_FOUND_RETRY", "IGNORE"),
        ("WEBSITE_FOUND_RETRY", "PREFILTER_PASSED"),
        ("WEBSITE_FOUND_RETRY", "PREFILTER_FAILED"),
        ("WEBSITE_FOUND_RETRY", "NO_PREFILTER_JOBLISTS"),
        ("WEBSITE_FOUND_RETRY", "WEBSITE_FOUND_RETRY"),
        ("WEBSITE_FOUND_RETRY", "ERROR_PREFILTER"),
        ("HOMEPAGE_READY", "PREFILTER_PASSED"),
        ("HOMEPAGE_READY", "PREFILTER_FAILED"),
        ("HOMEPAGE_READY", "NO_PREFILTER_JOBLISTS"),
        ("HOMEPAGE_READY", "TO_WATCH"),
        ("HOMEPAGE_READY", "IGNORE"),
        ("HOMEPAGE_READY", "WEBSITE_FOUND_RETRY"),
        ("HOMEPAGE_READY", "ERROR_PREFILTER"),
        ("HOMEPAGE_READY", "CANNOT_READ_WEBSITE"),
        ("TO_WATCH", "WATCH"),
        ("TO_WATCH", "HARD_PARSE"),
        ("TO_WATCH", "CANNOT_PARSE_JOB_SITE"),
        ("TO_WATCH", "NO_OPENINGS"),
        ("TO_WATCH", "NO_JOBLIST"),
        ("TO_WATCH", "BOT_BLOCK"),
        # NO_OPENINGS: Playwright-only recheck (recheck_no_openings batch); JOBS_FOUND is landing until AST-461 parse routing.
        ("NO_OPENINGS", "JOBS_FOUND"),
        # JOBS_FOUND: same locate/parse terminal set as TO_WATCH (AST-469).
        ("JOBS_FOUND", "WATCH"),
        ("JOBS_FOUND", "HARD_PARSE"),
        ("JOBS_FOUND", "CANNOT_PARSE_JOB_SITE"),
        ("JOBS_FOUND", "NO_OPENINGS"),
        ("JOBS_FOUND", "NO_JOBLIST"),
        ("JOBS_FOUND", "BOT_BLOCK"),
        # PREFILTER_PASSED: same locate/parse terminal set as TO_WATCH / JOBS_FOUND (AST-508).
        ("PREFILTER_PASSED", "WATCH"),
        ("PREFILTER_PASSED", "HARD_PARSE"),
        ("PREFILTER_PASSED", "CANNOT_PARSE_JOB_SITE"),
        ("PREFILTER_PASSED", "NO_OPENINGS"),
        ("PREFILTER_PASSED", "NO_JOBLIST"),
        ("PREFILTER_PASSED", "BOT_BLOCK"),
        ("PREFILTER_PASSED", "PJL_READY"),
        ("TO_WATCH", "JOBSITE_SCRAPE_ISSUE"),
        ("JOBS_FOUND", "JOBSITE_SCRAPE_ISSUE"),
        ("PREFILTER_PASSED", "JOBSITE_SCRAPE_ISSUE"),
        ("PJL_READY", "JOBLIST_IDENTIFIED"),
        ("PJL_READY", "PREFILTER_PASSED_RETRY"),
        ("PJL_READY", "NO_PJL_SELECTED"),
        ("PJL_READY", "NO_OPENINGS"),
        ("PJL_READY", "JOBSITE_SCRAPE_ISSUE"),
        ("PJL_READY", "NO_JOBLIST"),
        ("PREFILTER_PASSED_RETRY", "PJL_READY"),
        ("PREFILTER_PASSED_RETRY", "JOBSITE_SCRAPE_ISSUE"),
        ("JOBLIST_IDENTIFIED", "WATCH"),
        ("JOBLIST_IDENTIFIED", "JOBLIST_IDENTIFIED_RETRY"),
        ("JOBLIST_IDENTIFIED", "COULD_NOT_PARSE_JOBLIST"),
        ("JOBLIST_IDENTIFIED_RETRY", "WATCH"),
        ("JOBLIST_IDENTIFIED_RETRY", "COULD_NOT_PARSE_JOBLIST"),
    ],

    # --- Candidate state machine (candidate) ---
    # Simple: NEW → PROFILE_READY → CONTEXT_READY → LIVE_PROMPTS
    # CONTEXT_READY is gated by check_context_complete (all four context lists populated).
    "candidate_state_transitions": [
        ("NEW", "PROFILE_READY"),
        ("PROFILE_READY", "CONTEXT_READY"),
        ("CONTEXT_READY", "LIVE_PROMPTS"),
    ],

    # Valid grade letters — used by agent.py to build the grade-segment regex and for UI display.
    "valid_grades": ["A", "B", "C", "D", "F", "X"],

    # Output type registry — each entry drives {$OUTPUT_INSTRUCTIONS} token resolution and
    # determines how agent.py handles the agent_payload after receiving the AI response.
    # Entries with "_encoded" in their key are decoded by _decode_payload; "_meta" additionally
    # accepts listing metadata after grade segments; "grades_encoded_notes" maps tail to job["notes"].
    "output_types": {
        # Standard JSON grades — reserved for future use when grade_do and similar tasks
        # adopt output_type-driven instructions. No task uses this key today.
        "grades_json": {
            "payload_instructions": (
                "Respond with valid JSON using exactly the structure shown in the response schema.\n"
                "This output is parsed by software — any deviation will cause a processing failure."
            ),
        },
        # Compact encoded — grades only, no metadata fields after grade segments.
        "grades_encoded": {
            "payload_instructions": (
                "Return one JSON object with top-level keys exactly: \"agent_performance\" and \"agent_payload\".\n"
                "Put the multi-line encoded grading block inside \"agent_payload\" as a single string "
                "(newlines separate jobs). Never respond with bare pipe-lines only; never put a JSON array "
                'of jobs inside "agent_payload" — only the compact line format below.\n\n'
                "Inside agent_payload — one line per item. Format: {pos}|{code}{grade}{conf}|{code}{grade}{conf}|...\n"
                "  {pos}: 0-based input position, zero-padded to 3 digits\n"
                "  {code}: 2-char rubric vector code from the grading instructions\n"
                "  {grade}: one letter — A B C D F X\n"
                "  {conf}: one digit — confidence for that vector's grade:\n"
                "    - 5: The source explicitly states it.\n"
                "    - 4: The source strongly suggests it.\n"
                "    - 3: The source hints about it.\n"
                "    - 2: The source makes a vague reference.\n"
                "    - 1: The source doesn't say it out loud, but it's possible.\n"
                "    - 0: Use only with grade X (not applicable / no signal).\n"
                "Each grade segment is exactly 4 characters: {code}{grade}{conf}.\n"
                "\nExample:\n"
                "000|ERF1|MEF2|PGX0|WAF1|MWF1|KOF1|QCF1\n"
                "001|ERA3|MEF2|PGA4|WAA4|MWA5|KOA3|QCA1\n"
                "002|ERA5|MEA3|PGA3|WAA1|MWX0|KOF2|QCF2"
            ),
        },
        # Same grade segments as grades_encoded; optional tail → job["notes"] (do/get/like), not listing meta.
        "grades_encoded_notes": {
            "payload_instructions": (
                "Return one JSON object with top-level keys exactly: \"agent_performance\" and \"agent_payload\". "
                "Place the newline-separated compact grading lines inside \"agent_payload\" as one string "
                '(do/get/like use this shape; envelope is mandatory — not "lines only").\n'
                "Format inside agent_payload — one line per item: "
                "{pos}|{code}{grade}{conf}|{code}{grade}{conf}|...[|optional notes tail]\n"
                "  {pos}: 0-based input position, zero-padded to 3 digits\n"
                "  {code}: 2-char rubric vector code from the grading instructions\n"
                "  {grade}: one letter — A B C D F X\n"
                "  {conf}: one digit — confidence for that vector's grade:\n"
                "    - 5: The source explicitly states it.\n"
                "    - 4: The source strongly suggests it.\n"
                "    - 3: The source hints about it.\n"
                "    - 2: The source makes a vague reference.\n"
                "    - 1: The source doesn't say it out loud, but it's possible.\n"
                "    - 0: Use only with grade X (not applicable / no signal).\n"
                "Each grade segment is exactly 4 characters: {code}{grade}{conf}.\n"
                "After all segments you may append one optional notes field (pipe-separated from the last segment).\n"
                "Omit the tail entirely if you have nothing to add — that is valid.\n"
                "\nExamples (value of agent_payload):\n"
                "000|ERF1|MEF2|PGX0|WAF1|MWF1|KOF1|QCF1\n"
                "000|ERA3|MEF2|PGA4|WAA4|MWA5|KOA3|QCA1|Short optional note for the job"
            ),
        },
        # Compact encoded with optional metadata fields after grade segments.
        "grades_encoded_meta": {
            "payload_instructions": (
                "Return one JSON object with top-level keys exactly: \"agent_performance\" and \"agent_payload\".\n"
                "Pack the newline-separated qualification lines inside \"agent_payload\" as one string "
                '(outer envelope required — not bare lines).\n'
                "Format per line inside agent_payload: "
                "{pos}|{code}{grade}{conf}|{code}{grade}{conf}|...|{company_job_id}[|{job_title}|{job_link}[|{key}:{value}...]]\n"
                "  {pos}: 0-based input position, zero-padded to 3 digits\n"
                "  {code}: 2-char rubric vector code from the grading instructions\n"
                "  {grade}: one letter — A B C D F X\n"
                "  {conf}: one digit — confidence for that vector's grade:\n"
                "    - 5: The source explicitly states it.\n"
                "    - 4: The source strongly suggests it.\n"
                "    - 3: The source hints about it.\n"
                "    - 2: The source makes a vague reference.\n"
                "    - 1: The source doesn't say it out loud, but it's possible.\n"
                "    - 0: Use only with grade X (not applicable / no signal).\n"
                "Each grade segment is exactly 4 characters: {code}{grade}{conf}.\n"
                "Metadata fields follow all grade segments when your instructions say to include them.\n"
                "\nExample:\n"
                "000|ERC3|MEC4|PGA5|WAX0|MWC3|KOB5|QCB3|2983982372|Mediocre Job Title|https://www.workheredummy.com/jobs/2983982372|location:Remote|salary_range:$140-160k\n"
                "001|ERA2|MEA4|PGF5|WAA4|MWX0|KOA5|QCA2|8398237461\n"
                "002|ERB3|MEB4|PGB5|WAB5|MWA4|KOA5|QCB1|9823975238|Fine Job Title|https://www.workheredummy.com/jobs/9823975238|location:Remote|salary_range:$140-160k"
            ),
        },
        # Prefilter company: grades_encoded plus JOB:/CULT: link index tails (AST-603).
        "grades_encoded_prefilter_links": {
            "payload_instructions": (
                "Return one JSON object with top-level keys exactly: \"agent_performance\" and \"agent_payload\".\n"
                "Put the multi-line encoded grading block inside \"agent_payload\" as a single string "
                "(newlines separate jobs). Never respond with bare pipe-lines only; never put a JSON array "
                'of jobs inside "agent_payload" — only the compact line format below.\n\n'
                "Inside agent_payload — one line per item. Format: {pos}|{code}{grade}{conf}|{code}{grade}{conf}|...\n"
                "  {pos}: 0-based input position, zero-padded to 3 digits\n"
                "  {code}: 2-char rubric vector code from the grading instructions\n"
                "  {grade}: one letter — A B C D F X\n"
                "  {conf}: one digit — confidence for that vector's grade:\n"
                "    - 5: The source explicitly states it.\n"
                "    - 4: The source strongly suggests it.\n"
                "    - 3: The source hints about it.\n"
                "    - 2: The source makes a vague reference.\n"
                "    - 1: The source doesn't say it out loud, but it's possible.\n"
                "    - 0: Use only with grade X (not applicable / no signal).\n"
                "Each grade segment is exactly 4 characters: {code}{grade}{conf}.\n"
                "After all grade segments, append two optional link_set bracket fields (positional): "
                "first tail → possible job page indices (1–5 ints from the enumerated nav list); "
                "second tail → culture link indices (1–5 ints). "
                "Alternate shapes: JOB:<indices> and CULT:<indices> prefixes, or JSON keys "
                "possible_job_links / culture_links_to_explore. Software normalizes all listed shapes.\n"
                "\nExamples:\n"
                "000|ERC2|MEA3|PGA2|[13]|[3,6,19]\n"
                "000|RCA3|MPB3|USA3|[59,60]|[51,46,53]\n"
                "000|RCA3|MPB3|USA3|JOB:59,60|CULT:51,46,53"
            ),
        },
    },
    # --- Consult (consult): per-vector importance (1–10); multipliers for AST-358 scoring ---
    "consult_importance": {
        "min": 1,
        "max": 10,
        "default_vector_importance": 5,
        "multipliers": {
            1: 0.30,
            2: 0.49,
            3: 0.68,
            4: 0.87,
            5: 1.06,
            6: 1.25,
            7: 1.44,
            8: 1.63,
            9: 1.82,
            10: 2.00,
        },
    },
}

# Rubric vector feedback type/value codes (AST-722 / AST-378). AST-724 validates envelope against this.
RUBRIC_FEEDBACK_CONFIG = {
    "feedback_types": {
        "relevance": {
            "label": "Relevance",
            "value_codes": ("A", "O", "S", "R", "N"),
        },
        "clarity": {
            "label": "Clarity",
            "value_codes": ("A", "O", "S", "R", "N"),
        },
        "verdict": {
            "label": "Verdict",
            "value_codes": ("K", "E", "D"),
        },
    },
    "value_labels": {
        "A": "Always",
        "O": "Often",
        "S": "Sometimes",
        "R": "Rarely",
        "N": "Never",
        "K": "Keep",
        "E": "Edit",
        "D": "Drop",
    },
    "prompt_suffix": (
        "Vector rubric review (agent_performance only — not agent_payload): include "
        "vector_reviews as a JSON list of strings. One string per rubric vector code "
        "you were given, format CODE + R + {A|O|S|R|N} + C + {A|O|S|R|N} + V + {K|E|D} "
        '(example: "Q1RAOCVK"). agent_performance.status reflects only whether you '
        'could perform the task — never "failure" because grades or verdicts were harsh.'
    ),
}


def is_rubric_backed_task(task_key: str) -> bool:
    """True when task_key is a consumer or craft rubric task (AST-724)."""
    return rubric_owner_task_key(task_key) is not None


def importance_multiplier(n: int) -> float:
    """Return the configured multiplier for rubric importance (AST-359 / AST-358)."""
    ci = ASTRAL_CONFIG["consult_importance"]
    lo, hi = ci["min"], ci["max"]
    if isinstance(n, bool) or not isinstance(n, int):
        raise ValueError(f"importance must be int in [{lo}, {hi}], got {n!r}")
    if n < lo or n > hi:
        raise ValueError(f"importance out of range [{lo}, {hi}]: {n}")
    mult = ci["multipliers"].get(n)
    if mult is None:
        raise ValueError(f"No multiplier configured for importance {n}")
    return float(mult)


# ---------------------------------------------------------------------------
# RAILWAY_CONFIG: gunicorn / Railway deployment settings.
# Read by scripts/start_server.py to build the gunicorn command.
# Single worker required — the in-process scheduler thread runs per-worker.
# ---------------------------------------------------------------------------
RAILWAY_CONFIG = {
    "workers": 1,
    "timeout": 300,
    "playwright_browsers_path": str(_PROJECT_ROOT / ".browsers"),
}

# ---------------------------------------------------------------------------
# Timesheet rows (database ledgers): provider string validated on insert.
# ---------------------------------------------------------------------------
ALLOWED_TIMESHEET_PROVIDERS = ("anthropic", "deepseek")


# ---------------------------------------------------------------------------
# AGENT_CONFIG: Anthropic model catalog. Keyed by model_code (alias form — auto-upgrades
# with Anthropic releases). Each entry carries pricing and call defaults.
# cpm_* = cost per million tokens. temperature/max_tokens = defaults for new agents.
# cache_min_tokens = minimum prompt tokens required for Anthropic prompt caching to activate.
# Pricing as-of: 2026-03-07 — https://docs.anthropic.com/en/docs/about-claude/pricing
# Cache thresholds: https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching
# ---------------------------------------------------------------------------
AGENT_CONFIG = {
    "claude-haiku-4-5": {
        "model_label": "Haiku",
        "cpm_input": 1.00,
        "cpm_output": 5.00,
        "cpm_cache_write": 1.25,
        "cpm_cache_read": 0.10,
        "default_temperature": 0.3,
        "default_max_tokens": 8192,
        "cache_min_tokens": 4096,
    },
    "claude-sonnet-4-6": {
        "model_label": "Sonnet",
        "cpm_input": 3.00,
        "cpm_output": 15.00,
        "cpm_cache_write": 3.75,
        "cpm_cache_read": 0.30,
        "default_temperature": 0.3,
        "default_max_tokens": 16000,
        "cache_min_tokens": 2048,
    },
    "claude-opus-4-6": {
        "model_label": "Opus",
        "cpm_input": 5.00,
        "cpm_output": 25.00,
        "cpm_cache_write": 6.25,
        "cpm_cache_read": 0.50,
        "default_temperature": 0.3,
        "default_max_tokens": 16000,
        "cache_min_tokens": 4096,
    },
}

# Rough character-to-token ratio for prompt size estimation (industry standard approximation)
CHARS_PER_TOKEN = 4


def get_model(model_code: str) -> dict:
    """Return model config by model_code. Raises ValueError if not found."""
    m = AGENT_CONFIG.get(model_code)
    if not m:
        raise ValueError(f"Unknown model_code {model_code!r}. Valid: {list(AGENT_CONFIG.keys())}")
    return m


# ---------------------------------------------------------------------------
# LLM_PROVIDER_CONFIG — global active vendor (literal v1); brain tiers Little/Medium/Big;
# tier → Anthropic AGENT_CONFIG key or DeepSeek SKU + reasoning flags (AST-492).
# DeepSeek pricing USD/M tokens — https://api-docs.deepseek.com/quick_start/pricing
# Standard listed rates snapshot 2026-06-03 (vendor may adjust promos).
# Manage Agents UI catalog (AST-495) uses tier_map["anthropic"] + AGENT_CONFIG defaults.
# ---------------------------------------------------------------------------
BRAIN_LITTLE = "Little"
BRAIN_MEDIUM = "Medium"
BRAIN_BIG = "Big"
BRAIN_SETTINGS: tuple[str, str, str] = (BRAIN_LITTLE, BRAIN_MEDIUM, BRAIN_BIG)


def infer_brain_setting_from_legacy_model_code(model_code: Optional[str]) -> str:
    """Map historical AGENT_CONFIG model_code aliases to tiers (admin shim until UI sends tiers)."""
    if not model_code:
        return BRAIN_MEDIUM
    if model_code == "claude-haiku-4-5":
        return BRAIN_LITTLE
    if model_code == "claude-sonnet-4-6":
        return BRAIN_MEDIUM
    if model_code == "claude-opus-4-6":
        return BRAIN_BIG
    return BRAIN_MEDIUM


LLM_PROVIDER_CONFIG = {
    "active_provider": "deepseek",
    # anthropic | deepseek — literals only until multi-vendor UI exists
    "brain_settings": BRAIN_SETTINGS,
    "tier_map": {
        "anthropic": {
            BRAIN_LITTLE: {"agent_config_key": "claude-haiku-4-5"},
            BRAIN_MEDIUM: {"agent_config_key": "claude-sonnet-4-6"},
            BRAIN_BIG: {"agent_config_key": "claude-opus-4-6"},
        },
        "deepseek": {
            # AST-694: Little = v4-flash non-thinking; Medium = v4-pro non-thinking; Big = v4-pro thinking.
            BRAIN_LITTLE: {
                "vendor_model": "deepseek-v4-flash",
                "thinking": False,
                "reasoning_effort": None,
            },
            BRAIN_MEDIUM: {
                "vendor_model": "deepseek-v4-pro",
                "thinking": False,
                "reasoning_effort": None,
            },
            BRAIN_BIG: {
                "vendor_model": "deepseek-v4-pro",
                "thinking": True,
                "reasoning_effort": "max",
            },
        },
    },
}

# Vendor_model strings aligned with tier_map["deepseek"] (also DEEPSEEK cost_math / AST-493).
DEEPSEEK_MODEL_PRICING = {
    "deepseek-v4-flash": {
        "model_label": "DeepSeek V4 Flash",
        "cpm_cache_read": 0.0028,
        "cpm_input": 0.14,
        "cpm_cache_write": 0.0,
        "cpm_output": 0.28,
        "default_temperature": 1.0,
        "default_max_tokens": 8192,
        "cache_min_tokens": 0,
    },
    "deepseek-v4-pro": {
        "model_label": "DeepSeek V4 Pro",
        "cpm_cache_read": 3.625,
        "cpm_input": 0.435,
        "cpm_cache_write": 0.0,
        "cpm_output": 0.87,
        "default_temperature": 1.0,
        "default_max_tokens": 16000,
        "cache_min_tokens": 0,
    },
}


def get_active_llm_provider() -> str:
    """Return configured LLM vendor key (literal in LLM_PROVIDER_CONFIG)."""
    p = LLM_PROVIDER_CONFIG["active_provider"]
    if not isinstance(p, str) or not p.strip():
        raise ValueError("LLM_PROVIDER_CONFIG['active_provider'] is invalid")
    return p.strip()


def validate_allowed_brain_setting(value: str) -> None:
    if value not in LLM_PROVIDER_CONFIG["brain_settings"]:
        raise ValueError(
            f"Invalid brain_setting {value!r}. Allowed: {list(LLM_PROVIDER_CONFIG['brain_settings'])}"
        )


def resolve_brain_setting_to_anthropic_agent_key(brain_setting: str) -> str:
    validate_allowed_brain_setting(brain_setting)
    key = (
        LLM_PROVIDER_CONFIG["tier_map"]
        .get("anthropic", {})
        .get(brain_setting, {})
        .get("agent_config_key")
    )
    if not key or key not in AGENT_CONFIG:
        raise ValueError(f"No Anthropic tier mapping for brain_setting {brain_setting!r}")
    return str(key)


def resolve_brain_setting_to_deepseek_tier_meta(brain_setting: str) -> Dict[str, Any]:
    """Vendor model id + reasoning flags for send_to_deepseek (AST-493)."""
    validate_allowed_brain_setting(brain_setting)
    tier = dict(LLM_PROVIDER_CONFIG["tier_map"].get("deepseek", {}).get(brain_setting) or {})
    if not tier.get("vendor_model"):
        raise ValueError(f"No DeepSeek tier mapping for brain_setting {brain_setting!r}")
    return tier


def validate_llm_provider_environment() -> None:
    """Fatal startup parity: require secrets for whichever vendor config selects (no fallback)."""
    provider = get_active_llm_provider()
    if provider == "anthropic":
        _ = os.environ["ANTHROPIC_API_KEY"]
    elif provider == "deepseek":
        _ = os.environ["DEEPSEEK_API_KEY"]
    else:
        raise ValueError(f"Unknown LLM active_provider {provider!r}")


# --- AST-495 helpers (thin layer on AST-492 tier_map; names kept for Admin UI / plans) ---
def anthropic_agent_key_for_brain_setting(brain_setting: str) -> str:
    """Tier → Anthropic AGENT_CONFIG key (delegates to resolve_*)."""
    return resolve_brain_setting_to_anthropic_agent_key(brain_setting)


def brain_setting_for_anthropic_agent_key(agent_key: str | None) -> str | None:
    """Anthropic AGENT_CONFIG key → tier for legacy rows that only persist model_code."""
    if not agent_key:
        return None
    for tier in BRAIN_SETTINGS:
        if resolve_brain_setting_to_anthropic_agent_key(tier) == agent_key:
            return tier
    return None


def admin_brain_setting_catalog() -> list[dict[str, Any]]:
    """Tier rows for GET /api/admin/agents/brain_settings (defaults from AGENT_CONFIG)."""
    out: list[dict[str, Any]] = []
    for tier in BRAIN_SETTINGS:
        mk = resolve_brain_setting_to_anthropic_agent_key(tier)
        m = get_model(mk)
        out.append(
            {
                "brain_setting": tier,
                "label": tier,
                "default_temperature": m["default_temperature"],
                "default_max_tokens": m["default_max_tokens"],
            }
        )
    return out


# ---------------------------------------------------------------------------
# NAV_CONFIG: UI navigation structure. Grouped sidebar sections with labels
# and route paths. Served to React frontend via /api/nav_config.
#
# Optional group-level "visible": a CANDIDATE_STATES key. Group is hidden
# unless the candidate is at or past that state. Omit = always visible.
#
# Optional item-level "enabled": a CANDIDATE_STATES key (disabled unless at
# or past that state) or False (permanently disabled stub). Omit = always enabled.
#
# ADMIN_CONFIG: Frontend-facing admin UI configuration served via /api/admin/config.
# ---------------------------------------------------------------------------
ADMIN_CONFIG = {
    "reconciliation": {
        # Lines starting with these markers indicate an Astral-exported file, not a Claude billing export.
        "astral_export_markers": ["TOTALS", "ACTUAL_TOTAL", "VARIANCE"],
        # Prefix for downloaded reconciliation CSV filenames.
        "export_filename_prefix": "astral",
    },
    # AST-649: omit from Scheduled Actions UI; backend dispatch unchanged.
    "hidden_dispatch_task_keys": ("gaze_board",),
}


def admin_hidden_dispatch_task_keys() -> frozenset:
    """task_key values hidden from Scheduled Actions admin UI (dispatch backend unchanged)."""
    raw = ADMIN_CONFIG.get("hidden_dispatch_task_keys") or ()
    return frozenset(raw)

# ---------------------------------------------------------------------------
# AUTH_CONFIG: Authentication and admin role resolution (AST-609 / AST-610).
# Consumed by src/utils/auth.py. Admin lists are env-driven — never hardcode
# Susan in Flask decorators.
# ---------------------------------------------------------------------------
def _parse_csv_env(name: str) -> frozenset[str]:
    raw = os.environ.get(name, "")
    return frozenset(part.strip() for part in raw.split(",") if part.strip())


AUTH_CONFIG = {
    "admin_user_ids": _parse_csv_env("ASTRAL_ADMIN_USER_IDS"),
    "admin_emails": frozenset(
        e.lower() for e in _parse_csv_env("ASTRAL_ADMIN_EMAILS")
    ),
    "stytch_project_id": os.environ.get("STYTCH_PROJECT_ID", ""),
    "stytch_secret": os.environ.get("STYTCH_SECRET", ""),
}


def get_auth_config() -> Dict[str, Any]:
    """Return AUTH_CONFIG (shallow copy safe for read-only callers)."""
    return dict(AUTH_CONFIG)

# ---------------------------------------------------------------------------
# UI_CONFIG: Frontend display rules served via /api/system/ui_config.
# column_types maps the type string returned by req_dict API responses to
# display properties used by ListPage to format and align cell values.
# list_table_* keys configure shared list-table layout (frozen columns, truncation).
# number_format values are resolved by formatCell() in src/ui/frontend/src/lib/fmt.ts.
# ---------------------------------------------------------------------------
UI_CONFIG = {
    "column_types": {
        "str":      {"align": "left",  "number_format": None},
        "int":      {"align": "right", "number_format": "integer"},
        "float":    {"align": "right", "number_format": "decimal"},
        "currency": {"align": "right", "number_format": "currency"},
        "date":     {"align": "left",  "number_format": "date"},
        "datetime": {"align": "left",  "number_format": "datetime"},
    },
    # AST-647: shared list-table layout — default frozen data columns (N) and cell truncate length.
    "list_table_frozen_data_columns": 2,
    "list_table_cell_truncate_chars": 30,
    # AST-366: client + API validation for profile.cover_letter_signature_image (JPEG data URL).
    "cover_letter_signature_image": {
        "max_width_px": 400,
        "max_height_px": 90,
    },
}

# ---------------------------------------------------------------------------
# The /api/nav_config endpoint in system.py resolves these against the
# selected candidate's state before serving. The frontend renders the
# resolved response with no additional visibility logic.
#
# SYNC: Every path here must have a matching route in src/ui/frontend/src/routes.tsx.
#       If you add/remove/rename a nav item, update routes.tsx to match.
# ---------------------------------------------------------------------------
NAV_CONFIG = [
    {
        "label": "Jobs",
        "visible": "LIVE_PROMPTS",
        "items": [
            {"label": "In Review", "path": "/jobs/in_review"},
            {"label": "Skipped", "path": "/jobs/skipped"},
            {"label": "Recommended", "path": "/jobs/recommended"},
            {"label": "Applied", "path": "/jobs/applied", "enabled": False},
            {"label": "Responded", "path": "/jobs/responded", "enabled": False},
        ],
    },
    {
        "label": "Companies",
        "visible": "LIVE_PROMPTS",
        "items": [
            {"label": "Watch List", "path": "/companies/watch_list"},
            {"label": "New List", "path": "/companies/new_list"},
            {"label": "Inactive List", "path": "/companies/inactive_list"},
            {"label": "Ignored", "path": "/companies/ignored"},
            {"label": "Watch History", "path": "/companies/watch_history"},
        ],
    },
    {
        "label": "Artifacts",
        "visible": "CONTEXT_READY",
        "items": [
            {"label": "Base Resume Content", "path": "/artifacts/base_resume_content"},
            {"label": "Company Watch Criteria", "path": "/artifacts/company_watch_criteria"},
            {"label": "Company Search Terms", "path": "/artifacts/company_search_terms"},
            {"label": "Job List Criteria", "path": "/artifacts/job_list_criteria"},
            {"label": "Job Description Criteria", "path": "/artifacts/job_description_criteria"},
            {"label": "Get Job Criteria", "path": "/artifacts/get_job_criteria"},
            {"label": "Do Job Criteria", "path": "/artifacts/do_job_criteria"},
            {"label": "Like Job Criteria", "path": "/artifacts/like_job_criteria"},
        ],
    },
    {
        "label": "Candidate",
        "items": [
            {"label": "Intake", "path": "/candidate/intake"},
            {"label": "Profile", "path": "/candidate/profile"},
            {"label": "Strengths", "path": "/candidate/strengths"},
            {"label": "Priorities", "path": "/candidate/priorities"},
            {"label": "Deal Breakers", "path": "/candidate/deal_breakers"},
            {"label": "Backstory", "path": "/candidate/backstory"},
            {"label": "Writing Preferences", "path": "/candidate/writing_preferences"},
        ],
    },
    {
        "label": "Admin",
        "items": [
            {"label": "Scheduled Actions", "path": "/admin/scheduled_actions"},
            {"label": "Execution History", "path": "/admin/performance_monitor"},
            {"label": "Agent Timesheets", "path": "/admin/agent_timesheets"},
            {"label": "Vector Feedback", "path": "/admin/vector_feedback"},
            {"label": "Cost Reconciliation", "path": "/admin/cost_reconciliation"},
            {"label": "Manage Candidates", "path": "/admin/manage_candidates"},
            {"label": "Manage Agents", "path": "/admin/agent_prompts"},
            {"label": "Manage Tasks", "path": "/admin/task_prompts"},
            {"label": "Agent Ad Hoc", "path": "/admin/anthropic_ad_hoc"},
            {"label": "Data Management", "path": "/admin/data_management"},
        ],
    },
]


# ---------------------------------------------------------------------------
# DATA_SHAPES: UI data contracts per entity. Served to React frontend via
# /api/shapes/<entity>. Backend imports these to construct API responses and
# validate incoming saves.
#
# Structure per entity:
#   list.<view>  -- column defs for ListPage (key, label, sortable)
#   edit         -- field defs for Modal editing (key, label, type, options)
#   detail.<view> -- sectioned field defs for DetailsEditPage
#
# Shapes define structure only (no render functions or callbacks).
# React pages may augment with client-side behavior (edit icons, renderers).
# ---------------------------------------------------------------------------
DATA_SHAPES = {
    "candidates": {
        "list": {
            "manage": [
                {"key": "first", "label": "First Name", "sortable": True},
                {"key": "last", "label": "Last Name", "sortable": True},
                {"key": "contact_email", "label": "Email", "sortable": True},
                {"key": "state", "label": "State", "sortable": True},
                {"key": "api_key_status", "label": "API Key", "sortable": True},
            ],
        },
        "edit": {
            "manage": [
                {"key": "first", "label": "First Name", "type": "text"},
                {"key": "last", "label": "Last Name", "type": "text"},
                {"key": "contact_email", "label": "Contact Email", "type": "text"},
                {"key": "reply_email", "label": "Reply Email", "type": "text"},
                {"key": "phone", "label": "Phone", "type": "text"},
                {"key": "location", "label": "Location", "type": "text"},
            ],
        },
        "detail": {
            "profile": [
                {
                    "label": "Contact Information",
                    "fields": [
                        {"key": "profile.first", "label": "First Name", "type": "text"},
                        {"key": "profile.last", "label": "Last Name", "type": "text"},
                        {"key": "profile.contact_email", "label": "Contact Email", "type": "text"},
                        {"key": "profile.reply_email", "label": "Reply Email", "type": "text"},
                        {"key": "profile.phone", "label": "Phone", "type": "text"},
                        {"key": "profile.location", "label": "Location", "type": "text"},
                        {"key": "profile.github", "label": "GitHub", "type": "text"},
                        {"key": "profile.linkedin_url", "label": "LinkedIn URL", "type": "text"},
                        {"key": "profile.timezone", "label": "Timezone", "type": "select", "options": [
                            {"value": "", "label": "(UTC)"},
                            {"value": "America/New_York", "label": "Eastern"},
                            {"value": "America/Chicago", "label": "Central"},
                            {"value": "America/Denver", "label": "Mountain"},
                            {"value": "America/Los_Angeles", "label": "Pacific"},
                            {"value": "America/Anchorage", "label": "Alaska"},
                            {"value": "Pacific/Honolulu", "label": "Hawaii"},
                        ]},
                        {"key": "profile.pronoun_preference", "label": "Pronoun preference", "type": "select", "options": [
                            {"value": "", "label": "(not set)"},
                            {"value": "they/them", "label": "they/them"},
                            {"value": "she/her", "label": "she/her"},
                            {"value": "he/him", "label": "he/him"},
                            {"value": "ze/zir", "label": "ze/zir"},
                            {"value": "e/eir", "label": "e/eir"},
                        ]},
                    ],
                },
                {
                    "label": "Bio Summary",
                    "fields": [
                        {"key": "context.bio_summary", "label": "Bio Summary", "type": "textarea"},
                    ],
                },
                {
                    "label": "Sample Cover Letter",
                    "fields": [
                        {"key": "context.sample_cover_text", "label": "Sample Cover Letter", "type": "textarea"},
                    ],
                },
                {
                    "label": "Cover Letter Signature",
                    "fields": [
                        {"key": "profile.cover_letter_signature", "label": "Signature text", "type": "textarea"},
                    ],
                },
                {
                    "label": "Signature Image",
                    "fields": [
                        {
                            "key": "profile.cover_letter_signature_image",
                            "label": "Signature Image",
                            "type": "signature_image",
                        },
                    ],
                },
                {
                    "label": "Title Patterns",
                    "fields": [
                        {"key": "profile.title_patterns", "label": "Title Patterns (one regex per line)", "type": "textarea"},
                    ],
                },
                {
                    "label": "LinkedIn Profile Text",
                    "fields": [
                        {"key": "context.linkedin_profile_text", "label": "LinkedIn Profile Text", "type": "textarea"},
                    ],
                },
                {
                    "label": "Original Resume Text",
                    "fields": [
                        {"key": "context.starting_resume_text", "label": "Original Resume Text", "type": "textarea"},
                    ],
                },
            ],
            # Legacy global tab template until per-candidate UI (AST-519); persistence authority is artifacts.resume_structure.
            "base_resume_structure": [
                {"key": "candidate_name", "label": "Candidate Name", "type": "str"},
                {"key": "candidate_title", "label": "Candidate Title", "type": "str"},
                {"key": "candidate_contact_detail", "label": "Candidate Contact Detail", "type": "str"},
                {"key": "professional_summary", "label": "Professional Summary", "type": "str"},
                {"key": "core_competencies", "label": "Core Competencies", "type": "str"},
                {"key": "experience", "label": "Experience", "type": "str"},
                {"key": "prior_experience", "label": "Prior Experience", "type": "str"},
                {"key": "education_certifications", "label": "Education & Certifications", "type": "str"},
                {"key": "technical_skills", "label": "Technical Skills", "type": "str"},
            ],
        },
    },
    "companies": {
        "list": {
            "watch_list": [
                {"key": "company_name", "label": "Company", "sortable": True},
                {"key": "short_name", "label": "Short Name", "sortable": True},
                {"key": "company_website", "label": "Website", "sortable": True},
                {"key": "state", "label": "State", "sortable": True},
                {"key": "last_scan_at", "label": "Last Scanned", "sortable": True, "defaultDesc": True, "type": "datetime"},
            ],
            "new_list": [
                {"key": "company_name", "label": "Company", "sortable": True},
                {"key": "short_name", "label": "Short Name", "sortable": True},
                {"key": "company_website", "label": "Website", "sortable": True},
                {"key": "state", "label": "State", "sortable": True},
                {"key": "state_updated_at", "label": "State Updated", "sortable": True, "defaultDesc": True, "type": "datetime"},
                {"key": "batch_id", "label": "Batch ID", "sortable": True},
                {"key": "created_at", "label": "Created", "sortable": True, "type": "datetime"},
            ],
            "inactive_list": [
                {"key": "company_name", "label": "Company", "sortable": True},
                {"key": "short_name", "label": "Short Name", "sortable": True},
                {"key": "state", "label": "State", "sortable": True},
                {"key": "state_updated_at", "label": "State Updated", "sortable": True, "defaultDesc": True, "type": "datetime"},
            ],
            "ignored": [
                {"key": "company_name", "label": "Company", "sortable": True},
                {"key": "short_name", "label": "Short Name", "sortable": True},
                {"key": "prefilter_company_notes", "label": "Ignore Reason", "sortable": True, "expandable": True},
                {"key": "state_updated_at", "label": "Ignored At", "sortable": True, "defaultDesc": True, "type": "datetime"},
            ],
            "watch_history": [
                {"key": "company_name", "label": "Company", "sortable": True},
                {"key": "short_name", "label": "Short Name", "sortable": True},
                {"key": "scan_completed_at", "label": "Scan Time", "sortable": True, "defaultDesc": True, "type": "datetime"},
                {"key": "new", "label": "New Jobs", "sortable": True},
                {"key": "total_found", "label": "Total Found", "sortable": True},
                {"key": "duplicates", "label": "Duplicates", "sortable": True},
                {"key": "title_mismatch", "label": "Title mismatch", "sortable": True},
                {"key": "status", "label": "Status", "sortable": True},
                {"key": "batch_id", "label": "Batch", "sortable": True},
            ],
        },
    },
    "jobs": {},
}


# ---------------------------------------------------------------------------
# BUILD_CONFIG: default visual tokens (v07-oriented), resume/cover section
# formatting metadata, and documentation-first JSON contracts for artifacts.
# Candidate-specific accent / style overrides merge over default_style at
# render time (see AST-297); this block is the base only.
#
# Resume HTML typography/color defaults live below only — parity was validated against a legacy local ResumeSite snapshot (not committed).
# ---------------------------------------------------------------------------
BUILD_CONFIG = {
    "default_style": {
        "fonts": {
            "heading_stack": '"Helvetica Neue", Helvetica, Arial, sans-serif',
            "body_stack": 'Palatino, "Palatino Linotype", "Book Antiqua", serif',
            "list_stack": '"Helvetica Neue", Helvetica, Arial, sans-serif',
            "mono_stack": "'IBM Plex Mono', 'Consolas', monospace",
        },
        "type_scale": {
            "document_title": {
                "size_pt": 22,
                "weight": 700,
                "line_height": 1.15,
                "tracking_em": 0.02,
            },
            "candidate_name_line": {
                "size_pt": 18,
                "weight": 700,
                "line_height": 1.2,
            },
            "candidate_title_line": {
                "size_pt": 12,
                "weight": 600,
                "line_height": 1.25,
            },
            "contact_line": {
                "size_pt": 10,
                "weight": 400,
                "line_height": 1.35,
            },
            "section_heading": {
                "size_pt": 11,
                "weight": 700,
                "line_height": 1.2,
                "text_transform": "uppercase",
                "letter_spacing_em": 0.08,
            },
            "body": {
                "size_pt": 10,
                "weight": 400,
                "line_height": 1.45,
            },
            "body_tight": {
                "size_pt": 10,
                "weight": 400,
                "line_height": 1.35,
            },
            "caption": {
                "size_pt": 9,
                "weight": 400,
                "line_height": 1.35,
            },
        },
        "spacing_scale": {
            "page_gutter_pt": 36,
            "section_before_pt": 14,
            "section_after_pt": 8,
            "block_before_pt": 8,
            "block_after_pt": 6,
            "list_item_gap_pt": 4,
            "paragraph_gap_pt": 6,
        },
        "colors": {
            "ink": "#111111",
            "muted": "#555555",
            "rule": "#c8c8c8",
            "surface": "#ffffff",
            "default_accent": "#3c2c6e",
            "default_header": "#3c2c6e",
            "page_background": "#f5f5f5",
        },
        # Visually hidden ATS keyword strip — builder emits class ats-keywords; all knobs here (§1.4).
        "ats_keyword_block": {
            "font_size_px": 1,
            "line_height": 1.0,
            "text_color": "#f5f5f5",
            "background": "#f5f5f5",
            "position": "absolute",
            "left_px": -9999,
            "width_px": 1,
            "height_px": 1,
            "overflow": "hidden",
        },
        "section_heading_decoration": {
            "style": "flanking_horizontal_rules",
            "rule_thickness_pt": 0.75,
            "gap_between_rule_and_text_pt": 8,
            "rule_minimum_length_pt": 24,
            "vertical_align_with_cap_height": True,
        },
        "print": {
            "page_margin_top_mm": 12,
            "page_margin_right_mm": 12,
            "page_margin_bottom_mm": 12,
            "page_margin_left_mm": 12,
            "orphans_min_lines": 2,
            "widows_min_lines": 2,
            "avoid_break_inside_section_ids": [
                "experience",
                "education_certifications",
                "cover_letter_body",
            ],
        },
    },
    # Curated dark swatches for candidate base_resume accent (AST-297); served via /api/system/ui_config.
    "accent_palette": [
        "#1a1a2e",
        "#16213e",
        "#0f3460",
        "#1e3a5f",
        "#2d4a3e",
        "#3c2c6e",
        "#4a3728",
        "#3d2b3d",
        "#2b2b2b",
        "#111111",
    ],
    # Keys align to DATA_SHAPES["candidates"]["detail"]["base_resume_structure"]
    # keys and TASK_CONFIG["craft_resume_base"] field names (professional_summary
    # not "summary"; core_competencies not "competencies"). Cover keys mirror
    # artifact_shapes["cover_letter"] field names for one naming spine.
    #
    # supported_sections[*]["heading_level"]: key into default_style["type_scale"]
    # for the section title row's typography, or "none" when there is no separate
    # title line — not an HTML h1/h2 depth. Builder / AST-297 may wrap stricter types.
    "supported_sections": {
        "candidate_name": {
            "heading_level": "candidate_name_line",
            "body_kind": "prose",
            "page_break_policy": "keep_with_next",
        },
        "candidate_title": {
            "heading_level": "none",
            "body_kind": "prose",
            "page_break_policy": "keep_with_next",
        },
        "candidate_contact_detail": {
            "heading_level": "none",
            "body_kind": "prose",
            "page_break_policy": "normal",
        },
        "professional_summary": {
            "heading_level": "section_heading",
            "body_kind": "prose",
            "page_break_policy": "avoid_split",
        },
        "core_competencies": {
            "heading_level": "section_heading",
            "body_kind": "prose",
            "page_break_policy": "avoid_split",
        },
        "experience": {
            "heading_level": "section_heading",
            "body_kind": "prose",
            "page_break_policy": "avoid_split",
        },
        "prior_experience": {
            "heading_level": "section_heading",
            "body_kind": "prose",
            "page_break_policy": "avoid_split",
        },
        "education_certifications": {
            "heading_level": "section_heading",
            "body_kind": "prose",
            "page_break_policy": "avoid_split",
        },
        "technical_skills": {
            "heading_level": "section_heading",
            "body_kind": "prose",
            "page_break_policy": "avoid_split",
        },
        "publications_articles": {
            "heading_level": "section_heading",
            "body_kind": "prose",
            "page_break_policy": "normal",
            "implementation_status": "reserved",
        },
        # Logical slices of artifact_shapes["cover_letter"] (field names re_line, body, signature).
        "cover_letter_re_line": {
            "heading_level": "none",
            "body_kind": "prose",
            "page_break_policy": "keep_with_next",
        },
        "cover_letter_body": {
            "heading_level": "none",
            "body_kind": "prose",
            "page_break_policy": "normal",
        },
        "cover_letter_signature": {
            "heading_level": "none",
            "body_kind": "prose",
            "page_break_policy": "normal",
        },
    },
    # resume_content: documents known section ids; runtime allowed keys are per-candidate structure subset.
    # cover_letter: canonical Subject/Letter; legacy tasks may still output re_line/body until prompts update.
    "artifact_shapes": {
        "resume_content": {
            "candidate_name": {"type": "str", "required": True},
            "candidate_title": {"type": "str", "required": True},
            "candidate_contact_detail": {"type": "str", "required": True},
            "professional_summary": {"type": "str", "required": True},
            "core_competencies": {"type": "str", "required": True},
            "experience": {"type": "str", "required": True},
            "prior_experience": {"type": "str", "required": False},
            "education_certifications": {"type": "str", "required": False},
            "technical_skills": {"type": "str", "required": False},
        },
        "cover_letter": {
            "Subject": {"type": "str", "required": True},
            "Letter": {"type": "str", "required": True},
            "signature": {"type": "str", "required": False},
        },
    },
    # AST-300 / AST-370 / AST-450: dispatch entry TASK_CONFIG key only; further hops via run_next.
    "resume_artifact_chain": {
        "first_task_key": "contemplate_job",
        "hop_task_keys": _RESUME_ARTIFACT_HOP_TASK_KEYS,
    },
    # AST-301 / AST-368 / AST-450: dispatch entry TASK_CONFIG key only; further hops via run_next.
    "cover_letter_artifact_chain": {
        "first_task_key": "draft_cover_letter",
    },
}

# AST-595: compound BUILD_ARTIFACTS.<task_key> helpers (hop order from BUILD_CONFIG).
def resume_artifact_hop_task_keys() -> tuple[str, ...]:
    chain = BUILD_CONFIG.get("resume_artifact_chain") or {}
    keys = chain.get("hop_task_keys")
    if not keys:
        raise KeyError("BUILD_CONFIG resume_artifact_chain.hop_task_keys missing")
    return tuple(keys)


def resume_artifact_compound_state(task_key: str) -> str:
    return f"{RESUME_ARTIFACT_COMPOUND_PREFIX}{task_key}"


def resume_artifact_first_compound_state() -> str:
    return resume_artifact_compound_state(resume_artifact_hop_task_keys()[0])


def resume_artifact_next_compound_state(task_key: str) -> str | None:
    keys = resume_artifact_hop_task_keys()
    try:
        idx = keys.index(task_key)
    except ValueError:
        return None
    if idx + 1 >= len(keys):
        return None
    return resume_artifact_compound_state(keys[idx + 1])


def parse_resume_artifact_hop(state: str) -> str | None:
    st = state or ""
    if not st.startswith(RESUME_ARTIFACT_COMPOUND_PREFIX):
        return None
    return st[len(RESUME_ARTIFACT_COMPOUND_PREFIX):]


def is_resume_artifact_in_progress(state: str) -> bool:
    return (state or "").startswith(RESUME_ARTIFACT_COMPOUND_PREFIX)


def all_resume_artifact_compound_states() -> tuple[str, ...]:
    return tuple(resume_artifact_compound_state(tk) for tk in resume_artifact_hop_task_keys())


_RAH = resume_artifact_hop_task_keys()
assert len(_RAH) >= 1
assert all(tk in TASK_CONFIG for tk in _RAH)
assert all((TASK_CONFIG[tk] or {}).get("entity_type") == "job" for tk in _RAH)

# Per-candidate resume section catalog (AST-517); persistence on artifacts.resume_structure.
RESUME_STRUCTURE_CONTACT_SECTION_IDS = (
    "candidate_name",
    "candidate_title",
    "candidate_contact_detail",
)
RESUME_STRUCTURE_KNOWN_SECTION_IDS = (
    "candidate_name",
    "candidate_title",
    "candidate_contact_detail",
    "professional_summary",
    "core_competencies",
    "experience",
    "prior_experience",
    "education_certifications",
    "technical_skills",
)
RESUME_STRUCTURE_DEFAULT = {
    "sections": {
        "candidate_name": {
            "id": "candidate_name",
            "title": "Candidate Name",
            "enabled": True,
            "order": 0,
            "job_agent_editable": False,
        },
        "candidate_title": {
            "id": "candidate_title",
            "title": "Candidate Title",
            "enabled": True,
            "order": 1,
            "job_agent_editable": False,
        },
        "candidate_contact_detail": {
            "id": "candidate_contact_detail",
            "title": "Candidate Contact Detail",
            "enabled": True,
            "order": 2,
            "job_agent_editable": False,
        },
        "professional_summary": {
            "id": "professional_summary",
            "title": "Professional Summary",
            "enabled": True,
            "order": 3,
            "job_agent_editable": True,
        },
        "core_competencies": {
            "id": "core_competencies",
            "title": "Core Competencies",
            "enabled": True,
            "order": 4,
            "job_agent_editable": True,
        },
        "experience": {
            "id": "experience",
            "title": "Experience",
            "enabled": True,
            "order": 5,
            "job_agent_editable": True,
        },
        "prior_experience": {
            "id": "prior_experience",
            "title": "Prior Experience",
            "enabled": True,
            "order": 6,
            "job_agent_editable": True,
        },
        "education_certifications": {
            "id": "education_certifications",
            "title": "Education & Certifications",
            "enabled": True,
            "order": 7,
            "job_agent_editable": True,
        },
        "technical_skills": {
            "id": "technical_skills",
            "title": "Technical Skills",
            "enabled": True,
            "order": 8,
            "job_agent_editable": True,
        },
    },
}


# AST-575: pronoun preference + resolved forms (parent AST-573).
PRONOUN_PREFERENCE_DEFAULT = "they/them"
PRONOUN_PREFERENCE_OPTIONS: tuple[str, ...] = (
    "they/them",
    "she/her",
    "he/him",
    "ze/zir",
    "e/eir",
)
PRONOUN_FORMS: dict[str, dict[str, str]] = {
    "they/them": {"THEY": "they", "THEIR": "their", "THEIRS": "theirs", "THEM": "them", "THEMSELF": "themselves"},
    "she/her": {"THEY": "she", "THEIR": "her", "THEIRS": "hers", "THEM": "her", "THEMSELF": "herself"},
    "he/him": {"THEY": "he", "THEIR": "his", "THEIRS": "his", "THEM": "him", "THEMSELF": "himself"},
    "ze/zir": {"THEY": "ze", "THEIR": "zir", "THEIRS": "zirs", "THEM": "zir", "THEMSELF": "zirself"},
    "e/eir": {"THEY": "e", "THEIR": "eir", "THEIRS": "eirs", "THEM": "em", "THEMSELF": "emself"},
}

# ---------------------------------------------------------------------------
# TOKEN_SOURCES: authoritative registry of tokens available in prompt content.
# Prompt authors use {$TOKEN_NAME} syntax; resolve_tokens() replaces them at runtime.
# Adding a new token = adding one entry here, no code change needed.
# ---------------------------------------------------------------------------
TOKEN_SOURCES = {
    # profile (identity / contact)
    "FIRST_NAME":           {"source": "candidate", "path": "profile.first"},
    "LAST_NAME":            {"source": "candidate", "path": "profile.last"},
    "CONTACT_EMAIL":        {"source": "candidate", "path": "profile.contact_email"},
    "REPLY_EMAIL":          {"source": "candidate", "path": "profile.reply_email"},
    "PHONE":                {"source": "candidate", "path": "profile.phone"},
    "LOCATION":             {"source": "candidate", "path": "profile.location"},
    "GITHUB":               {"source": "candidate", "path": "profile.github"},
    "LINKEDIN_URL":         {"source": "candidate", "path": "profile.linkedin_url"},

    # context (candidate-provided, unaltered)
    "STARTING_RESUME_TEXT": {"source": "candidate", "path": "context.starting_resume_text"},
    "LINKEDIN_PROFILE_TEXT": {"source": "candidate", "path": "context.linkedin_profile_text"},
    "SAMPLE_COVER_TEXT":    {"source": "candidate", "path": "context.sample_cover_text"},
    "STRENGTHS":            {"source": "candidate", "path": "context.strengths"},
    "PRIORITIES":           {"source": "candidate", "path": "context.priorities"},
    "DEAL_BREAKERS":        {"source": "candidate", "path": "context.deal_breakers"},
    "BACKSTORY":            {"source": "candidate", "path": "context.backstory"},
    "WRITING_PREFERENCES":  {"source": "candidate", "path": "context.writing_preferences"},
    "TITLE_PATTERNS":       {"source": "candidate", "path": "profile.title_patterns"},
    "REASON_CODES":         {"source": "candidate", "path": "profile.reason_codes"},
    "COVER_LETTER_SIGNATURE": {"source": "candidate", "path": "profile.cover_letter_signature"},
    "THEY":     {"source": "pronoun"},
    "THEIR":    {"source": "pronoun"},
    "THEIRS":   {"source": "pronoun"},
    "THEM":     {"source": "pronoun"},
    "THEMSELF": {"source": "pronoun"},

    # artifacts (AI-produced / human-revised)
    "BASE_RESUME":          {"source": "candidate", "path": "artifacts.base_resume", "serialize": "resume_sections_json"},
    "BIO_SUMMARY":          {"source": "candidate", "path": "context.bio_summary"},
    # Resolved from company_search_terms table via agent overlay (AST-525); path kept for registry.
    "COMPANY_SEARCH_TERMS": {"source": "candidate", "path": "artifacts.company_search_terms"},
    # Resolved from rubric_vector rows for active task owner (AST-723).
    "RUBRIC_VECTORS":       {"source": "rubric"},

    # config-driven (resolved via named function, not dot-path)
    "RESPONSE_SCHEMA":      {"source": "config", "resolver": "stringify_response_schema"},

    # output-type-driven (resolved from ASTRAL_CONFIG["output_types"][task output_type])
    "OUTPUT_INSTRUCTIONS":  {"source": "output_type", "field": "payload_instructions"},

    # chain/runtime — values from resolve_tokens(..., chain_context=); AST-303 / AST-455
    # Caller-prefixed keys pass resolved segment text hop-to-hop (replaces CACHE_BLOCK_* / AST-304).
    "CALLER_RESPONSE":    {"source": "chain"},
    "CALLER_SYSTEM":      {"source": "chain"},
    "CALLER_CACHE_A":    {"source": "chain"},
    "CALLER_CACHE_B":    {"source": "chain"},
    "CALLER_CACHE_C":    {"source": "chain"},
    "CALLER_CACHE_D":    {"source": "chain"},
    "SELECTED_AGENT":     {"source": "chain"},
    # AST-469: visible listing text from locate hop → parse_job_list (chain_context).
    "JOB_LIST_VISIBLE": {"source": "chain"},

    # AST-513: job-scoped artifact prompt tokens (values from job_context dict).
    "VISIBLE_JD":    {"source": "job"},
    "ANALYSIS_JD":   {"source": "job"},
    "ANALYSIS_DO":   {"source": "job"},
    "ANALYSIS_GET":  {"source": "job"},
    "ANALYSIS_LIKE": {"source": "job"},
    "RESUME_SECTION_CATALOG": {"source": "job"},
}

# AST-513: phase token → persisted job_data grades_key + rubric artifact key.
JOB_TOKEN_CONFIG = {
    "analysis_phases": {
        "ANALYSIS_JD":   {"grades_key": "jd_grades",   "rubric_artifact": "jobdesc_rubric", "rubric_owner_task_key": "evaluate_jd"},
        "ANALYSIS_DO":   {"grades_key": "do_grades",   "rubric_artifact": "do_rubric", "rubric_owner_task_key": "grade_do"},
        "ANALYSIS_GET":  {"grades_key": "get_grades",  "rubric_artifact": "get_rubric", "rubric_owner_task_key": "grade_get"},
        "ANALYSIS_LIKE": {"grades_key": "like_grades", "rubric_artifact": "like_rubric", "rubric_owner_task_key": "grade_like"},
    },
}


def get_tokens() -> list:
    """Return sorted list of token names available for use in prompt content as {$TOKEN_NAME}."""
    return sorted(TOKEN_SOURCES.keys())


def get_manage_tasks_chain_tokens() -> list:
    """Sorted Manage Tasks chain-picker tokens ({% raw %}{$CALLER_*}{% endraw %}, SELECTED_AGENT). Registry excludes nocache/user shims."""
    return sorted(
        k for k, spec in TOKEN_SOURCES.items() if spec.get("source") == "chain"
    )


def get_manage_agents_tokens() -> list:
    """Sorted Manage Agents picker tokens — registry minus chain/hop tokens (AST-632)."""
    chain = set(get_manage_tasks_chain_tokens())
    return sorted(k for k in get_tokens() if k not in chain)


CALLER_HOP_TOKEN_NAMES: tuple[str, ...] = tuple(
    k for k in get_manage_tasks_chain_tokens() if k.startswith("CALLER_")
)


def stringify_response_schema(task_key: str) -> str:
    """Return the response_schema as a nested envelope for prompt insertion.
    For encoded output types, agent_payload is shown as a compact string example.
    For all others: { agent_performance: {...}, agent_payload: {...task fields...} }"""
    task_cfg = TASK_CONFIG.get(task_key, {})
    schema = task_cfg.get("response_schema")
    if not schema:
        return ""
    output_type = task_cfg.get("output_type", "")
    if "_encoded" in output_type:
        if output_type == "grades_encoded_notes":
            example = "000|ERC3|MEA4|PGA4|optional notes after grades"
        elif output_type == "grades_encoded_prefilter_links":
            example = "000|ERC2|MEA3|PGA2|[13]|[3,6,19]"
        elif "_meta" in output_type:
            example = "000|ERC3|MEA4|PGA5|2983982372|Job Title|https://example.com/jobs/123"
        else:
            example = "000|ERC2|MEA3|PGA2"
        payload: object = example
    else:
        payload = _schema_to_example(schema)
    envelope = {
        "agent_performance": _schema_to_example(BASE_SCHEMA),
        "agent_payload": payload,
    }
    return json.dumps(envelope, indent=2)


def _schema_to_example(schema: dict) -> object:
    """Recursively convert a response_schema definition into a JSON example shape."""
    result = {}
    for key, spec in schema.items():
        t = spec.get("type", "str")
        if t == "str":
            enum = spec.get("enum")
            result[key] = " | ".join(enum) if enum else f"<{key}>"
        elif t == "int":
            result[key] = 0
        elif t == "bool":
            result[key] = True
        elif t == "list":
            items_schema = spec.get("items_schema")
            result[key] = [_schema_to_example(items_schema)] if items_schema else [f"<{key} item>"]
        elif t in ("object", "dict"):
            result[key] = {"<key>": "<value>"}
        else:
            result[key] = f"<{key}>"
    return result


def _walk_dot_path(obj: object, path: str) -> object:
    """Walk a dot-delimited path into nested dicts. Returns None on miss."""
    for segment in path.split("."):
        if not isinstance(obj, dict):
            return None
        obj = obj.get(segment)
    return obj


def _pronoun_preference_key(candidate_data: dict) -> str:
    raw = _walk_dot_path(candidate_data, "profile.pronoun_preference")
    if not isinstance(raw, str):
        return PRONOUN_PREFERENCE_DEFAULT
    key = raw.strip()
    return key if key in PRONOUN_FORMS else PRONOUN_PREFERENCE_DEFAULT


from src.utils.formatting import value_to_str as _value_to_str


_CONFIG_RESOLVERS = {
    "stringify_response_schema": stringify_response_schema,
}

_TOKEN_RE = re.compile(r"\{\$([A-Z_]+)\}")


def chain_context_selected_agent(system_prompt: Optional[str] = None) -> Dict[str, str]:
    """Build chain_context with only {$SELECTED_AGENT} (AST-304). AST-303 may merge more keys into this dict."""
    return {"SELECTED_AGENT": system_prompt or ""}


def _caller_key_status_line(caller_map: Dict[str, str]) -> str:
    """Compact populated/empty summary for CALLER_HOP tokens (registry order)."""
    parts: list[str] = []
    for name in CALLER_HOP_TOKEN_NAMES:
        stripped = (caller_map.get(name) or "").strip()
        if stripped:
            parts.append(f"{name}=populated(len={len(stripped)})")
        else:
            parts.append(f"{name}=empty")
    return ",".join(parts)


def resolve_tokens(
    text: str,
    candidate_data: dict,
    task_key: str,
    chain_context: Optional[Dict[str, str]] = None,
    job_context: Optional[Dict[str, str]] = None,
    *,
    chain_entry: bool = False,
    parent_task_key: Optional[str] = None,
    parent_caller_summary: Optional[Dict[str, str]] = None,
) -> str:
    """Replace {$TOKEN_NAME} patterns in text using TOKEN_SOURCES registry.
    candidate_data: the parsed candidate_data dict (not the full DB row).
    chain_context: optional str values for tokens with source \"chain\" (e.g. SELECTED_AGENT, CALLER_RESPONSE).
    job_context: optional str values for tokens with source \"job\" (AST-513 artifact prompts).
    Unrecognized token names (absent from TOKEN_SOURCES) are left as-is for forward-compatibility."""
    def _replace(match: re.Match) -> str:
        name = match.group(1)
        spec = TOKEN_SOURCES.get(name)
        if spec is None:
            return match.group(0)
        if spec["source"] == "candidate":
            if spec.get("serialize") == "resume_sections_json":
                from src.core.candidate import format_base_resume_for_token
                out = format_base_resume_for_token(candidate_data)
                if not out:
                    _log.warning("Token {$%s} resolved to empty (path=%s, task=%s)", name, spec["path"], task_key)
                return out
            raw = _walk_dot_path(candidate_data, spec["path"])
            if raw is None or raw == "" or raw == []:
                _log.warning("Token {$%s} resolved to empty (path=%s, task=%s)", name, spec["path"], task_key)
            return _value_to_str(raw)
        if spec["source"] == "config":
            resolver = _CONFIG_RESOLVERS.get(spec.get("resolver", ""))
            return resolver(task_key) if resolver else ""
        if spec["source"] == "output_type":
            output_type_key = TASK_CONFIG.get(task_key, {}).get("output_type", "")
            entry = ASTRAL_CONFIG.get("output_types", {}).get(output_type_key, {})
            raw = entry.get(spec["field"], "")
            return _value_to_str(raw) if raw else ""
        if spec["source"] == "chain":
            raw = (chain_context or {}).get(name)
            if raw is None or raw == "" or raw == []:
                if name in CALLER_HOP_TOKEN_NAMES:
                    if not chain_entry:
                        summary_src = parent_caller_summary if parent_caller_summary is not None else (chain_context or {})
                        summary = _caller_key_status_line(summary_src)
                        _log.warning(
                            "Token {$%s} resolved to empty on mid-chain hop (task=%s, parent=%s, parent_caller=%s)",
                            name,
                            task_key,
                            parent_task_key or "",
                            summary,
                        )
                else:
                    _log.warning("Token {$%s} resolved to empty (chain_context, task=%s)", name, task_key)
            return _value_to_str(raw) if raw is not None else ""
        if spec["source"] == "job":
            raw = (job_context or {}).get(name)
            if raw is None or raw == "" or raw == []:
                _log.warning("Token {$%s} resolved to empty (job_context, task=%s)", name, task_key)
            return _value_to_str(raw) if raw is not None else ""
        if spec["source"] == "pronoun":
            pref = _pronoun_preference_key(candidate_data)
            return PRONOUN_FORMS[pref][name]
        if spec["source"] == "rubric":
            from src.core.candidate import rubric_criteria_for_token

            owner = rubric_owner_task_key(task_key)
            if not owner:
                _log.warning("Token {$%s} unresolved — task %r has no rubric owner", name, task_key)
                return ""
            cid = (candidate_data or {}).get("_astral_candidate_id") or ""
            if not cid:
                _log.warning("Token {$%s} unresolved — missing candidate id (task=%s)", name, task_key)
                return ""
            return _value_to_str(rubric_criteria_for_token(cid, owner))
        return match.group(0)
    return _TOKEN_RE.sub(_replace, text)


def validate_value(allowed_list: list, value: object) -> None:
    """Raise ValueError if value is not in allowed_list. Caller supplies the list (e.g. from config)."""
    if value not in allowed_list:
        raise ValueError(f"Value {value!r} not in allowed list: {allowed_list}")
