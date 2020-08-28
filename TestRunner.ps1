# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

$ErrorActionPreference = "Stop"

$expectedPerformanceCounters = @("\SQLServer:Access Methods\Full Scans/sec", "\SQLServer:SQL Statistics\Batch Requests/sec", "\SQLServer:General Statistics\User Connections", "\ASP.NET\Requests Queued", "\SQLServer:Wait Statistics(*)\Network IO Waits", "\SQLServer:Wait Statistics(*)\Page IO Latch Waits")

function Get-ServerMetrics {
    $result = [pscustomobject] @{
        Time = Get-Date -format "yyyy-MM-dd HH:mm:ss" ;
    }

    $result | Add-Member -Name "CPU Load (%)" -Value (Get-CimInstance win32_processor | Measure-Object -property LoadPercentage -Average).Average -MemberType NoteProperty
    $result | Add-Member -Name "Memory Used (%)" -Value (Get-CimInstance win32_operatingsystem | Select-Object @{Name = "MemoryUsage"; Expression = {"{0:N2}" -f ((($_.TotalVisibleMemorySize - $_.FreePhysicalMemory)*100)/ $_.TotalVisibleMemorySize) }}).MemoryUsage -MemberType NoteProperty

    foreach ($item in (Get-CimInstance Win32_LogicalDisk)) {

        $result | Add-Member -Name "Drive $($item.Name) Free Space (GB)" -Value ([Math]::Round($item.FreeSpace /1GB,2)) -MemberType NoteProperty

    }

    $networkIO = Get-CimInstance Win32_perfformatteddata_tcpip_networkinterface
    $result | Add-Member -MemberType NoteProperty -Name "Bytes Received per second" -Value ($networkIO | Measure-Object -property BytesReceivedPersec -Sum).Sum
    $result | Add-Member -MemberType NoteProperty -Name "Bytes Sent per second" -Value ($networkIO | Measure-Object -property BytesSentPersec -Sum).Sum
    if ($actualPerformanceCounters -contains "\ASP.NET\Requests Queued") {
        $result | Add-Member -MemberType NoteProperty -Name "Requests Queued" -Value (get-counter -Counter "\ASP.NET\Requests Queued").CounterSamples.CookedValue }
    if ($actualPerformanceCounters -contains "\SQLServer:Access Methods\Full Scans/sec") {
        $result | Add-Member -MemberType NoteProperty -Name "Full Scans per second" -Value ([Math]::Round((get-counter -Counter "\SQLServer:Access Methods\Full Scans/sec").CounterSamples.CookedValue,2)) }
    if ($actualPerformanceCounters -contains "\SQLServer:SQL Statistics\Batch Requests/sec") {
        $result | Add-Member -MemberType NoteProperty -Name "Batch Requests per second" -Value ([Math]::Round((get-counter -Counter "\SQLServer:SQL Statistics\Batch Requests/sec").CounterSamples.CookedValue,2)) }
    if ($actualPerformanceCounters -contains "\SQLServer:General Statistics\User Connections") {
        $result | Add-Member -MemberType NoteProperty -Name "User Connections" -Value (get-counter -Counter "\SQLServer:General Statistics\User Connections").CounterSamples.CookedValue }
    if ($actualPerformanceCounters -contains "\SQLServer:Wait Statistics(*)\Network IO Waits") {
        $result | Add-Member -MemberType NoteProperty -Name "Network IO Waits started per second" -Value (get-counter -Counter "\SQLServer:Wait Statistics(waits started per second)\Network IO Waits").CounterSamples.CookedValue }
    if ($actualPerformanceCounters -contains "\SQLServer:Wait Statistics(*)\Page IO Latch Waits") {
        $result | Add-Member -MemberType NoteProperty -Name "Page IO Latch Waits started per second" -Value (get-counter -Counter "\SQLServer:Wait Statistics(waits started per second)\Page IO Latch Waits").CounterSamples.CookedValue }

    $result
}

