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
    UPPER(load_shape) as load_shape,
    UPPER(therms_profile) as therms_profile
from read_parquet('parquet/project/*.parquet')
