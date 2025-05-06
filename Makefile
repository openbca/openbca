docker-build:
	docker build -t open-bca -f Dockerfile .

docker-run: docker-build
	docker run -it --rm -v $(shell pwd)/input:/app/input -v $(shell pwd)/output:/app/output -v $(shell pwd)/models:/app/models -v $(shell pwd)/test_data:/app/test_data -v $(shell pwd)/logs:/app/logs open-bca

install:
	pip install -r requirements.txt

run:
	sqlmesh plan --auto-apply
	echo "Writing output to output/flexvalue_legacy_one_query.csv"
	duckdb duckdb.db -c "COPY (SELECT * FROM flexvalue.flexvalue_legacy_one_query) TO 'output/flexvalue_legacy_one_query.csv' WITH (FORMAT CSV, HEADER TRUE);"

validate-output:
	sqlmesh table_diff flexvalue__dev.flexvalue_legacy_one_query:duckdb.flexvalue_test.rdc_output_table -o project_id --show-sample

duckdb:
	duckdb duckdb.db

unit-test:
	PYTHONPATH=. pytest tests/
	sqlmesh test

clean:
	rm -f duckdb.db
	rm -rf logs
	rm -rf .cache
	rm -rf output/*
