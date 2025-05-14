MODEL(
    name flexvalue.monthly_vs,
    kind FULL,
    grain (state, utility, region, value_stream, year, month),
);

SELECT
    'CA' AS state, utility, region,
    year, quarter, month
    value_stream, value
FROM flexvalue_reference.gas_av_costs
UNPIVOT (
    value FOR value_stream IN (
        market, t_d, environment, btm_methane, upstream_methane,
        total, marginal_ghg,
    )
)
