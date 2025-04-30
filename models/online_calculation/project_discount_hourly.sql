MODEL(
    name flexvalue.project_discount_hourly,
    kind FULL,
    grain (
        project_id,
        datetime
    ),
);
-- Expose project data and calculate discount as hourly timeseries
SELECT
    project_id,
    utility,
    region,
    year, hour_of_year,
    admin_cost,
    ntg,
    measure_cost,
    incentive_cost,
    discount_rate,
    units,
    mwh_savings,
    admin_cost + (((1 - ntg) * incentive_cost) + (ntg * measure_cost)) / (1 + (discount_rate / 4.0)) as trc_costs,
    admin_cost + (incentive_cost / (1 + (discount_rate / 4.0))) as pac_costs,
    1.0 / POW(1.0 + (discount_rate / 4.0), ((year - start_year) * 4) + quarter - start_quarter) AS discount
FROM (
    SELECT
      *,
      EXTRACT(YEAR FROM datetime) AS year,
      EXTRACT(QUARTER FROM datetime) AS quarter,
      EXTRACT(DAYOFYEAR FROM datetime)*24 + EXTRACT(HOUR FROM datetime) AS hour_of_year,
    FROM flexvalue.project_info,
    LATERAL generate_series(
      project_start_quarter,
      project_end_quarter - INTERVAL 1 HOUR,
      INTERVAL 1 HOUR
    ) AS g(datetime)
)
