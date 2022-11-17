# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

# Run this script as an administrator to install Chocolatey, Pyenv, Python 3.9.4, and Poetry.
# This script should be run should be run once for environments that do not
# already have these prerequisites set up.
####### Tools-Helper.psm1
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
####### Configure-Windows.psm1
function Set-TLS12Support {
    Write-Host "Enabling TLS 1.2"

    if (-not [Net.ServicePointManager]::SecurityProtocol.HasFlag([Net.SecurityProtocolType]::Tls12)) {
        [Net.ServicePointManager]::SecurityProtocol += [Net.SecurityProtocolType]::Tls12
    }
}

function Enable-LongFileNames {
    Write-Host "Enabling long file name support"

    if (Test-Path 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem') {
        Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' -name "LongPathsEnabled" -Value 1 -Verbose -Force
    }
}
###### Install-Applications.psm1
$common_args = @(
    "--execution-timeout=$installTimeout",
    "-y",
    "--ignore-pending-reboot"
)

$installTimeout = 14400 # Set to 0 for infinite

function Install-Choco {
    if (Get-Command "choco.exe" -ErrorAction SilentlyContinue) {
        Write-Output "Chocolatey is already installed. Setting choco command."
    }
    else {
        Write-Output "Installing Chocolatey..."
        $uri = "https://chocolatey.org/install.ps1"
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString($uri))

        &refreshenv
    }
    &choco feature disable --name showDownloadProgress --execution-timeout=$installTimeout
    Test-ExitCode

    return Get-Command "choco.exe" -ErrorAction SilentlyContinue
}
function Install-DotNet {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$True)]
        [string]
        $LogFile
    )
    Start-Transcript -Path $LogFile -Append

    # Need to install a minimal IIS component for next steps. Detailed IIS
    # install will be handled by the Ed-Fi custom installers
    Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole -NoRestart | Out-Null

    #&choco install dotnetcore-sdk @common_args
    #Test-ExitCode

    &choco install dotnetcore-windowshosting @common_args
    Test-ExitCode
    &refreshenv

    &choco install dotnet-6.0-windowshosting @common_args
    Test-ExitCode
    &refreshenv

    #&choco install dotnet-5.0-windowshosting @common_args
    #Test-ExitCode
    #&refreshenv

    &choco install dotnetfx @common_args
    Test-ExitCode
    &refreshenv

    Stop-Transcript
}
###### Run
Set-NetFirewallProfile -Enabled False
$ConfirmPreference="high"
$ErrorActionPreference = "Stop"
Set-TLS12Support
Invoke-RefreshPath
Enable-LongFileNames
Install-Choco
$applicationSetupLog = "$PSScriptRoot/application-setup.log"
Install-DotNet -LogFile $applicationSetupLog
