MODEL (
    name openbca_input.load_shapes_ts_duplicate,
    kind FULL,
    grain (
        commodity
        load_shape,
        quarter,
        month,
        day_of_year,
        hour_of_year
    )
);

SELECT
    CAST(load_shape AS STRING) AS load_shape,
    CAST(commodity AS STRING) AS commodity,
    CAST(quarter as INT) AS quarter,
    CAST(month as INT) AS month,
    CAST(day_of_year AS INT) AS day_of_year,
    CAST(hour_of_year AS INT) AS hour_of_year,
    CAST(load_shape_value AS FLOAT) AS load_shape_value
FROM 
    nspm.openbca_input_load_shapes_ts ls

