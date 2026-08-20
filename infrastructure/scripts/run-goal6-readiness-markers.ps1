[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ExpectedAccountId,
    [Parameter(Mandatory = $true)][string]$Region,
    [Parameter(Mandatory = $true)][string]$NamePrefix,
    [Parameter(Mandatory = $true)][string]$Cluster,
    [Parameter(Mandatory = $true)][string[]]$ApplicationSubnetIds,
    [Parameter(Mandatory = $true)][string]$AdminSecurityGroupId,
    [Parameter(Mandatory = $true)][string]$TaskDefinition,
    [Parameter(Mandatory = $true)][ValidateRange(1, 9999)][int]$ExpectedRevision,
    [Parameter(Mandatory = $true)][string]$ExpectedImage,
    [Parameter(Mandatory = $true)][string]$ExpectedFeHost,
    [Parameter(Mandatory = $true)][string]$ExpectedBeHost,
    [switch]$ConfirmGoal6ReadinessMarkers
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Fail-Closed {
    param([Parameter(Mandatory = $true)][string]$Message)
    throw "Goal 6 readiness-marker diagnostic stopped: $Message"
}

if (-not $ConfirmGoal6ReadinessMarkers) {
    Fail-Closed "the explicit ConfirmGoal6ReadinessMarkers approval switch is required."
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
if ($AdminSecurityGroupId -notmatch '^sg-[0-9a-f]+$') {
    Fail-Closed "AdminSecurityGroupId must be an EC2 security-group ID."
}
if ($ExpectedImage -notmatch '^.+@sha256:[0-9a-f]{64}$') {
    Fail-Closed "ExpectedImage must be an immutable digest-pinned image."
}
foreach ($hostAddress in @($ExpectedFeHost, $ExpectedBeHost)) {
    if ($hostAddress -notmatch '^10\.42\.[0-9]{1,3}\.[0-9]{1,3}$') {
        Fail-Closed "FE and BE hosts must be approved private Goal 6 addresses."
    }
}
if ($ExpectedFeHost -eq $ExpectedBeHost) {
    Fail-Closed "FE and BE hosts must be distinct."
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
if ($definition.family -ne "$NamePrefix-doris-admin-refresh") {
    Fail-Closed "task-definition family is not the Goal 6 admin family."
}
if ([int]$definition.revision -ne $ExpectedRevision) {
    Fail-Closed "task-definition revision does not match ExpectedRevision."
}
if ($definition.networkMode -ne "awsvpc" -or -not ($definition.requiresCompatibilities -contains "FARGATE")) {
    Fail-Closed "task definition is not private Fargate awsvpc."
}
if ($definition.containerDefinitions.Count -ne 1) {
    Fail-Closed "admin task must contain exactly one container."
}
$container = $definition.containerDefinitions[0]
if ($container.name -ne "doris-admin" -or $container.image -ne $ExpectedImage -or @($container.command) -join ' ' -ne "/app/doris-admin-refresh") {
    Fail-Closed "task container does not match the approved immutable admin image/command."
}
if ($null -ne $container.entryPoint -and @($container.entryPoint).Count -gt 0) {
    Fail-Closed "task definition must not override the reviewed image entrypoint."
}
$configuredFeHost = @($container.environment | Where-Object { $_.name -eq "DORIS_FE_HOST" } | Select-Object -ExpandProperty value -First 1)
$configuredBeHost = @($container.environment | Where-Object { $_.name -eq "DORIS_BE_HOST" } | Select-Object -ExpandProperty value -First 1)
if ($configuredFeHost.Count -ne 1 -or $configuredFeHost[0] -ne $ExpectedFeHost) {
    Fail-Closed "task definition DORIS_FE_HOST does not match ExpectedFeHost."
}
if ($configuredBeHost.Count -ne 1 -or $configuredBeHost[0] -ne $ExpectedBeHost) {
    Fail-Closed "task definition DORIS_BE_HOST does not match ExpectedBeHost."
}
$adminSecretReferences = @($container.secrets | Where-Object { $_.name -eq "DORIS_ADMIN_SECRET" })
if ($adminSecretReferences.Count -ne 1 -or $adminSecretReferences[0].valueFrom -notmatch '^arn:aws:secretsmanager:ap-southeast-1:[0-9]{12}:secret:') {
    Fail-Closed "task definition must inject exactly one approved Doris admin secret reference."
}

# The immutable image supplies ENTRYPOINT ["/bin/sh"], so the ECS override is
# exactly [-c, script]. The script performs only SHOW BACKENDS and emits five
# sanitized current-state markers. Credentials remain in MYSQL_PWD inside the
# task and neither the row nor any secret value is printed.
$markerCommand = @'
set -eu
admin_user="$(printf '%s' "$DORIS_ADMIN_SECRET" | jq -er '.username')"
admin_password="$(printf '%s' "$DORIS_ADMIN_SECRET" | jq -er '.password')"
if ! backend_rows="$(MYSQL_PWD="$admin_password" timeout 30 mariadb --ssl --protocol=TCP --connect-timeout=5 --host="$DORIS_FE_HOST" --port=9030 --user="$admin_user" --batch --skip-column-names -e 'SHOW BACKENDS;' 2>/dev/null)"; then
  printf '%s\n' '{"goal":"goal-06","operation":"readiness-markers","role":"fe","listener_state":"unavailable","marker":"doris-port-unavailable","port":9030}'
  exit 1
fi
printf '%s\n' '{"goal":"goal-06","operation":"readiness-markers","role":"fe","listener_state":"ready"}'
printf '%s\n' '{"goal":"goal-06","operation":"readiness-markers","role":"fe","marker":"doris-port-ready","port":9030}'
if ! printf '%s\n' "$backend_rows" | awk -F '\t' -v host="$DORIS_BE_HOST" '
  $2 == host {
    total_capacity = $17
    if (tolower($10) == "true" && tolower($11) == "false" && total_capacity !~ /^0([.]0+)?([[:space:]]*[[:alpha:]]+)?$/) {
      found = 1
    }
    exit
  }
  END { exit(found ? 0 : 1) }
'; then
  printf '%s\n' '{"goal":"goal-06","operation":"readiness-markers","role":"be","listener_state":"unavailable","marker":"be-storage-capacity-unavailable","port":9050}'
  exit 1
fi
printf '%s\n' '{"goal":"goal-06","operation":"readiness-markers","role":"be","listener_state":"ready"}'
printf '%s\n' '{"goal":"goal-06","operation":"readiness-markers","role":"be","marker":"doris-port-ready","port":9050}'
printf '%s\n' '{"goal":"goal-06","operation":"readiness-markers","role":"be","marker":"be-storage-capacity-ready","alive":true,"decommissioned":false,"non_zero_total_capacity":true}'
'@

$overrides = @{
    containerOverrides = @(@{
        name    = "doris-admin"
        command = @("-c", $markerCommand)
    })
} | ConvertTo-Json -Compress -Depth 6
$networkConfiguration = "awsvpcConfiguration={subnets=[$($ApplicationSubnetIds -join ',')],securityGroups=[$AdminSecurityGroupId],assignPublicIp=DISABLED}"
$runResult = (& aws ecs run-task --region $Region --cluster $Cluster --task-definition $TaskDefinition --launch-type FARGATE --platform-version LATEST --count 1 --network-configuration $networkConfiguration --overrides $overrides --query '{tasks:tasks,failures:failures}' --output json)
if ($LASTEXITCODE -ne 0) {
    Fail-Closed "ECS rejected the one approved diagnostic task launch. No retry is performed."
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
$containerResult = $task.containers | Where-Object { $_.name -eq "doris-admin" } | Select-Object -First 1
$eniDetails = @($task.attachments | Where-Object { $_.type -eq "ElasticNetworkInterface" } | ForEach-Object { $_.details })
$subnetId = ($eniDetails | Where-Object { $_.name -eq "subnetId" } | Select-Object -ExpandProperty value -First 1)
$privateIpv4Address = ($eniDetails | Where-Object { $_.name -eq "privateIPv4Address" } | Select-Object -ExpandProperty value -First 1)
if ($task.lastStatus -ne "STOPPED" -or $null -eq $containerResult -or $containerResult.exitCode -ne 0) {
    Fail-Closed "readiness-marker task failed. Inspect its CloudWatch stream; no retry is performed."
}
if ($subnetId -notin $ApplicationSubnetIds -or [string]::IsNullOrWhiteSpace($privateIpv4Address)) {
    Fail-Closed "task did not report the approved private-subnet attachment."
}

$taskId = ($taskArn -split '/')[-1]
$logStreamPrefix = "admin/doris-admin/"
$logStreamsJson = (& aws logs describe-log-streams --region $Region --log-group-name "/$NamePrefix/doris" --log-stream-name-prefix "$logStreamPrefix$taskId" --query 'logStreams[].{streamName:logStreamName,creationTime:creationTime,lastEventTimestamp:lastEventTimestamp}' --output json)
if ($LASTEXITCODE -ne 0) {
    Fail-Closed "CloudWatch log-stream metadata could not be inspected."
}
$logStreams = @($logStreamsJson | ConvertFrom-Json)
if ($logStreams.Count -ne 1) {
    Fail-Closed "exactly one CloudWatch log stream is required for the stopped task."
}
$streamName = $logStreams[0].streamName
$eventsJson = (& aws logs get-log-events --region $Region --log-group-name "/$NamePrefix/doris" --log-stream-name $streamName --start-from-head --query 'events[].message' --output json)
if ($LASTEXITCODE -ne 0) {
    Fail-Closed "CloudWatch marker evidence could not be read."
}
$events = @($eventsJson | ConvertFrom-Json)
$requiredMarkers = @(
    @{ Name = "fe-listener-ready"; Pattern = '"role":"fe".*"listener_state":"ready"' },
    @{ Name = "fe-port-ready"; Pattern = '"role":"fe".*"marker":"doris-port-ready".*"port":9030' },
    @{ Name = "be-listener-ready"; Pattern = '"role":"be".*"listener_state":"ready"' },
    @{ Name = "be-port-ready"; Pattern = '"role":"be".*"marker":"doris-port-ready".*"port":9050' },
    @{ Name = "be-capacity-ready"; Pattern = '"role":"be".*"marker":"be-storage-capacity-ready".*"non_zero_total_capacity":true' }
)
foreach ($requiredMarker in $requiredMarkers) {
    if ($null -eq ($events | Where-Object { $_ -match $requiredMarker.Pattern } | Select-Object -First 1)) {
        Fail-Closed "CloudWatch evidence is missing marker $($requiredMarker.Name). No retry is performed."
    }
}
if ($null -ne ($events | Where-Object { $_ -match 'doris-port-unavailable|be-storage-capacity-unavailable' } | Select-Object -First 1)) {
    Fail-Closed "CloudWatch evidence contains a terminal unavailable marker. No retry is performed."
}

@{
    goal = "goal-06"
    operation = "readiness-markers"
    taskArn = $taskArn
    taskDefinition = $definition.taskDefinitionArn
    status = $task.lastStatus
    exitCode = $containerResult.exitCode
    privateSubnetId = $subnetId
    privateIpv4Address = $privateIpv4Address
    securityGroupId = $AdminSecurityGroupId
    feTarget = "${ExpectedFeHost}:9030"
    beTarget = "${ExpectedBeHost}:9050"
    cloudWatchLogStreams = $logStreams
    cloudWatchMarkers = @($requiredMarkers | ForEach-Object { $_.Name })
} | ConvertTo-Json -Depth 6
