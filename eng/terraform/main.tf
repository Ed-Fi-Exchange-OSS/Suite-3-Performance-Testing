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
  base_vm_name = "${var.prefix}-vm"
  short_prefix = substr(var.prefix, 0, 17)
  short_vm_name = substr(local.base_vm_name, 0, 15)
}
data "azurerm_resource_group" "base_rg" {
  name     = var.base_rg_name
}

data "azurerm_virtual_network" "base_vnet" {
  name                = var.base_vnet
  resource_group_name = data.azurerm_resource_group.base_rg.name
}

data "azurerm_subnet" "base_subnet" {
  name                 = var.base_subnet
  virtual_network_name = data.azurerm_virtual_network.base_vnet.name
  resource_group_name  = data.azurerm_resource_group.base_rg.name
}
# Database VM
module "sql_vm" {
  source = "./modules/vm"
  resource_group_name = data.azurerm_resource_group.base_rg.name
  location = var.location
  subnet_id = data.azurerm_subnet.base_subnet.id
  prefix = var.prefix

  application = "sql"
  vm_size = var.sql_vm_size
  os_disk_size = var.sql_vm_os_disk_size
  vm_image_publisher = var.sql_vm_image_publisher
  vm_image_offer = var.sql_vm_image_offer
  vm_image_sku = var.sql_vm_image_sku

  admin_username = var.admin_username
  admin_password = var.admin_password
}
resource "azurerm_network_security_rule" "MSSQLRule" {
  name                        = "MSSQLRule"
  resource_group_name         = data.azurerm_resource_group.base_rg.name
  priority                    = 1100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = 1433
  source_address_prefix       = "*"
  destination_address_prefix  = "*"
  network_security_group_name = module.sql_vm.vm_sg_name
}

# Web VM
module "web_vm" {
  source = "./modules/vm"
  resource_group_name = data.azurerm_resource_group.base_rg.name
  location = var.location
  subnet_id = data.azurerm_subnet.base_subnet.id
  prefix = var.prefix

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
  resource_group_name = data.azurerm_resource_group.base_rg.name
  location = var.location
  subnet_id = data.azurerm_subnet.base_subnet.id
  prefix = var.prefix

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
  name                     = "${var.prefix}-tfstate-${random_id.rand_storage.hex}"
  resource_group_name      = data.azurerm_resource_group.base_rg.name
  location = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

}