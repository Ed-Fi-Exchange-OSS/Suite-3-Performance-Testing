Azure Test Lab
==============

Steps taken in the Azure Portal:

## Create Virtual Network:

    Name: ods-3-perf-vnet
    Address space: left at default: 10.2.0.0/16
    Subscription: Ed-Fi Alliance
    Resource Group: ods-3-performance
    Location: South Central US
    Subnet:
        Name: ods-3-perf-subnet
        Address space: left at default: 10.2.0.0/24
    DDoS Protection:
        Left at default, Basic.
    Service endpoints:
        Left at default, Disabled.

    Resources Created:
        ods-3-perf-vnet

## Create VM w/ SQL:

    Basics:
        VM Image: Free SQL Server License: SQL Server 2017 Developer on Windows Server 2016
        Name: ods-3-perf-db
        VM disk type: SSD
        Username: edFiAdmin
        Password: <in password keeper>
        Confirm Password: <in password keeper>
        Subscription: Ed-Fi Alliance
        Resource Group: ods-3-performance
        Location: South Central US
        Already have a Windows license? No.

    Size:
        DS3_v2 (Promo, 4 vcpus, 14 GB RAM, 12800 max iops, 28 GB local ssd, $313.97 estimated monthly)
            Chosen as comparable cpus/ram as VendorCertification, but for SSD, and alternatives in the same price range were not compelling over this one.

    Settings:
        Availability Zone: None //default
        Availability Set: None //default
        Use managed disks: Yes //default
        Network:
            Virtual Network: ods-3-perf-vnet //default
            Subnet: ods-3-perf-subnet //default
            Public IP Address: (new ods-3-perf-db-ip)
            Network Securtiy Group: Basic //default
            Select public inbound ports:

                Selected RDP (3389)

                UI suggests: "These ports will be exposed to the internet. Use the Advanced controls to limit inbound traffic to known IP addresses. You can also update inbound traffic rules later."

                We protect this port below.

            Accelerated networking: Disabled //default
        Auto-shutdown is Off. //default
        Monitoring:
            Boot diagnostics: Enabled //default
            Guest OS diagnostics: Disabled //default
        Managed service identity:
            Register with Azure Active Directory: No //default

    SQL Server Settings:
        SQL Connectivity: Public (internet) //We protect this port below.
        Port: 1433 //default
        SQL Authentication: Enable
            Login name and password autofilled with that of the VM above.
        Storage configuration:
            Left at defaults, all sliders on the lowest setting.
            "1 data disks will be added to the vm."
        Automated patching: left at default SUnday at 2:00
        Automated backup: left at defualt of Disabled.
        Azure Key Vault integration: left at default Disabled.
        SQL Server Machine Learning Services (in-database) left Disabled.

    Resources Created:
        ods-3-perf-db (vm)
        ods-3-perf-db_disk2_<id> (Disk)
        ods-3-perf-db_OsDisk_1_<id> (Disk)
        ods-3-perf-db262 (network interface)
        ods-3-perf-db-ip (public ip address)
        ods-3-perf-db-nsg (network security group)
        ods3performancediag127 (storage account)

    Define a DNS name for the VM:
        Select ods-3-perf-db VM in the Azure portal, click "Configure" under "DNS name".
        DNS Name: "edfi-perf-db"
        The full name of the VM is edfi-perf-db.southcentralus.cloudapp.azure.com

    Initial database state is that of a development environment after 'initdev'.
    Databases BAK created on developer machine, copied to VM over RDP.
    See RestoreSqlDatabases-v3.sql for the restore script. Note how the Data Disk is deliberately used for both backups and restored databases.

    Then, copy extract the Northridge 3.0 Dataset zip to the VM, extracting its BAK to F:\Database Backups\
        See https://s3.amazonaws.com/edfi_ods_samples/v3.0/EdFi_Ods_Northridge.7z

    Once the databases were restored, lock down public access to the SQL VM:
        RDP and SQL access were naturally enabled publicly above, but shouldn't be exposed at all times.

        In the Azure Portal, select the SQL VM and then go to Networking.

        Define 2 Inbound Port Rules:

            RDP allowing access to 3389 *from a trusted IP*.

            default-allow-sql allowing access to 1433 *from a trusted IP*.

            When you want to connect to these, simply set them to Allow.
            To lock them down, simply set them to Deny.

    To keep the test lab environment from being brittle with respect to password expiry across resources,
        set edFiAdmin's password to not *automatically* expire. Rotating passwords for the VMs is therefore
        the responsibility of the Test Lab administrators:

            Logged into the VM as edFiAdmin, open Computer Management \ Local Users and Groups \ edFiAdmin, check "password never expires".

    Enable PowerShell Remoting
        The test runner VM (defined below) will need to invoke PowerShell commands against this VM in order to collect performance metrics and restore database backups.
        Perform the following steps to enable PowerShell remoting using Microsoft's recommended settings.

        Copy AzureTestLab.ps1 to C:\Users\edFiAdmin.

        In a PowerShell prompt, navigate to C:\Users\edFiAdmin and execute:
            . .\AzureTestLab.ps1
            Enable-PowershellRemotingOverHttps

    Stop the SQL VM to minimize costs during periods of inactivity.

        Ensure the status changes to "Stopped (Deallocated)".

