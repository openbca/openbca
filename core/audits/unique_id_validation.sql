AUDIT (
  name unique_id_validation_audit,
);

-- This audit confirms that all IDs in the input file are unique.
-- While there's already a uniqueness check in the measures.sql model,
-- this audit provides more detailed information about duplicate IDs.

WITH
duplicate_measure_ids AS (
  -- Find duplicate measure_ids in the input measures table
  SELECT
    measure_id,
    COUNT(*) as occurrence_count
  FROM openbca_input.measures
  GROUP BY measure_id
  HAVING COUNT(*) > 1
)

-- Return detailed information about duplicate measure_ids
SELECT
  measure_id,
  occurrence_count,
  'Duplicate measure_id found in input file' as validation_message
FROM duplicate_measure_ids