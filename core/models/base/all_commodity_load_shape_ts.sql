MODEL(
    name openbca_core.all_commodity_load_shape_ts,
    kind VIEW,
    grain (commodity, load_shape, hour_of_year),
    audits (
        not_null(columns := (commodity, load_shape, load_shape_normalized_fraction, quarter, month)),
        unique_combination_of_columns(columns := (commodity, load_shape, quarter, month, hour_of_year, hour_of_day)),
        accepted_values(column := quarter, is_in := (1, 2, 3, 4)),
        accepted_values(column := month, is_in := (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)),
        accepted_values(column := hour_of_day, is_in := (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23)),
        accepted_range(column := hour_of_year, min_v := 0, max_v := 8760),
        accepted_values(column := commodity, is_in := ('ELECTRICITY', 'GAS')),
    )
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
