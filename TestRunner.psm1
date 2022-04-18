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

function Copy-ApiLogs {
    param(
        [Parameter(Mandatory=$True)]
        [string]
        $LogFilePath
    )

    $destination = (Join-Path $LogFilePath "OdsLogs")

    # Clear out the existing directory if needed
    Get-ChildItem -Path $destination -Recurse | Remove-Item -Recurse
    if (!(Test-Path $destination)) { New-Item -ItemType Directory -Force -Path $destination | Out-Null}

    # Copy all log files into the temporary OdsLogs irectory
    $logFiles = Get-ChildItem -Path $logFilePath -Recurse -Include *.log* -File
    foreach ($file in $logFiles) {
        $filePath = $file.ToString().Replace($logFilePath, $destination)
        $fileDirectory = Split-Path -parent $filePath
        if (!(Test-Path $fileDirectory)) { New-Item -ItemType Directory -Force -Path $fileDirectory | Out-Null}
        $file | Copy-Item -Destination $filePath
    }
}

function Test-IsLocalhost{
    param(
        [Parameter(Mandatory=$True)]
        [string]
        $server
    )

    # When running on localhost, no need to execute a remote command. Substring
    # check supports use of named instances.
    return $server.substring(0,9) -eq "localhost" -or $server.substring(0,7) -eq "(local)"
}

