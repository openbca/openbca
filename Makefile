install:
	pip install -r requirements.txt

run:
	sqlmesh plan --auto-apply
	echo "Writing output to output/flexvalue_legacy_one_query.csv"
	@duckdb output/duckdb.db -c "COPY (SELECT * FROM flexvalue.flexvalue_legacy_one_query) TO 'output/flexvalue_legacy_one_query.csv' WITH (FORMAT CSV, HEADER TRUE);"

duckdb:
	duckdb output/duckdb.db

test:
	PYTHONPATH=. pytest tests/
	sqlmesh test

clean:
	rm -f duckdb.db && rm -rf logs && rm -rf .cache && rm -rf output/*

DUCKDB_ARCH=aarch64
docker-build:
	docker build --build-arg ARCH=${DUCKDB_ARCH} -t open-bca -f Dockerfile .

DOCKER_RUN_ARGS=-v $(shell pwd)/input:/app/input -v $(shell pwd)/output:/app/output -v $(shell pwd)/models:/app/models -v $(shell pwd)/test_data:/app/test_data -v $(shell pwd)/logs:/app/logs -v $(shell pwd)/tests:/app/tests open-bca

docker-run: docker-build
	docker run --rm ${DOCKER_RUN_ARGS}

docker-shell: docker-build
	docker run -it --rm ${DOCKER_RUN_ARGS} bash

docker-test: docker-build
	docker run --rm ${DOCKER_RUN_ARGS} bash -c "make test"
