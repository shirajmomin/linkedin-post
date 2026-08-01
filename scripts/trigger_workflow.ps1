# Trigger LinkedIn Post Agent on GitHub (reliable alternative to schedule cron)
param(
    [string]$Topic = "",
    [switch]$NoAi
)

$ErrorActionPreference = "Stop"
$argsList = @("workflow", "run", "LinkedIn Post Agent", "--ref", "main")
if ($Topic) {
    $argsList += @("-f", "topic=$Topic")
}
if ($NoAi) {
    $argsList += @("-f", "no_ai=true")
}

Write-Host "Triggering LinkedIn Post Agent..."
& gh @argsList
if ($LASTEXITCODE -ne 0) {
    throw "gh workflow run failed (exit $LASTEXITCODE). Run: gh auth login"
}
Write-Host "Triggered. Check: https://github.com/shirajmomin/linkedin-post/actions"
