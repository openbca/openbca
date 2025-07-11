MODEL(
<<<<<<<< HEAD:core/models/impact/measure_commodity_impact_ts.sql
    name openbca_core.measure_commodity_impact_ts,
========
    name openbca_core.project_commodity_impact_ts,
>>>>>>>> main:core/models/project_impact/project_commodity_impact_ts.sql
    kind VIEW,
    grain (measure_id, commodity, avoided_cost, year, month, hour_of_year),
);

WITH
constant AS (
    SELECT
        pcls_ts.*,
<<<<<<<< HEAD:core/models/impact/measure_commodity_impact_ts.sql
        av_ts.avoided_cost, av_ts.av_cost_dollar_per_energy_unit
    FROM openbca_core.all_avoided_costs_ts av_ts
    JOIN openbca_core.measure_commodity_load_shape_ts pcls_ts
========
        av_ts.avoided_cost, av_ts.value
    FROM openbca_core.all_avoided_costs_ts av_ts
    JOIN openbca_core.project_commodity_load_shape_ts pcls_ts
>>>>>>>> main:core/models/project_impact/project_commodity_impact_ts.sql
        ON pcls_ts.commodity = av_ts.commodity
        --AND pcls_ts.avoided_cost_version = av_ts.avoided_cost_version
        AND pcls_ts.avoided_cost_subset IS NOT DISTINCT FROM av_ts.avoided_cost_subset
    WHERE
        av_ts.year IS NULL AND av_ts.month IS NULL AND av_ts.hour_of_year IS NULL
),
annual AS (
    SELECT
        pcls_ts.*,
<<<<<<<< HEAD:core/models/impact/measure_commodity_impact_ts.sql
        av_ts.avoided_cost, av_ts.av_cost_dollar_per_energy_unit
    FROM openbca_core.all_avoided_costs_ts av_ts
    JOIN openbca_core.measure_commodity_load_shape_ts pcls_ts
========
        av_ts.avoided_cost, av_ts.value
    FROM openbca_core.all_avoided_costs_ts av_ts
    JOIN openbca_core.project_commodity_load_shape_ts pcls_ts
>>>>>>>> main:core/models/project_impact/project_commodity_impact_ts.sql
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
<<<<<<<< HEAD:core/models/impact/measure_commodity_impact_ts.sql
        av_ts.avoided_cost, av_ts.av_cost_dollar_per_energy_unit
    FROM openbca_core.all_avoided_costs_ts av_ts
    JOIN openbca_core.measure_commodity_load_shape_ts pcls_ts
========
        av_ts.avoided_cost, av_ts.value
    FROM openbca_core.all_avoided_costs_ts av_ts
    JOIN openbca_core.project_commodity_load_shape_ts pcls_ts
>>>>>>>> main:core/models/project_impact/project_commodity_impact_ts.sql
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
<<<<<<<< HEAD:core/models/impact/measure_commodity_impact_ts.sql
        av_ts.avoided_cost, av_ts.av_cost_dollar_per_energy_unit
    FROM openbca_core.all_avoided_costs_ts av_ts
    JOIN openbca_core.measure_commodity_load_shape_ts pcls_ts
========
        av_ts.avoided_cost, av_ts.value
    FROM openbca_core.all_avoided_costs_ts av_ts
    JOIN openbca_core.project_commodity_load_shape_ts pcls_ts
>>>>>>>> main:core/models/project_impact/project_commodity_impact_ts.sql
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
<<<<<<<< HEAD:core/models/impact/measure_commodity_impact_ts.sql
        av_ts.avoided_cost, av_ts.av_cost_dollar_per_energy_unit
    FROM openbca_core.all_avoided_costs_ts av_ts
    JOIN openbca_core.measure_commodity_load_shape_ts pcls_ts
========
        av_ts.avoided_cost, av_ts.value
    FROM openbca_core.all_avoided_costs_ts av_ts
    JOIN openbca_core.project_commodity_load_shape_ts pcls_ts
>>>>>>>> main:core/models/project_impact/project_commodity_impact_ts.sql
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
<<<<<<<< HEAD:core/models/impact/measure_commodity_impact_ts.sql
        av_ts.avoided_cost, av_ts.av_cost_dollar_per_energy_unit
    FROM openbca_core.all_avoided_costs_ts av_ts
    JOIN openbca_core.measure_commodity_load_shape_ts pcls_ts
========
        av_ts.avoided_cost, av_ts.value
    FROM openbca_core.all_avoided_costs_ts av_ts
    JOIN openbca_core.project_commodity_load_shape_ts pcls_ts
>>>>>>>> main:core/models/project_impact/project_commodity_impact_ts.sql
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
<<<<<<<< HEAD:core/models/impact/measure_commodity_impact_ts.sql
    net_energy_savings_ts * discount_factor * av_cost_dollar_per_energy_unit AS impact_value
========
    value as av_cost_value,
    net_energy_savings_ts * discount * av_cost_value AS impact_value
>>>>>>>> main:core/models/project_impact/project_commodity_impact_ts.sql
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
<<<<<<<< HEAD:core/models/impact/measure_commodity_impact_ts.sql
) pci_ts JOIN measure.measure_commodity_avoided_costs pcac
    ON pci_ts.measure_id = pcac.measure_id AND (pcac.avoided_cost IS NULL OR pci_ts.avoided_cost = pcac.avoided_cost)
========
) pci_ts JOIN project.project_commodity_avoided_costs pcac
    ON pci_ts.project_id = pcac.project_id AND (pcac.avoided_cost IS NULL OR pci_ts.avoided_cost = pcac.avoided_cost)
>>>>>>>> main:core/models/project_impact/project_commodity_impact_ts.sql
