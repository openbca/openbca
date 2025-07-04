MODEL(
    name california.gas_av_costs,
    kind FULL,
    grain (utility, year, month),
);

SELECT
    utility, region,
    total, marginal_ghg,
    market, t_d, environment, btm_methane, upstream_methane,
    year, quarter, month
FROM
    read_csv_auto('models/reference/avoided_costs/california/full_ca_avoided_costs_2020acc_gas.csv')
