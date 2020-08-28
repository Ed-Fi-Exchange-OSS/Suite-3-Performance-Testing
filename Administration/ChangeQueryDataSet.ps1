function task($heading, $command, $path) {
    write-host
    write-host $heading -fore CYAN
    execute $command $path
}

function execute($command, $path) {
    if ($path -eq $null) {
        $global:lastexitcode = 0
        & $command
    } else {
        Push-Location $path
        $global:lastexitcode = 0
        & $command
        Pop-Location
    }
    if ($lastexitcode -ne 0) {
        throw "Error executing command: $command"
    }
}

function Get-Config {
    $configJson = Get-Content 'ChangeQueryDataSet-Config.json' | Out-String
    $global:config = $configJson | ConvertFrom-Json
}

function Get-LocustConfig {
    $configJson = Get-Content '../locust-config.json' | Out-String
    $global:locustConfig = $configJson | ConvertFrom-Json
    $locustConfig.change_query_backup_filenames = New-Object System.Collections.ArrayList
    $locustConfig.restore_database = "true"
}

function Update-LocustConfig($currentDataPeriod) {
    $locustConfig.change_query_backup_filenames.Add("$($config.databaseName)_DataPeriod_$currentDataPeriod.bak")
    $locustConfig | ConvertTo-Json | Set-Content -Path '../locust-config.json'
}

function Create-Backup {
    param(
        [Int]$dataPeriodNumber=$(throw "-dataPeriodNumber argument is required.  Must provide the data period number."),
        [string]$sqlBackupPath="",
        [string]$databaseName="")
    if ($sqlBackupPath -eq "") {
        Get-LocustConfig
        $sqlBackupPath = $locustConfig.sql_backup_path
    }
    if ($databaseName -eq "") {
        Get-Config
        $databaseName = $config.databaseName
    }
    $filePath = Join-Path $sqlBackupPath "$($databaseName)_DataPeriod_$dataPeriodNumber.bak"
    Invoke-SqlCmd -Database "master" `
                  -Query "ALTER DATABASE $($databaseName) SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
                          BACKUP DATABASE $($databaseName) TO DISK = '$($filePath)';
                          ALTER DATABASE $($databaseName) SET MULTI_USER;" -QueryTimeout 0
    write-host "Backup file created for Data Period: $($dataPeriodNumber)"
}

function ApiClientLoader {
    param(
        [Int]$dataPeriodNumber=$(throw "-dataPeriodNumber argument is required.  Must provide the data period number."),
        [string]$apiLoader=$(throw "-apiLoader argument is required.  Must provide the full file path to the folder containing the EdFi.ApiLoader.Console executable."),
        [string]$working=$(throw "-working argument is required. Must provide the full file path to a writable folder containing the working files for the Ed-Fi ApiLoader."),
        [string]$xml=$(throw "-xml argument is required.  Must provide the full file path to the folder containing the xml files created by the SDG."),
        [string]$xsd=$(throw "-xsd argument is required.  Must provide the full file path to the folder containing the Ed-Fi Xsd Schema files e.g. 'C:\dev\Ed-Fi-Standard\v3.1\Schemas\Bulk'."))
    # Useful when using a 31 (assessments) build of the api client loader against a corresponding ODS.
    # Note how this is using a specially-built api loader from a branch that claimed to know those Assessments changes.
    # Specifying /c 1 and /l 1 are maybe useful during troubleshooting but should be removed in general.
    Get-Config
    $outputPath = Resolve-Path .
    task $config.databaseName {
        .\EdFi.ApiLoader.Console.exe `
            /a "$($config.apiHost)/data/v$($config.apiVersion)/" `
            /m "$($config.apiHost)/metadata" `
            /o $config.apiHost `
            /k $config.clientId `
            /s $config.clientSecret `
            /d "$($xml)\Change Events Performance Test - Data Period $dataPeriodNumber" `
            /x $xsd `
            /w $working `
            /y $config.schoolYear `
            /c 1 `
            /l 1 `
            /f `
            2>&1 | tee "$($outputPath)\DataPeriod_$dataPeriodNumber.txt"
    } $apiLoader
}

