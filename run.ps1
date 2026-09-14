param(
    [string]$Config = "configs/new_york.yaml",
    [ValidateSet("run", "prepare")][string]$Command = "run"
)
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
conda run --no-capture-output -n my-neuro python -u -m mapagents $Command --config $Config
exit $LASTEXITCODE
