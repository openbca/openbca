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
        ('ADMIN', 'USI + Non-USI', '1'),
        ('ADMIN', 'USI', '1'),
        ('ADMIN', 'CA TRC', '1'),
        ('ADMIN', 'PCT', '0'),
        ('ADMIN', 'RIM', '1'),

        ('UTILITY INCENTIVE', 'USI + Non-USI', '1'),
        ('UTILITY INCENTIVE', 'USI', '0'),
        ('UTILITY INCENTIVE', 'CA TRC', '1-net_to_gross_ratio'),
        ('UTILITY INCENTIVE', 'PCT', '-1'),
        ('UTILITY INCENTIVE', 'RIM', '1'),

        ('MEASURE COST', 'USI + Non-USI', '0'),
        ('MEASURE COST', 'USI', 'net_to_gross_ratio'),
        ('MEASURE COST', 'CA TRC', 'net_to_gross_ratio'),
        ('MEASURE COST', 'PCT', '1'),
        ('MEASURE COST', 'RIM', '0'),

        ('TAX INCENTIVE', 'USI + Non-USI', '0'),
        ('TAX INCENTIVE', 'USI', '-1'),
        ('TAX INCENTIVE', 'CA TRC', '1-net_to_gross_ratio'),
        ('TAX INCENTIVE', 'PCT', '-1'),
        ('TAX INCENTIVE', 'RIM', '0'),

) AS t(impact_category, cost_treatment, factor)