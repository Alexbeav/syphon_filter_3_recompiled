[CmdletBinding()]
param(
    [string]$CuePath,
    [string]$OutputDirectory,
    [ValidateSet('widescreen-4x', 'compatibility-4x')]
    [string]$VideoProfile = 'widescreen-4x',
    [string]$PsxRecompPackageDirectory,
    [switch]$AcceptNoncommercialLicense,
    [switch]$GenerateOnly,
    [switch]$Interactive
)

$ErrorActionPreference = 'Stop'
$expectedExeSha256 = 'b4b32cc92e6b8634762893b637bc9a471442edbeb7569afcfb18eafbe82b9460'
$expectedGameId = 'SCUS-94640'

function Resolve-ExistingFile([string]$Path, [string]$Label) {
    if (-not $Path -or -not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Label does not exist: $Path"
    }
    return (Resolve-Path -LiteralPath $Path).Path
}

function Read-LicenseAcceptance {
    Write-Host ''
    Write-Host 'This project uses PSXRecomp under PolyForm Noncommercial 1.0.0.'
    Write-Host 'Generated game code and binaries remain private and must not be redistributed.'
    $answer = Read-Host 'Type I ACCEPT to continue'
    if ($answer -cne 'I ACCEPT') {
        throw 'The noncommercial license was not accepted.'
    }
}

$packagedAssets = Join-Path $PSScriptRoot 'sf3'
if (Test-Path -LiteralPath (Join-Path $packagedAssets 'configure_compatibility.py')) {
    $assetRoot = $packagedAssets
    if (-not $PsxRecompPackageDirectory) {
        $PsxRecompPackageDirectory = Join-Path $PSScriptRoot 'toolchain'
    }
    $packageVerifier = Join-Path $PSScriptRoot 'Test-SF3BootstrapPackage.ps1'
    if (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'PACKAGE_MANIFEST.json')) {
        & $packageVerifier -PackageDirectory $PSScriptRoot | Out-Null
    }
} else {
    $repoRoot = Split-Path -Parent $PSScriptRoot
    $assetRoot = Join-Path $repoRoot 'lab\sf3'
    if (-not $PsxRecompPackageDirectory) {
        $PsxRecompPackageDirectory = Join-Path $repoRoot 'dist\psxrecomp-cli-windows-x86_64'
    }
}

if ($Interactive) {
    if (-not $AcceptNoncommercialLicense) { Read-LicenseAcceptance }
    $AcceptNoncommercialLicense = $true
    if (-not $CuePath) {
        $CuePath = Read-Host 'Path to your Syphon Filter 3 USA CUE file'
    }
    if (-not $OutputDirectory) {
        $defaultOutput = Join-Path (Get-Location) 'SF3-Local-Build'
        $selectedOutput = Read-Host "Private output directory [$defaultOutput]"
        $OutputDirectory = if ($selectedOutput) { $selectedOutput } else { $defaultOutput }
    }
}

if (-not $AcceptNoncommercialLicense) {
    throw 'Review LICENSE, then pass -AcceptNoncommercialLicense to continue.'
}
if (-not $CuePath) { throw 'CuePath is required.' }
if (-not $OutputDirectory) { throw 'OutputDirectory is required.' }

$cue = Resolve-ExistingFile $CuePath 'Owned SCUS-94640 CUE'
$toolchain = [IO.Path]::GetFullPath($PsxRecompPackageDirectory)
$cli = Resolve-ExistingFile (Join-Path $toolchain 'psxrecomp.exe') 'PSXRecomp CLI'
$gameRecompiler = Resolve-ExistingFile (Join-Path $toolchain 'libexec\psxrecomp-game.exe') 'PSXRecomp game recompiler'
$openBios = Resolve-ExistingFile (Join-Path $toolchain 'framework\bios\openbios.bin') 'Bundled OpenBIOS'
$openBiosNotice = Resolve-ExistingFile (Join-Path $toolchain 'framework\bios\OpenBIOS.LICENSE') 'OpenBIOS license notice'
$configure = Resolve-ExistingFile (Join-Path $assetRoot 'configure_compatibility.py') 'SF3 configuration helper'
$settingsName = if ($VideoProfile -eq 'widescreen-4x') { 'settings-wide.toml' } else { 'settings-4x.toml' }
$settings = Resolve-ExistingFile (Join-Path $assetRoot "redux\$settingsName") 'SF3 runtime settings profile'

$output = [IO.Path]::GetFullPath($OutputDirectory)
if (Test-Path -LiteralPath $output) {
    throw "Refusing to overwrite an existing local project: $output"
}

