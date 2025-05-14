MODEL(
    name flexvalue.value_stream_ts,
    kind FULL,
    grain (state, utility, region, commodity, value_stream, year, hour_of_year),
);

-- hourly value streams
SELECT
    'CA' AS state, utility, region,
    'ELECTRICITY' AS commodity,
    year, quarter, month,
    hour_of_year, hour_of_day,
    value_stream, value
FROM flexvalue_reference.elec_av_costs
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
    'CA' AS state, utility,
    NULL AS region,
    'GAS' AS commodity,
    year, quarter, month,
    NULL AS hour_of_year, NULL AS hour_of_day,
    value_stream, value
FROM flexvalue_reference.gas_av_costs
UNPIVOT (
    value FOR value_stream IN (
        market, t_d, environment, btm_methane, upstream_methane,
        total, marginal_ghg,
    )
)
