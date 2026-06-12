"""
scripts/migrate_encoded_agent_data.py

One-time migration: update RESPONSE blocks in agent_data for encode-decode tasks
(qualify_job_listings, evaluate_jd) from raw encoded format to decoded JSON.

qualify_job_listings: parses encoded lines, looks up astral_job_id from job table by company_job_id.
evaluate_jd:         extracts [astral_job_id=xxx] markers from NO_CACHE block to reconstruct batch_entities.

Usage:
    python scripts/migrate_encoded_agent_data.py [--apply] [--task {qualify_job_listings,evaluate_jd,both}]

Default is dry-run. Pass --apply to write changes to the DB.
"""
import argparse, json, re, sqlite3, sys, zlib, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional
from src.utils.config import ASTRAL_CONFIG

DB_PATH = os.environ.get("DB_PATH", "data/astral.db")

# Grade segment: 2-char code + grade letter + confidence digit (AST-357), e.g. "TMA3", "SRX0"
_valid_grades = "".join(ASTRAL_CONFIG.get("valid_grades", ["A", "B", "C", "D", "F", "X"]))
_GRADE_SEG = re.compile(rf"^[A-Z]{{2}}[{_valid_grades}][0-5]$")
_ASTRAL_ID_RE = re.compile(r"\[astral_job_id=([^\]]+)\]")


def _compress(text: str) -> bytes:
    return zlib.compress(text.encode("utf-8"))


def _decompress(value) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, bytes):
        return zlib.decompress(value).decode("utf-8")
    return value  # legacy uncompressed TEXT


# ---------------------------------------------------------------------------
# Payload extraction — parse JSON envelope, return agent_payload as a string.
# Returns None if block is already decoded or has no encodable payload.
# ---------------------------------------------------------------------------

_FENCE_RE = re.compile(r'^```[a-z]*\s*', re.MULTILINE)

def _extract_payload_str(raw_text: str) -> Optional[str]:
    # Strip markdown code fences (```json ... ```) that Anthropic wraps around JSON responses
    text = raw_text.strip()
    if text.startswith("```"):
        text = _FENCE_RE.sub("", text).rstrip("`").strip()
    try:
        parsed = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None

    # Already decoded ({"jobs": [...]})
    if isinstance(parsed, dict) and "jobs" in parsed:
        return None

    payload = parsed.get("agent_payload")
    if payload is None:
        return None
    if isinstance(payload, list):
        payload = "\n".join(str(item) for item in payload)
    if not isinstance(payload, str) or not payload.strip():
        return None
    return payload


# ---------------------------------------------------------------------------
# qualify_job_listings decoder
# Parses encoded lines; looks up astral_job_id from job table by company_job_id.
# Lines where company_job_id has no DB match get astral_job_id=None.
# ---------------------------------------------------------------------------

def _decode_qualify(payload_str: str, conn: sqlite3.Connection) -> dict:
    jobs = []
    for line in (ln for ln in payload_str.splitlines() if ln.strip()):
        fields = [f.strip() for f in line.split("|")]
        try:
            int(fields[0])  # validate position field
        except (ValueError, IndexError):
            continue

        grades, meta = [], []
        for f in fields[1:]:
            (grades if _GRADE_SEG.match(f) else meta).append(f)

        company_job_id = meta[0] if meta else None
        job_title      = meta[1] if len(meta) > 1 else None
        job_link       = meta[2] if len(meta) > 2 else None
        job_data = (
            {k.strip(): (v.strip() or None) for field in meta[3:] if ":" in field for k, v in [field.split(":", 1)]}
            if meta[3:] else None
        )

        astral_job_id = None
        if company_job_id:
            row = conn.execute(
                "SELECT astral_job_id FROM job WHERE company_job_id = ?", (company_job_id,)
            ).fetchone()
            if row:
                astral_job_id = row[0]

        grade_rows = []
        for seg in grades:
            code, letter, conf_d = seg[:2], seg[2], int(seg[3])
            grade_rows.append({"vector": code, "grade": letter, "confidence": conf_d})

        job = {
            "astral_job_id": astral_job_id,
            "grades": grade_rows,
        }
        if company_job_id: job["company_job_id"] = company_job_id
        if job_title:      job["job_title"]      = job_title
        if job_link:       job["job_link"]        = job_link
        if job_data:       job["job_data"]        = job_data
        jobs.append(job)

    return {"jobs": jobs}


