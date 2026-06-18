#!/usr/bin/env python3
"""
Backfill rubric_vector rows from legacy candidate_data.artifacts JSON (AST-722).

Copies rubric criteria lists into rubric_vector with current=1. Idempotent per
(candidate_id, task_key). Optional purge removes legacy artifact keys after verify.

Usage:
  python scripts/migrations/backfill_rubric_vectors.py --dry-run
  python scripts/migrations/backfill_rubric_vectors.py
  python scripts/migrations/backfill_rubric_vectors.py --candidates susan,other
  python scripts/migrations/backfill_rubric_vectors.py --purge-artifacts --dry-run
  python scripts/migrations/backfill_rubric_vectors.py --purge-artifacts --confirm-purge
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data import database
from src.utils import rubric_text
from src.utils.config import ASTRAL_CONFIG, RUBRIC_CRITERIA_ARTIFACT_KEYS

_ARTIFACT_KEY_TO_TASK_KEY: Dict[str, str] = {
    "company_prefilter": "prefilter_company",
    "joblist_rubric": "qualify_job_listings",
    "jobdesc_rubric": "evaluate_jd",
    "do_rubric": "grade_do",
    "get_rubric": "grade_get",
    "like_rubric": "grade_like",
}

_COUNT_KEYS = (
    "candidates_scanned",
    "tasks_backfilled",
    "vectors_inserted",
    "skipped_existing",
    "skipped_no_agent_task",
    "errors",
    "would_insert",
)


def _empty_counts() -> Dict[str, int]:
    return {k: 0 for k in _COUNT_KEYS}


def _normalize_importance(raw: Any, ci: dict) -> int:
    default = int(ci["default_vector_importance"])
    lo, hi = int(ci["min"]), int(ci["max"])
    if raw is None:
        return default
    if isinstance(raw, bool):
        raise ValueError("importance must be an integer, not a boolean")
    if isinstance(raw, int):
        n = raw
    elif isinstance(raw, float):
        if not raw.is_integer():
            raise ValueError("importance must be a whole number")
        n = int(raw)
    elif isinstance(raw, str):
        s = raw.strip()
        if s.isdigit():
            n = int(s)
        else:
            raise ValueError("importance must be an integer from 1 to 10")
    else:
        raise ValueError("importance must be an integer from 1 to 10")
    if n < lo or n > hi:
        n = max(lo, min(hi, n))
    return n


def _criterion_from_artifact_item(item: dict, idx: int, ci: dict) -> Tuple[str, str, str, int, str]:
    if not isinstance(item, dict):
        raise ValueError(f"criterion {idx + 1} must be an object")
    code = (item.get("code") or "").strip() or f"V{idx + 1:02d}"
    label = (item.get("label") or "").strip() or code
    content = item.get("content") or ""
    if not str(content).strip():
        raise ValueError("criterion content is empty")
    importance = _normalize_importance(item.get("importance"), ci)
    fingerprint = rubric_text.rubric_vector_content_fingerprint(label, content)
    return code, label, content, importance, fingerprint


def backfill_candidate_rubric_vectors(candidate_id: str, *, dry_run: bool) -> Dict[str, int]:
    counts = _empty_counts()
    counts["candidates_scanned"] = 1
    candidate = database.get_candidate(candidate_id)
    if not candidate:
        print(f"[candidate {candidate_id}] not found — skip")
        return counts
    if candidate.get("state") == "DELETED":
        print(f"[candidate {candidate_id}] DELETED — skip")
        return counts

    cd = candidate.get("candidate_data") or {}
    arts = cd.get("artifacts") if isinstance(cd, dict) else None
    if not isinstance(arts, dict):
        return counts

    ci = ASTRAL_CONFIG["consult_importance"]
    for artifact_key in RUBRIC_CRITERIA_ARTIFACT_KEYS:
        if artifact_key not in arts:
            continue
        val = arts[artifact_key]
        if val is None:
            continue
        if not isinstance(val, list):
            print(f"[candidate {candidate_id}] artifact {artifact_key!r} not a list — skip")
            counts["errors"] += 1
            continue

        task_key = _ARTIFACT_KEY_TO_TASK_KEY.get(artifact_key)
        if not task_key:
            print(f"[candidate {candidate_id}] no task_key map for {artifact_key!r} — skip")
            counts["errors"] += 1
            continue

        if database.count_rubric_vectors_for_candidate_task(candidate_id, task_key) > 0:
            counts["skipped_existing"] += 1
            continue

        task_key_uuid = database.get_current_agent_task_uuid(task_key)
        if not task_key_uuid:
            print(
                f"[candidate {candidate_id}] no current agent_task for {task_key!r} "
                f"(artifact {artifact_key!r}) — skip"
            )
            counts["skipped_no_agent_task"] += 1
            continue

        inserted_for_task = 0
        for idx, item in enumerate(val):
            try:
                code, label, content, importance, fingerprint = _criterion_from_artifact_item(
                    item, idx, ci
                )
            except ValueError as e:
                print(
                    f"[candidate {candidate_id}] {artifact_key!r} vector {idx + 1}: {e}"
                )
                counts["errors"] += 1
                continue
            if dry_run:
                counts["would_insert"] += 1
                inserted_for_task += 1
                continue
            database.insert_rubric_vector_row(
                candidate_id=candidate_id,
                task_key=task_key,
                task_key_uuid=task_key_uuid,
                code=code,
                label=label,
                content=content,
                importance=importance,
                content_fingerprint=fingerprint,
            )
            counts["vectors_inserted"] += 1
            inserted_for_task += 1

        if inserted_for_task:
            counts["tasks_backfilled"] += 1
            action = "would insert" if dry_run else "inserted"
            print(
                f"[candidate {candidate_id}] {task_key}: {action} {inserted_for_task} vector(s)"
            )

    return counts


def _merge_counts(total: Dict[str, int], part: Dict[str, int]) -> None:
    for k in _COUNT_KEYS:
        total[k] += part.get(k, 0)


def run_backfill(dry_run: bool, candidates: Optional[List[str]]) -> Dict[str, int]:
    totals = _empty_counts()
    if candidates:
        ids = candidates
    else:
        ids = [
            c["astral_candidate_id"]
            for c in database.list_candidates()
            if c.get("state") != "DELETED"
        ]

    if dry_run:
        print("=== DRY RUN — no DB writes ===")

    for cid in ids:
        _merge_counts(totals, backfill_candidate_rubric_vectors(cid, dry_run=dry_run))

    print("\n=== Backfill summary ===")
    for k in _COUNT_KEYS:
        print(f"  {k}: {totals[k]}")
    return totals


def purge_rubric_artifacts(candidate_ids: List[str], *, dry_run: bool) -> Dict[str, int]:
    counts = {"candidates_scanned": 0, "candidates_purged": 0, "keys_removed": 0}
    for cid in candidate_ids:
        counts["candidates_scanned"] += 1
        candidate = database.get_candidate(cid)
        if not candidate or candidate.get("state") == "DELETED":
            continue
        cd = candidate.get("candidate_data") or {}
        arts = cd.get("artifacts") if isinstance(cd, dict) else None
        if not isinstance(arts, dict):
            continue
        would_remove = [k for k in RUBRIC_CRITERIA_ARTIFACT_KEYS if k in arts]
        if not would_remove:
            continue
        if dry_run:
            print(f"[candidate {cid}] DRY RUN — would remove keys: {', '.join(would_remove)}")
            counts["candidates_purged"] += 1
            counts["keys_removed"] += len(would_remove)
            continue
        removed = database.purge_legacy_rubric_artifact_keys(cid)
        if removed:
            print(f"[candidate {cid}] removed keys: {', '.join(removed)}")
            counts["candidates_purged"] += 1
            counts["keys_removed"] += len(removed)
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill rubric_vector from artifact JSON (AST-722)")
    parser.add_argument("--dry-run", action="store_true", help="Report only; no writes")
    parser.add_argument("--candidates", type=str, default="", help="Comma-separated candidate ids")
    parser.add_argument(
        "--purge-artifacts",
        action="store_true",
        help="Remove legacy rubric keys from candidate_data.artifacts",
    )
    parser.add_argument(
        "--confirm-purge",
        action="store_true",
        help="Required with --purge-artifacts (non-dry-run) to execute deletes",
    )
    args = parser.parse_args()

    candidates: Optional[List[str]] = None
    if args.candidates.strip():
        candidates = [c.strip() for c in args.candidates.split(",") if c.strip()]

    if args.purge_artifacts:
        if not args.dry_run and not args.confirm_purge:
            print(
                "ERROR: --purge-artifacts requires --confirm-purge (or use --dry-run). "
                "Run only after AC#9 verification AND AST-723 read-switch on origin/ftr."
            )
            sys.exit(1)
        if not args.dry_run:
            print(
                "WARNING: purge removes legacy rubric JSON from candidate_data.artifacts.\n"
                "Run only after AC#9 backfill verification AND AST-723 read-switch is on origin/ftr."
            )
        ids = candidates or [
            c["astral_candidate_id"]
            for c in database.list_candidates()
            if c.get("state") != "DELETED"
        ]
        if args.dry_run:
            print("=== DRY RUN — purge preview only ===")
        counts = purge_rubric_artifacts(ids, dry_run=args.dry_run)
        print("\n=== Purge summary ===")
        for k, v in counts.items():
            print(f"  {k}: {v}")
        return

    run_backfill(dry_run=args.dry_run, candidates=candidates)


if __name__ == "__main__":
    main()
