# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

param(
    [string]
    [Parameter(Mandatory=$True)]
    [ValidateSet("paging", "pipeclean", "volume", "changequeries", "stress", "soak")]
    $Type
)

Import-Module .\TestRunner.psm1 -Force

switch ($Type) {
    "paging" { Invoke-PageVolumeTests }
    "pipeclean" { Invoke-PipecleanTests }
    "volume" { Invoke-VolumeTests }
    "stress" { Invoke-StressTests }
    "soak" { Invoke-SoakTests }
    "changequeries" { Invoke-ChangeQueryTests }
}
