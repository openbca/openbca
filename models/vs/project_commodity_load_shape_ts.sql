MODEL(
    name flexvalue.project_commodity_load_shape_ts,
    kind FULL,
    grain (project_id, year, month, hour_of_year)
);

WITH
project_commodity_ts AS (
    SELECT
        project_discount_rate_ts.*,
        unnest([
            {'commodity': 'ELECTRICITY', 'load_shape': load_shape},
            {'commodity': 'GAS', 'load_shape': therms_profile}
        ], recursive := true)
    FROM flexvalue.project_discount_rate_ts
    JOIN flexvalue_input.projects ON project_discount_rate_ts.project_id = projects.project_id
)
SELECT
    vsts.project_id, cls_ts.load_shape,
    vsts.commodity, vsts.utility, vsts.region,
    vsts.year, vsts.quarter,
    cls_ts.month,
    cls_ts.hour_of_year, cls_ts.hour_of_day,
    cls_ts.value AS load_shape_value,
    discount,
    gross_adjusted_savings,
    gross_adjusted_savings * cls_ts.value AS net_energy_savings,
    net_energy_savings * discount AS discounted_net_energy_savings,
FROM flexvalue.commodity_load_shape_ts cls_ts
JOIN project_commodity_ts vsts
    ON vsts.commodity = cls_ts.commodity
        AND vsts.load_shape = cls_ts.load_shape AND vsts.utility = cls_ts.utility
        AND vsts.quarter = cls_ts.quarter
