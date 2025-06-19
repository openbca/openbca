MODEL(
    name california.gas_av_marginal_ghg_ton_co2_per_therm,
    kind VIEW,
    grain (version, utility, region, year, hour_of_year),
);

SELECT
    utility, region, 'full_ca_avoided_costs_2020acc_gas' as avoided_cost_version,
    marginal_ghg,
    year, quarter, month
FROM
    read_csv_auto('models/reference/avoided_costs/california/data/full_ca_avoided_costs_2020acc_gas.csv')