function Invoke-RemoteCommand($server, [PSCredential] $credential, $argumentList, [ScriptBlock] $scriptBlock) {

    if (Test-IsLocalhost $server) {
        return Invoke-Command -ArgumentList $argumentList -ScriptBlock $scriptBlock
    }

    $thisFolder = $PSScriptRoot
    $commonFunctions = (Get-Command $thisFolder\TestRunner.psm1).ScriptContents

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

function Write-Log {
    param(
        [Parameter(Mandatory=$True)]
        [string]
        $Message,

        [Parameter(Mandatory=$True)]
        [ValidateSet("ERROR", "INFO", "DEBUG")]
        [string]
        $Level
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss,fff"
    $output = "[$timestamp] $Level $Message"

    if ($Level -in ("ERROR", "WARNING")) {
        Write-Error $output
    } else {
        Write-Host $output
    }
}

function Write-ErrorLog {
    param(
        [Parameter(Mandatory=$True)]
        [string]
        $Message
    )

    Write-Log -Message $Message -Level "ERROR"
}

function Write-InfoLog {
    param(
        [Parameter(Mandatory=$True)]
        [string]
        $Message
    )

    Write-Log -Message $Message -Level "INFO"
}

function Write-DebugLog {
    param(
        [Parameter(Mandatory=$True)]
        [string]
        $Message
    )

    if ("DEBUG" -eq $env:PERF_LOG_LEVEL) {
        Write-Log -Message $Message -Level "DEBUG"
    }
}

function Reset-OdsDatabase {
    param(
        [Parameter(Mandatory=$True)]
        [string]
        $BackupFilename,

        [Parameter(Mandatory=$True)]
        [string]
        $DatabaseName
    )
    # This import needs to be here, not at the top, so that this function can be
    # executed on a remote server.
    Import-Module SqlServer

    $command = @"
DECLARE @statement NVARCHAR(1000) = N'ALTER DATABASE ' + QUOTENAME(N'$DatabaseName') + N' SET SINGLE_USER';
EXEC sys.sp_executesql @statement;
"@

    Write-DebugLog $command
    Invoke-SqlCmd -Database "master" -Query $command -QueryTimeout 0

    $command = @"
DECLARE @BackupFilename NVARCHAR(128) = N'$BackupFilename';
DECLARE @DatabaseName NVARCHAR(128) = N'$DatabaseName';
DECLARE @statement NVARCHAR(1000);

DECLARE @MdfPath NVARCHAR(256), @LdfPath NVARCHAR(256);
SELECT @MdfPath = CAST(SERVERPROPERTY('InstanceDefaultDataPath') as NVARCHAR(256)),
        @LdfPath = CAST(SERVERPROPERTY('InstanceDefaultLogPath') as NVARCHAR(256));

-- Table definition below based on documentation at
-- https://docs.microsoft.com/en-us/sql/t-sql/statements/restore-statements-filelistonly-transact-sql
DECLARE @bak_files TABLE (
    LogicalName nvarchar(128),
    PhysicalName nvarchar(260),
    [Type] char(1),
    FileGroupName nvarchar(128),
    Size numeric(20,0),
    MaxSize numeric(20,0),
    FileID bigint,
    CreateLSN numeric(25,0),
    DropLSN numeric(25,0),
    UniqueID uniqueidentifier,
    ReadOnlyLSN numeric(25,0),
    ReadWriteLSN numeric(25,0),
    BackupSizeInBytes bigint,
    SourceBlockSize int,
    FileGroupID int,
    LogGroupGUID uniqueidentifier,
    DifferentialBaseLSN numeric(25,0),
    DifferentialBaseGUID uniqueidentifier,
    IsReadOnly bit,
    IsPresent bit,
    TDEThumbprint varbinary(32),
    SnapshotURL nvarchar(360)
);

SET @statement = N'RESTORE FILELISTONLY FROM DISK = @file';

INSERT INTO @bak_files
EXEC sys.sp_executesql @statement, N'@file NVARCHAR(128)', @file = @BackupFilename;

SET @statement = 'RESTORE DATABASE @db FROM DISK = @disk WITH '
SELECT @statement = @statement + 'MOVE N''' + LogicalName + ''' TO N''' +
    CASE [Type] WHEN 'D' THEN @MdfPath + LogicalName +'.mdf'', '
                WHEN 'L' THEN @LdfPath + LogicalName + '.ldf'', '
    END
FROM @bak_files;

SET @statement = @statement + ' NOUNLOAD, REPLACE, STATS=5';

EXEC sys.sp_executesql @statement, N'@db NVARCHAR(128), @disk NVARCHAR(128)', @db = @DatabaseName, @disk = @BackupFilename;
"@

    Write-DebugLog $command
    Invoke-SqlCmd -Database "master" -Query $command -QueryTimeout 0

    $command = @"
DECLARE @statement NVARCHAR(1000) = N'ALTER DATABASE ' + QUOTENAME(N'$DatabaseName') + N' SET MULTI_USER';
EXEC sys.sp_executesql @statement;
"@

    Write-DebugLog $command
    Invoke-SqlCmd -Database "master" -Query $command -QueryTimeout 0

    $command = @"
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
DEALLOCATE reorganizeOrRebuildCommands_cursor;
"@

    Write-DebugLog $command
    Invoke-SqlCmd -Database $databaseName -Query $command -QueryTimeout 0

    $command = "EXEC sp_updatestats;"
    Write-DebugLog $command
    Invoke-SqlCmd -Database $databaseName -Query $command -QueryTimeout 0
}

# Runs the specified test suite for the specified run time.
function Invoke-TestRunner {
    param (
        $testSuite,
        $clientCount,
        $hatchRate,
        $testType,
        $runTime,
        $Config
    )

    $testResultsPath = Get-RunnerOutputDir -Config $Config

    Start-Transcript -Path $testResultsPath/performance-test.log

    if (($testSuite -eq "volume") -and ($null -eq $runTime)) {
        throw "The -RunTime parameter must be provided when running the 'volume' suite of tests, so that the test run can exit gracefully."
    }

    try {

        Write-InfoLog "Writing to $testResultsPath"

        $databaseServer = Get-ConfigValue -Config $Config -Key "PERF_DB_SERVER"
        $webServer = Get-ConfigValue -Config $Config -Key "PERF_WEB_SERVER"
        $sqlBackupFile = Get-ConfigValue -Config $Config -Key "PERF_SQL_BACKUP_FILE"
        $restoreDatabase = $false
        try {
            $restoreDatabase = [System.Convert]::ToBoolean($(Get-ConfigValue -Config $Config -Key "PERF_DB_RESTORE"))
        } catch {
            raise "Invalid configuration value for PERF_DB_RESTORE, should be a boolean"
        }
        $url = Get-ConfigValue -Config $Config -Key "PERF_API_URL"

        $databaseCredential = Get-CredentialOrDefault $databaseServer
        $webCredential = Get-CredentialOrDefault $webServer

        if ($restoreDatabase) {
            Write-InfoLog "Restoring $databaseName from sqlBackupFile"

            Invoke-RemoteCommand $databaseServer $databaseCredential -ArgumentList @($sqlBackupFile, $databaseName) -ScriptBlock {
                param(
                    [Parameter(Mandatory=$True)]
                    [string]
                    $BackupFilename,

                    [Parameter(Mandatory=$True)]
                    [string]
                    $DatabaseName
                )
                Reset-OdsDatabase -BackupFilename $BackupFilename -DatabaseName $DatabaseName
            }
        } else {
            Write-DebugLog "Skipping Database Restore"
        }

        Write-InfoLog "Verifying ODS API is running"
        $webClient = New-Object System.Net.WebClient
        try {

            # qqq
            [System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }
            $content = $webClient.DownloadString($url)
            Write-Host $content
        }
        finally {
            $webClient.Dispose()
            [System.Net.ServicePointManager]::ServerCertificateValidationCallback = $null
        }

        $serverMetricsBackgroundScript = {
            param(
                $server,

                [PSCredential]
                $credential,

                $getMetricsBlock,

                $expectedPerformanceCounters,

                $TestResultsPath,

                $TestType,

                $TestRunnerModulePath
            )

            $commonFunctions = (Get-Command $TestRunnerModulePath).ScriptContents

            try {
                $csvPath = "$TestResultsPath/$TestType.$server.csv"

                if (Test-IsLocalhost $server) {
                    $actualPerformanceCounters = Compare-Object (typeperf -q) $expectedPerformanceCounters -PassThru -IncludeEqual -ExcludeDifferent
                }
                else {
                    $sessionOptions = New-PSSessionOption -SkipCACheck -SkipCNCheck
                    $psSession = New-PSSession -ComputerName $server -Credential $credential -UseSSL -SessionOption $sessionOptions -ErrorAction Stop

                    # Prepare the remote session with the contents of this file.
                    Invoke-Command -Session $psSession -ArgumentList @($commonFunctions, $Using:configJson) -ScriptBlock {
                        param($commonFunctions, $configJson)
                        Invoke-Expression $commonFunctions
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
                    if (Test-IsLocalhost $server) {
                        $record = Invoke-Command -ScriptBlock $getMetricsBlock
                    } else {
                        $record = Invoke-Command -Session $psSession -ScriptBlock $getMetricsBlock
                    }
                    $record | Select-Object * -ExcludeProperty PSComputerName,RunspaceId,PSShowComputerName | Export-Csv -Path $csvPath -Append -NoTypeInformation
                    Start-Sleep -Seconds $sleepTime
                }
            }
            finally {
                if ($null -ne $psSession) {
                    $psSession | Remove-PSSession
                }
            }
        }

        $backgroundJobs = @{}

        Write-InfoLog "Starting background job to fetch metrics from $databaseServer"

        $parms = @(
            server = $databaseServer
            credential = $databaseCredential
            getMetricsBlock = ${function:Get-ServerMetrics}
            expectedPerformanceCounters = $expectedPerformanceCounters
            TestResultsPath = $testResultsPath
            TestType = $testType
            TestRunnerModulePath = (Split-Path -Path $MyInvocation.MyCommand.Path -Parent)/TestRunner.psm1
        )
        $collectStatsFromDb = Start-Job -ArgumentList $parms -ScriptBlock $serverMetricsBackgroundScript
        $backgroundJobs.Add($databaseServer, $collectStatsFromDb)

        if ($webServer -eq $databaseServer) {
            # If database and web are on the same server, there is no reason to
            # collect the same metrics twice.
            Write-InfoLog "Starting background job to fetch metrics from $webServer"

            $parms.server = $webServer
            $parms.credential = $webCredential
            $collectStatsFromWeb = Start-Job -ArgumentList $parms -ScriptBlock $serverMetricsBackgroundScript
            $backgroundJobs.Add($webServer, $collectStatsFromWeb)
        }

        if($testSuite -eq 'volume') {
            # If the number of clients is too low, locust will quit immediately
            # without running any tests. A safe minimum client count is the count of
            # the total number of volume test classes. This corrects the user's
            # request in the event that the number of volume test classes exceeds
            # the given client count.

            # TODO: change this to use Start-Process instead of "cmd /c"
            $command = & cmd /c "locust -f volume_tests.py --list 2>&1"
            $minimumCount = $command.length-1
            if($clientCount -lt $minimumCount) {
                Write-InfoLog "An inadequate number of clients was provided. Changing client count from $clientCount to $minimumCount"
                $clientCount = $minimumCount
            }
        }

        $runTimeArgument = ""
        if ($null -eq $runTime) {
            Write-InfoLog "Running $testSuite tests with $clientCount clients..."
        } else {
            Write-InfoLog "Running $testSuite tests with $clientCount clients for $runTime..."
            $runTimeArgument = "--run-time $runTime"
        }

        if($testSuite -eq 'pagevolume') {
            $outputDir = Resolve-Path $testResultsPath
            Push-Location .\src\edfi-paging-test
            $poetryProcess = Start-Process "poetry" -PassThru -NoNewWindow -ArgumentList `
                                        "run python edfi_paging_test --connectionLimit $clientCount --output $outputDir" `
                                        -RedirectStandardOutput $outputDir\Summary.txt
            Wait-Process -Id $poetryProcess.Id
            Pop-Location
            Write-InfoLog "Test runner process complete"
        }
        else{
            $locustProcess = Start-Process "locust" -PassThru -NoNewWindow -ArgumentList `
                                    "-f $($testSuite)_tests.py -c $clientCount -r $hatchRate --no-web --csv $testResultsPath\$testType $runTimeArgument --only-summary" `
                                    -RedirectStandardError $testResultsPath\Summary.txt
            Wait-Process -Id $locustProcess.Id
            Write-InfoLog "Test runner process complete"
        }

        foreach ($serverName in $backgroundJobs.Keys) {
            Write-InfoLog "Stopping background job to fetch metrics from $serverName. Output collected from background job:"
            $backgroundJob = $backgroundJobs.Item($serverName)
            try{
                Stop-Job -Job $backgroundJob
                Receive-Job -Job $backgroundJob
                Remove-Job -Job $backgroundJob
            }
            catch{
                Write-InfoLog "Failed to stop job for $($serverName):"
                Write-InfoLog $_.Exception.Message
                $formatstring = "{0} : {1}`n{2}`n" +
                    "    + CategoryInfo          : {3}`n" +
                    "    + FullyQualifiedErrorId : {4}`n"
                $fields = $_.InvocationInfo.MyCommand.Name,
                        $_.ErrorDetails.Message,
                        $_.InvocationInfo.PositionMessage,
                        $_.CategoryInfo.ToString(),
                        $_.FullyQualifiedErrorId
                Write-InfoLog ($formatstring -f $fields)
            }
        }

        Write-InfoLog "Fetching new ODS log file content from $webServer"
        $logFilePath = Get-ConfigValue -Config $config -Key "PERF_API_LOG_FILE_PATH"
        Invoke-RemoteCommand $webServer $webCredential -argumentList @(LogFilePath=$logFilePath) -ScriptBlock {
            param(
                [Parameter(Mandatory=$true)]
                [string]
                $LogFilePath
            )
            Copy-ApiLogs
        }

        # Retreive API log files from the web server
        $logFiles = (Join-Path $logFilePath "OdsLogs")
        if (Test-IsLocalhost $webServer) {
            Copy-Item $logFiles -Destination $testResultsPath -Recurse
        } else {
            $sessionOptions = New-PSSessionOption -SkipCACheck -SkipCNCheck
            $psSession = New-PSSession -ComputerName $webServer -Credential $webCredential -UseSSL -SessionOption $sessionOptions -ErrorAction Stop
            Copy-Item $logFiles -Destination $testResultsPath -FromSession $psSession -Recurse
        }
    }
    finally {
        Stop-Transcript
    }
}

function Get-ConfigValue {
    param (
        [Parameter(Mandatory=$True)]
        [hashtable]
        $Config,

        [Parameter(Mandatory=$True)]
        [string]
        $Key,

        [switch]
        $Optional
    )

    if ($Config.ContainsKey($Key)) {
        return $Config[$Key]
    }

    if (-not $Optional) {
        throw ".Env file is missing the required key $Key"
    }

    return $null
}

function Get-ConfigIgnoreTlsCertificate {
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]
        $config
    )

    $insecure = Get-ConfigValue -Config $config -Key "IGNORE_TLS_CERTIFICATE" -Optional

    # TODO: boolean parsing
    if ($insecure) { return $insecure }

    $false
}

function Get-Configuration {
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

        # Allow the testing process to access the API over HTTP instead of HTTPS ?
        $insecure = Get-ConfigValue -Config $config -Key "IGNORE_TLS_CERTIFICATE" -Optional
        $env:OAUTHLIB_INSECURE_TRANSPORT = if ($insecure) { $insecure } else { 0 }

        $config
    }
    else {
        throw "No configuration found. Please create a .env file. See .env.example for more information."
    }
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
    if (Test-IsLocalhost $server) {
        return $null
    } else {
        # First, attempt to load credentials previously registered with Register-Credentials.
        # If there is no such registered credential, asks the user for credentials interactively.

        $folderPath = (Join-Path $env:LOCALAPPDATA "Suite-3-Performance-Testing")
        $path = Join-Path $folderPath "credentials-$server.xml"

        if (Test-Path $path) {
            return Import-CliXml -Path $path
        } else {
            Write-InfoLog "Requesting credentials for $server interactively"
            return (Get-Credential -Message "Credentials for $server")
        }
    }
}

