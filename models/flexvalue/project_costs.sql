MODEL (
  name flexvalue.project_costs,
  kind FULL,
  grain project_id,
);

select
    project_id,
    utility, region, start_year, start_quarter,
    -- beginning of the quarter when the project starts.
    make_timestamp(start_year, (start_quarter - 1) * 3 + 1, 1, 0, 0, 0) as project_start_quater,
    discount_rate, eul, units, ntg,
    mwh_savings, therms_savings,
    load_shape,
    therms_profile,
    admin_cost + (((1 - ntg) * incentive_cost) + (ntg * measure_cost)) / (1 + (discount_rate / 4.0))
        as trc_costs,
    admin_cost + (incentive_cost / (1 + (discount_rate / 4.0)))
        as pac_costs
from
    flexvalue.project
