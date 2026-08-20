#!/usr/bin/env bash
set -euo pipefail

fail_closed() {
  printf 'Goal 6 admin-refresh stopped: %s\n' "$1" >&2
  exit 1
}

expected_account_id=""
region=""
name_prefix=""
cluster=""
admin_security_group_id=""
task_definition=""
expected_revision=""
expected_image=""
expected_fe_host=""
expected_be_host=""
expected_workspace_host=""
confirm_goal6_admin_refresh="false"
application_subnet_ids=()

while (($# > 0)); do
  case "$1" in
    --expected-account-id) expected_account_id="${2:-}"; shift 2 ;;
    --region) region="${2:-}"; shift 2 ;;
    --name-prefix) name_prefix="${2:-}"; shift 2 ;;
    --cluster) cluster="${2:-}"; shift 2 ;;
    --application-subnet-id) application_subnet_ids+=("${2:-}"); shift 2 ;;
    --admin-security-group-id) admin_security_group_id="${2:-}"; shift 2 ;;
    --task-definition) task_definition="${2:-}"; shift 2 ;;
    --expected-revision) expected_revision="${2:-}"; shift 2 ;;
    --expected-image) expected_image="${2:-}"; shift 2 ;;
    --expected-fe-host) expected_fe_host="${2:-}"; shift 2 ;;
    --expected-be-host) expected_be_host="${2:-}"; shift 2 ;;
    --expected-workspace-host) expected_workspace_host="${2:-}"; shift 2 ;;
    --confirm-goal6-admin-refresh) confirm_goal6_admin_refresh="true"; shift ;;
    *) fail_closed "unknown or incomplete argument: $1" ;;
  esac
done

