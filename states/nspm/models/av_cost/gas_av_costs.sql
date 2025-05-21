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
    read_csv_auto('states/california/test_data/test_real_data_calculations_aggregated/full_ca_avoided_costs_2020acc_gas.csv')
