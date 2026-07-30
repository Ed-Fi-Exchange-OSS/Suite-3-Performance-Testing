#Requires -Version 5
param(
    [Parameter(mandatory=$true)]
    [string]
    $PackageVersion
)

function Invoke-SemanticSort {
    param(
        [Parameter(Mandatory=$true)]
        [string[]]
        $Versions
    )

    $major = @{label="major";expression={[int]$_.Split(".")[0]}}
    $minor = @{label="minor";expression={[int]$_.Split(".")[1]}}
    $patch = @{label="patch";expression={[int]$_.Split(".")[2]}}

    $Versions `
        | Select-Object $major, $minor, $patch `
        | Sort-Object major, minor, patch -Descending `
        | ForEach-Object { "$($_.major).$($_.minor).$($_.patch)" }
}

function Get-NugetPackageVersion {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]
        $PackageName,

        [Parameter(Mandatory=$true)]
        [string]
        $PackageVersion,

        # URL for the release package feed
        [string]
        $ReleaseServiceIndex = "https://pkgs.dev.azure.com/ed-fi-alliance/Ed-Fi-Alliance-OSS/_packaging/EdFi%40Release/nuget/v3/index.json"
    )

    $nugetServicesURL = $ReleaseServiceIndex

    # The first URL just contains metadata for looking up more useful services
    $nugetServices = Invoke-RestMethod $nugetServicesURL

    $packageService = $nugetServices.resources `
                        | Where-Object { $_."@type" -like "PackageBaseAddress*" } `
                        | Select-Object -Property "@id" -ExpandProperty "@id"

    # Pad the package version out to three part semver
    switch ($PackageVersion.split(".").length) {
        1 { $versionSearch = "$PackageVersion.*.*"}
        2 { $versionSearch = "$PackageVersion.*" }
        3 { $versionSearch = $PackageVersion }
        default: { throw "Invalid version string ``$($PackageVersion)``. Should be one, two, or three components from a Semantic Version.".Trim() }
    }
    $lowerId = $PackageName.ToLower()

    # Lookup available packages
    $package = Invoke-RestMethod "$($packageService)$($lowerId)/index.json"

    # Sort by SemVer
    $versions = Invoke-SemanticSort $package.versions

    # Find the first available version that matches the requested version
    $version = $versions | Where-Object { $_ -like $versionSearch } | Select-Object -First 1

    if ($null -eq $version) {
        throw "Version ``$($PackageVersion)`` does not exist yet for ``$($PackageName)``."
    }

    $version
}
Write-Host $PackageVersion
switch -Exact ($PackageVersion)
{
    '7.3' { $StandardVersion = "5.2.0" }
    '7.2' { $StandardVersion = "5.1.0" }
    '7.1' { $StandardVersion = "5.0.0" }
}

$env:WEBAPI_INSTALLLER_VERSION = "$(Get-NugetPackageVersion -PackageName EdFi.Suite3.Installer.WebApi -PackageVersion $PackageVersion)".Trim()
$env:SWAGGER_INSTALLER_VERSION = "$(Get-NugetPackageVersion -PackageName EdFi.Suite3.Installer.SwaggerUI -PackageVersion $PackageVersion)".Trim()
$env:SANDBOXADMIN_INSTALLER_VERSION = "$(Get-NugetPackageVersion -PackageName EdFi.Suite3.Installer.SandboxAdmin -PackageVersion $PackageVersion)".Trim()

$env:SWAGGER_VERSION = "$(Get-NugetPackageVersion -PackageName EdFi.Suite3.Ods.SwaggerUI -PackageVersion $PackageVersion)".Trim()
$env:SANDBOXADMIN_VERSION = "$(Get-NugetPackageVersion -PackageName EdFi.Suite3.Ods.SandboxAdmin -PackageVersion $PackageVersion)".Trim()

if ($null -eq $StandardVersion) {
    $env:DATABASE_INSTALLER_VERSION = "$(Get-NugetPackageVersion -PackageName EdFi.Suite3.RestApi.Databases -PackageVersion $PackageVersion)".Trim()
    $env:DATABASE_INSTALLER = "EdFi.Suite3.RestApi.Databases"
    $env:WEBAPI_VERSION = "$(Get-NugetPackageVersion -PackageName EdFi.Suite3.Ods.WebApi -PackageVersion $PackageVersion)".Trim()
    $env:WEBAPI = "EdFi.Suite3.Ods.WebApi"
}else {
    $env:DATABASE_INSTALLER_VERSION = "$(Get-NugetPackageVersion -PackageName EdFi.Suite3.RestApi.Databases.Standard.$StandardVersion -PackageVersion $PackageVersion)".Trim()
    $env:DATABASE_INSTALLER = "EdFi.Suite3.RestApi.Databases.Standard.$StandardVersion"
    $env:WEBAPI_VERSION = "$(Get-NugetPackageVersion -PackageName EdFi.Suite3.Ods.WebApi.Standard.$StandardVersion -PackageVersion $PackageVersion)".Trim()
    $env:WEBAPI = "EdFi.Suite3.Ods.WebApi.Standard.$StandardVersion"
}
