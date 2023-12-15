# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

$ErrorActionPreference = "Stop"


function Get-ServerMetrics {
    $result = [pscustomobject] @{
        Time = Get-Date -format "yyyy-MM-dd HH:mm:ss" ;
    }

    $result | Add-Member -Name "CPU Load (%)" -Value (Get-CimInstance win32_processor | Measure-Object -property LoadPercentage -Average).Average -MemberType NoteProperty
    $result | Add-Member -Name "Memory Used (%)" -Value (Get-CimInstance win32_operatingsystem | Select-Object @{Name = "MemoryUsage"; Expression = {"{0:N2}" -f ((($_.TotalVisibleMemorySize - $_.FreePhysicalMemory)*100)/ $_.TotalVisibleMemorySize) }}).MemoryUsage -MemberType NoteProperty

    foreach ($item in (Get-CimInstance Win32_LogicalDisk)) {

        $result | Add-Member -Name "Drive $($item.Name) Free Space (GB)" -Value ([Math]::Round($item.FreeSpace /1GB,2)) -MemberType NoteProperty

    }

    $expectedPerformanceCounters = @("\SQLServer:Access Methods\Full Scans/sec", "\SQLServer:SQL Statistics\Batch Requests/sec", "\SQLServer:General Statistics\User Connections", "\ASP.NET\Requests Queued", "\SQLServer:Wait Statistics(*)\Network IO Waits", "\SQLServer:Wait Statistics(*)\Page IO Latch Waits")
    $actualPerformanceCounters = Compare-Object (typeperf -q) $expectedPerformanceCounters -PassThru -IncludeEqual -ExcludeDifferent


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

function Test-IsLocalhost {
    param(
        [Parameter(Mandatory=$True)]
        [string]
        $server
    )

    # When running on localhost, no need to execute a remote command. Substring
    # check supports use of named instances.
    return ($server.IndexOf("localhost") -gt -1) `
        -or ($server.IndexOf("(local)") -gt -1) `
        -or ($server.IndexOf(".") -eq 0) `
        -or ($server.IndexOf($env:ComputerName) -gt -1)
}

function Get-DatabaseServerName {
    # For handling named instances
    param(
        [Parameter(Mandatory=$True)]
        [string]
        $server
    )

    if ($server.IndexOf("\") -gt -1) {
        return ($server -split "\")[0]
    }

    return $server
}

function Invoke-RemoteCommand {
    param (
        $server, [PSCredential] $credential, $argumentList, [ScriptBlock] $scriptBlock
    )

    if (Test-IsLocalhost $server) {
        throw "Should not invoke remote command on localhost"
    }

    try {
        $sessionOptions = New-PSSessionOption -SkipCACheck -SkipCNCheck
        $psSession = New-PSSession -ComputerName $server -Credential $credential -UseSSL -SessionOption $sessionOptions -ErrorAction Stop

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
    $output = "$timestamp - $Level - TestRunner - $Message"

    $color = (get-host).ui.rawui.ForegroundColor
    switch ($Level) {
        "ERROR" { $color = "Red" }
        "DEBUG" { $color = "Yellow" }
    }

    Write-Host $output -ForegroundColor $color
}

function Write-InfoLog {
    param(
        [Parameter(Mandatory=$True)]
        [string]
        $Message
    )

    Write-Log -Message $Message -Level "INFO"
}

function Write-ErrorLog {
    param(
        [Parameter(Mandatory=$True)]
        [string]
        $Message
    )

    Write-Log -Message $Message -Level "ERROR"
}

function Write-DebugLog {
    param(
        [Parameter(Mandatory=$True)]
        [string]
        $Message,

        [string]
        $LogLevel = $null
    )

    if ("DEBUG" -eq $LogLevel) {
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
        $DatabaseName,

        [boolean]
        $WriteDebugMessages
    )


    function Write-DebugLog {
        param(
            [Parameter(Mandatory=$True)]
            [string]
            $Message
        )

        if ($WriteDebugMessages) {
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss,fff"
            $output = "[$timestamp] DEBUG $Message"
            Write-Host -Message $output
        }
    }


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
        $spawnRate,
        $testType,
        $runTime,
        $Config
    )

    $runnerOutputPath = Get-RunnerOutputDir -Config $Config
    $testKitOutputPath = Get-OutputDir -Config $Config

    Start-Transcript -Path $runnerOutputPath/performance-test.log

    if (($testSuite -eq "volume") -and ($null -eq $runTime)) {
        throw "The -RunTime parameter must be provided when running the 'volume' suite of tests, so that the test run can exit gracefully."
    }

    try {

        Write-InfoLog "Writing to $runnerOutputPath"

        $databaseInstance = Get-ConfigValue -Config $Config -Key "PERF_DB_SERVER"
        $databaseServer = Get-DatabaseServerName $databaseInstance

        $webServer = Get-ConfigValue -Config $Config -Key "PERF_WEB_SERVER"
        $sqlBackupFile = ""
        $restoreDatabase = $false
        $databaseName = ""
        try {
            $restoreDatabase = [System.Convert]::ToBoolean($(Get-ConfigValue -Config $Config -Key "PERF_DB_RESTORE"))
        } catch {
            throw "Invalid configuration value for PERF_DB_RESTORE, should be a boolean"
        }
        if ($restoreDatabase) {
            $sqlBackupFile = Get-ConfigValue -Config $Config -Key "PERF_SQL_BACKUP_FILE"
            $databaseName = Get-ConfigValue -Config $config -Key "PERF_DB_NAME"
        }

        $url = Get-ConfigValue -Config $Config -Key "PERF_API_BASEURL"
        $key = Get-ConfigValue -Config $Config -Key "PERF_API_KEY"
        $secret = Get-ConfigValue -Config $Config -Key "PERF_API_SECRET"
        if($null -eq $clientCount) {
            $clientCount = Get-ConfigValue -Config $Config -Key "CLIENT_COUNT" -Optional
        }
        if($null -eq $spawnRate){
            $spawnRate = Get-ConfigValue -Config $Config -Key "SPAWN_RATE" -Optional
        }
        if($null -eq $runTimeInMinutes){
            $runTimeInMinutes = Get-ConfigValue -Config $Config -Key "RUN_TIME_IN_MINUTES" -Optional
        }
        $connectionLimit = Get-ConfigValue -Config $Config -Key "PERF_CONNECTION_LIMIT" -Optional
        if ($null -eq $connectionLimit) {
            $connectionLimit = 5
        }
        $contentType = Get-ConfigValue -Config $Config -Key "PERF_CONTENT_TYPE" -Optional
        $resourceList = Get-ConfigValue -Config $Config -Key "PERF_RESOURCE_LIST" -Optional
        $pageSize = Get-ConfigValue -Config $Config -Key "PERF_API_PAGE_SIZE" -Optional
        $logLevel = Get-ConfigValue -Config $Config -Key "PERF_LOG_LEVEL" -Optional
        $description =Get-ConfigValue -Config $Config -Key "PERF_DESCRIPTION" -Optional
        $insecure = Get-ConfigIgnoreTlsCertificate -Config $config

        if ($restoreDatabase) {
            Write-InfoLog "Restoring $databaseName from $sqlBackupFile"

            if (Test-IsLocalhost $databaseServer) {
                Reset-OdsDatabase -BackupFilename $sqlBackupFile -DatabaseName $databaseName
            }
            else {
                Invoke-RemoteCommand $databaseServer (Get-CredentialOrDefault $databaseServer) `
                    -ArgumentList @($sqlBackupFile, $databaseName, ("DEBUG" -eq $env:PERF_LOG_LEVEL)) `
                    -ScriptBlock ${function:Reset-OdsDatabase}
            }
        } else {
            Write-InfoLog "Skipping Database Restore"
        }

        Write-InfoLog "Verifying ODS API is running"
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

        $serverMetricsBackgroundScript = {
            param(
                $server,

                $getMetricsBlock,

                $runnerOutputPath,

                $TestType,

                [Parameter(Mandatory=$false)]
                [PSCredential]
                $credential = $null
            )

            try {
                $csvPath = "$runnerOutputPath/$TestType.$server.csv"
                # Start with a fresh file
                Remove-Item -Path $runnerOutputPath  -Include "$TestType.$server.csv" -Force  | Out-Null

                # The Test-IsLocalhost function is not loading properly in the background task
                $isLocalhost = ($server.IndexOf("(local)") -gt -1) `
                    -or ($server.IndexOf("localhost") -gt -1) `
                    -or ($server.IndexOf(".") -eq 0) `
                    -or ($server.IndexOf($env:ComputerName) -gt -1)

                $getMetricsBlock = [scriptblock]::Create($getMetricsBlock)

                if ($Using:testType -eq 'soak'){
                    $sleepTime = 25
                } else {
                    $sleepTime = 5
                }

                while ($true) {
                    if ($isLocalhost) {
                        $record = Invoke-Command -ScriptBlock $getMetricsBlock
                    } else {
                        try {
                            $sessionOptions = New-PSSessionOption -SkipCACheck -SkipCNCheck
                            $psSession = New-PSSession -ComputerName $server -Credential $credential -UseSSL -SessionOption $sessionOptions -ErrorAction Stop

                            $record = Invoke-Command -Session $psSession -ScriptBlock $getMetricsBlock
                        }
                        finally {
                            if ($null -ne $psSession) {
                                $psSession | Remove-PSSession
                            }
                        }
                    }
                    $record | Select-Object * -ExcludeProperty PSComputerName,RunspaceId,PSShowComputerName `
                    | Export-Csv -Path $csvPath -Append -NoTypeInformation
                    Start-Sleep -Seconds $sleepTime
                }
            }
            catch {
                Write-ErrorLog $_.Exception.Message
            }
        }

        $backgroundJobs = @{}

        Write-InfoLog "Starting background job to fetch metrics from $databaseServer"

        $parms = @(
            $databaseServer,
            ${function:Get-ServerMetrics},
            $runnerOutputPath,
            $testType
        )
        if (-not (Test-IsLocalhost $databaseServer)) { $parms += (Get-CredentialOrDefault $databaseServer) }

        $collectStatsFromDb = Start-Job -ArgumentList $parms -ScriptBlock $serverMetricsBackgroundScript
        $backgroundJobs.Add($databaseServer, $collectStatsFromDb)

        # If database and web are on the same server, there is no reason to
        # collect the same metrics twice.
        if ($webServer -ne $databaseServer) {
            Write-InfoLog "Starting background job to fetch metrics from $webServer"

            $parms = @(
                $webServer,
                ${function:Get-ServerMetrics},
                $runnerOutputPath,
                $testType
            )
            if (-not (Test-IsLocalhost $webServer)) { $parms += (Get-CredentialOrDefault $webServer) }
            $collectStatsFromWeb = Start-Job -ArgumentList $parms -ScriptBlock $serverMetricsBackgroundScript
            $backgroundJobs.Add($webServer, $collectStatsFromWeb)
        }

        if($testSuite -eq 'volume' -and $clientCount -lt 5) {
            # If the number of clients is too low, locust will quit immediately
            # without running any tests.
            $clientCount = 5
        }

        if ($null -eq $runTime) {
            Write-InfoLog "Running $testSuite tests with $clientCount clients..."
        } else {
            Write-InfoLog "Running $testSuite tests with $clientCount clients for $runTime..."
        }

        if($testSuite -eq 'pagevolume') {
            $outputDir = Resolve-Path $testKitOutputPath
            Push-Location ./src/edfi-paging-test

            try {
                Write-DebugLog "Executing: poetry install" -LogLevel $logLevel
                &poetry install

                $command = "poetry run python edfi_paging_test --baseUrl $url --key  $key --secret $secret --output $outputDir"
                if ($connectionLimit) {
                    $command += " --connectionLimit  $connectionLimit"
                }
                if ($contentType) {
                    $command += " --contentType  $contentType"
                }
                if ($resourceList) {
                    $command += " --resourceList $resourceList"
                }
                if ($pageSize) {
                    $command += " --pageSize $pageSize"
                }
                if ($logLevel) {
                    $command += " --logLevel $logLevel"
                }
                if ($description) {
                    $command += " --description '$description'"
                }
                if ($insecure) {
                    $command += " --ignoreCertificateErrors"
                }

                Write-DebugLog "Executing: $command" -LogLevel $logLevel
                Invoke-Expression -Command $command
            }
            catch {
                Write-ErrorLog $_.Exception.Message
                $formatstring = "{0} : {1}`n{2}`n" +
                    "    + CategoryInfo          : {3}`n" +
                    "    + FullyQualifiedErrorId : {4}`n"
                $fields = $_.InvocationInfo.MyCommand.Name,
                        $_.ErrorDetails.Message,
                        $_.InvocationInfo.PositionMessage,
                        $_.CategoryInfo.ToString(),
                        $_.FullyQualifiedErrorId
                Write-ErrorLog ($formatstring -f $fields)
            }
            finally {
                Pop-Location
            }
        }
        else{
            $outputDir = Resolve-Path $runnerOutputPath
            Push-Location ./src/edfi-performance-test
            try {
                Write-DebugLog "Executing: poetry install" -LogLevel $logLevel
                &poetry install

                $command = "poetry run python edfi_performance_test --baseUrl $url --key  $key --secret $secret --output $outputDir --testType $testSuite"
                if ($clientCount) {
                    $command += " --clientCount  $clientCount"
                }
                if ($spawnRate) {
                    $command += " --spawnRate  $spawnRate"
                }
                if ($runTimeInMinutes) {
                    $command += " --runTimeInMinutes  $runTimeInMinutes"
                }
                if ($logLevel) {
                    $command += " --logLevel $logLevel"
                }
                if ($insecure) {
                    $command += " --ignoreCertificateErrors"
                }
                Write-DebugLog "Executing: $command" -LogLevel $logLevel
                Invoke-Expression -Command $command
            }
            catch {
                Write-ErrorLog $_.Exception.Message
                $formatstring = "{0} : {1}`n{2}`n" +
                    "    + CategoryInfo          : {3}`n" +
                    "    + FullyQualifiedErrorId : {4}`n"
                $fields = $_.InvocationInfo.MyCommand.Name,
                        $_.ErrorDetails.Message,
                        $_.InvocationInfo.PositionMessage,
                        $_.CategoryInfo.ToString(),
                        $_.FullyQualifiedErrorId
                Write-ErrorLog ($formatstring -f $fields)
            }
            finally {
                Pop-Location
            }
        }
        Write-InfoLog "Test runner process complete"

        foreach ($serverName in $backgroundJobs.Keys) {
            Write-InfoLog "Stopping background job to fetch metrics from $serverName. Output collected from background job:"
            $backgroundJob = $backgroundJobs.Item($serverName)
            try{
                Stop-Job -Job $backgroundJob
                Receive-Job -Job $backgroundJob
                Remove-Job -Job $backgroundJob
            }
            catch{
                Write-ErrorLog "Failed to stop job for $($serverName):"
                Write-ErrorLog $_.Exception.Message
                $formatstring = "{0} : {1}`n{2}`n" +
                    "    + CategoryInfo          : {3}`n" +
                    "    + FullyQualifiedErrorId : {4}`n"
                $fields = $_.InvocationInfo.MyCommand.Name,
                        $_.ErrorDetails.Message,
                        $_.InvocationInfo.PositionMessage,
                        $_.CategoryInfo.ToString(),
                        $_.FullyQualifiedErrorId
                Write-ErrorLog ($formatstring -f $fields)
            }
        }

        Write-InfoLog "Fetching new ODS log file content from $webServer"
        $logFile = Get-ConfigValue -Config $config -Key "PERF_API_LOG_FILE_PATH"

        Write-DebugLog "Log file path: $logFile" -LogLevel $logLevel

        # Retrieve API log file from the web server
        if (Test-IsLocalhost $webServer) {

            $has_iis = $null -ne (Get-Service -Name W3SVC -ErrorAction SilentlyContinue)
            if ($has_iis) {
                Write-DebugLog "Stopping IIS" -LogLevel $logLevel
                Stop-Service W3SVC
                Start-Sleep 1
            }

            Write-DebugLog "Copying WebAPI log file(s)" -LogLevel $logLevel
            Copy-Item $logFile -Destination $runnerOutputPath -Recurse

            if ($has_iis) {
                Write-DebugLog "Restarting IIS" -LogLevel $logLevel
                Start-Service W3SVC
            }
        } else {
            try {
                $sessionOptions = New-PSSessionOption -SkipCACheck -SkipCNCheck
                $webCredential = Get-CredentialOrDefault -Server $webServer
                $psSession = New-PSSession -ComputerName $webServer -Credential $webCredential -UseSSL -SessionOption $sessionOptions -ErrorAction Stop

                # It is necessary to stop IIS before trying to copy log files, otherwise
                # they will be locked and `Copy-Item` will throw an errror.
                Write-DebugLog "Stopping IIS" -LogLevel $logLevel
                Invoke-Command -Session $psSession -ScriptBlock { Stop-Service W3SVC }
                Start-Sleep 1

                Write-DebugLog "Copying WebAPI log file(s)" -LogLevel $logLevel
                Copy-Item $logFile -Destination $runnerOutputPath -FromSession $psSession -Recurse

                Write-DebugLog "Restarting IIS" -LogLevel $logLevel
                Invoke-Command -Session $psSession -ScriptBlock { Start-Service W3SVC }
            }
            finally {
                if ($null -ne $psSession) {
                    $psSession | Remove-PSSession
                }
            }
        }
    }
    finally {
        Stop-Transcript
    }
}

