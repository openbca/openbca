MODEL(
    name openbca_impact.project_commodity_load_shape_ts,
    kind FULL,
    grain (project_id, year, month, hour_of_year)
);

WITH
commodity_load_shape_ts AS (
    SELECT
        commodity, load_shape,
        year,
        (month - 1) / 3 + 1 AS quarter,
        month, hour_of_year,
        saved_energy_units
    FROM openbca_reference.commodity_load_shape_ts
)
SELECT
    pc.project_id, pc.load_shape,
    pc.commodity, pc.avoided_cost_subset, pc.avoided_cost_version,
    pdr_ts.year, cls_ts.month, cls_ts.hour_of_year,
    cls_ts.saved_energy_units,
    pdr_ts.discount,
    pc.net_energy_savings,
    pc.net_energy_savings * saved_energy_units AS net_energy_savings_ts,
FROM commodity_load_shape_ts cls_ts
JOIN openbca_project.project_commodity pc
    ON cls_ts.commodity = pc.commodity
        AND cls_ts.load_shape = pc.load_shape
JOIN openbca_project.project_discount_rate_ts pdr_ts
    ON pdr_ts.project_id = pc.project_id
    AND pdr_ts.quarter = cls_ts.quarter
