#!/usr/bin/env python3
"""
Bootstrap migration: seed the first candidate record ('somerset') from existing local files.

Scripts are exempt from layer import rules (see ASTRAL_CODE_RULES.md section 3.3).
Imports directly from data, external, and utils as needed.

Idempotent: safe to re-run. Checks for existing candidate before insert.
Reusable: change CANDIDATE_ID and file paths to bootstrap additional candidates.
"""

import asyncio
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.database import save_candidate, get_candidate
from src.core.agent import do_task
from src.utils.config import ASTRAL_CONFIG, CANDIDATE_CONFIG

RESET = "--reset" in sys.argv
CANDIDATE_ID = "somerset"
CANDIDATE_DIR = ASTRAL_CONFIG["candidate_dir"]

# Files to read for bootstrap (resume is separate for parse_resume call)
RESUME_FILE = "resume_base.txt"
BOOTSTRAP_FILES = [
    "resume_base.txt",
    "linkedinprofile.txt",
    "private_history.txt",
    "preferences_template.txt",
    "astral_settings.txt",
]

INITIAL_CANDIDATE_DATA = {
    "profile": {
        "first": "Susan",
        "last": "Somerset",
        "contact_email": "susan@susansomerset.com",
    },
}


def read_file(filename: str) -> str:
    path = CANDIDATE_DIR / filename
    if not path.exists():
        print(f"  WARNING: {path} not found, skipping")
        return ""
    return path.read_text(encoding="utf-8")


async def run_bootstrap():
    existing = get_candidate(CANDIDATE_ID)
    if existing and RESET:
        print(f"Resetting candidate_data for '{CANDIDATE_ID}'...")
        save_candidate(CANDIDATE_ID, state=CANDIDATE_CONFIG["initial_state"], candidate_data={}, merge=False)
        existing = get_candidate(CANDIDATE_ID)
    if existing:
        print(f"Candidate '{CANDIDATE_ID}' already exists (state={existing['state']}). Updating...")
    else:
        print(f"Creating candidate '{CANDIDATE_ID}'...")
        save_candidate(CANDIDATE_ID, state=CANDIDATE_CONFIG["initial_state"], candidate_data=INITIAL_CANDIDATE_DATA)

    # Read resume for parse_resume call
    resume_text = read_file(RESUME_FILE)
    if not resume_text.strip():
        print("ERROR: resume_base.txt is empty, cannot parse resume")
        return

    # Read all files for bootstrap_candidate call
    all_content_parts = []
    for fname in BOOTSTRAP_FILES:
        content = read_file(fname)
        if content.strip():
            all_content_parts.append(f"=== {fname} ===\n{content}")
    all_content = "\n\n".join(all_content_parts)

    # Call 1: parse_resume - structured resume sections
    print("Calling parse_resume...")
    resume_result = await do_task(
        task_key="parse_resume",
        live_content=resume_text,
        index=CANDIDATE_ID,
    )
    if not resume_result or not resume_result.get("success"):
        print(f"ERROR: parse_resume failed: {resume_result.get('error') if resume_result else 'None'}")
        return
    resume_parsed = resume_result["parsed_response"]
    print(f"  parse_resume OK: {list(resume_parsed.keys())}")

    # Call 2: bootstrap_candidate - context text fields
    print("Calling bootstrap_candidate...")
    bootstrap_result = await do_task(
        task_key="bootstrap_candidate",
        live_content=all_content,
        index=CANDIDATE_ID,
    )
    if not bootstrap_result or not bootstrap_result.get("success"):
        print(f"ERROR: bootstrap_candidate failed: {bootstrap_result.get('error') if bootstrap_result else 'None'}")
        return
    bootstrap_parsed = bootstrap_result["parsed_response"]
    print(f"  bootstrap_candidate OK: {list(bootstrap_parsed.keys())}")

    # Nest into profile/context/artifacts groups
    merged_data = {
        **INITIAL_CANDIDATE_DATA,
        "context": {
            "starting_resume_text": resume_text,
            "linkedin_profile_text": read_file("linkedinprofile.txt"),
            **bootstrap_parsed,
        },
        "artifacts": {
            "base_resume": resume_parsed,
        },
    }
    save_candidate(CANDIDATE_ID, candidate_data=merged_data, merge=True)
    print(f"  Saved merged candidate_data ({len(merged_data)} keys)")

    # ACTIVE_SEARCH: bootstrap intent is a candidate usable for generation (AST-973)
    save_candidate(CANDIDATE_ID, state="ACTIVE_SEARCH")
    print(f"  State set to ACTIVE_SEARCH")

    # Link all company rows to this candidate
    from src.data.database import _get_connection, _ensure_company_schema, _ensure_company_candidate_fk
    conn = _get_connection()
    try:
        _ensure_company_schema(conn)
        _ensure_company_candidate_fk(conn)
        cur = conn.execute(
            "UPDATE company SET candidate_id = ? WHERE candidate_id IS NULL OR candidate_id = ''",
            (CANDIDATE_ID,),
        )
        conn.commit()
        print(f"  Linked {cur.rowcount} company rows to candidate '{CANDIDATE_ID}'")
    finally:
        conn.close()

    print("Bootstrap complete.")


if __name__ == "__main__":
    asyncio.run(run_bootstrap())
