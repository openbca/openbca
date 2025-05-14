MODEL(
    name flexvalue.commodity_load_shape_monthly,
    kind FULL,
    grain (state, utility, region, commodity, year, quarter, month),
);
SELECT
    'CA' AS state,
    utility,
    'GAS' AS commodity,
    quarter, month,
    therms_profile as load_shape, value
FROM flexvalue_reference.therms_profile_unpivoted
