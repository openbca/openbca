-- SQLMesh model: converts openbca_input.avoided_costs_ts (long format) into
-- the wide format expected by avoided_costs_platform_use.ca_combined_value_curve_gas.
--
-- avoided_cost_subset must be the utility name (e.g. "PGE").
-- value_curve_name is hardcoded — update as needed.

MODEL(
    name ca_acc_gas_output.ca_combined_value_curve_gas,
    kind FULL,
    grain (value_curve_name, utility, year, month),
    columns (
        value_curve_name VARCHAR,
        utility VARCHAR,
        year INT,
        quarter INT,
        month INT,
        total DOUBLE,
        market DOUBLE,
        t_d DOUBLE,
        environment DOUBLE,
        upstream_methane DOUBLE,
        btm_methane DOUBLE,
        air_quality_adder DOUBLE,
        marginal_ghg DOUBLE,
    )
);

WITH gas_avoided_costs AS (
    -- Identify which avoided_cost names correspond to the Natural Gas commodity.
    SELECT DISTINCT avoided_cost
    FROM openbca_input.value_stream_groups
    WHERE commodity = 'Natural Gas'
),

gas_ts AS (
    SELECT
        -- Normalize sheet name to lowercase_with_underscores to match BQ column names.
        LOWER(REPLACE(REPLACE(ac.avoided_cost, ' ', '_'), '-', '_')) AS avoided_cost,
        -- avoided_cost_subset encodes the utility (e.g. "PGE").
        SPLIT_PART(ac.avoided_cost_subset, ' ', 1)                   AS utility,
        ac.year,
        ac.quarter,
        ac.month,
        ac.avoided_cost_value
    FROM openbca_input.avoided_costs_ts AS ac
    INNER JOIN gas_avoided_costs AS gac
        ON ac.avoided_cost = gac.avoided_cost
)

SELECT
    'openbca'        AS value_curve_name,
    utility,
    year::INT        AS year,
    quarter::INT     AS quarter,
    month::INT       AS month,

    MAX(CASE WHEN avoided_cost = 'total'             THEN avoided_cost_value END)::DOUBLE AS total,
    MAX(CASE WHEN avoided_cost = 'market'            THEN avoided_cost_value END)::DOUBLE AS market,
    MAX(CASE WHEN avoided_cost = 't_d'               THEN avoided_cost_value END)::DOUBLE AS t_d,
    MAX(CASE WHEN avoided_cost = 'environment'       THEN avoided_cost_value END)::DOUBLE AS environment,
    MAX(CASE WHEN avoided_cost = 'upstream_methane'  THEN avoided_cost_value END)::DOUBLE AS upstream_methane,
    MAX(CASE WHEN avoided_cost = 'btm_methane'       THEN avoided_cost_value END)::DOUBLE AS btm_methane,
    MAX(CASE WHEN avoided_cost = 'air_quality_adder' THEN avoided_cost_value END)::DOUBLE AS air_quality_adder,
    MAX(CASE WHEN avoided_cost = 'marginal_ghg'      THEN avoided_cost_value END)::DOUBLE AS marginal_ghg

FROM gas_ts
GROUP BY utility, year, quarter, month
