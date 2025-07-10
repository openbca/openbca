MODEL(
    name openbca_reference.avoided_costs_ts,
    kind FULL,
    grain (commodity, avoided_cost_subset, avoided_cost, year, hour_of_year),
);

WITH regions AS (
    SELECT distinct region FROM california.elec_av_costs
)

-- IMPORTANT NOTE: The time-granularity of the avoided_costs_ts table cannot be lower than the time-granularity of the commodity_load_shape_ts table.
-- For instance, if the commodity_load_shape_ts table is monthly then the avoided_costs_ts table cannot be hourly.


-- hourly value streams
SELECT
    utility || '_'|| region as avoided_cost_subset,
    'ELECTRICITY' AS commodity,
    year, quarter, month,
    hour_of_year, hour_of_day,
    avoided_cost, value as av_cost_dollar_per_energy_unit -- measured in $/kWh
FROM california.elec_av_costs
UNPIVOT (
    value FOR avoided_cost IN (
        energy, losses, ancillary_services, capacity,
        transmission, distribution, cap_and_trade, ghg_adder, ghg_rebalancing,
        methane_leakage, ghg_adder_rebalancing, marginal_ghg,
    )
)
UNION ALL
-- monthly value streams
SELECT
    utility || '_'|| r.region as avoided_cost_subset,
    'GAS' AS commodity,
    year, quarter, month,
    NULL AS hour_of_year, NULL AS hour_of_day,
    avoided_cost, value as av_cost_dollar_per_energy_unit -- measured in $/therm
FROM california.gas_av_costs
UNPIVOT (
    value FOR avoided_cost IN (
        market, t_d, environment, btm_methane, upstream_methane, marginal_ghg
    )
)
CROSS JOIN regions r
