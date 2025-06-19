MODEL(
    name openbca_reference.avoided_marginal_ghg_ts,
    kind VIEW,
    grain (commodity, avoided_cost_version, avoided_cost_subset, timestamp),
);

SELECT
    commodity,
    avoided_cost_version,
    avoided_cost_subset,
    timestamp,
    av_marginal_ghg_ton_co2_per_energy_unit
FROM california.avoided_marginal_ghg_ts


-- UNION ALL TODO add more marginal ghg

