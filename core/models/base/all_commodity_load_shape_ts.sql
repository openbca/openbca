MODEL(
    name openbca_core.all_commodity_load_shape_ts,
    kind VIEW,
    grain (commodity, load_shape, hour_of_year),
);

SELECT
    commodity::VARCHAR AS commodity,
    COALESCE(quarter, FLOOR((hour_of_year - 1) / (8760 / 4)) + 1)::INTEGER AS quarter, -- TODO quarter/month calculation is approximate
    COALESCE(month, FLOOR((hour_of_year - 1) / (8760 / 12)) + 1)::INTEGER AS month,
    COALESCE(hour_of_day, (hour_of_year - 1) % 24)::INTEGER AS hour_of_day,
    hour_of_year::INTEGER AS hour_of_year,
    upper(load_shape::VARCHAR) AS load_shape,
    load_shape_normalized_fraction::FLOAT AS load_shape_normalized_fraction
FROM (
    SELECT commodity, quarter, month, hour_of_day, hour_of_year, load_shape, load_shape_normalized_fraction
    FROM openbca_reference.commodity_load_shape_ts
    WHERE (commodity, load_shape) NOT IN (
        SELECT commodity, load_shape FROM openbca_input.load_shape_ts
    )
    UNION ALL
    SELECT commodity, quarter, month, hour_of_day, hour_of_year, load_shape, load_shape_normalized_fraction
    FROM openbca_input.load_shape_ts
)