function Duplicate-OdsLogs {
    $destination = (Join-Path $logFilePath "OdsLogs")
    Get-ChildItem -Path $destination -Recurse | Remove-Item -Recurse
    if (!(Test-Path $destination)) { New-Item -ItemType Directory -Force -Path $destination | Out-Null}
    $logFiles = Get-ChildItem -Path $logFilePath -Recurse -Include *.txt* -File
    foreach ($file in $logFiles) {
        $filePath = $file.ToString().Replace($logFilePath, $destination)
        $fileDirectory = Split-Path -parent $filePath
        if (!(Test-Path $fileDirectory)) { New-Item -ItemType Directory -Force -Path $fileDirectory | Out-Null}
        $file | Copy-Item -Destination $filePath
    }
}

function Invoke-RemoteCommand($server, [PSCredential] $credential, $argumentList, [ScriptBlock] $scriptBlock) {
    if ($server -eq 'localhost') {
        return Invoke-Command -ArgumentList $argumentList -ScriptBlock $scriptBlock
    }

    $thisFolder = $PSScriptRoot
    $commonFunctions = (Get-Command $thisFolder\TestRunner.ps1).ScriptContents

    try {
        $sessionOptions = New-PSSessionOption -SkipCACheck -SkipCNCheck
        $psSession = New-PSSession -ComputerName $server -Credential $credential -UseSSL -SessionOption $sessionOptions -ErrorAction Stop

        # Prepare the remote session with the contents of this file.
        Invoke-Command -Session $psSession -ArgumentList @($commonFunctions, $configJson) -ScriptBlock {
            param($commonFunctions, $configJson)
            Invoke-Expression $commonFunctions
            Set-GlobalsFromConfig $configJson
        }

        return Invoke-Command -Session $psSession -ArgumentList $argumentList -ScriptBlock $scriptBlock
    }
    finally {
        if ($null -ne $psSession) {
            $psSession | Remove-PSSession
        }
    }
}

function Log($message) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss,fff"
    $output = "[$timestamp] $message"
    Write-Host $output
    $output | Out-File -Encoding UTF8 $testResultsPath\PerformanceTesterLog.txt -Append
}

