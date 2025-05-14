MODEL(
    name flexvalue.hourly_vs,
    kind FULL,
    grain (state, utility, region, value_stream, year, hour_of_year),
);

SELECT
    'CA' AS state, utility, region,
    year, hour_of_year, quarter, month, hour_of_day,
    value_stream, value
FROM flexvalue_reference.elec_av_costs
UNPIVOT (
    value FOR value_stream IN (
        energy, losses, ancillary_services, capacity,
        transmission, distribution, cap_and_trade, ghg_adder, ghg_rebalancing,
        methane_leakage, ghg_adder_rebalancing, total, marginal_ghg,
    )
)