function Run-ApiClientLoader {
    param(
        [Int]$lastDataPeriod=$(throw "-lastDataPeriod argument is required.  Must provide the number for the last data period."),
        [string]$apiLoader=$(throw "-apiLoader argument is required.  Must provide the full file path to the folder containing the EdFi.ApiLoader.Console executable."),
        [string]$working=$(throw "-working argument is required. Must provide the full file path to a writable folder containing the working files for the Ed-Fi ApiLoader."),
        [string]$xml=$(throw "-xml argument is required.  Must provide the full file path to the folder containing the xml files created by the SDG."),
        [string]$xsd=$(throw "-xsd argument is required.  Must provide the full file path to the folder containing the Ed-Fi Xsd Schema files e.g. 'C:\dev\Ed-Fi-Standard\v3.1\Schemas\Bulk'."),
        [Int]$firstDataPeriod=1,
        [Bool]$updateConfig=$FALSE)
    # The $lastDataPeriod argument and the optional $firstDataPeriod argument allow the user to run the ApiClientLoader
    # for a particular range of data periods (e.g. data periods 2 to 5).
    Initialize-Folder $working
    Get-LocustConfig
    for ($i = $firstDataPeriod; $i -le $lastDataPeriod; $i++) {
        ApiClientLoader `
            -DataPeriodNumber $i `
            -ApiLoader $apiLoader `
            -Working $working `
            -Xml $xml `
            -Xsd $xsd
        Create-Backup `
            -DataPeriodNumber $i `
            -SqlBackupPath $locustConfig.sql_backup_path `
            -DatabaseName $config.databaseName
        if ($updateConfig) {
            Update-LocustConfig $i
        }
    }
}

function Initialize-Folder($path) {
    if (!(Test-Path $path)) {
        New-Item -ItemType Directory -Force -Path $path | Out-Null
    } else {
        Get-ChildItem -Path $path -Recurse | Remove-Item -Recurse
    }
}

function Sort-XmlFiles {
    param($xml=$(throw "-xml argument is required. Must provide the full file path to the folder containing the xml files created by the SDG."))
    $dataPeriodNumber = 1
    $isDataPresent = $TRUE
    while ($isDataPresent -eq $TRUE) {
        $searchTerm = "Change Events Performance Test - Data Period $dataPeriodNumber"
        $dataPeriodFolder = Join-Path $xml $searchTerm
        $dataPeriodFiles = Get-ChildItem -File -Path $xml -Filter "*$searchTerm*"
        if ($dataPeriodFiles.Count -eq 0 -and !(Test-Path -Path $dataPeriodFolder)) {
            $isDataPresent = $FALSE
        } elseif ($dataPeriodFiles.Count -eq 0 -and (Test-Path -Path $dataPeriodFolder)) {
            $dataPeriodNumber = $dataPeriodNumber + 1
        } else {
            New-Item -ItemType Directory -Force -Path $dataPeriodFolder | Out-Null
            foreach ($file in $dataPeriodFiles) {
                $file | Move-Item -Destination $dataPeriodFolder
            }
            $dataPeriodNumber = $dataPeriodNumber + 1
        }
    }
    $dataPeriodCount = $dataPeriodNumber - 1
    write-host "$dataPeriodCount Data Periods were sorted."
    return $dataPeriodCount
}

function GenerateAllSQLBackups {
   param(
       [string]$apiLoader=$(throw "-apiLoader argument is required.  Must provide the full file path to the folder containing the EdFi.ApiLoader.Console executable."),
       [string]$working=$(throw "-working argument is required. Must provide the full file path to a writable folder containing the working files for the Ed-Fi ApiLoader."),
       [string]$xml=$(throw "-xml argument is required.  Must provide the full file path to the folder containing the xml files created by the SDG."),
       [string]$xsd=$(throw "-xsd argument is required.  Must provide the full file path to the folder containing the Ed-Fi Xsd Schema files e.g. 'C:\dev\Ed-Fi-Standard\v3.1\Schemas\Bulk'."),
       [Bool]$updateConfig=$FALSE)
   $dataPeriodCount = Sort-XmlFiles $xml
   Run-ApiClientLoader `
       -LastDataPeriod $dataPeriodCount `
       -ApiLoader $apiLoader `
       -Working $working `
       -Xml $xml `
       -Xsd $xsd `
       -UpdateConfig $updateConfig
}

