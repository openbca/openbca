MODEL(
    name openbca_reference.ref_period_monthly_ts,
    kind VIEW,
);

 SELECT
 	timestamp,
 	EXTRACT(year FROM timestamp) AS year,
    EXTRACT(quarter FROM timestamp) AS quarter,
    EXTRACT(month FROM timestamp) AS month
 FROM generate_series(
    DATE '2000-01-01',
    DATE '2100-01-07',
    INTERVAL '1 month'
) AS ts(timestamp);
