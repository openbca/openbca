MODEL(
    name flexvalue.commodity_load_shape_ts,
    kind FULL,
    grain (state, utility, region, commodity, year, hour_of_year),
);
SELECT
    'CA' AS state,
    utility,
    'ELECTRICITY' AS commodity,
    quarter, month,
    hour_of_year, hour_of_day,
    load_shape, value
FROM flexvalue_reference.elec_load_shape_unpivoted
UNION ALL
SELECT
    'CA' AS state,
    utility,
    'GAS' AS commodity,
    quarter, month,
    NULL AS hour_of_year, NULL AS hour_of_day,
    therms_profile as load_shape, value
FROM flexvalue_reference.therms_profile_unpivoted
