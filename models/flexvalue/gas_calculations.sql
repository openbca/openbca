MODEL (
    name flexvalue.gas_calculations,
    kind FULL,
    grains (project_id, therms_profile, datetime),
);

SELECT pcwdga.project_id
, therms_profile.therms_profile
, MAX(pcwdga.trc_costs) as trc_costs
, MAX(pcwdga.pac_costs) as pac_costs
, SUM(pcwdga.units * pcwdga.ntg * pcwdga.therms_savings * therms_profile.value * pcwdga.discount * pcwdga.total) as gas_benefits
, SUM((pcwdga.units * pcwdga.therms_savings * pcwdga.ntg * therms_profile.value) / CAST(pcwdga.eul AS FLOAT) ) as annual_net_therms_savings
, SUM(pcwdga.units * pcwdga.therms_savings * pcwdga.ntg * therms_profile.value) as lifecycle_net_therms_savings
, SUM(pcwdga.units * pcwdga.therms_savings * pcwdga.ntg * therms_profile.value * pcwdga.marginal_ghg) as lifecycle_gas_ghg_savings
, pcwdga.datetime
FROM flexvalue.project_costs_with_discounted_gas_av pcwdga
JOIN flexvalue.therms_profile therms_profile
    ON pcwdga.therms_profile = therms_profile.therms_profile
        AND therms_profile.utility = pcwdga.utility
        AND therms_profile.month = pcwdga.month
GROUP BY pcwdga.project_id, eul, pcwdga.datetime, therms_profile.therms_profile
