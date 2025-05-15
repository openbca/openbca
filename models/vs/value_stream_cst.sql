MODEL(
    name flexvalue.value_stream_cst,
    kind FULL,
    grain (state, utility, region, commodity, value_stream),
);

SELECT
    'CA' AS state, utility, region,
    'ELECTRICITY' AS commodity,
    'marginal_cost' AS value_stream,
    marginal_cost AS value
FROM flexvalue.elec_marginal_cost

UNION ALL

SELECT
    'CA' AS state, utility, region,
    'GAS' AS commodity,
    'marginal_cost' AS value_stream,
    marginal_cost AS value
FROM flexvalue.gas_marginal_cost
