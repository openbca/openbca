MODEL(
    name flexvalue.project_commodity_load_shape_ts,
    kind FULL,
    grain (project_id, year, month, hour_of_year)
);

SELECT
    pc.project_id, pc.load_shape,
    pc.commodity, pc.utility, pc.region,
    pdr_ts.year, pdr_ts.quarter,
    cls_ts.month, cls_ts.hour_of_year, cls_ts.hour_of_day,
    cls_ts.value AS load_shape_value,
    pdr_ts.discount,
    pdr_ts.gross_adjusted_savings,
    pdr_ts.gross_adjusted_savings * cls_ts.value AS net_energy_savings,
    net_energy_savings * pdr_ts.discount AS discounted_net_energy_savings,
FROM flexvalue.commodity_load_shape_ts cls_ts
JOIN project.project_commodity pc
    ON cls_ts.commodity = pc.commodity AND cls_ts.utility = pc.utility
        AND cls_ts.load_shape = pc.load_shape
JOIN project.project_discount_rate_ts pdr_ts
    ON pdr_ts.project_id = pc.project_id
    AND pdr_ts.quarter = cls_ts.quarter
