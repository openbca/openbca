MODEL (
    name flexvalue.elec_calculations,
    kind FULL,
    grains (project_id, load_shape, datetime),
);

SELECT
pcwdea.project_id
, elec_load_shape.load_shape
, pcwdea.datetime
, SUM(pcwdea.units * pcwdea.ntg * pcwdea.mwh_savings * elec_load_shape.value * pcwdea.discount * pcwdea.total) AS electric_benefits
, SUM(pcwdea.units * pcwdea.ntg * pcwdea.mwh_savings * elec_load_shape.value) / CAST(pcwdea.eul AS FLOAT) as annual_net_mwh_savings
, MAX(pcwdea.trc_costs) AS trc_costs
, MAX(pcwdea.pac_costs) AS pac_costs
, SUM(pcwdea.units * pcwdea.ntg * pcwdea.mwh_savings * elec_load_shape.value) as lifecycle_net_mwh_savings
, SUM(pcwdea.units * pcwdea.ntg * pcwdea.mwh_savings * elec_load_shape.value * pcwdea.marginal_ghg) as lifecycle_elec_ghg_savings
FROM flexvalue.project_costs_with_discounted_elec_av pcwdea
JOIN flexvalue.elec_load_shape elec_load_shape
    ON elec_load_shape.load_shape = pcwdea.load_shape
        AND elec_load_shape.utility = pcwdea.utility
        AND elec_load_shape.hour_of_year = pcwdea.hour_of_year
GROUP BY pcwdea.project_id, eul, pcwdea.datetime, elec_load_shape.load_shape
