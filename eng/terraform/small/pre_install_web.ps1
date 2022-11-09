param (
    # Temporary directory for downloaded components.
    [string]
    $ToolsPath = "$PSScriptRoot/.tools"
)

# IIS Server
# .NET 6 for ODS/API v6.x
# .NET Core 3.1 for ODS/API v5.x
# .NET Framework 4.8 if we also deploy ODS/API v3.4
$ErrorActionPreference = "Stop"

# Disabling the progress report from `Invoke-WebRequest`, which substantially
# slows the download time.
$ProgressPreference = "SilentlyContinue"

New-Item -Path $ToolsPath -ItemType Directory -Force | Out-Null
$parent = (get-item $PSScriptRoot ).parent.FullName
$automationPath = Join-Path $parent "automation"
# Import all needed modules
Import-Module -Name "$automationPath/Configure-Windows.psm1" -Force
Import-Module -Name "$automationPath/Install-Applications.psm1" -Force
Import-Module -Name "$automationPath/Tool-Helpers.psm1" -Force

Set-TLS12Support
Invoke-RefreshPath
Enable-LongFileNames

Install-Choco
$applicationSetupLog = "$PSScriptRoot/application-setup.log"
Install-DotNet -LogFile $applicationSetupLog