function Reset-OdsDatabase($backupFilename) {
    Import-Module SQLPS

    $logicalName = "EdFi_Ods_Populated_Template"
    if ($backupFilename -Match "Minimal") {
        $logicalName = "EdFi_Ods_Minimal_Template"
    }

    Invoke-SqlCmd -Database "master" `
                  -Query "ALTER DATABASE [$databaseName] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;

                          RESTORE DATABASE [$databaseName] FROM DISK = '$sqlBackupPath\$backupFilename'
                            WITH
                                MOVE '$($logicalName)' TO '$sqlDataPath\$($databaseName).mdf',
                                MOVE '$($logicalName)_log' TO '$sqlDataPath\$($databaseName)_log.ldf',
                                REPLACE;

                          ALTER DATABASE [$databaseName] SET MULTI_USER;" -QueryTimeout 0

    Invoke-SqlCmd -Database $databaseName -Query "
        DECLARE @ReorganizeOrRebuildCommand NVARCHAR(MAX);
        DECLARE reorganizeOrRebuildCommands_cursor CURSOR
            FOR
                SELECT
                    CASE
                        WHEN pst.avg_fragmentation_in_percent > 30 THEN
                            'ALTER INDEX ['+idx.Name+'] ON ['+DB_NAME()+'].['+SCHEMA_NAME (tbl.schema_id)+'].['+tbl.name+'] REBUILD WITH (FILLFACTOR = 90, SORT_IN_TEMPDB = ON, STATISTICS_NORECOMPUTE = OFF);'
                        WHEN pst.avg_fragmentation_in_percent > 5 AND pst.avg_fragmentation_in_percent <= 30 THEN
                            'ALTER INDEX ['+idx.Name+'] ON ['+DB_NAME()+'].['+SCHEMA_NAME (tbl.schema_id)+'].['+tbl.name+'] REORGANIZE;'
                        ELSE
                            NULL
                    END
                FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL , 'SAMPLED') as pst
                INNER JOIN sys.tables as tbl ON pst.object_id = tbl.object_id
                INNER JOIN sys.indexes idx ON pst.object_id = idx.object_id AND pst.index_id = idx.index_id
                WHERE pst.index_id != 0
                AND pst.alloc_unit_type_desc IN ( N'IN_ROW_DATA', N'ROW_OVERFLOW_DATA')
                AND pst.avg_fragmentation_in_percent >= 15;

        OPEN reorganizeOrRebuildCommands_cursor;
        FETCH NEXT FROM reorganizeOrRebuildCommands_cursor INTO @ReorganizeOrRebuildCommand;
        WHILE @@fetch_status = 0
            BEGIN
                IF @ReorganizeOrRebuildCommand IS NOT NULL
                BEGIN
                    PRINT @ReorganizeOrRebuildCommand
                    EXEC (@ReorganizeOrRebuildCommand);
                END
                FETCH NEXT FROM reorganizeOrRebuildCommands_cursor INTO @ReorganizeOrRebuildCommand;
            END;
        CLOSE reorganizeOrRebuildCommands_cursor;
        DEALLOCATE reorganizeOrRebuildCommands_cursor;" -QueryTimeout 0

    Invoke-SqlCmd -Database $databaseName -Query "EXEC sp_updatestats;" -QueryTimeout 0
}

# Runs the specified test suite for the specified run time.
function Invoke-TestRunner($testSuite, $clientCount, $hatchRate, $testType, $backupFilename, $runTime) {
    Log "Writing to $testResultsPath"

    if (($testSuite -eq "volume") -and ($null -eq $runTime)) {
        throw "The -RunTime parameter must be provided when running the 'volume' suite of tests, so that the test run can exit gracefully."
    }

    $databaseCredential = Get-CredentialOrDefault $databaseServer
    $webCredential = Get-CredentialOrDefault $webServer

    if($restoreDatabase) {
        Log "Resetting ODS database from backup, and resetting indexes"
        Log "Restoring $databaseName from $sqlBackupPath\$backupFilename"
        Invoke-RemoteCommand $databaseServer $databaseCredential -ArgumentList @($backupFilename) -ScriptBlock { param($backupFilename) Reset-OdsDatabase $backupFilename }
    } else {
        Log "Skipping Database Restore"
    }

    Log "Verifying ODS API is running"
    $url = ($configJson | ConvertFrom-Json).host
    $webClient = New-Object System.Net.WebClient
    try {
        [System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }
        $content = $webClient.DownloadString($url)
        Write-Host $content
    }
    finally {
        $webClient.Dispose()
        [System.Net.ServicePointManager]::ServerCertificateValidationCallback = $null
    }

    $thisFolder = $PSScriptRoot

    $serverMetricsBackgroundScript = {
        param($server, [PSCredential] $credential, $getMetricsBlock, $expectedPerformanceCounters)

        $commonFunctions = (Get-Command $Using:thisFolder\TestRunner.ps1).ScriptContents

        try {
            $csvPath = "$Using:thisFolder\$Using:testResultsPath\$Using:testType.$server.csv"

            if ($server -eq 'localhost') {
                $actualPerformanceCounters = Compare-Object (typeperf -q) $expectedPerformanceCounters -PassThru -IncludeEqual -ExcludeDifferent
            }
            else {
                $sessionOptions = New-PSSessionOption -SkipCACheck -SkipCNCheck
                $psSession = New-PSSession -ComputerName $server -Credential $credential -UseSSL -SessionOption $sessionOptions -ErrorAction Stop

                # Prepare the remote session with the contents of this file.
                Invoke-Command -Session $psSession -ArgumentList @($commonFunctions, $Using:configJson) -ScriptBlock {
                    param($commonFunctions, $configJson)
                    Invoke-Expression $commonFunctions
                    Set-GlobalsFromConfig $configJson
                }

                Invoke-Command -Session $psSession -ScriptBlock {
                    $actualPerformanceCounters = Compare-Object (typeperf -q) $expectedPerformanceCounters -PassThru -IncludeEqual -ExcludeDifferent
                }
            }
            $getMetricsBlock = [scriptblock]::Create($getMetricsBlock)

            if ($Using:testType -eq 'soak'){
                $sleepTime = 25
            } else {
                $sleepTime = 5
            }

            while ($true) {
                if ($server -eq 'localhost') {
                    $record = Invoke-Command -ScriptBlock $getMetricsBlock
                } else {
                    $record = Invoke-Command -Session $psSession -ScriptBlock $getMetricsBlock
                }
                $record | Select-Object * -ExcludeProperty PSComputerName,RunspaceId,PSShowComputerName | Export-Csv -Path $csvPath -Append -NoTypeInformation
                Start-Sleep -Seconds $sleepTime
            }
        }
        finally {
            if ($psSession -ne $null) {
                $psSession | Remove-PSSession
            }
        }
    }

    $backgroundJobs = @{}

    Log "Starting background job to fetch metrics from $databaseServer"
    $collectStatsFromDb = Start-Job -ArgumentList @($databaseServer, $databaseCredential, ${function:Get-ServerMetrics}, $expectedPerformanceCounters) -ScriptBlock $serverMetricsBackgroundScript
    $backgroundJobs.Add($databaseServer, $collectStatsFromDb)

    if ($webServer -ne 'localhost') {
        Log "Starting background job to fetch metrics from $webServer"
        $collectStatsFromWeb = Start-Job -ArgumentList @($webServer, $webCredential, ${function:Get-ServerMetrics}, $expectedPerformanceCounters) -ScriptBlock $serverMetricsBackgroundScript
        $backgroundJobs.Add($webServer, $collectStatsFromWeb)
    }

    if($testSuite -eq 'volume') {
        # If the number of clients is too low, locust will quit immediately without running any tests. A safe minimum client count is the count of the total number of
        # volume test classes. This corrects the user's request in the event that the number of volume test classes exceeds the given client count.
        $command = & cmd /c "locust -f volume_tests.py --list 2>&1"
        $minimumCount = $command.length-1
        if($clientCount -lt $minimumCount) {
            Log "An inadequate number of clients was provided. Changing client count from $clientCount to $minimumCount"
            $clientCount = $minimumCount
        }
    }

    $runTimeArgument = ""
    if ($null -eq $runTime) {
        Log "Running $testSuite tests with $clientCount clients..."
    } else {
        Log "Running $testSuite tests with $clientCount clients for $runTime..."
        $runTimeArgument = "--run-time $runTime"
    }

    $locustProcess = Start-Process "locust" -PassThru -NoNewWindow -ArgumentList `
                                   "-f $($testSuite)_tests.py -c $clientCount -r $hatchRate --no-web --csv $testResultsPath\$testType $runTimeArgument --only-summary" `
                                   -RedirectStandardError $testResultsPath\Summary.txt
    Wait-Process -Id $locustProcess.Id
    Log "Test runner process complete"

    foreach ($serverName in $backgroundJobs.Keys) {
        Log "Stopping background job to fetch metrics from $serverName. Output collected from background job:"
        $backgroundJob = $backgroundJobs.Item($serverName)
        try{
            Stop-Job -Job $backgroundJob
            Receive-Job -Job $backgroundJob
            Remove-Job -Job $backgroundJob
        }
        catch{
            Log "Failed to stop job for $($serverName):"
            Log $_.Exception.Message
            $formatstring = "{0} : {1}`n{2}`n" +
                "    + CategoryInfo          : {3}`n" +
                "    + FullyQualifiedErrorId : {4}`n"
            $fields = $_.InvocationInfo.MyCommand.Name,
                    $_.ErrorDetails.Message,
                    $_.InvocationInfo.PositionMessage,
                    $_.CategoryInfo.ToString(),
                    $_.FullyQualifiedErrorId
            Log ($formatstring -f $fields)
        }
    }

    Log "Fetching new ODS log file content from $webServer"
    Invoke-RemoteCommand $webServer $webCredential -ScriptBlock { Duplicate-OdsLogs }

    $logFiles = (Join-Path $logFilePath "OdsLogs")
    if ($webServer -eq 'localhost') {
        Copy-Item $logFiles -Destination $testResultsPath -Recurse
    } else {
        $sessionOptions = New-PSSessionOption -SkipCACheck -SkipCNCheck
        $psSession = New-PSSession -ComputerName $webServer -Credential $webCredential -UseSSL -SessionOption $sessionOptions -ErrorAction Stop
        Copy-Item $logFiles -Destination $testResultsPath -FromSession $psSession -Recurse
    }
}

