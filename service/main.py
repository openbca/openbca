from typing import Dict, List

import uvicorn
from fastapi import FastAPI
import duckdb
from pydantic import BaseModel

app = FastAPI()

DATABASE_FILE = "tests/test_real_data_calculations_aggregated/duckdb.db"

@app.get("/calculate-electricity-benefit")
async def calculate_electricity_benefit(
        utility: str = "PGE",
        region: str = "CZ12",
        start_datetime: str = "2021-10-01 00:00:00",
        end_datetime: str = "2033-10-01 00:00:00",
        units: float = 1.0,
        ntg: float = 0.95,
        mwh_savings: float = 12.434473,
        discount: float = 0.9,
        load_shape_name: str = "NONRES_HVAC_SPLIT_PACKAGE_AC",
):
    with duckdb.connect(DATABASE_FILE) as conn:
        result = conn.execute(
            f"""
                SELECT
                    SUM(electricity_benefit) AS electricity_benefit
                FROM (
                    SELECT
                        datetime,
                        $units * $ntg * $mwh_savings * {load_shape_name} * $discount * total AS electricity_benefit
                    FROM flexvalue.elec_ts ets
                    WHERE utility = $utility AND region = $region AND datetime BETWEEN $start_datetime::timestamp AND $end_datetime::timestamp
                ) AS subquery
                """,
            {"units": units, "ntg": ntg, "mwh_savings": mwh_savings, "discount": discount, "utility": utility, "region": region, "start_datetime": start_datetime, "end_datetime": end_datetime},
        ).fetchall()
    return {"electricity_benefit": round(result[0][0], 2)}


class TimeseriesInput(BaseModel):
    utility: str
    region: str
    start_datetime: str
    end_datetime: str
    project_id: str
    units: float
    ntg: float
    mwh_savings: float
    load_shape_name: str = "NONRES_HVAC_SPLIT_PACKAGE_AC"
    discount: Dict[int, Dict[int, float]]


@app.post("/calculate-electricity-benefit-with-timeseries")
async def calculate_electricity_benefit_with_timeseries(input_data: TimeseriesInput):

    with duckdb.connect(DATABASE_FILE) as conn:
        conn.execute("""
            CREATE TEMPORARY TABLE temp_project_discount_hourly (year INTEGER, month INTEGER, discount FLOAT)
        """)

        conn.executemany("""
        INSERT INTO temp_project_discount_hourly VALUES (?, ?, ?)
        """, [(year, month, value) for year, year_records in input_data.discount.items() for month, value in year_records.items()])

        result = conn.execute(
            """
                SELECT
                    SUM(electricity_benefit) AS electricity_benefit
                FROM (
                    SELECT
                        datetime,
                        $units * $ntg * $mwh_savings * {load_shape_name} * COALESCE(p.discount, 0.9) * ets.total AS electricity_benefit
                    FROM flexvalue.elec_ts ets
                    LEFT JOIN temp_project_discount_hourly p ON p.year = ets.year AND p.month = ets.month
                    WHERE utility = $utility AND region = $region AND datetime BETWEEN $start_datetime::timestamp AND $end_datetime::timestamp
                ) AS subquery
                """.format(load_shape_name=input_data.load_shape_name),
            {
                "units": input_data.units,
                "ntg": input_data.ntg,
                "mwh_savings": input_data.mwh_savings,
                "utility": input_data.utility,
                "region": input_data.region,
                "start_datetime": input_data.start_datetime,
                "end_datetime": input_data.end_datetime,
            },
        ).fetchall()

        return {"electricity_benefit": round(result[0][0], 2)}


class ValueStreamInput(BaseModel):
    utility: str
    region: str
    start_datetime: str
    end_datetime: str
    project_id: str
    units: float
    ntg: float
    mwh_savings: float
    discount: float
    load_shape_name: str = "NONRES_HVAC_SPLIT_PACKAGE_AC"
    value_streams: List[str] = ["energy", "ghg_rebalancing", "total"]
    custom_value_streams: Dict[int, Dict[int, Dict[str, float]]]

@app.post("/calculate-electricity-benefit-with-valuestreams")
async def calculate_electricity_benefit_with_valuestreams(input_data: ValueStreamInput):

    with duckdb.connect(DATABASE_FILE) as conn:
        conn.execute("""
            CREATE TEMPORARY TABLE temp_vs_hourly (year INTEGER, hour_of_year INTEGER, value_stream VARCHAR, value FLOAT)
        """)

        conn.executemany("""
        INSERT INTO temp_vs_hourly VALUES (?, ?, ?, ?)
        """, [(year, hour_of_year, key, value) for year, year_records in input_data.custom_value_streams.items() for hour_of_year, value_stream in year_records.items() for key, value in value_stream.items()])

        result = conn.execute(
            f"""
                SELECT
                    value_stream,
                    SUM($units * $ntg * $mwh_savings * {input_data.load_shape_name} * $discount * value) AS benefit
                FROM (
                    (
                        SELECT
                            year, hour_of_year, value_stream, value, {input_data.load_shape_name}
                        FROM flexvalue__dev.elec_ts_unpivot ets
                        WHERE utility = $utility AND region = $region AND datetime BETWEEN $start_datetime::timestamp AND $end_datetime::timestamp
                        AND value_stream IN ({", ".join(["'" + vs + "'" for vs in input_data.value_streams])})
                    ) UNION ALL
                    (
                        SELECT
                            tvs.year, tvs.hour_of_year, value_stream, value, {input_data.load_shape_name}
                        FROM temp_vs_hourly tvs
                        JOIN flexvalue_input.elec_load_shape
                            ON  elec_load_shape.utility = $utility
                            AND tvs.hour_of_year = elec_load_shape.hour_of_year                                          
                    )
                ) AS subquery
                GROUP BY value_stream
                """,
            { "units": input_data.units, "ntg": input_data.ntg, "mwh_savings": input_data.mwh_savings, "discount": input_data.discount, "utility": input_data.utility, "region": input_data.region, "start_datetime": input_data.start_datetime, "end_datetime": input_data.end_datetime,},
        ).fetchall()

        return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
