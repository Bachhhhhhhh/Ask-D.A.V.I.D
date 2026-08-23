# Goal 7 private ECS-to-Databricks network-path analysis — 2026-08-21

## Status

**OFFLINE DESIGN COMPLETE — NO IMPLEMENTATION OR CONNECTED OPERATION**

The approved revision-2 indexer task reached `RUNNING` and failed closed while
requesting a Databricks OAuth token. The failure occurred before the governed
outbox read, embedding call, OpenSearch index creation, or document upsert.
This checkpoint only analyzes the repository-defined network path and records
the smallest safe remediation choices. No Terraform source, AWS resource,
Databricks resource, ECS task, ECR image, secret, or runtime code was changed.

## Evidence-backed current path

| Layer | Repository evidence | Conclusion |
| --- | --- | --- |
| Task placement | `goal7-indexer` uses existing application subnets, `awsvpc`, and no public IP | Private placement is preserved |
| Workload SG egress | `workload_aws_endpoints` permits TCP/443 only to the existing AWS interface-endpoint SG; `workload_s3` permits TCP/443 only to the S3 gateway prefix list | Secrets Manager/ECR/Logs and S3 paths are intentionally narrow |
| Private subnet routing | `network` associates application subnets with the private route table, whose default route is the existing NAT gateway | A technically usable NAT path exists at the route-table layer |
| Databricks endpoint | The task uses the approved `https://*.cloud.databricks.com` workspace host and the OAuth token endpoint is outside the AWS interface-endpoint SG and S3 prefix-list destinations | No approved workload-SG path to the Databricks host is declared |
| Runtime behavior | `DatabricksSqlClient._token()` fails closed on the OAuth connection timeout | The blocker is network reachability before UC or AOSS work, not an authorization or index contract failure |

The NAT route alone does not authorize a packet: the workload security group
still has no matching TCP/443 egress rule. Conversely, adding a
`0.0.0.0/0` rule would make the private workload an unrestricted HTTPS client
through NAT and would violate the current Goal 7 least-privilege boundary.
Static workspace IP rules are not a durable contract for a managed SaaS host.

## Remediation options

### Preferred: approved Databricks PrivateLink/private-connectivity path

First perform read-only verification that the existing Databricks workspace is
configured for AWS PrivateLink/private connectivity and that a supported
workspace/relay endpoint service is available in `ap-southeast-1`. If it is
already present, the minimal declarative extension should be limited to the
existing VPC and workload boundary:

1. reuse the approved Databricks private endpoint/service configuration;
2. attach or reuse a dedicated endpoint security group with TCP/443 ingress
   only from the Goal 7 workload SG;
3. ensure private DNS maps the approved workspace OAuth host to that private
   endpoint; and
4. add only the corresponding Terraform-managed SG-scoped workload egress.

The exact Databricks account/network resource identifiers must be discovered
read-only before any source change. No new metastore, catalog, public route,
static credential, or broad CIDR rule is part of this option.

### Not approved without a new security decision: generic NAT HTTPS egress

The existing NAT gateway could carry the traffic, but AWS security groups
cannot express a stable hostname-only egress destination. A direct
`0.0.0.0/0:443` workload rule would broaden the task beyond the reviewed
private endpoint/S3 paths. It must not be added as an implementation shortcut.
Using a new egress proxy, Network Firewall, or domain-filtering appliance would
be a new persistent architecture component and is outside this remediation
checkpoint.

## Required next checkpoint

Before source implementation, obtain a separately approved connected
read-only revalidation of:

- the Databricks workspace's private-connectivity/PrivateLink capability;
- any existing endpoint-service or relay identifiers and private DNS state;
- the VPC route table, NAT state, workload SG egress, endpoint SG ingress, and
  DNS resolution path; and
- the exact account, workspace, region, and development-only scope.

If an approved private path exists, the next approval is for offline
Terraform/source/tests/docs implementation of only that path. If it does not
exist, stop for an explicit architecture/security decision rather than adding
public or unrestricted NAT egress. Only after that implementation is reviewed
may a saved connected Terraform plan and a separate one-shot indexer task be
requested.

## Offline checks

| Check | Result |
| --- | --- |
| Goal 7 static validator | PASS — existing source remains valid |
| Focused Goal 7 regression tests | PASS — existing suite |
| Terraform formatting | PASS — no Terraform source changed in this checkpoint |
| Connected Terraform plan/apply/destroy | NOT RUN |
| AWS or Databricks mutation | NOT RUN |
| ECS retry or AOSS operation | NOT RUN |
