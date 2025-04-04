MODEL (
    name flexvalue.elec_calculations,
    kind FULL,
    grains (project_id, load_shape, datetime),
);

WITH calculated_values AS (
    SELECT
        pcwdea.project_id,
        elec_load_shape.load_shape,
        pcwdea.datetime,
        pcwdea.units * pcwdea.ntg * pcwdea.mwh_savings * elec_load_shape.value AS base_value,
        pcwdea.discount * pcwdea.total AS discounted_total,
        pcwdea.marginal_ghg AS marginal_ghg,
        pcwdea.eul AS eul,
        pcwdea.trc_costs AS trc_costs,
        pcwdea.pac_costs AS pac_costs
    FROM flexvalue.project_costs_with_discounted_elec_av pcwdea
    JOIN flexvalue.elec_load_shape elec_load_shape
        ON elec_load_shape.load_shape = pcwdea.load_shape
        AND elec_load_shape.utility = pcwdea.utility
        AND elec_load_shape.hour_of_year = pcwdea.hour_of_year
)
SELECT
    project_id,
    load_shape,
    datetime,
    SUM(base_value * discounted_total) AS electric_benefits,
    SUM(base_value) / CAST(eul AS FLOAT) AS annual_net_mwh_savings,
    MAX(trc_costs) AS trc_costs,
    MAX(pac_costs) AS pac_costs,
    SUM(base_value) AS lifecycle_net_mwh_savings,
    SUM(base_value * marginal_ghg) AS lifecycle_elec_ghg_savings
FROM calculated_values
GROUP BY project_id, eul, datetime, load_shape
