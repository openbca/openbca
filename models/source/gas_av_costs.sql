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
    total, marginal_ghg
from read_parquet('parquet/gas_av_costs/*.parquet')
