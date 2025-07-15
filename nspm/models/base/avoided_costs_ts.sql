MODEL(
    name openbca_input.avoided_costs_ts,
    kind FULL,
    grain (commodity, avoided_cost_subset, avoided_cost, year, hour_of_year),
);

select
    'ELECTRICITY' AS commodity,
    NULL AS avoided_cost_subset,
    year,
    NULL AS quarter,
    month AS month,
    hour as hour_of_year,
    NULL AS hour_of_day,
    value_stream AS avoided_cost,
    value AS av_cost_dollar_per_energy_unit
from openbca.nspm_raw.value_stream_timeseries
