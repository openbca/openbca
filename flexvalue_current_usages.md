# FlexValue current usages  
## [FlexValue inputs](https://docs.google.com/document/d/1tc1LpWSVGyQ2g8oNQN_9YbhL59OBobHwKrmKTyIufvg/edit?tab=t.0)
- Project/user inputs: 
    - utility, region
    - start_year, start_quarter, eul, 
    - discount_rate, admin cost…
    - elec_load_shape, therms_profile
- Electric avoided costs hourly
  - Utility, region
  - year , hour of year
  - Total
  - Marginal_ghg
  - avoided cost data can be segmented into specific value streams. 
- Gas avoided costs
  - Utility, region
  - Year, month
  - Total
  - avoided cost data can be segmented into specific value streams.
- Hourly electric load shapes
  - Utility, region
  - Hour_of_year
  - Columns corresponding to specific load shapes
- Gas monthly therms profiles
  - Utility, region
  - Year, month
  - Columns corresponding to specific profiles

## FlexValue current use cases:
### Project Value Estimator
System integration: Python/BigQuery

Inputs:
 - Fixed:
   - electric avoided costs hourly
   - gas avoided costs
   - hourly electric load shapes
   - gas monthly therms profiles
 - Dynamic:
   - Project/user inputs (built from ProjectHub schema)
Outputs:
   1. Project level metrics
      - Aggregation-columns:[]
      - Table: < uuid >_output
   2. Timeseries
      - Aggregation-columns: hour_of_year,year
      - Tables: < uuid >_ts_electric, < uuid >_ts_gas

### [Looker dashboard](https://lookerstudio.google.com/u/0/reporting/e480483d-7403-41cf-a25f-4235ed40a489/page/YB8jD)
System integration: SQL/BigQuery
Inputs: same as Project Value Estimator

### Metering Plus
System integration: Python/BigQuery

Inputs:
 - Fixed:
   - electric avoided costs hourly
   - gas avoided costs
   - hourly electric load shapes
   - gas monthly therms profiles
 - Dynamic:
   - Project/user inputs (built from ProjectHub schema)
   - electric avoided costs hourly (built from calculated savings tables)
   - gas avoided costs (built from calculated savings tables)

Output:
1. default 
   - Output tables:
     - Flexvalue_elec_direct_outputs 
       - dpsm_id, hour_of_year, annual_net_mwh_savings, electric_benefits
     - Flexvalue_gas_direct_outputs 
       - dpsm_id, month, annual_net_therms_savings, gas_benefits 
       - aggregation_columns dpsm_id,portfolio_name,savings_type,value_curve_name,hour_of_year,month
2. full_eul 
   - Output tables:
     - flexvalue_elec_direct_outputs
       - aggregation_columns dpsm_id,portfolio_name,savings_type,value_curve_name, year,quarter,month,hour_of_day,hour_of_year
     - flexvalue_gas_direct_outputs


References:
https://docs.recurve.energy/engineering/architecture/flexvalue/metering-plus/
https://docs.recurve.energy/metering/valuation/
https://docs.recurve.energy/engineering/architecture/flexvalue/metering-plus/
https://github.com/recurve-inc/metering-plus/blob/main/metering_plus/core/valuation/orchestrate_flexvalue.py


### - ICF
? <TODO>
