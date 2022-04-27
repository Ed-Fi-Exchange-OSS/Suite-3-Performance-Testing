# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

$envFile = "$PSScriptRoot/.env"

if (Test-Path $envFile) {
    $config = @{}
    Get-Content $envFile | ForEach-Object {
        $parts = $_ -split "="

        if (2 -eq $parts.Length) {
            # Be sure to ignore commented out lines
            if ("#" -ne $parts[0][0]) {
                $config[$parts[0]] = $parts[1]
            }
        }
    }

   $config | Out-String | Out-Host
}
