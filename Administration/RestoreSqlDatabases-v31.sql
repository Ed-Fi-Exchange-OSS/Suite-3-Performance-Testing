-- SPDX-License-Identifier: Apache-2.0
-- Licensed to the Ed-Fi Alliance under one or more agreements.
-- The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
-- See the LICENSE and NOTICES files in the project root for more information.

-- This script restores initial-state databases on the Azure SQL Server VM. It assumes the *.bak files have been copied into the VM under
-- F:\Database Backups\2018-11-25 v3 Change Query Backups\Initial State\
-- and restores them to the data disk at F:\Data.

RESTORE DATABASE EdFi_Admin FROM DISK = 'F:\Database Backups\2018-11-25 v3 Change Query Backups\Initial State\EdFi_Admin.bak'
WITH
    MOVE 'EdFi_Admin' TO 'F:\DATA\EdFi_Admin.mdf',
    MOVE 'EdFi_Admin_log' TO 'F:\DATA\EdFi_Admin_log.ldf',
	REPLACE;

RESTORE DATABASE EdFi_Bulk FROM DISK = 'F:\Database Backups\2018-11-25 v3 Change Query Backups\Initial State\EdFi_Bulk.bak'
WITH
    MOVE 'EdFi_Bulk' TO 'F:\DATA\EdFi_Bulk.mdf',
    MOVE 'EdFi_Bulk_log' TO 'F:\DATA\EdFi_Bulk_log.ldf',
	REPLACE;

RESTORE DATABASE EdFi_Security FROM DISK = 'F:\Database Backups\2018-11-25 v3 Change Query Backups\Initial State\EdFi_Security.bak'
WITH
    MOVE 'EdFi_Security' TO 'F:\DATA\EdFi_Security.mdf',
    MOVE 'EdFi_Security_log' TO 'F:\DATA\EdFi_Security_log.ldf',
	REPLACE;

RESTORE DATABASE EdFi_Ods_Sandbox_populatedSandbox FROM DISK = 'F:\Database Backups\2018-11-25 v3 Change Query Backups\Initial State\EdFi_Ods_Sandbox_populatedSandbox.bak'
WITH
    MOVE 'EdFi_Ods_Populated_Template' TO 'F:\DATA\EdFi_Ods_Sandbox_populatedSandbox.mdf',
    MOVE 'EdFi_Ods_Populated_Template_log' TO 'F:\DATA\EdFi_Ods_Sandbox_populatedSandbox_log.ldf',
	REPLACE;

RESTORE DATABASE EdFi_Ods_Sandbox_minimalSandbox FROM DISK = 'F:\Database Backups\2018-11-25 v3 Change Query Backups\Initial State\EdFi_Ods_Sandbox_minimalSandbox.bak'
WITH
    MOVE 'EdFi_Ods_Minimal_Template' TO 'F:\DATA\EdFi_Ods_Sandbox_minimalSandbox.mdf',
    MOVE 'EdFi_Ods_Minimal_Template_log' TO 'F:\DATA\EdFi_Ods_Sandbox_minimalSandbox_log.ldf',
	REPLACE;
