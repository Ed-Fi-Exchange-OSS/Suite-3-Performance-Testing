# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

$ErrorActionPreference = "Stop"

$resourceGroup = "ods-3-performance"
$applicationDisplayName = "ODS 3 Performance Tests"
$testRunnerServer = "ods-3-perf-test"
$databaseServer = "ods-3-perf-db"
$webServer = "ods-3-perf-web"
$virtualMachines = $testRunnerServer, $databaseServer, $webServer

# Start an Azure management session within the current PowerShell session, assuming the following environment
# variables. Useful when scripting Azure management from TeamCity. This is necessary before other *-AzureRm*
# commands can be executed.
#
# Relies on environment variables:
#   $env:AzureSubscriptionId
#   $env:AzureTenantId
#   $env:AzureADApplicationId
#   $env:AzureADServicePrincipalPassword
function Start-AzureManagementSession {
    Write-Host "================================================================================================"

    $securePassword = $env:AzureADServicePrincipalPassword | ConvertTo-SecureString -AsPlainText -Force
    Write-Host "sec:  '$securePassword' "
    Write-Host "ADA:  '$env:AzureADApplicationId' "
    $credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $env:AzureADApplicationId, $securePassword
    Write-Host "cred:  '$credential' "
    Write-Host "sub:  '$env:AzureSubscriptionId' "
    Write-Host "ten:  '$env:AzureTenantId' "
    Connect-AzureRmAccount -ServicePrincipal -Credential $credential -TenantId $env:AzureTenantId -SubscriptionId $env:AzureSubscriptionId
}

# Given a list of PowerShell job objects, wait for them all to complete,
# and demand that all jobs completed successfully. If any failed, output
# diagnostic information and then exit the process with a failure exit
# code.
function Wait-RequiredJobs($jobs) {
    $failed = $false

    foreach ($job in $jobs) {
        Wait-Job $job | Out-Null

        if ($job.State -ne "Completed") {
            Receive-Job $job
            $failed = $true
        }
    }

    Get-Job | Format-List
    Get-Job | Remove-Job

    if ($failed) {
        exit 1
    }
}

# As parallel background jobs, initiate the stopping and deallocating of several Azure
# VMs, demanding that all jobs complete successfully.
function Stop-AzureVmsInParallel() {
    Write-Host "================================================================================================"
    Write-Host "Stopping and deallocating $($virtualMachines.Length) Azure VMs. This can take several minutes..."
    Write-Host "================================================================================================"

    $jobs = @()
    foreach ($virtualMachine in $virtualMachines) {
        $jobs += Stop-AzureRmVM -ResourceGroupName $resourceGroup -Name $virtualMachine -Force -AsJob |
                 Add-Member -MemberType NoteProperty -Name VmName -Value $virtualMachine -PassThru
    }

    Wait-RequiredJobs $jobs
}

# As parallel background jobs, initiate the starting of several Azure
# VMs, demanding that all jobs complete successfully.
function Start-AzureVmsInParallel() {
    Write-Host "==============================================================================="
    Write-Host "Starting $($virtualMachines.Length) Azure VMs. This can take several minutes..."
    Write-Host "==============================================================================="

    $jobs = @()
    foreach ($virtualMachine in $virtualMachines) {
        $jobs += Start-AzureRmVM -ResourceGroupName $resourceGroup -Name $virtualMachine -AsJob |
                 Add-Member -MemberType NoteProperty -Name VmName -Value $virtualMachine -PassThru
    }

    Wait-RequiredJobs $jobs

    Write-Host "Waiting 30s to allow services to start up."
    Start-Sleep -Seconds 30
}

# Run this one time, in an Azure RM session, to create an Azure Active Directory application and service principal for automating access to performance testing resources.
# The password will use the default expiration of 1 year.
function Register-PerformanceTestingServicePrincipal([string]$subscriptionId, [string]$tenantId) {
    Set-AzureRMContext -SubscriptionId $subscriptionId -TenantId $tenantId

    $applicationUri = "http://ODS-3-Performance-Tests"

    Write-Host "This command will create a new Azure Active Directory Application named '$applicationDisplayName', an associated Azure Active Directory Service Principal for use in automating Azure operations, and grant it rights to the '$resourceGroup' Resource Group"

    $securePassword = Read-Host "Password for new Azure Active Directory Application" -AsSecureString

    # Create an Octopus Deploy Application in Active Directory
    Write-Output "Creating Azure Active Directory application '$applicationDisplayName'..."
    $application = New-AzureRmADApplication -DisplayName $applicationDisplayName -HomePage $applicationUri -IdentifierUris $applicationUri -Password $securePassword
    $application | Format-Table

    Write-Output "Creating Azure Active Directory service principal for ApplicationId '$($application.ApplicationId)'..."
    $servicePrincipal = New-AzureRmADServicePrincipal -ApplicationId $application.ApplicationId
    $servicePrincipal | Format-Table

    Write-Output "Sleeping for 30s to give the service principal a chance to finish creating..."
    Start-Sleep -Seconds 30

    Write-Output "Assigning the Contributor role to the service principal for resource group '$resourceGroup'..."
    New-AzureRmRoleAssignment -RoleDefinitionName Contributor -ServicePrincipalName $application.ApplicationId -ResourceGroupName $resourceGroup

    Write-Output "Connect to Azure using the following Application ID and the given password: $($application.ApplicationId)"
}

