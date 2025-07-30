MODEL(
    name openbca_input.avoided_costs_ts,
    kind FULL,
    grain (commodity, avoided_cost_subset, avoided_cost, year, hour_of_year),
);

SELECT
    'demo_avoided_costs' AS avoided_cost_version,
    commodity,
    avoided_cost_subset,
    year,
    quarter,
    month,
    hour_of_year,
    hour_of_day,
    avoided_cost,
    value AS av_cost_dollar_per_energy_unit
FROM demo.custom_avoided_costs_tabs
