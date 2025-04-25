MODEL(
    name flexvalue.elec_av_costs,
    kind FULL,
    grain (utility, region, year, hour_of_year),
);

SELECT
    utility, region,
    hour_of_year,
    year,
    month,
    hour_of_day,
    datetime,
    quarter,
    energy, losses, ancillary_services,
    capacity, transmission, distribution,
    cap_and_trade, ghg_adder, ghg_rebalancing,
    methane_leakage, total, marginal_ghg,
    ghg_adder_rebalancing
FROM flexvalue_input.elec_av_costs
