MODEL(
    name openbca_core.measure_commodity_impact_ts,
    kind VIEW,
    grain (measure_id, commodity, avoided_cost, year, month, hour_of_year),
);

WITH
constant AS (
    SELECT
        pcls_ts.*,
        av_ts.avoided_cost, av_ts.av_cost_dollar_per_energy_unit
    FROM openbca_core.all_avoided_costs_ts av_ts
    JOIN openbca_core.measure_commodity_load_shape_ts pcls_ts
        ON pcls_ts.commodity = av_ts.commodity
        --AND pcls_ts.avoided_cost_version = av_ts.avoided_cost_version
        AND pcls_ts.avoided_cost_subset IS NOT DISTINCT FROM av_ts.avoided_cost_subset
    WHERE
        av_ts.year IS NULL AND av_ts.month IS NULL AND av_ts.hour_of_year IS NULL
),
annual AS (
    SELECT
        pcls_ts.*,
        av_ts.avoided_cost, av_ts.av_cost_dollar_per_energy_unit
    FROM openbca_core.all_avoided_costs_ts av_ts
    JOIN openbca_core.measure_commodity_load_shape_ts pcls_ts
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
        av_ts.avoided_cost, av_ts.av_cost_dollar_per_energy_unit
    FROM openbca_core.all_avoided_costs_ts av_ts
    JOIN openbca_core.measure_commodity_load_shape_ts pcls_ts
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
        av_ts.avoided_cost, av_ts.av_cost_dollar_per_energy_unit
    FROM openbca_core.all_avoided_costs_ts av_ts
    JOIN openbca_core.measure_commodity_load_shape_ts pcls_ts
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
        av_ts.avoided_cost, av_ts.av_cost_dollar_per_energy_unit
    FROM openbca_core.all_avoided_costs_ts av_ts
    JOIN openbca_core.measure_commodity_load_shape_ts pcls_ts
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
        av_ts.avoided_cost, av_ts.av_cost_dollar_per_energy_unit
    FROM openbca_core.all_avoided_costs_ts av_ts
    JOIN openbca_core.measure_commodity_load_shape_ts pcls_ts
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
    pci_ts.*,
    net_energy_savings_ts * discount_factor * av_cost_dollar_per_energy_unit AS impact_value
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
) pci_ts JOIN measure.measure_commodity_avoided_costs pcac
    ON pci_ts.measure_id = pcac.measure_id AND (pcac.avoided_cost IS NULL OR pci_ts.avoided_cost = pcac.avoided_cost)
