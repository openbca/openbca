MODEL(
    name core_layer0_base.load_shapes_ts,
    kind VIEW,
    grain (commodity, load_shape, hour_of_year),
);

SELECT
    UPPER(load_shape::VARCHAR) AS load_shape,
    UPPER(commodity)::VARCHAR AS commodity,
    COALESCE(
        quarter, 
        CASE 
        WHEN month BETWEEN 1 AND 3 THEN 1
        WHEN month BETWEEN 4 AND 6 THEN 2
        WHEN month BETWEEN 7 AND 9 THEN 3
        WHEN month BETWEEN 10 AND 12 THEN 4
        END,
        CASE 
        WHEN day_of_year BETWEEN 1 AND 90 THEN 1
        WHEN day_of_year BETWEEN 91 AND 181 THEN 2
        WHEN day_of_year BETWEEN 182 AND 273 THEN 3
        WHEN day_of_year BETWEEN 274 AND 365 THEN 4
        END,
        CASE 
        WHEN hour_of_year BETWEEN 0 AND 2159 THEN 1
        WHEN hour_of_year BETWEEN 2160 AND 4343 THEN 2
        WHEN hour_of_year BETWEEN 4344 AND 6551 THEN 3
        WHEN hour_of_year BETWEEN 6552 AND 8759 THEN 4
        END
    )::INTEGER AS quarter,

    COALESCE(
        month,
        CASE 
        WHEN hour_of_year BETWEEN 0 AND 743 THEN 1
        WHEN hour_of_year BETWEEN 744 AND 1415 THEN 2
        WHEN hour_of_year BETWEEN 1416 AND 2159 THEN 3
        WHEN hour_of_year BETWEEN 2160 AND 2879 THEN 4
        WHEN hour_of_year BETWEEN 2880 AND 3623 THEN 5
        WHEN hour_of_year BETWEEN 3624 AND 4343 THEN 6
        WHEN hour_of_year BETWEEN 4344 AND 5087 THEN 7
        WHEN hour_of_year BETWEEN 5088 AND 5831 THEN 8
        WHEN hour_of_year BETWEEN 5832 AND 6551 THEN 9
        WHEN hour_of_year BETWEEN 6552 AND 7295 THEN 10
        WHEN hour_of_year BETWEEN 7296 AND 8015 THEN 11
        WHEN hour_of_year BETWEEN 8016 AND 8759 THEN 12
        END,        
        CASE 
        WHEN day_of_year BETWEEN 1 AND 31 THEN 1
        WHEN day_of_year BETWEEN 32 AND 59 THEN 2
        WHEN day_of_year BETWEEN 60 AND 90 THEN 3
        WHEN day_of_year BETWEEN 91 AND 120 THEN 4
        WHEN day_of_year BETWEEN 121 AND 151 THEN 5
        WHEN day_of_year BETWEEN 152 AND 181 THEN 6
        WHEN day_of_year BETWEEN 182 AND 212 THEN 7
        WHEN day_of_year BETWEEN 213 AND 243 THEN 8
        WHEN day_of_year BETWEEN 244 AND 273 THEN 9
        WHEN day_of_year BETWEEN 274 AND 304 THEN 10
        WHEN day_of_year BETWEEN 305 AND 334 THEN 11
        WHEN day_of_year BETWEEN 335 AND 365 THEN 12
        END
    )::INTEGER AS month,

    COALESCE(day_of_year, 1 + FLOOR(hour_of_year/24)) as day_of_year,
    (hour_of_year) % 24::INTEGER AS hour_of_day,
    hour_of_year::INTEGER AS hour_of_year,
    load_shape_value::FLOAT AS load_shape_value

FROM 
    openbca_input.load_shapes_ts ls
