MODEL(
    name flexvalue.project_value_stream_benefits,
    kind FULL,
    grain (project_id),
);
WITH pivoted_vsb(
    SELECT
        project_id,
        SUM(IF(value_stream = 'total' AND commodity = 'ELECTRICITY', value)) AS electric_benefits,
        SUM(IF(value_stream = 'total' AND commodity = 'GAS', value)) AS gas_benefits,
        SUM(IF(value_stream = 'marginal_ghg' AND commodity = 'ELECTRICITY', value)) AS lifecycle_elec_ghg_savings,
        SUM(IF(value_stream = 'marginal_ghg' AND commodity = 'GAS', value)) AS lifecycle_gas_ghg_savings,
    FROM flexvalue.project_commodity_value_stream_benefits
    GROUP BY ALL
)
SELECT
    pc.project_id,
    vsb.* EXCLUDE (project_id),
    (COALESCE(lifecycle_elec_ghg_savings, 0) + COALESCE(lifecycle_gas_ghg_savings, 0)) as lifecycle_total_ghg_savings,
    (COALESCE(electric_benefits, 0) + COALESCE(gas_benefits, 0)) as total_benefits,
    (COALESCE(electric_benefits, 0) + COALESCE(gas_benefits, 0)) / trc_costs as trc_ratio,
    (COALESCE(electric_benefits, 0) + COALESCE(gas_benefits, 0)) / pac_costs as pac_ratio,
FROM flexvalue.project_costs pc
LEFT JOIN pivoted_vsb vsb
    ON pc.project_id = vsb.project_id
