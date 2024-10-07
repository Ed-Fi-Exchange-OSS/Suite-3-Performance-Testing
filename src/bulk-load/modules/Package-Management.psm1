# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

#Requires -Version 7


# Azure DevOps hosts the Ed-Fi packages, and it requires TLS 1.2
if (-not [Net.ServicePointManager]::SecurityProtocol.HasFlag([Net.SecurityProtocolType]::Tls12)) {
    [Net.ServicePointManager]::SecurityProtocol += [Net.SecurityProtocolType]::Tls12
}

<#
.SYNOPSIS
    Sorts versions semantically.

.DESCRIPTION
    Semantic Version sorting means that "5.3.111" comes before "5.3.2", despite
    2 being greater than 1.

.EXAMPLE
    Invoke-SemanticSort @("5.1.1", "5.1.11", "5.2.9")

    Output: @("5.2.9", "5.1.11", "5.1.1")
#>
function Invoke-SemanticSort {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]
        $Versions
    )

    $Versions `
    | ForEach-Object { $_ -as [System.Version] } `
    | Sort-Object -Descending `
    | ForEach-Object { "$($_.Major).$($_.Minor).$($_.Build)" }
}

<#
.SYNOPSIS
    Downloads and extracts the latest compatible version of a NuGet package.

.OUTPUTS
    Directory name containing the downloaded files.

.EXAMPLE
    Get-NugetPackage -PackageName "EdFi.Suite3.RestApi.Databases" -PackageVersion "5.3.0"
#>
function Get-NugetPackage {
    [CmdletBinding()]
    [OutputType([String])]
    param(
        # Exact package name
        [Parameter(Mandatory = $true)]
        [string]
        $PackageName,

        # Exact package version
        [Parameter(Mandatory = $true)]
        [string]
        $PackageVersion,

        # URL for the NuGet package feed
        [string]
        $NugetServicesURL = "https://pkgs.dev.azure.com/ed-fi-alliance/Ed-Fi-Alliance-OSS/_packaging/EdFi/nuget/v3/index.json"
    )

    # The first URL just contains metadata for looking up more useful services
    $nugetServices = Invoke-RestMethod $NugetServicesURL

    $packageService = $nugetServices.resources `
    | Where-Object { $_."@type" -like "PackageBaseAddress*" } `
    | Select-Object -Property "@id" -ExpandProperty "@id"

    $lowerId = $PackageName.ToLower()
    $file = "$($lowerId).$($PackageVersion)"
    $zip = "$($file).zip"
    $packagesDir = ".packages"
    New-Item -Path $packagesDir -Force -ItemType Directory | Out-Null

    Push-Location $packagesDir

    if ($null -ne (Get-ChildItem $file -ErrorAction SilentlyContinue)) {
        # Already exists, don't re-download
        Pop-Location
        return "$($packagesDir)/$($file)"
    }

    try {
        Invoke-RestMethod "$($packageService)$($lowerId)/$($PackageVersion)/$($file).nupkg" -OutFile $zip

        Expand-Archive $zip -Force

        Remove-Item $zip
    }
    catch {
        throw $_
    }
    finally {
        Pop-Location
    }

    "$($packagesDir)/$($file)"
}

<#
.SYNOPSIS
    Download and extract the Data Standard sample files.

.OUTPUTS
    String containing the name of the created directory, e.g.
    `.packages/edfi.datastandard.sampledata.5.0.0-dev.1`.

.EXAMPLE
    Get-SampleData -PackageVersion 5.0.0-dev.1
#>
function Get-SampleData {
    param (
        # Exact package version
        [Parameter(Mandatory = $true)]
        [string]
        $PackageVersion
    )

    Get-NugetPackage -PackageName "EdFi.DataStandard.SampleData" -PackageVersion $PackageVersion | Out-String
}

<#
.SYNOPSIS
    Download and extract the Ed-Fi Client Side Bulk Loader.

.OUTPUTS
    String containing the name of the created directory, e.g.
    `.packages/edfi.suite3.bulkloadclient.console`.

.EXAMPLE
    Get-BulkLoadClient -PackageVersion 6.2.0

#>
function Get-BulkLoadClient {
    param (
        # Exact package version
        [Parameter(Mandatory = $true)]
        [string]
        $PackageVersion
    )

    Get-NugetPackage -PackageName "EdFi.Suite3.BulkLoadClient.Console" -PackageVersion $PackageVersion | Out-String
}

<#
.SYNOPSIS
    Download and extract the Southridge Data.

.OUTPUTS
    String containing the name of the created directory, e.g.
    `.packages/southridge`.

.EXAMPLE
    Get-SouthridgeSampleData

#>
function Get-SouthridgeSampleData {

    try {

        if (-not (Get-Module 7Zip4PowerShell -ListAvailable)) {
            Install-Module -Name 7Zip4PowerShell -Force
        }

        $file = "southridge-xml-2024"
        $zip = "$($file).7z"
        $packagesDir = ".packages"

        New-Item -Path $packagesDir -Force -ItemType Directory | Out-Null

        $destination = Join-Path -Path $packagesDir -ChildPath $file

        Push-Location $packagesDir

        if ($null -ne (Get-ChildItem $file -ErrorAction SilentlyContinue)) {
            # Already exists, don't re-download
            Pop-Location
            return $destination
        }

        Write-Host "Downloading Southridge zip file and unzipping into $destination"
        Invoke-WebRequest -Uri "https://odsassets.blob.core.windows.net/public/Northridge/$($zip)" `
            -OutFile $zip | Out-String

        Write-Host "$zip"
        Expand-7Zip $zip $file

        Remove-Item $zip

        return $destination
    }
    catch {
        throw $_
    }
    finally {
        Pop-Location
    }


}

Export-ModuleMember -Function Get-SampleData, Get-NugetPackage, Get-BulkLoadClient, Get-SouthridgeSampleData, Get-SmokeTestTool, Get-ApiSdkDll
