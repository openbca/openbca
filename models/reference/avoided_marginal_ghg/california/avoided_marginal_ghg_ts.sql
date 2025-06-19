MODEL(
    name california.avoided_marginal_ghg_ts,
    kind FULL,
    grain (version, commodity, avoided_cost_subset, timestamp),
);

WITH regions AS (
    SELECT distinct region FROM california.elec_avoided_marginal_ghg_ton_co2_per_kwh
)

SELECT
    'ELECTRICITY' AS commodity,
    avoided_cost_version,
    utility || '_'|| region as avoided_cost_subset,
    CAST(year || '-01-01' AS DATE) + interval hour_of_year HOUR AS timestamp,
    marginal_ghg AS av_marginal_ghg_ton_co2_per_energy_unit
FROM california.elec_avoided_marginal_ghg_ton_co2_per_kwh
UNION ALL
SELECT
    'GAS' AS commodity,
    avoided_cost_version,
    utility || '_'|| r.region as avoided_cost_subset,
    CAST(year || '-01-01' AS DATE) + interval month MONTH AS timestamp,
    marginal_ghg as av_marginal_ghg_ton_co2_per_energy_unit
FROM california.gas_av_marginal_ghg_ton_co2_per_therm
CROSS JOIN regions r
