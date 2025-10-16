MODEL(
    name openbca_core.measure_commodity_load_shape_ts,
    kind VIEW,
    grain (measure_id, year, month, hour_of_year)
);

SELECT
    mc.measure_id,
    mc.commodity, mc.avoided_cost_subset,
    m_ts.year, m_ts.quarter,
    cls_ts.month, cls_ts.hour_of_year, cls_ts.hour_of_day,
    cls_ts.load_shape_normalized_fraction AS load_shape_normalized_fraction,
    m_ts.discount_factor,
--     mc.net_energy_savings,
    mc.net_energy_savings * load_shape_normalized_fraction AS net_energy_savings_ts,
FROM openbca_core.all_commodity_load_shape_ts cls_ts
JOIN measure.measure_commodity mc
    ON cls_ts.commodity = mc.commodity
        AND cls_ts.load_shape = mc.load_shape_mapping
JOIN measure.measure_discount_rate_factor_ts m_ts
    ON m_ts.measure_id = mc.measure_id
    AND m_ts.quarter = cls_ts.quarter
