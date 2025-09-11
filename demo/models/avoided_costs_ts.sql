MODEL(
    name openbca_input.avoided_costs_ts,
    kind FULL,
    grain (commodity, avoided_cost_subset, avoided_cost, year, hour_of_year),
);

SELECT
    UPPER(commodity) AS commodity,
    UPPER(avoided_cost_subset) AS avoided_cost_subset,
    UPPER(avoided_cost_version) AS avoided_cost_version,
    UPPER(avoided_cost) AS avoided_cost,
    year, quarter, month, hour_of_year, hour_of_day,
    av_cost_dollar_per_energy_unit
FROM openbca_reference.avoided_costs_ts
WHERE
    (
        (UPPER(avoided_cost_version), UPPER(avoided_cost)) IN (SELECT DISTINCT avoided_cost_version, UNNEST(avoided_costs) AS avoided_cost FROM openbca_input.measures)
        OR NOT EXISTS (SELECT 1 FROM openbca_input.measures WHERE avoided_costs IS NOT NULL AND len(avoided_costs) > 0)
    )
    AND -- allow custom avoided costs to override reference avoided costs
    (UPPER(commodity), UPPER(avoided_cost)) NOT IN (SELECT DISTINCT UPPER(commodity), UPPER(avoided_cost) FROM demo.custom_avoided_costs_tabs)
UNION ALL
SELECT
    UPPER(commodity) AS commodity,
    UPPER(avoided_cost_subset) AS avoided_cost_subset,
    UPPER(avoided_cost_version) AS avoided_cost_version,
    UPPER(avoided_cost) AS avoided_cost,
    year, quarter, month, hour_of_year, hour_of_day,
    value AS av_cost_dollar_per_energy_unit
FROM demo.custom_avoided_costs_tabs
