MODEL(
    name core_layer0_base.cost_treatment_factors,
    kind VIEW,
);

SELECT
    commodity::VARCHAR AS commodity,
    cost_treatment::VARCHAR AS cost_treatment,
    factor::VARCHAR AS factor
FROM (
    VALUES
        ('ADMIN', 'UCT', '1'),
        ('ADMIN', 'TRC', '1'),
        ('ADMIN', 'CA TRC', '1'),
        ('ADMIN', 'PCT', '1'),
        ('ADMIN', 'RIM', '1'),

        ('INCENTIVE', 'UCT', '1'),
        ('INCENTIVE', 'TRC', '0'),
        ('INCENTIVE', 'CA TRC', '1-ntg'),
        ('INCENTIVE', 'PCT', '-1'),
        ('INCENTIVE', 'RIM', '1'),

        ('MEASURE', 'UCT', '0'),
        ('MEASURE', 'TRC', 'ntg'),
        ('MEASURE', 'CA TRC', 'ntg'),
        ('MEASURE', 'PCT', '1'),
        ('MEASURE', 'RIM', '0'),

        ('TAX INCENTIVE', 'UCT', '0'),
        ('TAX INCENTIVE', 'TRC', '0'),
        ('TAX INCENTIVE', 'CA TRC', '1-ntg'),
        ('TAX INCENTIVE', 'PCT', '-1'),
        ('TAX INCENTIVE', 'RIM', '0'),

) AS t(commodity, cost_treatment, factor)