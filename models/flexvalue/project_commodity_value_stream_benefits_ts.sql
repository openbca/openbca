MODEL(
    name flexvalue.project_commodity_value_stream_benefits_ts,
    kind FULL,
    grain (project_id, commodity, year, hour_of_year),
);
WITH all_time_granularities_vs_ts AS (
    SELECT
        pcls_ts.*,
        vs_ts.value_stream, vs_ts.value
    FROM flexvalue.project_commodity_load_shape_ts pcls_ts
    JOIN flexvalue.value_stream_ts vs_ts
        ON pcls_ts.region = vs_ts.region AND pcls_ts.commodity = vs_ts.commodity
        AND pcls_ts.year = vs_ts.year AND pcls_ts.month = vs_ts.month AND pcls_ts.hour_of_year = vs_ts.hour_of_year
    WHERE vs_ts.hour_of_year IS NOT NULL

    UNION ALL

    SELECT
        pcls_ts.*,
        vs_ts.value_stream, vs_ts.value
    FROM flexvalue.project_commodity_load_shape_ts pcls_ts
    JOIN flexvalue.value_stream_ts vs_ts
        ON pcls_ts.region = vs_ts.region AND pcls_ts.commodity = vs_ts.commodity
        AND pcls_ts.year = vs_ts.year AND pcls_ts.month = vs_ts.month
    WHERE vs_ts.hour_of_year IS NULL AND vs_ts.month IS NOT NULL

    UNION ALL

    SELECT
        pcls_ts.*,
        vs_ts.value_stream, vs_ts.value
    FROM flexvalue.project_commodity_load_shape_ts pcls_ts
    JOIN flexvalue.value_stream_ts vs_ts
        ON pcls_ts.region = vs_ts.region AND pcls_ts.commodity = vs_ts.commodity
        AND pcls_ts.year = vs_ts.year
    WHERE vs_ts.hour_of_year IS NULL AND vs_ts.month IS NULL AND vs_ts.year IS NOT NULL

    UNION ALL

    SELECT
        pcls_ts.*,
        vs_ts.value_stream, vs_ts.value
    FROM flexvalue.project_commodity_load_shape_ts pcls_ts
    JOIN flexvalue.value_stream_ts vs_ts
        ON pcls_ts.region = vs_ts.region AND pcls_ts.commodity = vs_ts.commodity
    WHERE vs_ts.hour_of_year IS NULL AND vs_ts.month IS NULL AND vs_ts.year IS NULL
)
 SELECT
     *,
    CASE
        WHEN value_stream = 'marginal_ghg' THEN net_energy_savings * value
        ELSE discounted_net_energy_savings * value END
    AS benefit_value
 FROM
    all_time_granularities_vs_ts