function Get-OutputDir {
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]
        $Config
    )

    $directory = Get-ConfigValue -Config $Config -Key "PERF_OUTPUT_DIR"

    # Adjust relative path
    $directory.Replace("./", "$PSScriptRoot/")
}

function Get-RunnerOutputDir {
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]
        $Config
    )
    $outputDir = Get-OutputDir -Config $Config
    $runnerDir = Join-Path -Path $outputDir -ChildPath "runner"
    $runnerDir
}

function Initialize-TestRunner {
    $config = Get-Configuration

    $runnerDir = Get-RunnerOutputDir -Config $config
    New-Item -ItemType Directory -Force -Path $runnerDir | Out-Null

    Write-InfoLog "Writing to $runnerDir"
    $config
}

function Invoke-PageVolumeTests {
    $config = Initialize-TestRunner

    Invoke-TestRunner `
        -TestSuite pagevolume `
        -ClientCount 5 `
        -TestType pagevolume `
        -Config $config
}

# Removed in version 2.0 release, will be restored in the future
# function Invoke-VolumeTests {
#     $config = Initialize-TestRunner
#     Invoke-TestRunner `
#         -TestSuite volume `
#         -ClientCount 50 `
#         -HatchRate 1 `
#         -RunTime 30m `
#         -TestType volume `
#         -Config $config
# }

