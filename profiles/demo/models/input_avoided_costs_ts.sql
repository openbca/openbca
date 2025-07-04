MODEL(
    name openbca_input.input_avoided_costs_ts,
    kind FULL,
    grain (utility, region, commodity, avoided_cost, year, hour_of_year),
);

SELECT
    commodity,
    avoided_cost_subset,
    year,
    quarter,
    month,
    hour_of_year,
    hour_of_day,
    avoided_cost as avoided_cost,
    value
FROM openbca_input.custom_avoided_costs_tabs
