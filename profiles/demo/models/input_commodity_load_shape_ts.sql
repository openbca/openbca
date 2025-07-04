MODEL(
    name openbca_input.input_commodity_load_shape_ts,
    kind FULL,
    grain (commodity, load_shape, hour_of_year),
);
SELECT
    commodity,
    quarter,
    month,
    hour_of_year,
    hour_of_day,
    load_shape,
    value
FROM openbca_input.custom_load_shapes
