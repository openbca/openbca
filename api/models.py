from typing import Any, Optional
from pydantic import BaseModel


# Full column order matching openbca_input_measures.MEASURES_SCHEMA_COLUMN_ORDER
MEASURES_COLUMNS = [
    "id",
    "program_name",
    "measure_id",
    "project_id",
    "measure_name",
    "avoided_cost_subset",
    "start_year",
    "start_quarter",
    "measure_specific_discount_rate",
    "measure_unit",
    "unit_quantity",
    "estimated_useful_life",
    "net_to_gross_ratio",
    "admin_cost_upfront_dollar",
    "admin_cost_annual_dollar_per_year",
    "utility_incentive_upfront_dollar",
    "utility_incentive_annual_dollar_per_year",
    "incremental_cost_upfront_dollar",
    "incremental_cost_annual_dollar_per_year",
    "host_customer_transaction_cost_dollar",
    "host_customer_interconnection_cost_dollar",
    "host_customer_tax_incentive_upfront_dollar",
    "electric_savings_load_shape",
    "annual_electric_savings_kwh",
    "coincident_peak_savings_kw",
    "natural_gas_savings_load_shape",
    "annual_natural_gas_savings_mmbtu",
    "annual_propane_savings_mmbtu",
    "annual_oil_savings_mmbtu",
    "annual_diesel_savings_mmbtu",
    "host_customer_non_energy_impacts_dollar",
    "host_customer_non_energy_impacts_low_income_dollar",
    "change_in_host_customer_risk",
    "change_in_host_customer_reliability",
    "change_in_host_customer_resilience",
    "change_in_societal_resilience",
    "custom_1_value_stream_name",
    "custom_1_value_stream_commodity",
    "custom_1_annual_savings",
    "custom_2_value_stream_name",
    "custom_2_value_stream_commodity",
    "custom_2_annual_savings",
    "custom_3_value_stream_name",
    "custom_3_value_stream_commodity",
    "custom_3_annual_savings",
    "custom_4_value_stream_name",
    "custom_4_value_stream_commodity",
    "custom_4_annual_savings",
    "custom_5_value_stream_name",
    "custom_5_value_stream_commodity",
    "custom_5_annual_savings",
    "label_1",
    "label_2",
    "label_3",
    "label_4",
    "label_5",
]


class MeasureInput(BaseModel):
    id: str
    program_name: Optional[str] = None
    measure_id: Optional[str] = None
    project_id: Optional[str] = None
    measure_name: Optional[str] = None
    avoided_cost_subset: Optional[str] = None
    start_year: Optional[int] = None
    start_quarter: Optional[int] = None
    measure_specific_discount_rate: Optional[float] = None
    measure_unit: Optional[str] = None
    unit_quantity: Optional[float] = None
    estimated_useful_life: Optional[int] = None
    net_to_gross_ratio: Optional[float] = None
    admin_cost_upfront_dollar: Optional[float] = None
    admin_cost_annual_dollar_per_year: Optional[float] = None
    utility_incentive_upfront_dollar: Optional[float] = None
    utility_incentive_annual_dollar_per_year: Optional[float] = None
    incremental_cost_upfront_dollar: Optional[float] = None
    incremental_cost_annual_dollar_per_year: Optional[float] = None
    host_customer_transaction_cost_dollar: Optional[float] = None
    host_customer_interconnection_cost_dollar: Optional[float] = None
    host_customer_tax_incentive_upfront_dollar: Optional[float] = None
    electric_savings_load_shape: Optional[str] = None
    annual_electric_savings_kwh: Optional[float] = None
    coincident_peak_savings_kw: Optional[float] = None
    natural_gas_savings_load_shape: Optional[str] = None
    annual_natural_gas_savings_mmbtu: Optional[float] = None
    annual_propane_savings_mmbtu: Optional[float] = None
    annual_oil_savings_mmbtu: Optional[float] = None
    annual_diesel_savings_mmbtu: Optional[float] = None
    host_customer_non_energy_impacts_dollar: Optional[float] = None
    host_customer_non_energy_impacts_low_income_dollar: Optional[float] = None
    change_in_host_customer_risk: Optional[float] = None
    change_in_host_customer_reliability: Optional[float] = None
    change_in_host_customer_resilience: Optional[float] = None
    change_in_societal_resilience: Optional[float] = None
    custom_1_value_stream_name: Optional[str] = None
    custom_1_value_stream_commodity: Optional[str] = None
    custom_1_annual_savings: Optional[float] = None
    custom_2_value_stream_name: Optional[str] = None
    custom_2_value_stream_commodity: Optional[str] = None
    custom_2_annual_savings: Optional[float] = None
    custom_3_value_stream_name: Optional[str] = None
    custom_3_value_stream_commodity: Optional[str] = None
    custom_3_annual_savings: Optional[float] = None
    custom_4_value_stream_name: Optional[str] = None
    custom_4_value_stream_commodity: Optional[str] = None
    custom_4_annual_savings: Optional[float] = None
    custom_5_value_stream_name: Optional[str] = None
    custom_5_value_stream_commodity: Optional[str] = None
    custom_5_annual_savings: Optional[float] = None
    label_1: Optional[str] = None
    label_2: Optional[str] = None
    label_3: Optional[str] = None
    label_4: Optional[str] = None
    label_5: Optional[str] = None


class CalculateRequest(BaseModel):
    measures: list[MeasureInput]


class CalculateResponse(BaseModel):
    jst_ratio: dict[str, Any]
    results_summary: list[dict[str, Any]]
    final_value_calculations: list[dict[str, Any]]
    net_energy_savings: list[dict[str, Any]]
