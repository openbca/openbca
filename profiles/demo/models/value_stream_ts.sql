MODEL(
    name flexvalue_input.value_stream_ts,
    kind FULL,
    grain (utility, region, commodity, value_stream, year, hour_of_year),
);

-- IMPORTANT NOTE: The time-granularity of the value_stream_ts table cannot be lower than the time-granularity of the commodity_load_shape_ts table.
-- For instance, if the commodity_load_shape_ts table is monthly then the value_stream_ts table cannot be hourly.

SELECT
    utility, region,
    commodity AS commodity,
    NULL AS year, NULL AS quarter, NULL AS month,
    NULL AS hour_of_year, NULL AS hour_of_day,
    'marginal_cost' AS value_stream,
    marginal_cost AS value
FROM demo.marginal_cost

UNION ALL

SELECT
    u.utility,
    r.region,
    'ELECTRICITY' AS commodity,
    (2020 + ((h - 1) / 8760))::INT AS year,
    (((h - 1) / 2190) % 4 + 1)::INT AS quarter,
    (((h - 1) / 730) % 12 + 1)::INT AS month,
    h AS hour_of_year,
    ((h - 1) % 24 + 1)::INT AS hour_of_day,
    vs.value_stream,
    random() AS value
FROM generate_series(1, 8760 * 13) AS h(h)  -- 13 years of hourly data
CROSS JOIN (SELECT unnest(ARRAY['PGE']) AS utility) AS u
CROSS JOIN (SELECT unnest(ARRAY['CZ12', 'CZ2']) AS region) AS r
CROSS JOIN (
    SELECT unnest(ARRAY['total', 'marginal_ghg', 'energy', 'losses', 'ancillary_services', 'capacity']) AS value_stream
) AS vs

UNION ALL

SELECT
    u.utility,
    r.region,
    'GAS' AS commodity,
    (2020 + ((m.month - 1) / 12))::INT AS year,
    (((m.month - 1) % 12) / 3 + 1)::INT AS quarter,
    (((m.month - 1) % 12) + 1)::INT AS month,
    NULL AS hour_of_year,
    NULL AS hour_of_day,
    vs.value_stream,
    random() AS value
FROM (SELECT unnest(ARRAY['PGE']) AS utility) AS u
CROSS JOIN (SELECT unnest(ARRAY['CZ12', 'CZ2']) AS region) AS r
CROSS JOIN (SELECT * FROM generate_series(1, 12 * 13) AS t(month)) AS m  -- 13 years of monthly data
CROSS JOIN (
    SELECT unnest(ARRAY['total', 'marginal_ghg', 'market', 't_d', 'environment', 'btm_methane', 'upstream_methane']) AS value_stream
) AS vs;
