# Contributing

Read `AGENTS.md` and all mandatory architecture documents before changing the
platform. Keep one roadmap goal isolated, do not modify accepted ADR decisions
without a new ADR, and do not commit secrets or cloud credentials.

Run `make check` or `./scripts/dev.ps1 check` before requesting review. Use
`make local-up` only for the documented local development dependencies; it is
not a deployment command.
