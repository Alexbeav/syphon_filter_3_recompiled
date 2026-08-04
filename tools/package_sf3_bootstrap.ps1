[CmdletBinding()]
param(
    [string]$Version = 'v0.1.0-alpha',
    [string]$CliPackageDirectory = 'dist\psxrecomp-cli-windows-x86_64'
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$cli = [IO.Path]::GetFullPath((Join-Path $root $CliPackageDirectory))
$dist = Join-Path $root 'dist'
$name = "SF3-Recompiled-Bootstrap-$Version-win64"
$stage = Join-Path $dist $name
$archive = Join-Path $dist "$name.zip"
$archiveHash = "$archive.sha256"
foreach ($path in @($stage, $archive, $archiveHash)) {
    if (Test-Path -LiteralPath $path) {
        throw "Refusing to overwrite existing release artifact: $path"
    }
}
if (-not (Test-Path -LiteralPath (Join-Path $cli 'psxrecomp.exe') -PathType Leaf)) {
    throw "Missing built PSXRecomp CLI package: $cli"
}

New-Item -ItemType Directory -Path $stage | Out-Null
Copy-Item -LiteralPath $cli -Destination (Join-Path $stage 'toolchain') -Recurse
Copy-Item -LiteralPath (Join-Path $root 'tools\New-SF3LocalBuild.ps1') `
    -Destination (Join-Path $stage 'Build-SF3.ps1')
Copy-Item -LiteralPath (Join-Path $root 'tools\Test-SF3BootstrapPackage.ps1') `
    -Destination $stage
Copy-Item -LiteralPath (Join-Path $root 'public\BUILD_SF3.cmd') -Destination $stage
Copy-Item -LiteralPath (Join-Path $root 'public\START_HERE.md') -Destination $stage
$releaseNotes = Join-Path $root "docs\sf3\RELEASE_NOTES_$Version.md"
if (-not (Test-Path -LiteralPath $releaseNotes -PathType Leaf)) {
    throw "Missing release notes for $Version`: $releaseNotes"
}
Copy-Item -LiteralPath $releaseNotes `
    -Destination (Join-Path $stage 'RELEASE_NOTES.md')
Copy-Item -LiteralPath (Join-Path $root 'LICENSE') -Destination (Join-Path $stage 'LICENSE.txt')
Copy-Item -LiteralPath (Join-Path $root 'THIRD_PARTY_ATTRIBUTION.md') -Destination $stage

$sf3 = Join-Path $stage 'sf3'
$redux = Join-Path $sf3 'redux'
New-Item -ItemType Directory -Path $redux -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $root 'lab\sf3\configure_compatibility.py') -Destination $sf3
Copy-Item -LiteralPath (Join-Path $root 'lab\sf3\keybinds.ini') -Destination $sf3
foreach ($profileFile in @('game-controller.toml', 'settings-wide.toml', 'settings-4x.toml')) {
    Copy-Item -LiteralPath (Join-Path $root "lab\sf3\redux\$profileFile") -Destination $redux
}

$files = @(Get-ChildItem -LiteralPath $stage -Recurse -File)
$forbidden = @($files | Where-Object {
    $_.Extension.ToLowerInvariant() -in @('.cue','.iso','.chd','.img','.mcd','.mcr','.sf3pad','.psxstate') -or
    $_.Name -match '(?i)^SCUS[_-]?946\.40$|overlay_captures|psx_freeze|psx_last_run|card[12]'
})
if ($forbidden.Count) { throw "Forbidden retail/private artifact entered package: $($forbidden[0].FullName)" }
$stagePrefix = $stage.TrimEnd('\') + '\'
$privatePath = @($files | Where-Object {
    $relative = $_.FullName.Substring($stagePrefix.Length).Replace('\', '/')
    $relative -match '(?i)(^|/)lab/sf3/(generated|captures|traces|evidence|local)(/|$)' -or
    $relative -match '(?i)(^|/)generated/SCUS[_-]?946\.40' -or
    $relative -match '(?i)(^|/)input/SCUS[_-]?946\.40$'
})
if ($privatePath.Count) {
    throw "A game-derived/private path entered the bootstrap package: $($privatePath[0].FullName)"
}

$rows = [Collections.Generic.List[object]]::new()
foreach ($file in $files | Sort-Object FullName) {
    $relative = $file.FullName.Substring($stagePrefix.Length).Replace('\', '/')
    $rows.Add([ordered]@{
        path = $relative
        size = [int64]$file.Length
        sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $file.FullName).Hash.ToLowerInvariant()
    })
}
$manifest = [ordered]@{
    schema = 'sf3-bootstrap-package-v1'
    version = $Version
    target = 'Syphon Filter 3 USA SCUS-94640'
    license = 'PolyForm-Noncommercial-1.0.0'
    retail_payload_included = $false
    generated_game_code_included = $false
    bundled_bios = 'PCSX-Redux OpenBIOS (MIT)'
    files = $rows
}
[IO.File]::WriteAllText(
    (Join-Path $stage 'PACKAGE_MANIFEST.json'),
    ($manifest | ConvertTo-Json -Depth 5) + [Environment]::NewLine,
    [Text.UTF8Encoding]::new($false))

& (Join-Path $root 'tools\Test-SF3BootstrapPackage.ps1') -PackageDirectory $stage | Out-Null
Compress-Archive -LiteralPath $stage -DestinationPath $archive -CompressionLevel Optimal
$hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $archive).Hash.ToLowerInvariant()
[IO.File]::WriteAllText($archiveHash, "$hash  $name.zip`r`n", [Text.UTF8Encoding]::new($false))

[pscustomobject]@{
    PackageDirectory = $stage
    Archive = $archive
    Sha256 = $hash
    Files = $rows.Count
}
