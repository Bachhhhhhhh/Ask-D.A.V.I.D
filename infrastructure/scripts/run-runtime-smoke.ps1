[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ExpectedAccountId,
    [Parameter(Mandatory = $true)][string]$Region,
    [Parameter(Mandatory = $true)][string]$NamePrefix,
    [Parameter(Mandatory = $true)][string]$Cluster,
    [Parameter(Mandatory = $true)][string[]]$ApplicationSubnetIds,
    [Parameter(Mandatory = $true)][string]$SmokeSecurityGroupId,
    [Parameter(Mandatory = $true)][string]$PostgresTaskDefinition,
    [Parameter(Mandatory = $true)][string]$RedisTaskDefinition,
    [Parameter(Mandatory = $true)][string]$S3TaskDefinition,
    [switch]$ConfirmCheckpoint3B
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not $ConfirmCheckpoint3B) {
    throw "Checkpoint 3B approval is required. This script launches only the three Terraform-created synthetic smoke tasks."
}
if ($Region -ne "ap-southeast-1") {
    throw "Goal 3B smoke tasks are approved only in ap-southeast-1."
}
if ($ApplicationSubnetIds.Count -lt 2) {
    throw "At least two private application subnet IDs are required."
}

$account = (& aws sts get-caller-identity --query Account --output text)
if ($LASTEXITCODE -ne 0 -or $account -ne $ExpectedAccountId) {
    throw "AWS account mismatch; no smoke task was launched."
}

$networkConfiguration = "awsvpcConfiguration={subnets=[$($ApplicationSubnetIds -join ',')],securityGroups=[$SmokeSecurityGroupId],assignPublicIp=DISABLED}"
$privateEcrCache = "${ExpectedAccountId}.dkr.ecr.${Region}.amazonaws.com/ecr-public"
$expectedImages = @{
    postgres = "$privateEcrCache/docker/library/postgres@sha256:57c72fd2a128e416c7fcc499958864df5301e940bca0a56f58fddf30ffc07777"
    redis    = "$privateEcrCache/docker/library/redis@sha256:e7723ff73d963f5cc6d9c4643ea3d989527a402a319239054e9472a7fb9219a2"
    s3       = "$privateEcrCache/aws-cli/aws-cli@sha256:7e0331f50ea97c09241521688082ef39a95b5f10ddd2eaabeef4313d974b5258"
}

function Invoke-StaticSmokeTask {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][ValidateSet("postgres", "redis", "s3")][string]$SmokeKey,
        [Parameter(Mandatory = $true)][string]$TaskDefinition
    )

    $definitionResult = (& aws ecs describe-task-definition --region $Region --task-definition $TaskDefinition --query taskDefinition --output json)
    if ($LASTEXITCODE -ne 0) {
        throw "$Name task definition could not be inspected."
    }
    $definition = $definitionResult | ConvertFrom-Json
    $expectedTaskRole = "arn:aws:iam::$ExpectedAccountId:role/$NamePrefix-smoke-task"
    $expectedExecutionRole = "arn:aws:iam::$ExpectedAccountId:role/$NamePrefix-smoke-execution"
    if ($definition.family -ne "$NamePrefix-smoke-$SmokeKey" -or $definition.taskRoleArn -ne $expectedTaskRole -or $definition.executionRoleArn -ne $expectedExecutionRole -or $definition.networkMode -ne "awsvpc" -or $definition.containerDefinitions.Count -ne 1 -or $definition.containerDefinitions[0].image -ne $expectedImages[$SmokeKey] -or -not ($definition.requiresCompatibilities -contains "FARGATE")) {
        throw "$Name task definition does not match the approved Terraform-created static smoke task."
    }

    $runResult = (& aws ecs run-task --region $Region --cluster $Cluster --task-definition $TaskDefinition --launch-type FARGATE --platform-version LATEST --count 1 --network-configuration $networkConfiguration --query '{tasks:tasks,failures:failures}' --output json)
    if ($LASTEXITCODE -ne 0) {
        throw "$Name smoke task launch failed."
    }
    $run = $runResult | ConvertFrom-Json
    if ($null -eq $run.tasks -or $run.tasks.Count -ne 1 -or ($null -ne $run.failures -and $run.failures.Count -gt 0)) {
        throw "$Name smoke task was not accepted by ECS."
    }

    $taskArn = $run.tasks[0].taskArn
    & aws ecs wait tasks-stopped --region $Region --cluster $Cluster --tasks $taskArn
    if ($LASTEXITCODE -ne 0) {
        throw "$Name smoke task did not stop successfully before the ECS waiter deadline."
    }

    $taskResult = (& aws ecs describe-tasks --region $Region --cluster $Cluster --tasks $taskArn --query 'tasks[0]' --output json)
    if ($LASTEXITCODE -ne 0) {
        throw "$Name smoke task could not be inspected."
    }
    $task = $taskResult | ConvertFrom-Json
    if ($task.lastStatus -ne "STOPPED" -or $task.containers.Count -ne 1 -or $task.containers[0].exitCode -ne 0) {
        throw "$Name smoke task failed. Inspect only its CloudWatch stream; do not retrieve or print secret values."
    }

    # Fargate may delete a stopped task's ENI before a follow-up EC2 lookup.
    # Validate the durable ECS attachment metadata instead. The launch request
    # above is constructed locally with assignPublicIp=DISABLED and cannot be
    # overridden by a caller.
    $eniDetails = @(($task.attachments | Where-Object { $_.type -eq "ElasticNetworkInterface" }).details)
    $eniId = $eniDetails |
        Where-Object { $_.name -eq "networkInterfaceId" } |
        Select-Object -ExpandProperty value
    $privateIpv4Address = $eniDetails |
        Where-Object { $_.name -eq "privateIPv4Address" } |
        Select-Object -ExpandProperty value
    if (
        [string]::IsNullOrWhiteSpace($eniId) -or
        [string]::IsNullOrWhiteSpace($privateIpv4Address)
    ) {
        throw "$Name smoke task did not report a private ECS ENI attachment."
    }

    Write-Output "$Name synthetic smoke task passed with assignPublicIp disabled and a private ECS attachment."
}

Invoke-StaticSmokeTask -Name "PostgreSQL TLS SELECT 1" -SmokeKey "postgres" -TaskDefinition $PostgresTaskDefinition
Invoke-StaticSmokeTask -Name "Redis TLS PING" -SmokeKey "redis" -TaskDefinition $RedisTaskDefinition
Invoke-StaticSmokeTask -Name "S3 raw allow / curated deny" -SmokeKey "s3" -TaskDefinition $S3TaskDefinition
Write-Output "Goal 3B dynamic runtime smoke tasks passed."
