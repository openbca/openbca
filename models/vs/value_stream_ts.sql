MODEL(
    name flexvalue.value_stream_ts,
    kind FULL,
    grain (utility, region, commodity, value_stream, year, hour_of_year),
);

-- hourly value streams
SELECT
    utility, region,
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
    utility, r.region,
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
CROSS JOIN flexvalue_reference.regions r

UNION ALL
-- constant value streams

SELECT
    utility, region,
    'ELECTRICITY' AS commodity,
    NULL AS year, NULL AS quarter, NULL AS month,
    NULL AS hour_of_year, NULL AS hour_of_day,
    'marginal_cost' AS value_stream,
    marginal_cost AS value
FROM flexvalue.elec_marginal_cost

UNION ALL

SELECT
    utility, region,
    'GAS' AS commodity,
    NULL AS year, NULL AS quarter, NULL AS month,
    NULL AS hour_of_year, NULL AS hour_of_day,
    'marginal_cost' AS value_stream,
    marginal_cost AS value
FROM flexvalue.gas_marginal_cost