function Set-GlobalsFromConfig($configJson) {
    $configValues = $configJson | ConvertFrom-Json
    $global:databaseServer = $configValues.database_server
    $global:webServer = $configValues.web_server
    $global:logFilePath = $configValues.log_file_path
    $global:sqlBackupPath = $configValues.sql_backup_path
    $global:sqlDataPath = $configValues.sql_data_path
    $global:databaseName = $configValues.database_name
    $global:backupFilename = $configValues.backup_filename
    $global:changeQueryBackupFilenames = $configValues.change_query_backup_filenames
    $global:restoreDatabase = [Bool]::Parse($configValues.restore_database)
}

function Read-TestRunnerConfig {
    $global:configJson = Get-Content 'locust-config.json' | Out-String
}

function Set-ChangeVersionTracker {
    $changeVersion = @{
        newest_change_version = 0
    }
    $changeVersion | ConvertTo-Json | Set-Content -Path 'change_version_tracker.json'
}

function Duplicate-ChangeVersionTracker {
    Copy-Item 'change_version_tracker.json' -Destination $testResultsPath
}

function Get-CredentialOrDefault($server) {
    if ($server -eq 'localhost') {
        return $null
    } else {
        # First, attempt to load credentials previously registered with Register-Credentials.
        # If there is no such registered credential, asks the user for credentials interactively.

        $folderPath = (Join-Path $env:LOCALAPPDATA "Ed-Fi-X-Performance")
        $path = Join-Path $folderPath "credentials-$server.xml"

        if (Test-Path $path) {
            return Import-CliXml -Path $path
        } else {
            Log "Requesting credentials for $server interactively"
            return (Get-Credential -Message "Credentials for $server")
        }
    }
}

