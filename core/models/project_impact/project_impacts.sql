MODEL(
    name openbca_core.project_impacts,
    kind VIEW,
    grain (project_id),
);
WITH
pivoted_economic_impacts(
    SELECT
        project_id,
        SUM(CASE WHEN commodity = 'ELECTRICITY' THEN net_energy_savings END) AS net_electric_energy_savings,
        SUM(CASE WHEN commodity = 'GAS' THEN net_energy_savings END) AS net_gas_energy_savings,
        SUM(IF(commodity = 'ELECTRICITY', impact_dollars)) AS electric_benefits,
        SUM(IF(commodity = 'GAS', impact_dollars)) AS gas_benefits,
    FROM openbca_core.project_commodity_economic_impacts
    GROUP BY ALL
),
pivoted_environmental_impacts(
    SELECT
        project_id,
        SUM(IF(commodity = 'ELECTRICITY', impact_tons_co2e)) AS electric_ghg_savings,
        SUM(IF(commodity = 'GAS', impact_tons_co2e)) AS gas_ghg_savings,
    FROM openbca_core.project_commodity_environmental_impacts
    GROUP BY ALL
)
SELECT
    pc.project_id,
    eco.* EXCLUDE (project_id),
    env.* EXCLUDE (project_id),
    (COALESCE(electric_ghg_savings, 0) + COALESCE(gas_ghg_savings, 0)) as total_ghg_benefits,
    (COALESCE(electric_benefits, 0) + COALESCE(gas_benefits, 0)) as total_benefits,
    (COALESCE(electric_benefits, 0) + COALESCE(gas_benefits, 0)) / trc_costs as trc_ratio,
    (COALESCE(electric_benefits, 0) + COALESCE(gas_benefits, 0)) / pac_costs as pac_ratio,
    electric_benefits / net_electric_energy_savings AS total_benefits_per_mwh,
    gas_benefits / net_gas_energy_savings AS total_benefits_per_therm,
FROM project.project_costs pc
LEFT JOIN pivoted_economic_impacts eco
    ON pc.project_id = eco.project_id
LEFT JOIN pivoted_environmental_impacts env
    ON pc.project_id = env.project_id
