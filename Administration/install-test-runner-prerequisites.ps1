# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

# Run this script as an administrator to install Chocolatey, Python 2.7.15,
# and to set up the performance test runner's Python "virtual environment".
# This script should be run should be run once for environments that do not
# already have these prerequisites set up.

$ErrorActionPreference = "Stop"

# Install Chocolatey if not already installed
if (! (Get-Command choco.exe -ErrorAction SilentlyContinue )) {
    Set-ExecutionPolicy Bypass -Scope Process -Force
    Invoke-WebRequest https://chocolatey.org/install.ps1 -UseBasicParsing | Invoke-Expression
    $env:ChocolateyInstall = Convert-Path "$((Get-Command choco).path)\..\.."
    Import-Module "$env:ChocolateyInstall\helpers\chocolateyProfile.psm1"
    refreshenv
}

# Install Python 3.6.7
# Note: This places both c:\Python36 and c:\Python36\Scripts into the system PATH variable.
$pyversion = cmd /c python --version '2>&1'
if ($pyversion -ne "Python 3.6.7") {
    choco install python3 -y --version 3.6.7 --params '"/InstallDir:C:\Python36"'
    refreshenv
}

# Ensure pip is on the latest version
python -m pip install --upgrade pip

# Install virtualenv
pip install virtualenv

# "Prepare a Virtual Environment for Python Test Execution"
$virtualdir="c:\virtualenv"
if (!(Test-Path $virtualdir)) {
    New-Item -Path $virtualdir -ItemType Directory -Force | Out-Null
}

Push-Location $virtualdir
virtualenv EDFI_PERFORMANCE
Pop-Location
