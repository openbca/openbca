MODEL(
    name flexvalue_input.value_stream_ts,
    kind FULL,
    grain (utility, region, commodity, value_stream, year, hour_of_year),
);

WITH regions AS (
    SELECT distinct region FROM california.elec_av_costs
)
-- hourly value streams
SELECT
    utility, region,
    'ELECTRICITY' AS commodity,
    year, quarter, month,
    hour_of_year, hour_of_day,
    value_stream, value
FROM california.elec_av_costs
UNPIVOT (
    value FOR value_stream IN (
        energy, losses, ancillary_services, capacity,
        transmission, distribution, cap_and_trade, ghg_adder, ghg_rebalancing,
        methane_leakage, ghg_adder_rebalancing, total, marginal_ghg,
    )
)
UNION ALL
-- monthly value streams
SELECT
    utility, r.region,
    'GAS' AS commodity,
    year, quarter, month,
    NULL AS hour_of_year, NULL AS hour_of_day,
    value_stream, value
FROM california.gas_av_costs
UNPIVOT (
    value FOR value_stream IN (
        market, t_d, environment, btm_methane, upstream_methane,
        total, marginal_ghg,
    )
)
CROSS JOIN regions r
