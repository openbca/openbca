MODEL(
    name california.avoided_costs_ts,
    kind FULL,
    grain (commodity, avoided_cost_version, avoided_cost_subset, avoided_cost, year, month, hour_of_year),
);

WITH regions AS (
    SELECT distinct region FROM california.elec_av_costs_dollar_per_kwh
)

SELECT * FROM (
    SELECT
        'ELECTRICITY' AS commodity,
        avoided_cost_version,
        avoided_cost,
        utility || '_'|| region AS avoided_cost_subset,
        year, month, hour_of_year,
        av_costs_dollar_per_kwh AS av_costs_dollar_per_energy_unit
    FROM california.elec_av_costs_dollar_per_kwh
    UNPIVOT (
        av_costs_dollar_per_kwh FOR avoided_cost IN (
            energy, losses, ancillary_services, capacity,
            transmission, distribution, cap_and_trade,
            ghg_adder, ghg_rebalancing,
            methane_leakage, ghg_adder_rebalancing
        )
    )
    UNION ALL
    SELECT
        'GAS' AS commodity,
        avoided_cost_version,
        avoided_cost,
        utility || '_'|| r.region AS avoided_cost_subset,
        year, month, NULL AS hour_of_year,
        av_costs_dollar_per_therm AS av_costs_dollar_per_energy_unit
    FROM california.gas_av_costs_dollar_per_therm
    UNPIVOT (
        av_costs_dollar_per_therm FOR avoided_cost IN (
            market, t_d, environment, btm_methane, upstream_methane,
        )
    )
    CROSS JOIN regions r
)
-- ORDER BY
--     commodity, avoided_cost_version, avoided_cost_subset, avoided_cost, year, month, hour_of_year