foreach ($command in @('python', 'cmake', 'ninja')) {
    if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
        throw "Required build tool is not available on PATH: $command"
    }
}

Write-Host 'Generating a private SF3 project from the owned disc...'
& $cli build --disc $cue --bios $openBios --output $output --name 'Syphon Filter 3'
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $output -PathType Container)) {
    throw "PSXRecomp project generation failed with exit code $LASTEXITCODE."
}

$retailExe = Resolve-ExistingFile (Join-Path $output 'input\SCUS_946.40') 'Extracted retail executable'
$actualExeSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $retailExe).Hash.ToLowerInvariant()
if ($actualExeSha256 -cne $expectedExeSha256) {
    throw "Unsupported retail executable. Expected $expectedExeSha256, got $actualExeSha256. The private output was not compiled."
}

$profileConfig = if ($VideoProfile -eq 'widescreen-4x') { 'game-wide.toml' } else { 'game.toml' }
$configureArgs = @($configure, $output)
if ($VideoProfile -eq 'widescreen-4x') {
    $configureArgs += @(
        '--widescreen', '--pgxp', '--precise-culling',
        '--output-config', $profileConfig)
}
& python @configureArgs
if ($LASTEXITCODE -ne 0) { throw 'SF3 profile configuration failed.' }

Push-Location $output
try {
    & $gameRecompiler --config $profileConfig
    if ($LASTEXITCODE -ne 0) { throw 'SF3 regeneration failed.' }
} finally {
    Pop-Location
}

$generatedConfig = Get-Content -LiteralPath (Join-Path $output $profileConfig) -Raw
if ($generatedConfig -notmatch '(?m)^id\s*=\s*"SCUS-94640"\s*$' -or
    $generatedConfig -notmatch '(?m)^overlay_native\s*=\s*false\s*$') {
    throw 'Generated SF3 configuration failed its identity/compatibility contract.'
}
if ($VideoProfile -eq 'widescreen-4x' -and
    ($generatedConfig -notmatch '(?m)^aspect_ratio\s*=\s*"16:9"\s*$' -or
     $generatedConfig -notmatch '(?m)^geometry_precision\s*=\s*true\s*$' -or
     $generatedConfig -notmatch '(?m)^perspective_textures\s*=\s*true\s*$' -or
     $generatedConfig -notmatch '(?m)^precise_culling\s*=\s*true\s*$')) {
    throw 'Generated SF3 configuration is missing the accepted widescreen/PGXP profile.'
}

$metadata = [ordered]@{
    schema = 'sf3-local-build-v1'
    game = 'Syphon Filter 3'
    revision = $expectedGameId
    retail_executable_sha256 = $actualExeSha256
    profile = $VideoProfile
    psxrecomp_cli_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $cli).Hash.ToLowerInvariant()
    openbios_notice_present = [bool](Test-Path -LiteralPath $openBiosNotice)
    owned_paths_recorded = $false
    retail_bytes_redistributable = $false
    generated_game_code_redistributable = $false
}
[IO.File]::WriteAllText(
    (Join-Path $output 'SF3_LOCAL_BUILD_INFO.json'),
    ($metadata | ConvertTo-Json -Depth 3) + [Environment]::NewLine,
    [Text.UTF8Encoding]::new($false))

if ($GenerateOnly) {
    Write-Host "Private generated project ready: $output"
    exit 0
}

$build = Join-Path $output 'build'
$selectedConfig = $profileConfig
Write-Host 'Compiling the private SF3 Release build...'
& cmake -S $output -B $build -G Ninja -DCMAKE_BUILD_TYPE=Release `
    -DPSX_RECOMP_UI=OFF "-DSF3_GAME_CONFIG=$selectedConfig"
if ($LASTEXITCODE -ne 0) { throw 'SF3 CMake configuration failed.' }
& cmake --build $build --config Release --target psx-runtime --parallel
if ($LASTEXITCODE -ne 0) { throw 'SF3 Release build failed.' }

Copy-Item -LiteralPath $settings -Destination (Join-Path $build 'settings.toml') -Force
Copy-Item -LiteralPath (Join-Path $assetRoot 'keybinds.ini') `
    -Destination (Join-Path $build 'keybinds.ini') -Force

$executables = @(Get-ChildItem -LiteralPath $build -File -Filter '*Recompiled*.exe')
if ($executables.Count -ne 1) {
    throw "Expected one SF3 Recompiled executable; found $($executables.Count)."
}

Write-Host ''
Write-Host 'SF3 local build completed successfully.' -ForegroundColor Green
Write-Host "Executable: $($executables[0].FullName)"
Write-Host 'Keep the generated project and executable private; they contain retail-derived code.'
