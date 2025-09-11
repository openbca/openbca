MODEL(
  name openbca_input.measures,
  dialect duckdb,
  kind FULL
);

WITH raw AS (
  SELECT * FROM read_csv_auto('./demo/data/measures.csv', HEADER = TRUE)
),
typed AS (
  SELECT
      CAST(measure_id AS VARCHAR)                           AS measure_id,
      UPPER(CAST(avoided_cost_subset AS VARCHAR))           AS avoided_cost_subset,
      UPPER(COALESCE(
        CAST(NULLIF(avoided_cost_version, '') AS VARCHAR),
        (SELECT max(avoided_cost_version) FROM demo.custom_avoided_costs_tabs),
        (SELECT max(avoided_cost_version) FROM openbca_reference.avoided_costs_ts),
      ))                                                    AS avoided_cost_version,
      CAST(start_year AS INT)                               AS start_year,
      CAST(start_quarter AS INT)                            AS start_quarter,
      CAST(discount_rate_ratio AS DOUBLE)                   AS discount_rate_ratio,
      CAST(estimated_useful_life AS INT)                    AS estimated_useful_life,
      CAST(unit_quantity AS DOUBLE)                         AS unit_quantity,
      CAST(net_to_gross_ratio AS DOUBLE)                    AS net_to_gross_ratio,
      CAST(admin_cost_dollars AS DOUBLE)                    AS admin_cost_dollars,
      CAST(incentive_cost_dollars AS DOUBLE)                AS incentive_cost_dollars,
      CAST(measure_cost_dollars AS DOUBLE)                  AS measure_cost_dollars,
      CAST(elec_savings_mwh AS DOUBLE)                      AS elec_savings_mwh,
      CAST(gas_saving_therms AS DOUBLE)                     AS gas_saving_therms,
      UPPER(CAST(elec_load_shape_mapping AS VARCHAR))       AS elec_load_shape_mapping,
      UPPER(CAST(gas_load_shape_mapping AS VARCHAR))        AS gas_load_shape_mapping,
      STR_SPLIT(NULLIF(UPPER(REPLACE(avoided_costs, ' ', '')), ''), ',') AS avoided_costs
  FROM raw
)
SELECT * FROM typed;
