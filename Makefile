DB?=output/openbca.db
export DB

DUCKDB_ARCH?=aarch64
docker-build:
	docker build --build-arg DUCKDB_ARCH=${DUCKDB_ARCH} -t openbca -f Dockerfile .

DOCKER_RUN_ARGS=-e DB=${DB} -v $(shell pwd)/reference:/app/reference -v $(shell pwd)/core:/app/core -v $(shell pwd)/demo:/app/demo -v $(shell pwd)/nspm:/app/nspm -v $(shell pwd)/output:/app/output -v $(shell pwd)/app:/app/app -v $(shell pwd)/logs:/app/logs openbca

install:
	pip install -r requirements.txt

test-core:
	sqlmesh -p core test

run-reference:
	sqlmesh -p reference plan --auto-apply

test-reference:
	PYTHONPATH=. pytest reference/tests
	sqlmesh -p reference test

run-demo:
	sqlmesh -p reference -p demo -p core plan --auto-apply
	@echo "Evaluating and writing output in output/measure_impacts.csv..."
	@time duckdb ${DB} -c "COPY (SELECT * FROM openbca_core.measure_impacts) TO 'output/measure_impacts.csv' WITH (FORMAT CSV, HEADER TRUE);"
	$(MAKE) test-demo

docker-run-demo: docker-build
	docker run --rm ${DOCKER_RUN_ARGS} bash -c "make run-demo"

test-demo:
	@echo "Comparing openbca_core.measure_impacts against demo/data/ref_measure_impacts.csv..."
	@duckdb ${DB} -c "CREATE OR REPLACE TABLE openbca_core.ref_measure_impacts AS SELECT * FROM read_csv_auto('demo/data/ref_measure_impacts.csv');"
	@sqlmesh -p core table_diff openbca_core.measure_impacts:openbca_core.ref_measure_impacts -o measure_id --show-sample

prepare-app:
	sqlmesh -p reference -p app -p core plan --auto-apply

run-app: prepare-app
	streamlit run app/src/main.py

docker-run-app: docker-build
	docker run -it -p 8501:8501 ${DOCKER_RUN_ARGS} bash -c "make run-app"

test-app: prepare-app
	PYTHONPATH=app/src python3 app/tests/test_app.py

docker-test-app: docker-build
	docker run --rm ${DOCKER_RUN_ARGS} bash -c "make test-app"

test: test-reference test-core test-demo test-app

docker-test: docker-build
	docker run --rm ${DOCKER_RUN_ARGS} bash -c "make test"

clean:
	@rm -rf logs && rm -rf output/*
	@find . -type d -name ".cache" -exec rm -rf {} +

docker-shell: docker-build
	docker run -it --rm ${DOCKER_RUN_ARGS} bash

generate-flow-diagram:
	sqlmesh -p . dag output/dag.html

sqlmesh-ui-core:
	sqlmesh -p core ui

run-all:
	$(MAKE) run-demo
	$(MAKE) test-app

docker-run-all: docker-build
	$(MAKE) docker-run-demo
	$(MAKE) docker-test-app
