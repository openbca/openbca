MODEL(
    name measure.measure_cost_dollars,
    kind VIEW,
    grain (measure_id),
);
SELECT
    measure_id,
    avoided_cost_subset,
    start_year, start_quarter,
    discount_rate_ratio, estimated_useful_life,
    unit_quantity, net_to_gross_ratio,
    admin_cost_dollars
        + (((1 - net_to_gross_ratio) * incentive_cost_dollars) + (net_to_gross_ratio * measure_cost_dollars))
        / (1 + (discount_rate_ratio / 4.0))
        AS trc_cost_dollars,
    admin_cost_dollars + (incentive_cost_dollars / (1 + (discount_rate_ratio / 4.0))) as pac_cost_dollars,
FROM
    openbca_core.measures