## Create VM w/ the 3.0.0 ODS API:

    Basics:
        VM Image: [smalldisk] Windows Server 2016 Datacenter
            "Note: This image comes with a 30GB OS Disk"
        Name: ods-3-perf-web
        VM disk type: SSD
        Username: edFiAdmin
        Password: <in password keeper>
        Confirm Password: <in password keeper>
        Subscription: Ed-Fi Alliance
        Resource Group: ods-3-performance
        Location: South Central US
        Already have a Windows license? No.

    Size:
        B2ms (Standard, 2 vcpus, 8 GB ram, 4800 max iops, 16GB local SSD, $99.70 estimated monthly)
            Chosen as comparable cpus/ram as VendorCertification, but for SSD, and alternatives in the same prics range were not compelling over this one.
        
    Settings:
        Availability Zone: None //default
        Availability Set: None //default
        Use managed disks: Yes //default
        OS Disk size: (31 GiB) //default
        Network:
            Virtual Network: ods-3-perf-vnet //default
            Subnet: ods-3-perf-subnet //default
            Public IP Address: (new ods-3-perf-web-ip)
            Network Security Group: Basic //default
            Select public inbound ports:
            
                Selected HTTP (80)
                Selected HTTPS (443)
                Selected RDP (3389)
                
                UI suggests: "These ports will be exposed to the internet. Use the Advanced controls to limit inbound traffic to known IP addresses. You can also update inbound traffic rules later."

                We protect these ports below.

            Extensions: No extensions //default
        Auto-shutdown is Off. //default
        Monitoring:
            Boot diagnostics: Enabled //default
            Guest OS diagnostics: Disabled //default
            Diagnostics storage account: ods3performancediag127 //default
        Managed service identity:
            Register with Azure Active Directory: No //default

    Resources Created:
        
        ods-3-perf-web (VM)
        ods-3-perf-web_OsDisk_1_<id> (Disk)
        ods-3-perf-web918 (Network interface)
        ods-3-perf-web-ip (Public IP address)
        ods-3-perf-web-nsg (Network security Group)

    Define a DNS name for the VM:
        Select ods-3-perf-web VM in the Azure portal, click "Configure" under "DNS name".
        DNS Name: "edfi-perf-web"
        The full name of the VM is edfi-perf-web.southcentralus.cloudapp.azure.com

    Lock down public access to the API VM:
        RDP and HTTP/HTTPS access were naturally enabled publicly above, but shouldn't be exposed at all times.

        In the Azure Portal, select the API VM and then go to Networking.

        Define 3 Inbound Port Rules:

            HTTP allowing access to 80 *from a trusted IP*.
            HTTPS allowing access to 443 *from a trusted IP*.
            RDP allowing access to 3389 *from a trusted IP*.

            When you want to connect to these, simply set them to Allow.
            To lock them down, simply set them to Deny.

    To keep the test lab environment from being brittle with respect to password expiry across resources,
        set edFiAdmin's password to not *automatically* expire. Rotating passwords for the VMs is therefore
        the responsibility of the Test Lab administrators:

            Logged into the VM as edFiAdmin, open Computer Management \ Local Users and Groups \ edFiAdmin, check "password never expires".

    Install web server:
        RDP into the VM, and run the following command from a Powershell prompt:

            Install-WindowsFeature -name Web-Server -IncludeManagementTools

        The command completes with the following summary:
            Success: True, Restart Needed: No, Exit Code: Success

        At this point, the defualt IIS landing page is visible via the VM's public IP.

    Install "Web Platform Installer"
        The installer can be downloaded from https://www.microsoft.com/web/downloads/platform.aspx

        The VM's security settings initially prevent such a download. In 'Server Manager' click on 'Local Server' and briefly set 'IE Enhanced Security Configuration' to 'Off'. Download the isntaller, and then change this setting back to 'On'.

    Using Web Platform Installer, install "URL Rewrite 2.1", a prerequisite for ODS's use of <rewrite> in Web.config

    Enable IIS Components
        In Server Manager, navigate to Dashboard \ Add roles and features.

        Under Web Server (IIS), locate "Application Development", select and install the following items:
            ASP.NET 4.6
            ASP.NET 3.5
            ISAPI Filters
            ISAPI Extensions
            .NET Extensibility 4.6.
            .NET Extensibility 3.5

    Configure Firewall Settings
        Enabling ports 80 and 443 on the Azure VM's Networking page is insufficient. The ports must also be enabled inside the VM's firewall settings.

        In Windows Firewall with Advanced Security, add a New Rule:
            Rule type: Port
            Protocol and Port: TCP 80, 443
            Action: Allow the connection
            Profile: Leave all checked (Domain, Private, Public)
            Name: HTTP Traffic for ODS API
            Description: Opening 80, 443 to serve up the ODS API.

    Enable HTTPS for the deployed apps:

        Select the server (root node) and then Server Certificates
            Under Actions, "Create Self-Signed Certificate"
                Friendly Name: Performance Testing ODS API Self-Signed Certificate
                Certifiate Store: Personal (default)

        On Default Web Site, Edit Bindings \ Add
            Type: https
            IP Address: All Unassigned (default)
            Port: 443
            Host Name: <blank>
            SSL certificate: "Performance Testing ODS API Self-Signed Certificate"

        If the site status is Stopped in IIS, Start it.

    Lock down public access rules via the Azure Portal:

        ods-3-perf-db \ SQL Server configuration:
            SQL connectivity level: Private (within Virtual Network)

        ods-3-perf-db \ Networking \ Inbound Rules:
            RDP, 3389, Source = <trusted IP address> DENY
            default-allow-sql, 1433, <trusted IP address> DENY

            (As well as the following rules, unchanged: AllowVnetInBound, AllowAzureLoadBalancerInBound, DenyAllInBound)

        ods-3-perf-web \ Networking \ Inbound Rules:
            HTTP, 80, Source = <trusted IP address> DENY
            HTTPS, 443, Source = <trusted IP address> DENY
            RDP, 3389, Source = <trusted IP address> DENY

            (As well as the following rules, unchanged: AllowVnetInBound, AllowAzureLoadBalancerInBound, DenyAllInBound)

        Leaving these specific rules in place but at DENY allows for easily reopening them during future troubleshooting.

    Enable PowerShell Remoting
        The test runner VM (defined below) will need to invoke PowerShell commands against this VM in order to collect performance metrics.
        Perform the following steps to enable PowerShell remoting using Microsoft's recommended settings.

        Copy AzureTestLab.ps1 to C:\Users\edFiAdmin.

        In a PowerShell prompt, navigate to C:\Users\edFiAdmin and execute:
            . .\AzureTestLab.ps1
            Enable-PowershellRemotingOverHttps

    Stop the API VM to minimize costs during periods of inactivity.

        Ensure the status changes to "Stopped (Deallocated)".

