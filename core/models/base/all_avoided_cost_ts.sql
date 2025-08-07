MODEL(
    name openbca_core.all_avoided_costs_ts,
    kind VIEW,
    grain (commodity, avoided_cost_subset, avoided_cost, year, month, hour_of_year),
    audits (
        not_null(columns := (commodity, avoided_cost, av_cost_dollar_per_energy_unit, year)),
        unique_combination_of_columns(columns := (commodity, avoided_cost_subset, avoided_cost, year, quarter, month, hour_of_year, hour_of_day)),
        accepted_range(column := year, min_v := 2010, max_v := 2100),
        accepted_values(column := quarter, is_in := (1, 2, 3, 4)),
        accepted_values(column := month, is_in := (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)),
        accepted_values(column := hour_of_day, is_in := (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23)),
        accepted_range(column := hour_of_year, min_v := 0, max_v := 8760),
        accepted_values(column := commodity, is_in := ('ELECTRICITY', 'GAS')),
    )
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
    SELECT commodity, avoided_cost_subset, year, quarter, month, hour_of_year, hour_of_day, avoided_cost, av_cost_dollar_per_energy_unit
    FROM openbca_reference.avoided_costs_ts
    WHERE (commodity, avoided_cost) NOT IN (SELECT commodity, avoided_cost FROM openbca_input.avoided_costs_ts)
    UNION ALL
    SELECT commodity, avoided_cost_subset, year, quarter, month, hour_of_year, hour_of_day, avoided_cost, av_cost_dollar_per_energy_unit
    FROM openbca_input.avoided_costs_ts
)
