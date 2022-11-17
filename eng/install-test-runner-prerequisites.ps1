# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

# Run this script as an administrator to install Chocolatey, Pyenv, Python 3.9.4, and Poetry.
# This script should be run should be run once for environments that do not
# already have these prerequisites set up.

function Install-PowerShellTools {
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    Install-PackageProvider -Name NuGet -Force
    Install-Module CredentialManager -Confirm
    Install-Module SqlServer -Confirm
}


function Update-Path {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") +
                ";" +
                [System.Environment]::GetEnvironmentVariable("Path","User")
}

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
    $pyenvVersion = cmd /c pyenv --version
    if(!$pyenvVersion -or $pyenvVersion -notlike 'pyenv 2.*'){
        choco install pyenv-win -y
        refreshenv
        # refreshenv doesn't appear to be sufficient to recognize user environment variable changes
        Update-Path
    }
}

function Install-Python {
    pyenv install 3.9.4
    pyenv rehash
    pyenv local 3.9.4
}

function Install-Poetry {
    # Ensure pip is on the latest version
    python -m pip install --upgrade pip

    # Update local and global PATH variables
    $addition = "$env:USERPROFILE\.pyenv\pyenv-win\versions\3.9.4\Scripts"
    $env:PATH="$env:PATH;$addition"

    $value = [Environment]::GetEnvironmentVariable("PATH", "Machine")
    $value = "$value;$addition"
    [Environment]::SetEnvironmentVariable("PATH", $value, "Machine")
    refreshenv

    # Install poetry
    # Poetry's native installation process encounters SSL errors
    # in some environments. `pip install` is a reasonable alternative
    # that has been shown to work in our situation.
    pip install --user poetry
}


$ErrorActionPreference = "Stop"
Install-PowerShellTools
Install-Chocolatey
Install-Pyenv
Install-Python
Install-Poetry
# @vimayya are these files still needed now that I have modified them and using them in ./terraform ?