## Create VM w/ Python, Locust, and Locust Test Scripts

    Basics:
        VM Image: [smalldisk] Windows Server 2016 Datacenter
            "Note: This image comes with a 30GB OS Disk"
        Name: ods-3-perf-test
        VM disk type: SSD
        Username: edFiAdmin
        Password: <in password keeper>
        Confirm Password: <in password keeper>
        Subscription: Ed-Fi Alliance
        Resource Group: ods-3-performance
        Location: South Central US
        Already have a Windows license? No.

    Size:
        B2ms (Standard, 2 vcpus, 8 GB ram, 4800 max iops, 16GB local SSD, $99.70 estimated monthly)
            Chosen as the same as our API VM.

    Settings:
        Availability Zone: None //default
        Availability Set: None //default
        Use managed disks: Yes //default
        OS Disk size: (31 GiB) //default
        Network:
            Virtual Network: ods-3-perf-vnet //default
            Subnet: ods-3-perf-subnet //default
            Public IP Address: (new ods-3-perf-test-ip)
            Network Security Group: Basic //default
            Select public inbound ports:

                Selected RDP (3389)

                UI suggests: "These ports will be exposed to the internet. Use the Advanced controls to limit inbound traffic to known IP addresses. You can also update inbound traffic rules later."

                We protect this port below.

            Extensions: No extensions //default
        Auto-shutdown is Off. //default
        Monitoring:
            Boot diagnostics: Enabled //default
            Guest OS diagnostics: Disabled //default
            Diagnostics storage account: ods3performancediag127 //default
        Managed service identity:
            Register with Azure Active Directory: No //default

    Resources Created:

        ods-3-perf-test (VM)
        ods-3-perf-test_OsDisk_1_<id> (Disk)
        ods-3-perf-test<integer> (Network interface)
        ods-3-perf-test-ip (Public IP address)
        ods-3-perf-test-nsg (Network security Group)

    Define a DNS name for the VM:
        Select ods-3-perf-test VM in the Azure portal, click "Configure" under "DNS name".
        DNS Name: "edfi-perf-test"
        The full name of the VM is edfi-perf-test.southcentralus.cloudapp.azure.com

    Lock down public access to the ods-3-perf-test VM:
        RDP access was naturally enabled publicly above, but shouldn't be exposed at all times.

        In the Azure Portal, select the VM and then go to Networking.

        Define the Inbound Port Rule:

            RDP allowing access to 3389 from a trusted IP.

            When you want to connect to these, simply set them to Allow.
            To lock them down, simply set them to Deny.

    To keep the test lab environment from being brittle with respect to password expiry across resources,
        set edFiAdmin's password to not *automatically* expire. Rotating passwords for the VMs is therefore
        the responsibility of the Test Lab administrators:

            Logged into the VM as edFiAdmin, open Computer Management \ Local Users and Groups \ edFiAdmin, check "password never expires".

    Install Test Runner Prerequisites
        Copy install-test-runner-prerequisites.ps1 to C:\Users\edFiAdmin

        In an Administrator PowerShell prompt, navigate to C:\Users\edFiAdmin and run install-test-runner-prerequisites.ps1
        Monitor the output for potential errors.

    Create Desktop Shortcuts:

        Target: C:\Windows\System32\cmd.exe /k "C:\Users\edFiAdmin\run-deployed-tests.bat Volume"
        Start in: C:\Users\edFiAdmin
        Shortcut icon text: Run Volume Tests

        Target: C:\Windows\System32\cmd.exe /k "C:\Users\edFiAdmin\run-deployed-tests.bat Pipeclean"
        Start in: C:\Users\edFiAdmin
        Shortcut icon text: Run Pipeclean Tests

        Target: C:\Windows\System32\cmd.exe /k "C:\Users\edFiAdmin\run-deployed-tests.bat Stress"
        Start in: C:\Users\edFiAdmin
        Shortcut icon text: Run Stress Tests

        Target: C:\Windows\System32\cmd.exe /k "C:\Users\edFiAdmin\run-deployed-tests.bat Soak"
        Start in: C:\Users\edFiAdmin
        Shortcut icon text: Run Soak Tests

        Target: C:\Windows\System32\cmd.exe /k "C:\Users\edFiAdmin\run-deployed-tests.bat ChangeQuery"
        Start in: C:\Users\edFiAdmin
        Shortcut icon text: Run Change Query Tests

    Register Credentials for the SQL and Web VMs
        Copy AzureTestLab.ps1 to C:\Users\edFiAdmin.

        In a PowerShell prompt, navigate to C:\Users\edFiAdmin and execute:
            . .\AzureTestLab.ps1
            Register-Credentials

        You will be prompted for credentials for three VMs (ods-3-perf-test, ods-3-perf-db, ods-3-perf-web). For each, use the corresponding edFiAdmin login set up above during VM creation.

        If those passwords are later changed, return here and run Register-Credentials again.

    Enable PowerShell Remoting
        The TeamCity agent will need to invoke PowerShell commands against this VM in order to initiate test runs and collect artifacts.
        Perform the following steps to enable PowerShell remoting using Microsoft's recommended settings.

        Copy AzureTestLab.ps1 to C:\Users\edFiAdmin.

        In a PowerShell prompt, navigate to C:\Users\edFiAdmin and execute:
            . .\AzureTestLab.ps1
            Enable-PowershellRemotingOverHttps

        Unlike the other VMs, where PowerShell Remoting need only be enabled *within* the Azure environment, *this* VM must expose the feature publicly so that TeamCity can initiate test runs. Here, we create a corresponding inbound port rule so that the feature is exposed publicly, **but only to the IP address of the TeamCity agents**.

            In the Azure Portal, select the VM and then go to Networking.

            Define the Inbound Port Rule:
                Name: WinRmHttps
                Port: 5986
                Protocol: TCP
                Description: Enable WinRM (PowerShell Remoting) so that test runs can be invoked from IP addresses of the TeamCity build agents.
                Source IP: The public IP address of the TeamCity build agents.

            To determine the public IP address of the TeamCity build agents, run the following PowerShell command on one of the agents:
                (Invoke-WebRequest ifconfig.me/ip -UseBasicParsing).Content

    Stop the Locust Test VM to minimize costs during periods of inactivity.

        Ensure the status changes to "Stopped (Deallocated)".

