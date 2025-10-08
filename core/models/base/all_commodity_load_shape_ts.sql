MODEL(
    name openbca_core.all_commodity_load_shape_ts,
    kind VIEW,
    grain (commodity, load_shape, hour_of_year),
);

SELECT
    commodity::VARCHAR AS commodity,
    COALESCE(
        quarter, 
        case when month in (1, 2, 3) then 1
        when month in (4, 5, 6) then 2
        when month in (7, 8, 9) then 3
        when month in (10, 11, 12) then 4
        end,
        case when hour_of_year between 0 and 2159 then 1
        when hour_of_year between 2160 and 4343 then 2
        when hour_of_year between 4344 and 6551 then 3
        when hour_of_year between 6552 and 8759 then 4
        end
    )::INTEGER AS quarter,

    COALESCE(
        month,
        case 
        when hour_of_year between 0 and 743 then 1
        when hour_of_year between 744 and 1415 then 2
        when hour_of_year between 1416 and 2159 then 3
        when hour_of_year between 2160 and 2879 then 4
        when hour_of_year between 2880 and 3623 then 5
        when hour_of_year between 3624 and 4343 then 6
        when hour_of_year between 4344 and 5087 then 7
        when hour_of_year between 5088 and 5831 then 8
        when hour_of_year between 5832 and 6551 then 9
        when hour_of_year between 6552 and 7295 then 10
        when hour_of_year between 7296 and 8015 then 11
        when hour_of_year between 8016 and 8750 then 12
        end
    )::INTEGER AS month,

    -- TODO quarter/month calculation is approximate
    --COALESCE(quarter, FLOOR((hour_of_year - 1) / (8760 / 4)) + 1)::INTEGER AS quarter, -- TODO quarter calculation is approximate
    --COALESCE(month, FLOOR((hour_of_year - 1) / (8760 / 12)) + 1)::INTEGER AS month,
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
