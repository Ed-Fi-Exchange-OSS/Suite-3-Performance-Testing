terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=3.25.0"
    }
  }
}

# Configure the Microsoft Azure Provider
provider "azurerm" {
  features {}
  skip_provider_registration = "true"
}

locals {
  full_prefix = "${var.prefix}-${var.label}"
  rg_name = "${var.prefix}-${var.label}"
  vnet_name = "${local.full_prefix}-vnet"
}

# Create RG
resource "azurerm_resource_group" "base_rg" {
  name     = local.rg_name
  location = var.location
}
# Or find rg
/*
data "azurerm_resource_group" "base_rg" {
  name     = var.base_rg_name
}
*/
# Create networking
module "network" {
  source = "./modules/network"

  resource_group_name = azurerm_resource_group.base_rg.name
  location = azurerm_resource_group.base_rg.location
  prefix = local.full_prefix
  vnet_name = local.vnet_name
  subnet_name = var.base_subnet
  vnet_cidr = "10.1.0.0/16"
  subnet_cidr = "10.1.0.0/24"
}

# or find networking
/*
data "azurerm_virtual_network" "base_vnet" {
  name                = var.base_vnet
  resource_group_name = data.azurerm_resource_group.base_rg.name
}
data "azurerm_subnet" "base_subnet" {
  name                 = var.base_subnet
  virtual_network_name = data.azurerm_virtual_network.base_vnet.name
  resource_group_name  = data.azurerm_resource_group.base_rg.name
}
*/
# Database VM
module "sql_vm" {
  source = "./modules/vm"
  resource_group_name = azurerm_resource_group.base_rg.name
  location = azurerm_resource_group.base_rg.location
  subnet_id = module.network.vnet_subnet_id[0]
  vm_sg_id = module.network.vm_sg_id
  prefix = local.full_prefix

  application = "sql"
  vm_size = var.sql_vm_size
  os_disk_size = var.sql_vm_os_disk_size
  vm_image_publisher = var.sql_vm_image_publisher
  vm_image_offer = var.sql_vm_image_offer
  vm_image_sku = var.sql_vm_image_sku

  admin_username = var.admin_username
  admin_password = var.admin_password
}

# Web VM
module "web_vm" {
  source = "./modules/vm"
  resource_group_name = azurerm_resource_group.base_rg.name
  location = azurerm_resource_group.base_rg.location
  subnet_id = module.network.vnet_subnet_id[0]
  vm_sg_id = module.network.vm_sg_id
  prefix = local.full_prefix

  application = "web"
  vm_size = var.web_vm_size
  os_disk_size = var.web_vm_os_disk_size
  vm_image_publisher = var.web_vm_image_publisher
  vm_image_offer = var.web_vm_image_offer
  vm_image_sku = var.web_vm_image_sku

  admin_username = var.admin_username
  admin_password = var.admin_password
}

# Test Runner VM

module "runner_vm" {
  source = "./modules/vm"
  resource_group_name = azurerm_resource_group.base_rg.name
  location = azurerm_resource_group.base_rg.location
  subnet_id = module.network.vnet_subnet_id[0]
  vm_sg_id = module.network.vm_sg_id
  prefix = local.full_prefix

  application = "runner"
  vm_size = var.web_vm_size
  os_disk_size = var.web_vm_os_disk_size
  vm_image_publisher = var.web_vm_image_publisher
  vm_image_offer = var.web_vm_image_offer
  vm_image_sku = var.web_vm_image_sku

  admin_username = var.admin_username
  admin_password = var.admin_password
}

resource "random_id" "rand_storage" {
  byte_length = 3
}
resource "azurerm_storage_account" "tf-state" {
  name                     = "${local.full_prefix}-tfstate-${random_id.rand_storage.hex}"
  resource_group_name = azurerm_resource_group.base_rg.name
  location = azurerm_resource_group.base_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

}
