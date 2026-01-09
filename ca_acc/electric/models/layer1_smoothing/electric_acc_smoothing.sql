MODEL(
    name ca_acc_layer1_smoothing.electric_acc_smoothed,
    kind FULL,
);

with net_peak_period as (
    select
    utility
    , region
    , year
    , avg(capacity) as net_avg_capacity
    , avg(transmission) as net_avg_transmission
    , avg(distribution) as net_avg_distribution
    from
    ca_acc_layer0_scraping.acc_electric_model_ts
    where
    month between 6 and 9
    and hour_of_day between 19 and 20
    group by
    utility
    , region
    , year
    )

    , gross_peak_period as (
    select
    utility
    , region
    , year
    , avg(capacity) as gross_avg_capacity
    , avg(transmission) as gross_avg_transmission
    , avg(distribution) as gross_avg_distribution
    from
    ca_acc_layer0_scraping.acc_electric_model_ts
    where
    month between 6 and 9
    and hour_of_day between 16 and 18
    group by
    utility
    , region
    , year
    )

    , off_peak_period as (
    select
    utility
    , region
    , year
    , avg(capacity) as off_avg_capacity
    , avg(transmission) as off_avg_transmission
    , avg(distribution) as off_avg_distribution
    from
    ca_acc_layer0_scraping.acc_electric_model_ts
    where not (
    month between 6 and 9
    and hour_of_day between 16 and 20 )
    group by
    utility
    , region
    , year
    )

    , smoothed_values as (
    select
    n.*
    , g.* except(utility, region, year)
    , o.* except(utility, region, year)
    from
    net_peak_period n
    join gross_peak_period g on
    n.utility = g.utility
    and n.region = g.region
    and n.year = g.year
    join off_peak_period o on 
    n.utility = o.utility
    and n.region = o.region
    and n.year = o.year
    )

    select
    acc.* except(total, capacity, transmission, distribution)
    , energy+losses+ancillary_services+capacity+transmission+distribution+cap_and_trade+ghg_adder+ghg_rebalancing+methane_leakage as total_raw 
    , capacity as capacity_raw
    , transmission as transmission_raw
    , distribution as distribution_raw
    , net_avg_capacity as capacity
    , net_avg_transmission as transmission
    , net_avg_distribution as distribution
    , energy+losses+ancillary_services+cap_and_trade+ghg_adder+ghg_rebalancing+methane_leakage + (net_avg_capacity + net_avg_transmission + net_avg_distribution) as total
    from 
    ca_acc_layer0_scraping.acc_electric_model_ts acc
    join smoothed_values sv on
    acc.utility = sv.utility
    and acc.region = sv.region
    and acc.year = sv.year
    where 
    month between 6 and 9
    and hour_of_day between 19 and 20

    union all

    select
    acc.* except(total, capacity, transmission, distribution)
    , energy+losses+ancillary_services+capacity+transmission+distribution+cap_and_trade+ghg_adder+ghg_rebalancing+methane_leakage as total_raw 
    , capacity as capacity_raw
    , transmission as transmission_raw
    , distribution as distribution_raw
    , gross_avg_capacity as capacity
    , gross_avg_transmission as transmission
    , gross_avg_distribution as distribution
    , energy+losses+ancillary_services+cap_and_trade+ghg_adder+ghg_rebalancing+methane_leakage + (gross_avg_capacity + gross_avg_transmission + gross_avg_distribution) as total
    from 
    ca_acc_layer0_scraping.acc_electric_model_ts acc
    join smoothed_values sv on
    acc.utility = sv.utility
    and acc.region = sv.region
    and acc.year = sv.year
    where 
    month between 6 and 9
    and hour_of_day between 16 and 18

    union all

    select
    acc.* except(total, capacity, transmission, distribution)
    , energy+losses+ancillary_services+capacity+transmission+distribution+cap_and_trade+ghg_adder+ghg_rebalancing+methane_leakage as total_raw
    , capacity as capacity_raw
    , transmission as transmission_raw
    , distribution as distribution_raw
    , off_avg_capacity as capacity
    , off_avg_transmission as transmission
    , off_avg_distribution as distribution
    , energy+losses+ancillary_services+cap_and_trade+ghg_adder+ghg_rebalancing+methane_leakage + (off_avg_capacity + off_avg_transmission + off_avg_distribution) as total
    from 
    ca_acc_layer0_scraping.acc_electric_model_ts acc
    join smoothed_values sv on
    acc.utility = sv.utility
    and acc.region = sv.region
    and acc.year = sv.year
    where not (
    month between 6 and 9
    and hour_of_day between 16 and 20 )