# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

$ErrorActionPreference = "Stop"

<#
    .SYNOPSIS
        Scans the subdirectories from the script location for Terraform modules, formats, validates,
        and runs linter rules against the modules. Ignores remote modules (in .Terraform).

        Priority of .tflint.hcl configuration files:
            1. In module directory
            2. In script directory (prefer this for default rules to apply across all modules)
            3. In user directory

        REQUIRES terraform AND tflint INSTALLED AND ON THE PATH.
#>

function Validate-TerraformModule {
    param (
        [Parameter()]
        [string]
        $TerraformRootPath = $PSScriptRoot
    )

    $fullPath = (Resolve-Path $TerraformRootPath).ToString().replace('\', '/')

    # Navigate in to module directory to run terraform commands
    pushd $fullPath
    try {
        terraform init
        terraform fmt
        terraform validate

        if ($LastExitCode -ne 0) {
            Write-Error "Error in Terraform code at $TerraformRootPath"
        }
    }
    finally {
        popd
    }

    if (Test-Path (Join-Path $fullPath '.tflint.hcl')) {
        Write-Host "Module contains a .tflint.hcl file, will use this instead of the root file."
        try {
            pushd $fullPath
            tflint --init
            tflint $fullPath
        }
        finally {
            popd
        }
    }
    else {
        tflint --init
        tflint $fullPath
    }

    if ($LastExitCode -ne 0) {
        Write-Error "Validation of Terraform for $TerraformRootPath failed"
    }
}

# Find all directories containing a .tf file that aren't within .terraform\
function Find-TerraformModules {
    param (
        [Parameter()]
        [string]
        $TerraformRootDirectory
    )
    $directories = Get-ChildItem $TerraformRootDirectory -Directory -Recurse | ? { $_.FullName -notmatch '.*\.terraform' }
    $directoriesWithTf = $directories | ? { (Get-ChildItem $_.FullName -File -Filter "*.tf").Count -gt 0 }

    return ($directoriesWithTf | ForEach-Object { $_.FullName })
}

$modulePaths = Find-TerraformModules -TerraformRootDirectory $PSScriptRoot

foreach ($tfModule in $modulePaths) {
    Validate-TerraformModule -TerraformRootPath $tfModule
}
