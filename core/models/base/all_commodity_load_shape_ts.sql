MODEL(
    name openbca_core.all_commodity_load_shape_ts,
    kind VIEW,
    grain (commodity, load_shape, hour_of_year),
);

SELECT
    commodity::VARCHAR AS commodity,
    quarter::INTEGER AS quarter,
    month::INTEGER AS month,
    hour_of_day::INTEGER AS hour_of_day,
    hour_of_year::INTEGER AS hour_of_year,
    load_shape::VARCHAR AS load_shape,
    load_shape_normalized_fraction::NUMERIC AS load_shape_normalized_fraction
FROM (
    SELECT * FROM openbca_reference.commodity_load_shape_ts
    WHERE (commodity, load_shape) NOT IN (
        SELECT commodity, load_shape FROM openbca_input.load_shape_ts
    )
    UNION ALL
    SELECT * FROM openbca_input.load_shape_ts
)