# ---------------------------------------------------------------------------
# evaluate_jd decoder
# Extracts [astral_job_id=xxx] markers from NO_CACHE block to reconstruct
# batch_entities, then delegates to _decode_payload.
# ---------------------------------------------------------------------------

def _decode_evaluate(payload_str: str, nocache_blocks: list) -> Optional[dict]:
    batch_entities = None
    for block in nocache_blocks:
        ids = _ASTRAL_ID_RE.findall(block.get("block_data") or "")
        if ids:
            batch_entities = [{"astral_job_id": i} for i in ids]
            break

    if not batch_entities:
        return None  # can't decode without the entity list

    from src.core.agent import _decode_payload
    return _decode_payload("evaluate_jd", "grades_encoded", payload_str, {"batch_entities": batch_entities})


# ---------------------------------------------------------------------------
# Per-task migration runner
# ---------------------------------------------------------------------------

def _migrate_task(task_key: str, apply: bool, conn: sqlite3.Connection) -> None:
    response_rows = conn.execute(
        "SELECT agent_data_id, batch_id, block_data FROM agent_data "
        "WHERE task_key = ? AND block_type = 'RESPONSE'",
        (task_key,),
    ).fetchall()

    total = updated = skipped = failed = 0

    for agent_data_id, batch_id, raw_blob in response_rows:
        total += 1
        raw_text = _decompress(raw_blob)
        payload_str = _extract_payload_str(raw_text)

        if payload_str is None:
            skipped += 1
            continue

        decoded = None
        try:
            if task_key == "qualify_job_listings":
                decoded = _decode_qualify(payload_str, conn)

            elif task_key == "evaluate_jd":
                nocache_rows = conn.execute(
                    "SELECT block_data FROM agent_data WHERE batch_id = ? AND block_type = 'NO_CACHE'",
                    (batch_id,),
                ).fetchall()
                nocache_blocks = [{"block_data": _decompress(r[0])} for r in nocache_rows]
                decoded = _decode_evaluate(payload_str, nocache_blocks)

        except Exception as exc:
            print(f"  FAIL    {agent_data_id}: {exc}")
            failed += 1
            continue

        if decoded is None:
            print(f"  SKIP    {agent_data_id}: could not reconstruct batch_entities")
            skipped += 1
            continue

        n_jobs = len(decoded.get("jobs", []))
        print(f"  {'UPDATE' if apply else 'DRY-RUN'} {agent_data_id} ({n_jobs} jobs)")

        if apply:
            conn.execute(
                "UPDATE agent_data SET block_data = ? WHERE agent_data_id = ?",
                (_compress(json.dumps(decoded)), agent_data_id),
            )
        updated += 1

    if apply:
        conn.commit()

    verb = "updated" if apply else "would update"
    print(f"\n  {task_key}: {total} RESPONSE blocks — {updated} {verb}, {skipped} skipped, {failed} failed\n")


# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true", help="Write changes to DB (default: dry run)")
    parser.add_argument("--task", choices=["qualify_job_listings", "evaluate_jd", "both"], default="both")
    args = parser.parse_args()

    tasks = ["qualify_job_listings", "evaluate_jd"] if args.task == "both" else [args.task]

    if not args.apply:
        print("=== DRY RUN — pass --apply to write changes ===\n")

    conn = sqlite3.connect(DB_PATH)
    try:
        for task in tasks:
            _migrate_task(task, args.apply, conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
