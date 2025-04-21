MODEL (
  name flexvalue.project,
  kind FULL,
  grain project_id,
);

select
    id as project_id,
    utility, region,
    start_year, start_quarter,
    discount_rate, eul, units, ntg, admin_cost, incentive_cost, measure_cost,
    mwh_savings, therms_savings,
    value_curve_name,
    make_timestamp(start_year, (start_quarter - 1) * 3 + 1, 1, 0, 0, 0) as project_start_quarter,
    project_start_quarter + eul * interval '1 year' as project_end_quarter,
    UPPER(load_shape) as load_shape,
    UPPER(therms_profile) as therms_profile
from read_parquet('parquet/project/*.parquet')
