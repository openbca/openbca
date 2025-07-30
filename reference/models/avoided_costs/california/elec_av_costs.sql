MODEL(
    name california.elec_av_costs,
    kind FULL,
    grain (utility, region, year, hour_of_year),
);

SELECT * FROM (
    SELECT
        'full_ca_avoided_costs_2020acc' as avoided_cost_version,
        utility, region,
        energy, losses, ancillary_services, capacity,
        transmission, distribution, cap_and_trade, ghg_adder, ghg_rebalancing,
        methane_leakage, ghg_adder_rebalancing,
        total, marginal_ghg,
        year, quarter, month, hour_of_day, hour_of_year
    FROM
        read_csv_auto('reference/models/avoided_costs/california/full_ca_avoided_costs_2020acc.csv.gz')
    UNION ALL
    SELECT
        'full_ca_avoided_costs_2020acc_v2' as avoided_cost_version,
        utility, region,
        energy * 100000, losses, ancillary_services, capacity,
        transmission, distribution, cap_and_trade, ghg_adder, ghg_rebalancing,
        methane_leakage, ghg_adder_rebalancing,
        total, marginal_ghg,
        year, quarter, month, hour_of_day, hour_of_year
    FROM
        read_csv_auto('reference/models/avoided_costs/california/full_ca_avoided_costs_2020acc.csv.gz')
)
-- ORDER BY
--     avoided_cost_version, utility, region, year, quarter, month, hour_of_year, hour_of_day
