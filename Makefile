install:
	pip install -r requirements.txt

init:
	sqlmesh init duckdb
	sqlmesh plan
	sqlmesh plan dev

run:
	sqlmesh plan dev --auto-apply #--include-unmodified
	#sqlmesh --gateway duckdb plan --auto-apply

run-bq:
	sqlmesh --gateway bigquery plan dev --auto-apply

test:
	PYTHONPATH=. pytest tests/
	sqlmesh test

integration-test: init-test
	sqlmesh --gateway test_real_data_calculations_aggregated plan dev --auto-apply --include-unmodified
	sqlmesh table_diff flexvalue__dev.flexvalue:duckdb.flexvalue.rdc_output_table -o project_id --show-sample

init-test:
	rm -f tests/test_real_data_calculations_aggregated/duckdb.db
	duckdb -init tests/test_real_data_calculations_aggregated/init.sql -no-stdin tests/test_real_data_calculations_aggregated/duckdb.db

refresh-ref-file:
	duckdb tests/test_real_data_calculations_aggregated/duckdb.db "COPY flexvalue__dev.flexvalue TO 'tests/test_real_data_calculations_aggregated/rdc_output_table.csv' (HEADER, DELIMITER ',');"

shell-test:
	duckdb tests/test_real_data_calculations_aggregated/duckdb.db

run_bq:
	sqlmesh --gateway bigquery plan dev --auto-apply

login:
	sqlmesh login --gateway duckdb

clean:
	sqlmesh invalidate dev
