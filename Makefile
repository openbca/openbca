install:
	pip install -r requirements.txt

init:
	sqlmesh init duckdb
	sqlmesh plan
	sqlmesh plan dev

run:
	sqlmesh --gateway duckdb plan dev --auto-apply --include-unmodified
	#sqlmesh --gateway duckdb plan --auto-apply

run_bq:
	sqlmesh --gateway bigquery plan dev --auto-apply

login:
	sqlmesh login --gateway duckdb

clean:
	sqlmesh invalidate dev
