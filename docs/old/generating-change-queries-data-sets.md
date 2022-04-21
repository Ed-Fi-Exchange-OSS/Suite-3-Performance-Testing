# Generating Change Queries Data Sets

## N.B. Change Queries Data Set Archived to Azure Storage

The data sets generated on the canonical performance test servers, using the
strategy outlined below, were moved to [Azure
Storage](https://odsassets.blob.core.windows.net/public) for better cost control
compared to leaving them archived in the virtual machine.

## How to Generate Database Backup Files

### 1. Use the Ed-Fi SDG to create Xml files

Configure the Ed-Fi Sample Data Generator (SDG) using multiple Data Periods like
so:

```xml
      <DataPeriod Name="Change Events Performance Test - Data Period 1">
        <StartDate>2016-08-22</StartDate>
        <EndDate>2016-09-29</EndDate>
      </DataPeriod>

      <DataPeriod Name="Change Events Performance Test - Data Period 2">
        <StartDate>2016-09-30</StartDate>
        <EndDate>2016-11-08</EndDate>
      </DataPeriod>

      <DataPeriod Name="Change Events Performance Test - Data Period 3">
        <StartDate>2016-11-09</StartDate>
        <EndDate>2016-12-17</EndDate>
      </DataPeriod>

      <DataPeriod Name="Change Events Performance Test - Data Period 4">
        <StartDate>2016-12-18</StartDate>
        <EndDate>2017-01-26</EndDate>
      </DataPeriod>

      <DataPeriod Name="Change Events Performance Test - Data Period 5">
        <StartDate>2017-01-27</StartDate>
        <EndDate>2017-03-07</EndDate>
      </DataPeriod>

      <DataPeriod Name="Change Events Performance Test - Data Period 6">
        <StartDate>2017-03-08</StartDate>
        <EndDate>2017-04-16</EndDate>
      </DataPeriod>

      <DataPeriod Name="Change Events Performance Test - Data Period 7">
        <StartDate>2017-04-17</StartDate>
        <EndDate>2017-05-26</EndDate>
      </DataPeriod>
```

Make note of the full file path of wherever the resulting xml files are stored.
This file path is a required argument in future steps.

### 2. Ensure that you have Ed-Fi-Standard

The ChangeQueryDataSet script requires that the user has the Ed-Fi-Standard
repository downloaded on their machine. Make sure you are on the correct branch
for the version you are trying to test and make note of the full file path of
wherever the schema files are stored for the particular version you are testing
e.g. "C:\dev\Ed-Fi-Standard\v3.1\Schemas\Bulk".

### 3. Ensure that you have EdFi.ApiLoader.Console

The EdFi.ApiLoader.Console is required to run the ChangeQueryDataSet script.
Make note of the file path of the folder that has the EdFi.ApiLoader.Console
executable as this file path is a required argument in future steps.

### 4. Start running the ODS API

The Ed-Fi-ODS documentation provides instructions on setting up and running the
ODS API.

### 5. Review values in Config

Review the values in the ChangeQueryDataSet-Config.json file and confirm that
the values are correct for your setup and tests that you are trying to run.

### 6. Run the ChangeQueryDataSet PowerShell script and associated function(s)

In PowerShell navigate to the eng\old folder and run:

```powershell
. .\ChangeQueryDataSet.ps1
```

This ensures that you can access all of the functions within the
ChangeQueryDataSet script.  There are five functions in the ChangeQueryDataSet
script that are useful for creating the Change Query data sets but the
GenerateALLSQLBackups function is all that is needed in most circumstances:

1. GenerateAllSQLBackups
    * This function is used to sort the xml files, run the ApiLoader for each
      data period and create database backups for each data period. In most
      cases this is the **only function** that will need to be run.  The other
      functions listed below are for special circumstances when the user may
      want greater control over which steps are done and in what order.
    * The required arguments are:
        * **apiLoader** : The full file path to the folder containing the
          EdFi.ApiLoader.Console executable (file path acquired in Step 3
          above).
        * **working** : The full file path to a writable folder containing the
          working files for the Ed-Fi ApiLoader e.g. "C:\Temp\API Client Working
          Folder".
        * **xml** : The full file path to the folder containing the xml files
          created by the SDG (file path acquired in Step 1 above).
        * **xsd** : The full file path to the folder containing the Ed-Fi Xsd
          Schema files e.g. "C:\dev\Ed-Fi-Standard\v3.1\Schemas\Bulk" (file path
          acquired in Step 2 above).
    * The optional argument is:
        * **updateConfig** - If set to $TRUE, the test-config.json file will
          be updated automatically so that the ChangeQuery test can be run
          without needing to update the config file.  Its default value is
          $FALSE.
    * The output from the ApiLoader is saved in individual "DataPeriod" text
      files in the current directory (e.g. eng\old).
    * The database backup files are saved in the backup location specified by
      the test-config.json file.  Each database backup file is numbered to
      match their corresponding Data Period.

2. Sort-XmlFiles
    * This function is used to sort, in place, the xml files created by the SDG
      into separate folders for each data period.
    * The required argument is:
        * **xml** : The full file path to the folder containing the xml files
          created by the SDG (file path acquired in Step 1 above).

3. Run-ApiClientLoader
    * This function is used to run the ApiLoader for a particular range of data
      periods and create backups for each data period.  It **does not** sort the
      xml files and it assumes that the xml files have been sorted previously.
    * The required arguments are:
        * **lastDataPeriod** : In the normal case of 7 data periods, this should
          be set to 7.  If the user is wanting to run the ApiLoader and generate
          backups for a particular range of data periods, this value should be
          set to the max of the range.  For instance if the range is data
          periods 3 through 5, this argument should be set to 5.
        * **apiLoader** : The full file path to the folder containing the
          EdFi.ApiLoader.Console executable (file path acquired in Step 3
          above).
        * **working** : The full file path to a writable folder containing the
          working files for the Ed-Fi ApiLoader e.g. "C:\temp\API Client Working
          Folder".
        * **xml** : The full file path to the folder containing the xml files
          created by the SDG (file path acquired in Step 1 above).
        * **xsd** : The full file path to the folder containing the Ed-Fi Xsd
          Schema files e.g. "C:\dev\Ed-Fi-Standard\v3.1\Schemas\Bulk" (file path
          acquired in Step 2 above).
    * The optional arguments are:
        * **firstDataPeriod** : Its default value is 1.  If the user wants to
          run the ApiLoader for a particular range of data periods, this
          argument should be set to the min of the range.  For instance if the
          range is data periods 3 through 7, this argument should be set to 3.
        * **updateConfig** - If set to $TRUE, the test-config.json file will
          be updated automatically so that the ChangeQuery test can be run
          without needing to update the config file.  Its default value is
          $FALSE.
    * The output from the ApiLoader is saved in individual "DataPeriod" text
      files in the current directory (e.g. eng\old).
    * The database backup files are saved in the backup location specified by
      the test-config.json file.  Each database backup file is numbered to
      match their corresponding Data Period.

4. Create-Backup
    * This function is used to create database backups.
    * The required argument is:
        * **dataPeriodNumber** - This integer value is used to name the database
          backup file correctly. It assumes that the value provided is accurate.
          If a backup file was already created for that data period it will be
          overwritten.
    * The optional arguments are:
        * **sqlBackupPath** - The full file path to the folder where the SQL
          backup file should be stored.  If not set, it defaults to the value
          provided in the test-config.json file.
        * **databaseName** - The name of the database that the backup is being
          generated for e.g. "EdFi_Ods_Sandbox_minimalSandbox".  If not set, it
          defaults to the database name provided in the ChangeQueryDataSet.json
          file.

5. ApiClientLoader
    * This function will run the ApiLoader for only one data period.  It *does
      not* create database backups.  This function also requires that the xml
      files have been sorted previously as occurs in the Sort-XmlFiles function
      above.
    * The required arguments are:
        * **dataPeriodNumber** - This integer value is used to grab the correct
          xml files to run the ApiLoader.
        * **apiLoader** : The full file path to the folder containing the
          EdFi.ApiLoader.Console executable (file path acquired in Step 3
          above).
        * **working** : The full file path to a writable folder containing the
          working files for the Ed-Fi ApiLoader e.g. "C:\Temp\API Client Working
          Folder".
        * **xml** : The full file path to the folder containing the xml files
          created by the SDG (file path acquired in Step 1 above).
        * **xsd** : The full file path to the folder containing the Ed-Fi Xsd
          Schema files e.g. "C:\dev\Ed-Fi-Standard\v3.1\Schemas\Bulk" (file path
          acquired in Step 2 above).
    * The output from the ApiLoader is saved in individual "DataPeriod" text
      files in the current directory (e.g. eng\old).

## Using the Generated Data Sets

If in Step 6, you ran GenerateAllSQLBackups or Run-ApiClientLoader and you set
the optional argument UpdateConfig to $TRUE, you can go ahead and run the
ChangeQuery test without needing to do anything else.  Otherwise, open the
test-config.json file, update the change_query_backup_filenames array to list
the names of the database backup files that you just created and change the
value of restore_database to "true".
