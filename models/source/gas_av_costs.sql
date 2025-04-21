MODEL (
      name flexvalue.gas_av_costs,
      kind INCREMENTAL_BY_TIME_RANGE (
        time_column datetime
      ),
      grain (utility, region, datetime),
);

select
    utility, region,
    year, quarter, month, datetime,
    total, marginal_ghg,
    market, t_d, environment, btm_methane, upstream_methane, value_curve_name
from read_parquet('parquet/gas_av_costs/*.parquet')
