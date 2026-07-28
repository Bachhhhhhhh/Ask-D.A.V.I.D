# Generic HTTP mock foundation

The Compose `mockserver` service is a domain-neutral HTTP mock server for
future client configuration, loopback networking, health-check, timeout, and
typed-response tests. `fixtures/` contains a versioned generic response schema
and safe success/error examples.

The pinned MockServer image does not provide a supported container health
check. The Goal 2 foundation therefore verifies that the service starts, but
does not claim protocol readiness. Future contract and integration tests must
own their explicit readiness criteria alongside their endpoint mappings.

It intentionally defines no endpoint mappings and does not emulate AWS,
Databricks, Doris, OpenSearch Serverless, a controlled tool service, an agent,
or data access. Goal 8 owns typed controlled-service contracts and any related
stub behavior.