[[ "$confirm_goal6_admin_refresh" == "true" ]] || fail_closed "the explicit confirmation switch is required"
[[ "$expected_account_id" =~ ^[0-9]{12}$ ]] || fail_closed "expected account ID must contain 12 digits"
[[ "$region" == "ap-southeast-1" ]] || fail_closed "Goal 6 is approved only in ap-southeast-1"
[[ "$name_prefix" =~ ^[a-z0-9-]+$ ]] || fail_closed "name prefix is invalid"
[[ "$cluster" =~ ^[A-Za-z0-9_:/.-]+$ ]] || fail_closed "cluster is invalid"
[[ ${#application_subnet_ids[@]} -eq 2 ]] || fail_closed "exactly two private application subnets are required"
for subnet_id in "${application_subnet_ids[@]}"; do
  [[ "$subnet_id" =~ ^subnet-[0-9a-f]+$ ]] || fail_closed "application subnet ID is invalid"
done
[[ "$admin_security_group_id" =~ ^sg-[0-9a-f]+$ ]] || fail_closed "admin security-group ID is invalid"
[[ "$expected_revision" =~ ^[1-9][0-9]*$ ]] || fail_closed "expected revision is invalid"
[[ "$expected_image" =~ ^.+@sha256:[0-9a-f]{64}$ ]] || fail_closed "expected image must be digest-pinned"
[[ "$expected_fe_host" =~ ^10\.42\.[0-9]{1,3}\.[0-9]{1,3}$ ]] || fail_closed "FE host is not an approved private Goal 6 address"
[[ "$expected_be_host" =~ ^10\.42\.[0-9]{1,3}\.[0-9]{1,3}$ ]] || fail_closed "BE host is not an approved private Goal 6 address"
[[ "$expected_fe_host" != "$expected_be_host" ]] || fail_closed "FE and BE hosts must be distinct"
[[ "$expected_workspace_host" =~ ^https://[A-Za-z0-9][A-Za-z0-9.-]*\.cloud\.databricks\.com$ ]] || fail_closed "workspace host is not an approved Databricks HTTPS origin"

command -v aws >/dev/null 2>&1 || fail_closed "AWS CLI is unavailable"
command -v jq >/dev/null 2>&1 || fail_closed "jq is unavailable"

account="$(aws sts get-caller-identity --query Account --output text)" || fail_closed "AWS identity could not be inspected"
[[ "$account" == "$expected_account_id" ]] || fail_closed "AWS account mismatch; no task was launched"

definition_json="$(aws ecs describe-task-definition \
  --region "$region" \
  --task-definition "$task_definition" \
  --query taskDefinition \
  --output json)" || fail_closed "the approved task definition could not be inspected"

jq -e \
  --arg family "$name_prefix-doris-admin-refresh" \
  --argjson revision "$expected_revision" \
  --arg image "$expected_image" \
  --arg fe_host "$expected_fe_host" \
  --arg be_host "$expected_be_host" \
  --arg workspace_host "$expected_workspace_host" \
  --arg region "$region" \
  --arg account "$expected_account_id" \
  --arg name_prefix "$name_prefix" '
    .status == "ACTIVE" and
    .family == $family and
    .revision == $revision and
    .networkMode == "awsvpc" and
    (.requiresCompatibilities | index("FARGATE") != null) and
    .cpu == "512" and
    .memory == "1024" and
    .executionRoleArn == ("arn:aws:iam::" + $account + ":role/" + $name_prefix + "-ecs-execution") and
    .taskRoleArn == ("arn:aws:iam::" + $account + ":role/" + $name_prefix + "-doris-admin-task") and
    (.containerDefinitions | length) == 1 and
    .containerDefinitions[0].name == "doris-admin" and
    .containerDefinitions[0].image == $image and
    .containerDefinitions[0].command == ["/app/doris-admin-refresh"] and
    ((.containerDefinitions[0].entryPoint // []) | length) == 0 and
    ([.containerDefinitions[0].environment[] | select(.name == "DORIS_FE_HOST") | .value] == [$fe_host]) and
    ([.containerDefinitions[0].environment[] | select(.name == "DORIS_BE_HOST") | .value] == [$be_host]) and
    ([.containerDefinitions[0].environment[] | select(.name == "DATABRICKS_WORKSPACE_HOST") | .value] == [$workspace_host]) and
    ([.containerDefinitions[0].environment[].name] | sort) == (["DATABRICKS_WORKSPACE_HOST","DORIS_BE_HOST","DORIS_FE_HOST"] | sort) and
    ([.containerDefinitions[0].secrets[].name] | sort) == (["DATABRICKS_OAUTH_SECRET","DORIS_ADMIN_SECRET","DORIS_QUERY_SECRET"] | sort) and
    (all(.containerDefinitions[0].secrets[];
      .valueFrom | startswith("arn:aws:secretsmanager:" + $region + ":" + $account + ":secret:"))) and
    .containerDefinitions[0].logConfiguration.logDriver == "awslogs" and
    .containerDefinitions[0].logConfiguration.options["awslogs-group"] == ("/" + $name_prefix + "/doris") and
    .containerDefinitions[0].logConfiguration.options["awslogs-region"] == $region and
    .containerDefinitions[0].logConfiguration.options["awslogs-stream-prefix"] == "admin"
  ' <<<"$definition_json" >/dev/null || fail_closed "task definition does not match the approved private admin-refresh contract"

network_configuration="awsvpcConfiguration={subnets=[$(IFS=,; printf '%s' "${application_subnet_ids[*]}")],securityGroups=[$admin_security_group_id],assignPublicIp=DISABLED}"
run_json="$(aws ecs run-task \
  --region "$region" \
  --cluster "$cluster" \
  --task-definition "$task_definition" \
  --launch-type FARGATE \
  --platform-version LATEST \
  --count 1 \
  --network-configuration "$network_configuration" \
  --query '{tasks:tasks,failures:failures}' \
  --output json)" || fail_closed "ECS rejected the one approved task launch; no retry is performed"

jq -e '(.tasks | length) == 1 and (.failures | length) == 0' <<<"$run_json" >/dev/null || fail_closed "ECS did not accept exactly one task; no retry is performed"
task_arn="$(jq -er '.tasks[0].taskArn' <<<"$run_json")"

aws ecs wait tasks-stopped --region "$region" --cluster "$cluster" --tasks "$task_arn" || fail_closed "task did not stop before the waiter deadline; no retry is performed"
task_json="$(aws ecs describe-tasks --region "$region" --cluster "$cluster" --tasks "$task_arn" --query 'tasks[0]' --output json)" || fail_closed "stopped task could not be inspected"

jq -e '
  .lastStatus == "STOPPED" and
  ([.containers[] | select(.name == "doris-admin" and .exitCode == 0)] | length) == 1
' <<<"$task_json" >/dev/null || fail_closed "admin-refresh task failed; inspect its CloudWatch stream and do not retry"

subnet_id="$(jq -er '[.attachments[] | select(.type == "ElasticNetworkInterface") | .details[] | select(.name == "subnetId") | .value][0]' <<<"$task_json")"
private_ipv4_address="$(jq -er '[.attachments[] | select(.type == "ElasticNetworkInterface") | .details[] | select(.name == "privateIPv4Address") | .value][0]' <<<"$task_json")"
[[ " ${application_subnet_ids[*]} " == *" $subnet_id "* ]] || fail_closed "task did not report an approved private subnet"
[[ "$private_ipv4_address" =~ ^10\.42\.[0-9]{1,3}\.[0-9]{1,3}$ ]] || fail_closed "task did not report a private Goal 6 address"

task_id="${task_arn##*/}"
log_group="/$name_prefix/doris"
log_streams_json="$(aws logs describe-log-streams \
  --region "$region" \
  --log-group-name "$log_group" \
  --log-stream-name-prefix "admin/doris-admin/$task_id" \
  --query 'logStreams[].{streamName:logStreamName,creationTime:creationTime,lastEventTimestamp:lastEventTimestamp}' \
  --output json)" || fail_closed "CloudWatch log-stream metadata could not be inspected"
jq -e 'length == 1' <<<"$log_streams_json" >/dev/null || fail_closed "exactly one CloudWatch log stream is required"
stream_name="$(jq -er '.[0].streamName' <<<"$log_streams_json")"
events_json="$(aws logs get-log-events \
  --region "$region" \
  --log-group-name "$log_group" \
  --log-stream-name "$stream_name" \
  --start-from-head \
  --query 'events[].message' \
  --output json)" || fail_closed "CloudWatch task evidence could not be read"

jq -e 'any(.[]; test("\\\"operation\\\":\\\"admin-refresh\\\".*\\\"status\\\":\\\"completed\\\""))' <<<"$events_json" >/dev/null || fail_closed "CloudWatch evidence has no completed status; no retry is performed"

jq -n \
  --arg task_arn "$task_arn" \
  --arg task_definition_arn "$(jq -r '.taskDefinitionArn' <<<"$definition_json")" \
  --arg subnet_id "$subnet_id" \
  --arg private_ipv4_address "$private_ipv4_address" \
  --arg security_group_id "$admin_security_group_id" \
  --arg stream_name "$stream_name" \
  '{
    goal:"goal-06",
    operation:"admin-refresh",
    taskArn:$task_arn,
    taskDefinition:$task_definition_arn,
    status:"STOPPED",
    exitCode:0,
    privateSubnetId:$subnet_id,
    privateIpv4Address:$private_ipv4_address,
    securityGroupId:$security_group_id,
    cloudWatchLogStream:$stream_name,
    cloudWatchCompletionStatus:"completed"
  }'
