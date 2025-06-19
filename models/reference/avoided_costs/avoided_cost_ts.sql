MODEL(
    name openbca_reference.avoided_costs_ts,
    kind VIEW,
    grain (commodity, version, avoided_cost, avoided_cost_subset, year, month, hour_of_year),
);

SELECT
    commodity,
    avoided_cost_version,
    avoided_cost_subset,
    avoided_cost,
    year, month, hour_of_year,
    av_costs_dollar_per_energy_unit
FROM california.avoided_costs_ts


-- UNION ALL TODO add more avoided costs
