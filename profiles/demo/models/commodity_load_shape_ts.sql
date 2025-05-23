MODEL(
    name flexvalue_input.commodity_load_shape_ts,
    kind FULL,
    grain (utility, commodity, hour_of_year),
);
SELECT
    u.utility,
    'ELECTRICITY' AS commodity,
    (CAST((h - 1) / 2190 AS INT) + 1) AS quarter,
    (CAST((h - 1) / 730 AS INT) + 1) AS month,
    h AS hour_of_year,
    (h - 1) % 24 + 1 AS hour_of_day,
    'NONRES_HVAC_SPLIT_PACKAGE_AC' AS load_shape,
    random() * 100 AS value
FROM range(1, 8761) AS h(h)
CROSS JOIN (SELECT unnest(['PGE']) AS utility) AS u
UNION ALL
SELECT
    u.utility,
    'GAS' AS commodity,
    m.month,
    ((m.month - 1) / 3 + 1)::INT AS quarter,
    NULL AS hour_of_year,
    NULL AS hour_of_day,
    'annual' AS load_shape,
    random() * 1000 AS value
FROM (SELECT unnest(['PGE']) AS utility) AS u
CROSS JOIN (SELECT * FROM range(1, 13) AS t(month)) AS m
