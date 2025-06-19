MODEL(
    name california.elec_avoided_marginal_ghg_ton_co2_per_kwh,
    kind VIEW,
    grain (version, utility, region, year, hour_of_year),
);

SELECT
    utility, region, 'full_ca_avoided_costs_2020acc' as avoided_cost_version,
    marginal_ghg,
    year, quarter, month, hour_of_day, hour_of_year
FROM
    read_csv_auto('models/reference/avoided_costs/california/data/full_ca_avoided_costs_2020acc.csv.gz')
