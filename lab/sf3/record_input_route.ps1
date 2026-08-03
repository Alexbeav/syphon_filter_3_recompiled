[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Project,
    [Parameter(Mandatory = $true)]
    [string]$Route,
    [string]$MemcardDir,
    [switch]$Silent
)

$ErrorActionPreference = 'Stop'
$projectPath = (Resolve-Path -LiteralPath $Project).Path
$exe = Join-Path $projectPath 'build\Syphon_Filter_3_Recompiled.exe'
$game = Join-Path $projectPath 'game.toml'
if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) {
    throw "Missing ordinary Release executable: $exe"
}
if (-not (Test-Path -LiteralPath $game -PathType Leaf)) {
    throw "Missing generated game configuration: $game"
}

$routePath = [IO.Path]::GetFullPath($Route)
if (Test-Path -LiteralPath $routePath) {
    throw "Refusing to overwrite input route: $routePath"
}
if (Test-Path -LiteralPath ($routePath + '.partial')) {
    throw "Refusing to overwrite partial input route: $routePath.partial"
}
$routeParent = Split-Path -Parent $routePath
if ($routeParent) {
    New-Item -ItemType Directory -Path $routeParent -Force | Out-Null
}

if (-not $MemcardDir) {
    $MemcardDir = Join-Path $projectPath 'playtest-memory-card'
}
$memcardPath = [IO.Path]::GetFullPath($MemcardDir)
New-Item -ItemType Directory -Path $memcardPath -Force | Out-Null

$savedRecord = $env:PSX_INPUT_RECORD
$savedReplay = $env:PSX_INPUT_REPLAY
$savedAudio = $env:SDL_AUDIODRIVER
try {
    $env:PSX_INPUT_RECORD = $routePath
    Remove-Item Env:PSX_INPUT_REPLAY -ErrorAction SilentlyContinue
    if ($Silent) { $env:SDL_AUDIODRIVER = 'dummy' }

    Write-Host "Recording retail-boundary input to $routePath"
    Write-Host 'Release all controls before closing the game to leave a neutral bookend.'
    Push-Location (Split-Path -Parent $exe)
    try {
        & $exe --no-launcher --game $game --memcard-dir $memcardPath
        $exitCode = $LASTEXITCODE
    } finally {
        Pop-Location
    }
} finally {
    if ($null -eq $savedRecord) { Remove-Item Env:PSX_INPUT_RECORD -ErrorAction SilentlyContinue }
    else { $env:PSX_INPUT_RECORD = $savedRecord }
    if ($null -eq $savedReplay) { Remove-Item Env:PSX_INPUT_REPLAY -ErrorAction SilentlyContinue }
    else { $env:PSX_INPUT_REPLAY = $savedReplay }
    if ($null -eq $savedAudio) { Remove-Item Env:SDL_AUDIODRIVER -ErrorAction SilentlyContinue }
    else { $env:SDL_AUDIODRIVER = $savedAudio }
}

if ($exitCode -ne 0) { exit $exitCode }
if (-not (Test-Path -LiteralPath $routePath -PathType Leaf)) {
    throw "The game exited without finalizing the route; inspect $routePath.partial"
}
Write-Host "Input route finalized: $routePath"
