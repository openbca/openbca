MODEL(
    name core_layer0_base.cost_treatment_factors,
    kind VIEW,
);

SELECT
    impact_category::VARCHAR AS impact_category,
    cost_treatment::VARCHAR AS cost_treatment,
    factor::VARCHAR AS factor
FROM (
    VALUES
        ('ADMIN', 'UCT', '1'),
        ('ADMIN', 'TRC', '1'),
        ('ADMIN', 'CA TRC', '1'),
        ('ADMIN', 'PCT', '0'),
        ('ADMIN', 'RIM', '1'),

        ('UTILITY INCENTIVE', 'UCT', '1'),
        ('UTILITY INCENTIVE', 'TRC', '0'),
        ('UTILITY INCENTIVE', 'CA TRC', '1-net_to_gross_ratio'),
        ('UTILITY INCENTIVE', 'PCT', '-1'),
        ('UTILITY INCENTIVE', 'RIM', '1'),

        ('MEASURE COST', 'UCT', '0'),
        ('MEASURE COST', 'TRC', 'net_to_gross_ratio'),
        ('MEASURE COST', 'CA TRC', 'net_to_gross_ratio'),
        ('MEASURE COST', 'PCT', '1'),
        ('MEASURE COST', 'RIM', '0'),

        ('TAX INCENTIVE', 'UCT', '0'),
        ('TAX INCENTIVE', 'TRC', '-1'),
        ('TAX INCENTIVE', 'CA TRC', '1-net_to_gross_ratio'),
        ('TAX INCENTIVE', 'PCT', '-1'),
        ('TAX INCENTIVE', 'RIM', '0'),

) AS t(impact_category, cost_treatment, factor)