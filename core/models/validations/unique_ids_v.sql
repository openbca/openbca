MODEL(
  name core_validations.unique_ids_v,
  kind FULL,
);

  SELECT
    DISTINCT id
  FROM
    openbca_input.measures
  QUALIFY 
    ROW_NUMBER() OVER (PARTITION BY id) > 1