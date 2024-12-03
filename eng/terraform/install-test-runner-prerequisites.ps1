# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.
function Add-Path {
    param(
      [Parameter(Mandatory, Position=0)]
      [string] $LiteralPath,
      [ValidateSet('User', 'CurrentUser', 'Machine', 'LocalMachine')]
      [string] $Scope
    )
    Set-StrictMode -Version 1; $ErrorActionPreference = 'Stop'
    $isMachineLevel = $Scope -in 'Machine', 'LocalMachine'
    if ($isMachineLevel -and -not $($ErrorActionPreference = 'Continue'; net session 2>$null)) { throw "You must run AS ADMIN to update the machine-level Path environment variable." }
    $regPath = 'registry::' + ('HKEY_CURRENT_USER\Environment', 'HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment')[$isMachineLevel]
    $currDirs = (Get-Item -LiteralPath $regPath).GetValue('Path', '', 'DoNotExpandEnvironmentNames') -split ';' -ne ''
    if ($LiteralPath -in $currDirs) {
      Write-Verbose "Already present in the persistent $(('user', 'machine')[$isMachineLevel])-level Path: $LiteralPath"
      return
    }
    $newValue = ($currDirs + $LiteralPath) -join ';'
    Set-ItemProperty -Type ExpandString -LiteralPath $regPath Path $newValue
    $dummyName = [guid]::NewGuid().ToString()
    [Environment]::SetEnvironmentVariable($dummyName, 'foo', 'User')
    [Environment]::SetEnvironmentVariable($dummyName, [NullString]::value, 'User')
    $env:Path = ($env:Path -replace ';$') + ';' + $LiteralPath
    Write-Verbose "`"$LiteralPath`" successfully appended to the persistent $(('user', 'machine')[$isMachineLevel])-level Path and also the current-process value."
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
function Invoke-RefreshPath {
    # Some of the installs in this process do not set the immediate path correctly.
    # This function simply reads the global path settings and reloads them. Useful
    # when you can't even get to chocolatey's `refreshenv` command.
    $env:Path=(
        [System.Environment]::GetEnvironmentVariable("Path","Machine"),
        [System.Environment]::GetEnvironmentVariable("Path","User")
    ) -match '.' -join ';'
}
function Enable-LongFileNames {
    Write-Host "Enabling long file name support"
    if (Test-Path 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem') {
        Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' -name "LongPathsEnabled" -Value 1 -Verbose -Force
    }
}
function Install-PowerShellTools {
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    Install-PackageProvider -Name NuGet -Force
    Install-Module CredentialManager -AllowClobber -Force
    Install-Module SqlServer -AllowClobber -Force
}
function Update-Path {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") +
                ";" +
                [System.Environment]::GetEnvironmentVariable("Path","User")
}
###### Install-Applications.psm1
$common_args = @(
    "--execution-timeout=$installTimeout",
    "-y",
    "--ignore-pending-reboot"
)
$installTimeout = 14400 # Set to 0 for infinite
function Install-Chocolatey {
    if (! (Get-Command choco.exe -ErrorAction SilentlyContinue )) {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        Invoke-WebRequest https://chocolatey.org/install.ps1 -UseBasicParsing | Invoke-Expression
        $env:ChocolateyInstall = Convert-Path "$((Get-Command choco).path)\..\.."
        Import-Module "$env:ChocolateyInstall\helpers\chocolateyProfile.psm1"
        refreshenv
    }
}
function Install-Pyenv {
    #$pyenvVersion = cmd /c pyenv --version
    if(!(Test-Path "C:\.pyenv\pyenv-win\bin")){
        &choco install pyenv-win @common_args
        refreshenv
        # refreshenv doesn't appear to be sufficient to recognize user environment variable changes
        Update-Path
        Copy-Item "C:\Windows\System32\config\systemprofile\.pyenv" "C:\.pyenv" -Recurse
        Add-Path "C:\.pyenv\pyenv-win\bin" -Scope Machine
        Add-Path "C:\.pyenv\pyenv-win\shims" -Scope Machine
    }
}
function Install-Python {
    pyenv install 3.9.4
    pyenv rehash
    pyenv local 3.9.4
    pyenv global 3.9.4
}
function Install-Poetry {
    # Ensure pip is on the latest version
    python -m pip install --upgrade pip
    # Update local and global PATH variables
    $addition = "C:\.pyenv\pyenv-win\versions\3.9.4\Scripts"
    Add-Path $addition -Scope Machine
    refreshenv
    # Install poetry
    # Poetry's native installation process encounters SSL errors
    # in some environments. `pip install` is a reasonable alternative
    # that has been shown to work in our situation.
    pip install poetry
}
Set-NetFirewallProfile -Enabled False
$ConfirmPreference="high"
$ErrorActionPreference = "Stop"
Set-TLS12Support
Invoke-RefreshPath
Enable-LongFileNames
Install-PowerShellTools
Install-Chocolatey
Install-Pyenv
Invoke-RefreshPath
Install-Python
Install-Poetry
