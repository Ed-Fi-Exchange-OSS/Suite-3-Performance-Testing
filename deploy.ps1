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
"@
}

Write-Host "Updating test runner entry points to latest deployed version."
$pathToThisDeployment = Resolve-Path -Path "."
Write-EntryPointPath $pathToThisDeployment
Write-EntryPointScript $pathToThisDeployment
