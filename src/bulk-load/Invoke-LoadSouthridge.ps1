# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.


param(
    [string]
    $Key = "minimalKey",

    [string]
    $Secret = "minimalSecret",

    # 8080 is the default docker port. 5198 is the default when running F5 on
    # DMS. 8001 for the ODS/API running from the Docker Compose files in this
    # performance testing repository.
    [string]
    $BaseUrl = "http://localhost:8080",

    # When false (default), only loads descriptors
    [switch]
    $FullDataSet,

    # Use with the DMS, do not use with the ODS/API
    [switch]
    $LoadSchoolYear
)

#Requires -Version 7
$ErrorActionPreference = "Stop"

Import-Module ./modules/Package-Management.psm1 -Force
Import-Module ./modules/Get-XSD.psm1 -Force
Import-Module ./modules/BulkLoad.psm1 -Force

$paths = Initialize-ToolsAndDirectories
$paths.SampleDataDirectory = Import-SampleData -Template "Southridge"

$parameters = @{
    BaseUrl = $BaseUrl
    Key     = $Key
    Secret  = $Secret
    Paths   = $paths
    LoadSchoolYear = $LoadSchoolYear
}

$stopwatch =  [system.diagnostics.stopwatch]::StartNew()
Write-Bootstrap @parameters

if ($FullDataSet) {
    $parameters = @{
        BaseUrl             = $BaseUrl
        Key                 = $Key
        Secret              = $Secret
        SampleDataDirectory = $Paths.SampleDataDirectory
        Paths               = $Paths
    }
    Write-XmlFiles @parameters
}

$stopwatch.Stop()
$stopwatch.Elapsed | Out-Host
