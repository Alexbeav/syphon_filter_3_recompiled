[CmdletBinding()]
param(
    [string]$CuePath,
    [string]$OutputDirectory,
    [string]$Mingw,
    [switch]$InstallDependencies,
    [switch]$NoInstallDependencies,
    [switch]$PreflightOnly,
    [switch]$ResolveCueOnly,
    [ValidateRange(1, 64)]
    [int]$BuildJobs = [Math]::Min(4, [Math]::Max(1, [Environment]::ProcessorCount))
)

$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$Kit = $PSScriptRoot
$ToolchainDir = Join-Path $Kit 'dependencies'
$WinLibsVersion = '16.1.0-14.0.0-r4'
$WinLibsArchiveName = 'winlibs-x86_64-posix-seh-gcc-16.1.0-mingw-w64ucrt-14.0.0-r4.zip'
$WinLibsUrl = "https://github.com/brechtsanders/winlibs_mingw/releases/download/16.1.0posix-14.0.0-ucrt-r4/$WinLibsArchiveName"
$WinLibsSha256 = 'c406a22f8cac82559a3a1d96b62ff603f666499fb5ff4784e87b4eb6fa37dede'
$WinLibsRoot = Join-Path $ToolchainDir "winlibs-$WinLibsVersion"
$PythonVersion = '3.13.14'
$PythonArchiveName = "python-$PythonVersion-embed-amd64.zip"
$PythonUrl = "https://www.python.org/ftp/python/$PythonVersion/$PythonArchiveName"
$PythonSha256 = '90b4e5b9898b72d744650524bff92377c367f44bd5fbd09e3148656c080ad907'
$PythonRoot = Join-Path $ToolchainDir "python-$PythonVersion"
$SetupLog = Join-Path $Kit 'setup.log'
$TranscriptStarted = $false

function Get-Sha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
}

function Find-Application([string]$Name, [string[]]$Candidates = @()) {
    $command = Get-Command $Name -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($command) { return $command.Source }
    if ($env:SF3_SETUP_DISABLE_STANDARD_DISCOVERY -eq '1') { return $null }
    foreach ($pattern in $Candidates) {
        if (-not $pattern) { continue }
        $match = Get-ChildItem -Path $pattern -File -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($match) { return $match.FullName }
    }
    return $null
}

function Test-Python([string]$File, [string[]]$Prefix = @()) {
    if (-not $File) { return $null }
    try {
        & $File @Prefix -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' *> $null
        if ($LASTEXITCODE -eq 0) {
            return [pscustomobject]@{ File = $File; Prefix = @($Prefix) }
        }
    } catch {}
    return $null
}

function Find-Python {
    $result = Test-Python (Join-Path $PythonRoot 'python.exe')
    if ($result) { return $result }
    $python = Get-Command python -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($python -and $python.Source -notmatch '(?i)\\WindowsApps\\python(?:3)?\.exe$') {
        $result = Test-Python $python.Source
        if ($result) { return $result }
    }
    $py = Get-Command py -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($py) {
        $result = Test-Python $py.Source @('-3')
        if ($result) { return $result }
    }
    if ($env:SF3_SETUP_DISABLE_STANDARD_DISCOVERY -ne '1') {
        foreach ($pattern in @(
            "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe",
            "$env:ProgramFiles\Python*\python.exe",
            "${env:ProgramFiles(x86)}\Python*\python.exe")) {
            foreach ($candidate in @(Get-ChildItem -Path $pattern -File -ErrorAction SilentlyContinue |
                    Sort-Object LastWriteTime -Descending)) {
                $result = Test-Python $candidate.FullName
                if ($result) { return $result }
            }
        }
    }
    return $null
}

function Test-MingwRoot([string]$Root) {
    if (-not $Root) { return $null }
    $gcc = Join-Path $Root 'bin\gcc.exe'
    $gxx = Join-Path $Root 'bin\g++.exe'
    $ninja = Join-Path $Root 'bin\ninja.exe'
    $cmake = Join-Path $Root 'bin\cmake.exe'
    if ((Test-Path -LiteralPath $gcc -PathType Leaf) -and
        (Test-Path -LiteralPath $gxx -PathType Leaf) -and
        (Test-Path -LiteralPath $ninja -PathType Leaf) -and
        (Test-Path -LiteralPath $cmake -PathType Leaf)) {
        return [pscustomobject]@{ Root=$Root; Gcc=$gcc; Gxx=$gxx; Ninja=$ninja; CMake=$cmake }
    }
    return $null
}

