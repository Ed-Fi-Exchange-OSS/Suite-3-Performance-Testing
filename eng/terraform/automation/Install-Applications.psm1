# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

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

function Install-SQLServer {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$True)]
        [string]
        $LogFile
    )
    Start-Transcript -Path $LogFile -Append

    &choco install sql-server-express @common_args -o -ia `
        "'/IACCEPTSQLSERVERLICENSETERMS /Q /ACTION=install /INSTANCEID=MSSQLSERVER /INSTANCENAME=MSSQLSERVER /TCPENABLED=1 /UPDATEENABLED=FALSE'"
    Test-ExitCode

    &choco install sql-server-management-studio @common_args
    Test-ExitCode
    &refreshenv

    Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force -Confirm:$false
    Install-Module -Name SqlServer -MinimumVersion '21.1.18068' -Scope AllUsers -Force -AllowClobber -Confirm:$false

    Stop-Transcript
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

    &choco install dotnetcore-sdk @common_args
    Test-ExitCode

    &choco install dotnetcore-windowshosting @common_args
    Test-ExitCode
    &refreshenv

    Stop-Transcript
}

function Install-VisualStudioCode {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$True)]
        [string]
        $LogFile
    )
    Start-Transcript -Path $LogFile -Append

    &choco install vscode @common_args
    Test-ExitCode
    &refreshenv

    Remove-Item "C:\Users\*\Desktop\Visual Studio Code.lnk" -Force | Out-Null
    Remove-Item "C:\Users\*\Desktop\Google Chrome.lnk" -Force | Out-Null

    Stop-Transcript
}

function Install-GoogleChrome {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$True)]
        [string]
        $LogFile
    )
    Start-Transcript -Path $LogFile -Append

    &choco install GoogleChrome @common_args --ignore-checksums
    Test-ExitCode
    &refreshenv

    Remove-Item "C:\Users\*\Desktop\Visual Studio Code.lnk" -Force | Out-Null
    Remove-Item "C:\Users\*\Desktop\Google Chrome.lnk" -Force | Out-Null

    Stop-Transcript
}


function Install-PowerBI {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$True)]
        [string]
        $DownloadPath,

        [Parameter(Mandatory=$True)]
        [string]
        $LogFile
    )
    Start-Transcript -Path $LogFile -Append

    $url = "https://download.microsoft.com/download/8/8/0/880BCA75-79DD-466A-927D-1ABF1F5454B0/PBIDesktopSetup_x64.exe"

    $installer = "$DownloadPath/PBIDesktopSetup_x64.exe"
    Invoke-RestMethod -Uri $url -OutFile $installer

    &$installer -quiet -norestart ACCEPT_EULA=1
    Test-ExitCode

    Stop-Transcript
}

function Install-Python {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$True)]
        [string]
        $LogFile
    )

    Start-Transcript -Path $LogFile -Append

    &choco install python3 --version 3.9.6 -y
    Test-ExitCode

    # This package does not add Python and Pip to the path
    $additions = "C:\Python39\;C:\Python39\Scripts"
    $env:PATH = "$env:PATH;$additions"

    $value = [Environment]::GetEnvironmentVariable("PATH", "Machine")
    $value = "$value;$additions"
    [Environment]::SetEnvironmentVariable("PATH", $value, "Machine")

    Stop-Transcript
}

function Install-Poetry {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$True)]
        [string]
        $LogFile
    )

    Start-Transcript -Path $LogFile -Append

    # Poetry's native installation process encounters SSL errors
    # in some environments. `pip install` is a reasonable alternative
    # that has been shown to work in our situation.
    &pip install --user poetry

    # Update local and global PATH variables
    $addition = "$env:APPDATA\Python\Python39\Scripts\"
    $env:PATH="$env:PATH;$addition"

    $value = [Environment]::GetEnvironmentVariable("PATH", "Machine")
    $value = "$value;$addition"
    [Environment]::SetEnvironmentVariable("PATH", $value, "Machine")
    Stop-Transcript
}


Export-ModuleMember *
