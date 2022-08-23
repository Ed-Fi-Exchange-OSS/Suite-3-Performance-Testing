# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

param([string] $versionPrefix, [int]$buildCounter, $prereleaseName=$null)

function remove-directory($path) {
    if (test-path $path) {
        write-host "Deleting $path"
        remove-item $path -recurse -force -ErrorAction SilentlyContinue | out-null
    }
}

function execute($command) {
    $global:lastexitcode = 0
    & $command

    if ($lastexitcode -ne 0) {
        throw "Error executing command:$command"
    }
}

function ensure-nuget-repository-is-registered {
    $nugetURL = "https://api.nuget.org/v3/index.json"
    $packageSources = Get-PackageSource
    if (@($packageSources).Where{$_.providerName -eq 'NuGet'}.count -eq 0 )
    {
      Register-PackageSource -name nuget.org -ProviderName NuGet -Trusted -Location $nugetURL
      write-output "Registered nuget.org PackageSource"
    }
}

function main($mainBlock) {
    try {
        &$mainBlock
        write-host
        write-host "Packaging Succeeded" -fore GREEN
        exit 0
    } catch [Exception] {
        write-host
        write-host $_.Exception.Message -fore DARKRED
        write-host
        write-host "Packaging Failed" -fore DARKRED
        exit 1
    }
}

main {
    $version = if ($prereleaseName -ne $null) {
        "$versionPrefix-$prereleaseName-{0:D4}" -f $buildCounter
    } else {
        "$versionPrefix.$buildCounter"
    }

    $artifacts = "$(resolve-path .)\artifacts"

    remove-directory $artifacts

    try {

        Push-Location ..

        Copy-Item -Path ".\deploy.env" -Destination ".\.env" -Force | Out-Null

        ensure-nuget-repository-is-registered
        dotnet tool install octopus.dotnet.cli --global | Out-Null

        execute {
            dotnet octo pack `
                --id=Suite-3-Performance-Testing `
                --version=$version `
                --outFolder=$artifacts `
                --include=./eng/deploy.ps1 `
                --include=src/** `
                --include=TestRunner.psm1 `
                --include=run-tests.bat `
                --include=.env `
        }
    }
    finally {
        Pop-Location
    }

}