function Find-Mingw([string]$RequestedRoot) {
    if ($RequestedRoot) { return Test-MingwRoot ([IO.Path]::GetFullPath($RequestedRoot)) }
    $portable = Test-MingwRoot (Join-Path $WinLibsRoot 'mingw64')
    if ($portable) { return $portable }
    $gcc = Get-Command gcc -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    $gxx = Get-Command g++ -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    $ninja = Get-Command ninja -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    $cmake = Get-Command cmake -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($gcc -and $gxx -and $ninja -and $cmake) {
        return [pscustomobject]@{ Root='PATH'; Gcc=$gcc.Source; Gxx=$gxx.Source; Ninja=$ninja.Source; CMake=$cmake.Source }
    }
    if ($env:SF3_SETUP_DISABLE_STANDARD_DISCOVERY -ne '1') {
        $roots = @('C:\msys64\mingw64', 'C:\mingw64')
        if ($env:LOCALAPPDATA) {
            $roots += @(Get-ChildItem -Path "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\BrechtSanders.WinLibs.*" -Directory -ErrorAction SilentlyContinue |
                ForEach-Object { Join-Path $_.FullName 'mingw64' })
        }
        foreach ($root in $roots) {
            $result = Test-MingwRoot $root
            if ($result) { return $result }
        }
    }
    return $null
}

function Install-VerifiedArchive(
    [string]$Key, [string]$Label, [string]$Url, [string]$ExpectedSha256,
    [string]$ArchiveName, [string]$Destination, [string[]]$RequiredFiles) {
    $receipt = Join-Path $Destination '.sf3-artifact-sha256'
    $complete = (Test-Path -LiteralPath $receipt -PathType Leaf)
    if ($complete) {
        $complete = (Get-Content -LiteralPath $receipt -Raw).Trim() -eq $ExpectedSha256
        foreach ($required in $RequiredFiles) {
            if (-not (Test-Path -LiteralPath (Join-Path $Destination $required) -PathType Leaf)) { $complete = $false }
        }
    }
    if ($complete) {
        Write-Host "$Label already verified inside this kit." -ForegroundColor Green
        return
    }
    $downloads = Join-Path $ToolchainDir 'downloads'
    $archive = Join-Path $downloads $ArchiveName
    $partial = "$archive.part"
    $extracting = "$Destination.extracting-$PID"
    New-Item -ItemType Directory -Force $downloads | Out-Null
    if (Test-Path -LiteralPath $partial) { Remove-Item -LiteralPath $partial -Force }
    $testArchive = [Environment]::GetEnvironmentVariable("SF3_SETUP_TEST_${Key}_ARCHIVE")
    $testHash = [Environment]::GetEnvironmentVariable("SF3_SETUP_TEST_${Key}_SHA256")
    Write-Host "Downloading pinned $Label directly; nothing is installed system-wide..." -ForegroundColor Cyan
    if ($env:SF3_SETUP_TEST_MODE -eq '1' -and $testArchive) {
        Copy-Item -LiteralPath $testArchive -Destination $partial
        $ExpectedSha256 = $testHash
    } else {
        $curl = Find-Application 'curl.exe' @("$env:SystemRoot\System32\curl.exe")
        if (-not $curl) { throw 'Windows curl.exe is unavailable.' }
        & $curl --fail --location --retry 3 --connect-timeout 30 --max-time 1800 --output $partial $Url
        if ($LASTEXITCODE -ne 0) { throw "$Label download failed (curl exit $LASTEXITCODE)." }
    }
    $actual = Get-Sha256 $partial
    if (-not $ExpectedSha256 -or $actual -ne $ExpectedSha256.ToLowerInvariant()) {
        Remove-Item -LiteralPath $partial -Force
        throw "$Label archive hash mismatch; the untrusted download was removed. Expected $ExpectedSha256, got $actual."
    }
    Move-Item -LiteralPath $partial -Destination $archive -Force
    if (Test-Path -LiteralPath $extracting) { Remove-Item -LiteralPath $extracting -Recurse -Force }
    New-Item -ItemType Directory -Force $extracting | Out-Null
    $tar = Find-Application 'tar.exe' @("$env:SystemRoot\System32\tar.exe")
    if (-not $tar) { throw 'Windows tar.exe is unavailable.' }
    & $tar -xf $archive -C $extracting
    if ($LASTEXITCODE -ne 0) { throw "$Label extraction failed (tar exit $LASTEXITCODE)." }
    foreach ($required in $RequiredFiles) {
        if (-not (Test-Path -LiteralPath (Join-Path $extracting $required) -PathType Leaf)) {
            throw "Verified $Label archive did not contain $required."
        }
    }
    if (Test-Path -LiteralPath $Destination) { Remove-Item -LiteralPath $Destination -Recurse -Force }
    Move-Item -LiteralPath $extracting -Destination $Destination
    [IO.File]::WriteAllText((Join-Path $Destination '.sf3-artifact-sha256'), $ExpectedSha256, [Text.Encoding]::ASCII)
    Remove-Item -LiteralPath $archive -Force
    Write-Host "$Label is ready inside this kit." -ForegroundColor Green
}

