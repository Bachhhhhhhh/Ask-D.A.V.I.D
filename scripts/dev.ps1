[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet(
        "setup", "format", "format-check", "lint", "typecheck", "test", "validate-env",
        "security", "check", "local-up", "local-down", "local-logs", "infra-format", "infra-validate",
        "infra-lint", "infra-security", "infra-test", "infra-preflight", "infra-plan",
        "databricks-static", "clean"
    )]
    [string]$Command
)

$repositoryRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repositoryRoot

if ($Command -eq "clean") {
    & py -3.12 scripts/dev.py $Command
} else {
    & uv run python scripts/dev.py $Command
}

exit $LASTEXITCODE
