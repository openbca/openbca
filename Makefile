install:
	pip install -r requirements.txt

init:
	sqlmesh init duckdb
	sqlmesh plan
	sqlmesh plan dev

run:
	sqlmesh plan dev --auto-apply #--include-unmodified
	#sqlmesh --gateway duckdb plan --auto-apply

test:
	sqlmesh test

integration-test: init-test
	sqlmesh --gateway test_real_data_calculations_aggregated plan dev --auto-apply --include-unmodified
	#sqlmesh table_diff sqlmesh_example.incremental_model:sqlmesh_example__dev.incremental_model -o id -o event_date --show-sample

init-test:
	rm -f tests/test_real_data_calculations_aggregated/duckdb.db
	duckdb -init tests/test_real_data_calculations_aggregated/init.sql -no-stdin tests/test_real_data_calculations_aggregated/duckdb.db

shell-test:
	duckdb tests/test_real_data_calculations_aggregated/duckdb.db

run_bq:
	sqlmesh --gateway bigquery plan dev --auto-apply

login:
	sqlmesh login --gateway duckdb

clean:
	sqlmesh invalidate dev
