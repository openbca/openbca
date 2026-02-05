
def generate_measure_filters_query():
    measure_filters_query = f"""
        SELECT  
        id
        , program_name 
        , measure_name
        , measure_id
        , avoided_cost_subset
        , cast(start_year as string) as start_year
        , label_1
        , label_2
        , label_3
        , label_4
        , label_5
        FROM 
        openbca.core_layer0_base.measures
    """
    return measure_filters_query


def generate_jst_query(where_sql):
    jst_query = f"""
        SELECT 
        SUM(total_costs) AS total_costs
        , SUM(total_benefits) AS total_benefits
        , SUM(total_net_benefits) AS total_net_benefits
        , -SUM(total_benefits) / SUM(total_costs) AS jst_ratio
        FROM 
        openbca.core_layer3_finalization.results_summary_by_id m
        {where_sql} 
        HAVING (
        SUM(total_costs) IS NOT NULL 
        OR SUM(total_benefits) IS NOT NULL
        )
    """
    return jst_query


def generate_waterfall_query(where_sql, waterfall_column):
    waterfall_query = f"""
        SELECT 
        {waterfall_column} 
        , sum(final_dollar_value) as final_dollar_value
        FROM 
        openbca.core_layer3_finalization.final_value_calculations_ts fvc 
        FULL OUTER JOIN openbca.core_layer0_base.measures m ON 
        fvc.id = m.id
        {where_sql} 
        GROUP BY 
        {waterfall_column} 
        HAVING 
        SUM(final_dollar_value) != 0
    """
    return waterfall_query


def generate_benefit_cost_scatter_query(where_sql, catalog_by_filter):
    benefit_cost_scatter_query = f"""
        SELECT 
        id
        , {catalog_by_filter}
        , ifnull(total_benefits, 0) as total_benefits
        , -ifnull(total_costs, 0) as total_costs
        FROM 
        openbca.core_layer3_finalization.results_summary_by_id m
        {where_sql} 
        """
    return benefit_cost_scatter_query


def generate_benefits_commodity_options_query(where_sql):   
    benefits_commodity_options_query = f"""
        SELECT 
        DISTINCT commodity 
        FROM 
        openbca.core_layer3_finalization.final_value_calculations_ts fvc
        FULL OUTER JOIN openbca.core_layer0_base.measures m ON 
        fvc.id = m.id
        {where_sql} 
        AND commodity NOT IN ('ADMIN', 'UTILITY INCENTIVE', 'MEASURE COST', 'TAX INCENTIVE')
        ORDER BY 
        commodity
        """
    return benefits_commodity_options_query
    

def generate_populated_temporal_cols_query(where_sql, commodity_filter, col):
    populated_temporal_cols_query = f"""
        SELECT 
        commodity 
        FROM 
        openbca.core_layer3_finalization.final_value_calculations_ts 
        WHERE 
        commodity = '{commodity_filter}'
        AND {col} IS NOT NULL
        LIMIT 1
    """
    return populated_temporal_cols_query


def generate_temporal_aggregation_benefits_query(where_sql, commodity_filter, temporal_aggregation_filter, unit, group_by_value_stream: bool = False):
    temporal_aggregation_benefits_sql = f"""
    WITH benefits AS (
        SELECT 
        {temporal_aggregation_filter}
        {', value_stream' if group_by_value_stream else ''}
        , sum(final_dollar_value) AS final_dollar_value
        FROM 
        openbca.core_layer3_finalization.final_value_calculations_ts fvc 
        FULL OUTER JOIN openbca.core_layer0_base.measures m ON 
        fvc.id = m.id
        {where_sql} 
        AND commodity = '{commodity_filter}'
        GROUP BY 
        {temporal_aggregation_filter}
        {', value_stream' if group_by_value_stream else ''}
    )
    """

    temporal_aggregation_savings_sql = f"""
        , savings AS (
        SELECT 
        {temporal_aggregation_filter}
        , sum(net_energy_savings) AS net_lifecycle_energy_savings
        FROM 
        openbca.core_layer3_finalization.final_value_calculations_ts fsc
        JOIN openbca.core_layer0_base.measures m ON 
        fsc.id = m.id
        {where_sql} 
        AND commodity = '{commodity_filter}'
        AND value_stream IN ('Energy Generation (E)', 'Fuel Supply and O&M (NG)', 'Propane Supply', 'Oil Supply', 'Diesel Supply')
        GROUP BY 
        {temporal_aggregation_filter}
            
    )
    """

    if unit == '':
        temporal_aggregation_query = f"""
            {temporal_aggregation_benefits_sql}
            select
            *
            from benefits
        """
        
    else:
        temporal_aggregation_query = f"""
            {temporal_aggregation_benefits_sql}
            {temporal_aggregation_savings_sql}
            SELECT 
            b.*
            , s.net_lifecycle_energy_savings
            FROM 
            benefits b 
            JOIN savings s ON 
            b.{temporal_aggregation_filter} = s.{temporal_aggregation_filter}
        """

    return temporal_aggregation_query


