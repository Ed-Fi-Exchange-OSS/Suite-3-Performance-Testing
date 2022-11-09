# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.
#Requires -version 5
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Set-ApiUrl {
    Param(
        [Parameter(Mandatory=$True)]
        [hashtable]
        $adminAppConfig,
        [Parameter(Mandatory=$True)]
        [hashtable]
        $swaggerUIConfig,
        [String] $expectedWebApiBaseUri
    )
    if ([string]::IsNullOrEmpty($adminAppConfig.odsApi.apiUrl)) {
        $adminAppConfig.odsApi.apiUrl = $expectedWebApiBaseUri
    }

    if ([string]::IsNullOrEmpty($formattedConfig.swaggerUIConfig.swaggerAppSettings.apiMetadataUrl)) {
        $swaggerUIConfig.swaggerAppSettings.apiMetadataUrl = "$expectedWebApiBaseUri/metadata/"
    }

    if ([string]::IsNullOrEmpty($formattedConfig.swaggerUIConfig.swaggerAppSettings.apiVersionUrl)) {
        $swaggerUIConfig.swaggerAppSettings.apiVersionUrl = $expectedWebApiBaseUri
    }
}
function Test-ApiUrl {
    param (
        [String] $apiUrl
    )
    if ([String]::IsNullOrEmpty($apiUrl)) {
        Write-Error "No API Url configured. Edit configuration.json and run install again."
        Exit -1
    }
}
function Install-SqlServerModule {

    if (-not (Get-Module -ListAvailable -Name SqlServer -ErrorAction SilentlyContinue)) {
        Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force | out-host
        Install-Module SqlServer -Force -AllowClobber -Confirm:$false | out-host
    }

    Import-Module SqlServer
}
function Invoke-SqlCmdOnODS {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$True)]
        [string]
        $FileName,

        [string]
        $DatabaseServer = "localhost",

        # Leave blank to use integrated security
        [string]
        $DatabaseUserName = "",

        [string]
        $DatabasePassword = "",

        [string]
        $DatabaseName = "EdFi_Ods"
    )

    $cmd = if ($DatabaseUserName -ne ""){
        "sqlcmd -S $DatabaseServer -U $DatabaseUserName -P $DatabasePassword -d $DatabaseName -b -i $FileName"
    }
    else{
        "sqlcmd -S $DatabaseServer -E -d $DatabaseName -b -i $FileName"
    }
    Invoke-Expression $cmd
    Test-ExitCode
}

function Invoke-RefreshPath {
    # Some of the installs in this process do not set the immediate path correctly.
    # This function simply reads the global path settings and reloads them. Useful
    # when you can't even get to chocolatey's `refreshenv` command.

    $env:Path=(
        [System.Environment]::GetEnvironmentVariable("Path","Machine"),
        [System.Environment]::GetEnvironmentVariable("Path","User")
    ) -match '.' -join ';'
}

function Test-ExitCode {
    if ($LASTEXITCODE -ne 0) {

        throw @"
The last task failed with exit code $LASTEXITCODE
$(Get-PSCallStack)
"@
    }
}
Export-ModuleMember *