# function Invoke-PipecleanTests {
#     $config = Initialize-TestRunner
#     Invoke-TestRunner `
#         -TestSuite pipeclean `
#         -ClientCount 1 `
#         -HatchRate 1 `
#         -TestType pipeclean `
#         -Config $config
# }

# function Invoke-StressTests {
#     $config = Initialize-TestRunner
#     Invoke-TestRunner `
#         -TestSuite volume `
#         -ClientCount 1000 `
#         -HatchRate 25 `
#         -RunTime 30m `
#         -TestType stress `
#         -Config $config
# }

# function Invoke-SoakTests {
#     $config = Initialize-TestRunner
#     Invoke-TestRunner `
#         -TestSuite volume `
#         -ClientCount 500 `
#         -HatchRate 1 `
#         -RunTime 48h `
#         -TestType soak `
#         -Config $config
# }

# function Invoke-ChangeQueryTests {
#     $config = Initialize-TestRunner

#     Set-ChangeVersionTracker

#     $iteration = 1
#     foreach ($changeQueryBackupFilename in $changeQueryBackupFilenames){
#         # TODO: fix this path to use value from .env config file, instead of being hard-coded
#         $global:testResultsPath = "TestResults\TestResult_$iteration"
#         $iteration = $iteration + 1

#         Initialize-Folder $testResultsPath

#         Invoke-TestRunner `
#             -TestSuite change_query `
#             -ClientCount 1 `
#             -HatchRate 1 `
#             -TestType change_query `
#             -Config $config
#         Duplicate-ChangeVersionTracker
#     }
# }

Export-ModuleMember -Function Invoke-PageVolumeTests
