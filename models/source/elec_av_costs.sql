MODEL (
      name flexvalue.elec_av_costs,
--       kind INCREMENTAL_BY_TIME_RANGE (
--         time_column datetime
--       ),
      kind FULL,
      grain (value_curve_name, utility, region, datetime),
);

select
    utility, region,
    datetime::TIMESTAMP,
    total, marginal_ghg,
    EXTRACT(year from datetime::TIMESTAMP) as year,
    EXTRACT(quarter from datetime::TIMESTAMP) as quarter,
    EXTRACT(month from datetime::TIMESTAMP) as month,
    EXTRACT(hour from datetime::TIMESTAMP) as hour_of_day,
    (EXTRACT(DOY FROM datetime::TIMESTAMP) - 1) * 24 + EXTRACT(HOUR FROM datetime::TIMESTAMP) AS hour_of_year
from
    --read_parquet('parquet/elec_av_costs/*.parquet')
    read_parquet('parquet/ca_combined_value_curve_electric/*.parquet')
