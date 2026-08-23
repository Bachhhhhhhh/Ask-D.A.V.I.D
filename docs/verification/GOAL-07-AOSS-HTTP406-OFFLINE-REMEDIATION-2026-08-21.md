# Goal 7 AOSS HTTP 406 offline remediation — 2026-08-21

## Status

**OFFLINE REMEDIATION IMPLEMENTED — NO CONNECTED RETRY**

The separately approved private indexer task reached the AOSS data-plane
request path and stopped with exit code `1`. Its sanitized CloudWatch error
was:

```text
RuntimeError: AOSS index creation failed: HTTP 406
```

Connected evidence for that one-shot attempt:

- account/region: `736956442295` / `ap-southeast-1`;
- cluster: `ask-david-development-cluster`;
- task definition: `ask-david-development-goal7-indexer:2`;
- task ARN suffix: `9e430600a2054511a418d408057c0eb2`;
- image digest: `sha256:08ef16bfbd3e4dbd6a940227a6fd7afab14385644eec617d02da7c8f46714669`;
- private ENI/IP: `eni-046225507fcef8431` / `10.42.30.90`;
- dedicated task SG: `sg-0ff2bcb1d5175c931`;
- final ECS result: `STOPPED`, `EssentialContainerExited`, exit `1`.

The failure occurred in `AossClient.ensure_index()` while issuing the
`PUT /<index>` request. The task did not complete index creation, bulk
upsert, vector search, or the final success contract. No retry was performed.

## Minimal source correction

`ensure_index()` now passes `Content-Type: application/json` for the JSON
index-creation request. The request helper already supported an explicit
content type, and the bulk endpoint already uses its required
`application/x-ndjson` value. This is a source-contract correction for the
observed HTTP 406; it does not broaden the index, mapping, identity, or
network scope.

A regression test asserts that the index-creation `PUT` carries exactly the
JSON content type while the existence `HEAD` remains unchanged.

## Scope boundary

This checkpoint changes only runtime source, regression tests, and durable
documentation. It does not:

- build or push an image;
- update the ignored image digest;
- create a Terraform plan or apply Terraform;
- create, delete, or mutate an AOSS collection/index/document;
- run Databricks SQL or a bundle;
- run or retry an ECS task.

The next boundaries are separate approval for offline validation review,
image build/push and digest update, any task-definition plan/apply, and one
new private indexer task attempt.