function Initialize-Folder($path) {
    Get-ChildItem -Path $path -Recurse | Remove-Item -Recurse
    if (!(Test-Path $path)) {
        New-Item -ItemType Directory -Force -Path $path | Out-Null
    }
}

function Initialize-TestRunner {
    Read-TestRunnerConfig
    Set-GlobalsFromConfig $configJson

    # Default to a single TestResults folder. This may be overridden,
    # such as for Change Query tests, which write to multiple subfolders
    # underneath TestResults.
    $global:testResultsPath = "TestResults"
    Initialize-Folder TestResults
}

function Invoke-VolumeTests {
    Initialize-TestRunner
    Invoke-TestRunner `
        -TestSuite volume `
        -ClientCount 50 `
        -HatchRate 1 `
        -RunTime 30m `
        -TestType volume `
        -BackupFilename $backupFilename
}

function Invoke-PipecleanTests {
    Initialize-TestRunner
    Invoke-TestRunner `
        -TestSuite pipeclean `
        -ClientCount 1 `
        -HatchRate 1 `
        -TestType pipeclean `
        -BackupFilename $backupFilename
}

function Invoke-StressTests {
    Initialize-TestRunner
    Invoke-TestRunner `
        -TestSuite volume `
        -ClientCount 1000 `
        -HatchRate 25 `
        -RunTime 30m `
        -TestType stress `
        -BackupFilename $backupFilename
}

function Invoke-SoakTests {
    Initialize-TestRunner
    Invoke-TestRunner `
        -TestSuite volume `
        -ClientCount 500 `
        -HatchRate 1 `
        -RunTime 48h `
        -TestType soak `
        -BackupFilename $backupFilename
}

function Invoke-ChangeQueryTests {
    Initialize-TestRunner

    Set-ChangeVersionTracker

    $iteration = 1
    foreach ($changeQueryBackupFilename in $changeQueryBackupFilenames) {
        $global:testResultsPath = "TestResults\TestResult_$iteration"
        $iteration = $iteration + 1

        Initialize-Folder $testResultsPath

        Invoke-TestRunner `
            -TestSuite change_query `
            -ClientCount 1 `
            -HatchRate 1 `
            -TestType change_query `
            -BackupFilename $changeQueryBackupFilename
        Duplicate-ChangeVersionTracker
    }
}
