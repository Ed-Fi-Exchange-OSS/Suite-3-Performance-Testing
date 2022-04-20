# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

# Run this script as an administrator to install Chocolatey, Pyenv, Python 3.9.4, and Poetry.
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
#$pyversion = cmd /c python --version '2>&1'
#if ($pyversion -ne "Python 3.6.7") {
 #   choco install python3 -y --version 3.6.7 --params '"/InstallDir:C:\Python36"'
  #  refreshenv
#}

#Install
$pyenvVersion = cmd /c pyenv --version
if($pyenvVersion -notlike 'pyenv 2.*'){
    choco install pyenv-win -y
    refreshenv
}

#install python
pyenv install 3.9.4
pyenv rehash
pyenv local 3.9.4

# Ensure pip is on the latest version
python -m pip install --upgrade pip

# Install poetry
# Poetry's native installation process encounters SSL errors
# in some environments. `pip install` is a reasonable alternative
# that has been shown to work in our situation.
pip install --user poetry
# Update local and global PATH variables
$addition = "$env:APPDATA\Python\Python39\Scripts\"
$env:PATH="$env:PATH;$addition"

$value = [Environment]::GetEnvironmentVariable("PATH", "Machine")
$value = "$value;$addition"
[Environment]::SetEnvironmentVariable("PATH", $value, "Machine")
refreshenv

Push-Location .\src\edfi-paging-test
poetry install
Pop-Location
