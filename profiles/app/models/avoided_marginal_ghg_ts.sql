MODEL(
    name openbca_input.avoided_marginal_ghg_ts,
    kind FULL,
    grain (version, commodity, avoided_cost_subset, timestamp),
);

WITH regions AS (
    SELECT distinct region FROM app.elec_av_costs
)
SELECT
    'ELECTRICITY' AS commodity,
    utility || '_'|| region as avoided_cost_subset,
    CAST(year || '-01-01' AS DATE) + interval hour_of_year HOUR AS timestamp,
    marginal_ghg AS av_marginal_ghg_ton_co2_per_energy_unit
FROM app.elec_av_costs
UNION ALL
SELECT
    'GAS' AS commodity,
    utility || '_'|| r.region as avoided_cost_subset,
    CAST(year || '-01-01' AS DATE) + interval month MONTH AS timestamp,
    marginal_ghg as av_marginal_ghg_ton_co2_per_energy_unit
FROM app.gas_av_costs
CROSS JOIN regions r
