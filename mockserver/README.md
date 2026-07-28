# Generic HTTP mock foundation

The Compose `mockserver` service is a domain-neutral HTTP mock server for
future client configuration, loopback networking, health-check, timeout, and
typed-response tests. `fixtures/` contains a versioned generic response schema
and safe success/error examples.

The Compose health check uses MockServer's Java health-check class. The pinned
image is distroless, so health checks must not depend on an in-container shell
or `curl`.

It intentionally defines no endpoint mappings and does not emulate AWS,
Databricks, Doris, OpenSearch Serverless, a controlled tool service, an agent,
or data access. Goal 8 owns typed controlled-service contracts and any related
stub behavior.
