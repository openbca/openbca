MODEL(
    name california.commodity_load_shape_ts,
    kind FULL,
    grain (commodity, load_shape, timestamp),
);

SELECT
    'ELECTRICITY' AS commodity,
    load_shape || '_' || utility AS load_shape,
    NULL AS year, NULL AS month, hour_of_year,
    saved_kwh AS saved_energy_units
FROM california.elec_load_shape_unpivoted
UNION ALL
SELECT
    'GAS' AS commodity,
    therms_profile || '_' || utility AS load_shape,
    NULL AS year, month, NULL AS hour_of_year,
    saved_therm AS saved_energy_units
FROM california.therms_profile_unpivoted