# Assigns a new password to the service principal set up by Register-PerformanceTestingServicePrincipal.
# These passwords expire every year.
function Update-PerformanceTestingServicePrincipalPassword([string]$subscriptionId, [string]$tenantId) {
    Set-AzureRMContext -SubscriptionId $subscriptionId -TenantId $tenantId
    $securePassword = Read-Host "New password for new Azure Active Directory Application '$applicationDisplayName'" -AsSecureString
    New-AzureRmADAppCredential -DisplayName $applicationDisplayName -Password $securePassword
}

# This command exposes this computer for remote PowerShell execution over HTTPS.
# Run this directly on an Azure VM, for instance, to allow subsequent automation of that VM.
# Proceed with caution.
#
# Usage:
#   Enable-PowerShellRemotingOverHttps -WhatIf
#       Displays a detailed description of the work to be performed, without performing any work.
#
#   Enable-PowerShellRemotingOverHttps
#       Displays a detailed description of the work to be performed, asking the user to confirm or reject the entire operation.
#       If the user confirms the operation, it proceeds in full.
function Enable-PowerShellRemotingOverHttps() {
    [CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='High')]
    param()

    $verboseDescription = @"

    This command exposes this computer for remote PowerShell execution over HTTPS. It performs the following changes:
        0. Enables PowerShell remoting.
        1. Creates a firewall rule, 'Allow WinRM HTTPS', allowing inbound traffic on the standard WinRM HTTPS port, 5986.
        2. Creates a self-signed certificate for use by a WinRM HTTPS listener.
        3. Creates the WinRM HTTPS listener using that certificate.

    You may wish to perform these or similar steps manually, if you want more control over the effect of running
    this command.

    If running this against an Azure VM, be sure to create a similar inbound Networking rule to allow TCP traffic on port 5986

"@

    if ($PSCmdlet.ShouldProcess($verboseDescription, $verboseDescription + "`r`n" + "Are you sure you want to perform this action?", "Confirm")) {
        # Based on the Azure "EnableRemotePS" Run Command script, but with an extended certificate expiration.
        Enable-PSRemoting -Force
        New-NetFirewallRule -Name "Allow WinRM HTTPS" -DisplayName "WinRM HTTPS" -Enabled True -Profile Any -Action Allow -Direction Inbound -LocalPort 5986 -Protocol TCP
        $thumbprint = (New-SelfSignedCertificate -DnsName $env:COMPUTERNAME -CertStoreLocation Cert:\LocalMachine\My -NotAfter (Get-Date).AddYears(5)).Thumbprint
        $command = "winrm create winrm/config/Listener?Address=*+Transport=HTTPS @{Hostname=""$env:computername""; CertificateThumbprint=""$thumbprint""}"
        cmd.exe /C $command
    }
}

# Collect and encrypt the credentials needed to establish remote PowerShell commands against the performance testing database and web servers,
# allowing them to be used during non-interactive test runs for which a login dialog would not be an option. Run this from the server which will
# generate API requests, and again whenever the test runner, database, or web server remoting accounts undergo password changes. This uses the same encryption
# scheme used by built-in PowerShell remoting commands. The encrypted files can only be decrypted by the same user and on the same machine
# as they are created on. This credentials persistence scheme is the intended use case for the built-in Export-CliXml command, which uses the
# Windows standard Data Protection API.
#
# In order to avoid the PowerShell remoting "second hop" problem, this also places the credentials for the test runner server into a PowerShell
# Session Configuration named SecondHopConfiguration.
function Register-Credentials {
    $registerCredential = {
        param($server)
        $folderPath = (Join-Path $env:LOCALAPPDATA "Suite-3-Performance-Testing")

        if (!(Test-Path -PathType Container $folderPath)) {
            New-Item -ItemType Directory -Force -Path $folderPath | Out-Null
        }

        $path = Join-Path $folderPath "credentials-$server.xml"
        $credential = Get-Credential -Message "Credentials for $server"
        $credential | Export-CliXml -Path $path
        Write-Host "Saved to $path"
        return $credential
    }

    $testRunnerCredential = Invoke-Command -ScriptBlock $registerCredential -ArgumentList $testRunnerServer
    $databaseCredential = Invoke-Command -ScriptBlock $registerCredential -ArgumentList $databaseServer
    $webCredential = Invoke-Command -ScriptBlock $registerCredential -ArgumentList $webServer

    $configuration = Get-PSSessionConfiguration | Where-Object { $_.Name -eq "SecondHopConfiguration" }

    if ($null -eq $configuration) {
        Write-Host "Registering new PowerShell Session Configuration 'SecondHopConfiguration'"
        Register-PSSessionConfiguration -Name SecondHopConfiguration -RunAsCredential $testRunnerCredential -MaximumReceivedDataSizePerCommandMB 1000 -MaximumReceivedObjectSizeMB 1000
    } else {
        Write-Host "Updating PowerShell Session Configuration 'SecondHopConfiguration'"
        Set-PSSessionConfiguration -Name SecondHopConfiguration -RunAsCredential $testRunnerCredential -MaximumReceivedDataSizePerCommandMB 1000 -MaximumReceivedObjectSizeMB 1000
    }
}

