MODEL(
    name california.gas_av_costs_dollar_per_therm,
    kind VIEW,
    grain (version, utility, year, month),
);

SELECT
    utility, region, 'full_ca_avoided_costs_2020acc_gas' as avoided_cost_version,
    market, t_d, environment, btm_methane, upstream_methane,
    year, quarter, month
FROM
    read_csv_auto('models/reference/avoided_costs/california/data/full_ca_avoided_costs_2020acc_gas.csv')
