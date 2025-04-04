MODEL (
      name flexvalue.elec_av_costs,
      kind INCREMENTAL_BY_TIME_RANGE (
        time_column datetime
      ),
      grain (value_curve_name, utility, region, datetime),
);

select
    utility, region,
    datetime,
    total, marginal_ghg,
    EXTRACT(year from datetime) as year,
    EXTRACT(quarter from datetime) as quarter,
    EXTRACT(month from datetime) as month,
    EXTRACT(hour from datetime) as hour_of_day,
    (EXTRACT(DOY FROM datetime) - 1) * 24 + EXTRACT(HOUR FROM datetime) AS hour_of_year
from
    read_parquet('parquet/elec_av_costs/*.parquet')
