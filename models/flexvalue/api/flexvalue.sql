MODEL (
    name flexvalue.flexvalue,
    kind FULL,
    grains (project_id),
);

SELECT
coalesce(elec_calculations.project_id, gas_calculations.project_id) AS project_id
, SUM(COALESCE(elec_calculations.electric_benefits, gas_calculations.gas_benefits)) / MAX(COALESCE(elec_calculations.trc_costs, gas_calculations.trc_costs)) as trc_ratio
, SUM(elec_calculations.electric_benefits) / MAX(elec_calculations.trc_costs) as trc_ratio_elec
, SUM(gas_calculations.gas_benefits) / MAX(gas_calculations.trc_costs) as trc_ratio_gas
, SUM(elec_calculations.electric_benefits + gas_calculations.gas_benefits) / MAX(COALESCE(elec_calculations.trc_costs, gas_calculations.trc_costs)) as trc_ratio_2
, SUM(COALESCE(elec_calculations.electric_benefits, gas_calculations.gas_benefits)) / MAX(COALESCE(elec_calculations.pac_costs, gas_calculations.pac_costs)) as pac_ratio
, COALESCE(SUM(elec_calculations.electric_benefits), 0) as electric_benefits
, COALESCE(SUM(gas_calculations.gas_benefits), 0) as gas_benefits
, SUM(COALESCE(elec_calculations.electric_benefits, 0)) + SUM(COALESCE(gas_calculations.gas_benefits, 0)) as total_benefits
, COALESCE(SUM(elec_calculations.annual_net_mwh_savings), 0) as annual_net_mwh_savings
, COALESCE(SUM(elec_calculations.lifecycle_net_mwh_savings), 0) as lifecycle_net_mwh_savings
, COALESCE(SUM(gas_calculations.annual_net_therms_savings), 0) as annual_net_therms_savings
, COALESCE(SUM(gas_calculations.lifecycle_net_therms_savings), 0) as lifecycle_net_therms_savings
, COALESCE(SUM(elec_calculations.lifecycle_elec_ghg_savings), 0) as lifecycle_elec_ghg_savings
, COALESCE(SUM(gas_calculations.lifecycle_gas_ghg_savings), 0) as lifecycle_gas_ghg_savings
, SUM(COALESCE(elec_calculations.lifecycle_elec_ghg_savings, 0)) + SUM(COALESCE(gas_calculations.lifecycle_gas_ghg_savings, 0)) as lifecycle_total_ghg_savings
FROM flexvalue.elec_calculations
FULL OUTER JOIN flexvalue.gas_calculations
	ON elec_calculations.project_id = gas_calculations.project_id AND elec_calculations.datetime = gas_calculations.datetime
GROUP BY 1