function Install-MissingTools($Python, $Toolchain) {
    if (-not $Toolchain) {
        Install-VerifiedArchive 'WINLIBS' "WinLibs $WinLibsVersion" $WinLibsUrl $WinLibsSha256 `
            $WinLibsArchiveName $WinLibsRoot @('mingw64\bin\gcc.exe','mingw64\bin\g++.exe','mingw64\bin\ninja.exe','mingw64\bin\cmake.exe')
    }
    if (-not $Python) {
        Install-VerifiedArchive 'PYTHON' "Python $PythonVersion" $PythonUrl $PythonSha256 `
            $PythonArchiveName $PythonRoot @('python.exe','python313.dll','python313.zip')
    }
}

function Assert-SafePath([string]$Path, [string]$Label) {
    if ($Path -match '[^\x00-\x7F]') {
        throw "$Label contains non-ASCII characters. Move the kit and disc to a path such as C:\Games\SF3Kit and rerun SETUP.cmd."
    }
}

function Resolve-OwnedCue {
    if ($CuePath) {
        if (-not (Test-Path -LiteralPath $CuePath -PathType Leaf)) { throw "SF3 CUE not found: $CuePath" }
        return (Resolve-Path -LiteralPath $CuePath).Path
    }
    $cues = @(Get-ChildItem -LiteralPath $Kit -File -Filter '*.cue')
    if ($cues.Count -ne 1) {
        throw "Could not uniquely find the Syphon Filter 3 USA CUE beside SETUP.cmd. Found $($cues.Count). Pass -CuePath explicitly."
    }
    return $cues[0].FullName
}

