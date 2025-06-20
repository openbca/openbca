MODEL(
    name openbca.project_commodity_impact_ts,
    kind VIEW,
    grain (project_id, commodity, avoided_cost, year, month, hour_of_year),
);

WITH
constant AS (
    SELECT
        pcls_ts.*,
        av_ts.avoided_cost, av_ts.value
    FROM openbca_input.avoided_costs_ts av_ts
    JOIN openbca.project_commodity_load_shape_ts pcls_ts
        ON pcls_ts.commodity = av_ts.commodity
        --AND pcls_ts.avoided_cost_version = av_ts.avoided_cost_version
        AND pcls_ts.avoided_cost_subset IS NOT DISTINCT FROM av_ts.avoided_cost_subset
    WHERE
        av_ts.year IS NULL AND av_ts.month IS NULL AND av_ts.hour_of_year IS NULL
),
annual AS (
    SELECT
        pcls_ts.*,
        av_ts.avoided_cost, av_ts.value
    FROM openbca_input.avoided_costs_ts av_ts
    JOIN openbca.project_commodity_load_shape_ts pcls_ts
        ON pcls_ts.commodity = av_ts.commodity
        --AND pcls_ts.avoided_cost_version = av_ts.avoided_cost_version
        AND pcls_ts.avoided_cost_subset IS NOT DISTINCT FROM av_ts.avoided_cost_subset
        AND pcls_ts.year = av_ts.year
    WHERE
        av_ts.year IS NOT NULL AND av_ts.month IS NULL AND av_ts.hour_of_year IS NULL
),
monthly_cross_years AS (
    SELECT
        pcls_ts.*,
        av_ts.avoided_cost, av_ts.value
    FROM openbca_input.avoided_costs_ts av_ts
    JOIN openbca.project_commodity_load_shape_ts pcls_ts
        ON pcls_ts.commodity = av_ts.commodity
        --AND pcls_ts.avoided_cost_version = av_ts.avoided_cost_version
        AND pcls_ts.avoided_cost_subset IS NOT DISTINCT FROM av_ts.avoided_cost_subset
        AND pcls_ts.month = av_ts.month
    WHERE
        av_ts.year IS NULL AND av_ts.month IS NOT NULL AND av_ts.hour_of_year IS NULL
),
monthly_with_year AS (
    SELECT
        pcls_ts.*,
        av_ts.avoided_cost, av_ts.value
    FROM openbca_input.avoided_costs_ts av_ts
    JOIN openbca.project_commodity_load_shape_ts pcls_ts
        ON pcls_ts.commodity = av_ts.commodity
        --AND pcls_ts.avoided_cost_version = av_ts.avoided_cost_version
        AND pcls_ts.avoided_cost_subset IS NOT DISTINCT FROM av_ts.avoided_cost_subset
        AND pcls_ts.year = av_ts.year
        AND pcls_ts.month = av_ts.month
    WHERE
        av_ts.year IS NOT NULL AND av_ts.month IS NOT NULL AND av_ts.hour_of_year IS NULL
),
hourly_by_hour_of_year_cross_years AS (
    SELECT
        pcls_ts.*,
        av_ts.avoided_cost, av_ts.value
    FROM openbca_input.avoided_costs_ts av_ts
    JOIN openbca.project_commodity_load_shape_ts pcls_ts
        ON pcls_ts.commodity = av_ts.commodity
        --AND pcls_ts.avoided_cost_version = av_ts.avoided_cost_version
        AND pcls_ts.avoided_cost_subset IS NOT DISTINCT FROM av_ts.avoided_cost_subset
        AND pcls_ts.hour_of_year = av_ts.hour_of_year
    WHERE
        pcls_ts.hour_of_year IS NOT NULL AND
        av_ts.year IS NULL AND av_ts.hour_of_year IS NOT NULL
),
hourly_by_hour_of_year_with_year AS (
    SELECT
        pcls_ts.*,
        av_ts.avoided_cost, av_ts.value
    FROM openbca_input.avoided_costs_ts av_ts
    JOIN openbca.project_commodity_load_shape_ts pcls_ts
        ON pcls_ts.commodity = av_ts.commodity
        --AND pcls_ts.avoided_cost_version = av_ts.avoided_cost_version
        AND pcls_ts.avoided_cost_subset IS NOT DISTINCT FROM av_ts.avoided_cost_subset
        AND pcls_ts.year = av_ts.year
        AND pcls_ts.hour_of_year = av_ts.hour_of_year
    WHERE
        pcls_ts.hour_of_year IS NOT NULL AND
        av_ts.year IS NOT NULL AND av_ts.hour_of_year IS NOT NULL
)
SELECT
     *,
    value as av_cost_value,
    net_energy_savings_ts * discount * av_cost_value AS impact_value
 FROM (
    SELECT * FROM constant
    UNION ALL
    SELECT * FROM annual
    UNION ALL
    SELECT * FROM monthly_cross_years
    UNION ALL
    SELECT * FROM monthly_with_year
    UNION ALL
    SELECT * FROM hourly_by_hour_of_year_cross_years
    UNION ALL
    SELECT * FROM hourly_by_hour_of_year_with_year
)
