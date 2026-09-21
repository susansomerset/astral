-- AST-1701 operator backfill — run manually (sqlite3 astral.db < this file).
-- NOT imported by SEED_CONFIG / _ensure_job_schema / server startup.
-- Run AFTER AST-1701 DDL has been applied (app boot once is enough for DDL).
-- Requires job.company_id + job.source_entity_id columns (AST-1701 ensure).

BEGIN;

-- ---------------------------------------------------------------------------
-- a) Meteorite-linked jobs (prefer meteorite.astral_job_id → meteorite parent)
-- ---------------------------------------------------------------------------
UPDATE job
SET
  source = 'meteorite',
  source_entity_id = (
    SELECT CAST(m.id AS TEXT)
    FROM meteorite AS m
    WHERE m.astral_job_id = job.astral_job_id
    ORDER BY m.id
    LIMIT 1
  ),
  company_id = CASE
    WHEN job.company_id LIKE 'meteorite-%' THEN NULL
    WHEN job.company_id IS NOT NULL
         AND TRIM(job.company_id) != ''
         AND EXISTS (
           SELECT 1 FROM company AS c
           WHERE c.short_name = job.company_id
             AND c.state = 'METEORITE'
         )
    THEN NULL
    ELSE job.company_id
  END
WHERE astral_job_id IN (
  SELECT astral_job_id
  FROM meteorite
  WHERE astral_job_id IS NOT NULL
    AND TRIM(astral_job_id) != ''
);

-- ---------------------------------------------------------------------------
-- b) Remaining gazed / unset / blank parent id → company parent from employer
-- ---------------------------------------------------------------------------
-- Non-placeholder employer still on the row:
UPDATE job
SET
  source = 'company',
  source_entity_id = company_id
WHERE (
    source IS NULL
    OR TRIM(source) = ''
    OR source = 'gazed'
    OR source_entity_id IS NULL
    OR TRIM(source_entity_id) = ''
  )
  AND company_id IS NOT NULL
  AND TRIM(company_id) != ''
  AND company_id NOT LIKE 'meteorite-%'
  AND NOT EXISTS (
    SELECT 1 FROM company AS c
    WHERE c.short_name = job.company_id
      AND c.state = 'METEORITE'
  );

-- Placeholder-only employer, no meteorite link: clear fake employer; leave diagnostic below.
UPDATE job
SET company_id = NULL
WHERE (
    source IS NULL
    OR TRIM(source) = ''
    OR source = 'gazed'
    OR source_entity_id IS NULL
    OR TRIM(source_entity_id) = ''
  )
  AND company_id IS NOT NULL
  AND (
    company_id LIKE 'meteorite-%'
    OR EXISTS (
      SELECT 1 FROM company AS c
      WHERE c.short_name = job.company_id
        AND c.state = 'METEORITE'
    )
  );

COMMIT;

-- ---------------------------------------------------------------------------
-- c) Verification (expect 0 rows each) — diagnostic only
-- ---------------------------------------------------------------------------
-- Bad / blank parent fields:
-- SELECT astral_job_id, source, source_entity_id, company_id
-- FROM job
-- WHERE source IS NULL
--    OR source NOT IN ('company', 'meteorite')
--    OR source_entity_id IS NULL
--    OR TRIM(source_entity_id) = '';

-- Legacy gazed still present:
-- SELECT astral_job_id, source, source_entity_id, company_id
-- FROM job
-- WHERE source = 'gazed';

-- Orphans: placeholder-cleared / no parent id and no meteorite link (Susan reviews):
-- SELECT astral_job_id, source, source_entity_id, company_id, candidate_id
-- FROM job
-- WHERE (source_entity_id IS NULL OR TRIM(source_entity_id) = '')
--   AND astral_job_id NOT IN (
--     SELECT astral_job_id FROM meteorite
--     WHERE astral_job_id IS NOT NULL AND TRIM(astral_job_id) != ''
--   );