## TeamCity Project to House Performance Testing Build Configurations

    Under Administration / <Root project> / Ed-Fi Builds, create project "Performance Testing" and subproject "ODS & API v3".

    When defining "Performance Testing":
        Configuration Parameters:
            vcsroot.branch: develop

    When defining "ODS & API v3":

        VCS Root (this is shared across build configurations in the project):
            Type of VCS: Git
            VCS root name: Suite-3-Performance-Testing
            Fetch URL: git@github.com:Ed-Fi-Exchange-OSS/Suite-3-Performance-Testing.git
            Default branch: %vcsroot.branch%
            Username style: Author Name and Email
            Submodules: Ignore
            Authentication method: Uploaded Key
            Uploaded Key: EdFiBuildAgent
            Passphrase : <entered by Ed-Fi staff>
            Convert line-endings to CRLF: checked
            Clean policy: Always
            Use mirrors: unchecked
            Minimum checking interval: use global server setting

        Parameters:

            env.AzureSubscriptionId
                Kind: Environment variable (env.)
                Spec: Display Hidden, Type Password

            env.AzureTenantId
                Kind: Environment variable (env.)
                Spec: Display Hidden, Type Password

            env.AzureADApplicationId
                Kind: Environment variable (env.)
                Spec: Display Hidden, Type Password
                      Description: The Azure Active Directory Application ID for the Service Principal which will be used to automate actions against Azure Resources (essentially the username of the Service Principal)

            env.AzureADServicePrincipalPassword
                Kind: Environment variable (env.)
                Spec: Display Hidden, Type Password
                      Description: The Azure Active Directory Service Principal's password, for the Service Principal which will be used to automate actions against Azure Resources

            env.AzureTestVmUsername
                Kind: Environment variable (env.)
                Spec: Display Hidden, Type Password
                      Description: The username for remoting into the Azure VM that runs performance tests.

            env.AzureTestVmPassword
                Kind: Environment variable (env.)
                Spec: Display Hidden, Type Password
                      Description: The password for remoting into the Azure VM that runs performance tests.

