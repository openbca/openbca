MODEL(
    name flexvalue_reference.gas_av_costs,
    kind FULL,
    grain (utility, year, month),
);

SELECT
    utility, region,
    datetime::TIMESTAMP AS datetime,
    total, marginal_ghg,
    market, t_d, environment, btm_methane, upstream_methane,
    EXTRACT(year from datetime::TIMESTAMP) AS year,
    EXTRACT(quarter from datetime::TIMESTAMP) AS quarter,
    EXTRACT(month from datetime::TIMESTAMP) AS month,
    (EXTRACT(DOY FROM datetime::TIMESTAMP) - 1) * 24 + EXTRACT(HOUR FROM datetime::TIMESTAMP) AS hour_of_year
FROM
    read_csv_auto('test_data/test_real_data_calculations_aggregated/full_ca_avoided_costs_2020acc_gas.csv')