# Run tests in the Azure Test Lab, assuming the following environment variables, write test results to an artifacts folder.
#
# Relies on environment variables:
#   $env:AzureTestVmPassword
#   $env:AzureTestVmUsername
function Invoke-TestRunnerFromTeamCity($testType) {
    if (!(Test-Path artifacts)) { New-Item -ItemType Directory -Force -Path artifacts | Out-Null }

    $securePassword = $env:AzureTestVmPassword | ConvertTo-SecureString -AsPlainText -Force
    $credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $env:AzureTestVmUsername, $securePassword

    $sessionOptions = New-PSSessionOption -SkipCACheck -SkipCNCheck -SkipRevocationCheck
    $session = New-PSSession -UseSSL -Port 5986 -ComputerName 'edfi-perf-test.southcentralus.cloudapp.azure.com' -Credential $credential -SessionOption $sessionOptions -ConfigurationName SecondHopConfiguration

    # Set $testRunnerPath locally and remotely.
    $testRunnerPath = Invoke-Command -Session $session {
        $testRunnerPath = Get-Content "C:\Users\edFiAdmin\deployed-test-runner-path.txt" -Raw
        $testRunnerPath
    }

    # Set $testResultsPath locally and remotely.
    $testResultsPath = Invoke-Command -Session $session {
        $testResultsPath = Join-Path $testRunnerPath "TestResults"
        $testResultsPath
    }

    # Set $zipPath locally and remotely.
    $zipPath = Invoke-Command -Session $session {
        $zipPath = Join-Path $testRunnerPath "TestResults.zip"
        $zipPath
    }

    # Set $zipReportPath locally and remotely for Report.
    $zipReportPath = Invoke-Command -Session $session {
        $zipReportPath = Join-Path $testRunnerPath "TestReport.zip"
        $zipReportPath
    }

    Invoke-Command -Session $session -ArgumentList $testType, $testResultsPath {
        param(
            [string] $testType,
            [string] $testResultsPath
            )

        C:\Users\edFiAdmin\run-deployed-tests.bat $testType $testResultsPath

        $latest = Get-ChildItem $testResultsPath | Where-Object { $_.PSIsContainer } | Sort-Object CreationTime -desc | Select-Object -f 1
        $testResultsPath = Join-Path $testResultsPath $latest

        Add-Type -Assembly System.IO.Compression.FileSystem
        [System.IO.File]::Delete($zipPath)
        [System.IO.Compression.ZipFile]::CreateFromDirectory($testResultsPath, $zipPath, [System.IO.Compression.CompressionLevel]::Optimal, $false)

        # Create Zip file for the report
        $reportName = $testType + " Test Analysis.html"
        $reportPath = Join-Path $testRunnerPath $reportName
        $reportPath

        if (Test-Path $reportPath -PathType Leaf) {
            $compress = @{
                Path = $reportPath
                CompressionLevel = "Optimal"
                DestinationPath = $zipReportPath
            }

            [System.IO.File]::Delete($zipReportPath)
            Compress-Archive @compress
        }
    }

    Write-Output "Uploading test results"
    Copy-Item $zipPath -Destination artifacts -FromSession $session -Recurse

    $reportExist = Invoke-Command -Session $session -ArgumentList $zipReportPath {
        if (Test-Path $zipReportPath -PathType Leaf) {
            $true
        }
    }

    if (-not $reportExist){
        exit
    }

    Write-Output "Uploading test reports"
    Copy-Item $zipReportPath -Destination artifacts -FromSession $session -Recurse

}
