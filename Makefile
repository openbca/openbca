install:
	pip install -r requirements.txt

init: install
	sqlmesh init duckdb
	sqlmesh plan
	sqlmesh plan dev

init-test-db:
	duckdb -init tests/test_real_data_calculations_aggregated/init.sql -no-stdin tests/test_real_data_calculations_aggregated/duckdb.db

run: init-test-db
	sqlmesh --gateway test_real_data_calculations_aggregated plan --auto-apply

validate-output:
	sqlmesh table_diff flexvalue__dev.flexvalue_legacy_one_query:duckdb.flexvalue_test.rdc_output_table -o project_id --show-sample

duckdb:
	duckdb tests/test_real_data_calculations_aggregated/duckdb.db

unit-test:
	PYTHONPATH=. pytest tests/
	sqlmesh test

run_bq:
	sqlmesh --gateway bigquery plan dev --select-model +flexvalue.flexvalue_legacy_one_query

run-service:
	uvicorn service.main:app --reload

clean:
	rm -f tests/test_real_data_calculations_aggregated/duckdb.db
	rm -rf logs
	rm -rf .cache
