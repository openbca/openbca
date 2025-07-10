MODEL(
    name openbca_core.all_avoided_costs_ts,
    kind VIEW,
    grain (commodity, avoided_cost_subset, avoided_cost, year, hour_of_year),
);

SELECT
    commodity::VARCHAR AS commodity,
    avoided_cost_subset::VARCHAR AS avoided_cost_subset,
    year::INTEGER AS year,
    quarter::INTEGER AS quarter,
    month::INTEGER AS month,
    hour_of_year::INTEGER AS hour_of_year,
    hour_of_day::INTEGER AS hour_of_day,
    avoided_cost::VARCHAR AS avoided_cost,
    av_cost_dollar_per_energy_unit::NUMERIC AS av_cost_dollar_per_energy_unit
FROM (
    SELECT * FROM openbca_reference.avoided_costs_ts
    WHERE (commodity, avoided_cost) NOT IN (SELECT commodity, avoided_cost FROM openbca_input.avoided_costs_ts)
    UNION ALL
    SELECT * FROM openbca_input.avoided_costs_ts
)
