# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

# Run this script as an administrator to install Chocolatey, Pyenv, Python 3.9.4, and Poetry.
# This script should be run should be run once for environments that do not
# already have these prerequisites set up.

#### PowerShell Tools
function Install-PowerShellTools {
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    Install-PackageProvider -Name NuGet -Force
    Install-Module SqlServer -AllowClobber -Force
}

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

function Install-DotNetHosting {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $True)]
        [string] $LogFile
    )

    Start-Transcript -Path $LogFile -Append

    # Install IIS Web Server Role withcommon features
    Write-Host "Installing IIS Web Server Role and features..."
    $features = @(
        "IIS-WebServerRole",
        "IIS-WebServer",
        "IIS-CommonHttpFeatures",
        "IIS-DefaultDocument",
        "IIS-DirectoryBrowsing",
        "IIS-HttpErrors",
        "IIS-StaticContent",
        "IIS-HttpRedirect",
        "IIS-HealthAndDiagnostics",
        "IIS-HttpLogging",
        "IIS-LoggingLibraries",
        "IIS-RequestMonitor",
        "IIS-Security",
        "IIS-RequestFiltering",
        "IIS-HttpCompressionStatic",
        "IIS-WebServerManagementTools",
        "IIS-ManagementConsole",
        "IIS-BasicAuthentication",
        "IIS-WindowsAuthentication",
        "IIS-ApplicationInit",
        "IIS-NetFxExtensibility45",
        "IIS-ASPNET45"
    )

    foreach ($feature in $features) {
        Write-Host "Installing feature: $feature"
        Enable-WindowsOptionalFeature -Online -FeatureName $feature -All -NoRestart | Out-Null
        if ($?) {
            Write-Host "$feature installed successfully."
        } else {
            Write-Error "Failed to install $feature."
            Stop-Transcript
            exit 1
        }
    }

    Write-Host "IIS installation completed successfully."

    # Install .NET 8.0 Hosting Bundle via Chocolatey
    Write-Host "Installing .NET 8.0 Hosting Bundle..."
    $common_args = @('-y', '--no-progress')
    choco install dotnet-8.0-windowshosting @common_args

    # Check if .NET Hosting Bundle was installed successfully
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Installation of .NET 8.0 Hosting Bundle failed."
        Stop-Transcript
        exit $LASTEXITCODE
    } else {
        Write-Host ".NET 8.0 Hosting Bundle installed successfully."
    }

    # Refresh environment variables
    & refreshenv

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
Install-PowerShellTools

# Remove all existing .NET Core and ASP.NET Core components before installing .NET 8.0
Write-Host "Removing existing .NET components..."
Get-ChildItem -Path "C:\Program Files\dotnet\shared\Microsoft.AspNetCore.App\" -Directory | Remove-Item -Recurse -Force
Get-ChildItem -Path "C:\Program Files\dotnet\shared\Microsoft.NETCore.App\" -Directory | Remove-Item -Recurse -Force

$applicationSetupLog = "$PSScriptRoot/application-setup.log"
Install-DotNetHosting -LogFile $applicationSetupLog
&choco install vcredist140 @common_args

# Restart the computer to complete the installation
Restart-Computer -Force
