[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Project,
    [ValidateSet('opengl', 'software')]
    [string]$Renderer = 'opengl',
    [string]$ReleaseWtrace = '',
    [string]$Executable = '',
    [switch]$OverlayNativeOff
)

$ErrorActionPreference = 'Stop'

function ConvertTo-NativeArgument([string]$Value) {
    if ($Value.Length -gt 0 -and $Value -notmatch '[\s"]') { return $Value }
    $escaped = [regex]::Replace($Value, '(\\*)"', {
        param($match)
        return $match.Groups[1].Value + $match.Groups[1].Value + '\"'
    })
    $escaped = [regex]::Replace($escaped, '(\\+)$', {
        param($match)
        return $match.Value + $match.Value
    })
    return '"' + $escaped + '"'
}

$projectPath = (Resolve-Path -LiteralPath $Project).Path
$buildPath = Join-Path $projectPath 'build'
$gamePath = Join-Path $projectPath 'game.toml'
$executables = if ($Executable) {
    $selected = (Resolve-Path -LiteralPath $Executable).Path
    if ([IO.Path]::GetDirectoryName($selected) -ne $buildPath) {
        throw "Explicit executable must be inside the project build directory: $selected"
    }
    @((Get-Item -LiteralPath $selected))
} else {
    @(Get-ChildItem -LiteralPath $buildPath -Filter '*_Recompiled.exe' -File)
}
if ($executables.Count -ne 1) {
    throw "Expected exactly one ordinary Release executable; found $($executables.Count). Use -Executable to select it explicitly."
}
if (-not (Test-Path -LiteralPath $gamePath -PathType Leaf)) {
    throw "Missing game configuration: $gamePath"
}

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$sessionPath = Join-Path $projectPath "evidence\human-transition-$stamp"
$memcardPath = Join-Path $sessionPath 'memcard'
$routePath = Join-Path $sessionPath 'manual-input.psxpad'
New-Item -ItemType Directory -Path $memcardPath -Force | Out-Null

$savedRecord = $env:PSX_INPUT_RECORD
$savedReplay = $env:PSX_INPUT_REPLAY
$savedStop = $env:PSX_INPUT_STOP_AFTER
$savedReleaseWtrace = $env:PSX_RELEASE_WTRACE
$savedOverlayNativeOff = $env:PSX_OVERLAY_NATIVE_OFF
try {
    $env:PSX_INPUT_RECORD = $routePath
    Remove-Item Env:PSX_INPUT_REPLAY -ErrorAction SilentlyContinue
    Remove-Item Env:PSX_INPUT_STOP_AFTER -ErrorAction SilentlyContinue
    if ($ReleaseWtrace) { $env:PSX_RELEASE_WTRACE = $ReleaseWtrace }
    else { Remove-Item Env:PSX_RELEASE_WTRACE -ErrorAction SilentlyContinue }
    if ($OverlayNativeOff) { $env:PSX_OVERLAY_NATIVE_OFF = '1' }
    else { Remove-Item Env:PSX_OVERLAY_NATIVE_OFF -ErrorAction SilentlyContinue }

    Write-Host "Evidence session: $sessionPath"
    Write-Host 'Play normally. On a freeze, wait five seconds for the bounded report, then close the game.'
    $start = [Diagnostics.ProcessStartInfo]::new()
    $start.FileName = $executables[0].FullName
    $start.WorkingDirectory = $sessionPath
    $start.UseShellExecute = $false
    $launchArguments = @(
        '--no-launcher', '--renderer', $Renderer,
        '--game', $gamePath, '--memcard-dir', $memcardPath
    )
    $start.Arguments = (($launchArguments | ForEach-Object {
        ConvertTo-NativeArgument ([string]$_)
    }) -join ' ')
    $process = [Diagnostics.Process]::Start($start)
    $process.WaitForExit()
    $exitCode = $process.ExitCode
} finally {
    if ($null -eq $savedRecord) { Remove-Item Env:PSX_INPUT_RECORD -ErrorAction SilentlyContinue }
    else { $env:PSX_INPUT_RECORD = $savedRecord }
    if ($null -eq $savedReplay) { Remove-Item Env:PSX_INPUT_REPLAY -ErrorAction SilentlyContinue }
    else { $env:PSX_INPUT_REPLAY = $savedReplay }
    if ($null -eq $savedStop) { Remove-Item Env:PSX_INPUT_STOP_AFTER -ErrorAction SilentlyContinue }
    else { $env:PSX_INPUT_STOP_AFTER = $savedStop }
    if ($null -eq $savedReleaseWtrace) { Remove-Item Env:PSX_RELEASE_WTRACE -ErrorAction SilentlyContinue }
    else { $env:PSX_RELEASE_WTRACE = $savedReleaseWtrace }
    if ($null -eq $savedOverlayNativeOff) { Remove-Item Env:PSX_OVERLAY_NATIVE_OFF -ErrorAction SilentlyContinue }
    else { $env:PSX_OVERLAY_NATIVE_OFF = $savedOverlayNativeOff }
}

$partialPath = $routePath + '.partial'
$freeze = @(Get-ChildItem -LiteralPath $sessionPath -Filter 'psx_freeze_dump_*.json' -File)
Write-Host "Runtime exit code: $exitCode"
Write-Host "Final input route present: $(Test-Path -LiteralPath $routePath -PathType Leaf)"
Write-Host "Crash-resilient input prefix present: $(Test-Path -LiteralPath $partialPath -PathType Leaf)"
Write-Host "Freeze reports: $($freeze.Count)"
Write-Host "Retain this directory for diagnosis: $sessionPath"

if ($exitCode -ne 0) { exit $exitCode }
