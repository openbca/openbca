MODEL(
  name openbca_input.avoided_costs_ts,
  kind FULL,
);

SELECT
    commodity, avoided_cost_subset,
    year, quarter, month, hour_of_year, hour_of_day,
    avoided_cost, av_cost_dollar_per_energy_unit
FROM openbca_reference.avoided_costs_ts
