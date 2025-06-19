MODEL(
    name openbca.project_commodity_impact_ts,
    kind VIEW,
    grain (project_id, commodity, year, hour_of_year),
);
SELECT
    project_id, load_shape,
    commodity, avoided_cost, avoided_cost_subset,
    year, quarter,
    month, hour_of_year, hour_of_day,
    discount, net_energy_savings_ts,
    value as av_cost_value,
    CASE
        WHEN avoided_cost = 'marginal_ghg' THEN net_energy_savings_ts * av_cost_value
        ELSE net_energy_savings_ts * discount * av_cost_value
    END AS impact_value
 FROM (

    -- joining value-stream with project_commodity_load_shape_ts
    -- for all possible time granularity: Constant, Annual, Monthly cross-year, Monthly within year, ...

    -- Constant
    SELECT
        pcls_ts.*,
        av_ts.avoided_cost, av_ts.value
    FROM openbca.project_commodity_load_shape_ts pcls_ts
    JOIN openbca_input.avoided_costs_ts av_ts
        ON pcls_ts.commodity = av_ts.commodity
        AND (pcls_ts.avoided_cost_subset = av_ts.avoided_cost_subset OR pcls_ts.avoided_cost_subset IS NULL)
    WHERE
        av_ts.year IS NULL AND av_ts.month IS NULL AND av_ts.hour_of_day IS NULL AND av_ts.hour_of_year IS NULL


    UNION ALL

    -- Annual
    SELECT
        pcls_ts.*,
        av_ts.avoided_cost, av_ts.value
    FROM openbca.project_commodity_load_shape_ts pcls_ts
    JOIN openbca_input.avoided_costs_ts av_ts
        ON pcls_ts.commodity = av_ts.commodity
        AND (pcls_ts.avoided_cost_subset = av_ts.avoided_cost_subset OR pcls_ts.avoided_cost_subset IS NULL)
        AND pcls_ts.year = av_ts.year
    WHERE av_ts.year IS NOT NULL AND av_ts.month IS NULL AND av_ts.hour_of_day IS NULL AND av_ts.hour_of_year IS NULL

    UNION ALL

    -- Monthly cross-year
    SELECT
        pcls_ts.*,
        av_ts.avoided_cost, av_ts.value
    FROM openbca.project_commodity_load_shape_ts pcls_ts
    JOIN openbca_input.avoided_costs_ts av_ts
        ON pcls_ts.commodity = av_ts.commodity
        AND (pcls_ts.avoided_cost_subset = av_ts.avoided_cost_subset OR pcls_ts.avoided_cost_subset IS NULL)
        AND pcls_ts.month = av_ts.month
    WHERE av_ts.year IS NULL AND av_ts.month IS NOT NULL AND av_ts.hour_of_day IS NULL AND av_ts.hour_of_year IS NULL

    UNION ALL

    -- Monthly with year
    SELECT
        pcls_ts.*,
        av_ts.avoided_cost, av_ts.value
    FROM openbca.project_commodity_load_shape_ts pcls_ts
    JOIN openbca_input.avoided_costs_ts av_ts
        ON pcls_ts.commodity = av_ts.commodity
        AND (pcls_ts.avoided_cost_subset = av_ts.avoided_cost_subset OR pcls_ts.avoided_cost_subset IS NULL)
        AND pcls_ts.year = av_ts.year AND pcls_ts.month = av_ts.month
    WHERE av_ts.year IS NOT NULL AND av_ts.month IS NOT NULL AND av_ts.hour_of_day IS NULL AND av_ts.hour_of_year IS NULL

    UNION ALL

    -- Hourly by hour_of_year cross-year
    SELECT
        pcls_ts.*,
        av_ts.avoided_cost, av_ts.value
    FROM openbca.project_commodity_load_shape_ts pcls_ts
    JOIN openbca_input.avoided_costs_ts av_ts
        ON pcls_ts.commodity = av_ts.commodity
        AND (pcls_ts.avoided_cost_subset = av_ts.avoided_cost_subset OR pcls_ts.avoided_cost_subset IS NULL)
        AND pcls_ts.hour_of_year = av_ts.hour_of_year
    WHERE av_ts.year IS NULL AND av_ts.hour_of_year IS NOT NULL

    UNION ALL

    -- Hourly by hour_of_year with year
    SELECT
        pcls_ts.*,
        av_ts.avoided_cost, av_ts.value
    FROM openbca.project_commodity_load_shape_ts pcls_ts
    JOIN openbca_input.avoided_costs_ts av_ts
        ON pcls_ts.commodity = av_ts.commodity
        AND (pcls_ts.avoided_cost_subset = av_ts.avoided_cost_subset OR pcls_ts.avoided_cost_subset IS NULL)
        AND pcls_ts.year = av_ts.year AND pcls_ts.hour_of_year = av_ts.hour_of_year
    WHERE av_ts.year IS NOT NULL AND av_ts.hour_of_year IS NOT NULL

    UNION ALL

    -- Hourly by hour_of_day cross year/month
    SELECT
        pcls_ts.*,
        av_ts.avoided_cost, av_ts.value
    FROM openbca.project_commodity_load_shape_ts pcls_ts
    JOIN openbca_input.avoided_costs_ts av_ts
        ON pcls_ts.commodity = av_ts.commodity
        AND (pcls_ts.avoided_cost_subset = av_ts.avoided_cost_subset OR pcls_ts.avoided_cost_subset IS NULL)
        AND pcls_ts.hour_of_day = av_ts.hour_of_day
    WHERE av_ts.year IS NULL AND av_ts.month IS NULL AND av_ts.hour_of_day IS NOT NULL AND av_ts.hour_of_year IS NULL

    UNION ALL

    -- Hourly by hour_of_day with year/month
    SELECT
        pcls_ts.*,
        av_ts.avoided_cost, av_ts.value
    FROM openbca.project_commodity_load_shape_ts pcls_ts
    JOIN openbca_input.avoided_costs_ts av_ts
        ON pcls_ts.commodity = av_ts.commodity
        AND (pcls_ts.avoided_cost_subset = av_ts.avoided_cost_subset OR pcls_ts.avoided_cost_subset IS NULL)
        AND pcls_ts.year = av_ts.year AND pcls_ts.month = av_ts.month
        AND pcls_ts.hour_of_day = av_ts.hour_of_day
    WHERE av_ts.year IS NOT NULL AND av_ts.month IS NOT NULL AND av_ts.hour_of_day IS NOT NULL AND av_ts.hour_of_year IS NULL

    UNION ALL

    -- Hourly by hour_of_day with year
    SELECT
        pcls_ts.*,
        av_ts.avoided_cost, av_ts.value
    FROM openbca.project_commodity_load_shape_ts pcls_ts
    JOIN openbca_input.avoided_costs_ts av_ts
        ON pcls_ts.commodity = av_ts.commodity
        AND (pcls_ts.avoided_cost_subset = av_ts.avoided_cost_subset OR pcls_ts.avoided_cost_subset IS NULL)
        AND pcls_ts.year = av_ts.year
        AND pcls_ts.hour_of_day = av_ts.hour_of_day
    WHERE av_ts.year IS NOT NULL AND av_ts.month IS NULL AND av_ts.hour_of_day IS NOT NULL AND av_ts.hour_of_year IS NULL

)
