terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=3.0.0"
    }
  }
}

# Configure the Microsoft Azure Provider
provider "azurerm" {
  features {}
  skip_provider_registration = "true"
}
####
locals {
  
}

####
# analytics perf testing VM
# SqlVirtualMachine | MicrosoftSQLServer - SQL2017-WS2016 - SQLDEV | Standard_DS11_v2 | South Central US
# NIC, PIP, 2 1024 GB data disks
module "sql_vm_at" {
  source = "./modules/at_server"
  prefix = var.apt_prefix
  base_rg_name = var.base_rg_name
  base_vnet = var.at_vnet_name
  base_subnet = var.at_base_subnet_name
  admin_username = var.at_vm_admin_username
  admin_password = var.at_vm_admin_password
  location = "southcentralus"
}
# tools di perf testing ODS VM
# SqlVirtualMachine | microsoftsqlserver - sql2019-ws2019 - sqldev | Standard_DS11_v2 | Central US
# NIC, PIP, 1 8 GB data disk
module "sql_vm_ods" {
  source = "./modules/gen_vm"
  prefix = var.tools_prefix
  application = "ods"
  base_rg_name = var.base_rg_name
  base_vnet = var.tools_vnet_name
  base_subnet = var.tools_base_subnet_name
  admin_username = var.ods_vm_admin_username
  admin_password = var.ods_vm_admin_password
  location = "centralus"
}
# tools di perf testing di VM
# SqlVirtualMachine | microsoftsqlserver - sql2019-ws2019 - sqldev | Standard_DS11_v2 | Central US
# NIC, PIP, 1 8 GB data disk
module "sql_vm_di" {
  source = "./modules/gen_vm"
  prefix = var.tools_prefix
  application = "di"
  base_rg_name = var.base_rg_name
  base_vnet = var.tools_vnet_name
  base_subnet = var.tools_base_subnet_name
  admin_username = var.di_vm_admin_username
  admin_password = var.di_vm_admin_password
  location = "centralus"
}


# analyticsteam App Service plan
# F1 - Linux - Central US

# EdFi Container Registry
# Basic - PublicNetworkAccess - South Central US

