MODEL (
    name openbca_input.load_shape_ts,
    kind FULL,
    grain (
        commodity
        quarter,
        month,
        day_of_year,
        hour_of_year
        load_shape,
        value

    )
);

SELECT
    CAST(commodity AS STRING) AS commodity,
    CAST(quarter as INT) AS quarter,
    CAST(month as INT) AS month,
    CAST(day_of_year AS INT) AS hour_of_day,
    CAST(hour_of_year AS INT) AS hour_of_year,
    CAST(load_shape AS STRING) AS load_shape,
    CAST(value AS FLOAT) AS load_shape_normalized_fraction
FROM nspm.openbca_input_load_shapes_ts

