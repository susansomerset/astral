# Candidate Migrations

**Test module:** `tests/component/data/database/test_candidate_migrations.py`

_(Coverage map and manifest blocks appended by Betty `qa-child`.)_

### AST-971 · AST-871

Vocab revise only (`NEW` → `NEW_CANDIDATE`). Primary: **`docs/test-bible/core/candidate.md`** § AST-971.

### AST-1014 · AST-952

`_migrate_candidate_library_ast1014`: profile→contact, name/pronoun columns, context remaps, hopes/interests/concerns, idempotent. Primary: **`docs/test-bible/core/candidate.md`** § AST-1014 — **`TestAst1014CandidateLibraryMigration`**. AST-575 end-state revised to columns after library migrate.
