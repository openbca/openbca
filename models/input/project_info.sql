MODEL (
  name flexvalue_input.project_info,
  kind FULL,
  grain project_id,
);

select *,
    project_start_quarter + eul * interval '1 year' as project_end_quarter
from (
    select
        id as project_id,
        utility, region,
        start_year, start_quarter,
        discount_rate, eul, units, ntg, admin_cost, incentive_cost, measure_cost,
        mwh_savings, therms_savings,
        load_shape as load_shape_name,
        UPPER(load_shape) as load_shape,
        UPPER(therms_profile) as therms_profile,
        make_timestamp(start_year, (start_quarter - 1) * 3 + 1, 1, 0, 0, 0) as project_start_quarter,
    from flexvalue_input.project
)
