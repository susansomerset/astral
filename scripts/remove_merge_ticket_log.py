#!/usr/bin/env python3
"""Remove one parent Linear ticket id from the merge ticket log (AST-792).

Usage:
    python3 scripts/remove_merge_ticket_log.py AST-741
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.merge_ticket_log import remove_merge_ticket_log


def main() -> None:
    if len(sys.argv) != 2:
        print(
            f"Usage: python3 {Path(__file__).name} AST-<number>",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        removed = remove_merge_ticket_log(sys.argv[1])
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    print(json.dumps({"removed": removed}))
    sys.exit(0)


if __name__ == "__main__":
    main()
