MODEL(
    name flexvalue.project_value_stream_benefits_ts,
    kind FULL,
    grain (project_id, commodity, year, hour_of_year),
);

SELECT
    pcls_ts.*,
    vs_ts.value_stream,
    vs_ts.value,
    discounted_net_energy_savings * vs_ts.value as benefit_value
FROM flexvalue.project_commodity_load_shape_ts pcls_ts
JOIN flexvalue.value_stream_ts vs_ts
    ON pcls_ts.state = vs_ts.state
    AND pcls_ts.region = vs_ts.region
    AND pcls_ts.commodity = vs_ts.commodity
    AND pcls_ts.year = vs_ts.year
    AND pcls_ts.month = vs_ts.month
    AND pcls_ts.hour_of_year IS NOT DISTINCT FROM vs_ts.hour_of_year