function Set-ConfigValue {
    param (
        [Parameter(Mandatory=$True)]
        [hashtable]
        $Config,

        [Parameter(Mandatory=$True)]
        [string]
        $Key,

        [Parameter(Mandatory=$True)]
        [string]
        $Value
    )

    $Config[$Key] = $Value
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
        $Config | Out-String | Out-Host
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

    try {
        return [System.Convert]::ToBoolean($(Get-ConfigValue -Config $config -Key "IGNORE_TLS_CERTIFICATE" -Optional))
    } catch {
        Write-InfoLog "Invalid value for IGNORE_TLS_CERTIFICATE; therefore use False by default."
        return $false
    }
}

function Get-Configuration {
    $envFile = "$PSScriptRoot/.env"

    if (Test-Path $envFile) {
        $config = @{}
        Get-Content $envFile | ForEach-Object {
            $parts = $_ -split "="

            if (2 -eq $parts.Length) {
                # Be sure to ignore commented out lines
                if (-not ($parts[0][0] -in ("#", ";"))) {
                    $config[$parts[0]] = $parts[1]
                }
            }
        }
        $logLevel = Get-ConfigValue -Config $config -Key "PERF_LOG_LEVEL"
        Write-DebugLog ($config | Out-String) -LogLevel $logLevel

        # Allow the testing process to access the API over HTTP instead of HTTPS ?
        $insecure = Get-ConfigIgnoreTlsCertificate -Config $config
        $env:OAUTHLIB_INSECURE_TRANSPORT = if ($insecure) { $insecure } else { $null }

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
    Copy-Item 'change_version_tracker.json' -Destination $runnerOutputPath
}

function Get-CredentialOrDefault {
    param (
        [Parameter(Mandatory=$True)]
        [string]
        $Server
    )

    if (Test-IsLocalhost $Server) {
        throw "This shouldn't happen" + (Get-PSCallStack)
        return $null
    } else {
        # First, attempt to load credentials previously registered with Register-Credentials.
        # If there is no such registered credential, asks the user for credentials interactively.

        $folderPath = (Join-Path $env:LOCALAPPDATA "Suite-3-Performance-Testing")
        $path = Join-Path $folderPath "credentials-$server.xml"

        if (Test-Path $path) {
            return Import-CliXml -Path $path
        }

        Write-InfoLog "Requesting credentials for $server interactively"
        $credentials = Get-Credential -Message "Please enter credentials for $server"
        $credential | Export-CliXml -Path $path
        Write-Host "Saved to $path"
        return $credential
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
    $runnerDir = Join-Path -Path $outputDir -ChildPath (Get-Date -Format "yyyy-MM-dd-HH-mm-ss")
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
        -TestType pagevolume `
        -Config $config
}

# Removed in version 2.0 release, will be restored in the future
function Invoke-VolumeTests {
    $config = Initialize-TestRunner
    Invoke-TestRunner `
        -TestSuite volume `
        -ClientCount 100 `
        -SpawnRate 25 `
        -RunTime 30m `
        -TestType volume `
        -Config $config
}

function Invoke-StressTests {
    $config = Initialize-TestRunner
    Invoke-TestRunner `
        -TestSuite volume `
        -ClientCount 1000 `
        -SpawnRate 25 `
        -RunTime 30m `
        -TestType stress `
        -Config $config
}

function Invoke-SoakTests {
    $config = Initialize-TestRunner
    Invoke-TestRunner `
        -TestSuite volume `
        -ClientCount 500 `
        -SpawnRate 1 `
        -RunTime 48h `
        -TestType soak `
        -Config $config
}
function Invoke-PipecleanTests {
    $config = Initialize-TestRunner
    Invoke-TestRunner `
        -TestSuite pipeclean `
        -ClientCount 1 `
        -SpawnRate 1 `
        -TestType pipeclean `
        -Config $config
}

function Invoke-ChangeQueryTests {
    $config = Initialize-TestRunner

    Set-ChangeVersionTracker
    $changeQueryBackupFilenames = Get-ConfigValue -Config $config -Key 'CHANGE_QUERY_BACKUP_FILE_NAMES'

    $iteration = 1
    foreach ($changeQueryBackupFilename in $changeQueryBackupFilenames){
        $testResultsPath = Get-OutputDir -Config $config
        $testResultsPath = $testResultsPath + "_" + $iteration
        Set-ConfigValue -Config $config -Key "PERF_OUTPUT_DIR" -Value $testResultsPath
        $iteration = $iteration + 1

        Invoke-TestRunner `
            -TestSuite change_query `
            -ClientCount 1 `
            -SpawnRate 1 `
            -TestType change_query `
            -Config $config
        Duplicate-ChangeVersionTracker
     }
}

Export-ModuleMember -Function Invoke-PageVolumeTests
Export-ModuleMember -Function Invoke-PipecleanTests
Export-ModuleMember -Function Invoke-VolumeTests
Export-ModuleMember -Function Invoke-StressTests
Export-ModuleMember -Function Invoke-SoakTests
Export-ModuleMember -Function Invoke-ChangeQueryTests

