MODEL(
    name flexvalue.project_benefits,
    kind FULL,
    grain (project_id),
);
SELECT
    pc.project_id,
    -- TODO we shouldn't have to cast
    electric_benefits::INT AS electric_benefits,
    energy::INT AS energy,
    lifecycle_elec_ghg_savings::INT AS lifecycle_elec_ghg_savings,
    lifecycle_gas_ghg_savings::INT AS lifecycle_gas_ghg_savings,
    gas_benefits::INT AS gas_benefits,
    peb.* EXCLUDE (project_id, electric_benefits, energy, lifecycle_elec_ghg_savings),
    pgb.* EXCLUDE (project_id, gas_benefits, lifecycle_gas_ghg_savings),
    -- TODO we shouldn't have to cast,
    -- lifecycle_total_ghg_savings
    lifecycle_elec_ghg_savings + lifecycle_gas_ghg_savings as lifecycle_total_ghg_savings,
    electric_benefits + gas_benefits as total_benefits,
    (electric_benefits + gas_benefits) / trc_costs as trc_ratio,
    (electric_benefits + gas_benefits) / pac_costs as pac_ratio,
FROM flexvalue.project_costs pc
LEFT JOIN flexvalue.project_elec_benefits peb
    ON pc.project_id = peb.project_id
LEFT JOIN flexvalue.project_gas_benefits pgb
    ON pc.project_id = pgb.project_id
