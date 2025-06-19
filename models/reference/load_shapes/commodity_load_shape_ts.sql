MODEL(
    name openbca_reference.commodity_load_shape_ts,
    kind FULL,
    grain (commodity, load_shape, year, quarter, month, hour_of_year),
);

WITH
all_commodity_load_shape_ts AS (
    SELECT
        commodity,
        load_shape,
        year, month, hour_of_year,
        saved_energy_units
    FROM california.commodity_load_shape_ts
    -- UNION ALL TODO add more load shapes
),

all_commodity_load_shape_ts_with_month AS (
    SELECT
        commodity,
        load_shape,
        year,
        COALESCE(month,
        CASE
            WHEN FLOOR(hour_of_year / 24) + 1 <= 31 THEN 1
            WHEN FLOOR(hour_of_year / 24) + 1 <= 59 THEN 2
            WHEN FLOOR(hour_of_year / 24) + 1 <= 90 THEN 3
            WHEN FLOOR(hour_of_year / 24) + 1 <= 120 THEN 4
            WHEN FLOOR(hour_of_year / 24) + 1 <= 151 THEN 5
            WHEN FLOOR(hour_of_year / 24) + 1 <= 181 THEN 6
            WHEN FLOOR(hour_of_year / 24) + 1 <= 212 THEN 7
            WHEN FLOOR(hour_of_year / 24) + 1 <= 243 THEN 8
            WHEN FLOOR(hour_of_year / 24) + 1 <= 273 THEN 9
            WHEN FLOOR(hour_of_year / 24) + 1 <= 304 THEN 10
            WHEN FLOOR(hour_of_year / 24) + 1 <= 334 THEN 11
            ELSE 12
        END) AS month,
        hour_of_year,
        saved_energy_units
    FROM all_commodity_load_shape_ts
)

SELECT
    commodity, load_shape,
    year,
    (month - 1) / 3 + 1 AS quarter,
    month, hour_of_year,
    saved_energy_units
FROM all_commodity_load_shape_ts_with_month
--ORDER BY commodity, load_shape, year, quarter, month, hour_of_year
