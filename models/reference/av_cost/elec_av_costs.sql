MODEL(
    name flexvalue_reference.elec_av_costs,
    kind FULL,
    grain (utility, region, year, hour_of_year),
);

SELECT
    utility, region,
    datetime::TIMESTAMP AS datetime,
    energy, losses, ancillary_services, capacity,
    transmission, distribution, cap_and_trade, ghg_adder, ghg_rebalancing,
    methane_leakage, ghg_adder_rebalancing,
    total, marginal_ghg,
    EXTRACT(year from datetime::TIMESTAMP) AS year,
    EXTRACT(quarter from datetime::TIMESTAMP) AS quarter,
    EXTRACT(month from datetime::TIMESTAMP) AS month,
    EXTRACT(hour from datetime::TIMESTAMP) AS hour_of_day,
--         (EXTRACT(DOY FROM datetime::TIMESTAMP) - 1) * 24 + EXTRACT(HOUR FROM datetime::TIMESTAMP) AS hour_of_year somehow this gives very different result than the existing hour_of_year field
    hour_of_year
FROM
    read_csv_auto('test_data/test_real_data_calculations_aggregated/full_ca_avoided_costs_2020acc.csv.gz')
