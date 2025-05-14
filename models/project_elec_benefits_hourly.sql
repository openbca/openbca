MODEL(
    name flexvalue.project_elec_benefits_hourly,
    kind FULL,
    grain (project_id, year, hour_of_year)
);
WITH
project_elec_hourly AS (
    SELECT
        pc.project_id,
        eac.*,
        1.0 / POW(
            1.0 + (pc.discount_rate / 4.0),
            ((eac.year - pc.start_year) * 4) + eac.quarter - pc.start_quarter
        ) AS discount,
        els.value as elec_load_shape_value
    FROM flexvalue.project_costs pc
    JOIN flexvalue_reference.elec_av_costs eac
        ON eac.utility = pc.utility
            AND eac.region = pc.region
            AND (
                (eac.year > pc.start_year OR (eac.year = pc.start_year AND eac.quarter >= pc.start_quarter))
                AND
                (eac.year < pc.start_year + pc.eul OR (eac.year = pc.start_year + pc.eul AND eac.quarter < pc.start_quarter))
            )
    JOIN flexvalue_reference.elec_load_shape_unpivoted els
        ON pc.load_shape = els.load_shape
            AND pc.utility = els.utility
            AND eac.hour_of_year = els.hour_of_year
)
SELECT
    peh.project_id,
    peh.year, peh.hour_of_year,
    peh.discount,
    pc.gross_adjusted_savings * peh.elec_load_shape_value * peh.discount * peh.total AS electric_benefits,
    pc.gross_adjusted_savings * peh.elec_load_shape_value * peh.discount * peh.losses AS losses,
    pc.gross_adjusted_savings * peh.elec_load_shape_value * peh.marginal_ghg AS marginal_ghg,
    pc.gross_adjusted_savings * peh.elec_load_shape_value * peh.discount * peh.ghg_rebalancing AS ghg_rebalancing,
    pc.gross_adjusted_savings * peh.elec_load_shape_value * peh.discount * peh.distribution AS distribution,
    pc.gross_adjusted_savings * peh.elec_load_shape_value * peh.discount * peh.methane_leakage AS methane_leakage,
    pc.gross_adjusted_savings * peh.elec_load_shape_value * peh.discount * peh.ancillary_services AS ancillary_services,
    pc.gross_adjusted_savings * peh.elec_load_shape_value * peh.discount * peh.energy AS energy,
    pc.gross_adjusted_savings * peh.elec_load_shape_value * peh.discount * peh.capacity AS capacity,
    pc.gross_adjusted_savings * peh.elec_load_shape_value * peh.discount * peh.cap_and_trade AS cap_and_trade,
    pc.gross_adjusted_savings * peh.elec_load_shape_value * peh.discount * peh.transmission AS transmission,
    pc.gross_adjusted_savings * peh.elec_load_shape_value * peh.discount * peh.ghg_adder_rebalancing AS ghg_adder_rebalancing,
    pc.gross_adjusted_savings * peh.elec_load_shape_value * peh.discount * peh.ghg_adder AS ghg_adder,
    pc.gross_adjusted_savings * peh.elec_load_shape_value * peh.discount * emc.marginal_cost as marginal_cost,
    pc.gross_adjusted_savings * peh.elec_load_shape_value AS net_mwh_savings,
    pc.gross_adjusted_savings * peh.elec_load_shape_value AS lifecycle_net_mwh_savings,
FROM project_elec_hourly peh
LEFT JOIN flexvalue.project_costs pc
    ON peh.project_id = pc.project_id
LEFT JOIN flexvalue.elec_marginal_cost emc
    ON peh.utility = emc.utility AND peh.region = emc.region