## TeamCity Configuration to Package Test Runner VM

    Create Build Configuration under Administration / <Root project> / Ed-Fi Builds / Performance Testing / ODS & API v3

        General Settings:
            Name: Performance Test Suite: Package Pre-Release
            Description: Creates an OctopusDeploy-compatible deployment package of the performance test suite.
            Build number format: %build.counter%
            Build counter: 1
            Artifact paths: artifacts/**

        Version Control Settings:
            VCS Root: Suite-3-Performance-Testing
            Clean build: checked

        Build Steps:
            Runner type: Command Line
            Step name: Package
            Run: Custom script
            Custom script: package %version% %build.counter% pre
                Note:
                    The optional third argument 'pre', indicates a prerelease.

                        `package 0.0.0 %build.counter% pre` builds ie. 0.0.0-pre-0123

        Triggers:
            Type: VCS Trigger
            Quiet period: 120 seconds

        Configuration Parameters:
            version: 1.0.0

        Agent Requirements:
            Parameter Name: teamcity.agent.name
            Condition: matches
            Value: INTEDFIBUILD[2|3]

    Create Build Configuration under Administration / <Root project> / Ed-Fi Builds / Performance Testing / ODS & API v3

        General Settings:
            Name: Performance Test Suite: Package Release
            Description: Creates an OctopusDeploy-compatible deployment package of the performance test suite.
            Build number format: %build.counter%
            Build counter: 1
            Artifact paths: artifacts/**

        Version Control Settings:
            VCS Root: Suite-3-Performance-Testing
            Clean build: checked

        Build Steps:
            Runner type: Command Line
            Step name: Package
            Run: Custom script
            Custom script: package %version% %build.counter%
                Note:
                        `package 0.0.0 %build.counter%` builds ie. 0.0.0.123

        Triggers:
            Type: VCS Trigger
            Quiet period: 120 seconds

        Configuration Parameters:
            version: 1.0.0
            vcsroot.branch: master
                Note: this overrides the inherited value.

        Agent Requirements:
            Parameter Name: teamcity.agent.name
            Condition: matches
            Value: INTEDFIBUILD[2|3]

## TeamCity Configuration to Run the Latest Deployed Pipeclean Tests

    Create Build Configuration under Administration / <Root project> / Ed-Fi Builds / Performance Testing / ODS & API v3

        General Settings:
            Name: Run Pipeclean Tests
            Artifact paths: artifacts/**

        Version Control Settings:
            VCS Root: Suite-3-Performance-Testing
            Clean build: checked

        Build Steps:
            Step 1:
                Runner type: PowerShell
                Step name: Start Test Lab Virtual Machines
                Execute step: If all previous steps finished successfully
                PowerShell version: 5.0
                Platform: x64
                Edition: Desktop
                Script: source code
                Script source:
                    . .\Administration\AzureTestLab.ps1
                    Start-AzureManagementSession
                    Start-AzureVmsInParallel

            Step 2:
                Runner type: PowerShell
                Step name: Run Pipeclean Tests
                Execute step: If all previous steps finished successfully
                PowerShell version: 5.0
                Platform: x64
                Edition: Desktop
                Script: source code
                Script source:
                    . .\Administration\AzureTestLab.ps1
                    Invoke-TestRunnerFromTeamCity pipeclean

            Step 3:
                Runner type: PowerShell
                Step name: Stop Test Lab Virtual Machines
                Execute step: Always, even if build stop command was issued
                    (IMPORTANT: This setting can dramatically improve Azure resource costs in the case of failed test runs.)
                PowerShell version: 5.0
                Platform: x64
                Edition: Desktop
                Script: source code
                Script source:
                    . .\Administration\AzureTestLab.ps1
                    Start-AzureManagementSession
                    Stop-AzureVmsInParallel

        Agent Requirements:
            Parameter Name: teamcity.agent.name
            Condition: matches
            Value: INTEDFIBUILD[2|3]

## TeamCity Configuration to Run the Latest Deployed Volume Tests

    Create Build Configuration under Administration / <Root project> / Ed-Fi Builds / Performance Testing / ODS & API v3

        General Settings:
            Name: Run Volume Tests
            Artifact paths: artifacts/**

        Version Control Settings:
            VCS Root: Suite-3-Performance-Testing
            Clean build: checked

        Build Steps:
            Step 1:
                Runner type: PowerShell
                Step name: Start Test Lab Virtual Machines
                Execute step: If all previous steps finished successfully
                PowerShell version: 5.0
                Platform: x64
                Edition: Desktop
                Script: source code
                Script source:
                    . .\Administration\AzureTestLab.ps1
                    Start-AzureManagementSession
                    Start-AzureVmsInParallel

            Step 2:
                Runner type: PowerShell
                Step name: Run Volume Tests
                Execute step: If all previous steps finished successfully
                PowerShell version: 5.0
                Platform: x64
                Edition: Desktop
                Script: source code
                Script source:
                    . .\Administration\AzureTestLab.ps1
                    Invoke-TestRunnerFromTeamCity volume

            Step 3:
                Runner type: PowerShell
                Step name: Stop Test Lab Virtual Machines
                Execute step: Always, even if build stop command was issued
                    (IMPORTANT: This setting can dramatically improve Azure resource costs in the case of failed test runs.)
                PowerShell version: 5.0
                Platform: x64
                Edition: Desktop
                Script: source code
                Script source:
                    . .\Administration\AzureTestLab.ps1
                    Start-AzureManagementSession
                    Stop-AzureVmsInParallel

        Agent Requirements:
            Parameter Name: teamcity.agent.name
            Condition: matches
            Value: INTEDFIBUILD[2|3]

## OctopusDeploy Configuration to Deploy to Test Runner VM and ODS API

    On the Test Runner VM (ods-3-perf-test), installed Octopus.Tentacle.3.4.14-x64.msi:
        Copied MSI downloaded from the OctopusDeploy "New deployment target" page to the ods-3-perf-test VM and installed there.

            Storage (leave at defaults):
                Tentacle configuration and logs directory: C:\Octopus
                Tentacle will install applications to (by default): C:\Octopus\Applications

            Communication (leave at default):
                Listening Tentacle

            Listening Tentacle:
                Listen port: 10933 (default)
                Add Windows Firewall exception: checked (default)
                Octopus thumbprint: <value from OctopusDeploy "New deployment target" page>

            The inbound firewall rule set up by the installer is not enough. The same rule needs to be defined on the Azure VM's Networking tab:
                Inbound Port Rule: "OctopusDeploy" Allow port 10933 TCP

    On the ODS API VM (ods-3-perf-web), installed Octopus.Tentacle.3.22.0-x64.msi:
        Copied MSI downloaded from the OctopusDeploy "New deployment target" page to the ods-3-perf-test VM and installed there.

            Storage (leave at defaults):
                Tentacle configuration and logs directory: C:\Octopus
                Tentacle will install applications to (by default): C:\Octopus\Applications

            Communication (leave at default):
                Listening Tentacle

            Listening Tentacle:
                Listen port: 10933 (default)
                Add Windows Firewall exception: checked (default)
                Octopus thumbprint: <value from OctopusDeploy "New deployment target" page>

            The inbound firewall rule set up by the installer is not enough. The same rule needs to be defined on the Azure VM's Networking tab:
                Inbound Port Rule: "OctopusDeploy" Allow port 10933 TCP

    Created Environment "Performance Testing - ODS & API v3" with 2 Deployment Targets:

        Deployment Target "edfi-perf-test":

            Target Type: Listening Tentacle
            Hostname: edfi-perf-test.southcentralus.cloudapp.azure.com
            Port: 10933

            Display name: edfi-perf-test (deliberately the same as the Hostname prefix, for clarity)
            Environments: "Performance Testing - ODS & API v3"
            Roles: PerformanceTestingClient
            Style: Listening Tentacle
            Thumbprint: <automatically filled in, matches the thumb print displayed on the VM>
            Tentacle URL: https://edfi-perf-test.southcentralus.cloudapp.azure.com:10933

            Confirm the OctopusDeploy Environments screen shows the environment with this deployment target as live.

        Deployment Target "edfi-perf-web":

            Target Type: Listening Tentacle
            Hostname: edfi-perf-web.southcentralus.cloudapp.azure.com
            Port: 10933

            Display Name: edfi-perf-web (deliberately the same as the Hostname prefix name, for clarity)
            Environments: "Performance Testing - ODS & API v3"
            Roles: PerformanceTestingWeb
            Style: Listening Tentacle
            Thumbprint: <automatically filled in, matches the thumb print displayed on the VM>
            Tentacle URL: https://edfi-perf-web.southcentralus.cloudapp.azure.com:10933

            Confirm the OctopusDeploy Environments screen shows the environment with this deployment target as live.

    Create the OctopusDeploy Lifecycle:
        Name: Performance Testing - ODS & API v3
        Phase 1: Performance Testing
            Performance Testing - ODS & API v3
            Retention Policy:
                Releases: Keep all
                Files on Tentacles: Keep 3 releases

    Create the OctopusDeploy Project
        Name: Performance Testing - Suite-3-Performance-Testing
        Project group: All Projects
        Lifecycle: Performance Testing - ODS & API v3

        Process:
            Step 1:
                Step Type: Deploy a Package
                Step Name: Deploy Performance Tests
                Runs on targets in roles: PerformanceTestingClient
                Package feed: Team City
                Package ID: Suite-3-Performance-Testing
                    (This is the prefix of artifacts on the TeamCity builds.)
                Download options: Octopus Server will download the package, then securely upload it to the Tentacles
                Environments: "Performance testing - ODS & API v3"

                Click "Configure features", unchecking all but "JSON Configuration Variables".

                JSON Configuration Variables:
                    Target files: edfi_performance\config\test-config.json

            Step 2:
                Step Type: Deploy to IIS
                Step Name: Deploy ODS API Under Test
                Runs on targets in roles: PerformanceTestingWeb
                Package feed: Octopus Server (built-in)
                Package ID: EdFi.Ods.WebApi.EFA
                IIS Deployment Type: IIS Web Application
                Web Application:
                    Parent web site name: Default Web Site
                    Virtual path: /EdFi.Ods.WebApi
                    Physical path: Package installation directory
                Application Pool:
                    Application Pool name: DefaultAppPool
                    .NET CLR version: v4.0
                    Identity: Application Pool Identity
                    Start IIS Application Pool: checked
                Configuration Transforms:
                    Run default XML transforms: checked
                    Additional Transforms:
                        Web.Release.config => Web.config
                        Web.Octopus.config => Web.config
                Substitute Variables in Files:
                    Web.config
                    Web.Octopus.config
                Configuration Variables:
                    Replace entries in .config files: checked
                Environments: "Performance testing - ODS & API v3"

                **This step should usually be left disabled. Be deliberate in the choice to deploy the ODS, and when you do, select the specific package version you wish to performance test.**

        Variables Scoped to the "Deploy Performance Tests" Step:
            host: https://ods-3-perf-web/EdFi.Ods.WebApi
            client_id: populatedSandbox
            client_secret: populatedSandboxSecret
            database_server: ods-3-perf-db
            web_server: ods-3-perf-web
            log_file_path: C:\ProgramData\Ed-Fi-ODS-API
            sql_backup_path: F:\Database Backups
            sql_data_path: F:\DATA
            database_name: EdFi_Ods_Sandbox_populatedSandbox
            backup_filename: EdFi_Ods_Northridge.bak
            restore_database: true
            delete_resources: true
            fail_deliberately: false

        Variables Scoped to the "Deploy ODS API Under Test" Step:
            OdsType: ConfigSpecificSandbox
            MSMQPrefix: EdFiOds
            MSMQEndpoint: localhost
            BearerTokenTimeoutMinutes: 20160

            DatabaseServer: ods-3-perf-db
            DatabaseUsername: Using variable type "Sensitive", the username selected when setting up SQL configuration while creating the SQL VM, above.
            DatabasePassword: Using variable type "Sensitive", the password selected when setting up SQL configuration while creating the SQL VM, above.

            OdsDbConnStr: Database=EdFi_{0}; Data Source=#{DatabaseServer}; Trusted_Connection=False;User ID=#{DatabaseUsername};Password=#{DatabasePassword}
            AdminDbConnStr: Database=EdFi_Admin; Data Source=#{DatabaseServer}; Trusted_Connection=False;User ID=#{DatabaseUsername};Password=#{DatabasePassword}
            SecurityDbConnStr: Database=EdFi_Security; Data Source=#{DatabaseServer}; Persist Security Info=True; Integrated Security=False;User ID=#{DatabaseUsername};Password=#{DatabasePassword}
            MasterDbConnStr: Database=master; Data Source=#{DatabaseServer}; Trusted_Connection=False;User ID=#{DatabaseUsername};Password=#{DatabasePassword}
            BulkOpsDbConnStr: Data Source=#{DatabaseServer};Initial Catalog=EdFi_Bulk;Trusted_Connection=False;MultipleActiveResultSets=True;User ID=#{DatabaseUsername};Password=#{DatabasePassword}
            UniqueIdDbConnStr: OBSOLETE - THIS CONNECTION STRING IS NOT USED

        Settings:
            Release Versioning:
                Use the version number from an included package
                Versioning package step: Deploy Performance Tests
