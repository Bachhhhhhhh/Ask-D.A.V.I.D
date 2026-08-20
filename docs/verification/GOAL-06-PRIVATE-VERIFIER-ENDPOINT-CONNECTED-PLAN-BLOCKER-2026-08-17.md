# Goal 6 Phase 6-6 private verifier endpoint remediation — connected plan blocker

Date: 2026-08-17
Environment: development only (`736956442295`, `ap-southeast-1`)
Status: **BLOCKED BEFORE A REVIEWABLE PLAN — NO APPLY, NO ECS RETRY**

## Approved attempt and read-only preflight

The project owner approved AWS/Databricks read-only revalidation and creation
of one saved development Terraform plan for the exact private
verifier-to-interface-endpoint TCP/443 rule.

Preflight confirmed:

- AWS account `736956442295`, principal
  `arn:aws:iam::736956442295:user/bach_dev_admin_david`;
- AWS region `ap-southeast-1`;
- active workspace profile `ask-david-development` for
  `bachvxuan@gmail.com`;
- current source contains exactly the reviewed SG-reference-only endpoint rule;
- the worktree remains intentionally dirty with uncommitted Goal 4–6 work;
  no unrelated file was changed by this attempt.

Terraform initialized the existing S3 backend using a temporary local data
directory and ran `plan -lock=false`. State refresh remained read-only; no
apply, destroy, ECS task, ECR, SQL, or Databricks mutation occurred.

## Failure

Terraform's account-level Databricks provider refresh failed because profile
`ask-david-account` cannot obtain an OAuth access token: its refresh token is
invalid. The workspace profile is not a substitute, because the existing
development root manages account-level identity resources.

The attempted artifact
`infrastructure/environments/development/goal-06-private-verifier-endpoint-remediation-20260817.tfplan`
has SHA-256
`9a5c230eeb0ec64b8d8c84b8956a552d48e3f6000619b3d8caceeae337d79722`, but it is
not a reviewable or applyable saved plan. Inspection with the matching local
provider cache shows only 149 no-op resource entries and no
`goal6_verifier_to_aws_endpoints` create. It is retained locally as failed-plan
diagnostic evidence only and must not be applied.

## Required next action

The project owner must perform interactive OAuth login for the existing
account-level profile, without sharing any token or secret:

```text
databricks auth login --profile ask-david-account
```

After that authentication succeeds, a fresh read-only identity check and a new
saved connected development plan require renewed explicit approval. The new
plan must show exactly one create of
`aws_vpc_security_group_ingress_rule.goal6_verifier_to_aws_endpoints[0]`, with
zero update, replacement, destroy, IAM/KMS, task-definition, ECS, Databricks,
public-exposure, or production changes. Applying it and any one-time ECS retry
remain separate approval boundaries.

## Resolution

The project owner reauthenticated the existing account-level profile. A new
saved plan subsequently completed and supersedes this failed attempt; see
[`GOAL-06-PRIVATE-VERIFIER-ENDPOINT-CONNECTED-PLAN-2026-08-17.md`](GOAL-06-PRIVATE-VERIFIER-ENDPOINT-CONNECTED-PLAN-2026-08-17.md).
