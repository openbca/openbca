MODEL(
    name flexvalue_input.commodity_load_shape_ts,
    kind FULL,
    grain (utility, commodity, hour_of_year),
);
SELECT
    utility,
    'ELECTRICITY' AS commodity,
    quarter, month,
    hour_of_year, hour_of_day,
    load_shape, value
FROM nspm.elec_load_shape_unpivoted
UNION ALL
SELECT
    utility,
    'GAS' AS commodity,
    quarter, month,
    NULL AS hour_of_year, NULL AS hour_of_day,
    therms_profile as load_shape, value
FROM nspm.therms_profile_unpivoted