$manifest = Join-Path $Kit 'PACKAGE_MANIFEST.json'
if (Test-Path -LiteralPath $manifest -PathType Leaf) {
    & (Join-Path $Kit 'Test-SF3BootstrapPackage.ps1') `
        -PackageDirectory $Kit -AllowLocalSetupState | Out-Null
}

if (-not $ResolveCueOnly) {
    try { Start-Transcript -LiteralPath $SetupLog -Append | Out-Null; $TranscriptStarted = $true } catch {}
}
trap {
    Write-Host ''
    Write-Host "SETUP FAILED: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host 'Review setup.log and redact personal paths before sharing it.'
    if ($TranscriptStarted) { Stop-Transcript | Out-Null }
    exit 1
}

$resolvedKit = (Resolve-Path -LiteralPath $Kit).Path
Assert-SafePath $resolvedKit 'The extracted kit path'
if ($resolvedKit -match '\s') {
    throw "The extracted kit path contains a space. Move the complete folder to C:\Games\SF3Kit and rerun SETUP.cmd."
}

if ($ResolveCueOnly) {
    $resolvedCue = Resolve-OwnedCue
    Write-Output $resolvedCue
    exit 0
}

Write-Host 'Syphon Filter 3 Recompiled self-contained setup' -ForegroundColor Cyan
Write-Host "A complete log is written to $SetupLog"
$python = Find-Python
$toolchain = Find-Mingw $Mingw
if (-not $python -or -not $toolchain) {
    if ($NoInstallDependencies) {
        throw 'Python 3.10+ or MinGW-w64 GCC/CMake/Ninja is missing. Rerun SETUP.cmd for isolated automatic download.'
    }
    if (-not $InstallDependencies) {
        $reply = Read-Host 'Download missing pinned, SHA-256-verified tools into this kit? [Y/n]'
        if ($reply -and $reply -notmatch '^(?i)y(?:es)?$') { throw 'Setup cancelled.' }
    }
    Install-MissingTools $python $toolchain
    $python = Find-Python
    $toolchain = Find-Mingw $Mingw
}
if (-not $python -or -not $toolchain) { throw 'Setup could not resolve its verified build tools.' }
Write-Host "Python: $($python.File) $($python.Prefix -join ' ')"
Write-Host "CMake:  $($toolchain.CMake)"
Write-Host "GCC:    $($toolchain.Gcc)"
Write-Host "Ninja:  $($toolchain.Ninja)"
Write-Host 'WinGet, Git, pip, and Visual Studio are not required.' -ForegroundColor Green
if ($PreflightOnly) {
    if ($TranscriptStarted) { Stop-Transcript | Out-Null }
    exit 0
}

$resolvedCue = Resolve-OwnedCue
Assert-SafePath $resolvedCue 'The SF3 CUE path'

Write-Host ''
Write-Host 'This project uses PSXRecomp under PolyForm Noncommercial 1.0.0.'
Write-Host 'Generated game code and binaries remain private and must not be redistributed.'
$accept = Read-Host 'Type I ACCEPT to generate and compile your private build'
if ($accept -cne 'I ACCEPT') { throw 'The noncommercial license was not accepted.' }

if (-not $OutputDirectory) { $OutputDirectory = Join-Path $Kit 'SF3-Local-Build' }
$pythonExecutable = $python.File
if ($python.Prefix.Count) {
    $pythonExecutable = (& $python.File @($python.Prefix) -c 'import sys; print(sys.executable)').Trim()
}
$builder = Join-Path $Kit 'Build-SF3.ps1'
& $builder -CuePath $resolvedCue -OutputDirectory $OutputDirectory `
    -AcceptNoncommercialLicense -PackageAlreadyVerified -VideoProfile widescreen-4x `
    -PythonExecutable $pythonExecutable -CMakeExecutable $toolchain.CMake `
    -NinjaExecutable $toolchain.Ninja -CCompiler $toolchain.Gcc `
    -CxxCompiler $toolchain.Gxx -BuildJobs $BuildJobs
if ($LASTEXITCODE -ne 0) { throw "SF3 build failed (exit $LASTEXITCODE)." }

$output = [IO.Path]::GetFullPath($OutputDirectory)
$build = Join-Path $output 'build'
$exe = @(Get-ChildItem -LiteralPath $build -File -Filter '*Recompiled*.exe')
if ($exe.Count -ne 1) { throw 'The completed SF3 executable could not be identified.' }
$game = Join-Path $output 'game-wide.toml'
$saves = Join-Path $output 'user-data'
New-Item -ItemType Directory -Force $saves | Out-Null
$bios = Join-Path $build 'bios\openbios.bin'
$biosArg = if (Test-Path -LiteralPath $bios -PathType Leaf) { " --bios `"$bios`"" } else { '' }
$play = @"
@echo off
cd /d "$build"
start "Syphon Filter 3 Recompiled" "$($exe[0].FullName)" --no-launcher --renderer opengl --game "$game"$biosArg --memcard-dir "$saves"
"@
$play = ($play -replace "`r?`n", "`r`n")
[IO.File]::WriteAllText((Join-Path $Kit 'PLAY_SF3.cmd'), $play, [Text.Encoding]::ASCII)
Write-Host ''
Write-Host 'Setup complete. Double-click PLAY_SF3.cmd for future runs.' -ForegroundColor Green
if ($TranscriptStarted) { Stop-Transcript | Out-Null }
