# FlexValue + SQLMesh POC

Pros:
- Complex SQL queries can be broken down into smaller, reusable and testable components.
- SQLMesh leverages https://antonz.org/sql-polyglot/ to ensure the portability of SQL across different engines.
- SQLMesh can leverage DuckDB to run SQL queries locally

Cons:
 - SQLMesh requires to store its state in a database.

TODO for the POC:
 - how to work with different inputs/outputs and different granularity (without parametrizing the columns)
 - can we precalculate for PVE and looker?

TODO to make it production ready:
 - load test with large datasets
 - wire it to real tables depending on the use case (Project Value Estimator, Metering Plus)
 - more unit tests + port some existing integrations
 - load reference data as "seed" files
 - refactor/clean up?
