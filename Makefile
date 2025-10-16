DB?=output/openbca.db
export DB

docker-build:
	docker build -t openbca -f Dockerfile .

DOCKER_RUN_ARGS=-e DB=${DB} -v $(shell pwd)/reference:/app/reference -v $(shell pwd)/core:/app/core -v $(shell pwd)/demo:/app/demo -v $(shell pwd)/nspm:/app/nspm -v $(shell pwd)/output:/app/output -v $(shell pwd)/app:/app/app -v $(shell pwd)/logs:/app/logs openbca

install:
	uv sync

test-core:
	uv run sqlmesh -p core test

run-reference:
	uv run sqlmesh -p reference plan --auto-apply

test-reference:
	PYTHONPATH=. pytest reference/tests
	uv run sqlmesh -p reference test

prepare-app:
	uv run sqlmesh -p reference -p app -p core plan --auto-apply

run-app: prepare-app
	uv run streamlit run app/src/main.py

test-app: prepare-app
	PYTHONPATH=app/src python3 app/tests/test_app.py

docker-test-app: docker-build
	docker run --rm ${DOCKER_RUN_ARGS} bash -c "make test-app"

docker-run-app: docker-build
	docker run -it -p 8501:8501 ${DOCKER_RUN_ARGS} bash -c "make run-app"

run-nspm:
	sqlmesh -p reference -p nspm -p core plan --auto-apply
	@echo "Evaluating and writing output in output/nspm_measure_impacts.csv..."
	@time uv run python -c "import os,duckdb; con=duckdb.connect(os.environ['DB']); con.execute(\"COPY (SELECT * FROM openbca_core.measure_impacts) TO 'output/nspm_measure_impacts.csv' (HEADER, DELIMITER ',');\"); con.close()"

docker-run-nspm: docker-build
	docker run --rm ${DOCKER_RUN_ARGS} bash -c "make run-nspm"

test-nspm:
	PYTHONPATH=. pytest nspm/tests

test: test-reference test-core test-demo test-app

docker-test: docker-build
	docker run --rm ${DOCKER_RUN_ARGS} bash -c "make test"

clean:
	@rm -rf logs && rm -rf output/*
	@find . -type d -name ".cache" -exec rm -rf {} +

docker-shell: docker-build
	docker run -it --rm ${DOCKER_RUN_ARGS} bash

generate-flow-diagram:
	uv run sqlmesh -p . dag output/dag.html

sqlmesh-ui-core:
	uv run sqlmesh -p core ui
