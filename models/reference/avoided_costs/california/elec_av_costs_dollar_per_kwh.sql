MODEL(
    name california.elec_av_costs_dollar_per_kwh,
    kind VIEW,
    grain (version, utility, region, year, hour_of_year),
);

SELECT
    utility, region, 'full_ca_avoided_costs_2020acc' as avoided_cost_version,
    energy, losses, ancillary_services, capacity,
    transmission, distribution, cap_and_trade, ghg_adder, ghg_rebalancing,
    methane_leakage, ghg_adder_rebalancing,
    year, quarter, month, hour_of_day, hour_of_year
FROM
    read_csv_auto('models/reference/avoided_costs/california/data/full_ca_avoided_costs_2020acc.csv.gz')
