[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PackageDirectory,
    [switch]$AllowLocalSetupState
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath $PackageDirectory).Path
$manifestPath = Join-Path $root 'PACKAGE_MANIFEST.json'
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw 'PACKAGE_MANIFEST.json is missing.'
}
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if ($manifest.schema -cne 'sf3-bootstrap-package-v1' -or
    $manifest.retail_payload_included -ne $false -or
    $manifest.generated_game_code_included -ne $false) {
    throw 'Bootstrap package manifest contract is invalid.'
}

$declared = @{}
foreach ($entry in $manifest.files) {
    if ($entry.path -match '(^|/)\.\.(/|$)' -or [IO.Path]::IsPathRooted($entry.path)) {
        throw "Unsafe manifest path: $($entry.path)"
    }
    if ($declared.ContainsKey($entry.path)) { throw "Duplicate manifest path: $($entry.path)" }
    $declared[$entry.path] = $entry
    $path = Join-Path $root ($entry.path -replace '/', [IO.Path]::DirectorySeparatorChar)
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Declared package file is missing: $($entry.path)"
    }
    $file = Get-Item -LiteralPath $path
    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLowerInvariant()
    if ($file.Length -ne [int64]$entry.size -or $hash -cne $entry.sha256) {
        throw "Package file failed hash/size verification: $($entry.path)"
    }
}

$rootPrefix = $root.TrimEnd('\') + '\'
$actual = @(Get-ChildItem -LiteralPath $root -Recurse -File | ForEach-Object {
    if (-not $_.FullName.StartsWith($rootPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Package file escaped root: $($_.FullName)"
    }
    $_.FullName.Substring($rootPrefix.Length).Replace('\', '/')
} | Where-Object { $_ -cne 'PACKAGE_MANIFEST.json' })
if ($AllowLocalSetupState) {
    $actual = @($actual | Where-Object {
        $_ -cne 'setup.log' -and
        $_ -cne 'PLAY_SF3.cmd' -and
        $_ -notmatch '^dependencies/' -and
        $_ -notmatch '^SF3-Local-Build/'
    })
}
$extra = @($actual | Where-Object { -not $declared.ContainsKey($_) })
if ($extra.Count) { throw "Undeclared package file: $($extra[0])" }
if ($actual.Count -ne $declared.Count) {
    throw "Package file-count mismatch: expected $($declared.Count), found $($actual.Count)."
}

[pscustomobject]@{
    PackageDirectory = $root
    Files = $actual.Count
    RetailPayloadIncluded = $false
    GeneratedGameCodeIncluded = $false
    Verified = $true
}
