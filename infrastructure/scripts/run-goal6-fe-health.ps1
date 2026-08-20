[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ExpectedAccountId,
    [Parameter(Mandatory = $true)][string]$Region,
    [Parameter(Mandatory = $true)][string]$NamePrefix,
    [Parameter(Mandatory = $true)][string]$Cluster,
    [Parameter(Mandatory = $true)][string[]]$ApplicationSubnetIds,
    [Parameter(Mandatory = $true)][string]$VerifierSecurityGroupId,
    [Parameter(Mandatory = $true)][string]$TaskDefinition,
    [Parameter(Mandatory = $true)][ValidateRange(1, 9999)][int]$ExpectedRevision,
    [Parameter(Mandatory = $true)][string]$ExpectedImage,
    [Parameter(Mandatory = $true)][string]$ExpectedFeHost,
    [switch]$ConfirmGoal6FeHealth
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Fail-Closed {
    param([Parameter(Mandatory = $true)][string]$Message)
    throw "Goal 6 FE health check stopped: $Message"
}

if (-not $ConfirmGoal6FeHealth) {
    Fail-Closed "the explicit ConfirmGoal6FeHealth approval switch is required."
}
if ($ExpectedAccountId -notmatch '^[0-9]{12}$') {
    Fail-Closed "ExpectedAccountId must be a 12-digit AWS account ID."
}
if ($Region -ne "ap-southeast-1") {
    Fail-Closed "Goal 6 is approved only in ap-southeast-1."
}
if ($ApplicationSubnetIds.Count -lt 2 -or @($ApplicationSubnetIds | Where-Object { $_ -notmatch '^subnet-[0-9a-f]+$' }).Count -gt 0) {
    Fail-Closed "at least two private subnet IDs are required."
}
if ($VerifierSecurityGroupId -notmatch '^sg-[0-9a-f]+$') {
    Fail-Closed "VerifierSecurityGroupId must be an EC2 security-group ID."
}
if ($ExpectedImage -notmatch '^.+@sha256:[0-9a-f]{64}$') {
    Fail-Closed "ExpectedImage must be an immutable digest-pinned image."
}
if ($ExpectedFeHost -notmatch '^10\.42\.[0-9]{1,3}\.[0-9]{1,3}$') {
    Fail-Closed "ExpectedFeHost must be an approved private Goal 6 address."
}

$account = (& aws sts get-caller-identity --query Account --output text)
if ($LASTEXITCODE -ne 0 -or $account.Trim() -ne $ExpectedAccountId) {
    Fail-Closed "AWS account mismatch; no task was launched."
}

$definitionJson = (& aws ecs describe-task-definition --region $Region --task-definition $TaskDefinition --query taskDefinition --output json)
if ($LASTEXITCODE -ne 0) {
    Fail-Closed "the approved task definition could not be inspected."
}
$definition = $definitionJson | ConvertFrom-Json
if ($definition.family -ne "$NamePrefix-doris-verifier") {
    Fail-Closed "task-definition family is not the Goal 6 verifier family."
}
if ([int]$definition.revision -ne $ExpectedRevision) {
    Fail-Closed "task-definition revision does not match ExpectedRevision."
}
if ($definition.networkMode -ne "awsvpc" -or -not ($definition.requiresCompatibilities -contains "FARGATE")) {
    Fail-Closed "task definition is not private Fargate awsvpc."
}
if ($definition.containerDefinitions.Count -ne 1) {
    Fail-Closed "verifier task must contain exactly one container."
}
$container = $definition.containerDefinitions[0]
if ($container.name -ne "doris-verifier" -or $container.image -ne $ExpectedImage -or @($container.command) -join ' ' -ne "/app/doris-readonly-verify") {
    Fail-Closed "task container does not match the approved immutable verifier image/command."
}
if ($null -ne $container.entryPoint -and @($container.entryPoint).Count -gt 0) {
    Fail-Closed "task definition must not override the reviewed image entrypoint."
}
$configuredFeHost = @($container.environment | Where-Object { $_.name -eq "DORIS_FE_HOST" } | Select-Object -ExpandProperty value -First 1)
if ($configuredFeHost.Count -ne 1 -or $configuredFeHost[0] -ne $ExpectedFeHost) {
    Fail-Closed "task definition DORIS_FE_HOST does not match ExpectedFeHost."
}

# ECS DescribeTaskDefinition reports null when it does not override an image
# entrypoint. The immutable ExpectedImage is the reviewed image whose Docker
# configuration is ENTRYPOINT ["/bin/sh"]. Supplying a second /bin/sh would
# make ECS execute '/bin/sh /bin/sh -c …' and prevents the health ping from
# starting. This command is only the MariaDB TLS ping; it performs no SQL.
$healthCommand = 'set -eu; timeout 15 mysqladmin --ssl --protocol=TCP --connect-timeout=5 --host="$DORIS_FE_HOST" --port=9030 ping'
$overrides = @{
    containerOverrides = @(@{
        name    = "doris-verifier"
        command = @("-c", $healthCommand)
    })
} | ConvertTo-Json -Compress -Depth 6
$networkConfiguration = "awsvpcConfiguration={subnets=[$($ApplicationSubnetIds -join ',')],securityGroups=[$VerifierSecurityGroupId],assignPublicIp=DISABLED}"
$runResult = (& aws ecs run-task --region $Region --cluster $Cluster --task-definition $TaskDefinition --launch-type FARGATE --platform-version LATEST --count 1 --network-configuration $networkConfiguration --overrides $overrides --query '{tasks:tasks,failures:failures}' --output json)
if ($LASTEXITCODE -ne 0) {
    Fail-Closed "ECS rejected the one approved task launch. No retry is performed."
}
$run = $runResult | ConvertFrom-Json
if ($null -eq $run.tasks -or $run.tasks.Count -ne 1 -or ($null -ne $run.failures -and $run.failures.Count -gt 0)) {
    Fail-Closed "ECS did not accept exactly one task. No retry is performed."
}

$taskArn = $run.tasks[0].taskArn
& aws ecs wait tasks-stopped --region $Region --cluster $Cluster --tasks $taskArn
if ($LASTEXITCODE -ne 0) {
    Fail-Closed "task did not reach STOPPED before the waiter deadline. No retry is performed."
}
$taskJson = (& aws ecs describe-tasks --region $Region --cluster $Cluster --tasks $taskArn --query 'tasks[0]' --output json)
if ($LASTEXITCODE -ne 0) {
    Fail-Closed "stopped task could not be inspected."
}
$task = $taskJson | ConvertFrom-Json
$containerResult = $task.containers | Where-Object { $_.name -eq "doris-verifier" } | Select-Object -First 1
$eniDetails = @($task.attachments | Where-Object { $_.type -eq "ElasticNetworkInterface" } | ForEach-Object { $_.details })
$subnetId = ($eniDetails | Where-Object { $_.name -eq "subnetId" } | Select-Object -ExpandProperty value -First 1)
$privateIpv4Address = ($eniDetails | Where-Object { $_.name -eq "privateIPv4Address" } | Select-Object -ExpandProperty value -First 1)
if ($task.lastStatus -ne "STOPPED" -or $null -eq $containerResult -or $containerResult.exitCode -ne 0) {
    Fail-Closed "FE health task failed. Inspect its CloudWatch stream; no retry is performed."
}
if ($subnetId -notin $ApplicationSubnetIds -or [string]::IsNullOrWhiteSpace($privateIpv4Address)) {
    Fail-Closed "task did not report the approved private-subnet attachment."
}

# Read CloudWatch only to establish non-sensitive MariaDB listener evidence.
$taskId = ($taskArn -split '/')[-1]
$logStreamPrefix = "verifier/doris-verifier/"
$logStreamsJson = (& aws logs describe-log-streams --region $Region --log-group-name "/$NamePrefix/doris" --log-stream-name-prefix "$logStreamPrefix$taskId" --query 'logStreams[].{streamName:logStreamName,creationTime:creationTime,lastEventTimestamp:lastEventTimestamp}' --output json)
if ($LASTEXITCODE -ne 0) {
    Fail-Closed "CloudWatch log-stream metadata could not be inspected."
}
$logStreams = @($logStreamsJson | ConvertFrom-Json)
if ($logStreams.Count -lt 1) {
    Fail-Closed "no CloudWatch log stream was found for the stopped task."
}
$streamName = $logStreams[0].streamName
$eventsJson = (& aws logs get-log-events --region $Region --log-group-name "/$NamePrefix/doris" --log-stream-name $streamName --start-from-head --query 'events[].message' --output json)
if ($LASTEXITCODE -ne 0) {
    Fail-Closed "CloudWatch task evidence could not be read."
}
$events = @($eventsJson | ConvertFrom-Json)
$listenerEvent = $events | Where-Object {
    $_ -match 'mysqld is alive' -or $_ -match 'Access denied for user'
} | Select-Object -Last 1
if ([string]::IsNullOrWhiteSpace($listenerEvent)) {
    Fail-Closed "CloudWatch evidence did not prove MariaDB listener reachability. No retry is performed."
}
$listenerEvidence = if ($listenerEvent -match 'mysqld is alive') {
    "mysqladmin-alive"
} else {
    "authenticated-listener-response"
}

@{
    goal = "goal-06"
    operation = "fe-health"
    taskArn = $taskArn
    taskDefinition = $definition.taskDefinitionArn
    status = $task.lastStatus
    exitCode = $containerResult.exitCode
    privateSubnetId = $subnetId
    privateIpv4Address = $privateIpv4Address
    securityGroupId = $VerifierSecurityGroupId
    target = "${ExpectedFeHost}:9030"
    cloudWatchLogStreams = $logStreams
    cloudWatchHealthStatus = "listener-reachable"
    cloudWatchListenerEvidence = $listenerEvidence
} | ConvertTo-Json -Depth 6