def generate_null_aggregation_benefits_query(where_sql, commodity_filter, temporal_aggregation_filter):
    null_aggregation_benefits_query = f"""
        SELECT 
        sum(final_dollar_value) AS final_dollar_value
        FROM 
        openbca.core_layer3_finalization.final_value_calculations_ts fvc 
        JOIN openbca.core_layer0_base.measures m ON 
        fvc.id = m.id
        {where_sql} 
        AND commodity = '{commodity_filter}'
        AND {temporal_aggregation_filter} IS NULL
        HAVING SUM(final_dollar_value) IS NOT NULL
    """
    return null_aggregation_benefits_query


def generate_value_stream_benefits_query(where_sql, commodity_filter):
    value_stream_benefits_query = f"""
        SELECT 
        value_stream 
        , sum(final_dollar_value) AS final_dollar_value
        FROM 
        openbca.core_layer3_finalization.final_value_calculations_ts fvc 
        FULL OUTER JOIN openbca.core_layer0_base.measures m ON 
        fvc.id = m.id
        {where_sql} 
        AND commodity = '{commodity_filter}'
        GROUP BY 
        value_stream
        ORDER BY 
        value_stream
    """
    return value_stream_benefits_query


def generate_multiple_options_probe_query(where_sql, column_names:list[str]):
    
    subqueries = []
    for column_name in column_names:
            
        column_filter_coalesce = column_name
        if column_name == 'program_name':
            column_filter_coalesce = "coalesce(m.program_name, fvc.id)"
    
        subqueries.append(
            f"""
            SELECT 
            '{column_name}' AS field 
            , count(distinct {column_filter_coalesce}) AS distinct_values
            FROM 
            openbca.core_layer3_finalization.final_value_calculations_ts fvc 
            FULL OUTER JOIN openbca.core_layer0_base.measures m ON 
            fvc.id = m.id
            {where_sql} 
            HAVING SUM(final_dollar_value) IS NOT NULL
            """
        )

    multiple_options_probe_query = ' UNION ALL '.join(subqueries)
    
    return multiple_options_probe_query


def generate_costs_commodity_query(where_sql):
    costs_commodity_query = f"""
        SELECT 
        commodity
        , -sum(final_dollar_value) AS final_dollar_value
        FROM 
        openbca.core_layer3_finalization.final_value_calculations_ts fvc 
        FULL OUTER JOIN openbca.core_layer0_base.measures m ON 
        fvc.id = m.id
        {where_sql} 
        AND commodity IN ('ADMIN', 'UTILITY INCENTIVE', 'MEASURE COST', 'TAX INCENTIVE')
        GROUP BY 
        commodity
        HAVING ABS(final_dollar_value) > 0
    """
    return costs_commodity_query


def generate_costs_value_stream_query(where_sql):
    costs_value_stream_query = f"""
        SELECT 
        value_stream AS 'Value Stream'
        , -sum(final_dollar_value) AS final_dollar_value
        FROM 
        openbca.core_layer3_finalization.final_value_calculations_ts fvc 
        FULL OUTER JOIN openbca.core_layer0_base.measures m ON 
        fvc.id = m.id
        {where_sql} 
        AND commodity IN ('ADMIN', 'UTILITY INCENTIVE', 'MEASURE COST', 'TAX INCENTIVE')
        GROUP BY 
        value_stream            
        HAVING ABS(final_dollar_value) > 0
        ORDER BY 
        value_stream
    """
    return costs_value_stream_query


def generate_categorical_summary_query(where_sql, category_filter, grouping_filter = None):
    
    category_filter_coalesce = category_filter
    if category_filter == 'program_name':
        category_filter_coalesce = "coalesce(m.program_name, fvc.id)"
    
    grouping_filter_coalesce = grouping_filter
    if grouping_filter == 'program_name':
        grouping_filter_coalesce = "coalesce(m.program_name, fvc.id)"

    categorical_summary_query = f"""
        SELECT 
        {category_filter_coalesce} AS {category_filter}
        {f", {grouping_filter_coalesce} AS {grouping_filter}" if grouping_filter is not None else ''}
        , sum(final_dollar_value) AS final_dollar_value
        FROM 
        openbca.core_layer3_finalization.final_value_calculations_ts fvc 
        FULL OUTER JOIN openbca.core_layer0_base.measures m ON 
        fvc.id = m.id
        {where_sql} 
        GROUP BY 
        {category_filter_coalesce}
        {f", {grouping_filter_coalesce}" if grouping_filter is not None else ''}
        HAVING SUM(final_dollar_value) IS NOT NULL
    """
    return categorical_summary_query


def generate_summary_results_query():
    summary_results_query = f"""
        SELECT 
        *
        FROM 
        openbca.core_layer3_finalization.results_summary_by_id
    """
    return summary_results_query

