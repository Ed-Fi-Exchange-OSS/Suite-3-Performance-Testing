/*
 * SPDX-License-Identifier: Apache-2.0
 * Licensed to the Ed-Fi Alliance under one or more agreements.
 * The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
 * See the LICENSE and NOTICES files in the project root for more information.
 */

# Configure the Microsoft Azure Provider
provider "azurerm" {
  features {}
  #skip_provider_registration = "true"
}

locals {
  full_prefix          = "${var.prefix}-${var.label}"
  rg_name              = "${var.prefix}-${var.label}"
  vnet_name            = "${local.full_prefix}-vnet"
  short_label          = replace(var.label, "-", "")
  long_sa_name         = "${local.short_label}tfstate${random_id.rand_storage.hex}"
  storage_account_name = substr(local.long_sa_name, 0, 24)
}

# Create RG
resource "azurerm_resource_group" "base_rg" {
  name     = local.rg_name
  location = var.location
}

# Create networking
module "network" {
  source = "./modules/network"

  resource_group_name = azurerm_resource_group.base_rg.name
  location            = azurerm_resource_group.base_rg.location
  prefix              = local.full_prefix
  vnet_name           = local.vnet_name
  subnet_name         = var.base_subnet
  vnet_cidr           = "10.1.0.0/16"
  subnet_cidr         = "10.1.0.0/24"
}

# Database VM
module "sql_vm" {
  source              = "./modules/vm"
  resource_group_name = azurerm_resource_group.base_rg.name
  location            = azurerm_resource_group.base_rg.location
  subnet_id           = module.network.vnet_subnet_id[0]
  vm_sg_id            = module.network.sql_sg_id
  prefix              = local.full_prefix

  application        = "sql"
  computer_name      = var.sql_vm_computer_name
  vm_size            = var.sql_vm_size
  data_disk_size     = var.sql_vm_data_disk_size
  vm_image_publisher = var.sql_vm_image_publisher
  vm_image_offer     = var.sql_vm_image_offer
  vm_image_sku       = var.sql_vm_image_sku

  admin_username = var.sql_admin_username
  admin_password = var.sql_admin_password
}
# DB VM Config
module "sql_config" {
  source           = "./modules/vm_scripts"
  vm_computer_name = module.sql_vm.vm_computer_name
  vm_id            = module.sql_vm.vm_id
  script_filename  = "install-db-server-prerequisites.ps1"
  depends_on = [
    module.sql_vm
  ]
}

# Web VM
module "web_vm" {
  source              = "./modules/vm"
  resource_group_name = azurerm_resource_group.base_rg.name
  location            = azurerm_resource_group.base_rg.location
  subnet_id           = module.network.vnet_subnet_id[0]
  vm_sg_id            = module.network.vm_sg_id
  prefix              = local.full_prefix

  application        = "web"
  computer_name      = var.web_vm_computer_name
  vm_size            = var.web_vm_size
  data_disk_size     = var.web_vm_data_disk_size
  vm_image_publisher = var.web_vm_image_publisher
  vm_image_offer     = var.web_vm_image_offer
  vm_image_sku       = var.web_vm_image_sku

  admin_username = var.web_admin_username
  admin_password = var.web_admin_password
}
# Web VM Config
module "web_config" {
  source           = "./modules/vm_scripts"
  vm_computer_name = module.web_vm.vm_computer_name
  vm_id            = module.web_vm.vm_id
  script_filename  = "install-web-server-prerequisites.ps1"
  depends_on = [
    module.web_vm
  ]
}
# # Test Runner VM
module "runner_vm" {
  source              = "./modules/vm"
  resource_group_name = azurerm_resource_group.base_rg.name
  location            = azurerm_resource_group.base_rg.location
  subnet_id           = module.network.vnet_subnet_id[0]
  vm_sg_id            = module.network.vm_sg_id
  prefix              = local.full_prefix

  application        = "runner"
  computer_name      = var.runner_vm_computer_name
  vm_size            = var.runner_vm_size
  data_disk_size     = var.web_vm_data_disk_size
  vm_image_publisher = var.web_vm_image_publisher
  vm_image_offer     = var.web_vm_image_offer
  vm_image_sku       = var.web_vm_image_sku

  admin_username = var.runner_admin_username
  admin_password = var.runner_admin_password
}
# Runner VM Config
module "runner_config" {
  source           = "./modules/vm_scripts"
  vm_computer_name = module.runner_vm.vm_computer_name
  vm_id            = module.runner_vm.vm_id
  script_filename  = "install-test-runner-prerequisites.ps1"
  depends_on = [
    module.runner_vm
  ]
}

### Terraform state Buckets
resource "random_id" "rand_storage" {
  byte_length = 3
}
resource "azurerm_storage_account" "tf_state" {
  name                     = local.storage_account_name
  resource_group_name      = azurerm_resource_group.base_rg.name
  location                 = azurerm_resource_group.base_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}
resource "azurerm_storage_container" "tf_state" {
  name                 = "tfstate"
  storage_account_name = azurerm_storage_account.tf_state.name
}
