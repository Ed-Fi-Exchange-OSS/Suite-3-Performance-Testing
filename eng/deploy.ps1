# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

function Write-EntryPointFile($filename, $content) {
    $path = Join-Path "C:\Users\edFiAdmin\" $filename
    Write-Host "Generating $path"
    [System.IO.File]::WriteAllText($path, $content, [System.Text.Encoding]::ASCII)
}

function Write-EntryPointPath($pathToThisDeployment) {
    Write-EntryPointFile "deployed-test-runner-path.txt" $pathToThisDeployment
}

function Write-EntryPointScript($pathToThisDeployment, $testType) {
    Write-EntryPointFile "run-deployed-tests.bat" @"
@echo off

REM Move to the latest deployed version of the test suite.
cd "$pathToThisDeployment"

call run-tests.bat %*

call run-report.bat %*
"@
}

Write-Host "Updating test runner entry points to latest deployed version."
$pathToThisDeployment = Resolve-Path -Path "."
Write-EntryPointPath $pathToThisDeployment
Write-EntryPointScript $pathToThisDeployment
