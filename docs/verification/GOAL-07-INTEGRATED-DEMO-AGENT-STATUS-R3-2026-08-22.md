# Goal 7 integrated demo retry R3 — agent-status failure — 2026-08-22

## Approved boundary

After the Doris FE/BE instances were started and status checks became healthy,
exactly one private integrated-demo task was run from revision 2. Only the
task's ECS/ENI/CloudWatch state was inspected afterward. No retry, Terraform,
ECR, Databricks, SQL, AOSS, or other AWS mutation was performed.

## Evidence

| Field | Result |
| --- | --- |
| Task ARN suffix | `cfbd08d76e264187b1ce2a36918ff236` |
| Task definition | `ask-david-development-goal7-integrated-demo:2` |
| Doris FE/BE preflight | `running`, EC2 status-ok |
| Task private IP | `10.42.22.218` |
| Container exit code | `1` |
| CloudWatch result | `connected Goal 7 integrated demo did not complete all agents` |

The previous Doris timeout did not recur; the log contains no Doris connection
traceback. The graph reached its final aggregate check, but
`connected_demo.py` discards each agent's `status` and `error` before raising
the generic message. Therefore the failing agent (RAG or Analytics) cannot be
identified from this run.

## Current checkpoint

Goal 7 remains UNVERIFIED. The next safe step is an offline source/test/docs
remediation that emits sanitized per-agent status and error diagnostics. No
additional task may run until that remediation is reviewed.