function Info {
  write-host
  write-host "FUNCTION LIST" -fore YELLOW
  write-host "-------------"
  write-host
  write-host "GenerateALLSQLBackups" -fore GREEN
  write-host "Purpose:" -fore YELLOW -NoNewLine
  write-host " Sort xml files, run ApiLoader for each data period and create backups for each data period."
  write-host "Required Arguments:" -fore YELLOW
  write-host "-apiLoader" -fore CYAN -NoNewLine
  write-host " Full file path to the folder containing the EdFi.ApiLoader.Console executable."
  write-host "-working" -fore CYAN -NoNewLine
  write-host " Full file path to a writable folder containing the working files for the Ed-Fi ApiLoader."
  write-host "-xml" -fore CYAN -NoNewLine
  write-host " Full file path to the folder containing the xml files created by the SDG."
  write-host "-xsd" -fore CYAN -NoNewLine
  write-host " Full file path to the folder containing the Ed-Fi Xsd Schema files e.g. 'C:\dev\Ed-Fi-Standard\v3.1\Schemas\Bulk'."
  write-host "Optional Argument:" -fore YELLOW
  write-host "-updateConfig" -fore CYAN -NoNewLine
  write-host " If set to $TRUE, the locust-config.json file will be updated automatically so that the ChangeQuery test can be run without needing to update the config file. Default value is $FALSE."
  write-host
  write-host "Sort-XmlFiles" -fore GREEN
  write-host "Purpose:" -fore YELLOW -NoNewLine
  write-host " Sort xml files created by the SDG."
  write-host "Required Argument:" -fore YELLOW
  write-host "-xml" -fore CYAN -NoNewLine
  write-host " Full file path to the folder containing the xml files created by the SDG."
  write-host
  write-host "Run-ApiClientLoader" -fore GREEN
  write-host "Purpose:" -fore YELLOW -NoNewLine
  write-host " Run the ApiLoader for a particular range of data periods and create backups for each data period.  It does not sort the xml files and assumes that the xml files have been sorted previously."
  write-host "Required Arguments:" -fore YELLOW
  write-host "-lastDataPeriod" -fore CYAN -NoNewLine
  write-host " In the normal case of 7 data periods, this should be set to 7.  To run the ApiLoader for a particular range of data periods, this argument should be set to the max of the range."
  write-host "-apiLoader" -fore CYAN -NoNewLine
  write-host " Full file path to the folder containing the EdFi.ApiLoader.Console executable."
  write-host "-working" -fore CYAN -NoNewLine
  write-host " Full file path to a writable folder containing the working files for the Ed-Fi ApiLoader."
  write-host "-xml" -fore CYAN -NoNewLine
  write-host " Full file path to the folder containing the xml files created by the SDG."
  write-host "-xsd" -fore CYAN -NoNewLine
  write-host " Full file path to the folder containing the Ed-Fi Xsd Schema files e.g. 'C:\dev\Ed-Fi-Standard\v3.1\Schemas\Bulk'."
  write-host "Optional Arguments:" -fore YELLOW
  write-host "-firstDataPeriod" -fore CYAN -NoNewLine
  write-host " Its default value is 1.  To run the ApiLoader for a particular range of data periods, this argument should be set to the min of the range."
  write-host "-updateConfig" -fore CYAN -NoNewLine
  write-host " If set to $TRUE, the locust-config.json file will be updated automatically so that the ChangeQuery test can be run without needing to update the config file. Default value is $FALSE."
  write-host
  write-host "Create-Backup" -fore GREEN
  write-host "Purpose:" -fore YELLOW -NoNewLine
  write-host " Create database backups."
  write-host "Required Argument:" -fore YELLOW
  write-host "-dataPeriodNumber" -fore CYAN -NoNewLine
  write-host " Integer value used to name the database backup file correctly."
  write-host "Optional Arguments:" -fore YELLOW
  write-host "-sqlBackupPath" -fore CYAN -NoNewLine
  write-host " Full file path to the folder where the SQL backup file should be stored.  If not set, it defaults to the value provided in the locust-config.json file."
  write-host "-databaseName" -fore CYAN -NoNewLine
  write-host " Name of database that the backup is being generated for e.g. 'EdFi_Ods_Sandbox_minimalSandbox'.  If not set, it defaults to the database name provided in the ChangeQueryDataSet.json file."
  write-host
  write-host "ApiClientLoader" -fore GREEN
  write-host "Purpose:" -fore YELLOW -NoNewLine
  write-host " Run ApiLoader for only one data period.  Does not create database backup.  This function also requires that the xml files have already been sorted."
  write-host "Required Arguments:" -fore YELLOW
  write-host "-dataPeriodNumber" -fore CYAN -NoNewLine
  write-host " Integer value used to grab the xml files for the correct data period."
  write-host "-apiLoader" -fore CYAN -NoNewLine
  write-host " Full file path to the folder containing the EdFi.ApiLoader.Console executable."
  write-host "-working" -fore CYAN -NoNewLine
  write-host " Full file path to a writable folder containing the working files for the Ed-Fi ApiLoader."
  write-host "-xml" -fore CYAN -NoNewLine
  write-host " Full file path to the folder containing the xml files created by the SDG."
  write-host "-xsd" -fore CYAN -NoNewLine
  write-host " Full file path to the folder containing the Ed-Fi Xsd Schema files e.g. 'C:\dev\Ed-Fi-Standard\v3.1\Schemas\Bulk'."
  write-host
}

Info
