[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Project,
    [Parameter(Mandatory = $true)]
    [string]$Route,
    [Parameter(Mandatory = $true)]
    [string]$Out,
    [ValidateSet('opengl', 'software')]
    [string]$Renderer = 'opengl',
    [switch]$Diagnostic
)

$ErrorActionPreference = 'Stop'
$projectPath = (Resolve-Path -LiteralPath $Project).Path
$buildName = if ($Diagnostic) { 'build-r1' } else { 'build' }
$exe = Join-Path $projectPath "$buildName\Syphon_Filter_3_Recompiled.exe"
$game = Join-Path $projectPath 'game.toml'
$routePath = (Resolve-Path -LiteralPath $Route).Path
foreach ($item in @(
    @{ Path = $exe; Label = 'Release executable' },
    @{ Path = $game; Label = 'generated game configuration' },
    @{ Path = $routePath; Label = 'input route' }
)) {
    if (-not (Test-Path -LiteralPath $item.Path -PathType Leaf)) {
        throw "Missing $($item.Label): $($item.Path)"
    }
}

$header = @(Get-Content -LiteralPath $routePath -TotalCount 1)[0] -split '\s+'
if ($header.Count -ne 3 -or $header[0] -ne 'PSXPAD2') {
    throw 'Input route must have a PSXPAD2 header with count and compatibility ID'
}
$sampleCount = 0L
if (-not [long]::TryParse($header[1], [ref]$sampleCount) -or
    $sampleCount -lt 1 -or $sampleCount -gt 10000000) {
    throw "Invalid input route sample count: $($header[1])"
}
if ($header[2] -eq '-') {
    throw 'Input route has no runtime compatibility ID'
}

$outPath = [IO.Path]::GetFullPath($Out)
if (Test-Path -LiteralPath $outPath) {
    throw "Output directory must not already exist: $outPath"
}
$memcardPath = Join-Path $outPath 'memcard'
New-Item -ItemType Directory -Path $memcardPath -Force | Out-Null

$savedReplay = $env:PSX_INPUT_REPLAY
$savedRecord = $env:PSX_INPUT_RECORD
$savedStop = $env:PSX_INPUT_STOP_AFTER
$savedAudio = $env:SDL_AUDIODRIVER
try {
    $env:PSX_INPUT_REPLAY = $routePath
    Remove-Item Env:PSX_INPUT_RECORD -ErrorAction SilentlyContinue
    $env:PSX_INPUT_STOP_AFTER = [string]$sampleCount
    $env:SDL_AUDIODRIVER = 'dummy'

    $stdoutPath = Join-Path $outPath 'stdout.log'
    $stderrPath = Join-Path $outPath 'stderr.log'
    Push-Location (Split-Path -Parent $exe)
    try {
        & $exe --hidden-window --no-launcher --renderer $Renderer `
            --game $game --memcard-dir $memcardPath `
            1> $stdoutPath 2> $stderrPath
        $exitCode = $LASTEXITCODE
    } finally {
        Pop-Location
    }
} finally {
    if ($null -eq $savedReplay) { Remove-Item Env:PSX_INPUT_REPLAY -ErrorAction SilentlyContinue }
    else { $env:PSX_INPUT_REPLAY = $savedReplay }
    if ($null -eq $savedRecord) { Remove-Item Env:PSX_INPUT_RECORD -ErrorAction SilentlyContinue }
    else { $env:PSX_INPUT_RECORD = $savedRecord }
    if ($null -eq $savedStop) { Remove-Item Env:PSX_INPUT_STOP_AFTER -ErrorAction SilentlyContinue }
    else { $env:PSX_INPUT_STOP_AFTER = $savedStop }
    if ($null -eq $savedAudio) { Remove-Item Env:SDL_AUDIODRIVER -ErrorAction SilentlyContinue }
    else { $env:SDL_AUDIODRIVER = $savedAudio }
}

if ($exitCode -ne 0) {
    throw "Input replay exited with code $exitCode; inspect $stderrPath"
}
$completion = Select-String -LiteralPath $stdoutPath `
    -Pattern "bounded input sample limit reached \($sampleCount\)" -Quiet
if (-not $completion) {
    throw "Input replay did not reach all $sampleCount samples; inspect $stdoutPath"
}
Write-Host "Input replay completed: $outPath"
