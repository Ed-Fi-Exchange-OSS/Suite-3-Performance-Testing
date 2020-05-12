-- This script restores initial-state databases on the Azure SQL Server VM. It assumes the *.bak files have been copied into the VM under
-- F:\Database Backups\
-- and restores them to the data disk at F:\Data.

RESTORE DATABASE EdFi_Admin FROM DISK = 'F:\Database Backups\EdFi_Admin.bak'
WITH
    MOVE 'EdFi_Admin' TO 'F:\DATA\EdFi_Admin.mdf',
    MOVE 'EdFi_Admin_log' TO 'F:\DATA\EdFi_Admin_log.ldf';

RESTORE DATABASE EdFi_Bulk FROM DISK = 'F:\Database Backups\EdFi_Bulk.bak'
WITH
    MOVE 'EdFi_Bulk' TO 'F:\DATA\EdFi_Bulk.mdf',
    MOVE 'EdFi_Bulk_log' TO 'F:\DATA\EdFi_Bulk_log.ldf';

RESTORE DATABASE EdFi_Security FROM DISK = 'F:\Database Backups\EdFi_Security.bak'
WITH
    MOVE 'EdFi_Security' TO 'F:\DATA\EdFi_Security.mdf',
    MOVE 'EdFi_Security_log' TO 'F:\DATA\EdFi_Security_log.ldf';

RESTORE DATABASE EdFi_Ods_Sandbox_populatedSandbox FROM DISK = 'F:\Database Backups\EdFi_Ods_Sandbox_populatedSandbox.bak'
WITH
    MOVE 'EdFi_Ods_Populated_Template' TO 'F:\DATA\EdFi_Ods_Sandbox_populatedSandbox.mdf',
    MOVE 'EdFi_Ods_Populated_Template_log' TO 'F:\DATA\EdFi_Ods_Sandbox_populatedSandbox_log.ldf',
	REPLACE;

RESTORE DATABASE EdFi_Ods_Sandbox_minimalSandbox FROM DISK = 'F:\Database Backups\EdFi_Ods_Sandbox_minimalSandbox.bak'
WITH
    MOVE 'EdFi_Ods_Minimal_Template' TO 'F:\DATA\EdFi_Ods_Sandbox_minimalSandbox.mdf',
    MOVE 'EdFi_Ods_Minimal_Template_log' TO 'F:\DATA\EdFi_Ods_Sandbox_minimalSandbox_log.ldf';
