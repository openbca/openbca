MODEL(
    name openbca_input.load_shape_ts,
    kind FULL,
    grain (commodity, load_shape, hour_of_year),
);
SELECT
    'ELECTRICITY' AS commodity,
    NULL AS quarter,
    NULL AS month,
    NULL AS hour_of_year,
	NULL AS hour_of_day,
    load_shape_name AS load_shape,
    load_shape_normalized_fraction AS load_shape_normalized_fraction
FROM nspm_raw.loadshape_mapping_annual
UNION ALL
SELECT
    'ELECTRICITY' AS commodity,
    NULL AS quarter,
    NULL AS month,
    hour_of_year AS hour_of_year,
	NULL AS hour_of_day,
    load_shape_name AS load_shape,
    load_shape_normalized_fraction AS load_shape_normalized_fraction
FROM nspm_raw.loadshape_mapping_hourly
