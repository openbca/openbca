MODEL(
    name flexvalue.commodity_load_shape_hourly,
    kind FULL,
    grain (state, utility, region, commodity, year, hour_of_year),
);
SELECT
    'CA' AS state,
    utility,
    'ELECTRICITY' AS commodity,
    quarter, month, hour_of_year, hour_of_day,
    load_shape, value
FROM flexvalue_reference.elec_load_shape_unpivoted
