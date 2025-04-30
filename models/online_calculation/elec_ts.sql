MODEL (
  name flexvalue.elec_ts,
  kind FULL,
  grain id,
);
-- pre-joining elec_av_costs & elec_load_shape to speed up FlexValue calculation at runtime
SELECT
    elec_av_costs.*,
    elec_load_shape.* EXCLUDE (utility, region, quarter, month, hour_of_year, hour_of_day)
FROM flexvalue.elec_av_costs
JOIN flexvalue_input.elec_load_shape
    ON elec_av_costs.utility = elec_load_shape.utility
    AND elec_av_costs.hour_of_year = elec_load_shape.hour_of_year
