MODEL(
    name california.elec_av_costs,
    kind FULL,
    grain (utility, region, year, hour_of_year),
);

SELECT
    utility, region,
    energy, losses, ancillary_services, capacity,
    transmission, distribution, cap_and_trade, ghg_adder, ghg_rebalancing,
    methane_leakage, ghg_adder_rebalancing,
    total, marginal_ghg,
    year, quarter, month, hour_of_day, hour_of_year
FROM
    read_csv_auto('reference/models/avoided_costs/california/full_ca_avoided_costs_2020acc.csv.gz')
