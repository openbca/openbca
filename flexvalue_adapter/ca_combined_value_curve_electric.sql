-- SQLMesh model: converts openbca_input.avoided_costs_ts (long format) into
-- the wide format expected by avoided_costs_platform_use.ca_combined_value_curve_electric.
--
-- avoided_cost_subset must be formatted as "<UTILITY> <REGION>" (e.g. "PGE CZ1").
-- value_curve_name is hardcoded — update as needed.

MODEL(
    name ca_acc_electric_output.ca_combined_value_curve_electric,
    kind FULL,
    grain (value_curve_name, utility, region, year, hour_of_year),
    columns (
        value_curve_name VARCHAR,
        utility VARCHAR,
        region VARCHAR,
        year INT,
        quarter INT,
        month INT,
        hour_of_day INT,
        hour_of_year INT,
        energy DOUBLE,
        losses DOUBLE,
        ancillary_services DOUBLE,
        capacity DOUBLE,
        transmission DOUBLE,
        distribution DOUBLE,
        cap_and_trade DOUBLE,
        ghg_adder DOUBLE,
        ghg_rebalancing DOUBLE,
        ghg_adder_rebalancing DOUBLE,
        methane_leakage DOUBLE,
        ghg_adder_societal DOUBLE,
        total DOUBLE,
        marginal_ghg DOUBLE,
        datetime TIMESTAMP,
    )
);

WITH electric_avoided_costs AS (
    -- Identify which avoided_cost names correspond to the Electric commodity.
    SELECT DISTINCT avoided_cost
    FROM openbca_input.value_stream_groups
    WHERE commodity = 'Electric'
),

electric_ts AS (
    SELECT
        -- Normalize sheet name to lowercase_with_underscores to match BQ column names.
        LOWER(REPLACE(REPLACE(ac.avoided_cost, ' ', '_'), '-', '_')) AS avoided_cost,
        -- avoided_cost_subset encodes "UTILITY REGION" (e.g. "PGE CZ1").
        SPLIT_PART(ac.avoided_cost_subset, ' ', 1)                   AS utility,
        SPLIT_PART(ac.avoided_cost_subset, ' ', 2)                   AS region,
        ac.year,
        ac.quarter,
        ac.month,
        ac.hour_of_day,
        ac.hour_of_year,
        ac.avoided_cost_value
    FROM openbca_input.avoided_costs_ts AS ac
    INNER JOIN electric_avoided_costs AS eac
        ON ac.avoided_cost = eac.avoided_cost
)

SELECT
    'openbca'          AS value_curve_name,
    utility,
    region,
    year::INT          AS year,
    quarter::INT       AS quarter,
    month::INT         AS month,
    hour_of_day::INT   AS hour_of_day,
    hour_of_year::INT  AS hour_of_year,

    MAX(CASE WHEN avoided_cost = 'energy'             THEN avoided_cost_value END)::DOUBLE AS energy,
    MAX(CASE WHEN avoided_cost = 'losses'             THEN avoided_cost_value END)::DOUBLE AS losses,
    MAX(CASE WHEN avoided_cost = 'ancillary_services' THEN avoided_cost_value END)::DOUBLE AS ancillary_services,
    MAX(CASE WHEN avoided_cost = 'capacity'           THEN avoided_cost_value END)::DOUBLE AS capacity,
    MAX(CASE WHEN avoided_cost = 'transmission'       THEN avoided_cost_value END)::DOUBLE AS transmission,
    MAX(CASE WHEN avoided_cost = 'distribution'       THEN avoided_cost_value END)::DOUBLE AS distribution,
    MAX(CASE WHEN avoided_cost = 'cap_and_trade'      THEN avoided_cost_value END)::DOUBLE AS cap_and_trade,
    MAX(CASE WHEN avoided_cost = 'ghg_adder'          THEN avoided_cost_value END)::DOUBLE AS ghg_adder,
    MAX(CASE WHEN avoided_cost = 'ghg_rebalancing'    THEN avoided_cost_value END)::DOUBLE AS ghg_rebalancing,
    -- ghg_adder_rebalancing is derived, matching the ACC model convention.
    (
        COALESCE(MAX(CASE WHEN avoided_cost = 'ghg_adder'        THEN avoided_cost_value END), 0)
        + COALESCE(MAX(CASE WHEN avoided_cost = 'ghg_rebalancing' THEN avoided_cost_value END), 0)
    )::DOUBLE AS ghg_adder_rebalancing,
    MAX(CASE WHEN avoided_cost = 'methane_leakage'    THEN avoided_cost_value END)::DOUBLE AS methane_leakage,
    MAX(CASE WHEN avoided_cost = 'ghg_adder_societal' THEN avoided_cost_value END)::DOUBLE AS ghg_adder_societal,
    MAX(CASE WHEN avoided_cost = 'total'              THEN avoided_cost_value END)::DOUBLE AS total,
    MAX(CASE WHEN avoided_cost = 'marginal_ghg'       THEN avoided_cost_value END)::DOUBLE AS marginal_ghg,

    -- hour_of_year is 0-based (0 = Jan 1 00:00), consistent with the openbca parser.
    (MAKE_TIMESTAMP(year::INT, 1, 1, 0, 0, 0) + INTERVAL (hour_of_year) HOUR)::TIMESTAMP AS datetime

FROM electric_ts
GROUP BY utility, region, year, quarter, month, hour_of_day, hour_of_year