MODEL(
    name openbca_reference.commodity_load_shape_ts,
    kind FULL,
    grain (commodity, load_shape, hour_of_year),
);
SELECT
    'ELECTRICITY' AS commodity,
    quarter, month,
    hour_of_year, hour_of_day,
    load_shape || '_' || utility AS load_shape,
    value AS load_shape_normalized_fraction
FROM california.elec_load_shape_unpivoted
UNION ALL
SELECT
    'GAS' AS commodity,
    quarter, month,
    NULL AS hour_of_year, NULL AS hour_of_day,
    therms_profile || '_' || utility AS load_shape,
    value AS load_shape_normalized_fraction
FROM california.therms_profile_unpivoted
