MODEL(
    name openbca_reference.ref_period_hourly_ts,
    kind VIEW,
);

 SELECT
 	timestamp,
 	EXTRACT(year FROM timestamp) AS year,
    EXTRACT(quarter FROM timestamp) AS quarter,
    EXTRACT(month FROM timestamp) AS month,
    EXTRACT(day FROM timestamp) AS day,
    EXTRACT(hour FROM timestamp) AS hour_of_day,
    EXTRACT(doy FROM timestamp) AS day_of_year,
    (date_diff('hour', date_trunc('year', timestamp), timestamp)) AS hour_of_year
 FROM generate_series(
    DATE '2000-01-01',
    DATE '2100-01-07',
    INTERVAL '1 hour'
) AS ts(timestamp);
